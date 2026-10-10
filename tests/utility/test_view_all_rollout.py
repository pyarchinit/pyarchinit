"""Il filtro per sito di «view all» deve stare in tutte le schede che possono usarlo.

Legge il sorgente delle schede (senza importare QGIS) e guarda dentro il
corpo del singolo handler, non nel file intero: una chiamata finita in un
metodo qualsiasi non conta. Prende sia una scheda dimenticata oggi sia un
handler rimesso com'era domani.
"""
from __future__ import annotations

import ast
from pathlib import Path

import re

import pytest

_HANDLER_RE = re.compile(r"on_pushButton_(view_all|show_all)\w*_pressed$")
_TABS = Path(__file__).resolve().parents[2] / "tabs"

# (file, handler) che devono passare da charge_records_for_site.
WIRED = [
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

# La scheda US ha una struttura sua: il bottone chiama `view_all()`, che
# carica con `charge_records_filtered_by_site()` e gestisce da sé il sito
# senza record (apre un record nuovo). Si fissa catena e guardia a parte.
US_BUTTON = ("US_USM.py", "on_pushButton_view_all_pressed")

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


def _mentions(node, text):
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id == text:
            return True
        if isinstance(n, ast.Attribute) and n.attr == text:
            return True
    return False


def _has_empty_guard(handler):
    """C'è un `if` che decide sul risultato del caricamento e, in un ramo,
    azzera la scheda con `clear_form_state`.

    Due forme valgono: il test contiene la chiamata a
    `charge_records_for_site` (`if not charge_records_for_site(self):`), oppure
    il test guarda `DATA_LIST` dopo la chiamata (Fauna, Pottery: la loro
    gestione del «nessun record» c'era già e guarda la lista).
    """
    for n in ast.walk(handler):
        if not isinstance(n, ast.If):
            continue
        decide = (_mentions(n.test, "charge_records_for_site")
                  or _mentions(n.test, "DATA_LIST"))
        if not decide:
            continue
        ramo = ast.Module(body=n.body + n.orelse, type_ignores=[])
        if "clear_form_state" in _calls(ramo):
            return True
    return False


def _all_handlers():
    found = set()
    for path in sorted(_TABS.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and _HANDLER_RE.match(node.name):
                found.add((path.name, node.name))
    return found


@pytest.mark.parametrize("filename,name", WIRED)
def test_handler_goes_through_the_site_filter(filename, name):
    node = _handler(filename, name)
    assert node is not None, f"{filename}: manca {name}"
    assert "charge_records_for_site" in _calls(node), (
        f"{filename}.{name} non passa da charge_records_for_site: "
        "«view all» mostrerebbe i record di tutti i siti")


@pytest.mark.parametrize("filename,name", WIRED)
def test_handler_guards_the_empty_case(filename, name):
    node = _handler(filename, name)
    assert _has_empty_guard(node), (
        f"{filename}.{name} non gestisce il sito senza record con "
        "clear_form_state: la scheda resterebbe con i contatori vecchi "
        "(IndexError al clic dopo) o con il record di un altro sito")


@pytest.mark.parametrize("filename,name", WIRED)
def test_wired_handler_does_not_reload_everything_afterwards(filename, name):
    node = _handler(filename, name)
    assert "charge_records" not in _calls(node), (
        f"{filename}.{name} richiama ancora charge_records(): "
        "annullerebbe il filtro")


def test_us_button_goes_through_the_filtered_loader():
    # Il bottone, non solo view_all(): rimetterlo su `charge_records_n()`
    # riporta il bug senza che view_all() cambi.
    node = _handler(*US_BUTTON)
    assert node is not None
    calls = _calls(node)
    assert "view_all" in calls
    assert "charge_records_n" not in calls
    assert "charge_records" not in calls


def test_us_view_all_chain_filters_and_guards_the_empty_case():
    va = _handler("US_USM.py", "view_all")
    assert va is not None
    assert "charge_records_filtered_by_site" in _calls(va)
    assert "charge_records" not in _calls(va)
    assert "charge_records_n" not in _calls(va)
    # La guardia: `if not self.DATA_LIST:` con dentro il record nuovo.
    guard = any(
        isinstance(n, ast.If) and _mentions(n.test, "DATA_LIST")
        and "on_pushButton_new_rec_pressed" in _calls(
            ast.Module(body=n.body + n.orelse, type_ignores=[]))
        for n in ast.walk(va))
    assert guard
    loader = _handler("US_USM.py", "charge_records_filtered_by_site")
    assert loader is not None
    assert "charge_records_for_site" in _calls(loader)


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


def test_struttura_gis_button_binds_results_on_every_path_and_reports_errors():
    node = _handler("Struttura.py", "on_pushButton_view_all_st_pressed")
    assert node is not None
    # (a) nessun `except ...: pass` che ingoia gli errori in silenzio
    for n in ast.walk(node):
        if isinstance(n, ast.ExceptHandler):
            assert not all(isinstance(b, ast.Pass) for b in n.body), (
                "except: pass nel bottone strutture sul GIS: l'utente "
                "non saprebbe che il caricamento e' fallito")
    # (b) `res` e' assegnato in entrambi i rami dell'if sul sito, e il ciclo
    # che lo legge sta nello stesso try (non dopo un if senza else).
    def stores(stmts, name):
        return any(isinstance(x, ast.Name) and x.id == name
                   and isinstance(x.ctx, ast.Store)
                   for s in stmts for x in ast.walk(s))
    ifs = [n for n in ast.walk(node)
           if isinstance(n, ast.If) and stores(n.body, "res")]
    assert ifs, "nessun ramo assegna `res`"
    for n in ifs:
        assert n.orelse and stores(n.orelse, "res"), (
            "`res` e' assegnato solo in un ramo: senza sito impostato "
            "il ciclo darebbe NameError")
    for tr in (n for n in ast.walk(node) if isinstance(n, ast.Try)):
        if any(n in ifs for n in ast.walk(ast.Module(body=tr.body, type_ignores=[]))):
            reads = [f for f in ast.walk(ast.Module(body=tr.body, type_ignores=[]))
                     if isinstance(f, ast.For) and _mentions(f.iter, "res")]
            assert reads, "il ciclo su `res` deve stare nello stesso try"


def test_every_view_all_handler_in_tabs_is_classified():
    # Una scheda aggiunta domani con il suo «view all» fallisce qui invece di
    # restare senza filtro in silenzio.
    liste = {"WIRED": set(WIRED), "NOT_WIRED": set(NOT_WIRED),
             "OWN_SITE_FILTER": set(OWN_SITE_FILTER), "US": {US_BUTTON}}
    trovati = _all_handlers()
    classificati = set().union(*liste.values())
    assert trovati - classificati == set(), (
        f"handler non classificati: {sorted(trovati - classificati)}")
    nomi = [h for v in liste.values() for h in v]
    assert len(nomi) == len(set(nomi)), "un handler è in più di una lista"
    # E nessuna voce deve riferirsi a un handler che non esiste più.
    assert classificati - trovati == set(), (
        f"voci senza handler: {sorted(classificati - trovati)}")


def test_no_handler_keeps_the_italian_literal():
    # Il testo va letto da no_records_texts(): un letterale lascia la scheda
    # in italiano per chi usa il plugin in un'altra lingua.
    letterale = "Nessun record per il sito corrente"
    for filename, name in WIRED:
        node = _handler(filename, name)
        testo = ast.get_source_segment(
            (_TABS / filename).read_text(encoding="utf-8"), node)
        assert letterale not in testo, f"{filename}.{name} ha il letterale"
    # E dove la scheda mostra il messaggio, lo prende dalla funzione.
    senza = [f for f, n in WIRED
             if f not in ("US_USM.py", "Fauna.py", "pyarchinit_Pottery_mainapp.py")
             and "no_records_texts" not in _calls(_handler(f, n))]
    assert senza == []
