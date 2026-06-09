# Feature B — Rilevamento paradossi temporali nella Verifica rapporti

**Data:** 2026-06-09
**Stato:** design approvato (brainstorming) → pronto per writing-plans
**Branch:** `Stratigraph_00001`
**Contesto:** ponte PyArchInit ↔ s3dgraphy / Extended Matrix. Segue la Feature A
("Genera continuità", CHANGELOG 5.12.12-alpha). Estende la *Verifica rapporti*
esistente (`modules/utility/rapporti_check.py` + `gui/rapporti_check_dialog.py`),
che già rileva cicli/self-loop/contraddizioni/reciprocità/connessioni illegali
**topologici**.

---

## 1. Problema

La *Verifica rapporti* attuale controlla la **topologia** dei rapporti (cicli,
contraddizioni, reciprocità) ma non la **coerenza cronologica**: un grafo può
essere topologicamente corretto eppure avere assegnazioni di **periodo** che
contraddicono la stratigrafia. Esempio: `US5 Copre US7` (US5 più recente) mentre
US5 è assegnata a un periodo **più antico** di US7 — impossibile.

In archeologia i rapporti stratigrafici sono **dati osservati** (riferimento),
mentre la periodizzazione è **interpretativa**: quando confliggono, è il periodo
ad essere (probabilmente) da correggere.

Citazione utente: *"vorrei che inserissi anche se ci sono paradossi stratigrafici
come quelli temporali e in base alla definizione stratigrafica e se possibile
correggerli. Per i conflitti che dovrebbero essere corretti manualmente dai anche
un suggerimento su cosa e come correggere."*

## 2. Obiettivo

Estendere la *Verifica rapporti* con il rilevamento dei **paradossi temporali**:

1. **rilevare** inversioni d'ordine e mismatch di contemporaneità tra periodi;
2. **auto-correggere** i casi risolvibili (spostando l'unità outlier o colmando un
   vuoto univoco), con anteprima + auto-backup + rollback;
3. per i casi ambigui, dare un **suggerimento "cosa + come"** correggere a mano.

### Non-obiettivi (YAGNI)

* Non si modificano i **rapporti** in auto per risolvere un paradosso temporale (si
  agisce sui periodi; la stratigrafia è il riferimento).
