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
