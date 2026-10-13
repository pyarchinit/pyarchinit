"""Le etichette dell'atlante si rimettono com'erano anche se la generazione
salta (13 ottobre 2026: «abbiamo forzato la scritta delle etichettature
nelle view» — il numero in un cerchio e la quota erano rimasti sulle viste
del progetto dopo una tavola non finita)."""
from __future__ import annotations

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _generate_images():
    albero = ast.parse((_ROOT / "tabs" / "Gis_Time_controller.py").read_text(encoding="utf-8"))
    for n in ast.walk(albero):
        if isinstance(n, ast.FunctionDef) and n.name == "generate_images":
            return n
    raise AssertionError("generate_images")


def _chiama(nodo, nome: str) -> bool:
    return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
               and c.func.attr == nome for c in ast.walk(nodo))


def test_le_etichette_si_rimettono_in_un_finally():
    f = _generate_images()
    tentativi = [n for n in ast.walk(f) if isinstance(n, ast.Try) and n.finalbody]
    con_rimessa = [t for t in tentativi
                   if any(_chiama(s, "_togli_le_etichette") for s in t.finalbody)]
    assert con_rimessa, "le etichette si tolgono solo in fondo: una tavola che salta le lascia sulle viste"
    tentativo = con_rimessa[0]
    assert any(_chiama(s, "_metti_le_etichette") for s in f.body), "si mettono prima del try"
    assert not any(_chiama(s, "_metti_le_etichette") for s in tentativo.body)
    assert any(_chiama(s, "_butta_via_la_panoramica") for s in tentativo.finalbody)
