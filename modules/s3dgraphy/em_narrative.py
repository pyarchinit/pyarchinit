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
    "narrative_import_newer": {
        "it": "Narrativa del file precedente non conservata: l'em.json importato il {when} è più "
              "recente, e vale la sua. Copia di sicurezza del file precedente in {bak}.",
        "en": "The previous file's narrative was not kept: the em.json imported on {when} is "
              "newer, and its narrative wins. Backup copy of the previous file in {bak}."},
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


#: I titoli fissi del template ``site_story`` — la libreria li scrive in
#: italiano e in inglese, le altre lingue ricadono sull'inglese — e il nome
#: della narrativa nuova, nelle lingue di pyArchInit. Servono anche a
#: riconoscere lo stesso capitolo scritto in un'altra lingua: la libreria
#: fonde i capitoli senza àncora per titolo, e «Presentation» accanto a
#: «Presentazione» sarebbe un doppione.
_TITOLI_FISSI = {
    "presentation": {"en": "Presentation", "it": "Presentazione", "de": "Präsentation",
                     "fr": "Présentation", "es": "Presentación", "ca": "Presentació",
                     "pt": "Apresentação", "ro": "Prezentare", "el": "Παρουσίαση",
                     "ar": "تقديم"},
    "where": {"en": "Where it is", "it": "Dove si trova", "de": "Wo es liegt",
              "fr": "Où il se trouve", "es": "Dónde se encuentra", "ca": "On es troba",
              "pt": "Onde se encontra", "ro": "Unde se află", "el": "Πού βρίσκεται",
              "ar": "أين يقع"},
}
_STORIA_DEL_SITO = {"de": "{site} — die Geschichte des Ortes", "fr": "{site} — l'histoire du site",
                    "es": "{site} — la historia del sitio", "ca": "{site} — la història del jaciment",
                    "pt": "{site} — a história do sítio", "ro": "{site} — povestea sitului",
                    "el": "{site} — η ιστορία του χώρου", "ar": "{site} — قصة الموقع"}
_LINGUE_DEL_TEMPLATE = ("it", "en")


def _chiave_titolo(titolo) -> Optional[str]:
    testo = str(titolo or "").strip()
    for chiave, voci in _TITOLI_FISSI.items():
        if testo in voci.values():
            return chiave
    return None


def _from_template(narrative) -> bool:
    """Nata dal template ``site_story`` o completata con lui («Prepara i
    capitoli» → «Aggiungi»): la libreria lo scrive in ``template_id``."""
    return bool((getattr(narrative, "data", None) or {}).get("template_id"))


def needs_template_choice(graph) -> bool:
    """La narrativa è quella che il file porta di suo (TempluMare: i
    capitoli di Emanuel, nessun template): prima di aggiungerle i capitoli
    di pyArchInit si chiede (Enzo, 17 ottobre 2026)."""
    n = narrative_of(graph)
    return n is not None and bool(n.chapters) and not _from_template(n)


def scaffold(graph, lang: Optional[str] = None, *, write_lang: Optional[str] = None):
    """Lo scheletro dei capitoli (``site_story``), fuso con la narrativa che
    il grafo ha già. Il nodo entra nel grafo se è nuovo: la libreria lo
    restituisce soltanto. I capitoli nuovi sono nella lingua scelta
    (``write_lang``), altrimenti in quella della narrativa, altrimenti in
    ``lang``; quelli che ci sono non si ritraducono, e lo stesso capitolo
    fisso in un'altra lingua non si aggiunge una seconda volta. Su una
    narrativa del file aggiunge i capitoli di pyArchInit: è la scelta
    «Aggiungi» di «Prepara i capitoli» (vedi :func:`ensure_narrative`)."""
    from s3dgraphy.narrative.registry import get_template, merge_narrative
    esistente = narrative_of(graph)
    lingua = str(write_lang or ((esistente.data or {}).get("lang") if esistente else None)
                 or _lang(lang))[:2].lower()
    bozza = get_template("site_story")(graph, lang=lingua)
    if lingua not in _LINGUE_DEL_TEMPLATE:
        for cap in bozza.chapters:
            chiave = None if cap.anchor else _chiave_titolo(cap.title)
            if chiave:
                cap.title = _TITOLI_FISSI[chiave].get(lingua, cap.title)
        if esistente is None and lingua in _STORIA_DEL_SITO:
            bozza.name = _STORIA_DEL_SITO[lingua].format(
                site=str(getattr(graph, "name", None) or graph.graph_id))
    if esistente is None:
        narrativa = bozza
        graph.add_node(narrativa)
    else:
        for cap in bozza.chapters:
            chiave = None if cap.anchor else _chiave_titolo(cap.title)
            gemello = next((c for c in esistente.chapters if chiave and not c.anchor
                            and _chiave_titolo(c.title) == chiave), None)
            if gemello is not None:
                cap.title = gemello.title           # la libreria li fonde per titolo
        narrativa = merge_narrative(esistente, bozza)
    for cap in narrativa.chapters:
        if _prose(cap):
            drop_placeholders(cap)
        prose_first(cap)
    return narrativa


