"""Il modello della matrice, letto dall'em.json (2026-10-08).

Chiesto da Enzo: vedere la matrice dentro QGIS, senza EMStudio e senza
nodo. Si parte dall'em.json e non dal grafo in memoria, così quello che
si vede nel pannello è esattamente quello che viaggia nel file.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility.em_matrix_model import (  # noqa: E402
    read_em_json,
    style_for,
)

SITO = "Scavo archeologico"


@pytest.fixture(scope="module")
def sample_emjson(tmp_path_factory):
    """L'em.json del sito di esempio, esportato una volta per sessione."""
    tmp_path = tmp_path_factory.mktemp("emjson")
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    vecchia = os.environ.get("PYARCHINIT_HOME")
    os.environ["PYARCHINIT_HOME"] = str(tmp_path)
    try:
        from modules.s3dgraphy import em_export
        path, _n, _e, _w = em_export.export_site(
            "sqlite:///%s" % (folder / "db.sqlite"), SITO, str(tmp_path / "out"))
    finally:
        if vecchia is None:
            os.environ.pop("PYARCHINIT_HOME", None)
        else:
            os.environ["PYARCHINIT_HOME"] = vecchia
    return path


def test_the_model_reads_units_epochs_and_relations(sample_emjson):
    model = read_em_json(sample_emjson)
    assert len(model.units) == 51          # le 51 righe della scheda
    assert len(model.epochs) == 12
    assert {r.kind for r in model.relations} >= {"overlies", "cuts", "fills"}
    per_label = {u.label: u for u in model.units}
    assert per_label["1.US9"].epoch_id == per_label["1.US3"].epoch_id


def test_only_the_stratigraphic_relations_are_kept(sample_emjson):
    """Le proprietà, la documentazione, le aree e gli autori non sono
    rapporti stratigrafici e non vanno disegnati come frecce."""
    model = read_em_json(sample_emjson)
    assert not {"has_property", "has_documentation", "is_in_location",
                "has_author", "has_first_epoch", "survive_in_epoch"} & {
        r.kind for r in model.relations}


def test_the_epochs_come_out_newest_first(sample_emjson):
    model = read_em_json(sample_emjson)
    anni = [e.start for e in model.epochs]
    assert anni == sorted(anni, reverse=True), anni
    assert model.epochs[0].name == "Età contemporanea"


def test_a_unit_without_an_epoch_is_kept():
    model = read_em_json({"graphs": {"S": {"nodes": [
        {"id": "u1", "name": "1.US1", "node_type": "US", "data": {"us": "1"}}],
        "edges": []}}})
    assert len(model.units) == 1
    assert model.units[0].epoch_id is None
    assert model.units[0].label == "1.US1"


def test_the_symbology_is_the_extended_matrix_one():
    """Forma e colori vengono dalle regole visive della libreria
    (ext_libs/s3dgraphy/JSON_config/em_visual_rules.json), non da una
    tabella nostra che prima o poi divergerebbe."""
    assert style_for("US").shape == "rectangle"
    assert style_for("US").stroke == "#9B3333"
    assert style_for("USVs").shape == "parallelogram"
    assert style_for("USVn").shape == "hexagon"
    assert style_for("SF").shape == "octagon"
    assert style_for("BR").shape == "diamond"


def test_the_paradata_types_are_translated_to_their_initials():
    """I nostri node_type sono «document», «extractor»…; le regole visive
    li chiamano DOC, EXT, COMB, PROP."""
    assert style_for("document").shape == "ellipse"
    assert style_for("extractor").shape == "pentagon"
    assert style_for("combiner").shape == "hexagon"
    assert style_for("property").shape == "circle"


def test_an_unknown_type_still_gets_a_shape():
    s = style_for("QUALCOSA")
    assert s.shape == "rectangle"
    assert s.fill and s.stroke


def test_a_file_that_is_not_an_emjson_says_so(tmp_path):
    rotto = tmp_path / "rotto.em.json"
    rotto.write_text("{non è json", encoding="utf-8")
    with pytest.raises(ValueError, match="em.json"):
        read_em_json(rotto)


def test_a_document_hanging_from_a_unit_is_not_a_unit(sample_emjson):
    """«Fotografie: Sì» è decorazione della scheda, non un nodo della
    matrice: nel sito di esempio sono cinque, e non devono comparire fra
    le unità. Le righe DOC di us_table, che partecipano a un rapporto,
    restano."""
    model = read_em_json(sample_emjson)
    etichette = {u.label for u in model.units}
    assert "Fotografie" not in etichette and "Planimetrie" not in etichette
    assert "1.DOC4001" in etichette


