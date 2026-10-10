"""Il filtro per sito di «view all» deve stare in tutte le schede che possono usarlo.

Legge il sorgente delle schede (senza importare QGIS) e guarda dentro il
corpo del singolo handler, non nel file intero: una chiamata finita in un
metodo qualsiasi non conta. Prende sia una scheda dimenticata oggi sia un
handler rimesso com'era domani.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

_TABS = Path(__file__).resolve().parents[2] / "tabs"

# (file, handler) che devono passare da charge_records_for_site.
WIRED = [
    # Il bottone chiama self.view_all(), che passa dal metodo qui sotto.
    ("US_USM.py", "charge_records_filtered_by_site"),
    ("Archeozoology.py", "on_pushButton_view_all_pressed"),
    ("Attrezzature.py", "on_pushButton_view_all_pressed"),
    ("Budget.py", "on_pushButton_view_all_pressed"),
    ("Campioni.py", "on_pushButton_view_all_pressed"),
    ("Deteta.py", "on_pushButton_view_all_pressed"),
    ("Detsesso.py", "on_pushButton_view_all_pressed"),
    ("Documentazione.py", "on_pushButton_view_all_pressed"),
    ("Fauna.py", "on_pushButton_view_all_pressed"),
    ("Inv_Lapidei.py", "on_pushButton_view_all_2_pressed"),
    ("Inv_Materiali.py", "on_pushButton_view_all_2_pressed"),
    ("Periodizzazione.py", "on_pushButton_view_all_pressed"),
    ("Personale.py", "on_pushButton_view_all_pressed"),
    ("Presenze.py", "on_pushButton_view_all_pressed"),
    ("Schedaind.py", "on_pushButton_view_all_pressed"),
    ("Struttura.py", "on_pushButton_view_all_pressed"),
    ("Tma.py", "on_pushButton_view_all_pressed"),
    ("Tomba.py", "on_pushButton_view_all_pressed"),
    ("pyarchinit_Pottery_mainapp.py", "on_pushButton_view_all_pressed"),
]

# Schede in cui «view all» NON deve passare dal filtro, e perché.
NOT_WIRED = [
    # È l'anagrafica dei siti: filtrarla al sito corrente mostrerebbe una
    # riga sola e renderebbe impossibile passare a un altro sito.
    ("Site.py", "on_pushButton_view_all_pressed"),
    # Le loro tabelle (pdf_administrator_table, pyarchinit_thesaurus_sigle,
    # ut_table) non hanno la colonna `sito`: non c'è per cosa filtrare.
    ("Pdf_administrator.py", "on_pushButton_view_all_pressed"),
    ("Thesaurus.py", "on_pushButton_view_all_pressed"),
    ("UT.py", "on_pushButton_view_all_pressed"),
    # Copia vecchia della scheda Tomba (stessa classe, stesso .ui, tabella
    # TOMBA) che nessun modulo importa: da decidere a parte.
    ("Tafonomia.py", "on_pushButton_view_all_pressed"),
]

# «View all» delle strutture sul GIS: filtra già per sito per conto suo
# (sito_set + query_bool) e non carica la scheda con charge_records().
OWN_SITE_FILTER = [("Struttura.py", "on_pushButton_view_all_st_pressed")]


def _handler(filename, name):
    src = (_TABS / filename).read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _calls(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            out.add(f.id if isinstance(f, ast.Name)
                    else f.attr if isinstance(f, ast.Attribute) else None)
    return out


@pytest.mark.parametrize("filename,name", WIRED)
def test_handler_goes_through_the_site_filter(filename, name):
    node = _handler(filename, name)
    assert node is not None, f"{filename}: manca {name}"
    assert "charge_records_for_site" in _calls(node), (
        f"{filename}.{name} non passa da charge_records_for_site: "
        "«view all» mostrerebbe i record di tutti i siti")


def test_us_view_all_uses_the_filtered_loader():
    node = _handler("US_USM.py", "view_all")
    assert node is not None
    assert "charge_records_filtered_by_site" in _calls(node)
    assert "charge_records" not in _calls(node)


@pytest.mark.parametrize("filename,name", WIRED)
def test_wired_handler_does_not_reload_everything_afterwards(filename, name):
    node = _handler(filename, name)
    if filename == "US_USM.py":
        pytest.skip("per la scheda US vale test_us_view_all_uses_the_filtered_loader")
    assert "charge_records" not in _calls(node), (
        f"{filename}.{name} richiama ancora charge_records(): "
        "annullerebbe il filtro")


@pytest.mark.parametrize("filename,name", NOT_WIRED)
def test_handler_must_not_be_wired(filename, name):
    node = _handler(filename, name)
    if node is None:
        return  # nessun handler, nessun filtro: va bene
    assert "charge_records_for_site" not in _calls(node), (
        f"{filename}.{name} è filtrato per sito ma non deve esserlo "
        "(vedi il motivo in NOT_WIRED)")


@pytest.mark.parametrize("filename,name", OWN_SITE_FILTER)
def test_own_site_filter_handlers_keep_filtering(filename, name):
    node = _handler(filename, name)
    assert node is not None
    calls = _calls(node)
    assert "query_bool" in calls and "sito_set" in calls
    assert "charge_records" not in calls
