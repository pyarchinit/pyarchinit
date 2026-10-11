"""Le voci di un vocabolario del thesaurus, chieste in un modo solo.

Le schede interrogano `pyarchinit_thesaurus_sigle` con
`{'nome_tabella': "'" + 'tomba_table' + "'", 'tipologia_sigla': ...}` e
mettono nel menu `sigla_estesa`. Il pezzo di codice che lo fa era copiato
decine di volte, e nelle copie si erano depositati tre difetti:

* `tabs/Tma.py` chiedeva **«TMA materiali archeologici»**, che non è un
  nome di tabella ma il nome **visualizzato**: la fonte è
  `TABLE_DISPLAY_MAPPING_I18N` in `tabs/Thesaurus.py`, e dice
  `tma_materiali_archeologici`. Lo stesso guasto dei 561 record del
  database di esempio, rinominati il 10 ottobre 2026;
* una copia pinzava `'lingua': "'it'"` **minuscolo** mentre il thesaurus
  tiene `IT`: quel menu non poteva riempirsi mai;
* nei database di chi usa pyArchInit da anni le righe col nome
  visualizzato ci sono per davvero, quindi chiedere solo il nome
  canonico svuoterebbe i menu che oggi funzionano.

Da qui un lettore solo, che prova il nome canonico, poi gli alias noti, e
tratta la lingua come la tratta il thesaurus.
"""
from __future__ import annotations

import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

from modules.utility.thesaurus_voci import voci_vocabolario  # noqa: E402


class _Riga:
    def __init__(self, sigla, estesa):
        self.sigla = sigla
        self.sigla_estesa = estesa


class _Manager:
    """Un db_manager finto: tiene le righe per chiave e registra le domande."""

    def __init__(self, righe):
        self.righe = righe          # (nome_tabella, sigla, lingua) -> [_Riga]
        self.domande = []

    def query_bool(self, search_dict, mapper):
        assert mapper == "PYARCHINIT_THESAURUS_SIGLE", mapper
        nudo = {k: str(v).strip().strip("'") for k, v in search_dict.items()}
        chiave = (nudo.get("nome_tabella"), nudo.get("tipologia_sigla"),
                  nudo.get("lingua", ""))
        self.domande.append(chiave)
        return list(self.righe.get(chiave, ()))


def test_il_nome_canonico_e_la_prima_domanda():
    m = _Manager({("tomba_table", "7.1", "IT"): [_Riga("FOS", "Fossa")]})
    assert voci_vocabolario(m, "tomba_table", "7.1", lingua="it") == ["Fossa"]
    assert m.domande[0] == ("tomba_table", "7.1", "IT")


def test_la_lingua_si_chiede_maiuscola():
    """Il thesaurus tiene `IT`: una copia chiedeva `it` e non trovava mai
    niente."""
    m = _Manager({("tomba_table", "7.1", "IT"): [_Riga("FOS", "Fossa")]})
    assert voci_vocabolario(m, "tomba_table", "7.1", lingua="it") == ["Fossa"]


def test_senza_lingua_si_chiede_senza_lingua():
    m = _Manager({("tomba_table", "7.1", ""): [_Riga("FOS", "Fossa")]})
    assert voci_vocabolario(m, "tomba_table", "7.1") == ["Fossa"]


def test_se_la_lingua_non_da_niente_si_riprova_senza():
    """Un database vecchio pu√≤ avere le voci senza lingua: meglio un menu
    pieno in una lingua sola che un menu vuoto."""
    m = _Manager({("us_table", "2.1", ""): [_Riga("STR", "Strato")]})
    assert voci_vocabolario(m, "us_table", "2.1", lingua="it") == ["Strato"]
    assert len(m.domande) == 2


def test_lalias_col_nome_visualizzato_si_prova_dopo():
    """Chi usa pyArchInit da anni ha le righe scritte col nome
    visualizzato: il menu non deve svuotarsi."""
    m = _Manager({("TMA materiali archeologici", "10.4", "IT"):
                  [_Riga("ETR", "Età etrusca")]})
    assert voci_vocabolario(m, "tma_materiali_archeologici", "10.4",
                            lingua="it") == ["Età etrusca"]


