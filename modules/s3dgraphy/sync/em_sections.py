"""Sezioni lungo le linee del layer delle sezioni, dai proxy 3D (spec
2026-10-18-sezioni-dai-proxy-3d-design, S1–S6).

Dopo l'import di un em.json: le linee di ``pyarchinit_sezioni`` del sito
tagliano i proxy delle unità (``em_drawings.section_line_geometry``) e ogni
linea diventa una sezione in ``pyunitastratigrafiche_usm``, in coordinate del
disegno (X lungo la linea dal suo primo punto, Y quota), a sinistra di
``u = 0`` dove i prospetti dell'import non arrivano. Ogni sezione è un
documento «Sezione» (``3D-SEZ-<id_sezione>``), legato ai poligoni, alla lista
Documentazione delle schede e, se è libera, alla linea. L'em.json è quello
ricordato all'import (``em_sources``); i proxy si cercano nelle cartelle date
e poi fra i media del database.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from .. import em_drawings as drw
from .. import glb_mesh as gm
from .em_drawings_import import (VERTICAL_LAYER, CrsDecision, Drawing, DrawingUnit, WriteResult,
                                 _engine, doc_type, layer_srid, plan_units, schede_of, status_text,
                                 unfilter_usm_view, write_drawings)

LINE_LAYER = "pyarchinit_sezioni"
OPEN_MODEL = "la sezione non si chiude (modello aperto)"
NO_PROXY = ("Nessuna unità del sito «%s» ha un modello 3D che si trovi: importa l'em.json con i media "
            "(«Extended Matrix → Importa em.json…»), o tieni collegato il disco dei proxy.")


def _is_section_name(nome) -> bool:
    return str(nome or "").startswith("3D-SEZ-") and drw.is_derived_name(nome)


class SectionsError(Exception):
    """Quello che manca per tagliare, detto a chi usa pyArchInit."""


@dataclass
class SectionLine:
    gid: int
    id_sezione: str
    descr: str
    area: str
    points: List[Tuple[float, float]]
    tipo_doc: str = ""
    nome_doc: str = ""

    @property
    def length(self) -> float:
        return drw.line_length(self.points)

    @property
    def segments(self) -> int:
        return max(len(self.points) - 1, 0)


@dataclass
class SectionsResult:
    written: WriteResult = field(default_factory=WriteResult)
    sections: int = 0
    cut: Dict[str, int] = field(default_factory=dict)
    empty: List[str] = field(default_factory=list)
    skipped: Dict[str, str] = field(default_factory=dict)
    linked: int = 0
    other_doc: List[str] = field(default_factory=list)
    raw_lines: bool = False
    epsg: Optional[int] = None

    def summary(self) -> str:
        if self.sections:
            testo = "Sezioni dal 3D: %d (%s)" % (self.sections, "; ".join(
                "%s: %d unità" % (n, k) for n, k in self.cut.items()))
        else:
            testo = "Sezioni dal 3D: nessuna scritta"
        if self.empty:
            testo += "; senza nessun profilo: %s" % ", ".join(self.empty)
        if self.skipped:
            testo += "; unità saltate: %s" % "; ".join("%s: %s" % kv for kv in sorted(self.skipped.items()))
        if self.linked:
            testo += "; %d linee collegate al loro documento" % self.linked
        if self.other_doc:
            testo += "; linee che hanno già un altro documento, lasciate com'erano: %s" % ", ".join(self.other_doc)
        if self.raw_lines:
            testo += ("; le linee di sezione non hanno un sistema di riferimento: le ho lette come "
                      "EPSG:%s dell'em.json" % self.epsg)
        if self.written.view_fixed:
            testo += ("; la vista USM del database mostrava solo le USM: ora mostra i disegni "
                      "verticali di tutte le unità")
        testo += "."
        if self.written.warnings:
            testo += "\nAvvisi: " + "; ".join(self.written.warnings[:5])
        return testo


# ------------------------------------------------------------------ le linee

def section_lines(db, sito: str) -> Tuple[List[SectionLine], Optional[int]]:
    """Le linee di sezione del sito, con i loro punti, e l'SRID del layer."""
    from qgis.core import QgsGeometry
    from sqlalchemy import text
    eng = _engine(db)
    testo = "ST_AsText" if eng.dialect.name.startswith("postgres") else "AsText"
    with eng.connect() as conn:
        srid = layer_srid(conn, LINE_LAYER)
        righe = conn.execute(text(
            "SELECT gid, id_sezione, descr, area, tipo_doc, nome_doc, %s(the_geom) FROM %s "
            "WHERE sito = :s ORDER BY gid" % (testo, LINE_LAYER)), {"s": sito}).fetchall()
    linee = []
    for gid, ids, descr, area, tipo, nome, wkt in righe:
        punti: List[Tuple[float, float]] = []
        if wkt:
            g = QgsGeometry.fromWkt(str(wkt))
            if not g.isEmpty():
                if g.isMultipart():
                    parti = g.asMultiPolyline()
                    punti = [(p.x(), p.y()) for p in parti[0]] if parti else []
                else:
                    punti = [(p.x(), p.y()) for p in g.asPolyline()]
        linee.append(SectionLine(int(gid), str(ids or "").strip(), str(descr or ""),
                                 "" if area is None else str(area), punti, str(tipo or ""), str(nome or "")))
    return linee, srid


