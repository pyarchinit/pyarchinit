"""La narrativa dell'Extended Matrix, scritta dall'AI già impostata. Puro.

Niente Qt, niente rete, nessun SDK di modelli: la chiamata al modello
arriva da fuori come ``chat(messages) -> str`` (o ``(str, troncato)``),
così i test la provano con un modello finto e la scheda del pannello le
passa ``LLMProviderManager``. Tutto il lato grafo lo fa la libreria
(``s3dgraphy.narrative``): scheletro dei capitoli, briefing, bozza
attribuita, convalida, export. Qui ci sono le decisioni di pyArchInit:
quale configurazione AI leggere, che cosa aggiungere al briefing (i
rapporti e i campi della scheda, che la libreria non porta), come
conservare la narrativa quando il sito si riesporta dal database.

Spec: docs/superpowers/specs/2026-10-12-narrativa-ai-design.md
"""
from __future__ import annotations

import io
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

#: Gli scope delle impostazioni AI già salvate, nell'ordine in cui si
#: leggono. Nessuna impostazione nuova: vale la prima usabile.
SCOPES = ("us_report", "rag_query", "palimpsest_report", "text2sql")

_SCOPE_LABELS = {
    # I nomi veri dei bottoni: nella scheda US «Report» apre il «Generatore
    # di Report» (gruppo «Provider AI»), e «Query AI Database» l'interrogazione.
    "us_report": {"it": "Generatore di Report della scheda US",
                  "en": "Report generator of the US form"},
    "rag_query": {"it": "Query AI Database",
                  "en": "Query AI Database"},
    "palimpsest_report": {"it": "Relazione Palimpsest",
                          "en": "Palimpsest report"},
    "text2sql": {"it": "Testo in SQL", "en": "Text to SQL"},
}

#: Oltre tante unità il briefing si taglia: un capitolo di trecento US
#: non si racconta in un paragrafo, e un prompt enorme costa e confonde.
MAX_ACTIONS = 80

#: Quanto può scrivere il modello per capitolo. Con 1800 Claude Opus 4.7
#: si fermava a metà di un capitolo di 23 unità (misurato il 2026-10-12,
#: 3397 caratteri): le menzioni costano token.
MAX_TOKENS = 4000

#: Tetto in caratteri del messaggio col briefing: oltre, si stringe
#: (``fit_briefing``). Un capitolo di 300 unità con descrizioni lunghe
#: arrivava a 127 000 caratteri (revisione del 2026-10-12): i modelli
#: locali tagliano in silenzio e vedono la coda del JSON, quelli cloud
#: li pagano.
MAX_PROMPT_CHARS = 25_000

#: Quanto resta di un testo lungo della scheda quando si stringe.
MAX_DETAIL_CHARS = 300

#: Quante immagini per unità, e com'è alta la striscia che le affianca.
MEDIA_PER_UNIT = 2
IMAGE_HEIGHT = 480
IMAGE_GAP = 12

#: Gli estrattori che registrano i prompt (``write_ai_draft``).
PROMPT_EXTRACTOR_PREFIX = "EXT.prompt."

#: Gli archi in cui la sorgente è più recente del bersaglio.
YOUNGER_FIRST_KINDS = ("overlies", "covers", "cuts", "fills", "abuts",
                       "leans_on", "is_after")
SYMMETRIC_KINDS = ("equals", "bonded_to", "has_same_time",
                   "is_physically_equal_to", "is_bonded_to")

#: Il segnaposto che il template scrive dove la prosa è da fare.
PLACEHOLDER_RE = re.compile(r"^\s*\[\s*(da scrivere|to be written)\s*:",
                            re.IGNORECASE)

#: Colonna della scheda → nome nel briefing (in inglese: è per il modello).
DETAIL_FIELDS = (
    ("unita_tipo", "unit_type"), ("d_stratigrafica", "stratigraphic_definition"),
    ("d_interpretativa", "interpretive_definition"),
    ("descrizione", "description_long"), ("interpretazione", "interpretation"),
    ("periodo_iniziale", "period_start"), ("fase_iniziale", "phase_start"),
    ("periodo_finale", "period_end"), ("fase_finale", "phase_end"),
    ("datazione_estesa", "dating"), ("attivita", "activity"),
    ("struttura", "structure"), ("saggio", "trench"), ("ambient", "room"),
    ("settore", "sector"), ("area", "area"), ("us", "unit_number"),
)

LANGUAGE = ["it"]

_M = {
    "file_unreadable": {"it": "«{name}» non si legge come em.json: {err}",
                        "en": "“{name}” cannot be read as em.json: {err}"},
    "file_unwritable": {"it": "Non sono riuscito a scrivere «{name}»: {err}. Il file precedente è intatto.",
                        "en": "Could not write “{name}”: {err}. The previous file is intact."},
    "empty_reply": {"it": "il modello non ha scritto niente",
                    "en": "the model wrote nothing"},
    "model_label": {"it": "Modello: {model} ({scope})",
                    "en": "Model: {model} ({scope})"},
    "status_empty": {"it": "da scrivere", "en": "to be written"},
    "status_ai_draft": {"it": "bozza AI", "en": "AI draft"},
    "status_ai_endorsed": {"it": "convalidato", "en": "endorsed"},
    "status_human": {"it": "scritto", "en": "written"},
    "truncated": {"it": "troncato", "en": "truncated"},
    "narrative_kept": {"it": "Narrativa conservata dal file precedente ({n} capitoli).",
                       "en": "Narrative kept from the previous file ({n} chapters)."},
    "narrative_not_kept": {"it": "Il file precedente non si legge ({err}): la narrativa, se c'era, non è stata conservata.",
                           "en": "The previous file cannot be read ({err}): its narrative, if any, was not kept."},
    "prompt_context": {"it": "Capitolo «{title}» ({kind}); unità, dalla più antica: {ids}",
                       "en": "Chapter “{title}” ({kind}); units, oldest first: {ids}"},
    "summary": {"it": "{ok} capitoli generati, {failed} falliti",
                "en": "{ok} chapters generated, {failed} failed"},
    "summary_cancelled": {"it": " (interrotto)", "en": " (cancelled)"},
    "narrative_not_travelled": {
        "it": "La narrativa del file precedente (grafi: {old}) non è passata nel file nuovo "
              "(grafi: {new}): la forma del file è cambiata. Copia di sicurezza in {bak}.",
        "en": "The previous file's narrative (graphs: {old}) did not travel into the new file "
              "(graphs: {new}): the file shape changed. Backup copy in {bak}."},
    "author_needs_name": {"it": "un autore ha bisogno di un nome",
                          "en": "an author needs a name"},
}


def set_language(lang: Optional[str]) -> None:
    LANGUAGE[0] = (lang or "it")[:2]


def msg(key: str, **kw) -> str:
    voce = _M[key]
    return voce.get(LANGUAGE[0], voce["en"]).format(**kw)


