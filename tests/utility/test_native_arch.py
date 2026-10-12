"""Rosetta: i sottoprocessi Python partono con l'architettura nativa (2026-10-12).

Il QGIS per macOS è x86_64 e gira sotto Rosetta sui Mac Apple Silicon: un
Python universal lanciato da lì parte come x86_64 e pip non trova le ruote
di torch («from versions: none»). `native_prefix()` mette `arch -arm64`
davanti ai comandi, solo dove serve.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import native_arch as na  # noqa: E402


def test_prefisso_solo_su_apple_silicon():
    assert na.native_prefix(system="Darwin", apple_silicon=True) == ["arch", "-arm64"]
    assert na.native_prefix(system="Darwin", apple_silicon=False) == []
    assert na.native_prefix(system="Linux", apple_silicon=True) == []
    assert na.native_prefix(system="Windows", apple_silicon=True) == []


def test_native_command_non_tocca_il_comando_originale():
    cmd = ["/v/bin/python", "-m", "pip", "install", "torch"]
    out = na.native_command(cmd, system="Darwin", apple_silicon=True)
    assert out == ["arch", "-arm64", "/v/bin/python", "-m", "pip", "install", "torch"]
    assert cmd[0] == "/v/bin/python"
    assert na.native_command(cmd, system="Linux") == cmd


def test_host_is_apple_silicon_legge_sysctl(monkeypatch):
    class R:
        def __init__(self, out):
            self.stdout = out
    monkeypatch.setattr(na, "_APPLE_SILICON", None)
    monkeypatch.setattr(na.platform, "system", lambda: "Darwin")
    assert na.host_is_apple_silicon(run=lambda *a, **k: R("1\n")) is True
    monkeypatch.setattr(na, "_APPLE_SILICON", None)
    assert na.host_is_apple_silicon(run=lambda *a, **k: R("0\n")) is False
    monkeypatch.setattr(na, "_APPLE_SILICON", None)
    monkeypatch.setattr(na.platform, "system", lambda: "Linux")
    assert na.host_is_apple_silicon(run=lambda *a, **k: R("1\n")) is False


def test_il_valore_e_cachato(monkeypatch):
    calls = []

    class R:
        stdout = "1\n"
    monkeypatch.setattr(na, "_APPLE_SILICON", None)
    monkeypatch.setattr(na.platform, "system", lambda: "Darwin")
    na.host_is_apple_silicon(run=lambda *a, **k: (calls.append(1), R())[1])
    na.host_is_apple_silicon(run=lambda *a, **k: (calls.append(1), R())[1])
    assert len(calls) == 1
