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

## 5. yEd-aware Import — importar graphmls editats externament (5.8.x)

A partir de **5.8.0-alpha** el bridge és **bidireccional també per a graphmls creats directament a yEd** (és a dir, sense passar abans per una exportació pyarchinit). Pyarchinit reconeix automàticament els graphmls «yEd-raw» — aquells que no porten data keys `pyarchinit.*` — i els importa mitjançant un dispatch dedicat que mapeja el prefix del label del node → tipus estratigràfic, reconeix files de TableNode com a períodes, recorre els group folder com a dimensions arqueològiques i deixa que l'usuari triï una política per a les edges que toquen folders.

### 5.1 Desplegament en 6 fites

| Fita | Tag | Què afegeix |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag de flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` amb 13 valors (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate des de files de TableNode) + `yed_group_walker.py` (FolderCandidate amb auto-dimension des del prefix del label: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orquestrador `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + sentinel `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` amb 5 pàgines (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + persistència sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Aquesta documentació + dev-log + CHANGELOG. |

### 5.2 Com funciona — flux d'usuari

1. **Obre un graphml a QGIS via el menú Import GraphML** (mateix path que el flux pyarchinit-projected existent).
2. Pyarchinit detecta automàticament que és yEd-raw (sense keys `pyarchinit.*`) → fa dispatch al nou branch en lloc de caure al path legacy.
3. S'obre l'assistent `YedImportDialog` amb **5 pàgines**:
   - **1/5 Classifier** — taula amb una fila per leaf node. Cada fila mostra `label` + `auto_kind` (p. ex. `us_real` / `usv_virtual` / `property`) + un combobox d'override `user_kind`. El botó **Accepta auto** reinicia cada fila al seu `auto_kind` (esborra tots els overrides).
   - **2/5 Periods** — una fila per TableNode-row parsejada, columnes editables `periodo` + `fase`. Les dates (`datazione_iniziale`/`finale`) queden buides: els graphmls yEd-raw no porten dates.
   - **3/5 Folders** — una fila per group folder. Combobox de `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` per excloure). `value` editable (default = `auto_value` derivat del prefix del label).
   - **4/5 Rapporti policy** — 4 radio buttons per tractar les edges que toquen folders:
     - **SKIP** (default): descarta les edges folder-touching. Les edges leaf-to-leaf passen intactes.
     - **FAN_OUT**: una edge `folder_A → folder_B` s'expandeix a `N×M` parells de leaves (producte cartesià dels membres).
     - **REPRESENTATIVE**: utilitza el primer membre de cada folder com a proxy.
     - **SYNTHETIC**: crea una fila us_table per folder (`unita_tipo='VA'` virtual activity) + reconnecta les edges a través d'aquests anchors.
   - **5/5 Preview** — dry-run de `import_yed_raw(overrides=..., dry_run=True)`. Mostra counts (us / inv / period / paradata) **sense commit**. Clic a **Finish** confirma, **Cancel** abandona.
4. En prémer **Finish** l'assistent desa els teus overrides en un **sidecar JSON** `<graphml>.yed_overrides.json` al costat del fitxer. Reobrir el mateix graphml precarrega el sidecar i els teus overrides previs tornen preaplicats.

### 5.3 Encaminament de destinacions

El dispatch fa servir `_classify_destination` (a `yed_import_pipeline.py`) per classificar cada leaf:

| ClassificationKind | Destinació | Nota |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | des de label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | des de `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | des de `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | des de `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derivat del prefix del label: USVs/USVn/USVc) | des de `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | des de `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | des de `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | des de `^VSF\d+` |
| DOCUMENT | `paradata` | des de `^D\.\d+` |
| COMBINER | `paradata` | des de `^C\.\d+` |
| PROPERTY | `paradata` | paraula clau al label (`material`/`position`/`width`/...) |

**Decisió de l'usuari 2026-05-13**: les USV* (virtuals) són «unità tipo» (segueixen sent unitats estratigràfiques) i van a `us_table`, no a paradata. Només DOC/COMB/PROP/VIRTUAL_FIND es queden a paradata.

### 5.4 Sidecar JSON — esquema

Versionat per a forward-compat:

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

Només es persisteixen els camps MODIFICATS per l'usuari (diff). Els valors `ClassificationKind` desconeguts (p. ex. de futures releases de s3dgraphy) es descarten silenciosament en carregar.

### 5.5 CLI per a ingest scripted

Per a CI / re-runs en batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mútex `--db` / `--conn-str` per a backend SQLite vs PostgreSQL. `--overrides` és opcional (sense overrides = defaults yE-D). `--auto-defaults` és un flag no-op forward-compat.

