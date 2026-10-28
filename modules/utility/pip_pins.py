"""Le versioni fissate di requirements.txt come vincolo a ogni pip --target.

Su macOS le dipendenze vanno in ext_libs con ``pip install --target``, un
pacchetto alla volta: pip non vede quello che c'è già in ext_libs e risolve
le dipendenze da capo. SQLAlchemy-Utils 0.38 e GeoAlchemy2 0.9 chiedono
«SQLAlchemy qualsiasi» e pip prendeva la 2.x, che sovrascriveva la 1.4.27
appena installata: GeoAlchemy2 non si importava più (``with_metaclass``) e la
finestra delle dipendenze tornava a ogni avvio (issue #667). Con le versioni
fissate come vincolo pip sceglie sempre quelle.

``pip --target`` che cambia versione lascia il vecchio dist-info accanto al
nuovo: ``prune_stale_dists`` tiene solo il più recente.

Se le versioni fissate, messe tutte insieme, non si possono risolvere (su
Python 3.9 langchain-core 0.3.85 vuole un langsmith più nuovo di quello
fissato), si riprova col vincolo solo sul database: è quello che, se salta,
non fa più caricare il plugin.
"""
import os
import re
import shutil
import sys
import tempfile

_OPS = {
    "<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b, "==": lambda a, b: a == b, "!=": lambda a, b: a != b,
}
# il salto da SQLAlchemy 1.4 a 2.x rompe GeoAlchemy2 0.9 (with_metaclass)
DB_STACK = ("sqlalchemy", "sqlalchemy-utils", "geoalchemy2")

_MARKER = re.compile(r'^\s*python_version\s*(<=|>=|==|!=|<|>)\s*["\'](\d+)\.(\d+)["\']\s*$')


def _marker_ok(marker, version):
    """True se il marcatore vale per ``version``; solo ``python_version``:
    un marcatore che non si sa leggere non vincola niente."""
    m = _MARKER.match(marker)
    if not m:
        return False
    return _OPS[m.group(1)](tuple(version[:2]), (int(m.group(2)), int(m.group(3))))


def _norm(nome):
    return re.sub(r"[-_.]+", "-", nome).lower()


def pinned_lines(requirements_path, version=None, only=None):
    """Le righe ``nome==versione`` di requirements.txt che valgono per questo
    Python, senza marcatore né commento; con ``only`` solo quei pacchetti."""
    version = tuple(version or sys.version_info[:2])
    righe = []
    try:
        with open(requirements_path, encoding="utf-8") as f:
            for riga in f:
                riga = riga.split("#", 1)[0].strip()
                if not riga:
                    continue
                spec, _, marcatore = riga.partition(";")
                spec = spec.strip()
                # pip non accetta gli extra in un file di vincoli
                if "==" not in spec or any(c in spec for c in "<>!~,["):
                    continue
                if only is not None and _norm(spec.split("==", 1)[0].strip()) not in only:
                    continue
                if marcatore.strip() and not _marker_ok(marcatore.strip(), version):
                    continue
                righe.append(spec.replace(" ", ""))
    except OSError:
        return []
    return righe


def constraints_file(requirements_path, version=None, workdir=None, only=None):
    """Un file temporaneo con le versioni fissate, da passare a pip con
    ``--constraint``; None se non ce ne sono o non si può scrivere."""
    righe = pinned_lines(requirements_path, version=version, only=only)
    if not righe:
        return None
    try:
        fd, path = tempfile.mkstemp(prefix="pyarchinit_pins_", suffix=".txt", dir=workdir)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(righe) + "\n")
        return path
    except OSError:
        return None


def constraint_sets(requirements_path, version=None, workdir=None):
    """Gli argomenti di pip da provare in ordine: tutte le versioni fissate,
    poi solo il database; ``[[]]`` (senza vincolo) se non ce ne sono. Torna
    anche i file temporanei, da togliere dopo."""
    files = [p for p in (constraints_file(requirements_path, version, workdir),
                         constraints_file(requirements_path, version, workdir, only=DB_STACK)) if p]
    return ([["--constraint", p] for p in files] or [[]]), files


def _version_key(entry):
    versione = entry[:-len(".dist-info")].rsplit("-", 1)[-1]
    return tuple(int(n) for n in re.findall(r"\d+", versione))


def _dist_name(entry):
    return entry[:-len(".dist-info")].rsplit("-", 1)[0].lower().replace("_", "-").replace(".", "-")


def prune_stale_dists(ext_dir):
    """Per ogni pacchetto con più dist-info in ``ext_dir`` tiene il più
    recente (quello appena installato) e toglie gli altri; dice cosa ha tolto."""
    try:
        voci = [e for e in os.listdir(ext_dir) if e.endswith(".dist-info")]
    except OSError:
        return []
    gruppi = {}
    for e in voci:
        gruppi.setdefault(_dist_name(e), []).append(os.path.join(ext_dir, e))
    tolti = []
    for percorsi in gruppi.values():
        if len(percorsi) < 2:
            continue
        # il più recente; a parità di data (una copia che non ha tenuto le
        # date) la versione più alta, come legge check_required_packages
        percorsi.sort(key=lambda p: (os.path.getmtime(p), _version_key(os.path.basename(p))), reverse=True)
        for vecchio in percorsi[1:]:
            try:
                shutil.rmtree(vecchio)
                tolti.append(vecchio)
            except OSError:
                pass
    return sorted(tolti)
