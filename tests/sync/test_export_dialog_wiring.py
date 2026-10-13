"""Chi legge un bottone deve essere la classe che quel bottone ce l'ha.

«Media: senza connessione al database: il pannello è stato aperto senza»,
e «in EMStudio non vedo i 4 saggi solo il primo e poi nemmeno si esporta
per sito intero» (Enzo, 12 ottobre 2026). Un sintomo solo, una causa
sola: due metodi stavano sulla classe sbagliata.

`modules/s3dgraphy/s3dgraphy_dot_bridge.py` tiene due classi. Il ponte
(`S3DGraphyDotBridge`) sa parlare col database; la finestra
(`S3DGraphyExportDialog`) ha i widget — i tre bottoni «Saggi» e il
bottone «Mostra matrice». `_scelta_saggi` leggeva i bottoni **dal
ponte**, che non li ha: `getattr(self, "rb_saggi_uno", None)` dava
`None`, la funzione tornava «automatico» e l'esportazione ignorava la
scelta (i due file uscivano identici al byte). `_connection_url` stava
anch'esso sul ponte, e la finestra lo chiamava su sé stessa: AttributeError
dentro un `except` larghissimo, connessione a `None`, e il pannello della
matrice si apriva senza database.

(I tre bottoni «Saggi» sono andati via il 13 ottobre 2026 — Emanuel:
l'em.json è un grafo per tutto il sito, la divisione per saggi era un
fraintendimento — e il test sui bottoni dice ora che non ci sono più.)

Nessuno dei due errori si vede leggendo il codice dall'alto, perché una
classe lunga 900 righe non si tiene in testa; si vedono contando. Questo
test conta: per ogni classe del file, **ogni `self._qualcosa()` che
chiama deve essere definito lì**. I nomi privati sono nostri — Qt non ne
eredita — quindi un nome che manca è un nome che manca davvero.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
PONTE = RADICE / "modules" / "s3dgraphy" / "s3dgraphy_dot_bridge.py"


def _classi(percorso: Path) -> dict:
    """Le classi del file: nome -> nodo, comprese quelle annidate in un
    `try:` di import (è lì che vive la finestra, perché Qt può mancare)."""
    albero = ast.parse(percorso.read_text(encoding="utf-8"))
    trovate = {}
    for nodo in ast.walk(albero):
        if isinstance(nodo, ast.ClassDef):
            trovate.setdefault(nodo.name, []).append(nodo)
    return trovate


def _definiti(classe: ast.ClassDef) -> set:
    return {f.name for f in classe.body
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _chiamati(classe: ast.ClassDef) -> set:
    """I `self._qualcosa()` che il corpo della classe chiama."""
    nomi = set()
    for nodo in ast.walk(classe):
        if not isinstance(nodo, ast.Call):
            continue
        f = nodo.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                and f.value.id == "self" and f.attr.startswith("_") \
                and not f.attr.startswith("__"):
            nomi.add(f.attr)
    return nomi


def _assegnati(classe: ast.ClassDef) -> set:
    """Gli attributi che la classe si crea addosso (`self.x = ...`)."""
    nomi = set()
    for nodo in ast.walk(classe):
        if not isinstance(nodo, (ast.Assign, ast.AnnAssign)):
            continue
        bersagli = nodo.targets if isinstance(nodo, ast.Assign) else [nodo.target]
        for b in bersagli:
            if isinstance(b, ast.Attribute) and isinstance(b.value, ast.Name) \
                    and b.value.id == "self":
                nomi.add(b.attr)
    return nomi


@pytest.fixture(scope="module")
def classi():
    return _classi(PONTE)


def _sola(classi, nome, con_definizioni=True):
    """La definizione «vera» di una classe: quella che ha dei metodi.

    La finestra compare due volte nel file — la seconda è il guscio vuoto
    del ramo «Qt non c'è»."""
    candidate = classi[nome]
    piene = [c for c in candidate if _definiti(c)]
    return (piene or candidate)[0] if con_definizioni else candidate[0]


def test_il_file_tiene_le_due_classi(classi):
    assert "S3DGraphyDotBridge" in classi
    assert "S3DGraphyExportDialog" in classi


@pytest.mark.parametrize("nome", ["S3DGraphyDotBridge", "S3DGraphyExportDialog"])
def test_ogni_metodo_privato_chiamato_e_definito_dove_viene_chiamato(classi, nome):
    classe = _sola(classi, nome)
    mancanti = sorted(_chiamati(classe) - _definiti(classe))
    assert mancanti == [], (
        "%s chiama metodi privati che non ha: %s. Se stanno su un'altra "
        "classe, l'AttributeError finisce in un `except` e il programma "
        "continua con un valore sbagliato." % (nome, mancanti))


def test_la_finestra_non_ha_piu_i_bottoni_dei_saggi(classi):
    """Emanuel (13 ottobre 2026): l'em.json è un grafo per tutto il sito;
    la divisione per saggi era un fraintendimento. I tre bottoni «Saggi» e
    chi li leggeva sono andati via insieme."""
    for nome in classi:
        c = _sola(classi, nome)
        assert not any(a.startswith("rb_saggi") for a in _assegnati(c)), nome
        assert "_scelta_saggi" not in _definiti(c), nome


def test_chi_apre_il_pannello_sa_la_connessione(classi):
    """`_on_show_matrix` passa la connessione al pannello: deve poterla
    chiedere a sé stesso, o il pannello si apre senza database."""
    apritori = [c.name for c in (_sola(classi, n) for n in classi)
                if "_on_show_matrix" in _definiti(c)]
    assert apritori == ["S3DGraphyExportDialog"], apritori
    finestra = _sola(classi, "S3DGraphyExportDialog")
    assert "_connection_url" in _definiti(finestra)


def test_l_esportazione_accetta_la_scelta_dei_saggi(classi):
    """`export_integrated_matrix(..., per_saggio=...)`: la scelta viaggia
    come parametro, non come lettura di un widget che non c'è."""
    ponte = _sola(classi, "S3DGraphyDotBridge")
    metodo = next(f for f in ponte.body
                  if isinstance(f, ast.FunctionDef)
                  and f.name == "export_integrated_matrix")
    argomenti = [a.arg for a in metodo.args.args] + \
                [a.arg for a in metodo.args.kwonlyargs]
    assert "per_saggio" in argomenti, argomenti


def test_la_finestra_esporta_un_grafo_solo(classi):
    """Il bottone «Esporta» chiede un grafo solo, e lo dice: `None`
    vorrebbe dire «automatico», che divide per saggi dove ci sono."""
    finestra = _sola(classi, "S3DGraphyExportDialog")
    chiamate = [n for n in ast.walk(finestra)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "export_integrated_matrix"]
    assert chiamate, "la finestra non chiama export_integrated_matrix"
    for chiamata in chiamate:
        chiavi = {k.arg: k.value for k in chiamata.keywords}
        assert "per_saggio" in chiavi, "una chiamata senza per_saggio"
        valore = chiavi["per_saggio"]
        assert isinstance(valore, ast.Constant) and valore.value is False, (
            "per_saggio deve essere False, esplicito: %s" % ast.dump(valore))
