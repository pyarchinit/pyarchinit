"""Il codice 7.2 della scheda Tomba è lo stato di conservazione (17 ottobre
2026). La scheda lo mette in `comboBox_conservazione_taf`, colonna
`stato_di_conservazione`, e i record di esempio ci scrivono «Buono», «Scarso».
`scripts/fill_thesaurus.py` lo chiamava invece «Tipo di copertura» e ci
aveva messo lastre litiche, coppi e terra di riempimento: nel menu della
conservazione comparivano tipi di copertura. Le coperture vanno al 7.3,
che è il campo `copertura_tipo`."""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
CONSERVAZIONE = {"Ottimo", "Buono", "Discreto", "Scarso", "Non determinabile"}
COPERTURE = {"Lastre litiche", "Coppi", "Terra di riempimento", "Assente"}


def _script():
    spec = importlib.util.spec_from_file_location(
        "fill_thesaurus", PLUGIN_ROOT / "scripts" / "fill_thesaurus.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _voci(con, codice):
    return {r[0] for r in con.execute(
        "SELECT sigla_estesa FROM pyarchinit_thesaurus_sigle WHERE nome_tabella = 'tomba_table'"
        " AND tipologia_sigla = ? AND lingua = 'IT'", (codice,))}


def test_lo_script_chiama_il_7_2_stato_di_conservazione():
    che_cosa, voci = _script().VOCABOLARI[("tomba_table", "7.2")]
    assert che_cosa == "Stato di conservazione"
    assert set(voci) == CONSERVAZIONE


def test_nel_database_di_esempio_il_7_2_e_la_conservazione_e_le_coperture_stanno_al_7_3():
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    try:
        assert _voci(con, "7.2") == CONSERVAZIONE
        assert COPERTURE <= _voci(con, "7.3")
        # i valori che i record di esempio usano ci sono nei menu
        record = con.execute("SELECT DISTINCT stato_di_conservazione, copertura_tipo, tipo_contenitore_resti"
                             " FROM tomba_table WHERE sito = 'Scavo archeologico'").fetchall()
        assert {r[0] for r in record} <= _voci(con, "7.2")
        assert {r[1] for r in record} <= _voci(con, "7.3")
        assert "Fossa terragna" in _voci(con, "7.4")
    finally:
        con.close()
