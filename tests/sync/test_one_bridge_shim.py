"""One bridge (A1): the shared modules come from the library.

The ten modules measured identical on 2026-10-07 are deleted from the
vendored package; a transitional alias keeps the old import path alive
until A5 rewires the callers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(_ROOT), str(_ROOT / "ext_libs")):
    if entry not in sys.path:
        sys.path.append(entry)

pytest.importorskip("s3dgraphy.sync")

FREE_WINS = ("yed_group_walker", "yed_detector", "vocab_types",
             "vocab_provider_core", "uuid7", "ingest_result",
             "group_store", "conflict_resolver",
             "_legacy_paradata_svgs", "_db_handle")

# A1, second wave: small drift reconciled hunk by hunk — every delta was a
# library-side improvement (reST docstrings, the coating kind of 1.6.13,
# invalidate_indices, JSON_config resolved inside the package).
RECONCILED = ("yed_rapporti_policy", "yed_classifier", "yed_import_pipeline",
              "paradata_store", "edge_registry", "group_projector",
              "yed_table_parser",
              # third wave: mappings and workspace resolved inside the
              # library (host mirrors PYARCHINIT_WORKSPACE_DIR), rapporti
              # on the canonical spellings (equals / bonded_to).
              "pyarchinit_pg_importer", "rapporti", "_workspace")


def test_the_identical_modules_are_gone_from_the_vendored_package():
    for name in FREE_WINS + RECONCILED:
        assert not (_ROOT / "modules" / "s3dgraphy" / "sync" / (name + ".py")).exists(), name


def test_the_library_modules_come_from_ext_libs():
    # A5 superseded A1's alias: the old import path is gone (guard
    # below); here we pin that the library modules really are the
    # installed ones, not some stray copy.
    import importlib
    for name in FREE_WINS + RECONCILED:
        mod = "s3dgraphy.rapporti" if name == "rapporti" else (
            "s3dgraphy.sync." + name)
        libs = importlib.import_module(mod)
        assert "ext_libs" in str(Path(libs.__file__).resolve()), name


def test_the_old_import_path_is_dead():
    import importlib
    for name in FREE_WINS + RECONCILED:
        try:
            importlib.import_module("modules.s3dgraphy.sync." + name)
        except ImportError:
            continue
        raise AssertionError(
            "modules.s3dgraphy.sync.%s still importable (alias back?)" % name)


def test_the_graphml_writer_is_gone():
    """A4 (spec 2026-10-07, decision 2): the writer retired with B1
    shipped — em.json is the working format, EMStudio the viewer; the
    one-time yEd import and the classic DOT matrix stay."""
    assert not (_ROOT / "modules" / "s3dgraphy" / "sync"
                / "graphml_writer.py").exists()
    for probe in ("tabs", "modules", "gui"):
        for path in (_ROOT / probe).rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "graphml_writer" not in text, path


# A5: every migrated module is imported from the library, nowhere else.
# graph_projector and graph_ingestor are NOT here: they stayed vendored
# (the wrapper and the pyArchInit-only ingestor — see the A2/A3 rulings).
MIGRATED = FREE_WINS + RECONCILED


def test_no_plugin_file_imports_the_vendored_path_for_migrated_modules():
    offenders = []
    for probe in ("tabs", "modules", "gui"):
        for path in (_ROOT / probe).rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for name in MIGRATED:
                if "modules.s3dgraphy.sync.%s" % name in text or \
                   "from modules.s3dgraphy.sync import %s" % name in text:
                    offenders.append("%s -> %s" % (path.relative_to(_ROOT), name))
    assert not offenders, offenders


def test_the_transitional_alias_is_gone():
    init = (_ROOT / "modules" / "s3dgraphy" / "sync"
            / "__init__.py").read_text(encoding="utf-8")
    assert "_sys.modules" not in init


def test_no_relative_import_reaches_a_migrated_or_deleted_module():
    """Final review (2026-10-07): the A5 guard missed the RELATIVE form —
    `.sync.group_projector` inside modules/s3dgraphy always failed into
    an except, and the export dialog still offered the retired GraphML."""
    relative_forms = tuple(".sync.%s" % n for n in MIGRATED + (
        "graphml_writer",))
    offenders = []
    for probe in ("tabs", "modules", "gui"):
        for path in (_ROOT / probe).rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for form in relative_forms:
                if ("from %s import" % form) in text or \
                   ("import %s" % form) in text:
                    offenders.append("%s -> %s" % (path.relative_to(_ROOT), form))
    assert not offenders, offenders


def test_the_export_dialog_no_longer_offers_graphml():
    src = (_ROOT / "modules" / "s3dgraphy"
           / "s3dgraphy_dot_bridge.py").read_text(encoding="utf-8")
    assert "cb_graphml" not in src
    assert "GraphML Format" not in src


def test_no_dead_relative_attempt_at_a_library_module():
    """The A5 mechanical rename turned `.modules.s3dgraphy.sync.X` into
    `.s3dgraphy.sync.X` / `..s3dgraphy.sync.X` — paths that do not exist
    under the pyarchinit package, so the try branch ALWAYS fails into
    its except. Library modules are imported absolutely, full stop."""
    offenders = []
    probes = [(_ROOT / "pyarchinitPlugin.py",)] + [
        tuple((_ROOT / d).rglob("*.py")) for d in ("tabs", "modules", "gui")]
    for group in probes:
        for path in group:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for form in ("from .s3dgraphy.", "from ..s3dgraphy."):
                if form in text:
                    offenders.append("%s -> %s" % (path.relative_to(_ROOT), form))
    assert not offenders, offenders