def _lang(lang: Optional[str]) -> str:
    return (lang or LANGUAGE[0] or "it")[:2]


class NarrativeError(RuntimeError):
    """Un motivo detto per l'utente, non un traceback."""


# ---------------------------------------------------------------------------
# L'AI già impostata
# ---------------------------------------------------------------------------

def llm_config(load: Optional[Callable[[str], Any]] = None):
    """``(config, scope)`` della prima impostazione AI usabile, o None.

    Usabile = ha un modello e, se il fornitore vuole la chiave, la chiave.
    ``load`` è ``LLMProviderManager.load_config`` (iniettabile per i test).
    """
    if load is None:
        from ..utility.llm_providers import LLMProviderManager
        load = LLMProviderManager.load_config
    for scope in SCOPES:
        try:
            cfg = load(scope)
        except Exception:                           # noqa: BLE001
            cfg = None
        if cfg is None or not str(getattr(cfg, "model", "") or "").strip():
            continue
        if getattr(cfg, "needs_api_key", False) and not getattr(cfg, "api_key", ""):
            continue
        return cfg, scope
    return None


def scope_label(scope: str, lang: Optional[str] = None) -> str:
    voce = _SCOPE_LABELS.get(scope) or {"it": scope, "en": scope}
    return voce.get(_lang(lang), voce["en"])


def describe_config(cfg, scope: str, lang: Optional[str] = None) -> str:
    voce = _M["model_label"]
    return voce.get(_lang(lang), voce["en"]).format(
        model=getattr(cfg, "model", "?"), scope=scope_label(scope, lang))


# ---------------------------------------------------------------------------
# Il progetto (il contenitore em.json)
# ---------------------------------------------------------------------------

def load_project(path):
    """``(Container, avvisi)`` del file, o NarrativeError con il nome del file."""
    from s3dgraphy.container import load_container_file
    try:
        return load_container_file(str(path))
    except Exception as e:                          # noqa: BLE001
        raise NarrativeError(msg("file_unreadable",
                                 name=os.path.basename(str(path)), err=e)) from e


def _reread(path: str) -> None:
    from s3dgraphy.container import load_container_file
    load_container_file(path)


def save_project(container, path) -> str:
    """Scrive in un file di lavoro accanto, lo rilegge, poi lo rinomina sul
    vero: un errore a metà (o un file che non si rilegge) lascia l'em.json
    di prima com'era."""
    from s3dgraphy.container import save_container_file
    percorso = str(path)
    lavoro = percorso + ".tmp"
    try:
        save_container_file(container, lavoro, bump=True)
        _reread(lavoro)
        os.replace(lavoro, percorso)
    except Exception as e:                          # noqa: BLE001
        try:
            os.remove(lavoro)
        except OSError:
            pass
        raise NarrativeError(msg("file_unwritable",
                                 name=os.path.basename(percorso), err=e)) from e
    return percorso


# ---------------------------------------------------------------------------
# La narrativa nel grafo
# ---------------------------------------------------------------------------

def narratives_of(graph) -> list:
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    return [n for n in (getattr(graph, "nodes", None) or [])
            if isinstance(n, NarrativeNode)]


def narrative_of(graph):
    trovate = narratives_of(graph)
    return trovate[0] if trovate else None


def scaffold(graph, lang: Optional[str] = None):
    """Lo scheletro dei capitoli (``site_story``), fuso con la narrativa che
    il grafo ha già. Il nodo entra nel grafo se è nuovo: la libreria lo
    restituisce soltanto. Una narrativa esistente tiene la sua lingua."""
    from s3dgraphy.narrative import build_narrative
    esistente = narrative_of(graph)
    lingua = ((esistente.data or {}).get("lang") if esistente else None) or _lang(lang)
    narrativa = build_narrative(graph, "site_story", lang=lingua, existing=esistente)
    if esistente is None:
        graph.add_node(narrativa)
    for cap in narrativa.chapters:
        if _prose(cap):
            drop_placeholders(cap)
    return narrativa


def is_placeholder(block) -> bool:
    return (getattr(block, "block_type", "") == "prose"
            and bool(PLACEHOLDER_RE.match(str(getattr(block, "text", "") or ""))))


def _prose(chapter, *, placeholders: bool = False) -> list:
    return [b for b in getattr(chapter, "blocks", None) or []
            if getattr(b, "block_type", "") == "prose"
            and is_placeholder(b) == placeholders]


def drop_placeholders(chapter) -> int:
    """Toglie i segnaposto del template da un capitolo che ha prosa vera:
    altrimenti gli export stampavano «[da scrivere: …]» davanti a ogni
    paragrafo generato (revisione del 2026-10-12)."""
    tenuti = [b for b in chapter.blocks if not is_placeholder(b)]
    tolti = len(chapter.blocks) - len(tenuti)
    chapter.blocks[:] = tenuti
    return tolti


def count_possible_chapters(graph) -> int:
    """Quanti capitoli farebbe lo scheletro: le epoche con almeno un'unità
    e le attività. Un'epoca vuota non ha storia e il template la salta."""
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    abitate = {e.edge_target for e in getattr(graph, "edges", None) or []
               if e.edge_type in ("has_first_epoch", "survive_in_epoch")}
    return sum(1 for n in getattr(graph, "nodes", None) or []
               if isinstance(n, ActivityNodeGroup)
               or (isinstance(n, EpochNode) and n.node_id in abitate))


def chapter_status(chapter) -> str:
    """``empty`` / ``ai_draft`` / ``ai_endorsed`` / ``human``: il peggiore
    vince, perché una bozza non convalidata va vista anche in un capitolo
    che ha già prosa scritta."""
    stati = [b.status for b in _prose(chapter)]
    if not stati:
        return "empty"
    if "ai_draft" in stati:
        return "ai_draft"
    if "ai_endorsed" in stati:
        return "ai_endorsed"
    return "human"


def name_of(graph) -> Callable[[str], Optional[str]]:
    """La funzione «nome del nodo» che gli esportatori della libreria
    vogliono per scrivere le menzioni."""
    def _nome(ref: str):
        nodo = graph.find_node_by_id(ref) if graph is not None else None
        if nodo is None:
            return None
        return str(getattr(nodo, "name", "") or ref)
    return _nome


def chapter_text(chapter,
                 name_of_fn: Optional[Callable[[str], Optional[str]]] = None) -> str:
    """La prosa del capitolo, menzioni scritte col nome; i segnaposto
    solo quando non c'è altro."""
    from s3dgraphy.nodes.narrative_node import plain_mentions
    blocchi = _prose(chapter) or _prose(chapter, placeholders=True)
    testi = [str(b.text or "").strip() for b in blocchi]
    testo = "\n\n".join(t for t in testi if t)
    if name_of_fn is not None:
        testo = plain_mentions(testo, name_of_fn)
    return testo


