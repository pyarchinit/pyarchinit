# Verifica cronologia dentro «Verifica rapporti» — piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** I problemi di cronologia di un sito si vedono **e si correggono** dentro la finestra «Verifica rapporti», senza passare da EMStudio.

**Architecture:** Un modulo nuovo e **puro** (`modules/utility/chronology_check.py`) giudica le righe della periodizzazione e delle US e restituisce `Issue` nella stessa forma di `rapporti_check`, così albero, anteprima, applica e annulla non cambiano. La macchina di scrittura che c'è già impara a scrivere in più di una tabella grazie a un campo `target` su `Edit` e a una whitelist per tabella. Il dialogo guadagna due righe di innesto, le proposte manuali spuntabili e una riga di provenienza nell'anteprima.

**Tech Stack:** Python 3 (QGIS ≥ 3.22), SQLAlchemy Core (`text()`), pytest, s3dgraphy 1.6.0.dev42 in `ext_libs/`, Qt via `qgis.PyQt`.

**Spec:** `docs/superpowers/specs/2026-10-10-verifica-cronologia-design.md`

## Global Constraints

- Branch di lavoro: **`Stratigraph_00001`**. Niente port su `master`.
- Versione plugin oggi `5.13.63-alpha` → **`5.13.64-alpha`** (Task 8).
- **Nessuna colonna nuova in nessuna tabella.**
- `modules/utility/chronology_check.py` è **puro**: nessun import di `qgis`, nessun widget, nessun accesso al database dentro `check_chronology`.
- Le scritture passano **solo** dalla whitelist `_WRITABLE`; fuori da lì non si scrive.
- Sei lingue in `_L`, le stesse che il dizionario copre già: `it`, `en`, `de`, `es`, `fr`, `pt`.
- La chiave di una fase è **sempre testo**, mai convertita a numero (`2.1` ≠ `2.10`).
- Niente attribuzione AI in commit, PR, issue, commenti.
- Comando test canonico (dalla radice del plugin):
  ```
  QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
  PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
  /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
    tests/sync tests/utility tests/migrations -q --continue-on-collection-errors \
    --ignore=tests/sync/test_groups_dialog_smoke.py \
    --ignore=tests/sync/test_paradata_dialog_smoke.py -p no:warnings
  ```
  Baseline a HEAD: **8 errori d'ambiente, 1 xfail, 1 skip, 0 failure.** Un errore in più è una regressione.
- Ogni nuovo file di test apre con il preambolo che mette `ext_libs` **primo** sul path: in `site-packages` di QGIS vive una `s3dgraphy 0.1.6` che altrimenti ombreggia la dev42.

## Tre scostamenti dalla spec, misurati

La spec è stata scritta prima di provare l'aritmetica. Tre numeri suoi non reggono, e il piano li corregge **in su**, non in giù:

1. **La proposta di `epoch_overlap` non ha istanze.** Le 20 sovrapposizioni del database (2 per sito × 10 siti) sono fra fasi con intervallo **identico** (1500–1549 due volte, 1451–1499 due volte). Qualunque restringimento — alzare l'inizio della più recente o abbassare la fine della più antica — produce una riga rovesciata. Quindi: la proposta si fa **solo** quando lascia un intervallo non vuoto, e su questo database **non si fa mai** (misurato: `prop=0` su tutti e dieci i siti). L'avviso resta, senza correzione. La proposta si prova su righe costruite a mano e serve alle periodizzazioni importate da fuori, che si sovrappongono parzialmente.
2. **`datazione_mismatch` sono 13, non 9.** Su «Scavo archeologico»: 38 combaciano, **9** differiscono, **4** hanno la scheda vuota e la fonte piena. Anche quelle 4 sono disallineamenti da chiudere — riempire una copia vuota dalla sua fonte è la stessa regola — quindi le issue sono **13**. Sui nove siti tradotti: 47 + 4 = **51**.
3. **Una fonte vuota non cancella una scheda piena.** Se `datazione_estesa` della fase è vuota non c'è niente da copiare: la US si salta. Senza questa regola la verifica svuoterebbe le schede dei siti con periodizzazione incompleta.

## Review Focus

Cinque classi d'ingresso che la spec implica e che nessun test nascerebbe a coprire da sé. Ognuna ha il suo test, nel task che possiede il codice.

1. **Anni a.C. e anno zero** — `cron_iniziale` negativo o `0`: l'intersezione, l'ordinamento e la proposta devono funzionare su interi negativi, e `0` non deve essere letto come «nessun anno». *(test in Task 1)*
2. **Righe di un altro sito** — `load_chronology_rows` deve filtrare per `sito`: senza filtro le 2 sovrapposizioni di un sito diventano le 20 del database, e la correzione automatica riscriverebbe dieci siti in un colpo. *(test in Task 4)*
3. **Vuoti che non sono disallineamenti** — `datazione = None` nella scheda e `datazione_estesa = ''` nella periodizzazione dicono la stessa cosa e non sono una issue; e una fonte vuota non deve cancellare una scheda piena. *(test in Task 2)*
4. **Una correzione sulla periodizzazione senza sito** — `apply_edits(..., sito=None)` con un `target` su `periodizzazione_table` individuerebbe la stessa `(periodo, fase)` in tutti e dieci i siti: deve rifiutare, non scrivere. *(test in Task 3)*
5. **Due correzioni sulla stessa riga** — una fase che si sovrappone a due altre produce due `Edit` sulla stessa riga: si applicano insieme, e l'annulla deve riportare il valore di **prima della prima**, non quello intermedio. *(test in Task 3)*

---

## File Structure

| file | che cosa ne risponde |
|---|---|
| `modules/utility/chronology_check.py` **(nuovo)** | il giudizio: quattro categorie, le correzioni che le chiudono, la lettura delle righe, le due formattazioni pure (`explain_bounds`, `edit_prefix`). Puro. |
| `modules/utility/rapporti_check.py` **(modificato)** | `Edit.target`, `_WRITABLE` per tabella, `apply_edits`/`rollback` per `(tabella, chiave)`, le 48 voci localizzate in `_L`. |
| `gui/rapporti_check_dialog.py` **(modificato)** | l'innesto: `_run` aggiunge le issue cronologiche, `_render` rende spuntabili le proposte manuali, `_preview` scrive il prefisso giusto e la riga di provenienza. |
| `tests/utility/test_chronology_check.py` **(nuovo)** | il giudizio, senza database e senza QGIS. |
| `tests/utility/test_chronology_apply.py` **(nuovo)** | la scrittura per tabella e l'annulla, su SQLite di prova. |
| `tests/utility/test_chronology_live.py` **(nuovo)** | i numeri veri sul database di esempio. |

Perché un modulo nuovo e non dentro `rapporti_check.py`: quello sta a 656 righe e risponde già dei rapporti, della loro reciprocità e della scrittura. La cronologia è un altro giudizio sugli stessi dati; condivide le **forme** (`Issue`, `Edit`, `_t`) e non il contenuto.

---

### Task 1: Rilevazione sulle fasi — `epoch_overlap`, `epoch_reversed`, `epoch_no_dates`

**Files:**
- Create: `modules/utility/chronology_check.py`
- Modify: `modules/utility/rapporti_check.py` (le voci in `_L`, sei blocchi lingua)
- Test: `tests/utility/test_chronology_check.py`

