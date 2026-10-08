"""Quello che un'unità della matrice tocca fuori dalla matrice (2026-10-08).

Richiesta di Enzo: cliccando una US nel pannello si vedono i suoi media e,
se la geometria è disegnata, ci si può zoomare sopra. Qui si prova la parte
pura — la riga del database, i media, l'espressione che ritrova la
geometria — su un database di prova, senza Qt e senza QGIS.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _unit(**dati):
    from modules.utility.em_matrix_model import Unit
    return Unit(node_id=dati.pop("node_id", "n1"),
                label=dati.pop("label", "1.US1"),
                node_type=dati.pop("node_type", "US"),
                epoch_id=None, data=dati)


def _db(tmp_path, *, node_uuid_column=True, media=True):
    """Un database con le tre tabelle che servono, e due siti dentro."""
    percorso = tmp_path / "prova.sqlite"
    con = sqlite3.connect(percorso)
    uuid_col = ", node_uuid TEXT" if node_uuid_column else ""
    con.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, "
                "sito TEXT, area TEXT, us TEXT, unita_tipo TEXT%s)" % uuid_col)
    righe = [(1, "Scavo", "1", "1", "US", "uuid-uno"),
             (2, "Scavo", "1", "2", "US", "uuid-due"),
             (3, "Scavo", "2", "1", "USM", "uuid-tre"),
             (4, "L'Aquila", "1", "1", "US", "uuid-quattro")]
    if node_uuid_column:
        con.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?)", righe)
    else:
        con.executemany("INSERT INTO us_table VALUES (?,?,?,?,?)",
                        [r[:5] for r in righe])
    if media:
        con.execute("CREATE TABLE media_to_entity_table ("
                    "id_mediaToEntity INTEGER PRIMARY KEY, id_entity INTEGER, "
                    "entity_type TEXT, table_name TEXT, id_media INTEGER, "
                    "filepath TEXT, media_name TEXT)")
        con.execute("CREATE TABLE media_thumb_table ("
                    "id_media_thumb INTEGER PRIMARY KEY, id_media INTEGER, "
                    "mediatype TEXT, media_filename TEXT, "
                    "media_thumb_filename TEXT, filetype TEXT, filepath TEXT, "
                    "path_resize TEXT)")
        con.executemany(
            "INSERT INTO media_to_entity_table VALUES (?,?,?,?,?,?,?)",
            [(1, 1, "US", "us_table", 10, "foto/uno.jpg", "uno.jpg"),
             (2, 1, "US", "us_table", 11, "foto/due.jpg", "due.jpg"),
             (3, 2, "US", "us_table", 12, "foto/tre.jpg", "tre.jpg"),
             (4, 1, "REPERTO", "inventario_materiali_table", 13,
              "foto/non_mia.jpg", "non_mia.jpg")])
        con.executemany(
            "INSERT INTO media_thumb_table VALUES (?,?,?,?,?,?,?,?)",
            [(1, 10, "image", "uno.jpg", "uno_thumb.jpg", "jpg",
              "thumb/uno_thumb.jpg", "resize/uno.jpg"),
             (2, 11, "image", "due.jpg", "due_thumb.jpg", "jpg",
              "thumb/due_thumb.jpg", "resize/due.jpg"),
             (3, 12, "image", "tre.jpg", "tre_thumb.jpg", "jpg",
              "thumb/tre_thumb.jpg", "resize/tre.jpg")])
    con.commit()
    con.close()
    return "sqlite:///%s" % percorso


# ----------------------------------------------------------------- identità

def test_the_identity_of_a_unit_is_what_the_record_is_keyed_by():
    """us_table ha un vincolo unico su (sito, area, us, unita_tipo): quelli
    sono i campi che ritrovano la riga, più node_uuid se c'è."""
    from modules.utility.em_matrix_links import unit_identity

    ident = unit_identity(_unit(sito="Scavo", area="1", us="1",
                                unita_tipo="US", node_uuid="uuid-uno"))
    assert ident["sito"] == "Scavo"
    assert ident["area"] == "1"
    assert ident["us"] == "1"
    assert ident["unita_tipo"] == "US"
    assert ident["node_uuid"] == "uuid-uno"


def test_a_node_that_is_not_a_record_has_no_identity():
    """Un nodo di continuità o un documento non è una riga di us_table:
    non deve far cercare nel database una US che non esiste."""
    from modules.utility.em_matrix_links import unit_identity

    assert unit_identity(_unit(label="CON 1")) == {}


