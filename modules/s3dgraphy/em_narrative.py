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
    "us_report": {"it": "Relazione AI della scheda US",
                  "en": "AI report of the US form"},
    "rag_query": {"it": "Interrogazione AI del database",
                  "en": "AI database query"},
    "palimpsest_report": {"it": "Relazione Palimpsest",
                          "en": "Palimpsest report"},
    "text2sql": {"it": "Testo in SQL", "en": "Text to SQL"},
}

#: Oltre tante unità il briefing si taglia: un capitolo di trecento US
#: non si racconta in un paragrafo, e un prompt enorme costa e confonde.
MAX_ACTIONS = 80

#: Quanto può scrivere il modello per capitolo.
MAX_TOKENS = 1800

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
    return narrativa


def is_placeholder(block) -> bool:
    return (getattr(block, "block_type", "") == "prose"
            and bool(PLACEHOLDER_RE.match(str(getattr(block, "text", "") or ""))))


def _prose(chapter, *, placeholders: bool = False) -> list:
    return [b for b in getattr(chapter, "blocks", None) or []
            if getattr(b, "block_type", "") == "prose"
            and is_placeholder(b) == placeholders]


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


def status_word(status: str, lang: Optional[str] = None) -> str:
    voce = _M.get("status_" + status) or {"it": status, "en": status}
    return voce.get(_lang(lang), voce["en"])


def overview(container, lang: Optional[str] = None) -> List[ChapterView]:
    """I capitoli di tutte le narrative del contenitore, grafo per grafo."""
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
                    can_generate=can_generate(graph, cap), truncated=troncato))
    return viste
