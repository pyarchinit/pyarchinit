# Tutorial 36: Export Extended Matrix și Bridge s3dgraphy

## Introducere

Începând cu versiunea **5.2.0-alpha** PyArchInit integrează un **bridge bidirecțional** cu biblioteca **s3dgraphy** (modelul de date Extended Matrix al lui Emanuel Demetrescu). Bridge-ul permite:

- **Exportarea** diagramei stratigrafice ca Extended Matrix în GraphML (cu swimlanes temporale, reducere tranzitivă, edge styling EM 1.5)
- **Re-importul** modificărilor făcute în yEd (mutarea UE între perioade/grupuri) actualizând baza de date SQL
- **Atașarea paradatelor** (Author / License / Embargo) la nivelul sitului
- **Gruparea** UE după dimensiune (struttura, area, attivita, settore, ambient, saggio, quad_par sau grupuri ad-hoc)

Tag curent: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

---

## 1. Cerințe

- Bază de date SQLite (PostgreSQL încă nesuportată)
- **Migrarea Phase 1 node_uuid** aplicată automat la deschiderea bazei
- **yEd Graph Editor** pentru vizualizarea ieșirii (https://www.yworks.com/products/yed)

> ⚠️ Pentru baze pre-5.2.0-alpha migrarea poate necesita repornirea QGIS.

---

## 2. Export Extended Matrix (butonul verde)

### 2.1 Deschiderea dialogului

1. Deschide **Fișa UE** a sitului dorit
2. Click pe butonul verde **"Esporta Extended Matrix"** (sub tab-ul Rapporti)

### 2.2 Tab "Export"

Dialogul afișează:

- **Output formats**: bifează DOT / GraphML / JSON / phased JSON (recomandat: GraphML)
- **Group US by (optional)**: 7 checkbox-uri pentru dimensiuni + 1 "ad-hoc"
  - Dimensiunile populate în DB sunt **bifate automat** la deschidere
- **"Select Output Directory"**: folderul destinație

### 2.3 Limită single-dimension (5.5.2-alpha)

Dacă bifezi **2 sau mai multe** checkbox-uri de grupare, apare un avertisment:

> *"Export multi-dim încă nesuportat. Continuă cu DOAR prima dimensiune selectată?"*

Alege **Da** (exportă cu prima dimensiune bifată) sau **Anulează** (modifică selecția). Nesting-ul ierarhic (struttura > attivita > UE) sosește cu AI08-F1.

### 2.4 Click pe "Export"

Se generează 4 fișiere cu prefixul `Extended_Matrix_<sit>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix pentru yEd (țintă principală)
- `_s3dgraphy.json` — format nativ s3dgraphy
- `_phased.json` — vizualizare per epocă

---

## 3. Dialog "Manage paradata" (4 tab-uri)

### 3.1 Acces
Click pe butonul **"Manage paradata"** în fișa UE (lângă butonul verde Export).

### 3.2 Cele 4 tab-uri

| Tab | Conținut | Fișier generat |
|---|---|---|
| **Authors** | Adaugă autori (nume + ORCID + rol) | `paradata_<sit>.graphml` |
| **Licenses** | Licență dataset (ex. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Date embargo + motiv | idem |
| **Groups** | Grupuri ad-hoc (nume + selecție UE membre) | `groups_<sit>.graphml` |

Fișierele se salvează lângă DB SQLite și sunt **versionabile în Git**.

---

## 4. Stil vizual per dimensiune (5.5.1-alpha)

Fiecare dimensiune de grupare are o culoare distinctivă în GraphML:

| Dimensiune | Fill (50% transparență) | Border |
|---|---|---|
| `area` | roz pastel `#FFE0E680` | `#C84A5F` |
| `struttura` | portocaliu pastel `#FFE6CC80` | `#C66B33` |
| `attivita` | galben pastel `#FFF5CC80` | `#A89A33` |
| `settore` | verde pastel `#E6FFCC80` | `#6BC633` |
| `ambient` | aqua pastel `#CCFFE680` | `#33A86B` |
| `saggio` | azur pastel `#CCF5FF80` | `#3389A8` |
| `quad_par` | violet pastel `#E0CCFF80` | `#6633C6` |
| `adhoc` | gri pastel `#F5F5F580` | `#666666` |

Alpha 50% lasă vizibile swimlane-urile epocilor în spatele dreptunghiului grupului.

---

## 5. Round-trip (tab Import)

Pentru a modifica baza SQL mutând UE între grupuri în GraphML:

1. Deschide GraphML în **yEd**
2. Trage o UE într-un alt grup, salvează
3. Înapoi la dialog → tab **"Import"**
4. **Bifează** checkbox-ul *"Update SQL on import (struttura/area/...)"*
5. Încarcă GraphML modificat

Sistemul rulează o tranzacție atomică: la eșec, **rollback complet** (DB rămâne nealterată). Grupurile `adhoc` nu scriu niciodată SQL — actualizează doar `groups_<sit>.graphml`.

---

## 6. CLI (alternativă la dialog)

Pentru scripts / batch:

```bash
# Export
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Listează grupuri ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Adaugă autor
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = succes, 1 = eroare bridge, 2 = eroare argparse.

---

## 7. Rezolvarea problemelor

| Simptom | Cauză | Soluție |
|---|---|---|
| "no such column: node_uuid" | Migrarea Phase 1 neexecutată | Repornește QGIS, redeschide DB |
| GraphML gol | DB fără rapporti / filtru area prea strict | Verifică us_table.rapporti |
| Folder grup gol în yEd | Bifezi 2+ dimensiuni (limită 5.5.2-alpha) | Bifează doar una, reîncearcă |
| "rapporti trebuie să fie TEXT" | Ai introdus un număr ca integer | Câmpurile UE/Area sunt **TEXT**, nu integer |
| Capitalizare greșită în rapporti | "copre" cu litere mici în DB | Folosește "Copre", "Coperto da" capitalizate |

---

## 8. Documentație tehnică

Pentru aprofundare arhitectură, decizii de design și roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over amânate:
- **AI07**: migrare `LocationNodeGroup` (deadline upstream 2026-05-23)
- **AI08-F1**: nesting ierarhic (pentru multi-dim export curat)
- **AI08-F3**: euristici auto-layout (bin-packing sub-grupuri)
- **AI09**: TimeBranchNodeGroup mapping
- **Phase 3**: SyncEngine + REST API
- **Phase 4**: GraphDBBackend + SPARQL

---

## Referințe

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
