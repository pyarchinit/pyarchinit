"""La rete contro la deriva fra la nostra copia e quella della libreria.

`modules/s3dgraphy/sync/graph_ingestor.py` e `…/graph_projector.py` sono
nostri — sottoclassi e adattamenti, non specchi: divergono di centinaia e
migliaia di righe, e va bene così. Ma **un** pezzo deve coincidere: l'elenco
dei tipi di nodo che non hanno una riga in `us_table`.

Perché proprio quello. L'11 ottobre 2026 la dev44 ha cominciato a far
dichiarare a ogni grafo proiettato il proprio studio (`hdto.declare_hdto`).
La libreria aveva già messo i quattro tipi della catena HDT-O nel suo
`_NON_STRAT_TYPES`; la nostra copia no, così lo `StudyNode` — che non porta
attributi, quindi `us` ricadeva sul nome del nodo, cioè il nome del sito —
veniva **scritto** in `us_table` come un'US fantasma (`us` = nome del sito,
`unita_tipo` 'US', `d_stratigrafica` vuota), visibile nella scheda, nella
matrice e in ogni esportazione. Una riga per importazione.

Un test di uguaglianza fra i due insiemi se ne accorge al primo
aggiornamento della libreria, invece che dopo — quando le righe fantasma
sono già nei database di qualcuno.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


RADICE = Path(__file__).resolve().parents[2]
NOSTRO = RADICE / "modules" / "s3dgraphy" / "sync" / "graph_ingestor.py"
LIBRERIA = RADICE / "ext_libs" / "s3dgraphy" / "sync" / "graph_ingestor.py"


def _tipi(percorso: Path) -> set:
    """Il contenuto di `_NON_STRAT_TYPES`, letto dall'albero sintattico.

    Si legge il sorgente invece di importare i due moduli: importarli
    entrambi nello stesso processo vuol dire caricare due `s3dgraphy`, e
    quale dei due vince dipende da `sys.path` — esattamente l'ambiguita che
    questo test deve misurare, non subire.
    """
    albero = ast.parse(percorso.read_text(encoding="utf-8"))
    for nodo in ast.walk(albero):
        obiettivi = ([nodo.target] if isinstance(nodo, ast.AnnAssign)
                     else getattr(nodo, "targets", []))
        if any(getattr(t, "id", None) == "_NON_STRAT_TYPES"
               for t in obiettivi):
            # `frozenset({...})`: l'insieme e il primo argomento
            return {e.value for e in nodo.value.args[0].elts}
    raise AssertionError("_NON_STRAT_TYPES non trovato in %s" % percorso)


def test_i_due_elenchi_dei_tipi_non_stratigrafici_coincidono():
    """Un tipo che la libreria salta e noi no finisce in `us_table`."""
    if not LIBRERIA.exists():
        pytest.skip("s3dgraphy non vendorizzata in ext_libs")
    nostri, loro = _tipi(NOSTRO), _tipi(LIBRERIA)
    assert nostri == loro, (
        "i due `_NON_STRAT_TYPES` non coincidono.\n"
        "  solo da noi    : %s\n"
        "  solo in libreria: %s\n"
        "Un tipo presente solo in libreria viene scritto in us_table da noi: "
        "e' il guasto dell'US fantasma dello StudyNode (dev44)."
        % (sorted(nostri - loro), sorted(loro - nostri)))


def test_la_catena_hdto_e_in_elenco():
    """I quattro tipi della catena HDT-O, nominati.

    L'uguaglianza qui sopra cade anche se **entrambi** gli elenchi li
    perdono; questo no. Uno studio, un bene, un gemello digitale e un
    progetto non sono unita stratigrafiche, e in `us_table` non hanno ne'
    una riga ne' un `unita_tipo` che gli somigli.
    """
    nostri = _tipi(NOSTRO)
    for tipo in ("StudyNode", "HeritageEntityNode", "HDTNode", "ProjectNode"):
        assert tipo in nostri, tipo
