# em.json fedele + conversione USV nei record — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Far uscire in em.json i dati del sito giusto, con la simbologia giusta per ogni tipo di unità, e riscrivere i vecchi codici USVA/USVB/USVC anche dentro i record (`unita_tipo`, `rapporti`, `rapporti2`), non solo nel vocabolario.

**Architecture:** Tre livelli, dal più profondo al più superficiale. (1) Alla **sorgente**: il filtro del sito viaggia nell'importer della libreria, così le righe degli altri siti non entrano nemmeno (oggi entrano e si fondono per omonimia). (2) Nel **proiettore**: ogni nodo prende la classe che il suo `unita_tipo` dichiara, perché `node_type` è quello che EMStudio legge per disegnare; la classe si cambia riassegnando `__class__` sull'istanza, senza toccare archi né indici del grafo. (3) Nei **dati**: la migrazione del vocabolario riscrive anche le due colonne dei rapporti.

**Tech Stack:** Python 3.9 (QGIS), s3dgraphy 1.6.0.dev40 (vendored in `ext_libs/`), SQLite/SQLAlchemy, pytest.

**Spec:** `docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md` (Addendum C). Questo piano nasce da una diagnosi su dati reali, non da una nuova specifica: le misure stanno in «Diagnosi» qui sotto.

## Diagnosi (misurata il 2026-10-08 sul DB demo, sito «Scavo archeologico»)

Il file che Enzo ha guardato in EMStudio (`~/Downloads/Scavo_archeologico_matrix.svg`) mostrava 462 nodi di cui **51 unità tutte `node_type: "US"`**, 172 documenti (di cui metà in francese) e 219 proprietà. Le cause, verificate una per una:

