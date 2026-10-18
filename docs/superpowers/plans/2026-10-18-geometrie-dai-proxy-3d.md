# Piante e prospetti dai proxy 3D — piano di lavoro

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** all'import dell'em.json, un'opzione ricava dai proxy 3D le piante delle unità (`pyunitastratigrafiche`), i prospetti del sito e delle unità (`pyunitastratigrafiche_usm`) e i loro documenti, collegati a poligoni e scheda US con lo stesso tipo e nome.

**Architecture:** quattro moduli nuovi. `glb_mesh` (numpy) legge i triangoli di un GLB. `em_drawings` (numpy + `QgsGeometry`, QGIS importato solo dentro le funzioni) fa sistemi, proiezioni, viste, impaginazione, nomi e coppie della scheda. `sync/em_drawings_import` (SQLAlchemy) sceglie le unità, applica la regola dell'SRID e scrive. `em_drawings_dialog` (Qt) è la finestra. La scheda Import di `s3dgraphy_dot_bridge` li collega. `graph_projector` lascia fuori dall'em.json le coppie ricavate, e `graph_ingestor` le conserva al reimport.

**Tech Stack:** Python 3.12 di QGIS 3.42, numpy, `qgis.core` (QgsGeometry, QgsCoordinateTransform), SQLAlchemy 2, SpatiaLite / PostGIS, s3dgraphy dev57 (`api.georeference_scene`, `api.georeference_state`, `api._geo_anchor`), pytest.

**Spec:** `docs/superpowers/specs/2026-10-18-geometrie-dai-proxy-3d-design.md`

## Global Constraints

- Ramo `Stratigraph_00001`; plugin da 5.13.133-alpha a **5.13.134-alpha**.
- Niente dipendenze nuove: **niente shapely**, niente trimesh né pygltflib. Solo numpy e `qgis.core`.
- Limiti: `MAX_TRIANGLES = 200_000`, `MAX_FILE = 100 MB`, semplificazione 1 cm, parti e buchi sotto 1 cm² via, triangoli sotto 1 mm² via, `GAP = 10 m`, rapporto lato lungo/corto 1,5.
- Segno di provenienza: `disegnatore = 'pyArchInit 3D'` e `nome_doc` che comincia con `3D-`. Coppie della scheda ricavate se il nome rispetta `^3D-(PLA|PRO-.+)$`.
- Nomi: `3D-PLA`; `3D-PRO-N`, `3D-PRO-E`, `3D-PRO-S`, `3D-PRO-W`; `3D-PRO-<unita_tipo><us>`, con `-A<area>` solo per i nomi doppi.
- Tipi dei documenti dal thesaurus `documentazione_table` 9.1 (`PLA`, `PRO`) nella lingua del plugin, poi IT, poi «Planimetria» / «Prospetto».
- `tipo_doc` e `nome_doc` dei poligoni sono **identici** a `tipo_documentazione` e `nome_doc` del documento, nello stesso sito.
- `coord` = centroide `POINT(x y)`, come il trigger `update_coord_on_geom`.
- Regola dell'SRID: prima di scrivere qualsiasi cosa. Piante: stesso EPSG si scrive; altro metrico, Converti/Annulla; in gradi, `-1` o assente, si ferma. Prospetti: basta un layer metrico. Senza geometrie da scrivere, nessun controllo.
- L'em.json non cambia: nessuna geometria e nessuna coppia ricavata nell'export.
- Su PostgreSQL non si toccano i database veri del server locale: i test usano solo `pyarchinit_test_pg`, in uno schema temporaneo.
- I commit non hanno righe di attribuzione AI (`~/.claude/CLAUDE.md`); prima del commit si cercano segreti nelle modifiche.
- Comando di test (dalla radice del plugin), d'ora in poi **PYT**:
  `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python QGIS_PREFIX_PATH=/Applications/QGIS.app/Contents/MacOS /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest -q -p no:warnings -p no:cacheprovider`
- Suite intera: `PYT tests/sync tests/utility tests/migrations --continue-on-collection-errors --ignore=tests/sync/test_groups_dialog_smoke.py --ignore=tests/sync/test_paradata_dialog_smoke.py`, poi `git checkout -- modules/geoarchaeo/test_layers/villa_ceramica.gpkg`. Base: 2439 passati, 2 saltati, 1 xfail.

## Review Focus

1. **Trasformazione del nodo padre.** Un GLB con un nodo radice ruotato o scalato, con il proxy fra i figli (export di Blender con radice): ci si aspetta la pianta nel posto giusto. Test in Task 1: `test_il_figlio_eredita_la_trasformazione_del_padre`.
2. **Proxy fatto solo di facce verticali** (un muro come piano senza spessore): la pianta viene vuota. Ci si aspetta che l'unità venga saltata con «vuoto in pianta», ma che abbia comunque il prospetto. Test in Task 6: `test_un_muro_senza_spessore_ha_il_prospetto_ma_non_la_pianta`.
3. **Poligono ricavato corretto a mano** (disegnatore cambiato) e poi reimport: ci si aspetta che il poligono resti e che il suo documento non venga tolto. Test in Task 7: `test_il_poligono_corretto_a_mano_resta_col_suo_documento`.
4. **DB senza il layer USM registrato** in `geometry_columns` (DB vecchio), con le sole piante scelte: ci si aspetta che le piante si scrivano, e che si fermi solo chi vuole i prospetti. Test in Task 5: `test_senza_layer_usm_le_sole_piante_passano`.
5. **Nomi di US con spazi o barre** («US 2/a»): ci si aspetta un nome di documento senza spazi che si possa usare come filtro. Test in Task 4: `test_i_nomi_dei_documenti_non_hanno_spazi_ne_barre`.

---

### Task 1: `glb_mesh` — i triangoli di un GLB

**Files:**
- Create: `modules/s3dgraphy/glb_mesh.py`
- Create: `tests/sync/glb_fixtures.py` (GLB sintetici per i test, usati anche dai Task 3, 6 e 7)
- Test: `tests/utility/test_glb_mesh.py`

**Interfaces:**
- Produces: `read_triangles(source, *, max_triangles=MAX_TRIANGLES, max_file=MAX_FILE) -> np.ndarray` di forma `(n, 3, 3)` float64, nel sistema glTF; `glb_info(source, ...) -> GlbInfo(ok, triangles, reason, detail, ymin, ymax)`; `GlbError(reason, detail)` con `.reason` fra le chiavi di `REASONS`; `REASONS: Dict[str, str]`; `MAX_TRIANGLES`, `MAX_FILE`.
- Produces (test): `tests.sync.glb_fixtures.box(sx, sy, sz, center) -> (positions, indices)`, `make_glb(meshes, nodes, scene_nodes=None, *, extensions_used=(), extensions_required=(), sparse=False, uri=None, strided=False, index_type=5125) -> bytes`, `box_glb(sx=1, sy=1, sz=1, center=(0,0,0), **node) -> bytes`, `quad_glb(points4) -> bytes`.

- [ ] **Step 1: Scrivere i GLB sintetici dei test**

```python
# tests/sync/glb_fixtures.py
"""GLB piccoli scritti a mano per i test: scatole, quadrilateri, nodi con
trasformazioni, estensioni e accessori che il lettore deve rifiutare."""
import json
import struct

import numpy as np

_JSON, _BIN = 0x4E4F534A, 0x004E4942


def box(sx=1.0, sy=1.0, sz=1.0, center=(0.0, 0.0, 0.0)):
    """Le 8 posizioni e i 36 indici (12 triangoli) di una scatola, in glTF."""
    cx, cy, cz = center
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    pos = [(cx + ix * hx, cy + iy * hy, cz + iz * hz)
           for ix in (-1, 1) for iy in (-1, 1) for iz in (-1, 1)]
    facce = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5),
             (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6),
             (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return pos, [i for f in facce for i in f]


def make_glb(meshes, nodes, scene_nodes=None, *, extensions_used=(),
             extensions_required=(), sparse=False, uri=None, strided=False,
             index_type=5125):
    """``meshes`` = [[{"positions": [...], "indices": [...] o None, "mode": 4}, ...], ...];
    ``nodes`` = [{"mesh": 0, "translation": [...], "children": [...]}, ...]."""
    binario = bytearray()
    viste, accessori, gl_meshes = [], [], []

    def vista(dati, passo=None):
        while len(binario) % 4:
            binario.append(0)
        v = {"buffer": 0, "byteOffset": len(binario), "byteLength": len(dati)}
        if passo:
            v["byteStride"] = passo
        viste.append(v)
        binario.extend(dati)
        return len(viste) - 1

    for mesh in meshes:
        primitive = []
        for prim in mesh:
            pos = np.asarray(prim["positions"], dtype="<f4").reshape(-1, 3)
            if strided:
                largo = np.zeros((len(pos), 4), dtype="<f4")
                largo[:, :3] = pos
                v = vista(largo.tobytes(), passo=16)
            else:
                v = vista(pos.tobytes())
            accessori.append({"bufferView": v, "componentType": 5126, "count": len(pos),
                              "type": "VEC3",
                              "min": pos.min(axis=0).tolist() if len(pos) else [0, 0, 0],
                              "max": pos.max(axis=0).tolist() if len(pos) else [0, 0, 0]})
            p = {"attributes": {"POSITION": len(accessori) - 1}, "mode": prim.get("mode", 4)}
            if prim.get("indices") is not None:
                tipo = {5121: "<u1", 5123: "<u2", 5125: "<u4"}[index_type]
                idx = np.asarray(prim["indices"], dtype=tipo)
                accessori.append({"bufferView": vista(idx.tobytes()), "componentType": index_type,
                                  "count": len(idx), "type": "SCALAR"})
                p["indices"] = len(accessori) - 1
            primitive.append(p)
        gl_meshes.append({"primitives": primitive})
    if sparse and accessori:
        accessori[0]["sparse"] = {"count": 1}
    while len(binario) % 4:
        binario.append(0)
    buf = {"byteLength": len(binario)}
    if uri:
        buf["uri"] = uri
    doc = {"asset": {"version": "2.0"}, "scene": 0,
           "scenes": [{"nodes": list(range(len(nodes))) if scene_nodes is None else list(scene_nodes)}],
           "nodes": nodes, "meshes": gl_meshes, "accessors": accessori,
           "bufferViews": viste, "buffers": [buf]}
    if extensions_used:
        doc["extensionsUsed"] = list(extensions_used)
    if extensions_required:
        doc["extensionsRequired"] = list(extensions_required)
    js = json.dumps(doc).encode("utf-8")
    js += b" " * (-len(js) % 4)
    corpo = struct.pack("<II", len(js), _JSON) + js
    corpo += struct.pack("<II", len(binario), _BIN) + bytes(binario)
    return b"glTF" + struct.pack("<II", 2, 12 + len(corpo)) + corpo


def box_glb(sx=1.0, sy=1.0, sz=1.0, center=(0.0, 0.0, 0.0), **node):
    pos, idx = box(sx, sy, sz, center)
    return make_glb([[{"positions": pos, "indices": idx}]], [dict(mesh=0, **node)])


def quad_glb(points4):
    """Un quadrilatero (due triangoli) con i quattro vertici dati, in glTF."""
    return make_glb([[{"positions": list(points4), "indices": [0, 1, 2, 0, 2, 3]}]], [{"mesh": 0}])
```

- [ ] **Step 2: Scrivere i test che falliscono**

```python
# tests/utility/test_glb_mesh.py
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
```

- [ ] **Step 3: Lanciare i test e vederli fallire**

Run: `PYT tests/utility/test_glb_mesh.py`
Expected: FAIL in raccolta con `ModuleNotFoundError: No module named 'modules.s3dgraphy.glb_mesh'`.

- [ ] **Step 4: Scrivere `glb_mesh.py`**

