"""Multi-page "poster" PDF for Harris matrices wider than any sheet.

A 1311-US matrix laid out by graphviz is 46 740 x 7 250 pt (16.5 m x
2.6 m at 1:1): no printer takes it and PDF viewers clip pages beyond
200 in. This module tiles the single-page vector PDF produced by graphviz
onto A0/A1/A2/A3 sheets (2 cm overlap, "foglio n/N" label) so the matrix
can be printed on a plotter and assembled. Default: A0, one row of sheets
scaled so the matrix height fills the page ("adatta all'altezza").

``plan_poster`` is pure arithmetic (unit-tested); ``build_poster_pdf``
needs PyMuPDF (``fitz``), a declared plugin dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

#: ISO 216 sheets, portrait, in points.
PAPER_PT = {
    'A0': (2384, 3370),
    'A1': (1684, 2384),
    'A2': (1191, 1684),
    'A3': (842, 1191),
    'A4': (595, 842),
}
#: (mode key, Italian label shown in Setting_Matrix) — order = combo order.
POSTER_SCALE_MODES = [
    ('fit_height', "Adatta all'altezza"),
    ('fit_page', 'Adatta alla pagina'),
    ('1:1', '1:1'),
    ('1:2', '1:2'),
    ('1:3', '1:3'),
]
#: overlap between neighbouring sheets (2 cm) and page margin, in points.
OVERLAP_PT = 57
MARGIN_PT = 20


@dataclass
class Tile:
    col: int
    row: int
    #: window on the source page, points (x0, y0, x1, y1)
    clip: Tuple[float, float, float, float]
    #: where that window lands on the sheet, points (x0, y0, x1, y1)
    target: Tuple[float, float, float, float]


@dataclass
class PosterPlan:
    paper: str
    landscape: bool
    page_w: int
    page_h: int
    scale: float
    cols: int
    rows: int
    tiles: List[Tile] = field(default_factory=list)

    @property
    def pages(self) -> int:
        return len(self.tiles)

    def describe(self) -> str:
        return (f"{self.paper} {'orizzontale' if self.landscape else 'verticale'}, "
                f"{self.rows} x {self.cols} = {self.pages} fogli, "
                f"scala 1:{1 / self.scale:.1f}")


def _scale_for(mode: str, content_w: float, content_h: float,
               usable_w: float, usable_h: float) -> float:
    if mode == 'fit_height':
        scale = usable_h / content_h
    elif mode == 'fit_width':
        scale = usable_w / content_w
    elif mode == 'fit_page':
        scale = min(usable_w / content_w, usable_h / content_h)
    elif ':' in mode:
        num, den = mode.split(':', 1)
        scale = float(num) / float(den)
    else:
        raise ValueError(f"unknown poster scale mode {mode!r}")
    return min(scale, 1.0)  # never enlarge


def _plan(content_w, content_h, paper, landscape, mode, overlap_pt, margin_pt):
    pw, ph = PAPER_PT[paper]
    if landscape:
        pw, ph = ph, pw
    usable_w, usable_h = pw - 2 * margin_pt, ph - 2 * margin_pt
    scale = _scale_for(mode, content_w, content_h, usable_w, usable_h)
    step_w, step_h = usable_w - overlap_pt, usable_h - overlap_pt

    def _count(extent_pt, usable, step):
        """Sheets needed along one axis (each sheet shows *usable* pt of
        page, neighbours overlap by *overlap_pt*)."""
        scaled = extent_pt * scale
        if scaled <= usable:
            return 1
        return max(1, -(-int(round(scaled - overlap_pt)) // int(step)))

    cols = _count(content_w, usable_w, step_w)
    rows = _count(content_h, usable_h, step_h)
    tiles = []
    for r in range(rows):
        y0 = r * step_h / scale
        y1 = min(content_h, y0 + usable_h / scale)
        for c in range(cols):
            x0 = c * step_w / scale
            x1 = min(content_w, x0 + usable_w / scale)
            tiles.append(Tile(
                col=c, row=r,
                clip=(x0, y0, x1, y1),
                target=(margin_pt, margin_pt,
                        margin_pt + (x1 - x0) * scale,
                        margin_pt + (y1 - y0) * scale)))
    return PosterPlan(paper=paper, landscape=landscape, page_w=pw, page_h=ph,
                      scale=scale, cols=cols, rows=rows, tiles=tiles)


def plan_poster(content_w: float, content_h: float, paper: str = 'A0',
                mode: str = 'fit_height', landscape: Optional[bool] = None,
                overlap_pt: int = OVERLAP_PT, margin_pt: int = MARGIN_PT
                ) -> PosterPlan:
    """Tile a *content_w* x *content_h* pt drawing onto *paper* sheets.

    *mode*: ``fit_height`` (one row of sheets, default), ``fit_width``,
    ``fit_page`` (single sheet) or an explicit ``"1:N"`` scale; the drawing
    is never enlarged. *landscape* None → the orientation needing fewer
    sheets (ties → landscape for wide drawings).
    """
    if paper not in PAPER_PT:
        raise ValueError(f"unknown paper size {paper!r}")
    if mode not in {m for m, _ in POSTER_SCALE_MODES} | {'fit_width'}:
        raise ValueError(f"unknown poster scale mode {mode!r}")
    if content_w <= 0 or content_h <= 0:
        raise ValueError("content size must be positive")
    if landscape is not None:
        return _plan(content_w, content_h, paper, landscape, mode,
                     overlap_pt, margin_pt)
    candidates = [_plan(content_w, content_h, paper, ls, mode, overlap_pt,
                        margin_pt) for ls in (content_w >= content_h,
                                              content_w < content_h)]
    return min(candidates, key=lambda p: p.pages)


def build_poster_pdf(src_pdf: str, out_pdf: str, plan: PosterPlan,
                     label: bool = True) -> str:
    """Write *out_pdf*: one sheet per tile of *plan*, cut from page 1 of
    *src_pdf* (vector, lossless). Requires PyMuPDF."""
    import fitz  # PyMuPDF — plugin dependency, imported lazily

    src = fitz.open(src_pdf)
    out = fitz.open()
    try:
        total = plan.pages
        for n, tile in enumerate(plan.tiles, start=1):
            page = out.new_page(width=plan.page_w, height=plan.page_h)
            page.show_pdf_page(fitz.Rect(*tile.target), src, 0,
                               clip=fitz.Rect(*tile.clip))
            if label:
                text = (f"foglio {n}/{total} - riga {tile.row + 1}/{plan.rows}, "
                        f"colonna {tile.col + 1}/{plan.cols} - "
                        f"{plan.paper} scala 1:{1 / plan.scale:.1f}")
                page.insert_text((MARGIN_PT, plan.page_h - 6), text, fontsize=8)
        out.save(out_pdf)
    finally:
        out.close()
        src.close()
    return out_pdf