def ensure_narrative(graph, lang: Optional[str] = None, *, write_lang: Optional[str] = None):
    """La narrativa pronta per generare o per viaggiare con una
    riesportazione: creata dal template se manca, fatta crescere (le epoche
    e le attività nuove) se è del template. Quella che il file porta di suo
    resta com'è: i capitoli di pyArchInit li aggiunge solo «Prepara i
    capitoli», quando lo si chiede — prima li aggiungevano anche «Genera»
    e ogni riesportazione (Enzo, 17 ottobre 2026: «mi dà altri capitoli che
    non sono in linea con quelli del template»)."""
    esistente = narrative_of(graph)
    if esistente is None or _from_template(esistente):
        return scaffold(graph, lang, write_lang=write_lang)
    return esistente


def is_placeholder(block) -> bool:
    return (getattr(block, "block_type", "") == "prose"
            and bool(PLACEHOLDER_RE.match(str(getattr(block, "text", "") or ""))))


def _prose(chapter, *, placeholders: bool = False) -> list:
    return [b for b in getattr(chapter, "blocks", None) or []
            if getattr(b, "block_type", "") == "prose"
            and is_placeholder(b) == placeholders]


def prose_first(chapter) -> None:
    """La prosa davanti, gli embed (le schede delle unità) dopo, nell'ordine
    che avevano. La libreria accoda la bozza in fondo, e negli export la
    storia usciva dopo le schede di tutte le unità del capitolo."""
    blocchi = list(getattr(chapter, "blocks", None) or [])
    prosa = [b for b in blocchi if getattr(b, "block_type", "") == "prose"]
    altri = [b for b in blocchi if getattr(b, "block_type", "") != "prose"]
    chapter.blocks[:] = prosa + altri


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


#: La chiave con cui la scheda e :func:`generate` indicano la «Presentazione»,
#: il capitolo canonico della libreria che non ha un'ancora nel grafo
#: (13 ottobre 2026: «la presentazione non viene inserita»).
PRESENTATION_KEY = "presentation"


def _scritto_da_una_persona(chapter) -> bool:
    return any(not getattr(b, "ai_generated", False) for b in _prose(chapter))


def is_presentation(narrative, chapter) -> bool:
    """La «Presentazione» che ``site_story`` apre con il segnaposto
    «presentazione di …»: canonica e senza àncora, in una narrativa del
    template. È quella col titolo fisso, in qualunque lingua — in una
    narrativa del file completata con i capitoli di pyArchInit sta in fondo
    —, altrimenti il primo capitolo (rinominato), se non l'ha scritto una
    persona. Il primo capitolo di una narrativa del file non lo è mai: in
    TempluMare era l'introduzione di Emanuel, e «Rigenera» ci avrebbe
    scritto sopra una presentazione dell'AI (17 ottobre 2026)."""
    if not getattr(chapter, "canonical", False) or getattr(chapter, "anchor", None):
        return False
    if not _from_template(narrative):
        return False
    capitoli = list(getattr(narrative, "chapters", None) or [])
    col_titolo = [c for c in capitoli if getattr(c, "canonical", False)
                  and not getattr(c, "anchor", None) and _chiave_titolo(c.title) == "presentation"]
    if col_titolo:
        return chapter is col_titolo[0]
    return bool(capitoli) and chapter is capitoli[0] and not _scritto_da_una_persona(chapter)


def chapter_key(narrative, chapter) -> Optional[str]:
    """L'ancora del capitolo, o :data:`PRESENTATION_KEY` per la Presentazione;
    ``None`` per gli altri capitoli canonici («Dove si trova»)."""
    if getattr(chapter, "anchor", None):
        return str(chapter.anchor)
    return PRESENTATION_KEY if is_presentation(narrative, chapter) else None


def chapter_by_key(narrative, key):
    if key == PRESENTATION_KEY:
        return next((c for c in getattr(narrative, "chapters", None) or []
                     if is_presentation(narrative, c)), None)
    return narrative.chapter_by_anchor(key)


def can_generate(graph, chapter, narrative=None) -> bool:
    """La libreria sa istruire il modello su un'epoca o un'attività; la
    Presentazione la istruiamo noi (:func:`site_briefing`), quindi si
    genera anche lei quando si sa quale narrativa la contiene."""
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    if narrative is not None and is_presentation(narrative, chapter):
        return True
    if getattr(chapter, "canonical", False) or not getattr(chapter, "anchor", None):
        return False
    nodo = graph.find_node_by_id(chapter.anchor)
    return isinstance(nodo, (EpochNode, ActivityNodeGroup))


