# Narrativa con l'AI nel pannello della matrice — piano

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dal pannello della matrice, far scrivere all'AI già impostata la narrativa del sito (capitoli di epoca e attività) dentro lo stesso em.json che EMStudio apre, con lettura, convalida umana, export HTML/DOCX e conservazione a ogni riesportazione.

**Architecture:** un modulo puro `modules/s3dgraphy/em_narrative.py` (chat iniettata, zero Qt) sopra `s3dgraphy.narrative` (scheletro, briefing, `write_ai_draft`, convalida, export); una scheda Qt `em_narrative_tab.py` nel pannello della matrice; cablaggio in `em_matrix_panel`, `em_export` (carry-over) e `pyarchinitPlugin` (file persistente, bottoni).

**Tech Stack:** Python 3.9 (QGIS), PyQt5, s3dgraphy 1.6.0.dev45 (`ext_libs`), `LLMProviderManager` (`modules/utility/llm_providers.py`), python-docx 1.1.2 (`ext_libs`), pytest.

**Spec:** `docs/superpowers/specs/2026-10-12-narrativa-ai-design.md`

## Global Constraints

- Ramo `Stratigraph_00001` soltanto; nessuna attribuzione AI nei commit; nessun segreto nel repo.
- Il modulo puro non importa Qt né SDK di modelli: la chiamata al modello è `chat(messages) -> str | (str, bool)`.
- Si usa `s3dgraphy.narrative.write_ai_draft` (accetta `sources`), non `s3dgraphy.api.write_ai_draft`.
- Stringhe utente it/en: nel modulo puro `set_language`/`msg`, nella scheda `_L`/`_t()` (modello: `tabs/Sam_Segmentation_Dialog.py`).
- Comando dei test: `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python QGIS_PREFIX_PATH=/Applications/QGIS.app/Contents/MacOS /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest <file> -q -p no:warnings` (la suite intera: `tests/sync tests/utility tests/migrations --continue-on-collection-errors --ignore=tests/sync/test_groups_dialog_smoke.py --ignore=tests/sync/test_paradata_dialog_smoke.py`).
- `ext_libs` deve precedere site-packages (il conftest di `tests/sync` lo fa; negli script a mano `PYTHONPATH="$PWD/ext_libs:$PWD:…"` e **mai** `python3 -I`).
- Versione finale `5.13.106-alpha`, tag `narrativa-ai-5.13.106-alpha`.

## Review Focus

1. Un em.json con **più grafi** (esportazione per saggi): ogni grafo ha la sua narrativa, l'elenco le mostra con il nome del grafo, il carry-over le conserva tutte. Prova in Task 4 (`con_saggi`).
2. Una narrativa scritta in **un'altra lingua** da EMStudio: `scaffold` non la ritraduce (usa `data.lang` della narrativa). Prova in Task 1.
3. Un capitolo con **molte unità** (oltre `MAX_ACTIONS`): il briefing si taglia e lo dice, il modello riceve comunque un JSON valido. Prova in Task 2.
4. Un **salvataggio che fallisce** a metà: il file precedente resta intatto. Prova in Task 1 (rilettura del `.tmp` che fallisce → il file originale non cambia).
5. Un **nodo del prompt** (`EXT.prompt.*`) nel file: non viene disegnato nella matrice né contato negli avvisi. Prova in Task 4.

---

### Task 1: modulo puro — configurazione, progetto, scheletro, stati, panoramica

**Files:**
- Create: `modules/s3dgraphy/em_narrative.py`
- Test: `tests/utility/test_em_narrative.py`

**Interfaces:**
- Produces: `SCOPES`, `llm_config(load=None)`, `scope_label(scope, lang=None)`, `describe_config(cfg, scope, lang=None)`, `NarrativeError`, `load_project(path)`, `save_project(container, path)`, `narratives_of(graph)`, `narrative_of(graph)`, `scaffold(graph, lang=None)`, `is_placeholder(block)`, `chapter_status(chapter)`, `chapter_text(chapter, name_of=None)`, `can_generate(graph, chapter)`, `chapters_to_generate(graph, narrative, only_empty=True)`, `ChapterView`, `overview(container, lang=None)`, `set_language`, `msg`, `name_of(graph)`.

- [ ] **Step 1: scrivere i test (falliscono: il modulo non esiste)**

```python
"""La narrativa dell'Extended Matrix: il modulo puro (2026-10-12)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import em_narrative as en  # noqa: E402


def grafo_di_prova():
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.author_node import AuthorNode
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit

    g = Graph(graph_id="Villa")
    g.add_node(EpochNode("epoch_1_1", "Età romana", -100, 300))
    g.add_node(EpochNode("epoch_2_1", "Medioevo", 500, 1400))
    unita = (
        ("u1", "1.US1", "epoch_2_1", {"us": "1", "area": "1", "unita_tipo": "US",
                                      "d_stratigrafica": "strato di crollo",
                                      "periodo_iniziale": "2", "fase_iniziale": "1"}),
        ("u2", "1.US2", "epoch_1_1", {"us": "2", "area": "1", "unita_tipo": "USM",
                                      "d_stratigrafica": "muro",
                                      "d_interpretativa": "muro perimetrale"}),
        ("u3", "1.US3", "epoch_1_1", {"us": "3", "area": "1", "unita_tipo": "US",
                                      "d_stratigrafica": "pavimento"}),
    )
    for uid, nome, epoca, dati in unita:
        n = StratigraphicUnit(uid, nome, description=dati["d_stratigrafica"])
        n.data = dict(dati)
        g.add_node(n)
        g.add_edge(uid + "_fe", uid, epoca, "has_first_epoch")
        g.add_edge(uid + "_fe_bis", uid, epoca, "has_first_epoch")   # doppione, come nell'export vero
    g.add_edge("u1_overlies_u2", "u1", "u2", "overlies")
    g.add_edge("u2_overlies_u3", "u2", "u3", "overlies")
    g.add_node(AuthorNode("author::mario_rossi", name="Mario Rossi"))
    return g


class _Cfg:
    def __init__(self, model="m", key="k", needs_key=True):
        self.model, self.api_key, self.needs_api_key = model, key, needs_key
        self.provider = type("P", (), {"value": "openai"})()


def test_llm_config_legge_gli_scope_in_ordine_e_scarta_quelle_inutilizzabili():
    salvate = {"rag_query": _Cfg(model="rag"), "us_report": _Cfg(model="", key="k")}
    trovato = en.llm_config(load=lambda scope: salvate.get(scope))
    assert trovato is not None and trovato[0].model == "rag" and trovato[1] == "rag_query"
    senza_chiave = {"us_report": _Cfg(model="x", key="")}
    assert en.llm_config(load=lambda s: senza_chiave.get(s)) is None
    locale = {"text2sql": _Cfg(model="llama", key="", needs_key=False)}
    assert en.llm_config(load=lambda s: locale.get(s))[1] == "text2sql"
    assert en.llm_config(load=lambda s: None) is None
    assert "Relazione AI" in en.scope_label("us_report", "it")
    assert "report" in en.scope_label("us_report", "en").lower()
    assert "rag" in en.describe_config(_Cfg(model="rag"), "rag_query", "it")


def test_scaffold_aggiunge_la_narrativa_una_volta_sola_e_rispetta_la_sua_lingua():
    g = grafo_di_prova()
    n1 = en.scaffold(g, "it")
    assert en.narrative_of(g) is n1
    assert [c.anchor for c in n1.chapters if c.anchor] == ["epoch_1_1", "epoch_2_1"]
    assert n1.data.get("lang") == "it"
    n2 = en.scaffold(g, "en")                    # seconda chiamata: fonde, non duplica
    assert n2 is n1 and len(en.narratives_of(g)) == 1
    assert n1.chapters[0].title == "Presentazione"   # non ritradotto in inglese


def test_segnaposto_stati_e_testo_del_capitolo():
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    cap = n.chapter_by_anchor("epoch_1_1")
    assert en.is_placeholder(cap.blocks[0])
    assert en.chapter_status(cap) == "empty"
    assert "da scrivere" in en.chapter_text(cap)
    cap.add_prose("Prosa scritta a mano su [[u2]].")
    assert en.chapter_status(cap) == "human"
    assert en.chapter_text(cap, en.name_of(g)) == "Prosa scritta a mano su 1.US2."
    assert en.can_generate(g, cap)
    assert not en.can_generate(g, n.chapters[0])            # Presentazione: canonico, senza àncora
    assert [c.anchor for c in en.chapters_to_generate(g, n)] == ["epoch_2_1"]
    assert [c.anchor for c in en.chapters_to_generate(g, n, only_empty=False)] == ["epoch_1_1", "epoch_2_1"]


def test_save_project_e_atomico_e_rilegge(tmp_path, monkeypatch):
    from s3dgraphy.container import container_of, load_container_file

    g = grafo_di_prova()
    en.scaffold(g, "it")
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(g), percorso)
    cont, _ = en.load_project(percorso)
    assert en.narratives_of(cont.active())
    assert not (tmp_path / "villa.em.json.tmp").exists()
    prima = percorso.read_bytes()

    # Il file di lavoro non si rilegge → l'originale non si tocca.
    monkeypatch.setattr(en, "_reread", lambda p: (_ for _ in ()).throw(ValueError("rotto")))
    with pytest.raises(en.NarrativeError):
        en.save_project(container_of(g), percorso)
    assert percorso.read_bytes() == prima
    assert not (tmp_path / "villa.em.json.tmp").exists()


def test_load_project_dice_il_nome_del_file_quando_non_si_legge(tmp_path):
    rotto = tmp_path / "rotto.em.json"
    rotto.write_text("{non json", encoding="utf-8")
    with pytest.raises(en.NarrativeError) as e:
        en.load_project(rotto)
    assert "rotto.em.json" in str(e.value)


def test_overview_elenca_i_capitoli_con_stato_e_grafo():
    from s3dgraphy.container import container_of

    g = grafo_di_prova()
    en.scaffold(g, "it")
    viste = en.overview(container_of(g), "it")
    assert [v.title for v in viste][:1] == ["Presentazione"]
    assert {v.graph_id for v in viste} == {"Villa"}
    assert [v.status for v in viste] == ["empty", "empty", "empty"]
    assert [v.can_generate for v in viste] == [False, True, True]
    assert en.overview(container_of(grafo_di_prova()), "it") == []
```

