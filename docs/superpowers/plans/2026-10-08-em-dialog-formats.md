# La finestra Extended Matrix dice la verità — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Che la finestra «Export Extended Matrix» esporti em.json (non un JSON interno), importi em.json, non offra interruttori che non fanno niente, e porti accanto i comandi dell'Extended Matrix che oggi stanno solo nel menu.

**Architecture:** La finestra resta dov'è (`modules/s3dgraphy/s3dgraphy_dot_bridge.py`), ma smette di essere l'ultimo pezzo di mondo yEd. Il formato JSON diventa quello che EMStudio legge, prodotto dalla funzione che già usiamo dal menu (`modules/s3dgraphy/em_export.export_site`), quindi con il proiettore corretto e la simbologia giusta. L'import sceglie il lettore dall'estensione: em.json di norma, GraphML ancora accettato perché è la via d'ingresso dei vecchi file yEd. Le opzioni che riguardavano solo yEd spariscono; quella che resta fa quello che dice.

**Tech Stack:** Python 3.9 (QGIS), PyQt5, s3dgraphy 1.6.0.dev40 (`ext_libs/`), pytest.

**Spec:** `docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md` (A4: l'export GraphML è stato demolito, em.json è il formato di lavoro, EMStudio il visore; «GraphML sopravvive solo come import una tantum da yEd»).

## Ricognizione (letta il 2026-10-08)

- `S3DGraphyExportDialog.setupUI` (riga 332) costruisce tre caselle formato — DOT, «JSON Format (s3dgraphy native)», «Phased Matrix» — e tre «Processing Options»: **Validate stratigraphic sequence**, **Generate yEd auto-layout hints**, **Apply period-based coloring**.
- `on_export` (riga 486) legge **solo** le tre caselle formato. Le tre Processing Options **non vengono mai lette**: la validazione gira sempre dentro `export_integrated_matrix`, e le altre due parlavano al writer GraphML, che non esiste più.
- La casella JSON produce `self.s3d_integration.export_to_json(...)` → `Extended_Matrix_<sito>_s3dgraphy.json`, un dump interno: **non** è em.json e EMStudio non lo apre.
- `on_export` ha ancora tre rami che stampano l'esito `graphml` / `graphml_status`, e `export_integrated_matrix` ha un blocco swimlane PNG che si attiva su `'graphml' in formats`: codice morto da quando A4 ha ritirato quell'export.
- La descrizione in cima alla scheda dice ancora «yEd-compatible GraphML output».
- La scheda Import legge **GraphML** (`GraphMLImporter`) e passa il grafo a `GraphIngestor.populate_list`, che prende un grafo e non sa da dove venga: basta cambiare lettore.
- La scheda «Verifica rapporti» funziona: sul DB di esempio `check_rapporti` trova **81 problemi** (reciprocità mancanti) per ciascuno dei due siti provati. Nello screenshot la tabella è vuota perché la verifica non era ancora stata eseguita.

## Global Constraints

- **Niente righe di attribuzione AI** in commit, issue, PR, commenti.
- **Solo ramo dev `Stratigraph_00001`.**
- **Confine GPL**: nessun codice EMStudio o del nodo dentro il plugin.
- Nessun `QWebEngineView` istanziato nei test; la finestra non va costruita nei test (serve QGIS): le prove leggono il sorgente o chiamano le funzioni pure.
- Comando di test canonico come negli altri piani di oggi.

## Review Focus

1. **Un sito senza righe.** «Esporta» su un sito vuoto deve dire perché, non lasciare un file da zero nodi o un messaggio di successo.
2. **La cartella scelta non è scrivibile.** L'errore deve arrivare all'utente come frase, non come traccia di stack.
3. **Import di un file che non è né em.json né GraphML** (o un em.json di un'altra versione di schema): messaggio chiaro, nessuna scrittura sul DB.
4. **I comandi EM dentro la finestra non devono duplicare la logica del menu**: se cambia il menu, deve cambiare anche qui — si chiamano le stesse funzioni, non se ne scrivono di gemelle.
5. **La casella «Valida» spenta** deve davvero saltare la validazione, altrimenti è di nuovo un interruttore finto.

---

### Task 1: Il formato JSON è em.json

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (`setupUI`, `on_export`, `export_integrated_matrix`)
- Test: `tests/sync/test_em_dialog_formats.py` (create)

**Interfaces:**
- Consumes: `modules.s3dgraphy.em_export.export_site(connection_url, site, out_dir) -> (path, nodes, edges, warnings)`
- Produces: `S3DGraphyDotBridge.export_integrated_matrix(..., formats=['dot', 'emjson', 'phased'])` — la chiave `'json'` resta accettata come sinonimo di `'emjson'`.

- [ ] **Step 1: Write the failing test**

```python
def test_the_dialog_offers_emjson_not_the_internal_dump():
    source = Path(BRIDGE).read_text()
    assert "em.json" in source
    assert "JSON Format (s3dgraphy native)" not in source


def test_the_export_asks_em_export_for_the_file(monkeypatch, tmp_path):
    """Il file JSON della finestra deve essere quello del menu Extended
    Matrix — stesso proiettore, stessa simbologia."""
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge_mod
    chiamate = []

    def finto_export_site(conn, sito, out_dir):
        chiamate.append((conn, sito, out_dir))
        p = Path(out_dir) / "x.em.json"
        p.write_text("{}")
        return str(p), 3, 2, []

    monkeypatch.setattr(bridge_mod, "export_site", finto_export_site)
    ...
    assert chiamate and out["emjson"].endswith(".em.json")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/sync/test_em_dialog_formats.py -q`
Expected: FAIL — il modulo non espone `export_site` e la casella si chiama ancora «JSON Format (s3dgraphy native)».

- [ ] **Step 3: Write minimal implementation**

In `export_integrated_matrix`, al posto del ramo `'json'`:

```python
        # em.json è il formato di lavoro dell'Extended Matrix (A4): lo
        # produce la stessa funzione del menu, quindi con il proiettore
        # del plugin — filtro del sito, classi giuste, paradati puliti.
        if 'emjson' in formats or 'json' in formats:
            try:
                path, nodes, edges, warnings = export_site(
                    self._connection_url(), site, output_dir)
                exported_files['emjson'] = path
                exported_files['emjson_counts'] = (nodes, edges, warnings)
            except EmExportError as e:
                exported_files['emjson_error'] = str(e)
```

e in `setupUI` la casella diventa:

```python
            self.cb_json = QCheckBox("em.json (Extended Matrix, per EMStudio)")
```

con la descrizione della scheda riscritta:

```python
                "Esporta la matrice del sito: em.json è il formato "
                "dell'Extended Matrix che EMStudio apre; DOT serve a "
                "Graphviz per la matrice di Harris classica."
```

- [ ] **Step 4: Run test to verify it passes**

Run: come allo Step 2. Expected: PASS.

- [ ] **Step 5: L'esito dice i numeri, e gli avvisi**

In `on_export`, il riepilogo per em.json riporta nodi/archi e gli avvisi del proiettore, e il ramo d'errore dice la frase di `EmExportError`. I tre rami `graphml` / `graphml_status` si cancellano, insieme al blocco swimlane di `export_integrated_matrix` che si attivava su `'graphml' in formats`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py tests/sync/test_em_dialog_formats.py
git commit -m "feat(finestra EM): il formato JSON è em.json, quello che EMStudio apre"
```

---

### Task 2: Le opzioni che non facevano niente

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py`
- Test: `tests/sync/test_em_dialog_formats.py`

- [ ] **Step 1: Write the failing test**

```python
def test_no_switch_in_the_dialog_is_a_decoration():
    """Ogni casella costruita in setupUI deve essere letta da on_export:
    le tre «Processing Options» non lo erano (auto-layout e colori
    parlavano al writer GraphML, ritirato in A4)."""
    source = Path(BRIDGE).read_text()
    costruite = set(re.findall(r"self\.(cb_\w+)\s*=\s*QCheckBox", source))
    lette = set(re.findall(r"self\.(cb_\w+)\.isChecked\(\)", source))
    assert costruite - lette == set(), costruite - lette
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL — `{'cb_auto_layout', 'cb_period_colors', 'cb_validate'}` non vengono mai lette.

- [ ] **Step 3: Write minimal implementation**

Via le due caselle yEd; `cb_validate` resta e viene **letta**, passata a `export_integrated_matrix(validate=...)`, che salta `validate_stratigraphic_sequence()` quando è spenta. Etichetta onesta:

```python
            self.cb_validate = QCheckBox(
                "Controlla la sequenza stratigrafica e segnala i problemi")
```

Le caselle dell'import (`cb_create_epochs`, `cb_sql_apply_groups`) sono già lette: il test le copre da ora in poi.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git commit -am "fix(finestra EM): via gli interruttori che non facevano niente"
```

---

### Task 3: L'import legge em.json

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (`_on_browse_import`, `_on_import_preview`, `_on_import_apply`)
- Test: `tests/sync/test_em_dialog_formats.py`

**Interfaces:**
- Produces: `read_graph_for_import(path) -> (graph, warnings)` — funzione di modulo, provabile senza finestra.

- [ ] **Step 1: Write the failing test**

```python
def test_an_emjson_file_can_be_read_back_for_import(tmp_path, sample_db):
    """Quello che la finestra esporta, la finestra lo deve poter
    rileggere: em.json di andata e ritorno."""
    from modules.s3dgraphy.em_export import export_site
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import

    path, _, _, _ = export_site(sample_db, "Scavo archeologico",
                                str(tmp_path / "out"))
    graph, warnings = read_graph_for_import(path)
    assert [n for n in graph.nodes]
    assert any(getattr(n, "node_type", "") == "USVs" for n in graph.nodes)


def test_a_graphml_file_is_still_accepted(tmp_path):
    """GraphML resta la via d'ingresso dei vecchi file yEd (A4)."""
    ...


def test_an_unknown_file_says_so(tmp_path):
    p = tmp_path / "foo.txt"
    p.write_text("ciao")
    with pytest.raises(ValueError, match="em.json"):
        read_graph_for_import(p)
```

- [ ] **Step 2: Run test to verify it fails** — Expected: FAIL, `read_graph_for_import` non esiste.

- [ ] **Step 3: Write minimal implementation**

```python
def read_graph_for_import(path):
    """Il grafo di un file da importare, scelto dall'estensione.

    em.json è il formato di lavoro (A4); GraphML resta accettato perché
    è la via d'ingresso dei file yEd di prima.
    """
    name = str(path).lower()
    if name.endswith(".json"):
        from s3dgraphy.importer.emjson_importer import import_emjson
        return import_emjson(str(path))
    if name.endswith(".graphml"):
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
        except ImportError:
            from s3dgraphy.importer.graphml_importer import GraphMLImporter
        return GraphMLImporter(filepath=str(path)).parse(), []
    raise ValueError(
        "Non so leggere «%s»: serve un em.json (o un .graphml di yEd)."
        % os.path.basename(str(path)))
```

`_on_browse_import` apre il filtro `"Extended Matrix (*.json *.em.json);;yEd (*.graphml)"`, il segnaposto del campo diventa `/percorso/del/sito.em.json`, e la descrizione della scheda viene riscritta. `_on_import_preview` / `_on_import_apply` chiamano `read_graph_for_import` al posto di `GraphMLImporter`, e passano `graphml_path=` solo quando il file è davvero un GraphML.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Run the whole suite** — Expected: PASS a parte il rumore noto.

- [ ] **Step 6: Commit**

```bash
git commit -am "feat(finestra EM): l'import legge em.json, e ancora il GraphML di yEd"
```

---

### Task 4: I comandi dell'Extended Matrix dentro la finestra

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (`setupUI`, nuovi slot)
- Test: `tests/sync/test_em_dialog_formats.py`

**Interfaces:**
- Consumes: `modules.s3dgraphy.em_export.open_in_emstudio(path)`; gli slot del plugin `_run_room_delivery` / `_open_rooms_door` quando il plugin è raggiungibile.

- [ ] **Step 1: Write the failing test**

```python
def test_the_dialog_can_open_what_it_just_exported(monkeypatch, tmp_path):
    """«Apri in EMStudio» agisce sul file appena esportato e non
    reimplementa l'apertura: chiama la funzione del menu."""
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge_mod
    aperti = []
    monkeypatch.setattr(bridge_mod, "open_in_emstudio",
                        lambda p: aperti.append(p) or True)
    bridge_mod.open_exported_emjson({"emjson": str(tmp_path / "x.em.json")})
    assert aperti == [str(tmp_path / "x.em.json")]


def test_the_room_commands_are_the_menu_ones():
    """Niente logica gemella: la finestra chiama gli stessi slot."""
    source = Path(BRIDGE).read_text()
    assert "_run_room_delivery" in source and "_open_rooms_door" in source
```

- [ ] **Step 2: Run test to verify it fails** — Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Una riga di bottoni sotto l'esito dell'export: «Apri in EMStudio» (attivo solo dopo un export riuscito, agisce su `self.exported_files['emjson']`), «Consegna il sito alla stanza…», «Apri la stanza». Gli ultimi due cercano il plugin via `qgis.utils.plugins.get('pyarchinit')` e ne chiamano gli slot; se il plugin non è raggiungibile, il bottone è spento con un tooltip che lo dice.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(finestra EM): da qui si apre EMStudio e si consegna alla stanza"
```

---

### Task 5: «Verifica rapporti» — una prova che risponde

**Files:**
- Test: `tests/sync/test_rapporti_check_live.py` (create)

- [ ] **Step 1: Write the failing test**

```python
def test_the_checker_answers_on_the_sample_site(sample_db):
    """Enzo chiede se la verifica funziona: sul DB di esempio trova le
    reciprocità mancanti (81 al 2026-10-08). La tabella vuota dello
    screenshot è una verifica non ancora lanciata, non un guasto."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    graph = GraphProjector().populate_graph(sample_db, "Scavo archeologico")
    report = RC.check_rapporti(graph, sito="Scavo archeologico")
    assert report.issues
    assert any(i.kind == RC.MISSING_RECIPROCITY for i in report.issues)
```

- [ ] **Step 2: Run test to verify it fails or passes**

Expected: PASS al primo colpo — è una prova di non-regressione su una funzione che già risponde. Se fallisce, è un guasto vero ed entra in questo piano.

- [ ] **Step 3: Commit**

```bash
git add tests/sync/test_rapporti_check_live.py
git commit -m "test(verifica rapporti): la verifica risponde sul DB di esempio"
```

---

## Chiusura

- Suite intera con il comando canonico.
- `tutorial-updater` (la finestra cambia sotto gli occhi dell'utente) poi `stratigraph-changelog`.
- Review indipendente dell'intero ramo prima del tag.
- Release: bump `metadata.txt`, changelog bilingue, tag `em-dialog-5.13.36-alpha`, push ramo + tag, `gh release create --prerelease`, voce api-docs RTD.
