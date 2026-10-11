"""L'anteprima della matrice della scheda US: il filtro e l'impaginazione.

Enzo, 2026-10-11: «nella scheda us nella tab rapporti c'è anche un
bottone preview matrix … è collegato a graphviz quindi ripuntiamo invece
s3d e deve funzionare con il filtro applicato, ad esempio se ho fatto
una query dove vedo solo le us dalla 1 alla 10 il matrix deve generare
quello e non tutto; e potresti far apparire anche le us disegnate, nella
stessa immagine del template, sotto il matrix, e me lo fai esportare in
png quindi non nel canvas».

Qui si prova la parte che decide: quali unità restano, come si ritrovano
le geometrie nei layer, quanto viene grande l'immagine e dove va ogni
pezzo. Niente Qt — costruire un widget sotto pytest, in questo ambiente,
ammazza il processo — e niente database.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.em_matrix_model import (  # noqa: E402
    Epoch, MatrixModel, Relation, Unit)
from modules.utility.matrix_preview import (  # noqa: E402
    GUTTER, PLAN_FIELD_SETS, PLAN_MIN_H, PLAN_MIN_W, Identity, choose_site,
    compose, filter_model, identities_from_records, key_of_unit, keys_of,
    layer_filter, plan_size, plan_source)


def _unit(us, tipo="US", area="1", sito="Alfa", epoca="2_1", node_type="US"):
    return Unit(node_id="%s.%s%s" % (area, tipo, us),
                label="%s.%s%s" % (area, tipo, us),
                node_type=node_type, epoch_id=epoca,
                data=dict(sito=sito, area=area, us=us, unita_tipo=tipo))


def _model(units, relations=(), epochs=None):
    return MatrixModel(
        units=list(units), relations=list(relations),
        epochs=list(epochs if epochs is not None
                    else [Epoch(node_id="2_1", name="XV secolo",
                                start=1451, end=1499)]),
        title="Alfa")


class _Riga:
    """Una riga di ``DATA_LIST``: un oggetto del mappatore, non un dizionario."""

    def __init__(self, sito, area, us, unita_tipo):
        self.sito, self.area, self.us, self.unita_tipo = (
            sito, area, us, unita_tipo)


# ------------------------------------------- il filtro viene da DATA_LIST

def test_the_filter_is_the_four_column_identity():
    """Non il solo numero: la US 1 dell'area 1 non è la US 1 dell'area 2.

    Il resto del plugin le distingue da tempo; una matrice che le
    confondesse contraddirebbe la scheda da cui nasce."""
    identita = identities_from_records([
        _Riga("Alfa", "1", "1", "US"), _Riga("Alfa", "2", "1", "US")])
    assert len(identita) == 2
    assert keys_of(identita) == {("Alfa", "1", "1", "us"),
                                 ("Alfa", "2", "1", "us")}


def test_records_may_be_dictionaries_too():
    identita = identities_from_records([
        dict(sito="Alfa", area="1", us="7", unita_tipo="USM")])
    assert identita[0] == Identity("Alfa", "1", "7", "USM")


def test_a_row_without_site_or_number_identifies_nothing():
    identita = identities_from_records([
        _Riga("", "1", "1", "US"), _Riga("Alfa", "1", "", "US"),
        _Riga("Alfa", "1", "2", "US")])
    assert [i.us for i in identita] == ["2"]


def test_the_same_unit_twice_counts_once():
    identita = identities_from_records([
        _Riga("Alfa", "1", "1", "US"), _Riga("Alfa", "1", "1", "US")])
    assert len(identita) == 1


def test_the_old_spelling_of_a_virtual_type_still_matches():
    """``USVA`` e ``USVs`` sono la stessa cosa scritta prima e dopo la
    migrazione del vocabolario: confrontarle alla lettera farebbe
    sparire dalla matrice unità che la query ha scelto."""
    vecchia = Identity("Alfa", "1", "102", "USVA")
    nuova = Identity("Alfa", "1", "102", "USVs")
    assert vecchia.key == nuova.key


def test_a_unit_of_the_emjson_gives_the_same_key():
    assert key_of_unit(_unit("1")) == ("Alfa", "1", "1", "us")


def test_a_node_that_is_not_a_record_has_no_key():
    """Un'epoca, un gruppo: cercarli nella scheda non avrebbe senso."""
    assert key_of_unit(Unit(node_id="e", label="e", node_type="EpochNode",
                            epoch_id=None, data={})) is None


