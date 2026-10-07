# Consegna alla stanza (C) + porta del nodo (B2 minimo) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** pyArchInit consegna le US di un sito a una stanza StratiGraph via REST (`POST /v1/rooms/{id}/ops`) e apre la UI delle stanze del nodo — collaudato contro il nodo locale già funzionante (`~/stratigraph-node`, uvicorn :8020).

**Architecture:** tre moduli nuovi sotto `modules/s3dgraphy/room/` — `us_ops.py` (adapter puro: dict di riga → operazioni, id con `stable_id`), `site_rows.py` (us_table → dict di riga + relazioni dai `rapporti` via `s3dgraphy.rapporti.parse_rapporti`), `room_client.py` (il filo: settings per ambiente, preflight `/v1/health`, lotti ≤1000, un `Outcome` leggibile) — più due voci di menu in `pyarchinitPlugin.py`. La logica è il porting dichiarato di `pyarchinit_mini/web_interface/room_client.py` + `connector/us_ops.py` (ramo `stratigraph/09-client-stanza`, già funzionante contro il server), adattato alle DUE differenze nostre: i rapporti vivono nella colonna testuale `us_table.rapporti` (non in una tabella a interi) e il vocabolario dev40 (USM = US con `stratigraphic_kind`).

**Tech Stack:** Python puro + urllib (niente dipendenze nuove); `s3dgraphy.contract.core.stable_id` e `s3dgraphy.rapporti.parse_rapporti` dalla libreria (pin dev40); Qt solo nel cablaggio menu.

**Spec:** `docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md` §C — con l'addendum del Task 0 (le conferme di Emanuel del 2026-10-07 e le misure sul nodo locale).

## Global Constraints

- Branch: feature branch `room-delivery` da `Stratigraph_00001`; merge solo al punto di release. Mai `master`.
- Suite canonica (sempre questa, dal checkout in prova): `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest tests/sync -q --continue-on-collection-errors --ignore=tests/sync/test_groups_dialog_smoke.py --ignore=tests/sync/test_paradata_dialog_smoke.py`. Baseline nota: 0 fail, 1 xfail (serializzatore rapporti), 7 error ambientali (`*_pg` + `test_yef_migration`); sweep `tests/migrations tests/utility`: ≤ 10 fail d'ordinamento (PDF).
- Le regole di Emanuel, non negoziabili: **REST, non WebSocket**; **refused dentro un 200 non è un errore**; **author/ts li scrive il server** (un `author` nel payload viene scartato); **id derivati con `stable_id`, mai uuid4**; **mai `graph_id` nel payload** («una stanza, un grafo vivo» — misurato: con un `graph_id` estraneo ogni op torna refused).
- Il nodo locale per il collaudo: `cd ~/stratigraph-node/stratigraph-server && EM_SERVER_ALLOW_ANON=1 ~/stratigraph-node/venv/bin/uvicorn app.main:app --port 8020` (auth `dev-no-auth`, store in RAM). I test vivi SI SALTANO se `http://127.0.0.1:8020/v1/health` non risponde (stesso patto dei test `*_pg`).
- Token e segreti: MAI in QSettings né su disco — solo env (`STRATIGRAPH_TOKEN`), pattern `modules/storage/credentials.py:ENV_NAMES`. URL e stanza (non segreti) in QSettings con override da env.
- GPL-2 (plugin) vs GPL-3 (server/EMStudio): solo HTTP/processo separato, mai linkare o bundle-are codice loro.
- Commit `feat:`/`fix:`/`test:` senza alcuna riga di AI-attribution (regola utente). Release: bump `metadata.txt` → `5.13.30-alpha`, changelog IT+EN, tag `room-delivery-5.13.30-alpha`, GitHub pre-release, api-docs RTD.

## Review Focus

1. **Un sito con unità `12a` o numeri non interi** — da noi `us` è TEXT e i rapporti citano il testo: devono viaggiare (il client mini NON ci riusciva, join a interi). → test in Task 2.
2. **Due aree con la stessa US** («1» in area A e in area B): un rapporto che cita solo il numero è ambiguo — risolto se unico, altrimenti riportato in `skipped`, mai indovinato. → Task 2.
3. **Riconsegna dello stesso sito**: nodi che fondono + archi `idempotent` dentro `refused` su 200 — `Outcome.a_repeat` vero, il dialogo dice «già consegnato», nessun retry. → Task 3 (finto server) e Task 5 (nodo vero).
4. **Nodo irraggiungibile o che rifiuta (403/413)**: una frase per l'utente, niente traceback, niente coda. → Task 3.
5. **Nodo con auth vera e nessun token**: il rifiuto avviene PRIMA di qualsiasi POST di ops (il preflight `/v1/health` dice `auth`), con la frase che nomina `STRATIGRAPH_TOKEN`. → Task 3.

---

### Task 0: Branch, addendum alla spec, baseline

**Files:**
- Modify: `docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md`

**Interfaces:**
- Produces: worktree `~/pyarchinit-room-delivery` su branch `room-delivery`; la spec dice ciò che il 2026-10-07 ha confermato/misurato.

- [ ] **Step 1: Worktree**

```bash
PLUGIN="/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git -C "$PLUGIN" worktree add -b room-delivery /Users/enzo/pyarchinit-room-delivery Stratigraph_00001
cp -R "$PLUGIN/ext_libs" /Users/enzo/pyarchinit-room-delivery/ext_libs
```

Expected: worktree creato; `ls /Users/enzo/pyarchinit-room-delivery/ext_libs/s3dgraphy-1.6.0.dev40.dist-info` esiste.

- [ ] **Step 2: Addendum alla spec** — in coda alla sezione C aggiungere (testo esatto):

```markdown
#### Addendum C — conferme di Emanuel e misure sul nodo locale (2026-10-07, sera)

- Il server è **FastAPI/Python** (`StratiGraph-ECCCH/stratigraph-server`, GPL-3), non axum: «StratiGraph Server adds no logic», ogni endpoint chiama `s3dgraphy.api`. La nota sui due livelli: `docs/SYNC-FIELD-TO-CLOUD.md`.
- pyArchInit sta sul livello **REST**: `POST /v1/rooms/{id}/ops`, ≤ `OPS_BATCH_MAX` (1000) op per chiamata, 413 oltre; serve ruolo **editor**; `author` nel payload scartato (lo scrive il server dal token Keycloak/ORCID).
- **Misurato in locale** (venv + `EM_SERVER_ALLOW_ANON=1`, porta 8020): 1ª consegna 4/4 applied; riconsegna 3 merge (`add_node` FONDE) + 1 `idempotent` in `refused` su HTTP 200. **Mai `graph_id` nel payload**: una stanza ha UN grafo vivo, con un id estraneo tutto torna refused («the graph X is not in this study»).
- Merge CRDT **per campo**: «if you write a field, stamp it» — chi non stampa degrada a last-writer-wins sul nodo, correttamente.
- Op shape (dal client di riferimento `pyarchinit-mini`, ramo `stratigraph/09-client-stanza`): `add_node` col payload DENTRO `node` (al top level verrebbe accettato e perso); `add_edge` piatto (`source`,`target`,`edge_type`) con id `source__edge_type__target` (convenzione di EMStudio: l'arco disegnato a mano e il nostro sono UNO); id unità `stable_id(ORIGIN,"us",sito,area,us)`.
- B2 minimo: la UI delle stanze è servita dal nodo stesso — `/em/rooms/` dietro Caddy, `/rooms/` sul nodo nudo.
```

