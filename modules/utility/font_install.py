"""Il font Cambria, che usano le schede in PDF, nei font dell'utente.

Prima su macOS il plugin apriva ``~/pyarchinit_5/bin`` e chiedeva di fare
doppio clic su ogni ``cambria.*``. Ora i file si copiano da soli nella
cartella dei font dell'utente (nessun permesso di amministratore), da
``<PYARCHINIT_HOME>/bin`` o, se lì non ci sono, da
``resources/dbfiles/cambria.zip`` del plugin.

ReportLab cerca i nomi esatti (``TTFont('Cambria', 'Cambria.ttc')``…): si
scrivono così, maiuscole comprese (su Linux contano), e conta come
installato solo un file intero che sia davvero un font. La copia passa da un
``.part`` rinominato alla fine: un disco pieno a metà non lascia un file
troncato col nome giusto. Solo libreria standard.
"""
from __future__ import annotations

import os
import platform
import shutil
import zipfile

# i nomi che cercano i moduli PDF
REQUIRED = ("Cambria.ttc", "cambriab.ttf", "cambriai.ttf", "cambriaz.ttf")
# più il regolare in .ttf, che altri programmi usano
CAMBRIA = REQUIRED + ("Cambria.ttf",)
_FIRME = (b"ttcf", b"\x00\x01\x00\x00", b"OTTO", b"true")


def user_fonts_dir(system=None):
    """La cartella dei font dell'utente, o None dove copiare non basta
    (Windows vuole anche la voce nel registro)."""
    system = system or platform.system()
    if system == "Darwin":
        return os.path.expanduser("~/Library/Fonts")
    if system == "Linux":
        return os.path.join(os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"), "fonts")
    return None


def _is_font(path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(4) in _FIRME
    except OSError:
        return False


def cambria_installed(fonts_dir) -> bool:
    """Tutti i file che cercano le schede in PDF, coi nomi esatti, e veri font."""
    if not fonts_dir:
        return False
    return all(_is_font(os.path.join(fonts_dir, f)) for f in REQUIRED)


def _copy_atomic(src_stream, dest) -> None:
    parte = dest + ".part"
    try:
        with open(parte, "wb") as dst:
            shutil.copyfileobj(src_stream, dst)
        if not _is_font(parte):
            raise OSError("%s non è un font" % os.path.basename(dest))
        os.replace(parte, dest)
    except BaseException:
        try:
            os.remove(parte)
        except OSError:
            pass
        raise


def install_cambria(source_dir, fonts_dir, zip_path=None) -> list:
    """Copia in ``fonts_dir`` i file di Cambria che mancano (o che non sono
    font interi); torna i nomi copiati. Non alza mai: le schede in PDF non
    valgono un plugin che non si carica."""
    if not fonts_dir:
        return []
    mancanti = [f for f in CAMBRIA if not _is_font(os.path.join(fonts_dir, f))]
    if not mancanti:
        return []
    copiati = []
    try:
        os.makedirs(fonts_dir, exist_ok=True)
        # «bin» relativo vorrebbe dire la cartella corrente: mai
        if source_dir and os.path.isabs(source_dir) and os.path.isdir(source_dir):
            per_nome = {v.lower(): os.path.join(source_dir, v) for v in os.listdir(source_dir)}
            for f in list(mancanti):
                sorgente = per_nome.get(f.lower())
                if sorgente and _is_font(sorgente):
                    try:
                        with open(sorgente, "rb") as src:
                            _copy_atomic(src, os.path.join(fonts_dir, f))
                    except OSError:
                        continue
                    copiati.append(f)
                    mancanti.remove(f)
        if mancanti and zip_path and os.path.isfile(zip_path):
            with zipfile.ZipFile(zip_path) as z:
                per_nome = {os.path.basename(n).lower(): n for n in z.namelist()}
                for f in list(mancanti):
                    voce = per_nome.get(f.lower())
                    if not voce:
                        continue
                    try:
                        with z.open(voce) as src:
                            _copy_atomic(src, os.path.join(fonts_dir, f))
                    except Exception:                       # noqa: BLE001 — zlib.error, EOFError, BadZipFile…
                        continue
                    copiati.append(f)
                    mancanti.remove(f)
    except Exception as e:                                  # noqa: BLE001
        print("pyArchInit: Cambria non installato: %s" % e)
    return copiati
