"""Stratigraphic-rapporti validation + conservative auto-fix (pyArchInit).

Qt-free application logic. Builds the site graph with GraphProjector, runs
s3dgraphy's validators (cycle detection + connection legality) plus a
reciprocity scan derived from the same stratigraphic edges, and emits
``Issue`` objects each carrying the exact ``rapporti``-column edits for its
fix. See docs/superpowers/specs/2026-06-06-rapporti-validation-autofix-design.md.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from s3dgraphy.rapporti import (
    NON_RAPPORTI_EDGE_TYPES,
    RAPPORTI_TO_EDGE_TYPE,
    _REL_INDEX_EDGE_TYPE,
    _coerce_to_list,
    strip_us_prefix,
)

# Issue kinds
SELF_LOOP = "self_loop"
MISSING_RECIPROCITY = "missing_reciprocity"
CONTRADICTION_REDUNDANT = "contradiction_redundant"   # auto
CONTRADICTION_AMBIGUOUS = "contradiction_ambiguous"   # manual
CYCLE = "cycle"                                        # manual
ILLEGAL_CONNECTION = "illegal_connection"             # report-only

#: Canonical edge-type inverse. Symmetric relations map to themselves.
_EDGE_TYPE_INVERSE = {
    "overlies": "is_overlain_by", "is_overlain_by": "overlies",
    "cuts": "is_cut_by", "is_cut_by": "cuts",
    "fills": "is_filled_by", "is_filled_by": "fills",
    "abuts": "is_abutted_by", "is_abutted_by": "abuts",
    "is_physically_equal_to": "is_physically_equal_to",
    "is_bonded_to": "is_bonded_to",
    # canonical spellings since s3dgraphy 2026-09-27 (the old ones stay
    # readable as spelling_of in the datamodel)
    "equals": "equals",
    "bonded_to": "bonded_to",
}


@dataclass(frozen=True)
class Edit:
    """One change to a single row. ``add``/``remove`` hold
    ``(label, target_us, area, sito)`` rapporti 4-tuples; ``set_fields`` holds
    ``(column, value)`` pairs for non-rapporti columns (e.g. period fields).

    ``target`` dice **in quale tabella** e **con quale chiave**: per la
    periodizzazione ``("periodizzazione_table", {"periodo": "2",
    "fase": "2.2"})``. Vuoto vale ``us_table`` con la chiave ``us``, cioè
    esattamente quello che ``apply_edits`` ha sempre fatto — nessuna chiamata
    esistente cambia.

    Su ``us_table`` la chiave buona è di **quattro** colonne —
    ``{"us": …, "area": …, "unita_tipo": …}`` più il sito, che
    ``apply_edits`` riceve a parte: è ``UniqueConstraint('sito', 'area',
    'us', 'unita_tipo')`` (modules/db/structures/US_table.py). La sola ``us``
    individua più righe su uno scavo a più aree, e ``apply_edits`` lo rifiuta
    invece di riscriverle tutte.
    """
    us: str
    add: tuple = ()
    remove: tuple = ()
    set_fields: tuple = ()
    target: tuple = ()


@dataclass
class Issue:
    """Un problema, le US che nomina e la correzione che lo chiude.

    ``rows`` dice **quali righe** di ``us_table`` sono le US di ``us_path``,
    posizione per posizione: ``{"us": …, "area": …, "unita_tipo": …}``, la
    stessa forma che ``Edit.target`` porta e che ``chronology_check._us_target``
    costruisce. Il numero di US da solo non nomina una riga —
    ``UniqueConstraint('sito', 'area', 'us', 'unita_tipo')`` — e una
    correzione su una chiave ambigua `apply_edits` la rifiuta.

    Un elemento vale ``None`` quando la riga non si sa nominare (il numero ne
    individua più di una e nessuna area aiuta a scegliere): lì si segnala e
    non si propone niente.

    La lista **vuota** è il valore di sempre, e vuol dire «righe non
    nominate»: la portano gli avvisi sulle fasi di :mod:`chronology_check`,
    che non riguardano righe di ``us_table``, e qualunque chiamata scritta
    prima che questo campo esistesse. Chi la trova vuota si comporta come
    prima — la correzione tiene la chiave `us` e nient'altro.
    """
    kind: str
    us_path: list           # involved US numbers (1=self-loop, 2=contradiction, N=cycle)
    auto: bool              # True when the fix is unambiguous
    summary: str
    edits: list = field(default_factory=list)   # the fix (auto) OR suggested (manual)
    rows: list = field(default_factory=list)    # chiavi di riga, allineate a us_path


@dataclass
class RapportiReport:
    sito: str
    issues: list = field(default_factory=list)


def _us_of(node):
    if node is None:
        return None
    a = getattr(node, "attributes", None) or {}
    return a.get("us") or strip_us_prefix(str(getattr(node, "name", "") or ""))


def _real_us(node):
    """STRICT real-US identity: the ``us`` attribute set by GraphProjector for
    an actual us_table row. Returns ``None`` for projector-synthesized
    placeholder nodes (e.g. ``_synth_BR_654`` targets, group/epoch nodes),
    which carry ``us=None`` — those must NOT drive a DB-writing fix."""
    if node is None:
        return None
    a = getattr(node, "attributes", None) or {}
    us = a.get("us")
    if us is None or str(us).strip() == "" or str(us).startswith("_synth"):
        return None
    return str(us)


def _txt(val):
    """Il testo di un campo, con ``None`` e ``''`` che dicono la stessa cosa.

    La stessa normalizzazione di ``chronology_check._text`` e di :func:`_where`
    (``TRIM(COALESCE(CAST(… AS TEXT), ''))``): le due sponde di una chiave
    devono dire la stessa cosa, o la riga non si trova e la finestra direbbe
    di averla corretta. È riscritta qui e non importata perché
    ``chronology_check`` importa da questo modulo, e un import all'indietro
    chiuderebbe il cerchio.
    """
    return "" if val is None else str(val).strip()


def _row_key(node):
    """La riga di ``us_table`` che un nodo rappresenta, o ``None``.

    Tre colonne più il sito, che :func:`apply_edits` riceve a parte:
    ``UniqueConstraint('sito', 'area', 'us', 'unita_tipo')``
    (modules/db/structures/US_table.py). Un segnaposto sintetizzato dal
    projector (``us=None``) non ha una riga, quindi non ne ha nemmeno una
    chiave: e senza riga non si scrive niente.
    """
    us = _real_us(node)
    if us is None:
        return None
    a = getattr(node, "attributes", None) or {}
    return (_txt(us), _txt(a.get("area")), _txt(a.get("unita_tipo")))


def _as_row(chiave):
    """La chiave di riga come la porta ``Issue.rows``: un dizionario, o
    ``None`` quando la riga non si sa nominare."""
    if chiave is None:
        return None
    us, area, unita_tipo = chiave
    return {"us": us, "area": area, "unita_tipo": unita_tipo}


def _key_of_row(riga):
    """La chiave a tre colonne di una ``Issue.rows``, per ritrovarne il nodo."""
    if not riga:
        return None
    return (_txt(riga.get("us")), _txt(riga.get("area")),
            _txt(riga.get("unita_tipo")))


def _target_of_row(riga):
    """Il ``target`` di una ``Edit`` che deve toccare quella riga.

    Una riga non nominata dà ``()``, cioè la chiave `us` e nient'altro: è
    quello che ``apply_edits`` ha sempre fatto, e che una issue senza ``rows``
    continua ad avere.
    """
    return ("us_table", dict(riga)) if riga else ()


def _index_rows(graph):
    """Le righe di ``us_table`` che il grafo rappresenta.

    Restituisce ``(per_chiave, per_us)``: la chiave a tre colonne → il nodo, e
    il numero di US → le chiavi che lo portano. Più di una quando lo scavo ha
    più aree, o quando una US e una USM si chiamano con lo stesso numero —
    che il vincolo permette.
    """
    per_chiave, per_us = {}, {}
    for n in getattr(graph, "nodes", None) or []:
        k = _row_key(n)
        if k is None:
            continue
        per_chiave.setdefault(k, n)
        chiavi = per_us.setdefault(k[0], [])
        if k not in chiavi:
            chiavi.append(k)
    return per_chiave, per_us


def _named_rows(us, area_scritta, area_scrittore, per_us):
    """Le righe che una voce di ``rapporti`` può nominare.

    Una voce è ``[rapporto, us, area, sito]``, e quell'area è **quella del
    contraente**: ``['Copre', '9', '2', 'Sito']`` dice «copro la US 9
    dell'area 2».

    La forma corta ``['Copre', '9']`` l'area non la dice, e allora si assume
    quella della **scheda che l'ha scritta**. È quello che il plugin stesso ci
    scrive quando espande la forma corta: ``US_USM.update_rapporti_col`` gira
    area per area e appende ``[area, sito]`` dell'area in lavorazione. Ed è
    l'unica lettura sotto cui uno scavo a più aree si possa verificare: la
    stratigrafia si osserva dentro un'area, e un rapporto che esce dall'area
    lo dice scrivendola.

    **Un candidato solo e non si disambigua niente**, ed è il caso di ogni
    scavo a un'area sola — tutte e 510 le righe del database di esempio, e
    tutto quello che la suite copre: lì questa funzione restituisce quello che
    il controllo ha sempre restituito, e l'area non entra in gioco. L'area
    decide soltanto quando il numero di US da solo nomina più di una riga.

    Se nessuna riga sta nell'area chiesta decide il numero: l'area di una voce
    è un dato denormalizzato che il plugin riscrive da sé (Ctrl+U) e può
    essere vecchia, e andare in silenzio sarebbe peggio che leggerla come un
    suggerimento. Se restano più righe la voce è ambigua — il tipo di unità
    una voce non lo dice mai — e allora il reciproco si riconosce comunque
    (indulgenti nel leggere) ma non si propone nessuna correzione, perché non
    si saprebbe quale riga scrivere.
    """
    cand = per_us.get(us) or []
    if len(cand) <= 1:
        return cand
    for preferita in (area_scritta, area_scrittore):
        if preferita:
            stessa = [k for k in cand if k[1] == preferita]
            if stessa:
                return stessa
    return cand


def _strat_edges(graph):
    out = []
    for e in getattr(graph, "edges", None) or []:
        et = getattr(e, "edge_type", None)
        if not et or et in NON_RAPPORTI_EDGE_TYPES:
            continue
        s = getattr(e, "edge_source", None)
        t = getattr(e, "edge_target", None)
        if s and t:
            out.append((s, t, et))
    return out


# ---------------------------------------------------------------------------
# Localisation (report messages follow the QGIS UI language)
# ---------------------------------------------------------------------------
# Relationship WORDS come from pyArchInit's i18n RELATIONSHIPS table (all 10
# languages). The surrounding template phrases are provided for the Latin-
# script UI languages; any other language falls back to English (the
# relationship words stay localised regardless).
_EDGE_TYPE_TO_REL_INDEX = {et: i for i, et in enumerate(_REL_INDEX_EDGE_TYPE)}

_L = {
    "it": {
        "t_self_loop": "Self-loop (US in relazione con sé stessa)",
        "t_missing_reciprocity": "Reciprocità mancante (verrà creata)",
        "t_contradiction_redundant": "Contraddizione ridondante",
        "t_contradiction_ambiguous": "Contraddizione diretta (scelta manuale)",
        "t_cycle": "Ciclo stratigrafico (scelta manuale)",
        "t_illegal_connection": "Tipo relazione non valido (solo segnalazione)",
        "t_temporal_inversion": "Paradosso temporale (inversione di periodo)",
        "t_temporal_contemporaneity": "Paradosso temporale (contemporaneità non sovrapposta)",
        "t_temporal_unevaluable": "Coerenza temporale non valutabile (periodo mancante)",
        "s_self": "{us} è in relazione con sé stessa",
        "s_recip": "Manca il reciproco su {b} per {a} (rapporto «{rel}»)",
        "s_contr": "Contraddizione: {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— tieni una sola direzione, elimina l'altra",
        "s_cycle": "Ciclo: {chain} — spezza l'anello eliminando il rapporto errato",
        "s_illegal": "Tipo relazione non valido: {a} → {b}",
        "s_temporal_inv": "{a} (periodo {pa}) risulta interamente più antica di "
                          "{b} (periodo {pb}) pur essendone stratigraficamente più "
                          "recente — sposta {a} a un periodo ≥ {pb}, oppure {b} ≤ "
                          "{pa}, oppure verifica il rapporto",
        "s_temporal_contemp": "{a} (periodo {pa}) e {b} (periodo {pb}) sono "
                              "dichiarate contemporanee ma i periodi non si "
                              "sovrappongono — assegnale allo stesso periodo",
        "s_temporal_uneval": "{a} e {b} condividono una relazione ma manca la "
                             "datazione di periodo per valutarne la coerenza — "
                             "assegna il periodo mancante",
        "t_epoch_overlap": "Fasi con intervalli sovrapposti (scelta manuale)",
        "t_epoch_reversed": "Periodizzazione con inizio dopo la fine (scelta manuale)",
        "t_epoch_no_dates": "Fase senza anni (solo segnalazione)",
        "t_datazione_mismatch": "Datazione della scheda disallineata (verrà riscritta)",
        "s_epoch_overlap": "Le fasi {a} e {b} si sovrappongono per {anni} anni ({ini}–{fin})",
        "s_epoch_reversed": "Fase {fase}: inizio {ini} dopo la fine {fin} — probabili "
                            "date a.C. inserite senza il segno meno (a.C. = numeri "
                            "negativi, es. -1650). La proposta riscrive i due anni "
                            "negativi ({nini} → {nfin}); se invece è un refuso, "
                            "scambia i due valori nella scheda Periodizzazione",
        "s_epoch_reversed_swap": "Fase {fase}: inizio {ini} dopo la fine {fin} — qui "
                                 "il segno meno non manca, quindi la lettura più "
                                 "probabile è un refuso: la proposta scambia i due anni "
                                 "({nini} → {nfin}). Controlla nella scheda "
                                 "Periodizzazione",
        "s_epoch_no_dates": "Fase {fase}: nessun anno leggibile in cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (fase {fase}): datazione «{corrente}» invece di «{atteso}»",
        "m_site_changed": "Il sito è cambiato: l'albero mostra la verifica di «{atteso}», il "
                          "selettore dice «{scelto}». Esegui di nuovo la verifica "
                          "sul sito che vuoi correggere — le spunte restano.",
        "m_nothing_to_undo": "Niente da annullare: in questa sessione non è stata applicata "
                             "nessuna correzione.",
    },
    "en": {
        "t_self_loop": "Self-loop (US related to itself)",
        "t_missing_reciprocity": "Missing reciprocity (will be created)",
        "t_contradiction_redundant": "Redundant contradiction",
        "t_contradiction_ambiguous": "Direct contradiction (manual choice)",
        "t_cycle": "Stratigraphic cycle (manual choice)",
        "t_illegal_connection": "Invalid relationship type (report only)",
        "t_temporal_inversion": "Temporal paradox (period inversion)",
        "t_temporal_contemporaneity": "Temporal paradox (non-overlapping contemporaneity)",
        "t_temporal_unevaluable": "Temporal consistency not evaluable (missing period)",
        "s_self": "{us} is related to itself",
        "s_recip": "Missing reciprocal on {b} for {a} (relationship \"{rel}\")",
        "s_contr": "Contradiction: {a} \"{lab1}\" {b}  ⇄  {b} \"{lab2}\" {a} "
                   "— keep one direction, remove the other",
        "s_cycle": "Cycle: {chain} — break the loop by removing the wrong relationship",
        "s_illegal": "Invalid relationship type: {a} → {b}",
        "s_temporal_inv": "{a} (period {pa}) is entirely older than {b} (period "
                          "{pb}) yet stratigraphically more recent — move {a} to a "
                          "period ≥ {pb}, or {b} ≤ {pa}, or check the relationship",
        "s_temporal_contemp": "{a} (period {pa}) and {b} (period {pb}) are declared "
                              "contemporary but their periods do not overlap — "
                              "assign them to the same period",
        "s_temporal_uneval": "{a} and {b} share a relationship but a period date is "
                             "missing to evaluate consistency — assign the missing "
                             "period",
        "t_epoch_overlap": "Phases with overlapping spans (manual choice)",
        "t_epoch_reversed": "Periodization starting after it ends (manual choice)",
        "t_epoch_no_dates": "Phase with no years (report only)",
        "t_datazione_mismatch": "Sheet dating out of step (will be rewritten)",
        "s_epoch_overlap": "Phases {a} and {b} overlap by {anni} years ({ini}–{fin})",
        "s_epoch_reversed": "Phase {fase}: starts {ini} after it ends {fin} — most "
                            "likely BC years entered without the minus sign (BC = "
                            "negative numbers, e.g. -1650). The proposal rewrites "
                            "both years as negatives ({nini} → {nfin}); if it is a "
                            "typo instead, swap the two values in the Periodization "
                            "form",
        "s_epoch_reversed_swap": "Phase {fase}: starts {ini} after it ends {fin} — the "
                                 "minus sign is not missing here, so the likeliest "
                                 "reading is a typo: the proposal swaps the two years "
                                 "({nini} → {nfin}). Check it in the Periodization form",
        "s_epoch_no_dates": "Phase {fase}: no readable year in cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (phase {fase}): dating «{corrente}» instead of «{atteso}»",
        "m_site_changed": "The site has changed: the tree shows the check of «{atteso}», the "
                          "picker says «{scelto}». Run the check again on the site "
                          "you want to fix — the ticks stay.",
        "m_nothing_to_undo": "Nothing to undo: no fix has been applied in this session.",
    },
    "de": {
        "t_self_loop": "Self-loop (US in Beziehung zu sich selbst)",
        "t_missing_reciprocity": "Fehlende Reziprozität (wird erstellt)",
        "t_contradiction_redundant": "Redundanter Widerspruch",
        "t_contradiction_ambiguous": "Direkter Widerspruch (manuelle Wahl)",
        "t_cycle": "Stratigraphischer Zyklus (manuelle Wahl)",
        "t_illegal_connection": "Ungültiger Beziehungstyp (nur Hinweis)",
        "t_temporal_inversion": "Zeitliches Paradoxon (Periodenumkehrung)",
        "t_temporal_contemporaneity": "Zeitliches Paradoxon (nicht überlappende Gleichzeitigkeit)",
        "t_temporal_unevaluable": "Zeitliche Konsistenz nicht bewertbar (fehlende Periode)",
        "s_self": "{us} steht in Beziehung zu sich selbst",
        "s_recip": "Fehlende Reziprozität bei {b} für {a} (Beziehung \"{rel}\")",
        "s_contr": "Widerspruch: {a} \"{lab1}\" {b}  ⇄  {b} \"{lab2}\" {a} "
                   "— eine Richtung behalten, die andere entfernen",
        "s_cycle": "Zyklus: {chain} — die Schleife durch Entfernen der falschen "
                   "Beziehung auflösen",
        "s_illegal": "Ungültiger Beziehungstyp: {a} → {b}",
        "s_temporal_inv": "{a} (Periode {pa}) ist vollständig älter als {b} (Periode "
                          "{pb}), obwohl stratigraphisch jünger — {a} in eine Periode "
                          "≥ {pb} verschieben, oder {b} ≤ {pa}, oder Beziehung prüfen",
        "s_temporal_contemp": "{a} (Periode {pa}) und {b} (Periode {pb}) sind als "
                              "gleichzeitig deklariert, aber ihre Perioden überlappen "
                              "sich nicht — derselben Periode zuweisen",
        "s_temporal_uneval": "{a} und {b} stehen in einer Beziehung, aber eine "
                             "Periodendatierung fehlt — fehlende Periode zuweisen",
        "t_epoch_overlap": "Phasen mit überlappenden Zeiträumen (manuelle Wahl)",
        "t_epoch_reversed": "Periodisierung beginnt nach ihrem Ende (manuelle Wahl)",
        "t_epoch_no_dates": "Phase ohne Jahresangaben (nur Hinweis)",
        "t_datazione_mismatch": "Datierung im Formular abweichend (wird überschrieben)",
        "s_epoch_overlap": "Die Phasen {a} und {b} überlappen sich um {anni} Jahre ({ini}–{fin})",
        "s_epoch_reversed": "Phase {fase}: beginnt {ini} nach dem Ende {fin} — "
                            "wahrscheinlich v. Chr.-Jahre ohne Minuszeichen "
                            "(v. Chr. = negative Zahlen, z. B. -1650). Der Vorschlag "
                            "schreibt beide Jahre negativ ({nini} → {nfin}); handelt "
                            "es sich dagegen um einen Tippfehler, die beiden Werte im "
                            "Periodisierungsformular tauschen",
        "s_epoch_reversed_swap": "Phase {fase}: beginnt {ini} nach dem Ende {fin} — hier "
                                 "fehlt das Minuszeichen nicht, die wahrscheinlichste "
                                 "Lesart ist also ein Tippfehler: der Vorschlag tauscht "
                                 "die beiden Jahre ({nini} → {nfin}). Bitte im "
                                 "Periodisierungsformular prüfen",
        "s_epoch_no_dates": "Phase {fase}: kein lesbares Jahr in cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (Phase {fase}): Datierung «{corrente}» statt «{atteso}»",
        "m_site_changed": "Die Fundstelle hat sich geändert: der Baum zeigt die Prüfung von "
                          "«{atteso}», die Auswahl sagt «{scelto}». Die Prüfung erneut "
                          "auf der zu korrigierenden Fundstelle ausführen — die Haken "
                          "bleiben.",
        "m_nothing_to_undo": "Nichts zum Rückgängigmachen: in dieser Sitzung wurde keine "
                             "Korrektur angewendet.",
    },
    "es": {
        "t_self_loop": "Self-loop (US relacionada consigo misma)",
        "t_missing_reciprocity": "Reciprocidad ausente (se creará)",
        "t_contradiction_redundant": "Contradicción redundante",
        "t_contradiction_ambiguous": "Contradicción directa (elección manual)",
        "t_cycle": "Ciclo estratigráfico (elección manual)",
        "t_illegal_connection": "Tipo de relación no válido (solo aviso)",
        "t_temporal_inversion": "Paradoja temporal (inversión de período)",
        "t_temporal_contemporaneity": "Paradoja temporal (contemporaneidad no solapada)",
        "t_temporal_unevaluable": "Consistencia temporal no evaluable (período faltante)",
        "s_self": "{us} está relacionada consigo misma",
        "s_recip": "Falta el recíproco en {b} para {a} (relación «{rel}»)",
        "s_contr": "Contradicción: {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— conserva una dirección, elimina la otra",
        "s_cycle": "Ciclo: {chain} — rompe el bucle eliminando la relación errónea",
        "s_illegal": "Tipo de relación no válido: {a} → {b}",
        "s_temporal_inv": "{a} (período {pa}) es completamente más antigua que {b} "
                          "(período {pb}) aunque estratigráficamente más reciente — "
                          "mueve {a} a un período ≥ {pb}, o {b} ≤ {pa}, o verifica "
                          "la relación",
        "s_temporal_contemp": "{a} (período {pa}) y {b} (período {pb}) se declaran "
                              "contemporáneas pero sus períodos no se solapan — "
                              "asígnalas al mismo período",
        "s_temporal_uneval": "{a} y {b} comparten una relación pero falta la "
                             "datación de período — asigna el período faltante",
        "t_epoch_overlap": "Fases con intervalos superpuestos (elección manual)",
        "t_epoch_reversed": "Periodización que empieza después de terminar (elección manual)",
        "t_epoch_no_dates": "Fase sin años (solo aviso)",
        "t_datazione_mismatch": "Datación de la ficha desalineada (se reescribirá)",
        "s_epoch_overlap": "Las fases {a} y {b} se superponen {anni} años ({ini}–{fin})",
        "s_epoch_reversed": "Fase {fase}: empieza {ini} después de terminar {fin} — "
                            "probablemente años a.C. introducidos sin el signo menos "
                            "(a.C. = números negativos, p. ej. -1650). La propuesta "
                            "reescribe los dos años en negativo ({nini} → {nfin}); si "
                            "en cambio es un error de tecleo, intercambia los dos "
                            "valores en la ficha Periodización",
        "s_epoch_reversed_swap": "Fase {fase}: empieza {ini} después de terminar {fin} "
                                 "— aquí no falta el signo menos, así que la lectura "
                                 "más probable es un error de tecleo: la propuesta "
                                 "intercambia los dos años ({nini} → {nfin}). "
                                 "Compruébalo en la ficha Periodización",
        "s_epoch_no_dates": "Fase {fase}: ningún año legible en cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (fase {fase}): datación «{corrente}» en vez de «{atteso}»",
        "m_site_changed": "El sitio ha cambiado: el árbol muestra la verificación de "
                          "«{atteso}», el selector dice «{scelto}». Vuelve a ejecutar "
                          "la verificación en el sitio que quieres corregir — las "
                          "marcas se mantienen.",
        "m_nothing_to_undo": "Nada que deshacer: en esta sesión no se ha aplicado ninguna "
                             "corrección.",
    },
    "fr": {
        "t_self_loop": "Self-loop (US en relation avec elle-même)",
        "t_missing_reciprocity": "Réciprocité manquante (sera créée)",
        "t_contradiction_redundant": "Contradiction redondante",
        "t_contradiction_ambiguous": "Contradiction directe (choix manuel)",
        "t_cycle": "Cycle stratigraphique (choix manuel)",
        "t_illegal_connection": "Type de relation non valide (signalement)",
        "t_temporal_inversion": "Paradoxe temporel (inversion de période)",
        "t_temporal_contemporaneity": "Paradoxe temporel (contemporanéité non chevauchante)",
        "t_temporal_unevaluable": "Cohérence temporelle non évaluable (période manquante)",
        "s_self": "{us} est en relation avec elle-même",
        "s_recip": "Réciproque manquant sur {b} pour {a} (relation «{rel}»)",
        "s_contr": "Contradiction : {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— gardez une direction, supprimez l'autre",
        "s_cycle": "Cycle : {chain} — brisez la boucle en supprimant la relation "
                   "erronée",
        "s_illegal": "Type de relation non valide : {a} → {b}",
        "s_temporal_inv": "{a} (période {pa}) est entièrement plus ancienne que {b} "
                          "(période {pb}) bien que stratigraphiquement plus récente — "
                          "déplacez {a} vers une période ≥ {pb}, ou {b} ≤ {pa}, ou "
                          "vérifiez la relation",
        "s_temporal_contemp": "{a} (période {pa}) et {b} (période {pb}) sont déclarées "
                              "contemporaines mais leurs périodes ne se chevauchent pas "
                              "— assignez-les à la même période",
        "s_temporal_uneval": "{a} et {b} partagent une relation mais la datation de "
                             "période est manquante — assignez la période manquante",
        "t_epoch_overlap": "Phases aux intervalles qui se chevauchent (choix manuel)",
        "t_epoch_reversed": "Périodisation qui commence après sa fin (choix manuel)",
        "t_epoch_no_dates": "Phase sans années (signalement seul)",
        "t_datazione_mismatch": "Datation de la fiche décalée (elle sera réécrite)",
        "s_epoch_overlap": "Les phases {a} et {b} se chevauchent sur {anni} ans ({ini}–{fin})",
        "s_epoch_reversed": "Phase {fase} : commence en {ini} après sa fin {fin} — "
                            "probablement des années av. J.-C. saisies sans le signe "
                            "moins (av. J.-C. = nombres négatifs, p. ex. -1650). La "
                            "proposition réécrit les deux années en négatif ({nini} → "
                            "{nfin}) ; s'il s'agit plutôt d'une coquille, échangez les "
                            "deux valeurs dans la fiche Périodisation",
        "s_epoch_reversed_swap": "Phase {fase} : commence en {ini} après sa fin {fin} — "
                                 "ici le signe moins ne manque pas, la lecture la plus "
                                 "probable est donc une coquille : la proposition "
                                 "échange les deux années ({nini} → {nfin}). Vérifiez "
                                 "dans la fiche Périodisation",
        "s_epoch_no_dates": "Phase {fase} : aucune année lisible dans cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (phase {fase}) : datation «{corrente}» au lieu de «{atteso}»",
        "m_site_changed": "Le site a changé : l'arbre montre la vérification de «{atteso}», "
                          "le sélecteur indique «{scelto}». Relancez la vérification "
                          "sur le site à corriger — les cases cochées restent.",
        "m_nothing_to_undo": "Rien à annuler : aucune correction n'a été appliquée dans cette "
                             "session.",
    },
    "pt": {
        "t_self_loop": "Self-loop (US relacionada consigo mesma)",
        "t_missing_reciprocity": "Reciprocidade ausente (será criada)",
        "t_contradiction_redundant": "Contradição redundante",
        "t_contradiction_ambiguous": "Contradição direta (escolha manual)",
        "t_cycle": "Ciclo estratigráfico (escolha manual)",
        "t_illegal_connection": "Tipo de relação inválido (apenas aviso)",
        "t_temporal_inversion": "Paradoxo temporal (inversão de período)",
        "t_temporal_contemporaneity": "Paradoxo temporal (contemporaneidade não sobreposta)",
        "t_temporal_unevaluable": "Consistência temporal não avaliável (período em falta)",
        "s_self": "{us} está relacionada consigo mesma",
        "s_recip": "Falta o recíproco em {b} para {a} (relação «{rel}»)",
        "s_contr": "Contradição: {a} «{lab1}» {b}  ⇄  {b} «{lab2}» {a} "
                   "— mantenha uma direção, remova a outra",
        "s_cycle": "Ciclo: {chain} — quebre o ciclo removendo a relação errada",
        "s_illegal": "Tipo de relação inválido: {a} → {b}",
        "s_temporal_inv": "{a} (período {pa}) é inteiramente mais antiga que {b} "
                          "(período {pb}) embora estratigraficamente mais recente — "
                          "mova {a} para um período ≥ {pb}, ou {b} ≤ {pa}, ou "
                          "verifique a relação",
        "s_temporal_contemp": "{a} (período {pa}) e {b} (período {pb}) são declaradas "
                              "contemporâneas mas os seus períodos não se sobrepõem — "
                              "atribua-as ao mesmo período",
        "s_temporal_uneval": "{a} e {b} partilham uma relação mas a datação de "
                             "período está em falta — atribua o período em falta",
        "t_epoch_overlap": "Fases com intervalos sobrepostos (escolha manual)",
        "t_epoch_reversed": "Periodização que começa depois de terminar (escolha manual)",
        "t_epoch_no_dates": "Fase sem anos (apenas aviso)",
        "t_datazione_mismatch": "Datação da ficha desalinhada (será reescrita)",
        "s_epoch_overlap": "As fases {a} e {b} sobrepõem-se em {anni} anos ({ini}–{fin})",
        "s_epoch_reversed": "Fase {fase}: começa em {ini} depois de terminar {fin} — "
                            "provavelmente anos a.C. introduzidos sem o sinal menos "
                            "(a.C. = números negativos, p. ex. -1650). A proposta "
                            "reescreve os dois anos como negativos ({nini} → {nfin}); "
                            "se for um erro de digitação, troque os dois valores na "
                            "ficha Periodização",
        "s_epoch_reversed_swap": "Fase {fase}: começa em {ini} depois de terminar {fin} "
                                 "— aqui o sinal menos não falta, portanto a leitura "
                                 "mais provável é um erro de digitação: a proposta troca "
                                 "os dois anos ({nini} → {nfin}). Verifique na ficha "
                                 "Periodização",
        "s_epoch_no_dates": "Fase {fase}: nenhum ano legível em cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (fase {fase}): datação «{corrente}» em vez de «{atteso}»",
        "m_site_changed": "O sítio mudou: a árvore mostra a verificação de «{atteso}», o "
                          "seletor diz «{scelto}». Execute a verificação de novo no "
                          "sítio que quer corrigir — as marcas mantêm-se.",
        "m_nothing_to_undo": "Nada para anular: nesta sessão não foi aplicada nenhuma "
                             "correção.",
    },
}


def _t(lang, key):
    """Localised template string (falls back to English)."""
    return _L.get(lang, _L["en"]).get(key) or _L["en"][key]


def kind_title(kind, lang="it"):
    """Localised group title for an issue *kind* (used by the report UI)."""
    return _t(lang, "t_" + kind)


def _unit_prefix(lang):
    try:
        from modules.utility.pyarchinit_i18n_stratigraphic import UNIT_TYPE_ABBREV
        return UNIT_TYPE_ABBREV.get(lang, UNIT_TYPE_ABBREV.get("en", ("US",)))[0]
    except Exception:
        return "US"


def _utok(us, lang):
    """US display token in the UI language, e.g. 'US 661' / 'SU 661' / 'SE 661'."""
    return f"{_unit_prefix(lang)} {us}"


def _rel_label(et, lang):
    """Localised rapporti word for an edge type (e.g. overlies → Copre / Covers)."""
    try:
        from modules.utility.pyarchinit_i18n_stratigraphic import RELATIONSHIPS
        terms = RELATIONSHIPS.get(lang) or RELATIONSHIPS.get("en")
    except Exception:
        terms = None
    idx = _EDGE_TYPE_TO_REL_INDEX.get(et)
    if terms is not None and idx is not None:
        return terms[idx]
    if terms is not None and et == "is_after":
        return terms[2]      # temporal precedence shown as "covers"
    if terms is not None and et == "is_before":
        return terms[3]      # "covered by"
    return et or "→"


def check_rapporti(graph, *, sito, lang="it", validate=True,
                   inverse_label=None, chrono=None, unit_periods=None) -> RapportiReport:
    """Detect rapporti inconsistencies. *lang* (2-letter QGIS UI locale)
    localises every issue ``summary``. Edit computation is in
    :func:`_fill_edits`."""
    rep = RapportiReport(sito=sito)
    edges = _strat_edges(graph)
    edge_set = {(s, t, et) for (s, t, et) in edges}

    # Direction lookup over ALL graph edges so cycle/contradiction summaries
    # can name the actual relationship of each step (overlies→Copre/Covers…).
    all_dir = {}
    for e in getattr(graph, "edges", None) or []:
        es = getattr(e, "edge_source", None)
        et2 = getattr(e, "edge_target", None)
        ety = getattr(e, "edge_type", None)
        if es and et2 and ety:
            all_dir.setdefault((es, et2), ety)

    def _step(x, y):
        ety = all_dir.get((x, y)) or all_dir.get((y, x))
        return _rel_label(ety, lang) if ety else "→"

    # Cycles + self-loops (s3dgraphy SCC detector). Only report cycles whose
    # members are ALL real us_table-backed US nodes; skip any cycle that
    # threads a projector-synthesized placeholder (graph artifact, not a real
    # stratigraphic contradiction the user can act on).
    from s3dgraphy.diagnostics import detect_stratigraphic_cycles
    _per_chiave, per_us = _index_rows(graph)
    for cyc in detect_stratigraphic_cycles(graph):
        us_real = [_real_us(graph.find_node_by_id(x)) for x in cyc]
        if any(u is None for u in us_real):
            continue
        us_path = us_real
        # Le righe si sanno per nodo, non per numero: un ciclo arriva dal
        # rilevatore come una lista di `node_id`, e ogni nodo è una riga.
        righe = [_row_key(graph.find_node_by_id(x)) for x in cyc]
        n = len(cyc)
        if n == 1:
            rep.issues.append(Issue(
                SELF_LOOP, us_path, True,
                _t(lang, "s_self").format(us=_utok(us_path[0], lang)),
                rows=[_as_row(k) for k in righe]))
        elif n == 2:
            rep.issues.append(Issue(
                CONTRADICTION_AMBIGUOUS, us_path, False,
                _t(lang, "s_contr").format(
                    a=_utok(us_path[0], lang), b=_utok(us_path[1], lang),
                    lab1=_step(cyc[0], cyc[1]), lab2=_step(cyc[1], cyc[0])),
                rows=[_as_row(k) for k in righe]))
        else:
            # "US102 «Copre» US103 «Coperto da» US101 … US102"
            parts = [f"{_utok(us_real[i], lang)} «{_step(cyc[i], cyc[(i + 1) % n])}»"
                     for i in range(n)]
            chain = " ".join(parts) + f" {_utok(us_real[0], lang)}"
            rep.issues.append(Issue(
                CYCLE, us_path, False,
                _t(lang, "s_cycle").format(chain=chain),
                rows=[_as_row(k) for k in righe]))

    # Missing reciprocity. Si legge in quello che le due schede hanno
    # SCRITTO, non negli archi del grafo.
    #
    # Il projector fonde una coppia reciproca in UN arco canonico: US 1
    # «Copre 2» e US 2 «Coperto da 1» danno un solo `overlies`, e il verso
    # inverso nel grafo non c'è mai. Cercandolo lì, ogni rapporto scritto
    # bene risultava mancante: sul sito di esempio 81 problemi su 81 erano
    # falsi, e il «fix» aggiungeva un doppione a quattro elementi di un
    # rapporto già presente in forma corta, su 38 righe, a ogni clic
    # (Enzo, 2026-10-10).
    #
    # Il confronto è sul **tipo di arco** e sulla RIGA, non sulla parola né
    # sul numero di elementi: «Coperto da» e «Covered by» sono lo stesso
    # rapporto, e `['Coperto da','1']` dice quanto `['Coperto da','1','1',
    # 'Sito']`. Solo fra US vere: il fix scrive in una riga di us_table, e
    # un segnaposto sintetico (us=None) non ne ha una.
    #
    # L'indice è per **chiave di riga** e non per numero di US: l'identità di
    # una scheda è `UniqueConstraint('sito', 'area', 'us', 'unita_tipo')`, e
    # indicizzando per numero la seconda riga copriva la prima — sullo scavo a
    # due aree il reciproco scritto nell'area 2 zittiva l'avviso dell'area 1,
    # e i rapporti dell'area 1 risultavano mancanti tutti quanti perché a
    # risponderne era la scheda dell'altra area (2026-10-10).
    scritti = {}
    for n in getattr(graph, "nodes", None) or []:
        k = _row_key(n)
        if k is None:
            continue
        a = getattr(n, "attributes", None) or {}
        voci = []
        for voce in _coerce_to_list(a.get("rapporti")):
            if not isinstance(voce, (list, tuple)) or len(voce) < 2:
                continue
            et_voce = RAPPORTI_TO_EDGE_TYPE.get(str(voce[0]).strip().lower())
            if et_voce:
                # Il terzo elemento è l'area del contraente, quando c'è.
                voci.append((et_voce, _txt(voce[1]),
                             _txt(voce[2]) if len(voce) > 2 else ""))
        scritti[k] = voci

    def _risponde(b_key, inv, a_key):
        """Vero quando la scheda B porta il reciproco **della riga A**, e non
        di una riga che ne ripete soltanto il numero."""
        for (et_b, us_b, area_b) in scritti.get(b_key) or ():
            if et_b != inv or us_b != a_key[0]:
                continue
            if a_key in _named_rows(us_b, area_b, b_key[1], per_us):
                return True
        return False

    visti = set()
    for a_key, voci in scritti.items():
        for (et, b_us, b_area) in voci:
            inv = _EDGE_TYPE_INVERSE.get(et)
            if inv is None:
                continue
            b_keys = _named_rows(b_us, b_area, a_key[1], per_us)
            if not b_keys:
                continue          # la voce non nomina nessuna riga del sito
            if any(_risponde(bk, inv, a_key) for bk in b_keys):
                continue
            # Una sola riga candidata: la correzione sa dove scrivere. Più di
            # una: si segnala e `_fill_edits` non propone niente.
            b_key = b_keys[0] if len(b_keys) == 1 else None
            segno = (a_key, b_key or b_us, et)
            if segno in visti:
                continue
            visti.add(segno)
            rep.issues.append(Issue(
                MISSING_RECIPROCITY, [a_key[0], b_us], True,
                _t(lang, "s_recip").format(
                    a=_utok(a_key[0], lang), b=_utok(b_us, lang),
                    rel=_rel_label(et, lang)),
                rows=[_as_row(a_key), _as_row(b_key)]))

    # Connection-type legality (report-only).
    if validate:
        from s3dgraphy.graph import Graph
        for (s, t, et) in edges:
            sn = graph.find_node_by_id(s)
            tn = graph.find_node_by_id(t)
            if sn is None or tn is None:
                continue
            if _real_us(sn) is None or _real_us(tn) is None:
                continue
            try:
                ok = Graph.validate_connection(
                    getattr(sn, "node_type", None),
                    getattr(tn, "node_type", None), et)
            except Exception:
                ok = True
            if not ok:
                rep.issues.append(Issue(
                    ILLEGAL_CONNECTION,
                    [str(_us_of(sn)), str(_us_of(tn))], False,
                    _t(lang, "s_illegal").format(
                        a=_utok(_us_of(sn), lang), b=_utok(_us_of(tn), lang))
                    + f"  («{_rel_label(et, lang)}»)",
                    rows=[_as_row(_row_key(sn)), _as_row(_row_key(tn))]))

    _fill_edits(rep, graph, inverse_label=inverse_label)

    # Temporal paradoxes (only when chronology + period spans are supplied).
    if chrono and unit_periods is not None:
        from modules.utility import temporal_check as _TC   # lazy: avoid import cycle
        rep.issues += _TC.detect_temporal(
            graph, chrono, unit_periods, sito=sito, lang=lang)
        _TC.solve_fixes(
            [i for i in rep.issues if i.kind in (
                _TC.TEMPORAL_INVERSION, _TC.TEMPORAL_CONTEMPORANEITY,
                _TC.TEMPORAL_UNEVALUABLE)],
            graph, chrono, unit_periods, sito=sito)

    return rep


def _source_term(node, target_us, target_area=None):
    """The source row's own rapporti label for target_us (capitalized).

    Fra due voci che nominano lo stesso numero in aree diverse — «Copre 9
    (area 1)» e «Taglia 9 (area 2)» sulla stessa scheda — si prende quella
    dell'area chiesta: è di quella riga che il reciproco manca.
    """
    a = getattr(node, "attributes", None) or {}
    voci = [e for e in _coerce_to_list(a.get("rapporti"))
            if isinstance(e, (list, tuple)) and len(e) >= 2
            and _txt(e[1]) == _txt(target_us)]

    def _priorita(e):
        """Prima la voce dell'area chiesta, poi quella che l'area non la dice,
        per ultima quella che ne dice un'altra."""
        area = _txt(e[2]) if len(e) > 2 else ""
        if area == _txt(target_area):
            return 0
        return 1 if not area else 2

    if target_area:
        voci.sort(key=_priorita)
    for entry in voci:
        lbl = str(entry[0]).strip()
        if lbl:
            return lbl.capitalize(), entry
    return None, None


