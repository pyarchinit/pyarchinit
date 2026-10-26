"""The Python running QGIS: which interpreter can run pip for it, and
whether the plugin's ext_libs was built for it.

ext_libs holds the packages pip installs for pyArchInit. Their compiled
modules (``_psycopg.cpython-39-darwin.so``, numpy, pandas, PIL, lxml ...)
load only in the Python version and CPU architecture they were built for.
On macOS the installer took the first Python found among fixed paths: with
QGIS 3 (Python 3.9, x86_64) and QGIS 4.2.2 (Python 3.12, arm64) both
installed, QGIS 4 got packages built for 3.9 and failed with
"No module named 'psycopg2._psycopg'" (2026-09-11). A QGIS 3 profile copied
to QGIS 4, ext_libs included, ends the same way.

- ``pip_interpreter()``: a Python with the same version and architecture as
  the running one, preferring the one inside the running QGIS (QGIS 4 on
  macOS: ``Contents/MacOS/python3.12``, which starts only with
  ``PYTHONHOME=sys.prefix``);
- ``ensure_ext_libs()``: an ext_libs built for another Python is parked
  aside as ``ext_libs_<tag>`` (never deleted) and a fresh one is started;
  a parked one matching the running Python is put back, so a plugin folder
  shared by two QGIS versions swaps instead of reinstalling. A marker file
  records which Python an ext_libs is for, so the check is instant.

Standard library only: imported at the very top of the plugin's __init__.
"""
from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime

MARKER = ".pyarchinit_python"
# _psycopg.cpython-39-darwin.so, _x.cp39-win_amd64.pyd, _x.cpython-39-x86_64-linux-gnu.so
# (abi3 modules carry no version and load in any later Python)
_TAG_RE = re.compile(r"\.(?:cpython-|cp)(\d{2,3})[a-z]*(?:-[\w.-]+)?\.(?:so|pyd)$")
# no quotes, pipes or percent signs: the probe may go through cmd.exe (.bat)
_PROBE = ("import sys, platform, importlib.util; "
          "print(sys.version_info[0], sys.version_info[1], platform.machine().lower(), "
          "int(importlib.util.find_spec(chr(112) + chr(105) + chr(112)) is not None))")
_DROP_ENV = ("PYTHONHOME", "PYTHONPATH", "__PYVENV_LAUNCHER__")

_cache = {}


def python_tag(version=None) -> str:
    major, minor = (version or sys.version_info)[:2]
    return "%d%d" % (major, minor)


def abi_tag(version=None, machine=None) -> str:
    """``cp312-arm64``: the Python an ext_libs is built for."""
    return "cp%s-%s" % (python_tag(version), (machine or platform.machine()).lower())


def read_marker(ext_dir):
    try:
        with open(os.path.join(ext_dir, MARKER), encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def write_marker(ext_dir, tag=None) -> None:
    try:
        with open(os.path.join(ext_dir, MARKER), "w", encoding="utf-8") as f:
            f.write((tag or abi_tag()) + "\n")
    except OSError:
        pass


def foreign_extension(ext_dir, version=None):
    """First compiled module under ``ext_dir`` built for another Python
    version, or None."""
    want = python_tag(version)
    for root, dirs, files in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            m = _TAG_RE.search(name)
            if m and m.group(1) != want:
                return os.path.join(root, name)
    return None


def _has_packages(ext_dir) -> bool:
    try:
        return any(n.endswith((".dist-info", ".egg-info")) for n in os.listdir(ext_dir))
    except OSError:
        return False


def _fits(ext_dir, version=None, machine=None):
    """(built for the running Python?, tag of the Python it was built for)."""
    marker = read_marker(ext_dir)
    if marker is not None:
        return marker == abi_tag(version, machine), marker
    bad = foreign_extension(ext_dir, version)
    if bad is None:
        return True, None
    return False, "cp" + _TAG_RE.search(os.path.basename(bad)).group(1)


def _free(path) -> str:
    if not os.path.exists(path):
        return path
    return "%s_%s" % (path, datetime.now().strftime("%Y%m%d%H%M%S"))


def ensure_ext_libs(plugin_dir, version=None, machine=None, log=print) -> str:
    """The ext_libs directory to use for the running Python (created if
    needed). Never raises: if ext_libs cannot be renamed, a directory
    ``ext_libs_<tag>`` next to it is used instead."""
    flat = os.path.join(plugin_dir, "ext_libs")
    mine = abi_tag(version, machine)
    try:
        if os.path.isdir(flat):
            fits, built_for = _fits(flat, version, machine)
            if not fits:
                parked = _free(os.path.join(plugin_dir, "ext_libs_" + built_for))
                os.rename(flat, parked)
                log("PyArchInit: ext_libs was built for another Python (%s; this QGIS runs %s): "
                    "moved to %s, the packages will be installed again for this Python"
                    % (built_for, mine, parked))
                for name in ("ext_libs_" + mine, "ext_libs_cp" + python_tag(version)):
                    candidate = os.path.join(plugin_dir, name)
                    if os.path.isdir(candidate) and _fits(candidate, version, machine)[0]:
                        os.rename(candidate, flat)
                        log("PyArchInit: %s put back as ext_libs" % candidate)
                        break
        os.makedirs(flat, exist_ok=True)
        if read_marker(flat) is None and _has_packages(flat):
            write_marker(flat, mine)  # checked above: skip the scan next time
        return flat
    except OSError as e:
        fallback = os.path.join(plugin_dir, "ext_libs_" + mine)
        try:
            os.makedirs(fallback, exist_ok=True)
        except OSError:
            pass
        log("PyArchInit: cannot prepare ext_libs (%s): using %s" % (e, fallback))
        return fallback


def _env(home=None) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in _DROP_ENV}
    if home:
        env["PYTHONHOME"] = home
    return env