- [ ] **Step 3: Baseline** — suite canonica dal worktree, salvare l'ultima riga in `docs/superpowers/plans/2026-10-07-room-delivery-baseline.txt`.

Run: la suite canonica. Expected: `0 failed` (xfail/error come da Global Constraints).

- [ ] **Step 4: Commit** — `docs(spec): addendum C — conferme Emanuel + misure nodo locale (REST, refused-in-200, niente graph_id)`

### Task 1: `us_ops.py` — l'adapter puro, lato unità (TDD)

**Files:**
- Create: `modules/s3dgraphy/room/__init__.py`, `modules/s3dgraphy/room/us_ops.py`
- Test: `tests/sync/test_room_us_ops.py` (nuovo)

**Interfaces:**
- Consumes: `s3dgraphy.contract.core.stable_id`; `s3dgraphy.nodes.stratigraphic_node.KIND_OF_CODE` (dev40: codici → (kind, classe)).
- Produces: `ORIGIN = "pyarchinit"`; `normalize_area(v) -> str`; `unit_id(sito, area, us) -> str`; `edge_id(source, edge_type, target) -> str` (= `f"{source}__{edge_type}__{target}"`); `Delivery` dataclass (`ops: list`, `skipped: list[str]`, `counts: dict`, metodo `bump(key)`); `ops_for_units(units, delivery=None) -> Delivery`. Una unità = dict con chiavi di `us_table` (`sito`,`area`,`us`,`unita_tipo`,`d_stratigrafica`,`d_interpretativa`,`descrizione`,`interpretazione`,`periodo_iniziale`,`fase_iniziale`,`periodo_finale`,`fase_finale`,`anno_scavo`,`scavato`).

- [ ] **Step 1: Test rossi** — `tests/sync/test_room_us_ops.py` con l'header sys.path standard dei test sync (PLUGIN_ROOT + ext_libs inserito davanti, purge s3dgraphy; copiare da `tests/sync/test_em_export.py` righe 17-20):

```python
def test_unit_ids_are_stable_and_origin_bound():
    from modules.s3dgraphy.room.us_ops import unit_id
    a = unit_id("Scavo", "1", "12a")
    assert a == unit_id("Scavo", "1", "12a")          # deterministico
    assert a != unit_id("Scavo", "2", "12a")          # l'area identifica
    assert a != unit_id("Scavo", "1", "12")           # il testo conta ("12a" ≠ "12")


def test_a_plain_us_becomes_an_add_node_with_payload_inside_node():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([{"sito": "S", "area": "1", "us": "3",
                           "unita_tipo": "US",
                           "d_stratigrafica": "strato", "scavato": "Si"}])
    assert len(made.ops) == 1
    op = made.ops[0]
    assert op["op"] == "add_node" and "node" in op
    assert op["node"]["node_type"] == "US"
    assert op["node"]["name"] == "3"
    assert op["node"]["data"]["site"] == "S"
    assert op["node"]["data"]["origin"] == "pyarchinit"
    assert "node_type" not in op, "il tipo al top level viene PERSO dal CRDT"


def test_masonry_and_coating_travel_as_us_with_a_kind():
    # dev40: USM è una US con stratigraphic_kind='masonry'; i codici
    # localizzati (WSU...) idem. Il codice d'origine resta in source_code.
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "S", "area": "1", "us": "4", "unita_tipo": "USM"},
        {"sito": "S", "area": "1", "us": "5", "unita_tipo": "WSU"},
        {"sito": "S", "area": "1", "us": "6", "unita_tipo": "USR"},
    ])
    kinds = {o["node"]["name"]: (o["node"]["node_type"],
                                 o["node"]["data"].get("stratigraphic_kind"),
                                 o["node"]["data"].get("source_code"))
             for o in made.ops}
    assert kinds["4"] == ("US", "masonry", "USM")
    assert kinds["5"] == ("US", "masonry", "WSU")
    assert kinds["6"] == ("US", "coating", "USR")


def test_virtual_units_keep_their_class_and_legacy_codes_remap():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "S", "area": "1", "us": "7", "unita_tipo": "USVs"},
        {"sito": "S", "area": "1", "us": "8", "unita_tipo": "USVA"},
    ])
    types = {o["node"]["name"]: o["node"]["node_type"] for o in made.ops}
    assert types == {"7": "USVs", "8": "USVs"}
    assert made.counts.get("units_remapped_USVA_to_USVs") == 1


def test_rows_that_cannot_be_nodes_are_reported_not_invented():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "", "area": "1", "us": "1"},              # senza sito
        {"sito": "S", "area": "1", "us": "9",
         "unita_tipo": "DOC"},                              # paradata: non US
    ])
    assert made.ops == []
    assert len(made.skipped) == 2
```

- [ ] **Step 2: Run — FAIL** (`ModuleNotFoundError: modules.s3dgraphy.room`).

Run: `pytest tests/sync/test_room_us_ops.py -q` (env canonico). Expected: 5 FAILED/errors di import.

- [ ] **Step 3: Implementazione.** `__init__.py` con una riga di docstring («La consegna di un sito a una stanza StratiGraph. REST, mai WebSocket — spec 2026-10-07 §C.»). `us_ops.py`:

```python
"""us_table → operazioni per la stanza. Puro: niente Qt, niente rete, niente DB.

Porting dichiarato di ``pyarchinit_mini/connector/us_ops.py`` (ramo
stratigraph/09-client-stanza), con le differenze NOSTRE scritte qui:

- il vocabolario è quello dev40: USM/USR/USS e i codici localizzati (WSU,
  MSE, …) viaggiano come ``US`` con ``stratigraphic_kind`` in ``data`` e il
  codice d'origine in ``source_code`` (``KIND_OF_CODE`` della libreria);
- USVA/USVB→USVs, USVC→USVn (la stessa mappa della migrazione vocabolario);
- i paradata (DOC, Combinar, Extractor, property, CON) NON diventano nodi
  stratigrafici della stanza: riportati in ``skipped``.

IL PAYLOAD VA DENTRO ``node``: il CRDT legge ``op["node"]`` e un ``node_type``
al top level viene accettato e PERSO in silenzio (misurato da mini,
crdt.py:727). L'id di un arco è ``source__edge_type__target`` — la stessa
convenzione di EMStudio, così l'arco disegnato a mano e il nostro sono UNO.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from s3dgraphy.contract.core import stable_id

ORIGIN = "pyarchinit"

#: unita_tipo → node_type della stanza. I codici-kind (USM, WSU, …) NON
#: stanno qui: li risolve KIND_OF_CODE come US+kind. None = paradata, mai
#: un nodo stratigrafico della stanza.
UNIT_TYPES: Dict[str, Optional[str]] = {
    "US": "US", "SF": "SF", "USD": "USD", "VSF": "VSF", "RSF": "RSF",
    "TSU": "TSU", "UL": "UL",
    "USVs": "USVs", "USVn": "USVn", "USVc": "USVn",
    "USVA": "USVs", "USVB": "USVs", "USVC": "USVn",
    "serSU": "serSU", "serUSVn": "serUSVn", "serUSVs": "serUSVs",
    "DOC": None, "Combinar": None, "Extractor": None, "property": None,
    "CON": None,
}
DEFAULT_UNIT_TYPE = "US"

#: colonna → nome nel ``data`` del nodo (il sottoinsieme che serve a chi
#: ragiona sulla stratigrafia; il resto resta nel database di scavo).
UNIT_FIELDS: Dict[str, str] = {
    "sito": "site", "area": "area", "us": "unit",
    "d_stratigrafica": "stratigraphic_definition",
    "d_interpretativa": "interpretive_definition",
    "descrizione": "description", "interpretazione": "interpretation",
    "periodo_iniziale": "period_start", "fase_iniziale": "phase_start",
    "periodo_finale": "period_end", "fase_finale": "phase_end",
    "anno_scavo": "excavation_year", "scavato": "excavated",
}


def normalize_area(area: Any) -> str:
    return "" if area is None else str(area).strip()


def unit_id(sito: Any, area: Any, us: Any) -> str:
    return stable_id(ORIGIN, "us", str(sito or "").strip(),
                     normalize_area(area), str(us or "").strip())


def edge_id(source: str, edge_type: str, target: str) -> str:
    return f"{source}__{edge_type}__{target}"


@dataclass
class Delivery:
    ops: List[Dict[str, Any]] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)

    def bump(self, key: str) -> None:
        self.counts[key] = self.counts.get(key, 0) + 1


def _resolve_type(declared: str):
    """(node_type, kind, source_code) per una unita_tipo, o (None, …) = skip."""
    if not declared:
        return DEFAULT_UNIT_TYPE, None, None
    if declared in UNIT_TYPES:
        return UNIT_TYPES[declared], None, None
    try:
        from s3dgraphy.nodes.stratigraphic_node import KIND_OF_CODE
        kind = KIND_OF_CODE.get(declared)
    except Exception:
        kind = None
    if kind:
        return "US", kind, declared
    return False, None, None          # sconosciuta: riportata, mai inventata


def _node_data(row: Dict[str, Any], kind, source_code) -> Dict[str, Any]:
    kept: Dict[str, Any] = {}
    for column, name in UNIT_FIELDS.items():
        value = row.get(column)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        kept[name] = value.strip() if isinstance(value, str) else value
    if kind:
        kept["stratigraphic_kind"] = kind
        kept["source_code"] = source_code
    kept["origin"] = ORIGIN
    return kept


def ops_for_units(units: Iterable[Dict[str, Any]],
                  delivery: Optional[Delivery] = None) -> Delivery:
    made = delivery if delivery is not None else Delivery()
    for row in units:
        sito, us = row.get("sito"), row.get("us")
        if not str(sito or "").strip() or not str(us or "").strip():
            made.skipped.append(
                "riga con sito=%r e us=%r: senza sito o numero una unità "
                "non è identificabile" % (sito, us))
            made.bump("units_unidentifiable")
            continue
        declared = str(row.get("unita_tipo") or "").strip()
        node_type, kind, source_code = _resolve_type(declared)
        if node_type is None:
            made.skipped.append(
                "%s/%s/%s: %r è paradata, non una unità della stanza"
                % (sito, normalize_area(row.get("area")), us, declared))
            made.bump("units_paradata_%s" % declared)
            continue
        if node_type is False:
            made.skipped.append(
                "%s/%s/%s: unita_tipo=%r senza corrispondente nel datamodel "
                "— lasciata fuori, mai approssimata"
                % (sito, normalize_area(row.get("area")), us, declared))
            made.bump("units_unmappable_type_%s" % declared)
            continue
        if not declared:
            made.bump("units_typed_by_default")
        elif declared in UNIT_TYPES and UNIT_TYPES[declared] != declared:
            made.bump("units_remapped_%s_to_%s"
                      % (declared, UNIT_TYPES[declared]))
        made.ops.append({
            "op": "add_node",
            "id": unit_id(sito, row.get("area"), us),
            "node": {
                "node_type": node_type,
                "name": str(us).strip(),
                "description": (row.get("d_stratigrafica") or "").strip() or None,
                "data": _node_data(row, kind, source_code),
            },
        })
        made.bump("units")
    return made
```

- [ ] **Step 4: Run — PASS** (`pytest tests/sync/test_room_us_ops.py -q` → 5 passed).
- [ ] **Step 5: Commit** — `feat(room): adapter unità → add_node (stable_id, kind dev40, payload dentro node)`

### Task 2: rapporti → `add_edge` (TDD)

**Files:**
- Modify: `modules/s3dgraphy/room/us_ops.py`
- Create: `modules/s3dgraphy/room/site_rows.py`
- Test: `tests/sync/test_room_us_ops.py` (estendere)

**Interfaces:**
- Consumes: `s3dgraphy.rapporti.parse_rapporti(raw) -> [(edge_type, target_us, area, sito, swap)]` (grafie canoniche `equals`/`bonded_to`, le vecchie restano leggibili); `unit_id`/`edge_id` del Task 1.
- Produces: `ops_for_relationships(relationships, known, delivery=None) -> Delivery` dove una relazione = dict `{"sito","area","us","edge_type","target_us","target_area","target_sito","swap","verb"}`; `SYMMETRIC = {"equals","bonded_to","has_same_time","is_physically_equal_to","is_bonded_to"}`; `site_rows.load(conn_str, sito) -> (units, relationships)` (SQLAlchemy, SELECT su us_table, parse dei rapporti riga per riga).

- [ ] **Step 1: Test rossi** (estendere il file del Task 1):

