"""Il lettore dei GLB dei proxy (spec 2026-10-18-geometrie-dai-proxy-3d, D2)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import glb_mesh as gm  # noqa: E402
from tests.sync.glb_fixtures import box, box_glb, make_glb  # noqa: E402


def test_una_scatola_ha_dodici_triangoli_al_suo_posto():
    tri = gm.read_triangles(box_glb(2.0, 3.0, 4.0, center=(10.0, 20.0, 30.0)))
    assert tri.shape == (12, 3, 3)
    pts = tri.reshape(-1, 3)
    assert np.allclose(pts.min(axis=0), (9.0, 18.5, 28.0))
    assert np.allclose(pts.max(axis=0), (11.0, 21.5, 32.0))


def test_traslazione_rotazione_e_scala_del_nodo():
    s = math.sin(math.pi / 4)                        # 90° attorno a Y
    tri = gm.read_triangles(box_glb(2.0, 1.0, 1.0, translation=[5.0, 0.0, 0.0],
                                    rotation=[0.0, s, 0.0, s], scale=[1.0, 2.0, 1.0]))
    pts = tri.reshape(-1, 3)
    # la scatola lunga 2 in X, ruotata di 90° attorno a Y, è lunga 2 in Z
    assert np.allclose(pts.max(axis=0) - pts.min(axis=0), (1.0, 2.0, 2.0))
    assert np.allclose(pts.mean(axis=0), (5.0, 0.0, 0.0))


def test_il_figlio_eredita_la_trasformazione_del_padre():
    pos, idx = box(1.0, 1.0, 1.0)
    s = math.sin(math.pi / 4)
    dati = make_glb([[{"positions": pos, "indices": idx}]],
                    [{"children": [1], "translation": [100.0, 0.0, 0.0], "rotation": [0.0, s, 0.0, s]},
                     {"mesh": 0, "translation": [10.0, 0.0, 0.0]}], scene_nodes=[0])
    centro = gm.read_triangles(dati).reshape(-1, 3).mean(axis=0)
    # +10 in X ruotato di 90° attorno a Y diventa −10 in Z, poi +100 in X
    assert np.allclose(centro, (100.0, 0.0, -10.0))


def test_la_matrice_del_nodo():
    m = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 7, 8, 9, 1]      # column-major: traslazione 7, 8, 9
    centro = gm.read_triangles(box_glb(matrix=m)).reshape(-1, 3).mean(axis=0)
    assert np.allclose(centro, (7.0, 8.0, 9.0))


def test_strip_e_fan():
    pts = [(0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1), (2, 0, 1)]
    strip = gm.read_triangles(make_glb([[{"positions": pts, "indices": None, "mode": 5}]], [{"mesh": 0}]))
    fan = gm.read_triangles(make_glb([[{"positions": pts, "indices": None, "mode": 6}]], [{"mesh": 0}]))
    assert strip.shape == (3, 3, 3) and fan.shape == (3, 3, 3)


def test_posizioni_con_passo_e_indici_a_otto_bit():
    pos, idx = box()
    tri = gm.read_triangles(make_glb([[{"positions": pos, "indices": idx}]], [{"mesh": 0}],
                                     strided=True, index_type=5121))
    assert tri.shape == (12, 3, 3) and np.allclose(np.abs(tri).max(), 0.5)


@pytest.mark.parametrize("kw, motivo", [
    ({"extensions_required": ["KHR_draco_mesh_compression"]}, "compresso"),
    ({"extensions_used": ["EXT_meshopt_compression"]}, "compresso"),
    ({"sparse": True}, "sparso"),
    ({"uri": "esterno.bin"}, "buffer_esterno"),
])
def test_quello_che_non_si_legge_si_dice(kw, motivo):
    pos, idx = box()
    with pytest.raises(gm.GlbError) as e:
        gm.read_triangles(make_glb([[{"positions": pos, "indices": idx}]], [{"mesh": 0}], **kw))
    assert e.value.reason == motivo
    assert not gm.glb_info(make_glb([[{"positions": pos, "indices": idx}]], [{"mesh": 0}], **kw)).ok


def test_non_e_un_glb():
    for dati in (b"solid ascii stl", b"glTF" + b"\x01\x00\x00\x00" + b"\x00" * 12):
        with pytest.raises(gm.GlbError) as e:
            gm.read_triangles(dati)
        assert e.value.reason == "non_glb"


def test_troppi_triangoli_o_file_troppo_grande():
    with pytest.raises(gm.GlbError) as e:
        gm.read_triangles(box_glb(), max_triangles=5)
    assert e.value.reason == "troppo_grande"
    with pytest.raises(gm.GlbError) as e:
        gm.read_triangles(box_glb(), max_file=100)
    assert e.value.reason == "troppo_grande"


def test_solo_punti_e_vuoto():
    with pytest.raises(gm.GlbError) as e:
        gm.read_triangles(make_glb([[{"positions": [(0, 0, 0), (1, 1, 1)], "indices": None, "mode": 0}]],
                                   [{"mesh": 0}]))
    assert e.value.reason == "vuoto"


def test_info_senza_leggere_il_binario(tmp_path):
    f = tmp_path / "SU001.glb"
    f.write_bytes(box_glb(1.0, 2.0, 1.0, translation=[0.0, 495.0, 0.0]))
    info = gm.glb_info(str(f))
    assert info.ok and info.triangles == 12
    assert info.ymin == pytest.approx(494.0) and info.ymax == pytest.approx(496.0)
    assert gm.glb_info(str(f), max_triangles=3).reason == "troppo_grande"