def test_the_search_decides_which_site_is_drawn():
    """La casella del sito si può cambiare senza rifare la ricerca: se
    non è fra i siti delle righe trovate varrebbe il grafo di un sito che
    con queste unità non c'entra, e la matrice uscirebbe vuota."""
    identita = identities_from_records([_Riga("Alfa", "1", "1", "US")])
    assert choose_site(identita, "Beta") == ("Alfa", [])
    assert choose_site(identita, "") == ("Alfa", [])


def test_a_search_over_two_sites_names_the_one_left_out():
    identita = identities_from_records([_Riga("Alfa", "1", "1", "US"),
                                        _Riga("Beta", "1", "1", "US")])
    assert choose_site(identita, "Beta") == ("Beta", ["Alfa"])
    assert choose_site(identita, None) == ("Alfa", ["Beta"])


# ------------------------------------------------- la matrice si restringe

def test_only_the_filtered_units_are_drawn():
    model = _model([_unit("1"), _unit("2"), _unit("30")])
    ridotto = filter_model(model, {("Alfa", "1", "1", "us"),
                                   ("Alfa", "1", "2", "us")})
    assert {u.label for u in ridotto.units} == {"1.US1", "1.US2"}


def test_an_edge_with_one_end_outside_keeps_its_box_but_faded():
    """La scelta: si tiene la casella all'altro capo, sbiadita.

    Buttare l'arco direbbe che la US scelta non copre niente, cioè una
    cosa falsa sulla stratigrafia; disegnare la casella come le altre
    farebbe credere che sia fra quelle filtrate. È la stessa convenzione
    del Time Manager (``Unit.dimmed``)."""
    model = _model([_unit("1"), _unit("2")],
                   [Relation(source="1.US1", target="1.US2",
                             kind="overlies")])
    ridotto = filter_model(model, {("Alfa", "1", "1", "us")})
    etichette = {u.label: u.dimmed for u in ridotto.units}
    assert etichette == {"1.US1": False, "1.US2": True}
    assert len(ridotto.relations) == 1


def test_the_faded_box_does_not_bring_its_own_neighbours():
    """Un salto solo: se no una US tirerebbe dentro mezzo scavo."""
    model = _model([_unit("1"), _unit("2"), _unit("3")],
                   [Relation(source="1.US1", target="1.US2", kind="overlies"),
                    Relation(source="1.US2", target="1.US3", kind="overlies")])
    ridotto = filter_model(model, {("Alfa", "1", "1", "us")})
    assert {u.label for u in ridotto.units} == {"1.US1", "1.US2"}
    # e il rapporto fra due sbiadite non si disegna: quella casella è lì
    # per mostrare dove va il rapporto della US scelta
    assert [(r.source, r.target) for r in ridotto.relations] == [
        ("1.US1", "1.US2")]


def test_a_relation_between_two_faded_boxes_is_not_drawn():
    model = _model([_unit("1"), _unit("2"), _unit("3")],
                   [Relation(source="1.US1", target="1.US2", kind="overlies"),
                    Relation(source="1.US1", target="1.US3", kind="overlies"),
                    Relation(source="1.US2", target="1.US3", kind="overlies")])
    ridotto = filter_model(model, {("Alfa", "1", "1", "us")})
    assert len(ridotto.units) == 3
    assert ("1.US2", "1.US3") not in [(r.source, r.target)
                                      for r in ridotto.relations]


def test_the_paradata_hanging_off_a_filtered_unit_comes_along():
    """Enzo si lamentava di non vedere combinatori, estrattori, proprietà
    e documenti: col motore di s3dgraphy ci sono, e il filtro non li
    butta se stanno attaccati a una unità scelta."""
    estrattore = _unit("400", tipo="Extractor", node_type="extractor")
    model = _model([_unit("106"), estrattore],
                   [Relation(source="1.Extractor400", target="1.US106",
                             kind="extracted_from")])
    ridotto = filter_model(model, {("Alfa", "1", "106", "us")})
    assert {u.node_type for u in ridotto.units} == {"US", "extractor"}


