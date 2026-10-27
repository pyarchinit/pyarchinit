"""Piante e prospetti dai proxy 3D all'import dell'em.json (spec 2026-10-18,
D8–D13): un progetto EM finto con tre unità, i GLB scritti dai test, un DB
copiato dal template con l'SRID dei layer scelto dal test."""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

pytest.importorskip("s3dgraphy")

from tests.sync.glb_fixtures import box_glb, quad_glb  # noqa: E402
from modules.utility.spatialite_loader import load_spatialite  # noqa: E402

TEMPLATE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite"
SITO = "Tempio 3D"


def _nodo(nid, tipo, nome, **data):
    return {"id": nid, "node_type": tipo, "name": nome, "data": dict(data)}


def _arco(src, tipo, dst):
    return {"id": "%s_%s_%s" % (src, tipo, dst), "edge_type": tipo, "source": src, "target": dst}


def _unita(nid, nome, tipo="US"):
    # Come negli em.json di EMStudio: la proprietà è di tipo «geometry» e la
    # risorsa è un «proxy_model» (la regola dei proxy di s3dgraphy li vuole).
    return [_nodo(nid, tipo, nome),
            _nodo("p" + nid, "property", "geometry", property_type="geometry"),
            _nodo("sh" + nid, "semantic_shape", "Shape for " + nome),
            _nodo("r" + nid, "resource", nome + ".glb", url="proxies/%s.glb" % nome,
                  url_type="proxy_model")]


def _archi(nid):
    return [_arco(nid, "has_property", "p" + nid), _arco("p" + nid, "has_semantic_shape", "sh" + nid),
            _arco("sh" + nid, "has_linked_resource", "r" + nid)]


def _spatialite_engine(path):
    from sqlalchemy import create_engine, event
    eng = create_engine("sqlite:///%s" % path)

    @event.listens_for(eng, "connect")
    def _carica(dbapi_conn, _record):
        load_spatialite(dbapi_conn)
    return eng


def make_project(tmp_path, *, srid=31700, georef=True, muro_sottile=False, muro_ns=False):
    """Tre unità: SU001 una scatola 4×1×3 a nord, SU002 una scatola 2×2×1 a
    sud, USV103 senza file. Coordinate glTF (Y in alto)."""
    radice = tmp_path / "Tempio"
    (radice / "EM" / "proxies").mkdir(parents=True)
    if muro_ns:      # un muro N–S senza spessore, proprio a nord del centro del sito
        su001 = quad_glb([(1, 0, -12), (1, 0, -8), (1, 3, -8), (1, 3, -12)])
    elif muro_sottile:
        su001 = quad_glb([(0, 0, -10), (4, 0, -10), (4, 3, -10), (0, 3, -10)])
    else:
        su001 = box_glb(4.0, 3.0, 1.0, center=(2.0, 1.5, -10.0))
    (radice / "EM" / "proxies" / "SU001.glb").write_bytes(su001)
    (radice / "EM" / "proxies" / "SU002.glb").write_bytes(box_glb(2.0, 1.0, 2.0, center=(1.0, 0.5, 5.0)))
    nodi = _unita("u1", "SU001") + _unita("u2", "SU002") + _unita("u3", "USV103", "USVs")
    if georef:
        nodi.append(_nodo("geo_g", "geo_position", "geo_position", epsg=31700,
                          shift_x=327300.0, shift_y=448370.0, shift_z=0.0))
    archi = _archi("u1") + _archi("u2") + _archi("u3")
    em = radice / "EM" / "tempio.em.json"
    em.write_text(json.dumps({"version": "1.0", "active_graph_id": "g",
                              "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
                              "graphs": {"g": {"graph_id": "g", "name": "Tempio",
                                               "nodes": nodi, "edges": archi}}}), encoding="utf-8")
    db = tmp_path / "db.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    con = sqlite3.connect(db)
    con.execute("UPDATE geometry_columns SET srid = ? WHERE f_table_name IN "
                "('pyunitastratigrafiche', 'pyunitastratigrafiche_usm')", (srid,))
    con.commit()
    con.close()
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    grafo, _ = read_graph_for_import(str(em))
    eng = _spatialite_engine(db)
    GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    return {"db": db, "eng": eng, "em": em, "grafo": grafo, "radice": radice}


