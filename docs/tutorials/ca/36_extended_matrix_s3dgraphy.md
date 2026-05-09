# Tutorial 36: Exportació Extended Matrix i Bridge s3dgraphy

## Introducció

A partir de la versió **5.2.0-alpha** PyArchInit integra un **bridge bidireccional** amb la biblioteca **s3dgraphy** (model de dades Extended Matrix d'Emanuel Demetrescu). El bridge permet:

- **Exportar** el diagrama estratigràfic com a Extended Matrix en GraphML (amb swimlanes temporals, reducció transitiva, edge styling EM 1.5)
- **Reimportar** modificacions fetes a yEd (moviments d'UE entre períodes/grups) actualitzant la base SQL
- **Adjuntar paradata** (Author / License / Embargo) a nivell de lloc
- **Agrupar** UE per dimensió (struttura, area, attivita, settore, ambient, saggio, quad_par o grups ad-hoc)

Tag actual: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

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
- **"Select Output Directory"**: carpeta de destinació

### 2.3 Límit single-dimension (5.5.2-alpha)

Si marques **2 o més** checkboxes d'agrupament, apareix un avís:

> *"Exportació multi-dim no suportada encara. Continuar amb NOMÉS la primera dimensió seleccionada?"*

Tria **Sí** (exporta amb la primera marcada) o **Cancel·la** (modifica selecció). El nesting jeràrquic (struttura > attivita > UE) arriba amb AI08-F1.

### 2.4 Clica "Export"

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

## 4. Estil visual per dimensió (5.5.1-alpha)

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

L'alpha 50% deixa visibles les swimlanes de les èpoques darrere del rectangle del grup.

---

## 5. Round-trip (pestanya Import)

Per modificar la base SQL movent UE entre grups en GraphML:

1. Obrir el GraphML a **yEd**
2. Arrossegar una UE a un altre grup, desar
3. Tornar al diàleg → pestanya **"Import"**
4. **Marcar** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Carregar el GraphML modificat

El sistema executa una transacció atòmica: si alguna cosa falla, **rollback complet** (la DB queda inalterada). Els grups `adhoc` mai escriuen SQL — només actualitzen `groups_<lloc>.graphml`.

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
| Carpeta de grup buida a yEd | Marcant 2+ dimensions (límit 5.5.2-alpha) | Marcar només una, reintentar |
| "rapporti han de ser TEXT" | Has introduït un número com a integer | Els camps UE/Area són **TEXT**, no integer |
| Capitalització incorrecta a rapporti | "copre" en minúscula a la DB | Usar "Copre", "Coperto da" capitalitzats |

---

## 8. Documentació tècnica

Per aprofundir en arquitectura, decisions de disseny i roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over diferits:
- **AI07**: migració `LocationNodeGroup` (deadline upstream 2026-05-23)
- **AI08-F1**: nesting jeràrquic (per multi-dim export net)
- **AI08-F3**: heurístiques d'auto-layout (bin-packing de sub-grups)
- **AI09**: TimeBranchNodeGroup mapping
- **Phase 3**: SyncEngine + REST API
- **Phase 4**: GraphDBBackend + SPARQL

---

## Referències

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositori pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