def test_an_epoch_left_without_units_goes_away():
    """Una fascia vuota occupa altezza e non racconta niente: l'immagine
    deve adattarsi al contenuto."""
    epoche = [Epoch(node_id="2_1", name="XV secolo", start=1451, end=1499),
              Epoch(node_id="1_1", name="Età moderna", start=1600, end=1799)]
    model = _model([_unit("1", epoca="2_1"), _unit("2", epoca="1_1")],
                   epochs=epoche)
    ridotto = filter_model(model, {("Alfa", "1", "1", "us")})
    assert [e.name for e in ridotto.epochs] == ["XV secolo"]


def test_without_a_filter_the_whole_site_is_drawn():
    model = _model([_unit("1"), _unit("2")])
    assert filter_model(model, frozenset()) is model


def test_a_filter_that_matches_nothing_says_so_and_draws_everything():
    """Meglio una matrice intera con un avviso che un'immagine vuota."""
    model = _model([_unit("1")])
    ridotto = filter_model(model, {("Beta", "1", "99", "us")})
    assert len(ridotto.units) == 1
    assert any("Nessuna delle unità filtrate" in a for a in ridotto.warnings)


def test_the_filtered_model_says_how_much_it_left_out():
    model = _model([_unit("1"), _unit("2"), _unit("3")])
    ridotto = filter_model(model, {("Alfa", "1", "1", "us")})
    assert any("non entrano in questa matrice" in a for a in ridotto.warnings)


# ------------------------------------------- le geometrie sulla pianta

#: I campi veri delle tabelle dei disegni del database di esempio.
CAMPI_US = ["gid", "area_s", "scavo_s", "us_s", "stratigraph_index_us",
            "tipo_us_s", "the_geom", "unita_tipo_s"]
CAMPI_QUOTE = ["gid", "sito_q", "area_q", "us_q", "quota_q", "the_geom",
               "unita_tipo_q"]


def test_the_drawing_fields_are_the_ones_the_zoom_already_knows():
    """Due copie che divergono sono peggio di una copia sola: i nomi dei
    campi dei disegni vengono da ``em_matrix_links.FIELD_SETS``."""
    from modules.utility.em_matrix_links import FIELD_SETS

    assert PLAN_FIELD_SETS[:len(FIELD_SETS)] == FIELD_SETS
    assert PLAN_FIELD_SETS[-1] == ("sito_q", "area_q", "us_q", "unita_tipo_q")


def test_the_us_drawing_table_is_filtered_by_site_area_and_number():
    espressione = layer_filter(
        [Identity("Alfa", "1", "1", "US"), Identity("Alfa", "1", "2", "US")],
        CAMPI_US)
    assert '"scavo_s" = \'Alfa\'' in espressione
    assert '"area_s" = \'1\'' in espressione
    assert '"us_s" IN (\'1\', \'2\')' in espressione


def test_the_quote_table_is_filtered_with_its_own_field_names():
    espressione = layer_filter([Identity("Alfa", "1", "1", "US")],
                               CAMPI_QUOTE)
    assert '"sito_q" = \'Alfa\'' in espressione
    assert '"us_q" IN (\'1\')' in espressione


def test_a_layer_that_knows_nothing_is_left_out_of_the_plan():
    """``None`` vuol dire «questo layer non sa chi sono»: meglio lasciarlo
    fuori che disegnarci tutto lo scavo."""
    assert layer_filter([Identity("Alfa", "1", "1", "US")],
                        ["gid", "the_geom"]) is None


def test_the_type_is_compared_with_tolerance():
    """``unita_tipo_s`` è una colonna aggiunta ai disegni ed è vuota in
    ogni database visto finora: nel sito di esempio è NULL su tutte e 700
    le quote. Una geometria in più si vede e si capisce; una pianta vuota
    perché la colonna non è stata riempita, no."""
    espressione = layer_filter([Identity("Alfa", "1", "1", "US")], CAMPI_US)
    assert '"unita_tipo_s" IS NULL' in espressione
    assert '"unita_tipo_s" = \'US\'' in espressione


