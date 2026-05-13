#!/usr/bin/env python3
"""
/****************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
    -------------------
    begin                : 2018-04-22
    copyright            : (C) 2008 by Salvatore Larosa; Enzo Cocca <enzo.ccc@gmail.com>
    email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *                                                                        *
 ***************************************************************************/
"""

import re
import shutil
import subprocess
import sys
import platform
import os
#from .. modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility


# s3dgraphy-bump (5.8.1-alpha): clean stale dist-info / package dirs in
# ext_libs/ BEFORE pip-installing a new version. Without this, multiple
# dist-info dirs accumulate (e.g. s3dgraphy-0.1.40.dist-info +
# s3dgraphy-0.1.41.dist-info + s3dgraphy-0.1.42.dist-info side-by-side),
# importlib.metadata.version() picks the lexically-first match instead
# of the active one, and residual files from old releases (a module
# deleted between versions) keep getting imported.
_EXT_LIBS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "ext_libs")
)

# Package-name extraction regex: matches the bare name from a
# requirements line ("s3dgraphy>=0.1.42", "pkg==1.2", "pkg[extra]>=1.0").
_PKG_NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)")


def _cleanup_stale_dists(package_name: str) -> None:
    """Remove ext_libs/<pkg>-*.dist-info/ directories + ext_libs/<pkg>/
    *.dist-info entries for the given package, plus any stale
    __pycache__ inside the package dir.

    Skips silently when ext_libs/ does not exist (fresh install / CI).
    Tolerates package_name case mismatch (PyPI normalises names to lower
    + dashes; on-disk dist-info uses the wheel-name form which may keep
    underscores).
    """
    if not os.path.isdir(_EXT_LIBS_DIR):
        return

    # PyPI / wheel name normalisation: lowercase, underscores -> dashes.
    canon = package_name.lower().replace("_", "-")
    candidates: list[str] = []
    for entry in os.listdir(_EXT_LIBS_DIR):
        # match <name>-*.dist-info exactly (case- and separator-insensitive).
        if entry.lower().endswith(".dist-info"):
            stem = entry[:-len(".dist-info")].lower().replace("_", "-")
            # stem = "<name>-<version>"; split on last '-'.
            if "-" in stem and stem.rsplit("-", 1)[0] == canon:
                candidates.append(entry)

    for entry in candidates:
        full = os.path.join(_EXT_LIBS_DIR, entry)
        try:
            shutil.rmtree(full)
            print(f"[modules_installer] removed stale dist: {entry}")
        except Exception as e:
            print(f"[modules_installer] failed to remove {entry}: {e}")

    # Best-effort: also remove the package dir's __pycache__ so the .pyc
    # files don't shadow the freshly-installed sources.
    pkg_pycache = os.path.join(_EXT_LIBS_DIR, package_name, "__pycache__")
    if os.path.isdir(pkg_pycache):
        try:
            shutil.rmtree(pkg_pycache)
            print(f"[modules_installer] removed stale __pycache__ "
                  f"for {package_name}")
        except Exception as e:
            print(f"[modules_installer] failed to remove "
                  f"__pycache__ for {package_name}: {e}")


def _extract_pkg_name(requirement: str) -> str | None:
    """Return the bare package name from a requirements line, or None
    if the line is empty / unparseable."""
    if not requirement or requirement.startswith("#"):
        return None
    m = _PKG_NAME_RE.match(requirement)
    if not m:
        return None
    name = m.group(1)
    # Strip a trailing [extras] segment.
    if "[" in name:
        name = name.split("[", 1)[0]
    return name or None


packages = sys.argv[1].split(',') if len(sys.argv) >= 2 else []
l = sys.argv[1].split(',') if len(sys.argv) >= 2 else []
# Adding the dependencies python modules in
# package list in order to install via pip module


if not packages:
    # Read dependencies from requirements.txt
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        # Fallback to minimal set if requirements.txt not found
        packages = [
            'SQLAlchemy>=2.0.0',
            'SQLAlchemy-Utils>=0.41.0',
            'GeoAlchemy2>=0.14.0',
            'reportlab>=4.0.0',
            'matplotlib>=3.7.0',
            'graphviz>=0.20',
            'xlsxwriter>=3.1.0',
            'pandas>=2.0.0',
            'opencv-python>=4.8.0',
            'qrcode>=7.4']
if not l:    
    l=[
        'totalopenstation'
        
    ]

   
python_path = sys.exec_prefix
python_version = sys.version[:3]

if platform.system()=='Windows':
    cmd = 'python'
elif platform.system()=='Darwin':
    cmd = '{}/bin/python{}'.format(python_path, python_version)
else:
    cmd = '{}/bin/python{}'.format(python_path, python_version)


for p in packages:
    # Pre-step: clean stale dist-info / __pycache__ in ext_libs/ for
    # this package so importlib.metadata can resolve the freshly
    # installed version unambiguously (5.8.1-alpha s3dgraphy-bump fix).
    name = _extract_pkg_name(p)
    if name:
        _cleanup_stale_dists(name)
    # Use --upgrade to ensure exact versions (==) are installed even if older version exists
    subprocess.call(['python', '-m', 'pip', 'install', '--upgrade', p, '--user'], shell=True)
for t in l:    
    if platform.system() == 'Windows':
        cmd = '{}\python'.format(python_path)
        try:
            subprocess.call(['python','-m','pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=True)
        except KeyError as e:
            print(e)
        else:
            subprocess.call(
                [cmd, '-m', 'pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=True)


    else:
        cmd = '{}/bin/python{}'.format(python_path, python_version)
        try:
            subprocess.call([cmd,'-m','pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=True)
        except KeyError as e:
            print(e)
        else:
            subprocess.call(
                [cmd, '-m', 'pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=False)
