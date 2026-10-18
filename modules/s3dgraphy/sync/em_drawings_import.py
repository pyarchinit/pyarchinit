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
import re
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
        _mark_hand_drawn(db, sito, unita, graph=graph)
    return unita


def schede_of(db, sito: str, keys: Iterable[str], graph=None) -> Dict[str, Scheda]:
    """Le schede del sito delle unità date, per ``node_uuid``. Con il grafo,
    quelle che non si trovano così (l'em.json importato in un secondo sito: le
    schede copiate hanno un uuid nuovo) si cercano per numero e tipo, come fa
    l'import dei media."""
    from sqlalchemy import text
    voluti = {str(k) for k in keys}
    out: Dict[str, Scheda] = {}
    per_nome: Dict[Tuple[str, str], List[Scheda]] = {}
    with _engine(db).connect() as conn:
        for id_us, area, us, ut, doc, uuid in conn.execute(text(
                "SELECT id_us, area, us, unita_tipo, documentazione, node_uuid "
                "FROM us_table WHERE sito = :s"), {"s": sito}):
            s = Scheda(int(id_us), str(area if area is not None else "1"), str(us), str(ut or ""), doc)
            per_nome.setdefault((s.us, s.unita_tipo), []).append(s)
            if uuid is not None and str(uuid) in voluti:
                out[str(uuid)] = s
    mancanti = voluti - set(out)
    if mancanti and graph is not None:
        from . import em_native_import as emn
        from .graph_ingestor import _NON_STRAT_TYPES, _PARADATA_ROW_TYPES, _is_synthetic_node
        righe = emn.row_nodes(graph, _NON_STRAT_TYPES - _PARADATA_ROW_TYPES, _is_synthetic_node)
        nomi = emn.row_names(righe, getattr(graph, "edges", None) or [])
        for k in mancanti:
            if k not in righe or not nomi.get(k):
                continue
            candidate = per_nome.get((str(nomi[k]), str(righe[k][1] or "")), [])
            if len(candidate) == 1:
                out[k] = candidate[0]
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


def _mark_hand_drawn(db, sito: str, unita: List[DrawingUnit], graph=None) -> None:
    schede = schede_of(db, sito, [u.key for u in unita], graph=graph)
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
    lati_scelti = [x for x in choice.sides if x in drw.SITE_VIEWS]
    totale = len(voluti) * (2 + len(lati_scelti)) + len([k for k in voluti if k in choice.prospect])
    passi = [0]

    def avanti(nome: str) -> None:
        passi[0] += 1
        if progress:
            progress(min(passi[0], totale), totale, nome)

    for k in voluti:
        u = per_chiave.get(k)
        avanti(u.name if u else k)
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
    disegni: List[Drawing] = []
    if not mesh:
        if progress:
            progress(totale, totale, "")
        return disegni, saltate
    piante = {}
    for k in voluti:
        if k in mesh:
            avanti(per_chiave[k].name)
            piante[k] = drw.plan_geometry(mesh[k])
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
        for k in voluti:
            if k not in mesh:
                continue
            t = mesh[k]
            avanti("%s · %s" % (lati[lato], per_chiave[k].name))
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
        avanti(nomi[k])
        vista = drw.unit_view(nomi[k], piante.get(k), drw.centroid_xy(mesh[k]), centro,
                              xy=mesh[k][..., :2])
        g = drw.view_geometry(mesh[k], vista, origine)
        if g is None:
            saltate[k] = (saltate[k] + "; " if k in saltate else "") + "vuoto nel prospetto"
            continue
        verticali.append(Drawing(VERTICAL_LAYER, tipi[1], nomi[k], note["unit"].format(
            unita=per_chiave[k].name, da=vista.side, src=source_name, z=z), [(k, g)]))
    if progress:
        progress(totale, totale, "")
    verticali = [d for d in verticali if d.features]
    campate = [(min(drw.span_u(g)[0] for _k, g in d.features),
                max(drw.span_u(g)[1] for _k, g in d.features)) for d in verticali]
    for d, du in zip(verticali, drw.lay_out(campate)):
        d.features = [(k, drw.translated(g, du)) for k, g in d.features]
    return disegni + verticali, saltate


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
    view_fixed: bool = False

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
        if self.view_fixed:
            testo += ("; la vista USM del database mostrava solo le USM: ora mostra i "
                      "disegni verticali di tutte le unità")
        testo += "."
        if self.warnings:
            testo += "\nAvvisi: " + "; ".join(self.warnings[:5])
        return testo