def test_an_apostrophe_in_the_site_name_does_not_break_the_expression():
    espressione = layer_filter([Identity("L'Aquila", "1", "1", "US")],
                               CAMPI_US)
    assert "'L''Aquila'" in espressione


def test_two_areas_become_two_groups_joined_by_or():
    espressione = layer_filter(
        [Identity("Alfa", "1", "1", "US"), Identity("Alfa", "2", "5", "US")],
        CAMPI_US)
    assert espressione.count('"scavo_s" = \'Alfa\'') == 2
    assert " OR " in espressione


def test_many_units_do_not_become_a_chain_of_ors():
    """Con 1300 US una catena di OR a quattro condizioni è un'espressione
    che QGIS valuta per ogni geometria del layer."""
    espressione = layer_filter(
        [Identity("Alfa", "1", str(n), "US") for n in range(1, 400)],
        CAMPI_US)
    assert espressione.count('"scavo_s" = ') == 1
    assert espressione.count('"us_s" IN (') == 1


# ------------------------------------------------- quanto viene grande

def test_the_plan_is_as_wide_as_the_matrix():
    assert plan_size(1200, (0, 0, 100, 50)) == (1200, 600)


def test_a_narrow_matrix_does_not_make_an_unreadable_strip():
    larghezza, altezza = plan_size(80, (0, 0, 100, 10))
    assert larghezza == PLAN_MIN_W
    assert altezza == PLAN_MIN_H


def test_a_tall_excavation_does_not_grow_without_end():
    _larghezza, altezza = plan_size(1000, (0, 0, 10, 100000))
    assert altezza <= 2800


def test_a_single_point_is_drawn_square():
    """Una quota sola, una US con un vertice solo: si disegna comunque."""
    assert plan_size(1000, (5, 5, 5, 5)) == (1000, 1000)


def test_without_geometries_there_is_no_plan():
    assert plan_size(1000, None) is None


# -------------------------------------------------- matrice sopra, pianta sotto

def test_the_matrix_goes_above_and_the_plan_below():
    misura = compose((800, 600), (800, 300))
    assert misura.width == 800
    assert misura.height == 600 + GUTTER + 300
    assert misura.matrix_at == (0, 0)
    assert misura.plan_at == (0, 600 + GUTTER)


def test_the_narrower_piece_is_centred():
    """Una colonna sbilanciata si legge come un errore di impaginazione."""
    misura = compose((400, 100), (800, 100))
    assert misura.width == 800
    assert misura.matrix_at == (200, 0)
    assert misura.plan_at == (0, 100 + GUTTER)


def test_with_the_matrix_alone_there_is_no_gutter_and_no_divider():
    """Uno scavo senza disegno: l'immagine esce con la sola matrice."""
    misura = compose((800, 600), None)
    assert (misura.width, misura.height) == (800, 600)
    assert misura.plan_at is None
    assert misura.divider_y is None


def test_the_divider_runs_in_the_gutter():
    misura = compose((800, 600), (800, 300))
    assert 600 <= misura.divider_y <= 600 + GUTTER


def test_nothing_to_compose_gives_nothing():
    assert compose(None, None) is None
    assert compose((0, 0), None) is None


# ------------------------------------------------ da dove vengono i layer

def test_the_sqlite_file_comes_from_the_connection_string():
    fonte = plan_source("sqlite:////tmp/pyarchinit_db.sqlite")
    assert fonte.provider == "ogr"
    assert fonte.path == "/tmp/pyarchinit_db.sqlite"


def test_the_postgres_pieces_come_from_the_connection_string():
    fonte = plan_source(
        "postgresql://utente:parola@localhost:5433/scavo?sslmode=allow")
    assert (fonte.provider, fonte.host, fonte.port) == (
        "postgres", "localhost", "5433")
    assert (fonte.database, fonte.user, fonte.password) == (
        "scavo", "utente", "parola")


