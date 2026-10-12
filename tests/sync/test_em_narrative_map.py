"""Le unità di cui parla la narrativa, evidenziate sulla mappa (2026-10-12,
«evidenziando le geometrie di cui sta discutendo»). Layer finti, come per
lo zoom della scheda Unità."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _unit(node_id, label, **dati):
    from modules.utility.em_matrix_model import Unit
    return Unit(node_id=node_id, label=label, node_type="US", epoch_id=None, data=dati)


def _crs():
    from qgis.core import QgsCoordinateReferenceSystem
    return QgsCoordinateReferenceSystem()


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
    def __init__(self, fid, riquadro, attributi):
        self._id, self._g, self._a = fid, _Geometria(riquadro), attributi

    def id(self):
        return self._id

    def geometry(self):
        return self._g

    def hasGeometry(self):
        return self._g._r is not None


class _Layer:
    """Un layer finto che filtra le feature con l'espressione `"us" = '2'`
    quanto basta per il test: guarda il numero di US nell'espressione."""

    def __init__(self, nome, campi, feature=()):
        self._nome, self._campi, self._feature = nome, [_Campo(c) for c in campi], list(feature)
        self.selezioni = []
        self.lampi = []

    def name(self):
        return self._nome

    def fields(self):
        return self._campi

    def crs(self):
        return _crs()

    def getFeatures(self, request=None):
        espressione = request.filterExpression().expression() if request is not None else ""
        return iter([f for f in self._feature
                     if any("'%s'" % f._a.get("us") in espressione for _ in [0])])

    def selectByIds(self, ids):
        self.selezioni.append(list(ids))


class _Impostazioni:
    def destinationCrs(self):
        return _crs()


class _Canvas:
    def __init__(self):
        self.inquadratura = None
        self.aggiornato = 0

    def mapSettings(self):
        return _Impostazioni()

    def setExtent(self, r):
        self.inquadratura = (r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum())

    def refresh(self):
        self.aggiornato += 1

    def flashFeatureIds(self, layer, ids):
        layer.lampi.append(list(ids))


class _Iface:
    def __init__(self):
        self._canvas = _Canvas()

    def mapCanvas(self):
        return self._canvas


def _layer_con_due_us():
    return _Layer("US view", ("sito", "area", "us", "unita_tipo"),
                  [_Feature(3, _Riquadro(0, 0, 10, 10), {"us": "2"}),
                   _Feature(4, _Riquadro(20, 20, 30, 30), {"us": "3"})])


def test_le_unita_del_capitolo_si_selezionano_insieme_e_si_inquadrano_tutte():
    from modules.utility.em_matrix_map import zoom_to_units
    layer = _layer_con_due_us()
    iface = _Iface()
    unita = [_unit("u2", "1.US2", sito="Scavo", area="1", us="2", unita_tipo="US"),
             _unit("u3", "1.US3", sito="Scavo", area="1", us="3", unita_tipo="US")]
    quante, messaggio = zoom_to_units(iface, unita, layers=[layer], margin=0.0)
    assert quante == 2
    assert layer.selezioni == [[3, 4]]                                 # una selezione sola, tutte insieme
    assert iface.mapCanvas().inquadratura == (0, 0, 30, 30)
    assert iface.mapCanvas().aggiornato == 1 and layer.lampi == [[3, 4]]
    assert "2" in messaggio and "US view" in messaggio


def test_le_unita_non_disegnate_si_dicono_per_nome_e_le_altre_si_evidenziano():
    from modules.utility.em_matrix_map import zoom_to_units
    layer = _layer_con_due_us()
    iface = _Iface()
    unita = [_unit("u2", "1.US2", sito="Scavo", area="1", us="2", unita_tipo="US"),
             _unit("u9", "1.US9", sito="Scavo", area="1", us="9", unita_tipo="US"),
             _unit("d1", "Relazione")]                                 # non è una riga della scheda
    quante, messaggio = zoom_to_units(iface, unita, layers=[layer], margin=0.0)
    assert quante == 1 and layer.selezioni == [[3]]
    assert "1.US9" in messaggio and "Relazione" not in messaggio
    assert iface.mapCanvas().inquadratura == (0, 0, 10, 10)


def test_senza_niente_da_mostrare_lo_dice_e_non_tocca_la_mappa():
    from modules.utility.em_matrix_map import zoom_to_units
    iface = _Iface()
    quante, messaggio = zoom_to_units(iface, [_unit("d1", "Relazione")], layers=[_layer_con_due_us()])
    assert quante == 0 and messaggio and iface.mapCanvas().aggiornato == 0
    quante, messaggio = zoom_to_units(iface, [_unit("u9", "1.US9", sito="S", area="1", us="9", unita_tipo="US")],
                                      layers=[_layer_con_due_us()], lang="en")
    assert quante == 0 and "1.US9" in messaggio and iface.mapCanvas().aggiornato == 0


def test_il_pannello_evidenzia_dagli_id_dei_nodi(monkeypatch):
    from modules.s3dgraphy import em_matrix_panel as panel
    panel.remember_units([_unit("u2", "1.US2", sito="Scavo", area="1", us="2", unita_tipo="US"),
                          _unit("d1", "Relazione")])
    panel.remember_connection(None)
    visti = []

    def finto(iface, units, connection=None, **kw):
        visti.append([u.node_id for u in units])
        return len(units), "ok"
    monkeypatch.setattr("modules.utility.em_matrix_map.zoom_to_units", finto)
    assert panel.can_highlight(["u2", "d1", "zz"]) and not panel.can_highlight(["d1", "zz"])
    assert panel.highlight(object(), ["u2", "d1", "zz"]) == (1, "ok")
    assert visti == [["u2"]]