```python
# modules/s3dgraphy/glb_mesh.py
"""I triangoli di un GLB, letti a mano con numpy, per ricavare piante e
prospetti dai proxy 3D (spec 2026-10-18-geometrie-dai-proxy-3d-design, D2).

Un GLB 2.0 è un'intestazione di 12 byte, un chunk JSON e un chunk BIN. Si
percorrono i nodi della scena componendo le loro trasformazioni e si leggono
le primitive a triangoli (TRIANGLES, STRIP, FAN): il risultato è un array
``(n, 3, 3)`` nel sistema della scena glTF (Y in alto, metri). Quello che
cambierebbe il modo di leggere le posizioni (Draco, meshopt, quantizzazione,
accessori sparsi, buffer esterni) è un ``GlbError`` con un motivo di una
parola, per il riepilogo dell'import.
"""
from __future__ import annotations

import json
import os
import struct
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import numpy as np

MAX_TRIANGLES = 200_000
MAX_FILE = 100 * 1024 * 1024

#: Le estensioni che cambiano il modo di leggere le posizioni.
GEOMETRY_EXTENSIONS = frozenset({
    "KHR_draco_mesh_compression", "EXT_meshopt_compression", "KHR_mesh_quantization"})

#: Le parole del riepilogo, una per motivo.
REASONS = {
    "non_glb": "non è un GLB",
    "compresso": "formato non supportato (compresso)",
    "sparso": "formato non supportato (accessori sparsi)",
    "buffer_esterno": "formato non supportato (buffer esterni)",
    "formato": "formato non supportato",
    "troppo_grande": "troppo grande",
    "vuoto": "modello vuoto",
    "rotto": "file rotto",
}

_JSON, _BIN = 0x4E4F534A, 0x004E4942
_DTYPE = {5121: "<u1", 5123: "<u2", 5125: "<u4", 5126: "<f4"}
_SIZE = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

Source = Union[str, bytes, bytearray, "os.PathLike[str]"]


class GlbError(Exception):
    """Un GLB che non si legge: ``reason`` è una chiave di ``REASONS``."""

    def __init__(self, reason: str, detail: str = ""):
        testo = REASONS.get(reason, reason)
        super().__init__("%s: %s" % (testo, detail) if detail else testo)
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class GlbInfo:
    """Quello che la finestra deve sapere di un proxy senza calcolare niente."""
    ok: bool
    triangles: int = 0
    reason: str = ""
    detail: str = ""
    ymin: Optional[float] = None          # quota glTF (Y in alto) più bassa
    ymax: Optional[float] = None


def _load(source: Source, max_file: int) -> bytes:
    if isinstance(source, (bytes, bytearray, memoryview)):
        data = bytes(source)
        if len(data) > max_file:
            raise GlbError("troppo_grande", "%d byte" % len(data))
        return data
    if os.path.getsize(source) > max_file:
        raise GlbError("troppo_grande", "più di %d MB" % (max_file // (1024 * 1024)))
    with open(source, "rb") as fh:
        return fh.read()


def _header(data: bytes) -> int:
    if len(data) < 12 or data[:4] != b"glTF":
        raise GlbError("non_glb")
    version, length = struct.unpack_from("<II", data, 4)
    if version != 2:
        raise GlbError("non_glb", "versione %d" % version)
    return length


def _parse(data: bytes) -> Tuple[dict, bytes]:
    length = min(_header(data), len(data))
    offset, doc, binary = 12, None, b""
    while offset + 8 <= length:
        clen, ctype = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8: offset + 8 + clen]
        if ctype == _JSON and doc is None:
            try:
                doc = json.loads(bytes(chunk).decode("utf-8"))
            except (UnicodeDecodeError, ValueError) as e:
                raise GlbError("rotto", "JSON: %s" % e)
        elif ctype == _BIN and not binary:
            binary = bytes(chunk)
        offset += 8 + clen
    if not isinstance(doc, dict):
        raise GlbError("rotto", "manca il JSON")
    return doc, binary


def _check(doc: dict) -> None:
    usate = set(doc.get("extensionsRequired") or []) | set(doc.get("extensionsUsed") or [])
    compresse = sorted(usate & GEOMETRY_EXTENSIONS)
    if compresse:
        raise GlbError("compresso", ", ".join(compresse))
    for b in doc.get("buffers") or []:
        if isinstance(b, dict) and b.get("uri"):
            raise GlbError("buffer_esterno", str(b.get("uri"))[:60])
    for a in doc.get("accessors") or []:
        if isinstance(a, dict) and a.get("sparse"):
            raise GlbError("sparso")


def _accessor(doc: dict, binary: bytes, index) -> np.ndarray:
    try:
        a = doc["accessors"][int(index)]
        view = doc["bufferViews"][int(a["bufferView"])]
        dtype = np.dtype(_DTYPE[int(a["componentType"])])
        comps = _SIZE[a["type"]]
        count = int(a["count"])
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise GlbError("rotto", "accessore %s: %s" % (index, e))
    if int(view.get("buffer", 0)) != 0:
        raise GlbError("buffer_esterno", "buffer %s" % view.get("buffer"))
    if count == 0:
        return np.zeros((0, comps), dtype=dtype)
    start = int(view.get("byteOffset", 0)) + int(a.get("byteOffset", 0))
    item = dtype.itemsize * comps
    stride = int(view.get("byteStride") or item)
    end = start + stride * (count - 1) + item
    if start < 0 or end > len(binary):
        raise GlbError("rotto", "accessore %s oltre il buffer" % index)
    return np.ndarray(shape=(count, comps), dtype=dtype, buffer=binary,
                      offset=start, strides=(stride, dtype.itemsize))


def _matrix(node: dict) -> np.ndarray:
    if "matrix" in node:
        return np.asarray(node["matrix"], dtype=float).reshape(4, 4).T
    tx, ty, tz = node.get("translation") or (0.0, 0.0, 0.0)
    x, y, z, w = node.get("rotation") or (0.0, 0.0, 0.0, 1.0)
    n = (x * x + y * y + z * z + w * w) ** 0.5 or 1.0
    x, y, z, w = x / n, y / n, z / n, w / n
    sx, sy, sz = node.get("scale") or (1.0, 1.0, 1.0)
    r = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    m = np.eye(4)
    m[:3, :3] = r * np.array([sx, sy, sz], dtype=float)[None, :]
    m[:3, 3] = (tx, ty, tz)
    return m


def _faces(idx: np.ndarray, mode: int) -> np.ndarray:
    if mode == 4:
        n = len(idx) // 3
        return idx[: n * 3].reshape(n, 3)
    if len(idx) < 3:
        return np.zeros((0, 3), dtype=np.int64)
    if mode == 5:                                            # TRIANGLE_STRIP
        a, b, c = idx[:-2], idx[1:-1], idx[2:]
        dispari = (np.arange(len(a)) % 2) == 1
        return np.stack([a, np.where(dispari, c, b), np.where(dispari, b, c)], axis=1)
    return np.stack([np.full(len(idx) - 2, idx[0]), idx[1:-1], idx[2:]], axis=1)   # FAN


def _primitive(doc: dict, binary: bytes, prim: dict) -> np.ndarray:
    mode = int(prim.get("mode", 4))
    pos_index = (prim.get("attributes") or {}).get("POSITION")
    if mode not in (4, 5, 6) or pos_index is None:
        return np.zeros((0, 3, 3))
    acc = doc["accessors"][int(pos_index)]
    if acc.get("componentType") != 5126 or acc.get("type") != "VEC3":
        raise GlbError("formato", "POSITION non è float32 VEC3")
    pos = _accessor(doc, binary, pos_index).astype(np.float64)
    if "indices" in prim:
        idx = _accessor(doc, binary, prim["indices"]).reshape(-1).astype(np.int64)
    else:
        idx = np.arange(len(pos), dtype=np.int64)
    if idx.size and (idx.min() < 0 or idx.max() >= len(pos)):
        raise GlbError("rotto", "indici fuori dalle posizioni")
    faces = _faces(idx, mode)
    return pos[faces] if len(faces) else np.zeros((0, 3, 3))


def _roots(doc: dict) -> List[int]:
    scenes = doc.get("scenes") or []
    nodes = doc.get("nodes") or []
    if scenes:
        si = int(doc.get("scene", 0) or 0)
        scena = scenes[si] if 0 <= si < len(scenes) else scenes[0]
        return [int(i) for i in scena.get("nodes") or []]
    figli = {int(c) for n in nodes for c in n.get("children") or []}
    return [i for i in range(len(nodes)) if i not in figli]


def _walk(doc: dict):
    """I nodi della scena con la loro matrice, ``(nodo, matrice)``."""
    nodes = doc.get("nodes") or []
    pila = [(i, np.eye(4)) for i in _roots(doc)]
    passi = 0
    while pila:
        passi += 1
        if passi > 4 * max(len(nodes), 1):
            raise GlbError("rotto", "nodi in ciclo")
        i, genitore = pila.pop()
        if not 0 <= i < len(nodes):
            raise GlbError("rotto", "nodo %s inesistente" % i)
        nodo = nodes[i]
        m = genitore @ _matrix(nodo)
        yield nodo, m
        for c in nodo.get("children") or []:
            pila.append((int(c), m))


def _primitives_of(doc: dict, nodo: dict) -> list:
    if "mesh" not in nodo:
        return []
    try:
        return doc["meshes"][int(nodo["mesh"])].get("primitives") or []
    except (KeyError, IndexError, TypeError, ValueError):
        raise GlbError("rotto", "mesh %s inesistente" % nodo.get("mesh"))


def read_triangles(source: Source, *, max_triangles: int = MAX_TRIANGLES,
                   max_file: int = MAX_FILE) -> np.ndarray:
    """Tutti i triangoli della scena del GLB, ``(n, 3, 3)`` float64, nel
    sistema della scena glTF (Y in alto). ``GlbError`` se non si legge."""
    doc, binary = _parse(_load(source, max_file))
    _check(doc)
    parti, totale = [], 0
    for nodo, m in _walk(doc):
        for prim in _primitives_of(doc, nodo):
            tri = _primitive(doc, binary, prim)
            if not len(tri):
                continue
            totale += len(tri)
            if totale > max_triangles:
                raise GlbError("troppo_grande", "più di %d triangoli" % max_triangles)
            piatti = tri.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
            parti.append(piatti.reshape(-1, 3, 3))
    if not parti:
        raise GlbError("vuoto")
    return np.concatenate(parti)


def _summary(doc: dict) -> Tuple[int, Optional[float], Optional[float]]:
    """Triangoli e quote glTF dagli accessori (count, min, max), senza il binario."""
    accessori = doc.get("accessors") or []
    totale, quote = 0, []
    for nodo, m in _walk(doc):
        for prim in _primitives_of(doc, nodo):
            mode = int(prim.get("mode", 4))
            pos_index = (prim.get("attributes") or {}).get("POSITION")
            if mode not in (4, 5, 6) or pos_index is None:
                continue
            ref = prim.get("indices", pos_index)
            n = int(accessori[int(ref)].get("count", 0))
            totale += n // 3 if mode == 4 else max(n - 2, 0)
            acc = accessori[int(pos_index)]
            lo, hi = acc.get("min"), acc.get("max")
            if lo and hi and len(lo) == 3 and len(hi) == 3:
                angoli = np.array([(x, y, z) for x in (lo[0], hi[0])
                                   for y in (lo[1], hi[1]) for z in (lo[2], hi[2])], dtype=float)
                quote.append((angoli @ m[:3, :3].T + m[:3, 3])[:, 1])
    if not quote:
        return totale, None, None
    tutte = np.concatenate(quote)
    return totale, float(tutte.min()), float(tutte.max())


def glb_info(source: Source, *, max_triangles: int = MAX_TRIANGLES,
             max_file: int = MAX_FILE) -> GlbInfo:
    """Si legge solo il JSON: se il modello si potrà usare, quanti triangoli
    ha e a che quote sta (per la finestra, che non deve calcolare niente)."""
    try:
        if isinstance(source, (bytes, bytearray, memoryview)):
            data = bytes(source)
            if len(data) > max_file:
                raise GlbError("troppo_grande", "%d byte" % len(data))
        else:
            if os.path.getsize(source) > max_file:
                raise GlbError("troppo_grande", "più di %d MB" % (max_file // (1024 * 1024)))
            with open(source, "rb") as fh:
                testa = fh.read(20)
                _header(testa)
                clen, _ctype = struct.unpack_from("<II", testa, 12)
                data = testa + fh.read(clen)
        doc, _ = _parse(data)
        _check(doc)
        n, ymin, ymax = _summary(doc)
        if n == 0:
            raise GlbError("vuoto")
        if n > max_triangles:
            raise GlbError("troppo_grande", "%d triangoli" % n)
        return GlbInfo(True, n, ymin=ymin, ymax=ymax)
    except GlbError as e:
        return GlbInfo(False, 0, e.reason, e.detail)
    except (OSError, struct.error, KeyError, IndexError, TypeError, ValueError) as e:
        return GlbInfo(False, 0, "rotto", str(e))
```

- [ ] **Step 5: Lanciare i test e vederli passare**

Run: `PYT tests/utility/test_glb_mesh.py`
Expected: PASS (15 test: 12 funzioni, una parametrizzata su 4 casi).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/glb_mesh.py tests/sync/glb_fixtures.py tests/utility/test_glb_mesh.py
git commit -m "feat(3d): glb_mesh legge i triangoli dei proxy GLB con numpy — nodi, matrici, strip e fan, rifiuta compressi, sparsi e buffer esterni"
```

---

### Task 2: `em_drawings` — sistemi, posizione e pianta

**Files:**
- Create: `modules/s3dgraphy/em_drawings.py`
- Test: `tests/utility/test_em_drawings.py`

**Interfaces:**
- Consumes: niente dai task precedenti (array numpy).
- Produces: `scene_from_gltf(tri) -> ndarray`; `Georef(state, epsg, shift_x, shift_y, shift_z, rotation, metric)` con `.usable`; `georef_of(graph) -> Georef`; `crs_kind(srid) -> 'metric'|'geographic'|'undefined'`; `place(graph, georef, pts (n,3), shift_z) -> ndarray (n,3)`; `plan_geometry(tri_map (n,3,3)) -> Optional[QgsGeometry]` (MultiPolygon); costanti `DRAWER`, `PLAN_NAME`, `SIDES`, `MIN_TRIANGLE_AREA`, `MIN_PART_AREA`, `SIMPLIFY`, `UNION_BLOCK`, `GAP`, `LONG_RATIO`; funzioni interne `_union_2d(tri2d)` e `_clean(geom)`, riusate dal Task 3.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# tests/utility/test_em_drawings.py
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
```

- [ ] **Step 2: Lanciare i test e vederli fallire**

Run: `PYT tests/utility/test_em_drawings.py`
Expected: FAIL in raccolta, `ModuleNotFoundError: No module named 'modules.s3dgraphy.em_drawings'`.

- [ ] **Step 3: Scrivere la prima parte di `em_drawings.py`**

```python
# modules/s3dgraphy/em_drawings.py
"""Piante e prospetti dai proxy 3D (spec 2026-10-18-geometrie-dai-proxy-3d-design).

Da un array di triangoli (``glb_mesh``) alle geometrie dei due layer di
pyArchInit:

* la **pianta** (``pyunitastratigrafiche``): l'ombra vista dall'alto, nel
  sistema dell'em.json, messa sulla mappa con la regola di s3dgraphy
  (rotazione, poi spostamento: ``api.georeference_scene``);
* i **disegni verticali** (``pyunitastratigrafiche_usm``): la sagoma su un
  piano verticale, in coordinate del disegno, cioè X = metri lungo la vista
  e Y = quota.

Le coppie ``[tipo, nome]`` dei disegni ricavati si riconoscono dal nome
(``3D-PLA``, ``3D-PRO-…``): ``without_derived_pairs`` le toglie dall'export
dell'em.json, ``merge_derived_pairs`` le fa sopravvivere al reimport.
QGIS si importa solo dentro le funzioni di geometria.
"""
from __future__ import annotations

import ast
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

#: Il disegnatore dei poligoni e dei documenti ricavati (il segno di provenienza).
DRAWER = "pyArchInit 3D"
PLAN_NAME = "3D-PLA"
SIDES = ("N", "E", "S", "W")

MIN_TRIANGLE_AREA = 1e-6        # m²: le facce viste di taglio
MIN_PART_AREA = 1e-4            # m²: parti e buchi più piccoli si tolgono
SIMPLIFY = 0.01                 # m
UNION_BLOCK = 2000
GAP = 10.0                      # m fra un disegno verticale e l'altro
LONG_RATIO = 1.5                # lato lungo / lato corto perché un'unità abbia un «fronte»


# --------------------------------------------------------------- i sistemi

def scene_from_gltf(tri: np.ndarray) -> np.ndarray:
    """Dalla scena glTF (Y in alto) alla scena EM (Z in alto): X = gx, Y = −gz, Z = gy."""
    tri = np.asarray(tri, dtype=np.float64)
    out = np.empty_like(tri)
    out[..., 0] = tri[..., 0]
    out[..., 1] = -tri[..., 2]
    out[..., 2] = tri[..., 1]
    return out


def crs_kind(srid) -> str:
    """``metric``, ``geographic`` o ``undefined`` (``-1``, ``0``, assente o sconosciuto)."""
    try:
        srid = int(srid)
    except (TypeError, ValueError):
        return "undefined"
    if srid <= 0:
        return "undefined"
    from qgis.core import QgsCoordinateReferenceSystem
    crs = QgsCoordinateReferenceSystem.fromEpsgId(srid)
    if not crs.isValid():
        return "undefined"
    return "geographic" if crs.isGeographic() else "metric"


@dataclass(frozen=True)
class Georef:
    """Dove sta la scena, secondo l'em.json (il ``GeoPositionNode``)."""
    state: str                      # declared | undeclared | legacy_default
    epsg: Optional[int]
    shift_x: float = 0.0
    shift_y: float = 0.0
    shift_z: float = 0.0
    rotation: float = 0.0
    metric: bool = False

    @property
    def usable(self) -> bool:
        """Le piante si possono mettere sulla mappa."""
        return self.state == "declared" and self.epsg is not None and self.metric


def georef_of(graph) -> Georef:
    from s3dgraphy import api
    stato = api.georeference_state(graph)
    a = api._geo_anchor(graph)
    epsg = a.get("epsg")
    return Georef(state=stato, epsg=epsg, shift_x=float(a.get("shift_x") or 0.0),
                  shift_y=float(a.get("shift_y") or 0.0), shift_z=float(a.get("shift_z") or 0.0),
                  rotation=float(a.get("rotation") or 0.0),
                  metric=epsg is not None and crs_kind(epsg) == "metric")


def place(graph, georef: Georef, pts: np.ndarray, shift_z: float) -> np.ndarray:
    """Punti della scena EM ``(n, 3)`` → mappa: XY con la regola di s3dgraphy
    (se la scena è georeferenziata), quota + ``shift_z``."""
    pts = np.asarray(pts, dtype=np.float64)
    out = pts.copy()
    if georef.usable and len(pts):
        from s3dgraphy import api
        info = api.georeference_scene(graph, [(float(x), float(y)) for x, y in pts[:, :2]],
                                      epsg_target=int(georef.epsg))
        out[:, :2] = np.asarray(info["points"], dtype=np.float64)
    out[:, 2] = pts[:, 2] + float(shift_z)
    return out


# ------------------------------------------------------------- i poligoni

def _areas(tri2d: np.ndarray) -> np.ndarray:
    a = tri2d[:, 1] - tri2d[:, 0]
    b = tri2d[:, 2] - tri2d[:, 0]
    return 0.5 * np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])


def _wkt(blocco: list) -> str:
    parti = ["((%r %r,%r %r,%r %r,%r %r))" % (x0, y0, x1, y1, x2, y2, x0, y0)
             for (x0, y0), (x1, y1), (x2, y2) in blocco]
    return "MULTIPOLYGON(" + ",".join(parti) + ")"


def _union_2d(tri2d):
    """L'unione dei triangoli piani ``(n, 3, 2)``, a blocchi; None se non resta niente."""
    from qgis.core import QgsGeometry
    tri2d = np.asarray(tri2d, dtype=np.float64)
    if tri2d.size == 0:
        return None
    tri2d = tri2d[_areas(tri2d) >= MIN_TRIANGLE_AREA]
    if not len(tri2d):
        return None
    blocchi = []
    for s in range(0, len(tri2d), UNION_BLOCK):
        g = QgsGeometry.fromWkt(_wkt(tri2d[s:s + UNION_BLOCK].tolist()))
        blocchi.append(QgsGeometry.unaryUnion([g]))
    return blocchi[0] if len(blocchi) == 1 else QgsGeometry.unaryUnion(blocchi)


def _polygons(g) -> list:
    from qgis.core import QgsWkbTypes
    if g is None or g.isEmpty():
        return []
    parti = []
    for p in g.asGeometryCollection():
        if p.isEmpty() or p.type() != QgsWkbTypes.PolygonGeometry:
            continue
        parti.extend(p.asGeometryCollection() if p.isMultipart() else [p])
    return parti


def _clean(g):
    """Valida, semplificata a 1 cm, senza briciole: un MultiPolygon o None."""
    from qgis.core import QgsGeometry
    if g is None or g.isEmpty():
        return None
    g = g.makeValid().simplify(SIMPLIFY).makeValid()
    parti = []
    for p in _polygons(g):
        if p.area() < MIN_PART_AREA:
            continue
        p = p.removeInteriorRings(MIN_PART_AREA)
        if not p.isEmpty():
            parti.append(p)
    if not parti:
        return None
    out = QgsGeometry.collectGeometry(parti)
    out.convertToMultiType()
    return out


def plan_geometry(tri_map: np.ndarray):
    """La pianta di triangoli già sulla mappa ``(n, 3, 3)``: MultiPolygon o None."""
    tri_map = np.asarray(tri_map, dtype=np.float64)
    return _clean(_union_2d(tri_map[..., :2])) if tri_map.size else None
```

