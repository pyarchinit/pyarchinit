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