# ------------------------------------------------------------------ id_us

def test_the_record_is_found_by_node_uuid(tmp_path):
    from modules.utility.em_matrix_links import resolve_id_us

    conn = _db(tmp_path)
    assert resolve_id_us(conn, _unit(sito="Scavo", us="1", area="1",
                                     unita_tipo="US",
                                     node_uuid="uuid-tre")) == 3


def test_without_a_uuid_the_record_is_found_by_site_area_us_and_type(tmp_path):
    from modules.utility.em_matrix_links import resolve_id_us

    conn = _db(tmp_path)
    assert resolve_id_us(conn, _unit(sito="Scavo", area="2", us="1",
                                     unita_tipo="USM")) == 3
    # stesso us, altro sito: non si confondono
    assert resolve_id_us(conn, _unit(sito="L'Aquila", area="1", us="1",
                                     unita_tipo="US")) == 4


def test_a_database_without_the_uuid_column_still_finds_the_record(tmp_path):
    """La colonna node_uuid la aggiunge una migrazione: su un database che
    non l'ha ancora il pannello non deve rompersi."""
    from modules.utility.em_matrix_links import resolve_id_us

    conn = _db(tmp_path, node_uuid_column=False)
    assert resolve_id_us(conn, _unit(sito="Scavo", area="1", us="2",
                                     unita_tipo="US",
                                     node_uuid="uuid-due")) == 2


def test_a_unit_that_is_not_in_the_database_resolves_to_nothing(tmp_path):
    from modules.utility.em_matrix_links import resolve_id_us

    conn = _db(tmp_path)
    assert resolve_id_us(conn, _unit(sito="Scavo", area="9", us="99",
                                     unita_tipo="US")) is None
    assert resolve_id_us(conn, _unit()) is None


def test_an_unreachable_database_does_not_raise(tmp_path):
    from modules.utility.em_matrix_links import resolve_id_us

    conn = "sqlite:///%s" % (tmp_path / "non_esiste.sqlite")
    assert resolve_id_us(conn, _unit(sito="Scavo", area="1", us="1",
                                     unita_tipo="US")) is None


# ------------------------------------------------------------------- media

def test_the_media_of_a_unit_come_with_their_thumbnail(tmp_path):
    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path)
    media = media_for_unit(conn, _unit(sito="Scavo", area="1", us="1",
                                       unita_tipo="US",
                                       node_uuid="uuid-uno"))
    assert [m.name for m in media] == ["due.jpg", "uno.jpg"]
    assert [m.thumb_file for m in media] == ["thumb/due_thumb.jpg",
                                            "thumb/uno_thumb.jpg"]
    assert media[0].id_media == 11


def test_the_media_of_another_entity_with_the_same_id_are_not_mine(tmp_path):
    """id_entity 1 è anche un reperto: il suo media non è di questa US."""
    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path)
    nomi = [m.name for m in media_for_unit(
        conn, _unit(sito="Scavo", area="1", us="1", unita_tipo="US"))]
    assert "non_mia.jpg" not in nomi


def test_a_unit_with_no_media_gets_an_empty_list(tmp_path):
    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path)
    assert media_for_unit(conn, _unit(sito="Scavo", area="2", us="1",
                                      unita_tipo="USM")) == []


def test_a_database_without_the_media_tables_gets_an_empty_list(tmp_path):
    """Un database appena creato può non avere ancora le tabelle media."""
    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path, media=False)
    assert media_for_unit(conn, _unit(sito="Scavo", area="1", us="1",
                                      unita_tipo="US")) == []


def test_a_media_without_a_thumbnail_is_still_listed(tmp_path):
    """Senza anteprima si mostra almeno il nome: un media che c'è e non si
    vede è peggio di un media senza miniatura."""
    import sqlite3 as s3

    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path)
    c = s3.connect(tmp_path / "prova.sqlite")
    c.execute("DELETE FROM media_thumb_table WHERE id_media = 10")
    c.commit()
    c.close()
    media = media_for_unit(conn, _unit(sito="Scavo", area="1", us="1",
                                       unita_tipo="US"))
    senza = [m for m in media if m.name == "uno.jpg"]
    assert senza and senza[0].thumb_file == ""


