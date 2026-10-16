"""Le regole per importare un em.json scritto da EMStudio (non da
pyArchInit) nelle schede di pyArchInit.

Enzo, 16 ottobre 2026, con TempluMare_v3.2.em.json in un database vuoto:
«solo le US hanno archi, doc, property, USVn non hanno connessioni; non
importa la periodizzazione». Misurato sul file: 1064 nodi senza scheda
(risorse, file, modelli 3D, forme, processi del gemello digitale)
diventavano «US» (la colonna ``unita_tipo`` vale 'US' per default); le
proprietà, gli estrattori e i combinatori restavano fuori, così i
documenti erano isolati; fra unità virtuali il «prima di» diventava «>>»,
che l'esportazione rilegge come connessione generica; l'attività finiva
nei rapporti; le epoche di EMStudio (id generici, solo nome e date)
venivano saltate.

Qui niente SQL e niente Qt: decide quali nodi sono schede, come si
chiamano, che rapporti hanno, in che periodo stanno. Le usa
:mod:`graph_ingestor`.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

#: Le classi che diventano schede oltre a quelle della tabella della
#: libreria (``S3DGRAPHY_TYPE_TO_UNITA_TIPO``): la proprietà, che la
#: libreria non elenca, con il codice storico di pyArchInit.
_EXTRA_CLASS_TO_UNITA_TIPO = {
    "PropertyNode": "property",
    "VirtualSpecialFindUnit": "VSF",
}

#: Il vocabolario di ripiego, se quello di pyArchInit non si carica.
_FALLBACK_VOCAB = (
    "US", "USM", "USR", "USD", "USVs", "USVn", "SF", "VSF", "RSF", "serSU",
    "serUSD", "serUSVn", "serUSVs", "TSU", "UL", "USN", "USNt", "CON",
    "DOC", "property", "Extractor", "Combinar",
)

#: Rapporti fisici: fra unità di tipo diverso si scrivono per esteso, che
#: l'esportazione rilegge nell'arco giusto (``Taglia`` → ``cuts``).
PHYSICAL_EDGES = frozenset({
    "overlies", "is_overlain_by", "cuts", "is_cut_by", "fills",
    "is_filled_by", "equals", "bonded_to", "abuts", "is_abutted_by",
})

#: «Prima / dopo»: fra unità non US/USM è la freccia semplice ``>``, che
#: l'esportazione rilegge come ``is_after`` (la doppia ``>>`` diventava
#: una connessione generica).
TEMPORAL_EDGES = frozenset({"is_after", "is_before"})

#: La catena dei paradati: la doppia freccia, che l'esportazione rifà
#: nell'arco dell'Extended Matrix (``paradata_edge_resolver``).
PARADATA_EDGES = frozenset({
    "has_property", "has_data_provenance", "extracted_from", "combines",
    "is_part_of", "generic_connection", "has_documentation",
})

#: Archi che non sono rapporti: periodi, attività, gruppi, risorse,
#: autori, processi. Hanno altre colonne o nessuna.
NOT_RAPPORTI_EDGES = frozenset({
    "has_first_epoch", "survive_in_epoch", "is_in_activity",
    "is_in_location", "is_in_paradata_nodegroup", "has_paradata_nodegroup",
    "has_same_time", "has_author", "has_license", "has_embargo",
    "has_linked_resource", "has_file", "has_representation_model",
    "has_semantic_shape", "dtc_derived_from", "dtc_had_input",
    "dtc_had_output",
})

_EPOCH_ID = re.compile(r"^epoch_([^_]+)_(.+?)(_synthetic)?$")


# ---------------------------------------------------------------- tipi

def known_unita_tipi() -> frozenset:
    """I codici che una scheda può avere: il vocabolario di pyArchInit,
    più le varianti di US/USM e i codici della libreria."""
    voci = set(_FALLBACK_VOCAB)
    try:
        from ...utility.pyarchinit_i18n_stratigraphic import _build_common_items
        voci.update(str(v) for v in _build_common_items())
    except Exception:                               # noqa: BLE001
        pass
    try:
        from s3dgraphy.rapporti import S3DGRAPHY_TYPE_TO_UNITA_TIPO, UNITA_TIPO_CANONICAL
        voci.update(UNITA_TIPO_CANONICAL)
        voci.update(S3DGRAPHY_TYPE_TO_UNITA_TIPO.values())
    except Exception:                               # noqa: BLE001
        pass
    return frozenset(voci)


def row_unita_tipo(node, vocabolario: Optional[frozenset] = None) -> Optional[str]:
    """Il codice della scheda per ``node``, o ``None`` se il nodo non è
    una scheda (risorse, file, modelli, forme, processi, narrativa…).
    Prima l'attributo, poi il codice della libreria, poi la classe, poi il
    ``node_type`` se pyArchInit lo conosce (serUSVn, USN, USNt…)."""
    attrs = getattr(node, "attributes", None) or {}
    if attrs.get("unita_tipo"):
        return str(attrs["unita_tipo"])
    try:
        from s3dgraphy.nodes.stratigraphic_node import unit_code
        code = unit_code(node)
        if code:
            return str(code)
    except Exception:                               # noqa: BLE001
        pass
    nome_classe = type(node).__name__
    try:
        from s3dgraphy.rapporti import S3DGRAPHY_TYPE_TO_UNITA_TIPO
        if nome_classe in S3DGRAPHY_TYPE_TO_UNITA_TIPO:
            return S3DGRAPHY_TYPE_TO_UNITA_TIPO[nome_classe]
    except Exception:                               # noqa: BLE001
        pass
    if nome_classe in _EXTRA_CLASS_TO_UNITA_TIPO:
        return _EXTRA_CLASS_TO_UNITA_TIPO[nome_classe]
    tipo = getattr(node, "node_type", None)
    voci = vocabolario if vocabolario is not None else known_unita_tipi()
    if tipo and str(tipo) in voci:
        return str(tipo)
    return None


def is_row_born(node) -> bool:
    """Vero per un nodo nato da una scheda di pyArchInit (un export di
    pyArchInit reimportato): porta ``node_uuid`` o ``us``."""
    attrs = getattr(node, "attributes", None) or {}
    return bool(attrs.get("node_uuid") or attrs.get("us"))


def is_generated_document(node) -> bool:
    """I documenti che l'esportazione di pyArchInit genera dalla colonna
    «documentazione» (``<uuid>_doc_<nome>``): non sono schede."""
    return (type(node).__name__ == "DocumentNode"
            and "_doc_" in str(getattr(node, "node_id", "") or "")
            and not is_row_born(node))


def is_generated_property(node, ids) -> bool:
    """Le proprietà che il proiettore genera dalle colonne di una scheda
    (``<id dell'unità>_<nome>``, ``pyarchinit_importer``): non sono schede."""
    if type(node).__name__ != "PropertyNode" or is_row_born(node):
        return False
    nid = str(getattr(node, "node_id", "") or "")
    nome = str(getattr(node, "name", "") or "")
    if not nome or not nid.endswith("_" + nome):
        return False
    return nid[: -(len(nome) + 1)] in ids


def row_nodes(graph, skip_classes: Iterable[str] = (), is_synthetic=None) -> Dict[str, Tuple[Any, str]]:
    """``{node_id: (nodo, unita_tipo)}`` dei nodi che diventano schede."""
    salta = frozenset(skip_classes)
    voci = known_unita_tipi()
    nodi = list(getattr(graph, "nodes", None) or [])
    ids = {str(getattr(n, "node_id", "")) for n in nodi}
    out: Dict[str, Tuple[Any, str]] = {}
    for n in nodi:
        if type(n).__name__ in salta:
            continue
        if is_synthetic is not None and is_synthetic(n):
            continue
        if is_generated_document(n) or is_generated_property(n, ids):
            continue
        nid = getattr(n, "node_id", None)
        if not nid:
            continue
        tipo = row_unita_tipo(n, voci)
        if not tipo:
            continue
        out[str(nid)] = (n, tipo)
    return out


def summarize(graph, rows: Dict[str, Tuple[Any, str]]) -> Tuple[Counter, Counter]:
    """(schede per ``unita_tipo``, nodi che non sono schede per tipo)."""
    schede = Counter(ut for _n, ut in rows.values())
    altri = Counter(str(getattr(n, "node_type", None) or type(n).__name__)
                    for n in getattr(graph, "nodes", None) or []
                    if str(getattr(n, "node_id", "")) not in rows)
    return schede, altri


def summary_text(schede: Counter, altri: Counter, massimo: int = 10) -> str:
    """Il riepilogo per la finestra: quante schede e di che tipo, quanti
    nodi restano fuori e di che tipo."""
    def elenco(c):
        voci = ["%s %d" % (k, v) for k, v in c.most_common(massimo)]
        if len(c) > massimo:
            voci.append("…")
        return ", ".join(voci)
    righe = ["%d schede: %s." % (sum(schede.values()), elenco(schede))]
    if altri:
        righe.append("%d nodi non sono schede: %s." % (sum(altri.values()), elenco(altri)))
    return "\n".join(righe)


# ---------------------------------------------------------------- nomi

#: Chi tiene il nome breve quando due tipi lo condividono: la stratigrafia
#: prima dei paradati, la US prima delle altre.
_PRIORITA = ("US", "USM", "USR", "USD", "USVs", "USVn", "serUSVs", "serUSVn",
             "serSU", "serUSD", "SF", "VSF", "RSF", "USN", "USNt", "TSU", "UL",
             "CON", "DOC", "Extractor", "Combinar", "property")


def _rango(unita_tipo: str) -> int:
    try:
        from s3dgraphy.rapporti import canonical_unita_tipo
        unita_tipo = canonical_unita_tipo(unita_tipo)
    except Exception:                               # noqa: BLE001
        pass
    return _PRIORITA.index(unita_tipo) if unita_tipo in _PRIORITA else len(_PRIORITA)

def row_names(rows: Dict[str, Tuple[Any, str]], edges: Iterable[Any]) -> Dict[str, str]:
    """Il campo ``us`` di ogni scheda. Le proprietà di EMStudio con lo
    stesso nome («height» 28 volte in TempluMare, una per unità)
    diventano «height (105)», col nome dell'unità a cui appartengono:
    la scheda US è unica per sito, area, US e tipo, e senza distinguerle
    finirebbero tutte su una riga."""
    from s3dgraphy.rapporti import strip_us_prefix
    base: Dict[str, str] = {}
    for nid, (n, _ut) in rows.items():
        attrs = getattr(n, "attributes", None) or {}
        if attrs.get("us") not in (None, ""):
            base[nid] = str(attrs["us"])
        else:
            nome = str(getattr(n, "name", "") or "").strip()
            base[nid] = strip_us_prefix(nome) if nome else ""
    proprietari: Dict[str, List[str]] = defaultdict(list)
    for e in edges or []:
        if getattr(e, "edge_type", None) == "has_property":
            src, tgt = str(e.edge_source), str(e.edge_target)
            if src in rows and tgt in rows:
                proprietari[tgt].append(src)
    omonime: Dict[str, List[str]] = defaultdict(list)
    for nid, (n, ut) in rows.items():
        if ut == "property" and not is_row_born(n) and base[nid]:
            omonime[base[nid]].append(nid)
    nomi = dict(base)
    for nome, ids in omonime.items():
        if len(ids) < 2:
            continue
        for nid in ids:
            chi = sorted(base[o] for o in proprietari.get(nid, []) if base.get(o))
            nomi[nid] = "%s (%s)" % (nome, chi[0] if chi else nid[:8])
    # Lo stesso nome breve per due tipi («C.05» e «D.05» → «05», «SU002» e
    # «USD002» → «002»): i rapporti indicano il bersaglio solo con numero e
    # area, e l'esportazione attaccava i legami all'unità sbagliata (20
    # collisioni in TempluMare, 9 legami proprietà→combinatore finiti su un
    # documento). Il tipo più forte tiene il nome breve, gli altri prendono
    # il nome completo di EMStudio.
    per_nome: Dict[str, List[str]] = defaultdict(list)
    for nid in rows:
        per_nome[nomi[nid]].append(nid)
    for nome, ids in per_nome.items():
        if len({rows[i][1] for i in ids}) < 2:
            continue
        ordinati = sorted(ids, key=lambda i: (_rango(rows[i][1]), str(getattr(rows[i][0], "name", "")), i))
        for nid in ordinati[1:]:
            nodo, tipo = rows[nid]
            if is_row_born(nodo) or rows[ordinati[0]][1] == tipo:
                continue
            completo = str(getattr(nodo, "name", "") or "").strip()
            nomi[nid] = completo if completo and completo != nome else "%s (%s)" % (nome, tipo)
    visti: Counter = Counter()
    for nid in sorted(rows, key=lambda x: (nomi[x], x)):
        chiave = (nomi[nid], rows[nid][1])
        visti[chiave] += 1
        if visti[chiave] > 1 and not is_row_born(rows[nid][0]):
            nomi[nid] = "%s %d" % (nomi[nid], visti[chiave])
    return nomi


# ---------------------------------------------------------------- periodi

def is_epoch(node) -> bool:
    return type(node).__name__ == "EpochNode"


def epoch_key(node) -> Optional[Tuple[str, str]]:
    """(periodo, fase) di un'epoca scritta da pyArchInit: dagli attributi
    o dall'id ``epoch_<periodo>_<fase>``. ``None`` per un'epoca di EMStudio."""
    attrs = getattr(node, "attributes", None) or {}
    periodo, fase = attrs.get("periodo"), attrs.get("fase")
    if periodo is None:
        m = _EPOCH_ID.match(str(getattr(node, "node_id", "") or ""))
        if m:
            periodo, fase = m.group(1), m.group(2)
    if periodo is None:
        return None
    return str(periodo), (str(fase) if fase is not None else "")


def _anno(valore) -> float:
    try:
        return float(valore)
    except (TypeError, ValueError):
        return float("inf")


def _numero(valore) -> float:
    try:
        return float(valore)
    except (TypeError, ValueError):
        return float("-inf")


def plan_epochs(graph, existing: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, Tuple[str, str]], List[Dict[str, Any]]]:
    """``({epoch_id: (periodo, fase)}, [epoche da creare])``.

    Le epoche di pyArchInit tengono il loro periodo e la loro fase. Quelle
    di EMStudio si ritrovano nella periodizzazione del sito per
    ``node_uuid`` o per nome («II A.D.» = datazione estesa o descrizione);
    le altre diventano periodi nuovi, dal più antico (``start_time``), con
    numeri dopo l'ultimo periodo del sito e fase 1."""
    righe = [dict(r) for r in existing or []]
    per_uuid = {str(r["node_uuid"]): r for r in righe if r.get("node_uuid")}
    per_nome: Dict[str, Dict[str, Any]] = {}
    for r in righe:
        for campo in ("datazione_estesa", "descrizione"):
            v = str(r.get(campo) or "").strip().lower()
            if v:
                per_nome.setdefault(v, r)
    massimo = 0
    for r in righe:
        try:
            massimo = max(massimo, int(r.get("periodo")))
        except (TypeError, ValueError):
            pass
    mappa: Dict[str, Tuple[str, str]] = {}
    native = []
    for n in getattr(graph, "nodes", None) or []:
        if not is_epoch(n):
            continue
        chiave = epoch_key(n)
        if chiave is not None:
            mappa[str(n.node_id)] = chiave
        else:
            native.append(n)
    nuove: List[Dict[str, Any]] = []
    for n in sorted(native, key=lambda x: (_anno(getattr(x, "start_time", None)), str(getattr(x, "name", "")))):
        nome = str(getattr(n, "name", "") or "").strip()
        r = per_uuid.get(str(n.node_id)) or per_nome.get(nome.lower())
        if r is not None:
            mappa[str(n.node_id)] = (str(r.get("periodo")), str(r.get("fase") if r.get("fase") is not None else ""))
            continue
        massimo += 1
        mappa[str(n.node_id)] = (str(massimo), "1")
        nuove.append({
            "node_id": str(n.node_id), "periodo": massimo, "fase": "1", "nome": nome,
            "descrizione": str(getattr(n, "description", "") or "").strip() or nome,
            "inizio": getattr(n, "start_time", None), "fine": getattr(n, "end_time", None),
        })
    return mappa, nuove


