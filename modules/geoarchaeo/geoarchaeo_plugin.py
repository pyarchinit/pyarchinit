"""
Plugin principale GeoArchaeo
Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

import os
import sys
import glob
from qgis.core import (
    QgsProcessingProvider, QgsApplication, QgsMessageLog,
    Qgis, QgsProject, QgsVectorLayer, QgsRasterLayer
)
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QAction
from qgis.PyQt.QtWidgets import QDockWidget, QMenu

from .processing_provider import GeoArchaeoProvider
from .gui.main_dock import GeoArchaeoDockWidget
from .core.geostat_engine import GeostatEngine
from .compat import (
    Qt_RightDockWidgetArea, Qgis_Info, Qgis_Warning,
    Qgis_Critical, Qgis_Success, exec_dialog
)


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
        
        # Inizializza motore geostatistico
        self.engine = GeostatEngine()
        
    def initGui(self):
        """Inizializza interfaccia plugin"""
        # Aggiungi provider Processing
        self.provider = GeoArchaeoProvider(self.engine)
        QgsApplication.processingRegistry().addProvider(self.provider)
        
        # Crea toolbar
        self.toolbar = self.iface.addToolBar('GeoArchaeo')
        self.toolbar.setObjectName('GeoArchaeoToolbar')
        
        # Crea dock widget
        self.dock = GeoArchaeoDockWidget()
        self.iface.addDockWidget(Qt_RightDockWidgetArea, self.dock)
        
        # Aggiungi azioni
        self._create_actions()
        
        # Log inizializzazione
        QgsMessageLog.logMessage(
            'GeoArchaeo Plugin caricato con successo',
            'GeoArchaeo', Qgis_Info
        )
        
    def _create_actions(self):
        """Crea azioni del plugin"""
        # Azione principale - mostra/nascondi dock
        icon = QIcon(os.path.join(self.plugin_dir, 'icons', 'geoarchaeo.png'))
        action = QAction(icon, 'GeoArchaeo Panel', self.iface.mainWindow())
        action.triggered.connect(self.toggle_dock)
        action.setCheckable(True)
        self.toolbar.addAction(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        
        # Azioni rapide
        actions_config = [
            ('variogram.png', 'Variogramma Rapido', self.quick_variogram),
            ('kriging.png', 'Kriging Rapido', self.quick_kriging),
            ('ml.png', 'Pattern Recognition', self.ml_analysis),
            ('report.png', 'Genera Report', self.generate_report)
        ]
        
        self.toolbar.addSeparator()
        
        # Aggiungi bottone Help
        help_icon = QIcon(os.path.join(self.plugin_dir, 'icons', 'help.png'))
        help_action = QAction(help_icon, 'Guida GeoArchaeo', self.iface.mainWindow())
        help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(help_action)
        self.iface.addPluginToMenu(self.menu, help_action)
        self.actions.append(help_action)
        
        # Aggiungi bottone Test Layers
        test_icon = QIcon(os.path.join(self.plugin_dir, 'icons', 'test.png'))
        test_action = QAction(test_icon, 'Carica Layer di Test', self.iface.mainWindow())
        test_action.triggered.connect(self.load_test_layers)
        self.toolbar.addAction(test_action)
        self.iface.addPluginToMenu(self.menu, test_action)
        self.actions.append(test_action)
        
        self.toolbar.addSeparator()
        
        for icon_name, text, callback in actions_config:
            icon = QIcon(os.path.join(self.plugin_dir, 'icons', icon_name))
            action = QAction(icon, text, self.iface.mainWindow())
            action.triggered.connect(callback)
            self.toolbar.addAction(action)
            self.iface.addPluginToMenu(self.menu, action)
            self.actions.append(action)
            
    def toggle_dock(self):
        """Mostra/nascondi dock widget"""
        if self.dock:
            self.dock.setVisible(not self.dock.isVisible())
            
    def quick_variogram(self):
        """Lancia analisi variogramma rapida"""
        if self.dock:
            self.dock.switch_to_tab('variogram')
            self.dock.show()
            
    def quick_kriging(self):
        """Lancia kriging rapido"""
        if self.dock:
            self.dock.switch_to_tab('kriging')
            self.dock.show()
            
    def ml_analysis(self):
        """Lancia analisi Machine Learning"""
        if self.dock:
            self.dock.switch_to_tab('ml')
            self.dock.show()
            
    def generate_report(self):
        """Genera report completo"""
        if self.dock:
            self.dock.generate_full_report()
    
    def show_help(self):
        """Mostra guida HTML"""
        import webbrowser
        help_file = os.path.join(self.plugin_dir, 'doc', 'help.html')
        if os.path.exists(help_file):
            webbrowser.open(f'file://{help_file}')
        else:
            QgsMessageLog.logMessage(
                'File guida non trovato',
                'GeoArchaeo', Qgis_Warning
            )
    
    def load_test_layers(self):
        """Carica layer di test"""
        from qgis.PyQt.QtWidgets import QMenu
        import glob
        
        # Crea menu per scegliere quale layer caricare
        menu = QMenu()
        
        test_dir = os.path.join(self.plugin_dir, 'test_layers')
        if not os.path.exists(test_dir):
            QgsMessageLog.logMessage(
                'Cartella test_layers non trovata',
                'GeoArchaeo', Qgis_Warning
            )
            return
            
        # Trova tutti i file disponibili
        csv_files = glob.glob(os.path.join(test_dir, '*.csv'))
        geojson_files = glob.glob(os.path.join(test_dir, '*.geojson'))
        
        # Aggiungi azione per caricare tutti i layer
        load_all_action = menu.addAction('Carica Tutti i Layer')
        load_all_action.triggered.connect(lambda: self._load_all_test_layers())
        menu.addSeparator()
        
        # Aggiungi azioni per singoli layer
        for csv_file in csv_files:
            basename = os.path.basename(csv_file).replace('.csv', '')
            action = menu.addAction(f'CSV: {basename}')
            action.triggered.connect(lambda checked, f=csv_file: self._load_csv_layer(f))
            
        menu.addSeparator()
        
        for geojson_file in geojson_files:
            basename = os.path.basename(geojson_file).replace('.geojson', '')
            action = menu.addAction(f'GeoJSON: {basename}')
            action.triggered.connect(lambda checked, f=geojson_file: self._load_geojson_layer(f))
            
        # Mostra menu al posto del cursore
        # Qt5/Qt6 compatible menu popup
        pos = self.iface.mainWindow().cursor().pos()
        if hasattr(menu, 'exec'):
            menu.exec(pos)
        else:
            menu.exec_(pos)
            
    def _load_csv_layer(self, filepath):
        """Carica un layer CSV"""
        from qgis.core import QgsVectorLayer, QgsProject
        
        basename = os.path.basename(filepath).replace('.csv', '')
        
        # URI per CSV con coordinate
        uri = f'file:///{filepath}?delimiter=,&xField=x&yField=y&crs=EPSG:32633'
        
        layer = QgsVectorLayer(uri, basename, 'delimitedtext')
        
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            QgsMessageLog.logMessage(
                f'Layer {basename} caricato con successo',
                'GeoArchaeo', Qgis_Success
            )
        else:
            QgsMessageLog.logMessage(
                f'Errore nel caricamento di {basename}',
                'GeoArchaeo', Qgis_Critical
            )
            
    def _load_geojson_layer(self, filepath):
        """Carica un layer GeoJSON"""
        from qgis.core import QgsVectorLayer, QgsProject
        
        basename = os.path.basename(filepath).replace('.geojson', '')
        
        layer = QgsVectorLayer(filepath, basename, 'ogr')
        
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            QgsMessageLog.logMessage(
                f'Layer {basename} caricato con successo',
                'GeoArchaeo', Qgis_Success
            )
        else:
            QgsMessageLog.logMessage(
                f'Errore nel caricamento di {basename}',
                'GeoArchaeo', Qgis_Critical
            )
            
    def _load_all_test_layers(self):
        """Carica tutti i layer di test disponibili"""
        test_dir = os.path.join(self.plugin_dir, 'test_layers')
        
        # Preferisci GeoJSON se disponibili
        loaded = 0
        
        # Prima carica i GeoJSON
        for geojson_file in glob.glob(os.path.join(test_dir, '*.geojson')):
            self._load_geojson_layer(geojson_file)
            loaded += 1
            
        # Poi carica CSV solo se non c'è il corrispondente GeoJSON
        for csv_file in glob.glob(os.path.join(test_dir, '*.csv')):
            basename = os.path.basename(csv_file).replace('.csv', '')
            geojson_path = os.path.join(test_dir, f'{basename}.geojson')
            if not os.path.exists(geojson_path):
                self._load_csv_layer(csv_file)
                loaded += 1
                
        QgsMessageLog.logMessage(
            f'{loaded} layer di test caricati',
            'GeoArchaeo', Qgis_Success
        )
            
    def unload(self):
        """Rimuove il plugin"""
        # Rimuovi provider
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            
        # Rimuovi GUI
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
            
        if self.toolbar:
            del self.toolbar
            
        if self.dock:
            self.iface.removeDockWidget(self.dock)
            del self.dock