### 5.6 Limitacions conegudes

- **Sense edició de dates a l'assistent**: els graphmls yEd-raw no porten `datazione_iniziale`/`datazione_finale`. La pàgina Periods només edita `periodo` + `fase` (targets FK).
- **API ParadataStore parcial**: l'upstream s3dgraphy encara no proporciona `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D registra «skip — method missing» per leaf paradata però compta els intents al preview.
- **PropertyNode → Path B (sense enllaç a US)**: els nodes PROPERTY s'escriuen sense US target. L'assistent emet un warning. Futur: follow-up yE-Closure per afegir «assign target» a la UI.
- **Multi-DB**: el sidecar JSON és per graphml, no per DB. Si importes el mateix graphml a DBs diferents, es reutilitzen els mateixos overrides per a totes.

### 5.7 Cobertura de tests final

| Suite | Test | Cobertura |
|---|---|---|
| yE-A | `test_yed_detector.py` | detecció de flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | policies + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | persistència sidecar + CLI |

**Suite total post-rollout**: 354 passed / 42 skipped (PG-L1 requereixen psycopg2).

### 5.8 Actualització 5.8.5-alpha (yed-fastfix)

Pack de correccions de comportament sobre `5.8.3-alpha` que millora la qualitat del re-export GraphML després d'un import yEd-aware. Canvis rellevants per a l'usuari final:

- **Paradata multi-folder**: les labels DOC / Combinar / Extractor / property compartides entre diversos folders yEd (p. ex. `material` referenciat des de VA01 + VA04 + VA05) generen ara UNA fila a `us_table` PER ocurrència — visibilitat multi-folder restaurada al GraphML re-exportat. Compromís: el dedup per identitat (col·lapse de `D.01` / `D.01-2` / `D.01bis` en una sola fila) ja no s'aplica a la segona/tercera ocurrència.
- **Rapporti recíprocs**: cada edge yEd `a → b` escriu el rapporto directe sobre la fila d'`a` I l'invers sobre la fila de `b` (`<<` / «Coperto da» / etc.). Els DOC mostren ara totes les connexions extractor entrants al formulari Scheda US.
- **Strip del prefix `us` numèric**: `US100` → `us='100'` `unita_tipo='US'` (abans `us='US100'`). SF/VSF/RSF s'escriuen dualment a `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase**: la pertinença d'una fila TableNode yEd a un període es propaga a `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserva la distinció semàntica EM 1.5.
- **Re-import idempotent**: tornar a executar el mateix import salta les files ja presents; cap rollback per col·lisió UNIQUE en la passada repetida.
- **Paleta USV**: els nodes USV es renderitzen ara amb el paral·lelogram blau canònic d'EM (abans rectangle amb vora vermella).

### 5.9 yE-F paradata multi-carpeta (5.9.0-alpha)

Evolució estructural de `yed-fastfix-5.8.5-alpha`: el compromís del Bug R B1 (una fila `us_table` per ocurrència, amb `us='D.01_2'` / `us='D.01_3'`) ha estat superat. Una fulla paradata (DOC / Combinar / Extractor / property) compartida entre diverses carpetes yEd produeix ara **una sola fila** a `us_table` per label canònic, i la multi-pertinença es preserva en una nova columna `other_locations`.

Canvis visibles per a l'usuari final:

1. **Nou widget "Altres activitats" a la fitxa US/USM**: a la pestanya *Periodizzazione* apareix un `QListWidget` etiquetat "Altres activitats" — visible **només** quan `unita_tipo` és una tipologia paradata (`DOC`, `Combinar`, `Extractor`, `property`). L'usuari pot seleccionar diversos codis d'activitat; la selecció es serialitza com a llista JSON a la nova columna `other_locations`.
2. **Nova entrada de menú QGIS**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Cal executar-la **una vegada** a cada DB preexistent per afegir la nova columna (les DB creades post-5.9 ja tenen la columna).
3. **Import yEd-aware millorat**: una fulla paradata que apareix en N carpetes yEd genera ara **només 1** fila `us_table` (ja no N files amb sufix `_2`/`_3` com a 5.8.5). La primera carpeta trobada es converteix en l'`attivita` principal; les carpetes secundàries es llisten a `other_locations`. En **export** s'emeten N còpies visuals yEd (una per carpeta), totes compartint el mateix `node_uuid` canònic per garantir la identitat round-trip.

**Compatibilitat enrere**: les dades produïdes pel Bug R B1 a 5.8.5-alpha (files amb sufix `_2`/`_3`) continuen sent llegibles sense cap conversió automàtica. La nova lògica s'aplica als nous imports; les files legacy continuen comportant-se com abans.

Predecessor: vegeu la secció 5.8 (`yed-fastfix-5.8.5-alpha`) per al comportament substituït.

---

## 6. Generar continuïtat (fitxes CON)

Al panell **«Verifica rapporti»** — disponible com a pestanya dins del diàleg d'importació/exportació de s3dgraphy — hi ha el botó **«Genera continuità»** (etiqueta mantinguda en italià com al connector). Per al jaciment actualment seleccionat, aquesta funció crea automàticament les **fitxes de continuïtat** de les US/USM la vida de les quals abasta més d'un període.

### 6.1 Què fa

1. Escaneja totes les US/USM del jaciment on **període inicial ≠ període final** (és a dir, la vida de les quals abasta més d'un període).
2. Per a cadascuna crea o actualitza una fitxa de continuïtat anomenada **`CON_<us>`** (p. ex. `US5` → `CON_US5`).
3. La fitxa CON **hereta** de la unitat mare: jaciment, àrea (més les àrees secundàries), estructura i tot l'arc de períodes (inicial → final). La seva descripció es genera automàticament.
4. Escriu una **relació de continuïtat recíproca** a tots dos costats: a la CON i a la seva unitat mare.

### 6.2 Idempotència

L'operació és **idempotent**: tornar-la a executar no duplica les fitxes existents — actualitza les `CON_<us>` existents si les dades de la unitat mare han canviat.

### 6.3 Previsualització (dry-run) i còpia de seguretat

Abans d'escriure es mostra una **previsualització dry-run** amb els recomptes: quantes fitxes cal **crear**, **actualitzar**, **sense canvis** i quantes **òrfenes**. Els canvis s'apliquen **només després de la confirmació** (botó «Genera»). En aplicar-los es fa primer una **còpia de seguretat de la base de dades** automàtica.

Una fitxa CON és **òrfena** quan la seva unitat mare ja no abasta diversos períodes (p. ex. se n'han igualat el període inicial i final). Per defecte les òrfenes només se **senyalen**; una **casella de selecció** («Rimuovi anche le CON orfane») permet optar per eliminar-les.

### 6.4 A l'exportació Extended Matrix

Les fitxes `CON_<us>` generades així apareixen a l'exportació GraphML de l'Extended Matrix com a **elements de continuïtat**.

---

## 7. Verificació de paradoxes temporals (estratigràfics)

Al panell **"Verifica rapporti"** (Verificar relacions — una pestanya del diàleg d'import/export de s3dgraphy), la verificació ara també assenyala les **paradoxes temporals**: quan el període/fase assignat a una unitat contradiu l'estratigrafia observada. L'estratigrafia és la dada de referència, per això les correccions automàtiques desplacen els **períodes**, no les relacions.

### 7.1 Què detecta
- **Inversió temporal**: dues unitats datades unides per una relació d'ordre (p. ex. US5 «cobreix» US7) en què la unitat més recent en l'estratigrafia resulta enterament més **antiga** per període.
- **Contemporaneïtat incoherent**: unitats declarades contemporànies (igualtat física / vincle) però amb intervals cronològics **disjunts**.
- **No avaluable**: relació d'ordre en què almenys una de les dues unitats no té un període datable (només assenyalat, sense correcció).

Nota sobre el límit: dos períodes **adjacents que es toquen** en un únic punt cronològic es consideren superposats → **no** són una paradoxa (benefici del dubte).

### 7.2 Correcció automàtica i suggeriments
- Quan un sol desplaçament resol el conflicte, la verificació proposa desplaçar la unitat **monoperíode** en conflicte amb la majoria dels seus veïns, escollint el període de desplaçament mínim; per a les contemporaneïtats amb una unitat no datable copia el període del veí datat.
- En els casos ambigus — empat, unitats **multiperíode** (p. ex. fitxes CON), cap període vàlid — no corregeix automàticament: proporciona un **suggeriment «què + com»** (p. ex. «Desplaça US5 a un període ≥ 3, o US7 a un període ≤ 1, o verifica la relació»).

### 7.3 Vista prèvia i còpia de seguretat
- La **vista prèvia** mostra els canvis de període proposats abans d'aplicar-los.
- Abans d'escriure els períodes es realitza una **còpia de seguretat automàtica de la base de dades** (SQLite i PostgreSQL).
- Després d'aplicar, torna a llançar la verificació per comprovar eventuals paradoxes residuals.

---

## Referències

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositori pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