def _fill_edits(rep, graph, *, inverse_label=None):
    if inverse_label is None:
        from modules.utility.pyarchinit_i18n_stratigraphic import (
            get_inverse_relationship as inverse_label)
    per_chiave, _per_us = _index_rows(graph)
    by_us_node = {}
    for n in graph.nodes:
        u = _us_of(n)
        if u is not None:
            by_us_node.setdefault(str(u), n)

    def _riga(iss, i):
        """La riga i-esima di una issue, o ``None`` se non la nomina."""
        righe = getattr(iss, "rows", None) or ()
        return righe[i] if i < len(righe) else None

    def _nodo(riga, us):
        """Il nodo di quella riga; senza riga si ripiega sul numero di US,
        come faceva questa funzione prima che le righe si nominassero."""
        n = per_chiave.get(_key_of_row(riga)) if riga else None
        return n if n is not None else by_us_node.get(str(us))

    for iss in rep.issues:
        if iss.kind == SELF_LOOP:
            us = iss.us_path[0]
            riga = _riga(iss, 0)
            n = _nodo(riga, us)
            a = getattr(n, "attributes", None) or {}
            rem = tuple(tuple(str(x) for x in e)
                        for e in _coerce_to_list(a.get("rapporti"))
                        if isinstance(e, (list, tuple)) and len(e) >= 2
                        and str(e[1]).strip() == us)
            iss.edits = [Edit(us=us, remove=rem,
                              target=_target_of_row(riga))] if rem else []
        elif iss.kind == MISSING_RECIPROCITY:
            a_us, b_us = iss.us_path
            riga_a, riga_b = _riga(iss, 0), _riga(iss, 1)
            if getattr(iss, "rows", None) and riga_b is None:
                # La riga da scrivere non si sa nominare: `apply_edits`
                # rifiuterebbe la chiave ambigua e porterebbe via tutte le
                # correzioni dello stesso clic. Si segnala e non si propone.
                iss.auto = False
                iss.edits = []
                continue
            # source term on A for B; build the inverse on B for A
            src = _nodo(riga_a, a_us)
            term, entry = _source_term(
                src, b_us, (riga_b or {}).get("area")) if src else (None, None)
            if term is None:
                iss.auto = False
                iss.edits = []
                continue
            # L'area che si scrive nella voce nuova è quella di **A**: la voce
            # sta sulla scheda di B e nomina A. Quando la riga di A non porta
            # un'area si tiene quella che la voce di A dichiarava, e in
            # mancanza di tutto l'area 1 — il valore di sempre.
            area = ((riga_a or {}).get("area")
                    or (str(entry[2]) if len(entry) > 2 else "")
                    or "1")
            sito = str(entry[3]) if len(entry) > 3 else rep.sito
            inv = inverse_label(term) or term
            # Honesty guard: only auto-fix when the inverse label round-trips
            # to the correct inverse edge type. Otherwise parse_rapporti
            # silently drops it (the projector never builds the reciprocal
            # edge), so the fix could never satisfy reciprocity and the issue
            # re-appears on every re-scan — the bug where the dialog claimed
            # "113 fixes" but only ~6 stuck (abuts → "Supports", which had no
            # edge-type mapping). Surface non-round-tripping cases as manual.
            et = RAPPORTI_TO_EDGE_TYPE.get(str(term).lower())
            inv_et = _EDGE_TYPE_INVERSE.get(et) if et else None
            if (inv_et is None
                    or RAPPORTI_TO_EDGE_TYPE.get(str(inv).lower()) != inv_et):
                iss.auto = False
                iss.edits = []
                continue
            iss.edits = [Edit(us=b_us, add=((inv, a_us, area, sito),),
                              target=_target_of_row(riga_b))]
        # CONTRADICTION_AMBIGUOUS / CYCLE / ILLEGAL_CONNECTION: no auto edits
    return rep


