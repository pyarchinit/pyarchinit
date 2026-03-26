"""Optional Rust acceleration helpers.
Falls back to pure Python if Rust module not available."""

try:
    import pyarchinit_core as _rust
    HAS_RUST = True
except ImportError:
    HAS_RUST = False

import ast


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