@pytest.fixture
def progetto(tmp_path):
    return make_project(tmp_path)


def _per_nome(unita):
    return {u.name: u for u in unita}


def test_le_unita_con_il_loro_proxy(progetto):
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = _per_nome(edi.plan_units(progetto["grafo"], str(progetto["em"]),
                                     db=progetto["eng"], sito=SITO))
    assert unita["SU001"].usable and unita["SU001"].triangles == 12
    assert unita["SU001"].paths[0].endswith("SU001.glb")
    assert unita["USV103"].status == "missing" and not unita["USV103"].usable
    assert edi.status_text(unita["USV103"]) == "file non trovato"


def test_la_scelta_predefinita(progetto):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    geo = drw.georef_of(progetto["grafo"])
    scelta = edi.default_choice(unita, geo)
    nomi = {u.key: u.name for u in unita}
    assert {nomi[k] for k in scelta.plan} == {"SU001", "SU002"}
    assert {nomi[k] for k in scelta.prospect} == {"SU001", "SU002"}
    assert scelta.sides == ("N", "E", "S", "W") and scelta.shift_z is None
    assert edi.preview_line(unita, scelta, geo) == (
        "Dal 3D: 2 piante, 4 prospetti del sito, 2 prospetti di unità "
        "(si calcolano all'Applica); 1 unità senza modello utilizzabile.")


def test_le_schede_si_trovano_per_node_uuid(progetto):
    from modules.s3dgraphy.sync import em_drawings_import as edi
    schede = edi.schede_of(progetto["eng"], SITO, ["u1", "u2", "nessuno"])
    assert set(schede) == {"u1", "u2"}
    assert schede["u1"].us == "001" and schede["u1"].area == "1" and schede["u1"].unita_tipo == "US"


@pytest.mark.parametrize("srid, tipo", [(31700, "ok"), (3004, "convert"), (4326, "refuse"), (-1, "refuse")])
def test_la_regola_dell_srid(tmp_path, srid, tipo):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path, srid=srid)
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    geo = drw.georef_of(p["grafo"])
    decisione = edi.crs_decision(p["eng"], geo, edi.default_choice(unita, geo))
    assert decisione.kind == tipo
    if tipo == "convert":
        assert decisione.message == "Converto le piante in EPSG:3004 del database?"
    if tipo == "refuse":
        assert "ricrea il database in epsg:31700" in decisione.message.lower()


def test_senza_geometrie_nessun_controllo(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path, srid=4326)
    geo = drw.georef_of(p["grafo"])
    vuota = edi.Choice(plan=set(), prospect=set(), sides=(), shift_z=None)
    assert edi.crs_decision(p["eng"], geo, vuota).kind == "none"


def test_senza_layer_usm_le_sole_piante_passano(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path)
    con = sqlite3.connect(p["db"])
    con.execute("DELETE FROM geometry_columns WHERE f_table_name = 'pyunitastratigrafiche_usm'")
    con.commit()
    con.close()
    geo = drw.georef_of(p["grafo"])
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    piante = edi.Choice(plan={u.key for u in unita if u.usable}, prospect=set(), sides=(), shift_z=None)
    assert edi.crs_decision(p["eng"], geo, piante).kind == "ok"
    tutto = edi.default_choice(unita, geo)
    assert edi.crs_decision(p["eng"], geo, tutto).kind == "refuse"


def test_senza_posizione_niente_piante(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path, georef=False)
    geo = drw.georef_of(p["grafo"])
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    scelta = edi.default_choice(unita, geo)
    assert scelta.plan == set() and len(scelta.prospect) == 2
    assert edi.crs_decision(p["eng"], geo, scelta).kind == "ok"