def test_the_number_of_thumbnails_is_capped(tmp_path):
    """Una US con duecento foto non deve bloccare il pannello."""
    import sqlite3 as s3

    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path)
    c = s3.connect(tmp_path / "prova.sqlite")
    c.executemany("INSERT INTO media_to_entity_table VALUES (?,?,?,?,?,?,?)",
                  [(100 + i, 1, "US", "us_table", 200 + i,
                    "foto/m%d.jpg" % i, "m%d.jpg" % i) for i in range(60)])
    c.commit()
    c.close()
    media = media_for_unit(conn, _unit(sito="Scavo", area="1", us="1",
                                       unita_tipo="US"), limit=24)
    assert len(media) == 24


# --------------------------------------------------------- geometria sulla mappa

def test_the_feature_is_found_by_id_us_when_the_layer_has_it(tmp_path):
    """pyarchinit_us_view porta id_us: una sola chiave, nessun dubbio."""
    from modules.utility.em_matrix_links import pick_feature_expression

    espressione = pick_feature_expression(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="US"),
        {"id_us", "sito", "area", "us", "the_geom"}, id_us=7)
    assert espressione == '"id_us" = 7'


def test_without_id_us_the_feature_is_found_by_site_area_and_us():
    from modules.utility.em_matrix_links import pick_feature_expression

    espressione = pick_feature_expression(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="US"),
        {"sito", "area", "us"})
    assert espressione == (
        '"sito" = \'Scavo\' AND "area" = \'1\' AND "us" = \'1\'')


def test_the_drawing_table_has_its_own_field_names():
    """pyunitastratigrafiche chiama gli stessi campi scavo_s/area_s/us_s:
    è il layer che l'archeologo ha caricato più spesso."""
    from modules.utility.em_matrix_links import pick_feature_expression

    espressione = pick_feature_expression(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="US"),
        {"scavo_s", "area_s", "us_s", "the_geom"})
    assert espressione == (
        '"scavo_s" = \'Scavo\' AND "area_s" = \'1\' AND "us_s" = \'1\'')


def test_a_site_name_with_an_apostrophe_is_quoted():
    """«L'Aquila» dentro un'espressione QGIS la spezzerebbe in due."""
    from modules.utility.em_matrix_links import pick_feature_expression

    espressione = pick_feature_expression(
        _unit(sito="L'Aquila", area="1", us="1", unita_tipo="US"),
        {"sito", "area", "us"})
    assert "'L''Aquila'" in espressione


def test_a_layer_that_cannot_identify_the_unit_gets_no_expression():
    from modules.utility.em_matrix_links import pick_feature_expression

    assert pick_feature_expression(
        _unit(sito="Scavo", area="1", us="1"),
        {"fid", "nome", "the_geom"}) is None


def test_a_node_that_is_not_a_record_is_never_looked_for_on_the_map():
    from modules.utility.em_matrix_links import pick_feature_expression

    assert pick_feature_expression(
        _unit(label="CON 1"), {"sito", "area", "us"}) is None


def test_the_type_of_unit_refines_the_search_when_the_layer_knows_it():
    """Una US 1 e una USM 1 nella stessa area sono due righe diverse: se il
    layer porta unita_tipo si usa, altrimenti si zoomerebbe sulla prima
    delle due che capita."""
    from modules.utility.em_matrix_links import pick_feature_expression

    espressione = pick_feature_expression(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="USM"),
        {"sito", "area", "us", "unita_tipo"})
    assert espressione == ('"sito" = \'Scavo\' AND "area" = \'1\' AND '
                           '"us" = \'1\' AND "unita_tipo" = \'USM\'')


def test_a_media_linked_twice_is_shown_once(tmp_path):
    """media_thumb_table non ha un vincolo unico su id_media: due anteprime
    dello stesso media non devono diventare due voci."""
    import sqlite3 as s3

    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path)
    c = s3.connect(tmp_path / "prova.sqlite")
    c.execute("INSERT INTO media_thumb_table VALUES "
              "(9, 10, 'image', 'uno.jpg', 'altro.jpg', 'jpg', "
              "'thumb/altro.jpg', 'resize/uno.jpg')")
    c.commit()
    c.close()
    media = media_for_unit(conn, _unit(sito="Scavo", area="1", us="1",
                                       unita_tipo="US"))
    assert len([m for m in media if m.id_media == 10]) == 1


# ------------------------------------------------- quale layer si prova prima

