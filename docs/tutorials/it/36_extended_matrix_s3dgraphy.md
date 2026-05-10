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

## Riferimenti

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
