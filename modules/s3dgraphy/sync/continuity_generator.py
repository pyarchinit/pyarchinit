"""Feature A — "Genera continuità": idempotent CON-record generation.

Qt-free domain logic. Scans US/USM rows whose life spans more than one
period (``periodo_iniziale != periodo_finale``) and creates/updates one
``CON_<us_madre>`` record per candidate, with the reciprocal continuity
rapporto on both the CON and its madre.

Pure functions: scan_candidates / build_con_record / desired_rapporti /
diff_continuity. I/O surface: load_site_records / load_existing_con /
apply_plan / generate_continuity (the orchestrator).

Spec: docs/superpowers/specs/2026-06-09-genera-continuita-con-design.md
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .rapporti import continuity_label

#: Source unit types that can bear a continuity (per spec: US / USM only).
CONTINUITY_SOURCE_TYPES = frozenset({"US", "USM"})

#: Columns read for scanning + CON construction.
_READ_COLUMNS = (
    "sito", "us", "unita_tipo", "area", "struttura",
    "periodo_iniziale", "fase_iniziale", "periodo_finale", "fase_finale",
    "other_locations",
)


@dataclass(frozen=True)
class Candidate:
    sito: str
    us: str
    unita_tipo: str
    area: str | None
    struttura: str | None
    periodo_iniziale: str
    fase_iniziale: str | None
    periodo_finale: str
    fase_finale: str | None
    other_locations: str | None


def _nz(v):
    """Normalise a DB cell to a stripped string or None."""
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def scan_candidates(records) -> list[Candidate]:
    """Return one Candidate per US/USM with both periods set and distinct."""
    out: list[Candidate] = []
    for r in records:
        if str(r.get("unita_tipo") or "").strip() not in CONTINUITY_SOURCE_TYPES:
            continue
        pi = _nz(r.get("periodo_iniziale"))
        pf = _nz(r.get("periodo_finale"))
        if pi is None or pf is None or pi == pf:
            continue
        out.append(Candidate(
            sito=str(r.get("sito") or ""),
            us=str(r.get("us") or ""),
            unita_tipo=str(r.get("unita_tipo") or ""),
            area=_nz(r.get("area")),
            struttura=_nz(r.get("struttura")),
            periodo_iniziale=pi,
            fase_iniziale=_nz(r.get("fase_iniziale")),
            periodo_finale=pf,
            fase_finale=_nz(r.get("fase_finale")),
            other_locations=r.get("other_locations"),
        ))
    return out


# ---------------------------------------------------------------------------
# Task 3: build_con_record + desired_rapporti (pure)
# ---------------------------------------------------------------------------

def con_us_code(us_madre: str) -> str:
    """Deterministic CON identity for a madre US (idempotency key)."""
    return f"CON_{us_madre}"


def desired_rapporti(cand: Candidate, *, lang: str = "it"):
    """Return (con_side_entry, madre_side_entry) rapporti rows.

    Both are 4-lists ``[label, target_us, area, sito]`` in pyArchInit's
    column convention. The CON side carries the forward label, the madre
    side the reverse label (swap → same CON is_after US edge)."""
    area = cand.area or "1"
    sito = cand.sito
    con_us = con_us_code(cand.us)
    fwd = continuity_label(lang, "forward")
    rev = continuity_label(lang, "reverse")
    con_entry = [fwd, cand.us, area, sito]
    madre_entry = [rev, con_us, area, sito]
    return con_entry, madre_entry


def build_con_record(cand: Candidate, *, schedatore: str = "",
                     lang: str = "it") -> dict:
    """Build the CON scheda dict for a candidate (no DB I/O, no uuids)."""
    # Resolve area once so the record dict and the rapporti entry are
    # consistent: a NULL/empty area in the madre defaults to "1" everywhere.
    area = cand.area or "1"
    con_entry, _ = desired_rapporti(cand, lang=lang)
    descr = (f"Continuità di {cand.us} dal periodo "
             f"{cand.periodo_iniziale} al periodo {cand.periodo_finale}")
    return {
        "sito": cand.sito,
        "us": con_us_code(cand.us),
        "unita_tipo": "CON",
        "area": area,
        "struttura": cand.struttura,
        "periodo_iniziale": cand.periodo_iniziale,
        "fase_iniziale": cand.fase_iniziale,
        "periodo_finale": cand.periodo_finale,
        "fase_finale": cand.fase_finale,
        "other_locations": cand.other_locations,
        "d_stratigrafica": "Continuità",
        "descrizione": descr,
        "rapporti": [con_entry],
        "schedatore": schedatore,
    }


# ---------------------------------------------------------------------------
# Task 4: diff_continuity (pure, idempotent)
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    to_create: list = field(default_factory=list)   # CON record dicts
    to_update: list = field(default_factory=list)   # CON record dicts
    unchanged: list = field(default_factory=list)   # us codes
    orphan: list = field(default_factory=list)      # us codes


#: CON fields compared to decide create/update/unchanged.
_COMPARE_FIELDS = (
    "area", "struttura", "periodo_iniziale", "fase_iniziale",
    "periodo_finale", "fase_finale", "other_locations",
    "d_stratigrafica", "descrizione",
)


def _norm_rapporti(value):
    """Order-insensitive normalised form of a rapporti value for compare.

    All four elements (label, target_us, area, sito) are included so that
    drift in the area/sito slots baked into rapporti entries is detected and
    triggers an update, not silently treated as unchanged.
    """
    from .rapporti import _coerce_to_list
    rows = []
    for e in _coerce_to_list(value):
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            rows.append(tuple(str(e[i]).strip() for i in range(min(len(e), 4))))
    return sorted(rows)


def _record_matches(existing: dict, desired: dict) -> bool:
    for f in _COMPARE_FIELDS:
        if _nz(existing.get(f)) != _nz(desired.get(f)):
            return False
    return _norm_rapporti(existing.get("rapporti")) == \
        _norm_rapporti(desired.get("rapporti"))


def diff_continuity(existing_con: dict, desired: list) -> Plan:
    """Compare desired CON records against existing ones (keyed by us).

    Duplicate entries with the same ``us`` key in *desired* (e.g. from
    duplicate DB rows returned by scan_candidates) are silently deduplicated:
    the first occurrence wins and subsequent occurrences are dropped.
    """
    plan = Plan()
    desired_keys = set()
    seen: set = set()
    for d in desired:
        key = d["us"]
        if key in seen:
            continue
        seen.add(key)
        desired_keys.add(key)
        cur = existing_con.get(key)
        if cur is None:
            plan.to_create.append(d)
        elif _record_matches(cur, d):
            plan.unchanged.append(key)
        else:
            plan.to_update.append(d)
    for key in existing_con:
        if key not in desired_keys:
            plan.orphan.append(key)
    return plan


# ---------------------------------------------------------------------------
# Task 5: I/O — readers + apply_plan (DbHandle, SQLite integration)
# ---------------------------------------------------------------------------

@dataclass
class Report:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    orphans_removed: int = 0
    warnings: list = field(default_factory=list)


def load_site_records(handle, sito) -> list[dict]:
    """Read US/USM rows for *sito* (only the columns scan/build need)."""
    from sqlalchemy import text
    cols = ", ".join(_READ_COLUMNS)
    with handle.engine.connect() as conn:
        rows = conn.execute(
            text(f"SELECT {cols} FROM us_table WHERE sito = :s"),
            {"s": sito}).mappings().fetchall()
    return [dict(r) for r in rows]


def load_existing_con(handle, sito) -> dict:
    """Read existing CON_* rows for *sito*, keyed by us. Includes the
    comparable fields + rapporti so diff_continuity can classify them."""
    from sqlalchemy import text
    cols = ("us, area, struttura, periodo_iniziale, fase_iniziale, "
            "periodo_finale, fase_finale, other_locations, "
            "d_stratigrafica, descrizione, rapporti")
    with handle.engine.connect() as conn:
        rows = conn.execute(
            text(f"SELECT {cols} FROM us_table "
                 "WHERE sito = :s AND unita_tipo = 'CON'"),
            {"s": sito}).mappings().fetchall()
    return {r["us"]: dict(r) for r in rows}


def _next_id(conn):
    from sqlalchemy import text
    row = conn.execute(text("SELECT MAX(id_us) FROM us_table")).fetchone()
    return (row[0] or 0) + 1


def _insert_con(conn, rec, next_id, has_node_uuid):
    """Insert one CON row. Sets id_us explicitly (cross-backend safe),
    entity_uuid always, node_uuid only when the column exists."""
    from sqlalchemy import text
    from .uuid7 import uuid7
    fields = {
        "id_us": next_id,
        "sito": rec["sito"], "area": rec["area"], "us": rec["us"],
        "unita_tipo": "CON", "struttura": rec["struttura"],
        "periodo_iniziale": rec["periodo_iniziale"],
        "fase_iniziale": rec["fase_iniziale"],
        "periodo_finale": rec["periodo_finale"],
        "fase_finale": rec["fase_finale"],
        "other_locations": rec["other_locations"],
        "d_stratigrafica": rec["d_stratigrafica"],
        "descrizione": rec["descrizione"],
        "rapporti": str([list(map(str, e)) for e in rec["rapporti"]]),
        "schedatore": rec["schedatore"],
        "entity_uuid": str(uuid7()),
    }
    if has_node_uuid:
        fields["node_uuid"] = str(uuid7())
    cols = ", ".join(fields)
    binds = ", ".join(f":{k}" for k in fields)
    conn.execute(text(f"INSERT INTO us_table ({cols}) VALUES ({binds})"),
                 fields)


def _update_con(conn, rec):
    from sqlalchemy import text
    sets = ("area=:area, struttura=:struttura, "
            "periodo_iniziale=:pi, fase_iniziale=:fi, "
            "periodo_finale=:pf, fase_finale=:ff, "
            "other_locations=:ol, d_stratigrafica=:ds, "
            "descrizione=:descr, rapporti=:rap")
    conn.execute(text(f"UPDATE us_table SET {sets} "
                      "WHERE sito=:sito AND us=:us AND unita_tipo='CON'"),
                 {"area": rec["area"], "struttura": rec["struttura"],
                  "pi": rec["periodo_iniziale"], "fi": rec["fase_iniziale"],
                  "pf": rec["periodo_finale"], "ff": rec["fase_finale"],
                  "ol": rec["other_locations"], "ds": rec["d_stratigrafica"],
                  "descr": rec["descrizione"],
                  "rap": str([list(map(str, e)) for e in rec["rapporti"]]),
                  "sito": rec["sito"], "us": rec["us"]})


def _add_reciprocal_to_madre(conn, sito, us_madre, madre_entry):
    """Append the reverse continuity rapporto to the madre row if absent."""
    from sqlalchemy import text
    from .rapporti import _coerce_to_list
    row = conn.execute(
        text("SELECT rapporti FROM us_table WHERE sito=:s AND us=:u"),
        {"s": sito, "u": us_madre}).fetchone()
    if row is None:
        return
    lst = [list(map(str, e)) for e in _coerce_to_list(row[0])
           if isinstance(e, (list, tuple))]
    target = list(map(str, madre_entry))
    # de-dup on (label, target_us)
    if any(x[:2] == target[:2] for x in lst):
        return
    lst.append(target)
    conn.execute(
        text("UPDATE us_table SET rapporti=:r WHERE sito=:s AND us=:u"),
        {"r": str(lst), "s": sito, "u": us_madre})


def _madre_entry_for(rec, us_madre, lang):
    """Rebuild the (con_entry, madre_entry) pair from a CON record dict."""
    area = rec.get("area") or "1"
    sito = rec["sito"]
    fwd = continuity_label(lang, "forward")
    rev = continuity_label(lang, "reverse")
    return ([fwd, us_madre, area, sito], [rev, rec["us"], area, sito])


def apply_plan(handle, plan, sito, *, remove_orphans=False, lang="it") -> Report:
    """Apply a Plan in a single transaction; return a Report.

    *sito* is required so that the orphan DELETE is always site-scoped,
    preventing accidental deletion of identically-named CON rows in other
    sites (critical for multi-site databases shared across excavations).
    """
    from sqlalchemy import text
    from ._db_handle import _columns_of
    rep = Report(unchanged=len(plan.unchanged))
    has_node_uuid = "node_uuid" in _columns_of(handle.engine, "us_table")
    with handle.engine.begin() as conn:
        nid = _next_id(conn)
        for rec in plan.to_create:
            if not rec.get("area"):
                rep.warnings.append(f"{rec['us']}: madre senza area")
            _insert_con(conn, rec, nid, has_node_uuid)
            nid += 1
            us_madre = rec["us"].split("CON_", 1)[-1]
            _, madre_entry = _madre_entry_for(rec, us_madre, lang)
            _add_reciprocal_to_madre(conn, rec["sito"], us_madre, madre_entry)
            rep.created += 1
        for rec in plan.to_update:
            _update_con(conn, rec)
            us_madre = rec["us"].split("CON_", 1)[-1]
            _, madre_entry = _madre_entry_for(rec, us_madre, lang)
            _add_reciprocal_to_madre(conn, rec["sito"], us_madre, madre_entry)
            rep.updated += 1
        if remove_orphans:
            for us in plan.orphan:
                conn.execute(
                    text("DELETE FROM us_table "
                         "WHERE sito=:sito AND us=:u AND unita_tipo='CON'"),
                    {"sito": sito, "u": us})
                rep.orphans_removed += 1
    return rep


# ---------------------------------------------------------------------------
# Task 6: generate_continuity orchestrator + auto-backup
# ---------------------------------------------------------------------------

def build_plan(handle, sito, *, schedatore="", lang="it") -> Plan:
    """Read site → scan → build desired → diff existing. Pure of writes
    (used by the UI to show a dry-run preview before applying)."""
    records = load_site_records(handle, sito)
    desired = [build_con_record(c, schedatore=schedatore, lang=lang)
               for c in scan_candidates(records)]
    return diff_continuity(load_existing_con(handle, sito), desired)


def auto_backup(handle, tag="genera_continuita"):
    """Best-effort pre-write backup. SQLite → file copy; PG → pg_dump.
    Returns the backup path, or None when skipped (caller may warn)."""
    from pathlib import Path
    try:
        from scripts.migrations._common import (
            auto_backup_sqlite, auto_backup_postgres, BackupSkipped)
    except Exception:
        return None
    try:
        if handle.is_postgres:
            return auto_backup_postgres(handle.engine, tag, Path.cwd())
        if handle.sqlite_path:
            return auto_backup_sqlite(Path(handle.sqlite_path), tag)
    except Exception:
        # Best-effort: never block the write for any backup failure
        # (BackupSkipped, IOError, OSError, CalledProcessError, etc.)
        return None
    return None


def generate_continuity(handle, sito, *, schedatore="", lang="it",
                        remove_orphans=False, do_backup=False) -> Report:
    """End-to-end: build plan, optionally back up, apply, return Report."""
    plan = build_plan(handle, sito, schedatore=schedatore, lang=lang)
    if do_backup and (plan.to_create or plan.to_update or
                      (remove_orphans and plan.orphan)):
        auto_backup(handle)
    return apply_plan(handle, plan, sito,
                      remove_orphans=remove_orphans, lang=lang)
