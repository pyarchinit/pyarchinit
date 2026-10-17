"""I toponimi della scheda sito passano dal thesaurus (Enzo, 17 ottobre 2026:
«nazione, regione, provincia, comune … andrebbero aggiornati anche nella
scheda thesaurus perché li dovrebbe leggere da lì»). Codici 1.2–1.5 di
site_table; regioni e province italiane come voci; un database senza voci
mostra gli elenchi di prima."""
from __future__ import annotations

import sqlite3
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"


def test_i_codici_dei_toponimi():
    from modules.utility.site_toponyms import SITE_DEFINITION_CODE, TOPONYM_CODES
    assert SITE_DEFINITION_CODE == "1.1"
    assert TOPONYM_CODES == (("nazione", "1.2"), ("regione", "1.3"),
                             ("provincia", "1.4"), ("comune", "1.5"))


def test_regioni_e_province_hanno_sigle_uniche():
    from modules.utility.site_toponyms import NAZIONI_IT, PROVINCE_IT, REGIONI_IT
    assert len(REGIONI_IT) == 20 and ("TOS", "Toscana") in REGIONI_IT
    assert ("PI", "Pisa") in PROVINCE_IT and ("BT", "Barletta-Andria-Trani") in PROVINCE_IT
    assert ("SU", "Sud Sardegna") in PROVINCE_IT
    for elenco in (NAZIONI_IT, REGIONI_IT, PROVINCE_IT):
        sigle = [s for s, _ in elenco]
        assert len(sigle) == len(set(sigle)) and all(len(s) <= 3 for s in sigle)


def test_il_thesaurus_vince_e_senza_voci_restano_gli_elenchi_di_prima():
    from modules.utility.site_toponyms import PROVINCE_IT, REGIONI_IT, toponym_choices
    dal_thesaurus = {"regione": ["Transilvania"], "comune": ["Sarmizegetusa"]}
    scelte = toponym_choices(dal_thesaurus, "it")
    assert scelte["regione"] == ["Transilvania"] and scelte["comune"] == ["Sarmizegetusa"]
    assert scelte["provincia"] == [p for _s, p in PROVINCE_IT]        # ripiego italiano
    assert scelte["nazione"] == []
    assert toponym_choices({}, "en") == {"nazione": [], "regione": [], "provincia": [], "comune": []}
    assert toponym_choices({}, "it")["regione"] == [r for _s, r in REGIONI_IT]


def test_la_scheda_sito_legge_i_toponimi_dal_thesaurus():
    src = (PLUGIN_ROOT / "tabs" / "Site.py").read_text(encoding="utf-8")
    assert "toponym_choices(" in src and "TOPONYM_CODES" in src
    assert "'Carbonia-Iglesias'" not in src          # gli elenchi stanno nel modulo condiviso


def test_il_database_di_esempio_ha_regioni_e_province():
    con = sqlite3.connect("file:%s?mode=ro" % SAMPLE_DB, uri=True)
    try:
        conta = dict(con.execute(
            "SELECT tipologia_sigla, count(*) FROM pyarchinit_thesaurus_sigle "
            "WHERE nome_tabella = 'site_table' AND lingua = 'IT' GROUP BY tipologia_sigla"))
    finally:
        con.close()
    assert conta.get("1.2", 0) >= 1 and conta.get("1.3") == 20 and conta.get("1.4", 0) >= 107


def test_la_finestra_del_thesaurus_conosce_i_codici_nuovi():
    src = (PLUGIN_ROOT / "tabs" / "Thesaurus.py").read_text(encoding="utf-8")
    for codice, nome in (("1.2", "Nazione"), ("1.3", "Regione"), ("1.4", "Provincia"), ("1.5", "Comune")):
        assert "'%s': {'it': '%s'" % (codice, nome) in src, codice