def test_a_connection_string_we_do_not_know_gives_nothing():
    assert plan_source("") is None
    assert plan_source("mysql://x/y") is None
    assert plan_source("sqlite:///:memory:") is None


# ------------------------------- le promesse del pezzo che tocca QGIS
# Come per la vista della matrice: qui non si istanzia nessun widget —
# costruirne uno sotto pytest, in questo ambiente, ammazza il processo.
# Si leggono le promesse nel sorgente.

_RENDER = _ROOT / "modules" / "utility" / "matrix_preview_png.py"
_SCHEDA = _ROOT / "tabs" / "US_USM.py"


def _sorgente(percorso) -> str:
    return Path(percorso).read_text(encoding="utf-8")


def _codice(percorso) -> str:
    """Il sorgente senza commenti né stringhe: si guardano le righe che
    fanno qualcosa, non quelle che spiegano perché."""
    import io
    import tokenize

    pezzi = []
    with io.open(percorso, "rb") as fh:
        for token in tokenize.tokenize(fh.readline):
            if token.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            pezzi.append(token.string)
    return " ".join(pezzi)


def test_the_image_is_not_a_print_layout():
    """Una composizione di stampa è una pagina fissa; Enzo ha chiesto
    un'immagine che si adatti al contenuto."""
    codice = _codice(_RENDER)
    assert "QgsPrintLayout" not in codice
    assert "QgsLayoutExporter" not in codice


def test_the_matrix_is_drawn_in_a_scene_not_in_a_widget():
    """Per salvare un'immagine una finestra non serve, e un widget sotto
    i test ammazza il processo."""
    codice = _codice(_RENDER)
    assert "QGraphicsScene" in codice and "build_scene" in codice
    assert "MatrixView" not in codice


def test_the_preview_goes_through_the_s3dgraphy_pipeline():
    codice = _codice(_RENDER)
    assert "export_site" in codice and "read_em_json" in codice
    assert "graphviz" not in codice.lower()


def test_the_button_draws_the_filtered_matrix_and_no_longer_graphviz():
    """Il bottone «visualizza matrix» della scheda US: s3dgraphy al posto
    di «tred» + «dot», il filtro di DATA_LIST, il PNG nella cartella
    della matrice invece della finestra di matplotlib."""
    src = _sorgente(_SCHEDA)
    inizio = src.index("def on_pushButton_viewmatrix_pressed")
    fine = src.index("def on_pushButton_export_extended_matrix_integrated")
    corpo = src[inizio:fine]
    assert "build_preview" in corpo
    assert "self.DATA_LIST" in corpo
    assert "self.MATRIX_PATH" in corpo
    assert "pyarchinit_view_Matrix" not in corpo
    assert "Harris_matrix_viewtred.dot.jpg" not in corpo
    assert "plt.show" not in corpo


# ------------------------------------------------- l'etichetta della pianta

def test_etichetta_solo_la_riga_con_indice_due():
    """Una etichetta per unità: US 5 ha 101 righe ma una sola con indice 2."""
    from modules.utility.matrix_preview import label_expression
    espr = label_expression()
    assert espr == ("CASE WHEN \"stratigraph_index_us\" = 2 "
                    "THEN 'US' || ' ' || \"us_s\" END")


def test_etichetta_con_poligoni_di_ripiego():
    from modules.utility.matrix_preview import label_expression
    espr = label_expression([7, 3])
    assert '"stratigraph_index_us" = 2 OR "gid" IN (7, 3)' in espr


def test_ripiego_solo_per_unita_senza_indice_due():
    from modules.utility.matrix_preview import fallback_label_ids
    righe = [
        (1, "S", "1", "5", 1), (2, "S", "1", "5", 2),     # ha l'indice 2
        (9, "S", "1", "0", 1), (8, "S", "1", "0", 1),     # non ce l'ha
        (4, "S", "2", "5", 1),                            # altra area
    ]
    assert fallback_label_ids(righe) == [4, 8]


def test_ripiego_vuoto_se_tutte_hanno_l_indice_due():
    from modules.utility.matrix_preview import fallback_label_ids
    assert fallback_label_ids([(1, "S", "1", "1", 2)]) == []
    assert fallback_label_ids([]) == []
