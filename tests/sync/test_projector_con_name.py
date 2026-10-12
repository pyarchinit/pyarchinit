"""«1.CONCON_12»: la sigla letta due volte nel nome della continuità.

Il generatore chiama la scheda `us='CON_12'` con `unita_tipo='CON'` — il
codice è la sua chiave di idempotenza, e un `us='12'` sarebbe ambiguo nei
rapporti con la USM 12 — ma il modello del nome, `{area}.{unita_tipo}{us}`,
legge il prefisso due volte. Il nome si ripulisce nel projector, la chiave
non si tocca.
"""
from __future__ import annotations

import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

from modules.s3dgraphy.sync.graph_projector import nome_senza_prefisso_doppio  # noqa: E402


def test_the_generated_continuity_reads_like_a_hand_made_one():
    assert nome_senza_prefisso_doppio("1.CONCON_12", "CON", "CON_12") == "1.CON12"


def test_a_hand_made_continuity_is_left_alone():
    assert nome_senza_prefisso_doppio("1.CON500", "CON", "500") == "1.CON500"


def test_a_unit_whose_code_merely_starts_with_the_letters_is_left_alone():
    """`USM12` con sigla «US»: comincia con le lettere, ma senza il
    trattino basso non è un prefisso ripetuto."""
    assert nome_senza_prefisso_doppio("1.USUSM12", "US", "USM12") == "1.USUSM12"
    assert nome_senza_prefisso_doppio("1.US12", "US", "12") == "1.US12"


def test_an_empty_piece_changes_nothing():
    assert nome_senza_prefisso_doppio("", "CON", "CON_12") == ""
    assert nome_senza_prefisso_doppio("1.CONCON_12", "", "CON_12") == "1.CONCON_12"
