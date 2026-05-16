"""yE-F import fold tests — _resolve_folder_for_leaf + _write_us_rows
fold branch."""
from __future__ import annotations
from pathlib import Path
from sqlalchemy import text
import pytest

from modules.s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync.yed_classifier import (
    ClassificationKind, ClassifiedNode,
)
from modules.s3dgraphy.sync.yed_group_walker import FolderCandidate


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
    from modules.s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "VA01-foundation", members=["y1", "y2"])]
    assert _resolve_folder_for_leaf("y1", folders) == "VA01"
    assert _resolve_folder_for_leaf("y2", folders) == "VA01"


def test_resolve_folder_for_leaf_returns_none_when_orphan():
    """Leaf not in any folder → None."""
    from modules.s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "VA01", members=["y1"])]
    assert _resolve_folder_for_leaf("y_orphan", folders) is None


def test_resolve_folder_for_leaf_skips_non_attivita_dim():
    """Folder with dim='area' is ignored — only attivita matters."""
    from modules.s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "AR05", members=["y1"], dim="area")]
    assert _resolve_folder_for_leaf("y1", folders) is None
