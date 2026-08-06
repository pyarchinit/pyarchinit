# Supporto ZIP per "Importa da QField (GPKG)" — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** L'importer QField accetta come sorgente anche un archivio `.zip` (estratto in temp dir e ripulito a fine run) in pipeline, dialog e CLI.

**Architecture:** Helper `_resolve_qfield_source(path)` in `modules/utility/qfield_importer.py`; il corpo attuale di `run_qfield_import` viene rinominato `_run_qfield_import_on_dir` e la funzione pubblica diventa un wrapper sottile che risolve la sorgente e garantisce il cleanup in `finally` (copre anche copia media e thumbnail post-commit, che avvengono dentro la funzione delegata). Dialog e CLI passano solo il percorso.

**Tech Stack:** Python stdlib (`zipfile`, `tempfile`, `shutil`), SQLAlchemy (invariato), PyQt (solo dialog), pytest.

**Spec:** `docs/superpowers/specs/2026-08-06-qfield-zip-import-design.md`

## Global Constraints

- `modules/utility/qfield_importer.py`: ZERO import Qt/QGIS/osgeo a livello modulo (stdlib ok, a livello modulo).
- Firma pubblica di `run_qfield_import(db, qfield_dir, *, ...)` INVARIATA (stessi nomi e default dei kwargs).
- pytest va lanciato DALLA ROOT del repo (`pyproject.toml` ha `--confcutdir=tests/sync` relativo): prima `cd` alla root in un comando Bash a sé, poi pytest.
- `tests/` è nel `.gitignore`: i nuovi test restano locali, NON vanno mai aggiunti ai commit.
- Lingue `TRANSLATIONS` del dialog: esattamente `{it, en, de, es, fr, ar, ca, ro, pt, el}` per ogni chiave (test AST esistente lo impone).
- Commit: nessun trailer `Co-Authored-By` né footer di attribuzione AI.
- Python per i test: python3 di sistema (i test girano senza osgeo/Qt/QGIS).
- Root del repo: `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit` (citata sotto come `<ROOT>`).

---

### Task 1: Helper `_resolve_qfield_source` nella pipeline

**Files:**
- Modify: `modules/utility/qfield_importer.py` (import stdlib in testa ~riga 15-18; helper dopo `apply_provenance`, ~riga 149)
- Test: `tests/qfield/test_zip_source.py` (NUOVO — locale, non committare)

**Interfaces:**
- Consumes: `Path` (già importato nel modulo).
- Produces: `_resolve_qfield_source(path) -> tuple[str, callable | None]` — `(source_dir, cleanup)`; `cleanup` è `None` per le cartelle, altrimenti una funzione senza argomenti che rimuove la temp dir. Solleva `ValueError` per zip corrotto o percorso non valido. Task 2 la chiama da `run_qfield_import`.

- [ ] **Step 1: Scrivere i test che falliscono**

Creare `tests/qfield/test_zip_source.py`:

```python
import glob
import os
import tempfile
import zipfile

import pytest

from modules.utility.qfield_importer import (
    QFieldImportError, _resolve_qfield_source, run_qfield_import,
)


def _make_zip(tmp_path, name="progetto.zip"):
    """Zip di un progetto QField finto: un .gpkg placeholder + una foto.

    Il contenuto del .gpkg e' irrilevante: i test che usano questo zip
    passano rows_override, quindi osgeo non viene mai importato.
    """
    src = tmp_path / "progetto"
    (src / "DCIM").mkdir(parents=True)
    (src / "data.gpkg").write_bytes(b"not-a-real-gpkg")
    (src / "DCIM" / "us100.jpg").write_bytes(b"jpg")
    zip_path = tmp_path / name
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in sorted(src.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(tmp_path))
    return zip_path


def _tmp_zip_dirs():
    return set(glob.glob(os.path.join(tempfile.gettempdir(),
                                      "pyarchinit_qfield_zip_*")))


def test_resolve_dir_passthrough(tmp_path):
    source, cleanup = _resolve_qfield_source(str(tmp_path))
    assert source == str(tmp_path)
    assert cleanup is None


def test_resolve_zip_extracts_and_cleanup(tmp_path):
    zip_path = _make_zip(tmp_path)
    source, cleanup = _resolve_qfield_source(str(zip_path))
    assert source != str(tmp_path)
    assert os.path.isfile(os.path.join(source, "progetto", "data.gpkg"))
    assert os.path.isfile(
        os.path.join(source, "progetto", "DCIM", "us100.jpg"))
    cleanup()
    assert not os.path.exists(source)


def test_resolve_corrupt_zip_raises_and_leaves_nothing(tmp_path):
    before = _tmp_zip_dirs()
    bad = tmp_path / "corrotto.zip"
    bad.write_bytes(b"questo non e' uno zip")
    with pytest.raises(ValueError, match="ZIP"):
        _resolve_qfield_source(str(bad))
    assert _tmp_zip_dirs() == before


def test_resolve_invalid_path_raises(tmp_path):
    with pytest.raises(ValueError, match="cartella"):
        _resolve_qfield_source(str(tmp_path / "inesistente"))
```