def chapter_unit_ids(chapter) -> List[str]:
    """Le unità di cui parla il capitolo: le menzioni della prosa, in ordine
    e senza doppioni; se non c'è prosa, gli embed «us» (le unità della
    fascia). Sono quelle da evidenziare sulla mappa (Enzo, 2026-10-12)."""
    from s3dgraphy.nodes.narrative_node import mentions_in
    ids: List[str] = []
    for b in _prose(chapter):
        for ref in mentions_in(b.text):
            if ref not in ids:
                ids.append(ref)
    if ids:
        return ids
    for b in getattr(chapter, "blocks", None) or []:
        if (getattr(b, "block_type", "") == "embed" and getattr(b, "view_type", "") == "us"
                and b.ref and b.ref not in ids):
            ids.append(b.ref)
    return ids


def chapter_html(chapter,
                 name_of_fn: Optional[Callable[[str], Optional[str]]] = None,
                 media_of: Optional[Callable[[str], list]] = None) -> str:
    """La prosa del capitolo in HTML: un paragrafo per blocco, e ogni
    menzione risolta diventa un link ``unit:<id>`` col nome dell'unità,
    così un clic la evidenzia sulla mappa. Il resto del testo si scappa.

    ``media_of(ref)`` → ``[(src, didascalia)]``: le immagini dell'unità,
    messe sotto il paragrafo in cui è nominata la prima volta (Enzo,
    2026-10-12: «le immagini delle US associate quando parlo di quella US»)."""
    import html as _html
    from urllib.parse import quote
    from s3dgraphy.nodes.narrative_node import MENTION_PATTERN
    blocchi = _prose(chapter) or _prose(chapter, placeholders=True)
    paragrafi = []
    mostrate: set = set()
    for b in blocchi:
        for pezzo in str(b.text or "").split("\n\n"):
            pezzo = pezzo.strip()
            if not pezzo:
                continue
            parti, pos, nuove = [], 0, []
            for m in MENTION_PATTERN.finditer(pezzo):
                parti.append(_html.escape(pezzo[pos:m.start()]))
                ref = m.group(1).strip()
                nome = name_of_fn(ref) if name_of_fn is not None else None
                if nome:
                    parti.append('<a href="unit:%s">%s</a>'
                                 % (quote(ref, safe=""), _html.escape(str(nome))))
                    if ref not in mostrate:
                        mostrate.add(ref)
                        nuove.append((ref, str(nome)))
                else:
                    parti.append(_html.escape(ref))
                pos = m.end()
            parti.append(_html.escape(pezzo[pos:]))
            paragrafi.append("<p>%s</p>" % "".join(parti).replace("\n", "<br>"))
            if media_of is None:
                continue
            for ref, nome in nuove:
                try:
                    immagini = list(media_of(ref) or [])
                except Exception:                   # noqa: BLE001
                    immagini = []
                if not immagini:
                    continue
                tag = " ".join('<img src="%s" height="110" title="%s">'
                               % (_html.escape(str(src), quote=True),
                                  _html.escape(str(did), quote=True))
                               for src, did in immagini)
                didascalie = ", ".join(_html.escape(str(did)) for _src, did in immagini)
                paragrafi.append('<p class="media">%s</p>' % tag)
                paragrafi.append('<p class="media-caption"><small><i>%s: %s</i></small></p>'
                                 % (_html.escape(nome), didascalie))
    return "\n".join(paragrafi)


def can_generate(graph, chapter) -> bool:
    """La libreria sa istruire il modello solo su un'epoca o un'attività."""
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    if getattr(chapter, "canonical", False) or not getattr(chapter, "anchor", None):
        return False
    nodo = graph.find_node_by_id(chapter.anchor)
    return isinstance(nodo, (EpochNode, ActivityNodeGroup))


def chapters_to_generate(graph, narrative, only_empty: bool = True) -> list:
    return [c for c in narrative.chapters
            if can_generate(graph, c)
            and (not only_empty or chapter_status(c) == "empty")]


@dataclass(frozen=True)
class ChapterView:
    graph_id: str
    narrative_id: str
    index: int
    title: str
    anchor: Optional[str]
    status: str
    text: str
    can_generate: bool
    truncated: bool = False
    #: La prosa con le menzioni come link ``unit:<id>`` (per la scheda).
    html: str = ""
    #: Le unità di cui parla il capitolo, da evidenziare sulla mappa.
    unit_ids: List[str] = field(default_factory=list)


def status_word(status: str, lang: Optional[str] = None) -> str:
    voce = _M.get("status_" + status) or {"it": status, "en": status}
    return voce.get(_lang(lang), voce["en"])


def overview(container, lang: Optional[str] = None,
             media_of: Optional[Callable[[str], list]] = None) -> List[ChapterView]:
    """I capitoli di tutte le narrative del contenitore, grafo per grafo.
    ``media_of`` come in :func:`chapter_html`."""
    viste: List[ChapterView] = []
    for graph_id, graph in (getattr(container, "graphs", None) or {}).items():
        nomi = name_of(graph)
        for narrativa in narratives_of(graph):
            for i, cap in enumerate(narrativa.chapters):
                troncato = any(bool((b.options or {}).get("truncated"))
                               for b in _prose(cap))
                viste.append(ChapterView(
                    graph_id=str(graph_id), narrative_id=narrativa.node_id,
                    index=i, title=str(cap.title), anchor=cap.anchor,
                    status=chapter_status(cap), text=chapter_text(cap, nomi),
                    can_generate=can_generate(graph, cap), truncated=troncato,
                    html=chapter_html(cap, nomi, media_of), unit_ids=chapter_unit_ids(cap)))
    return viste


# ---------------------------------------------------------------------------
# Il briefing per il modello
# ---------------------------------------------------------------------------

def _label(graph, node_id: str) -> str:
    nodo = graph.find_node_by_id(node_id)
    return str(getattr(nodo, "name", "") or node_id) if nodo is not None else str(node_id)


def oldest_first(graph, ids: Sequence[str]) -> list:
    """Le unità date, dalla più antica alla più recente, secondo gli archi
    stratigrafici fra loro (chi copre, taglia, riempie o è dopo è più
    recente). A parità resta l'ordine dato; un ciclo non ferma niente."""
    scelte = list(dict.fromkeys(ids))
    dentro = set(scelte)
    sotto_di: Dict[str, List[str]] = {i: [] for i in scelte}      # id → chi gli sta sotto
    for e in getattr(graph, "edges", None) or []:
        if (e.edge_type in YOUNGER_FIRST_KINDS and e.edge_source in dentro
                and e.edge_target in dentro and e.edge_source != e.edge_target):
            sotto_di[e.edge_source].append(e.edge_target)
    ordine: list = []
    visti: set = set()
    in_corso: set = set()

    def visita(uid):
        if uid in visti or uid in in_corso:
            return
        in_corso.add(uid)
        for sotto in sotto_di[uid]:                 # prima chi sta sotto
            visita(sotto)
        in_corso.discard(uid)
        visti.add(uid)
        ordine.append(uid)

    for uid in scelte:
        visita(uid)
    return ordine


