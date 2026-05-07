"""Qt-aware VocabProvider — wraps VocabProviderCore with a vocabulary_changed
signal and a QFileSystemWatcher for hot-reload of overrides.

This module imports PyQt symbols, so it should NOT be imported from
non-Qt contexts. Use VocabProviderCore directly for tests and CLI tools.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from qgis.PyQt.QtCore import QFileSystemWatcher, QObject, pyqtSignal
    _HAS_QT = True
except ImportError:  # pragma: no cover (only when QGIS not available)
    _HAS_QT = False
    QObject = object  # type: ignore[assignment,misc]

from .vocab_provider_core import VocabProviderCore


def _default_bundled_dir() -> Path:
    """Locate the bundled JSON_config/ inside ext_libs/s3dgraphy/."""
    here = Path(__file__).resolve()
    plugin_root = here.parents[3]
    return plugin_root / "ext_libs" / "s3dgraphy" / "JSON_config"


def _default_overrides_dir() -> Path:
    """User-writable overrides location."""
    return Path(os.path.expanduser("~/.config/pyarchinit/vocab_overrides"))


class VocabProvider(QObject if _HAS_QT else object):  # type: ignore[misc]
    """Process-wide vocabulary provider with hot-reload."""

    if _HAS_QT:
        vocabulary_changed = pyqtSignal(str)  # 'nodes' | 'connections' | 'visual_rules'

    def __init__(self,
                 bundled_dir: Path | None = None,
                 overrides_dir: Path | None = None,
                 parent=None):
        if _HAS_QT:
            super().__init__(parent)
        bundled = bundled_dir or _default_bundled_dir()
        overrides = overrides_dir or _default_overrides_dir()
        overrides.mkdir(parents=True, exist_ok=True)
        self._core = VocabProviderCore(bundled_dir=bundled, overrides_dir=overrides)
        if _HAS_QT:
            self._watcher = QFileSystemWatcher(self)
            for d in (bundled, overrides):
                if d.is_dir():
                    self._watcher.addPath(str(d))
            self._watcher.directoryChanged.connect(self._on_directory_changed)

    def _on_directory_changed(self, path: str) -> None:
        self._core.reload()
        if _HAS_QT:
            # We don't know which file changed; emit for all three for now.
            for which in ("nodes", "connections", "visual_rules"):
                self.vocabulary_changed.emit(which)

    # Delegations
    def get_unit_types(self, *args, **kwargs):
        return self._core.get_unit_types(*args, **kwargs)

    def get_edge_types(self):
        return self._core.get_edge_types()

    def get_legal_targets_for(self, source_type: str, edge_name: str):
        return self._core.get_legal_targets_for(source_type, edge_name)

    def get_paradata_types(self):
        return self._core.get_paradata_types()

    def get_visual_rule(self, node_type: str):
        return self._core.get_visual_rule(node_type)

    def get_cidoc_mapping(self, type_abbreviation: str):
        return self._core.get_cidoc_mapping(type_abbreviation)

    @property
    def versions(self):
        return self._core.versions


_DEFAULT_PROVIDER: VocabProvider | None = None


def get_default_provider() -> VocabProvider:
    global _DEFAULT_PROVIDER
    if _DEFAULT_PROVIDER is None:
        _DEFAULT_PROVIDER = VocabProvider()
    return _DEFAULT_PROVIDER
