"""I file che un em.json di EMStudio cita diventano media di pyArchInit,
registrati come quelli caricati dalla scheda (Enzo, 16 ottobre 2026: «non
trova i media»; i media sono anche 3D, pdf, excel, word, txt e csv; «fai
gestire anche i glb»).

Da ogni scheda importata si seguono i legami del grafo verso i file:

* scheda —has_linked_resource→ risorsa (—has_file→ file);
* scheda —has_representation_model / has_semantic_shape→ modello —
  has_linked_resource→ risorsa —has_file→ file;
* l'``url`` della scheda stessa (il PDF di un documento, l'immagine di un
  estrattore).

Il proxy di un'unità, nel grafo, sta sulla sua proprietà «geometry»
(unità —has_property→ geometry —has_semantic_shape→ forma → proxies/SU002.glb):
quello che si trova partendo da una proprietà va all'unità che la possiede,
dove la scheda e il pannello della matrice lo cercano.

I file si cercano come li cerca EMStudio, con il risolutore della libreria
(``s3dgraphy.resources.locate``): l'albero di un progetto EM (``EM/``,
``EM/DosCo``, ``EM/proxies``, ``RB``, ``RM``, ``SB``) attorno all'em.json e
alle cartelle indicate da chi importa. Un file che è lì ma con i byte a zero
(un segnaposto del cloud) si dice, non si importa.

Il media punta al file ORIGINALE, come quelli della scheda; la miniatura e la
copia vanno nelle cartelle di pyArchInit (``media_preview``). Prima si
copiava tutto nella radice di ``pyarchinit_5`` e i .glb restavano senza
miniatura, quindi invisibili nella scheda.
"""
from __future__ import annotations

import os
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from ...utility.media_kinds import media_type_of, split_media_name

#: i legami che portano da una scheda ai suoi file
_VERSO_I_FILE = frozenset({
    "has_linked_resource", "has_file", "has_representation_model",
    "has_semantic_shape",
})

#: i nodi che portano un file
_NODI_FILE = frozenset({"resource", "resource_file"})

#: per tipo di media, come si dice nel riepilogo
_NOMI_TIPI = {"3d_model": "3D", "document": "documenti", "image": "immagini",
              "video": "video"}


@dataclass
class EmMediaResult:
    inserted: int = 0
    linked: int = 0
    already_present: int = 0
    thumbnails: int = 0
    #: i file citati che non ci sono da nessuna parte (il locatore)
    missing: List[str] = field(default_factory=list)
    #: i file che ci sono ma con i byte a zero (segnaposti del cloud)
    empty_copies: List[str] = field(default_factory=list)
    #: indirizzi web, di rete o del cloud: restano indirizzi
    references: int = 0
    #: i file citati che non sono media (blend, mtl…), per estensione
    skipped_types: Dict[str, int] = field(default_factory=dict)
    #: i media nuovi per tipo
    by_type: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        tipi = ", ".join("%s %d" % (_NOMI_TIPI.get(k, k), v)
                         for k, v in sorted(self.by_type.items(), key=lambda kv: -kv[1]))
        parti = ["%d media nuovi%s, %d collegamenti, %d già presenti"
                 % (self.inserted, " (%s)" % tipi if tipi else "", self.linked,
                    self.already_present)]
        if self.thumbnails:
            parti.append("%d miniature" % self.thumbnails)
        if self.missing:
            parti.append("%d file citati non trovati (%s): se il progetto di EMStudio "
                         "sta in un'altra cartella, indicala in «Cartella dei file» e "
                         "importa di nuovo" % (len(self.missing), _esempi(self.missing)))
        if self.empty_copies:
            parti.append("%d copie vuote, segnaposti del cloud da scaricare di nuovo (%s)"
                         % (len(self.empty_copies), _esempi(self.empty_copies)))
        if self.references:
            parti.append("%d riferimenti esterni (web, rete, cloud) lasciati come indirizzi"
                         % self.references)
        if self.skipped_types:
            parti.append("non sono media: " + ", ".join(
                "%s %d" % (k, v) for k, v in sorted(self.skipped_types.items())))
        return "; ".join(parti) + "."


def _per_file(locatori: Sequence[str]) -> List[str]:
    """I locatori, uno per nome di file (il primo che lo cita)."""
    visti, out = set(), []
    for loc in locatori:
        chiave = os.path.basename(str(loc).replace("\\", "/").rstrip("/")).lower()
        if chiave not in visti:
            visti.add(chiave)
            out.append(loc)
    return out