# ---------------------------------------------------------------------------
# Task 3: apply + rollback (backend-agnostic)
# ---------------------------------------------------------------------------
import ast as _ast
from dataclasses import dataclass as _dc


@_dc
class RollbackToken:
    sito: str
    snapshot: dict   # (tabella, chiave) -> (sito della riga, valori originali)


#: Dove le correzioni possono scrivere, tabella per tabella. Fuori da qui non
#: si scrive: una colonna che nessuno ha autorizzato resta com'è.
_WRITABLE = {
    "us_table": {"periodo_iniziale", "fase_iniziale", "periodo_finale",
                 "fase_finale", "datazione"},
    "periodizzazione_table": {"cron_iniziale", "cron_finale"},
}


def _target_of(edit):
    """La tabella e la chiave di una ``Edit``, la chiave ordinata.

    Un ``target`` vuoto vale ``us_table`` con la chiave ``us``, cioè
    esattamente quello che questa funzione faceva prima che le correzioni
    cronologiche avessero bisogno di un'altra tabella: nessuna chiamata
    esistente cambia.
    """
    target = getattr(edit, "target", ()) or ()
    if not target:
        return "us_table", (("us", str(edit.us)),)
    tabella = str(target[0])
    chiave = dict(target[1]) if len(target) > 1 else {}
    return tabella, tuple(sorted((str(k), str(v)) for k, v in chiave.items()))


