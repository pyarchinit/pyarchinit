# Tutorial 36: Exportación Extended Matrix y Bridge s3dgraphy

## Introducción

A partir de la versión **5.2.0-alpha** PyArchInit integra un **bridge bidireccional** con la biblioteca **s3dgraphy** (modelo de datos Extended Matrix de Emanuel Demetrescu). El bridge permite:

- **Exportar** el diagrama estratigráfico como Extended Matrix en **em.json**, el formato que abre EMStudio (la antigua exportación GraphML está retirada)
- **Reimportar** modificaciones realizadas en yEd (movimientos de UE entre periodos/grupos) actualizando la base SQL
- **Adjuntar paradata** (Author / License / Embargo) a nivel de sitio
- **Agrupar** UE por dimensión (struttura, area, attivita, settore, ambient, saggio, quad_par o grupos ad-hoc)

Tag actual: `ordine-indice-5.13.116-alpha` (2026-10-13).

---

## 1. Requisitos

- Base de datos SQLite/Spatialite **o PostgreSQL/PostGIS**: la exportación a em.json es la misma en los dos motores (la conexión es la del proyecto; `export_site` acepta `sqlite://` y `postgresql://`)
- **Migración Phase 1 node_uuid** aplicada automáticamente al abrir el DB
- **EMStudio** para abrir el em.json (se instala desde **Extended Matrix → Installa EMStudio…**), o el panel **Vedi la matrice…** dentro de QGIS, que no necesita nada más. **yEd** (https://www.yworks.com/products/yed) solo hace falta si importas archivos GraphML dibujados allí (§5)

> ⚠️ Para DB pre-5.2.0-alpha la migración puede requerir reiniciar QGIS.

---

## 2. Exportar Extended Matrix (botón verde)

### 2.1 Abrir el diálogo

1. Abre la **Ficha UE** del sitio deseado
2. Click en el botón verde **"Esporta Extended Matrix"** (debajo de la pestaña Rapporti)

### 2.2 Pestaña "Export"

La ventana dice arriba para qué sirve cada formato. Contiene:

- **Formati** (Formatos): **DOT (Graphviz) — matrice di Harris** y **em.json (Extended Matrix, per EMStudio)**, marcados de partida, más **Matrice per fasi** (matriz por fases, análisis cronológico), opcional. El GraphML ya no se exporta: el JSON de esta ventana **es el em.json**, el mismo archivo que produce el menú **Extended Matrix → Esporta sito in em.json…** — mismo proyector, misma simbología.
- **Opzioni** (Opciones): **Controlla la sequenza stratigrafica e segnala i problemi** (comprobar la secuencia estratigráfica y señalar los problemas). Es la única opción que queda, y ahora se lee de verdad: sin la marca, la comprobación no se hace. Las dos casillas antiguas que hablaban a yEd (pistas de auto-layout, color por periodo) se fueron con la exportación GraphML.
- **Extended Matrix**: cuatro botones junto a la exportación — **Apri in EMStudio** y **Vedi la matrice** (ambos se activan tras una exportación em.json correcta; el segundo dibuja la matriz dentro de QGIS, sin EMStudio), **Consegna alla stanza…** y **Apri la stanza**. Son las mismas entradas del menú pyArchInit, al alcance de la mano.

Al pulsar **Esporta** se pide la **carpeta de destino**.

Autores, licencias, embargos y grupos se gestionan en la ventana **"Manage paradata"** (§3).

### 2.2.1 Sondeos: un solo grafo para todo el sitio

A partir de la versión **5.13.109-alpha**, el em.json lleva **un solo grafo**, con las unidades de todos los sondeos: no hay nada que elegir. La ventana «Esporta Extended Matrix» ya no tiene el grupo «Saggi» (sondeos), y las entradas de menú **Esporta sito in em.json…** y **Vedi la matrice…** solo piden el sitio.

El sondeo es el campo **Saggio** de la ficha UE: sigue siendo un campo como los demás, que se puede usar como dimensión para agrupar las unidades (`saggio`, §4) y que pasa al *briefing* de la narrativa (§10.4), pero ya no divide el archivo. Un archivo exportado con las versiones anteriores (hasta la 5.13.108-alpha), con un grafo por sondeo, se sigue abriendo en el panel de la matriz (§10.8).

### 2.3 Click en "Esporta"

Los archivos que nacen, según los formatos marcados:
- `<sitio>.em.json` — Extended Matrix, para abrir en EMStudio o entregar a una sala
- `Extended_Matrix_<sitio>[_<area>].dot` — Graphviz DOT, para la matriz de Harris clásica
- `Extended_Matrix_<sitio>[_<area>]_phased.json` — vista por época

> **Los lugares viajan en el em.json.** El lugar del sitio, la cadena toponímica y los grupos de áreas, sectores, sondeos y ambientes salen junto con las unidades, unidos por aristas `is_in_location` (§4).

El resumen final enumera los archivos y, para el em.json, **cuántos nodos y cuántas aristas** han salido, con los avisos que haya.

> **El GraphML ya no se exporta**: la matriz se mira y se valida en EMStudio, que lee em.json. Las filas temporales (swimlanes) del GraphML antiguo se fueron con él. El GraphML sobrevive solo a la **entrada**, para los archivos dibujados en yEd (§5).

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

## 4. Dimensiones y tipos de grupo en el em.json

El em.json que exporta pyArchInit lleva los **grupos de lugar** (`LocationNodeGroup`) de la ficha UE, distinguidos por el tipo `kind`: `toponym`, la cadena nazione → regione → provincia → comune y el lugar del sitio (§4.1); `study`, las **áreas**, los **sectores** y los **sondeos**; `functional`, los **ambientes**. Cada unidad está unida a los grupos en que se encuentra mediante aristas `is_in_location`; el identificador del grupo dice el campo del que nace (por ejemplo `loc::area::study::1`). El archivo no lleva colores: los decide quien lo lee, EMStudio con su propio estilo y el panel de la matriz en QGIS con las reglas visuales de la biblioteca s3dgraphy. La antigua exportación GraphML coloreaba los grupos por dimensión: esa paleta quedó retirada con ella. La biblioteca sabe también agrupar por **estructura**, **actividad**, **cuadro** y por grupos ad-hoc, con una pertenencia primaria y las demás secundarias (`is_primary`): pyArchInit hoy no se lo pide, y en el archivo ese atributo aparece solo en las aristas de la cadena toponímica, siempre falso.

### 4.1 Cadena toponímica (5.6.0-alpha)

Los campos `site_table.{nazione, regione, provincia, comune}` se emiten automáticamente como una cadena recursiva de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Los niveles administrativos vacíos se omiten sin romper la cadena. Una deduplicación cross-sitio garantiza que el mismo `comune` presente en 2 sitios se convierta en **un único nodo compartido** en el em.json.

---

## 4.2 Pertenencia multidimensional (5.6.0-alpha)

Una unidad puede estar en varios grupos a la vez — un área, un sector, un sondeo, un ambiente, además del lugar del sitio — y en el archivo tiene una arista `is_in_location` por cada uno, todas en pie de igualdad. Ejemplo: una UE con `area=1`, `settore=1` y `ambient=Ambiente 3` tiene tres aristas, hacia «1» (área, `study`), «1» (sector, `study`) y «Ambiente 3» (`functional`), más la que va al lugar del sitio, de donde sube la cadena toponímica. La distinción entre pertenencia primaria y secundaria (`is_primary`, con `struttura` en primer lugar y `toponym` nunca primario) es del modelo de la biblioteca, para quien le pide los grupos por dimensión: en el em.json de pyArchInit no existe.

---

## 5. Round-trip (pestaña Import)

> **Qué se puede importar**: la pestaña Import lee ahora también **em.json** — el de EMStudio o el del nodo StratiGraph — y elige el lector según la extensión del archivo; el `.graphml` de yEd sigue aceptándose para los archivos de antes. El procedimiento de abajo, mover UE entre grupos, se refiere a la vía yEd/GraphML.

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
| Las filas de la swimlane muestran un texto larguísimo | Las versiones anteriores usaban la Descrizione de la periodización como etiqueta | Actualiza el plugin y reexporta, y/o rellena **Datazione estesa** con un nombre breve |
| Las épocas de la swimlane están en orden incorrecto (ej. Bronce por encima del Tardoantiguo) | Las filas se ordenan por **Cronología Inicial**; las fechas a.C. introducidas como números positivos (1650 en lugar de -1650) se ordenan como d.C. | En la Ficha de Periodización introduce los años a.C. como números negativos y reexporta. El resumen de la exportación muestra ahora un aviso "⚠️ Periodizzazione: ..." con la lista de periodos a corregir |

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

### 5.9 yE-F paradata multi-carpeta (5.9.0-alpha)

Evolución estructural de `yed-fastfix-5.8.5-alpha`: el compromiso del Bug R B1 (una fila `us_table` por ocurrencia, con `us='D.01_2'` / `us='D.01_3'`) ha sido superado. Una hoja paradata (DOC / Combinar / Extractor / property) compartida entre varias carpetas yEd ahora produce **una sola fila** en `us_table` por label canónico, y la multi-pertenencia se preserva en una nueva columna `other_locations`.

Cambios visibles para el usuario final:

1. **Nuevo widget "Otras actividades" en la ficha US/USM**: en la pestaña *Periodizzazione* aparece un `QListWidget` etiquetado "Otras actividades" — visible **solo** cuando `unita_tipo` es una tipología paradata (`DOC`, `Combinar`, `Extractor`, `property`). El usuario puede seleccionar varios códigos de actividad; la selección se serializa como lista JSON en la nueva columna `other_locations`.
2. **Nueva entrada de menú QGIS**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Debe ejecutarse **una vez** en cada DB preexistente para añadir la nueva columna (las DB creadas post-5.9 ya tienen la columna).
3. **Import yEd-aware mejorado**: una hoja paradata que aparece en N carpetas yEd genera ahora **solo 1** fila `us_table` (ya no N filas con sufijo `_2`/`_3` como en 5.8.5). La primera carpeta encontrada se convierte en la `attivita` principal; las carpetas secundarias se listan en `other_locations`. En **export** se emiten N copias visuales yEd (una por carpeta), todas compartiendo el mismo `node_uuid` canónico para garantizar la identidad round-trip.

**Compatibilidad hacia atrás**: los datos producidos por el Bug R B1 en 5.8.5-alpha (filas con sufijo `_2`/`_3`) siguen siendo legibles sin ninguna conversión automática. La nueva lógica se aplica a los nuevos imports; las filas legacy continúan comportándose como antes.

Predecesor: véase la sección 5.8 (`yed-fastfix-5.8.5-alpha`) para el comportamiento sustituido.

---

## 6. Generar continuidad (fichas CON)

En el panel **«Verifica rapporti»** — disponible como pestaña dentro del diálogo de importación/exportación de s3dgraphy — se encuentra el botón **«Genera continuità»** (etiqueta mantenida en italiano como en el plugin). Para el sitio actualmente seleccionado, esta función crea automáticamente las **fichas de continuidad** de las US/USM cuya vida abarca más de un periodo.

### 6.1 Qué hace

1. Escanea todas las US/USM del sitio cuyo **periodo inicial ≠ periodo final** (es decir, cuya vida abarca más de un periodo).
2. Para cada una crea o actualiza una ficha de continuidad llamada **`CON_<us>`** (p. ej. `US5` → `CON_US5`).
3. La ficha CON **hereda** de la unidad madre: sitio, área (más las áreas secundarias), estructura y todo el arco de periodos (inicial → final). Su descripción se genera automáticamente.
4. Escribe una **relación de continuidad recíproca** en ambos lados: en la CON y en su unidad madre.

> **La fase, por sí sola, no cuenta.** La regla mira el **periodo**: una USM que va de **2/3 a 2/4** —mismo periodo, solo cambia la fase— no genera nada. Si tus unidades sobreviven de fase en fase dentro del mismo periodo, marca **«anche i salti di fase»** («también los saltos de fase») junto al botón: entonces esos saltos también cuentan, siempre que **ambas** fases estén rellenadas. Una unidad que no se mueve —mismo periodo y misma fase— nunca es una continuidad. La casilla empieza **sin marcar**, y vale para la vista previa y para la escritura a la vez.

### 6.2 Idempotencia

La operación es **idempotente**: relanzarla no duplica las fichas existentes — actualiza las `CON_<us>` existentes si los datos de la unidad madre han cambiado.

### 6.3 Vista previa (dry-run) y copia de seguridad

Antes de escribir se muestra una **vista previa dry-run** con los recuentos: cuántas fichas hay que **crear**, **actualizar**, **sin cambios** y cuántas **huérfanas**. Los cambios se aplican **solo tras la confirmación** (botón «Genera»). Al aplicar se realiza primero una **copia de seguridad de la base de datos** automática.

Una ficha CON es **huérfana** cuando su unidad madre ya no abarca varios periodos (p. ej. se igualaron su periodo inicial y final). Por defecto las huérfanas solo se **señalan**; una **casilla de verificación** («Rimuovi anche le CON orfane») permite optar por eliminarlas.

**Una continuidad escrita a mano se reconoce.** Una ficha CON cuyas relaciones nombran una sola unidad —`> 12`, o «Continuidad posterior a 12»— es la continuidad de esa unidad, se llame como se llame: el generador la **actualiza** (arco de periodos, etiqueta canónica) y el nombre sigue siendo el suyo. No nace una segunda: la continuidad es **una por unidad**. Si también existe una `CON_<us>` canónica, gana esa y la otra queda como huérfana para decidir a mano.

### 6.4 En la exportación Extended Matrix

Las fichas `CON_<us>` así generadas aparecen en el **em.json** del Extended Matrix como **elementos de continuidad** (la exportación GraphML está retirada, §2.3).

---

## 7. Verificación de paradojas temporales (estratigráficas)

En el panel **"Verifica rapporti"** (Verificar relaciones — una pestaña del diálogo de import/export de s3dgraphy), la verificación ahora también señala las **paradojas temporales**: cuando el periodo/fase asignado a una unidad contradice la estratigrafía observada. La estratigrafía es el dato de referencia, por lo que las correcciones automáticas desplazan los **periodos**, no las relaciones.

### 7.1 Qué detecta
- **Inversión temporal**: dos unidades datadas unidas por una relación de orden (p. ej. US5 «cubre» US7) en la que la unidad más reciente en la estratigrafía resulta enteramente más **antigua** por periodo.
- **Contemporaneidad incoherente**: unidades declaradas contemporáneas (igualdad física / vínculo) pero con intervalos cronológicos **disjuntos**.
- **No evaluable**: relación de orden en la que al menos una de las dos unidades no tiene un periodo datable (solo señalado, sin corrección).

Nota sobre el límite: dos periodos **adyacentes que se tocan** en un único punto cronológico se consideran solapados → **no** son una paradoja (beneficio de la duda).

### 7.2 Corrección automática y sugerencias
- Cuando un solo desplazamiento resuelve el conflicto, la verificación propone desplazar la unidad **mono-periodo** en conflicto con la mayoría de sus vecinos, eligiendo el periodo de desplazamiento mínimo; para las contemporaneidades con una unidad no datable copia el periodo del vecino datado.
- En los casos ambiguos — empate, unidades **multi-periodo** (p. ej. fichas CON), ningún periodo válido — no corrige automáticamente: proporciona una **sugerencia «qué + cómo»** (p. ej. «Desplaza US5 a un periodo ≥ 3, o US7 a un periodo ≤ 1, o verifica la relación»).

### 7.3 Vista previa y copia de seguridad
- La **vista previa** muestra los cambios de periodo propuestos antes de aplicarlos.
- Antes de escribir los periodos se realiza una **copia de seguridad automática de la base de datos** (SQLite y PostgreSQL).
- Tras aplicar, vuelve a lanzar la verificación para comprobar eventuales paradojas residuales.

---

## 8. Verificación de la cronología (periodización y fichas)

En el mismo panel **"Verifica rapporti"** (Verificar relaciones — una pestaña del diálogo de import/export de s3dgraphy), desde la versión 5.13.64-alpha la verificación también encuentra y corrige problemas de **cronología** del sitio seleccionado. La verificación de paradojas temporales (sección 7) compara el periodo de una unidad con la estratigrafía; esta compara la periodización consigo misma y con las fichas UE que la copian.

### 8.1 Qué detecta

El árbol del panel agrupa los problemas por tipo. Junto a los grupos de relaciones aparecen cuatro grupos nuevos:

| Grupo | Qué señala | Cómo se trata |
|-------|-----------|---------------|
| **Fases con intervalos solapados** | Dos filas de la periodización cuyos intervalos de años se cruzan | Manual: el panel propone acortar los intervalos solo si, tras acortarlos, queda un intervalo utilizable |
| **Datación de la ficha desalineada** | El campo `datazione` de la ficha UE dice algo distinto de la `datazione_estesa` de su periodo/fase | Automático: la periodización es la fuente y la ficha es la copia, así que la copia se reescribe desde la fuente. Un campo vacío se rellena del mismo modo. Una UE sin periodo se omite, porque no hay nada que copiar |
| **Periodización con inicio posterior al fin** | `cron_iniziale` mayor que `cron_finale` | Manual: probablemente son fechas a.C. sin el signo menos — el panel propone reescribir los dos años en negativo (`-1650` en lugar de `1650`); si en cambio es un error de tecleo, intercambia los dos valores a mano |
| **Fase sin años** | Una fase cuyos años faltan o no se pueden leer | Solo se señala: no hay nada de lo que heredarlos |

Un ejemplo para los solapamientos. La base de datos de ejemplo tiene dos y ninguno lleva propuesta: las dos fases tienen intervalos **idénticos**, y cualquier recorte haría que una fase terminara antes de empezar. El panel se limita a decirlo; la decisión (fusionar las fases, corregir los años, dejarlo como está) corresponde al arqueólogo.

### 8.2 Corrección automática y sugerencias

**Correcciones automáticas y propuestas.** Las correcciones automáticas vienen **ya marcadas**; las propuestas **no**, y solo se aplican si se marca la casilla. Antes la regla era distinta: un problema cuya corrección requería una decisión humana solo podía leerse. Ahora tiene una casilla, que se deja sin marcar. Esto vale también para las dos categorías antiguas de relaciones que ofrecen una sugerencia, es decir, la contradicción directa y el ciclo estratigráfico.

Para usar el panel:

1. Seleccione en el panel el **sitio** que se desea verificar. La verificación es **por sitio**: mira solo el sitio elegido y corrige solo ese. En una base de datos con diez sitios esto importa, porque los mismos números de UE existen en todos.
2. Lea la **línea de resumen** sobre el árbol: indica cuántos problemas hay, cuántos son corregibles automáticamente y **cuántas son las propuestas que hay que marcar a mano**.
3. Abra los grupos y seleccione un problema para leer su detalle en el panel de vista previa.
4. Revise las casillas. Las correcciones automáticas ya están marcadas: desmarque las que no quiera aplicar. Marque las propuestas con las que esté de acuerdo.
5. Aplique las correcciones. Antes de escribir nada se crea una **copia de seguridad automática** (copia del archivo SQLite, o `pg_dump` para PostgreSQL en `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); la copia, que ya existía para las correcciones de los campos de periodo, ahora cubre también las cronológicas.
6. Si el resultado no convence, pulse **Annulla ultimo fix** (deshacer la última corrección): deshacer revierte también las correcciones escritas en la tabla de periodización.

### 8.3 Vista previa y copia de seguridad

**La vista previa muestra la fecha calculada.** Para cada unidad citada por un problema, el panel de vista previa muestra su fecha calculada en una línea como esta:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

La línea indica, por orden, el intervalo de años, la regla que lo produjo y la relación a lo largo de la cual viajó la restricción, junto con el nodo del que procede. Cuando los dos extremos del intervalo llegan por caminos distintos, cada extremo lleva su etiqueta (`inizio …` y `fine …`), de modo que una fecha nunca se atribuye a la relación equivocada. Hoy, en una base de datos normal, cada unidad toma sus fechas de su propio periodo, así que la mayoría de las líneas dirán `epoca`. El sentido de la línea no es sorprender, sino permitir ver **de dónde viene** una fecha.

---

## 9. Cómo leer los arcos de la matrix

Algunas decisiones del dibujo de la matrix pueden parecer extrañas, pero no son errores:

- **Una flecha nunca pasa por debajo de un nodo.** Cuando la columna de llegada está ocupada, la flecha entra en la casilla **por el lado**: es normal.
- **La igualdad no es una superposición.** Una relación «Uguale a» (Igual a) o «Si lega a» (Se une a) coloca las dos unidades en la **misma fila**, una junto a otra, unidas por **dos líneas horizontales** (el signo igual) **sin punta de flecha**.
- **Los arcos redundantes no se dibujan.** Si la UE 1 cubre la 2 y la 2 cubre la 3, la flecha de 1 a 3 no aparece, porque no añade nada. Dentro de un **ciclo**, en cambio, todos los arcos permanecen, porque un ciclo es un error que hay que ver.
- **Las líneas dicen qué relación son.** Gris y continua: la secuencia (cubre, rellena, se apoya). **Punteada verde**: un corte (`Taglia` / `Tagliato da`), sea cual sea la definición estratigráfica y en cualquier idioma. **Gruesa y negra**: la continuidad —un rombo pequeño y negro sin nombre (el nombre aparece al pasar el ratón), en la columna de su unidad, así la línea es recta. **Roja**: una flecha que sube por las bandas, es decir, una contradicción entre estratigrafía y cronología; un corte que sube es rojo **y** sigue punteado.
- **Los paradatos nunca son una línea continua.** Toman color y trazo de las reglas del Extended Matrix (`em_visual_rules.json`): pardo-rojo punteado «extraído de», naranja discontinuo «procedencia del dato», oro discontinuo «propiedad», gris discontinuo «conexión genérica», rojo tomate discontinuo «combina» (en el archivo sería continuo: es la única excepción, porque un arco hacia un documento no debe parecer una superposición).
- **El borde pardo es una estructura muraria.** Las USM —WSU, MSE, UEM, USZ, ΤΣΜ en los demás idiomas— tienen la misma casilla que las US, con el borde pardo en vez de rojo.

---

## 10. Narrativa con IA

A partir de la versión **5.13.106-alpha**, el panel de la matriz dentro de QGIS (§2.2, «Vedi la matrice») tiene dos pestañas en la columna de la derecha: **Units** (*Unità*; Unidades) —la ficha de la unidad elegida, el zoom a la geometría y los medios, como antes— y **Narrative** (*Narrativa*), nueva. La pestaña Narrative hace que una IA escriba la **historia del sitio**, un capítulo por época, y después te permite leerla, hacer que una persona la valide y exportarla a HTML, DOCX o PDF. Lee y escribe **el mismo em.json** que abre EMStudio, en el formato de la biblioteca s3dgraphy: la narrativa que ves aquí es la que EMStudio muestra en su pestaña *Narrative*.

> **Sin ajustes nuevos.** La pestaña no tiene una ventana de configuración propia: usa la IA que ya has configurado en otro lugar de pyArchInit (§10.2).

> **La IA escribe borradores, no textos definitivos.** Cada párrafo escrito por el modelo sigue siendo un «AI draft» (borrador de IA) hasta que una persona lo valida (§10.6), y en los documentos exportados lleva la marca ⚠.

Los nombres de las pestañas y de los botones de la pestaña Narrative existen en italiano y en inglés: **están en italiano si QGIS está en italiano, en inglés con cualquier otro idioma**. Aquí se dan siempre los dos. Las entradas de menú y las ventanas de diálogo del plugin (como «Vedi la matrice…» o los tres botones de §10.9) están, en cambio, solo en italiano; la traducción al español se da entre paréntesis.

### 10.1 Abrir la pestaña Narrative

1. Abre el menú **Plugins → pyArchInit - Archaeological GIS Tools** y elige la entrada **Extended Matrix → Vedi la matrice…** (Ver la matriz).
2. Elige el **sitio**.
3. pyArchInit exporta el sitio desde la base de datos a `<home>/pyarchinit_EM_folder/<sitio>.em.json` —`<home>` es `~/pyarchinit_5`, o la carpeta indicada por la variable de entorno `PYARCHINIT_HOME`— y abre el panel **«Matrice — `<sitio>`»**, acoplado a la derecha de la ventana de QGIS. El nombre del archivo es el del sitio, con los caracteres especiales sustituidos por «_» (por ejemplo, «Scavo 1» se convierte en `Scavo_1.em.json`).
4. En la columna de la derecha del panel, haz clic en la pestaña **Narrative**.

<!-- IMMAGINE: Captura del menú Plugins → pyArchInit - Archaeological GIS Tools con la entrada «Extended Matrix → Vedi la matrice…» -->
![Menú Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figura 1: La entrada «Extended Matrix → Vedi la matrice…» en el menú del plugin*

<!-- IMMAGINE: Captura del panel de la matriz acoplado a la derecha, con las pestañas Units y Narrative -->
![Panel con dos pestañas](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figura 2: El panel de la matriz con las pestañas Units y Narrative*

El archivo es **uno por sitio y permanece en el disco**: ya no está en una carpeta temporal. Es el archivo que abre EMStudio y es allí donde se escribe la narrativa. Cada vez que eliges «Vedi la matrice…» el sitio se **exporta de nuevo desde la base de datos** y el archivo se reescribe; la narrativa que ya contiene se conserva (§10.8).

A la pestaña se llega también desde otros dos lugares:

- desde la entrada **Extended Matrix → Esporta sito in em.json…** (Exportar sitio a em.json), que al final ofrece el botón «Narrativa con l'AI» (§10.9);
- desde el botón **Vedi la matrice** de la ventana «Esporta Extended Matrix» de la ficha UE (§2.2): abre el mismo panel sobre el archivo que acabas de exportar, en la carpeta que elegiste.

### 10.2 Qué IA se utiliza

En la parte superior de la pestaña Narrative una línea indica qué IA va a usar: **«Model: `<model>` (`<where it comes from>`)»**, seguida del recordatorio sobre EMStudio. Si no encuentra ninguna, escribe **«No AI configured: set it in the US form with “Report” (AI provider) or with “Query AI Database”.»** (no hay ninguna IA configurada: configúrala en la ficha UE con el botón «Report» (Provider AI) o con «Query AI Database») y los botones **Generate with AI** (Generar con IA) y **Regenerate chapter** (Regenerar capítulo) quedan deshabilitados.

La pestaña lee los ajustes de IA **ya guardados** por las demás ventanas de pyArchInit, en este orden, y usa **el primero** que tiene un modelo y —para los proveedores en red— la clave API:

| # | Dónde se configura | Cómo la llama la pestaña (en / it) |
|---|--------------------|-------------------------------------|
| 1 | Ficha UE, botón «Report» → ventana «Generatore di Report» (Generador de informes), grupo «Provider AI» | Report generator of the US form / Generatore di Report della scheda US |
| 2 | Ficha UE, botón «Query AI Database» | Query AI Database / Query AI Database |
| 3 | Ventana palimpsestr, botón «Report AI (analisi descrittiva)…», selector «Provider AI» | Palimpsest report / Relazione Palimpsest |
| 4 | Ventana «Generazione SQL con AI» (texto a SQL: véase el tutorial 30) | Text to SQL / Testo in SQL |

Los proveedores son los de los selectores «Provider AI»: **OpenAI** y **Anthropic (Claude)** en red, con la clave API escrita en el campo «API key»; **Ollama** y **LM Studio** en tu propio ordenador, sin clave. El selector guarda tu elección en cuanto la cambias. Si quieres otro modelo, cámbialo en la ventana que la pestaña indica entre paréntesis (o en una que aparezca antes en la lista). La pestaña vuelve a leer los ajustes **cuando se abre el panel**: tras cambiarlos, abre de nuevo la matriz.

### 10.3 La pestaña Narrative

```
┌─ Units ─┬─ Narrative ───────────────────────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the                        │
│ file open, close it first: the last writer wins.                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                                        │
│ Early 15th century — AI draft                                                       │
│ 15th century — endorsed                                                             │
│ Modern age — AI draft, truncated                                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                                    │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]                                │
│ [Prepare the chapters]  [Show on the map]  [Export…]  [Open in EMStudio]  [Cancel]* │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

\* La línea de progreso y el botón «Cancel» (Cancelar) solo se ven mientras la IA escribe. En este diagrama las filas de la lista son las del sitio de ejemplo.

<!-- IMMAGINE: Captura de la pestaña Narrative con la lista de capítulos, el texto del capítulo elegido y los siete botones -->
![Pestaña Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figura 3: La pestaña Narrative*

De arriba abajo:

- **la línea de estado**: el modelo en uso (§10.2) y el recordatorio *«If EMStudio has the file open, close it first: the last writer wins.»* (si EMStudio tiene el archivo abierto, ciérralo antes: gana el último que escribe);
- **la lista de capítulos**, una fila por capítulo: *Título — estado*. Un archivo de una versión anterior, dividido por sondeos, muestra todos los grafos: cada fila va precedida del nombre del grafo entre corchetes, por ejemplo `[Saggio A] 15th century — AI draft`;
- **el texto del capítulo elegido**: la prosa, con las unidades citadas por su nombre; los nombres son **enlaces**: un clic muestra la unidad en el mapa (§10.10); bajo el párrafo en el que una unidad se nombra por primera vez aparecen hasta dos fotos suyas (§10.11). Si el capítulo todavía no tiene prosa, ves su marcador de posición «[to be written: …]»;
- **la línea de progreso**, solo durante la generación: «Chapter 3 of 9 · 15th century»;
- **los botones**, en dos filas.

El resultado de cada operación aparece en la barra de mensajes de QGIS, con el título «Narrative».

Cuando el archivo **todavía no tiene narrativa**, la lista está vacía y un texto dice: *«No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it.»* (no hay narrativa en el archivo: “Prepare the chapters” crea el esquema, con N capítulos entre épocas y actividades; “Generate with AI” la escribe).

#### Los estados de un capítulo

| Estado (en / it) | Qué significa |
|------------------|---------------|
| **to be written** / da scrivere | El capítulo solo tiene el marcador «[to be written: …]». |
| **AI draft** / bozza AI | Hay prosa escrita por el modelo que ninguna persona ha validado. Basta un párrafo: si el capítulo tiene aunque sea un solo párrafo sin validar, este es su estado, aunque haya otra prosa. |
| **endorsed** / convalidato | Toda la prosa de la IA ha sido validada por una persona. |
| **written** / scritto | Prosa escrita por una persona (en EMStudio). |
| **truncated** / troncato | Se añade al estado (por ejemplo «AI draft, truncated»): el modelo se detuvo porque alcanzó el límite de longitud y el texto termina a medias. |

#### Los botones

| Botón (en) | En italiano | Qué hace |
|------------|-------------|----------|
| **Generate with AI** | Genera con l'AI | Escribe, **de uno en uno**, todos los capítulos que todavía están «to be written» —primero la **Presentation**, luego los de época (y de actividad)—; los ya escritos no se tocan. Si todavía no hay narrativa, crea primero el esquema. Muestra el progreso y el botón **Cancel**. Habilitado solo con un archivo abierto y una IA configurada. |
| **Regenerate chapter** | Rigenera capitolo | Reescribe **el capítulo elegido** en la lista: el borrador de IA sin validar se sustituye —pero solo cuando el modelo ha respondido: si la llamada falla, el borrador anterior se queda— y los bloques ya validados se mantienen. Se habilita cuando eliges la Presentation o un capítulo de época o de actividad y hay una IA configurada; para «Where it is» permanece deshabilitado. |
| **Endorse…** | Convalida… | Abre un menú con «This chapter» y «All chapters», y luego pregunta quién valida (§10.6). Habilitado cuando hay una narrativa. |
| **Prepare the chapters** | Prepara i capitoli | Crea **solo el esquema** de los capítulos, sin IA: funciona aunque no haya ninguna IA configurada, para poder escribir a mano en EMStudio. No toca la prosa ya escrita y añade los capítulos de las épocas nuevas. Resultado: «Chapters prepared: N.» (Capítulos preparados: N). |
| **Show on the map** | Mostra sulla mappa | Selecciona y encuadra en el mapa, **todas juntas**, las unidades de las que habla el capítulo elegido (§10.10): las citadas en la prosa o, si el capítulo todavía no está escrito, todas las de su banda. Habilitado solo si al menos una de las unidades de las que habla el capítulo elegido es una fila de la ficha UE. |
| **Export…** | Esporta… | Guarda la narrativa en HTML (con el mapa interactivo del sitio, §10.7), DOCX o PDF imprimible (§10.7), con las fotos de las unidades citadas cuando las hay (§10.11). Habilitado cuando hay una narrativa. |
| **Open in EMStudio** | Apri in EMStudio | Abre el em.json en EMStudio. Si EMStudio no está, la barra de mensajes remite a la entrada de menú **Extended Matrix → Installa EMStudio…** (Instalar EMStudio). |
| **Cancel** | Annulla | Aparece solo durante la generación: la IA se detiene **después del capítulo en curso** y lo que se ha escrito se guarda. |

Durante la generación todos los botones están deshabilitados salvo **Cancel**.

### 10.4 Qué escribe la IA

**Qué capítulos.** El esquema es el de la biblioteca s3dgraphy (la plantilla «site_story»):

- Desde la **5.13.110-alpha** la **Presentation** (Presentación) es un capítulo canónico que la IA escribe como los demás, a partir de un briefing del sitio entero (ver «El briefing de la Presentation» más abajo); antes se quedaba como marcador. **Where it is** (Dónde está) es el otro capítulo canónico y se queda como marcador «[to be written: …]» para escribirlo a mano en EMStudio: nace de la posición del sitio y la biblioteca le pone el mapa. Existe solo si el grafo lleva una posición geográfica. La IA no lo genera.
- **Un capítulo por época** (periodo/fase) que tenga unidades, de la más antigua a la más reciente. El título es el nombre de la época, es decir, la «Datazione estesa» (Datación Extendida) de la periodización; si falta, sale un nombre genérico como «Period 8 Phase 1»: rellénala en la Ficha de Periodización para obtener títulos legibles. Una unidad aparece en el capítulo de la época en que nace y en los de las épocas en que sobrevive.
- **Un capítulo por actividad**, si el grafo contiene grupos de actividad. Un sitio exportado desde la base de datos normalmente no los tiene —el campo Actividad de la ficha UE viaja como propiedad de la unidad— y entonces los capítulos son los de época.

**Qué recibe el modelo.** Para cada capítulo de época o de actividad, un *briefing* con, por cada unidad: nombre, tipo y descripción; los campos rellenados de la ficha UE (definición estratigráfica e interpretativa, interpretación, periodo y fase, datación, actividad, estructura, sondeo, ambiente, sector, área); las épocas; **las relaciones estratigráficas** con las demás unidades (cubre, corta, rellena, se apoya, igual a…), con sus nombres; y, si las hay, las fuentes documentales vinculadas. Las unidades se enumeran **de la más antigua a la más reciente**, siguiendo las relaciones. Por encima de **80 unidades** por capítulo, el briefing se recorta a las primeras 80. Tiene además un tope de longitud (unos 25.000 caracteres): pasado ese límite, se acortan los textos largos de las fichas, se eliminan las relaciones repetidas y las cadenas de evidencias y, si aún no basta, se omiten las unidades más recientes. En ambos casos se informa al modelo de cuántas unidades faltan.

**Las reglas.** El modelo recibe las cinco reglas de la biblioteca: escribir solo lo que el contexto respalda (nada de fechas, materiales, funciones o eventos inventados); mantener la incertidumbre (una unidad virtual es una hipótesis, no un hecho); no citar fuentes que no estén; escribir prosa continua, sin listas ni títulos; decir abiertamente cuándo el contexto es demasiado pobre. Pide de uno a tres párrafos.

**El briefing de la Presentation.** La Presentation no tiene unidades propias: el modelo recibe un briefing del **sitio entero**, tomado del grafo y no de la base de datos, con el nombre del sitio; la cadena de topónimos (país → región → provincia → municipio); los lugares de la ficha UE (áreas, sectores, sondeos, ambientes); las épocas de la más antigua a la más reciente, cada una con cuántas unidades están presentes en ella (una misma unidad puede estar en varias épocas, así que la suma puede superar el total); cuántas unidades hay y de qué tipo, y cuántas relaciones estratigráficas; los documentos; las personas nombradas en las fichas UE; y los títulos de los capítulos de la historia. Sus instrucciones son las de la Presentation, no las cinco reglas de arriba: piden de dos a cuatro párrafos que digan qué es el sitio y dónde está, qué épocas abarca la historia, cómo se lee esta historia (un capítulo por época y por actividad, con las unidades citadas por su nombre y los borradores marcados como tales hasta que una persona los valide) y en qué fuentes se apoya; que use solo el briefing, sin inventar fechas ni hechos, y que deje fuera un dato que parezca raro en lugar de comentarlo. La prosa va **al principio** del capítulo; las fichas de las fuentes (los documentos) quedan después, y los marcadores «[to be written: a presentation of …]» y «[to be written: how this account is to be read…]» desaparecen.

**El idioma.** La prosa está en el **idioma de la narrativa**, que se fija cuando se crea el esquema por primera vez: **italiano si en ese momento QGIS está en italiano, inglés con cualquier otro idioma** (el modelo recibe sus instrucciones solo en esos dos idiomas). Una narrativa ya creada conserva su idioma aunque después cambies el de QGIS. Lo mismo vale para los títulos de los capítulos canónicos y para los marcadores.

**Cómo se guarda.** En el formato de la biblioteca, el mismo que lee EMStudio: un nodo de narrativa (`NarrativeNode`) que contiene los capítulos; cada párrafo escrito por el modelo es un bloque «AI draft» atribuido al **autor de IA** de ese modelo; el **prompt** utilizado se registra como un extractor vinculado a las fuentes, de modo que se puede rastrear qué se pidió. Las unidades citadas en el texto son **menciones** (`[[name]]`): en el archivo permanecen vinculadas al nodo de la unidad, y en la pestaña y en las exportaciones aparecen con su nombre. Una mención que no corresponde a ninguna unidad del grafo se reduce a simples palabras, sin corchetes.

**Costes y tiempos.** Se llama al modelo **una vez por capítulo**, la Presentation incluida. Con un proveedor en red cada llamada tiene un coste y un tiempo de espera (en las pruebas con un modelo en red, unas decenas de segundos por capítulo: un sitio con una decena de épocas tarda unos minutos); con Ollama o LM Studio no se paga nada, pero los tiempos dependen de tu ordenador.

### 10.5 Paso a paso

1. Abre la matriz del sitio (§10.1) y haz clic en la pestaña **Narrative**. Comprueba arriba **qué modelo** va a usar.
2. **Cierra EMStudio** si tiene el archivo abierto: pyArchInit y EMStudio escriben el mismo archivo, y gana el último que escribe.
3. Opcional: haz clic en **Prepare the chapters** para ver el esquema, sin IA.
4. Haz clic en **Generate with AI**. Observa el progreso: la Presentation, si todavía está «to be written», va primero («Chapter 1 of 9 · Presentation»), luego los capítulos de época («Chapter 3 of 9 · …»); puedes seguir usando QGIS. Al final la barra de mensajes dice, por ejemplo, *«7 chapters generated, 1 failed: Modern age — …»* (7 capítulos generados, 1 fallido), con *«(cancelled)»* si has cancelado, y la lista se recarga: los capítulos escritos están en «AI draft».
5. **Lee**: elige un capítulo tras otro y lee el texto bajo la lista. Contrástalo con la estratigrafía: es un borrador construido a partir de los datos de la ficha UE. Para ver dónde están las unidades de las que habla, haz clic en sus nombres o usa **Show on the map** (Mostrar en el mapa; §10.10).
6. Si un capítulo no te convence, elige su fila y haz clic en **Regenerate chapter**. El nuevo borrador **sustituye** al anterior sin validar: si quieres conservar la versión anterior, expórtala antes. Si un capítulo está «truncated», regenéralo **antes** de validarlo.
7. Cuando un capítulo está bien, haz clic en **Endorse…** (§10.6).
8. Con **Export…** exporta a HTML, DOCX o PDF (§10.7); con **Open in EMStudio** ábrelo en EMStudio para escribir a mano «Where it is» y pulir el resto.
9. Más adelante puedes volver a abrir la matriz: la narrativa se conserva (§10.8).

<!-- IMMAGINE: Captura de la generación en curso: la línea de progreso «Chapter 3 of 9 · …» y el botón Cancel -->
![Generación en curso](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figura 4: Generación en curso, con la línea de progreso y el botón Cancel*

Un capítulo que falla no detiene a los demás: el resumen dice cuáles. Para reintentar basta con volver a hacer clic en **Generate with AI**, que escribe solo los capítulos todavía «to be written».

### 10.6 Validar: quién firma

Validar significa que una **persona** asume la responsabilidad del texto escrito por el modelo. Nunca ocurre por sí solo: ni al generar, ni al guardar.

1. Haz clic en **Endorse…** (Validar…). Se abre un pequeño menú: **«This chapter»** (Este capítulo) —habilitado solo si el capítulo elegido es un «AI draft»— o **«All chapters»** (Todos los capítulos), es decir, todos los borradores de IA aún sin validar, en todos los grafos del archivo. La Presentation se valida como cualquier otro capítulo: elígela en la lista y «This chapter» la valida por sí sola.
2. Una ventana pregunta **«Who endorses? Pick an author or type a new name.»** (¿Quién valida? Elige un autor o escribe un nombre nuevo). La lista contiene los **autores humanos que ya están en el grafo** —las personas nombradas en la ficha UE como compilador (*schedatore*), director UE y responsable UE— y puedes escribir un nombre nuevo, que se convierte en un nuevo autor del grafo.
3. La barra de mensajes dice **«N blocks endorsed by `<name>`.»** (N bloques validados por la persona elegida), o «Nothing to endorse.» (Nada que validar). El archivo se guarda.

<!-- IMMAGINE: Captura del menú Endorse… («This chapter» / «All chapters») y de la ventana para elegir el autor -->
![Validar](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figura 5: Validar: el menú y la elección del autor*

Los bloques pasan de «AI draft» a «endorsed». En el documento exportado la persona aparece entre los responsables («a cura di», a cargo de) y el modelo como asistente («con l'assistenza di», con la asistencia de), y los párrafos validados ya no llevan la marca ⚠. Regenerar no borra los bloques validados: una firma es un acto y no se pierde al reescribir.

### 10.7 Exportar a HTML, DOCX o PDF

Haz clic en **Export…**: se abre la ventana para guardar, con tres formatos: «HTML page» (página HTML; `.html`), «Word document» (documento Word; `.docx`) y «Printable PDF» (PDF imprimible; `.pdf`). El nombre propuesto es `<sitio>_narrativa`, sin extensión, en la carpeta del em.json: la extensión la pone el formato elegido en el filtro de la ventana; una extensión escrita a mano (`.html`, `.docx` o `.pdf`) prevalece sobre el filtro. La barra de mensajes lo confirma: «Narrative exported to `<path>`» (narrativa exportada, con la ruta del archivo).

El documento contiene:

- el título de la narrativa (por ejemplo «Scavo archeologico — the story of the site»; en español, «la historia del sitio»), los responsables («a cura di») y el modelo como asistente («con l'assistenza di»);
- para cada capítulo, primero la prosa, con las unidades citadas por su nombre, y después la lista de las unidades del capítulo; para las unidades citadas que tienen fotos, una tira de fotos ocupa el lugar de su línea (§10.11);
- **el mapa del sitio** (desde la 5.13.115-alpha, solo en el HTML), en un recuadro fijo: a la derecha en las pantallas anchas, arriba en el teléfono. Con el mapa la página se ensancha (desde la 5.13.116-alpha) y el texto mantiene una columna legible. En reposo muestra todas las unidades del grafo en gris claro; un clic en el nombre de una unidad en el texto muestra **solo las unidades del periodo de ese capítulo** como contornos con el número encima, la unidad pulsada **coloreada**, y encuadra el grupo; un clic en el título de un capítulo hace lo mismo, sin la unidad coloreada. La línea bajo el mapa indica el periodo y cuántas unidades; «whole site» (todo el sitio) vuelve a la vista completa. Las geometrías proceden de las vistas US y USM de la base de datos del proyecto en el momento de la exportación (sitio del grafo, unidades asociadas por área y número): una unidad citada pero sin dibujo tiene el enlace y nada en el mapa; sin una base de datos conectada, el documento no lleva mapa;
- al final, la sección **Fonti** (fuentes): los documentos en los que se apoya el relato y la entrada «Prompt», que remite al prompt registrado en el archivo.

Algunas cosas que conviene saber:

- **los borradores sin validar entran**, cada uno precedido de «⚠︎ non validato da una persona» (no validado por una persona), y el encabezado indica cuántos bloques están en este estado. Para un documento sin marcas, valida primero (§10.6). En el HTML el borrador se lee como el resto del texto, con la misma tipografía y el mismo fondo: encima del párrafo está la línea de aviso y a la izquierda un filete ámbar. En Word y en el PDF el aviso va delante del párrafo (en el PDF, en una línea propia y sin el signo ⚠, §10.11);
- **entran todos los capítulos**, incluso los que todavía están «to be written»: su marcador «[to be written: …]» permanece en el texto;
- la prosa va **al principio** del capítulo, antes de la lista de las unidades; en una narrativa escrita con una versión anterior puede estar todavía al final, y se coloca en su sitio volviendo a exportar el sitio (§10.8) o con **Prepare the chapters** (Preparar los capítulos);
- las figuras que un autor ha previsto en EMStudio (por ejemplo la matriz de una época) no las dibuja la exportación de pyArchInit: en el documento queda un marcador;
- el HTML es un único archivo autocontenido (las fotos también van incorporadas, y el mapa es un SVG dentro del archivo, sin bibliotecas externas: se abre también en el teléfono sin red); el DOCX se abre con Word o LibreOffice y requiere el paquete `python-docx`, y el PDF la biblioteca ReportLab (§10.11): ambos están entre los requisitos del plugin.

<!-- IMMAGINE: Captura del documento HTML exportado: un capítulo con un borrador precedido de «⚠︎ non validato da una persona» -->
![Documento HTML exportado](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figura 6: El documento HTML exportado, con un borrador sin validar marcado*

### 10.8 Volver a exportar el sitio: la narrativa se conserva

Volver a exportar el sitio desde la base de datos —con **Vedi la matrice…**, con **Esporta sito in em.json…** o con la ventana «Esporta Extended Matrix» de la ficha UE— **conserva la narrativa** que ya está en el archivo de destino: prosa, validaciones, autor de IA y prompts. Las épocas que han aparecido entretanto reciben un capítulo «to be written». Un aviso lo dice: **«Narrative kept from the previous file (N chapters).»** (Narrativa conservada del archivo anterior, N capítulos). Lo ves en la barra de mensajes con «Vedi la matrice…», en el resumen de la ventana «Esporta Extended Matrix» y, con «Esporta sito in em.json…», en los detalles de la ventana final.

Las **demás modificaciones** hechas al archivo en EMStudio —posiciones de los nodos, descripciones reescritas— **no sobreviven**, como antes: el archivo se regenera desde la base de datos. Solo se conserva la narrativa.

Antes de reescribir un archivo que contiene una narrativa, pyArchInit hace una **copia de seguridad** al lado: `<sitio>.em.json.bak` (cada nueva exportación sustituye la copia anterior).

Si el archivo de antes estaba dividido por sondeos (las versiones hasta la 5.13.108-alpha podían exportar un grafo por sondeo), en la primera reexportación el archivo nuevo tiene **un solo grafo** para todo el sitio: los grafos tienen nombres distintos y la narrativa **no puede pasar** al archivo nuevo. Un aviso lo dice: *«The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …»* (la narrativa del archivo anterior —grafos: …— no pasó al archivo nuevo —grafos: …—: la forma del archivo ha cambiado; copia de seguridad en …). El texto no se pierde: está en la copia `.bak`, que, sin embargo, se sustituye en la próxima reexportación de un archivo que contenga una narrativa: guárdala en un lugar seguro. Si necesitas la narrativa vieja, abre esa copia (renombrándola como un archivo `.em.json` con otro nombre); si no, genera de nuevo los capítulos en el archivo nuevo (§10.5). Desde la 5.13.109-alpha el archivo tiene siempre un solo grafo y la narrativa pasa de una reexportación a la siguiente.

Si el archivo anterior no se puede leer (por ejemplo, un archivo que quedó a medias), la exportación continúa igualmente: el archivo ilegible se **renombra** como `<sitio>.em.json.broken` y un aviso dice *«The previous file cannot be read (…): its narrative, if any, was not kept.»* (el archivo anterior no se puede leer: su narrativa, si la había, no se conservó).

> **La narrativa no está en la base de datos de pyArchInit: vive solo en el em.json.** Una copia de seguridad de la base de datos no la copia. Copia de vez en cuando la carpeta `pyarchinit_EM_folder`.

### 10.9 Desde la entrada «Esporta sito in em.json…»

La entrada **Extended Matrix → Esporta sito in em.json…** escribe el mismo archivo `<sitio>.em.json` en `pyarchinit_EM_folder`. Al final muestra «Esportato `<percorso>`» (Exportado), con los recuentos de nodos, aristas y avisos (el texto de los avisos está en los detalles de la ventana), y **tres botones**:

| Botón | Qué hace |
|-------|----------|
| **Apri in EMStudio** (Abrir en EMStudio) | Abre el archivo en EMStudio; si no está instalado, ofrece instalarlo. |
| **Narrativa con l'AI** (Narrativa con IA) | Aparece **solo si hay una IA configurada** (§10.2): abre el panel de la matriz ya en la pestaña Narrative. |
| **Chiudi** (Cerrar) | Cierra la ventana. |

<!-- IMMAGINE: Captura de la ventana final de «Esporta sito in em.json…» con los tres botones -->
![Exportar sitio a em.json: tres botones](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figura 7: La ventana final de «Esporta sito in em.json…»*

### 10.10 Las unidades en el mapa

A partir de la versión **5.13.108-alpha**, la pestaña Narrative lleva al **mapa de QGIS** las unidades de las que habla un capítulo, de dos maneras:

- **Una sola unidad: haz clic en su nombre.** En el texto del capítulo elegido, los nombres de las unidades citadas son **enlaces**: un clic selecciona esa unidad en la capa UE cargada y encuadra el mapa sobre ella, con un parpadeo. No abre nada.
- **Todas juntas: «Show on the map»** (*Mostra sulla mappa*; Mostrar en el mapa), en la segunda fila de botones, entre «Prepare the chapters» (Preparar los capítulos) y «Export…» (Exportar…). Selecciona y encuadra a la vez todas las unidades de las que habla el capítulo elegido: las citadas en la prosa o, si la prosa no cita ninguna (por ejemplo, porque el capítulo todavía no está escrito), todas las unidades de su banda (la época). La selección es una sola por capa —sustituye a la que había— y el encuadre abarca todas las geometrías encontradas, que parpadean.

<!-- IMMAGINE: Captura de QGIS con las unidades del capítulo seleccionadas en el mapa y, arriba, la barra de mensajes «Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.» -->
![Las unidades del capítulo en el mapa](images/36_extended_matrix_s3dgraphy/09_unita_sulla_mappa.png)
*Figura 8: Las unidades de las que habla un capítulo, seleccionadas en el mapa, y la barra de mensajes*

Hace falta que una capa con las geometrías de las UE esté ya cargada en el proyecto, por ejemplo la **vista US** de pyArchInit: la pestaña la busca entre las capas cargadas, como el botón «Zoom sulla geometria» (Zoom a la geometría) de la pestaña Units (tutorial 01), reconociendo las unidades por los campos `sito`, `area` y `us`. **El proyecto no se modifica**: no se añade ninguna capa, solo cambian la selección y el encuadre del mapa. Desde la **5.13.110-alpha**, si varias capas llevan los mismos campos —como la vista US (polígonos) y la vista de cotas (puntos)—, la pestaña prueba primero la geometría más plena: polígonos, luego líneas, luego puntos; el orden de las capas en la leyenda solo cuenta si todo lo demás es igual. Vale también para el botón «Zoom sulla geometria»: ya no hace falta poner la vista US al principio de la leyenda.

La barra de mensajes («Narrative») dice qué se ha encontrado, por ejemplo «Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.» (5 de 6 unidades resaltadas en «US view», 7 geometrías; no dibujadas: 1.US9). El nombre entre comillas es el de la capa donde se han encontrado las unidades, tal como aparece en el panel de capas de QGIS; una unidad puede tener más de una geometría, así que las geometrías pueden ser más que las unidades. Solo se buscan las unidades que son filas de la ficha UE: un documento o un nodo de continuidad no tiene geometría y no entra en el recuento. Si las unidades no dibujadas son más de cinco, los nombres se detienen en las cinco primeras, seguidas de «…» y el total.

Un clic en un nombre que no es una fila de la ficha UE no encuentra nada, y la barra de mensajes lo dice. Si ninguna capa cargada lleva los campos para reconocer las unidades, el mensaje lo dice: carga la vista US (§10.13).

### 10.11 Las fotos de las unidades y el PDF

A partir de la versión **5.13.108-alpha**, la narrativa muestra también las **fotos** de las unidades de las que habla —en el texto de la pestaña y en las exportaciones— y se puede guardar además como **PDF imprimible**.

**En el texto del capítulo.** Bajo el párrafo en el que una unidad se nombra por primera vez aparecen **hasta dos miniaturas** de sus medios: son las mismas de la pestaña Units, leídas de la carpeta de miniaturas del proyecto, y debajo, en letra pequeña, están el nombre de la unidad y los nombres de los medios. Si la unidad se vuelve a nombrar en el mismo capítulo, las fotos no se repiten.

**En las exportaciones.** En los tres formatos, para cada unidad citada en la prosa que tiene imágenes en el disco, una **tira con una o dos fotos juntas** ocupa el lugar de la línea de texto de la unidad, con el nombre de la unidad como pie de foto: se usa la copia reducida si existe y, si no, la miniatura. Las unidades no citadas en la prosa se quedan como una línea de texto. Las fotos van incorporadas al archivo: el HTML y el DOCX los escribe la biblioteca s3dgraphy; el PDF, pyArchInit.

**El PDF imprimible.** Es un documento A4 que pyArchInit escribe con ReportLab, con la fuente Cambria como los otros PDF del plugin (si el archivo de la fuente no está en la carpeta `bin` de pyArchInit, usa Helvetica). Contiene el título, los responsables («edited by») y el modelo como asistente («with the assistance of»); arriba, si hay borradores sin validar, aparece además un aviso con su número; después todos los capítulos, como en los otros formatos, cada uno con su prosa —las unidades citadas escritas por su nombre, y delante de cada párrafo sin validar una línea «non validato da una persona» (no validado por una persona), sin el signo ⚠— seguida de las fotos con su pie y de las demás unidades en letra pequeña; al final, las fuentes. En el pie de página están «Generated by pyArchInit on …» (generado por pyArchInit el …) con la fecha y el número de página.

<!-- IMMAGINE: Capturas de pantalla juntas: el texto de un capítulo con las miniaturas bajo la primera mención de una unidad y una página del PDF imprimible con la tira de fotos y su pie -->
![Fotos de las unidades en el texto y en el PDF](images/36_extended_matrix_s3dgraphy/10_foto_e_pdf.png)
*Figura 9: Las fotos de las unidades en el texto del capítulo y en una página del PDF*

**Qué hace falta.** Las fotos no están en el em.json: se leen de la base de datos y de las carpetas del proyecto. Hacen falta, pues, la base de datos vinculada (la matriz abierta desde el proyecto), las rutas **Thumbnail path** e **Image resize** fijadas en la configuración (tutorial 01) y los archivos en el disco; para el texto basta la carpeta de miniaturas. Las imágenes en un almacén remoto no se usan. Si falta algo no hay ningún mensaje: las fotos simplemente no aparecen y la exportación funciona igualmente (§10.13).

### 10.12 Advertencias

- **Cierra EMStudio antes de generar o validar.** Si EMStudio tiene el archivo abierto, gana el último que escribe.
- **Una IA escribe solo a partir de lo que encuentra en el grafo, y puede equivocarse.** Las reglas la frenan, no la hacen infalible: lee cada capítulo antes de validarlo.
- **Con un proveedor en red, los datos salen de tu ordenador.** El briefing de cada capítulo (nombres, definiciones, descripciones y relaciones de las unidades) y el de la Presentation (nombre del sitio, topónimos, lugares, épocas, documentos y los nombres de las personas nombradas en las fichas UE) se envían al servicio elegido; con Ollama o LM Studio se quedan en local.
- **El archivo se escribe al final.** La generación guarda cuando termina, incluso si la has cancelado: no cierres QGIS mientras la IA escribe. El guardado es seguro: el archivo se escribe al lado, se vuelve a leer y solo entonces sustituye al verdadero; si algo sale mal, **el archivo anterior se queda como estaba**.
- **No vuelvas a abrir la matriz mientras la IA escribe.** La pestaña se queda en el archivo anterior y avisa: *«Generation in progress: wait for it to finish, or press Cancel, before changing file.»* (generación en curso: espera a que termine, o pulsa Cancel, antes de cambiar de archivo).
- **El texto se edita en EMStudio**, no en pyArchInit.
- La narrativa y los nodos que la sostienen (autor de IA, prompts) **no aparecen en el dibujo de la matriz**.

### 10.13 Resolución de problemas

| Mensaje (en / it) | Causa | Solución |
|-------------------|-------|----------|
| «No AI configured…» / «Nessuna AI impostata…» | Ninguna de las cuatro ventanas de §10.2 tiene un modelo (ni, para OpenAI y Anthropic, la clave API). | Configura proveedor y modelo —y la clave— en una de esas ventanas y luego **vuelve a abrir la matriz**: la pestaña vuelve a leer los ajustes solo cuando se abre. Incluso sin IA puedes preparar los capítulos, validar, exportar y abrir EMStudio. |
| «No narrative in the file…» / «Nessuna narrativa nel file…» | El archivo todavía no tiene narrativa (es normal la primera vez). | Haz clic en **Prepare the chapters** (esquema) o en **Generate with AI** (esquema y prosa). El número N cuenta los capítulos de época y de actividad que tendrá el esquema (una época sin unidades no tiene ninguno); el mensaje «Chapters prepared» cuenta también «Presentation» y, si existe, «Where it is». «Generate with AI» escribe además la «Presentation», que N no cuenta: el progreso cuenta un capítulo más. |
| «EMStudio is not installed…» / «EMStudio non risulta installato…» | No se encontró el programa en el ordenador. | Usa la entrada de menú **Extended Matrix → Installa EMStudio…** (tiene este nombre con cualquier idioma de QGIS). |
| «truncated» / «troncato» junto al estado | El modelo se detuvo en el límite de longitud y el texto termina a medias. | Antes de validar, usa **Regenerate chapter**; si se repite, termina el capítulo en EMStudio. |
| «N chapters generated, M failed: `<title>` — `<reason>`» / «N capitoli generati, M falliti: …» | El proveedor rechazó la petición (clave no válida, cuota, modelo no disponible) o el servidor local no responde. «the model wrote nothing» (el modelo no escribió nada) significa que la respuesta estaba vacía. | Elimina la causa y haz clic de nuevo en **Generate with AI**: escribe solo los capítulos que han quedado «to be written». |
| «The previous file cannot be read (…)» / «Il file precedente non si legge (…)» | En la reexportación, el archivo existente no era un em.json legible. | La exportación continuó: el archivo ilegible se conservó al lado del nuevo como `….broken`, y la narrativa que contenía, si la había, no pasó al archivo nuevo. Si la necesitas, recupérala de ese archivo o de una copia de seguridad. |
| «The previous file's narrative (graphs: …) did not travel into the new file…» / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | El archivo de antes estaba dividido por sondeos (versiones hasta la 5.13.108-alpha): los grafos tienen nombres distintos y la narrativa no puede pasar. | El archivo anterior está en la copia `.bak`: ábrela si necesitas la narrativa vieja, o genera de nuevo los capítulos en el archivo nuevo. |
| «Could not write … The previous file is intact.» / «Non sono riuscito a scrivere … Il file precedente è intatto.» | Falló el guardado (disco lleno, archivo bloqueado, permisos). | Soluciona el problema y repite: los capítulos generados en esa sesión no se habían guardado. |
| «DocX export needs python-docx — install the extra: …» (siempre en inglés) | El paquete `python-docx` no está instalado en el Python de QGIS: solo hace falta para el DOCX. | Instala `python-docx` (es uno de los requisitos del plugin) o exporta a HTML, que no necesita nada. |
| «None of the loaded layers has the fields to recognise the units…» / «Nessuno dei layer caricati porta i campi per riconoscere le unità…» | El proyecto abierto no tiene ninguna capa con los campos `sito`, `area` y `us` de las unidades (por ejemplo, la vista US de pyArchInit): la pestaña busca solo entre las capas ya cargadas. | **Carga la vista US** de pyArchInit (o una capa con los mismos campos) en el proyecto y vuelve a hacer clic en el nombre o en **Show on the map** (Mostrar en el mapa). La pestaña no añade capas por sí sola. Desde la 5.13.110-alpha no hace falta ponerla al principio de la leyenda: con los mismos campos la pestaña prueba primero los polígonos (§10.10). Cargada desde la ficha UE con un estilo elegido (ventana «Style Choice», tutorial 14), la vista US lleva además el número de la unidad dentro de un círculo. Desde la 5.13.111-alpha, la vista de cotas (puntos), cargada desde la ficha UE, lleva también la cota (dos decimales) encima del símbolo. El estilo y las etiquetas de la vista se establecen en la ventana «View styles» (entrada de menú «View styles…», tutorial 14); desde la 5.13.112-alpha, un predeterminado guardado allí manda en la carga. |
| Ningún mensaje: las fotos no aparecen en el texto del capítulo ni en las exportaciones | Las fotos se leen de la base de datos del proyecto y de sus carpetas, y falta algo: la base de datos no está vinculada (la matriz se abrió sin ella), la ruta **Thumbnail path** no existe en este ordenador o es un almacén remoto, los archivos no están en el disco, o la unidad no es una fila de la ficha UE o no tiene medios. | Mira la pestaña **Units**: si allí la unidad muestra sus miniaturas, las encontrarás también aquí. Si no, abre la matriz desde el proyecto, comprueba **Thumbnail path** e **Image resize** en la configuración (tutorial 01) y que los archivos estén en el ordenador: las imágenes en un almacén remoto no entran. La exportación funciona igualmente, sin fotos. |

---

## Referencias

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositorio pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
