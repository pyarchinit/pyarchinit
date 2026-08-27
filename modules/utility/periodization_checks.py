"""Sanity checks on ``periodizzazione_table`` chronologies.

pyArchInit stores years as signed integers (BC = negative, see tutorial
04 "Scheda periodizzazione"). A period whose *cron_iniziale* is later
than its *cron_finale* (e.g. ``1650 → 1450``) is almost always a BC
period typed without the minus sign: it sorts as "AD 1650" and lands
above the Roman periods in the Extended Matrix swimlane and in the DOT
period clusters (Ventena DB, 2026-08-27). Pure module, no Qt.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence


@dataclass(frozen=True)
class SuspiciousChronology:
    periodo: object
    fase: object
    cron_iniziale: int
    cron_finale: int
    label: str = ""


def _as_int(value) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def suspicious_chronologies(rows: Iterable[Sequence]) -> List[SuspiciousChronology]:
    """Rows ``(periodo, fase, cron_iniziale, cron_finale[, label])`` whose
    start year is later than the end year. Non-numeric/None years are
    skipped (nothing to compare)."""
    found = []
    for row in rows:
        periodo, fase, ini, fin = row[0], row[1], row[2], row[3]
        label = str(row[4]) if len(row) > 4 and row[4] is not None else ""
        ini_i, fin_i = _as_int(ini), _as_int(fin)
        if ini_i is None or fin_i is None:
            continue
        if ini_i > fin_i:
            found.append(SuspiciousChronology(periodo, fase, ini_i, fin_i, label))
    return found


_TEXTS = {
    'it': (
        "Periodizzazione: {n} periodo/i con cronologia iniziale maggiore "
        "della finale:\n{items}\n\nProbabili date a.C. inserite senza il "
        "segno meno (a.C. = numeri negativi, es. -1650): l'ordine delle "
        "epoche nel matrix e nel GraphML risulterà sbagliato. Correggi i "
        "valori nella scheda Periodizzazione.",
        "Periodo {p} Fase {f}: {ini} → {fin}{label}"),
    'en': (
        "Periodization: {n} period(s) whose start chronology is later than "
        "the end:\n{items}\n\nMost likely BC years entered without the "
        "minus sign (BC = negative numbers, e.g. -1650): the epoch order in "
        "the matrix and in the GraphML will be wrong. Fix the values in the "
        "Periodization form.",
        "Period {p} Phase {f}: {ini} → {fin}{label}"),
    'de': (
        "Periodisierung: {n} Periode(n) mit Anfangschronologie später als "
        "Endchronologie:\n{items}\n\nWahrscheinlich v. Chr.-Jahre ohne "
        "Minuszeichen (v. Chr. = negative Zahlen, z. B. -1650): die "
        "Reihenfolge der Epochen in Matrix und GraphML wird falsch sein. "
        "Bitte die Werte im Periodisierungsformular korrigieren.",
        "Periode {p} Phase {f}: {ini} → {fin}{label}"),
}


def format_chronology_warning(bad: Sequence[SuspiciousChronology],
                              lang: str = 'it') -> str:
    """Human-readable warning (it / en / de, English fallback)."""
    template, item_fmt = _TEXTS.get((lang or 'en')[:2].lower(), _TEXTS['en'])
    items = "\n".join(
        item_fmt.format(p=b.periodo, f=b.fase, ini=b.cron_iniziale,
                        fin=b.cron_finale,
                        label=f" ({b.label})" if b.label else "")
        for b in bad)
    return template.format(n=len(bad), items=items)