def doc_type(db, sigla: str, ripiego: str, lingua: Optional[str] = None) -> str:
    """Il tipo di documento della sigla dal thesaurus (9.1) nella lingua del
    plugin, poi IT, poi ``ripiego``."""
    from sqlalchemy import text
    from .em_native_import import thesaurus_lingua
    lingua = lingua or thesaurus_lingua()
    try:
        with _engine(db).connect() as conn:
            for lng in (lingua, "IT"):
                estesa = conn.execute(text(
                    "SELECT sigla_estesa FROM pyarchinit_thesaurus_sigle WHERE "
                    "nome_tabella = 'documentazione_table' AND tipologia_sigla = '9.1' "
                    "AND lingua = :l AND sigla = :g"), {"l": lng, "g": sigla}).scalar()
                if estesa:
                    return str(estesa)
    except Exception:                                       # noqa: BLE001
        pass
    return ripiego


def doc_types(db, lingua: Optional[str] = None) -> Tuple[str, str]:
    """I tipi della pianta e dei prospetti (9.1 PLA e PRO)."""
    return doc_type(db, "PLA", "Planimetria", lingua), doc_type(db, "PRO", "Prospetto", lingua)


def _columns(eng, table: str) -> Set[str]:
    from sqlalchemy import inspect
    try:
        return {c["name"] for c in inspect(eng).get_columns(table)}
    except Exception:                                       # noqa: BLE001
        return set()


def _auto_id(conn, table: str, column: str) -> bool:
    """La colonna si riempie da sé: un DEFAULT su PostgreSQL (nello schema del
    plugin ``nextval`` di una sequenza che NON è OWNED BY la colonna, quindi
    ``pg_get_serial_sequence`` non la vede), INTEGER PRIMARY KEY su SQLite."""
    from sqlalchemy import text
    try:
        if conn.dialect.name.startswith("postgres"):
            # la tabella che il nome trova davvero (search_path), col suo
            # DEFAULT o la sua identity
            return bool(conn.execute(text(
                "SELECT (d.adbin IS NOT NULL) OR (a.attidentity <> '') FROM pg_attribute a "
                "LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum "
                "WHERE a.attrelid = to_regclass(:t) AND a.attname = :c AND NOT a.attisdropped"),
                {"t": table, "c": column}).scalar())
        for riga in conn.execute(text('PRAGMA table_info("%s")' % table)):
            if str(riga[1]) == column:
                return bool(riga[5]) and str(riga[2] or "").upper() == "INTEGER"
    except Exception:                                       # noqa: BLE001
        return False
    return False


def _centroid(g) -> str:
    c = g.centroid().asPoint()
    return "POINT(%.6f %.6f)" % (c.x(), c.y())


