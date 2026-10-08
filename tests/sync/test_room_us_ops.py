"""L'adapter della stanza: righe di us_table → operazioni (C, piano 2026-10-07).

Puro: niente Qt, niente rete, niente DB. Il payload va DENTRO ``node`` (il
CRDT perde in silenzio un node_type al top level); gli id sono derivati con
stable_id, mai uuid4; i paradata non diventano unità della stanza.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest  # noqa: F401

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


def test_unit_ids_are_stable_and_origin_bound():
    from modules.s3dgraphy.room.us_ops import unit_id
    a = unit_id("Scavo", "1", "12a")
    assert a == unit_id("Scavo", "1", "12a")          # deterministico
    assert a != unit_id("Scavo", "2", "12a")          # l'area identifica
    assert a != unit_id("Scavo", "1", "12")           # il testo conta ("12a" ≠ "12")


def test_a_plain_us_becomes_an_add_node_with_payload_inside_node():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([{"sito": "S", "area": "1", "us": "3",
                           "unita_tipo": "US",
                           "d_stratigrafica": "strato", "scavato": "Si"}])
    assert len(made.ops) == 1
    op = made.ops[0]
    assert op["op"] == "add_node" and "node" in op
    assert op["node"]["node_type"] == "US"
    assert op["node"]["name"] == "3"
    assert op["node"]["data"]["site"] == "S"
    assert op["node"]["data"]["origin"] == "pyarchinit"
    assert "node_type" not in op, "il tipo al top level viene PERSO dal CRDT"


def test_masonry_and_coating_travel_as_us_with_a_kind():
    # dev40: USM è una US con stratigraphic_kind='masonry'; i codici
    # localizzati (WSU...) idem. Il codice d'origine resta in source_code.
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "S", "area": "1", "us": "4", "unita_tipo": "USM"},
        {"sito": "S", "area": "1", "us": "5", "unita_tipo": "WSU"},
        {"sito": "S", "area": "1", "us": "6", "unita_tipo": "USR"},
    ])
    kinds = {o["node"]["name"]: (o["node"]["node_type"],
                                 o["node"]["data"].get("stratigraphic_kind"),
                                 o["node"]["data"].get("source_code"))
             for o in made.ops}
    assert kinds["4"] == ("US", "masonry", "USM")
    assert kinds["5"] == ("US", "masonry", "WSU")
    assert kinds["6"] == ("US", "coating", "USR")


def test_virtual_units_keep_their_class_and_legacy_codes_remap():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "S", "area": "1", "us": "7", "unita_tipo": "USVs"},
        {"sito": "S", "area": "1", "us": "8", "unita_tipo": "USVA"},
    ])
    types = {o["node"]["name"]: o["node"]["node_type"] for o in made.ops}
    assert types == {"7": "USVs", "8": "USVs"}
    assert made.counts.get("units_remapped_USVA_to_USVs") == 1


def test_rows_that_cannot_be_nodes_are_reported_not_invented():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "", "area": "1", "us": "1"},              # senza sito
        {"sito": "S", "area": "1", "us": "9",
         "unita_tipo": "DOC"},                              # paradata: non US
    ])
    assert made.ops == []
    assert len(made.skipped) == 2


def _known(*triples):
    from modules.s3dgraphy.room.us_ops import unit_id, normalize_area
    return {(s, normalize_area(a), u): unit_id(s, a, u) for s, a, u in triples}


def test_a_directional_rapporto_becomes_one_oriented_edge():
    from modules.s3dgraphy.room.us_ops import ops_for_relationships, unit_id
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "1", "edge_type": "overlies",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Copre"}], known)
    assert len(made.ops) == 1
    op = made.ops[0]
    assert op["op"] == "add_edge" and op["edge_type"] == "overlies"
    assert op["source"] == unit_id("S", "1", "1")
    assert op["target"] == unit_id("S", "1", "2")
    assert op["attributes"]["pyarchinit_relationship"] == "Copre"
    assert op["id"] == "%s__overlies__%s" % (op["source"], op["target"])


def test_swap_means_the_target_is_the_source():
    # «Coperto da 2» sulla riga 1 = 2 overlies 1 (parse_rapporti: swap=True)
    from modules.s3dgraphy.room.us_ops import ops_for_relationships, unit_id
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "1", "edge_type": "overlies",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": True, "verb": "Coperto da"}], known)
    assert made.ops[0]["source"] == unit_id("S", "1", "2")
    assert made.ops[0]["target"] == unit_id("S", "1", "1")


def test_an_inverse_type_folds_into_its_forward_type():
    # parse_rapporti dà 'Coperto da' come is_overlain_by (swap=False, misurato):
    # l'adapter DEVE piegarlo in overlies con gli estremi scambiati, o la
    # coppia inversa diventa due archi nella stanza condivisa (C1 review).
    from modules.s3dgraphy.room.us_ops import ops_for_relationships, unit_id
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "2", "edge_type": "is_overlain_by",
          "target_us": "1", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Coperto da"}], known)
    op = made.ops[0]
    assert op["edge_type"] == "overlies"
    assert op["source"] == unit_id("S", "1", "1")
    assert op["target"] == unit_id("S", "1", "2")


def test_the_inverse_pair_collapses_to_one_edge():
    # 1 Copre 2 + 2 Coperto da 1 → UN arco, con i tipi VERI del parse
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    made = ops_for_relationships([
        {"sito": "S", "area": "1", "us": "1", "edge_type": "overlies",
         "target_us": "2", "target_area": "1", "target_sito": "S",
         "swap": False, "verb": "Copre"},
        {"sito": "S", "area": "1", "us": "2", "edge_type": "is_overlain_by",
         "target_us": "1", "target_area": "1", "target_sito": "S",
         "swap": False, "verb": "Coperto da"},
    ], known)
    assert len(made.ops) == 1
    assert made.counts.get("edges_deduplicated") == 1


def test_a_real_reciprocal_pair_through_site_rows_is_one_edge(tmp_path):
    """La prova che mancava: Copre/Coperto da dalla COLONNA, col parse vero.
    Sul sito campione la mancanza di questa piega metteva 81 archi doppi
    nella stanza (misurato dal revisore)."""
    import sqlite3
    db = tmp_path / "pair.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, node_uuid TEXT,
        rapporti TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        descrizione TEXT, interpretazione TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        anno_scavo TEXT, scavato TEXT)""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        sito TEXT, periodo TEXT, fase TEXT, cron_iniziale INTEGER,
        cron_finale INTEGER, descrizione TEXT, datazione_estesa TEXT)""")
    conn.executemany(
        "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
        "VALUES (?, ?, ?, ?, ?)",
        [("S", "1", "1", "US", '[["Copre", "2", "1", "S"]]'),
         ("S", "1", "2", "US", '[["Coperto da", "1", "1", "S"]]')])
    conn.commit(); conn.close()
    from modules.s3dgraphy.room import site_rows, us_ops
    units, rels, _periods, _problems = site_rows.load("sqlite:///%s" % db, "S")
    made = us_ops.deliver(units, rels)
    edges = [o for o in made.ops if o["op"] == "add_edge"]
    assert len(edges) == 1, [(e["edge_type"], e["id"]) for e in edges]
    assert edges[0]["edge_type"] == "overlies"


