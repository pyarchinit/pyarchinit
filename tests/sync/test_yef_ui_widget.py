"""yE-F UI widget logic tests — populate, save, visibility.

These tests bypass Qt by mocking QListWidget. The real Qt widget is
exercised at smoke level via QGIS manual testing; this file pins the
business logic that runs around the widget.

The helpers live in ``tabs/US_USM.py`` (per yE-F Task 13 spec), but that
module's top-level imports require QGIS, which is not available in the
test environment. To exercise the pure-logic helpers without QGIS we
source-extract just the ``_populate_other_locations_logic`` and
``_save_other_locations_logic`` function definitions from the file and
``exec`` them in a clean namespace.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
US_USM_PATH = PLUGIN_ROOT / "tabs" / "US_USM.py"


def _load_yef_helpers():
    """Source-extract the yE-F helpers from tabs/US_USM.py without
    triggering the module's QGIS imports.

    Also extracts the ``_YEF_PARADATA_UTS`` module-level frozenset on
    which the visibility helper depends.
    """
    source = US_USM_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    wanted = {
        "_populate_other_locations_logic",
        "_save_other_locations_logic",
        "_yef_widget_visible_for_unita_tipo",
    }
    extracted_src_parts = ["import json\n"]
    for node in tree.body:
        # Carry the _YEF_PARADATA_UTS frozenset assignment so the
        # visibility helper can resolve it at exec time.
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "_YEF_PARADATA_UTS":
                    extracted_src_parts.append(ast.get_source_segment(source, node))
                    extracted_src_parts.append("\n\n")
        if isinstance(node, ast.FunctionDef) and node.name in wanted:
            extracted_src_parts.append(ast.get_source_segment(source, node))
            extracted_src_parts.append("\n\n")
    ns: dict = {}
    exec("".join(extracted_src_parts), ns)  # noqa: S102 - controlled source
    missing = wanted - set(ns)
    if missing:
        raise RuntimeError(
            f"Could not extract yE-F helpers from {US_USM_PATH}: "
            f"missing {missing}"
        )
    return (
        ns["_populate_other_locations_logic"],
        ns["_save_other_locations_logic"],
        ns["_yef_widget_visible_for_unita_tipo"],
    )


(
    _populate_other_locations_logic,
    _save_other_locations_logic,
    _yef_widget_visible_for_unita_tipo,
) = _load_yef_helpers()


class _FakeListWidget:
    """In-memory stand-in for QListWidget."""

    def __init__(self):
        self.items: list[tuple[str, bool]] = []
        self.visible = True

    def clear(self):
        self.items = []

    def addItem(self, text):
        self.items.append((str(text), False))

    def selectedItems(self):
        return [_FakeItem(t) for t, sel in self.items if sel]

    def select(self, text):
        self.items = [(t, t == text or sel) for t, sel in self.items]

    def setVisible(self, v):
        self.visible = v


class _FakeItem:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


def test_populate_other_locations_from_db_distinct_attivita():
    """Widget loads DISTINCT attivita values from us_table for the sito."""
    widget = _FakeListWidget()
    db_rows = [("VA01",), ("VA04",), ("VA05",), ("VA01",), (None,)]
    current_other_locations = '["VA04"]'

    _populate_other_locations_logic(
        widget, db_rows, current_other_locations,
    )

    item_texts = [t for t, _ in widget.items]
    assert item_texts == ["VA01", "VA04", "VA05"]
    selected_texts = [t for t, sel in widget.items if sel]
    assert selected_texts == ["VA04"]


def test_save_other_locations_returns_json():
    """Serialize selected items into JSON list, exclude primary."""
    widget = _FakeListWidget()
    widget.addItem("VA01")
    widget.addItem("VA04")
    widget.addItem("VA05")
    widget.select("VA04")
    widget.select("VA05")
    widget.select("VA01")

    json_str = _save_other_locations_logic(widget, current_attivita="VA01")

    parsed = json.loads(json_str)
    assert parsed == ["VA04", "VA05"]


def test_save_other_locations_returns_none_when_empty():
    """Empty selection → None (DB NULL)."""
    widget = _FakeListWidget()
    widget.addItem("VA01")

    result = _save_other_locations_logic(widget, current_attivita="VA01")

    assert result is None


def test_yef_widget_visible_for_unita_tipo():
    """Paradata types show the widget; stratigraphic types hide it."""
    fn = _yef_widget_visible_for_unita_tipo
    # Paradata kinds → visible
    assert fn("DOC") is True
    assert fn("Combinar") is True
    assert fn("Extractor") is True
    assert fn("property") is True
    # Stratigraphic kinds → hidden
    assert fn("US") is False
    assert fn("USM") is False
    assert fn("USV") is False
    assert fn("SF") is False
    # Edge cases
    assert fn("") is False
    assert fn(None) is False