def _key_clause(chiave, prefisso):
    """Il confronto delle colonne di chiave, e i suoi parametri.

    Le colonne si confrontano **come testo**, un NULL conta come stringa vuota
    e gli spazi in testa e in coda non contano: ``periodizzazione_table.periodo``
    è ``Integer`` nello schema e ``fase`` è ``Text``, PostgreSQL non converte
    da sé, e chi legge la chiave normalizza il NULL a ``''`` **e la striscia**
    (``chronology_check._text``, :func:`_txt`) — se qui non facessimo lo stesso,
    la correzione non troverebbe mai la sua riga e la finestra direbbe di
    averla applicata.

    Lo spazio non è un caso di scuola: ``area`` e ``fase`` sono testo battuto a
    mano in una scheda, e un ``area = '1 '`` faceva aggiornare zero righe con
    la finestra che diceva «1 correzioni applicate» e la riverifica che
    ripresentava lo stesso avviso per sempre — «dice corretti e non applica»,
    il guasto che l'utente ha segnalato. ``TRIM`` in SQL toglie gli spazi (è
    quello che si batte in un campo di testo); il lato Python striscia tutti i
    bianchi, come chi legge la chiave.
    """
    parti, params = [], {}
    for i, (col, val) in enumerate(chiave):
        if not col.isidentifier():
            raise ValueError("colonna di chiave non valida: %r" % (col,))
        parti.append("TRIM(COALESCE(CAST(%s AS TEXT), '')) = :%s_%d"
                     % (col, prefisso, i))
        params["%s_%d" % (prefisso, i)] = str(val).strip()
    return parti, params


