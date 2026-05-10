# Tutorial 36: Exportación Extended Matrix y Bridge s3dgraphy

## Introducción

A partir de la versión **5.2.0-alpha** PyArchInit integra un **bridge bidireccional** con la biblioteca **s3dgraphy** (modelo de datos Extended Matrix de Emanuel Demetrescu). El bridge permite:

- **Exportar** el diagrama estratigráfico como Extended Matrix en GraphML (con swimlane temporales, reducción transitiva, edge styling EM 1.5)
- **Reimportar** modificaciones realizadas en yEd (movimientos de UE entre periodos/grupos) actualizando la base SQL
- **Adjuntar paradata** (Author / License / Embargo) a nivel de sitio
- **Agrupar** UE por dimensión (struttura, area, attivita, settore, ambient, saggio, quad_par o grupos ad-hoc)

Tag actual: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

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
- **Selector de dimensión primaria** (predeterminado `struttura`): cuando una UE tiene pertenencia en 2+ dimensiones, la primaria gana como folder yEd visible (parent jerárquico). Las demás dimensiones aparecen como insignias en línea bajo el nodo UE. `toponym` nunca es primaria, sin importar la selección.
- **"Select Output Directory"**: carpeta de destino

A partir de 5.6.0-alpha puedes marcar **2+ dimensiones**: la exportación funciona nativamente gracias al modelo m:n con `is_primary` (ver sección "Pertenencia multidimensional").

### 2.3 Click en "Export"

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

## 4. Estilo visual por dimensión (5.5.1-alpha + 5.6.0-alpha)

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

A partir de 5.6.0-alpha, los `LocationNodeGroup` se distinguen por `kind`:

| `kind` | Fill (50% transparencia) | Border |
|---|---|---|
| `toponym` | lavanda pastel `#E6E6FA80` | `#9370DB` |
| `study` | marfil pastel `#FFFFE080` | `#888888` |
| `functional` | cian pastel `#E0FFFF80` | `#008B8B` |

El alpha 50% deja visibles las swimlane de las épocas detrás del rectángulo del grupo.

### 4.1 Cadena toponímica (5.6.0-alpha)

Los campos `site_table.{nazione, regione, provincia, comune}` se emiten automáticamente como una cadena recursiva de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Los niveles administrativos vacíos se omiten sin romper la cadena. Una deduplicación cross-sitio garantiza que el mismo `comune` presente en 2 sitios se convierta en **un único nodo compartido** en el GraphML.

---

## 4.2 Pertenencia multidimensional (5.6.0-alpha)

A partir de 5.6.0-alpha una UE puede pertenecer a **múltiples dimensiones simultáneamente** gracias al modelo m:n con flag `is_primary`. Solo la dimensión primaria se convierte en el folder yEd visible; las demás aparecen como **insignias en línea** bajo el nodo UE y como JSON en `<data key="s3d:other_locations">` para herramientas posteriores.

Ejemplo: una UE con `struttura=basilica` y `area=B` (primaria `struttura`) produce:
- folder yEd "struttura: basilica" como parent visible;
- bajo el nodo UE, una insignia en línea `also: B (study), TestCity (toponym)`;
- en el GraphML, el atributo `s3d:other_locations` con array JSON de las pertenencias secundarias.

La dimensión primaria se controla mediante el selector en §2.2.

---

## 5. Round-trip (pestaña Import)

Para modificar la base SQL moviendo UE entre grupos en GraphML:

1. Abrir el GraphML en **yEd**
2. Arrastrar una UE a otro grupo, guardar
3. Volver al diálogo → pestaña **"Import"**
4. **Marcar** el checkbox *"Update SQL on import (struttura/area/...)"*
5. Cargar el GraphML modificado

El sistema ejecuta una transacción atómica: si algo falla, **rollback completo** (el DB queda inalterado). Los grupos `adhoc` nunca escriben SQL — solo actualizan `groups_<sito>.graphml`.

A partir de 5.6.0-alpha el walker de import es **recursivo** y soporta folders anidados (p. ej. cadena toponímica `nazione > regione > provincia > comune > UE`). Si se detectan ciclos en el grafo de folders, se lanza la excepción `CycleDetectedError` y se aborta el import con rollback.

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
| "rapporti deben ser TEXT" | Has introducido un número como integer | Los campos UE/Area son **TEXT**, no integer |
| Capitalización errónea en rapporti | "copre" minúsculo en DB | Usar "Copre", "Coperto da" capitalizados |
| `DeprecationWarning` en archivo 5.5.x | Archivo legacy `ActivityNodeGroup + group_kind` | El projector lo promociona en memoria a `LocationNodeGroup`. Reexportar para migrar el archivo en disco. |

---

## 8. Documentación técnica

Para profundizar en arquitectura, decisiones de diseño y roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over diferidos:
- **AI08-F3**: auto-layout heuristics (bin-packing de sub-grupos) — sigue diferido
- **AI09**: TimeBranchNodeGroup mapping — futuro
- **Phase 3**: SyncEngine + REST API — futuro
- **Phase 4**: GraphDBBackend + SPARQL — futuro

Entregados:
- **AI07** (5.6.0-alpha, 2026-05-10): migración `LocationNodeGroup` con enum `kind` + cadena toponímica + pertenencias multidimensionales
- **AI08-F1** (fusionado en AI07): nesting jerárquico nativo vía `is_primary`

---

## Referencias

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositorio pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
