# Feature A — "Genera continuità": automatismo schede CON

**Data:** 2026-06-09
**Stato:** design approvato (brainstorming) → pronto per writing-plans
**Branch:** `Stratigraph_00001`
**Contesto:** ponte PyArchInit ↔ s3dgraphy / Extended Matrix. Segue il lavoro di
rendering export EM (paradata come archi, CON visibili, contemporaneità a doppio
arco) già shippato. Precede la Feature B (paradossi temporali in Verifica rapporti).

---

## 1. Problema

In Extended Matrix una **continuità (CON)** rappresenta la persistenza di una
US/USM lungo più periodi — dalla sua **nascita** (`periodo_iniziale`) alla sua
**fine** (`periodo_finale`). Oggi:

* l'utente deve creare a mano le schede CON, oppure
* l'export iniettava diamanti sintetici `_synth_BR_<us>` (ora **soppressi** con
  `continuity_diamonds=False`) che non lasciavano traccia nel DB.

L'utente vuole che il sistema **generi automaticamente le schede CON** quando una
US/USM attraversa più periodi, **persistendole nel database** (non solo a runtime
in export), in modo che diventino dati di prima classe — editabili, esportabili,
round-trippabili verso EM-tools/Blender.

Citazione utente: *"posso anche non creare manualmente le schede di continuità, il
sistema lo fa in automatico … ma poi deve creare le schede CON."*

## 2. Obiettivo

Un'**azione esplicita "Genera continuità"** che, sul **sito corrente**:

1. trova le US/USM con `periodo_iniziale ≠ periodo_finale` (salto di periodo);
2. crea/aggiorna **idempotentemente** una scheda `CON_<us_madre>` per ciascuna,
   con lo span di periodi della madre;
3. scrive il rapporto reciproco di continuità su CON e madre;
4. mostra un'**anteprima dry-run** prima di scrivere, fa **auto-backup**, applica
   in transazione, e produce un **report**.

L'export (già funzionante) renderizza le schede CON reali; i diamanti sintetici
restano soppressi — le CON reali li **sostituiscono**.

### Non-obiettivi (YAGNI)

* Nessuna scrittura silenziosa in fase di export.
* Nessuna cancellazione automatica delle CON orfane (solo opt-in).
* Nessuna gestione delle fasi intra-periodo: conta **solo** il salto di periodo.
* Nessun supporto multi-sito in questa azione (un sito per volta).
* La Feature B (paradossi temporali) è separata e successiva.

## 3. Decisioni di design (approvate)

| Tema | Decisione |
|---|---|
| Trigger | Azione esplicita **"Genera continuità"** (pulsante), no side-effect in export |
| Rilevamento | US/USM con `periodo_iniziale` e `periodo_finale` entrambi valorizzati e **diversi** |
| Identità scheda | `us = "CON_<us_madre>"` — deterministica → idempotenza per chiave |
| Rapporto CON↔madre | **Reciproco**: CON `>` madre + madre `<` CON, scritto su entrambe |
| Etichette rapporto | **Dedicate**: "Continuità successiva a" (`>`, sulla CON) ↔ "Continuità precedente a" (`<`, sulla madre), in tutte e 10 le lingue |
| Eredità campi | CON eredita `sito`, **tutte le `area`** (multi-valore), `struttura`, span periodi/fasi dalla madre |
| Ambito | **Sito corrente** (selezionato nel dialog s3dgraphy) |
| Orfane | Solo **segnalate** di default; rimozione **opt-in** via checkbox in anteprima |
| Confine sintetico | Le CON reali **sostituiscono** i `_synth_BR_` (export resta `continuity_diamonds=False`) |

## 4. Architettura

Logica pura isolata dalla UI; compatibile PostgreSQL + SQLite via `DbHandle`
(pattern Fase 3 PG-Compat).

### 4.1 Nuovo modulo — `modules/s3dgraphy/sync/continuity_generator.py`

Solo logica di dominio, **zero import Qt**. Funzioni pure dove possibile per
massimizzare la testabilità unitaria.

