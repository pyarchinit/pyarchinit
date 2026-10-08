"""Library for the USVA/USVB→USVs, USVC→USVn migration.

Split from the CLI script so tests can import the logic without invoking
argparse. The CLI module imports plan_changes/apply_changes from here.

Since 2026-10-08 the migration rewrites the **records**, not just the
unit type: the old codes also live inside the two relationship columns,
and leaving them there means the scheda keeps showing USVA next to a unit
that is now a USVs (reported by Enzo).
"""
from __future__ import annotations

import ast
import sqlite3
from pathlib import Path

# Mapping from legacy pyarchinit unit-type abbreviations to the
# EM 1.5dev1 canonical names used by the s3dgraphy GraphMLExporter.
#
# Per legacy resources/dbfiles/dot.py:
#   USVA → parallelogram (Structural Virtual SU = USV/s)
#   USVB → hexagon (Non-Structural Virtual SU = USV/n)
#   USVC → ellipse (Series of USV — pyarchinit had no separate
#                   "series" type so we collapse to USV/n which
#                   shares the green border palette).
REPLACEMENTS = {
    "USVA": "USVs",
    "USVB": "USVn",
    "USVC": "USVn",
}

#: The columns that quote other units, and may quote their type with them.
#: ``rapporti``  = [tipo, us, area, sito] (and an older [tipo, us])
#: ``rapporti2`` = [tipo, us, unita_tipo, descr, periodo, area, sito]
#:                 (and an older five-place form)
#: The code's position is not fixed across the two shapes and across the
#: ages of a scheda, so the rewrite does not assume one: it replaces any
#: cell that IS a legacy code, and any reference that starts with one
#: ("USVA104"). Nothing else in the row is touched.
RAPPORTI_COLUMNS = ("rapporti", "rapporti2")

_EMPTY_CELLS = ("", "[]", "[[]]")


def _rewrite_reference(text: str):
    """``("USVs104", True)`` for a reference that begins with a legacy code."""
    for legacy, canonical in REPLACEMENTS.items():
        if text.startswith(legacy) and len(text) > len(legacy):
            rest = text[len(legacy):]
            if not rest[0].isalpha():
                return canonical + rest, True
    return text, False


def _rewrite_cell(raw):
    """Rewrite the legacy codes in one relationship cell.

    Returns ``(new_text, changed_cells)``; ``(None, 0)`` when there is
    nothing to do and ``(None, -1)`` when the cell cannot be read — in
    which case nothing is written, because a list rewritten halfway is
    worse than an old one.
    """
    text = str(raw or "").strip()
    if text in _EMPTY_CELLS:
        return None, 0
    try:
        entries = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return None, -1
    if not isinstance(entries, (list, tuple)):
        return None, -1

    changed = 0
    out = []
    for entry in entries:
        if not isinstance(entry, (list, tuple)):
            out.append(entry)
            continue
        cells = list(entry)
        for i, cell in enumerate(cells):
            if not isinstance(cell, str):
                continue
            if cell in REPLACEMENTS:
                cells[i] = REPLACEMENTS[cell]
                changed += 1
                continue
            new, hit = _rewrite_reference(cell)
            if hit:
                cells[i] = new
                changed += 1
        out.append(cells)
    return (str(out), changed) if changed else (None, 0)


def _existing_columns(cur) -> set:
    return {row[1] for row in cur.execute("PRAGMA table_info(us_table)")}


def _scan(db_path: Path, apply: bool) -> dict:
    """Walk us_table once, counting (and optionally writing) the changes."""
    counts = {k: 0 for k in REPLACEMENTS}
    counts["USVs (already-aligned)"] = 0
    counts["USVn (already-aligned)"] = 0
    for column in RAPPORTI_COLUMNS:
        counts["%s (voci)" % column] = 0
    counts["illeggibili"] = 0

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        columns = _existing_columns(cur)
        for src in REPLACEMENTS:
            cur.execute(
                "SELECT COUNT(*) FROM us_table WHERE unita_tipo = ?", (src,))
            counts[src] = cur.fetchone()[0]
        for tgt in ("USVs", "USVn"):
            cur.execute(
                "SELECT COUNT(*) FROM us_table WHERE unita_tipo = ?", (tgt,))
            counts["%s (already-aligned)" % tgt] = cur.fetchone()[0]

        present = [c for c in RAPPORTI_COLUMNS if c in columns]
        if present:
            rows = cur.execute(
                "SELECT id_us, %s FROM us_table" % ", ".join(present)
            ).fetchall()
            for row in rows:
                id_us, cells = row[0], row[1:]
                for column, raw in zip(present, cells):
                    new_text, changed = _rewrite_cell(raw)
                    if changed < 0:
                        counts["illeggibili"] += 1
                        continue
                    if not changed:
                        continue
                    counts["%s (voci)" % column] += changed
                    if apply:
                        cur.execute(
                            "UPDATE us_table SET %s = ? WHERE id_us = ?"
                            % column, (new_text, id_us))

        if apply:
            for src, tgt in REPLACEMENTS.items():
                cur.execute(
                    "UPDATE us_table SET unita_tipo = ? WHERE unita_tipo = ?",
                    (tgt, src))
            conn.commit()
    finally:
        conn.close()
    return counts


def plan_changes(db_path: Path) -> dict:
    """Return counts per source-abbreviation and per relationship column.

    No mutation.
    """
    return _scan(Path(db_path), apply=False)


def apply_changes(db_path: Path) -> dict:
    """Apply REPLACEMENTS in-place — unit type AND relationship columns.

    Returns the same counts ``plan_changes`` would have reported before
    the run.
    """
    return _scan(Path(db_path), apply=True)
