"""media-fk-migration (5.7.9.3-alpha) L0 source-inspection guards.

Background: on 2026-05-13 a pyarchinit production PG database (khutm2)
silently lost ~5156 media + ~5758 MTE rows because of a buggy plpgsql
trigger shipped in the PG schema templates. The trigger function body
contained the tautology ``IF OLD.id_media != OLD.id_media THEN ...
ELSE DELETE FROM media_table ...`` which made the cascade-DELETE branch
fire on every UPDATE/DELETE against ``media_thumb_table``.

The Group A surgery removes both trigger functions + their CREATE TRIGGER
DO-blocks from ``pyarchinit_schema_clean.sql`` and
``pyarchinit_schema_updated.sql``, and replaces them with proper
``FOREIGN KEY ... ON DELETE CASCADE`` constraints in the natural
master -> derived direction (``media_table`` -> ``media_thumb_table`` +
``media_to_entity_table``).

These four L0 tests read the SQL files as plain text and assert the
killer trigger code is gone AND the FK constraints are in place. They
do NOT execute any SQL — they are pure source inspection, runnable
without a PG cluster.

See ``docs/superpowers/specs/2026-05-13-media-fk-migration-design.md``
and ``docs/superpowers/plans/2026-05-13-media-fk-migration.md``.
"""
from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLEAN_SQL = _REPO_ROOT / "resources" / "dbfiles" / "pyarchinit_schema_clean.sql"
_UPDATED_SQL = _REPO_ROOT / "resources" / "dbfiles" / "pyarchinit_schema_updated.sql"


def _read_lines(path: Path) -> list[str]:
    """Return file contents as a list of lines (preserves line numbers
    via 0-indexed offsets, so failures can pinpoint the offending line)."""
    assert path.exists(), f"schema file missing: {path}"
    return path.read_text(encoding="utf-8").splitlines()


def _non_comment_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Strip out comment-only lines (lines whose first non-whitespace
    characters are ``--``). Returns ``[(lineno_1indexed, content), ...]``
    so a failure message can quote the offending line."""
    out: list[tuple[int, str]] = []
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.lstrip()
        if stripped.startswith("--"):
            continue
        out.append((idx, raw))
    return out


# ---------------------------------------------------------------------------
# Killer-trigger absence guards
# ---------------------------------------------------------------------------

_KILLER_FN_RE = re.compile(
    r"^\s*CREATE\s+(OR\s+REPLACE\s+)?FUNCTION\s+delete_media(_to_entity)?_table\b",
    re.IGNORECASE,
)
_KILLER_TRIG_RE = re.compile(
    r"^\s*CREATE\s+TRIGGER\s+delete_media(_to_entity)?_table\b",
    re.IGNORECASE,
)


def _assert_no_killer_trigger(path: Path) -> None:
    """Fail if any non-comment line in ``path`` matches the legacy
    ``CREATE FUNCTION`` or ``CREATE TRIGGER`` killer-trigger pattern.
    Comment lines (starting ``--``) are skipped because we intentionally
    leave a descriptive block-comment behind to document the removal."""
    raw = _read_lines(path)
    survivors = _non_comment_lines(raw)
    offenders: list[str] = []
    for lineno, content in survivors:
        if _KILLER_FN_RE.match(content) or _KILLER_TRIG_RE.match(content):
            offenders.append(f"{path.name}:{lineno}: {content!r}")
    assert not offenders, (
        "Legacy killer-trigger code still present in "
        f"{path.name}. The Group A surgery must remove both "
        "delete_media_table and delete_media_to_entity_table function + "
        "trigger blocks. Offending lines:\n  " + "\n  ".join(offenders)
    )


def test_pg_schema_clean_has_no_killer_trigger():
    """``pyarchinit_schema_clean.sql`` must NOT contain active CREATE
    FUNCTION or CREATE TRIGGER statements for the legacy killer
    triggers. A descriptive comment block referring to them by name is
    permitted (and present)."""
    _assert_no_killer_trigger(_CLEAN_SQL)


def test_pg_schema_updated_has_no_killer_trigger():
    """Same guard for ``pyarchinit_schema_updated.sql``."""
    _assert_no_killer_trigger(_UPDATED_SQL)


# ---------------------------------------------------------------------------
# FK CASCADE presence guards
# ---------------------------------------------------------------------------

_FK_THUMB_RE = re.compile(
    r"ADD\s+CONSTRAINT\s+fk_media_thumb_to_media\b", re.IGNORECASE
)
_FK_MTE_RE = re.compile(
    r"ADD\s+CONSTRAINT\s+fk_mte_to_media\b", re.IGNORECASE
)
_CASCADE_RE = re.compile(
    r"REFERENCES\s+media_table\s*\(\s*id_media\s*\)\s+ON\s+DELETE\s+CASCADE",
    re.IGNORECASE,
)


def _assert_fk_cascade(path: Path) -> None:
    """Fail unless the file declares exactly one ``fk_media_thumb_to_media``
    constraint and one ``fk_mte_to_media`` constraint, and at least two
    ``REFERENCES media_table(id_media) ON DELETE CASCADE`` clauses (one
    for each FK)."""
    src = path.read_text(encoding="utf-8")

    thumb_hits = _FK_THUMB_RE.findall(src)
    mte_hits = _FK_MTE_RE.findall(src)
    cascade_hits = _CASCADE_RE.findall(src)

    assert len(thumb_hits) == 1, (
        f"{path.name} must declare ADD CONSTRAINT fk_media_thumb_to_media "
        f"exactly once; got {len(thumb_hits)} match(es). The FK is the "
        "replacement for the deleted killer trigger on media_thumb_table."
    )
    assert len(mte_hits) == 1, (
        f"{path.name} must declare ADD CONSTRAINT fk_mte_to_media exactly "
        f"once; got {len(mte_hits)} match(es). The FK is the replacement "
        "for the deleted killer trigger that targeted media_to_entity_table."
    )
    assert len(cascade_hits) >= 2, (
        f"{path.name} must contain at least two "
        "'REFERENCES media_table(id_media) ON DELETE CASCADE' clauses "
        f"(one per FK); got {len(cascade_hits)}. Without ON DELETE CASCADE "
        "the FK behaves as RESTRICT and the migration semantics break."
    )


def test_pg_schema_clean_has_fk_cascade():
    """``pyarchinit_schema_clean.sql`` must define both replacement FK
    constraints with ON DELETE CASCADE in the natural master -> derived
    direction (media_table -> media_thumb_table + media_to_entity_table)."""
    _assert_fk_cascade(_CLEAN_SQL)


def test_pg_schema_updated_has_fk_cascade():
    """Same guard for ``pyarchinit_schema_updated.sql``."""
    _assert_fk_cascade(_UPDATED_SQL)