```python
def _known(*triples):
    from modules.s3dgraphy.room.us_ops import unit_id, normalize_area
    return {(s, normalize_area(a), u): unit_id(s, a, u) for s, a, u in triples}


def test_a_directional_rapporto_becomes_one_oriented_edge():
    from modules.s3dgraphy.room.us_ops import ops_for_relationships, unit_id
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "1", "edge_type": "overlies",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Copre"}], known)
    assert len(made.ops) == 1
    op = made.ops[0]
    assert op["op"] == "add_edge" and op["edge_type"] == "overlies"
    assert op["source"] == unit_id("S", "1", "1")
    assert op["target"] == unit_id("S", "1", "2")
    assert op["attributes"]["pyarchinit_relationship"] == "Copre"
    assert op["id"] == "%s__overlies__%s" % (op["source"], op["target"])


def test_swap_means_the_target_is_the_source():
    # «Coperto da 2» sulla riga 1 = 2 overlies 1 (parse_rapporti: swap=True)
    from modules.s3dgraphy.room.us_ops import ops_for_relationships, unit_id
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "1", "edge_type": "overlies",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": True, "verb": "Coperto da"}], known)
    assert made.ops[0]["source"] == unit_id("S", "1", "2")
    assert made.ops[0]["target"] == unit_id("S", "1", "1")


def test_the_inverse_pair_collapses_to_one_edge():
    # 1 Copre 2 + 2 Coperto da 1 → UN arco (stesso edge_id dopo orientazione)
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    made = ops_for_relationships([
        {"sito": "S", "area": "1", "us": "1", "edge_type": "overlies",
         "target_us": "2", "target_area": "1", "target_sito": "S",
         "swap": False, "verb": "Copre"},
        {"sito": "S", "area": "1", "us": "2", "edge_type": "overlies",
         "target_us": "1", "target_area": "1", "target_sito": "S",
         "swap": True, "verb": "Coperto da"},
    ], known)
    assert len(made.ops) == 1
    assert made.counts.get("edges_deduplicated") == 1


def test_symmetric_edges_have_one_canonical_orientation():
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "1", "1"), ("S", "1", "2"))
    a = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "1", "edge_type": "equals",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Uguale a"}], known).ops[0]
    b = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "2", "edge_type": "equals",
          "target_us": "1", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Uguale a"}], known).ops[0]
    assert a["id"] == b["id"], "stessa relazione = stesso arco, da qualsiasi lato"


def test_alphanumeric_units_can_be_cited():
    # Review Focus 1: '12a' è TEXT da noi e deve viaggiare (mini non poteva)
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "1", "12a"), ("S", "1", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "1", "us": "12a", "edge_type": "cuts",
          "target_us": "2", "target_area": "1", "target_sito": "S",
          "swap": False, "verb": "Taglia"}], known)
    assert len(made.ops) == 1 and not made.skipped


def test_an_ambiguous_bare_number_is_reported_not_guessed():
    # Review Focus 2: il target '1' esiste in due aree, il rapporto non dice quale
    from modules.s3dgraphy.room.us_ops import ops_for_relationships
    known = _known(("S", "A", "1"), ("S", "B", "1"), ("S", "A", "2"))
    made = ops_for_relationships(
        [{"sito": "S", "area": "A", "us": "2", "edge_type": "overlies",
          "target_us": "1", "target_area": "", "target_sito": "S",
          "swap": False, "verb": "Copre"}], known)
    assert made.ops == []
    assert any("ambigu" in s for s in made.skipped)


def test_site_rows_reads_units_and_parses_rapporti(tmp_path):
    import sqlite3
    db = tmp_path / "s.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, node_uuid TEXT,
        rapporti TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        descrizione TEXT, interpretazione TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        anno_scavo TEXT, scavato TEXT)""")
    rows = [("S", "1", "1", "US", '[["Copre", "2", "1", "S"]]'),
            ("S", "1", "2", "USM", "[]"),
            ("ALTRO", "1", "9", "US", "[]")]
    conn.executemany(
        "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
        "VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit(); conn.close()
    from modules.s3dgraphy.room.site_rows import load
    units, rels = load("sqlite:///%s" % db, "S")
    assert {u["us"] for u in units} == {"1", "2"}      # un sito per consegna
    assert len(rels) == 1 and rels[0]["edge_type"] == "overlies"
    assert rels[0]["target_us"] == "2" and rels[0]["verb"] == "Copre"
```

- [ ] **Step 2: Run — FAIL** (funzioni mancanti). Expected: 7 FAILED.

- [ ] **Step 3: Implementazione.** In `us_ops.py` aggiungere:

```python
SYMMETRIC = {"equals", "bonded_to", "has_same_time",
             "is_physically_equal_to", "is_bonded_to"}


def _resolve_target(rel, known):
    """L'id del target, o (None, perché)."""
    sito = str(rel.get("target_sito") or rel.get("sito") or "").strip()
    area = normalize_area(rel.get("target_area"))
    us = str(rel.get("target_us") or "").strip()
    if area:
        hit = known.get((sito, area, us))
        return (hit, None) if hit else (
            None, "unità %s/%s/%s non consegnata" % (sito, area, us))
    hits = [v for (s, _a, u), v in known.items() if s == sito and u == us]
    if len(hits) == 1:
        return hits[0], None
    if not hits:
        return None, "unità %s/?/%s non consegnata" % (sito, us)
    return None, ("il numero %s/%s è ambiguo fra %d aree: il rapporto non "
                  "dice quale" % (sito, us, len(hits)))


def ops_for_relationships(relationships, known, delivery=None):
    """`add_edge` per ogni rapporto risolvibile, UNA volta per relazione.

    La coppia inversa (1 Copre 2 / 2 Coperto da 1) produce lo stesso arco
    orientato: dedup per ``edge_id``. Le simmetriche (equals, bonded_to…)
    viaggiano con gli estremi in ordine lessicografico, così la stessa
    relazione scritta dai due lati è UN arco.
    """
    made = delivery if delivery is not None else Delivery()
    seen = set()
    for rel in relationships:
        src = known.get((str(rel.get("sito") or "").strip(),
                         normalize_area(rel.get("area")),
                         str(rel.get("us") or "").strip()))
        if not src:
            made.skipped.append(
                "rapporto da %s/%s/%s: la riga stessa non è stata consegnata"
                % (rel.get("sito"), rel.get("area"), rel.get("us")))
            made.bump("edges_source_missing")
            continue
        dst, why = _resolve_target(rel, known)
        if not dst:
            made.skipped.append("rapporto %r di %s/%s/%s: %s"
                                % (rel.get("verb"), rel.get("sito"),
                                   rel.get("area"), rel.get("us"), why))
            made.bump("edges_unresolved")
            continue
        edge_type = rel["edge_type"]
        source, target = (dst, src) if rel.get("swap") else (src, dst)
        if edge_type in SYMMETRIC and target < source:
            source, target = target, source
        eid = edge_id(source, edge_type, target)
        if eid in seen:
            made.bump("edges_deduplicated")
            continue
        seen.add(eid)
        made.ops.append({
            "op": "add_edge", "id": eid,
            "source": source, "target": target, "edge_type": edge_type,
            "attributes": {"pyarchinit_relationship": rel.get("verb") or ""},
        })
        made.bump("edges")
    return made


def deliver(units, relationships=()):
    """Tutto il sito in operazioni: prima i nodi, poi gli archi fra loro."""
    units = list(units)
    made = ops_for_units(units)
    known = {(str(r.get("sito") or "").strip(),
              normalize_area(r.get("area")),
              str(r.get("us") or "").strip()):
             unit_id(r.get("sito"), r.get("area"), r.get("us"))
             for r in units
             if str(r.get("sito") or "").strip()
             and str(r.get("us") or "").strip()}
    # solo le unità DIVENTATE nodi possono essere estremi
    delivered = {op["id"] for op in made.ops}
    known = {k: v for k, v in known.items() if v in delivered}
    return ops_for_relationships(relationships, known, made)
```

`site_rows.py` (nuovo, intero):

```python
"""us_table → righe per l'adapter. SQLAlchemy, un sito per consegna.

I rapporti si leggono dalla colonna TESTUALE ``us_table.rapporti`` con
``s3dgraphy.rapporti.parse_rapporti`` — il client mini li prendeva da una
tabella a interi e un'unità «12a» non poteva essere citata; da noi può.
``parse_rapporti`` dà ``(edge_type, target_us, area, sito, swap)`` già nelle
grafie canoniche, vecchie comprese.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

#: le colonne che l'adapter legge (UNIT_FIELDS + identità + rapporti)
_COLUMNS = ("sito", "area", "us", "unita_tipo", "rapporti",
            "d_stratigrafica", "d_interpretativa", "descrizione",
            "interpretazione", "periodo_iniziale", "fase_iniziale",
            "periodo_finale", "fase_finale", "anno_scavo", "scavato")


def load(conn_str: str, sito: str) -> Tuple[List[Dict[str, Any]],
                                            List[Dict[str, Any]]]:
    from sqlalchemy import create_engine, text

    from s3dgraphy.rapporti import parse_rapporti

    engine = create_engine(conn_str)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT %s FROM us_table WHERE sito = :s"
                % ", ".join(_COLUMNS)), {"s": sito}).fetchall()
    finally:
        engine.dispose()

    units: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []
    for row in rows:
        unit = dict(zip(_COLUMNS, row))
        units.append(unit)
        raw = unit.get("rapporti")
        if not raw:
            continue
        try:
            parsed = parse_rapporti(raw)
        except Exception:
            parsed = []
        for verb_entry, (edge_type, target_us, area, t_sito, swap) in zip(
                _verbs(raw), parsed):
            relationships.append({
                "sito": unit["sito"], "area": unit["area"], "us": unit["us"],
                "edge_type": edge_type, "target_us": target_us,
                "target_area": area, "target_sito": t_sito or unit["sito"],
                "swap": swap, "verb": verb_entry,
            })
    return units, relationships


def _verbs(raw) -> List[str]:
    """La parola dell'archeologo, nell'ordine delle voci parse-ate."""
    import ast
    import json
    try:
        entries = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        try:
            entries = ast.literal_eval(raw)
        except Exception:
            return []
    out = []
    for e in entries or []:
        if isinstance(e, (list, tuple)) and e and str(e[0] or "").strip():
            out.append(str(e[0]).strip())
    return out
```