def _relations_of(graph, uid: str) -> List[Dict[str, str]]:
    out = []
    for e in getattr(graph, "edges", None) or []:
        if e.edge_type not in YOUNGER_FIRST_KINDS + SYMMETRIC_KINDS:
            continue
        if uid not in (e.edge_source, e.edge_target):
            continue
        out.append({"kind": e.edge_type,
                    "subject": _label(graph, e.edge_source), "subject_id": e.edge_source,
                    "object": _label(graph, e.edge_target), "object_id": e.edge_target})
    return out


def _dedup(voci: list) -> list:
    viste, out = set(), []
    for v in voci:
        chiave = json.dumps(v, sort_keys=True, default=str)
        if chiave not in viste:
            viste.add(chiave)
            out.append(v)
    return out


def briefing(graph, anchor_id: str) -> Dict[str, Any]:
    """Il contesto della libreria, arricchito di quello che la libreria non
    porta e che fa la storia: i campi della scheda, i rapporti fra le
    unità, l'ordine dalla più antica."""
    from s3dgraphy.api import build_narrative_generation_context
    ctx = build_narrative_generation_context(graph, anchor_id)
    per_id = {a["id"]: a for a in ctx["actions"]}
    azioni = []
    for uid in oldest_first(graph, list(per_id)):
        a = dict(per_id[uid])
        nodo = graph.find_node_by_id(uid)
        dati = getattr(nodo, "data", None) or {}
        a["details"] = {en_: str(dati[it_]).strip() for it_, en_ in DETAIL_FIELDS
                        if str(dati.get(it_) or "").strip()}
        a["epochs"] = _dedup(a.get("epochs") or [])
        a["relations"] = _relations_of(graph, uid)
        azioni.append(a)
    omesse = max(0, len(azioni) - MAX_ACTIONS)
    return {**ctx, "actions": azioni[:MAX_ACTIONS], "order": "oldest_first",
            "omitted_actions": omesse}


_SYSTEM = {
    "it": ("Sei un archeologo che scrive la storia di un sito a partire dalla sua "
           "matrice stratigrafica. Scrivi in italiano, in prosa continua, da uno a "
           "tre paragrafi, per un lettore che non ha la matrice davanti. Le unità "
           "sono elencate dalla più antica alla più recente: racconta la sequenza "
           "in quell'ordine, usando i rapporti stratigrafici forniti. Quando nomini "
           "un'unità scrivi [[nome]] con il nome esatto che ti è dato, per esempio "
           "[[1.US38]]. Regole:"),
    "en": ("You are an archaeologist writing the story of a site from its "
           "stratigraphic matrix. Write in English, continuous prose, one to three "
           "paragraphs, for a reader who is not holding the matrix. The units are "
           "listed from the oldest to the most recent: tell the sequence in that "
           "order, using the stratigraphic relations given. When you name a unit "
           "write [[name]] with the exact name you were given, for example "
           "[[1.US38]]. Rules:"),
}

_USER_HEAD = {
    "it": "Capitolo «{title}» ({kind}). Unità dalla più antica alla più recente{omitted}. Contesto in JSON:\n",
    "en": "Chapter “{title}” ({kind}). Units from the oldest to the most recent{omitted}. Context as JSON:\n",
}
_OMITTED = {"it": " ({n} unità omesse per brevità)", "en": " ({n} units omitted for brevity)"}
_KIND = {"epoch": {"it": "epoca", "en": "epoch"}, "activity": {"it": "attività", "en": "activity"}}


def _prompt_lang(lang: Optional[str]) -> str:
    lingua = _lang(lang)
    return lingua if lingua in _SYSTEM else "en"


def _kind_word(brief, lang: str) -> str:
    voce = _KIND.get(brief.get("anchor_kind") or "epoch", _KIND["epoch"])
    return voce.get(lang, voce["en"])


def _system_text(brief, lang: str) -> str:
    testa = _SYSTEM.get(lang, _SYSTEM["en"])
    regole = "\n".join("- " + str(c) for c in brief.get("constraints") or [])
    return testa + "\n" + regole


#: Le chiavi che portano gli id delle unità: uuid lunghi, che il modello
#: non deve ripetere (cita per nome) e che costano token a ogni occorrenza
#: — un capitolo di 23 unità ne portava più di cento (2026-10-12).
_ID_KEYS = ("id", "subject_id", "object_id")


def _slim(valore):
    """Una copia senza gli id delle unità; le epoche tengono il loro
    (corto, e il modello non le cita)."""
    if isinstance(valore, dict):
        return {k: _slim(v) for k, v in valore.items()
                if not (k in _ID_KEYS and _looks_like_unit_id(valore))}
    if isinstance(valore, list):
        return [_slim(v) for v in valore]
    return valore


def _looks_like_unit_id(voce: dict) -> bool:
    """Le epoche (``relation``/``start``) e l'àncora tengono l'id."""
    return "relation" not in voce and "start" not in voce


def _corpo(brief: Dict[str, Any]) -> Dict[str, Any]:
    return _slim({k: brief[k] for k in ("activity", "actions", "epochs", "sources")
                  if k in brief})


def _misura(brief: Dict[str, Any], lang: Optional[str] = None) -> int:
    """Quanto è lungo il messaggio utente così com'è: intestazione compresa."""
    return len(messages(brief, lang)[1]["content"])


def _relations_once(azioni: List[Dict[str, Any]]) -> None:
    """Ogni rapporto una volta sola: nell'unità soggetto se è nel capitolo,
    altrimenti nell'oggetto. Elencato da tutte e due le parti raddoppiava."""
    dentro = {a["id"] for a in azioni}
    visti: set = set()
    for a in azioni:
        tenute = []
        for r in a.get("relations") or []:
            chiave = (r.get("kind"), r.get("subject_id"), r.get("object_id"))
            padrone = (r.get("subject_id") if r.get("subject_id") in dentro
                       else r.get("object_id"))
            if padrone != a["id"] or chiave in visti:
                continue
            visti.add(chiave)
            tenute.append(r)
        a["relations"] = tenute


def _accorcia(testo: Any, massimo: int = MAX_DETAIL_CHARS) -> Any:
    testo = str(testo)
    return testo if len(testo) <= massimo else testo[:massimo].rstrip() + "…"


