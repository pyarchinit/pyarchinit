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
 *   (at your option) any later version.  #simple                          *
 *                                                                         *
 ***************************************************************************/
"""

import os
import random
import sqlite3
import time
from builtins import object
from builtins import range
from builtins import str

from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import Qt
from qgis.core import *
from qgis.gui import *

import urllib.request
import urllib.error

from ..utility.create_style import ThesaurusStyler, USViewStyler
from ..utility.settings import Settings

from ..db.pyarchinit_conn_strings import Connection

class Pyarchinit_pyqgis(QDialog):

    HOME = os.environ['PYARCHINIT_HOME']
    FILEPATH = os.path.dirname(__file__)
    LAYER_STYLE_PATH = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles', os.sep)
    LAYER_STYLE_PATH_SPATIALITE = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles_spatialite', os.sep)
    #SRS = 3004
    L=QgsSettings().value("locale/userLocale")[0:2]
    USLayerId = ""
    
    LAYERS_DIZ = {"1": "pyarchinit_campionature",
                  "2": "pyarchinit_individui",
                  "3": "pyarchinit_linee_rif",
                  "4": "pyarchinit_punti_rif",
                  "5": "pyarchinit_quote",
                  "6": "pyarchinit_quote_view",
                  "7": "pyarchinit_ripartizioni_spaziali",
                  "8": "pyarchinit_sezioni",
                  "9": "pyarchinit_siti",
                  "10": "pyarchinit_strutture_ipotesi",
                  "11": "pyarchinit_us_view",
                  "12": "pyunitastratigrafiche",
                  "13": "pyarchinit_documentazione",
                  "14": "pyarchinit_doc_view",
                  "15": "pyarchinit_us_view",  # per documentazione
                  "16": "pyarchinit_us_negative_doc",  # per documentazione
                  "17": "pyarchinit_us_negative_doc_view",  # per documentazione
                  "18": "pyarchinit_site_view",
                  "19": "pyarchinit_siti_polygonal",
                  "20": "pyarchinit_siti_polygonal_view",
                  "21": "pyarchinit_site_view",
                  "22": "pyarchinit_strutture_view",
                  "23": "pyarchinit_tomba_view",
                  "24": "pyarchinit_tafonomia",
                  "25": "pyarchinit_doc_view_b",
                  "26": "pyarchinit_reperti",
                  "27": "pyarchinit_reperti_view",
                  "28": "pyarchinit_sezioni_view",
                  "29": "pyunitastratigrafiche_usm",
                  "30": "pyarchinit_usm_view",
                  "31": "pyarchinit_quote_usm",
                  "32": "pyarchinit_quote_usm_view"
                  }
    if L=='it':
        LAYERS_CONVERT_DIZ = {"pyarchinit_campionature": "Punti di campionatura",
                              "pyarchinit_individui": "Individui",
                              "pyarchinit_linee_rif": "Linee di riferimento",
                              "pyarchinit_punti_rif": "Punti di riferimento",
                              "pyarchinit_quote": "Quote US disegno",
                              "pyarchinit_quote_view": "Quote US Vista",
                              "pyarchinit_ripartizioni_spaziali": "Ripartizioni spaziali",
                              "pyarchinit_sezioni": "Sezioni di scavo",
                              "pyarchinit_siti": "Localizzazione siti puntuale",
                              "pyarchinit_strutture_ipotesi": "Ipotesi strutture da scavo",
                              "pyarchinit_us_view": "US Vista",
                              "pyunitastratigrafiche": "Unità Stratigrafiche disegno",
                              "pyarchinit_documentazione": "Registro documentazione",
                              "pyarchinit_doc_view": "Documentazione Vista",
                              "pyarchinit_us_negative_doc": "US Negative per sezioni/elevati",
                              "pyarchinit_us_negative_doc_view": "Vista US Negative per sezioni/elevati",
                              "pyarchinit_site_view": "Localizzazione siti Vista",
                              "pyarchinit_siti_polygonal": "Perimetrazione siti poligonali",
                              "pyarchinit_siti_polygonal_view": "Perimetrazione siti poligonali Vista",
                              #"pyarchinit_site_view": "Localizzazione siti puntuale Vista",
                              "pyarchinit_strutture_view": "Ipotesi strutture da scavo Vista",
                              "pyarchinit_tomba_view": "Tomba View",
                              "pyarchinit_tafonomia": "Tomba",
                              "pyarchinit_doc_view_b": "Documentazione Vista B",
                              "pyarchinit_reperti": "Reperti",
                              "pyarchinit_reperti_view": "Reperti view",
                              "pyarchinit_sezioni_view": "Sezioni di scavo Vista",
                              "pyunitastratigrafiche_usm":"Unità Stratigrafiche Verticali disegno",
                              "pyarchinit_usm_view":"USM Vista",
                              "pyarchinit_quote_usm":"Quote Verticali disegno",
                              "pyarchinit_quote_usm_view":"Quote USM Vista"

                              }
    elif L=='de':
        LAYERS_CONVERT_DIZ = {"pyarchinit_campionature": "Probenmesspunkte",
                              "pyarchinit_individui": "Individuen",
                              "pyarchinit_linee_rif": "Bezugslinien",
                              "pyarchinit_punti_rif": "Bezugspunkte",
                              "pyarchinit_quote": "Nivellements der SE",
                              "pyarchinit_quote_view": "Nivellements Ansicht der SE",
                              "pyarchinit_ripartizioni_spaziali": "Ausgrabungsstättenunterteilungen",
                              "pyarchinit_sezioni": "Profile",
                              "pyarchinit_siti": "Genauer Ausgrabungsstättenbereich",
                              "pyarchinit_strutture_ipotesi": "Vorläufige Strukturinterpretation der Grabung",
                              "pyarchinit_us_view": "SE Ansicht",
                              "pyunitastratigrafiche": "Zeichnung der Stratigraphischen Einheiten",
                              "pyarchinit_documentazione": "Dokumentation zurücksetzen",
                              "pyarchinit_doc_view": "Dokumentation Ansicht",
                              "pyarchinit_us_negative_doc": "SE-Negativ für profile/groß",
                              "pyarchinit_us_negative_doc_view": "SE Ansicht Negative für profile/groß",
                              #"pyarchinit_site_view": "Genauer Ausgrabungsstättenbereich Ansicht",
                              "pyarchinit_siti_polygonal": "Perimeterstand Ausgrabungsstätte poligonal",
                              "pyarchinit_siti_polygonal_view": "Perimeterstand Ausgrabungsstätte poligonal Ansicht",
                              "pyarchinit_site_view": "Genauer Ausgrabungsstättenbereich Ansicht",
                              "pyarchinit_strutture_view": "Vorläufige Strukturinterpretation der Grabung Ansicht",
                              "pyarchinit_tomba_view": "Taphonomie Ansicht",
                              "pyarchinit_tafonomia": "Taphonomie",
                              "pyarchinit_doc_view_b": "Dokumentation Ansicht B",
                              "pyarchinit_reperti": "Artefakt",
                              "pyarchinit_reperti_view": "Artefakt view",
                              "pyarchinit_sezioni_view": "Profile view",
                              "pyunitastratigrafiche_usm":"SEW",
                              "pyarchinit_usm_view":"SEW Ansicht",
                              "pyarchinit_quote_usm":"Nivellements Ansicht der SEW",
                              "pyarchinit_quote_usm_view":"Nivellements Ansicht der SEW"

                              }
    else:
        LAYERS_CONVERT_DIZ = {"pyarchinit_campionature": "Samples point",
                              "pyarchinit_individui": "Individual",
                              "pyarchinit_linee_rif": "Reference line",
                              "pyarchinit_punti_rif": "Reference point",
                              "pyarchinit_quote": "SU elevation",
                              "pyarchinit_quote_view": "SU elevation view",
                              "pyarchinit_ripartizioni_spaziali": "Spatial allocation",
                              "pyarchinit_sezioni": "Excavation section",
                              "pyarchinit_siti": "Point site localization",
                              "pyarchinit_strutture_ipotesi": "Hypothetical excavation structures",
                              "pyarchinit_us_view": "SU view",
                              "pyunitastratigrafiche": "SU drawing",
                              "pyarchinit_documentazione": "Documentation register",
                              "pyarchinit_doc_view": "Documentation view",
                              "pyarchinit_us_negative_doc": "Negative SU for section/elevation",
                              "pyarchinit_us_negative_doc_view": "Negative SU for section/elevation view",
                              #"pyarchinit_site_view": "Site view",
                              "pyarchinit_siti_polygonal": "Areal site",
                              "pyarchinit_siti_polygonal_view": "Areal site view",
                              "pyarchinit_site_view": "Site point view",
                              "pyarchinit_strutture_view": "Hypothetical excavation structures view",
                              "pyarchinit_tomba_view": "Taphonomy view",
                              "pyarchinit_tafonomia": "Taphonomy",
                              "pyarchinit_doc_view_b": "Documentation view B",
                              "pyarchinit_reperti": "Artefact",
                              "pyarchinit_reperti_view": "Artefact view",
                              "pyarchinit_sezioni_view": "Excavation section view",
                              "pyunitastratigrafiche_usm":"SUW drawing",
                              "pyarchinit_usm_view":"SUW View",
                              "pyarchinit_quote_usm":"SUW Elevation",
                              "pyarchinit_quote_usm_view":"SUW Elevation View"
                              }

    def __init__(self, iface):
        super().__init__()
        self.iface = iface


    def remove_USlayer_from_registry(self):
        QgsProject.instance().removeMapLayer(self.USLayerId)
        return 0

    def charge_individui_us(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if self.L=='it':
            name_layer_s='US view'
        elif self.L=='de':
            name_layer_s='SE view'
        else:
            name_layer_s='SU view'
        if self.L=='it':
            name_layer_q='Quote view'
        elif self.L=='de':
            name_layer_q='Hoch view'
        else:
            name_layer_q='Elevation view'   
        groupName="View scheda US-Individui"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]
            gidstr = "id_us = '" + str(data[0]) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = '" + str(data[i]) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            
                
            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), '', 'spatialite')
            ###################################################################
            if layerUS.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)

                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                
            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', 'spatialite')

            if layerQUOTE.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerQUOTE.setCrs(crs)
                unique_name = self.unique_layer_name(name_layer_q)
                layerQUOTE.setName(unique_name)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                QgsProject.instance().addMapLayers([layerQUOTE], False)


        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "id_us = " + str(data[0])
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = " + str(data[i])

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, "postgres")

            if layerUS.isValid():

                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)

                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)

            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', "postgres")

            if layerQUOTE.isValid():

                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:

                    unique_name = self.unique_layer_name(name_layer_q)
                    layerQUOTE.setName(unique_name)

                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                except Exception as e:
                    pass
                    # f = open('/test_ok.txt','w')
                    # f.write(str(e))
                    # f.close()

    def charge_vector_layers_from_matrix(self, idus):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)
        self.idus = idus

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        if self.L=='it':
            name_layer_s='US view'
        elif self.L=='de':
            name_layer_s='SE view'
        else:
            name_layer_s='SU view'
        if self.L=='it':
            name_layer_q='Quote view'
        elif self.L=='de':
            name_layer_q='Hoch view'
        else:
            name_layer_q='Elevation view'
        groupName="View scheda US-Matrix"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            gidstr = "id_us = '" + str(self.idus) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', 'spatialite')

            if layerQUOTE.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerQUOTE.setCrs(crs)
                unique_name = self.unique_layer_name(name_layer_q)
                layerQUOTE.setName(unique_name)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            else:
                pass
            
            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), '', 'spatialite')

            if layerUS.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer valid", QMessageBox.Ok)
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                pass

            

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "id_us = " + str(self.idus)

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            
            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', "postgres")

            if layerQUOTE.isValid():
                unique_name = self.unique_layer_name(name_layer_q)
                layerQUOTE.setName(unique_name)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                except Exception as e:
                    pass
                   
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer Quote non valido", QMessageBox.Ok)
            
            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(),'' , "postgres")

            if layerUS.isValid():
                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)
                # self.USLayerId = layerUS.getLayersID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer US non valido", QMessageBox.Ok)

            
        
    def charge_vector_layers_doc(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View scheda Documentazione"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            sezstr = ""
            if len(data) == 1:
                sezstr = "sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                sezstr = "(sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    sezstr += " OR (sito = '" + str(data[i].sito) + "' AND tipo_doc = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc = '" + str(data[i].nome_doc) + "')"
            else:
                pass
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            
            

            
            layer_name_pos = "Sezione - "+ str(data[0].sito)+ ": " + str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)
            uri.setDataSource('', 'pyarchinit_sezioni_view', 'the_geom', sezstr, "ROWID")
            ##          uri.setDataSource('','pyarchinit_doc_view_b', 'the_geom', docstr, "ROWID")
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'spatialite')
            if layerPos.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerPos.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "Layer Sezioni valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Sezioni non valido", QMessageBox.Ok)

            
            
            
            
            docstr = ""
            if len(data) == 1:
                docstr = "sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                docstr = "(sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    docstr += " OR (sito = '" + str(data[i].sito) + "' AND tipo_doc = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc = '" + str(data[i].nome_doc) + "')"
            else:
                pass
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            
            

            
            layer_name_pos = "Registro Doc - "+str(data[0].sito)+ ": " + str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)
            uri.setDataSource('', 'pyarchinit_doc_view', 'the_geom', docstr, "ROWID")
            ##          uri.setDataSource('','pyarchinit_doc_view_b', 'the_geom', docstr, "ROWID")
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'spatialite')
            if layerPos.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerPos.setCrs(crs)

                #QMessageBox.warning(self, "Pyarchinit", "Layer Registro Documentazione valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Registro Documentazione non valido", QMessageBox.Ok)
                


            gdrst = "id_us = '" + str(data[0]) + "'"
            if len(data) == 1:
                gdrst = "sito_n = '" + str(data[0].sito) + "' AND nome_doc_n = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc_n = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                gdrst = "(sito_n = '" + str(data[0].sito) + "' AND nome_doc_n = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    gdrst += " OR (sito_n = '" + str(data[i].sito) + "' AND tipo_doc_n = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc_n = '" + str(data[i].nome_doc) + "')"
            else:
                pass


            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            layer_name_neg = "US Negative - "+str(data[0].sito)+ ": " + str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)
            uri.setDataSource('', 'pyarchinit_us_negative_doc_view', 'the_geom', gdrst, "ROWID")
            layerNeg = QgsVectorLayer(uri.uri(), layer_name_neg, 'spatialite')



            if layerNeg.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerNeg.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US Negative valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerNeg))
                QgsProject.instance().addMapLayers([layerNeg], False)
              
                
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer US Negative non valido", QMessageBox.Ok)
            
            docstr = ""
            if len(data) == 1:
                docstr = "sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                docstr = "(sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    docstr += " OR (sito = '" + str(data[i].sito) + "' AND tipo_doc = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc = '" + str(data[i].nome_doc) + "')"
            else:
                pass
            

            layer_name_pos = "US orizzontali - "+ str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)

            uri.setDataSource("public", 'pyarchinit_us_view', 'the_geom', docstr, "ROWID")

            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'spatialite')

            if layerPos.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerPos.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(layerPos.extent())





            layer_name_verticali = "US Verticali - "+ str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)

            uri.setDataSource("public", 'pyarchinit_usm_view', 'the_geom', docstr, "ROWID")

            layerverticali = QgsVectorLayer(uri.uri(), layer_name_verticali, 'spatialite')

            if layerPos.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerPos.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer USM valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerverticali))
                QgsProject.instance().addMapLayers([layerverticali], False)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(layerPos.extent())

            docstr_grezzo = ""
            if len(data) == 1:
                docstr = "sito = '" + str(data[0].sito) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                docstr = "(sito = '" + str(data[0].sito) + "' AND tipo_doc = '" + str(
                    data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    docstr += " OR (sito = '" + str(data[0].sito) + "' AND tipo_doc = '" + str(
                        data[0].tipo_documentazione) + "')"
            else:
                pass


            layer_name_pos = "US Disegno - " + str(data[0].tipo_documentazione)

            uri.setDataSource("public", 'pyunitastratigrafiche', 'the_geom', docstr_grezzo, "gid")

            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'spatialite')

            if layerPos.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerPos.setCrs(crs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_vuote.qml')


                layerPos.loadNamedStyle(style_path)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US disegno valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(layerPos.extent())


        elif settings.SERVER == 'postgres':
            

            
            uri = QgsDataSourceUri()
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            docstr = ""
            if len(data) == 1:
                docstr = "sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                docstr = "(sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    docstr += " OR (sito = '" + str(data[i].sito) + "' AND tipo_doc = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc = '" + str(data[i].nome_doc) + "')"
            else:
                pass
            

            layer_name_pos = "US orizzontali - "+str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)

            uri.setDataSource("", 'pyarchinit_us_view', 'the_geom', docstr, "gid")
            
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'postgres')

            if layerPos.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(layerPos.extent())

            us_name_pos = "US Disegno grezzo - "+str(data[0].tipo_documentazione)

            docstr_grezzo = ""
            if len(data) == 1:
                docstr = "sito = '" + str(data[0].sito) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                docstr = "(sito = '" + str(data[0].sito) + "' AND tipo_doc = '" + str(
                    data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    docstr += " OR (sito = '" + str(data[0].sito) + "' AND tipo_doc = '" + str(
                        data[0].tipo_documentazione) + "')"
            else:
                pass

            uri.setDataSource("", 'pyunitastratigrafiche', 'the_geom', docstr_grezzo, "gid")

            usPos = QgsVectorLayer(uri.uri(), us_name_pos, 'postgres')

            if usPos.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(usPos))
                QgsProject.instance().addMapLayers([layerPos], False)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(usPos.extent())



            layer_name_pos = "US Verticali - "+ str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)

            uri.setDataSource("", 'pyarchinit_usm_view', 'the_geom', docstr, "gid")
            
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'postgres')

            if layerPos.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer USM valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(layerPos.extent())
            
            
            layer_name_neg = "US Negative - "+str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc) + " - negative"

            '''docstrn = "sito_n = '" + str(data[0].sito) + "' AND nome_doc_n = '" + str(
                data[0].nome_doc) + "' AND tipo_doc_n = '" + str(data[0].tipo_documentazione) + "')"
            if len(data) > 1:
                for i in range(len(data)):
                    docstr += " OR (sito_n = '" + str(data[i].sito) + "' AND tipo_doc_n = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc_n = '" + str(data[i].nome_doc) + "')"'''
            gdrst = "id_us = '" + str(data[0]) + "'"
            if len(data) == 1:
                gdrst = "sito_n = '" + str(data[0].sito) + "' AND nome_doc_n = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc_n = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                gdrst = "(sito_n = '" + str(data[0].sito) + "' AND nome_doc_n = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    gdrst += " OR (sito_n = '" + str(data[i].sito) + "' AND tipo_doc_n = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc_n = '" + str(data[i].nome_doc) + "')"
            else:
                pass
            uri.setDataSource("", 'pyarchinit_us_negative_doc_view', 'the_geom', gdrst, "gid")
            layerNeg = QgsVectorLayer(uri.uri(), layer_name_neg, 'postgres')

            if layerNeg.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US Negative valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerNeg))
                QgsProject.instance().addMapLayers([layerNeg], False)

              

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer US Negative non valido", QMessageBox.Ok)
            
            
            if len(data) == 1:
                docstr = "sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                docstr = "(sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    docstr += " OR (sito = '" + str(data[i].sito) + "' AND tipo_doc = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc = '" + str(data[i].nome_doc) + "')"
            else:
                pass
            
            
            layer_name_pos = "Registro doc - "+str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)
            uri.setDataSource("", 'pyarchinit_doc_view', 'the_geom', docstr, "gid")
            ##          uri.setDataSource('','pyarchinit_doc_view_b', 'the_geom', docstr, "ROWID")
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'postgres')
            if layerPos.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)
                #self.canvas = QgsMapCanvas()
                #self.canvas.setExtent(layerPos.extent())
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer US non valido", QMessageBox.Ok)

            layer_name_pos = "Sezione - " + str(data[0].sito) + ": " + str(data[0].tipo_documentazione) + ": " + str(
                data[0].nome_doc)

            sezstr = ""
            if len(data) == 1:
                sezstr = "sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "'"
            elif len(data) > 1:
                sezstr = "(sito = '" + str(data[0].sito) + "' AND nome_doc = '" + str(
                    data[0].nome_doc) + "' AND tipo_doc = '" + str(data[0].tipo_documentazione) + "')"
                for i in range(len(data)):
                    sezstr += " OR (sito = '" + str(data[i].sito) + "' AND tipo_doc = '" + str(
                        data[i].tipo_documentazione) + " AND nome_doc = '" + str(data[i].nome_doc) + "')"
            else:
                pass

            uri.setDataSource('', 'pyarchinit_sezioni_view', 'the_geom', sezstr, "gid")
            ##          uri.setDataSource('','pyarchinit_doc_view_b', 'the_geom', docstr, "ROWID")
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'postgres')
            if layerPos.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "Layer Sezioni valido", QMessageBox.Ok)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerPos))
                QgsProject.instance().addMapLayers([layerPos], False)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Sezioni non valido", QMessageBox.Ok)

    def charge_vector_layers_doc_from_scheda_US(self, lista_draw_doc):
        # data riceve 5 valori che saranno: sito, area, US, nome_doc e tipo_doc
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)
        sito = lista_draw_doc[0]
        area = lista_draw_doc[1]
        us = lista_draw_doc[2]
        tipo_documentazione = lista_draw_doc[3]
        nome_doc = lista_draw_doc[4]

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()

        # ("sito" = 'Scavo esame' AND "tipo_doc" =  'Sezione'  AND "nome_doc" = 'AA1')  OR ("sito" = 'Scavo esame' AND "tipo_doc" =  'Sezione'  AND "nome_doc" = 'AA1')


        if self.L=='it':
            name_layer_s='US view'
        elif self.L=='de':
            name_layer_s='SE view'
        else:
            name_layer_s='SU view'
        if self.L=='it':
            name_layer_sw='USM view'
        elif self.L=='de':
            name_layer_sw='SEW view'
        else:
            name_layer_sw='SUW view'
        
        
        
        if self.L=='it':
            name_layer_d='Sezione view'
        elif self.L=='de':
            name_layer_d='Profile view'
        else:
            name_layer_d='Section view' 
        if self.L=='it':
            name_layer_q='Quote view'
        elif self.L=='de':
            name_layer_q='Hoch view'
        else:
            name_layer_q='Elevation view'
        
        if self.L=='it':
            name_layer_qw='Quote USM view'
        elif self.L=='de':
            name_layer_qw='Hoch SEW view'
        else:
            name_layer_qw='Elevation SUW view'
        
        if self.L=='it':
            name_layer_s_n='US negative view'
        elif self.L=='de':
            name_layer_s_n='SE negative view'
        else:
            name_layer_s_n='SU negative view'   
            
        groupName="View scheda US-Documentazione"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            doc_from_us_str = "sito = '" + sito + "' AND tipo_doc = '" + tipo_documentazione + "' AND nome_doc = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_doc_view', 'the_geom', doc_from_us_str, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_d, 'spatialite')

            if layerUS.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            doc_from_us_neg_str = "sito_n = '" + sito + "' AND area_n = '" + area + "' AND tipo_doc_n = '" + tipo_documentazione + "' AND nome_doc_n = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_negative_doc_view', 'the_geom', doc_from_us_neg_str, "ROWID")
            layerUSneg = QgsVectorLayer(uri.uri(), name_layer_s_n, 'spatialite')

            if layerUSneg.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUSneg.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US negative valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUSneg))
                QgsProject.instance().addMapLayers([layerUSneg], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            doc_from_us_str = "sito = '" + sito + "' AND tipo_doc = '" + tipo_documentazione + "' AND nome_doc = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', doc_from_us_str, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, 'spatialite')

            if layerUS.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer valid", QMessageBox.Ok)
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer US non valido", QMessageBox.Ok)

                # implementare sistema per quote se si vogliono visualizzare sulle piante
            
            
            
            doc_from_us_str = "sito = '" + sito + "' AND tipo_doc = '" + tipo_documentazione + "' AND nome_doc = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_usm_view', 'the_geom', doc_from_us_str, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_sw, 'spatialite')

            if layerUS.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer valid", QMessageBox.Ok)
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer USM non valido", QMessageBox.Ok)
            
            
            """
            uri.setDataSource('','pyarchinit_quote_view', 'the_geom', gidstr.tipodoc(pianta), "ROWID")
            layerQUOTE=QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if  layerQUOTE.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer Quote non valido",QMessageBox.Ok)
            """

        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            doc_from_us_str = "sito = '" + sito + "' AND tipo_doc = '" + tipo_documentazione + "' AND nome_doc = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            

            uri.setDataSource('', 'pyarchinit_doc_view', 'the_geom', doc_from_us_str, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_d, 'postgres')

            if layerUS.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            doc_from_us_neg_str = "sito_n = '" + sito + "' AND area_n = '" + area + "' AND tipo_doc_n = '" + tipo_documentazione + "' AND nome_doc_n = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            #uri = QgsDataSourceUri()
            #uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_negative_doc_view', 'the_geom', doc_from_us_neg_str, "gid")
            layerUSneg = QgsVectorLayer(uri.uri(), name_layer_s_n, 'postgres')

            if layerUSneg.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US negative valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUSneg))
                QgsProject.instance().addMapLayers([layerUSneg], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            doc_from_us_str = "sito = '" + sito + "' AND tipo_doc = '" + tipo_documentazione + "' AND nome_doc = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            #uri = QgsDataSourceUri()
            #uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', doc_from_us_str, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, 'postgres')

            if layerUS.isValid():
                QMessageBox.warning(self, "Pyarchinit", "OK Layer valid", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer US non valido", QMessageBox.Ok)

                # implementare sistema per quote se si vogliono visualizzare sulle piante
            
            
            doc_from_us_str = "sito = '" + sito + "' AND tipo_doc = '" + tipo_documentazione + "' AND nome_doc = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            #uri = QgsDataSourceUri()
            #uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_usm_view', 'the_geom', doc_from_us_str, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_sw, 'postgres')

            if layerUS.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer valid", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer USM non valido", QMessageBox.Ok)
            
            
            """
            uri.setDataSource('','pyarchinit_quote_view', 'the_geom', gidstr.tipodoc(pianta), "ROWID")
            layerQUOTE=QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if  layerQUOTE.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer Quote non valido",QMessageBox.Ok)
            """
            
    
    
    def charge_vector_layers(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        a = Connection()
        styler = USViewStyler(a)
        if self.L=='it':
            name_layer_s='US view'
        elif self.L=='de':
            name_layer_s='SE view'
        else:
            name_layer_s='SU view'
        if self.L=='it':
            name_layer_q='Quote view'
        elif self.L=='de':
            name_layer_q='Hoch view'
        else:
            name_layer_q='Elevation view'
        
        
        
        groupName="View scheda US"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)  
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            gidstr = "id_us = '" + str(data[0].id_us) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = '" + str(data[i].id_us) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', 'spatialite')

            if layerQUOTE.isValid():

                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerQUOTE.setCrs(crs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                layerQUOTE.loadNamedStyle(style_path)
                unique_name = self.unique_layer_name(name_layer_q)
                layerQUOTE.setName(unique_name)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valid", QMessageBox.Ok)
            
            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), '', 'spatialite')

            if layerUS.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                # Applica lo stile automatico

                # Applica lo stile al layer
                styler.apply_style_to_layer(layerUS)

                # Forza l'aggiornamento del layer
                layerUS.triggerRepaint()

                print("Stile applicato al layer US")





                #else:
                    #style_path_us = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_preview.qml')
                    #layerUS.loadNamedStyle(style_path_us)


                #style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)
                

                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                #layerUS.loadNamedStyle(style_path)
                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "id_us = " + str(data[0].id_us)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = " + str(data[i].id_us)

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            
            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', "postgres")

            if layerQUOTE.isValid():
                unique_name = self.unique_layer_name(name_layer_q)
                layerQUOTE.setName(unique_name)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                except Exception as e:
                    pass
                    # f = open('/test_ok.txt','w')
                    # f.write(str(e))
                    # f.close()
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valide", QMessageBox.Ok)
            
            
            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), '', "postgres")

            if layerUS.isValid():

                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)
                # self.USLayerId = layerUS.getLayersID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer US non valido", QMessageBox.Ok)

            
    def charge_usm_layers(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        if self.L=='it':
            name_layer_s='Stratigrafia Verticale view'
        elif self.L=='de':
            name_layer_s='SEW view'
        else:
            name_layer_s='SUW view'
        if self.L=='it':
            name_layer_q='Quote Verticali view'
        elif self.L=='de':
            name_layer_q='Hoch SEW view'
        else:
            name_layer_q='Elevation SUW view'
        
        
        
        groupName="View scheda USM"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)  
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            gidstr = "id_us = '" + str(data[0].id_us) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = '" + str(data[i].id_us) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            uri.setDataSource('', 'pyarchinit_quote_usm_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', 'spatialite')

            if layerQUOTE.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerQUOTE.setCrs(crs)
                unique_name = self.unique_layer_name(name_layer_q)
                layerQUOTE.setName(unique_name)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valid", QMessageBox.Ok)
            
            uri.setDataSource('', 'pyarchinit_usm_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), '', 'spatialite')

            if layerUS.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)

                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)
                

                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "id_us = " + str(data[0].id_us)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = " + str(data[i].id_us)

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            
            uri.setDataSource("public", "pyarchinit_quote_usm_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), '', "postgres")

            if layerQUOTE.isValid():
                unique_name = self.unique_layer_name(name_layer_q)
                layerQUOTE.setName(unique_name)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                except Exception as e:
                    pass
                    # f = open('/test_ok.txt','w')
                    # f.write(str(e))
                    # f.close()
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valide", QMessageBox.Ok)
            
            
            uri.setDataSource("public", "pyarchinit_usm_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), '', "postgres")

            if layerUS.isValid():
                unique_name = self.unique_layer_name(name_layer_s)
                layerUS.setName(unique_name)
                #layerUS.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer USM non valido", QMessageBox.Ok)
    def charge_vector_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat):
        
        # a = QgsProject.instance().layerTreeRoot()
        # QgsLayoutItemLegend(a).legendFilterByMapEnabled(True) 
        
        self.sito_p = sito_p
        self.cont_per = str(cont_per)
        self.per_label = per_label
        self.fas_label = fas_label
        self.dat = dat
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name
        # self.find_us_cutted(data)
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="Stratigrafie Orizzontali  - %s " % (self.dat)
        
        root = QgsProject.instance().layerTreeRoot()

        
        group = root.addGroup(groupName)
        group.setExpanded(False)  
        
        if self.L=='it':
            layer_name_label_us = "Unita Stratigrafiche" 
            layer_name_label_quote = "Quote US"
        elif self.L=='de':
            layer_name_label_us = "Stratigraphischen Einheiten" 
            layer_name_label_quote = "Nivellements der SE"
        else:
            layer_name_label_us = "Stratigraphic Units"
            layer_name_label_quote = "Elevations SU"
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"
            
            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', cont_per_string, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, 'spatialite')

            if layerQUOTE.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerQUOTE.setCrs(crs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            
            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', cont_per_string, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, 'spatialite')
            


            if layerUS.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                
                QgsProject.instance().addMapLayers([layerUS], False)
                
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer US non valido", QMessageBox.Ok)

            

        elif settings.SERVER == 'postgres':
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            
            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", cont_per_string, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, "postgres")
            if layerQUOTE.isValid():
                #crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                #layerQUOTE.setCrs(crs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                except Exception as e:
                    pass
            
            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", cont_per_string, "gid")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, "postgres")
            if layerUS.isValid():
                #layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer US non valido", QMessageBox.Ok)

            
    def charge_vector_usm_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat):
        
        # a = QgsProject.instance().layerTreeRoot()
        # QgsLayoutItemLegend(a).legendFilterByMapEnabled(True) 
        
        self.sito_p = sito_p
        self.cont_per = str(cont_per)
        self.per_label = per_label
        self.fas_label = fas_label
        self.dat = dat
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name
        # self.find_us_cutted(data)
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()
        groupName=" Stratigrafie Verticali %s " % (self.dat)
        
        root = QgsProject.instance().layerTreeRoot()

        
        group = root.addGroup(groupName)
        group.setExpanded(False)  
        
        if self.L=='it':
            layer_name_label_us = "Unita Stratigrafiche Verticali" 
            layer_name_label_quote = "Quote USM"
        elif self.L=='de':
            layer_name_label_us = "Wand Stratigraphischen Einheiten" 
            layer_name_label_quote = "Nivellements der SEW"
        else:
            layer_name_label_us = "Mansory Stratigraphic Units "
            layer_name_label_quote = "Elevations SUW"
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"
            
            uri.setDataSource('', 'pyarchinit_quote_usm_view', 'the_geom', cont_per_string, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, 'spatialite')

            if layerQUOTE.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerQUOTE.setCrs(crs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            
            uri.setDataSource('', 'pyarchinit_usm_view', 'the_geom', cont_per_string, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, 'spatialite')
            
            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            if layerUS.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                
                QgsProject.instance().addMapLayers([layerUS], False)
                
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer USM non valido", QMessageBox.Ok)

            

        elif settings.SERVER == 'postgres':
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            
            uri.setDataSource("public", "pyarchinit_quote_usm_view", "the_geom", cont_per_string, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, "postgres")
            if layerQUOTE.isValid():
                #layerQUOTE.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                except Exception as e:
                    pass
            
            uri.setDataSource("public", "pyarchinit_usm_view", "the_geom", cont_per_string, "gid")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, "postgres")
            if layerUS.isValid():
                #layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer USM non valido", QMessageBox.Ok)        
    
    def charge_vector_layers_all_period(self, sito_p, cont_per, per_label, fas_label,dat):
        self.sito_p = sito_p
        self.cont_per = str(cont_per)
        self.per_label = per_label
        self.fas_label = fas_label
        self.dat=dat
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()
        
        
        
        
        groupName="Stratigrafie Orizzontali - %s" % (self.dat)
        root = QgsProject.instance().layerTreeRoot()
       
        group = root.addGroup(groupName)
        
        group.setExpanded(False)    
        
        
        if self.L=='it':
            layer_name_label_us = "Unita Stratigrafiche"
            layer_name_label_quote = "Quote US" 
        elif self.L=='de':
            layer_name_label_us = "Stratigraphischen Einheiten" 
            layer_name_label_quote = "Nivellements der SE"
        else:
            layer_name_label_us = "Stratigraphic Units" 
            layer_name_label_quote = "Elevations SU"

        a=Connection()
        styler = USViewStyler(a)

        # Chiedi lo stile una sola volta
        style_choice = styler.ask_user_style_preference()
        saved_style = None

        for periodo in cont_per:  # Assumiamo che cont_per sia una lista di periodi
            cont_per_string = f"sito = '{sito_p}' AND (cont_per = '{periodo}' OR cont_per LIKE '{periodo}/%' OR cont_per LIKE '%/{periodo}' OR cont_per LIKE '%/{periodo}/%')"

            if settings.SERVER == 'sqlite':
                sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
                db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
                # Open a connection to the SpatiaLite database
                conn = sqlite3.connect(db_file_path)
                cursor = conn.cursor()

                # Extract the SRID from the 'pyarchinit_individui' table
                cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
                srid = cursor.fetchone()[0]

                # Close the database connection
                conn.close()
                uri = QgsDataSourceUri()
                uri.setDatabase(db_file_path)


                #cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"


                uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', cont_per_string, "ROWID")
                layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, 'spatialite')

                if layerQUOTE.isValid():
                    # Create a CRS using a predefined SRID
                    crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                    layerQUOTE.setCrs(crs)
                    # self.USLayerId = layerUS.getLayerID()
                    style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                    layerQUOTE.loadNamedStyle(style_path)
                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', cont_per_string, "ROWID")
                layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, 'spatialite')

                if layerUS.isValid():
                    print(f"Layer US per periodo {periodo} è valido")
                    crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                    layerUS.setCrs(crs)

                    # Applica lo stile
                    if style_choice == "load":
                        if saved_style is None:
                            saved_style = styler.load_style_from_db(layerUS)
                        if saved_style:
                            success = layerUS.loadNamedStyle(saved_style)
                            print(f"Caricamento stile dal database: {'Successo' if success else 'Fallito'}")
                        else:
                            print("Nessuno stile trovato nel database, applico stile di default")
                            styler.apply_style_to_layer(layerUS)
                    elif style_choice == "save" or style_choice == "temp":
                        styler.apply_style_to_layer(layerUS)

                    if style_choice == "save":
                        styler.save_style_to_db(layerUS)
                        style_choice = "load"  # Cambia a "load" per i periodi successivi
                        saved_style = styler.load_style_from_db(layerUS)

                    print("Stile applicato, ora modifico il renderer")

                    # Modifica le regole del renderer
                    renderer = layerUS.renderer()
                    if isinstance(renderer, QgsRuleBasedRenderer):
                        print("Renderer è QgsRuleBasedRenderer")
                        root_rule = renderer.rootRule()

                        new_root_rule = QgsRuleBasedRenderer.Rule(None)

                        for rule in root_rule.children():
                            new_expression = f"({rule.filterExpression()}) AND ({cont_per_string})"
                            new_rule = QgsRuleBasedRenderer.Rule(rule.symbol().clone(), 0, 0, new_expression,
                                                                 rule.label())

                            # Verifica se la nuova regola ha elementi corrispondenti
                            request = QgsFeatureRequest().setFilterExpression(new_expression)
                            matching_features = layerUS.getFeatures(request)
                            if any(True for _ in matching_features):
                                new_root_rule.appendChild(new_rule)

                        new_renderer = QgsRuleBasedRenderer(new_root_rule)
                        layerUS.setRenderer(new_renderer)
                        print("Nuovo renderer creato e applicato")
                    else:
                        print(f"Il renderer non è QgsRuleBasedRenderer, ma {type(renderer)}")

                    # Applica il filtro globale al layer
                    layerUS.setSubsetString(cont_per_string)
                    print(f"Filtro applicato: {cont_per_string}")
                    print(f"Numero di features dopo il filtro: {layerUS.featureCount()}")

                    # Aggiorna il layer
                    layerUS.triggerRepaint()
                    print("Layer aggiornato")

                    group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                    QgsProject.instance().addMapLayers([layerUS], False)
                    print(f"Layer per periodo {periodo} aggiunto al progetto")
                else:
                    print(f"Layer US per periodo {periodo} non è valido")
                    QMessageBox.warning(self, "Pyarchinit", f"Layer US per periodo {periodo} non valido",
                                        QMessageBox.Ok)


            elif settings.SERVER == 'postgres':
                uri = QgsDataSourceUri()
                # set host name, port, database name, username and password
                uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
                cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"

                #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

                uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", cont_per_string, "gid")
                layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, "postgres")
                if layerQUOTE.isValid():
                    #layerQUOTE.setCrs(srs)
                    style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                    layerQUOTE.loadNamedStyle(style_path)
                    try:
                        group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                        QgsProject.instance().addMapLayers([layerQUOTE], False)
                    except Exception as e:
                        pass

                uri.setDataSource("public", "pyarchinit_us_view", "the_geom", cont_per_string, "gid")
                layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, "postgres")
                if layerUS.isValid():
                    print(f"Layer US per periodo {periodo} è valido")


                    # Applica lo stile
                    if style_choice == "load" and saved_style:
                        success = layerUS.loadNamedStyle(saved_style)
                        print(f"Caricamento stile dal database: {'Successo' if success else 'Fallito'}")
                    elif style_choice == "save" or style_choice == "temp":
                        styler.apply_style_to_layer(layerUS)

                    if style_choice == "save":
                        styler.save_style_to_db(layerUS)
                        style_choice = "load"  # Cambia a "load" per i periodi successivi
                        saved_style = styler.load_style_from_db(layerUS)

                    print("Stile applicato, ora modifico il renderer")

                    # Modifica le regole del renderer
                    renderer = layerUS.renderer()
                    if isinstance(renderer, QgsRuleBasedRenderer):
                        print("Renderer è QgsRuleBasedRenderer")
                        root_rule = renderer.rootRule()

                        new_root_rule = QgsRuleBasedRenderer.Rule(None)

                        for rule in root_rule.children():
                            new_expression = f"({rule.filterExpression()}) AND ({cont_per_string})"
                            new_rule = QgsRuleBasedRenderer.Rule(rule.symbol().clone(), 0, 0, new_expression,
                                                                 rule.label())

                            # Verifica se la nuova regola ha elementi corrispondenti
                            request = QgsFeatureRequest().setFilterExpression(new_expression)
                            matching_features = layerUS.getFeatures(request)
                            if any(True for _ in matching_features):
                                new_root_rule.appendChild(new_rule)

                        new_renderer = QgsRuleBasedRenderer(new_root_rule)
                        layerUS.setRenderer(new_renderer)
                        print("Nuovo renderer creato e applicato")
                    else:
                        print(f"Il renderer non è QgsRuleBasedRenderer, ma {type(renderer)}")

                    # Applica il filtro globale al layer
                    layerUS.setSubsetString(cont_per_string)
                    print(f"Filtro applicato: {cont_per_string}")
                    print(f"Numero di features dopo il filtro: {layerUS.featureCount()}")

                    # Aggiorna il layer
                    layerUS.triggerRepaint()
                    print("Layer aggiornato")

                    group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                    QgsProject.instance().addMapLayers([layerUS], False)
                    print(f"Layer per periodo {periodo} aggiunto al progetto")
                else:
                    print(f"Layer US per periodo {periodo} non è valido")
                    QMessageBox.warning(self, "Pyarchinit", f"Layer US per periodo {periodo} non valido",
                                        QMessageBox.Ok)

    def charge_vector_layers_usm_all_period(self, sito_p, cont_per, per_label, fas_label,dat):
        self.sito_p = sito_p
        self.cont_per = str(cont_per)
        self.per_label = per_label
        self.fas_label = fas_label
        self.dat=dat
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()
        
        
        
        
        groupName="Stratigrafie Verticali  - %s" % (self.dat)
        root = QgsProject.instance().layerTreeRoot()
       
        group = root.addGroup(groupName)
        
        group.setExpanded(False)    
        
        
        if self.L=='it':
            layer_name_label_us = "Unita Stratigrafiche Verticali" 
            layer_name_label_quote = "Quote USM"
        elif self.L=='de':
            layer_name_label_us = "Wand Stratigraphischen Einheiten" 
            layer_name_label_quote = "Nivellements der SEW"
        else:
            layer_name_label_us = "Mansory Stratigraphic Units "
            layer_name_label_quote = "Elevations SUW"
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            
            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"
            
            
            uri.setDataSource('', 'pyarchinit_quote_usm_view', 'the_geom', cont_per_string, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, 'spatialite')

            if layerQUOTE.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerQUOTE.setCrs(crs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                QgsProject.instance().addMapLayers([layerQUOTE], False)
            uri.setDataSource('', 'pyarchinit_usm_view', 'the_geom', cont_per_string, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, 'spatialite')

            

            if layerUS.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer USM non valido", QMessageBox.Ok)

            
            
            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

        elif settings.SERVER == 'postgres':
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            
            uri.setDataSource("public", "pyarchinit_quote_usm_view", "the_geom", cont_per_string, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, "postgres")
            if layerQUOTE.isValid():
                #layerQUOTE.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    group.insertChildNode(-1, QgsLayerTreeLayer(layerQUOTE))
                    QgsProject.instance().addMapLayers([layerQUOTE], False)
                except Exception as e:
                    pass
            
            uri.setDataSource("public", "pyarchinit_usm_view", "the_geom", cont_per_string, "gid")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, "postgres")
            if layerUS.isValid():
                #layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer US non valido", QMessageBox.Ok)                    


    def loadMapPreview(self, gidstr):
        """ if has geometry column load to map canvas """
        layerToSet = []
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_DB_folder")
        path_cfg = '{}{}{}'.format(sqlite_DB_path, os.sep, 'config.cfg')
        conf = open(path_cfg, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()

        if settings.SERVER == 'postgres':
            uri_u = QgsDataSourceUri()
            uri_u.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)


            uri_u.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri_u.uri(), "Unita Stratigrafiche in uso", "postgres")


            uri_u.setDataSource("public", "pyarchinit_us_view", "the_geom", "","gid")
            layerUS_us = QgsVectorLayer(uri_u.uri(), "mappa completa", "postgres")

            if layerUS.isValid():

                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_preview.qml')

                style_path_us = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_dot.qml')
                layerUS_us.loadNamedStyle(style_path_us)
                layerUS.loadNamedStyle(style_path)

                QgsProject.instance().addMapLayers([layerUS], False)
                QgsProject.instance().addMapLayers([layerUS_us], False)

                layerToSet.append(layerUS_us)
                layerToSet.append(layerUS)

            return layerToSet

        elif settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri_us = QgsDataSourceUri()
            uri_us.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            uri_us.setDataSource('', 'pyarchinit_us_view', 'the_geom', 'id_us', "ROWID")
            layerUS_us = QgsVectorLayer(uri_us.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS_us.setCrs(crs)
                layerUS.setCrs(crs)
                # QMessageBox.warning(self, "Pyarchinit", "OK ayer US valido",   #QMessageBox.Ok)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_preview.qml')
                layerUS.loadNamedStyle(style_path)
                style_path_us = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_dot.qml')
                layerUS_us.loadNamedStyle(style_path_us)
                QgsProject.instance().addMapLayers([layerUS], False)
                QgsProject.instance().addMapLayers([layerUS_us], False)

                layerToSet.append(layerUS)
                layerToSet.append(layerUS_us)
            else:
                pass
                # QMessageBox.warning(self, "Pyarchinit", "NOT! Layer US not valid",#QMessageBox.Ok)

            return layerToSet

    def loadMapPreview_new(self, gidstr):
        """ if has geometry column load to map canvas """
        layerToSet = []
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_DB_folder")
        path_cfg = '{}{}{}'.format(sqlite_DB_path, os.sep, 'config.cfg')
        conf = open(path_cfg, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()

        style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_preview.qml')# Inizializza ThesaurusStyler

        styler = ThesaurusStyler(style_path)

        if settings.SERVER == 'postgres':
            uri_u = QgsDataSourceUri()
            uri_u.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            uri_u.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri_u.uri(), "Unita Stratigrafiche in uso", "postgres")

            uri_u.setDataSource("public", "pyarchinit_us_view", "the_geom", "", "gid")
            layerUS_us = QgsVectorLayer(uri_u.uri(), "mappa completa", "postgres")

            if layerUS.isValid():
                # Applica lo stile automatico
                d_stratigrafica_field = 'd_stratigrafica'  # Campo nel layer pyarchinit_us_view
                unique_values = layerUS.uniqueValues(layerUS.fields().indexOf(d_stratigrafica_field))

                # Ottieni il mapping tra d_stratigrafica e sigla dal thesaurus
                thesaurus_mapping = self.get_thesaurus_mapping_postgres(uri_u)

                styler.apply_style_to_layer(layerUS, d_stratigrafica_field, thesaurus_mapping)

                # Crea un nuovo simbolo personalizzato per layerUS_us
                symbol = QgsFillSymbol.createSimple({'color': 'transparent', 'outline_color': 'black'})

                # Imposta il contorno punteggiato
                line_layer = QgsSimpleLineSymbolLayer()
                line_layer.setPenStyle(Qt.DotLine)
                line_layer.setColor(QColor('black'))
                line_layer.setWidth(0.5)  # Puoi regolare lo spessore del contorno qui

                # Sostituisci il layer di contorno del simbolo con quello punteggiato
                symbol.changeSymbolLayer(0, line_layer)

                # Crea un nuovo renderer a simbolo singolo con il simbolo personalizzato
                new_renderer = QgsSingleSymbolRenderer(symbol)
                layerUS_us.setRenderer(new_renderer)

                print("Renderer personalizzato applicato a layerUS_us")

                # Imposta l'opacità per layerUS_us
                self.set_layer_opacity(layerUS_us, 0.6)
                self.set_layer_opacity(layerUS, 0.6)

                # Forza l'aggiornamento del layer
                layerUS_us.triggerRepaint()

                QgsProject.instance().addMapLayers([layerUS, layerUS_us], False)

                layerToSet.append(layerUS)
                layerToSet.append(layerUS_us)

            else:
                print("Uno o entrambi i layer non sono validi")

            return layerToSet

        elif settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]
            conn.close()

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri_us = QgsDataSourceUri()
            uri_us.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            uri_us.setDataSource('', 'pyarchinit_us_view', 'the_geom', 'id_us', "ROWID")
            layerUS_us = QgsVectorLayer(uri_us.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS_us.setCrs(crs)
                layerUS.setCrs(crs)

                # Applica lo stile automatico a layerUS
                d_stratigrafica_field = 'd_stratigrafica'
                thesaurus_mapping = self.get_thesaurus_mapping(uri)
                styler.apply_style_to_layer(layerUS, d_stratigrafica_field, thesaurus_mapping)

                # Crea un nuovo simbolo personalizzato per layerUS_us
                symbol = QgsFillSymbol.createSimple({'color': 'transparent', 'outline_color': 'black'})

                # Imposta il contorno punteggiato
                line_layer = QgsSimpleLineSymbolLayer()
                line_layer.setPenStyle(Qt.DotLine)
                line_layer.setColor(QColor('black'))
                line_layer.setWidth(0.5)  # Puoi regolare lo spessore del contorno qui

                # Sostituisci il layer di contorno del simbolo con quello punteggiato
                symbol.changeSymbolLayer(0, line_layer)

                # Crea un nuovo renderer a simbolo singolo con il simbolo personalizzato
                new_renderer = QgsSingleSymbolRenderer(symbol)
                layerUS_us.setRenderer(new_renderer)

                print("Renderer personalizzato applicato a layerUS_us")

                # Imposta l'opacità per layerUS_us
                self.set_layer_opacity(layerUS_us, 0.6)
                self.set_layer_opacity(layerUS, 0.6)

                # Forza l'aggiornamento del layer
                layerUS_us.triggerRepaint()

                QgsProject.instance().addMapLayers([layerUS, layerUS_us], False)

                layerToSet.append(layerUS)
                layerToSet.append(layerUS_us)

            else:
                print("Uno o entrambi i layer non sono validi")

            return layerToSet


    def show_message(self, message):
        """Mostra un messaggio all'utente."""
        QMessageBox.information(None, 'Informazione', message, QMessageBox.Ok)

    def set_layer_opacity(self, layer, opacity):
        """
        Imposta l'opacità per tutti i simboli in un layer, indipendentemente dal tipo di renderer.
        """
        renderer = layer.renderer()
        if isinstance(renderer, QgsRuleBasedRenderer):
            root_rule = renderer.rootRule()
            for rule in root_rule.children():
                symbol = rule.symbol()
                if symbol:
                    symbol.setOpacity(opacity)
        elif hasattr(renderer, 'symbol'):
            symbol = renderer.symbol()
            if symbol:
                symbol.setOpacity(opacity)
        elif isinstance(renderer, QgsCategorizedSymbolRenderer):
            for category in renderer.categories():
                symbol = category.symbol()
                if symbol:
                    symbol.setOpacity(opacity)
        layer.triggerRepaint()

    def get_thesaurus_mapping(self, conn):
        """
        Ottiene il mapping tra sigla_estesa e d_stratigrafica.

        :param conn: Connessione al database
        :return: Dizionario con sigla_estesa come chiave e d_stratigrafica come valore
        """
        mapping = {}
        query = """
        SELECT ts.sigla_estesa, us.d_stratigrafica
        FROM thesaurus_sigle ts
        JOIN pyarchinit_us_view us ON ts.sigla = us.d_stratigrafica
        WHERE ts.nome_tabella = 'us_table'
        """

        try:
            result = conn.execute(query)
            for row in result:
                mapping[row['sigla_estesa']] = row['d_stratigrafica']
        except Exception as e:
            print(f"Errore nell'esecuzione della query: {e}")
            # Qui potresti voler gestire l'errore in modo più appropriato

        return mapping

    def get_thesaurus_mapping_postgres(self, uri):
        """
        Ottiene il mapping tra d_stratigrafica e sigla dal thesaurus per PostgreSQL usando solo QGIS.

        :param uri: QgsDataSourceUri configurato per la connessione PostgreSQL
        :return: Dizionario con d_stratigrafica come chiave e sigla_estesa come valore
        """
        mapping = {}

        # Crea una copia dell'uri per non modificare quello originale
        query_uri = QgsDataSourceUri(uri.uri())

        # Imposta la query SQL
        sql = """
        SELECT ts.sigla_estesa, us.d_stratigrafica
        FROM thesaurus_sigle ts
        JOIN pyarchinit_us_view us ON ts.sigla_estesa = us.d_stratigrafica
        WHERE ts.nome_tabella = 'us_table'
        """
        query_uri.setDataSource("public", f"({sql})", None, "", "id")

        # Crea un layer temporaneo con i risultati della query
        layer = QgsVectorLayer(query_uri.uri(), "thesaurus_mapping", "postgres")

        if layer.isValid():
            features = layer.getFeatures()
            for feature in features:
                sigla_estesa = feature['sigla_estesa']
                d_stratigrafica = feature['d_stratigrafica']
                mapping[d_stratigrafica] = sigla_estesa
        else:
            print("Errore nel caricamento del layer per il mapping del thesaurus")

        return mapping

    def loadMapPreviewReperti(self, gidstr):
        """ if has geometry column load to map canvas """
        layerToSet = []
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_DB_folder")
        path_cfg = '{}{}{}'.format(sqlite_DB_path, os.sep, 'config.cfg')
        conf = open(path_cfg, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()

        if settings.SERVER == 'postgres':
            uri_u = QgsDataSourceUri()
            uri_u.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)


            uri_u.setDataSource("public", "rep", "the_geom", gidstr, "id_invmat")
            layerUS = QgsVectorLayer(uri_u.uri(), "vv", "postgres")


            uri_u.setDataSource("public", "pyarchinit_us_view", "the_geom", '',"gid")
            layerUS_us = QgsVectorLayer(uri_u.uri(), "mappa completa", "postgres")

            if layerUS.isValid():

                #style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_preview.qml')

                #style_path_us = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_dot.qml')
                #layerUS_us.loadNamedStyle(style_path_us)
                #layerUS_us.loadNamedStyle(style_path)

                QgsProject.instance().addMapLayers([layerUS, layerUS_us], False)
                #QgsProject.instance().addMapLayers([layerUS_us], False)


                layerToSet.append(layerUS)
                #layerToSet.append(layerUS_us)

            return layerToSet

        elif settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri_us = QgsDataSourceUri()
            uri_us.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            uri_us.setDataSource('', 'pyarchinit_us_view', 'the_geom', 'id_us', "ROWID")
            layerUS_us = QgsVectorLayer(uri_us.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS_us.setCrs(crs)
                layerUS.setCrs(crs)
                # QMessageBox.warning(self, "Pyarchinit", "OK ayer US valido",   #QMessageBox.Ok)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_preview.qml')
                layerUS.loadNamedStyle(style_path)
                style_path_us = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view_dot.qml')
                layerUS_us.loadNamedStyle(style_path_us)
                QgsProject.instance().addMapLayers([layerUS], False)
                QgsProject.instance().addMapLayers([layerUS_us], False)

                layerToSet.append(layerUS)
                layerToSet.append(layerUS_us)
            else:
                pass
                # QMessageBox.warning(self, "Pyarchinit", "NOT! Layer US not valid",#QMessageBox.Ok)

            return layerToSet
    def loadMapPreviewDoc(self,docstr):
        """ if has geometry column load to map canvas """
        layerToSet = []
        #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_DB_folder")
        path_cfg = '{}{}{}'.format(sqlite_DB_path, os.sep, 'config.cfg')
        conf = open(path_cfg, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()

        if settings.SERVER == 'postgres':
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            # docstr =  docstr
            #docstr = ' "nome_doc" = \'A-B\' '
            # layerUS
            ##          uri.setDataSource("public", "pyarchinit_us_view", "the_geom", sing_layer, "id_us")
            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", docstr, "id_us")
            layerUS = QgsVectorLayer(uri.uri(), "pyarchinit_doc_view_b", "postgres")

            if layerUS.isValid():
                #QMessageBox.warning(self, "WARNING", "OK layer ", QMessageBox.Ok)
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                layerToSet.append(layerUS)
            else:
                QMessageBox.warning(self, "WARNING", " Layer not valid", QMessageBox.Ok)

                # layerQuote
            ##          uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "id_us")
            ##          layerQUOTE = QgsVectorLayer(uri.uri(), "Quote", "postgres")

            ##          if layerQUOTE.isValid() == True:
            ##              #style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
            ##              #layerQUOTE.loadNamedStyle(style_path)
            ##              QgsProject.instance().addMapLayers([layerQUOTE], False)
            ##              layerToSet.append(QgsMapCanvas(layerQUOTE, True, False))

            return layerToSet

        elif settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            # docstr =  docstr
            #docstr = ' "nome_doc" = \'A-B\' '

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', docstr, "ROWID")

            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK ayer US valido", QMessageBox.Ok)
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                layerToSet.append(layerUS)
            else:
                QMessageBox.warning(self, "Pyarchinit", "NOT! Layer US not valid", QMessageBox.Ok)

            

            return layerToSet

    """
    def addRasterLayer(self):
        fileName = "/rimini_1_25000/Rimini_25000_g.tif"
        fileInfo = QFileInfo(fileName)
        baseName = fileInfo.baseName()
        rlayer = QgsRasterLayer(fileName, baseName)

        if not rlayer.isValid():
            #QMessageBox.warning(self, "Pyarchinit", "PROBLEMA DI CARICAMENTO RASTER" + str(baseName),   #QMessageBox.Ok)

        srs = QgsCoordinateReferenceSystem(3004, QgsCoordinateReferenceSystem.PostgisCrsId)
        rlayer.setCrs(srs)
        # add layer to the registry
        QgsProject.instance().addMapLayers(rlayer);

        self.canvas = QgsMapCanvas()
        self.canvas.setExtent(rlayer.extent())

        # set the map canvas layer set
        cl = QgsMapCanvas(rlayer)
        layers = [cl]
        self.canvas.setLayers(layers)
    """

    # iface custom methods
    def dataProviderFields(self):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        fields = self.iface.mapCanvas().currentLayer().dataProvider().fields()
        return fields

    def selectedFeatures(self):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        selected_features = self.iface.mapCanvas().currentLayer().selectedFeatures()
        return selected_features

    def findFieldFrDict(self, fn):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        ##non funziona piu dopo changelog
        self.field_name = fn
        fields_dict = self.dataProviderFields()
        res=None
        for k in fields_dict:
            if fields_dict[k].name() == self.field_name:
                res = k
        return res

    def findItemInAttributeMap(self, fp, fl):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        ##non funziona piu dopo changelog
        self.field_position = fp
        self.features_list = fl
        value_list = []
        for item in self.iface.mapCanvas().currentLayer().selectedFeatures():
            value_list.append(item.attributeMap().__getitem__(self.field_position).toString())
        return value_list

    ###################### - Site Section - ########################
    def charge_layers_for_draw(self, options):
        self.options = options

        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        if self.L=='it':
            groupName="Layer Archeologici"
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup(groupName)
            group.setExpanded(False)
            myGroup1 = group.insertGroup(1, "Riferimenti di localizzazione")
            myGroup2 = group.insertGroup(2, "Linee di riferimento")        
            myGroup3 = group.insertGroup(3, "Ingombri")
            
        else:
            groupName="Archaeological layer"
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup(groupName)
            group.setExpanded(False)
            myGroup1 = group.insertGroup(1, "Place reference")
            myGroup2 = group.insertGroup(2, "Lines refernces")        
            myGroup3 = group.insertGroup(3, "Space requirements")
            
        
        #myGroup4 = group.insertGroup(4, "Base Map")
        myGroup1.setExpanded(False)
        myGroup2.setExpanded(False)
        myGroup3.setExpanded(False)
        #myGroup4.setExpanded(False)    


        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_individui'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()

            layer_name = 'pyarchinit_individui'
            layer_name_conv = "'" + str(layer_name) + "'"

            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)

            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"

            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)

                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_linee_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_punti_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_campionature'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_documentazione'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyunitastratigrafiche'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)
            
            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
                
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            
            
            layer_name = 'pyunitastratigrafiche_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)
            
            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
                
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            
            
            layer_name = 'pyarchinit_strutture_ipotesi'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_reperti'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"siti = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_siti'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_nome = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
                
            layer_name = 'pyarchinit_tafonomia'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)    
            
            
            layer_name = 'pyarchinit_siti_polygonal'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_id = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_us_negative_doc'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_n = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            
            layer_name = 'pyarchinit_ripartizioni_spaziali'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_rs = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_sezioni'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"siti = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            layer_name = 'pyarchinit_individui'
            layer_name_conv = "'" + str(layer_name) + "'"
            ##value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_linee_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_punti_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_campionature'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_documentazione'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyunitastratigrafiche'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyunitastratigrafiche_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_strutture_ipotesi'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_reperti'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"siti = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_siti'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_nome = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
                
            layer_name = 'pyarchinit_tafonomia'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)    
            
            
            layer_name = 'pyarchinit_siti_polygonal'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_id = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_us_negative_doc'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_n = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            
            layer_name = 'pyarchinit_ripartizioni_spaziali'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"sito_rs = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_sezioni'
            layer_name_conv = "'" + str(layer_name) + "'"
            #value_conv = ('"siti = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
    
    
    def charge_sites_geometry(self, options, col, val):
        self.options = options
        self.col = col
        self.val = val

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        if self.L=='it':
            groupName="Layer Archeologici(%s)"%(val)
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup(groupName)
            group.setExpanded(False)
            myGroup1 = group.insertGroup(1, "Riferimenti di localizzazione")
            myGroup2 = group.insertGroup(2, "Linee di riferimento")        
            myGroup3 = group.insertGroup(3, "Ingombri")
            
        else:
            groupName="Archaeological layer(%s)"%(val)
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup(groupName)
            group.setExpanded(False)
            myGroup1 = group.insertGroup(1, "Place reference")
            myGroup2 = group.insertGroup(2, "Lines refernces")        
            myGroup3 = group.insertGroup(3, "Space requirements")
        myGroup1.setExpanded(False)
        myGroup2.setExpanded(False)
        myGroup3.setExpanded(False)
        #myGroup4.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_individui'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()




            layer_name = 'pyarchinit_individui'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)

                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_linee_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_punti_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_campionature'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_documentazione'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyunitastratigrafiche'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            
            layer_name = 'pyunitastratigrafiche_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_strutture_ipotesi'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_reperti'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"siti = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_siti'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_nome = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
                
            layer_name = 'pyarchinit_tafonomia'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)    
            
            
            layer_name = 'pyarchinit_siti_polygonal'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_id = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_us_negative_doc'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_n = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            
            layer_name = 'pyarchinit_ripartizioni_spaziali'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_rs = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_sezioni'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # Create a CRS using the SRID we extracted
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layer.setCrs(crs)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            layer_name = 'pyarchinit_individui'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_linee_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_punti_rif'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_campionature'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            layer_name = 'pyarchinit_documentazione'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyunitastratigrafiche'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            
            layer_name = 'pyunitastratigrafiche_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"scavo_s = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)

            layer_name = 'pyarchinit_quote_usm'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_q = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            
            
            layer_name = 'pyarchinit_strutture_ipotesi'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_reperti'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"siti = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_siti'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_nome = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
                
            layer_name = 'pyarchinit_tafonomia'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)    
            
            
            layer_name = 'pyarchinit_siti_polygonal'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_id = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_us_negative_doc'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_n = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
            
            layer_name = 'pyarchinit_ripartizioni_spaziali'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito_rs = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_sezioni'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"sito = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer not valid", QMessageBox.Ok)
            
            
    def charge_sites_from_research(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Localizzazione Sito archeologico"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]

            # Close the database connection
            conn.close()
            gidstr = "sito_nome= '" + str(data[0].sito) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR sito_nome = '" + str(data[i].sito) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_site_view', 'the_geom', gidstr, "ROWID")
            layerSITE = QgsVectorLayer(uri.uri(), 'pyarchinit_site_view', 'spatialite')

            if layerSITE.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerSITE.setCrs(crs)

                self.iface.mapCanvas().setExtent(layerSITE.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerSITE))
                QgsProject.instance().addMapLayers([layerSITE], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer US non valido", QMessageBox.Ok)


        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "sito_nome= '" + str(data[0].sito) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR sito_nome = '" + str(data[i].sito) + "'"

            uri.setDataSource('', 'pyarchinit_site_view', 'the_geom', gidstr, "gid")
            layerSITE = QgsVectorLayer(uri.uri(), 'pyarchinit_site_view', 'postgres')

            if layerSITE.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer Sito valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerSITE.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerSITE))
                QgsProject.instance().addMapLayers([layerSITE], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer US non valido", QMessageBox.Ok)
    def charge_reperti_layers(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View scheda Reperti"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if self.L=='it':
            name_layer='Reperti view'
        elif self.L=='de':
            name_layer='ArtefaKt view'
        else:
            name_layer='Artefact view'
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]
            gidstr = "numero_inventario = '" + str(data[0].numero_inventario) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR numero_inventario = '" + str(data[i].numero_inventario) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_reperti_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, 'spatialite')

            if layerUS.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)

                

                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valid", QMessageBox.Ok)    
            

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "numero_inventario = " + str(data[0].numero_inventario)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR numero_inventario = " + str(data[i].numero_inventario)

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_reperti_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, "postgres")

            if layerUS.isValid():
                #layerUS.setCrs(srs)
                
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
           
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valid", QMessageBox.Ok)
    
    def charge_tomba_layers(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View scheda Tomba"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if self.L=='it':
            name_layer='Tomba view'
        elif self.L=='de':
            name_layer='ArtefaKt view'
        else:
            name_layer='Artefact view'
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]
            gidstr = "nr_scheda_taf = '" + str(data[0].nr_scheda_taf) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR nr_scheda_taf = '" + str(data[i].nr_scheda_taf) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_tomba_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, 'spatialite')

            if layerUS.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerUS.setCrs(crs)

                #QMessageBox.warning(self, "Pyarchinit", "OK Layer US valido", QMessageBox.Ok)

                

                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valid", QMessageBox.Ok)    
            

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "nr_scheda_taf = " + str(data[0].nr_scheda_taf)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR nr_scheda_taf = " + str(data[i].nr_scheda_taf)

            #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_tomba_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, "postgres")

            if layerUS.isValid():
                #layerUS.setCrs(srs)
                
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
           
            else:
                QMessageBox.warning(self, "Pyarchinit", "OK Layer not valid", QMessageBox.Ok)
    
    #def dothejob(group_name):
        

        #dothejob()
    
    
    def charge_vector_layers_all_st(self, sito_p,sigla_st,n_st):
        self.sito_p = sito_p
        self.sigla_st = sigla_st
        self.n_st = str(n_st)
        #self.dothejob()

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View scheda Struttura  - Sigla: %s / Num: %s" % (self.sigla_st, self.n_st)
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]
            string = "sito = '" + self.sito_p + "' AND  sigla_struttura = '" + self.sigla_st + "' AND numero_struttura= '" + self.n_st + "'"
            
            #gidstr = "id_struttura = '" + str(self.data[0].id_struttura) + "'"
            # if len(data) > 1:
                # for i in range(len(data)):
                    # gidstr += " OR id_struttura = '" + str(data[i].id_struttura) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_strutture_view', 'the_geom', string, "ROWID")
            layerSTRUTTURA = QgsVectorLayer(uri.uri(), 'pyarchinit_strutture_view', 'spatialite')

            if layerSTRUTTURA.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerSTRUTTURA.setCrs(crs)

                #QMessageBox.warning(self, "Pyarchinit", "OK Layer Struttura valido", QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layerSTRUTTURA.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerSTRUTTURA))
                QgsProject.instance().addMapLayers([layerSTRUTTURA], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Struttura non valido", QMessageBox.Ok)

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            string = "sito = '" + self.sito_p + "' AND  sigla_struttura = '" + self.sigla_st + "' AND numero_struttura= '" + self.n_st + "'"

            uri.setDataSource("public", 'pyarchinit_strutture_view', 'the_geom', string, "gid")
            layerSTRUTTURA = QgsVectorLayer(uri.uri(), 'pyarchinit_strutture_view', 'postgres')

            if layerSTRUTTURA.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer Struttura valido", QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layerSTRUTTURA.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerSTRUTTURA))
                QgsProject.instance().addMapLayers([layerSTRUTTURA], False)
            else:
                pass#QMessageBox.warning(self, "Pyarchinit", "Layer Struttura non valido", QMessageBox.Ok)

    
    def charge_structure_from_research(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View scheda Struttura"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]
            gidstr = "id_struttura = '" + str(data[0].id_struttura) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_struttura = '" + str(data[i].id_struttura) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_strutture_view', 'the_geom', gidstr, "ROWID")
            layerSTRUTTURA = QgsVectorLayer(uri.uri(), 'pyarchinit_strutture_view', 'spatialite')

            if layerSTRUTTURA.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerSTRUTTURA.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer Struttura valido", QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layerSTRUTTURA.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerSTRUTTURA))
                QgsProject.instance().addMapLayers([layerSTRUTTURA], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Struttura non valido", QMessageBox.Ok)

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "id_struttura = '" + str(data[0].id_struttura) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_struttura = '" + str(data[i].id_struttura) + "'"

            uri.setDataSource("public", 'pyarchinit_strutture_view', 'the_geom', gidstr, "gid")
            layerSTRUTTURA = QgsVectorLayer(uri.uri(), 'pyarchinit_strutture_view', 'postgres')

            if layerSTRUTTURA.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer Struttura valido", QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layerSTRUTTURA.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerSTRUTTURA))
                QgsProject.instance().addMapLayers([layerSTRUTTURA], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Struttura non valido", QMessageBox.Ok)
    
    def charge_individui_from_research(self, data):
        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View scheda Individui"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            # Open a connection to the SpatiaLite database
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            # Extract the SRID from the 'pyarchinit_individui' table
            cursor.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_siti'")
            srid = cursor.fetchone()[0]
            gidstr = "id_scheda_ind = '" + str(data[0].id_scheda_ind) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_scheda_ind = '" + str(data[i].id_scheda_ind) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_individui_view', 'the_geom', gidstr, "ROWID")
            layerIndividui = QgsVectorLayer(uri.uri(), 'pyarchinit_individui_view', 'spatialite')

            if layerIndividui.isValid():
                # Create a CRS using a predefined SRID
                crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                layerIndividui.setCrs(crs)
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer Individui valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Individui non valido", QMessageBox.Ok)

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "id_scheda_ind = '" + str(data[0].id_scheda_ind) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_scheda_ind = '" + str(data[i].id_scheda_ind) + "'"



            uri.setDataSource('public', 'pyarchinit_individui_view', 'the_geom', gidstr, "gid")
            layerIndividui = QgsVectorLayer(uri.uri(), 'pyarchinit_individui_view', 'postgres')

            if layerIndividui.isValid():
                #QMessageBox.warning(self, "Pyarchinit", "OK Layer Individui valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
            else:
                QMessageBox.warning(self, "Pyarchinit", "Layer Individui non valido", QMessageBox.Ok)

    def unique_layer_name(self,base_name):
        '''
        funzione per creare un nome unico alle view quando vengono caricate
        '''

        project = QgsProject.instance()
        i = 1
        new_name = base_name
        while project.mapLayersByName(new_name):
            i += 1
            new_name = f"{base_name}_{i}"
        return new_name
    
    
    
    
    def internet_on(self):
        try:
            urllib.request.urlopen('https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities', timeout=0.5)
            return True
        except urllib.error.URLError:
            
            return False

class Order_layer_v2(object):
    MAX_LOOP_COUNT = 10
    order_dict = {}
    order_count = 0
    db = ''
    L=QgsSettings().value("locale/userLocale")[0:2]
    SITO = ""
    AREA = ""

    def __init__(self, dbconn, SITOol, AREAol):
        self.db = dbconn
        self.SITO = SITOol
        self.AREA = AREAol


    def center_on_screen(self, widget):
        frame_gm = widget.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        widget.move(frame_gm.topLeft())

    def main_order_layer(self):
        """

        This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

        Returns:
        - order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 1000.
        - "error" (str): If the order_count is greater than or equal to 1000 or if the execution time exceeds 60 seconds.

        """
        # ricava la base delle us del matrix a cui non succedono altre US

        #progress_dialog = ProgressDialog()
        matrix_us_level = self.find_base_matrix()
        #result = None

        self.insert_into_dict(matrix_us_level)
        #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(matrix_us_level), QMessageBox.Ok)
        test = 0
        start_time = time.time()
        error_occurred = False
        cycle_count = 0

        # Set the maximum value of the progress bar
        #progress_bar.setMaximum(1000)
        try:
            while test == 0:
                # your code here
                cycle_count += 1

                # Check for error
                if error_occurred:
                    print("An error occurred!")
                    break

                # Check for cycle count
                if cycle_count > 1000:
                    print("Maximum cycle count reached!")
                    break

                rec_list_str = []
                for i in matrix_us_level:
                    rec_list_str.append(str(i))
                    # cerca prima di tutto se ci sono us uguali o che si legano alle US sottostanti
                #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(rec_list_str), QMessageBox.Ok)
                if self.L=='it':
                    value_list_equal = self.create_list_values(['Uguale a', 'Si lega a', 'Same as','Connected to'], rec_list_str, self.AREA, self.SITO)
                elif self.L=='de':
                    value_list_equal = self.create_list_values(["Entspricht", "Bindet an"], rec_list_str, self.AREA, self.SITO)
                else:
                    value_list_equal = self.create_list_values(['Same as','Connected to'], rec_list_str, self.AREA, self.SITO)

                res = self.db.query_in_contains(value_list_equal, self.SITO, self.AREA)

                matrix_us_equal_level = []
                for r in res:
                    matrix_us_equal_level.append(str(r.us))
                #QMessageBox.information(None, 'matrix_us_equal_level', f"{value_list_equal}")
                if matrix_us_equal_level:
                    self.insert_into_dict(matrix_us_equal_level, 1)

                rec = rec_list_str+matrix_us_equal_level#rec_list_str+
                if self.L=='it':
                    value_list_post = self.create_list_values(['>>','Copre', 'Riempie', 'Taglia', 'Si appoggia a','Covers','Fills','Cuts','Abuts'], rec,self.AREA, self.SITO)
                elif self.L=='de':
                    value_list_post = self.create_list_values(['>>','Liegt über','Verfüllt','Schneidet','Stützt sich auf'], rec,self.AREA, self.SITO)
                else:
                    value_list_post = self.create_list_values(['>>','Covers','Fills','Cuts','Abuts'], rec,self.AREA, self.SITO)

                #QMessageBox.information(None, 'value_list_post', f"{value_list_post}", QMessageBox.Ok)
                #try:
                res_t = self.db.query_in_contains(value_list_post, self.SITO, self.AREA)
                matrix_us_level = []
                for e in res_t:
                    #QMessageBox.information(None, "res_t", f"{e}", QMessageBox.Ok)
                    matrix_us_level.append(str(e.us))

                if not matrix_us_level or self.order_count >= 1000 or time.time() - start_time > 90:
                    test = 1

                    return self.order_dict if self.order_count < 1000 else "error"

                else:
                    self.insert_into_dict(matrix_us_level, 1)
            #progress_dialog.closeEvent(Ignore)

        except Exception as e:
            QMessageBox.warning(self, "Attenzione", "La lista delle us generate supera il limite depth max 1000."
                                                    " usare Postgres per generare l'order layer"+str(e), QMessageBox.Ok)


    def find_base_matrix(self):
        res = self.db.select_not_like_from_db_sql(self.SITO, self.AREA)
        
        rec_list = []
        for rec in res:
            rec_list.append(str(rec.us))
        #QMessageBox.warning(None, "Messaggio", "find base_matrix by sql" + str(rec_list), QMessageBox.Ok)
        return rec_list

    def create_list_values(self, rapp_type_list, value_list, ar, si):
        self.rapp_type_list = rapp_type_list
        self.value_list = value_list
        self.ar = ar
        self.si = si

        value_list_to_find = []
        #QMessageBox.warning(None, "rapp1", str(self.rapp_type_list) + '-' + str(self.value_list), QMessageBox.Ok)
        for sing_value in self.value_list:
            for sing_rapp in self.rapp_type_list:

                sql_query_string = "['%s', '%s', '%s', '%s']" % (sing_rapp, sing_value, self.ar, self.si)  # funziona!!!

                value_list_to_find.append(sql_query_string)

        #QMessageBox.warning(None, "rapp1", str(value_list_to_find), QMessageBox.Ok)
        return value_list_to_find

    def us_extractor(self, res):
        self.res = res
        rec_list = []
        for rec in self.res:
            rec_list.append(rec.us)
        return rec_list

    def insert_into_dict(self, base_matrix, v=0):
        self.base_matrix = base_matrix
        if v == 1:
            self.remove_from_list_in_dict(self.base_matrix)
        self.order_dict[self.order_count] = self.base_matrix
        self.order_count += 1  # aggiunge un nuovo livello di ordinamento ad ogni passaggio

    def insert_into_dict_equal(self, base_matrix, v=0):
        self.base_matrix = base_matrix
        if v == 1:
            self.remove_from_list_in_dict(self.base_matrix)
        self.order_dict[self.order_count] = self.base_matrix
        self.order_count += 1  # aggiunge un nuovo livello di ordinamento ad ogni passaggio

    def remove_from_list_in_dict(self, curr_base_matrix):
        self.curr_base_matrix = curr_base_matrix

        for k, v in list(self.order_dict.items()):
            l = v
            # print self.curr_base_matrix
            for i in self.curr_base_matrix:
                try:
                    l.remove(str(i))
                except:
                    pass
            self.order_dict[k] = l
        return


class MyError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ProgressDialog:
    def __init__(self):
        self.progressDialog = QProgressDialog()
        self.progressDialog.setWindowTitle("Aggiornamento rapporti area e sito")
        self.progressDialog.setLabelText("Inizializzazione...")
        #self.progressDialog.setCancelButtonText("")  # Disallow cancelling
        self.progressDialog.setRange(0, 0)
        self.progressDialog.setModal(True)
        self.progressDialog.show()

    def setValue(self, value):
        self.progressDialog.setValue(value)
        if value < value +1:  # Assuming that 100 is the maximum value
            self.progressDialog.setLabelText(f"Aggiornamento in corso... {value}")
        else:
            self.progressDialog.setLabelText("Finito")
            #self.progressDialog.close()


    def closeEvent(self, event):
        self.progressDialog.close()
        event.ignore()