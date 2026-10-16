"""La memoria dell'em.json importato da EMStudio, e il suo ritorno
nell'esportazione (Enzo, 16 ottobre 2026: «confronta con l'em.json
originale»). In EMStudio l'export di TempluMare si apriva come «Untitled
(TE)», con i nomi «1.USDUSD003», senza i 65 proxy, le 485 risorse, i 274
processi, gli autori, le licenze e la georeferenziazione.

pyArchInit tiene nelle sue tabelle le unità, i paradati, i rapporti e le
epoche: quella resta la fonte, e quello che si cambia nelle schede vale.
Il resto del grafo non ha una casa nelle schede, quindi l'em.json si ricorda
com'era (tabella ``pyarchinit_em_sources``, una riga per sito) e
all'esportazione si rimette:

* i **nomi** di EMStudio (``SU006``, ``D.07.08``, ``height``) alle schede
  il cui numero è ancora quello dato all'importazione — una scheda
  rinominata in pyArchInit tiene il nome nuovo;
* il **titolo** del grafo, il **codice dello studio** (``GT16``: Blender
  riattacca i proxy con quello, e una proposta ``TE`` li perdeva) e la
  **georeferenziazione** (EPSG e spostamenti);
* i **nodi che non sono schede** — risorse, file, modelli, forme semantiche,
  processi, gruppi, autori, licenze, narrativa — con i loro archi, le epoche
  rimappate su quelle della periodizzazione. Un ramo che non tocca più
  nessuna scheda (la proprietà a cui stava la forma è stata cancellata) non
  torna.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import delete, insert, inspect as sa_inspect, select, text

from ...db.structures.Em_sources_table import Em_sources_table as _EST

TABLE = _EST.pyarchinit_em_sources

#: i nodi che l'esportazione scrive già una volta sola: si fondono
_SINGOLI = ("graph", "geo_position", "study")

#: gli archi verso le epoche che le schede dicono da sé (periodo iniziale e
#: finale): tornano dal database, mai dal file
_ARCHI_DELLE_SCHEDE = frozenset({"has_first_epoch", "survive_in_epoch"})

#: i dati della georeferenziazione che il file di EMStudio porta e che il
#: database non sa (la scheda sito non ha EPSG né spostamenti)
_DATI_GEO = ("epsg", "shift_x", "shift_y", "shift_z", "rotation", "rotation_reference")


def _engine(db):
    from sqlalchemy import create_engine
    if hasattr(db, "engine"):
        return db.engine
    if isinstance(db, Path) or (isinstance(db, str) and "://" not in db):
        return create_engine("sqlite:///%s" % db)
    if isinstance(db, str):
        return create_engine(db)
    return db


def ensure_table(engine) -> None:
    """Crea la tabella se manca, su SQLite e PostgreSQL. Idempotente."""
    _EST.metadata.create_all(engine, checkfirst=True)


def remember_source(db, sito: str, emjson_path: str) -> bool:
    """Ricorda l'em.json importato nel sito: una riga per sito, l'ultima
    importazione vince. False quando il file non è un em.json."""
    try:
        with open(str(emjson_path), encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return False
    if not isinstance(doc, dict) or not isinstance(doc.get("graphs"), (dict, list)):
        return False
    # Un em.json scritto da pyArchInit porta il sito nelle sue schede: se è
    # un altro sito, il suo titolo, il suo codice e la sua posizione non
    # sono di questo (revisione 16-10-2026). Un file di EMStudio non porta
    # nessun sito; quello dello stesso sito si ricorda (le aggiunte fatte in
    # EMStudio a un export di pyArchInit tornano).
    siti = {str(d.get("sito")) for d in (n.get("data") or {} for n in _nodi_nel_file(doc).values())
            if isinstance(d, dict) and d.get("sito")}
    if siti and str(sito) not in siti:
        return False
    engine = _engine(db)
    ensure_table(engine)
    with engine.begin() as conn:
        conn.execute(delete(TABLE).where(TABLE.c.sito == str(sito)))
        conn.execute(insert(TABLE).values(
            sito=str(sito), graph_id=str(doc.get("active_graph_id") or "")[:200],
            source_name=os.path.basename(str(emjson_path))[:500],
            imported_at=datetime.now().isoformat(timespec="seconds"),
            payload=json.dumps(doc, ensure_ascii=False)))
    return True


def load_source(db, sito: str) -> Optional[Dict[str, Any]]:
    """L'em.json ricordato per il sito, o None."""
    engine = _engine(db)
    try:
        if not sa_inspect(engine).has_table(TABLE.name):
            return None
        with engine.connect() as conn:
            riga = conn.execute(select(TABLE.c.payload).where(TABLE.c.sito == str(sito))
                                .order_by(TABLE.c.id.desc())).first()
    except Exception:                                        # noqa: BLE001
        return None
    if riga is None:
        return None
    try:
        return json.loads(riga[0])
    except ValueError:
        return None


