# -*- coding: utf-8 -*-
"""
3D DEM viewer dialog for the PyArchInit Site Dashboard.

Shows a QGIS 3D map canvas with:
  - a DEM raster used as terrain (pre-excavation)
  - optional DEM-difference raster draped over the terrain
  - optional TIN mesh layers (pre / post surfaces) to visualise volume

The dialog is fully defensive: if the ``qgis._3d`` module is not available
(headless builds, some minimal QGIS installs) a clear message is shown
instead of crashing.

Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6).

Author: Enzo Cocca
"""
from __future__ import absolute_import

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
    QPushButton, QCheckBox, QSizePolicy, QFrame, QWidget,
)
from qgis.core import QgsProject, QgsVector3D

# Defensive import of the 3D module — may be missing on headless builds
_HAS_3D = True
try:
    from qgis._3d import (
        Qgs3DMapSettings,
        Qgs3DMapCanvas,
        QgsDemTerrainGenerator,
        QgsFlatTerrainGenerator,
    )
except Exception:  # pragma: no cover
    _HAS_3D = False
    Qgs3DMapSettings = None  # type: ignore
    Qgs3DMapCanvas = None    # type: ignore


# --------------------------------------------------------------------------- #
#                          Qt5 / Qt6 compatibility helpers                    #
# --------------------------------------------------------------------------- #

def _align_center():
    try:
        return Qt.AlignmentFlag.AlignCenter  # Qt6
    except AttributeError:
        return Qt.AlignCenter                # Qt5


def _sp_expanding():
    """QSizePolicy.Expanding in Qt5, QSizePolicy.Policy.Expanding in Qt6."""
    try:
        return QSizePolicy.Policy.Expanding  # Qt6
    except AttributeError:
        return QSizePolicy.Expanding         # Qt5


def _frame_styled_panel():
    try:
        return QFrame.Shape.StyledPanel      # Qt6
    except AttributeError:
        return QFrame.StyledPanel            # Qt5


# --------------------------------------------------------------------------- #
#                                Translations                                 #
# --------------------------------------------------------------------------- #