def section_names(lines: Sequence[SectionLine]) -> Dict[int, str]:
    """``3D-SEZ-<id_sezione>``; senza id ``3D-SEZ-G<gid>``; ai doppi ``-<gid>``."""
    base = {}
    for linea in lines:
        nome = drw._safe(linea.id_sezione)
        base[linea.gid] = "3D-SEZ-" + (nome if nome else "G%d" % linea.gid)
    quanti = Counter(base.values())
    return {g: (n + "-%d" % g if quanti[n] > 1 else n) for g, n in base.items()}


def _lines_in(lines: Sequence[SectionLine], srid, epsg: int):
    """I punti delle linee nel sistema dell'em.json; True se il layer non ha un
    sistema e i punti si sono presi così come sono."""
    if drw.crs_kind(srid) == "undefined":
        return {l.gid: list(l.points) for l in lines}, True
    if int(srid) == int(epsg):
        return {l.gid: list(l.points) for l in lines}, False
    from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY,
                           QgsProject)
    ct = QgsCoordinateTransform(QgsCoordinateReferenceSystem.fromEpsgId(int(srid)),
                                QgsCoordinateReferenceSystem.fromEpsgId(int(epsg)), QgsProject.instance())
    out = {}
    for linea in lines:
        out[linea.gid] = [(p.x(), p.y()) for p in (ct.transform(QgsPointXY(x, y)) for x, y in linea.points)]
    return out, False


# ------------------------------------------------------------- em.json e unità

def load_graph(db, sito: str):
    """Il grafo dell'em.json ricordato all'import del sito, o None."""
    from .em_sources import load_source
    doc = load_source(db, sito)
    if not doc:
        return None
    from s3dgraphy.importer.emjson_importer import parse_emjson
    graph, _avvisi = parse_emjson(doc)
    return graph


def _source_name(db, sito: str) -> str:
    from sqlalchemy import select
    from .em_sources import TABLE
    try:
        with _engine(db).connect() as conn:
            riga = conn.execute(select(TABLE.c.source_name).where(TABLE.c.sito == str(sito))
                                .order_by(TABLE.c.id.desc())).first()
        return str(riga[0]) if riga and riga[0] else "em.json"
    except Exception:                                       # noqa: BLE001
        return "em.json"


def section_units(graph, db, sito: str, *, search_dirs: Sequence[str] = (),
                  resize_base: str = "") -> List[DrawingUnit]:
    """Le unità con un proxy: i file si cercano nelle cartelle date (come
    all'import) e, per quelle che lì non ci sono, fra i media del database."""
    unita = plan_units(graph, "", search_dirs=search_dirs, db=db, sito=sito)
    mancanti = [u for u in unita if u.status == "missing"]
    if not mancanti:
        return unita
    try:
        from ..em_project import media_file_for, media_index
        indice = media_index(_engine(db).url.render_as_string(hide_password=False), resize_base)
    except Exception:                                       # noqa: BLE001
        return unita
    for u in mancanti:
        percorsi = [media_file_for(loc, indice) for loc in u.locators]
        if not percorsi or not all(percorsi):
            continue
        info = [gm.glb_info(p) for p in percorsi]
        guasto = next((i for i in info if not i.ok), None)
        if guasto is not None:
            u.status, u.detail = guasto.reason, guasto.detail
            continue
        u.paths, u.status, u.detail = list(percorsi), "ok", ""
        u.triangles = sum(i.triangles for i in info)
        basse = [i.ymin for i in info if i.ymin is not None]
        alte = [i.ymax for i in info if i.ymax is not None]
        u.ymin, u.ymax = (min(basse), max(alte)) if basse else (None, None)
    return unita