def test_the_most_precise_layer_is_tried_first():
    """Fra i layer caricati si parte da quello che identifica l'unità senza
    ambiguità: id_us prima dei nomi della scheda, i nomi della scheda prima
    di quelli della tabella dei disegni."""
    from modules.utility.em_matrix_links import candidate_layers

    unit = _unit(sito="Scavo", area="1", us="1", unita_tipo="US")
    ordine = candidate_layers(unit, [
        ("disegni", {"scavo_s", "area_s", "us_s"}),
        ("schede", {"sito", "area", "us"}),
        ("vista", {"id_us", "sito", "area", "us"}),
    ], id_us=7)
    assert [chiave for chiave, _ in ordine] == ["vista", "schede", "disegni"]
    assert ordine[0][1] == '"id_us" = 7'


def test_layers_that_cannot_identify_the_unit_are_left_out():
    from modules.utility.em_matrix_links import candidate_layers

    unit = _unit(sito="Scavo", area="1", us="1", unita_tipo="US")
    ordine = candidate_layers(unit, [
        ("catasto", {"fid", "foglio"}),
        ("schede", {"sito", "area", "us"}),
    ])
    assert [chiave for chiave, _ in ordine] == ["schede"]


def test_without_an_id_us_the_view_is_still_a_candidate():
    """Se la riga non si risolve si usa comunque la vista, con i nomi della
    scheda: meglio cercare per sito/area/us che non cercare."""
    from modules.utility.em_matrix_links import candidate_layers

    ordine = candidate_layers(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="US"),
        [("vista", {"id_us", "sito", "area", "us"})], id_us=None)
    assert len(ordine) == 1
    assert "id_us" not in ordine[0][1]


def test_two_equally_precise_layers_keep_the_order_of_the_project():
    from modules.utility.em_matrix_links import candidate_layers

    unit = _unit(sito="Scavo", area="1", us="1", unita_tipo="US")
    ordine = candidate_layers(unit, [("primo", {"sito", "area", "us"}),
                                     ("secondo", {"sito", "area", "us"})])
    assert [chiave for chiave, _ in ordine] == ["primo", "secondo"]


def test_a_node_that_is_not_a_record_has_no_candidate_layer():
    from modules.utility.em_matrix_links import candidate_layers

    assert candidate_layers(_unit(label="CON 1"),
                            [("schede", {"sito", "area", "us"})]) == []


# ------------------------------------------------- dove inquadrare la mappa

def test_two_boxes_become_the_box_that_holds_both():
    from modules.utility.em_matrix_links import merge_boxes

    assert merge_boxes([(0, 0, 10, 10), (5, -5, 20, 2)]) == (0, -5, 20, 10)


def test_no_box_is_no_box():
    from modules.utility.em_matrix_links import merge_boxes

    assert merge_boxes([]) is None
    assert merge_boxes([None, None]) is None


def test_a_point_gets_a_window_around_it():
    """Una quota è un punto: inquadrarlo esattamente darebbe una finestra
    di larghezza zero, cioè uno zoom infinito."""
    from modules.utility.em_matrix_links import padded_box

    assert padded_box((100, 200, 100, 200), minimum=5.0) == (95, 195, 105, 205)


def test_a_polygon_gets_some_air_around_it():
    from modules.utility.em_matrix_links import padded_box

    x1, y1, x2, y2 = padded_box((0, 0, 10, 10), margin=0.2)
    assert (x1, y1, x2, y2) == (-2, -2, 12, 12)


def test_a_sliver_is_widened_only_where_it_is_flat():
    """Un muro disegnato come linea è alto zero: va allargato di là, non
    in tutte e due le direzioni."""
    from modules.utility.em_matrix_links import padded_box

    x1, y1, x2, y2 = padded_box((0, 50, 100, 50), margin=0.1, minimum=5.0)
    assert (x1, x2) == (-10, 110)
    assert (y1, y2) == (45, 55)


def test_the_first_layer_with_a_geometry_wins():
    from modules.utility.em_matrix_links import find_unit_extent

    unit = _unit(sito="Scavo", area="1", us="1", unita_tipo="US")
    trovate = {"schede": [], "disegni": [(3, (0, 0, 4, 4))]}

    def fetch(chiave, espressione):
        assert "Scavo" in espressione
        return trovate[chiave]

    esito = find_unit_extent(unit, [("schede", {"sito", "area", "us"}),
                                    ("disegni", {"scavo_s", "area_s", "us_s"})],
                             fetch=fetch)
    assert esito == ("disegni", [3], (0, 0, 4, 4))


def test_a_unit_that_is_drawn_nowhere_has_no_extent():
    from modules.utility.em_matrix_links import find_unit_extent

    esito = find_unit_extent(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="US"),
        [("schede", {"sito", "area", "us"})], fetch=lambda k, e: [])
    assert esito is None


