#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""
from __future__ import absolute_import

import os
from datetime import date
import requests
import urllib
from builtins import range
from builtins import str
#from pyper import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
#from qgis.gui import QgsMapLayerComboBox
from distutils.dir_util import copy_tree
from processing.tools.system import mkdir, userFolder
import processing
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.print_relazione_pdf import exp_rel_pdf
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.Utils import *
from ..test_area import Test_area
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from .PlaceSelectionDialog import PlaceSelectionDialog
from .networkaccessmanager import NetworkAccessManager
import sys,  json

NAM = NetworkAccessManager()
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Site.ui'))


class pyarchinit_Site(QDialog, MAIN_DIALOG_CLASS):
    """This class provides to manage the Site Sheet"""

    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Sito"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Site form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Formular Ausgrabungsstätte"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    
    if L=='de':
        STATUS_ITEMS = {"b": "Aktuell ", "f": "Finden", "n": "Neuer Rekord"}
    
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    if L=='de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'site_table'
    MAPPER_TABLE_CLASS = "SITE"
    NOME_SCHEDA = "Scheda di Sito"
    ID_TABLE = "id_sito"
    SITO = pyArchInitDialog_Config
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Nazione": "nazione",
            "Regione": "regione",
            "Descrizione": "descrizione",
            "Comune": "comune",
            "Provincia": "provincia",
            "Definizione sito": "definizione_sito",
            "Directory Sito": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Descrizione",
            "Nazione",
            "Regione",
            "Comune",
            "Provincia",
            "Definizione sito",
            "Directory Sito"
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Nation": "nazione",
            "Region": "regione",
            "Beschreibung": "descrizione",
            "Ort / Stadt": "comune",
            "Landkreis": "provincia",
            "Definition Ausgrabungsstätte": "definizione_sito",
            "Folder path": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Nation",
            "Region",
            "Beschreibung",
            "Ort / Stadt",
            "Landkreis",
            "Definition Ausgrabungsstätte",
            "Folder path"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Nation": "nazione",
            "Region": "regione",
            "Description": "descrizione",
            "Town": "comune",
            "Provincie": "provincia",
            "Definition site ": "definizione_sito",
            "Directory": "sito_path"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Nation",
            "Region",
            "Description",
            "Town",
            "Provincie",
            "Definition site ",
            "Directory"
        ]   
    TABLE_FIELDS = [
        "sito",
        "nazione",
        "regione",
        "comune",
        "descrizione",
        "provincia",
        "definizione_sito",
        "sito_path"
    ]

    LANG = {
        "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN_US": ['en_US','EN_US'],
        "DE": ['de_DE','de','DE', 'DE_DE'],
        "FR": ['fr_FR','fr','FR', 'FR_FR'],
        "ES": ['es_ES','es','ES', 'ES_ES'],
        "PT": ['pt_PT','pt','PT', 'PT_PT'],
        "SV": ['sv_SV','sv','SV', 'SV_SV'],
        "RU": ['ru_RU','ru','RU', 'RU_RU'],
        "RO": ['ro_RO','ro','RO', 'RO_RO'],
        "AR": ['ar_AR','ar','AR', 'AR_AR'],
        "PT_BR": ['pt_BR','PT_BR'],
        "SL": ['sl_SL','sl','SL', 'SL_SL'],
    }

    DB_SERVER = "not defined"  ####nuovo sistema sort
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.mDockWidget.setHidden(True)
        
        self.canvas = iface.mapCanvas()
        self.layerid = ''
        #self.layer = None
        self.currentLayerId = None
        self.HOME = os.environ['PYARCHINIT_HOME']
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)

        self.pbnOpenSiteDirectory.clicked.connect(self.openSiteDir)
        self.pbn_browse_folder.clicked.connect(self.setPathToSites)
        self.set_sito()
        self.msg_sito()
        self.config = QgsSettings()
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        
    def on_pushButton_movecost_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:movecost')
        
    def on_pushButton_movecost_p_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:movecostbypolygon')
        
    def on_pushButton_movebound_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:movebound')
    
    def on_pushButton_movebound_p_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:moveboundbypolygon')
    
    def on_pushButton_movecorr_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:movecorr')
    
    def on_pushButton_movecorr_p_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:movecorrbypolygon')
    
    def on_pushButton_movealloc_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:movealloc')
    
    def on_pushButton_movealloc_p_pressed(self):#####modifiche apportate per il calcolo statistico con R
        processing.execAlgorithmDialog('r:moveallocbypolygon')
    
    def defaultScriptsFolder():
        folder = str(os.path.join(userFolder(), "rscripts"))
        mkdir(folder)
        return os.path.abspath(folder)
    
    def on_pushButton_add_script_pressed(self):# Paths to source files and qgis profile directory
        source_profile = os.path.join(self.HOME,'bin', 'rscripts')
        profile_home = QgsApplication.qgisSettingsDirPath()
        rs=os.path.join(profile_home,'processing','rscripts')

        # The acutal "copy" with or without overwrite (update)
        ##if button_pressed == QMessageBox.Yes:
        copy_tree(source_profile,rs)
    
    def setPathToSites(self):
        s = QgsSettings()
        self.siti_path = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )

        if self.siti_path:
            self.lineEdit_sito_path.setText(self.siti_path)

    def openSiteDir(self):
        s = QgsSettings()
        dir = self.lineEdit_sito_path.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    def on_wms_vincoli_pressed(self):
        groupName="Vincoli Archelogici"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        myGroup5 = group.insertGroup(5, "Vincoli")
        nome_vestizione='Vincoli puntuali'
        url_vestizione ='http://vincoliinrete.beniculturali.it/geoserver/wms_public/ows?layers=v_layer_anagrafica_beniculturali:comune&CQL_FILTER=comune=%27{}%27'.format(self.comboBox_comune.currentText())
        uri_vestizione ='IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&contextualWMSLegend=0&crs=EPSG:6875&dpiMode=7&featureCount=10&format=image/png&layers=v_geo_anagrafica_beni_puntuali&styles&url='+requests.utils.quote(url_vestizione)
        rlayer3= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
        myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer3))
        
        
        nome_vestizione='Vincoli Lineari'
        url_vestizione ='http://vincoliinrete.beniculturali.it/geoserver/wms_public/ows?layers=v_layer_anagrafica_beniculturali:comune&CQL_FILTER=comune=%27{}%27'.format(self.comboBox_comune.currentText())
        uri_vestizione ='IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&contextualWMSLegend=0&crs=EPSG:6875&dpiMode=7&featureCount=10&format=image/png&layers=v_geo_anagrafica_beni_lineari&styles&url='+requests.utils.quote(url_vestizione)
        rlayer4= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
        myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer4))
        
        nome_vestizione='Vincoli poligonali'
        url_vestizione ='http://vincoliinrete.beniculturali.it/geoserver/wms_public/ows?layers=v_layer_anagrafica_beniculturali:comune&CQL_FILTER=comune=%27{}%27'.format(self.comboBox_comune.currentText())
        uri_vestizione ='IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&contextualWMSLegend=0&crs=EPSG:6875&dpiMode=7&featureCount=10&format=image/png&layers=v_geo_anagrafica_beni_poligonali&styles&url='+requests.utils.quote(url_vestizione)
        rlayer5= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
        myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer5))
        QgsProject.instance().addMapLayers([rlayer3,rlayer4,rlayer5],False)
    def internet_on(self):
        try:
            urllib.request.urlopen('https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities', timeout=0.5)
            return True
        except urllib.error.URLError:
            
            return False
    def on_basemap_pressed(self):
        if self.internet_on():
            groupName="BaseMap"
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup(groupName)
            group.setExpanded(False)

            if self.L=='it':
                myGroup7 = group.insertGroup(4, "Toponomastica")
                nome_igm_t = ' Toponomastica IGM 25000'
                url_igm_t = "http://wms.pcn.minambiente.it/ogc?map=/ms_ogc/wfs/Toponimi_2011.map&version=1.1.0&service=wfs&request=getFeature&typename=NG.TOPONIMI.&Filter=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3Ecomune%3C/PropertyName%3E%3CLiteral%3E{}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E".format(
                    self.comboBox_comune.currentText().upper())

                rlayer11 = QgsVectorLayer(url_igm_t, nome_igm_t, 'wfs')
                myGroup7.insertChildNode(-1, QgsLayerTreeLayer(rlayer11))

                myGroup4 = group.insertGroup(6, "Catasto")
                
                nome_vestizione='Vestizione'
                url_vestizione ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_vestizione ='contextualWMSLegend=0&crs=EPSG:25832&dpiMode=7&featureCount=10&format=image/png&layers=vestizioni&styles&url=https://'+requests.utils.quote(url_vestizione)
                rlayer3= QgsRasterLayer(uri_vestizione, nome_vestizione,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer3))
                
                nome_fabbricati='Fabbricati'
                url_fabbricati ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_fabbricati ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=fabbricati&styles&url=https://'+requests.utils.quote(url_vestizione)
                rlayer4= QgsRasterLayer(uri_fabbricati, nome_fabbricati,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer4))
                
                nome_Particelle='Particelle'
                url_Particelle ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Particelle ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=CP.CadastralParcel&styles&url=https://'+requests.utils.quote(url_Particelle)
                rlayer5= QgsRasterLayer(uri_Particelle, nome_Particelle,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer5))
                
                nome_Strade='Strade'
                url_Strade ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Strade ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=strade&styles&url=https://'+requests.utils.quote(url_Strade)
                rlayer6= QgsRasterLayer(uri_Strade, nome_Strade,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer6))
                
                nome_Acque='Acque'
                url_Acque ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Acque ='contextualWMSLegend=0&crs=EPSG:4258&dpiMode=7&featureCount=10&format=image/png&layers=acque&styles&url=https://'+requests.utils.quote(url_Acque)
                rlayer7= QgsRasterLayer(uri_Acque, nome_Acque,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer7))
                
                nome_Mappe='Mappe'
                url_Mappe ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Mappe ='crs=EPSG:4326&dpiMode=7&format=image/png&layers=CP.CadastralZoning&styles&url=https://'+requests.utils.quote(url_Mappe)
                rlayer8= QgsRasterLayer(uri_Mappe, nome_Mappe,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer8))
                
                nome_Province='Province'
                url_Province ='wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php'
                uri_Province ='crs=EPSG:4258&dpiMode=7&format=image/png&layers=province&styles&url=https://'+requests.utils.quote(url_Province)
                rlayer9= QgsRasterLayer(uri_Province, nome_Province,'wms')
                myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer9))
                
                myGroup6 = group.insertGroup(7, "IGM 2500")
                nome_igm='IGM 25000'
                url_igm ='wms.pcn.minambiente.it/ogc?map=/ms_ogc/WMS_v1.3/raster/IGM_25000.map'
                uri_igm ='crs=EPSG:4806&dpiMode=7&featureCount=10&format=image/png&layers=CB.IGM25000.32&layers=CB.IGM25000.33&styles&styles&url=http://'+requests.utils.quote(url_igm)
                rlayer10= QgsRasterLayer(uri_igm, nome_igm,'wms')
                myGroup6.insertChildNode(-1, QgsLayerTreeLayer(rlayer10))


            
            else:
                pass
            myGroup5 = group.insertGroup(5, "BaseMap")
            basemap_name = 'Google Maps'
            basemap_wiki = 'Wikimedia Maps'
            basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
            basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
            basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
            basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
            
            rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
            rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
            
            
            if rlayer.isValid() and rlayer_wiki.isValid():
                myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                myGroup5.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                if self.L=='it':
                    QgsProject.instance().addMapLayers([rlayer11,rlayer_wiki,rlayer,rlayer3,rlayer4,rlayer5,rlayer6,rlayer7,rlayer8,rlayer9,rlayer10],False)
                else:
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
        else:
            QMessageBox.warning(self, "Pyarchinit", "Internet Assente o Lento\n Non verranno caricate le Base Map", QMessageBox.Ok)
    
    def enable_button(self, n):
        """This method Unable or Enable the GUI buttons on browse modality"""

        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_new_search.setEnabled(n)

        self.pushButton_search_go.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

    def enable_button_search(self, n):
        """This method Unable or Enable the GUI buttons on searching modality"""

        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_save.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

    def on_pushButton_connect_pressed(self):
        """This method establishes a connection between GUI and database"""

        conn = Connection()

        conn_str = conn.conn_str()

        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Munsterformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok) 
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                elif self.L=='de':
                    msg = "Verbindungsfehler {}. " \
                          " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))        
            else:
                if self.L=='it':
                    msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
                elif self.L=='de':
                    msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)  
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)    

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)
        if self.L=='it':
            regioni_list = ['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna', 'Friuli Venezia Giulia',
                            'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise', 'Piemonte', 'Puglia', 'Sardegna',
                            'Sicilia', 'Toscana', 'Trentino Alto Adige', 'Umbria', 'Valle d\'Aosta', 'Veneto']
            self.comboBox_regione.clear()
            self.comboBox_regione.addItems(regioni_list)

            province_list = ['Agrigento', 'Alessandria', 'Ancona', 'Aosta', 'Arezzo', 'Ascoli Piceno', 'Asti', 'Avellino',
                             'Bari', 'Barletta-Andria-Trani',  'Belluno', 'Benevento', 'Bergamo', 'Biella',
                             'Bologna', 'Bolzano', 'Brescia', 'Brindisi', 'Cagliari',  'Caltanissetta',
                             'Campobasso', 'Carbonia-Iglesias', 'Caserta', 'Catania', 'Catanzaro', 'Chieti',
                             'Como', 'Cosenza', 'Cremona', 'Crotone', 'Cuneo',  'Enna', 'Fermo', 'Ferrara',
                             'Firenze', 'Foggia', "Forlì-Cesena", 'Frosinone', 'Genova', 'Gorizia', 'Grosseto', 'Imperia',
                             'Isernia', "L'Aquila", 'La Spezia', 'Latina', 'Lecce', 'Lecco', 'Livorno', 'Lodi', 'Lucca',
                             'Macerata', 'Mantova', 'Massa e Carrara', 'Matera', 'Medio Campidano', 'Messina', 'Milano',
                             'Modena', 'Monza e Brianza', 'Napoli', 'Novara', 'Nuoro', 'Ogliastra', 'Olbia-Tempio',
                             'Oristano', 'Padova', 'Palermo', 'Parma', 'Pavia', 'Perugia', 'Pesaro e Urbino', 'Pescara',
                             'Piacenza', 'Pisa', 'Pistoia', 'Pordenone', 'Potenza', 'Prato', 'Ragusa', 'Ravenna',
                             'Reggio Calabria', 'Reggio Emilia', 'Rieti', 'Rimini', 'Roma', 'Rovigo', 'Salerno', 'Sassari',
                             'Savona', 'Siena', 'Siracusa', 'Sondrio', 'Taranto', 'Teramo', 'Terni', 'Torino', 'Trapani',
                             'Trento', 'Treviso', 'Trieste', 'Udine', 'Varese', 'Venezia', 'Verbano-Cusio-Ossola',
                             'Vercelli', 'Verona', 'Vibo Valentia', 'Vicenza', 'Viterbo']
            self.comboBox_provincia.clear()
            self.comboBox_provincia.addItems(province_list)
        else:
            regioni_list = []
            self.comboBox_regione.clear()
            self.comboBox_regione.addItems(regioni_list)

            province_list = []
            self.comboBox_provincia.clear()
            self.comboBox_provincia.addItems(province_list)
        l = QgsSettings().value("locale/userLocale", QVariant)
        lang=""
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lang = str(key)
        lang = "'"+lang+"'"

        # lista definizione_sito
        search_dict = {
            'lingua': lang,
            'nome_tabella': "'" + 'site_table' + "'",
            'tipologia_sigla': "'" + '1.1' + "'"
        }
        self.comboBox_definizione_sito.clear()
        d_sito = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')

        d_sito_vl = []

        for i in range(len(d_sito)):
            d_sito_vl.append(d_sito[i].sigla_estesa)

        d_sito_vl.sort()
        self.comboBox_definizione_sito.addItems(d_sito_vl)

        # buttons functions

    def on_pushButton_pdf_pressed(self):
        pass

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))

            self.DATA_LIST = []

            temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                        self.MAPPER_TABLE_CLASS, self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR

            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def on_pushButton_new_rec_pressed(self):
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if self.DATA_LIST:
                        if self.records_equal_check() == 1:
                            if self.L=='it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                                                   "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                            elif self.L=='de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                                   QMessageBox.Ok | QMessageBox.Cancel))
                                                                   
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "The record has been changed. Do you want to save the changes?",
                                                                   QMessageBox.Ok | QMessageBox.Cancel))
                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEditable(["self.comboBox_sito"], 1)
            self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
            self.setComboBoxEditable(["self.comboBox_definizione_sito"], 1)

            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L=='it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                    elif self.L=='de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                                                    
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "The record has been changed. Do you want to save the changes?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)  
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.set_sito()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()
        if self.L=='it':

            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
                test = 1
        elif self.L=='de':  
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", " Feld Ausgrabungstätte. \n Das Feld darf nicht leer sein", QMessageBox.Ok)
                test = 1    
                
        else:   
            if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Site Field. \n The field must not be empty", QMessageBox.Ok)
                test = 1        
        return test

    def insert_new_rec(self):
        try:
            data = self.DB_MANAGER.insert_site_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.comboBox_nazione.currentText()),  # 2 - nazione
                str(self.comboBox_regione.currentText()),  # 3 - regione
                str(self.comboBox_comune.currentText()),  # 4 - comune
                str(self.textEdit_descrizione_site.toPlainText()),  # 5 - descrizione
                str(self.comboBox_provincia.currentText()),  # 6 - comune
                str(self.comboBox_definizione_sito.currentText()),  # 7 - definizione sito
                str(self.lineEdit_sito_path.text()), # 8 - path
                0  # 9 - find check
            )

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    
                    if self.L=='it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)  
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)  
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L=='it':
                self.update_if(
                
                    QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            elif self.L=='de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            # self.charge_records()
            return 0  # non ci sono errori di immissione

            # records surf functions

    def on_pushButton_view_all_pressed(self):

        if self.check_record_state() == 1:
            pass
        else:
            self.empty_fields()
            self.charge_records()
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            # records surf functions

    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.Ok)        
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.Ok)  
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def on_pushButton_delete_pressed(self):
        
        
        if self.L=='it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio!!!", "Tipo di errore: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "Il database è vuoto!", QMessageBox.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
                    # check if DB is empty
                if bool(self.DATA_LIST):
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
        elif self.L=='de':
            msg = QMessageBox.warning(self, "Achtung!!!",
                                      "Willst du wirklich diesen Eintrag löschen? \n Der Vorgang ist unumkehrbar",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Achtung", "Die Datenbank ist leer!", QMessageBox.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
                    # check if DB is empty
                if bool(self.DATA_LIST):
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
        else:
            msg = QMessageBox.warning(self, "Warning!!!",
                                      "Do you really want to break the record? \n Action is irreversible.",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
                    # check if DB is empty
                if bool(self.DATA_LIST):
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()  
                    self.set_sito()
            
            
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                ###
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
                self.setComboBoxEnable(["self.textEdit_descrizione_site"], "False")
                ###
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()

    def msg_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
            
            if self.L=='it':
                QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.Ok) 
        
            elif self.L=='de':
                QMessageBox.information(self, "OK", "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),QMessageBox.Ok) 
                
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),QMessageBox.Ok)     
        
        elif sito_set_str=='':    
            if self.L=='it':
                msg = QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",QMessageBox.Ok | QMessageBox.Cancel) 
            elif self.L=='de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",QMessageBox.Ok | QMessageBox.Cancel) 
            else:
                msg = QMessageBox.information(self, "Warning" , "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",QMessageBox.Ok | QMessageBox.Cancel) 
            if msg == QMessageBox.Cancel:
                pass
            else: 
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec_()
    def set_sito(self):
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        try:
            if bool (sito_set_str):
                search_dict = {
                    'sito': "'" + str(sito_set_str) + "'"}  # 1 - Sito
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass#
        except:
            if self.L=='it':
            
                QMessageBox.information(self, "Attenzione" ,"Non esiste questo sito: "'"'+ str(sito_set_str) +'"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",QMessageBox.Ok) 
            elif self.L=='de':
            
                QMessageBox.information(self, "Warnung" , "Es gibt keine solche archäologische Stätte: "'""'+ str(sito_set_str) +'"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",QMessageBox.Ok) 
            else:
            
                QMessageBox.information(self, "Warning" , "There is no such site: "'"'+ str(sito_set_str) +'"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",QMessageBox.Ok)   
    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L=='it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.Ok)  
        else:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                'nazione': "'" + str(self.comboBox_nazione.currentText()) + "'",  # 2 - Nazione
                'regione': "'" + str(self.comboBox_regione.currentText()) + "'",  # 3 - Regione
                'comune': "'" + str(self.comboBox_comune.currentText()) + "'",  # 4 - Comune
                'descrizione': str(self.textEdit_descrizione_site.toPlainText()),  # 5 - Descrizione
                'provincia': "'" + str(self.comboBox_provincia.currentText()) + "'",  # 6 - Provincia
                'definizione_sito': "'" + str(self.comboBox_definizione_sito.currentText()) + "'" # 7- definizione_sito
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)      
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING," "No record found!", QMessageBox.Ok) 

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_site"], "True")
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)

                    ##                  if self.DB_SERVER == 'sqlite':
                    ##                      for i in self.DATA_LIST:
                    ##                          self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, self.ID_TABLE, [i.id_sito], ['find_check'], [1])

                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                        if self.toolButton_draw_siti.isChecked():
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            #self.pyQGIS.charge_sites_from_research(sing_layer)
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                            #self.pyQGIS.charge_sites_from_research(self.DATA_LIST)
                    
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                        if self.toolButton_draw_siti.isChecked():
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            #self.pyQGIS.charge_sites_from_research(sing_layer)
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                            #self.pyQGIS.charge_sites_from_research(self.DATA_LIST)
                            
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                        if self.toolButton_draw_siti.isChecked():
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            #self.pyQGIS.charge_sites_from_research(sing_layer)
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")
                            #self.pyQGIS.charge_sites_from_research(self.DATA_LIST)      
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_definizione_sito"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_site"], "True")

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

    def on_pushButton_test_pressed(self):

        data = "Sito: " + str(self.comboBox_sito.currentText())

        ##      data = [
        ##      unicode(self.comboBox_sito.currentText()),                              #1 - Sito
        ##      unicode(self.comboBox_nazione.currentText()),                       #2 - Nazione
        ##      unicode(self.comboBox_regione.currentText()),                       #3 - Regione
        ##      unicode(self.comboBox_comune.currentText()),                        #4 - Comune
        ##      unicode(self.textEdit_descrizione_site.toPlainText()),                  #5 - Descrizione
        ##      unicode(self.comboBox_provincia.currentText())]                         #6 - Provincia

        test = Test_area(data)
        test.run_test()

    def on_pushButton_draw_pressed(self):
        self.pyQGIS.charge_layers_for_draw(["19", "12", "10", "7","8","13","16", "3","1", "2", "4", "5", "9","24","26"])

    def on_pushButton_sites_geometry_pressed(self):
        sito = str(self.comboBox_sito.currentText())
        self.pyQGIS.charge_sites_geometry([ "13", "3", "1", "2", "4","24"],
                                          "sito", sito)

    def on_pushButton_draw_sito_pressed(self):
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_sites_from_research(sing_layer)

    def on_pushButton_rel_pdf_pressed(self):
        check = QMessageBox.warning(self, "Attention",
                                    "Under testing: this method can contains some bugs. Do you want proceed?",
                                    QMessageBox.Ok | QMessageBox.Cancel)
        if check == QMessageBox.Ok:
            erp = exp_rel_pdf(str(self.comboBox_sito.currentText()))
            erp.export_rel_pdf()

    def on_toolButton_draw_siti_toggled(self):
        if self.L=='it':
            if self.toolButton_draw_siti.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                    QMessageBox.Ok)
        elif self.L=='de':
            if self.toolButton_draw_siti.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS aktiv. Von jetzt wird Deine Untersuchung mit Gis visualisiert",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Modalität' GIS deaktiviert. Von jetzt an wird deine Untersuchung nicht mehr mit Gis visualisiert",
                                    QMessageBox.Ok)
                                    
        else:
            if self.toolButton_draw_siti.isChecked():
                QMessageBox.warning(self, "Message",
                                    "GIS mode active. From now on your searches will be displayed on the GIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "GIS mode disabled. From now on, your searches will no longer be displayed on the GIS.",
                                    QMessageBox.Ok)
    def on_pushButton_genera_us_pressed(self):
        self.DB_MANAGER.insert_arbitrary_number_of_us_records(int(self.lineEdit_us_range.text()),
                                                              str(self.comboBox_sito.currentText()),
                                                              int(self.lineEdit_area.text()),
                                                              int(self.lineEdit_n_us.text()),
                                                              str(self.comboBox_t_us.currentText()))

        if self.L=='it':
            QMessageBox.warning(self, "Messaggio",
                                    "US create con successo nella Scheda US", QMessageBox.Ok)

        elif self.L=='de':
            QMessageBox.warning(self, "Message",
                                    "TO TRANSLATE: US create con successo nella Scheda US",
                                    QMessageBox.Ok)


        else:
            QMessageBox.warning(self, "Message",
                                    "SU successfully created on SU Sheet",
                                    QMessageBox.Ok)


    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i." + self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS,
                                                                self.ID_TABLE)  # self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                if type(self.REC_CORR) == "<type 'str'>":
                    corr = 0
                else:
                    corr = self.REC_CORR
                return 1
            elif test == 0:
                return 0

                # custom functions

    def charge_records(self):
        self.DATA_LIST = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_list.append(eval("i." + self.ID_TABLE))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if bool(value):
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista

    def empty_fields(self):
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_nazione.setEditText("")  # 2 - Nazione
        self.comboBox_regione.setEditText("")  # 3 - Regione
        self.comboBox_comune.setEditText("")  # 4 - Comune
        self.textEdit_descrizione_site.clear()  # 5 - Descrizione
        self.comboBox_provincia.setEditText("")  # 6 - Provincia
        self.comboBox_definizione_sito.setEditText("")  # 7 - definizione_sito
        self.lineEdit_sito_path.setText("") # 8 - path

    def fill_fields(self, n=0):
        self.rec_num = n

        str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
        str(self.comboBox_nazione.setEditText(self.DATA_LIST[self.rec_num].nazione))  # 2 - Nazione
        str(self.comboBox_regione.setEditText(self.DATA_LIST[self.rec_num].regione))  # 3 - Regione
        str(self.comboBox_comune.setEditText(self.DATA_LIST[self.rec_num].comune))  # 4 - Comune
        str(self.textEdit_descrizione_site.setText(self.DATA_LIST[self.rec_num].descrizione))  # 5 - Descrizione
        str(self.comboBox_provincia.setEditText(self.DATA_LIST[self.rec_num].provincia))  # 6 - Provincia
        str(self.comboBox_definizione_sito.setEditText(
            self.DATA_LIST[self.rec_num].definizione_sito))  # 7 - definizione_sito
        str(self.lineEdit_sito_path.setText(self.DATA_LIST[self.rec_num].sito_path)) # 8 - path

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # data
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_nazione.currentText()),  # 2 - Nazione
            str(self.comboBox_regione.currentText()),  # 3 - Regione
            str(self.comboBox_comune.currentText()),  # 4 - Comune
            str(self.textEdit_descrizione_site.toPlainText()),  # 5 - Descrizione
            str(self.comboBox_provincia.currentText()),  # 6 - Provincia
            str(self.comboBox_definizione_sito.currentText()), # 7 - Definizione sito
            str(self.lineEdit_sito_path.text()) # 8 - path
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)

    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
            eval(cmd)

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            str(e)
            save_file='{}{}{}'.format(self.HOME, os.sep,"pyarchinit_Report_folder") 
            file_=os.path.join(save_file,'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio",
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report _Folder", QMessageBox.Ok)
            
            
            elif self.L=='de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report _Folder", QMessageBox.Ok) 
            else:
                QMessageBox.warning(self, "Message",
                                    "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report _Ordner abrufen können", QMessageBox.Ok)                                               
            return 0

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()
    def get_config(self,  key, default=''):
        # return a config parameter
        return self.config.value('PythonPlugins/pyarchinit/' + key, default )


    def set_config(self,  key,  value):
        # set a config parameter
        return self.config.setValue('PythonPlugins/pyarchinit/' + key, value)

    def reverse(self):
        # Reverse geocoding
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "pyarchinit geocoding plugin error"), chk)
            return
        sb = self.iface.mainWindow().statusBar()
        sb.showMessage(QCoreApplication.translate('pyarchinit geocoding', "Click on the map to obtain the address"))
        ct = ClickTool(self.iface,  self.reverse_action);
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(ct)


   # change settings
    def reverse_action(self, point):

        
        geocoder = self.get_geocoder_instance()

        try:
            # reverse lat/lon
            self.logMessage('Reverse clicked point ' + str(point[0]) + ' ' + str(point[1]))
            pt = pointToWGS84(point, self._get_canvas_crs())
            self.logMessage('Reverse transformed point ' + str(pt[0]) + ' ' + str(pt[1]))
            address = geocoder.reverse(pt[0],pt[1])
            self.logMessage(str(address))
            if len(address) == 0:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "Reverse pyarchinit geocoding error"), unicode(QCoreApplication.translate('pyarchinit geocoding', "<strong>Empty result</strong>.<br>")))
            else:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse pyarchinit geocoding"),  unicode(QCoreApplication.translate('v', "Reverse geocoding found the following address:<br><strong>%s</strong>")) %  address[0][0])
                # save point
                self.save_point(point, address[0][0])
        except Exception as e:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "Reverse pyarchinit geocoding error"), unicode(QCoreApplication.translate('pyarchinit geocoding', "<strong>Unhandled exception</strong>.<br>%s" % e)))
        return
    def on_pushButton_locate_pressed(self):
        
        if self.previous_map_tool:
            self.iface.mapCanvas().setMapTool(self.previous_map_tool)
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(),QCoreApplication.translate('pyarchinit geocoding', "pyarchinit geocoding error"), chk)
            return

        geocoder = self.get_geocoder_instance()
        
        # # create and show the dialog
        # dlg = GeoCodingDialog()
        # # show the dialog
        # dlg.adjustSize()
        # dlg.show()
        #result = DialogSita.exec_()
        # # See if OK was pressed
        # if result == 1 :
        try:
            result = geocoder.geocode(unicode(self.address.text()).encode('utf-8'))
        except Exception as e:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "pyarchinit geocoding plugin error"), QCoreApplication.translate('GeoCoding', "Sembra esserci un errore con il servizio geocoding:<br><strong>%s</strong>"% e+"\n\n Controlla l'indirizzo" ))
            return

        if not result:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('pyarchinit geocoding', "Not found"), QCoreApplication.translate('pyarchinit geocoding', "Questo indirizzo non esiste: <strong>%s</strong>." % self.address.text()))
            return

        places = {}
        for place, point in result:
            places[place] = point

        if len(places) == 1:
            self.process_point(place, point)
        else:
            #all_str = QCoreApplication.translate('pyarchinit geocoding', 'Tutti')
            place_dlg = PlaceSelectionDialog()
            #place_dlg.placesComboBox.addItem(all_str)
            place_dlg.placesComboBox.addItems(places.keys())
            place_dlg.show()
            result = place_dlg.exec_()
            # if result == 1 :
                # if place_dlg.placesComboBox.currentText() == 'Tutti':
                    # for place in places:
                        # self.process_point(place, places[place])
                # else:
            point = places[unicode(place_dlg.placesComboBox.currentText())]
            self.process_point(place_dlg.placesComboBox.currentText(), point)
        return
    
    def logMessage(self, msg):
        if self.get_config('writeDebug'):
            QgsMessageLog.logMessage(msg, 'GeoCoding')
    def get_geocoder_instance(self):
        """
        Loads a concrete Geocoder class
        """

        #geocoder_class = str(self.get_config('GeocoderClass'))

        #if not geocoder_class:
        geocoder_class ='Nominatim'

        #if geocoder_class == 'Nominatim':
        return OsmGeoCoder()
        # else:
            # return GoogleGeoCoder(self.get_config('googleKey'))



    def process_point(self, place, point):
        """
        Transforms the point and save
        """
        # lon lat and transform
        point = QgsPoint(float(point[0]), float(point[1]))
        point = pointFromWGS84(point, self._get_layer_crs())
        
        # Set the extent to our new point
        self.canvas.setCenter(point)

        scale = float(self.get_config('ZoomScale', 200))
        # adjust scale to display correct scale in qgis
        if scale:
            self.canvas.zoomScale(scale)

        # Refresh the map
        self.canvas.refresh()
        # save point
        self.save_point(point, unicode(place))

    def _get_layer_crs(self):
        """get CRS from destination layer or from canvas if the layer does not exist"""
        try:
            return self.currentLayerId.crs()
        except:
            return self._get_canvas_crs()


    def _get_canvas_crs(self):
        """compat"""
        try:
            return self.iface.mapCanvas().mapRenderer().destinationCrs()
        except:
            return self.iface.mapCanvas().mapSettings().destinationCrs()

    def _get_registry(self):
        """compat"""
        try:
            return QgsMapLayerRegistry.instance()
        except:
            return QgsProject.instance()

    # save point to file, point is in project's crs
    def save_point(self, point, address):
        try:
            sourceLYR = QgsProject.instance().mapLayersByName('Pyrchinit localizzazione trovata')[0]
            QgsProject.instance().removeMapLayer(sourceLYR)  
        except:
            pass
        self.logMessage('Saving point ' + str(point[0])  + ' ' + str(point[1]))
        # create and add the point layer if not exists or not set
        if not self._get_registry().mapLayer(self.layerid) :
            # create layer with same CRS as map canvas
            crs = self._get_canvas_crs()
            self.layer = QgsVectorLayer("Point?crs=" + crs.authid(), "Pyrchinit localizzazione trovata", "memory")
            self.provider = self.layer.dataProvider()

            # add fields
            self.provider.addAttributes([QgsField("id", QVariant.Int)])
            self.provider.addAttributes([QgsField("indirizzo", QVariant.String)])

            # BUG: need to explicitly call it, should be automatic!
            self.layer.updateFields()

            # Labels on
            try:
                label_settings = QgsPalLayerSettings()
                label_settings.fieldName = "sito"
                self.layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
                self.layer.setLabelsEnabled(True)
            except:
                self.layer.setCustomProperty("labeling", "pal")
                self.layer.setCustomProperty("labeling/enabled", "true")
                self.layer.setCustomProperty("labeling/fontFamily", "Arial")
                self.layer.setCustomProperty("labeling/fontSize", "12")
                self.layer.setCustomProperty("labeling/multilineAlign", "0" )
                self.layer.layer.setCustomProperty("labeling/bufferDraw", True)
                self.layer.setCustomProperty("labeling/namedStyle", "Bold")
                self.layer.setCustomProperty("labeling/fieldName", "sito")
                self.layer.setCustomProperty("labeling/placement", "2")

            # add layer if not already
            self._get_registry().addMapLayer(self.layer)

            # store layer id
            self.layerid = self.layer.id()


        # add a feature
        try:
            fields=self.layer.pendingFields()
        except:
            fields=self.layer.fields()

        fet = QgsFeature(fields)
        try:
            fet.setGeometry(QgsGeometry.fromPoint(point))
        except:
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point)))

        try: # QGIS < 1.9
            
            fet.setAttributeMap({0 : 1})
            fet.setAttributeMap({1 : address})
        except: # QGIS >= 1.9
            fet['id']=1
            fet['indirizzo'] = address

        self.layer.startEditing()
        self.layer.addFeatures([ fet ])
        self.layer.commitChanges()
        self.canvas.refresh()
        # res = QMessageBox.information(self, 'PyArchInit',"Vuoi settarlo come sito?\n Schiaccia ok altrimenti verrà visualizzato solo la localizzazione", QMessageBox.Ok | QMessageBox.Cancel)
            
        # if res==QMessageBox.Ok:
            # conn = Connection()
            # conn_str = conn.conn_str()
            # conn_sqlite = conn.databasename()
            # conn_user = conn.datauser()
            # conn_host = conn.datahost()
            # conn_port = conn.dataport()
            # port_int  = conn_port["port"]
            # port_int.replace("'", "")
            


            
            # self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            # self.DB_MANAGER.connection()
            # test_conn = conn_str.find('sqlite')
            # if test_conn == 0:
                # sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                               # "pyarchinit_DB_folder")
                # uri = QgsDataSourceUri()
                # uri.setDatabase(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
                # schema = ''
                
                    
                # table = 'site_table'
                
                # uri.setDataSource(schema, table,'')
                #sourceLYR = QgsProject.instance().mapLayersByName('Pyrchinit localizzazione trovata')[0]
                #puntiLYR2 = QgsProject.instance().mapLayersByName('Localizzazione siti puntuale')[0]
        layer_provider = self.layer.dataProvider()
        layer_provider.addAttributes([QgsField("sito", QVariant.String)])     
        layer_provider.addAttributes([QgsField("nazione", QVariant.String)])                
        layer_provider.addAttributes([QgsField("regione", QVariant.String)])
        layer_provider.addAttributes([QgsField("comune", QVariant.String)])
        layer_provider.addAttributes([QgsField("descrizione", QVariant.String)])
        layer_provider.addAttributes([QgsField("provincia", QVariant.String)])
        
        self.layer.updateFields()

       
        self.layer.startEditing()
        # ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
        # Sito = str(ID_Sito[0])
        features = []
        for f in self.layer.getFeatures():
            s = {2: f['indirizzo'].split(',')[0]}
            layer_provider.changeAttributeValues({f.id(): s})
            nazione = {3: f['indirizzo'].split(',')[-1]}
            layer_provider.changeAttributeValues({f.id(): nazione})
            regione = {4: f['indirizzo'].split(',')[-3]}
            layer_provider.changeAttributeValues({f.id(): regione})                    
            comune = {5: f['indirizzo'].split(',')[1]}
            layer_provider.changeAttributeValues({f.id(): comune})
            provincia = {7: f['indirizzo'].split(',')[-4]}
            layer_provider.changeAttributeValues({f.id(): provincia})
        
        for feature in self.layer.getFeatures():
            
            sito=feature.attributes()[2]
            feature.setAttribute('sito', sito)
            na=feature.attributes()[3]
            feature.setAttribute('nazione', na)
            r=feature.attributes()[4]
            feature.setAttribute('regione', r)             
            comune=feature.attributes()[5]
            feature.setAttribute('comune', comune)
            pr=feature.attributes()[6]
            feature.setAttribute('descrizione','')
            pr=feature.attributes()[7]
            feature.setAttribute('provincia', pr)
            
            self.layer.updateFeature(feature)
            
            features.append(feature)
        self.layer.commitChanges()    
                # destLYR1 = QgsVectorLayer(uri.uri(), table, 'spatialite') 
                # destLYR1.commitChanges()
                # destLYR1.startEditing()
                # data_provider = destLYR1.dataProvider()
                # data_provider.addFeatures(features)
                # destLYR1.commitChanges()
                
                # res = QMessageBox.information(self, 'PyArchInit',"Vuoi salvare il sito", QMessageBox.Ok | QMessageBox.Cancel)
                # if res==QMessageBox.Ok:
                    # f=[]
                    # for feature in self.layer.getFeatures():
                        # f.append(feature)
                    # puntiLYR2 = QgsProject.instance().mapLayersByName('Localizzazione siti puntuale')[0]
                    # puntiLYR2.startEditing()
                    # data_provider2 = puntiLYR2.dataProvider()
                    # data_provider2.addFeatures(f)
                    # puntiLYR2.commitChanges()
                    
            # else:
                # uri = QgsDataSourceUri()
                # uri.setConnection(conn_host["host"], conn_port["port"], conn_sqlite["db_name"], conn_user['user'], conn_password['password'])
                # schema = 'public'
                # table = 'site_table'
                # geom_column = ''
                # uri.setDataSource(schema, table,geom_column)
                # sourceLYR = QgsProject.instance().mapLayersByName('Pyrchinit localizzazione trovata')[0]
                # puntiLYR2 = QgsProject.instance().mapLayersByName('Localizzazione siti puntuale')[0]
                # layer_provider = sourceLYR.dataProvider()
                # layer_provider.addAttributes([QgsField("sito", QVariant.String)])     
                # layer_provider.addAttributes([QgsField("nazione", QVariant.String)])                
                # layer_provider.addAttributes([QgsField("regione", QVariant.String)])
                # layer_provider.addAttributes([QgsField("comune", QVariant.String)])
                # layer_provider.addAttributes([QgsField("descrizione", QVariant.String)])
                # layer_provider.addAttributes([QgsField("provincia", QVariant.String)])
                
                # sourceLYR.updateFields()

               
                # # sourceLYR.startEditing()
                # # ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                # # Sito = str(ID_Sito[0])
                # features = []
                # for f in sourceLYR.getFeatures():
                    # s = {1: f['indirizzo'].split(',')[0]}
                    # layer_provider.changeAttributeValues({f.id(): s})
                    # nazione = {2: f['indirizzo'].split(',')[-1]}
                    # layer_provider.changeAttributeValues({f.id(): nazione})
                    # regione = {3: f['indirizzo'].split(',')[-3]}
                    # layer_provider.changeAttributeValues({f.id(): regione})                    
                    # comune = {4: f['indirizzo'].split(',')[1]}
                    # layer_provider.changeAttributeValues({f.id(): comune})
                    # provincia = {6: f['indirizzo'].split(',')[-4]}
                    # layer_provider.changeAttributeValues({f.id(): provincia})
                # sourceLYR.commitChanges()    
                # for feature in sourceLYR.getFeatures():
                    
                    # sito=feature.attributes()[1]
                    # feature.setAttribute('sito', sito)            
                    # na=feature.attributes()[2]
                    # feature.setAttribute('nazione', na)
                    # r=feature.attributes()[3]
                    # feature.setAttribute('regione', r)             
                    # comune=feature.attributes()[4]
                    # feature.setAttribute('comune', comune)
                    # pr=feature.attributes()[5]
                    # feature.setAttribute('descrizione','')
                    # pr=feature.attributes()[6]
                    # feature.setAttribute('provincia', pr)
                    # features.append(feature)
                    # sourceLYR.updateFeature(feature)
                    
                
                # destLYR = QgsVectorLayer(uri.uri(), table, 'postgres')    
                # destLYR.startEditing()
                # data_provider = destLYR.dataProvider()
                # data_provider.addFeatures(features)
                # destLYR.commitChanges()

                # table2 = 'pyarchinit_siti'
                # geom_column = 'the_geom'
                # uri.setDataSource(schema, table2, geom_column)
                # features2 = []
                # for feature in sourceLYR.getFeatures():
                    # features2.append(feature)
                    # feature.setAttribute('comune', '')
                    # feature.setAttribute('nazione', '')
                    # sito = feature.attributes()[1]
                    # feature.setAttribute('sito', sito)

                    # sourceLYR.updateFeature(feature)
                    
                # #puntiLYR2 = QgsVectorLayer(uri.uri(), table2, 'spatialite')
                # puntiLYR2.startEditing()
                # data_provider2 = puntiLYR2.dataProvider()
                # data_provider2.addFeatures(features2)
                # puntiLYR2.commitChanges()
            # destLYR1.commitChanges()
            
            # #QgsProject.instance().removeMapLayer(sourceLYR)          
        # else:
            # pass
   
        
    def check_settings (self):
        p = QgsProject.instance()
        error = ''
        if QT_VERSION==4:
            if not self.iface.mapCanvas().hasCrsTransformEnabled() and self.iface.mapCanvas().mapRenderer().destinationCrs().authid() != 'EPSG:4326':
                error = QCoreApplication.translate('pyarchinit geocoding', "On-the-fly reprojection must be enabled if the destination CRS is not EPSG:4326. Please enable on-the-fly reprojection.")

        return error
## Class end


def logMessage(msg):
    if QgsSettings().value('PythonPlugins/pyarchinit/writeDebug'):
        QgsMessageLog.logMessage(msg, 'GeoCoding')
class GeoCodeException(Exception):
    pass
class OsmGeoCoder():

    url = 'https://nominatim.openstreetmap.org/search?format=json&q={address}'
    reverse_url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}'

    def geocode(self, address):
        try: 
            url = self.url.format(**{'address': address.decode('utf8')})
            logMessage(url)
            results = json.loads(NAM.request(url, blocking=True)[1].decode('utf8'))
            return [(rec['display_name'], (rec['lon'], rec['lat'])) for rec in results]
        except Exception as e:
            raise GeoCodeException(str(e))

    def reverse(self, lon, lat):
        """single result"""
        try: 
            url = self.reverse_url.format(**{'lon': lon, 'lat': lat})
            logMessage(url)
            rec = json.loads(NAM.request(url, blocking=True)[1].decode('utf8'))
            return [(rec['display_name'], (rec['lon'], rec['lat']))]
        except Exception as e:
            raise GeoCodeException(str(e))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_US()
    ui.show()
    sys.exit(app.exec_())