> Nota per l'esecutore: se `parse_rapporti` scarta voci vuote, lo zip di `_verbs` può disallineare — verificare con il test e, se serve, far restituire a `_verbs` solo le voci che `parse_rapporti` accetta (stesso filtro: primo campo non vuoto E voce riconosciuta). Il test `test_site_rows_reads_units_and_parses_rapporti` è il giudice.

- [ ] **Step 4: Run — PASS** (`pytest tests/sync/test_room_us_ops.py -q` → 12 passed).
- [ ] **Step 5: Commit** — `feat(room): rapporti testuali → add_edge (parse canonico, dedup inversi, simmetriche canoniche, '12a' cittadino)`

### Task 3: `room_client.py` — il filo (TDD, server finto)

**Files:**
- Create: `modules/s3dgraphy/room/room_client.py`
- Test: `tests/sync/test_room_client.py` (nuovo)

**Interfaces:**
- Consumes: `us_ops.deliver`, `site_rows.load`.
- Produces: `NodeSettings` (`server_url`, `room_id`, `token`; da env `STRATIGRAPH_SERVER_URL`/`STRATIGRAPH_ROOM_ID`/`STRATIGRAPH_TOKEN` con fallback QSettings `pyarchinit/stratigraph/server_url|room_id` — il token MAI da QSettings); `RoomRefusal(RuntimeError)`; `Outcome` (`sent`,`applied`,`refused`,`skipped`,`counts`,`batches`, proprietà `idempotent`,`other_refusals`,`a_repeat`, metodo `summary()`); `preflight(server_url, http=...) -> dict` (GET `/v1/health`); `deliver_site(conn_str, sito, settings=None, http=None) -> Outcome`; `rooms_door(server_url, http=None) -> str` (la prima fra `/em/rooms/` e `/rooms/` che risponde 200); `BATCH_MAX = 1000`.
- `http` è un callable iniettabile `(method, url, payload, token) -> (status, dict)` con default urllib — è ciò che rende il modulo testabile senza rete.

- [ ] **Step 1: Test rossi** — `tests/sync/test_room_client.py` (header sys.path standard; `monkeypatch` per le env):

```python
class FakeNode:
    """Un nodo finto: registra le chiamate, risponde come quello vero."""

    def __init__(self, auth="dev-no-auth", applied_all=True):
        self.calls = []
        self.auth = auth
        self.applied_all = applied_all

    def __call__(self, method, url, payload, token):
        self.calls.append((method, url, payload, token))
        if url.endswith("/v1/health"):
            return 200, {"ok": True, "auth": self.auth}
        if "/ops" in url:
            ops = payload["ops"]
            if self.applied_all:
                return 200, {"applied": len(ops), "refused": [], "kept": None}
            return 200, {"applied": 0,
                         "refused": [{"id": o["id"], "reason": "idempotent"}
                                     for o in ops], "kept": None}
        raise AssertionError(url)


def _settings(monkeypatch, url="http://127.0.0.1:9", room="r1", token=""):
    monkeypatch.setenv("STRATIGRAPH_SERVER_URL", url)
    monkeypatch.setenv("STRATIGRAPH_ROOM_ID", room)
    if token:
        monkeypatch.setenv("STRATIGRAPH_TOKEN", token)
    else:
        monkeypatch.delenv("STRATIGRAPH_TOKEN", raising=False)
    from modules.s3dgraphy.room.room_client import NodeSettings
    return NodeSettings()


UNITS = [{"sito": "S", "area": "1", "us": str(n), "unita_tipo": "US"}
         for n in range(1, 4)]


def test_no_settings_no_delivery_and_no_network(monkeypatch, tmp_path):
    monkeypatch.delenv("STRATIGRAPH_SERVER_URL", raising=False)
    monkeypatch.delenv("STRATIGRAPH_ROOM_ID", raising=False)
    import pytest as _pytest
    from modules.s3dgraphy.room import room_client
    # il fallback QSettings legge le preferenze REALI dell'utente: un uso
    # manuale precedente del dialogo non deve rendere flaky questo test
    monkeypatch.setattr(room_client, "_qsetting", lambda key: "")
    node = FakeNode()
    with _pytest.raises(room_client.RoomRefusal) as err:
        room_client.deliver_site("sqlite:///nowhere", "S",
                                 settings=room_client.NodeSettings(),
                                 http=node)
    assert "STRATIGRAPH_SERVER_URL" in str(err.value)
    assert node.calls == [], "niente configurazione → niente rete"


def test_enforcing_auth_without_token_refuses_before_any_ops(monkeypatch):
    import pytest as _pytest
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)                       # nessun token
    node = FakeNode(auth="keycloak")
    with _pytest.raises(room_client.RoomRefusal) as err:
        room_client._require_identity(st, node)
    assert "STRATIGRAPH_TOKEN" in str(err.value)
    assert [c for c in node.calls if "/ops" in c[1]] == []


def test_batches_are_capped_at_1000_and_all_arrive(monkeypatch):
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)
    node = FakeNode()
    ops = [{"op": "add_node", "id": "n%d" % i, "node": {}}
           for i in range(2300)]
    out = room_client._deliver_ops(ops, st, node)
    posts = [c for c in node.calls if "/ops" in c[1]]
    assert [len(c[2]["ops"]) for c in posts] == [1000, 1000, 300]
    assert out.sent == 2300 and out.applied == 2300 and out.batches == 3
    assert all("graph_id" not in c[2] for c in posts), \
        "una stanza, un grafo vivo: mai graph_id"


def test_a_repeat_reads_as_already_delivered(monkeypatch):
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)
    node = FakeNode(applied_all=False)                # tutto idempotent
    ops = [{"op": "add_edge", "id": "e%d" % i} for i in range(4)]
    out = room_client._deliver_ops(ops, st, node)
    assert out.idempotent == 4 and out.a_repeat
    assert "già presenti" in out.summary()


def test_a_network_error_is_a_sentence_not_a_traceback(monkeypatch):
    import pytest as _pytest
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)

    def dead(method, url, payload, token):
        raise OSError("connection refused")

    with _pytest.raises(room_client.RoomRefusal) as err:
        room_client._deliver_ops([{"op": "add_node", "id": "n1"}], st, dead)
    assert "riprova" in str(err.value) or "raggiung" in str(err.value)


def test_rooms_door_prefers_the_caddy_path(monkeypatch):
    from modules.s3dgraphy.room import room_client

    def node(method, url, payload, token):
        return (200, {}) if url.endswith("/em/rooms/") else (404, {})

    assert room_client.rooms_door("http://x", http=node).endswith("/em/rooms/")

    def bare(method, url, payload, token):
        return (200, {}) if url.endswith("/rooms/") and "/em/" not in url \
            else (404, {})

    assert room_client.rooms_door("http://x", http=bare).endswith("/rooms/")
```