- [ ] **Step 4: Lanciare i test e vederli passare**

Run: `PYT tests/utility/test_em_drawings.py`
Expected: PASS (9 test). Se `api.declare_georeference` vuole parole chiave, adattare `_grafo` e scrivere una Ruling.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/em_drawings.py tests/utility/test_em_drawings.py
git commit -m "feat(3d): em_drawings — dalla scena glTF alla mappa con la regola di s3dgraphy, pianta come unione dei triangoli con buchi, semplificata a 1 cm"
```

---

### Task 3: `em_drawings` — le viste verticali e l'impaginazione

**Files:**
- Modify: `modules/s3dgraphy/em_drawings.py` (in coda)
- Test: `tests/utility/test_em_drawings.py` (in coda)

**Interfaces:**
- Consumes: `_union_2d`, `_clean`, `plan_geometry`, `GAP`, `LONG_RATIO` (Task 2).
- Produces: `View(code, d, side)` con `.r`; `SITE_VIEWS: Dict[str, View]`; `rose8(dx, dy) -> str`; `unit_view(code, plan, unit_c, site_c) -> View`; `view_geometry(tri_map, view, origin) -> Optional[QgsGeometry]`; `depth(tri_map, view) -> float`; `centroid_xy(tri_map) -> (x, y)`; `site_frame(tri_maps) -> ((x0, y0), (cx, cy))`; `lay_out(spans, gap=GAP) -> List[float]`; `span_u(geom) -> (umin, umax)`; `translated(geom, du) -> QgsGeometry`.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# in coda a tests/utility/test_em_drawings.py

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
```

- [ ] **Step 2: Lanciare i test e vederli fallire**

Run: `PYT tests/utility/test_em_drawings.py`
Expected: FAIL con `AttributeError: module 'modules.s3dgraphy.em_drawings' has no attribute 'SITE_VIEWS'` (e simili).

- [ ] **Step 3: Scrivere le viste**

```python
# in coda a modules/s3dgraphy/em_drawings.py

# ---------------------------------------------------------- le viste verticali

@dataclass(frozen=True)
class View:
    """Un piano verticale da cui si guarda. ``d`` va da chi guarda verso la
    scena (orizzontale, unitario); ``r`` è l'asse destro del disegno;
    ``side`` è da dove si guarda, con gli otto punti della rosa."""
    code: str
    d: Tuple[float, float]
    side: str

    @property
    def r(self) -> Tuple[float, float]:
        return (self.d[1], -self.d[0])


#: Chi guarda sta dal lato che dà il nome alla vista (spec D5).
SITE_VIEWS: Dict[str, View] = {
    "N": View("N", (0.0, -1.0), "N"),
    "E": View("E", (-1.0, 0.0), "E"),
    "S": View("S", (0.0, 1.0), "S"),
    "W": View("W", (1.0, 0.0), "W"),
}

_ROSA = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def rose8(dx: float, dy: float) -> str:
    """La direzione ``(dx, dy)`` con gli otto punti della rosa (0 = nord, in senso orario)."""
    angolo = (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0
    return _ROSA[int((angolo + 22.5) // 45) % 8]


def centroid_xy(tri_map: np.ndarray) -> Tuple[float, float]:
    c = np.asarray(tri_map, dtype=np.float64).reshape(-1, 3).mean(axis=0)
    return float(c[0]), float(c[1])


def site_frame(tri_maps: Iterable[np.ndarray]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """L'angolo minimo e il centro dell'ingombro in pianta di tutte le unità."""
    pts = np.concatenate([np.asarray(t, dtype=np.float64).reshape(-1, 3) for t in tri_maps])
    lo, hi = pts[:, :2].min(axis=0), pts[:, :2].max(axis=0)
    return (float(lo[0]), float(lo[1])), (float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2))


def unit_view(code: str, plan, unit_c: Tuple[float, float], site_c: Tuple[float, float]) -> View:
    """Il prospetto di un'unità: perpendicolare al suo lato lungo, guardato dal
    lato del centro dello scavo; un'unità quasi quadrata si guarda dal centro."""
    vx, vy = unit_c[0] - site_c[0], unit_c[1] - site_c[1]
    d = None
    if plan is not None and not plan.isEmpty():
        anello = plan.orientedMinimumBoundingBox()[0].asPolygon()[0]
        e1 = (anello[1].x() - anello[0].x(), anello[1].y() - anello[0].y())
        e2 = (anello[2].x() - anello[1].x(), anello[2].y() - anello[1].y())
        l1, l2 = math.hypot(*e1), math.hypot(*e2)
        (lx, ly), lungo, corto = (e1, l1, l2) if l1 >= l2 else (e2, l2, l1)
        if lungo > 0 and (corto == 0 or lungo / corto >= LONG_RATIO):
            nx, ny = -ly / lungo, lx / lungo
            prodotto = nx * vx + ny * vy
            if prodotto < -1e-9 or (abs(prodotto) <= 1e-9 and ny < 0):
                nx, ny = -nx, -ny
            d = (nx + 0.0, ny + 0.0)
    if d is None:
        n = math.hypot(vx, vy)
        d = (vx / n, vy / n) if n > 1e-9 else (0.0, 1.0)
    return View(code, d, rose8(-d[0], -d[1]))


def view_geometry(tri_map: np.ndarray, view: View, origin: Tuple[float, float]):
    """La sagoma sul piano della vista, in coordinate del disegno:
    u = (P − O)·r, v = quota. MultiPolygon o None."""
    t = np.asarray(tri_map, dtype=np.float64)
    if not t.size:
        return None
    rx, ry = view.r
    u = (t[..., 0] - origin[0]) * rx + (t[..., 1] - origin[1]) * ry
    return _clean(_union_2d(np.stack([u, t[..., 2]], axis=-1)))


def depth(tri_map: np.ndarray, view: View) -> float:
    """Quanto è lontano da chi guarda: più grande, più lontano."""
    x, y = centroid_xy(tri_map)
    return x * view.d[0] + y * view.d[1]


def lay_out(spans: Sequence[Tuple[float, float]], gap: float = GAP) -> List[float]:
    """Lo spostamento in u di ogni disegno, ``spans`` = ``(u_min, u_max)``
    nell'ordine: uno accanto all'altro, separati da ``gap``."""
    spostamenti, cursore = [], 0.0
    for umin, umax in spans:
        spostamenti.append(cursore - umin)
        cursore += (umax - umin) + gap
    return spostamenti


def span_u(geom) -> Tuple[float, float]:
    bb = geom.boundingBox()
    return bb.xMinimum(), bb.xMaximum()


def translated(geom, du: float):
    from qgis.core import QgsGeometry
    out = QgsGeometry(geom)
    out.translate(float(du), 0.0)
    return out
```

- [ ] **Step 4: Lanciare i test e vederli passare**

Run: `PYT tests/utility/test_em_drawings.py`
Expected: PASS (18 test).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/em_drawings.py tests/utility/test_em_drawings.py
git commit -m "feat(3d): em_drawings — prospetti dai quattro lati e di ogni unità (lato lungo, dal centro dello scavo), profondità, impaginazione a 10 m"
```

---

### Task 4: i nomi dei documenti, le coppie della scheda e l'em.json che non cambia

**Files:**
- Modify: `modules/s3dgraphy/em_drawings.py` (in coda)
- Modify: `modules/s3dgraphy/sync/graph_projector.py` (nel ciclo delle righe di `us_table`, subito dopo l'unpacking, ~riga 997)
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py` (`_completa`, prima di `return existing, eff_uuid`, ~riga 857)
- Test: `tests/utility/test_em_drawings.py` (in coda), `tests/sync/test_em_drawings_pairs.py` (nuovo)

**Interfaces:**
- Produces: `side_name(code) -> str`; `is_derived_name(nome) -> bool`; `unit_drawing_names(items: Sequence[Tuple[key, unita_tipo, us, area]]) -> Dict[key, str]`; `without_derived_pairs(value) -> value`; `with_derived_pairs(value, pairs) -> Optional[str]`; `merge_derived_pairs(new_value, old_value) -> value`.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# in coda a tests/utility/test_em_drawings.py

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
```

```python
# tests/sync/test_em_drawings_pairs.py
"""Le coppie dei disegni ricavati dal 3D non vanno nell'em.json e non si
perdono reimportandolo (spec 2026-10-18, D11)."""
from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

FIXTURE_DB = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "mini_volterra.sqlite"
CON_3D = "[['Fotografie', 'Si'], ['Prospetto', '3D-PRO-N']]"


