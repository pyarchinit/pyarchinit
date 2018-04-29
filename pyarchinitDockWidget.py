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
from __future__ import absolute_import

import os

from qgis.PyQt.QtXml import *
from qgis.PyQt.uic import loadUiType
from qgis.gui import QgsDockWidget

from .tabs.Archeozoology import pyarchinit_Archeozoology
from .tabs.Deteta import pyarchinit_Deteta
from .tabs.Detsesso import pyarchinit_Detsesso
from .tabs.Gis_Time_controller import pyarchinit_Gis_Time_Controller
from .tabs.Image_viewer import Main
from .tabs.Images_directory_export import pyarchinit_Images_directory_export
from .tabs.Inv_Materiali import pyarchinit_Inventario_reperti
from .tabs.Pdf_export import pyarchinit_pdf_export
from .tabs.Periodizzazione import pyarchinit_Periodizzazione
from .tabs.Schedaind import pyarchinit_Schedaind
from .tabs.Site import pyarchinit_Site
from .tabs.Struttura import pyarchinit_Struttura
from .tabs.Tafonomia import pyarchinit_Tafonomia
from .tabs.US_USM import pyarchinit_US
from .tabs.UT import pyarchinit_UT
from .tabs.Upd import pyarchinit_Upd_Values
from .gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from .gui.pyarchinitInfoDialog import pyArchInitDialog_Info

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'gui', 'ui', 'pyarchinit_plugin.ui')))


class PyarchinitPluginDialog(QgsDockWidget, MAIN_DIALOG_CLASS):
    def __init__(self, iface):
        super(PyarchinitPluginDialog, self).__init__()
        self.setupUi(self)

        self.iface = iface
        self.btnUStable.clicked.connect(self.runUS)
        self.btnUStable_2.clicked.connect(self.runUS)

        self.btnStrutturatable.clicked.connect(self.runStruttura)
        self.btnPeriodotable.clicked.connect(self.runPer)

        self.btnSitotable.clicked.connect(self.runSite)
        self.btnSitotable_2.clicked.connect(self.runSite)

        self.btnReptable.clicked.connect(self.runInr)
        self.btnReptable_2.clicked.connect(self.runInr)
        self.btnReptable_3.clicked.connect(self.runInr)

        self.btnMedtable.clicked.connect(self.runImageViewer)
        self.btnExptable.clicked.connect(self.runImages_directory_export)

        self.btnPDFmen.clicked.connect(self.runPDFadministrator)
        self.btnUTtable.clicked.connect(self.runUT)

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
        pluginPDFadmin = pyarchinit_pdf_export(self.iface)
        pluginPDFadmin.show()
        self.pluginGui = pluginPDFadmin  # save