1. **Nessun filtro del sito nell'importer SQLite.** `s3dgraphy.sync.graph_projector.populate_graph` costruisce `PyArchInitImporter(filepath=…, mapping_name=…)` **senza** `filters`, quindi legge tutte le 510 righe dei 10 siti. Il nome del nodo è `{area}.{settore}.{unita_tipo}{us}` e **non contiene il sito**: il sito italiano e quello francese numerano le US allo stesso modo e usano entrambi `US`, così le loro righe **si fondono sullo stesso nodo**, che eredita la documentazione di tutti e due (`Fotografie` + `Photographies`, `Planimetrie` + `Plans`, `Sezioni` + `Coupes`). Misura: senza filtro 210 unità / 342 documenti / 132 epoche; con `filters={'sito': sito}` **51 / 87 / 24**, e i documenti tornano solo italiani. La via PostgreSQL (`import_from_pg`) il sito lo passa già: manca solo su SQLite.
2. **Ogni unità esce come `US`.** `canonical_unita_tipo` non conosce USVA/USVB/USVC (li restituisce identici) e `STRATIGRAPHIC_CLASS_MAP` non li ha, quindi una unità virtuale diventa una US: `node_type: "US"`, `data.symbol: "white rectangle"`, `data.label: "US (or SU)"`. Lo stesso per `SF` (c'è la classe, non ci arriva) e per `CON` (la classe si chiama `BR`). Il `USM` è l'unico caso già corretto per disegno della libreria: resta US con `stratigraphic_kind: "masonry"`.
3. **`us_ops.UNIT_TYPES` manda USVB sul tipo sbagliato.** Dice `"USVB": "USVs"`; la fonte storica (`resources/dbfiles/dot.py`, righe 855-865) assegna a USVA il **parallelogramma** (strutturale, USVs), a USVB l'**esagono** (non strutturale, **USVn**) e a USVC l'**ellisse** (serie, collassata su USVn). La migrazione del vocabolario usa già la mappa giusta. Oggi la consegna alla stanza battezza le USVB come strutturali.
4. **Paradati scritti come unità.** Il DB demo ha 8 righe di `us_table` il cui `unita_tipo` è `property`, `DOC`, `Extractor`, `Combinar`: nate da un round-trip yEd, escono come US. `_PARADATA_UNITA_TIPO` le teneva US di proposito perché il **writer GraphML** smistava la forma da `attributes['unita_tipo']`; quel writer non esiste più (demolito in A4), e em.json smista da `node_type`.
5. **Proprietà vuote che diventano nodi.** 30 dei 219 nodi proprietà hanno `value` uguale alla stringa `"[]"`: la colonna `inclusi` vuota di pyArchInit è `"[]"`, che è una stringa non vuota, e il controllo a monte è `if value and str(value).strip()`.
6. **La migrazione del vocabolario non tocca i record.** `scripts/migrations/_2026_05_us_vocabulary_alignment_lib.py` riscrive solo `us_table.unita_tipo`. Il tipo dell'unità compare anche nei rapporti: `rapporti` è `[tipo, us, area, sito]` (4 colonne, senza tipo di unità) e **`rapporti2` è `[tipo, us, unita_tipo, descr, periodizzazione, area, sito]`** — la posizione 2 è il tipo. Nel DB demo **60 righe** hanno USVA/USVB/USVC dentro `rapporti2`.

## Global Constraints

- **Niente righe di attribuzione AI** in commit, issue, PR, commenti (regola globale dell'utente, vale sempre).
- **Si sviluppa solo sul ramo dev `Stratigraph_00001`**; `master` resta a v4.9.17.
- **Un ponte solo**: i moduli `s3dgraphy.sync` arrivano dalla libreria. Non si forka la libreria: quello che serve a noi vive nel wrapper `modules/s3dgraphy/sync/graph_projector.py`, documentato e rimovibile, e diventa candidato PR upstream (s3Dgraphy#25).
- **Confine GPL**: nessun codice EMStudio/server dentro il plugin; solo HTTP o processo separato.
- s3dgraphy pinnata a `1.6.0.dev40`; `dtcstamp>=0.1.4`.
- Comando di test canonico:
  `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest tests/sync -q --continue-on-collection-errors --ignore=tests/sync/test_groups_dialog_smoke.py --ignore=tests/sync/test_paradata_dialog_smoke.py`
  Rumore noto e accettato: 7 errori d'ambiente (`*_pg` + `yef_migration`, per un pacchetto `tests` estraneo in `~/.local/lib/python3.9/site-packages`), 1 xfail (serializzatore rapporti non identità).
- Mai istanziare un `QWebEngineView` nei test.

## Review Focus

1. **Due esportazioni insieme.** Il filtro del sito si installa sostituendo un simbolo di modulo: due proiezioni concorrenti (una in `QgsTask`, una sul thread GUI) si pesterebbero i piedi. Un lock serializza l'installazione; il test lo esercita con due thread.
2. **Un DB a sito unico non deve cambiare di una virgola.** Il filtro è una restrizione: su un DB con un solo sito il grafo prima e dopo deve essere identico, altrimenti il filtro sta mangiando righe che gli spettano (es. `sito` con spazi o maiuscole diverse).
3. **`SE` non è un evento stratigrafico.** `STRATIGRAPHIC_CLASS_MAP['SE']` è `StratigraphicEventNode`, ma `SE` in pyArchInit è il codice tedesco per US (`canonical_unita_tipo('SE') == 'US'`). Se la riclassificazione legge il codice grezzo invece del canonico, tutte le US del sito tedesco diventano eventi. Lo stesso vale per `UE`, `SU`, `ΣΜ`.
4. **Riassegnare `__class__` deve conservare tutto.** Dopo il cambio di classe il nodo deve avere ancora `node_id`, `name`, `description`, `attributes`, `data`, e gli archi che lo toccano devono restare validi: un nodo riclassificato e poi orfano è un nodo perso.
5. **La migrazione dei record deve essere idempotente e non deve corrompere i rapporti.** Due passaggi di fila danno lo stesso risultato; una riga con `rapporti2` illeggibile (non parsabile) viene lasciata intatta e segnalata, non riscritta a metà.

---

### Task 1: Il filtro del sito alla sorgente

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py`
- Test: `tests/sync/test_graph_projector_multisite.py`

**Interfaces:**
- Consumes: `s3dgraphy.importer.pyarchinit_importer.PyArchInitImporter(filters=…)` (già supportato dalla libreria, parametrizzato e a prova di injection).
- Produces: `_site_filtered_importer(sito)` — context manager usato da `GraphProjector.populate_graph`.

- [ ] **Step 1: Write the failing test**

In `tests/sync/test_graph_projector_multisite.py`, estendi l'helper `_mini_db` perché scriva anche `documentazione`, poi aggiungi:

```python
def test_only_the_sites_own_rows_are_imported(tmp_path):
    """Due siti che numerano le US allo stesso modo non si fondono.

    Il nome del nodo non contiene il sito ({area}.{settore}.{unita_tipo}{us}):
    senza filtro alla sorgente le due righe collassano su un nodo solo, che si
    porta dietro la documentazione di entrambi i siti.
    """
    db = _mini_db(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="1", unita_tipo="US",
             documentazione="[['Fotografie', 'Si']]"),
        dict(sito="Beta", area="1", us="1", unita_tipo="US",
             documentazione="[['Photographies', 'Si']]"),
    ])
    graph = GraphProjector().populate_graph(str(db), "Alfa")
    units = [n for n in graph.nodes if type(n).__name__ == "StratigraphicUnit"]
    assert len(units) == 1, [n.name for n in units]
    docs = sorted(n.name for n in graph.nodes
                  if type(n).__name__ == "DocumentNode")
    assert docs == ["Fotografie"], docs
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest tests/sync/test_graph_projector_multisite.py::test_only_the_sites_own_rows_are_imported -q`
Expected: FAIL — `docs == ['Fotografie', 'Photographies']` (e, se i nomi collidono, una sola unità con due documentazioni).

- [ ] **Step 3: Write minimal implementation**

In `modules/s3dgraphy/sync/graph_projector.py`, in testa al modulo:

```python
#: Il monkeypatch del Task 1 sostituisce un simbolo di modulo: due
#: proiezioni concorrenti (una in QgsTask, una sul thread GUI) si
#: pesterebbero i piedi. Il lock serializza solo l'installazione e la
#: proiezione, che dura decimi di secondo.
_IMPORTER_PATCH_LOCK = threading.RLock()


@contextlib.contextmanager
def _site_filtered_importer(sito):
    """L'importer SQLite della libreria legge solo le righe di ``sito``.

    dev40 costruisce ``PyArchInitImporter`` senza ``filters``, quindi la
    via SQLite legge TUTTA ``us_table``: in un DB multi-sito arrivano
    anche le righe degli altri siti e — poiché l'etichetta del nodo non
    contiene il sito (``{area}.{settore}.{unita_tipo}{us}``) — due siti
    che numerano le unità allo stesso modo collassano su UN nodo, che
    si porta la documentazione, le proprietà e le epoche di entrambi.
    La via PostgreSQL passa già il sito (``import_from_pg``). Candidato
    PR upstream: s3Dgraphy#25.
    """
    import s3dgraphy.importer.pyarchinit_importer as mod

    with _IMPORTER_PATCH_LOCK:
        original = mod.PyArchInitImporter

        class _SiteFiltered(original):
            def __init__(self, *args, **kwargs):
                if not kwargs.get("filters"):
                    kwargs["filters"] = {"sito": sito}
                super().__init__(*args, **kwargs)

        mod.PyArchInitImporter = _SiteFiltered
        try:
            yield
        finally:
            mod.PyArchInitImporter = original
```

con gli import `contextlib` e `threading` in testa, e in `populate_graph`:

```python
        with _site_filtered_importer(sito):
            graph = super().populate_graph(db_path, sito, **kwargs)
```

- [ ] **Step 4: Run test to verify it passes**

Run: come allo Step 2.
Expected: PASS.

- [ ] **Step 5: Il DB a sito unico non cambia, e due thread non si pestano**

```python
def test_a_single_site_db_is_unchanged_by_the_filter(tmp_path):
    db = _mini_db(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="1", unita_tipo="US"),
        dict(sito="Alfa", area="1", us="2", unita_tipo="US"),
    ])
    graph = GraphProjector().populate_graph(str(db), "Alfa")
    assert sorted(n.name for n in graph.nodes
                  if type(n).__name__ == "StratigraphicUnit") == ["1.US1", "1.US2"]


