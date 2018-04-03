# -*- coding: utf-8 -*-
"""
/***************************************************************************
Code from QgisCloudPluginDialog
                                 A QGIS plugin
 Publish maps on qgiscloud.com
                             -------------------
        begin                : 2011-04-04
        copyright            : (C) 2011 by Sourcepole
        email                : pka@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *

from modules.gui.ui_pyarchinitplugin import Ui_PyarchinitPlugin
from pyarchinitConfigDialog import pyArchInitDialog_Config
from pyarchinitInfoDialog import pyArchInitDialog_Info
from pyarchinit_Archeozoology_mainapp import pyarchinit_Archeozoology
from pyarchinit_Deteta_mainapp import pyarchinit_Deteta
from pyarchinit_Detsesso_mainapp import pyarchinit_Detsesso
from pyarchinit_Gis_Time_controller import pyarchinit_Gis_Time_Controller
from pyarchinit_Inv_Materiali_mainapp import pyarchinit_Inventario_reperti
from pyarchinit_Periodizzazione_mainapp import pyarchinit_Periodizzazione
from pyarchinit_Schedaind_mainapp import pyarchinit_Schedaind
from pyarchinit_Site_mainapp import pyarchinit_Site
from pyarchinit_Struttura_mainapp import pyarchinit_Struttura
from pyarchinit_Tafonomia_mainapp import pyarchinit_Tafonomia
from pyarchinit_US_mainapp import pyarchinit_US
from pyarchinit_UT_mainapp import pyarchinit_UT
from pyarchinit_Upd_mainapp import pyarchinit_Upd_Values
from pyarchinit_image_viewer_main import Main
from pyarchinit_images_directory_export_mainapp import pyarchinit_Images_directory_export
from pyarchinit_pdf_export_mainapp import pyarchinit_pdf_export


class PyarchinitPluginDialog(QDockWidget):
    def __init__(self, iface):
        QDockWidget.__init__(self, None)
        self.iface = iface
        ##        self.version = version
        # Set up the user interface from Designer.
        self.ui = Ui_PyarchinitPlugin()
        self.ui.setupUi(self)
        QObject.connect(self.ui.btnUStable, SIGNAL("clicked()"), self.runUS)
        QObject.connect(self.ui.btnUStable_2, SIGNAL("clicked()"), self.runUS)

        QObject.connect(self.ui.btnStrutturatable, SIGNAL("clicked()"), self.runStruttura)
        QObject.connect(self.ui.btnPeriodotable, SIGNAL("clicked()"), self.runPer)

        QObject.connect(self.ui.btnSitotable, SIGNAL("clicked()"), self.runSite)
        QObject.connect(self.ui.btnSitotable_2, SIGNAL("clicked()"), self.runSite)

        QObject.connect(self.ui.btnReptable, SIGNAL("clicked()"), self.runInr)
        QObject.connect(self.ui.btnReptable_2, SIGNAL("clicked()"), self.runInr)
        QObject.connect(self.ui.btnReptable_3, SIGNAL("clicked()"), self.runInr)

        QObject.connect(self.ui.btnMedtable, SIGNAL("clicked()"), self.runImageViewer)
        QObject.connect(self.ui.btnExptable, SIGNAL("clicked()"), self.runImages_directory_export)

        QObject.connect(self.ui.btnPDFmen, SIGNAL("clicked()"), self.runPDFadministrator)
        QObject.connect(self.ui.btnUTtable, SIGNAL("clicked()"), self.runUT)

    def runSite(self):
        pluginGui = pyarchinit_Site(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runPer(self):
        pluginGui = pyarchinit_Periodizzazione(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runStruttura(self):
        pluginGui = pyarchinit_Struttura(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runUS(self):
        pluginGui = pyarchinit_US(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runInr(self):
        pluginGui = pyarchinit_Inventario_reperti(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runGisTimeController(self):
        pluginGui = pyarchinit_Gis_Time_Controller(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runUpd(self):
        pluginGui = pyarchinit_Upd_Values(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runConf(self):
        pluginConfGui = pyArchInitDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui  # save

    def runInfo(self):
        pluginInfoGui = pyArchInitDialog_Info()
        pluginInfoGui.show()
        self.pluginGui = pluginInfoGui  # save

    def runImageViewer(self):
        pluginImageView = Main()
        pluginImageView.show()
        self.pluginGui = pluginImageView  # save

    def runImages_directory_export(self):
        pluginImage_directory_export = pyarchinit_Images_directory_export()
        pluginImage_directory_export.show()
        self.pluginGui = pluginImage_directory_export  # save

    def runTafonomia(self):
        pluginTafonomia = pyarchinit_Tafonomia(self.iface)
        pluginTafonomia.show()
        self.pluginGui = pluginTafonomia  # save

    def runSchedaind(self):
        pluginIndividui = pyarchinit_Schedaind(self.iface)
        pluginIndividui.show()
        self.pluginGui = pluginIndividui  # save

    def runDetsesso(self):
        pluginSesso = pyarchinit_Detsesso(self.iface)
        pluginSesso.show()
        self.pluginGui = pluginSesso  # save

    def runDeteta(self):
        pluginEta = pyarchinit_Deteta(self.iface)
        pluginEta.show()
        self.pluginGui = pluginEta  # save

    def runArcheozoology(self):
        pluginArchezoology = pyarchinit_Archeozoology(self.iface)
        pluginArchezoology.show()
        self.pluginGui = pluginArchezoology  # save

    def runUT(self):
        pluginUT = pyarchinit_UT(self.iface)
        pluginUT.show()
        self.pluginGui = pluginUT  # save

    def runPDFadministrator(self):
        pluginPDFadmin = pyarchinit_pdf_export()
        pluginPDFadmin.show()
        self.pluginGui = pluginPDFadmin  # save