**Interfaces:**
- Consumes: da `modules.utility.rapporti_check` → `Issue(kind, us_path, auto, summary, edits)`, `Edit(us, add, remove, set_fields, target)`, `_t(lang, key)`. **`Edit.target` non esiste ancora** e arriva in Task 3: qui le `Edit` lo passano come quinto campo keyword, quindi fino a Task 3 i test di questo task falliscono su `TypeError: unexpected keyword argument 'target'`. Per questo **Task 3 va eseguito prima di lanciare la suite intera**; i test di Task 1 girano verdi solo da Task 3 in poi. Per tenere la catena RED→GREEN pulita, il campo `target` si aggiunge **in questo task** (sole tre righe nella dataclass), e Task 3 gli dà il significato nella scrittura.
- Produces: `check_chronology(periods, units, *, sito, lang="it") -> list[Issue]`; `_PERIOD_TABLE = "periodizzazione_table"`; gli helper puri `_year(val) -> int | None`, `_key(row) -> tuple[str, str]`, `_label(key) -> str`, `_text(val) -> str`; le chiavi `_L` `t_epoch_overlap`, `t_epoch_reversed`, `t_epoch_no_dates`, `t_datazione_mismatch`, `s_epoch_overlap`, `s_epoch_reversed`, `s_epoch_no_dates`, `s_datazione_mismatch`.

- [ ] **Step 1: aggiungere `target` alla dataclass `Edit`**

In `modules/utility/rapporti_check.py`, la dataclass `Edit` (riga 43) diventa:

```python
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
    """
    us: str
    add: tuple = ()
    remove: tuple = ()
    set_fields: tuple = ()
    target: tuple = ()
```

- [ ] **Step 2: scrivere il test che fallisce (sovrapposizione)**

Creare `tests/utility/test_chronology_check.py`:

```python
"""Il giudizio sulla cronologia di un sito, senza database e senza QGIS.

Le righe sono costruite a mano: `check_chronology` non deve sapere da dove
vengono, ed è questo che lo rende provabile.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility import chronology_check as CC


def _p(periodo, fase, ini, fin, estesa="XV secolo"):
    return {"periodo": periodo, "fase": fase, "cron_iniziale": ini,
            "cron_finale": fin, "datazione_estesa": estesa}


def test_two_phases_with_the_same_span_are_one_overlap():
    """Due fasi con lo stesso intervallo sono UNA sovrapposizione, non due.

    È il caso del database di Enzo: 2/2.2 e 3/1 portano entrambe 1500–1549.
    """
    periods = [_p("2", "2.2", 1500, 1549), _p("3", "1", 1500, 1549)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_overlap"]
    assert issues[0].auto is False
    assert "1500" in issues[0].summary and "1549" in issues[0].summary
    assert "50" in issues[0].summary          # 1549 - 1500 + 1 anni sovrapposti


def test_identical_spans_carry_no_proposal():
    """Con due intervalli identici non esiste un restringimento possibile.

    Alzare l'inizio della più recente a 1550 la farebbe finire prima di
    cominciare. Si segnala e basta: chi si sposta lo sa solo chi ha scavato.
    """
    periods = [_p("2", "2.2", 1500, 1549), _p("3", "1", 1500, 1549)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert issues[0].edits == []


def test_partial_overlap_proposes_moving_the_more_recent_start():
    periods = [_p("2", "2.2", 1500, 1600), _p("3", "1", 1550, 1650)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert len(issues) == 1
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", 1601),)
    assert edit.target == ("periodizzazione_table",
                           {"periodo": "3", "fase": "1"})


def test_spans_that_touch_without_overlapping_are_not_an_issue():
    periods = [_p("2", "2.2", 1450, 1499), _p("3", "1", 1500, 1549)]
    assert CC.check_chronology(periods, [], sito="S") == []
```