def unit_epochs(graph, mappa: Dict[str, Tuple[str, str]]) -> Dict[str, Dict[str, str]]:
    """Periodo e fase, iniziali e finali, di ogni unità: l'iniziale da
    ``has_first_epoch``, la finale dall'ultima ``survive_in_epoch`` (o
    uguale all'iniziale se l'unità non sopravvive)."""
    prima: Dict[str, Tuple[str, str]] = {}
    dopo: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for e in getattr(graph, "edges", None) or []:
        tipo, src, tgt = getattr(e, "edge_type", None), str(e.edge_source), str(e.edge_target)
        if tgt not in mappa:
            continue
        if tipo == "has_first_epoch":
            prima.setdefault(src, mappa[tgt])
        elif tipo == "survive_in_epoch":
            dopo[src].append(mappa[tgt])
    out: Dict[str, Dict[str, str]] = {}
    for nid in set(prima) | set(dopo):
        d: Dict[str, str] = {}
        if nid in prima:
            d["periodo_iniziale"], d["fase_iniziale"] = prima[nid]
        if dopo.get(nid):
            p, f = max(dopo[nid], key=lambda k: (_numero(k[0]), _numero(k[1])))
            d["periodo_finale"], d["fase_finale"] = p, f
        elif nid in prima:
            d["periodo_finale"], d["fase_finale"] = prima[nid]
        out[nid] = d
    return out


