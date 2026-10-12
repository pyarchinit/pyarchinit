"""La narrativa dell'Extended Matrix: il modulo puro (2026-10-12).

Tutto con un modello finto: la chiamata al modello è iniettata, e qui si
prova quello che pyArchInit decide — la configurazione AI da leggere, il
briefing arricchito, come la bozza entra nel grafo, come si conserva alla
riesportazione. Il lato grafo è della libreria.
"""
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
    from s3dgraphy.container import container_of

    g = grafo_di_prova()
    en.scaffold(g, "it")
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(g), percorso)
    cont, _ = en.load_project(percorso)
    assert en.narratives_of(cont.active())
    assert not (tmp_path / "villa.em.json.tmp").exists()
    prima = percorso.read_bytes()

    # Il file di lavoro non si rilegge → l'originale non si tocca.
    def _rotto(p):
        raise ValueError("rotto")
    monkeypatch.setattr(en, "_reread", _rotto)
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


# ---------------------------------------------------------------------------
# Task 2: briefing, messaggi, prompt registrato, menzioni
# ---------------------------------------------------------------------------

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
    assert "[[" in it[0]["content"] and "nome" in it[0]["content"]
    assert b["constraints"][0] in it[0]["content"]
    assert "Età romana" in it[1]["content"] and '"1.US3"' in it[1]["content"]
    assert '"u3"' not in it[1]["content"]                      # niente uuid al modello
    assert '"epoch_1_1"' in it[1]["content"]                    # le epoche tengono l'id
    en_ = en.messages(b, "en")
    assert "english" in en_[0]["content"].lower()
    record = en.prompt_record(b, "it")
    assert "u3, u2" in record and '"details"' not in record       # il JSON intero non va nel file


def test_normalize_mentions_tiene_gli_id_traduce_i_nomi_toglie_il_resto():
    g = grafo_di_prova()
    testo = "Sopra [[u3]] sta [[1.US2]] e poi [[ 1.us1 ]]; [[zz]] non esiste."
    assert en.normalize_mentions(testo, g) == "Sopra [[u3]] sta [[u2]] e poi [[u1]]; zz non esiste."


# ---------------------------------------------------------------------------
# Task 3: generazione, rigenerazione, convalida, autori, export
# ---------------------------------------------------------------------------

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
    assert rep3.generated == 1
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
        en.generate_chapter(g, n, n.chapter_by_anchor(anchor),
                            chat=lambda m, a=anchor: "Bozza di %s." % a, model="m")
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


# ---------------------------------------------------------------------------
# Task 4: conservare la narrativa alla riesportazione
# ---------------------------------------------------------------------------

def test_carry_over_conserva_narrativa_autori_prompt_e_convalida_e_aggiunge_le_epoche_nuove():
    from s3dgraphy.nodes.epoch_node import EpochNode
    vecchio = grafo_di_prova()
    n = en.scaffold(vecchio, "it")
    en.generate_chapter(vecchio, n, n.chapter_by_anchor("epoch_1_1"),
                        chat=lambda m: "Scritto [[u3]].", model="m")
    nuovo_autore = en.add_author(vecchio, "Anna Bianchi")
    en.endorse(vecchio, n, nuovo_autore)
    nuovo = grafo_di_prova()                       # riesportato dal DB: senza narrativa, senza Anna
    nuovo.add_node(EpochNode("epoch_3_1", "Età moderna", 1500, 1800))
    nuovo.add_edge("u1_se", "u1", "epoch_3_1", "survive_in_epoch")
    assert en.carry_over({"Villa": vecchio}, {"Villa": nuovo}, "it") == 1
    portata = en.narrative_of(nuovo)
    assert portata is not None and en.chapter_status(portata.chapter_by_anchor("epoch_1_1")) == "ai_endorsed"
    assert nuovo.find_node_by_id("AI.m") is not None and nuovo.find_node_by_id(nuovo_autore) is not None
    blocco = [b for b in portata.chapter_by_anchor("epoch_1_1").blocks if b.ai_generated][0]
    assert nuovo.find_node_by_id(blocco.prompt_ref) is not None
    assert nuovo.find_edge_by_id("%s_has_author_AI.m" % portata.node_id) is not None
    assert portata.chapter_by_anchor("epoch_3_1") is not None          # epoca nuova → capitolo
    assert en.carry_over({"Altro": vecchio}, {"Villa": grafo_di_prova()}, "it") == 0


def test_is_support_node_riconosce_i_nodi_della_narrativa():
    assert en.is_support_node("narrative", "narrative_Villa")
    assert en.is_support_node("author_ai", "AI.m")
    assert en.is_support_node("extractor", "EXT.prompt.abc")
    assert not en.is_support_node("extractor", "EXT.1")
    assert not en.is_support_node("US", "u1")


# ---------------------------------------------------------------------------
# Revisione finale (2026-10-12): i difetti trovati dal revisore
# ---------------------------------------------------------------------------

def _due_grafi():
    """L'esportazione per saggi: due grafi con le STESSE epoche (stessi id)."""
    from s3dgraphy.container import Container
    a = grafo_di_prova()
    a.graph_id = "Villa|Saggio A"
    b = grafo_di_prova()
    b.graph_id = "Villa|Saggio B"
    return Container(graphs={a.graph_id: a, b.graph_id: b}, active_graph_id=a.graph_id)


def _bozze(graph, anchor):
    return [b.text for b in en.narrative_of(graph).chapter_by_anchor(anchor).blocks
            if b.ai_generated]


