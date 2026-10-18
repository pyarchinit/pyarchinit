"""Il taglio dei proxy lungo una linea di sezione (spec 2026-10-18 sezioni, S2)."""
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
    v = np.array([(x0 + i * dx, y0 + j * dy, z0 + k * dz)
                  for i in (0, 1) for j in (0, 1) for k in (0, 1)], dtype=float)
    f = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
         (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return v[np.array(f)]


SCATOLA = _cubo(0.0, 0.0, 10.0, 4.0, 2.0, 3.0)


def test_una_scatola_tagliata_a_meta():
    g = drw.section_geometry(SCATOLA, (-1.0, 1.0), (5.0, 1.0))
    bb = g.boundingBox()
    assert g.area() == pytest.approx(12.0, abs=1e-6)
    assert (bb.xMinimum(), bb.xMaximum()) == pytest.approx((1.0, 5.0))
    assert (bb.yMinimum(), bb.yMaximum()) == pytest.approx((10.0, 13.0))


def test_il_taglio_si_ferma_al_tratto():
    g = drw.section_geometry(SCATOLA, (-1.0, 1.0), (2.0, 1.0))
    assert g.area() == pytest.approx(6.0, abs=1e-6)


def test_una_linea_spezzata_continua():
    punti = [(-1.0, 1.0), (2.0, 1.0), (2.0, 5.0)]
    g = drw.section_line_geometry(SCATOLA, punti)
    assert drw.line_length(punti) == pytest.approx(7.0)
    assert g.area() == pytest.approx(6.0 + 3.0, abs=1e-6)
    assert g.boundingBox().xMaximum() == pytest.approx(4.0)        # 3 del primo tratto + 1 del secondo


def test_a_sinistra_c_e_sempre_a():
    avanti = drw.section_geometry(SCATOLA, (-1.0, 1.0), (7.0, 1.0)).boundingBox()
    indietro = drw.section_geometry(SCATOLA, (7.0, 1.0), (-1.0, 1.0)).boundingBox()
    assert (avanti.xMinimum(), avanti.xMaximum()) == pytest.approx((1.0, 5.0))
    assert (indietro.xMinimum(), indietro.xMaximum()) == pytest.approx((3.0, 7.0))


def test_un_modello_aperto_o_lontano_non_da_profilo():
    piano = np.array([[[0, 0, 0], [0, 4, 0], [0, 4, 3]], [[0, 0, 0], [0, 4, 3], [0, 0, 3]]], dtype=float)
    assert drw.section_geometry(piano, (-2.0, 2.0), (2.0, 2.0)) is None
    assert drw.section_geometry(SCATOLA, (-1.0, 50.0), (5.0, 50.0)) is None


def _scatola_a_griglia(x0, y0, z0, dx, dy, dz, n=8):
    """La scatola con ogni faccia divisa in n × n quadrati: i vertici della
    griglia stanno su piani come x = x0 + dx/2."""
    def faccia(o, a, b):
        o, a, b = (np.asarray(v, dtype=float) for v in (o, a, b))
        tri = []
        for i in range(n):
            for j in range(n):
                p00 = o + a * i / n + b * j / n
                p10 = o + a * (i + 1) / n + b * j / n
                p01 = o + a * i / n + b * (j + 1) / n
                p11 = o + a * (i + 1) / n + b * (j + 1) / n
                tri += [(p00, p10, p11), (p00, p11, p01)]
        return tri
    X, Y, Z = (dx, 0, 0), (0, dy, 0), (0, 0, dz)
    o = (x0, y0, z0)
    alto = (x0, y0, z0 + dz)
    fondo = (x0, y0 + dy, z0)
    destra = (x0 + dx, y0, z0)
    tri = (faccia(o, Y, X) + faccia(alto, X, Y) + faccia(o, X, Z) + faccia(fondo, Z, X)
           + faccia(o, Z, Y) + faccia(destra, Y, Z))
    return np.array(tri)


def test_un_vertice_sul_piano_non_rompe_il_taglio():
    """Revisione finale: un piano che passa per i vertici della mesh (linee
    dritte su modelli in coordinate locali) lasciava buchi di 1e-9 nel contorno
    e l'unità spariva dalla sezione."""
    griglia = _scatola_a_griglia(0.0, 0.0, 10.0, 4.0, 2.0, 3.0)
    g = drw.section_geometry(griglia, (2.0, -1.0), (2.0, 3.0))          # x = 2: vertici sul piano
    assert g is not None and g.isGeosValid()
    assert g.area() == pytest.approx(6.0, abs=1e-6)
    g = drw.section_geometry(griglia, (-1.0, 1.0), (5.0, 1.0))          # y = 1: anche
    assert g is not None and g.area() == pytest.approx(12.0, abs=1e-6)
    g = drw.section_geometry(SCATOLA, (-1.0, 0.0), (5.0, 2.0))          # per due spigoli della scatola
    assert g is not None and g.isGeosValid() and g.area() > 0


def test_un_modello_aperto_si_riconosce():
    """Il piano attraversa il modello ma il profilo non si chiude: si dice
    perché, invece di contarla come una linea che non incontra niente."""
    aperto = SCATOLA[2:]                                             # senza la faccia di sotto
    assert drw.section_line_geometry(aperto, [(-1.0, 1.0), (5.0, 1.0)]) is None
    assert drw.section_crosses(aperto, [(-1.0, 1.0), (5.0, 1.0)])
    assert not drw.section_crosses(SCATOLA, [(-1.0, 9.0), (5.0, 9.0)])


def test_le_sezioni_sono_nomi_ricavati():
    assert drw.is_derived_name("3D-SEZ-1") and drw.is_derived_name("3D-SEZ-G12")
    assert not drw.is_derived_name("3D-SEZIONE")


def test_una_linea_obliqua_chiude_il_profilo():
    """Il punto su uno spigolo condiviso da due triangoli si calcola due volte,
    con i vertici in ordine opposto: deve venire uguale, o con coordinate
    grandi (Stereo 70) i segmenti non si toccano e il profilo non si chiude."""
    from modules.s3dgraphy import glb_mesh as gm
    from tests.sync.glb_fixtures import box_glb
    tri = drw.scene_from_gltf(gm.read_triangles(box_glb(4.0, 3.0, 1.0, center=(2.0, 1.5, -10.0))))
    tri[..., 0] += 327300.0
    tri[..., 1] += 448370.0
    for a, b in (((327298.0, 448380.0), (327306.0, 448380.0)),
                 ((327297.9999998525, 448379.99999969243), (327305.9999997554, 448380.0000001692)),
                 ((327298.0, 448379.7), (327306.0, 448380.3))):
        g = drw.section_geometry(tri, a, b)
        assert g is not None, (a, b)
        assert g.area() > 11.9


def test_un_proxy_a_doppio_guscio_e_pieno():
    """I proxy di TempluMare hanno un guscio interno rientrato di un centimetro:
    il taglio dà un anello sottile attorno a un'area grande. L'unità è piena,
    non un tubo: si riempie tutto quello che sta dentro il contorno esterno."""
    doppio = np.concatenate([SCATOLA, _cubo(0.01, 0.01, 10.01, 3.98, 1.98, 2.98)])
    g = drw.section_geometry(doppio, (-1.0, 1.0), (5.0, 1.0))
    assert g.area() == pytest.approx(12.0, abs=1e-6)
