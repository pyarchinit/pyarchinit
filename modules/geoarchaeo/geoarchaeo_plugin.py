"""
Plugin principale GeoArchaeo
Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

import os
import webbrowser

from qgis.core import QgsApplication, QgsMessageLog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .processing_provider import GeoArchaeoProvider
from .gui.main_dock import GeoArchaeoDockWidget
from .core.geostat_engine import GeostatEngine
from .i18n import tr
from .compat import Qt_RightDockWidgetArea, Qgis_Info, Qgis_Warning


class GeoArchaeoPlugin:
    """Plugin QGIS per analisi geostatistica archeologica avanzata"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.provider = None
        self.dock = None
        self.toolbar = None
        self.actions = []
        self.menu = '&GeoArchaeo'
        self.engine = GeostatEngine()

    def initGui(self):
        """Inizializza interfaccia plugin"""
        self.provider = GeoArchaeoProvider(self.engine)
        QgsApplication.processingRegistry().addProvider(self.provider)

        self.toolbar = self.iface.addToolBar('GeoArchaeo')
        self.toolbar.setObjectName('GeoArchaeoToolbar')

        self.dock = GeoArchaeoDockWidget(self.iface)
        self.iface.addDockWidget(Qt_RightDockWidgetArea, self.dock)

        self._create_actions()
        QgsMessageLog.logMessage('GeoArchaeo plugin loaded', 'GeoArchaeo', Qgis_Info)

    def _icon(self, name):
        return QIcon(os.path.join(self.plugin_dir, 'icons', name))

    def _add_action(self, icon_name, text, callback, checkable=False):
        action = QAction(self._icon(icon_name), text, self.iface.mainWindow())
        action.triggered.connect(callback)
        action.setCheckable(checkable)
        self.toolbar.addAction(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def _create_actions(self):
        """Crea azioni del plugin"""
        self.panel_action = self._add_action('geoarchaeo.png', tr('toolbar_panel'), self.toggle_dock, checkable=True)
        self.panel_action.setChecked(True)
        self.dock.visibilityChanged.connect(self.panel_action.setChecked)
        self.toolbar.addSeparator()
        self._add_action('help.png', tr('toolbar_help'), self.show_help)
        self._add_action('test.png', tr('toolbar_examples'), self.load_test_layers)
        self.toolbar.addSeparator()
        self._add_action('variogram.png', tr('toolbar_variogram'), self.quick_variogram)
        self._add_action('kriging.png', tr('toolbar_kriging'), self.quick_kriging)
        self._add_action('ml.png', tr('toolbar_ml'), self.ml_analysis)
        self._add_action('report.png', tr('toolbar_report'), self.generate_report)

    def toggle_dock(self, checked=None):
        """Mostra/nascondi dock widget"""
        if self.dock:
            visible = checked if isinstance(checked, bool) else not self.dock.isVisible()
            self.dock.setVisible(visible)

    def _show_tab(self, name):
        if self.dock:
            self.dock.switch_to_tab(name)
            self.dock.show()
            self.dock.raise_()

    def quick_variogram(self):
        self._show_tab('variogram')

    def quick_kriging(self):
        self._show_tab('kriging')

    def ml_analysis(self):
        self._show_tab('ml')

    def generate_report(self):
        if self.dock:
            self.dock.show()
            self.dock.raise_()
            self.dock.generate_full_report()

    def show_help(self):
        """Mostra guida HTML"""
        help_file = os.path.join(self.plugin_dir, 'doc', 'help.html')
        if os.path.exists(help_file):
            webbrowser.open(f'file://{help_file}')
        else:
            QgsMessageLog.logMessage('Help file not found', 'GeoArchaeo', Qgis_Warning)

    def load_test_layers(self):
        """Apre il dialogo dei dati di esempio (cartella test_layers del plugin)"""
        if self.dock:
            self.dock.show()
            self.dock.show_load_examples_dialog()

    def unload(self):
        """Rimuove il plugin"""
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions = []

        if self.toolbar:
            self.iface.mainWindow().removeToolBar(self.toolbar)
            self.toolbar.deleteLater()
            self.toolbar = None

        if self.dock:
            self.dock.cleanup()
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
            self.dock = None
