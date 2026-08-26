"""US sheet / US index PDF must survive records with hundreds of relations.

Bug report (2026-08-26, DB with 1311 US): US 8 has 544 "Tagliato da" and
US 143 has 545 "Copre". The ICCD sheet is one big ReportLab ``Table`` whose
rows 13-22 (the stratigraphic-relations block) are locked together by
row-spans, so the block cannot be split across pages — when the relation
cells grow past the frame ReportLab raises
``LayoutError: Flowable ... too large on page``. The US index list failed
the same way (one 3282-pt row). ``splitInRow=1`` was rejected: it "works"
but emits one line per page (45 pages for US 8).

Fix: relation strings are capped at ``MAX_INLINE_RAPPORTI`` targets in the
sheet cells (with a "see annex" marker) and the full lists are printed in
an annex table appended after the sheet, which splits by row.

The PDF module imports ``qgis`` and the plugin ``Connection``; both are
stubbed here so the tests run under the plain test interpreter.
"""
from __future__ import annotations

import io
import os
import re
import sys
import types
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _install_stubs():
    if "qgis.PyQt.QtWidgets" not in sys.modules:
        qgis = types.ModuleType("qgis")
        pyqt = types.ModuleType("qgis.PyQt")
        qtw = types.ModuleType("qgis.PyQt.QtWidgets")

        class QMessageBox:  # never shown in tests
            @staticmethod
            def warning(*_a, **_k):
                return None

        qtw.QMessageBox = QMessageBox
        pyqt.QtWidgets = qtw
        qgis.PyQt = pyqt
        sys.modules.update(
            {"qgis": qgis, "qgis.PyQt": pyqt, "qgis.PyQt.QtWidgets": qtw})
    if "modules.db.pyarchinit_conn_strings" not in sys.modules:
        cs = types.ModuleType("modules.db.pyarchinit_conn_strings")

        class Connection:
            def logo_path(self):
                return {"logo": ""}

        cs.Connection = Connection
        sys.modules["modules.db.pyarchinit_conn_strings"] = cs
    # The sheet builders load <PYARCHINIT_HOME>/pyarchinit_DB_folder/logo.jpg
    import tempfile
    from PIL import Image as _PILImage
    home = Path(tempfile.mkdtemp(prefix="pyarchinit_pdf_test_"))
    (home / "pyarchinit_DB_folder").mkdir()
    _PILImage.new("RGB", (20, 20), "white").save(
        home / "pyarchinit_DB_folder" / "logo.jpg")
    os.environ["PYARCHINIT_HOME"] = str(home)
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))


_install_stubs()
pdfmod = pytest.importorskip("modules.utility.pyarchinit_exp_USsheet_pdf")

from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import PageBreak, SimpleDocTemplate, Table  # noqa: E402

N_FIELDS = 115  # length of the list built by US_USM.generate_list_pdf


def _record(rapporti, unita_tipo="US", us="8"):
    data = [""] * N_FIELDS
    data[0], data[1], data[2] = "Sito test", "1", us
    data[3] = "strato"
    data[5] = "descrizione " * 40
    data[17] = str(rapporti)
    data[29] = unita_tipo
    return data


def _many(kind, n, start=100):
    return [[kind, str(i), "1", "Sito test"] for i in range(start, start + n)]


def _build_pages(flowables) -> int:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=(21 * cm, 29 * cm), topMargin=10,
                            bottomMargin=20, leftMargin=10, rightMargin=10)
    doc.build(flowables, canvasmaker=pdfmod.NumberedCanvas_USsheet)
    return len(re.findall(rb"/Type\s*/Page[^s]", buf.getvalue()))


def _table_text(flowables) -> str:
    out = []
    for f in flowables:
        if isinstance(f, Table):
            for row in f._cellvalues:
                for cell in row:
                    out.append(getattr(cell, "text", str(cell)))
        else:
            out.append(getattr(f, "text", ""))
    return "\n".join(out)


# --- regression: the reported records must print -------------------------