def fit_briefing(brief: Dict[str, Any], budget: Optional[int] = None,
                 lang: Optional[str] = None) -> Dict[str, Any]:
    """Una copia del briefing il cui messaggio sta in ``budget`` caratteri
    (``MAX_PROMPT_CHARS`` se non detto).

    In ordine, finché serve: i rapporti una volta sola; i testi lunghi
    della scheda accorciati; via la catena di evidenza; meno unità, dalla
    fine (le più recenti), contate in ``omitted_actions``. L'originale
    non si tocca."""
    ridotto = dict(brief)
    ridotto["actions"] = [dict(a, relations=list(a.get("relations") or []),
                               details=dict(a.get("details") or {}))
                          for a in brief.get("actions") or []]
    ridotto["omitted_actions"] = int(brief.get("omitted_actions") or 0)
    budget = MAX_PROMPT_CHARS if budget is None else int(budget)
    if _misura(ridotto, lang) <= budget:
        return ridotto
    _relations_once(ridotto["actions"])
    if _misura(ridotto, lang) <= budget:
        return ridotto
    for a in ridotto["actions"]:
        a["details"] = {k: _accorcia(v) for k, v in a["details"].items()}
        if a.get("description"):
            a["description"] = _accorcia(a["description"])
    if _misura(ridotto, lang) <= budget:
        return ridotto
    for a in ridotto["actions"]:
        a.pop("evidence", None)
    while ridotto["actions"] and _misura(ridotto, lang) > budget:
        ridotto["actions"].pop()
        ridotto["omitted_actions"] += 1
    return ridotto


def messages(brief: Dict[str, Any], lang: Optional[str] = None) -> List[Dict[str, str]]:
    """I due messaggi per il modello: le istruzioni e il briefing in JSON.
    Chi vuole il tetto in caratteri passa prima da ``fit_briefing``."""
    lingua = _prompt_lang(lang)
    omesse = brief.get("omitted_actions") or 0
    testa = _USER_HEAD[lingua].format(
        title=(brief.get("activity") or {}).get("name") or "",
        kind=_kind_word(brief, lingua),
        omitted=_OMITTED[lingua].format(n=omesse) if omesse else "")
    return [{"role": "system", "content": _system_text(brief, lingua)},
            {"role": "user", "content": testa + json.dumps(_corpo(brief), ensure_ascii=False)}]


def prompt_record(brief: Dict[str, Any], lang: Optional[str] = None) -> str:
    """Quello che si registra nell'estrattore del prompt: le istruzioni e
    l'intestazione del capitolo con gli id delle unità — non il JSON intero,
    che gonfierebbe l'em.json a ogni capitolo."""
    lingua = _prompt_lang(lang)
    voce = _M["prompt_context"]
    testa = voce.get(lingua, voce["en"]).format(
        title=(brief.get("activity") or {}).get("name") or "",
        kind=_kind_word(brief, lingua),
        ids=", ".join(a["id"] for a in brief.get("actions") or []))
    omesse = brief.get("omitted_actions") or 0
    if omesse:
        testa += _OMITTED[lingua].format(n=omesse)
    return _system_text(brief, lingua) + "\n\n" + testa


def normalize_mentions(text: str, graph) -> str:
    """``[[x]]``: con ``x`` id del grafo resta; con ``x`` nome di un nodo
    diventa l'id; altrimenti restano le parole senza parentesi, così
    un'invenzione del modello non diventa una citazione che non risolve."""
    from s3dgraphy.nodes.narrative_node import MENTION_PATTERN
    nodi = getattr(graph, "nodes", None) or []
    ids = {n.node_id for n in nodi}
    per_nome = {str(getattr(n, "name", "") or "").strip().lower(): n.node_id
                for n in nodi if str(getattr(n, "name", "") or "").strip()}

    def _swap(m):
        ref = m.group(1).strip()
        if ref in ids:
            return "[[%s]]" % ref
        trovato = per_nome.get(ref.lower())
        return "[[%s]]" % trovato if trovato else ref

    return MENTION_PATTERN.sub(_swap, str(text or ""))


# ---------------------------------------------------------------------------
# La generazione
# ---------------------------------------------------------------------------

@dataclass
class Outcome:
    anchor: str
    title: str
    ok: bool
    text: str = ""
    error: str = ""
    truncated: bool = False


@dataclass
class Report:
    outcomes: List[Outcome] = field(default_factory=list)
    cancelled: bool = False

    @property
    def generated(self) -> int:
        return sum(1 for o in self.outcomes if o.ok)

    @property
    def failed(self) -> int:
        return sum(1 for o in self.outcomes if not o.ok)

    def summary(self, lang: Optional[str] = None) -> str:
        voce = _M["summary"]
        testo = voce.get(_lang(lang), voce["en"]).format(ok=self.generated, failed=self.failed)
        if self.cancelled:
            fine = _M["summary_cancelled"]
            testo += fine.get(_lang(lang), fine["en"])
        errori = [o for o in self.outcomes if not o.ok]
        if errori:
            testo += ": " + "; ".join("%s — %s" % (o.title, o.error) for o in errori[:3])
        return testo


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_chapter(graph, narrative, chapter, *, chat: Callable, model: str,
                     lang: Optional[str] = None, now: Optional[str] = None,
                     version: str = "", replace: bool = False) -> Outcome:
    """Un capitolo: briefing → modello → bozza nel grafo. Non alza mai:
    un capitolo che va male è un esito negativo, e gli altri continuano.

    ``replace``: le bozze AI non convalidate del capitolo lasciano il posto
    alla nuova — ma solo **dopo** che il modello ha risposto: una
    rigenerazione fallita tiene la bozza di prima (revisione 2026-10-12)."""
    anchor = str(getattr(chapter, "anchor", "") or "")
    titolo = str(getattr(chapter, "title", "") or anchor)
    try:
        brief = fit_briefing(briefing(graph, anchor), lang=lang)
        risposta = chat(messages(brief, lang))
        testo, troncato = (risposta if isinstance(risposta, tuple) else (risposta, False))
        testo = normalize_mentions(str(testo or "").strip(), graph)
        if not testo:
            raise NarrativeError(msg("empty_reply"))
        if replace:
            forget_ai_drafts(chapter)
        prima = {n.node_id for n in graph.nodes}
        from s3dgraphy.narrative import write_ai_draft
        write_ai_draft(graph, anchor, testo, model=str(model), version=version,
                       date=now or _now(), prompt=prompt_record(brief, lang),
                       narrative_id=narrative.node_id, chapter_title=titolo,
                       sources=[s["id"] for s in brief.get("sources") or []])
        if troncato:
            chapter.blocks[-1].options["truncated"] = True
        drop_placeholders(chapter)
        clean_author_placeholders(graph)
        try:
            from s3dgraphy.language import stamp_born_nodes
            stamp_born_nodes(graph, prima)
        except Exception:                           # noqa: BLE001
            pass
        return Outcome(anchor, titolo, True, text=testo, truncated=bool(troncato))
    except Exception as e:                          # noqa: BLE001
        return Outcome(anchor, titolo, False, error=str(e))


def forget_ai_drafts(chapter) -> int:
    """Toglie i blocchi AI non convalidati. Quelli che una persona ha
    firmato restano: la firma è un atto, non si cancella rigenerando."""
    tenuti = [b for b in chapter.blocks
              if not (getattr(b, "block_type", "") == "prose"
                      and getattr(b, "ai_generated", False)
                      and b.status == "ai_draft")]
    tolti = len(chapter.blocks) - len(tenuti)
    chapter.blocks[:] = tenuti
    return tolti


