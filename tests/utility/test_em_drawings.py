"""Piante e prospetti dai proxy 3D: la geometria (spec 2026-10-18, D3–D7, D9)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import em_drawings as drw  # noqa: E402


def _cubo(x0, y0, z0, dx, dy, dz):
    """Triangoli di una scatola nel sistema della MAPPA (Z in alto)."""
    v = np.array([(x0 + i * dx, y0 + j * dy, z0 + k * dz)
                  for i in (0, 1) for j in (0, 1) for k in (0, 1)], dtype=float)
    f = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
         (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return v[np.array(f)]


def _grafo(epsg=31700, sx=327300.0, sy=448370.0, sz=500.0, rot=0.0):
    from s3dgraphy import api
    from s3dgraphy.graph import Graph
    g = Graph(graph_id="T")
    if epsg is not None:
        api.declare_georeference(g, epsg, sx, sy, sz, rot)
    return g


def test_da_glTF_a_Z_in_alto():
    tri = np.array([[[1.0, 2.0, 3.0], [0, 0, 0], [0, 0, 0]]])
    assert np.allclose(drw.scene_from_gltf(tri)[0, 0], (1.0, -3.0, 2.0))


def test_la_posizione_dell_em_json():
    geo = drw.georef_of(_grafo())
    assert geo.usable and geo.epsg == 31700 and geo.shift_z == 500.0
    assert not drw.georef_of(_grafo(epsg=None)).usable
    legacy = drw.georef_of(_grafo(epsg=4326, sx=0.0, sy=0.0, sz=0.0))
    assert legacy.state == "legacy_default" and not legacy.usable


def test_sulla_mappa_come_s3dgraphy():
    from s3dgraphy import api
    for rot in (0.0, 90.0, 33.0):
        g = _grafo(rot=rot)
        geo = drw.georef_of(g)
        pts = np.array([[1.0, 2.0, 3.0], [-4.0, 5.0, -6.0]])
        fuori = drw.place(g, geo, pts, shift_z=geo.shift_z)
        attesi = api.georeference_scene(g, [(1.0, 2.0), (-4.0, 5.0)], epsg_target=31700)["points"]
        assert np.allclose(fuori[:, :2], attesi)
        assert np.allclose(fuori[:, 2], (503.0, 494.0))


def test_senza_posizione_restano_locali():
    g = _grafo(epsg=None)
    fuori = drw.place(g, drw.georef_of(g), np.array([[1.0, 2.0, 3.0]]), shift_z=0.0)
    assert np.allclose(fuori, (1.0, 2.0, 3.0))


def test_che_sistema_e():
    assert drw.crs_kind(31700) == "metric" and drw.crs_kind(3004) == "metric"
    assert drw.crs_kind(4326) == "geographic"
    for s in (-1, 0, None, "", 99999999):
        assert drw.crs_kind(s) == "undefined"


def test_la_pianta_di_una_scatola():
    g = drw.plan_geometry(_cubo(10.0, 20.0, 0.0, 2.0, 3.0, 5.0))
    assert g is not None and g.isMultipart()
    assert g.area() == pytest.approx(6.0, abs=1e-6)


def test_la_pianta_di_un_anello_ha_il_buco():
    esterno = _cubo(0.0, 0.0, 0.0, 4.0, 4.0, 1.0)
    # anello: quattro scatole attorno a un buco 2 × 2
    pezzi = [_cubo(0, 0, 0, 4, 1, 1), _cubo(0, 3, 0, 4, 1, 1), _cubo(0, 1, 0, 1, 2, 1), _cubo(3, 1, 0, 1, 2, 1)]
    g = drw.plan_geometry(np.concatenate(pezzi))
    assert g.area() == pytest.approx(12.0, abs=1e-6)
    poligono = g.asMultiPolygon()[0]
    assert len(poligono) == 2                                  # anello esterno + un buco
    assert drw.plan_geometry(esterno).area() == pytest.approx(16.0, abs=1e-6)


def test_un_piano_verticale_non_ha_pianta():
    muro = np.array([[[0, 0, 0], [5, 0, 0], [5, 0, 3]], [[0, 0, 0], [5, 0, 3], [0, 0, 3]]], dtype=float)
    assert drw.plan_geometry(muro) is None


def test_le_briciole_si_tolgono():
    briciola = np.array([[[0, 0, 0], [0.005, 0, 0], [0, 0.005, 0]]], dtype=float)
    assert drw.plan_geometry(briciola) is None


def _u(view, x, y):
    return x * view.r[0] + y * view.r[1]


def test_i_quattro_lati_chi_sta_a_sinistra():
    n, e, s, w = (drw.SITE_VIEWS[k] for k in ("N", "E", "S", "W"))
    assert _u(n, 10, 0) < _u(n, -10, 0)        # da nord: est a sinistra
    assert _u(e, 0, -10) < _u(e, 0, 10)        # da est: sud a sinistra
    assert _u(s, -10, 0) < _u(s, 10, 0)        # da sud: ovest a sinistra
    assert _u(w, 0, 10) < _u(w, 0, -10)        # da ovest: nord a sinistra


def test_la_rosa_a_otto_punti():
    assert [drw.rose8(*v) for v in ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))] == \
        ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def test_il_prospetto_di_un_muro_lo_guarda_di_fronte_dal_centro():
    muro = _cubo(-10.0, 20.0, 0.0, 20.0, 1.0, 3.0)            # muro lungo in X, a nord del centro
    pianta = drw.plan_geometry(muro)
    v = drw.unit_view("3D-PRO-US1", pianta, drw.centroid_xy(muro), (0.0, 0.0))
    assert v.d == pytest.approx((0.0, 1.0), abs=1e-9) and v.side == "S"
    sagoma = drw.view_geometry(muro, v, (-10.0, 0.0))
    assert sagoma.area() == pytest.approx(60.0, abs=1e-6)     # 20 m × 3 m


def test_un_unita_quasi_quadrata_si_guarda_dal_centro():
    cubo = _cubo(10.0, 10.0, 0.0, 2.0, 2.0, 2.0)
    v = drw.unit_view("x", drw.plan_geometry(cubo), drw.centroid_xy(cubo), (0.0, 0.0))
    assert v.d == pytest.approx((2 ** -0.5, 2 ** -0.5)) and v.side == "SW"
    centro = drw.unit_view("y", drw.plan_geometry(cubo), (11.0, 11.0), (11.0, 11.0))
    assert centro.d == (0.0, 1.0)


def test_la_sagoma_del_lato_nord():
    scatola = _cubo(0.0, 0.0, 490.0, 2.0, 1.0, 3.0)
    g = drw.view_geometry(scatola, drw.SITE_VIEWS["N"], (0.0, 0.0))
    bb = g.boundingBox()
    assert g.area() == pytest.approx(6.0, abs=1e-6)
    assert bb.yMinimum() == pytest.approx(490.0) and bb.yMaximum() == pytest.approx(493.0)


def test_dal_piu_lontano_al_piu_vicino():
    nord, sud = _cubo(0, 50, 0, 1, 1, 1), _cubo(0, -50, 0, 1, 1, 1)
    vista = drw.SITE_VIEWS["N"]                    # chi guarda sta a nord: il cubo a nord è il più vicino
    assert drw.depth(sud, vista) > drw.depth(nord, vista)


def test_l_ingombro_del_sito():
    origine, centro = drw.site_frame([_cubo(0, 0, 0, 2, 2, 1), _cubo(10, -4, 0, 2, 2, 1)])
    assert origine == (0.0, -4.0) and centro == (6.0, -1.0)


def test_i_disegni_uno_accanto_all_altro():
    assert drw.lay_out([(5.0, 15.0), (-3.0, 2.0), (0.0, 1.0)], gap=10.0) == [-5.0, 23.0, 35.0]


def test_spostare_un_disegno():
    from qgis.core import QgsGeometry
    g = QgsGeometry.fromWkt("MULTIPOLYGON(((0 0,1 0,1 1,0 0)))")
    assert drw.span_u(drw.translated(g, 5.0)) == (5.0, 6.0)
    assert drw.span_u(g) == (0.0, 1.0)              # l'originale resta com'era


def test_i_nomi_dei_documenti():
    assert drw.side_name("N") == "3D-PRO-N" and drw.PLAN_NAME == "3D-PLA"
    nomi = drw.unit_drawing_names([("a", "US", "002", "1"), ("b", "USVn", "106", "1"),
                                   ("c", "US", "002", "2")])
    assert nomi == {"a": "3D-PRO-US002-A1", "b": "3D-PRO-USVn106", "c": "3D-PRO-US002-A2"}
    assert drw.is_derived_name("3D-PRO-N") and drw.is_derived_name(" 3D-PLA ")
    assert not drw.is_derived_name("3D-PIANTA") and not drw.is_derived_name("PR001")


def test_i_nomi_dei_documenti_non_hanno_spazi_ne_barre():
    nome = drw.unit_drawing_names([("a", "US", "2/a b", "1")])["a"]
    assert nome == "3D-PRO-US2-a_b" and drw.is_derived_name(nome)


def test_le_coppie_ricavate_fuori_dall_em_json():
    v = "[['Fotografie', 'Si'], ['Prospetto', '3D-PRO-N'], ['Sezione', 'AA1']]"
    assert drw.without_derived_pairs(v) == "[['Fotografie', 'Si'], ['Sezione', 'AA1']]"
    for intatto in (None, "", "[['Fotografie', 'Si']]", "non si legge [", "Fotografie: Si"):
        assert drw.without_derived_pairs(intatto) == intatto


def test_le_coppie_ricavate_di_adesso_al_posto_di_quelle_di_prima():
    prima = "[['Fotografie', 'Si'], ['Planimetria', '3D-PLA'], ['Prospetto', '3D-PRO-US002']]"
    dopo = drw.with_derived_pairs(prima, [["Planimetria", "3D-PLA"], ["Prospetto", "3D-PRO-N"]])
    assert dopo == "[['Fotografie', 'Si'], ['Planimetria', '3D-PLA'], ['Prospetto', '3D-PRO-N']]"
    assert drw.with_derived_pairs(None, [["Prospetto", "3D-PRO-N"]]) == "[['Prospetto', '3D-PRO-N']]"
    assert drw.with_derived_pairs("rotto [", [["Prospetto", "3D-PRO-N"]]) is None
    assert drw.with_derived_pairs(prima, []) == "[['Fotografie', 'Si']]"


def test_al_reimport_le_coppie_ricavate_restano():
    vecchio = "[['Fotografie', 'Si'], ['Prospetto', '3D-PRO-N']]"
    assert drw.merge_derived_pairs("[['Fotografie', 'Si'], ['Sezione', 'B']]", vecchio) == \
        "[['Fotografie', 'Si'], ['Sezione', 'B'], ['Prospetto', '3D-PRO-N']]"
    assert drw.merge_derived_pairs("[['Fotografie', 'Si']]", None) == "[['Fotografie', 'Si']]"
    assert drw.merge_derived_pairs("rotto [", vecchio) == "rotto ["


def test_i_nomi_non_si_scontrano_e_tengono_le_lettere():
    """Minori della revisione: «2/a» e «2-a» nella stessa area davano lo
    stesso nome, e le lettere non ASCII diventavano «_»."""
    nomi = drw.unit_drawing_names([("a", "US", "2/a", "1"), ("b", "US", "2-a", "1"),
                                   ("c", "US", "ü1", "1")])
    assert len(set(nomi.values())) == 3
    assert nomi["c"] == "3D-PRO-USü1"
    assert all(drw.is_derived_name(n) for n in nomi.values())
    rovescio = drw.unit_drawing_names([("c", "US", "ü1", "1"), ("b", "US", "2-a", "1"),
                                       ("a", "US", "2/a", "1")])
    assert rovescio == nomi                                    # non dipende dall'ordine


def test_un_unita_non_prende_il_nome_di_un_lato():
    """Un'unità senza tipo e con US «N» darebbe «3D-PRO-N», il prospetto nord del sito."""
    nomi = drw.unit_drawing_names([("a", "", "N", "1"), ("b", "US", "1", "1")])
    assert nomi["a"] not in {drw.side_name(x) for x in drw.SIDES}
    assert nomi["a"].startswith("3D-PRO-N") and drw.is_derived_name(nomi["a"])
