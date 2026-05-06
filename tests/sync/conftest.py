"""Shared pytest fixtures for tests/sync/."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def node_datamodel_path() -> Path:
    return FIXTURES / "node_datamodel_sample.json"


@pytest.fixture
def connections_datamodel_path() -> Path:
    return FIXTURES / "connections_datamodel_sample.json"


@pytest.fixture
def visual_rules_path() -> Path:
    return FIXTURES / "em_visual_rules_sample.json"


@pytest.fixture
def vocab_dir(tmp_path: Path,
              node_datamodel_path: Path,
              connections_datamodel_path: Path,
              visual_rules_path: Path) -> Path:
    """Create an isolated JSON_config/ directory holding sample fixtures."""
    out = tmp_path / "JSON_config"
    out.mkdir()
    (out / "s3Dgraphy_node_datamodel.json").write_bytes(node_datamodel_path.read_bytes())
    (out / "s3Dgraphy_connections_datamodel.json").write_bytes(connections_datamodel_path.read_bytes())
    (out / "em_visual_rules.json").write_bytes(visual_rules_path.read_bytes())
    return out


@pytest.fixture
def overrides_dir(tmp_path: Path) -> Path:
    out = tmp_path / "vocab_overrides"
    out.mkdir()
    return out