- [ ] **Step 2: Verificare che falliscano**

```bash
cd "<ROOT>"
```

```bash
python3 -m pytest tests/qfield/test_zip_source.py -v
```

Atteso: 4 FAIL/ERROR con `ImportError: cannot import name '_resolve_qfield_source'`.

- [ ] **Step 3: Implementazione minima**

In `modules/utility/qfield_importer.py`, aggiungere agli import in testa (dopo `import os`, riga 16):

```python
import shutil
import tempfile
import zipfile
```

Dopo `apply_provenance` (~riga 149), prima della sezione "Lettura GPKG":

```python
def _resolve_qfield_source(path):
    """Risolve la sorgente dell'import: cartella o archivio .zip.

    Ritorna (source_dir, cleanup):
    - cartella          -> (path, None)
    - file .zip valido  -> estrae TUTTO l'archivio in una temp dir
                           (prefisso pyarchinit_qfield_zip_) e ritorna
                           (temp_dir, cleanup); cleanup() la rimuove
    - altrimenti        -> ValueError con messaggio esplicito

    extract()/extractall() di zipfile sanificano percorsi assoluti e
    componenti '..': zip-slip coperto dalla stdlib.
    """
    p = Path(path)
    if p.is_dir():
        return str(p), None
    if p.is_file() and p.suffix.lower() == ".zip":
        tmpdir = tempfile.mkdtemp(prefix="pyarchinit_qfield_zip_")

        def cleanup():
            shutil.rmtree(tmpdir, ignore_errors=True)

        try:
            with zipfile.ZipFile(str(p)) as zf:
                zf.extractall(tmpdir)
        except zipfile.BadZipFile as exc:
            cleanup()
            raise ValueError(
                f"Archivio ZIP non valido o corrotto: {path}") from exc
        except Exception:
            cleanup()
            raise
        return tmpdir, cleanup
    raise ValueError(
        f"Sorgente QField non valida (né cartella né archivio .zip): {path}")
```

- [ ] **Step 4: Verificare che i 4 test passino**

```bash
python3 -m pytest tests/qfield/test_zip_source.py -v
```

Atteso: 4 PASS (dalla root del repo).

- [ ] **Step 5: Commit (solo il file di pipeline: i test sono gitignorati)**

```bash
git -C "<ROOT>" add modules/utility/qfield_importer.py
git -C "<ROOT>" commit -m "feat(qfield): helper _resolve_qfield_source (cartella o archivio zip)"
```

---

### Task 2: `run_qfield_import` accetta un `.zip`

**Files:**
- Modify: `modules/utility/qfield_importer.py:835` (def `run_qfield_import`)
- Test: `tests/qfield/test_zip_source.py` (aggiunta in coda — locale, non committare)

**Interfaces:**
- Consumes: `_resolve_qfield_source(path) -> (source_dir, cleanup)` dal Task 1.
- Produces: `run_qfield_import(db, qfield_dir, *, ...)` con firma INVARIATA; `qfield_dir` ora può essere cartella o `.zip`. Internamente il corpo esistente diventa `_run_qfield_import_on_dir` (stessa firma). Dialog (Task 4) e CLI (Task 3) non cambiano le loro chiamate.

- [ ] **Step 1: Aggiungere i test che falliscono**

In coda a `tests/qfield/test_zip_source.py`:

```python
def _rows_min():
    return {
        "us_table": [{"_fid": 1, "id_us": None, "sito": "F", "area": "1",
                      "us": "100", "d_stratigrafica": "s"}],
        "inventario_materiali_table": [],
        "media_table": [],
        "media_to_entity_table": [],
    }


def test_run_import_accepts_zip_and_cleans_up(engine, tmp_path):
    zip_path = _make_zip(tmp_path)
    before = _tmp_zip_dirs()
    res = run_qfield_import(engine, str(zip_path), dry_run=True,
                            copy_media=False, make_thumbs=False,
                            log=lambda m: None, rows_override=_rows_min())
    assert res.us.inserted == 1
    assert _tmp_zip_dirs() == before


def test_run_import_zip_without_gpkg_raises_no_layers(engine, tmp_path):
    # zip SENZA .gpkg: l'errore deve essere "nessun layer" (quindi
    # l'archivio e' stato estratto e scansionato), non un errore di percorso;
    # niente osgeo: find_gpkg_layers ritorna {} prima di importarlo
    src = tmp_path / "vuoto"
    src.mkdir()
    (src / "leggimi.txt").write_text("niente gpkg")
    zip_path = tmp_path / "vuoto.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(src / "leggimi.txt", "leggimi.txt")
    before = _tmp_zip_dirs()
    with pytest.raises(QFieldImportError):
        run_qfield_import(engine, str(zip_path), dry_run=True,
                          copy_media=False, make_thumbs=False,
                          log=lambda m: None)
    assert _tmp_zip_dirs() == before


def test_run_import_corrupt_zip_raises_valueerror(engine, tmp_path):
    # discriminante TDD: SENZA il wiring del Task 2 questo solleva
    # QFieldImportError ("nessun layer": rglob su un file ritorna []),
    # COL wiring l'helper intercetta prima e solleva ValueError
    bad = tmp_path / "corrotto.zip"
    bad.write_bytes(b"questo non e' uno zip")
    with pytest.raises(ValueError, match="ZIP"):
        run_qfield_import(engine, str(bad), dry_run=True,
                          copy_media=False, make_thumbs=False,
                          log=lambda m: None)
```

- [ ] **Step 2: Verificare il fallimento del test discriminante**

```bash
python3 -m pytest tests/qfield/test_zip_source.py -v
```

Atteso: i 4 test del Task 1 PASS; `test_run_import_corrupt_zip_raises_valueerror` FAIL (solleva `QFieldImportError` invece di `ValueError`). Gli altri 2 nuovi test possono già passare — sono lock di regressione, non discriminanti: con `rows_override` senza media la pipeline non tocca `qfield_dir`, e `rglob` su un file ritorna `[]` producendo lo stesso `QFieldImportError`; dopo il wiring validano estrazione e cleanup reali.

- [ ] **Step 3: Implementazione — wrapper con `finally`**

In `modules/utility/qfield_importer.py`:

1. Rinominare `def run_qfield_import(` (riga 835) in `def _run_qfield_import_on_dir(` — corpo e docstring INVARIATI.
2. Subito PRIMA di `def _run_qfield_import_on_dir`, aggiungere la nuova funzione pubblica:

```python
def run_qfield_import(db, qfield_dir, *, sito=None, srid=None, dry_run=True,
                      geom_dedup=True, copy_media=True, make_thumbs=True,
                      media_dest=None, thumb_path=None, thumb_resize=None,
                      log=print, layers_override=None, rows_override=None):
    """Esegue l'intero import QField. Vedi spec 2026-07-21 e 2026-08-06.

    ``qfield_dir`` può essere la cartella progetto QField oppure un
    archivio ``.zip``: l'archivio viene estratto in una cartella
    temporanea rimossa a fine run (anche in caso di errore), DOPO la
    copia media e le thumbnail che leggono dall'albero estratto.
    """
    source_dir, cleanup = _resolve_qfield_source(qfield_dir)
    try:
        return _run_qfield_import_on_dir(
            db, source_dir, sito=sito, srid=srid, dry_run=dry_run,
            geom_dedup=geom_dedup, copy_media=copy_media,
            make_thumbs=make_thumbs, media_dest=media_dest,
            thumb_path=thumb_path, thumb_resize=thumb_resize, log=log,
            layers_override=layers_override, rows_override=rows_override)
    finally:
        if cleanup is not None:
            cleanup()
```

