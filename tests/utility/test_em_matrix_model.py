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
