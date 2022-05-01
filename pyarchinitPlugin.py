#! /usr/bin/env python
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
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
import os
from builtins import object
from builtins import str
from qgis.PyQt.QtCore import Qt, QFileInfo, QTranslator, QVariant, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolButton, QMenu
from qgis.core import QgsApplication, QgsSettings
from .pyarchinitDockWidget import PyarchinitPluginDialog
from .tabs.Archeozoology import pyarchinit_Archeozoology
from .tabs.Campioni import pyarchinit_Campioni
from .tabs.Deteta import pyarchinit_Deteta
from .tabs.Detsesso import pyarchinit_Detsesso
from .tabs.Documentazione import pyarchinit_Documentazione
from .tabs.Gis_Time_controller import pyarchinit_Gis_Time_Controller
from .tabs.Image_viewer import Main
from .tabs.Images_comparison import Comparision
from .tabs.Images_directory_export import pyarchinit_Images_directory_export
from .tabs.Inv_Materiali import pyarchinit_Inventario_reperti
from .tabs.Pdf_export import pyarchinit_pdf_export
from .tabs.Excel_export import pyarchinit_excel_export
from .tabs.Periodizzazione import pyarchinit_Periodizzazione
from .tabs.Schedaind import pyarchinit_Schedaind
from .tabs.Site import pyarchinit_Site
from .tabs.Struttura import pyarchinit_Struttura
from .tabs.Tomba import pyarchinit_Tomba
from .tabs.Thesaurus import pyarchinit_Thesaurus
from .tabs.US_USM import pyarchinit_US
from .tabs.UT import pyarchinit_UT
from .tabs.PRINTMAP import pyarchinit_PRINTMAP
from .tabs.gpkg_export import pyarchinit_GPKG
from .tabs.tops_pyarchinit import pyarchinit_TOPS
from .gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from .gui.dbmanagment import pyarchinit_dbmanagment
from .gui.pyarchinitInfoDialog import pyArchInitDialog_Info
filepath = os.path.dirname(__file__)