- [ ] **Step 2: eseguire i test → FAIL** (`ModuleNotFoundError: modules.s3dgraphy.em_narrative`).

- [ ] **Step 3: scrivere il modulo (prima parte)**

```python
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


def chapter_text(chapter, name_of_fn: Optional[Callable[[str], Optional[str]]] = None) -> str:
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
```

- [ ] **Step 4: eseguire i test → PASS** (6 passati).

- [ ] **Step 5: commit** `git add modules/s3dgraphy/em_narrative.py tests/utility/test_em_narrative.py && git commit -m "feat(narrativa): modulo puro — AI già impostata, progetto em.json, scheletro, stati, panoramica"`

---

### Task 2: briefing arricchito, messaggi, prompt registrato, menzioni

**Files:**
- Modify: `modules/s3dgraphy/em_narrative.py`
- Test: `tests/utility/test_em_narrative.py`

**Interfaces:**
- Consumes: Task 1.
- Produces: `briefing(graph, anchor_id) -> dict`, `messages(brief, lang=None) -> list`, `prompt_record(brief, lang=None) -> str`, `normalize_mentions(text, graph) -> str`, `oldest_first(graph, ids) -> list`.

- [ ] **Step 1: test (falliscono)**

```python
def test_briefing_porta_campi_della_scheda_rapporti_e_ordine_dalla_piu_antica():
    g = grafo_di_prova()
    b = en.briefing(g, "epoch_1_1")
    assert [a["id"] for a in b["actions"]] == ["u3", "u2"]        # u2 copre u3: u3 è più antica
    u2 = b["actions"][1]
    assert u2["details"]["unit_type"] == "USM"
    assert u2["details"]["interpretive_definition"] == "muro perimetrale"
    assert len(u2["epochs"]) == 1                                   # doppioni tolti
    assert {"kind": "overlies", "subject": "1.US2", "subject_id": "u2",
            "object": "1.US3", "object_id": "u3"} in u2["relations"]
    assert {"kind": "overlies", "subject": "1.US1", "subject_id": "u1",
            "object": "1.US2", "object_id": "u2"} in u2["relations"]   # anche con unità fuori capitolo
    assert b["order"] == "oldest_first" and b["omitted_actions"] == 0
    assert b["anchor_kind"] == "epoch" and b["constraints"]


def test_briefing_si_taglia_oltre_max_actions(monkeypatch):
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = grafo_di_prova()
    for i in range(10, 20):
        n = StratigraphicUnit("u%d" % i, "1.US%d" % i)
        n.data = {"us": str(i)}
        g.add_node(n)
        g.add_edge("u%d_fe" % i, "u%d" % i, "epoch_1_1", "has_first_epoch")
    monkeypatch.setattr(en, "MAX_ACTIONS", 4)
    b = en.briefing(g, "epoch_1_1")
    assert len(b["actions"]) == 4 and b["omitted_actions"] == 8
    json.dumps(b)                                                  # resta serializzabile


def test_messaggi_nella_lingua_con_vincoli_e_regola_delle_menzioni():
    g = grafo_di_prova()
    b = en.briefing(g, "epoch_1_1")
    it = en.messages(b, "it")
    assert [m["role"] for m in it] == ["system", "user"]
    assert "italiano" in it[0]["content"].lower()
    assert "[[" in it[0]["content"] and "id" in it[0]["content"]
    assert b["constraints"][0] in it[0]["content"]
    assert "Età romana" in it[1]["content"] and '"u3"' in it[1]["content"]
    en_ = en.messages(b, "en")
    assert "english" in en_[0]["content"].lower()
    record = en.prompt_record(b, "it")
    assert "u3, u2" in record and '"details"' not in record       # il JSON intero non va nel file


def test_normalize_mentions_tiene_gli_id_traduce_i_nomi_toglie_il_resto():
    g = grafo_di_prova()
    testo = "Sopra [[u3]] sta [[1.US2]] e poi [[ 1.us1 ]]; [[zz]] non esiste."
    assert en.normalize_mentions(testo, g) == "Sopra [[u3]] sta [[u2]] e poi [[u1]]; zz non esiste."
```

- [ ] **Step 2: eseguire → FAIL** (`AttributeError: briefing`).

- [ ] **Step 3: implementazione**

```python
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
    piu_recenti: Dict[str, set] = {i: set() for i in scelte}     # id → chi gli sta sopra
    for e in getattr(graph, "edges", None) or []:
        if e.edge_type in YOUNGER_FIRST_KINDS and e.edge_source in dentro and e.edge_target in dentro:
            piu_recenti[e.edge_target].add(e.edge_source)
    ordine: list = []
    visti: set = set()
    in_corso: set = set()

    def visita(uid):
        if uid in visti or uid in in_corso:
            return
        in_corso.add(uid)
        # prima chi sta sotto: le unità coperte da uid (uid è fra i «più recenti» di loro)
        for sotto in [t for t, sopra in piu_recenti.items() if uid in sopra]:
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
           "un'unità scrivi [[id]] con l'id esatto che ti è dato (non il nome). "
           "Regole:"),
    "en": ("You are an archaeologist writing the story of a site from its "
           "stratigraphic matrix. Write in English, continuous prose, one to three "
           "paragraphs, for a reader who is not holding the matrix. The units are "
           "listed from the oldest to the most recent: tell the sequence in that "
           "order, using the stratigraphic relations given. When you name a unit "
           "write [[id]] with the exact id you were given (not the name). Rules:"),
}

_USER_HEAD = {
    "it": "Capitolo «{title}» ({kind}). Unità dalla più antica alla più recente{omitted}. Contesto in JSON:\n",
    "en": "Chapter “{title}” ({kind}). Units from the oldest to the most recent{omitted}. Context as JSON:\n",
}
_OMITTED = {"it": " ({n} unità omesse per brevità)", "en": " ({n} units omitted for brevity)"}
_KIND = {"epoch": {"it": "epoca", "en": "epoch"}, "activity": {"it": "attività", "en": "activity"}}


def _kind_word(brief, lang: str) -> str:
    voce = _KIND.get(brief.get("anchor_kind") or "epoch", _KIND["epoch"])
    return voce.get(lang, voce["en"])


def _system_text(brief, lang: str) -> str:
    testa = _SYSTEM.get(lang, _SYSTEM["en"])
    regole = "\n".join("- " + str(c) for c in brief.get("constraints") or [])
    return testa + "\n" + regole


def messages(brief: Dict[str, Any], lang: Optional[str] = None) -> List[Dict[str, str]]:
    lingua = _lang(lang)
    lingua = lingua if lingua in _SYSTEM else "en"
    omesse = brief.get("omitted_actions") or 0
    testa = _USER_HEAD[lingua].format(
        title=(brief.get("activity") or {}).get("name") or "",
        kind=_kind_word(brief, lingua),
        omitted=_OMITTED[lingua].format(n=omesse) if omesse else "")
    corpo = {k: brief[k] for k in ("activity", "actions", "epochs", "sources") if k in brief}
    return [{"role": "system", "content": _system_text(brief, lingua)},
            {"role": "user", "content": testa + json.dumps(corpo, ensure_ascii=False)}]


def prompt_record(brief: Dict[str, Any], lang: Optional[str] = None) -> str:
    """Quello che si registra nell'estrattore del prompt: le istruzioni e
    l'intestazione del capitolo con gli id delle unità — non il JSON intero,
    che gonfierebbe l'em.json a ogni capitolo."""
    lingua = _lang(lang)
    lingua = lingua if lingua in _SYSTEM else "en"
    voce = _M["prompt_context"]
    testa = voce.get(lingua, voce["en"]).format(
        title=(brief.get("activity") or {}).get("name") or "",
        kind=_kind_word(brief, lingua),
        ids=", ".join(a["id"] for a in brief.get("actions") or []))
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
```

