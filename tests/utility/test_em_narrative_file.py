"""La narrativa che il file porta già e quella che pyArchInit costruisce col
template ``site_story`` (Enzo, 17 ottobre 2026, con TempluMare: «se poi
schiaccio prepara capitoli mi dà altri capitoli che non sono in linea con
quelli del template, poi me li scrive in inglese»).

TempluMare arriva con 13 capitoli canonici di Emanuel, in inglese, senza
``template_id``: la narrativa è sua. I capitoli di pyArchInit si aggiungono
solo quando lo si chiede («Prepara i capitoli» → «Aggiungi»), mai da soli
(rigenerare, riesportare); la Presentazione è quella del template, non il
primo capitolo del file; la lingua della prosa la sceglie chi scrive; e
riesportare il sito dal database non rimette la narrativa importata sopra
quella lavorata nel pannello.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import em_narrative as en  # noqa: E402


def _grafo():
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="Villa")
    g.name = "Villa"
    g.add_node(EpochNode("epoch_1_1", "Età romana", -100, 300))
    g.add_node(EpochNode("epoch_2_1", "Medioevo", 500, 1400))
    for uid, nome, epoca in (("u1", "1.US1", "epoch_2_1"), ("u2", "1.US2", "epoch_1_1"),
                             ("u3", "1.US3", "epoch_1_1")):
        n = StratigraphicUnit(uid, nome)
        n.data = {"us": uid[1:], "area": "1", "unita_tipo": "US"}
        g.add_node(n)
        g.add_edge(uid + "_fe", uid, epoca, "has_first_epoch")
    g.add_edge("u1_overlies_u2", "u1", "u2", "overlies")
    # la scena georeferenziata, come in TempluMare: il template fa anche «Dove si trova»
    from s3dgraphy.nodes.geo_position_node import GeoPositionNode
    g.add_node(GeoPositionNode("geo", epsg=31700, shift_x=1000.0, shift_y=2000.0))
    return g


def _del_file(g, node_id="narrative_villa"):
    """Come quella di TempluMare: capitoli canonici scritti da una persona,
    in inglese, il primo senza àncora, nessun template."""
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    n = NarrativeNode(node_id=node_id, name="The Villa", lang="en")
    intro = n.add_chapter("Survey — Introduction", canonical=True)
    intro.add_prose("The villa is known since the eighteenth century.")
    romana = n.add_chapter("Reconstruction — The Roman house", anchor="epoch_1_1", canonical=True)
    romana.add_prose("The walls of the Roman house were rebuilt in the second century.")
    g.add_node(n)
    return n


def _container(g):
    from s3dgraphy.container import container_of
    return container_of(g)


# --------------------------------------------------------- niente da soli

def test_rigenerare_non_aggiunge_i_capitoli_del_template_alla_narrativa_del_file():
    g = _grafo()
    n = _del_file(g)
    chiamate = []
    rapporto = en.generate(_container(g), chat=lambda m: chiamate.append(m) or "x", model="m", lang="it")
    assert [c.title for c in n.chapters] == ["Survey — Introduction", "Reconstruction — The Roman house"]
    assert chiamate == [] and rapporto.outcomes == []           # la prosa è di una persona
    assert "template_id" not in (n.data or {})


def test_riesportare_porta_la_narrativa_del_file_senza_capitoli_nuovi():
    vecchio, nuovo = _grafo(), _grafo()
    _del_file(vecchio)
    assert en.carry_over({"Villa": vecchio}, {"Villa": nuovo}, "it") == 1
    assert len(en.narrative_of(nuovo).chapters) == 2


def test_ensure_narrative_crea_quando_manca_e_fa_crescere_solo_quella_del_template():
    g = _grafo()
    n = en.ensure_narrative(g, "it")
    assert n is en.narrative_of(g) and n.data.get("template_id") == "site_story"
    prima = len(n.chapters)
    from s3dgraphy.nodes.epoch_node import EpochNode
    g.add_node(EpochNode("epoch_3_1", "Età moderna", 1500, 1800))
    g.add_edge("u1_se", "u1", "epoch_3_1", "survive_in_epoch")
    assert len(en.ensure_narrative(g, "it").chapters) == prima + 1
    f = _grafo()
    _del_file(f)
    assert len(en.ensure_narrative(f, "it").chapters) == 2


# --------------------------------------------------------- «Prepara» chiede

def test_si_chiede_solo_per_la_narrativa_del_file():
    g = _grafo()
    assert en.needs_template_choice(g) is False                 # niente narrativa: si crea
    _del_file(g)
    assert en.needs_template_choice(g) is True
    en.scaffold(g, write_lang="it")                             # «Aggiungi»: da qui è col template
    assert en.needs_template_choice(g) is False
    t = _grafo()
    en.scaffold(t, "it")
    assert en.needs_template_choice(t) is False


def test_aggiungere_i_capitoli_di_pyarchinit_tiene_quelli_del_file_davanti():
    g = _grafo()
    n = _del_file(g)
    en.scaffold(g, write_lang="it")
    titoli = [c.title for c in n.chapters]
    assert titoli[:2] == ["Survey — Introduction", "Reconstruction — The Roman house"]
    assert "Presentazione" in titoli and "Dove si trova" in titoli
    assert n.chapters[1].blocks[0].text.startswith("The walls")   # canonico: intatto
    assert n.data.get("template_id") == "site_story" and n.data.get("lang") == "en"


# --------------------------------------------------------- la Presentazione

def test_il_primo_capitolo_del_file_non_e_la_presentazione():
    g = _grafo()
    n = _del_file(g)
    assert en.is_presentation(n, n.chapters[0]) is False
    assert en.chapter_key(n, n.chapters[0]) is None
    assert en.can_generate(g, n.chapters[0], n) is False


def test_la_presentazione_del_template_si_riconosce_anche_in_fondo():
    g = _grafo()
    n = _del_file(g)
    en.scaffold(g, write_lang="it")
    presentazione = [c for c in n.chapters if c.title == "Presentazione"][0]
    assert en.is_presentation(n, presentazione) and not en.is_presentation(n, n.chapters[0])
    assert en.chapter_by_key(n, en.PRESENTATION_KEY) is presentazione
    assert presentazione in en.chapters_to_generate(g, n)


def test_la_presentazione_di_una_narrativa_del_template_resta_la_prima():
    g = _grafo()
    n = en.scaffold(g, "it")
    assert en.is_presentation(n, n.chapters[0])
    n.chapters[0].title = "Il sito"                              # rinominata: è ancora lei
    assert en.is_presentation(n, n.chapters[0])


# --------------------------------------------------------- la lingua

def _prompt(g, **kw):
    visti = []
    en.generate(_container(g), chat=lambda m: visti.append(m[0]["content"]) or "Testo.",
                model="m", **kw)
    return visti


def test_la_lingua_scelta_vince_su_quella_della_narrativa():
    g = _grafo()
    en.scaffold(g, "en")                                         # narrativa inglese
    visti = _prompt(g, lang="en", write_lang="it")
    assert visti and all("italiano" in v.lower() for v in visti)


def test_senza_scelta_vince_ancora_la_lingua_della_narrativa():
    g = _grafo()
    en.scaffold(g, "en")
    visti = _prompt(g, lang="it")
    assert visti and all("english" in v.lower() for v in visti)


def test_una_lingua_senza_istruzioni_proprie_si_chiede_per_nome():
    g = _grafo()
    en.scaffold(g, "en")
    visti = _prompt(g, lang="it", write_lang="de")
    assert visti and all("German" in v and "Write in English" not in v for v in visti)


def test_i_titoli_nuovi_nella_lingua_scelta_e_nessun_doppione_cambiandola():
    g = _grafo()
    n = _del_file(g)
    en.scaffold(g, write_lang="it")
    quanti = len(n.chapters)
    en.scaffold(g, write_lang="en")                              # un'altra lingua: niente «Presentation»
    en.scaffold(g)                                               # né con quella della narrativa
    assert len(n.chapters) == quanti
    assert "Presentation" not in [c.title for c in n.chapters]


def test_una_lingua_che_il_template_non_ha_traduce_i_due_titoli_fissi():
    g = _grafo()
    n = en.scaffold(g, write_lang="de")
    titoli = [c.title for c in n.chapters]
    assert titoli[0] == "Präsentation" and "Wo es liegt" in titoli
    en.scaffold(g, write_lang="it")
    assert len(n.chapters) == len(titoli)                        # «Presentazione» non si aggiunge


# --------------------------------------------------------- riesportare

def test_carry_over_sostituisce_la_narrativa_ricordata_solo_se_si_chiede():
    vecchio, nuovo = _grafo(), _grafo()
    lavorata = _del_file(vecchio)
    en.scaffold(vecchio, write_lang="it")                        # 2 + i capitoli di pyArchInit
    _del_file(nuovo)                                             # quella dell'importazione: 2
    assert en.carry_over({"Villa": vecchio}, {"Villa": nuovo}, "it") == 0
    assert len(en.narrative_of(nuovo).chapters) == 2
    assert en.carry_over({"Villa": vecchio}, {"Villa": nuovo}, "it", replace=True) == 1
    assert len(en.narrative_of(nuovo).chapters) == len(lavorata.chapters)
    assert len(en.narratives_of(nuovo)) == 1


def _file_lavorato(tmp_path):
    vecchio = _grafo()
    _del_file(vecchio)
    en.scaffold(vecchio, write_lang="it")
    percorso = tmp_path / "Villa.em.json"
    en.save_project(_container(vecchio), percorso)
    return percorso, len(en.narrative_of(vecchio).chapters)


def _non_passata(avviso):
    """L'avviso di prima, che dava la colpa alla «forma del file»."""
    return avviso == en.msg("narrative_not_travelled", old="Villa", new="Villa",
                            bak="Villa.em.json.bak")


