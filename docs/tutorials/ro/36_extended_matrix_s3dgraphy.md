# Tutorial 36: Export Extended Matrix și Bridge s3dgraphy

## Introducere

Începând cu versiunea **5.2.0-alpha** PyArchInit integrează un **bridge bidirecțional** cu biblioteca **s3dgraphy** (modelul de date Extended Matrix al lui Emanuel Demetrescu). Bridge-ul permite:

- **Exportarea** diagramei stratigrafice ca Extended Matrix în GraphML (cu swimlanes temporale, reducere tranzitivă, edge styling EM 1.5)
- **Re-importul** modificărilor făcute în yEd (mutarea UE între perioade/grupuri) actualizând baza de date SQL
- **Atașarea paradatelor** (Author / License / Embargo) la nivelul sitului
- **Gruparea** UE după dimensiune (struttura, area, attivita, settore, ambient, saggio, quad_par sau grupuri ad-hoc)

Tag curent: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

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
- **Combobox dimensiune primară** (implicit `struttura`): când o UE are apartenențe pe 2+ dimensiuni, dimensiunea primară câștigă ca folder yEd vizibil (parent ierarhic). Celelalte dimensiuni apar ca insigne inline sub nodul UE. `toponym` nu este niciodată primar, indiferent de selecție.
- **"Select Output Directory"**: folderul destinație

Începând cu 5.6.0-alpha poți bifa **2+ dimensiuni**: exportul funcționează nativ datorită modelului m:n cu `is_primary` (vezi secțiunea "Apartenență multidimensională").

### 2.3 Click pe "Export"

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

## 4. Stil vizual per dimensiune (5.5.1-alpha + 5.6.0-alpha)

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

Începând cu 5.6.0-alpha, elementele `LocationNodeGroup` se disting prin `kind`:

| `kind` | Fill (50% transparență) | Border |
|---|---|---|
| `toponym` | lavandă pastel `#E6E6FA80` | `#9370DB` |
| `study` | fildeș pastel `#FFFFE080` | `#888888` |
| `functional` | cyan pastel `#E0FFFF80` | `#008B8B` |

Alpha 50% lasă vizibile swimlane-urile epocilor în spatele dreptunghiului grupului.

### 4.1 Lanț toponim (5.6.0-alpha)

Câmpurile `site_table.{nazione, regione, provincia, comune}` sunt emise automat ca un lanț recursiv de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Nivelurile administrative goale sunt sărite fără a întrerupe lanțul. O deduplicare cross-sit garantează că aceeași `comune` prezentă în 2 situri devine **un singur nod partajat** în GraphML.

---

## 4.2 Apartenență multidimensională (5.6.0-alpha)

Începând cu 5.6.0-alpha o UE poate aparține **mai multor dimensiuni simultan** datorită modelului m:n cu flag-ul `is_primary`. Doar dimensiunea primară devine folderul yEd vizibil; celelalte apar ca **insigne inline** sub nodul UE și ca JSON în `<data key="s3d:other_locations">` pentru tool-urile downstream.

Exemplu: o UE cu `struttura=basilica` și `area=B` (primar `struttura`) produce:
- folder yEd "struttura: basilica" ca parent vizibil;
- sub nodul UE, o insignă inline `also: B (study), TestCity (toponym)`;
- în GraphML, atributul `s3d:other_locations` cu array JSON al apartenențelor secundare.

Dimensiunea primară se controlează prin combobox în §2.2.

---

## 5. Round-trip (tab Import)

Pentru a modifica baza SQL mutând UE între grupuri în GraphML:

1. Deschide GraphML în **yEd**
2. Trage o UE într-un alt grup, salvează
3. Înapoi la dialog → tab **"Import"**
4. **Bifează** checkbox-ul *"Update SQL on import (struttura/area/...)"*
5. Încarcă GraphML modificat

Sistemul rulează o tranzacție atomică: la eșec, **rollback complet** (DB rămâne nealterată). Grupurile `adhoc` nu scriu niciodată SQL — actualizează doar `groups_<sit>.graphml`.

Începând cu 5.6.0-alpha walker-ul de import este **recursiv** și suportă foldere imbricate (de ex. lanț toponim `nazione > regione > provincia > comune > UE`). La detectarea ciclurilor în graful folderelor, este ridicată excepția `CycleDetectedError` și importul este abandonat cu rollback.

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
| "rapporti trebuie să fie TEXT" | Ai introdus un număr ca integer | Câmpurile UE/Area sunt **TEXT**, nu integer |
| Capitalizare greșită în rapporti | "copre" cu litere mici în DB | Folosește "Copre", "Coperto da" capitalizate |
| `DeprecationWarning` pe fișier 5.5.x | Fișier legacy `ActivityNodeGroup + group_kind` | Projector-ul îl promovează în memorie la `LocationNodeGroup`. Reexportă pentru a migra fișierul pe disc. |

---

## 8. Documentație tehnică

Pentru aprofundare arhitectură, decizii de design și roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over amânate:
- **AI08-F3**: euristici auto-layout (bin-packing sub-grupuri) — încă amânat
- **AI09**: TimeBranchNodeGroup mapping — viitor
- **Phase 3**: SyncEngine + REST API — viitor
- **Phase 4**: GraphDBBackend + SPARQL — viitor

Livrate:
- **AI07** (5.6.0-alpha, 2026-05-10): migrare `LocationNodeGroup` cu enum `kind` + lanț toponim + apartenențe multidimensionale
- **AI08-F1** (fuzionat în AI07): nesting ierarhic nativ via `is_primary`

---

## Referințe

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
