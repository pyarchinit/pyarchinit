"""Un PostgreSQL che non risponde (server spento, rete giù): QGIS non deve
restare fermo. Prima ``connection()`` lanciava l'aggiornamento dello schema
prima di provare la connessione, e ognuno dei suoi controlli tentava una
connessione nuova senza tempo massimo (75 s l'una su macOS, misurati con
192.0.2.1): decine di minuti di QGIS bloccato. Qui una porta chiusa di
questo Mac, che rifiuta subito, così i test restano veloci."""
from __future__ import annotations

import re
import sys
import time
import uuid
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

PLUGIN = (_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")


def _spento():
    # un nome di database nuovo ogni volta: connection() ricorda per sessione
    # i database già controllati
    return "postgresql://utente:prova@127.0.0.1:59999/spento_%s" % uuid.uuid4().hex[:8]


@pytest.fixture
def avvisi(monkeypatch):
    from qgis.PyQt.QtWidgets import QMessageBox
    detti = []
    for nome in ("information", "warning", "critical"):
        monkeypatch.setattr(QMessageBox, nome, staticmethod(lambda *a, _n=nome, **k: detti.append(_n) or QMessageBox.Ok))
    return detti


def test_con_il_server_spento_l_aggiornamento_dello_schema_non_parte(avvisi, monkeypatch):
    from modules.db import postgres_db_updater as U
    from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
    lanciati = []
    monkeypatch.setattr(U, "check_and_update_postgres_db", lambda *a, **k: lanciati.append(1))
    db = Pyarchinit_db_management(_spento())
    t = time.monotonic()
    assert db.connection() is False
    assert lanciati == []
    assert avvisi == ["warning"]                 # un avviso solo, quello di connection()
    assert time.monotonic() - t < 5


def test_postgresql_ha_un_tempo_massimo_per_collegarsi(avvisi, monkeypatch):
    from modules.db import pyarchinit_db_manager as M
    vero = M.create_engine
    argomenti = []
    monkeypatch.setattr(M, "create_engine", lambda *a, **k: argomenti.append(k) or vero(*a, **k))
    M.Pyarchinit_db_management(_spento()).connection()
    tempi = [k.get("connect_args", {}).get("connect_timeout") for k in argomenti]
    assert tempi and all(t and 0 < int(t) <= 15 for t in tempi)


def test_le_voci_extended_matrix_non_aprono_niente_se_la_connessione_fallisce():
    for voce in ("_run_em_export", "_run_em_sections", "_run_em_project", "_run_em_import",
                 "_run_em_matrix_view", "_run_room_delivery"):
        corpo = PLUGIN[PLUGIN.index("    def %s(self):" % voce):]
        corpo = corpo[:corpo.index("\n    def ", 10)]
        assert re.search(r"if db\.connection\(\) is False:\s*\n\s*return", corpo), voce
