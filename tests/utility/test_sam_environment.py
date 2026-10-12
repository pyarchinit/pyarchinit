"""SAM: l'ambiente separato (venv, pesi, comandi) — 2026-10-12.

La finestra SAM cercava `sam_venv` e tre script worker in `bin/` che nessuno
creava: il modulo non poteva girare. Ora `sam_environment` sa creare
l'ambiente con un Python di sistema 3.10–3.13, scaricare i pesi da GitHub
(asset ultralytics) e costruire la riga di comando del worker, che sta nel
plugin (`scripts/sam_worker.py`).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

pytest.importorskip("qgis.PyQt")
from modules.utility import sam_environment as se  # noqa: E402


# --- registro dei pesi -------------------------------------------------------
def test_i_pesi_sam_e_a_testo_sono_asset_pubblici_di_ultralytics():
    for key in se.SAM_KEYS + se.TEXT_KEYS + ("mobileclip2_b",):
        w = se.WEIGHTS[key]
        assert w.url.startswith("https://github.com/ultralytics/assets/releases/download/")
        assert w.url.endswith("/" + w.file)
        assert w.size_mb > 0


def test_le_classi_a_testo_vogliono_anche_il_codificatore():
    for key in se.TEXT_KEYS:
        files = [w.file for w in se.weight_files(key)]
        assert files[0].startswith("yoloe-26") and files[-1] == "mobileclip2_b.ts"
    assert [w.file for w in se.weight_files("sam2.1_t")] == ["sam2.1_t.pt"]


def test_pesi_mancanti_e_dimensione(tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    assert se.weights_dir() == os.path.join(str(tmp_path), "bin", "models", "sam")
    assert [w.key for w in se.missing_weights("yoloe-26s")] == ["yoloe-26s", "mobileclip2_b"]
    assert se.download_size_mb("yoloe-26s") == 31 + 254
    os.makedirs(se.weights_dir())
    Path(se.weight_path("mobileclip2_b")).write_bytes(b"x")
    assert [w.key for w in se.missing_weights("yoloe-26s")] == ["yoloe-26s"]
    assert se.download_size_mb("yoloe-26s") == 31


# --- l'interprete -------------------------------------------------------------
def test_i_candidati_mac_preferiscono_python_org_e_non_includono_qgis():
    cands = se.python_candidates(system="Darwin", environ={}, which=lambda n: None)
    assert cands[0] == ["/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"]
    assert ["/opt/homebrew/bin/python3.12"] in cands
    assert not any("QGIS.app" in c[0] for c in cands)


def test_i_candidati_windows_usano_il_launcher_e_osgeo4w():
    env = {"LOCALAPPDATA": r"C:\Users\x\AppData\Local", "OSGEO4W_ROOT": r"C:\OSGeo4W"}
    cands = se.python_candidates(system="Windows", environ=env, which=lambda n: None)
    assert cands[0] == ["py", "-3.12"]
    assert any(c[0].endswith("python-qgis.bat") for c in cands)


def test_pick_python_scarta_le_versioni_fuori_finestra():
    versions = {"old": (3, 9), "new": (3, 14), "ok": (3, 12), "broken": None}
    chosen, version = se.pick_python([["old"], ["broken"], ["new"], ["ok"]],
                                     version_of=lambda cmd: versions[cmd[0]])
    assert chosen == ["ok"] and version == (3, 12)
    assert se.pick_python([["old"]], version_of=lambda cmd: (3, 9)) == (None, None)


def test_pick_python_salta_i_percorsi_che_non_esistono(tmp_path):
    missing = str(tmp_path / "nope" / "python3")
    calls = []

    def version_of(cmd):
        calls.append(cmd)
        return (3, 12)
    chosen, _ = se.pick_python([[missing], ["python3"]], version_of=version_of)
    assert chosen == ["python3"] and calls == [["python3"]]


def test_python_version_legge_major_minor_e_vuole_venv(monkeypatch):
    class R:
        def __init__(self, code, out):
            self.returncode, self.stdout = code, out
    assert se.python_version(["py"], run=lambda *a, **k: R(0, "3 12\n")) == (3, 12)
    assert se.python_version(["py"], run=lambda *a, **k: R(1, "")) is None
    cmd_seen = {}

    def run(cmd, **k):
        cmd_seen["cmd"] = cmd
        return R(0, "3 11\n")
    monkeypatch.setattr(se, "native_prefix", lambda *a, **k: [])
    se.python_version(["py", "-3.11"], run=run)
    assert cmd_seen["cmd"][:2] == ["py", "-3.11"] and "import sys, venv, ensurepip" in cmd_seen["cmd"][-1]


# --- architettura (Rosetta) ------------------------------------------------------
def test_su_apple_silicon_ogni_comando_parte_con_arch_arm64():
    assert se.native_prefix(system="Darwin", apple_silicon=True) == ["arch", "-arm64"]
    assert se.native_prefix(system="Darwin", apple_silicon=False) == []
    assert se.native_prefix(system="Linux", apple_silicon=True) == []
    assert se.native_prefix(system="Windows", apple_silicon=True) == []


def test_i_comandi_usano_il_prefisso_nativo(monkeypatch):
    monkeypatch.setattr(se, "native_prefix", lambda *a, **k: ["arch", "-arm64"])
    assert se.create_venv_command(["/py"], "/v")[:3] == ["arch", "-arm64", "/py"]
    assert se.pip_install_command("/v/bin/python", system="Darwin", nvidia=False)[:3] == ["arch", "-arm64", "/v/bin/python"]
    assert se.check_command("/v/bin/python")[:3] == ["arch", "-arm64", "/v/bin/python"]
    assert se.worker_command("/v/bin/python", "a", "b", "sam2")[:3] == ["arch", "-arm64", "/v/bin/python"]
    seen = {}

    def run(cmd, **k):
        seen["cmd"] = cmd

        class R:
            returncode, stdout = 0, "3 12\n"
        return R()
    se.python_version(["/py"], run=run)
    assert seen["cmd"][:3] == ["arch", "-arm64", "/py"]


# --- comandi ------------------------------------------------------------------
def test_pip_su_linux_senza_nvidia_prende_torch_cpu(monkeypatch):
    monkeypatch.setattr(se, "native_prefix", lambda *a, **k: [])
    cmd = se.pip_install_command("/v/bin/python", system="Linux", nvidia=False)
    assert "--extra-index-url" in cmd and "https://download.pytorch.org/whl/cpu" in cmd
    cmd = se.pip_install_command("/v/bin/python", system="Linux", nvidia=True)
    assert "--extra-index-url" not in cmd
    cmd = se.pip_install_command("/v/bin/python", system="Darwin", nvidia=False)
    assert "--extra-index-url" not in cmd and cmd[-2:] == list(se.PACKAGES)


def test_clean_env_toglie_le_variabili_di_qgis():
    env = se.clean_env({"PYTHONHOME": "/qgis", "PYTHONPATH": "/x", "QT_PLUGIN_PATH": "/q", "HOME": "/h"})
    assert "PYTHONHOME" not in env and "PYTHONPATH" not in env and "QT_PLUGIN_PATH" not in env
    assert env["HOME"] == "/h" and env["PYTHONUNBUFFERED"] == "1"


def test_is_ready_senza_venv_e_con_check_finto(tmp_path):
    ok, info = se.is_ready(str(tmp_path / "nope"))
    assert ok is False and "non installato" in info
    py = tmp_path / "python"
    py.write_text("")

    class R:
        returncode, stderr = 0, ""
        stdout = "WARNING ⚠️ Ultralytics settings reset\nSAMENV 8.4.175 2.8.0 mps\n"
    ok, info = se.is_ready(str(py), run=lambda *a, **k: R())
    assert ok and info == "ultralytics 8.4.175, torch 2.8.0, mps"

    class R2:
        returncode, stderr, stdout = 0, "", "qualcosa d'altro\n"
    ok, info = se.is_ready(str(py), run=lambda *a, **k: R2())
    assert not ok and "inattesa" in info


def test_worker_command_e_una_lista_con_lo_script_del_plugin(monkeypatch):
    monkeypatch.setattr(se, "native_prefix", lambda *a, **k: [])
    cmd = se.worker_command("/v/bin/python", "/t/in.png", "/t/out.json", "yoloe",
                            weights="/w/yoloe-26s-seg.pt", classes=["building", "road"], conf=0.3)
    assert cmd[0] == "/v/bin/python" and cmd[1].endswith(os.path.join("scripts", "sam_worker.py"))
    assert os.path.isfile(cmd[1]), "lo script del worker deve stare nel plugin"
    assert cmd[cmd.index("--classes") + 1] == "building,road"
    assert cmd[cmd.index("--conf") + 1] == "0.3"
    assert "--api-key" not in cmd and "--prompts" not in cmd
    cmd = se.worker_command("/v/bin/python", "a", "b", "roboflow", classes="stones", api_key="k")
    assert cmd[cmd.index("--api-key") + 1] == "k" and "--weights" not in cmd


def test_venv_python_segue_il_sistema(tmp_path):
    py = se.venv_python(str(tmp_path))
    if sys.platform.startswith("win"):
        assert py.endswith(os.path.join("Scripts", "python.exe"))
    else:
        assert py == os.path.join(str(tmp_path), "bin", "python")


# --- lingua e tempo scaduto -------------------------------------------------------
def test_i_messaggi_dell_ambiente_seguono_la_lingua(tmp_path):
    se.set_language("en")
    try:
        ok, info = se.is_ready(str(tmp_path / "nope"))
        assert not ok and info == "environment not installed"
        assert se.msg("timeout", 7) == "Timed out (7 s): process stopped."
    finally:
        se.set_language("it")
    assert se.is_ready(str(tmp_path / "nope"))[1] == "ambiente non installato"


def test_worker_command_porta_la_lingua(monkeypatch):
    monkeypatch.setattr(se, "native_prefix", lambda *a, **k: [])
    cmd = se.worker_command("/v/bin/python", "a", "b", "sam2", lang="en")
    assert cmd[cmd.index("--lang") + 1] == "en"
    cmd = se.worker_command("/v/bin/python", "a", "b", "sam2")
    assert cmd[cmd.index("--lang") + 1] == se.LANGUAGE


def test_il_tempo_scaduto_ferma_davvero_il_worker(tmp_path, monkeypatch):
    """Prima `wait(timeout)` veniva dopo la lettura dell'output fino alla fine: non scattava mai."""
    import time
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    esiti = []
    thread = se.SamWorkerThread(["sleep", "30"], str(tmp_path / "out.json"), timeout_s=1)
    thread.finished_ok.connect(lambda ok, m, path: esiti.append((ok, m, path)))
    t0 = time.time()
    thread.run()                                   # sincrono: niente event loop
    assert time.time() - t0 < 8
    assert esiti and esiti[0][0] is False and "scaduto" in esiti[0][1]


def test_il_tempo_scaduto_ferma_anche_l_installazione(tmp_path, monkeypatch):
    import time
    righe = []
    thread = se.SamSetupThread()
    thread.log.connect(righe.append)
    t0 = time.time()
    assert thread._stream(["sleep", "30"], 1) is False
    assert time.time() - t0 < 8 and any("scaduto" in r for r in righe)