@pytest.mark.parametrize("storto", [
    {"graphs": {"S": "ciao"}},
    {"graphs": {"S": []}},
    {"graphs": {"S": {"nodes": {"a": 1}, "edges": []}}},
    {"graphs": {"S": {"nodes": [], "edges": {"a": 1}}}},
    {"graphs": {"S": {"nodes": ["non un nodo"], "edges": []}}},
    {"graphs": {"S": {"nodes": [], "edges": ["non un rapporto"]}}},
])
def test_a_file_that_cannot_be_read_says_so_in_a_sentence(storto):
    """Dalla review: queste forme uscivano come AttributeError o
    TypeError, e all'archeologo arrivava un errore Python in inglese. Il
    contratto è uno solo: ValueError con una frase."""
    with pytest.raises(ValueError):
        read_em_json(storto)


@pytest.mark.parametrize("storto", [
    {"graphs": {"S": {"nodes": [{"id": "u", "node_type": "US",
                                 "data": "non un dizionario"}], "edges": []}}},
    {"graphs": {"S": {"nodes": [{"id": "e", "node_type": "EpochNode",
                                 "data": {"start_time": {"a": 1}}}],
                      "edges": []}}},
    {"graphs": {"S": {"nodes": [{"id": "e", "node_type": "EpochNode",
                                 "data": {"start_time": "XIII secolo"}}],
                      "edges": []}}},
])
def test_a_field_written_badly_does_not_throw_away_the_site(storto):
    """Un dato storto in una casella non vale il rifiuto di tutto il
    disegno: si legge quello che si può, il resto vale zero, e il sito si
    vede lo stesso."""
    model = read_em_json(storto)
    assert model is not None


def test_an_epoch_without_dates_does_not_jump_the_queue():
    """Un'epoca senza anni diventava 0 e si infilava fra il romano e il
    medievale. Va in fondo, dove sta quello che non si sa datare."""
    model = read_em_json({"graphs": {"S": {"nodes": [
        {"id": "a", "name": "Età contemporanea", "node_type": "EpochNode",
         "data": {"start_time": 1800, "end_time": 2022}},
        {"id": "b", "name": "Senza date", "node_type": "EpochNode",
         "data": {}},
        {"id": "c", "name": "Medievale", "node_type": "EpochNode",
         "data": {"start_time": 1200, "end_time": 1400}}],
        "edges": []}}})
    assert [e.name for e in model.epochs] == [
        "Età contemporanea", "Medievale", "Senza date"]


def test_an_active_graph_that_is_not_there_is_said_not_assumed():
    """Dalla review: con un active_graph_id inesistente si disegnava il
    primo grafo col titolo di quello chiesto. Si disegna quello che c'è,
    si intitola per quello che è, e lo si dice."""
    model = read_em_json({
        "active_graph_id": "NON_ESISTE",
        "graphs": {"Primo": {"nodes": [], "edges": []},
                   "Secondo": {"nodes": [], "edges": []}}})
    assert model.title == "Primo"
    assert any("NON_ESISTE" in w for w in model.warnings), model.warnings


def test_two_nodes_without_an_id_are_both_kept():
    """Diventavano la stessa chiave «None» e uno spariva."""
    model = read_em_json({"graphs": {"S": {"nodes": [
        {"name": "1.US1", "node_type": "US", "data": {"us": "1"}},
        {"name": "1.US2", "node_type": "US", "data": {"us": "2"}}],
        "edges": []}}})
    assert len(model.units) == 2
    assert len({u.node_id for u in model.units}) == 2


def test_what_is_left_out_of_the_drawing_is_written_down():
    """I nodi che non entrano nella matrice (una voce di spunta della
    documentazione) non devono sparire in silenzio."""
    model = read_em_json({"graphs": {"S": {"nodes": [
        {"id": "u", "name": "1.US1", "node_type": "US", "data": {"us": "1"}},
        {"id": "d", "name": "Fotografie", "node_type": "document"}],
        "edges": []}}})
    assert len(model.units) == 1
    assert any("Fotografie" in w or "1" in w for w in model.warnings), \
        model.warnings
