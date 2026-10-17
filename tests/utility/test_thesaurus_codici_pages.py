"""Le pagine dei codici del thesaurus dicono quello che fanno le schede
(verifica del 17 ottobre 2026, dalle incongruenze trovate da graphify).

* La scheda Thesaurus apriva solo sette lingue: le pagine in greco,
  portoghese e rumeno c'erano, ma chi usa quelle lingue vedeva l'inglese.
* Le etichette di alcuni codici non erano quelle del campo che il codice
  riempie: 3.1 è il tipo del reperto (`comboBox_tipo_reperto`), non la classe
  del materiale; 10.3 è la località, 10.2 la tipologia della collocazione
  (LDCT); 9.2 la sorgente, non la scala; 7.8 l'area, non il periodo.
* I codici che le schede usano e le pagine non elencavano: 2.20–2.43,
  11.12–11.16, 12.7.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
TABS = PLUGIN_ROOT / "tabs"
PAGINE = sorted(TABS.glob("codici_*.html"))
LINGUE = [p.stem.split("_", 1)[1] for p in PAGINE]


def _righe(pagina: Path) -> dict:
    testo = pagina.read_text(encoding="utf-8")
    return {c: e for c, e in re.findall(
        r'<span class="code">(\d+\.\d+)</span></td>\s*<td>(.*?)</td>', testo)}


def test_ogni_pagina_dei_codici_si_apre_nella_sua_lingua():
    testo = (TABS / "Thesaurus.py").read_text(encoding="utf-8")
    blocco = testo[testo.index("lang_files = {"):]
    blocco = blocco[:blocco.index("}")]
    for lingua in LINGUE:
        assert "'%s': 'codici_%s.html'" % (lingua, lingua) in blocco, lingua
    assert len(LINGUE) == 10


@pytest.mark.parametrize("pagina", PAGINE, ids=LINGUE)
def test_ogni_pagina_elenca_i_codici_che_le_schede_usano(pagina):
    codici = set(_righe(pagina))
    attesi = ({"1.%d" % n for n in range(1, 6)}          # i toponimi del sito (17-10-2026)
              | {"2.%d" % n for n in range(1, 44)} | {"11.%d" % n for n in range(1, 17)}
              | {"12.%d" % n for n in range(1, 8)} | {"3.1", "3.2", "3.3", "3.11", "7.2", "7.7", "7.8",
                                                       "9.2", "10.2", "10.3", "10.4", "10.5", "10.6",
                                                       "10.12", "10.15"})
    assert attesi - codici == set()


def test_le_etichette_italiane_sono_quelle_dei_campi():
    righe = _righe(TABS / "codici_it.html")
    attese = {
        "3.1": "Tipo reperto", "3.2": "Classe materiale", "3.3": "Definizione", "3.11": "Area",
        "7.2": "Stato di conservazione", "7.7": "Sepoltura", "7.8": "Area", "9.2": "Sorgente",
        "10.2": "Tipologia collocazione (LDCT)", "10.3": "Località",
        "10.4": "Fascia cronologica (DTZG)", "10.5": "Tipo di intervento (SCAN)",
        "10.6": "Tipo di acquisizione (AINT)", "10.12": "Precisazione tipologica", "10.15": "Settore",
    }
    assert {c: righe.get(c) for c in attese} == attese


@pytest.mark.parametrize("pagina", PAGINE, ids=LINGUE)
def test_nessun_refuso_dopo_il_tag_html(pagina):
    seconda = pagina.read_text(encoding="utf-8").splitlines()[1]
    assert re.fullmatch(r'\s*<html lang="[a-z]{2}"( dir="rtl")?>\s*', seconda), seconda
