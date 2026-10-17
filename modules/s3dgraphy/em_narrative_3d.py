"""La scena 3D dei proxy nell'HTML della narrativa (Enzo, 17 ottobre 2026:
«assemblare insieme tutti i 3D come ad esempio per la mappa e quando nel
capitolo si fa riferimento a quello se ci clicco sopra … si evidenzia il
proxy interessato e gli altri sono in trasparenza»).

I proxy vengono dalla regola della libreria, la stessa di EMStudio
(``s3dgraphy.paradata_view.proxy_instances``: unità → proprietà «geometry» →
forma → risorsa ``proxy_model``; una proprietà ereditata si disegna una
volta, dal proprietario); i file dal database, come per il progetto EM
(:func:`em_project.media_index`, :func:`em_project.media_file_for`). Ogni GLB
di EMStudio porta già la sua posizione nella scena (il nodo con traslazione
e rotazione esportato da Blender): messi insieme si incastrano — TempluMare:
65 proxy, 2,4 MB, 43 × 14 × 52 m. La pagina li porta in base64 e li disegna
con three.js, che sta dentro la pagina (:data:`BUNDLE`, rifatto da
``scripts/build_three_bundle.sh``): niente rete.
"""
from __future__ import annotations

import base64
import html as _html
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_LOG = logging.getLogger(__name__)

#: un proxy più grande non entra nella pagina; né oltre il totale
MAX_PROXY_FILE = 15 * 1024 * 1024
MAX_PROXY_FILES = 40 * 1024 * 1024

#: three.js 0.186.1 con GLTFLoader e OrbitControls, in uno script classico (window.PYA_THREE)
BUNDLE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      "resources", "js", "pya_three_scene.min.js")


@dataclass
class SceneProxy:
    """Un file di proxy: la risorsa (``key``), l'unità che lo possiede, il
    locator dell'em.json e, trovato il file, dove sta e quanto pesa."""
    key: str
    unit: str
    locator: str
    path: str = ""
    size: int = 0


@dataclass
class Scene:
    proxies: List[SceneProxy] = field(default_factory=list)
    unit_proxies: Dict[str, List[str]] = field(default_factory=dict)
    names: Dict[str, str] = field(default_factory=dict)
    epochs: Dict[str, List[str]] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def _locatore(nodo) -> str:
    """Il primo indirizzo locale del file della risorsa: l'url, o uno degli
    indirizzi alternativi (``data.addresses``)."""
    dati = getattr(nodo, "data", None) or {}
    candidati = [getattr(nodo, "url", None), dati.get("url")]
    candidati += [a.get("locator") for a in dati.get("addresses") or [] if isinstance(a, dict)]
    for c in candidati:
        c = str(c or "").strip()
        if c and "://" not in c:
            return c
    return ""


def scene_proxies(graph) -> Scene:
    """I proxy dal grafo, senza file: uno per risorsa col suo proprietario,
    e per ogni unità le chiavi dei suoi proxy — anche per chi ha la stessa
    proprietà «geometry» senza esserne il proprietario (la USV che eredita
    la geometria della US che completa)."""
    from s3dgraphy.paradata_view import proxy_instances
    from .em_narrative_map import epochs_of
    scena = Scene()
    epoche = epochs_of(graph)
    eredi: Dict[str, List[str]] = {}
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) == "has_property":
            eredi.setdefault(str(e.edge_target), []).append(str(e.edge_source))
    visti = set()
    for ist in proxy_instances(graph):
        if ist.get("removed") or not ist.get("files"):
            continue
        proprietario = str(ist["owner"])
        chiavi = []
        for rid in ist["files"]:
            rid = str(rid)
            loc = _locatore(graph.find_node_by_id(rid))
            if not loc:
                continue
            if rid not in visti:
                visti.add(rid)
                scena.proxies.append(SceneProxy(key=rid, unit=proprietario, locator=loc))
            chiavi.append(rid)
        if not chiavi:
            continue
        for u in [proprietario] + [x for x in eredi.get(str(ist.get("beside")), []) if x != proprietario]:
            lista = scena.unit_proxies.setdefault(u, [])
            lista.extend(k for k in chiavi if k not in lista)
            nodo = graph.find_node_by_id(u)
            scena.names[u] = str(getattr(nodo, "name", "") or u)
            scena.epochs[u] = list(epoche.get(u, []))
    return scena


def build_scene(graph, connection_url: str, resize_base: str = "", *,
                max_file: int = MAX_PROXY_FILE, budget: int = MAX_PROXY_FILES) -> Scene:
    """:func:`scene_proxies` con i file dal database (come il progetto EM) e
    i limiti: i più piccoli entrano per primi finché ci stanno, quelli
    rimasti fuori si contano. Un'unità senza più proxy resta col suo nome."""
    from .em_project import media_file_for, media_index
    scena = scene_proxies(graph)
    if not scena.proxies:
        return scena
    indice = media_index(connection_url, resize_base or "")
    trovati = []
    for p in scena.proxies:
        percorso = media_file_for(p.locator, indice)
        if percorso is None:
            scena.missing.append(p.locator)
            continue
        p.path, p.size = percorso, os.path.getsize(percorso)
        trovati.append(p)
    dentro, totale = set(), 0
    for p in sorted(trovati, key=lambda x: x.size):
        if p.size > max_file or totale + p.size > budget:
            scena.skipped.append(os.path.basename(p.locator))
            continue
        dentro.add(p.key)
        totale += p.size
    scena.proxies = [p for p in trovati if p.key in dentro]
    tenute = {u: [k for k in ks if k in dentro] for u, ks in scena.unit_proxies.items()}
    scena.unit_proxies = {u: ks for u, ks in tenute.items() if ks}
    return scena
