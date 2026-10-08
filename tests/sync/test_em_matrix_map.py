"""Lo zoom dalla matrice alla geometria (2026-10-08).

Il modulo che parla con QGIS si prova con layer finti: niente progetto,
niente QgsApplication. Quello che decide quale layer vince sta in
``em_matrix_links`` e si prova là; qui si prova il meccanismo — la
selezione, l'inquadratura, le frasi che tornano all'utente.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

MAP = _ROOT / "modules" / "utility" / "em_matrix_map.py"


def _unit(**dati):
    from modules.utility.em_matrix_model import Unit
    return Unit(node_id="n1", label=dati.pop("label", "1.US1"),
                node_type="US", epoch_id=None, data=dati)


def _crs():
    from qgis.core import QgsCoordinateReferenceSystem
    return QgsCoordinateReferenceSystem()           # non valida: niente riproiezione


class _Campo:
    def __init__(self, nome):
        self._nome = nome

    def name(self):
        return self._nome


class _Riquadro:
    def __init__(self, x1, y1, x2, y2):
        self._v = (x1, y1, x2, y2)

    def xMinimum(self):
        return self._v[0]

    def yMinimum(self):
        return self._v[1]

    def xMaximum(self):
        return self._v[2]

    def yMaximum(self):
        return self._v[3]


class _Geometria:
    def __init__(self, riquadro):
        self._r = riquadro

    def isEmpty(self):
        return self._r is None

    def isNull(self):
        return self._r is None

    def boundingBox(self):
        return self._r


class _Feature:
    def __init__(self, fid, riquadro):
        self._id = fid
        self._g = _Geometria(riquadro)

    def id(self):
        return self._id

    def geometry(self):
        return self._g

    def hasGeometry(self):
        return self._g._r is not None


class _Layer:
    def __init__(self, nome, campi, feature=()):
        self._nome = nome
        self._campi = [_Campo(c) for c in campi]
        self._feature = list(feature)
        self.selezionate = None

    def name(self):
        return self._nome

    def fields(self):
        return self._campi

    def crs(self):
        return _crs()

    def getFeatures(self, request=None):
        return iter(self._feature)

    def selectByIds(self, ids):
        self.selezionate = list(ids)


class _Impostazioni:
    def destinationCrs(self):
        return _crs()


class _Canvas:
    def __init__(self):
        self.inquadratura = None
        self.aggiornato = 0

    def mapSettings(self):
        return _Impostazioni()

    def setExtent(self, rettangolo):
        self.inquadratura = (rettangolo.xMinimum(), rettangolo.yMinimum(),
                             rettangolo.xMaximum(), rettangolo.yMaximum())

    def refresh(self):
        self.aggiornato += 1


class _Iface:
    def __init__(self):
        self._canvas = _Canvas()

    def mapCanvas(self):
        return self._canvas


def _us():
    return _unit(sito="Scavo", area="1", us="1", unita_tipo="US")


# ------------------------------------------------------------- il meccanismo

def test_the_geometry_is_selected_and_the_canvas_framed_around_it():
    from modules.utility.em_matrix_map import zoom_to_unit

    layer = _Layer("US view", ("sito", "area", "us"),
                   [_Feature(3, _Riquadro(0, 0, 10, 10))])
    iface = _Iface()
    fatto, messaggio = zoom_to_unit(iface, _us(), layers=[layer], margin=0.2)
    assert fatto, messaggio
    assert layer.selezionate == [3]
    assert iface.mapCanvas().inquadratura == (-2, -2, 12, 12)
    assert iface.mapCanvas().aggiornato == 1
    assert "US view" in messaggio


def test_two_pieces_of_the_same_unit_are_framed_together():
    """Una US può essere disegnata in più pezzi: si inquadrano tutti."""
    from modules.utility.em_matrix_map import zoom_to_unit

    layer = _Layer("US view", ("sito", "area", "us"),
                   [_Feature(1, _Riquadro(0, 0, 10, 10)),
                    _Feature(2, _Riquadro(20, 0, 30, 10))])
    iface = _Iface()
    fatto, _ = zoom_to_unit(iface, _us(), layers=[layer], margin=0.0)
    assert fatto
    assert layer.selezionate == [1, 2]
    assert iface.mapCanvas().inquadratura == (0, 0, 30, 10)


def test_a_unit_whose_plan_was_never_drawn_says_so():
    from modules.utility.em_matrix_map import zoom_to_unit

    layer = _Layer("US view", ("sito", "area", "us"), [])
    iface = _Iface()
    fatto, messaggio = zoom_to_unit(iface, _us(), layers=[layer])
    assert not fatto
    assert iface.mapCanvas().inquadratura is None
    assert "disegn" in messaggio.lower()
    assert "1.US1" in messaggio


def test_a_row_in_the_layer_without_a_geometry_is_not_a_drawing():
    from modules.utility.em_matrix_map import zoom_to_unit

    layer = _Layer("US view", ("sito", "area", "us"), [_Feature(1, None)])
    fatto, messaggio = zoom_to_unit(_Iface(), _us(), layers=[layer])
    assert not fatto
    assert "disegn" in messaggio.lower()


def test_when_no_loaded_layer_knows_the_unit_it_says_which_layers_to_load():
    from modules.utility.em_matrix_map import zoom_to_unit

    layer = _Layer("Catasto", ("fid", "foglio"), [])
    fatto, messaggio = zoom_to_unit(_Iface(), _us(), layers=[layer])
    assert not fatto
    assert "layer" in messaggio.lower()


def test_a_node_that_is_not_a_record_is_never_looked_for_on_the_map():
    from modules.utility.em_matrix_map import zoom_to_unit

    layer = _Layer("US view", ("sito", "area", "us"),
                   [_Feature(1, _Riquadro(0, 0, 1, 1))])
    fatto, _ = zoom_to_unit(_Iface(), _unit(label="CON 1"), layers=[layer])
    assert not fatto
    assert layer.selezionate is None


def test_a_broken_layer_does_not_stop_the_next_one():
    from modules.utility.em_matrix_map import zoom_to_unit

    class Rotto(_Layer):
        def getFeatures(self, request=None):
            raise RuntimeError("fonte non raggiungibile")

    rotto = Rotto("Rotto", ("sito", "area", "us"))
    buono = _Layer("Disegni", ("scavo_s", "area_s", "us_s"),
                   [_Feature(7, _Riquadro(1, 1, 2, 2))])
    fatto, messaggio = zoom_to_unit(_Iface(), _us(), layers=[rotto, buono])
    assert fatto, messaggio
    assert buono.selezionate == [7]


# ------------------------------------------------------------- le promesse

def test_the_map_module_only_reads_the_project():
    """Zoomare non è modificare: il pannello non deve aggiungere layer,
    aprire una modifica o cancellare niente nel progetto dell'utente."""
    vietati = ("addMapLayer", "removeMapLayer", "startEditing",
               "commitChanges", "deleteFeature", "setDataSource",
               "removeAllMapLayers", "addGroup")
    src = MAP.read_text(encoding="utf-8")
    assert not [v for v in vietati if v in src]


def test_the_layers_come_in_the_order_of_the_legend():
    """mapLayers() è un dizionario e l'ordine è quello che capita: fra due
    layer che sanno rispondere si prova prima quello che l'utente vede in
    cima."""
    src = MAP.read_text(encoding="utf-8")
    assert "layerTreeRoot" in src and "findLayers" in src


def test_the_coordinates_are_reprojected_when_the_layer_is_not_in_the_canvas_crs():
    src = MAP.read_text(encoding="utf-8")
    assert "QgsCoordinateTransform" in src


def test_the_map_module_does_not_need_a_web_engine():
    import ast

    moduli = set()
    for nodo in ast.walk(ast.parse(MAP.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            moduli |= {a.name for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            moduli.add(nodo.module)
    assert not [m for m in moduli if "WebEngine" in m or "WebKit" in m], moduli