- [ ] **Step 4: eseguire → PASS** (10 passati).

- [ ] **Step 5: commit** `git commit -am "feat(narrativa): briefing con rapporti, campi della scheda e ordine stratigrafico; messaggi it/en; menzioni normalizzate"`

---

### Task 3: generazione, rigenerazione, convalida, autori, export

**Files:**
- Modify: `modules/s3dgraphy/em_narrative.py`
- Test: `tests/utility/test_em_narrative.py`

**Interfaces:**
- Consumes: Task 1–2.
- Produces: `Outcome`, `Report` (`.generated`, `.failed`, `.cancelled`, `.outcomes`, `.summary(lang)`), `generate_chapter(graph, narrative, chapter, *, chat, model, lang=None, now=None, version="") -> Outcome`, `forget_ai_drafts(chapter) -> int`, `generate(container, *, chat, model, lang=None, anchors=None, progress=None, cancelled=None, version="") -> Report`, `human_authors(graph) -> [(id, name)]`, `add_author(graph, name) -> str`, `endorse(graph, narrative, author_id, anchor=None) -> int`, `export_file(graph, narrative, fmt, path) -> str`, `EXPORT_FORMATS = ("html", "docx")`.

- [ ] **Step 1: test (falliscono)**

```python
def _chat_finto(risposta="Nel capitolo si posa [[u3]], poi [[1.US2]] la copre; [[zz]] no."):
    chiamate = []

    def chat(messages):
        chiamate.append(messages)
        return risposta
    chat.chiamate = chiamate
    return chat


def test_generate_chapter_scrive_la_bozza_attribuita_con_prompt_e_fonti():
    from s3dgraphy.nodes.author_node import AuthorAINode
    from s3dgraphy.nodes.extractor_node import ExtractorNode
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    cap = n.chapter_by_anchor("epoch_1_1")
    chat = _chat_finto()
    esito = en.generate_chapter(g, n, cap, chat=chat, model="modello-x", lang="it",
                                now="2026-10-12T10:00:00Z", version="1")
    assert esito.ok and esito.anchor == "epoch_1_1" and not esito.truncated
    assert "[[u2]]" in esito.text and "zz no" in esito.text
    assert en.chapter_status(cap) == "ai_draft"
    blocco = [b for b in cap.blocks if b.block_type == "prose" and b.ai_generated][0]
    assert blocco.authored_by == "AI.modello-x" and blocco.options["generated_at"] == "2026-10-12T10:00:00Z"
    assert isinstance(g.find_node_by_id(blocco.authored_by), AuthorAINode)
    estrattore = g.find_node_by_id(blocco.prompt_ref)
    assert isinstance(estrattore, ExtractorNode) and estrattore.node_id.startswith(en.PROMPT_EXTRACTOR_PREFIX)
    assert "u3, u2" in estrattore.description and "Regole" in estrattore.description
    assert chat.chiamate[0][0]["role"] == "system"


def test_generate_chapter_non_alza_mai_e_segna_il_troncato():
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    cap = n.chapter_by_anchor("epoch_1_1")
    vuoto = en.generate_chapter(g, n, cap, chat=lambda m: "   ", model="m")
    assert not vuoto.ok and "niente" in vuoto.error and en.chapter_status(cap) == "empty"

    def esplode(m):
        raise RuntimeError("quota finita")
    rotto = en.generate_chapter(g, n, cap, chat=esplode, model="m")
    assert not rotto.ok and "quota finita" in rotto.error

    troncato = en.generate_chapter(g, n, cap, chat=lambda m: ("Testo a metà", True), model="m")
    assert troncato.ok and troncato.truncated
    assert any(b.options.get("truncated") for b in cap.blocks if b.block_type == "prose")


def test_forget_ai_drafts_toglie_solo_le_bozze_non_convalidate():
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    cap = n.chapter_by_anchor("epoch_1_1")
    en.generate_chapter(g, n, cap, chat=lambda m: "Prima bozza.", model="m")
    en.endorse(g, n, "author::mario_rossi", anchor="epoch_1_1")
    en.generate_chapter(g, n, cap, chat=lambda m: "Seconda bozza.", model="m")
    cap.add_prose("A mano.")
    assert en.forget_ai_drafts(cap) == 1
    testi = [b.text for b in cap.blocks if b.block_type == "prose"]
    assert "Seconda bozza." not in testi and "Prima bozza." in testi and "A mano." in testi


def test_generate_continua_dopo_un_errore_salta_i_pieni_e_si_ferma_se_annullato():
    from s3dgraphy.container import container_of
    g = grafo_di_prova()
    cont = container_of(g)
    risposte = iter([RuntimeError("no"), "Medioevo scritto."])

    def chat(m):
        r = next(risposte)
        if isinstance(r, Exception):
            raise r
        return r
    avanzamenti = []
    rep = en.generate(cont, chat=chat, model="m", lang="it",
                      progress=lambda i, n, t: avanzamenti.append((i, n, t)))
    assert rep.generated == 1 and rep.failed == 1 and not rep.cancelled
    assert avanzamenti == [(1, 2, "Età romana"), (2, 2, "Medioevo")]
    assert "1 capitoli generati, 1 falliti" in rep.summary("it")
    # seconda passata: il capitolo scritto si salta, quello vuoto si riprova
    rep2 = en.generate(cont, chat=lambda m: "Età romana scritta.", model="m")
    assert rep2.generated == 1 and [o.anchor for o in rep2.outcomes] == ["epoch_1_1"]
    # rigenerazione mirata: la bozza vecchia sparisce
    rep3 = en.generate(cont, chat=lambda m: "Medioevo riscritto.", model="m", anchors=["epoch_2_1"])
    cap = en.narrative_of(g).chapter_by_anchor("epoch_2_1")
    assert [b.text for b in cap.blocks if b.ai_generated] == ["Medioevo riscritto."]
    # annulla prima del primo capitolo
    rep4 = en.generate(cont, chat=lambda m: "x", model="m", anchors=["epoch_1_1", "epoch_2_1"],
                       cancelled=lambda: True)
    assert rep4.cancelled and rep4.outcomes == []


def test_autori_umani_convalida_ed_export(tmp_path):
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    assert en.human_authors(g) == [("author::mario_rossi", "Mario Rossi")]
    nuovo = en.add_author(g, "Anna Bianchi")
    assert nuovo == "author::anna_bianchi" and en.add_author(g, "Anna Bianchi") == nuovo
    assert ("author::anna_bianchi", "Anna Bianchi") in en.human_authors(g)
    for anchor in ("epoch_1_1", "epoch_2_1"):
        en.generate_chapter(g, n, n.chapter_by_anchor(anchor), chat=lambda m: "Bozza di %s." % anchor, model="m")
    assert en.endorse(g, n, nuovo, anchor="epoch_1_1") == 1
    assert en.chapter_status(n.chapter_by_anchor("epoch_1_1")) == "ai_endorsed"
    assert en.endorse(g, n, nuovo) == 1                       # il resto
    assert en.chapter_status(n.chapter_by_anchor("epoch_2_1")) == "ai_endorsed"
    with pytest.raises(Exception):
        en.endorse(g, n, "AI.m")                             # un modello non convalida
    html = en.export_file(g, n, "html", tmp_path / "v.html")
    assert "Bozza di epoch_1_1" in Path(html).read_text(encoding="utf-8")
    docx = en.export_file(g, n, "docx", tmp_path / "v.docx")
    assert Path(docx).stat().st_size > 1000
    with pytest.raises(ValueError):
        en.export_file(g, n, "pdf", tmp_path / "v.pdf")
```

- [ ] **Step 2: eseguire → FAIL** (`AttributeError: generate_chapter`).

- [ ] **Step 3: implementazione**

