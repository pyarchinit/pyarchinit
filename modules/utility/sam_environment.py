# -*- coding: utf-8 -*-
"""L'ambiente del modulo SAM: l'interprete separato, i pacchetti, i pesi.

La segmentazione gira **fuori** da QGIS, in un ambiente virtuale creato in
`<home>/bin/sam_venv` con un Python di sistema (3.10–3.13): torch e
ultralytics non si possono installare nel Python di QGIS senza rischi. Il
dialogo chiama lo script `scripts/sam_worker.py` con quel Python; questo
modulo sa dove sta tutto, come si crea e come si controlla.

I pesi stanno in `<home>/bin/models/sam/` e vengono dagli asset pubblici di
ultralytics (GitHub, senza token):

- SAM 2.1 (Meta) per punti, riquadri e «tutto automatico»;
- YOLOE-26 per le **classi a testo** («building, road, river, field»), che
  ha bisogno anche del codificatore di testo MobileCLIP2 (254 MB, una volta).

Le funzioni pure (registro, scelta dell'interprete, comandi) non toccano Qt e
sono provate dai test; i thread in fondo sono il lato Qt che il dialogo usa.

**Trappola Rosetta (Mac Apple Silicon).** Il QGIS per macOS e' un binario
x86_64 che gira sotto Rosetta: ogni processo figlio eredita la traduzione, e
un Python «universal» (python.org) parte come x86_64 — pip non trova allora
nessuna ruota di torch («from versions: none»). Per questo ogni comando
passa da `native_prefix()`: su Apple Silicon e' `arch -arm64`, che forza il
ramo nativo; altrove e' vuoto.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

from qgis.PyQt.QtCore import QThread, pyqtSignal

from .native_arch import host_is_apple_silicon, native_prefix  # noqa: F401 - riesportati
from .pyarchinit_home import pyarchinit_home_bin

ASSETS = "https://github.com/ultralytics/assets/releases/download/"

#: Pacchetti dell'ambiente. `ultralytics` porta con se' torch, torchvision,
#: opencv, numpy, pillow e requests.
PACKAGES = ("ultralytics>=8.4", "requests")

#: Versioni di Python accettate per l'ambiente (torch ha ruote da 3.10 a 3.13).
PYTHON_MIN = (3, 10)
PYTHON_MAX = (3, 13)


@dataclass(frozen=True)
class Weight:
    """Un file di pesi scaricabile."""
    key: str
    file: str
    url: str
    size_mb: int
    kind: str                     # 'sam' | 'text' | 'encoder'
    label: str
    extras: Tuple[str, ...] = ()  # altri pesi necessari (chiavi del registro)


WEIGHTS = {
    "sam2.1_t": Weight("sam2.1_t", "sam2.1_t.pt", ASSETS + "v8.3.0/sam2.1_t.pt", 78, "sam", "SAM 2.1 Tiny"),
    "sam2.1_s": Weight("sam2.1_s", "sam2.1_s.pt", ASSETS + "v8.3.0/sam2.1_s.pt", 92, "sam", "SAM 2.1 Small"),
    "sam2.1_b": Weight("sam2.1_b", "sam2.1_b.pt", ASSETS + "v8.3.0/sam2.1_b.pt", 162, "sam", "SAM 2.1 Base+"),
    "sam2.1_l": Weight("sam2.1_l", "sam2.1_l.pt", ASSETS + "v8.3.0/sam2.1_l.pt", 449, "sam", "SAM 2.1 Large"),
    "yoloe-26s": Weight("yoloe-26s", "yoloe-26s-seg.pt", ASSETS + "v8.4.0/yoloe-26s-seg.pt", 31, "text",
                        "YOLOE-26 S (classi a testo)", ("mobileclip2_b",)),
    "yoloe-26m": Weight("yoloe-26m", "yoloe-26m-seg.pt", ASSETS + "v8.4.0/yoloe-26m-seg.pt", 70, "text",
                        "YOLOE-26 M (classi a testo)", ("mobileclip2_b",)),
    "yoloe-26l": Weight("yoloe-26l", "yoloe-26l-seg.pt", ASSETS + "v8.4.0/yoloe-26l-seg.pt", 79, "text",
                        "YOLOE-26 L (classi a testo)", ("mobileclip2_b",)),
    "mobileclip2_b": Weight("mobileclip2_b", "mobileclip2_b.ts", ASSETS + "v8.4.0/mobileclip2_b.ts", 254,
                            "encoder", "MobileCLIP2 (codificatore di testo)"),
}

#: Le chiavi offerte per tipo di prompt, nell'ordine della tendina.
SAM_KEYS = ("sam2.1_t", "sam2.1_s", "sam2.1_b", "sam2.1_l")
TEXT_KEYS = ("yoloe-26s", "yoloe-26m", "yoloe-26l")


# ----------------------------------------------------------------------
# Percorsi
# ----------------------------------------------------------------------
def weights_dir():
    return os.path.join(pyarchinit_home_bin(), "models", "sam")


def weight_path(key):
    return os.path.join(weights_dir(), WEIGHTS[key].file)


def weight_files(key):
    """Il peso e i suoi extra, nell'ordine di scaricamento."""
    w = WEIGHTS[key]
    return [w] + [WEIGHTS[k] for k in w.extras]


