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


def edit_prefix(edit):
    """Chi tocca una correzione, come si legge nell'anteprima.

    Una correzione sulla periodizzazione non riguarda una US: scrivere
    «US 2/2.2» mentirebbe sulla riga che si sta per cambiare.
    """
    target = getattr(edit, "target", ()) or ()
    if not target:
        return "US %s" % edit.us
    chiave = dict(target[1]) if len(target) > 1 else {}
    return "%s %s" % (target[0], " ".join("%s=%s" % (k, chiave[k])
                                          for k in sorted(chiave)))


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


def _mismatches(periods, units, lang):
    """Le schede la cui ``datazione`` non dice quello che dice la loro fase.

    La periodizzazione è la fonte e la scheda la copia — Enzo, 2026-10-10:
    «in US c'è il campo datazione che legge dalla table periodizzazione a
    seconda del periodo e fase» — quindi riscrivere la copia dalla fonte non
    ha alternative, ed è automatica.

    Tre righe non entrano: una US **senza** periodo, perché non c'è fonte; una
    US che punta a una fase che non esiste, per lo stesso motivo; e una fase
    con la ``datazione_estesa`` vuota, perché non si cancella una scheda piena
    in nome di una fonte che non dice niente.
    """
    atteso = {_key(r): _text(r.get("datazione_estesa")) for r in periods}
    out = []
    for row in units:
        key = (str(row.get("periodo_iniziale") or "").strip(),
               str(row.get("fase_iniziale") or "").strip())
        voluto = atteso.get(key, "")
        if not key[0] or not voluto:
            continue
        corrente = _text(row.get("datazione"))
        if corrente == voluto:
            continue
        us = str(row.get("us") or "").strip()
        out.append(Issue(
            kind=DATAZIONE_MISMATCH, us_path=[us], auto=True,
            summary=_t(lang, "s_datazione_mismatch").format(
                us=us, fase=_label(key), corrente=corrente or "—",
                atteso=voluto),
            edits=[Edit(us=us, set_fields=(("datazione", voluto),))]))
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
    issues.extend(_mismatches(periods, units, lang))
    return issues


def load_chronology_rows(handle, sito):
    """Le righe che :func:`check_chronology` giudica, di un sito solo.

    Due liste di dizionari e non un oggetto: il giudizio non deve sapere da
    dove vengono, ed è questo che lo rende provabile senza database. Il filtro
    per sito non è un'ottimizzazione — senza, le due sovrapposizioni di un
    sito diventano le venti del database, e la correzione automatica
    riscriverebbe dieci siti in un colpo.
    """
    from sqlalchemy import text
    with handle.engine.connect() as conn:
        periods = [
            {"periodo": r[0], "fase": r[1], "cron_iniziale": r[2],
             "cron_finale": r[3], "datazione_estesa": r[4]}
            for r in conn.execute(text(
                "SELECT periodo, fase, cron_iniziale, cron_finale, "
                "datazione_estesa FROM periodizzazione_table "
                "WHERE sito = :s"), {"s": sito}).fetchall()]
        units = [
            {"us": r[0], "periodo_iniziale": r[1], "fase_iniziale": r[2],
             "datazione": r[3]}
            for r in conn.execute(text(
                "SELECT us, periodo_iniziale, fase_iniziale, datazione "
                "FROM us_table WHERE sito = :s"), {"s": sito}).fetchall()]
    return periods, units


#: Come si chiamano in chiaro le cinque regole di ``graph.chronology()``.
#: Stanno qui e non in ``_L`` perché sono i nomi delle regole della
#: libreria, non voci del dialogo: ``tpq`` e ``taq`` non si traducono.
_RULES = {
    "it": {"written": "data scritta", "epoch": "epoca",
           "contained": "da ciò che contiene",
           "tpq": "terminus post quem", "taq": "terminus ante quem"},
    "en": {"written": "written date", "epoch": "epoch",
           "contained": "from what it contains",
           "tpq": "terminus post quem", "taq": "terminus ante quem"},
    "de": {"written": "geschriebenes Datum", "epoch": "Epoche",
           "contained": "aus dem Enthaltenen",
           "tpq": "terminus post quem", "taq": "terminus ante quem"},
    "es": {"written": "fecha escrita", "epoch": "época",
           "contained": "de lo que contiene",
           "tpq": "terminus post quem", "taq": "terminus ante quem"},
    "fr": {"written": "date écrite", "epoch": "époque",
           "contained": "de ce qu'elle contient",
           "tpq": "terminus post quem", "taq": "terminus ante quem"},
    "pt": {"written": "data escrita", "epoch": "época",
           "contained": "do que contém",
           "tpq": "terminus post quem", "taq": "terminus ante quem"},
}