def test_il_canonico_vince_sullalias():
    m = _Manager({
        ("tma_materiali_archeologici", "10.4", "IT"): [_Riga("A", "canonico")],
        ("TMA materiali archeologici", "10.4", "IT"): [_Riga("B", "alias")],
    })
    assert voci_vocabolario(m, "tma_materiali_archeologici", "10.4",
                            lingua="it") == ["canonico"]


def test_le_voci_vuote_non_entrano_nel_menu():
    m = _Manager({("tomba_table", "7.1", "IT"):
                  [_Riga("", ""), _Riga("FOS", "Fossa"), _Riga("X", "   ")]})
    assert voci_vocabolario(m, "tomba_table", "7.1", lingua="it") == ["Fossa"]


def test_lordine_e_alfabetico_e_senza_doppioni():
    m = _Manager({("tomba_table", "7.1", "IT"): [
        _Riga("C", "Cassa"), _Riga("F", "Fossa"), _Riga("C2", "Cassa")]})
    assert voci_vocabolario(m, "tomba_table", "7.1",
                            lingua="it") == ["Cassa", "Fossa"]


def test_si_pu0_chiedere_la_sigla_invece_del_nome():
    """L'unità di misura dei reperti mostra `sigla` («nr», «g»), non
    `sigla_estesa`: lo fa `delegateUnMis`."""
    m = _Manager({("inventario_materiali_table", "3.10", "IT"): [
        _Riga("nr", "Numero"), _Riga("g", "Grammi")]})
    assert voci_vocabolario(m, "inventario_materiali_table", "3.10",
                            lingua="it", campo="sigla") == ["g", "nr"]


def test_un_vocabolario_che_non_esiste_da_una_lista_vuota():
    m = _Manager({})
    assert voci_vocabolario(m, "tomba_table", "7.99", lingua="it") == []


def test_un_manager_che_alza_non_fa_cadere_la_scheda():
    class Rotto:
        def query_bool(self, *a, **k):
            raise RuntimeError("niente connessione")

    assert voci_vocabolario(Rotto(), "tomba_table", "7.1") == []


def test_senza_manager_non_si_chiede_niente():
    assert voci_vocabolario(None, "tomba_table", "7.1") == []
    assert voci_vocabolario("", "tomba_table", "7.1") == []


# --------------------------------------------------------------------------
# La rete: nessuna scheda chieda il thesaurus con un nome visualizzato
# --------------------------------------------------------------------------

def test_nessuna_scheda_interroga_il_thesaurus_con_un_nome_visualizzato():
    """`nome_tabella` è un **nome di tabella**: minuscolo, senza spazi.

    I nomi visualizzati («TMA materiali archeologici», «Tomba») stanno in
    `TABLE_DISPLAY_MAPPING_I18N` e servono a riempire un menu, non a
    cercare: una query scritta con quelli non trova niente e il
    vocabolario esce vuoto. Era il guasto dei 561 record del database di
    esempio e delle sei query della TMA, e questo test lo tiene chiuso.
    """
    import re

    buono = re.compile(r"^[a-z][a-z0-9_]*$")
    # il valore di 'nome_tabella' quando è una costante scritta a mano
    letterale = re.compile(
        r"'nome_tabella':\s*(?:\"'\"\s*\+\s*)?'([^']+)'")
    colpevoli = []
    for sorgente in sorted((RADICE / "tabs").glob("*.py")):
        testo = sorgente.read_text(encoding="utf-8", errors="replace")
        for riga in testo.splitlines():
            m = letterale.search(riga)
            if m and not buono.match(m.group(1).strip()):
                colpevoli.append("%s: %s" % (sorgente.name, riga.strip()))
    assert colpevoli == [], colpevoli