def _where(tabella, chiave, row_sito):
    """La clausola che individua la riga, e i suoi parametri.

    Il sito serve sempre, per ogni tabella: senza, la chiave individua la
    stessa riga in tutti i siti del database — dieci, in quello di esempio.
    Una riga il cui ``sito`` è NULL non si può nemmeno nominare con
    ``sito = :w_sito``, quindi si rifiuta invece di allargare la clausola.

    Le colonne della chiave le confronta :func:`_key_clause`, come testo
    strisciato: là c'è il perché.
    """
    if not row_sito:
        raise ValueError(
            "una correzione su %s ha bisogno del sito: senza, la chiave %s "
            "individua la stessa riga in tutti i siti"
            % (tabella, dict(chiave)))
    parti, params = _key_clause(chiave, "w")
    return " AND ".join(["sito = :w_sito"] + parti), dict(params, w_sito=row_sito)


def apply_edits(edits, handle, *, sito=None) -> RollbackToken:
    from sqlalchemy import text
    # Raggruppate per (tabella, chiave): due correzioni sulla stessa riga si
    # applicano con una UPDATE sola, e lo snapshot per l'annulla tiene il
    # valore di prima della prima.
    by_row = {}
    for e in edits:
        by_row.setdefault(_target_of(e), []).append(e)
    snapshot = {}
    with handle.engine.begin() as conn:
        for (tabella, chiave), row_edits in by_row.items():
            scrivibili = _WRITABLE.get(tabella, frozenset())
            touch_rapporti = (tabella == "us_table"
                              and any(e.add or e.remove for e in row_edits))
            field_cols = []
            for e in row_edits:
                for (col, _v) in e.set_fields:
                    if col in scrivibili and col not in field_cols:
                        field_cols.append(col)
            if not touch_rapporti and not field_cols:
                continue

            # Il sito della riga: per us_table lo si cerca quando non è dato,
            # com'è sempre stato; per le altre tabelle è obbligatorio e
            # _where lo pretende. Lo si cerca con **tutta** la chiave: la sola
            # `us` individua più righe su uno scavo a più aree, e il sito
            # della prima che capita potrebbe non essere quello della riga che
            # si sta per scrivere.
            if tabella == "us_table" and sito is None:
                parti, kparams = _key_clause(chiave, "k")
                r = conn.execute(text("SELECT sito FROM us_table WHERE %s"
                                      % " AND ".join(parti)),
                                 kparams).fetchone()
                row_sito = r[0] if r else None
            else:
                row_sito = sito
            where, wparams = _where(tabella, chiave, row_sito)

            # Snapshot: i valori di prima, letti con la stessa clausola con
            # cui si scriverà.
            #
            # `fetchall` e non `fetchone`: se la clausola individua più di una
            # riga, la UPDATE le riscriverebbe tutte e lo snapshot terrebbe i
            # valori della prima — così l'annulla appiattirebbe le altre su
            # un valore che non hanno mai avuto. È il bug della US 1 in due
            # aree (l'identità di una scheda è `UniqueConstraint('sito',
            # 'area', 'us', 'unita_tipo')`). Una chiave ambigua è un errore,
            # non una scrittura in silenzio, e vale per **qualunque**
            # produttore di correzioni, anche futuro. Il `raise` sta dentro
            # `engine.begin()`: la transazione si annulla e non resta niente
            # scritto a metà.
            cols = (["rapporti"] if touch_rapporti else []) + field_cols
            orig = {}
            righe = conn.execute(text("SELECT %s FROM %s WHERE %s"
                                      % (", ".join(cols), tabella, where)),
                                 wparams).fetchall()
            if len(righe) > 1:
                raise ValueError(
                    "una correzione su %s individua %d righe con la chiave "
                    "%s (sito %r): la chiave non basta a nominare la riga e "
                    "nessuna correzione è stata applicata"
                    % (tabella, len(righe), dict(chiave), row_sito))
            if righe:
                for i, c in enumerate(cols):
                    orig[c] = righe[0][i]
            snapshot[(tabella, chiave)] = (row_sito, orig)

            new_vals = {}
            if touch_rapporti:
                lst = _coerce_to_list(orig.get("rapporti"))
                lst = [list(map(str, x)) for x in lst
                       if isinstance(x, (list, tuple))]
                for e in row_edits:
                    for rr in e.remove:
                        rr = list(map(str, rr))
                        lst = [x for x in lst if x != rr]
                    for ad in e.add:
                        aa = list(map(str, ad))
                        # Un rapporto si riconosce da **rapporto + US**, non
                        # dal numero di elementi: `['Coperto da','1']` dice
                        # quanto `['Coperto da','1','1','Sito']`, e appendere
                        # il secondo sporcava la scheda a ogni clic (Enzo,
                        # 2026-10-10).
                        if not any(x[:2] == aa[:2] for x in lst):
                            lst.append(aa)
                new_vals["rapporti"] = str(lst)
            for e in row_edits:
                for (col, val) in e.set_fields:
                    if col in scrivibili:
                        new_vals[col] = val

            set_clause = ", ".join("%s = :v_%s" % (c, c) for c in new_vals)
            params = {"v_%s" % c: v for c, v in new_vals.items()}
            params.update(wparams)
            conn.execute(text("UPDATE %s SET %s WHERE %s"
                              % (tabella, set_clause, where)), params)
    return RollbackToken(sito=sito or "", snapshot=snapshot)


def rollback(token, handle):
    from sqlalchemy import text
    with handle.engine.begin() as conn:
        for (tabella, chiave), (row_sito, orig) in token.snapshot.items():
            if not orig:
                continue
            where, wparams = _where(tabella, chiave, row_sito)
            set_clause = ", ".join("%s = :v_%s" % (c, c) for c in orig)
            params = {"v_%s" % c: v for c, v in orig.items()}
            params.update(wparams)
            conn.execute(text("UPDATE %s SET %s WHERE %s"
                              % (tabella, set_clause, where)), params)


# ---------------------------------------------------------------------------
# Task 4: import copy-mode — regenerate_node_uuids
# ---------------------------------------------------------------------------

def regenerate_node_uuids(graph) -> int:
    """Assign a fresh uuid7 to every node's ``attributes['node_uuid']`` so a
    copy-import does not match (and overwrite) existing DB rows. Returns the
    count changed."""
    from s3dgraphy.sync.uuid7 import uuid7
    n = 0
    for node in getattr(graph, "nodes", None) or []:
        attrs = getattr(node, "attributes", None)
        if attrs is None:
            continue
        attrs["node_uuid"] = str(uuid7())
        n += 1
    return n