def test_symmetric_edges_have_one_canonical_orientation():
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    a = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "1", "edge_type": "equals",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Uguale a"}], known).ops[0]
    b = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "2", "edge_type": "equals",
          "target_us": "1", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Uguale a"}], known).ops[0]
    assert a["id"] == b["id"], "stessa relazione = stesso arco, da qualsiasi lato"


def test_alphanumeric_units_can_be_cited():
    # Review Focus 1: '12a' è TEXT da noi e deve viaggiare (mini non poteva)
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "1", "12a"), ("S", "1", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "12a", "edge_type": "cuts",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Taglia"}], known)
    assert len(made.ops) == 1 and not made.skipped


def test_an_ambiguous_bare_number_is_reported_not_guessed():
    # Review Focus 2: il target '1' esiste in due aree, il rapporto non dice quale
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "A", "1"), ("S", "B", "1"), ("S", "A", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "A", "us": "2", "edge_type": "overlies",
          "target_us": "1", "target_area": "", "target_sito": "S",
          "swap": False, "verb": "Copre"}], known)
    assert made.ops == []
    assert any("ambigu" in s for s in made.skipped)


def test_site_rows_reads_units_and_parses_rapporti(tmp_path):
    import sqlite3
    db = tmp_path / "s.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, node_uuid TEXT,
        rapporti TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        descrizione TEXT, interpretazione TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        anno_scavo TEXT, scavato TEXT)""")
    rows = [("S", "1", "1", "US", '[["Copre", "2", "1", "S"]]'),
            ("S", "1", "2", "USM", "[]"),
            ("ALTRO", "1", "9", "US", "[]")]
    conn.execute("""CREATE TABLE periodizzazione_table (
        sito TEXT, periodo TEXT, fase TEXT, cron_iniziale INTEGER,
        cron_finale INTEGER, descrizione TEXT, datazione_estesa TEXT)""")
    conn.executemany(
        "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
        "VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit(); conn.close()
    from modules.s3dgraphy.room.site_rows import load
    units, rels, _periodi, problems = load("sqlite:///%s" % db, "S")
    assert {u["us"] for u in units} == {"1", "2"}      # un sito per consegna
    assert problems == []
    assert len(rels) == 1 and rels[0]["edge_type"] == "overlies"
    assert rels[0]["target_us"] == "2" and rels[0]["verb"] == "Copre"


def test_an_unknown_verb_in_the_middle_does_not_shift_the_words(tmp_path):
    """Rischio dichiarato nel piano: se parse_rapporti scarta una voce,
    lo zip coi verbi non deve disallineare la «parola dell'archeologo»."""
    import sqlite3
    db = tmp_path / "v.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, node_uuid TEXT,
        rapporti TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        descrizione TEXT, interpretazione TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        anno_scavo TEXT, scavato TEXT)""")
    raw = ('[["Copre", "2", "1", "S"], ["VerboInventato", "3", "1", "S"], '
           '["Taglia", "4", "1", "S"]]')
    conn.executemany(
        "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
        "VALUES (?, ?, ?, ?, ?)",
        [("S", "1", "1", "US", raw), ("S", "1", "2", "US", "[]"),
         ("S", "1", "3", "US", "[]"), ("S", "1", "4", "US", "[]")])
    conn.commit(); conn.close()
    from modules.s3dgraphy.room.site_rows import load
    _units, rels, _periodi, problems = load("sqlite:///%s" % db, "S")
    assert any("VerboInventato" in p_ for p_ in problems)
    by_target = {r["target_us"]: r["verb"] for r in rels}
    assert by_target.get("2") == "Copre"
    assert by_target.get("4") == "Taglia", by_target
    assert "VerboInventato" not in set(by_target.values()) or \
        by_target.get("3") == "VerboInventato"


def test_localized_unit_codes_become_us_not_dropped():
    """C2 review: SU (en/ar), SE (de), UE (es/ca/pt), ΣΜ (el) sono il modo
    in cui pyArchInit scrive 'US' nelle altre lingue — sul DB campione se ne
    perdevano 36 per sito. canonical_unita_tipo li conosce già."""
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "S", "area": "1", "us": str(i + 1), "unita_tipo": code}
        for i, code in enumerate(("SU", "SE", "UE", "ΣΜ"))])
    assert len(made.ops) == 4, made.skipped
    assert {o["node"]["node_type"] for o in made.ops} == {"US"}
    assert made.counts.get("units_canonicalized_SU") == 1


def test_every_unit_op_carries_its_language():
    """I4 review: il contratto dev40 (crdt.make_op, decisione 12) rifiuta un
    add_node testuale senza data.lang — lo mette il produttore, una volta."""
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units(
        [{"sito": "S", "area": "1", "us": "1", "unita_tipo": "US"}],
        lang="it")
    assert made.ops[0]["node"]["data"]["lang"] == "it"
    default = ops_for_units(
        [{"sito": "S", "area": "1", "us": "1", "unita_tipo": "US"}])
    assert default.ops[0]["node"]["data"]["lang"] == "und"


def test_unreadable_rapporti_are_reported_not_swallowed(tmp_path):
    """I6 review: una colonna rapporti illeggibile o un verbo sconosciuto
    devono finire nel rapporto, mai sparire in silenzio."""
    import sqlite3
    db = tmp_path / "bad.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, node_uuid TEXT,
        rapporti TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        descrizione TEXT, interpretazione TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        anno_scavo TEXT, scavato TEXT)""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        sito TEXT, periodo TEXT, fase TEXT, cron_iniziale INTEGER,
        cron_finale INTEGER, descrizione TEXT, datazione_estesa TEXT)""")
    conn.executemany(
        "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
        "VALUES (?, ?, ?, ?, ?)",
        [("S", "1", "1", "US", "{non è json né literal"),
         ("S", "1", "2", "US", '[["VerboInventato", "1", "1", "S"]]')])
    conn.commit(); conn.close()
    from modules.s3dgraphy.room.site_rows import load
    _units, rels, _periodi, problems = load("sqlite:///%s" % db, "S")
    assert rels == []
    assert len(problems) == 2
    assert any("illeggibil" in p for p in problems)
    assert any("VerboInventato" in p for p in problems)


