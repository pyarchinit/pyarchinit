"""I paradossi temporali anche nel «Controllo rapporti» della scheda US.

Nel plugin ci sono **due** verifiche dei rapporti, separate e senza codice
in comune: quella dentro la scheda US (`rapporti_stratigrafici_check`, che
riempie `listWidget_rapp`) e il pannello «Verifica rapporti» dentro il
dialogo dell'Extended Matrix.

Il pannello trovava i paradossi temporali; la scheda US no — controllava US
inesistenti, reciproci mancanti, aree vuote e rapporti incompleti, e i
periodi non li leggeva affatto. L'archeologo che apre la scheda US non ha
ragione di sapere che sono due controlli diversi, e infatti: «pur essendoci
paradossi temporali non vengono segnalati» (Enzo, 11 ottobre 2026).

Perché i test sono fatti così: `tabs/US_USM.py` non si importa sotto pytest
— costruisce troppo e il processo muore — quindi il comportamento si prova
sul modulo che fa il lavoro, e l'innesto nella scheda si legge dall'albero
sintattico. È lo stesso modo di `test_view_all_rollout.py`.
"""
from __future__ import annotations

import ast
import sqlite3
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

SORGENTE = RADICE / "tabs" / "US_USM.py"
PROVA = RADICE / "resources" / "dbfiles" / "pyarchinit_db_test.sqlite"


def _metodi() -> dict:
    albero = ast.parse(SORGENTE.read_text(encoding="utf-8"))
    fuori = {}
    for nodo in ast.walk(albero):
        if isinstance(nodo, ast.FunctionDef):
            fuori[nodo.name] = nodo
    return fuori


def test_la_scheda_us_ha_il_metodo_dei_paradossi():
    assert "paradossi_temporali" in _metodi()


def test_il_controllo_rapporti_lo_chiama():
    """Senza la chiamata il metodo esisterebbe e non direbbe niente a
    nessuno: è la riga che l'archeologo vede."""
    metodo = _metodi().get("rapporti_stratigrafici_check")
    assert metodo is not None
    chiamate = {
        nodo.func.attr for nodo in ast.walk(metodo)
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)}
    assert "paradossi_temporali" in chiamate


def test_i_paradossi_entrano_nel_conto_degli_errori():
    """Il riepilogo finale dice «trovati N errori»: un paradosso che non
    entra nel conto fa dire «nessun errore» a una scheda che ne ha uno."""
    testo = SORGENTE.read_text(encoding="utf-8")
    i = testo.index("paradossi = self.paradossi_temporali(")
    coda = testo[i:i + 400]
    assert "error_count += len(paradossi)" in coda, coda[:200]


def test_il_metodo_non_alza_mai():
    """Il «Controllo rapporti» deve dire quello che sa, non fallire per una
    verifica in più: il metodo cattura tutto e torna una lista vuota."""
    metodo = _metodi()["paradossi_temporali"]
    gestori = [n for n in ast.walk(metodo) if isinstance(n, ast.ExceptHandler)]
    assert gestori, "nessun except: un inciampo porterebbe via tutto il controllo"
    assert any(g.type is not None and getattr(g.type, "id", "") == "Exception"
               for g in gestori), [ast.dump(g.type) for g in gestori if g.type]


def test_il_metodo_riusa_temporal_check_invece_di_riscriverlo():
    """Due controlli scritti separatamente direbbero cose diverse alla prima
    divergenza."""
    metodo = _metodi()["paradossi_temporali"]
    sorgente = ast.unparse(metodo)
    assert "temporal_check" in sorgente
    assert "detect_temporal" in sorgente


def test_sul_db_di_prova_il_paradosso_c_e_davvero():
    """Il comportamento, non la struttura: il caso 8 del generatore — la US
    30 copre la 31 ma la sua fase finisce prima che cominci quella della
    31 — deve uscire come inversione."""
    if not PROVA.is_file():
        pytest.skip("manca il database di prova")
    # `ext_libs` davanti: la s3dgraphy vendorizzata sta là, e nelle
    # site-packages di QGIS ce n'è una 0.1.6 senza `s3dgraphy.sync`.
    ext = str(RADICE / "ext_libs")
    if ext in sys.path:
        sys.path.remove(ext)
    sys.path.insert(0, ext)
    pytest.importorskip("s3dgraphy.sync")
    from s3dgraphy.sync._db_handle import DbHandle

    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import temporal_check as TC

    sito = [r[0] for r in sqlite3.connect(PROVA).execute(
        "SELECT DISTINCT sito FROM us_table")][0]
    handle = DbHandle.from_path(PROVA)
    chrono = TC.build_chronology(handle, sito)
    periodi = TC.load_unit_periods(handle, sito)
    graph = GraphProjector().populate_graph("sqlite:///%s" % PROVA, sito=sito)
    issues = TC.detect_temporal(graph, chrono, periodi, sito=sito)
    inversioni = [i for i in issues if i.kind == TC.TEMPORAL_INVERSION]
    assert len(inversioni) == 1, [(i.kind, i.us_path) for i in issues]
    assert sorted(inversioni[0].us_path) == ["30", "31"], inversioni[0].us_path