```python
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
                     version: str = "") -> Outcome:
    """Un capitolo: briefing → modello → bozza nel grafo. Non alza mai:
    un capitolo che va male è un esito negativo, e gli altri continuano."""
    anchor = str(getattr(chapter, "anchor", "") or "")
    titolo = str(getattr(chapter, "title", "") or anchor)
    try:
        brief = briefing(graph, anchor)
        risposta = chat(messages(brief, lang))
        testo, troncato = (risposta if isinstance(risposta, tuple) else (risposta, False))
        testo = normalize_mentions(str(testo or "").strip(), graph)
        if not testo:
            raise NarrativeError(msg("empty_reply"))
        prima = {n.node_id for n in graph.nodes}
        from s3dgraphy.narrative import write_ai_draft
        write_ai_draft(graph, anchor, testo, model=str(model), version=version,
                       date=now or _now(), prompt=prompt_record(brief, lang),
                       narrative_id=narrative.node_id, chapter_title=titolo,
                       sources=[s["id"] for s in brief.get("sources") or []])
        if troncato:
            chapter.blocks[-1].options["truncated"] = True
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
    ``anchors`` dati: quei capitoli, rigenerati (le bozze vecchie via).
    ``cancelled()`` si legge prima di ogni capitolo."""
    da_fare = []
    for graph in (getattr(container, "graphs", None) or {}).values():
        narrativa = scaffold(graph, lang)
        if anchors is None:
            scelti = chapters_to_generate(graph, narrativa, only_empty=True)
        else:
            voluti = set(anchors)
            scelti = [c for c in chapters_to_generate(graph, narrativa, only_empty=False)
                      if c.anchor in voluti]
        da_fare.extend((graph, narrativa, c) for c in scelti)
    rapporto = Report()
    for i, (graph, narrativa, cap) in enumerate(da_fare, 1):
        if cancelled is not None and cancelled():
            rapporto.cancelled = True
            break
        if progress is not None:
            progress(i, len(da_fare), str(cap.title))
        if anchors is not None:
            forget_ai_drafts(cap)
        rapporto.outcomes.append(generate_chapter(
            graph, narrativa, cap, chat=chat, model=model, lang=lang, version=version))
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
    dell'esportazione (``author::<nome>``)."""
    from s3dgraphy.nodes.author_node import AuthorNode
    nome = str(name or "").strip()
    if not nome:
        raise NarrativeError("an author needs a name")
    for node_id, esistente in human_authors(graph):
        if esistente.strip().lower() == nome.lower():
            return node_id
    node_id = "author::" + _slug(nome)
    if graph.find_node_by_id(node_id) is None:
        graph.add_node(AuthorNode(node_id, name=nome))
    return node_id


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


def export_file(graph, narrative, fmt: str, path) -> str:
    """HTML o DOCX della narrativa, bozze comprese (segnate dalla libreria)."""
    from s3dgraphy.api import export_narrative
    if fmt not in EXPORT_FORMATS:
        raise ValueError("fmt must be one of %s" % (EXPORT_FORMATS,))
    esito = export_narrative(graph, narrative.node_id, fmt, include_unvalidated=True)
    payload = esito["payload"]
    percorso = str(path)
    if isinstance(payload, bytes):
        with open(percorso, "wb") as fh:
            fh.write(payload)
    else:
        with open(percorso, "w", encoding="utf-8") as fh:
            fh.write(str(payload))
    return percorso
```

- [ ] **Step 4: eseguire → PASS** (15 passati).

- [ ] **Step 5: commit** `git commit -am "feat(narrativa): generazione per capitolo con esiti, rigenerazione, convalida con autore umano, export HTML/DOCX"`

---

### Task 4: carry-over nell'esportazione e nodi di supporto fuori dalla matrice

**Files:**
- Modify: `modules/s3dgraphy/em_narrative.py` (`carry_over`, `support_node`)
- Modify: `modules/s3dgraphy/em_export.py:90-199` (`export_site(..., keep_narrative=True)`)
- Modify: `modules/utility/em_matrix_model.py:78-85, 330-340` (`_NOT_A_UNIT` + estrattori dei prompt)
- Test: `tests/utility/test_em_narrative.py`, `tests/sync/test_em_narrative_export.py`, `tests/utility/test_em_matrix_model.py`

**Interfaces:**
- Produces: `carry_over(previous_graphs: dict, fresh_graphs: dict, lang=None) -> int`, `is_support_node(node_type, node_id) -> bool`; `export_site(connection_url, site, out_dir, per_saggio=None, keep_narrative=True)` (firma estesa, default invariato per i chiamanti).

- [ ] **Step 1: test (falliscono)**

In `tests/utility/test_em_narrative.py`:

```python
def test_carry_over_conserva_narrativa_autori_prompt_e_convalida_e_aggiunge_le_epoche_nuove():
    from s3dgraphy.nodes.epoch_node import EpochNode
    vecchio = grafo_di_prova()
    n = en.scaffold(vecchio, "it")
    en.generate_chapter(vecchio, n, n.chapter_by_anchor("epoch_1_1"), chat=lambda m: "Scritto [[u3]].", model="m")
    nuovo_autore = en.add_author(vecchio, "Anna Bianchi")
    en.endorse(vecchio, n, nuovo_autore)
    nuovo = grafo_di_prova()                       # riesportato dal DB: senza narrativa, senza Anna
    nuovo.add_node(EpochNode("epoch_3_1", "Età moderna", 1500, 1800))
    nuovo.add_edge("u1_se", "u1", "epoch_3_1", "survive_in_epoch")
    assert en.carry_over({"Villa": vecchio}, {"Villa": nuovo}, "it") == 1
    portata = en.narrative_of(nuovo)
    assert portata is not None and en.chapter_status(portata.chapter_by_anchor("epoch_1_1")) == "ai_endorsed"
    assert nuovo.find_node_by_id("AI.m") is not None and nuovo.find_node_by_id(nuovo_autore) is not None
    bloccho = [b for b in portata.chapter_by_anchor("epoch_1_1").blocks if b.ai_generated][0]
    assert nuovo.find_node_by_id(bloccho.prompt_ref) is not None
    assert nuovo.find_edge_by_id("%s_has_author_AI.m" % portata.node_id) is not None
    assert portata.chapter_by_anchor("epoch_3_1") is not None          # epoca nuova → capitolo
    assert en.carry_over({"Altro": vecchio}, {"Villa": grafo_di_prova()}, "it") == 0


def test_is_support_node_riconosce_i_nodi_della_narrativa():
    assert en.is_support_node("narrative", "narrative_Villa")
    assert en.is_support_node("author_ai", "AI.m")
    assert en.is_support_node("extractor", "EXT.prompt.abc")
    assert not en.is_support_node("extractor", "EXT.1")
    assert not en.is_support_node("US", "u1")
```

In `tests/utility/test_em_matrix_model.py` (in coda):

```python
def test_i_nodi_di_supporto_della_narrativa_non_entrano_nel_disegno_ne_negli_avvisi():
    from modules.utility.em_matrix_model import read_em_json
    modello = read_em_json({"graphs": {"S": {"nodes": [
        {"id": "u1", "name": "US1", "node_type": "US", "data": {"us": "1"}},
        {"id": "d1", "name": "Relazione", "node_type": "document"},
        {"id": "narrative_S", "name": "Storia", "node_type": "narrative", "data": {"chapters": []}},
        {"id": "AI.m", "name": "m", "node_type": "author_ai"},
        {"id": "EXT.prompt.abc", "name": "Prompt", "node_type": "extractor"}],
        "edges": [{"source": "EXT.prompt.abc", "target": "d1", "type": "extracted_from"},
                  {"source": "narrative_S", "target": "AI.m", "type": "has_author"}]}}})
    assert [u.node_id for u in modello.units] == ["u1"]
    assert modello.relations == []
    assert not any("narrative" in a or "AI.m" in a or "Prompt" in a for a in modello.warnings)
```

Nuovo `tests/sync/test_em_narrative_export.py`:

```python
"""La narrativa sopravvive alla riesportazione dal database (2026-10-12)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.s3dgraphy import em_export  # noqa: E402
from modules.s3dgraphy import em_narrative as en  # noqa: E402

SITO = "Scavo archeologico"


@pytest.fixture()
def sample_db(tmp_path, monkeypatch):
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    return "sqlite:///%s" % (folder / "db.sqlite")


def test_la_narrativa_resta_quando_il_sito_si_riesporta(sample_db, tmp_path):
    out = tmp_path / "em"
    path, _n, _e, _w = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    cont, _ = en.load_project(path)
    graph = cont.active()
    assert en.narrative_of(graph) is None
    rep = en.generate(cont, chat=lambda m: "Capitolo scritto dal modello finto.", model="finto", lang="it")
    assert rep.generated >= 1 and rep.failed == 0
    autore = en.human_authors(graph)[0][0]
    en.endorse(graph, en.narrative_of(graph), autore)
    en.save_project(cont, path)

    path2, _n2, _e2, avvisi = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    assert path2 == path
    assert any("conservata" in a or "kept" in a for a in avvisi)
    cont2, _ = en.load_project(path2)
    viste = en.overview(cont2, "it")
    assert viste and all(v.status == "ai_endorsed" for v in viste if v.can_generate)
    assert "Capitolo scritto dal modello finto." in viste[1].text

    senza, _, _, avvisi3 = em_export.export_site(sample_db, SITO, str(out), per_saggio=False,
                                                 keep_narrative=False)
    assert en.narrative_of(en.load_project(senza)[0].active()) is None
    assert not any("conservata" in a for a in avvisi3)


def test_un_file_precedente_rotto_non_ferma_l_esportazione(sample_db, tmp_path):
    out = tmp_path / "em"
    path, *_ = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    Path(path).write_text("{rotto", encoding="utf-8")
    path2, _n, _e, avvisi = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    assert path2 == path and any("non si legge" in a or "cannot be read" in a for a in avvisi)
    assert en.load_project(path2)
```