- [ ] **Step 2: Run — FAIL** (modulo mancante). Expected: 6 errori di import/attributo.

- [ ] **Step 3: Implementazione** — `room_client.py`:

```python
"""Portare le operazioni alla stanza. Niente altro.

Porting dichiarato di ``pyarchinit_mini/web_interface/room_client.py`` con le
sue quattro regole: (1) configurazione per ambiente, assente = spento; (2)
niente identità, niente consegna NÉ rete — qui l'identità la decide il
preflight ``/v1/health``: un nodo ``dev-no-auth`` non la chiede, uno con auth
vera esige ``STRATIGRAPH_TOKEN`` PRIMA di qualsiasi POST; (3) POST sincroni
senza coda né retry — una differenza dal mini, dichiarata: i NOSTRI siti
superano le 1000 op, quindi il lotto si spezza in pagine ≤1000 consegnate in
sequenza, fail-fast alla prima rete caduta, mai un retry; (4) ``author`` e
``ts`` li scrive il server.

E UN RIFIUTO DELLA STANZA NON È UN ERRORE: ``refused`` dentro un 200 è la
risposta normale alla seconda consegna (i nodi FONDONO, gli archi tornano
``idempotent`` — misurato sul nodo locale il 2026-10-07). Mai ``graph_id``
nel payload: una stanza, un grafo vivo.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

log = logging.getLogger(__name__)

SERVER_URL_VARIABLE = "STRATIGRAPH_SERVER_URL"
ROOM_ID_VARIABLE = "STRATIGRAPH_ROOM_ID"
TOKEN_VARIABLE = "STRATIGRAPH_TOKEN"          # SOLO env: un token non si salva
QSETTINGS_URL = "pyarchinit/stratigraph/server_url"
QSETTINGS_ROOM = "pyarchinit/stratigraph/room_id"
BATCH_MAX = 1000
TIMEOUT = 30.0

Http = Callable[[str, str, Optional[Dict[str, Any]], str],
                "tuple[int, Dict[str, Any]]"]


def _urllib_http(method, url, payload, token):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer %s" % token
    req = urllib.request.Request(url, data=body, method=method,
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as answer:
        return answer.status, json.loads(answer.read().decode("utf-8") or "{}")


def _qsetting(key):
    try:
        from qgis.PyQt.QtCore import QSettings
        return str(QSettings().value(key, "") or "").strip()
    except Exception:
        return ""


class NodeSettings:
    """Dove sta il nodo e quale stanza. Env prima, QSettings poi; il token
    SOLO da env (pattern modules/storage/credentials.py)."""

    def __init__(self):
        self.server_url = (os.environ.get(SERVER_URL_VARIABLE, "").strip()
                           or _qsetting(QSETTINGS_URL)).rstrip("/")
        self.room_id = (os.environ.get(ROOM_ID_VARIABLE, "").strip()
                        or _qsetting(QSETTINGS_ROOM))
        self.token = os.environ.get(TOKEN_VARIABLE, "").strip()

    @property
    def enforcing(self):
        return bool(self.server_url and self.room_id)

    @property
    def ops_endpoint(self):
        import urllib.parse
        return "%s/v1/rooms/%s/ops" % (
            self.server_url, urllib.parse.quote(self.room_id, safe=""))


class RoomRefusal(RuntimeError):
    """Qualcosa che questo modulo non fa, in una frase per una persona."""


@dataclass
class Outcome:
    sent: int = 0
    applied: int = 0
    refused: List[Dict[str, Any]] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    room_id: str = ""
    batches: int = 0

    @property
    def idempotent(self):
        return sum(1 for r in self.refused
                   if r.get("reason") == "idempotent")

    @property
    def other_refusals(self):
        return [r for r in self.refused if r.get("reason") != "idempotent"]

    @property
    def a_repeat(self):
        return (self.sent > 0 and self.idempotent > 0
                and self.idempotent + self.applied == self.sent
                and not self.other_refusals)

    def summary(self):
        parts = ["%d applicate su %d" % (self.applied, self.sent)]
        if self.idempotent:
            parts.append("%d già presenti" % self.idempotent)
        if self.other_refusals:
            parts.append("%d rifiutate" % len(self.other_refusals))
        if self.skipped:
            parts.append("%d righe non tradotte" % len(self.skipped))
        return ", ".join(parts)


def preflight(server_url, http: Http = _urllib_http):
    try:
        status, body = http("GET", server_url + "/v1/health", None, "")
    except Exception as exc:
        raise RoomRefusal(
            "Non ho potuto raggiungere il nodo (%s/v1/health): %s. "
            "Riprova quando il nodo risponde — niente coda."
            % (server_url, exc)) from exc
    if status != 200 or not body.get("ok"):
        raise RoomRefusal("Il nodo %s non sta bene (HTTP %d): consegna "
                          "rifiutata." % (server_url, status))
    return body


def _require_identity(settings, http: Http = _urllib_http):
    """Regola 2, adattata: l'identità la esige il NODO, non noi. Un nodo
    dev-no-auth non la chiede; uno vero la chiede PRIMA di ogni POST."""
    health = preflight(settings.server_url, http)
    if health.get("auth") != "dev-no-auth" and not settings.token:
        raise RoomRefusal(
            "Il nodo %s esige un'identità (%s) e %s non è impostata: "
            "senza un nome verificato non si scrive nel grafo di nessuno. "
            "Procurati un token dal nodo e mettilo in %s."
            % (settings.server_url, health.get("auth") or "auth",
               TOKEN_VARIABLE, TOKEN_VARIABLE))
    return health


def _deliver_ops(ops, settings, http: Http = _urllib_http):
    out = Outcome(sent=len(ops), room_id=settings.room_id)
    for start in range(0, len(ops), BATCH_MAX):
        page = ops[start:start + BATCH_MAX]
        try:
            status, answer = http("POST", settings.ops_endpoint,
                                  {"ops": page}, settings.token)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            try:
                detail = json.loads(detail).get("detail") or detail
            except Exception:
                pass
            raise RoomRefusal(
                "La stanza «%s» ha rifiutato la consegna (HTTP %d): %s"
                % (settings.room_id, exc.code, detail)) from exc
        except Exception as exc:
            raise RoomRefusal(
                "Non ho potuto raggiungere il nodo (%s): %s. Consegnate "
                "%d operazioni su %d; le operazioni sono idempotenti — "
                "riprova tutto quando il nodo risponde."
                % (settings.server_url, exc, start, len(ops))) from exc
        if status != 200:
            raise RoomRefusal(
                "La stanza «%s» ha risposto HTTP %d alla pagina %d."
                % (settings.room_id, status, out.batches + 1))
        out.batches += 1
        out.applied += int(answer.get("applied") or 0)
        out.refused.extend(answer.get("refused") or [])
    return out


def deliver_site(conn_str, sito, settings=None, http: Http = _urllib_http):
    """us_table → stanza, nell'ordine che conta: configurazione, identità,
    traduzione, e SOLO POI la rete delle ops."""
    from . import site_rows, us_ops

    settings = settings or NodeSettings()
    if not settings.enforcing:
        missing = [n for n, v in ((SERVER_URL_VARIABLE, settings.server_url),
                                  (ROOM_ID_VARIABLE, settings.room_id))
                   if not v]
        raise RoomRefusal(
            "Nessuna stanza configurata: manca %s. Imposta server e stanza "
            "(env o campo del dialogo) — senza entrambi una consegna "
            "andrebbe dove nessuno ha scelto." % " e ".join(missing))
    _require_identity(settings, http)

    units, relationships = site_rows.load(conn_str, sito)
    made = us_ops.deliver(units, relationships)
    if not made.ops:
        out = Outcome(room_id=settings.room_id)
        out.skipped = list(made.skipped)
        out.counts = dict(made.counts)
        return out
    out = _deliver_ops(made.ops, settings, http)
    out.skipped = list(made.skipped)
    out.counts = dict(made.counts)
    log.info("[room] %s → %s (sito=%r)", settings.room_id, out.summary(), sito)
    return out


def rooms_door(server_url, http: Http = _urllib_http):
    """La porta della UI delle stanze: /em/rooms/ dietro Caddy, /rooms/ sul
    nodo nudo. La prima che risponde 200."""
    for path in ("/em/rooms/", "/rooms/"):
        try:
            status, _body = http("GET", server_url.rstrip("/") + path,
                                 None, "")
        except Exception:
            continue
        if status == 200:
            return server_url.rstrip("/") + path
    return server_url.rstrip("/") + "/em/rooms/"
```

