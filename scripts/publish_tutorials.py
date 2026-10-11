#!/usr/bin/env python3
"""Pubblica i tutorial su Read the Docs, come versione **dev**.

    python3 scripts/publish_tutorials.py            # prepara e mostra
    python3 scripts/publish_tutorials.py --push     # e manda

I tutorial vivono qui, in `docs/tutorials/`: dieci lingue, 38 capitoli
ciascuna, con le immagini. Il sito `pyarchinitdoc.readthedocs.io` però non
si costruisce da questo repository: il progetto Read the Docs guarda
**`enzococca/pyarchinitDOC`**, dove sta il manuale 4.0 — lo dice il link
«Edit on GitHub» della pagina pubblicata
(`github.com/enzococca/pyarchinitDOC/blob/master/source/index.rst`).

Quindi per pubblicarli bisogna portarli là. Questo script li copia nel
ramo **`dev`** di quel repository, sotto `tutorials/`, e ci mette la
configurazione perché Read the Docs costruisca **quelli** invece del
manuale vecchio. Il manuale resta dov'è, in `source/`: non si cancella
niente, cambia solo che cosa viene costruito per la versione `dev`.

**Perché una copia e non un sottomodulo.** Un sottomodulo terrebbe una
sorgente sola, ma Read the Docs dovrebbe clonare questo repository, che
pesa **260 MB** (ci sono i database di esempio): un clone così a ogni
build è lento e fragile. I tutorial sono 14 MB. Si copiano, e si rifà la
copia a ogni rilascio — una riga di comando, nessun segreto da
custodire.

**Che cosa NON fa.** Non attiva la versione su Read the Docs: quella è
una spunta nel pannello del progetto (Versions → `dev` → Active), e ci
vuole chi ha le chiavi. Finché non è attiva, il ramo c'è e il sito no.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
TUTORIAL = RADICE / "docs" / "tutorials"

#: Il repository che Read the Docs costruisce, e il ramo della versione.
REPO = "https://github.com/enzococca/pyarchinitDOC.git"
RAMO = "dev"
#: Dove vanno i tutorial dentro quel repository.
DENTRO = "tutorials"

#: Quello che non si copia: la build locale, la roba di sistema, i PDF.
ESCLUSI = ("_build", ".DS_Store", "__pycache__", ".doctrees")

#: La configurazione di Read the Docs per la versione dev.
#:
#: `fail_on_warning` è **spento** di proposito: i tutorial sono Markdown
#: scritto da più mani, e una segnalazione cosmetica di Pygments su un
#: blocco di codice SQL non deve far sparire il sito. Il `sphinx:`
#: dichiarato una volta sola, e non due come nel file del manuale vecchio,
#: dove la seconda chiave cancella la prima e la `configuration` va persa.
READTHEDOCS = """# Read the Docs — versione «dev»: i tutorial di pyArchInit 5.
#
# I sorgenti stanno in `tutorials/`, copiati da
# https://github.com/pyarchinit/pyarchinit (docs/tutorials) con
# `scripts/publish_tutorials.py`. Il manuale 4.0 resta in `source/` e non
# viene costruito per questa versione.
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

sphinx:
  configuration: tutorials/conf.py
  fail_on_warning: false

formats:
  - htmlzip

python:
  install:
    - requirements: tutorials/requirements.txt
"""

#: Quello che serve per costruirli: Markdown e il tema del sito. Nient'altro
#: — il manuale vecchio installa SQLAlchemy, OpenCV e PyQt5 perché
#: documenta il codice; i tutorial sono testo.
REQUISITI = """sphinx>=7.0
myst-parser>=2.0
sphinx-rtd-theme>=2.0
"""


def _git(*args, cwd=None, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check,
                          capture_output=True, text=True)


def copia(sorgente: Path, destinazione: Path) -> int:
    """Rifà `destinazione` con quello che c'è in `sorgente`."""
    if destinazione.exists():
        shutil.rmtree(destinazione)
    quanti = 0
    for radice, cartelle, file in os.walk(sorgente):
        cartelle[:] = [c for c in cartelle if c not in ESCLUSI]
        relativo = Path(radice).relative_to(sorgente)
        (destinazione / relativo).mkdir(parents=True, exist_ok=True)
        for nome in file:
            if nome in ESCLUSI:
                continue
            shutil.copy2(Path(radice) / nome, destinazione / relativo / nome)
            quanti += 1
    return quanti


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--push", action="store_true",
                    help="manda il ramo dev (se no si ferma al commit)")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--ramo", default=RAMO)
    args = ap.parse_args(argv)

    if not TUTORIAL.is_dir():
        raise SystemExit("mancano i tutorial in %s" % TUTORIAL)

    lavoro = Path(tempfile.mkdtemp(prefix="pyarchinit-doc-"))
    try:
        print("clono %s (ramo %s)…" % (args.repo, args.ramo))
        _git("clone", "--depth", "1", "--branch", args.ramo, args.repo,
             str(lavoro / "doc"))
        doc = lavoro / "doc"

        quanti = copia(TUTORIAL, doc / DENTRO)
        (doc / ".readthedocs.yaml").write_text(READTHEDOCS, encoding="utf-8")
        (doc / DENTRO / "requirements.txt").write_text(REQUISITI,
                                                       encoding="utf-8")
        print("copiati %d file in %s/" % (quanti, DENTRO))

        _git("add", "-A", cwd=doc)
        stato = _git("status", "--porcelain", cwd=doc).stdout.strip()
        if not stato:
            print("niente di nuovo da pubblicare")
            return 0
        print("%d file cambiati" % len(stato.splitlines()))
        versione = (RADICE / "metadata.txt").read_text(encoding="utf-8")
        versione = next((r.split("=", 1)[1].strip()
                         for r in versione.splitlines()
                         if r.startswith("version=")), "")
        _git("commit", "-m",
             "docs: i tutorial di pyArchInit %s, dieci lingue\n\n"
             "Copiati da pyarchinit/pyarchinit (docs/tutorials) con\n"
             "scripts/publish_tutorials.py. La versione dev del sito\n"
             "costruisce questi invece del manuale 4.0, che resta in\n"
             "source/ e non viene toccato." % versione, cwd=doc)
        if args.push:
            _git("push", "origin", args.ramo, cwd=doc)
            print("mandato sul ramo %s" % args.ramo)
            print("ora, nel pannello di Read the Docs: Versions -> %s -> "
                  "Active" % args.ramo)
        else:
            print("commit fatto ma non mandato: rilancia con --push")
        return 0
    finally:
        shutil.rmtree(lavoro, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