def test_two_projections_at_once_keep_their_own_site(tmp_path):
    """Il patch è un simbolo di modulo: due thread non devono scambiarsi i siti."""
    db = _mini_db(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="1", unita_tipo="US"),
        dict(sito="Beta", area="1", us="2", unita_tipo="US"),
    ])
    import threading
    out = {}

    def run(sito):
        g = GraphProjector().populate_graph(str(db), sito)
        out[sito] = sorted(n.name for n in g.nodes
                           if type(n).__name__ == "StratigraphicUnit")

    threads = [threading.Thread(target=run, args=(s,)) for s in ("Alfa", "Beta")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert out == {"Alfa": ["1.US1"], "Beta": ["1.US2"]}
```

Run: `… -m pytest tests/sync/test_graph_projector_multisite.py -q`
Expected: PASS (tutti).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py tests/sync/test_graph_projector_multisite.py
git commit -m "fix(projector): il filtro del sito viaggia nell'importer, non dopo"
```

---

### Task 2: USVB è non strutturale (la mappa della stanza)

**Files:**
- Modify: `modules/s3dgraphy/room/us_ops.py:34`
- Test: `tests/sync/test_room_us_ops.py`

**Interfaces:**
- Produces: `UNIT_TYPES["USVB"] == "USVn"` (la stessa mappa di `REPLACEMENTS` nella migrazione).

- [ ] **Step 1: Write the failing test**

```python
def test_usvb_is_a_non_structural_virtual_unit():
    """USVA parallelogramma (strutturale), USVB esagono (NON strutturale),
    USVC ellisse (serie → non strutturale): le forme che il vecchio
    esportatore pyArchInit assegnava (resources/dbfiles/dot.py:855-865),
    e la stessa mappa della migrazione del vocabolario."""
    assert UNIT_TYPES["USVA"] == "USVs"
    assert UNIT_TYPES["USVB"] == "USVn"
    assert UNIT_TYPES["USVC"] == "USVn"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/sync/test_room_us_ops.py::test_usvb_is_a_non_structural_virtual_unit -q`
Expected: FAIL — `assert 'USVs' == 'USVn'`.

- [ ] **Step 3: Write minimal implementation**

In `modules/s3dgraphy/room/us_ops.py`, nella tabella `UNIT_TYPES`:

```python
    "USVA": "USVs", "USVB": "USVn", "USVC": "USVn",
```

e aggiorna il commento del modulo (riga 9) in `USVA→USVs, USVB/USVC→USVn (la stessa mappa della migrazione vocabolario)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `… -m pytest tests/sync/test_room_us_ops.py -q`
Expected: PASS (tutti i test del file).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/room/us_ops.py tests/sync/test_room_us_ops.py
git commit -m "fix(room): USVB è una unità virtuale non strutturale (USVn)"
```

---

### Task 3: La classe giusta per ogni unità (la simbologia)

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py`
- Test: `tests/sync/test_graph_projector_multisite.py`, `tests/sync/test_em_export.py`

**Interfaces:**
- Consumes: `s3dgraphy.rapporti.canonical_unita_tipo`, `s3dgraphy.utils.utils.get_stratigraphic_node_class`, `s3dgraphy.nodes.stratigraphic_node.KIND_OF_CODE`.
- Produces: `LEGACY_UNITA_TIPO` (dict), `_class_key_for_unita_tipo(declared) -> str | None`, `_retype_nodes_from_unita_tipo(graph) -> dict[str, int]` (conteggi per tipo, per il changelog e i test).

- [ ] **Step 1: Write the failing test**

In `tests/sync/test_graph_projector_multisite.py`:

```python
def test_each_unit_gets_the_class_its_type_declares(tmp_path):
    """node_type è quello che EMStudio legge per disegnare: una unità
    virtuale non può uscire come 'US' con un rettangolo bianco."""
    db = _mini_db(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="1", unita_tipo="US"),
        dict(sito="Alfa", area="1", us="2", unita_tipo="USVA"),
        dict(sito="Alfa", area="1", us="3", unita_tipo="USVB"),
        dict(sito="Alfa", area="1", us="4", unita_tipo="SF"),
        dict(sito="Alfa", area="1", us="5", unita_tipo="CON"),
        dict(sito="Alfa", area="1", us="6", unita_tipo="USM"),
    ])
    graph = GraphProjector().populate_graph(str(db), "Alfa")
    got = {n.attributes.get("us"): n.node_type
           for n in graph.nodes if n.attributes.get("us")}
    assert got == {"1": "US", "2": "USVs", "3": "USVn", "4": "SF",
                   "5": "BR", "6": "US"}
    usm = next(n for n in graph.nodes if n.attributes.get("us") == "6")
    assert usm.stratigraphic_kind == "masonry"   # USM = US + genere


