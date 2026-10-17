"""I paradati sotto la loro unità, come EMStudio (Enzo, 17 ottobre 2026:
«quello che non mi trovo è come è gestito questo ammasso … non è come l'ho
visto nel matrix di EMStudio»). TempluMare dava 853 «unità» di cui 739
paradati (360 proprietà, 301 estrattori, 55 documenti, 23 combinatori),
tutti nel calcolo dei livelli. Scelta di Enzo: ogni unità porta il suo
gruppo di paradati compatto sotto di sé, fuori dal calcolo dei livelli; un
documento usato da più unità compare in ogni gruppo («One master per
document, re-instanced in every paradata group that uses it», EMStudio)."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.em_matrix_layout import LayoutConfig, layout  # noqa: E402
from modules.utility.em_matrix_model import Epoch, MatrixModel, Relation, Unit  # noqa: E402


def _u(nid, tipo="US", epoca="e"):
    return Unit(node_id=nid, label=nid, node_type=tipo, epoch_id=epoca)


def _modello(con_paradati=True, condiviso=True):
    unita = [_u("US1"), _u("US2"), _u("US3")]
    rapporti = [Relation("US1", "US2", "overlies"), Relation("US2", "US3", "overlies")]
    if con_paradati:
        unita += [_u("p1", "property", None), _u("p2", "property", None),
                  _u("e1", "extractor", None), _u("e2", "extractor", None),
                  _u("c1", "combiner", None), _u("D.05", "document", None)]
        rapporti += [
            Relation("US1", "p1", "has_property"), Relation("p1", "c1", "has_data_provenance"),
            Relation("c1", "e1", "combines"), Relation("e1", "D.05", "extracted_from"),
            Relation("US3", "p2", "has_property"), Relation("p2", "e2", "has_data_provenance"),
        ]
        if condiviso:
            rapporti.append(Relation("e2", "D.05", "extracted_from"))
    return MatrixModel(units=unita, epochs=[Epoch("e", "Epoca", 100, 200)], relations=rapporti)


def _caselle(lay, nid):
    return [b for b in lay.boxes if b.unit.node_id == nid]


def test_i_paradati_stanno_sotto_la_loro_unita():
    lay = layout(_modello())
    us1 = _caselle(lay, "US1")[0]
    passo = LayoutConfig().box_w + LayoutConfig().h_gap
    for nid in ("p1", "c1", "e1"):
        (b,) = _caselle(lay, nid)
        assert b.y >= us1.y + us1.h, nid                         # sotto
        assert us1.x - 1 <= b.x and b.x + b.w <= us1.x + passo, nid   # nella sua colonna


def test_i_paradati_non_cambiano_i_livelli_delle_unita():
    con = layout(_modello())
    senza = layout(_modello(con_paradati=False))
    righe = lambda lay: sorted({b.y for b in lay.boxes if b.unit.node_type == "US"})
    assert len(righe(con)) == len(righe(senza)) == 3
    colonne = lambda lay: {b.unit.node_id: b.x for b in lay.boxes if b.unit.node_type == "US"}
    assert colonne(con) == colonne(senza)


def test_un_documento_condiviso_sta_in_ogni_gruppo():
    lay = layout(_modello())
    istanze = _caselle(lay, "D.05")
    assert len(istanze) == 2

    def gruppo_di(b):
        return [g.owner for g in lay.groups
                if g.x <= b.x and b.x + b.w <= g.x + g.w and g.y <= b.y and b.y + b.h <= g.y + g.h]

    assert sorted(o for b in istanze for o in gruppo_di(b)) == ["US1", "US3"]


def test_si_disegnano_solo_i_legami_dentro_il_gruppo():
    lay = layout(_modello())
    gruppi = {g.owner: g for g in lay.groups}
    assert set(gruppi) == {"US1", "US3"}
    for e in lay.edges:
        if not e.paradata:
            continue
        xs = [p[0] for p in e.points]
        ys = [p[1] for p in e.points]
        dentro = [g for g in gruppi.values()
                  if g.x - 1 <= min(xs) and max(xs) <= g.x + g.w + 1 and max(ys) <= g.y + g.h + 1]
        assert dentro, (e.source, e.target)                      # nessuna linea fra due gruppi
    tipi = {(e.source, e.target) for e in lay.edges}
    assert ("US1", "p1") in tipi and ("e1", "D.05") in tipi and ("e2", "D.05") in tipi


def test_niente_si_sovrappone_e_la_fascia_li_contiene():
    lay = layout(_modello())
    rett = [(b.x, b.y, b.w, b.h) for b in lay.boxes]
    for i, (x1, y1, w1, h1) in enumerate(rett):
        for x2, y2, w2, h2 in rett[i + 1:]:
            assert (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1), \
                ((x1, y1, w1, h1), (x2, y2, w2, h2))
    (banda,) = lay.bands
    for b in lay.boxes:
        assert banda.y <= b.y and b.y + b.h <= banda.y + banda.h
    for g in lay.groups:
        assert banda.y <= g.y and g.y + g.h <= banda.y + banda.h
    assert lay.height >= banda.y + banda.h


def test_i_paradati_senza_unita_hanno_una_fascia_loro():
    modello = _modello()
    modello.units.append(_u("D.99", "document", None))
    lay = layout(modello)
    (orfano,) = _caselle(lay, "D.99")
    fascia = [b for b in lay.bands if b.y <= orfano.y < b.y + b.h]
    assert fascia and fascia[0].epoch is None and "paradati" in fascia[0].label.lower()


def test_senza_paradati_il_disegno_non_cambia():
    lay = layout(_modello(con_paradati=False))
    assert lay.groups == []
    assert all(not e.paradata for e in lay.edges)


def test_la_cornice_del_gruppo_si_disegna_nell_svg():
    from modules.utility.em_matrix_svg import to_svg
    import re
    lay = layout(_modello())
    svg = to_svg(lay)
    cornici = re.findall(r'<rect class="paradata-group"[^>]*>', svg)
    assert len(cornici) == len(lay.groups) == 2
    assert all("stroke-dasharray" in c and 'fill="none"' in c for c in cornici)


def test_la_vista_disegna_le_cornici_tratteggiate():
    src = (_ROOT / "modules" / "utility" / "em_matrix_view.py").read_text(encoding="utf-8")
    assert "for gruppo in lay.groups" in src
    corpo = src[src.index("for gruppo in lay.groups"):][:900]
    assert "DashLine" in corpo or "setDashPattern" in corpo


def test_il_titolo_conta_unita_e_paradati_a_parte():
    from modules.utility.em_matrix_model import summary_text
    assert summary_text(_modello()) == "3 unità · 6 paradati · 1 epoche · 2 rapporti"
    assert summary_text(_modello(con_paradati=False)) == "3 unità · 1 epoche · 2 rapporti"
    src = (_ROOT / "modules" / "s3dgraphy" / "em_matrix_panel.py").read_text(encoding="utf-8")
    assert src.count("summary_text(") >= 2          # la barra e l'intestazione
