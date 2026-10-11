"""Le voci di un vocabolario del thesaurus, chieste in un modo solo.

Ogni menu a tendina delle schede viene da `pyarchinit_thesaurus_sigle`,
interrogata per **nome di tabella** e **sigla di tipologia**
(`{'nome_tabella': "'" + 'tomba_table' + "'", 'tipologia_sigla': "'" +
'7.1' + "'"}`), e mostra `sigla_estesa`. Il codice che lo fa era copiato
decine di volte nelle schede, e nelle copie si erano depositati tre
difetti:

* `tabs/Tma.py` chiedeva **«TMA materiali archeologici»**, che non è un
  nome di tabella ma il nome **visualizzato**. La fonte è
  `TABLE_DISPLAY_MAPPING_I18N` in `tabs/Thesaurus.py`, e dice
  `tma_materiali_archeologici`: è lo stesso guasto dei 561 record del
  database di esempio, scritti coi nomi visualizzati e rinominati il
  10 ottobre 2026.
* una copia pinzava `'lingua': "'it'"` **minuscolo** mentre il thesaurus
  tiene `IT`: quel menu non poteva riempirsi mai.
* nei database di chi usa pyArchInit da anni le righe col nome
  visualizzato esistono per davvero: chiedere soltanto il nome canonico
  svuoterebbe menu che oggi funzionano.

Quindi: si chiede il nome canonico, poi la stessa cosa senza vincolo di
lingua, poi gli alias noti. La prima risposta non vuota vince.
"""
from __future__ import annotations

#: I nomi **visualizzati** con cui lo stesso vocabolario può essere
#: scritto nei database esistenti. Non sono nomi di tabella: stanno qui
#: solo per non svuotare i menu di chi li ha.
_ALIAS = {
    "tma_materiali_archeologici": ("TMA materiali archeologici",
                                   "TMA Materiali Archeologici"),
    "tma_materiali_ripetibili": ("TMA Materiali Ripetibili",
                                 "TMA materiali ripetibili"),
}

#: Il mapper con cui `query_bool` nomina la tabella del thesaurus.
_MAPPER = "PYARCHINIT_THESAURUS_SIGLE"


def _virgolette(valore) -> str:
    """Il valore come lo vuole `query_bool`: tra apici.

    `_normalize_query_params` li accetta e li toglie, ma tutte le schede
    li mettono: scriverlo diverso qui vorrebbe dire due convenzioni.
    """
    return "'" + str(valore) + "'"


def voci_vocabolario(db_manager, tabella, sigla, *, lingua=None,
                     campo="sigla_estesa"):
    """Le voci del vocabolario `(tabella, sigla)`, in ordine, senza vuote.

    `campo` è quello che il menu mostra: `sigla_estesa` quasi sempre,
    `sigla` dove la scheda vuole il codice breve — l'unità di misura dei
    reperti mostra «nr» e «g», non «Num» e «Gra».

    La lingua si chiede **maiuscola**, com'è scritta nel thesaurus; se
    con quel vincolo non c'è niente si riprova senza, perché un menu
    pieno in una lingua sola è meglio di un menu vuoto.

    Ritorna sempre una lista: un database non raggiungibile o un
    vocabolario che non esiste danno `[]`, e la scheda si apre comunque.
    """
    if not db_manager:
        return []

    nomi = [str(tabella)]
    nomi.extend(_ALIAS.get(str(tabella), ()))

    tentativi = []
    for nome in nomi:
        if lingua:
            tentativi.append((nome, str(lingua).upper()))
        tentativi.append((nome, None))

    for nome, lang in tentativi:
        chiave = {"nome_tabella": _virgolette(nome),
                  "tipologia_sigla": _virgolette(sigla)}
        if lang:
            chiave["lingua"] = _virgolette(lang)
        try:
            righe = db_manager.query_bool(chiave, _MAPPER)
        except Exception:
            return []
        voci = []
        for riga in righe or ():
            valore = getattr(riga, campo, None)
            if valore is None:
                continue
            valore = str(valore).strip()
            if valore and valore not in voci:
                voci.append(valore)
        if voci:
            return sorted(voci)
    return []
