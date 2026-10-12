# -*- coding: utf-8 -*-
"""Far partire i sottoprocessi Python con l'architettura giusta (Rosetta).

Il QGIS per macOS e' un binario **x86_64**: su un Mac con chip Apple gira
sotto Rosetta, e ogni processo figlio eredita la traduzione. Un Python
«universal» (python.org) lanciato da li' parte come x86_64, e `pip` non trova
piu' le ruote native: per torch, che non ha ruote x86_64 per i Python
recenti, il risultato e' «No matching distribution found for torch».

`native_prefix()` restituisce `['arch', '-arm64']` quando serve, e una lista
vuota altrove: va messo davanti a OGNI comando che lancia un interprete di
sistema (creazione del venv, pip, controlli, script esterni). Lo usano il
modulo SAM e Pottery Tools.
"""
from __future__ import annotations

import platform
import subprocess

_APPLE_SILICON = None


def host_is_apple_silicon(run=subprocess.run):
    """True su un Mac con chip Apple, anche se il processo corrente gira sotto Rosetta."""
    global _APPLE_SILICON
    if _APPLE_SILICON is None:
        _APPLE_SILICON = False
        if platform.system() == "Darwin":
            try:
                out = run(["/usr/sbin/sysctl", "-n", "hw.optional.arm64"], capture_output=True, text=True, timeout=5)
                _APPLE_SILICON = out.stdout.strip() == "1"
            except (OSError, subprocess.SubprocessError):
                _APPLE_SILICON = platform.machine() == "arm64"
    return _APPLE_SILICON


def native_prefix(system=None, apple_silicon=None):
    """`['arch', '-arm64']` su Apple Silicon, altrimenti `[]`."""
    system = system or platform.system()
    if system != "Darwin":
        return []
    if apple_silicon is None:
        apple_silicon = host_is_apple_silicon()
    return ["arch", "-arm64"] if apple_silicon else []


def native_command(cmd, system=None, apple_silicon=None):
    """Il comando (lista) con il prefisso davanti."""
    return native_prefix(system, apple_silicon) + list(cmd)