def missing_weights(key):
    """I file che mancano per usare `key`."""
    return [w for w in weight_files(key) if not os.path.isfile(os.path.join(weights_dir(), w.file))]


def download_size_mb(key):
    return sum(w.size_mb for w in missing_weights(key))


def venv_dir():
    return os.path.join(pyarchinit_home_bin(), "sam_venv")


def venv_python(root=None):
    root = root or venv_dir()
    if sys.platform.startswith("win"):
        return os.path.join(root, "Scripts", "python.exe")
    return os.path.join(root, "bin", "python")


def worker_script():
    """`scripts/sam_worker.py` del plugin (sta accanto al codice, non in bin/)."""
    plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(plugin_dir, "scripts", "sam_worker.py")


def clean_env(environ=None):
    """Variabili d'ambiente senza quelle che QGIS mette per il suo Python."""
    env = dict(os.environ if environ is None else environ)
    for key in ("PYTHONHOME", "PYTHONPATH", "PYTHONEXECUTABLE", "PYTHONSTARTUP", "VIRTUAL_ENV",
                "PYTHONNOUSERSITE", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
        env.pop(key, None)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUNBUFFERED", "1")
    return env


# ----------------------------------------------------------------------
# Scelta dell'interprete
# ----------------------------------------------------------------------
def python_candidates(system=None, environ=None, which=shutil.which):
    """Gli interpreti da provare, nell'ordine, come liste di argomenti.

    Prima i Python «da python.org» e Homebrew nelle versioni con le ruote di
    torch, poi quelli sul PATH; su Windows il launcher `py`. Il Python di
    QGIS non c'e' apposta: sul Mac e' un 3.9 e su Windows non crea venv.
    """
    system = system or platform.system()
    environ = os.environ if environ is None else environ
    versions = ("3.12", "3.11", "3.13", "3.10")
    found: List[List[str]] = []

    def add(cmd):
        if cmd and cmd not in found:
            found.append(list(cmd))

    if system == "Darwin":
        for v in versions:
            add([f"/Library/Frameworks/Python.framework/Versions/{v}/bin/python3"])
        for v in versions:
            add([f"/opt/homebrew/bin/python{v}"])
            add([f"/usr/local/bin/python{v}"])
    elif system == "Windows":
        for v in versions:
            add(["py", f"-{v}"])
        local = environ.get("LOCALAPPDATA", "")
        for v in versions:
            add([os.path.join(local, "Programs", "Python", "Python" + v.replace(".", ""), "python.exe")])
        osgeo = environ.get("OSGEO4W_ROOT", "")
        if osgeo:
            add([os.path.join(osgeo, "bin", "python-qgis.bat")])
    for v in versions:
        exe = which(f"python{v}")
        if exe:
            add([exe])
    for name in ("python3", "python"):
        exe = which(name)
        if exe:
            add([exe])
    return found


def python_version(cmd, run=subprocess.run):
    """(major, minor) dell'interprete, o None se non parte o non ha `venv`."""
    try:
        result = run(native_prefix() + list(cmd)
                     + ["-c", "import sys, venv, ensurepip; print(sys.version_info[0], sys.version_info[1])"],
                     capture_output=True, text=True, timeout=20, env=clean_env())
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    try:
        major, minor = result.stdout.split()[:2]
        return int(major), int(minor)
    except ValueError:
        return None


def pick_python(candidates=None, version_of=python_version, minimum=PYTHON_MIN, maximum=PYTHON_MAX):
    """Il primo interprete utilizzabile e la sua versione: (cmd, (3, 12)) o (None, None)."""
    for cmd in (python_candidates() if candidates is None else candidates):
        exe = cmd[0]
        if os.sep in exe and not os.path.exists(exe):
            continue
        version = version_of(cmd)
        if version and minimum <= version <= maximum:
            return list(cmd), version
    return None, None


# ----------------------------------------------------------------------
# Comandi
# ----------------------------------------------------------------------
def create_venv_command(python_cmd, root=None):
    return native_prefix() + list(python_cmd) + ["-m", "venv", "--clear", root or venv_dir()]


def has_nvidia(which=shutil.which):
    return which("nvidia-smi") is not None


def pip_install_command(py=None, packages=PACKAGES, system=None, nvidia=None):
    """`pip install` dei pacchetti; su Linux senza NVIDIA prende torch «cpu»,
    che pesa 200 MB invece dei 2.5 GB delle ruote CUDA."""
    system = system or platform.system()
    cmd = native_prefix(system) + [py or venv_python(), "-m", "pip", "install", "--upgrade", "--no-warn-script-location"]
    nvidia = has_nvidia() if nvidia is None else nvidia
    if system == "Linux" and not nvidia:
        cmd += ["--extra-index-url", "https://download.pytorch.org/whl/cpu"]
    return cmd + list(packages)


CHECK_MARKER = "SAMENV"


def check_command(py=None):
    """Stampa una riga `SAMENV <ultralytics> <torch> <device>`: ultralytics scrive
    avvisi su stdout, per questo la riga si riconosce dal marcatore."""
    return native_prefix() + [py or venv_python(), "-c",
            "import ultralytics, torch, cv2\n"
            "dev = 'mps' if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available() "
            "else ('cuda' if torch.cuda.is_available() else 'cpu')\n"
            f"print('{CHECK_MARKER}', ultralytics.__version__, torch.__version__, dev)"]


def is_ready(py=None, run=subprocess.run, timeout=120):
    """(True, 'ultralytics 8.4.x, torch 2.x, mps') se l'ambiente c'e' e importa."""
    py = py or venv_python()
    if not os.path.isfile(py):
        return False, "ambiente non installato"
    try:
        result = run(check_command(py), capture_output=True, text=True, timeout=timeout, env=clean_env())
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"ambiente non utilizzabile: {e}"
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip().splitlines()
        return False, "pacchetti mancanti: " + (tail[-1] if tail else "?")
    marked = [l for l in result.stdout.splitlines() if l.startswith(CHECK_MARKER + " ")]
    try:
        ultra, torch, dev = marked[-1].split()[1:4]
    except (IndexError, ValueError):
        return False, "risposta inattesa: " + result.stdout.strip()[:80]
    return True, f"ultralytics {ultra}, torch {torch}, {dev}"


def worker_command(py, image, output, backend, *, weights=None, mode="auto", prompts=None,
                   classes=None, conf=0.25, imgsz=1024, min_area=20.0, simplify=1.0,
                   api_key=None, device="auto"):
    """La riga di comando del worker (lista, mai shell)."""
    cmd = native_prefix() + [py, worker_script(), "--image", image, "--output", output, "--backend", backend,
           "--mode", mode, "--conf", str(conf), "--imgsz", str(int(imgsz)),
           "--min-area", str(min_area), "--simplify", str(simplify), "--device", device]
    if weights:
        cmd += ["--weights", weights]
    if prompts:
        cmd += ["--prompts", prompts]
    if classes:
        cmd += ["--classes", ",".join(classes) if not isinstance(classes, str) else classes]
    if api_key:
        cmd += ["--api-key", api_key]
    return cmd


# ----------------------------------------------------------------------
# Thread Qt
# ----------------------------------------------------------------------
class SamSetupThread(QThread):
    """Crea l'ambiente (o lo aggiorna) e installa i pacchetti, riga per riga."""
    log = pyqtSignal(str)
    finished_ok = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        if self._process is not None:
            try:
                self._process.terminate()
            except OSError:
                pass

    def _stream(self, cmd, timeout_s):
        self.log.emit("$ " + " ".join(cmd))
        self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         text=True, env=clean_env(), bufsize=1)
        try:
            for line in self._process.stdout:
                line = line.rstrip()
                if line:
                    self.log.emit(line)
            self._process.wait(timeout=timeout_s)
        finally:
            code = self._process.returncode
            self._process = None
        return code == 0

    def run(self):
        try:
            py = venv_python()
            if not os.path.isfile(py):
                cmd, version = pick_python()
                if cmd is None:
                    self.finished_ok.emit(False, "Nessun Python 3.10–3.13 trovato: installa Python da python.org "
                                                 "(o Homebrew) e riprova.")
                    return
                self.log.emit(f"Python {version[0]}.{version[1]}: {' '.join(cmd)}")
                os.makedirs(os.path.dirname(venv_dir()), exist_ok=True)
                if not self._stream(create_venv_command(cmd), 300):
                    self.finished_ok.emit(False, "Creazione dell'ambiente fallita (vedi il registro).")
                    return
            if self._cancelled:
                self.finished_ok.emit(False, "Annullato.")
                return
            self._stream(native_prefix() + [py, "-m", "pip", "install", "--upgrade", "pip"], 300)
            if not self._stream(pip_install_command(py), 3600):
                self.finished_ok.emit(False, "Installazione dei pacchetti fallita (vedi il registro).")
                return
            ok, info = is_ready(py)
            self.finished_ok.emit(ok, info)
        except Exception as e:                       # noqa: BLE001 - va mostrato, non perso
            self.finished_ok.emit(False, f"Errore: {e}")