- [ ] **Step 2: eseguire → FAIL** (`carry_over` manca; `keep_narrative` non accettato; i nodi di supporto entrano negli avvisi).

- [ ] **Step 3: implementazione**

In `em_narrative.py`:

```python
# ---------------------------------------------------------------------------
# Conservare la narrativa quando il sito si riesporta
# ---------------------------------------------------------------------------

def is_support_node(node_type: str, node_id: str) -> bool:
    """I nodi che reggono la narrativa e non sono stratigrafia: la narrativa,
    l'autore AI, gli estrattori dei prompt."""
    tipo = str(node_type or "")
    return (tipo in ("narrative", "author_ai")
            or (tipo == "extractor" and str(node_id or "").startswith(PROMPT_EXTRACTOR_PREFIX)))


def _support_refs(narrative) -> List[str]:
    refs: List[str] = []
    for cap in narrative.chapters:
        if cap.authored_by:
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
```

In `em_export.py`, firma `def export_site(connection_url, site, out_dir, per_saggio=None, keep_narrative=True):` e, subito dopo `path = _claim_path(path, site)` (dentro il `try` di scrittura, prima di scrivere):

```python
        if keep_narrative and os.path.exists(path):
            warnings.extend(_keep_narrative(path, contenitore, graph, site))
```

con, a livello di modulo:

```python
def _keep_narrative(path, contenitore, graph, site):
    """La narrativa del file che sta per essere sovrascritto passa nel
    grafo nuovo (spec 2026-10-12). Un file che non si legge non ferma
    l'esportazione: lo si dice."""
    from . import em_narrative as en
    try:
        precedente, _ = en.load_project(path)
    except Exception as e:                          # noqa: BLE001
        return [en.msg("narrative_not_kept", err=e)]
    nuovi = (dict(getattr(contenitore, "graphs", None) or {})
             if contenitore is not None else {str(site): graph})
    try:
        quante = en.carry_over(dict(precedente.graphs), nuovi)
    except Exception as e:                          # noqa: BLE001
        return [en.msg("narrative_not_kept", err=e)]
    if not quante:
        return []
    capitoli = sum(len(n.chapters) for g in nuovi.values() for n in en.narratives_of(g))
    return [en.msg("narrative_kept", n=capitoli)]
```

Nota: `warnings` è definita prima del `try` di scrittura (riga «warnings = [str(w) …]»), quindi l'append è lecito; la lingua dei messaggi è quella di `en.LANGUAGE` (il plugin chiama `en.set_language` all'apertura della scheda).

In `em_matrix_model.py`: aggiungere `"narrative", "author_ai"` a `_NOT_A_UNIT`, e nel ciclo dei nodi di `read_em_json`, prima di `elif tipo not in _NOT_A_UNIT:`, saltare gli estrattori dei prompt:

```python
        elif tipo == "extractor" and chiave.startswith("EXT.prompt."):
            continue          # il prompt di una narrativa non è un paradato della matrice
```

- [ ] **Step 4: eseguire** `tests/utility/test_em_narrative.py tests/utility/test_em_matrix_model.py tests/sync/test_em_narrative_export.py tests/sync/test_em_export.py tests/sync/test_export_per_saggio.py` → PASS.

- [ ] **Step 5: commit** `git commit -am "feat(narrativa): la narrativa sopravvive alla riesportazione; i nodi che la reggono restano fuori dalla matrice"`

---

### Task 5: la scheda «Narrativa» nel pannello

**Files:**
- Create: `modules/s3dgraphy/em_narrative_tab.py`
- Modify: `modules/s3dgraphy/em_matrix_panel.py:237-450` (`open_in_panel(..., tab=None)`, colonna destra in un `QTabWidget`)
- Test: `tests/sync/test_em_narrative_wiring.py`

**Interfaces:**
- Produces: `build_tab(parent, iface) -> QWidget` (objectName `narrativa`, figli `stato`, `capitoli`, `testo`, `genera`, `rigenera`, `convalida`, `prepara`, `esporta`, `emstudio`, `annulla`, `avanzamento`), `show_file(widget, path)`, `NarrativeThread`, `_L`, `_t(key, **kw)`, `_lang()`; `open_in_panel(iface, em_json_path, title="", conn_str=None, tab=None)`.

- [ ] **Step 1: test (falliscono)**

```python
"""La scheda «Narrativa» del pannello della matrice (2026-10-12).

Come per il pannello: si leggono le promesse nel sorgente e si prova il
widget in offscreen con un iface finto, senza database.
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

TAB = _ROOT / "modules" / "s3dgraphy" / "em_narrative_tab.py"
PANEL = _ROOT / "modules" / "s3dgraphy" / "em_matrix_panel.py"


@pytest.fixture(scope="module")
def qgs():
    from qgis.core import QgsApplication
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


class _Bar:
    def __init__(self):
        self.messaggi = []

    def pushInfo(self, t, m):
        self.messaggi.append(("info", t, m))

    def pushWarning(self, t, m):
        self.messaggi.append(("warn", t, m))


class _Iface:
    def __init__(self):
        self._bar = _Bar()

    def messageBar(self):
        return self._bar

    def mainWindow(self):
        return None


def _file_con_narrativa(tmp_path):
    from s3dgraphy.container import container_of
    from modules.s3dgraphy import em_narrative as en
    sys.path.insert(0, str(_ROOT / "tests" / "utility"))
    from test_em_narrative import grafo_di_prova
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    en.generate_chapter(g, n, n.chapter_by_anchor("epoch_1_1"), chat=lambda m: "Bozza romana.", model="m")
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(g), percorso)
    return percorso


def test_le_stringhe_hanno_italiano_e_inglese():
    from modules.s3dgraphy.em_narrative_tab import _L
    for chiave, voce in _L.items():
        assert set(voce) >= {"it", "en"}, chiave


def test_il_pannello_ha_la_scheda_e_la_ricarica_a_ogni_apertura():
    src = PANEL.read_text(encoding="utf-8")
    assert "QTabWidget" in src and '"schede"' in src
    assert "em_narrative_tab" in src and "show_file(" in src and "build_tab(" in src
    assert 'tab="narrativa"' in src or "tab == \"narrativa\"" in src


def test_ogni_metodo_privato_chiamato_su_self_esiste_nel_thread():
    albero = ast.parse(TAB.read_text(encoding="utf-8"))
    for cls in [n for n in albero.body if isinstance(n, ast.ClassDef)]:
        definiti = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
        chiamati = {n.attr for n in ast.walk(cls)
                    if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                    and n.value.id == "self" and n.attr.startswith("_")
                    and not n.attr.startswith("__")}
        assert chiamati - definiti - {"_stop"} == set(), cls.name


def test_la_scheda_elenca_i_capitoli_con_gli_stati_e_spegne_l_ai_se_manca(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QLabel, QListWidget, QPushButton, QTextBrowser, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    assert w.objectName() == "narrativa"
    tab.show_file(w, _file_con_narrativa(tmp_path))
    elenco = w.findChild(QListWidget, "capitoli")
    assert elenco.count() == 3
    voci = [elenco.item(i).text() for i in range(elenco.count())]
    assert any("bozza AI" in v for v in voci) and any("da scrivere" in v for v in voci)
    elenco.setCurrentRow(1)
    assert "Bozza romana" in w.findChild(QTextBrowser, "testo").toPlainText()
    assert not w.findChild(QPushButton, "genera").isEnabled()
    assert not w.findChild(QPushButton, "rigenera").isEnabled()
    assert w.findChild(QPushButton, "convalida").isEnabled()
    assert w.findChild(QPushButton, "esporta").isEnabled()
    assert "Relazione AI" in w.findChild(QLabel, "stato").text()


def test_la_scheda_con_l_ai_impostata_accende_genera(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QLabel, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab

    class _Cfg:
        model, provider = "gpt-finto", None
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: (_Cfg(), "us_report"))
    w = tab.build_tab(QWidget(), _Iface())
    tab.show_file(w, _file_con_narrativa(tmp_path))
    assert w.findChild(QPushButton, "genera").isEnabled()
    assert "gpt-finto" in w.findChild(QLabel, "stato").text()


def test_la_scheda_su_un_file_senza_narrativa_lo_dice(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QLabel, QListWidget, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    percorso = tmp_path / "vuoto.em.json"
    percorso.write_text(json.dumps({"graphs": {"S": {"nodes": [
        {"id": "e1", "name": "XV", "node_type": "EpochNode", "data": {"start_time": 1400, "end_time": 1499}},
        {"id": "u1", "name": "US1", "node_type": "US", "data": {"us": "1"}}],
        "edges": [{"source": "u1", "target": "e1", "type": "has_first_epoch"}]}}}), encoding="utf-8")
    w = tab.build_tab(QWidget(), _Iface())
    tab.show_file(w, percorso)
    assert w.findChild(QListWidget, "capitoli").count() == 0
    assert "Nessuna narrativa" in w.findChild(QLabel, "vuoto").text()
```