# ------------------------------------------------------------------ il calcolo

_NOTE = {
    "it": ("Sezione {ids} lungo la linea «{descr}» ({tratti} tratti, {lung} m), dai proxy 3D di {src}: "
           "X = metri lungo la linea dal primo punto (a sinistra), Y = quota (spostamento Z {z} m)."),
    "en": ("Section {ids} along the line \"{descr}\" ({tratti} segments, {lung} m), from the 3D proxies "
           "of {src}: X = metres along the line from its first point (on the left), Y = elevation "
           "(Z shift {z} m)."),
}


def _min_u_kept(db, sito: str, scope: Set[str]) -> Optional[float]:
    """La u più a sinistra dei disegni ricavati del sito che restano."""
    from sqlalchemy import text
    eng = _engine(db)
    xmin = "ST_XMin" if eng.dialect.name.startswith("postgres") else "MbrMinX"
    nomi = sorted(scope)
    escludi = (" AND nome_doc NOT IN (%s)" % ", ".join(":n%d" % i for i in range(len(nomi)))) if nomi else ""
    try:
        with eng.connect() as conn:
            valore = conn.execute(text(
                "SELECT MIN(%s(the_geom)) FROM %s WHERE scavo_s = :s AND nome_doc LIKE '3D-%%'%s"
                % (xmin, VERTICAL_LAYER, escludi)),
                {"s": sito, **{"n%d" % i: n for i, n in enumerate(nomi)}}).scalar()
    except Exception:                                       # noqa: BLE001
        return None
    return float(valore) if valore is not None else None


