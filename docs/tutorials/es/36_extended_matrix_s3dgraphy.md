# Tutorial 36: Exportación Extended Matrix y Bridge s3dgraphy

## Introducción

A partir de la versión **5.2.0-alpha** PyArchInit integra un **bridge bidireccional** con la biblioteca **s3dgraphy** (modelo de datos Extended Matrix de Emanuel Demetrescu). El bridge permite:

- **Exportar** el diagrama estratigráfico como Extended Matrix en GraphML (con swimlane temporales, reducción transitiva, edge styling EM 1.5)
- **Reimportar** modificaciones realizadas en yEd (movimientos de UE entre periodos/grupos) actualizando la base SQL
- **Adjuntar paradata** (Author / License / Embargo) a nivel de sitio
- **Agrupar** UE por dimensión (struttura, area, attivita, settore, ambient, saggio, quad_par o grupos ad-hoc)

Tag actual: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

---

## 1. Requisitos

- Base de datos SQLite (PostgreSQL no soportado todavía)
- **Migración Phase 1 node_uuid** aplicada automáticamente al abrir el DB
- **yEd Graph Editor** para visualizar el output (https://www.yworks.com/products/yed)

> ⚠️ Para DB pre-5.2.0-alpha la migración puede requerir reiniciar QGIS.

---

## 2. Exportar Extended Matrix (botón verde)

### 2.1 Abrir el diálogo

1. Abre la **Ficha UE** del sitio deseado
2. Click en el botón verde **"Esporta Extended Matrix"** (debajo de la pestaña Rapporti)

### 2.2 Pestaña "Export"

El diálogo muestra:

- **Output formats**: marca DOT / GraphML / JSON / phased JSON (recomendado: GraphML)
- **Group US by (optional)**: 7 checkboxes de dimensiones de agrupamiento + 1 "ad-hoc"
  - Las dimensiones con valores en el DB se **autoseleccionan** al abrir
- **"Select Output Directory"**: carpeta de destino

### 2.3 Límite single-dimension (5.5.2-alpha)

Si marcas **2 o más** checkboxes de agrupamiento, aparece un aviso:

> *"Exportación multi-dim no soportada todavía. ¿Continuar con SOLO la primera dimensión seleccionada?"*

Elige **Sí** (exporta con el primer checkbox marcado) o **Cancelar** (modificar selección). El nesting jerárquico (struttura > attivita > UE) llega con AI08-F1.

### 2.4 Click en "Export"

Se generan 4 archivos con prefijo `Extended_Matrix_<sito>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix para yEd (objetivo principal)
- `_s3dgraphy.json` — formato nativo s3dgraphy
- `_phased.json` — vista por época

---

## 3. Diálogo "Manage paradata" (4 pestañas)

### 3.1 Acceso
Click en el botón **"Manage paradata"** en la ficha UE (cerca del botón verde Export).

### 3.2 Las 4 pestañas

| Pestaña | Contenido | Archivo generado |
|---|---|---|
| **Authors** | Añadir autores (nombre + ORCID + rol) | `paradata_<sito>.graphml` |
| **Licenses** | Licencia del dataset (ej. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Fechas de embargo + motivo | idem |
| **Groups** | Grupos ad-hoc (nombre + selección UE miembros) | `groups_<sito>.graphml` |

Los archivos se guardan junto al DB SQLite y son **versionables en Git**.

---

## 4. Estilo visual por dimensión (5.5.1-alpha)

Cada dimensión de agrupamiento tiene un color distintivo en GraphML:

| Dimensión | Fill (50% transparencia) | Border |
|---|---|---|
| `area` | rosa pastel `#FFE0E680` | `#C84A5F` |
| `struttura` | naranja pastel `#FFE6CC80` | `#C66B33` |
| `attivita` | amarillo pastel `#FFF5CC80` | `#A89A33` |
| `settore` | verde pastel `#E6FFCC80` | `#6BC633` |
| `ambient` | aqua pastel `#CCFFE680` | `#33A86B` |
| `saggio` | azul pastel `#CCF5FF80` | `#3389A8` |
| `quad_par` | violeta pastel `#E0CCFF80` | `#6633C6` |
| `adhoc` | gris pastel `#F5F5F580` | `#666666` |

El alpha 50% deja visibles las swimlane de las épocas detrás del rectángulo del grupo.

---

## 5. Round-trip (pestaña Import)

Para modificar la base SQL moviendo UE entre grupos en GraphML:

1. Abrir el GraphML en **yEd**
2. Arrastrar una UE a otro grupo, guardar
3. Volver al diálogo → pestaña **"Import"**
4. **Marcar** el checkbox *"Update SQL on import (struttura/area/...)"*
5. Cargar el GraphML modificado

El sistema ejecuta una transacción atómica: si algo falla, **rollback completo** (el DB queda inalterado). Los grupos `adhoc` nunca escriben SQL — solo actualizan `groups_<sito>.graphml`.

---

## 6. CLI (alternativa al diálogo)

Para scripts / batch:

```bash
# Exportar
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Listar grupos ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Añadir autor
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = éxito, 1 = error de bridge, 2 = error argparse.

---

## 7. Resolución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| "no such column: node_uuid" | Migración Phase 1 no ejecutada | Reiniciar QGIS, reabrir el DB |
| GraphML vacío | DB sin rapporti / area filter muy estricto | Verificar us_table.rapporti |
| Folder de grupo vacío en yEd | Estás marcando 2+ dimensiones (límite 5.5.2-alpha) | Marcar solo una, reintentar |
| "rapporti deben ser TEXT" | Has introducido un número como integer | Los campos UE/Area son **TEXT**, no integer |
| Capitalización errónea en rapporti | "copre" minúsculo en DB | Usar "Copre", "Coperto da" capitalizados |

---

## 8. Documentación técnica

Para profundizar en arquitectura, decisiones de diseño y roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over diferidos:
- **AI07**: migración `LocationNodeGroup` (deadline upstream 2026-05-23)
- **AI08-F1**: hierarchical nesting (para multi-dim export limpio)
- **AI08-F3**: auto-layout heuristics (bin-packing de sub-grupos)
- **AI09**: TimeBranchNodeGroup mapping
- **Phase 3**: SyncEngine + REST API
- **Phase 4**: GraphDBBackend + SPARQL

---

## Referencias

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositorio pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