def generate(container, *, chat: Callable, model: str, lang: Optional[str] = None,
             anchors: Optional[Sequence[str]] = None, progress=None, cancelled=None,
             version: str = "") -> Report:
    """Tutti i grafi del contenitore. ``anchors=None``: i capitoli vuoti;
    ``anchors`` dati: quei capitoli, rigenerati (la bozza vecchia lascia il
    posto alla nuova solo se il modello risponde). Una voce di ``anchors``
    è ``(graph_id, anchor)`` — nell'esportazione per saggi i grafi hanno
    le STESSE epoche, e un'àncora sola avrebbe riscritto il capitolo in
    tutti — oppure una stringa, che vale per tutti i grafi.
    La prosa nasce nella lingua della narrativa (``data.lang``), quando ne
    dichiara una; altrimenti in quella chiesta. ``cancelled()`` si legge
    prima di ogni capitolo."""
    da_fare = []
    for graph_id, graph in (getattr(container, "graphs", None) or {}).items():
        narrativa = scaffold(graph, lang)
        lingua = (narrativa.data or {}).get("lang") or lang
        if anchors is None:
            scelti = chapters_to_generate(graph, narrativa, only_empty=True)
        else:
            voluti = {a for a in anchors if isinstance(a, str)}
            voluti |= {a[1] for a in anchors if not isinstance(a, str)
                       and str(a[0]) == str(graph_id)}
            scelti = [c for c in chapters_to_generate(graph, narrativa, only_empty=False)
                      if c.anchor in voluti]
        da_fare.extend((graph, narrativa, c, lingua) for c in scelti)
    rapporto = Report()
    for i, (graph, narrativa, cap, lingua) in enumerate(da_fare, 1):
        if cancelled is not None and cancelled():
            rapporto.cancelled = True
            break
        if progress is not None:
            progress(i, len(da_fare), str(cap.title))
        rapporto.outcomes.append(generate_chapter(
            graph, narrativa, cap, chat=chat, model=model, lang=lingua,
            version=version, replace=anchors is not None))
    return rapporto


# ---------------------------------------------------------------------------
# Convalida, autori, export
# ---------------------------------------------------------------------------

def human_authors(graph) -> List[Tuple[str, str]]:
    from s3dgraphy.nodes.author_node import AuthorAINode, AuthorNode
    return [(n.node_id, str(getattr(n, "name", "") or n.node_id))
            for n in (getattr(graph, "nodes", None) or [])
            if isinstance(n, AuthorNode) and not isinstance(n, AuthorAINode)]


def _slug(testo: str) -> str:
    return re.sub(r"[^\w]+", "_", str(testo).strip().lower(), flags=re.UNICODE).strip("_")


def add_author(graph, name: str) -> str:
    """L'autore umano con quel nome, creato se manca. Stesso schema di id
    dell'esportazione (``author::<nome>``). Senza il cognome segnaposto
    della libreria («nosurname»), che gli export stampavano."""
    from s3dgraphy.nodes.author_node import AuthorNode
    nome = str(name or "").strip()
    if not nome:
        raise NarrativeError(msg("author_needs_name"))
    for node_id, esistente in human_authors(graph):
        if esistente.strip().lower() == nome.lower():
            return node_id
    node_id = "author::" + _slug(nome)
    if graph.find_node_by_id(node_id) is None:
        graph.add_node(AuthorNode(node_id, name=nome, surname=""))
    return node_id


#: I segnaposto che la libreria mette a un autore senza cognome o ORCID.
_AUTHOR_PLACEHOLDERS = {"surname": "nosurname", "orcid": "noorcid"}


def clean_author_placeholders(graph) -> int:
    """Toglie «nosurname» (e «noorcid») dagli autori: gli export scrivevano
    «a cura di nosurname, Mario Rossi» e «con l'assistenza di nosurname,
    claude-…» (agente dei tutorial, 2026-10-12). Quanti autori puliti."""
    from s3dgraphy.nodes.author_node import AuthorNode
    puliti = 0
    for n in getattr(graph, "nodes", None) or []:
        if not isinstance(n, AuthorNode):
            continue
        toccato = False
        for campo, segnaposto in _AUTHOR_PLACEHOLDERS.items():
            if (getattr(n, "data", None) or {}).get(campo) == segnaposto:
                n.data[campo] = ""
                toccato = True
            if getattr(n, campo, None) == segnaposto:
                setattr(n, campo, "")
                toccato = True
        puliti += int(toccato)
    return puliti


def endorse(graph, narrative, author_id: str, anchor: Optional[str] = None) -> int:
    """Una persona firma le bozze AI: tutte, o quelle di un capitolo."""
    from s3dgraphy.nodes.narrative_node import endorse_block, endorse_narrative
    if anchor is None:
        return endorse_narrative(graph, narrative, author_id)
    cap = narrative.chapter_by_anchor(anchor)
    if cap is None:
        return 0
    firmati = 0
    for b in list(cap.blocks):
        if getattr(b, "block_type", "") == "prose" and getattr(b, "ai_generated", False) \
                and b.status == "ai_draft":
            endorse_block(graph, b, author_id)
            firmati += 1
    return firmati


EXPORT_FORMATS = ("html", "docx")


def export_file(graph, narrative, fmt: str, path, *,
                figures: Optional[Dict[str, bytes]] = None) -> str:
    """HTML o DOCX della narrativa, bozze comprese (segnate dalla libreria).
    ``figures`` (da :func:`figures_for`): le foto delle unità, che la
    libreria mette al posto della scheda dell'unità citata."""
    from s3dgraphy.api import export_narrative
    if fmt not in EXPORT_FORMATS:
        raise ValueError("fmt must be one of %s" % (EXPORT_FORMATS,))
    clean_author_placeholders(graph)
    opzioni = {"figures": dict(figures), "figure_suffix": ".png"} if figures else {}
    esito = export_narrative(graph, narrative.node_id, fmt, include_unvalidated=True,
                             **opzioni)
    payload = esito["payload"]
    percorso = str(path)
    if isinstance(payload, bytes):
        with open(percorso, "wb") as fh:
            fh.write(payload)
    else:
        with open(percorso, "w", encoding="utf-8") as fh:
            fh.write(str(payload))
    return percorso


# ---------------------------------------------------------------------------
# Conservare la narrativa quando il sito si riesporta
# ---------------------------------------------------------------------------

def is_support_node(node_type: str, node_id: str) -> bool:
    """I nodi che reggono la narrativa e non sono stratigrafia: la narrativa,
    l'autore AI, gli estrattori dei prompt."""
    tipo = str(node_type or "")
    return (tipo in ("narrative", "author_ai")
            or (tipo == "extractor"
                and str(node_id or "").startswith(PROMPT_EXTRACTOR_PREFIX)))