def _calcola(p, scelta=None):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    geo = drw.georef_of(p["grafo"])
    scelta = scelta or edi.default_choice(unita, geo)
    schede = edi.schede_of(p["eng"], SITO, [u.key for u in unita])
    return edi.compute_drawings(p["grafo"], unita, scelta, geo, schede, source_name="tempio.em.json")


def test_i_disegni_di_due_unita(progetto):
    disegni, saltate = _calcola(progetto)
    nomi = [d.nome for d in disegni]
    assert nomi == ["3D-PLA", "3D-PRO-N", "3D-PRO-E", "3D-PRO-S", "3D-PRO-W",
                    "3D-PRO-US001", "3D-PRO-US002"]
    assert saltate == {}
    pianta = disegni[0]
    assert pianta.layer == "pyunitastratigrafiche" and pianta.tipo == "Planimetria"
    aree = sorted(round(g.area(), 6) for _k, g in pianta.features)
    assert aree == [4.0, 4.0]                     # SU001: 4 × 1; SU002: 2 × 2
    x0 = min(g.boundingBox().xMinimum() for _k, g in pianta.features)
    assert x0 == pytest.approx(327300.0)          # spostamento X dell'em.json


def test_le_viste_verticali_non_si_sovrappongono(progetto):
    from modules.s3dgraphy import em_drawings as drw
    disegni, _ = _calcola(progetto)
    verticali = [d for d in disegni if d.layer == "pyunitastratigrafiche_usm"]
    assert all(d.tipo == "Prospetto" for d in verticali)
    campate = []
    for d in verticali:
        lo = min(drw.span_u(g)[0] for _k, g in d.features)
        hi = max(drw.span_u(g)[1] for _k, g in d.features)
        campate.append((lo, hi))
    for (a0, a1), (b0, b1) in zip(campate, campate[1:]):
        assert b0 == pytest.approx(a1 + 10.0)
    assert campate[0][0] == pytest.approx(0.0)


def test_nel_prospetto_nord_il_piu_vicino_e_scritto_per_ultimo(progetto):
    disegni, _ = _calcola(progetto)
    nord = next(d for d in disegni if d.nome == "3D-PRO-N")
    # SU001 sta a nord (z glTF −10 → Y +10): è il più vicino a chi guarda da nord
    assert [k for k, _g in nord.features] == ["u2", "u1"]


def test_un_muro_senza_spessore_ha_il_prospetto_ma_non_la_pianta(tmp_path):
    p = make_project(tmp_path, muro_sottile=True)
    disegni, saltate = _calcola(p)
    pianta = next(d for d in disegni if d.nome == "3D-PLA")
    assert [k for k, _g in pianta.features] == ["u2"]
    assert saltate == {"u1": "vuoto in pianta"}
    assert "3D-PRO-US001" in [d.nome for d in disegni]


def test_lo_spostamento_z_scelto_vale_per_le_quote(progetto):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    geo = drw.georef_of(progetto["grafo"])
    scelta = edi.default_choice(unita, geo)
    scelta.shift_z = 495.0
    disegni, _ = _calcola(progetto, scelta)
    nord = next(d for d in disegni if d.nome == "3D-PRO-N")
    assert min(g.boundingBox().yMinimum() for _k, g in nord.features) == pytest.approx(495.0)


def _scrivi(p, decisione_attesa="ok", scelta=None):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    geo = drw.georef_of(p["grafo"])
    scelta = scelta or edi.default_choice(unita, geo)
    decisione = edi.crs_decision(p["eng"], geo, scelta)
    assert decisione.kind == decisione_attesa
    return edi.run_drawings(p["eng"], p["grafo"], SITO, str(p["em"]), units=unita,
                            choice=scelta, georef=geo, decision=decisione, lang="it")