```
@dataclass
class Candidate:
    sito: str
    us: str                 # us della madre (es. "US5", "USM6")
    unita_tipo: str         # "US" | "USM" (la madre)
    aree: list[str]         # tutte le aree della madre
    struttura: str | None
    periodo_iniziale: str
    fase_iniziale: str | None
    periodo_finale: str
    fase_finale: str | None

@dataclass
class Plan:
    to_create: list[dict]   # schede CON nuove
    to_update: list[dict]   # schede CON esistenti con campi divergenti
    unchanged: list[str]    # us delle CON già allineate
    orphan:    list[str]    # us di CON la cui madre non ha più il salto di periodo

@dataclass
class Report:
    created: int
    updated: int
    unchanged: int
    orphans_removed: int
    warnings: list[str]
```

| Funzione | Firma | Responsabilità |
|---|---|---|
| `scan_candidates` | `(records: list[dict]) -> list[Candidate]` | filtra le madri con salto di periodo |
| `build_con_record` | `(cand: Candidate, schedatore: str) -> dict` | costruisce la scheda `CON_<us>` (campi §5) |
| `desired_rapporti` | `(cand: Candidate) -> tuple[list, list]` | coppia rapporti reciproci (CON-side, madre-side) |
| `diff_continuity` | `(existing_con: dict[str,dict], desired: list[dict]) -> Plan` | confronto idempotente per chiave `us` |
| `apply_plan` | `(handle: DbHandle, plan: Plan, remove_orphans: bool) -> Report` | upsert schede CON + rapporto reciproco sulle madri, in transazione |

`scan/build/desired/diff` sono **pure** (nessun I/O); `apply_plan` è l'unica con
side-effect DB.

### 4.2 UI — controller del dialog s3dgraphy

Un solo metodo, p.es. `_run_genera_continuita()`, accanto al pulsante *Verifica
rapporti* già presente nel dialog (`gui/rapporti_check_dialog.py`, ospitato nel
tab import/export via `modules/s3dgraphy/s3dgraphy_dot_bridge.py`). Il metodo:

1. legge il **sito selezionato** nel dialog;
2. carica i record del sito (DbHandle) e chiama `scan_candidates` + `diff_continuity`;
3. mostra l'**anteprima** (dialog modale con conteggi + lista + checkbox orfane);
4. su conferma: **auto-backup** del DB → `apply_plan` in transazione;
5. mostra il **report** finale.

Nessuna logica di dominio nel controller — solo orchestrazione e presentazione.

### 4.3 Vocabolario — `modules/s3dgraphy/sync/rapporti.py`

Aggiungere la coppia reciproca dedicata di continuità in tutte e 10 le lingue
(it/en/de/es/fr/ar/ca/ro/pt/el), riconosciuta sia da `parse_rapporti` sia dal
controllo di reciprocità della *Verifica rapporti*:

* "Continuità successiva a" (e equivalenti) → mappa su `is_after` direzione
  forward (come lo shorthand `>`);
* "Continuità precedente a" (e equivalenti) → reciproca (come `<`).

Le due etichette vengono registrate come **coppia reciproca** così che la Verifica
rapporti non segnali la CON come priva di reciproco.

## 5. Modello dati — scheda CON

`build_con_record` produce, in `us_table`:

| Campo | Valore |
|---|---|
| `sito` | = madre |
| `us` | `CON_<us_madre>` |
| `unita_tipo` | `CON` |
| `area` | = **tutte** le aree della madre (set multi-valore preservato) |
| `struttura` | = madre |
| `periodo_iniziale` / `fase_iniziale` | = madre (nascita) |
| `periodo_finale` / `fase_finale` | = madre (fine) → la CON **copre l'intervallo** |
| `d_stratigrafica` | `Continuità` |
| `descrizione` | auto: *"Continuità di {us_madre} dal periodo {pi} al periodo {pf}"* (rigenerata ad ogni run) |
| `rapporti` | `[["Continuità successiva a", "<us_madre>", "", "", ""]]` |
| `schedatore` | utente corrente (dalla UI) |
| `node_uuid` | UUID v7 nuovo (backfill per pipeline grafo) |
| `entity_uuid` | UUID nuovo (identità entità, ≠ node_uuid) |

Sulla **madre**, l'azione aggiunge — solo se assente — il rapporto reciproco
`["Continuità precedente a", "CON_<us>", "", "", ""]`, **senza** toccare gli altri
rapporti esistenti.

## 6. Flusso dati