def _support_refs(narrative) -> List[str]:
    refs: List[str] = []
    for cap in narrative.chapters:
        if getattr(cap, "authored_by", None):
            refs.append(cap.authored_by)
        for b in cap.blocks:
            for ref in (getattr(b, "authored_by", None), getattr(b, "prompt_ref", None),
                        getattr(b, "validated_by", None)):
                if ref:
                    refs.append(ref)
    return list(dict.fromkeys(refs))


def carry_over(previous_graphs: Dict[str, Any], fresh_graphs: Dict[str, Any],
               lang: Optional[str] = None) -> int:
    """Porta nel grafo nuovo (stesso id) la narrativa del vecchio e quello
    che la regge, poi le dà un capitolo per ogni epoca nuova. Quante
    narrative portate."""
    portate = 0
    for graph_id, nuovo in (fresh_graphs or {}).items():
        vecchio = (previous_graphs or {}).get(graph_id)
        if vecchio is None:
            continue
        for narrativa in narratives_of(vecchio):
            if nuovo.find_node_by_id(narrativa.node_id) is not None:
                continue
            nuovo.add_node(narrativa)
            riferiti = set(_support_refs(narrativa))
            for e in vecchio.edges:
                if e.edge_source == narrativa.node_id and e.edge_type == "has_author":
                    riferiti.add(e.edge_target)
            for ref in riferiti:
                nodo = vecchio.find_node_by_id(ref)
                if nodo is not None and nuovo.find_node_by_id(ref) is None:
                    nuovo.add_node(nodo)
            for e in vecchio.edges:
                porta = ((e.edge_source == narrativa.node_id and e.edge_type == "has_author")
                         or (str(e.edge_source).startswith(PROMPT_EXTRACTOR_PREFIX)
                             and e.edge_type == "extracted_from"))
                if not porta:
                    continue
                if nuovo.find_node_by_id(e.edge_source) is None \
                        or nuovo.find_node_by_id(e.edge_target) is None:
                    continue
                if nuovo.find_edge_by_id(e.edge_id) is None:
                    nuovo.add_edge(e.edge_id, e.edge_source, e.edge_target, e.edge_type)
            scaffold(nuovo, lang)
            portate += 1
    return portate


# ---------------------------------------------------------------------------
# Le immagini delle unità: nel testo, nelle figure degli export, nel PDF
# ---------------------------------------------------------------------------

_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".JPG", ".PNG", ".tif", ".tiff")


def _resized_candidates(resize_base: str, ref) -> List[str]:
    """Dove sta la copia ridotta di un media: ``<id>_<nome>.<est>`` nella
    cartella delle ridotte (così le scrive il gestore dei media), oppure il
    nome del file originale."""
    out: List[str] = []
    if not resize_base:
        return out
    base = "%s_%s" % (ref.id_media, ref.name)
    for ext in _IMAGE_EXTS:
        out.append(os.path.join(resize_base, base + ext))
    if ref.original_file:
        out.append(os.path.join(resize_base, os.path.basename(str(ref.original_file))))
    return out


def unit_media_files(connection, unit, thumb_base: str, resize_base: str,
                     limit: int = MEDIA_PER_UNIT, prefer: str = "resized") -> List[str]:
    """Fino a ``limit`` file immagine dell'unità, esistenti sul disco: la copia
    ridotta se c'è, altrimenti l'anteprima (``prefer="thumb"`` inverte).
    Solo file locali: le anteprime remote non si incorporano."""
    if connection is None or unit is None:
        return []
    from ..utility.em_matrix_links import media_for_unit
    try:
        refs = media_for_unit(connection, unit, limit=max(int(limit), 1) * 3)
    except Exception:                               # noqa: BLE001
        return []
    trovati: List[str] = []
    for ref in refs:
        anteprima = [os.path.join(thumb_base, ref.thumb_file)] if (thumb_base and ref.thumb_file) else []
        ridotte = _resized_candidates(resize_base, ref)
        candidati = anteprima + ridotte if prefer == "thumb" else ridotte + anteprima
        for percorso in candidati:
            if os.path.isfile(percorso):
                trovati.append(percorso)
                break
        if len(trovati) >= limit:
            break
    return trovati


def compose_images(paths, height: int = IMAGE_HEIGHT, gap: int = IMAGE_GAP) -> Optional[bytes]:
    """Una striscia PNG con le immagini affiancate alla stessa altezza; un
    file illeggibile non ferma gli altri. ``None`` senza immagini."""
    try:
        from PIL import Image
    except Exception:                               # noqa: BLE001
        return None
    pezzi = []
    for percorso in paths or []:
        try:
            img = Image.open(percorso)
            img.load()
            img = img.convert("RGB")
            larghezza = max(1, int(round(img.width * height / float(img.height))))
            pezzi.append(img.resize((larghezza, height)))
        except Exception:                           # noqa: BLE001
            continue
    if not pezzi:
        return None
    totale = sum(p.width for p in pezzi) + gap * (len(pezzi) - 1)
    tela = Image.new("RGB", (totale, height), "white")
    x = 0
    for p in pezzi:
        tela.paste(p, (x, 0))
        x += p.width + gap
    buffer = io.BytesIO()
    tela.save(buffer, format="PNG")
    return buffer.getvalue()


def _mentioned_ids(chapter) -> List[str]:
    from s3dgraphy.nodes.narrative_node import mentions_in
    ids: List[str] = []
    for b in _prose(chapter):
        for ref in mentions_in(b.text):
            if ref not in ids:
                ids.append(ref)
    return ids


def figures_for(graph, narrative, connection, thumb_base: str, resize_base: str,
                per_unit: int = MEDIA_PER_UNIT, height: int = IMAGE_HEIGHT) -> Dict[str, bytes]:
    """Le figure per gli export della libreria: una striscia di immagini per
    ogni unità **citata nella prosa** che ha file sul disco, con la chiave
    ``us:<id>`` che la libreria cerca per l'embed dell'unità."""
    figure: Dict[str, bytes] = {}
    if connection is None:
        return figure
    for cap in narrative.chapters:
        for ref in _mentioned_ids(cap):
            chiave = "us:" + ref
            if chiave in figure:
                continue
            nodo = graph.find_node_by_id(ref)
            if nodo is None:
                continue
            file = unit_media_files(connection, nodo, thumb_base, resize_base, limit=per_unit)
            dati = compose_images(file, height=height) if file else None
            if dati:
                figure[chiave] = dati
    return figure


# ---------------------------------------------------------------------------
# Il PDF stampabile
# ---------------------------------------------------------------------------

_PDF = {
    "by": {"it": "a cura di", "en": "edited by"},
    "assist": {"it": "con l'assistenza di", "en": "with the assistance of"},
    "unvalidated": {"it": "Attenzione: {n} paragrafi sono bozze scritte dall'AI che nessuno ha ancora convalidato.",
                    "en": "Warning: {n} paragraphs are AI drafts nobody has endorsed yet."},
    "sources": {"it": "Fonti", "en": "Sources"},
    "page": {"it": "pagina {n}", "en": "page {n}"},
    "generated": {"it": "Generato da pyArchInit il {date}", "en": "Generated by pyArchInit on {date}"},
}
_FONTS = {"ok": None}