class SamDownloadThread(QThread):
    """Scarica i pesi che mancano per una chiave, con avanzamento."""
    progress = pyqtSignal(int, str)      # percento del file corrente, testo
    finished_ok = pyqtSignal(bool, str)

    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            os.makedirs(weights_dir(), exist_ok=True)
            todo = missing_weights(self.key)
            for n, w in enumerate(todo, 1):
                dest = os.path.join(weights_dir(), w.file)
                part = dest + ".part"
                self.progress.emit(0, f"{w.label} ({n}/{len(todo)}, ~{w.size_mb} MB)")
                try:
                    with urllib.request.urlopen(w.url, timeout=60) as resp, open(part, "wb") as out:
                        total = int(resp.headers.get("Content-Length") or 0)
                        done = 0
                        while True:
                            chunk = resp.read(1 << 18)
                            if not chunk:
                                break
                            if self._cancelled:
                                raise RuntimeError("annullato")
                            out.write(chunk)
                            done += len(chunk)
                            if total:
                                self.progress.emit(int(done * 100 / total),
                                                   f"{w.label}: {done // (1 << 20)} / {total // (1 << 20)} MB")
                    os.replace(part, dest)
                except Exception:
                    if os.path.exists(part):
                        os.remove(part)         # mai lasciare un file a meta'
                    raise
            self.finished_ok.emit(True, "Pesi pronti.")
        except Exception as e:                       # noqa: BLE001
            self.finished_ok.emit(False, f"Scaricamento fallito: {e}")