```
1. read    → US/USM del sito X (DbHandle, PG+SQLite)
2. scan    → candidate = madri con pi≠pf (entrambi valorizzati)
3. desired → build_con_record + coppia rapporti reciproci per ogni candidate
4. existing→ schede del sito X con us LIKE 'CON\_%'
5. diff    → per chiave us='CON_<madre>':
               assente          → to_create
               divergente       → to_update (span/descr/area/rapporto)
               identico         → unchanged
               madre persa      → orphan
6. preview → "N crea, M aggiorna, K invariate, J orfane" + lista + ☐ rimuovi orfane
7. confirm → [Annulla] / [Genera]
8. backup  → auto-backup DB
9. apply   → transazione: upsert CON + rapporto reciproco sulle madri (+ rimozione orfane se opt-in)
10. report → "Create N, aggiornate M. Orfane J (rimosse: sì/no). Warning: …"
```

### Idempotenza

Chiave `us = 'CON_<madre>'`. Seconda esecuzione consecutiva senza modifiche →
tutto in `unchanged`, **0 scritture**. Cambiando `periodo_finale` di una madre e
ri-eseguendo → quella CON va in `to_update` e lo span si riallinea.

## 7. Gestione errori

| Caso | Comportamento |
|---|---|
| madre senza `area`/`struttura` | CON creata, campi ereditati vuoti, **warning** nel report (non blocca) |
| `periodo_iniziale`/`periodo_finale` uno nullo | madre **non candidata** (no CON), nessun errore |
| rapporto reciproco già presente sulla madre | non duplicato (controllo prima di aggiungere) |
| scrittura fallita a metà | **rollback** transazione, DB intatto; auto-backup come rete |
| CON orfana | segnalata; rimossa **solo** se checkbox opt-in attiva |

## 8. Testing

**Unit (logica pura, no DB):**

* `scan_candidates`: include solo pi≠pf entrambi valorizzati; esclude pi==pf, pi/pf
  nulli.
* `build_con_record`: us=`CON_<madre>`, unita_tipo=`CON`, span = madre, tutte le
  aree ereditate, descrizione auto corretta, rapporto CON-side.
* `desired_rapporti`: coppia reciproca corretta (CON `>` madre, madre `<` CON).
* `diff_continuity`: classi to_create / to_update / unchanged / orphan; idempotenza
  (secondo diff senza modifiche → tutto unchanged).

**Integrazione (DbHandle, SQLite — e PG dove il fixture è disponibile):**

* `apply_plan` su DB di test: crea le CON, scrive i rapporti reciproci su entrambe
  le schede, è idempotente (seconda apply → 0 scritture), opzione orfane rispettata.

**Vocabolario (`rapporti.py`):**

* `parse_rapporti` riconosce le nuove etichette di continuità in tutte e 10 le
  lingue; la coppia è riconosciuta come reciproca dalla Verifica rapporti.

**Regressione:**

* Suite `tests/sync` invariata; baseline AC-2 (`mini_volterra_baseline_ai03.graphml`)
  preservata (l'azione non gira in export).

## 9. File toccati

| File | Tipo | Responsabilità |
|---|---|---|
| `modules/s3dgraphy/sync/continuity_generator.py` | **nuovo** | logica pura + apply_plan |
| `modules/s3dgraphy/sync/rapporti.py` | modifica | coppia reciproca continuità 10 lingue |
| `gui/rapporti_check_dialog.py` (o host dialog s3dgraphy) | modifica | pulsante + `_run_genera_continuita()` + anteprima/report |
| `tests/sync/test_continuity_generator.py` | **nuovo** | unit + integrazione |
| `tests/sync/test_rapporti_check.py` | modifica | etichette continuità + reciprocità |
| `dev_logs/CHANGELOG.md` | modifica | entry bilingue (agente stratigraph-changelog) |
| `docs/tutorials/<lang>/…` | modifica | nuova azione UI (agente tutorial-updater) |

## 10. Relazione con la Feature B

La Feature B (paradossi temporali in Verifica rapporti, auto-correzione e
suggerimenti) è **separata e successiva**. Le schede CON generate qui forniranno a
B segnali temporali espliciti (span di periodi persistito), ma B non dipende da A
per essere progettata. Ordine confermato: **A poi B**.
