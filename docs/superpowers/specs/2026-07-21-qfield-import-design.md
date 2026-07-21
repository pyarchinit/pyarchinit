# Importa da QField — Design

**Data:** 2026-07-21
**Branch:** `Stratigraph_00001`
**Stato:** approvato a voce, spec in revisione

## Obiettivo

Portare dentro pyArchInit l'import dei dati raccolti in campo con QField
(plugin companion `pyarchinit-qfield`): i GeoPackage del progetto QField
vengono letti e riversati nel DB pyArchInit corrente (PostGIS o SpatiaLite)
con dedup, aggiornamento dei campi vuoti, copia foto sul backend media
configurato (locale o WebDAV) e generazione automatica delle thumbnail.

Origine: script standalone `pyarchinit_qfield_import.py` (Enzo, GPL-2.0) —
la logica viene vendorizzata come modulo riusabile; lo script CLI resta come
wrapper sottile.

## Non-obiettivi (v1)

- Nessun UPDATE di campi già valorizzati nel DB (niente merge/conflitti UI).
- Nessun refactoring di `Image_viewer` (il glue thumbnail viene *duplicato*
  in forma riusabile, non estratto dal viewer).
- Nessuna sincronizzazione bidirezionale pyArchInit → QField (il progetto
  QField si prepara con il plugin companion, fuori scope qui).
- Niente rapporti stratigrafici: restano da ricontrollare a mano dopo
  l'import (nota nel riepilogo).

## Componenti

| File | Ruolo |
|---|---|
| `modules/utility/qfield_importer.py` (NUOVO) | Pipeline riusabile, zero Qt |
| `scripts/import_qfield.py` (NUOVO) | CLI sottile sopra la pipeline |
| `gui/qfield_import_dialog.py` (NUOVO) | QDialog con worker QThread |
| `pyarchinitPlugin.py` (MODIFICA) | Voce di menu "Importa da QField (GPKG)" |

### `modules/utility/qfield_importer.py`

Funzioni pure (niente Qt, niente QGIS API): riusa OGR (`osgeo`) e SQLAlchemy
già presenti nell'ambiente QGIS.

API principale:

```python
def run_qfield_import(
    db_manager,               # Pyarchinit_db_management (o conn_str: risolto internamente)
    qfield_dir,               # cartella progetto QField
    *,
    sito=None,                # filtra un solo sito (None = tutti)
    srid=None,                # override SRID sorgente (None = dal GPKG)
    dry_run=True,             # default sicuro
    geom_dedup=True,
    copy_media=True,          # copia/upload foto sul backend configurato
    make_thumbs=True,
    log=print,                # callable per il log riga-per-riga
) -> QFieldImportResult
```

`QFieldImportResult` (dataclass): per ciascuna tabella
(`us`, `materiali`, `geometrie`, `quote`, `media`, `links`, `thumbs`) i contatori
`inserted / updated / skipped / errors`, più:

- `filled_fields`: lista `(tabella, chiave_record, campo, valore)` dei campi
  riempiti dalla policy fill-empty — mostrata integralmente in anteprima;
- `media_upload_failures`: lista file non copiati/caricati (post-commit);
- `warnings`: lista messaggi non bloccanti.

Struttura interna: le funzioni dello script originale, adattate —
`find_gpkg_layers`, `read_features`, `import_us`, `import_materiali`,
`import_geometrie`, `import_media` + nuove `fill_empty_fields`,
`make_thumbnails`, `store_media_file`.

Tabelle trattate (nomi layer GPKG = nomi tabella DB):
`us_table`, `inventario_materiali_table`, `pyunitastratigrafiche`,
`pyarchinit_quote`, `media_table`, `media_to_entity_table`.

`read_features(..., force_multi=True)`: i poligoni US vengono forzati a
MULTIPOLYGON; per `pyarchinit_quote` (punti) `force_multi=False` e la
INSERT non applica `ST_Multi`/`CastToMultiPolygon`.

### `scripts/import_qfield.py`

Pattern `scripts/import_yed_graphml.py`:

- `--qfield-dir` obbligatorio;
- `--db <sqlite_path>` / `--conn-str <postgresql://...>` mutuamente
  esclusivi; in assenza di entrambi usa `Connection().conn_str()`
  (il DB configurato del plugin);