def test_a_feature_without_a_geometry_does_not_count_as_drawn():
    """La riga c'è nel layer ma la pianta non è stata disegnata: non è una
    geometria su cui zoomare."""
    from modules.utility.em_matrix_links import find_unit_extent

    esito = find_unit_extent(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="US"),
        [("schede", {"sito", "area", "us"}),
         ("disegni", {"scavo_s", "area_s", "us_s"})],
        fetch=lambda k, e: ([(1, None)] if k == "schede"
                            else [(9, (1, 1, 2, 2))]))
    assert esito == ("disegni", [9], (1, 1, 2, 2))


def test_a_layer_that_raises_is_skipped_not_fatal():
    """Un layer rotto o una fonte non raggiungibile non deve impedire di
    provare il prossimo."""
    from modules.utility.em_matrix_links import find_unit_extent

    def fetch(chiave, espressione):
        if chiave == "rotto":
            raise RuntimeError("fonte non raggiungibile")
        return [(2, (0, 0, 1, 1))]

    esito = find_unit_extent(
        _unit(sito="Scavo", area="1", us="1", unita_tipo="US"),
        [("rotto", {"sito", "area", "us"}),
         ("buono", {"scavo_s", "area_s", "us_s"})], fetch=fetch)
    assert esito == ("buono", [2], (0, 0, 1, 1))


# --------------------------------------- come si apre il database del plugin

def test_reading_our_own_database_does_not_go_through_the_library():
    """Scoperto provando con QGIS vero (2026-10-08): appoggiandosi a
    ``s3dgraphy.sync._db_handle._resolve_db_handle`` — un nome privato
    della libreria — dove la libreria non è importabile i media e lo zoom
    tacevano senza dire perché. Il database del progetto è roba nostra:
    si apre con SQLAlchemy, come fa il resto del plugin."""
    import ast
    from pathlib import Path as _P

    sorgente = (_P(__file__).resolve().parents[2] / "modules" / "utility"
                / "em_matrix_links.py").read_text(encoding="utf-8")
    moduli = set()
    for nodo in ast.walk(ast.parse(sorgente)):
        if isinstance(nodo, ast.Import):
            moduli |= {a.name for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            moduli.add(nodo.module)
    assert not [m for m in moduli if "s3dgraphy" in m], moduli
    assert "_resolve_db_handle" not in sorgente


def test_the_database_manager_of_the_plugin_is_accepted_as_it_is(tmp_path):
    """Chi chiama può avere in mano il gestore del database invece della
    stringa: porta già l'engine aperto."""
    from sqlalchemy import create_engine

    from modules.utility.em_matrix_links import resolve_id_us

    url = _db(tmp_path)

    class Gestore:
        def __init__(self):
            self.engine = create_engine(url)

    gestore = Gestore()
    assert resolve_id_us(gestore, _unit(sito="Scavo", area="1", us="1",
                                        unita_tipo="US")) == 1
    gestore.engine.dispose()


def test_a_path_to_the_sqlite_file_is_accepted_too(tmp_path):
    from modules.utility.em_matrix_links import resolve_id_us

    _db(tmp_path)
    assert resolve_id_us(tmp_path / "prova.sqlite",
                         _unit(sito="Scavo", area="1", us="2",
                               unita_tipo="US")) == 2


def test_nothing_at_all_is_not_a_database(tmp_path):
    from modules.utility.em_matrix_links import media_for_unit, resolve_id_us

    unit = _unit(sito="Scavo", area="1", us="1", unita_tipo="US")
    assert resolve_id_us(None, unit) is None
    assert media_for_unit(None, unit) == []
    assert resolve_id_us(object(), unit) is None


def test_the_connection_is_not_left_open_behind_us(tmp_path):
    """Il database di Enzo lo tiene aperto il suo QGIS in WAL: una lettura
    del pannello non deve lasciare dietro di sé un engine con il file
    agganciato (lezione del «disk I/O error» del 2026-10-08)."""
    import gc

    from sqlalchemy.engine import Engine

    from modules.utility.em_matrix_links import media_for_unit

    conn = _db(tmp_path)
    prima = len([o for o in gc.get_objects() if isinstance(o, Engine)])
    for _ in range(5):
        media_for_unit(conn, _unit(sito="Scavo", area="1", us="1",
                                   unita_tipo="US"))
    gc.collect()
    dopo = len([o for o in gc.get_objects() if isinstance(o, Engine)])
    assert dopo <= prima + 1, (prima, dopo)