def _esempi(elenco: Sequence[str], quanti: int = 3) -> str:
    nomi = [os.path.basename(str(p).rstrip("/")) or str(p) for p in elenco[:quanti]]
    return ", ".join(nomi) + ("…" if len(elenco) > quanti else "")


# ----------------------------------------------------------- dal grafo

def _locatore(node) -> Optional[str]:
    """L'url di un nodo, com'è scritto."""
    if node is None:
        return None
    dati = getattr(node, "data", None)
    attributi = getattr(node, "attributes", None)
    for valore in (getattr(node, "url", None),
                   dati.get("url") if isinstance(dati, dict) else None,
                   attributi.get("url") if isinstance(attributi, dict) else None):
        if valore and isinstance(valore, str) and valore.strip():
            return valore.strip()
    return None


def _checksum(node) -> str:
    dati = getattr(node, "data", None)
    return str(dati.get("checksum") or "") if isinstance(dati, dict) else ""


def owners_of_properties(graph, rows: Dict[str, Tuple[Any, str]]) -> Dict[str, str]:
    """``{id della proprietà: id della scheda che la possiede}``."""
    out: Dict[str, str] = {}
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) != "has_property":
            continue
        src, tgt = str(e.edge_source), str(e.edge_target)
        if src in rows and tgt in rows and rows[tgt][1] == "property":
            out.setdefault(tgt, src)
    return out


def collect_files(graph, rows: Dict[str, Tuple[Any, str]]) -> Dict[str, List[Dict[str, str]]]:
    """``{id della scheda: [{id, locator, checksum}]}``: i file raggiungibili
    da ogni scheda attraverso risorse e modelli (al massimo tre passi, senza
    attraversare altre schede). Quelli di una proprietà vanno all'unità che
    la possiede."""
    per_id = {str(n.node_id): n for n in getattr(graph, "nodes", None) or []}
    uscite: Dict[str, List[str]] = defaultdict(list)
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) in _VERSO_I_FILE:
            uscite[str(e.edge_source)].append(str(e.edge_target))
    proprietari = owners_of_properties(graph, rows)
    out: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for nid, (nodo, _ut) in rows.items():
        trovati = []
        proprio = _locatore(nodo)
        if proprio:
            trovati.append({"id": nid, "locator": proprio, "checksum": _checksum(nodo)})
        visti, frontiera = {nid}, [nid]
        for _passo in range(3):
            prossimi = []
            for corrente in frontiera:
                for dopo in uscite.get(corrente, []):
                    if dopo in visti or dopo in rows:
                        continue
                    visti.add(dopo)
                    prossimi.append(dopo)
                    nodo_file = per_id.get(dopo)
                    if getattr(nodo_file, "node_type", None) in _NODI_FILE:
                        loc = _locatore(nodo_file)
                        if loc:
                            trovati.append({"id": dopo, "locator": loc,
                                            "checksum": _checksum(nodo_file)})
            frontiera = prossimi
        if trovati:
            out[proprietari.get(nid, nid)].extend(trovati)
    return {k: list({t["locator"]: t for t in v}.values()) for k, v in out.items()}


def search_dirs_for(emjson_path: str, extra: Sequence[str] = ()) -> List[str]:
    """Le cartelle in cui cercare: quella dell'em.json e quelle indicate,
    ognuna con il suo ``DosCo`` e i suoi ``proxies``, e l'albero standard
    del progetto EM a cui appartengono (se ce n'è uno)."""
    from s3dgraphy.project_tree import find_project_root, search_bases
    basi: List[str] = []
    partenze = [os.path.dirname(os.path.abspath(str(emjson_path)))] if emjson_path else []
    partenze += [str(d) for d in extra or () if d]
    for d in partenze:
        d = os.path.abspath(os.path.expanduser(d))
        basi += [d, os.path.join(d, "DosCo"), os.path.join(d, "proxies")]
        radice = find_project_root(d)
        if radice:
            basi += search_bases(radice)
    visti, out = set(), []
    for b in basi:
        if b not in visti and os.path.isdir(b):
            visti.add(b)
            out.append(b)
    return out


# ----------------------------------------------------------- nel database