- [ ] **Step 3: lanciarlo e vederlo fallire**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_check.py -q -p no:warnings
```
Expected: FAIL in collection — `ModuleNotFoundError: No module named 'modules.utility.chronology_check'`.

- [ ] **Step 4: scrivere il modulo con la sola rilevazione delle fasi**

Creare `modules/utility/chronology_check.py`:

```python
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
    """
    if val is None or isinstance(val, bool):
        return None
    try:
        return int(str(val).strip())
    except (TypeError, ValueError):
        return None


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
```

- [ ] **Step 5: lanciare e vedere passare**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_check.py -q -p no:warnings
```
Expected: FAIL — `KeyError: 's_epoch_overlap'` da `_t`: le voci localizzate non ci sono ancora.

- [ ] **Step 6: aggiungere le voci in `_L`, sei lingue**

In `modules/utility/rapporti_check.py`, dentro `_L`, in coda al blocco di ciascuna lingua (dopo l'ultima voce di quel blocco, prima della `}` che lo chiude).

`"it"`:
```python
        "t_epoch_overlap": "Fasi con intervalli sovrapposti (scelta manuale)",
        "t_epoch_reversed": "Periodizzazione con inizio dopo la fine",
        "t_epoch_no_dates": "Fase senza anni (solo segnalazione)",
        "t_datazione_mismatch": "Datazione della scheda disallineata (verrà riscritta)",
        "s_epoch_overlap": "Le fasi {a} e {b} si sovrappongono per {anni} anni ({ini}–{fin})",
        "s_epoch_reversed": "Fase {fase}: inizio {ini} dopo la fine {fin} (i due anni si scambiano)",
        "s_epoch_no_dates": "Fase {fase}: nessun anno leggibile in cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (fase {fase}): datazione «{corrente}» invece di «{atteso}»",
```

`"en"`:
```python
        "t_epoch_overlap": "Phases with overlapping spans (manual choice)",
        "t_epoch_reversed": "Periodization starting after it ends",
        "t_epoch_no_dates": "Phase with no years (report only)",
        "t_datazione_mismatch": "Sheet dating out of step (will be rewritten)",
        "s_epoch_overlap": "Phases {a} and {b} overlap by {anni} years ({ini}–{fin})",
        "s_epoch_reversed": "Phase {fase}: starts {ini} after it ends {fin} (the two years swap)",
        "s_epoch_no_dates": "Phase {fase}: no readable year in cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (phase {fase}): dating «{corrente}» instead of «{atteso}»",
```

`"de"`:
```python
        "t_epoch_overlap": "Phasen mit überlappenden Zeiträumen (manuelle Wahl)",
        "t_epoch_reversed": "Periodisierung beginnt nach ihrem Ende",
        "t_epoch_no_dates": "Phase ohne Jahresangaben (nur Hinweis)",
        "t_datazione_mismatch": "Datierung im Formular abweichend (wird überschrieben)",
        "s_epoch_overlap": "Die Phasen {a} und {b} überlappen sich um {anni} Jahre ({ini}–{fin})",
        "s_epoch_reversed": "Phase {fase}: beginnt {ini} nach dem Ende {fin} (die Jahre werden getauscht)",
        "s_epoch_no_dates": "Phase {fase}: kein lesbares Jahr in cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (Phase {fase}): Datierung «{corrente}» statt «{atteso}»",
```

`"es"`:
```python
        "t_epoch_overlap": "Fases con intervalos superpuestos (elección manual)",
        "t_epoch_reversed": "Periodización que empieza después de terminar",
        "t_epoch_no_dates": "Fase sin años (solo aviso)",
        "t_datazione_mismatch": "Datación de la ficha desalineada (se reescribirá)",
        "s_epoch_overlap": "Las fases {a} y {b} se superponen {anni} años ({ini}–{fin})",
        "s_epoch_reversed": "Fase {fase}: empieza {ini} después de terminar {fin} (los dos años se intercambian)",
        "s_epoch_no_dates": "Fase {fase}: ningún año legible en cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (fase {fase}): datación «{corrente}» en vez de «{atteso}»",
```

`"fr"`:
```python
        "t_epoch_overlap": "Phases aux intervalles qui se chevauchent (choix manuel)",
        "t_epoch_reversed": "Périodisation qui commence après sa fin",
        "t_epoch_no_dates": "Phase sans années (signalement seul)",
        "t_datazione_mismatch": "Datation de la fiche décalée (elle sera réécrite)",
        "s_epoch_overlap": "Les phases {a} et {b} se chevauchent sur {anni} ans ({ini}–{fin})",
        "s_epoch_reversed": "Phase {fase} : commence en {ini} après sa fin {fin} (les deux années sont échangées)",
        "s_epoch_no_dates": "Phase {fase} : aucune année lisible dans cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (phase {fase}) : datation «{corrente}» au lieu de «{atteso}»",
```

`"pt"`:
```python
        "t_epoch_overlap": "Fases com intervalos sobrepostos (escolha manual)",
        "t_epoch_reversed": "Periodização que começa depois de terminar",
        "t_epoch_no_dates": "Fase sem anos (apenas aviso)",
        "t_datazione_mismatch": "Datação da ficha desalinhada (será reescrita)",
        "s_epoch_overlap": "As fases {a} e {b} sobrepõem-se em {anni} anos ({ini}–{fin})",
        "s_epoch_reversed": "Fase {fase}: começa em {ini} depois de terminar {fin} (os dois anos são trocados)",
        "s_epoch_no_dates": "Fase {fase}: nenhum ano legível em cron_iniziale/cron_finale",
        "s_datazione_mismatch": "US {us} (fase {fase}): datação «{corrente}» em vez de «{atteso}»",
```

- [ ] **Step 7: lanciare e vedere passare**

Run: lo stesso comando dello Step 5.
Expected: PASS, 4 passed.

- [ ] **Step 8: i test che restano della rilevazione sulle fasi**

In coda a `tests/utility/test_chronology_check.py`:

```python
def test_reversed_span_swaps_the_two_years_automatically():
    periods = [_p("2", "2.2", 1549, 1500)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_reversed"]
    assert issues[0].auto is True
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", 1500), ("cron_finale", 1549))
    assert edit.target == ("periodizzazione_table",
                           {"periodo": "2", "fase": "2.2"})


def test_a_reversed_span_is_not_also_an_overlap():
    """Un intervallo rovesciato esce dal confronto: un problema per volta.

    La riverifica che segue l'applicazione lo guarda da capo, raddrizzato.
    """
    periods = [_p("2", "2.2", 1549, 1500), _p("3", "1", 1480, 1560)]
    kinds = [i.kind for i in CC.check_chronology(periods, [], sito="S")]
    assert kinds == ["epoch_reversed"]


def test_phase_without_years_is_reported_and_not_automatic():
    periods = [_p("2", "2.2", None, None)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_no_dates"]
    assert issues[0].auto is False
    assert issues[0].edits == []
    assert "2/2.2" in issues[0].summary


def test_a_year_written_as_text_is_a_phase_without_years_not_a_crash():
    periods = [_p("2", "2.2", "XV sec", 1499)]
    assert [i.kind for i in CC.check_chronology(periods, [], sito="S")] \
        == ["epoch_no_dates"]


def test_bc_years_are_negative_and_year_zero_is_a_year():
    """Le date a.C. si scrivono negative, e lo zero è un anno come gli altri.

    Senza questo, uno `if not ini` leggerebbe l'anno 0 come «nessun anno» e
    una periodizzazione a cavallo dell'era non si verificherebbe mai.
    """
    periods = [_p("1", "1", -100, 0), _p("1", "2", -50, 50)]
    issues = CC.check_chronology(periods, [], sito="S")
    assert [i.kind for i in issues] == ["epoch_overlap"]
    edit, = issues[0].edits
    assert edit.set_fields == (("cron_iniziale", 1),)
    assert edit.target == ("periodizzazione_table",
                           {"periodo": "1", "fase": "2"})


def test_phase_2_1_and_2_10_stay_distinct():
    """Come float sarebbero la stessa fase, e una delle due si perderebbe."""
    periods = [_p("2", "2.1", 1400, 1450), _p("2", "2.10", 1500, 1550)]
    assert CC.check_chronology(periods, [], sito="S") == []


def test_empty_periodization_is_not_an_error():
    assert CC.check_chronology([], [], sito="S") == []


def test_the_four_titles_exist_in_all_six_languages():
    from modules.utility import rapporti_check as RC
    for kind in ("epoch_overlap", "epoch_reversed", "epoch_no_dates",
                 "datazione_mismatch"):
        for lang in ("it", "en", "de", "es", "fr", "pt"):
            titolo = RC.kind_title(kind, lang)
            assert titolo and not titolo.startswith("t_"), (kind, lang)
```

- [ ] **Step 9: lanciare e vedere passare**

Run: lo stesso comando dello Step 5.
Expected: PASS, 12 passed.

- [ ] **Step 10: commit**

```bash
git add modules/utility/chronology_check.py modules/utility/rapporti_check.py \
        tests/utility/test_chronology_check.py
git commit -m "feat(cronologia): le fasi che si sovrappongono, si rovesciano o non hanno anni"
```

---

### Task 2: `datazione_mismatch` — la scheda che non dice quello che dice la sua fase

**Files:**
- Modify: `modules/utility/chronology_check.py`
- Test: `tests/utility/test_chronology_check.py`

**Interfaces:**
- Consumes: da Task 1 → `_key`, `_label`, `_text`, `check_chronology`, `DATAZIONE_MISMATCH`, la voce `_L` `s_datazione_mismatch`.
- Produces: `_mismatches(periods, units, lang) -> list[Issue]`, chiamata da `check_chronology` dopo `_overlaps`. Le sue `Edit` hanno `target=()` e `set_fields=(("datazione", <atteso>),)`.

- [ ] **Step 1: scrivere i test che falliscono**

In coda a `tests/utility/test_chronology_check.py`:

```python
def _u(us, periodo, fase, datazione):
    return {"us": us, "periodo_iniziale": periodo, "fase_iniziale": fase,
            "datazione": datazione}


def test_sheet_dating_out_of_step_is_rewritten_from_the_periodization():
    """La periodizzazione è la fonte e la scheda la copia (Enzo, 2026-10-10).

    Riscrivere la copia dalla fonte non ha alternative: automatica.
    """
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", "Prima metà del XV secolo")]
    issues = CC.check_chronology(periods, units, sito="S")
    assert [i.kind for i in issues] == ["datazione_mismatch"]
    assert issues[0].auto is True
    edit, = issues[0].edits
    assert edit.us == "12"
    assert edit.set_fields == (("datazione", "XV secolo"),)
    assert edit.target == ()          # us_table, come sempre


def test_the_summary_shows_both_texts():
    """L'anteprima è l'unico punto in cui si vede cosa si sta per riscrivere,
    e su un sito tradotto sono cinquantuno righe in un colpo."""
    periods = [_p("2", "2", 1500, 1549, "First half of the 16th century")]
    units = [_u("4", "2", "2", "Prima metà del XVI secolo")]
    issues = CC.check_chronology(periods, units, sito="S")
    assert "Prima metà del XVI secolo" in issues[0].summary
    assert "First half of the 16th century" in issues[0].summary


def test_matching_dating_is_not_an_issue():
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", "XV secolo")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_an_empty_sheet_dating_is_filled_from_its_phase():
    """Sul database di esempio sono quattro per sito: la fonte c'è e la copia
    manca, che è la stessa regola."""
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", None)]
    issues = CC.check_chronology(periods, units, sito="S")
    assert [i.kind for i in issues] == ["datazione_mismatch"]
    assert issues[0].edits[0].set_fields == (("datazione", "XV secolo"),)


def test_none_and_empty_string_say_the_same_thing():
    """`datazione = None` nella scheda e `datazione_estesa = ''` nella
    periodizzazione non sono un disallineamento: sono due vuoti."""
    periods = [_p("2", "3", 1451, 1499, "")]
    units = [_u("12", "2", "3", None)]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_an_empty_source_never_blanks_a_filled_sheet():
    """Senza questa regola la verifica svuoterebbe le schede dei siti con la
    periodizzazione incompleta: non c'è niente da copiare."""
    periods = [_p("2", "3", 1451, 1499, None)]
    units = [_u("12", "2", "3", "XV secolo")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_a_unit_without_a_period_has_no_source_to_copy_from():
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "", "", "qualcosa")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_a_unit_pointing_at_a_phase_that_does_not_exist_is_skipped():
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "9", "9", "qualcosa")]
    assert CC.check_chronology(periods, units, sito="S") == []


