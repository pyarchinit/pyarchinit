"""Il pannello «Verifica rapporti»: l'annulla e il sito, provati davvero.

Si provano i **metodi veri** del pannello — `_run`, `_render`, `_apply`,
`_rollback` — su uno stub di attributi, perché in questo ambiente costruire
un `QWidget` dentro pytest aborta il processo (è la ragione per cui i due
test smoke dei dialoghi stanno fra gli `--ignore` del comando di verifica).
Gli elementi dell'albero sono `QTreeWidgetItem` veri, che senza finestra
funzionano: così `_selected_issues` legge le spunte che `_render` ha messo,
che è il punto.

Il grafo si sostituisce con uno vuoto: qui non si verificano i rapporti, si
verifica il *ciclo di vita* di quello che la finestra promette — «potrai
annullare con 'Annulla ultimo fix'» — e che le correzioni finiscano nel sito
che l'albero sta mostrando. Gli avvisi cronologici arrivano dal database di
prova, che è di due siti.
"""
from __future__ import annotations

import sqlite3
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


def _qt_disponibile():
    try:
        from qgis.PyQt.QtWidgets import QTreeWidgetItem  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(not _qt_disponibile(),
                                reason="Qt di QGIS non disponibile")

SITO_A = "Scavo A"
SITO_B = "Scavo B"


@pytest.fixture()
def db(tmp_path):
    """Due siti, un disallineamento ciascuno: `datazione` ≠ `datazione_estesa`.

    È la categoria automatica, quindi l'albero la mostra già spuntata e
    «Applica» ha qualcosa da scrivere senza che nessuno spunti niente.
    """
    p = tmp_path / "pannello.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, area TEXT, us TEXT,"
              " unita_tipo TEXT, rapporti TEXT, periodo_iniziale TEXT,"
              " fase_iniziale TEXT, periodo_finale TEXT, fase_finale TEXT,"
              " datazione TEXT)")
    c.execute("CREATE TABLE periodizzazione_table (sito TEXT,"
              " periodo INTEGER, fase TEXT, cron_iniziale INTEGER,"
              " cron_finale INTEGER, datazione_estesa TEXT, descrizione TEXT)")
    for sito, datazione in ((SITO_A, "SBAGLIATA A"), (SITO_B, "SBAGLIATA B")):
        c.execute("INSERT INTO us_table VALUES (?,'1','1','US','[]','2','1',"
                  "'2','1',?)", (sito, datazione))
        c.execute("INSERT INTO periodizzazione_table VALUES "
                  "(?,2,'1',1500,1549,?,'')", (sito, "XVI secolo " + sito))
    c.commit(); c.close()
    return p


def _datazioni(db):
    c = sqlite3.connect(db)
    try:
        return dict(c.execute(
            "SELECT sito, datazione FROM us_table ORDER BY sito").fetchall())
    finally:
        c.close()


class _Combo:
    def __init__(self, testo=""):
        self._testo = testo

    def currentText(self):
        return self._testo

    def setCurrentText(self, testo):
        self._testo = testo


class _Albero:
    """Quel tanto di `QTreeWidget` che `_render` e `_selected_issues` usano."""

    def __init__(self):
        self._tops = []
        self._scelti = []

    def clear(self):
        self._tops = []
        self._scelti = []

    def selectedItems(self):
        return self._scelti

    def seleziona(self, kind):
        """La prima riga di quella categoria, come un clic dell'utente."""
        from qgis.PyQt.QtCore import Qt
        for top in self._tops:
            for j in range(top.childCount()):
                ch = top.child(j)
                iss = ch.data(0, int(Qt.UserRole))
                if iss is not None and iss.kind == kind:
                    self._scelti = [ch]
                    return iss
        raise AssertionError("nessuna riga di categoria %r" % kind)

    def addTopLevelItem(self, item):
        self._tops.append(item)

    def topLevelItemCount(self):
        return len(self._tops)

    def topLevelItem(self, i):
        return self._tops[i]


class _Etichetta:
    def __init__(self):
        self._testo = ""

    def setText(self, testo):
        self._testo = testo

    def text(self):
        return self._testo