_I18N = {
    'it': {
        'title': 'Vista 3D - Computo Metrico',
        'exag': 'Esagerazione verticale:',
        'drape_diff': 'Mostra differenza DEM (cut/fill)',
        'show_mesh_pre': 'Mostra mesh DEM pre',
        'show_mesh_post': 'Mostra mesh DEM post',
        'reset': 'Reset Vista',
        'close': 'Chiudi',
        'no_3d': 'Il modulo QGIS 3D non è disponibile in questo profilo.\n'
                 'Abilitare il supporto 3D dalle impostazioni di QGIS.',
        'legend': 'Rosso = scavo / Blu = riporto',
    },
    'en': {
        'title': '3D View - Quantity Surveying',
        'exag': 'Vertical exaggeration:',
        'drape_diff': 'Show DEM difference (cut/fill)',
        'show_mesh_pre': 'Show pre-DEM mesh',
        'show_mesh_post': 'Show post-DEM mesh',
        'reset': 'Reset View',
        'close': 'Close',
        'no_3d': 'QGIS 3D module is not available in this profile.\n'
                 'Enable 3D support in QGIS settings.',
        'legend': 'Red = cut / Blue = fill',
    },
    'de': {
        'title': '3D-Ansicht - Mengenermittlung',
        'exag': 'Vertikale Überhöhung:',
        'drape_diff': 'DEM-Differenz anzeigen (Abtrag/Auftrag)',
        'show_mesh_pre': 'Pre-DEM-Mesh anzeigen',
        'show_mesh_post': 'Post-DEM-Mesh anzeigen',
        'reset': 'Ansicht zurücksetzen',
        'close': 'Schließen',
        'no_3d': 'Das QGIS-3D-Modul ist in diesem Profil nicht verfügbar.',
        'legend': 'Rot = Abtrag / Blau = Auftrag',
    },
    'es': {
        'title': 'Vista 3D - Mediciones',
        'exag': 'Exageración vertical:',
        'drape_diff': 'Mostrar diferencia DEM (corte/relleno)',
        'show_mesh_pre': 'Mostrar malla DEM pre',
        'show_mesh_post': 'Mostrar malla DEM post',
        'reset': 'Restablecer vista',
        'close': 'Cerrar',
        'no_3d': 'El módulo QGIS 3D no está disponible en este perfil.',
        'legend': 'Rojo = corte / Azul = relleno',
    },
    'fr': {
        'title': 'Vue 3D - Métré',
        'exag': 'Exagération verticale :',
        'drape_diff': 'Afficher différence MNT (déblai/remblai)',
        'show_mesh_pre': 'Afficher maillage MNT pré',
        'show_mesh_post': 'Afficher maillage MNT post',
        'reset': 'Réinitialiser',
        'close': 'Fermer',
        'no_3d': "Le module QGIS 3D n'est pas disponible dans ce profil.",
        'legend': 'Rouge = déblai / Bleu = remblai',
    },
    'ar': {
        'title': 'عرض ثلاثي الأبعاد - حساب الكميات',
        'exag': 'المبالغة العمودية:',
        'drape_diff': 'عرض فرق DEM',
        'show_mesh_pre': 'عرض شبكة DEM قبل',
        'show_mesh_post': 'عرض شبكة DEM بعد',
        'reset': 'إعادة ضبط',
        'close': 'إغلاق',
        'no_3d': 'وحدة QGIS ثلاثية الأبعاد غير متاحة في هذا الملف الشخصي.',
        'legend': 'أحمر = حفر / أزرق = ردم',
    },
    'ca': {
        'title': "Vista 3D - Amidament",
        'exag': 'Exageració vertical:',
        'drape_diff': 'Mostra diferència DEM',
        'show_mesh_pre': 'Mostra malla DEM pre',
        'show_mesh_post': 'Mostra malla DEM post',
        'reset': 'Restableix',
        'close': 'Tanca',
        'no_3d': 'El mòdul QGIS 3D no està disponible.',
        'legend': 'Vermell = excavació / Blau = reompliment',
    },
    'ro': {
        'title': 'Vizualizare 3D - Măsurători',
        'exag': 'Exagerare verticală:',
        'drape_diff': 'Afișează diferența DEM (săpare/umplere)',
        'show_mesh_pre': 'Afișează mesh DEM pre',
        'show_mesh_post': 'Afișează mesh DEM post',
        'reset': 'Resetează Vederea',
        'close': 'Închide',
        'no_3d': 'Modulul QGIS 3D nu este disponibil în acest profil.',
        'legend': 'Roșu = săpare / Albastru = umplere',
    },
    'pt': {
        'title': 'Vista 3D - Medição',
        'exag': 'Exagero vertical:',
        'drape_diff': 'Mostrar diferença DEM (corte/aterro)',
        'show_mesh_pre': 'Mostrar malha DEM pré',
        'show_mesh_post': 'Mostrar malha DEM pós',
        'reset': 'Redefinir Vista',
        'close': 'Fechar',
        'no_3d': 'O módulo QGIS 3D não está disponível neste perfil.',
        'legend': 'Vermelho = corte / Azul = aterro',
    },
    'el': {
        'title': 'Προβολή 3D - Επιμετρήσεις',
        'exag': 'Κατακόρυφη υπερύψωση:',
        'drape_diff': 'Εμφάνιση διαφοράς DEM',
        'show_mesh_pre': 'Εμφάνιση πλέγματος pre-DEM',
        'show_mesh_post': 'Εμφάνιση πλέγματος post-DEM',
        'reset': 'Επαναφορά',
        'close': 'Κλείσιμο',
        'no_3d': 'Η μονάδα QGIS 3D δεν είναι διαθέσιμη σε αυτό το προφίλ.',
        'legend': 'Κόκκινο = εκσκαφή / Μπλε = πλήρωση',
    },
}


# --------------------------------------------------------------------------- #
#                                  Dialog                                     #
# --------------------------------------------------------------------------- #

