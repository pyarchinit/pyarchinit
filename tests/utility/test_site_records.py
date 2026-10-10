"""«View all» deve mostrare i record del sito su cui il plugin è settato.

Fino alla 5.13.64 il bottone caricava la tabella intera. Qui il database e
la scheda sono finti: conta che il sito arrivi davvero alla query.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility import site_records as SR


class FakeDB:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else []
        self.calls = []

    def query_bool(self, params, table_class_name):
        self.calls.append((params, table_class_name))
        return list(self.rows)


class FakeTab:
    MAPPER_TABLE_CLASS = "US"

    def __init__(self, rows=None, all_rows=None):
        self.DB_MANAGER = FakeDB(rows)
        self.DATA_LIST = []
        self.REC_TOT = 99
        self.REC_CORR = 99
        self._all = all_rows or []

    def charge_records(self):
        self.DATA_LIST = list(self._all)


def _site(monkeypatch, value):
    monkeypatch.setattr(SR, "current_site", lambda: value)


def test_records_for_site_passes_the_site_to_the_query():
    db = FakeDB(rows=["a", "b"])
    out = SR.records_for_site(db, "US", "Scavo")
    assert out == ["a", "b"]
    assert len(db.calls) == 1
    params, name = db.calls[0]
    assert name == "US"
    assert "Scavo" in params["sito"]


def test_charge_fills_data_list_and_returns_true(monkeypatch):
    _site(monkeypatch, "Scavo")
    tab = FakeTab(rows=["r1", "r2", "r3"])
    assert SR.charge_records_for_site(tab) is True
    assert tab.DATA_LIST == ["r1", "r2", "r3"]
    assert (tab.REC_TOT, tab.REC_CORR) == (3, 0)
    assert "Scavo" in tab.DB_MANAGER.calls[0][0]["sito"]


def test_without_site_loads_everything(monkeypatch):
    _site(monkeypatch, "")
    tab = FakeTab(rows=["solo-sito"], all_rows=["x", "y"])
    assert SR.charge_records_for_site(tab) is True
    assert tab.DATA_LIST == ["x", "y"]
    assert tab.DB_MANAGER.calls == []
    assert (tab.REC_TOT, tab.REC_CORR) == (2, 0)


def test_site_without_records_returns_false_and_empty_list(monkeypatch):
    _site(monkeypatch, "Vuoto")
    tab = FakeTab(rows=[])
    tab.DATA_LIST = ["vecchio"]
    assert SR.charge_records_for_site(tab) is False
    assert tab.DATA_LIST == []


def test_current_site_returns_empty_string_when_config_unreadable(monkeypatch):
    import modules.db.pyarchinit_conn_strings as cs

    class Boom:
        def __init__(self, *a, **k):
            raise RuntimeError("config illeggibile")

    monkeypatch.setattr(cs, "Connection", Boom)
    assert SR.current_site() == ""