class PyArchInitPlugin(object):
    HOME = os.environ['PYARCHINIT_HOME']
    PARAMS_DICT = {'SERVER': '',
                   'HOST': '',
                   'DATABASE': '',
                   'PASSWORD': '',
                   'PORT': '',
                   'USER': '',
                   'THUMB_PATH': '',
                   'THUMB_RESIZE': '',
                   'EXPERIMENTAL': '',
                   'SITE_SET': ''
                  }
    def __init__(self, iface):
        self.iface = iface
        userPluginPath = os.path.dirname(__file__)
        systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/pyarchinit"
        overrideLocale = QgsSettings().value("locale/overrideFlag", QVariant)  # .toBool()
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QgsSettings().value("locale/userLocale", QVariant)  # .toString()
        if QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + "/i18n/pyarchinit_plugin_" + localeFullName + ".qm"
        else:
            translationPath = systemPluginPath + "/i18n/pyarchinit_plugin_" + localeFullName + ".qm"
        self.localePath = translationPath
        if QFileInfo(self.localePath).exists():
            self.translator = QTranslator()
            self.translator.load(self.localePath)
            QCoreApplication.installTranslator(self.translator)
        
    def initGui(self):
        l=QgsSettings().value("locale/userLocale")[0:2] 
        if l == 'it':
            settings = QgsSettings()
            icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pai_us.png'))
            self.action = QAction(QIcon(icon_paius), "pyArchInit Main Panel",
                                  self.iface.mainWindow())
            self.action.triggered.connect(self.showHideDockWidget)
            # dock widget
            self.dockWidget = PyarchinitPluginDialog(self.iface)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
            # TOOLBAR
            self.toolBar = self.iface.addToolBar("pyArchInit")
            self.toolBar.setObjectName("pyArchInit")
            self.toolBar.addAction(self.action)
            self.dataToolButton = QToolButton(self.toolBar)
            self.dataToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            ######  Section dedicated to the basic data entry
            # add Actions data
            icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
            self.actionSite = QAction(QIcon(icon_site), "Siti", self.iface.mainWindow())
            self.actionSite.setWhatsThis("Siti")
            self.actionSite.triggered.connect(self.runSite)
            icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSus.png'))
            self.actionUS = QAction(QIcon((icon_US)), u"US", self.iface.mainWindow())
            self.actionUS.setWhatsThis(u"US")
            self.actionUS.triggered.connect(self.runUS)
            icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconFinds.png'))
            self.actionInr = QAction(QIcon(icon_Finds), "Reperti", self.iface.mainWindow())
            self.actionInr.setWhatsThis("Reperti")
            self.actionInr.triggered.connect(self.runInr)
            icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'champion.png'))
            self.actionCampioni = QAction(QIcon(icon_camp_exp), "Campioni", self.iface.mainWindow())
            self.actionCampioni.setWhatsThis("Campioni")
            self.actionCampioni.triggered.connect(self.runCampioni)
            #icon_Lapidei = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAlma.png'))
            # self.actionLapidei = QAction(QIcon(icon_Lapidei), "Lapidei", self.iface.mainWindow())
            # self.actionLapidei.setWhatsThis("Lapidei")
            # self.actionLapidei.triggered.connect(self.runLapidei)
            self.dataToolButton.addActions(
                [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni])
            self.dataToolButton.setDefaultAction(self.actionSite)
            self.toolBar.addWidget(self.dataToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the interpretations
            # add Actions interpretation
            self.interprToolButton = QToolButton(self.toolBar)
            self.interprToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPer.png'))
            self.actionPer = QAction(QIcon(icon_per), "Periodizzazione", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Periodizzazione")
            self.actionPer.triggered.connect(self.runPer)
            icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconStrutt.png'))
            self.actionStruttura = QAction(QIcon(icon_Struttura), "Strutture", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Strutture")
            self.actionStruttura.triggered.connect(self.runStruttura)
            self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
            self.interprToolButton.setDefaultAction(self.actionStruttura)
            self.toolBar.addWidget(self.interprToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the funerary archaeology
            # add Actions funerary archaeology
            self.funeraryToolButton = QToolButton(self.toolBar)
            self.funeraryToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconIND.png'))
            self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individui", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis("Individui")
            self.actionSchedaind.triggered.connect(self.runSchedaind)
            icon_Tomba = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconGrave.png'))
            self.actionTomba = QAction(QIcon(icon_Tomba), "Tomba", self.iface.mainWindow())
            self.actionTomba.setWhatsThis("Tomba")
            self.actionTomba.triggered.connect(self.runTomba)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSesso.png'))
                self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Determinazione Sesso", self.iface.mainWindow())
                self.actionDetsesso.setWhatsThis("Determinazione del sesso")
                self.actionDetsesso.triggered.connect(self.runDetsesso)
                icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconEta.png'))
                self.actionDeteta = QAction(QIcon(icon_Deteta), u"Determinazione dell'età", self.iface.mainWindow())
                self.actionSchedaind.setWhatsThis(u"Determinazione dell'età")
                self.actionDeteta.triggered.connect(self.runDeteta)
            self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTomba])
            self.funeraryToolButton.setDefaultAction(self.actionSchedaind)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])
            self.toolBar.addWidget(self.funeraryToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the topographical research
            #if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.topoToolButton = QToolButton(self.toolBar)
            #self.topoToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconUT.png'))
            self.actionUT = QAction(QIcon(icon_UT), u"Unità Topografiche", self.iface.mainWindow())
            self.actionUT.setWhatsThis(u"Unità Topografiche")
            self.actionUT.triggered.connect(self.runUT)
            self.topoToolButton.addActions([self.actionUT])
            self.topoToolButton.setDefaultAction(self.actionUT)
            self.toolBar.addWidget(self.topoToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the documentation
            # add Actions documentation
            self.docToolButton = QToolButton(self.toolBar)
            self.docToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'icondoc.png'))
            self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Scheda Documentazione",
                                                self.iface.mainWindow())
            self.actionDocumentazione.setWhatsThis("Documentazione")
            self.actionDocumentazione.triggered.connect(self.runDocumentazione)
            icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))            
            self.actionExcel = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
            self.actionExcel.setWhatsThis("Download EXCEL")
            self.actionExcel.triggered.connect(self.runExcel)
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Gestione immagini", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Gestione immagini")
            self.actionimageViewer.triggered.connect(self.runImageViewer)
            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Esportazione immagini",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Esportazione immagini")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)
            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Esportazione PDF", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Esportazione PDF")
            self.actionpdfExp.triggered.connect(self.runPdfexp)
            icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconTimeControll.png'))
            self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Time Manager",
                                                   self.iface.mainWindow())
            self.actionGisTimeController.setWhatsThis("Time Manager")
            self.actionGisTimeController.triggered.connect(self.runGisTimeController)
            self.docToolButton.addActions([self.actionDocumentazione,self.actionimageViewer,self.actionImages_Directory_export,self.actionpdfExp, self.actionExcel,self.actionGisTimeController])
            self.docToolButton.setDefaultAction(self.actionDocumentazione)
            self.toolBar.addWidget(self.docToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to elaborations
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.elabToolButton = QToolButton(self.toolBar)
                self.elabToolButton.setPopupMode(QToolButton.MenuButtonPopup)
                # add Actions elaboration
                icon_Archeozoology = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconMegacero.png'))
                self.actionArcheozoology = QAction(QIcon(icon_Archeozoology), "Statistiche Archeozoologiche",
                                                   self.iface.mainWindow())
                self.actionArcheozoology.setWhatsThis("Statistiche Archeozoologiche")
                self.actionArcheozoology.triggered.connect(self.runArcheozoology)
                icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'comparision.png'))
                self.actionComparision = QAction(QIcon(icon_Comparision), "Comparazione immagini", self.iface.mainWindow())
                self.actionComparision.setWhatsThis("Comparazione immagini")
                self.actionComparision.triggered.connect(self.runComparision)
                self.elabToolButton.addActions(
                    [self.actionArcheozoology, self.actionComparision, self.actionGisTimeController])
                self.elabToolButton.setDefaultAction(self.actionArcheozoology)
                self.toolBar.addWidget(self.elabToolButton)
                self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_tops = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tops.png'))
            self.actionTops = QAction(QIcon(icon_tops), "Importa dati da TOPS", self.iface.mainWindow())
            self.actionTops.setWhatsThis("Importa dati da TOPS")
            self.actionTops.triggered.connect(self.runTops)
            self.manageToolButton.addActions(
                [self.actionTops])
            self.manageToolButton.setDefaultAction(self.actionTops)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ####################################################################
            self.manageToolButton = QToolButton(self.toolBar) 
            icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
            self.actionPrint = QAction(QIcon(icon_print), "Crea la tua Mappa", self.iface.mainWindow())
            self.actionPrint.setWhatsThis("Crea la tua Mappa")
            self.actionPrint.triggered.connect(self.runPrint)
            self.manageToolButton.addActions(
                [self.actionPrint])
            self.manageToolButton.setDefaultAction(self.actionPrint)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_gpkg = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpkg.png'))
            self.actionGpkg = QAction(QIcon(icon_gpkg), "Impacchetta per geopackage", self.iface.mainWindow())
            self.actionGpkg.setWhatsThis("Impacchetta per geopackage")
            self.actionGpkg.triggered.connect(self.runGpkg)
            self.manageToolButton.addActions(
                [self.actionGpkg])
            self.manageToolButton.setDefaultAction(self.actionGpkg)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'thesaurusicon.png'))
            self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus sigle", self.iface.mainWindow())
            self.actionThesaurus.setWhatsThis("Thesaurus sigle")
            self.actionThesaurus.triggered.connect(self.runThesaurus)
            icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
            self.actionConf = QAction(QIcon(icon_Con), "Configurazione plugin", self.iface.mainWindow())
            self.actionConf.setWhatsThis("Configurazione plugin")
            self.actionConf.triggered.connect(self.runConf)
            icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "Gestione database", self.iface.mainWindow())
            self.actionDbmanagment.setWhatsThis("Gestione database")
            self.actionDbmanagment.triggered.connect(self.runDbmanagment)
            icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
            self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
            self.actionInfo.setWhatsThis("Plugin info")
            self.actionInfo.triggered.connect(self.runInfo)
            self.manageToolButton.addActions(
                [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            self.manageToolButton.setDefaultAction(self.actionConf)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            # menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            #self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)    
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            # MENU
            self.menu = QMenu("pyArchInit")
            # self.pyarchinitSite = pyarchinit_Site(self.iface)
            self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPer, self.actionStruttura])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTomba, self.actionSchedaind])
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.menu.addActions([self.actionDetsesso, self.actionDeteta])
            self.menu.addSeparator()
            #if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.menu.addActions([self.actionUT])
            self.menu.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export,self.actionExcel,self.actionGisTimeController])
            self.menu.addSeparator()
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.menu.addActions([self.actionArcheozoology, self.actionComparision])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTops])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPrint])
            self.menu.addSeparator()
            self.menu.addActions([self.actionGpkg])
            self.menu.addSeparator()
            self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)
        elif l == 'en':
            settings = QgsSettings()
            icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pai_us.png'))
            self.action = QAction(QIcon(icon_paius), "pyArchInit Main Panel",
                                  self.iface.mainWindow())
            self.action.triggered.connect(self.showHideDockWidget)
            # dock widget
            self.dockWidget = PyarchinitPluginDialog(self.iface)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
            # TOOLBAR
            self.toolBar = self.iface.addToolBar("pyArchInit")
            self.toolBar.setObjectName("pyArchInit")
            self.toolBar.addAction(self.action)
            self.dataToolButton = QToolButton(self.toolBar)
            self.dataToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            ######  Section dedicated to the basic data entry
            # add Actions data
            icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
            self.actionSite = QAction(QIcon(icon_site), "Site", self.iface.mainWindow())
            self.actionSite.setWhatsThis("Site")
            self.actionSite.triggered.connect(self.runSite)
            icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSus.png'))
            self.actionUS = QAction(QIcon((icon_US)), u"SU", self.iface.mainWindow())
            self.actionUS.setWhatsThis(u"SU")
            self.actionUS.triggered.connect(self.runUS)
            icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconFinds.png'))
            self.actionInr = QAction(QIcon(icon_Finds), "Artefact", self.iface.mainWindow())
            self.actionInr.setWhatsThis("Artefact")
            self.actionInr.triggered.connect(self.runInr)
            icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'champion.png'))
            self.actionCampioni = QAction(QIcon(icon_camp_exp), "Samples", self.iface.mainWindow())
            self.actionCampioni.setWhatsThis("Samples")
            self.actionCampioni.triggered.connect(self.runCampioni)
            # icon_Lapidei = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAlma.png'))
            # self.actionLapidei = QAction(QIcon(icon_Lapidei), "Stone", self.iface.mainWindow())
            # self.actionLapidei.setWhatsThis("Stone")
            # self.actionLapidei.triggered.connect(self.runLapidei)
            self.dataToolButton.addActions(
                [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni])
            self.dataToolButton.setDefaultAction(self.actionSite)
            self.toolBar.addWidget(self.dataToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the interpretations
            # add Actions interpretation
            self.interprToolButton = QToolButton(self.toolBar)
            self.interprToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPer.png'))
            self.actionPer = QAction(QIcon(icon_per), "Periodization", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Periodization")
            self.actionPer.triggered.connect(self.runPer)
            icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconStrutt.png'))
            self.actionStruttura = QAction(QIcon(icon_Struttura), "Structure", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Structure")
            self.actionStruttura.triggered.connect(self.runStruttura)
            self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
            self.interprToolButton.setDefaultAction(self.actionStruttura)
            self.toolBar.addWidget(self.interprToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the funerary archaeology
            # add Actions funerary archaeology
            self.funeraryToolButton = QToolButton(self.toolBar)
            self.funeraryToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconIND.png'))
            self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individual", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis("Individual")
            self.actionSchedaind.triggered.connect(self.runSchedaind)
            icon_Tomba = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconGrave.png'))
            self.actionTomba = QAction(QIcon(icon_Tomba), "Taphonomy", self.iface.mainWindow())
            self.actionTomba.setWhatsThis("Taphonomy")
            self.actionTomba.triggered.connect(self.runTomba)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSesso.png'))
                self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Sex determination", self.iface.mainWindow())
                self.actionDetsesso.setWhatsThis("Sex determination")
                self.actionDetsesso.triggered.connect(self.runDetsesso)
                icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconEta.png'))
                self.actionDeteta = QAction(QIcon(icon_Deteta), u"Age determination", self.iface.mainWindow())
                self.actionSchedaind.setWhatsThis(u"Age determination")
                self.actionDeteta.triggered.connect(self.runDeteta)
            self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTomba])
            self.funeraryToolButton.setDefaultAction(self.actionSchedaind)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])
            self.toolBar.addWidget(self.funeraryToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the topographical research
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.topoToolButton = QToolButton(self.toolBar)
                self.topoToolButton.setPopupMode(QToolButton.MenuButtonPopup)
                icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconUT.png'))
                self.actionUT = QAction(QIcon(icon_UT), u"Topographic Unit", self.iface.mainWindow())
                self.actionUT.setWhatsThis(u"Topographic Unit")
                self.actionUT.triggered.connect(self.runUT)
                self.topoToolButton.addActions([self.actionUT])
                self.topoToolButton.setDefaultAction(self.actionUT)
                self.toolBar.addWidget(self.topoToolButton)
                self.toolBar.addSeparator()
            ######  Section dedicated to the documentation
            # add Actions documentation
            self.docToolButton = QToolButton(self.toolBar)
            self.docToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'icondoc.png'))
            self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Documentation",
                                                self.iface.mainWindow())
            self.actionDocumentazione.setWhatsThis("Documentation")
            self.actionDocumentazione.triggered.connect(self.runDocumentazione)
            icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))            
            self.actionExcel = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
            self.actionExcel.setWhatsThis("Download EXCEL")
            self.actionExcel.triggered.connect(self.runExcel)    
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Media manager", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Media menager")
            self.actionimageViewer.triggered.connect(self.runImageViewer)
            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Image exportation",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Image exportation")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)
            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Pdf exportation", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Pdf exportation")
            self.actionpdfExp.triggered.connect(self.runPdfexp)
            icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconTimeControll.png'))
            self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Time Manager",
                                                   self.iface.mainWindow())
            self.actionGisTimeController.setWhatsThis("Time Manager")
            self.actionGisTimeController.triggered.connect(self.runGisTimeController)
            self.docToolButton.addActions([self.actionDocumentazione,self.actionpdfExp, self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel, self.actionGisTimeController])
            self.docToolButton.setDefaultAction(self.actionDocumentazione)
            self.toolBar.addWidget(self.docToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to elaborations
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.elabToolButton = QToolButton(self.toolBar)
                self.elabToolButton.setPopupMode(QToolButton.MenuButtonPopup)
                # add Actions elaboration
                icon_Archeozoology = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconMegacero.png'))
                self.actionArcheozoology = QAction(QIcon(icon_Archeozoology), "Archaeozoology",
                                                   self.iface.mainWindow())
                self.actionArcheozoology.setWhatsThis("Archaeozoology")
                self.actionArcheozoology.triggered.connect(self.runArcheozoology)
                icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconTimeControll.png'))
                self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Time Manager",
                                                       self.iface.mainWindow())
                self.actionGisTimeController.setWhatsThis("Time Manager")
                self.actionGisTimeController.triggered.connect(self.runGisTimeController)
                icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'comparision.png'))
                self.actionComparision = QAction(QIcon(icon_Comparision), "Image comparison", self.iface.mainWindow())
                self.actionComparision.setWhatsThis("Image comparison")
                self.actionComparision.triggered.connect(self.runComparision)
                self.elabToolButton.addActions(
                    [self.actionArcheozoology, self.actionComparision, self.actionGisTimeController])
                self.elabToolButton.setDefaultAction(self.actionArcheozoology)
                self.toolBar.addWidget(self.elabToolButton)
                self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_tops = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tops.png'))
            self.actionTops = QAction(QIcon(icon_tops), "Import data from TOPS", self.iface.mainWindow())
            self.actionTops.setWhatsThis("Import data from TOPS")
            self.actionTops.triggered.connect(self.runTops)
            self.manageToolButton.addActions(
                [self.actionTops])
            self.manageToolButton.setDefaultAction(self.actionTops)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            
            
            self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
            self.actionPrint = QAction(QIcon(icon_print), "Make your Map", self.iface.mainWindow())
            self.actionPrint.setWhatsThis("Make your Map")
            self.actionPrint.triggered.connect(self.runPrint)
            self.manageToolButton.addActions(
                [self.actionPrint])
            self.manageToolButton.setDefaultAction(self.actionPrint)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            icon_gpkg = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpkg.png'))
            self.actionGpkg = QAction(QIcon(icon_gpkg), "Import into Geopackage", self.iface.mainWindow())
            self.actionGpkg.setWhatsThis("Import into Geopackage")
            self.actionGpkg.triggered.connect(self.runGpkg)
            self.manageToolButton.addActions(
                [self.actionGpkg])
            self.manageToolButton.setDefaultAction(self.actionGpkg)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'thesaurusicon.png'))
            self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus code", self.iface.mainWindow())
            self.actionThesaurus.setWhatsThis("Thesaurus code")
            self.actionThesaurus.triggered.connect(self.runThesaurus)
            icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
            self.actionConf = QAction(QIcon(icon_Con), "Plugin settings", self.iface.mainWindow())
            self.actionConf.setWhatsThis("Plugin settings")
            self.actionConf.triggered.connect(self.runConf)
            icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "DB manager", self.iface.mainWindow())
            self.actionDbmanagment.setWhatsThis("DB manager")
            self.actionDbmanagment.triggered.connect(self.runDbmanagment)
            icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
            self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
            self.actionInfo.setWhatsThis("Plugin info")
            self.actionInfo.triggered.connect(self.runInfo)
            self.manageToolButton.addActions(
                [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            self.manageToolButton.setDefaultAction(self.actionConf)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            # menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            #self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            # MENU
            self.menu = QMenu("pyArchInit")
            # self.pyarchinitSite = pyarchinit_Site(self.iface)
            self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPer, self.actionStruttura])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTomba, self.actionSchedaind])
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.menu.addActions([self.actionDetsesso, self.actionDeteta])
            self.menu.addSeparator()
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.menu.addActions([self.actionUT])
            self.menu.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel])
            self.menu.addSeparator()
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.menu.addActions([self.actionArcheozoology, self.actionComparision, self.actionGisTimeController])
            self.menu.addSeparator() 
            self.menu.addActions([self.actionTops])
               
            self.menu.addSeparator()
            self.menu.addActions([self.actionPrint])
            self.menu.addSeparator()
            self.menu.addActions([self.actionGpkg])
            self.menu.addSeparator()
            self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)  
        elif l=='de':
            settings = QgsSettings()
            icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pai_us.png'))
            self.action = QAction(QIcon(icon_paius), "pyArchInit Main Panel",
                                  self.iface.mainWindow())
            self.action.triggered.connect(self.showHideDockWidget)
            # dock widget
            self.dockWidget = PyarchinitPluginDialog(self.iface)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
            # TOOLBAR
            self.toolBar = self.iface.addToolBar("pyArchInit")
            self.toolBar.setObjectName("pyArchInit")
            self.toolBar.addAction(self.action)
            self.dataToolButton = QToolButton(self.toolBar)
            self.dataToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            ######  Section dedicated to the basic data entry
            # add Actions data
            icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
            self.actionSite = QAction(QIcon(icon_site), "Ausgrabungsstätte", self.iface.mainWindow())
            self.actionSite.setWhatsThis("Ausgrabungsstätte")
            self.actionSite.triggered.connect(self.runSite)
            icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSus.png'))
            self.actionUS = QAction(QIcon((icon_US)), u"SE", self.iface.mainWindow())
            self.actionUS.setWhatsThis(u"SE")
            self.actionUS.triggered.connect(self.runUS)
            icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconFinds.png'))
            self.actionInr = QAction(QIcon(icon_Finds), "Artefakts", self.iface.mainWindow())
            self.actionInr.setWhatsThis("Artefakts")
            self.actionInr.triggered.connect(self.runInr)
            icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'champion.png'))
            self.actionCampioni = QAction(QIcon(icon_camp_exp), "Proben", self.iface.mainWindow())
            self.actionCampioni.setWhatsThis("Proben")
            self.actionCampioni.triggered.connect(self.runCampioni)
            # icon_Lapidei = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAlma.png'))
            # self.actionLapidei = QAction(QIcon(icon_Lapidei), "Steinartefakt", self.iface.mainWindow())
            # self.actionLapidei.setWhatsThis("Steinartefakt")
            # self.actionLapidei.triggered.connect(self.runLapidei)
            self.dataToolButton.addActions(
                [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni])
            self.dataToolButton.setDefaultAction(self.actionSite)
            self.toolBar.addWidget(self.dataToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the interpretations
            # add Actions interpretation
            self.interprToolButton = QToolButton(self.toolBar)
            self.interprToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPer.png'))
            self.actionPer = QAction(QIcon(icon_per), "Periodizierung", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Periodizierung")
            self.actionPer.triggered.connect(self.runPer)
            icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconStrutt.png'))
            self.actionStruttura = QAction(QIcon(icon_Struttura), "Strukturen", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Strukturen")
            self.actionStruttura.triggered.connect(self.runStruttura)
            self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
            self.interprToolButton.setDefaultAction(self.actionStruttura)
            self.toolBar.addWidget(self.interprToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the funerary archaeology
            # add Actions funerary archaeology
            self.funeraryToolButton = QToolButton(self.toolBar)
            self.funeraryToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconIND.png'))
            self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individuen", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis("Individuen")
            self.actionSchedaind.triggered.connect(self.runSchedaind)
            icon_Tomba = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconGrave.png'))
            self.actionTomba = QAction(QIcon(icon_Tomba), "Taphonomie", self.iface.mainWindow())
            self.actionTomba.setWhatsThis("Taphonomie")
            self.actionTomba.triggered.connect(self.runTomba)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSesso.png'))
                self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Geschlechtsbestimmung", self.iface.mainWindow())
                self.actionDetsesso.setWhatsThis("Geschlechtsbestimmung")
                self.actionDetsesso.triggered.connect(self.runDetsesso)
                icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconEta.png'))
                self.actionDeteta = QAction(QIcon(icon_Deteta), u"Altersbestimmung", self.iface.mainWindow())
                self.actionSchedaind.setWhatsThis(u"DAltersbestimmung")
                self.actionDeteta.triggered.connect(self.runDeteta)
            self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTomba])
            self.funeraryToolButton.setDefaultAction(self.actionSchedaind)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])
            self.toolBar.addWidget(self.funeraryToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the topographical research
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.topoToolButton = QToolButton(self.toolBar)
                self.topoToolButton.setPopupMode(QToolButton.MenuButtonPopup)
                icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconUT.png'))
                self.actionUT = QAction(QIcon(icon_UT), u"Topographische Einheit", self.iface.mainWindow())
                self.actionUT.setWhatsThis(u"Topographische Einheit")
                self.actionUT.triggered.connect(self.runUT)
                self.topoToolButton.addActions([self.actionUT])
                self.topoToolButton.setDefaultAction(self.actionUT)
                self.toolBar.addWidget(self.topoToolButton)
                self.toolBar.addSeparator()
            ######  Section dedicated to the documentation
            # add Actions documentation
            self.docToolButton = QToolButton(self.toolBar)
            self.docToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'icondoc.png'))
            self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Formular dokumentation",
                                                self.iface.mainWindow())
            self.actionDocumentazione.setWhatsThis("Formular dokumentation")
            self.actionDocumentazione.triggered.connect(self.runDocumentazione)
            icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))            
            self.actionExcel = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
            self.actionExcel.setWhatsThis("Download EXCEL")
            self.actionExcel.triggered.connect(self.runExcel)
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Media manager", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Media manager")
            self.actionimageViewer.triggered.connect(self.runImageViewer)
            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Exportation Bilder",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Exportation Bilder")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)
            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Exportation PDF", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Exportation PDF")
            self.actionpdfExp.triggered.connect(self.runPdfexp)
            self.docToolButton.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel])
            self.docToolButton.setDefaultAction(self.actionDocumentazione)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.actionImages_Directory_export.setCheckable(True)
                self.actionpdfExp.setCheckable(True)
                self.actionimageViewer.setCheckable(True)
            self.toolBar.addWidget(self.docToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to elaborations
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.elabToolButton = QToolButton(self.toolBar)
                self.elabToolButton.setPopupMode(QToolButton.MenuButtonPopup)
                # add Actions elaboration
                icon_Archeozoology = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconMegacero.png'))
                self.actionArcheozoology = QAction(QIcon(icon_Archeozoology), "Archeozoologische Quantifizierung",
                                                   self.iface.mainWindow())
                self.actionArcheozoology.setWhatsThis("Archeozoologische Quantifizierung")
                self.actionArcheozoology.triggered.connect(self.runArcheozoology)
                icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconTimeControll.png'))
                self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Zeitsteuerung",
                                                       self.iface.mainWindow())
                self.actionGisTimeController.setWhatsThis("Zeitsteuerung")
                self.actionGisTimeController.triggered.connect(self.runGisTimeController)
                icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'comparision.png'))
                self.actionComparision = QAction(QIcon(icon_Comparision), "Bildvergleich", self.iface.mainWindow())
                self.actionComparision.setWhatsThis("Bildvergleich")
                self.actionComparision.triggered.connect(self.runComparision)
                self.elabToolButton.addActions(
                    [self.actionArcheozoology, self.actionComparision, self.actionGisTimeController])
                self.elabToolButton.setDefaultAction(self.actionArcheozoology)
                self.toolBar.addWidget(self.elabToolButton)
                self.toolBar.addSeparator()
            
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_tops = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tops.png'))
            self.actionTops = QAction(QIcon(icon_tops), "Import data from TOPS", self.iface.mainWindow())
            self.actionTops.setWhatsThis("Import data from TOPS")
            self.actionTops.triggered.connect(self.runTops)
            self.manageToolButton.addActions(
                [self.actionTops])
            self.manageToolButton.setDefaultAction(self.actionTops)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
            self.actionPrint = QAction(QIcon(icon_print), "Make your Map", self.iface.mainWindow())
            self.actionPrint.setWhatsThis("Make your Map")
            self.actionPrint.triggered.connect(self.runPrint)
            self.manageToolButton.addActions(
                [self.actionPrint])
            self.manageToolButton.setDefaultAction(self.actionPrint)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_gpkg = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpkg.png'))
            self.actionGpkg = QAction(QIcon(icon_gpkg), "Importiert ain geopackage", self.iface.mainWindow())
            self.actionGpkg.setWhatsThis("Importiert ain geopackage")
            self.actionGpkg.triggered.connect(self.runGpkg)
            self.manageToolButton.addActions(
                [self.actionGpkg])
            self.manageToolButton.setDefaultAction(self.actionGpkg)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'thesaurusicon.png'))
            self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus", self.iface.mainWindow())
            self.actionThesaurus.setWhatsThis("Thesaurus")
            self.actionThesaurus.triggered.connect(self.runThesaurus)
            icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
            self.actionConf = QAction(QIcon(icon_Con), "Plugin settings", self.iface.mainWindow())
            self.actionConf.setWhatsThis("Plugin settings")
            self.actionConf.triggered.connect(self.runConf)
            icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "DB manager", self.iface.mainWindow())
            self.actionDbmanagment.setWhatsThis("DB manager")
            self.actionDbmanagment.triggered.connect(self.runDbmanagment)
            icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
            self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
            self.actionInfo.setWhatsThis("Plugin info")
            self.actionInfo.triggered.connect(self.runInfo)
            self.manageToolButton.addActions(
                [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            self.manageToolButton.setDefaultAction(self.actionConf)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            # menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            #self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            # MENU
            self.menu = QMenu("pyArchInit")
            # self.pyarchinitSite = pyarchinit_Site(self.iface)
            self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPer, self.actionStruttura])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTomba, self.actionSchedaind])
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.menu.addActions([self.actionDetsesso, self.actionDeteta])
            self.menu.addSeparator()
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.menu.addActions([self.actionUT])
            self.menu.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel])
            self.menu.addSeparator()
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.menu.addActions([self.actionArcheozoology, self.actionComparision, self.actionGisTimeController])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTops])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPrint])
            self.menu.addSeparator()
            self.menu.addActions([self.actionGpkg])
            self.menu.addSeparator()
            self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)
        else:
            pass
    ##
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
    def runCampioni(self):
        pluginGui = pyarchinit_Campioni(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    # def runLapidei(self):
        # pluginGui = pyarchinit_Inventario_Lapidei(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui  # save
    def runGisTimeController(self):
        pluginGui = pyarchinit_Gis_Time_Controller(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    def runTops(self):
        pluginTops = pyarchinit_TOPS(self.iface)
        pluginTops.show()
        self.pluginGui = pluginTops  # save
    def runPrint(self):
        pluginPrint = pyarchinit_PRINTMAP(self.iface)
        pluginPrint.show()
        self.pluginGui = pluginPrint  # save
    def runGpkg(self):
        pluginGpkg = pyarchinit_GPKG(self.iface)
        pluginGpkg.show()
        self.pluginGui = pluginGpkg  # save
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
    def runTomba(self):
        pluginTomba = pyarchinit_Tomba(self.iface)
        pluginTomba.show()
        self.pluginGui = pluginTomba  # save
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
    def runImages_directory_export(self):
        pluginImage_directory_export = pyarchinit_Images_directory_export()
        pluginImage_directory_export.show()
        self.pluginGui = pluginImage_directory_export  # save
    def runComparision(self):
        pluginComparision = Comparision()
        pluginComparision.show()
        self.pluginGui = pluginComparision  # save
    def runDbmanagment(self):
        pluginDbmanagment = pyarchinit_dbmanagment(self.iface)
        pluginDbmanagment.show()
        self.pluginGui = pluginDbmanagment  # save
    def runPdfexp(self):
        pluginPdfexp = pyarchinit_pdf_export(self.iface)
        pluginPdfexp.show()
        self.pluginGui = pluginPdfexp  # save
    def runThesaurus(self):
        pluginThesaurus = pyarchinit_Thesaurus(self.iface)
        pluginThesaurus.show()
        self.pluginGui = pluginThesaurus  # save
    def runDocumentazione(self):
        pluginDocumentazione = pyarchinit_Documentazione(self.iface)
        pluginDocumentazione.show()
        self.pluginGui = pluginDocumentazione  # save
    def runExcel(self):
        pluginExcel = pyarchinit_excel_export(self.iface)
        pluginExcel.show()
        self.pluginGui = pluginExcel  # save
    def unload(self):
        # Remove the plugin
        l=QgsSettings().value("locale/userLocale")[0:2] 
        if l == 'it':
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            #self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
                
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg) 
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.removeToolBarIcon(self.actionSite)
            self.iface.removeToolBarIcon(self.actionPer)
            self.iface.removeToolBarIcon(self.actionStruttura)
            self.iface.removeToolBarIcon(self.actionUS)
            self.iface.removeToolBarIcon(self.actionInr)
            self.iface.removeToolBarIcon(self.actionCampioni)
            #self.iface.removeToolBarIcon(self.actionLapidei)
            self.iface.removeToolBarIcon(self.actionTomba)
            self.iface.removeToolBarIcon(self.actionSchedaind)
            self.iface.removeToolBarIcon(self.actionDocumentazione)
            self.iface.removeToolBarIcon(self.actionExcel)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
                self.iface.removeToolBarIcon(self.actionDetsesso)
                self.iface.removeToolBarIcon(self.actionDeteta)
                self.iface.removeToolBarIcon(self.actionArcheozoology)
                
                # self.iface.removeToolBarIcon(self.actionUpd)
                self.iface.removeToolBarIcon(self.actionimageViewer)
                self.iface.removeToolBarIcon(self.actionImages_Directory_export)
                self.iface.removeToolBarIcon(self.actionpdfExp)
                self.iface.removeToolBarIcon(self.actionComparision)
                self.iface.removeToolBarIcon(self.actionGisTimeController)
            self.iface.removeToolBarIcon(self.actionUT)
            self.iface.removeToolBarIcon(self.actionTops)
            self.iface.removeToolBarIcon(self.actionPrint)
            self.iface.removeToolBarIcon(self.actionGpkg)
            self.iface.removeToolBarIcon(self.actionConf)
            self.iface.removeToolBarIcon(self.actionThesaurus)
            self.iface.removeToolBarIcon(self.actionInfo)
            self.iface.removeToolBarIcon(self.actionDbmanagment)
            self.dockWidget.setVisible(False)
            self.iface.removeDockWidget(self.dockWidget)
            # remove tool bar
            del self.toolBar
        elif l== 'en':
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            #self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.removeToolBarIcon(self.actionSite)
            self.iface.removeToolBarIcon(self.actionPer)
            self.iface.removeToolBarIcon(self.actionStruttura)
            self.iface.removeToolBarIcon(self.actionUS)
            self.iface.removeToolBarIcon(self.actionInr)
            self.iface.removeToolBarIcon(self.actionCampioni)
            #self.iface.removeToolBarIcon(self.actionLapidei)
            self.iface.removeToolBarIcon(self.actionTomba)
            self.iface.removeToolBarIcon(self.actionSchedaind)
            self.iface.removeToolBarIcon(self.actionDocumentazione)
            self.iface.removeToolBarIcon(self.actionExcel)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Yes':
                self.iface.removeToolBarIcon(self.actionDetsesso)
                self.iface.removeToolBarIcon(self.actionDeteta)
                self.iface.removeToolBarIcon(self.actionArcheozoology)
                self.iface.removeToolBarIcon(self.actionUT)
                # self.iface.removeToolBarIcon(self.actionUpd)
                self.iface.removeToolBarIcon(self.actionimageViewer)
                self.iface.removeToolBarIcon(self.actionImages_Directory_export)
                self.iface.removeToolBarIcon(self.actionpdfExp)
                self.iface.removeToolBarIcon(self.actionComparision)
                self.iface.removeToolBarIcon(self.actionGisTimeController)
            self.iface.removeToolBarIcon(self.actionTops)    
            self.iface.removeToolBarIcon(self.actionPrint)
            self.iface.removeToolBarIcon(self.actionGpkg)
            self.iface.removeToolBarIcon(self.actionConf)
            self.iface.removeToolBarIcon(self.actionThesaurus)
            self.iface.removeToolBarIcon(self.actionInfo)
            self.iface.removeToolBarIcon(self.actionDbmanagment)
            self.dockWidget.setVisible(False)
            self.iface.removeDockWidget(self.dockWidget)
            # remove tool bar
            del self.toolBar            
        elif l== 'de':
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            #self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.removeToolBarIcon(self.actionSite)
            self.iface.removeToolBarIcon(self.actionPer)
            self.iface.removeToolBarIcon(self.actionStruttura)
            self.iface.removeToolBarIcon(self.actionUS)
            self.iface.removeToolBarIcon(self.actionInr)
            self.iface.removeToolBarIcon(self.actionCampioni)
            #self.iface.removeToolBarIcon(self.actionLapidei)
            self.iface.removeToolBarIcon(self.actionTomba)
            self.iface.removeToolBarIcon(self.actionSchedaind)
            self.iface.removeToolBarIcon(self.actionDocumentazione)
            self.iface.removeToolBarIcon(self.actionExcel)
            if self.PARAMS_DICT['EXPERIMENTAL'] == 'Ja':
                self.iface.removeToolBarIcon(self.actionDetsesso)
                self.iface.removeToolBarIcon(self.actionDeteta)
                self.iface.removeToolBarIcon(self.actionArcheozoology)
                self.iface.removeToolBarIcon(self.actionUT)
                # self.iface.removeToolBarIcon(self.actionUpd)
                self.iface.removeToolBarIcon(self.actionimageViewer)
                self.iface.removeToolBarIcon(self.actionImages_Directory_export)
                self.iface.removeToolBarIcon(self.actionpdfExp)
                self.iface.removeToolBarIcon(self.actionComparision)
                self.iface.removeToolBarIcon(self.actionGisTimeController)
            self.iface.removeToolBarIcon(self.actionTops)    
            self.iface.removeToolBarIcon(self.actionPrint)
            self.iface.removeToolBarIcon(self.actionGpkg)
            self.iface.removeToolBarIcon(self.actionConf)
            self.iface.removeToolBarIcon(self.actionThesaurus)
            self.iface.removeToolBarIcon(self.actionInfo)
            self.iface.removeToolBarIcon(self.actionDbmanagment)
            self.dockWidget.setVisible(False)
            self.iface.removeDockWidget(self.dockWidget)
            # remove tool bar
            del self.toolBar        
    def showHideDockWidget(self):
        if self.dockWidget.isVisible():
            self.dockWidget.hide()
        else:
            self.dockWidget.show()