def test_a_localized_us_code_is_not_a_stratigraphic_event(tmp_path):
    """SE è il codice tedesco per US; STRATIGRAPHIC_CLASS_MAP['SE'] è
    StratigraphicEventNode. Si canonicalizza PRIMA di scegliere la classe."""
    db = _mini_db(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="1", unita_tipo="SE"),
        dict(sito="Alfa", area="1", us="2", unita_tipo="UE"),
        dict(sito="Alfa", area="1", us="3", unita_tipo="ΣΜ"),
    ])
    graph = GraphProjector().populate_graph(str(db), "Alfa")
    assert {n.node_type for n in graph.nodes
            if n.attributes.get("us")} == {"US"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/sync/test_graph_projector_multisite.py -q -k "class_its_type or stratigraphic_event"`
Expected: FAIL — tutti i `node_type` valgono `US` (il primo test), e il secondo passa già ma va tenuto come guardia.

- [ ] **Step 3: Write minimal implementation**

In `modules/s3dgraphy/sync/graph_projector.py`:

```python
#: I codici che pyArchInit usava per le unità virtuali, con la lettura che
#: il suo esportatore storico gli dava (resources/dbfiles/dot.py:855-865):
#: USVA parallelogramma = strutturale, USVB esagono = non strutturale,
#: USVC ellisse (serie) = collassata su non strutturale. La libreria non li
#: conosce: `canonical_unita_tipo` li restituisce identici. Stessa mappa di
#: scripts/migrations/_2026_05_us_vocabulary_alignment_lib.REPLACEMENTS e di
#: room/us_ops.UNIT_TYPES.
LEGACY_UNITA_TIPO = {
    "USVA": "USVs", "USVB": "USVn", "USVC": "USVn", "USVc": "USVn",
}

#: Codici il cui nome di classe nella libreria è un altro: la continuità
#: pyArchInit (CON) è il ContinuityNode, che la libreria chiama BR.
_CLASS_KEY_ALIAS = {"CON": "BR"}


def _class_key_for_unita_tipo(declared):
    """La chiave di STRATIGRAPHIC_CLASS_MAP che ``declared`` dichiara, o None.

    L'ordine conta: prima i codici legacy pyArchInit, poi la
    canonicalizzazione della libreria (che porta UE/SU/SE/ΣΜ su US e i
    codici di muratura su USM), poi gli alias di nome. Al contrario —
    cioè leggendo il codice grezzo — 'SE', che per pyArchInit è il
    tedesco di US, finirebbe su StratigraphicEventNode.
    """
    code = (declared or "").strip()
    if not code:
        return None
    code = LEGACY_UNITA_TIPO.get(code, code)
    try:
        from s3dgraphy.rapporti import canonical_unita_tipo
        code = canonical_unita_tipo(code) or code
    except Exception:                               # noqa: BLE001
        pass
    return _CLASS_KEY_ALIAS.get(code, code)
```

e il passo che riclassifica (chiamato in `populate_graph` subito dopo `_apply_pyarchinit_attributes`):

```python
    @staticmethod
    def _retype_nodes_from_unita_tipo(graph):
        """Dà a ogni nodo la classe che il suo ``unita_tipo`` dichiara.

        ``node_type`` è un attributo DI CLASSE: è quello che em.json
        scrive e che EMStudio legge per scegliere la forma. L'importer
        costruisce tutte le righe come ``StratigraphicUnit`` e tiene il
        genere a parte (``apply_legacy_kind``), così una unità virtuale,
        un reperto o una continuità uscivano come US con il rettangolo
        bianco. Si riassegna ``__class__`` sull'istanza invece di
        sostituire il nodo: identità, attributi e archi restano quelli,
        e il grafo non viene toccato (``add_node(overwrite=True)``
        lascerebbe un avviso per nodo).
        """
        from s3dgraphy.utils.utils import get_stratigraphic_node_class

        counts = {}
        for node in list(graph.nodes):
            attrs = getattr(node, "attributes", None) or {}
            key = _class_key_for_unita_tipo(attrs.get("unita_tipo"))
            if not key:
                continue
            target = get_stratigraphic_node_class(key)
            if target is None or type(node) is target:
                continue
            if getattr(target, "node_type", None) in (None, "StratigraphicNode"):
                continue                     # classe astratta o non tipata
            _become(node, target)
            counts[target.node_type] = counts.get(target.node_type, 0) + 1
        return counts
```

con l'aiutante, in testa al modulo:

```python
#: I campi che appartengono al nodo e non alla sua classe: non si toccano
#: quando il nodo cambia classe.
_IDENTITY_FIELDS = ("node_id", "name", "description", "attributes", "data")


def _become(node, target_cls):
    """``node`` diventa un ``target_cls`` conservando identità e archi.

    Riassegnare ``__class__`` è legale su istanze di classi Python
    normali e non passa da ``__init__``: i campi che la nuova classe
    avrebbe impostato (``symbol``, ``label``, ``detailed_description``…)
    si copiano da un esemplare di prova, gli altri restano quelli del
    nodo.
    """
    probe = target_cls(node_id="_probe", name="_probe")
    node.__class__ = target_cls
    for field, value in vars(probe).items():
        if field in _IDENTITY_FIELDS:
            continue
        current = getattr(node, field, _MISSING)
        if current is _MISSING or current is None:
            setattr(node, field, value)
    return node
```

(`_MISSING = object()` in testa al modulo.) Nota: `symbol`/`label` del nodo vecchio sono quelli della US, quindi NON sono `None` e non verrebbero sovrascritti dal ciclo. Imposta esplicitamente i tre campi di presentazione dall'esemplare:

```python
    for field in ("symbol", "label", "detailed_description"):
        if hasattr(probe, field):
            setattr(node, field, getattr(probe, field))
```

(prima del ciclo generico).

- [ ] **Step 4: Run test to verify it passes**

Run: `… -m pytest tests/sync/test_graph_projector_multisite.py -q`
Expected: PASS.

- [ ] **Step 5: La guardia sull'export: il file parla la simbologia giusta**

In `tests/sync/test_em_export.py`:

```python
def test_the_file_draws_virtual_units_as_virtual(tmp_path):
    """Dal DB al file: una USVA esce USVs, una USVB esce USVn."""
    db = _db_with(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="1", unita_tipo="USVA"),
        dict(sito="Alfa", area="1", us="2", unita_tipo="USVB"),
    ])
    path, _, _, _ = em_export.export_site(_url(db), "Alfa", tmp_path)
    graph = json.loads(Path(path).read_text())["graphs"]["Alfa"]
    types = {n["data"]["us"]: n["node_type"] for n in graph["nodes"]
             if (n.get("data") or {}).get("us")}
    assert types == {"1": "USVs", "2": "USVn"}
    for node in graph["nodes"]:
        if node["node_type"] == "USVs":
            assert node["data"].get("symbol") != "white rectangle"
