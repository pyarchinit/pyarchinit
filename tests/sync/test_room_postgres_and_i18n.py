"""What a pull into PostgreSQL measured (26 Nov 2026), held without a server,
and the ten languages of the StratiGraph windows.

* PostgreSQL gives Decimal('1.40') for a numeric column, the em.json 1.4:
  compared as text, 44 units were «updated» at every pull.
* The library read PostgreSQL with a reduced importer whose node id is the US
  NUMBER: pyArchInit swaps in the full importer (node id = node_uuid).
* «2» in the room and «2.0» here are the same value, not a field change.
"""
from __future__ import annotations

import decimal
import datetime
import string
from types import SimpleNamespace


def test_numbers_and_dates_compare_as_values():
    from modules.s3dgraphy.sync.graph_ingestor import _values_equal
    assert _values_equal("larghezza_media", decimal.Decimal("1.40"), 1.4)
    assert _values_equal("quota_abs", decimal.Decimal("488.80"), "488.8")
    assert not _values_equal("quota_abs", decimal.Decimal("488.80"), 488.81)
    assert _values_equal("data_rilevazione", datetime.date(2021, 4, 5), "2021-04-05")
    assert not _values_equal("colore", "Bruno", "bruno")


def test_the_same_number_is_not_a_field_change():
    from modules.stratigraph.room_sync import _same_number
    node = SimpleNamespace(data={"larghezza_media": 2, "colore": "Bruno"})
    remote = SimpleNamespace(find_node_by_id=lambda nid: node)
    assert _same_number({"op": "update_field", "node_id": "u", "field": "data.larghezza_media", "value": 2.0}, remote)
    assert not _same_number({"op": "update_field", "node_id": "u", "field": "data.larghezza_media", "value": 2.5}, remote)
    assert not _same_number({"op": "update_field", "node_id": "u", "field": "data.colore", "value": "Rosso"}, remote)


def test_a_column_this_database_lacks_is_not_an_edit():
    from s3dgraphy.contract import Delta
    from modules.stratigraph import room_sync as RS
    delta = Delta(nodes=[], edges=[])
    delta.update_field("u5", "data.sing_doc", remove=True)        # PostgreSQL schema has no sing_doc
    delta.update_field("u5", "data.colore", remove=True)          # a real removal
    out = RS._without_noise(delta, set(), frozenset(), frozenset({"sing_doc"}))
    assert [op["field"] for op in out.ops] == ["data.colore"]


def test_every_text_in_ten_languages_with_the_same_placeholders():
    from gui import stratigraph_i18n as I
    fields = lambda txt: {f[1] for f in string.Formatter().parse(txt) if f[1]}
    for key, texts in I.TEXTS.items():
        assert set(texts) == set(I.LANGS), key
        for lang, txt in texts.items():
            assert fields(txt) == fields(texts["en"]), (key, lang)


def test_the_language_falls_back_to_english(monkeypatch):
    from gui import stratigraph_i18n as I
    monkeypatch.setattr(I, "lang", lambda: "it")
    assert I.t("pull") == "Porta dalla stanza"
    assert I.t("pulled", room="r", ins=1, upd=2) == "✔ Portato da r: 1 unità nuove, 2 aggiornate"
    monkeypatch.setattr(I, "lang", lambda: "en")
    assert I.t("no-such-key") == "no-such-key"


def test_the_client_pyarchinit_signs_in_as():
    from modules.stratigraph.node_client import client_of
    node = {"native_client_id": "em-tools"}
    assert client_of(node) == "em-tools"                                   # as today
    assert client_of(node, "pyarchinit") == "pyarchinit"                   # a setting
    assert client_of(dict(node, native_clients={"pyarchinit": "pa"})) == "pa"   # announced by the node
