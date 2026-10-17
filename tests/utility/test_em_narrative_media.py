"""I media che illustrano la narrativa: li sceglie l'AI fra quelli delle
unità di cui il capitolo parla, seguendo il filo del testo, e la scelta
resta nel file (Enzo, 17 ottobre 2026: «l'AI in modo deterministico possa
scegliere i media, 3D, da incorporare nella narrativa seguendo il filo
logico della narrativa»). Senza AI la scelta è automatica: i media delle
unità nell'ordine in cui il testo le nomina."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import em_narrative_media as nm  # noqa: E402


def _cand(key, unit, kind="3d", name=None):
    return nm.MediaCandidate(key=key, unit_id=unit, unit_name=unit.upper(), filename=name or key,
                             kind=kind, description="desc " + unit)


def test_il_tipo_del_media_dal_nome_del_file():
    assert nm.media_kind("SU002.glb") == "3d" and nm.media_kind("colonna.OBJ") == "3d"
    assert nm.media_kind("D.07.05.jpg") == "image" and nm.media_kind("scavo.mp4") == "video"
    assert nm.media_kind("D.05 Relazione.pdf") is None                # i documenti sono fonti


def test_la_risposta_dell_ai_si_controlla():
    candidati = [_cand("a", "u1"), _cand("b", "u2"), _cand("c", "u3")]
    testo = ("Ecco:\n```json\n" + json.dumps({"choices": [
        {"key": "b", "after": 1, "caption": "La colonna."},
        {"key": "zz", "after": 0, "caption": "inventato"},                 # non è un candidato
        {"key": "b", "after": 2, "caption": "doppione"},
        {"key": "a", "after": 99, "caption": "x" * 400}]}) + "\n```")
    scelte = nm.parse_choices(testo, candidati, n_paragrafi=3)
    assert [s["key"] for s in scelte] == ["b", "a"]
    assert scelte[1]["after"] == 3                                      # in fondo, non oltre
    assert len(scelte[1]["caption"]) <= 200


def test_senza_ai_i_media_delle_unita_nell_ordine_del_testo():
    candidati = [_cand("m1", "u1"), _cand("m2", "u2", "image"), _cand("m3", "u3")]
    paragrafi = ["Si parte da U2 e dal suo crollo.", "Poi U1 lo copre.", "Niente di U3 qui? Sì: U3."]
    scelte = nm.auto_choices(paragrafi, candidati, massimo=2)
    assert [(s["key"], s["after"]) for s in scelte] == [("m2", 1), ("m1", 2)]
    assert all(s["by"] == "auto" for s in scelte)


def test_le_istruzioni_chiedono_json_temperatura_zero_e_la_lingua():
    candidati = [_cand("a", "u1"), _cand("b", "u2", "image")]
    msgs = nm.media_messages("VAct.01", ["Primo.", "Secondo."], candidati, "it")
    assert msgs[0]["role"] == "system" and "JSON" in msgs[0]["content"]
    assert "italiano" in msgs[0]["content"].lower()
    corpo = msgs[1]["content"]
    assert '"a"' in corpo and '"b"' in corpo and "[1] Primo." in corpo
    assert nm.media_messages("x", ["p"], candidati, "de")[0]["content"].count("German") == 1


def test_la_scelta_resta_nella_narrativa_per_capitolo():
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    n = NarrativeNode(node_id="narr", name="T")
    ancorato = n.add_chapter("VAct.01", anchor="a1")
    libero = n.add_chapter("Introduzione", canonical=True)
    nm.store_choices(n, ancorato, [{"key": "a", "after": 1, "caption": "c", "by": "ai"}])
    nm.store_choices(n, libero, [{"key": "b", "after": 0, "caption": "", "by": "auto"}])
    assert nm.stored_choices(n, ancorato)[0]["key"] == "a"
    assert nm.stored_choices(n, libero)[0]["key"] == "b"
    dati = n.to_data()
    assert "pyarchinit_media" in json.dumps(dati, ensure_ascii=False)
    nm.store_choices(n, ancorato, [])
    assert nm.stored_choices(n, ancorato) == []


def test_choose_media_chiede_all_ai_e_salva_la_scelta(monkeypatch):
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    n = NarrativeNode(node_id="narr", name="T")
    cap = n.add_chapter("VAct.01", anchor="a1")
    cap.add_prose("La colonna T19 era alta.\n\nPoi crollò.")
    candidati = {id(cap): [_cand("t19.glb", "t19"), _cand("foto.jpg", "t19", "image")]}
    monkeypatch.setattr(nm, "chapter_media_candidates",
                        lambda graph, chapter, *a, **k: candidati.get(id(chapter), []))
    chiesti = []

    def chat(messages):
        chiesti.append(messages)
        return json.dumps({"choices": [{"key": "foto.jpg", "after": 1, "caption": "La colonna."}]})
    esito = nm.choose_media(None, n, chat=chat, model="m", lang="it", connection=None,
                            media_base=("", ""))
    assert len(chiesti) == 1 and esito.chosen == 1 and esito.chapters == 1
    scelta = nm.stored_choices(n, cap)[0]
    assert scelta["key"] == "foto.jpg" and scelta["by"] == "ai" and scelta["model"] == "m"


def test_se_l_ai_sbaglia_si_sceglie_da_soli(monkeypatch):
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    n = NarrativeNode(node_id="narr", name="T")
    cap = n.add_chapter("VAct.01", anchor="a1")
    cap.add_prose("La colonna T19 era alta.")
    monkeypatch.setattr(nm, "chapter_media_candidates",
                        lambda graph, chapter, *a, **k: [_cand("t19.glb", "t19")])

    def chat(messages):
        raise RuntimeError("rete giù")
    esito = nm.choose_media(None, n, chat=chat, model="m", lang="it", connection=None,
                            media_base=("", ""))
    assert esito.failed == 1
    assert [s["by"] for s in nm.stored_choices(n, cap)] == ["auto"]


def test_i_paragrafi_nominano_le_unita_per_nome():
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="T")
    g.add_node(StratigraphicUnit("uuid-1", "SU004"))
    n = NarrativeNode(node_id="narr", name="T")
    cap = n.add_chapter("Uno")
    cap.add_prose("Il livello di [[uuid-1]].\n\n### Sottotitolo\n\nAltro.")
    assert nm.chapter_paragraphs(cap, g) == ["Il livello di SU004.", "Altro."]


# ------------------------------------------------ i media dentro la pagina

_PAGINA_M = ("<!doctype html><html><head><style>body{}</style></head><body>\n<h1>T</h1>\n"
             "<h2>Uno</h2>\n<p>Primo paragrafo.</p>\n<p>### Un sottotitolo</p>\n<p>Secondo paragrafo.</p>\n"
             "<h2>Due</h2>\n<p>Altro.</p>\n"
             "<footer class=\"em-footer\">snapshot</footer>\n</body></html>\n")

_REG_M = {
    "m::a": {"title": "SU004.glb", "description": "Il muro di fondazione.", "kind": "3D",
             "unit": "SU004", "model": True, "preview": "data:image/png;base64,AAA",
             "file": "Z2xURg==", "mime": "model/gltf-binary", "link": "", "path": "/x/SU004.glb", "uses": []},
    "m::b": {"title": "foto.jpg", "description": "", "kind": "JPG", "unit": "T19",
             "preview": "data:image/jpeg;base64,BBB", "file": "", "mime": "image/jpeg",
             "link": "", "path": "", "uses": []},
}


def test_il_media_va_dopo_il_paragrafo_scelto():
    fuori = nm.add_media(_PAGINA_M, [[{"key": "m::a", "after": 2, "caption": "Il muro."}],
                                     [{"key": "m::b", "after": 0, "caption": ""}]], _REG_M, "it")
    uno = fuori[fuori.index("<h2>Uno</h2>"):fuori.index("<h2>Due</h2>")]
    # il sottotitolo non conta: «dopo il paragrafo 2» è dopo «Secondo paragrafo»
    assert uno.index("Secondo paragrafo") < uno.index('class="pya-media"')
    assert 'data-src="m::a"' in uno and "Il muro." in uno and "SU004" in uno
    due = fuori[fuori.index("<h2>Due</h2>"):]
    assert due.index('data-src="m::b"') < due.index("Altro.")       # «dopo 0»: prima del primo


def test_un_media_senza_voce_nel_registro_non_si_mette():
    fuori = nm.add_media(_PAGINA_M, [[{"key": "m::zz", "after": 1, "caption": ""}], []], _REG_M, "it")
    assert "pya-media" not in fuori


def test_il_modello_3d_si_apre_nel_visore():
    from modules.s3dgraphy import em_narrative_html as nh
    fuori = nm.add_media(_PAGINA_M, [[{"key": "m::a", "after": 1, "caption": ""}], []], _REG_M, "it")
    fuori = nh.add_sources(fuori, [[], []], _REG_M, "it")
    assert "model-viewer" in fuori and "unpkg.com/@google/model-viewer" in fuori
    assert 'id="pya-pannello"' in fuori


def test_due_capitoli_con_la_stessa_ancora_hanno_ognuno_la_sua_scelta():
    """In TempluMare «Virtual Activity 2» e «Virtual Activity 3» sono ancorati
    alla stessa attività (VAct.03): con l'àncora come chiave la scelta del
    terzo capitolo prendeva il posto di quella del secondo."""
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    n = NarrativeNode(node_id="narr", name="T")
    due = n.add_chapter("Virtual Activity 2: colonnade", anchor="vact03", canonical=True)
    tre = n.add_chapter("Virtual Activity 3: lintel", anchor="vact03", canonical=True)
    nm.store_choices(n, due, [{"key": "USV104.glb", "after": 5, "caption": "", "by": "auto"}])
    nm.store_choices(n, tre, [{"key": "USV106.glb", "after": 1, "caption": "", "by": "auto"}])
    assert [s["key"] for s in nm.stored_choices(n, due)] == ["USV104.glb"]
    assert [s["key"] for s in nm.stored_choices(n, tre)] == ["USV106.glb"]