Nota comportamentale accettata (in spec): un percorso inesistente ora
solleva `ValueError` dall'helper invece di arrivare a `find_gpkg_layers`
e diventare `QFieldImportError` "nessun layer". La CLI lo intercetta già
in validazione (Task 3); il worker del dialog cattura `Exception` e
mostra il messaggio (`gui/qfield_import_dialog.py:220`).

- [ ] **Step 4: Tutta la suite qfield deve passare**

```bash
python3 -m pytest tests/qfield -v
```

Atteso: 40 PASS (33 esistenti + 7 nuovi), 0 fail. I test esistenti passano
cartelle (`tmp_path`): percorso passthrough, nessuna regressione.

- [ ] **Step 5: Commit**

```bash
git -C "<ROOT>" add modules/utility/qfield_importer.py
git -C "<ROOT>" commit -m "feat(qfield): run_qfield_import accetta archivi .zip (estrazione temporanea)"
```

---

### Task 3: CLI — `--qfield-dir` accetta cartella o `.zip`

**Files:**
- Modify: `scripts/import_qfield.py:47-48` (help) e `scripts/import_qfield.py:66-67` (validazione)

**Interfaces:**
- Consumes: `run_qfield_import` (Task 2) — la chiamata esistente a riga 85-90 resta identica.
- Produces: nessuna nuova interfaccia; solo validazione e help.

- [ ] **Step 1: Modificare help e validazione**

Sostituire (righe 47-48):

```python
    parser.add_argument("--qfield-dir", required=True,
                        help="Cartella del progetto QField (contiene i .gpkg)")
```

con:

```python
    parser.add_argument("--qfield-dir", required=True,
                        help="Cartella del progetto QField (contiene i .gpkg) "
                             "oppure archivio .zip del progetto")
```

Sostituire (righe 66-67):

```python
    if not Path(args.qfield_dir).is_dir():
        sys.exit(f"Cartella non trovata: {args.qfield_dir}")
```

con:

```python
    src = Path(args.qfield_dir)
    if not (src.is_dir() or (src.is_file()
                             and src.suffix.lower() == ".zip")):
        sys.exit("Sorgente non trovata (cartella o archivio .zip): "
                 f"{args.qfield_dir}")
```

- [ ] **Step 2: Verifica sintassi + smoke test**

```bash
python3 -m py_compile "<ROOT>/scripts/import_qfield.py"
```

```bash
cd "<ROOT>"
```

```bash
python3 scripts/import_qfield.py --qfield-dir /percorso/inesistente --db /tmp/x.sqlite; echo "exit=$?"
```

Atteso: stampa `Sorgente non trovata (cartella o archivio .zip): /percorso/inesistente`, exit=1.

- [ ] **Step 3: Commit**

```bash
git -C "<ROOT>" add scripts/import_qfield.py
git -C "<ROOT>" commit -m "feat(qfield): CLI --qfield-dir accetta anche un archivio .zip"
```

---

### Task 4: Dialog — pulsante "Archivio ZIP…" e traduzioni

**Files:**
- Modify: `gui/qfield_import_dialog.py` — `TRANSLATIONS` (dopo la chiave `'browse'`, ~riga 45), `_build_ui` (~riga 271), nuovo handler dopo `_choose_dir` (~riga 335)
- Test: `tests/qfield/test_dialog_import.py` (aggiunta in coda — locale, non committare)

**Interfaces:**
- Consumes: `run_qfield_import` via `QFieldImportWorker` (invariato: passa `params["qfield_dir"]`, che ora può essere un percorso .zip).
- Produces: chiavi `TRANSLATIONS['zip_browse']` e `TRANSLATIONS['zip_filter']` (10 lingue), pulsante `self.zip_btn`, handler `_choose_zip`.

- [ ] **Step 1: Aggiungere il test che fallisce**

In coda a `tests/qfield/test_dialog_import.py`:

```python
def test_translations_have_zip_keys():
    tree = ast.parse(open(DIALOG).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and \
                getattr(node.targets[0], 'id', '') == 'TRANSLATIONS':
            d = ast.literal_eval(node.value)
            assert 'zip_browse' in d and 'zip_filter' in d
            return
    pytest.fail("TRANSLATIONS non trovato")
```

