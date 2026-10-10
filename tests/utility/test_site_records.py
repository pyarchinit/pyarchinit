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
        self.cache_cleared = 0

    def clear_cache(self):
        self.cache_cleared += 1

    def query_bool(self, params, table_class_name):
        self.calls.append((params, table_class_name))
        sito = params.get("sito")
        if sito is None:
            return list(self.rows)
        sito = sito.strip("'")
        # Se le righe portano un sito, la finta query lo rispetta davvero.
        return [r for r in self.rows
                if not hasattr(r, "sito") or r.sito == sito]


class Row:
    def __init__(self, id_us=None, sito=None, attr="id_us"):
        if id_us is not None:
            setattr(self, attr, id_us)
        if sito is not None:
            self.sito = sito


class FakeLabel:
    def __init__(self):
        self.text = None

    def setText(self, t):
        self.text = t


class FakeTab:
    MAPPER_TABLE_CLASS = "US"
    ID_TABLE = "id_us"

    def __init__(self, rows=None, all_rows=None):
        self.DB_MANAGER = FakeDB(rows)
        self.DATA_LIST = []
        self.REC_TOT = 99
        self.REC_CORR = 99
        self._all = all_rows or []
        self.counter = []
        self.BROWSE_STATUS = "b"
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = "vecchio"
        self.STATUS_ITEMS = {"b": "Usa", "n": "Nuovo"}
        self.label_status = FakeLabel()

    def set_rec_counter(self, tot, corr):
        self.counter.append((tot, corr))

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


def test_filtered_list_is_sorted_by_the_forms_id_ascending(monkeypatch):
    # query_bool non ordina: senza l'ordinamento «view all» cambierebbe
    # il primo record mostrato rispetto a charge_records() (id crescente).
    _site(monkeypatch, "Scavo")
    tab = FakeTab(rows=[Row(30), Row(5), Row(12)])
    assert SR.charge_records_for_site(tab) is True
    assert [r.id_us for r in tab.DATA_LIST] == [5, 12, 30]


def test_sorting_tolerates_missing_attribute_and_none_id(monkeypatch):
    _site(monkeypatch, "Scavo")
    senza_id = Row()          # manca l'attributo
    con_none = Row(None)
    con_none.id_us = None
    tab = FakeTab(rows=[Row(9), senza_id, Row(2), con_none])
    assert SR.charge_records_for_site(tab) is True
    ids = [getattr(r, "id_us", None) for r in tab.DATA_LIST]
    assert ids[:2] == [2, 9]
    assert len(tab.DATA_LIST) == 4


def test_cache_is_cleared_before_loading_with_a_site(monkeypatch):
    _site(monkeypatch, "Scavo")
    tab = FakeTab(rows=[Row(1)])
    SR.charge_records_for_site(tab)
    assert tab.DB_MANAGER.cache_cleared == 1


def test_cache_is_cleared_also_without_a_site(monkeypatch):
    _site(monkeypatch, "")
    tab = FakeTab(all_rows=[Row(1)])
    SR.charge_records_for_site(tab)
    assert tab.DB_MANAGER.cache_cleared == 1


def test_a_failing_clear_cache_does_not_break_loading(monkeypatch):
    _site(monkeypatch, "Scavo")
    tab = FakeTab(rows=[Row(1)])

    def boom():
        raise RuntimeError("cache rotta")
    tab.DB_MANAGER.clear_cache = boom
    assert SR.charge_records_for_site(tab) is True


def test_only_the_current_sites_rows_come_back(monkeypatch):
    _site(monkeypatch, "Scavo")
    rows = [Row(1, sito="Scavo"), Row(2, sito="Altro"), Row(3, sito="Scavo")]
    tab = FakeTab(rows=rows)
    assert SR.charge_records_for_site(tab) is True
    assert [r.id_us for r in tab.DATA_LIST] == [1, 3]


def test_sort_uses_the_forms_own_id_column(monkeypatch):
    _site(monkeypatch, "Scavo")
    tab = FakeTab(rows=[Row(7, attr="id_tomba"), Row(2, attr="id_tomba"),
                        Row(5, attr="id_tomba")])
    tab.ID_TABLE = "id_tomba"
    SR.charge_records_for_site(tab)
    assert [r.id_tomba for r in tab.DATA_LIST] == [2, 5, 7]


def test_mixed_type_ids_sort_without_raising(monkeypatch):
    _site(monkeypatch, "Scavo")
    tab = FakeTab(rows=[Row(30), Row("5"), Row(None)])
    assert SR.charge_records_for_site(tab) is True
    ids = [getattr(r, "id_us", None) for r in tab.DATA_LIST]
    assert ids == ["5", 30, None]


def test_current_site_reads_and_strips_the_configured_site(monkeypatch):
    import modules.db.pyarchinit_conn_strings as cs

    class Conn:
        def sito_set(self):
            return {"sito_set": "  Villa Romana \n"}

    monkeypatch.setattr(cs, "Connection", Conn)
    assert SR.current_site() == "Villa Romana"


def test_current_site_empty_when_no_site_configured(monkeypatch):
    import modules.db.pyarchinit_conn_strings as cs

    class Conn:
        def sito_set(self):
            return {"sito_set": ""}

    monkeypatch.setattr(cs, "Connection", Conn)
    assert SR.current_site() == ""


def test_current_site_logs_a_warning_when_config_unreadable(monkeypatch, caplog):
    import logging
    import modules.db.pyarchinit_conn_strings as cs

    class Boom:
        def __init__(self, *a, **k):
            raise RuntimeError("config illeggibile")

    monkeypatch.setattr(cs, "Connection", Boom)
    with caplog.at_level(logging.WARNING):
        assert SR.current_site() == ""
    assert any("config" in r.getMessage().lower() for r in caplog.records)


def test_clear_form_state_resets_everything_navigation_reads():
    tab = FakeTab()
    tab.DATA_LIST = ["x"]
    SR.clear_form_state(tab)
    assert tab.DATA_LIST == []
    assert (tab.REC_TOT, tab.REC_CORR) == (0, 0)
    assert tab.DATA_LIST_REC_TEMP is None and tab.DATA_LIST_REC_CORR is None
    assert tab.BROWSE_STATUS == "x"
    assert tab.counter == [(0, 0)]


def test_clear_form_state_sets_label_when_status_x_exists():
    tab = FakeTab()
    tab.STATUS_ITEMS = {"b": "Usa", "x": "Nessun record"}
    SR.clear_form_state(tab)
    assert tab.label_status.text == "Nessun record"


def test_clear_form_state_adds_x_status_when_form_lacks_it():
    # Con BROWSE_STATUS = "x" un STATUS_ITEMS[BROWSE_STATUS] sulle schede
    # senza la voce solleverebbe KeyError.
    tab = FakeTab()
    SR.clear_form_state(tab)
    assert "x" in tab.STATUS_ITEMS
    assert tab.label_status.text == tab.STATUS_ITEMS["x"]


def test_clear_form_state_never_raises_on_a_bare_object():
    class Bare:
        pass
    SR.clear_form_state(Bare())


def test_clear_form_state_survives_failing_counter():
    tab = FakeTab()

    def boom(*a):
        raise RuntimeError("x")
    tab.set_rec_counter = boom
    SR.clear_form_state(tab)
    assert tab.REC_TOT == 0
