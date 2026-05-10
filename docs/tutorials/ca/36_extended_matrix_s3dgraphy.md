# Tutorial 36: Exportació Extended Matrix i Bridge s3dgraphy

## Introducció

A partir de la versió **5.2.0-alpha** PyArchInit integra un **bridge bidireccional** amb la biblioteca **s3dgraphy** (model de dades Extended Matrix d'Emanuel Demetrescu). El bridge permet:

- **Exportar** el diagrama estratigràfic com a Extended Matrix en GraphML (amb swimlanes temporals, reducció transitiva, edge styling EM 1.5)
- **Reimportar** modificacions fetes a yEd (moviments d'UE entre períodes/grups) actualitzant la base SQL
- **Adjuntar paradata** (Author / License / Embargo) a nivell de lloc
- **Agrupar** UE per dimensió (struttura, area, attivita, settore, ambient, saggio, quad_par o grups ad-hoc)

Tag actual: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Requisits

- Base de dades SQLite (PostgreSQL no suportat encara)
- **Migració Phase 1 node_uuid** aplicada automàticament en obrir la DB
- **yEd Graph Editor** per visualitzar la sortida (https://www.yworks.com/products/yed)

> ⚠️ Per DB pre-5.2.0-alpha la migració pot requerir reiniciar QGIS.

---

## 2. Exportar Extended Matrix (botó verd)

### 2.1 Obrir el diàleg

1. Obre la **Fitxa UE** del lloc desitjat
2. Clica al botó verd **"Esporta Extended Matrix"** (sota la pestanya Rapporti)

### 2.2 Pestanya "Export"

El diàleg mostra:

- **Output formats**: marca DOT / GraphML / JSON / phased JSON (recomanat: GraphML)
- **Group US by (optional)**: 7 checkboxes de dimensions + 1 "ad-hoc"
  - Les dimensions amb valors a la DB es **autoseleccionen** en obrir
- **Combobox de dimensió primària** (per defecte `struttura`): quan una UE té pertinença en 2+ dimensions, la primària guanya com a folder yEd visible (parent jeràrquic). Les altres dimensions apareixen com a insígnies en línia sota el node UE. `toponym` mai és primària, independentment de la selecció.
- **"Select Output Directory"**: carpeta de destinació

A partir de 5.6.0-alpha pots marcar **2+ dimensions**: l'exportació funciona nativament gràcies al model m:n amb `is_primary` (vegeu secció "Pertinença multidimensional").

### 2.3 Clica "Export"

Es generen 4 fitxers amb prefix `Extended_Matrix_<lloc>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix per a yEd (objectiu principal)
- `_s3dgraphy.json` — format natiu s3dgraphy
- `_phased.json` — vista per època

---

## 3. Diàleg "Manage paradata" (4 pestanyes)

### 3.1 Accés
Clica al botó **"Manage paradata"** a la fitxa UE (al costat del botó verd Export).

### 3.2 Les 4 pestanyes

| Pestanya | Contingut | Fitxer generat |
|---|---|---|
| **Authors** | Afegir autors (nom + ORCID + rol) | `paradata_<lloc>.graphml` |
| **Licenses** | Llicència del dataset (ex. CC-BY-NC-4.0 + URL) | ídem |
| **Embargoes** | Dates d'embargament + motiu | ídem |
| **Groups** | Grups ad-hoc (nom + selecció UE membres) | `groups_<lloc>.graphml` |

Els fitxers es desen al costat de la DB SQLite i són **versionables a Git**.

---

## 4. Estil visual per dimensió (5.5.1-alpha + 5.6.0-alpha)

Cada dimensió d'agrupament té un color distintiu en GraphML:

| Dimensió | Fill (50% transparència) | Border |
|---|---|---|
| `area` | rosa pastel `#FFE0E680` | `#C84A5F` |
| `struttura` | taronja pastel `#FFE6CC80` | `#C66B33` |
| `attivita` | groc pastel `#FFF5CC80` | `#A89A33` |
| `settore` | verd pastel `#E6FFCC80` | `#6BC633` |
| `ambient` | aqua pastel `#CCFFE680` | `#33A86B` |
| `saggio` | atzur pastel `#CCF5FF80` | `#3389A8` |
| `quad_par` | violeta pastel `#E0CCFF80` | `#6633C6` |
| `adhoc` | gris pastel `#F5F5F580` | `#666666` |

A partir de 5.6.0-alpha, els `LocationNodeGroup` es distingeixen per `kind`:

| `kind` | Fill (50% transparència) | Border |
|---|---|---|
| `toponym` | lavanda pastel `#E6E6FA80` | `#9370DB` |
| `study` | marfil pastel `#FFFFE080` | `#888888` |
| `functional` | cian pastel `#E0FFFF80` | `#008B8B` |

L'alpha 50% deixa visibles les swimlanes de les èpoques darrere del rectangle del grup.

### 4.1 Cadena toponímica (5.6.0-alpha)

Els camps `site_table.{nazione, regione, provincia, comune}` s'emeten automàticament com a cadena recursiva de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Els nivells administratius buits s'ometen sense trencar la cadena. Una desduplicació cross-lloc garanteix que la mateixa `comune` present en 2 llocs esdevingui **un sol node compartit** al GraphML.

---

## 4.2 Pertinença multidimensional (5.6.0-alpha)

A partir de 5.6.0-alpha una UE pot pertànyer a **múltiples dimensions simultàniament** gràcies al model m:n amb el flag `is_primary`. Només la dimensió primària esdevé el folder yEd visible; les altres apareixen com a **insígnies en línia** sota el node UE i com a JSON a `<data key="s3d:other_locations">` per a eines posteriors.

Exemple: una UE amb `struttura=basilica` i `area=B` (primària `struttura`) produeix:
- folder yEd "struttura: basilica" com a parent visible;
- sota el node UE, una insígnia en línia `also: B (study), TestCity (toponym)`;
- al GraphML, l'atribut `s3d:other_locations` amb array JSON de les pertinences secundàries.

La dimensió primària es controla via combobox a §2.2.

---

## 5. Round-trip (pestanya Import)

Per modificar la base SQL movent UE entre grups en GraphML:

1. Obrir el GraphML a **yEd**
2. Arrossegar una UE a un altre grup, desar
3. Tornar al diàleg → pestanya **"Import"**
4. **Marcar** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Carregar el GraphML modificat

El sistema executa una transacció atòmica: si alguna cosa falla, **rollback complet** (la DB queda inalterada). Els grups `adhoc` mai escriuen SQL — només actualitzen `groups_<lloc>.graphml`.

A partir de 5.6.0-alpha el walker d'import és **recursiu** i suporta folders niats (p. ex. cadena toponímica `nazione > regione > provincia > comune > UE`). Si es detecten cicles al graf de folders, es llança l'excepció `CycleDetectedError` i s'avorta l'import amb rollback.

---

## 6. CLI (alternativa al diàleg)

Per a scripts / batch:

```bash
# Exportar
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Llistar grups ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Afegir autor
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = èxit, 1 = error de bridge, 2 = error argparse.

---

## 7. Resolució de problemes

| Símptoma | Causa | Solució |
|---|---|---|
| "no such column: node_uuid" | Migració Phase 1 no executada | Reiniciar QGIS, reobrir la DB |
| GraphML buit | DB sense rapporti / area filter massa estricte | Verificar us_table.rapporti |
| "rapporti han de ser TEXT" | Has introduït un número com a integer | Els camps UE/Area són **TEXT**, no integer |
| Capitalització incorrecta a rapporti | "copre" en minúscula a la DB | Usar "Copre", "Coperto da" capitalitzats |
| `DeprecationWarning` en fitxer 5.5.x | Fitxer legacy `ActivityNodeGroup + group_kind` | El projector el promociona en memòria a `LocationNodeGroup`. Reexporta per migrar el fitxer al disc. |

---

## 8. Documentació tècnica

Per aprofundir en arquitectura, decisions de disseny i roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over diferits:
- **AI08-F3**: heurístiques d'auto-layout (bin-packing de sub-grups) — encara diferit
- **AI09**: TimeBranchNodeGroup mapping — futur
- **Phase 3**: SyncEngine + REST API — futur
- **Phase 4**: GraphDBBackend + SPARQL — futur

Lliurats:
- **AI07** (5.6.0-alpha, 2026-05-10): migració `LocationNodeGroup` amb enum `kind` + cadena toponímica + pertinences multidimensionals
- **AI08-F1** (fusionat en AI07): nesting jeràrquic natiu via `is_primary`

---

## Referències

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositori pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
