#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiornare le traduzioni - compatibile con Qt5 e Qt6

Uso:
    python scripts/update_translations.py [--qt6]

Con --qt6 usa pylupdate6 (nuova sintassi)
Senza flag usa pylupdate5 (vecchia sintassi con .pro)
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

# Directory del plugin
PLUGIN_DIR = Path(__file__).parent.parent
I18N_DIR = PLUGIN_DIR / "i18n"

# Lingue supportate
LANGUAGES = ["it_IT", "de_DE", "en_US", "fr_FR", "ar_LB", "es_ES", "ca_ES"]

# Pattern per trovare i file sorgente
SOURCE_PATTERNS = [
    "*.py",
    "tabs/*.py",
    "gui/*.py",
    "gui/ui/*.py",
    "modules/**/*.py",
]

# Pattern per trovare i file UI
UI_PATTERNS = [
    "gui/ui/*.ui",
]


def find_files(patterns, base_dir):
    """Trova tutti i file che corrispondono ai pattern."""
    files = []
    for pattern in patterns:
        full_pattern = str(base_dir / pattern)
        files.extend(glob.glob(full_pattern, recursive=True))
    return sorted(set(files))


def update_with_pylupdate5():
    """Usa pylupdate5 con il file .pro (metodo tradizionale)."""
    pro_file = PLUGIN_DIR / "pyarchinit.pro"
    if not pro_file.exists():
        print(f"Errore: {pro_file} non trovato")
        return False

    print("Usando pylupdate5 con pyarchinit.pro...")
    try:
        result = subprocess.run(
            ["pylupdate5", str(pro_file)],
            cwd=str(PLUGIN_DIR),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("pylupdate5 completato con successo")
            return True
        else:
            print(f"Errore pylupdate5: {result.stderr}")
            return False
    except FileNotFoundError:
        print("pylupdate5 non trovato. Installa PyQt5 tools.")
        return False


def update_with_pylupdate6():
    """Usa pylupdate6 con sintassi nuova (Qt6)."""
    print("Usando pylupdate6...")

    # Trova tutti i file sorgente
    py_files = find_files(SOURCE_PATTERNS, PLUGIN_DIR)
    ui_files = find_files(UI_PATTERNS, PLUGIN_DIR)

    all_sources = py_files + ui_files
    print(f"Trovati {len(py_files)} file Python e {len(ui_files)} file UI")

    for lang in LANGUAGES:
        ts_file = I18N_DIR / f"pyarchinit_plugin_{lang}.ts"
        print(f"\nAggiornamento {ts_file.name}...")

        # pylupdate6 sintassi: pylupdate6 source1.py source2.py -ts output.ts
        cmd = ["pylupdate6"] + all_sources + ["-ts", str(ts_file)]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(PLUGIN_DIR),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  OK: {ts_file.name}")
            else:
                print(f"  Errore: {result.stderr}")
        except FileNotFoundError:
            print("pylupdate6 non trovato. Installa PyQt6 tools:")
            print("  pip install PyQt6-tools")
            return False

    return True


def compile_translations():
    """Compila i file .ts in .qm usando lrelease."""
    print("\nCompilazione traduzioni (.ts -> .qm)...")

    for lang in LANGUAGES:
        ts_file = I18N_DIR / f"pyarchinit_plugin_{lang}.ts"
        qm_file = I18N_DIR / f"pyarchinit_plugin_{lang}.qm"

        if not ts_file.exists():
            print(f"  Saltato: {ts_file.name} non esiste")
            continue

        # Prova prima lrelease6, poi lrelease
        for lrelease_cmd in ["lrelease6", "lrelease"]:
            try:
                result = subprocess.run(
                    [lrelease_cmd, str(ts_file), "-qm", str(qm_file)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"  OK: {qm_file.name}")
                    break
            except FileNotFoundError:
                continue
        else:
            print(f"  Errore: lrelease non trovato per {ts_file.name}")

    return True


def main():
    use_qt6 = "--qt6" in sys.argv

    print("=" * 50)
    print("Aggiornamento traduzioni PyArchInit")
    print("=" * 50)
    print(f"Directory plugin: {PLUGIN_DIR}")
    print(f"Modalita: {'Qt6' if use_qt6 else 'Qt5'}")
    print()

    # Aggiorna i file .ts
    if use_qt6:
        success = update_with_pylupdate6()
    else:
        success = update_with_pylupdate5()

    if not success:
        print("\nAggiornamento traduzioni fallito!")
        return 1

    # Compila i file .qm
    compile_translations()

    print("\n" + "=" * 50)
    print("Completato!")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
