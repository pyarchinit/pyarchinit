"""
Plugin QGIS GeoArchaeo - Advanced Geostatistical Analysis for Archaeological Research
Full version with Co-Kriging, Spatio-Temporal, ML and Interactive Charts
Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

import sys
import subprocess
import importlib
from qgis.core import QgsMessageLog, Qgis
from qgis.PyQt.QtWidgets import QMessageBox

# Qt5/Qt6 compatibility for Qgis message levels
try:
    Qgis_Info = Qgis.MessageLevel.Info
    Qgis_Warning = Qgis.MessageLevel.Warning
except AttributeError:
    Qgis_Info = Qgis_Info
    Qgis_Warning = Qgis_Warning

def check_and_install_dependencies():
    """Verifica e installa le dipendenze necessarie"""
    required_packages = {
        'numpy': 'numpy>=1.20',
        'scipy': 'scipy>=1.5',
        'pandas': 'pandas>=1.0',
        'sklearn': 'scikit-learn>=0.24',
        'plotly': 'plotly>=5.0'
    }
    
    missing_packages = []
    
    for module_name, package_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            QgsMessageLog.logMessage(f"{module_name} trovato", 'GeoArchaeo', Qgis_Info)
        except ImportError:
            missing_packages.append(package_name)
            QgsMessageLog.logMessage(f"{module_name} mancante", 'GeoArchaeo', Qgis_Warning)
    
    if missing_packages:
        # Messaggio all'utente
        msg = "GeoArchaeo richiede i seguenti pacchetti:\n\n"
        msg += "\n".join(missing_packages)
        msg += "\n\nVuoi installarli automaticamente?"
        
        reply = QMessageBox.question(
            None, 
            "Dipendenze Mancanti", 
            msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Trova il percorso Python di QGIS
                python_exec = sys.executable
                
                # Installa pacchetti
                for package in missing_packages:
                    QgsMessageLog.logMessage(
                        f"Installazione {package}...", 
                        'GeoArchaeo', 
                        Qgis_Info
                    )
                    
                    subprocess.check_call([
                        python_exec, "-m", "pip", "install", 
                        "--user", package
                    ])
                
                QMessageBox.information(
                    None,
                    "Installazione Completata",
                    "Dipendenze installate con successo!\n\nRiavvia QGIS per completare l'installazione."
                )
                return False
                
            except Exception as e:
                error_msg = f"Errore installazione automatica:\n{str(e)}\n\n"
                error_msg += "Installa manualmente con:\n"
                error_msg += f"{python_exec} -m pip install --user " + " ".join(missing_packages)
                
                QMessageBox.critical(
                    None,
                    "Errore Installazione",
                    error_msg
                )
                return False
        else:
            # Mostra istruzioni manuali
            cmd = f"{sys.executable} -m pip install --user " + " ".join(missing_packages)
            QMessageBox.warning(
                None,
                "Installazione Manuale",
                f"Per usare GeoArchaeo, installa le dipendenze con:\n\n{cmd}"
            )
            return False
    
    return True

def classFactory(iface):
    """Entry point per QGIS - carica il plugin"""
    # Verifica dipendenze
    if not check_and_install_dependencies():
        # Return a dummy plugin if dependencies are missing
        class DummyPlugin:
            def initGui(self):
                pass
            def unload(self):
                pass
        return DummyPlugin()
    
    from .geoarchaeo_plugin import GeoArchaeoPlugin
    return GeoArchaeoPlugin(iface)