def test_unit_ids_do_not_collide_on_pipes():
    """Minor 14 review: stable_id unisce le parti con '|' — un sito o
    un'area che lo contengono non devono poter collidere."""
    from modules.s3dgraphy.room.us_ops import unit_id
    assert unit_id("S|1", "2", "3") != unit_id("S", "1|2", "3")
    assert unit_id("S|", "", "3") != unit_id("S", "|", "3")


def test_usvb_is_a_non_structural_virtual_unit():
    """USVA parallelogramma (strutturale), USVB esagono (NON strutturale),
    USVC ellisse (serie → non strutturale): le forme che l'esportatore
    storico di pyArchInit assegnava (resources/dbfiles/dot.py:855-865), e
    la stessa mappa della migrazione del vocabolario. La tabella della
    stanza diceva USVB → USVs e battezzava strutturali unità che non lo
    sono."""
    from modules.s3dgraphy.room.us_ops import UNIT_TYPES

    assert UNIT_TYPES["USVA"] == "USVs"
    assert UNIT_TYPES["USVB"] == "USVn"
    assert UNIT_TYPES["USVC"] == "USVn"


def test_the_room_the_projector_and_the_migration_agree():
    """Tre tabelle, un significato solo: la stanza, il proiettore e la
    migrazione. Se una cambia, questo test cade (la review del
    2026-10-08 ha trovato che il proiettore non era controllato da
    nessuno, ed è l'unico che porta anche «USVc»)."""
    from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
        REPLACEMENTS)

    from modules.s3dgraphy.room.us_ops import UNIT_TYPES
    from modules.s3dgraphy.sync.graph_projector import LEGACY_UNITA_TIPO

    for legacy, canonical in REPLACEMENTS.items():
        assert UNIT_TYPES[legacy] == canonical, legacy
        assert LEGACY_UNITA_TIPO[legacy] == canonical, legacy
    extra = set(LEGACY_UNITA_TIPO) - set(REPLACEMENTS)
    assert extra == {"USVc"}, extra