def test_rigenera_tocca_solo_il_capitolo_del_grafo_scelto():
    cont = _due_grafi()
    assert en.generate(cont, chat=lambda m: "Prima.", model="m").generated == 4
    rep = en.generate(cont, chat=lambda m: "Riscritto.", model="m",
                      anchors=[("Villa|Saggio B", "epoch_1_1")])
    assert len(rep.outcomes) == 1 and rep.outcomes[0].ok
    assert _bozze(cont.graphs["Villa|Saggio A"], "epoch_1_1") == ["Prima."]
    assert _bozze(cont.graphs["Villa|Saggio B"], "epoch_1_1") == ["Riscritto."]
    # una stringa sola vale per tutti i grafi (chiamate di prima)
    assert len(en.generate(cont, chat=lambda m: "Tutti.", model="m",
                           anchors=["epoch_2_1"]).outcomes) == 2


def test_una_rigenerazione_fallita_tiene_la_bozza_di_prima():
    from s3dgraphy.container import container_of
    g = grafo_di_prova()
    cont = container_of(g)
    en.generate(cont, chat=lambda m: "Bozza buona.", model="m", anchors=["epoch_1_1"])

    def esplode(m):
        raise RuntimeError("rete giù")
    assert en.generate(cont, chat=esplode, model="m", anchors=["epoch_1_1"]).failed == 1
    assert _bozze(g, "epoch_1_1") == ["Bozza buona."]
    assert en.generate(cont, chat=lambda m: "  ", model="m", anchors=["epoch_1_1"]).failed == 1
    assert _bozze(g, "epoch_1_1") == ["Bozza buona."]


def test_il_segnaposto_sparisce_quando_il_capitolo_e_scritto(tmp_path):
    g = grafo_di_prova()
    n = en.scaffold(g, "it")
    cap = n.chapter_by_anchor("epoch_1_1")
    en.generate_chapter(g, n, cap, chat=lambda m: "Scritto.", model="m")
    assert not any(en.is_placeholder(b) for b in cap.blocks)
    assert [b.block_type for b in cap.blocks].count("embed") == 2      # gli embed restano
    en.scaffold(g, "it")                                                # lo scheletro rifatto non lo rimette
    assert not any(en.is_placeholder(b) for b in cap.blocks)
    testo = Path(en.export_file(g, n, "html", tmp_path / "v.html")).read_text(encoding="utf-8")
    assert "Scritto." in testo and "che cosa accade in «Età romana»" not in testo
    assert any(en.is_placeholder(b) for b in n.chapter_by_anchor("epoch_2_1").blocks)  # non generato: resta


def test_la_lingua_della_narrativa_vince_su_quella_dell_interfaccia():
    from s3dgraphy.container import container_of
    g = grafo_di_prova()
    en.scaffold(g, "en")                      # narrativa inglese, per esempio da EMStudio
    visti = []

    def chat(m):
        visti.append(m[0]["content"])
        return "Written."
    en.generate(container_of(g), chat=chat, model="m", lang="it")
    assert "english" in visti[0].lower() and "italiano" not in visti[0].lower()


def _grafo_grasso(quante=50):
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = grafo_di_prova()
    for i in range(10, 10 + quante):
        n = StratigraphicUnit("u%d" % i, "1.US%d" % i, description="x" * 400)
        n.data = {"us": str(i), "descrizione": "d" * 400, "interpretazione": "i" * 300}
        g.add_node(n)
        g.add_edge("u%d_fe" % i, "u%d" % i, "epoch_1_1", "has_first_epoch")
        if i > 10:
            g.add_edge("u%d_ov" % i, "u%d" % i, "u%d" % (i - 1), "overlies")
    return g


def test_il_briefing_rispetta_un_tetto_di_caratteri():
    g = _grafo_grasso()
    b = en.briefing(g, "epoch_1_1")
    pieno = len(en.messages(b, "it")[1]["content"])
    ridotto = en.fit_briefing(b, budget=8000)
    corto = len(en.messages(ridotto, "it")[1]["content"])
    assert corto <= 8000 < pieno
    assert ridotto["actions"] and ridotto["omitted_actions"] > 0
    assert [a["id"] for a in ridotto["actions"]] == [a["id"] for a in b["actions"]][:len(ridotto["actions"])]
    assert en.fit_briefing(b, budget=10 ** 7)["omitted_actions"] == 0
    assert len(en.messages(b, "it")[1]["content"]) == pieno           # l'originale non si tocca


def test_i_rapporti_si_elencano_una_volta_sola_quando_serve_posto():
    g = _grafo_grasso(8)
    b = en.briefing(g, "epoch_1_1")
    doppi = sum(len(a["relations"]) for a in b["actions"])
    stretto = en.fit_briefing(b, budget=len(en.messages(b, "it")[1]["content"]) - 1)
    singoli = sum(len(a["relations"]) for a in stretto["actions"])
    assert singoli < doppi and stretto["omitted_actions"] == 0


def test_generate_chapter_registra_il_prompt_del_briefing_ridotto(monkeypatch):
    g = _grafo_grasso(30)
    n = en.scaffold(g, "it")
    cap = n.chapter_by_anchor("epoch_1_1")
    monkeypatch.setattr(en, "MAX_PROMPT_CHARS", 6000)
    visti = []
    esito = en.generate_chapter(g, n, cap, chat=lambda m: visti.append(m) or "Ok.", model="m")
    assert esito.ok and len(visti[0][1]["content"]) <= 6000
    estrattore = g.find_node_by_id([b for b in cap.blocks if b.ai_generated][0].prompt_ref)
    assert "omesse" in estrattore.description or "omitted" in estrattore.description


def test_il_conteggio_dei_capitoli_possibili_conta_solo_le_epoche_con_unita():
    from s3dgraphy.nodes.epoch_node import EpochNode
    g = grafo_di_prova()
    g.add_node(EpochNode("epoch_9_9", "Vuota", 1900, 1950))
    assert en.count_possible_chapters(g) == 2