(la copertura delle 10 lingue è già imposta dal test esistente
`test_translations_cover_10_languages` su OGNI chiave.)

- [ ] **Step 2: Verificare che fallisca**

```bash
python3 -m pytest tests/qfield/test_dialog_import.py -v
```

Atteso: `test_translations_have_zip_keys` FAIL (`'zip_browse' in d` è False); gli altri PASS.

- [ ] **Step 3: Implementazione**

1. In `TRANSLATIONS`, subito dopo il blocco `'browse'` (~riga 45), aggiungere:

```python
    'zip_browse': {
        'it': "Archivio ZIP…", 'en': "ZIP archive…", 'de': "ZIP-Archiv…",
        'es': "Archivo ZIP…", 'fr': "Archive ZIP…", 'ar': "أرشيف ZIP…",
        'ca': "Arxiu ZIP…", 'ro': "Arhivă ZIP…", 'pt': "Arquivo ZIP…",
        'el': "Αρχείο ZIP…",
    },
    'zip_filter': {
        'it': "Archivi ZIP (*.zip)", 'en': "ZIP archives (*.zip)",
        'de': "ZIP-Archive (*.zip)", 'es': "Archivos ZIP (*.zip)",
        'fr': "Archives ZIP (*.zip)", 'ar': "أرشيفات ZIP (*.zip)",
        'ca': "Arxius ZIP (*.zip)", 'ro': "Arhive ZIP (*.zip)",
        'pt': "Arquivos ZIP (*.zip)", 'el': "Αρχεία ZIP (*.zip)",
    },
```

2. In `_build_ui`, dopo `grid.addWidget(self.browse_btn, 0, 2)` (~riga 271):

```python
        self.zip_btn = QPushButton(self.tr_('zip_browse'))
        self.zip_btn.clicked.connect(self._choose_zip)
        grid.addWidget(self.zip_btn, 0, 3)
```

3. Dopo il metodo `_choose_dir` (~riga 335), aggiungere:

```python
    def _choose_zip(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr_('zip_browse'), os.path.expanduser("~"),
            self.tr_('zip_filter'))
        if not path:
            return
        self.dir_edit.setText(path)
        # niente scansione siti dal .zip (servirebbe estrarlo nel main
        # thread): la combo torna a "Tutti i siti"
        self.site_combo.clear()
        self.site_combo.addItem(self.tr_('all_sites'), None)
```

- [ ] **Step 4: Verificare che i test del dialog passino**

```bash
python3 -m pytest tests/qfield/test_dialog_import.py -v
```

Atteso: tutti PASS (incluso `test_translations_cover_10_languages`, che ora valida anche le 2 chiavi nuove).

- [ ] **Step 5: Commit**

```bash
git -C "<ROOT>" add gui/qfield_import_dialog.py
git -C "<ROOT>" commit -m "feat(qfield): pulsante Archivio ZIP nel dialog di import (10 lingue)"
```

---

### Task 5: Verifica finale

**Files:**
- Nessun file nuovo; solo verifica.

**Interfaces:**
- Consumes: tutto quanto sopra.
- Produces: suite verde, py_compile pulito.

- [ ] **Step 1: Suite completa qfield**

```bash
cd "<ROOT>"
```

```bash
python3 -m pytest tests/qfield -v
```

Atteso: 41 PASS (33 esistenti + 7 zip + 1 dialog), 0 fail.

- [ ] **Step 2: py_compile su tutti i file toccati**

```bash
python3 -m py_compile "<ROOT>/modules/utility/qfield_importer.py" "<ROOT>/scripts/import_qfield.py" "<ROOT>/gui/qfield_import_dialog.py" && echo OK
```

Atteso: `OK`.

- [ ] **Step 3: Log pulito**

```bash
git -C "<ROOT>" log --oneline -5 && git -C "<ROOT>" status -sb
```

Atteso: 4 commit nuovi (Task 1-4) sopra `902ef916`; nessun file di test in staging.

**Post-implementazione (fuori piano, sessione principale):** invocare gli agenti `tutorial-updater` (tutorial 38, sorgente ZIP, 10 lingue) e `stratigraph-changelog` (voce IT+EN) come da CLAUDE.md. La verifica visiva del pulsante va fatta in QGIS reale.
