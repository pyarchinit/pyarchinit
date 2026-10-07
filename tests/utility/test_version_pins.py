"""An exact pin means THAT version (C2, one-bridge final review 2026-10-07).

check_required_packages treated `s3dgraphy==1.6.0.dev40` as satisfied by
an installed 1.6.0.dev9 (same major): users upgrading the plugin never
received dev40 and the whole bridge broke with no recovery path — the
installer itself said everything was fine.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.version_pins import pin_satisfied  # noqa: E402


def test_an_exact_pin_rejects_any_other_version():
    assert pin_satisfied("s3dgraphy==1.6.0.dev40", "1.6.0.dev40") is True
    assert pin_satisfied("s3dgraphy==1.6.0.dev40", "1.6.0.dev9") is False
    assert pin_satisfied("s3dgraphy==1.6.0.dev40", "1.6.0") is False
    assert pin_satisfied("s3dgraphy==1.6.0.dev40", None) is False


def test_an_exact_pin_tolerates_spelling_variants_of_the_same_version():
    # packaging equality, not string equality: 1.6.0.dev40 == 1.6.0.DEV40
    assert pin_satisfied("s3dgraphy==1.6.0.dev40", "1.6.0.DEV40") is True


def test_a_floor_pin_checks_the_floor():
    assert pin_satisfied("dtcstamp>=0.1.4", "0.1.4") is True
    assert pin_satisfied("dtcstamp>=0.1.4", "0.2.0") is True
    assert pin_satisfied("dtcstamp>=0.1.4", "0.1.3") is False


def test_the_installer_uses_the_exact_comparison():
    """Source guard: the `==` branch of check_required_packages delegates
    to pin_satisfied — the old major-only tolerance must be gone."""
    src = (_ROOT / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r"elif '==' in line:(.*?)elif '>=' in line:", src, re.S)
    assert m, "the == branch of check_required_packages has moved"
    assert "pin_satisfied" in m.group(1)
    assert "req_major" not in m.group(1), "major-only tolerance is back"