def candidates(system=None, executable=None, prefix=None, base_prefix=None, version=None) -> list:
    """(interpreter, PYTHONHOME or None) to try, those of the running QGIS
    first. Never the QGIS binary itself (on macOS sys.executable is QGIS:
    running it would start a new QGIS)."""
    system = system or platform.system()
    executable = sys.executable if executable is None else executable
    prefix = prefix or sys.prefix
    base_prefix = base_prefix or getattr(sys, "base_prefix", prefix)
    major, minor = (version or sys.version_info)[:2]
    names = ["python%d.%d" % (major, minor), "python%d" % major, "python"]
    found = []
    if system == "Darwin":
        # QGIS 4: Contents/MacOS/python3.12 (prefix Contents/Frameworks);
        # QGIS 3: Contents/MacOS/bin/python3 (prefix Contents/MacOS)
        dirs = [os.path.dirname(executable), os.path.join(os.path.dirname(prefix), "MacOS"),
                os.path.join(prefix, "bin")]
        found += [(os.path.join(d, n), prefix) for d in dirs if d for n in names]
    elif system == "Windows":
        dirs = [prefix, base_prefix, os.path.dirname(executable)]
        qgis_prefix = os.environ.get("QGIS_PREFIX_PATH")
        if qgis_prefix:
            dirs.append(os.path.join(os.path.dirname(os.path.dirname(qgis_prefix)),
                                     "apps", "Python%d%d" % (major, minor)))
        found += [(os.path.join(d, "python.exe"), d) for d in dirs if d]
    else:
        if os.path.basename(executable).startswith("python"):
            found.append((executable, None))
        found += [(w, None) for w in (shutil.which(n) for n in names) if w]
    unique, seen = [], set()
    for path, home in found:
        key = os.path.normcase(os.path.abspath(path))
        if key not in seen:
            seen.add(key)
            unique.append((path, home))
    return unique


def probe(python, home=None, timeout=20):
    """(major, minor, machine, has pip) of ``python``, or None when it does
    not run."""
    if not os.path.isfile(python):
        return None
    extra = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)} if os.name == "nt" else {}
    try:
        out = subprocess.run([python, "-c", _PROBE], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=_env(home), timeout=timeout,
                             shell=python.lower().endswith(".bat"), **extra).stdout
        major, minor, machine, pip = out.decode(errors="replace").strip().splitlines()[-1].split()
        return int(major), int(minor), machine, pip == "1"
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def reset_cache() -> None:
    _cache.clear()


def pip_interpreter(extra=(), version=None, machine=None):
    """(python, env) that runs pip for the running Python — same version
    and architecture, so the wheels it installs load in QGIS — or None."""
    want = (tuple((version or sys.version_info)[:2]), (machine or platform.machine()).lower())
    key = (want, tuple(extra))
    if key in _cache:
        return _cache[key]
    result = without_pip = None
    tried = set()
    for python, home in candidates(version=version) + [(p, None) for p in extra if p]:
        if python in tried:
            continue
        tried.add(python)
        got = probe(python, home)
        if not got or got[:2] != want[0] or got[2] != want[1]:
            continue
        if got[3]:
            result = (python, _env(home))
            break
        without_pip = without_pip or (python, _env(home))
    _cache[key] = result or without_pip
    return _cache[key]


