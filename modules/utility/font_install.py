"""Il font Cambria, che usano le schede in PDF, nei font dell'utente.

Prima su macOS il plugin apriva ``~/pyarchinit_5/bin`` e chiedeva di fare
doppio clic su ogni ``cambria.*``. Ora i file si copiano da soli nella
cartella dei font dell'utente (nessun permesso di amministratore): da
``<PYARCHINIT_HOME>/bin`` o, se lì non ci sono, da
``resources/dbfiles/cambria.zip`` del plugin. Solo libreria standard.
"""
from __future__ import annotations

import os
import platform
import shutil
import zipfile

CAMBRIA = ("Cambria.ttf", "cambria.ttc", "cambriab.ttf", "cambriai.ttf", "cambriaz.ttf")


def user_fonts_dir(system=None):
    """La cartella dei font dell'utente, o None dove copiare non basta
    (Windows vuole anche la voce nel registro)."""
    system = system or platform.system()
    if system == "Darwin":
        return os.path.expanduser("~/Library/Fonts")
    if system == "Linux":
        return os.path.join(os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"), "fonts")
    return None


def cambria_installed(fonts_dir) -> bool:
    if not fonts_dir:
        return False
    try:
        presenti = {f.lower() for f in os.listdir(fonts_dir)}
    except OSError:
        return False
    return "cambria.ttc" in presenti or "cambria.ttf" in presenti


def install_cambria(source_dir, fonts_dir, zip_path=None) -> list:
    """Copia i file di Cambria che mancano in ``fonts_dir``; torna i nomi
    copiati ([] se c'era già tutto o non c'è da dove prenderli)."""
    if not fonts_dir:
        return []
    try:
        presenti = {f.lower() for f in os.listdir(fonts_dir)}
    except OSError:
        presenti = set()
    mancanti = [f for f in CAMBRIA if f.lower() not in presenti]
    if not mancanti:
        return []
    copiati = []
    try:
        os.makedirs(fonts_dir, exist_ok=True)
        for f in list(mancanti):
            sorgente = os.path.join(source_dir or "", f)
            if os.path.isfile(sorgente):
                shutil.copy2(sorgente, os.path.join(fonts_dir, f))
                copiati.append(f)
                mancanti.remove(f)
        if mancanti and zip_path and os.path.isfile(zip_path):
            with zipfile.ZipFile(zip_path) as z:
                nomi = {os.path.basename(n).lower(): n for n in z.namelist()}
                for f in mancanti:
                    voce = nomi.get(f.lower())
                    if voce:
                        with z.open(voce) as src, open(os.path.join(fonts_dir, f), "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        copiati.append(f)
    except (OSError, zipfile.BadZipFile):
        pass
    return copiati
