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