class _Anteprima:
    def __init__(self):
        self._testo = ""

    def setPlainText(self, testo):
        self._testo = testo

    def toPlainText(self):
        return self._testo


class _Bottone:
    def __init__(self):
        self._attivo = False

    def setEnabled(self, attivo):
        self._attivo = bool(attivo)

    def isEnabled(self):
        return self._attivo


@pytest.fixture()
def panel(db, monkeypatch):
    """Il pannello sul database di prova, con il projector sostituito.

    `populate_graph` costa un grafo intero e qui non serve: la verifica dei
    rapporti su un grafo vuoto non trova niente, e gli avvisi cronologici —
    quelli che interessano — vengono dal database.
    """
    from qgis.PyQt.QtWidgets import QMessageBox

    from s3dgraphy.graph import Graph
    from modules.s3dgraphy.sync import graph_projector as GP

    class _ProjectorFinto:
        def populate_graph(self, handle, sito=None, *a, **kw):
            return Graph(graph_id="prova")

    monkeypatch.setattr(GP, "GraphProjector", _ProjectorFinto)

    detti = []
    monkeypatch.setattr(QMessageBox, "question",
                        staticmethod(lambda *a, **k: QMessageBox.Yes))
    for nome in ("information", "warning", "critical"):
        monkeypatch.setattr(
            QMessageBox, nome,
            staticmethod(lambda *a, _n=nome, **k: detti.append((_n, a[2]))))

    from gui.rapporti_check_dialog import RapportiCheckPanel

    class _Pannello:
        # I metodi veri, su attributi finti.
        _handle = RapportiCheckPanel._handle
        _run = RapportiCheckPanel._run
        _render = RapportiCheckPanel._render
        _selected_issues = RapportiCheckPanel._selected_issues
        _apply = RapportiCheckPanel._apply
        _rollback = RapportiCheckPanel._rollback
        _preview = RapportiCheckPanel._preview

        def __init__(self):
            self._db_provider = lambda: "sqlite:///%s" % db
            self._lang = "it"
            self._report = None
            self._token = None
            self._chrono_bounds = {}
            self._chrono_errore = None
            self.cboSite = _Combo()
            self.tree = _Albero()
            self.lblSummary = _Etichetta()
            self.preview = _Anteprima()
            self.btnRollback = _Bottone()
            self.detti = detti

    return _Pannello()


def _issues(panel):
    return [i.kind for i in panel._report.issues]


# ---------------------------------------------------------------------------
# «Annulla ultimo fix» era acceso e non faceva niente
# ---------------------------------------------------------------------------

def test_the_undo_keeps_its_token_across_the_rescan(panel, db):
    """`_apply` salvava il token, poi la riverifica chiamava `_render`, che lo
    azzerava — e il bottone restava acceso su un annulla che non c'era."""
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    assert "datazione_mismatch" in _issues(panel)
    panel._apply()
    assert _datazioni(db)[SITO_A] == "XVI secolo " + SITO_A
    assert panel._token is not None, "il token dell'annulla è stato perso"
    assert panel.btnRollback.isEnabled()


def test_the_undo_puts_the_values_back(panel, db):
    """La promessa della conferma — «potrai annullare con 'Annulla ultimo
    fix'» — si prova sul valore nel database, non sul bottone."""
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    prima = _datazioni(db)
    panel._apply()
    assert _datazioni(db) != prima
    panel._rollback()
    assert _datazioni(db) == prima
    assert not panel.btnRollback.isEnabled()


def test_the_undo_says_so_when_there_is_nothing_to_undo(panel):
    """Senza token tornava in silenzio: un bottone che non risponde non si
    distingue da un bottone rotto."""
    panel._rollback()
    assert panel.detti, "nessun messaggio: l'annulla è tornato in silenzio"
    assert not panel.btnRollback.isEnabled()


def test_a_fresh_scan_clears_the_undo_and_the_button_with_it(panel, db):
    """Una verifica lanciata a mano riparte da zero: il bottone si spegne
    insieme al token, così i due non si contraddicono mai."""
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    panel._apply()
    panel._run()
    assert panel._token is None
    assert not panel.btnRollback.isEnabled()