- [ ] **Step 2: eseguire → FAIL** (`ModuleNotFoundError: em_narrative_tab`).

- [ ] **Step 3: scrivere `em_narrative_tab.py`**

```python
"""La scheda «Narrativa» del pannello della matrice (2026-10-12).

Qt sta qui; la logica sta in ``em_narrative`` (puro) e il lato grafo
nella libreria. La scheda legge e scrive **lo stesso em.json** che il
pannello disegna e che EMStudio apre: niente copie.

Spec: docs/superpowers/specs/2026-10-12-narrativa-ai-design.md
"""
from __future__ import annotations

import os
from typing import List, Optional

from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (QFileDialog, QHBoxLayout, QInputDialog, QLabel,
                                 QListWidget, QListWidgetItem, QMenu, QMessageBox,
                                 QPushButton, QTextBrowser, QVBoxLayout, QWidget)

from . import em_narrative as en


def _lang() -> str:
    try:
        from qgis.core import QgsSettings
        return (QgsSettings().value("locale/userLocale", "it", type=str) or "it")[:2]
    except Exception:                               # noqa: BLE001
        return "it"


_L = {
    "tab": {"it": "Narrativa", "en": "Narrative"},
    "no_ai": {"it": "Nessuna AI impostata: impostala nella scheda US → Relazione AI (o nell'interrogazione AI del database).",
              "en": "No AI configured: set it in the US form → AI report (or in the AI database query)."},
    "empty": {"it": "Nessuna narrativa nel file: «Prepara i capitoli» crea lo scheletro ({n} capitoli fra epoche e attività), «Genera con l'AI» lo scrive.",
              "en": "No narrative in the file: “Prepare the chapters” builds the outline ({n} chapters over epochs and activities), “Generate with AI” writes it."},
    "generate": {"it": "Genera con l'AI", "en": "Generate with AI"},
    "regenerate": {"it": "Rigenera capitolo", "en": "Regenerate chapter"},
    "endorse": {"it": "Convalida…", "en": "Endorse…"},
    "endorse_chapter": {"it": "Questo capitolo", "en": "This chapter"},
    "endorse_all": {"it": "Tutti i capitoli", "en": "All chapters"},
    "prepare": {"it": "Prepara i capitoli", "en": "Prepare the chapters"},
    "export": {"it": "Esporta…", "en": "Export…"},
    "emstudio": {"it": "Apri in EMStudio", "en": "Open in EMStudio"},
    "cancel": {"it": "Annulla", "en": "Cancel"},
    "progress": {"it": "Capitolo {i} di {n} · {title}", "en": "Chapter {i} of {n} · {title}"},
    "who": {"it": "Chi convalida? Scegli un autore o scrivi un nome nuovo.",
            "en": "Who endorses? Pick an author or type a new name."},
    "endorsed": {"it": "{n} blocchi convalidati da {who}.", "en": "{n} blocks endorsed by {who}."},
    "nothing_to_endorse": {"it": "Niente da convalidare.", "en": "Nothing to endorse."},
    "export_filter": {"it": "Pagina HTML (*.html);;Documento Word (*.docx)",
                      "en": "HTML page (*.html);;Word document (*.docx)"},
    "exported": {"it": "Narrativa esportata in {path}", "en": "Narrative exported to {path}"},
    "emstudio_missing": {"it": "EMStudio non risulta installato: menu Extended Matrix → Installa EMStudio…",
                         "en": "EMStudio is not installed: menu Extended Matrix → Install EMStudio…"},
    "prepared": {"it": "Capitoli preparati: {n}.", "en": "Chapters prepared: {n}."},
    "saved": {"it": "Narrativa salvata in {name}.", "en": "Narrative saved in {name}."},
    "error": {"it": "Narrativa", "en": "Narrative"},
    "close_emstudio": {"it": "Se EMStudio ha il file aperto, chiudilo prima: chi scrive per ultimo vince.",
                       "en": "If EMStudio has the file open, close it first: the last writer wins."},
}


def _t(key: str, **kw) -> str:
    voce = _L[key]
    return voce.get(_lang(), voce["en"]).format(**kw)


class NarrativeThread(QThread):
    """Genera fuori dal filo dell'interfaccia e salva alla fine."""

    progress = pyqtSignal(int, int, str)
    finished_ok = pyqtSignal(bool, str)

    def __init__(self, path, cfg, lang, anchors=None, parent=None):
        super().__init__(parent)
        self._path, self._cfg, self._lang, self._anchors = str(path), cfg, lang, anchors
        self._stop = False

    def cancel(self):
        self._stop = True

    def _chat(self, messages):
        from ..utility.llm_providers import LLMProviderManager
        meta = {}
        testo = "".join(LLMProviderManager.stream_chat(
            self._cfg, messages, max_tokens=en.MAX_TOKENS, meta=meta))
        return testo, bool(meta.get("truncated"))

    def run(self):                                  # noqa: D401
        try:
            contenitore, _ = en.load_project(self._path)
            rapporto = en.generate(
                contenitore, chat=self._chat, model=str(getattr(self._cfg, "model", "")),
                lang=self._lang, anchors=self._anchors,
                progress=lambda i, n, t: self.progress.emit(i, n, t),
                cancelled=lambda: self._stop)
            if rapporto.outcomes:
                en.save_project(contenitore, self._path)
            self.finished_ok.emit(rapporto.failed == 0 and not rapporto.cancelled,
                                  rapporto.summary(self._lang))
        except Exception as e:                      # noqa: BLE001
            self.finished_ok.emit(False, str(e))


class _State:
    def __init__(self):
        self.path: Optional[str] = None
        self.views: List[en.ChapterView] = []
        self.thread: Optional[NarrativeThread] = None
        self.config = None


def build_tab(parent, iface) -> QWidget:
    en.set_language(_lang())
    w = QWidget(parent)
    w.setObjectName("narrativa")
    stato = _State()
    w._stato = stato                                # noqa: SLF001 (vive col widget)
    colonna = QVBoxLayout(w)
    colonna.setContentsMargins(0, 0, 0, 0)

    etichetta_stato = QLabel("", w)
    etichetta_stato.setObjectName("stato")
    etichetta_stato.setWordWrap(True)
    colonna.addWidget(etichetta_stato)

    vuoto = QLabel("", w)
    vuoto.setObjectName("vuoto")
    vuoto.setWordWrap(True)
    vuoto.setVisible(False)
    colonna.addWidget(vuoto)

    capitoli = QListWidget(w)
    capitoli.setObjectName("capitoli")
    colonna.addWidget(capitoli, 2)

    testo = QTextBrowser(w)
    testo.setObjectName("testo")
    colonna.addWidget(testo, 3)

    avanzamento = QLabel("", w)
    avanzamento.setObjectName("avanzamento")
    avanzamento.setVisible(False)
    colonna.addWidget(avanzamento)

    bottoni = {}
    for riga in (("genera", "regenerate_placeholder"),):
        pass
    riga1, riga2 = QHBoxLayout(), QHBoxLayout()
    for nome, chiave, riga in (("genera", "generate", riga1), ("rigenera", "regenerate", riga1),
                               ("convalida", "endorse", riga1), ("prepara", "prepare", riga2),
                               ("esporta", "export", riga2), ("emstudio", "emstudio", riga2),
                               ("annulla", "cancel", riga2)):
        b = QPushButton(_t(chiave), w)
        b.setObjectName(nome)
        riga.addWidget(b)
        bottoni[nome] = b
    bottoni["annulla"].setVisible(False)
    colonna.addLayout(riga1)
    colonna.addLayout(riga2)

    def _barra(livello, messaggio):
        try:
            barra = iface.messageBar()
            (barra.pushInfo if livello == "info" else barra.pushWarning)(_t("error"), messaggio)
        except Exception:                           # noqa: BLE001
            pass

    def _scelta() -> Optional[en.ChapterView]:
        i = capitoli.currentRow()
        return stato.views[i] if 0 <= i < len(stato.views) else None

    def _mostra_scelta():
        v = _scelta()
        testo.setPlainText(v.text if v else "")
        bottoni["rigenera"].setEnabled(bool(v and v.can_generate and stato.config is not None
                                            and stato.thread is None))

    def _occupato(si: bool):
        for nome in ("genera", "rigenera", "convalida", "prepara", "esporta", "emstudio"):
            bottoni[nome].setEnabled(not si and bottoni[nome].property("abilitabile") is not False)
        bottoni["annulla"].setVisible(si)
        avanzamento.setVisible(si)
        if not si:
            _aggiorna_bottoni()

    def _aggiorna_bottoni():
        ha_file = stato.path is not None
        ha_narrativa = bool(stato.views)
        ha_ai = stato.config is not None
        for nome, acceso in (("genera", ha_file and ha_ai),
                             ("prepara", ha_file),
                             ("convalida", ha_narrativa),
                             ("esporta", ha_narrativa),
                             ("emstudio", ha_file)):
            bottoni[nome].setEnabled(bool(acceso))
            bottoni[nome].setProperty("abilitabile", bool(acceso))
        _mostra_scelta()

    def _ricarica():
        capitoli.clear()
        stato.views = []
        vuoto.setVisible(False)
        if not stato.path:
            _aggiorna_bottoni()
            return
        try:
            contenitore, _ = en.load_project(stato.path)
        except en.NarrativeError as e:
            etichetta_stato.setText(str(e))
            stato.path = None
            _aggiorna_bottoni()
            return
        stato.views = en.overview(contenitore, _lang())
        piu_grafi = len(getattr(contenitore, "graphs", {}) or {}) > 1
        for v in stato.views:
            parola = en.status_word(v.status, _lang())
            if v.truncated:
                parola += ", " + en.msg("truncated")
            voce = "%s%s — %s" % ("[%s] " % v.graph_id if piu_grafi else "", v.title, parola)
            capitoli.addItem(QListWidgetItem(voce))
        if not stato.views:
            quanti = 0
            for g in (getattr(contenitore, "graphs", {}) or {}).values():
                from s3dgraphy.nodes.epoch_node import EpochNode
                from s3dgraphy.nodes.group_node import ActivityNodeGroup
                quanti += sum(1 for n in g.nodes if isinstance(n, (EpochNode, ActivityNodeGroup)))
            vuoto.setText(_t("empty", n=quanti))
            vuoto.setVisible(True)
        _aggiorna_bottoni()

    def _avvia(anchors=None):
        if stato.thread is not None or stato.config is None or not stato.path:
            return
        cfg, _scope = stato.config
        t = NarrativeThread(stato.path, cfg, _lang(), anchors=anchors, parent=w)
        stato.thread = t

        def _progresso(i, n, titolo):
            avanzamento.setText(_t("progress", i=i, n=n, title=titolo))

        def _fine(ok, messaggio):
            stato.thread = None
            _occupato(False)
            _ricarica()
            _barra("info" if ok else "warn", messaggio)
        t.progress.connect(_progresso)
        t.finished_ok.connect(_fine)
        avanzamento.setText(_t("progress", i=0, n=0, title="…"))
        _occupato(True)
        t.start()

    def _genera():
        _avvia(None)

    def _rigenera():
        v = _scelta()
        if v is not None and v.can_generate:
            _avvia([v.anchor])

    def _annulla():
        if stato.thread is not None:
            stato.thread.cancel()

    def _prepara():
        if not stato.path:
            return
        try:
            contenitore, _ = en.load_project(stato.path)
            n = 0
            for g in contenitore.graphs.values():
                n += len(en.scaffold(g, _lang()).chapters)
            en.save_project(contenitore, stato.path)
        except Exception as e:                      # noqa: BLE001
            _barra("warn", str(e))
            return
        _ricarica()
        _barra("info", _t("prepared", n=n))

    def _convalida():
        v = _scelta()
        menu = QMenu(w)
        azione_capitolo = menu.addAction(_t("endorse_chapter"))
        azione_capitolo.setEnabled(v is not None and v.status == "ai_draft")
        azione_tutti = menu.addAction(_t("endorse_all"))
        scelta = menu.exec_(bottoni["convalida"].mapToGlobal(bottoni["convalida"].rect().bottomLeft()))
        if scelta is None:
            return
        try:
            contenitore, _ = en.load_project(stato.path)
        except en.NarrativeError as e:
            _barra("warn", str(e))
            return
        grafi = list(contenitore.graphs.items())
        autori = []
        for _gid, g in grafi:
            autori.extend(n for n in en.human_authors(g) if n not in autori)
        nomi = [nome for _id, nome in autori]
        nome, ok = QInputDialog.getItem(w, _t("endorse"), _t("who"), nomi, 0, True)
        if not ok or not str(nome).strip():
            return
        firmati = 0
        for gid, g in grafi:
            narrativa = en.narrative_of(g)
            if narrativa is None:
                continue
            if scelta is azione_capitolo and v is not None and v.graph_id != gid:
                continue
            autore = en.add_author(g, str(nome))
            try:
                firmati += en.endorse(g, narrativa, autore,
                                      anchor=v.anchor if scelta is azione_capitolo else None)
            except Exception as e:                  # noqa: BLE001
                _barra("warn", str(e))
                return
        if not firmati:
            _barra("info", _t("nothing_to_endorse"))
            return
        try:
            en.save_project(contenitore, stato.path)
        except en.NarrativeError as e:
            _barra("warn", str(e))
            return
        _ricarica()
        _barra("info", _t("endorsed", n=firmati, who=nome))

    def _esporta():
        if not stato.path:
            return
        base = os.path.splitext(os.path.splitext(stato.path)[0])[0] + "_narrativa"
        percorso, filtro = QFileDialog.getSaveFileName(w, _t("export"), base + ".html", _t("export_filter"))
        if not percorso:
            return
        fmt = "docx" if percorso.lower().endswith(".docx") or "docx" in filtro else "html"
        if not percorso.lower().endswith("." + fmt):
            percorso += "." + fmt
        try:
            contenitore, _ = en.load_project(stato.path)
            scritti = []
            for gid, g in contenitore.graphs.items():
                narrativa = en.narrative_of(g)
                if narrativa is None:
                    continue
                destinazione = percorso
                if len(contenitore.graphs) > 1:
                    radice, est = os.path.splitext(percorso)
                    destinazione = "%s_%s%s" % (radice, gid.split("|")[-1], est)
                scritti.append(en.export_file(g, narrativa, fmt, destinazione))
        except Exception as e:                      # noqa: BLE001
            _barra("warn", str(e))
            return
        _barra("info", _t("exported", path=", ".join(scritti)))

    def _emstudio():
        if not stato.path:
            return
        from . import em_export
        if not em_export.open_in_emstudio(stato.path):
            _barra("warn", _t("emstudio_missing"))

    capitoli.currentRowChanged.connect(lambda _i: _mostra_scelta())
    bottoni["genera"].clicked.connect(_genera)
    bottoni["rigenera"].clicked.connect(_rigenera)
    bottoni["convalida"].clicked.connect(_convalida)
    bottoni["prepara"].clicked.connect(_prepara)
    bottoni["esporta"].clicked.connect(_esporta)
    bottoni["emstudio"].clicked.connect(_emstudio)
    bottoni["annulla"].clicked.connect(_annulla)
    w._ricarica = _ricarica                         # noqa: SLF001
    _aggiorna_bottoni()
    return w


def show_file(widget, path) -> None:
    """Punta la scheda sul file e la ricarica (anche a ogni riapertura
    del pannello su un altro sito)."""
    stato: _State = widget._stato                   # noqa: SLF001
    stato.path = str(path) if path else None
    stato.config = en.llm_config()
    etichetta = widget.findChild(QLabel, "stato")
    if stato.config is None:
        etichetta.setText(_t("no_ai"))
    else:
        cfg, scope = stato.config
        etichetta.setText(en.describe_config(cfg, scope, _lang()) + " · " + _t("close_emstudio"))
    widget._ricarica()                              # noqa: SLF001
```