def _testo(valore) -> str:
    if isinstance(valore, dict):
        valore = valore.get("default") or next(iter(valore.values()), "")
    return str(valore or "").strip()


def _dati(node) -> Dict[str, Any]:
    d = getattr(node, "data", None)
    if not isinstance(d, dict):
        d = {}
        try:
            node.data = d
        except Exception:                                    # noqa: BLE001
            pass
    return d


#: i dati che il file decide anche quando l'export ne ha già uno: il tipo e il
#: valore di una proprietà (EMStudio riconosce il proxy di un'unità dalla
#: proprietà «geometry» con l'id della forma nel valore; l'export la
#: riscriveva «string» e senza valore, e i proxy erano 0 su 114)
_DATI_DEL_FILE = frozenset({"property_type", "value"})


#: i dati che l'esportatore prende dagli attributi del nodo quando ``data``
#: non li ha (``_LIFTED_ATTRS`` di emjson_exporter): se il nodo ne ha uno,
#: è quello di adesso e vince sul file
_DATI_DEL_NODO = frozenset({"start_time", "end_time", "color", "url", "source",
                            "symbol", "label", "definition", "stratigraphic_kind",
                            "source_code"})

#: come si disegna un nodo del suo tipo: vale solo se il tipo è ancora quello
_DATI_DI_VISTA = frozenset({"shape", "border_style", "fill_color"})


