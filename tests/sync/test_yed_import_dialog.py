"""yE-E (5.8.2-alpha) sidecar JSON tests for gui/yed_import_dialog.

These tests exercise the pure-function persistence helpers
(``save_sidecar``, ``load_sidecar``, ``sidecar_path``) without
touching Qt. The QWizard / QWizardPage classes are gated by
``_QT_AVAILABLE`` and only resolve when a QApplication is present —
the test suite cannot create one headlessly, so dialog behaviour is
covered by the manual QGIS gate in Group D.
"""
from __future__ import annotations

import json
from pathlib import Path

from gui.yed_import_dialog import (
    load_sidecar,
    save_sidecar,
    sidecar_path,
)
from modules.s3dgraphy.sync.yed_classifier import ClassificationKind
from modules.s3dgraphy.sync.yed_import_pipeline import YedOverrides
from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy


def test_sidecar_path_appends_suffix(tmp_path: Path) -> None:
    """sidecar_path('foo.graphml') -> 'foo.graphml.yed_overrides.json'."""
    g = tmp_path / "demo.graphml"
    assert sidecar_path(g) == tmp_path / "demo.graphml.yed_overrides.json"


def test_sidecar_json_round_trip(tmp_path: Path) -> None:
    """A YedOverrides serialised + reloaded equals the original
    (modulo enum value comparisons)."""
    g = tmp_path / "demo.graphml"
    g.write_text("<graphml/>")  # placeholder; content not parsed here

    ov = YedOverrides(
        classifier={
            "n0::n0::n0": ClassificationKind.US_REAL,
            "n0::n0::n1": ClassificationKind.USV_VIRTUAL,
            "n0::n1::n0": ClassificationKind.REUSED_SPECIAL_FIND,
        },
        periods={"p0": {"periodo": 5, "fase": 7}},
        folders={"f0": {"dimension": "struttura", "value": "S01"}},
        policy=FolderEdgePolicy.FAN_OUT,
    )
    saved = save_sidecar(g, ov)
    assert saved.exists()

    # Inspect the on-disk JSON: top-level keys + version.
    payload = json.loads(saved.read_text())
    assert payload["version"] == 1
    assert "saved_at" in payload
    assert payload["policy"] == "fan_out"
    assert payload["classifier"]["n0::n0::n0"] == "us_real"
    assert payload["folders"]["f0"]["dimension"] == "struttura"

    # Reload and compare back to ov.
    loaded = load_sidecar(g)
    assert loaded.classifier == ov.classifier
    assert loaded.periods == ov.periods
    assert loaded.folders == ov.folders
    assert loaded.policy == FolderEdgePolicy.FAN_OUT


def test_sidecar_load_missing_returns_empty(tmp_path: Path) -> None:
    """No sidecar present -> empty YedOverrides() (not an error)."""
    g = tmp_path / "no_sidecar.graphml"
    g.write_text("<graphml/>")
    loaded = load_sidecar(g)
    assert loaded == YedOverrides()


def test_sidecar_load_corrupt_returns_empty_plus_warning(
    tmp_path: Path, caplog,
) -> None:
    """Malformed JSON sidecar -> empty YedOverrides + log warning,
    NO exception."""
    g = tmp_path / "bad.graphml"
    g.write_text("<graphml/>")
    target = sidecar_path(g)
    target.write_text("{ not json")
    import logging
    with caplog.at_level(logging.WARNING):
        loaded = load_sidecar(g)
    assert loaded == YedOverrides()
    assert any("sidecar load failed" in r.message for r in caplog.records)


def test_sidecar_load_unknown_kind_skipped(tmp_path: Path) -> None:
    """Forward-compat: an unknown ClassificationKind value in the
    sidecar JSON (e.g. from a future s3dgraphy release) is silently
    skipped, the rest of the classifier dict loads cleanly."""
    g = tmp_path / "future.graphml"
    g.write_text("<graphml/>")
    target = sidecar_path(g)
    target.write_text(json.dumps({
        "version": 1,
        "saved_at": "2026-05-13T00:00:00+00:00",
        "graphml_path": str(g.resolve()),
        "classifier": {
            "n0": "us_real",
            "n1": "future_kind_not_yet_in_enum",
        },
        "periods": {},
        "folders": {},
        "policy": None,
    }))
    loaded = load_sidecar(g)
    assert loaded.classifier == {"n0": ClassificationKind.US_REAL}
