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
    """Order-insensitive normalised form of a rapporti value for compare."""
    from .rapporti import _coerce_to_list
    rows = []
    for e in _coerce_to_list(value):
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            rows.append((str(e[0]).strip(), str(e[1]).strip()))
    return sorted(rows)


def _record_matches(existing: dict, desired: dict) -> bool:
    for f in _COMPARE_FIELDS:
        if _nz(existing.get(f)) != _nz(desired.get(f)):
            return False
    return _norm_rapporti(existing.get("rapporti")) == \
        _norm_rapporti(desired.get("rapporti"))


def diff_continuity(existing_con: dict, desired: list) -> Plan:
    """Compare desired CON records against existing ones (keyed by us)."""
    plan = Plan()
    desired_keys = set()
    for d in desired:
        key = d["us"]
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