def _nodi_nel_file(doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """``{id del nodo: nodo}`` com'è scritto nel file, grafo attivo."""
    grafi = doc.get("graphs") or {}
    if isinstance(grafi, dict):
        grafo = grafi.get(doc.get("active_graph_id")) or next(iter(grafi.values()), {})
    else:
        grafo = grafi[0] if grafi else {}
    nodi = grafo.get("nodes") or []
    if isinstance(nodi, dict):
        nodi = list(nodi.values())
    return {str(n.get("id")): n for n in nodi if isinstance(n, dict)}


def _pieno(valore) -> bool:
    return valore not in (None, "", [], {})


def _rimetti_dati(nodo, nel_file: Dict[str, Any]) -> None:
    """I dati del nodo nel file tornano nel nodo esportato, senza mai
    prevalere su quello che la scheda dice adesso:

    * tipo e valore di una proprietà vengono dal file (la scheda non li tiene);
    * il file di un documento è quello del campo Documentazione della scheda;
    * un dato che il nodo ha già (data, attributi, o un attributo che
      l'esportatore solleva, come ``symbol`` o ``label``) resta il suo;
    * forma e colori del disegno solo se il tipo non è cambiato;
    * il resto (posizione, istanze di un documento…) si aggiunge."""
    dati_file = (nel_file or {}).get("data") or {}
    if not isinstance(dati_file, dict) or not dati_file:
        return
    dati = _dati(nodo)
    attributi = getattr(nodo, "attributes", None) or {}
    percorso = str(attributi.get("documentazione") or "").strip()
    stesso_tipo = (nel_file or {}).get("node_type") == getattr(nodo, "node_type", None)
    for chiave, valore in dati_file.items():
        if chiave in _DATI_DEL_FILE:
            dati[chiave] = valore
            try:
                setattr(nodo, chiave, valore)
            except Exception:                                # noqa: BLE001
                pass
            continue
        if chiave == "url" and percorso and not percorso.startswith("["):
            dati["url"] = percorso                           # la scheda vince
            continue
        if chiave in dati or chiave in attributi:
            continue
        if chiave in _DATI_DEL_NODO and _pieno(getattr(nodo, chiave, None)):
            continue
        if chiave in _DATI_DI_VISTA and not stesso_tipo:
            continue
        dati[chiave] = valore


def restore_into(graph, doc: Dict[str, Any], db, sito: str) -> Dict[str, Any]:
    """Rimette nel ``graph`` esportato quello che l'em.json ricordato porta e
    le schede no. Restituisce quanto ha rimesso: ``names``, ``nodes``,
    ``edges``, ``pruned`` (rami rimasti senza scheda), ``code``."""
    from s3dgraphy import hdto
    from s3dgraphy.importer.emjson_importer import parse_emjson

    from . import em_native_import as emn
    from .graph_ingestor import _NON_STRAT_TYPES, _PARADATA_ROW_TYPES, _is_synthetic_node

    esito: Dict[str, Any] = {"names": 0, "nodes": 0, "edges": 0, "pruned": 0, "code": None}
    sorgente, _avvisi = parse_emjson(doc)
    righe = emn.row_nodes(sorgente, _NON_STRAT_TYPES - _PARADATA_ROW_TYPES, _is_synthetic_node)
    nomi_importati = emn.row_names(righe, getattr(sorgente, "edges", None) or [])

    engine = _engine(db)
    with engine.connect() as conn:
        attuali = {str(r[0]): str(r[1]) for r in conn.execute(
            text("SELECT node_uuid, us FROM us_table WHERE sito = :s AND node_uuid IS NOT NULL"),
            {"s": sito})}
        periodi: Dict[str, tuple] = {}
        try:
            colonne = {c["name"] for c in sa_inspect(conn).get_columns("periodizzazione_table")}
            if "node_uuid" in colonne:
                for uu, per, fase in conn.execute(text(
                        "SELECT node_uuid, periodo, fase FROM periodizzazione_table "
                        "WHERE sito = :s AND node_uuid IS NOT NULL"), {"s": sito}):
                    periodi[str(uu)] = (per, fase)
        except Exception:                                    # noqa: BLE001
            periodi = {}

    per_id = {str(n.node_id): n for n in graph.nodes}
    nodi_nel_file = _nodi_nel_file(doc)

    # 1 · i dati e i nomi di EMStudio alle schede
    for nid, (nodo_sorgente, _ut) in righe.items():
        nodo = per_id.get(nid)
        if nodo is None:
            continue
        _rimetti_dati(nodo, nodi_nel_file.get(nid) or {})
        nome = getattr(nodo_sorgente, "name", None)
        if not nome or attuali.get(nid) != nomi_importati.get(nid):
            continue                   # rinominata in pyArchInit: vale il nome nuovo
        if getattr(nodo, "name", None) != nome:
            nodo.name = nome
            esito["names"] += 1

    # 2 · da un id del file a un id dell'export: epoche e nodi singoli
    mappa: Dict[str, str] = {}
    epoche_sorgente = {str(n.node_id) for n in sorgente.nodes if type(n).__name__ == "EpochNode"}
    epoche = {str(n.node_id) for n in graph.nodes if type(n).__name__ == "EpochNode"}
    per_nome = {_testo(n.name): str(n.node_id) for n in graph.nodes
                if type(n).__name__ == "EpochNode"}
    for n in sorgente.nodes:
        if type(n).__name__ != "EpochNode":
            continue
        pf = periodi.get(str(n.node_id))
        candidato = ("epoch_%s_%s" % pf) if pf else None
        if candidato not in epoche:
            candidato = per_nome.get(_testo(n.name))
        if candidato:
            mappa[str(n.node_id)] = candidato
    for tipo in _SINGOLI:
        mio = next((n for n in graph.nodes if getattr(n, "node_type", None) == tipo), None)
        suo = next((n for n in sorgente.nodes if getattr(n, "node_type", None) == tipo), None)
        if mio is None or suo is None:
            continue
        mappa[str(suo.node_id)] = str(mio.node_id)
        dati_miei, dati_suoi = _dati(mio), _dati(suo)
        for chiave, valore in dati_suoi.items():
            if chiave in ("hdto_role", "code", "code_proposed"):
                continue
            if tipo == "geo_position" and chiave in _DATI_GEO:
                if valore not in (None, ""):
                    dati_miei[chiave] = valore
            elif chiave not in dati_miei:
                dati_miei[chiave] = valore

    # 3 · il codice dello studio e il titolo
    codice = hdto.study_code(sorgente)
    # Un codice che nel file è solo una proposta (l'export di pyArchInit
    # reimportato) resta una proposta: lo conferma una persona, non noi.
    if codice and not hdto.is_code_proposed(sorgente):
        try:
            esito["code"] = hdto.confirm_study_code(graph, codice)
        except ValueError:
            pass                       # un codice confermato da una persona resta
    if _testo(getattr(sorgente, "name", None)):
        graph.name = getattr(sorgente, "name")

    # 4 · i nodi che non sono schede, agganciati a quello che c'è ancora
    candidati: Dict[str, Any] = {}
    for n in sorgente.nodes:
        sid = str(n.node_id)
        if sid in righe or sid in mappa or sid in per_id:
            continue
        if type(n).__name__ == "EpochNode" or getattr(n, "node_type", None) in _SINGOLI:
            continue                   # un'epoca senza periodo non torna
        candidati[sid] = n

    def destinazione(sid: str) -> Optional[str]:
        if sid in candidati:
            return sid
        if sid in mappa:
            return mappa[sid]
        return sid if sid in per_id else None

    archi = []
    gradi: Counter = Counter()
    for e in getattr(sorgente, "edges", None) or []:
        s, t = str(e.edge_source), str(e.edge_target)
        gradi[s] += 1
        gradi[t] += 1
        if s not in candidati and t not in candidati:
            # Fra schede, e nascita e sopravvivenza nelle epoche: li fa il
            # database, che è la fonte. Gli altri legami di un'epoca con una
            # scheda (l'epoca che possiede «absolute_time_start») nelle
            # schede non ci sono: tornano dal file.
            epoca = (s in mappa and s in epoche_sorgente) or (t in mappa and t in epoche_sorgente)
            if not epoca or e.edge_type in _ARCHI_DELLE_SCHEDE:
                continue
        ds, dt = destinazione(s), destinazione(t)
        if ds is None or dt is None or ds == dt:
            continue
        archi.append((e.edge_id, ds, e.edge_type, dt, getattr(e, "attributes", None)))

    vicini = defaultdict(set)
    coda = deque(c for c in candidati if gradi[c] == 0)     # soli anche nel file
    for _eid, ds, _ty, dt, _attr in archi:
        vicini[ds].add(dt)
        vicini[dt].add(ds)
        for a, b in ((ds, dt), (dt, ds)):
            if a in candidati and b not in candidati:
                coda.append(a)                               # tocca una scheda o un'epoca
    vivi = set()
    while coda:
        x = coda.popleft()
        if x in vivi:
            continue
        vivi.add(x)
        coda.extend(y for y in vicini[x] if y in candidati and y not in vivi)
    esito["pruned"] = len(candidati) - len(vivi)

    for sid, nodo in candidati.items():
        if sid in vivi:
            try:
                graph.add_node(nodo)
                esito["nodes"] += 1
            except Exception:                                # noqa: BLE001
                vivi.discard(sid)
    terne = {(e.edge_source, e.edge_type, e.edge_target) for e in graph.edges}
    ids = {e.edge_id for e in graph.edges}
    for eid, ds, ty, dt, attributi in archi:
        if (ds in candidati and ds not in vivi) or (dt in candidati and dt not in vivi):
            continue
        if (ds, ty, dt) in terne:
            continue
        nuovo_id = str(eid) if eid and str(eid) not in ids else "%s_%s_%s" % (ds, ty, dt)
        try:
            arco = graph.add_edge(edge_id=nuovo_id, edge_source=ds, edge_target=dt, edge_type=ty)
        except ValueError:
            continue
        # quale file di una risorsa è il modello (`role`, `path`), i segni
        # della propagazione dei paradati (`derived`…): viaggiano sull'arco
        if isinstance(attributi, dict) and attributi:
            if not isinstance(getattr(arco, "attributes", None), dict):
                arco.attributes = {}
            arco.attributes.update(attributi)
        terne.add((ds, ty, dt))
        ids.add(nuovo_id)
        esito["edges"] += 1
    if hasattr(graph, "invalidate_indices"):
        graph.invalidate_indices()
    return esito


def restore_for_export(db, sito: str, graphs) -> list:
    """Per l'esportazione: rimette la memoria del sito in ogni grafo, e
    restituisce le righe da dire a chi esporta (nessuna se il sito non viene
    da un em.json di EMStudio)."""
    doc = load_source(db, sito)
    if doc is None:
        return []
    righe = []
    for g in graphs:
        try:
            r = restore_into(g, doc, db, sito)
        except Exception as e:                               # noqa: BLE001
            righe.append("La memoria dell'em.json importato non è tornata: %s" % e)
            continue
        righe.append("Dall'em.json importato tornano %d nomi, %d nodi e %d archi%s%s."
                     % (r["names"], r["nodes"], r["edges"],
                        ", codice dello studio %s" % r["code"] if r["code"] else "",
                        "; %d rami senza più schede restano fuori" % r["pruned"]
                        if r["pruned"] else ""))
    return righe