def write_drawings(db, sito: str, drawings: Sequence[Drawing], schede: Dict[str, Scheda],
                   decision: CrsDecision, *, source_name: str, today: Optional[str] = None,
                   rilievi: Optional[Dict[str, str]] = None,
                   scope: Optional[Set[str]] = None) -> WriteResult:
    """Sostituisce l'insieme ricavato del sito: poligoni nei due layer,
    documenti, coppie della scheda US. Una transazione; un SAVEPOINT per riga.
    ``scope`` None = piante e prospetti (``3D-PLA``, ``3D-PRO-…``), che l'import
    rifà tutti; un insieme = solo quei nomi (le sezioni che si ricalcolano)."""
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
    if scope is None:
        filtro, parametri = "(nome_doc = :pla OR nome_doc LIKE :pro)", {"pla": drw.PLAN_NAME, "pro": "3D-PRO-%"}

        def nell_ambito(nome) -> bool:
            return nome == drw.PLAN_NAME or str(nome or "").startswith("3D-PRO-")
    else:
        nomi = sorted(scope)
        filtro = ("nome_doc IN (%s)" % ", ".join(":n%d" % i for i in range(len(nomi)))) if nomi else "1 = 0"
        parametri = {"n%d" % i: n for i, n in enumerate(nomi)}

        def nell_ambito(nome) -> bool:
            return nome in scope
    with eng.begin() as conn:
        for layer in (PLAN_LAYER, VERTICAL_LAYER):
            if not colonne[layer]:
                continue
            r = conn.execute(text("DELETE FROM %s WHERE scavo_s = :s AND disegnatore = :d AND %s"
                                  % (layer, filtro)), {"s": sito, "d": drw.DRAWER, **parametri})
            esito.removed += max(r.rowcount or 0, 0)
        gid = {l: int(conn.execute(text("SELECT COALESCE(MAX(gid), 0) FROM %s" % l)).scalar() or 0)
               for l in (PLAN_LAYER, VERTICAL_LAYER) if colonne[l]}
        # Gli id che il database assegna da sé (la sequenza dello schema del
        # plugin su PostgreSQL) non si scrivono: il primo poligono disegnato poi
        # in QGIS prenderebbe un gid già usato.
        gid_da_se = {l: _auto_id(conn, l, "gid") for l in gid}
        doc_da_se = _auto_id(conn, "documentazione_table", "id_documentazione")
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
                valori = {"gid": None if gid_da_se[d.layer] else gid[d.layer], "area_s": s.area, "scavo_s": sito, "us_s": s.us,
                          "stratigraph_index_us": 1, "rilievo_originale": (rilievi or {}).get(k, ""),
                          "disegnatore": drw.DRAWER, "data": oggi, "tipo_doc": d.tipo,
                          "nome_doc": d.nome, "coord": _centroid(g), "unita_tipo_s": s.unita_tipo}
                usate = [c for c in valori if c in colonne[d.layer] and valori[c] is not None]
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
                valori_doc = {"s": sito, "n": d.nome, "dt": oggi, "t": d.tipo, "src": sorgente,
                              "d": drw.DRAWER, "note": d.note}
                if doc_da_se:
                    conn.execute(text(
                        "INSERT INTO documentazione_table (sito, nome_doc, data, tipo_documentazione, "
                        "sorgente, scala, disegnatore, note) VALUES (:s, :n, :dt, :t, :src, '', :d, :note)"),
                        valori_doc)
                else:
                    valori_doc["i"] = int(conn.execute(text(
                        "SELECT COALESCE(MAX(id_documentazione), 0) + 1 FROM documentazione_table")).scalar())
                    conn.execute(text(
                        "INSERT INTO documentazione_table (id_documentazione, sito, nome_doc, data, "
                        "tipo_documentazione, sorgente, scala, disegnatore, note) VALUES "
                        "(:i, :s, :n, :dt, :t, :src, '', :d, :note)"), valori_doc)
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
            if (tipo, nome) in ora or not nell_ambito(nome):
                continue
            citato = any(conn.execute(text(
                "SELECT 1 FROM %s WHERE scavo_s = :s AND tipo_doc = :t AND nome_doc = :n LIMIT 1" % l),
                {"s": sito, "t": tipo, "n": nome}).fetchone() for l in (PLAN_LAYER, VERTICAL_LAYER)
                if colonne[l])
            if not citato:
                conn.execute(text("DELETE FROM documentazione_table WHERE id_documentazione = :i"), {"i": i})
                esito.documents_removed += 1
        # Le coppie della scheda US: da tutti i poligoni con un nome ricavato che
        # ci sono adesso, anche quelli corretti a mano (disegnatore cambiato),
        # così la scheda continua a richiamarli.
        chiavi: Dict[Tuple[str, str, str], int] = {}
        per_area_us: Dict[Tuple[str, str], int] = {}
        for id_us, area, us, ut in conn.execute(text(
                "SELECT id_us, area, us, unita_tipo FROM us_table WHERE sito = :s"), {"s": sito}):
            chiavi.setdefault((str(area), str(us), str(ut or "")), int(id_us))
            per_area_us.setdefault((str(area), str(us)), int(id_us))
        coppie: Dict[int, List[List[str]]] = {}
        for layer in (PLAN_LAYER, VERTICAL_LAYER):
            if not colonne[layer]:
                continue
            tipo_col = "unita_tipo_s" if "unita_tipo_s" in colonne[layer] else "''"
            for area, us, ut, tipo, nome in conn.execute(text(
                    "SELECT area_s, us_s, %s, tipo_doc, nome_doc FROM %s WHERE scavo_s = :s "
                    "AND nome_doc LIKE '3D-%%' ORDER BY gid" % (tipo_col, layer)), {"s": sito}):
                if not tipo or not drw.is_derived_name(nome):
                    continue
                i = chiavi.get((str(area), str(us), str(ut or ""))) or per_area_us.get((str(area), str(us)))
                if i is None:
                    continue
                lista = coppie.setdefault(i, [])
                if [str(tipo), str(nome)] not in lista:
                    lista.append([str(tipo), str(nome)])
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
        if is_pg:
            # Gli id sono scritti espliciti (MAX + 1): la sequenza va rimessa
            # in pari, o il primo poligono disegnato in QGIS prenderebbe un
            # gid già usato.
            for tabella, chiave in ((PLAN_LAYER, "gid"), (VERTICAL_LAYER, "gid"),
                                    ("documentazione_table", "id_documentazione")):
                try:
                    with conn.begin_nested():
                        conn.execute(text(
                            "SELECT setval(pg_get_serial_sequence(:t, :c), "
                            "(SELECT COALESCE(MAX(%s), 0) + 1 FROM %s), false)" % (chiave, tabella)),
                            {"t": tabella, "c": chiave})
                except Exception:                           # noqa: BLE001
                    pass
    return esito


