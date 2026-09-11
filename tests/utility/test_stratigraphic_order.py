"""Drawing order of the US/USM layers, computed like the Time Manager (2026-09-11).

The Time Manager reads order_layer as time going up (0 = oldest, N = most
recent: "order_layer <= v" builds the site up level by level) and places a
US in time through the chronology (cron_iniziale) of its periodo_iniziale /
fase_iniziale in periodizzazione_table. The map draws the same way: the
oldest first (underneath), the most recent last (on top). In the views
periodo/fase are text ('2', '2.1'), in periodizzazione_table numbers.
Pure Python.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import stratigraphic_order as so  # noqa: E402

# sito, periodo, fase, cron_iniziale, cont_per
ROWS = [("S", 1, 1, 1800, 1), ("S", 1, 2, 1600, 2), ("S", 2, 1, 1550, 3),
        ("S", 2, 2.1, 1451, 11), ("T", 2, 1, 100, 3)]


def test_text_periods_of_the_us_match_the_numeric_periodization():
    starts = so.period_starts(ROWS)
    assert so.period_start(starts, "S", "2", "1", "") == 1550
    assert so.period_start(starts, "S", "2", "2.1", None) == 1451
    assert so.period_start(starts, "S", 2, 2.1, None) == 1451


def test_each_site_has_its_own_chronology():
    starts = so.period_starts(ROWS)
    assert so.period_start(starts, "T", "2", "1", "") == 100


def test_a_period_without_phase_starts_with_its_oldest_phase():
    assert so.period_start(so.period_starts(ROWS), "S", "1", None, None) == 1600


def test_cont_per_is_the_fallback_and_its_oldest_code_wins():
    starts = so.period_starts(ROWS)
    assert so.period_start(starts, "S", None, None, "2/3") == 1550
    assert so.period_start(starts, "S", "", "", "1") == 1800


def test_an_unknown_period_has_no_start():
    starts = so.period_starts(ROWS)
    assert so.period_start(starts, "S", "9", "9", "") is None
    assert so.period_start(starts, "X", "2", "1", "3") is None


def test_the_case_expression_uses_the_exact_values_of_the_layer():
    expr = so.period_case([
        ({"sito": "S", "periodo_iniziale": "2", "fase_iniziale": "1"}, 1550),
        ({"sito": "O'Hara", "periodo_iniziale": None, "fase_iniziale": 3}, 7),
        ({"sito": "S", "periodo_iniziale": "9", "fase_iniziale": "9"}, None),
    ])
    assert expr == ('CASE WHEN "sito" = \'S\' AND "periodo_iniziale" = \'2\' AND "fase_iniziale" = \'1\' THEN 1550 '
                    'WHEN "sito" = \'O\'\'Hara\' AND "periodo_iniziale" IS NULL AND "fase_iniziale" = 3 THEN 7 END')
    assert so.period_case([({"periodo_iniziale": "9"}, None)]) is None


def test_order_like_the_time_manager():
    assert so.order_clauses(["order_layer", "stratigraph_index_us"], "CASE WHEN 1 THEN 2 END") == [
        ("CASE WHEN 1 THEN 2 END", True, True),      # undated first (underneath), oldest period first
        ('"order_layer"', True, False),              # 0 = oldest ... N = most recent (on top)
        ('"stratigraph_index_us"', True, False),     # the cut (2) over its fill (1)
    ]
    assert so.order_clauses(["order_layer"]) == [('"order_layer"', True, False)]
    assert so.order_clauses(["us"]) == []