# --------------------------------------------------------------------------
#  Il numpy di QGIS (issue #666)
# --------------------------------------------------------------------------
#
# numpy è di QGIS: una volta caricato non si cambia. Ma pip, installando in
# ext_libs, sceglieva i pacchetti per l'ultimo numpy: su QGIS 3.40 (Python
# 3.12, numpy 1.26.4) prendeva pandas 3.1, che vuole numpy >= 2.0.2, e le
# schede che usano pandas non si aprivano. Ogni installazione in ext_libs ha
# quindi il vincolo del numpy di QGIS; un pacchetto già installato che ne
# chiede un altro si rifà, una volta sola per quel numpy (ATTEMPTS ricorda i
# tentativi, così una riparazione impossibile non torna a ogni avvio).

ATTEMPTS = ".pyarchinit_numpy_attempts.json"


def _inside(path, folder) -> bool:
    try:
        path, folder = os.path.realpath(path), os.path.realpath(folder)
    except (OSError, ValueError):
        return False
    return path == folder or path.startswith(folder.rstrip(os.sep) + os.sep)


def _public(versione):
    """Senza l'etichetta locale (2.1.3+mkl → 2.1.3): pip non ha candidati
    con quella, e un vincolo con l'etichetta farebbe fallire tutto."""
    return str(versione).split("+", 1)[0].strip() if versione else versione


def host_numpy_version(ext_dir, path=None):
    """La versione del numpy di QGIS: quello già caricato se viene da fuori
    ext_libs (dentro QGIS è così), altrimenti il primo numpy fuori da
    ext_libs sul percorso degli import."""
    if path is None:
        mod = sys.modules.get("numpy")
        if mod is not None and not _inside(getattr(mod, "__file__", "") or "", ext_dir):
            v = getattr(mod, "__version__", None)
            if v:
                return _public(v)
    from importlib.metadata import distributions
    radici = [p for p in (sys.path if path is None else path) if p and not _inside(p, ext_dir)]
    for d in distributions(name="numpy", path=radici):
        return _public(d.version)
    return None


def numpy_constraint_args(ext_dir, path=None, workdir=None) -> list:
    """``["--constraint", file]`` con ``numpy==<quello di QGIS>`` per pip;
    niente se QGIS non ha numpy o se il file non si può scrivere (meglio
    un'installazione senza vincolo che una finestra bloccata)."""
    versione = host_numpy_version(ext_dir, path=path)
    if not versione:
        return []
    import tempfile
    try:
        fd, nome = tempfile.mkstemp(prefix="pyarchinit_numpy_", suffix=".txt", dir=workdir)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("numpy==%s\n" % versione)
    except OSError:
        return []
    return ["--constraint", nome]


def _packaging():
    try:
        from packaging.markers import Marker
        from packaging.requirements import Requirement
    except ImportError:
        try:
            from pip._vendor.packaging.markers import Marker
            from pip._vendor.packaging.requirements import Requirement
        except ImportError:
            return None
    return Requirement, Marker


def _newest_dists(ext_dir):
    """Una distribuzione per nome, la più recente sul disco: pip --target che
    scende di versione lascia il vecchio dist-info accanto al nuovo."""
    from importlib.metadata import distributions
    scelte = {}
    for d in distributions(path=[ext_dir]):
        nome = (d.metadata.get("Name") or "").lower().replace("_", "-")
        if not nome:
            continue
        try:
            quando = os.path.getmtime(str(d._path))           # noqa: SLF001
        except (AttributeError, OSError):
            quando = 0.0
        if nome not in scelte or quando > scelte[nome][0]:
            scelte[nome] = (quando, d)
    return {n: d for n, (_q, d) in scelte.items()}


def prune_stale_dists(ext_dir) -> list:
    """Toglie i dist-info vecchi rimasti accanto a quello nuovo dello stesso
    pacchetto (dopo pip --target --upgrade); torna i nomi delle cartelle tolte."""
    if not os.path.isdir(ext_dir):
        return []
    tieni = {str(getattr(d, "_path", "")) for d in _newest_dists(ext_dir).values()}
    tolti = []
    for voce in os.listdir(ext_dir):
        cartella = os.path.join(ext_dir, voce)
        if voce.endswith(".dist-info") and os.path.isdir(cartella) and cartella not in tieni:
            try:
                shutil.rmtree(cartella)
                tolti.append(voce)
            except OSError:
                pass
    return tolti