def _righe(p, sql, *args):
    con = sqlite3.connect(p["db"])
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def test_poligoni_documenti_e_schede_si_richiamano_insieme(progetto):
    esito = _scrivi(progetto)
    assert (esito.plans, esito.side_views, esito.unit_views) == (2, 4, 2)
    piante = _righe(progetto, "SELECT scavo_s, area_s, us_s, unita_tipo_s, tipo_doc, nome_doc, "
                              "disegnatore, coord FROM pyunitastratigrafiche ORDER BY us_s")
    assert [r[:6] for r in piante] == [(SITO, "1", "001", "US", "Planimetria", "3D-PLA"),
                                       (SITO, "1", "002", "US", "Planimetria", "3D-PLA")]
    assert all(r[6] == "pyArchInit 3D" and r[7].startswith("POINT(") for r in piante)
    documenti = _righe(progetto, "SELECT tipo_documentazione, nome_doc, disegnatore FROM "
                                 "documentazione_table WHERE sito = ? ORDER BY nome_doc", SITO)
    assert [(t, n) for t, n, _d in documenti] == [
        ("Planimetria", "3D-PLA"), ("Prospetto", "3D-PRO-E"), ("Prospetto", "3D-PRO-N"),
        ("Prospetto", "3D-PRO-S"), ("Prospetto", "3D-PRO-US001"), ("Prospetto", "3D-PRO-US002"),
        ("Prospetto", "3D-PRO-W")]
    # il filtro della scheda Documentazione trova le «US verticali» del documento
    verticali = _righe(progetto, "SELECT us FROM pyarchinit_usm_view WHERE sito = ? AND "
                                 "nome_doc = ? AND tipo_doc = ?", SITO, "3D-PRO-N", "Prospetto")
    assert sorted(r[0] for r in verticali) == ["001", "002"]
    orizzontali = _righe(progetto, "SELECT us FROM pyarchinit_us_view WHERE sito = ? AND "
                                   "nome_doc = ? AND tipo_doc = ?", SITO, "3D-PLA", "Planimetria")
    assert sorted(r[0] for r in orizzontali) == ["001", "002"]
    import ast
    doc = ast.literal_eval(_righe(progetto, "SELECT documentazione FROM us_table WHERE sito = ? "
                                            "AND us = '001'", SITO)[0][0])
    assert doc == [["Planimetria", "3D-PLA"], ["Prospetto", "3D-PRO-N"], ["Prospetto", "3D-PRO-E"],
                   ["Prospetto", "3D-PRO-S"], ["Prospetto", "3D-PRO-W"], ["Prospetto", "3D-PRO-US001"]]


def test_reimportare_sostituisce_solo_il_ricavato(progetto):
    _scrivi(progetto)
    con = sqlite3.connect(progetto["db"])
    load_spatialite(con)
    con.execute("INSERT INTO pyunitastratigrafiche (gid, scavo_s, area_s, us_s, disegnatore, tipo_doc, "
                "nome_doc, the_geom) VALUES (9999, ?, '1', '001', 'Enzo', 'Planimetria', 'P1', "
                "CastToMultiPolygon(GeomFromText('POLYGON((0 0,1 0,1 1,0 0))', 31700)))", (SITO,))
    con.commit()
    con.close()
    esito = _scrivi(progetto)
    assert esito.removed == 2 + 4 * 2 + 2              # le piante, i lati, i prospetti di prima
    totale = _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche WHERE scavo_s = ?", SITO)[0][0]
    # SU001 ha ora una pianta a mano: la scelta predefinita non le rifà la sua
    assert totale == 2                                 # SU002 ricavata + quella a mano di SU001
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE sito = ?", SITO)[0][0] == 7


