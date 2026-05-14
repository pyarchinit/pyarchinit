# Tutorial 36: Extended Matrix Export e Bridge s3dgraphy

## Introduzione

A partire dalla versione **5.2.0-alpha** PyArchInit integra un **bridge bidirezionale** con la libreria **s3dgraphy** (modello dati Extended Matrix di Emanuel Demetrescu). Il bridge consente di:

- **Esportare** il diagramma stratigrafico come Extended Matrix in GraphML (con swimlane temporali, transitive reduction, edge styling EM 1.5)
- **Reimportare** modifiche fatte in yEd (movimenti di US tra periodi/gruppi) aggiornando il database SQL pyarchinit
- **Allegare paradata** (Author / License / Embargo) a livello sito
- **Raggruppare** US per dimensione (struttura, area, attivita, settore, ambient, saggio, quad_par o gruppi ad-hoc)

Tag corrente: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Prerequisiti

- Database SQLite (PostgreSQL non ancora supportato)
- Migrazione **Phase 1 node_uuid** applicata automaticamente all'apertura del DB
- **yEd Graph Editor** per visualizzare l'output (https://www.yworks.com/products/yed)

> ⚠️ Per DB pre-5.2.0-alpha la migrazione potrebbe richiedere riavvio di QGIS.

---

## 2. Esporta Extended Matrix (pulsante verde)

### 2.1 Aprire il dialog

1. Apri la **Scheda US** del sito desiderato
2. Click sul pulsante verde **"Esporta Extended Matrix"** (sotto la tab Rapporti)

### 2.2 Tab "Export"

Il dialog mostra:

- **Output formats**: spunta DOT / GraphML / JSON / phased JSON (raccomandato: GraphML)
- **Group US by (optional)**: 7 checkbox per le dimensioni di raggruppamento + 1 checkbox "ad-hoc"
  - Le dimensioni con valori popolati nel DB vengono **auto-spuntate** all'apertura
- **Combobox dimensione primaria** (default `struttura`): quando una US ha membership su 2+ dimensioni, la dimensione primaria vince come folder yEd visibile (parent gerarchico). Le altre dimensioni appaiono come badge inline sotto il nodo US. `toponym` non è mai primario, indipendentemente dalla scelta.
- **"Select Output Directory"**: cartella di destinazione

Da 5.6.0-alpha è possibile spuntare **2+ dimensioni**: l'export funziona nativamente grazie al modello m:n con `is_primary` (vedi sez. "Membership multidimensionale").

### 2.3 Click "Export"

Vengono generati 4 file con prefisso `Extended_Matrix_<sito>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix per yEd (nostro target principale)
- `_s3dgraphy.json` — formato nativo s3dgraphy
- `_phased.json` — vista per epoche

---

## 3. Dialog "Manage paradata" (4 tab)

### 3.1 Accesso
Click sul pulsante **"Manage paradata"** nella scheda US (vicino al pulsante verde Export).

### 3.2 I 4 tab

| Tab | Contenuto | File generato |
|---|---|---|
| **Authors** | Aggiungi autori (nome + ORCID + ruolo) | `paradata_<sito>.graphml` |
| **Licenses** | Licenza dataset (es. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Date di embargo + motivazione | idem |
| **Groups** | Gruppi ad-hoc (nome + selezione US membri) | `groups_<sito>.graphml` |

I file vengono salvati accanto al DB SQLite e sono **versionabili in Git**.

---

## 4. Stile visivo per dimensione (5.5.1-alpha + 5.6.0-alpha)

Ogni dimensione di raggruppamento ha un colore distintivo nel GraphML:

| Dimensione | Fill (50% trasparenza) | Border |
|---|---|---|
| `area` | rosa pastello `#FFE0E680` | `#C84A5F` |
| `struttura` | arancio pastello `#FFE6CC80` | `#C66B33` |
| `attivita` | giallo pastello `#FFF5CC80` | `#A89A33` |
| `settore` | verde pastello `#E6FFCC80` | `#6BC633` |
| `ambient` | acqua pastello `#CCFFE680` | `#33A86B` |
| `saggio` | azzurro pastello `#CCF5FF80` | `#3389A8` |
| `quad_par` | viola pastello `#E0CCFF80` | `#6633C6` |
| `adhoc` | grigio pastello `#F5F5F580` | `#666666` |

A partire da 5.6.0-alpha, i `LocationNodeGroup` sono distinti per `kind`:

| `kind` | Fill (50% trasparenza) | Border |
|---|---|---|
| `toponym` | lavanda pastello `#E6E6FA80` | `#9370DB` |
| `study` | avorio pastello `#FFFFE080` | `#888888` |
| `functional` | ciano pastello `#E0FFFF80` | `#008B8B` |

L'alpha 50% lascia visibili le swimlane delle epoche dietro al rettangolo del gruppo.

