# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2007-12-01
        copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
        email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                       *
 ***************************************************************************/
"""

import subprocess
import sys

try:
    # Tenta di importare pip
    import pip
except ImportError:
    # Se l'importazione fallisce, installa pip
    subprocess.call(['python', '-m', 'ensurepip'])

        
    # Aggiorna pip all'ultima versione
    subprocess.call(['python', '-m', 'pip', 'install', '--upgrade', 'pip'])

# Da questo punto in poi, puoi assumere che pip sia installato e aggiornato

import os
from os import path
import re
import platform
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsSettings
from .modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from .modules.utility.pyarchinit_folder_installation import pyarchinit_Folder_installation
L=QgsSettings().value("locale/userLocale")[0:2]
sys.path.append(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'resources')))
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'gui', 'ui')))

pyarchinit_home = os.path.expanduser("~") + os.sep + 'pyarchinit'
fi = pyarchinit_Folder_installation()
if not os.path.exists(pyarchinit_home):
    fi.install_dir()
else:
    os.environ['PYARCHINIT_HOME'] = pyarchinit_home

confing_path = os.path.join(os.sep, pyarchinit_home, 'pyarchinit_DB_folder', 'config.cfg')
logo_iccd = os.path.join(os.sep, pyarchinit_home, 'pyarchinit_DB_folder', 'logo.jpg')
if not os.path.isfile(confing_path):
    fi.installConfigFile(os.path.dirname(confing_path))

fi.installConfigFile(os.path.dirname(logo_iccd))

missing_libraries = []
try:
    
    import pytesseract

except Exception as e:
    missing_libraries.append(str(e))

try:
    
    import graphviz

except Exception as e:
    missing_libraries.append(str(e))



try:
    import pyper
except Exception as e:
    missing_libraries.append(str(e))

try:
    import pkg_resources

    pkg_resources.require("sqlalchemy==1.4.27")

except Exception as e:
    missing_libraries.append(str(e))
try:
    import pkg_resources

    pkg_resources.require("geoalchemy2==0.9.4")
except Exception as e:
    missing_libraries.append(str(e))
try:
    import reportlab
except Exception as e:
    missing_libraries.append(str(e))

try:
    import matplotlib
except Exception as e:
    missing_libraries.append(str(e))

try:
    import sqlalchemy_utils
except Exception as e:
    missing_libraries.append(str(e))
try:
    import pysftp
except Exception as e:
    missing_libraries.append(str(e))
try:
    import xlsxwriter
except Exception as e:
    missing_libraries.append(str(e))

try:
    import cv2 
except Exception as e:
    print(e)#missing_libraries.append(str(e))
    if platform.system() == 'Windows':
        subprocess.call(['pip', 'install', 'opencv-python','--user'])

    elif platform.system() == 'Darwin':
        subprocess.call(["/Applications/QGIS.app/Contents/MacOS/bin/python3", "-m", "pip","install",'opencv-python','--user'])

try:
    import pandas
except Exception as e:
    missing_libraries.append(str(e))
try:
    

    import totalopenstation
    

except Exception as e:
    missing_libraries.append(str(e))


install_libraries = []
for l in missing_libraries:
    p = re.findall(r"'(.*?)'", l)
    install_libraries.append(p[0])

if install_libraries:
    '''legge le librerie mancanti dalla cartella ext-libs'''
    import site
    site.addsitedir(os.path.abspath(os.path.dirname(__file__) + '/ext-libs'))


    

s = QgsSettings()
if not Pyarchinit_OS_Utility.checkgraphvizinstallation() and s.value('pyArchInit/graphvizBinPath'):
    os.environ['PATH'] += os.pathsep + os.path.normpath(s.value('pyArchInit/graphvizBinPath'))
    
if not Pyarchinit_OS_Utility.checkpostgresinstallation() and s.value('pyArchInit/postgresBinPath'):
    os.environ['PATH'] += os.pathsep + os.path.normpath(s.value('pyArchInit/postgresBinPath'))    



packages = [
    'postgres',
    'graphviz',
]


for p in packages:
            
    if p.startswith('postgres'):
        try:
            subprocess.call(['pg_dump', '-V'])
        except Exception as e:
        #except Exception as e:
            #if L=='it':
            QMessageBox.warning(None, 'Pyarchinit',
                            "INFO: Sembra che postgres non sia installato sul vostro sistema o che non abbiate impostato il percorso in Pyarchinit config. ",
                            QMessageBox.Ok | QMessageBox.Cancel)

    if p.startswith('graphviz'):
        try:
            subprocess.call(['dot', '-V'])
        except Exception as e:
            if L=='it':
                QMessageBox.warning(None, 'Pyarchinit',
                                "INFO: Sembra che Graphviz non sia installato sul vostro sistema o che non abbiate impostato il percorso in Pyarchinit config. In ogni caso il modulo python di graphviz sarà installato sul vostro sistema, ma la funzionalità di esportazione del matrix dal plugin pyarchinit sarà disabilitata.",
                                QMessageBox.Ok | QMessageBox.Cancel)
            elif L=='de':
                QMessageBox.warning(None, 'Pyarchinit',
                                "INFO: Es scheint, dass Graphviz nicht auf Ihrem System installiert ist oder dass Sie den Pfad in der Pyarchinit-Konfiguration nicht festgelegt haben. Wie auch immer, das Graphviz-Python-Modul wird auf Ihrem System installiert sein, aber die Exportmatrix-Funktionalität aus dem Pyarchinit-Plugin wird deaktiviert sein.",
                                QMessageBox.Ok | QMessageBox.Cancel)
                                
            else:
                QMessageBox.warning(None, 'Pyarchinit',
                                "INFO: It seems that Graphviz is not installed on your system or you don't have set the path in Pyarchinit config. Anyway the graphviz python module will be installed on your system, but the export matrix functionality from pyarchinit plugin will be disabled.",
                                QMessageBox.Ok | QMessageBox.Cancel)
    

               


if platform.system() == "Darwin":
    location = os.path.expanduser("~/Library/Fonts")

    if not path.exists(location + '/cambria.ttc'):

        QMessageBox.warning(None, 'Pyarchinit',
                            "INFO: Il font Cambria sembra non essere installato. per installarlo clicca Ok\n e poi doppio click su cambria.*\Dopo ricarica il plugin",
                            QMessageBox.Ok)

        if QMessageBox.Ok:
            HOME = os.environ['PYARCHINIT_HOME']
            path = '{}{}{}'.format(HOME, os.sep, "bin")

            subprocess.Popen(["open", path])
def classFactory(iface):
    
                
    from .pyarchinitPlugin import PyArchInitPlugin
    return PyArchInitPlugin(iface)