> Nota per l'esecutore: `_urllib_http` su GET verso la UI riceve HTML, non JSON — il `json.loads` fallirebbe. Correggere in implementazione: per i GET non-JSON catturare il `JSONDecodeError` e restituire `(status, {})`; il test `test_rooms_door_prefers_the_caddy_path` usa http finti e non lo vede, quindi aggiungere anche un collaudo nel Task 5 contro il nodo vero.

- [ ] **Step 4: Run — PASS** (`pytest tests/sync/test_room_client.py -q` → 6 passed).
- [ ] **Step 5: Commit** — `feat(room): client della stanza — preflight health, identità a carico del nodo, pagine ≤1000, refused-in-200`

### Task 4: menu «Consegna sito alla stanza…» + «Apri il nodo» (B2 minimo)

**Files:**
- Modify: `pyarchinitPlugin.py` (due azioni accanto a `actionEmExport`; rimozione in `unload()` — la lista del 5.13.29 va estesa con le due nuove)
- Test: `tests/sync/test_room_client.py` (guard di cablaggio)

**Interfaces:**
- Consumes: `room_client.deliver_site`, `room_client.rooms_door`, `room_client.NodeSettings`, `Connection().conn_str()`, `Pyarchinit_db_management.query_bool({}, 'SITE')` (stesso giro di `_run_em_export`).
- Produces: `self.actionRoomDelivery` («Extended Matrix → Consegna sito alla stanza…») → `_run_room_delivery`; `self.actionRoomOpen` («Extended Matrix → Apri il nodo (stanze)…») → `_open_rooms_door`.

- [ ] **Step 1: Guard rosso** (in coda a `tests/sync/test_room_client.py`):

```python
def test_the_menu_offers_delivery_and_the_node_door():
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    src = (root / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert "Consegna sito alla stanza" in src
    assert "deliver_site" in src and "rooms_door" in src
    unload = re.search(r"def unload\(self\):(.*?)\n    def ", src, re.S)
    assert unload and "actionRoomDelivery" in unload.group(1)
    assert "actionRoomOpen" in unload.group(1)
```

- [ ] **Step 2: Run — FAIL.** Expected: 1 FAILED.

- [ ] **Step 3: Cablaggio.** In `_init_migrations_menu`, subito dopo il blocco `actionEmExport`:

```python
            self.actionRoomDelivery = QAction(
                "Extended Matrix → Consegna sito alla stanza…",
                self.iface.mainWindow())
            self.actionRoomDelivery.triggered.connect(self._run_room_delivery)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionRoomDelivery)

            self.actionRoomOpen = QAction(
                "Extended Matrix → Apri il nodo (stanze)…",
                self.iface.mainWindow())
            self.actionRoomOpen.triggered.connect(self._open_rooms_door)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionRoomOpen)
```

In `unload()`, aggiungere `"actionRoomDelivery", "actionRoomOpen"` alla tupla delle voci rimosse. Poi gli handler, accanto a `_run_em_export`:

```python
    def _run_room_delivery(self):
        """C (spec 2026-10-07 §C + addendum): un sito → una stanza, REST."""
        from qgis.PyQt.QtCore import QSettings
        from qgis.PyQt.QtWidgets import (QDialog, QDialogButtonBox,
                                         QFormLayout, QInputDialog,
                                         QLineEdit, QMessageBox)
        from modules.db.pyarchinit_conn_strings import Connection
        from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
        from modules.s3dgraphy.room import room_client

        try:
            conn_str = Connection().conn_str()
            db = Pyarchinit_db_management(conn_str)
            db.connection()
            sites = sorted({str(r.sito) for r in db.query_bool({}, 'SITE')})
        except Exception as e:
            QMessageBox.warning(self.iface.mainWindow(), "Stanza",
                                "Connessione al database fallita:\n%s" % e)
            return
        if not sites:
            QMessageBox.information(self.iface.mainWindow(), "Stanza",
                                    "Nessun sito nel database.")
            return
        site, ok = QInputDialog.getItem(
            self.iface.mainWindow(), "Consegna alla stanza", "Sito:",
            sites, 0, False)
        if not ok:
            return

        settings = room_client.NodeSettings()
        dialog = QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("Stanza StratiGraph")
        form = QFormLayout(dialog)
        url_edit = QLineEdit(settings.server_url)
        url_edit.setPlaceholderText("http://127.0.0.1:8020")
        room_edit = QLineEdit(settings.room_id)
        room_edit.setPlaceholderText("scavo-2026")
        token_edit = QLineEdit(settings.token)
        token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        token_edit.setPlaceholderText(
            "solo se il nodo lo esige (meglio: env %s)"
            % room_client.TOKEN_VARIABLE)
        form.addRow("Nodo:", url_edit)
        form.addRow("Stanza:", room_edit)
        form.addRow("Token:", token_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        settings.server_url = url_edit.text().strip().rstrip("/")
        settings.room_id = room_edit.text().strip()
        settings.token = token_edit.text().strip()   # mai persistito
        qs = QSettings()
        qs.setValue(room_client.QSETTINGS_URL, settings.server_url)
        qs.setValue(room_client.QSETTINGS_ROOM, settings.room_id)

        try:
            outcome = room_client.deliver_site(conn_str, site,
                                               settings=settings)
        except room_client.RoomRefusal as e:
            QMessageBox.warning(self.iface.mainWindow(), "Stanza", str(e))
            return
        title = ("Sito già consegnato" if outcome.a_repeat
                 else "Consegna alla stanza")
        box = QMessageBox(self.iface.mainWindow())
        box.setWindowTitle(title)
        box.setText("«%s» → stanza «%s»\n%s"
                    % (site, outcome.room_id, outcome.summary()))
        details = []
        if outcome.other_refusals:
            details += ["RIFIUTATE:"] + [
                "  %s: %s" % (r.get("id", "?"), r.get("reason"))
                for r in outcome.other_refusals]
        if outcome.skipped:
            details += ["NON TRADOTTE:"] + [
                "  " + s for s in outcome.skipped]
        if details:
            box.setDetailedText("\n".join(details))
        box.exec()

    def _open_rooms_door(self):
        """B2 minimo: la UI delle stanze servita dal nodo, nel browser."""
        import webbrowser
        from qgis.PyQt.QtWidgets import QMessageBox
        from modules.s3dgraphy.room import room_client

        settings = room_client.NodeSettings()
        if not settings.server_url:
            QMessageBox.information(
                self.iface.mainWindow(), "Nodo StratiGraph",
                "Nessun nodo configurato: consegna prima un sito (la "
                "finestra chiede l'indirizzo) o imposta %s."
                % room_client.SERVER_URL_VARIABLE)
            return
        try:
            door = room_client.rooms_door(settings.server_url)
        except Exception:
            door = settings.server_url + "/em/rooms/"
        webbrowser.open(door)
```

