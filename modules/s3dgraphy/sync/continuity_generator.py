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

from dataclasses import dataclass

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
