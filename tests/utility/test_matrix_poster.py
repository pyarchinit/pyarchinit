"""Unit tests for modules/utility/matrix_poster.py (2026-08-27).

Multi-page "poster" PDF for Harris matrices too wide for a single sheet
(1311-US DB with periods: 46 740 x 7 250 pt = 16.5 m x 2.6 m at 1:1).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.matrix_poster import (  # noqa: E402
    MARGIN_PT, OVERLAP_PT, PAPER_PT, POSTER_SCALE_MODES, build_poster_pdf,
    plan_poster,
)

# root bb of the real period matrix (dpi 72)
W, H = 46740.0, 7250.0


def test_fit_height_makes_a_single_row_strip_on_landscape_a0():
    plan = plan_poster(W, H, paper='A0', mode='fit_height')
    assert plan.rows == 1 and plan.cols == 5 and plan.pages == 5
    assert plan.landscape and (plan.page_w, plan.page_h) == (3370, 2384)
    assert plan.scale == pytest.approx((2384 - 2 * MARGIN_PT) / H)
    # tiles cover the whole width, in order, overlapping by OVERLAP_PT
    assert plan.tiles[0].clip[0] == 0
    assert plan.tiles[-1].clip[2] == pytest.approx(W)
    for a, b in zip(plan.tiles, plan.tiles[1:]):
        assert (a.clip[2] - b.clip[0]) * plan.scale == pytest.approx(OVERLAP_PT)
        assert b.clip[0] > a.clip[0]


def test_fit_page_is_one_sheet_and_1_to_1_needs_sixty():
    one = plan_poster(W, H, paper='A0', mode='fit_page')
    assert one.pages == 1 and one.scale <= (3370 - 2 * MARGIN_PT) / W
    full = plan_poster(W, H, paper='A0', mode='1:1')
    assert full.scale == 1.0 and (full.rows, full.cols) == (4, 15)


def test_small_matrix_is_never_enlarged_and_fits_one_page():
    plan = plan_poster(500, 300, paper='A3', mode='fit_height')
    assert plan.pages == 1 and plan.scale == 1.0


def test_paper_and_mode_tables():
    assert set(PAPER_PT) >= {'A0', 'A1', 'A2', 'A3'}
    assert PAPER_PT['A0'] == (2384, 3370)
    assert [m for m, _label in POSTER_SCALE_MODES][:2] == ['fit_height', 'fit_page']
    with pytest.raises(ValueError):
        plan_poster(W, H, paper='B9')
    with pytest.raises(ValueError):
        plan_poster(W, H, mode='1:x')


def test_build_poster_pdf_writes_one_page_per_tile(tmp_path):
    fitz = pytest.importorskip("fitz")
    src = tmp_path / "wide.pdf"
    doc = fitz.open()
    page = doc.new_page(width=6000, height=2000)
    page.draw_rect(fitz.Rect(10, 10, 5990, 1990), color=(0, 0, 1))
    page.insert_text((5800, 1000), "END", fontsize=40)
    doc.save(str(src)); doc.close()

    plan = plan_poster(6000, 2000, paper='A3', mode='fit_height')
    out = build_poster_pdf(str(src), str(tmp_path / "poster.pdf"), plan)
    with fitz.open(out) as poster:
        assert len(poster) == plan.pages > 1
        for p in poster:
            assert (round(p.rect.width), round(p.rect.height)) == (plan.page_w, plan.page_h)
        assert "END" in poster[-1].get_text()
        assert "1/%d" % plan.pages in poster[0].get_text()