# ---------------------------------------------------------------- rapporti

def activity_of(graph, rows: Dict[str, Tuple[Any, str]]) -> Dict[str, str]:
    """L'attività di ogni scheda (``is_in_activity``), per la colonna
    «attivita»: prima finiva nei rapporti come «>> VAct.04 Temple»."""
    gruppi = {str(n.node_id): str(getattr(n, "name", "") or "")
              for n in getattr(graph, "nodes", None) or []
              if type(n).__name__ == "ActivityNodeGroup"}
    out: Dict[str, str] = {}
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) != "is_in_activity":
            continue
        src, tgt = str(e.edge_source), str(e.edge_target)
        if src in rows and gruppi.get(tgt):
            out.setdefault(src, gruppi[tgt])
    return out


def build_rapporti(graph, rows: Dict[str, Tuple[Any, str]], names: Dict[str, str],
                   sito: str, area_of: Dict[str, str]) -> Dict[str, List[List[str]]]:
    """I rapporti di ogni scheda, ``[segno, us, area, sito]``.

    Solo fra due schede. Fra due US/USM come la libreria (stesse parole,
    ancorate ai termini della scheda d'origine). Fra tipi diversi: i fisici
    per esteso, il prima/dopo con ``>``/``<``, la catena dei paradati con
    ``>>``/``<<``. Periodi, attività, gruppi, risorse e processi non sono
    rapporti."""
    from s3dgraphy.rapporti import (CANONICAL_UNIT_TYPES, EDGE_TYPE_DIRECTION_FORWARD,
                                    EDGE_TYPE_TO_RAPPORTI_IT, NON_RAPPORTI_EDGE_TYPES,
                                    canonical_unita_tipo, select_rapporti_label)
    try:
        from s3dgraphy.rapporti import _as_written, _source_rapporti_label
    except Exception:                               # noqa: BLE001
        _as_written = None
        _source_rapporti_label = None
    abbreviati = (">", "<", ">>", "<<")
    out: Dict[str, List[List[str]]] = {}
    for e in getattr(graph, "edges", None) or []:
        src, tgt = str(getattr(e, "edge_source", "")), str(getattr(e, "edge_target", ""))
        tipo = getattr(e, "edge_type", None)
        if not tipo or src not in rows or tgt not in rows:
            continue
        if _as_written is not None:
            try:
                tipo = _as_written(tipo)
            except Exception:                       # noqa: BLE001
                pass
        if tipo in NOT_RAPPORTI_EDGES:
            continue
        ut_src, ut_tgt = rows[src][1], rows[tgt][1]
        canonici = (canonical_unita_tipo(ut_src) in CANONICAL_UNIT_TYPES
                    and canonical_unita_tipo(ut_tgt) in CANONICAL_UNIT_TYPES)
        if canonici:
            if tipo in NON_RAPPORTI_EDGE_TYPES:
                continue
            segno = select_rapporti_label(tipo, ut_src, ut_tgt)
            if segno not in abbreviati and _source_rapporti_label is not None:
                try:
                    segno = _source_rapporti_label(rows[src][0], names[tgt], tipo) or segno
                except Exception:                   # noqa: BLE001
                    pass
        elif tipo in PHYSICAL_EDGES:
            segno = EDGE_TYPE_TO_RAPPORTI_IT.get(tipo, str(tipo))
        elif tipo in TEMPORAL_EDGES:
            segno = ">" if EDGE_TYPE_DIRECTION_FORWARD.get(tipo, True) else "<"
        elif tipo in PARADATA_EDGES:
            segno = ">>" if EDGE_TYPE_DIRECTION_FORWARD.get(tipo, True) else "<<"
        elif tipo in NON_RAPPORTI_EDGE_TYPES:
            continue
        else:
            segno = select_rapporti_label(tipo, ut_src, ut_tgt)
        voce = [segno, names[tgt], str(area_of.get(tgt) or "1"), sito]
        cesto = out.setdefault(src, [])
        if voce not in cesto:
            cesto.append(voce)
    return out