* Niente risoluzione globale multi-passata nascosta (un solo solve greedy;
  l'utente rilancia la verifica per i residui).
* Niente auto-spostamento di unità **multi-periodo** (CON / span voluti) → solo
  suggerimento.
* Niente nuovo motore cronologico nel core s3dgraphy: i dati di periodo/cron sono
  specifici di pyArchInit.

## 3. Decisioni di design (approvate)

| Tema | Decisione |
|---|---|
| Soglia inversione | **Inversione stretta** su intervalli: stesso periodo / sovrapposizione = OK |
| Confronto periodi | **Per intervallo** via `cron`: "A interamente più antica di B" = `cron_finale(A) < cron_iniziale(B)` |
| Contemporaneità | Archi cronologici devono **sovrapporsi**; disgiunti = paradosso |
| Riferimento correzione | La **stratigrafia** è il dato osservato → l'auto-fix sposta i **periodi**, non i rapporti |
| Politica auto-fix | Risolve inversioni spostando l'unità in conflitto con la **maggioranza** dei vicini + colma vuoti univoci; **pareggio / nessun target valido → suggerimento** |
| Restrizione | Auto-spostamento solo su unità **mono-periodo**; multi-periodo → suggerimento |
| Integrazione | **Dentro la Verifica rapporti** (nuovi `kind`, stesso albero/checkbox/apply/rollback) + **auto-backup** prima di scrivere periodi |

## 4. Architettura

Logica cronologica isolata e Qt-free, innestata nel flusso *Verifica rapporti*.

### 4.1 Nuovo modulo — `modules/utility/temporal_check.py`

Qt-free. Riusa i predicati su nodi reali di `rapporti_check` (`_real_us`,
`_strat_edges`) — importati o ri-esposti — per restare allineato.

| Funzione | Firma | Responsabilità |
|---|---|---|
| `build_chronology` | `(handle, sito) -> dict[(str,str), tuple[int\|None,int\|None]]` | da `periodizzazione_table` (sito): `(periodo, fase) → (cron_iniziale, cron_finale)` |
| `unit_span` | `(node, chrono) -> tuple[int,int] \| None` | arco `(cron_ini, cron_fin)` dell'unità dai suoi `periodo_iniziale/fase` → `periodo_finale/fase`; `None` se non databile |
| `detect_temporal` | `(graph, chrono, *, sito, lang) -> list[Issue]` | rileva `TEMPORAL_INVERSION` + `TEMPORAL_CONTEMPORANEITY` (+ informativi non valutabili) |
| `solve_fixes` | `(issues, graph, chrono, *, sito) -> None` | popola `iss.edits` (auto) o lascia il suggerimento (manuale) con l'euristica della maggioranza |

`build_chronology`/`unit_span`/`detect_temporal`/`solve_fixes` sono **pure** salvo
`build_chronology` (unica lettura DB).

### 4.2 Integrazione — `modules/utility/rapporti_check.py`

* `check_rapporti(graph, *, sito, lang, validate=True, inverse_label=None,
  chrono=None)` — **nuovo parametro opzionale `chrono`** (la mappa già costruita
  da `build_chronology`). Quando `chrono` è fornito: dopo i controlli esistenti,
  `rep.issues += temporal_check.detect_temporal(graph, chrono, sito=sito, lang=lang)`
  e `temporal_check.solve_fixes(...)`. Quando `chrono is None` (default) i controlli
  temporali sono **saltati** → backward-compatible coi chiamanti/test esistenti che
  invocano `check_rapporti(g, sito=...)`.
  **Nota:** `check_rapporti` resta DB-free; l'unica lettura DB (`build_chronology`)
  è fatta dal chiamante. `RapportiCheckPanel._run` ha già `self._handle()` →
  costruisce `chrono` e lo passa.
* Nuovi `kind`: `TEMPORAL_INVERSION`, `TEMPORAL_CONTEMPORANEITY`,
  `TEMPORAL_UNEVALUABLE` (informativo, no fix). Titoli + summary aggiunti al
  dizionario `_L` (it/en/de/es/fr/pt, fallback EN), come gli altri kind.

### 4.3 Apply/rollback unificato — `modules/utility/rapporti_check.py`

* `Edit` (frozen dataclass) estesa con `set_fields: tuple = ()` —
  tuple di `(colonna, valore)` per scrivere le colonne periodo
  (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`).
  `add`/`remove` (rapporti) restano invariati; un `Edit` può portare l'uno,
  l'altro o entrambi.
* `apply_edits(edits, handle, *, sito)`: per ogni US, snapshotta **tutte** le
  colonne che toccherà (`rapporti` se ci sono add/remove + le colonne in
  `set_fields`), poi applica gli add/remove al `rapporti` e i `set_fields` alle
  colonne periodo in un solo `UPDATE`. Lo snapshot generalizzato (per-US dict
  colonna→valore originale) è dentro il `RollbackToken`.
* `rollback(token, handle)`: ripristina dallo snapshot tutte le colonne salvate.
* L'**auto-backup** del DB (file SQLite / `pg_dump`) viene fatto dal pannello
  prima dell'apply **quando** almeno un edit selezionato ha `set_fields` (scrittura
  di periodi = dati interpretativi). Riusa `scripts/migrations/_common.py`
  (`auto_backup_sqlite` / `auto_backup_postgres` / `BackupSkipped`).

### 4.4 UI — `gui/rapporti_check_dialog.py`

Nessun cambio strutturale: i paradossi temporali compaiono come nuovi gruppi
nell'albero di "Esegui verifica", con le stesse checkbox (auto-fix selezionabili),
anteprima (`_preview` mostra `set_fields` oltre a add/remove) e
"Applica fix selezionati"/rollback. Aggiunta: auto-backup pre-apply se ci sono
`set_fields` selezionati (con dialog "pg_dump assente: procedo senza backup?" su
`BackupSkipped`).

## 5. Regole di rilevamento

**Mappa relazione → vincolo:**

| edge_type | semantica | vincolo |
|---|---|---|
| `overlies`, `cuts`, `fills`, `abuts`, `is_after` | source più **recente** | source non interamente più antica del target |
| `is_overlain_by`, `is_cut_by`, `is_filled_by`, `is_abutted_by` | source più **antica** | speculare |
| `is_physically_equal_to`, `is_bonded_to` | **contemporanee** | archi cronologici sovrapposti |

* **`TEMPORAL_INVERSION`**: relazione d'ordine tra due unità **datate** con
  `cron_finale(più_recente) < cron_iniziale(più_antica)`.
* **`TEMPORAL_CONTEMPORANEITY`**: relazione di contemporaneità con archi
  **disgiunti** (`cron_finale(A) < cron_iniziale(B)` o viceversa).
* **Vuoto colmabile**: contemporaneità con una unità datata + una **non databile**
  → non è conflitto, è un fill univoco (auto, §6).
* **Non valutabile** (`TEMPORAL_UNEVALUABLE`, informativo): relazione d'ordine con
  almeno una unità senza periodo / senza `cron` → elencata, nessun fix.
* **Esclusi**: nodi con `_real_us is None` (placeholder `_synth_*`, gruppi, epoche).

## 6. Auto-correzione (`solve_fixes`)

* **Punteggio di conflitto** di U = n° rapporti di U (ordine + contemporaneità)
  violati con i periodi correnti.
* **Unità da spostare** per un arco in paradosso A–B: quella con punteggio più
  alto. **Pareggio → suggerimento** (nessun edit).
* **Periodo target** di M: tra le `(periodo,fase)` della periodizzazione del sito,
  quelle il cui arco `cron` soddisfa **tutti** i vincoli di M contro i periodi
  **correnti** dei vicini; scelta quella a **spostamento minimo**. **Set vuoto →
  suggerimento.** Scrive `periodo_iniziale = periodo_finale` (+ `fase_*`) = target.
* **Restrizione**: auto-spostamento solo su unità **mono-periodo**
  (`periodo_iniziale == periodo_finale`); multi-periodo → suggerimento.
* **Colma-vuoto** (contemporaneità, datata + non databile): scrive sull'unità non
  datata il periodo del vicino datato → auto.
* **Solve greedy a passata singola**: ordina gli archi in paradosso per conflitto
  decrescente; ogni mossa è applicata **in memoria** sulla mappa-periodi di lavoro
  così le decisioni successive vedono l'effetto; ogni mossa risolta → `Edit` con
  `set_fields`. Nessuna scrittura DB multi-passata: l'utente applica e rilancia la
  verifica per i residui.

**Suggerimento (cosa + come)**, localizzato:
> *US5 «Copre» US7, ma US5 (periodo 1) risulta interamente più antica di US7
> (periodo 3). Sposta US5 a un periodo ≥ 3, oppure US7 a un periodo ≤ 1, oppure
> verifica il rapporto.*

Con candidato concreto in pareggio, nomina entrambe le opzioni coi target calcolati
(*"US5 → periodo 3, oppure US7 → periodo 1"*).

## 7. Gestione errori

| Caso | Comportamento |
|---|---|
| `periodizzazione_table` assente/vuota per il sito | nessun paradosso valutabile; report informativo "cronologia non disponibile" |
| `(periodo,fase)` senza riga o `cron` NULL | unità non databile → archi d'ordine `TEMPORAL_UNEVALUABLE`, nessun fix |
| unità multi-periodo coinvolta | mai auto-spostata → suggerimento |
| nessun periodo target valido / pareggio | suggerimento, nessun edit |
| `pg_dump` assente (PG) | dialog: procedi senza backup / annulla (`BackupSkipped`) |
| apply fallito a metà | rollback transazione + `RollbackToken` ripristina le colonne snapshot |

## 8. Testing

**Unit (logica pura):**
* `build_chronology`/`unit_span`: mappa cron corretta; `None` su periodo mancante.
* `detect_temporal`: inversione stretta rilevata; stesso-periodo/sovrapposizione
  **non** segnalati; contemporaneità disgiunta rilevata; non-databile →
  `TEMPORAL_UNEVALUABLE`; placeholder esclusi.
* `solve_fixes`: outlier scelto per maggioranza; pareggio → suggerimento (no edit);
  target a spostamento minimo; set vuoto → suggerimento; multi-periodo →
  suggerimento; colma-vuoto contemporaneità → edit auto.

**Integrazione (DbHandle, SQLite):**
* `check_rapporti` accoda i paradossi al `RapportiReport`.
* `apply_edits` con `set_fields` scrive le colonne periodo + snapshot/rollback le
  ripristina; un `Edit` misto (rapporti + periodi) applica entrambi.

**Regressione:** suite `tests/sync` invariata; baseline AC-2 byte-identica
(il check non gira all'export).

## 9. File toccati

| File | Tipo | Responsabilità |
|---|---|---|
| `modules/utility/temporal_check.py` | **nuovo** | cronologia + detection + solve (puro) |
| `modules/utility/rapporti_check.py` | modifica | `Edit.set_fields`, apply/rollback generalizzati, `_L` nuovi kind, chiamata a `temporal_check` in `check_rapporti(... handle ...)` |
| `gui/rapporti_check_dialog.py` | modifica | costruisce `chrono` (`build_chronology`) e lo passa a `check_rapporti`; auto-backup pre-apply se `set_fields`; `_preview` mostra `set_fields` |
| `tests/sync/test_temporal_check.py` | **nuovo** | unit + integrazione |
| `tests/sync/test_rapporti_check.py` | modifica | apply/rollback con `set_fields` |
| `dev_logs/CHANGELOG.md` | modifica | entry bilingue |
| `docs/tutorials/<lang>/36_extended_matrix_s3dgraphy.md` | modifica | sezione paradossi temporali |

## 10. Relazione con la Feature A

Indipendente da A per l'implementazione, ma le **CON** generate da A (unità
multi-periodo) sono correttamente trattate come suggerimento-only nell'auto-fix
(restrizione mono-periodo), così il loro span voluto non viene mai alterato.
