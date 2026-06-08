# PyArchInit - StratiGraph Development Changelog

> Registro dettagliato delle modifiche effettuate durante lo sviluppo dell'integrazione StratiGraph.
> Branch: `Stratigraph_00001`

---

## [5.12.9-alpha] - 2026-06-08 — Export EM: edge paradata tipizzati + USV/SF connessi

> Branch `Stratigraph_00001`. Nell'export verso GraphML/EM-tools i nodi paradata (DOC/Combinar/Extractor/property) e gli USV/SF risultavano scollegati o con relazioni generiche. Ora la catena paradata EM si tipizza correttamente.

### Italiano

**Due fix lato proiettore rendono corretto il grafo paradata EM.**

1. **Nuovo `modules/s3dgraphy/sync/paradata_edge_resolver.py`** (+ post-pass in `graph_projector.populate_graph`): dopo la costruzione del grafo, ri-tipizza gli edge `generic_connection` (lo shorthand EM `>>`/`<<` che pyArchInit salva per i collegamenti virtuali/paradata) negli edge **specifici** del datamodel s3dgraphy — `extracted_from` (Extractor→Document), `combines` (Combiner→Extractor), `has_property` ((US/USV|Document)→Property), `has_documentation` ((US/USV/SF)→Document), `has_data_provenance` (Property→Extractor/Combiner), `is_part_of` (SF/VSF→US) — leggendo le `allowed_connections` dal datamodel. La direzione viene scambiata quando la regola combacia solo al contrario. **Combiner/Extractor non si collegano mai a US/USM** (nessuna regola lo consente → restano generic). Il tipo EM del nodo è preso da `attributes['unita_tipo']` (i paradata sono `StratigraphicUnit` + attr per design, *Bug P*), non dalla classe Python. 16 test in `tests/sync/test_paradata_edge_resolver.py`.

2. **`graph_projector._is_us_node` (+3 punti in `_propagate`/`_enrich`)**: il riconoscimento della famiglia stratigrafica usava un test sul **prefisso del nome classe** (`startswith("Stratigraphic")`) che escludeva `StructuralVirtualStratigraphicUnit` / `SpecialFindUnit` / `VirtualSpecialFindUnit` (iniziano con Structural/Special/Virtual). Risultato: USV/SF/VSF non venivano indicizzati e i loro `rapporti` non diventavano mai edge. Ora si usa la MRO (qualsiasi sottoclasse di `StratigraphicNode`), così gli edge stratigrafici degli USV e i collegamenti SF/USV→DOC si formano.

Verifica headless sul DB di test: `extracted_from`/`combines`/`has_data_provenance`/`has_property`/`has_documentation`/`is_part_of` tutti presenti, USV/SF connessi. Suite `tests/sync` **415 passed**, zero nuove regressioni (9+9 PG/Spatialite pre-esistenti).

### English

**Two projector-side fixes make the EM paradata graph correct on export.** New `paradata_edge_resolver.py` runs a post-pass over `populate_graph`'s graph, retyping the EM-shorthand `generic_connection` edges into the specific s3dgraphy datamodel edge types (`extracted_from`/`combines`/`has_property`/`has_documentation`/`has_data_provenance`/`is_part_of`) by looking up `allowed_connections` from the node classes — derived from `attributes['unita_tipo']` (pyArchInit stores row-paradata as `StratigraphicUnit` + attr by design), with direction swap when the rule matches in reverse. Combiner/Extractor never link a plain US/USM. Second fix: `_is_us_node` (+3 call sites) walked a class-name prefix that missed `StructuralVirtualStratigraphicUnit`/`SpecialFindUnit`/`VirtualSpecialFindUnit`, so USV/SF/VSF nodes were never indexed and their rapporti never became edges — now it walks the MRO. Suite **415 passed**, no new regressions. 16 new resolver tests.

---

## [5.12.8-alpha] - 2026-06-08 — fix schema: `us_table.other_locations` su updater + template

> Branch `Stratigraph_00001`. Un DB creato dal template dava `OperationalError: no such column: us_table.other_locations` all'apertura.

### Italiano

**La colonna `other_locations` (yE-F, `yed-f-multifolder-5.9.0-alpha`) ora viene aggiunta automaticamente.**

Causa: `other_locations` è dichiarata nell'ORM (`US_table.py`) e selezionata ad ogni query, ma esisteva solo come **migrazione manuale** (`scripts/migrations/2026_05_yef_other_locations.py`) — non era nel template `resources/dbfiles/pyarchinit.sqlite` (del 13/05, antecedente a yE-F) né negli updater on-open. Quindi qualunque DB nato da quel template falliva all'apertura finché non si lanciava la migrazione a mano.

- **`modules/db/sqlite_db_updater.py`** (`update_us_table`): aggiunge `other_locations TEXT` via `add_column_if_missing`.
- **`modules/db/postgres_db_updater.py`**: nuovo `update_us_table()` (chiamato in `run_essential_migrations`, eseguito ad ogni connessione) che aggiunge `other_locations`.
- **Template** `resources/dbfiles/pyarchinit.sqlite` e `pyarchinit_db.sqlite`: colonna aggiunta così i nuovi DB nascono già corretti.

I DB esistenti si auto-riparano alla riconnessione; i nuovi nascono completi.

### English

**`us_table.other_locations` (yE-F) is now added automatically.** The column is in the ORM and selected on every query, but only existed as a manual migration — absent from the pre-yE-F shipped template and from the on-open updaters, so any DB created from that template errored on open. Added to the SQLite `update_us_table` and a new PostgreSQL `update_us_table` (run on every connection via `run_essential_migrations`), and added to both shipped sqlite templates. Existing DBs self-heal on reconnect; new DBs are born complete.

---

## [5.12.7-alpha] - 2026-06-08 — s3dgraphy bump 1.6.0.dev8 → 1.6.0.dev9 + stop-gap ritirato

> Branch `Stratigraph_00001`. Emanuel ha mergiato il nostro PR #23 (multilingual relationship-label vocabulary) e pubblicato `1.6.0.dev9` su PyPI. Lo stop-gap che tenevamo in locale non serve più.

### Italiano

**Allineamento a `1.6.0.dev9` e rimozione dello stop-gap multilingue.**

- **`requirements.txt`**: pin `s3dgraphy==1.6.0.dev8` → `==1.6.0.dev9`.
- **`ext_libs/s3dgraphy`** ri-vendorizzato a dev9 (`pip install … --no-deps --target ext_libs`, pulizia del `.dist-info` dev8 stantio). dev9 = dev8 + il PR #23 (vocabolario **multilingue dei rapporti**, 10 relazioni × 10 lingue UI + `"supports"→is_abutted_by`), ora ufficialmente upstream.
- **`modules/s3dgraphy/sync/rapporti.py`** ri-sincronizzato **verbatim** da dev9: il blocco vocabolario locale (`_REL_INDEX_EDGE_TYPE` / `_REL_TERMS_BY_LANG` / fold in `RAPPORTI_TO_EDGE_TYPE`) non è più una divergenza pyArchInit ma il file upstream. Tutti i simboli consumati dal tree modules (`graph_ingestor`/`graphml_writer`/`graph_projector`: `CANONICAL_UNIT_TYPES`, `strip_us_prefix`, `select_rapporti_label`, …) restano esportati da dev9 (backward-compat preservata) → nessun import rotto.
- **Eliminato il monkeypatch** `modules/s3dgraphy/sync/ext_rapporti_patch.py` e la sua chiamata in `pyarchinitPlugin.initGui()`: il percorso d'export d13 risolve ora il vocabolario multilingue (unita_tipo + rapporti) nativamente da ext_libs dev9.
- **`tests/sync/test_rapporti_multilingual_map.py`** invariato: continua a passare e ora fa da guardia anti-drift fra il vocabolario upstream e l'i18n `RELATIONSHIPS` di pyArchInit.

Suite `tests/sync` col core dev9: **399 passed**, zero nuove regressioni (i 9 failed + 9 errors sono PG/Spatialite pre-esistenti, infra headless — `no such module: VirtualSpatialIndex`). ext_libs è git-ignored: in repo cambiano `requirements.txt`, `modules/s3dgraphy/sync/rapporti.py`, `pyarchinitPlugin.py` e la rimozione di `ext_rapporti_patch.py`.

### English

**Align to upstream `1.6.0.dev9` and retire the multilingual stop-gap.** `requirements.txt` pin dev8→dev9; `ext_libs/s3dgraphy` re-vendored (`--no-deps`, stale dev8 `.dist-info` cleaned). dev9 = dev8 + merged PR #23 (relationship-label vocabulary, 10 relations × 10 UI languages + `"supports"→is_abutted_by`), now official upstream. `modules/s3dgraphy/sync/rapporti.py` re-synced **verbatim** from dev9 — the local vocab block is no longer a pyArchInit divergence but the upstream file; every symbol the modules tree consumes (`CANONICAL_UNIT_TYPES`, `strip_us_prefix`, `select_rapporti_label`, …) is still exported by dev9 (backward-compat), so no import breaks. **Removed** the `ext_rapporti_patch.py` boot monkeypatch and its `initGui()` call — the d13 export path now resolves the multilingual vocab natively from ext_libs dev9. The consistency test stays as an upstream-vs-i18n drift guard. Suite **399 passed** with the dev9 core; the 9 failed + 9 errors are pre-existing PG/Spatialite headless-infra issues. In-repo changes: `requirements.txt`, `modules/s3dgraphy/sync/rapporti.py`, `pyarchinitPlugin.py`, deletion of `ext_rapporti_patch.py`.

---

## [5.12.6-alpha] - 2026-06-07 — s3dgraphy bump 1.6.0.dev7 → 1.6.0.dev8

> Branch `Stratigraph_00001`. Emanuel ha mergiato il nostro PR #22 (multilingual US/USM unita_tipo, issue #21) e pubblicato 1.6.0.dev8 su PyPI.

### Italiano

**Allineamento alla release upstream `1.6.0.dev8`.**

- **`requirements.txt`**: pin `s3dgraphy==1.6.0.dev7` → `==1.6.0.dev8`.
- **`ext_libs/s3dgraphy`** ri-vendorizzato a dev8 (`pip install … --no-deps --target ext_libs`). dev8 = dev7 + il fix multilingual unita_tipo del PR #22 (`UNITA_TIPO_CANONICAL` dict + `canonical_unita_tipo()` + `_SHORTHAND_TOKENS` + `_source_rapporti_label`), già equivalente alle modifiche locali che avevamo applicato direttamente a ext_libs — ora ufficialmente upstream. Nessun breaking change (puramente additivo; il core importer/exporter/graph/diagnostics è invariato dev7→dev8 a parte docstring).
- **Resta locale** in `modules/s3dgraphy/sync/rapporti.py` (NON ancora upstream): il vocabolario **multilingue dei rapporti** (10×10 `RAPPORTI_TO_EDGE_TYPE` + `"supports"→is_abutted_by`). Il monkeypatch `ext_rapporti_patch.py` resta attivo: la parte unita_tipo ora è ridondante (ext_libs dev8 ce l'ha), ma il bridge serializzazione continua a passare per esso. → candidato a un secondo PR upstream.

Suite `tests/sync` col core dev8: **399 passed**, zero nuove regressioni (9+9 PG pre-esistenti, infra). ext_libs è git-ignored: in repo cambia solo il pin in `requirements.txt`.

### English

**Align to upstream `1.6.0.dev8`.** `requirements.txt` pin dev7→dev8; `ext_libs/s3dgraphy` re-vendored (`--no-deps`). dev8 = dev7 + the merged PR #22 multilingual unita_tipo fix (now official upstream, superseding the equivalent local ext_libs edits). The multilingual **relationship-label** vocabulary stays local in `modules/s3dgraphy/sync/rapporti.py` (not yet upstream) — candidate for a second PR. No breaking changes. Suite 399 passed with the dev8 core; only `requirements.txt` changes in-repo (ext_libs is git-ignored).

---

## [5.12.5-alpha] - 2026-06-07 — Verifica rapporti: dettaglio direzionale di cicli/contraddizioni, localizzato

> Branch `Stratigraph_00001`. Richiesta utente: scrivere il dettaglio dei cicli/contraddizioni nella verifica stessa, nella lingua di QGIS.

### Italiano

**Cicli e contraddizioni ora mostrano la catena completa con il rapporto di ogni passo, nella lingua impostata in QGIS.**

Prima il report diceva solo "Contraddizione diretta 616 ↔ 618" e "Ciclo: 102 → 103 → …": l'utente non vedeva *quale* rapporto fosse in conflitto. Ora:

- **Contraddizione**: `US 616 «Coperto da» US 618  ⇄  US 618 «Coperto da» US 616 — tieni una sola direzione, elimina l'altra`.
- **Ciclo**: `US 102 «Coperto da» US 103 «Coperto da» US 101 … US 102 — spezza l'anello eliminando il rapporto errato`.

Così l'utente vede subito su quale US e quale rapporto intervenire a mano (cicli e contraddizioni non sono auto-correggibili: richiedono la scelta archeologica).

- **`modules/utility/rapporti_check.py`**: `check_rapporti(..., lang=...)`; le parole dei rapporti vengono dalla tabella i18n `RELATIONSHIPS` di pyArchInit (**tutte le 10 lingue**), il prefisso unità segue la lingua (US/SU/SE/UE/…), e i template dei messaggi sono tradotti per it/en/de/es/fr/pt (fallback inglese per le altre, con le parole dei rapporti comunque localizzate). Nuova `kind_title(kind, lang)` per i titoli di gruppo.
- **`gui/rapporti_check_dialog.py`**: legge la lingua da `QgsSettings("locale/userLocale")` e la passa alla verifica; i titoli usano `kind_title`.

Test: `test_contradiction_summary_is_localized_and_directional`, `test_kind_title_localized_with_fallback`. Suite `tests/sync` 397 passed, zero nuove regressioni.

### English

**Cycles and contradictions now show the full chain with each step's relationship, in the QGIS UI language.**

Before, the report only said "Direct contradiction 616 ↔ 618" / "Cycle: 102 → 103 → …" without naming the conflicting relationship. Now each step shows its rapporto (e.g. `SU 102 «Covered by» SU 103 … SU 102 — break the loop by removing the wrong relationship`), so the user sees exactly which US and which relationship to fix by hand. `check_rapporti(..., lang=...)`: relationship words from pyArchInit's i18n table (all 10 languages), unit prefix follows the language (US/SU/SE/…), message templates translated for it/en/de/es/fr/pt (English fallback otherwise). Dialog reads the QGIS locale and passes it through. Tests added; suite 397 passed.

---

## [5.12.4-alpha] - 2026-06-07 — Reciprocità rapporti: copertura completa di tutte le 10 lingue pyArchInit

> Branch `Stratigraph_00001`. Completa/corregge [5.12.2-alpha] su indicazione dell'utente: il reciproco va preso dal vocabolario pyArchInit, per **tutte** le lingue.

### Italiano

**`parse_rapporti` ora riconosce le etichette di rapporto in tutte e 10 le lingue gestite da pyArchInit** (it, en, de, es, fr, ar, ca, ro, pt, el), non solo it/en.

In [5.12.2] avevo tappato solo il caso inglese `abuts` con alias inventati (`"is abutted by"`, `"abutted by"`). Errato: il reciproco di "Abuts" nel vocabolario pyArchInit è **"Supports"** (indice 9 della tabella `RELATIONSHIPS`), e il problema valeva per ogni lingua — un sito in tedesco/greco/arabo ecc. avrebbe avuto lo stesso fallimento di round-trip su qualsiasi relazione, non solo abuts.

- **`modules/s3dgraphy/sync/rapporti.py`**: rimossi gli alias non canonici; aggiunta la copertura completa **10 relazioni × 10 lingue** in `RAPPORTI_TO_EDGE_TYPE`, derivata dalla tabella i18n `RELATIONSHIPS` di pyArchInit (indice → edge type: 0 `is_physically_equal_to`, 1 `is_bonded_to`, 2/3 `overlies`/`is_overlain_by`, 4/5 `fills`/`is_filled_by`, 6/7 `cuts`/`is_cut_by`, 8/9 `abuts`/`is_abutted_by`). La tabella è **duplicata** (non importata) per non accoppiare il package sync a `pyarchinit.*`. Da 20 → 97 chiavi.
- **`tests/sync/test_rapporti_multilingual_map.py`** (nuovo): verifica di consistenza — la tabella embedded deve combaciare **esattamente** con `RELATIONSHIPS` di pyArchInit; ogni termine i18n mappa all'edge type giusto; le coppie inverse i18n sono coerenti con `_EDGE_TYPE_INVERSE` del detector. Fallisce se le due tabelle divergono.
- **`tests/sync/test_rapporti_check.py`**: il test sugli alias inglesi inventati è sostituito da uno multilingue (`Supports` / `Gli si appoggia` / `Wird gestützt von` / `Υποστηρίζει` / `Apoiado por` → `is_abutted_by`).

Suite `tests/sync`: 397 passed, zero nuove regressioni. *Follow-up upstream: la copertura multilingue è candidata a PR per s3dgraphy (oggi porta solo it/en parziale).*

### English

**`parse_rapporti` now recognises relationship labels in all 10 languages pyArchInit supports**, not just it/en.

[5.12.2] only patched the English `abuts` case with invented aliases — wrong: pyArchInit's reciprocal of "Abuts" is **"Supports"** (index 9 of `RELATIONSHIPS`), and the round-trip failure affected every language. Replaced with the full 10×10 mapping in `RAPPORTI_TO_EDGE_TYPE`, derived from pyArchInit's i18n table (duplicated, not imported, to keep the sync package decoupled; 20 → 97 keys). Added a consistency test that fails if the duplicate drifts from the i18n source of truth.

Suite: 397 passed, zero new regressions.

---

## [5.12.3-alpha] - 2026-06-07 — "Verifica rapporti" spostata da menu a tab del dialog di import

> Branch `Stratigraph_00001`. Richiesta utente: "invece di inserirlo nel menu inseriscilo come tab dopo import del graphml".

### Italiano

**La "Verifica rapporti stratigrafici" non è più una voce di menu separata: è un tab del dialog di import s3dgraphy.**

- **`gui/rapporti_check_dialog.py`**: la logica (site picker → report ad albero → anteprima → Applica/Annulla) è estratta in `RapportiCheckPanel(QWidget)` riutilizzabile, con un parametro `db_provider` opzionale (callable → `DbHandle`) così il pannello può puntare al DB del progetto attivo. `RapportiCheckDialog(QDialog)` resta come wrapper sottile.
- **`modules/s3dgraphy/s3dgraphy_dot_bridge.py`**: aggiunto il tab **"Verifica rapporti"** in `S3DGraphyExportDialog` (accanto a Export/Import), alimentato dal `db_manager` del progetto. Dopo un **import** riuscito il dialog passa automaticamente a quel tab e preseleziona il sito appena importato, pronto per la verifica.
- **`pyarchinitPlugin.py`**: rimossa l'azione di menu `actionRapportiCheck` (4 rami `initGui`) e l'handler `runRapportiCheck`.

Nessun test automatico (cambiamento GUI) — da verificare in QGIS ricaricando il plugin. La logica core (`rapporti_check`) è invariata e coperta dai test esistenti.

### English

**"Verifica rapporti stratigrafici" is no longer a separate menu entry — it is a tab in the s3dgraphy import dialog.**

- **`gui/rapporti_check_dialog.py`**: the logic is extracted into a reusable `RapportiCheckPanel(QWidget)` with an optional `db_provider` callable so it can target the active project DB; `RapportiCheckDialog(QDialog)` remains as a thin wrapper.
- **`s3dgraphy_dot_bridge.py`**: added a "Verifica rapporti" tab to `S3DGraphyExportDialog`; after a successful import the dialog switches to it and pre-selects the just-imported site.
- **`pyarchinitPlugin.py`**: removed the `actionRapportiCheck` menu action (4 initGui branches) and the `runRapportiCheck` handler.

GUI change — verify in QGIS by reloading the plugin. The `rapporti_check` core is unchanged and covered by existing tests.

---

## [5.12.2-alpha] - 2026-06-07 — Fix auto-fix reciprocità: l'inverso di "abuts" ora round-trippa (vocab + guardia onestà)

> Branch `Stratigraph_00001`. Risolve "la verifica dice 'Applicare 113 correzioni' ma ne corregge ~6".

### Italiano

**Il fix automatico della reciprocità sulle relazioni `abuts` (si appoggia) non funzionava sui siti in inglese.**

Su `test_6` (khutm, etichette inglesi) la verifica dichiarava 113 correzioni ma ne risolveva ~6: le 107 relazioni "Abuts" restavano. Causa: **due vocabolari disallineati**. Il fix calcola l'inverso con l'i18n di pyArchInit (`get_inverse_relationship("Abuts") → "Supports"`), ma `RAPPORTI_TO_EDGE_TYPE` di s3dgraphy **non aveva alcuna etichetta inglese per `is_abutted_by`** (solo l'italiano "Gli si appoggia") → `parse_rapporti("Supports")` la scartava silenziosamente → l'edge reciproco non nasceva mai → la reciprocità restava "mancante" a ogni ri-scansione. (Copre/Taglia/Riempie invece round-trippavano e si correggevano — da qui i ~6.)

- **`modules/s3dgraphy/sync/rapporti.py`**: aggiunti gli alias inglesi mancanti per `is_abutted_by` in `RAPPORTI_TO_EDGE_TYPE` — `"supports"`, `"abutted by"`, `"is abutted by"`. Ora "Supports" round-trippa; le voci già scritte da un apply precedente diventano valide retroattivamente (su `test_6`: reciprocità **107 → 0**).
- **`modules/utility/rapporti_check.py`** — *guardia di onestà*: una reciprocità è marcata auto-correggibile **solo se** l'etichetta inversa round-trippa all'edge type inverso corretto (`RAPPORTI_TO_EDGE_TYPE[inv] == _EDGE_TYPE_INVERSE[et]`), altrimenti è mostrata come scelta manuale. Così il conteggio in anteprima è sempre veritiero — mai più "dice N, ne applica M".

Test: `test_abuts_reciprocity_fix_label_round_trips` + `test_parse_rapporti_knows_english_is_abutted_by`. Suite `tests/sync`: 394 passed, zero nuove regressioni (9+9 PG pre-esistenti). *Follow-up upstream: la lacuna del vocabolario inglese `is_abutted_by` esiste anche in s3dgraphy — candidata a PR per Emanuel.*

### English

**The reciprocity auto-fix failed on `abuts` relationships for English-language sites.**

On `test_6` (khutm, English labels) the check claimed 113 corrections but resolved ~6: the 107 "Abuts" relations stayed. Root cause: **two misaligned vocabularies**. The fix derives the inverse via pyArchInit i18n (`get_inverse_relationship("Abuts") → "Supports"`), but s3dgraphy's `RAPPORTI_TO_EDGE_TYPE` had **no English label for `is_abutted_by`** (only Italian "Gli si appoggia"), so `parse_rapporti("Supports")` silently dropped it → the reciprocal edge never formed → reciprocity stayed "missing" on every re-scan. (Covers/cuts/fills did round-trip → the ~6 that stuck.)

- **`rapporti.py`**: added the missing English aliases for `is_abutted_by` — `"supports"`, `"abutted by"`, `"is abutted by"`. Entries already written by a prior apply become valid retroactively (`test_6`: reciprocity 107 → 0).
- **`rapporti_check.py`** — *honesty guard*: a reciprocity is auto-fixable only when the inverse label round-trips to the correct inverse edge type; otherwise it is surfaced as a manual choice, so the preview count is always truthful.

Tests added. Suite: 394 passed, zero new regressions. *Upstream follow-up: the English `is_abutted_by` gap exists in s3dgraphy too — PR candidate.*

---

## [5.12.1-alpha] - 2026-06-07 — Fix import round-trip: copia cross-sito invece di spostamento + skip nodi sintetici

> Branch `Stratigraph_00001`. Risolve l'"import azzera le US" segnalato su khutm2.

### Italiano

**Importare un GraphML in un sito NUOVO ora copia le righe invece di spostarle; gli artefatti sintetici non inquinano più `us_table`.**

Causa radice (riprodotta headless con la fixture `mini_volterra`): `GraphIngestor.populate_list` abbinava le righe per `node_uuid` **senza filtro sito** (`SELECT ... WHERE node_uuid = :uuid`) e forzava `sito` al target → importare il GraphML di un sito A dentro un sito B faceva una UPDATE che **spostava** le righe di A in B, azzerando A (`TestSite` 5→0, `NewSite` 0→8 nel repro). In più, i nodi diamante `_synth_BR_*` che l'export materializza dalla continuità tornavano all'import come finte US (`us='_synth_BR_1'`).

- **`graph_ingestor._resolve_target_row()`**: stesso sito (node_uuid già presente in `sito`) → UPDATE in place (round-trip idempotente, contratto AC-2 preservato); **cross-sito** (node_uuid appartiene a un altro sito) → **INSERT di una copia con `node_uuid` nuovo (uuid7)**, lasciando la sorgente intatta; re-import della copia → match per chiave naturale `(sito, area, us, unita_tipo)` → UPDATE (idempotente, niente duplicati / violazioni UNIQUE).
- **`graph_ingestor._is_synthetic_node()`**: i nodi `_synth_*` (artefatti del grafo) sono saltati in entrambi i loop (detection + write) → niente più righe US spurie.
- `node_uuid` (identità della riga) non viene mai riscritto in UPDATE.

Test: nuovo `tests/sync/test_round_trip_file.py` (round-trip su FILE) — same-site senza perdita/sintetici, **import in sito nuovo copia e NON sposta** (sorgente intatta, uuid freschi, rapporti ri-targettati al nuovo sito), re-import idempotente. Suite `tests/sync`: 392 passed, zero nuove regressioni (i 9+9 fallimenti `*_pg` sono pre-esistenti, infra/API-drift, falliscono a setup/costruzione prima di questo codice); 2 round-trip prima `xfail` ora passano.

### English

**Importing a GraphML into a NEW site now copies rows instead of moving them; synthetic artifacts no longer pollute `us_table`.**

Root cause (reproduced headless with the `mini_volterra` fixture): `GraphIngestor.populate_list` matched rows by `node_uuid` with **no sito filter** and forced `sito` to the target, so importing site A's GraphML into site B issued an UPDATE that **moved** A's rows into B, emptying A. Also, the `_synth_BR_*` diamond nodes the exporter materializes from continuity came back on import as bogus US rows.

- **`graph_ingestor._resolve_target_row()`**: same site → UPDATE in place (idempotent round-trip; AC-2 preserved); **cross-site** → INSERT a copy with a fresh `node_uuid` (uuid7), source untouched; copy re-import → natural-key `(sito, area, us, unita_tipo)` match → UPDATE (idempotent, no duplicates/UNIQUE violations).
- **`graph_ingestor._is_synthetic_node()`**: `_synth_*` graph artifacts skipped in both detection + write loops.
- `node_uuid` (row identity) is never rewritten on UPDATE.

Tests: new `tests/sync/test_round_trip_file.py`. Suite: 392 passed, zero new regressions (9+9 pre-existing PG infra/API-drift); 2 previously-xfail round-trips now pass.

---

## [5.12.0-alpha] - 2026-06-06 — Verifica rapporti stratigrafici + auto-fix conservativo + import copia

> Branch `Stratigraph_00001`. Spec/piano in `docs/superpowers/specs|plans/2026-06-06-rapporti-validation-autofix*`.

### Italiano

**Nuova funzione "Verifica rapporti stratigrafici" (menu pyArchInit) + helper import-copia.**

I validatori di s3dgraphy esistono ma non erano collegati al flusso pyArchInit: incongruenze nei rapporti (cicli Harris, self-loop, reciprocità mancante) passavano silenziose. Su dati reali khutm la verifica trova 3 self-loop, 13 cicli (9 multi-nodo + 4 contraddizioni dirette) e 110 reciprocità a un solo lato.

- **`modules/utility/rapporti_check.py`** (core Qt-free): costruisce il grafo del sito (`GraphProjector`) ed esegue `detect_stratigraphic_cycles` + `validate_connection` di s3dgraphy + uno scan di reciprocità derivato dai rapporti — **ristretto ai soli nodi US reali** (i placeholder sintetici del projector con `us=None`, es. `_synth_BR_654`, sono esclusi così un fix non scrive mai su righe inesistenti). **Fix conservativi**: self-loop → rimuove l'auto-relazione; **reciprocità mancante → CREA** il rapporto inverso sull'altra US (etichetta localizzata via `get_inverse_relationship`, additivo); contraddizioni dirette e cicli multi-nodo → mostrati per scelta manuale (nessun fix automatico). `apply_edits` fa snapshot dei rapporti toccati poi scrive via `DbHandle` (SQLite + PostgreSQL); `rollback` ripristina **byte-identico**.
- **`gui/rapporti_check_dialog.py`** + voce di menu "Verifica rapporti stratigrafici": scegli sito → esegui → report ad albero per tipo (auto-fix pre-selezionati) → anteprima (diff prima/dopo) → **Applica** (protetto da snapshot) / **Annulla ultimo fix**.
- **Import copia** (anti-rename): `regenerate_node_uuids(graph)` + flag `--copy` in `scripts/s3dgraphy_sync.py` (path `populate_list`) → rigenera i node_uuid così l'import INSERISCE una copia nel sito target invece di abbinare/rinominare le righe esistenti. *(Il wiring nel dialog GUI di import è in sospeso — i due path di import hanno semantiche di match diverse: populate_list per node_uuid, import_yed_raw per (us, unita_tipo).)*

Test: `tests/sync/test_rapporti_check.py` (rilevamento, fix IT/EN localizzati, esclusione placeholder sintetici, apply+rollback byte-identico) + `tests/sync/test_import_copy_mode.py`. Suite 389 passed / 0 fallimenti non-PG / 6 xfailed / 9+9 PG pre-esistenti.

### English

**New "Verifica rapporti stratigrafici" tool (pyArchInit menu) + import-copy helper.**

s3dgraphy's validators existed but were not wired into pyArchInit, so rapporti inconsistencies (Harris cycles, self-loops, missing reciprocity) passed silently. On real khutm data the check finds 3 self-loops, 13 cycles (9 multi-node + 4 direct contradictions) and 110 one-sided reciprocity gaps.

- **`modules/utility/rapporti_check.py`** (Qt-free core): builds the site graph (`GraphProjector`), runs s3dgraphy `detect_stratigraphic_cycles` + `validate_connection` + a column-derived reciprocity scan, restricted to REAL us_table-backed US nodes (synthetic projector placeholders excluded so a fix never targets a non-existent row). Conservative fixes: self-loop → remove the self-entry; missing reciprocity → CREATE the localized inverse rapporto on the other US (additive); direct contradictions / multi-node cycles → surfaced for manual choice. `apply_edits` snapshots then writes via `DbHandle` (SQLite + PostgreSQL); `rollback` restores byte-identical.
- **`gui/rapporti_check_dialog.py`** + menu action: site picker → run → report tree → preview → Apply (snapshot-protected) / Rollback.
- **Import copy** (anti-rename): `regenerate_node_uuids` + `--copy` flag in `scripts/s3dgraphy_sync.py` (the `populate_list` path) → INSERT a fresh copy under the target site instead of matching/renaming existing rows. *(GUI import-dialog wiring pending — the two import paths match differently.)*

Tests added. Suite 389 passed / 0 non-PG failures / 6 xfailed / 9+9 pre-existing PG.

---

## [5.11.4-alpha] - 2026-06-06 — DB update: coercion '' → NULL per colonne numeriche (PG strict-typing)

> Branch `Stratigraph_00001`. Emerso navigando la scheda Periodizzazione su un DB PostgreSQL (khutm2).

### Italiano

**Fix: l'UPDATE non crasha più passando stringa vuota a una colonna numerica su PostgreSQL.**

**Problema.** Muovendosi tra i record della scheda Periodizzazione (che fa un UPDATE di auto-save): `(psycopg2.errors.InvalidTextRepresentation) invalid input syntax for type bigint: "" ... cont_per=''`. La colonna `cont_per` ("codice periodo", numerico sequenziale) — come `cron_iniziale/finale`, `periodo` — è `Integer`/`bigint`. Il form passa `''` (stringa vuota dal line-edit) per il campo non valorizzato; PostgreSQL rifiuta `''` per una colonna numerica, mentre SQLite la tollera (type-loose). Audit fatto: **nessun drift di schema** — la dichiarazione ORM è correttamente `Integer`; il problema è il `''` sul path di scrittura. Il path INSERT del form (`insert_new_rec`) già coerce `cont_per=None`; mancava sul path **UPDATE** centrale.

**Fix** (`modules/db/pyarchinit_db_manager.py`): nuovo `_coerce_numeric_blanks(params, table_class_name)` — companion in scrittura di `_normalize_query_params` (lettura) — chiamato dentro `update()`. Per ogni colonna il cui `python_type` SQLAlchemy è int/float, converte `''` (e stringhe di soli spazi) in `None`. Le colonne testuali e i valori non vuoti restano invariati. Generale: vale per **tutte** le schede in UPDATE sotto PostgreSQL; **no-op su SQLite**. Verificato che `cont_per`/`cron_*` vuoti → `None`, mentre `sito`/`fase`/`descrizione` vuoti restano `''` e i valori numerici valorizzati restano invariati.

**Nota:** `cont_per` (codice periodo, sequenziale periodo→fase) resta `NULL` dopo l'import del GraphML; va ricalcolato con la funzione esistente "Codice periodo" (`update_cont_per`) se serve.

### English

**Fix: UPDATE no longer crashes passing an empty string to a numeric column on PostgreSQL.**

Navigating Periodizzazione records (an auto-save UPDATE) raised `InvalidTextRepresentation: invalid input syntax for type bigint: "" ... cont_per=''`. `cont_per`/`cron_*`/`periodo` are Integer/bigint; the form hands back `''` for an untouched line-edit, which PostgreSQL rejects for a numeric column (SQLite tolerates it). Audit: **no schema drift** — the ORM declares `Integer` correctly; the write path just sent `''`. The form's INSERT path already coerced to `None`; the central UPDATE path didn't.

**Fix** (`modules/db/pyarchinit_db_manager.py`): `_coerce_numeric_blanks()` — the write-path companion of `_normalize_query_params()` — called inside `update()`, converts `''`/whitespace to `None` for columns whose SQLAlchemy `python_type` is int/float. Text columns and non-blank values pass through. Generic across all forms' UPDATE on PostgreSQL; no-op on SQLite. `cont_per` stays NULL after a GraphML import — recompute via the existing "period code" function if needed.

---

## [5.11.3-alpha] - 2026-06-06 — Import: epoch INSERT robusto al desync di sequence PostgreSQL

> Branch `Stratigraph_00001`. L'import del GraphML in un sito target nuovo crashava su `periodizzazione_table_pkey`.

### Italiano

**Fix: l'import non crasha più per sequence PostgreSQL disallineate (`id_perfas`/`id_us`).**

**Problema.** Importando il GraphML esportato in un **sito target nuovo** (es. `test_import`), anche in **anteprima**: `UniqueViolation ... periodizzazione_table_pkey Key (id_perfas)=(12) already exists`. Non è un bug di logica: lo skip per `(sito, periodo, fase)` è corretto (è per-sito, quindi un sito nuovo crea legittimamente le sue epoche). La causa è che il DB PostgreSQL (es. khutm2) ha le **sequence serial rimaste indietro** rispetto ai dati (tipico dopo un `pg_restore`, che non resetta le sequence), quindi l'INSERT auto-PK collide. Colpiva anche l'anteprima perché il dry-run esegue gli INSERT e poi fa rollback.

**Fix** (`modules/s3dgraphy/sync/graph_ingestor.py`): nuovo `_resync_pg_serial_sequences(conn, handle)` chiamato all'apertura della transazione di `populate_list` → riallinea con `setval` le sequence di `us_table.id_us` e `periodizzazione_table.id_perfas` a `MAX(pk)` prima di scrivere. **Solo PostgreSQL; no-op su SQLite** (l'AUTOINCREMENT si autocorregge). Ogni `setval` gira in un proprio `SAVEPOINT` (`begin_nested`): in PG uno statement fallito aborta l'intera transazione, quindi un semplice try/except non basterebbe — il savepoint isola una tabella/colonna assente (schemi minimali di test) senza bloccare l'ingest.

Verificato su PG reale: con `us_table` assente, il savepoint rolla indietro, la transazione sopravvive, `periodizzazione` viene resincronizzata → insert auto-PK `id_perfas=13`, nessuna collisione. Test: `tests/sync/test_graph_ingestor.py::test_resync_pg_serial_sequences_is_noop_on_sqlite`. Suite 380 passed / 6 xfailed / 9+9 PG pre-esistenti.

Nota: questo auto-ripara l'import; le altre sequence disallineate del DB (campioni, media_thumb, ecc.) restano un tema di manutenzione DB separato (un `setval`-all su khutm2 è consigliato per la UI).

### English

**Fix: import no longer crashes on desynced PostgreSQL serial sequences (`id_perfas`/`id_us`).**

Importing the exported GraphML into a **new target site** (e.g. `test_import`), even in **preview**, raised `UniqueViolation ... periodizzazione_table_pkey Key (id_perfas)=(12)`. Not a logic bug — the `(sito, periodo, fase)` skip is per-site and a new site legitimately creates its epochs. Root cause: the PostgreSQL DB (e.g. khutm2) has serial sequences lagging the data (typical after `pg_restore`, which doesn't reset sequences), so the auto-PK INSERT collides. Hit the preview too because dry-run executes the INSERTs then rolls back.

**Fix** (`modules/s3dgraphy/sync/graph_ingestor.py`): `_resync_pg_serial_sequences(conn, handle)` at the start of `populate_list`'s transaction `setval`s the `us_table.id_us` + `periodizzazione_table.id_perfas` sequences to `MAX(pk)` before writing. **PostgreSQL-only; no-op on SQLite**. Each `setval` runs in its own `SAVEPOINT` (`begin_nested`) so a missing table/column can't abort the ingest transaction (a plain try/except can't recover an aborted PG transaction). Verified on real PG. Test added. Suite 380 passed / 6 xfailed / 9+9 pre-existing PG.

---

## [5.11.2-alpha] - 2026-06-06 — GraphProjector: riconoscimento US/USM multilingua (export DB non italiani)

> Branch `Stratigraph_00001`. Follow-up del fix d13: su DB non italiani l'export costruiva pochissimi nodi/relazioni.

### Italiano

**Fix: il GraphProjector riconosce gli US/USM in tutte le lingue → l'export di DB non italiani costruisce davvero il grafo stratigrafico.**

**Problema (più profondo del d13).** In `graph_projector.py` il gating della riga stratigrafica usava una tupla **solo italiana** (`"US","USM","USD","USV","USVs","USVn","USVc","SF","VSF","RSF"`). Su un DB inglese (khutm/Al-Khutm: 479 righe su 485 sono `SU`/`WSU`) ogni US/USM non italiano finiva in `continue` → nessun attributo `us`, nessun edge dei rapporti, nessun raggruppamento. Diagnosi su khutm2 reale: `populate_graph` produceva **6 nodi-us / 0 strat-edge** (le 6 righe `unita_tipo='US'`), da cui i sintomi "solo 5-6 nodi raggruppati in area 1, gli altri in italiano".

**Fix** (`modules/s3dgraphy/sync/graph_projector.py`): nuova mappa `_UNITA_TIPO_CANONICAL` + `_canonical_unita_tipo()`; il gating stratigrafico e la factory `_create_stratigraphic_node_for_unita_tipo` usano ora il codice **canonico** (`ut_canon`), mentre `attributes['unita_tipo']` conserva l'**originale** (round-trip + dispatch rapporti language-aware). Dopo il fix, sul vero Al-Khutm: **485 nodi-us / 2368 strat-edge / d13 tutto in inglese** (Covered by, Covers, Abuts, Same as, Cut by/Cuts, Fills/Filled by) — zero italiano, zero shorthand. Sistema anche la copertura del raggruppamento per area. Il projector è la copia `modules/` usata dall'export → durevole in codice tracciato, senza monkeypatch.

Test: `tests/sync/test_graph_projector.py::test_projector_recognizes_localized_su_wsu`. Suite 379 passed / 6 xfailed / 9+9 PG pre-esistenti.

### English

**Fix: GraphProjector recognises US/USM in every language → exporting non-Italian DBs actually builds the stratigraphic graph.**

**Problem (deeper than the d13 label).** `graph_projector.py` gated stratigraphic-row building on an **Italian-only** tuple (`"US","USM","USD","USV","USVs","USVn","USVc","SF","VSF","RSF"`). On an English DB (khutm/Al-Khutm: 479 of 485 rows are `SU`/`WSU`) every non-Italian US/USM row hit `continue` → no `us` attribute, no rapporti edges, no grouping. Diagnosed on the real khutm2 DB: `populate_graph` produced **6 us-nodes / 0 strat-edges** (the 6 `unita_tipo='US'` rows), explaining "only 5-6 nodes grouped in area 1, the rest in Italian".

**Fix** (`modules/s3dgraphy/sync/graph_projector.py`): new `_UNITA_TIPO_CANONICAL` map + `_canonical_unita_tipo()`; the stratigraphic gating and the `_create_stratigraphic_node_for_unita_tipo` factory now use the **canonical** code (`ut_canon`), while `attributes['unita_tipo']` keeps the **original** (round-trip + language-aware rapporti dispatch). After the fix, on the real Al-Khutm: **485 us-nodes / 2368 strat-edges / d13 all English** — zero Italian, zero shorthand. Also fixes area-grouping coverage. The projector is the `modules/` copy used by export → durable in tracked code, no monkeypatch.

Tests: `tests/sync/test_graph_projector.py::test_projector_recognizes_localized_su_wsu`. Suite 379 passed / 6 xfailed / 9+9 pre-existing PG.

---

## [5.11.1-alpha] - 2026-06-06 — d13 physical_relationships: US/USM multilingua + etichette localizzate

> Branch `Stratigraph_00001`. Fix segnalato su dati khutm (inglese): il d13 `physical_relationships` scriveva `<<`/`>>` per US/USM reali invece del rapporto.

### Italiano

**Fix: il d13 riconosce gli US/USM in tutte le lingue e mostra l'etichetta localizzata in Maiuscolo.**

**Problema.** Il packed string d13 lo costruisce il *core exporter* s3dgraphy via `from ...sync.rapporti import serialize_rapporti_from_edges`. Il dispatch verbose/shorthand in `rapporti.py` riconosceva come unità stratigrafica canonica **solo i codici italiani** `{"US","USM"}`. Su un DB inglese (`unita_tipo` = `SU`/`WSU`, da `UNIT_TYPE_ABBREV`) gli US/USM reali cadevano nello shorthand `>>`/`<<`.

**Fix** (in `modules/s3dgraphy/sync/rapporti.py`):
- `CANONICAL_UNIT_TYPES` esteso multilingua: US,USM,SU,WSU,SE,MSE,UE,UEM,USZ,ΣΜ,ΤΣΜ (da `pyarchinit_i18n_stratigraphic.UNIT_TYPE_ABBREV`).
- `serialize_rapporti_from_edges`: quando il dispatch è verbose (US/USM, qualunque lingua) preferisce l'etichetta originale del campo `rapporti` del nodo sorgente, normalizzata in Maiuscolo (`Covers`/`Copre`/`Liegt über`…); fallback al canonico se assente (grafi yEd). Le unità virtuali restano `>>`/`<<`, la continuità `>`/`<`.

**Durabilità (monkeypatch al boot).** Il d13 dell'export usa `ext_libs/s3dgraphy/sync/rapporti.py`, che è git-ignored e si riscarica da PyPI. Nuovo `modules/s3dgraphy/sync/ext_rapporti_patch.py` (`apply()`) ricopia i simboli corretti sul modulo ext_libs al caricamento del plugin (`pyarchinitPlugin.initGui`). `ext_libs` resta pristino (= pip); il fix vive nel codice tracciato. Verificato: su ext_libs pulito, prima `select('overlies','SU','SU')`=`>>`, dopo `apply()` l'export d13 = `[['Covers','2','1','Al-Khutm']]`. **Riavviare QGIS** per caricare la patch. Da rimuovere quando il fix sarà a monte (s3Dgraphy > 1.6.0.dev7) e `requirements` lo includerà — issue/PR a Emanuel in apertura.

Test: `tests/sync/test_rapporti_multilingual_d13.py` (16 casi). Suite 378 passed / 6 xfailed / 9+9 PG pre-esistenti.

### English

**Fix: d13 recognises US/USM in every language and shows the localized label, capitalized.**

**Problem.** The d13 packed string is built by the s3dgraphy *core exporter* via `from ...sync.rapporti import serialize_rapporti_from_edges`. The verbose/shorthand dispatch in `rapporti.py` only treated the **Italian** codes `{"US","USM"}` as canonical Harris units. On an English DB (`unita_tipo` = `SU`/`WSU`, per `UNIT_TYPE_ABBREV`) real US/USM fell through to the `>>`/`<<` shorthand.

**Fix** (in `modules/s3dgraphy/sync/rapporti.py`):
- `CANONICAL_UNIT_TYPES` extended multilingual: US,USM,SU,WSU,SE,MSE,UE,UEM,USZ,ΣΜ,ΤΣΜ.
- `serialize_rapporti_from_edges`: on the verbose branch (US/USM, any language) prefer the source node's own `rapporti` column label, capitalized (`Covers`/`Copre`/…); fall back to the canonical label when absent (yEd graphs). Virtual units keep `>>`/`<<`, continuity `>`/`<`.

**Durability (boot monkeypatch).** The export d13 imports rapporti from `ext_libs/s3dgraphy/sync/rapporti.py` (git-ignored, reinstalled from PyPI). New `modules/s3dgraphy/sync/ext_rapporti_patch.py` (`apply()`) copies the corrected symbols onto the ext_libs module at plugin start (`pyarchinitPlugin.initGui`); ext_libs stays pristine. Verified end-to-end on a clean ext_libs. **Restart QGIS** to load the patch. Remove once fixed upstream and pinned — issue/PR to Emanuel pending.

Tests: `tests/sync/test_rapporti_multilingual_d13.py` (16 cases). Suite 378 passed / 6 xfailed / 9+9 pre-existing PG.

---

## [5.11.0-alpha] - 2026-06-06 — Allineamento a s3dgraphy 1.6.0.dev7 (Phase 1)

> Branch `s3dgraphy-1.6-migration` (da `Stratigraph_00001`). Non ancora committato/taggato al momento della scrittura. Allineamento Phase 1 "in-place / due alberi": Emanuel ha mergeato upstream le nostre PR #11 (sync package, Qt-decoupled) + #12 (Postgres read backend) e pubblicato `s3dgraphy==1.6.0.dev7` su PyPI, con sopra la serie *canonical-edges*. Questo bump porta `rapporti` + `physical_relationships (d13)` nell'albero sync attivo del plugin, **senza churn ai call-site** (path `modules.s3dgraphy.sync.*` invariato).

### Italiano

**Bump dipendenza s3dgraphy 1.5.0 → 1.6.0.dev7 + migrazione canonical-edges nel sync vendored.**

- **`requirements.txt`**: pin `s3dgraphy>=1.5.0` → `s3dgraphy==1.6.0.dev7` (pin esatto pre-release).
- **`ext_libs/s3dgraphy`**: 1.5.0 → 1.6.0.dev7 via `pip install --target ext_libs --no-deps --pre` (solo core; include **d13** in `exporter/graphml/*` + `importer/import_graphml.py`). dist-info rigenerato.
- **`modules/s3dgraphy/sync/`** (albero Qt-aware vendored, import path `modules.s3dgraphy.sync.*` invariato → zero churn):
  - **ADD** `rapporti.py` (API pubbliche `parse_rapporti` / `serialize_rapporti_from_edges`, vocabolario pyArchInit↔canonical-edge).
  - **UPDATE** `graph_ingestor.py`, `graph_projector.py`, `graphml_writer.py` alle versioni dev7 (canonical-edges).
  - **`__init__.py`** merge 3-way: superficie pubblica upstream dev7 + innesto del simbolo solo-pyArchInit `get_vocab_provider()` (wrapper Qt).
  - **Preservati (non sovrascritti da upstream)**: `vocab_provider.py` (wrapper Qt), `_workspace.py` (fallback 3-tier incl. QSettings), `edge_registry.py` e `pyarchinit_pg_importer.py` (path adattati a `ext_libs/s3dgraphy/`).
- **`tests/sync/`**: baseline AC-2 `mini_volterra_baseline_ai03.graphml` rinfrescato sull'output canonical-edges+d13 (adottato il baseline upstream rinfrescato, commit `1159779`; equivalenza verificata: stessa fixture input — md5 identico — e stesso fingerprint strutturale). Marcati `xfail` (debito di test upstream, falliscono identici su dev7, in attesa della riconciliazione s3Dgraphy #13): `test_populate_list_dry_run_counts_skipped_when_unchanged`, `test_pipeline_diversifies_edge_styles`, `test_pipeline_applies_transitive_reduction`, `test_round_trip_preserves_mapped_fields`, `test_default_no_sql_update_on_import`, `test_adhoc_groups_never_touch_sql`.

**Verifica — zero regressioni (prova prima/dopo).** Suite `tests/sync` su 1.5.0 (BEFORE) = 9 failed / 368 passed / 9 errors; su dev7 (AFTER, post-fix) = 9 failed / 362 passed / 6 xfailed / 9 errors. I 18 fallimenti/errori residui sono **tutti `test_*_pg.py`** = gap di schema pre-esistente in `conftest_pg.py` (insieme identico prima e dopo; **0 fallimenti non-PG**). Smoke core-API (Graph, nodes.*, GraphMLImporter, GraphMLExporter, get_stratigraphic_node_class) tutto risolto su dev7. Backup tar di `ext_libs`+`modules` in `~/Downloads/pyarchinit_s3dg16_backup_20260606/`.

### English

**Dependency bump s3dgraphy 1.5.0 → 1.6.0.dev7 + canonical-edges migration into the vendored sync tree.**

- **`requirements.txt`**: pin `s3dgraphy>=1.5.0` → `s3dgraphy==1.6.0.dev7` (exact pre-release pin).
- **`ext_libs/s3dgraphy`**: 1.5.0 → 1.6.0.dev7 via `pip install --target ext_libs --no-deps --pre` (core only; includes **d13** in `exporter/graphml/*` + `importer/import_graphml.py`). dist-info refreshed.
- **`modules/s3dgraphy/sync/`** (vendored Qt-aware tree, `modules.s3dgraphy.sync.*` import path unchanged → zero call-site churn):
  - **ADD** `rapporti.py` (public `parse_rapporti` / `serialize_rapporti_from_edges`, pyArchInit↔canonical-edge vocabulary).
  - **UPDATE** `graph_ingestor.py`, `graph_projector.py`, `graphml_writer.py` to the dev7 canonical-edges versions.
  - **`__init__.py`** 3-way merge: upstream dev7 public surface + grafted pyArchInit-only `get_vocab_provider()` (Qt wrapper).
  - **Preserved (not overwritten from upstream)**: `vocab_provider.py` (Qt wrapper), `_workspace.py` (3-tier fallback incl. QSettings), `edge_registry.py` and `pyarchinit_pg_importer.py` (paths adapted to `ext_libs/s3dgraphy/`).
- **`tests/sync/`**: AC-2 baseline `mini_volterra_baseline_ai03.graphml` refreshed to the canonical-edges+d13 output (adopted upstream's refreshed baseline, commit `1159779`; equivalence verified — same input fixture md5 + identical structural fingerprint). Marked `xfail` (upstream test debt, fails identically on dev7, awaiting s3Dgraphy #13 reconciliation): the six tests listed above.

**Verification — zero regressions (before/after proof).** `tests/sync` on 1.5.0 (BEFORE) = 9 failed / 368 passed / 9 errors; on dev7 (AFTER, post-fix) = 9 failed / 362 passed / 6 xfailed / 9 errors. The 18 remaining failures/errors are **all `test_*_pg.py`** = pre-existing `conftest_pg.py` schema gap (identical set before and after; **0 non-PG failures**). Core-API smoke (Graph, nodes.*, GraphMLImporter, GraphMLExporter, get_stratigraphic_node_class) all resolve on dev7. Tar backups of `ext_libs`+`modules` in `~/Downloads/pyarchinit_s3dg16_backup_20260606/`.

---

## [5.10.1-alpha] - 2026-05-24 — US-USM rapporti save: positional consistency for empty cells

> Bump patch (5.10.0 → 5.10.1) su branch `Stratigraph_00001`. Fix surfacing in `tabs/US_USM.py` del residuo "Bug C" che era stato già osservato e parzialmente mitigato dalla riscrittura di Phase 2 di `update_rapporti_col_2` su questo branch. Il bug "wipe completo dei rapporti" descritto in audio WhatsApp del 2026-05-24 (utente UNIPA, Roma) è già coperto qui dal helper `_update_rapporti_add_area_sito` (commit di Phase 2 precedente); questa patch chiude il caso al momento del **salvataggio iniziale**, non solo del successivo update master.

### Italiano

**Fix: `table2dict()` ora preserva le celle vuote del rapporti table widget come stringhe vuote.**

**Problema osservato.** In `tableWidget_rapporti` (4 colonne: `tipo, us, area, sito`) e `tableWidget_rapporti2` (7 colonne: `tipo, us, unita_tipo, descr, periodo, area, sito`), quando l'utente lasciava una cella **non toccata** (`item(r,c)` ritorna `None`, non un `QTableWidgetItem` vuoto), `table2dict` la **saltava** invece di salvare `""`. Risultato: sottoliste a lunghezza variabile salvate nel campo `rapporti` (`TEXT`):

| Input utente | Salvato in DB |
|---|---|
| tipo+us+area+sito | `['Coperto da', '7', 'A1', 'Roma']` (len 4) ✓ |
| solo tipo+us (area, sito intoccate) | `['Coperto da', '7']` (len 2) ⚠️ |
| tipo+us+area | `['Coperto da', '7', 'A1']` (len 3) ⚠️ |
| **tipo+us+sito** (col 2 saltata) | `['Coperto da', '7', 'Roma']` (len 3) ⚠️⚠️ **dato posizionalmente corrotto** |

L'ultimo caso è il più grave: `"Roma"` finisce nella posizione 2 (area) anziché 3 (sito). Il master update (bottone `pushButton_area_sito_update` / hotkey `Ctrl+U`) chiama `_update_rapporti_add_area_sito` che fa lookup `find_correct_area_for_us(us=7, sito)` nel DB e ripara la posizione 2, ma **solo se l'US referenziata esiste con area non NULL**. Se l'US 7 ha area NULL nel DB, fallback a `sub[2]` = "Roma" → salvato `['Coperto da', '7', 'Roma', 'Roma']`.

**Fix applicato.** Aggiunto parametro opt-in `preserve_empty: bool = False` a `table2dict()` (riga 24630). Quando `True`, le celle `None` vengono serializzate come `""` invece di essere saltate. Attivato a `True` ai 4 call site dei rapporti widget:

- `insert_new_rec()` riga 23167-23168 (insert nuovo record US)
- `set_LIST_REC_TEMP()` riga 25420-25421 (aggiornamento record corrente in memoria pre-save)

Altri tableWidget (`inclusi`, `campioni`, `organici`, `inorganici`, `documentazione`, `colore_legante_usm`, ecc.) **non sono toccati** — usano il default `preserve_empty=False` e mantengono il comportamento skip-None precedente. Filtro chirurgico: cambio comportamento solo dove serve.

**Confronto con master.** Su `master` (versione `4.9.7`) abbiamo dovuto applicare 3 fix concatenati:
- Fix A: `get_all_areas` cursore esaurito → su `Stratigraph_00001` **già fixato** in Phase 2 (`[row[0] for row in result.fetchall()]`)
- Fix B: `update_rapporti_col_2` droppava sublist `len<3` → su `Stratigraph_00001` **già fixato** (helper `_update_rapporti_add_area_sito` + `_update_rapporti2_add_area_sito` con padding intelligente)
- Fix C: `table2dict` saltava None → **applicato ora con questo bump**

Phase 2 è quindi una base più robusta. Questo commit chiude l'ultimo gap residuo.

**Nessuna migrazione necessaria.** Le sottoliste corte già nel DB vengono riparate dal prossimo `update_all_areas` (bottone o `Ctrl+U`).

### English

**Fix: `table2dict()` now preserves empty cells in rapporti table widgets as empty strings.**

**Observed problem.** In `tableWidget_rapporti` (4-col: `tipo, us, area, sito`) and `tableWidget_rapporti2` (7-col: `tipo, us, unita_tipo, descr, periodo, area, sito`), when the user left a cell **untouched** (`item(r,c)` returns `None` instead of an empty `QTableWidgetItem`), `table2dict` **skipped it** rather than saving `""`. This produced length-variable sublists in the `rapporti` field (`TEXT`):

| User input | Saved to DB |
|---|---|
| type+us+area+sito | `['Coperto da', '7', 'A1', 'Roma']` (len 4) ✓ |
| only type+us (area, sito untouched) | `['Coperto da', '7']` (len 2) ⚠️ |
| type+us+area | `['Coperto da', '7', 'A1']` (len 3) ⚠️ |
| **type+us+sito** (col 2 skipped) | `['Coperto da', '7', 'Roma']` (len 3) ⚠️⚠️ **positionally corrupted** |

The last case is the worst: `"Roma"` lands in position 2 (area) instead of 3 (sito). The master update (`pushButton_area_sito_update` button / `Ctrl+U` hotkey) calls `_update_rapporti_add_area_sito`, which performs a `find_correct_area_for_us(us=7, sito)` DB lookup and fixes position 2 — **but only if the referenced US exists with a non-NULL area**. If US 7 has NULL area in the DB, fallback to `sub[2]` = "Roma" → saved as `['Coperto da', '7', 'Roma', 'Roma']`.

**Fix applied.** Added opt-in `preserve_empty: bool = False` parameter to `table2dict()` (line 24630). When `True`, `None` cells are serialized as `""` instead of being skipped. Enabled at the 4 rapporti widget call sites:

- `insert_new_rec()` lines 23167-23168 (new US record insert)
- `set_LIST_REC_TEMP()` lines 25420-25421 (current record in-memory update pre-save)

Other tableWidgets (`inclusi`, `campioni`, `organici`, `inorganici`, `documentazione`, `colore_legante_usm`, etc.) **are untouched** — they keep the default `preserve_empty=False` and the previous skip-None behavior. Surgical opt-in: behavior changes only where needed.

**Comparison with master.** On `master` (version `4.9.7`) we had to apply 3 concatenated fixes:
- Fix A: `get_all_areas` exhausted cursor → already fixed on `Stratigraph_00001` in Phase 2 (`[row[0] for row in result.fetchall()]`)
- Fix B: `update_rapporti_col_2` dropped `len<3` sublists → already fixed on `Stratigraph_00001` (helpers `_update_rapporti_add_area_sito` + `_update_rapporti2_add_area_sito` with smart padding)
- Fix C: `table2dict` skipped None → applied now with this bump

Phase 2 is therefore a more robust baseline. This commit closes the last remaining gap.

**No migration needed.** Short sublists already in the DB are repaired by the next `update_all_areas` run (button or `Ctrl+U`).

---

## [5.10.0-alpha] - 2026-05-22 — Extended Matrix renderer (Graphviz dot + EM palette icons)

> Tag `5.10.0-alpha` su branch `Stratigraph_00001`. Bump minor (5.9 → 5.10) per nuova feature: pipeline rendering automatico del matrix Harris/Extended Matrix in PNG accanto all'export GraphML (prima richiedeva apertura manuale in yEd + Apply Swimlane Layout). 11 commit cumulati `7cf297fd..5d990988`.

### Italiano

**Nuovo: 3-generation matrix renderer pipeline.**

Dopo `pushButton_export_extended_matrix` (sito → graphml + json), il plugin genera AUTOMATICAMENTE un `<base>_swimlane.png` nella stessa cartella usando **Graphviz `dot`** come engine di layout (hierarchical + orthogonal + bin-packed clusters). Output visualmente equivalente a "Apply Swimlane Layout + Orthogonal Edges" in yEd, ma in batch senza intervento manuale.

**File nuovi (5 moduli, ~1900 righe):**

- `modules/utility/em_palette_parser.py` — parser EM palette graphml shippata da s3dgraphy (auto-aggiorna su `pip install -U s3dgraphy`)
- `modules/utility/s3d_json_loader.py` — JSON s3dgraphy 1.5 → NetworkX DiGraph (supporta sia hierarchical sia flat format)
- `modules/utility/harris_swimlane_layout.py` — Sugiyama layered layout fallback (matplotlib path)
- `modules/utility/matrix_swimlane_renderer.py` — matplotlib renderer fallback
- `modules/utility/extended_matrix_renderer.py` — **renderer principale**: usa Graphviz `dot` per layout autoritativo + EM palette icons ufficiali (combiner.png, extractor.png, document.png, property.png da s3dgraphy)

**Caratteristiche renderer principale**:

- **Layout via dot binary** (`splines=ortho`, `rankdir=TB`, `compound=true`, `pack=true`): cluster boxes auto-bin-packed in colonne, edge ortogonali Manhattan veri (no curve)
- **EM palette icons**: nodi paradata (DOC/Combinar/Extractor/property) usano le PNG ufficiali shippate da s3dgraphy invece di rectangle/parallelogram generici. Size adattivo per kind: Combinar/Extractor 0.32", DOC 0.42", property 0.55"
- **Edge tipizzati** da `pyarchinit.rapporti` field (lista `[tipo, us, area, sito]`):
  - **Copre / Coperto da / Riempie / Riempito da** → linea solid blu navy con freccia
  - **Taglia / Tagliato da** → linea **dashed rossa** (#C0392B) con freccia (rapporti negativi)
  - **Uguale a / Si lega a** → **linea doppia nera orizzontale senza frecce** (trick `color="black:white:black"` + `dir=none` + `{rank=same}` subgraph)
  - **Si appoggia a / Gli si appoggia** → linea solid sottile
  - **`<<` / `>>`** (paradata connections) → **linea dashed grigia** con freccia
- **Dedup edge reciproci** (A↔B → 1 edge) via `frozenset((src,tgt))` → riduce edge count 204→118 sul test_1
- **300 dpi output** (configurabile), formato A3 portrait per stampa professionale
- **Dynamic key lookup** via `<key attr.name="...">` declarations (no hardcoded d-ids → resistente a schema drift)

**Wire pipeline** (`modules/s3dgraphy/s3dgraphy_dot_bridge.py:export_extended_matrix_multi_format`):

```
graphml export → try extended_matrix_renderer (dot-based)
              → fallback matrix_swimlane_renderer (matplotlib) on failure
              → save <base>_swimlane.png + <base>_swimlane.dot
```

Output utente: 2 file aggiunti per ogni export (PNG render + DOT source). Il `.dot` apribile in xdot/yEd/VS Code per ispezione/tweak.

**Dipendenza esterna**: richiede Graphviz `dot` binary installato (`brew install graphviz` macOS, `apt-get install graphviz` Linux, `choco install graphviz` Windows). Se mancante → fallback matplotlib automatico (visualmente meno bello ma funzionante). Auto-discovery via `shutil.which("dot")` + path fallback (`/opt/homebrew/bin/dot`, `/usr/local/bin/dot`, `/usr/bin/dot`).

**Output validato su `test_1.graphml`** (sito test, 7 group folder VA01-VA06, 83 nodi, 118 edge dedup):
- PNG 1.1 MB a 300 dpi, 8046×11331 px (≈A3 portrait)
- 66/83 nodi paradata renderizzati con EM palette icons ufficiali
- Layout hierarchical entro ogni cluster (USV in cima → property/extractor → US in basso)
- 7 cluster bin-packed in ~3 colonne portrait-oriented (`ratio=1.4` + `packmode="array_t2"`)

### English

**New: 3-generation matrix renderer pipeline.**

After `pushButton_export_extended_matrix` (site → graphml + json), the plugin AUTOMATICALLY generates a `<base>_swimlane.png` in the same folder using **Graphviz `dot`** as the layout engine (hierarchical + orthogonal + bin-packed clusters). Output visually equivalent to "Apply Swimlane Layout + Orthogonal Edges" in yEd, but batch without manual intervention.

**5 new modules (~1900 lines)** in `modules/utility/`: em_palette_parser, s3d_json_loader, harris_swimlane_layout, matrix_swimlane_renderer, **extended_matrix_renderer** (primary, dot-based).

**Primary renderer features**:

- **dot binary layout**: `splines=ortho`, `rankdir=TB`, `compound=true`, `pack=true` → auto-bin-packed clusters, true Manhattan orthogonal edges (no curves)
- **Official EM palette icons** for paradata (DOC/Combinar/Extractor/property) from s3dgraphy's bundled PNGs, with per-kind sizing (Combiner/Extractor smaller than Document/property for visual balance)
- **Typed edges** from `pyarchinit.rapporti` data field:
  - **Copre / Coperto da / Riempie / Riempito da** → solid navy with arrow
  - **Taglia / Tagliato da** → **red dashed** (#C0392B) with arrow (negative relations)
  - **Uguale a / Si lega a** → **black double horizontal line, no arrows** (Graphviz `color="black:white:black"` trick + `dir=none` + `{rank=same}` subgraph)
  - **Si appoggia a / Gli si appoggia** → thin solid
  - **`<<` / `>>`** (paradata membership) → **dashed grey** with arrow
- **Reciprocal edge dedup** (A↔B → 1 edge) via `frozenset((src,tgt))` → reduces edge count from 204 to 118 on test_1
- **300 dpi output** (configurable), A3 portrait format
- **Dynamic key lookup** via `<key attr.name>` declarations (no hardcoded d-ids → robust to schema drift)

**Pipeline wiring** in `modules/s3dgraphy/s3dgraphy_dot_bridge.py`:
1. Try `extended_matrix_renderer.render_extended_matrix()` (dot-based)
2. Fall back to `matrix_swimlane_renderer.render_to_file()` (matplotlib) on failure
3. Save `<base>_swimlane.png` + `<base>_swimlane.dot` (source for inspection/tweak)

**External dependency**: Graphviz `dot` binary (`brew install graphviz` / `apt-get install graphviz` / `choco install graphviz`). Auto-discovery via `shutil.which("dot")` + fallback paths. If missing → graceful matplotlib fallback.

**Validated on test_1.graphml** (7 group folders VA01-VA06, 83 nodes, 118 deduped edges): PNG 1.1 MB @ 300 dpi, 8046×11331 px (≈A3 portrait), 66/83 paradata nodes with EM icons, hierarchical layout within each cluster.

---

## [post-5.9.0.1-alpha] - 2026-05-21 (cont. 2) — Box labels: professional A4 portrait redesign + QR code

> Commit `402faba2` su branch `Stratigraph_00001`, **senza nuovo tag né bump di `metadata.txt`** (resta `5.9.0.1-alpha`). Continuazione della giornata test PDF su `pyarchinit-AA39.sqlite`: dopo aver fatto funzionare la generazione del `Etichette Casse Materiali.pdf`, l'utente ha chiesto un redesign professionale "applicabili alla cassa" con QR code.

### Italiano

**Box label PDF: redesign professionale + QR code.**

Il vecchio formato delle etichette casse (`Box_labels_Finds_pdf_sheet.create_sheet`) era una tabella 4-righe senza stile: solo testo su pagina bianca, identica al data-dump di `build_index_Casse`. Visualmente inutilizzabile come etichetta da applicare a una cassa fisica di magazzino archeologico.

**Nuovo layout** (`modules/utility/pyarchinit_exp_Findssheet_pdf.py:Box_labels_Finds_pdf_sheet`):

- **Formato**: A4 portrait (21×29.7 cm), 1 etichetta per pagina (full-page → ritagli a misura o stampi su carta adesiva A4)
- **Banner header**: logo (sinistra) + nome sito (centro, 22pt bold blu scuro) + **badge cassa GIGANTE** (64pt bianco su sfondo blu scuro `#1a2d4a`) — leggibile da 1-2m di distanza per scaffalatura
- **Banda luogo conservazione**: sfondo grigio chiaro (`#f0f2f7`), 14pt, evidenzia "dove sta la cassa"
- **Body a 2 colonne**:
  - Sinistra (~13cm): "Unità Stratigrafiche" (header 13pt bold blu) + lista una-per-riga; "Elenco materiali" (header 13pt bold blu) + lista una-per-riga
  - Destra (~5.5cm): QR code 5×5cm + hint "Scansiona per ID" (9pt grigio)
- **Footer**: "Generato il DATA — pyArchInit" (8pt italic grigio, sfondo grigio chiaro)
- **Bordo esterno** in blue scuro `#1a2d4a` (1pt)

**QR code payload strutturato pipe-delimited**:

```
PYARCHINIT|SITE:Geta|BOX:5|PLACE:Magazzino C - Lucerne|US:Area:1,US:10|ITEMS:Nr.inv:9/LIT,Nr.inv:10/CER|GEN:2026-05-21
```

Tre proprietà desiderate: (1) compatto (<150 chars tipici, stays nei limiti di QR version 10), (2) human-readable quando scansionato a un QR reader generico smartphone, (3) parseable da future app pyArchInit mobile. ITEMS auto-truncato a ~400 chars max per non sforare la capacity QR. Fallback a placeholder testuale se libreria `qrcode` mancante (è già in `requirements.txt`).

**Refactor bonus**:

- I 3 metodi duplicati `create_sheet[_de/_en]` (~100 righe l'uno, ~300 righe totali) collassati in un singolo `_render_label(lang)` + dict `TR_LABEL` (it/de/en) con tutte le stringhe i18n. Risultato: **-287 / +322 righe** nel file, codice più mantenibile, design consistente per tutte le lingue.
- Helpers module-level aggiunti vicino al safe_eval block: `_strip_html`, `_make_qr_image`, `_build_qr_payload`, `TR_LABEL` dict.

**Build size change**: `build_box_labels_Finds[_de/_en]` ora usa A4 portrait `(21 × 29.7 cm)` invece di A4 landscape `(29 × 21 cm)`. L'orientamento verticale matcha tipiche dimensioni di casse archeologiche e dà più spazio verticale per la lista materiali.

**Public API invariato**: `tabs/Inv_Materiali.py:on_pushButton_print_pressed` continua a chiamare `Mat_casse_pdf.build_box_labels_Finds(data_list, sito_ec)` senza modifiche.

**Test isolation**: helpers (`_strip_html`, `_build_qr_payload`, `_make_qr_image`, `TR_LABEL`) verificati in standalone Python senza dipendenze QGIS — tutti OK (QR image 5×5cm generata, strip HTML rimuove `<b>5</b>`, payload 131 chars per la cassa di test).

### English

**Box label PDF: professional redesign + QR code.**

The old box label format (`Box_labels_Finds_pdf_sheet.create_sheet`) was a 4-row unstyled table — just text on a white page, identical to the data dump from `build_index_Casse`. Visually unusable as an adhesive label on a physical archive box.

**New layout** (`modules/utility/pyarchinit_exp_Findssheet_pdf.py:Box_labels_Finds_pdf_sheet`):

- **Format**: A4 portrait (21×29.7 cm), 1 label per page (full-page → trim to fit or print on A4 adhesive paper)
- **Header banner**: logo (left) + site name (centre, 22pt bold dark blue) + **HUGE cassa badge** (64pt white on dark blue `#1a2d4a` background) — readable from 1-2m for shelf identification
- **Storage location band**: light grey background (`#f0f2f7`), 14pt, highlights "where the box lives"
- **2-column body**:
  - Left (~13cm): "Stratigraphic Units" (13pt bold blue header) + one-per-line list; "Materials list" (13pt bold blue header) + one-per-line list
  - Right (~5.5cm): QR code 5×5cm + "Scan for ID" hint (9pt grey)
- **Footer**: "Generated on DATE — pyArchInit" (8pt italic grey, light grey background)
- **Outer border** in dark blue `#1a2d4a` (1pt)

**Structured pipe-delimited QR payload**:

```
PYARCHINIT|SITE:Geta|BOX:5|PLACE:Magazzino C - Lucerne|US:Area:1,US:10|ITEMS:Nr.inv:9/LIT,Nr.inv:10/CER|GEN:2026-05-21
```

Three desired properties: (1) compact (<150 chars typical, fits QR version 10 limits), (2) human-readable when scanned with a generic smartphone QR reader, (3) parseable by future pyArchInit mobile apps. ITEMS auto-truncated to ~400 chars max to stay within QR capacity. Falls back to a text placeholder if `qrcode` lib missing (already in `requirements.txt`).

**Refactor bonus**:

- The 3 duplicated `create_sheet[_de/_en]` methods (~100 lines each, ~300 total) collapsed into a single `_render_label(lang)` + `TR_LABEL` dict (it/de/en) with all i18n strings. Result: **-287 / +322 lines** in the file, more maintainable code, consistent design across all languages.
- Module-level helpers added near the safe_eval block: `_strip_html`, `_make_qr_image`, `_build_qr_payload`, `TR_LABEL` dict.

**Build size change**: `build_box_labels_Finds[_de/_en]` now use A4 portrait `(21 × 29.7 cm)` instead of A4 landscape `(29 × 21 cm)`. The vertical orientation matches typical archive box dimensions and gives more vertical room for the materials list.

**Public API unchanged**: `tabs/Inv_Materiali.py:on_pushButton_print_pressed` keeps calling `Mat_casse_pdf.build_box_labels_Finds(data_list, sito_ec)` without modification.

**Isolation test**: helpers (`_strip_html`, `_build_qr_payload`, `_make_qr_image`, `TR_LABEL`) verified standalone (no QGIS deps) — all OK (5×5cm QR image generated, HTML strip removes `<b>5</b>`, 131-char payload for the test box).

---

## [post-5.9.0.1-alpha] - 2026-05-21 (cont.) — Safe eval override + Etichette Casse + nr_cassa quoting + unload recursion regression

> Continuazione della stessa sessione del 21-05. Tre fix legati al test end-to-end dell'export PDF Inventario Materiali su `pyarchinit-AA39.sqlite` (sito Geta, 10 reperti seed).

### Italiano

**(A) Safe eval override in `pyarchinit_exp_Findssheet_pdf.py`.**
12 chiamate `eval(self.<campo>)` non protette su campi `elementi_reperto`, `misurazioni`, `tecnologie`, `rif_biblio` crashavano con `NameError` quando l'utente inseriva testo libero invece del literal Python atteso (es. `"orlo, collo"` → `eval` cercava variabili `orlo` e `collo`). La memoria del 13-04 indicava "Protected ~80 eval() calls", ma 12 erano scappati. Fix: shadow di `eval` a livello modulo (`_safe_eval` che ritorna `[]` su qualsiasi eccezione) — copre tutti i call site senza dover patchare 12+ punti uno per uno. I literal validi continuano a parsare normalmente.

**(B) Wire `build_box_labels_Finds` in 3 locale branches.**
Quando l'utente clicca "Esporta Elenco Casse" ora viene generato sia `Elenco Casse.pdf` sia `Etichette Casse Materiali.pdf` in un'unica azione. Funzione `build_box_labels_Finds(records, sito)` esisteva già in `pyarchinit_exp_Findssheet_pdf.py` ma era commentata nei caller. Decommentata e attivata per it/de/en (con messaggi di conferma localizzati).

**(C) Quoting drift `nr_cassa` → IndexError fix.**
`generate_el_casse_pdf` line 5106 costruiva `params_dict = {..., 'nr_cassa': '"' + str(cassa) + '"'}` wrappando un INT in `'"5"'` (3 chars: quote-5-quote). `_normalize_query_params` Step 1 strippava solo single quotes, quindi `'"5"'` sopravviveva → coerce `int('"5"')` falliva → fallback alla stringa originale → SQL `nr_cassa = '"5"'` mai matchava INT su PG (silenzioso 0 righe, IndexError su `res[0]` sul client). Fix triplo: caller passa `cassa` plain INT senza quote; `_normalize_query_params` ora strippa anche double quotes (difensivo per altri caller); aggiunto guard `if not res_luogo_conservazione: continue` nel loop.

**(D) Regression fix: `_unload_main_dockwidget` ricorsione infinita.**
Il commit precedente di unload cleanup (`b84634fe`) aveva fatto `replace_all` di `setVisible(False)+removeDockWidget` per delegare a un nuovo helper, MA il pattern matchava anche le 2 righe DENTRO il body dell'helper stesso → metodo che chiama se stesso → `RecursionError: maximum recursion depth exceeded` al primo unload. Corretto.

**(E) PK rebuild `inventario_materiali_table` su AA39 (operativo, non in repo).**
DB AA39 aveva `id_invmat INT` (no PK), causando `id_invmat=NULL` su INSERT da SQLAlchemy. L'ORM raggruppava tutte le righe NULL in una sola identity → DATA_LIST vuota → form mostrava 0 record. Rebuild via `PRAGMA writable_schema=ON` + `UPDATE sqlite_master` (Python sqlite3, perché il CLI macOS ha `SQLITE_DBCONFIG_DEFENSIVE=ON` di default). Tentativo CREATE+INSERT+DROP+RENAME standard è fallito perché trigger Spatialite `ISO_metadata_reference_row_id_value_insert` ha bug noto (referenzia `rowid` in subquery inline). 10 record + valori id_invmat 1..10 preservati, INSERT post-rebuild senza id_invmat → auto-assegna 11 ✓. Backup pre-rebuild salvato. **Questa parte è solo locale su AA39, non c'è codice da committare.**

**Test path completo end-to-end (post questi fix):**
1. Riavvia QGIS → carica plugin con safe eval override + box labels wired + unload recursion fixed
2. Apri Inventario Materiali sito=Geta → 10 record visibili con tutti i campi popolati (inclusi i list-format `elementi_reperto`/`misurazioni`/`tecnologie`)
3. Click `pushButton_print` con `checkBox_e_us` checked → genera **2 PDF**: `Elenco Casse.pdf` (5 casse) + `Etichette Casse Materiali.pdf` (10 etichette)
4. Aggiungi nuovo reperto da form → riceve `id_invmat=11` auto-assegnato

### English

**(A) Safe eval override in `pyarchinit_exp_Findssheet_pdf.py`.**
12 unprotected `eval(self.<field>)` calls on `elementi_reperto`, `misurazioni`, `tecnologie`, `rif_biblio` crashed with `NameError` when users entered free text instead of the expected Python literal (e.g. `"orlo, collo"` → eval looked up variables `orlo` and `collo`). Memory note from Apr 13 said "Protected ~80 eval() calls" but 12 slipped through. Fix: module-level `eval` shadow (`_safe_eval` that returns `[]` on any exception) — covers all call sites without patching 12+ places individually. Valid literals still parse normally.

**(B) Wire `build_box_labels_Finds` in 3 locale branches.**
Clicking "Export Box List" now generates both `Elenco Casse.pdf` and `Etichette Casse Materiali.pdf` in one action. Function existed in `pyarchinit_exp_Findssheet_pdf.py` but was commented out at the call sites. Now active for it/de/en with localized confirm messages.

**(C) `nr_cassa` quoting drift → IndexError fix.**
`generate_el_casse_pdf` line 5106 built `params_dict = {..., 'nr_cassa': '"' + str(cassa) + '"'}` wrapping an INT in `'"5"'`. `_normalize_query_params` Step 1 only stripped single quotes, so `'"5"'` survived → `int('"5"')` failed → fell through with the string → SQL `nr_cassa = '"5"'` never matched the INT column on PG. Triple fix: caller passes plain INT; `_normalize_query_params` now also strips double quotes (defensive); added `if not res_luogo_conservazione: continue` guard.

**(D) Regression fix: `_unload_main_dockwidget` infinite recursion.**
Previous unload cleanup commit (`b84634fe`) used `replace_all` to delegate `setVisible(False)+removeDockWidget` to a new helper, BUT the pattern ALSO matched the 2 lines INSIDE the helper body → method calling itself → `RecursionError` on first unload. Fixed.

**(E) PK rebuild on `inventario_materiali_table` for AA39 (operational, not in repo).**
AA39 had `id_invmat INT` (no PK), causing `id_invmat=NULL` on SQLAlchemy INSERTs. ORM coalesced all NULL-PK rows into one identity → DATA_LIST empty → form showed 0 records. Rebuild via `PRAGMA writable_schema=ON` + `UPDATE sqlite_master` (Python sqlite3 because macOS CLI has `SQLITE_DBCONFIG_DEFENSIVE=ON` default). Standard CREATE+INSERT+DROP+RENAME failed because the Spatialite trigger `ISO_metadata_reference_row_id_value_insert` has a known bug (references `rowid` in an inline subquery). 10 records + id_invmat 1..10 preserved, post-rebuild INSERT auto-assigns 11 ✓. Backup saved. **Local-only fix on AA39, no code to commit.**

**Full end-to-end test path (post these fixes):**
1. Restart QGIS → loads plugin with safe eval override + box labels wired + unload recursion fixed
2. Open Inventario Materiali site=Geta → 10 records visible with all fields populated
3. Click `pushButton_print` with `checkBox_e_us` → generates **2 PDFs**: `Elenco Casse.pdf` (5 boxes) + `Etichette Casse Materiali.pdf` (10 labels)
4. Add new record via form → receives auto-assigned `id_invmat=11`

---

## [post-5.9.0.1-alpha] - 2026-05-21 — Inventario Materiali "Elenco Casse" crash + DB schema repair

> Commit su branch `Stratigraph_00001`, **senza nuovo tag né bump di `metadata.txt`** (resta `5.9.0.1-alpha`). Bugfix sull'export PDF Elenco Casse + nuovo strumento di **schema repair** generico (tabelle + colonne mancanti) per DB legacy che l'auto-update del config dialog non riesce a migrare. Scoperto su `pyarchinit-AA39.sqlite` dove mancavano sia 5 colonne (`schedatore`, `date_scheda`, `punto_rinv`, `negativo_photo`, `diapositiva` su `inventario_materiali_table`) sia 1 colonna (`other_locations` su `us_table`) sia 1 intera tabella (`tomba_table`).

### Italiano

**Bug 1 — `build_index_Casse` crashava con TypeError quando l'elenco casse era vuoto.**

`tabs/Inv_Materiali.py:on_pushButton_print_pressed` chiamava `Mat_casse_pdf.build_index_Casse(data_list, sito_ec)` senza controllo, mentre `generate_el_casse_pdf` aveva il `return data_for_pdf` **dentro il try**: se una qualsiasi query SQL falliva (es. `res_luogo_conservazione[0]` su lista vuota → `IndexError`), l'`except` mostrava il warning fuorviante "Il campo cassa non deve essere vuoto" e **ritornava `None` implicitamente**. Il caller passava quel `None` a `build_index_Casse` che crashava su `range(len(None))`.

**Fix in 4 punti**:
- `generate_el_casse_pdf` (line 5020): l'`except` ora ritorna `[]` esplicitamente + mostra messaggio con tipo eccezione/messaggio/traceback completo (rimosso il testo fuorviante).
- 3 call site di `on_pushButton_print_pressed` (line 4751 it, 4811 de, 4907 en): aggiunto `if not data_list:` con warning localizzato ("Nessuna cassa trovata" / "Keine Kisten gefunden" / "No boxes found") che salta la generazione PDF invece di crashare.

**Bug 2 — DB schema drift su DB importate da backup vecchi.**

L'auto-migration in `modules/db/pyarchinit_db_update.py:446-459` aggiunge le 5 colonne schedatore SE `safe_load_table('inventario_materiali_table')` ritorna la tabella, MA per DB importate da backup o create da plugin molto vecchi `safe_load_table` ritorna `None` e l'intero blocco ADD COLUMN viene saltato silenziosamente. Stesso pattern per `us_table.other_locations` (migrazione yE-F del 5.9.0-alpha) e per tabelle intere (es. `tomba_table`).

**Due nuove migrazioni standalone idempotenti** (pattern `2026_05_yef_other_locations.py`):

1. **`scripts/migrations/2026_05_inventario_materiali_schedatore_fields.py` + lib**: aggiunge le 5 colonne TEXT (`schedatore`, `date_scheda`, `punto_rinv`, `negativo_photo`, `diapositiva`) su `inventario_materiali_table` se mancanti.
2. **`scripts/migrations/2026_05_schema_repair.py` + lib**: audit completo + fix generico. Discover dinamico di tutti i `modules/db/structures/*.py` (47 file), crea le tabelle mancanti via `MetaData.create_all` (idempotente), poi delega alle migration granulari per le colonne note (`add_schedatore_columns` + `add_other_locations_column`). Returns un report `{tables_created, columns_added}`. Quando lanciato da CLI standalone (no env QGIS) traccia esplicitamente i moduli non importabili così l'utente capisce che l'audit è parziale; dentro QGIS l'audit è completo.

**Wire QGIS menu** (`pyarchinitPlugin.py`):
- `Migrazioni → Aggiungi colonne schedatore (inventario_materiali)` → handler con conferma + auto-backup + apply + report colonne aggiunte/già presenti.
- `Migrazioni → Schema repair (tabelle + colonne mancanti)` → handler con dry-run preview (tabelle mancanti listate) + warning se discovery parziale + conferma + auto-backup + apply + report completo.

**Applicato manualmente su `pyarchinit-AA39.sqlite`** durante il troubleshooting:
- Backup pre-fix: `pyarchinit-AA39.sqlite.backup_20260521_085102_pre_schedatore_fix` (6.8 MB).
- 5 colonne aggiunte a `inventario_materiali_table` (era a 0 righe).
- 1 colonna aggiunta a `us_table` (268 US preservate, count invariato).
- 1 tabella creata: `tomba_table` con schema da `modules/db/structures/Tomba_table.py`.
- Row count post-fix verificato: us_table=268, site_table=1, media_table=10 (tutti invariati vs backup). **Nessun dato perso.**

### English

**Bug 1 — `build_index_Casse` crashed with TypeError on empty box list.**

`tabs/Inv_Materiali.py:on_pushButton_print_pressed` called `Mat_casse_pdf.build_index_Casse(data_list, sito_ec)` without checks, while `generate_el_casse_pdf` had its `return data_for_pdf` **inside the try block**: if any SQL query raised (e.g. `res_luogo_conservazione[0]` on empty list → `IndexError`), the `except` showed the misleading warning "Il campo cassa non deve essere vuoto" and **implicitly returned `None`**. The caller passed that `None` to `build_index_Casse` which crashed on `range(len(None))`.

**Fix in 4 places**:
- `generate_el_casse_pdf` (line 5020): the `except` now explicitly returns `[]` + shows a message with exception type/message/full traceback (misleading text removed).
- 3 call sites of `on_pushButton_print_pressed` (line 4751 it, 4811 de, 4907 en): added `if not data_list:` with localized warning that skips PDF generation instead of crashing.

**Bug 2 — DB schema drift on DBs imported from old backups.**

The auto-migration in `modules/db/pyarchinit_db_update.py:446-459` adds the 5 schedatore columns IF `safe_load_table('inventario_materiali_table')` returns the table, BUT for DBs imported from backups or created by very old plugin versions `safe_load_table` returns `None` and the entire ADD COLUMN block is silently skipped. Same pattern for `us_table.other_locations` (yE-F 5.9.0-alpha migration) and for whole tables (e.g. `tomba_table`).

**Two new standalone idempotent migrations** (following `2026_05_yef_other_locations.py` pattern):

1. **`scripts/migrations/2026_05_inventario_materiali_schedatore_fields.py` + lib**: adds the 5 TEXT columns (`schedatore`, `date_scheda`, `punto_rinv`, `negativo_photo`, `diapositiva`) to `inventario_materiali_table` if missing.
2. **`scripts/migrations/2026_05_schema_repair.py` + lib**: full audit + generic fix. Dynamically discovers all `modules/db/structures/*.py` (47 files), creates missing tables via `MetaData.create_all` (idempotent), then delegates to granular migrations for known columns (`add_schedatore_columns` + `add_other_locations_column`). Returns a `{tables_created, columns_added}` report. When run via standalone CLI (no QGIS env) explicitly tracks non-importable modules so the user understands the audit is partial; inside QGIS the audit is complete.

**QGIS menu wire** (`pyarchinitPlugin.py`):
- `Migrazioni → Aggiungi colonne schedatore (inventario_materiali)` → handler with confirm + auto-backup + apply + report of added/already-present columns.
- `Migrazioni → Schema repair (tabelle + colonne mancanti)` → handler with dry-run preview (missing tables listed) + warning if discovery partial + confirm + auto-backup + apply + full report.

**Manually applied on `pyarchinit-AA39.sqlite`** during troubleshooting:
- Pre-fix backup: `pyarchinit-AA39.sqlite.backup_20260521_085102_pre_schedatore_fix` (6.8 MB).
- 5 columns added to `inventario_materiali_table` (was at 0 rows).
- 1 column added to `us_table` (268 US preserved, count unchanged).
- 1 table created: `tomba_table` with schema from `modules/db/structures/Tomba_table.py`.
- Post-fix row count verified: us_table=268, site_table=1, media_table=10 (all unchanged vs backup). **No data lost.**

---

## [post-5.9.0.1-alpha] - 2026-05-16 — LLM models refresh

> Commit `e05229a0` su branch `Stratigraph_00001`, **senza nuovo tag né bump di `metadata.txt`** (resta `5.9.0.1-alpha`). Aggiornamento puntuale al selettore modelli AI usato dal dialog "Interrogazione Database con AI (RAG)" e da tutte le feature LLM.

### Italiano

**Aggiunti GPT-5.5 e Claude Sonnet 4.6 nel selettore provider; routing automatico `max_completion_tokens` per famiglia GPT-5 e o-series.**

File toccato: `modules/utility/llm_providers.py` (+44 / −2).

**Modelli aggiunti**:

- **OpenAI** `default_models` (in testa): `gpt-5.5`, `gpt-5.5-2026-04-23`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1`. Rimosso `gpt-4-vision-preview` (deprecato). `vision_models` allineata. Modelli legacy (`gpt-4o*`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`) conservati per chi è ancora pinnato.
- **Anthropic** `default_models` (in testa): `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5`. `vision_models` allineata. ID dated 4-5 e 3-5 conservati.

**Token-param shim**:

- Nuova costante `OPENAI_MAX_COMPLETION_TOKENS_PREFIXES = ("gpt-5", "o1", "o3", "o4")` + helper `_openai_token_param(model)`.
- `LLMProviderManager.stream_chat()` branch OpenAI: ora invia `max_completion_tokens=N` per famiglia GPT-5 / o-series (che restituiscono 400 con `max_tokens`), e mantiene `max_tokens=N` per i modelli legacy + backend OpenAI-compatibili locali (Ollama, LM Studio).
- Branch Anthropic invariato: `max_tokens=` è il nome param ufficiale Anthropic.

**Verifica live**: chiamata reale a `api.openai.com` con `model='gpt-5.5'`, `max_tokens=20`, prompt "Reply with just OK.", risposta `'OK'`. Shim verificato su 8 model id (gpt-5.5, gpt-5.5-2026-04-23, gpt-5, gpt-5-mini, gpt-4o, gpt-3.5-turbo, o3-mini, o4-mini).

**Impatto UI**: i nuovi modelli compaiono nel dropdown del `RAGQueryDialog` (`tabs/US_USM.py:4079`) e in ogni altro consumer di `LLMSelectorWidget` al prossimo "Aggiorna modelli" o restart QGIS. La selezione salvata in QSettings non viene toccata.

### English

**Added GPT-5.5 and Claude Sonnet 4.6 to the provider selector; automatic `max_completion_tokens` routing for the GPT-5 family and o-series.**

File touched: `modules/utility/llm_providers.py` (+44 / −2).

**Models added**:

- **OpenAI** `default_models` (prepended): `gpt-5.5`, `gpt-5.5-2026-04-23`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1`. Removed `gpt-4-vision-preview` (deprecated). `vision_models` mirrored. Legacy models (`gpt-4o*`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`) kept for users still pinned.
- **Anthropic** `default_models` (prepended): `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5`. `vision_models` mirrored. Dated 4-5 / 3-5 IDs kept.

**Token-param shim**:

- New constant `OPENAI_MAX_COMPLETION_TOKENS_PREFIXES = ("gpt-5", "o1", "o3", "o4")` + helper `_openai_token_param(model)`.
- `LLMProviderManager.stream_chat()` OpenAI branch: now sends `max_completion_tokens=N` for the GPT-5 / o-series family (which 400 on `max_tokens`), keeps `max_tokens=N` for legacy models and OpenAI-compatible local backends (Ollama, LM Studio).
- Anthropic branch unchanged: `max_tokens=` is Anthropic's own param name.

**Live verification**: real call to `api.openai.com` with `model='gpt-5.5'`, `max_tokens=20`, prompt "Reply with just OK.", reply `'OK'`. Shim verified on 8 model IDs (gpt-5.5, gpt-5.5-2026-04-23, gpt-5, gpt-5-mini, gpt-4o, gpt-3.5-turbo, o3-mini, o4-mini).

**UI impact**: new models appear in the `RAGQueryDialog` dropdown (`tabs/US_USM.py:4079`) and in every other `LLMSelectorWidget` consumer at next "Refresh models" or QGIS restart. Saved QSettings selection is left untouched.

---

## [5.9.0.1-alpha] - 2026-05-16

### Italiano

**yE-F hotfix — primary `attivita` non più sovrascritta dall'ultimo folder iterato, niente più duplicato in `other_locations`.**

Tag `yed-f-fix-duplicate-primary-5.9.0.1-alpha` (commit `1653363c` su branch `Stratigraph_00001`). Hotfix immediato post-5.9.0 scoperto su `Extended_Matrix_test_1.graphml` (5 occorrenze D.01 in 5 folder VA01-VA05).

**Bug**: dopo un import yE-F pulito, la `attivita` primaria della riga fold finiva sovrascritta dal **last folder iterato** (es. D.01 atterrava su `attivita='VA01'` anziché `'VA02'` primo-in-doc-order), e il valore primario veniva anche **duplicato dentro `other_locations`**.

**Root cause**: `_apply_yed_folder_dimensions` (chiamata dopo `_write_us_rows`) itera ogni folder ed esegue `UPDATE us_table SET <dim>=<value> WHERE node_uuid IN (...)`. Per le righe fold paradata (5 occorrenze yEd → 1 riga `us_table` → 1 `node_uuid` condiviso), l'UPDATE di ogni folder colpiva la stessa riga; vinceva l'ultima iterazione.

**Fix**: quando `dim == "attivita"`, skip dei `node_uuid` paradata in `_apply_yed_folder_dimensions` — yE-F ha già scritto la primary corretta (primo folder in document order) durante l'INSERT del fold. Promosso `_PARADATA_NODEDUP_UTS` a costante module-level. Aggiunto test regressione `test_apply_yed_folder_dimensions_skips_paradata_attivita` che asserisce che `attivita` resta sul folder primo-in-doc-order e non viene duplicato in `other_locations`.

**Test**: 351 → **352 sync tests passed** (+1 regression test), 35 skipped (PG offline), 0 failed. AC-2 byte-identical preservato.

**Compatibilità**: fix SQL portabile (`text()` + named bind params). Funziona sia su SQLite che PostgreSQL. PG `conftest_pg.py` DDL esteso con colonna `other_locations`.

**Versioning**: patch `5.9.0 → 5.9.0.1-alpha`. Predecessor: `yed-f-multifolder-5.9.0-alpha` (commit `83d82f40`).

### English

**yE-F hotfix — primary `attivita` no longer overwritten by the last iterated folder, no more duplicate in `other_locations`.**

Tag `yed-f-fix-duplicate-primary-5.9.0.1-alpha` (commit `1653363c` on branch `Stratigraph_00001`). Immediate post-5.9.0 hotfix discovered on `Extended_Matrix_test_1.graphml` (5 D.01 occurrences in 5 folders VA01-VA05).

**Bug**: after a clean yE-F import, the primary `attivita` of the fold row ended up overwritten by the **last folder iterated** (e.g. D.01 landed on `attivita='VA01'` instead of `'VA02'` first-in-doc-order), and the primary value was also **duplicated inside `other_locations`**.

**Root cause**: `_apply_yed_folder_dimensions` (called after `_write_us_rows`) iterates every folder and runs `UPDATE us_table SET <dim>=<value> WHERE node_uuid IN (...)`. For paradata fold rows (5 yEd occurrences → 1 `us_table` row → 1 shared `node_uuid`), every folder's UPDATE hit the same row; the last iteration won.

**Fix**: when `dim == "attivita"`, skip paradata `node_uuid`s in `_apply_yed_folder_dimensions` — yE-F has already written the correct primary (first folder in document order) during fold INSERT. Promoted `_PARADATA_NODEDUP_UTS` to module-level constant. Added regression test `test_apply_yed_folder_dimensions_skips_paradata_attivita` asserting `attivita` stays on the first-in-doc-order folder and is not duplicated in `other_locations`.

**Tests**: 351 → **352 sync tests passed** (+1 regression test), 35 skipped (PG offline), 0 failed. AC-2 byte-identical preserved.

**Compatibility**: portable SQL fix (`text()` + named bind params). Works on both SQLite and PostgreSQL. PG `conftest_pg.py` DDL extended with `other_locations` column.

**Versioning**: patch `5.9.0 → 5.9.0.1-alpha`. Predecessor: `yed-f-multifolder-5.9.0-alpha` (commit `83d82f40`).

---

## [5.9.0-alpha] - 2026-05-16

### Italiano

**yE-F multi-folder paradata — fold-to-one-row model che supera il trade-off Bug R B1.**

Tag `yed-f-multifolder-5.9.0-alpha` (commit `83d82f40` su branch `Stratigraph_00001`). yE-F sostituisce il trade-off Bug R B1 introdotto in `5.8.5-alpha` (una riga `us_table` per ogni occorrenza yEd di paradata multi-folder, con suffisso `_2`/`_3`) con un modello a **una sola riga canonica per paradata** che porta una lista di "altre attività" e produce N copie visive in export. Identity-dedup ripristinata, multi-folder visibility preservata. 16 task pianificati, 16 commit indipendentemente revertabili.

**Modello dati**:

- **Nuova colonna `us_table.other_locations`** (TEXT, JSON list dei codici attività secondari). Migration lib `scripts/migrations/_2026_05_yef_other_locations_lib.py` + CLI `scripts/migrations/2026_05_yef_other_locations.py` + wire menu QGIS **Plugins → pyArchInit → "Migrazioni → Aggiungi colonna other_locations (yE-F)"** (file-picker + auto-backup + conferma).

**Pipeline**:

- **Import fold** (`modules/s3dgraphy/sync/yed_import_pipeline.py`): `_write_us_rows` ora produce **una sola riga `us_table`** per ogni label paradata unica, indipendentemente dal numero di occorrenze yEd. `attivita` = primo folder incontrato; folder successivi accodati a `other_locations` JSON. Niente più suffissi `_2`/`_3` su `us` per i kinds paradata.
- **Export fan-out** (`modules/s3dgraphy/sync/graphml_writer.py`): nuovo `_apply_yef_fan_out` emette N copie visive yEd per ogni riga paradata multi-folder (1 primary + N-1 secondaries), tutte con lo stesso `node_uuid` canonico per il round-trip identity.
- **Edge resolver** (`modules/s3dgraphy/sync/graph_projector.py`): nuovo `_resolve_target_for_folder` seleziona, per ogni edge che punta a un target multi-folder, la copia il cui `attivita` matcha il folder della source; fallback alla primary copy se nessun match.

**UI**:

- Nuovo `listWidget_other_locations` (QListWidget, MultiSelection) + `label_other_locations` in `gui/ui/US_USM.ui` tab_2.
- Handler populate/save in `tabs/US_USM.py`; visibilità reattiva al `comboBox_unita_tipo` (mostra solo per paradata kinds: DOC/Combinar/Extractor/property).
- i18n in **10 lingue**: it/en/de/es/fr/ar/ca/ro/pt/el.

**Coesistenza con dati B1**:

- I dati multi-row B1 esistenti in `pyarchinit_test{002..010}.sqlite` (suffissi `_2`/`_3` ancora in `us`) restano leggibili: pre-load loop con degradazione a 2 livelli + resolver no-op quando `_yef_copies_by_canonical` è vuoto.

**Test**: 312 → **351 sync tests** (+39 nuovi test yE-F), 35 skipped (PG offline), 0 failed. AC-2 byte-identical preservato (resolver attivo solo quando fan-out ha già modificato il graph).

**Versioning**: minor `5.8.5 → 5.9.0-alpha`. Predecessor: `yed-fastfix-5.8.5-alpha` (commit `a5e8502b`).

### English

**yE-F multi-folder paradata — fold-to-one-row model superseding the Bug R B1 trade-off.**

Tag `yed-f-multifolder-5.9.0-alpha` (commit `83d82f40` on `Stratigraph_00001`). yE-F replaces the Bug R B1 trade-off introduced in `5.8.5-alpha` (one `us_table` row per yEd occurrence of multi-folder paradata, with `_2`/`_3` suffix) with a **single canonical row per paradata** carrying a list of "other activities" and producing N visual copies on export. Identity-dedup restored, multi-folder visibility preserved. 16 planned tasks, 16 independently revertable commits.

**Data model**:

- **New `us_table.other_locations` column** (TEXT, JSON list of secondary activity codes). Migration lib `scripts/migrations/_2026_05_yef_other_locations_lib.py` + CLI `scripts/migrations/2026_05_yef_other_locations.py` + QGIS menu wire **Plugins → pyArchInit → "Migrazioni → Aggiungi colonna other_locations (yE-F)"** (file-picker + auto-backup + confirm).

**Pipeline**:

- **Import fold** (`modules/s3dgraphy/sync/yed_import_pipeline.py`): `_write_us_rows` now produces **one `us_table` row** per unique paradata label, regardless of N yEd occurrences. `attivita` = first folder encountered; subsequent folders appended to `other_locations` JSON. No more `_2`/`_3` suffixes on `us` for paradata kinds.
- **Export fan-out** (`modules/s3dgraphy/sync/graphml_writer.py`): new `_apply_yef_fan_out` emits N visual yEd copies per multi-folder paradata row (1 primary + N-1 secondaries), all sharing the canonical `node_uuid` for round-trip identity.
- **Edge resolver** (`modules/s3dgraphy/sync/graph_projector.py`): new `_resolve_target_for_folder` picks, for each edge pointing to a multi-folder target, the copy whose `attivita` matches the source's folder; falls back to the primary copy if no match.

**UI**:

- New `listWidget_other_locations` (QListWidget, MultiSelection) + `label_other_locations` in `gui/ui/US_USM.ui` tab_2.
- Populate/save handlers in `tabs/US_USM.py`; visibility reactive to `comboBox_unita_tipo` (shown only for paradata kinds: DOC/Combinar/Extractor/property).
- i18n in **10 languages**: it/en/de/es/fr/ar/ca/ro/pt/el.

**Coexistence with B1 data**:

- Existing B1 multi-row data in `pyarchinit_test{002..010}.sqlite` (`_2`/`_3` suffixes still in `us`) remains readable: pre-load loop with 2-tier degradation + resolver is a no-op when `_yef_copies_by_canonical` is empty.

**Tests**: 312 → **351 sync tests** (+39 new yE-F tests), 35 skipped (PG offline), 0 failed. AC-2 byte-identical preserved (resolver only activates when fan-out has already touched the graph).

**Versioning**: minor `5.8.5 → 5.9.0-alpha`. Predecessor: `yed-fastfix-5.8.5-alpha` (commit `a5e8502b`).

---

## [5.8.5-alpha] - 2026-05-16

### Italiano

**yed-fastfix — 19 bug (A→T) corretti sul pipeline yEd-aware import, scoperti tramite test manuali su `pyarchinit_test{002..010}.sqlite`.**

Tag `yed-fastfix-5.8.5-alpha` (commit `a5e8502b` su branch `Stratigraph_00001`). Round di hardening intensivo post-5.8.3 sul percorso yEd-aware import: 19 bug nominali risolti, tutti scoperti via test manuali iterativi su 9 fixture SQLite (`pyarchinit_test002.sqlite` → `pyarchinit_test010.sqlite`). Nessun bug architetturale, tutto comportamentale/edge-case.

**Bug breakdown per modulo**:

**`modules/s3dgraphy/sync/yed_import_pipeline.py`** (core del fix):

- **A — rapporti tuple format**: tuple `[type, us_target, area, sito]` aveva posizioni 1 e 3 scambiate; reader pyarchinit non risolveva il target.
- **B — period_iniziale/fase_iniziale** propagati a `us_table` dai `PeriodCandidate.member_yed_ids`.
- **C — periodizzazione_table.cont_per** popolato (campo UI "Codice periodo" ora valorizzato).
- **E — us stripped + dual-write**: `us_table.us` stripped del prefisso `unita_tipo` (`'US100'` → `'100'`); SF/VSF/RSF dual-write su `us_table` + `inventario_materiali`.
- **F — rapporti tokens via `_select_rapporti_label`** per `unita_tipo`: verboso IT per US/USM, `>>`/`<<` per altri, `>`/`<` per CON.
- **G — DOC/Combinar/Extractor/property** diventano record `us_table` con `unita_tipo` corretto, **non** `paradata.graphml`.
- **H — idempotent re-import**: skip-if-exists su `us_table`, `inventario`, `periodizzazione`.
- **M — default edge_type=`generic_connection`** quando endpoint paradata (overrides `overlies` invalido US↔Document).
- **R — B1 multi-folder trade-off**: i paradata kinds saltano il dedup-by-identity; ogni occorrenza yEd è una sua riga; `us` suffix `_2`/`_3` per disambiguare; `d_stratigrafica` = label originale. **Trade-off scelto**: multi-folder visibility > identity-dedup per le paradata families.
- **S — rapporti target resolved at per-occurrence us value** (es. `01_2`, `01_3`), non shared stripped label.
- **T — rapporti reciprocity**: forward sulla riga del source + inverse (`<<`, "Coperto da") sulla riga del target.

**`modules/s3dgraphy/sync/yed_classifier.py`**:

- **D — EXTRACTOR**: aggiunto a `ClassificationKind` enum + regex `^E\.\d+`.
- **I — BPMN-aware classifier**: D.NN con BPMN data-object → DOCUMENT; D.NN.MM senza → EXTRACTOR. Senza questa distinzione il dedup collassava i due tipi in una sola riga e gli edges sparivano.

**`modules/s3dgraphy/sync/graph_projector.py`**:

- **K — composite-key `(name, unita_tipo)` → node_by_key index**: evita aliasing su `_find_node_by_name` del bridge.
- **N — reorder**: `_propagate_node_uuid_and_us` PRIMA di `_enrich_into`; family-preference target resolution per attributo `unita_tipo`.
- **P — row-paradata as StratigraphicNode-class instances**: `StratigraphicUnit` con `attributes['unita_tipo']='DOC'/'Combinar'/etc.` per swimlane integration in `GraphMLExporter`. Reverte l'approccio precedente (Bug O) che le trattava come paradata-class isolate.

**`modules/s3dgraphy/sync/graphml_writer.py`**:

- **Q — USV palette entry** aggiunta (mirrora USVs — parallelogramma blu, fill nero, testo bianco); property label legge `d_stratigrafica` con fallback (basta con `'propertymaterial'`).

**`gui/yed_import_dialog.py`**:

- **J — `_kind_choices`** include ora EXTRACTOR (fixa `ValueError` nel wizard).

**Trade-off principale** (Bug R): per le paradata families la multi-folder visibility ha avuto precedenza sull'identity-dedup. Ogni occorrenza yEd di un Documento/Combinar/Extractor produce ora una propria riga `us_table` (con suffisso `_2`/`_3`), per garantire che la struttura visiva yEd (folder placement) sopravviva al round-trip. Conseguenza: contenuto duplicato in `d_stratigrafica` per le righe figlie, ma rapporti coerenti per ciascuna occorrenza (Bug S+T).

**Test**: 311 → **329 passed** (+18 regression tests aggiunti), 0 regression. AC-2 byte-identical preservato.

**Versioning**: minor `5.8.3 → 5.8.5-alpha` (salto 5.8.4 — riservato a dry-run interno non-rilasciato). Predecessor: `yed-import-closure-5.8.3-alpha` (commit `cbc2a5b7`).

### English

**yed-fastfix — 19 bugs (A→T) fixed across the yEd-aware import pipeline, discovered via manual testing on `pyarchinit_test{002..010}.sqlite`.**

Tag `yed-fastfix-5.8.5-alpha` (commit `a5e8502b` on `Stratigraph_00001`). Intensive post-5.8.3 hardening round on the yEd-aware import path: 19 named bugs resolved, all discovered via iterative manual testing against 9 SQLite fixtures. No architectural bugs, all behavioral / edge-case.

**Bug breakdown by module**:

**`modules/s3dgraphy/sync/yed_import_pipeline.py`** (main work):

- **A — rapporti tuple format**: tuple `[type, us_target, area, sito]` had positions 1 and 3 swapped; pyarchinit reader could not resolve the target.
- **B — period_iniziale/fase_iniziale** propagated to `us_table` from `PeriodCandidate.member_yed_ids`.
- **C — periodizzazione_table.cont_per** populated (UI "Codice periodo" field).
- **E — us stripped + dual-write**: `us_table.us` stripped of `unita_tipo` prefix (`'US100'` → `'100'`); SF/VSF/RSF dual-write to `us_table` + `inventario_materiali`.
- **F — rapporti tokens via `_select_rapporti_label`** by `unita_tipo`: verbose IT for US/USM, `>>`/`<<` for others, `>`/`<` for CON.
- **G — DOC/Combinar/Extractor/property** become `us_table` records with proper `unita_tipo`, **not** `paradata.graphml`.
- **H — idempotent re-import**: skip-if-exists on `us_table`, `inventario`, `periodizzazione`.
- **M — default edge_type=`generic_connection`** when paradata endpoint (overrides invalid `overlies` US↔Document).
- **R — B1 multi-folder trade-off**: paradata kinds skip dedup-by-identity; each yEd occurrence becomes its own row; `us` suffix `_2`/`_3` to disambiguate; `d_stratigrafica` keeps the original label. **Trade-off chosen**: multi-folder visibility > identity-dedup for paradata families.
- **S — rapporti target resolved at per-occurrence us value** (e.g. `01_2`, `01_3`), not shared stripped label.
- **T — rapporti reciprocity**: forward on source row + inverse (`<<`, "Coperto da") on target row.

**`modules/s3dgraphy/sync/yed_classifier.py`**:

- **D — EXTRACTOR** added to `ClassificationKind` enum + regex `^E\.\d+`.
- **I — BPMN-aware classifier**: D.NN with BPMN data-object → DOCUMENT; D.NN.MM without → EXTRACTOR. Without this distinction the dedup collapsed both types into a single row and edges disappeared.

**`modules/s3dgraphy/sync/graph_projector.py`**:

- **K — composite-key `(name, unita_tipo)` → node_by_key index**: avoids aliasing in the bridge's `_find_node_by_name`.
- **N — reorder**: `_propagate_node_uuid_and_us` BEFORE `_enrich_into`; family-preference target resolution by `unita_tipo` attribute.
- **P — row-paradata as StratigraphicNode-class instances**: `StratigraphicUnit` with `attributes['unita_tipo']='DOC'/'Combinar'/etc.` for swimlane integration in `GraphMLExporter`. Reverts the earlier (Bug O) approach that treated them as isolated paradata classes.

**`modules/s3dgraphy/sync/graphml_writer.py`**:

- **Q — USV palette entry** added (mirrors USVs — blue parallelogram, black fill, white text); property label reads `d_stratigrafica` with fallback (no more `'propertymaterial'`).

**`gui/yed_import_dialog.py`**:

- **J — `_kind_choices`** now includes EXTRACTOR (fixes `ValueError` in the wizard).

**Main trade-off** (Bug R): for paradata families, multi-folder visibility took precedence over identity-dedup. Each yEd occurrence of a Document/Combinar/Extractor now produces its own `us_table` row (with `_2`/`_3` suffix) so the yEd visual structure (folder placement) survives the round-trip. Consequence: duplicated content in `d_stratigrafica` for child rows, but coherent rapporti per occurrence (Bug S+T).

**Tests**: 311 → **329 passed** (+18 regression tests added), 0 regressions. AC-2 byte-identical preserved.

**Versioning**: minor `5.8.3 → 5.8.5-alpha` (skipped 5.8.4 — reserved for internal unreleased dry-run). Predecessor: `yed-import-closure-5.8.3-alpha` (commit `cbc2a5b7`).

---

## [5.8.3-alpha] - 2026-05-14

### Italiano

**yE-Closure — sign-off del rollout yEd-aware import (6/6 milestone shipped).**

Sesto e ultimo milestone della rollout `yEd-aware-graphml-import`. Sign-off + documentazione user-facing + dev-log + CHANGELOG. Nessun codice di produzione modificato.

**Tutorial 36** (`docs/tutorials/<lang>/36_extended_matrix_s3dgraphy.md`) — esteso con nuova sezione **"5. yEd-aware Import"** in **IT + EN** (deferred per le altre 8 langs: de/es/fr/ar/ca/ro/pt/el — saranno aggiornate via `tutorial-updater` agent in batch separato). La sezione copre:
- Rollout 6-milestone con tabella tag
- User flow del 5-page wizard (`YedImportDialog`)
- Routing destinazioni per ogni ClassificationKind (US/USM/USD/USV/USVs/USVn/USVc/RSF/SF/VSF/DOC/COMB/PROP)
- Sidecar JSON `<graphml>.yed_overrides.json` schema versionato
- CLI `scripts/import_yed_graphml.py` con `--overrides PATH`
- Limiti noti (date editing assente, ParadataStore API parziale, PropertyNode Path B, sidecar per-graphml)
- Test coverage finale: 354 passed / 42 skipped

**Dev-log T5.4** (`docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`) — prepend sezione yE-Closure + yE-E + yE-D sopra le sezioni esistenti yE-C/B/A. La sezione yE-Closure include:
- Sign-off summary (cosa è stato consegnato)
- Tag chronology (10 tag dal 2026-05-12 al 2026-05-14: 6 yE + s3dgraphy-bump + 3 pg-pottery fix)
- Test coverage breakdown per suite file
- AC-2 byte-identical preservation summary
- Known follow-ups deferred (ParadataStore upstream, PropertyNode linkage, 8 lang translation, api-docs RTD)
- TODO list dettagliato per il PR api-docs su repo esterno

**api-docs RTD** — DEFERRED. Sandbox macOS blocca `~/Downloads/pyarchinit-api-docs/` da questa session. TODO list completa nel dev-log con elenco dei nuovi simboli pubblici da documentare (`YedOverrides`, `apply_overrides_to_drafts`, `import_yed_raw`, `FolderEdgePolicy`, `YedImportDialog`, etc.) e mappatura file `.rst` target. Il PR è autosufficiente: docstring sono già in place, basta aggiungere `.. automodule::` entries.

**Versioning**: patch `5.8.2.3 → 5.8.3-alpha`. Chiude la serie 5.8.x della rollout yEd-aware import. Predecessor: `pg-pottery-typefix-5.8.2.3-alpha` (commit `3f30d368`, pushato).

**Test count finale**: 354 passed / 42 skipped, invariato (yE-Closure è doc-only, nessuna modifica produzione).

**Bilancio rollout** (2026-05-12 → 2026-05-14, 3 giorni):
- 6 yE milestone (yE-A/B/C/D/E/Closure)
- 1 dependency bump (s3dgraphy 0.1.41 → 0.1.42 con RSF integration)
- 3 PG-pottery hotfix (coercion bidirezionale + belt-and-braces + declaration align)
- +56 test (298 → 354)
- AC-2 byte-identical preservato su tutti e 10 i tag

### English

**yE-Closure — sign-off of the yEd-aware import rollout (6/6 milestones shipped).**

Sixth and final milestone of the `yEd-aware-graphml-import` rollout. Sign-off + user-facing documentation + dev-log + CHANGELOG. No production code touched.

**Tutorial 36** (`docs/tutorials/<lang>/36_extended_matrix_s3dgraphy.md`) — extended with a new **"5. yEd-aware Import"** section in **IT + EN** (other 8 langs deferred: de/es/fr/ar/ca/ro/pt/el — to be updated via `tutorial-updater` agent in a separate batch). Section covers: 6-milestone tag chronology, user flow of the 5-page wizard, destination routing per ClassificationKind, sidecar JSON schema, CLI `--overrides` flag, known limits, final test coverage.

**Dev-log T5.4** — prepended yE-Closure + yE-E + yE-D sections above existing yE-C/B/A. yE-Closure section includes sign-off summary, 10-tag chronology, per-suite test coverage breakdown, AC-2 preservation summary, deferred follow-ups, detailed TODO list for the external api-docs PR.

**api-docs RTD** — DEFERRED. macOS sandbox blocks `~/Downloads/pyarchinit-api-docs/` from this session. Complete TODO list in the dev-log with new public symbols to document and target `.rst` file mapping. Self-contained PR (docstrings already in place, just add `.. automodule::` entries).

**Versioning**: patch `5.8.2.3 → 5.8.3-alpha`. Closes the 5.8.x series of the yEd-aware import rollout. Predecessor: `pg-pottery-typefix-5.8.2.3-alpha` (commit `3f30d368`).

Suite count unchanged: 354 passed / 42 skipped (doc-only milestone).

**Rollout balance sheet** (2026-05-12 → 2026-05-14, 3 days):
- 6 yE milestones (yE-A/B/C/D/E/Closure)
- 1 dependency bump (s3dgraphy 0.1.41 → 0.1.42 with RSF integration)
- 3 PG-pottery hotfixes (bidirectional coercion + belt-and-braces + declaration align)
- +56 tests (298 → 354)
- AC-2 byte-identical preserved across all 10 tags

---

## [5.8.2.3-alpha] - 2026-05-14

### Italiano

**pg-pottery-typefix — schema declaration disallineata: `Pottery_table.us` + `US_table.us` dichiarati Integer ma il DB ha TEXT.**

Diagnosi finale dell'errore `operator does not exist: text = integer LINE 3: ... pottery_table.us = 672` persistente attraverso 5.8.2.1 e 5.8.2.2. La full traceback ha rivelato:

```
File "tabs/pyarchinit_Pottery_mainapp.py", line 3645, in on_pushButton_search_go_pressed
    res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
```

Il caller passava `us = "672"` (str da `lineEdit_us.text()`). Il mio `_normalize_query_params` + belt-and-braces leggevano `column.type.python_type` per decidere la coercion. Per `pottery_table.us`, il `python_type` era **`int`** — perché `modules/db/structures/Pottery_table.py:19` dichiarava `Column('us', Integer)`. Quindi:

- input: `us = "672"` (str)
- coercion: `isinstance(str) AND col_pytype in (int, float)` → True → `int("672")` → **672**
- SQL bind: `us_1 = 672` (int)
- PG: TEXT column rifiuta `text = integer` → ERROR

**Il vero problema**: pyarchinit declared **Integer** ma PG schema (e tutti i deploy reali archeologici) usano **TEXT** per la colonna `us`. SQLite type-loose nascondeva il bug; PG strict-typing lo ha esposto.

**Fix definitivo**: allineamento delle declaration al DB reale:

| File | Was | Now |
|---|---|---|
| `modules/db/structures/Pottery_table.py:19` | `Column('us', Integer)` | `Column('us', Text)` |
| `modules/db/structures/US_table.py:20` | `Column('us', Integer)` | `Column('us', Text)` |

**Audit corollario** (eseguito): altre tabelle con colonna `us` su PG online khutm2:
- `archeozoology_table.us` → TEXT ✓
- `campioni_table.us` → TEXT ✓
- `individui_table.us` → TEXT ✓
- `inventario_materiali_table.us` → TEXT (già allineato, declaration `Column('us', Text)`) ✓
- `pottery_table.us` → TEXT (**fix shipped**)
- `us_table.us` → TEXT (**fix shipped**)
- `media_to_us_table.us` → bigint (declaration matches, BIGINT)
- `periodizzazione_table.us` → integer
- `fauna.us` → integer (legacy backup table, no fix needed)

**Effetti collaterali**: nessuno su SQLite (type-loose, accetta sia int che str). Su PG il bug `text = integer` non si presenterà più per pottery_table e us_table. La bidirectional coercion (5.8.2.1-alpha) + belt-and-braces (5.8.2.2-alpha) restano come safety net per altre tabelle che dovessero avere disallineamenti analoghi futuri.

**Versioning**: patch `5.8.2.2 → 5.8.2.3-alpha`. Predecessor: `pg-pottery-fix-belt-and-braces-5.8.2.2-alpha` (commit `3f6956d2`, pushato).

### English

**pg-pottery-typefix — schema declaration mismatch: `Pottery_table.us` + `US_table.us` declared Integer but PG schema is TEXT.**

Final diagnosis of the persistent `operator does not exist: text = integer` error through 5.8.2.1 and 5.8.2.2. Full traceback revealed the caller passes `us = "672"` (str from `lineEdit_us.text()`). My `_normalize_query_params` + belt-and-braces read `column.type.python_type` to decide coercion. For `pottery_table.us`, `python_type` returned **`int`** because `Pottery_table.py:19` declared `Column('us', Integer)`. So the bidirectional logic coerced str "672" → int 672, SQL bound `us_1=672` (int), and PG TEXT column rejected `text = integer`.

**Root cause**: pyarchinit declared Integer but PG schema (and all real archaeological deploys) use TEXT for the `us` column. SQLite's type-loose comparison hid the bug; PG strict-typing exposed it.

**Fix**: align the declarations to the actual DB schema:
- `modules/db/structures/Pottery_table.py:19`: `Integer` → `Text`.
- `modules/db/structures/US_table.py:20`: `Integer` → `Text`.

Audit confirmed `Inventario_materiali_table.py` already had `Column('us', Text)`. No other us-column mismatches found across `archeozoology / campioni / individui / pottery / us / inventario / media_to_us / periodizzazione`.

Side effects: none on SQLite. PG `text = integer` error gone for pottery and us tables. The bidirectional coercion (5.8.2.1) + belt-and-braces (5.8.2.2) remain as safety net for any future type-mismatch discoveries.

Versioning: patch `5.8.2.2 → 5.8.2.3-alpha`. Predecessor: `pg-pottery-fix-belt-and-braces-5.8.2.2-alpha` (commit `3f6956d2`).

---

## [5.8.2.2-alpha] - 2026-05-14

### Italiano

**pg-pottery-fix belt-and-braces — coercion replicata anche dentro `query_bool` loop.**

L'utente ha segnalato che dopo 5.8.2.1-alpha l'errore `operator does not exist: text = integer LINE 3: ... pottery_table.us = 672` persisteva. Diagnosi: il fix in `_normalize_query_params` era corretto on-disk (test inline confermato: `{us: 672}` → `{us: '672'}`), ma **Plugin Reloader di QGIS non rimuove i moduli da `sys.modules`** — quindi la classe `Pyarchinit_db_management` retained in memoria continuava a invocare la vecchia `_normalize_query_params` senza il blocco bidirezionale.

**Fix preventivo**: aggiunta una **seconda coercion DENTRO il loop di `query_bool`** (linea ~2996-3010), subito prima di `conditions.append(column == value)`. Anche se `_normalize_query_params` viene bypassato (per stale cache, hot-reload, future refactor), il valore viene comunque coerced contro `column.type.python_type` prima di finire nella query SQLAlchemy. Stessa logica bidirezionale di `_normalize_query_params`. Idempotente: no-op quando `value` è già del tipo corretto. Costo: 1 attribute access + 1 isinstance per ogni param di ogni `query_bool` (trascurabile vs DB roundtrip).

**Versioning**: patch `5.8.2.1 → 5.8.2.2-alpha`. Predecessor: `pg-pottery-fix-5.8.2.1-alpha` (commit `2788ccf7`, pushato).

### English

**pg-pottery-fix belt-and-braces — coercion replicated inside `query_bool` loop.**

User reported the `text = integer` error persisted after 5.8.2.1-alpha. Diagnosis: the fix in `_normalize_query_params` is correct on-disk (inline test confirms `{us: 672}` → `{us: '672'}`), but **QGIS Plugin Reloader does NOT remove modules from `sys.modules`** — the `Pyarchinit_db_management` class instance kept in memory used the cached pre-fix `_normalize_query_params`.

**Defensive fix**: added a **second coercion INSIDE the `query_bool` loop** (line ~2996-3010), right before `conditions.append(column == value)`. Even if `_normalize_query_params` is bypassed (stale cache / hot-reload / future refactor), the value is coerced against `column.type.python_type` before reaching SQLAlchemy. Same bidirectional logic as `_normalize_query_params`. Idempotent: no-op when value already matches. Negligible cost.

Versioning: patch `5.8.2.1 → 5.8.2.2-alpha`. Predecessor: `pg-pottery-fix-5.8.2.1-alpha` (commit `2788ccf7`).

---

## [5.8.2.1-alpha] - 2026-05-14

### Italiano

**pg-pottery-fix — `_normalize_query_params` bidirezionale per coercion int→str su colonne TEXT in PG.**

L'utente ha segnalato 2026-05-14 mattina che aprire un pottery sul DB online khutm2 (PG) fallisce con `psycopg2.errors.UndefinedFunction: operator does not exist: text = integer LINE 3: ... pottery_table.us = 672`. Stessa famiglia di bug di `pg-media-fix` (5.7.9.1-alpha) ma direzione inversa:

- pg-media-fix: caller passava `'42'` (str) ma colonna `MEDIATOENTITY.id_entity` era BIGINT → coercion `str → int`.
- **pg-pottery-fix**: caller passa `672` (int, da uno SpinBox widget) ma colonna `pottery_table.us` è TEXT → PostgreSQL strict-typing rifiuta `text = integer`.

**Root cause**: `_normalize_query_params` in `modules/db/pyarchinit_db_manager.py:2802-2827` (introdotto da pg-media-fix) catturava solo `isinstance(value, str) AND col_pytype in (int, float)`. Il caso inverso (`value` int + colonna TEXT) restava non-coerced e finiva nella query SQLAlchemy ORM, dove `pottery_table.us == 672` generava il SQL `WHERE pottery_table.us = %(us_1)s` con bind param int → PG error.

**Fix** (~13 LOC delta): esteso `_normalize_query_params` per essere **bidirezionale**. Ora il blocco coercion riconosce 2 direzioni:
- `str + numeric column` → `col_pytype(value)` (pre-esistente pg-media-fix).
- `int/float + str column` → `str(value)` (nuovo pg-pottery-fix). Esclude `bool` (sotto-tipo di int) per evitare di convertire `True/False` in `"True"/"False"`.

**Test**: 2 nuovi L0 in `tests/migrations/test_pg_media_fix.py` (5 → 7 totali nel file):
- `test_query_bool_coerces_int_to_str_for_text_column`: caller passa `672` int + colonna TEXT, dopo coercion → `'672'` (str).
- `test_query_bool_int_to_str_coercion_safe_for_numeric_column`: caller passa `42` int + colonna Integer → resta int (la coercion inversa non deve sparare).

**Universalità**: come pg-media-fix, opera a runtime sulla declaration SQLAlchemy dell'entity. Funziona su tutti i DB PG pyarchinit (vecchi e nuovi) senza migrazioni. SQLite type-loose è no-op behaviour-wise.

**Test count**: 352 → 354 passed, 42 skipped.

**Versioning**: patch `5.8.2 → 5.8.2.1-alpha`. Predecessor: `yed-import-dialog-5.8.2-alpha` (commit `7120dc23`, locale non-pushato; il push avviene con questo hotfix). yE-Closure resta `5.8.3-alpha`.

### English

**pg-pottery-fix — `_normalize_query_params` bidirectional, int→str coercion for TEXT 'us' on PG.**

User-reported 2026-05-14: opening a pottery record on the online khutm2 PG fails with `psycopg2 UndefinedFunction: operator does not exist: text = integer`. Same family as pg-media-fix but inverse direction: caller passes int (from SpinBox), `pottery_table.us` is TEXT.

Fix: extended `_normalize_query_params` to be bidirectional — int/float + str column → coerce to str; pre-existing str + numeric column → coerce to int/float. `bool` excluded to avoid `True → "True"`.

2 new L0 tests. Suite: 352 → 354 passed, 42 skipped.

Versioning: patch `5.8.2 → 5.8.2.1-alpha`. Predecessor: `yed-import-dialog-5.8.2-alpha` (commit `7120dc23`).

---

## [5.8.2-alpha] - 2026-05-13

### Italiano

**yE-E Dialog UX — Qt wizard 5 pagine per override su yEd-raw import.**

Quinto dei 6 milestone del rollout yEd-aware-graphml-import. yE-D ha shippato hardcoded defaults (classifier auto, period auto, folder dimension auto, rapporti SKIP). yE-E aggiunge la Qt dialog che apre **prima del commit** e permette all'utente di overridare le scelte.

**Componenti**:

1. **`YedOverrides` dataclass** in `yed_import_pipeline.py`: 4 campi opzionali (`classifier`, `periods`, `folders`, `policy`) che catturano i diff utente. `apply_overrides_to_drafts(drafts, overrides)` è una pure function che ritorna un nuovo drafts dict con `user_*` valorizzati. `import_yed_raw()` accetta nuovo parametro `overrides: YedOverrides | None = None` (None = comportamento yE-D, AC-1 preservato).

2. **`gui/yed_import_dialog.py`** (~570 LOC): `YedImportDialog(QWizard)` con 5 `QWizardPage`:
   - **1/5 Classifier**: tabella con combobox per riga (13 ClassificationKind options compreso RSF di s3dgraphy 0.1.42), bottone "Accetta auto".
   - **2/5 Periods**: tabella editable per `periodo` + `fase`, bottone "Ripristina auto".
   - **3/5 Folders**: combobox per riga con 7 dimension valide + `'skip'` sentinel + value text.
   - **4/5 Rapporti policy**: 4 radio button SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC.
   - **5/5 Preview**: dry-run pass di `import_yed_raw(overrides=...)` con count display.
   
   Costruzione programmatica delle pagine (no .ui XML): table content dinamico dai drafts → più pulito senza Qt Designer XML. Pattern allineato con altri `gui/*.py` del progetto.

3. **Sidecar JSON `<graphml>.yed_overrides.json`**: load al `__init__` del wizard (preload widgets), save on Finish (`QWizard.accept()` override). Schema versionato (`"version": 1`). Forward-compat: ClassificationKind values unrecognized (es. da future s3dgraphy releases) skippati silently.

4. **Branch hook in `graph_ingestor.py`**: probe `QApplication.instance()` → se presente apre il wizard, else fall-through ai defaults yE-D. CLI/tests/headless calls non vedono mai la dialog. Defensive ImportError catch su qgis.PyQt + pyarchinit.gui.yed_import_dialog.

5. **CLI `--overrides PATH`** in `scripts/import_yed_graphml.py`: carica YedOverrides da JSON e passa a `import_yed_raw(overrides=...)`. Use case: CI/scripted re-runs con overrides riproducibili.

**i18n**: tutte le stringhe visibili in `self.tr(...)`. Il progetto ha file `.ts` monolitici per 10 lingue in `i18n/`; le nuove stringhe saranno auto-estratte al prossimo `pyside6-lupdate`. No file `.ts` dedicato per il dialog.

**Test**: 14 totali aggiunti (6 L0 `apply_overrides_to_drafts` + 5 L0 sidecar JSON + 2 L1 e2e classifier+folder_skip + 1 CLI `--overrides`). Suite: 338 → 352 passed, 42 skipped.

**AC-2 preservato**: pyarchinit-projected branch in `graph_ingestor.populate_list()` byte-identical (le modifiche sono tutte nella yEd-raw branch).

**Manual gate**: aprire QGIS → import yEd-raw graphml via menu → wizard apre → walk 5 pagine → Finish/Cancel → verify DB.

**Out of scope**: persistence multi-file (sidecar è per-graphml), drag-reorder dei rows, undo/redo within wizard (Cancel discards, Finish commits).

**Versioning**: minor bump `5.8.1 → 5.8.2-alpha`. yE-Closure shifta a `5.8.3-alpha`. Predecessor: `s3dgraphy-bump-5.8.1-alpha` (commit `7f5f82a8`, pushato).

### English

**yE-E Dialog UX — Qt wizard 5-page user-overrides for yEd-raw import.**

Fifth of the 6 yEd-aware-graphml-import rollout milestones. yE-D ships hardcoded defaults; yE-E adds a Qt wizard that opens BEFORE commit, letting the user review + override classifier kinds, periods, folder dimensions, and rapporti policy.

Components: **YedOverrides** dataclass + `apply_overrides_to_drafts` pure helper + `import_yed_raw(overrides=None)` parameter (yE-D regression preserved); **YedImportDialog** QWizard with 5 pages (programmatic, no .ui XML); sidecar JSON `<graphml>.yed_overrides.json` persistence; **branch hook** in `graph_ingestor.py` probes QApplication and opens the wizard when alive; **CLI** gets `--overrides PATH` flag for scripted runs.

i18n: all visible strings tr()-wrapped; auto-merged at next pyside6-lupdate. AC-2 preserved. 14 new tests. 338 → 352 passed, 42 skipped.

Versioning: minor bump `5.8.1 → 5.8.2-alpha`. yE-Closure shifts to `5.8.3-alpha`. Predecessor: `s3dgraphy-bump-5.8.1-alpha`.

---

## [5.8.1-alpha] - 2026-05-13

### Italiano

**s3dgraphy-bump — vendoring 0.1.41 → 0.1.42 + integrazione RSF (Reused Special Find).**

Emanuel ha rilasciato `s3dgraphy 0.1.42` su PyPI il 2026-05-10. Cambiamenti principali:

1. **RSF (Reused Special Find)** — nuovo tipo stratigrafico per "spolia" (elementi architettonici/decorativi riutilizzati). Famiglia `real`, `is_series=false`. Visual: ottagono, bordo rosso `#9B3333`, fill bianco. Origine: DP-26, ultimo Development Project prima di EM 1.5 cut. Classe Python `ReusedSpecialFind` in `stratigraphic_node.py`, registrato in `STRATIGRAPHIC_CLASS_MAP`, datamodel JSON, visual rules, palette template.
2. **`serUSD` export dispatch fixed** — la classe esisteva già ma l'exporter routava silently allo stencil default. Chiusa l'asimmetria export/import.
3. **Export refactor — semantic dispatch** — `node_registry.py` (+162/-31): selezione palette per regex sul `<y:NodeLabel>` invece di dispatch posizionale per id GraphML. Robusto a riordini palette in yEd.
4. **`S3DgraphyPaletteWarning`** — nuovo simbolo pubblico (subclass di `UserWarning`) emesso su label non riconosciuto o palette mancante stencil canonical. Backfill da defaults hardcoded.

**Vendor copia** in `ext_libs/s3dgraphy/`: 9 file production aggiornati (`__init__.py` con version `0.1.42`, `JSON_config/em_visual_rules.json`, `JSON_config/s3Dgraphy_node_datamodel.json`, `exporter/graphml/node_generator.py`, `exporter/graphml/node_registry.py`, `nodes/__init__.py`, `nodes/stratigraphic_node.py`, `templates/em_palette_template.graphml`, `utils/utils.py`).

**AC-2 byte-identical PRESERVATO**: `test_ai03_export_byte_identical.py` verde senza alcuna baseline regenerata. Emanuel ha mantenuto la promessa "round-trip identity preserved for all existing fixtures" — il refactor semantico produce output equivalente byte-by-byte.

**Integrazione RSF in pyarchinit**:
- `yed_classifier.py`: aggiunto `REUSED_SPECIAL_FIND` a `ClassificationKind` enum (13 valori totali) + regola regex `^RSF\d+` in `DEFAULT_CLASSIFIER_RULES` (posizionata tra VSF e SF).
- `yed_import_pipeline.py`: aggiunto `REUSED_SPECIAL_FIND` a `_SQL_US_KINDS` (RSF va in us_table come gli altri US-family, decisione utente "è unità tipo, va in us_table") + entry `REUSED_SPECIAL_FIND: "RSF"` in `_CLASSIFIED_KIND_TO_UNITA_TIPO`.
- `graph_ingestor.py`: aggiunto `"ReusedSpecialFind": "RSF"` a `_S3DGRAPHY_TYPE_TO_UNITA_TIPO` (round-trip recovery per graphml exportati con la nuova classe s3dgraphy).
- `gui/ui/US_USM.ui`: nuovo `<item><string>RSF</string></item>` in `comboBox_unita_tipo` (visible nel form US/USM).

**Smoke E2E**: import graphml con `RSF42` + `US01` + `SF99` + edge `RSF42→US01` → DB risultante: 2 righe us_table (`US01` unita_tipo='US', `RSF42` unita_tipo='RSF') + 1 riga inventario_materiali (`SF99`) + rapporto risolto correttamente con label (non yed_id).

**Test**: 2 nuovi L0 in `tests/sync/test_yed_classifier.py::test_classify_reused_special_find` + `tests/sync/test_yed_import_pipeline.py::test_classify_destination_routes_rsf_to_us_table`. Suite: 336 → 338 passed, 42 skipped. AC-2 verde.

**Cleanup `ext_libs/` stale dist-info** (commit `34f94215`): l'utente ha segnalato che `ext_libs/s3dgraphy-0.1.40.dist-info`, `0.1.41.dist-info` e `0.1.42.dist-info` coesistevano side-by-side dopo upgrade ripetuti. `importlib.metadata.version("s3dgraphy")` ritornava la prima alfabetica (`0.1.40`) invece di quella attiva, e file rimossi tra versioni restavano on-disk venendo importati. Fix: `modules_installer.py` ora pre-cleanup `<pkg>-*.dist-info/` dirs + `__pycache__/` per ogni package in `requirements.txt` prima del `pip install --upgrade`. Logica wheel-name-normalised (lowercase + underscore→dash), idempotente, robusta a `ext_libs/` assente. Applica a tutti i package, non solo s3dgraphy.

**Versioning**: minor bump `5.8.0 → 5.8.1-alpha`. yE-E shifta a `5.8.2-alpha`, yE-Closure a `5.8.3-alpha`. Predecessor: `yed-import-pipeline-5.8.0-alpha` (commit `bfd9c858`, pushato).

### English

**s3dgraphy-bump — vendoring 0.1.41 → 0.1.42 + RSF integration.**

Emanuel released `s3dgraphy 0.1.42` on PyPI 2026-05-10. Key changes: **RSF (Reused Special Find)** new stratigraphic node type for spolia (re-used architectural/decorative elements, family=real non-series, octagon shape #9B3333 border); **serUSD export dispatch** fixed (class existed but exporter silently fell back to default); **export refactor — semantic dispatch** in `node_registry.py` (regex on `<y:NodeLabel>` instead of GraphML-id positional, robust to palette reordering in yEd); **`S3DgraphyPaletteWarning`** new public warning class.

Vendor copy: 9 production files updated in `ext_libs/s3dgraphy/` (full version `0.1.42`). **AC-2 byte-identical PRESERVED** — `test_ai03_export_byte_identical.py` green without regenerating baselines.

RSF integration in pyarchinit:
- `yed_classifier.py`: new `REUSED_SPECIAL_FIND` ClassificationKind + `^RSF\d+` regex rule.
- `yed_import_pipeline.py`: RSF routed to `_SQL_US_KINDS` (us_table) with `unita_tipo='RSF'` per user decision ("è unità tipo, va in us_table").
- `graph_ingestor.py`: `"ReusedSpecialFind": "RSF"` added to `_S3DGRAPHY_TYPE_TO_UNITA_TIPO`.
- `gui/ui/US_USM.ui`: new `<item><string>RSF</string></item>` in `comboBox_unita_tipo`.

Smoke E2E: RSF42 + US01 + SF99 graphml → 2 us_table rows (US01 'US' + RSF42 'RSF') + 1 inventario row (SF99) + rapporto correctly resolved to label.

2 new L0 tests. Suite: 336 → 338 passed, 42 skipped. AC-2 green.

Versioning: minor bump `5.8.0 → 5.8.1-alpha`. yE-E shifts to `5.8.2-alpha`, yE-Closure to `5.8.3-alpha`. Predecessor: `yed-import-pipeline-5.8.0-alpha` (commit `bfd9c858`, pushed).

---

## [5.8.0-alpha] - 2026-05-13

### Italiano

**Fix post-Group-D (commit `cafde15b`)** — feedback utente sul primo smoke test in QGIS:

1. **USV* in `us_table`**: `_classify_destination` ora instrada `USV_VIRTUAL` + `USV_FORMAL` in `sql_us` (erano in paradata). Le unità stratigrafiche virtuali sono "unità tipo" come le altre US e vanno nello stesso table con `unita_tipo` dedicato (`USV`, `USVs`, `USVn`, `USVc`). Solo DOC/COMB/PROP/VIRTUAL_FIND restano paradata. Helper `_resolve_unita_tipo()` deriva il valore corretto: USV_VIRTUAL→`USV`, USV_FORMAL→prefisso 4 caratteri del label.
2. **Rapporti target = us label, non yed_id**: `_write_rapporti` ora riceve `id_to_label` (yed_id → us label) e produce tuple `[type, sito, area, us_label]` con il label leggibile (`"US02"`, `"USV101"`), NON l'id interno graphml (`"n0::n4::n12"` come prima). Rapporti il cui target non è in us_table (paradata, inventario) sono dropped con debug log — pyarchinit non li join'erebbe comunque.

Smoke E2E su EM_demo_02.graphml (CLI):
- us_table: **12 righe** (4 US + 8 USV) — era 4
- rapporti corretti con label reali — era yed_id
- attivita VA01..VA06 applicato a tutte e 12 — era applicato a 4
- inv_mat 2 + periodi 2 invariati

5 test L1 aggiornati per riflettere il comportamento corretto. Suite invariata: 336 passed / 42 skipped.

---

**yE-D Pipeline — primo milestone con DB write dal branch yEd-raw.**

Quarto dei 6 milestone della rollout yEd-aware-graphml-import. Dopo yE-A (foundation), yE-B (classifier), yE-C (parsers), yE-D è la prima milestone che effettivamente **scrive nel database** dalla branch yEd-raw del dispatcher. Importare `EM_demo_02.graphml` (o qualsiasi file yEd-raw) ora produce `us_table` + `inventario_materiali_table` + `periodizzazione_table` + paradata popolati correttamente, invece del comportamento buggato pre-yE-D dove cadeva nel legacy path e produceva 17 righe distorte in `us_table`.

**Architettura — 4 commit groups subagent-driven**:

1. `feat(yE-D): folder-edge policy module with 4 active policies` (commit `b90138f8`) — `modules/s3dgraphy/sync/yed_rapporti_policy.py` (~376 LOC) con `FolderEdgePolicy` StrEnum + 3 dataclass + `analyze_edges()` + `apply_policy()`. 4 policy attive: SKIP (default), FAN_OUT (espansione N×M), REPRESENTATIVE (primo membro proxy), SYNTHETIC (us virtuale VA per folder, rapporti rewired). Filtro universale per self-loop folder edges. 7 L0 tests.

2. `feat(yE-D): import_yed_raw orchestrator + 5 write functions + paradata` (commit `9f053264`) — `modules/s3dgraphy/sync/yed_import_pipeline.py` (~510 LOC). `import_yed_raw(handle, graphml_path, sito, drafts, *, policy=SKIP, dry_run=False)` orchestra single-transaction `engine.begin()` (PG+SQLite via DbHandle). 5 write functions: `_write_us_rows` (assegna `uuid7()` node_uuid), `_write_inventario_rows`, `_write_periodizzazione_rows` (no dates), `_apply_yed_folder_dimensions` (UPDATE us_table.<dim> con allowlist column-name per safety), `_write_rapporti` (UPDATE rapporti JSON + INSERT synthetic VA rows). `_write_paradata_via_store` dispatcha a ParadataStore (Path B per PropertyNode: no US linkage in yE-D, yE-E userà dialog). `_DryRunRollback` sentinel pattern ereditato da PG-C. 8 L0 tests.

3. `feat(yE-D): branch hook dispatch + VA vocab + 7 L1 integration tests` (commit `cab0d243`) — `graph_ingestor.py:166-216` rewritten: detection yEd-raw + costruzione drafts + dispatch a `import_yed_raw()` + RETURN IngestResult. Legacy `_run()` NON eseguito per yEd-raw. Pyarchinit-projected branch UNCHANGED (AC-2 byte-identical sacro). Defensive try/except fallback al legacy solo per exception inattese in detection/parsing (NON sul normal error return di `import_yed_raw`). Vocab patch in 2 punti: `graph_ingestor.py:1375` (`"VirtualActivity": "VA"` in `_S3DGRAPHY_TYPE_TO_UNITA_TIPO`) + `gui/ui/US_USM.ui:42716` (nuovo `<item><string>VA</string></item>` in `comboBox_unita_tipo`). 7 L1 integration tests su `em_demo_02_mini.graphml` (4 policy E2E + paradata writes + dry_run rollback + idempotency).

4. `feat(yE-D): cli scripts/import_yed_graphml.py + 2 cli tests` — `scripts/import_yed_graphml.py` (~150 LOC) argparse CLI per batch/CI: positional graphml + `--site` + `--db`/`--conn-str` mutex + `--policy` choice + `--dry-run` + `-v` verbose. 2 CLI tests (argparse smoke + subprocess dry-run E2E).

**Test count progression**: 312 (baseline post media-fk-migration) → 319 (Group A) → 327 (Group B) → 334 (Group C) → 336 (Group D). +24 tests totali. PG-L1 5 skipped offline (psycopg2 assente).

**Plan-time decisions risolte**:
- PropertyNode linkage: **Path B** (standalone, no US linkage al yE-D-time) — yE-E dialog assegnerà target.
- Vocab whitelist source: **pure code edits** (UI XML + ingestor dict map). Nessun JSON file né DB CHECK constraint esistono.
- DbHandle: **sì** per tutte le 5 write functions (pattern PG-C `engine.begin()`).
- No hooks readiness: **α** (defaults hardcoded in yE-D; yE-E rewires aggiungendo `overrides: YedOverrides | None = None` parameter).

**AC-2**: pyarchinit-projected branch in `graph_ingestor.populate_list()` byte-identical. Verifica: `test_ai03_export_byte_identical` + `test_graph_ingestor` + `test_cli_helper` tutti verdi (25/25 critical regression). `test_cli_helper.py::_project_to_graphml` ha richiesto una correzione minore (chiamata aggiuntiva a `_embed_pyarchinit_data_keys` per produrre graphml con marker keys che rotteano l'export del raw s3dgraphy — il test esercita il legacy path, non yE-D).

**Versioning**: minor bump `5.7.9.3 → 5.8.0-alpha`. Predecessor: `media-fk-migration-5.7.9.3-alpha` (commit `0919f5ce`). Successor: `yE-E Dialog → 5.8.1-alpha`, `yE-Closure → 5.8.2-alpha`.

### English

**yE-D Pipeline — first milestone with DB writes from the yEd-raw branch.**

Fourth of the 6 yEd-aware-graphml-import rollout milestones. After yE-A (foundation), yE-B (classifier), yE-C (parsers), yE-D is the first milestone that actually **writes to the database** from the yEd-raw branch of the dispatcher. Importing `EM_demo_02.graphml` (or any yEd-raw file) now produces correctly populated `us_table` + `inventario_materiali_table` + `periodizzazione_table` + paradata, instead of the pre-yE-D buggy behaviour where it fell through to the legacy path and produced 17 distorted rows in `us_table`.

**Architecture — 4 subagent-driven commit groups**:

1. `feat(yE-D): folder-edge policy module with 4 active policies` (commit `b90138f8`) — `modules/s3dgraphy/sync/yed_rapporti_policy.py` (~376 LOC) with `FolderEdgePolicy` StrEnum + 3 dataclasses + `analyze_edges()` + `apply_policy()`. 4 active policies: SKIP (default), FAN_OUT (N×M expansion), REPRESENTATIVE (first-member proxy), SYNTHETIC (virtual VA us per folder, rapporti rewired). Universal filter for self-loop folder edges. 7 L0 tests.

2. `feat(yE-D): import_yed_raw orchestrator + 5 write functions + paradata` (commit `9f053264`) — `modules/s3dgraphy/sync/yed_import_pipeline.py` (~510 LOC). `import_yed_raw(handle, graphml_path, sito, drafts, *, policy=SKIP, dry_run=False)` orchestrates a single-transaction `engine.begin()` (PG+SQLite via DbHandle). 5 write functions: `_write_us_rows` (assigns `uuid7()` node_uuid), `_write_inventario_rows`, `_write_periodizzazione_rows` (no dates), `_apply_yed_folder_dimensions` (UPDATE us_table.<dim> with column-name allowlist for safety), `_write_rapporti` (UPDATE rapporti JSON + INSERT synthetic VA rows). `_write_paradata_via_store` dispatches to ParadataStore (Path B for PropertyNode: no US linkage in yE-D, yE-E will use dialog). `_DryRunRollback` sentinel pattern inherited from PG-C. 8 L0 tests.

3. `feat(yE-D): branch hook dispatch + VA vocab + 7 L1 integration tests` (commit `cab0d243`) — `graph_ingestor.py:166-216` rewritten: yEd-raw detection + drafts build + dispatch to `import_yed_raw()` + RETURN IngestResult. Legacy `_run()` NOT executed for yEd-raw. Pyarchinit-projected branch UNCHANGED (AC-2 byte-identical sacred). Defensive try/except falls back to legacy ONLY on unexpected detection/parsing exceptions (NOT on `import_yed_raw`'s normal error return). Vocab patch in 2 spots: `graph_ingestor.py:1375` (`"VirtualActivity": "VA"` in `_S3DGRAPHY_TYPE_TO_UNITA_TIPO`) + `gui/ui/US_USM.ui:42716` (new `<item><string>VA</string></item>` in `comboBox_unita_tipo`). 7 L1 integration tests on `em_demo_02_mini.graphml` (4 policy E2E + paradata writes + dry_run rollback + idempotency).

4. `feat(yE-D): cli scripts/import_yed_graphml.py + 2 cli tests` — `scripts/import_yed_graphml.py` (~150 LOC) argparse CLI for batch/CI: positional graphml + `--site` + `--db`/`--conn-str` mutex + `--policy` choice + `--dry-run` + `-v` verbose. 2 CLI tests (argparse smoke + subprocess dry-run E2E).

**Test count progression**: 312 (baseline post media-fk-migration) → 319 (Group A) → 327 (Group B) → 334 (Group C) → 336 (Group D). +24 tests total. PG-L1 5 skipped offline (psycopg2 absent).

**Plan-time decisions resolved**:
- PropertyNode linkage: **Path B** (standalone, no US linkage at yE-D time) — yE-E dialog will assign target.
- Vocab whitelist source: **pure code edits** (UI XML + ingestor dict map). No JSON file or DB CHECK constraint exists.
- DbHandle: **yes** for all 5 write functions (PG-C `engine.begin()` pattern).
- No hooks readiness: **α** (defaults hardcoded in yE-D; yE-E rewires by adding `overrides: YedOverrides | None = None` parameter).

**AC-2**: pyarchinit-projected branch in `graph_ingestor.populate_list()` byte-identical. Verification: `test_ai03_export_byte_identical` + `test_graph_ingestor` + `test_cli_helper` all green (25/25 critical regression). `test_cli_helper.py::_project_to_graphml` needed a minor correction (extra `_embed_pyarchinit_data_keys` call to produce a graphml with marker keys — without it the raw s3dgraphy export got misclassified as yEd-raw under the new dispatch; the test exercises the legacy path, not yE-D).

**Versioning**: minor bump `5.7.9.3 → 5.8.0-alpha`. Predecessor: `media-fk-migration-5.7.9.3-alpha` (commit `0919f5ce`). Successor: `yE-E Dialog → 5.8.1-alpha`, `yE-Closure → 5.8.2-alpha`.

---

## [5.7.9.3-alpha] - 2026-05-13

### Italiano

**media-fk-migration — i killer trigger del media_thumb_table sono stati sostituiti con FK ON DELETE CASCADE.**

L'utente ha segnalato 2026-05-13 pomeriggio che il database `khutm2` aveva perso ~5156 righe in `media_table` e ~5758 in `media_to_entity_table`. Investigazione live ha rivelato due trigger plpgsql su `media_thumb_table` con check tautologico `IF OLD.id_media != OLD.id_media THEN ... ELSE DELETE FROM media_table ...` — la condizione è SEMPRE falsa (valore confrontato con sé stesso), quindi il ramo ELSE (cascade DELETE) si attivava su ogni UPDATE/DELETE di un thumb, cancellando in cascata `media_table` + `media_to_entity_table`. Recupero su khutm2 da `bk20260513.backup` via additive `INSERT ... ON CONFLICT DO NOTHING`. Trigger droppati e FK ON DELETE CASCADE installate nella direzione corretta (master → derivati).

**Universalità del bug**: gli stessi trigger sono nei file schema `pyarchinit_schema_clean.sql` (linee 3548-3627) + `pyarchinit_schema_updated.sql` (3524-3603) — quindi presenti in **ogni** installazione PG di pyarchinit. SQLite ha una versione attenuata (solo `AFTER DELETE`, no `UPDATE`, no MTE trigger) presente nei template binari `pyarchinit.sqlite` + `pyarchinit_db.sqlite`.

**Fix shipped**:

1. **Schema PG aggiornati** (file `pyarchinit_schema_clean.sql` + `pyarchinit_schema_updated.sql`): rimossi i 2 trigger killer + le 2 funzioni + i 2 DO `$$ ... $$` block che li installano. Aggiunte 2 `ALTER TABLE ... ADD CONSTRAINT FOREIGN KEY (id_media) REFERENCES media_table(id_media) ON DELETE CASCADE` per `media_thumb_table` e `media_to_entity_table`. Nuovi DB PG nascono puliti.

2. **Template SQLite ripuliti** in-place (`resources/dbfiles/pyarchinit.sqlite` 4297728→4289536 bytes, `pyarchinit_db.sqlite` 8997888→8975360 bytes via DROP TRIGGER + VACUUM). Nessuna FK retroattiva (limitazione SQLite — richiederebbe table-recreate; deferred). Nuove installazioni SQLite non subiscono il trigger killer.

3. **Migration library** `scripts/migrations/_2026_05_media_fk_cascade_lib.py` + **CLI** `scripts/migrations/2026_05_media_fk_cascade.py` per i DB PG **esistenti** che ancora portano i trigger. API: `detect_killer_triggers`, `count_orphans`, `apply_migration(handle, dry_run=False)`, `verify_post_migration`. Idempotente. Ordine in single-transaction: DROP TRIGGER → DROP FUNCTION → DELETE orfani → ADD CONSTRAINT (l'ordine è obbligatorio — PG rifiuta FK con orfani). Dry-run via `_DryRunRollback` sentinel (pattern PG-C). CLI ha 3 modes mutex (`--detect`/`--dry-run`/`--apply`) + mutex `--db`/`--conn-str` (pattern PG-A node_uuid). `--apply` invoca `auto_backup_postgres` prima.

4. **Menu QGIS wire** in `pyarchinitPlugin.py` linee 2706-2713 (entry "Migrazioni → Fix trigger media (cascade pericoloso)") + handler `_run_media_fk_migration` linee 2900-3101 che fa: PG-only check → detect → count orphans + dialog preview → confirm → auto-backup → apply → verify → summary. Mirror del pattern `_run_uuid_backfill_migration`.

**Test**: 13 totali nel file `tests/migrations/test_media_fk_migration.py` (4 L0 schema PG + 2 L0 lib/CLI + 2 L1 SQLite template + 5 L1 PG fixture). Suite: 304 → 312 passed offline (PG-L1 skipped per assenza psycopg2) / 317 online expected. `tests/migrations/test_media_fk_migration.py` da solo: 8 passed, 5 skipped.

**Out of scope**: SQLite existing DB migration (FK retrofit invasivo, danno minore — deferred); audit altri DB PG (festos2025, pyarchinit_v2 — non raggiungibili dalla rete dev oggi); riscrittura "rename propagator" trigger con `NEW != OLD` corretto (utilità marginale, `id_media` è sequence-driven PK).

**Versioning**: patch `5.7.9.2 → 5.7.9.3-alpha`. NESSUNO shift su yE-D (`5.8.0-alpha`), yE-E, yE-Closure. Predecessor: `pg-bv2-hotfix-5.7.9.2-alpha` (commit `c26e7763`).

### English

**media-fk-migration — killer triggers on media_thumb_table replaced with FK ON DELETE CASCADE.**

User-reported 2026-05-13 afternoon: production DB `khutm2` had lost ~5156 rows in `media_table` and ~5758 in `media_to_entity_table`. Live investigation revealed two plpgsql triggers on `media_thumb_table` with the tautology check `IF OLD.id_media != OLD.id_media THEN ... ELSE DELETE FROM media_table ...` — the condition is ALWAYS false (value compared to itself), so the ELSE branch (cascade DELETE) fired on every UPDATE/DELETE of a thumb, cascade-deleting `media_table` + `media_to_entity_table`. Recovered on khutm2 from `bk20260513.backup` via additive `INSERT ... ON CONFLICT DO NOTHING`. Triggers dropped and FK ON DELETE CASCADE installed in the natural direction (master → derived).

**Universal bug**: the same triggers are in schema files `pyarchinit_schema_clean.sql` (lines 3548-3627) + `pyarchinit_schema_updated.sql` (3524-3603) — so present in **every** pyarchinit PG installation. SQLite has a milder version (only `AFTER DELETE`, no `UPDATE`, no MTE trigger) in the binary templates `pyarchinit.sqlite` + `pyarchinit_db.sqlite`.

**Fix shipped**:

1. **PG schemas updated** (`pyarchinit_schema_clean.sql` + `pyarchinit_schema_updated.sql`): killer triggers + 2 functions + 2 DO `$$ ... $$` install blocks removed. Two `ALTER TABLE ... ADD CONSTRAINT FOREIGN KEY (id_media) REFERENCES media_table(id_media) ON DELETE CASCADE` added for `media_thumb_table` and `media_to_entity_table`. New PG DBs are born clean.

2. **SQLite templates cleaned** in-place (`resources/dbfiles/pyarchinit.sqlite` 4297728→4289536 bytes, `pyarchinit_db.sqlite` 8997888→8975360 bytes via DROP TRIGGER + VACUUM). No retroactive FK (SQLite limitation — would require table recreate; deferred). New SQLite installations don't carry the killer trigger.

3. **Migration library** `scripts/migrations/_2026_05_media_fk_cascade_lib.py` + **CLI** `scripts/migrations/2026_05_media_fk_cascade.py` for **existing** PG DBs that still carry the triggers. API: `detect_killer_triggers`, `count_orphans`, `apply_migration(handle, dry_run=False)`, `verify_post_migration`. Idempotent. Single-transaction order: DROP TRIGGER → DROP FUNCTION → DELETE orphans → ADD CONSTRAINT (order mandatory — PG rejects FK with orphans). Dry-run via `_DryRunRollback` sentinel (PG-C pattern). CLI has 3 mutex modes (`--detect`/`--dry-run`/`--apply`) + `--db`/`--conn-str` mutex (PG-A node_uuid pattern). `--apply` invokes `auto_backup_postgres` first.

4. **QGIS menu wire** in `pyarchinitPlugin.py` lines 2706-2713 (entry "Migrazioni → Fix trigger media (cascade pericoloso)") + handler `_run_media_fk_migration` lines 2900-3101: PG-only check → detect → count orphans + preview dialog → confirm → auto-backup → apply → verify → summary. Mirror of `_run_uuid_backfill_migration` pattern.

**Tests**: 13 total in `tests/migrations/test_media_fk_migration.py` (4 L0 PG schema + 2 L0 lib/CLI + 2 L1 SQLite template + 5 L1 PG fixture). Suite: 304 → 312 passed offline (PG-L1 skipped — psycopg2 absent) / 317 online expected. Module alone: 8 passed, 5 skipped.

**Out of scope**: SQLite existing DB migration (FK retrofit invasive, smaller damage — deferred); audit of other PG DBs (festos2025, pyarchinit_v2 — unreachable from dev network today); rewrite of "rename propagator" trigger with correct `NEW != OLD` (marginal utility — `id_media` is sequence-driven PK).

**Versioning**: patch `5.7.9.2 → 5.7.9.3-alpha`. NO shift on yE-D (`5.8.0-alpha`), yE-E, yE-Closure. Predecessor: `pg-bv2-hotfix-5.7.9.2-alpha` (commit `c26e7763`).

---

## [5.7.9.2-alpha] - 2026-05-13

### Italiano

**pg-bv2-hotfix — esportazione GraphML rotta su SQLite dopo PG-Bv2.**

L'utente ha segnalato 2026-05-13 mattina: dopo il rilascio di `pg-bv2-5.7.9-alpha` (commit `97e2ec13`) l'export GraphML è rotto su SQLite con `TypeError: expected str, bytes or os.PathLike object, not Pyarchinit_db_management`. L'export di DOT/JSON/Phased JSON funziona — il problema è isolato a `populate_graph` nel branch SQLite.

**Root cause**: PG-Bv2 ha aggiornato `s3dgraphy_dot_bridge.py:195` a passare `self.db_manager` (un `Pyarchinit_db_management`) come `db_path` invece di un `Path`. Il branch SQLite di `GraphProjector.populate_graph` in `modules/s3dgraphy/sync/graph_projector.py:183` faceva ancora `Path(db_path)` direttamente sull'istanza DbManager → TypeError. Stessa cosa alla riga 212 con `str(db_path)` passato come `filepath` al `PyArchInitImporter` upstream.

**Fix** (`graph_projector.py:182-201`): nel branch `not handle.is_postgres`, deriva `sqlite_path` da `handle.sqlite_path` (già estratto da `DbHandle.from_engine` — funziona per Path, str conn-string, Engine, DbManager). Fallback a `Path(db_path)` solo quando `db_path` è già `str|Path` (callers legacy). `PyArchInitImporter(filepath=str(sqlite_path))` invece di `str(db_path)`.

**Test regressione**: `test_populate_graph_accepts_db_manager_on_sqlite` in `tests/sync/test_graph_projector.py` — `FakeDbManager(conn_str + engine)` puntato al fixture `mini_volterra.sqlite` → `populate_graph(mgr, sito=...)` deve produrre grafo non vuoto. Pre-fix solleva `TypeError`, post-fix passa.

**Backward-compat preservata**: callers che passano `Path` direttamente continuano a funzionare via la branch fallback. AC-2 (export byte-identical) preservato — solo derivazione path, nessun cambio nel pipeline downstream.

**Test count**: 303 → 304 passed, 37 skipped. +1 L0 regressione mirata.

**Versioning**: patch increment `5.7.9.1 → 5.7.9.2-alpha`. NESSUNO shift su yE-D (`5.8.0-alpha`), yE-E, yE-Closure. Predecessor: `pg-media-fix-5.7.9.1-alpha` (commit `f8bdfc0e`, locale).

### English

**pg-bv2-hotfix — GraphML export broken on SQLite after PG-Bv2.**

User-reported 2026-05-13 morning: after `pg-bv2-5.7.9-alpha` (commit `97e2ec13`) shipped, GraphML export is broken on SQLite with `TypeError: expected str, bytes or os.PathLike object, not Pyarchinit_db_management`. DOT/JSON/Phased JSON exports still work — issue is isolated to `populate_graph` SQLite branch.

**Root cause**: PG-Bv2 updated `s3dgraphy_dot_bridge.py:195` to pass `self.db_manager` (a `Pyarchinit_db_management`) as `db_path` instead of a `Path`. The SQLite branch of `GraphProjector.populate_graph` at `modules/s3dgraphy/sync/graph_projector.py:183` still did `Path(db_path)` directly on the DbManager instance → TypeError. Same at line 212 where `str(db_path)` was passed as `filepath` to the upstream `PyArchInitImporter`.

**Fix** (`graph_projector.py:182-201`): in the `not handle.is_postgres` branch, derive `sqlite_path` from `handle.sqlite_path` (already extracted by `DbHandle.from_engine` — works for Path, str conn-string, Engine, DbManager). Fall back to `Path(db_path)` only when `db_path` is already `str|Path` (legacy callers). `PyArchInitImporter(filepath=str(sqlite_path))` instead of `str(db_path)`.

**Regression test**: `test_populate_graph_accepts_db_manager_on_sqlite` in `tests/sync/test_graph_projector.py` — `FakeDbManager(conn_str + engine)` pointing at the `mini_volterra.sqlite` fixture → `populate_graph(mgr, sito=...)` must produce a non-empty graph. Pre-fix raises `TypeError`, post-fix passes.

**Backward-compat preserved**: callers passing `Path` directly still work via the fallback branch. AC-2 (byte-identical export) preserved — only path derivation changed, no downstream pipeline change.

**Test count**: 303 → 304 passed, 37 skipped. +1 targeted regression L0.

**Versioning**: patch increment `5.7.9.1 → 5.7.9.2-alpha`. NO shift on yE-D (`5.8.0-alpha`), yE-E, yE-Closure. Predecessor: `pg-media-fix-5.7.9.1-alpha` (commit `f8bdfc0e`, local).

---

## [5.7.9.1-alpha] - 2026-05-12

### Italiano

**pg-media-fix — bottone "Carica Media" non funzionante su PostgreSQL.**

L'utente ha segnalato 2026-05-12 sera: il bottone "Carica Media" nei form **US**, **Pottery**, **Struttura**, **Tafonomia**, **Inventario Materiali** non fa nulla quando cliccato su un progetto PostgreSQL. Il Media Manager invece funziona.

**Root cause**: `Pyarchinit_db_management.query_bool()` in `modules/db/pyarchinit_db_manager.py` riceve dai form handler una `search_dict` con pattern legacy `{'id_entity': "'42'", 'entity_type': "'US'"}`. Il metodo strippa le virgolette esterne ma lascia il valore come stringa `'42'`. La colonna `MEDIATOENTITY.id_entity` è `BIGINT` su PG (Integer nell'entity SQLAlchemy). PostgreSQL è strict sui tipi: `BIGINT = 'text'` ritorna silently zero righe. SQLite è type-loose e coerce automaticamente — bug invisibile su SQLite, manifesto su PG. Il handler `loadMediaPreview()` (es. `tabs/US_USM.py:18707`) ha `if not record_us_list: return` → silent exit → bottone "non fa nulla".

**Fix**: aggiunto in `query_bool` (linea ~2908) un blocco di coercion che ispeziona `column.type.python_type`. Se la colonna è numerica (int/float) e il valore è stringa, coerce con `col_pytype(value)`. Sicuro con try/except per `NotImplementedError, ValueError, AttributeError`. ~10 LOC.

**Universale**: il fix opera a runtime sulla declaration SQLAlchemy dell'entity, NON sullo schema DB fisico. Funziona su:
- Nuovi DB PG (id_entity BIGINT) → coerce string→int → match ✓
- Vecchi DB PG (es. khutm2) → stessa coerce → match ✓
- SQLite (nuovo o vecchio) → coerce è no-op behaviour-wise (era loose-comparison prima, ora int-comparison) → nessuna regressione

Nessuna migrazione DB richiesta.

**Test**: 4 nuovi L0 in `tests/migrations/test_pg_media_fix.py`:
1. `test_query_bool_has_numeric_coercion_block` — source-inspection guard (lettura filesystem perché modulo importa QGIS)
2. `test_query_bool_coerces_string_to_int_for_integer_column` — end-to-end con SQLite + Integer column + insert+query, verifica match esatto
3. `test_query_bool_coercion_safe_for_non_numeric_column` — coerce NON deve toccare String columns
4. `test_query_bool_coercion_resilient_to_garbage_input` — input non-numerico (`'abc'`) per colonna Integer → coercion solleva ValueError → except preserva valore originale → no crash

**Test count**: 298 → 302 passed, 37 skipped (PG offline). +4 L0 sempre verdi.

**Versioning**: patch increment `5.7.9 → 5.7.9.1-alpha`. NESSUNO shift su yE-D (resta `5.8.0-alpha`), yE-E, yE-Closure. Predecessor: `pg-bv2-5.7.9-alpha` (commit `97e2ec13`, pushato).

### English

**pg-media-fix — "Carica Media" button does nothing on PostgreSQL.**

User-reported 2026-05-12 evening: the "Carica Media" button in **US**, **Pottery**, **Struttura**, **Tafonomia**, **Inventario Materiali** forms does nothing when clicked on a PostgreSQL project. Media Manager works fine.

**Root cause**: `Pyarchinit_db_management.query_bool()` in `modules/db/pyarchinit_db_manager.py` receives from form handlers a `search_dict` with legacy pattern `{'id_entity': "'42'", 'entity_type': "'US'"}`. The method strips outer quotes but leaves the value as string `'42'`. The `MEDIATOENTITY.id_entity` column is `BIGINT` on PG (Integer in the SQLAlchemy entity). PostgreSQL is strict on types: `BIGINT = 'text'` silently returns zero rows. SQLite is type-loose and auto-coerces — bug invisible on SQLite, manifest on PG. The handler `loadMediaPreview()` (e.g. `tabs/US_USM.py:18707`) has `if not record_us_list: return` → silent exit → button "does nothing".

**Fix**: added in `query_bool` (line ~2908) a coercion block that inspects `column.type.python_type`. If the column is numeric (int/float) and the value is a string, coerce with `col_pytype(value)`. Safe via try/except for `NotImplementedError, ValueError, AttributeError`. ~10 LOC.

**Universal**: the fix operates at runtime on the SQLAlchemy entity declaration, NOT on the physical DB schema. Works on:
- New PG DBs (id_entity BIGINT) → coerce string→int → match ✓
- Legacy PG DBs (e.g. khutm2) → same coerce → match ✓
- SQLite (new or old) → coerce is behaviorally a no-op (was loose-comparison before, now int-comparison) → no regression

No DB migration required.

**Tests**: 4 new L0 in `tests/migrations/test_pg_media_fix.py`:
1. `test_query_bool_has_numeric_coercion_block` — source-inspection guard (filesystem read because module imports QGIS)
2. `test_query_bool_coerces_string_to_int_for_integer_column` — end-to-end with SQLite + Integer column + insert+query, verifies exact match
3. `test_query_bool_coercion_safe_for_non_numeric_column` — coerce must NOT touch String columns
4. `test_query_bool_coercion_resilient_to_garbage_input` — non-numeric input (`'abc'`) for Integer column → coercion raises ValueError → except preserves original value → no crash

**Test count**: 298 → 302 passed, 37 skipped (PG offline). +4 L0 always-green.

**Versioning**: patch increment `5.7.9 → 5.7.9.1-alpha`. NO shift on yE-D (stays `5.8.0-alpha`), yE-E, yE-Closure. Predecessor: `pg-bv2-5.7.9-alpha` (commit `97e2ec13`, pushed).

---

## [5.7.9-alpha] - 2026-05-12

### Italiano

**PG-Bv2 — GraphML export su PostgreSQL backend.**

Chiude il gap PG lasciato aperto da PG-B (`phase3-pgcompat-b-export-5.7.1-alpha`, 2026-05-10): l'export GraphML dal matrix viewer ora funziona end-to-end su DB PostgreSQL.

**Cosa shipa**:

- **NEW** `modules/s3dgraphy/sync/pyarchinit_pg_importer.py` (~120 LOC): nuova funzione `import_from_pg(handle, sito, mapping_name)` che sostituisce l'upstream `PyArchInitImporter` (SQLite-only) per il branch PG. Legge `us_table` via SQLAlchemy + costruisce `StratigraphicNode` + `PropertyNode` dal mapping `pyarchinit_us_mapping.json`. Approccio **α-narrow**: solo PG usa il nuovo reader, SQLite continua su upstream (preserva AC-2 byte-identical).
- **MODIFIED** `graph_projector.py:populate_graph()`: routing via `_resolve_db_handle` + branch `if handle.is_postgres: import_from_pg() else: PyArchInitImporter()`. I 5 helper a valle accettano già DbHandle (PG-B).
- **MODIFIED** `s3dgraphy_dot_bridge.py`: rimosso il branch `if db_path is None: skip` ripristinato dal revert PG-UIFix. Ora sicuro perché `populate_graph()` supporta PG end-to-end.
- **INVERTED** test `tests/sync/test_pg_uifix.py::test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2` → `test_graphml_export_runs_on_pg_backend` (asserisce assenza dei marker deferred-state).
- **NEW** `tests/sync/test_pg_bv2_pg_importer.py`: 2 L0 (mapping load + mock row build) + 2 L2 PG (end-to-end export + SQLite-vs-PG structural equivalence usando `pg_with_volterra`).

**Garanzie regressione (tutte verdi)**:
- AC-2 byte-identical (SQLite path invariato)
- 3 critical SQLite gates
- 8 PG-D L2 + 5 yE-A + 12 yE-B + 16 yE-C + 2 PG-UIFix L0 + 7 PG-UUIDFix tests

Test count: 298 passed, 37 skipped (PG offline) — +4 delta (2 L0 passed + 2 L2 added to skip; matches plan's 296→300 progression target with actual baseline of 298).

**Side-effect sulla rollout yEd-aware**:

- yE-D Pipeline: `yed-import-pipeline-5.7.9-alpha` → `yed-import-pipeline-5.8.0-alpha`
- yE-E Dialog: `yed-import-dialog-5.8.0-alpha` → `yed-import-dialog-5.8.1-alpha`
- yE-Closure: `yed-import-closure-5.8.1-alpha` → `yed-import-closure-5.8.2-alpha`

Spec yE-D aggiornato in commit separato.

### English

**PG-Bv2 — GraphML export on PostgreSQL backend.**

Closes the PG gap left by PG-B (`phase3-pgcompat-b-export-5.7.1-alpha`, 2026-05-10): graphml export from the matrix viewer now works end-to-end on PostgreSQL databases.

**What ships**:

- **NEW** `modules/s3dgraphy/sync/pyarchinit_pg_importer.py` (~120 LOC): new `import_from_pg(handle, sito, mapping_name)` function replacing the upstream SQLite-only `PyArchInitImporter` for the PG branch. Reads `us_table` via SQLAlchemy + builds `StratigraphicNode` + `PropertyNode` from `pyarchinit_us_mapping.json`. **α-narrow** approach: only PG uses the new reader, SQLite keeps upstream (preserves AC-2 byte-identical).
- **MODIFIED** `graph_projector.py:populate_graph()`: routes through `_resolve_db_handle` + branches `if handle.is_postgres: import_from_pg() else: PyArchInitImporter()`. The 5 downstream helpers already accept DbHandle (PG-B).
- **MODIFIED** `s3dgraphy_dot_bridge.py`: removed the `if db_path is None: skip` envelope restored by PG-UIFix revert. Safe now because `populate_graph()` supports PG end-to-end.
- **INVERTED** `tests/sync/test_pg_uifix.py::test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2` → `test_graphml_export_runs_on_pg_backend` (asserts deferred-state markers absent).
- **NEW** `tests/sync/test_pg_bv2_pg_importer.py`: 2 L0 (mapping load + mocked row build) + 2 L2 PG (end-to-end export + SQLite-vs-PG structural equivalence via `pg_with_volterra`).

**Regression guarantees (all green)**:
- AC-2 byte-identical (SQLite path untouched)
- 3 critical SQLite gates
- 8 PG-D L2 + 5 yE-A + 12 yE-B + 16 yE-C + 2 PG-UIFix L0 + 7 PG-UUIDFix tests

Test count: 298 passed, 37 skipped (PG offline) — +4 delta (2 L0 passed + 2 L2 added to skip; matches plan's 296→300 progression target with actual baseline of 298).

**Rollout cascade**:

- yE-D Pipeline: `yed-import-pipeline-5.7.9-alpha` → `yed-import-pipeline-5.8.0-alpha`
- yE-E Dialog: `yed-import-dialog-5.8.0-alpha` → `yed-import-dialog-5.8.1-alpha`
- yE-Closure: `yed-import-closure-5.8.1-alpha` → `yed-import-closure-5.8.2-alpha`

yE-D spec updated in separate commit.

---

## [5.7.8.1-alpha] - 2026-05-12

### Italiano

**PG-UUIDFix — hotfix patch sulla migrazione UUID per dump PG legacy.**

L'utente ha segnalato fallimento della migrazione UUID v7 su PG con dump `khutm2.sql`:

```
periodizzazione_table: no primary key declared on PostgreSQL — cannot backfill safely
```

**Root cause**: il backfill di PG-A (`phase3-pgcompat-a-migration-5.7.0-alpha`, 2026-05-10) ha un check difensivo che fallisce quando la tabella PG non ha `PRIMARY KEY` dichiarata. Il dump dell'utente è stato creato da uno schema pre-2018 (o template legacy) che non emette il vincolo, anche se lo schema SQLAlchemy di `Periodizzazione_table.py` lo dichiara correttamente. I 3 schema SQL ufficiali (`pyarchinit_schema_updated.sql`, `pyarchinit_schema_clean.sql`, `pyarchinit_update_postgres.sql`) hanno tutti i PK corretti — audit confermato. Solo DB esistenti come `khutm2.sql` sono affetti.

**Fix**: trasformato il check difensivo in **auto-fix**:

- `scripts/migrations/_2026_05_node_uuid_backfill_lib.py`: aggiunta mappa `_CANONICAL_PK` (`us_table → id_us`, `inventario_materiali_table → id_invmat`, `periodizzazione_table → id_perfas`). Quando PG ritorna 0 PK colonne per una tabella, il backfill ora: (1) verifica che la colonna canonica esista nello schema live, (2) controlla che non ci siano duplicati via `GROUP BY ... HAVING COUNT(*) > 1 LIMIT 5`, (3) esegue `ALTER TABLE ... ADD CONSTRAINT {table}_pkey PRIMARY KEY ({pk_col})` dentro lo stesso `engine.begin()`, (4) procede al backfill normale. Se duplicati: errore chiaro con sample degli ID conflittuali, no data corruption. Backup automatico di PG-A copre la transazione.

**Verifica utente pre-fix** (test3_graphml.sqlite SQLite, 34 righe in us_table): tutti i 34 UUID v7 erano stati assegnati correttamente. periodizzazione_table SQLite vuota → 0 UUID (idempotente). Confermato che SQLite path è OK; bug solo su PG legacy.

**Tests**: 4 nuovi test in `tests/migrations/test_node_uuid_backfill.py`:
1. `test_canonical_pk_mapping_covers_all_target_tables` (L0): mappa `_CANONICAL_PK` deve coprire ogni TABLES entry con convenzione `id_<short>`.
2. `test_backfill_auto_pk_source_inspection` (L0): source-inspection guard su `ADD CONSTRAINT` + `PRIMARY KEY` + `HAVING COUNT(*) > 1` + error fallback.
3. `test_backfill_pg_legacy_schema_auto_adds_pk` (L2 PG): crea tabella throwaway senza PK su live PG, runna backfill, verifica PK aggiunto + UUID assegnati. Skip clean se PG offline.
4. `test_backfill_pg_legacy_rejects_duplicate_ids` (L2 PG): tabella con `id_perfas` duplicati → `RuntimeError("duplicate values")`. Skip clean se PG offline.

**Schema files**: NON modificati. Audit confermato che tutti i 3 hanno già i `{table}_pkey` constraint sui 3 TABLES.

**Garanzie regressione (tutte verdi)**:
- AC-2 byte-identical
- 3 critical SQLite gates
- 8 PG-D L2 + 5 yE-A + 12 yE-B + 16 yE-C + 2 PG-UIFix L0 tests preservati

Test count: 291 → 293 passed, 35 skipped (PG offline +2 new L2 skip). 

**Versioning**: patch increment a `5.7.8.1-alpha`, NESSUNO shift su yE-D (resta `5.7.9-alpha`) né su PG-Bv2 (TBD). Predecessor: `pg-uifix-5.7.8-alpha` (commit `e35e137c`).

### English

**PG-UUIDFix — UUID migration hotfix for legacy PG dumps.**

User reported PG UUID v7 migration failure with `khutm2.sql` dump:

```
periodizzazione_table: no primary key declared on PostgreSQL — cannot backfill safely
```

**Root cause**: PG-A's backfill (`phase3-pgcompat-a-migration-5.7.0-alpha`, 2026-05-10) has a defensive check that fails when a PG table lacks a declared `PRIMARY KEY`. The user's dump was created from a pre-2018 schema (or legacy template) that doesn't emit the constraint, even though the SQLAlchemy structure at `Periodizzazione_table.py` declares it correctly. All 3 official schema SQL files (`pyarchinit_schema_updated.sql`, `pyarchinit_schema_clean.sql`, `pyarchinit_update_postgres.sql`) have correct PKs — audit confirmed. Only existing DBs like `khutm2.sql` are affected.

**Fix**: turned the defensive check into **auto-fix**:

- `scripts/migrations/_2026_05_node_uuid_backfill_lib.py`: added `_CANONICAL_PK` map (`us_table → id_us`, `inventario_materiali_table → id_invmat`, `periodizzazione_table → id_perfas`). When PG returns 0 PK columns for a table, backfill now: (1) verifies the canonical column exists in the live schema, (2) checks no duplicate values via `GROUP BY ... HAVING COUNT(*) > 1 LIMIT 5`, (3) runs `ALTER TABLE ... ADD CONSTRAINT {table}_pkey PRIMARY KEY ({pk_col})` inside the same `engine.begin()`, (4) proceeds to normal backfill. On duplicates: clear error with sample of conflicting IDs, no data corruption. PG-A's auto-backup covers the transaction.

**User pre-fix verification** (test3_graphml.sqlite SQLite, 34 us_table rows): all 34 UUID v7 had been assigned correctly. periodizzazione_table SQLite empty → 0 UUIDs (idempotent). Confirmed SQLite path is OK; bug only on legacy PG.

**Tests**: 4 new in `tests/migrations/test_node_uuid_backfill.py`:
1. `test_canonical_pk_mapping_covers_all_target_tables` (L0): `_CANONICAL_PK` must cover every TABLES entry with `id_<short>` convention.
2. `test_backfill_auto_pk_source_inspection` (L0): source-inspection guard on `ADD CONSTRAINT` + `PRIMARY KEY` + `HAVING COUNT(*) > 1` + error fallback.
3. `test_backfill_pg_legacy_schema_auto_adds_pk` (L2 PG): creates throwaway PK-less table on live PG, runs backfill, asserts PK added + UUIDs assigned. Skip clean when PG offline.
4. `test_backfill_pg_legacy_rejects_duplicate_ids` (L2 PG): table with duplicate `id_perfas` → `RuntimeError("duplicate values")`. Skip clean when PG offline.

**Schema files**: NOT modified. Audit confirmed all 3 already declare `{table}_pkey` constraint for the 3 TABLES.

**Regression guarantees (all green)**:
- AC-2 byte-identical
- 3 critical SQLite gates
- 8 PG-D L2 + 5 yE-A + 12 yE-B + 16 yE-C + 2 PG-UIFix L0 tests preserved

Test count: 291 → 293 passed, 35 skipped (PG offline, +2 new L2 skip).

**Versioning**: patch increment to `5.7.8.1-alpha`, NO shift on yE-D (stays `5.7.9-alpha`) or PG-Bv2 (TBD). Predecessor: `pg-uifix-5.7.8-alpha` (commit `e35e137c`).

---

## [5.7.8-alpha] - 2026-05-12

### Italiano

**PG-UIFix — hotfix milestone Phase 3 PG-compat UI (scope PARZIALE).**

Rimuove i guards SQLite-only obsoleti in `gui/dialog_paradata_manager.py` (Bug 1, SHIPPATO) e i 2 import-flow guards in `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (parte di Bug 2 SHIPPATA). **Bug 2 graphml export DEFERITO a milestone PG-Bv2** dopo che il test utente ha rivelato che PG-B (5.7.1-alpha) non aveva completato il supporto PG per `populate_graph()`.

**Bug fixati (SHIPPATO):**

- **Bug 1** (Paradata manager + Group manager + US picker bloccati su PG): tre guards `"requires a SQLite-backed pyarchinit project"` rimossi da `dialog_paradata_manager.py`. `_store()` e `_group_store()` passano `db_manager` direttamente a `ParadataStore` / `GroupStore` (shim `_resolve_db_handle` da PG-D accetta `Path | DbHandle | str`). US picker RISCRITTO con SQLAlchemy via engine del `db_manager` (era raw `sqlite3.connect`, SQLite-only).
- **Bug 2 (parziale — Import-flow guards)**: rimossi 2 guards `"Import requires a SQLite-backed pyarchinit project"` da `s3dgraphy_dot_bridge.py:742 + 830` (ingest path, non export). `GraphIngestor.populate_list` accetta `db_manager` via `_resolve_db_handle` dal PG-C (5.7.2-alpha).

**Bug DEFERITI:**

- **Bug 2 (graphml export su PG)**: **DEFERITO a milestone PG-Bv2**. Causa: test utente su raw PG ha sollevato `TypeError: expected str, bytes or os.PathLike object, not Pyarchinit_db_management`. Root cause: PG-B (commit `3a2597ab`, 2026-05-10) aveva flippato 5 helper SQL in `modules/s3dgraphy/sync/graph_projector.py` (siti 303, 367, 509, 761, 877) ma aveva mancato l'orchestratore `populate_graph()` stesso: linea 165 fa `Path(db_path)` incondizionale + linea 190 chiama `PyArchInitImporter(filepath=str(db_path))` — l'importer upstream in `ext_libs/s3dgraphy/importer/pyarchinit_importer.py` usa `sqlite3` direttamente ed accetta solo path filesystem. Fix proprio richiede ~80 LOC (o sostituzione importer con reader SQLAlchemy + costruzione manuale `StratigraphicNode`, o wrapper temp-SQLite roundtrip). Scope-creep evitato — fix originale revertito, branch `if db_path is None: skip` ripristinato con messaggio onesto: `"GraphML export on PostgreSQL backend is not yet supported: pending PG-Bv2 milestone (upstream PyArchInitImporter is SQLite-only). DOT and JSON exports are unaffected."`
- **Bug 3** (media non caricati nei form US/Pottery/Artefact su PG): **DEFERITO** a milestone separato post-diagnosi (root cause sconosciuta, serve error logs dall'utente). Workaround: Media Manager funziona.

**Test:** 2 test L0 in `tests/sync/test_pg_uifix.py` (entrambi passano):
1. `test_paradata_manager_does_not_block_on_pg_handle` (Bug 1) — asserisce assenza dei 3 guard SQLite-only obsoleti.
2. `test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2` (Bug 2 deferred-state pin) — asserisce **presenza** del messaggio `"pending PG-Bv2 milestone"` e del nuovo status `"postgresql backend deferred to PG-Bv2"`. Documenta che quando PG-Bv2 shippa, il test va cancellato e l'asserzione originale `no_skip_branch` ripristinata.

**Side-effect sulla rollout**: PG-UIFix riserva il tag `pg-uifix-5.7.8-alpha`. yE-D shifta da `yed-import-pipeline-5.7.8-alpha` (era pianificato) a `yed-import-pipeline-5.7.9-alpha`. yE-E e yE-Closure shifano corrispondentemente. **Nuovo milestone PG-Bv2** aperto come follow-up (no version reserved yet — orderable post yE-Closure o prima su richiesta utente).

**Lezione**: PG-B (5.7.1-alpha) aveva dichiarato "graphml export su PG supportato" basato sulla flippatura di 5 helper SQL, ma `populate_graph()` non era mai stato testato end-to-end su raw PG (i test L2 PG-D coprono paradata/group store, non export pipeline). PG-Bv2 chiuderà il gap.

**Garanzie regressione (tutte verdi post-PG-UIFix):**
- AC-2 byte-identical
- 3 critical SQLite gates
- 5 yE-A + 12 yE-B + 16 yE-C + 8 PG-D L2 preservati

Test count: 289 → 291 passed, 33 skipped (PG offline) — 2 PG-UIFix L0 tests aggiunti, count finale invariato dopo revert (test Bug 2 invertito, non rimosso).

### English

**PG-UIFix — Phase 3 PG-compat UI hotfix milestone (PARTIAL scope).**

Removes obsolete SQLite-only guards in `gui/dialog_paradata_manager.py` (Bug 1, SHIPPED) and the 2 import-flow guards in `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (part of Bug 2, SHIPPED). **Bug 2 graphml export DEFERRED to PG-Bv2 milestone** after user testing revealed that PG-B (5.7.1-alpha) had not completed PG support for `populate_graph()`.

**Bugs fixed (SHIPPED):**

- **Bug 1** (Paradata manager + Group manager + US picker blocked on PG): three `"requires a SQLite-backed pyarchinit project"` guards removed from `dialog_paradata_manager.py`. `_store()` and `_group_store()` now pass `db_manager` directly to `ParadataStore` / `GroupStore` (`_resolve_db_handle` shim from PG-D accepts `Path | DbHandle | str`). US picker REWRITTEN with SQLAlchemy via `db_manager` engine (was raw `sqlite3.connect`, SQLite-only).
- **Bug 2 (partial — Import-flow guards)**: removed 2 `"Import requires a SQLite-backed pyarchinit project"` guards from `s3dgraphy_dot_bridge.py:742 + 830` (ingest path, not export). `GraphIngestor.populate_list` accepts `db_manager` via `_resolve_db_handle` since PG-C (5.7.2-alpha).

**Bugs DEFERRED:**

- **Bug 2 (graphml export on PG)**: **DEFERRED to PG-Bv2 milestone**. Cause: user testing on raw PG raised `TypeError: expected str, bytes or os.PathLike object, not Pyarchinit_db_management`. Root cause: PG-B (commit `3a2597ab`, 2026-05-10) had flipped 5 SQL helpers in `modules/s3dgraphy/sync/graph_projector.py` (sites 303, 367, 509, 761, 877) but missed the orchestrator `populate_graph()` itself: line 165 does unconditional `Path(db_path)` + line 190 calls `PyArchInitImporter(filepath=str(db_path))` — the upstream importer in `ext_libs/s3dgraphy/importer/pyarchinit_importer.py` uses `sqlite3` directly and accepts only filesystem paths. Proper fix requires ~80 LOC (either replace the importer with a SQLAlchemy-based reader that constructs `StratigraphicNode` objects manually, or wrap with a temp-SQLite roundtrip). Scope-creep avoided — original fix reverted, `if db_path is None: skip` branch restored with honest message: `"GraphML export on PostgreSQL backend is not yet supported: pending PG-Bv2 milestone (upstream PyArchInitImporter is SQLite-only). DOT and JSON exports are unaffected."`
- **Bug 3** (media not loading in US/Pottery/Artefact forms on PG): **DEFERRED** to separate milestone post-diagnosis (root cause unknown, needs user-provided error logs). Workaround: Media Manager works.

**Tests:** 2 L0 tests in `tests/sync/test_pg_uifix.py` (both pass):
1. `test_paradata_manager_does_not_block_on_pg_handle` (Bug 1) — asserts absence of the 3 obsolete SQLite-only guards.
2. `test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2` (Bug 2 deferred-state pin) — asserts **presence** of the `"pending PG-Bv2 milestone"` message and the new status `"postgresql backend deferred to PG-Bv2"`. Documents that when PG-Bv2 ships, this test must be deleted and the original `no_skip_branch` assertion restored.

**Rollout side-effect**: PG-UIFix reserves tag `pg-uifix-5.7.8-alpha`. yE-D shifts from `yed-import-pipeline-5.7.8-alpha` (originally planned) to `yed-import-pipeline-5.7.9-alpha`. yE-E and yE-Closure shift correspondingly. **New PG-Bv2 milestone** opened as follow-up (no version reserved yet — orderable post yE-Closure or earlier on user demand).

**Lesson**: PG-B (5.7.1-alpha) claimed "graphml export on PG supported" based on flipping 5 SQL helpers, but `populate_graph()` was never tested end-to-end on raw PG (PG-D L2 tests cover paradata/group store, not the export pipeline). PG-Bv2 will close the gap.

**Regression guarantees (all green post-PG-UIFix):**
- AC-2 byte-identical
- 3 critical SQLite gates
- 5 yE-A + 12 yE-B + 16 yE-C + 8 PG-D L2 preserved

Test count: 289 → 291 passed, 33 skipped (PG offline) — 2 PG-UIFix L0 tests added, final count unchanged after revert (Bug 2 test inverted, not removed).

---

## [5.7.7-alpha] - 2026-05-12

### Italiano

**yE-C Parsers — terzo milestone del feature yEd-aware graphml import.**

Aggiunge due parser standalone (`yed_table_parser.py` + `yed_group_walker.py`) wirati nel branch hook esistente. All'import di un file yEd-raw, il log ora mostra una sintesi a 3 righe: classifier counts + periods detected + group folders detected. Più il nuovo field `IngestResult.parsed_drafts: dict | None` per forward-compat con il pipeline yE-D.

Esempio su EM_demo_02.graphml (82 leaf, 6 folder, 2 periods):
```
yEd-raw graphml detected at <path>.
  Classified 82 leaves: combiner: 3, document: 38, property: 25, ...
  Detected 2 periods: Period01, Contemporary era.
  Detected 6 group folders: VA01 (attivita, N members), ...
  Yed-aware import path not yet wired (yE-C parsers only).
  Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_table_parser.py`**: estrae yEd TableNode swimlane → list[PeriodCandidate]. 10 field (yed_row_id, auto_label, user_label, 1-based auto_periodo, auto_fase=1, user_periodo/fase, member_yed_ids da Y-coord, y_min/y_max). Leaf nell'header area (Y < primo row.y_min) esclusi dalla membership. datazione_iniziale/finale restano NULL (yEd non encoda date) — l'utente compila dopo nel tab pyarchinit Periodizzazione.
- **NEW `modules/s3dgraphy/sync/yed_group_walker.py`**: descende yfiles.foldertype="group" hierarchy → list[FolderCandidate]. 10 field (yed_id, full_label, auto/user_dimension, auto/user_value, member_yed_ids direct only, nested_folder_ids, parent_folder_id, extra_attrs). `DEFAULT_FOLDER_PREFIX_MAP` con 7 pattern (VA→attivita, AR→area, ST→struttura, SE→settore, AM→ambient, SG→saggio, QP→quad_par). Auto-value extracts prefix via regex `^([A-Z]+\d+)`; description tail va in `extra_attrs["description"]`. Top-level TableNode swimlane recursed-into per nested folders ma NON registrato. Cycle detection riusa `CycleDetectedError` esistente.
- **NEW field `IngestResult.parsed_drafts: dict | None = None`** in `ingest_result.py`. Default None preserva back-compat. Shape: `{"classified": [...], "periods": [...], "folders": [...]}`. yE-D consumerà questo per le DB writes.
- **MODIFY `graph_ingestor.py:169-196`**: branch hook yE-B aggiornato per orchestrare classify + extract_periods + walk_folders + 3-line summary log. Local var `_yed_parsed_drafts` inizializzata a None; popolata se yEd-raw detectato. Threaded come kwarg a `_run()` (il vero construction site di `IngestResult(...)`). Passata come `parsed_drafts=_yed_parsed_drafts` a construction time — mutation post-construction è vietata perché `IngestResult` è `frozen=True`.
- **NEW 13 test L0** + **3 test L1**: per-parser + cross-parser consistency check su `em_demo_02_mini.graphml`.

**Correzione architetturale durante esecuzione**: lo spec §7 diceva "attach to result before final return" — non possibile (`IngestResult` è frozen). Plan corretto a "pass `parsed_drafts=` a construction". Durante l'esecuzione l'implementer ha scoperto che il vero construction site è dentro `_run()` (helper privato chiamato da `populate_list()`), non `populate_list()` stesso. Fix: threaded `_yed_parsed_drafts` come kwarg a `_run()`. Soluzione più pulita.

**Eredita dal parent spec §6 + §7** specializzato per MVP:
- Input Path-only (NON Graph union)
- TableNode swimlane escluso da walk_folders
- DEFAULT_FOLDER_PREFIX_MAP è l'unico ruleset; override dialog deferito a yE-E

**Garanzie regressione (tutte verdi post-yE-C):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A + 12 yE-B preservati
- 8 PG-D L2 (skip puliti offline)

Test count: 273 → 289 passed, 33 skipped (PG offline) o 281 → 297 passed, 12 skipped (PG online + psycopg2).

### English

**yE-C Parsers — third milestone of the yEd-aware graphml import feature.**

Adds two standalone parsers (`yed_table_parser.py` + `yed_group_walker.py`) wired into the existing branch hook. On import of a yEd-raw file, the log now shows a 3-line summary: classifier counts + periods detected + group folders detected. Plus the new `IngestResult.parsed_drafts: dict | None` field for forward-compat with the yE-D pipeline.

Example on EM_demo_02.graphml (82 leaves, 6 folders, 2 periods):
```
yEd-raw graphml detected at <path>.
  Classified 82 leaves: combiner: 3, document: 38, property: 25, ...
  Detected 2 periods: Period01, Contemporary era.
  Detected 6 group folders: VA01 (attivita, N members), ...
  Yed-aware import path not yet wired (yE-C parsers only).
  Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_table_parser.py`**: extracts yEd TableNode swimlane → list[PeriodCandidate]. 10 fields (yed_row_id, auto_label, user_label, 1-based auto_periodo, auto_fase=1, user counterparts, member_yed_ids by Y-coord, y_min/y_max). Leaves in the header area (Y < first row.y_min) excluded from membership. datazione_iniziale/finale stay NULL (yEd doesn't encode dates) — user fills later in pyarchinit Periodizzazione tab.
- **NEW `modules/s3dgraphy/sync/yed_group_walker.py`**: descends yfiles.foldertype="group" hierarchy → list[FolderCandidate]. 10 fields (yed_id, full_label, auto/user_dimension, auto/user_value, member_yed_ids direct only, nested_folder_ids, parent_folder_id, extra_attrs). `DEFAULT_FOLDER_PREFIX_MAP` with 7 patterns (VA→attivita, AR→area, ST→struttura, SE→settore, AM→ambient, SG→saggio, QP→quad_par). Auto-value extracts prefix via regex `^([A-Z]+\d+)`; description tail goes to `extra_attrs["description"]`. Top-level TableNode swimlane recursed-into for nested folders but NOT recorded. Cycle detection reuses existing `CycleDetectedError`.
- **NEW field `IngestResult.parsed_drafts: dict | None = None`** in `ingest_result.py`. Default None preserves back-compat. Shape: `{"classified": [...], "periods": [...], "folders": [...]}`. yE-D will consume this for DB writes.
- **MODIFY `graph_ingestor.py:169-196`**: yE-B branch hook updated to orchestrate classify + extract_periods + walk_folders + 3-line summary log. Local var `_yed_parsed_drafts` initialized to None; populated if yEd-raw detected. Threaded as kwarg to `_run()` (the actual `IngestResult(...)` construction site). Passed as `parsed_drafts=_yed_parsed_drafts` at construction time — mutation after construction is forbidden because `IngestResult` is `frozen=True`.
- **NEW 13 L0 tests** + **3 L1 tests**: per-parser + cross-parser consistency check on `em_demo_02_mini.graphml`.

**Architectural correction during execution**: spec §7 said "attach to result before final return" — not possible (`IngestResult` is frozen). Plan corrected to "pass `parsed_drafts=` at construction". During execution the implementer discovered the actual construction site is inside `_run()` (private helper called from `populate_list()`), not `populate_list()` itself. Fix: threaded `_yed_parsed_drafts` as a kwarg to `_run()`. Cleaner solution.

**Inherits parent spec §6 + §7** specialized for MVP:
- Input is Path-only (NOT Graph union)
- TableNode swimlane excluded from walk_folders
- DEFAULT_FOLDER_PREFIX_MAP is the only ruleset; dialog override deferred to yE-E

**Regression guarantees (all green post-yE-C):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A + 12 yE-B preserved
- 8 PG-D L2 (skip cleanly offline)

Test count: 273 → 289 passed, 33 skipped (PG offline) or 281 → 297 passed, 12 skipped (PG online + psycopg2).

---

## [5.7.6-alpha] - 2026-05-12

### Italiano

**yE-B Classifier — secondo milestone del feature yEd-aware graphml import.**

Aggiunge il classifier label-prefix per i leaf node dei graphml yEd-raw + wiring nel branch hook esistente (introdotto in yE-A). All'import di un file yEd-raw, il log ora mostra una sintesi della classificazione (esempio su EM_demo_02.graphml, 82 leaf):

```
yEd-raw graphml detected at <path>. Classified 82 leaves:
  combiner: 3, document: 38, property: 25, special_find: 2,
  us_real: 4, usv_virtual: 8, virtual_find: 2.
Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_classifier.py`**: helper `classify_leaves(graphml_path)` con enum `ClassificationKind` (12 valori: US_REAL, US_MASONRY, US_DOCUMENTARY, USV_VIRTUAL, USV_FORMAL, SPECIAL_FIND, VIRTUAL_FIND, DOCUMENT, COMBINER, PROPERTY, UNKNOWN, SKIP), regex map `DEFAULT_CLASSIFIER_RULES` (10 pattern order-sensitive — USV* prima di US*, USM* prima di US*, USD* prima di US*, VSF* prima di SF*), e dataclass `ClassifiedNode`.
- **Esclusione folder**: i nodi con `yfiles.foldertype="group"` NON vengono classificati — quelli sono territorio di yE-C `yed_group_walker`.
- **Sicurezza**: parse error / file mancante → lista vuota (safe default, fall-through al path legacy preservato).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py:169-196`**: il bare warning di yE-A viene sostituito con invocazione di `classify_leaves()` + summary `Counter` nel log. Outer `try/except Exception: pass` di yE-A preservato (classifier errors non possono rompere il path legacy). Import lazy preservati.
- **NEW 11 test L0** in `tests/sync/test_yed_classifier.py`: ordering prefix, case insensitivity, unknown fallback, document order, USV_FORMAL bare/numbered semantics, `rules=` override mechanism.
- **NEW 1 test L1** in `tests/sync/test_yed_classifier_integration.py`: integration su `em_demo_02_mini.graphml` (fixture yE-A) — verifica count breakdown e esclusione folder.

**Polish durante l'esecuzione**: il code quality reviewer ha catturato un bug a livello spec carried into the plan: il pattern `^USVs\b|^USVn\b` non matchava label reali come `USVs01` o `USVn05` perché `\b` richiede una transizione word→non-word, ma `s→0`/`n→0` è word→word. Corretto a `^USVs\d*$|^USVn\d*$` che matcha sia bare che numbered forms.

**Eredita dal parent spec** (`docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` §5) ma specializza:
- Input è Path-only (NON union `Graph | Path | str`) — consistenza con `yed_detector.detect_flavor`
- DEFAULT_CLASSIFIER_RULES è l'unico ruleset shippato; override utente via dialog deferito a yE-E

**Garanzie regressione (tutte verdi post-yE-B):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A detector tests
- 8 PG-D L2 (skip puliti offline)

Test count: 261 → 273 passed, 33 skipped (PG offline) o 269 → 281 passed, 12 skipped (PG online + psycopg2).

### English

**yE-B Classifier — second milestone of the yEd-aware graphml import feature.**

Adds the label-prefix classifier for yEd-raw graphml leaf nodes + wiring into the existing branch hook (introduced in yE-A). On import of a yEd-raw file, the log now shows a classification summary (example on EM_demo_02.graphml, 82 leaves):

```
yEd-raw graphml detected at <path>. Classified 82 leaves:
  combiner: 3, document: 38, property: 25, special_find: 2,
  us_real: 4, usv_virtual: 8, virtual_find: 2.
Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_classifier.py`**: helper `classify_leaves(graphml_path)` with `ClassificationKind` enum (12 values: US_REAL, US_MASONRY, US_DOCUMENTARY, USV_VIRTUAL, USV_FORMAL, SPECIAL_FIND, VIRTUAL_FIND, DOCUMENT, COMBINER, PROPERTY, UNKNOWN, SKIP), `DEFAULT_CLASSIFIER_RULES` regex map (10 order-sensitive patterns — USV* before US*, USM* before US*, USD* before US*, VSF* before SF*), and `ClassifiedNode` dataclass.
- **Folder exclusion**: nodes with `yfiles.foldertype="group"` are NOT classified — those are yE-C `yed_group_walker` territory.
- **Safety**: parse error / missing file → empty list (safe default, legacy path fall-through preserved).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py:169-196`**: the yE-A bare warning is replaced with `classify_leaves()` invocation + `Counter` summary log. The yE-A outer `try/except Exception: pass` is preserved (classifier errors cannot break the legacy path). Lazy imports preserved.
- **NEW 11 L0 tests** in `tests/sync/test_yed_classifier.py`: prefix ordering, case insensitivity, unknown fallback, document order, USV_FORMAL bare/numbered semantics, `rules=` override mechanism.
- **NEW 1 L1 test** in `tests/sync/test_yed_classifier_integration.py`: integration on `em_demo_02_mini.graphml` (yE-A fixture) — verifies count breakdown and folder exclusion.

**Polish during execution**: code quality reviewer caught a spec-level bug carried into the plan: the `^USVs\b|^USVn\b` pattern didn't match real-world labels like `USVs01` or `USVn05` because `\b` requires a word→non-word transition, but `s→0`/`n→0` is word→word. Fixed to `^USVs\d*$|^USVn\d*$` which matches both bare and numbered forms.

**Inherits parent spec** (`docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` §5) but specializes:
- Input is Path-only (NOT `Graph | Path | str` union) — consistency with `yed_detector.detect_flavor`
- DEFAULT_CLASSIFIER_RULES is the only ruleset shipped; user override via dialog deferred to yE-E

**Regression guarantees (all green post-yE-B):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A detector tests
- 8 PG-D L2 (skip cleanly offline)

Test count: 261 → 273 passed, 33 skipped (PG offline) or 269 → 281 passed, 12 skipped (PG online + psycopg2).

---

## [5.7.5-alpha] - 2026-05-12

### Italiano

**yE-A Foundation — primo milestone del feature yEd-aware graphml import.**

Apre la rollout in 6 milestone della feature di import yEd-raw (graphml authored in yEd da team archeologici esterni, senza data keys `pyarchinit.*`). yE-A shippa **solo la detection** + un hook no-op nel codice ingestor: nessun cambiamento visibile per l'utente, ma la fondazione per le milestone successive (yE-B Classifier → yE-C Parsers → yE-D Pipeline → yE-E Dialog → yE-Closure).

- **NEW `modules/s3dgraphy/sync/yed_detector.py`**: helper `detect_flavor(graphml_path) -> "pyarchinit-projected" | "yed-raw"`. Header scan O(1) via `lxml.etree.iterparse` (con fallback `xml.etree`), stop al primo `<graph>` element. Default sicuro `"yed-raw"` su file vuoto / malformato / mancante (la pipeline a valle in yE-B+ gestisce il problema).
- **Detection marker**: presenza di QUALSIASI `pyarchinit.<*>` key in top-level `<key>` declarations (NON specificamente `pyarchinit.node_uuid` come scritto nello spec — quella key è emessa condizionalmente, il namespace prefix è il marker robusto, confermato da evidenza sui fixture esistenti).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py`**: aggiunto un if-branch di 21 righe al top di `populate_list()`. Quando rileva yEd-raw, emette un warning log + cade attraverso al path esistente (no-op placeholder). yE-B+ sostituirà il no-op con dispatch reale a `yed_import_pipeline.import_yed_raw()`.
- **NEW fixture `tests/sync/fixtures/em_demo_02_mini.graphml`**: yEd-raw minimale (~108 righe XML, ~4 KB) con 1 TableNode con 2 row Period01/Period02, 2 group folder (VA01 attivita + AR01 area), 6 leaf (2 US + 1 USV + 1 SF + 1 VSF + 1 PropertyNode), 5 edge (2 leaf-to-leaf + 1 folder-to-leaf + 1 leaf-to-folder + 1 folder-to-folder). Sarà riusato in yE-B/C/D/E.
- **NEW 5 test L0** in `tests/sync/test_yed_detector.py`: detection corretta su baseline AC-2 + fixture nuova + malformed XML + file vuoto + file mancante.

**Garanzie regressione (tutte verde post-yE-A):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates (`test_round_trip_with_paradata`, `test_round_trip_with_groups`, `test_graph_projector_paradata`)
- 8 PG-D L2 (skip cleanly offline, pass online)
- Pipeline pyarchinit-projected esistente: invariata byte-by-byte

Test count: 256 → 261 passed, 33 skipped (PG offline) o 269 passed, 12 skipped (PG online + psycopg2).

### English

**yE-A Foundation — first milestone of the yEd-aware graphml import feature.**

Opens the 6-milestone rollout of the yEd-raw graphml import feature (graphmls authored in yEd by external archaeological teams, without `pyarchinit.*` data keys). yE-A ships **detection only** + a no-op hook in the ingestor code: no user-visible behavior change, but the foundation for subsequent milestones (yE-B Classifier → yE-C Parsers → yE-D Pipeline → yE-E Dialog → yE-Closure).

- **NEW `modules/s3dgraphy/sync/yed_detector.py`**: helper `detect_flavor(graphml_path) -> "pyarchinit-projected" | "yed-raw"`. O(1) header scan via `lxml.etree.iterparse` (with `xml.etree` fallback), stops at first `<graph>` element. Safe default `"yed-raw"` on empty / malformed / missing file (the downstream pipeline in yE-B+ surfaces the issue).
- **Detection marker**: presence of ANY `pyarchinit.<*>` key in top-level `<key>` declarations (NOT specifically `pyarchinit.node_uuid` as the spec said — that key is conditionally emitted; the namespace prefix is the robust marker, confirmed by evidence on existing fixtures).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py`**: added a 21-line if-branch at the top of `populate_list()`. On yEd-raw detection, emits a warning log + falls through to the existing path (no-op placeholder). yE-B+ will replace the no-op with real dispatch to `yed_import_pipeline.import_yed_raw()`.
- **NEW fixture `tests/sync/fixtures/em_demo_02_mini.graphml`**: minimal yEd-raw (~108 XML lines, ~4 KB) with 1 TableNode + 2 rows Period01/Period02, 2 group folders (VA01 attivita + AR01 area), 6 leaves (2 US + 1 USV + 1 SF + 1 VSF + 1 PropertyNode), 5 edges (2 leaf-to-leaf + 1 folder-to-leaf + 1 leaf-to-folder + 1 folder-to-folder). Will be reused in yE-B/C/D/E.
- **NEW 5 L0 tests** in `tests/sync/test_yed_detector.py`: correct detection on AC-2 baseline + new fixture + malformed XML + empty file + missing file.

**Regression guarantees (all green post-yE-A):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates (`test_round_trip_with_paradata`, `test_round_trip_with_groups`, `test_graph_projector_paradata`)
- 8 PG-D L2 (skip cleanly offline, pass online)
- Existing pyarchinit-projected pipeline: byte-by-byte unchanged

Test count: 256 → 261 passed, 33 skipped (PG offline) or 269 passed, 12 skipped (PG online + psycopg2).

---

## [5.7.4-alpha] - 2026-05-11

### Italiano

**Consolidation — chiusura ufficiale di Phase 3.**

Sesto e ultimo milestone di Phase 3. Aggiunge l'override UI del workspace dir (deferito da PG-D Q1=b) e il docs pass di chiusura. Scope minimale (~310 LOC + polish) per chiudere la fase senza churn API.

- **`_resolve_workspace_root()` helper** in `modules/s3dgraphy/sync/_workspace.py`: 3-tier fallback chain.
  1. `PYARCHINIT_WORKSPACE_DIR` env var (priorità massima — utile per CI/test)
  2. QSettings `pyarchinit/paradata_workspace` (UI override persistente)
  3. Default `~/pyarchinit/pyarchinit_DB_folder/`
  Import QSettings lazy con try/except ImportError, instantiation runtime con try/except Exception. Non-Qt env (es. pytest) saltano trasparentemente il layer QSettings; Qt-installato-ma-no-QCoreApplication ricade defensivamente sul default.
- **`_resolve_workspace_dir()` PG branch** ora chiama il nuovo helper invece di hardcodare il default. SQLite branch INVARIATO (`handle.sqlite_path.parent`).
- **Sezione UI "Paradata Workspace"** in `gui/pyarchinitConfigDialog.py` (tab DB Sync). QLineEdit + Browse + Reset. Read/write QSettings con `sync()` defensivo. `editingFinished` signal sul QLineEdit persiste path digitati a mano. Persistente tra sessioni QGIS. NON influenza SQLite users (il loro path resta accanto al `.sqlite`).
- **6 test L0** in `tests/sync/test_workspace_root.py`: 4 test env-var/default (env precedence, default fallback, empty env skip-through, tilde expansion) + 2 test QSettings mock (success path + defensive runtime-error fall-through). Pure pytest, no Qt, no PG dependency.
- **Phase 3 closure summary** nel dev-log: tutti i 6 tag + statistiche cumulative + items deferred.

**Items deferred** (saranno gestiti in Phase 4 / 5.8.x):
- Rename `db_path` -> `db_input` su 5 API pubbliche con DeprecationWarning cycle
- Test parametrizzati SQLite + PG (low ROI — gli env PG-offline già skippano puliti)
- Adozione opzionale di `_conn_slug` in `_common.py:auto_backup_postgres`

**Phase 3 chiusura ufficiale**: 6 tag (Foundation + PG-A + PG-B + PG-C + PG-D + Consolidation), ~2500 LOC totali, ~36+ commit, AC-2 byte-identical preservato dall'inizio alla fine, zero residui `sqlite3.connect()` in `modules/s3dgraphy/sync/`. Phase 4 (SyncEngine + REST API) può essere brainstormata quando l'utente è pronto.

Test count: 250 -> 256 passed, 33 skipped (PG offline) o 264 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato.

### English

**Consolidation — official Phase 3 closure.**

Sixth and final Phase 3 milestone. Adds the deferred UI override for the workspace dir (from PG-D Q1=b) and the closure docs pass. Minimal scope (~310 LOC + polish) to close the phase without API churn.

- **`_resolve_workspace_root()` helper** in `modules/s3dgraphy/sync/_workspace.py`: 3-tier fallback chain.
  1. `PYARCHINIT_WORKSPACE_DIR` env var (highest priority — useful for CI/tests)
  2. QSettings `pyarchinit/paradata_workspace` (persistent UI override)
  3. Default `~/pyarchinit/pyarchinit_DB_folder/`
  QSettings import is lazy with try/except ImportError, instantiation runtime with try/except Exception. Non-Qt environments (e.g., pytest) skip the QSettings layer transparently; Qt-installed-but-no-QCoreApplication defensively falls through to the default.
- **`_resolve_workspace_dir()` PG branch** now calls the new helper instead of hardcoding the default. SQLite branch UNCHANGED (`handle.sqlite_path.parent`).
- **UI "Paradata Workspace" section** in `gui/pyarchinitConfigDialog.py` (DB Sync tab). QLineEdit + Browse + Reset. Read/write QSettings with defensive `sync()`. `editingFinished` signal on the QLineEdit persists manually-typed paths. Persists across QGIS sessions. Does NOT affect SQLite users (their path stays next to the `.sqlite`).
- **6 L0 tests** in `tests/sync/test_workspace_root.py`: 4 env-var/default tests (env precedence, default fallback, empty env skip-through, tilde expansion) + 2 QSettings mock tests (success path + defensive runtime-error fall-through). Pure pytest, no Qt, no PG dependency.
- **Phase 3 closure summary** in the dev-log: all 6 tags + cumulative stats + deferred items.

**Deferred items** (will be handled in Phase 4 / 5.8.x):
- Rename `db_path` -> `db_input` on 5 public APIs with DeprecationWarning cycle
- Parametrized SQLite + PG tests (low ROI — PG-offline environments already skip cleanly)
- Optional adoption of `_conn_slug` in `_common.py:auto_backup_postgres`

**Phase 3 official closure**: 6 tags (Foundation + PG-A + PG-B + PG-C + PG-D + Consolidation), ~2500 LOC total, ~36+ commits, AC-2 byte-identical preserved from start to finish, zero residual `sqlite3.connect()` in `modules/s3dgraphy/sync/`. Phase 4 (SyncEngine + REST API) can be brainstormed when the user is ready.

Test count: 250 -> 256 passed, 33 skipped (PG offline) or 264 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved.

---

## [5.7.3-alpha] - 2026-05-11

### Italiano

**PG-D — ParadataStore + GroupStore lavorano su PostgreSQL.**

Quarto e ultimo milestone "core" della Phase 3. Ribalta i due file system store (paradata + groups) sull'infrastruttura cross-backend. Tutti i 250 test SQLite di PG-C restano verdi via shim, INCLUSO i 3 critical gate (test_round_trip_with_paradata, test_round_trip_with_groups, test_graph_projector_paradata). AC-2 byte-identical preservato.

- **NEW `modules/s3dgraphy/sync/_workspace.py`**: helper module con `_resolve_workspace_dir(handle, sito) -> Path` e `_conn_slug(handle) -> str`. SQLite branch ritorna `handle.sqlite_path.parent` (byte-identical al comportamento pre-PG-D). PG branch ritorna `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/` con `mkdir(parents=True, exist_ok=True)`.
- **`_conn_slug`**: formula deterministica `slugify(f"{host}_{port}_{dbname}")` con regex `[^a-zA-Z0-9_-]` → `_`. Single source of truth per identificatori filesystem-safe basati su URL PG.
- **`paradata_store.py` + `group_store.py`**: constructor accetta `Path | DbHandle | str` via shim Foundation. Property `file_path` chiama `_resolve_workspace_dir` invece di `self._db_path.parent`. Filename pattern uniforme su entrambi i backend (`paradata_<sito>.graphml` / `groups_<sito>.graphml`).
- **Zero SQL refactor**: questi file non hanno query SQL. PG-D è il più piccolo milestone PG-X (~360 LOC vs PG-A/B/C ~470-660 LOC).
- **SQLite preservation**: i 15 caller esistenti (1 bridge, 2 graph_projector, 11 scripts/s3dgraphy_sync, 6 test) continuano a passare `Path` e funzionano invariati via shim. Comportamento file system byte-identical per SQLite users.
- **NO QSettings UI** (deferred to Consolidation 5.7.4 per Q1=b).
- **8 nuovi test L2 PG**: 4 in `test_paradata_store_pg.py` + 4 in `test_group_store_pg.py`. Tutti usano `monkeypatch` su `Path.home()` per non polluire il home dir reale. Skippano puliti quando PG offline o psycopg2 mancante.

**Phase 3 è ora completa modulo Consolidation 5.7.4-alpha** (rename `db_path → db_input` + QSettings UI + cleanup).

Test count: 250 → 250 passed, 33 skipped (PG offline) o 258 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato.

### English

**PG-D — ParadataStore + GroupStore work on PostgreSQL.**

Fourth and final "core" milestone of Phase 3. Flips the two filesystem stores (paradata + groups) onto the cross-backend infrastructure. All 250 PG-C SQLite tests stay green via shim, INCLUDING the 3 critical gates (test_round_trip_with_paradata, test_round_trip_with_groups, test_graph_projector_paradata). AC-2 byte-identical preserved.

- **NEW `modules/s3dgraphy/sync/_workspace.py`**: helper module with `_resolve_workspace_dir(handle, sito) -> Path` and `_conn_slug(handle) -> str`. SQLite branch returns `handle.sqlite_path.parent` (byte-identical to pre-PG-D behaviour). PG branch returns `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/` with `mkdir(parents=True, exist_ok=True)`.
- **`_conn_slug`**: deterministic formula `slugify(f"{host}_{port}_{dbname}")` with regex `[^a-zA-Z0-9_-]` → `_`. Single source of truth for filesystem-safe PG identifiers.
- **`paradata_store.py` + `group_store.py`**: constructor accepts `Path | DbHandle | str` via Foundation shim. `file_path` property calls `_resolve_workspace_dir` instead of `self._db_path.parent`. Filename pattern uniform across backends (`paradata_<sito>.graphml` / `groups_<sito>.graphml`).
- **Zero SQL refactor**: these files have no SQL queries. PG-D is the smallest PG-X milestone (~360 LOC vs PG-A/B/C ~470-660 LOC).
- **SQLite preservation**: the 15 existing callers (1 bridge, 2 graph_projector, 11 scripts/s3dgraphy_sync, 6 tests) continue to pass `Path` and work unchanged via shim. File-system behaviour byte-identical for SQLite users.
- **NO QSettings UI** (deferred to Consolidation 5.7.4 per Q1=b).
- **8 new L2 PG tests**: 4 in `test_paradata_store_pg.py` + 4 in `test_group_store_pg.py`. All use `monkeypatch` on `Path.home()` to avoid polluting the real home dir. Skip cleanly when PG offline or psycopg2 missing.

**Phase 3 is now complete modulo Consolidation 5.7.4-alpha** (rename `db_path → db_input` + QSettings UI + cleanup).

Test count: 250 → 250 passed, 33 skipped (PG offline) or 258 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved.

---

## [5.7.2-alpha] - 2026-05-11

### Italiano

**PG-C — Il pipeline di IMPORT ora funziona su PostgreSQL.**

Terzo milestone post-Foundation della Phase 3. Ribalta il pipeline di import (`GraphIngestor.populate_list`) sull'infrastruttura cross-backend. Tutti i 250 test SQLite di PG-B restano verdi via shim, INCLUSO il critical `test_round_trip.py` che esercita populate_list end-to-end su SQLite. AC-2 byte-identical preservato (PG-C non tocca export).

- **1 `sqlite3.connect()` sito swappato a `engine.begin()`**: il singolo punto di transazione atomica che wrappa l'intero `_run` body diventa `with handle.engine.begin() as conn:`. Semantica BEGIN/COMMIT/ROLLBACK identica su entrambi i backend.
- **~10 query interne tradotte**: SELECT COUNT/INSERT su site_table, SELECT */INSERT/UPDATE su us_table (loop di detection + write block, con `cur.description` → `result.keys()` per i nomi colonna), SELECT/INSERT su periodizzazione_table, 2 UPDATE in `_apply_group_folders_to_sql` (signature `cur` → `conn`). Tutte usano `text(":name")` con named params.
- **Public API senza breaking change**: `populate_list(graph, db_path, sito, ...)` mantiene il keyword `db_path` ma accetta `Path | DbHandle | str` via shim Foundation. Linea 152 `db_path = Path(db_path)` coercion **RIMOSSA** (avrebbe rotto i caller DbHandle — stessa trap catturata in PG-B Group C). Internal `_run(graph, handle, ...)` ricezione handle direttamente.
- **`_DryRunRollback` internal sentinel exception**: pattern necessario perché `engine.begin()` non ha "conditional rollback". In dry_run mode, alla fine del blocco `with` solleviamo `_DryRunRollback()` per forzare il rollback automatico del context manager, poi swallow l'eccezione fuori dal `with`. Preserva la semantica "dry_run = nessuna modifica DB" su entrambi i backend.
- **ConflictResolver verificato pure in-memory**: zero modifiche a `conflict_resolver.py`. Il policy GRAPH_WINS di AI04 funziona identicamente su PG.
- **`import sqlite3` rimosso da `graph_ingestor.py`**. Dopo PG-C, l'unico sqlite3 residuo in `modules/s3dgraphy/sync/` è in `paradata_store.py` / `group_store.py` (scope PG-D).
- **7 nuovi test L2 PG**: 6 in `test_ingest_pg.py` (DbHandle acceptance, dry_run rollback — il critical per `_DryRunRollback`, ConflictResolver, MissingEpochError, create_missing_epochs, atomic rollback su mock failure) + 1 round-trip identity in `test_round_trip_pg.py` (il gate del milestone). Tutti skippano puliti quando PG offline o psycopg2 mancante.

Test count: 250 → 250 passed, 25 skipped (PG offline) o 257 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato. SQLite round-trip preservato.

### English

**PG-C — Import pipeline now works on PostgreSQL.**

Third post-Foundation milestone of Phase 3. Flips the import pipeline (`GraphIngestor.populate_list`) onto the cross-backend infrastructure. All 250 PG-B SQLite tests stay green via shim, INCLUDING the critical `test_round_trip.py` that exercises populate_list end-to-end on SQLite. AC-2 byte-identical preserved (PG-C doesn't touch export).

- **1 `sqlite3.connect()` site swapped to `engine.begin()`**: the single atomic-transaction point wrapping the entire `_run` body becomes `with handle.engine.begin() as conn:`. BEGIN/COMMIT/ROLLBACK semantics identical on both backends.
- **~10 inner queries translated**: SELECT COUNT / INSERT on site_table, SELECT */INSERT/UPDATE on us_table (detection loop + write block, with `cur.description` → `result.keys()` for column names), SELECT/INSERT on periodizzazione_table, 2 UPDATEs in `_apply_group_folders_to_sql` (signature `cur` → `conn`). All use `text(":name")` with named params.
- **Public API zero-breaking-change**: `populate_list(graph, db_path, sito, ...)` keeps the `db_path` keyword but accepts `Path | DbHandle | str` via the Foundation shim. Line 152 `db_path = Path(db_path)` coercion **REMOVED** (would have broken DbHandle callers — same trap caught in PG-B Group C). Internal `_run(graph, handle, ...)` receives the handle directly.
- **`_DryRunRollback` internal sentinel exception**: pattern required because `engine.begin()` has no conditional rollback. In dry_run mode, at end of the `with` block we raise `_DryRunRollback()` to force the context manager to roll back, then swallow outside the `with`. Preserves the "dry_run = no DB writes" semantic on both backends.
- **ConflictResolver verified pure in-memory**: zero changes to `conflict_resolver.py`. AI04's GRAPH_WINS policy works identically on PG.
- **`import sqlite3` removed from `graph_ingestor.py`**. After PG-C, the only remaining sqlite3 usage in `modules/s3dgraphy/sync/` is in `paradata_store.py` / `group_store.py` (PG-D scope).
- **7 new L2 PG tests**: 6 in `test_ingest_pg.py` (DbHandle acceptance, dry_run rollback — the critical test for `_DryRunRollback`, ConflictResolver, MissingEpochError, create_missing_epochs, atomic rollback on mock failure) + 1 round-trip identity in `test_round_trip_pg.py` (the milestone gate). All skip cleanly when PG offline or psycopg2 missing.

Test count: 250 → 250 passed, 25 skipped (PG offline) or 257 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved. SQLite round-trip preserved.

---

## [5.7.1-alpha] - 2026-05-10

### Italiano

**PG-B — La pipeline di export ora funziona su PostgreSQL.**

Secondo milestone post-Foundation della Phase 3. Ribalta il secondo gruppo di caller di produzione (GraphProjector + GraphMLWriter + GroupProjector — il lato export del bridge s3dgraphy) sull'infrastruttura cross-backend. Tutti i 250 test SQLite di PG-A restano verdi via shim. Round-trip CI fixture suite (PR #6) intatta. AC-2 byte-identical preservato.

- **11 `sqlite3.connect()` siti swappati a SQLAlchemy**: 5 in `graph_projector.py` (`_verify_node_uuid_column`, `_propagate_node_uuid_and_us`, `_enrich_into`, `_merge_groups`, `_emit_toponym_chain`), 2 in `group_projector.py` (`dimensions_with_data`, `build_groups_from_sql`), 1 in `graphml_writer.py` (`_read_first_sito`).
- **Pattern uniforme**: ogni site usa `with handle.engine.connect() as conn:` (read-only) o `engine.begin()` (read+write). Tutte le query usano `text("... :name")` con named params. Tutti gli `except sqlite3.Error` → `except Exception`.
- **NESSUNA modifica al contenuto delle query SQL** — solo wrap della connessione e sintassi placeholder. Il rischio AC-2 è quindi minimo per design.
- **Public API senza breaking change**: `populate_graph(db_path, sito, ...)`, `export_graphml(db_path=..., ...)`, `dimensions_with_data(db_path, sito)`, `build_groups_from_sql(db_path, sito, dimensions)` mantengono il nome `db_path` ma accettano `Path | DbHandle | str` via shim Foundation. Esistenti call site (AC-2 test, PR #6, QGIS dialog) restano invariati.
- **`load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper** in `conftest_pg.py`: riflette lo schema SQLite via SQLAlchemy `Inspector`, esegue `CREATE TABLE IF NOT EXISTS` su PG, `TRUNCATE`, e `executemany INSERT`. Idempotente. Riusabile per PG-C/D.
- **6 nuovi test L2 PG**: 5 in `test_export_pg.py` + 1 AC-2 cousin in `test_ai03_export_pg_structural.py` (il gate del milestone: verifica che il fingerprint strutturale PG corrisponda alla baseline SQLite). Tutti skippano puliti quando PG offline o psycopg2 mancante.

Test count: 250 → 250 passed, 18 skipped (PG offline) o 256 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato dopo ogni Group A/B/C.

### English

**PG-B — Export pipeline now works on PostgreSQL.**

Second post-Foundation milestone of Phase 3. Flips the second batch of production callers (GraphProjector + GraphMLWriter + GroupProjector — the export side of the s3dgraphy bridge) onto the cross-backend infrastructure. All 250 PG-A SQLite tests stay green via shim. Round-trip CI fixture suite (PR #6) intact. AC-2 byte-identical preserved.

- **11 `sqlite3.connect()` sites swapped to SQLAlchemy**: 5 in `graph_projector.py` (`_verify_node_uuid_column`, `_propagate_node_uuid_and_us`, `_enrich_into`, `_merge_groups`, `_emit_toponym_chain`), 2 in `group_projector.py` (`dimensions_with_data`, `build_groups_from_sql`), 1 in `graphml_writer.py` (`_read_first_sito`).
- **Uniform pattern**: each site uses `with handle.engine.connect() as conn:` (read-only) or `engine.begin()` (read+write). All queries use `text("... :name")` named params. All `except sqlite3.Error` → `except Exception`.
- **NO SQL query content changes** — only connection wrapping + placeholder syntax. AC-2 risk minimized by design.
- **Public API zero-breaking-change**: `populate_graph(db_path, sito, ...)`, `export_graphml(db_path=..., ...)`, `dimensions_with_data(db_path, sito)`, `build_groups_from_sql(db_path, sito, dimensions)` keep the `db_path` keyword but accept `Path | DbHandle | str` via the Foundation shim. Existing call sites (AC-2 test, PR #6, QGIS dialog) unchanged.
- **`load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper** in `conftest_pg.py`: reflects SQLite schema via SQLAlchemy `Inspector`, emits `CREATE TABLE IF NOT EXISTS` on PG, `TRUNCATE`, and `executemany INSERT`. Idempotent. Reusable for PG-C/D.
- **6 new L2 PG tests**: 5 in `test_export_pg.py` + 1 AC-2 cousin in `test_ai03_export_pg_structural.py` (the milestone gate: verifies PG structural fingerprint matches SQLite baseline). All skip cleanly when PG offline or psycopg2 missing.

Test count: 250 → 250 passed, 18 skipped (PG offline) or 256 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved after every Group A/B/C.

---

## [5.7.0-alpha] - 2026-05-10

### Italiano

**PG-A — Phase 1 `node_uuid` backfill ora funziona su PostgreSQL.**

Primo milestone post-Foundation della Phase 3. Ribalta il primo caller di produzione (lo script di migrazione `node_uuid`) sull'infrastruttura cross-backend. Tutti i 245 test SQLite di Foundation restano verdi via shim. Nessuna modifica a `populate_list`, projector, paradata store — quelli sono PG-B/C/D.

- **Migration lib SQLAlchemy-everywhere**: `add_columns(db)` e `backfill_uuids(db)` accettano `DbHandle | Path` (backward compat via shim). `engine.begin()` invece di `sqlite3.connect()` ovunque. Atomic via transazione SQLAlchemy.
- **PK discovery cross-dialect**: `sqlalchemy.inspect(engine).get_pk_constraint(table)["constrained_columns"]` rimpiazza il `PRAGMA table_info` SQLite-only. Funziona identicamente su entrambi i backend.
- **`auto_backup_postgres(engine, tag, dest_dir)`**: wrapper di `pg_dump` via `subprocess.run` con timeout 5min, PGPASSWORD in env (mai in argv). Solleva `BackupSkipped` se `pg_dump` non è nel PATH; il caller (CLI o QGIS dialog) decide se procedere senza backup.
- **CLI `--db` / `--conn-str` mutex**: l'argparse richiede esattamente uno dei due. `--conn-str` accetta sia `sqlite:///path` che `postgresql://...`.
- **QGIS handler senza file-picker**: `Migrazioni → Backfill node_uuid` legge la conn-str da `Connection().conn_str()`. Dialog di conferma mostra il backend (sqlite path o pg host/db). Backup dispatch automatico per backend. Errore se nessuna connessione è configurata.
- **`GraphIngestor._verify_schema` cross-dialect**: usa `_columns_of` di Foundation invece di `PRAGMA table_info`. Signature `db_path: Path` preservata (il flip a `DbHandle` è PG-C).
- **Bridge `_offer_node_uuid_migration`**: il dialog di auto-migration nel bridge accetta Path, DbManager, conn-str, o DbHandle.

12 nuovi test (3 lib unit + 3 mutex/backup unit + 6 PG L2). Test count: 245 → 250 passed (PG offline, 12 skip) o 256 passed (PG online + psycopg2). AC-2 byte-identical preservato.

### English

**PG-A — Phase 1 `node_uuid` backfill now works on PostgreSQL.**

First post-Foundation milestone of Phase 3. Flips the first production caller (the `node_uuid` migration script) onto the cross-backend infrastructure. All 245 Foundation SQLite tests stay green via the shim. No changes to `populate_list`, projector, paradata store — those are PG-B/C/D.

- **Migration lib SQLAlchemy-everywhere**: `add_columns(db)` and `backfill_uuids(db)` accept `DbHandle | Path` (backward compat via shim). `engine.begin()` instead of `sqlite3.connect()` throughout. Atomic via SQLAlchemy transactions.
- **Cross-dialect PK discovery**: `sqlalchemy.inspect(engine).get_pk_constraint(table)["constrained_columns"]` replaces SQLite-only `PRAGMA table_info`. Identical behaviour on both backends.
- **`auto_backup_postgres(engine, tag, dest_dir)`**: `pg_dump` subprocess wrapper with 5-minute timeout, PGPASSWORD in env (never on argv). Raises `BackupSkipped` when `pg_dump` is missing from PATH; caller (CLI or QGIS dialog) decides whether to proceed without backup.
- **CLI `--db` / `--conn-str` mutex**: argparse requires exactly one. `--conn-str` accepts both `sqlite:///path` and `postgresql://...`.
- **QGIS handler without file picker**: `Migrazioni → Backfill node_uuid` reads conn-str from `Connection().conn_str()`. Confirmation dialog shows the backend (sqlite path or pg host/db). Backup helper dispatches per backend. Error dialog when no connection is configured.
- **`GraphIngestor._verify_schema` cross-dialect**: uses Foundation's `_columns_of` instead of `PRAGMA table_info`. `db_path: Path` signature preserved (the `DbHandle` flip is PG-C).
- **Bridge `_offer_node_uuid_migration`**: the auto-migration dialog now accepts Path, DbManager, conn-str, or DbHandle.

12 new tests (3 lib unit + 3 mutex/backup unit + 6 PG L2). Test count: 245 → 250 passed (PG offline, 12 skip) or 256 passed (PG online + psycopg2). AC-2 byte-identical preserved.

---

## [5.6.2-alpha] - 2026-05-10

### Italiano

**Foundation per PostgreSQL compat — machinery only, nessun caller cambiato.**

Primo step della Phase 3 (PG-compat refactor del bridge s3dgraphy). Rilascia l'infrastruttura `DbHandle` + shim resolver + dialect-aware introspection senza modificare alcun call site di produzione. Tutti i 234 test SQLite esistenti restano verdi.

- **`DbHandle` dataclass**: wrapper immutabile attorno a un `Engine` SQLAlchemy che traccia se il backend è PostgreSQL, conserva il path SQLite (quando applicabile) e la conn string originale per derivare slugs.
- **`_resolve_db_handle()` shim**: accetta 5 tipi di input (`Path`, `str`, `DbManager`, `Engine`, `DbHandle` passthrough) e li normalizza a `DbHandle`. I `Path` callers ricevono `DeprecationWarning` (continuano a funzionare per tutta la durata di PG-A/B/C/D).
- **`_columns_of()` introspection**: dispatch su `engine.dialect.name` — `PRAGMA table_info` su SQLite, `information_schema.columns` su PostgreSQL, fallback a SQLAlchemy reflection. Sostituisce il path SQLite-only in `GraphIngestor._verify_schema` (cambio caller deferito a PG-C).
- **3 nuove eccezioni**: `DbHandleError`, `UnsupportedBackendError`, `PgConnectionError` (tutte subclass di `GraphSyncError`).
- **Test infrastructure**: `tests/sync/conftest_pg.py` (`pg_engine` + `clean_pg` fixtures, schema bootstrap su `localhost:5433/pyarchinit_test_pg`) + `tests/sync/test_pg_smoke.py`. Skip puliti quando PG è offline o psycopg2 mancante — niente fallimenti CI senza PG locale.
- **`psycopg2-binary>=2.9`** aggiunto a `requirements.txt`.
- **API pubblica**: `DbHandle` + 3 eccezioni esportate da `modules.s3dgraphy.sync`.

13 nuovi test (12 unit + 1 PG smoke). Test count: 234 → 245 passed, 5 skipped (PG offline) o 247 passed, 3 skipped (PG online con psycopg2). AC-2 byte-identical preservato.

### English

**Foundation for PostgreSQL compat — machinery only, no callers changed.**

First step of Phase 3 (PG-compat refactor of the s3dgraphy bridge). Lands the `DbHandle` + resolver shim + dialect-aware introspection infrastructure without changing any production call site. All 234 existing SQLite tests stay green.

- **`DbHandle` dataclass**: immutable wrapper around a SQLAlchemy `Engine` tracking whether the backend is PostgreSQL, the SQLite path (when applicable), and the original conn string for slug derivation.
- **`_resolve_db_handle()` shim**: accepts 5 input types (`Path`, `str`, `DbManager`, `Engine`, `DbHandle` passthrough) and normalises them to `DbHandle`. `Path` callers receive a `DeprecationWarning` (continue to work for the full lifetime of PG-A/B/C/D).
- **`_columns_of()` introspection**: dispatches on `engine.dialect.name` — `PRAGMA table_info` on SQLite, `information_schema.columns` on PostgreSQL, SQLAlchemy reflection fallback. Replaces the SQLite-only path in `GraphIngestor._verify_schema` (caller swap deferred to PG-C).
- **3 new exceptions**: `DbHandleError`, `UnsupportedBackendError`, `PgConnectionError` (all subclass of `GraphSyncError`).
- **Test infrastructure**: `tests/sync/conftest_pg.py` (`pg_engine` + `clean_pg` fixtures, schema bootstrap on `localhost:5433/pyarchinit_test_pg`) + `tests/sync/test_pg_smoke.py`. Skips cleanly when PG is offline or psycopg2 absent — no CI failures without a local PG.
- **`psycopg2-binary>=2.9`** added to `requirements.txt`.
- **Public API**: `DbHandle` + 3 exceptions exported from `modules.s3dgraphy.sync`.

13 new tests (12 unit + 1 PG smoke). Test count: 234 → 245 passed, 5 skipped (PG offline) or 247 passed, 3 skipped (PG online with psycopg2). AC-2 byte-identical preserved.

---

## [5.6.1-alpha] - 2026-05-10

### Italiano

**Hot-fix post-AI07 driven dal primo smoke test su file EM-native.**

Due fix bounded driven dal feedback dell'utente dopo aver provato a importare un file `EM_demo_02.graphml` (formato EMtools nativo, NON pyarchinit-export) in un DB vuoto:

- **Fix #1 — Shorthand `< > << >>` per non-US/USM nei rapporti**: l'importer ora rispetta la convenzione pyarchinit per i tipi unità non canonici. Su read di un edge stratigrafico, il rapporto label viene scelto dal `unita_tipo` di source/target:
  - **Both ∈ {US, USM}** → verbose Italian ("Copre", "Coperto da", "Si lega a", "Tagliato da", ...) — invariato
  - **Either is CON (Continuity)** → single arrow `>` / `<`
  - **Other non-canonical** (USVs, USVn, SF, VSF, USD, DOC, ...) → double arrow `>>` / `<<`
  - Direzione (`>` vs `<`, `>>` vs `<<`) deriva dall'edge_type (overlies/cuts/is_after = `>`, inversi = `<`)
  - Round-trip identity: ora un rapporto utente `>` torna come `>` invece di "Copre"

- **Fix #2 — Auto-detect Phase 1 `node_uuid` migration**: il dialog Import (preview + apply) ora intercetta `SchemaMismatchError` e propone all'utente di applicare la migrazione node_uuid in-place. Click "Sì" → backup automatico + add_columns + backfill UUID v7 + retry dell'import. L'utente non vede più il messaggio criptico "run scripts/migrations/2026_05_node_uuid_backfill.py --apply" su DB freschi.

- 10 nuovi test (`test_rapporti_shorthand_dispatch.py`) che pinnano la dispatch logic in 7 scenari (US-US, USM-US, CON, USVs, DOC, SF/VSF/USVn/USD, unknown) + 3 helper coverage.

- 224 → 234 passed, 3 skipped. AC-2 byte-identical preservato.

### English

**Post-AI07 hot-fix driven by the first smoke test on an EM-native file.**

Two bounded fixes driven by user feedback after attempting to import an `EM_demo_02.graphml` file (EMtools native format, NOT a pyarchinit-export) into an empty DB:

- **Fix #1 — `< > << >>` shorthand for non-US/USM rapporti**: the importer now respects the pyarchinit convention for non-canonical unit types. On reading a stratigraphic edge, the rapporti label is chosen from source/target `unita_tipo`:
  - **Both ∈ {US, USM}** → verbose Italian ("Copre", "Coperto da", "Si lega a", "Tagliato da", ...) — unchanged
  - **Either is CON (Continuity)** → single arrow `>` / `<`
  - **Other non-canonical** (USVs, USVn, SF, VSF, USD, DOC, ...) → double arrow `>>` / `<<`
  - Direction (`>` vs `<`, `>>` vs `<<`) derives from edge_type (overlies/cuts/is_after = `>`, inverses = `<`)
  - Round-trip identity: a user-typed `>` now comes back as `>` instead of "Copre"

- **Fix #2 — Auto-detect Phase 1 `node_uuid` migration**: the Import dialog (preview + apply) now catches `SchemaMismatchError` and offers the user to apply the node_uuid migration in-place. Click "Yes" → auto-backup + add_columns + backfill UUID v7 + retry the import. The user no longer sees the cryptic "run scripts/migrations/2026_05_node_uuid_backfill.py --apply" message on fresh DBs.

- 10 new tests (`test_rapporti_shorthand_dispatch.py`) pinning the dispatch logic across 7 scenarios (US-US, USM-US, CON, USVs, DOC, SF/VSF/USVn/USD, unknown) + 3 helper coverage cases.

- 224 → 234 passed, 3 skipped. AC-2 byte-identical preserved.

---

## [5.6.0-alpha] - 2026-05-10

### Italiano

**AI07 — Migrazione `LocationNodeGroup` + AI08-F1 m:n hierarchical (fusi).**

Le 6 dimensioni spaziali (`area`, `struttura`, `settore`, `ambient`,
`saggio`, `quad_par`) ora producono nodi `LocationNodeGroup` di
s3dgraphy 0.1.41 con `kind ∈ {functional, study}` e edge
`is_in_location`. La dimensione `attivita` resta `ActivityNodeGroup`
con edge `is_in_activity` (Q1 — Emanuel 2026-05-09).

- **m:n membership**: ogni US può appartenere a più gruppi
  contemporaneamente; `is_primary=true` su un singolo edge
  determina il folder yEd visivo. Le altre membership sono
  emesse come `<data key="s3d:other_locations">` array sul
  nodo US per render badge inline.
- **Toponym chain**: da `site_table.{nazione, regione, provincia,
  comune}` viene emesso un chain ricorsivo di
  `LocationNodeGroup(kind="toponym")`, con dedupe cross-site
  (stesso comune in 2 siti = 1 nodo condiviso, UUID deterministico).
- **On-read up-conversion**: i file 5.5.x esistenti vengono
  promossi in-memory automaticamente — il projector intercetta
  `ActivityNodeGroup + group_kind ∈ {area, ..., quad_par}` e li
  converte. Una sola `DeprecationWarning` per chiamata.
- **Multi-dim export warning rimosso**: il workaround di
  5.5.2-alpha (single-dimension only) decade, sostituito dal
  modello m:n con `is_primary`.
- **Dialog combobox "Primary dimension"**: l'utente può
  sovrascrivere la priorità default (struttura > attivita > ...)
  per quel singolo export.
- **Walker ricorsivo**: `_apply_group_folders_to_sql` ora
  discende in folder-in-folder nesting yEd con detection cicli
  via `CycleDetectedError`.

### English

**AI07 — `LocationNodeGroup` migration + AI08-F1 m:n hierarchical (fused).**

The 6 spatial dimensions (`area`, `struttura`, `settore`, `ambient`,
`saggio`, `quad_par`) now produce s3dgraphy 0.1.41
`LocationNodeGroup` nodes with `kind ∈ {functional, study}` and
`is_in_location` edges. The `attivita` dimension stays as
`ActivityNodeGroup` with `is_in_activity` edges (Q1 — Emanuel
2026-05-09).

- **m:n membership**: each US can belong to multiple groups;
  `is_primary=true` on exactly one edge determines the visual
  yEd folder. Other memberships emit `<data key="s3d:other_locations">`
  on the US node for inline badge rendering.
- **Toponym chain**: from `site_table.{nazione, regione, provincia,
  comune}`, a recursive
  `LocationNodeGroup(kind="toponym")` chain is emitted with
  cross-site dedupe (same comune across 2 sites = 1 shared node,
  deterministic UUID).
- **On-read up-conversion**: legacy 5.5.x files are promoted
  in-memory automatically — projector intercepts
  `ActivityNodeGroup + group_kind ∈ {area, ..., quad_par}` and
  converts. One `DeprecationWarning` per call.
- **Multi-dim export warning removed**: the 5.5.2-alpha workaround
  (single-dimension only) is obsolete, replaced by the m:n model
  with `is_primary`.
- **Dialog combobox "Primary dimension"**: user can override the
  default priority (struttura > attivita > ...) for a single export.
- **Recursive walker**: `_apply_group_folders_to_sql` now descends
  into yEd folder-in-folder nesting with cycle detection
  (`CycleDetectedError`).

---

## [s3dgraphy-0.1.41-bump] - 2026-05-09

### Italiano

**Bump della libreria `s3dgraphy` da 0.1.40 a 0.1.41 + sblocco di AI07.**

- **`requirements.txt`** aggiornato: `s3dgraphy>=0.1.41` (riga 79). I nuovi installer prendono 0.1.41+.
- **`ext_libs/s3dgraphy/`** aggiornato in locale a 0.1.41 (datamodel 1.5.5). La cartella è in `.gitignore`, quindi l'aggiornamento per l'utente finale arriva tramite `requirements.txt` + `modules_installer.py`.
- **Test regression-free**: 179 passed, 3 skipped (uguale al baseline pre-bump).

**Cosa porta 0.1.41 (per AI07):**

- `LocationNodeGroup` con `kind ∈ {toponym, study, functional}` e `propagation = "additive"`.
- Nuovo edge type `is_in_location` con doppio mapping CIDOC (`P53 has former or current location` per node→location, `P89 falls within` per la gerarchia ricorsiva location→location).
- Attributo opzionale `is_primary: true` su un singolo `is_in_location` per disambiguare il rendering yEd (m:n membership con un primario per visualizzazione).
- `ActivityNodeGroup` mantenuto, **non deprecato**.

**Decisioni di Emanuel** (issue [zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5)):

- **Q1 — `attivita`**: resta `ActivityNodeGroup`. La semantica di "attività di scavo" è intentional/historical activity, non spaziale. Possibile futuro `kind` (historical/recording) su ActivityNodeGroup se servirà mai.
- **Q2 — Backward compat 5.5.x**: la libreria 0.1.41 legge `ActivityNodeGroup + group_kind` come opaque metadata, **senza promozione automatica a LocationNodeGroup**. La up-conversion vive nel projector di pyarchinit (AI07), non nella libreria — separazione corretta tra layer consumer e layer dato.
- **Multi-projection georef**: siblings paritari (multipli `P161 has spatial projection`), niente canonical-vs-alternates split.

**AI07 ora è ACTIVE** — vedi memory note `project_ai07_active.md` per il piano dettagliato. La self-deadline 2026-05-23 (option B fallback) decade automaticamente.

### English

**Bumped `s3dgraphy` library 0.1.40 → 0.1.41 + AI07 unblocked.**

- **`requirements.txt`** updated: `s3dgraphy>=0.1.41` (line 79). New installs pick up 0.1.41+.
- **`ext_libs/s3dgraphy/`** updated locally to 0.1.41 (datamodel 1.5.5). Directory is `.gitignore`'d — end-user upgrade flows via `requirements.txt` + `modules_installer.py`.
- **Tests regression-free**: 179 passed, 3 skipped (identical to pre-bump baseline).

**What 0.1.41 brings (for AI07):**

- `LocationNodeGroup` with `kind ∈ {toponym, study, functional}` and `propagation = "additive"`.
- New `is_in_location` edge type with dual CIDOC mapping (`P53 has former or current location` for node→location, `P89 falls within` for the recursive location→location hierarchy).
- Optional `is_primary: true` attribute on a single `is_in_location` per source to disambiguate yEd rendering (m:n membership with one primary for visualization).
- `ActivityNodeGroup` retained, **not deprecated**.

**Emanuel's decisions** (issue [zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5)):

- **Q1 — `attivita`**: stays as `ActivityNodeGroup`. "Recording activity" semantics read as intentional/historical activity, not spatial. Future `kind` (historical/recording) on ActivityNodeGroup possible if real attivita data ever requires it.
- **Q2 — Backward compat for 5.5.x**: 0.1.41 reads `ActivityNodeGroup + group_kind` as opaque metadata, **no automatic promotion to LocationNodeGroup**. Up-conversion lives in pyarchinit's projector (AI07), not in the library — correct separation between consumer layer and data layer.
- **Multi-projection georef**: paritary siblings (multiple `P161 has spatial projection`), no canonical-vs-alternate split.

**AI07 is now ACTIVE** — see memory note `project_ai07_active.md` for the detailed plan. Self-deadline 2026-05-23 (option B fallback) is now obsolete.

---

## [housekeeping] - 2026-05-09 (commit `6c9c97c0`)

### Italiano

**Tre task di housekeeping post-pausa Phase 2, raggruppati in un unico commit:**

- **Tooltips Area + US (TEXT, non integer) in tutte le 10 lingue.** I campi `lineEdit_us` e `comboBox_area` nella Scheda US ora mostrano un tooltip che chiarisce: "Inserire come TESTO (non numero intero). Il campo accetta valori alfanumerici come '1', '1A', '42-bis', 'USM01'." Aggiunto anche `setPlaceholderText` per `lineEdit_us`. Tradotto in 10 lingue (`it/en/de/fr/es/ar/ca/ro/pt/el`) con 30 nuovi `<message>` nei file `.ts`, ricompilati a `.qm` con `pyside6-lrelease`.

- **Tutorial 36 "Extended Matrix Export & s3dgraphy Bridge" in 10 lingue.** Nuovo file `36_extended_matrix_s3dgraphy.md` per ogni lingua con 8 sezioni (intro 5.2.0-alpha, prerequisiti, dialog Export, dialog Manage Paradata 4 tab, palette per-dimension visual style, round-trip Import, CLI alternativa, troubleshooting + riferimenti tecnici). Registrato in entrambi i registry: `tabs/Tutorial_viewer.py::TUTORIALS_METADATA` (10 lingue) e `pyarchinitDockWidget.py::TUTORIALS_METADATA` (6 lingue supportate dal dockwidget). Aggiunto al toctree Sphinx in `docs/tutorials/{lang}/index.rst` per 7 lingue (gap pre-esistente: ro/pt/el non hanno `index.rst`).

- **Conversione MD → DOCX per condivisione su Microsoft Teams.** Tutti i markdown in `docs/superpowers/{specs,plans,dev-log}/` sono stati convertiti in `.docx` via pandoc (gfm → docx). Versionati per facilitare la condivisione dei documenti Phase 2 (AI03 → AI08-F2) con stakeholder non tecnici.

### English

**Three post-pause Phase 2 housekeeping tasks bundled in one commit:**

- **Tooltips for Area + US fields (TEXT, not integer) in all 10 languages.** The `lineEdit_us` and `comboBox_area` widgets in the Scheda US now display a tooltip clarifying: "Enter as TEXT (not integer). The field accepts alphanumeric values like '1', '1A', '42-bis', 'USM01'." Also added `setPlaceholderText` to `lineEdit_us`. Translated in 10 languages (`it/en/de/fr/es/ar/ca/ro/pt/el`) via 30 new `<message>` entries in `.ts` files, recompiled to `.qm` with `pyside6-lrelease`.

- **Tutorial 36 "Extended Matrix Export & s3dgraphy Bridge" in 10 languages.** New file `36_extended_matrix_s3dgraphy.md` per language with 8 sections (intro 5.2.0-alpha, prerequisites, Export dialog, Manage Paradata dialog 4 tabs, per-dimension visual style palette, Import round-trip, CLI alternative, troubleshooting + technical references). Registered in both registries: `tabs/Tutorial_viewer.py::TUTORIALS_METADATA` (10 langs) and `pyarchinitDockWidget.py::TUTORIALS_METADATA` (6 langs supported by dockwidget). Added to Sphinx toctree in `docs/tutorials/{lang}/index.rst` for 7 langs (pre-existing gap: ro/pt/el have no `index.rst`).

- **MD → DOCX conversion for Microsoft Teams sharing.** All markdown files in `docs/superpowers/{specs,plans,dev-log}/` converted to `.docx` via pandoc (gfm → docx). Versioned to ease sharing of Phase 2 (AI03 → AI08-F2) documents with non-technical stakeholders.

### Files modified
- `tabs/US_USM.py` (tooltips)
- `i18n/pyarchinit_plugin_*.{ts,qm}` × 10
- `docs/tutorials/{10 langs}/36_extended_matrix_s3dgraphy.md` (new)
- `docs/tutorials/{7 langs}/index.rst` (toctree update)
- `tabs/Tutorial_viewer.py` (TUTORIALS_METADATA × 10 langs)
- `pyarchinitDockWidget.py` (TUTORIALS_METADATA × 6 langs)
- `docs/superpowers/**/*.docx` (15 files generated/updated)

---

## [5.5.2-alpha] - 2026-05-09

### Italiano

**Due hot-fix discovered durante smoke test su DB sintetico (50 US × 7 dimensioni):**

- **Fix #1 — Limite single-dimension per export multi-dim con avviso.** AI06's `_inject_group_folders` re-parenta ogni US dentro un folder yEd via `parent.remove(me); inner.append(me)` — ma ogni elemento XML ha UN solo parent. Quando l'utente spuntava 2+ checkbox di raggruppamento (caso comune con strutture/attività che condividono US), solo l'ULTIMA dimensione processata conteneva effettivamente le US; le altre N-1 dimensioni renderizzavano come folder vuoti. **Workaround** in `S3DGraphyExportDialog.on_export()`: se sono spuntate >1 checkbox, mostra `QMessageBox.warning` con due opzioni: (a) Procedi con SOLO la prima dimensione selezionata, (b) Annulla. Default Annulla. Soluzione strutturale rimandata ad **AI08-F1** (hierarchical nesting), ora a priorità più alta.

- **Fix #2 — Campi mancanti nelle property dei nodi US esportati.** `_propagate_node_uuid_and_us` in `graph_projector.py` interrogava solo 12 colonne di `us_table`, lasciando empty in yEd 5+ campi: `settore`, `ambient`, `saggio`, `quad_par`, `documentazione`. Inoltre `d_interpretativa` non era registrata in `_PYARCHINIT_NODE_DATA_KEYS`. E `datazione_estesa` (per-US, derivata da `periodizzazione_table` via `(periodo, fase)`) mancava completamente per-nodo. **Fix**: estesa la SELECT a 17 colonne, aggiunto lookup `periodizzazione_table → datazione_estesa`, registrate `d_interpretativa` + `datazione_estesa` nei data keys per-US. Risultato: ogni US esportato ora porta 17 campi `pyarchinit.*` popolati invece di 12 (più i due nuovi extra).

- Nessuna modifica al backend di base (AC-2 baseline byte-identical preservato; `_inject_group_folders` invariato). 11 critical regression guards verdi (179/179 passed).

### English

**Two hot-fixes discovered during smoke test on synthetic 50-US × 7-dim DB:**

- **Fix #1 — Single-dimension limit on multi-dim export with warning.** AI06's `_inject_group_folders` re-parents each US into a yEd folder via `parent.remove(me); inner.append(me)` — but each XML element has only ONE parent. When the user checked 2+ grouping checkboxes (common case with structures/activities sharing members), only the LAST processed dimension actually contained the US; the other N-1 rendered as empty rectangles. **Workaround** in `S3DGraphyExportDialog.on_export()`: if >1 checkboxes checked, show `QMessageBox.warning` with two options: (a) proceed with ONLY the first selected dimension, (b) cancel. Default cancel. Structural fix deferred to **AI08-F1** (hierarchical nesting), now higher priority.

- **Fix #2 — Missing fields in exported US node properties.** `_propagate_node_uuid_and_us` in `graph_projector.py` queried only 12 us_table columns, leaving 5+ empty in yEd: `settore`, `ambient`, `saggio`, `quad_par`, `documentazione`. Also `d_interpretativa` was not registered in `_PYARCHINIT_NODE_DATA_KEYS`. And `datazione_estesa` (per-US, derived from `periodizzazione_table` via `(periodo, fase)`) was missing entirely per-node. **Fix**: extended SELECT to 17 columns, added `periodizzazione_table → datazione_estesa` lookup, registered `d_interpretativa` + `datazione_estesa` in per-US data keys. Result: each exported US now carries 17 populated `pyarchinit.*` fields (vs 12 before).

- No core backend changes (AC-2 baseline byte-identical preserved; `_inject_group_folders` untouched). All 11 critical regression guards green (179/179 passed).

---

## [5.5.1-alpha] - 2026-05-09

### Italiano

- **Phase 2 / AI08-F2 — Stile visivo per dimensione nei group folder.** Ogni dimensione di raggruppamento (area / struttura / attivita / settore / ambient / saggio / quad_par / adhoc) ora ha un fill pastello distinto al 50% di trasparenza più un bordo solido colorato della stessa famiglia. Il fill 50% lascia intravedere le righe delle epoche dietro il rettangolo del gruppo.
- **Palette hardcoded** in `modules/s3dgraphy/sync/graphml_writer.py` come constante `_GROUP_KIND_PALETTE`. Niente file di config — 8 entry, ognuna `(fill_rgba_50pct, border_solid)`.
- **Default invariato.** Senza checkbox spuntate (`groups=None`) il pulsante verde produce lo stesso GraphML byte-identico al baseline AC-2. La palette si attiva solo quando i gruppi sono materializzati.
- **Background label** (`#EBEBEB`) e geometry restano AI06. Solo `<y:Fill>` e `<y:BorderStyle>` cambiano per dimensione.
- **Round-trip preservato.** L'output AI06 importava i folder via `yfiles.foldertype="group"` + prefix `grp_*` (lxml-based, color-agnostic) — nessun impatto su `sql_apply_groups`.

### English

- **Phase 2 / AI08-F2 — Per-dimension visual style for group folders.** Each grouping dimension (area / struttura / attivita / settore / ambient / saggio / quad_par / adhoc) now has its own pastel fill at 50% transparency plus a matching solid darker border. The 50% alpha lets the epoch row swimlanes show through the group rectangle.
- **Hardcoded palette** in `modules/s3dgraphy/sync/graphml_writer.py` as the `_GROUP_KIND_PALETTE` constant. No config file — 8 entries, each `(fill_rgba_50pct, border_solid)`.
- **Default unchanged.** Without checked checkboxes (`groups=None`) the green Export button produces the same GraphML byte-identical to the AC-2 baseline. The palette only kicks in when groups are materialised.
- **Label background** (`#EBEBEB`) and geometry remain as in AI06. Only `<y:Fill>` and `<y:BorderStyle>` vary per dimension.
- **Round-trip preserved.** The AI06 import path identifies group folders by `yfiles.foldertype="group"` + `grp_*` id prefix (lxml-based, color-agnostic) — no impact on `sql_apply_groups`.

## [5.5.0-alpha] - 2026-05-08

### Italiano

- **Phase 2 / AI06 — Node grouping nell'export Extended Matrix.** Aggiunto raggruppamento opt-in delle US per qualunque sottoinsieme delle 7 colonne `us_table` (`area`, `struttura`, `attivita`, `settore`, `ambient`, `saggio`, `quad_par`) più gruppi ad-hoc creati dall'utente. Default invariato (no checkbox = no raggruppamento, AC-2 baseline preservato byte-identical).
- **Rendering yEd canonico.** Ogni gruppo è un folder yEd (`yfiles.foldertype="group"`, border tratteggiato, fill `#F5F5F5`, label in alto su sfondo `#EBEBEB`) nidificato dentro lo swimlane delle epoche, con geometria che attraversa tutte le righe epoca dei suoi membri.
- **Knowledge graph.** Ogni gruppo è un `s3dgraphy.ActivityNodeGroup` con attributo `group_kind` discriminator (struttura/area/attivita/...) e edge `is_in_activity` da ogni US membro.
- **GroupStore.** Nuova classe `modules/s3dgraphy/sync/group_store.py` per gestire gruppi ad-hoc in `groups_{sito_slug}.graphml` accanto al DB. CRUD atomic-safe via `os.replace()`. Specchio del `ParadataStore` di AI05.
- **Dialog "Manage paradata" → 4 tab.** Aggiunta tab "Groups" con form Add (name + kind + Pick US members) e tabella esistenti.
- **Export dialog → 7 checkbox.** Pulsante verde "Esporta Extended Matrix" mostra "Group US by" con preselect automatico delle dimensioni popolate.
- **Round-trip configurabile.** Tab Import ha checkbox "Update SQL on import" (default OFF). Quando attivo, lo spostamento di una US in un altro gruppo via yEd aggiorna `us_table` con transazione atomica e rollback su errore.
- **CLI** con 4 nuovi sub-subcomandi `paradata add-group/list-groups/add-us-to-group/remove-group` e flag `export --group-by struttura,attivita,adhoc`.
- **Issue upstream aperta** ([zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5)) per `LocationNodeGroup` + edge `is_in_location` — migrazione AI07 quando upstream landa.

### English

- **Phase 2 / AI06 — Node grouping in Extended Matrix export.** Adds opt-in US grouping by any subset of 7 `us_table` columns (`area`, `struttura`, `attivita`, `settore`, `ambient`, `saggio`, `quad_par`) plus user-authored ad-hoc groups. Default unchanged (no checkbox = no grouping, AC-2 baseline byte-identical preserved).
- **EM canonical yEd rendering.** Each group is a yEd folder (`yfiles.foldertype="group"`, dashed border, fill `#F5F5F5`, NodeLabel top with bg `#EBEBEB`) nested inside the epoch swimlane, with geometry spanning all epoch rows of its member US.
- **Knowledge graph.** Each group is a `s3dgraphy.ActivityNodeGroup` with `group_kind` discriminator attribute (struttura/area/attivita/...) and `is_in_activity` edge from each member US.
- **GroupStore.** New `modules/s3dgraphy/sync/group_store.py` class for ad-hoc groups stored in `groups_{sito_slug}.graphml` next to the DB. Atomic-safe CRUD via `os.replace()`. Mirror of AI05's `ParadataStore`.
- **"Manage paradata" dialog → 4 tabs.** Adds "Groups" tab with Add form (name + kind + Pick US members) and existing-groups table.
- **Export dialog → 7 checkboxes.** Green "Esporta Extended Matrix" button now shows "Group US by" with auto-preselect of populated dimensions.
- **Configurable round-trip.** Import tab has "Update SQL on import" checkbox (default OFF). When enabled, moving a US to a different group folder in yEd writes back to `us_table` in an atomic transaction with rollback on error.
- **CLI** with 4 new sub-subcommands `paradata add-group/list-groups/add-us-to-group/remove-group` plus `export --group-by struttura,attivita,adhoc` flag.
- **Upstream issue opened** ([zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5)) for `LocationNodeGroup` + `is_in_location` edge — AI07 migration target when upstream lands.

## [5.4.0-alpha] - 2026-05-08

### Italiano

- **Phase 2 / AI05 — ParadataStore + UI authoring + chiusura Phase 2.** Nuova classe `ParadataStore` per la gestione atomica di `paradata_{sito}.graphml` (Author/License/Embargo per sito). API low-level (`read`/`write`/`add_node`/`remove_node`/`find`) e high-level (`add_author`/`add_license`/`add_embargo` + `list_*`).
- **Dialog "Manage paradata".** Nuovo bottone nella scheda US/USM apre un dialog 3-tab (Authors / Licenses / Embargoes) per CRUD visuale. Versionable in Git accanto al DB.
- **GraphProjector Strategy A promotion.** Il body di `_enrich_pyarchinit_graph` è stato spostato dentro `GraphProjector` (la funzione standalone in `graphml_writer.py` è stata eliminata). `populate_graph(..., include_paradata=True)` di default fonde strat + paradata.
- **Edge styling automation.** Nuovo modulo `edge_registry` legge `s3Dgraphy_connections_datamodel.json` + `em_visual_rules.json` per classificazione e style automatici. Override-wins via `_PYARCHINIT_EDGE_OVERRIDES`.
- **CLI `s3dgraphy_sync.py paradata`** con 7 sub-subcomandi: add-author / list-authors / add-license / list-licenses / add-embargo / list-embargos / remove.

### English

- **Phase 2 / AI05 — ParadataStore + UI authoring + Phase 2 closure.** New `ParadataStore` class managing `paradata_{sito}.graphml` atomically (site-level Author/License/Embargo). Low-level API (`read`/`write`/`add_node`/`remove_node`/`find`) and high-level helpers (`add_author`/`add_license`/`add_embargo` + `list_*`).
- **"Manage paradata" dialog.** New button in the US/USM scheda opens a 3-tab dialog (Authors / Licenses / Embargoes) for visual CRUD. Versionable in Git next to the DB.
- **GraphProjector Strategy A promotion.** The `_enrich_pyarchinit_graph` body was moved into `GraphProjector` (the standalone function in `graphml_writer.py` is now DELETED). `populate_graph(..., include_paradata=True)` defaults to merging strat + paradata.
- **Edge styling automation.** New `edge_registry` module reads `s3Dgraphy_connections_datamodel.json` + `em_visual_rules.json` for automatic classification and styling. Override-wins via `_PYARCHINIT_EDGE_OVERRIDES`.
- **CLI `s3dgraphy_sync.py paradata`** with 7 sub-subcommands: add-author / list-authors / add-license / list-licenses / add-embargo / list-embargos / remove.

## [5.3.0-alpha] - 2026-05-08

### Italiano

- **Phase 2 / AI04 — Bridge bidirezionale PyArchInit ↔ s3dgraphy.** Nuova API pubblica `GraphProjector.populate_graph(db, sito)` e `GraphIngestor.populate_list(graph, db, sito, dry_run, create_missing_epochs)` per il round-trip DB↔grafo. Strategia D wrapper su `_enrich_pyarchinit_graph` (zero impatto sul path AI03; AC-2 garantita).
- **Tab "Import" nel dialog Extended Matrix.** Nuova tab con file picker, anteprima dry-run dei conflitti, e bottone "Applica" per scrivere nel DB. La tab "Export" è inalterata.
- **CLI helper `scripts/s3dgraphy_sync.py`** con sottocomandi `export` e `import`. L'import è dry-run di default; `--apply` obbligatorio per scrivere.
- **`UPDATE` selettivo sui 12 campi mappati.** Le 40+ colonne pyarchinit-specifiche (descrizione, foto, profondita, ...) sono preservate intatte durante il round-trip.
- **Transazioni atomiche.** Qualsiasi fallimento durante l'ingestion fa ROLLBACK al DB; mai stati misti.

### English

- **Phase 2 / AI04 — Bidirectional PyArchInit ↔ s3dgraphy bridge.** New public API `GraphProjector.populate_graph(db, sito)` and `GraphIngestor.populate_list(graph, db, sito, dry_run, create_missing_epochs)` for round-trip DB↔graph. Strategy D wrapper on `_enrich_pyarchinit_graph` (zero impact on the AI03 path; AC-2 guarantee).
- **"Import" tab in the Extended Matrix dialog.** New tab with file picker, dry-run conflict preview, and "Apply" button for committing to the DB. The "Export" tab is unchanged.
- **CLI helper `scripts/s3dgraphy_sync.py`** with `export` and `import` subcommands. Import is dry-run by default; `--apply` is required to actually write.
- **Selective `UPDATE` on the 12 mapped columns.** The 40+ pyarchinit-specific columns (descrizione, foto, profondita, ...) are preserved untouched during round-trip.
- **Atomic transactions.** Any ingestion failure ROLLBACKs the DB; no mixed states.

## [5.2.0-alpha] - 2026-05-07

**Phase 2 / AI03 chiuso: delega del ramo GraphML dell'export "Extended Matrix" a s3Dgraphy.** Cut-over pulito (nessun fallback): la pipeline legacy DOT→GraphML viene rimossa e il bridge invoca `s3dgraphy.PyArchInitImporter` + `s3dgraphy.exporter.graphml.GraphMLExporter`. Chiude le quattro limitazioni EM emerse alla fine della Phase 1 (graphml vuoto con flag di grouping, niente swimlane di periodo, edge styling parziale, niente riduzione transitiva). / **Phase 2 / AI03 closed: delegation of the GraphML branch of the "Extended Matrix" export to s3Dgraphy.** Clean cut-over (no fallback): the legacy DOT→GraphML pipeline is removed and the bridge invokes `s3dgraphy.PyArchInitImporter` + `s3dgraphy.exporter.graphml.GraphMLExporter`. Closes the four EM limitations surfaced at the end of Phase 1 (empty graphml on grouping flag, no period swimlanes, partial edge styling, no transitive reduction).

### Aggiunto / Added

- **feat(s3dgraphy/sync): nuovo modulo `graphml_writer.py`** con tre helper puri (`build_pyarchinit_mapping()`, `count_epoch_nodes()`, `count_topological_edges()`) e un orchestratore `write_graphml_via_s3dgraphy(sqlite_path, output_path) -> ExportResult` che: (1) apre la SQLite via `sqlalchemy.create_engine`, (2) instanzia `PyArchInitImporter(connection_url=..., mapping_name="pyarchinit_us_mapping", overwrite=True)` e popola il grafo, (3) chiama `_enrich_pyarchinit_graph()` per aggiungere `EpochNode` da `periodizzazione_table` + edge `has_first_epoch` da US a EpochNode + edge topologici `is_before` derivati da `us_table.rapporti` (`PyArchInitImporter` da solo non li produce, è un workaround documentato nel modulo), (4) invoca `GraphMLExporter(graph, output_path).export()` con riduzione transitiva interna, (5) restituisce un `ExportResult` con `node_count`, `edge_count`, `epoch_count`, `tred_removed_edges` (calcolato in aritmetica come `pre_edges - post_edges`, non via regex), `warnings`. / **feat(s3dgraphy/sync): new `graphml_writer.py` module** with three pure helpers (`build_pyarchinit_mapping()`, `count_epoch_nodes()`, `count_topological_edges()`) and an orchestrator `write_graphml_via_s3dgraphy(sqlite_path, output_path) -> ExportResult` that: (1) opens the SQLite via `sqlalchemy.create_engine`, (2) instantiates `PyArchInitImporter(connection_url=..., mapping_name="pyarchinit_us_mapping", overwrite=True)` and populates the graph, (3) calls `_enrich_pyarchinit_graph()` to add `EpochNode`s from `periodizzazione_table` + `has_first_epoch` edges from US to EpochNode + topological `is_before` edges derived from `us_table.rapporti` (`PyArchInitImporter` alone does not produce them — this is a documented workaround inside the module), (4) invokes `GraphMLExporter(graph, output_path).export()` with internal transitive reduction, (5) returns an `ExportResult` with `node_count`, `edge_count`, `epoch_count`, `tred_removed_edges` (computed arithmetically as `pre_edges - post_edges`, not via regex), `warnings`.
- **feat(s3dgraphy_dot_bridge): cut-over del ramo GraphML al nuovo orchestratore.** Il dispatcher dell'export "Extended Matrix" ora chiama `write_graphml_via_s3dgraphy()` quando il formato richiesto è GraphML; il ramo DOT resta invariato (è ancora usato dagli export Harris matrix fuori scope AI03). / **feat(s3dgraphy_dot_bridge): GraphML-branch cut-over to the new orchestrator.** The "Extended Matrix" export dispatcher now calls `write_graphml_via_s3dgraphy()` when the requested format is GraphML; the DOT branch is left untouched (it is still used by Harris-matrix exporters out of AI03 scope).
- **feat(db_manager): nuovo metodo `get_sqlite_path()`** che restituisce il path assoluto della SQLite quando il backend è SpatiaLite, altrimenti `None`. Il bridge usa questo segnale per saltare il ramo GraphML con un Info dialog ("PostgreSQL backend will be supported in AI04") quando il progetto QGIS è collegato a PostgreSQL/PostGIS, evitando crash di `PyArchInitImporter` che oggi accetta solo `connection_url` SQLite. / **feat(db_manager): new `get_sqlite_path()` method** that returns the absolute path of the SQLite file when the backend is SpatiaLite, otherwise `None`. The bridge uses this signal to skip the GraphML branch with an Info dialog ("PostgreSQL backend will be supported in AI04") when the QGIS project is connected to PostgreSQL/PostGIS, avoiding crashes in `PyArchInitImporter` (which today accepts only a SQLite `connection_url`).
- **feat(S3DGraphyExportDialog): summary post-export con metriche per-formato.** Il dialog finale ora mostra, per ciascun formato esportato (GraphML/DOT/JSON), `node_count`, `edge_count`, `epoch_count`, `tred_removed_edges` e l'eventuale lista di warning (es. "no periodizzazione_table rows → epoch_count=0"). Sostituisce il vecchio messaggio binario "Export completed". / **feat(S3DGraphyExportDialog): post-export summary with per-format metrics.** The final dialog now shows, per exported format (GraphML/DOT/JSON), `node_count`, `edge_count`, `epoch_count`, `tred_removed_edges`, and any warnings list (e.g. "no periodizzazione_table rows → epoch_count=0"). Replaces the old binary "Export completed" message.

### Rimosso / Removed

- **refactor(s3dgraphy): cancellato `graphml_spatial_enhancer.py`** (post-processor che annidava nodi nei subgraph y:ProxyAutoBoundsNode dentro un GraphML già scritto). Funzione obsoleta: `GraphMLExporter` di s3Dgraphy emette già le swimlane di epoca nativamente. / **refactor(s3dgraphy): deleted `graphml_spatial_enhancer.py`** (post-processor that nested nodes inside `y:ProxyAutoBoundsNode` subgraphs in an already-written GraphML). Obsolete: s3Dgraphy's `GraphMLExporter` emits epoch swimlanes natively.
- **refactor(s3dgraphy_dot_bridge): rimosso `_convert_dot_to_graphml()`** + import di `dottoxml` dal bridge. Il bridge non converte più DOT in GraphML in nessun cammino. / **refactor(s3dgraphy_dot_bridge): removed `_convert_dot_to_graphml()`** + the `dottoxml` import from the bridge. The bridge no longer converts DOT to GraphML in any path.
- **refactor(spatial_grouping_manager): rimossi `apply_grouping_to_dot()` e la classe `SpatialGroupingDialog`** (Qt UI accoppiata al vecchio flusso DOT→GraphML). Il modulo conserva solo le strutture-dati di grouping consultate altrove. / **refactor(spatial_grouping_manager): removed `apply_grouping_to_dot()` and the `SpatialGroupingDialog` class** (Qt UI coupled to the old DOT→GraphML flow). The module keeps only the grouping data-structures consulted elsewhere.
- **refactor(S3DGraphyExportDialog): rimosso il checkbox `cb_spatial_grouping`** + tutto il codice che lo leggeva. Lo spatial grouping per GraphML è ora gestito nativamente da `GraphMLExporter`. / **refactor(S3DGraphyExportDialog): removed the `cb_spatial_grouping` checkbox** + all code that read it. Spatial grouping for GraphML is now handled natively by `GraphMLExporter`.
- **note**: `resources/dbfiles/dot.py` e `dottoxml.py` sono stati conservati: sono ancora usati dagli export Harris-matrix legacy (fuori dallo scope AI03, valutati per AI04). / **note**: `resources/dbfiles/dot.py` and `dottoxml.py` are kept: they are still consumed by the legacy Harris-matrix exporters (out of AI03 scope, to be reassessed in AI04).

### Test

- **16 nuovi test sotto `tests/sync/`** (totale post-AI03: 59 passing): 3 helper unit test per `build_pyarchinit_mapping`/`count_epoch_nodes`/`count_topological_edges`, 4 test sulla pipeline end-to-end con la fixture deterministica `tests/sync/fixtures/mini_volterra.sqlite` (mappati 1:1 alle quattro limitazioni EM: graphml non vuoto con grouping, swimlane di periodo presenti, edge `is_before` con stile, riduzione transitiva > 0), 4 test per `db_manager.get_sqlite_path()` (SQLite valido, SQLite mancante, PostgreSQL → None, db_manager non inizializzato → None), 5 test pre-esistenti dei helper di eccezione del modulo. / **16 new tests under `tests/sync/`** (total after AI03: 59 passing): 3 helper unit tests for `build_pyarchinit_mapping`/`count_epoch_nodes`/`count_topological_edges`, 4 end-to-end pipeline tests against the deterministic fixture `tests/sync/fixtures/mini_volterra.sqlite` (mapped 1:1 to the four EM limitations: non-empty graphml with grouping, period swimlanes present, styled `is_before` edges, transitive reduction > 0), 4 tests for `db_manager.get_sqlite_path()` (valid SQLite, missing SQLite, PostgreSQL → None, uninitialized db_manager → None), 5 pre-existing exception-helper tests of the module.
- **fixture**: `tests/sync/fixtures/mini_volterra.sqlite` è una mini-DB deterministica con 6 US (rapporti incrociati che esercitano la riduzione transitiva), 3 periodi (`periodizzazione_table`) e una geometria semplificata. È committata binaria nel repo: i test sono riproducibili senza dipendere da DB di produzione. / **fixture**: `tests/sync/fixtures/mini_volterra.sqlite` is a deterministic mini-DB with 6 US records (cross-cutting `rapporti` that exercise transitive reduction), 3 periods (`periodizzazione_table`) and simplified geometry. It is committed as a binary blob: tests are reproducible without depending on production DBs.

### File modificati / Modified files

- **Nuovi / New**: `modules/s3dgraphy/sync/graphml_writer.py`, `tests/sync/test_graphml_writer_helpers.py`, `tests/sync/test_graphml_writer_pipeline.py`, `tests/sync/test_db_manager_sqlite_path.py`, `tests/sync/fixtures/mini_volterra.sqlite`.
- **Modificati / Modified**: `metadata.txt` (5.1.0-alpha → 5.2.0-alpha + entry changelog), `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (rimossa `_convert_dot_to_graphml`, dispatcher GraphML chiama ora `write_graphml_via_s3dgraphy`), `modules/s3dgraphy/spatial_grouping_manager.py` (rimossi `apply_grouping_to_dot` + `SpatialGroupingDialog`), `modules/db/pyarchinit_db_manager.py` (nuovo `get_sqlite_path()`), `tabs/S3DGraphyExportDialog.py` (rimosso `cb_spatial_grouping`, summary metrics-rich), `gui/ui/S3DGraphyExportDialog.ui` (rimosso checkbox).
- **Cancellati / Deleted**: `modules/s3dgraphy/graphml_spatial_enhancer.py`.
- **Conservati intenzionalmente / Kept on purpose**: `resources/dbfiles/dot.py`, `resources/dbfiles/dottoxml.py` (ancora usati dagli export Harris-matrix).

---

## [5.1.0-alpha] - 2026-05-07

**Phase 1 (Foundation) of the StratiGraph WP5/T5.4 PyArchInit ↔ s3Dgraphy bridge.** Closes meeting action items AI01–AI05 (T5.4 minutes 2026-05-04) and aligns to Reference Document v0.1 (Emanuel Demetrescu, 2026-05-06). Tag: `phase1-foundation-5.1.0-alpha`. Rollback tag: `pre-s3dgraphy-040`.

### Aggiunto / Added

- **feat(s3dgraphy/sync): nuovo `VocabProvider` che parsa direttamente i tre pillars JSON di s3Dgraphy 0.1.40** (Option B per Reference Doc v0.1 §4.5). Il pacchetto `modules/s3dgraphy/sync/` ospita un core puro Python (`vocab_provider_core.py`) testabile via pytest senza QGIS bootstrap, e un wrapper Qt (`vocab_provider.py`) che aggiunge `vocabulary_changed` signal + `QFileSystemWatcher` per hot-reload. `VocabProvider` espone `get_unit_types(family=...)`, `get_edge_types()`, `get_paradata_types()`, `get_visual_rule()`, `get_cidoc_mapping()`, `get_legal_targets_for()`, `versions` (con minimum-version gating opzionale al costruttore). Override priority: `~/.config/pyarchinit/vocab_overrides/*.json` → bundled `ext_libs/s3dgraphy/JSON_config/*.json` con merge per top-level key (un override parziale non cancella tipi bundled). Compatibilità con il filename storico 0.1.30 con spazio finale `s3Dgraphy_node_datamodel .json`. Generatore UUID v7 locale RFC 9562 §5.7 (sostituito da `uuid.uuid7()` quando il minimo Python sarà 3.14+). 25 test unitari + 2 smoke test contro il vendor reale 0.1.40. / **feat(s3dgraphy/sync): new `VocabProvider` that parses the three s3Dgraphy 0.1.40 JSON pillars directly** (Option B per Reference Doc v0.1 §4.5). The `modules/s3dgraphy/sync/` package hosts a pure-Python core (`vocab_provider_core.py`) testable via pytest without QGIS bootstrap, and a Qt wrapper (`vocab_provider.py`) that adds a `vocabulary_changed` signal + `QFileSystemWatcher` for hot-reload. `VocabProvider` exposes `get_unit_types(family=...)`, `get_edge_types()`, `get_paradata_types()`, `get_visual_rule()`, `get_cidoc_mapping()`, `get_legal_targets_for()`, `versions` (with optional minimum-version gating at construction). Override priority: `~/.config/pyarchinit/vocab_overrides/*.json` → bundled `ext_libs/s3dgraphy/JSON_config/*.json` with per-top-level-key merge (a partial override does not erase bundled types). Compatibility with the legacy 0.1.30 trailing-space filename `s3Dgraphy_node_datamodel .json`. Local UUID v7 generator (RFC 9562 §5.7; replaced with stdlib `uuid.uuid7()` once project minimum is Python 3.14+). 25 unit tests + 2 smoke tests against the real bundled 0.1.40 vendor.

- **feat(migrations): migrazione one-shot `USVA/USVB → USVs`, `USVC → USVn`** allinea i database storici al vocabolario canonico EM 1.5 di s3Dgraphy. Idempotente. Voce di menu QGIS `Maintenance → Migrazioni → Allinea vocabolario US`. Auto-backup prima di `--apply` con timestamp UTC nel nome file (`<db>.pre_us_vocab_alignment_<UTC>`). Rollback supportato via `--rollback <backup_path>`. Library/CLI split per testabilità. Spec §4.4. / **feat(migrations): one-shot `USVA/USVB → USVs`, `USVC → USVn` migration** aligns historical databases with the canonical EM 1.5 s3Dgraphy vocabulary. Idempotent. QGIS menu entry under `Maintenance → Migrazioni → Allinea vocabolario US`. Auto-backup before `--apply` with UTC-timestamped filename (`<db>.pre_us_vocab_alignment_<UTC>`). Rollback supported via `--rollback <backup_path>`. Library/CLI split for testability. Spec §4.4.

- **feat(migrations): backfill UUID v7 sulla colonna `node_uuid TEXT`** aggiunta a `us_table`, `inventario_materiali_table`, `periodizzazione_table` con indice UNIQUE parziale (`WHERE node_uuid IS NOT NULL`, così i NULL temporanei durante recovery parziali non collidono). UUID generato in Python via `modules/s3dgraphy/sync/uuid7.py`; monotonico per processo. Idempotente. Voce menu QGIS dedicata. Spec §4.5. / **feat(migrations): UUID v7 backfill on `node_uuid TEXT` column** added to `us_table`, `inventario_materiali_table`, `periodizzazione_table` with a partial UNIQUE index (`WHERE node_uuid IS NOT NULL`, so transient NULLs during partial recovery don't collide). UUID generated in Python via `modules/s3dgraphy/sync/uuid7.py`; monotonic per process. Idempotent. Dedicated QGIS menu entry. Spec §4.5.

### Modificato / Changed

- **refactor(i18n): `pyarchinit_i18n_stratigraphic.py` diventa adapter su `VocabProvider`**. La picker dialog dei tipi US/USM ora espone 27 voci (era 14) sourced dal datamodel JSON 0.1.40: appaiono `USVs`, `USVn`, `serSU`, `WorkingUnit (UL)`, `NegativeStratigraphicUnit (USN)`, `TSU` e gli aggiornamenti EM 1.6 in arrivo. `_COMMON_ITEMS`, `UNIT_TYPE_ABBREV`, `get_unit_type_items`, `is_us_type`, `is_usm_type`, `ALL_US_ABBREVS`/`ALL_USM_ABBREVS` rimangono importabili come prima — 5 regression test in `tests/sync/test_i18n_compat.py` lockano la public surface. Fallback al vecchio elenco hardcoded quando `ext_libs/s3dgraphy/` è assente. Deprecation log al primo import. Rimozione del fallback prevista per 6.0.0. / **refactor(i18n): `pyarchinit_i18n_stratigraphic.py` becomes an adapter over `VocabProvider`**. The US/USM type picker dialog now exposes 27 items (was 14) sourced from the 0.1.40 JSON datamodel: `USVs`, `USVn`, `serSU`, `WorkingUnit (UL)`, `NegativeStratigraphicUnit (USN)`, `TSU` and the incoming EM 1.6 additions appear. `_COMMON_ITEMS`, `UNIT_TYPE_ABBREV`, `get_unit_type_items`, `is_us_type`, `is_usm_type`, `ALL_US_ABBREVS`/`ALL_USM_ABBREVS` remain importable — 5 regression tests in `tests/sync/test_i18n_compat.py` lock the public surface. Fallback to the legacy hardcoded list when `ext_libs/s3dgraphy/` is missing. One-time deprecation log on first import. Fallback removal scheduled for 6.0.0.

- **refactor(s3dgraphy): 12 file in `modules/s3dgraphy/` auditati; 7 refactored** per consultare `VocabProvider` invece di tabelle hardcoded. Lista: `cidoc_crm_mapper.py` (`CRM_CLASSES` da dict statico a `@property` su VocabProvider), `s3dgraphy_integration.py` (string-tag `node.node_type = 'virtual_reconstruction'` rimpiazzato), `s3dgraphy_dot_bridge.py` (visual rules da `em_visual_rules.json`), `matrix_graph_visualizer.py`/`plotly_visualizer.py`/`simple_graph_visualizer.py`/`graphviz_visualizer.py` (color_map hardcoded → VocabProvider con fallback legacy). 4 file rimangono audit-only (`blender_integration.py`, `graphml_spatial_enhancer.py`, `spatial_grouping_manager.py`, `matrix_visualizer_qgis.py`). Per-file commits per `git revert` selettivo. / **refactor(s3dgraphy): 12 files in `modules/s3dgraphy/` audited; 7 refactored** to consult `VocabProvider` instead of hardcoded tables. List: `cidoc_crm_mapper.py` (`CRM_CLASSES` from static dict to a `@property` over VocabProvider), `s3dgraphy_integration.py` (string-tag `node.node_type = 'virtual_reconstruction'` replaced), `s3dgraphy_dot_bridge.py` (visual rules from `em_visual_rules.json`), `matrix_graph_visualizer.py`/`plotly_visualizer.py`/`simple_graph_visualizer.py`/`graphviz_visualizer.py` (hardcoded `color_map` → VocabProvider with legacy fallback). 4 files remain audit-only (`blender_integration.py`, `graphml_spatial_enhancer.py`, `spatial_grouping_manager.py`, `matrix_visualizer_qgis.py`). Per-file commits for selective `git revert`.

### Dipendenze / Dependencies

- **deps(s3dgraphy): bump 0.1.30 → 0.1.40** in `ext_libs/` (gitignored runtime install — `requirements.txt` floor è la fonte di verità). datamodel 1.5.3 → 1.5.4. La 0.1.40 porta `GraphMerger`, `GraphMLPatcher`, classification API (`get_family`, `is_real`, `iter_subtypes`), `aux_tracking`, le nuove classi `NegativeStratigraphicUnit` e `WorkingUnit`, e il fix del filename `s3Dgraphy_node_datamodel.json` (rimosso lo spazio finale del 0.1.30). Tag di rollback: `pre-s3dgraphy-040`. Procedura di rollback: `pip install s3dgraphy==0.1.30 --target ext_libs/ --no-deps`. / **deps(s3dgraphy): bump 0.1.30 → 0.1.40** in `ext_libs/` (gitignored runtime install — `requirements.txt` floor is the source of truth). datamodel 1.5.3 → 1.5.4. 0.1.40 brings `GraphMerger`, `GraphMLPatcher`, classification API (`get_family`, `is_real`, `iter_subtypes`), `aux_tracking`, the new `NegativeStratigraphicUnit` and `WorkingUnit` classes, and the `s3Dgraphy_node_datamodel.json` filename fix (trailing space removed). Rollback tag: `pre-s3dgraphy-040`. Rollback procedure: `pip install s3dgraphy==0.1.30 --target ext_libs/ --no-deps`.

### Test

- **42 unit test passing** (29 in `tests/sync/` + 13 in `tests/migrations/`). `pyproject.toml` configura pytest scoped a `tests/sync` e `tests/migrations` (i test legacy in `tests/` continuano a richiedere QGIS bootstrap come prima). / **42 unit tests passing** (29 in `tests/sync/` + 13 in `tests/migrations/`). `pyproject.toml` scopes pytest to `tests/sync` and `tests/migrations` (legacy tests in `tests/` continue to require QGIS bootstrap as before).

### File modificati / Modified files

- `ext_libs/s3dgraphy/` (gitignored — wholesale 0.1.30 → 0.1.40 vendor swap on each developer machine via `pip install --target ext_libs/`)
- `modules/s3dgraphy/sync/` (NEW: `vocab_types.py`, `vocab_provider_core.py`, `vocab_provider.py`, `uuid7.py`, `__init__.py`)
- `modules/utility/pyarchinit_i18n_stratigraphic.py` (adapter refactor)
- `modules/s3dgraphy/cidoc_crm_mapper.py` (`CRM_CLASSES` → `@property`)
- `modules/s3dgraphy/s3dgraphy_integration.py` (string-tag → typed)
- `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (visual rules from JSON)
- `modules/s3dgraphy/{matrix_graph_visualizer,plotly_visualizer,simple_graph_visualizer,graphviz_visualizer}.py` (color_map → VocabProvider)
- `scripts/migrations/` (NEW: `_common.py`, `_2026_05_us_vocabulary_alignment_lib.py`, `2026_05_us_vocabulary_alignment.py`, `_2026_05_node_uuid_backfill_lib.py`, `2026_05_node_uuid_backfill.py`, `__init__.py`)
- `tests/sync/`, `tests/migrations/` (NEW: 42 unit tests + fixtures + smoke)
- `pyarchinitPlugin.py` (two new menu entries — vocab alignment and UUID backfill)
- `requirements.txt` (`s3dgraphy>=0.1.40`)
- `metadata.txt` (`5.0.27-alpha` → `5.1.0-alpha`)
- `pyproject.toml` (NEW: pytest scoping for `tests/sync` + `tests/migrations`)
- `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md` (Reference Doc v0.1 alignment §2.2)
- `docs/superpowers/plans/2026-05-06-phase-1-foundation.md` (NEW: implementation plan)
- `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.{md,docx}` (NEW: rolling English-language partner-facing dev log)

---

## [5.0.27-alpha] - 2026-05-06

### Corretto / Fixed

- **fix(SQLite updater): allineamento dei DB legacy al template canonico `resources/dbfiles/pyarchinit.sqlite`**: la procedura di migrazione dei DB SQLite (`modules/db/sqlite_db_updater.py`) presentava tre divergenze sistematiche dal template, che generavano warning rumorosi nei log e impedivano la ricreazione di `pyarchinit_us_view` su DB di scavo storici (es. `pyarchinitcs_SCHEDE2024.sqlite`). (1) Definizione di `pyarchinit_us_view` referenziava `us_table.quota_max`, `us_table.quota_min` e `us_table.piante` — colonne che non esistono né nel template né nei DB utente. La verifica post-creazione falliva con `ATTENZIONE: Verifica fallita per pyarchinit_us_view: no such column: us_table.quota_max`. Sostituite con le quattro colonne canoniche `quota_max_abs/quota_max_rel/quota_min_abs/quota_min_rel` presenti nel template; rimosso `piante` (codice morto). (2) `views_to_fix` includeva `pyarchinit_quote`, `pyarchinit_quote_usm`, `pyunitastratigrafiche` e `pyunitastratigrafiche_usm` come VIEW, ma nel template canonico questi sono **TABELLE** con schema proprio (gid AUTOINCREMENT, geometria registrata su Spatialite). La migrazione tentava `DROP VIEW IF EXISTS` (no-op su una tabella) seguito da `CREATE VIEW` (fallisce con `use DROP TABLE to delete table X`), generando quattro warning per ogni avvio. Le quattro voci sono state rimosse da `views_to_fix`: queste tabelle restano sotto il governo di `_check_and_restore_backup_tables` e dei meccanismi di registrazione Spatialite. (3) Otto colonne stringa erano dichiarate `INT`/`INTEGER` in DB legacy ma il template le definisce `TEXT`: `us_table.us`, `inventario_materiali_table.area`/`us`, `campioni_table.us`, `pyarchinit_quote{,_usm}.area_q`/`us_q`. Le JOIN con `pyunitastratigrafiche.*_s` (TEXT) silenziosamente non matchavano per row con valori non puramente numerici. Aggiunto rilevamento in `needs_update()` per forzare la migrazione, e nuovo helper `_fix_column_to_text()` che fa un rebuild atomico (rename → recreate → copy → drop) preservando trigger e indici utente. Il rebuild usa `PRAGMA legacy_alter_table=ON` per aggirare il trigger Spatialite `ISO_metadata_reference_row_id_value_insert` che su SQLite 3.25+ rompe il RENAME a causa di `no such column: rowid` durante la ri-parsificazione automatica delle trigger body. / **fix(SQLite updater): align legacy DBs to the canonical template `resources/dbfiles/pyarchinit.sqlite`**: the SQLite migration (`modules/db/sqlite_db_updater.py`) had three systematic divergences from the template that produced noisy log warnings and prevented `pyarchinit_us_view` from being recreated on historical excavation DBs (e.g. `pyarchinitcs_SCHEDE2024.sqlite`). (1) The `pyarchinit_us_view` definition referenced `us_table.quota_max`, `us_table.quota_min` and `us_table.piante` — columns that exist neither in the template nor in user DBs. Post-creation verification failed with `ATTENZIONE: Verifica fallita per pyarchinit_us_view: no such column: us_table.quota_max`. Replaced with the four canonical `quota_max_abs/quota_max_rel/quota_min_abs/quota_min_rel` columns present in the template; removed `piante` (dead code). (2) `views_to_fix` included `pyarchinit_quote`, `pyarchinit_quote_usm`, `pyunitastratigrafiche` and `pyunitastratigrafiche_usm` as VIEWS, but in the canonical template these are **TABLES** with their own schema (gid AUTOINCREMENT, Spatialite-registered geometry). The migration attempted `DROP VIEW IF EXISTS` (no-op on a table) followed by `CREATE VIEW` (fails with `use DROP TABLE to delete table X`), producing four warnings on every start. The four entries were removed from `views_to_fix`: these tables remain governed by `_check_and_restore_backup_tables` and Spatialite registration paths. (3) Eight string columns were declared `INT`/`INTEGER` in legacy DBs but the template defines them as `TEXT`: `us_table.us`, `inventario_materiali_table.area`/`us`, `campioni_table.us`, `pyarchinit_quote{,_usm}.area_q`/`us_q`. JOINs against `pyunitastratigrafiche.*_s` (TEXT) silently failed to match for rows with non-purely-numeric values. Added detection in `needs_update()` to force the migration, and a new `_fix_column_to_text()` helper that performs an atomic rebuild (rename → recreate → copy → drop) preserving user triggers and indexes. The rebuild uses `PRAGMA legacy_alter_table=ON` to bypass the Spatialite `ISO_metadata_reference_row_id_value_insert` trigger which on SQLite 3.25+ breaks RENAME with `no such column: rowid` during automatic trigger-body reparsing.

### File modificati / Modified files
- `modules/db/sqlite_db_updater.py` (`import re`; `needs_update()` extended with column-type mismatch detection at module-level list `columns_must_be_text`; `fix_field_types_in_base_tables()` coerces 8 columns to TEXT via the same list; new `_fix_column_to_text()` helper with trigger/index preservation and `PRAGMA legacy_alter_table=ON`; `views_to_fix` cleaned of the four spurious view definitions; `pyarchinit_us_view` SQL aligned with the template — `quota_max_abs`/`quota_max_rel`/`quota_min_abs`/`quota_min_rel`; `piante` reference removed)
- `metadata.txt` (version 5.0.26-alpha → 5.0.27-alpha; changelog updated; legacy 5.0.25-alpha entry backfilled for completeness)

---

## [5.0.26-alpha] - 2026-04-30

### Aggiunto / Added

- **feat(LLM): Supporto unificato per Ollama e LM Studio accanto a OpenAI/Anthropic**: introdotto un layer centrale di astrazione per tutti i provider LLM. L'utente può ora scegliere il provider e il modello in ogni dialog AI di pyArchInit (Generatore Report, RAG Query, Text2SQL, Skatch GPT US, Skatch GPT Inv. Materiali). Per i provider locali (Ollama, LM Studio) i modelli **caricati** vengono auto-scoperti via `/v1/models` (LM Studio) e `/api/tags` (Ollama) e popolati automaticamente nel combo; per LM Studio si interroga anche l'endpoint nativo `/api/v0/models` per filtrare ai soli modelli con `state: "loaded"` e si striscia il suffisso d'istanza `:N`. Per i modelli vision (Skatch GPT) è disponibile un filtro che mantiene solo i modelli multimodali. Discovery degli embedding model gestita separatamente (`/api/v0/models` filtrato a `type=embeddings`) con fallback automatico a OpenAI cloud quando il server locale non ha un embedding model caricato. La selezione provider+modello+API key viene persistita per scope in `QSettings` (uno scope per dialog), così ogni feature ricorda la propria configurazione. / **feat(LLM): Unified support for Ollama and LM Studio alongside OpenAI/Anthropic**: introduced a central abstraction layer for all LLM providers. The user can now pick provider and model in every pyArchInit AI dialog (Report Generator, RAG Query, Text2SQL, Skatch GPT US, Skatch GPT Inv. Materials). For local providers (Ollama, LM Studio) the **loaded** models are auto-discovered via `/v1/models` (LM Studio) and `/api/tags` (Ollama) and populated in the combo; for LM Studio the native `/api/v0/models` endpoint is also queried to filter to models with `state: "loaded"` and strip the instance suffix `:N`. For vision models (Skatch GPT) a filter keeps only multimodal models. Embedding model discovery is handled separately (`/api/v0/models` filtered to `type=embeddings`) with automatic fallback to OpenAI cloud when no embedding model is loaded on the local server. The provider+model+API key selection is persisted per scope in `QSettings` (one scope per dialog), so each feature remembers its own configuration.

### Corretto / Fixed

- **fix CRITICAL(RAG Query): client OpenAI streaming non ereditava `base_url` da LangChain**: in `RAGQueryWorker.SimpleGPT5Wrapper.invoke`, quando `enable_streaming=True`, veniva creato un nuovo client `OpenAI(api_key=...)` **senza** `base_url`. Anche se l'utente aveva selezionato Ollama o LM Studio nel widget, lo streaming finiva sempre su `api.openai.com` con il model id locale (es. `openai/gpt-oss-20b`), generando `400 'invalid model ID'` (formato OpenAI cloud con `code: null, param: null` — diverso da LM Studio che usa `{"error": "stringa"}`). Risolto leggendo `self.llm.openai_api_base` e passandolo come `base_url` al nuovo client. Aggiunto anche logging diagnostico in `RAGQueryWorker.run()` (`[AI Query] provider=... chat_url=... chat_model=... embed_path=...`) e wrap dei call FAISS embeddings con annotazione del contesto, così future regressioni di base_url sono identificabili senza dover indovinare. / **fix CRITICAL(RAG Query): streaming OpenAI client did not inherit `base_url` from LangChain**: in `RAGQueryWorker.SimpleGPT5Wrapper.invoke`, when `enable_streaming=True`, a fresh `OpenAI(api_key=...)` client was created **without** `base_url`. Even if the user picked Ollama or LM Studio in the widget, streaming always hit `api.openai.com` with the local model id (e.g. `openai/gpt-oss-20b`), causing `400 'invalid model ID'` (OpenAI cloud shape with `code: null, param: null` — different from LM Studio which uses `{"error": "string"}`). Fixed by reading `self.llm.openai_api_base` and passing it as `base_url` to the new client. Also added diagnostic logging in `RAGQueryWorker.run()` (`[AI Query] provider=... chat_url=... chat_model=... embed_path=...`) and wrapped FAISS embeddings calls with context annotation, so future base_url regressions are identifiable without guessing.

- **fix(RAGQueryWorker): `_thumb_path` non inizializzato dopo refactor LLM**: l'aggiunta dei nuovi metodi `_effective_config` / `_get_embeddings` aveva inserito le 3 righe finali di `__init__` (init `_thumb_path`, `_thumb_resize`, `_load_media_paths()`) **fuori** dal corpo del metodo come dead code. Risultato: `AttributeError: 'RAGQueryWorker' object has no attribute '_thumb_path'` al primo accesso. Spostate dentro `__init__`. / **fix(RAGQueryWorker): `_thumb_path` not initialized after LLM refactor**: adding the new `_effective_config` / `_get_embeddings` methods had moved the trailing 3 lines of `__init__` (`_thumb_path`, `_thumb_resize`, `_load_media_paths()` init) **outside** the method body as dead code. Result: `AttributeError: 'RAGQueryWorker' object has no attribute '_thumb_path'` on first access. Moved back inside `__init__`.

- **fix(LM Studio): auto-pick del primo modello caricato quando il `saved_model` non è più disponibile**: il widget salvava in `QSettings` il model id corrente (es. `openai/gpt-oss-20b:2`); al successivo avvio, se il server aveva ricaricato istanze diverse, il `saved_model` non era nella lista discovered e il combo lo ripristinava via `setEditText(...)` — ma poi le chiamate a quel model id davano `400 No models loaded`. Ora se il `saved_model` non matcha la lista corrente, il widget seleziona automaticamente il primo modello caricato e segnala il fallback nella status bar. / **fix(LM Studio): auto-pick first loaded model when `saved_model` is no longer available**: the widget saved the current model id (e.g. `openai/gpt-oss-20b:2`) in `QSettings`; on next start, if the server had reloaded different instances, the `saved_model` was not in the discovered list and the combo restored it via `setEditText(...)` — but then chat calls to that model id returned `400 No models loaded`. Now if `saved_model` doesn't match the current list, the widget auto-picks the first loaded model and reports the fallback in the status bar.

- **fix(SQLite updater): `needs_update()` ora rileva la colonna mancante `inventario_materiali_table.sub_inv`**: l'updater per `sub_inv` esisteva già in `update_other_tables()` ma `needs_update()` non lo controllava, quindi i database SQLite preesistenti (tipo `pyarchinit_DB_folder/pyarchinit_db.sqlite`) non innescavano il flusso di aggiornamento. Conseguenza: il RAG (e qualsiasi altra query SQLAlchemy che caricasse `INVENTARIO_MATERIALI`) crashava con `OperationalError: no such column: inventario_materiali_table.sub_inv`. Aggiunto check per la colonna `sub_inv` in `needs_update()`. Al prossimo avvio QGIS, i DB legacy mostreranno il dialog "Database vecchio, aggiornare?" e l'updater aggiungerà automaticamente la colonna (con backup). / **fix(SQLite updater): `needs_update()` now detects the missing `inventario_materiali_table.sub_inv` column**: the updater for `sub_inv` already existed in `update_other_tables()` but `needs_update()` did not check it, so pre-existing SQLite databases (like `pyarchinit_DB_folder/pyarchinit_db.sqlite`) didn't trigger the update flow. Result: RAG (and any SQLAlchemy query loading `INVENTARIO_MATERIALI`) crashed with `OperationalError: no such column: inventario_materiali_table.sub_inv`. Added a check for `sub_inv` in `needs_update()`. On next QGIS start, legacy DBs will show the "Old database, update?" dialog and the updater will add the column automatically (with backup).

### File modificati / Modified files
- `modules/utility/llm_providers.py` (NEW: `LLMProvider`, `LLMConfig`, `LLMProviderManager` con discovery `/v1/models` + `/api/v0/models`, `discover_embedding_models`, `stream_chat`/`chat` unificati, persistenza `QSettings`, gestione API key per file `~/pyarchinit/bin/{gpt,claude}_api_key.txt`)
- `modules/utility/llm_selector_widget.py` (NEW: combo provider+modello, discovery asincrona, vision-only filter, test connessione, persistenza per scope)
- `modules/utility/report_generator.py` (`generate_report(prompt, LLMConfig)` provider-aware; `generate_report_with_openai` mantenuto come alias backward-compat)
- `modules/utility/askgpt.py` (`ask_with_config(prompt, LLMConfig)`; `ask_gpt(prompt, apikey, model)` mantenuto come wrapper)
- `modules/utility/textTosql.py` (sostituiti i radio button OpenAI/Anthropic/Ollama con `LLMSelectorWidget(scope="text2sql")`; nuovi `MakeSQL.make_query` / `MakeSQL.explain_query` provider-agnostic)
- `modules/utility/skatch_gpt_US.py` (sostituito `model_selector` QComboBox con `LLMSelectorWidget(scope="skatch_us", vision_only=True)`; nuovo `ask_with_llm(prompt, file_path, config, is_image)` che gestisce sia OpenAI image_url che Anthropic source.base64)
- `modules/utility/skatch_gpt_INVMAT.py` (idem, scope="skatch_invmat")
- `tabs/US_USM.py` (`ReportGeneratorDialog` ora ha sezione "Provider AI" con `LLMSelectorWidget(scope="us_report")`; `RAGQueryDialog` usa `LLMSelectorWidget(scope="rag_query")` al posto del QComboBox OpenAI-only; `GenerateReportThread` accetta `llm_config=` con helper `_make_chat_llm`/`_get_embeddings`/`_provider_chat_completion`; `RAGQueryWorker` accetta `llm_config=` con helper analoghi; tutte le `OpenAI(api_key=self.api_key)` interne ora rispettano `base_url`; embedding fallback a OpenAI cloud quando `discover_embedding_models()` torna vuoto; FAISS embeddings calls wrapped con annotazione del contesto)
- `modules/db/sqlite_db_updater.py` (`needs_update()` controlla `sub_inv` su `inventario_materiali_table`)
- `metadata.txt` (version 5.0.25-alpha → 5.0.26-alpha)

---

## [5.0.25-alpha] - 2026-04-28

### Corretto / Fixed

- **fix CRITICAL(installer macOS): Nuovi utenti Mac vedevano "Sorgente Dati non Valida" al primo avvio**: `PackageManager.install()` su Darwin usava `sys.executable` come ultimo fallback, ma dentro QGIS in esecuzione `sys.executable` è il binario dell'app QGIS (`/Applications/QGIS.app/Contents/MacOS/QGIS`), non un interprete Python. Quando i candidati Python precedenti fallivano (per timeout di rete o path mancanti su QGIS 4.x), `subprocess.run([qgis_binary, "-m", "pip", "install", "<pkg>"])` lanciava una *seconda istanza di QGIS* che interpretava il package spec come percorso file → "Sorgente Dati non Valida". Risolto: (1) rimosso `sys.executable` dal fallback su macOS, (2) aggiunti path bundle QGIS 4.x (`Contents/Resources/python/bin/`, `Contents/Frameworks/Python.framework/Versions/Current/bin/`) e nomi multi-versione (python3.9–3.13), (3) aggiunta validazione `python -c 'import sys; print(sys.version_info[0])'` con timeout 5s prima di usare ciascun candidato — qualsiasi binario non-Python viene scartato silenziosamente. / **fix CRITICAL(installer macOS): New Mac users hit "Sorgente Dati non Valida" on first launch**: `PackageManager.install()` on Darwin used `sys.executable` as last-resort fallback, but inside a running QGIS, `sys.executable` is the QGIS app binary (`/Applications/QGIS.app/Contents/MacOS/QGIS`), not a Python interpreter. When prior Python candidates failed (network timeout or missing paths on QGIS 4.x), `subprocess.run([qgis_binary, "-m", "pip", "install", "<pkg>"])` launched a *second QGIS instance* that interpreted the package spec as a file path → "Sorgente Dati non Valida" / "Invalid Data Source". Fixed: (1) removed `sys.executable` from macOS fallback, (2) added QGIS 4.x bundle paths (`Contents/Resources/python/bin/`, `Contents/Frameworks/Python.framework/Versions/Current/bin/`) and multi-version names (python3.9–3.13), (3) added `python -c 'import sys; print(sys.version_info[0])'` probe with 5s timeout before using each candidate — any non-Python binary is silently discarded.

### File modificati / Modified files
- `__init__.py` (`PackageManager.install` Darwin branch, lines 336–397: candidate discovery + interpreter probe)
- `metadata.txt` (version 5.0.24-alpha → 5.0.25-alpha)

---

## [5.0.24-alpha] - 2026-04-27

### Corretto / Fixed

- **fix CRITICAL(loader): Parser requirements.txt ora gestisce PEP 508 environment markers**: Il bump 5.0.22 aveva introdotto `package>=X; python_version<"3.10"` in `requirements.txt` ma `PackageManager.check_required_packages()` non sapeva interpretare il `;`. Conseguenza: il plugin **non si caricava** con `ValueError: invalid literal for int() with base 10: '4; python_version'`. Aggiunto blocco che usa `packaging.markers.Marker(...).evaluate()` per: (1) saltare le righe il cui marker non si applica all'ambiente corrente, (2) processare solo il version spec residuo. Compatibile con righe legacy senza marker. / **fix CRITICAL(loader): requirements.txt parser now handles PEP 508 environment markers**: The 5.0.22 bump introduced `package>=X; python_version<"3.10"` in `requirements.txt` but `PackageManager.check_required_packages()` didn't know about `;`. Result: the plugin **failed to load** with `ValueError: invalid literal for int() with base 10: '4; python_version'`. Added block using `packaging.markers.Marker(...).evaluate()` to: (1) skip lines whose marker doesn't apply to the current environment, (2) process only the residual version spec. Compatible with legacy non-marker lines.

### File modificati / Modified files
- `__init__.py` (`PackageManager.check_required_packages` + marker handling at lines 470-481)
- `metadata.txt` (version 5.0.23 → 5.0.24-alpha)

---

## [5.0.23-alpha] - 2026-04-27

### Corretto / Fixed

- **fix(deps): Floor condizionali per nltk/requests/PyMuPDF**: Anche le patch di sicurezza per `nltk` (3.9.3+), `requests` (2.33.0+) e `PyMuPDF` (1.26.6+) richiedono Python ≥3.10, non solo le librerie langchain. Estesa la strategia env-marker anche a questi pacchetti. Per Python 3.9 (QGIS 3.x): `nltk>=3.8` (nessun fix possibile a monte — 6 CVE residue), `requests>=2.32.4` (fixa solo `.netrc` leak #9), `PyMuPDF>=1.26.5` (nessun fix possibile, 1.26.7 è 3.10+). Per Python ≥3.10: floor pieni. / **fix(deps): Conditional floors for nltk/requests/PyMuPDF**: Security patches for `nltk` (3.9.3+), `requests` (2.33.0+) and `PyMuPDF` (1.26.6+) also require Python ≥3.10, not just LangChain. Extended env-marker strategy to these packages. For Python 3.9 (QGIS 3.x): `nltk>=3.8` (no upstream fix — 6 residual CVEs), `requests>=2.32.4` (closes only .netrc leak #9), `PyMuPDF>=1.26.5` (no fix possible, 1.26.7 is 3.10+). For Python ≥3.10: full floors.

### Coverage CVE finale per Python 3.9 (QGIS 3.x)

| CVE | Pacchetto/Floor | Status |
|---|---|---|
| #14 critical (langchain-core serialization injection) | langchain-core 0.3.84 | ✅ Closed |
| #16 critical (nltk zip slip CVE-2026-0846) | nltk 3.9.4 | ❌ Residual (Python 3.9 only) |
| #28 high (nltk arbitrary file read) | nltk 3.9.3 | ❌ Residual |
| #19 high (nltk remote shutdown) | nltk 3.9.4 | ❌ Residual |
| #20 high (nltk downloader path traversal) | no upstream patch | ❌ Residual |
| #23 high (langchain-core load_prompt path traversal) | langchain-core 1.2.22 | ❌ Residual (requires Python 3.10) |
| #13 high (langchain-core template injection) | langchain-core 0.3.80 | ✅ Closed |
| #12 high (langchain-text-splitters XXE) | langchain-text-splitters 0.3.9 | ✅ Closed |
| #10 high (langchain-community XXE) | langchain-community 0.3.27 | ✅ Closed |
| #18 medium (nltk XSS) | nltk 3.9.4 | ❌ Residual |
| #17 medium (nltk JSONTaggedDecoder recursion) | no upstream patch | ❌ Residual |
| #24 medium (langchain-core f-string) | langchain-core 0.3.84 | ✅ Closed |
| #26 medium (langchain-text-splitters SSRF redirect) | langchain-text-splitters 1.1.2 | ❌ Residual (requires Python 3.10) |
| #25 medium (langsmith streaming bypass) | langsmith 0.7.31 | ❌ Residual (requires Python 3.10) |
| #22 medium (requests temp file) | requests 2.33.0 | ❌ Residual (requires Python 3.10) |
| #9 medium (requests .netrc) | requests 2.32.4 | ✅ Closed |
| #21 medium (PyMuPDF path traversal) | PyMuPDF 1.26.7 | ❌ Residual (requires Python 3.10) |
| #15 low (langchain-core SSRF image_url) | langchain-core 1.2.11 | ❌ Residual (requires Python 3.10) |
| #27 low (langchain-openai SSRF token counting) | langchain-openai 1.1.14 | ❌ Residual (requires Python 3.10) |

**Su Python 3.9: 5 CVE chiusi, 14 residue (di cui 12 fixabili solo passando a QGIS 4.x con Python 3.10+, 2 senza patch upstream).**
**Su Python 3.10+: 17 CVE chiusi, 2 residue (no upstream patch nltk).**

### Note operative
- **Pacchetti aggiornati manualmente in `ext_libs`** del repo locale dell'utente per il QGIS 3.42 (Python 3.9): `requests 2.32.5`, `langchain 0.3.28`, `langchain-community 0.3.31`, `langchain-core 0.3.84`, `langchain-text-splitters 0.3.11`, `langsmith 0.4.37`. Questo evita il dialog "Sorgente Dati non Valida" al prossimo avvio QGIS perché tutti i floor sono soddisfatti.
- numpy 2.0.2 entrato in `ext_libs` durante l'install è stato rimosso manualmente (CLAUDE.md richiede numpy 1.26.4 strict per QGIS — è in `QGIS_PROTECTED_PACKAGES`).

---

## [5.0.22-alpha] - 2026-04-27

### Corretto / Fixed

- **fix(deps): Compatibilità Python 3.9 (QGIS 3.x) tramite environment markers in requirements.txt**: Il bump 5.0.21 a `langchain>=1.2` rompeva l'installazione su QGIS 3.x macOS che usa il Python 3.9 bundled (langchain 1.x richiede Python >=3.10). Ogni dipendenza langchain ora ha due righe con marker condizionale: `package>=0.3.X; python_version<"3.10"` e `package>=1.x; python_version>="3.10"`. Pip selezionerà automaticamente la riga giusta in base al Python in uso. / **fix(deps): Python 3.9 compatibility (QGIS 3.x) via environment markers in requirements.txt**: The 5.0.21 bump to `langchain>=1.2` broke installs on QGIS 3.x macOS which uses the bundled Python 3.9 (langchain 1.x requires Python >=3.10). Each langchain dependency now has two lines with conditional markers: `package>=0.3.X; python_version<"3.10"` and `package>=1.x; python_version>="3.10"`. Pip will automatically pick the right line based on Python in use.

### Coverage CVE per Python version

**Python 3.9 (QGIS 3.x bundled)** — chiude 7 dei 17 CVE patchabili:
- nltk 3.9.4, requests 2.33.0, PyMuPDF 1.26.7 (5 CVE chiusi)
- langchain-core 0.3.84 (3 CVE chiusi: #14, #13, #24)
- langchain-text-splitters 0.3.9 (1 CVE chiuso: #12)
- langchain-community 0.3.27 (1 CVE chiuso: #10)
- **Residui Python 3.9-only** (richiedono upgrade a QGIS 4.x): #23, #15 (langchain-core), #26 (langchain-text-splitters), #27 (langchain-openai), #25 (langsmith)

**Python 3.10+ (QGIS 4.x)** — chiude tutti i 17 CVE patchabili.

### Sintomi precedenti (5.0.21)
- Su QGIS 3.x macOS: dialog "Sorgente Dati non Valida: /langchain>=1.2.0" e simili al prossimo avvio QGIS, perché pip falliva l'install della linea 1.x su Python 3.9 e QGIS interpretava le stringhe come tentativi di caricamento layer.

### File modificati / Modified files
- `requirements.txt` (env markers per langchain ecosystem)
- `metadata.txt` (version 5.0.21 → 5.0.22-alpha + changelog entry)

---

## [5.0.21-alpha] - 2026-04-27

### Sicurezza / Security

- **security(deps): Risolti 17 dei 19 CVE Dependabot tramite bump dei floor `>=` in `requirements.txt`**: 2 critici, 6 high, 7 medium, 2 low. Le 2 alert residue (`nltk` Downloader Path Traversal #20 e `JSONTaggedDecoder` recursion #17) non hanno patch upstream — tracking aperto. Rischio reale per pyarchinit (plugin offline dentro QGIS) limitato a vettori specifici: file PDF/DOCX malevoli (PyMuPDF), URL inseriti in feature LangChain che fanno fetch (SSRF), corpus NLTK da fonti non verificate (zip slip). Bump effettuati: `nltk>=3.9.4` (era 3.8), `requests>=2.33.0` (era 2.28), `PyMuPDF>=1.26.7` (era 1.23), `langchain>=1.2.0`, `langchain-community>=0.4.0`, `langchain-core>=1.2.22`, `langchain-openai>=1.1.14`, `langchain-anthropic>=1.0.0`, `langchain-text-splitters>=1.1.2`, `langsmith>=0.7.31` (tutti era 0.3). / **security(deps): Resolved 17 of 19 Dependabot CVEs by bumping `>=` floors in `requirements.txt`**: 2 critical, 6 high, 7 medium, 2 low. The 2 residual alerts (`nltk` Downloader Path Traversal #20 and `JSONTaggedDecoder` recursion #17) have no upstream patch — open tracking. Real risk for pyarchinit (offline plugin inside QGIS) is limited to specific vectors: malicious PDF/DOCX files (PyMuPDF), URLs entered in LangChain features that fetch (SSRF), NLTK corpora from unverified sources (zip slip).

### CVE chiusi / Closed CVEs

- **CRITICAL** — `nltk` Zip Slip (CVE-2026-0846, GHSA-h8wq-7xc4-p3qx) → patched ≥3.9.3
- **CRITICAL** — `langchain-core` serialization injection (secret extraction in dump/load) → patched ≥0.3.81 / ≥1.2.22
- **HIGH** — `nltk` Arbitrary File Read in `nltk.util.filestring()` → patched ≥3.9.3
- **HIGH** — `nltk` Unauthenticated remote shutdown in `nltk.app.wordnet_app` → patched ≥3.9.4
- **HIGH** — `langchain-core` Path Traversal in `load_prompt` → patched ≥1.2.22
- **HIGH** — `langchain-core` Template Injection via attribute access → patched ≥0.3.80 / ≥1.2.22
- **HIGH** — `langchain-text-splitters` XXE attacks → patched ≥0.3.9 / ≥1.1.2
- **HIGH** — `langchain-community` XXE → patched ≥0.3.27
- **MEDIUM** — `nltk` XSS in pagine generate → patched ≥3.9.4
- **MEDIUM** — `langchain-core` incomplete f-string validation → patched ≥0.3.84 / ≥1.2.22
- **MEDIUM** — `langchain-text-splitters` SSRF in `HTMLHeaderTextSplitter.split_text_from_url` → patched ≥1.1.2
- **MEDIUM** — `langsmith` Streaming token events bypass output redaction → patched ≥0.7.31
- **MEDIUM** — `requests` Insecure Temp File Reuse in `extract_zipped_paths()` → patched ≥2.33.0
- **MEDIUM** — `requests` `.netrc` credentials leak via malicious URLs → patched ≥2.32.4
- **MEDIUM** — `PyMuPDF` path traversal in `_main_.py` → patched ≥1.26.7
- **LOW** — `langchain-openai` SSRF protection bypass via DNS in image token counting → patched ≥1.1.14
- **LOW** — `langchain-core` SSRF via image_url in `ChatOpenAI.get_num_tokens` → patched ≥1.2.11

### Residui / Residual (no upstream patch)
- `nltk` Downloader Path Traversal (file overwrite) — alert #20
- `nltk` `JSONTaggedDecoder.decode()` unbounded recursion — alert #17

### File modificati / Modified files
- `requirements.txt` (10 floor bumps + commenti CVE inline)
- `metadata.txt` (version 5.0.20 → 5.0.21-alpha + changelog entry)

### Note operative / Operational notes
- Il bump è solo nel manifest (`>=` floor). Utenti con installazioni esistenti devono lanciare `pip install -r requirements.txt --upgrade` (o usare `python scripts/modules_installer.py`) per applicare gli aggiornamenti.
- LangChain ecosystem migrato dal canale 0.3.x al canale 1.x. API potenzialmente incompatibili in alcuni punti — testare le feature AI dopo l'upgrade. / LangChain ecosystem moved from 0.3.x to 1.x channel. APIs may have minor incompatibilities — test AI features after upgrade.

---

## [5.0.20-alpha] - 2026-04-27

### Aggiunto / Added

- **feat(ai): Migrazione modelli OpenAI a strategia mista gpt-5.4 / gpt-5.5**: Aggiornati 21 riferimenti in 11 file. Le chiamate streaming e analisi documenti/immagini in `skatch_gpt_INVMAT.py` e `skatch_gpt_US.py` (6 call sites) usano `gpt-5.5`. I punti che richiedono determinismo (`textTosql.py` × 2, `auto_translate_ts.py`, `translate_ts_complete.py`, `US_USM.py:6213` RAG factual) restano su `gpt-5.4` con `temperature` custom (0.1 / 0.2 / 0.3) perché `gpt-5.5` accetta solo `temperature=1` di default. `gpt-5.5-mini` non esiste come modello: i 7 riferimenti `gpt-5.4-mini` originali sono stati conservati. / **feat(ai): OpenAI model migration with mixed gpt-5.4 / gpt-5.5 strategy**: Updated 21 references across 11 files. Streaming and document/image analysis calls in `skatch_gpt_INVMAT.py` and `skatch_gpt_US.py` (6 call sites) use `gpt-5.5`. Determinism-critical points (`textTosql.py` × 2, `auto_translate_ts.py`, `translate_ts_complete.py`, `US_USM.py:6213` RAG factual) stay on `gpt-5.4` with custom `temperature` (0.1 / 0.2 / 0.3) because `gpt-5.5` only accepts default `temperature=1`. `gpt-5.5-mini` does not exist as a model: the 7 original `gpt-5.4-mini` references were preserved.

### Corretto / Fixed

- **fix(ai): Rimossi parametri non supportati da chiamate gpt-5.5**: `gpt-5.5` rifiuta sia `temperature` con valori custom (errore 400 `Only the default (1) value is supported`) sia `top_p` (errore 400 `'top_p' is not supported with this model`). Rimossi `temperature=0.5` e `top_p=0.5` dalle 6 call in `skatch_gpt_INVMAT.py` e `skatch_gpt_US.py`. / **fix(ai): Removed unsupported params from gpt-5.5 calls**: `gpt-5.5` rejects both custom `temperature` (400 `Only the default (1) value is supported`) and `top_p` (400 `'top_p' is not supported with this model`). Removed `temperature=0.5` and `top_p=0.5` from 6 calls in `skatch_gpt_INVMAT.py` and `skatch_gpt_US.py`.

- **fix(ai): Logica condizionale temperature in US_USM ChatOpenAI**: La call `ChatOpenAI(...)` a riga 6213 di `US_USM.py` riceve il modello scelto runtime dall'utente (`gpt-5.4-mini` o `gpt-5.5`). Aggiunto check `if not self.model.startswith("gpt-5.5"): kwargs["temperature"]=0.1` per mantenere determinismo solo dove supportato. / **fix(ai): Conditional temperature in US_USM ChatOpenAI**: The `ChatOpenAI(...)` call at line 6213 of `US_USM.py` receives the runtime-chosen model (`gpt-5.4-mini` or `gpt-5.5`). Added check `if not self.model.startswith("gpt-5.5"): kwargs["temperature"]=0.1` to preserve determinism only where supported.

- **fix(scripts): max_tokens → max_completion_tokens in auto_translate_ts.py**: Aggiornato il parametro deprecato per compatibilità con i modelli OpenAI gpt-5.x. / **fix(scripts): max_tokens → max_completion_tokens in auto_translate_ts.py**: Updated deprecated parameter for OpenAI gpt-5.x model compatibility.

- **fix(metadata): Typo accidentale in `metadata.txt`**: Corretto `instalclaude /resumelation` → `installation` nella entry changelog 5.0.8-alpha. / **fix(metadata): Accidental typo in `metadata.txt`**: Fixed `instalclaude /resumelation` → `installation` in the 5.0.8-alpha changelog entry.

### File modificati / Modified files
- `metadata.txt` (version 5.0.8 → 5.0.20-alpha + changelog entry + typo fix)
- `modules/utility/skatch_gpt_INVMAT.py` (3 calls: removed temperature/top_p)
- `modules/utility/skatch_gpt_US.py` (3 calls: removed temperature/top_p)
- `scripts/auto_translate_ts.py` (max_tokens → max_completion_tokens, comment update)
- `tabs/Periodizzazione.py` (model selector: `gpt-5.4` → `gpt-5.5`)
- `tabs/Thesaurus.py` (model selector: `gpt-5.4` → `gpt-5.5`)
- `tabs/US_USM.py` (model selector + conditional temperature for ChatOpenAI)

### Test verificati / Tests verified
- 6 pattern di chiamata API testati live contro OpenAI: streaming `skatch_gpt`, non-streaming `textTosql`, generic `askgpt.py` (entrambi gpt-5.5 e gpt-5.4-mini), vision (`pottery_similarity` con immagine reale), translation script. Tutti PASS.

---

## [5.0.19-alpha] - 2026-04-18

### Aggiunto / Added

- **feat(ui,invmat): Sub-tab in Dati Quantitativi (`_restructure_dati_quantitativi_tab`)**: Il pannello sinistro della tab "Dati quantitativi" (tab_3) aveva "Elementi reperto" e "Misurazioni" impilati verticalmente, difficili da consultare/modificare. Riorganizzato in `QTabWidget` interno con 2 sub-tab ("Elementi reperto" / "Misurazioni"): ogni tabella ora usa l'intera altezza disponibile. Il pannello destro (Forme min/max, Totale, Peso, Diametro orlo, E.v.e.) è preservato identico — tutti i signal Qt auto-connect sui 6 lineEdit restano validi perché il layout genitore è stato spostato come blocco via `removeItem`+`addLayout` invece di ricreare i widget. Wrapping in `QSplitter` orizzontale. Labels localizzate IT/EN/DE + flag idempotenza `tab3._dq_restructured`. / **feat(ui,invmat): Sub-tabs in Dati Quantitativi (`_restructure_dati_quantitativi_tab`)**: The "Dati quantitativi" tab (tab_3) stacked "Elementi reperto" and "Misurazioni" vertically, making them hard to consult/edit. Reorganised into a nested `QTabWidget` with 2 sub-tabs ("Artefact Elements" / "Measurements"): each table now uses the full available height. Right panel (Min/Max shape, Total fragments, Weight, Rim diameter, E.v.e.) preserved identically — Qt auto-connect signals on the 6 lineEdits stay valid because the parent layout was relocated as a block via `removeItem`+`addLayout` instead of recreating widgets. Wrapped in horizontal `QSplitter`. Labels localised IT/EN/DE + idempotence flag.

### Corretto / Fixed

- **fix(db,invmat): Normalizzazione whitespace descrizione (festos2025)**: 1416 record avevano newline, tab o spazi multipli ereditati dalle celle Excel originali, che producevano righe "spezzate" nel form. UPDATE SQL `REGEXP_REPLACE(descrizione, E'[\n\r\t]+', ' ') → ' +' → ' '`. Il parser `parse_to_festos2025.py` ora chiama `_clean_ws()` su ciascun componente prima della concatenazione per evitare regressioni. / **fix(db,invmat): Descrizione whitespace normalization (festos2025)**: 1416 records had newlines, tabs or multi-spaces inherited from original Excel cells, producing broken lines in the form. SQL UPDATE `REGEXP_REPLACE(descrizione, E'[\n\r\t]+', ' ') → ' +' → ' '`. The parser now calls `_clean_ws()` on each component before concatenation to avoid regressions.

- **fix(thesaurus,invmat): Popolamento gap thesaurus (4 campi TMA)**: 12 valori distinti presenti nei dati ma mancanti in `pyarchinit_thesaurus_sigle` sono stati inseriti per lingua `it` (2 tipologie, 2 tipo_reperto, 1 criterio_schedatura, 7 definizioni). Usata INSERT con `NOT EXISTS` e `ON CONFLICT DO NOTHING` per idempotenza. I combobox del form Inventario Materiali ora offrono l'elenco completo delle voci effettivamente usate. / **fix(thesaurus,invmat): Thesaurus gap filling (4 TMA fields)**: 12 distinct values present in data but missing from `pyarchinit_thesaurus_sigle` inserted for language `it` (2 tipologie, 2 tipo_reperto, 1 criterio_schedatura, 7 definizioni). Used INSERT with `NOT EXISTS` + `ON CONFLICT DO NOTHING` for idempotency. Inventario Materiali form combos now offer the complete list of values actually used.

### File modificati / Modified files
- `tabs/Inv_Materiali.py` (`_restructure_dati_quantitativi_tab` + helper `_find_layout_containing`)
- `/Users/enzo/Downloads/parsingra/parse_to_festos2025.py` (`_clean_ws` applicato nei campi descrizione)

### DB festos2025 (thesaurus TMA esteso)
- Popolate anche le tabelle `TMA Materiali Ripetibili` (thesaurus delle schede TMA) per coerenza cross-scheda: `10.10 Categoria` +29 (da MATERIALE), `10.11 Classe` +8 (da CLASSE), `10.12 Precisazione Tipologica` +35 (da TIPO), `10.13 Definizione` +461 (da FORMA), `10.4 cronologia` +18 (da CRONOLOGIA). Totale +551 nuove voci nel thesaurus TMA.
- Parser aggiornato con `THES_MAP` multi-target: ogni campo TMA del form Inv_Materiali ora scrive contemporaneamente nei codici `inventario_materiali_table / 3.x` (lowercase, per combo Inv_Materiali) E nei codici `TMA Materiali Ripetibili / 10.1x` (uppercase, per la scheda TMA).
- Note: nessuna FK tra `inventario_materiali_table` e `periodizzazione_table` — il collegamento via `datazione_reperto` è testuale. La `periodizzazione_table` festos2025 ha gia' 71 record preesistenti.

### DB festos2025
- 1416 record: descrizione normalizzata (no newline/tab/spazi multipli)
- 12 nuove voci thesaurus inserite in `pyarchinit_thesaurus_sigle`: tipo_reperto +2, criterio_schedatura +1, definizione +7, tipo +2
- **Lingua thesaurus consolidata IT (maiuscolo)**: il codice pyarchinit fa match sulla chiave del dict `LANG` che è `'IT'` maiuscolo (i values `['it_IT','IT','it','IT_IT']` servono solo a mappare la locale QGIS sulla chiave). Il parser originale inseriva `'it'` minuscolo, quindi il form non trovava le voci. UPDATE: 636 record `'it'` → `'IT'` (0 conflitti con 248 record `'IT'` preesistenti). Parser aggiornato per scrivere `'IT'` in futuro.
- **Rimappatura `tipologia_sigla` sui codici ufficiali pyarchinit**: il form popola i combobox cercando per codice numerico, non per nome-stringa. `tipo_reperto` -> `3.1`, `criterio_schedatura` -> `3.2`, `definizione` -> `3.3`, `tipo` -> `10.12` + `nome_tabella='tma_materiali_ripetibili'` (da `inventario_materiali_table`). Prima rimossi 94 duplicati sigla_estesa già presenti sotto i codici ufficiali (7 + 15 + 72), poi UPDATE di 30+11+463+38 record con sigle generate automaticamente (`MACC1xx`, `CLSS1xx`, `DEF1xxx`, `TIPO1xx`). Adesso i 4 combobox del form ("Tipo reperto", "Classe materiale", "Definizione", "Tipologia") elencano tutti i valori dell'Excel.

---

## [5.0.18-alpha] - 2026-04-17

### Corretto / Fixed

- **fix(ui,invmat): Posizionamento corretto `lineEdit_sub_inv` accanto a `lineEdit_num_inv`**: La precedente iniezione via `QGridLayout.removeWidget`+`addWidget(r, c+1)` finiva nel fallback e il widget compariva in basso a sinistra. Riscritto `_inject_sub_inv_field` per usare un wrapper `QWidget` con `QHBoxLayout [num_inv | sub_inv]` e `QLayout.replaceWidget` sul layout genitore: funziona con qualsiasi tipo di layout (QGridLayout, QFormLayout, QHBoxLayout) e il widget appare immediatamente a destra del Nr. Inventario come richiesto dall'utente. / **fix(ui,invmat): Correct positioning of `lineEdit_sub_inv` next to `lineEdit_num_inv`**: The previous injection via `QGridLayout.removeWidget`+`addWidget(r, c+1)` hit the fallback and the widget appeared bottom-left. Rewrote `_inject_sub_inv_field` to use a wrapper `QWidget` with `QHBoxLayout [num_inv | sub_inv]` and `QLayout.replaceWidget` on the parent layout: works with any layout kind (QGridLayout, QFormLayout, QHBoxLayout) and the widget now appears immediately to the right of Nr. Inventario as requested.

- **fix(ui,invmat): Elimina visualizzazione letterale `"None"` nei campi combo/text**: In `fill_fields` numerose chiamate `setEditText(str(record.campo))` producevano la stringa letterale `"None"` quando il campo DB era NULL. Introdotto helper `_safe_str(v)` che restituisce `""` per `None`/`str(None)` e wrappato le 11 chiamate interessate (`tipo_reperto`, `criterio_schedatura`, `definizione`, `descrizione`, `lavato`, `luogo_conservazione`, `stato_conservazione`, `datazione_reperto`, `rivestimento`, `corpo_ceramico`, `tipo`, `repertato`, `diagnostico`, `tipo_contenitore`, `struttura`, `years`). / **fix(ui,invmat): Remove literal `"None"` from combo/text fields**: `fill_fields` had many `setEditText(str(record.field))` calls that produced the literal string `"None"` when the DB value was NULL. Added `_safe_str(v)` helper returning `""` for `None`/`str(None)` and wrapped the 11 affected call sites.

- **fix(import,invmat): Formato `rif_biblio` compatibile con `tableWidget_rif_biblio` (4 colonne)**: il parser Festòs produceva `rif_biblio=['testo']` ma il widget si aspetta `[[autore, anno, titolo, pag]]` (4 colonne). Aggiornato `build_rif_biblio` in `parse_to_festos2025.py` per emettere `[['', '', testo, '']]` e skippare placeholder `No/Sì/-/na/none/yes`. Applicato UPDATE al DB `festos2025` che ha riformattato 22 record reali e azzerato 2068 placeholder, lasciando 11 riferimenti bibliografici effettivi. / **fix(import,invmat): `rif_biblio` format compatible with `tableWidget_rif_biblio` (4 columns)**: Festòs parser was producing `rif_biblio=['text']` but the widget expects `[[author, year, title, page]]`. Updated `build_rif_biblio` to emit `[['', '', text, '']]` and skip placeholders. Applied UPDATE to `festos2025` DB: 22 real records reformatted, 2068 placeholders cleared, 11 actual bibliographic references retained.

### Aggiunto / Added

- **feat(ui,invmat): Sub-tab in Quantificazioni per migliore visibilita' (`stats_subtabs`)**: Il pannello sinistro della tab Quantificazioni impilava verticalmente "Riepilogo Generale", "Statistiche Quantitative" e "Report AI Descrittivo" richiedendo scroll per consultarli su schermi piccoli. Sostituiti i 3 `QGroupBox` con un `QTabWidget` interno (sub-tab "Riepilogo" / "Statistiche" / "Report AI") — ciascuna sezione ora ha spazio pieno e il grafico a destra resta sempre visibile. Label localizzate IT/DE/EN. / **feat(ui,invmat): Sub-tabs in Quantificazioni for better visibility (`stats_subtabs`)**: The Quantificazioni tab's left panel stacked "General Summary", "Quantitative Statistics" and "AI Report" vertically, requiring scroll on small screens. Replaced the 3 `QGroupBox` with a nested `QTabWidget` (sub-tabs "Summary" / "Statistics" / "AI Report") — each section gets full space and the chart on the right stays always visible. Labels localised IT/DE/EN.

### File modificati / Modified files
- `tabs/Inv_Materiali.py` (riscrittura `_inject_sub_inv_field` con wrapper+replaceWidget; helper `_safe_str`; 11 siti `setEditText` aggiornati; sub-tab `stats_subtabs` in setup Quantificazioni)
- `/Users/enzo/Downloads/parsingra/parse_to_festos2025.py` (build_rif_biblio formato 4 colonne + skip placeholder)

### DB festos2025
- UPDATE rif_biblio: 2057 `['No']` -> `''`, 22 `[testo]` -> `[['','',testo,'']]`, 11 `['Sì']` -> `''`. Risultato: 11 riferimenti reali, il resto vuoto.

---

## [5.0.17-alpha] - 2026-04-17

### Aggiunto / Added

- **feat(db,invmat): Colonna `sub_inv` per sub-inventario opzionale in `inventario_materiali_table`**: Nuova colonna `VARCHAR(8)` che affianca `numero_inventario` / `n_reperto` (entrambi `bigint`) per catturare suffissi tipo `"a"`, `"b1"`, `"bis"` senza encoding numerico artificioso: il numero d'inventario rimane intero puro (sort numerico, referenze FK logiche preservate) e la variante del sub-frammento è in una colonna dedicata. I vincoli UNIQUE `ID_invmat_unico` e `idx_n_reperto` sono stati estesi a `(sito, numero_inventario, sub_inv)` e `(sito, n_reperto, sub_inv)` rispettivamente, così `"1"` e `"1a"` possono convivere. Modifiche: `modules/db/structures/Inventario_materiali_table.py` (Column + UniqueConstraint), `modules/db/entities/INVENTARIO_MATERIALI.py` (nuovo kwarg `sub_inv=None`), `resources/dbfiles/pyarchinit_schema_clean.sql` (DDL install PostgreSQL), template SQLite `pyarchinit_db.sqlite` e `pyarchinit.sqlite` (ALTER TABLE sui template distribuiti). / **feat(db,invmat): `sub_inv` column for optional sub-inventory suffix in `inventario_materiali_table`**: New `VARCHAR(8)` column alongside `numero_inventario` / `n_reperto` (both `bigint`) to store suffixes like `"a"`, `"b1"`, `"bis"` without synthetic numeric encoding: the inventory number stays a pure integer (numeric sorting, logical FK references preserved) and the sub-fragment variant lives in a dedicated column. `ID_invmat_unico` and `idx_n_reperto` UNIQUE constraints extended to `(sito, numero_inventario, sub_inv)` and `(sito, n_reperto, sub_inv)` so `"1"` and `"1a"` coexist.

- **feat(db): Migrazione automatica `sub_inv` per DB esistenti (PostgreSQL + SQLite)**: `postgres_db_updater.update_inventario_materiali_table()` rileva la mancanza di `sub_inv`, la aggiunge con `ADD COLUMN IF NOT EXISTS` e richiama `_rebuild_invmat_unique_constraints()` che droppa/ricrea `ID_invmat_unico` e `idx_n_reperto` includendo la nuova colonna. `sqlite_db_updater.update_other_tables()` fa lo stesso per SQLite tramite PRAGMA + `_rebuild_invmat_unique_indexes()`. Entrambi sono idempotenti: se la colonna esiste già, non toccano nulla. / **feat(db): Automatic `sub_inv` migration for existing DBs (PostgreSQL + SQLite)**: `postgres_db_updater.update_inventario_materiali_table()` detects missing `sub_inv`, adds it via `ADD COLUMN IF NOT EXISTS` and invokes `_rebuild_invmat_unique_constraints()` to drop/recreate `ID_invmat_unico` and `idx_n_reperto` including the new column. `sqlite_db_updater.update_other_tables()` does the same for SQLite using PRAGMA + `_rebuild_invmat_unique_indexes()`. Both are idempotent: if the column already exists, nothing changes.

- **feat(ui,invmat): Widget `lineEdit_sub_inv` iniettato nel form Inventario Materiali**: Nuovo `QLineEdit` (maxLength=8, placeholder `"a/b/bis"`) iniettato programmaticamente dopo `setupUi()` accanto a `lineEdit_num_inv` nel `QGridLayout` (il file `.ui` non è stato modificato). Collegato ai percorsi save/update/load/clear tramite `_get_sub_inv_value()` + `hasattr` guard per retrocompatibilità. / **feat(ui,invmat): `lineEdit_sub_inv` widget injected in Inventario Materiali form**: New `QLineEdit` (maxLength=8, placeholder `"a/b/bis"`) programmatically injected after `setupUi()` next to `lineEdit_num_inv` in the `QGridLayout` (the `.ui` file was not modified). Wired into save/update/load/clear paths via `_get_sub_inv_value()` + `hasattr` guards for backward compatibility.

### File modificati / Modified files
- `modules/db/structures/Inventario_materiali_table.py` (nuova `Column('sub_inv', String(8))`, UniqueConstraint esteso a 3 colonne)
- `modules/db/entities/INVENTARIO_MATERIALI.py` (nuovo kwarg `sub_inv=None` + attributo)
- `modules/db/postgres_db_updater.py` (add_column_if_missing + nuovo helper `_rebuild_invmat_unique_constraints`)
- `modules/db/sqlite_db_updater.py` (PRAGMA pre-check + nuovo helper `_rebuild_invmat_unique_indexes`)
- `resources/dbfiles/pyarchinit_schema_clean.sql` (DDL install + UNIQUE + CREATE INDEX)
- `resources/dbfiles/pyarchinit_db.sqlite` / `pyarchinit.sqlite` (template: ALTER TABLE ADD COLUMN sub_inv)
- `tabs/Inv_Materiali.py` (injection widget + save/update/load/clear + TODO su InventarioFilterDialog)

### Note / Notes
- I filter dialogs (`InventarioFilterDialog`) non sono ancora aggiornati per filtrare su `sub_inv`: TODO esplicito nel codice. / Filter dialogs (`InventarioFilterDialog`) not yet updated to filter by `sub_inv`: explicit TODO in the code.
- SQLite considera `NULL != NULL` nei vincoli UNIQUE, quindi record senza `sub_inv` non falsificano l'unicità della coppia `(sito, numero_inventario)`. Stesso comportamento su PostgreSQL di default. / SQLite treats `NULL != NULL` in UNIQUE constraints, so records without `sub_inv` don't falsify the uniqueness of `(sito, numero_inventario)`. Same behaviour on PostgreSQL by default.

---

## [5.0.16-alpha] - 2026-04-10

### Aggiunto / Added

- **feat(dashboard): Combo di esclusione Muri / Strutture nel pannello Computo Metrico (`_inject_walls_combo` + `_populate_walls_combo`)**: Nuova combobox poligonale "Muri / Strutture" (etichette localizzate in 10 lingue) iniettata sotto la combo "Layer Poligono" esistente nel pannello Computo Metrico. Permette all'utente di selezionare un layer poligonale che rappresenta i muri in elevato o le strutture costruite, che devono essere **escluse** dal calcolo del volume in m³. Quando impostata, `calculate_dem_difference()` chiama il nuovo helper `exclude_polygons_from_raster()` per bruciare NODATA sui poligoni corrispondenti nel raster differenza clippato prima del calcolo delle statistiche: le celle mascherate non vengono conteggiate nei volumi totali / di scavo / di riporto. L'esito è riportato sulla message bar di QGIS (`walls masked: <nome layer>` oppure `walls masking failed: <errore>`). / **feat(dashboard): Walls / structures exclusion combo in Computo Metrico panel (`_inject_walls_combo` + `_populate_walls_combo`)**: New "Muri / Strutture" polygon combobox (10-language localised labels) injected below the existing "Layer Poligono" combo in the Computo Metrico panel. Lets the user pick a polygon layer representing upstanding walls or built structures that must be **excluded** from the cubic-meter calculation. When set, `calculate_dem_difference()` calls the new `exclude_polygons_from_raster()` helper to burn NODATA over those features on the clipped diff raster before computing stats: the masked cells are not counted in total / cut / fill volumes. Outcome is reported to the QGIS message bar (`walls masked: <layer name>` or `walls masking failed: <error>`).

- **feat(dem-visualizer): Helper `exclude_polygons_from_raster()` in `pyarchinit_dem_visualizer.py`**: Usa `gdal.Rasterize` in modalità update per bruciare le feature poligonali in un raster esistente con un valore NODATA. Prima chiama `SetNoDataValue` sul banda 1 così che gli strumenti a valle (block access raster di QGIS, `compute_volume_stats`) saltino correttamente le celle bruciate. `allTouched=True` così anche i muri sottili vengono catturati interamente. Nessuna dipendenza da `processing.run`. / **feat(dem-visualizer): `exclude_polygons_from_raster()` helper in `pyarchinit_dem_visualizer.py`**: Uses `gdal.Rasterize` in update mode to burn polygon features into an existing raster with a NODATA value. First calls `SetNoDataValue` on band 1 so downstream tools (QGIS raster block access, `compute_volume_stats`) correctly skip the burned cells. `allTouched=True` so thin walls are fully captured. No `processing.run` dependency.

- **feat(dem-visualizer): Clip allineato — `clip_raster_by_polygon` accetta `target_x_res` / `target_y_res` / `target_bounds`**: Nuovi parametri opzionali di griglia pixel target passati attraverso a `gdal.Warp` come `xRes` / `yRes` / `targetAlignedPixels=True` / `outputBounds`. `calculate_dem_difference()` ora usa la risoluzione nativa del pre-DEM (`rasterUnitsPerPixelX()/Y()`) per entrambe le chiamate di clip pre e post, così i due raster clippati hanno **griglie pixel identiche** — questa è la correzione fondamentale del bug "si clippa lo stesso DEM" dove pre e post venivano ciascuno ritagliati individualmente al proprio footprint e il calcolatore a valle produceva silenziosamente risultati errati / vuoti. I nomi dei file di output usano ora un singolo timestamp esplicito più prefisso (`dem_pre_clipped_<ts>.tif` / `dem_post_clipped_<ts>.tif`) così non possono collidere nello stesso secondo. / **feat(dem-visualizer): Aligned clipping — `clip_raster_by_polygon` now accepts `target_x_res` / `target_y_res` / `target_bounds`**: Optional target pixel grid parameters passed through to `gdal.Warp` as `xRes` / `yRes` / `targetAlignedPixels=True` / `outputBounds`. `calculate_dem_difference()` now uses the pre-DEM's native `rasterUnitsPerPixelX()/Y()` for both the pre and post clip calls, so the two clipped outputs have **identical pixel grids** — this is the core fix for the "clipping the same DEM" bug where pre and post were each individually cropped to their own footprint and the downstream calculator silently produced wrong / empty results. Output filenames now use an explicit single timestamp + prefix (`dem_pre_clipped_<ts>.tif` / `dem_post_clipped_<ts>.tif`) so they cannot collide in the same second.

### Corretto / Fixed

- **fix(dashboard): Regressione "Clippa lo stesso DEM / il calcolo non è tra pre e post"**: La causa principale era la mancanza di una griglia target condivisa tra le due operazioni di clip, che rendeva i raster pre e post clippati incompatibili per la sottrazione cella-per-cella di `QgsRasterCalculator` — il risultato era che il calcolatore a valle sembrava "clippare lo stesso DEM" o produceva computi a zero. Fix dettagliato sopra: entrambe le chiamate di clip sono ora ancorate alla stessa griglia pixel derivata dal pre-DEM, così l'output del calcolatore è effettivamente `post − pre` sulla stessa estensione e risoluzione. / **fix(dashboard): "Clipping the same DEM / calculation is not between pre and post" regression**: Root cause was the lack of a shared target grid between the two clip operations, which made the pre and post clipped rasters incompatible for `QgsRasterCalculator` cell-by-cell subtraction — the downstream calculator appeared to "clip the same DEM" or produced empty/zero results. Fix detailed above: both clip calls are now anchored to the same pixel grid derived from the pre-DEM, so the calculator output is genuinely `post − pre` on the same extent and resolution.

- **fix(dashboard): Critico — formula del volume sbagliata in modalità poligono (`calculate_dem_polygon`)**: In `calculate_dem_polygon()` il volume era calcolato come `abs(dem_sum) * pixel_area` — cioè l'integrale della quota assoluta sull'area del poligono. Per una piccola trincea archeologica di ~62 m² su un terreno a ~1130 m s.l.m. ciò produceva risultati assurdi come **70 123 m³** (in pratica `62 × 1130`), perché ogni pixel contribuiva con la sua quota piena sopra il livello del mare invece che con la sua profondità. Fix: sostituita con `(dem_max × count − dem_sum) × pixel_area`, ovvero il volume della depressione al di sotto della quota massima del poligono (lo standard archeologico per computare i metri cubi da un singolo DEM post-scavo: il punto più alto del poligono è trattato come la superficie di terreno originaria, e ogni cella al di sotto contribuisce con la propria profondità × area pixel). Il risultato è clampato a zero per proteggere da arrotondamenti in virgola mobile. Con la nuova formula la stessa trincea riporta ora ~2 m³ (o quello che è il volume effettivamente scavato) invece di decine di migliaia di metri cubi. / **fix(dashboard): Critical — polygon-mode volume formula was wrong (`calculate_dem_polygon`)**: In `calculate_dem_polygon()` the volume was computed as `abs(dem_sum) * pixel_area` — i.e. the integral of absolute elevation over the polygon area. For a small archaeological trench of ~62 m² over terrain sitting at ~1130 m above sea level, this produced non-sensical results like **70 123 m³** (essentially `62 × 1130`), because every pixel contributed its full elevation above sea level instead of its depth. Fix: replaced with `(dem_max × count − dem_sum) × pixel_area`, which is the volume of the depression below the polygon's maximum elevation (the archaeological standard for computing cubic metres from a single post-excavation DEM: the polygon's highest point is treated as the original ground surface, and every cell below it contributes its depth × pixel area). Result is clamped to zero to guard against floating-point rounding. With the new formula the same trench now reports ~2 m³ (or whatever the real excavated volume is) instead of tens of thousands of cubic metres.

### File modificati / Modified files
- `modules/utility/pyarchinit_dem_visualizer.py` (new `exclude_polygons_from_raster()` helper using `gdal.Rasterize` in update mode with `SetNoDataValue` on band 1 and `allTouched=True`; `clip_raster_by_polygon` extended with optional `target_x_res` / `target_y_res` / `target_bounds` passed as `xRes` / `yRes` / `targetAlignedPixels=True` / `outputBounds` to `gdal.Warp`; explicit single-timestamp output filename prefixing to avoid collisions)
- `tabs/Cantiere.py` (new "Muri / Strutture" polygon combobox injected via `_inject_walls_combo` + `_populate_walls_combo` with 10-language labels below the existing polygon combo; `calculate_dem_difference()` derives the pre-DEM's native pixel size via `rasterUnitsPerPixelX()/Y()` and passes it as the shared target grid to both pre and post clip calls, then invokes `exclude_polygons_from_raster()` on the clipped diff raster when a walls layer is selected, with diagnostics pushed to the QGIS message bar; `calculate_dem_polygon()` now computes volume as `(dem_max × count − dem_sum) × pixel_area` — the depression-below-max formula — instead of the incorrect `abs(dem_sum) × pixel_area`, with zero-clamping to guard against floating-point rounding)

---

## [5.0.15-alpha] - 2026-04-10

### Aggiunto / Added

- **feat(dashboard): Layout a schede del Site Dashboard (`_reorganize_into_tabs` in `tabs/Cantiere.py`)**: A runtime, dopo `setupUi` e dopo l'iniezione del pulsante di visualizzazione e del pannello Analisi Costi, il layout piatto del Cantiere viene riorganizzato in un `QTabWidget` con tre schede — **Riepilogo / Overview** (Riepilogo Budget in alto a tutta larghezza, Personale ed Attrezzature affiancati), **Computo Metrico / Quantity Surveying** (input DEM, pulsanti Calcola + Mostra 2D + Mostra 3D + Esporta 2DM + 3D, label area/volume, pannello Analisi Costi, Salva Record, tabella storico) ed **Esportazione / Export** (pulsanti PDF + CSV con breve descrizione). La riga di header (combo Sito, combo Anno, pulsante Aggiorna, eventuale toggle tema) rimane in cima sopra le schede. La riorganizzazione avviene programmaticamente re-parentando i group box esistenti via `setParent()` + `removeWidget()`, così il file `.ui` non deve cambiare e i vecchi profili utente continuano a funzionare. La riorganizzazione è avvolta in try/except così qualunque errore ricade sul layout piatto originale e il dashboard resta pienamente funzionante. Le etichette delle schede sono localizzate in 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el). / **feat(dashboard): Tabbed Site Dashboard layout (`_reorganize_into_tabs` in `tabs/Cantiere.py`)**: At runtime, after `setupUi` and after the visualization button / cost panel injection, the flat Cantiere layout is reorganised into a `QTabWidget` with three tabs — **Riepilogo / Overview** (Budget Summary on top full-width, Personnel and Equipment side by side), **Computo Metrico / Quantity Surveying** (DEM inputs, Calcola + Show 2D + Show 3D + Export 2DM + 3D buttons, area/volume labels, Cost Analysis panel, Save Record, history table) and **Esportazione / Export** (PDF + CSV buttons with a short description). The header row (Site combo, Year combo, Refresh button, optional theme toggle) stays on top above the tabs. Done programmatically by re-parenting the existing group-box widgets via `setParent()` + `removeWidget()`, so the `.ui` file does not need to change and old user profiles keep working. The reorg is wrapped in try/except so any failure falls back to the original flat layout — the dashboard remains fully functional. Tab labels are localised in 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el).

### Corretto / Fixed

- **fix(dashboard): Critico — i DEM sparivano al click su Calcola**: Regressione introdotta nella 5.0.13-alpha: `calculate_dem_difference()` e `calculate_dem_polygon()` chiamavano `populate_raster_combos()` / `populate_vector_combos()` all'inizio per intercettare layer appena caricati, ma quei metodi facevano `.clear()` + re-add e resettavano la selezione corrente dell'utente, così `currentData()` ritornava immediatamente `None` e compariva il warning "Select both DEM layers". Fix: entrambi i metodi di popolamento catturano ora `currentData()` in ingresso e chiamano `setCurrentIndex(findData(...))` dopo il rebuild, con `blockSignals(True)/False` attorno al ciclo così gli slot a valle non scattano a vuoto. L'auto-refresh su Calcola ora mantiene correttamente i DEM e il poligono selezionati. / **fix(dashboard): Critical — DEMs disappeared on Calcola**: Regression introduced in 5.0.13-alpha: `calculate_dem_difference()` and `calculate_dem_polygon()` called `populate_raster_combos()` / `populate_vector_combos()` at the very start to pick up freshly-loaded layers, but those methods did `.clear()` + re-add, which reset the user's current selection, so `currentData()` immediately returned `None` and the warning "Select both DEM layers" popped up. Fix: both populate methods now capture `currentData()` on entry and call `setCurrentIndex(findData(...))` after the rebuild, with `blockSignals(True)/False` around the cycle so downstream slots don't fire spuriously. The auto-refresh on Calcola now correctly keeps the selected DEMs and polygon visible.

### File modificati / Modified files
- `tabs/Cantiere.py` (new `_reorganize_into_tabs` with `QTabWidget` re-parenting the existing group boxes into Riepilogo / Computo Metrico / Esportazione tabs with 10-language i18n and try/except fallback to the flat layout; `populate_raster_combos()` and `populate_vector_combos()` preserve the user's current selection via `currentData()` capture + `setCurrentIndex(findData(...))` restore with `blockSignals` around the rebuild)

---

## [5.0.14-alpha] - 2026-04-10

### Aggiunto / Added

- **feat(dashboard): Analisi Costi nel pannello Computo Metrico (`_inject_cost_panel` + persistenza `QgsSettings`)**: Nuovo group box "Analisi Costi / Cost Analysis" iniettato nel pannello Computo Metrico con due input — **Costo unitario** (€/m³) e **Produttività** (m³/giorno) — e tre label read-only aggiornate in tempo reale: **costo totale** (volume × costo unitario), **giorni stimati** (volume / produttività) e **costo giornaliero** (costo unitario × produttività). I valori sono persistiti per-sito sotto `pyArchInit/site_dashboard/costs/<sito>/{cost_per_m3,prod_m3_day}` in `QgsSettings` e seguono automaticamente la selezione del sito. Il ricalcolo è agganciato al `valueChanged` delle spinbox e a ogni esecuzione riuscita di `calculate_dem_difference()` / `calculate_dem_polygon()`, così l'utente vede i nuovi valori non appena "Calcola" produce un nuovo volume. / **feat(dashboard): Cost Analysis in Computo Metrico panel (`_inject_cost_panel` + `QgsSettings` persistence)**: New "Analisi Costi / Cost Analysis" group box injected in the Computo Metrico panel with two inputs — **Unit cost** (€/m³) and **Production rate** (m³/day) — and three live read-only labels: **total cost** (volume × unit cost), **estimated days** (volume / production rate) and **daily cost** (unit cost × production rate). Values are persisted per-site under `pyArchInit/site_dashboard/costs/<sito>/{cost_per_m3,prod_m3_day}` in `QgsSettings` and follow the site selection automatically. Recomputation is hooked to `valueChanged` on the spinboxes and to every successful `calculate_dem_difference()` / `calculate_dem_polygon()` run, so the user sees the new figures as soon as Calcola produces a new volume.

- **feat(dashboard): Sezione Analisi Costi nell'export PDF del Site Dashboard**: Nuova sezione tra Computo Metrico e Statistiche con una card arancione dei parametri (costo unitario + produttività) e una tabella per-computo con data, tipo, volume, costo, giorni, costo/giorno e riga totali. La card Statistiche è stata estesa con una nuova riga: costo totale (€) e giorni totali. I18n completa per 10 lingue (it, en, de, es, fr, ro, pt, ca, el, ar). / **feat(dashboard): Cost Analysis section in Site Dashboard PDF export**: New section between Computo Metrico and Statistics with an orange parameter card (unit cost + production rate) and a per-computo breakdown table with date, type, volume, cost, days, cost/day and a totals row. The Statistics card was extended with a new row: total cost (€) and total days. Full 10-language i18n (it, en, de, es, fr, ro, pt, ca, el, ar).

- **feat(dashboard): Blocco COST ANALYSIS nell'export CSV**: Nuova sezione dopo COMPUTO METRICO con righe di metadati per costo unitario e produttività, seguita da una tabella per-record (data, tipo, volume, costo, giorni, costo/giorno). Il blocco SUMMARY è stato esteso con `Total cost (EUR)` e `Total days`. Etichette localizzate per it + en. / **feat(dashboard): COST ANALYSIS block in CSV export**: New section after COMPUTO METRICO with metadata rows for unit cost and production rate, followed by a per-record table (date, type, volume, cost, days, cost/day). The SUMMARY block was extended with `Total cost (EUR)` and `Total days`. Localized labels for it + en.

- **feat(dashboard): Clipping per poligono in modalità "DEM su Poligono"**: `calculate_dem_polygon()` ora chiama `clip_raster_by_polygon` sul DEM singolo così che i viewer Show 2D / Show 3D / Build 2DM lavorino esclusivamente sull'area clippata. I messaggi diagnostici sono pushati sulla message bar di QGIS nello stesso modo della modalità differenza. Il raster clippato viene tracciato come `terrain_layer` (e il path del clip come `diff_raster_path` così il viewer 2D può leggerlo). / **feat(dashboard): Polygon clipping in "DEM on Polygon" mode**: `calculate_dem_polygon()` now calls `clip_raster_by_polygon` on the single DEM so that the Show 2D / Show 3D / Build 2DM viewers all work on the clipped area only. Diagnostics are pushed to the QGIS message bar the same way as in diff mode. The clipped raster is tracked as `terrain_layer` (and the clip path as `diff_raster_path` so the 2D viewer can read it).

- **feat(section-viewer): Fallback DEM singolo in `DemSectionViewerDialog`**: Quando `diff_arr` è `None` ed è disponibile solo un pre-DEM (modalità poligono), la heatmap renderizza ora l'elevazione del DEM con colormap `terrain` e l'istogramma mostra la distribuzione delle quote (con marker sulla media) — invece di restare vuoti. Le sezioni longitudinale e trasversale gestivano già il caso single-DEM. Nuove chiavi i18n `elev_heat_title` e `elev_hist_title` (it + en). / **feat(section-viewer): Single-DEM fallback in `DemSectionViewerDialog`**: When `diff_arr` is `None` and only a pre-DEM is available (polygon mode), the heatmap now renders the DEM elevation with a `terrain` colormap and the histogram shows the elevation distribution (with a mean marker) — instead of staying empty. Longitudinal and transverse sections already handled the single-DEM case. New i18n keys `elev_heat_title` and `elev_hist_title` (it + en).

### Corretto / Fixed

- **fix(dashboard): Bug "non clippa nulla" in modalità poligono**: Nella modalità poligono il ramo di clip non veniva mai eseguito (la logica di clip era presente solo nel ramo differenza), quindi Show 2D / Show 3D vedevano il DEM intero non clippato. Ora il clip viene eseguito in entrambe le modalità. / **fix(dashboard): "Nothing gets clipped" bug in polygon mode**: In polygon mode the clip branch never ran (clip logic was only in the diff path), so Show 2D / Show 3D saw the full unclipped DEM. The clip now runs in both modes.

### File modificati / Modified files
- `tabs/Cantiere.py` (cost panel injection + `QgsSettings` persistence, cost-aware PDF/CSV export with 10-language i18n, polygon-mode clipping via `clip_raster_by_polygon`, cost recompute hooks on spinbox `valueChanged` and after `calculate_dem_difference()` / `calculate_dem_polygon()`)
- `tabs/DemPlotDialogs.py` (single-DEM fallback heatmap with `terrain` colormap + elevation histogram with mean marker, new `elev_heat_title` / `elev_hist_title` i18n keys for it + en)

---

## [5.0.13-alpha] - 2026-04-10

### Aggiunto / Added

- **feat(dashboard): Auto-refresh delle combobox all'avvio del calcolo**: `calculate_dem_difference` in `tabs/Cantiere.py` ora invoca `populate_raster_combos()` e `populate_vector_combos()` prima di leggere le selezioni, così raster o poligoni caricati DOPO l'apertura del pannello Computo Metrico vengono rilevati automaticamente senza bisogno di premere manualmente "Aggiorna". / **feat(dashboard): Auto-refresh combos on Calcola**: `calculate_dem_difference` in `tabs/Cantiere.py` now calls `populate_raster_combos()` and `populate_vector_combos()` before reading the selections, so rasters or polygons loaded AFTER the Computo Metrico panel was opened are picked up automatically without requiring a manual refresh.

- **feat(dashboard): Messaggi diagnostici sulla message bar per ogni clip**: Ogni step di clip del DEM ora riporta l'esito alla message bar di QGIS tramite il nuovo helper `_notify_info()` (livello info, durata 6 s), così l'utente vede esattamente cosa è stato clippato, cosa no e perché. / **feat(dashboard): Diagnostic message bar on clip**: Every DEM clip step now reports its outcome to the QGIS message bar via the new `_notify_info()` helper (info level, 6 s duration) so the user can see exactly what was clipped, what wasn't, and why.

- **feat(dem-visualizer): Helper `_clean_raster_path()` in `pyarchinit_dem_visualizer.py`**: Rimuove i suffissi di provider come `|layername=...`, `|layerid=...` e simili dalle URI di source dei layer, così GDAL può consumarli direttamente senza errori su raster backed da GPKG / database. / **feat(dem-visualizer): `_clean_raster_path()` helper in `pyarchinit_dem_visualizer.py`**: Strips `|layername=...`, `|layerid=...` and similar provider suffixes from layer source URIs so GDAL can consume them directly without errors on GPKG / DB-backed rasters.

- **feat(dem-visualizer): `clip_raster_by_polygon` ora ritorna `(path, error)`**: L'helper restituisce una tupla così il chiamante può mostrare all'utente la vera causa di un clip fallito (intersezione vuota, mismatch di CRS, file mancante, eccezione di `gdal.Warp`, ecc.). Inoltre passa ora `cutlineSRS` dal CRS del layer poligonale e `dstSRS` dal CRS del raster, lasciando a GDAL la riproiezione automatica della cutline quando i CRS differiscono. / **feat(dem-visualizer): `clip_raster_by_polygon` now returns `(path, error)`**: The helper now returns a tuple so the caller can surface the real reason for a clip failure (empty intersection, CRS mismatch, missing file, gdal.Warp exception, etc.). It also passes `cutlineSRS` from the polygon layer CRS and `dstSRS` from the raster CRS to let GDAL reproject the cutline automatically when the CRSs differ.

### Corretto / Fixed

- **fix(dem-visualizer): Critico — "Costruisci Mesh 3D" non fa più crashare QGIS**: Il crash residuo dopo la 5.0.12-alpha è stato rintracciato nel caricamento di `QgsMeshLayer` e nelle chiamate a `QgsMeshRendererScalarSettings` da Python, che segfaultano su diverse build di QGIS perché le signature dell'API mesh non sono stabili tra minor version. Soluzione: il pulsante non carica più alcun mesh layer nel progetto QGIS. Ora (a) scrive i file 2DM su disco per uso esterno e (b) apre direttamente il viewer 3D matplotlib sui DEM (eventualmente clippati). Il percorso mesh-library non viene mai toccato da Python → non può segfaultare. `load_mesh_layer()` è mantenuto come stub ma non applica più `_style_mesh_terrain`. `_style_mesh_terrain()` conservato come dead code a scopo documentativo; il percorso attivo non lo chiama. / **fix(dem-visualizer): Critical — "Build 3D Mesh" no longer crashes QGIS**: The remaining crash after 5.0.12-alpha was traced to `QgsMeshLayer` loading and `QgsMeshRendererScalarSettings` calls from Python, which segfault on several QGIS builds because the mesh API signatures are unstable across minor versions. Solution: the button no longer loads any mesh layer into the QGIS project. It now (a) writes the 2DM files to disk for external use only, and (b) opens the matplotlib 3D surface viewer directly on the (possibly clipped) DEMs. The mesh-library path is never touched from Python → cannot segfault. `load_mesh_layer()` kept as a stub but no longer applies `_style_mesh_terrain`. `_style_mesh_terrain()` retained as dead code for documentation; the active path does not call it.

- **fix(dashboard): Pulsante rinominato da "Crea mesh 3D" / "Build 3D Mesh" a "Esporta 2DM + 3D" / "Export 2DM + 3D"**: Rinominato (e equivalenti in tutte le 10 lingue UI) per riflettere onestamente il nuovo comportamento. Tooltip aggiornato di conseguenza. / **fix(dashboard): Button renamed from "Crea mesh 3D" / "Build 3D Mesh" to "Esporta 2DM + 3D" / "Export 2DM + 3D"**: Renamed (and equivalents in all 10 UI languages) to honestly reflect the new behaviour. Tooltip updated accordingly.

- **fix(dem-visualizer): Pulizia del path del raster prima del clip**: La versione precedente passava `layer.source()` grezzo a `gdal.Warp`, che fallisce per i raster backed da GPKG / database a causa del suffisso `|layername=`. Ora viene gestito da `_clean_raster_path()`. / **fix(dem-visualizer): Clip path cleanup**: The previous version passed raw `layer.source()` to `gdal.Warp`, which fails for GPKG / DB-backed rasters because of the `|layername=` suffix. Now handled by `_clean_raster_path()`.

### File modificati / Modified files
- `tabs/Cantiere.py` (auto-refresh combos in `calculate_dem_difference`, `_notify_info()` helper and diagnostic message bar on clip, `_on_build_mesh` no longer loads mesh layers into QGIS — writes 2DM to disk and opens matplotlib 3D viewer directly, button renamed to "Esporta 2DM + 3D" / "Export 2DM + 3D" in all 10 UI languages, tooltip updated)
- `modules/utility/pyarchinit_dem_visualizer.py` (new `_clean_raster_path()` helper, `clip_raster_by_polygon` now returns `(path, error)` tuple and passes `cutlineSRS` / `dstSRS` for automatic reprojection, `load_mesh_layer()` kept as stub without `_style_mesh_terrain`, `_style_mesh_terrain()` retained as dead code)

---

## [5.0.12-alpha] - 2026-04-10

### Aggiunto / Added

- **feat(dashboard): Poligono come maschera di clip per la differenza DEM (`calculate_dem_difference`)**: Quando nel pannello Computo Metrico viene selezionato un layer poligonale in `comboBox_layer_poligono` insieme ai due DEM in modalita' "differenza DEM", i due DEM vengono ora clippati al poligono tramite `gdal.Warp` prima del calcolo della differenza. I raster pre/post clippati sono aggiunti al gruppo "Cruscotto Cantiere - Computi" / "Site Dashboard - Computi" con suffisso "clipped". Tutti gli step a valle — statistiche, section viewer 2D, fallback 3D matplotlib, builder della mesh TIN — operano ora esclusivamente sull'area di intervento. Nuovo stato `_last_calc['clip_poly_layer']` per tracciare la maschera di clip attiva. / **feat(dashboard): Polygon as clip mask for DEM difference (`calculate_dem_difference`)**: When a polygon layer is selected in `comboBox_layer_poligono` together with the two DEMs in "DEM difference" mode, both DEMs are now clipped to the polygon first via `gdal.Warp` before computing the difference. The clipped pre/post rasters are added to the "Cruscotto Cantiere - Computi" / "Site Dashboard - Computi" group with the suffix "clipped". Every downstream step — stats, 2D section viewer, matplotlib 3D fallback, TIN mesh builder — now operates on the intervention area only. New `_last_calc['clip_poly_layer']` state tracks the active clip mask.

- **feat(dem-visualizer): Utility `clip_raster_by_polygon` in `pyarchinit_dem_visualizer.py`**: Nuovo helper che clippa un raster a un `QgsVectorLayer` poligonale usando `gdal.Warp` e una cutline shapefile ESRI temporanea (esportata via `QgsVectorFileWriter.writeAsVectorFormatV3` con fallback legacy). Funziona sia con memory layer che con layer file-backed e non dipende dal framework `processing`. / **feat(dem-visualizer): `clip_raster_by_polygon` utility in `pyarchinit_dem_visualizer.py`**: New helper that clips a raster to a `QgsVectorLayer` polygon using `gdal.Warp` and a temporary ESRI Shapefile cutline (exported via `QgsVectorFileWriter.writeAsVectorFormatV3` with legacy fallback). Works with both memory layers and file-backed layers, and does not depend on the `processing` framework.

### Corretto / Fixed

- **fix(dem-visualizer): "Costruisci Mesh 3D" faceva crashare QGIS — fix critico**: L'implementazione precedente di `create_tin_mesh_from_dem()` invocava `native:pixelstopoints` + `native:tinmeshcreation` via `processing.run`. Su alcune build di QGIS questo causava un segfault lato C++ che faceva crashare l'intera applicazione. Sostituita con un **writer 2DM pure-Python**: legge il DEM via GDAL in NumPy, opzionalmente lo clippa per poligono (`clip_raster_by_polygon`), sottocampiona se la griglia supera le 15 000 celle, e scrive un file `MESH2D` a griglia regolare con un elemento quad `E4Q` per cella valida (nodi al centro del pixel, celle con nodata agli angoli scartate). Nessuna chiamata a `processing.run` — il percorso non puo' piu' segfaultare. Compatibile con tutte le versioni e profili QGIS. `_on_build_mesh()` ora avvolge ogni step in try/except, raccoglie i messaggi d'errore e propone come fallback l'uso diretto di "Mostra 3D" (matplotlib) quando la generazione della mesh fallisce per qualunque motivo. / **fix(dem-visualizer): "Build 3D Mesh" crashed QGIS — critical fix**: The previous implementation of `create_tin_mesh_from_dem()` invoked `native:pixelstopoints` + `native:tinmeshcreation` via `processing.run`. On some QGIS builds this caused a C++ segfault that crashed the whole application. Replaced with a **pure-Python 2DM writer**: reads the DEM via GDAL into NumPy, optionally clips it by polygon (`clip_raster_by_polygon`), downsamples if the grid exceeds 15 000 cells, and writes a regular-grid `MESH2D` file with one `E4Q` quad element per valid cell (nodes at pixel centres, cells with nodata corners skipped). No `processing.run` call is made — the path cannot segfault. Compatible with all QGIS versions and profiles. `_on_build_mesh()` now wraps each step in try/except, collects error messages, and offers the fallback suggestion of using "Show 3D" (matplotlib) directly when mesh generation fails for any reason.

### File modificati / Modified files
- `modules/utility/pyarchinit_dem_visualizer.py` (added `clip_raster_by_polygon`, `_write_polygon_to_temp_shp`, fully rewrote `create_tin_mesh_from_dem` as pure-Python 2DM writer)
- `tabs/Cantiere.py` (clip-aware `calculate_dem_difference`, safer `_on_build_mesh` with try/except and fallback suggestion, extended `_last_calc` with `clip_poly_layer`)

---

## [5.0.11-alpha] - 2026-04-10

### Aggiunto / Added

- **feat(dashboard): Dialog visualizzatore di sezione archeologica per il Computo Metrico**: Nuovo file `tabs/DemPlotDialogs.py` con `DemSectionViewerDialog`, un viewer analitico basato su matplotlib richiamato dal pulsante "Mostra 2D" del pannello Computo Metrico, che sostituisce il precedente comportamento (zoom sul canvas) con un vero grafico archeologico. Mostra: mappa di calore della differenza DEM con colormap divergente RdBu, colorbar e linee guida riga/colonna; istogramma cut/fill con aree di scavo (rosso) e riporto (blu); sezione longitudinale E-W attraverso i DEM — pre in blu, post in rosso, volume scavato riempito tra le due curve (stile classico della sezione archeologica); sezione trasversale N-S con stessa semantica; spinbox riga/colonna per scorrere interattivamente la linea di sezione; salvataggio PNG, toolbar di navigazione matplotlib; UI bilingue (it, en) con fallback inglese. / **feat(dashboard): Archaeological section viewer dialog for Computo Metrico**: New file `tabs/DemPlotDialogs.py` with `DemSectionViewerDialog`, a matplotlib-based analytical viewer invoked by the "Show 2D" button in the Computo Metrico panel, replacing the previous behaviour (canvas zoom) with a real archaeological chart. Shows: DEM difference heat-map with diverging RdBu colormap, colorbar and row/column guide-lines; cut/fill histogram with cut (red) and fill (blue) shaded regions; longitudinal section (E-W) through the DEMs — pre in blue, post in red, excavated volume filled between the two curves (classical archaeological section style); transverse (N-S) section with the same semantics; row/column spin boxes to scrub the section line interactively; PNG export, matplotlib navigation toolbar; 2-language UI (it, en) with English fallback.

- **feat(dashboard): Viewer 3D matplotlib come fallback quando `qgis._3d` non è disponibile**: Aggiunto `DemMatplotlib3dDialog` in `tabs/DemPlotDialogs.py`, una vista 3D basata su `mpl_toolkits.mplot3d` usata automaticamente quando il modulo `qgis._3d` non è disponibile nel profilo QGIS (librerie Qt3D mancanti). Modalità: overlay Pre+Post, Solo differenza, Solo DEM Pre; spinbox di esagerazione verticale; rotazione interattiva matplotlib; salvataggio PNG. Funziona su qualunque build di QGIS perché matplotlib è già dipendenza del plugin. / **feat(dashboard): Matplotlib 3D fallback viewer when `qgis._3d` is unavailable**: Added `DemMatplotlib3dDialog` in `tabs/DemPlotDialogs.py`, a `mpl_toolkits.mplot3d`-based 3D surface view used automatically when the `qgis._3d` module is missing in the QGIS profile (missing Qt3D libraries). Modes: Pre+Post overlay, Difference only, Pre-DEM only; vertical exaggeration spinbox; interactive matplotlib rotation; PNG export. Works on any QGIS build because matplotlib is already a plugin dependency.

- **feat(dem-visualizer): Auto-styling del mesh layer 2DM con rampa terreno**: `pyarchinit_dem_visualizer.load_mesh_layer()` ora applica un `QgsMeshRendererScalarSettings` con rampa colore "terreno" (verde → arancio → marrone) sul dataset group dell'elevazione del bed della mesh 2DM caricata, così la mesh è immediatamente riconoscibile nel canvas QGIS invece di apparire come una superficie piatta tipo raster. Nuova funzione helper privata `_style_mesh_terrain`. Messaggio post-build informativo che indirizza l'utente a "Mostra 3D". / **feat(dem-visualizer): 2DM mesh layer auto-styling with terrain ramp**: `pyarchinit_dem_visualizer.load_mesh_layer()` now applies a `QgsMeshRendererScalarSettings` with a terrain color ramp (green → orange → brown) on the bed-elevation dataset group of the loaded 2DM mesh, so the mesh is immediately recognisable in the QGIS canvas instead of appearing as a flat raster-like surface. New private helper `_style_mesh_terrain`. Informative post-build message pointing the user to "Show 3D".

### Corretto / Fixed

- **fix(dashboard): `_on_show_2d` apre il section viewer invece di zoomare il canvas**: Il pulsante "Mostra 2D" del pannello Computo Metrico ora apre il nuovo `DemSectionViewerDialog` (heat-map, istogramma, sezioni longitudinale e trasversale). Lo zoom sul canvas resta come fallback difensivo se matplotlib fallisce. / **fix(dashboard): `_on_show_2d` opens the section viewer instead of zooming the canvas**: The "Show 2D" button in the Computo Metrico panel now opens the new `DemSectionViewerDialog` (heat-map, histogram, longitudinal and transverse sections). Canvas zoom is retained as a defensive fallback if matplotlib fails.

- **fix(dashboard): `_on_show_3d` fallback trasparente a matplotlib quando manca `qgis._3d`**: Il pulsante "Mostra 3D" ora tenta prima `Qgs3DMapCanvas` e in caso di `ImportError` sul modulo `qgis._3d` apre in modo trasparente `DemMatplotlib3dDialog` invece di mostrare un dialog di errore (comportamento precedente). / **fix(dashboard): `_on_show_3d` transparent fallback to matplotlib when `qgis._3d` is missing**: The "Show 3D" button now tries `Qgs3DMapCanvas` first and, on `ImportError` of the `qgis._3d` module, transparently opens `DemMatplotlib3dDialog` instead of showing an error dialog (previous behaviour).

- **fix(dem-visualizer): Rimosso ramo dead-code nel blocco del messaggio di mesh pronta**: Pulito un piccolo ramo di codice morto nel blocco che mostra il messaggio di mesh pronta in `pyarchinit_dem_visualizer`. / **fix(dem-visualizer): Removed dead-code branch in the mesh-ready message block**: Cleaned up a small dead-code branch in the mesh-ready message block in `pyarchinit_dem_visualizer`.

### File modificati / Modified files
- `tabs/DemPlotDialogs.py` (NEW — `DemSectionViewerDialog` matplotlib archaeological section viewer + `DemMatplotlib3dDialog` 3D fallback viewer, it/en i18n)
- `modules/utility/pyarchinit_dem_visualizer.py` (`_style_mesh_terrain` helper, terrain ramp auto-styling in `load_mesh_layer()`, informative mesh-ready message, dead-code cleanup)
- `tabs/Cantiere.py` (`_on_show_2d` opens `DemSectionViewerDialog` with canvas zoom fallback, `_on_show_3d` transparent fallback to `DemMatplotlib3dDialog` when `qgis._3d` is unavailable)

---

## [5.0.10-alpha] - 2026-04-10

### Aggiunto / Added

- **feat(dashboard): Visualizzazione 2D e 3D del Computo Metrico nel Site Dashboard**: Nuovo modulo `modules/utility/pyarchinit_dem_visualizer.py` che persiste il raster di differenza DEM (pre - post) in `$PYARCHINIT_HOME/site_dashboard/<sito>/`, applica una rampa colore divergente rosso/blu (cut/fill), poligonizza l'area d'intervento tramite `gdal:polygonize` e la raggruppa nel Layers Panel, e genera mesh TIN dai DEM pre e post usando `native:pixelstopoints` + `native:tinmeshcreation`. Nuovo dialog `tabs/Dem3dViewerDialog.py` con `Qgs3DMapCanvas` embedded che mostra il DEM pre come terrain, il raster di differenza drappeggiato sopra, e opzionalmente le mesh TIN pre/post; include spinbox per l'esagerazione verticale, checkbox per attivare/disattivare i layer e pulsante reset vista. Etichette multilingua per 10 lingue. In `tabs/Cantiere.py`, `calculate_dem_difference()` ora persiste il raster di differenza, lo stilizza, lo inserisce in un gruppo dedicato del progetto, poligonizza l'area di scavo e zooma il canvas; `calculate_dem_polygon()` raggruppa ed evidenzia il layer poligonale; aggiunti programmaticamente i pulsanti "Mostra 2D", "Mostra 3D" e "Costruisci Mesh 3D" accanto a "Calcola", con nuovo dizionario di stato `_last_calc` che traccia tutti gli artefatti generati. / **feat(dashboard): 2D and 3D Computo Metrico visualization in Site Dashboard**: New module `modules/utility/pyarchinit_dem_visualizer.py` that persists the DEM difference raster (pre - post) under `$PYARCHINIT_HOME/site_dashboard/<sito>/`, applies a diverging red/blue color ramp (cut/fill), polygonizes the intervention area via `gdal:polygonize` and groups it in the Layers Panel, and generates TIN meshes from pre and post DEMs using `native:pixelstopoints` + `native:tinmeshcreation`. New dialog `tabs/Dem3dViewerDialog.py` with an embedded `Qgs3DMapCanvas` that shows the pre DEM as terrain, the difference raster draped over it, and optionally the pre/post TIN mesh layers; includes a vertical exaggeration spinbox, layer toggle checkboxes and a reset view button. Multi-language labels for 10 languages. In `tabs/Cantiere.py`, `calculate_dem_difference()` now persists the diff raster, styles it, adds it to the project in a dedicated group, polygonizes the cut area and zooms the canvas; `calculate_dem_polygon()` groups and highlights the polygon layer; "Show 2D", "Show 3D" and "Build 3D Mesh" buttons injected programmatically next to "Calcola", with a new `_last_calc` state dict tracking all generated artifacts.

- **feat(dashboard): Sezione Computo Metrico nell'export PDF del Site Dashboard**: Aggiunta una nuova sezione "Computo Metrico" nel PDF del Site Dashboard tra Attrezzature e Statistiche, con tabella completa (data, tipo, nome, area, volume, quota min/max, note) e riga totali. La tabella Statistiche è stata estesa con: numero totale computi, area totale (m²), volume totale (m³), volume di scavo (cut), volume di riporto (fill). / **feat(dashboard): Computo Metrico section in Site Dashboard PDF export**: Added a new "Computo Metrico" section in the Site Dashboard PDF between Equipment and Statistics, with a full table (date, type, name, area, volume, min/max elevation, notes) and a totals row. The Statistics table was extended with: total computi count, total area (m²), total volume (m³), cut volume, fill volume.

- **feat(dashboard): Sezione COMPUTO METRICO e SUMMARY nell'export CSV**: L'export CSV del Site Dashboard include ora un blocco metadati in testa (sito, anno, timestamp generazione), una nuova sezione **COMPUTO METRICO** con tutte le 12 colonne della tabella `COMPUTO_METRICO`, e un nuovo blocco aggregato **SUMMARY** con totali di budget, conteggio personale / attrezzature / computi, area e volume totali. Etichette di sezione localizzate (it + en) con fallback inglese per le altre lingue. / **feat(dashboard): COMPUTO METRICO and SUMMARY sections in CSV export**: Site Dashboard CSV export now includes a metadata block at the top (site, year, generation timestamp), a new **COMPUTO METRICO** section with all 12 columns from the `COMPUTO_METRICO` table, and a new aggregated **SUMMARY** block with budget totals, personnel / equipment / computi counts, total area and volume. Localized section labels (it + en) with English fallback for other languages.

### Corretto / Fixed

- **fix(dashboard): Font Unicode nell'export PDF del Site Dashboard**: Il font Helvetica non supporta i caratteri non-ASCII e mostrava quadrati vuoti (■) per rumeno (ă, â, î, ș, ț), greco, arabo, cirillico, portoghese e catalano. Ora il PDF registra DejaVu Sans (fornito con matplotlib) via `pdfmetrics.registerFont` / `registerFontFamily`, garantendo il rendering corretto di tutti i caratteri diacritici. L'i18n del PDF è stata estesa da 5 a 10 lingue (aggiunte ca, ro, pt, el, ar) e corrette le diacritiche mancanti nelle voci esistenti de/es/fr (ä, ñ, é ecc. ora tutte via Unicode corretto). / **fix(dashboard): Unicode font in Site Dashboard PDF export**: Helvetica font does not support non-ASCII characters and was showing empty boxes (■) for Romanian (ă, â, î, ș, ț), Greek, Arabic, Cyrillic, Portuguese and Catalan. The PDF now registers DejaVu Sans (bundled with matplotlib) via `pdfmetrics.registerFont` / `registerFontFamily`, ensuring correct rendering of all diacritic characters. PDF i18n extended from 5 to 10 languages (added ca, ro, pt, el, ar) and fixed missing diacritics in existing de/es/fr entries (ä, ñ, é etc. all now via proper Unicode).

- **fix(dashboard): Layout del title page e header bar nel PDF**: La title page è stata rifattorizzata come card con bordo, eliminando l'artefatto di sovrapposizione della HRFlowable "sottolineatura" sul titolo "Site Dashboard". Nella header bar, il nome del sito viene troncato a 32 caratteri con ellissi e usa un separatore a bullet invece di una stringa concatenata con pipe, che poteva collidere con la data di generazione allineata a destra. / **fix(dashboard): Title page and header bar layout in PDF**: Title page refactored as a bordered card, removing the HRFlowable "underline" overlap artifact over the "Site Dashboard" title. In the header bar, the site name is trimmed to 32 chars with ellipsis and uses a bullet separator instead of a pipe-concatenated string that could collide with the right-aligned generation date.

- **fix(dashboard): Encoding e delimitatore nell'export CSV**: Il CSV viene ora scritto in UTF-8 con BOM (`utf-8-sig`) così Excel / LibreOffice decodificano correttamente i nomi di file e i dati Unicode su qualsiasi locale, e usa il punto e virgola come delimitatore (default europeo di Excel). / **fix(dashboard): Encoding and delimiter in CSV export**: CSV is now written as UTF-8 with BOM (`utf-8-sig`) so Excel / LibreOffice correctly decode Unicode filenames and data on any locale, and uses semicolon as delimiter (European Excel default).

- **fix(compat): Compatibilità Qt6 / QGIS 4 per Site Dashboard e DEM visualizer**: Sostituito `matplotlib.backends.backend_qt5agg` con `backend_qtagg` con fallback (auto-rileva Qt5/Qt6). Enum Qt resi scoped-safe: `Qt.CursorShape.WaitCursor`, `Qt.AlignmentFlag.AlignCenter`, `QSizePolicy.Policy.Expanding`, `QFrame.Shape.StyledPanel` tutti protetti da try/except con fallback agli enum flat di Qt5. Lookup difensivo per `QgsColorRampShader.Type.Interpolated` (prima solo `QgsColorRampShader.Interpolated`). `QgsZonalStatistics.Statistic.Sum` accedutato via helper (prima `QgsZonalStatistics.Sum` flat). Import del modulo 3D (`qgis._3d`) avvolto in try/except così l'assenza del supporto 3D mostra un messaggio amichevole invece di causare crash. / **fix(compat): Qt6 / QGIS 4 compatibility for Site Dashboard and DEM visualizer**: Replaced `matplotlib.backends.backend_qt5agg` with `backend_qtagg` with fallback (auto-detects Qt5/Qt6). Qt enums made scoped-safe: `Qt.CursorShape.WaitCursor`, `Qt.AlignmentFlag.AlignCenter`, `QSizePolicy.Policy.Expanding`, `QFrame.Shape.StyledPanel` all wrapped with try/except fallback to Qt5 flat enums. Defensive lookup for `QgsColorRampShader.Type.Interpolated` (was only `QgsColorRampShader.Interpolated`). `QgsZonalStatistics.Statistic.Sum` accessed via helper (was flat `QgsZonalStatistics.Sum`). 3D module import (`qgis._3d`) wrapped in try/except so missing 3D support shows a friendly message instead of crashing.

### File modificati / Modified files
- `modules/utility/pyarchinit_dem_visualizer.py` (NEW — persistent DEM diff raster, diverging color ramp, polygonize, TIN mesh creation)
- `tabs/Dem3dViewerDialog.py` (NEW — Qgs3DMapCanvas dialog with draped diff raster, TIN mesh toggles, vertical exaggeration, 10-language labels)
- `tabs/Cantiere.py` (calculate_dem_difference persists + styles + polygonizes + zooms, calculate_dem_polygon groups/highlights, Show 2D / Show 3D / Build 3D Mesh buttons, `_last_calc` state dict)
- `tabs/SiteDashboard.py` / PDF export module (DejaVu Sans registration, Computo Metrico section, extended statistics, title page card, trimmed header bar, 10-language PDF i18n, UTF-8-sig CSV with semicolon delimiter, COMPUTO METRICO + SUMMARY sections, Qt6 enum fallbacks, `backend_qtagg`, defensive QgsColorRampShader / QgsZonalStatistics / `qgis._3d` imports)

---

## [5.0.9-alpha] - 2026-04-03

### Corretto / Fixed

- **fix(pdf): Protezione eval() da campi vuoti nei PDF export**: Tutti i `eval(self.campo)` nelle schede PDF (Finds, InvLap, Tafonomia, Struttura, Tomba, Periodo) e in Interactive_matrix/Inv_Materiali causavano `SyntaxError: unexpected EOF while parsing` quando il campo era stringa vuota `""` o `None`. Aggiunto guard `if self.campo` prima di ogni `eval()`, pattern: `eval(self.campo) if self.campo else []`. 9 file corretti, ~80 occorrenze totali. / **fix(pdf): Guard eval() against empty fields in PDF exports**: All `eval(self.field)` calls in PDF sheet files (Finds, InvLap, Taphonomy, Structure, Tomb, Period) and in Interactive_matrix/Inv_Materiali raised `SyntaxError: unexpected EOF while parsing` when field was empty string `""` or `None`. Added `if self.field` guard before every `eval()`, pattern: `eval(self.field) if self.field else []`. 9 files fixed, ~80 occurrences total.

### File modificati / Modified files
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py` (guard eval for elementi_reperto, misurazioni, tecnologie, rif_biblio)
- `modules/utility/pyarchinit_exp_Invlapsheet_pdf.py` (guard eval for bibliografia)
- `modules/utility/pyarchinit_exp_Tafonomiasheet_pdf.py` (guard eval for caratteristiche, corredo_tipo, misure_tomba)
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py` (guard eval for materiali_impiegati, elementi_strutturali, rapporti_struttura, misure_struttura)
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py` (guard eval for materiali, caratteristiche, corredo_tipo, misure_tomba)
- `modules/utility/pyarchinit_exp_Periodosheet_pdf.py` (guard eval for rapporti, documentazione, inclusi, campioni)
- `modules/utility/pdf_models/pyarchinit_exp_Findssheet_pdf.py` (guard eval for misurazioni, tecnologie, rif_biblio)
- `tabs/Interactive_matrix.py` (guard eval for rapporti2, rapporti)
- `tabs/Inv_Materiali.py` (guard eval for elementi_reperto)

---

## [5.0.9-alpha] - 2026-04-01

### Corretto / Fixed

- **fix(db): Campi schema ampliati — attivita, stato_di_conservazione, formazione**: Tre campi della `us_table` avevano limiti VARCHAR troppo stretti per dati reali. `attivita`: VARCHAR(4) → VARCHAR(100), insufficiente per descrizioni come "Distruzione post abbandono dell'anfiteatro" (42 caratteri). `stato_di_conservazione`: VARCHAR(20) → VARCHAR(255), troncava valori lunghi. `formazione`: VARCHAR(20) → VARCHAR(100). Aggiornati tutti gli schema SQL (clean, clean_backup, updated), strutture SQLAlchemy (structures + structures_metadata), script di aggiornamento PostgreSQL (ALTER COLUMN) e SQLite (commento, tipo advisory), e validatori IT/DE/EN. / **fix(db): Schema fields widened — attivita, stato_di_conservazione, formazione**: Three `us_table` fields had VARCHAR limits too narrow for real data. `attivita`: VARCHAR(4) → VARCHAR(100), insufficient for activity descriptions like "Distruzione post abbandono dell'anfiteatro" (42 chars). `stato_di_conservazione`: VARCHAR(20) → VARCHAR(255), was truncating long values. `formazione`: VARCHAR(20) → VARCHAR(100). Updated all SQL schemas (clean, clean_backup, updated), SQLAlchemy structures (structures + structures_metadata), PostgreSQL update script (ALTER COLUMN) and SQLite update script (comment, advisory type), and IT/DE/EN validators.

- **fix(matrix): Numeri US negativi causavano errori di sintassi DOT nel grafo Harris**: I numeri US negativi (es. `-3858`) venivano interpretati da Graphviz come operatori di sottrazione nel formato DOT, causando errori di rendering. Aggiunta funzione `_quote_node()` in `Interactive_matrix.py` che prefixa i nodi con 'US' (es. `US_3858`). Inoltre, l'output di `tred` (riduzione transitiva) conteneva attributi di layout (`pos`, `width`, `height`, `bb`) e frammenti di coordinate orfane che causavano errori di sintassi al re-rendering. Aggiunto stripping di questi attributi in `pyarchinit_matrix_exp.py`. Cambiato `subprocess.Popen` per usare `proc.wait()` con `tred`. / **fix(matrix): Negative US numbers caused DOT syntax errors in Harris matrix graph**: Negative US numbers (e.g. `-3858`) were interpreted by Graphviz as subtraction operators in DOT format, causing rendering errors. Added `_quote_node()` function in `Interactive_matrix.py` that prefixes nodes with 'US' (e.g. `US_3858`). Additionally, `tred` (transitive reduction) output contained layout attributes (`pos`, `width`, `height`, `bb`) and orphan coordinate fragments that caused syntax errors when re-rendered. Added stripping of these attributes in `pyarchinit_matrix_exp.py`. Changed `subprocess.Popen` to use `proc.wait()` with `tred`.

- **fix(ui): NameError table_name nella scheda rapporti stratigrafici**: In `US_USM.py`, la variabile `table_name` era usata in 4 punti della gestione rapporti stratigrafici ma era stata commentata, causando `NameError` a runtime. Sostituita con chiamate dirette a `self.tableWidget_rapporti.selectedItems()` / `.selectedIndexes()`. / **fix(ui): NameError table_name in stratigraphic rapporti tab**: In `US_USM.py`, the variable `table_name` was used in 4 places in the stratigraphic rapporti management but had been commented out, causing `NameError` at runtime. Replaced with direct calls to `self.tableWidget_rapporti.selectedItems()` / `.selectedIndexes()`.

### File modificati / Modified files
- `resources/dbfiles/pyarchinit_schema_clean.sql` (attivita, stato_di_conservazione widened)
- `resources/dbfiles/pyarchinit_schema_clean_backup.sql` (attivita, stato_di_conservazione widened)
- `resources/dbfiles/pyarchinit_schema_updated.sql` (attivita, stato_di_conservazione widened)
- `resources/dbfiles/pyarchinit_update_postgres.sql` (ALTER COLUMN for attivita, stato_di_conservazione)
- `resources/dbfiles/pyarchinit_update_sqlite.sql` (advisory type comments)
- `modules/db/structures/US_table.py` (attivita, stato_di_conservazione, formazione widened)
- `modules/db/structures/US_table_toimp.py` (attivita, stato_di_conservazione, formazione widened)
- `modules/db/structures_metadata/US_table.py` (attivita, stato_di_conservazione, formazione widened)
- `modules/db/structures_metadata/US_table_toimp.py` (attivita, stato_di_conservazione, formazione widened)
- `tabs/Interactive_matrix.py` (`_quote_node()` for negative US numbers)
- `modules/utility/pyarchinit_matrix_exp.py` (strip tred layout attributes, `proc.wait()`)
- `tabs/US_USM.py` (fix table_name NameError in 4 occurrences)

---

## [5.0.8-alpha] - 2026-03-27

### Corretto / Fixed

- **fix(init): Installazione pacchetti QGIS 4 macOS con fallback Python multipli**: Il Python embedded di QGIS 4 non supporta pip (errore `encodings`). Ora il sistema prova in ordine: QGIS python3, QGIS python3.12, /usr/bin/python3, Homebrew python3, sys.executable. Aggiunto QGIS 4 path a QGIS_PATHS. / **fix(init): QGIS 4 macOS package installation with multiple Python fallbacks**: QGIS 4 embedded Python doesn't support pip (`encodings` error). Now tries in order: QGIS python3, QGIS python3.12, /usr/bin/python3, Homebrew python3, sys.executable. Added QGIS 4 path to QGIS_PATHS.

- **fix(time-manager): Filtro per SITE_SET invece di tutti i siti**: `_get_cached_sito_area` ora legge SITE_SET dalla configurazione invece di caricare tutti i siti dal DB. `set_max_num` calcola max order_layer solo per il sito corrente. Fix ORDER_LAYER_VALUE None → 0 nel filtro SQL. / **fix(time-manager): Filter by SITE_SET instead of all sites**: `_get_cached_sito_area` now reads SITE_SET from config instead of loading all sites. `set_max_num` computes max order_layer for current site only. Fix ORDER_LAYER_VALUE None → 0 in SQL filter.

- **fix(gis): Quote caricate da materialized view per Time Manager**: Le quote ora vengono caricate da `pyarchinit_quote_view` (materialized view con order_layer) invece di `pyarchinit_quote` (tabella base senza order_layer). Stessa correzione per quote USM e USM view. / **fix(gis): Quote loaded from materialized view for Time Manager**: Quote now loaded from `pyarchinit_quote_view` (materialized view with order_layer) instead of `pyarchinit_quote` (base table without order_layer). Same fix for quote USM and USM view.

- **fix(us): Order layer usa sito dal combobox**: `launch_order_layer_if` ora usa `comboBox_sito.currentText()` (sito configurato) invece di `DATA_LIST[0].sito` che poteva essere sbagliato. / **fix(us): Order layer uses sito from combobox**: `launch_order_layer_if` now uses `comboBox_sito.currentText()` (configured site) instead of `DATA_LIST[0].sito` which could be wrong.

### File modificati / Modified files
- `__init__.py` (QGIS 4 paths, Python fallbacks)
- `tabs/Gis_Time_controller.py` (SITE_SET filter, ORDER_LAYER_VALUE fix)
- `modules/gis/pyarchinit_pyqgis.py` (quote from matview, USM sito filter)
- `tabs/US_USM.py` (order layer sito from combobox)

---

## [5.0.7-alpha] - 2026-03-26

### Performance / Prestazioni

- **perf(gis): Map preview filtra per sito**: Il layer di sfondo "mappa completa" nel map preview ora filtra per sito corrente invece di caricare tutte le 164K geometrie del DB. Zoom sul bbox del sito con 10% buffer. / **perf(gis): Map preview filters by site**: Background "complete map" layer in map preview now filters by current site instead of loading all 164K geometries. Zoom to site bbox with 10% buffer.

- **perf(gis): Materialized views per US/USM/Quote**: Le 4 view spaziali principali sono ora materialized views pre-calcolate su disco con indici GiST. 17K geometrie in 14ms (prima 10+ minuti). Funzione `refresh_pyarchinit_matviews()` per aggiornamento. / **perf(gis): Materialized views for US/USM/Quote**: 4 main spatial views are now materialized views pre-computed on disk with GiST indexes. 17K geometries in 14ms (was 10+ minutes). `refresh_pyarchinit_matviews()` function for refresh.

- **perf(gis): Semplificazione geometrie per rendering veloce**: Abilitata `QgsVectorSimplifyMethod` per i layer US con algoritmo distance-based per velocizzare pan/zoom. / **perf(gis): Geometry simplification for fast rendering**: Enabled `QgsVectorSimplifyMethod` for US layers with distance-based algorithm for faster pan/zoom.

- **perf(rust): Modulo Rust compilato per 3 piattaforme**: Binari pre-compilati per Linux x86_64, macOS ARM64, Windows x86_64 via GitHub Actions CI. Auto-loader rileva piattaforma e carica il binario corretto. Fallback Python trasparente. / **perf(rust): Rust module compiled for 3 platforms**: Pre-compiled binaries for Linux x86_64, macOS ARM64, Windows x86_64 via GitHub Actions CI. Auto-loader detects platform and loads correct binary. Transparent Python fallback.

### Aggiunto / Added

- **feat(style): Opzione "Solo contorno" nello stile**: Nuovo bottone "Simbolo singolo (solo contorno)" nel dialog stile con riempimento trasparente e contorno grigio scuro. Rendering 10x più veloce per grandi dataset. / **feat(style): "Outline only" style option**: New "Single symbol (outline only)" button in style dialog with transparent fill and dark grey outline. 10x faster rendering for large datasets.

- **feat(permissions): Permessi sito per utente**: Admin può assegnare siti specifici a ogni utente. Il combobox sito nel config dialog mostra solo i siti autorizzati. / **feat(permissions): Site permissions per user**: Admin can assign specific sites to each user. Site combobox in config dialog shows only authorized sites.

- **feat(us): Ricerca e navigazione relazioni stratigrafiche**: Bottone "Cerca Relazioni" nella scheda US con dialog per visualizzare, filtrare per tipo e navigare le relazioni. / **feat(us): Stratigraphic relationship search and navigation**: "Search Relationships" button in US form with dialog to view, filter by type and navigate relationships.

### File modificati / Modified files
- `modules/gis/pyarchinit_pyqgis.py` (map preview sito filter, simplification, zoom)
- `modules/utility/create_style.py` (null fill style, i18n dialog)
- `modules/utility/rust_helpers.py` (auto-loader multi-platform)
- `tabs/US_USM.py` (map preview zoom to layer extent)
- `resources/dbfiles/create_view.sql` + `create_view_updated.sql` (materialized views)
- `_rust_core/src/spatial/mod.rs` (new Rust module)
- `_rust_binaries/` (pre-compiled binaries)
- `.github/workflows/build-rust.yml` (CI for 3 platforms)

---

## [5.0.9-alpha] - 2026-03-26

### Aggiunto / Added

- **perf(sql): Viste materializzate per le 4 viste geometriche principali in PostgreSQL**: Convertite `pyarchinit_us_view`, `pyarchinit_usm_view`, `pyarchinit_quote_view` e `pyarchinit_quote_usm_view` da viste regolari a MATERIALIZED VIEW in entrambi i file SQL di installazione (`create_view.sql` e `create_view_updated.sql`). Rimosse le clausole ORDER BY (non necessarie per matviews, QGIS ordina lato client). Aggiunti indici GiST spaziali, indici su sito e indici univoci su gid per ogni matview. Aggiunta funzione `refresh_pyarchinit_matviews()` per il refresh concorrente. Le altre viste restano regolari. Solo PostgreSQL, nessun impatto su SQLite. / **perf(sql): Materialized views for the 4 main geometry views in PostgreSQL**: Converted `pyarchinit_us_view`, `pyarchinit_usm_view`, `pyarchinit_quote_view` and `pyarchinit_quote_usm_view` from regular views to MATERIALIZED VIEW in both installation SQL files (`create_view.sql` and `create_view_updated.sql`). Removed ORDER BY clauses (not needed for matviews, QGIS sorts client-side). Added spatial GiST indexes, sito indexes and unique gid indexes for each matview. Added `refresh_pyarchinit_matviews()` function for concurrent refresh. Other views remain regular. PostgreSQL only, no impact on SQLite.

- **feat(rust): Integrazione opzionale del modulo Rust pyarchinit_core**: Aggiunto import opzionale di `pyarchinit_core` in `pyarchinit_pyqgis.py` con fallback Python. Nell'area di caricamento layer US (`charge_vector_layers`), se il modulo Rust e' disponibile, viene usato per pre-calcolare le categorie di stile. Creato modulo helper `modules/utility/rust_helpers.py` con funzioni `parse_rapporti()`, `compute_style_categories()` e `is_rust_available()` che usano Rust quando disponibile e Python come fallback. / **feat(rust): Optional Rust module pyarchinit_core integration**: Added optional import of `pyarchinit_core` in `pyarchinit_pyqgis.py` with Python fallback. In the US layer loading area (`charge_vector_layers`), if the Rust module is available, it is used to pre-compute style categories. Created helper module `modules/utility/rust_helpers.py` with `parse_rapporti()`, `compute_style_categories()` and `is_rust_available()` functions that use Rust when available and Python as fallback.

### File modificati / Modified files
- `resources/dbfiles/create_view.sql` (4 views -> materialized views + indexes + refresh function)
- `resources/dbfiles/create_view_updated.sql` (4 views -> materialized views + indexes + refresh function)
- `modules/gis/pyarchinit_pyqgis.py` (optional Rust import + style acceleration)
- `modules/utility/rust_helpers.py` (NEW - Rust/Python helper functions)

---

## [5.0.8-alpha] - 2026-03-26

### Aggiunto / Added

- **feat(us): Ricerca e navigazione relazioni stratigrafiche nella scheda US**: Aggiunto pulsante "Cerca Relazioni Stratigrafiche" vicino alla tabella rapporti nella scheda US. Apre un dialog professionale che mostra tutte le relazioni della US corrente (dirette e inverse) con: tabella risultati con colonne Tipo/US/Area/Sito/Direzione/Naviga, pulsante "Naviga" per saltare direttamente a una US correlata, checkbox "Mostra relazioni inverse" che cerca in tutto il sito le US che referenziano la US corrente, dropdown "Cerca per Tipo di Relazione" per filtrare tutte le US del sito per tipo (Copre, Taglia, Riempie, ecc.), pulsante "Mostra Tutti Correlati" che filtra DATA_LIST alle sole US correlate. Supporto i18n per IT/EN/DE/ES/FR. / **feat(us): Stratigraphic relationship search and navigation in US form**: Added "Search Stratigraphic Relationships" button near the rapporti table in the US form. Opens a professional dialog showing all relationships of the current US (direct and inverse) with: results table with Type/US/Area/Site/Direction/Navigate columns, "Navigate" button to jump directly to a related US, "Show inverse relationships" checkbox that searches the entire site for US records referencing the current US, "Search by Relationship Type" dropdown to filter all site US by type (Covers, Cuts, Fills, etc.), "Show All Related" button that filters DATA_LIST to only related US records. i18n support for IT/EN/DE/ES/FR.

### File modificati / Modified files
- `tabs/US_USM.py` (button in __init__, new method on_pushButton_search_relationships_pressed)

---

## [5.0.7-alpha] - 2026-03-26

### Aggiunto / Added

- **feat(permissions): Permessi utente basati su sito - filtro siti autorizzati per utente**: Aggiunto widget QListWidget con checkbox nella scheda Gestione Utenti per assegnare siti autorizzati per ogni utente. Il campo `site_filter` (comma-separated) nella tabella `pyarchinit_users` viene letto/scritto automaticamente. Nel Config Dialog, il combobox siti viene filtrato in base ai permessi dell'utente PostgreSQL corrente (solo PostgreSQL, non SQLite). Superuser (postgres, admin_pyarchinit) e utenti con site_filter vuoto vedono tutti i siti. Pulsanti "Seleziona tutti" / "Deseleziona tutti" con traduzioni in 10 lingue. / **feat(permissions): Site-based user permissions - authorized site filter per user**: Added QListWidget widget with checkboxes in User Management tab to assign authorized sites per user. The `site_filter` field (comma-separated) in `pyarchinit_users` table is read/written automatically. In Config Dialog, site combobox is filtered based on current PostgreSQL user's permissions (PostgreSQL only, not SQLite). Superusers (postgres, admin_pyarchinit) and users with empty site_filter see all sites. "Select All" / "Deselect All" buttons with translations in 10 languages.

### File modificati / Modified files
- `gui/user_management_dialog.py` (site list widget, translations, save/load site_filter)
- `gui/pyarchinitConfigDialog.py` (site filter in charge_list)

---

## [5.0.6-alpha] - 2026-03-26

### Corretto / Fixed

- **fix(db): Aggiornamento DB ora esegue SQL statement per statement con autocommit**: L'esecuzione del file SQL di aggiornamento (`update_production_db_safe.sql` e `add_concurrency_fixed.sql`) ora splitta ogni statement e li esegue singolarmente con try/except. Se uno statement fallisce (colonna già esistente, tabella pre-esistente, tipo mismatch), viene saltato e si prosegue col successivo. Errori non critici loggati in QgsMessageLog. Aggiunto `ALTER TABLE ADD COLUMN IF NOT EXISTS` prima degli INSERT in pyarchinit_roles per gestire tabelle pre-esistenti con schema diverso. / **fix(db): DB update now executes SQL statement-by-statement with autocommit**: SQL update file execution now splits each statement and executes them individually with try/except. If a statement fails (column already exists, pre-existing table, type mismatch), it is skipped and execution continues. Non-critical errors logged to QgsMessageLog. Added `ALTER TABLE ADD COLUMN IF NOT EXISTS` before INSERT into pyarchinit_roles to handle pre-existing tables with different schema.

- **fix(geoarchaeo): Errore QVariant float conversion in main_dock.py**: Le feature QGIS restituiscono QVariant NULL che non è convertibile con float(). Protetti tutti i 4 punti di chiamata float(feature[field]) con try/except e filtro str(val) per valori NULL/None. / **fix(geoarchaeo): QVariant float conversion error in main_dock.py**: QGIS features return QVariant NULL which is not convertible with float(). Protected all 4 float(feature[field]) call sites with try/except and str(val) filter for NULL/None values.

- **fix(geoarchaeo): Errore MultiPolygonZ asPoint() in main_dock.py**: La funzione asPoint() fallisce su geometrie Polygon/MultiPolygon. Sostituiti tutti i 4 geom.asPoint() con geom.centroid().asPoint() per supportare qualsiasi tipo di geometria. / **fix(geoarchaeo): MultiPolygonZ asPoint() error in main_dock.py**: The asPoint() function fails on Polygon/MultiPolygon geometries. Replaced all 4 geom.asPoint() with geom.centroid().asPoint() to support any geometry type.

### Aggiornamento / Update

- **feat(ai): Tradotta scheda RAG AI Query in 10 lingue con ThemeManager**: Aggiunto dizionario traduzioni con 35 chiavi (it/en/de/es/fr/ar/ca/ro/pt/el) a RAGQueryDialog. Sostituiti tutti gli string hardcoded italiani in setup_ui. Aggiunto ThemeManager.apply_theme e add_theme_toggle_to_form. / **feat(ai): Translated RAG AI Query dialog to 10 languages with ThemeManager**: Added 35-key translation dict (it/en/de/es/fr/ar/ca/ro/pt/el) to RAGQueryDialog. Replaced all hardcoded Italian strings in setup_ui. Added ThemeManager.apply_theme and add_theme_toggle_to_form.

- **feat(ai): Aggiornati modelli Claude a Sonnet 4.6, fix path API key**: Aggiornato claude-sonnet-4-5-20250929 a claude-sonnet-4-6 in textTosql.py, skatch_gpt_US.py, skatch_gpt_INVMAT.py. Corretto lookup API key: ora cerca prima claude_api_key.txt poi fallback a anthropic_api_key.txt. / **feat(ai): Updated Claude models to Sonnet 4.6, fix API key path**: Updated claude-sonnet-4-5-20250929 to claude-sonnet-4-6 in textTosql.py, skatch_gpt_US.py, skatch_gpt_INVMAT.py. Fixed API key lookup: now tries claude_api_key.txt first, fallback to anthropic_api_key.txt.

### File modificati / Modified files
- `modules/geoarchaeo/gui/main_dock.py` (QVariant + centroid fix)
- `tabs/US_USM.py` (RAG dialog i18n + ThemeManager)
- `modules/utility/textTosql.py` (Claude 4.6 + key path)
- `modules/utility/skatch_gpt_US.py` (Claude 4.6)
- `modules/utility/skatch_gpt_INVMAT.py` (Claude 4.6)

---

## [5.0.5-alpha.3] - 2026-03-24

### Aggiornamento / Update

- **fix(ai): Sostituito `max_tokens` con `max_completion_tokens` nelle chiamate API OpenAI per compatibilità GPT-5.4**: I nuovi modelli GPT-5.4 richiedono il parametro `max_completion_tokens` anziché `max_tokens` nelle chiamate `client.chat.completions.create()` e nei dizionari di parametri per richieste HTTP dirette. Aggiornati 14 punti di chiamata in 6 file. Non modificati: variabili interne (`self.max_tokens`), logica di splitting token, chiamate API Anthropic (che usano correttamente `max_tokens`). File modificati: modules/utility/textTosql.py (2), modules/utility/skatch_gpt_US.py (3), modules/utility/skatch_gpt_INVMAT.py (3), modules/utility/pottery_similarity/embedding_models.py (1), tabs/US_USM.py (4), scripts/translate_ts_complete.py (1). / **fix(ai): Replaced `max_tokens` with `max_completion_tokens` in OpenAI API calls for GPT-5.4 compatibility**: New GPT-5.4 models require the `max_completion_tokens` parameter instead of `max_tokens` in `client.chat.completions.create()` calls and HTTP request parameter dicts. Updated 14 call sites across 6 files. Not modified: internal variables (`self.max_tokens`), token splitting logic, Anthropic API calls (which correctly use `max_tokens`). Files modified: modules/utility/textTosql.py (2), modules/utility/skatch_gpt_US.py (3), modules/utility/skatch_gpt_INVMAT.py (3), modules/utility/pottery_similarity/embedding_models.py (1), tabs/US_USM.py (4), scripts/translate_ts_complete.py (1).

---

## [5.0.5-alpha.2] - 2026-03-24

### Aggiornamento / Update

- **chore(ai): Aggiornati tutti i riferimenti ai modelli OpenAI GPT alla versione marzo 2026**: Sostituiti tutti i modelli GPT obsoleti (gpt-4.1, gpt-4.1-mini, gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-4-vision-preview, gpt-3.5-turbo) con le versioni aggiornate (gpt-5.4, gpt-5.4-mini). Le liste dropdown/combobox ora offrono ["gpt-5.4-mini", "gpt-5.4", "gpt-5.3-codex"]. File modificati: tabs/US_USM.py, tabs/Thesaurus.py, tabs/Periodizzazione.py, tabs/Inv_Materiali.py, tabs/pyarchinit_Pottery_mainapp.py, modules/utility/skatch_gpt_US.py, modules/utility/skatch_gpt_INVMAT.py, modules/utility/textTosql.py, modules/utility/pottery_similarity/embedding_models.py, scripts/translate_ts_complete.py, scripts/auto_translate_ts.py. / **chore(ai): Updated all OpenAI GPT model references to March 2026 versions**: Replaced all obsolete GPT models (gpt-4.1, gpt-4.1-mini, gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-4-vision-preview, gpt-3.5-turbo) with updated versions (gpt-5.4, gpt-5.4-mini). Dropdown/combobox lists now offer ["gpt-5.4-mini", "gpt-5.4", "gpt-5.3-codex"]. Files modified: tabs/US_USM.py, tabs/Thesaurus.py, tabs/Periodizzazione.py, tabs/Inv_Materiali.py, tabs/pyarchinit_Pottery_mainapp.py, modules/utility/skatch_gpt_US.py, modules/utility/skatch_gpt_INVMAT.py, modules/utility/textTosql.py, modules/utility/pottery_similarity/embedding_models.py, scripts/translate_ts_complete.py, scripts/auto_translate_ts.py.

---

## [5.0.5-alpha.1] - 2026-03-24

### Corretto / Fixed

- **fix(ui): Corretto overlap tra DB Settings e Path Settings nel Config Dialog**: Le sezioni groupBox_3 (DB Settings) e groupBox_4 (Path Settings) nel primo tab del dialog di configurazione si sovrapponevano quando entrambe espanse. Aggiunto wrapping automatico in QScrollArea tramite `_fix_settings_tab_overlap()` nel costruttore Python che ri-parentizza i widget in un layout verticale scrollabile. / **fix(ui): Fixed overlap between DB Settings and Path Settings in Config Dialog**: The groupBox_3 (DB Settings) and groupBox_4 (Path Settings) sections in the first tab of the configuration dialog overlapped when both expanded. Added automatic QScrollArea wrapping via `_fix_settings_tab_overlap()` in the Python constructor that re-parents widgets into a scrollable vertical layout.

- **fix(i18n): Tradotte etichette e messaggi hardcoded italiani nel Config Dialog in 10 lingue**: Sostituiti oltre 30 messaggi italiani hardcoded (Connessione avvenuta, Errore di connessione, Imposta variabile ambientale, Non dimenticarti di inserire la password, etc.) con chiamate `self.tr()` per supporto i18n. Aggiunto metodo `_translate_ui_labels()` che traduce titoli tab, titoli groupbox, testi pulsanti e tooltip dal caricamento UI italiano. Eliminata la triplicazione di codice per it/de/else in `try_connection()`, `connection_up()`, `save_p()`, `on_pushButton_save_pressed()` e altri metodi. / **fix(i18n): Translated hardcoded Italian labels and messages in Config Dialog to 10 languages**: Replaced 30+ hardcoded Italian messages (Connessione avvenuta, Errore di connessione, Imposta variabile ambientale, Non dimenticarti di inserire la password, etc.) with `self.tr()` calls for i18n support. Added `_translate_ui_labels()` method that translates tab titles, groupbox titles, button texts and tooltips from Italian UI definitions. Eliminated triplicated code for it/de/else in `try_connection()`, `connection_up()`, `save_p()`, `on_pushButton_save_pressed()` and other methods.

- **feat(ui): Modernizzato Info Dialog con interfaccia a schede professionale e supporto 10 lingue**: Riscritto `pyarchinitInfoDialog.py` con QTabWidget a 4 schede (About, System, Dependencies, Links & Support). Tab About: logo, badge versione, sviluppatori, ringraziamenti, licenza. Tab System: tabella con versione plugin, Python, QGIS, Qt, OS, tipo DB e stato connessione con indicatori colorati. Tab Dependencies: tabella 11 dipendenze con stato disponibile/mancante e versione. Tab Links: card con link a sito, GitHub, documentazione, gruppo supporto, email, PayPal donazioni. Aggiunto ThemeManager con apply_theme e toggle. Dizionario I18N completo per 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el). / **feat(ui): Modernized Info Dialog with professional tabbed interface and 10-language support**: Rewrote `pyarchinitInfoDialog.py` with 4-tab QTabWidget (About, System, Dependencies, Links & Support). About tab: logo, version badge, developers, acknowledgments, license. System tab: table with plugin version, Python, QGIS, Qt, OS, DB type and connection status with colored indicators. Dependencies tab: table of 11 dependencies with available/missing status and version. Links tab: cards with links to website, GitHub, documentation, support group, email, PayPal donations. Added ThemeManager with apply_theme and toggle. Complete I18N dictionary for 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el).

---

## [5.0.5-alpha] - 2026-03-24

### Corretto / Fixed

- **fix(charts): Corretto rendering grafici nel tab Analytics di Budget.py - matplotlib come backend primario**: I grafici Plotly nel tab Budget Analytics non venivano visualizzati perche' QWebEngineView spesso non e' disponibile nell'ambiente QGIS. Riscritti i tre metodi di disegno grafici (`draw_category_chart`, `draw_timeline_chart`, `draw_variance_chart`) per usare matplotlib come backend primario con FigureCanvasQTAgg, mantenendo Plotly come fallback opzionale. Grafico a ciambella per categorie con legenda esterna, grafico barre+linea cumulativa per timeline mensile con doppio asse Y, grafico barre orizzontali raggruppate per scostamento con colori verde/rosso. DPI 100, stile professionale, palette colori coerente, titoli multilingua. Aggiunta `_plotly_html_template()` helper e `FuncFormatter` per formattazione assi. / **fix(charts): Fixed chart rendering in Budget.py Analytics tab - matplotlib as primary backend**: Plotly charts in the Budget Analytics tab were not displaying because QWebEngineView is often unavailable in QGIS environments. Rewrote all three chart drawing methods (`draw_category_chart`, `draw_timeline_chart`, `draw_variance_chart`) to use matplotlib as the primary backend with FigureCanvasQTAgg, keeping Plotly as an optional fallback. Donut chart with external legend for categories, bar+cumulative line chart for monthly timeline with dual Y axes, grouped horizontal bar chart for variance with green/red coloring. 100 DPI, professional styling, consistent color palette, language-aware titles. Added `_plotly_html_template()` helper and `FuncFormatter` for axis formatting.

- **fix(ui): Riposizionato pulsante toggle tema in basso a destra per evitare sovrapposizione con toolbar**: Il pulsante toggle tema in `pyarchinit_theme_manager.py` era posizionato in alto a destra (y=10) e si sovrapponeva con barre degli strumenti e label dei form. Spostato in basso a destra (`form.width()-40, form.height()-40`) con aggiornamento dinamico al resize. / **fix(ui): Repositioned theme toggle button to bottom-right to avoid toolbar overlap**: The theme toggle button in `pyarchinit_theme_manager.py` was positioned at top-right (y=10) and overlapped with toolbars and labels in many forms. Moved to bottom-right (`form.width()-40, form.height()-40`) with dynamic repositioning on resize.

- **feat(theme): Aggiunto supporto tema a GPT Sketch e DB Management dialog**: Integrato ThemeManager con `apply_theme()` e `add_theme_toggle_to_form()` in `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py` e `gui/dbmanagment.py` per coerenza visiva con il resto del plugin. / **feat(theme): Added theme support to GPT Sketch and DB Management dialog**: Integrated ThemeManager with `apply_theme()` and `add_theme_toggle_to_form()` in `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py` and `gui/dbmanagment.py` for visual consistency with the rest of the plugin.

### Internazionalizzazione / Internationalization

- **feat(i18n): Tradotto sistema gestione utenti e permessi in 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el)**: Aggiunta internazionalizzazione completa a `gui/user_management_dialog.py` con dizionario TRANSLATIONS contenente 80+ chiavi tradotte per etichette, pulsanti, intestazioni colonne, messaggi di errore/conferma/successo e metodo helper `tr_()`. Refactoring di `modules/db/permission_handler.py` da 3 lingue (it/de/en) a 10, con dizionari classificati per tipo errore (encoding, connection, duplicate, foreign_key, generic) e messaggi permessi per operazione (INSERT/UPDATE/DELETE/SELECT). Completata `_show_cantiere_permission_denied()` in `pyarchinitPlugin.py` aggiungendo le 5 lingue mancanti (ar, ca, ro, pt, el) alle 5 esistenti. / **feat(i18n): Translated user management and permissions system into 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el)**: Added full internationalization to `gui/user_management_dialog.py` with TRANSLATIONS dictionary containing 80+ translated keys for labels, buttons, column headers, error/confirm/success messages and `tr_()` helper method. Refactored `modules/db/permission_handler.py` from 3 languages (it/de/en) to 10, with dictionaries organized by error type (encoding, connection, duplicate, foreign_key, generic) and permission messages per operation (INSERT/UPDATE/DELETE/SELECT). Completed `_show_cantiere_permission_denied()` in `pyarchinitPlugin.py` by adding the 5 missing languages (ar, ca, ro, pt, el) to the existing 5.

### Migliorato / Improved

- **feat(analytics): Aggiunta funzionalità analytics al form Budget.py**: Nuovo tab Analytics con schede riepilogative (totale previsto, totale effettivo, scostamento con colori verde/rosso, barra progresso utilizzo budget), tabella riepilogativa raggruppata per categoria con ordinamento e colorazione, tre grafici Plotly interattivi (donut spesa per categoria, timeline mensile con barre spesa e linea cumulativa previsto, barre orizzontali raggruppate planned vs actual per categoria con colori verde/rosso). Export PDF analytics con ReportLab (tabella sommario + dettaglio per categoria). Pattern QWebEngineView con 3 percorsi import e fallback matplotlib. Supporto completo i18n per 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el). / **feat(analytics): Added analytics functionality to Budget.py form**: New Analytics tab with summary cards (total planned, total actual, variance with green/red coloring, budget usage progress bar), summary table grouped by category with sorting and color-coding, three interactive Plotly charts (category spending donut, monthly timeline with spending bars and cumulative planned line, horizontal grouped bars planned vs actual per category with green/red coloring). Analytics PDF export with ReportLab (summary table + category breakdown). QWebEngineView pattern with 3 import paths and matplotlib fallback. Full i18n support for 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el).

- **feat(pdf): Ridisegnato export PDF professionale per Presenze.py**: Layout landscape A4 full-page con header/footer su ogni pagina (barra blu scuro #1a237e con nome sito, periodo, data generazione), tabella presenze con colori alternati, risoluzione nomi personale da personale_table (non solo ID), sezione riepilogo con ore totali ordinarie/straordinarie, costo totale, giorni lavorati e personale coinvolto. Supporto multilingua completo (it/en/de/es/fr). Font Helvetica coerente. / **feat(pdf): Redesigned professional PDF export for Presenze.py**: Full-page landscape A4 layout with header/footer on every page (dark blue #1a237e bar with site name, period, generation date), attendance table with alternating row colors, personnel name resolution from personale_table (not just IDs), summary section with total regular/overtime hours, total cost, days worked and personnel count. Full multilingual support (it/en/de/es/fr). Consistent Helvetica fonts throughout.

- **feat(pdf): Ridisegnato export PDF dashboard professionale per Cantiere.py**: PDF portrait A4 multi-pagina con pagina titolo (nome sito, anno, data generazione), sezione budget con tabella dettagliata (preventivato/effettivo/differenza con colori verde/rosso) e grafico a barre orizzontali ReportLab (Drawing/Rect/String), tabella personale con 6 colonne, inventario attrezzature con stato colorato, sezione statistiche riepilogative. Header/footer professionali su ogni pagina, supporto multilingua (it/en/de/es/fr). / **feat(pdf): Redesigned professional dashboard PDF export for Cantiere.py**: Multi-page portrait A4 PDF with title page (site name, year, generation date), budget section with detailed table (budgeted/actual/variance with green/red coloring) and horizontal bar chart using ReportLab Drawing primitives (Drawing/Rect/String), personnel table with 6 columns, equipment inventory with color-coded status, summary statistics section. Professional header/footer on every page, multilingual support (it/en/de/es/fr).

### Sicurezza / Security

- **feat(permissions): Collegato sistema permessi ai form gestione cantiere in pyarchinitPlugin.py**: Aggiunti controlli permessi prima dell'apertura dei 5 form cantiere (Cantiere, Personale, Presenze, Attrezzature, Budget). Solo utenti con ruolo 'admin' o 'responsabile' possono accedere. Il controllo e' un soft gate: se il sistema permessi non e' installato, se si usa SQLite, o se si verifica un errore, l'accesso e' consentito per retrocompatibilita'. Aggiunti metodi _check_cantiere_permission() e _show_cantiere_permission_denied() con messaggi in 5 lingue (it/en/de/es/fr). / **feat(permissions): Connected permission system to cantiere management forms in pyarchinitPlugin.py**: Added permission checks before opening the 5 cantiere forms (Cantiere, Personale, Presenze, Attrezzature, Budget). Only users with 'admin' or 'responsabile' role can access. The check is a soft gate: if the permission system tables don't exist, if using SQLite, or if any error occurs, access is allowed for backward compatibility. Added _check_cantiere_permission() and _show_cantiere_permission_denied() helper methods with messages in 5 languages (it/en/de/es/fr).

### Migliorato / Improved

- **feat(chart): Sostituito grafico budget matplotlib con Plotly interattivo in Cantiere.py**: Il metodo draw_budget_chart ora genera un grafico a ciambella Plotly interattivo renderizzato in QWebEngineView, con tooltip in euro, palette professionale Material Design, titoli multilingua (10 lingue) e fallback automatico a matplotlib se Plotly o QWebEngineView non sono disponibili. Refactoring in metodi helper (_clear_chart_layout, _aggregate_budget_by_category, _get_chart_title, _draw_budget_chart_plotly, _draw_budget_chart_matplotlib). / **feat(chart): Replaced matplotlib budget pie chart with interactive Plotly in Cantiere.py**: The draw_budget_chart method now generates an interactive Plotly donut chart rendered in QWebEngineView, with hover tooltips showing euro amounts, a professional Material Design color palette, locale-aware titles (10 languages), and automatic fallback to matplotlib if Plotly or QWebEngineView are unavailable. Refactored into helper methods (_clear_chart_layout, _aggregate_budget_by_category, _get_chart_title, _draw_budget_chart_plotly, _draw_budget_chart_matplotlib).

- **feat(ui): Convertiti campi data da QLineEdit a QDateEdit con popup calendario in 4 schede cantiere**: Sostituiti 10 campi data (QLineEdit) con QDateEdit dotati di calendario popup e formato yyyy-MM-dd nei file UI: Personale.ui (3 campi), Presenze.ui (1 campo), Attrezzature.ui (3 campi), Budget.ui (2 campi). Aggiornati i 4 file Python corrispondenti (Personale.py, Presenze.py, Attrezzature.py, Budget.py) per usare QDate con parsing multi-formato e fallback. / **feat(ui): Converted date fields from QLineEdit to QDateEdit with calendar popup in 4 cantiere forms**: Replaced 10 date fields (QLineEdit) with QDateEdit widgets featuring calendar popup and yyyy-MM-dd display format in UI files: Personale.ui (3 fields), Presenze.ui (1 field), Attrezzature.ui (3 fields), Budget.ui (2 fields). Updated the 4 corresponding Python files (Personale.py, Presenze.py, Attrezzature.py, Budget.py) to use QDate with multi-format parsing and fallback.

### Corretto / Fixed

- **fix(presenze): Collegata comboBox_personale a charge_list() e al cambio sito in Presenze.py**: La comboBox del personale nel form Presenze non si popolava automaticamente. Collegata la comboBox_personale a charge_list() e al segnale di cambio sito, così la lista del personale ora si popola automaticamente in base al sito selezionato. / **fix(presenze): Connected comboBox_personale to charge_list() and site change signal in Presenze.py**: The personnel comboBox in the Attendance form was not auto-populating. Connected comboBox_personale to charge_list() and the site change signal, so the personnel list now auto-populates based on the selected site.

### Migliorato / Improved

- **feat(thesaurus): TABLE_DISPLAY_MAPPING ora multilingua (10 lingue) con 4 tabelle cantiere aggiunte**: Esteso TABLE_DISPLAY_MAPPING in pyarchinit_thesaurus_compatibility.py per supportare 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el) e aggiunte le 4 tabelle del modulo cantiere (personale, presenze, attrezzature, budget). / **feat(thesaurus): TABLE_DISPLAY_MAPPING now multilingual (10 languages) with 4 cantiere tables added**: Extended TABLE_DISPLAY_MAPPING in pyarchinit_thesaurus_compatibility.py to support 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el) and added the 4 cantiere module tables (personnel, attendance, equipment, budget).

- **feat(i18n): Aggiunta traduzione dinamica UI (retranslate_ui) per 4 schede cantiere in 6 lingue (it/en/de/es/fr/ar)**: Implementato il metodo retranslate_ui() nelle 4 schede del modulo cantiere per aggiornare dinamicamente label, placeholder e tooltip al cambio lingua dell'interfaccia, supportando 6 lingue. / **feat(i18n): Added dynamic UI translation (retranslate_ui) for 4 cantiere forms in 6 languages (it/en/de/es/fr/ar)**: Implemented retranslate_ui() method in the 4 cantiere module forms to dynamically update labels, placeholders and tooltips on UI language change, supporting 6 languages.

- **feat(thesaurus): Aggiunto code_descriptions con tooltips per tabelle cantiere (14.1-14.7) in Thesaurus.py**: Aggiunte le definizioni code_descriptions per i codici thesaurus 14.1-14.7 relativi alle tabelle cantiere, con tooltip descrittivi per ogni vocabolario. / **feat(thesaurus): Added code_descriptions with tooltips for cantiere tables (14.1-14.7) in Thesaurus.py**: Added code_descriptions definitions for thesaurus codes 14.1-14.7 related to cantiere tables, with descriptive tooltips for each vocabulary.

### Dati / Data

- **data(db): Inseriti 4 record personale nel DB khutm2 (Al-Khutm)**: Aggiunti i record del personale per il sito Al-Khutm nel database khutm2: Cattani, Gambino, Garbelli, Vinci. / **data(db): Inserted 4 personnel records in khutm2 DB (Al-Khutm)**: Added personnel records for the Al-Khutm site in the khutm2 database: Cattani, Gambino, Garbelli, Vinci.

- **data(thesaurus): Inseriti 130+ record thesaurus nel DB per 7 vocabolari cantiere (14.1-14.7) in IT e en_US**: Aggiunti oltre 130 record nella tabella thesaurus del database per i 7 vocabolari del modulo cantiere (14.1 ruolo, 14.2 tipo_contratto, 14.3 tipo_giornata, 14.4 categoria_attrezzature, 14.5 stato, 14.6 proprietà, 14.7 categoria_budget) nelle lingue italiano e inglese (en_US). / **data(thesaurus): Inserted 130+ thesaurus records in DB for 7 cantiere vocabularies (14.1-14.7) in IT and en_US**: Added over 130 records in the database thesaurus table for the 7 cantiere module vocabularies (14.1 role, 14.2 contract_type, 14.3 day_type, 14.4 equipment_category, 14.5 status, 14.6 ownership, 14.7 budget_category) in Italian and English (en_US).

- **data(db): Aggiornati tutti i campi dei 5 record personale nel DB khutm2 (ruolo, qualifica, email, telefono, contratto, tariffe, IBAN, note)**: Completati i dati di tutti e 5 i record del personale nel database khutm2 con informazioni dettagliate su ruolo, qualifica, email, telefono, tipo di contratto, tariffe orarie, IBAN e note operative. / **data(db): Updated all fields for 5 personnel records in khutm2 DB (role, qualification, email, phone, contract, rates, IBAN, notes)**: Completed data for all 5 personnel records in the khutm2 database with detailed information on role, qualification, email, phone, contract type, hourly rates, IBAN and operational notes.

### Corretto / Fixed

- **fix(presenze): Corretto mismatch widget: lineEdit_turno→comboBox_turno con metodi corretti (currentText, setEditText)**: Il codice Python referenziava lineEdit_turno ma il file UI conteneva comboBox_turno. Aggiornati tutti i riferimenti nel controller Presenze.py per usare comboBox_turno con i metodi corretti currentText() e setEditText(). / **fix(presenze): Fixed widget mismatch: lineEdit_turno→comboBox_turno with correct methods (currentText, setEditText)**: The Python code referenced lineEdit_turno but the UI file contained comboBox_turno. Updated all references in the Presenze.py controller to use comboBox_turno with the correct currentText() and setEditText() methods.

- **fix(budget): Corretto mismatch widget: lineEdit_anno→comboBox_anno e textEdit_descrizione→lineEdit_descrizione**: Il codice Python referenziava widget inesistenti nel file UI. Aggiornati i riferimenti in Budget.py: lineEdit_anno→comboBox_anno (con currentText/setEditText) e textEdit_descrizione→lineEdit_descrizione (con text/setText). / **fix(budget): Fixed widget mismatch: lineEdit_anno→comboBox_anno and textEdit_descrizione→lineEdit_descrizione**: The Python code referenced widgets that did not exist in the UI file. Updated references in Budget.py: lineEdit_anno→comboBox_anno (with currentText/setEditText) and textEdit_descrizione→lineEdit_descrizione (with text/setText).

- **fix(attrezzature): Corretto mismatch widget: lineEdit_nome→comboBox_nome e lineEdit_assegnato_a→comboBox_assegnato_a**: Il codice Python referenziava lineEdit per nome e assegnato_a ma il file UI conteneva comboBox. Aggiornati tutti i riferimenti in Attrezzature.py per usare comboBox_nome e comboBox_assegnato_a con i metodi corretti. / **fix(attrezzature): Fixed widget mismatch: lineEdit_nome→comboBox_nome and lineEdit_assegnato_a→comboBox_assegnato_a**: The Python code referenced lineEdit for nome and assegnato_a but the UI file contained comboBox. Updated all references in Attrezzature.py to use comboBox_nome and comboBox_assegnato_a with the correct methods.

### Migliorato / Improved

- **feat(i18n): Tradotti bottoni rapidi Presenze (Registra Oggi, Ferie, Malattia, Permesso) in 10 lingue**: Aggiunte le traduzioni per i 4 bottoni rapidi del form Presenze in tutte le 10 lingue supportate (it, en, de, es, fr, ar, ca, ro, pt, el). / **feat(i18n): Translated Presenze quick buttons (Register Today, Holiday, Sick Leave, Day Off) in 10 languages**: Added translations for the 4 quick buttons in the Attendance form across all 10 supported languages (it, en, de, es, fr, ar, ca, ro, pt, el).

- **feat(ui): Convertiti tutti i campi data da QLineEdit a QDateEdit con calendario popup in 4 schede (9 campi totali)**: Sostituzione sistematica di tutti i campi data rimasti come QLineEdit con widget QDateEdit dotati di calendario popup e formato yyyy-MM-dd nelle schede Personale, Presenze, Attrezzature e Budget. / **feat(ui): Converted all date fields from QLineEdit to QDateEdit with calendar popup in 4 forms (9 total fields)**: Systematic replacement of all remaining date fields from QLineEdit to QDateEdit widgets with calendar popup and yyyy-MM-dd format in the Personale, Presenze, Attrezzature and Budget forms.

- **feat(i18n): Completate traduzioni retranslate_ui a 10 lingue (aggiunte ca, ro, pt, el)**: Esteso il metodo retranslate_ui() nelle 4 schede cantiere per supportare tutte le 10 lingue, aggiungendo le traduzioni mancanti per catalano, rumeno, portoghese e greco. / **feat(i18n): Completed retranslate_ui translations to 10 languages (added ca, ro, pt, el)**: Extended the retranslate_ui() method in the 4 cantiere forms to support all 10 languages, adding the missing translations for Catalan, Romanian, Portuguese and Greek.

#### File modificati / Modified files
- `tabs/Presenze.py` - fix comboBox_personale charge_list() + site change signal
- `modules/utility/pyarchinit_thesaurus_compatibility.py` - TABLE_DISPLAY_MAPPING multilingual + cantiere tables
- `tabs/Personale.py` - retranslate_ui() dynamic i18n
- `tabs/Presenze.py` - retranslate_ui() dynamic i18n + fix lineEdit_turno→comboBox_turno + i18n quick buttons
- `tabs/Attrezzature.py` - retranslate_ui() dynamic i18n + fix lineEdit_nome→comboBox_nome, lineEdit_assegnato_a→comboBox_assegnato_a
- `tabs/Budget.py` - retranslate_ui() dynamic i18n + fix lineEdit_anno→comboBox_anno, textEdit_descrizione→lineEdit_descrizione
- `modules/utility/pyarchinit_thesaurus.py` - code_descriptions tooltips 14.1-14.7
- `gui/ui/Personale.ui` - QDateEdit conversion
- `gui/ui/Presenze.ui` - QDateEdit conversion
- `gui/ui/Attrezzature.ui` - QDateEdit conversion
- `gui/ui/Budget.ui` - QDateEdit conversion

---

## [5.0.5-alpha] - 2026-02-20

### i18n e Thesaurus / i18n and Thesaurus

- **feat(i18n): Espansione traduzioni da 3 a 10 lingue per le tab Gestione Cantiere**: Aggiunte traduzioni per es, fr, ar, ca, ro, pt, el nelle variabili MSG_BOX_TITLE, STATUS_ITEMS e SORTED_ITEMS per Personale.py, Presenze.py, Attrezzature.py e Budget.py. Le CONVERSION_DICT e SORT_ITEMS erano già complete in 10 lingue. / **feat(i18n): Expand translations from 3 to 10 languages for Site Management tabs**: Added translations for es, fr, ar, ca, ro, pt, el in MSG_BOX_TITLE, STATUS_ITEMS and SORTED_ITEMS variables for Personale.py, Presenze.py, Attrezzature.py and Budget.py. CONVERSION_DICT and SORT_ITEMS were already complete in 10 languages.

- **feat(thesaurus): Nuovo thesaurus codici 14.1-14.7 per Gestione Cantiere (~470 record)**: Creati 7 codici tipologia_sigla per le tabelle cantiere: 14.1 ruolo (10 valori), 14.2 tipo_contratto (6), 14.3 tipo_giornata (6), 14.4 categoria_attrezzature (7), 14.5 stato (4), 14.6 proprietà (4), 14.7 categoria_budget (7), ciascuno in 10 lingue. Seed implementato sia in sqlite_db_updater.py che postgres_db_updater.py con guard idempotente. / **feat(thesaurus): New thesaurus codes 14.1-14.7 for Site Management (~470 records)**: Created 7 tipologia_sigla codes for cantiere tables: 14.1 role (10 values), 14.2 contract_type (6), 14.3 day_type (6), 14.4 equipment_category (7), 14.5 status (4), 14.6 ownership (4), 14.7 budget_category (7), each in 10 languages. Seed implemented in both sqlite_db_updater.py and postgres_db_updater.py with idempotent guard.

- **feat(tabs): Integrazione thesaurus nei combobox delle tab Cantiere**: I combobox ruolo/tipo_contratto (Personale), tipo_giornata (Presenze), categoria/stato/proprietà (Attrezzature), categoria (Budget) ora si popolano dal thesaurus tramite query_thesaurus_batch() nella lingua corrente dell'interfaccia. Aggiunta mappa LANG_TO_THESAURUS in ogni tab. Aggiornato pyarchinit_thesaurus_compatibility.py con mapping per le 4 tabelle cantiere. / **feat(tabs): Thesaurus integration in Site Management comboboxes**: Comboboxes for role/contract_type (Personnel), day_type (Attendance), category/status/ownership (Equipment), category (Budget) now populate from the thesaurus via query_thesaurus_batch() in the current UI language. Added LANG_TO_THESAURUS mapping in each tab. Updated pyarchinit_thesaurus_compatibility.py with mapping for the 4 cantiere tables.

#### File modificati / Modified files
- `tabs/Personale.py` - i18n expansion + thesaurus charge_list()
- `tabs/Presenze.py` - i18n expansion + thesaurus charge_list()
- `tabs/Attrezzature.py` - i18n expansion + thesaurus charge_list()
- `tabs/Budget.py` - i18n expansion + thesaurus charge_list()
- `modules/db/sqlite_db_updater.py` - update_site_management_thesaurus()
- `modules/db/postgres_db_updater.py` - update_site_management_thesaurus()
- `modules/utility/pyarchinit_thesaurus_compatibility.py` - cantiere table mappings

### Documentazione / Documentation

- **docs(tutorials): Tutorial spagnolo per il modulo Gestion de Obra (35_gestion_obra.md)**: Creato tutorial completo in spagnolo per il modulo Gestione Cantiere (~276 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Panel de Obra/Dashboard (selettori sito/anno, riepilogo budget con barra progresso codificata per colori e grafico a torta, riepilogo personale con presenti/vacaciones/baja e totali mensili ore/costi, riepilogo attrezzature con alert manutenzione, computo metrico con differenza DEM e DEM+poligono), Formulario de Personal (9 campi), Formulario de Asistencia (8 campi con tipi giornata: laboral/vacaciones/baja/permiso), Formulario de Equipamiento (11 campi con stati: en_uso/mantenimiento/fuera_servicio), Formulario de Presupuesto (7 campi con 7 categorie di spesa), flusso di lavoro operativo (configurazione iniziale e gestione giornaliera), FAQ, note tecniche con tabelle database e file sorgente. / **docs(tutorials): Spanish tutorial for Site Management module (35_gestion_obra.md)**: Created comprehensive Spanish tutorial for the Gestione Cantiere module (~276 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Panel de Obra/Dashboard (site/year selectors, budget summary with color-coded progress bar and pie chart, personnel summary with present/vacation/sick and monthly hour/cost totals, equipment summary with maintenance alerts, computo metrico with DEM difference and DEM+polygon), Personnel form (9 fields), Attendance form (8 fields with day types: laboral/vacaciones/baja/permiso), Equipment form (11 fields with states: en_uso/mantenimiento/fuera_servicio), Budget form (7 fields with 7 expense categories), operational workflow (initial setup and daily management), FAQ, technical notes with database tables and source files.

#### File creati / Created files
- `docs/tutorials/es/35_gestion_obra.md`

- **docs(tutorials): Tutorial greco moderno per il modulo Διαχειριση Εργοταξιου (35_διαχειριση_εργοταξιου.md)**: Creato tutorial completo in greco moderno per il modulo Gestione Cantiere (~495 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Πινακας Εργοταξιου/Dashboard (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione Computo Metrico con calcolo differenza DEM e DEM+poligono, storico), Φορμα Προσωπικου (9 campi), Φορμα Παρουσιων (8 campi con tabella tipo_giornata), Φορμα Εξοπλισμου (11 campi con tabella stato), Φορμα Προυπολογισμου (7 campi con categorie tipiche), flusso di lavoro operativo (6 passi), FAQ (7 domande), note tecniche con file sorgente e tabelle database. / **docs(tutorials): Modern Greek tutorial for Site Management module (35_διαχειριση_εργοταξιου.md)**: Created comprehensive Modern Greek tutorial for the Gestione Cantiere module (~495 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Πινακας Εργοταξιου/Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, Computo Metrico section with DEM difference and DEM+polygon calculation, history), Personnel form (9 fields), Attendance form (8 fields with day type table), Equipment form (11 fields with status table), Budget form (7 fields with typical categories), operational workflow (6 steps), FAQ (7 questions), technical notes with source files and database tables.

#### File creati / Created files
- `docs/tutorials/el/35_διαχειριση_εργοταξιου.md`

- **docs(tutorials): Tutorial portoghese europeo per il modulo Gestao de Obra (35_gestao_obra.md)**: Creato tutorial completo in portoghese europeo per il modulo Gestione Cantiere (~454 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone) e menu estensione, Painel de Obra/Dashboard (selettori sito/anno, riepilogo orcamento con barra progresso e grafico a torta, riepilogo pessoal con presenti/ferias/baixa e totali mensili ore/costi, riepilogo equipamentos con alert manutencao, computo metrico con differenza DEM e DEM+poligono e storico), Ficha de Pessoal (9 campi), Ficha de Presencas (8 campi con tipi di giornata), Ficha de Equipamentos (11 campi con stati), Ficha de Orcamento (7 campi con categorie suggerite), flussi di lavoro operativi (configurazione iniziale, routine giornaliera, aggiornamento budget, computo volumi), FAQ (7 domande), note tecniche con tabelle DB e file sorgente. / **docs(tutorials): European Portuguese tutorial for Site Management module (35_gestao_obra.md)**: Created comprehensive European Portuguese tutorial for the Gestione Cantiere module (~454 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons) and plugin menu, Painel de Obra/Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly hour/cost totals, equipment summary with maintenance alerts, computo metric with DEM difference and DEM+polygon and history), Personnel form (9 fields), Attendance form (8 fields with day types), Equipment form (11 fields with states), Budget form (7 fields with suggested categories), operational workflows (initial setup, daily routine, budget update, volume computation), FAQ (7 questions), technical notes with DB tables and source files.

#### File creati / Created files
- `docs/tutorials/pt/35_gestao_obra.md`

- **docs(tutorials): Tutorial arabo per il modulo إدارة الموقع (35_إدارة_الموقع.md)**: Creato tutorial completo in arabo per il modulo Gestione Cantiere (~517 righe). Copre: indice con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Dashboard/لوحة القيادة (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione computo metrico con calcolo differenza DEM e DEM+poligono, storico computi), Scheda Personale/الموظفون (18 campi), Scheda Presenze/الحضور (12 campi con tipi giornata), Scheda Attrezzature/المعدات (16 campi con stati), Scheda Budget/الميزانية (11 campi con categorie spesa), barra strumenti DBMS, flussi di lavoro operativi (setup iniziale + lavoro quotidiano + calcolo quantità), FAQ (7 domande), note tecniche con tabelle database. / **docs(tutorials): Arabic tutorial for Site Management module (35_إدارة_الموقع.md)**: Created comprehensive Arabic tutorial for the Gestione Cantiere module (~517 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, quantity surveying section with DEM difference and DEM+polygon, computo history), Personnel form (18 fields), Attendance form (12 fields with day types), Equipment form (16 fields with statuses), Budget form (11 fields with expense categories), DBMS toolbar, operational workflows (initial setup + daily work + quantity calculation), FAQ (7 questions), technical notes with database tables.

#### File creati / Created files
- `docs/tutorials/ar/35_إدارة_الموقع.md`

- **docs(tutorials): Tutorial tedesco per il modulo Baustellenverwaltung (35_baustellenverwaltung.md)**: Creato tutorial completo in tedesco per il modulo Gestione Cantiere (~300 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Baustellen-Dashboard (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione Massenberechnung con calcolo differenza DEM e DEM+poligono, storico computi), Personalformular (18 campi), Anwesenheitsformular (12 campi con tabella tipo_giornata), Ausruestungsformular (16 campi con tabella stato), Budgetformular (11 campi), flusso di lavoro operativo, FAQ, risoluzione problemi, note tecniche con file sorgente e tabelle database. / **docs(tutorials): German tutorial for Site Management module (35_baustellenverwaltung.md)**: Created comprehensive German tutorial for the Gestione Cantiere module (~300 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Baustellen-Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, Massenberechnung section with DEM difference and DEM+polygon calculation, computo history), Personnel form (18 fields), Attendance form (12 fields with tipo_giornata table), Equipment form (16 fields with stato table), Budget form (11 fields), operational workflow, FAQ, troubleshooting, technical notes with source files and database tables.

#### File creati / Created files
- `docs/tutorials/de/35_baustellenverwaltung.md`

- **docs(tutorials): Tutorial catalano per il modulo Gestio d'Obra (35_gestio_obra.md)**: Creato tutorial completo in catalano per il modulo Gestione Cantiere (~567 righe). Copre: indice con ancoraggi, introduzione al modulo, accesso dalla barra strumenti (5 icone), Tauler d'Obra/Dashboard (selettori lloc/any, riepilogo pressupost con barra di avanzamento e grafico a torta, riepilogo personale con presents/vacances/malaltia e totali mensili, riepilogo equipament con alert manteniment, sezione comput metric con calcolo differenza DEM e DEM+poligon, storico computi), Fitxa de Personal (18 campi), Fitxa d'Assistencia (12 campi), Fitxa d'Equipament (16 campi), Fitxa de Pressupost (11 campi), barra d'eines DBMS condivisa, flussi di lavoro operativi, FAQ, note tecniche. / **docs(tutorials): Catalan tutorial for Site Management module (35_gestio_obra.md)**: Created comprehensive Catalan tutorial for the Gestione Cantiere module (~567 lines). Covers: TOC with anchors, module introduction, toolbar access (5 icons), Tauler d'Obra dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, computo metric section with DEM difference and DEM+polygon, computo history), Personnel form (18 fields), Attendance form (12 fields), Equipment form (16 fields), Budget form (11 fields), shared DBMS toolbar, operational workflows, FAQ, technical notes.

#### File creati / Created files
- `docs/tutorials/ca/35_gestio_obra.md`

- **docs(tutorials): Tutorial romeno per il modulo Gestiune Santier (35_gestiune_santier.md)**: Creato tutorial completo in romeno per il modulo Gestione Cantiere (~457 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 formulari, accesso dalla barra strumenti (5 icone), Panou Santier/Dashboard (selettori sito/anno, riepilogo budget con barra progresso e grafico a torta, riepilogo personale con presenti/concediu/medical e totali mensili ore/costi, riepilogo attrezzature con alert manutenzione), Fisa Personal (18 campi), Fisa Prezente (12 campi con flusso tipico), Fisa Echipamente (16 campi con alert manutenzione), Fisa Buget (11 campi con categorie tipiche), Computo Metric (differenza DEM e DEM+Poligon, storico), flusso di lavoro operativo (configurazione iniziale, operazioni giornaliere, monitoraggio periodico), depanare, FAQ, note tecniche. / **docs(tutorials): Romanian tutorial for Site Management module (35_gestiune_santier.md)**: Created comprehensive Romanian tutorial for the Gestione Cantiere module (~457 lines). Covers: TOC with anchors, module introduction with 5-form table, toolbar access (5 icons), Panou Santier/Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/leave/medical and monthly hour/cost totals, equipment summary with maintenance alerts), Personnel form (18 fields), Attendance form (12 fields with typical workflow), Equipment form (16 fields with maintenance alerts), Budget form (11 fields with typical categories), Computo Metric (DEM difference and DEM+Polygon, history), operational workflow (initial setup, daily operations, periodic monitoring), troubleshooting, FAQ, technical notes.

#### File creati / Created files
- `docs/tutorials/ro/35_gestiune_santier.md`

- **docs(tutorials): Tutorial francese per il modulo Gestion de Chantier (35_gestion_chantier.md)**: Creato tutorial completo in francese per il modulo Gestione Cantiere (~480 righe). Copre: sommario con ancoraggi, introduzione al modulo, accesso dalla barra strumenti (5 icone), Tableau de Bord (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione metrages con calcolo differenza DEM e DEM+poligono, storico computi), Fiche Personnel (18 campi), Fiche Presences (12 campi), Fiche Equipements (16 campi), Fiche Budget (11 campi), flussi di lavoro operativi, FAQ, note tecniche. / **docs(tutorials): French tutorial for Site Management module (35_gestion_chantier.md)**: Created comprehensive French tutorial for the Gestione Cantiere module (~480 lines). Covers: TOC with anchors, module introduction, toolbar access (5 icons), Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary, equipment summary with maintenance alerts, metrages section with DEM difference and DEM+polygon, computo history), Personnel form (18 fields), Attendance form (12 fields), Equipment form (16 fields), Budget form (11 fields), operational workflows, FAQ, technical notes.

#### File creati / Created files
- `docs/tutorials/fr/35_gestion_chantier.md`

- **docs: Tutorial inglese per il modulo Site Management (35_site_management.md)**: Creato tutorial completo in inglese per il modulo Gestione Cantiere. Il tutorial copre tutte e 5 le componenti del modulo: Dashboard Cantiere (riepilogo budget con grafico a torta, riepilogo personale, riepilogo attrezzature con alert manutenzione, computo metrico con calcolo differenza DEM e statistiche zonali), form CRUD Personale (18 campi inclusi ruolo, qualifica, tariffe, contratto), form CRUD Presenze (12 campi inclusi tipo giornata, ore ordinarie/straordinario, turno, area di lavoro), form CRUD Attrezzature (17 campi inclusi stato, costi, date manutenzione), form CRUD Budget (11 campi inclusi importo previsto/effettivo, fornitore, fattura). Include: indice con ancore, workflow operativo completo, sezione FAQ, note tecniche con tabelle database e file sorgente. / **docs: English tutorial for the Site Management module (35_site_management.md)**: Created comprehensive English tutorial for the Gestione Cantiere module. The tutorial covers all 5 module components: Site Dashboard (budget summary with pie chart, personnel summary, equipment summary with maintenance alerts, computo metrico with DEM difference calculation and zonal statistics), Personnel CRUD form (18 fields including role, qualification, rates, contract), Attendance CRUD form (12 fields including day type, regular/overtime hours, shift, work area), Equipment CRUD form (17 fields including status, costs, maintenance dates), Budget CRUD form (11 fields including estimated/actual amounts, supplier, invoice). Includes: table of contents with anchors, complete operational workflow, FAQ section, technical notes with database tables and source files.

#### File creati / Created files
- `docs/tutorials/en/35_site_management.md`

---

## [5.0.5-alpha] - 2026-02-20

### Corretto / Fixed

- **fix(db): Autenticazione password fallita nelle funzioni admin (#660)** (commit `4bdff5cb`): In SQLAlchemy 2.0, `str(engine.url)` maschera le password come `***`, causando il fallimento di `psycopg2.connect()` nelle funzioni `apply_concurrency_system()` e `update_database_schema()`. Corretto accedendo direttamente agli attributi dell'oggetto `engine.url` (host, port, database, username, password) invece di convertire l'URL in stringa. / **fix(db): Resolve password auth failure in admin functions (#660)** (commit `4bdff5cb`): In SQLAlchemy 2.0, `str(engine.url)` masks passwords as `***`, causing `psycopg2.connect()` to fail in `apply_concurrency_system()` and `update_database_schema()`. Fixed by accessing `engine.url` object attributes (host, port, database, username, password) directly instead of converting the URL to a string.

- **fix(db): SQLite updater non creava le nuove tabelle Site Management (#660)** (commit `9d053ed9`): Aggiunti controlli `needs_update()` per 5 nuove tabelle del modulo Site Management (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) e per `inventario_lapidei_table`. Corretto `test2()` per eseguire solo su SQLite e chiudere correttamente le connessioni. Aggiunto metodo `apply_sito_set()` alla dashboard Cantiere. / **fix(db): SQLite updater not creating new site management tables (#660)** (commit `9d053ed9`): Added `needs_update()` checks for 5 new Site Management module tables (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) and for `inventario_lapidei_table`. Fixed `test2()` to only run for SQLite and properly close connections. Added `apply_sito_set()` method to the Cantiere dashboard.

- **fix(db): Aggiunta inventario_lapidei_table e fix stringa connessione DB_update (#660)** (commit `6223cb73`): Usato `render_as_string(hide_password=False)` per ottenere la stringa di connessione corretta in DB_update, evitando il mascheramento della password. Creata `inventario_lapidei_table` sia nel SQLite updater che nel PostgreSQL updater: la tabella era referenziata nelle viste SQL del sistema di concorrenza ma non era mai stata creata, causando errori durante `apply_concurrency_system()`. / **fix(db): Add inventario_lapidei_table and fix DB_update password auth (#660)** (commit `6223cb73`): Used `render_as_string(hide_password=False)` to get the correct connection string in DB_update, avoiding password masking. Created `inventario_lapidei_table` in both SQLite and PostgreSQL updaters: the table was referenced in concurrency system SQL views but had never been created, causing errors during `apply_concurrency_system()`.

- **fix(db): Backport correzioni password auth su branch qt6-migration (#660)** (commit `9a5c7dae` su `feature/qt6-migration`): Portate le stesse correzioni per l'autenticazione password (`engine.url` attributes e `render_as_string(hide_password=False)`) e la creazione di `inventario_lapidei_table` sul branch `feature/qt6-migration`, senza le tabelle Site Management. / **fix(db): Backport password auth fixes to qt6-migration branch (#660)** (commit `9a5c7dae` on `feature/qt6-migration`): Backported the same password authentication fixes (`engine.url` attributes and `render_as_string(hide_password=False)`) and `inventario_lapidei_table` creation to the `feature/qt6-migration` branch, without the Site Management tables.

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (fix `str(engine.url)` password masking, `render_as_string(hide_password=False)`, attributi `engine.url` per psycopg2)
- `modules/db/sqlite_db_updater.py` (aggiunti `needs_update()` per 6 tabelle, creazione `inventario_lapidei_table`)
- `modules/db/postgres_db_updater.py` (creazione `inventario_lapidei_table`)
- `tabs/Cantiere.py` (aggiunto metodo `apply_sito_set()`)

---

## [5.0.5-alpha] - 2026-02-20

### Aggiunto / Added
- **Dashboard Controller Cantiere (Cantiere.py)**: Creato il controller dashboard `tabs/Cantiere.py` che aggrega i dati dalle 4 tabelle del modulo Site Management (Budget, Presenze, Attrezzature, Computo Metrico). Non e' un form CRUD standard ma una vista di aggregazione/dashboard. Include: riepilogo budget con progress bar e grafico a torta matplotlib, riepilogo personale presente oggi con totali mensili ore/costi, riepilogo attrezzature con alert scadenze manutenzione, calcolo computo metrico GIS (differenza DEM e DEM su poligono) tramite QgsRasterCalculator e QgsZonalStatistics, storico computi in QTableWidget, salvataggio risultati calcolo nel database. Supporto i18n per 10 lingue nei titoli. Segue il pattern di connessione DB singleton da `Personale.py`. / Created the dashboard controller `tabs/Cantiere.py` that aggregates data from the 4 Site Management module tables (Budget, Presenze, Attrezzature, Computo Metrico). This is NOT a standard CRUD form but an aggregation/dashboard view. Includes: budget summary with progress bar and matplotlib pie chart, today's personnel summary with monthly hour/cost totals, equipment summary with overdue maintenance alerts, GIS computo metrico calculation (DEM difference and DEM over polygon) via QgsRasterCalculator and QgsZonalStatistics, computo history in QTableWidget, saving calculation results to database. i18n support for 10 languages in titles. Follows the DB singleton connection pattern from `Personale.py`.

#### File creati / Created files
- `tabs/Cantiere.py`

- **Controller CRUD Tab per Site Management**: Creati 4 controller tab Python per il modulo Site Management: `Personale.py`, `Presenze.py`, `Attrezzature.py`, `Budget.py`. Ogni controller segue esattamente il pattern di `Periodizzazione.py` con: supporto i18n per 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el), integrazione ThemeManager, operazioni CRUD complete via `get_db_manager()` singleton, navigazione record, ricerca/ordinamento, gestione sito, metodi `fill_fields`/`empty_fields`/`insert_new_rec`/`update_record`. Presenze.py include metodi extra `calculate_hours()` e `calculate_cost()`. Attrezzature.py include `check_maintenance_alert()` per avvisi scadenza manutenzione. / Created 4 Python tab controllers for the Site Management module: `Personale.py`, `Presenze.py`, `Attrezzature.py`, `Budget.py`. Each controller follows the exact `Periodizzazione.py` pattern with: i18n support for 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el), ThemeManager integration, full CRUD operations via `get_db_manager()` singleton, record navigation, search/sort, site management, `fill_fields`/`empty_fields`/`insert_new_rec`/`update_record` methods. Presenze.py includes extra `calculate_hours()` and `calculate_cost()` methods. Attrezzature.py includes `check_maintenance_alert()` for maintenance due date warnings.

#### File creati / Created files
- `tabs/Personale.py`
- `tabs/Presenze.py`
- `tabs/Attrezzature.py`
- `tabs/Budget.py`

- **Database Updaters per Site Management**: Aggiunti metodi CREATE TABLE per le 5 nuove tabelle (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) sia nel SQLite updater che nel PostgreSQL updater. I database esistenti riceveranno le nuove tabelle automaticamente alla prossima connessione. Il SQLite updater usa `self.cursor.execute()` con `table_exists()` guard, il PostgreSQL updater usa il pattern `with self.db_manager.engine.connect()` con `sqlalchemy.text()` e `COMMIT` esplicito. / Added CREATE TABLE methods for the 5 new tables (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) to both the SQLite and PostgreSQL database updaters. Existing databases will receive the new tables automatically on next connection. The SQLite updater uses `self.cursor.execute()` with `table_exists()` guard; the PostgreSQL updater uses the `with self.db_manager.engine.connect()` pattern with `sqlalchemy.text()` and explicit `COMMIT`.

#### File modificati / Modified files
- `modules/db/sqlite_db_updater.py`
- `modules/db/postgres_db_updater.py`

- **Mapper registration + DB Manager per Site Management**: Registrate le 5 nuove entita (PERSONALE, PRESENZE, ATTREZZATURE, BUDGET, COMPUTO_METRICO) nel sistema di mapping SQLAlchemy e nel DB manager. Aggiunti import entita e strutture, chiamate `mapper()`, 5 metodi `insert_*_values()`, e voci nei dizionari `table_classes` di `query_bool` e `group_by`. / Registered the 5 new entity classes (PERSONALE, PRESENZE, ATTREZZATURE, BUDGET, COMPUTO_METRICO) in the SQLAlchemy mapping system and DB manager. Added entity and structure imports, `mapper()` calls, 5 `insert_*_values()` methods, and entries in the `table_classes` dictionaries of `query_bool` and `group_by`.

#### File modificati / Modified files
- `modules/db/pyarchinit_db_mapper.py`
- `modules/db/pyarchinit_db_manager.py`

- **Strutture tabelle Site Management**: Creati 10 file di definizione tabelle per il modulo Site Management (5 in `modules/db/structures/` e 5 in `modules/db/structures_metadata/`). Le tabelle coprono: personale (`personale_table`), presenze (`presenze_table`), attrezzature (`attrezzature_table`), budget (`budget_table`) e computo metrico (`computo_metrico_table`). Le strutture seguono i pattern esistenti del progetto (Pattern A con `MetaData()` a livello di classe e Pattern B con `@classmethod define_table`). / Created 10 table definition files for the Site Management module (5 in `modules/db/structures/` and 5 in `modules/db/structures_metadata/`). Tables cover: personnel (`personale_table`), attendance (`presenze_table`), equipment (`attrezzature_table`), budget (`budget_table`) and metric computation (`computo_metrico_table`). Structures follow existing project patterns (Pattern A with class-level `MetaData()` and Pattern B with `@classmethod define_table`).

#### File creati / Created files
- `modules/db/structures/Personale_table.py`
- `modules/db/structures/Presenze_table.py`
- `modules/db/structures/Attrezzature_table.py`
- `modules/db/structures/Budget_table.py`
- `modules/db/structures/Computo_metrico_table.py`
- `modules/db/structures_metadata/Personale_table.py`
- `modules/db/structures_metadata/Presenze_table.py`
- `modules/db/structures_metadata/Attrezzature_table.py`
- `modules/db/structures_metadata/Budget_table.py`
- `modules/db/structures_metadata/Computo_metrico_table.py`

---

## [5.0.5-alpha] - 2026-02-19

### Corretto / Fixed
- **Import geometrie PostgreSQL #659**: La clausola `ON CONFLICT` veniva aggiunta dopo `RETURNING` nella SQL generata, causando un `SyntaxError`. Corretto posizionando `ON CONFLICT` prima di `RETURNING` in tutti e tre i gestori di import (replace/ignore/abort). / The `ON CONFLICT` clause was appended after `RETURNING` in the generated SQL, causing a `SyntaxError`. Fixed by inserting `ON CONFLICT` before `RETURNING` in all three import mode handlers (replace/ignore/abort).

---

## [5.0.5-alpha] - 2026-02-19

### Corretto / Fixed
- **Import PostgreSQL #658**: Aggiunto helper `_pg_quote()` nel codice di importazione tabelle per quotare i nomi di colonna con lettere maiuscole (es. `id_mediaToEntity`) nella clausola `ON CONFLICT DO UPDATE SET`. PostgreSQL fa il fold dei nomi non quotati a lowercase causando un `UndefinedColumn`. / Added `_pg_quote()` helper in the table import code to double-quote mixed-case column names (e.g. `id_mediaToEntity`) in `ON CONFLICT DO UPDATE SET`. PostgreSQL folds unquoted identifiers to lowercase, causing `UndefinedColumn` errors.

---

## [5.0.5-alpha] - 2026-02-19

### Corretto / Fixed
- **Schema PostgreSQL #657**: Aggiunto `quota_usm`, `unita_misura_quota`, `photo_id`, `drawing_id`, `audit_trail` al CREATE TABLE di `inventario_materiali_table` in `pyarchinit_schema_updated.sql`. I nuovi database PostgreSQL ora includono tutte le colonne necessarie fin dalla creazione. Aggiornati anche i template SQLite (`pyarchinit.sqlite`, `pyarchinit_db.sqlite`). / Added missing columns (`quota_usm`, `unita_misura_quota`, `photo_id`, `drawing_id`, `audit_trail`) to the `inventario_materiali_table` CREATE TABLE in `pyarchinit_schema_updated.sql`. Newly created PostgreSQL databases now include all required columns. Also updated SQLite template files.

---

## [5.0.5-alpha] - 2026-02-19

### Aggiunto / Added
- **Traduzioni ro/pt/el**: Aggiunte traduzioni complete per Rumeno (ro_RO), Portoghese (pt_PT) e Greco (el_GR) con ~2100+ stringhe tradotte per ciascuna lingua. Aggiornato pyarchinit.pro per includere le tre lingue. / Added complete translations for Romanian (ro_RO), Portuguese (pt_PT) and Greek (el_GR) with ~2100+ strings translated per language. Updated pyarchinit.pro to include all three languages.
- **Combobox US/USM dinamico**: Il combobox del tipo di unità stratigrafica (US/USM) viene ora popolato dinamicamente in base alla lingua impostata in QGIS. / The stratigraphic unit type combobox (US/USM) is now dynamically populated based on the language set in QGIS.

---

## [5.3.20-alpha] - 2026-02-18

### feat(i18n): Add Romanian, Portuguese, and Greek translations

- **IT**: Infrastruttura di traduzione aggiornata e traduzioni generate per tre nuove lingue: rumeno (ro_RO), portoghese (pt_PT) e greco (el_GR). (1) **pyarchinit.pro**: Aggiunte le voci mancanti per ro_RO, pt_PT e el_GR nella variabile TRANSLATIONS. (2) **Traduzione dei file .ts**: Scritto ed eseguito script Python che utilizza dizionari completi di termini UI comuni e vocabolario archeologico per tradurre i blocchi <message> dei file .ts dal testo inglese nelle rispettive lingue target. Tradotti 1.044 blocchi per il rumeno, 1.055 per il portoghese e 1.081 per il greco, coprendo etichette di pulsanti, voci di menu, termini GIS/archeologici e frasi comuni dell'interfaccia. (3) **Compilazione file .qm**: Compilati i file .qm binari usando lrelease di PySide6. Ciascun file compila 2.734 traduzioni finite con 92 stringhe sorgente non tradotte ignorate. Le dimensioni dei file confermano l'incorporamento corretto delle traduzioni (ro: 295KB, pt: 296KB, el: 296KB vs. 292KB quando erano copie solo in inglese).
- **EN**: Updated translation infrastructure and generated translations for three new languages: Romanian (ro_RO), Portuguese (pt_PT), and Greek (el_GR). (1) **pyarchinit.pro**: Added missing entries for ro_RO, pt_PT, and el_GR to the TRANSLATIONS variable. (2) **.ts file translation**: Wrote and executed Python script using comprehensive dictionaries of common UI terms and archaeological vocabulary to translate .ts file <message> blocks from English text into respective target languages. Translated 1,044 blocks for Romanian, 1,055 for Portuguese, and 1,081 for Greek, covering button labels, menu items, GIS/archaeological terms, and common UI phrases. (3) **.qm compilation**: Compiled binary .qm files using PySide6's lrelease. Each file compiles 2,734 finished translations with 92 untranslated source texts ignored. File sizes confirm correct translation embedding (ro: 295KB, pt: 296KB, el: 296KB vs. 292KB when they were English-only copies).

#### File modificati / Modified files
- `pyarchinit.pro` (aggiunte voci TRANSLATIONS per ro_RO, pt_PT, el_GR)
- `i18n/pyarchinit_plugin_ro_RO.ts` (1.044 stringhe tradotte in rumeno)
- `i18n/pyarchinit_plugin_pt_PT.ts` (1.055 stringhe tradotte in portoghese)
- `i18n/pyarchinit_plugin_el_GR.ts` (1.081 stringhe tradotte in greco)
- `i18n/pyarchinit_plugin_ro_RO.qm` (file binario compilato)
- `i18n/pyarchinit_plugin_pt_PT.qm` (file binario compilato)
- `i18n/pyarchinit_plugin_el_GR.qm` (file binario compilato)

---

## [5.3.19-alpha] - 2026-02-18

### fix(postgres): Non-blocking PostgreSQL version check and improved error handling (#656)

- **IT**: Risolto il problema di blocco della pipeline save/connect quando il controllo della versione PostgreSQL fallisce. (1) **select_version_sql() non-bloccante**: la funzione ora restituisce `None` se il controllo della versione fallisce, invece di sollevare un'eccezione che interrompe l'intero flusso. Questa modifica consente al plugin di continuare a funzionare anche quando il database non supporta il controllo della versione o quando si verificano errori transitori di connessione. (2) **Messaggi di errore migliorati**: sostituite le eccezioni generiche "Problema di connessione al db" con messaggi di errore dettagliati che mostrano l'effettivo errore restituito dal database, migliorando notevolmente la diagnostica per gli utenti. (3) **Corretta perdita di risorse**: aggiunto `engine.dispose()` dopo il controllo della versione SQLAlchemy per garantire il rilascio adeguato delle risorse del pool di connessioni.
- **EN**: Fixed issue where PostgreSQL version check failure blocked the entire save/connect pipeline. (1) **Non-blocking select_version_sql()**: function now returns `None` if version check fails instead of raising an exception that blocks the entire flow. This allows the plugin to continue working even when the database doesn't support version checking or transient connection errors occur. (2) **Improved error messages**: replaced generic "Problema di connessione al db" exceptions with detailed error messages showing the actual database error, significantly improving diagnostics for users. (3) **Fixed resource leak**: added `engine.dispose()` after SQLAlchemy version check to ensure proper cleanup of connection pool resources.

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (reso non-bloccante select_version_sql(), migliorati messaggi errore)
- `metadata.txt` (versione patch)

---

## [5.3.22-alpha] - 2026-02-17

### feat(ui): Splash screen non-bloccante con durata minima 5s / Smooth non-blocking splash screen with 5s minimum duration

- **IT**: Reso lo splash screen non-bloccante con chiamate `processEvents()` durante l'inizializzazione, garantendo che la UI rimanga reattiva. Aggiunta durata minima di 5 secondi con messaggi di stato rotanti. Aggiunta animazione di fade-out di 0.6s. Lo splash non si blocca piu durante le operazioni pesanti di init.
- **EN**: Made splash screen non-blocking with `processEvents()` calls during initialization, ensuring the UI remains responsive. Added 5-second minimum duration with rotating status messages. Added smooth 0.6s fade-out animation. Splash no longer freezes during heavy init operations.

#### File modificati / Modified files
- `pyarchinitPlugin.py` (splash screen non-bloccante con processEvents, durata minima 5s, fade-out animato)

---

## [5.3.21-alpha] - 2026-02-17

### fix(db): Compatibilita SQLAlchemy 2.x in db_createdump e db_migrations / SQLAlchemy 2.x compatibility in db_createdump and db_migrations

- **IT**: Risolto errore `'Connection' object has no attribute 'rollback'/'commit'` in `db_createdump.py`. Cambiato al pattern esplicito `transaction = conn.begin()` compatibile con SA 1.x e 2.x. Corretto `db_migrations.py` per usare il context manager `engine.begin()`.
- **EN**: Fixed `'Connection' object has no attribute 'rollback'/'commit'` error in `db_createdump.py`. Changed to explicit `transaction = conn.begin()` pattern compatible with SA 1.x and 2.x. Fixed `db_migrations.py` to use `engine.begin()` context manager.

#### File modificati / Modified files
- `modules/db/db_createdump.py` (pattern transazione esplicito per SA 2.x / explicit transaction pattern for SA 2.x)
- `modules/db/db_migrations.py` (engine.begin() context manager)

---

## [5.3.20-alpha] - 2026-02-17

### fix(deps): Gestione commenti inline in requirements.txt / Strip inline comments from requirements.txt when parsing versions

- **IT**: Risolto `ValueError` quando le righe di `requirements.txt` contengono commenti inline come `pkg>=1.0  # Optional`. Il parser ora rimuove i commenti prima di confrontare le versioni.
- **EN**: Fixed `ValueError` when `requirements.txt` lines have inline comments like `pkg>=1.0  # Optional`. The parser now strips comments before comparing versions.

#### File modificati / Modified files
- `__init__.py` (strip dei commenti inline nel parsing di requirements.txt)

---

## [5.3.19-alpha] - 2026-02-17

### fix(deps): Isolamento dipendenze plugin con ext_libs e correzione compatibilita versioni / Isolate plugin dependencies with ext_libs and fix version compatibility

- **IT**: Creata directory `ext_libs/` per isolare le dipendenze del plugin dai pacchetti bundled di QGIS. Corretti tutti i pin `==` in `requirements.txt` sostituiti con versioni minime `>=` (molte versioni pinnate non esistevano per Python 3.9). Corrette le versioni dei pacchetti langchain (erano completamente inventate, es. `langchain==1.2.10` non esiste). Aggiunta lista `QGIS_PROTECTED_PACKAGES` per evitare di sovrascrivere numpy, scipy, sip, pyqt5. Corretto `PackageManager.install()` su tutte le piattaforme per installare in `ext_libs/` con `--target`. Corretta logica di confronto versioni per pacchetti 0.x (es. GeoAlchemy2 0.9 vs 0.18).
- **EN**: Created `ext_libs/` directory for dependency isolation from QGIS-bundled packages. Fixed all pinned `==` versions in `requirements.txt` replaced with `>=` minimum versions (many pinned versions didn't exist for Python 3.9). Fixed langchain package versions (were completely fabricated, e.g. `langchain==1.2.10` doesn't exist). Added `QGIS_PROTECTED_PACKAGES` to prevent overriding numpy, scipy, sip, pyqt5. Fixed `PackageManager.install()` on all platforms to install to `ext_libs/` with `--target`. Fixed version checking logic for 0.x packages (GeoAlchemy2 0.9 vs 0.18).

#### File creati / Created files
- `ext_libs/` (directory per dipendenze isolate del plugin / directory for isolated plugin dependencies)

#### File modificati / Modified files
- `requirements.txt` (tutte le versioni corrette da == a >= con versioni reali / all versions fixed from == to >= with real versions)
- `__init__.py` (QGIS_PROTECTED_PACKAGES, PackageManager.install con --target ext_libs, logica confronto versioni 0.x / QGIS_PROTECTED_PACKAGES, PackageManager.install with --target ext_libs, 0.x version comparison logic)
- `modules/db/db_createdump.py` (compatibilita SA 2.x / SA 2.x compatibility)
- `modules/db/db_migrations.py` (engine.begin() context manager)

---

## [5.3.17-alpha] - 2026-02-17

### feat(rust): Phase 5 — Pipeline di distribuzione modulo Rust / Phase 5 — Rust module distribution pipeline

- **IT**: Implementata la pipeline completa di distribuzione per il modulo opzionale di accelerazione Rust `pyarchinit_core`. (1) **CI/CD**: Creato workflow GitHub Actions `.github/workflows/build-rust.yml` che compila wheel cross-platform (Linux x86_64, Windows x86_64, macOS universal2) usando `maturin-action`, con trigger su tag `rust-v*` e pubblicazione automatica come GitHub Release. (2) **Installer**: Creato `scripts/rust_installer.py` con funzioni `check_rust_available()` (verifica importabilita e versione) e `install_rust_acceleration()` (rileva piattaforma/architettura, costruisce URL wheel corretto, installa via pip dal GitHub Release). (3) **Pannello impostazioni**: Aggiunto tab "Rust Acceleration" nel dialog di configurazione (`gui/pyarchinitConfigDialog.py`) con: stato del modulo (installato/non installato con versione), checkbox per abilitare/disabilitare l'accelerazione (persistita in `QgsSettings pyArchInit/rust_acceleration_enabled`), pulsante Install/Update con feedback visivo, e dettagli tecnici sugli algoritmi accelerati. (4) **Indicatore di stato**: Aggiunto log message all'avvio del plugin (`pyarchinitPlugin.py`) che riporta lo stato dell'accelerazione Rust nel pannello messaggi di QGIS.
- **EN**: Implemented the complete distribution pipeline for the optional Rust acceleration module `pyarchinit_core`. (1) **CI/CD**: Created GitHub Actions workflow `.github/workflows/build-rust.yml` that builds cross-platform wheels (Linux x86_64, Windows x86_64, macOS universal2) using `maturin-action`, triggered on `rust-v*` tags with automatic GitHub Release publishing. (2) **Installer**: Created `scripts/rust_installer.py` with `check_rust_available()` (checks importability and version) and `install_rust_acceleration()` (detects platform/architecture, builds correct wheel URL, installs via pip from GitHub Release). (3) **Settings panel**: Added "Rust Acceleration" tab to the configuration dialog (`gui/pyarchinitConfigDialog.py`) with: module status (installed/not installed with version), checkbox to enable/disable acceleration (persisted in `QgsSettings pyArchInit/rust_acceleration_enabled`), Install/Update button with visual feedback, and technical details about accelerated algorithms. (4) **Status indicator**: Added startup log message (`pyarchinitPlugin.py`) that reports Rust acceleration status in the QGIS message log panel.

#### File creati / Created files
- `.github/workflows/build-rust.yml` (CI/CD workflow cross-platform wheel build)
- `scripts/rust_installer.py` (installer e checker per modulo Rust)

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (aggiunto tab Rust Acceleration con UI gestione modulo)
- `pyarchinitPlugin.py` (aggiunto log stato Rust all'avvio plugin)

---

## [5.3.18-alpha] - 2026-02-17

### feat(rust): Phase 4 — Layout Sugiyama per Harris Matrix / Phase 4 — Sugiyama Harris Matrix layout engine

- **IT**: Implementato l'algoritmo di layout a livelli Sugiyama completo nel modulo Rust `matrix` (`_rust_core/src/matrix/mod.rs`) per la visualizzazione della Harris Matrix senza dipendenza da graphviz/dot per il posizionamento dei nodi. L'algoritmo comprende 4 fasi: (1) **Assegnazione livelli**: algoritmo longest-path basato su Kahn con supporto opzionale per vincoli di raggruppamento per fase (nodi contemporanei sullo stesso livello); (2) **Inserimento nodi dummy**: per archi che attraversano livelli multipli, inserimento di nodi virtuali per mantenere l'instradamento corretto degli archi; (3) **Minimizzazione incroci**: euristica del baricentro con sweep alternati top-down/bottom-up (6 iterazioni configurabili); (4) **Assegnazione coordinate**: posizionamento mediano con risoluzione sovrapposizioni e centratura dei livelli. Integrato nella pipeline di esportazione matrix (`modules/utility/pyarchinit_matrix_exp.py`): aggiunta funzione `_rust_transitive_reduction()` che sostituisce il subprocess `tred` usando il modulo Rust `graph.transitive_reduction()`, con fallback automatico al subprocess. Tutti e 4 i punti di chiamata `tred` in `HarrisMatrix.export_matrix`, `export_matrix_2`, `ViewHarrisMatrix.export_matrix` e `export_matrix_3` ora provano prima Rust e ricadono sul subprocess automaticamente. Aggiunte anche le funzioni pubbliche `rust_harris_layout()` e `rust_layout_to_dot()` per uso programmatico del layout engine.
- **EN**: Implemented the complete Sugiyama layered layout algorithm in the Rust `matrix` module (`_rust_core/src/matrix/mod.rs`) for Harris Matrix visualization without dependency on graphviz/dot for node positioning. The algorithm comprises 4 phases: (1) **Layer assignment**: longest-path algorithm based on Kahn's topological sort with optional phase group constraints (contemporary nodes on same layer); (2) **Dummy node insertion**: for edges spanning multiple layers, virtual nodes are inserted to maintain proper edge routing; (3) **Crossing minimization**: barycenter heuristic with alternating top-down/bottom-up sweeps (6 configurable iterations); (4) **Coordinate assignment**: median positioning with overlap resolution and layer centering. Integrated into the matrix export pipeline (`modules/utility/pyarchinit_matrix_exp.py`): added `_rust_transitive_reduction()` function that replaces the `tred` subprocess using the Rust `graph.transitive_reduction()` module, with automatic fallback to subprocess. All 4 `tred` call sites in `HarrisMatrix.export_matrix`, `export_matrix_2`, `ViewHarrisMatrix.export_matrix`, and `export_matrix_3` now try Rust first and fall back to subprocess automatically. Also added public functions `rust_harris_layout()` and `rust_layout_to_dot()` for programmatic use of the layout engine.

#### File modificati / Modified files
- `_rust_core/src/matrix/mod.rs` (implementazione completa Sugiyama: layer assignment, dummy nodes, crossing minimization, coordinate assignment)
- `modules/utility/pyarchinit_matrix_exp.py` (Rust fast path per tred + funzioni layout pubbliche)

---

## [5.3.16-alpha] - 2026-02-17

### feat(rust): Phase 3 — Modulo geostatistico Rust / Phase 3 — Rust geostatistics module

- **IT**: Implementato il modulo geostatistico completo in Rust (`_rust_core/src/geostat/mod.rs`) con 5 funzioni ad alte prestazioni: (1) `calculate_variogram` -- calcolo variogramma empirico con binning per lag e computazione pairwise parallelizzata via rayon; (2) `ordinary_kriging` -- kriging ordinario su griglia regolare con matrice di covarianza, risoluzione del sistema lineare via LU decomposition (nalgebra) e parallelizzazione per cella via rayon, supporta 4 modelli di variogramma (sferico, esponenziale, gaussiano, lineare); (3) `idw_interpolation` -- interpolazione IDW (Inverse Distance Weighting) parallelizzata con raggio di ricerca opzionale; (4) `maximin_design` -- campionamento ottimale maximin greedy per la selezione di nuovi punti di campionamento che massimizzano la distanza minima dai punti esistenti; (5) `cross_validate_kriging` -- cross-validation leave-one-out parallelizzata per kriging con sottocampionamento deterministico. Aggiornato il bridge Python `modules/_rust_bridge.py` con metodi wrapper per tutte le 5 funzioni geostatistiche. Integrati fast path Rust in `modules/geoarchaeo/core/geostat_engine.py` (variogramma, kriging, cross-validation) e in `modules/analysis/ut_heatmap_generator.py` (IDW), ciascuno con fallback automatico alle implementazioni Python in caso di errore.
- **EN**: Implemented the complete geostatistics module in Rust (`_rust_core/src/geostat/mod.rs`) with 5 high-performance functions: (1) `calculate_variogram` -- empirical variogram computation with lag binning and rayon-parallelized pairwise distance/semivariance calculation; (2) `ordinary_kriging` -- ordinary kriging on regular grid with covariance matrix, LU decomposition solver (nalgebra) and per-cell rayon parallelization, supporting 4 variogram models (spherical, exponential, gaussian, linear); (3) `idw_interpolation` -- parallelized IDW (Inverse Distance Weighting) interpolation with optional search radius; (4) `maximin_design` -- greedy maximin optimal sampling design for selecting new sample points that maximize minimum distance to existing points; (5) `cross_validate_kriging` -- parallelized leave-one-out cross-validation for kriging with deterministic subsampling. Updated Python bridge `modules/_rust_bridge.py` with wrapper methods for all 5 geostatistical functions. Integrated Rust fast paths into `modules/geoarchaeo/core/geostat_engine.py` (variogram, kriging, cross-validation) and `modules/analysis/ut_heatmap_generator.py` (IDW), each with automatic fallback to Python implementations on error.

#### File modificati / Modified files
- `_rust_core/src/geostat/mod.rs` (implementazione completa: variogramma, kriging, IDW, maximin, cross-validation)
- `modules/_rust_bridge.py` (aggiunti 5 metodi wrapper geostatistici)
- `modules/geoarchaeo/core/geostat_engine.py` (Rust fast path per variogramma, kriging, cross-validation)
- `modules/analysis/ut_heatmap_generator.py` (Rust fast path per IDW)

---

## [5.3.15-alpha] - 2026-02-17

### feat(rust): Phase 2 — Scaffolding modulo Rust pyarchinit_core / Phase 2 — Rust pyarchinit_core module scaffolding

- **IT**: Creato il crate Rust `pyarchinit_core` con PyO3 0.22 (abi3-py39) per accelerazione opzionale del plugin. Il modulo `graph` implementa tre algoritmi: (1) `topological_sort_with_levels` (algoritmo di Kahn con raggruppamento per livelli), (2) `detect_and_remove_cycles` (DFS iterativo per rilevamento e rimozione cicli), (3) `transitive_reduction` (algoritmo di Warshall per riduzione transitiva, sostituisce il subprocess `tred`). I moduli `geostat` e `matrix` sono placeholder per le fasi 3-4. Creato il bridge Python `modules/_rust_bridge.py` con pattern singleton lazy-loading e graceful degradation (il plugin funziona anche senza il modulo Rust). Integrato il Rust engine in `Order_layer_graph._remove_cycles()` e `_topological_sort_with_levels()` con fallback automatico alle implementazioni Python. Build verificato con maturin 1.12 su macOS ARM64.
- **EN**: Created `pyarchinit_core` Rust crate with PyO3 0.22 (abi3-py39) for optional plugin acceleration. The `graph` module implements three algorithms: (1) `topological_sort_with_levels` (Kahn's algorithm with level grouping), (2) `detect_and_remove_cycles` (iterative DFS for cycle detection and removal), (3) `transitive_reduction` (Warshall's algorithm for transitive reduction, replaces `tred` subprocess). `geostat` and `matrix` modules are placeholders for phases 3-4. Created Python bridge `modules/_rust_bridge.py` with lazy-loading singleton pattern and graceful degradation (plugin works without Rust module). Integrated Rust engine into `Order_layer_graph._remove_cycles()` and `_topological_sort_with_levels()` with automatic fallback to Python implementations. Build verified with maturin 1.12 on macOS ARM64.

#### File creati / Created files
- `_rust_core/Cargo.toml`, `_rust_core/pyproject.toml` (configurazione crate/build)
- `_rust_core/src/lib.rs` (entry point #[pymodule])
- `_rust_core/src/graph/mod.rs` (topo_sort, cycle detection, tred)
- `_rust_core/src/geostat/mod.rs`, `_rust_core/src/matrix/mod.rs` (placeholder)
- `modules/_rust_bridge.py` (bridge Python con graceful degradation)

#### File modificati / Modified files
- `modules/gis/pyarchinit_pyqgis.py` (Rust fast path in _remove_cycles e _topological_sort_with_levels)
- `.gitignore` (aggiunto `_rust_core/target/`)

---

## [5.3.14-alpha] - 2026-02-17

### perf: Phase 1 — Ottimizzazioni prestazioni Python / Phase 1 — Python Performance Optimizations

#### Gruppo A: Order Layer (`modules/gis/pyarchinit_pyqgis.py`)

- **IT**: (1) Sostituito `eval()` con `ast.literal_eval()` in `_build_graph()` — sicurezza e prestazioni. (2) Riscritta `_remove_cycles()` da DFS ricorsivo O(N²) a iterativo O(N+E) con stack esplicito e `path_set`. (3) Riscritta `update_database_with_order()` con singola query batch `UPDATE ... SET order_layer = CASE WHEN ... END` invece di N query + N `clear_cache()`.
- **EN**: (1) Replaced `eval()` with `ast.literal_eval()` in `_build_graph()` — security and performance. (2) Rewrote `_remove_cycles()` from recursive O(N²) DFS to iterative O(N+E) with explicit stack and `path_set`. (3) Rewrote `update_database_with_order()` with single batch `UPDATE ... SET order_layer = CASE WHEN ... END` instead of N queries + N `clear_cache()` calls.

#### Gruppo B: Time Manager (`tabs/Gis_Time_controller.py`)

- **IT**: (1) Rimosso `QThread.sleep(2)` — sostituito con `canvas.renderComplete` signal + `QEventLoop` con timeout 10s. (2) Debounce dial/spinbox con `QTimer.singleShot(300ms)` + cache sito/area. (3) Lazy matrix rebuild solo al cambio stato checkbox. (4) Pre-scan SQL ottimizzato: singola query `SELECT COUNT(DISTINCT order_layer)` invece di triplo ciclo annidato.
- **EN**: (1) Removed `QThread.sleep(2)` — replaced with `canvas.renderComplete` signal + `QEventLoop` with 10s timeout. (2) Debounce dial/spinbox with `QTimer.singleShot(300ms)` + cached sito/area. (3) Lazy matrix rebuild only on checkbox state change. (4) Optimized pre-scan SQL: single `SELECT COUNT(DISTINCT order_layer)` query instead of triple nested loop.

#### Gruppo C: DB Manager (`modules/db/pyarchinit_db_manager.py`)

- **IT**: (1) Rimosso `engine.dispose()` dopo ogni insert in `insert_data_session()`. (2) Riuso `self.Session()` in `update()` invece di creare nuovo `sessionmaker` per chiamata.
- **EN**: (1) Removed `engine.dispose()` after every insert in `insert_data_session()`. (2) Reuse `self.Session()` in `update()` instead of creating new `sessionmaker` per call.

#### Gruppo D: Database Sync (`modules/db/database_sync.py`)

- **IT**: (1) Connessione SQLite persistente in `SQLiteAdapter` con validazione `SELECT 1`. (2) Import batch con `executemany()` + fallback row-by-row. (3) Supporto SQLAlchemy engine per `PostgreSQLAdapter` — elimina ~188 subprocess `psql` per sessione.
- **EN**: (1) Persistent SQLite connection in `SQLiteAdapter` with `SELECT 1` validation. (2) Batch import with `executemany()` + row-by-row fallback. (3) SQLAlchemy engine support for `PostgreSQLAdapter` — eliminates ~188 `psql` subprocess spawns per session.

#### Gruppo E: DB Index

- **IT**: Aggiunto indice `idx_us_order_layer` su `us_table.order_layer` in structures e structures_metadata.
- **EN**: Added `idx_us_order_layer` index on `us_table.order_layer` in structures and structures_metadata.

#### File modificati / Modified files
- `modules/gis/pyarchinit_pyqgis.py` (eval→ast.literal_eval, DFS iterativo, batch SQL update)
- `tabs/Gis_Time_controller.py` (renderComplete signal, debounce, lazy matrix, SQL pre-scan)
- `modules/db/pyarchinit_db_manager.py` (rimosso engine.dispose, riuso self.Session)
- `modules/db/database_sync.py` (connessione persistente, executemany, SQLAlchemy engine)
- `modules/db/structures/US_table.py` (indice order_layer)
- `modules/db/structures_metadata/US_table.py` (indice order_layer)

---

## [5.3.13-alpha] - 2026-02-16

### refactor(cleanup): Rimossi eseguibili obsoleti e codice morto associato / Removed obsolete bundled executables and associated dead code

- **IT**: Rimossi 4 eseguibili obsoleti dalla directory `resources/dbfiles/`: `sqldiff.exe`, `sqldiff_linux`, `sqldiff_osx` e `spatialite_convert.exe`. Questi file non erano piu utilizzati dal plugin e appesantivano inutilmente il pacchetto. Rimosso il metodo `compare()` da `gui/pyarchinitConfigDialog.py`, che eseguiva `os.system("start cmd /k...")` per lanciare `sqldiff` solo su Windows — un pattern insicuro (shell injection) e non portabile. Rimosso il metodo `on_pushButton_convertdb_pressed()` dallo stesso file, anch'esso esclusivamente Windows-only e legato a `spatialite_convert.exe`. Rimosso il pannello UI `mDockWidget` dal file `gui/ui/pyarchinitConfigDialog.ui` che ospitava i pulsanti per queste funzionalita. Rimosse le voci di copia file per i 4 eseguibili da `modules/utility/pyarchinit_folder_installation.py`, che li copiava nella directory utente durante l'installazione delle cartelle del plugin. Il risultato e un plugin piu leggero, senza codice specifico Windows/insicuro e senza binari inutilizzati.
- **EN**: Removed 4 obsolete executables from the `resources/dbfiles/` directory: `sqldiff.exe`, `sqldiff_linux`, `sqldiff_osx`, and `spatialite_convert.exe`. These files were no longer used by the plugin and unnecessarily bloated the package. Removed the `compare()` method from `gui/pyarchinitConfigDialog.py`, which ran `os.system("start cmd /k...")` to launch `sqldiff` on Windows only — an insecure pattern (shell injection risk) and non-portable. Removed the `on_pushButton_convertdb_pressed()` method from the same file, also Windows-only and tied to `spatialite_convert.exe`. Removed the `mDockWidget` UI panel from `gui/ui/pyarchinitConfigDialog.ui` that hosted the buttons for these features. Removed the file-copy entries for the 4 executables from `modules/utility/pyarchinit_folder_installation.py`, which copied them into the user directory during plugin folder installation. The result is a lighter plugin, free of Windows-specific/insecure code paths and unused binaries.

#### File eliminati / Deleted files
- `resources/dbfiles/sqldiff.exe`
- `resources/dbfiles/sqldiff_linux`
- `resources/dbfiles/sqldiff_osx`
- `resources/dbfiles/spatialite_convert.exe`

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (rimossi metodi `compare()` e `on_pushButton_convertdb_pressed()` / removed `compare()` and `on_pushButton_convertdb_pressed()` methods)
- `gui/ui/pyarchinitConfigDialog.ui` (rimosso pannello `mDockWidget` / removed `mDockWidget` panel)
- `modules/utility/pyarchinit_folder_installation.py` (rimosse voci copia eseguibili / removed executable copy entries)

---

## [5.3.12-alpha] - 2026-02-16

### fix(perf): Risolto CPU 100% su Windows al caricamento del plugin / Fixed Windows CPU 100% at plugin load

- **IT**: Risolto un problema critico di prestazioni che causava il blocco della CPU al 100% su macchine Windows durante il caricamento del plugin, in particolare quando PostgreSQL o Graphviz non erano installati. Tre interventi principali: (1) **Timeout sui subprocess**: aggiunto `timeout=5` alle chiamate `subprocess.run()` per i controlli di versione `pg_dump -V` e `dot -V` in `__init__.py` e `modules/utility/pyarchinit_OS_utility.py`. In precedenza veniva usato `subprocess.call()` senza timeout, che poteva bloccarsi indefinitamente su Windows in assenza dei programmi esterni. (2) **Import lazy dei tab**: spostati oltre 30 import di moduli tab/dialog dal livello di modulo all'interno dei rispettivi metodi `run*()` (click handler) sia in `pyarchinitPlugin.py` che in `pyarchinitDockWidget.py`. Questo differisce il caricamento delle dipendenze pesanti (cv2, matplotlib, pandas, numpy, ecc.) dall'avvio del plugin al momento in cui l'utente apre effettivamente ciascun tab. (3) **Cache dei percorsi**: aggiunta variabile cache `_cached_windows_python_path` in `PackageManager.get_windows_qgis_python()` in `__init__.py` per evitare scansioni ripetute del filesystem in `C:\Program Files` durante l'installazione dei pacchetti.
- **EN**: Fixed a critical performance issue causing 100% CPU lock on Windows machines during plugin loading, particularly when PostgreSQL or Graphviz were not installed. Three main interventions: (1) **Subprocess timeout**: added `timeout=5` to `subprocess.run()` calls for `pg_dump -V` and `dot -V` version checks in `__init__.py` and `modules/utility/pyarchinit_OS_utility.py`. Previously bare `subprocess.call()` was used without timeout, which could hang indefinitely on Windows when the external programs were missing. (2) **Lazy tab imports**: moved 30+ tab/dialog module imports from module-level to inside their respective `run*()` click handler methods in both `pyarchinitPlugin.py` and `pyarchinitDockWidget.py`. This defers loading heavy dependencies (cv2, matplotlib, pandas, numpy, etc.) from plugin startup to when the user actually opens each tab. (3) **Path caching**: added `_cached_windows_python_path` cache variable to `PackageManager.get_windows_qgis_python()` in `__init__.py` to avoid repeated filesystem scans of `C:\Program Files` during package installation.

#### File modificati / Modified files
- `__init__.py` (timeout subprocess, cache percorsi / subprocess timeout, path caching)
- `pyarchinitPlugin.py` (import lazy dei tab / lazy tab imports)
- `pyarchinitDockWidget.py` (import lazy dei tab / lazy tab imports)
- `modules/utility/pyarchinit_OS_utility.py` (timeout subprocess / subprocess timeout)

---

## [5.3.11-alpha] - 2026-02-16

### fix(docs): Corretto tutorial MoveCost greco (el/34_movecost.md) da traslitterazione latina a caratteri greci / Fixed Greek MoveCost tutorial (el/34_movecost.md) from Latin transliteration to Greek characters

- **IT**: Riscritto completamente il file `docs/tutorials/el/34_movecost.md` convertendo tutto il testo dalla traslitterazione latina (Greeklish, es. "Eisagwgi", "Periechomena", "Algorithmoi") ai caratteri greci propri (es. "Εισαγωγη", "Περιεχομενα", "Αλγοριθμοι"). Lo stile adottato e il greco monotonico senza accenti, coerente con il tutorial GeoArchaeo greco (`el/33_geoarchaeo.md`). I termini tecnici (MoveCost, QGIS, R, DTM, CSV, HTML, PDF, Processing, ecc.) sono stati mantenuti in caratteri latini. La struttura e il contenuto del documento sono rimasti invariati (574 righe, 11 sezioni).
- **EN**: Completely rewrote the file `docs/tutorials/el/34_movecost.md` converting all text from Latin transliteration (Greeklish, e.g. "Eisagwgi", "Periechomena", "Algorithmoi") to proper Greek characters (e.g. "Εισαγωγη", "Περιεχομενα", "Αλγοριθμοι"). The style used is monotonic Greek without accents, consistent with the Greek GeoArchaeo tutorial (`el/33_geoarchaeo.md`). Technical terms (MoveCost, QGIS, R, DTM, CSV, HTML, PDF, Processing, etc.) were kept in Latin characters. The document structure and content remain unchanged (574 lines, 11 sections).

#### File modificati / Modified files
- `docs/tutorials/el/34_movecost.md`

---

## [5.3.10-alpha] - 2026-02-16

### docs(tutorials): Creato tutorial GeoArchaeo (33_geoarchaeo.md) in 10 lingue / Created GeoArchaeo tutorial (33_geoarchaeo.md) in 10 languages

- **IT**: Creato il file tutorial `33_geoarchaeo.md` in tutte le 10 directory linguistiche (it, en, de, fr, es, ar, ca, ro, pt, el) per lo strumento di analisi geostatistica GeoArchaeo. Ogni file contiene circa 463-466 righe di markdown con: indice, introduzione (cos'e GeoArchaeo, perche l'analisi geostatistica in archeologia), accesso allo strumento (Analysis Tools toolbar), interfaccia utente (6 schede), scheda Dati (caricamento layer, selezione campi, dati di esempio, esplorazione), scheda Variogramma (calcolo variogramma sperimentale, modellazione con 4 tipi di modello, variogrammi direzionali, parametri nugget/sill/range), scheda Kriging (kriging ordinario e universale, parametri griglia, risultati predizione e varianza), scheda Machine Learning (Random Forest, Gradient Boosting, SVR, validazione crociata, importanza variabili), scheda Campionamento (4 strategie: casuale semplice, stratificato, griglia regolare, ottimizzato), scheda Report (generazione automatica, formati PDF/HTML/Markdown), flusso di lavoro operativo in 6 passi, risoluzione problemi (tabella con 6 problemi comuni e soluzioni), note tecniche (dipendenze, CRS, esportazione, integrazione QGIS). Ogni versione linguistica e una traduzione propria, non una copia.
- **EN**: Created the tutorial file `33_geoarchaeo.md` in all 10 language directories (it, en, de, fr, es, ar, ca, ro, pt, el) for the GeoArchaeo geostatistical analysis tool. Each file contains approximately 463-466 lines of markdown with: table of contents, introduction (what is GeoArchaeo, why geostatistical analysis in archaeology), accessing the tool (Analysis Tools toolbar), user interface (6 tabs), Data tab (loading layers, field selection, example data, exploration), Variogram tab (experimental variogram computation, modelling with 4 model types, directional variograms, nugget/sill/range parameters), Kriging tab (ordinary and universal kriging, grid parameters, prediction and variance results), Machine Learning tab (Random Forest, Gradient Boosting, SVR, cross-validation, variable importance), Sampling tab (4 strategies: simple random, stratified, regular grid, optimised), Report tab (automatic generation, PDF/HTML/Markdown formats), 6-step operational workflow, troubleshooting (table with 6 common issues and solutions), technical notes (dependencies, CRS, export, QGIS integration). Each language version is a proper translation, not a copy.

#### File creati / Created files
- `docs/tutorials/it/33_geoarchaeo.md`
- `docs/tutorials/en/33_geoarchaeo.md`
- `docs/tutorials/de/33_geoarchaeo.md`
- `docs/tutorials/fr/33_geoarchaeo.md`
- `docs/tutorials/es/33_geoarchaeo.md`
- `docs/tutorials/ar/33_geoarchaeo.md`
- `docs/tutorials/ca/33_geoarchaeo.md`
- `docs/tutorials/ro/33_geoarchaeo.md`
- `docs/tutorials/pt/33_geoarchaeo.md`
- `docs/tutorials/el/33_geoarchaeo.md`

---

## [5.3.9-alpha] - 2026-02-16

### docs(tutorials): Creato tutorial MoveCost (34_movecost.md) in 10 lingue / Created MoveCost tutorial (34_movecost.md) in 10 languages

- **IT**: Creato il file tutorial `34_movecost.md` in tutte le 10 directory linguistiche (it, en, de, fr, es, ar, ca, ro, pt, el) per lo strumento autonomo MoveCost di analisi percorsi di minor costo. Ogni file contiene circa 450-550 righe di markdown con: indice, introduzione (storia dell'estrazione dalla scheda Sito), accesso allo strumento (Analysis Tools toolbar), prerequisiti (R, pacchetto movecost, Processing R Provider), interfaccia utente (4 schede), scheda Algoritmi (14 algoritmi in 3 gruppi: Superficie di Costo e Percorsi, Analisi Corridoi e Reti, Confronto e Classificazione), scheda Risultati (riepilogo costi e visualizzatore grafici R), scheda Esportazione (CSV, PDF stub, HTML), scheda Impostazioni (script R, lingua, organizzazione layer, help), flusso di lavoro operativo passo-passo, risoluzione problemi (R non trovato, script mancanti, grafici non visibili, pacchetto non installato, analisi lenta, errore CRS), note tecniche (architettura, file sorgente, funzioni di costo supportate, riferimenti bibliografici, compatibilita).
- **EN**: Created the tutorial file `34_movecost.md` in all 10 language directories (it, en, de, fr, es, ar, ca, ro, pt, el) for the standalone MoveCost least-cost path analysis tool. Each file contains approximately 450-550 lines of markdown with: table of contents, introduction (history of extraction from Site form), accessing the tool (Analysis Tools toolbar), prerequisites (R, movecost package, Processing R Provider), user interface (4 tabs), Algorithms tab (14 algorithms in 3 groups: Cost Surface & Paths, Corridor & Network Analysis, Comparison & Ranking), Results tab (cost summary and R plot viewer), Export tab (CSV, PDF stub, HTML), Settings tab (R scripts, language, layer organization, help), step-by-step operational workflow, troubleshooting (R not found, scripts missing, plots not showing, package not installed, slow analysis, CRS error), technical notes (architecture, source files, supported cost functions, bibliographic references, compatibility).

#### File creati / Created files
- `docs/tutorials/it/34_movecost.md`
- `docs/tutorials/en/34_movecost.md`
- `docs/tutorials/de/34_movecost.md`
- `docs/tutorials/fr/34_movecost.md`
- `docs/tutorials/es/34_movecost.md`
- `docs/tutorials/ar/34_movecost.md`
- `docs/tutorials/ca/34_movecost.md`
- `docs/tutorials/ro/34_movecost.md`
- `docs/tutorials/pt/34_movecost.md`
- `docs/tutorials/el/34_movecost.md`

### docs(tutorials): Aggiornamento tutorial Scheda Sito (02_*) in 10 lingue: rimossa sezione MoveCost, aggiunta nota strumenti di analisi standalone / Update Site Form tutorial (02_*) in 10 languages: removed MoveCost section, added standalone analysis tools note

- **IT**: Aggiornati i tutorial della Scheda Sito (02_*) in tutte le 10 directory linguistiche (it, en, de, fr, es, ar, ca, ro, pt, el). Modifiche: (1) Rimossa voce MoveCost dall'indice e sostituita con "Strumenti di Analisi"; (2) Aggiornata tabella interfaccia utente, riga 5 da "MoveCost" a "Strumenti di Analisi"; (3) Rimossa intera sezione MoveCost (prerequisiti, funzioni R, screenshot) e sostituita con una breve nota sugli strumenti di analisi standalone accessibili dalla toolbar (MoveCost, GeoArchaeo, SAM Segmentation, Pottery Tools, TOPS, Image Search) con link ai tutorial dedicati; (4) Sostituita voce troubleshooting "MoveCost non funziona" con riferimento generico ai tutorial dedicati; (5) Aggiornato elenco video nella versione IT.
- **EN**: Updated the Site Form tutorials (02_*) in all 10 language directories (it, en, de, fr, es, ar, ca, ro, pt, el). Changes: (1) Removed MoveCost entry from table of contents and replaced with "Analysis Tools"; (2) Updated user interface table, row 5 from "MoveCost" to "Analysis Tools"; (3) Removed entire MoveCost section (prerequisites, R functions, screenshots) and replaced with a short note about standalone analysis tools accessible from the toolbar (MoveCost, GeoArchaeo, SAM Segmentation, Pottery Tools, TOPS, Image Search) with links to dedicated tutorials; (4) Replaced troubleshooting entry "MoveCost not working" with a generic reference to dedicated tutorials; (5) Updated video list in IT version.

#### File modificati / Modified files
- `docs/tutorials/it/02_scheda_sito.md`
- `docs/tutorials/en/02_scheda_sito.md`
- `docs/tutorials/de/02_fundort_formular.md`
- `docs/tutorials/fr/02_fiche_site.md`
- `docs/tutorials/es/02_ficha_sitio.md`
- `docs/tutorials/ar/02_بطاقة_الموقع.md`
- `docs/tutorials/ca/02_fitxa_lloc.md`
- `docs/tutorials/ro/02_scheda_sito.md`
- `docs/tutorials/pt/02_scheda_sito.md`
- `docs/tutorials/el/02_scheda_sito.md`

### refactor(movecost): Estrazione MoveCost dalla scheda Sito in strumento di analisi standalone / Extract MoveCost from Site form into standalone analysis tool

- **IT**: Estratto MoveCost dalla scheda Sito (`tabs/Site.py`, `gui/ui/Site.ui`) in uno strumento di analisi standalone. Creato nuovo dialogo `tabs/Movecost.py` (classe `pyarchinit_Movecost`) con tutte le funzionalità movecost: 14 algoritmi R (movecost, movebound, movecorr, movealloc, movecomp, movenetw, moverank con varianti polygon), organizzazione layer, riepilogo risultati, visualizzazione plot R, esportazione CSV/PDF/HTML, impostazioni (script R, lingua, help). Creato file UI `gui/ui/Movecost.ui` con 4 tab (Algoritmi, Risultati, Esportazione, Impostazioni). Rimosso `QgsDockWidget mDockWidget`, `pushButton_mc` e connessione signal/slot da `Site.ui`. Rimossi tutti i metodi movecost e import inutilizzati da `Site.py`. Aggiunto `actionMovecost` al `analysisToolButton` in tutte le 4 sezioni locali (IT/EN/DE/else) di `pyarchinitPlugin.py`. Aggiunto metodo `runMovecost` al plugin.
- **EN**: Extracted MoveCost from the Site form (`tabs/Site.py`, `gui/ui/Site.ui`) into a standalone analysis tool. Created new dialog `tabs/Movecost.py` (class `pyarchinit_Movecost`) containing all movecost functionality: 14 R algorithms (movecost, movebound, movecorr, movealloc, movecomp, movenetw, moverank with polygon variants), layer organization, results summary, R plot viewer, CSV/PDF/HTML export, settings (R scripts, language, help). Created UI file `gui/ui/Movecost.ui` with 4 tabs (Algorithms, Results, Export, Settings). Removed `QgsDockWidget mDockWidget`, `pushButton_mc` and signal/slot connection from `Site.ui`. Removed all movecost methods and unused imports from `Site.py`. Added `actionMovecost` to `analysisToolButton` in all 4 locale sections (IT/EN/DE/else) of `pyarchinitPlugin.py`. Added `runMovecost` method to the plugin.

#### File creati / Created files
- `tabs/Movecost.py` (nuovo / new)
- `gui/ui/Movecost.ui` (nuovo / new)

#### File modificati / Modified files
- `tabs/Site.py` (rimossi metodi e import movecost / removed movecost methods and imports)
- `gui/ui/Site.ui` (rimosso mDockWidget, pushButton_mc e connessione / removed mDockWidget, pushButton_mc and connection)
- `pyarchinitPlugin.py` (aggiunto actionMovecost e runMovecost / added actionMovecost and runMovecost)

### feat(ui): Creato file UI standalone per MoveCost Analysis / Created standalone MoveCost Analysis UI file

- **IT**: Creato nuovo file Qt Designer `gui/ui/Movecost.ui` con classe `MovecostDialog` (QDialog, 420x700). Il dialogo contiene un QTabWidget con 4 tab: (1) Algorithms -- pulsanti per movecost, movebound, movecorr, movealloc, movenetw, movecomp, moverank con varianti "by polygon", raggruppati in 3 QGroupBox (Cost Surface & Paths, Corridor & Network Analysis, Comparison & Ranking); (2) Results -- QTextEdit per il riepilogo costi e QLabel per visualizzazione plot R con pulsanti Refresh/Save; (3) Export -- pulsanti per esportazione CSV, PDF e HTML; (4) Settings -- installazione script R, selezione lingua, organizzazione layer automatica, help. Applicato stylesheet completo con bordi arrotondati, colori tematici per ogni pulsante e stile coerente per tab, gruppi, combo e text edit.
- **EN**: Created new Qt Designer file `gui/ui/Movecost.ui` with class `MovecostDialog` (QDialog, 420x700). The dialog contains a QTabWidget with 4 tabs: (1) Algorithms -- buttons for movecost, movebound, movecorr, movealloc, movenetw, movecomp, moverank with "by polygon" variants, grouped in 3 QGroupBoxes (Cost Surface & Paths, Corridor & Network Analysis, Comparison & Ranking); (2) Results -- QTextEdit for cost summary and QLabel for R plot display with Refresh/Save buttons; (3) Export -- buttons for CSV, PDF and HTML export; (4) Settings -- R script installation, language selection, automatic layer organization, help. Applied comprehensive stylesheet with rounded borders, themed colors per button, and consistent styling for tabs, groups, combos, and text edits.

#### File creati / Created files
- `gui/ui/Movecost.ui` (nuovo / new)

### refactor(toolbar): Raggruppamento strumenti di analisi nelle sezioni EN ed else della toolbar / Group analysis tools in EN and else toolbar sections

- **IT**: Aggiornate le sezioni `elif l == 'en'` ed `else` in `pyarchinitPlugin.py` per allinearle alla sezione italiana (`l == 'it'`) gia' modificata. Modifiche: (1) rimosso `self.toolBar.addAction(self.actionSamSegmentation)` -- SAM ora raggruppato nell'analysisToolButton; (2) rimosso `self.actionPotteryTools` dal `dataToolButton`; (3) sostituito il vecchio pulsante standalone TOPS con un nuovo `analysisToolButton` che contiene: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo; (4) rimossa la vecchia definizione di `ImageSearch` dalla sezione documentazione (ora creata nell'area analysis tools); (5) rimosso `ImageSearch` dal `docToolButton`; (6) aggiunti `actionImageSearch` e `actionGeoArchaeo` al menu plugin; (7) aggiornato il QMenu per raggruppare gli strumenti di analisi e rimuovere PotteryTools dalla riga data entry.
- **EN**: Updated the `elif l == 'en'` and `else` sections in `pyarchinitPlugin.py` to match the already-modified Italian (`l == 'it'`) section. Changes: (1) removed `self.toolBar.addAction(self.actionSamSegmentation)` -- SAM now grouped in analysisToolButton; (2) removed `self.actionPotteryTools` from `dataToolButton`; (3) replaced the old standalone TOPS button with a new `analysisToolButton` containing: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo; (4) removed old `ImageSearch` definition from the documentation section (now created in the analysis tools area); (5) removed `ImageSearch` from `docToolButton`; (6) added `actionImageSearch` and `actionGeoArchaeo` to the plugin menu; (7) updated the QMenu to group analysis tools and remove PotteryTools from the data entry line.

#### File modificati / Modified files
- `pyarchinitPlugin.py` (aggiornate sezioni EN ed else / updated EN and else sections)

### fix(security): Aggiornamento dipendenze per vulnerabilita' Dependabot / Update dependencies for Dependabot vulnerabilities

- **IT**: Aggiornato `requirements.txt` per risolvere vulnerabilita' segnalate da Dependabot: `langchain` da 1.2.3 a 1.2.10 e `langchain-core` da 1.2.7 a 1.2.13. Le nuove versioni includono patch di sicurezza e fix di stabilita'.
- **EN**: Updated `requirements.txt` to resolve Dependabot-reported vulnerabilities: `langchain` from 1.2.3 to 1.2.10 and `langchain-core` from 1.2.7 to 1.2.13. The new versions include security patches and stability fixes.

#### File modificati / Modified files
- `requirements.txt` (aggiornato / updated)

### feat(ai): Aggiornamento modelli AI a GPT-4.1 e Claude 4.5 Sonnet / Update AI models to GPT-4.1 and Claude 4.5 Sonnet

- **IT**: Aggiornati tutti i riferimenti ai modelli AI nel codebase. Tutti i riferimenti a GPT-4o sostituiti con GPT-4.1 in 5 file: `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py`, `embedding_models.py`, `translate_ts_complete.py`, `textTosql.py`. Modello Claude aggiornato da `claude-3-5-sonnet` a `claude-sonnet-4-5-20250929`. Aggiunto Anthropic Claude 4.5 Sonnet come alternativa nel modulo txt2sql (`textTosql.py`) per query SQL in linguaggio naturale.
- **EN**: Updated all AI model references across the codebase. All GPT-4o references replaced with GPT-4.1 in 5 files: `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py`, `embedding_models.py`, `translate_ts_complete.py`, `textTosql.py`. Claude model updated from `claude-3-5-sonnet` to `claude-sonnet-4-5-20250929`. Added Anthropic Claude 4.5 Sonnet as alternative in the txt2sql module (`textTosql.py`) for natural language SQL queries.

#### File modificati / Modified files
- `modules/ai/skatch_gpt_US.py` (aggiornato / updated)
- `modules/ai/skatch_gpt_INVMAT.py` (aggiornato / updated)
- `modules/ai/embedding_models.py` (aggiornato / updated)
- `scripts/translate_ts_complete.py` (aggiornato / updated)
- `modules/ai/textTosql.py` (aggiornato / updated)

### feat(geoarchaeo): Integrazione plugin GeoArchaeo per analisi geostatistica / GeoArchaeo geostatistical analysis plugin integration

- **IT**: Integrato il plugin GeoArchaeo per analisi geostatistica come modulo interno in `modules/geoarchaeo/`. Aggiunto alla toolbar in tutte le sezioni locali (IT/EN/DE/else) all'interno del nuovo `analysisToolButton`. Implementato metodo `runGeoArchaeo` in `pyarchinitPlugin.py` che avvia il pannello dock widget per l'analisi geostatistica. Il plugin fornisce strumenti per analisi spaziale, interpolazione e statistica dei dati archeologici direttamente dall'interfaccia PyArchInit.
- **EN**: Integrated the GeoArchaeo geostatistical analysis plugin as an internal module at `modules/geoarchaeo/`. Added to the toolbar in all locale sections (IT/EN/DE/else) within the new `analysisToolButton`. Implemented `runGeoArchaeo` method in `pyarchinitPlugin.py` that launches the dock widget panel for geostatistical analysis. The plugin provides tools for spatial analysis, interpolation and statistics on archaeological data directly from the PyArchInit interface.

#### File modificati / Modified files
- `modules/geoarchaeo/` (nuovo modulo / new module)
- `pyarchinitPlugin.py` (aggiornato / updated)

### refactor(tops): Riscrittura completa del modulo TOPS con API Python diretta / Complete rewrite of TOPS module with direct Python API

- **IT**: Riscrittura completa di `tabs/tops_pyarchinit.py`: rimosso il vecchio approccio basato su subprocess a favore dell'API Python diretta. Aggiunto auto-rilevamento dei formati di input disponibili. Ora supporta 17 formati di input (CSV, DXF, GeoJSON, GML, GPX, JSON, KML, KMZ, MapInfo, ODS, OpenFileGDB, Parquet, SHP, SQLite, XLSX, GeoPackage, TopoJSON) e 11 formati di output (CSV, DXF, GeoJSON, GML, GPX, KML, MapInfo, SHP, SQLite, GeoPackage, XLSX). Aggiornata l'interfaccia utente `gui/ui/Tops2pyarchinit.ui` con le nuove liste di formati.
- **EN**: Complete rewrite of `tabs/tops_pyarchinit.py`: removed the old subprocess-based approach in favor of direct Python API. Added auto-detection of available input formats. Now supports 17 input formats (CSV, DXF, GeoJSON, GML, GPX, JSON, KML, KMZ, MapInfo, ODS, OpenFileGDB, Parquet, SHP, SQLite, XLSX, GeoPackage, TopoJSON) and 11 output formats (CSV, DXF, GeoJSON, GML, GPX, KML, MapInfo, SHP, SQLite, GeoPackage, XLSX). Updated the UI `gui/ui/Tops2pyarchinit.ui` with the new format lists.

#### File modificati / Modified files
- `tabs/tops_pyarchinit.py` (riscritto / rewritten)
- `gui/ui/Tops2pyarchinit.ui` (aggiornato / updated)

### fix(toolbar): Correzione sezione DE della toolbar per allineamento con IT/EN/else / Fix DE toolbar section to match IT/EN/else

- **IT**: Corretta la sezione tedesca (`elif l == 'de'`) della toolbar in `pyarchinitPlugin.py` per allinearla alle sezioni IT/EN/else gia' aggiornate. Rimosso il pulsante standalone `self.toolBar.addAction(self.actionSamSegmentation)`. Sostituito il vecchio `manageToolButton` standalone per TOPS con il nuovo `analysisToolButton` che raggruppa: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo. Ora tutte e 4 le sezioni della toolbar (IT/EN/DE/else) hanno la stessa struttura.
- **EN**: Fixed the German (`elif l == 'de'`) toolbar section in `pyarchinitPlugin.py` to match the already-updated IT/EN/else sections. Removed the standalone `self.toolBar.addAction(self.actionSamSegmentation)` button. Replaced the old standalone TOPS `manageToolButton` with the new `analysisToolButton` grouping: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo. All 4 toolbar sections (IT/EN/DE/else) now have the same structure.

#### File modificati / Modified files
- `pyarchinitPlugin.py` (aggiornata sezione DE / updated DE section)

---

## [5.3.8-alpha] - 2026-02-16

### feat(movecost): Integrazione MoveCost completa nella Scheda Sito con interfaccia a 4 tab / Complete MoveCost integration in Site tab with 4-tab interface

- **IT**: Completamente ristrutturata l'integrazione MoveCost nella Scheda Sito (`Site.ui` + `Site.py`). **UI** (`gui/ui/Site.ui`): Rimosso il vecchio dock widget a posizionamento assoluto con 8 pulsanti (371x221px), sostituito con un'interfaccia moderna a 4 schede (420x700px): (1) Tab "Algorithms" con 14 pulsanti organizzati in 3 gruppi (Cost Surface & Paths: movecost, movecost_focalcost, movecost_focalslope, movealloc, movecorr; Corridor & Network Analysis: movecorr, movenetw; Comparison & Ranking: movecomp, moverank) per 7 algoritmi base + 7 varianti poligonali -- aggiunge i nuovi algoritmi movecomp, movenetw, moverank; (2) Tab "Results" con riepilogo costi (statistiche) e visualizzatore R Plot con funzioni refresh/salva; (3) Tab "Export" con opzioni esportazione CSV, HTML e PDF per i dati di analisi dei costi; (4) Tab "Settings" con installatore R Scripts, selettore lingua (5 lingue), controlli organizzazione layer e documentazione help. **Backend** (`tabs/Site.py`): Sostituiti i metodi handler semplici con implementazione completa: wrapper `_mc_run_algorithm()` con auto-organizzazione layer e aggiornamento automatico tab risultati; 14 handler di algoritmo (7 base + 7 poligonali) invece di 8; tab risultati con riepilogo costi e statistiche + auto-rilevamento R plot; esportazione CSV e generazione report HTML; integrazione organizzatore layer (dal plugin movecost); sistema tooltip multilingua (carica dai file JSON i18n del plugin movecost); documentazione help (apre le pagine help del plugin movecost); installatore R script aggiornato: ora copia dalla directory `rscripts/` del plugin movecost (28 script) con fallback agli script propri di pyarchinit.
- **EN**: Completely restructured the MoveCost integration in the Site tab (`Site.ui` + `Site.py`). **UI** (`gui/ui/Site.ui`): Removed the old absolute-positioned dock widget with 8 buttons (371x221px), replaced with a modern 4-tab interface (420x700px): (1) "Algorithms" tab with 14 buttons organized in 3 groups (Cost Surface & Paths: movecost, movecost_focalcost, movecost_focalslope, movealloc, movecorr; Corridor & Network Analysis: movecorr, movenetw; Comparison & Ranking: movecomp, moverank) for 7 base + 7 polygon variants -- adds new movecomp, movenetw, moverank algorithms; (2) "Results" tab with cost summary display (statistics) and R Plot Viewer with refresh/save capabilities; (3) "Export" tab with CSV, HTML and PDF export options for cost analysis data; (4) "Settings" tab with R Scripts installer, language selector (5 languages), layer organization controls and help documentation. **Backend** (`tabs/Site.py`): Replaced simple handler methods with full-featured implementation: `_mc_run_algorithm()` wrapper with auto-organize layers and results tab auto-update; 14 algorithm handlers (7 base + 7 polygon variants) instead of 8; results tab with cost summary and statistics + R plot auto-detection; CSV export and HTML report generation; layer organizer integration (from movecost plugin); multi-language tooltips system (loads from movecost plugin's i18n JSON files); help documentation (opens movecost plugin's help pages); updated R script installer: now copies from movecost plugin's `rscripts/` directory (28 scripts) with fallback to pyarchinit's own scripts.

#### File modificati / Modified files
- `gui/ui/Site.ui` (ristrutturato / restructured)
- `tabs/Site.py` (aggiornato / updated)

---

## [5.3.7-alpha] - 2026-02-16

### fix(i18n): Compilazione .qm mancanti e completamento traduzioni italiane / Compile missing .qm files and complete Italian translations

- **IT**: Compilati i 3 file `.qm` mancanti per rumeno (`ro_RO`), portoghese (`pt_PT`) e greco (`el_GR`) — prima gli utenti di queste lingue vedevano il testo italiano di fallback per tutte le etichette dei form .ui. Completato il file di traduzione italiano (`it_IT.ts`): 2.252 voci vuote riempite (271 tradotte dall'inglese, 1.981 copiate dal sorgente italiano). Ricompilato `it_IT.qm` con 2.826 traduzioni finite. Ora tutti i 10 file `.qm` sono presenti e completi.
- **EN**: Compiled the 3 missing `.qm` files for Romanian (`ro_RO`), Portuguese (`pt_PT`) and Greek (`el_GR`) — previously users of these languages saw Italian fallback text for all .ui form labels. Completed the Italian translation file (`it_IT.ts`): 2,252 empty entries filled (271 translated from English, 1,981 copied from Italian source text). Recompiled `it_IT.qm` with 2,826 finished translations. All 10 `.qm` files now present and complete.

#### File modificati / Modified files
- `i18n/pyarchinit_plugin_it_IT.ts` (completato / completed)
- `i18n/pyarchinit_plugin_it_IT.qm` (ricompilato / recompiled)
- `i18n/pyarchinit_plugin_ro_RO.qm` (nuovo / new)
- `i18n/pyarchinit_plugin_pt_PT.qm` (nuovo / new)
- `i18n/pyarchinit_plugin_el_GR.qm` (nuovo / new)

---

## [5.3.6-alpha] - 2026-02-16

### feat(i18n): Espansione completa CONVERSION_DICT e SORT_ITEMS a 10 lingue / Complete expansion of CONVERSION_DICT and SORT_ITEMS to 10 languages

- **IT**: Espansi `CONVERSION_DICT` e `SORT_ITEMS` da 3 lingue (it/de/en) a 10 lingue (it/de/en/es/fr/ar/ca/ro/pt/el) + fallback else in tutti i 14 file tab. File aggiornati: `Site.py` (8 campi), `Struttura.py` (13 campi), `Tomba.py` (33 campi), `Schedaind.py` (12 campi), `Campioni.py` (4 campi + SORT_ITEMS), `Thesaurus.py` (6 campi), `Documentazione.py` (8 campi), `Tafonomia.py` (33 campi), `US_USM.py` (~85 campi + SORT_ITEMS), `Deteta.py` (~40 campi), `Inv_Lapidei.py` (20 campi), `Inv_Materiali.py` (29 campi + QUANT_ITEMS), `UT.py` (48 campi + SORT_ITEMS). Corretti bug: blocchi `if` separati in Inv_Materiali.py convertiti in catena `elif` corretta. Corretto blocco `else:` → `elif L=='en':` in Inv_Lapidei.py, UT.py, US_USM.py. Corretti refusi inglesi in Inv_Lapidei.py. Espanso `LAYERS_CONVERT_DIZ` in `pyarchinit_pyqgis.py` (33 layer) e aggiunto sistema centralizzato `_GROUP_NAMES` + `_gn()` per 21 nomi di gruppi GIS. Creati 3 file HTML codici thesaurus: `codici_el.html`, `codici_pt.html`, `codici_ro.html`. Totale: ~15.000 nuove righe.
- **EN**: Expanded `CONVERSION_DICT` and `SORT_ITEMS` from 3 languages (it/de/en) to 10 languages (it/de/en/es/fr/ar/ca/ro/pt/el) + else fallback across all 14 tab files. Files updated: `Site.py` (8 fields), `Struttura.py` (13 fields), `Tomba.py` (33 fields), `Schedaind.py` (12 fields), `Campioni.py` (4 fields + SORT_ITEMS), `Thesaurus.py` (6 fields), `Documentazione.py` (8 fields), `Tafonomia.py` (33 fields), `US_USM.py` (~85 fields + SORT_ITEMS), `Deteta.py` (~40 fields), `Inv_Lapidei.py` (20 fields), `Inv_Materiali.py` (29 fields + QUANT_ITEMS), `UT.py` (48 fields + SORT_ITEMS). Bug fixes: separate `if` blocks in Inv_Materiali.py converted to proper `elif` chain. Fixed `else:` → `elif L=='en':` in Inv_Lapidei.py, UT.py, US_USM.py. Fixed English typos in Inv_Lapidei.py. Expanded `LAYERS_CONVERT_DIZ` in `pyarchinit_pyqgis.py` (33 layers) and added centralized `_GROUP_NAMES` + `_gn()` system for 21 GIS group names. Created 3 thesaurus codes HTML files: `codici_el.html`, `codici_pt.html`, `codici_ro.html`. Total: ~15,000 new lines.

#### File modificati / Modified files
- `tabs/Site.py`, `tabs/Struttura.py`, `tabs/Tomba.py`, `tabs/Schedaind.py`
- `tabs/Campioni.py`, `tabs/Thesaurus.py`, `tabs/Documentazione.py`, `tabs/Tafonomia.py`
- `tabs/US_USM.py`, `tabs/Deteta.py`, `tabs/Inv_Lapidei.py`, `tabs/Inv_Materiali.py`, `tabs/UT.py`
- `modules/gis/pyarchinit_pyqgis.py`
- `tabs/codici_el.html`, `tabs/codici_pt.html`, `tabs/codici_ro.html`

---

## [5.3.5-alpha] - 2026-02-16

### feat(i18n): Thesaurus codes HTML per greco, portoghese e rumeno / Thesaurus codes HTML for Greek, Portuguese and Romanian

- **IT**: Creati 3 nuovi file HTML di codici thesaurus tradotti dalla versione inglese: `tabs/codici_el.html` (Greco moderno), `tabs/codici_pt.html` (Portoghese europeo), `tabs/codici_ro.html` (Rumeno). Ogni file contiene 12 sezioni tabellari (Sito, US/USM, Struttura, Sepoltura, Inventario Materiali, Campioni, Individui, Documentazione, TMA, Ceramica, UT, Fauna) con intestazioni di colonna, titoli di sezione, descrizioni dei campi e valori di esempio tradotti. Struttura HTML, CSS e nomi tecnici dei campi database mantenuti identici alla versione inglese. ~300 righe per file.
- **EN**: Created 3 new translated thesaurus codes HTML files from the English version: `tabs/codici_el.html` (Modern Greek), `tabs/codici_pt.html` (European Portuguese), `tabs/codici_ro.html` (Romanian). Each file contains 12 table sections (Site, SU/WSU, Structure, Burial, Finds Inventory, Samples, Individuals, Documentation, TMA, Pottery, UT, Fauna) with translated column headers, section titles, field descriptions and example values. HTML structure, CSS and technical database field names kept identical to the English version. ~300 lines per file.

#### File modificati / Modified files
- `tabs/codici_el.html` (nuovo / new)
- `tabs/codici_pt.html` (nuovo / new)
- `tabs/codici_ro.html` (nuovo / new)

---

## [5.3.4-alpha] - 2026-02-16

### feat(i18n): CONVERSION_DICT, QUANT_ITEMS e SORT_ITEMS multilingua in Inv_Materiali / Multilingual CONVERSION_DICT, QUANT_ITEMS and SORT_ITEMS in Inv_Materiali

- **IT**: Aggiunti blocchi `CONVERSION_DICT`, `QUANT_ITEMS` e `SORT_ITEMS` per 7 lingue aggiuntive (es, fr, ar, ca, ro, pt, el) nel file `tabs/Inv_Materiali.py`. Corretta la catena di `if` separati: le istruzioni `if L =='de':` e `if L =='en':` sono state convertite in `elif` per formare una catena corretta `if/elif/else`. Aggiunto blocco `else:` finale con fallback inglese. 29 campi tradotti per ogni lingua (sito, numero_inventario, tipo_reperto, criterio_schedatura, definizione, descrizione, area, us, lavato, nr_cassa, luogo_conservazione, stato_conservazione, datazione_reperto, forme_minime, forme_massime, totale_frammenti, corpo_ceramico, rivestimento, diametro_orlo, peso, tipo, eve_orlo, repertato, diagnostico, n_reperto, tipo_contenitore, struttura, years). QUANT_ITEMS include 9 voci tradotte per lingua. Totale: ~580 nuove righe.
- **EN**: Added `CONVERSION_DICT`, `QUANT_ITEMS` and `SORT_ITEMS` blocks for 7 additional languages (es, fr, ar, ca, ro, pt, el) in `tabs/Inv_Materiali.py`. Fixed separate `if` statements: `if L =='de':` and `if L =='en':` were converted to `elif` to form a proper `if/elif/else` chain. Added final `else:` block with English fallback. 29 fields translated per language (site, inventory_number, artefact_type, material_class, definition, description, area, stratigraphic_unit, washed, box, place_of_conservation, status_of_conservation, artefact_period, min_shape, max_shape, total_fragments, body_sherds, coating, rim_diameter, weight, type, eve_rim, reperted, diagnostic, ra, container_type, structure, years). QUANT_ITEMS includes 9 translated entries per language. Total: ~580 new lines.

#### File modificati / Modified files
- `tabs/Inv_Materiali.py` (aggiornato / updated)

---

## [5.3.3-alpha] - 2026-02-16

### feat(i18n): CONVERSION_DICT e SORT_ITEMS multilingua in Inv_Lapidei / Multilingual CONVERSION_DICT and SORT_ITEMS in Inv_Lapidei

- **IT**: Aggiunti blocchi `CONVERSION_DICT` e `SORT_ITEMS` per 7 lingue aggiuntive (es, fr, ar, ca, ro, pt, el) nel file `tabs/Inv_Lapidei.py`. Il blocco `else:` (fallback inglese) è stato convertito in `elif L=='en':` esplicito, seguito da 7 nuovi blocchi `elif` per ciascuna lingua e un blocco `else:` finale che usa l'inglese come default. 19 campi tradotti per ogni lingua (sito, scheda_numero, collocazione, oggetto, tipologia, materiale, d_letto_posa, d_letto_attesa, toro, spessore, larghezza, lunghezza, h, descrizione, lavorazione_e_stato_di_conservazione, confronti, cronologia, bibliografia, compilatore). Corretti refusi nelle etichette inglesi: "Thikness" -> "Thickness", "Weight" -> "Width", "Lenght" -> "Length", "presevation" -> "preservation", "Comparision" -> "Comparisons". Totale: ~370 nuove righe.
- **EN**: Added `CONVERSION_DICT` and `SORT_ITEMS` blocks for 7 additional languages (es, fr, ar, ca, ro, pt, el) in `tabs/Inv_Lapidei.py`. The `else:` block (English fallback) was converted to an explicit `elif L=='en':`, followed by 7 new `elif` blocks for each language and a final `else:` block defaulting to English. 19 fields translated per language (site, form_number, placement, object, typology, material, bed_pose, waiting_bed, toro, thickness, width, length, h, description, processing_and_preservation_state, comparisons, chronology, bibliography, author). Fixed English label typos: "Thikness" -> "Thickness", "Weight" -> "Width", "Lenght" -> "Length", "presevation" -> "preservation", "Comparision" -> "Comparisons". Total: ~370 new lines.

#### File modificati / Modified files
- `tabs/Inv_Lapidei.py` (aggiornato / updated)

---

## [5.3.2-alpha] - 2026-02-16

### feat(i18n): CONVERSION_DICT e SORT_ITEMS multilingua in Documentazione e Tafonomia / Multilingual CONVERSION_DICT and SORT_ITEMS in Documentazione and Tafonomia

- **IT**: Aggiunti blocchi `CONVERSION_DICT` e `SORT_ITEMS` per 7 lingue aggiuntive (es, fr, ar, ca, ro, pt, el) nei file `Documentazione.py` e `Tafonomia.py`. Il blocco `else:` (fallback inglese) è stato convertito in `elif L=='en':` esplicito, seguito da 7 nuovi blocchi `elif` per ciascuna lingua e un blocco `else:` finale che usa l'inglese come default. In `Documentazione.py`: 8 campi tradotti per ogni lingua (sito, nome_doc, data, tipo_documentazione, sorgente, scala, disegnatore, note). In `Tafonomia.py`: 33 campi tradotti per ogni lingua (sito, nr_scheda_taf, sigla_struttura, nr_struttura, nr_individuo, rito, descrizione, interpretazione, segnacoli, canale_libatorio, oggetti_rinvenuti, stato_conservazione, copertura, contenitore_resti, orientamento_asse/azimut, corredo, lunghezza/posizione_scheletro, cranio, arti_superiori/inferiori, completo, disturbato, connessione, caratteristiche, periodo/fase iniziale/finale, datazione_estesa). Totale: ~560 nuove righe in Documentazione.py, ~1050 nuove righe in Tafonomia.py.
- **EN**: Added `CONVERSION_DICT` and `SORT_ITEMS` blocks for 7 additional languages (es, fr, ar, ca, ro, pt, el) in `Documentazione.py` and `Tafonomia.py`. The `else:` block (English fallback) was converted to an explicit `elif L=='en':`, followed by 7 new `elif` blocks for each language and a final `else:` block defaulting to English. In `Documentazione.py`: 8 fields translated per language (site, doc_name, date, documentation_type, source, scale, draftsman, notes). In `Tafonomia.py`: 33 fields translated per language (site, taphonomy_sheet_nr, structure_acronym, structure_nr, individual_nr, rite, description, interpretation, markers, libation_channel, external_objects, conservation_state, covering_type, remains_container_type, axis/azimuth_orientation, grave_goods, skeleton_length/position, cranium/upper_limbs/lower_limbs position, complete, disturbed, in_connection, characteristics, initial/final period/phase, extended_dating). Total: ~560 new lines in Documentazione.py, ~1050 new lines in Tafonomia.py.

#### File modificati / Modified files
- `tabs/Documentazione.py` (aggiornato / updated)
- `tabs/Tafonomia.py` (aggiornato / updated)

---

## [5.3.1-alpha] - 2026-02-15

### feat(db): Estensione dati i18n: tabelle aggiuntive + layer GIS / Extend i18n example data: additional tables + GIS layers

- **IT**: Esteso lo script `scripts/populate_i18n_example_data.py` per popolare 6 tabelle aggiuntive in tutte le 10 lingue: `struttura_table` (10 record: edifici, focolare, muri, pavimenti, fossa, spoliazione), `tomba_table` (10 sepolture: inumazioni e cremazione, vari tipi), `individui_table` (10 individui con sesso, età, posizioni), `pottery_table` (10 ceramiche: maiolica, invetriata, grezza, ingobbiata), `inventario_materiali_table` (10 reperti: ceramica, metallo, vetro, osso, moneta, laterizio). Replicati i layer GIS per 9 lingue aggiuntive: `pyunitastratigrafiche` (482×10=4820 righe), `pyunitastratigrafiche_usm` (19×10=190 righe), `pyarchinit_quote` (70×10=700 righe) con traduzione dei tipi di materiale (tipo_us_s) e delle abbreviazioni unità tipo. Gestione trigger SpatiaLite per pyarchinit_quote. Aggiunti ~25 dizionari di traduzione per i nuovi campi. Totale: 500 record per le nuove tabelle (100 ciascuna × 5 tabelle), 5710 geometrie GIS.
- **EN**: Extended `scripts/populate_i18n_example_data.py` to populate 6 additional tables across all 10 languages: `struttura_table` (10 records: buildings, hearth, walls, floors, pit, robber trench), `tomba_table` (10 burials: inhumations and cremation, various types), `individui_table` (10 individuals with sex, age, positions), `pottery_table` (10 ceramics: majolica, glazed, coarse, slipped), `inventario_materiali_table` (10 finds: ceramic, metal, glass, bone, coin, brick). Replicated GIS layers for 9 additional languages: `pyunitastratigrafiche` (482×10=4820 rows), `pyunitastratigrafiche_usm` (19×10=190 rows), `pyarchinit_quote` (70×10=700 rows) with translation of material types (tipo_us_s) and unit type abbreviations. Handled SpatiaLite geometry triggers for pyarchinit_quote. Added ~25 translation dictionaries for new fields. Total: 500 records for new tables (100 each × 5 tables), 5710 GIS geometries.

#### File modificati / Modified files
- `scripts/populate_i18n_example_data.py` (aggiornato / updated)
- `resources/dbfiles/pyarchinit_db.sqlite` (aggiornato / updated)

---

## [5.3.0-alpha] - 2026-02-15

### feat(db): Dati di esempio i18n per 10 lingue nel template SQLite / i18n example data for 10 languages in template SQLite

- **IT**: Creato script `scripts/populate_i18n_example_data.py` che popola il database template `resources/dbfiles/pyarchinit_db.sqlite` con dati di esempio tradotti per tutte le 10 lingue supportate (IT, EN, DE, ES, FR, AR, CA, RO, PT, EL). Partendo dai 51 record US italiani esistenti ("Scavo archeologico"), vengono generati 9 siti aggiuntivi con nomi localizzati (es. "Archaeological Excavation", "Archäologische Ausgrabung", "Αρχαιολογική Ανασκαφή"). Per ogni sito: 51 record US con termini di relazione tradotti (rapporti/rapporti2), abbreviazioni unità tipo localizzate (US→SU/SE/UE/ΣΜ, USM→WSU/MSE/UEM/USZ/ΤΣΜ), campi testuali tradotti (d_stratigrafica, d_interpretativa, formazione, stato_di_conservazione, colore, consistenza, metodo_di_scavo, inclusi, documentazione) e testi lunghi (descrizione/interpretazione) con sostituzione terminologica. 12 record periodizzazione con descrizioni cronologiche tradotte. Totale: 510 US, 120 periodizzazioni, 11 siti. Lo script utilizza il modulo centrale `pyarchinit_i18n_stratigraphic` per i termini di relazione e le abbreviazioni.
- **EN**: Created script `scripts/populate_i18n_example_data.py` that populates the template database `resources/dbfiles/pyarchinit_db.sqlite` with translated example data for all 10 supported languages (IT, EN, DE, ES, FR, AR, CA, RO, PT, EL). Starting from the existing 51 Italian US records ("Scavo archeologico"), 9 additional sites are generated with localized names (e.g. "Archaeological Excavation", "Archäologische Ausgrabung", "Αρχαιολογική Ανασκαφή"). For each site: 51 US records with translated relationship terms (rapporti/rapporti2), localized unit type abbreviations (US→SU/SE/UE/ΣΜ, USM→WSU/MSE/UEM/USZ/ΤΣΜ), translated text fields (d_stratigrafica, d_interpretativa, formazione, stato_di_conservazione, colore, consistenza, metodo_di_scavo, inclusi, documentazione) and long texts (descrizione/interpretazione) with term replacement. 12 periodizzazione records with translated chronological descriptions. Total: 510 US, 120 periods, 11 sites. The script uses the central `pyarchinit_i18n_stratigraphic` module for relationship terms and abbreviations.

#### File modificati / Modified files
- `scripts/populate_i18n_example_data.py` (nuovo / new)
- `resources/dbfiles/pyarchinit_db.sqlite` (aggiornato / updated)

---

## [5.2.9-alpha] - 2026-02-15

### refactor(i18n): Integrazione modulo i18n centrale per relazioni stratigrafiche in 5 file / Integrate central i18n module for stratigraphic relationships in 5 files

- **IT**: Aggiornati 5 file per utilizzare il modulo centrale `pyarchinit_i18n_stratigraphic` al posto di termini di relazione stratigrafica hardcoded. In `pyarchinit_matrix_exp.py`: le etichette della legenda "Contemporaneo" / "Same as" / "Sama as" ora utilizzano `RELATIONSHIPS[lang][0]` per la localizzazione corretta in tutte le 10 lingue. In `pyarchinit_pyqgis.py`: le liste `rel_covers_*` e `rel_equals_*` per 6 lingue sostituite con i group set del modulo centrale (`COVERS_GROUP`, `FILLS_GROUP`, `CUTS_GROUP`, `ABUTS_GROUP`, `SAME_AS_GROUP`, `CONNECTED_GROUP`) che coprono automaticamente tutte le 10 lingue. In `pyarchinit_db_manager.py`: i filtri SQL `select_not_like_from_db_sql()` per 3 lingue (it/en/de) sostituiti con filtri generati dinamicamente dai group set, coprendo tutte le 10 lingue. In `skatch_gpt_US.py`: il prompt di analisi Harris Matrix con termini italiani hardcoded ora utilizza `RELATIONSHIPS[lang]` per inserire i termini localizzati. In `Struttura.py`: il blocco `valuesRapporti` if/elif/else per 3 lingue (it/de/en) sostituito con lookup dinamico da `RELATIONSHIPS` + dizionario `_STRUTTURA_EXTRA` per i termini specifici delle strutture, ora con supporto per tutte le 10 lingue.
- **EN**: Updated 5 files to use the central `pyarchinit_i18n_stratigraphic` module instead of hardcoded stratigraphic relationship terms. In `pyarchinit_matrix_exp.py`: legend labels "Contemporaneo" / "Same as" / "Sama as" now use `RELATIONSHIPS[lang][0]` for correct localization across all 10 languages. In `pyarchinit_pyqgis.py`: per-language `rel_covers_*` and `rel_equals_*` lists for 6 languages replaced with central module group sets (`COVERS_GROUP`, `FILLS_GROUP`, `CUTS_GROUP`, `ABUTS_GROUP`, `SAME_AS_GROUP`, `CONNECTED_GROUP`) that automatically cover all 10 languages. In `pyarchinit_db_manager.py`: SQL filters in `select_not_like_from_db_sql()` for 3 languages (it/en/de) replaced with dynamically generated filters from group sets, covering all 10 languages. In `skatch_gpt_US.py`: Harris Matrix analysis prompt with hardcoded Italian terms now uses `RELATIONSHIPS[lang]` to insert localized terms. In `Struttura.py`: `valuesRapporti` if/elif/else block for 3 languages (it/de/en) replaced with dynamic lookup from `RELATIONSHIPS` + `_STRUTTURA_EXTRA` dict for structure-specific terms, now supporting all 10 languages.

#### File modificati / Modified files
- `modules/utility/pyarchinit_matrix_exp.py`
- `modules/gis/pyarchinit_pyqgis.py`
- `modules/db/pyarchinit_db_manager.py`
- `modules/utility/skatch_gpt_US.py`
- `tabs/Struttura.py`

---

## [5.2.8-alpha] - 2026-02-15

### refactor(pdf): Pulizia codice orfano in pyarchinit_exp_USsheet_pdf.py / Remove orphan code from pyarchinit_exp_USsheet_pdf.py

- **IT**: Rimossi ~983 righe di codice orfano dal file `pyarchinit_exp_USsheet_pdf.py`. Eliminati i due metodi placeholder `_unzip_compat_placeholder()` e tutti i blocchi `len==4`, `len==3`, `len==2` rimasti dopo la sostituzione dei vecchi metodi `unzip_rapporti_stratigrafici()` con la nuova versione unificata basata sui group set del modulo i18n centrale (`pyarchinit_i18n_stratigraphic`). I metodi `unzip_rapporti_stratigrafici_de()` e `unzip_rapporti_stratigrafici_en()` (4 istanze totali, 2 per classe) sono stati sostituiti con one-liner che delegano al metodo unificato `unzip_rapporti_stratigrafici()`. Sintassi Python verificata dopo le modifiche.
- **EN**: Removed ~983 lines of orphan code from `pyarchinit_exp_USsheet_pdf.py`. Deleted two `_unzip_compat_placeholder()` methods and all leftover `len==4`, `len==3`, `len==2` blocks remaining after replacing the old `unzip_rapporti_stratigrafici()` methods with the new unified version based on group sets from the central i18n module (`pyarchinit_i18n_stratigraphic`). The `unzip_rapporti_stratigrafici_de()` and `unzip_rapporti_stratigrafici_en()` methods (4 total instances, 2 per class) were replaced with one-liners that delegate to the unified `unzip_rapporti_stratigrafici()`. Python syntax verified after changes.

#### File modificati / Modified files
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`

---

## [5.2.7-alpha] - 2026-02-15

### feat(i18n): Aggiunta supporto lingua Greco Moderno (el_GR) / Added Modern Greek (el_GR) language support

- **IT**: Aggiunta completa del supporto per la lingua Greca Moderna (Ελληνικά) al plugin, decima lingua supportata. Modifiche effettuate: aggiunta `'el': 'el_GR'` al `LOCALE_MAPPING` in `pyarchinitPlugin.py`; aggiunta `'el': 'Ελληνικά'` a `SUPPORTED_LANGUAGES` e relativi `TUTORIALS_METADATA` + `UI_LABELS` in `Tutorial_viewer.py` e `pyarchinitDockWidget.py`; aggiunta `'el'` a `SUPPORTED_LANGUAGES` in `Fauna.py`; aggiunta voce `"EL"` ai dizionari `LANG` in tutti i 13 file tab (US_USM, Tma, Pottery, Tomba, Thesaurus, Tafonomia, Struttura, Site, Schedaind, Inv_Materiali, Inv_Lapidei, Documentazione, Campioni); creazione di 32 file tutorial tradotti in greco in `docs/tutorials/el/` con terminologia archeologica appropriata (ΣΜ per Στρωματογραφική Μονάδα, ΤΝ per Τεχνητή Νοημοσύνη ecc.); creazione file i18n `pyarchinit_plugin_el_GR.ts`; aggiornamento di tutti i 7 script di traduzione con voci `el_GR`; aggiornamento `build_docs.py`, `conf.py` e `metadata.txt`.
- **EN**: Complete addition of Modern Greek (Ελληνικά) language support to the plugin, now the tenth supported language. Changes made: added `'el': 'el_GR'` to `LOCALE_MAPPING` in `pyarchinitPlugin.py`; added `'el': 'Ελληνικά'` to `SUPPORTED_LANGUAGES` and related `TUTORIALS_METADATA` + `UI_LABELS` in `Tutorial_viewer.py` and `pyarchinitDockWidget.py`; added `'el'` to `SUPPORTED_LANGUAGES` in `Fauna.py`; added `"EL"` entry to `LANG` dicts in all 13 tab files (US_USM, Tma, Pottery, Tomba, Thesaurus, Tafonomia, Struttura, Site, Schedaind, Inv_Materiali, Inv_Lapidei, Documentazione, Campioni); created 32 Greek tutorial files in `docs/tutorials/el/` with proper archaeological terminology (ΣΜ for Στρωματογραφική Μονάδα, ΤΝ for Τεχνητή Νοημοσύνη etc.); created i18n file `pyarchinit_plugin_el_GR.ts`; updated all 7 translation scripts with `el_GR` entries; updated `build_docs.py`, `conf.py` and `metadata.txt`.

#### File modificati / Modified files
- `pyarchinitPlugin.py`
- `tabs/Tutorial_viewer.py`
- `pyarchinitDockWidget.py`
- `tabs/Fauna.py`
- `tabs/US_USM.py`, `tabs/Tma.py`, `tabs/pyarchinit_Pottery_mainapp.py`
- `tabs/Tomba.py`, `tabs/Thesaurus.py`, `tabs/Tafonomia.py`, `tabs/Struttura.py`
- `tabs/Site.py`, `tabs/Schedaind.py`, `tabs/Inv_Materiali.py`, `tabs/Inv_Lapidei.py`
- `tabs/Documentazione.py`, `tabs/Campioni.py`
- `docs/tutorials/el/` (32 file)
- `i18n/pyarchinit_plugin_el_GR.ts`
- `scripts/update_translations.py`, `scripts/update_struttura_translations.py`
- `scripts/update_fauna_translations.py`, `scripts/update_other_translations.py`
- `scripts/add_sync_translations.py`, `scripts/auto_translate_ts.py`
- `scripts/translate_ts_complete.py`
- `docs/tutorials/build_docs.py`
- `metadata.txt`

---

## [5.2.6-alpha] - 2026-02-12

### refactor(ui): Refactoring layout descrizioni in 12 animazioni docs/animations / Description layout refactoring in 12 animations docs/animations

- **IT**: Refactoring completo del layout descrizioni in tutti i 12 file HTML in `docs/animations/`. I pannelli descrizione (`.desc-box`, `.scene-desc`, `.dsc`, `.scenario-desc` — 4 varianti di classe diverse) erano overlay assoluti (`position:absolute; top/left`) che si sovrapponevano al contenuto del canvas. Sono stati tutti trasformati in `.desc-panel` — un pannello flex dedicato posizionato sotto l'area canvas. Miglioramenti: descrizioni spostate da overlay assoluto a child flex, nuovo CSS con tipografia migliorata (font 0.9rem, line-height 1.7, monospace per nomi di funzioni in `<strong>`), preservati gli schemi colore specifici di ogni file (#4ec9b0 per harris_matrix, #4fc3f7 per stratigraph_sync, #58a6ff per i restanti), regole responsive aggiunte in tutti i blocchi `@media`. Script batch Python per 10 file + 2 fix manuali per strutture HTML particolari (installation con `<div class="scene">` e stratigraph_sync con `step-indicator` e `kg-overlay`).
- **EN**: Complete description layout refactoring in all 12 HTML files in `docs/animations/`. The description panels (`.desc-box`, `.scene-desc`, `.dsc`, `.scenario-desc` — 4 different class variants) were absolute-positioned overlays (`position:absolute; top/left`) that overlapped canvas content. They have all been transformed into `.desc-panel` — a dedicated flex panel positioned below the canvas area. Improvements: descriptions moved from absolute overlay to proper flex child, new CSS with improved typography (font 0.9rem, line-height 1.7, monospace for function names in `<strong>`), preserved each file's specific color scheme (#4ec9b0 for harris_matrix, #4fc3f7 for stratigraph_sync, #58a6ff for the rest), responsive rules added in all `@media` blocks. Python batch script for 10 files + 2 manual fixes for particular HTML structures (installation with `<div class="scene">` and stratigraph_sync with `step-indicator` and `kg-overlay`).

#### File modificati / Modified files
- `docs/animations/harris_matrix_animation.html`
- `docs/animations/pyarchinit_concurrency_animation.html`
- `docs/animations/pyarchinit_create_map_animation.html`
- `docs/animations/pyarchinit_image_classification_animation.html`
- `docs/animations/pyarchinit_image_export_animation.html`
- `docs/animations/pyarchinit_installation_animation.html`
- `docs/animations/pyarchinit_media_manager_animation.html`
- `docs/animations/pyarchinit_pottery_tools_animation.html`
- `docs/animations/pyarchinit_remote_storage_animation.html`
- `docs/animations/pyarchinit_thesaurus_animation.html`
- `docs/animations/pyarchinit_timemanager_animation.html`
- `docs/animations/stratigraph_sync_animation.html`

---

## [5.2.5-alpha] - 2026-02-12

### refactor(ui): Refactoring layout descrizioni in 11 animazioni algoritmi / Description layout refactoring in 11 algorithm animations

- **IT**: Refactoring completo del layout descrizioni in tutti gli 11 file HTML in `docs/algorithm_animations/`. I pannelli descrizione (`.desc-box`) erano in precedenza overlay assoluti (`position:absolute; top/left`) che si sovrapponevano al contenuto del canvas e agli elementi animati. Sono stati trasformati in `.desc-panel` - un pannello flex dedicato posizionato sotto l'area canvas che non si sovrappone mai. Miglioramenti chiave: descrizioni spostate da overlay assoluto a child flex di `.main`, nuovo CSS con tipografia migliorata (font 0.9rem invece di 0.8rem, line-height 1.7 invece di 1.4, styling monospace per nomi di funzioni), tag `<strong>` ora renderizzati con font monospace e sfondo accent sottile per migliore leggibilità del codice, regole responsive aggiunte per schermi piccoli (max-height ridotto, padding compatto), tutti gli 11 file aggiornati in modo consistente (escluso file sperimentale MODERN_TEST), dots bar rimane nel canvas, pannello descrizione si posiziona tra canvas e area sidebar/log.
- **EN**: Complete description layout refactoring in all 11 HTML files in `docs/algorithm_animations/`. The description panels (`.desc-box`) were previously absolute-positioned overlays (`position:absolute; top/left`) that overlapped canvas content and animation elements. They have been transformed into `.desc-panel` - a dedicated flex panel positioned below the canvas area that never overlaps. Key improvements: descriptions moved from absolute overlay to proper flex child of `.main`, new CSS with improved typography (font 0.9rem instead of 0.8rem, line-height 1.7 instead of 1.4, monospace styling for function names), `<strong>` tags now rendered with monospace font and subtle accent background for better code readability, responsive rules added for small screens (reduced max-height, compact padding), all 11 files updated consistently (excluding MODERN_TEST experimental file), dots bar remains in canvas, description panel sits between canvas and sidebar/log area.

#### File modificati / Modified files
- `docs/algorithm_animations/crud_operations_algorithm.html`
- `docs/algorithm_animations/database_creation_algorithm.html`
- `docs/algorithm_animations/db_import_export_algorithm.html`
- `docs/algorithm_animations/harris_matrix_algorithm.html`
- `docs/algorithm_animations/image_classification_algorithm.html`
- `docs/algorithm_animations/media_management_algorithm.html`
- `docs/algorithm_animations/order_layer_algorithm.html`
- `docs/algorithm_animations/package_installation_algorithm.html`
- `docs/algorithm_animations/pdf_creation_algorithm.html`
- `docs/algorithm_animations/report_ai_algorithm.html`
- `docs/algorithm_animations/tops_algorithm.html`

---

## [5.2.4-alpha] - 2026-02-11

### Fix nested flex layout per 6 animazioni docs/animations / Nested flex layout fix for 6 animations in docs/animations

- **IT**: Applicato il fix del layout flex nidificato a 6 file HTML in `docs/animations/`. Il vecchio layout usava `flex-wrap:wrap` su `.app` che causava bug di ridimensionamento del canvas. Il fix introduce un nuovo wrapper `.middle` (flex row) tra header e log, cambia `.app` da `flex-wrap:wrap` a `flex-direction:column`, imposta `body` a `height:100vh;overflow:hidden` (rimosso `min-height:100vh;overflow-x:hidden`), aggiunge `min-height:0` a `.main` e alla classe scene (`.scene-wrap`/`.scene`), rimuove `width:100%`, `order`, `flex-basis`, `flex-shrink` dalla classe log (`.log-area`/`.log`), e cambia i riferimenti `.app` nei media query in `.middle`. Gestiti sia layout multi-riga (harris_matrix, concurrency) sia layout compatti su riga singola (installation, media_manager, pottery_tools, thesaurus), con varianti di nomi classe (`.sidebar`/`.side`, `.scene-wrap`/`.scene`, `.log-area`/`.log`, `.main`/`.main-col`).
- **EN**: Applied the nested flex layout fix to 6 HTML files in `docs/animations/`. The old layout used `flex-wrap:wrap` on `.app` which caused canvas resize bugs. The fix introduces a new `.middle` wrapper (flex row) between header and log, changes `.app` from `flex-wrap:wrap` to `flex-direction:column`, sets `body` to `height:100vh;overflow:hidden` (removed `min-height:100vh;overflow-x:hidden`), adds `min-height:0` to `.main` and the scene class (`.scene-wrap`/`.scene`), removes `width:100%`, `order`, `flex-basis`, `flex-shrink` from the log class (`.log-area`/`.log`), and changes `.app` references in media queries to `.middle`. Handled both multi-line layouts (harris_matrix, concurrency) and compact single-line layouts (installation, media_manager, pottery_tools, thesaurus), with class name variants (`.sidebar`/`.side`, `.scene-wrap`/`.scene`, `.log-area`/`.log`, `.main`/`.main-col`).

#### File modificati / Modified files
- `docs/animations/harris_matrix_animation.html`
- `docs/animations/pyarchinit_concurrency_animation.html`
- `docs/animations/pyarchinit_installation_animation.html`
- `docs/animations/pyarchinit_media_manager_animation.html`
- `docs/animations/pyarchinit_pottery_tools_animation.html`
- `docs/animations/pyarchinit_thesaurus_animation.html`

---

## [5.2.3-alpha] - 2026-02-11

### Rimozione completa DPR scaling dal canvas in tutte le animazioni / Complete DPR scaling removal from canvas in all animations

- **IT**: Rimosso completamente il sistema di scaling `devicePixelRatio` da tutte le 23 animazioni HTML (11 in `docs/algorithm_animations/` + 12 in `docs/animations/`). Il fix precedente (cap a 4096px + `ctx.setTransform`) non risolveva il problema: il canvas continuava a spostarsi e sparire durante il resize perché `canvas.style.width/height` settato da JS sovrascriveva il CSS `width:100%;height:100%` rompendo il flex layout. Nuovo approccio: resize semplificato a `canvas.width = wrap.clientWidth; canvas.height = h` (mapping 1:1 buffer↔display), rimosso `canvas.style.width/height` da JS, rimosso `ctx.setTransform(scale,...)`, rimosso tutte le divisioni per DPR nelle funzioni di disegno (`cv.width/(window.devicePixelRatio||1)` → `cv.width`), rimossi i fallback `canvas.clientWidth || parseInt(canvas.style.width, 10) || canvas.width` → `canvas.width`.
- **EN**: Completely removed `devicePixelRatio` scaling system from all 23 animation HTML files (11 in `docs/algorithm_animations/` + 12 in `docs/animations/`). The previous fix (4096px cap + `ctx.setTransform`) didn't solve the problem: canvas kept shifting and disappearing on resize because JS-set `canvas.style.width/height` overrode CSS `width:100%;height:100%` breaking flex layout. New approach: simplified resize to `canvas.width = wrap.clientWidth; canvas.height = h` (1:1 buffer↔display mapping), removed `canvas.style.width/height` from JS, removed `ctx.setTransform(scale,...)`, removed all DPR divisions in drawing functions (`cv.width/(window.devicePixelRatio||1)` → `cv.width`), removed `canvas.clientWidth || parseInt(...)` fallbacks → `canvas.width`.

#### File modificati / Modified files
- `docs/algorithm_animations/*.html` (tutti 11 file / all 11 files)
- `docs/animations/*.html` (tutti 12 file / all 12 files)

---

## [5.2.2-alpha] - 2026-02-11

### Fix canvas e posizione desc-box in 5 animazioni (Gruppo B) / Fix canvas and desc-box position in 5 animations (Group B)

- **IT**: Corretti gli stessi due bug nelle rimanenti 5 animazioni HTML (Gruppo B: `crud_operations_algorithm.html`, `database_creation_algorithm.html`, `image_classification_algorithm.html`, `pdf_creation_algorithm.html`, `db_import_export_algorithm.html`). Bug 1: il canvas spariva a dimensioni finestra grandi; fix: dimensioni interne limitate a max 4096px per asse con DPR-aware scaling e `ctx.setTransform(scale, ...)`. Per i file 1-4 che usavano `canvas.width = wrap.clientWidth` senza DPR, aggiunto calcolo scale completo. Per `db_import_export_algorithm.html` che gia usava DPR, aggiunto solo il cap. Aggiornate anche le funzioni `layoutBoxes()`/`drawScene()` per leggere le dimensioni CSS (`canvas.clientWidth`/`canvas.clientHeight`) invece di `canvas.width`/`canvas.height` (ora in pixel fisici). Bug 2: `.desc-box` spostato da `top:10px` a `bottom:40px`. Tutto in ES5 puro.
- **EN**: Fixed the same two bugs in the remaining 5 animation HTML files (Group B: `crud_operations_algorithm.html`, `database_creation_algorithm.html`, `image_classification_algorithm.html`, `pdf_creation_algorithm.html`, `db_import_export_algorithm.html`). Bug 1: canvas disappeared at large window sizes; fix: internal canvas dimensions capped at max 4096px per axis with DPR-aware scaling and `ctx.setTransform(scale, ...)`. For files 1-4 that used `canvas.width = wrap.clientWidth` without DPR, added full scale calculation. For `db_import_export_algorithm.html` that already used DPR, added only the cap. Also updated `layoutBoxes()`/`drawScene()` functions to read CSS dimensions (`canvas.clientWidth`/`canvas.clientHeight`) instead of `canvas.width`/`canvas.height` (now in physical pixels). Bug 2: `.desc-box` moved from `top:10px` to `bottom:40px`. All pure ES5.

#### File modificati / Modified files
- `docs/algorithm_animations/crud_operations_algorithm.html`
- `docs/algorithm_animations/database_creation_algorithm.html`
- `docs/algorithm_animations/image_classification_algorithm.html`
- `docs/algorithm_animations/pdf_creation_algorithm.html`
- `docs/algorithm_animations/db_import_export_algorithm.html`

---

## [5.2.1-alpha] - 2026-02-11

### Fix canvas e posizione desc-box in 6 animazioni / Fix canvas and desc-box position in 6 animations

- **IT**: Corretti due bug in 6 file animazione HTML (`order_layer_algorithm.html`, `harris_matrix_algorithm.html`, `media_management_algorithm.html`, `tops_algorithm.html`, `report_ai_algorithm.html`, `package_installation_algorithm.html`). Bug 1: il canvas spariva a dimensioni finestra grandi perche `canvas.width = parent.width * devicePixelRatio` poteva superare il limite browser (~16384px); fix: le dimensioni interne del canvas sono ora limitate a max 4096px per asse con guard `Math.floor`/`Math.max` e fattore `scale` calcolato come `Math.min(dpr, maxPx/w, maxPx/h)`. Bug 2: il box descrizione (`.desc-box`) era posizionato a `top:10px` sovrapponendosi all'animazione canvas; fix: spostato a `bottom:40px` sopra la dots-bar (`bottom:10px`). Tutto in ES5 puro senza `const`/`let`/arrow functions.
- **EN**: Fixed two bugs in 6 animation HTML files (`order_layer_algorithm.html`, `harris_matrix_algorithm.html`, `media_management_algorithm.html`, `tops_algorithm.html`, `report_ai_algorithm.html`, `package_installation_algorithm.html`). Bug 1: canvas disappeared at large window sizes because `canvas.width = parent.width * devicePixelRatio` could exceed browser limits (~16384px); fix: internal canvas dimensions are now capped at max 4096px per axis with `Math.floor`/`Math.max` guards and a `scale` factor computed as `Math.min(dpr, maxPx/w, maxPx/h)`. Bug 2: description box (`.desc-box`) was positioned at `top:10px` overlapping the canvas animation; fix: moved to `bottom:40px` above the dots-bar (`bottom:10px`). All pure ES5, no `const`/`let`/arrow functions.

#### File modificati / Modified files
- `docs/algorithm_animations/order_layer_algorithm.html`
- `docs/algorithm_animations/harris_matrix_algorithm.html`
- `docs/algorithm_animations/media_management_algorithm.html`
- `docs/algorithm_animations/tops_algorithm.html`
- `docs/algorithm_animations/report_ai_algorithm.html`
- `docs/algorithm_animations/package_installation_algorithm.html`

---

## [5.2.0-alpha] - 2026-02-11

### 11 animazioni tecniche algoritmi / 11 Technical Algorithm Animations

- **IT**: Create 11 animazioni HTML5 interattive per documentazione tecnica sviluppatori in `docs/algorithm_animations/`. Ogni animazione visualizza il flusso del codice reale: file sorgente, classi, funzioni, call chain, data flow tra moduli. Include canvas animato con `requestAnimationFrame`, sidebar con Source/Call Stack/Data, event log con formato `[file.py:line] Class.method()`, controlli Auto/Manual, speed 1x/2x/4x, shortcuts tastiera. Pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created 11 interactive HTML5 animations for technical developer documentation in `docs/algorithm_animations/`. Each animation visualizes real code flow: source files, classes, functions, call chains, data flow between modules. Includes animated canvas with `requestAnimationFrame`, sidebar with Source/Call Stack/Data widgets, event log with `[file.py:line] Class.method()` format, Auto/Manual controls, speed 1x/2x/4x, keyboard shortcuts. ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
1. `harris_matrix_algorithm.html` — HarrisMatrix class, Graphviz DOT, transitive reduction, adaptive DPI
2. `order_layer_algorithm.html` — Gis_Time_Controller, field definition, filter, atlas generation
3. `report_ai_algorithm.html` — ReportGenerator, OpenAI streaming, text cleaner, DOCX output
4. `image_classification_algorithm.html` — CLIP/DINOv2/OpenAI embeddings, FAISS index, similarity search
5. `media_management_algorithm.html` — Media_utility, PIL resample, remote storage, CloudinarySync
6. `crud_operations_algorithm.html` — insert/query/update/delete, session_scope, cache TTL
7. `database_creation_algorithm.html` — connection(), engine creation, Spatialite, schema mapper, migrations
8. `db_import_export_algorithm.html` — pg_dump/pg_restore, SQLite backup, Excel/GeoPackage export
9. `pdf_creation_algorithm.html` — ReportLab, NumberedCanvas, table construction, story build
10. `tops_algorithm.html` — Total Open Station CLI, CSV enrichment, coordinate transform, QGIS layers
11. `package_installation_algorithm.html` — requirements parsing, pip install loop, GitHub ZIP, verification

---

## [5.1.4-alpha] - 2026-02-11

### Nuova animazione algoritmo PDF Creation / New PDF Creation Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/pdf_creation_algorithm.html` che documenta il flusso interno del sistema di generazione PDF delle schede US di PyArchInit (`modules/utility/pyarchinit_exp_USsheet_pdf.py`). L'animazione visualizza 5 scenari: (1) Constructor `single_US_pdf_sheet.__init__(data)` con ricezione tupla di 115 campi dall'ORM US, mapping posizionale `self.sito = data[0]` fino a `self.consistenza_p = data[114]`, suddivisione in campi core US (data[0..28]), campi USM muro (data[29..50]), campi ICCD estesi (data[51..114]), e `unzip_rapporti_stratigrafici()` per parsing relazioni (copre, coperto_da, taglia, tagliato_da, riempie, riempito_da, si_appoggia_a, gli_si_appoggia, uguale_a, si_lega_a) con supporto tuple da 2 a 5 elementi e varianti multilingua (it/en/de), (2) Document Setup con registrazione font a livello modulo `pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))` per 4 varianti (Regular/Bold/Italic/BoldItalic) e `registerFontFamily('Cambria')`, `SimpleDocTemplate(f, pagesize=(21*cm, 29*cm), topMargin=10, bottomMargin=20, leftMargin=10, rightMargin=10)`, canvas personalizzato `NumberedCanvas_USsheet` con `_saved_page_states = []` in `__init__`, `showPage()` che salva stato pagina, `save()` che itera tutti gli stati e chiama `draw_page_number(num_pages)`, e `drawRightString(200*mm, 8*mm, "Pag. X di Y")` con Cambria 5pt, piu 5+ varianti ParagraphStyle (`styNormal` 7pt LEFT, `styDescrizione` 7pt JUSTIFIED, `styUnitaTipo` 14pt CENTER, `styTitoloComponenti` 7pt CENTER, `styVerticale` 7pt CENTER leading=8), (3) Table Construction con `create_sheet_archeo3_usm_fields_2()` che costruisce griglia 18 colonne, celle Paragraph con HTML (`<b>LOCALITA</b><br/>` + `escape_html(sito)`), matrice `cell_schema` di 34 righe x 18 colonne con Paragraph objects e placeholder per SPAN, `TableStyle` con `GRID(0,0,-1,-1, 0.3, black)` e ~60 regole SPAN per merge celle (header, relazioni, descrizioni, datazione, campioni, responsabile), `colWidths = (15,30,30,...,30)` per 18 colonne ~485pt totali, `Table(cell_schema, colWidths=colWidths, rowHeights=None, style=table_style)`, e branch US/USM con layout differenti, (4) Image Integration con `Connection().logo_path()` per recupero path logo personalizzato da DB settings con fallback a `$PYARCHINIT_HOME/pyarchinit_DB_folder/logo.jpg`, `Image(logo_path)` ReportLab con scaling proporzionale `drawWidth=2.5*inch, drawHeight=2.5*inch*h/w, hAlign="CENTER"`, logo separato a 2" per header scheda in `create_sheet_archeo3_usm_fields_2()`, `PIL Image` aliasato come `giggino` per ispezione dimensioni con `ImageReader` per compatibilita formato, e pattern `story.append(logo) + Spacer(4,6)` per gap verticale 6pt tra logo e tabella, (5) Build Final PDF con `elements_us_iccd = []` story list, loop `for i in range(len(records)):` su tutti i record US, per-record: `single_US_pdf_sheet(records[i])` + `elements.append(logo)` + `elements.append(Spacer(4,6))` + `elements.append(create_sheet_archeo3_usm_fields_2())` + `elements.append(PageBreak())`, output `filename = "Scheda USICCD.pdf"` aperto in `"wb"`, `doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)` per rendering finale con numerazione automatica pagine, e 7 varianti linguistiche (`build_US_sheets_en/de/fr/es/ar/ca`) con metodi `create_sheet_*()` locale-specifici. Include canvas con pipeline 5 box orizzontale (US ORM Record -> Field Mapping -> Sheet Builder -> Story List -> PDF Output), miniatura pagina PDF animata con logo placeholder, type label US/USM, righe tabella che appaiono progressivamente (LOCALITA, AREA/SAGGIO, DEF. STRATIGRAFICA, RAPPORTI, DESCRIZIONE, INTERPRETAZIONE, DATAZIONE, CAMPIONI, AFFIDABILITA, RESPONSABILE), grid overlay per styling, effetto stack multi-pagina, footer "Pag. X di Y", stage labels colorati (DATA, MAP, BUILD, STORY, PDF), particelle animate lungo il pipeline, e sidebar con Source/Call Stack/Data (Page Size, Font, Tables, Pages). Dati reali da `pyarchinit_exp_USsheet_pdf.py` linee 41-5729: classi `NumberedCanvas_USsheet`, `NumberedCanvas_USindex`, `single_US_pdf_sheet`, `US_index_pdf_sheet`, metodi `build_US_sheets()` e 7 varianti linguistiche. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/pdf_creation_algorithm.html` documenting the internal code flow of PyArchInit's US sheet PDF generation system (`modules/utility/pyarchinit_exp_USsheet_pdf.py`). The animation visualizes 5 scenarios: (1) Constructor `single_US_pdf_sheet.__init__(data)` receiving a tuple of 115 fields from the US ORM entity, positional mapping from `self.sito = data[0]` through `self.consistenza_p = data[114]`, split into core US fields (data[0..28]), USM wall fields (data[29..50]), extended ICCD fields (data[51..114]), and `unzip_rapporti_stratigrafici()` for relationship parsing (copre, coperto_da, taglia, tagliato_da, riempie, riempito_da, si_appoggia_a, gli_si_appoggia, uguale_a, si_lega_a) supporting 2-to-5-element tuples with multilingual variants (it/en/de), (2) Document Setup with module-level font registration `pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))` for 4 variants (Regular/Bold/Italic/BoldItalic) and `registerFontFamily('Cambria')`, `SimpleDocTemplate(f, pagesize=(21*cm, 29*cm), topMargin=10, bottomMargin=20, leftMargin=10, rightMargin=10)`, custom canvas `NumberedCanvas_USsheet` with `_saved_page_states = []` in `__init__`, `showPage()` saving page state, `save()` iterating all states calling `draw_page_number(num_pages)`, and `drawRightString(200*mm, 8*mm, "Pag. X di Y")` in Cambria 5pt, plus 5+ ParagraphStyle variants (`styNormal` 7pt LEFT, `styDescrizione` 7pt JUSTIFIED, `styUnitaTipo` 14pt CENTER, `styTitoloComponenti` 7pt CENTER, `styVerticale` 7pt CENTER leading=8), (3) Table Construction with `create_sheet_archeo3_usm_fields_2()` building an 18-column grid layout, Paragraph cells with HTML (`<b>LOCALITA</b><br/>` + `escape_html(sito)`), `cell_schema` matrix of 34 rows x 18 columns with Paragraph objects and placeholders for SPAN, `TableStyle` with `GRID(0,0,-1,-1, 0.3, black)` and ~60 SPAN rules for cell merging (header, relationships, descriptions, dating, samples, responsible), `colWidths = (15,30,30,...,30)` for 18 columns ~485pt total, `Table(cell_schema, colWidths=colWidths, rowHeights=None, style=table_style)`, and US/USM branch with different layouts, (4) Image Integration with `Connection().logo_path()` for custom logo path retrieval from DB settings with fallback to `$PYARCHINIT_HOME/pyarchinit_DB_folder/logo.jpg`, `Image(logo_path)` ReportLab with proportional scaling `drawWidth=2.5*inch, drawHeight=2.5*inch*h/w, hAlign="CENTER"`, separate 2" logo for sheet header in `create_sheet_archeo3_usm_fields_2()`, `PIL Image` aliased as `giggino` for dimension inspection with `ImageReader` for format compatibility, and `story.append(logo) + Spacer(4,6)` pattern for 6pt vertical gap between logo and table, (5) Build Final PDF with `elements_us_iccd = []` story list, `for i in range(len(records)):` loop over all US records, per-record: `single_US_pdf_sheet(records[i])` + `elements.append(logo)` + `elements.append(Spacer(4,6))` + `elements.append(create_sheet_archeo3_usm_fields_2())` + `elements.append(PageBreak())`, output `filename = "Scheda USICCD.pdf"` opened in `"wb"`, `doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)` for final rendering with automatic page numbering, and 7 language variants (`build_US_sheets_en/de/fr/es/ar/ca`) with locale-specific `create_sheet_*()` methods. Includes canvas with horizontal 5-box pipeline (US ORM Record -> Field Mapping -> Sheet Builder -> Story List -> PDF Output), animated PDF page miniature with logo placeholder, US/USM type label, progressively appearing table rows (LOCALITA, AREA/SAGGIO, DEF. STRATIGRAFICA, RAPPORTI, DESCRIZIONE, INTERPRETAZIONE, DATAZIONE, CAMPIONI, AFFIDABILITA, RESPONSABILE), grid overlay for styling, multi-page stack effect, "Pag. X di Y" footer, colored stage labels (DATA, MAP, BUILD, STORY, PDF), animated particles along the pipeline, and sidebar with Source/Call Stack/Data (Page Size, Font, Tables, Pages). Real data from `pyarchinit_exp_USsheet_pdf.py` lines 41-5729: classes `NumberedCanvas_USsheet`, `NumberedCanvas_USindex`, `single_US_pdf_sheet`, `US_index_pdf_sheet`, methods `build_US_sheets()` and 7 language variants. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/pdf_creation_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.3-alpha] - 2026-02-11

### Nuova animazione algoritmo Database Creation / New Database Creation Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/database_creation_algorithm.html` che documenta il flusso interno del metodo `connection()` di `pyarchinit_db_manager.py` (linee 352-556). L'animazione visualizza 5 scenari: (1) DB Type Detection con `conn_str.find("sqlite")` per branch detection, check host remoti (supabase.com, amazonaws.com, neon.tech, azure.com, heroku.com) e albero decisionale SQLite local / PG remote / PG local, (2) Engine Creation con `create_engine()` differenziato per tipo: SQLite senza pool + `listen(engine, 'connect', load_spatialite)`, PG remote con `pool_size=10, max_overflow=20, pool_timeout=60, pool_recycle=1800, pool_pre_ping=True` e `connect_args` ottimizzati, PG local con `pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600`, (3) Spatialite Loading (Mac) con `dbapi_conn.enable_load_extension(True)`, ricerca path QGIS.app/Contents/MacOS/lib/ e Contents/Frameworks/, fallback homebrew (/opt/homebrew/lib/, /usr/local/lib/), glob pattern per versioni QGIS, `dbapi_conn.load_extension(mod_spatialite)` e `PRAGMA foreign_keys=ON`, (4) Schema Setup & Mapper con `MetaData()`, `sessionmaker(bind=engine, autoflush=False, autocommit=False)`, test connessione `engine.connect()/close()`, `mapper_registry = registry()` da `pyarchinit_db_mapper.py`, e `map_imperatively()` per 40 entita (25 data + 15 GIS + 1 view: US, SITE, TOMBA, STRUTTURA, MEDIA, POTTERY, TMA, PYUS, PYUSM, PYSITO_*, PYQUOTE*, ecc.), (5) Migrations con `_get_db_checked()/_set_db_checked()` guard once-per-session via `sys.modules`, `check_and_update_sqlite_db(db_path)` pre-engine per SQLite, `check_and_update_postgres_db(self)` post-engine per PostgreSQL, `UUIDSupport(engine=engine).update_all_tables()` per 19 tabelle entity_uuid, `ensure_ut_geometry_tables_exist()` solo SQLite, e `return True` a linea 556. Include canvas con pipeline 9 box (ConnStr -> Detection -> Decision diamond -> Engine -> Spatialite/PostGIS -> Extension Search -> Schema+Session -> Mapper 40 entities -> Migrations), griglia entita animata per Sc4, branch labels per Sc1, indicatori fase colorati, particelle animate lungo il pipeline, e sidebar con Source/Call Stack/Data (DB Type, Pool Size, Tables, Migrations). Dati reali da `pyarchinit_db_manager.py:352-556`, `pyarchinit_db_mapper.py:25-246`, `sqlite_db_updater.py:2075`, `postgres_db_updater.py:1915`, `add_uuid_support.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/database_creation_algorithm.html` documenting the internal code flow of `pyarchinit_db_manager.py`'s `connection()` method (lines 352-556). The animation visualizes 5 scenarios: (1) DB Type Detection with `conn_str.find("sqlite")` for branch detection, remote host check (supabase.com, amazonaws.com, neon.tech, azure.com, heroku.com) and decision tree SQLite local / PG remote / PG local, (2) Engine Creation with differentiated `create_engine()`: SQLite with no pool + `listen(engine, 'connect', load_spatialite)`, PG remote with `pool_size=10, max_overflow=20, pool_timeout=60, pool_recycle=1800, pool_pre_ping=True` and optimized `connect_args`, PG local with `pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600`, (3) Spatialite Loading (Mac) with `dbapi_conn.enable_load_extension(True)`, QGIS.app/Contents/MacOS/lib/ and Contents/Frameworks/ path search, homebrew fallback (/opt/homebrew/lib/, /usr/local/lib/), glob patterns for QGIS versions, `dbapi_conn.load_extension(mod_spatialite)` and `PRAGMA foreign_keys=ON`, (4) Schema Setup & Mapper with `MetaData()`, `sessionmaker(bind=engine, autoflush=False, autocommit=False)`, connection test `engine.connect()/close()`, `mapper_registry = registry()` from `pyarchinit_db_mapper.py`, and `map_imperatively()` for 40 entities (25 data + 15 GIS + 1 view: US, SITE, TOMBA, STRUTTURA, MEDIA, POTTERY, TMA, PYUS, PYUSM, PYSITO_*, PYQUOTE*, etc.), (5) Migrations with `_get_db_checked()/_set_db_checked()` once-per-session guard via `sys.modules`, `check_and_update_sqlite_db(db_path)` pre-engine for SQLite, `check_and_update_postgres_db(self)` post-engine for PostgreSQL, `UUIDSupport(engine=engine).update_all_tables()` for 19 tables entity_uuid, `ensure_ut_geometry_tables_exist()` SQLite only, and `return True` at line 556. Includes canvas with 9-box pipeline (ConnStr -> Detection -> Decision diamond -> Engine -> Spatialite/PostGIS -> Extension Search -> Schema+Session -> Mapper 40 entities -> Migrations), animated entity grid for Sc4, branch labels for Sc1, colored phase indicators, animated particles along the pipeline, and sidebar with Source/Call Stack/Data (DB Type, Pool Size, Tables, Migrations). Real data from `pyarchinit_db_manager.py:352-556`, `pyarchinit_db_mapper.py:25-246`, `sqlite_db_updater.py:2075`, `postgres_db_updater.py:1915`, `add_uuid_support.py`. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/database_creation_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.2-alpha] - 2026-02-11

### Nuova animazione algoritmo Report AI / New Report AI Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/report_ai_algorithm.html` che documenta il flusso interno del sistema di generazione report AI di PyArchInit (`modules/utility/report_generator.py`, `modules/utility/report_text_cleaner.py`). L'animazione visualizza 5 scenari: (1) Read Data from DB con `ReportGenerator.read_data_from_db(db_url, table_name)`, `create_engine(db_url)` per PostgreSQL/SQLite, `MetaData(bind=engine)` e `Table(table_name, metadata, autoload_with=engine)` per reflection schema, `sessionmaker(bind=engine)` e `session.query(table).all()` per fetch record, e `return records, columns` con session cleanup, (2) Chunk Data con `ReportGenerator.chunk_data(data, chunk_size)` generator statico, `for i in range(0, len(data), chunk_size)` per iterazione a step, `yield data[i:i + chunk_size]` per rispettare limiti token API, tracking conteggio e dimensione chunk, (3) Generate Report with OpenAI con `generate_report_with_openai(prompt, modello, apikey)`, lazy import `from openai import OpenAI` per evitare conflitti pydantic, `OpenAI(api_key=apikey)` per client init, `client.chat.completions.create(model=modello, messages=[...], stream=True)` per streaming, `for chunk in response:` loop streaming con `chunk.choices[0].delta.content` per estrazione token, `messaggio_combinato += content` per accumulazione, e `ReportTextCleaner.clean_report_text()` prima del return, (4) Clean Report Text con `ReportTextCleaner.clean_report_text(text)`, `text.split('\\n')` per split in linee, `_is_list_item(line, i, lines)` per discriminare liste vere da paragrafi (check lunghezza >80, contesto ELENCO/LISTA, elementi consecutivi, keyword paragrafo), rimozione dash e capitalizzazione per falsi list item, e `prepare_for_docx(cleaned)` per strutturazione in `{paragraphs: [{text, style, level}], has_lists, has_tables}` con parsing heading (#), liste (- /bullet), tabelle (|), (5) Save Report to File con `save_report_to_file(report, file_path)`, doppia pulizia via `clean_report_text()` + `prepare_for_docx()`, `Document()` python-docx, loop `for para_info in prepared['paragraphs']` con dispatch `doc.add_heading(text, level)` / `doc.add_paragraph(text, 'List Bullet')` / `doc.add_paragraph(text)`, styling `run.font.name = 'Cambria'` e `run.font.size = Pt(12)`, e `doc.save(file_path)`. Include canvas con pipeline 5 moduli animata (Database -> Chunker -> OpenAI API -> Text Cleaner -> DOCX Writer), visualizzazione streaming token con cursore lampeggiante, icona DB con cilindro, griglia chunk con progress tracking, pattern regex cleaner animati, icona DOCX con indicatore salvataggio, particelle flusso dati tra moduli, e sidebar con Source/Call Stack/Data widgets. Dati reali da `report_generator.py` (linee 19-131) e `report_text_cleaner.py` (linee 17-302). Segue pattern ES5-strict con helper bezier per ellisse (compatibilita QtWebKit, no ctx.ellipse nativo).
- **EN**: Created new technical developer animation at `docs/algorithm_animations/report_ai_algorithm.html` documenting the internal code flow of PyArchInit's AI report generation system (`modules/utility/report_generator.py`, `modules/utility/report_text_cleaner.py`). The animation visualizes 5 scenarios: (1) Read Data from DB with `ReportGenerator.read_data_from_db(db_url, table_name)`, `create_engine(db_url)` for PostgreSQL/SQLite, `MetaData(bind=engine)` and `Table(table_name, metadata, autoload_with=engine)` for schema reflection, `sessionmaker(bind=engine)` and `session.query(table).all()` for record fetch, and `return records, columns` with session cleanup, (2) Chunk Data with `ReportGenerator.chunk_data(data, chunk_size)` static generator, `for i in range(0, len(data), chunk_size)` step iteration, `yield data[i:i + chunk_size]` to respect API token limits, chunk count and size tracking, (3) Generate Report with OpenAI with `generate_report_with_openai(prompt, modello, apikey)`, lazy import `from openai import OpenAI` to avoid pydantic conflicts, `OpenAI(api_key=apikey)` for client init, `client.chat.completions.create(model=modello, messages=[...], stream=True)` for streaming, `for chunk in response:` streaming loop with `chunk.choices[0].delta.content` for token extraction, `messaggio_combinato += content` for accumulation, and `ReportTextCleaner.clean_report_text()` before return, (4) Clean Report Text with `ReportTextCleaner.clean_report_text(text)`, `text.split('\\n')` for line splitting, `_is_list_item(line, i, lines)` to discriminate true lists from paragraphs (length check >80, ELENCO/LISTA context, consecutive items, paragraph keywords), dash removal and capitalization for false list items, and `prepare_for_docx(cleaned)` for structuring into `{paragraphs: [{text, style, level}], has_lists, has_tables}` with heading (#), list (- /bullet), table (|) parsing, (5) Save Report to File with `save_report_to_file(report, file_path)`, double cleaning via `clean_report_text()` + `prepare_for_docx()`, `Document()` python-docx, `for para_info in prepared['paragraphs']` loop dispatching `doc.add_heading(text, level)` / `doc.add_paragraph(text, 'List Bullet')` / `doc.add_paragraph(text)`, `run.font.name = 'Cambria'` and `run.font.size = Pt(12)` styling, and `doc.save(file_path)`. Includes canvas with animated 5-module pipeline (Database -> Chunker -> OpenAI API -> Text Cleaner -> DOCX Writer), streaming token visualization with blinking cursor, DB icon with cylinder, chunk grid with progress tracking, animated cleaner regex patterns, DOCX icon with save indicator, data flow particles between modules, and sidebar with Source/Call Stack/Data widgets. Real data from `report_generator.py` (lines 19-131) and `report_text_cleaner.py` (lines 17-302). Follows ES5-strict pattern with bezier ellipse helper (QtWebKit compatible, no native ctx.ellipse).

#### File creati / Created files
- `docs/algorithm_animations/report_ai_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.1-alpha] - 2026-02-11

### Nuova animazione algoritmo Image Classification / New Image Classification Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/image_classification_algorithm.html` che documenta il flusso interno del sistema di classificazione immagini e similarita ceramica di PyArchInit (`modules/utility/pottery_similarity/`). L'animazione visualizza 5 scenari: (1) Embedding Models con 4 implementazioni — `CLIPEmbeddingModel` (dim=512, ViT-B/32, locale), `DINOv2EmbeddingModel` (dim=768, ViT-B/14, locale), `OpenAIVisionEmbeddingModel` (dim=1536, text-embedding-3-small, cloud API con prompt specializzati per decorazione/forma/generale), `KhutmCLIPEmbeddingModel` (dim=512, fine-tuned per ceramica archeologica con projection layer addestrato), (2) Generate Embedding con `model.get_embedding(image_path, search_type, auto_crop, edge_preprocessing)`, esecuzione via `subprocess.run()` con `pottery_embedding_runner.py` in virtualenv pulito (rimozione PYTHONHOME/PYTHONPATH), preprocessing opzionale (auto_crop, edge detection, segment_decoration, remove_background), e ritorno `np.ndarray` float32 via file .npy temporaneo, (3) Build FAISS Index con `build_index_for_model(model_name, search_type)`, `db_manager.get_all_pottery_with_images()` per lista immagini, loop per-immagine con `build_full_image_path()` da config THUMB_RESIZE, `model.get_embedding()` + `compute_image_hash()`, e `index_manager.rebuild_index()` che crea `faiss.IndexIDMap(IndexFlatL2(dim))` salvato come .faiss + _mapping.pkl, (4) Search Similar Images con `search_similar(query_image_path, model_name, threshold)`, generazione embedding query, `index_manager.search()` per FAISS nearest neighbor, arricchimento risultati con pottery_id/media_id/similarity/similarity_percent/image_path/pottery_data, e `normalize_similarity()` model-specific (CLIP: [0.5,1.0]->[0,100], DINOv2: [0.4,1.0]->[0,100], OpenAI: lineare), (5) Text-to-Image Search con `search_by_text(text_query, model_name="openai")`, `OpenAI().embeddings.create(model="text-embedding-3-small", input=text_query)` per embedding cross-modale testo-immagine, ricerca FAISS con embedding testuale sullo stesso indice immagini, e risultati con score di similarita. Include canvas con pipeline ML animata (Image -> Preprocessing -> Embedding Model -> Vector Space -> FAISS Index -> Results), visualizzazione dots FAISS con query vector e nearest neighbors, barre similarita percentuali, icone 4 modelli con dimensioni, particelle animate lungo il pipeline, e sidebar con Source/Call Stack/Data widgets. Dati reali da `embedding_models.py`, `similarity_search.py`, `index_manager.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/image_classification_algorithm.html` documenting the internal code flow of PyArchInit's image classification and pottery similarity system (`modules/utility/pottery_similarity/`). The animation visualizes 5 scenarios: (1) Embedding Models with 4 implementations — `CLIPEmbeddingModel` (dim=512, ViT-B/32, local), `DINOv2EmbeddingModel` (dim=768, ViT-B/14, local), `OpenAIVisionEmbeddingModel` (dim=1536, text-embedding-3-small, cloud API with specialized prompts for decoration/shape/general), `KhutmCLIPEmbeddingModel` (dim=512, fine-tuned for archaeological pottery with trained projection layer), (2) Generate Embedding with `model.get_embedding(image_path, search_type, auto_crop, edge_preprocessing)`, execution via `subprocess.run()` with `pottery_embedding_runner.py` in clean virtualenv (removing PYTHONHOME/PYTHONPATH), optional preprocessing (auto_crop, edge detection, segment_decoration, remove_background), and return `np.ndarray` float32 via temporary .npy file, (3) Build FAISS Index with `build_index_for_model(model_name, search_type)`, `db_manager.get_all_pottery_with_images()` for image list, per-image loop with `build_full_image_path()` from config THUMB_RESIZE, `model.get_embedding()` + `compute_image_hash()`, and `index_manager.rebuild_index()` creating `faiss.IndexIDMap(IndexFlatL2(dim))` saved as .faiss + _mapping.pkl, (4) Search Similar Images with `search_similar(query_image_path, model_name, threshold)`, query embedding generation, `index_manager.search()` for FAISS nearest neighbor, result enrichment with pottery_id/media_id/similarity/similarity_percent/image_path/pottery_data, and model-specific `normalize_similarity()` (CLIP: [0.5,1.0]->[0,100], DINOv2: [0.4,1.0]->[0,100], OpenAI: linear), (5) Text-to-Image Search with `search_by_text(text_query, model_name="openai")`, `OpenAI().embeddings.create(model="text-embedding-3-small", input=text_query)` for cross-modal text-to-image embedding, FAISS search with text embedding on the same image index, and results with similarity scores. Includes canvas with animated ML pipeline (Image -> Preprocessing -> Embedding Model -> Vector Space -> FAISS Index -> Results), FAISS dots visualization with query vector and nearest neighbors, percentage similarity bars, 4 model icons with dimensions, animated particles along the pipeline, and sidebar with Source/Call Stack/Data widgets. Real data from `embedding_models.py`, `similarity_search.py`, `index_manager.py`. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/image_classification_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.0-alpha] - 2026-02-11

### Nuova animazione algoritmo Harris Matrix / New Harris Matrix Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/harris_matrix_algorithm.html` che documenta il flusso interno del codice dell'algoritmo Harris Matrix di PyArchInit (`modules/utility/pyarchinit_matrix_exp.py`). L'animazione visualizza 5 scenari: (1) Constructor `HarrisMatrix.__init__` con ricezione dei 6 parametri (sequence, negative, conteporene, connection, connection_to, periodi), query `db_manager.query_bool()` per record US, e apertura dialogo `Setting_Matrix().exec()`, (2) export_matrix Graph Creation con `Digraph(engine='dot', strict=False)`, configurazione `rankdir='TB'`, `splines='ortho'`, costruzione `us_rilevanti = set()`, creazione edge lists (elist1/elist2/elist3) per relazioni sequenziali/negative/contemporanee con styling da combo_box del dialogo, (3) Subgraph Clustering Period/Phase con iterazione `self.periodi`, generazione chiavi cluster gerarchiche `cluster_{site}_sito_{area}_per_{period}_fase_{phase}`, subgraph annidati `G.subgraph(name=site_key)` con `rank='same'`, query periodizzazione_table per datazione, e assegnazione nodi US alle fasi con colorazione per tipo (negative_sources/conteporene_sources/default), (4) Transitive Reduction con `G.render()` per file DOT, `subprocess.call(['tred', dot_file])` per riduzione transitiva, `Source.from_file().render()` per grafo ridotto, confronto before/after 15->11 edges, (5) Adaptive DPI Rendering con `dpi_levels = ['150','120','100','75','50']`, loop try/render con fallback automatico a DPI inferiore, check `matrix_error.txt` per errori critici vs warning cicli, e output finale JPG/PNG. Include canvas con grafi DAG Harris Matrix animati (12 nodi US, 15 edges), box periodi colorati, moduli codice (pyarchinit_matrix_exp.py, graphviz, subprocess, db_manager, Setting_Matrix, OS_utility), particelle animate lungo gli edges, indicatore DPI cascade, e confronto visuale riduzione transitiva. Dati reali dal codice sorgente `pyarchinit_matrix_exp.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/harris_matrix_algorithm.html` documenting the internal code flow of PyArchInit's Harris Matrix algorithm (`modules/utility/pyarchinit_matrix_exp.py`). The animation visualizes 5 scenarios: (1) Constructor `HarrisMatrix.__init__` receiving 6 parameters (sequence, negative, conteporene, connection, connection_to, periodi), `db_manager.query_bool()` query for US records, and `Setting_Matrix().exec()` dialog opening, (2) export_matrix Graph Creation with `Digraph(engine='dot', strict=False)`, `rankdir='TB'` and `splines='ortho'` configuration, `us_rilevanti = set()` construction, edge list creation (elist1/elist2/elist3) for sequential/negative/contemporary relationships with styling from dialog combo_boxes, (3) Subgraph Clustering Period/Phase with `self.periodi` iteration, hierarchical cluster key generation `cluster_{site}_sito_{area}_per_{period}_fase_{phase}`, nested subgraphs `G.subgraph(name=site_key)` with `rank='same'`, periodizzazione_table query for dating labels, and US node assignment to phases with type-based coloring (negative_sources/conteporene_sources/default), (4) Transitive Reduction with `G.render()` for DOT file, `subprocess.call(['tred', dot_file])` for transitive reduction, `Source.from_file().render()` for reduced graph, before/after comparison 15->11 edges, (5) Adaptive DPI Rendering with `dpi_levels = ['150','120','100','75','50']`, try/render loop with automatic fallback to lower DPI, `matrix_error.txt` check for critical errors vs cycle warnings, and final JPG/PNG output. Includes canvas with animated Harris Matrix DAG graphs (12 US nodes, 15 edges), colored period boxes, code module boxes (pyarchinit_matrix_exp.py, graphviz, subprocess, db_manager, Setting_Matrix, OS_utility), animated particles along edges, DPI cascade indicator, and transitive reduction visual comparison. Real data from `pyarchinit_matrix_exp.py` source code. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/harris_matrix_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.0.9-alpha] - 2026-02-11

### Nuova animazione algoritmo Package Installation / New Package Installation Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/package_installation_algorithm.html` che documenta il flusso interno del sistema di installazione pacchetti di PyArchInit (`scripts/modules_installer.py`, `__init__.py`). L'animazione visualizza 5 scenari: (1) Requirements Parsing con `sys.argv[1].split(',')` e fallback a `requirements.txt` con lettura di 39 pacchetti pinned (SQLAlchemy==2.0.45, reportlab==4.4.7, openai==2.15.0, langchain==1.2.3, ecc.), piu lista separata `l = ["totalopenstation"]` per pacchetti GitHub, (2) Platform Detection con `platform.system()` per Windows/Darwin/Linux, `sys.exec_prefix` per path Python, costruzione comando `cmd = "{}/bin/python{}"` e template pip con `--upgrade --user`, (3) Standard Install Loop con `for p in packages:` e `subprocess.call(["python", "-m", "pip", "install", "--upgrade", p, "--user"], shell=True)` per ogni pacchetto, tracking successo/fallimento, contatore progresso, (4) GitHub ZIP Packages con URL hardcoded `https://github.com/enzococca/totalopenstation/zipball/main`, `subprocess.call()` con `shell=True`, try/except KeyError con fallback a `shell=False`, download+extract+build wheel, (5) Verification con `get_missing_packages()` e `importlib.import_module()` per ogni pacchetto, validazione versione, report errori per import falliti, e `QgsSettings().setValue("pyArchInit/dependenciesInstalled", True)`. Include griglia 40 pacchetti (39 pip + 1 GitHub) con color coding (verde=installato, giallo=in corso, rosso=fallito, grigio=pending), pipeline 5-stage animata con frecce e dot pulsante, sidebar con Source/Call Stack/Data widgets, barra progresso e visualizzazione verifica import. Dati reali da `requirements.txt` e `modules_installer.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/package_installation_algorithm.html` documenting the internal code flow of PyArchInit's package installation system (`scripts/modules_installer.py`, `__init__.py`). The animation visualizes 5 scenarios: (1) Requirements Parsing with `sys.argv[1].split(',')` and fallback to `requirements.txt` reading 39 pinned packages (SQLAlchemy==2.0.45, reportlab==4.4.7, openai==2.15.0, langchain==1.2.3, etc.), plus separate `l = ["totalopenstation"]` list for GitHub packages, (2) Platform Detection with `platform.system()` for Windows/Darwin/Linux, `sys.exec_prefix` for Python path, command construction `cmd = "{}/bin/python{}"` and pip template with `--upgrade --user`, (3) Standard Install Loop with `for p in packages:` and `subprocess.call(["python", "-m", "pip", "install", "--upgrade", p, "--user"], shell=True)` per package, success/failure tracking, progress counter, (4) GitHub ZIP Packages with hardcoded URL `https://github.com/enzococca/totalopenstation/zipball/main`, `subprocess.call()` with `shell=True`, try/except KeyError with fallback to `shell=False`, download+extract+build wheel, (5) Verification with `get_missing_packages()` and `importlib.import_module()` per package, version validation, error reporting for failed imports, and `QgsSettings().setValue("pyArchInit/dependenciesInstalled", True)`. Includes 40-package grid (39 pip + 1 GitHub) with color coding (green=installed, yellow=installing, red=failed, gray=pending), animated 5-stage pipeline with arrows and pulsing dot, sidebar with Source/Call Stack/Data widgets, progress bar and import verification visualization. Real data from `requirements.txt` and `modules_installer.py`. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/package_installation_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.0.8-alpha] - 2026-02-11

### Nuova animazione algoritmo Total Open Station / New Total Open Station Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/tops_algorithm.html` che documenta il flusso interno del codice di integrazione Total Open Station (TOPS) di PyArchInit (`tabs/tops_pyarchinit.py`). L'animazione visualizza 5 scenari: (1) Input File Setup con `setPathinput()` via QFileDialog, selezione formato input (Leica/Topcon/Nikon/Sokkia) e formato output (csv/shp/gpkg), (2) CLI Processing con `subprocess.check_call()` che lancia `totalopenstation-cli-parser.py` con argomenti -i/-o/-f/-t/--overwrite, gestione errori e cattura output, (3) CSV Loading & Enrichment con `loadCsv()` via csv.reader in QStandardItemModel, `convert_csv()` con pandas split point_name su '-', e dialoghi QInputDialog per sito/unita_misura/disegnatore, (4) Coordinate Transformation con `checkBox_coord.isChecked()`, calcolo `p = float(ID_Z) + float(attr_Q)` per quota assoluta, e `feature.setAttribute('quota_q', p)`, (5) QGIS Layer Creation con `QgsVectorLayer("file:///path?type=csv&xField=x&yField=y")`, copia features da sourceLYR a destLYR via `dataProvider().addFeatures()`, `commitChanges()` e cleanup con `removeMapLayer()`. Include sidebar con Source, Call Stack e Data widgets, canvas con icona strumento topografico, griglia coordinate con punti survey animati, diagramma flusso 9 moduli con frecce animate, barra pipeline e visualizzazione trasferimento layer. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/tops_algorithm.html` documenting the internal code flow of PyArchInit's Total Open Station (TOPS) integration (`tabs/tops_pyarchinit.py`). The animation visualizes 5 scenarios: (1) Input File Setup with `setPathinput()` via QFileDialog, input format selection (Leica/Topcon/Nikon/Sokkia) and output format (csv/shp/gpkg), (2) CLI Processing with `subprocess.check_call()` launching `totalopenstation-cli-parser.py` with -i/-o/-f/-t/--overwrite arguments, error handling and output capture, (3) CSV Loading & Enrichment with `loadCsv()` via csv.reader into QStandardItemModel, `convert_csv()` with pandas split point_name on '-', and QInputDialog prompts for site/unit/drawer, (4) Coordinate Transformation with `checkBox_coord.isChecked()`, computing `p = float(ID_Z) + float(attr_Q)` for absolute quota, and `feature.setAttribute('quota_q', p)`, (5) QGIS Layer Creation with `QgsVectorLayer("file:///path?type=csv&xField=x&yField=y")`, feature copy from sourceLYR to destLYR via `dataProvider().addFeatures()`, `commitChanges()` and cleanup with `removeMapLayer()`. Includes sidebar with Source, Call Stack and Data widgets, canvas with survey instrument icon, coordinate grid with animated survey points, 9-module flow diagram with animated arrows, pipeline bar and layer transfer visualization. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/tops_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.0.7-alpha] - 2026-02-11

### Nuova animazione algoritmo DB Import/Export / New DB Import/Export Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/db_import_export_algorithm.html` che documenta il flusso interno del sistema di backup, ripristino ed esportazione dati di PyArchInit (`gui/dbmanagment.py`, `tabs/Excel_export.py`, `tabs/gpkg_export.py`). L'animazione visualizza 4 scenari: (1) Backup PostgreSQL con `BackupThread(QThread)`, pg_dump -Fc -Z9, monitoraggio progresso basato su file size e timeout 300s, (2) Backup SQLite con `shutil.copy()` e naming convention `backup_{name}_{date}.sqlite`, (3) Restore PostgreSQL in 3 step (dropdb/createdb -T template_postgis con fallback CREATE EXTENSION postgis/pg_restore --no-owner --no-acl) + fix sequenze e creazione tabelle utenti, (4) Export Excel/GeoPackage con psycopg2, pandas DataFrame, df.to_excel() e QgsVectorFileWriter.writeAsVectorFormat(). Include sidebar con Source, Call Stack e Data widgets, canvas con icone DB/file, frecce animate con particelle e barra progresso. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/db_import_export_algorithm.html` documenting the internal code flow of PyArchInit's backup, restore and data export system (`gui/dbmanagment.py`, `tabs/Excel_export.py`, `tabs/gpkg_export.py`). The animation visualizes 4 scenarios: (1) PostgreSQL Backup with `BackupThread(QThread)`, pg_dump -Fc -Z9, file-size-based progress monitoring and 300s timeout, (2) SQLite Backup with `shutil.copy()` and naming convention `backup_{name}_{date}.sqlite`, (3) PostgreSQL Restore in 3 steps (dropdb/createdb -T template_postgis with fallback CREATE EXTENSION postgis/pg_restore --no-owner --no-acl) + sequence fixes and user table creation, (4) Excel/GeoPackage Export with psycopg2, pandas DataFrame, df.to_excel() and QgsVectorFileWriter.writeAsVectorFormat(). Includes sidebar with Source, Call Stack and Data widgets, canvas with DB/file icons, animated arrows with particles and progress bar. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/db_import_export_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 4 scenari / complete algorithm animation with canvas, sidebar, event log, 4 scenarios

---

## [5.0.6-alpha] - 2026-02-11

### Nuova animazione algoritmo Order Layer / New Order Layer Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/order_layer_algorithm.html` che documenta il flusso interno del codice del sistema Order Layer di PyArchInit (`Gis_Time_controller.py`). L'animazione visualizza 4 scenari: (1) Field Definition & Schema con definizione colonna in `US_table.py:44`, entity mapping in `US.py:158`, variante import in `US_table_toimp.py:45`, e styling QML con `orderByClause`, (2) Controller Initialization con constructor `__init__()`, layer discovery via `fields().indexFromName('order_layer')`, query `max_num_id()` e configurazione dial/spinbox, (3) Filter Application con `define_order_layer_value()`, modalita cumulativa (`<=`) vs esatta (`=`), e `setSubsetString()` su ogni layer, (4) Atlas Generation con loop `range(0, max+1)`, filtro per-step, export `QgsLayoutExporter.exportToImage()` e completamento. Include sidebar con Source, Call Stack e Data widgets, visualizzazione layer stack animata, diagramma flusso moduli con particelle, e confronto visuale modalita cumulativa/esatta. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/order_layer_algorithm.html` documenting the internal code flow of PyArchInit's Order Layer system (`Gis_Time_controller.py`). The animation visualizes 4 scenarios: (1) Field Definition & Schema with column definition in `US_table.py:44`, entity mapping in `US.py:158`, import variant in `US_table_toimp.py:45`, and QML styling with `orderByClause`, (2) Controller Initialization with `__init__()` constructor, layer discovery via `fields().indexFromName('order_layer')`, `max_num_id()` query and dial/spinbox configuration, (3) Filter Application with `define_order_layer_value()`, cumulative (`<=`) vs exact (`=`) modes, and `setSubsetString()` on each layer, (4) Atlas Generation with `range(0, max+1)` loop, per-step filter, `QgsLayoutExporter.exportToImage()` export and completion. Includes sidebar with Source, Call Stack and Data widgets, animated layer stack visualization, module flow diagram with particles, and visual cumulative/exact mode comparison. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/order_layer_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 4 scenari / complete algorithm animation with canvas, sidebar, event log, 4 scenarios

---

## [5.0.5-alpha] - 2026-02-11

### Nuova animazione algoritmo Media Management / New Media Management Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/media_management_algorithm.html` che documenta il flusso interno del codice di gestione media di PyArchInit (`pyarchinit_media_utility.py`). L'animazione visualizza 5 scenari: (1) Input Detection con `is_remote_path()` e `get_storage_manager()`, (2) Local Thumbnail Resample con `Media_utility` (150x150 @100 DPI), (3) High-Res Resample con `Media_utility_resize` (2008x1417 @300 DPI), (4) Remote Storage Pipeline con download/resample/upload e CloudinarySync (AI tagging + OCR), (5) Video Utility con `shutil.move()`/`shutil.copy()`. Include sidebar con Source, Call Stack e Data widgets aggiornati ad ogni step. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/media_management_algorithm.html` documenting the internal code flow of PyArchInit's media management system (`pyarchinit_media_utility.py`). The animation visualizes 5 scenarios: (1) Input Detection with `is_remote_path()` and `get_storage_manager()`, (2) Local Thumbnail Resample with `Media_utility` (150x150 @100 DPI), (3) High-Res Resample with `Media_utility_resize` (2008x1417 @300 DPI), (4) Remote Storage Pipeline with download/resample/upload and CloudinarySync (AI tagging + OCR), (5) Video Utility with `shutil.move()`/`shutil.copy()`. Includes sidebar with Source, Call Stack and Data widgets updated at each step. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/media_management_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.0.4-alpha] - 2026-02-10

### Fix canvas resize in QtWebKit QWebView / Fix ridimensionamento canvas in QtWebKit QWebView

- **IT**: Risolto bug per cui le animazioni canvas HTML5 scomparivano quando si ridimensionava la finestra del Tutorial Viewer. QtWebKit non genera l'evento `window.resize` quando il widget QWebView padre viene ridimensionato, lasciando il buffer pixel del canvas con le dimensioni precedenti. Fix implementato su due livelli: (1) polling lato HTML ogni 250ms che controlla le dimensioni del container canvas e chiama `resize()` quando cambiano, e (2) bridge lato Python che intercetta `resizeEvent` del QWebView e invoca `resize()` via `evaluateJavaScript()`. Tutti i 12 file HTML delle animazioni aggiornati.
- **EN**: Fixed bug where HTML5 canvas animations disappeared when resizing the Tutorial Viewer window. QtWebKit does not fire `window.resize` when the parent QWebView widget is resized, leaving the canvas pixel buffer at stale dimensions. Fix implemented at two levels: (1) HTML-side polling every 250ms that checks canvas container dimensions and calls `resize()` when they change, and (2) Python-side bridge that intercepts QWebView `resizeEvent` and invokes `resize()` via `evaluateJavaScript()`. All 12 animation HTML files updated.

#### File modificati / Modified files
- `docs/animations/*.html` (12 file) — aggiunto polling dimensioni canvas / added canvas dimension polling
- `tabs/Tutorial_viewer.py` — aggiunto `eventFilter` + `_trigger_animation_resize()` / added resize event filter bridge
- `pyarchinitDockWidget.py` — aggiunto `eventFilter` + `_trigger_animation_resize()` / added resize event filter bridge

---

## [5.0.1-alpha] - 2026-02-10

### Riscrittura animazioni HTML5 per QtWebKit / HTML5 Animation Rewrite for QtWebKit

- **IT**: Riscrittura completa di tutte le 12 animazioni HTML5 in `docs/animations/` per compatibilita con il motore QtWebKit (~2015) integrato in QGIS 3.42.1 su macOS. Il Tutorial Viewer usa `QWebView` (QtWebKit) che supporta solo JavaScript ES5 e CSS3 senza funzionalita moderne.
- **EN**: Complete rewrite of all 12 HTML5 animations in `docs/animations/` for compatibility with the QtWebKit engine (~2015) bundled with QGIS 3.42.1 on macOS. The Tutorial Viewer uses `QWebView` (QtWebKit) which only supports ES5 JavaScript and CSS3 without modern features.

#### Modifiche JavaScript / JavaScript Changes
- `const`/`let` sostituiti con `var`
- Arrow functions `() => {}` sostituite con `function() {}`
- Template literals sostituite con concatenazione stringhe
- `String.padStart()` sostituito con funzione manuale `padTwo()`
- `NodeList.forEach()` sostituito con `Array.prototype.slice.call()` + ciclo `for`
- `classList.toggle(name, force)` sostituito con manipolazione `className` + `indexOf`/`replace`
- `element.dataset.xxx` sostituito con `getAttribute('data-xxx')`
- `String.includes()` sostituito con `indexOf() !== -1`
- `Array.findIndex()` sostituito con ciclo `for` manuale
- `ctx.ellipse()` sostituito con `drawEllipse()` custom (save/translate/scale/arc/restore)
- `.prepend()` sostituito con `insertBefore(el, firstChild)`
- Unicode escape ES6 `\u{1F3DB}` sostituiti con simboli BMP
- Optional chaining `?.` e nullish coalescing `??` rimossi

#### Modifiche CSS / CSS Changes
- Rimosso blocco `:root` e tutti i `var(--name)` — colori hardcoded inline
- Rimosso `backdrop-filter: blur()`
- CSS Grid sostituito con Flexbox + prefissi `-webkit-`
- `gap` sostituito con `margin` sui figli
- `inset: 0` sostituito con `top:0; right:0; bottom:0; left:0`
- Aggiunti prefissi `-webkit-` per: flex, transform, transition, animation, box-sizing, box-shadow
- Aggiunti `@-webkit-keyframes` per tutte le animazioni
- Rimosso `font-variant-numeric: tabular-nums`

#### File riscritti / Rewritten files
1. `pyarchinit_remote_storage_animation.html`
2. `pyarchinit_media_manager_animation.html`
3. `pyarchinit_installation_animation.html`
4. `harris_matrix_animation.html`
5. `pyarchinit_concurrency_animation.html`
6. `pyarchinit_image_classification_animation.html`
7. `pyarchinit_thesaurus_animation.html`
8. `pyarchinit_timemanager_animation.html`
9. `pyarchinit_image_export_animation.html`
10. `pyarchinit_create_map_animation.html`
11. `pyarchinit_pottery_tools_animation.html`
12. `stratigraph_sync_animation.html`

**Comportamento invariato / Behavior unchanged**: tutte le animazioni mantengono gli stessi scenari, controlli (Auto/Manual, speed, loop, pause, prev/next, restart, keyboard shortcuts), sidebar, event log, e animazioni canvas.

---

## [5.0.1-alpha] - 2026-02-08

### Fase 1 - Fondamenta

#### Commit `8abd7b2d` - Phase 1 StratiGraph integration
- **UUID Manager** (`modules/stratigraph/uuid_manager.py`): Creato modulo per generazione, validazione e gestione UUID v4. Funzioni: `generate_uuid()`, `ensure_uuid()`, `build_uri()`, `validate_uuid()`.
- **Bundle Creator** (`modules/stratigraph/bundle_creator.py`): Sistema di creazione bundle ZIP con struttura `data/`, `metadata/`, `media/`. Include export CIDOC-CRM, manifest e hash SHA-256.
- **Bundle Manifest** (`modules/stratigraph/bundle_manifest.py`): Generazione manifest JSON con 6 campi BMD obbligatori (schema_version, tool_id, provenance, integrity_hash, export_timestamp, ontology_references).
- **Bundle Validator** (`modules/stratigraph/bundle_validator.py`): Validazione pre-export con livelli ERROR/WARNING/INFO. Verifica BMD, file manifest, coerenza UUID, riferimenti ontologici.
- **Colonna entity_uuid**: Aggiunta a 19 tabelle in `structures/`, `entities/`, `structures_metadata/`.
- **Tabelle coinvolte**: site_table, us_table, inventario_materiali_table, tomba_table, periodizzazione_table, struttura_table, campioni_table, individui_table, pottery_table, media_table, media_thumb_table, media_to_entity_table, fauna_table, ut_table, tma_materiali_archeologici, tma_materiali_ripetibili, archeozoology_table, documentazione_table, inventario_lapidei_table.

#### Commit `fb1e67e5` - Auto-generate UUID on insert and migrate existing DBs
- **Entity auto-generation**: Tutte le 19 classi entity (`modules/db/entities/*.py`) ora generano automaticamente UUID v4 all'inserimento. Pattern: `entity_uuid=None` default + `uuid.uuid4()` nel `__init__`.
- **Migration hook**: `add_uuid_support.py` integrato nel flusso `connection()` di `pyarchinit_db_manager.py`. Usa pattern `_get_db_checked()` per esecuzione una tantum per sessione QGIS.
- **Engine sharing**: `UUIDSupport` accetta engine esterno per evitare connessioni duplicate.
- **Fix TMA table names**: Corretti nomi tabelle da `tma_table`/`tma_materiali_table` a `tma_materiali_archeologici`/`tma_materiali_ripetibili`.

#### Commit `85f14dac` - Add entity_uuid to SQL schemas, views, and template databases
- **PostgreSQL schema**: `entity_uuid text` aggiunto a 17 CREATE TABLE in `pyarchinit_schema_updated.sql` e 16 in `pyarchinit_schema_clean.sql`.
- **Migration SQL**: 19 ALTER TABLE in `pyarchinit_update_postgres.sql` (IF NOT EXISTS) e `pyarchinit_update_sqlite.sql`.
- **Views SQL**: `entity_uuid` aggiunto a 16 view SELECT in `create_view.sql` e `create_view_updated.sql`.
- **Template SQLite**: Colonna entity_uuid aggiunta a tutte le 19 tabelle in `pyarchinit.sqlite` e `pyarchinit_db.sqlite`.

#### Metadata
- **Versione**: Aggiornata a `5.0.1-alpha` in `metadata.txt`.
- **Experimental**: Impostato a `False` in `metadata.txt`.
- **Changelog**: Aggiunto blocco StratiGraph nel changelog di metadata.txt.

---

### Fase 2 — Offline-First

#### Sync State Machine (`modules/stratigraph/sync_state_machine.py`) — NUOVO
- **Enum `SyncState`**: 6 stati del ciclo di vita sync — `OFFLINE_EDITING`, `LOCAL_EXPORT`, `LOCAL_VALIDATION`, `QUEUED_FOR_SYNC`, `SYNC_SUCCESS`, `SYNC_FAILED`.
- **Classe `SyncStateMachine(QObject)`**: macchina a stati finiti con segnali Qt `state_changed(str, str)` e `transition_failed(str, str, str)`.
- **Mappa transizioni**: definizione esplicita delle transizioni valide tra stati.
- **Persistenza**: stato corrente e cronologia transizioni (max 50 voci, formato JSON) salvati in `QgsSettings` con prefisso `pyArchInit/stratigraph/`.
- **Metodi**: `transition()`, `get_transition_history()`, `reset()`.
- **Logging**: tutte le transizioni registrate via `QgsMessageLog`.

#### Sync Queue (`modules/stratigraph/sync_queue.py`) — NUOVO
- **Database SQLite dedicato**: `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite` con journal mode WAL.
- **Tabella `sync_queue`**: campi `id`, `bundle_path`, `bundle_hash`, `created_at`, `status`, `attempts`, `last_attempt_at`, `last_error`, `metadata`.
- **Dataclass `QueueEntry`**: rappresentazione in-memory di una voce della coda.
- **Classe `SyncQueue`**: operazioni FIFO — `enqueue`, `dequeue` (marca come uploading), `mark_completed`, `mark_failed` (auto-retry fino a 5 tentativi), `retry_failed`, `get_pending`, `get_all`, `cleanup_completed`, `get_stats`.
- **Thread-safety**: pattern open-use-close per le connessioni SQLite.

#### Connectivity Monitor (`modules/stratigraph/connectivity_monitor.py`) — NUOVO
- **Classe `ConnectivityMonitor(QObject)`**: monitoraggio periodico della connettivita di rete.
- **Segnali Qt**: `connection_available`, `connection_lost`, `connectivity_changed(bool)`.
- **Health check**: HTTP GET periodico (default 30s) verso URL configurabile (default `localhost:8080/health`).
- **Debounce**: N check consecutivi con stesso risultato prima di cambiare stato (default 2).
- **Rete**: usa `QgsNetworkAccessManager` con timeout 5 secondi.
- **Configurazione**: tutti i parametri regolabili via `QgsSettings`.

#### Sync Orchestrator (`modules/stratigraph/sync_orchestrator.py`) — NUOVO
- **Classe `SyncOrchestrator(QObject)`**: coordinamento centrale di state machine, coda e connectivity monitor.
- **Segnali Qt**: `sync_started(int)`, `sync_progress(int, int, str)`, `sync_completed(int, bool, str)`, `bundle_exported(str)`.
- **Pipeline `export_bundle(site_name)`**: flusso completo `OFFLINE_EDITING` -> `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC` con validazione bundle integrata (usa `BundleCreator` e `validate_bundle` dalla Fase 1).
- **`sync_now()`**: forza tentativo di sincronizzazione immediato.
- **`get_status()`**: snapshot dello stato corrente dell'orchestratore.
- **Auto-sync**: la coda viene processata automaticamente quando arriva il segnale `connection_available`.
- **Retry con backoff esponenziale**: intervalli `[30s, 60s, 120s, 300s, 900s]`.
- **Upload temporaneo**: wrapper HTTP POST placeholder in attesa delle specifiche API WP4.

#### UI Sync Panel (`gui/stratigraph_sync_panel.py`) — NUOVO
- **Classe `StratiGraphSyncPanel(QDockWidget)`**: pannello dock con indicatori di stato (stato sync, connettivita, statistiche coda, ultimo sync).
- **Pulsanti azione**: Export Bundle, Sync Now, Queue...
- **Log attivita**: `QTextEdit` read-only con voci timestampate.
- **`QueueDialog(QDialog)`**: finestra con `QTableWidget` per visualizzare tutte le voci della coda.
- **Aggiornamento live**: connesso ai segnali dell'orchestratore per aggiornamenti in tempo reale.
- **Refresh periodico**: timer a 5 secondi per statistiche della coda.

#### Icona (`resources/icons/stratigraph_sync.png`) — NUOVO
- Icona 22x22 PNG: cerchio verde con frecce di sync e lettera "S".

#### File modificati

- **`modules/stratigraph/__init__.py`**: aggiunti import Fase 2 — `SyncState`, `SyncStateMachine`, `SyncQueue`, `QueueEntry`, `ConnectivityMonitor`, `SyncOrchestrator`.
- **`pyarchinitPlugin.py`**: integrazione nel plugin principale:
  - `_init_stratigraph_sync()`: crea `SyncOrchestrator`, `StratiGraphSyncPanel`, aggiunge dock widget (nascosto per default), crea azione toolbar con icona `stratigraph_sync.png`, avvia orchestratore.
  - `_unload_stratigraph_sync()`: ferma orchestratore, rimuove dock widget e icona toolbar.
  - `_toggle_sync_panel()`: mostra/nasconde il pannello sync.
  - `_init_stratigraph_sync()` chiamato alla fine di tutti e 4 i blocchi locale in `initGui()` (it, en, de, else).
  - `_unload_stratigraph_sync()` chiamato all'inizio di `unload()`.
- **`STRATIGRAPH_INTEGRATION.md`**: aggiornamento stati Task 2.x da "DA FARE" a "FATTO 100%", gap analysis sezione 3.4 completata, retry sezione 3.5 completato, struttura moduli aggiornata, tabella riepilogativa da ~42% a ~57%.

---

### Strumenti di Testing

#### Mock Server (`scripts/stratigraph_mock_server.py`) — NUOVO

Server HTTP locale che simula il Knowledge Graph di WP4 per testare il flusso di sincronizzazione senza dipendere dall'infrastruttura esterna.

**Perché serve**: Il server StratiGraph (gestito da WP4) non è ancora disponibile. Per verificare che il flusso di sync funzioni end-to-end — dall'export del bundle alla validazione, all'invio HTTP — serve un endpoint locale che accetti i bundle e risponda correttamente al health check.

**Architettura StratiGraph**: PyArchInit NON sincronizza con un server personale. StratiGraph è un **Knowledge Graph condiviso** dove confluiscono dati da più strumenti archeologici (PyArchInit, 3DHOP, ArcheoGrid, ecc.), ciascuno specializzato in un aspetto. Il flusso è **unidirezionale**: PyArchInit esporta bundle CIDOC-CRM verso il KG, non riceve dati indietro. Il mock server simula esattamente questo comportamento.

**Endpoint simulati**:
- `GET /health` — health check (usato da `ConnectivityMonitor`)
- `POST /api/v1/bundles` — ricezione bundle ZIP (usato da `SyncOrchestrator`)
- `GET /api/v1/bundles` — lista bundle ricevuti (JSON)
- `GET /` — pagina web di stato (solo modalità FastAPI)

**Due modalità**:
- Completa (FastAPI + uvicorn): web UI, log dettagliati. Richiede `pip install fastapi uvicorn python-multipart`.
- Semplice (http.server built-in): nessuna dipendenza esterna, funzionalità base.

**Uso**:
```bash
python scripts/stratigraph_mock_server.py          # FastAPI (default)
python scripts/stratigraph_mock_server.py --simple  # http.server
```

I bundle ricevuti vengono salvati in `$PYARCHINIT_HOME/stratigraph_mock_received/`.

#### Documentazione architettura

- **`STRATIGRAPH_INTEGRATION.md` sezione 1.1**: Aggiunto diagramma completo dell'architettura del Knowledge Graph StratiGraph, spiegazione del flusso dati unidirezionale, chiarimento su cosa NON è il sistema, e motivazione dell'architettura offline-first.
- **`STRATIGRAPH_INTEGRATION.md` sezione 1.2**: Documentazione dettagliata del mock server con tabella endpoint, istruzioni d'uso e opzioni di configurazione.

---

### Tutorial Viewer — Embedded Animation Playback

#### `tabs/Tutorial_viewer.py` — RISCRITTO parzialmente
- **Multi-path import**: QWebEngineView importato tramite fallback chain (`qgis.PyQt.QtWebEngineWidgets` → `PyQt5.QtWebEngineWidgets` → `PyQt6.QtWebEngineWidgets`). Nuovi globali: `HAS_WEBENGINE_ANIM`, `_QWebEngineView`.
- **Rimossa classe `TutorialWebEnginePage`**: non più necessaria — QTextBrowser gestisce il markdown, QWebEngineView carica le animazioni direttamente via `setUrl()`.
- **QStackedWidget**: area contenuto ora usa `self.content_stack` con due pagine:
  - **Pagina 0**: `self.content_browser` (QTextBrowser) — sempre usato per rendering markdown
  - **Pagina 1**: `self.animation_viewer` (QWebEngineView) — per file HTML5 animazione
- **`_on_link_clicked()`**: rileva file `.html` locali e li carica nel viewer animazione embedded tramite `_load_animation()` invece di aprire il browser di sistema.
- **`_load_animation(path)`**: sostituisce `_load_local_html_file()` — switcha lo stack a pagina 1, carica via `setUrl()`, mostra pulsante indietro.
- **`_on_back_clicked()`**: switcha lo stack a pagina 0, pulisce il viewer animazione.
- **Gestione immagini**: rimosso branch `use_webengine` — sempre usa thumbnail base64 di QTextBrowser.

#### `pyarchinitDockWidget.py` — RISCRITTO parzialmente
- **Multi-path import**: stesso pattern di fallback chain. Nuovi globali: `_DockQWebEngineView`, `_dock_log()`.
- **Rimossa classe `DockTutorialWebPage`**: non più necessaria.
- **QStackedWidget**: tab tutorial ora usa `self.tutorial_content_stack` con:
  - **Pagina 0**: `self.tutorial_content` (QTextBrowser) — markdown
  - **Pagina 1**: `self.tutorial_animation` (QWebEngineView) — animazioni
- **`_on_tutorial_link_clicked(url)`**: nuovo handler per click su link in QTextBrowser, rileva `.html` e carica nel viewer embedded.
- **`_load_animation_in_viewer(path)`**: switcha lo stack a pagina 1.
- **`_on_tutorial_back()`**: switcha lo stack a pagina 0.
- **Gestione immagini**: sempre converte a base64 (rimossa condizione `not HAS_WEBENGINE`).

#### Degradazione graceful
Se QWebEngineView non è disponibile da nessun percorso di import, `self.animation_viewer` / `self.tutorial_animation` è `None`, e i link `.html` aprono nel browser di sistema (comportamento precedente).

---

### UI & Branding

#### Splash Screen — Redesign futuristico (`gui/pyarchinit_splash.py`) — RISCRITTO

Splash screen completamente riscritto con design futuristico "deep space", sempre in movimento.

**Nuove classi:**
- `Particle`: singola particella nel campo (usa `__slots__` per performance)
- `OrbitalRing`: anello orbitale con proiezione 3D
- `FuturisticSplashWidget(QWidget)`: widget principale con rendering custom via `paintEvent`

**Effetti visivi (tutti in movimento continuo):**
- **Particle field** (90 particelle): drift orbitale con gravita verso il centro, glow, fade-in/out, palette cyan/blue/orange
- **4 anelli orbitali 3D**: proiezione prospettica con tilt variabile, punti luminosi, color cycling
- **5 nodi energetici**: orbiting con trail ghosting (3 posizioni fantasma)
- **Onde energetiche**: 3 anelli concentrici espandibili dal centro
- **Griglia di scansione**: linee sottili con sweep line orizzontale animata
- **Logo centrale**: halo pulsante multi-layer (4 livelli), sfondo circolare scuro con bordo cyan
- **Titolo "pyArchInit 5"**: letter-spacing, glow cyan pulsante
- **Testo status**: effetto typewriter (30 chars/sec) con cursore lampeggiante
- **Accenti angolari**: bracket sui 4 angoli + tick dati mobili sui bordi superiore/inferiore
- **Sfondo**: gradiente radiale deep-space (15,25,60 -> 3,5,15)

**Loghi partner (in basso, centrati):**
- Logo CNR-ISPC con glow e pulsazione opacita
- Logo Horizon StratiGraph (placeholder) con glow
- Separatore luminoso con gradiente fade
- Label "in collaboration with" animata

**Compatibilita:**
- Qt5/Qt6: tutti gli import usano `qgis.PyQt` (version-independent)
- Enum Qt6 syntax: `Qt.WindowType.FramelessWindowHint`, `Qt.PenStyle.NoPen`, etc.
- API pubblica invariata: `PyArchInitSplash(parent, message, modal)`, `set_message()`, `show_splash_during_operation()`

**Dimensioni:** 700x500px (da 650x520)

#### Loghi partner — NUOVI
- `resources/icons/logo_cnr_ispc.png` (258x89px): logo compatto CNR-ISPC scaricato da ispc.cnr.it
- `resources/icons/logo_horizon_stratigraph.png` (258x89px): placeholder generato programmaticamente — da sostituire con logo ufficiale Horizon

---

### Documentation

#### README.md — Aggiornamento progetto StratiGraph
- Aggiunta sezione **StratiGraph / Horizon Europe Integration** con: CIDOC-CRM mapping, bundle system, offline-first architecture, UUID, connectivity monitoring, sync dashboard
- Aggiornato **Project Structure** con albero `modules/stratigraph/` (8 file)
- Aggiunta sezione **Acknowledgments > StratiGraph - Horizon Europe** con partner (CNR-ISPC, 3DR, ARC) e timeline
- Link a `STRATIGRAPH_INTEGRATION.md` per dettagli tecnici

---

### Organizzazione Progetto e Tooling / Project Organization & Tooling

#### Commit `284835e2` — 2026-02-10: Riorganizzazione animazioni, pulizia git, agenti autonomi / Reorganize animations, git cleanup, autonomous agents

##### Riorganizzazione file animazioni / Animation files reorganization
- IT: Spostati 12 file HTML5 animazione da `docs/` a `docs/animations/` per una struttura directory piu ordinata e manutenibile.
- EN: Moved 12 HTML5 animation files from `docs/` root to `docs/animations/` for a cleaner, more maintainable directory structure.

##### Aggiornamento riferimenti tutorial / Tutorial references update
- IT: Aggiornati 84 riferimenti in 77 file tutorial markdown in tutte le 7 lingue (it, en, de, es, fr, ar, ca) per puntare al nuovo percorso `../animations/` invece di `../../`.
- EN: Updated 84 references across 77 tutorial markdown files in all 7 languages (it, en, de, es, fr, ar, ca) to point to the new path `../animations/` instead of `../../`.

##### Aggiornamento `.gitignore` / `.gitignore` update
- IT: Aggiornato `.gitignore` per tracciare la directory `docs/animations/` e tutti e 4 i file di configurazione agenti in `.claude/agents/`.
- EN: Updated `.gitignore` to track the `docs/animations/` directory and all 4 agent config files in `.claude/agents/`.

##### Agenti autonomi in `CLAUDE.md` / Autonomous agents in `CLAUDE.md`
- IT: Aggiunta sezione "Autonomous Agents" a `CLAUDE.md` con istruzioni per l'invocazione automatica degli agenti `stratigraph-changelog` e `tutorial-updater` dopo ogni modifica al codice o all'interfaccia utente.
- EN: Added "Autonomous Agents" section to `CLAUDE.md` with instructions for automatic invocation of `stratigraph-changelog` and `tutorial-updater` agents after every code or UI change.

##### Aggiornamento configurazione agenti / Agent configuration update
- IT: Aggiornati `.claude/agents/stratigraph-changelog.md` (invocazione proattiva, voci bilingui IT+EN) e `.claude/agents/tutorial-updater.md` (invocazione proattiva).
- EN: Updated `.claude/agents/stratigraph-changelog.md` (proactive invocation, bilingual IT+EN entries) and `.claude/agents/tutorial-updater.md` (proactive invocation).

##### Pulizia cronologia git / Git history cleanup
- IT: Rimossi tutti i 108 riferimenti `Co-Authored-By: Claude` dalla cronologia git su tutti i branch tramite `git filter-repo` e force push. Tutti i commit risultano ora esclusivamente a nome di Enzo Cocca.
- EN: Removed all 108 `Co-Authored-By: Claude` lines from git history across all branches via `git filter-repo` and force push. All commits now appear solely under Enzo Cocca's authorship.

#### File modificati / Files modified
- `docs/animations/` — nuova directory con 12 file HTML5 animazione
- `docs/tutorials/{it,en,de,es,fr,ar,ca}/*.md` — 77 file, 84 riferimenti aggiornati
- `.gitignore` — regole per `docs/animations/` e `.claude/agents/`
- `CLAUDE.md` — sezione Autonomous Agents
- `.claude/agents/stratigraph-changelog.md` — configurazione aggiornata
- `.claude/agents/tutorial-updater.md` — configurazione aggiornata

---

### Compatibilita QtWebKit / QtWebKit Compatibility

#### `docs/animations/pyarchinit_remote_storage_animation.html` — RISCRITTO per QtWebKit / REWRITTEN for QtWebKit

##### Description / Descrizione
- 🇮🇹 **IT**: Riscritta completamente l'animazione HTML5 "Remote Storage" per compatibilita con il vecchio motore QtWebKit (circa 2015) usato dal QWebView di QGIS. Tutte le funzionalita ES6+ sono state sostituite con equivalenti ES5: `const`/`let` → `var`, arrow functions → `function()`, template literals → concatenazione stringhe, `padStart` → funzione manuale `padTwo()`, `classList.toggle(name, force)` → if/else con add/remove via regex, `forEach` su NodeList → `Array.prototype.slice.call()`, `ctx.ellipse()` → funzione `drawEllipse()` con `arc()` + `scale()`. Nel CSS: rimosso `:root` e `var()` con colori hardcoded, rimosso `backdrop-filter`, sostituito CSS Grid con Flexbox + prefissi `-webkit-`, aggiunti `@-webkit-keyframes`, aggiunti prefissi `-webkit-flex`, `-webkit-box-flex`, `-webkit-transform`, etc. Il layout, le animazioni Canvas, l'interattivita e il comportamento visivo sono identici all'originale.
- 🇬🇧 **EN**: Completely rewrote the "Remote Storage" HTML5 animation for compatibility with the old QtWebKit engine (circa 2015) used by QGIS QWebView. All ES6+ features replaced with ES5 equivalents: `const`/`let` → `var`, arrow functions → `function()`, template literals → string concatenation, `padStart` → manual `padTwo()` function, `classList.toggle(name, force)` → if/else with add/remove via regex, `forEach` on NodeList → `Array.prototype.slice.call()`, `ctx.ellipse()` → `drawEllipse()` function using `arc()` + `scale()`. In CSS: removed `:root` and `var()` with hardcoded colors, removed `backdrop-filter`, replaced CSS Grid with Flexbox + `-webkit-` prefixes, added `@-webkit-keyframes`, added `-webkit-flex`, `-webkit-box-flex`, `-webkit-transform` prefixes, etc. Layout, Canvas animations, interactivity and visual behavior are identical to the original.

##### File modificati / Files modified
- `docs/animations/pyarchinit_remote_storage_animation.html` — riscrittura completa ES5/QtWebKit

---

#### `docs/animations/pyarchinit_media_manager_animation.html` — RISCRITTO per QtWebKit / REWRITTEN for QtWebKit

##### Description / Descrizione
- IT: Riscritta completamente l'animazione HTML5 "Media Manager" per compatibilita con il vecchio motore QtWebKit (circa 2015) usato dal QWebView di QGIS. Tutte le funzionalita ES6+ sono state sostituite con equivalenti ES5: `const`/`let` -> `var`, arrow functions -> `function(){}`, template literals -> concatenazione stringhe, `padStart` -> funzione manuale `padTwo()`, `classList.toggle(name, force)` -> if/else con add/remove via regex su `className`, `forEach` su NodeList -> `Array.prototype.slice.call()` + for-loop, `dataset.xxx` -> `getAttribute('data-xxx')`, `String.includes()` -> `indexOf() !== -1`. Nel CSS: rimosso `:root` e `var(--name)` con colori hardcoded inline, rimosso `backdrop-filter`, sostituito CSS Grid con Flexbox + prefissi `-webkit-`, `gap` sostituito con `margin` sui figli, aggiunti `@-webkit-keyframes`, aggiunti prefissi `-webkit-flex`, `-webkit-transform`, `-webkit-transition`, `-webkit-animation`, `-webkit-align-items`, `-webkit-justify-content`, `-webkit-flex-direction`, `-webkit-flex-wrap`, `-webkit-flex-shrink`, `-webkit-order`. Il layout (header, main canvas, sidebar, log), le animazioni Canvas (media gallery, association diagram, entity nodes, dashed arrows), l'interattivita (auto/manual mode, speed, play/pause, loop, prev/next, keyboard shortcuts, scenario select) e il comportamento visivo sono identici all'originale.
- EN: Completely rewrote the "Media Manager" HTML5 animation for compatibility with the old QtWebKit engine (circa 2015) used by QGIS QWebView. All ES6+ features replaced with ES5 equivalents: `const`/`let` -> `var`, arrow functions -> `function(){}`, template literals -> string concatenation, `padStart` -> manual `padTwo()` function, `classList.toggle(name, force)` -> if/else with add/remove via regex on `className`, `forEach` on NodeList -> `Array.prototype.slice.call()` + for-loop, `dataset.xxx` -> `getAttribute('data-xxx')`, `String.includes()` -> `indexOf() !== -1`. In CSS: removed `:root` and `var(--name)` with hardcoded inline colors, removed `backdrop-filter`, replaced CSS Grid with Flexbox + `-webkit-` prefixes, `gap` replaced with `margin` on children, added `@-webkit-keyframes`, added `-webkit-flex`, `-webkit-transform`, `-webkit-transition`, `-webkit-animation`, `-webkit-align-items`, `-webkit-justify-content`, `-webkit-flex-direction`, `-webkit-flex-wrap`, `-webkit-flex-shrink`, `-webkit-order` prefixes. Layout (header, main canvas, sidebar, log), Canvas animations (media gallery, association diagram, entity nodes, dashed arrows), interactivity (auto/manual mode, speed, play/pause, loop, prev/next, keyboard shortcuts, scenario select) and visual behavior are identical to the original.

##### File modificati / Files modified
- `docs/animations/pyarchinit_media_manager_animation.html` — riscrittura completa ES5/QtWebKit

---

## Note

- Tutte le modifiche sono sul branch `Stratigraph_00001`
- La Fase 1 (Fondamenta) e la Fase 2 (Offline-First) sono completate
- La Fase 3 (Integrazione WP4) e in attesa delle specifiche API dal WP4
- La Fase 4 (CIDOC-CRM e ottimizzazione) e ancora da implementare
- I task bloccati dipendono da deliverable esterni WP3/WP4