(Nel codice finale togliere il ciclo vuoto `for riga in (("genera", "regenerate_placeholder"),): pass`, residuo di stesura.)

In `em_matrix_panel.open_in_panel`: firma `def open_in_panel(iface, em_json_path, title: str = "", conn_str=None, tab=None) -> bool:`; importare `QTabWidget`; dopo `destra.setMaximumWidth(380)` sostituire con:

```python
            from . import em_narrative_tab
            schede = QTabWidget(contenitore)
            schede.setObjectName("schede")
            schede.addTab(destra, "Unità" if em_narrative_tab._lang() == "it" else "Units")
            narrativa = em_narrative_tab.build_tab(schede, iface)
            schede.addTab(narrativa, em_narrative_tab._t("tab"))
            schede.setMinimumWidth(240)
            schede.setMaximumWidth(420)
            divisore = QSplitter(Qt.Orientation.Horizontal, contenitore)
            divisore.addWidget(vista)
            divisore.addWidget(schede)
```

(e togliere `destra.setMinimumWidth/MaximumWidth` e la vecchia `divisore.addWidget(destra)`). Nel ramo «dock esistente» niente da cambiare. Dopo `vista.show_layout(impaginato)`:

```python
        from . import em_narrative_tab
        contenuto = dock.widget()
        scheda_narrativa = contenuto.findChild(QWidget, "narrativa")
        if scheda_narrativa is not None:
            em_narrative_tab.show_file(scheda_narrativa, em_json_path)
        schede = contenuto.findChild(QTabWidget, "schede")
        if schede is not None:
            schede.setCurrentIndex(1 if tab == "narrativa" else 0)
```