def test_whitespace_around_the_dating_is_not_a_mismatch():
    periods = [_p("2", "3", 1451, 1499, "XV secolo")]
    units = [_u("12", "2", "3", "  XV secolo  ")]
    assert CC.check_chronology(periods, units, sito="S") == []
```

- [ ] **Step 2: lanciarli e vederli fallire**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_check.py -q -p no:warnings
```
Expected: FAIL — `test_sheet_dating_out_of_step_is_rewritten_from_the_periodization` dà `assert [] == ['datazione_mismatch']`: `check_chronology` ignora ancora `units`.

- [ ] **Step 3: scrivere `_mismatches` e chiamarla**

In `modules/utility/chronology_check.py`, prima di `check_chronology`:

```python
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
```

e in `check_chronology`, dopo `issues.extend(_overlaps(spans, lang))`:

```python
    issues.extend(_mismatches(periods, units, lang))
```

- [ ] **Step 4: lanciare e vedere passare**

Run: lo stesso comando dello Step 2.
Expected: PASS, 21 passed.

- [ ] **Step 5: commit**

```bash
git add modules/utility/chronology_check.py tests/utility/test_chronology_check.py
git commit -m "feat(cronologia): la datazione della scheda si riallinea alla sua fase"
```

---

### Task 3: `apply_edits` scrive in più di una tabella

**Files:**
- Modify: `modules/utility/rapporti_check.py:541-637` (`_PERIOD_COL_WHITELIST`, `apply_edits`, `rollback`, `_read_rapporti`)
- Test: `tests/utility/test_chronology_apply.py`

**Interfaces:**
- Consumes: da Task 1 → `Edit.target`; il `target` prodotto da `_period_target`, cioè `("periodizzazione_table", {"periodo": "2", "fase": "2.2"})`.
- Produces: `_WRITABLE: dict[str, set[str]]`; `_target_of(edit) -> tuple[str, tuple[tuple[str, str], ...]]`; `_where(tabella, chiave, row_sito) -> tuple[str, dict]`; `apply_edits(edits, handle, *, sito=None) -> RollbackToken` con `RollbackToken.snapshot` ora indicizzato su `(tabella, chiave)`; `rollback(token, handle)`.

**Tre decisioni, dette qui perché la spec non le dice:**

1. **Le colonne della chiave si confrontano come testo.** `periodizzazione_table.periodo` è `Integer` nello schema e `fase` è `Text`. Su PostgreSQL, che non converte da sé, una chiave passata come stringa contro una colonna intera dà `operator does not exist: integer = text` — la deriva di schema che si nasconde sotto SQLite e salta fuori su PG. Il `CAST(col AS TEXT)` toglie il problema in tutti e due i motori; la tabella è di decine di righe, quindi l'indice non manca a nessuno. Vale anche per `us_table.us`, dove è una robustezza in più e non un cambio di comportamento (una `us` di testo resta tale, una intera si confronta come prima).
2. **Un `target` diverso da `us_table` senza `sito` si rifiuta.** Senza la clausola sul sito, `(periodo, fase)` individua la stessa fase in tutti e dieci i siti del database. Meglio un `ValueError` che dieci siti riscritti.
3. **Lo snapshot tiene il valore di prima della prima correzione.** Le `Edit` sulla stessa riga si raggruppano e si applicano con una `UPDATE` sola, quindi lo snapshot si legge una volta, prima di scrivere.

- [ ] **Step 1: scrivere i test che falliscono**

Creare `tests/utility/test_chronology_apply.py`:

```python
"""Le correzioni cronologiche atterrano nella tabella giusta, e si annullano.

Su SQLite di prova: la scrittura si guarda, non si deduce.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility import rapporti_check as RC


def _db(tmp_path):
    """us_table e periodizzazione_table, due siti, con i tipi dello schema:
    `periodo` intero e `fase` testo, che è dove PostgreSQL inciampa."""
    from s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "chrono.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, us TEXT, rapporti TEXT,"
              " periodo_iniziale TEXT, fase_iniziale TEXT,"
              " periodo_finale TEXT, fase_finale TEXT, datazione TEXT)")
    c.execute("CREATE TABLE periodizzazione_table (sito TEXT,"
              " periodo INTEGER, fase TEXT, cron_iniziale INTEGER,"
              " cron_finale INTEGER, datazione_estesa TEXT, descrizione TEXT)")
    c.execute("INSERT INTO us_table VALUES ('S','12','[]','2','3','2','3',"
              "'Prima metà del XV secolo')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',2,'2.2',1500,1549,'Prima metà del XVI secolo','')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',3,'1',1500,1549,'Prima metà del XV secolo rec','')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('ALTRO',2,'2.2',1500,1549,'non toccare','')")
    c.commit(); c.close()
    return DbHandle.from_path(p)


def _periodo(h, sito, periodo, fase):
    from sqlalchemy import text
    with h.engine.connect() as c:
        return c.execute(text(
            "SELECT cron_iniziale, cron_finale FROM periodizzazione_table "
            "WHERE sito = :s AND CAST(periodo AS TEXT) = :p AND fase = :f"),
            {"s": sito, "p": periodo, "f": fase}).fetchone()


def test_a_period_edit_writes_in_the_periodization(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    assert _periodo(h, "S", "2", "2.2") == (1500, 1480)
    with h.engine.connect() as c:
        # us_table non è stata sfiorata: nessuna riga 'us' = '2/2.2'
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_a_period_edit_leaves_the_other_sites_alone(tmp_path):
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    assert _periodo(h, "ALTRO", "2", "2.2") == (1500, 1549)


def test_a_period_edit_without_a_sito_refuses_to_write(tmp_path):
    """(periodo, fase) senza sito è la stessa fase in dieci siti."""
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    with pytest.raises(ValueError, match="sito"):
        RC.apply_edits([e], h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
    assert _periodo(h, "ALTRO", "2", "2.2") == (1500, 1549)


def test_an_edit_without_a_target_still_writes_in_us_table(tmp_path):
    """Nessuna chiamata esistente cambia: `target` vuoto vale us_table."""
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="12", set_fields=(("datazione", "XV secolo"),))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("XV secolo",)


def test_a_column_outside_the_whitelist_is_not_written(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("descrizione", "cancellata"),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text(
            "SELECT descrizione FROM periodizzazione_table "
            "WHERE sito='S' AND fase='2.2'")).fetchone() == ("",)


def test_datazione_is_writable_in_us_table_and_cron_is_not(tmp_path):
    """La whitelist è per tabella: `datazione` solo in us_table."""
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="12", set_fields=(("cron_iniziale", 1),))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_rollback_restores_both_tables(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    edits = [
        RC.Edit(us="12", set_fields=(("datazione", "XV secolo"),)),
        RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"})),
    ]
    tok = RC.apply_edits(edits, h, sito="S")
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_two_edits_on_the_same_row_roll_back_to_the_first_value(tmp_path):
    """Una fase che si sovrappone a due altre produce due Edit sulla stessa
    riga: si applicano insieme, e l'annulla torna a prima della prima."""
    h = _db(tmp_path)
    target = ("periodizzazione_table", {"periodo": "2", "fase": "2.2"})
    edits = [RC.Edit(us="2/2.2", set_fields=(("cron_iniziale", 1510),),
                     target=target),
             RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1540),),
                     target=target)]
    tok = RC.apply_edits(edits, h, sito="S")
    assert _periodo(h, "S", "2", "2.2") == (1510, 1540)
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)


def test_an_edit_whose_row_is_gone_writes_nothing_and_does_not_raise(tmp_path):
    """Qualcuno ha cancellato la fase nel frattempo: zero righe aggiornate, e
    la riverifica che segue ripresenta il problema."""
    h = _db(tmp_path)
    e = RC.Edit(us="9/9", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "9", "fase": "9"}))
    tok = RC.apply_edits([e], h, sito="S")
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
```

