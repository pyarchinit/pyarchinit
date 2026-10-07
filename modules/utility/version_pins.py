"""Version-pin checks for the dependency installer (pure, no Qt).

An exact pin (``==``) means THAT version: the old installer tolerance
(same major = satisfied) left users on s3dgraphy dev9 while the plugin
required dev40, with the installer itself reporting everything fine —
one-bridge final review, 2026-10-07.
"""
from __future__ import annotations


def pin_satisfied(spec, installed):
    """True when *installed* satisfies the single requirement *spec*.

    Supports the two shapes requirements.txt actually uses: ``name==X``
    (exact, packaging equality) and ``name>=X`` (floor, first clause of
    a range). Anything else — or no installed version — is False for
    ``==`` and True for shapes this checker does not know (the caller
    keeps its own handling for those).
    """
    if "==" in spec:
        required = spec.split("==", 1)[1].strip()
        if not installed:
            return False
        try:
            from packaging.version import Version
            return Version(installed) == Version(required)
        except Exception:
            return str(installed).strip() == required
    if ">=" in spec:
        floor = spec.split(">=", 1)[1].split(",")[0].strip()
        if not installed:
            return False
        try:
            from packaging.version import Version
            return Version(installed) >= Version(floor)
        except Exception:
            def _parts(v):
                out = []
                for piece in str(v).split("."):
                    digits = "".join(c for c in piece if c.isdigit())
                    out.append(int(digits) if digits else 0)
                return tuple(out)
            return _parts(installed) >= _parts(floor)
    return True