# ---------------------------------------------------------------- sito

def _testo(valore) -> str:
    if isinstance(valore, dict):
        valore = valore.get("default") or next(iter(valore.values()), "")
    return str(valore or "").strip()


def graph_title(graph) -> str:
    """Il nome del grafo (l'em.json lo scrive per lingua: ``{'default': …}``)."""
    return _testo(getattr(graph, "name", None))


def site_description(graph) -> str:
    """La descrizione della scheda sito creata dall'import: nome del
    grafo, codice, autori, posizione."""
    parti: List[str] = []
    titolo = graph_title(graph)
    codice = ""
    autori: List[str] = []
    posizione = ""
    for n in getattr(graph, "nodes", None) or []:
        classe = type(n).__name__
        dati = getattr(n, "data", None) or {}
        if not isinstance(dati, dict):
            dati = {}
        if classe == "GraphNode" and dati.get("em_id"):
            codice = str(dati["em_id"])
        elif classe == "AuthorNode":
            nome = str(getattr(n, "name", "") or "").strip()
            if nome and nome not in autori:
                autori.append(nome)
        elif classe == "GeoPositionNode":
            epsg = dati.get("epsg") or (getattr(n, "attributes", None) or {}).get("epsg")
            if epsg:
                posizione = "EPSG:%s" % epsg
                if dati.get("shift_x") is not None and dati.get("shift_y") is not None:
                    posizione += ", origine %s / %s" % (dati["shift_x"], dati["shift_y"])
    intestazione = "Importato da Extended Matrix"
    if titolo:
        intestazione += ": «%s»" % titolo
    if codice:
        intestazione += " (%s)" % codice
    parti.append(intestazione + ".")
    if autori:
        parti.append("Autori: %s." % ", ".join(autori))
    if posizione:
        parti.append("Posizione: %s." % posizione)
    return " ".join(parti)