def _periodo(periodo="2", fase="1", nome="XV secolo", da=1451, a=1499):
    return {"sito": "Scavo", "periodo": periodo, "fase": fase,
            "datazione_estesa": nome, "cron_iniziale": da, "cron_finale": a,
            "descrizione": "descrizione di %s" % nome}


def test_the_room_gets_the_periods_as_epochs():
    """Misurato il 2026-10-08 sulla stanza vera: «by_epoch: []». La
    consegna mandava unità e rapporti ma non la periodizzazione, così
    nella stanza la cronologia non esisteva."""
    from modules.s3dgraphy.room.us_ops import epoch_id, ops_for_epochs

    fatto = ops_for_epochs([_periodo()])
    nodi = [o for o in fatto.ops if o["op"] == "add_node"]
    assert len(nodi) == 1
    nodo = nodi[0]
    assert nodo["id"] == epoch_id("Scavo", "2", "1")
    assert nodo["node"]["node_type"] == "EpochNode"
    assert nodo["node"]["name"] == "XV secolo"
    assert nodo["node"]["data"]["start_time"] == 1451
    assert nodo["node"]["data"]["end_time"] == 1499


def test_an_epoch_id_is_stable_and_never_a_fresh_uuid():
    from modules.s3dgraphy.room.us_ops import epoch_id

    a = epoch_id("Scavo", "2", "1")
    assert a == epoch_id("Scavo", "2", "1")
    assert a != epoch_id("Scavo", "2", "2")
    assert a != epoch_id("Altro", "2", "1")


def test_a_period_without_dates_is_left_out_and_said():
    """Senza anni un'epoca non sa dove stare: meglio non mandarla che
    mandarla a zero."""
    from modules.s3dgraphy.room.us_ops import ops_for_epochs

    fatto = ops_for_epochs([_periodo(da=None, a=None)])
    assert fatto.ops == []
    assert fatto.skipped and "ann" in fatto.skipped[0].lower()


def test_every_unit_is_tied_to_the_epoch_it_was_born_in():
    from modules.s3dgraphy.room.us_ops import deliver, epoch_id, unit_id

    unita = [{"sito": "Scavo", "area": "1", "us": "1", "unita_tipo": "US",
              "periodo_iniziale": "2", "fase_iniziale": "1"}]
    fatto = deliver(unita, (), periods=[_periodo()])
    archi = [o for o in fatto.ops if o["op"] == "add_edge"]
    tipi = {o["edge_type"] for o in archi}
    assert "has_first_epoch" in tipi
    nascita = next(o for o in archi if o["edge_type"] == "has_first_epoch")
    assert nascita["source"] == unit_id("Scavo", "1", "1")
    assert nascita["target"] == epoch_id("Scavo", "2", "1")


