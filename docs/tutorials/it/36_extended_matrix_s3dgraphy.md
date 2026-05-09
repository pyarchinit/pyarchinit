# Tutorial 36: Extended Matrix Export e Bridge s3dgraphy

## Introduzione

A partire dalla versione **5.2.0-alpha** PyArchInit integra un **bridge bidirezionale** con la libreria **s3dgraphy** (modello dati Extended Matrix di Emanuel Demetrescu). Il bridge consente di:

- **Esportare** il diagramma stratigrafico come Extended Matrix in GraphML (con swimlane temporali, transitive reduction, edge styling EM 1.5)
- **Reimportare** modifiche fatte in yEd (movimenti di US tra periodi/gruppi) aggiornando il database SQL pyarchinit
- **Allegare paradata** (Author / License / Embargo) a livello sito
- **Raggruppare** US per dimensione (struttura, area, attivita, settore, ambient, saggio, quad_par o gruppi ad-hoc)

Tag corrente: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

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
- **"Select Output Directory"**: cartella di destinazione

### 2.3 Limite single-dimension (5.5.2-alpha)

Se spunti **2 o più** checkbox di raggruppamento, appare un warning:

> *"Multi-dim export non ancora supportato. Procedi con SOLO la prima dimensione selezionata?"*

Scegli **Sì** (esporta con la prima checkbox spuntata) o **Annulla** (modifica selezione). L'annidamento gerarchico (struttura > attività > US) sarà disponibile con AI08-F1.

### 2.4 Click "Export"

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

## 4. Stile visivo per dimensione (5.5.1-alpha)

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

L'alpha 50% lascia visibili le swimlane delle epoche dietro al rettangolo del gruppo.

---

## 5. Round-trip (Tab Import)

Per modificare il database SQL spostando US tra gruppi nel GraphML:

1. Apri il GraphML in **yEd**
2. Trascina una US in un altro gruppo, salva
3. Torna al dialog → tab **"Import"**
4. **Spunta** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Carica il GraphML modificato

Il sistema esegue una transazione atomica: se qualcosa fallisce, **rollback completo** (il DB resta invariato). I gruppi `adhoc` non scrivono mai SQL — aggiornano solo `groups_<sito>.graphml`.

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
| Folder gruppo vuoto in yEd | Stai spuntando 2+ dimensioni (limite 5.5.2-alpha) | Spunta una sola dimensione, riprova |
| "i campi rapporti devono essere TESTO" | Hai inserito un numero come integer | I campi US/Area sono **TEXT**, non integer |
| Capitalizzazione errata sui rapporti | "copre" minuscolo nel DB | Usa "Copre", "Coperto da" capitalizzati |

---

## 8. Documentazione tecnica

Per approfondimenti su architettura, decisioni di design e roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over deferiti:
- **AI07**: migrazione `LocationNodeGroup` (deadline upstream 2026-05-23)
- **AI08-F1**: hierarchical nesting (per multi-dim export pulito)
- **AI08-F3**: auto-layout heuristics (bin-packing dei sub-gruppi)
- **AI09**: TimeBranchNodeGroup mapping
- **Phase 3**: SyncEngine + REST API
- **Phase 4**: GraphDBBackend + SPARQL

---

## Riferimenti

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