def run_sections(db, sito: str, *, gids: Sequence[int], shift_z: Optional[float] = None,
                 search_dirs: Sequence[str] = (), resize_base: str = "", lang: Optional[str] = None,
                 progress: Optional[Callable[[int, int, str], None]] = None) -> SectionsResult:
    """Taglia i proxy del sito lungo le linee ``gids`` e scrive le sezioni."""
    from sqlalchemy import text
    graph = load_graph(db, sito)
    if graph is None:
        raise SectionsError(
            "Il sito «%s» non ha un em.json importato: importalo prima con «Extended Matrix → "
            "Importa em.json…», con i media, così pyArchInit ha i modelli 3D delle unità." % sito)
    georef = drw.georef_of(graph)
    if not georef.usable:
        raise SectionsError(
            "L'em.json del sito non dice dove sta la scena (EPSG e spostamenti): senza posizione "
            "le linee della mappa e i modelli 3D non si incontrano.")
    linee, srid_linee = section_lines(db, sito)
    voluti = {int(g) for g in gids}
    scelte = [l for l in linee if l.gid in voluti]
    if not scelte:
        raise SectionsError(
            "Non c'è nessuna linea di sezione da tagliare: tracciale nel layer delle sezioni "
            "(pyarchinit_sezioni) del sito «%s» e sceglile." % sito)
    with _engine(db).connect() as conn:
        usm_srid = layer_srid(conn, VERTICAL_LAYER)
    if drw.crs_kind(usm_srid) != "metric":
        raise SectionsError(
            "Il layer pyunitastratigrafiche_usm del database non è in un sistema metrico (SRID %s): "
            "i disegni verticali non ci possono stare. Ricrea il database in un sistema metrico." % usm_srid)
    if lang is None:
        try:
            from qgis.core import QgsSettings
            lang = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        except Exception:                                   # noqa: BLE001
            lang = "it"
    nota = _NOTE.get((lang or "it")[:2].lower(), _NOTE["en"])
    unita = section_units(graph, db, sito, search_dirs=search_dirs, resize_base=resize_base)
    usabili = [u for u in unita if u.usable]
    if not usabili:
        raise SectionsError(NO_PROXY % sito)
    schede = schede_of(db, sito, [u.key for u in usabili], graph=graph)
    nomi = section_names(linee)
    punti, grezze = _lines_in(scelte, srid_linee, int(georef.epsg))
    z = georef.shift_z if shift_z is None else float(shift_z)
    tipo = doc_type(db, "SEZ", "Sezione")
    sorgente = _source_name(db, sito)
    esito = SectionsResult(raw_lines=grezze, epsg=georef.epsg)
    for u in unita:
        if not u.usable and u.status != "heir":
            esito.skipped[u.name] = status_text(u)
    nome_di = {u.key: u.name for u in usabili}
    totale = len(usabili) + len(scelte) * max(len(usabili), 1)
    passi = [0]

    def avanti(nome: str) -> None:
        passi[0] += 1
        if progress:
            progress(min(passi[0], totale), totale, nome)

    mesh: Dict[str, np.ndarray] = {}
    for u in usabili:
        avanti(u.name)
        if u.key not in schede:
            esito.skipped[u.name] = "scheda non trovata"
            continue
        try:
            tri = np.concatenate([drw.scene_from_gltf(gm.read_triangles(p)) for p in u.paths])
        except gm.GlbError as e:
            esito.skipped[u.name] = str(e)
            continue
        mesh[u.key] = drw.place(graph, georef, tri.reshape(-1, 3), z).reshape(-1, 3, 3)
    disegni: List[Drawing] = []
    for linea in scelte:
        nome = nomi[linea.gid]
        pts = punti[linea.gid]
        if len(pts) < 2 or drw.line_length(pts) <= 1e-9:
            esito.empty.append(nome)
            continue
        figure = []
        for k, t in mesh.items():
            avanti("%s · %s" % (nome, k))
            g = drw.section_line_geometry(t, pts)
            if g is not None:
                figure.append((k, g))
            elif drw.section_crosses(t, pts):
                esito.skipped[nome_di.get(k, k)] = OPEN_MODEL
        if not figure:
            esito.empty.append(nome)
            continue
        disegni.append(Drawing(VERTICAL_LAYER, tipo, nome, nota.format(
            ids=linea.id_sezione or linea.gid, descr=linea.descr, tratti=linea.segments,
            lung=("%.2f" % drw.line_length(pts)), src=sorgente, z=z), figure))
        esito.cut[nome] = len(figure)
    if progress:
        progress(totale, totale, "")
    # Si rifanno tutte le linee scelte, anche quelle che ora non incontrano
    # niente (la sezione di prima se ne va), e i nomi ricavati che le linee
    # avevano prima, se nel frattempo il nome è cambiato (un id doppio, un id
    # corretto): la sezione col vecchio nome resterebbe orfana. Senza nessun
    # modello che si legga non si tocca niente.
    ambito: Set[str] = set()
    if mesh:
        attuali = set(nomi.values())
        ambito = {nomi[l.gid] for l in scelte}
        ambito |= {l.nome_doc for l in scelte if _is_section_name(l.nome_doc) and l.nome_doc not in attuali}
    if not ambito:
        return esito
    # a sinistra di u = 0 e di tutto quello che resta nel sito
    minimo = _min_u_kept(db, sito, ambito)
    cursore = min(0.0, minimo if minimo is not None else 0.0) - drw.GAP
    for d in disegni:
        lo = min(drw.span_u(g)[0] for _k, g in d.features)
        hi = max(drw.span_u(g)[1] for _k, g in d.features)
        d.features = [(k, drw.translated(g, cursore - hi)) for k, g in d.features]
        cursore -= (hi - lo) + drw.GAP
    rilievi = {u.key: "; ".join(u.locators) for u in unita}
    esito.written = write_drawings(db, sito, disegni, schede, CrsDecision("ok", usm_srid=usm_srid),
                                   source_name=sorgente, rilievi=rilievi, scope=ambito)
    esito.sections = esito.written.unit_views
    # La linea si lega al suo documento, se non ne ha già uno o se ha quello
    # di una sezione ricavata di prima; perde quello ricavato se non ne ha più.
    with _engine(db).begin() as conn:
        for linea in scelte:
            nome = nomi[linea.gid]
            nostra = (not linea.tipo_doc and not linea.nome_doc) or _is_section_name(linea.nome_doc)
            if nome not in esito.cut:
                if nostra and linea.nome_doc and linea.nome_doc in ambito:
                    conn.execute(text("UPDATE %s SET tipo_doc = NULL, nome_doc = NULL WHERE gid = :g"
                                      % LINE_LAYER), {"g": linea.gid})
                continue
            if (linea.tipo_doc, linea.nome_doc) == (tipo, nome):
                continue
            if nostra:
                conn.execute(text("UPDATE %s SET tipo_doc = :t, nome_doc = :n WHERE gid = :g" % LINE_LAYER),
                             {"t": tipo, "n": nome, "g": linea.gid})
                esito.linked += 1
            else:
                esito.other_doc.append("%s (%s %s)" % (linea.id_sezione or linea.gid,
                                                       linea.tipo_doc, linea.nome_doc))
    esito.written.view_fixed = unfilter_usm_view(db)
    return esito