> Decisione dichiarata (dal messaggio di Emanuel): B2 «ancora più semplice all'inizio» = la porta del nodo nel BROWSER. Il pannello QWebEngineView dentro pyArchInit resta il B2 pieno, pianificato a parte quando la stanza avrà contenuti da guardare in sola lettura (serve il ruolo viewer lato nodo).

- [ ] **Step 4: Run — PASS** (`pytest tests/sync/test_room_client.py -q` → 7 passed) e `python3 -m py_compile pyarchinitPlugin.py`.
- [ ] **Step 5: Commit** — `feat(room): menu «Consegna sito alla stanza…» + porta del nodo nel browser (B2 minimo)`

### Task 5: collaudo vivo sul nodo locale

**Files:**
- Create: `tests/sync/test_room_delivery_live.py` (si salta senza nodo)

**Interfaces:**
- Consumes: il nodo locale (`EM_SERVER_ALLOW_ANON=1 … uvicorn app.main:app --port 8020`), `room_client`, `site_rows`, fixture `tests/sync/fixtures/mini_volterra.sqlite`.

- [ ] **Step 1: Test vivo** (intero file):

```python
"""Collaudo contro il nodo locale VERO. Si salta se il nodo non risponde —
stesso patto dei test *_pg: l'ambiente è una precondizione, non un fallimento.

Avvio del nodo:
    cd ~/stratigraph-node/stratigraph-server && \
    EM_SERVER_ALLOW_ANON=1 ~/stratigraph-node/venv/bin/uvicorn \
        app.main:app --port 8020
"""
from __future__ import annotations

import json
import shutil
import sys
import urllib.request
import uuid
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

NODE = "http://127.0.0.1:8020"


def _node_answers():
    try:
        with urllib.request.urlopen(NODE + "/v1/health", timeout=3) as r:
            return json.loads(r.read().decode()).get("ok") is True
    except Exception:
        return False


if not _node_answers():
    pytest.skip("nessun nodo StratiGraph su %s" % NODE,
                allow_module_level=True)


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(PLUGIN_ROOT / "tests" / "sync" / "fixtures"
                 / "mini_volterra.sqlite", dst)
    return "sqlite:///%s" % dst


@pytest.fixture
def room(monkeypatch):
    room_id = "collaudo-%s" % uuid.uuid4().hex[:8]
    body = json.dumps({"room_id": room_id,
                       "title": "Collaudo pyArchInit"}).encode()
    req = urllib.request.Request(
        NODE + "/v1/rooms", data=body, method="POST",
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 201
    monkeypatch.setenv("STRATIGRAPH_SERVER_URL", NODE)
    monkeypatch.setenv("STRATIGRAPH_ROOM_ID", room_id)
    monkeypatch.delenv("STRATIGRAPH_TOKEN", raising=False)
    return room_id


def test_a_site_lands_and_a_repeat_is_a_merge(mini_volterra, room):
    import sqlite3
    from modules.s3dgraphy.room import room_client
    sito = sqlite3.connect(mini_volterra.replace("sqlite:///", "")).execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]

    first = room_client.deliver_site(mini_volterra, sito)
    assert first.sent > 0 and first.applied > 0
    assert not first.other_refusals, first.other_refusals

    again = room_client.deliver_site(mini_volterra, sito)
    assert again.a_repeat, again.summary()


def test_the_rooms_door_answers(room):
    from modules.s3dgraphy.room import room_client
    door = room_client.rooms_door(NODE)
    assert door.endswith("/rooms/")
    with urllib.request.urlopen(door, timeout=5) as r:
        assert r.status == 200
```

- [ ] **Step 2: Run col nodo acceso** — avviare il nodo (comando nel docstring), poi `pytest tests/sync/test_room_delivery_live.py -q`. Expected: `2 passed`. Spegnere il nodo e rilanciare: Expected `2 skipped` (il patto).
- [ ] **Step 3: Collaudo a mano, misurato** — consegnare «Scavo archeologico» (DB campione, con node_uuid backfillato in copia tmp) a una stanza nuova del nodo locale via `deliver_site`; annotare nel changelog: inviate/applicate/già-presenti/non-tradotte della 1ª e della 2ª consegna.
- [ ] **Step 4: Suite canonica + sweep → ≤ baseline del Task 0.**
- [ ] **Step 5: Commit** — `test(room): collaudo vivo sul nodo locale (consegna, riconsegna=merge, porta della UI)`

### Task 6: release + satelliti

**Files:**
- Modify: `metadata.txt` (→ `5.13.30-alpha`), `dev_logs/CHANGELOG.md`, `docs/tutorials/{it,en,pt,ro,el}/01_configurazione.md`

- [ ] **Step 1: Tutorial** — nelle 5 lingue che hanno il tutorial 01, sotto la sezione em.json, una sezione breve «Consegnare un sito a una stanza StratiGraph» nello stesso stile (menu, i 3 campi del dialogo, il significato di «già presenti», il token solo se il nodo lo esige, la voce «Apri il nodo»).
- [ ] **Step 2: Changelog IT+EN** — con le misure del collaudo (Task 5 Step 3) e le decisioni: ORIGIN `"pyarchinit"` (≠ mini: stessa unità consegnata dai due strumenti = due nodi — da chiedere a Emanuel se serve un'identità cross-strumento), pagine ≤1000, mai `graph_id`.
- [ ] **Step 3: Merge ff su `Stratigraph_00001`; tag `room-delivery-5.13.30-alpha`; push; GitHub pre-release; api-docs RTD; rimozione worktree.**
- [ ] **Step 4: Memoria** — aggiornare `project_stratigraph_node_local.md` (C spedito, tag, cosa resta: B2 pieno in QWebEngineView; la domanda ORIGIN per Emanuel) e la riga indice in `MEMORY.md`.
- [ ] **Step 5: Commento su s3Dgraphy#25** — C collaudato contro il nodo locale (numeri), porting dichiarato del client mini, la domanda sull'identità cross-strumento (ORIGIN), e che B2 pieno aspetta una stanza con ruolo viewer da guardare.
