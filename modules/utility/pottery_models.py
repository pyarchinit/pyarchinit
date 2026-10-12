# -*- coding: utf-8 -*-
"""I modelli di Pottery Tools, in un posto solo.

Pottery Tools usa i modelli pubblicati da Lorenzo Cardarelli (lrncrd) per la
suite PyPottery: i modelli di inchiostrazione di **PyPotteryInk** e il
rilevatore YOLO di **PyPotteryLens**. Gli indirizzi stanno qui, e non sparsi
nella finestra, cosi' quando a monte esce un modello nuovo si aggiunge una
riga e la tendina, lo scaricamento e la scelta del file seguono da sole.

Fonte dei modelli (verificata il 2026-10-12):
- https://huggingface.co/lrncrd/PyPotteryInk  (model_10k, 6h-MCG, 6h-MC,
  4h-PAINT, 5h_PAPERGRID — ~38 MB l'uno)
- https://huggingface.co/lrncrd/PyPotteryLens (BasicModelv8_v01.pt, il
  rilevatore YOLOv8 dei disegni; model_classifier.pth, il classificatore
  ENT/FRAG che qui non si usa)
"""
from __future__ import annotations

import os

from .pyarchinit_home import pyarchinit_home_bin

#: Repository Hugging Face dei modelli (download diretto, senza token).
INK_REPO = "https://huggingface.co/lrncrd/PyPotteryInk/resolve/main/"
LENS_REPO = "https://huggingface.co/lrncrd/PyPotteryLens/resolve/main/"

#: Etichetta nella tendina -> (nome file, descrizione breve).
#: L'ordine e' quello della tabella «Available Models» del README di
#: PyPotteryInk 2.1.2; le prime quattro etichette sono quelle storiche di
#: Pottery Tools e non vanno cambiate (le impostazioni salvate le usano).
POTTERY_INK_MODELS = {
    "10k Model (General)": ("model_10k.pkl", "General-purpose model for pottery drawings"),
    "6h-MCG Model (Bronze Age)": ("6h-MCG.pkl", "High-quality model for Bronze Age drawings"),
    "6h-MC Model (Protohistoric)": ("6h-MC.pkl", "High-quality model for Protohistoric and Historic drawings"),
    "4h-PAINT Model (Historic/Painted)": ("4h-PAINT.pkl", "Tailored model for Historic and painted pottery"),
    "5h-PAPERGRID Model (Paper grid tables)": ("5h_PAPERGRID.pkl",
                                              "Tailored model for paper grid tables (no shadows)"),
}

#: Il rilevatore dei disegni (YOLOv8) di PyPotteryLens.
YOLO_MODEL_FILE = "BasicModelv8_v01.pt"
#: Dove provare a scaricarlo, nell'ordine: Hugging Face (ufficiale, stabile),
#: poi il fork GitHub di enzococca (raw, puo' fallire sui file grandi).
YOLO_MODEL_URLS = (
    LENS_REPO + YOLO_MODEL_FILE + "?download=true",
    "https://github.com/enzococca/PyPotteryLens/raw/main/models_vision/" + YOLO_MODEL_FILE,
)
#: Nomi accettati per il rilevatore gia' presente in bin/ (il secondo e'
#: il nome storico di Pottery Tools).
YOLO_MODEL_NAMES = (YOLO_MODEL_FILE, "pottery_yolo.pt")


def ink_model_labels():
    """Le etichette per la tendina, nell'ordine del registro."""
    return list(POTTERY_INK_MODELS)


def ink_model_filename(label):
    """Nome del file .pkl per un'etichetta (None se sconosciuta)."""
    entry = POTTERY_INK_MODELS.get(label)
    return entry[0] if entry else None


def ink_model_url(label):
    """Indirizzo di download per un'etichetta (None se sconosciuta)."""
    filename = ink_model_filename(label)
    return INK_REPO + filename + "?download=true" if filename else None


def ink_models_dir():
    """Cartella dei modelli di inchiostrazione: <home>/bin/models."""
    return os.path.join(pyarchinit_home_bin(), "models")


def ink_model_path(label):
    """Percorso locale del modello per un'etichetta (None se sconosciuta)."""
    filename = ink_model_filename(label)
    return os.path.join(ink_models_dir(), filename) if filename else None


def local_yolo_candidates():
    """Copie locali del rilevatore da cui copiare prima di scaricare."""
    home = os.path.expanduser("~")
    return [
        os.path.join(home, "Documents", "PyPotteryLens", "models_vision", YOLO_MODEL_FILE),
        os.path.join(home, "PyPotteryLens", "models_vision", YOLO_MODEL_FILE),
    ]
