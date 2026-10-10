"""Gli avvisi cronologici di un sito, e le correzioni che li chiudono.

Puro: niente QGIS, niente widget, niente database dentro il giudizio. Prende
le righe della periodizzazione e delle US e restituisce ``Issue`` nella stessa
forma di :mod:`modules.utility.rapporti_check`, così l'albero, l'anteprima,
l'applica e l'annulla del dialogo «Verifica rapporti» non cambiano.

Gli avvisi che EMStudio mostra nel suo pannello Warnings **non vengono dalla
libreria**: ``graph.chronology(warnings=…)`` su questo sito ne emette zero.
Quel controllo è di EMStudio, e qui è scritto, non richiamato.

Vedi docs/superpowers/specs/2026-10-10-verifica-cronologia-design.md.
"""
from __future__ import annotations

from .rapporti_check import Edit, Issue, _t

#: Le categorie, con i nomi che il dialogo usa per raggrupparle.
EPOCH_OVERLAP = "epoch_overlap"              # manuale, proposta quando si può
EPOCH_REVERSED = "epoch_reversed"            # automatica
EPOCH_NO_DATES = "epoch_no_dates"            # solo segnalazione
DATAZIONE_MISMATCH = "datazione_mismatch"    # automatica

#: La tabella in cui atterrano le correzioni sulle fasi.
_PERIOD_TABLE = "periodizzazione_table"


def _year(val):
    """L'anno come intero, o ``None`` se la riga non ne porta uno leggibile.

    Un ``cron_iniziale`` a testo («XV sec») non è un errore da sollevare: è
    una fase senza anni, e la categoria ``epoch_no_dates`` lo dice. Lo zero è
    un anno come gli altri e il meno pure: le date a.C. si scrivono negative.
    Un float che è un anno intero (``1500.0``) vale quell'anno; ``1500.5`` no.
    """
    if val is None or isinstance(val, bool):
        return None
    testo = str(val).strip()
    try:
        return int(testo)
    except (TypeError, ValueError):
        pass
    # Un anno intero scritto come float — la colonna è `Integer` nello schema,
    # ma su un database che ha derivato torna come REAL, e trattare 1500.0 come
    # «nessun anno» farebbe sparire una fase vera dal confronto, in silenzio.
    try:
        numero = float(testo)
    except (TypeError, ValueError):
        return None
    return int(numero) if numero.is_integer() else None


def _key(row):
    """La chiave di una fase: sempre testo, mai numero.

    ``2.1`` e ``2.10`` sono fasi diverse, e come float sarebbero la stessa.
    """
    return (str(row.get("periodo") or "").strip(),
            str(row.get("fase") or "").strip())


def _label(key):
    """Come una fase si legge in un avviso."""
    periodo, fase = key
    return "%s/%s" % (periodo, fase) if fase else periodo


def _text(val):
    """Il testo di un campo, con ``None`` e ``''`` che dicono la stessa cosa."""
    return "" if val is None else str(val).strip()


def _period_target(key):
    return (_PERIOD_TABLE, {"periodo": key[0], "fase": key[1]})


def _no_dates(key, lang):
    return Issue(kind=EPOCH_NO_DATES, us_path=[_label(key)], auto=False,
                 summary=_t(lang, "s_epoch_no_dates").format(fase=_label(key)),
                 edits=[])


def _reversed_issue(key, ini, fin, lang):
    """Inizio dopo la fine: i due anni si scambiano, altra lettura non c'è."""
    return Issue(
        kind=EPOCH_REVERSED, us_path=[_label(key)], auto=True,
        summary=_t(lang, "s_epoch_reversed").format(
            fase=_label(key), ini=ini, fin=fin),
        edits=[Edit(us=_label(key),
                    set_fields=(("cron_iniziale", fin), ("cron_finale", ini)),
                    target=_period_target(key))])


def _overlaps(spans, lang):
    """Le coppie di fasi i cui intervalli si intersecano, una per coppia.

    La proposta alza **l'inizio della più recente** all'anno dopo la fine
    della più antica: è la fase che comincia più tardi quella che cede, così
    la più antica resta come l'ha scavata chi l'ha scavata.

    Quando l'alzata lascerebbe un intervallo vuoto o rovesciato — due fasi con
    lo **stesso** intervallo, che sono tutte e venti quelle del database di
    esempio — la proposta non si fa: non esiste un restringimento dell'una o
    dell'altra che non produca una riga impossibile, e scegliere chi si sposta
    lo sa solo chi ha scavato. L'avviso resta, senza correzione.
    """
    out = []
    ordered = sorted(spans.items(), key=lambda kv: (kv[1][0], kv[1][1], kv[0]))
    for i, (key_a, (ini_a, fin_a)) in enumerate(ordered):
        for key_b, (ini_b, fin_b) in ordered[i + 1:]:
            if ini_b > fin_a:
                # Ordinate per inizio: le successive cominciano ancora più
                # tardi, quindi nessuna delle rimanenti tocca questa.
                break
            nuovo_inizio = fin_a + 1
            proposta = []
            if nuovo_inizio <= fin_b:
                proposta = [Edit(us=_label(key_b),
                                 set_fields=(("cron_iniziale", nuovo_inizio),),
                                 target=_period_target(key_b))]
            out.append(Issue(
                kind=EPOCH_OVERLAP, us_path=[_label(key_a), _label(key_b)],
                auto=False,
                summary=_t(lang, "s_epoch_overlap").format(
                    a=_label(key_a), b=_label(key_b),
                    anni=min(fin_a, fin_b) - max(ini_a, ini_b) + 1,
                    ini=max(ini_a, ini_b), fin=min(fin_a, fin_b)),
                edits=proposta))
    return out


def check_chronology(periods, units, *, sito, lang="it"):
    """Gli avvisi cronologici del sito.

    ``periods``: righe di ``periodizzazione_table`` come dizionari, con
    ``periodo``, ``fase``, ``cron_iniziale``, ``cron_finale``,
    ``datazione_estesa``.
    ``units``: righe di ``us_table`` con ``us``, ``periodo_iniziale``,
    ``fase_iniziale``, ``datazione``.

    Una periodizzazione assente o vuota non è un errore: nessuna issue, e la
    verifica dei rapporti continua per conto suo.
    """
    issues = []
    spans = {}
    for row in periods:
        key = _key(row)
        ini, fin = _year(row.get("cron_iniziale")), _year(row.get("cron_finale"))
        if ini is None or fin is None:
            issues.append(_no_dates(key, lang))
            continue
        if ini > fin:
            # Fuori dalle sovrapposizioni: un intervallo rovesciato non si
            # interseca con niente in modo sensato. Si corregge, e la verifica
            # che segue l'applicazione lo guarda da capo.
            issues.append(_reversed_issue(key, ini, fin, lang))
            continue
        spans[key] = (ini, fin)
    issues.extend(_overlaps(spans, lang))
    return issues
