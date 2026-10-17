"""La scena 3D dei proxy nell'HTML della narrativa (Enzo, 17 ottobre 2026:
«assemblare insieme tutti i 3D … se ci clicco sopra si evidenzia il proxy
interessato e gli altri sono in trasparenza»)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "ext_libs")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_PACCHETTO = _ROOT / "resources" / "js" / "pya_three_scene.min.js"


def test_il_pacchetto_three_e_quello_fissato():
    testo = _PACCHETTO.read_text(encoding="utf-8")
    assert testo.startswith("/*! three.js 0.186.1 (MIT")
    assert "PYA_THREE" in testo and "GLTFLoader" in testo and "OrbitControls" in testo
    assert 300_000 < len(testo.encode("utf-8")) < 1_500_000
    assert (_PACCHETTO.parent / "THREE_LICENSE.txt").read_text(encoding="utf-8").startswith("The MIT License")


@pytest.mark.skipif(shutil.which("node") is None, reason="node non c'è")
def test_il_pacchetto_si_legge():
    subprocess.run(["node", "--check", str(_PACCHETTO)], check=True)
