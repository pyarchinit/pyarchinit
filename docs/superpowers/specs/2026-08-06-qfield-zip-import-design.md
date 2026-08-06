# Supporto ZIP per "Importa da QField (GPKG)" — Design

**Data:** 2026-08-06
**Branch:** `Stratigraph_00001`
**Stato:** approvato (design validato in sessione)

## Contesto

L'importer QField (`modules/utility/qfield_importer.py` + `gui/qfield_import_dialog.py`
+ `scripts/import_qfield.py`) oggi accetta solo una **cartella** progetto QField:

- dialog: `QFileDialog.getExistingDirectory` → campo `dir_edit`
  (`gui/qfield_import_dialog.py:330`);
- CLI: `--qfield-dir` validato con `Path(...).is_dir()`
  (`scripts/import_qfield.py:66`);
- pipeline: `Path(qfield_dir).rglob("*.gpkg")`
  (`modules/utility/qfield_importer.py:161`); anche la copia media e le
  thumbnail leggono file dallo stesso albero.

I progetti QField arrivano però spesso come **archivio .zip** (export/condivisione da
mobile). Obiettivo: accettare anche un file `.zip` con estrazione automatica in
cartella temporanea, in tutti i punti d'ingresso.

## Obiettivo

Un utente può indicare indifferentemente una cartella **o** un file `.zip` come
sorgente; il comportamento a valle (scansione, dedup, fill-empty, media,
thumbnail, dry-run/apply) è identico nei due casi.

## Non-obiettivi

- Nessun supporto per altri formati di archivio (tar, 7z, rar).
- Nessuna cache dell'estrazione tra dry-run e apply: ogni run estrae la propria
  copia temporanea (doppia estrazione accettata).
- Nessun check preventivo dello spazio disco.
- Nessuna modifica al companion `pyarchinit-qfield`.

## Design

### 1. Pipeline — helper `_resolve_qfield_source`

Nuova funzione module-level in `modules/utility/qfield_importer.py`, senza
import Qt/QGIS (vincolo esistente del modulo: testabile col python di sistema):

```python
def _resolve_qfield_source(path):
    """Ritorna (source_dir, cleanup).

    - path e' una cartella          -> (path, None)
    - path e' un file .zip valido   -> estrae TUTTO l'archivio in
      tempfile.mkdtemp(prefix="pyarchinit_qfield_zip_") e ritorna
      (tmpdir, cleanup) dove cleanup() fa shutil.rmtree(ignore_errors=True)
    - altrimenti                    -> ValueError con messaggio esplicito
      ("ne' cartella ne' archivio .zip")
    """
```

Note:

- estrazione con `zipfile.ZipFile.extractall` (l'`extract()` di Python sanifica
  percorsi assoluti e componenti `..`: zip-slip coperto);
- si estrae l'**intero** archivio, non solo i `.gpkg`: i media referenziati da
  `media_table` vengono copiati dallo stesso albero;
- `zipfile.BadZipFile` viene catturata e ritradotta in `ValueError` con
  messaggio chiaro (zip corrotto / non valido);
- il riconoscimento è: `Path(path).is_dir()` → cartella;
  `Path(path).is_file()` e suffisso `.zip` (case-insensitive) → archivio.

`run_qfield_import` chiama l'helper come prima operazione e avvolge tutto il
corpo esistente — pipeline, copia media post-commit, thumbnail — in
`try/finally` con `cleanup()` nel `finally`. Il `rglob` ricorsivo esistente
gestisce sia zip con i file alla radice sia zip con una sottocartella progetto.

### 2. Dialog (`gui/qfield_import_dialog.py`)

- Il pulsante esistente per scegliere la cartella resta invariato.
- Nuovo pulsante "ZIP…" accanto: `QFileDialog.getOpenFileName` con filtro
  `Archivi ZIP (*.zip)`, scrive il percorso scelto nello stesso `dir_edit`.
- Due nuove chiavi in `TRANSLATIONS`, tradotte nelle 10 lingue già presenti
  nel dialog: `zip_browse` (etichetta del pulsante) e `zip_filter` (stringa
  del filtro file, es. IT "Archivi ZIP (*.zip)").
- Nessuno stato aggiuntivo nel dialog: dry-run e apply estraggono ciascuno la
  propria copia temporanea dentro `run_qfield_import`.

### 3. CLI (`scripts/import_qfield.py`)

- Validazione di `--qfield-dir`: da `is_dir()` a "cartella esistente **oppure**
  file `.zip` esistente"; messaggio d'errore aggiornato.
- Help dell'argomento aggiornato ("cartella progetto QField o archivio .zip").
- Nessun nuovo flag.

### 4. Error handling

| Caso | Comportamento |
|------|---------------|
| zip corrotto / non-zip con estensione .zip | `ValueError` con messaggio chiaro; il worker del dialog lo mostra come gli altri errori, la CLI esce con messaggio |
| percorso né cartella né .zip | `ValueError` esplicito dall'helper (la CLI lo intercetta già in validazione) |
| zip valido senza `.gpkg` | messaggio esistente "nessun gpkg trovato" (invariato) |
| eccezione a metà run | `finally` esegue comunque il cleanup della temp dir (best-effort, `ignore_errors=True`) |

### 5. Test (`tests/qfield/`, locali — cartella gitignorata)

Nuovi casi:

1. passthrough cartella: `_resolve_qfield_source` su una dir ritorna la dir e
   cleanup `None`;
2. zip della fixture (costruito al volo in `tmp_path` zippando la
   cartella-fixture esistente): il dry-run produce lo **stesso** risultato del
   dry-run sulla cartella;
3. zip corrotto: errore pulito, nessuna temp dir residua;
4. cleanup: dopo un run con zip la temp dir non esiste più.

La suite esistente (33 test) resta verde.

### 6. Post-implementazione

- Tutorial 38 (`docs/tutorials/<lang>/38_qfield_import.md`, 10 lingue):
  documentare la sorgente ZIP (agente tutorial-updater).
- `dev_logs/CHANGELOG.md`: voce bilingue IT+EN (agente stratigraph-changelog).

## Criteri di accettazione

1. Import da cartella: comportamento identico a oggi (nessuna regressione).
2. Import da `.zip`: stesso risultato dell'import dalla cartella equivalente,
   in dry-run e in apply, media e thumbnail inclusi.
3. Zip corrotto o percorso invalido → errore chiaro, nessun file temporaneo
   residuo.
4. `py_compile` pulito su file toccati; `tests/qfield` tutti verdi
   (33 esistenti + nuovi).