def _engine(db):
    from sqlalchemy import create_engine
    if hasattr(db, "engine"):
        return db.engine
    if isinstance(db, Path) or (isinstance(db, str) and "://" not in db):
        return create_engine("sqlite:///%s" % db)
    if isinstance(db, str):
        return create_engine(db)
    return db


def import_emjson_media(db, graph, sito: str, emjson_path: str, *,
                        search_dirs: Sequence[str] = (),
                        thumb_path: Optional[str] = None,
                        thumb_resize: Optional[str] = None,
                        log: Optional[Callable[[str], None]] = None,
                        progress: Optional[Callable[[int, int, str], None]] = None
                        ) -> EmMediaResult:
    """Registra come media i file citati dall'em.json per le schede del sito
    appena importate. Da chiamare DOPO l'importazione delle schede (servono
    i loro ``id_us``). Una seconda chiamata non duplica niente: il media si
    riconosce dal percorso del file, il collegamento da scheda e media."""
    from s3dgraphy.resources.locate import resolve
    from sqlalchemy import MetaData, text

    from ...utility.media_preview import make_previews
    from ...utility.qfield_importer import next_id, reflected
    from . import em_native_import as emn
    from .graph_ingestor import _NON_STRAT_TYPES, _PARADATA_ROW_TYPES, _is_synthetic_node

    scrivi = log or (lambda _m: None)
    esito = EmMediaResult()
    rows = emn.row_nodes(graph, _NON_STRAT_TYPES - _PARADATA_ROW_TYPES, _is_synthetic_node)
    names = emn.row_names(rows, getattr(graph, "edges", None) or [])
    basi = search_dirs_for(emjson_path, search_dirs)

    # 1 · i file, cercati e classificati
    da_collegare: List[Tuple[str, str]] = []                  # (id della scheda, percorso)
    mancanti, vuoti = [], []
    risolti: Dict[str, Optional[str]] = {}
    for nid, voci in collect_files(graph, rows).items():
        for voce in voci:
            loc = voce["locator"]
            basso = loc.lower()
            if basso.startswith(("blend://", "psx://")):
                chiave = basso.split("://", 1)[0]
                esito.skipped_types[chiave] = esito.skipped_types.get(chiave, 0) + 1
                continue
            if "://" in loc and not basso.startswith("file://"):
                esito.references += 1
                continue
            if media_type_of(loc) is None:
                estensione = split_media_name(loc)[1].lower() or "?"
                esito.skipped_types[estensione] = esito.skipped_types.get(estensione, 0) + 1
                continue
            if loc not in risolti:
                stato = resolve(voce, base_dirs=basi)
                if stato["state"] in ("on_disk", "both") and os.path.isfile(stato["path"]):
                    risolti[loc] = os.path.realpath(stato["path"])
                else:
                    risolti[loc] = None
                    (vuoti if stato["state"] == "empty_copy" else mancanti).append(loc)
            if risolti[loc]:
                da_collegare.append((nid, risolti[loc]))
    # Lo stesso file citato due volte (il PDF dal documento, «D.05.pdf», e
    # dalla sua risorsa, «DosCo/D.05.pdf») è un file solo che manca.
    esito.missing = _per_file(mancanti)
    esito.empty_copies = _per_file(vuoti)
    da_collegare = list(dict.fromkeys(da_collegare))
    if not da_collegare:
        return esito

    # 2 · media e collegamenti, in una transazione
    engine = _engine(db)
    md = MetaData()
    t_media = reflected(md, engine, "media_table")
    t_thumb = reflected(md, engine, "media_thumb_table")
    t_link = reflected(md, engine, "media_to_entity_table")
    nuovi: List[Dict[str, Any]] = []
    da_miniare: List[Dict[str, Any]] = []
    with engine.begin() as conn:
        id_us: Dict[str, Any] = {}
        prossimo_media = next_id(conn, t_media, "id_media")
        prossimo_link = next_id(conn, t_link, "id_mediaToEntity")
        media_di: Dict[str, Tuple[Any, str]] = {}
        for nid, percorso in da_collegare:
            if nid not in id_us:
                nodo, unita_tipo = rows[nid]
                riga = conn.execute(text("SELECT id_us FROM us_table WHERE sito = :s AND node_uuid = :n"),
                                    {"s": sito, "n": str(nodo.node_id)}).fetchone()
                if riga is None:
                    riga = conn.execute(text("SELECT id_us FROM us_table WHERE sito = :s AND us = :u "
                                             "AND unita_tipo = :t"),
                                        {"s": sito, "u": names.get(nid), "t": unita_tipo}).fetchone()
                id_us[nid] = riga[0] if riga is not None else None
                if riga is None:
                    esito.warnings.append("Scheda %s %s non trovata: i suoi media restano fuori"
                                          % (unita_tipo, names.get(nid)))
            if id_us[nid] is None:
                continue
            nome, estensione = split_media_name(percorso)
            if percorso not in media_di:
                gia = conn.execute(text("SELECT id_media FROM media_table WHERE filepath = :p"),
                                   {"p": percorso}).fetchone()
                if gia is not None:
                    media_di[percorso] = (gia[0], nome)
                    esito.already_present += 1
                    ha_miniatura = conn.execute(text("SELECT 1 FROM media_thumb_table WHERE id_media = :i"),
                                                {"i": gia[0]}).fetchone()
                    if ha_miniatura is None:
                        da_miniare.append({"id_media": gia[0], "path": percorso, "filename": nome,
                                           "filetype": estensione, "mediatype": media_type_of(percorso)})
                else:
                    tipo = media_type_of(percorso)
                    conn.execute(t_media.insert().values(
                        id_media=prossimo_media, mediatype=tipo, filename=nome,
                        filetype=estensione, filepath=percorso,
                        descrizione=str(getattr(rows[nid][0], "name", "") or nome)))
                    voce = {"id_media": prossimo_media, "path": percorso, "filename": nome,
                            "filetype": estensione, "mediatype": tipo}
                    nuovi.append(voce)
                    da_miniare.append(voce)
                    media_di[percorso] = (prossimo_media, nome)
                    esito.by_type[tipo] = esito.by_type.get(tipo, 0) + 1
                    prossimo_media += 1
            id_media, nome_media = media_di[percorso]
            collegato = conn.execute(text("SELECT 1 FROM media_to_entity_table WHERE id_entity = :e "
                                          "AND entity_type = 'US' AND id_media = :m"),
                                     {"e": id_us[nid], "m": id_media}).fetchone()
            if collegato is None:
                conn.execute(t_link.insert().values(
                    id_mediaToEntity=prossimo_link, id_entity=id_us[nid], entity_type="US",
                    table_name="us_table", id_media=id_media, filepath=percorso,
                    media_name=nome_media))
                prossimo_link += 1
                esito.linked += 1
    esito.inserted = len(nuovi)

    # 3 · miniature e copie, fuori dalla transazione (pyvista e i PDF
    # richiedono il loro tempo), poi le righe delle miniature
    if not da_miniare:
        return esito
    if not thumb_path or not thumb_resize:
        esito.warnings.append("Cartelle delle miniature non impostate (Impostazioni → percorsi): "
                              "%d media registrati senza miniature, la scheda non li mostra"
                              % len(da_miniare))
        return esito
    for cartella in (thumb_path, thumb_resize):
        if "://" not in str(cartella):
            os.makedirs(cartella, exist_ok=True)
    fatti = []
    for i, voce in enumerate(da_miniare):
        if progress is not None:
            progress(i, len(da_miniare), "%s.%s" % (voce["filename"], voce["filetype"]))
        try:
            miniatura, copia = make_previews(voce["id_media"], voce["path"], voce["filename"],
                                             voce["filetype"], voce["mediatype"],
                                             thumb_path, thumb_resize, log=esito.warnings.append)
        except Exception as e:                               # noqa: BLE001
            esito.warnings.append("%s.%s: miniatura non riuscita (%s)"
                                  % (voce["filename"], voce["filetype"], e))
            continue
        fatti.append((voce, miniatura, copia))
        scrivi("  + miniatura %s" % miniatura)
    if progress is not None:
        progress(len(da_miniare), len(da_miniare), "")
    with engine.begin() as conn:
        prossimo = next_id(conn, t_thumb, "id_media_thumb")
        for voce, miniatura, copia in fatti:
            conn.execute(t_thumb.insert().values(
                id_media_thumb=prossimo, id_media=voce["id_media"], mediatype=voce["mediatype"],
                media_filename=voce["filename"], media_thumb_filename=miniatura,
                filetype=voce["filetype"], filepath=miniatura, path_resize=copia))
            prossimo += 1
    esito.thumbnails = len(fatti)
    return esito
