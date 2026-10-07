"""yE-F import fold tests — _resolve_folder_for_leaf + _write_us_rows
fold branch."""
from __future__ import annotations
from pathlib import Path
from sqlalchemy import text
import pytest

from s3dgraphy.sync._db_handle import DbHandle
from s3dgraphy.sync.yed_classifier import (
    ClassificationKind, ClassifiedNode,
)
from s3dgraphy.sync.yed_group_walker import FolderCandidate


def _folder(yed_id, label, members, dim="attivita"):
    return FolderCandidate(
        yed_id=yed_id, full_label=label,
        auto_dimension=dim, user_dimension=dim,
        auto_value=label.split("-")[0], user_value=label.split("-")[0],
        member_yed_ids=list(members), nested_folder_ids=[],
        parent_folder_id=None,
    )


def test_resolve_folder_for_leaf_returns_attivita_value():
    """Leaf y1 in folder VA01 → returns 'VA01'."""
    from s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "VA01-foundation", members=["y1", "y2"])]
    assert _resolve_folder_for_leaf("y1", folders) == "VA01"
    assert _resolve_folder_for_leaf("y2", folders) == "VA01"


def test_resolve_folder_for_leaf_returns_none_when_orphan():
    """Leaf not in any folder → None."""
    from s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "VA01", members=["y1"])]
    assert _resolve_folder_for_leaf("y_orphan", folders) is None


def test_resolve_folder_for_leaf_skips_non_attivita_dim():
    """Folder with dim='area' is ignored — only attivita matters."""
    from s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "AR05", members=["y1"], dim="area")]
    assert _resolve_folder_for_leaf("y1", folders) is None


_US_TABLE_DDL = """
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, area TEXT, us TEXT,
    unita_tipo TEXT, rapporti TEXT, attivita TEXT,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT,
    d_stratigrafica TEXT, node_uuid TEXT,
    other_locations TEXT,
    UNIQUE (sito, area, us, unita_tipo)
)
"""


def _make_yef_handle(tmp_path):
    dbfile = tmp_path / "yef_fold.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        conn.execute(text(_US_TABLE_DDL))
    return handle


def _leaf(yed_id, kind, label=None):
    return ClassifiedNode(
        yed_id=yed_id, label=label or yed_id,
        auto_kind=kind, user_kind=kind,
    )


def test_write_us_rows_yef_fold_first_occurrence_primary(tmp_path):
    """3 'material' leaves in folders VA01/VA04/VA05 → 1 us_table row
    with attivita='VA01' (first folder) + other_locations=['VA04','VA05'].
    """
    from s3dgraphy.sync.yed_import_pipeline import _write_us_rows
    handle = _make_yef_handle(tmp_path)
    leaves = [
        _leaf("m1", ClassificationKind.PROPERTY, "material"),
        _leaf("m2", ClassificationKind.PROPERTY, "material"),
        _leaf("m3", ClassificationKind.PROPERTY, "material"),
    ]
    folders = [
        _folder("F1", "VA01", members=["m1"]),
        _folder("F4", "VA04", members=["m2"]),
        _folder("F5", "VA05", members=["m3"]),
    ]

    with handle.engine.begin() as conn:
        count, uuid_map = _write_us_rows(
            conn, leaves, sito="X", folders_map={f.yed_id: f for f in folders},
        )

    assert count == 1, f"expected 1 INSERT, got {count}"
    with handle.engine.connect() as conn:
        rows = list(conn.execute(text(
            "SELECT us, unita_tipo, attivita, other_locations, "
            "d_stratigrafica FROM us_table WHERE sito = 'X'"
        )))
    assert len(rows) == 1
    us, ut, attivita, ol, d_strat = rows[0]
    assert us == "material"
    assert ut == "property"
    assert attivita == "VA01"
    import json
    secondary = json.loads(ol) if ol else []
    assert secondary == ["VA04", "VA05"]
    assert d_strat == "material"
    assert len(set(uuid_map.values())) == 1


def test_write_us_rows_yef_idempotent_on_re_run(tmp_path):
    """Second run of the same drafts → 0 new inserts, other_locations unchanged."""
    from s3dgraphy.sync.yed_import_pipeline import _write_us_rows
    handle = _make_yef_handle(tmp_path)
    leaves = [
        _leaf("m1", ClassificationKind.PROPERTY, "material"),
        _leaf("m2", ClassificationKind.PROPERTY, "material"),
    ]
    folders = [
        _folder("F1", "VA01", members=["m1"]),
        _folder("F4", "VA04", members=["m2"]),
    ]
    folders_map = {f.yed_id: f for f in folders}

    with handle.engine.begin() as conn:
        count1, _ = _write_us_rows(conn, leaves, sito="X", folders_map=folders_map)
    assert count1 == 1

    with handle.engine.begin() as conn:
        count2, uuid_map2 = _write_us_rows(conn, leaves, sito="X", folders_map=folders_map)
    assert count2 == 0, f"expected 0 inserts on re-run, got {count2}"

    with handle.engine.connect() as conn:
        rows = list(conn.execute(text(
            "SELECT us, attivita, other_locations FROM us_table WHERE sito = 'X'"
        )))
    assert len(rows) == 1
    us, attivita, ol = rows[0]
    assert us == "material"
    assert attivita == "VA01"
    import json
    assert json.loads(ol) == ["VA04"]


