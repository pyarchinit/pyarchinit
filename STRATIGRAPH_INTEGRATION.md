# PyArchInit — Piano di Integrazione StratiGraph (Progetto Horizon)

> Documento di riferimento per l'implementazione delle funzionalità richieste dal progetto europeo StratiGraph.
> Aggiornare le percentuali di completamento man mano che si procede.
> Ultimo aggiornamento: 2026-02-08

---

## Indice

1. [Contesto del Progetto](#1-contesto-del-progetto)
2. [Stato Attuale di PyArchInit](#2-stato-attuale-di-pyarchinit)
3. [Requisiti StratiGraph e Gap Analysis](#3-requisiti-stratigraph-e-gap-analysis)
4. [Piano di Implementazione](#4-piano-di-implementazione)
   - [Fase 1 — Fondamenta (M7–M10)](#fase-1--fondamenta-m7m10)
   - [Fase 2 — Offline-First (M10–M14)](#fase-2--offline-first-m10m14)
   - [Fase 3 — Integrazione WP4 (M12–M16)](#fase-3--integrazione-wp4-m12m16)
   - [Fase 4 — Testing e Raffinamento (M15–M18)](#fase-4--testing-e-raffinamento-m15m18)
5. [Dipendenze Esterne](#5-dipendenze-esterne)
6. [Registro Modifiche](#6-registro-modifiche)

---

## 1. Contesto del Progetto

PyArchInit partecipa al progetto StratiGraph come **Task 5.4 di WP5**, guidato da 3DR con CNR e ARC.
L'obiettivo NON è riscrivere PyArchInit, ma estenderlo con moduli aggiuntivi per:

- Esportare dati verso il **Knowledge Graph** centrale tramite formato **bundle** standardizzato
- Funzionare **completamente offline** con sincronizzazione automatica al ritorno della connessione
- Mappare i dati interni verso l'ontologia **CIDOC-CRM**
- Assegnare **identificatori persistenti (PID/UUID)** a ogni entità
- Integrarsi con il **toolkit Python di WP4** (API, auth, sync)

**Tempistiche**: M1 = Novembre 2025, deadline primo periodo = M18 (Maggio 2027)
**Risorse**: ~8,5 person-months (4,5 WP5 + 4 WP13)

---

## 2. Stato Attuale di PyArchInit

Riepilogo delle funzionalità già presenti nel codebase, con riferimenti ai file.

### 2.1 Mappatura CIDOC-CRM

File: `modules/s3dgraphy/cidoc_crm_mapper.py`

- **Class mapping**: stratigraphic\_unit -- E18, site -- E53, period -- E4, special\_find -- E19
- **Property mapping**: P120, P119, P132, P113, P46, P122
- **JSON-LD export**: `export_to_cidoc_jsonld()`
- **RDF Turtle export**: `export_to_rdf_turtle()`
- **Namespace**: `http://www.cidoc-crm.org/cidoc-crm/` e `http://pyarchinit.org/ontology/`

### 2.2 Vocabolari Controllati

- **Vocabolari GNA (8+)** -- `modules/gna/gna_vocabulary_mapper.py`
  AMA, MTDM, VGTC, GPMT, MCND, ACCB, WTHR, VRP, VRD
- **Thesaurus multi-lingua** -- `tabs/Thesaurus.py`
  IT, EN, DE, ES, FR, AR. Tabella `pyarchinit_thesaurus_sigle`
- **Field mapping GNA** -- `modules/gna/gna_field_mapper.py`
  Mappatura campi interni verso standard GNA

### 2.3 Export

Formati supportati (10+):

- **PDF** -- `tabs/Pdf_export.py` -- generate\_US\_pdf() ecc.
- **Excel** -- `tabs/Excel_export.py` -- Pandas + xlsxwriter
- **GeoPackage** -- `tabs/gpkg_export.py` -- QgsVectorFileWriter
- **GeoPackage GNA** -- `modules/gna/gna_exporter.py` -- MOPR, MOSI, VRP, VRD
- **CSV** -- `modules/utility/csv_writer.py` -- UTF-8
- **JSON-LD** -- `modules/s3dgraphy/cidoc_crm_mapper.py` -- CIDOC-CRM
- **RDF Turtle** -- `modules/s3dgraphy/cidoc_crm_mapper.py` -- CIDOC-CRM
- **GraphML** -- `modules/s3dgraphy/s3dgraphy_integration.py`
- **Harris Matrix (DOT)** -- `modules/utility/pyarchinit_matrix_exp.py`
- **ZIP** -- `tabs/pyarchinit_Pottery_mainapp.py` -- ceramica index+model

### 2.4 Sincronizzazione Database

File: `modules/db/database_sync.py` (1290 righe)

- **Sync engine**: PostgreSQL -- SQLite bidirezionale
- **Sync differenziale**: solo record nuovi/modificati
- **Threading**: SyncAnalyzer e SyncWorker (QThread)
- **Config persistente**: SyncConfig + QgsSettings
- **123 tabelle gestite**: data, thesaurus, media, geometric

### 2.5 Validazione Dati

- **Validazione entita** -- `modules/report/validation_tools.py`
  US, siti, materiali, ceramica, tombe, periodi, strutture
- **Validazione GeoPackage** -- `modules/gna/gna_exporter.py`
  validate\_geopackage()
- **Validazione campi** -- `modules/utility/tma_import_parser.py`
  validate\_field\_value(), validate\_required\_fields()

### 2.6 Autenticazione e Permessi

- **User management** -- `gui/user_management_dialog.py`
  Ruoli, admin, permessi
- **Permission handler** -- `modules/db/permission_handler.py`
  has\_permission(), PostgreSQL has\_table\_privilege()
- **Credenziali multi-source** -- `modules/storage/credentials.py`
  Env, .env, QGIS, JSON, manual
- **JWT (Unibo backend)** -- `modules/storage/unibo_filemanager_backend.py`
  Token refresh automatico

### 2.7 Concorrenza e Versioning

- **Conflict detection** -- `modules/db/concurrency_manager.py`
  check\_version\_conflict(), lock/unlock
- **Versioning columns** -- `modules/db/add_versioning_support.py`
  last\_modified\_timestamp, last\_modified\_by, version\_number
- **ID migration mapper** -- `modules/db/media_migration_mapper.py`
  Rimappatura ID tra database

### 2.8 Infrastruttura di Rete

- **Network manager** -- `tabs/networkaccessmanager.py`
  Qt-based, SSL, auth, redirect
- **Storage manager** -- `modules/storage/storage_manager.py`
  Auto-detect backend da URL scheme
- **Storage backends** -- `modules/storage/`
  HTTP, S3, WebDAV, GDrive, Dropbox, Cloudinary, SFTP
- **API proxy** -- `storage_server/main.py`
  FastAPI, Google Drive proxy

### 2.9 Schema ID Entita (stato attuale)

- **Auto-increment** (id\_us, id\_invmat, ecc.) -- **INSTABILE**: cambia tra database diversi
- **Vincoli compositi** (sito+area+us+unita\_tipo) -- **STABILE**: identifica semanticamente il record
- **Campi catalogo** (n\_catalogo\_generale, ecc.) -- **STABILE**: standard ICCD, non sempre compilati
- **UUID persistenti** -- **IMPLEMENTATO**: `entity_uuid` (UUID v4) su tutte le 19 tabelle, auto-generato all'inserimento

---

## 3. Requisiti StratiGraph e Gap Analysis

### Legenda stato

- `[FATTO]` — Funzionalità presente e completa
- `[PARZIALE]` — Base presente, da estendere
- `[DA FARE]` — Non esiste, da implementare
- `[BLOCCATO]` — Dipende da deliverable esterni (WP3/WP4)

### 3.1 Interoperabilità con il Knowledge Graph

> Mappatura semantica: per ogni campo dati di PyArchInit deve esistere corrispondenza con classi/proprietà CIDOC-CRM.

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| Mappatura classi CIDOC-CRM | `[PARZIALE]` | 85% | Presente per US, siti, periodi, reperti. Allineare a specifiche WP3 finali. |
| Mappatura proprietà CIDOC-CRM | `[PARZIALE]` | 80% | Relazioni stratigrafiche mappate. Verificare completezza con WP3. |
| Vocabolari controllati StratiGraph | `[PARZIALE]` | 70% | Vocabolari GNA presenti. Aggiungere vocabolari specifici StratiGraph da WP3. |
| URI persistenti per entità | `[FATTO]` | 90% | UUID v4 stabili su tutte le tabelle. URI costruite via `uuid_manager.build_uri()`. |
| Export JSON-LD conforme | `[PARZIALE]` | 75% | Funziona. Va verificata conformità alle specifiche finali WP3. |
| Export RDF Turtle conforme | `[PARZIALE]` | 75% | Funziona. Va verificata conformità alle specifiche finali WP3. |

**File da modificare**: `modules/s3dgraphy/cidoc_crm_mapper.py`, `modules/gna/gna_vocabulary_mapper.py`
**File da creare**: nessuno (estensione di esistenti)

---

### 3.2 Sistema di Esportazione a Bundle

> Pacchetti strutturati contenenti: dati esportati, manifest, 6 campi metadati obbligatori (BMD).

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| Struttura directory bundle | `[FATTO]` | 100% | data/, metadata/, media/ in bundle\_creator.py |
| Manifest JSON (indice contenuti) | `[FATTO]` | 100% | bundle\_manifest.py con file list + hashes |
| BMD: versione schema | `[FATTO]` | 100% | "1.0-draft" (da aggiornare con spec WP4) |
| BMD: identificativo tool | `[FATTO]` | 100% | "pyarchinit/" + versione da metadata.txt |
| BMD: dati provenienza | `[FATTO]` | 100% | user, organization, created\_at |
| BMD: hash integrità | `[FATTO]` | 100% | SHA-256 su tutti i file del bundle |
| BMD: timestamp esportazione | `[FATTO]` | 100% | ISO 8601 UTC |
| BMD: riferimenti ontologici | `[FATTO]` | 100% | CIDOC-CRM 7.1.2, CRMdig 3.2.2, PyArchInit 1.0 |
| Generazione ZIP bundle | `[FATTO]` | 100% | bundle\_creator.py con struttura completa |
| Versionamento bundle | `[PARZIALE]` | 50% | Schema version presente, versionamento da WP4 |

**File creati**: `modules/stratigraph/bundle_creator.py`, `modules/stratigraph/bundle_manifest.py`
**File da estendere**: `modules/report/validation_tools.py`

---

### 3.3 Validazione Pre-Export

> Verificare metadati obbligatori, file referenziati nel manifest, coerenza ID. Report con warning/errori.

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| Validazione BMD completi | `[FATTO]` | 100% | 6 campi verificati in bundle\_validator.py |
| Validazione file nel manifest | `[FATTO]` | 100% | Esistenza + hash SHA-256 match |
| Coerenza ID/UUID | `[FATTO]` | 100% | Formato, duplicati, mancanti verificati |
| Report warning/errori | `[FATTO]` | 100% | ValidationResult con ERROR/WARNING/INFO |
| Validazione dati archeologici | `[FATTO]` | 90% | Già presente per US, siti, materiali, ecc. |

**File creato**: `modules/stratigraph/bundle_validator.py`
**File da estendere**: `modules/report/validation_tools.py`

---

### 3.4 Architettura Offline-First

> Macchina a 6 stati con feedback visivo. Sincronizzazione automatica via micro-server WP4.

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| Stato 1: cattura/modifica offline | `[FATTO]` | 95% | SQLite locale funziona già offline |
| Stato 2: esportazione locale | `[PARZIALE]` | 40% | Export funzionano, non integrati nella state machine |
| Stato 3: validazione locale | `[PARZIALE]` | 50% | Validazione esiste, non integrata nella state machine |
| Stato 4: coda pronta per sync | `[DA FARE]` | 0% | Tabella `sync_queue` da creare |
| Stato 5: sincronizzato con successo | `[PARZIALE]` | 30% | Sync engine esiste, manca feedback di stato |
| Stato 6: sync fallita + retry | `[DA FARE]` | 0% | Retry con backoff da implementare |
| State machine formale | `[DA FARE]` | 0% | Modulo nuovo |
| Rilevamento connettività | `[DA FARE]` | 0% | Timer Qt periodico |
| Feedback visivo transizioni | `[DA FARE]` | 0% | Widget Qt nel pannello principale |
| Scheduler sync automatica | `[DA FARE]` | 0% | Trigger su ritorno connessione |

**File da creare**: `modules/stratigraph/sync_state_machine.py`, `modules/stratigraph/sync_queue.py`, `modules/stratigraph/connectivity_monitor.py`, `gui/stratigraph_sync_panel.py`
**File da estendere**: `modules/db/database_sync.py` (hook per state machine)

---

### 3.5 Interfaccia di Sincronizzazione con WP4

> Usare interfaccia standard WP4: autenticazione, submit bundle, query stato, recupero errori, retry.

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| Client API StratiGraph | `[DA FARE]` | 0% | `[BLOCCATO]` — API specs da WP4 |
| Autenticazione token-based | `[PARZIALE]` | 40% | JWT già implementato per Unibo. Adattare per StratiGraph. |
| Submit bundle | `[DA FARE]` | 0% | `[BLOCCATO]` — endpoint da WP4 |
| Query stato sync | `[DA FARE]` | 0% | `[BLOCCATO]` — endpoint da WP4 |
| Recupero errori validazione | `[DA FARE]` | 0% | `[BLOCCATO]` — formato errori da WP4 |
| Retry su fallimento | `[DA FARE]` | 0% | Pattern retry con backoff esponenziale |

**File da creare**: `modules/stratigraph/api_client.py`, `modules/stratigraph/auth_stratigraph.py`
**File da estendere**: `modules/storage/credentials.py` (aggiungere tipo `stratigraph`)

---

### 3.6 Stabilità degli Identificatori

> ID stabili tra sessioni e tra export multipli. Merge/update invece di duplicazione.

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| UUID v4 per entità core | `[FATTO]` | 100% | Colonna `entity_uuid` aggiunta a 19 tabelle |
| Generazione UUID automatica | `[FATTO]` | 100% | Auto-generato in entity `__init__` + `uuid_manager.py` |
| Mappatura UUID → URI | `[FATTO]` | 100% | `build_uri()` in uuid\_manager.py |
| Preservazione UUID in sync | `[DA FARE]` | 0% | `database_sync.py` deve preservare UUID |
| Preservazione UUID in export/import | `[DA FARE]` | 0% | Tutti gli export devono includere UUID |
| Migration dati esistenti | `[FATTO]` | 100% | `add_uuid_support.py` integrato nel flusso di connessione |
| Schema SQL aggiornati | `[FATTO]` | 100% | entity\_uuid in schema PostgreSQL, SQLite, views, template DB |

**File creati/modificati**:
- `modules/db/add_uuid_support.py` — migration automatica al primo avvio
- `modules/db/pyarchinit_db_manager.py` — hook UUID nel metodo `connection()`
- `modules/db/entities/*.py` — 19 entità con `entity_uuid=None` + auto-generazione
- `modules/db/structures/*.py` — 19 strutture con colonna `entity_uuid`
- `modules/db/structures_metadata/*.py` — 18 strutture metadata aggiornate
- `resources/dbfiles/pyarchinit_schema_updated.sql` — schema PostgreSQL
- `resources/dbfiles/pyarchinit_schema_clean.sql` — schema PostgreSQL clean
- `resources/dbfiles/pyarchinit_update_postgres.sql` — migration PostgreSQL
- `resources/dbfiles/pyarchinit_update_sqlite.sql` — migration SQLite
- `resources/dbfiles/create_view.sql` — views con entity\_uuid
- `resources/dbfiles/create_view_updated.sql` — views aggiornate
- `resources/dbfiles/pyarchinit.sqlite` — template SQLite
- `resources/dbfiles/pyarchinit_db.sqlite` — DB esempio SQLite

---

### 3.7 Autenticazione e Sicurezza

> Token-based quando connesso + autenticazione locale offline.

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| Auth locale (offline) | `[FATTO]` | 90% | `user_management_dialog.py` + `permission_handler.py` |
| Auth token StratiGraph | `[DA FARE]` | 0% | `[BLOCCATO]` — protocollo auth da WP4 |
| Token storage sicuro | `[PARZIALE]` | 60% | `credentials.py` multi-source. Aggiungere tipo StratiGraph. |
| Token refresh automatico | `[PARZIALE]` | 50% | Pattern JWT refresh esiste in backend Unibo. Riusare. |
| Fallback offline su scadenza token | `[DA FARE]` | 0% | Logica da integrare nella state machine |

**File da creare**: `modules/stratigraph/auth_stratigraph.py`
**File da estendere**: `modules/storage/credentials.py`, `gui/user_management_dialog.py`

---

### 3.8 Integrazione SDK Python WP4

> Librerie Python riusabili per accesso KG, autenticazione, sync, I/O dati.

| Sotto-requisito | Stato | % | Note |
|-----------------|-------|---|------|
| Installazione dipendenze WP4 | `[DA FARE]` | 0% | `[BLOCCATO]` — SDK non ancora rilasciato |
| Wrapper per accesso KG | `[DA FARE]` | 0% | `[BLOCCATO]` — API KG da WP4 |
| Wrapper per auth WP4 | `[DA FARE]` | 0% | `[BLOCCATO]` — protocollo da WP4 |
| Wrapper per sync WP4 | `[DA FARE]` | 0% | `[BLOCCATO]` — interfaccia da WP4 |
| Wrapper per I/O dati WP4 | `[DA FARE]` | 0% | `[BLOCCATO]` — formato da WP4 |

**File da creare**: `modules/stratigraph/wp4_sdk_wrapper.py`
**File da estendere**: `requirements.txt`, `scripts/modules_installer.py`

---

## 4. Piano di Implementazione

### Struttura moduli nuovi

Tutti i nuovi moduli vanno nella directory `modules/stratigraph/`. Questo isola completamente il codice StratiGraph dal core di PyArchInit.

```
modules/stratigraph/
    __init__.py
    bundle_creator.py          # Fase 1 — generazione bundle ZIP
    bundle_manifest.py         # Fase 1 — manifest JSON + BMD
    bundle_validator.py        # Fase 1 — validazione pre-export
    uuid_manager.py            # Fase 1 — gestione UUID entità
    sync_state_machine.py      # Fase 2 — macchina a 6 stati
    sync_queue.py              # Fase 2 — coda operazioni pendenti
    connectivity_monitor.py    # Fase 2 — rilevamento connettività
    api_client.py              # Fase 3 — client API StratiGraph
    auth_stratigraph.py        # Fase 3 — autenticazione token
    wp4_sdk_wrapper.py         # Fase 3 — wrapper SDK WP4

gui/
    stratigraph_sync_panel.py  # Fase 2 — widget stato sync
```

---

### Fase 1 — Fondamenta (M7–M10)

**Obiettivo**: UUID stabili, sistema bundle, validazione pre-export.
**Dipendenze esterne**: Nessuna (lavoro autonomo).

#### Task 1.1 — Aggiungere UUID a tutte le entità

- **Cosa**: Colonna `entity_uuid` (TEXT, UUID v4) in ogni tabella principale
- **Dove**: Migration SQL + modifica strutture e entità
- **Come**:
  1. Migration SQL: `ALTER TABLE <table> ADD COLUMN entity_uuid TEXT;`
  2. Trigger o logica applicativa: generare UUID alla creazione
  3. Script migrazione: generare UUID per record esistenti
  4. Aggiornare `database_sync.py` per preservare UUID
- **Tabelle coinvolte**: `site_table`, `us_table`, `inventario_materiali_table`, `tomba_table`, `periodizzazione_table`, `struttura_table`, `campioni_table`, `individui_table`, `tafonomia_table`, `pottery_table`, `media_table`, `media_thumb_table`, `media_entity_to_table`, `fauna_table`, `ut_table`, `tma_materiali_ripetibili`, `tma_materiali_archeologici`
- **Impatto**: BASSO — aggiunge colonna, non modifica logica esistente
- **Stato**: `[FATTO]` | **95%** (colonne aggiunte a 19 tabelle, migration automatica al primo avvio, schema SQL/SQLite aggiornati, auto-generazione in entity. Manca solo integrazione con database_sync.py per preservazione UUID in sync)

#### Task 1.2 — Modulo UUID Manager

- **Cosa**: Classe per generazione, validazione e gestione UUID
- **Dove**: `modules/stratigraph/uuid_manager.py`
- **Come**:
  1. `generate_uuid()` — genera UUID v4
  2. `ensure_uuid(record)` — assegna UUID se mancante
  3. `build_uri(entity_type, uuid)` — costruisce URI persistente
  4. `validate_uuid(value)` — verifica formato
- **Impatto**: NESSUNO — modulo nuovo
- **Stato**: `[FATTO]` | **100%**

#### Task 1.3 — Bundle Creator

- **Cosa**: Generazione bundle ZIP con struttura directory standardizzata
- **Dove**: `modules/stratigraph/bundle_creator.py`
- **Come**:
  1. Classe `BundleCreator` che raccoglie dati da export esistenti
  2. Crea struttura directory: `data/`, `metadata/`, `manifest.json`
  3. Include export CIDOC-CRM (JSON-LD), GeoPackage, media
  4. Genera hash SHA-256 per ogni file
  5. Crea ZIP finale
- **Usa**: `cidoc_crm_mapper.py`, `gna_exporter.py`, `hashlib`
- **Impatto**: NESSUNO — modulo nuovo che riusa funzioni esistenti
- **Stato**: `[FATTO]` | **100%**

#### Task 1.4 — Bundle Manifest e BMD

- **Cosa**: Generazione manifest JSON con i 6 campi BMD obbligatori
- **Dove**: `modules/stratigraph/bundle_manifest.py`
- **Come**:
  1. Classe `BundleManifest` con i 6 campi BMD:
     - `schema_version`: versione schema bundle (da WP4, default `"1.0"`)
     - `tool_id`: `"pyarchinit"` + versione plugin
     - `provenance`: utente, organizzazione, ruolo, timestamp creazione
     - `integrity_hash`: SHA-256 del contenuto bundle
     - `export_timestamp`: ISO 8601 UTC
     - `ontology_references`: lista URI ontologie usate (CIDOC-CRM, CRMdig, ecc.)
  2. `generate()` — crea manifest completo
  3. `to_json()` — serializza
  4. Lista file inclusi con path relativo e hash individuale
- **Impatto**: NESSUNO — modulo nuovo
- **Stato**: `[FATTO]` | **100%**

#### Task 1.5 — Bundle Validator

- **Cosa**: Validazione pre-export con report warning/errori
- **Dove**: `modules/stratigraph/bundle_validator.py`
- **Come**:
  1. Classe `BundleValidator` con metodi:
     - `validate_bmd()` — verifica 6 campi presenti e validi
     - `validate_files()` — verifica che i file nel manifest esistano
     - `validate_ids()` — verifica coerenza UUID (no mancanti, no duplicati)
     - `validate_ontology_refs()` — verifica URI ontologie risolvibili
     - `validate_data()` — riusa `validation_tools.py` per dati archeologici
  2. Output: lista di `ValidationResult(level, code, message, context)`
  3. Livelli: `ERROR` (blocca export), `WARNING` (segnala, non blocca)
- **Usa**: `modules/report/validation_tools.py`
- **Impatto**: BASSO — estende validazione esistente
- **Stato**: `[FATTO]` | **100%**

---

### Fase 2 — Offline-First (M10–M14)

**Obiettivo**: State machine, coda sync, monitoring connettività, UI feedback.
**Dipendenze esterne**: Specifiche micro-server da WP4 (parziale).

#### Task 2.1 — Sync State Machine

- **Cosa**: Macchina a 6 stati con transizioni e segnali Qt
- **Dove**: `modules/stratigraph/sync_state_machine.py`
- **Come**:
  1. Enum `SyncState`: `OFFLINE_EDITING`, `LOCAL_EXPORT`, `LOCAL_VALIDATION`, `QUEUED_FOR_SYNC`, `SYNC_SUCCESS`, `SYNC_FAILED`
  2. Classe `SyncStateMachine(QObject)` con:
     - `current_state` property
     - `transition(new_state)` con validazione transizioni ammesse
     - Segnale Qt `state_changed(old_state, new_state)`
     - Log transizioni con timestamp
     - Persistenza stato in `QgsSettings`
  3. Transizioni valide:
     - `OFFLINE_EDITING` → `LOCAL_EXPORT`
     - `LOCAL_EXPORT` → `LOCAL_VALIDATION`
     - `LOCAL_VALIDATION` → `QUEUED_FOR_SYNC` | `OFFLINE_EDITING` (se validazione fallisce)
     - `QUEUED_FOR_SYNC` → `SYNC_SUCCESS` | `SYNC_FAILED`
     - `SYNC_FAILED` → `QUEUED_FOR_SYNC` (retry)
     - `SYNC_SUCCESS` → `OFFLINE_EDITING`
- **Impatto**: NESSUNO — modulo nuovo
- **Stato**: `[DA FARE]` | **0%**

#### Task 2.2 — Sync Queue

- **Cosa**: Coda persistente di bundle pronti per la sincronizzazione
- **Dove**: `modules/stratigraph/sync_queue.py`
- **Come**:
  1. Tabella SQLite locale `stratigraph_sync_queue`:
     - `id` INTEGER PK
     - `bundle_path` TEXT — percorso bundle ZIP locale
     - `created_at` TIMESTAMP
     - `status` TEXT — `pending`, `uploading`, `completed`, `failed`
     - `attempts` INTEGER — numero tentativi
     - `last_attempt_at` TIMESTAMP
     - `last_error` TEXT
     - `bundle_hash` TEXT — SHA-256 per verifica integrità
  2. Classe `SyncQueue`:
     - `enqueue(bundle_path)` — aggiunge bundle alla coda
     - `dequeue()` — prende prossimo pending
     - `mark_completed(id)`, `mark_failed(id, error)`
     - `get_pending()` — lista bundle da sincronizzare
     - `retry_failed()` — ri-accoda bundle falliti
     - `cleanup_completed(older_than_days)` — pulizia
- **Impatto**: BASSO — nuova tabella locale, non tocca tabelle esistenti
- **Stato**: `[DA FARE]` | **0%**

#### Task 2.3 — Connectivity Monitor

- **Cosa**: Rilevamento periodico della connessione verso micro-server WP4
- **Dove**: `modules/stratigraph/connectivity_monitor.py`
- **Come**:
  1. Classe `ConnectivityMonitor(QObject)`:
     - Timer Qt con intervallo configurabile (default 30s)
     - Ping verso endpoint health-check micro-server
     - Segnali: `connection_available()`, `connection_lost()`
     - Stato corrente: `is_online` property
     - Debounce: conferma cambio stato dopo N check consecutivi
  2. Usa `NetworkAccessManager` esistente per i check
- **Impatto**: NESSUNO — modulo nuovo
- **Stato**: `[DA FARE]` | **0%**

#### Task 2.4 — Pannello UI Stato Sync

- **Cosa**: Widget Qt integrato nel pannello principale PyArchInit
- **Dove**: `gui/stratigraph_sync_panel.py`
- **Come**:
  1. Classe `StratiGraphSyncPanel(QWidget)`:
     - Indicatore stato corrente (icona + testo)
     - Indicatore connettività (online/offline)
     - Contatore bundle in coda
     - Ultimo sync: timestamp + esito
     - Pulsanti: "Esporta Bundle", "Sincronizza Ora", "Vedi Coda"
     - Log recente transizioni di stato
  2. Connesso a segnali di `SyncStateMachine` e `ConnectivityMonitor`
  3. Integrato come dock widget o tab nel pannello principale
- **Impatto**: BASSO — nuovo widget, non modifica UI esistente
- **Stato**: `[DA FARE]` | **0%**

#### Task 2.5 — Orchestratore Sync Automatica

- **Cosa**: Coordinamento tra state machine, coda, connectivity e sync engine
- **Dove**: `modules/stratigraph/sync_orchestrator.py` (aggiungere a struttura)
- **Come**:
  1. Classe `SyncOrchestrator(QObject)`:
     - Ascolta `connection_available()` dal monitor
     - Quando online: processa coda bundle automaticamente
     - Retry con backoff esponenziale (30s, 1m, 2m, 5m, max 15m)
     - Aggiorna state machine ad ogni transizione
     - Emette segnali per UI
  2. Usa `database_sync.py` esistente come motore di sync
- **Impatto**: BASSO — orchestra moduli esistenti
- **Stato**: `[DA FARE]` | **0%**

---

### Fase 3 — Integrazione WP4 (M12–M16)

**Obiettivo**: Client API, autenticazione StratiGraph, integrazione SDK.
**Dipendenze esterne**: CRITICA — richiede specifiche API e SDK da WP4.

#### Task 3.1 — Client API StratiGraph

- **Cosa**: Client HTTP per interazione con servizi StratiGraph
- **Dove**: `modules/stratigraph/api_client.py`
- **Come**:
  1. Classe `StratiGraphClient`:
     - `authenticate(username, password)` → token
     - `submit_bundle(bundle_path)` → submission_id
     - `get_sync_status(submission_id)` → stato
     - `get_validation_errors(submission_id)` → lista errori
     - `retry_submission(submission_id)` → nuovo tentativo
  2. Basato su `NetworkAccessManager` esistente
  3. Gestione errori HTTP con retry
  4. Configurazione endpoint via `QgsSettings`
- **Dipendenza**: `[BLOCCATO]` fino a specifiche API WP4
- **Impatto**: NESSUNO — modulo nuovo
- **Stato**: `[DA FARE]` | **0%**

#### Task 3.2 — Autenticazione StratiGraph

- **Cosa**: Gestione token StratiGraph con fallback offline
- **Dove**: `modules/stratigraph/auth_stratigraph.py`
- **Come**:
  1. Classe `StratiGraphAuth`:
     - `login(username, password)` → token
     - `refresh_token()` → nuovo token
     - `is_authenticated()` → bool
     - `get_token()` → token corrente (o None se scaduto)
     - Token storage via `credentials.py` esistente
  2. Pattern: riusare logica JWT da `unibo_filemanager_backend.py`
  3. Fallback: se token scaduto e offline, permettere operazioni locali
- **Dipendenza**: `[BLOCCATO]` fino a protocollo auth WP4
- **Impatto**: BASSO — estende `credentials.py`
- **Stato**: `[DA FARE]` | **0%**

#### Task 3.3 — Wrapper SDK WP4

- **Cosa**: Layer di astrazione sopra le librerie Python di WP4
- **Dove**: `modules/stratigraph/wp4_sdk_wrapper.py`
- **Come**:
  1. Import condizionale delle librerie WP4 (graceful degradation se non installate)
  2. Classe `WP4SDKWrapper`:
     - `query_knowledge_graph(sparql)` → risultati
     - `push_to_knowledge_graph(jsonld_data)` → status
     - `resolve_pid(entity_uuid)` → URI/PID esterno
  3. Aggiungere dipendenze WP4 a `requirements.txt`
  4. Gestire installazione via `modules_installer.py`
- **Dipendenza**: `[BLOCCATO]` fino a rilascio SDK WP4
- **Impatto**: BASSO
- **Stato**: `[DA FARE]` | **0%**

#### Task 3.4 — Tab StratiGraph nella UI

- **Cosa**: Sezione dedicata nell'interfaccia per login e configurazione StratiGraph
- **Dove**: `gui/user_management_dialog.py` (estensione) o nuovo tab
- **Come**:
  1. Tab "StratiGraph" con:
     - Campi login (username/password)
     - URL micro-server configurabile
     - Stato connessione e token
     - Pulsante test connessione
  2. Integrato nel dialog user management esistente
- **Dipendenza**: Parzialmente bloccato (UI può essere preparata)
- **Impatto**: BASSO — aggiunge tab a dialog esistente
- **Stato**: `[DA FARE]` | **0%**

---

### Fase 4 — Testing e Raffinamento (M15–M18)

**Obiettivo**: Conformità CIDOC-CRM, performance, documentazione.

#### Task 4.1 — Test Conformità CIDOC-CRM

- **Cosa**: Validatore che verifica export contro ontologia CIDOC-CRM ufficiale
- **Dove**: `modules/stratigraph/cidoc_conformance_test.py`
- **Come**:
  1. Caricare ontologia CIDOC-CRM (RDF/OWL)
  2. Verificare che ogni tripla nell'export usi classi/proprietà valide
  3. Verificare che i range e domain siano rispettati
  4. Report conformità con % di copertura
- **Stato**: `[DA FARE]` | **0%**

#### Task 4.2 — Allineamento Mappatura a Specifiche WP3 Finali

- **Cosa**: Aggiornare `cidoc_crm_mapper.py` alle specifiche definitive WP3
- **Dove**: `modules/s3dgraphy/cidoc_crm_mapper.py`
- **Come**:
  1. Integrare nuove classi/proprietà definite da WP3
  2. Aggiungere vocabolari controllati StratiGraph
  3. Verificare strategia PID definitiva
- **Dipendenza**: `[BLOCCATO]` fino a deliverable finali WP3
- **Stato**: `[DA FARE]` | **0%**

#### Task 4.3 — Ottimizzazione Performance

- **Cosa**: Profiling e ottimizzazione per dataset GIS grandi
- **Dove**: vari file
- **Come**:
  1. Profiling tempi di export bundle per dataset > 10.000 record
  2. Profiling query spaziali
  3. Ottimizzazione batch processing
  4. Il query caching in `pyarchinit_db_manager.py` è già presente — verificare efficacia
- **Stato**: `[DA FARE]` | **0%**

#### Task 4.4 — Documentazione Tecnica

- **Cosa**: Documentare API interne, formato bundle, flusso sync per SRS
- **Dove**: `docs/stratigraph/` (nuova directory)
- **Come**:
  1. Descrizione architettura modulo `stratigraph/`
  2. Schema bundle con esempi
  3. Diagramma state machine
  4. Guida integrazione per sviluppatori WP4
- **Stato**: `[DA FARE]` | **0%**

---

## 5. Dipendenze Esterne

**Da WP3:**

- **Ontologia CIDOC-CRM definitiva** -- Classi, proprieta, regole mappatura.
  Impatto se ritarda: mappatura GIS verso KG incompleta. Task bloccati: 4.2
- **Vocabolari controllati StratiGraph** -- Liste termini standardizzati.
  Impatto se ritarda: vocabolari parziali. Task bloccati: 3.1 (parziale)
- **Strategia PID definitiva** -- Regole per URI persistenti.
  Impatto se ritarda: UUID locali ok, PID esterni no. Task bloccati: 1.2 (parziale)

**Da WP4:**

- **Schema bundle** -- Struttura directory, schema manifest.
  Impatto se ritarda: bundle provvisorio funziona, da adattare. Task bloccati: 1.3, 1.4
- **API sincronizzazione** -- Endpoint, formati request/response.
  Impatto se ritarda: sync impossibile. Task bloccati: 3.1
- **SDK Python** -- Librerie per KG, auth, sync.
  Impatto se ritarda: integrazione impossibile. Task bloccati: 3.3
- **Micro-server specs** -- Configurazione, deployment.
  Impatto se ritarda: monitor connettivita generico ok. Task bloccati: 2.3
- **Protocollo autenticazione** -- OAuth/JWT specs, endpoint.
  Impatto se ritarda: auth locale ok, remota no. Task bloccati: 3.2

### Strategia di mitigazione ritardi

Per i task `[BLOCCATO]`, la strategia è:
1. **Implementare con interfacce astratte**: definire le API interne di PyArchInit come se le specifiche fossero note, usando valori placeholder e interfacce che saranno facilmente adattabili.
2. **Mock dei servizi esterni**: creare mock server per testing locale.
3. **Prioritizzare il lavoro autonomo**: Fase 1 e buona parte di Fase 2 non dipendono da WP3/WP4.

---

## 6. Registro Modifiche

| Data | Autore | Modifica |
|------|--------|----------|
| 2026-02-07 | — | Creazione documento. Analisi stato attuale e gap analysis completata. |
| 2026-02-08 | — | Fase 1: UUID su 19 tabelle, uuid\_manager, bundle\_creator, bundle\_manifest, bundle\_validator. Branch Stratigraph\_00001. |
| 2026-02-08 | — | UUID auto-generazione: entity `__init__` con default `None` + `uuid.uuid4()`. Hook migration in `connection()`. |
| 2026-02-08 | — | Schema SQL: entity\_uuid in schema PostgreSQL, SQLite, views, template DB. Fix nomi tabelle TMA. |
| 2026-02-08 | — | Metadata: versione 5.0.1-alpha, experimental=True. Task 1.5 bundle\_validator completato. |

---

## Riepilogo Percentuali Globali

| Area | Completamento |
|------|--------------|
| Mappatura CIDOC-CRM | 80% |
| Vocabolari controllati | 70% |
| Export semantici (JSON-LD, RDF) | 75% |
| Sistema Bundle | 95% |
| Validazione pre-export bundle | 95% |
| UUID/PID stabili | 85% |
| Offline-first (state machine) | 0% |
| Coda sync + orchestratore | 0% |
| UI pannello sync | 0% |
| Client API StratiGraph | 0% (bloccato) |
| Auth StratiGraph | 0% (bloccato) |
| SDK WP4 | 0% (bloccato) |
| Test conformità CIDOC-CRM | 0% |
| Performance optimization | 0% |
| **MEDIA COMPLESSIVA** | **~42%** |