### 4.1 Catena toponym (5.6.0-alpha)

I campi `site_table.{nazione, regione, provincia, comune}` vengono emessi automaticamente come catena ricorsiva di `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). I livelli amministrativi vuoti vengono saltati senza interrompere la catena. Un dedupe cross-sito garantisce che lo stesso comune presente in 2 siti diventi **un solo nodo condiviso** nel GraphML.

---

## 4.2 Membership multidimensionale (5.6.0-alpha)

Da 5.6.0-alpha una US può appartenere a **più dimensioni contemporaneamente** grazie al modello m:n con flag `is_primary`. Solo la dimensione primaria diventa il folder yEd visibile; le altre appaiono come **badge inline** sotto il nodo US e come JSON in `<data key="s3d:other_locations">` per i tool downstream.

Esempio: una US con `struttura=basilica` e `area=B` (con `struttura` primario) avrà:
- folder yEd "struttura: basilica" come parent visibile;
- sotto il nodo US, un badge inline `also: B (study), TestCity (toponym)`;
- nel GraphML, l'attributo `s3d:other_locations` con array JSON delle membership secondarie.

La dimensione primaria si controlla via combobox in §2.2.

---

## 5. Round-trip (Tab Import)

Per modificare il database SQL spostando US tra gruppi nel GraphML:

1. Apri il GraphML in **yEd**
2. Trascina una US in un altro gruppo, salva
3. Torna al dialog → tab **"Import"**
4. **Spunta** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Carica il GraphML modificato

Il sistema esegue una transazione atomica: se qualcosa fallisce, **rollback completo** (il DB resta invariato). I gruppi `adhoc` non scrivono mai SQL — aggiornano solo `groups_<sito>.graphml`.

Da 5.6.0-alpha il walker di import è **ricorsivo** e supporta folder annidati (es. catena toponym `nazione > regione > provincia > comune > US`). In presenza di cicli nel grafo dei folder viene sollevata l'eccezione `CycleDetectedError` e l'import viene abortito con rollback.

---

## 6. CLI (alternativa al dialog)

Per script / batch:

```bash
# Esporta
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <nome> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Lista gruppi ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <nome>

# Aggiungi autore
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <nome> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = success, 1 = errore di bridge, 2 = errore argparse.

---

## 7. Risoluzione dei problemi

| Sintomo | Causa | Soluzione |
|---|---|---|
| "no such column: node_uuid" | Migrazione Phase 1 non eseguita | Riavvia QGIS, riapri il DB |
| GraphML vuoto | DB privo di rapporti / area filter troppo stretto | Verifica us_table.rapporti popolato |
| "i campi rapporti devono essere TESTO" | Hai inserito un numero come integer | I campi US/Area sono **TEXT**, non integer |
| Capitalizzazione errata sui rapporti | "copre" minuscolo nel DB | Usa "Copre", "Coperto da" capitalizzati |
| `DeprecationWarning` su file 5.5.x | File legacy `ActivityNodeGroup + group_kind` | Il projector promuove in-memory a `LocationNodeGroup`. Ri-esporta per migrare il file su disco. |

---

## 8. Documentazione tecnica

Per approfondimenti su architettura, decisioni di design e roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over deferiti:
- **AI08-F3**: auto-layout heuristics (bin-packing dei sub-gruppi) — ancora differito
- **AI09**: TimeBranchNodeGroup mapping — futuro
- **Phase 3**: SyncEngine + REST API — futuro
- **Phase 4**: GraphDBBackend + SPARQL — futuro

Completati:
- **AI07** (5.6.0-alpha, 2026-05-10): migrazione `LocationNodeGroup` con `kind` enum + catena toponym + multi-dim memberships
- **AI08-F1** (fuso in AI07): hierarchical nesting nativo grazie a `is_primary`

---

## 5. yEd-aware Import — importare graphml editati esternamente (5.8.x)

A partire dalla **5.8.0-alpha** il bridge è **bidirezionale anche per graphml authored direttamente in yEd** (cioè senza prima passare da un export pyarchinit). Pyarchinit riconosce automaticamente i graphml "yEd-raw" — quelli che non hanno le data keys `pyarchinit.*` — e li importa con un dispatch dedicato che mappa node-label-prefix → tipo stratigrafico, riconosce TableNode-rows come periodi, walka i group folder come dimensioni archeologiche, e sceglie una policy per le edge che toccano folder.

### 5.1 Rollout in 6 milestone