- [ ] **Step 2: lanciarli e vederli fallire**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_apply.py -q -p no:warnings
```
Expected: FAIL — `test_a_period_edit_writes_in_the_periodization` dà `(1500, 1549)` invece di `(1500, 1480)`: `apply_edits` scrive solo in `us_table` e `cron_finale` non è in whitelist.

- [ ] **Step 3: riscrivere la macchina di scrittura**

In `modules/utility/rapporti_check.py`, sostituire il blocco da `def _read_rapporti` (riga 534) fino alla fine di `rollback` (riga 637) con:

```python
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


def _where(tabella, chiave, row_sito):
    """La clausola che individua la riga, e i suoi parametri.

    Le colonne della chiave si confrontano **come testo**:
    ``periodizzazione_table.periodo`` è ``Integer`` nello schema e ``fase`` è
    ``Text``, e PostgreSQL — che non converte da sé — su una chiave di testo
    contro una colonna intera dà «operator does not exist: integer = text».
    Il ``CAST`` lo toglie in tutti e due i motori, e la tabella è di decine di
    righe.
    """
    if tabella != "us_table" and row_sito is None:
        raise ValueError(
            "una correzione su %s ha bisogno del sito: senza, la chiave %s "
            "individua la stessa riga in tutti i siti"
            % (tabella, dict(chiave)))
    parti, params = [], {}
    if row_sito is not None:
        parti.append("sito = :w_sito")
        params["w_sito"] = row_sito
    for i, (col, val) in enumerate(chiave):
        parti.append("CAST(%s AS TEXT) = :w_%d" % (col, i))
        params["w_%d" % i] = str(val)
    return " AND ".join(parti), params


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
            # _where lo pretende.
            if tabella == "us_table" and sito is None:
                r = conn.execute(text(
                    "SELECT sito FROM us_table WHERE CAST(us AS TEXT) = :u"),
                    {"u": dict(chiave)["us"]}).fetchone()
                row_sito = r[0] if r else None
            else:
                row_sito = sito
            where, wparams = _where(tabella, chiave, row_sito)

            # Snapshot: i valori di prima, letti con la stessa clausola con
            # cui si scriverà.
            cols = (["rapporti"] if touch_rapporti else []) + field_cols
            orig = {}
            r = conn.execute(text("SELECT %s FROM %s WHERE %s"
                                  % (", ".join(cols), tabella, where)),
                             wparams).fetchone()
            if r is not None:
                for i, c in enumerate(cols):
                    orig[c] = r[i]
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
```

Aggiornare anche la docstring di `RollbackToken` (riga 529):

```python
@_dc
class RollbackToken:
    sito: str
    snapshot: dict   # (tabella, chiave) -> (sito della riga, valori originali)
```

`_read_rapporti` e `_PERIOD_COL_WHITELIST` sparicono: la lettura passa dallo snapshot, la whitelist è `_WRITABLE`. Nessun altro file li nomina (verificato: l'unica altra occorrenza di `_PERIOD_COL_WHITELIST` è nella spec).

- [ ] **Step 4: lanciare e vedere passare**

Run: lo stesso comando dello Step 2.
Expected: PASS, 9 passed.

- [ ] **Step 5: provare che i rapporti non sono regrediti**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/sync/test_rapporti_check.py tests/sync/test_rapporti_check_live.py \
  tests/utility/test_chronology_check.py -q -p no:warnings
```
Expected: PASS — in particolare `test_apply_and_rollback`, `test_apply_set_fields_writes_period_and_rolls_back`, `test_apply_mixed_rapporti_and_fields` e `test_set_fields_only_no_rapporti_unchanged`, che sono i quattro che coprono la vecchia macchina di scrittura.

- [ ] **Step 6: commit**

```bash
git add modules/utility/rapporti_check.py tests/utility/test_chronology_apply.py
git commit -m "fix(correzioni): la correzione sa in quale tabella e con quale chiave scrivere"
```

---

### Task 4: `load_chronology_rows` — le righe, per un sito solo

**Files:**
- Modify: `modules/utility/chronology_check.py`
- Test: `tests/utility/test_chronology_apply.py`

**Interfaces:**
- Consumes: un `handle` con `.engine` (`s3dgraphy.sync._db_handle.DbHandle`), come lo usa già `temporal_check.load_unit_periods`.
- Produces: `load_chronology_rows(handle, sito) -> tuple[list[dict], list[dict]]`, nella forma che `check_chronology` prende: `(periods, units)`.

- [ ] **Step 1: scrivere il test che fallisce**

In coda a `tests/utility/test_chronology_apply.py`:

```python
def test_load_chronology_rows_reads_one_site_only(tmp_path):
    """Senza il filtro, le 2 sovrapposizioni di un sito diventano le 20 del
    database, e la correzione automatica riscriverebbe dieci siti in un colpo.
    """
    from modules.utility import chronology_check as CC
    h = _db(tmp_path)
    periods, units = CC.load_chronology_rows(h, "S")
    assert len(periods) == 2
    assert {p["datazione_estesa"] for p in periods} == {
        "Prima metà del XVI secolo", "Prima metà del XV secolo rec"}
    assert [u["us"] for u in units] == ["12"]


def test_load_chronology_rows_keeps_the_phase_key_as_text(tmp_path):
    """`periodo` è Integer nello schema: se arrivasse come 2 la chiave della
    fase diventerebbe (2, '2.2') e non combacerebbe con nessun atteso."""
    from modules.utility import chronology_check as CC
    h = _db(tmp_path)
    periods, _ = CC.load_chronology_rows(h, "S")
    chiavi = {CC._key(p) for p in periods}
    assert chiavi == {("2", "2.2"), ("3", "1")}


def test_the_sample_shaped_rows_go_straight_into_check_chronology(tmp_path):
    """Le due funzioni combaciano senza adattatori in mezzo."""
    from modules.utility import chronology_check as CC
    h = _db(tmp_path)
    periods, units = CC.load_chronology_rows(h, "S")
    kinds = sorted(i.kind for i in CC.check_chronology(
        periods, units, sito="S"))
    assert kinds == ["datazione_mismatch", "epoch_overlap"]
```

- [ ] **Step 2: lanciarli e vederli fallire**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_apply.py -q -p no:warnings
```
Expected: FAIL — `AttributeError: module 'modules.utility.chronology_check' has no attribute 'load_chronology_rows'`.

- [ ] **Step 3: scrivere la lettura**

In coda a `modules/utility/chronology_check.py`:

```python
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
```

- [ ] **Step 4: lanciare e vedere passare**

Run: lo stesso comando dello Step 2.
Expected: PASS, 12 passed.

- [ ] **Step 5: commit**

```bash
git add modules/utility/chronology_check.py tests/utility/test_chronology_apply.py
git commit -m "feat(cronologia): le righe della verifica si leggono per un sito solo"
```

---

### Task 5: l'innesto nel dialogo

**Files:**
- Modify: `gui/rapporti_check_dialog.py:138-211` (`_run`, `_render`, `_selected_auto_issues`, `_preview`)
- Modify: `modules/utility/chronology_check.py` (`edit_prefix`)
- Test: `tests/utility/test_chronology_check.py`

**Interfaces:**
- Consumes: da Task 1/2 → `check_chronology`; da Task 4 → `load_chronology_rows`; da Task 3 → `Edit.target`.
- Produces: `edit_prefix(edit) -> str`, usata da `_preview`; `RapportiCheckPanel._selected_issues()` (era `_selected_auto_issues`).

**Un cambio di comportamento oltre la lettera della spec, deliberato.** La spec vuole che la proposta di `epoch_overlap` «si applichi solo se spuntata». Oggi `_render` mette la spunta solo su `iss.auto and iss.edits` e `_selected_auto_issues` pretende `iss.auto`: una issue manuale **con** correzione suggerita non è spuntabile, quindi non è applicabile. La regola nuova è una e vale per tutte: **spuntabile se ha correzioni, spuntata di suo solo se automatica.** Conseguenza: anche i suggerimenti di `contradiction_ambiguous` e `cycle`, che esistono da giugno e finora si leggevano e basta, diventano applicabili **se l'archeologo li spunta a mano**. È quello che la spec chiede per le sovrapposizioni, e trattare le altre manuali in modo diverso vorrebbe dire un caso speciale per categoria.

- [ ] **Step 1: scrivere il test che fallisce (il prefisso dell'anteprima)**

In coda a `tests/utility/test_chronology_check.py`:

```python
def test_edit_prefix_names_the_us_when_there_is_no_target():
    from modules.utility.rapporti_check import Edit
    assert CC.edit_prefix(Edit(us="12")) == "US 12"