@pytest.mark.parametrize("kind", ["Tagliato da", "Copre"])
def test_it_sheet_with_hundreds_of_relations_builds(kind):
    sheet = pdfmod.single_US_pdf_sheet(_record(_many(kind, 545)))
    table = sheet.create_sheet_archeo3_usm_fields_2()
    flow = [table] + sheet.create_rapporti_annex("it") + [PageBreak()]
    pages = _build_pages(flow)
    assert 1 <= pages <= 6, pages  # 45 pages with splitInRow, LayoutError before


@pytest.mark.parametrize("method,lang", [
    ("create_sheet_en", "en"), ("create_sheet_de", "de"),
    ("create_sheet_fr", "fr"), ("create_sheet_es", "es"),
])
def test_other_language_sheets_build(method, lang):
    sheet = pdfmod.single_US_pdf_sheet(_record(_many("Copre", 545)))
    table = getattr(sheet, method)()
    pages = _build_pages([table] + sheet.create_rapporti_annex(lang)
                         + [PageBreak()])
    assert 1 <= pages <= 6, pages


def test_usm_sheet_with_hundreds_of_relations_builds():
    sheet = pdfmod.single_US_pdf_sheet(
        _record(_many("Si appoggia a", 545), unita_tipo="USM"))
    table = sheet.create_sheet_archeo3_usm_fields_2()
    pages = _build_pages([table] + sheet.create_rapporti_annex("it")
                         + [PageBreak()])
    assert 1 <= pages <= 6, pages


# --- the cap + annex contract --------------------------------------------

def test_inline_cell_is_capped_and_annex_has_every_target():
    n = 545
    sheet = pdfmod.single_US_pdf_sheet(_record(_many("Tagliato da", n)))
    sheet.create_sheet_archeo3_usm_fields_2()
    cap = pdfmod.MAX_INLINE_RAPPORTI
    inline = sheet.tagliato_da
    shown = inline.split(" …")[0]
    assert shown.count(", ") == cap - 1, shown
    assert "allegato" in inline.lower()
    assert str(n - cap) in inline  # "+465" count of hidden targets
    annex = sheet.create_rapporti_annex("it")
    assert annex, "annex expected for an overflowing record"
    text = _table_text(annex)
    for i in range(100, 100 + n):
        assert re.search(rf"\b{i}\b", text), f"target {i} missing from annex"
    assert "TAGLIATO DA" in text.upper()


def test_small_record_is_unchanged_and_has_no_annex():
    rels = [["Copre", "2", "1", "S"], ["Copre", "5", "1", "S"],
            ["Tagliato da", "9", "1", "S"]]
    sheet = pdfmod.single_US_pdf_sheet(_record(rels))
    sheet.create_sheet_archeo3_usm_fields_2()
    assert sheet.copre == "2, 5"
    assert sheet.tagliato_da == "9"
    assert sheet.create_rapporti_annex("it") == []


def test_cap_boundary_exactly_max_is_inline():
    cap = pdfmod.MAX_INLINE_RAPPORTI
    sheet = pdfmod.single_US_pdf_sheet(_record(_many("Copre", cap)))
    sheet.create_sheet_archeo3_usm_fields_2()
    assert "allegato" not in sheet.copre.lower()
    assert sheet.create_rapporti_annex("it") == []
    sheet2 = pdfmod.single_US_pdf_sheet(_record(_many("Copre", cap + 1)))
    sheet2.create_sheet_archeo3_usm_fields_2()
    assert "allegato" in sheet2.copre.lower()
    assert len(sheet2.create_rapporti_annex("it")) > 0


# --- US index list --------------------------------------------------------

def test_index_list_with_hundreds_of_relations_builds():
    recs = [_record(_many("Tagliato da", 545), us="8"),
            _record(_many("Copre", 545), us="143"),
            _record([["Copre", "2", "1", "S"]], us="3")]
    rows = []
    for r in recs:
        exp = pdfmod.US_index_pdf_sheet(r)
        rows.append(exp.getTable())
    styles = exp.makeStyles()
    col_widths = [30, 28, 118, 45, 58, 45, 58, 55, 64, 64, 52, 52, 52]
    table = Table(rows, col_widths, style=styles)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=(29.7 * cm, 21 * cm), topMargin=10,
                            bottomMargin=20, leftMargin=10, rightMargin=10)
    doc.build([table], canvasmaker=pdfmod.NumberedCanvas_USindex)
    assert buf.getvalue()
