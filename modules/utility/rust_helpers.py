"""Optional Rust acceleration helpers.
Falls back to pure Python if Rust module not available.

The Rust module (pyarchinit_core) is pre-compiled for:
  - Linux x86_64:       pyarchinit_core.abi3.so
  - macOS Intel:        pyarchinit_core.abi3.so
  - macOS Apple Silicon: pyarchinit_core.abi3.so
  - Windows x86_64:     pyarchinit_core.pyd

The module is loaded automatically from the plugin directory.
If not found, all functions fall back to pure Python transparently.
"""

import ast
import os
import sys
import platform

def _load_rust_module():
    """Try to load the Rust module, handling platform-specific binary names."""
    # First try direct import (if installed via pip or in sys.path)
    try:
        import pyarchinit_core
        return pyarchinit_core
    except ImportError:
        pass

    # Try to find platform-specific binary in _rust_binaries/ or plugin root
    plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    binaries_dir = os.path.join(plugin_dir, '_rust_binaries')

    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map platform to binary filename
    candidates = []
    if system == 'linux':
        candidates = [
            os.path.join(plugin_dir, 'pyarchinit_core.abi3.so'),
            os.path.join(binaries_dir, 'pyarchinit_core.linux-x86_64.so'),
        ]
    elif system == 'darwin':
        if machine == 'arm64':
            candidates = [
                os.path.join(plugin_dir, 'pyarchinit_core.abi3.so'),
                os.path.join(binaries_dir, 'pyarchinit_core.macos-arm64.so'),
                os.path.join(binaries_dir, 'pyarchinit_core.macos-arm64.dylib'),
            ]
        else:
            candidates = [
                os.path.join(plugin_dir, 'pyarchinit_core.abi3.so'),
                os.path.join(binaries_dir, 'pyarchinit_core.macos-x86_64.so'),
                os.path.join(binaries_dir, 'pyarchinit_core.macos-x86_64.dylib'),
            ]
    elif system == 'windows':
        candidates = [
            os.path.join(plugin_dir, 'pyarchinit_core.pyd'),
            os.path.join(binaries_dir, 'pyarchinit_core.windows-x86_64.pyd'),
        ]

    for path in candidates:
        if os.path.exists(path):
            try:
                # Add directory to sys.path temporarily
                dir_path = os.path.dirname(path)
                if dir_path not in sys.path:
                    sys.path.insert(0, dir_path)
                import pyarchinit_core
                return pyarchinit_core
            except ImportError:
                continue

    return None

_rust = _load_rust_module()
HAS_RUST = _rust is not None


def parse_rapporti(rapporti_str):
    """Parse rapporti field - uses Rust if available, else ast.literal_eval."""
    if not rapporti_str or rapporti_str in ('[]', '[[]]', ''):
        return []
    if HAS_RUST:
        try:
            return _rust.parse_rapporti_fast(rapporti_str)
        except Exception:
            pass
    # Fallback to Python
    try:
        return ast.literal_eval(rapporti_str)
    except Exception:
        return []


def compute_style_categories(d_stratigrafica_list):
    """Compute style categories - uses Rust if available."""
    if HAS_RUST:
        try:
            return _rust.compute_style_categories(d_stratigrafica_list)
        except Exception:
            pass
    # Fallback: Python implementation
    result = {}
    for cat in set(d_stratigrafica_list):
        if cat:
            h = hash(str(cat))
            result[cat] = (abs(h) % 200 + 40, abs(h >> 8) % 200 + 40, abs(h >> 16) % 200 + 40)
    return result


def is_rust_available():
    """Check if the Rust acceleration module is available."""
    return HAS_RUST
