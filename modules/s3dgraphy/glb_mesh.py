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