class SamWorkerThread(QThread):
    """Esegue il worker esterno e riporta l'esito."""
    progress = pyqtSignal(str)
    finished_ok = pyqtSignal(bool, str, str)   # ok, messaggio, percorso del JSON

    def __init__(self, cmd, output, timeout_s=1800, parent=None):
        super().__init__(parent)
        self.cmd = list(cmd)
        self.output = output
        self.timeout_s = timeout_s
        self._process = None

    def cancel(self):
        if self._process is not None:
            try:
                self._process.terminate()
            except OSError:
                pass

    def run(self):
        try:
            os.makedirs(weights_dir(), exist_ok=True)
            self.progress.emit("Segmentazione in corso…")
            self._process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             text=True, env=clean_env(), cwd=weights_dir(), bufsize=1)
            lines = []
            for line in self._process.stdout:
                line = line.rstrip()
                if line:
                    lines.append(line)
                    if line.startswith("[sam]"):
                        self.progress.emit(line[5:].strip())
            self._process.wait(timeout=self.timeout_s)
            code = self._process.returncode
            self._process = None
            if code == 0 and os.path.isfile(self.output):
                self.finished_ok.emit(True, "Segmentazione completata.", self.output)
            else:
                tail = "\n".join(lines[-12:])
                self.finished_ok.emit(False, f"Il worker e' uscito con codice {code}:\n{tail}", "")
        except subprocess.TimeoutExpired:
            self.cancel()
            self.finished_ok.emit(False, "Tempo scaduto.", "")
        except Exception as e:                       # noqa: BLE001
            self.finished_ok.emit(False, f"Errore: {e}", "")