@pytest.fixture
def db(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import add_columns, backfill_uuids
    add_columns(dst)
    backfill_uuids(dst)
    con = sqlite3.connect(dst)
    sito, id_us = con.execute("SELECT sito, id_us FROM us_table WHERE unita_tipo = 'US' LIMIT 1").fetchone()
    con.execute("UPDATE us_table SET documentazione = ? WHERE id_us = ?", (CON_3D, id_us))
    con.commit()
    con.close()
    return dst, sito, id_us


def test_export_senza_coppie_ricavate_e_reimport_che_le_tiene(db):
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    path, sito, id_us = db
    con = sqlite3.connect(path)
    uuid = con.execute("SELECT node_uuid FROM us_table WHERE id_us = ?", (id_us,)).fetchone()[0]
    con.close()
    grafo = GraphProjector().populate_graph(path, sito=sito)
    nodo = grafo.find_node_by_id(uuid)
    esportato = str((getattr(nodo, "attributes", None) or {}).get("documentazione"))
    assert "3D-PRO-N" not in esportato and "Fotografie" in esportato
    GraphIngestor().populate_list(grafo, path, sito=sito, dry_run=False, create_missing_epochs=True)
    con = sqlite3.connect(path)
    dopo = con.execute("SELECT documentazione FROM us_table WHERE id_us = ?", (id_us,)).fetchone()[0]
    con.close()
    assert "3D-PRO-N" in dopo and "Fotografie" in dopo
```

- [ ] **Step 2: Lanciare i test e vederli fallire**

Run: `PYT tests/utility/test_em_drawings.py tests/sync/test_em_drawings_pairs.py`
Expected: FAIL. I test di `em_drawings` danno `AttributeError` (`side_name`, `unit_drawing_names`…). Il test dell'em.json fallisce sull'asserzione `"3D-PRO-N" not in esportato`.

- [ ] **Step 3: Scrivere i nomi e le coppie**

```python
# in coda a modules/s3dgraphy/em_drawings.py

# ------------------------------------------------- i nomi e le coppie della scheda

_DERIVED = re.compile(r"^3D-(PLA|PRO-.+)$")
_UNSAFE = re.compile(r"[^0-9A-Za-z._-]+")


def side_name(code: str) -> str:
    return "3D-PRO-" + str(code)


def is_derived_name(nome) -> bool:
    return bool(_DERIVED.match(str(nome or "").strip()))


def _safe(testo) -> str:
    return _UNSAFE.sub("_", str(testo or "").strip().replace("/", "-")).strip("_")


def unit_drawing_names(items: Sequence[Tuple[str, str, str, str]]) -> Dict[str, str]:
    """``(chiave, unita_tipo, us, area)`` → «3D-PRO-<tipo><us>»; ai nomi che
    verrebbero doppi si aggiunge «-A<area>»."""
    base = {k: "3D-PRO-%s%s" % (_safe(t), _safe(u)) for k, t, u, _a in items}
    quanti = Counter(base.values())
    return {k: base[k] + ("-A%s" % _safe(a) if quanti[base[k]] > 1 else "")
            for k, _t, _u, a in items}


def _pairs(value):
    """La lista della scheda US (la ``repr`` di una lista di coppie) → lista;
    ``None`` se non si legge."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [list(p) if isinstance(p, (list, tuple)) else p for p in value]
    testo = str(value).strip()
    if not testo:
        return []
    try:
        dati = ast.literal_eval(testo)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return None
    if not isinstance(dati, (list, tuple)):
        return None
    return [list(p) if isinstance(p, (list, tuple)) else p for p in dati]


def _is_derived_pair(p) -> bool:
    return isinstance(p, list) and len(p) >= 2 and is_derived_name(p[1])


def without_derived_pairs(value):
    """Per l'export dell'em.json: la lista senza le coppie ricavate dal 3D.
    Un valore che non si legge, o senza coppie ricavate, torna com'era."""
    coppie = _pairs(value)
    if not coppie or not any(_is_derived_pair(p) for p in coppie):
        return value
    return str([p for p in coppie if not _is_derived_pair(p)])


def with_derived_pairs(value, pairs) -> Optional[str]:
    """La lista della scheda con le coppie ricavate di adesso al posto di
    quelle di prima; le altre restano. ``None`` se la lista non si legge."""
    coppie = _pairs(value)
    if coppie is None:
        return None
    resto = [p for p in coppie if not _is_derived_pair(p)]
    nuove = []
    for p in pairs:
        p = [str(x) for x in p]
        if p not in resto and p not in nuove:
            nuove.append(p)
    return str(resto + nuove)


def merge_derived_pairs(new_value, old_value):
    """Reimport di un em.json: la lista che arriva, più le coppie ricavate che
    la scheda aveva (nell'em.json non ci sono mai)."""
    vecchie = _pairs(old_value)
    ricavate = [p for p in (vecchie or []) if _is_derived_pair(p)]
    if not ricavate:
        return new_value
    nuove = _pairs(new_value)
    if nuove is None:
        return new_value
    return str([p for p in nuove if not _is_derived_pair(p)] + ricavate)
```

- [ ] **Step 4: Filtro nell'export e fusione nel reimport**

In `modules/s3dgraphy/sync/graph_projector.py`, dentro il ciclo `for (us_val, node_uuid, sito_v, area, ..., documentazione, descrizione) in rows:`, come prima riga del corpo:

```python
            # I disegni ricavati dal 3D (3D-PLA, 3D-PRO-…) restano in
            # pyArchInit: nell'em.json non vanno (spec 2026-10-18, D11).
            documentazione = _without_derived_pairs(documentazione)
```

e fra gli import in cima al modulo:

```python
from ..em_drawings import without_derived_pairs as _without_derived_pairs
```

In `modules/s3dgraphy/sync/graph_ingestor.py`, dentro `_completa`, subito prima di `return existing, eff_uuid`:

```python
                    # Le coppie dei disegni ricavati dal 3D non viaggiano
                    # nell'em.json: reimportandolo, la scheda le tiene.
                    if existing is not None and "documentazione" in attrs:
                        attrs["documentazione"] = _merge_derived_pairs(
                            attrs.get("documentazione"), existing.get("documentazione"))
```

e fra gli import in cima al modulo:

```python
from ..em_drawings import merge_derived_pairs as _merge_derived_pairs
```

- [ ] **Step 5: Lanciare i test e vederli passare**

Run: `PYT tests/utility/test_em_drawings.py tests/sync/test_em_drawings_pairs.py tests/sync/test_graph_projector.py tests/sync/test_graph_ingestor.py`
Expected: PASS, compresi i test già esistenti di projector e ingestor.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/em_drawings.py modules/s3dgraphy/sync/graph_projector.py modules/s3dgraphy/sync/graph_ingestor.py tests/utility/test_em_drawings.py tests/sync/test_em_drawings_pairs.py
git commit -m "feat(3d): nomi dei documenti 3D-PLA/3D-PRO-…, coppie della scheda US — fuori dall'export dell'em.json, conservate al reimport"
```

---

### Task 5: `em_drawings_import` — unità, scelta, regola dell'SRID

**Files:**
- Create: `modules/s3dgraphy/sync/em_drawings_import.py`
- Test: `tests/sync/test_em_drawings_import.py` (con la fixture del progetto, riusata dai Task 6 e 7)

**Interfaces:**
- Consumes: `glb_mesh.glb_info`, `glb_mesh.REASONS`; `em_drawings.georef_of`, `em_drawings.crs_kind`, `em_drawings.is_derived_name`, `em_drawings.DRAWER`, `em_drawings.SIDES`; `em_narrative_3d.scene_proxies(graph)`; `em_media_import.search_dirs_for`, `em_media_import._checksum`, `em_media_import._engine`; `s3dgraphy.resources.locate.resolve`.
- Produces: `PLAN_LAYER`, `VERTICAL_LAYER`; `DrawingUnit(key, name, unit_type, locators, paths, status, detail="", heir_of="", hand_plan=False, hand_vertical=False, triangles=0, ymin=None, ymax=None)` con `.usable`; `Choice(plan: set, prospect: set, sides: tuple, shift_z: Optional[float])` con `.units` (unione); `Scheda(id_us, area, us, unita_tipo, documentazione)`; `CrsDecision(kind, message, plan_srid, usm_srid, source_epsg)`; `plan_units(graph, emjson_path, *, search_dirs=(), db=None, sito=None) -> List[DrawingUnit]`; `schede_of(db, sito, keys) -> Dict[str, Scheda]`; `default_choice(units, georef) -> Choice`; `layer_srid(conn, table, column="the_geom") -> Optional[int]`; `wants(choice, georef) -> (bool plan, bool vertical)`; `crs_decision(db, georef, choice) -> CrsDecision`; `status_text(unit) -> str`; `preview_line(units, choice, georef) -> str`.

- [ ] **Step 1: Scrivere la fixture e i test che falliscono**

```python
# tests/sync/test_em_drawings_import.py
"""Piante e prospetti dai proxy 3D all'import dell'em.json (spec 2026-10-18,
D8–D13): un progetto EM finto con tre unità, i GLB scritti dai test, un DB
copiato dal template con l'SRID dei layer scelto dal test."""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

pytest.importorskip("s3dgraphy")

from tests.sync.glb_fixtures import box_glb, quad_glb  # noqa: E402

TEMPLATE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite"
SITO = "Tempio 3D"
_SPATIALITE = ["/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so",
               "/opt/homebrew/lib/mod_spatialite", "mod_spatialite"]


def _nodo(nid, tipo, nome, **data):
    return {"id": nid, "node_type": tipo, "name": nome, "data": dict(data)}


def _arco(src, tipo, dst):
    return {"id": "%s_%s_%s" % (src, tipo, dst), "edge_type": tipo, "source": src, "target": dst}


def _unita(nid, nome, tipo="US"):
    return [_nodo(nid, tipo, nome), _nodo("p" + nid, "property", "geometry"),
            _nodo("sh" + nid, "semantic_shape", "Shape for " + nome),
            _nodo("r" + nid, "resource", nome + ".glb", url="proxies/%s.glb" % nome)]


def _archi(nid):
    return [_arco(nid, "has_property", "p" + nid), _arco("p" + nid, "has_semantic_shape", "sh" + nid),
            _arco("sh" + nid, "has_linked_resource", "r" + nid)]


def _spatialite_engine(path):
    from sqlalchemy import create_engine, event
    eng = create_engine("sqlite:///%s" % path)

    @event.listens_for(eng, "connect")
    def _carica(dbapi_conn, _record):
        dbapi_conn.enable_load_extension(True)
        for nome in _SPATIALITE:
            try:
                dbapi_conn.load_extension(nome)
                return
            except Exception:                     # noqa: BLE001
                continue
        raise RuntimeError("mod_spatialite non si carica")
    return eng


def make_project(tmp_path, *, srid=31700, georef=True, muro_sottile=False):
    """Tre unità: SU001 una scatola 4×1×3 a nord, SU002 una scatola 2×2×1 a
    sud, USV103 senza file. Coordinate glTF (Y in alto)."""
    radice = tmp_path / "Tempio"
    (radice / "EM" / "proxies").mkdir(parents=True)
    (radice / "EM" / "proxies" / "SU001.glb").write_bytes(
        quad_glb([(0, 0, -10), (4, 0, -10), (4, 3, -10), (0, 3, -10)]) if muro_sottile
        else box_glb(4.0, 3.0, 1.0, center=(2.0, 1.5, -10.0)))
    (radice / "EM" / "proxies" / "SU002.glb").write_bytes(box_glb(2.0, 1.0, 2.0, center=(1.0, 0.5, 5.0)))
    nodi = _unita("u1", "SU001") + _unita("u2", "SU002") + _unita("u3", "USV103", "USVs")
    if georef:
        nodi.append(_nodo("geo_g", "geo_position", "geo_position", epsg=31700,
                          shift_x=327300.0, shift_y=448370.0, shift_z=0.0))
    archi = _archi("u1") + _archi("u2") + _archi("u3")
    em = radice / "EM" / "tempio.em.json"
    em.write_text(json.dumps({"version": "1.0", "active_graph_id": "g",
                              "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
                              "graphs": {"g": {"graph_id": "g", "name": "Tempio",
                                               "nodes": nodi, "edges": archi}}}), encoding="utf-8")
    db = tmp_path / "db.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    con = sqlite3.connect(db)
    con.execute("UPDATE geometry_columns SET srid = ? WHERE f_table_name IN "
                "('pyunitastratigrafiche', 'pyunitastratigrafiche_usm')", (srid,))
    con.commit()
    con.close()
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    grafo, _ = read_graph_for_import(str(em))
    eng = _spatialite_engine(db)
    GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    return {"db": db, "eng": eng, "em": em, "grafo": grafo, "radice": radice}


@pytest.fixture
def progetto(tmp_path):
    return make_project(tmp_path)


def _per_nome(unita):
    return {u.name: u for u in unita}


def test_le_unita_con_il_loro_proxy(progetto):
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = _per_nome(edi.plan_units(progetto["grafo"], str(progetto["em"]),
                                     db=progetto["eng"], sito=SITO))
    assert unita["SU001"].usable and unita["SU001"].triangles == 12
    assert unita["SU001"].paths[0].endswith("SU001.glb")
    assert unita["USV103"].status == "missing" and not unita["USV103"].usable
    assert edi.status_text(unita["USV103"]) == "file non trovato"


def test_la_scelta_predefinita(progetto):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    geo = drw.georef_of(progetto["grafo"])
    scelta = edi.default_choice(unita, geo)
    nomi = {u.key: u.name for u in unita}
    assert {nomi[k] for k in scelta.plan} == {"SU001", "SU002"}
    assert {nomi[k] for k in scelta.prospect} == {"SU001", "SU002"}
    assert scelta.sides == ("N", "E", "S", "W") and scelta.shift_z is None
    assert edi.preview_line(unita, scelta, geo) == (
        "Dal 3D: 2 piante, 4 prospetti del sito, 2 prospetti di unità "
        "(si calcolano all'Applica); 1 unità senza modello utilizzabile.")


def test_le_schede_si_trovano_per_node_uuid(progetto):
    from modules.s3dgraphy.sync import em_drawings_import as edi
    schede = edi.schede_of(progetto["eng"], SITO, ["u1", "u2", "nessuno"])
    assert set(schede) == {"u1", "u2"}
    assert schede["u1"].us == "001" and schede["u1"].area == "1" and schede["u1"].unita_tipo == "US"


@pytest.mark.parametrize("srid, tipo", [(31700, "ok"), (3004, "convert"), (4326, "refuse"), (-1, "refuse")])
def test_la_regola_dell_srid(tmp_path, srid, tipo):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path, srid=srid)
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    geo = drw.georef_of(p["grafo"])
    decisione = edi.crs_decision(p["eng"], geo, edi.default_choice(unita, geo))
    assert decisione.kind == tipo
    if tipo == "convert":
        assert decisione.message == "Converto le piante in EPSG:3004 del database?"
    if tipo == "refuse":
        assert "ricrea il database in epsg:31700" in decisione.message.lower()


def test_senza_geometrie_nessun_controllo(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path, srid=4326)
    geo = drw.georef_of(p["grafo"])
    vuota = edi.Choice(plan=set(), prospect=set(), sides=(), shift_z=None)
    assert edi.crs_decision(p["eng"], geo, vuota).kind == "none"


def test_senza_layer_usm_le_sole_piante_passano(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path)
    con = sqlite3.connect(p["db"])
    con.execute("DELETE FROM geometry_columns WHERE f_table_name = 'pyunitastratigrafiche_usm'")
    con.commit()
    con.close()
    geo = drw.georef_of(p["grafo"])
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    piante = edi.Choice(plan={u.key for u in unita if u.usable}, prospect=set(), sides=(), shift_z=None)
    assert edi.crs_decision(p["eng"], geo, piante).kind == "ok"
    tutto = edi.default_choice(unita, geo)
    assert edi.crs_decision(p["eng"], geo, tutto).kind == "refuse"


def test_senza_posizione_niente_piante(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path, georef=False)
    geo = drw.georef_of(p["grafo"])
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    scelta = edi.default_choice(unita, geo)
    assert scelta.plan == set() and len(scelta.prospect) == 2
    assert edi.crs_decision(p["eng"], geo, scelta).kind == "ok"
```

- [ ] **Step 2: Lanciare i test e vederli fallire**

Run: `PYT tests/sync/test_em_drawings_import.py`
Expected: FAIL con `ModuleNotFoundError: No module named 'modules.s3dgraphy.sync.em_drawings_import'`.

- [ ] **Step 3: Scrivere la prima parte di `em_drawings_import.py`**

```python
# modules/s3dgraphy/sync/em_drawings_import.py
"""Piante e prospetti dai proxy 3D all'import dell'em.json: quali unità, il
sistema del database, il calcolo e la scrittura (spec
2026-10-18-geometrie-dai-proxy-3d-design, D8–D13).

Le unità sono quelle di ``em_narrative_3d.scene_proxies`` (un proxy per
risorsa, con il suo proprietario); i file si cercano come per i media
(``em_media_import.search_dirs_for`` e il risolutore di s3dgraphy). Il
controllo del sistema di riferimento si fa prima di scrivere qualsiasi cosa:
è il chiamante (la scheda Import) che, con ``refuse``, non comincia nemmeno.
"""
from __future__ import annotations

import datetime
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np

from .. import em_drawings as drw
from .. import glb_mesh as gm

PLAN_LAYER = "pyunitastratigrafiche"
VERTICAL_LAYER = "pyunitastratigrafiche_usm"


@dataclass
class DrawingUnit:
    key: str                        # id del nodo EM (= us_table.node_uuid)
    name: str
    unit_type: str
    locators: List[str]
    paths: List[str]
    status: str                     # ok | missing | heir | un motivo di glb_mesh
    detail: str = ""
    heir_of: str = ""
    hand_plan: bool = False
    hand_vertical: bool = False
    triangles: int = 0
    ymin: Optional[float] = None
    ymax: Optional[float] = None

    @property
    def usable(self) -> bool:
        return self.status == "ok"


@dataclass
class Choice:
    plan: Set[str]
    prospect: Set[str]
    sides: Tuple[str, ...] = drw.SIDES
    shift_z: Optional[float] = None         # None = quello dell'em.json

    @property
    def units(self) -> Set[str]:
        return set(self.plan) | set(self.prospect)


@dataclass(frozen=True)
class Scheda:
    id_us: int
    area: str
    us: str
    unita_tipo: str
    documentazione: Optional[str]


@dataclass(frozen=True)
class CrsDecision:
    kind: str                       # none | ok | convert | refuse
    message: str = ""
    plan_srid: Optional[int] = None
    usm_srid: Optional[int] = None
    source_epsg: Optional[int] = None


def _engine(db):
    from .em_media_import import _engine as engine_of
    return engine_of(db)


# ------------------------------------------------------------------ le unità

def plan_units(graph, emjson_path: str, *, search_dirs: Sequence[str] = (),
               db=None, sito: Optional[str] = None) -> List[DrawingUnit]:
    """Le unità con un proxy, con il loro file e quello che la finestra deve
    dire. Con ``db`` e ``sito``, anche se hanno già disegni fatti a mano."""
    from s3dgraphy.resources.locate import resolve
    from ..em_narrative_3d import scene_proxies
    from .em_media_import import _checksum, search_dirs_for
    scena = scene_proxies(graph)
    basi = search_dirs_for(emjson_path, [d for d in search_dirs or () if d])
    risorse = {p.key: p for p in scena.proxies}
    trovati: Dict[str, Optional[str]] = {}

    def percorso(chiave: str) -> Optional[str]:
        if chiave not in trovati:
            nodo = graph.find_node_by_id(chiave)
            stato = resolve({"id": chiave, "locator": risorse[chiave].locator,
                             "checksum": _checksum(nodo)}, base_dirs=basi)
            path = str(stato.get("path") or "")
            ok = stato.get("state") in ("on_disk", "both") and os.path.isfile(path)
            trovati[chiave] = os.path.realpath(path) if ok else None
        return trovati[chiave]

    unita: List[DrawingUnit] = []
    for chiave_u in sorted(scena.unit_proxies, key=lambda k: str(scena.names.get(k, k))):
        chiavi = scena.unit_proxies[chiave_u]
        nodo = graph.find_node_by_id(chiave_u)
        nome = str(scena.names.get(chiave_u, chiave_u))
        tipo = str(getattr(nodo, "node_type", "") or "")
        proprie = [k for k in chiavi if risorse[k].unit == chiave_u]
        if not proprie:
            padrone = risorse[chiavi[0]].unit
            unita.append(DrawingUnit(chiave_u, nome, tipo, [risorse[k].locator for k in chiavi], [],
                                     "heir", heir_of=str(scena.names.get(padrone, padrone))))
            continue
        u = DrawingUnit(chiave_u, nome, tipo, [risorse[k].locator for k in proprie], [], "ok")
        for k in proprie:
            path = percorso(k)
            if not path:
                u.status, u.detail = "missing", risorse[k].locator
                break
            info = gm.glb_info(path)
            if not info.ok:
                u.status, u.detail = info.reason, info.detail
                break
            u.paths.append(path)
            u.triangles += info.triangles
            if info.ymin is not None:
                u.ymin = info.ymin if u.ymin is None else min(u.ymin, info.ymin)
                u.ymax = info.ymax if u.ymax is None else max(u.ymax, info.ymax)
        if not u.usable:
            u.paths = []
        unita.append(u)
    if db is not None and sito:
        _mark_hand_drawn(db, sito, unita)
    return unita


def schede_of(db, sito: str, keys: Iterable[str]) -> Dict[str, Scheda]:
    """Le schede del sito delle unità date, per ``node_uuid``."""
    from sqlalchemy import text
    voluti = {str(k) for k in keys}
    out: Dict[str, Scheda] = {}
    with _engine(db).connect() as conn:
        for id_us, area, us, ut, doc, uuid in conn.execute(text(
                "SELECT id_us, area, us, unita_tipo, documentazione, node_uuid "
                "FROM us_table WHERE sito = :s"), {"s": sito}):
            if uuid is not None and str(uuid) in voluti:
                out[str(uuid)] = Scheda(int(id_us), str(area if area is not None else "1"),
                                        str(us), str(ut or ""), doc)
    return out


def _hand_drawn(conn, layer: str, sito: str) -> Set[Tuple[str, str]]:
    from sqlalchemy import text
    try:
        righe = conn.execute(text(
            "SELECT area_s, us_s, disegnatore, nome_doc FROM %s WHERE scavo_s = :s" % layer),
            {"s": sito}).fetchall()
    except Exception:                                       # noqa: BLE001
        return set()
    return {(str(a), str(u)) for a, u, dis, nome in righe
            if not (dis == drw.DRAWER and drw.is_derived_name(nome))}


def _mark_hand_drawn(db, sito: str, unita: List[DrawingUnit]) -> None:
    schede = schede_of(db, sito, [u.key for u in unita])
    with _engine(db).connect() as conn:
        piante, verticali = _hand_drawn(conn, PLAN_LAYER, sito), _hand_drawn(conn, VERTICAL_LAYER, sito)
    for u in unita:
        s = schede.get(u.key)
        if s is not None:
            u.hand_plan = (s.area, s.us) in piante
            u.hand_vertical = (s.area, s.us) in verticali


def status_text(u: DrawingUnit) -> str:
    if u.status == "missing":
        testo = "file non trovato"
    elif u.status == "heir":
        testo = "usa il 3D di %s" % u.heir_of
    elif u.status == "ok":
        testo = "ok"
    else:
        testo = gm.REASONS.get(u.status, u.status)
    note = []
    if u.hand_plan:
        note.append("ha già una pianta a mano")
    if u.hand_vertical:
        note.append("ha già un disegno verticale a mano")
    return "; ".join([testo] + note)


def default_choice(units: Sequence[DrawingUnit], georef) -> Choice:
    """Tutte le unità proprietarie di un proxy che si legge, pianta e prospetto,
    tranne quelle con un disegno a mano; i quattro lati; lo spostamento Z dell'em.json."""
    usabili = [u for u in units if u.usable]
    piante = {u.key for u in usabili if not u.hand_plan} if georef.usable else set()
    return Choice(plan=piante, prospect={u.key for u in usabili if not u.hand_vertical},
                  sides=drw.SIDES, shift_z=None)


# --------------------------------------------------------- il sistema del DB

def layer_srid(conn, table: str, column: str = "the_geom") -> Optional[int]:
    from sqlalchemy import text
    if conn.dialect.name.startswith("postgres"):
        q = ("SELECT srid FROM geometry_columns WHERE f_table_name = :t AND "
             "f_geometry_column = :g AND f_table_schema::name = ANY (current_schemas(false))")
    else:
        q = ("SELECT srid FROM geometry_columns WHERE lower(f_table_name) = lower(:t) "
             "AND lower(f_geometry_column) = lower(:g)")
    try:
        valore = conn.execute(text(q), {"t": table, "g": column}).scalar()
    except Exception:                                       # noqa: BLE001
        return None
    return int(valore) if valore is not None else None


def wants(choice: Choice, georef) -> Tuple[bool, bool]:
    piante = bool(choice.plan) and georef.usable
    verticali = bool(choice.prospect) or (bool(choice.sides) and bool(choice.units))
    return piante, verticali


def _descrivi(srid) -> str:
    kind = drw.crs_kind(srid)
    if kind == "geographic":
        return "è in gradi (EPSG:%s)" % srid
    return "non ha un sistema di riferimento" if srid in (None, 0, -1) else \
        "ha un sistema sconosciuto (EPSG:%s)" % srid


def crs_decision(db, georef, choice: Choice) -> CrsDecision:
    """La regola dell'SRID (spec D8), da chiedere prima di scrivere qualsiasi cosa."""
    piante, verticali = wants(choice, georef)
    if not (piante or verticali):
        return CrsDecision("none")
    with _engine(db).connect() as conn:
        plan_srid = layer_srid(conn, PLAN_LAYER) if piante else None
        usm_srid = layer_srid(conn, VERTICAL_LAYER) if verticali else None
    problemi = []
    if piante and drw.crs_kind(plan_srid) != "metric":
        problemi.append("il layer %s %s" % (PLAN_LAYER, _descrivi(plan_srid)))
    if verticali and drw.crs_kind(usm_srid) != "metric":
        problemi.append("il layer %s %s" % (VERTICAL_LAYER, _descrivi(usm_srid)))
    sorgente = georef.epsg if georef.usable else None
    if problemi:
        rimedio = ("ricrea il database in EPSG:%s (quello dell'em.json)" % georef.epsg
                   if georef.usable else "ricrea il database in un sistema metrico")
        return CrsDecision("refuse", (
            "Nel database %s: piante e prospetti non ci possono stare. Per avere le "
            "geometrie, %s; oppure togli la casella «Ricava piante e prospetti dai "
            "modelli 3D» e importa solo le schede." % ("; ".join(problemi), rimedio)),
            plan_srid, usm_srid, sorgente)
    if piante and int(plan_srid) != int(georef.epsg):
        return CrsDecision("convert", "Converto le piante in EPSG:%s del database?" % plan_srid,
                           plan_srid, usm_srid, sorgente)
    return CrsDecision("ok", "", plan_srid, usm_srid, sorgente)


def preview_line(units: Sequence[DrawingUnit], choice: Choice, georef) -> str:
    piante = len(choice.plan) if georef.usable else 0
    lati = len(choice.sides) if choice.units else 0
    testo = ("Dal 3D: %d piante, %d prospetti del sito, %d prospetti di unità "
             "(si calcolano all'Applica)" % (piante, lati, len(choice.prospect)))
    senza = sum(1 for u in units if not u.usable)
    if senza:
        testo += "; %d unità senza modello utilizzabile" % senza
    return testo + "."
```

- [ ] **Step 4: Lanciare i test e vederli passare**

Run: `PYT tests/sync/test_em_drawings_import.py`
Expected: PASS (11 test, compresi i 4 casi della regola dell'SRID).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/em_drawings_import.py tests/sync/test_em_drawings_import.py
git commit -m "feat(3d): unità con proxy, scelta predefinita, schede per node_uuid e regola dell'SRID del database prima di scrivere"
```

---

### Task 6: `em_drawings_import` — calcolo dei disegni

**Files:**
- Modify: `modules/s3dgraphy/sync/em_drawings_import.py` (in coda)
- Test: `tests/sync/test_em_drawings_import.py` (in coda)

**Interfaces:**
- Consumes: Task 1 (`read_triangles`, `GlbError`), Task 2–4 (`scene_from_gltf`, `place`, `plan_geometry`, `SITE_VIEWS`, `unit_view`, `view_geometry`, `depth`, `centroid_xy`, `site_frame`, `lay_out`, `span_u`, `translated`, `side_name`, `unit_drawing_names`, `PLAN_NAME`), Task 5 (`DrawingUnit`, `Choice`, `Scheda`).
- Produces: `Drawing(layer, tipo, nome, note, features: List[Tuple[key, QgsGeometry]], plan: bool)`; `compute_drawings(graph, units, choice, georef, schede, *, source_name="em.json", lang="it", tipi=("Planimetria", "Prospetto"), progress=None) -> Tuple[List[Drawing], Dict[str, str]]` (i disegni e le unità saltate, `{chiave: motivo}`).

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# in coda a tests/sync/test_em_drawings_import.py

def _calcola(p, scelta=None):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    geo = drw.georef_of(p["grafo"])
    scelta = scelta or edi.default_choice(unita, geo)
    schede = edi.schede_of(p["eng"], SITO, [u.key for u in unita])
    return edi.compute_drawings(p["grafo"], unita, scelta, geo, schede, source_name="tempio.em.json")


def test_i_disegni_di_due_unita(progetto):
    disegni, saltate = _calcola(progetto)
    nomi = [d.nome for d in disegni]
    assert nomi == ["3D-PLA", "3D-PRO-N", "3D-PRO-E", "3D-PRO-S", "3D-PRO-W",
                    "3D-PRO-US001", "3D-PRO-US002"]
    assert saltate == {}
    pianta = disegni[0]
    assert pianta.layer == "pyunitastratigrafiche" and pianta.tipo == "Planimetria"
    aree = sorted(round(g.area(), 6) for _k, g in pianta.features)
    assert aree == [4.0, 4.0]                     # SU001: 4 × 1; SU002: 2 × 2
    x0 = min(g.boundingBox().xMinimum() for _k, g in pianta.features)
    assert x0 == pytest.approx(327300.0)          # spostamento X dell'em.json


def test_le_viste_verticali_non_si_sovrappongono(progetto):
    from modules.s3dgraphy import em_drawings as drw
    disegni, _ = _calcola(progetto)
    verticali = [d for d in disegni if d.layer == "pyunitastratigrafiche_usm"]
    assert all(d.tipo == "Prospetto" for d in verticali)
    campate = []
    for d in verticali:
        lo = min(drw.span_u(g)[0] for _k, g in d.features)
        hi = max(drw.span_u(g)[1] for _k, g in d.features)
        campate.append((lo, hi))
    for (a0, a1), (b0, b1) in zip(campate, campate[1:]):
        assert b0 == pytest.approx(a1 + 10.0)
    assert campate[0][0] == pytest.approx(0.0)


def test_nel_prospetto_nord_il_piu_vicino_e_scritto_per_ultimo(progetto):
    disegni, _ = _calcola(progetto)
    nord = next(d for d in disegni if d.nome == "3D-PRO-N")
    # SU001 sta a nord (z glTF −10 → Y +10): è il più vicino a chi guarda da nord
    assert [k for k, _g in nord.features] == ["u2", "u1"]


def test_un_muro_senza_spessore_ha_il_prospetto_ma_non_la_pianta(tmp_path):
    p = make_project(tmp_path, muro_sottile=True)
    disegni, saltate = _calcola(p)
    pianta = next(d for d in disegni if d.nome == "3D-PLA")
    assert [k for k, _g in pianta.features] == ["u2"]
    assert saltate == {"u1": "vuoto in pianta"}
    assert "3D-PRO-US001" in [d.nome for d in disegni]


def test_lo_spostamento_z_scelto_vale_per_le_quote(progetto):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    geo = drw.georef_of(progetto["grafo"])
    scelta = edi.default_choice(unita, geo)
    scelta.shift_z = 495.0
    disegni, _ = _calcola(progetto, scelta)
    nord = next(d for d in disegni if d.nome == "3D-PRO-N")
    assert min(g.boundingBox().yMinimum() for _k, g in nord.features) == pytest.approx(495.0)
```

- [ ] **Step 2: Lanciare i test e vederli fallire**

Run: `PYT tests/sync/test_em_drawings_import.py`
Expected: FAIL con `AttributeError: module ... has no attribute 'compute_drawings'`.

- [ ] **Step 3: Scrivere il calcolo**

```python
# in coda a modules/s3dgraphy/sync/em_drawings_import.py

# ----------------------------------------------------------------- il calcolo

@dataclass
class Drawing:
    layer: str
    tipo: str
    nome: str
    note: str
    features: List[Tuple[str, object]] = field(default_factory=list)   # (chiave, QgsGeometry)
    plan: bool = False


_LATI = {"it": {"N": "nord", "E": "est", "S": "sud", "W": "ovest"},
         "en": {"N": "north", "E": "east", "S": "south", "W": "west"}}
_SINISTRA = {"N": "E", "E": "S", "S": "W", "W": "N"}
_NOTE = {
    "it": {"plan": "Pianta ricavata dai proxy 3D di {src}, EPSG:{epsg}.",
           "side": ("Prospetto {lato} del sito ricavato dai proxy 3D di {src}: X = metri lungo "
                    "la vista ({sinistra} a sinistra), Y = quota (spostamento Z {z} m)."),
           "unit": ("Prospetto di {unita} visto da {da}, ricavato dal proxy 3D di {src}: "
                    "X = metri lungo la vista, Y = quota (spostamento Z {z} m).")},
    "en": {"plan": "Plan derived from the 3D proxies of {src}, EPSG:{epsg}.",
           "side": ("{lato} elevation of the site derived from the 3D proxies of {src}: X = metres "
                    "along the view ({sinistra} on the left), Y = elevation (Z shift {z} m)."),
           "unit": ("Elevation of {unita} seen from {da}, derived from the 3D proxy of {src}: "
                    "X = metres along the view, Y = elevation (Z shift {z} m).")},
}


def _parole(lang: str):
    lang = (lang or "it")[:2].lower()
    return _NOTE.get(lang, _NOTE["en"]), _LATI.get(lang, _LATI["en"])


def compute_drawings(graph, units: Sequence[DrawingUnit], choice: Choice, georef,
                     schede: Dict[str, Scheda], *, source_name: str = "em.json", lang: str = "it",
                     tipi: Tuple[str, str] = ("Planimetria", "Prospetto"),
                     progress: Optional[Callable[[int, int, str], None]] = None
                     ) -> Tuple[List[Drawing], Dict[str, str]]:
    """I disegni della scelta: la pianta, i lati del sito, i prospetti delle
    unità, impaginati. Torna anche le unità saltate, con il motivo."""
    note, lati = _parole(lang)
    z = georef.shift_z if choice.shift_z is None else float(choice.shift_z)
    per_chiave = {u.key: u for u in units}
    voluti = sorted(choice.units, key=lambda k: per_chiave[k].name if k in per_chiave else k)
    saltate: Dict[str, str] = {}
    mesh: Dict[str, np.ndarray] = {}
    for i, k in enumerate(voluti):
        u = per_chiave.get(k)
        if progress:
            progress(i, len(voluti), u.name if u else k)
        if u is None or not u.usable:
            saltate[k] = status_text(u) if u else "unità sconosciuta"
            continue
        if k not in schede:
            saltate[k] = "scheda non trovata"
            continue
        try:
            parti = [drw.scene_from_gltf(gm.read_triangles(p)) for p in u.paths]
        except gm.GlbError as e:
            saltate[k] = str(e)
            continue
        tri = np.concatenate(parti)
        mesh[k] = drw.place(graph, georef, tri.reshape(-1, 3), z).reshape(-1, 3, 3)
    if progress:
        progress(len(voluti), len(voluti), "")
    disegni: List[Drawing] = []
    if not mesh:
        return disegni, saltate
    piante = {k: drw.plan_geometry(t) for k, t in mesh.items()}
    if georef.usable and choice.plan:
        pianta = Drawing(PLAN_LAYER, tipi[0], drw.PLAN_NAME,
                         note["plan"].format(src=source_name, epsg=georef.epsg), plan=True)
        for k in sorted(choice.plan & set(mesh), key=lambda k: per_chiave[k].name):
            if piante.get(k) is None:
                saltate[k] = "vuoto in pianta"
            else:
                pianta.features.append((k, piante[k]))
        disegni.append(pianta)
    origine, centro = drw.site_frame(mesh.values())
    verticali: List[Drawing] = []
    for lato in choice.sides:
        vista = drw.SITE_VIEWS[lato]
        sagome = []
        for k, t in mesh.items():
            g = drw.view_geometry(t, vista, origine)
            if g is not None:
                sagome.append((drw.depth(t, vista), per_chiave[k].name, k, g))
        sagome.sort(key=lambda s: (-s[0], s[1]))
        verticali.append(Drawing(VERTICAL_LAYER, tipi[1], drw.side_name(lato), note["side"].format(
            lato=lati[lato], src=source_name, sinistra=lati[_SINISTRA[lato]], z=z),
            [(k, g) for _d, _n, k, g in sagome]))
    prospetti = [k for k in voluti if k in mesh and k in choice.prospect]
    nomi = drw.unit_drawing_names([(k, schede[k].unita_tipo, schede[k].us, schede[k].area)
                                   for k in prospetti])
    for k in prospetti:
        vista = drw.unit_view(nomi[k], piante.get(k), drw.centroid_xy(mesh[k]), centro)
        g = drw.view_geometry(mesh[k], vista, origine)
        if g is None:
            saltate.setdefault(k, "vuoto nel prospetto")
            continue
        verticali.append(Drawing(VERTICAL_LAYER, tipi[1], nomi[k], note["unit"].format(
            unita=per_chiave[k].name, da=vista.side, src=source_name, z=z), [(k, g)]))
    verticali = [d for d in verticali if d.features]
    campate = [(min(drw.span_u(g)[0] for _k, g in d.features),
                max(drw.span_u(g)[1] for _k, g in d.features)) for d in verticali]
    for d, du in zip(verticali, drw.lay_out(campate)):
        d.features = [(k, drw.translated(g, du)) for k, g in d.features]
    return disegni + verticali, saltate
```

- [ ] **Step 4: Lanciare i test e vederli passare**

Run: `PYT tests/sync/test_em_drawings_import.py`
Expected: PASS (16 test).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/em_drawings_import.py tests/sync/test_em_drawings_import.py
git commit -m "feat(3d): calcolo di pianta, lati del sito e prospetti delle unità dalla scelta, dal più lontano al più vicino, impaginati"
```

---

### Task 7: `em_drawings_import` — scrittura nel database (SQLite e PostgreSQL)

**Files:**
- Modify: `modules/s3dgraphy/sync/em_drawings_import.py` (in coda)
- Test: `tests/sync/test_em_drawings_import.py` (in coda), `tests/sync/test_em_drawings_import_pg.py` (nuovo)

**Interfaces:**
- Consumes: Task 5–6 (`Drawing`, `Scheda`, `CrsDecision`, `compute_drawings`, `plan_units`, `schede_of`, `default_choice`, `crs_decision`); `utility.qfield_importer.build_geom_sql`; `em_native_import.thesaurus_lingua`.
- Produces: `WriteResult(plans, side_views, unit_views, features, removed, documents, documents_removed, pairs_updated, warnings, skipped, converted)` con `.summary(units=())`; `doc_types(db, lingua=None) -> (str, str)`; `write_drawings(db, sito, drawings, schede, decision, *, source_name, today=None, rilievi=None) -> WriteResult`; `run_drawings(db, graph, sito, emjson_path, *, units, choice, georef, decision, lang=None, progress=None) -> WriteResult`.

- [ ] **Step 1: Scrivere i test che falliscono (SQLite)**

```python
# in coda a tests/sync/test_em_drawings_import.py

def _scrivi(p, decisione_attesa="ok", scelta=None):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    geo = drw.georef_of(p["grafo"])
    scelta = scelta or edi.default_choice(unita, geo)
    decisione = edi.crs_decision(p["eng"], geo, scelta)
    assert decisione.kind == decisione_attesa
    return edi.run_drawings(p["eng"], p["grafo"], SITO, str(p["em"]), units=unita,
                            choice=scelta, georef=geo, decision=decisione, lang="it")


def _righe(p, sql, *args):
    con = sqlite3.connect(p["db"])
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def test_poligoni_documenti_e_schede_si_richiamano_insieme(progetto):
    esito = _scrivi(progetto)
    assert (esito.plans, esito.side_views, esito.unit_views) == (2, 4, 2)
    piante = _righe(progetto, "SELECT scavo_s, area_s, us_s, unita_tipo_s, tipo_doc, nome_doc, "
                              "disegnatore, coord FROM pyunitastratigrafiche ORDER BY us_s")
    assert [r[:6] for r in piante] == [(SITO, "1", "001", "US", "Planimetria", "3D-PLA"),
                                       (SITO, "1", "002", "US", "Planimetria", "3D-PLA")]
    assert all(r[6] == "pyArchInit 3D" and r[7].startswith("POINT(") for r in piante)
    documenti = _righe(progetto, "SELECT tipo_documentazione, nome_doc, disegnatore FROM "
                                 "documentazione_table WHERE sito = ? ORDER BY nome_doc", SITO)
    assert [(t, n) for t, n, _d in documenti] == [
        ("Planimetria", "3D-PLA"), ("Prospetto", "3D-PRO-E"), ("Prospetto", "3D-PRO-N"),
        ("Prospetto", "3D-PRO-S"), ("Prospetto", "3D-PRO-US001"), ("Prospetto", "3D-PRO-US002"),
        ("Prospetto", "3D-PRO-W")]
    # il filtro della scheda Documentazione trova le «US verticali» del documento
    verticali = _righe(progetto, "SELECT us FROM pyarchinit_usm_view WHERE sito = ? AND "
                                 "nome_doc = ? AND tipo_doc = ?", SITO, "3D-PRO-N", "Prospetto")
    assert sorted(r[0] for r in verticali) == ["001", "002"]
    orizzontali = _righe(progetto, "SELECT us FROM pyarchinit_us_view WHERE sito = ? AND "
                                   "nome_doc = ? AND tipo_doc = ?", SITO, "3D-PLA", "Planimetria")
    assert sorted(r[0] for r in orizzontali) == ["001", "002"]
    import ast
    doc = ast.literal_eval(_righe(progetto, "SELECT documentazione FROM us_table WHERE sito = ? "
                                            "AND us = '001'", SITO)[0][0])
    assert doc == [["Planimetria", "3D-PLA"], ["Prospetto", "3D-PRO-N"], ["Prospetto", "3D-PRO-E"],
                   ["Prospetto", "3D-PRO-S"], ["Prospetto", "3D-PRO-W"], ["Prospetto", "3D-PRO-US001"]]


def test_reimportare_sostituisce_solo_il_ricavato(progetto):
    _scrivi(progetto)
    con = sqlite3.connect(progetto["db"])
    con.enable_load_extension(True)
    for nome in _SPATIALITE:
        try:
            con.load_extension(nome)
            break
        except sqlite3.Error:
            continue
    con.execute("INSERT INTO pyunitastratigrafiche (gid, scavo_s, area_s, us_s, disegnatore, tipo_doc, "
                "nome_doc, the_geom) VALUES (9999, ?, '1', '001', 'Enzo', 'Planimetria', 'P1', "
                "CastToMultiPolygon(GeomFromText('POLYGON((0 0,1 0,1 1,0 0))', 31700)))", (SITO,))
    con.commit()
    con.close()
    esito = _scrivi(progetto)
    assert esito.removed == 2 + 4 * 2 + 2              # le piante, i lati, i prospetti di prima
    totale = _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche WHERE scavo_s = ?", SITO)[0][0]
    # SU001 ha ora una pianta a mano: la scelta predefinita non le rifà la sua
    assert totale == 2                                 # SU002 ricavata + quella a mano di SU001
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE sito = ?", SITO)[0][0] == 7


def test_il_poligono_corretto_a_mano_resta_col_suo_documento(progetto):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    _scrivi(progetto)
    con = sqlite3.connect(progetto["db"])
    con.execute("UPDATE pyunitastratigrafiche_usm SET disegnatore = 'Enzo' WHERE nome_doc = '3D-PRO-US001'")
    con.commit()
    con.close()
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    geo = drw.georef_of(progetto["grafo"])
    scelta = edi.default_choice(unita, geo)
    su001 = next(u for u in unita if u.name == "SU001")
    assert su001.hand_vertical and su001.key not in scelta.prospect
    _scrivi(progetto, scelta=scelta)
    assert _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche_usm WHERE nome_doc = '3D-PRO-US001'")[0][0] == 1
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE nome_doc = '3D-PRO-US001'")[0][0] == 1


def test_convertire_le_piante_in_un_altro_sistema(tmp_path):
    p = make_project(tmp_path, srid=3004)
    esito = _scrivi(p, decisione_attesa="convert")
    assert esito.converted == (31700, 3004)
    x = _righe(p, "SELECT coord FROM pyunitastratigrafiche LIMIT 1")[0][0]
    assert not x.startswith("POINT(3273")                # le coordinate non sono più quelle di Stereo 70
    assert "convertite da EPSG:31700 a EPSG:3004" in esito.summary()


def test_il_riepilogo(progetto):
    esito = _scrivi(progetto)
    assert esito.summary().startswith("Dal 3D: 2 piante, 4 prospetti del sito, 2 prospetti di unità")
```

- [ ] **Step 2: Scrivere il test PostgreSQL che fallisce**

```python
# tests/sync/test_em_drawings_import_pg.py
"""La scrittura dei disegni ricavati dal 3D su PostgreSQL/PostGIS, in uno
schema temporaneo di pyarchinit_test_pg (gli altri database del server non
si toccano)."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from tests.sync.conftest_pg import PG_CONN_STR  # noqa: E402

_DDL = [
    "CREATE TABLE us_table (id_us SERIAL PRIMARY KEY, sito TEXT, area TEXT, us TEXT, "
    "unita_tipo TEXT, node_uuid TEXT, documentazione TEXT)",
    "CREATE TABLE documentazione_table (id_documentazione SERIAL PRIMARY KEY, sito TEXT, "
    "nome_doc TEXT, data TEXT, tipo_documentazione TEXT, sorgente TEXT, scala TEXT, "
    "disegnatore TEXT, note TEXT)",
]
_LAYER = ("CREATE TABLE {t} (gid INTEGER PRIMARY KEY, area_s TEXT, scavo_s TEXT, us_s TEXT, "
          "stratigraph_index_us INTEGER, tipo_us_s TEXT, rilievo_originale TEXT, disegnatore TEXT, "
          "data TEXT, tipo_doc TEXT, nome_doc TEXT, coord TEXT, unita_tipo_s TEXT, "
          "the_geom geometry(MultiPolygon, {srid}))")
_VISTA = ("CREATE VIEW pyarchinit_usm_view AS SELECT a.gid, a.tipo_doc, a.nome_doc, a.the_geom, "
          "b.sito, b.area, b.us FROM pyunitastratigrafiche_usm a JOIN us_table b "
          "ON (a.area_s = b.area AND a.scavo_s = b.sito AND a.us_s = b.us)")


@pytest.fixture
def pg_schema():
    from sqlalchemy import create_engine, text
    nome = "drw_" + uuid.uuid4().hex[:8]
    base = create_engine(PG_CONN_STR)
    try:
        with base.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.execute(text("CREATE SCHEMA %s" % nome))
    except Exception as e:                              # noqa: BLE001
        pytest.skip("PostGIS non disponibile su pyarchinit_test_pg: %s" % e)
    eng = create_engine(PG_CONN_STR, connect_args={"options": "-csearch_path=%s,public" % nome})
    with eng.begin() as conn:
        for ddl in _DDL:
            conn.execute(text(ddl))
        for t in ("pyunitastratigrafiche", "pyunitastratigrafiche_usm"):
            conn.execute(text(_LAYER.format(t=t, srid=31700)))
        conn.execute(text(_VISTA))
    yield eng
    eng.dispose()
    with base.begin() as conn:
        conn.execute(text("DROP SCHEMA %s CASCADE" % nome))
    base.dispose()


def test_su_postgis_si_scrive_e_si_richiama_insieme(pg_schema, tmp_path):
    from sqlalchemy import text
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    from tests.sync.test_em_drawings_import import SITO, make_project
    p = make_project(tmp_path)                          # l'em.json e i GLB; le schede qui sotto
    with pg_schema.begin() as conn:
        for nid, us in (("u1", "001"), ("u2", "002")):
            conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, documentazione) "
                              "VALUES (:s, '1', :u, 'US', :n, '[]')"), {"s": SITO, "u": us, "n": nid})
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=pg_schema, sito=SITO)
    geo = drw.georef_of(p["grafo"])
    scelta = edi.default_choice(unita, geo)
    decisione = edi.crs_decision(pg_schema, geo, scelta)
    assert decisione.kind == "ok"
    esito = edi.run_drawings(pg_schema, p["grafo"], SITO, str(p["em"]), units=unita, choice=scelta,
                             georef=geo, decision=decisione, lang="it")
    assert (esito.plans, esito.side_views, esito.unit_views) == (2, 4, 2)
    with pg_schema.connect() as conn:
        righe = conn.execute(text("SELECT us FROM pyarchinit_usm_view WHERE sito = :s AND "
                                  "nome_doc = '3D-PRO-N' AND tipo_doc = 'Prospetto'"), {"s": SITO}).fetchall()
        assert sorted(r[0] for r in righe) == ["001", "002"]
        assert conn.execute(text("SELECT ST_SRID(the_geom) FROM pyunitastratigrafiche LIMIT 1")).scalar() == 31700
    esito2 = edi.run_drawings(pg_schema, p["grafo"], SITO, str(p["em"]), units=unita, choice=scelta,
                              georef=geo, decision=decisione, lang="it")
    assert esito2.removed == 2 + 8 + 2
```

- [ ] **Step 3: Lanciare i test e vederli fallire**

Run: `PYT tests/sync/test_em_drawings_import.py tests/sync/test_em_drawings_import_pg.py`
Expected: FAIL con `AttributeError: ... has no attribute 'run_drawings'`. Il test PG può anche essere SKIPPED, se PostGIS non si può attivare: va scritto nel ledger.

- [ ] **Step 4: Scrivere la scrittura**

```python
# in coda a modules/s3dgraphy/sync/em_drawings_import.py

# ---------------------------------------------------------------- la scrittura

@dataclass
class WriteResult:
    plans: int = 0
    side_views: int = 0
    unit_views: int = 0
    features: int = 0
    removed: int = 0
    documents: int = 0
    documents_removed: int = 0
    pairs_updated: int = 0
    warnings: List[str] = field(default_factory=list)
    skipped: Dict[str, str] = field(default_factory=dict)
    converted: Optional[Tuple[int, int]] = None

    def summary(self, units: Sequence[DrawingUnit] = ()) -> str:
        nomi = {u.key: u.name for u in units}
        testo = ("Dal 3D: %d piante, %d prospetti del sito, %d prospetti di unità"
                 % (self.plans, self.side_views, self.unit_views))
        if self.skipped:
            voci = ["%s: %s" % (nomi.get(k, k), m) for k, m in sorted(self.skipped.items(),
                                                                       key=lambda kv: nomi.get(kv[0], kv[0]))]
            testo += "; %d saltate (%s)" % (len(voci), "; ".join(voci[:8]) +
                                             (" e altre %d" % (len(voci) - 8) if len(voci) > 8 else ""))
        if self.converted:
            testo += "; piante convertite da EPSG:%d a EPSG:%d" % self.converted
        testo += "."
        if self.warnings:
            testo += "\nAvvisi: " + "; ".join(self.warnings[:5])
        return testo


def doc_types(db, lingua: Optional[str] = None) -> Tuple[str, str]:
    """I tipi dei documenti dal thesaurus (9.1 PLA e PRO) nella lingua del
    plugin, poi IT, poi «Planimetria» e «Prospetto»."""
    from sqlalchemy import text
    from .em_native_import import thesaurus_lingua
    lingua = lingua or thesaurus_lingua()
    trovati: Dict[str, str] = {}
    try:
        with _engine(db).connect() as conn:
            for lng in (lingua, "IT"):
                for sigla, estesa in conn.execute(text(
                        "SELECT sigla, sigla_estesa FROM pyarchinit_thesaurus_sigle WHERE "
                        "nome_tabella = 'documentazione_table' AND tipologia_sigla = '9.1' "
                        "AND lingua = :l AND sigla IN ('PLA', 'PRO')"), {"l": lng}):
                    if estesa:
                        trovati.setdefault(str(sigla), str(estesa))
    except Exception:                                       # noqa: BLE001
        pass
    return trovati.get("PLA", "Planimetria"), trovati.get("PRO", "Prospetto")


def _columns(eng, table: str) -> Set[str]:
    from sqlalchemy import inspect
    try:
        return {c["name"] for c in inspect(eng).get_columns(table)}
    except Exception:                                       # noqa: BLE001
        return set()


def _centroid(g) -> str:
    c = g.centroid().asPoint()
    return "POINT(%.6f %.6f)" % (c.x(), c.y())


def write_drawings(db, sito: str, drawings: Sequence[Drawing], schede: Dict[str, Scheda],
                   decision: CrsDecision, *, source_name: str, today: Optional[str] = None,
                   rilievi: Optional[Dict[str, str]] = None) -> WriteResult:
    """Sostituisce l'insieme ricavato del sito: poligoni nei due layer,
    documenti, coppie della scheda US. Una transazione; un SAVEPOINT per riga."""
    from sqlalchemy import text
    from ...utility.qfield_importer import build_geom_sql
    esito = WriteResult()
    oggi = today or datetime.date.today().isoformat()
    eng = _engine(db)
    is_pg = eng.dialect.name.startswith("postgres")
    colonne = {l: _columns(eng, l) for l in (PLAN_LAYER, VERTICAL_LAYER)}
    trasforma = None
    if decision.kind == "convert":
        from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
        trasforma = QgsCoordinateTransform(QgsCoordinateReferenceSystem.fromEpsgId(int(decision.source_epsg)),
                                           QgsCoordinateReferenceSystem.fromEpsgId(int(decision.plan_srid)),
                                           QgsProject.instance())
        esito.converted = (int(decision.source_epsg), int(decision.plan_srid))
    geom_sql = build_geom_sql(is_pg, True, False, None)
    with eng.begin() as conn:
        for layer in (PLAN_LAYER, VERTICAL_LAYER):
            if not colonne[layer]:
                continue
            r = conn.execute(text("DELETE FROM %s WHERE scavo_s = :s AND disegnatore = :d "
                                  "AND nome_doc LIKE '3D-%%'" % layer), {"s": sito, "d": drw.DRAWER})
            esito.removed += max(r.rowcount or 0, 0)
        gid = {l: int(conn.execute(text("SELECT COALESCE(MAX(gid), 0) FROM %s" % l)).scalar() or 0)
               for l in (PLAN_LAYER, VERTICAL_LAYER) if colonne[l]}
        coppie: Dict[int, List[List[str]]] = {}
        for d in drawings:
            if not d.features or not colonne.get(d.layer):
                continue
            srid = decision.plan_srid if d.plan else decision.usm_srid
            scritti = 0
            for k, g in d.features:
                s = schede.get(k)
                if s is None:
                    continue
                if d.plan and trasforma is not None:
                    from qgis.core import QgsGeometry
                    g = QgsGeometry(g)
                    g.transform(trasforma)
                gid[d.layer] += 1
                valori = {"gid": gid[d.layer], "area_s": s.area, "scavo_s": sito, "us_s": s.us,
                          "stratigraph_index_us": 1, "rilievo_originale": (rilievi or {}).get(k, ""),
                          "disegnatore": drw.DRAWER, "data": oggi, "tipo_doc": d.tipo,
                          "nome_doc": d.nome, "coord": _centroid(g), "unita_tipo_s": s.unita_tipo}
                usate = [c for c in valori if c in colonne[d.layer]]
                sql = 'INSERT INTO %s (%s, "the_geom") VALUES (%s, %s)' % (
                    d.layer, ", ".join('"%s"' % c for c in usate), ", ".join(":" + c for c in usate), geom_sql)
                try:
                    with conn.begin_nested():
                        conn.execute(text(sql), {**{c: valori[c] for c in usate},
                                                 "wkt": g.asWkt(6), "srid": int(srid)})
                except Exception as e:                      # noqa: BLE001
                    esito.warnings.append("%s %s: %s" % (d.nome, s.us, str(e).splitlines()[0][:120]))
                    continue
                scritti += 1
                lista = coppie.setdefault(s.id_us, [])
                if [d.tipo, d.nome] not in lista:
                    lista.append([d.tipo, d.nome])
            esito.features += scritti
            if scritti:
                if d.plan:
                    esito.plans += scritti
                elif d.nome in {drw.side_name(x) for x in drw.SIDES}:
                    esito.side_views += 1
                else:
                    esito.unit_views += 1
        # i documenti, con lo stesso tipo e nome dei poligoni
        ora = set()
        for d in drawings:
            if not any(schede.get(k) for k, _g in d.features):
                continue
            ora.add((d.tipo, d.nome))
            riga = conn.execute(text(
                "SELECT id_documentazione, disegnatore FROM documentazione_table WHERE sito = :s "
                "AND nome_doc = :n AND tipo_documentazione = :t"),
                {"s": sito, "n": d.nome, "t": d.tipo}).fetchone()
            sorgente = "em.json: %s" % source_name
            if riga is None:
                nid = int(conn.execute(text(
                    "SELECT COALESCE(MAX(id_documentazione), 0) + 1 FROM documentazione_table")).scalar())
                conn.execute(text(
                    "INSERT INTO documentazione_table (id_documentazione, sito, nome_doc, data, "
                    "tipo_documentazione, sorgente, scala, disegnatore, note) VALUES "
                    "(:i, :s, :n, :dt, :t, :src, '', :d, :note)"),
                    {"i": nid, "s": sito, "n": d.nome, "dt": oggi, "t": d.tipo, "src": sorgente,
                     "d": drw.DRAWER, "note": d.note})
                esito.documents += 1
            elif riga[1] == drw.DRAWER:
                conn.execute(text("UPDATE documentazione_table SET data = :dt, sorgente = :src, "
                                  "note = :note WHERE id_documentazione = :i"),
                             {"dt": oggi, "src": sorgente, "note": d.note, "i": riga[0]})
            else:
                esito.warnings.append("il documento %s «%s» c'era già e non è ricavato: "
                                      "i disegni lo usano" % (d.tipo, d.nome))
        for i, tipo, nome in conn.execute(text(
                "SELECT id_documentazione, tipo_documentazione, nome_doc FROM documentazione_table "
                "WHERE sito = :s AND disegnatore = :d AND nome_doc LIKE '3D-%'"),
                {"s": sito, "d": drw.DRAWER}).fetchall():
            if (tipo, nome) in ora:
                continue
            citato = any(conn.execute(text(
                "SELECT 1 FROM %s WHERE scavo_s = :s AND tipo_doc = :t AND nome_doc = :n LIMIT 1" % l),
                {"s": sito, "t": tipo, "n": nome}).fetchone() for l in (PLAN_LAYER, VERTICAL_LAYER)
                if colonne[l])
            if not citato:
                conn.execute(text("DELETE FROM documentazione_table WHERE id_documentazione = :i"), {"i": i})
                esito.documents_removed += 1
        # le coppie della scheda US
        for id_us, valore in conn.execute(text(
                "SELECT id_us, documentazione FROM us_table WHERE sito = :s"), {"s": sito}).fetchall():
            nuove = coppie.get(int(id_us), [])
            if not nuove and "3D-" not in str(valore or ""):
                continue
            dopo = drw.with_derived_pairs(valore, nuove)
            if dopo is None:
                esito.warnings.append("la Documentazione della scheda %s non si legge: "
                                      "non l'ho toccata" % id_us)
                continue
            if dopo != (valore or ""):
                conn.execute(text("UPDATE us_table SET documentazione = :v WHERE id_us = :i"),
                             {"v": dopo, "i": int(id_us)})
                esito.pairs_updated += 1
    return esito


def run_drawings(db, graph, sito: str, emjson_path: str, *, units: Sequence[DrawingUnit],
                 choice: Choice, georef, decision: CrsDecision, lang: Optional[str] = None,
                 progress: Optional[Callable[[int, int, str], None]] = None) -> WriteResult:
    """Tutto il passo dei disegni, dopo l'import delle schede."""
    if lang is None:
        try:
            from qgis.core import QgsSettings
            lang = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        except Exception:                                   # noqa: BLE001
            lang = "it"
    schede = schede_of(db, sito, [u.key for u in units])
    tipi = doc_types(db)
    nome = os.path.basename(str(emjson_path or "")) or "em.json"
    disegni, saltate = compute_drawings(graph, units, choice, georef, schede, source_name=nome,
                                        lang=lang, tipi=tipi, progress=progress)
    rilievi = {u.key: "; ".join(u.locators) for u in units}
    esito = write_drawings(db, sito, disegni, schede, decision, source_name=nome, rilievi=rilievi)
    esito.skipped.update(saltate)
    return esito
```

- [ ] **Step 5: Lanciare i test e vederli passare**

Run: `PYT tests/sync/test_em_drawings_import.py tests/sync/test_em_drawings_import_pg.py`
Expected: PASS (21 SQLite + 1 PG; il PG può restare SKIPPED, con il motivo nel ledger).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/em_drawings_import.py tests/sync/test_em_drawings_import.py tests/sync/test_em_drawings_import_pg.py
git commit -m "feat(3d): scrittura di piante, prospetti, documenti e coppie della scheda US — sostituisce solo il ricavato, SQLite e PostGIS"
```

---

### Task 8: la finestra e la scheda Import

**Files:**
- Create: `modules/s3dgraphy/em_drawings_dialog.py`
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py`. Casella e pulsante dopo `import_layout.addLayout(media_row)`, ~riga 531. Anteprima in `_on_import_preview`, prima di `self.btn_apply.setEnabled(True)`, ~riga 926. Applica in `_on_import_apply`, subito dopo `self.btn_apply.setEnabled(False)`, ~riga 936, e dopo il passo dei media, ~riga 1017. Metodi nuovi `_on_choose_geom_3d`, `_geom_plan` e `_import_drawings` accanto a `_import_media`.
- Test: `tests/sync/test_em_drawings_dialog.py`

**Interfaces:**
- Consumes: `DrawingUnit`, `Choice`, `status_text`, `default_choice`, `plan_units`, `crs_decision`, `preview_line`, `run_drawings`, `WriteResult.summary` (Task 5–7); `em_drawings.georef_of`.
- Produces: `DrawingsDialog(units, choice, georef, parent=None)` con `.choice() -> Choice`, `.table`, `.sp_z`, `.lb_quote`, `.cb_lati`; `position_text(georef) -> str`; `quote_text(units, shift_z) -> str`.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# tests/sync/test_em_drawings_dialog.py
"""La finestra «Geometrie dai modelli 3D» (spec 2026-10-18, D12)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
for p in (str(PLUGIN_ROOT / "ext_libs"), str(PLUGIN_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _unita():
    from modules.s3dgraphy.sync.em_drawings_import import DrawingUnit
    return [DrawingUnit("u1", "SU001", "US", ["proxies/SU001.glb"], ["/x/SU001.glb"], "ok",
                        triangles=12, ymin=-4.0, ymax=-2.0),
            DrawingUnit("u2", "SU002", "US", ["proxies/SU002.glb"], ["/x/SU002.glb"], "ok",
                        hand_plan=True, triangles=12, ymin=-3.0, ymax=1.5),
            DrawingUnit("u3", "USV103", "USVs", ["proxies/USV103.glb"], [], "missing")]


def _geo(usable=True):
    from modules.s3dgraphy.em_drawings import Georef
    return Georef("declared" if usable else "undeclared", 31700 if usable else None,
                  327300.0, 448370.0, 500.0, 0.0, metric=usable)


def test_la_finestra_mostra_unita_e_scelta():
    from modules.s3dgraphy.em_drawings_dialog import DrawingsDialog
    from modules.s3dgraphy.sync.em_drawings_import import default_choice
    unita, geo = _unita(), _geo()
    dlg = DrawingsDialog(unita, default_choice(unita, geo), geo)
    assert dlg.table.rowCount() == 3
    assert dlg.table.item(1, 4).text() == "ok; ha già una pianta a mano"
    assert dlg.table.item(2, 4).text() == "file non trovato"
    scelta = dlg.choice()
    assert scelta.plan == {"u1"} and scelta.prospect == {"u1", "u2"}
    assert scelta.sides == ("N", "E", "S", "W") and scelta.shift_z == pytest.approx(500.0)
    assert dlg.lb_quote.text() == "quote da 496,00 a 501,50 m"
    dlg.sp_z.setValue(0.0)
    assert dlg.lb_quote.text() == "quote da -4,00 a 1,50 m"
    dlg.cb_lati["W"].setChecked(False)
    assert dlg.choice().sides == ("N", "E", "S")


def test_senza_posizione_la_pianta_non_si_sceglie():
    from modules.s3dgraphy.em_drawings_dialog import DrawingsDialog, position_text
    from modules.s3dgraphy.sync.em_drawings_import import default_choice
    unita, geo = _unita(), _geo(False)
    dlg = DrawingsDialog(unita, default_choice(unita, geo), geo)
    assert dlg.choice().plan == set()
    assert "non dice dove sta la scena" in position_text(geo)
    assert position_text(_geo()) == ("Posizione (dall'em.json): EPSG:31700 · X +327300 · "
                                     "Y +448370 · rotazione 0°")
```

- [ ] **Step 2: Lanciare i test e vederli fallire**

Run: `PYT tests/sync/test_em_drawings_dialog.py`
Expected: FAIL con `ModuleNotFoundError: No module named 'modules.s3dgraphy.em_drawings_dialog'`.

- [ ] **Step 3: Scrivere la finestra**

```python
# modules/s3dgraphy/em_drawings_dialog.py
"""La finestra «Geometrie dai modelli 3D» dell'import em.json: quali unità
hanno pianta e prospetto, quali lati del sito, lo spostamento Z
(spec 2026-10-18-geometrie-dai-proxy-3d-design, D12)."""
from __future__ import annotations

from typing import List, Sequence

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QHBoxLayout,
                                 QHeaderView, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                                 QVBoxLayout)

from .sync.em_drawings_import import Choice, DrawingUnit, status_text

_LATI = (("N", "Nord"), ("E", "Est"), ("S", "Sud"), ("W", "Ovest"))


def _numero(x: float) -> str:
    return ("%.2f" % x).replace(".", ",")


def position_text(georef) -> str:
    if not georef.usable:
        return ("L'em.json non dice dove sta la scena: niente piante, solo prospetti "
                "con le quote locali.")
    return "Posizione (dall'em.json): EPSG:%d · X %+.0f · Y %+.0f · rotazione %.0f°" % (
        georef.epsg, georef.shift_x, georef.shift_y, georef.rotation)


def quote_text(units: Sequence[DrawingUnit], shift_z: float) -> str:
    basse = [u.ymin for u in units if u.usable and u.ymin is not None]
    alte = [u.ymax for u in units if u.usable and u.ymax is not None]
    if not basse:
        return ""
    return "quote da %s a %s m" % (_numero(min(basse) + shift_z), _numero(max(alte) + shift_z))


class DrawingsDialog(QDialog):
    def __init__(self, units: Sequence[DrawingUnit], choice: Choice, georef, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Geometrie dai modelli 3D")
        self.resize(720, 520)
        self._units: List[DrawingUnit] = list(units)
        self._georef = georef
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(position_text(georef)))
        riga = QHBoxLayout()
        riga.addWidget(QLabel("Spostamento Z:"))
        self.sp_z = QDoubleSpinBox()
        self.sp_z.setRange(-100000.0, 100000.0)
        self.sp_z.setDecimals(2)
        self.sp_z.setSuffix(" m")
        self.sp_z.setValue(georef.shift_z if choice.shift_z is None else float(choice.shift_z))
        self.lb_quote = QLabel()
        riga.addWidget(self.sp_z)
        riga.addWidget(self.lb_quote, 1)
        lay.addLayout(riga)
        self.sp_z.valueChanged.connect(self._aggiorna_quote)
        lati = QHBoxLayout()
        lati.addWidget(QLabel("Prospetti del sito:"))
        self.cb_lati = {}
        for codice, nome in _LATI:
            cb = QCheckBox(nome)
            cb.setChecked(codice in choice.sides)
            self.cb_lati[codice] = cb
            lati.addWidget(cb)
        lati.addStretch(1)
        lay.addLayout(lati)
        self.table = QTableWidget(len(self._units), 5)
        self.table.setHorizontalHeaderLabels(["Unità", "Tipo", "Pianta", "Prospetto", "Stato"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        for r, u in enumerate(self._units):
            for c, testo in ((0, u.name), (1, u.unit_type), (4, status_text(u))):
                it = QTableWidgetItem(testo)
                it.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(r, c, it)
            for c, scelte, possibile in ((2, choice.plan, u.usable and georef.usable),
                                         (3, choice.prospect, u.usable)):
                it = QTableWidgetItem()
                if possibile:
                    it.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                    it.setCheckState(Qt.CheckState.Checked if u.key in scelte else Qt.CheckState.Unchecked)
                else:
                    it.setFlags(Qt.ItemFlag.NoItemFlags)
                self.table.setItem(r, c, it)
        lay.addWidget(self.table, 1)
        tasti = QHBoxLayout()
        for testo, stato in (("Tutte", Qt.CheckState.Checked), ("Nessuna", Qt.CheckState.Unchecked)):
            b = QPushButton(testo)
            b.clicked.connect(lambda _x=False, s=stato: self._tutte(s))
            tasti.addWidget(b)
        tasti.addStretch(1)
        lay.addLayout(tasti)
        nota = QLabel("Le geometrie ricavate da un import precedente di questo sito vengono "
                      "sostituite; quelle disegnate a mano restano.")
        nota.setWordWrap(True)
        lay.addWidget(nota)
        bottoni = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bottoni.button(QDialogButtonBox.StandardButton.Ok).setText("Conferma")
        bottoni.button(QDialogButtonBox.StandardButton.Cancel).setText("Annulla")
        bottoni.accepted.connect(self.accept)
        bottoni.rejected.connect(self.reject)
        lay.addWidget(bottoni)
        self._aggiorna_quote()

    def _aggiorna_quote(self, *_):
        self.lb_quote.setText(quote_text(self._units, self.sp_z.value()))

    def _tutte(self, stato):
        for r in range(self.table.rowCount()):
            for c in (2, 3):
                it = self.table.item(r, c)
                if it.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                    it.setCheckState(stato)

    def _spuntate(self, colonna: int) -> set:
        return {u.key for r, u in enumerate(self._units)
                if self.table.item(r, colonna).flags() & Qt.ItemFlag.ItemIsUserCheckable
                and self.table.item(r, colonna).checkState() == Qt.CheckState.Checked}

    def choice(self) -> Choice:
        return Choice(plan=self._spuntate(2) if self._georef.usable else set(),
                      prospect=self._spuntate(3),
                      sides=tuple(c for c, _n in _LATI if self.cb_lati[c].isChecked()),
                      shift_z=float(self.sp_z.value()))
```

- [ ] **Step 4: Collegare la scheda Import**

In `s3dgraphy_dot_bridge.py`, dopo `import_layout.addLayout(media_row)`:

```python
            # Piante e prospetti ricavati dai proxy 3D (18 ottobre 2026,
            # spec 2026-10-18-geometrie-dai-proxy-3d-design): spenta di partenza.
            geo_row = QHBoxLayout()
            self.cb_geom_3d = QCheckBox("Ricava piante e prospetti dai modelli 3D")
            self.cb_geom_3d.setChecked(False)
            self.btn_geom_3d = QPushButton("Scegli…")
            self.btn_geom_3d.setEnabled(False)
            self.cb_geom_3d.toggled.connect(self.btn_geom_3d.setEnabled)
            self.btn_geom_3d.clicked.connect(self._on_choose_geom_3d)
            geo_row.addWidget(self.cb_geom_3d)
            geo_row.addWidget(self.btn_geom_3d)
            geo_row.addStretch(1)
            import_layout.addLayout(geo_row)
            self._geom_choice = None          # (percorso dell'em.json, sito, Choice)
```

Metodi nuovi, accanto a `_import_media`:

```python
        def _geom_plan(self, graph, source_path, target_sito):
            """(unità, scelta, posizione, decisione) per i disegni dal 3D, o
            None se la casella è spenta o il file non è un em.json."""
            if not self.cb_geom_3d.isChecked() or not str(source_path or "").lower().endswith(".json"):
                return None
            from modules.s3dgraphy import em_drawings as drw
            from modules.s3dgraphy.sync import em_drawings_import as edi
            altrove = self.le_media_dir.text().strip()
            unita = edi.plan_units(graph, source_path, search_dirs=[altrove] if altrove else [],
                                   db=self.db_manager, sito=target_sito)
            geo = drw.georef_of(graph)
            if self._geom_choice and self._geom_choice[:2] == (source_path, target_sito):
                scelta = self._geom_choice[2]
            else:
                scelta = edi.default_choice(unita, geo)
            return unita, scelta, geo, edi.crs_decision(self.db_manager, geo, scelta)

        def _on_choose_geom_3d(self):
            from modules.s3dgraphy.em_drawings_dialog import DrawingsDialog
            source_path = self.le_import_file.text().strip()
            target_sito = self.cb_sito.currentText().strip() or self.site
            if not source_path.lower().endswith(".json") or not os.path.exists(source_path):
                QMessageBox.warning(self, "Nessun em.json",
                                    "Scegli prima l'em.json: piante e prospetti si ricavano dai suoi proxy 3D.")
                return
            try:
                graph, _w = read_graph_for_import(source_path)
                piano = self._geom_plan(graph, source_path, target_sito)
            except Exception as e:                  # noqa: BLE001
                QMessageBox.critical(self, "Geometrie dai modelli 3D", "%s: %s" % (type(e).__name__, e))
                return
            unita, scelta, geo, _decisione = piano
            dlg = DrawingsDialog(unita, scelta, geo, self)
            if dlg.exec():
                self._geom_choice = (source_path, target_sito, dlg.choice())

        def _import_drawings(self, graph, target_sito, piano):
            from qgis.PyQt.QtCore import Qt
            from qgis.PyQt.QtWidgets import QApplication, QProgressDialog
            unita, scelta, geo, decisione = piano
            try:
                from modules.s3dgraphy.sync.em_drawings_import import run_drawings
                attesa = QProgressDialog("Piante e prospetti dai modelli 3D…", "", 0, 0, self)
                attesa.setCancelButton(None)
                attesa.setWindowTitle("Importa em.json")
                attesa.setWindowModality(Qt.WindowModality.WindowModal)
                attesa.setMinimumDuration(400)

                def avanza(fatti, totale, nome):
                    attesa.setMaximum(max(totale, 1))
                    attesa.setValue(fatti)
                    attesa.setLabelText("Modelli 3D: %d di %d\n%s" % (fatti, totale, nome))
                    QApplication.processEvents()

                try:
                    esito = run_drawings(self.db_manager, graph, target_sito, self._last_source_path,
                                         units=unita, choice=scelta, georef=geo, decision=decisione,
                                         progress=avanza)
                finally:
                    attesa.close()
                if hasattr(self.db_manager, "clear_cache"):
                    try:
                        self.db_manager.clear_cache()
                    except Exception:               # noqa: BLE001
                        pass
                return esito.summary(unita)
            except Exception as e:                  # noqa: BLE001
                return "Piante e prospetti dal 3D non fatti: %s" % e
```

In `_on_import_preview`, subito prima di `self.btn_apply.setEnabled(True)`:

```python
            piano = None
            try:
                piano = self._geom_plan(graph, source_path, target_sito)
            except Exception as e:                  # noqa: BLE001
                self.import_summary.setText(self.import_summary.text()
                                            + "\nPiante e prospetti dal 3D: %s" % e)
            if piano is not None:
                from modules.s3dgraphy.sync.em_drawings_import import preview_line
                unita, scelta, geo, decisione = piano
                self.import_summary.setText(self.import_summary.text() + "\n"
                                            + preview_line(unita, scelta, geo))
                if decisione.kind == "refuse":
                    self.import_summary.setText(self.import_summary.text() + "\n" + decisione.message)
                    QMessageBox.warning(self, "Sistema di riferimento", decisione.message)
                    return                          # Applica resta spento
```

In `_on_import_apply`, dopo `self.btn_apply.setEnabled(False)`, prima del `try:` che importa le schede:

```python
            piano = None
            target_sito_3d = self.cb_sito.currentText().strip() or self.site
            if self.cb_geom_3d.isChecked() and str(self._last_source_path or "").lower().endswith(".json"):
                try:
                    grafo_3d, _w = read_graph_for_import(self._last_source_path)
                    piano = self._geom_plan(grafo_3d, self._last_source_path, target_sito_3d)
                except Exception as e:              # noqa: BLE001
                    QMessageBox.critical(self, "Geometrie dai modelli 3D", "%s: %s" % (type(e).__name__, e))
                    return
                decisione = piano[3]
                if decisione.kind == "refuse":
                    QMessageBox.warning(self, "Sistema di riferimento", decisione.message)
                    return                          # nel DB non è entrato niente
                if decisione.kind == "convert":
                    box = QMessageBox(QMessageBox.Icon.Question, "Sistema di riferimento",
                                      decisione.message, parent=self)
                    converti = box.addButton("Converti", QMessageBox.ButtonRole.AcceptRole)
                    box.addButton("Annulla", QMessageBox.ButtonRole.RejectRole)
                    box.exec()
                    if box.clickedButton() is not converti:
                        return                      # nel DB non è entrato niente
```

e dopo il blocco dei media (`if self.cb_import_media.isChecked(): esito_media = self._import_media(...)`):

```python
            if piano is not None:
                testo_3d = self._import_drawings(graph, target_sito, piano)
                esito_media = (esito_media + "\n" if esito_media else "") + testo_3d
```

- [ ] **Step 5: Lanciare i test e vederli passare**

Run: `PYT tests/sync/test_em_drawings_dialog.py tests/sync/test_em_drawings_import.py`
Expected: PASS. Poi un controllo che la finestra Import si costruisca ancora:
Run: `PYT tests/sync -k "import_tab or dot_bridge or s3dgraphy_dot"`
Expected: PASS, oppure «no tests ran» se non c'è un test con quel nome: va scritto nel ledger.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/em_drawings_dialog.py modules/s3dgraphy/s3dgraphy_dot_bridge.py tests/sync/test_em_drawings_dialog.py
git commit -m "feat(3d): finestra «Geometrie dai modelli 3D» e casella nella scheda Import — anteprima, controllo del sistema prima di scrivere, disegni dopo i media"
```

---

### Task 9: verifica su TempluMare, documentazione e versione

**Files:**
- Create (scratch, non nel repo): `$SP/geo3d/verifica.py`, `$SP/geo3d/out/*.png`
- Modify: `docs/tutorials/it/36_*.md`, `docs/tutorials/en/36_*.md` (§5.0.2 nuovo), e le altre otto lingue (ar ca de el es fr pt ro) con gli agenti traduttori
- Modify: `dev_logs/CHANGELOG.md`, `metadata.txt` (`version=5.13.134-alpha`)

- [ ] **Step 1: Verifica su TempluMare (copie)**

Lo script `$SP/geo3d/verifica.py`, lanciato con il Python di QGIS:
1. copia `resources/dbfiles/pyarchinit.sqlite` in `$SP/geo3d/templu.sqlite` e porta i due layer a SRID 31700;
2. legge l'em.json da `$SP/scena3d/Temple.em.json`, con la cartella dei file `/Volumes/Extreme Pro/TempluMare_v2_for_3DR_2026-10-06/EM`, in sola lettura;
3. importa le schede (`GraphIngestor().populate_list`), poi `plan_units`, `default_choice`, `crs_decision` (deve dare `ok`) e `run_drawings`;
4. stampa il riepilogo;
5. rende con QGIS senza schermo (`QgsMapSettings`, `QgsMapRendererSequentialJob`) la vista US, e ognuno dei quattro prospetti filtrato per `nome_doc`, in PNG, che vanno guardati.

Expected:
- 65 piante, con le unità saltate elencate col motivo;
- il tempio, in pianta, nell'ingombro di circa 43 × 52 m attorno a X 327 280, Y 448 350;
- i prospetti affiancati, con le quote che dipendono dallo spostamento Z;
- la narrativa del sito, esportata da quel DB, con la scheda Mappa.

- [ ] **Step 2: Tutorial 36 §5.0.2 in italiano e inglese**

Una sezione nuova dopo §5.0.1, «Piante e prospetti dai modelli 3D», con: cosa fa la casella; la finestra «Geometrie dai modelli 3D»; la regola del sistema di riferimento (le tre righe); i nomi `3D-PLA`, `3D-PRO-N/E/S/W`, `3D-PRO-<tipo><us>`; dove si vedono (vista US, vista USM, scheda Documentazione, lista Documentazione della scheda US); cosa succede al reimport; il caso di TempluMare (lo spostamento Z di 500 m). Poi gli agenti traduttori portano la sezione nelle altre otto lingue, ognuno nella sua cartella e cercando il file per numero (36), con le etichette dei comandi lasciate in italiano, come sono nella finestra.

- [ ] **Step 3: CHANGELOG e versione**

Voce 5.13.134-alpha bilingue (IT + EN) in `dev_logs/CHANGELOG.md`, nello stile delle voci 5.13.131–133; `metadata.txt`: `version=5.13.134-alpha`.

- [ ] **Step 4: Suite intera**

Run: la suite intera (Global Constraints), poi `git checkout -- modules/geoarchaeo/test_layers/villa_ceramica.gpkg`.
Expected: 2439 + i test nuovi passati, 0 falliti.

- [ ] **Step 5: Commit**

```bash
git add docs/tutorials metadata.txt dev_logs/CHANGELOG.md
git commit -m "docs: tutorial 36 §5.0.2 — piante e prospetti dai modelli 3D in dieci lingue, changelog (5.13.134-alpha)"
```

---

## Dopo i task

Revisione finale di tutto il ramo, con un revisore nuovo sul modello più capace. Poi il fix pass, la suite, e il rilascio: tag `geometrie-3d-5.13.134-alpha`, push del ramo e del tag, pre-release su GitHub, voce nel CHANGELOG delle api-docs con push.
