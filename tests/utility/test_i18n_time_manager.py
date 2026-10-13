"""Le etichette del Time Manager in greco e portoghese erano mezze inglesi
(«Atlas Imprimir Período Tables», «Διακοπή print process»): si leggono
dai `.ts` e si controlla che non restino parole inglesi dentro una frase
tradotta (13 ottobre 2026)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
FRASI = ("Atlas Stampa Tavole Periodo", "Arresta processo stampa", "Absolute cronology system",
         "Relative cronology system", "Visualizza l'intervallo di tempo compreso tra l'anno:",
         "Cronologia iniziale", "Cronologia finale", "Visualizza", "Visualizza matrix")
INGLESE = ("Tables", "print process", "system", "Displays", "Initial", "Final", "chronology", "Relative")


def _traduzioni(lingua: str) -> dict:
    albero = ET.parse(_ROOT / "i18n" / ("pyarchinit_plugin_%s.ts" % lingua))
    fuori = {}
    for msg in albero.getroot().iter("message"):
        sorgente = msg.findtext("source") or ""
        trad = msg.find("translation")
        if sorgente in FRASI and trad is not None and trad.get("type") != "obsolete":
            fuori[sorgente] = (trad.text or "").strip()
    return fuori


@pytest.mark.parametrize("lingua", ["el_GR", "pt_PT"])
def test_le_etichette_del_time_manager_sono_tradotte_per_intero(lingua):
    tradotte = _traduzioni(lingua)
    assert set(tradotte) == set(FRASI), sorted(set(FRASI) - set(tradotte))
    for sorgente, testo in tradotte.items():
        assert testo and testo != sorgente, sorgente
        for parola in INGLESE:
            assert parola not in testo, (sorgente, testo)
