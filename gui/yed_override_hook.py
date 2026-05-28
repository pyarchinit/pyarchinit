"""yEd-raw override hook implementation (Qt/QGIS-aware).

Registered into ``modules.s3dgraphy.sync.graph_ingestor`` at plugin
``initGui`` time via ``register_yed_override_hook``. Keeps Qt + the
``YedImportDialog`` out of the core ``graph_ingestor`` module so the
latter stays portable into the s3dgraphy package proper (issue #10).

Behavior is identical to the legacy inline block (yE-E, 5.8.2-alpha):
- If no QApplication is alive (CLI / tests / headless), return defaults
  (no overrides, FolderEdgePolicy.SKIP, not cancelled).
- Otherwise open YedImportDialog. If the user cancels, return
  cancelled=True. On accept, return user's overrides + policy.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.s3dgraphy.sync.graph_ingestor import YedOverrideResult
from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy


def yed_override_hook(
    drafts: dict,
    graphml_path: Path,
    handle: Any,
    sito: str,
) -> YedOverrideResult:
    """Open YedImportDialog when a Qt event loop is available."""
    from qgis.PyQt.QtWidgets import QApplication
    if QApplication.instance() is None:
        return YedOverrideResult(
            overrides=None,
            policy=FolderEdgePolicy.SKIP,
            cancelled=False,
        )

    from pyarchinit.gui.yed_import_dialog import YedImportDialog
    dlg = YedImportDialog(drafts, graphml_path, handle, sito)
    if dlg.exec() != dlg.DialogCode.Accepted:
        return YedOverrideResult(
            overrides=None,
            policy=FolderEdgePolicy.SKIP,
            cancelled=True,
        )
    return YedOverrideResult(
        overrides=dlg.get_overrides(),
        policy=dlg.get_policy(),
        cancelled=False,
    )
