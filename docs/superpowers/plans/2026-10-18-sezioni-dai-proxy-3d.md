# Sezioni lungo linee dai proxy 3D — piano di lavoro

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** un comando di menu che taglia i proxy 3D delle unità di un sito lungo le linee di `pyarchinit_sezioni` e scrive le sezioni nel layer dei disegni verticali, con documenti «Sezione» collegati a poligoni, schede e linee.

**Architecture:** `em_drawings.section_geometry` (taglio puro: segmenti d'intersezione, poligonazione, parità per i buchi, ritaglio al tratto). `sync/em_sections.py` legge linee, em.json ricordato e proxy (cartella o media del DB), calcola, impagina a sinistra e scrive con `write_drawings` limitato ai nomi delle sezioni. `em_sections_dialog.py` e `pyarchinitPlugin._run_em_sections` sono l'interfaccia. Il primo pezzo smette di cancellare il `3D-SEZ-…`.

**Tech Stack:** Python di QGIS 3.42, numpy, `qgis.core` (QgsGeometry.polygonize, QgsCoordinateTransform), SQLAlchemy, SpatiaLite / PostGIS, s3dgraphy dev57.

**Spec:** `docs/superpowers/specs/2026-10-18-sezioni-dai-proxy-3d-design.md`

## Global Constraints

- Plugin da 5.13.134-alpha a **5.13.135-alpha**; ramo `Stratigraph_00001`.
- Nomi: `3D-SEZ-<id_sezione>` (ripulito come `_safe`); senza `id_sezione`, `3D-SEZ-G<gid>`; i nomi doppi prendono `-<gid>`. Tipo dal thesaurus 9.1 `SEZ` (lingua del plugin, poi IT, poi «Sezione»).
- Disegnatore «pyArchInit 3D». Il comando sostituisce solo le sezioni che calcola; il reimport del primo pezzo sostituisce solo `3D-PLA` e `3D-PRO-…`.
- Le sezioni vanno a sinistra di `u = 0`, separate da `GAP = 10 m`.
- Niente dipendenze nuove; niente attribuzioni AI nei commit; prima del commit si cercano segreti.
- **PYT** = `.superpowers/sdd/2026-10-18-sezioni-dai-proxy-3d/pyt` (pytest col Python di QGIS, dalla radice). La suite intera è quella del primo pezzo. Base: 2511 passati.

## Review Focus

1. **Linea tracciata al contrario** (da est a ovest): ci si aspetta lo stesso profilo, specchiato, con A sempre a sinistra. Test in Task 1: `test_a_sinistra_c_e_sempre_a`.
2. **Il layer delle sezioni in un sistema diverso da quello dell'em.json** (3004 contro 31700): ci si aspetta che le linee si convertano e che il taglio cada nello stesso posto. Test in Task 3: `test_le_linee_in_un_altro_sistema_si_convertono`.
3. **La linea ha già un suo documento** (`tipo_doc` e `nome_doc` pieni): non va toccata, e il riepilogo lo dice. Test in Task 3: `test_la_linea_con_un_altro_documento_non_si_tocca`.
4. **Reimport con piante e prospetti dopo le sezioni**: le sezioni restano, comprese le loro coppie nella scheda. Test in Task 2: `test_il_reimport_non_tocca_le_sezioni`.
5. **Sito senza em.json ricordato o senza linee**: ci si aspetta un messaggio chiaro, senza errori. Test in Task 3: `test_senza_em_json_o_senza_linee_si_dice`.

---

### Task 1: il taglio (`em_drawings.section_geometry`)

**Files:** Modify `modules/s3dgraphy/em_drawings.py` (in coda; `_DERIVED` con `SEZ`) · Test `tests/utility/test_em_drawings_sezioni.py`

**Produces:** `section_geometry(tri_map, a, b) -> Optional[QgsGeometry]`; `section_line_geometry(tri_map, points) -> Optional[QgsGeometry]`; `line_length(points) -> float`; `is_derived_name` riconosce `3D-SEZ-…`.

- [ ] **Step 1: test che falliscono**

```python
# tests/utility/test_em_drawings_sezioni.py
"""Il taglio dei proxy lungo una linea di sezione (spec 2026-10-18 sezioni, S2)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.s3dgraphy import em_drawings as drw  # noqa: E402


def _cubo(x0, y0, z0, dx, dy, dz):
    v = np.array([(x0 + i * dx, y0 + j * dy, z0 + k * dz)
                  for i in (0, 1) for j in (0, 1) for k in (0, 1)], dtype=float)
    f = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
         (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return v[np.array(f)]


SCATOLA = _cubo(0.0, 0.0, 10.0, 4.0, 2.0, 3.0)


def test_una_scatola_tagliata_a_meta():
    g = drw.section_geometry(SCATOLA, (-1.0, 1.0), (5.0, 1.0))
    bb = g.boundingBox()
    assert g.area() == pytest.approx(12.0, abs=1e-6)
    assert (bb.xMinimum(), bb.xMaximum()) == pytest.approx((1.0, 5.0))
    assert (bb.yMinimum(), bb.yMaximum()) == pytest.approx((10.0, 13.0))


def test_il_taglio_si_ferma_al_tratto():
    g = drw.section_geometry(SCATOLA, (-1.0, 1.0), (2.0, 1.0))
    assert g.area() == pytest.approx(6.0, abs=1e-6)


def test_una_linea_spezzata_continua():
    punti = [(-1.0, 1.0), (2.0, 1.0), (2.0, 5.0)]
    g = drw.section_line_geometry(SCATOLA, punti)
    assert drw.line_length(punti) == pytest.approx(7.0)
    assert g.area() == pytest.approx(6.0 + 3.0, abs=1e-6)
    assert g.boundingBox().xMaximum() == pytest.approx(4.0)        # 3 del primo tratto + 1 del secondo


def test_a_sinistra_c_e_sempre_a():
    avanti = drw.section_geometry(SCATOLA, (-1.0, 1.0), (7.0, 1.0)).boundingBox()
    indietro = drw.section_geometry(SCATOLA, (7.0, 1.0), (-1.0, 1.0)).boundingBox()
    assert (avanti.xMinimum(), avanti.xMaximum()) == pytest.approx((1.0, 5.0))
    assert (indietro.xMinimum(), indietro.xMaximum()) == pytest.approx((3.0, 7.0))


def test_un_modello_aperto_o_lontano_non_da_profilo():
    piano = np.array([[[0, 0, 0], [0, 4, 0], [0, 4, 3]], [[0, 0, 0], [0, 4, 3], [0, 0, 3]]], dtype=float)
    assert drw.section_geometry(piano, (-2.0, 2.0), (2.0, 2.0)) is None
    assert drw.section_geometry(SCATOLA, (-1.0, 50.0), (5.0, 50.0)) is None


def test_un_vertice_sul_piano_non_rompe_il_taglio():
    g = drw.section_geometry(SCATOLA, (-1.0, 0.0), (5.0, 2.0))         # passa per gli spigoli
    assert g is None or g.isGeosValid()


def test_le_sezioni_sono_nomi_ricavati():
    assert drw.is_derived_name("3D-SEZ-1") and drw.is_derived_name("3D-SEZ-G12")
    assert not drw.is_derived_name("3D-SEZIONE")
```

- [ ] **Step 2:** `PYT tests/utility/test_em_drawings_sezioni.py` → FAIL (`AttributeError: … 'section_geometry'`).

- [ ] **Step 3: il codice**

In `em_drawings.py` cambiare `_DERIVED = re.compile(r"^3D-(PLA|PRO-.+)$")` in `_DERIVED = re.compile(r"^3D-(PLA|PRO-.+|SEZ-.+)$")`, e in coda:

```python
# ------------------------------------------------------------------ le sezioni

def _section_segments(tri_map: np.ndarray, a, b):
    """I segmenti dove i triangoli attraversano il piano verticale per a→b, in
    coordinate del disegno (u lungo il tratto da a, v quota); e la lunghezza."""
    t = np.asarray(tri_map, dtype=np.float64)
    ax, ay = float(a[0]), float(a[1])
    lung = math.hypot(float(b[0]) - ax, float(b[1]) - ay)
    if lung <= 1e-9 or not t.size:
        return np.zeros((0, 2, 2)), lung
    rx, ry = (float(b[0]) - ax) / lung, (float(b[1]) - ay) / lung
    dx, dy = -ry, rx
    s = (t[..., 0] - ax) * dx + (t[..., 1] - ay) * dy
    s = np.where(np.abs(s) < 1e-9, 1e-9, s)            # un vertice sul piano conta da una parte
    sopra = s > 0
    attraversa = sopra.any(axis=1) & (~sopra).any(axis=1)
    t, s, sopra = t[attraversa], s[attraversa], sopra[attraversa]
    if not len(t):
        return np.zeros((0, 2, 2)), lung
    seg = np.zeros((len(t), 2, 3))
    quanti = np.zeros(len(t), dtype=int)
    for i, j in ((0, 1), (1, 2), (2, 0)):
        taglia = sopra[:, i] != sopra[:, j]
        f = s[:, i] / (s[:, i] - s[:, j])
        punto = t[:, i] + (t[:, j] - t[:, i]) * f[:, None]
        k = np.nonzero(taglia)[0]
        seg[k, quanti[k]] = punto[k]
        quanti[k] += 1
    u = (seg[..., 0] - ax) * rx + (seg[..., 1] - ay) * ry
    return np.stack([u, seg[..., 2]], axis=-1), lung


def section_geometry(tri_map: np.ndarray, a, b):
    """Il profilo tagliato dal piano verticale del tratto a→b, fra u = 0 e
    u = |ab|: MultiPolygon o None. Le facce sono riempite pari/dispari, così il
    buco di un anello non si riempie."""
    from qgis.core import QgsGeometry, QgsRectangle
    seg, lung = _section_segments(tri_map, a, b)
    if not len(seg):
        return None
    seg = seg[np.hypot(seg[:, 1, 0] - seg[:, 0, 0], seg[:, 1, 1] - seg[:, 0, 1]) > 1e-9]
    if not len(seg):
        return None
    wkt = "MULTILINESTRING(" + ",".join(
        "(%r %r,%r %r)" % (x0, y0, x1, y1) for (x0, y0), (x1, y1) in seg.tolist()) + ")"
    facce = _polygons(QgsGeometry.polygonize([QgsGeometry.unaryUnion([QgsGeometry.fromWkt(wkt)])]))
    if not facce:
        return None
    esterni = [QgsGeometry.fromPolygonXY([f.asPolygon()[0]]) for f in facce]
    piene = [f for i, f in enumerate(facce)
             if sum(1 for j, e in enumerate(esterni) if j != i and e.contains(f.pointOnSurface())) % 2 == 0]
    if not piene:
        return None
    vmin, vmax = float(seg[..., 1].min()) - 1.0, float(seg[..., 1].max()) + 1.0
    tratto = QgsGeometry.fromRect(QgsRectangle(0.0, vmin, lung, vmax))
    return _clean(QgsGeometry.collectGeometry(piene).intersection(tratto))


def line_length(points) -> float:
    return float(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])))


def section_line_geometry(tri_map: np.ndarray, points):
    """Il profilo lungo una linea spezzata: ogni tratto si taglia da sé, e u
    continua da un tratto all'altro."""
    from qgis.core import QgsGeometry
    parti, u0 = [], 0.0
    for a, b in zip(points, points[1:]):
        lung = math.hypot(b[0] - a[0], b[1] - a[1])
        if lung <= 1e-9:
            continue
        g = section_geometry(tri_map, a, b)
        if g is not None:
            parti.append(translated(g, u0))
        u0 += lung
    if not parti:
        return None
    return _clean(QgsGeometry.unaryUnion(parti))
```

- [ ] **Step 4:** `PYT tests/utility/test_em_drawings_sezioni.py tests/utility/test_em_drawings.py` → PASS.
- [ ] **Step 5:** commit «feat(3d): il taglio dei proxy lungo una linea di sezione — segmenti, poligonazione pari/dispari, ritaglio al tratto, linee spezzate».

---

### Task 2: il primo pezzo lascia stare le sezioni; `write_drawings` limitato ai nomi

**Files:** Modify `modules/s3dgraphy/sync/em_drawings_import.py` · Test `tests/sync/test_em_drawings_import.py` (in coda)

**Produces:** `write_drawings(…, scope: Optional[Set[str]] = None)` (None = `3D-PLA` e `3D-PRO-…`; un insieme = solo quei nomi, sia per i poligoni sia per i documenti); `doc_type(db, sigla, ripiego, lingua=None) -> str`.

- [ ] **Step 1: test che fallisce**

```python
def test_il_reimport_non_tocca_le_sezioni(progetto):
    _scrivi(progetto)
    con = sqlite3.connect(progetto["db"])
    con.enable_load_extension(True)
    for nome in _SPATIALITE:
        try:
            con.load_extension(nome)
            break
        except sqlite3.Error:
            continue
    con.execute("INSERT INTO pyunitastratigrafiche_usm (gid, scavo_s, area_s, us_s, unita_tipo_s, disegnatore, "
                "tipo_doc, nome_doc, the_geom) VALUES (900, ?, '1', '001', 'US', 'pyArchInit 3D', 'Sezione', "
                "'3D-SEZ-1', CastToMultiPolygon(GeomFromText('POLYGON((-20 0,-18 0,-18 2,-20 0))', 31700)))", (SITO,))
    con.execute("INSERT INTO documentazione_table (id_documentazione, sito, nome_doc, tipo_documentazione, "
                "disegnatore) VALUES (900, ?, '3D-SEZ-1', 'Sezione', 'pyArchInit 3D')", (SITO,))
    con.commit()
    con.close()
    _scrivi(progetto)
    assert _righe(progetto, "SELECT count(*) FROM pyunitastratigrafiche_usm WHERE nome_doc = '3D-SEZ-1'")[0][0] == 1
    assert _righe(progetto, "SELECT count(*) FROM documentazione_table WHERE nome_doc = '3D-SEZ-1'")[0][0] == 1
    doc = _righe(progetto, "SELECT documentazione FROM us_table WHERE sito = ? AND us = '001'", SITO)[0][0]
    assert "['Sezione', '3D-SEZ-1']" in doc
```

- [ ] **Step 2:** `PYT tests/sync/test_em_drawings_import.py -k sezioni` → FAIL (la riga `3D-SEZ-1` cancellata).

- [ ] **Step 3: il codice**
  - `write_drawings(…, rilievi=None, scope=None)`. La cancellazione dei poligoni:
    ```python
            if scope is None:
                filtro, parametri = "(nome_doc = :pla OR nome_doc LIKE :pro)", {"pla": drw.PLAN_NAME, "pro": "3D-PRO-%"}
            else:
                nomi = sorted(scope)
                filtro = "nome_doc IN (%s)" % ", ".join(":n%d" % i for i in range(len(nomi))) if nomi else "1 = 0"
                parametri = {"n%d" % i: n for i, n in enumerate(nomi)}
    ```
    e `DELETE FROM <layer> WHERE scavo_s = :s AND disegnatore = :d AND <filtro>`.
  - La pulizia dei documenti considera solo i nomi nello stesso ambito: `scope is None` → `nome == PLAN_NAME or nome.startswith("3D-PRO-")`; altrimenti `nome in scope`.
  - `doc_type(db, sigla, ripiego, lingua=None)` come `doc_types`, per una sigla sola; `doc_types` la usa.

- [ ] **Step 4:** `PYT tests/sync/test_em_drawings_import.py tests/sync/test_em_drawings_import_pg.py` → PASS.
- [ ] **Step 5:** commit «fix(3d): il reimport con piante e prospetti sostituisce solo 3D-PLA e 3D-PRO-…; write_drawings limitato ai nomi».

---

### Task 3: `sync/em_sections.py` — linee, unità, calcolo, scrittura

**Files:** Create `modules/s3dgraphy/sync/em_sections.py` · Test `tests/sync/test_em_sections.py`, `tests/sync/test_em_sections_pg.py`

**Produces:** `SectionLine(gid, id_sezione, descr, area, points, tipo_doc, nome_doc)` con `.length`, `.segments`; `SectionsError(Exception)`; `section_lines(db, sito) -> Tuple[List[SectionLine], Optional[int]]`; `section_names(lines) -> Dict[int, str]`; `load_graph(db, sito)`; `section_units(graph, db, sito, *, search_dirs=(), resize_base="") -> List[DrawingUnit]`; `SectionsResult` con `.summary()`; `run_sections(db, sito, *, gids, shift_z=None, search_dirs=(), resize_base="", lang=None, progress=None) -> SectionsResult`.

Il codice e i test seguono il disegno della spec (S2–S6):
- le linee si leggono con `AsText`/`ST_AsText` e `QgsGeometry.fromWkt(...).asPolyline()` (la prima parte di una multilinea);
- le unità vengono da `plan_units(graph, "", search_dirs=…)`, e per quelle senza file da `em_project.media_index`/`media_file_for` (con l'URL del motore, password compresa, solo in memoria);
- le linee si convertono nell'EPSG dell'em.json con `QgsCoordinateTransform` se il layer ha un altro sistema metrico o geografico; se non ne ha (−1 o 0) si usano così e il risultato ha una nota;
- le mesh si piazzano come in `compute_drawings`;
- il profilo di ogni unità per linea viene da `section_line_geometry`;
- le sezioni si impaginano a sinistra del disegno ricavato più a sinistra che resta (`MbrMinX`/`ST_XMin` sui `3D-%` del sito che non sono nell'ambito);
- si scrive con `write_drawings(…, scope=<nomi calcolati>)` e una `CrsDecision("ok", usm_srid=…)`;
- poi le linee senza documento prendono `tipo_doc`/`nome_doc`.

`SectionsError` è il messaggio per:
- un sito senza em.json ricordato;
- un em.json non georeferenziato;
- nessuna linea scelta;
- un layer USM non metrico.

Test con la fixture del primo pezzo, dopo `em_sources.remember_source`, con una linea scritta in `pyarchinit_sezioni` sopra SU001:
- poligoni, documento «Sezione», coppia della scheda e linea collegata;
- la seconda volta sostituisce;
- impaginazione a sinistra di 0;
- una linea con un altro documento resta com'era e il riepilogo lo dice;
- le linee in 3004 si convertono e il taglio cade nello stesso posto (stessa larghezza del profilo);
- senza em.json, o senza linee, `SectionsError` con un messaggio chiaro.

Su PG, in uno schema temporaneo come nel primo pezzo, con `pyarchinit_sezioni` e la memoria dell'em.json: si scrive e si richiama.

---

### Task 4: finestra, menu, verifica, documentazione e versione

**Files:**
- Create `modules/s3dgraphy/em_sections_dialog.py`.
- Modify `pyarchinitPlugin.py`: `actionEmSections` «Extended Matrix → Sezioni dai modelli 3D…» dopo `actionEmProject`, nell'elenco dello scarico, e `_run_em_sections`.
- Tutorial 36 §5.0.3, in dieci lingue.
- `dev_logs/CHANGELOG.md`, `metadata.txt` 5.13.135-alpha.
- Test `tests/sync/test_em_sections_dialog.py`.

La finestra `SectionsDialog(lines, units, georef, shift_z, names)` ha:
- la posizione;
- lo spostamento Z con le quote;
- la tabella delle linee, cioè casella, Sezione, Descrizione, Area, Tratti, Lunghezza in metri;
- il numero di unità con un modello.

`.chosen() -> (gids, shift_z)`. Il menu sceglie il sito come `_run_em_project`. Poi legge grafo, linee e unità; se manca qualcosa dice cosa; apre la finestra; calcola con la barra e mostra il riepilogo.

Test: la finestra si costruisce e restituisce la scelta; il menu ha la voce, la toglie allo scarico e chiama `run_sections` (controllo sul sorgente, come `test_em_import_dialog_wiring`).

Verifica su TempluMare: sulla copia del Task 9 del primo pezzo, una linea attraverso la cella, da ovest a est, con `run_sections`, e l'immagine della sezione resa con OGR. Poi la suite intera.

## Dopo i task

Revisione finale con un revisore nuovo, giro di correzioni, suite, e rilascio: tag `sezioni-3d-5.13.135-alpha`, push, pre-release, api-docs.