def test_write_us_rows_yef_appends_new_folder_on_re_import(tmp_path):
    """Second run with an EXTRA folder occurrence appends to other_locations."""
    from s3dgraphy.sync.yed_import_pipeline import _write_us_rows
    handle = _make_yef_handle(tmp_path)

    leaves_1 = [
        _leaf("m1", ClassificationKind.PROPERTY, "material"),
        _leaf("m2", ClassificationKind.PROPERTY, "material"),
    ]
    folders_1 = {
        "F1": _folder("F1", "VA01", members=["m1"]),
        "F4": _folder("F4", "VA04", members=["m2"]),
    }
    with handle.engine.begin() as conn:
        _write_us_rows(conn, leaves_1, sito="X", folders_map=folders_1)

    leaves_2 = leaves_1 + [_leaf("m3", ClassificationKind.PROPERTY, "material")]
    folders_2 = {**folders_1, "F6": _folder("F6", "VA06", members=["m3"])}
    with handle.engine.begin() as conn:
        _write_us_rows(conn, leaves_2, sito="X", folders_map=folders_2)

    with handle.engine.connect() as conn:
        ol_row = conn.execute(text(
            "SELECT other_locations FROM us_table WHERE sito = 'X' AND us = 'material'"
        )).first()
    import json
    assert json.loads(ol_row[0]) == ["VA04", "VA06"]


def test_apply_yed_folder_dimensions_skips_paradata_attivita(tmp_path):
    """Regression — yE-F primary attivita must NOT be overwritten by
    ``_apply_yed_folder_dimensions`` for paradata fold rows.

    Pre-fix bug: for paradata multi-folder rows (e.g. DOC.01 appearing
    in folders VA02/VA04/VA05), ``_write_us_rows`` correctly set
    ``attivita=VA02`` (first in document order) + ``other_locations=
    ['VA04','VA05']``. But ``_apply_yed_folder_dimensions`` then
    iterated folders VA02/VA04/VA05 and ran one UPDATE per folder on
    the shared node_uuid, with the LAST iteration winning — so
    ``attivita`` ended up as VA05. Worse, the primary ended up
    duplicated in ``other_locations`` on subsequent re-imports.

    Fix: skip paradata node_uuids when ``dim=='attivita'``; yE-F has
    already written the correct value during fold INSERT.
    """
    from s3dgraphy.sync.yed_import_pipeline import (
        _write_us_rows, _apply_yed_folder_dimensions,
    )
    handle = _make_yef_handle(tmp_path)
    leaves = [
        _leaf("d1", ClassificationKind.DOCUMENT, "D.01"),
        _leaf("d2", ClassificationKind.DOCUMENT, "D.01"),
        _leaf("d3", ClassificationKind.DOCUMENT, "D.01"),
    ]
    folders = [
        _folder("F2", "VA02", members=["d1"]),
        _folder("F4", "VA04", members=["d2"]),
        _folder("F5", "VA05", members=["d3"]),
    ]
    folders_map = {f.yed_id: f for f in folders}

    with handle.engine.begin() as conn:
        _, uuid_map = _write_us_rows(
            conn, leaves, sito="X", folders_map=folders_map,
        )

    # Simulate the rest of the pipeline that calls
    # _apply_yed_folder_dimensions AFTER _write_us_rows.
    with handle.engine.begin() as conn:
        _apply_yed_folder_dimensions(conn, folders, "X", uuid_map)

    with handle.engine.connect() as conn:
        rows = list(conn.execute(text(
            "SELECT us, attivita, other_locations FROM us_table "
            "WHERE sito = 'X' AND unita_tipo = 'DOC'"
        )))
    assert len(rows) == 1, "yE-F should fold 3 D.01 occurrences to 1 row"
    us, attivita, ol = rows[0]
    assert us == "01"
    # Primary must be the FIRST folder in document order, NOT the last.
    assert attivita == "VA02", (
        f"attivita should stay 'VA02' (first folder) but got {attivita!r} "
        f"— _apply_yed_folder_dimensions overwrote yE-F primary"
    )
    import json
    secondary = json.loads(ol) if ol else []
    assert secondary == ["VA04", "VA05"], (
        f"other_locations should be ['VA04','VA05'] but got {secondary!r}"
    )
    # Critical: primary must NOT appear in other_locations.
    assert attivita not in secondary, (
        f"primary {attivita!r} duplicated in other_locations {secondary!r}"
    )