- **dry-run è il default**; `--apply` per scrivere;
- `--sito`, `--srid`, `--no-geom-dedup`, `--no-media`, `--no-thumbs`, `-v`;
- exit code ≠ 0 se `errors > 0`.

### `gui/qfield_import_dialog.py`

`QFieldImportDialog(QDialog)` + `QFieldImportWorker(QThread)`
(pattern `tma_import_dialog.py`, ma con anteprima funzionante):

- **Input**: picker cartella progetto QField; alla scelta, scansione rapida
  dei GPKG (nel worker) → popola combo "Sito" (siti trovati + "Tutti") e
  mostra i layer trovati nel log.
- **Opzioni**: SRID override (spin/edit, vuoto = auto), checkbox
  "Deduplica geometrie" (on), "Copia foto" (on), "Genera thumbnail" (on).
- **Bottoni**: "Anteprima (dry-run)" e "Importa" — entrambi lanciano lo
  stesso worker (`dry_run=True/False`); durante l'esecuzione i controlli si
  disabilitano, `QProgressBar` a step per tabella, log live su `QTextEdit`
  via segnale `log_message`.
- **Anteprima**: al termine del dry-run, riepilogo contatori + elenco
  completo dei campi che la policy fill-empty riempirebbe.
- **Fine import**: riepilogo + eventuali `media_upload_failures` in
  evidenza.
- **DB**: pattern `rapporti_check_dialog` — parametro opzionale
  `db_manager`; se assente si auto-risolve `Connection().conn_str()` →
  `get_db_manager(conn_str, use_singleton=True)`. Nessun campo URL in UI.
- **i18n**: dict `TRANSLATIONS` a 10 lingue + `self.L` da
  `QgsSettings "locale/userLocale"` (convenzione `user_management_dialog.py`).

### Menu (`pyarchinitPlugin.py`)

`QAction("Importa da QField (GPKG)")` registrato con il pattern di
`_init_migrations_menu` (guard `_wired`, try/except con `QgsMessageLog`),
`iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", action)`.
Handler: apre il dialog senza `db_manager` (auto-risoluzione).

## Semantica di import

### Dedup e fill-empty

| Tabella | Chiave dedup | Se nuovo | Se esistente |
|---|---|---|---|
| `us_table` | `sito+area+us` (normalizzati) | INSERT | **UPDATE dei soli campi vuoti** |
| `inventario_materiali_table` | `sito+numero_inventario` | INSERT | **UPDATE dei soli campi vuoti** |
| `pyunitastratigrafiche` | `scavo_s+area_s+us_s` | INSERT | skip (disattivabile) |
| `pyarchinit_quote` | `sito_q+area_q+us_q+quota_q` | INSERT | skip |
| `media_table` | `filepath` finale | INSERT | skip |
| `media_to_entity_table` | `(id_entity, entity_type, id_media)` rimappati | INSERT | skip |

**Fill-empty** (US e reperti): un campo del DB si considera vuoto se
`NULL` o stringa vuota/whitespace; viene riempito solo se il valore dal
campo è non-vuoto. Mai toccati: PK, chiavi di dedup, `node_uuid`,
colonne di concorrenza (`version_number`, `sync_status`, `editing_*`,
`last_modified_*` — quest'ultima aggiornata dal marcatore di provenienza,
vedi sotto). Ogni riempimento è loggato e conteggiato in `updated`.

**Rimappatura media→US** (invariata dallo script): mappa
`id sorgente (id_us GPKG o fid) → id_us DB` costruita durante l'import US
(nuovo id o id esistente); `media_to_entity_table.id_entity` riscritto di
conseguenza; link con sorgente non rimappabile → skip + warning.

### Metadati automatici sui record inseriti

- `node_uuid = uuid7()` (generatore di `modules/s3dgraphy/sync/uuid7`) su
  `us_table`, `inventario_materiali_table` (e `periodizzazione_table` se in
  futuro entra nello scope). Nessun backfill successivo necessario.
- Provenienza: `created_by='qfield_import'` se la colonna esiste
  (reflection), altrimenti `last_modified_by='qfield_import'` se esiste.
  `schedatore` non viene MAI usato come marcatore (è un dato di campo).

### Geometrie e SRID