```

- [ ] **Step 6: Run the whole suite**

Run: il comando canonico su `tests/sync`.
Expected: PASS a parte il rumore noto. **Se il round-trip (ingestor / d13) si rompe**, la causa è che legge `node_type`: è il momento di decidere con una riga di ledger, non di allargare il task.

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py tests/sync/test_graph_projector_multisite.py tests/sync/test_em_export.py
git commit -m "fix(projector): ogni unità con la classe che dichiara (USVs, USVn, SF, BR)"
```

---

### Task 4: I paradati escono come paradati

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py`
- Test: `tests/sync/test_graph_projector_multisite.py`

**Interfaces:**
- Consumes: `_become` e `_retype_nodes_from_unita_tipo` del Task 3.
- Produces: `PARADATA_CLASS_OF` (dict `unita_tipo` → classe della libreria).

- [ ] **Step 1: Write the failing test**

```python
def test_paradata_rows_are_not_stratigraphic_units(tmp_path):
    """Le righe di us_table nate da un round-trip yEd (property, DOC,
    Extractor, Combinar) sono paradati: in em.json devono avere il loro
    node_type, non 'US'. Il writer GraphML che smistava la forma da
    attributes['unita_tipo'] non esiste più (demolito in A4)."""
    db = _mini_db(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="800", unita_tipo="property"),
        dict(sito="Alfa", area="1", us="4001", unita_tipo="DOC"),
        dict(sito="Alfa", area="1", us="400", unita_tipo="Extractor"),
        dict(sito="Alfa", area="1", us="900", unita_tipo="Combinar"),
    ])
    graph = GraphProjector().populate_graph(str(db), "Alfa")
    got = {n.attributes.get("us"): n.node_type
           for n in graph.nodes if n.attributes.get("us")}
    assert got == {"800": "property", "4001": "document",
                   "400": "extractor", "900": "combiner"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/sync/test_graph_projector_multisite.py::test_paradata_rows_are_not_stratigraphic_units -q`
Expected: FAIL — tutti `US`.

- [ ] **Step 3: Write minimal implementation**

In `modules/s3dgraphy/sync/graph_projector.py`:

```python
def _paradata_class_of(declared):
    """La classe paradato che ``declared`` nomina, o None.

    pyArchInit tiene in us_table anche righe che l'Extended Matrix
    considera paradati (l'eredità del round-trip yEd): finché il writer
    GraphML c'era, restavano StratigraphicUnit e la forma la sceglieva
    lui dall'attributo; em.json la sceglie da node_type.
    """
    code = (declared or "").strip()
    if code not in _PARADATA_UNITA_TIPO:
        return None
    from s3dgraphy.nodes.combiner_node import CombinerNode
    from s3dgraphy.nodes.document_node import DocumentNode
    from s3dgraphy.nodes.extractor_node import ExtractorNode
    from s3dgraphy.nodes.property_node import PropertyNode
    return {"property": PropertyNode, "DOC": DocumentNode,
            "Extractor": ExtractorNode, "Combinar": CombinerNode}[code]
```

e in `_retype_nodes_from_unita_tipo`, prima della via stratigrafica:

```python
            target = _paradata_class_of(attrs.get("unita_tipo"))
            if target is None:
                key = _class_key_for_unita_tipo(attrs.get("unita_tipo"))
                ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: come allo Step 2.
Expected: PASS.

- [ ] **Step 5: Run the whole suite** (il round-trip legge `unita_tipo` dagli attributi, che restano)

Run: il comando canonico su `tests/sync`.
Expected: PASS a parte il rumore noto.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py tests/sync/test_graph_projector_multisite.py
git commit -m "fix(projector): i paradati di us_table escono come paradati"
```

---

### Task 5: Igiene dei paradati (niente nodi per il vuoto)

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py`
- Test: `tests/sync/test_graph_projector_multisite.py`

**Interfaces:**
- Produces: `_drop_empty_property_nodes(graph) -> int`.

- [ ] **Step 1: Write the failing test**

```python
def test_an_empty_column_does_not_become_a_property(tmp_path):
    """La colonna `inclusi` vuota di pyArchInit vale la stringa '[]', che a
    monte è un valore non vuoto: 30 dei 219 nodi proprietà del DB demo
    dicevano '[]'."""
    db = _mini_db(tmp_path, rows=[
        dict(sito="Alfa", area="1", us="1", unita_tipo="US", inclusi="[]"),
        dict(sito="Alfa", area="1", us="2", unita_tipo="US",
             inclusi="['ceramica']"),
    ])
    graph = GraphProjector().populate_graph(str(db), "Alfa")
    values = [getattr(n, "value", None) for n in graph.nodes
              if n.node_type == "property"]
    assert "[]" not in values
    assert "['ceramica']" in values
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/sync/test_graph_projector_multisite.py::test_an_empty_column_does_not_become_a_property -q`
Expected: FAIL — `'[]' in values`.

- [ ] **Step 3: Write minimal implementation**

```python
#: Quello che pyArchInit scrive quando una colonna a lista è vuota.
_EMPTY_PROPERTY_VALUES = ("", "[]", "[[]]", "{}", "None", "null")


def _drop_empty_property_nodes(graph):
    """Toglie i nodi proprietà che non dicono niente, e i loro archi."""
    doomed = {n.node_id for n in graph.nodes
              if getattr(n, "node_type", None) == "property"
              and str(getattr(n, "value", "") or "").strip()
              in _EMPTY_PROPERTY_VALUES}
    if not doomed:
        return 0
    graph.nodes = [n for n in graph.nodes if n.node_id not in doomed]
    graph.edges = [e for e in graph.edges
                   if e.edge_source not in doomed
                   and e.edge_target not in doomed]
    if hasattr(graph, "invalidate_indices"):
        graph.invalidate_indices()
    return len(doomed)
```

chiamato in `populate_graph` dopo la riclassificazione.

- [ ] **Step 4: Run test to verify it passes**

Run: come allo Step 2.
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py tests/sync/test_graph_projector_multisite.py
git commit -m "fix(projector): una colonna vuota non diventa un paradato"
```

---

### Task 6: La migrazione riscrive anche i record

**Files:**
- Modify: `scripts/migrations/_2026_05_us_vocabulary_alignment_lib.py`
- Modify: `pyarchinitPlugin.py` (il testo del riepilogo, `_run_vocab_alignment_migration`)
- Test: `tests/migrations/test_us_vocabulary_alignment.py`

**Interfaces:**
- Consumes: `REPLACEMENTS` (già nel modulo).
- Produces: `plan_changes(db)` con le chiavi nuove `rapporti2 (voci)` e `rapporti (voci)`; `apply_changes(db)` con gli stessi conteggi; `rewrite_rapporti_entry(entry, index)` riusabile.

- [ ] **Step 1: Write the failing test**

```python
def test_the_unit_type_is_rewritten_inside_rapporti2(tmp_path):
    """rapporti2 è [tipo, us, unita_tipo, descr, periodo, area, sito]: il
    tipo dell'unità collegata sta in posizione 2 e porta i vecchi codici."""
    db = _db(tmp_path, rows=[dict(
        unita_tipo="USVA",
        rapporti="[['Copre', '3', '1', 'Alfa']]",
        rapporti2="[['Copre', '3', 'USVB', 'muro', '2-1', '1', 'Alfa']]",
    )])
    plan = plan_changes(db)
    assert plan["rapporti2 (voci)"] == 1

    apply_changes(db)
    row = _row(db)
    assert row["unita_tipo"] == "USVs"
    assert ast.literal_eval(row["rapporti2"])[0][2] == "USVn"
    assert row["rapporti"] == "[['Copre', '3', '1', 'Alfa']]"   # intatto


def test_applying_twice_changes_nothing_the_second_time(tmp_path):
    db = _db(tmp_path, rows=[dict(
        unita_tipo="USVB",
        rapporti2="[['Copre', '3', 'USVA', 'muro', '2-1', '1', 'Alfa']]")])
    apply_changes(db)
    first = _row(db)
    second_counts = apply_changes(db)
    assert _row(db) == first
    assert second_counts["rapporti2 (voci)"] == 0


def test_an_unreadable_rapporti2_is_left_alone(tmp_path):
    """Una cella che non si legge si lascia com'è e si conta a parte: mai
    riscritta a metà."""
    db = _db(tmp_path, rows=[dict(unita_tipo="USVA", rapporti2="non una lista")])
    counts = apply_changes(db)
    assert _row(db)["rapporti2"] == "non una lista"
    assert counts["illeggibili"] == 1
    assert _row(db)["unita_tipo"] == "USVs"       # il resto passa lo stesso
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/migrations/test_us_vocabulary_alignment.py -q`
Expected: FAIL — `KeyError: 'rapporti2 (voci)'`.

- [ ] **Step 3: Write minimal implementation**

In `scripts/migrations/_2026_05_us_vocabulary_alignment_lib.py`:

```python
#: Dove, dentro una voce dei rapporti, vive il tipo dell'unità collegata.
#: ``rapporti``  = [tipo, us, area, sito]                      → non c'è
#: ``rapporti2`` = [tipo, us, unita_tipo, descr, periodo, area, sito]
_TYPE_INDEX = {"rapporti": None, "rapporti2": 2}


def _rewrite_entries(raw, type_index):
    """Riscrive i codici legacy in una cella di rapporti.

    Ritorna ``(nuovo_testo, voci_cambiate)``; ``(None, 0)`` se la cella
    non si legge — in quel caso non si tocca niente, perché una lista
    riscritta a metà è peggio di una lista vecchia.
    """
    text = (raw or "").strip()
    if not text or text in ("[]", "[[]]"):
        return None, 0
    try:
        entries = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return None, -1                   # -1 = illeggibile
    if not isinstance(entries, (list, tuple)):
        return None, -1
    changed = 0
    out = []
    for entry in entries:
        item = list(entry) if isinstance(entry, (list, tuple)) else entry
        if (type_index is not None and isinstance(item, list)
                and len(item) > type_index
                and item[type_index] in REPLACEMENTS):
            item[type_index] = REPLACEMENTS[item[type_index]]
            changed += 1
        # il numero dell'unità può portare il codice attaccato (USVA104)
        if isinstance(item, list) and len(item) > 1 and isinstance(item[1], str):
            for src, tgt in REPLACEMENTS.items():
                if item[1].startswith(src):
                    item[1] = tgt + item[1][len(src):]
                    changed += 1
                    break
        out.append(item)
    return (str(out), changed) if changed else (None, 0)
```

e `plan_changes` / `apply_changes` che scorrono `SELECT id_us, unita_tipo, rapporti, rapporti2 FROM us_table`, contano e (solo in `apply_changes`) scrivono con `UPDATE … WHERE id_us = ?`. Le chiavi nuove del dizionario: `"rapporti2 (voci)"`, `"rapporti (voci)"`, `"illeggibili"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `… -m pytest tests/migrations/test_us_vocabulary_alignment.py -q`
Expected: PASS.

- [ ] **Step 5: Il riepilogo del menu dice cosa tocca**

In `pyarchinitPlugin.py::_run_vocab_alignment_migration`, il testo della conferma:

```python
        msg = ("Piano:\n" + "\n".join(f"  {k}: {v}" for k, v in plan.items())
               + "\n\nLa migrazione riscrive il tipo dell'unità e i codici "
                 "dentro i rapporti (colonne «rapporti» e «rapporti2»).")
```

- [ ] **Step 6: Collaudo sul DB demo (copia, non l'originale)**

```bash
cp ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite "$SCRATCHPAD/demo.sqlite"
… -c "from scripts.migrations._2026_05_us_vocabulary_alignment_lib import plan_changes, apply_changes; from pathlib import Path; p=Path('$SCRATCHPAD/demo.sqlite'); print(plan_changes(p)); print(apply_changes(p)); print(plan_changes(p))"
```
Expected: il primo piano conta 30 USVA + 10 USVB + 60 voci in `rapporti2`; dopo l'applicazione il terzo piano conta zero ovunque.

- [ ] **Step 7: Commit**

```bash
git add scripts/migrations/_2026_05_us_vocabulary_alignment_lib.py pyarchinitPlugin.py tests/migrations/test_us_vocabulary_alignment.py
git commit -m "feat(migrazione): i codici USV si riscrivono anche dentro i rapporti"
```

---

## Chiusura

- Suite intera (`tests/sync` + `tests/migrations` + `tests/utility`) con il comando canonico.
- Rigenerare l'em.json del sito demo e misurare prima/dopo (nodi, archi, `node_type`, avvisi EMStudio).
- Review indipendente dell'intero ramo **prima** del tag (lezione di one-bridge): le correzioni entrano nella stessa release.
- Release: bump `metadata.txt`, changelog bilingue, tag `em-fidelity-5.13.35-alpha`, push ramo + tag, `gh release create --prerelease`, voce api-docs RTD.
- Da portare a Emanuel su s3Dgraphy#25: il filtro del sito mancante nell'importer SQLite (con la misura 210→51), USVA/USVB/USVC che `canonical_unita_tipo` non conosce, e `inclusi` vuoto che diventa un nodo proprietà.