def test_il_poligono_corretto_a_mano_resta_col_suo_documento(progetto):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    _scrivi(progetto)
    con = sqlite3.connect(progetto["db"])
    con.execute("UPDATE pyunitastratigrafiche_usm SET disegnatore = 'Enzo' WHERE nome_doc = '3D-PRO-US001'")
    con.commit()
    con.close()
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    geo = drw.georef_of(progetto["grafo"])
    scelta = edi.default_choice(unita, geo)
    su001 = next(u for u in unita if u.name == "SU001")
    assert su001.hand_vertical and su001.key not in scelta.prospect
    _scrivi(progetto, scelta=scelta)
    assert _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche_usm WHERE nome_doc = '3D-PRO-US001'")[0][0] == 1
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE nome_doc = '3D-PRO-US001'")[0][0] == 1
    # e la scheda US lo richiama ancora
    doc = _righe(progetto, "SELECT documentazione FROM us_table WHERE sito = ? AND us = '001'", SITO)[0][0]
    assert "['Prospetto', '3D-PRO-US001']" in doc


def test_convertire_le_piante_in_un_altro_sistema(tmp_path):
    p = make_project(tmp_path, srid=3004)
    esito = _scrivi(p, decisione_attesa="convert")
    assert esito.converted == (31700, 3004)
    x = _righe(p, "SELECT coord FROM pyunitastratigrafiche LIMIT 1")[0][0]
    assert not x.startswith("POINT(3273")                # le coordinate non sono più quelle di Stereo 70
    assert "convertite da EPSG:31700 a EPSG:3004" in esito.summary()


def test_il_riepilogo(progetto):
    esito = _scrivi(progetto)
    assert esito.summary().startswith("Dal 3D: 2 piante, 4 prospetti del sito, 2 prospetti di unità")


def test_la_vista_usm_filtrata_del_template_torna_canonica(progetto):
    """Il template SQLite (resources/dbfiles/pyarchinit.sqlite, da cui nasce
    ogni DB nuovo) ha una pyarchinit_usm_view che mostra solo le unità di
    tipo USM; la definizione canonica (spatial_view_definitions, e la vista
    di PostgreSQL) mostra i disegni verticali di tutte le unità."""
    prima = _righe(progetto, "SELECT sql FROM sqlite_master WHERE name = 'pyarchinit_usm_view'")[0][0]
    assert "unita_tipo = 'USM'" in prima
    esito = _scrivi(progetto)
    assert esito.view_fixed
    dopo = _righe(progetto, "SELECT sql FROM sqlite_master WHERE name = 'pyarchinit_usm_view'")[0][0]
    assert "unita_tipo = 'USM'" not in dopo
    assert "la vista USM del database mostrava solo le USM" in esito.summary()
    assert not _scrivi(progetto).view_fixed          # la seconda volta non c'è più niente da fare


def test_senza_nessun_proxy_trovato_i_disegni_di_prima_restano(progetto):
    """L'SSD staccato: nessun proxy si trova, e il passo dei disegni non deve
    cancellare quelli ricavati la volta prima."""
    _scrivi(progetto)
    (progetto["radice"] / "EM" / "proxies").rename(progetto["radice"] / "EM" / "proxies_via")
    esito = _scrivi(progetto, decisione_attesa="none")
    assert esito.removed == 0 and esito.features == 0
    assert "i disegni ricavati di prima restano" in esito.summary()
    assert _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche WHERE scavo_s = ?", SITO)[0][0] == 2
    assert _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche_usm WHERE scavo_s = ?", SITO)[0][0] == 10


def test_la_barra_avanza_anche_durante_il_calcolo(progetto):
    """Su TempluMare il calcolo dura quasi un minuto dopo la lettura dei
    modelli: la barra deve contare anche piante e prospetti, o la finestra
    sembra ferma."""
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    geo = drw.georef_of(progetto["grafo"])
    schede = edi.schede_of(progetto["eng"], SITO, [u.key for u in unita])
    chiamate = []
    edi.compute_drawings(progetto["grafo"], unita, edi.default_choice(unita, geo), geo, schede,
                         progress=lambda fatti, totale, nome: chiamate.append((fatti, totale)))
    # 2 modelli letti, 2 piante, 4 lati × 2 unità, 2 prospetti di unità
    assert chiamate[-1] == (14, 14)
    fatti = [f for f, _t in chiamate]
    assert fatti == sorted(fatti) and max(f for f, _t in chiamate[:-1]) > 2