def test_a_unit_without_a_declared_end_survives_in_its_own_epoch():
    """La stessa regola dell'export em.json (5.13.40): quello che la
    scheda dice e niente di più."""
    from modules.s3dgraphy.room.us_ops import deliver, epoch_id

    unita = [{"sito": "Scavo", "area": "1", "us": "1", "unita_tipo": "US",
              "periodo_iniziale": "2", "fase_iniziale": "1"}]
    fatto = deliver(unita, (), periods=[_periodo()])
    sopravvive = [o for o in fatto.ops
                  if o.get("edge_type") == "survive_in_epoch"]
    assert len(sopravvive) == 1
    assert sopravvive[0]["target"] == epoch_id("Scavo", "2", "1")


def test_a_declared_final_period_wins():
    from modules.s3dgraphy.room.us_ops import deliver, epoch_id

    unita = [{"sito": "Scavo", "area": "1", "us": "1", "unita_tipo": "US",
              "periodo_iniziale": "2", "fase_iniziale": "1",
              "periodo_finale": "1", "fase_finale": "1"}]
    fatto = deliver(unita, (), periods=[_periodo(),
                                        _periodo("1", "1", "Età moderna",
                                                 1600, 1799)])
    sopravvive = [o for o in fatto.ops
                  if o.get("edge_type") == "survive_in_epoch"]
    assert sopravvive[0]["target"] == epoch_id("Scavo", "1", "1")


def test_a_unit_pointing_at_a_period_that_is_not_there_is_said_not_invented():
    from modules.s3dgraphy.room.us_ops import deliver

    unita = [{"sito": "Scavo", "area": "1", "us": "1", "unita_tipo": "US",
              "periodo_iniziale": "9", "fase_iniziale": "9"}]
    fatto = deliver(unita, (), periods=[_periodo()])
    assert not [o for o in fatto.ops
                if o.get("edge_type") in ("has_first_epoch",
                                          "survive_in_epoch")]
    assert any("9" in s for s in fatto.skipped), fatto.skipped


def test_delivering_without_periods_still_works():
    """La consegna di prima non si rompe: senza periodizzazione si
    manda quello che c'è."""
    from modules.s3dgraphy.room.us_ops import deliver

    unita = [{"sito": "Scavo", "area": "1", "us": "1", "unita_tipo": "US"}]
    fatto = deliver(unita, ())
    assert [o for o in fatto.ops if o["op"] == "add_node"]
    assert not [o for o in fatto.ops if o.get("edge_type", "").endswith("epoch")]


def test_the_site_loader_also_brings_the_periodisation(tmp_path):
    """Senza questa lettura la consegna non avrebbe niente da cui fare le
    epoche: la stanza misurata il 2026-10-08 aveva «by_epoch: []»."""
    import sqlite3

    from modules.s3dgraphy.room import site_rows

    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, rapporti TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT, periodo_finale TEXT,
        fase_finale TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        descrizione TEXT, interpretazione TEXT, anno_scavo TEXT,
        scavato TEXT, quota_min_abs TEXT, quota_max_abs TEXT)""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        sito TEXT, periodo TEXT, fase TEXT, cron_iniziale INTEGER,
        cron_finale INTEGER, descrizione TEXT, datazione_estesa TEXT)""")
    conn.execute("INSERT INTO us_table (sito, area, us, unita_tipo,"
                 " periodo_iniziale, fase_iniziale)"
                 " VALUES ('S','1','1','US','2','1')")
    conn.execute("INSERT INTO periodizzazione_table VALUES"
                 " ('S','2','1',1451,1499,'descrizione','XV secolo')")
    conn.commit()
    conn.close()

    caricato = site_rows.load("sqlite:///%s" % db, "S")
    assert len(caricato) == 4, "load deve restituire anche i periodi"
    units, relationships, periods, problems = caricato
    assert len(units) == 1
    assert len(periods) == 1
    assert periods[0]["datazione_estesa"] == "XV secolo"
    assert periods[0]["cron_iniziale"] == 1451


def test_a_database_without_the_periodisation_table_does_not_fail(tmp_path):
    """Un DB vecchio o monco non deve impedire la consegna."""
    import sqlite3

    from modules.s3dgraphy.room import site_rows

    db = tmp_path / "y.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, rapporti TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT, periodo_finale TEXT,
        fase_finale TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        descrizione TEXT, interpretazione TEXT, anno_scavo TEXT,
        scavato TEXT, quota_min_abs TEXT, quota_max_abs TEXT)""")
    conn.execute("INSERT INTO us_table (sito, area, us, unita_tipo)"
                 " VALUES ('S','1','1','US')")
    conn.commit()
    conn.close()

    units, relationships, periods, problems = site_rows.load(
        "sqlite:///%s" % db, "S")
    assert len(units) == 1
    assert periods == []
    assert any("periodizzazione" in p.lower() for p in problems), problems
