#!/usr/bin/env python3
"""Rende adatti all'atlante del Time Manager i modelli di stampa.

L'atlante cerca nel modello due elementi: il titolo «Tavola N» e
l'immagine della matrice. I modelli generici distribuiti con pyArchInit
non li hanno, e fino alla 5.13.46 sceglierne uno faceva tornare indietro
il generatore in silenzio. Questo script ne scrive una copia preparata
accanto all'originale — mai una sovrascrittura — con i due elementi su
una **pagina nuova**, così non si copre niente di quello che c'era.

    python3 prepare_atlas_templates.py [cartella] [--prova]

Senza argomenti lavora su ``<home pyArchInit>/bin/profile/template``.
Va eseguito con il Python di QGIS, perché è QGIS a scrivere il file:

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/prepare_atlas_templates.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))


def cartella_predefinita() -> Path:
    casa = os.environ.get("PYARCHINIT_HOME") or str(Path.home() / "pyarchinit_5")
    return Path(casa) / "bin" / "profile" / "template"


def main(argv) -> int:
    prova = "--prova" in argv or "--dry-run" in argv
    resto = [a for a in argv if not a.startswith("--")]
    cartella = Path(resto[0]) if resto else cartella_predefinita()
    if not cartella.is_dir():
        print("La cartella %s non c'è." % cartella)
        return 1

    from qgis.core import QgsApplication

    app = QgsApplication([], False)
    QgsApplication.initQgis()
    try:
        from modules.utility.atlas_template import (PREPARED_SUFFIX,
                                                    capabilities,
                                                    prepare_file,
                                                    prepared_name,
                                                    what_to_add)

        modelli = sorted(p for p in cartella.glob("*.qpt")
                         if PREPARED_SUFFIX not in p.stem)
        print("Modelli trovati in %s: %d\n" % (cartella, len(modelli)))
        preparati = saltati = falliti = 0
        for percorso in modelli:
            testo = percorso.read_text(encoding="utf-8", errors="replace")
            caps = capabilities(testo)
            mancanti = what_to_add(caps)
            if not mancanti:
                motivo = ("già completo" if caps.get("map")
                          else "senza mappa, non è da atlante")
                print("  –  %-52s %s" % (percorso.name, motivo))
                saltati += 1
                continue
            if prepared_name(percorso).exists():
                print("  =  %-52s già preparato" % percorso.name)
                saltati += 1
                continue
            if prova:
                print("  +  %-52s aggiungerei: %s"
                      % (percorso.name, ", ".join(mancanti)))
                preparati += 1
                continue
            scritto = prepare_file(percorso)
            if scritto:
                print("  ✓  %-52s -> %s"
                      % (percorso.name, Path(scritto).name))
                preparati += 1
            else:
                print("  ✗  %-52s non scritto" % percorso.name)
                falliti += 1
        print("\n%s: %d, saltati %d, falliti %d"
              % ("Da preparare" if prova else "Preparati",
                 preparati, saltati, falliti))
        return 1 if falliti else 0
    finally:
        QgsApplication.exitQgis()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
