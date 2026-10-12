"""Pottery Tools: i modelli di Lorenzo Cardarelli in un registro solo (2026-10-12).

Prima la finestra teneva tre copie della tabella dei modelli di
PyPotteryInk (tendina, download, scelta del file), un percorso personale
(`/Users/enzo/Documents/PyPotteryLens/...`) e scaricava il rilevatore YOLO
dal fork GitHub con `raw/`, che sui file grandi fallisce. Ora c'e'
`modules/utility/pottery_models.py`: una riga per modello, e il nuovo
5h-PAPERGRID di PyPotteryInk 2.1.2 ci sta gia'.
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import pottery_models as pm  # noqa: E402

STORICHE = ["10k Model (General)", "6h-MCG Model (Bronze Age)",
            "6h-MC Model (Protohistoric)", "4h-PAINT Model (Historic/Painted)"]


def test_le_etichette_storiche_restano_e_in_quell_ordine():
    labels = pm.ink_model_labels()
    assert labels[:4] == STORICHE, "le impostazioni salvate usano queste etichette"


def test_il_modello_papergrid_di_pypotteryink_212_e_nel_registro():
    labels = pm.ink_model_labels()
    nuovo = [l for l in labels if "PAPERGRID" in l]
    assert len(nuovo) == 1
    assert pm.ink_model_filename(nuovo[0]) == "5h_PAPERGRID.pkl"     # nome con underscore, come su HF


def test_tutti_gli_indirizzi_puntano_a_hugging_face_lrncrd():
    for label in pm.ink_model_labels():
        url = pm.ink_model_url(label)
        assert url.startswith("https://huggingface.co/lrncrd/PyPotteryInk/resolve/main/")
        assert url.endswith(".pkl?download=true")
    assert pm.YOLO_MODEL_URLS[0].startswith("https://huggingface.co/lrncrd/PyPotteryLens/resolve/main/")
    assert pm.YOLO_MODEL_FILE in pm.YOLO_MODEL_URLS[0]


def test_etichetta_sconosciuta_da_none():
    assert pm.ink_model_filename("boh") is None
    assert pm.ink_model_url("boh") is None
    assert pm.ink_model_path("boh") is None


def test_il_percorso_locale_sta_in_bin_models(tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    path = pm.ink_model_path("10k Model (General)")
    assert path == os.path.join(str(tmp_path), "bin", "models", "model_10k.pkl")


def test_i_nomi_del_rilevatore_includono_quello_storico():
    assert pm.YOLO_MODEL_NAMES == ("BasicModelv8_v01.pt", "pottery_yolo.pt")


def test_le_copie_locali_non_sono_di_una_macchina_sola():
    for cand in pm.local_yolo_candidates():
        assert cand.startswith(os.path.expanduser("~"))
        assert "/Users/enzo" not in cand.replace(os.path.expanduser("~"), "~")


# --- la finestra usa il registro, non copie sue ----------------------------
SORGENTE = (_ROOT / "tabs" / "Pottery_tools.py").read_text(encoding="utf-8")


def test_la_finestra_non_ha_piu_percorsi_personali_ne_tabelle_copiate():
    assert "/Users/enzo" not in SORGENTE
    assert "model_name_map" not in SORGENTE
    assert "huggingface.co/lrncrd/PyPotteryInk" not in SORGENTE, "gli indirizzi stanno nel registro"


def test_la_tendina_dei_modelli_viene_dal_registro():
    tree = ast.parse(SORGENTE)
    chiamate = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute) and n.func.attr == "addItems"
                and isinstance(n.func.value, ast.Attribute)
                and n.func.value.attr == "combo_pottery_ink_model"]
    assert len(chiamate) == 1
    arg = chiamate[0].args[0]
    assert isinstance(arg, ast.Call) and getattr(arg.func, "id", "") == "ink_model_labels"


# --- Rosetta: ogni Python esterno parte con l'architettura nativa --------------
UTILITIES = (_ROOT / "modules" / "utility" / "pottery_utilities.py").read_text(encoding="utf-8")


def test_ogni_python_esterno_di_pottery_tools_passa_da_native_prefix():
    """Il QGIS macOS e' x86_64 sotto Rosetta: senza `arch -arm64` il venv nasce
    x86_64 e pip non trova torch. Nessuna lista `[venv_python, …]` nuda."""
    import re
    pattern = re.compile(r"(?<!native_prefix\(\) \+ )\[\s*(?:self\.)?(?:venv_python|python_exe)\b")
    for name, src in (("Pottery_tools.py", SORGENTE), ("pottery_utilities.py", UTILITIES)):
        righe = [src.count("\n", 0, m.start()) + 1 for m in pattern.finditer(src)]
        assert not righe, f"{name}: Python lanciato senza native_prefix alle righe {righe}"
    assert "native_prefix() + [py, '-m', 'venv'" in SORGENTE
    assert "from ..modules.utility.native_arch import native_prefix" in SORGENTE
    assert "from .native_arch import native_prefix" in UTILITIES