class Dem3dViewerDialog(QDialog):
    """
    Stand-alone 3D viewer window.

    Parameters
    ----------
    parent : QWidget or None
    terrain_layer : QgsRasterLayer
        DEM used as terrain source (typically the pre-excavation DEM).
    drape_layer : QgsRasterLayer, optional
        DEM-difference raster draped over the terrain.
    mesh_pre_layer : QgsMeshLayer, optional
    mesh_post_layer : QgsMeshLayer, optional
    lang : str
        2-letter language code for UI strings.
    """

    def __init__(self, parent, terrain_layer,
                 drape_layer=None, mesh_pre_layer=None, mesh_post_layer=None,
                 lang='en'):
        super().__init__(parent)
        self.terrain_layer = terrain_layer
        self.drape_layer = drape_layer
        self.mesh_pre_layer = mesh_pre_layer
        self.mesh_post_layer = mesh_post_layer
        self.lang = lang if lang in _I18N else 'en'

        self._t = _I18N[self.lang]
        self.map_settings = None
        self.canvas_3d = None

        self.setWindowTitle(self._t['title'])
        self.resize(1050, 720)

        self._build_ui()
        if _HAS_3D and self.terrain_layer is not None:
            self._setup_3d_canvas()
        else:
            self._show_not_available()

    # ------------------------------------------------------------------ UI --

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # Controls bar
        controls = QFrame(self)
        controls.setFrameShape(_frame_styled_panel())
        controls.setStyleSheet(
            "QFrame { background:#eceff1; border:1px solid #b0bec5; border-radius:4px; }"
            "QLabel { background: transparent; }"
        )
        ctrl_layout = QHBoxLayout(controls)
        ctrl_layout.setContentsMargins(8, 6, 8, 6)

        ctrl_layout.addWidget(QLabel(self._t['exag']))
        self.exag_spin = QDoubleSpinBox()
        self.exag_spin.setRange(0.1, 20.0)
        self.exag_spin.setSingleStep(0.5)
        self.exag_spin.setDecimals(1)
        self.exag_spin.setValue(2.0)
        self.exag_spin.valueChanged.connect(self._on_exag_changed)
        ctrl_layout.addWidget(self.exag_spin)

        ctrl_layout.addSpacing(12)

        self.chk_drape = QCheckBox(self._t['drape_diff'])
        self.chk_drape.setChecked(self.drape_layer is not None)
        self.chk_drape.setEnabled(self.drape_layer is not None)
        self.chk_drape.toggled.connect(self._refresh_layer_set)
        ctrl_layout.addWidget(self.chk_drape)

        self.chk_mesh_pre = QCheckBox(self._t['show_mesh_pre'])
        self.chk_mesh_pre.setChecked(self.mesh_pre_layer is not None)
        self.chk_mesh_pre.setEnabled(self.mesh_pre_layer is not None)
        self.chk_mesh_pre.toggled.connect(self._refresh_layer_set)
        ctrl_layout.addWidget(self.chk_mesh_pre)

        self.chk_mesh_post = QCheckBox(self._t['show_mesh_post'])
        self.chk_mesh_post.setChecked(self.mesh_post_layer is not None)
        self.chk_mesh_post.setEnabled(self.mesh_post_layer is not None)
        self.chk_mesh_post.toggled.connect(self._refresh_layer_set)
        ctrl_layout.addWidget(self.chk_mesh_post)

        ctrl_layout.addStretch(1)

        self.btn_reset = QPushButton(self._t['reset'])
        self.btn_reset.clicked.connect(self._reset_view)
        ctrl_layout.addWidget(self.btn_reset)

        self.btn_close = QPushButton(self._t['close'])
        self.btn_close.clicked.connect(self.accept)
        ctrl_layout.addWidget(self.btn_close)

        root.addWidget(controls)

        # Legend bar
        legend = QLabel(self._t['legend'])
        legend.setAlignment(_align_center())
        legend.setStyleSheet(
            "QLabel { padding:4px; font-size:10px; "
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #b2182b, stop:0.5 #f7f7f7, stop:1 #2166ac); "
            "color:#263238; border:1px solid #90a4ae; border-radius:3px; }"
        )
        root.addWidget(legend)

        # Placeholder; real canvas inserted in _setup_3d_canvas
        self._canvas_host = QWidget(self)
        self._canvas_host.setSizePolicy(_sp_expanding(), _sp_expanding())
        self._canvas_host_layout = QVBoxLayout(self._canvas_host)
        self._canvas_host_layout.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._canvas_host, 1)

    # --------------------------------------------------------------- 3D --

    def _setup_3d_canvas(self):
        try:
            self.map_settings = Qgs3DMapSettings()

            crs = self.terrain_layer.crs()
            if not crs.isValid():
                crs = QgsProject.instance().crs()
            self.map_settings.setCrs(crs)

            extent = self.terrain_layer.extent()
            try:
                self.map_settings.setExtent(extent)
            except (AttributeError, TypeError):
                pass

            # Origin at centre of terrain (required in QGIS >= 3.26)
            try:
                center = extent.center()
                self.map_settings.setOrigin(
                    QgsVector3D(center.x(), center.y(), 0.0)
                )
            except Exception:
                pass

            # Layers in the 3D scene
            self._apply_layers_to_settings()

            # DEM terrain generator
            try:
                terrain = QgsDemTerrainGenerator()
                terrain.setLayer(self.terrain_layer)
                self.map_settings.setTerrainGenerator(terrain)
            except Exception:
                flat = QgsFlatTerrainGenerator()
                flat.setCrs(crs)
                flat.setExtent(extent)
                self.map_settings.setTerrainGenerator(flat)

            # Vertical exaggeration
            try:
                self.map_settings.setTerrainVerticalScale(self.exag_spin.value())
            except Exception:
                pass

            # Background
            try:
                from qgis.PyQt.QtGui import QColor as _QC
                self.map_settings.setBackgroundColor(_QC('#0d1b2a'))
            except Exception:
                pass

            # Canvas
            self.canvas_3d = Qgs3DMapCanvas(self)
            try:
                self.canvas_3d.setMap(self.map_settings)
            except AttributeError:
                # QGIS 4 renamed to setMapSettings in some builds
                setter = getattr(self.canvas_3d, 'setMapSettings', None)
                if setter:
                    setter(self.map_settings)

            self.canvas_3d.setSizePolicy(
                _sp_expanding(), _sp_expanding()
            )
            self._canvas_host_layout.addWidget(self.canvas_3d)
            self._reset_view()
        except Exception as ex:
            err = QLabel(f"{self._t['no_3d']}\n\n{ex}")
            err.setAlignment(_align_center())
            err.setStyleSheet("QLabel { color:#c62828; padding:20px; }")
            self._canvas_host_layout.addWidget(err)

    def _apply_layers_to_settings(self):
        """Recompute the list of layers shown in the 3D scene and push it."""
        if self.map_settings is None:
            return
        layers = []
        if self.chk_drape.isChecked() and self.drape_layer is not None:
            layers.append(self.drape_layer)
        if self.chk_mesh_pre.isChecked() and self.mesh_pre_layer is not None:
            layers.append(self.mesh_pre_layer)
        if self.chk_mesh_post.isChecked() and self.mesh_post_layer is not None:
            layers.append(self.mesh_post_layer)
        if not layers:
            # Fall back to the terrain raster itself so the scene is not empty
            layers.append(self.terrain_layer)
        try:
            self.map_settings.setLayers(layers)
        except Exception:
            pass

    def _refresh_layer_set(self, _checked=None):
        self._apply_layers_to_settings()
        if self.canvas_3d is not None:
            try:
                self.canvas_3d.update()
            except Exception:
                pass

    def _on_exag_changed(self, val):
        if self.map_settings is not None:
            try:
                self.map_settings.setTerrainVerticalScale(float(val))
            except Exception:
                pass
            if self.canvas_3d is not None:
                try:
                    self.canvas_3d.update()
                except Exception:
                    pass

    def _reset_view(self):
        if self.canvas_3d is None or self.terrain_layer is None:
            return
        try:
            extent = self.terrain_layer.extent()
            cx = extent.center().x()
            cy = extent.center().y()
            dist = max(extent.width(), extent.height()) * 1.5
            for method, args in (
                ('setViewFromTop', (cx, cy, dist)),
                ('resetView', (dist,)),
                ('zoomToFullExtent', ()),
            ):
                fn = getattr(self.canvas_3d, method, None)
                if fn is not None:
                    try:
                        fn(*args)
                        return
                    except TypeError:
                        try:
                            fn()
                            return
                        except Exception:
                            continue
                    except Exception:
                        continue
        except Exception:
            pass

    def _show_not_available(self):
        msg = QLabel(self._t['no_3d'])
        msg.setAlignment(_align_center())
        msg.setWordWrap(True)
        msg.setStyleSheet(
            "QLabel { color:#c62828; padding:40px; font-size:13px; }"
        )
        self._canvas_host_layout.addWidget(msg)
        # Disable 3D-related controls
        self.exag_spin.setEnabled(False)
        self.chk_drape.setEnabled(False)
        self.chk_mesh_pre.setEnabled(False)
        self.chk_mesh_post.setEnabled(False)
        self.btn_reset.setEnabled(False)
