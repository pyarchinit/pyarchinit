#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2007-12-01
        copyright            : (C) 2008 by Luca Mandolesi
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

from .dbmanagment import pyarchinit_dbmanagment
from .pyarchinitConfigDialog import pyArchInitDialog_Config
from .pyarchinitInfoDialog import pyArchInitDialog_Info
from .pyarchinitplugindialog import PyarchinitPluginDialog
from .tabs.Archeozoology import pyarchinit_Archeozoology
from .tabs.Campioni import pyarchinit_Campioni
from .tabs.Deteta import pyarchinit_Deteta
from .tabs.Detsesso import pyarchinit_Detsesso
from .tabs.Documentazione import pyarchinit_Documentazione
from .tabs.Gis_Time_controller import pyarchinit_Gis_Time_Controller
from .tabs.Inv_Lapidei import pyarchinit_Inventario_Lapidei
from .tabs.Inv_Materiali import pyarchinit_Inventario_reperti
from .tabs.Periodizzazione import pyarchinit_Periodizzazione
from .tabs.Schedaind import pyarchinit_Schedaind
from .tabs.Site import pyarchinit_Site
from .tabs.Struttura import pyarchinit_Struttura
from .tabs.Tafonomia import pyarchinit_Tafonomia
from .tabs.Thesaurus import pyarchinit_Thesaurus
from .tabs.US_USM import pyarchinit_US
from .tabs.UT import pyarchinit_UT
from .tabs.Image_viewer import Main
from .tabs.Images_comparision import Comparision
from .tabs.Images_directory_export import pyarchinit_Images_directory_export
from .tabs.Pdf_export import pyarchinit_pdf_export

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
                   'EXPERIMENTAL': ''}

    path_rel = os.path.join(os.sep, str(HOME), 'pyarchinit_DB_folder', 'config.cfg')
    conf = open(path_rel, "r")
    data = conf.read()
    PARAMS_DICT = eval(data)

    # TODO: find a better way to settings config
    # if 'EXPERIMENTAL' in PARAMS_DICT:
    #     PARAMS_DICT['EXPERIMENTAL'] = 'No'
    #     f = open(path_rel, "w")
    #     f.write(str(PARAMS_DICT))
    #     f.close()

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
        settings = QgsSettings()
        icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'pai_us.png'))
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
        icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconSite.png'))
        self.actionSite = QAction(QIcon(icon_site), "Siti", self.iface.mainWindow())
        self.actionSite.setWhatsThis("Siti")
        self.actionSite.triggered.connect(self.runSite)

        icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconSus.png'))
        self.actionUS = QAction(QIcon((icon_US)), u"US", self.iface.mainWindow())
        self.actionUS.setWhatsThis(u"US")
        self.actionUS.triggered.connect(self.runUS)

        icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconFinds.png'))
        self.actionInr = QAction(QIcon(icon_Finds), "Reperti", self.iface.mainWindow())
        self.actionInr.setWhatsThis("Reperti")
        self.actionInr.triggered.connect(self.runInr)

        icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'champion.png'))
        self.actionCampioni = QAction(QIcon(icon_camp_exp), "Campioni", self.iface.mainWindow())
        self.actionCampioni.setWhatsThis("Campioni")
        self.actionCampioni.triggered.connect(self.runCampioni)

        icon_Lapidei = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconAlma.png'))
        self.actionLapidei = QAction(QIcon(icon_Lapidei), "Lapidei", self.iface.mainWindow())
        self.actionLapidei.setWhatsThis("Lapidei")
        self.actionLapidei.triggered.connect(self.runLapidei)

        self.dataToolButton.addActions(
            [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionLapidei])
        self.dataToolButton.setDefaultAction(self.actionSite)

        ##		self.actionSite.setCheckable(True)
        ##		self.actionUS.setCheckable(True)
        ##		self.actionInr.setCheckable(True)
        ##		self.actionCampioni.setCheckable(True)
        ##		self.actionLapidei.setCheckable(True)

        self.toolBar.addWidget(self.dataToolButton)

        self.toolBar.addSeparator()

        ######  Section dedicated to the interpretations
        # add Actions interpretation
        self.interprToolButton = QToolButton(self.toolBar)
        self.interprToolButton.setPopupMode(QToolButton.MenuButtonPopup)

        icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconPer.png'))
        self.actionPer = QAction(QIcon(icon_per), "Periodizzazione", self.iface.mainWindow())
        self.actionPer.setWhatsThis("Periodizzazione")
        self.actionPer.triggered.connect(self.runPer)

        icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconStrutt.png'))
        self.actionStruttura = QAction(QIcon(icon_Struttura), "Strutture", self.iface.mainWindow())
        self.actionPer.setWhatsThis("Strutture")
        self.actionStruttura.triggered.connect(self.runStruttura)

        self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
        self.interprToolButton.setDefaultAction(self.actionStruttura)

        ##		self.actionPer.setCheckable(True)
        ##		self.actionStruttura.setCheckable(True)

        self.toolBar.addWidget(self.interprToolButton)

        self.toolBar.addSeparator()

        ######  Section dedicated to the funerary archaeology
        # add Actions funerary archaeology
        self.funeraryToolButton = QToolButton(self.toolBar)
        self.funeraryToolButton.setPopupMode(QToolButton.MenuButtonPopup)

        icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconIND.png'))
        self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individui", self.iface.mainWindow())
        self.actionSchedaind.setWhatsThis("Individui")
        self.actionSchedaind.triggered.connect(self.runSchedaind)

        icon_Tafonomia = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconGrave.png'))
        self.actionTafonomia = QAction(QIcon(icon_Tafonomia), "Tafonomica/Sepolture", self.iface.mainWindow())
        self.actionTafonomia.setWhatsThis("Tafonomica/Sepolture")
        self.actionTafonomia.triggered.connect(self.runTafonomia)

        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconSesso.png'))
            self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Determinazione Sesso", self.iface.mainWindow())
            self.actionDetsesso.setWhatsThis("Determinazione del sesso")
            self.actionDetsesso.triggered.connect(self.runDetsesso)

            icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconEta.png'))
            self.actionDeteta = QAction(QIcon(icon_Deteta), u"Determinazione dell'età", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis(u"Determinazione dell'età")
            self.actionDeteta.triggered.connect(self.runDeteta)

        self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTafonomia])
        self.funeraryToolButton.setDefaultAction(self.actionSchedaind)

        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])

        ##		self.actionSchedaind.setCheckable(True)
        ##		self.actionTafonomia.setCheckable(True)

        self.toolBar.addWidget(self.funeraryToolButton)

        self.toolBar.addSeparator()

        ######  Section dedicated to the topographical research
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.topoToolButton = QToolButton(self.toolBar)
            self.topoToolButton.setPopupMode(QToolButton.MenuButtonPopup)

            icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconUT.png'))
            self.actionUT = QAction(QIcon(icon_UT), u"Unità Topografiche", self.iface.mainWindow())
            self.actionUT.setWhatsThis(u"Unità Topografiche")
            self.actionUT.triggered.connect(self.runUT)

            self.topoToolButton.addActions([self.actionUT])
            self.topoToolButton.setDefaultAction(self.actionUT)

            ##			self.actionUT.setCheckable(True)

            self.toolBar.addWidget(self.topoToolButton)

            self.toolBar.addSeparator()

        ######  Section dedicated to the documentation
        # add Actions documentation
        self.docToolButton = QToolButton(self.toolBar)
        self.docToolButton.setPopupMode(QToolButton.MenuButtonPopup)

        icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'icondoc.png'))
        self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Scheda Documentazione",
                                            self.iface.mainWindow())
        self.actionDocumentazione.setWhatsThis("Documentazione")
        self.actionDocumentazione.triggered.connect(self.runDocumentazione)

        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Gestione immagini", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Gestione immagini")
            self.actionimageViewer.triggered.connect(self.runImageViewer)

            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Esportazione immagini",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Esportazione immagini")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)

            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Esportazione PDF", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Esportazione PDF")
            self.actionpdfExp.triggered.connect(self.runPdfexp)

        self.docToolButton.addActions([self.actionDocumentazione])

        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.docToolButton.addActions(
                [self.actionpdfExp, self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export])

        self.docToolButton.setDefaultAction(self.actionDocumentazione)

        ##		self.actionDocumentazione.setCheckable(True)

        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.actionImages_Directory_export.setCheckable(True)
            self.actionpdfExp.setCheckable(True)
            self.actionimageViewer.setCheckable(True)

        self.toolBar.addWidget(self.docToolButton)

        self.toolBar.addSeparator()

        ######  Section dedicated to elaborations
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.elabToolButton = QToolButton(self.toolBar)
            self.elabToolButton.setPopupMode(QToolButton.MenuButtonPopup)

            # add Actions elaboration
            icon_Archeozoology = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconMegacero.png'))
            self.actionArcheozoology = QAction(QIcon(icon_Archeozoology), "Statistiche Archeozoologiche",
                                               self.iface.mainWindow())
            self.actionArcheozoology.setWhatsThis("Statistiche Archeozoologiche")
            self.actionArcheozoology.triggered.connect(self.runArcheozoology)

            icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconTimeControll.png'))
            self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Time Manager",
                                                   self.iface.mainWindow())
            self.actionGisTimeController.setWhatsThis("Time Manager")
            self.actionGisTimeController.triggered.connect(self.runGisTimeController)

            icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'comparision.png'))
            self.actionComparision = QAction(QIcon(icon_Comparision), "Comparazione immagini", self.iface.mainWindow())
            self.actionComparision.setWhatsThis("Comparazione immagini")
            self.actionComparision.triggered.connect(self.runComparision)

            self.elabToolButton.addActions(
                [self.actionArcheozoology, self.actionComparision, self.actionGisTimeController])
            self.elabToolButton.setDefaultAction(self.actionArcheozoology)

            ##			self.actionArcheozoology.setCheckable(True)
            ##			self.actionComparision.setCheckable(True)
            ##			self.actionGisTimeController.setCheckable(True)

            self.toolBar.addWidget(self.elabToolButton)

            self.toolBar.addSeparator()

        ######  Section dedicated to the plugin management

        self.manageToolButton = QToolButton(self.toolBar)
        self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)

        icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'thesaurusicon.png'))
        self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus sigle", self.iface.mainWindow())
        self.actionThesaurus.setWhatsThis("Thesaurus sigle")
        self.actionThesaurus.triggered.connect(self.runThesaurus)

        icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconConn.png'))
        self.actionConf = QAction(QIcon(icon_Con), "Configurazione plugin", self.iface.mainWindow())
        self.actionConf.setWhatsThis("Configurazione plugin")
        self.actionConf.triggered.connect(self.runConf)

        icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'backup.png'))
        self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "Gestione database", self.iface.mainWindow())
        self.actionDbmanagment.setWhatsThis("Gestione database")
        self.actionDbmanagment.triggered.connect(self.runDbmanagment)

        icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'ui', 'icons', 'iconInfo.png'))
        self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
        self.actionInfo.setWhatsThis("Plugin info")
        self.actionInfo.triggered.connect(self.runInfo)

        self.manageToolButton.addActions(
            [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
        self.manageToolButton.setDefaultAction(self.actionConf)

        ##			self.actionThesaurus.setCheckable(True)
        ##			self.actionConf.setCheckable(True)
        ##			self.actionDbmanagment.setCheckable(True)
        ##			self.actionInfo.setCheckable(True)

        self.toolBar.addWidget(self.manageToolButton)

        self.toolBar.addSeparator()

        # menu
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)

        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)

        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTafonomia)

        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)

        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)

        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)

            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)

        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
        self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)

        # MENU
        self.menu = QMenu("pyArchInit")
        # self.pyarchinitSite = pyarchinit_Site(self.iface)
        self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionLapidei])
        self.menu.addSeparator()
        self.menu.addActions([self.actionPer, self.actionStruttura])
        self.menu.addSeparator()
        self.menu.addActions([self.actionTafonomia, self.actionSchedaind])
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.menu.addActions([self.actionDetsesso, self.actionDeteta])
        self.menu.addSeparator()
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.menu.addActions([self.actionUT])
        self.menu.addActions([self.actionDocumentazione])
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.menu.addActions([self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export])
        self.menu.addSeparator()
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.menu.addActions([self.actionArcheozoology, self.actionComparision, self.actionGisTimeController])
        self.menu.addSeparator()
        self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.addMenu(self.menu)

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

    def runLapidei(self):
        pluginGui = pyarchinit_Inventario_Lapidei(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runGisTimeController(self):
        pluginGui = pyarchinit_Gis_Time_Controller(self.iface)
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

    def unload(self):
        # Remove the plugin
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
        self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTafonomia)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionArcheozoology)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
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
        self.iface.removeToolBarIcon(self.actionLapidei)
        self.iface.removeToolBarIcon(self.actionTafonomia)
        self.iface.removeToolBarIcon(self.actionSchedaind)
        self.iface.removeToolBarIcon(self.actionDocumentazione)
        if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
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