_USM_FILTER = re.compile(r"where\s+(\"?us_table\"?\.)?\"?unita_tipo\"?\s*=\s*'USM'", re.I)


def unfilter_usm_view(db) -> bool:
    """Il template SQLite (``resources/dbfiles/pyarchinit.sqlite``, da cui
    nasce ogni DB nuovo) ha una ``pyarchinit_usm_view`` che mostra solo le
    unità di tipo USM: i disegni verticali delle US non comparirebbero fra le
    «US verticali» della scheda Documentazione. La si riporta alla definizione
    canonica di pyArchInit (``spatial_view_definitions``), che è anche quella di
    PostgreSQL. Solo SQLite, solo con quel filtro; se la vista canonica non si
    legge su questo DB, resta quella di prima. True se l'ha cambiata."""
    from sqlalchemy import text
    eng = _engine(db)
    if eng.dialect.name != "sqlite":
        return False
    from ...db.spatial_view_definitions import CANONICAL_VIEWS
    canonica = CANONICAL_VIEWS.get("pyarchinit_usm_view")
    if not canonica:
        return False
    try:
        with eng.connect() as conn:
            vecchia = conn.execute(text("SELECT sql FROM sqlite_master WHERE type = 'view' "
                                        "AND name = 'pyarchinit_usm_view'")).scalar()
    except Exception:                                       # noqa: BLE001
        return False
    if not vecchia or not _USM_FILTER.search(str(vecchia)):
        return False
    # Prima la prova, in una vista temporanea: SQLite crea una vista anche con
    # colonne che non ci sono, e se ne accorge solo quando la si legge.
    prova = re.sub(r'(?is)^\s*CREATE\s+VIEW\s+"?pyarchinit_usm_view"?\s+AS\b',
                   'CREATE TEMP VIEW "pya_prova_usm_view" AS', canonica, count=1)
    if prova == canonica:
        return False
    try:
        with eng.begin() as conn:
            try:
                conn.execute(text(prova))
                conn.execute(text('SELECT 1 FROM temp."pya_prova_usm_view" LIMIT 1')).fetchall()
            finally:
                conn.execute(text('DROP VIEW IF EXISTS temp."pya_prova_usm_view"'))
    except Exception:                                       # noqa: BLE001
        return False
    try:
        with eng.begin() as conn:
            conn.execute(text('DROP VIEW "pyarchinit_usm_view"'))
            conn.execute(text(canonica))
            conn.execute(text('SELECT 1 FROM "pyarchinit_usm_view" LIMIT 1')).fetchall()
    except Exception:                                       # noqa: BLE001
        # Il DDL di SQLite qui non torna indietro da solo: si rimette la vista di prima.
        try:
            with eng.begin() as conn:
                conn.execute(text('DROP VIEW IF EXISTS "pyarchinit_usm_view"'))
                conn.execute(text(vecchia))
        except Exception:                                   # noqa: BLE001
            pass
        return False
    return True


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
    schede = schede_of(db, sito, [u.key for u in units], graph=graph)
    tipi = doc_types(db)
    nome = os.path.basename(str(emjson_path or "")) or "em.json"
    disegni, saltate = compute_drawings(graph, units, choice, georef, schede, source_name=nome,
                                        lang=lang, tipi=tipi, progress=progress)
    rilievi = {u.key: "; ".join(u.locators) for u in units}
    if not any(d.features for d in disegni):
        # Per esempio il disco dei proxy staccato: niente da scrivere, e i
        # disegni ricavati la volta prima non si cancellano.
        esito = WriteResult()
        esito.skipped.update(saltate)
        esito.warnings.append("nessun disegno da scrivere: i disegni ricavati di prima restano")
        return esito
    esito = write_drawings(db, sito, disegni, schede, decision, source_name=nome, rilievi=rilievi)
    esito.skipped.update(saltate)
    if esito.side_views or esito.unit_views:
        esito.view_fixed = unfilter_usm_view(db)
    return esito
