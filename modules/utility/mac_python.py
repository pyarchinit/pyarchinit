"""Il Python di QGIS su macOS, per installare le dipendenze con pip.

Il QGIS 3.44 ha il lanciatore ``Contents/MacOS/python``, che imposta
PYTHONHOME e chiama ``python3.12``: lanciato da solo, ``python3.12`` non
parte (``No module named 'encodings'``). I QGIS più vecchi avevano
``Contents/MacOS/bin/python3`` o il Python.framework dentro Frameworks.
Si prova prima il QGIS che sta girando, poi gli altri installati.
"""
import glob
import os
import sys

APP_ROOTS = ("/Applications", "~/Applications")
_NAMES = ("python3", "python3.12", "python3.11", "python3.10", "python3.9")


def _running_macos_dir(path):
    """``…/Qualcosa.app/Contents/MacOS`` se ``path`` sta dentro un'app."""
    if not path:
        return None
    parti = os.path.abspath(path).split(os.sep)
    for i in range(len(parti) - 1, -1, -1):
        if parti[i].endswith(".app"):
            return os.sep.join(parti[:i + 1] + ["Contents", "MacOS"])
    return None


def mac_python_candidates(prefix=None, executable=None, app_roots=APP_ROOTS, extra_macos_dirs=()):
    """Gli interpreti da provare per ``pip install``, nell'ordine; solo
    quelli che esistono, ognuno una volta."""
    prefix = sys.prefix if prefix is None else prefix
    executable = sys.executable if executable is None else executable
    basi = [_running_macos_dir(prefix), _running_macos_dir(executable)] + list(extra_macos_dirs)
    for root in app_roots:
        basi += sorted(glob.glob(os.path.join(os.path.expanduser(root), "QGIS*.app", "Contents", "MacOS")))
    risultato = []
    for base in basi:
        if not base:
            continue
        contents = os.path.dirname(base)
        possibili = [os.path.join(base, "python")]
        for cartella in (os.path.join(base, "bin"),
                         os.path.join(contents, "Frameworks", "Python.framework", "Versions", "Current", "bin")):
            possibili += [os.path.join(cartella, n) for n in _NAMES]
        for p in possibili:
            if os.path.isfile(p) and p not in risultato:
                risultato.append(p)
    return risultato


def same_python(candidates, timeout=20):
    """Solo gli interpreti con la stessa versione e architettura di quello
    che fa girare il plugin: i pacchetti compilati per un altro Python (un
    QGIS 4 accanto a un QGIS 3) in ext_libs non si importerebbero."""
    import platform
    import subprocess
    voluto = "%d %d %s" % (sys.version_info[0], sys.version_info[1], platform.machine().lower())
    sonda = "import sys, platform; print(sys.version_info[0], sys.version_info[1], platform.machine().lower())"
    buoni = []
    for python in candidates:
        try:
            out = subprocess.run([python, "-c", sonda], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 timeout=timeout).stdout.decode(errors="replace").strip()
        except (OSError, subprocess.SubprocessError):
            continue
        if out.splitlines() and out.splitlines()[-1] == voluto:
            buoni.append(python)
    return buoni
