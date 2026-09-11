"""The style chosen for the US / USM layers must not be overwritten (2026-09-11).

"Visualizza su GIS" from a US search asks how to style the layer (save /
load / temporary / outline only) and which field to categorise by
(stratigraphic definition, US type, interpretive definition). On SQLite
charge_vector_layers then called create_us_nested_symbology(), which
replaced that renderer with one rule per US: the map always came out "by
US number" whatever the user chose. charge_usm_layers on SQLite never asked
at all. PostgreSQL did it right: the styler only. Pure Python (ast).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[2] / "modules" / "gis" / "pyarchinit_pyqgis.py"


def _calls(function_name):
    tree = ast.parse(_SRC.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == function_name)
    return [n.func.attr for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]


@pytest.mark.parametrize("loader", ["charge_vector_layers", "charge_usm_layers"])
def test_the_user_style_is_applied_on_sqlite_and_postgres(loader):
    assert _calls(loader).count("apply_style_to_layer") >= 2, (
        f"{loader}: the style choice must be offered on both SQLite and PostgreSQL")


@pytest.mark.parametrize("loader", ["charge_vector_layers", "charge_usm_layers"])
def test_the_chosen_style_is_not_replaced_by_the_per_us_symbology(loader):
    assert "create_us_nested_symbology" not in _calls(loader), (
        f"{loader}: create_us_nested_symbology() would overwrite the style the user chose")


@pytest.mark.parametrize("source", [_SRC, _SRC.parents[1] / "utility" / "create_style.py"])
def test_the_drawing_order_is_set_on_the_renderer(source):
    # QgsVectorLayer has no setOrderBy(): the call raised AttributeError,
    # swallowed by an except, and no drawing order was ever applied
    import re
    assert not re.search(r"\blayer\w*\.setOrderBy(Enabled)?\(", source.read_text(encoding="utf-8")), source.name
