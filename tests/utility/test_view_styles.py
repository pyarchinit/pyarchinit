"""Il registro delle viste di pyArchInit, le ricette delle etichette e la
scelta dello stile (13 ottobre 2026, spec «Stili delle viste»). Modulo
puro: niente Qt, niente QGIS."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import view_styles as vs  # noqa: E402

CARICATE = ("pyarchinit_us_view", "pyarchinit_usm_view", "pyarchinit_quote_view",
            "pyarchinit_quote_usm_view", "pyarchinit_doc_view", "pyarchinit_doc_view_b",
            "pyarchinit_us_negative_doc_view", "pyarchinit_strutture_view", "pyarchinit_tomba_view",
            "pyarchinit_individui_view", "pyarchinit_ut_point_view", "pyarchinit_ut_line_view",
            "pyarchinit_ut_polygon_view", "pyarchinit_site_view", "pyarchinit_siti_polygonal_view",
            "pyarchinit_reperti_view", "pyarchinit_sezioni_view")


def test_ogni_vista_caricata_dal_plugin_sta_nel_registro():
    nomi = [v.name for v in vs.VIEWS]
    assert set(CARICATE) <= set(nomi), sorted(set(CARICATE) - set(nomi))
    assert len(nomi) == len(set(nomi))
    for v in vs.VIEWS:
        assert v.geometry in ("polygon", "line", "point"), v.name
        assert v.label.get("it") and v.label.get("en"), v.name
        assert v.group in vs.GROUPS, v.name
        assert vs.view_by_name(v.name) is v
    assert vs.view_by_name("pyarchinit_che_non_esiste") is None
    assert [g for g in vs.GROUPS] == ["unita", "quote", "documentazione", "strutture", "ut", "siti", "reperti", "sezioni"]


def test_le_ricette_di_partenza_us_e_quote():
    assert vs.view_by_name("pyarchinit_us_view").recipe == "us_circle"
    assert vs.view_by_name("pyarchinit_usm_view").recipe == "us_circle"
    assert vs.view_by_name("pyarchinit_quote_view").recipe == "quota"
    assert vs.view_by_name("pyarchinit_quote_usm_view").recipe == "quota"
    assert vs.view_by_name("pyarchinit_strutture_view").recipe is None
    assert vs.view_by_name("pyarchinit_quote_view").geometry == "point"
    assert vs.view_by_name("pyarchinit_ut_line_view").geometry == "line"
    assert vs.view_by_name("pyarchinit_us_view").site_field == "scavo_s"
    assert vs.view_by_name("pyarchinit_quote_view").site_field == "sito_q"
    assert "d_stratigrafica" in vs.view_by_name("pyarchinit_us_view").category_fields


def test_i_qml_dichiarati_esistono():
    cartella = _ROOT / "modules" / "gis" / "styles_spatialite"
    dichiarati = [v for v in vs.VIEWS if v.qml]
    assert {v.name for v in dichiarati} >= {"pyarchinit_us_view", "pyarchinit_quote_view"}
    for v in dichiarati:
        assert (cartella / v.qml).is_file(), v.qml


def test_la_ricetta_fa_il_giro_del_json():
    r = vs.LabelRecipe(enabled=True, preset="field", expression='"us"', placement="around_point",
                       offset_mm=1.5, one_per_unit=False)
    assert vs.LabelRecipe.from_json(r.to_json()) == r
    assert vs.LabelRecipe.from_json("") == vs.LabelRecipe()              # vuota: spenta
    assert vs.LabelRecipe.from_json("{non json") == vs.LabelRecipe()
    assert vs.LabelRecipe.from_json(None) == vs.LabelRecipe()
    d = vs.default_recipe(vs.view_by_name("pyarchinit_us_view"))
    assert d.enabled and d.preset == "us_circle" and d.one_per_unit
    q = vs.default_recipe(vs.view_by_name("pyarchinit_quote_view"))
    assert q.enabled and q.preset == "quota" and not q.one_per_unit
    assert not vs.default_recipe(vs.view_by_name("pyarchinit_strutture_view")).enabled
    assert set(vs.PRESETS) == {"none", "us_circle", "quota", "field"}
    assert set(vs.PLACEMENTS) == {"centroid", "around_point", "above_symbol"}


def _stile(id, site, is_default, name="s"):
    return vs.SavedStyle(id=id, view_name="pyarchinit_us_view", site=site, name=name, qml="<qgis/>",
                         recipe=vs.LabelRecipe(), is_default=is_default, author="", updated_at="")


def test_la_scelta_dello_stile_sito_poi_tutti_poi_niente():
    tutti = _stile(1, None, True)
    scavo = _stile(2, "Scavo", True)
    altro = _stile(3, "Altro", True)
    non_pred = _stile(4, "Scavo", False)
    assert vs.choose_style([tutti, scavo, altro, non_pred], "Scavo") is scavo
    assert vs.choose_style([tutti, altro, non_pred], "Scavo") is tutti
    assert vs.choose_style([altro, non_pred], "Scavo") is None
    assert vs.choose_style([non_pred], None) is None
    assert vs.choose_style([tutti], None) is tutti
    assert vs.choose_style([], "Scavo") is None
