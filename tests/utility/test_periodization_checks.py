"""Unit tests for modules/utility/periodization_checks.py (2026-08-27).

Ventena DB: BC periods entered as positive years (1650 -> 1450) put the
Bronze Age above the Late Roman period in the GraphML swimlane and in
the DOT period clusters. The tell-tale sign is start > end.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.periodization_checks import (  # noqa: E402
    format_chronology_warning, suspicious_chronologies,
)

ROWS = [
    (1, "1", 1970, 2000, "Età Contemporanea - XXI secolo"),
    (3, "2", 301, 600, "Età Tardoromana"),
    (4, "1", "300", "100", "Tra fine Età del Ferro e Romanizzazione"),  # strings from the ORM
    (5, "1", 1449, 301, "Post Età del Bronzo Medio"),
    (6, "1", -1650, -1450, "Età del Bronzo Medio"),                     # correct BC entry
    (7, None, None, 500, "senza inizio"),
    (8, "1", "abc", 10, "non numerico"),
]


def test_flags_only_rows_whose_start_is_later_than_end():
    bad = suspicious_chronologies(ROWS)
    assert [(b.periodo, b.fase) for b in bad] == [(4, "1"), (5, "1")]
    assert bad[0].cron_iniziale == 300 and bad[0].cron_finale == 100
    assert bad[0].label == "Tra fine Età del Ferro e Romanizzazione"


def test_nothing_flagged_on_clean_table():
    assert suspicious_chronologies([]) == []
    assert suspicious_chronologies(ROWS[:2] + ROWS[4:]) == []


def test_warning_text_names_the_periods_and_the_bc_hint():
    bad = suspicious_chronologies(ROWS)
    it = format_chronology_warning(bad, "it")
    assert "Periodo 4 Fase 1" in it and "300 → 100" in it
    assert "Periodo 5 Fase 1" in it and "1449 → 301" in it
    assert "a.C." in it and "negativ" in it.lower()
    en = format_chronology_warning(bad, "en")
    assert "Period 4 Phase 1" in en and "BC" in en
    de = format_chronology_warning(bad, "de")
    assert "Periode 4 Phase 1" in de and "v. Chr." in de
    # unknown locale falls back to English
    assert format_chronology_warning(bad, "xx") == en
