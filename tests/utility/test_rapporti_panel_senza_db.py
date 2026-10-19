"""Il pannello «Verifica rapporti» senza database: costruito dentro la
finestra Extended Matrix legge subito i siti, e se non c'è un database
apriva un avviso modale prima ancora che la finestra si vedesse (e senza
schermo, nei test, aspettava per sempre). Ora lo dice dentro il pannello,
spegne i pulsanti e rilegge i siti quando il database c'è."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture
def avvisi(monkeypatch):
    """Gli avvisi modali, contati invece che aperti."""
    from qgis.PyQt.QtWidgets import QMessageBox
    detti = []
    for nome in ("information", "warning", "critical"):
        monkeypatch.setattr(QMessageBox, nome,
                            staticmethod(lambda *a, _n=nome, **k: detti.append((_n, a[2] if len(a) > 2 else ""))))
    return detti


def _db(tmp_path):
    p = tmp_path / "siti.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, area TEXT, us TEXT)")
    c.execute("INSERT INTO us_table VALUES ('Scavo A', '1', '1')")
    c.commit()
    c.close()
    return "sqlite:///%s" % p


def _apri(pannello):
    """La scheda che si apre: il pannello legge i siti solo allora."""
    from qgis.PyQt.QtGui import QShowEvent
    pannello.showEvent(QShowEvent())
    return pannello


def test_senza_database_nessun_avviso_e_i_pulsanti_spenti(avvisi):
    from gui.rapporti_check_dialog import RapportiCheckPanel
    pannello = _apri(RapportiCheckPanel(db_provider=lambda: None))
    assert avvisi == []
    assert "database" in pannello.lblStato.text().lower()
    assert not pannello.lblStato.isHidden()
    for b in (pannello.btnRun, pannello.btnContinuity, pannello.btnApply):
        assert not b.isEnabled()


def test_quando_il_database_c_e_i_siti_si_rileggono(avvisi, tmp_path):
    from gui.rapporti_check_dialog import RapportiCheckPanel
    db = {"x": None}
    pannello = RapportiCheckPanel(db_provider=lambda: db["x"])
    db["x"] = _db(tmp_path)
    pannello.select_sito("Scavo A")                      # dopo l'import nella finestra
    assert [pannello.cboSite.itemText(i) for i in range(pannello.cboSite.count())] == ["Scavo A"]
    assert pannello.btnRun.isEnabled() and pannello.lblStato.isHidden()
    assert avvisi == []


def test_riprova_rilegge_i_siti(avvisi, tmp_path):
    from gui.rapporti_check_dialog import RapportiCheckPanel
    db = {"x": None}
    pannello = _apri(RapportiCheckPanel(db_provider=lambda: db["x"]))
    assert not pannello.btnRiprova.isHidden()
    db["x"] = _db(tmp_path)
    pannello.btnRiprova.click()
    assert pannello.cboSite.count() == 1 and pannello.btnRun.isEnabled()
    assert pannello.btnRiprova.isHidden()


def test_il_pannello_non_legge_niente_finche_la_scheda_non_si_apre(avvisi, tmp_path):
    """La finestra Extended Matrix si apre sulla scheda Import: il pannello
    non deve collegarsi al database (con un server spento, 75 s fermi)."""
    from gui.rapporti_check_dialog import RapportiCheckPanel
    letture = []
    percorso = _db(tmp_path)
    pannello = RapportiCheckPanel(db_provider=lambda: letture.append(1) or percorso)
    assert letture == []
    _apri(pannello)
    assert letture == [1] and pannello.cboSite.count() == 1
    _apri(pannello)
    assert letture == [1]                       # già letti: non si rilegge


def test_dopo_un_errore_di_connessione_la_scheda_non_riprova_da_sola(avvisi):
    """Un server che non risponde: un tentativo quando la scheda si apre,
    poi solo con «Riprova» (ogni tentativo può tenere QGIS fermo)."""
    from gui.rapporti_check_dialog import RapportiCheckPanel
    tentativi = []
    spento = "postgresql://utente:prova@127.0.0.1:59999/spento"
    pannello = _apri(RapportiCheckPanel(db_provider=lambda: tentativi.append(1) or spento))
    assert len(tentativi) == 1 and not pannello.btnRun.isEnabled()
    _apri(pannello)
    _apri(pannello)
    assert len(tentativi) == 1
    pannello.btnRiprova.click()
    assert len(tentativi) == 2 and avvisi == []


def test_il_messaggio_e_nelle_sei_lingue():
    from modules.utility.rapporti_check import _L
    for lang in ("it", "en", "de", "es", "fr", "pt"):
        assert "m_no_database" in _L[lang], lang


def test_la_finestra_extended_matrix_senza_database_non_apre_avvisi(avvisi):
    from modules.s3dgraphy.s3dgraphy_dot_bridge import S3DGraphyExportDialog
    S3DGraphyExportDialog(db_manager=None)
    assert avvisi == []


# ------------------------------------------- seconda revisione (19 ottobre 2026)

def test_un_database_che_non_si_legge_lo_dice_con_parole_sue(avvisi, tmp_path, monkeypatch):
    import gui.rapporti_check_dialog as dlg
    monkeypatch.setattr(dlg, "_qgis_lang", lambda: "it")
    vuoto = tmp_path / "vuoto.sqlite"
    sqlite3.connect(vuoto).close()                      # c'è, ma senza us_table
    pannello = _apri(dlg.RapportiCheckPanel(db_provider=lambda: "sqlite:///%s" % vuoto))
    testo = pannello.lblStato.text()
    assert "non si legge" in testo and "Nessun database" not in testo
    assert "((" not in testo and "us_table" in testo
    assert avvisi == [] and not pannello.btnRun.isEnabled()


def test_il_messaggio_del_database_che_non_si_legge_e_nelle_sei_lingue():
    from modules.utility.rapporti_check import _L
    for lang in ("it", "en", "de", "es", "fr", "pt"):
        assert "{errore}" in _L[lang].get("m_db_unreadable", ""), lang
