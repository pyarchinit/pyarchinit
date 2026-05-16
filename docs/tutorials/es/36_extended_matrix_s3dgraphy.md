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

## 5. yEd-aware Import — importar graphmls editados externamente (5.8.x)

A partir de **5.8.0-alpha** el bridge es **bidireccional también para graphmls creados directamente en yEd** (es decir, sin pasar antes por una exportación pyarchinit). Pyarchinit reconoce automáticamente los graphmls «yEd-raw» — los que no llevan data keys `pyarchinit.*` — y los importa mediante un dispatch dedicado que mapea el prefijo de label del nodo → tipo estratigráfico, reconoce filas de TableNode como periodos, recorre los group folder como dimensiones arqueológicas y permite al usuario elegir una política para las edges que tocan folders.

### 5.1 Despliegue en 6 hitos

| Hito | Tag | Qué añade |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag de flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` con 13 valores (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate desde filas de TableNode) + `yed_group_walker.py` (FolderCandidate con auto-dimension desde el prefijo del label: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orquestador `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + centinela `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` con 5 páginas (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + persistencia sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Esta documentación + dev-log + CHANGELOG. |

### 5.2 Cómo funciona — flujo de usuario

1. **Abre un graphml en QGIS mediante el menú Import GraphML** (mismo path que el flujo pyarchinit-projected existente).
2. Pyarchinit detecta automáticamente que es yEd-raw (sin keys `pyarchinit.*`) → dispatcha al nuevo branch en lugar de caer en el path legacy.
3. Se abre el wizard `YedImportDialog` con **5 páginas**:
   - **1/5 Classifier** — tabla con una fila por leaf node. Cada fila muestra `label` + `auto_kind` (p. ej. `us_real` / `usv_virtual` / `property`) + un combobox de override `user_kind`. El botón **Aceptar auto** reinicia cada fila a su `auto_kind` (borra todos los overrides).
   - **2/5 Periods** — una fila por TableNode-row parseada, columnas editables `periodo` + `fase`. Las fechas (`datazione_iniziale`/`finale`) quedan vacías: los graphmls yEd-raw no llevan fechas.
   - **3/5 Folders** — una fila por group folder. Combobox de `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` para excluir). `value` editable (default = `auto_value` derivado del prefijo del label).
   - **4/5 Rapporti policy** — 4 radio buttons para tratar las edges que tocan folders:
     - **SKIP** (default): descarta las edges folder-touching. Las edges leaf-to-leaf pasan intactas.
     - **FAN_OUT**: una edge `folder_A → folder_B` se expande a `N×M` pares de leaves (producto cartesiano de los miembros).
     - **REPRESENTATIVE**: usa el primer miembro de cada folder como proxy.
     - **SYNTHETIC**: crea una fila us_table por folder (`unita_tipo='VA'` virtual activity) + reconecta las edges a través de estos anchors.
   - **5/5 Preview** — dry-run de `import_yed_raw(overrides=..., dry_run=True)`. Muestra counts (us / inv / period / paradata) **sin commit**. Click en **Finish** confirma, **Cancel** abandona.
4. Al pulsar **Finish** el wizard guarda tus overrides en un **sidecar JSON** `<graphml>.yed_overrides.json` junto al fichero. Al reabrir el mismo graphml se precarga el sidecar, así que tus overrides previos vuelven preaplicados.

### 5.3 Routing de destinos

El dispatch usa `_classify_destination` (en `yed_import_pipeline.py`) para clasificar cada leaf:

| ClassificationKind | Destino | Nota |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | desde label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | desde `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | desde `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | desde `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derivado del prefijo del label: USVs/USVn/USVc) | desde `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | desde `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | desde `^SF\d+` |
| VIRTUAL_FIND | `paradata` (vía `ParadataStore`) | desde `^VSF\d+` |
| DOCUMENT | `paradata` | desde `^D\.\d+` |
| COMBINER | `paradata` | desde `^C\.\d+` |
| PROPERTY | `paradata` | keyword en label (`material`/`position`/`width`/...) |

**Decisión de usuario 2026-05-13**: las USV* (virtuales) son «unità tipo» (siguen siendo unidades estratigráficas) y van en `us_table`, no en paradata. Solo DOC/COMB/PROP/VIRTUAL_FIND permanecen en paradata.

### 5.4 Sidecar JSON — esquema

Versionado para forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
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

Solo se persisten los campos MODIFICADOS por el usuario (diff). Los valores `ClassificationKind` desconocidos (p. ej. de futuras releases de s3dgraphy) se omiten silenciosamente al cargar.

### 5.5 CLI para ingest scripted

Para CI / re-runs en batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` para backend SQLite vs PostgreSQL. `--overrides` es opcional (sin overrides = defaults de yE-D). `--auto-defaults` es un no-op forward-compat.

### 5.6 Limitaciones conocidas

- **Sin edición de fechas en el wizard**: los graphmls yEd-raw no llevan `datazione_iniziale`/`datazione_finale`. La página Periods solo edita `periodo` + `fase` (targets FK).
- **API ParadataStore parcial**: upstream s3dgraphy aún no entrega `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D loggea «skip — method missing» por cada paradata leaf pero contabiliza los intentos en el preview.
- **PropertyNode → Path B (sin enlace a US)**: los nodos PROPERTY se escriben sin US target. El wizard emite un warning. Futuro: follow-up yE-Closure para añadir «assign target» en la UI.
- **Multi-DB**: el sidecar JSON es por graphml, no por DB. Si importas el mismo graphml en DBs distintas, se reutilizan los mismos overrides para ambas.

### 5.7 Cobertura de tests final

| Suite | Test | Cobertura |
|---|---|---|
| yE-A | `test_yed_detector.py` | detección de flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse de PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | políticas + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | persistencia sidecar + CLI |

**Suite total post-rollout**: 354 passed / 42 skipped (PG-L1 requieren psycopg2).

### 5.8 Actualización 5.8.5-alpha (yed-fastfix)

Pack de correcciones de comportamiento sobre `5.8.3-alpha` que mejora la calidad del re-export GraphML tras un import yEd-aware. Cambios relevantes para el usuario final:

- **Paradata multi-folder**: las labels DOC / Combinar / Extractor / property compartidas entre varias folders yEd (ej. `material` referenciado desde VA01 + VA04 + VA05) ahora generan UNA fila en `us_table` POR ocurrencia — visibilidad multi-folder restaurada en el GraphML re-exportado. Compromiso: el dedup por identidad (colapsar `D.01` / `D.01-2` / `D.01bis` en una sola fila) ya no se aplica a la segunda/tercera ocurrencia.
- **Rapporti recíprocos**: cada edge yEd `a → b` escribe el rapporto directo en la fila de `a` Y el inverso en la fila de `b` (`<<` / «Coperto da» / etc.). Los DOC muestran ahora todas las conexiones extractor entrantes en el formulario Scheda US.
- **Strip del prefijo `us` numérico**: `US100` → `us='100'` `unita_tipo='US'` (antes `us='US100'`). SF/VSF/RSF se escriben dual en `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase**: la pertenencia de una fila TableNode yEd a un período se propaga a `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserva la distinción semántica EM 1.5.
- **Re-import idempotente**: volver a ejecutar el mismo import omite las filas ya presentes; sin rollback por colisión UNIQUE en la pasada repetida.
- **Paleta USV**: los nodos USV se renderizan ahora con el paralelogramo azul canónico de EM (antes rectángulo con borde rojo).

---

## Referencias

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositorio pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
