"""ext_libs must match the Python running QGIS (2026-09-11).

QGIS 4.2.2 on macOS (Python 3.12, arm64) with QGIS 3 (Python 3.9, x86_64)
also installed: the installer took QGIS 3's Python, ext_libs got psycopg2
built for 3.9 and pyArchInit failed with "No module named
'psycopg2._psycopg'". Standard library only, except the last test.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import python_env as pe  # noqa: E402

V39, V312 = (3, 9), (3, 12)
QUIET = dict(log=lambda message: None)


def _touch(path: Path, text=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _qgis3_ext_libs(plugin: Path) -> Path:
    ext = plugin / "ext_libs"
    _touch(ext / "psycopg2" / "_psycopg.cpython-39-darwin.so")
    _touch(ext / "psycopg2" / "__init__.py")
    _touch(ext / "psycopg2_binary-2.9.12.dist-info" / "METADATA")
    _touch(ext / "yaml" / "_yaml.abi3.so")          # version-independent
    return ext


# --- which ext_libs -------------------------------------------------------------

def test_a_module_built_for_another_python_is_found(tmp_path):
    ext = _qgis3_ext_libs(tmp_path)
    assert pe.foreign_extension(str(ext), V312).endswith("_psycopg.cpython-39-darwin.so")
    assert pe.foreign_extension(str(ext), V39) is None


@pytest.mark.parametrize("name", ["_x.cp39-win_amd64.pyd", "_x.cpython-39-x86_64-linux-gnu.so",
                                  "_x.cpython-39-darwin.so"])
def test_version_tags_of_every_system(tmp_path, name):
    _touch(tmp_path / name)
    assert pe.foreign_extension(str(tmp_path), V312)
    assert pe.foreign_extension(str(tmp_path), V39) is None


def test_ext_libs_of_another_python_is_parked_and_a_fresh_one_started(tmp_path):
    _qgis3_ext_libs(tmp_path)
    logs = []

    active = pe.ensure_ext_libs(str(tmp_path), V312, "arm64", log=logs.append)

    assert active == str(tmp_path / "ext_libs") and os.listdir(active) == []
    assert (tmp_path / "ext_libs_cp39" / "psycopg2" / "_psycopg.cpython-39-darwin.so").exists()  # kept
    assert logs and "cp39" in logs[0]


def test_ext_libs_of_the_running_python_is_kept_and_marked(tmp_path):
    _qgis3_ext_libs(tmp_path)
    active = pe.ensure_ext_libs(str(tmp_path), V39, "x86_64", **QUIET)
    assert (Path(active) / "psycopg2").is_dir()
    assert pe.read_marker(active) == "cp39-x86_64"


def test_the_marker_also_catches_another_architecture(tmp_path):
    ext = tmp_path / "ext_libs"
    _touch(ext / "six.py")
    pe.write_marker(str(ext), "cp312-x86_64")      # same version, Intel build
    pe.ensure_ext_libs(str(tmp_path), V312, "arm64", **QUIET)
    assert (tmp_path / "ext_libs_cp312-x86_64" / "six.py").exists()


def test_a_folder_shared_by_two_qgis_swaps_instead_of_reinstalling(tmp_path):
    _qgis3_ext_libs(tmp_path)
    pe.ensure_ext_libs(str(tmp_path), V39, "x86_64", **QUIET)       # QGIS 3: marked
    pe.ensure_ext_libs(str(tmp_path), V312, "arm64", **QUIET)       # QGIS 4: parks it
    ext = tmp_path / "ext_libs"
    _touch(ext / "psycopg2" / "_psycopg.cpython-312-darwin.so")     # QGIS 4 installs
    pe.write_marker(str(ext), "cp312-arm64")

    active = pe.ensure_ext_libs(str(tmp_path), V39, "x86_64", **QUIET)  # QGIS 3 again

    assert (Path(active) / "psycopg2" / "_psycopg.cpython-39-darwin.so").exists()
    assert (tmp_path / "ext_libs_cp312-arm64" / "psycopg2" / "_psycopg.cpython-312-darwin.so").exists()


# --- which Python runs pip ------------------------------------------------------------

def test_the_python_inside_the_running_qgis_4_comes_first():
    app = "/Applications/QGIS-final-4_2_2.app/Contents"
    found = pe.candidates("Darwin", app + "/MacOS/QGIS-final-4_2_2", app + "/Frameworks",
                          app + "/Frameworks", V312)
    assert found[0] == (app + "/MacOS/python3.12", app + "/Frameworks")   # needs PYTHONHOME
    assert not any(p.endswith("QGIS-final-4_2_2") for p, _ in found)       # never QGIS itself


def test_windows_takes_the_python_of_the_running_qgis():
    prefix = r"C:\Program Files\QGIS 4.2\apps\Python312"
    found = pe.candidates("Windows", r"C:\Program Files\QGIS 4.2\bin\qgis-bin.exe", prefix, prefix, V312)
    assert found[0] == (os.path.join(prefix, "python.exe"), prefix)


def test_linux_never_runs_the_qgis_binary():
    assert all(p != "/usr/bin/qgis" for p, _ in pe.candidates("Linux", "/usr/bin/qgis", "/usr", "/usr", V312))


def _fake(monkeypatch, answers):
    monkeypatch.setattr(pe, "candidates", lambda **kw: [(p, h) for p, h, _ in answers])
    table = {p: a for p, _, a in answers}
    monkeypatch.setattr(pe, "probe", lambda python, home=None, timeout=20: table.get(python))
    pe.reset_cache()


def test_pip_runs_with_a_python_of_the_same_version_and_architecture(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "/somewhere/ext_libs")
    _fake(monkeypatch, [("/qgis3/bin/python3", "/qgis3", (3, 9, "x86_64", True)),
                        ("/qgis4/MacOS/python3.12", "/qgis4/Frameworks", (3, 12, "arm64", True)),
                        ("/brew/python3.12", None, (3, 12, "arm64", True))])
    python, env = pe.pip_interpreter(version=V312, machine="arm64")
    assert python == "/qgis4/MacOS/python3.12"
    assert env["PYTHONHOME"] == "/qgis4/Frameworks" and "PYTHONPATH" not in env


def test_without_a_matching_python_nothing_is_installed(monkeypatch):
    _fake(monkeypatch, [("/qgis3/bin/python3", "/qgis3", (3, 9, "x86_64", True)),
                        ("/rosetta/python3.12", None, (3, 12, "x86_64", True))])
    assert pe.pip_interpreter(version=V312, machine="arm64") is None


def test_a_python_without_pip_is_the_last_resort(monkeypatch):
    _fake(monkeypatch, [("/a/python3.12", None, (3, 12, "arm64", False)),
                        ("/b/python3.12", None, (3, 12, "arm64", True))])
    assert pe.pip_interpreter(version=V312, machine="arm64")[0] == "/b/python3.12"


_Q4 = "/Applications/QGIS-final-4_2_2.app/Contents"


@pytest.mark.skipif(not os.path.isfile(_Q4 + "/MacOS/python3.12"), reason="QGIS 4.2.2 not installed here")
def test_the_real_qgis_4_python_runs_only_with_pythonhome():
    got = pe.probe(_Q4 + "/MacOS/python3.12", _Q4 + "/Frameworks")
    assert got[:2] == (3, 12) and got[3]                 # with pip
    assert pe.probe(_Q4 + "/MacOS/python3.12") is None   # cannot find its stdlib alone


# --- requirements (needs the plugin package: QGIS python) -------------------------------

def test_psycopg2_shipped_by_qgis_satisfies_psycopg2_binary(tmp_path, monkeypatch):
    pytest.importorskip("qgis.core")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path / "home"))
    if str(_ROOT.parent) not in sys.path:
        sys.path.insert(0, str(_ROOT.parent))
    plugin = importlib.import_module(_ROOT.name)
    req = tmp_path / "requirements.txt"
    req.write_text("psycopg2-binary>=2.9\n")
    monkeypatch.setattr(plugin, "_EXT_LIBS_DIR", str(tmp_path / "ext_libs"))

    class Dist:
        metadata = {"Name": "psycopg2", "Version": "2.9.12"}

    monkeypatch.setattr(plugin, "distributions", lambda: [Dist()])
    assert plugin.PackageManager.check_required_packages(str(req)) == []
    monkeypatch.setattr(plugin, "distributions", lambda: [])
    assert plugin.PackageManager.check_required_packages(str(req)) == ["psycopg2-binary>=2.9"]