def needs_newer_numpy(ext_dir, numpy_version) -> list:
    """I pacchetti di ext_libs (nomi minuscoli, in ordine) il cui requisito
    su numpy esclude quello di QGIS; [] se non si può dire."""
    strumenti = _packaging()
    if strumenti is None or not numpy_version or not os.path.isdir(ext_dir):
        return []
    Requirement, _Marker = strumenti
    fuori = []
    for nome, d in sorted(_newest_dists(ext_dir).items()):
        if nome == "numpy":
            continue
        for riga in d.requires or []:
            try:
                req = Requirement(riga)
            except Exception:                               # noqa: BLE001
                continue
            if req.name.lower() != "numpy":
                continue
            if req.marker is not None and not req.marker.evaluate({"extra": ""}):
                continue
            if not req.specifier.contains(numpy_version, prereleases=True):
                fuori.append(nome)
                break
    return fuori


def _attempts(ext_dir) -> dict:
    import json
    try:
        with open(os.path.join(ext_dir, ATTEMPTS), encoding="utf-8") as f:
            dati = json.load(f)
        return dati if isinstance(dati, dict) else {}
    except (OSError, ValueError):
        return {}


def _spec_name(spec) -> str:
    return re.split(r"[<>=!~;\[ ]", str(spec), 1)[0].strip().lower().replace("_", "-")


def note_numpy_attempt(ext_dir, spec, path=None) -> None:
    """Ricorda che il pacchetto di ``spec`` si è reinstallato per il numpy di
    QGIS di adesso: riuscito o no, non si ripropone a ogni avvio."""
    import json
    versione = host_numpy_version(ext_dir, path=path)
    if not versione or not os.path.isdir(ext_dir):
        return
    dati = _attempts(ext_dir)
    dati[_spec_name(spec)] = versione
    try:
        with open(os.path.join(ext_dir, ATTEMPTS), "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=1, sort_keys=True)
    except OSError:
        pass


def numpy_repairs(requirements_path, ext_dir, path=None) -> list:
    """Le righe dei requisiti (senza marcatore; per le dipendenze il nome)
    da reinstallare perché in ext_libs chiedono un numpy diverso da quello
    di QGIS, tolte quelle già tentate per questo numpy."""
    versione = host_numpy_version(ext_dir, path=path)
    fuori = needs_newer_numpy(ext_dir, versione)
    if not fuori:
        return []
    tentati = _attempts(ext_dir)
    fuori = [n for n in fuori if tentati.get(n) != versione]
    strumenti = _packaging()
    righe = {}
    try:
        with open(requirements_path, encoding="utf-8") as f:
            for riga in f:
                riga = riga.split(" #", 1)[0].strip()
                if not riga or riga.startswith("#"):
                    continue
                spec, _, marcatore = riga.partition(";")
                if marcatore.strip():
                    try:
                        if strumenti is None or not strumenti[1](marcatore.strip()).evaluate():
                            continue        # la riga non vale per questo Python
                    except Exception:                       # noqa: BLE001
                        continue
                righe.setdefault(_spec_name(spec), spec.strip())
    except OSError:
        pass
    return [righe.get(n, n) for n in fuori]


def drop_ext_numpy(ext_dir, path=None) -> list:
    """Toglie da ext_libs la copia di numpy che pip --target ci mette come
    dipendenza, se QGIS ha il suo (quello che conta, già caricato). Torna le
    voci tolte; niente se QGIS non ha numpy."""
    if not host_numpy_version(ext_dir, path=path) or not os.path.isdir(ext_dir):
        return []
    tolte = []
    for voce in os.listdir(ext_dir):
        bassa = voce.lower()
        if bassa in ("numpy", "numpy.libs") or (
                bassa.startswith("numpy-") and bassa.endswith((".dist-info", ".whl"))):
            pieno = os.path.join(ext_dir, voce)
            try:
                if os.path.isdir(pieno) and not os.path.islink(pieno):
                    shutil.rmtree(pieno)
                else:
                    os.remove(pieno)
                tolte.append(voce)
            except OSError:
                pass
    return tolte