- [ ] **Step 4: eseguire** `tests/sync/test_em_narrative_wiring.py tests/sync/test_em_matrix_panel.py tests/sync/test_matrix_panel_media.py` → PASS.

- [ ] **Step 5: commit** `git add -A modules/s3dgraphy/em_narrative_tab.py modules/s3dgraphy/em_matrix_panel.py tests/sync/test_em_narrative_wiring.py && git commit -m "feat(narrativa): la scheda Narrativa nel pannello della matrice — genera, rigenera, convalida, esporta, apri in EMStudio"`

---

### Task 6: il plugin — file persistente, domanda sui saggi condivisa, bottoni dopo l'esportazione

**Files:**
- Modify: `pyarchinitPlugin.py:2933-3062`
- Test: `tests/sync/test_em_narrative_wiring.py`

**Interfaces:**
- Produces: `_ask_split(self, site, conn_str) -> (ok, per_saggio)`; `_run_em_matrix_view` senza `tempfile`; `_run_em_export` con i tre bottoni.

- [ ] **Step 1: test (falliscono)** — aggiungere a `tests/sync/test_em_narrative_wiring.py`:

```python
PLUGIN = _ROOT / "pyarchinitPlugin.py"


def _corpo(nome: str) -> str:
    albero = ast.parse(PLUGIN.read_text(encoding="utf-8"))
    for n in ast.walk(albero):
        if isinstance(n, ast.FunctionDef) and n.name == nome:
            return ast.get_source_segment(PLUGIN.read_text(encoding="utf-8"), n)
    raise AssertionError(nome)


def test_vedi_la_matrice_scrive_nella_cartella_em_e_non_in_una_temporanea():
    vista = _corpo("_run_em_matrix_view")
    assert "tempfile" not in vista and "_matrice_temp" not in vista
    assert "pyarchinit_EM_folder" in vista and "_ask_split(" in vista
    assert "_ask_split(" in _corpo("_run_em_export")
    assert "_matrice_temp" not in PLUGIN.read_text(encoding="utf-8")


def test_dopo_l_esportazione_si_puo_aprire_la_narrativa():
    esporta = _corpo("_run_em_export")
    assert "llm_config(" in esporta and 'tab="narrativa"' in esporta
    assert "open_in_emstudio" in esporta
```

- [ ] **Step 2: eseguire → FAIL**.

- [ ] **Step 3: implementazione** in `pyarchinitPlugin.py`:

Nuovo metodo, prima di `_run_em_export`:

```python
    def _ask_split(self, site, conn_str):
        """Come dividere l'em.json quando il sito ha dei saggi: (ok, per_saggio).

        Una domanda sola, condivisa da «Esporta in em.json» e da «Vedi la
        matrice», così le due voci scrivono lo **stesso** file con la
        stessa forma (spec 2026-10-12: un file solo, la narrativa dentro).
        """
        from qgis.PyQt.QtWidgets import QInputDialog
        from modules.s3dgraphy import em_export
        try:
            saggi = em_export.saggi_del_sito(conn_str, site)
        except Exception:                           # noqa: BLE001
            saggi = []
        if not saggi:
            return True, None
        scelte = ["Un grafo per ogni saggio (%s)" % ", ".join(saggi),
                  "Un grafo solo per tutto il sito"]
        scelta, ok = QInputDialog.getItem(
            self.iface.mainWindow(), "Esporta in em.json",
            "Il sito ha %d saggi. Come divido il file?" % len(saggi),
            scelte, 0, False)
        if not ok:
            return False, None
        return True, scelta == scelte[0]
```

In `_run_em_export`: sostituire il blocco `per_saggio = None … per_saggio = scelta == scelte[0]` con:

```python
        ok, per_saggio = self._ask_split(site, conn_str)
        if not ok:
            return
```

e il finale (da `msg = (...)` in poi) con:

```python
        from modules.s3dgraphy import em_narrative, em_matrix_panel
        box = QMessageBox(self.iface.mainWindow())
        box.setWindowTitle("em.json")
        box.setText("Esportato %s\n%d nodi, %d archi, %d avvisi."
                    % (path, nodes, edges, len(warnings)))
        apri = box.addButton("Apri in EMStudio", QMessageBox.ButtonRole.AcceptRole)
        narrativa = None
        if em_narrative.llm_config() is not None:
            narrativa = box.addButton("Narrativa con l'AI", QMessageBox.ButtonRole.ActionRole)
        box.addButton("Chiudi", QMessageBox.ButtonRole.RejectRole)
        box.exec_()
        premuto = box.clickedButton()
        if premuto is narrativa:
            em_matrix_panel.open_in_panel(self.iface, path, "Matrice — %s" % site,
                                          conn_str=conn_str, tab="narrativa")
            return
        if premuto is apri:
            if not em_export.open_in_emstudio(path):
                answer = QMessageBox.question(
                    self.iface.mainWindow(), "EMStudio",
                    "EMStudio non risulta installato. Il file è in:\n%s\n\n"
                    "Vuoi installarlo adesso?" % path,
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No)
                if answer == QMessageBox.StandardButton.Yes:
                    if self._run_emstudio_install():
                        em_export.open_in_emstudio(path)
```

In `_run_em_matrix_view`: togliere `import tempfile`, `import shutil` e il blocco `for vecchia in … self._matrice_temp = [cartella]`; al loro posto:

```python
        from pathlib import Path
        ok, per_saggio = self._ask_split(site, conn_str)
        if not ok:
            return
        cartella = str(Path(pyarchinit_home()) / "pyarchinit_EM_folder")
        try:
            path, _n, _e, avvisi = em_export.export_site(
                conn_str, site, cartella, per_saggio=per_saggio)
```

Anche in `unload()`: niente da fare (`_matrice_temp` sparisce con la funzione; controllare con grep che non resti altrove).

- [ ] **Step 4: eseguire** `tests/sync/test_em_narrative_wiring.py tests/sync/test_em_matrix_panel.py tests/sync/test_em_export.py` → PASS; poi la suite intera → tutto verde.

- [ ] **Step 5: commit** `git commit -am "feat(narrativa): Vedi la matrice scrive in pyarchinit_EM_folder; dopo l'esportazione «Narrativa con l'AI»"`

---

### Task 7: giro vero, tutorial, changelog, versione

**Files:**
- Modify: `docs/tutorials/<lang>/36_extended_matrix_s3dgraphy.md` (dieci lingue) — sezione «Narrativa con l'AI»
- Modify: `dev_logs/CHANGELOG.md`, `metadata.txt` (5.13.106-alpha)
- Memory: `project_narrativa_matrice_interattiva.md`

- [ ] **Step 1: giro vero.** Con `PYARCHINIT_HOME=/Users/enzo/pyarchinit_5` e la configurazione AI di Enzo (`en.llm_config()` fuori da QGIS non ha `QSettings` del profilo: usare `QgsApplication` offscreen con il profilo predefinito, oppure costruire `LLMConfig` dal file chiave): esportare il sito di prova in una cartella di lavoro, `generate` su **un** capitolo con `NarrativeThread._chat`-equivalente, misurare secondi e caratteri, leggere la prosa. Annotare nel changelog modello, tempo e lunghezza. Se nessuna chiave è configurata, dirlo nel rapporto finale e saltare.
- [ ] **Step 2: tutorial.** Agente `tutorial-updater` (o general-purpose con la sua definizione) con il brief: sezione nuova in 36 «Narrativa con l'AI» — da dove si apre (Vedi la matrice → scheda Narrativa; Esporta → bottone), da dove legge l'AI (nessuna impostazione nuova), che cosa genera e che cosa no, bozza/convalida/stati, Rigenera, Esporta HTML/DOCX (bozze segnate ⚠), Apri in EMStudio (stessa scheda Narrative), il file in `pyarchinit_EM_folder` e la conservazione alla riesportazione, chiudere EMStudio prima di generare; dieci lingue; niente righe che iniziano con `|` nei blocchi di codice.
- [ ] **Step 3: changelog** (`stratigraph-changelog` o a mano, formato della 5.13.105): sezione `[feat] - 2026-10-12 — Narrativa con l'AI nel pannello della matrice — 5.13.106-alpha`, bilingue, con i numeri della suite e del giro vero.
- [ ] **Step 4: versione** `metadata.txt` → `5.13.106-alpha`; memoria aggiornata (A fatta, B parcheggiata, gotcha: `api.write_ai_draft` senza `sources`, `python3 -I` ignora `PYTHONPATH`, `extracted_from` disegnato).
- [ ] **Step 5: commit** `git commit -am "release: 5.13.106-alpha — narrativa con l'AI nel pannello della matrice; tutorial 36 in dieci lingue"`; tag e push **solo dopo** la verifica SAM chiesta da Enzo («prima di pushare controlla perché nel SAM le classi a testo non ne trovano uno»).