def test_un_muro_senza_spessore_visto_di_taglio_ha_il_prospetto_di_fronte(tmp_path):
    """Senza pianta la direzione dal centro dello scavo può essere parallela al
    muro: il lato lungo si prende dai vertici."""
    p = make_project(tmp_path, muro_ns=True)
    disegni, saltate = _calcola(p)
    prospetto = next((d for d in disegni if d.nome == "3D-PRO-US001"), None)
    assert prospetto is not None
    assert prospetto.features[0][1].area() == pytest.approx(12.0, abs=1e-6)     # 4 m × 3 m, di fronte
    assert saltate == {"u1": "vuoto in pianta"}


def test_la_vista_canonica_che_non_si_legge_lascia_quella_di_prima(progetto, monkeypatch):
    """Un DB vecchio a cui manca una colonna che la vista canonica legge: SQLite
    crea la vista lo stesso, ma poi non si legge. Deve restare quella di prima."""
    from modules.db import spatial_view_definitions as svd
    rotta = svd.CANONICAL_VIEWS["pyarchinit_usm_view"].replace(
        '"b"."d_stratigrafica" AS', '"b"."colonna_che_non_c_e" AS', 1)
    assert rotta != svd.CANONICAL_VIEWS["pyarchinit_usm_view"]
    monkeypatch.setitem(svd.CANONICAL_VIEWS, "pyarchinit_usm_view", rotta)
    esito = _scrivi(progetto)
    assert not esito.view_fixed
    sql = _righe(progetto, "SELECT sql FROM sqlite_master WHERE name = 'pyarchinit_usm_view'")[0][0]
    assert "unita_tipo = 'USM'" in sql
    _righe(progetto, "SELECT * FROM pyarchinit_usm_view LIMIT 1")       # si legge ancora


def test_importare_in_un_secondo_sito_ha_i_suoi_disegni(progetto):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    GraphIngestor().populate_list(progetto["grafo"], progetto["db"], sito="Copia", create_missing_epochs=True)
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito="Copia")
    geo = drw.georef_of(progetto["grafo"])
    scelta = edi.default_choice(unita, geo)
    esito = edi.run_drawings(progetto["eng"], progetto["grafo"], "Copia", str(progetto["em"]), units=unita,
                             choice=scelta, georef=geo, decision=edi.crs_decision(progetto["eng"], geo, scelta))
    assert esito.plans == 2 and esito.skipped == {"u3": "file non trovato"}     # solo l'unità senza file


def test_il_reimport_non_tocca_le_sezioni(progetto):
    _scrivi(progetto)
    con = sqlite3.connect(progetto["db"])
    load_spatialite(con)
    con.execute("INSERT INTO pyunitastratigrafiche_usm (gid, scavo_s, area_s, us_s, unita_tipo_s, disegnatore, "
                "tipo_doc, nome_doc, the_geom) VALUES (900, ?, '1', '001', 'US', 'pyArchInit 3D', 'Sezione', "
                "'3D-SEZ-1', CastToMultiPolygon(GeomFromText('POLYGON((-20 0,-18 0,-18 2,-20 0))', 31700)))", (SITO,))
    con.execute("INSERT INTO documentazione_table (id_documentazione, sito, nome_doc, tipo_documentazione, "
                "disegnatore) VALUES (900, ?, '3D-SEZ-1', 'Sezione', 'pyArchInit 3D')", (SITO,))
    con.commit()
    con.close()
    _scrivi(progetto)
    assert _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche_usm WHERE nome_doc = '3D-SEZ-1'")[0][0] == 1
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE nome_doc = '3D-SEZ-1'")[0][0] == 1
    doc = _righe(progetto, "SELECT documentazione FROM us_table WHERE sito = ? AND us = '001'", SITO)[0][0]
    assert "['Sezione', '3D-SEZ-1']" in doc


