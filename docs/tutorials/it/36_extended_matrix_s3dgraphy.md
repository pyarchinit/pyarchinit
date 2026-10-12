# Tutorial 36: Extended Matrix Export e Bridge s3dgraphy

## Introduzione

A partire dalla versione **5.2.0-alpha** PyArchInit integra un **bridge bidirezionale** con la libreria **s3dgraphy** (modello dati Extended Matrix di Emanuel Demetrescu). Il bridge consente di:

- **Esportare** il diagramma stratigrafico come Extended Matrix in **em.json**, il formato che apre EMStudio (il vecchio export GraphML è in pensione)
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

La finestra dice in alto a cosa serve ogni formato. Contiene:

- **Formati**: **DOT (Graphviz) — matrice di Harris** ed **em.json (Extended Matrix, per EMStudio)**, spuntati di partenza, più **Matrice per fasi (analisi cronologica)**, facoltativa. Il GraphML non si esporta più: il JSON di questa finestra **è l'em.json**, lo stesso file che fa il menu **Extended Matrix → Esporta sito in em.json…** — stesso proiettore, stessa simbologia.
- **Opzioni**: **Controlla la sequenza stratigrafica e segnala i problemi**. È l'unica opzione rimasta, ed è davvero letta: togliendo la spunta, il controllo non viene fatto. Le due vecchie caselle che parlavano a yEd (suggerimenti di auto-layout, colori per periodo) sono sparite insieme all'export GraphML.
- **Extended Matrix**: quattro pulsanti accanto all'export — **Apri in EMStudio** e **Vedi la matrice** (si accendono dopo un'esportazione em.json riuscita; il secondo disegna la matrice dentro QGIS, senza EMStudio), **Consegna alla stanza…** e **Apri la stanza**. Sono le stesse voci del menu pyArchInit, a portata di mano.

Premendo **Esporta** viene chiesta la **cartella di destinazione**.

Autori, licenze, embargo e gruppi si gestiscono nella finestra **"Manage paradata"** (§3).

### 2.2.1 Saggi: un grafo solo o uno per saggio

Un gruppo di tre scelte, nella stessa finestra, decide **come dividere
l'em.json** quando lo scavo ha più saggi:

- **Automatico**: un grafo solo se il sito ha un saggio, un grafo per
  saggio se ne ha più. È la scelta di partenza.
- **Un grafo solo per tutto il sito**: tutto lo scavo in un grafo, come
  si è sempre fatto.
- **Un grafo per ogni saggio**: **un file solo**, che porta dentro un
  grafo per ciascun saggio, più uno per le unità che non l'hanno
  compilato. I rapporti che **escono** dal saggio non si perdono:
  restano nel file come collegamenti fra grafi (`graph.links`).

> **EMStudio 1.6.0 ne mostra uno per volta.** Il file è giusto — il
> lettore della libreria rilegge tutti i grafi, senza un avviso — ma
> EMStudio apre il grafo dichiarato `active_graph_id`, cioè il primo
> saggio, e non ha un selettore per gli altri. La matrice dentro QGIS,
> **Mostra matrice**, li unisce tutti e disegna lo scavo intero.
> Misurato il 2026-10-12 sul sito di esempio: 4 grafi (52/49/56/51
> nodi), 32 collegamenti fra saggi, 51 unità nella matrice unita.

Il saggio è il campo **Saggio** della scheda US: le unità che non lo hanno
compilato finiscono in un grafo a parte, dentro lo stesso file.

### 2.3 Click "Esporta"

I file che nascono, secondo i formati spuntati:
- `<sito>.em.json` — Extended Matrix, da aprire in EMStudio o da consegnare alla stanza
- `Extended_Matrix_<sito>[_<area>].dot` — Graphviz DOT, per la matrice di Harris classica
- `Extended_Matrix_<sito>[_<area>]_phased.json` — vista per epoche

> **I luoghi non entrano nell'em.json.** Sito, area e settore restano nella scheda di ogni unità, ma non viaggiano come nodi-gruppo con i loro archi: finché nel file c'è anche un solo arco `is_in_location`, la vista **Matrix** di EMStudio ammucchia tutte le unità nella prima fascia invece di distribuirle per epoca (misurato il 2026-10-08 su EMStudio 1.6.0-dev.26, per bisezione su cinque file). Nessuna informazione si perde: cambia solo il modo di rappresentarla.

Il riepilogo finale elenca i file e, per l'em.json, **quanti nodi e quanti archi** sono usciti, con gli eventuali avvisi.

> **Il GraphML non si esporta più**: la matrice si guarda e si valida in EMStudio, che legge em.json. Le righe temporali (swimlane) del vecchio GraphML sono andate via con lui. Il GraphML resta solo in **entrata**, per i file disegnati in yEd (§5).

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

La dimensione primaria segue un ordine predefinito, con `struttura` al primo posto; `toponym` non è mai primario.

---

## 5. Round-trip (Tab Import)

> **Che cosa si può importare**: la tab Import legge adesso anche **em.json** — quello di EMStudio o del nodo StratiGraph — e sceglie il lettore dall'estensione del file; il `.graphml` di yEd resta accettato per i file di prima. La procedura qui sotto, spostare le US fra i gruppi, riguarda la via yEd/GraphML.

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
| Le righe della swimlane mostrano un testo lunghissimo | Nelle versioni precedenti come etichetta veniva usata la Descrizione della periodizzazione | Aggiorna il plugin e ri-esporta, e/o compila **Datazione estesa** con un nome breve |
| Le epoche della swimlane sono in ordine sbagliato (es. Bronzo sopra il Tardoantico) | Le righe sono ordinate per **Cronologia iniziale**; date a.C. inserite come numeri positivi (1650 invece di -1650) vengono ordinate come d.C. | Nella scheda Periodizzazione inserisci gli anni a.C. come numeri negativi e ri-esporta. Il riepilogo dell'export mostra ora un avviso "⚠️ Periodizzazione: ..." con l'elenco dei periodi da correggere |

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

### 5.8 Aggiornamento 5.8.5-alpha (yed-fastfix)

Pacchetto di correzioni comportamentali sopra `5.8.3-alpha` che alza la qualità del re-export GraphML dopo un import yEd-aware. Modifiche rilevanti per l'utente finale:

- **Paradata multi-folder**: DOC / Combinar / Extractor / property label condivisi fra più folder yEd (es. `material` referenziato da VA01 + VA04 + VA05) generano ora UNA riga in `us_table` PER occorrenza — visibilità multi-folder ripristinata nel GraphML ri-esportato. Trade-off: il dedup per identità (`D.01` / `D.01-2` / `D.01bis` collassati su un'unica riga) non si applica più alla seconda/terza occorrenza.
- **Rapporti reciproci**: ogni edge yEd `a → b` scrive il rapporto diretto sulla riga di `a` E l'inverso sulla riga di `b` (`<<` / "Coperto da" / ecc.). I DOC mostrano ora tutte le connessioni extractor entranti nella Scheda US.
- **Strip del prefisso `us` numerico**: `US100` → `us='100'` `unita_tipo='US'` (prima `us='US100'`). SF/VSF/RSF scritti in dual-write su `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase**: l'appartenenza di una row di TableNode yEd al periodo si propaga a `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserva la distinzione semantica EM 1.5.
- **Re-import idempotente**: ri-eseguire lo stesso import salta le righe già presenti; nessun rollback per collisione UNIQUE alla seconda passata.
- **Palette USV**: i nodi USV sono ora resi col parallelogramma blu canonico EM (prima rettangolo con bordo rosso).

### 5.9 yE-F paradata multi-folder (5.9.0-alpha)

Evoluzione strutturale di `yed-fastfix-5.8.5-alpha`: il trade-off del Bug R B1 (una riga `us_table` per occorrenza, con `us='D.01_2'` / `us='D.01_3'`) è stato superato. Ora una foglia paradata (DOC / Combinar / Extractor / property) condivisa fra più folder yEd produce **una sola riga** in `us_table` per label canonico, e la multi-appartenenza è preservata in un nuovo campo `other_locations`.

Modifiche visibili all'utente finale:

1. **Nuovo widget "Altre attività" nella Scheda US/USM**: nel tab *Periodizzazione* compare un `QListWidget` etichettato "Altre attività" — visibile **solo** quando `unita_tipo` è una tipologia paradata (`DOC`, `Combinar`, `Extractor`, `property`). L'utente può selezionare più codici attività; la selezione viene serializzata come JSON list nella nuova colonna `other_locations`.
2. **Nuova voce di menu QGIS**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Va eseguita **una volta** su ogni DB pre-esistente per aggiungere la nuova colonna (i DB creati post-5.9 hanno già la colonna).
3. **Import yEd-aware migliorato**: una foglia paradata che compare in N folder yEd genera **1 sola** riga `us_table` (non più N righe con suffisso `_2`/`_3` come in 5.8.5). Il primo folder incontrato diventa l'`attivita` primario; i folder secondari vengono elencati in `other_locations`. In **export** vengono emesse N copie visuali yEd (una per folder), tutte condividenti lo stesso `node_uuid` canonico per garantire la round-trip identity.

**Backward compatibility**: i dati prodotti dal Bug R B1 in 5.8.5-alpha (righe con suffisso `_2`/`_3`) restano leggibili senza alcuna conversione automatica. La nuova logica si applica ai nuovi import; le righe legacy continuano a comportarsi come prima.

Predecessore: vedi sezione 5.8 (`yed-fastfix-5.8.5-alpha`) per il comportamento sostituito.

---

## 6. Genera continuità (schede CON)

Nel pannello **"Verifica rapporti"** — disponibile come tab all'interno del dialog di import/export s3dgraphy — è presente il pulsante **"Genera continuità"**. La funzione crea automaticamente, per il sito attualmente selezionato, le **schede di continuità** delle US/USM che attraversano più di un periodo.

### 6.1 Cosa fa

1. Scansiona tutte le US/USM del sito in cui **periodo iniziale ≠ periodo finale** (cioè la cui vita si estende su più periodi).
2. Per ognuna crea o aggiorna una scheda di continuità denominata **`CON_<us>`** (es. `US5` → `CON_US5`).
3. La scheda CON **eredita** dall'unità madre: sito, area (più le aree secondarie), struttura e l'intero arco di periodi (iniziale → finale). La descrizione viene generata automaticamente.
4. Scrive un **rapporto di continuità reciproco** su entrambi i lati: sulla CON e sull'unità madre.

> **La fase, di suo, non conta.** La regola guarda il **periodo**: una USM che va da **2/3 a 2/4** — stesso periodo, cambia solo la fase — non genera niente. Se le tue unità sopravvivono di fase in fase dentro lo stesso periodo, spunta **«anche i salti di fase»** accanto al pulsante: allora contano anche quei salti, purché **entrambe** le fasi siano compilate. Un'unità che non si muove — stesso periodo e stessa fase — non è mai una continuità. La spunta parte **spenta**, e vale per l'anteprima e per la scrittura insieme.

### 6.2 Idempotenza

L'operazione è **idempotente**: rilanciarla non duplica le schede già presenti, ma aggiorna le `CON_<us>` esistenti se i dati dell'unità madre sono cambiati.

### 6.3 Anteprima (dry-run) e backup

Prima di scrivere viene mostrata un'**anteprima dry-run** con i conteggi: quante schede da **creare**, da **aggiornare**, **invariate** e quante **orfane**. Le modifiche vengono applicate **solo dopo conferma** (pulsante "Genera"). Al momento dell'applicazione viene eseguito automaticamente un **backup del database**.

Una scheda CON è **orfana** quando l'unità madre non attraversa più periodi (ad es. periodo iniziale e finale sono stati resi uguali). Di default le orfane vengono solo **segnalate**; una **casella di spunta** ("Rimuovi anche le CON orfane") consente di rimuoverle.

**Una continuità scritta a mano si riconosce.** Una scheda CON che nei suoi rapporti nomina una sola unità — `> 12`, o «Continuità successiva a 12» — è la continuità di quella unità, comunque si chiami: il generatore la **aggiorna** (arco di periodi, etichetta canonica) e il nome resta suo. Non ne nasce una seconda: la continuità è **una per unità**. Se esiste già anche la `CON_<us>` col nome canonico, vince quella e l'altra resta un'orfana da decidere a mano.

### 6.4 In export Extended Matrix

Le schede `CON_<us>` così generate compaiono nell'**em.json** dell'Extended Matrix come **elementi di continuità** (il GraphML in uscita è in pensione, §2.3).

---

## 7. Verifica paradossi temporali (stratigrafici)

Nel pannello **"Verifica rapporti"** (tab del dialog di import/export s3dgraphy), la verifica ora segnala anche i **paradossi temporali**: quando il periodo/fase assegnato a un'unità contraddice la stratigrafia osservata. La stratigrafia è il dato di riferimento, quindi le correzioni automatiche spostano i **periodi**, non i rapporti.

### 7.1 Cosa rileva
- **Inversione temporale**: due unità datate legate da un rapporto d'ordine (es. US5 «copre» US7) in cui l'unità più recente in stratigrafia risulta interamente più **antica** per periodo.
- **Contemporaneità incoerente**: unità dichiarate contemporanee (uguaglianza fisica / legame) ma con intervalli cronologici **disgiunti**.
- **Non valutabile**: rapporto d'ordine in cui almeno una delle due unità non ha un periodo databile (solo segnalato, nessuna correzione).

Nota sul confine: due periodi **adiacenti che si toccano** in un solo punto cronologico sono considerati sovrapposti → **non** sono un paradosso (beneficio del dubbio).

### 7.2 Correzione automatica e suggerimenti
- Quando un solo spostamento risolve il conflitto, la verifica propone di spostare l'unità **mono-periodo** in conflitto con la maggioranza dei vicini, scegliendo il periodo a spostamento minimo; per le contemporaneità con un'unità non databile copia il periodo del vicino datato.
- Nei casi ambigui — pareggio, unità **multi-periodo** (es. schede CON), nessun periodo valido — non corregge automaticamente: fornisce un **suggerimento «cosa + come»** (es. «Sposta US5 a un periodo ≥ 3, oppure US7 a un periodo ≤ 1, oppure verifica il rapporto»).

### 7.3 Anteprima e backup
- L'**anteprima** mostra le modifiche di periodo proposte prima di applicarle.
- Prima di scrivere i periodi viene eseguito un **auto-backup del database** (SQLite e PostgreSQL).
- Dopo l'applicazione, rilancia la verifica per controllare eventuali paradossi residui.

---

## 8. Verifica della cronologia (periodizzazione e schede)

Nello stesso pannello **"Verifica rapporti"** (tab del dialog di import/export s3dgraphy), dalla versione 5.13.64-alpha, la verifica trova e corregge anche i problemi di **cronologia** del sito selezionato. Il controllo dei paradossi temporali (sezione 7) confronta il periodo di un'unità con la stratigrafia; questo confronta la periodizzazione con se stessa e con le schede US che la copiano.

### 8.1 Cosa rileva

L'albero del pannello raggruppa i problemi per tipo. Accanto ai gruppi dei rapporti compaiono quattro gruppi nuovi:

| Gruppo | Che cosa segnala | Come viene trattato |
|--------|------------------|---------------------|
| **Fasi con intervalli sovrapposti** | Due righe della periodizzazione i cui intervalli di anni si intersecano | Manuale: il pannello propone di restringere gli intervalli solo se, dopo la restrizione, resta un intervallo utilizzabile |
| **Datazione della scheda disallineata** | Il campo `datazione` della scheda US dice una cosa diversa dalla `datazione_estesa` della sua periodizzazione | Automatico: la periodizzazione è la fonte, la scheda è la copia, quindi la copia viene riscritta dalla fonte. Un campo vuoto si compila allo stesso modo. Una US senza periodo viene saltata, perché non c'è nulla da cui copiare |
| **Periodizzazione con inizio dopo la fine** | `cron_iniziale` maggiore di `cron_finale` | Manuale: sono probabili date a.C. senza il segno meno — il pannello propone di riscrivere i due anni negativi (`-1650` invece di `1650`); se invece è un refuso, scambia i due valori a mano |
| **Fase senza anni** | Una fase i cui anni mancano o non sono leggibili | Solo segnalata: non c'è nulla da cui ereditarli |

Un esempio per le sovrapposizioni. Nel database di esempio ce ne sono due, e nessuna delle due ha una proposta: le due fasi hanno intervalli **identici**, e qualunque restrizione farebbe finire una fase prima del suo inizio. Il pannello si limita a dirlo; la decisione (accorpare le fasi, correggere gli anni, lasciare le cose come stanno) spetta all'archeologo.

### 8.2 Correzione automatica e suggerimenti

**Correzioni automatiche e proposte.** Le correzioni automatiche sono **già spuntate**; le proposte **non lo sono** e vengono applicate solo se si spunta la casella. Prima la regola era diversa: un problema la cui correzione richiedeva una decisione umana poteva solo essere letto. Ora ha una casella, lasciata vuota. Questo vale anche per le due categorie più vecchie dei rapporti che offrono un suggerimento, cioè la contraddizione diretta e il ciclo stratigrafico.

Per usare il pannello:

1. Selezionare nel pannello il **sito** da verificare. La verifica è **per sito**: guarda solo il sito scelto e corregge solo quello. In un database con dieci siti la cosa conta, perché gli stessi numeri di US esistono in tutti.
2. Leggere la **riga di riepilogo** sopra l'albero: dice quanti problemi ci sono, quanti sono correggibili in automatico e **quante sono le proposte da spuntare a mano**.
3. Aprire i gruppi e selezionare un problema per leggerne il dettaglio nel pannello di anteprima.
4. Controllare le caselle. Le correzioni automatiche sono già spuntate: togliere la spunta a quelle che non si vogliono applicare. Spuntare le proposte che si condividono.
5. Applicare le correzioni. Prima di scrivere qualsiasi cosa viene creato un **backup automatico** (copia del file SQLite oppure `pg_dump` per PostgreSQL in `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); il backup, che già esisteva per le correzioni dei campi periodo, ora copre anche quelle cronologiche.
6. Se il risultato non convince, premere **Annulla ultimo fix**: l'annullamento riporta indietro anche le correzioni scritte nella tabella della periodizzazione.

### 8.3 Anteprima e backup

**L'anteprima mostra la data calcolata.** Per ogni unità citata da un problema il pannello di anteprima riporta la sua data calcolata, in una riga come questa:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

La riga dice, nell'ordine, l'intervallo di anni, la regola che lo ha prodotto e il rapporto lungo il quale il vincolo è arrivato, con il nodo da cui proviene. Quando i due estremi dell'intervallo arrivano da strade diverse, ciascuno è etichettato (`inizio …` e `fine …`), così una data non viene mai attribuita al rapporto sbagliato. Oggi, in un database normale, ogni unità prende le sue date dal proprio periodo: la maggior parte delle righe dirà quindi `epoca`. Il senso della riga non è sorprendere, è permettere di vedere **da dove viene** una data.

---

## 9. Come leggere gli archi della matrice

Nel disegno della matrice alcune scelte possono sembrare strane, ma non sono errori:

- **Una freccia non passa mai sotto a un nodo.** Quando la colonna d'arrivo è occupata, la freccia entra nella casella **dal fianco**: è normale.
- **L'uguaglianza non è una sovrapposizione.** Un rapporto «Uguale a» o «Si lega a» mette le due unità sulla **stessa riga**, accostate, collegate da **due linee orizzontali** (il segno di uguale) **senza punta di freccia**.
- **Gli archi ridondanti non si disegnano.** Se la US 1 copre la 2 e la 2 copre la 3, la freccia da 1 a 3 non compare, perché non aggiunge niente. Dentro un **ciclo** invece gli archi restano tutti, perché un ciclo è un errore da vedere.
- **Le linee dicono che rapporto sono.** Grigia e piena: la sequenza (copre, riempie, si appoggia). **Punteggiata verde**: un taglio (`Taglia` / `Tagliato da`), qualunque sia la definizione stratigrafica e in qualunque lingua. **Spessa e nera**: la continuità — un rombo piccolo e nero, senza nome sopra (il nome compare passando col mouse), nella colonna della sua unità, così la linea è dritta. **Rossa**: una freccia che risale le fasce, cioè una contraddizione fra stratigrafia e cronologia; un taglio che risale è rosso **e** resta punteggiato.
- **I paradati non sono mai una linea piena.** Prendono colore e tratto dalle regole dell'Extended Matrix (`em_visual_rules.json`): bruno-rosso punteggiato «estratto da», arancio tratteggiato «provenienza del dato», oro tratteggiato «proprietà», grigio tratteggiato «connessione generica», rosso-pomodoro tratteggiato «combina» (nel file sarebbe pieno: è l'unica deroga, perché un arco verso un documento non deve sembrare una sovrapposizione).
- **Il bordo bruno è una muratura.** Le USM — WSU, MSE, UEM, USZ, ΤΣΜ nelle altre lingue — hanno la stessa casella delle US, con il bordo bruno invece che rosso.

---

## 10. Narrativa con l'AI

Dalla versione **5.13.106-alpha** il pannello della matrice dentro QGIS (§2.2, «Vedi la matrice») ha due schede nella colonna di destra: **Unità** (*Units*) — la scheda dell'unità scelta, lo zoom sulla geometria e i media, come prima — e **Narrativa** (*Narrative*), nuova. La scheda Narrativa fa scrivere a un'AI la **storia del sito**, un capitolo per ogni epoca, e poi te la fa leggere, convalidare da una persona ed esportare in HTML o DOCX. Legge e scrive **lo stesso em.json** che apre EMStudio, nel formato della libreria s3dgraphy: la narrativa che vedi qui è quella che EMStudio mostra nella sua scheda *Narrative*.

> **Nessuna impostazione nuova.** La scheda non ha una finestra di configurazione: usa l'AI che hai già impostato altrove in pyArchInit (§10.2).

> **L'AI scrive bozze, non testi definitivi.** Ogni paragrafo scritto dal modello resta «bozza AI» finché una persona non lo convalida (§10.6), e nei documenti esportati porta il segno ⚠.

I nomi delle schede e dei pulsanti della scheda Narrativa esistono in italiano e in inglese: **sono in italiano se QGIS è in italiano, in inglese con qualsiasi altra lingua**. Qui trovi sempre tutti e due. Le voci di menu e le finestre di dialogo del plugin (come «Vedi la matrice…» o i tre bottoni di §10.9) sono invece solo in italiano.

### 10.1 Aprire la scheda Narrativa

1. Apri il menu **Plugins → pyArchInit - Archaeological GIS Tools** e scegli la voce **Extended Matrix → Vedi la matrice…**
2. Scegli il **sito**.
3. Se il sito ha dei **saggi**, pyArchInit chiede «Il sito ha N saggi. Come divido il file?» con due risposte: «Un grafo per ogni saggio (…)», proposta di partenza, oppure «Un grafo solo per tutto il sito». È la stessa scelta di §2.2.1 e della voce «Esporta sito in em.json…»: le due voci scrivono lo **stesso file**, con la stessa forma.
4. pyArchInit esporta il sito dal database in `<home>/pyarchinit_EM_folder/<sito>.em.json` — `<home>` è `~/pyarchinit_5`, o la cartella indicata dalla variabile d'ambiente `PYARCHINIT_HOME` — e apre il pannello **«Matrice — `<sito>`»**, agganciato a destra della finestra di QGIS. Il nome del file è quello del sito, con i caratteri speciali sostituiti da «_» (ad esempio «Scavo 1» diventa `Scavo_1.em.json`).
5. Nella colonna di destra del pannello clicca la scheda **Narrativa**.

<!-- IMMAGINE: Screenshot del menu Plugins → pyArchInit - Archaeological GIS Tools con la voce «Extended Matrix → Vedi la matrice…» -->
![Menu Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figura 1: La voce «Extended Matrix → Vedi la matrice…» nel menu del plugin*

<!-- IMMAGINE: Screenshot della domanda sui saggi con le due risposte -->
![Domanda sui saggi](images/36_extended_matrix_s3dgraphy/02_domanda_saggi.png)
*Figura 2: La domanda sui saggi: un grafo per ogni saggio o un grafo solo*

<!-- IMMAGINE: Screenshot del pannello della matrice agganciato a destra, con le schede Unità e Narrativa -->
![Pannello con due schede](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figura 3: Il pannello della matrice con le schede Unità e Narrativa*

Il file è **uno per sito e resta sul disco**: non sta più in una cartella temporanea. È il file che apre EMStudio ed è lì che la narrativa viene scritta. Ogni volta che scegli «Vedi la matrice…» il sito viene **esportato di nuovo dal database** e il file viene riscritto; la narrativa già presente si conserva (§10.8).

Alla scheda si arriva anche da altre due parti:

- dalla voce **Extended Matrix → Esporta sito in em.json…**, che alla fine offre il bottone «Narrativa con l'AI» (§10.9);
- dal pulsante **Vedi la matrice** della finestra «Esporta Extended Matrix» della scheda US (§2.2): apre lo stesso pannello sul file appena esportato, nella cartella che hai scelto.

### 10.2 Quale AI viene usata

In alto, nella scheda Narrativa, una riga dice quale AI userà: **«Modello: `<modello>` (`<da dove>`)»**, seguita dal promemoria su EMStudio. Se non ne trova nessuna scrive **«Nessuna AI impostata: impostala nella scheda US con «Report» (Provider AI) o con «Query AI Database».»** e i pulsanti **Genera con l'AI** e **Rigenera capitolo** restano spenti.

La scheda legge le impostazioni AI **già salvate** dalle altre finestre di pyArchInit, in quest'ordine, e usa la **prima** che ha un modello e — per i provider in rete — la chiave API:

| # | Dove è impostata | Come la chiama la scheda (it / en) |
|---|------------------|-------------------------------------|
| 1 | Scheda US, pulsante «Report» → finestra «Generatore di Report», gruppo «Provider AI» | Generatore di Report della scheda US / Report generator of the US form |
| 2 | Scheda US, pulsante «Query AI Database» | Query AI Database / Query AI Database |
| 3 | Finestra palimpsestr, pulsante «Report AI (analisi descrittiva)…», selettore «Provider AI» | Relazione Palimpsest / Palimpsest report |
| 4 | Finestra «Generazione SQL con AI» (testo in SQL: vedi il tutorial 30) | Testo in SQL / Text to SQL |

I provider sono quelli dei selettori «Provider AI»: **OpenAI** e **Anthropic (Claude)** in rete, con la chiave API da scrivere nel campo «API key»; **Ollama** e **LM Studio** sul tuo computer, senza chiave. Il selettore salva la scelta appena la cambi. Se vuoi un altro modello, cambialo nella finestra che la scheda indica tra parentesi (o in una che viene prima nell'elenco). La scheda rilegge le impostazioni **quando il pannello si apre**: dopo averle cambiate, riapri la matrice.

### 10.3 La scheda Narrativa

```
┌─ Unità ─┬─ Narrativa ────────────────────────────────────────────┐
│ Modello: <modello> (<da dove>) · Se EMStudio ha il file          │
│ aperto, chiudilo prima: chi scrive per ultimo vince.             │
├──────────────────────────────────────────────────────────────────┤
│ Presentazione — da scrivere                                      │
│ Inizi XV secolo — bozza AI                                       │
│ XV secolo — convalidato                                          │
│ Età moderna — bozza AI, troncato                                 │
├──────────────────────────────────────────────────────────────────┤
│ Il testo del capitolo scelto, con le unità citate per nome.      │
├──────────────────────────────────────────────────────────────────┤
│ Capitolo 3 di 9 · XV secolo  *                                   │
│ [Genera con l'AI]  [Rigenera capitolo]  [Convalida…]             │
│ [Prepara i capitoli]  [Esporta…]  [Apri in EMStudio]  [Annulla]* │
└──────────────────────────────────────────────────────────────────┘
```

\* La riga di avanzamento e il pulsante «Annulla» si vedono solo mentre l'AI sta scrivendo. In questo schema le righe dell'elenco sono quelle del sito di esempio.

<!-- IMMAGINE: Screenshot della scheda Narrativa con l'elenco dei capitoli, il testo del capitolo scelto e i sei pulsanti -->
![Scheda Narrativa](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figura 4: La scheda Narrativa*

Dall'alto in basso:

- **la riga di stato**: il modello in uso (§10.2) e il promemoria *«Se EMStudio ha il file aperto, chiudilo prima: chi scrive per ultimo vince.»*;
- **l'elenco dei capitoli**, una riga per capitolo: *Titolo — stato*. Con l'esportazione per saggi (§2.2.1) ogni saggio ha la sua narrativa e ogni riga è preceduta dal nome del saggio tra parentesi quadre, ad esempio `[Saggio A] XV secolo — bozza AI`;
- **il testo del capitolo scelto**: la prosa, con le unità citate per nome. Se il capitolo non ha ancora prosa vedi il suo segnaposto «[da scrivere: …]»;
- **la riga di avanzamento**, solo durante la generazione: «Capitolo 3 di 9 · XV secolo»;
- **i pulsanti**, in due righe.

L'esito di ogni operazione compare nella barra dei messaggi di QGIS, con il titolo «Narrativa».

Quando il file **non ha ancora una narrativa** l'elenco è vuoto e un testo dice: *«Nessuna narrativa nel file: “Prepara i capitoli” crea lo scheletro (N capitoli fra epoche e attività), “Genera con l'AI” lo scrive.»*

#### Gli stati di un capitolo

| Stato (it / en) | Che cosa significa |
|-----------------|--------------------|
| **da scrivere** / to be written | Il capitolo ha solo il segnaposto «[da scrivere: …]». |
| **bozza AI** / AI draft | C'è prosa scritta dal modello che nessuna persona ha convalidato. Basta un paragrafo: se il capitolo ne ha anche solo uno non convalidato, lo stato è questo, anche se c'è altra prosa. |
| **convalidato** / endorsed | Tutta la prosa dell'AI è stata convalidata da una persona. |
| **scritto** / written | Prosa scritta da una persona (in EMStudio). |
| **troncato** / truncated | Si aggiunge allo stato (ad esempio «bozza AI, troncato»): il modello si è fermato perché ha raggiunto il limite di lunghezza, e il testo finisce a metà. |

#### I pulsanti

| Pulsante (it) | In inglese | Che cosa fa |
|---------------|------------|-------------|
| **Genera con l'AI** | Generate with AI | Scrive, **uno alla volta**, tutti i capitoli di epoca (e di attività) ancora «da scrivere»; quelli già scritti non si toccano. Se la narrativa non c'è, crea prima lo scheletro. Mostra l'avanzamento e il pulsante **Annulla**. Acceso solo con un file aperto e un'AI impostata. |
| **Rigenera capitolo** | Regenerate chapter | Riscrive **il capitolo scelto** nell'elenco (con più saggi, solo quello del saggio scelto): la bozza AI non convalidata viene sostituita — ma solo quando il modello ha risposto: se la chiamata fallisce, la bozza di prima resta — e i blocchi già convalidati restano. Si accende scegliendo un capitolo di epoca o di attività, con un'AI impostata; per «Presentazione» e «Dove si trova» resta spento. |
| **Convalida…** | Endorse… | Apre un menu con «Questo capitolo» e «Tutti i capitoli», poi chiede chi convalida (§10.6). Acceso quando c'è una narrativa. |
| **Prepara i capitoli** | Prepare the chapters | Crea **solo lo scheletro** dei capitoli, senza AI: serve anche se non c'è nessuna AI impostata, per scrivere a mano in EMStudio. Non tocca la prosa già scritta e aggiunge i capitoli delle epoche nuove. Esito: «Capitoli preparati: N.» |
| **Esporta…** | Export… | Salva la narrativa in HTML o DOCX (§10.7). Acceso quando c'è una narrativa. |
| **Apri in EMStudio** | Open in EMStudio | Apre l'em.json in EMStudio. Se EMStudio non c'è, la barra dei messaggi rimanda alla voce di menu **Extended Matrix → Installa EMStudio…** |
| **Annulla** | Cancel | Compare solo durante la generazione: l'AI si ferma **dopo il capitolo in corso** e quanto è stato scritto viene salvato. |

Durante la generazione tutti i pulsanti sono spenti tranne **Annulla**.

### 10.4 Che cosa scrive l'AI

**Quali capitoli.** Lo scheletro è quello della libreria s3dgraphy (il modello «site_story»):

- **Presentazione** e **Dove si trova** sono capitoli canonici: restano segnaposto «[da scrivere: …]» da scrivere a mano in EMStudio, perché nel grafo non c'è niente da cui scriverli senza inventare. «Dove si trova» esiste solo se il grafo porta una posizione geografica. L'AI non li genera.
- **Un capitolo per ogni epoca** (periodo/fase) che ha unità, dalla più antica alla più recente. Il titolo è il nome dell'epoca, cioè la «Datazione estesa» della periodizzazione; se manca, ne esce un nome generico come «Period 8 Phase 1»: compilala nella scheda Periodizzazione per avere titoli leggibili. Un'unità compare nel capitolo dell'epoca in cui nasce e in quelli delle epoche in cui sopravvive.
- **Un capitolo per ogni attività**, se il grafo contiene gruppi di attività. Un sito esportato dal database di norma non ne ha — il campo Attività della scheda US viaggia come proprietà dell'unità — e allora i capitoli sono quelli di epoca.

**Che cosa riceve il modello.** Per ogni capitolo un *briefing* con, per ciascuna unità: nome, tipo e descrizione; i campi compilati della scheda US (definizione stratigrafica e interpretativa, interpretazione, periodo e fase, datazione, attività, struttura, saggio, ambiente, settore, area); le epoche; **i rapporti stratigrafici** con le altre unità (copre, taglia, riempie, si appoggia, uguale a…) con i nomi; e, se ci sono, le fonti documentarie collegate. Le unità sono elencate **dalla più antica alla più recente**, seguendo i rapporti. Oltre **80 unità** per capitolo il briefing si taglia alle prime 80. Ha anche un tetto di lunghezza (circa 25.000 caratteri): oltre, si accorciano i testi lunghi delle schede, si tolgono i rapporti ripetuti e le catene di prova e, se ancora non basta, si omettono le unità più recenti. In entrambi i casi il modello è informato di quante unità mancano.

**Le regole.** Il modello riceve le cinque regole della libreria: scrivere solo ciò che il contesto sostiene (niente date, materiali, funzioni o eventi inventati); mantenere l'incertezza (un'unità virtuale è un'ipotesi, non un fatto); non citare fonti che non ci sono; scrivere prosa continua, senza elenchi né titoli; dire apertamente che il contesto è troppo povero, quando lo è. Chiede da uno a tre paragrafi.

**La lingua.** La prosa è nella **lingua della narrativa**, che si fissa quando nasce lo scheletro: **italiano se in quel momento QGIS è in italiano, inglese con qualsiasi altra lingua** (il modello riceve le istruzioni soltanto in queste due lingue). Una narrativa già creata tiene la sua lingua anche se poi cambi quella di QGIS. Lo stesso vale per i titoli dei capitoli canonici e per i segnaposto.

**Come viene salvata.** Nel formato della libreria, lo stesso che legge EMStudio: un nodo narrativa (`NarrativeNode`) con i capitoli; ogni paragrafo scritto dal modello è un blocco «bozza AI» attribuito all'**autore AI** di quel modello; il **prompt** usato è registrato come estrattore collegato alle fonti, così si può risalire a che cosa è stato chiesto. Le unità citate nel testo sono **menzioni** (`[[nome]]`): nel file restano legate al nodo dell'unità, e nella scheda e negli export compaiono con il suo nome. Una menzione che non corrisponde a nessuna unità del grafo viene ridotta a semplici parole, senza parentesi.

**Costi e tempi.** Il modello viene chiamato **una volta per capitolo**. Con un provider in rete ogni chiamata ha un costo e un tempo di attesa (nelle prove con un modello in rete, qualche decina di secondi per capitolo: un sito con una decina di epoche richiede alcuni minuti); con Ollama o LM Studio non si paga nulla, ma i tempi dipendono dal computer.

### 10.5 Passo per passo

1. Apri la matrice del sito (§10.1) e clicca la scheda **Narrativa**. Controlla in alto **quale modello** userà.
2. **Chiudi EMStudio** se ha il file aperto: pyArchInit e EMStudio scrivono lo stesso file e chi scrive per ultimo vince.
3. Facoltativo: **Prepara i capitoli** per vedere lo scheletro, senza AI.
4. Clicca **Genera con l'AI**. Guarda l'avanzamento («Capitolo 3 di 9 · …»); puoi continuare a usare QGIS. Alla fine la barra dei messaggi dice, ad esempio, *«7 capitoli generati, 1 falliti: Età moderna — …»* (con *«(interrotto)»* se hai annullato) e l'elenco si ricarica: i capitoli scritti sono «bozza AI».
5. **Leggi**: scegli un capitolo dopo l'altro e leggi il testo sotto l'elenco. Controllalo sulla stratigrafia: è una bozza costruita dai dati della scheda.
6. Se un capitolo non convince, scegli la sua riga e clicca **Rigenera capitolo**. La nuova bozza **sostituisce** quella precedente non convalidata: se vuoi conservare la versione di prima, esportala prima. Se un capitolo è «troncato», rigeneralo **prima** di convalidare.
7. Quando un capitolo è a posto, clicca **Convalida…** (§10.6).
8. **Esporta…** in HTML o DOCX (§10.7), oppure **Apri in EMStudio** per scrivere a mano «Presentazione» e «Dove si trova» e rifinire il resto.
9. In seguito puoi riaprire la matrice: la narrativa resta (§10.8).

<!-- IMMAGINE: Screenshot della generazione in corso: riga di avanzamento «Capitolo 3 di 9 · …» e pulsante Annulla -->
![Generazione in corso](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figura 5: Generazione in corso, con l'avanzamento e il pulsante Annulla*

Un capitolo che fallisce non ferma gli altri: il riepilogo dice quali. Per riprovare basta un altro clic su **Genera con l'AI**, che scrive solo i capitoli ancora «da scrivere».

### 10.6 Convalidare: chi firma

Convalidare vuol dire che una **persona** si assume la responsabilità del testo scritto dal modello. Non avviene mai da solo: né generando, né salvando.

1. Clicca **Convalida…**. Si apre un piccolo menu: **«Questo capitolo»** — acceso solo se il capitolo scelto è in «bozza AI» — oppure **«Tutti i capitoli»**, cioè tutte le bozze AI non ancora convalidate, in tutti i grafi del file.
2. Una finestra chiede **«Chi convalida? Scegli un autore o scrivi un nome nuovo.»** L'elenco contiene gli **autori umani già nel grafo** — le persone nominate nella scheda US come schedatore, direttore US e responsabile US — e puoi scrivere un nome nuovo, che diventa un nuovo autore del grafo (con più saggi, in ogni grafo che ha bozze da firmare).
3. La barra dei messaggi dice **«N blocchi convalidati da `<nome>`.»**, oppure «Niente da convalidare.» Il file viene salvato.

<!-- IMMAGINE: Screenshot del menu Convalida… («Questo capitolo» / «Tutti i capitoli») e della finestra con la scelta dell'autore -->
![Convalida](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figura 6: Convalida: il menu e la scelta dell'autore*

I blocchi passano da «bozza AI» a «convalidato». Nel documento esportato la persona compare tra i responsabili («a cura di») e il modello come assistente («con l'assistenza di»), e i paragrafi convalidati non portano più il segno ⚠. Rigenerare non cancella i blocchi convalidati: la firma è un atto, non si perde riscrivendo.

### 10.7 Esportare in HTML o DOCX

Clicca **Esporta…**: si apre la finestra di salvataggio con due formati, «Pagina HTML (\*.html)» e «Documento Word (\*.docx)». Il nome proposto è `<sito>_narrativa.html`, nella cartella dell'em.json; se scrivi tu l'estensione (`.html` o `.docx`) vale quella, altrimenti decide il formato scelto. Con l'esportazione per saggi si scrive **un file per saggio**, aggiungendo il nome del saggio al nome scelto. La barra dei messaggi conferma: «Narrativa esportata in `<percorso>`».

Il documento contiene:

- il titolo della narrativa (ad esempio «Scavo archeologico — la storia del sito»), i responsabili («a cura di») e il modello come assistente («con l'assistenza di»);
- per ogni capitolo la prosa, con le unità citate col loro nome, e l'elenco delle unità del capitolo;
- in fondo la sezione **Fonti**: i documenti su cui si appoggia il racconto e la voce «Prompt», che richiama il prompt registrato nel file.

Alcune cose da sapere:

- le **bozze non convalidate entrano**, ciascuna preceduta da «⚠︎ non validato da una persona», e l'intestazione dice quanti blocchi sono in questo stato. Per un documento senza segni, convalida prima (§10.6);
- entrano **tutti i capitoli**, anche quelli ancora «da scrivere»: il loro segnaposto «[da scrivere: …]» resta nel testo;
- le figure che un autore ha previsto in EMStudio (ad esempio la matrice di un'epoca) non vengono disegnate dall'esportazione di pyArchInit: nel documento resta un segnaposto;
- l'HTML è un file solo e autosufficiente; il DOCX si apre con Word o LibreOffice e richiede il pacchetto `python-docx`, fra i requisiti del plugin.

<!-- IMMAGINE: Screenshot del documento HTML esportato: un capitolo con una bozza preceduta da «⚠︎ non validato da una persona» -->
![Documento HTML esportato](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figura 7: Il documento HTML esportato, con una bozza non convalidata segnata*

### 10.8 Riesportare il sito: la narrativa resta

Riesportare il sito dal database — con **Vedi la matrice…**, con **Esporta sito in em.json…** o con la finestra «Esporta Extended Matrix» della scheda US — **conserva la narrativa** già presente nel file di destinazione: prosa, convalide, autore AI e prompt. Le epoche nate nel frattempo ricevono un capitolo «da scrivere». Un avviso lo dice: **«Narrativa conservata dal file precedente (N capitoli).»** Lo vedi nella barra dei messaggi con «Vedi la matrice…», nel riepilogo della finestra «Esporta Extended Matrix» e, con «Esporta sito in em.json…», nei dettagli della finestra finale.

Le **altre modifiche** fatte al file in EMStudio — posizioni dei nodi, descrizioni riscritte — **non sopravvivono**, come prima: il file si rigenera dal database. Si conserva soltanto la narrativa.

Prima di riscrivere un file che porta una narrativa, pyArchInit ne fa una **copia di sicurezza** accanto: `<sito>.em.json.bak` (a ogni riesportazione sostituisce la copia precedente).

Se cambi la forma del file — passi da «Un grafo per ogni saggio» a «Un grafo solo per tutto il sito», o viceversa — i grafi cambiano nome e la narrativa **non può passare** nel file nuovo. Un avviso lo dice: *«La narrativa del file precedente (grafi: …) non è passata nel file nuovo (grafi: …): la forma del file è cambiata. Copia di sicurezza in …»*. Il testo non è perso: sta nella copia `.bak`, che però viene sostituita alla prossima riesportazione di un file con una narrativa — mettila al sicuro. Per recuperarlo rinomina la copia in `.em.json` e riesporta con la scelta di prima.

Se il file precedente non si legge (ad esempio un file rimasto a metà), l'esportazione va avanti lo stesso: il file illeggibile viene **rinominato** `<sito>.em.json.broken` e un avviso dice *«Il file precedente non si legge (…): la narrativa, se c'era, non è stata conservata.»*

> **La narrativa non è nel database di pyArchInit: vive solo nell'em.json.** Il backup del database non la copia. Copia ogni tanto la cartella `pyarchinit_EM_folder`.

### 10.9 Dalla voce «Esporta sito in em.json…»

La voce **Extended Matrix → Esporta sito in em.json…** fa la stessa domanda sui saggi e scrive lo stesso file `<sito>.em.json` in `pyarchinit_EM_folder`. Alla fine mostra «Esportato `<percorso>`», con i conti di nodi, archi e avvisi (il testo degli avvisi è nei dettagli della finestra), e **tre bottoni**:

| Bottone | Che cosa fa |
|---------|-------------|
| **Apri in EMStudio** | Apre il file in EMStudio; se non è installato, offre di installarlo. |
| **Narrativa con l'AI** | Compare **solo se un'AI è impostata** (§10.2): apre il pannello della matrice già sulla scheda Narrativa. |
| **Chiudi** | Chiude la finestra. |

<!-- IMMAGINE: Screenshot della finestra finale di «Esporta sito in em.json…» con i tre bottoni -->
![Esporta sito in em.json: tre bottoni](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figura 8: La finestra finale di «Esporta sito in em.json…»*

### 10.10 Avvertenze

- **Chiudi EMStudio prima di generare o convalidare.** Se EMStudio ha il file aperto, chi scrive per ultimo vince. Con più saggi, EMStudio mostra un grafo alla volta (nota di §2.2.1): la scheda Narrativa li mostra tutti.
- **Un'AI scrive solo da quello che trova nel grafo, e può sbagliare.** Le regole la tengono a freno, non la rendono infallibile: leggi ogni capitolo prima di convalidarlo.
- **Con un provider in rete i dati escono dal computer.** Il briefing di ogni capitolo (nomi, definizioni, descrizioni e rapporti delle unità) viene inviato al servizio scelto; con Ollama o LM Studio resta in locale.
- **Il file si scrive alla fine.** La generazione salva quando termina, anche se l'hai annullata: non chiudere QGIS mentre l'AI sta scrivendo. Il salvataggio è sicuro: il file viene scritto accanto, riletto e solo allora sostituisce il vero; se qualcosa va storto, **il file precedente resta com'era**.
- **Non riaprire la matrice mentre l'AI scrive.** La scheda resta sul file di prima e avvisa: *«Generazione in corso: aspetta che finisca, o premi Annulla, prima di cambiare file.»*
- **Il testo si modifica in EMStudio**, non in pyArchInit.
- La narrativa e i nodi che la reggono (autore AI, prompt) **non compaiono nel disegno della matrice**.

### 10.11 Risoluzione dei problemi

| Messaggio (it / en) | Causa | Rimedio |
|---------------------|-------|---------|
| «Nessuna AI impostata…» / “No AI configured…” | Nessuna delle quattro finestre di §10.2 ha un modello (e, per OpenAI e Anthropic, la chiave API). | Imposta provider e modello — e la chiave — in una di quelle finestre, poi **riapri la matrice**: la scheda rilegge le impostazioni solo all'apertura. Anche senza AI puoi preparare i capitoli, convalidare, esportare e aprire EMStudio. |
| «Nessuna narrativa nel file…» / “No narrative in the file…” | Il file non ha ancora una narrativa (è normale la prima volta). | Clicca **Prepara i capitoli** (scheletro) o **Genera con l'AI** (scheletro e prosa). Il numero N conta i capitoli di epoca e di attività che lo scheletro avrà (un'epoca senza unità non ne ha); il messaggio «Capitoli preparati» conta anche «Presentazione» ed, eventualmente, «Dove si trova». |
| «EMStudio non risulta installato…» / “EMStudio is not installed…” | Il programma non è stato trovato sul computer. | Usa la voce di menu **Extended Matrix → Installa EMStudio…** (la voce ha questo nome con qualsiasi lingua di QGIS). |
| «troncato» / “truncated” accanto allo stato | Il modello si è fermato al limite di lunghezza e il testo finisce a metà. | Prima di convalidare, **Rigenera capitolo**; se si ripete, completa il capitolo in EMStudio. |
| «N capitoli generati, M falliti: `<titolo>` — `<motivo>`» / “N chapters generated, M failed: …” | Il fornitore ha rifiutato la richiesta (chiave non valida, quota, modello non disponibile) o il server locale non risponde. «il modello non ha scritto niente» vuol dire che la risposta era vuota. | Rimuovi la causa e clicca di nuovo **Genera con l'AI**: scrive solo i capitoli rimasti «da scrivere». |
| «Il file precedente non si legge (…)» / “The previous file cannot be read (…)” | Alla riesportazione il file esistente non era un em.json leggibile. | L'esportazione è andata avanti: il file illeggibile è stato conservato accanto come `….broken` e la narrativa che conteneva, se c'era, non è passata nel file nuovo. Se ti serve, recuperala da quel file o da una copia di sicurezza. |
| «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» / “The previous file's narrative (graphs: …) did not travel into the new file…” | Hai cambiato la forma del file (un grafo per saggio ↔ un grafo solo): i grafi hanno nomi diversi e la narrativa non può passare. | Il file di prima è nella copia `.bak`: rinominala in `.em.json` e riesporta con la scelta di prima. |
| «Non sono riuscito a scrivere … Il file precedente è intatto.» / “Could not write … The previous file is intact.” | Il salvataggio è fallito (disco pieno, file bloccato, permessi). | Rimedia e ripeti: i capitoli generati in quella sessione non erano stati salvati. |
| «DocX export needs python-docx — install the extra: …» (sempre in inglese) | Il pacchetto `python-docx` non è installato nel Python di QGIS: serve solo per il DOCX. | Installa `python-docx` (è fra i requisiti del plugin), oppure esporta in HTML, che non richiede niente. |

---

## Riferimenti

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