def test_edit_prefix_names_the_row_when_the_target_is_another_table():
    """«US 2/2.2» mentirebbe sulla riga che si sta per cambiare."""
    from modules.utility.rapporti_check import Edit
    e = Edit(us="2/2.2", target=("periodizzazione_table",
                                 {"periodo": "2", "fase": "2.2"}))
    assert CC.edit_prefix(e) == "periodizzazione_table fase=2.2 periodo=2"
```

- [ ] **Step 2: lanciarli e vederli fallire**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_check.py -q -p no:warnings
```
Expected: FAIL — `AttributeError: module 'modules.utility.chronology_check' has no attribute 'edit_prefix'`.

- [ ] **Step 3: scrivere `edit_prefix`**

In `modules/utility/chronology_check.py`, dopo `_period_target`:

```python
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
```

- [ ] **Step 4: lanciare e vedere passare**

Run: lo stesso comando dello Step 2.
Expected: PASS, 23 passed.

- [ ] **Step 5: innestare la verifica in `_run`**

In `gui/rapporti_check_dialog.py`, dentro `_run`, sostituire

```python
            from modules.s3dgraphy.sync.graph_projector import GraphProjector
            from modules.utility import temporal_check as TC
            handle = self._handle()
            graph = GraphProjector().populate_graph(handle, sito=sito)
            chrono = TC.build_chronology(handle, sito)
            unit_periods = TC.load_unit_periods(handle, sito)
            self._report = RC.check_rapporti(
                graph, sito=sito, lang=self._lang,
                chrono=chrono, unit_periods=unit_periods)
```

con

```python
            from modules.s3dgraphy.sync.graph_projector import GraphProjector
            from modules.utility import chronology_check as CC
            from modules.utility import temporal_check as TC
            handle = self._handle()
            graph = GraphProjector().populate_graph(handle, sito=sito)
            chrono = TC.build_chronology(handle, sito)
            unit_periods = TC.load_unit_periods(handle, sito)
            self._report = RC.check_rapporti(
                graph, sito=sito, lang=self._lang,
                chrono=chrono, unit_periods=unit_periods)
            # Gli avvisi cronologici sono altre categorie dello stesso albero:
            # _render raggruppa per `kind` e non ha bisogno di sapere da quale
            # verifica arrivano.
            periods, units = CC.load_chronology_rows(handle, sito)
            self._report.issues.extend(CC.check_chronology(
                periods, units, sito=sito, lang=self._lang))
            # La cronologia calcolata, per la provenienza nell'anteprima.
            self._chrono_bounds = graph.chronology()
```

e in `__init__` (riga 45-55), accanto a `self._report`, aggiungere:

```python
        self._chrono_bounds = {}
```

- [ ] **Step 6: rendere spuntabili le proposte manuali**

In `_render`, sostituire

```python
                if iss.auto and iss.edits:
                    child.setCheckState(0, Qt.Checked)
                    n_auto += 1
```

con

```python
                if iss.edits:
                    # Spuntabile perché una correzione c'è; spuntata di suo
                    # solo se automatica. Una proposta — la fase da
                    # restringere, il rapporto da togliere a un ciclo — si
                    # applica solo se l'archeologo la spunta.
                    child.setCheckState(0, Qt.Checked if iss.auto
                                        else Qt.Unchecked)
                    if iss.auto:
                        n_auto += 1
```

e rinominare `_selected_auto_issues` in `_selected_issues`, togliendo il requisito `iss.auto`:

```python
    def _selected_issues(self):
        """Le issue spuntate che hanno una correzione: le automatiche sono
        spuntate di suo, le proposte solo se l'archeologo le ha spuntate."""
        out = []
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                ch = top.child(j)
                iss = ch.data(0, _USER_ROLE)
                if (iss is not None and iss.edits
                        and ch.checkState(0) == Qt.Checked):
                    out.append(iss)
        return out
```

In `_apply`, la prima riga diventa:

```python
        issues = self._selected_issues()
```

- [ ] **Step 7: il prefisso giusto nell'anteprima**

In `_preview`, sostituire

```python
        for e in iss.edits:
            for r in e.remove:
                lines.append(f"US {e.us}: rimuovi  {list(r)}")
            for a in e.add:
                lines.append(f"US {e.us}: aggiungi {list(a)}")
            for (col, val) in getattr(e, "set_fields", ()):
                lines.append(f"US {e.us}: imposta {col} = {val}")
```

con

```python
        from modules.utility import chronology_check as CC
        for e in iss.edits:
            chi = CC.edit_prefix(e)
            for r in e.remove:
                lines.append(f"{chi}: rimuovi  {list(r)}")
            for a in e.add:
                lines.append(f"{chi}: aggiungi {list(a)}")
            for (col, val) in getattr(e, "set_fields", ()):
                lines.append(f"{chi}: imposta {col} = {val}")
```

- [ ] **Step 8: provare che nulla è regredito**

Run (la suite canonica intera):
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/sync tests/utility tests/migrations -q --continue-on-collection-errors \
  --ignore=tests/sync/test_groups_dialog_smoke.py \
  --ignore=tests/sync/test_paradata_dialog_smoke.py -p no:warnings
```
Expected: 0 failure, 8 errori d'ambiente, 1 xfail, 1 skip — la baseline, più i test nuovi passati. Qualunque failure va inseguita con superpowers:systematic-debugging, non aggirata.

- [ ] **Step 9: commit**

```bash
git add gui/rapporti_check_dialog.py modules/utility/chronology_check.py \
        tests/utility/test_chronology_check.py