# ------------------------------------------- minori della revisione (19 ottobre 2026)

def test_un_file_che_non_si_legge_salta_solo_la_sua_unita(progetto, monkeypatch):
    from modules.s3dgraphy import glb_mesh as gm
    vero = gm.read_triangles

    def finto(p, **kw):
        if "SU001" in str(p):
            raise OSError("file sparito")
        return vero(p, **kw)
    monkeypatch.setattr(gm, "read_triangles", finto)
    disegni, saltate = _calcola(progetto)
    assert any(d.features for d in disegni)
    assert any("file sparito" in m for m in saltate.values())


def test_nessun_documento_se_nessun_poligono_si_scrive(progetto):
    con = sqlite3.connect(progetto["db"])
    con.execute("CREATE TRIGGER no_nord BEFORE INSERT ON pyunitastratigrafiche_usm "
                "WHEN NEW.nome_doc = '3D-PRO-N' BEGIN SELECT RAISE(ABORT, 'rifiutato'); END")
    con.commit()
    con.close()
    esito = _scrivi(progetto)
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE nome_doc = '3D-PRO-N'")[0][0] == 0
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE nome_doc = '3D-PRO-E'")[0][0] == 1
    assert esito.side_views == 3 and any("rifiutato" in w for w in esito.warnings)


def test_il_rilievo_originale_sta_in_250_caratteri():
    from modules.s3dgraphy.sync import em_drawings_import as edi
    lunghi = ["webdav://server.example/progetto/EM/proxies/%03d_%s.glb" % (i, "x" * 40) for i in range(8)]
    testo = edi.rilievo_text(lunghi)
    assert len(testo) <= 250 and testo.startswith(lunghi[0]) and testo.endswith("(+%d)" % (8 - testo.count(";") - 1))
    assert edi.rilievo_text(["a.glb", "b.glb"]) == "a.glb; b.glb"
    assert len(edi.rilievo_text(["y" * 400])) <= 250


def test_il_fermo_dice_quale_layer_non_va(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path)
    con = sqlite3.connect(p["db"])
    con.execute("UPDATE geometry_columns SET srid = 4326 WHERE f_table_name = 'pyunitastratigrafiche_usm'")
    con.commit()
    con.close()
    geo = drw.georef_of(p["grafo"])
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    decisione = edi.crs_decision(p["eng"], geo, edi.default_choice(unita, geo))
    assert decisione.kind == "refuse"
    assert "i prospetti non ci possono stare" in decisione.message
    assert "piante e prospetti non ci possono stare" not in decisione.message
    assert "solo le piante" in decisione.message


def test_il_riepilogo_dice_le_unita_senza_modello(progetto):
    from modules.s3dgraphy.sync import em_drawings_import as edi
    unita = edi.plan_units(progetto["grafo"], str(progetto["em"]), db=progetto["eng"], sito=SITO)
    esito = _scrivi(progetto)
    assert "USV103: file non trovato" in esito.summary(unita)


# ------------------------------------------- seconda revisione (19 ottobre 2026)

def test_il_fermo_non_propone_quello_che_non_si_puo(tmp_path):
    """Senza posizione nell'em.json le piante non si possono fare: il fermo
    per il layer USM non deve consigliare «importa solo le piante»."""
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    p = make_project(tmp_path, georef=False)
    con = sqlite3.connect(p["db"])
    con.execute("UPDATE geometry_columns SET srid = 4326 WHERE f_table_name = 'pyunitastratigrafiche_usm'")
    con.commit()
    con.close()
    geo = drw.georef_of(p["grafo"])
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    decisione = edi.crs_decision(p["eng"], geo, edi.default_choice(unita, geo))
    assert decisione.kind == "refuse"
    assert "solo le piante" not in decisione.message and "solo le schede" in decisione.message