# ---------------------------------------------------------------------------
# Cambiare sito fra «Esegui verifica» e «Applica»
# ---------------------------------------------------------------------------

def test_changing_the_site_before_applying_refuses_to_write(panel, db):
    """L'albero mostra ancora le spunte del sito di prima: applicarle al sito
    nuovo scriverebbe le correzioni di uno sulle righe dell'altro."""
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    prima = _datazioni(db)
    panel.cboSite.setCurrentText(SITO_B)
    panel._apply()
    assert _datazioni(db) == prima, "scritto nel sito sbagliato"
    assert any(SITO_A in str(t) and SITO_B in str(t)
               for _n, t in panel.detti), panel.detti


def test_the_tree_survives_the_refusal(panel, db):
    """Si rifiuta invece di svuotare l'albero: le spunte sono lavoro
    dell'archeologo, e tornare sul sito giusto le ritrova."""
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    quante = len(panel._selected_issues())
    assert quante
    panel.cboSite.setCurrentText(SITO_B)
    panel._apply()
    assert len(panel._selected_issues()) == quante
    panel.cboSite.setCurrentText(SITO_A)
    panel._apply()
    assert _datazioni(db)[SITO_A] == "XVI secolo " + SITO_A


def test_the_two_panel_messages_are_in_all_six_languages():
    """`_t` ripiega sull'inglese, quindi una chiave mancante non si vedrebbe
    dal messaggio: si guarda il dizionario. E il rifiuto nomina i due siti,
    altrimenti non si capisce quale dei due si stava correggendo."""
    from modules.utility.rapporti_check import _L, _t
    for lang in ("it", "en", "de", "es", "fr", "pt"):
        for chiave in ("m_site_changed", "m_nothing_to_undo"):
            assert chiave in _L[lang], (lang, chiave)
        testo = _t(lang, "m_site_changed").format(atteso="Alfa", scelto="Beta")
        assert "Alfa" in testo and "Beta" in testo, lang


def test_a_textual_year_does_not_take_the_whole_panel_away(panel, db):
    """`build_chronology` si chiama fuori dal try della cronologia: con un
    anno a testo sollevava, e la finestra diceva «Verifica fallita» — via
    anche la verifica dei rapporti, che non aveva nessuna colpa."""
    c = sqlite3.connect(db)
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "(?,9,'1','XV sec',1499,'',' ')", (SITO_A,))
    c.commit(); c.close()
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    assert panel._report is not None
    assert "epoch_no_dates" in _issues(panel)
    assert not any(n == "critical" for n, _t in panel.detti), panel.detti


def test_the_preview_of_an_overlap_does_not_show_a_us_chronology(panel, db):
    """`us_path` di una sovrapposizione porta etichette di fase, e una fase
    senza nome si legge col solo periodo: «4». Su un sito che ha anche la US 4
    l'anteprima mostrava la cronologia di quella US sotto un avviso che
    parlava della fase — una data attribuita alla cosa sbagliata.
    """
    c = sqlite3.connect(db)
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "(?,4,NULL,1000,1300,'',''), (?,5,NULL,1200,1400,'','')",
              (SITO_A, SITO_A))
    c.commit(); c.close()
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    iss = panel.tree.seleziona("epoch_overlap")
    assert iss.us_path == ["4", "5"]
    # La cronologia calcolata della US 4 esiste: è quella che non deve
    # comparire sotto un avviso che parla della fase 4.
    panel._chrono_bounds = {"4": {"start": 1500.0, "end": 1549.0,
                                  "rule": "epoch"}}
    panel._preview()
    testo = panel.preview.toPlainText()
    assert "1500–1549" not in testo, testo


def test_the_preview_of_a_sheet_dating_still_shows_its_chronology(panel, db):
    """Il taglio è per categoria, non per tutti: su un avviso che nomina
    davvero una US la riga della data calcolata resta."""
    panel.cboSite.setCurrentText(SITO_A)
    panel._run()
    panel.tree.seleziona("datazione_mismatch")
    panel._chrono_bounds = {"1": {"start": 1500.0, "end": 1549.0,
                                  "rule": "epoch"}}
    panel._preview()
    assert "US 1 · 1500–1549" in panel.preview.toPlainText()