#: Come si nominano i due estremi, quando vengono da relazioni diverse e
#: bisogna dire quale è quale.
_LATI = {
    "it": ("inizio", "fine"),
    "en": ("start", "end"),
    "de": ("Beginn", "Ende"),
    "es": ("inicio", "fin"),
    "fr": ("début", "fin"),
    "pt": ("início", "fim"),
}


def _anno(val):
    """L'anno come si scrive in un avviso: senza il decimale che non dice
    niente (``chronology()`` restituisce float)."""
    return "…" if val is None else "%d" % int(val)


def explain_bounds(entry, *, lang="it"):
    """Gli estremi di una voce di ``graph.chronology()``, con la regola che li
    ha prodotti e la provenienza.

    ``1500–1549 · epoca · has_first_epoch → epoch_2_2``: cioè l'intervallo, da
    quale regola viene e lungo quale arco è arrivato il vincolo, da quale
    nodo. La provenienza di una data **è la relazione che ha percorso** (E. D.,
    29 settembre 2026), e qui si legge.

    Niente colonne nuove, nessuna scrittura: si ricalcola a ogni verifica, e
    costa poco perché il grafo si sta già proiettando per i rapporti. Una voce
    senza estremi non è un errore: dà la riga vuota.
    """
    entry = entry or {}
    inizio, fine = entry.get("start"), entry.get("end")
    if inizio is None and fine is None:
        return ""
    regola = entry.get("rule") or ""
    nomi = _RULES.get(lang) or _RULES["en"]
    pezzi = ["%s–%s" % (_anno(inizio), _anno(fine))]
    if regola:
        pezzi.append(nomi.get(regola, regola))
    da_inizio = _provenienza(entry, "start")
    da_fine = _provenienza(entry, "end")
    if inizio is None or fine is None or da_inizio == da_fine:
        # Un estremo solo, o due estremi che vengono dalla stessa relazione:
        # dirlo due volte sarebbe rumore.
        provenienza = da_inizio or da_fine
        if provenienza:
            pezzi.append(provenienza)
    else:
        # I due estremi arrivano per strade diverse, e allora si dice quale è
        # quale: una data attribuita alla relazione sbagliata è peggio di
        # nessuna data.
        etichette = _LATI.get(lang) or _LATI["en"]
        for etichetta, provenienza in zip(etichette, (da_inizio, da_fine)):
            if provenienza:
                pezzi.append("%s %s" % (etichetta, provenienza))
    return " · ".join(pezzi)


def _provenienza(entry, lato):
    """L'arco percorso e il nodo da cui il vincolo è arrivato, per un estremo.

    La provenienza di una data **è la relazione che ha percorso** (E. D.,
    29 settembre 2026): non un campo scritto da qualche parte, ma l'arco del
    grafo lungo cui il vincolo si è propagato.
    """
    relazione = entry.get("%s_relation" % lato)
    sorgente = entry.get("%s_source" % lato)
    if not (relazione and sorgente):
        return ""
    return "%s → %s" % (relazione, sorgente)


def bounds_by_us(graph):
    """La cronologia calcolata, indicizzata per numero di US.

    ``graph.chronology()`` ha per chiave l'id del nodo, che è un uuid7: per
    accostarla a un avviso — che nomina le unità per numero — serve lo stesso
    modo in cui la verifica dei rapporti riconosce una unità, cioè l'attributo
    ``us`` del nodo, o il suo nome ripulito del prefisso.
    """
    from .rapporti_check import _us_of

    per_us = {}
    for node_id, voce in (graph.chronology() or {}).items():
        us = _us_of(graph.find_node_by_id(node_id))
        if us:
            per_us[str(us)] = voce
    return per_us