def _pdf_fonts():
    """Cambria dalla ``bin`` di pyArchInit se c'è (come gli altri PDF del
    plugin), altrimenti Helvetica. ``(normale, grassetto, corsivo)``."""
    if _FONTS["ok"] is not None:
        return _FONTS["ok"]
    scelta = ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique")
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from ..utility.pyarchinit_home import pyarchinit_home_bin
        cartella = pyarchinit_home_bin()
        normale = os.path.join(cartella, "Cambria.ttf")
        grassetto = os.path.join(cartella, "cambriab.ttf")
        corsivo = os.path.join(cartella, "cambriai.ttf")
        if os.path.isfile(normale):
            pdfmetrics.registerFont(TTFont("PyaCambria", normale))
            pdfmetrics.registerFont(TTFont("PyaCambriaB", grassetto if os.path.isfile(grassetto) else normale))
            pdfmetrics.registerFont(TTFont("PyaCambriaI", corsivo if os.path.isfile(corsivo) else normale))
            scelta = ("PyaCambria", "PyaCambriaB", "PyaCambriaI")
    except Exception:                               # noqa: BLE001
        pass
    _FONTS["ok"] = scelta
    return scelta


def export_pdf(graph, narrative, path, *, figures: Optional[Dict[str, bytes]] = None,
               lang: Optional[str] = None) -> str:
    """Il PDF stampabile della narrativa (A4): titolo, responsabili, capitoli,
    prosa con le menzioni scritte per nome, le foto delle unità citate
    (``figures``) con didascalia, le schede delle altre unità in piccolo,
    le fonti. Dallo stesso ``bake`` di HTML e DOCX, quindi dice le stesse
    cose."""
    import html as _html
    from datetime import date as _date
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                    SimpleDocTemplate, Spacer)
    from s3dgraphy.narrative.bake import bake_narrative
    from s3dgraphy.nodes.narrative_node import UNVALIDATED_NOTICE

    lingua = _prompt_lang(lang)
    clean_author_placeholders(graph)
    baked = bake_narrative(graph, narrative.node_id, figures=dict(figures or {}) or None,
                           figure_suffix=".png", include_unvalidated=True)
    normale, grassetto, corsivo = _pdf_fonts()
    stili = {
        "titolo": ParagraphStyle("t", fontName=grassetto, fontSize=20, leading=24, spaceAfter=6),
        "sotto": ParagraphStyle("s", fontName=corsivo, fontSize=9.5, leading=13,
                                textColor=colors.HexColor("#555555"), spaceAfter=4),
        "avviso": ParagraphStyle("a", fontName=grassetto, fontSize=9.5, leading=13,
                                 textColor=colors.HexColor("#8a2d00"), spaceAfter=8),
        "h2": ParagraphStyle("h", fontName=grassetto, fontSize=14, leading=18, spaceBefore=16,
                             spaceAfter=6, keepWithNext=1),
        "corpo": ParagraphStyle("c", fontName=normale, fontSize=10.5, leading=15,
                                alignment=TA_JUSTIFY, spaceAfter=6),
        "unita": ParagraphStyle("u", fontName=normale, fontSize=8.5, leading=11,
                                textColor=colors.HexColor("#444444"), leftIndent=8, spaceAfter=1),
        "didascalia": ParagraphStyle("d", fontName=corsivo, fontSize=9, leading=12,
                                     textColor=colors.HexColor("#333333"), spaceAfter=10),
        "nota": ParagraphStyle("n", fontName=corsivo, fontSize=9, leading=12,
                               textColor=colors.HexColor("#777777"), spaceAfter=4),
    }

    def _t(key, **kw):
        voce = _PDF[key]
        return voce.get(lingua, voce["en"]).format(**kw)

    def _p(testo, stile):
        return Paragraph(_html.escape(str(testo or "")).replace("\n", "<br/>"), stili[stile])

    documento = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                                  topMargin=2 * cm, bottomMargin=2 * cm,
                                  title=str(baked.title or ""), author=", ".join(baked.responsible))
    larghezza = documento.width
    storia = [_p(baked.title, "titolo")]
    if baked.description:
        storia.append(_p(baked.description, "sotto"))
    if baked.responsible:
        storia.append(_p("%s %s" % (_t("by"), ", ".join(baked.responsible)), "sotto"))
    if baked.assisting:
        storia.append(_p("%s %s" % (_t("assist"), ", ".join(baked.assisting)), "sotto"))
    if getattr(baked, "unvalidated", 0):
        storia.append(_p(_t("unvalidated", n=baked.unvalidated), "avviso"))
    storia.append(Spacer(1, 8))

    for capitolo in baked.chapters:
        storia.append(_p(capitolo.title, "h2"))
        for blocco in capitolo.blocks:
            tipo = getattr(blocco, "kind", "")
            if tipo == "prose":
                testo = blocco.plain_text
                if getattr(blocco, "unendorsed", False):
                    testo = UNVALIDATED_NOTICE + " " + testo
                storia.append(_p(testo, "corpo"))
            elif tipo == "image" and getattr(blocco, "image", None) is not None \
                    and blocco.image.resolved:
                try:
                    figura = Image(io.BytesIO(blocco.image.data))
                    rapporto = figura.imageHeight / float(figura.imageWidth or 1)
                    w = min(larghezza, figura.imageWidth)
                    h = w * rapporto
                    if h > 11 * cm:
                        h = 11 * cm
                        w = h / rapporto
                    figura.drawWidth, figura.drawHeight = w, h
                    storia.append(KeepTogether([figura, _p(blocco.text, "didascalia")]))
                except Exception:                   # noqa: BLE001
                    storia.append(_p(blocco.text, "nota"))
            elif tipo == "unit":
                storia.append(_p(blocco.text, "unita"))
            elif tipo == "citation":
                storia.append(_p(blocco.text, "nota"))
            else:
                storia.append(_p(getattr(blocco, "text", "") or tipo, "nota"))

    if baked.citations:
        storia.append(_p(_t("sources"), "h2"))
        for voce in baked.citations:
            titolo = voce.get("title") or voce.get("id") or ""
            dettagli = ", ".join(str(voce[k]) for k in ("author", "year") if voce.get(k))
            storia.append(_p(titolo + (" (%s)" % dettagli if dettagli else ""), "nota"))

    piede = _t("generated", date=_date.today().isoformat())

    def _pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont(normale, 8)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(2 * cm, 1.2 * cm, piede)
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, _t("page", n=doc.page))
        canvas.restoreState()

    documento.build(storia, onFirstPage=_pagina, onLaterPages=_pagina)
    return str(path)