| Milestone | Tag | Cosa aggiunge |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — `ClassificationKind` enum 13 valori (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive `^USVs|^USV|^USM|^US|^VSF|^RSF|^SF|^D\.|^C\.|property-keywords` |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate da TableNode rows) + `yed_group_walker.py` (FolderCandidate con auto-dimension da prefisso label: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orchestrator `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + `_DryRunRollback` sentinel + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` 5 pagine (classifier / periods / folders / policy / preview) + `YedOverrides` dataclass + sidecar `<graphml>.yed_overrides.json` persistence |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Questa documentazione + dev-log + CHANGELOG. |

### 5.2 Come funziona — flow utente

1. **Apri un graphml in QGIS via menu Import GraphML** (stesso path del flusso pyarchinit-projected esistente).
2. Pyarchinit rileva automaticamente che è yEd-raw (no `pyarchinit.*` keys) → dispatcha al nuovo branch invece di passare al legacy.
3. Si apre il wizard `YedImportDialog` con **5 pagine**:
   - **1/5 Classifier** — tabella con 1 riga per leaf node. Per ogni riga vedi `label` + `auto_kind` (es. `us_real` / `usv_virtual` / `property`) + combobox `user_kind` per override. Bottone **Accetta auto** azzera gli override (ritorna a `auto_kind` per ogni riga).
   - **2/5 Periods** — 1 riga per TableNode-row trovata, colonne editable `periodo` + `fase`. Le date (`datazione_iniziale`/`finale`) restano vuote: yEd-raw graphml non porta date.
   - **3/5 Folders** — 1 riga per group folder. Combobox per `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` per escludere). `value` editabile (default = `auto_value` derivato dal prefisso label).
   - **4/5 Rapporti policy** — 4 radio button per scegliere come trattare le edge che toccano folder:
     - **SKIP** (default): scarta le edge folder-touching. Le edge leaf-to-leaf passano intatte.
     - **FAN_OUT**: edge `folder_A → folder_B` espande in `N×M` leaf pairs (cartesian product dei membri).
     - **REPRESENTATIVE**: usa il primo membro del folder come proxy.
     - **SYNTHETIC**: crea 1 us_table row per folder (`unita_tipo='VA'` virtual activity) + rewire edge attraverso questi anchor.
   - **5/5 Preview** — dry-run di `import_yed_raw(overrides=..., dry_run=True)`. Mostra counts (us / inv / period / paradata) **senza committare**. Click **Finish** committa, **Cancel** abbandona.
4. Su **Finish** il wizard salva i tuoi override nel **sidecar JSON** `<graphml>.yed_overrides.json` accanto al file. Riaprire lo stesso graphml fa preload del sidecar → vedi i tuoi override pre-applicati.

### 5.3 Routing destinazioni

Il dispatch usa `_classify_destination` (in `yed_import_pipeline.py`) per smistare ogni leaf:

| ClassificationKind | Destinazione | Note |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | da label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | da `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | da `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | da `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` dal prefisso del label: USVs/USVn/USVc) | da `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | da `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | da `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | da `^VSF\d+` |
| DOCUMENT | `paradata` | da `^D\.\d+` |
| COMBINER | `paradata` | da `^C\.\d+` |
| PROPERTY | `paradata` | label keyword (`material`/`position`/`width`/...) |

**Decisione utente 2026-05-13**: USV* (virtuali) sono "unità tipo" e vanno in `us_table`, non in paradata. Solo DOC/COMB/PROP/VIRTUAL_FIND restano paradata.

### 5.4 Sidecar JSON — formato

Schema versionato per garantire forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/path/assoluto/al/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Solo i campi MODIFICATI dall'utente vengono salvati (diff). `ClassificationKind` values sconosciuti (es. da future s3dgraphy releases) sono skippati silently al load.

### 5.5 CLI per ingest scripted

Per CI / re-run batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` per backend SQLite vs PostgreSQL. `--overrides` è opzionale (no overrides = defaults yE-D). `--auto-defaults` è no-op forward-compat.

### 5.6 Limiti noti

- **No editing date in wizard**: yEd-raw graphml non porta `datazione_iniziale`/`datazione_finale`. La pagina Periods edita solo `periodo` + `fase` (gli FK target).
- **ParadataStore API parziale**: i metodi `add_virtual_us`/`add_document`/`add_combiner`/`add_property` non sono ancora implementati upstream. yE-D logga "skip — method missing" per ogni paradata leaf ma conta gli attempt nel preview.
- **PropertyNode → Path B (no US linkage)**: i nodi PROPERTY vengono scritti senza target US. Il wizard avvisa con warning. Futuro: yE-Closure follow-up per aggiungere "assign target" nell'interfaccia.
- **Multi-DB**: il sidecar JSON è per-graphml, non per-DB. Se importi lo stesso graphml in DB diversi, il sidecar contiene gli override applicabili a entrambi.

### 5.7 Test coverage finale

| Suite | Test | Coverage |
|---|---|---|
| yE-A | `test_yed_detector.py` | flavor detection |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | PeriodCandidate + FolderCandidate parse |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | policies + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | sidecar persistence + CLI |

**Suite totale post-rollout**: 354 passed / 42 skipped (PG-L1 require psycopg2).

---

## Riferimenti

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
