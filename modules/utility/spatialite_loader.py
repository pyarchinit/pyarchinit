"""Dove si trova mod_spatialite e come si carica, per tutto il plugin.

Su macOS il percorso cambia col QGIS: il 3.44 lo mette in
``Contents/Frameworks/mod_spatialite.so``, i QGIS più vecchi in
``Contents/MacOS/lib``. Si cerca prima nel QGIS che sta girando (da
``sys.prefix`` e ``sys.executable``), poi negli altri QGIS installati, poi in
Homebrew e MacPorts: Homebrew porta un suo SQLite, meglio non mescolarlo con
quello di QGIS se non serve. ``libspatialite.dylib`` non è un candidato: è la
libreria, non l'estensione, e ``load_extension`` non ci trova il punto
d'ingresso (``symbol not found``).

Su Windows e Linux si prova il nome nudo, come prima: lì lo trova il caricatore
del sistema. Su macOS il nome nudo chiude l'elenco (un QGIS di conda o
MacPorts che lo ha solo nel percorso del caricatore).
"""
from __future__ import annotations

import glob
import os
import platform
import sqlite3
import sys

APP_ROOTS = ("/Applications", "~/Applications")
MAC_EXTRA_DIRS = ("/opt/homebrew/lib", "/opt/homebrew/opt/libspatialite/lib",
                  "/usr/local/lib", "/usr/local/opt/libspatialite/lib", "/opt/local/lib")
LINUX_DIRS = ("/usr/lib/x86_64-linux-gnu", "/usr/lib/aarch64-linux-gnu", "/usr/lib64", "/usr/lib")
# dentro Contents/ di un QGIS.app: 3.44 e successivi, poi i più vecchi
_BUNDLE_DIRS = ("Frameworks", "MacOS/lib", "Frameworks/lib")

# l'ultimo che si è caricato: le connessioni dopo la prima lo provano subito
_last_good = None


def _in_dir(directory):
    """I file mod_spatialite di una cartella: prima quelli senza numero."""
    if not directory or not os.path.isdir(directory):
        return []
    nudi = [os.path.join(directory, "mod_spatialite" + ext) for ext in (".so", ".dylib")]
    numerati = sorted(glob.glob(os.path.join(directory, "mod_spatialite.*.so"))
                      + glob.glob(os.path.join(directory, "mod_spatialite.*.dylib")))
    return [p for p in nudi + numerati if os.path.isfile(p)]


def _bundle_contents(path):
    """``…/Qualcosa.app/Contents`` se ``path`` sta dentro un'app, o None."""
    parti = os.path.abspath(path).split(os.sep)
    for i in range(len(parti) - 1, -1, -1):
        if parti[i].endswith(".app"):
            return os.sep.join(parti[:i + 1] + ["Contents"])
    return None


def _mac_dirs(prefix, executable, app_roots, mac_extra_dirs):
    dirs = []
    # il QGIS che gira
    for path in (prefix, executable):
        if not path:
            continue
        contents = _bundle_contents(path)
        if contents:
            dirs += [os.path.join(contents, d) for d in _BUNDLE_DIRS]
    if prefix:
        # anche fuori da un .app (un Python copiato, conda, Homebrew)
        dirs += [prefix, os.path.join(prefix, "lib"),
                 os.path.join(os.path.dirname(prefix), "Frameworks"),
                 os.path.join(os.path.dirname(prefix), "MacOS", "lib")]
    # gli altri QGIS installati
    for root in app_roots:
        for app in sorted(glob.glob(os.path.join(os.path.expanduser(root), "QGIS*.app"))):
            dirs += [os.path.join(app, "Contents", d) for d in _BUNDLE_DIRS]
    return dirs + list(mac_extra_dirs)


def spatialite_candidates(system=None, prefix=None, executable=None, app_roots=APP_ROOTS,
                          mac_extra_dirs=MAC_EXTRA_DIRS, linux_dirs=LINUX_DIRS):
    """I percorsi da provare con ``load_extension``, nell'ordine.

    Su macOS solo file che esistono, e ognuno una volta sola (anche quando
    ``mod_spatialite.so`` è un collegamento a ``mod_spatialite.8.so``)."""
    system = system or platform.system()
    if system == "Windows":
        return ["mod_spatialite.dll", "mod_spatialite"]
    if system != "Darwin":
        assoluti = [p for d in linux_dirs for p in _in_dir(d)]
        return ["mod_spatialite.so", "mod_spatialite"] + assoluti
    prefix = sys.prefix if prefix is None else prefix
    executable = sys.executable if executable is None else executable
    visti, risultato = set(), []
    for directory in _mac_dirs(prefix, executable, app_roots, mac_extra_dirs):
        for path in _in_dir(directory):
            vero = os.path.realpath(path)
            if vero not in visti:
                visti.add(vero)
                risultato.append(path)
    return risultato + ["mod_spatialite"]


def load_spatialite(dbapi_conn, candidates=None):
    """Carica mod_spatialite nella connessione sqlite3 e dice da dove.

    Prova i candidati in ordine (prima l'ultimo che ha funzionato, senza
    rifare la ricerca a ogni connessione); se nessuno si carica solleva
    ``sqlite3.OperationalError`` con l'elenco dei percorsi provati e l'ultimo
    errore, anche quando il Python non sa caricare estensioni."""
    global _last_good
    try:
        dbapi_conn.enable_load_extension(True)
    except AttributeError as e:
        raise sqlite3.OperationalError(
            "Could not find mod_spatialite library (this Python cannot load SQLite extensions: %s)" % e)
    if candidates is None and _last_good:
        try:
            dbapi_conn.load_extension(_last_good)
            return _last_good
        except Exception:                                   # noqa: BLE001
            pass
    if candidates is None:
        candidates = spatialite_candidates()
    ordine = list(candidates)
    if _last_good in ordine:
        ordine.remove(_last_good)
        ordine.insert(0, _last_good)
    ultimo = None
    for path in ordine:
        try:
            dbapi_conn.load_extension(path)
        except Exception as e:                              # noqa: BLE001
            ultimo = e
            continue
        _last_good = path
        return path
    provati = ", ".join(ordine) or "nessun file trovato"
    consiglio = (" Please ensure QGIS is properly installed or install libspatialite via "
                 "Homebrew: brew install libspatialite") if platform.system() == "Darwin" else ""
    raise sqlite3.OperationalError(
        "Could not find mod_spatialite library (tried: %s; last error: %s).%s"
        % (provati, ultimo, consiglio))
