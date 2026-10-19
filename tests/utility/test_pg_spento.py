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


# ------------------------------------------- revisione finale (19 ottobre 2026)

def test_dopo_una_connessione_fallita_il_gestore_condiviso_puo_ancora_salvare(avvisi):
    """Il gestore condiviso (get_db_manager) resta in memoria anche se la
    prima connessione fallisce (server che si sta accendendo, VPN giù): deve
    avere la sua sessione, o quando il server torna le schede caricano i
    record ma non salvano finché non si riavvia QGIS."""
    from modules.db.pyarchinit_db_manager import DbConnectionSingleton, get_db_manager
    conn = _spento()
    try:
        m = get_db_manager(conn, use_singleton=True)
        assert m.Session is not None and m.metadata not in (None, "")
        assert m.connection() is True              # quello in memoria, come prima
    finally:
        DbConnectionSingleton._instances.pop(conn, None)


def test_il_tempo_massimo_si_puo_alzare(avvisi, monkeypatch):
    """10 s se non si dice niente; PGCONNECT_TIMEOUT (la variabile di libpq)
    o connect_timeout nella stringa di connessione per alzarlo."""
    from modules.db import pyarchinit_db_manager as M
    vero = M.create_engine
    argomenti = []
    monkeypatch.setattr(M, "create_engine", lambda *a, **k: argomenti.append(k) or vero(*a, **k))
    monkeypatch.delenv("PGCONNECT_TIMEOUT", raising=False)

    def tempo(conn):
        argomenti.clear()
        M.Pyarchinit_db_management(conn).connection()
        return argomenti[-1]["connect_args"]["connect_timeout"]
    assert tempo(_spento()) == 10
    assert tempo(_spento() + "?connect_timeout=60") == 60
    monkeypatch.setenv("PGCONNECT_TIMEOUT", "3")
    assert tempo(_spento()) == 3


def test_quando_il_server_torna_il_gestore_condiviso_salva(avvisi, monkeypatch):
    """Dall'inizio alla fine: la prima connessione fallisce (server spento,
    simulato), il gestore resta in memoria; il server torna e la scheda
    salva. Prima della correzione: «Database not connected» fino al riavvio
    di QGIS. Schema temporaneo di pyarchinit_test_pg."""
    import psycopg2
    from sqlalchemy import create_engine as vero, event, text
    from modules.db import pyarchinit_db_manager as M
    from tests.sync.conftest_pg import PG_CONN_STR
    nome = "spento_" + uuid.uuid4().hex[:8]
    base = vero(PG_CONN_STR)
    try:
        with base.begin() as c:
            c.execute(text("CREATE SCHEMA %s" % nome))
            c.execute(text("CREATE TABLE %s.t (id INT PRIMARY KEY, x TEXT)" % nome))
            c.execute(text("INSERT INTO %s.t VALUES (1, 'prima')" % nome))
    except Exception as e:                              # noqa: BLE001
        pytest.skip("PostgreSQL di prova non raggiungibile: %s" % e)
    giu = {"si": True}

    def con_guasto(*a, **k):
        eng = vero(*a, **k)

        @event.listens_for(eng, "do_connect")
        def _spento(dialect, conn_rec, cargs, cparams):
            if giu["si"]:
                raise psycopg2.OperationalError("server spento (simulato)")
        return eng
    monkeypatch.setattr(M, "create_engine", con_guasto)
    conn = PG_CONN_STR + "?options=-csearch_path%3D" + nome
    try:
        m = M.get_db_manager(conn, use_singleton=True)
        assert avvisi == ["warning"]                    # la connessione è fallita
        giu["si"] = False                               # ... e il server torna
        assert M.get_db_manager(conn, use_singleton=True) is m
        with m.session_scope() as s:
            s.execute(text("UPDATE t SET x = 'dopo' WHERE id = 1"))
        with base.connect() as c:
            assert c.execute(text("SELECT x FROM %s.t" % nome)).scalar() == "dopo"
    finally:
        M.DbConnectionSingleton._instances.pop(conn, None)
        with base.begin() as c:
            c.execute(text("DROP SCHEMA %s CASCADE" % nome))
        base.dispose()