- SRID sorgente: dal GPKG (`AutoIdentifyEPSG`), override con `srid=`.
- SRID target: letto da `geometry_columns` per `pyunitastratigrafiche` e
  `pyarchinit_quote`; se diverso dal sorgente → `ST_Transform` (PG) /
  `Transform` (SpatiaLite) dentro la INSERT. Poligoni US forzati a
  MULTIPOLYGON come nello script; punti quota inseriti come POINT nativo.
- Filtro sito per layer: `scavo_s` (pyunitastratigrafiche), `sito_q`
  (pyarchinit_quote), `sito` (us/reperti); media/link mai filtrati
  direttamente (passano dalla rimappatura).
- SpatiaLite: `mod_spatialite` caricato con listener `connect` sull'engine
  (come nello script) — se il caricamento fallisce, errore strutturale.

### Media, StorageManager e thumbnail

- Destinazione foto: il backend media configurato del plugin. Path locale →
  copia su filesystem; `webdav://` → upload via lo StorageManager già usato
  dal Media Manager (stesso codice di `Media_utility`/`_resample_remote`).
  La cartella di destinazione deriva dalla config (`Connection()`), non è
  scelta nel dialog.
- `media_table.filepath` = path finale (locale o webdav) coerente con la
  convenzione del Media Manager.
- Thumbnail (se `make_thumbs`): per ogni media **inserito**,
  `Media_utility().resample_images()` + `Media_utility_resize()` verso
  `thumb_path`/`thumb_resize` da `Connection()`, poi insert in
  `media_thumb_table` via `DB_MANAGER.insert_mediathumb_values(...)` +
  `insert_data_session(...)` (glue replicato da `Image_viewer`, in forma
  di funzione riusabile `make_thumbnails(db_manager, media_records, log)`).

### Transazione ed errori

- Tutte le scritture DB in **una transazione**: commit unico a fine import;
  `dry_run=True` → rollback garantito (zero scritture).
- Copia/upload foto e generazione thumbnail avvengono **dopo il commit**:
  un fallimento non annulla i record; finisce in `media_upload_failures` /
  `warnings` con istruzioni di recupero nel riepilogo.
- Errori per-riga (es. valore incompatibile): log + `errors += 1`, la riga
  è saltata, l'import continua.
- Errori strutturali (tabella/layer mancante, mod_spatialite assente,
  SRID indeterminabile senza override): eccezione → messaggio d'errore,
  rollback, niente scritture parziali.
- Le colonne del GPKG vengono intersecate con le colonne reali della
  tabella DB (reflection): campi extra nel GPKG ignorati, campi DB assenti
  nel GPKG restano NULL.

## Test (pytest, senza Qt, in `tests/` — gitignorato ma locale)

Fixture: GPKG minimale generato con OGR in tmp (2 US, 1 reperto,
1 geometria poligonale, 1 punto quota, 2 media + link), DB SQLite creato
dal template o schema minimo in-memory.

Casi:
1. dry-run: contatori corretti e **zero scritture** (rollback verificato);
2. import pulito: righe inserite, `node_uuid` valorizzato, provenienza
   presente;
3. dedup: secondo import identico → tutto `skipped`, nessun duplicato;
4. fill-empty: US esistente con campo vuoto → riempito; campo valorizzato
   → intatto; `filled_fields` lo riporta;
5. rimappatura media: US già esistente nel DB → link foto agganciato
   all'id_us esistente;
6. thumbnail: record `media_thumb_table` creati per i soli media inseriti
   (con immagini-fixture reali minuscole);
7. errore strutturale: cartella senza GPKG → eccezione pulita.

## Rilascio

- CHANGELOG bilingue (agente changelog) + tutorial nelle 10 lingue
  (tutorial-updater): feature user-facing.
- CLI documentato nel docstring del modulo (esempi d'uso come nello script
  originale).

## Rischi noti

- **WebDAV lento su import massivi**: mitigato dal worker QThread (QGIS non
  si blocca) e dalla checkbox "Copia foto" disattivabile.
- **Fill-empty su dati sporchi di campo**: mitigato da anteprima obbligatoria
  di fatto (dry-run mostra ogni campo che verrebbe riempito) — la policy non
  sovrascrive mai valori esistenti.
- **Divergenza schema GPKG ↔ DB**: mitigata dall'intersezione per reflection;
  i campi non mappabili sono ignorati con log.