def test_riesportando_vince_il_file_se_e_piu_recente_dell_importazione(tmp_path):
    from modules.s3dgraphy import em_export
    percorso, quanti = _file_lavorato(tmp_path)
    nuovo = _grafo()
    _del_file(nuovo)                                             # rimessa da em_sources
    avvisi = em_export._keep_narrative(str(percorso), None, nuovo, "Villa",
                                       imported_at=os.path.getmtime(percorso) - 3600)
    assert len(en.narrative_of(nuovo).chapters) == quanti
    assert avvisi and not any(_non_passata(a) for a in avvisi)


def test_riesportando_vince_l_importazione_se_e_piu_recente_del_file(tmp_path):
    from modules.s3dgraphy import em_export
    percorso, _quanti = _file_lavorato(tmp_path)
    nuovo = _grafo()
    _del_file(nuovo)
    avvisi = em_export._keep_narrative(str(percorso), None, nuovo, "Villa",
                                       imported_at=time.time() + 3600)
    assert len(en.narrative_of(nuovo).chapters) == 2
    assert avvisi and "import" in avvisi[0].lower() and not _non_passata(avvisi[0])
    assert Path(str(percorso) + ".bak").is_file()


def test_export_site_passa_l_ora_dell_importazione():
    src = (_ROOT / "modules" / "s3dgraphy" / "em_export.py").read_text(encoding="utf-8")
    assert "imported_at=" in src and "source_imported_at(" in src


def test_l_ora_dell_importazione_si_legge_dalla_memoria(tmp_path):
    import json
    from modules.s3dgraphy.sync.em_sources import remember_source, source_imported_at
    db = tmp_path / "db.sqlite"
    em = tmp_path / "t.em.json"
    em.write_text(json.dumps({"graphs": {"g": {"nodes": [], "edges": []}}}), encoding="utf-8")
    assert source_imported_at(db, "Villa") is None
    assert remember_source(db, "Villa", str(em))
    quando = source_imported_at(db, "Villa")
    assert quando is not None and abs(quando - time.time()) < 120