def chapters_to_generate(graph, narrative, only_empty: bool = True) -> list:
    return [c for c in narrative.chapters
            if can_generate(graph, c, narrative)
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
                    index=i, title=str(cap.title), anchor=chapter_key(narrativa, cap),
                    status=chapter_status(cap), text=chapter_text(cap, nomi),
                    can_generate=can_generate(graph, cap, narrativa), truncated=troncato,
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


#: Le lingue di pyArchInit che non hanno istruzioni proprie: si danno
#: quelle inglesi, chiedendo la lingua per nome.
_NOMI_DELLE_LINGUE = {"de": "German", "fr": "French", "es": "Spanish", "ca": "Catalan",
                      "pt": "Portuguese", "ro": "Romanian", "el": "Greek", "ar": "Arabic"}


def _scrivi_in(testo: str, lang: Optional[str]) -> str:
    nome = _NOMI_DELLE_LINGUE.get(_lang(lang))
    return testo.replace("Write in English", "Write in %s" % nome) if nome else testo


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
    return [{"role": "system", "content": _scrivi_in(_system_text(brief, lingua), lang)},
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
    return _scrivi_in(_system_text(brief, lingua), lang) + "\n\n" + testa


# ---------------------------------------------------------------------------
# La Presentazione: briefing del sito, prompt, bozza in un capitolo senza ancora
# ---------------------------------------------------------------------------

#: L'ordine dei livelli della catena dei toponimi, dal più largo al sito.
_TOPONYM_LEVELS = ("nazione", "regione", "provincia", "comune", "sito")


def _is_unit(node) -> bool:
    try:
        from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
    except Exception:                               # noqa: BLE001
        return False
    return isinstance(node, StratigraphicNode) and type(node).__name__ != "ContinuityNode"


def _study_id(graph) -> str:
    for n in getattr(graph, "nodes", None) or []:
        if type(n).__name__ == "StudyNode":
            return str(n.node_id)
    return ""


def _site_name(graph) -> str:
    for n in getattr(graph, "nodes", None) or []:
        if type(n).__name__ == "StudyNode" and str(getattr(n, "name", "") or "").strip():
            return str(n.name).strip()
    nome = getattr(graph, "name", None)
    if isinstance(nome, str) and nome.strip():
        return nome.strip()
    return str(getattr(graph, "graph_id", "") or "")


def _toponym_level(node) -> str:
    """«Administrative level: comune» → ``comune``; «Site» → ``sito``."""
    descrizione = str(getattr(node, "description", "") or "")
    if ":" in descrizione:
        return descrizione.split(":", 1)[1].strip().lower()
    return "sito" if descrizione.strip().lower() == "site" else descrizione.strip().lower()


def _place_field(node) -> str:
    """``loc::area::study::1`` → ``area``; senza quello schema, il ``kind``."""
    parti = str(getattr(node, "node_id", "") or "").split("::")
    if len(parti) >= 4 and parti[0] == "loc":
        return parti[1]
    return str(getattr(node, "kind", "") or "")


def site_briefing(graph, narrative) -> Dict[str, Any]:
    """Il briefing per la Presentazione: che cos'è il sito e dove sta, le
    epoche dalla più antica, quante unità e di che tipo, i luoghi della
    scheda (aree, settori, saggi, ambienti), i documenti, chi ha lavorato,
    i capitoli del racconto. Tutto dal grafo: niente database."""
    from s3dgraphy.nodes.document_node import DocumentNode
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.group_node import LocationNodeGroup
    nodi = list(getattr(graph, "nodes", None) or [])
    archi = list(getattr(graph, "edges", None) or [])
    unita = [n for n in nodi if _is_unit(n)]
    per_tipo: Dict[str, int] = {}
    for n in unita:
        tipo = str(getattr(n, "node_type", "") or type(n).__name__)
        per_tipo[tipo] = per_tipo.get(tipo, 0) + 1
    epoche = []
    for e in sorted((n for n in nodi if isinstance(n, EpochNode)),
                    key=lambda n: (getattr(n, "start_time", None) is None,
                                   getattr(n, "start_time", 0) or 0,
                                   getattr(n, "end_time", 0) or 0)):
        quante = sum(1 for a in archi if a.edge_target == e.node_id
                     and a.edge_type in ("has_first_epoch", "survive_in_epoch"))
        epoche.append({"name": str(e.name), "start": getattr(e, "start_time", None),
                       "end": getattr(e, "end_time", None), "units_present": quante})
    toponimi, luoghi = [], {}
    for n in nodi:
        if not isinstance(n, LocationNodeGroup):
            continue
        if getattr(n, "kind", "") == "toponym":
            toponimi.append({"level": _toponym_level(n), "name": str(n.name)})
        else:
            luoghi.setdefault(_place_field(n), []).append(str(n.name))
    toponimi.sort(key=lambda t: (_TOPONYM_LEVELS.index(t["level"])
                                 if t["level"] in _TOPONYM_LEVELS else len(_TOPONYM_LEVELS)))
    documenti = [{"name": str(n.name), "description": str(getattr(n, "description", "") or "")}
                 for n in nodi if isinstance(n, DocumentNode)]
    documenti.sort(key=lambda d: d["name"])
    rapporti = sum(1 for a in archi
                   if a.edge_type in YOUNGER_FIRST_KINDS or a.edge_type in SYMMETRIC_KINDS)
    return {
        "site": _site_name(graph),
        "toponyms": toponimi,
        "places": {k: sorted(v) for k, v in luoghi.items()},
        # «units_present»: nate o sopravvissute in quell'epoca — una unità vive
        # in più epoche, quindi la somma supera il totale (il modello lo
        # prendeva per un'incoerenza da segnalare, 13 ottobre 2026).
        "epochs": epoche,
        "epochs_note": "a unit can be present in more than one epoch: the sums exceed the total",
        "units": {"total": len(unita), "by_type": per_tipo, "relations": rapporti},
        "documents": documenti,
        "authors": [nome for _, nome in human_authors(graph)],
        "chapters": [str(c.title) for c in getattr(narrative, "chapters", None) or []
                     if getattr(c, "anchor", None)],
    }


def _fit_site(brief: Dict[str, Any], budget: Optional[int] = None) -> Dict[str, Any]:
    """Il briefing del sito entro il tetto in caratteri: testi dei documenti
    accorciati, poi gli elenchi lunghi dimezzati finché ci sta."""
    tetto = MAX_PROMPT_CHARS if budget is None else budget
    b = json.loads(json.dumps(brief, ensure_ascii=False))
    for d in b.get("documents") or []:
        d["description"] = _accorcia(d.get("description") or "")
    while len(json.dumps(b, ensure_ascii=False)) > tetto:
        lunghi = [(k, v) for k, v in (b.get("places") or {}).items() if len(v) > 2]
        if b.get("documents") and len(b["documents"]) > 2:
            b["documents"] = b["documents"][:max(2, len(b["documents"]) // 2)]
        elif lunghi:
            k, v = max(lunghi, key=lambda kv: len(kv[1]))
            b["places"][k] = v[:max(2, len(v) // 2)]
        elif b.get("epochs") and len(b["epochs"]) > 2:
            b["epochs"] = b["epochs"][:max(2, len(b["epochs"]) // 2)]
        else:
            break
    return b


_SYSTEM_PRESENTATION = {
    "it": ("Sei un archeologo che presenta un sito di scavo a chi sta per leggerne la "
           "storia, ricostruita dalla matrice stratigrafica. Scrivi in italiano, in prosa "
           "continua, da due a quattro paragrafi. Di' che cos'è il sito e dove si trova; "
           "quali epoche copre la storia, dalla più antica alla più recente, e quante unità "
           "stratigrafiche la compongono; come si legge questo racconto: un capitolo per "
           "epoca e uno per attività, con le unità citate per nome, e le bozze scritte da un "
           "modello segnate come tali finché una persona non le convalida; e su quali fonti "
           "si appoggia: le schede delle unità con i loro rapporti stratigrafici, i documenti "
           "elencati, le fotografie. Usa solo i dati del briefing: non inventare date, "
           "luoghi o fatti. Presenta, non revisionare: se un dato ti sembra strano o "
           "incoerente, lascia fuori quel dettaglio invece di commentarlo. Non usare le "
           "doppie parentesi quadre."),
    "en": ("You are an archaeologist introducing an excavation site to someone about to "
           "read its story, reconstructed from the stratigraphic matrix. Write in English, "
           "continuous prose, two to four paragraphs. Say what the site is and where it "
           "lies; which epochs the story covers, from the oldest to the most recent, and how "
           "many stratigraphic units make it up; how this story is read: one chapter per "
           "epoch and one per activity, units cited by name, and drafts written by a model "
           "marked as such until a person endorses them; and which sources it rests on: the "
           "unit records with their stratigraphic relations, the documents listed, the "
           "photographs. Use only the briefing: invent no dates, places or facts. Present, "
           "do not review: if a datum looks odd or inconsistent, leave that detail out "
           "rather than commenting on it. Do not use double square brackets."),
}
_PRESENTATION_HEAD = {
    "it": "Presentazione del sito «{site}». Briefing in JSON:\n",
    "en": "Presentation of the site “{site}”. Briefing as JSON:\n",
}


def presentation_messages(brief: Dict[str, Any], lang: Optional[str] = None) -> List[Dict[str, str]]:
    lingua = _prompt_lang(lang)
    testa = _PRESENTATION_HEAD[lingua].format(site=brief.get("site") or "")
    return [{"role": "system", "content": _scrivi_in(_SYSTEM_PRESENTATION[lingua], lang)},
            {"role": "user", "content": testa + json.dumps(brief, ensure_ascii=False)}]


def presentation_prompt_record(brief: Dict[str, Any], lang: Optional[str] = None) -> str:
    """Quello che si registra nell'estrattore: le istruzioni, il sito e i
    nomi dei documenti — non il JSON intero."""
    lingua = _prompt_lang(lang)
    testa = _PRESENTATION_HEAD[lingua].format(site=brief.get("site") or "").strip()
    fonti = ", ".join(d.get("name") or "" for d in brief.get("documents") or [])
    return (_scrivi_in(_SYSTEM_PRESENTATION[lingua], lang) + "\n\n" + testa
            + (" " + fonti if fonti else ""))


def write_ai_prose_in_chapter(graph, narrative, chapter, text: str, *, model: str,
                              version: str = "", date: Optional[str] = None,
                              prompt: str = "", sources: Optional[List[str]] = None,
                              based_on: str = ""):
    """La bozza del modello in un capitolo che non ha un'ancora: le stesse
    tre cose di ``write_ai_draft`` della libreria — autore AI, prompt
    registrato come estrattore legato alle fonti, blocco non convalidato —
    che però vuole l'ancora per trovare il capitolo."""
    from s3dgraphy.narrative import ensure_ai_author, register_prompt_extractor
    autore = ensure_ai_author(graph, model=str(model), version=version)
    estrattore = (register_prompt_extractor(graph, prompt, sources=list(sources or []),
                                            based_on=based_on) if prompt else None)
    blocco = chapter.add_ai_prose(text.strip(), author_id=autore.node_id,
                                  prompt_ref=estrattore.node_id if estrattore else None)
    if date:
        blocco.options["generated_at"] = date
    if version:
        blocco.options["model_version"] = version
    arco = "%s_has_author_%s" % (narrative.node_id, autore.node_id)
    if not graph.find_edge_by_id(arco):
        graph.add_edge(arco, narrative.node_id, autore.node_id, "has_author")
    return blocco


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
    presentazione = is_presentation(narrative, chapter)
    anchor = PRESENTATION_KEY if presentazione else str(getattr(chapter, "anchor", "") or "")
    titolo = str(getattr(chapter, "title", "") or anchor)
    try:
        if presentazione:
            brief = _fit_site(site_briefing(graph, narrative))
            risposta = chat(presentation_messages(brief, lang))
        else:
            brief = fit_briefing(briefing(graph, anchor), lang=lang)
            risposta = chat(messages(brief, lang))
        testo, troncato = (risposta if isinstance(risposta, tuple) else (risposta, False))
        testo = normalize_mentions(str(testo or "").strip(), graph)
        if not testo:
            raise NarrativeError(msg("empty_reply"))
        if replace:
            forget_ai_drafts(chapter)
        prima = {n.node_id for n in graph.nodes}
        if presentazione:
            fonti = [str(b.ref) for b in chapter.blocks
                     if getattr(b, "block_type", "") == "embed" and getattr(b, "ref", None)]
            write_ai_prose_in_chapter(graph, narrative, chapter, testo, model=str(model),
                                      version=version, date=now or _now(),
                                      prompt=presentation_prompt_record(brief, lang),
                                      sources=fonti, based_on=_study_id(graph))
        else:
            from s3dgraphy.narrative import write_ai_draft
            write_ai_draft(graph, anchor, testo, model=str(model), version=version,
                           date=now or _now(), prompt=prompt_record(brief, lang),
                           narrative_id=narrative.node_id, chapter_title=titolo,
                           sources=[s["id"] for s in brief.get("sources") or []])
        if troncato:
            chapter.blocks[-1].options["truncated"] = True
        drop_placeholders(chapter)
        prose_first(chapter)
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
             version: str = "", write_lang: Optional[str] = None) -> Report:
    """Tutti i grafi del contenitore. ``anchors=None``: i capitoli vuoti;
    ``anchors`` dati: quei capitoli, rigenerati (la bozza vecchia lascia il
    posto alla nuova solo se il modello risponde). Una voce di ``anchors``
    è ``(graph_id, anchor)`` — nell'esportazione per saggi i grafi hanno
    le STESSE epoche, e un'àncora sola avrebbe riscritto il capitolo in
    tutti — oppure una stringa, che vale per tutti i grafi.
    La prosa nasce nella lingua scelta nel pannello (``write_lang``);
    senza scelta in quella della narrativa (``data.lang``), quando ne
    dichiara una; altrimenti in quella chiesta. Una narrativa del file non
    prende capitoli nuovi (:func:`ensure_narrative`). ``cancelled()`` si
    legge prima di ogni capitolo."""
    da_fare = []
    for graph_id, graph in (getattr(container, "graphs", None) or {}).items():
        narrativa = ensure_narrative(graph, lang, write_lang=write_lang)
        lingua = write_lang or (narrativa.data or {}).get("lang") or lang
        if anchors is None:
            scelti = chapters_to_generate(graph, narrativa, only_empty=True)
        else:
            voluti = {a for a in anchors if isinstance(a, str)}
            voluti |= {a[1] for a in anchors if not isinstance(a, str)
                       and str(a[0]) == str(graph_id)}
            scelti = [c for c in chapters_to_generate(graph, narrativa, only_empty=False)
                      if chapter_key(narrativa, c) in voluti]
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
    cap = chapter_by_key(narrative, anchor)
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

#: Aggiunta in coda al foglio di stile della libreria. La libreria chiude
#: ogni bozza non convalidata in un riquadro grigio, con un carattere più
#: piccolo e senza grazie: sul telefono «le scritte si vedono opache»
#: (Enzo, 13 ottobre 2026). Restano l'avviso «non validato da una persona»
#: e il filetto ambra a sinistra; il testo è quello del resto della pagina.
HTML_DRAFT_CSS = """
/* pyArchInit: la bozza si legge come il resto della pagina */
.em-embed.em-unendorsed {
  background: transparent; border: 0; border-left: 3px solid #d08b00;
  border-radius: 0; padding: 0 0 0 .9rem; margin: 1.1rem 0;
  font: inherit; color: inherit;
}
"""


def export_file(graph, narrative, fmt: str, path, *,
                figures: Optional[Dict[str, bytes]] = None,
                map_conn: Optional[str] = None, lang: Optional[str] = None,
                media_base: Optional[Tuple[str, str]] = None) -> str:
    """HTML o DOCX della narrativa, bozze comprese (segnate dalla libreria).
    ``figures`` (da :func:`figures_for`): le foto delle unità, che la
    libreria mette al posto della scheda dell'unità citata. Con ``map_conn``
    (la connessione al database del progetto) l'HTML porta la **mappa
    interattiva** delle unità (:mod:`em_narrative_map`): un clic sul nome
    di un'unità la evidenzia e mostra solo quelle del periodo del capitolo;
    senza disegni o senza database l'HTML resta quello della libreria.
    Con i file dei proxy nel database l'HTML porta anche la **scena 3D**
    (:mod:`em_narrative_3d`), nella stessa scheda della mappa
    (:mod:`em_narrative_views`).
    L'HTML porta anche l'**indice** e le **fonti come hotspot**
    (:mod:`em_narrative_html`); ``media_base`` — le cartelle (miniature,
    ridotte) del progetto — serve a trovare i file dei documenti."""
    from s3dgraphy.api import export_narrative
    if fmt not in EXPORT_FORMATS:
        raise ValueError("fmt must be one of %s" % (EXPORT_FORMATS,))
    clean_author_placeholders(graph)
    opzioni = {"figures": dict(figures), "figure_suffix": ".png"} if figures else {}
    esito = export_narrative(graph, narrative.node_id, fmt, include_unvalidated=True,
                             **opzioni)
    payload = esito["payload"]
    if fmt == "html":
        payload = str(payload).replace("</style>", HTML_DRAFT_CSS + "</style>", 1)
        if map_conn:
            try:
                from . import em_narrative_map as nmap
                from . import em_narrative_views as nviews
                capitoli = [{"title": str(getattr(c, "title", "") or ""),
                             "epoch": nmap.epoch_anchor(graph, c),
                             "units": chapter_unit_ids(c)} for c in narrative.chapters]
                payload = nviews.html_with_views(payload, graph, map_conn, _site_name(graph), capitoli, lang,
                                                 resize_base=str((media_base or ("", ""))[1] or ""))
            except Exception as e:                  # noqa: BLE001
                import logging
                logging.getLogger(__name__).warning("Mappa e scena 3D della narrativa non aggiunte: %s", e)
        payload = _html_per_chi_legge(payload, graph, narrative, map_conn, media_base, lang)
    elif fmt == "docx":
        try:
            from . import em_narrative_html as nh
            payload = nh.improve_docx(bytes(payload), graph, narrative, lang)
        except Exception as e:                      # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Indice e fonti del DOCX non aggiunti: %s", e)
    percorso = str(path)
    if isinstance(payload, bytes):
        with open(percorso, "wb") as fh:
            fh.write(payload)
    else:
        with open(percorso, "w", encoding="utf-8") as fh:
            fh.write(str(payload))
    return percorso


def _html_per_chi_legge(payload: str, graph, narrative, conn, media_base, lang) -> str:
    """I media scelti dentro i capitoli, le fonti come hotspot e l'indice
    (17 ottobre 2026). Un inciampo non porta via l'esportazione: la pagina
    resta com'era, e lo si scrive nel log."""
    import logging
    from . import em_narrative_html as nh
    from . import em_narrative_media as nm
    registro: Dict[str, dict] = {}
    titoli = [str(getattr(c, "title", "") or "") for c in narrative.chapters]
    ordine = nh.align_chapters(payload, titoli)

    def allineati(liste):
        return [liste[i] if i is not None and i < len(liste) else [] for i in ordine]
    # le fonti per prime: i loro documenti stanno anche nelle tabelle delle unità
    per_capitolo: List[List[str]] = []
    try:
        per_capitolo, fonti = nh.sources_for_chapters(graph, narrative)
        if fonti:
            miniature, ridotte = media_base or ("", "")
            registro.update(nh.sources_registry(graph, fonti, conn, miniature, ridotte))
    except Exception as e:                          # noqa: BLE001
        logging.getLogger(__name__).warning("Fonti della narrativa non trovate: %s", e)
    try:
        payload = nh.group_units(payload, graph, narrative, ordine, registro, lang)
    except Exception as e:                          # noqa: BLE001
        logging.getLogger(__name__).warning("Unità della narrativa non raggruppate: %s", e)
    try:
        per_media, voci_media = nm.media_registry(graph, narrative, conn, media_base or ("", ""))
        if voci_media:
            payload = nm.add_media(payload, allineati(per_media), voci_media, lang)
            registro.update(voci_media)
    except Exception as e:                          # noqa: BLE001
        logging.getLogger(__name__).warning("Media della narrativa non aggiunti: %s", e)
    try:
        if registro:
            payload = nh.add_sources(payload, allineati(per_capitolo), registro, lang)
    except Exception as e:                          # noqa: BLE001
        logging.getLogger(__name__).warning("Fonti della narrativa non aggiunte: %s", e)
    try:
        payload = nh.add_index(payload, lang)
    except Exception as e:                          # noqa: BLE001
        logging.getLogger(__name__).warning("Indice della narrativa non aggiunto: %s", e)
    return payload


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
               lang: Optional[str] = None, *, replace: bool = False) -> int:
    """Porta nel grafo nuovo (stesso id) la narrativa del vecchio e quello
    che la regge, poi — se è del template — le dà un capitolo per ogni
    epoca nuova. Quante narrative portate.

    ``replace``: se il grafo nuovo ha già una narrativa con lo stesso id —
    quella che la memoria dell'em.json importato rimette nell'esportazione —
    il vecchio file la sostituisce. Chi decide quale delle due è più
    recente è :func:`em_export._keep_narrative`."""
    portate = 0
    for graph_id, nuovo in (fresh_graphs or {}).items():
        vecchio = (previous_graphs or {}).get(graph_id)
        if vecchio is None:
            continue
        for narrativa in narratives_of(vecchio):
            if nuovo.find_node_by_id(narrativa.node_id) is not None:
                if not replace:
                    continue
                nuovo.remove_node(narrativa.node_id)
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
            ensure_narrative(nuovo, lang)
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
    "unvalidated_one": {"it": "Attenzione: {n} paragrafo è una bozza scritta dall'AI che nessuno ha ancora convalidato.",
                        "en": "Warning: {n} paragraph is an AI draft nobody has endorsed yet."},
    "sources": {"it": "Fonti", "en": "Sources"},
    "chapter_sources": {"it": "Fonti del capitolo", "en": "Chapter sources"},
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
    from reportlab.platypus.tableofcontents import TableOfContents
    from . import em_narrative_html as nh
    from s3dgraphy.narrative.bake import bake_narrative
    from s3dgraphy.nodes.narrative_node import UNVALIDATED_MARK, UNVALIDATED_NOTICE

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
        "h3": ParagraphStyle("h3", fontName=grassetto, fontSize=11.5, leading=15, spaceBefore=10,
                             spaceAfter=4, keepWithNext=1),
        "indice": ParagraphStyle("i", fontName=grassetto, fontSize=14, leading=18, spaceAfter=8),
        "corpo": ParagraphStyle("c", fontName=normale, fontSize=10.5, leading=15,
                                alignment=TA_JUSTIFY, spaceAfter=6),
        "unita": ParagraphStyle("u", fontName=normale, fontSize=8.5, leading=11,
                                textColor=colors.HexColor("#444444"), leftIndent=8, spaceAfter=1),
        "didascalia": ParagraphStyle("d", fontName=corsivo, fontSize=9, leading=12,
                                     textColor=colors.HexColor("#333333"), spaceAfter=10),
        "nota": ParagraphStyle("n", fontName=corsivo, fontSize=9, leading=12,
                               textColor=colors.HexColor("#777777"), spaceAfter=4),
        "avviso_blocco": ParagraphStyle("ab", fontName=corsivo, fontSize=9, leading=12,
                                        textColor=colors.HexColor("#8a2d00"), spaceAfter=2),
    }

    def _t(key, **kw):
        voce = _PDF[key]
        return voce.get(lingua, voce["en"]).format(**kw)

    def _p(testo, stile):
        return Paragraph(_html.escape(str(testo or "")).replace("\n", "<br/>"), stili[stile])

    # L'indice (17 ottobre 2026): ogni titolo di capitolo e ogni sottotitolo
    # dice alla pagina dove è finito, e il PDF ne ricava l'indice con i
    # numeri di pagina e i segnalibri.
    class _Documento(SimpleDocTemplate):
        def afterFlowable(self, flowable):
            livello = getattr(flowable, "_pya_livello", None)
            if livello is None:
                return
            testo = flowable.getPlainText()
            self.canv.bookmarkPage(flowable._pya_chiave)
            self.canv.addOutlineEntry(testo, flowable._pya_chiave, level=livello, closed=False)
            self.notify("TOCEntry", (livello, testo, self.page, flowable._pya_chiave))

    contatore = [0]

    def _titolo(testo, stile, livello):
        par = _p(testo, stile)
        contatore[0] += 1
        par._pya_livello, par._pya_chiave = livello, "pya-%d" % contatore[0]
        return par

    def _in_linea(testo):
        """Il corsivo e il grassetto del Markdown, come li fa la libreria
        nell'HTML: con i caratteri del PDF, non con <i> (non c'è famiglia)."""
        sicuro = _html.escape(str(testo or ""))
        for marca, carattere in (("**", grassetto), ("*", corsivo)):
            parti = sicuro.split(marca)
            if len(parti) > 2:
                fuori = parti[0]
                for i in range(1, len(parti)):
                    fuori += ('<font name="%s">%s</font>' % (carattere, parti[i]) if i % 2 else parti[i])
                sicuro = fuori
        return sicuro.replace("\n", "<br/>")

    def _prosa(testo):
        """Un paragrafo per paragrafo; «### titolo» è un sottotitolo."""
        fuori = []
        for paragrafo in re.split(r"\n\s*\n", str(testo or "")):
            paragrafo = paragrafo.strip()
            if not paragrafo:
                continue
            m = re.match(r"^(#{2,4})\s+(.+)$", paragrafo, re.S)
            if m:
                fuori.append(_titolo(m.group(2).strip(), "h3", 1))
            else:
                fuori.append(Paragraph(_in_linea(paragrafo), stili["corpo"]))
        return fuori

    try:
        per_capitolo, fonti = nh.sources_for_chapters(graph, narrative)
    except Exception:                               # noqa: BLE001
        per_capitolo, fonti = [], {}
    ordine = nh.align_titles([str(c.title or "") for c in baked.chapters],
                             [str(getattr(c, "title", "") or "") for c in narrative.chapters])

    documento = _Documento(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
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
    # `pending_validation` è il nome della libreria (dev45); `unvalidated`
    # non esisteva e l'avviso non usciva mai (agente dei tutorial, 2026-10-12).
    in_sospeso = int(getattr(baked, "pending_validation", 0) or getattr(baked, "unvalidated", 0) or 0)
    if in_sospeso:
        storia.append(_p(_t("unvalidated_one" if in_sospeso == 1 else "unvalidated", n=in_sospeso), "avviso"))
    storia.append(Spacer(1, 8))
    indice = TableOfContents()
    indice.levelStyles = [
        ParagraphStyle("toc0", fontName=normale, fontSize=10.5, leading=14, leftIndent=0,
                       firstLineIndent=0),
        ParagraphStyle("toc1", fontName=normale, fontSize=9.5, leading=12.5, leftIndent=14,
                       firstLineIndent=0, textColor=colors.HexColor("#444444")),
    ]
    storia.append(_p(nh._INDICE.get(_lang(lang), nh._INDICE["en"]), "indice"))
    storia.append(indice)
    storia.append(PageBreak())

    for k, capitolo in enumerate(baked.chapters):
        storia.append(_titolo(capitolo.title, "h2", 0))
        for blocco in capitolo.blocks:
            tipo = getattr(blocco, "kind", "")
            if tipo == "prose":
                if getattr(blocco, "unendorsed", False):
                    # Su una riga sua, in corsivo, senza il simbolo ⚠ che
                    # Cambria non ha: attaccato alla prima frase si leggeva male.
                    storia.append(_p(UNVALIDATED_NOTICE.replace(UNVALIDATED_MARK, "").strip(),
                                     "avviso_blocco"))
                storia.extend(_prosa(blocco.plain_text))
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
        ids = per_capitolo[ordine[k]] if k < len(ordine) and ordine[k] is not None else []
        if ids:
            voci = ["%s%s" % (fonti[d].name, " (%s)" % fonti[d].description if fonti[d].description else "")
                    for d in ids]
            storia.append(_p("%s: %s" % (_t("chapter_sources"), " · ".join(voci)), "nota"))

    gia = set()
    if baked.citations or fonti:
        storia.append(_titolo(_t("sources"), "h2", 0))
    for voce in baked.citations:
        titolo = voce.get("title") or voce.get("id") or ""
        gia.add(str(titolo))
        dettagli = ", ".join(str(voce[k]) for k in ("author", "year") if voce.get(k))
        storia.append(_p(titolo + (" (%s)" % dettagli if dettagli else ""), "nota"))
    for fonte in fonti.values():
        if fonte.name not in gia:
            storia.append(_p(fonte.name + (" (%s)" % fonte.description if fonte.description else ""),
                             "nota"))

    piede = _t("generated", date=_date.today().isoformat())

    def _pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont(normale, 8)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(2 * cm, 1.2 * cm, piede)
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, _t("page", n=doc.page))
        canvas.restoreState()

    documento.multiBuild(storia, onFirstPage=_pagina, onLaterPages=_pagina)
    return str(path)