git commit -m "feat(verifica rapporti): gli avvisi cronologici stanno nello stesso albero"
```

---

### Task 6: i numeri veri, sul database di esempio

**Files:**
- Test: `tests/utility/test_chronology_live.py` (nuovo)

**Interfaces:**
- Consumes: `load_chronology_rows`, `check_chronology`, `apply_edits`, `rollback`; il database `resources/dbfiles/pyarchinit_db.sqlite`, copiato in `tmp_path` come fa `tests/sync/test_rapporti_check_live.py`.
- Produces: niente codice di produzione. È il test che prova che le quattro categorie trovano quello che c'è, non quello che si crede ci sia.

**I numeri, misurati sul database di esempio prima di scrivere il piano:**

| sito | fasi | US | `epoch_overlap` | con proposta | `epoch_reversed` | `epoch_no_dates` | `datazione_mismatch` |
|---|---|---|---|---|---|---|---|
| Scavo archeologico | 12 | 51 | **2** | **0** | 0 | 0 | **13** (9 diverse + 4 vuote) |
| ciascuno dei 9 tradotti | 12 | 51 | **2** | **0** | 0 | 0 | **51** (47 diverse + 4 vuote) |
| **tutti e dieci** | | | **20** | **0** | **0** | **0** | **472** |

- [ ] **Step 1: scrivere il test che fallisce**

Creare `tests/utility/test_chronology_live.py`:

```python
"""La verifica cronologica sul database di esempio: i numeri, non le opinioni.

Le quattro categorie si provano su righe costruite a mano in
`test_chronology_check.py`. Qui si prova che su un database vero trovano
quello che c'è — e che una seconda verifica non ripresenta quello che la
prima ha corretto.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility import chronology_check as CC
from modules.utility import rapporti_check as RC

ITALIANO = "Scavo archeologico"
TRADOTTO = "Archaeological Excavation"


@pytest.fixture()
def handle(tmp_path):
    """Una copia del database di esempio: l'originale non si apre mai in
    scrittura — il QGIS di Enzo lo tiene aperto in WAL."""
    from s3dgraphy.sync._db_handle import DbHandle
    sorgente = _ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
    if not sorgente.exists():
        pytest.skip("database di esempio non presente")
    copia = tmp_path / "db.sqlite"
    shutil.copy(sorgente, copia)
    return DbHandle.from_path(copia)


def _per_kind(handle, sito):
    periods, units = CC.load_chronology_rows(handle, sito)
    issues = CC.check_chronology(periods, units, sito=sito)
    out = {}
    for i in issues:
        out.setdefault(i.kind, []).append(i)
    return out


def test_the_italian_site_has_two_overlaps_and_thirteen_misalignments(handle):
    per_kind = _per_kind(handle, ITALIANO)
    assert len(per_kind.get("epoch_overlap", [])) == 2
    assert len(per_kind.get("datazione_mismatch", [])) == 13
    assert per_kind.get("epoch_reversed", []) == []
    assert per_kind.get("epoch_no_dates", []) == []


def test_the_two_overlaps_carry_no_proposal(handle):
    """Le due coppie portano intervalli identici — 1500–1549 e 1451–1499 —
    e qualunque restringimento farebbe finire una fase prima di cominciare."""
    for iss in _per_kind(handle, ITALIANO)["epoch_overlap"]:
        assert iss.edits == [], iss.summary
        assert iss.auto is False


def test_a_translated_site_has_fifty_one_misalignments_with_both_texts(handle):
    """La periodizzazione è tradotta e la datazione nella scheda è rimasta in
    italiano: il summary deve mostrare tutti e due i testi, perché
    l'anteprima è l'unico punto in cui si vede cosa si sta per riscrivere."""
    issues = _per_kind(handle, TRADOTTO)["datazione_mismatch"]
    assert len(issues) == 51
    con_entrambi = [i for i in issues
                    if "Prima metà del XVI secolo" in i.summary
                    and "First half of the 16th century" in i.summary]
    assert con_entrambi, [i.summary for i in issues[:3]]


def test_applying_the_automatic_fixes_empties_the_category(handle):
    """Una seconda verifica non ripresenta quello che la prima ha corretto."""
    prima = _per_kind(handle, ITALIANO)["datazione_mismatch"]
    edits = [e for iss in prima for e in iss.edits]
    assert len(edits) == 13
    RC.apply_edits(edits, handle, sito=ITALIANO)
    dopo = _per_kind(handle, ITALIANO)
    assert dopo.get("datazione_mismatch", []) == []
    # Le sovrapposizioni restano: non sono automatiche e nessuno le ha spuntate.
    assert len(dopo["epoch_overlap"]) == 2


def test_the_fix_touches_only_its_own_site(handle):
    """La verifica è per sito, così non si riscrivono dieci siti in un colpo."""
    prima_altrove = len(_per_kind(handle, TRADOTTO)["datazione_mismatch"])
    edits = [e for iss in _per_kind(handle, ITALIANO)["datazione_mismatch"]
             for e in iss.edits]
    RC.apply_edits(edits, handle, sito=ITALIANO)
    assert len(_per_kind(handle, TRADOTTO)["datazione_mismatch"]) \
        == prima_altrove


def test_the_rollback_puts_the_site_back(handle):
    edits = [e for iss in _per_kind(handle, ITALIANO)["datazione_mismatch"]
             for e in iss.edits]
    token = RC.apply_edits(edits, handle, sito=ITALIANO)
    RC.rollback(token, handle)
    assert len(_per_kind(handle, ITALIANO)["datazione_mismatch"]) == 13
```

- [ ] **Step 2: lanciarli**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_live.py -q -p no:warnings
```
Expected: PASS, 6 passed. Il codice di produzione c'è già da Task 1–4: questo task è il test che lo prova sui dati veri, e se un numero non torna è il codice che ha torto, non il numero — i conteggi sono stati misurati sullo stesso file.

- [ ] **Step 3: commit**

```bash
git add tests/utility/test_chronology_live.py
git commit -m "test(cronologia): i numeri del database di esempio, 2 sovrapposizioni e 13 datazioni"
```

---

### Task 7: B — la data calcolata, nell'anteprima

**Files:**
- Modify: `modules/utility/chronology_check.py` (`explain_bounds`)
- Modify: `gui/rapporti_check_dialog.py` (`_preview`)
- Test: `tests/utility/test_chronology_check.py`

**Interfaces:**
- Consumes: una voce di `graph.chronology()`, cioè `{"start": 1500.0, "end": 1549.0, "start_rule": "epoch", "start_source": "epoch_2_2", "start_relation": "has_first_epoch", "end_rule": …, "end_source": …, "end_relation": …, "rule": "epoch"}`; `self._chrono_bounds` messo in `_run` da Task 5; `Issue.us_path`.
- Produces: `explain_bounds(entry, *, lang="it") -> str`; `_RULES` (i nomi delle cinque regole nelle sei lingue).

**Onestà su quello che dice oggi:** finché nessuna US porta date assolute, tutte le righe diranno `epoca` — misurato: `chronology()` dà gli estremi a 45 nodi su 76, **tutti** con `rule='epoch'`. Serve a rendere visibile **da dove viene** una data; e quando diranno tutte la stessa cosa, si vedrà da sé che manca la parte accantonata (le date assolute su una US).

- [ ] **Step 1: scrivere i test che falliscono**

In coda a `tests/utility/test_chronology_check.py`:

```python
def test_explain_bounds_reads_span_rule_and_provenance():
    entry = {"start": 1500.0, "end": 1549.0, "start_rule": "epoch",
             "start_source": "epoch_2_2", "start_relation": "has_first_epoch",
             "end_rule": "epoch", "end_source": "epoch_2_2",
             "end_relation": "survive_in_epoch", "rule": "epoch"}
    riga = CC.explain_bounds(entry)
    assert riga == "1500–1549 · epoca · has_first_epoch → epoch_2_2"


def test_explain_bounds_names_the_rule_in_the_chosen_language():
    entry = {"start": -100.0, "end": 0.0, "start_rule": "tpq",
             "start_source": "USM101", "start_relation": "is_after",
             "rule": "tpq"}
    assert CC.explain_bounds(entry, lang="en") == \
        "-100–0 · terminus post quem · is_after → USM101"


def test_explain_bounds_on_an_entry_without_bounds_does_not_raise():
    assert CC.explain_bounds({}) == ""
    assert CC.explain_bounds(None) == ""


def test_explain_bounds_with_only_an_end_says_so():
    entry = {"end": 1549.0, "end_rule": "taq", "end_source": "US7",
             "end_relation": "is_before", "rule": "taq"}
    assert CC.explain_bounds(entry) == \
        "…–1549 · terminus ante quem · is_before → US7"


def test_explain_bounds_without_provenance_gives_just_span_and_rule():
    entry = {"start": 1500.0, "end": 1549.0, "rule": "written"}
    assert CC.explain_bounds(entry) == "1500–1549 · data scritta"
```

- [ ] **Step 2: lanciarli e vederli fallire**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_chronology_check.py -q -p no:warnings
```
Expected: FAIL — `AttributeError: module 'modules.utility.chronology_check' has no attribute 'explain_bounds'`.

- [ ] **Step 3: scrivere `explain_bounds`**

In coda a `modules/utility/chronology_check.py`:

```python
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
    # La provenienza è quella dell'estremo che la regola ha prodotto.
    lato = "start" if entry.get("start_rule") == regola and inizio is not None \
        else "end"
    relazione = entry.get("%s_relation" % lato)
    sorgente = entry.get("%s_source" % lato)
    if relazione and sorgente:
        pezzi.append("%s → %s" % (relazione, sorgente))
    return " · ".join(pezzi)
```

- [ ] **Step 4: lanciare e vedere passare**

Run: lo stesso comando dello Step 2.
Expected: PASS, 28 passed.

- [ ] **Step 5: scrivere la riga nell'anteprima**

In `gui/rapporti_check_dialog.py`, in `_preview`, dopo il ciclo sulle `iss.edits` e prima di `self.preview.setPlainText(...)`:

```python
        # La data calcolata delle US nominate: da dove viene, non solo quanto
        # vale. Si ricalcola a ogni verifica e non si scrive da nessuna parte.
        righe_data = []
        for us in getattr(iss, "us_path", ()) or ():
            for node_id, entry in (self._chrono_bounds or {}).items():
                if str(node_id).split(".")[-1] != str(us):
                    continue
                testo = CC.explain_bounds(entry, lang=self._lang)
                if testo:
                    righe_data.append("US %s · %s" % (us, testo))
                break
        if righe_data:
            lines.extend([""] + righe_data)
```

- [ ] **Step 6: provare la suite intera**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/sync tests/utility tests/migrations -q --continue-on-collection-errors \
  --ignore=tests/sync/test_groups_dialog_smoke.py \
  --ignore=tests/sync/test_paradata_dialog_smoke.py -p no:warnings
```
Expected: 0 failure, 8 errori d'ambiente, 1 xfail, 1 skip.

- [ ] **Step 7: commit**

```bash
git add modules/utility/chronology_check.py gui/rapporti_check_dialog.py \
        tests/utility/test_chronology_check.py
git commit -m "feat(anteprima): la data calcolata dice da dove viene"
```

---

### Task 8: versione, changelog, tutorial

**Files:**
- Modify: `metadata.txt` (`version=`)
- Modify: `dev_logs/CHANGELOG.md` (dall'agente)
- Modify: `docs/tutorials/<lang>/…` (dall'agente)

**Interfaces:**
- Consumes: tutto quello che i Task 1–7 hanno spedito.
- Produces: il tag `verifica-cronologia-5.13.64-alpha`.

- [ ] **Step 1: alzare la versione**

In `metadata.txt`:

```
version=5.13.64-alpha
```

- [ ] **Step 2: provare che il pin della versione regge**

Run:
```
QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 \
PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest \
  tests/utility/test_version_pins.py -q -p no:warnings
```
Expected: PASS.

- [ ] **Step 3: commit del bump**

```bash
git add metadata.txt
git commit -m "chore: 5.13.64-alpha"
```

- [ ] **Step 4: i due agenti, nell'ordine che CLAUDE.md impone**

La verifica cambia quello che l'archeologo vede nella finestra «Verifica rapporti» — quattro categorie nuove nell'albero, le proposte spuntabili, la riga della data nell'anteprima — quindi vale per tutti e due:

1. `tutorial-updater` — le quattro categorie e la riga della data nei tutorial, nelle 9 lingue di `docs/tutorials/<lang>/`.
2. `stratigraph-changelog` — la voce bilingue IT + EN in `dev_logs/CHANGELOG.md`.

Possono girare in parallelo: non dipendono l'uno dall'altro.

- [ ] **Step 5: tag**

```bash
git tag verifica-cronologia-5.13.64-alpha
```

Il tag fa scattare da sé i tre aggiornamenti del flusso di rilascio (changelog, tutorial, api-docs RTD). **Non** fare push senza che Enzo lo chieda.

---

## Autorevisione

**1. Copertura della spec.** Sezione per sezione:

| spec | task |
|---|---|
| modulo puro `chronology_check.py`, `check_chronology(periods, units, *, sito, lang)` | 1 |
| `load_chronology_rows(handle, sito)` nello stesso modulo | 4 |
| `epoch_overlap` — manuale, proposta | 1 |
| `datazione_mismatch` — automatica, i due testi nel summary | 2 |
| `epoch_reversed` — automatica, lo scambio | 1 |
| `epoch_no_dates` — solo segnalazione | 1 |
| `Edit.target` con il ripiego che conserva il comportamento | 1 (campo) + 3 (significato) |
| `_WRITABLE` per tabella, con `datazione` | 3 |
| snapshot e `rollback` su `(tabella, chiave)` | 3 |
| innesto in `_run` dopo `check_rapporti` | 5 |
| quattro voci `t_*` in sei lingue | 1 |
| `explain_bounds(entry, *, lang)` nell'anteprima | 7 |
| periodizzazione assente → nessuna issue | 1 (`test_empty_periodization_is_not_an_error`) |
| `fase` non numerica, mai float | 1 (`test_phase_2_1_and_2_10_stay_distinct`), 4 (`…keeps_the_phase_key_as_text`) |
| anni a testo → `epoch_no_dates`, non si solleva | 1 (`…a_year_written_as_text…`) |
| la riga è sparita → zero righe aggiornate | 3 (`…whose_row_is_gone…`) |
| le prove elencate nella spec | 1, 2, 3, 4, 6, 7 |
| nessuna colonna nuova | nessun task ne crea |

Due cose della spec **non** diventano task, e la spec stessa le mette fuori: le date assolute su una US (serve una correzione nel projector, e oggi non avrebbe niente da fare) e la narrativa di EMStudio (spec separata).

Due cose che la spec dà per fatte e che il piano corregge sono dette in «Tre scostamenti dalla spec, misurati»: la proposta di `epoch_overlap` che su questo database non si fa mai, e i conteggi 13/51 invece di 9/47.

Il backup automatico prima di una scrittura di colonne **non va aggiunto**: `_apply` lo fa già per qualunque `Edit` con `set_fields` (`gui/rapporti_check_dialog.py:228-250`, `auto_backup_sqlite` / `auto_backup_postgres`), e tutte le correzioni cronologiche sono `set_fields`.

**2. Segnaposti.** Nessun «TBD», nessun «gestire gli errori», nessun «come il Task N»: ogni step che tocca codice porta il codice, e ogni step che lancia un comando porta il comando intero e l'esito atteso. I 48 testi localizzati sono scritti per esteso.

**3. Coerenza dei tipi.** `check_chronology(periods, units, *, sito, lang)` è la stessa firma in Task 1, 4, 5, 6. `Edit.target` è sempre `(str, dict)` e `_target_of` lo normalizza in `(str, tuple-ordinata)`; `RollbackToken.snapshot` è indicizzato su quella forma in `apply_edits` e in `rollback`. `edit_prefix` e `explain_bounds` prendono quello che Task 3 e la libreria producono. `_selected_auto_issues` è rinominata in `_selected_issues` in un punto solo, e `_apply` è l'unico chiamante (verificato).

**4. Review Focus.** Le cinque classi hanno il loro test: anni a.C. e zero → `test_bc_years_are_negative_and_year_zero_is_a_year` (Task 1); righe di un altro sito → `test_load_chronology_rows_reads_one_site_only` e `test_the_fix_touches_only_its_own_site` (Task 4, 6); vuoti → `test_none_and_empty_string_say_the_same_thing` e `test_an_empty_source_never_blanks_a_filled_sheet` (Task 2); periodizzazione senza sito → `test_a_period_edit_without_a_sito_refuses_to_write` (Task 3); due correzioni sulla stessa riga → `test_two_edits_on_the_same_row_roll_back_to_the_first_value` (Task 3).
