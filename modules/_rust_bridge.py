"""
Bridge module for optional Rust acceleration.

Usage:
    from modules._rust_bridge import rust_bridge

    if rust_bridge.is_available():
        result = rust_bridge.topological_sort_with_levels(edges, reverse_order=True)
    else:
        # fallback to Python implementation
"""


class _RustBridge:
    """Lazy-loading bridge to pyarchinit_core Rust module."""

    def __init__(self):
        self._module = None
        self._checked = False
        self._available = False

    def _load(self):
        if self._checked:
            return
        self._checked = True
        try:
            import pyarchinit_core
            self._module = pyarchinit_core
            self._available = True
        except ImportError:
            self._available = False

    def is_available(self):
        self._load()
        return self._available

    @property
    def version(self):
        self._load()
        if self._available:
            return self._module.__version__
        return None

    # Graph functions
    def topological_sort_with_levels(self, edges, reverse_order=True):
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.graph.topological_sort_with_levels(edges, reverse_order)

    def detect_and_remove_cycles(self, edges):
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.graph.detect_and_remove_cycles(edges)

    def transitive_reduction(self, edges):
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.graph.transitive_reduction(edges)


# Singleton instance
rust_bridge = _RustBridge()
