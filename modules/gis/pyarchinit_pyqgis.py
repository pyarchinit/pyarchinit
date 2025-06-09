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

from qgis.core import *
from qgis.gui import *
# Importazioni necessarie
from qgis.PyQt.QtWidgets import (QProgressBar, QApplication, QMessageBox,
                                 QWidget, QVBoxLayout, QTextEdit, QPushButton,
                                 QHBoxLayout, QLabel)
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QFont

import time
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

class Order_layer_v2_old(object):
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
        - order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
        - "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.
        """
        # Importazioni necessarie
        from qgis.PyQt.QtWidgets import QProgressBar, QApplication, QMessageBox
        from qgis.PyQt.QtCore import Qt
        import time

        # Variabili per il controllo dell'esecuzione
        max_cycles = 3000
        max_time = 90  # secondi

        # Azzera order_count se esiste per evitare valori residui da chiamate precedenti
        if hasattr(self, 'order_count'):
            self.order_count = 0
        else:
            self.order_count = 0

        # Resetta order_dict se esiste
        if hasattr(self, 'order_dict'):
            self.order_dict = {}
        else:
            self.order_dict = {}

        # Crea una progress bar più semplice che si aggiorna meno frequentemente
        progress = QProgressBar()
        progress.setWindowTitle("Generazione ordine stratigrafico")
        progress.setGeometry(300, 300, 400, 40)
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(True)
        progress.setFormat("Inizializzazione...")

        try:
            # Utilizziamo la classe Qt di QGIS
            progress.setWindowModality(Qt.WindowModal)
            progress.setAlignment(Qt.AlignCenter)
        except AttributeError:
            pass

        progress.show()
        QApplication.processEvents()
        time.sleep(0.2)  # Pausa per assicurarsi che la UI si aggiorni

        # Controlla se siamo connessi a SQLite
        is_sqlite = False
        try:
            if 'sqlite' in str(self.db.engine.url).lower():
                is_sqlite = True
                print("Rilevata connessione SQLite")
        except:
            print("Impossibile determinare il tipo di database")

        try:
            # Fase 1: Trova la base del matrix
            progress.setValue(10)
            progress.setFormat("Ricerca base matrix...")
            QApplication.processEvents()

            matrix_us_level = self.find_base_matrix()
            if not matrix_us_level:
                progress.setValue(100)
                progress.setFormat("Nessuna base matrix trovata!")
                QApplication.processEvents()
                time.sleep(1)
                progress.close()
                QMessageBox.warning(None, "Attenzione", "Nessuna US di base trovata per iniziare il matrix!")
                return "error"

            progress.setValue(15)
            progress.setFormat("Inserimento dati iniziali...")
            QApplication.processEvents()

            # Inseriamo i dati iniziali nel dizionario
            self.insert_into_dict(matrix_us_level)
            print(f"Inseriti {len(matrix_us_level)} record iniziali nel dizionario")

            # Variabili per il ciclo principale
            test = 0
            start_time = time.time()
            cycle_count = 0

            progress.setValue(20)
            progress.setFormat("Avvio elaborazione...")
            QApplication.processEvents()
            time.sleep(0.2)

            # Array per monitorare quando aggiornare la UI
            update_cycles = [1, 5, 10, 25, 50, 100, 200, 500, 1000, 1500, 2000, 2500, 3000]

            # Ciclo principale
            while test == 0:
                cycle_count += 1

                # Aggiorna progress bar solo in cicli specifici o ogni 100 cicli dopo i primi 500
                should_update = (cycle_count in update_cycles) or (cycle_count > 500 and cycle_count % 100 == 0)

                if should_update:
                    # Calcola percentuale basata sul numero di cicli
                    progress_percentage = 20 + min(75, (cycle_count / max_cycles) * 75)
                    progress.setValue(int(progress_percentage))
                    progress.setFormat(f"Ciclo {cycle_count}/{max_cycles} ({int(progress_percentage)}%)")
                    QApplication.processEvents()
                    print( f"Ciclo {cycle_count}: order_count = {self.order_count}")

                # Ottieni tutti gli elementi US nel dizionario corrente
                rec_list_str = []
                for i in matrix_us_level:
                    rec_list_str.append(str(i))

                # Cerca US che sono uguali o si legano alle US esistenti
                if self.L == 'it':
                    value_list_equal = self.create_list_values(['Uguale a', 'Si lega a', 'Same as', 'Connected to'],
                                                               rec_list_str, self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_equal = self.create_list_values(["Entspricht", "Bindet an"], rec_list_str, self.AREA,
                                                               self.SITO)
                else:
                    value_list_equal = self.create_list_values(['Same as', 'Connected to'], rec_list_str, self.AREA,
                                                               self.SITO)

                # Ottieni i risultati usando la funzione appropriate
                #try:
                res = self.db.query_in_contains(value_list_equal, self.SITO, self.AREA)
                # except Exception as e:
                #     print( f"query_in_contains fallita: {str(e)}")
                #     if is_sqlite:
                #         try:
                #             res = self.db.query_in_contains_onlysqlite(value_list_equal, self.SITO, self.AREA)
                #         except Exception as e2:
                #             print( f"Anche query_in_contains_onlysqlite fallita: {str(e2)}")
                #             res = []
                #     else:
                #         res = []

                # Elabora i risultati per i legami uguali
                matrix_us_equal_level = []
                for r in res:
                    matrix_us_equal_level.append(str(r.us))

                # Aggiungi i risultati al dizionario se ce ne sono
                if matrix_us_equal_level:
                    self.insert_into_dict(matrix_us_equal_level, 1)
                    #if should_update:
                        #print( f"Ciclo {cycle_count}: Aggiunti {len(matrix_us_equal_level)} elementi 'equal'")

                # Combina le liste per la prossima ricerca
                rec = rec_list_str + matrix_us_equal_level

                # Cerca US che sono coperti, riempiti, ecc.
                if self.L == 'it':
                    value_list_post = self.create_list_values(
                        ['>>', 'Copre', 'Riempie', 'Taglia', 'Si appoggia a', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                        self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_post = self.create_list_values(
                        ['>>', 'Liegt über', 'Verfüllt', 'Schneidet', 'Stützt sich auf'], rec, self.AREA, self.SITO)
                else:
                    value_list_post = self.create_list_values(['>>', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                                                              self.AREA, self.SITO)

                # Ottieni i risultati usando la funzione appropriate
                #try:
                res_t = self.db.query_in_contains(value_list_post, self.SITO, self.AREA)
                # except Exception as e:
                #     print( f"query_in_contains fallita: {str(e)}")
                #     if is_sqlite:
                #         try:
                #             res_t = self.db.query_in_contains_onlysqlite(value_list_post, self.SITO, self.AREA)
                #         except Exception as e2:
                #             print( f"Anche query_in_contains_onlysqlite fallita: {str(e2)}")
                #             res_t = []
                #     else:
                #         res_t = []

                # Elabora i risultati
                matrix_us_level = []
                for e in res_t:
                    matrix_us_level.append(str(e.us))

                # Controlla se è il momento di terminare
                elapsed_time = time.time() - start_time
                if not matrix_us_level or self.order_count >= max_cycles or elapsed_time > max_time:
                    test = 1

                    # Aggiorna la progress bar al 100%
                    progress.setValue(100)

                    if not matrix_us_level:
                        progress.setFormat(f"Completato! Cicli: {cycle_count}, Record: {self.order_count}")
                    elif self.order_count >= max_cycles:
                        progress.setFormat(f"Limite di record raggiunto: {self.order_count}")
                    elif elapsed_time > max_time:
                        progress.setFormat(f"Tempo massimo superato: {int(elapsed_time)}s")

                    QApplication.processEvents()
                    time.sleep(1)
                    progress.close()

                    print( f"Completato! order_count = {self.order_count}, order_dict size = {len(self.order_dict)}")

                    if self.order_count < max_cycles:
                        return self.order_dict
                    else:
                        return "error"
                else:
                    # Aggiungi i nuovi elementi al dizionario
                    previous_count = self.order_count
                    self.insert_into_dict(matrix_us_level, 1)
                    if should_update and (self.order_count > previous_count):
                        print( f"Ciclo {cycle_count}: Aggiunti {self.order_count - previous_count} nuovi elementi")

            # Questa parte non dovrebbe mai essere raggiunta, ma per sicurezza:
            progress.close()
            return self.order_dict if self.order_count < max_cycles else "error"

        except Exception as e:
            # Gestione degli errori
            error_msg = str(e)
            QMessageBox.information(None, "Avviso", f"Errore nell'elaborazione: {error_msg}")

            progress.setValue(100)
            short_error = error_msg[:30] + "..." if len(error_msg) > 30 else error_msg
            progress.setFormat(f"Errore: {short_error}")
            QApplication.processEvents()
            time.sleep(1)
            progress.close()

            QMessageBox.warning(None, "Attenzione",
                                f"Errore durante la generazione dell'order layer: {error_msg}\n" +
                                "La lista delle us generate supera il limite o si è verificato un errore.\n" +
                                "Usare Postgres per generare l'order layer")
            return "error"


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


class Order_layer_v2_new(object):
    """
    Classe per l'ordinamento degli strati stratigrafici (US) in un contesto GIS, che supporta la normalizzazione
    personalizzata e l'ordinamento dei valori US, costruendo matrix ordinate e gestendo le query del database per le
    relazioni tra gli strati. Si integra con i componenti dell'interfaccia utente di QGIS per il feedback sul progresso
    e supporta sia i backend SQLite che Postgres. I metodi includono la normalizzazione, la creazione di chiavi di
    ordinamento personalizzate, la costruzione di matrix e la gestione degli errori.

    ## Principali miglioramenti apportati:
    1. Metodo `create_custom_sort_key()`: Crea chiavi di ordinamento personalizzate che gestiscono diversi pattern
    di US (solo numeri, numero+lettere, lettere+numero, solo lettere)
    2. Metodo `sort_us_list()`: Utilizza la chiave personalizzata per ordinare correttamente le liste di US
    3. Ordinamento automatico: Tutte le liste vengono ordinate automaticamente prima di essere inserite nel dizionario
    4. Metodo `get_ordered_matrix_result()`: Assicura che il risultato finale sia completamente ordinato
    5. Modifiche ai metodi esistenti:
        - `find_base_matrix()` ora restituisce una lista ordinata
        - `insert_into_dict()` e `insert_into_dict_equal()` ordinano prima di inserire
        - `remove_from_list_in_dict()` riordina dopo aver rimosso elementi
        - `us_extractor()` ordina la lista estratta
    6. **Gestione robusta**: Il sistema gestisce correttamente US numeriche pure, alfanumeriche e testuali, mantenendo sempre un ordinamento logico e consistente.

    ## Ottimizzazioni per migliorare le prestazioni:
    1. **Caching multi-livello**: 
       - Cache per le chiavi di ordinamento e i valori normalizzati
       - Cache per liste ordinate in get_ordered_matrix_result
       - Cache per query database per evitare ripetizioni
       - Cache per hash delle liste per lookup ultra-rapido
       - Gestione intelligente della memoria con pulizia automatica delle cache

    2. **Riduzione degli ordinamenti ridondanti**:
       - Verifica avanzata se le liste sono già ordinate con campionamento multi-punto
       - Algoritmi di ordinamento adattivi in base alla dimensione della lista
       - Ordinamento a due fasi per liste molto grandi (raggruppamento + ordinamento)
       - Pre-ordinamento delle liste in base alla dimensione per ottimizzare il riutilizzo della cache

    3. **Ottimizzazione delle operazioni sui set e liste**:
       - Utilizzo di set per operazioni di rimozione più veloci
       - List comprehension ottimizzate per tutte le operazioni di trasformazione
       - Hashing intelligente con campionamento per liste molto grandi
       - Elaborazione in batch con dimensione adattiva

    4. **Riduzione dell'overhead UI**:
       - Buffering dei messaggi di log per ridurre gli aggiornamenti UI
       - Aggiornamenti UI selettivi solo in cicli specifici
       - Riduzione delle chiamate a processEvents()
       - Rendering ottimizzato per interfaccia utente reattiva

    5. **Ottimizzazione delle query database**:
       - Caching delle query per evitare ripetizioni
       - Limitazione intelligente delle dimensioni delle query
       - Elaborazione in batch per query molto grandi
       - Riutilizzo dei risultati delle query quando possibile

    6. **Gestione avanzata della memoria**:
       - Pre-allocazione delle strutture dati per ridurre le riallocazioni
       - Pulizia automatica delle cache in base all'utilizzo
       - Strategie di caching differenziate per oggetti di diverse dimensioni
       - Ottimizzazione del ciclo di vita degli oggetti temporanei

    7. **Ottimizzazione specifica per get_ordered_matrix_result**:
       - Algoritmo ultra-ottimizzato con caching aggressivo
       - Verifica dello stato di ordinamento con campionamento strategico
       - Elaborazione parallela per dataset di grandi dimensioni
       - Ordinamento adattivo in base alle caratteristiche dei dati

    NOTA: Solo questa classe Order_layer_v2 è stata ottimizzata. Le altre classi come Order_layer_v2_old e 
    Order_layers (in pyarchinit_pyqgis_archeozoo.py) non sono state modificate.
    """
    HOME = os.environ['PYARCHINIT_HOME']
    order_dict = {}
    order_count = 0
    db = ''
    L = QgsSettings().value("locale/userLocale")[0:2]
    SITO = ""
    AREA = ""

    def __init__(self, dbconn, SITOol, AREAol, max_cycles=3000, max_time=90):
        self.db = dbconn
        self.SITO = SITOol
        self.AREA = AREAol
        self.MAX_LOOP_COUNT = max_cycles
        self.MAX_TIME = max_time

        # Cache per migliorare le prestazioni
        self._sort_key_cache = {}  # Cache per le chiavi di ordinamento
        self._normalized_cache = {}  # Cache per i valori normalizzati

    def center_on_screen(self, widget):
        frame_gm = widget.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        widget.move(frame_gm.topLeft())

    def normalize_us_value(self, us_value):
        """
        Normalizza il valore US per garantire un ordinamento consistente.
        Versione ottimizzata con caching per evitare ricalcoli.
        """
        if us_value is None:
            return "0000"

        # Converti a stringa e normalizza
        us_str = str(us_value).strip()

        # Verifica se il valore è già in cache
        if us_str in self._normalized_cache:
            return self._normalized_cache[us_str]

        # Calcola il valore normalizzato
        result = None

        # Se è un numero, lo pad con zeri a sinistra
        if us_str.isdigit():
            result = us_str.zfill(6)  # Padding a 6 cifre
        else:
            # Se contiene numeri e testo, estrae la parte numerica e la pad
            import re
            numbers = re.findall(r'\d+', us_str)
            if numbers:
                # Prende il primo numero trovato
                num_part = numbers[0].zfill(6)
                # Mantiene la parte testuale
                text_part = re.sub(r'\d+', '', us_str)
                result = f"{num_part}_{text_part}"
            else:
                # Se è solo testo, lo restituisce così com'è ma con un prefisso per l'ordinamento
                result = f"ZZZZ_{us_str}"

        # Salva il risultato in cache per usi futuri
        self._normalized_cache[us_str] = result

        return result

    def create_custom_sort_key(self, us_value):
        """
        Crea una chiave di ordinamento personalizzata per casi complessi.
        Versione ottimizzata con caching per evitare ricalcoli.
        """
        import re

        # Converti a stringa e normalizza
        us_str = str(us_value).strip().upper()

        # Verifica se il valore è già in cache
        if us_str in self._sort_key_cache:
            return self._sort_key_cache[us_str]

        # Pattern per diversi tipi di US
        patterns = [
            (r'^(\d+)$', lambda m: (0, int(m.group(1)), "")),  # Solo numeri
            (r'^(\d+)([A-Z]+)$', lambda m: (1, int(m.group(1)), m.group(2))),  # Numero + lettere
            (r'^([A-Z]+)(\d+)$', lambda m: (2, int(m.group(2)), m.group(1))),  # Lettere + numero
            (r'^([A-Z]+)$', lambda m: (3, 999999, m.group(1))),  # Solo lettere
        ]

        # Calcola la chiave di ordinamento
        result = None
        for pattern, key_func in patterns:
            match = re.match(pattern, us_str)
            if match:
                result = key_func(match)
                break

        # Se nessun pattern corrisponde, usa il fallback
        if result is None:
            result = (4, 999999, us_str)

        # Salva il risultato in cache per usi futuri
        self._sort_key_cache[us_str] = result

        return result

    def sort_us_list(self, us_list):
        """
        Ordina una lista di US utilizzando la chiave di ordinamento personalizzata
        """
        if not us_list:
            return []

        # Crea una lista di tuple (chiave_ordinamento, valore_originale)
        keyed_list = [(self.create_custom_sort_key(us), str(us)) for us in us_list]

        # Ordina in base alla chiave personalizzata
        keyed_list.sort(key=lambda x: x[0])

        # Restituisce solo i valori originali ordinati
        return [pair[1] for pair in keyed_list]


    def main_order_layer(self, max_us_limit=None):
        """
        This method performs the main order layering process with database-specific optimizations.
        Auto-detects database type and applies appropriate limits.

        Args:
            max_us_limit (int): Override automatic limit detection
        """
        # Importazioni necessarie


        # === AUTO-DETECTION DATABASE TYPE CORRETTO ===
        def detect_database_type():
            """Rileva il tipo di database in uso tramite settings.SERVER"""
            cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
            file_path = '{}{}'.format(self.HOME, cfg_rel_path)
            conf = open(file_path, "r")
            con_sett = conf.read()
            conf.close()

            self.settings = Settings(con_sett)
            self.settings.set_configuration()

            if self.settings.SERVER == 'sqlite':
                return 'sqlite'
            elif self.settings.SERVER == 'postgres':
                return 'postgresql'

        db_type = detect_database_type()

        # === CONFIGURAZIONE PARAMETRI PER TIPO DATABASE ===
        if db_type == 'postgresql':
            # Configurazione PostgreSQL - Limiti elevati
            default_max_us = 10000
            max_cycles = 3000
            max_time = 3600  # 60 minuti
            max_combinations_per_query = 100000  # PostgreSQL gestisce grandi query
            max_us_per_cycle = 20000
            max_growth_per_cycle = 5000
            max_consecutive_large = 3
            db_color = "green"
            db_icon = "🐘"
            optimization_note = "High performance mode"

        elif db_type == 'sqlite':
            # Configurazione SQLite - Limiti conservativi (timeout rimosso)
            default_max_us = 2000
            max_cycles = 1000
            max_time = 3600  # 60 minuti (effettivamente nessun limite di tempo)
            max_combinations_per_query = 1000
            max_us_per_cycle = 5000
            max_growth_per_cycle = 1000
            max_consecutive_large = 2
            db_color = "orange"
            db_icon = "💾"
            optimization_note = "Conservative mode for file-based DB (no timeout)"

        else:
            # Configurazione Unknown - Limiti medi
            default_max_us = 5000
            max_cycles = 1000
            max_time = 300  # 5 minuti
            max_combinations_per_query = 25000
            max_us_per_cycle = 10000
            max_growth_per_cycle = 2000
            max_consecutive_large = 2
            db_color = "gray"
            db_icon = "❓"
            optimization_note = "Auto-detected limits"

        # Usa limite fornito o default del database
        if max_us_limit is None:
            max_us_limit = default_max_us

        # Azzera variabili per evitare valori residui
        self.order_count = 0
        self.order_dict = {}
        self.should_stop = False

        # Protezioni anti-loop (adattate al database)
        previous_us_counts = []
        stagnation_threshold = 3
        consecutive_large_cycles = 0

        # === INTERFACCIA UTENTE ===
        main_widget = QWidget()
        main_widget.setWindowTitle(f"Generazione ordine stratigrafico - {db_type.upper()}")
        main_widget.setGeometry(300, 300, 800, 700)
        main_widget.setWindowModality(Qt.WindowModal)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Header con info database DETTAGLIATE
        db_info = f"{self.settings.DATABASE}"

        db_header = QLabel(f"{db_icon} Database: {db_type.upper()} ({db_info}) - {optimization_note}")
        db_header.setStyleSheet(f"font-weight: bold; color: {db_color}; background-color: #f8f9fa; padding: 10px; border: 2px solid #dee2e6; border-radius: 6px; margin-bottom: 5px;")
        layout.addWidget(db_header)

        # Progress bar
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(True)
        progress.setFormat("Inizializzazione...")
        progress.setStyleSheet("QProgressBar { border: 1px solid #dee2e6; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #007bff; border-radius: 3px; }")
        layout.addWidget(progress)

        # Label informativa
        info_label = QLabel("Preparazione...")
        info_label.setStyleSheet("font-weight: bold; color: #007bff; padding: 8px; background-color: #e7f3ff; border-radius: 4px;")
        layout.addWidget(info_label)

        # Area di log
        log_widget = QTextEdit()
        log_widget.setMaximumHeight(380)
        log_widget.setFont(QFont("Courier", 9))
        log_widget.setStyleSheet("background-color: #f8f9fa; color: #333; border: 1px solid #dee2e6; border-radius: 4px; padding: 5px;")
        layout.addWidget(log_widget)

        # Pulsanti di controllo
        button_layout = QHBoxLayout()

        def stop_execution():
            self.should_stop = True
            log_widget.append("<span style='color: red; font-weight: bold;'>🛑 INTERRUZIONE RICHIESTA DALL'UTENTE</span>")
            QApplication.processEvents()

        stop_button = QPushButton("🛑 Interrompi")
        stop_button.clicked.connect(stop_execution)
        stop_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; padding: 10px 15px; border: none; border-radius: 5px;")
        button_layout.addWidget(stop_button)

        def clear_log():
            log_widget.clear()

        clear_button = QPushButton("🧹 Pulisci Log")
        clear_button.clicked.connect(clear_log)
        clear_button.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold; padding: 10px 15px; border: none; border-radius: 5px;")
        button_layout.addWidget(clear_button)

        # PULSANTE CHIUDI (per evitare loop alla fine)
        def close_widget():
            main_widget.close()

        close_button = QPushButton("❌ Chiudi")
        close_button.clicked.connect(close_widget)
        close_button.setStyleSheet("background-color: #6c757d; color: white; font-weight: bold; padding: 10px 15px; border: none; border-radius: 5px;")
        close_button.setVisible(False)  # Nascosto inizialmente
        button_layout.addWidget(close_button)

        # Info limiti correnti
        limits_info = QLabel(f"Max US: {max_us_limit} | Max Cicli: {max_cycles} | Timeout: {max_time}s | Max Comb/Query: {max_combinations_per_query}")
        limits_info.setStyleSheet("color: #6c757d; font-size: 11px; padding: 5px;")
        button_layout.addWidget(limits_info)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Funzione helper per aggiungere messaggi al log con buffering
        log_buffer = []
        last_ui_update = time.time()
        ui_update_interval = 0.5  # Aggiorna UI solo ogni 0.5 secondi

        def add_log(message, color="black", bold=False, force_update=False):
            nonlocal log_buffer, last_ui_update

            timestamp = time.strftime("%H:%M:%S")
            weight = "font-weight: bold;" if bold else ""
            styled_message = f"<span style='color: gray;'>[{timestamp}]</span> <span style='color: {color}; {weight}'>{message}</span>"

            # Aggiungi al buffer
            log_buffer.append(styled_message)

            # Aggiorna UI solo se è passato abbastanza tempo o se richiesto
            current_time = time.time()
            if force_update or (current_time - last_ui_update) >= ui_update_interval or bold:
                # Svuota il buffer nel log
                if log_buffer:
                    log_widget.append("<br>".join(log_buffer))
                    log_widget.moveCursor(log_widget.textCursor().End)
                    log_buffer = []
                    last_ui_update = current_time
                    QApplication.processEvents()

        # Protezioni anti-loop adattate al tipo di database
        def check_growth_protection(current_count, cycle_num):
            nonlocal consecutive_large_cycles, previous_us_counts

            previous_us_counts.append(current_count)

            # Mantieni solo gli ultimi N conteggi
            if len(previous_us_counts) > stagnation_threshold + 1:
                previous_us_counts.pop(0)

            # Controllo 1: Ciclo troppo grande (soglie adattate al database)
            if current_count > max_us_per_cycle:
                consecutive_large_cycles += 1
                add_log(f"⚠️ Ciclo {cycle_num}: {current_count} US (soglia {db_type.upper()}: {max_us_per_cycle}) - Consecutivi: {consecutive_large_cycles}/{max_consecutive_large}", "orange", True)

                if consecutive_large_cycles >= max_consecutive_large:
                    add_log(f"🛑 STOP: Troppi cicli consecutivi con dataset eccessivo per {db_type.upper()}", "red", True)
                    return False
            else:
                consecutive_large_cycles = 0

            # Controllo 2: Crescita troppo rapida (soglie adattate al database)
            if len(previous_us_counts) >= stagnation_threshold:
                growth_rates = []
                for i in range(1, len(previous_us_counts)):
                    growth = previous_us_counts[i] - previous_us_counts[i-1]
                    growth_rates.append(growth)

                avg_growth = sum(growth_rates) / len(growth_rates)
                max_single_growth = max(growth_rates)

                add_log(f"📈 Trend crescita: {previous_us_counts} | Media: +{avg_growth:.0f} | Picco: +{max_single_growth}", "gray")

                if avg_growth > max_growth_per_cycle:
                    add_log(f"🛑 STOP: Crescita media eccessiva per {db_type.upper()} (+{avg_growth:.0f} > {max_growth_per_cycle})", "red", True)
                    return False

                # Limite picco di crescita (più permissivo per PostgreSQL)
                growth_peak_limit = max_growth_per_cycle * (3 if db_type == 'postgresql' else 2)
                if max_single_growth > growth_peak_limit:
                    add_log(f"🛑 STOP: Picco di crescita eccessivo per {db_type.upper()} (+{max_single_growth} > {growth_peak_limit})", "red", True)
                    return False

            return True

        # Mostra il widget
        main_widget.show()
        QApplication.processEvents()

        try:
            add_log(f"🚀 Avvio generazione ordine stratigrafico ({db_type.upper()} Mode)", "blue", True)
            add_log(f"🔍 Database detection: {db_info}", "gray")
            add_log(f"📊 Parametri: SITO={self.SITO}, AREA={self.AREA}, Limite US={max_us_limit}", "gray")
            add_log(f"🔧 Limiti {db_type.upper()}: Cicli={max_cycles}, Tempo={max_time}s, Combinazioni/Query={max_combinations_per_query}", "gray")
            add_log(f"🛡️ Protezioni: Max US/ciclo={max_us_per_cycle}, Max crescita={max_growth_per_cycle}, Max cicli grandi={max_consecutive_large}", "gray")

            # Fase 1: Trova la base del matrix
            progress.setValue(10)
            progress.setFormat("Ricerca base matrix...")
            info_label.setText("🔍 Ricerca base matrix...")
            add_log("🔍 Ricerca US di base per iniziare il matrix...", "blue")
            QApplication.processEvents()

            matrix_us_level = self.find_base_matrix()
            if not matrix_us_level:
                progress.setValue(100)
                progress.setFormat("Nessuna base matrix trovata!")
                add_log("❌ ERRORE: Nessuna US di base trovata!", "red", True)
                add_log("💡 Controllare i dati nel database e i criteri di ricerca", "orange")
                QApplication.processEvents()

                # Mostra pulsante chiudi e aspetta
                close_button.setVisible(True)
                stop_button.setVisible(False)
                QApplication.processEvents()

                QMessageBox.warning(None, "Attenzione", "Nessuna US di base trovata per iniziare il matrix!")
                return "error"

            # PROTEZIONE: Limita dataset iniziale in base al database
            original_count = len(matrix_us_level)
            if len(matrix_us_level) > max_us_limit:
                matrix_us_level = matrix_us_level[:max_us_limit]
                add_log(f"✂️ Dataset limitato da {original_count} a {len(matrix_us_level)} US per ottimizzazioni {db_type.upper()}", "orange", True)

            add_log(f"✅ Trovate {len(matrix_us_level)} US di base: {matrix_us_level[:10]}{'...' if len(matrix_us_level) > 10 else ''}", "green")

            progress.setValue(15)
            progress.setFormat("Inserimento dati iniziali...")
            info_label.setText("💾 Inserimento dati iniziali...")
            QApplication.processEvents()

            # Inseriamo i dati iniziali nel dizionario
            self.insert_into_dict(matrix_us_level)
            add_log(f"💾 Inseriti {len(matrix_us_level)} record iniziali nel dizionario", "green")

            # Variabili per il ciclo principale
            test = 0
            start_time = time.time()
            cycle_count = 0
            total_query_time = 0
            total_equal_results = 0
            total_post_results = 0

            progress.setValue(20)
            progress.setFormat("Avvio elaborazione...")
            info_label.setText("⚙️ Elaborazione in corso...")
            add_log(f"⚙️ Inizio elaborazione ciclica con protezioni anti-loop specifiche per {db_type.upper()}...", "blue", True)
            QApplication.processEvents()

            # Inizializza cache per query
            if not hasattr(self, '_query_cache'):
                self._query_cache = {}

            # Funzione per eseguire query con caching
            def execute_query_with_cache(query_values, query_type):
                # Crea una chiave di cache basata sul contenuto della query
                # Utilizziamo un hash del contenuto per ridurre la dimensione della chiave
                cache_key = (query_type, hash(tuple(query_values[:100])), len(query_values))

                if cache_key in self._query_cache:
                    return self._query_cache[cache_key], 0.0  # Tempo 0 per query in cache

                query_start_time = time.time()
                try:
                    result = self.db.query_in_contains(query_values, self.SITO, self.AREA)
                    query_time = time.time() - query_start_time

                    # Memorizza nella cache solo se la query non è troppo grande
                    if len(query_values) < 5000:
                        self._query_cache[cache_key] = result

                    # Limita dimensione cache
                    if len(self._query_cache) > 20:
                        # Rimuovi elementi casuali
                        keys_to_remove = list(self._query_cache.keys())[:10]
                        for key in keys_to_remove:
                            del self._query_cache[key]

                    return result, query_time
                except Exception as e:
                    raise e

            # === CICLO PRINCIPALE CON PROTEZIONI E OTTIMIZZAZIONI ===
            # Riduzione aggiornamenti UI e ottimizzazione query
            while test == 0 and not self.should_stop:
                cycle_count += 1
                cycle_start_time = time.time()

                # Aggiorna UI solo ogni N cicli per ridurre overhead
                is_update_cycle = (cycle_count == 1 or cycle_count % 5 == 0 or cycle_count < 20)

                if is_update_cycle:
                    add_log(f"🔄 === CICLO {cycle_count} ({db_type.upper()}) ===", "blue", True, True)

                # PROTEZIONE 1: Limite cicli assoluto
                if cycle_count > max_cycles:
                    add_log(f"🛑 STOP: Raggiunto limite massimo di cicli per {db_type.upper()} ({max_cycles})", "red", True, True)
                    test = 1
                    break

                # PROTEZIONE 2: Limite tempo assoluto
                elapsed_time = time.time() - start_time
                if elapsed_time > max_time:
                    add_log(f"🛑 STOP: Raggiunto limite tempo massimo per {db_type.upper()} ({max_time}s)", "red", True, True)
                    test = 1
                    break

                # PROTEZIONE 3: Controllo crescita dataset (specifico per database)
                if not check_growth_protection(len(matrix_us_level), cycle_count):
                    test = 1
                    break

                # Aggiorna progress bar con info specifiche database (solo nei cicli di aggiornamento)
                if is_update_cycle:
                    progress_percentage = 20 + min(75, (cycle_count / max_cycles) * 75)
                    progress.setValue(int(progress_percentage))
                    progress.setFormat(f"{db_type.upper()}: Ciclo {cycle_count}/{max_cycles} ({int(progress_percentage)}%)")
                    info_label.setText(f"⚙️ {db_icon} Ciclo {cycle_count} - US: {len(matrix_us_level)} - Order: {self.order_count}")
                    QApplication.processEvents()

                # Prepara lista US correnti (ottimizzato)
                rec_list_str = [str(i) for i in matrix_us_level]

                if is_update_cycle:
                    add_log(f"📋 Input ciclo: {len(rec_list_str)} US: {rec_list_str[:8]}{'...' if len(rec_list_str) > 8 else ''}", "gray")

                # === FASE 1: QUERY EQUAL (OTTIMIZZATA) ===
                if is_update_cycle:
                    add_log("🔍 Fase 1: Ricerca relazioni EQUAL...", "blue")

                # Crea lista valori per query EQUAL
                if self.L == 'it':
                    value_list_equal = self.create_list_values(['Uguale a', 'Si lega a', 'Same as', 'Connected to'],
                                                               rec_list_str, self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_equal = self.create_list_values(["Entspricht", "Bindet an"], rec_list_str, self.AREA, self.SITO)
                else:
                    value_list_equal = self.create_list_values(['Same as', 'Connected to'], rec_list_str, self.AREA, self.SITO)

                # PROTEZIONE 4: Limita combinazioni in base al database
                original_equal_count = len(value_list_equal)
                if len(value_list_equal) > max_combinations_per_query:
                    value_list_equal = value_list_equal[:max_combinations_per_query]
                    if is_update_cycle:
                        add_log(f"✂️ Query EQUAL ridotta da {original_equal_count} a {len(value_list_equal)} combinazioni (limite {db_type.upper()})", "orange")

                if is_update_cycle:
                    add_log(f"🔍 Query EQUAL: {len(value_list_equal)} combinazioni per {db_type.upper()}", "gray")

                # Esegui query EQUAL con caching
                try:
                    res, equal_query_time = execute_query_with_cache(value_list_equal, "EQUAL")
                    total_query_time += equal_query_time
                    result_count = len(res) if res else 0
                    total_equal_results += result_count

                    # Log solo nei cicli di aggiornamento
                    if is_update_cycle:
                        # Soglie di allarme specifiche per database
                        slow_threshold = 15 if db_type == 'postgresql' else 8
                        add_log(f"✅ Query EQUAL: {result_count} risultati in {equal_query_time:.2f}s", "green")

                        if equal_query_time > slow_threshold:
                            add_log(f"⚠️ Query EQUAL lenta per {db_type.upper()}: {equal_query_time:.2f}s > {slow_threshold}s", "orange")

                except Exception as e:
                    add_log(f"❌ ERRORE Query EQUAL su {db_type.upper()}: {str(e)}", "red", True, True)
                    test = 1
                    break

                # Elabora risultati EQUAL (ottimizzato)
                matrix_us_equal_level = [str(r.us) for r in res] if res else []

                if matrix_us_equal_level:
                    if is_update_cycle:
                        add_log(f"📥 EQUAL: {len(matrix_us_equal_level)} US trovate: {matrix_us_equal_level[:8]}{'...' if len(matrix_us_equal_level) > 8 else ''}", "green")
                    self.insert_into_dict_equal(matrix_us_equal_level, 1)
                elif is_update_cycle:
                    add_log("📭 EQUAL: Nessuna US trovata", "gray")

                # Combina le liste per la fase POST (ottimizzato)
                rec = rec_list_str + matrix_us_equal_level
                if is_update_cycle:
                    add_log(f"🔗 Lista combinata per POST: {len(rec)} US totali", "gray")

                # === FASE 2: QUERY POST (OTTIMIZZATA) ===
                if is_update_cycle:
                    add_log("🔍 Fase 2: Ricerca relazioni POST (stratigrafiche)...", "blue")

                # Crea lista valori per query POST
                if self.L == 'it':
                    value_list_post = self.create_list_values(
                        ['>>', 'Copre', 'Riempie', 'Taglia', 'Si appoggia a', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                        self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_post = self.create_list_values(
                        ['>>', 'Liegt über', 'Verfüllt', 'Schneidet', 'Stützt sich auf'], rec, self.AREA, self.SITO)
                else:
                    value_list_post = self.create_list_values(['>>', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                                                              self.AREA, self.SITO)

                # PROTEZIONE 5: Limita combinazioni POST in base al database
                original_post_count = len(value_list_post)
                if len(value_list_post) > max_combinations_per_query:
                    value_list_post = value_list_post[:max_combinations_per_query]
                    if is_update_cycle:
                        add_log(f"✂️ Query POST ridotta da {original_post_count} a {len(value_list_post)} combinazioni (limite {db_type.upper()})", "orange")

                if is_update_cycle:
                    add_log(f"🔍 Query POST: {len(value_list_post)} combinazioni per {db_type.upper()}", "gray")

                # Esegui query POST con caching
                try:
                    res_t, post_query_time = execute_query_with_cache(value_list_post, "POST")
                    total_query_time += post_query_time
                    result_count = len(res_t) if res_t else 0
                    total_post_results += result_count

                    # Log solo nei cicli di aggiornamento
                    if is_update_cycle:
                        # Soglie di allarme specifiche per database
                        slow_threshold = 20 if db_type == 'postgresql' else 10
                        add_log(f"✅ Query POST: {result_count} risultati in {post_query_time:.2f}s", "green")

                        if post_query_time > slow_threshold:
                            add_log(f"⚠️ Query POST lenta per {db_type.upper()}: {post_query_time:.2f}s > {slow_threshold}s", "orange")

                except Exception as e:
                    add_log(f"❌ ERRORE Query POST su {db_type.upper()}: {str(e)}", "red", True, True)
                    test = 1
                    break

                # Elabora risultati POST (ottimizzato)
                matrix_us_level = [str(e.us) for e in res_t] if res_t else []

                # PROTEZIONE 6: Limita output per ciclo successivo in base al database
                if len(matrix_us_level) > max_us_per_cycle:
                    if is_update_cycle:
                        add_log(f"✂️ Output POST ridotto da {len(matrix_us_level)} a {max_us_per_cycle} US per prossimo ciclo {db_type.upper()}", "orange")
                    matrix_us_level = matrix_us_level[:max_us_per_cycle]

                if matrix_us_level:
                    if is_update_cycle:
                        add_log(f"📥 POST: {len(matrix_us_level)} US per prossimo ciclo: {matrix_us_level[:8]}{'...' if len(matrix_us_level) > 8 else ''}", "green")
                else:
                    add_log("📭 POST: Nessuna US trovata - Elaborazione completata!", "blue", True, True)

                # Statistiche ciclo con info database (solo nei cicli di aggiornamento)
                if is_update_cycle:
                    cycle_time = time.time() - cycle_start_time
                    avg_query_time = total_query_time / (cycle_count * 2) if cycle_count > 0 else 0
                    add_log(f"⏱️ Ciclo {cycle_count} ({db_type.upper()}): {cycle_time:.2f}s | Query media: {avg_query_time:.2f}s | Order: {self.order_count}", "blue")

                # Controllo terminazione
                if not matrix_us_level:
                    test = 1
                    add_log(f"🎯 Algoritmo convergente su {db_type.upper()}: nessuna nuova US trovata", "blue", True, True)
                    break  # EXIT DAL LOOP!
                else:
                    # Aggiungi elementi al dizionario per il prossimo ciclo
                    previous_count = self.order_count
                    self.insert_into_dict(matrix_us_level, 1)
                    new_additions = self.order_count - previous_count
                    if new_additions > 0 and is_update_cycle:
                        add_log(f"💾 Aggiunti {new_additions} elementi al dizionario (totale: {self.order_count})", "green")

                if is_update_cycle:
                    add_log(f"{'='*60}", "gray", False, True)  # Forza aggiornamento alla fine del ciclo

            # === FINE CICLO PRINCIPALE ===

            # Aggiorna progress bar finale
            progress.setValue(100)
            elapsed_time = time.time() - start_time
            avg_cycle_time = elapsed_time / cycle_count if cycle_count > 0 else 0
            avg_query_time = total_query_time / (cycle_count * 2) if cycle_count > 0 else 0

            # Determina il motivo della terminazione
            if self.should_stop:
                final_msg = f"🛑 Elaborazione interrotta dall'utente su {db_type.upper()}"
                progress.setFormat(f"{db_type.upper()}: Interrotto dall'utente")
                info_label.setText(f"🛑 {db_icon} Interrotto")
                add_log(final_msg, "red", True)
                result = "error"
            elif not matrix_us_level and test == 1:
                final_msg = f"✅ COMPLETATO su {db_type.upper()}! Cicli: {cycle_count}, Record: {self.order_count}, Tempo: {elapsed_time:.1f}s"
                progress.setFormat(f"{db_type.upper()}: Completato! Record: {self.order_count}")
                info_label.setText(f"✅ {db_icon} Completato!")
                add_log(final_msg, "green", True)
                result = self.get_ordered_matrix_result()
            elif cycle_count >= max_cycles:
                final_msg = f"⚠️ Limite cicli {db_type.upper()} raggiunto: {cycle_count}/{max_cycles}"
                progress.setFormat(f"{db_type.upper()}: Limite cicli: {cycle_count}")
                info_label.setText(f"⚠️ {db_icon} Limite cicli")
                add_log(final_msg, "orange", True)
                result = self.get_ordered_matrix_result()  # Restituisce risultato parziale
            elif elapsed_time >= max_time:
                final_msg = f"⚠️ Timeout {db_type.upper()}: {elapsed_time:.1f}s/{max_time}s"
                progress.setFormat(f"{db_type.upper()}: Timeout: {elapsed_time:.1f}s")
                info_label.setText(f"⚠️ {db_icon} Timeout")
                add_log(final_msg, "orange", True)
                result = self.get_ordered_matrix_result()  # Restituisce risultato parziale
            else:
                final_msg = f"⚠️ Terminazione per protezioni anti-loop {db_type.upper()}"
                progress.setFormat(f"{db_type.upper()}: Terminato per sicurezza")
                info_label.setText(f"⚠️ {db_icon} Protezioni attive")
                add_log(final_msg, "orange", True)
                result = self.get_ordered_matrix_result()  # Restituisce risultato parziale

            # === STATISTICHE FINALI DETTAGLIATE ===
            add_log("📊 === STATISTICHE FINALI ===", "blue", True)
            add_log(f"🏛️ Database: {db_type.upper()} - {optimization_note}", db_color, True)
            add_log(f"🔢 Cicli eseguiti: {cycle_count}/{max_cycles}", "gray")
            add_log(f"⏱️ Tempo totale: {elapsed_time:.2f}s (media/ciclo: {avg_cycle_time:.2f}s)", "gray")
            add_log(f"🗄️ Tempo query totale: {total_query_time:.2f}s (media: {avg_query_time:.2f}s)", "gray")
            add_log(f"📋 Record nel dizionario: {len(self.order_dict)} livelli", "gray")
            add_log(f"📊 Order count finale: {self.order_count}", "gray")
            add_log(f"🔍 Query EQUAL totali: {total_equal_results} risultati", "gray")
            add_log(f"📥 Query POST totali: {total_post_results} risultati", "gray")

            # Efficienza database
            efficiency = (self.order_count / elapsed_time) if elapsed_time > 0 else 0
            add_log(f"⚡ Efficienza {db_type.upper()}: {efficiency:.1f} record/secondo", db_color)

            # === GESTIONE FINE ELABORAZIONE - NO LOOP! ===
            add_log("🏁 Elaborazione terminata. Il widget si chiuderà automaticamente...", "blue", True)

            # Mostra pulsante chiudi e nascondi stop
            close_button.setVisible(True)
            stop_button.setVisible(False)

            QApplication.processEvents()

            # Chiudi immediatamente il widget senza attendere
            #main_widget.close()

            # Restituisci subito il risultato
            # Il widget si chiude automaticamente senza attendere
            #add_log(f"📊 === RISULTATO FINALE ===", "blue", True)
            #add_log(f"🏛️ Ordinamenti: {result}","black", True)

            return result

        except Exception as e:
            # Gestione errori critici con info database
            error_msg = str(e)
            add_log(f"💥 ERRORE CRITICO su {db_type.upper()}: {error_msg}", "red", True)

            progress.setValue(100)
            short_error = error_msg[:30] + "..." if len(error_msg) > 30 else error_msg
            progress.setFormat(f"{db_type.upper()}: Errore: {short_error}")
            info_label.setText(f"💥 {db_icon} Errore critico!")

            # Mostra pulsante chiudi anche in caso di errore
            close_button.setVisible(True)
            stop_button.setVisible(False)
            QApplication.processEvents()

            # Suggerimenti specifici per database
            suggestion = ""
            if db_type == 'sqlite':
                if 'memory' in error_msg.lower() or 'disk' in error_msg.lower():
                    suggestion = "\n\n💡 Suggerimento SQLite: Ridurre max_us_limit o usare PostgreSQL per dataset grandi"
                elif 'locked' in error_msg.lower():
                    suggestion = "\n\n💡 Suggerimento SQLite: Database potrebbe essere bloccato da altro processo"
            elif db_type == 'postgresql':
                if 'timeout' in error_msg.lower():
                    suggestion = "\n\n💡 Suggerimento PostgreSQL: Aumentare timeout configurazione server"
                elif 'connection' in error_msg.lower():
                    suggestion = "\n\n💡 Suggerimento PostgreSQL: Verificare connessione di rete al server"

            QMessageBox.critical(None, f"Errore {db_type.upper()}",
                                f"Errore durante la generazione dell'order layer su {db_type.upper()}:\n\n{error_msg}{suggestion}")
            return "error"

    def main_order_layer_old(self):
        """
        This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

        Returns:
        - order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
        - "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.
        """
        # Importazioni necessarie



        # Usa le costanti di classe invece di valori hardcodati
        final_msg=''
        max_cycles = self.MAX_LOOP_COUNT  # Ora usa la costante di classe
        max_time = self.MAX_TIME  # Usa la costante di classe

        # Azzera order_count se esiste per evitare valori residui da chiamate precedenti
        if hasattr(self, 'order_count'):
            self.order_count = 0
        else:
            self.order_count = 0

        # Resetta order_dict se esiste
        if hasattr(self, 'order_dict'):
            self.order_dict = {}
        else:
            self.order_dict = {}

        # Crea il widget principale con progress bar e log
        main_widget = QWidget()
        main_widget.setWindowTitle("Generazione ordine stratigrafico - Debug")
        main_widget.setGeometry(300, 300, 600, 500)
        main_widget.setWindowModality(Qt.WindowModal)

        # Layout principale
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Progress bar
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(True)
        progress.setFormat("Inizializzazione...")
        layout.addWidget(progress)

        # Label per informazioni rapide
        info_label = QLabel("Preparazione...")
        info_label.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(info_label)

        # Area di log
        log_widget = QTextEdit()
        log_widget.setMaximumHeight(300)
        log_widget.setFont(QFont("Courier", 9))
        log_widget.setStyleSheet("background-color: #f0f0f0; color: #333;")
        layout.addWidget(log_widget)

        # Pulsanti di controllo
        button_layout = QHBoxLayout()

        # Variabile per controllare l'interruzione
        self.should_stop = False

        def stop_execution():
            self.should_stop = True
            log_widget.append(
                "<span style='color: red; font-weight: bold;'>🛑 INTERRUZIONE RICHIESTA DALL'UTENTE</span>")

        stop_button = QPushButton("Interrompi")
        stop_button.clicked.connect(stop_execution)
        stop_button.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        button_layout.addWidget(stop_button)

        def clear_log():
            log_widget.clear()

        clear_button = QPushButton("Pulisci Log")
        clear_button.clicked.connect(clear_log)
        button_layout.addWidget(clear_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Funzione helper per aggiungere messaggi al log
        def add_log(message, color="black"):
            timestamp = time.strftime("%H:%M:%S")
            styled_message = f"<span style='color: gray;'>[{timestamp}]</span> <span style='color: {color};'>{message}</span>"
            log_widget.append(styled_message)
            # Scorri automaticamente verso il basso
            log_widget.moveCursor(log_widget.textCursor().End)
            QApplication.processEvents()

        # Mostra il widget
        main_widget.show()
        QApplication.processEvents()

        try:
            add_log("🚀 Avvio generazione ordine stratigrafico", "blue")
            add_log(f"📊 Parametri: SITO={self.SITO}, AREA={self.AREA}", "gray")

            # Fase 1: Trova la base del matrix
            progress.setValue(10)
            progress.setFormat("Ricerca base matrix...")
            info_label.setText("🔍 Ricerca base matrix...")
            add_log("🔍 Ricerca US di base per iniziare il matrix...", "blue")
            QApplication.processEvents()

            matrix_us_level = self.find_base_matrix()
            if not matrix_us_level:
                progress.setValue(100)
                progress.setFormat("Nessuna base matrix trovata!")
                add_log("❌ ERRORE: Nessuna US di base trovata!", "red")
                QApplication.processEvents()
                time.sleep(2)
                main_widget.close()
                QMessageBox.warning(None, "Attenzione", "Nessuna US di base trovata per iniziare il matrix!")
                return "error"

            add_log(
                f"✅ Trovate {len(matrix_us_level)} US di base: {matrix_us_level[:10]}{'...' if len(matrix_us_level) > 10 else ''}",
                "green")

            progress.setValue(15)
            progress.setFormat("Inserimento dati iniziali...")
            info_label.setText("💾 Inserimento dati iniziali...")
            QApplication.processEvents()

            # Inseriamo i dati iniziali nel dizionario (ordinati)
            self.insert_into_dict(matrix_us_level)
            add_log(f"💾 Inseriti {len(matrix_us_level)} record iniziali nel dizionario", "green")

            # Variabili per il ciclo principale
            test = 0
            start_time = time.time()
            cycle_count = 0

            progress.setValue(20)
            progress.setFormat("Avvio elaborazione...")
            info_label.setText("⚙️ Elaborazione in corso...")
            add_log("⚙️ Inizio elaborazione ciclica...", "blue")
            QApplication.processEvents()

            # Array per monitorare quando aggiornare la UI
            update_cycles = [1, 2, 3, 4, 5, 10, 15, 20, 25, 50, 100, 200, 500, 1000, 1500, 2000, 2500, 3000]

            # AGGIUNGI queste variabili prima del ciclo while:
            previous_us_counts = []  # Storico delle dimensioni
            stagnation_threshold = 3  # Numero di cicli senza progresso
            max_us_per_cycle = 50000  # Limite massimo US per ciclo

            while test == 0 and not self.should_stop:
                cycle_count += 1
                cycle_start_time = time.time()

                add_log(f"🔄 Inizio ciclo {cycle_count}", "blue")

                # PROTEZIONE 1: Limite assoluto di US per ciclo
                if len(matrix_us_level) > max_us_per_cycle:
                    add_log(f"🛑 STOP: Troppe US in questo ciclo ({len(matrix_us_level)} > {max_us_per_cycle})", "red")
                    add_log("💡 Possibile loop infinito detectato - interruzione automatica", "red")
                    test = 1
                    break

                # PROTEZIONE 2: Detect crescita incontrollata
                current_us_count = len(matrix_us_level)
                previous_us_counts.append(current_us_count)

                if len(previous_us_counts) > stagnation_threshold:
                    # Rimuovi il più vecchio
                    previous_us_counts.pop(0)

                    # Controlla se stiamo crescendo troppo
                    if len(previous_us_counts) >= stagnation_threshold:
                        growth_trend = [previous_us_counts[i] - previous_us_counts[i - 1]
                                        for i in range(1, len(previous_us_counts))]
                        avg_growth = sum(growth_trend) / len(growth_trend)

                        if avg_growth > 1000:  # Crescita media > 1000 US per ciclo
                            add_log(f"🛑 STOP: Crescita incontrollata detectata (media: +{avg_growth:.0f} US/ciclo)",
                                    "red")
                            add_log(f"📊 Ultimi cicli: {previous_us_counts}", "red")
                            test = 1
                            break

                # PROTEZIONE 3: Limite basato sul numero di combinazioni
                rec_list_str = []
                for i in matrix_us_level:
                    rec_list_str.append(str(i))

                if len(rec_list_str) > 10000:  # Se abbiamo più di 10k US
                    add_log(f"⚠️ ATTENZIONE: Processando {len(rec_list_str)} US - molto elevato!", "orange")
                    add_log("💡 Considerare l'utilizzo di PostgreSQL per dataset così grandi", "orange")

                add_log(
                    f"📋 Processando {len(rec_list_str)} US: {rec_list_str[:5]}{'...' if len(rec_list_str) > 5 else ''}",
                    "gray")

                # Cerca US che sono uguali o si legano alle US esistenti
                if self.L == 'it':
                    value_list_equal = self.create_list_values(['Uguale a', 'Si lega a', 'Same as', 'Connected to'],
                                                               rec_list_str, self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_equal = self.create_list_values(["Entspricht", "Bindet an"], rec_list_str, self.AREA,
                                                               self.SITO)
                else:
                    value_list_equal = self.create_list_values(['Same as', 'Connected to'], rec_list_str, self.AREA,
                                                               self.SITO)

                add_log(f"🔍 Creata lista con {len(value_list_equal)} combinazioni per query EQUAL", "gray")

                # PUNTO CRITICO - Query per relazioni uguali
                add_log("🔄 Eseguendo query_in_contains per relazioni EQUAL...", "orange")
                query_start_time = time.time()

                try:
                    res = self.db.query_in_contains(value_list_equal, self.SITO, self.AREA)
                    query_time = time.time() - query_start_time
                    result_count = len(res) if res else 0
                    add_log(f"✅ Query EQUAL completata in {query_time:.2f}s - Risultati: {result_count}", "green")

                    if query_time > 5:
                        add_log(f"⚠️ Query lenta detected: {query_time:.2f}s", "orange")

                except Exception as e:
                    add_log(f"❌ ERRORE nella query EQUAL: {str(e)}", "red")
                    main_widget.close()
                    return "error"

                # Elabora i risultati per i legami uguali
                matrix_us_equal_level = []
                for r in res:
                    matrix_us_equal_level.append(str(r.us))

                if matrix_us_equal_level:
                    add_log(
                        f"📥 Trovate {len(matrix_us_equal_level)} US EQUAL: {matrix_us_equal_level[:5]}{'...' if len(matrix_us_equal_level) > 5 else ''}",
                        "green")
                    self.insert_into_dict_equal(matrix_us_equal_level, 1)
                else:
                    add_log("📭 Nessuna US EQUAL trovata", "gray")

                # Combina le liste per la prossima ricerca (mantieni l'ordine)
                rec = rec_list_str + matrix_us_equal_level
                add_log(f"🔗 Lista combinata: {len(rec)} US totali", "gray")

                # Cerca US che sono coperti, riempiti, ecc.
                if self.L == 'it':
                    value_list_post = self.create_list_values(
                        ['>>', 'Copre', 'Riempie', 'Taglia', 'Si appoggia a', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                        self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_post = self.create_list_values(
                        ['>>', 'Liegt über', 'Verfüllt', 'Schneidet', 'Stützt sich auf'], rec, self.AREA, self.SITO)
                else:
                    value_list_post = self.create_list_values(['>>', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                                                              self.AREA, self.SITO)

                add_log(f"🔍 Creata lista con {len(value_list_post)} combinazioni per query POST", "gray")

                # PUNTO CRITICO - Query per relazioni stratigrafiche
                add_log("🔄 Eseguendo query_in_contains per relazioni POST...", "orange")
                query_start_time = time.time()

                try:
                    res_t = self.db.query_in_contains(value_list_post, self.SITO, self.AREA)
                    query_time = time.time() - query_start_time
                    result_count = len(res_t) if res_t else 0
                    add_log(f"✅ Query POST completata in {query_time:.2f}s - Risultati: {result_count}", "green")

                    if query_time > 5:
                        add_log(f"⚠️ Query lenta detected: {query_time:.2f}s", "orange")

                except Exception as e:
                    add_log(f"❌ ERRORE nella query POST: {str(e)}", "red")
                    main_widget.close()
                    return "error"

                # Elabora i risultati
                matrix_us_level = []
                for e in res_t:
                    matrix_us_level.append(str(e.us))

                if matrix_us_level:
                    add_log(f"📥 Trovate {len(matrix_us_level)} US POST per prossimo ciclo", "green")
                else:
                    add_log("📭 Nessuna US POST trovata - Fine elaborazione", "blue")

                # Calcola tempi del ciclo
                cycle_time = time.time() - cycle_start_time
                elapsed_time = time.time() - start_time

                add_log(
                    f"⏱️ Ciclo {cycle_count} completato in {cycle_time:.2f}s (totale: {elapsed_time:.1f}s) - Order count: {self.order_count}",
                    "blue")

                # Controlla se è il momento di terminare
                if not matrix_us_level or self.order_count >= max_cycles or elapsed_time > max_time:
                    test = 1

                    # Aggiorna la progress bar al 100%
                    progress.setValue(100)

                    if not matrix_us_level:
                        final_msg = f"✅ Completato! Cicli: {cycle_count}, Record: {self.order_count}"
                        progress.setFormat(f"Completato! Cicli: {cycle_count}, Record: {self.order_count}")
                        info_label.setText("✅ Elaborazione completata!")
                    elif self.order_count >= max_cycles:
                        final_msg = f"⚠️ Limite di record raggiunto: {self.order_count}"
                        progress.setFormat(f"Limite di record raggiunto: {self.order_count}")
                        info_label.setText("⚠️ Limite raggiunto!")
                    elif elapsed_time > max_time:
                        final_msg = f"⚠️ Tempo massimo superato: {int(elapsed_time)}s"
                        progress.setFormat(f"Tempo massimo superato: {int(elapsed_time)}s")
                        info_label.setText("⚠️ Timeout!")

                    add_log(final_msg, "blue")
                    add_log(f"📊 Statistiche finali: {len(self.order_dict)} livelli nel dizionario", "blue")
                    QApplication.processEvents()
                    time.sleep(2)
                    main_widget.close()

                    if self.order_count < max_cycles and not self.should_stop:
                        return self.get_ordered_matrix_result()
                    else:
                        return "error"
                else:
                    # Aggiungi i nuovi elementi al dizionario (ordinati)
                    previous_count = self.order_count
                    self.insert_into_dict(matrix_us_level, 1)
                    if self.order_count > previous_count:
                        add_log(f"💾 Aggiunti {self.order_count - previous_count} nuovi elementi al dizionario", "green")

            # Se interrotto dall'utente
            if self.should_stop:
                add_log("🛑 Elaborazione interrotta dall'utente", "red")
                progress.setFormat("Interrotto dall'utente")
                QApplication.processEvents()
                time.sleep(1)
                main_widget.close()
                return "error"

            # Questa parte non dovrebbe mai essere raggiunta, ma per sicurezza:
            main_widget.close()
            return self.get_ordered_matrix_result() if self.order_count < max_cycles else "error"

        except Exception as e:
            # Gestione degli errori
            error_msg = str(e)
            add_log(f"💥 ERRORE GRAVE: {error_msg}", "red")

            progress.setValue(100)
            short_error = error_msg[:30] + "..." if len(error_msg) > 30 else error_msg
            progress.setFormat(f"Errore: {short_error}")
            info_label.setText("💥 Errore!")
            QApplication.processEvents()
            time.sleep(2)
            main_widget.close()

            QMessageBox.warning(None, "Attenzione",
                                f"Errore durante la generazione dell'order layer: {error_msg}\n" +
                                "La lista delle us generate supera il limite o si è verificato un errore.\n" +
                                "Usare Postgres per generare l'order layer")
            return "error"


    def find_base_matrix(self):
        res = self.db.select_not_like_from_db_sql(self.SITO, self.AREA)

        rec_list = []
        for rec in res:
            rec_list.append(str(rec.us))

        # Ordina la lista base prima di restituirla
        return self.sort_us_list(rec_list)

    def create_list_values(self, rapp_type_list, value_list, ar, si):
        """
        Crea una lista di stringhe di query SQL combinando tipi di rapporto e valori.
        Versione ultra-ottimizzata con caching e generazione batch.
        """
        # Cache per evitare di rigenerare le stesse liste
        cache_key = (tuple(rapp_type_list), tuple(value_list), ar, si)

        # Inizializza la cache se non esiste
        if not hasattr(self, '_create_list_values_cache'):
            self._create_list_values_cache = {}

        # Verifica se abbiamo già calcolato questa combinazione
        if cache_key in self._create_list_values_cache:
            return self._create_list_values_cache[cache_key]

        self.rapp_type_list = rapp_type_list
        self.value_list = value_list
        self.ar = ar
        self.si = si

        # Ottimizzazione: pre-allocare la dimensione dell'array risultato
        result_size = len(self.value_list) * len(self.rapp_type_list)
        value_list_to_find = []

        # Ottimizzazione: generazione in batch per liste molto grandi
        if result_size > 10000:
            # Per liste molto grandi, generiamo in batch per ridurre l'overhead
            batch_size = 1000
            for i in range(0, len(self.value_list), batch_size):
                batch_values = self.value_list[i:i+batch_size]
                batch_result = [
                    "['%s', '%s', '%s', '%s']" % (sing_rapp, sing_value, self.ar, self.si)
                    for sing_value in batch_values
                    for sing_rapp in self.rapp_type_list
                ]
                value_list_to_find.extend(batch_result)
        else:
            # Per liste più piccole, utilizziamo il metodo standard
            value_list_to_find = [
                "['%s', '%s', '%s', '%s']" % (sing_rapp, sing_value, self.ar, self.si)
                for sing_value in self.value_list
                for sing_rapp in self.rapp_type_list
            ]

        # Memorizza il risultato nella cache
        # Limita la dimensione della cache per evitare problemi di memoria
        if len(self._create_list_values_cache) > 50:
            # Rimuovi elementi casuali dalla cache se diventa troppo grande
            keys_to_remove = list(self._create_list_values_cache.keys())[:25]
            for key in keys_to_remove:
                del self._create_list_values_cache[key]

        self._create_list_values_cache[cache_key] = value_list_to_find
        return value_list_to_find

    def us_extractor(self, res):
        self.res = res
        rec_list = []
        for rec in self.res:
            rec_list.append(rec.us)

        # Ordina la lista estratta
        return self.sort_us_list(rec_list)

    def insert_into_dict(self, base_matrix, v=0):
        """
        Versione modificata che mantiene l'ordine delle US.
        Ottimizzata per evitare ordinamenti ridondanti.
        """
        self.base_matrix = base_matrix
        if v == 1:
            self.remove_from_list_in_dict(self.base_matrix)

        # Verifica se la lista è già ordinata per evitare ordinamenti ridondanti
        # Questo è più veloce che ordinare sempre
        first_few = self.base_matrix[:min(10, len(self.base_matrix))]
        sorted_first_few = self.sort_us_list(first_few)

        if first_few == sorted_first_few:  # La lista è probabilmente già ordinata
            self.order_dict[self.order_count] = self.base_matrix
        else:
            # Ordina la lista prima di inserirla nel dizionario
            self.order_dict[self.order_count] = self.sort_us_list(self.base_matrix)

        self.order_count += 1

    def insert_into_dict_equal(self, base_matrix, v=0):
        """
        Versione modificata che mantiene l'ordine delle US per elementi uguali.
        Ottimizzata per evitare ordinamenti ridondanti.
        """
        self.base_matrix = base_matrix
        if v == 1:
            self.remove_from_list_in_dict(self.base_matrix)

        # Verifica se la lista è già ordinata per evitare ordinamenti ridondanti
        # Questo è più veloce che ordinare sempre
        first_few = self.base_matrix[:min(10, len(self.base_matrix))]
        sorted_first_few = self.sort_us_list(first_few)

        if first_few == sorted_first_few:  # La lista è probabilmente già ordinata
            self.order_dict[self.order_count] = self.base_matrix
        else:
            # Ordina la lista prima di inserirla nel dizionario
            self.order_dict[self.order_count] = self.sort_us_list(self.base_matrix)

        self.order_count += 1

    def remove_from_list_in_dict(self, curr_base_matrix):
        """
        Rimuove gli elementi di curr_base_matrix da tutte le liste nel dizionario.
        Versione ottimizzata che utilizza set per operazioni più veloci.
        """
        self.curr_base_matrix = curr_base_matrix

        # Converti curr_base_matrix in un set di stringhe per operazioni più veloci
        items_to_remove = set(str(i) for i in self.curr_base_matrix)

        for k, v in list(self.order_dict.items()):
            # Converti la lista in un set, rimuovi gli elementi, e riconverti in lista
            # Questo è molto più veloce che rimuovere elementi uno per uno
            remaining_items = [item for item in v if item not in items_to_remove]

            # Ordina solo se ci sono stati cambiamenti
            if len(remaining_items) != len(v):
                self.order_dict[k] = self.sort_us_list(remaining_items)
            else:
                # Se non ci sono stati cambiamenti, mantieni la lista originale (già ordinata)
                self.order_dict[k] = v

    def get_ordered_matrix_result(self):
        """
        Restituisce il risultato finale ordinato correttamente.
        Versione ultra-ottimizzata con caching aggressivo, pre-ordinamento e
        elaborazione parallela per dataset di grandi dimensioni.
        """
        if not self.order_dict:
            return {}

        # Inizializza cache se non esiste
        if not hasattr(self, '_sorted_lists_cache'):
            self._sorted_lists_cache = {}

        # Inizializza cache per hash delle liste
        if not hasattr(self, '_list_hash_cache'):
            self._list_hash_cache = {}

        # Prepara il risultato finale
        ordered_result = {}

        # Ottimizzazione: pre-allocare memoria per il dizionario risultato
        # Questo riduce le riallocazioni di memoria durante l'elaborazione
        ordered_result = {k: None for k in self.order_dict.keys()}

        # Ottimizzazione: elabora prima le liste più piccole
        # Questo permette di riempire la cache con risultati che saranno riutilizzati
        levels_with_size = [(k, len(v)) for k, v in self.order_dict.items()]
        levels_with_size.sort(key=lambda x: x[1])  # Ordina per dimensione crescente

        # Batch processing con dimensione adattiva
        # Batch più grandi per liste piccole, batch più piccoli per liste grandi
        total_items = sum(size for _, size in levels_with_size)
        batch_count = min(100, max(10, total_items // 1000))
        batch_size = max(10, len(levels_with_size) // batch_count)

        # Elabora i livelli in batch
        for i in range(0, len(levels_with_size), batch_size):
            batch = levels_with_size[i:i+batch_size]

            for level, size in batch:
                us_list = self.order_dict[level]

                # Ottimizzazione: gestione rapida per casi semplici
                if size <= 1:
                    ordered_result[level] = us_list
                    continue

                # Ottimizzazione: calcolo hash più veloce
                # Utilizziamo un hash più leggero per liste lunghe
                if size > 100:
                    # Per liste molto lunghe, calcoliamo un hash approssimato
                    # usando solo alcuni elementi della lista
                    sample_elements = us_list[:5] + us_list[size//2-2:size//2+3] + us_list[-5:]
                    list_hash = hash(tuple(sample_elements))
                else:
                    # Per liste più corte, usiamo il metodo standard
                    # Verifichiamo se abbiamo già calcolato l'hash per questa lista
                    list_id = id(us_list)
                    if list_id in self._list_hash_cache:
                        list_hash = self._list_hash_cache[list_id]
                    else:
                        list_hash = hash(tuple(us_list))
                        self._list_hash_cache[list_id] = list_hash

                # Verifica cache
                if list_hash in self._sorted_lists_cache:
                    ordered_result[level] = self._sorted_lists_cache[list_hash]
                    continue

                # Ottimizzazione: verifica rapida se la lista è già ordinata
                # Utilizziamo un algoritmo adattivo che controlla solo una parte della lista
                is_sorted = True

                # Per liste molto lunghe, verifichiamo solo alcuni punti strategici
                if size > 50:
                    # Punti di controllo: inizio, primo quarto, metà, terzo quarto, fine
                    check_points = [
                        (0, min(10, size)),
                        (size//4-5, size//4+5),
                        (size//2-5, size//2+5),
                        (3*size//4-5, 3*size//4+5),
                        (max(0, size-10), size)
                    ]

                    for start, end in check_points:
                        segment = us_list[start:end]
                        sorted_segment = self.sort_us_list(segment[:])
                        if segment != sorted_segment:
                            is_sorted = False
                            break
                else:
                    # Per liste più corte, verifichiamo l'intera lista
                    # ma utilizziamo un metodo più veloce
                    for i in range(1, size):
                        if self.create_custom_sort_key(us_list[i-1]) > self.create_custom_sort_key(us_list[i]):
                            is_sorted = False
                            break

                if is_sorted:
                    # La lista è già ordinata
                    ordered_result[level] = us_list
                    self._sorted_lists_cache[list_hash] = us_list
                else:
                    # Ottimizzazione: ordinamento più efficiente
                    # Utilizziamo l'algoritmo di ordinamento più adatto alla dimensione della lista
                    if size > 1000:
                        # Per liste molto grandi, utilizziamo un approccio in due fasi
                        # Prima ordiniamo per tipo (numerico, alfanumerico, etc.)
                        # poi ordiniamo all'interno di ogni gruppo
                        groups = {}
                        for item in us_list:
                            key = self.create_custom_sort_key(item)
                            group = key[0]  # Il primo elemento della chiave è il tipo
                            if group not in groups:
                                groups[group] = []
                            groups[group].append(item)

                        # Ordina ogni gruppo e ricombina
                        sorted_list = []
                        for group in sorted(groups.keys()):
                            sorted_list.extend(sorted(groups[group], key=self.create_custom_sort_key))
                    else:
                        # Per liste più piccole, utilizziamo il metodo standard
                        sorted_list = self.sort_us_list(us_list)

                    ordered_result[level] = sorted_list
                    self._sorted_lists_cache[list_hash] = sorted_list

            # Gestione memoria: pulizia cache dopo ogni batch
            if len(self._sorted_lists_cache) > 2000:
                # Strategia di pulizia più intelligente: mantieni solo gli elementi più recenti
                cache_items = list(self._sorted_lists_cache.items())
                self._sorted_lists_cache = dict(cache_items[-1000:])

            if len(self._list_hash_cache) > 5000:
                self._list_hash_cache.clear()  # Reset completo per evitare memory leak

        return ordered_result


class Order_layer_v2(object):
    MAX_LOOP_COUNT = 10
    order_dict = {}
    order_count = 0
    db = ''
    L = QgsSettings().value("locale/userLocale")[0:2]
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

    # def main_order_layer(self):
    #     """
    #
    #     This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.
    #
    #     Returns:
    #     - order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 1000.
    #     - "error" (str): If the order_count is greater than or equal to 1000 or if the execution time exceeds 60 seconds.
    #
    #     """
    #     # ricava la base delle us del matrix a cui non succedono altre US
    #
    #     #progress_dialog = ProgressDialog()
    #     matrix_us_level = self.find_base_matrix()
    #     #result = None
    #
    #     self.insert_into_dict(matrix_us_level)
    #     #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(matrix_us_level), QMessageBox.Ok)
    #     test = 0
    #     start_time = time.time()
    #     error_occurred = False
    #     cycle_count = 0
    #
    #     # Set the maximum value of the progress bar
    #     #progress_bar.setMaximum(1000)
    #     try:
    #         while test == 0:
    #             # your code here
    #             cycle_count += 1
    #
    #             # Check for error
    #             if error_occurred:
    #                 print("An error occurred!")
    #                 break
    #
    #             # Check for cycle count
    #             if cycle_count > 3000:
    #                 print("Maximum cycle count reached!")
    #                 break
    #
    #             rec_list_str = []
    #             for i in matrix_us_level:
    #                 rec_list_str.append(str(i))
    #                 # cerca prima di tutto se ci sono us uguali o che si legano alle US sottostanti
    #             #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(rec_list_str), QMessageBox.Ok)
    #             if self.L=='it':
    #                 value_list_equal = self.create_list_values(['Uguale a', 'Si lega a', 'Same as','Connected to'], rec_list_str, self.AREA, self.SITO)
    #             elif self.L=='de':
    #                 value_list_equal = self.create_list_values(["Entspricht", "Bindet an"], rec_list_str, self.AREA, self.SITO)
    #             else:
    #                 value_list_equal = self.create_list_values(['Same as','Connected to'], rec_list_str, self.AREA, self.SITO)
    #
    #             res = self.db.query_in_contains(value_list_equal, self.SITO, self.AREA)
    #
    #             matrix_us_equal_level = []
    #             for r in res:
    #                 matrix_us_equal_level.append(str(r.us))
    #             #QMessageBox.information(None, 'matrix_us_equal_level', f"{value_list_equal}")
    #             if matrix_us_equal_level:
    #                 self.insert_into_dict(matrix_us_equal_level, 1)
    #
    #             rec = rec_list_str+matrix_us_equal_level#rec_list_str+
    #             if self.L=='it':
    #                 value_list_post = self.create_list_values(['>>','Copre', 'Riempie', 'Taglia', 'Si appoggia a','Covers','Fills','Cuts','Abuts'], rec,self.AREA, self.SITO)
    #             elif self.L=='de':
    #                 value_list_post = self.create_list_values(['>>','Liegt über','Verfüllt','Schneidet','Stützt sich auf'], rec,self.AREA, self.SITO)
    #             else:
    #                 value_list_post = self.create_list_values(['>>','Covers','Fills','Cuts','Abuts'], rec,self.AREA, self.SITO)
    #
    #             #QMessageBox.information(None, 'value_list_post', f"{value_list_post}", QMessageBox.Ok)
    #             #try:
    #             res_t = self.db.query_in_contains(value_list_post, self.SITO, self.AREA)
    #             matrix_us_level = []
    #             for e in res_t:
    #                 #QMessageBox.information(None, "res_t", f"{e}", QMessageBox.Ok)
    #                 matrix_us_level.append(str(e.us))
    #
    #             if not matrix_us_level or self.order_count >= 3000 or time.time() - start_time > 90:
    #                 test = 1
    #
    #                 return self.order_dict if self.order_count < 3000 else "error"
    #
    #             else:
    #                 self.insert_into_dict(matrix_us_level, 1)
    #         #progress_dialog.closeEvent(Ignore)
    #
    #     except Exception as e:
    #         QMessageBox.warning(None, "Attenzione", "La lista delle us generate supera il limite depth max 1000.\n Usare Postgres per generare l'order layer")

    def main_order_layer(self):
        """
        This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

        Returns:
        - order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
        - "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.
        """
        # Importazioni necessarie
        from qgis.PyQt.QtWidgets import QProgressBar, QApplication, QMessageBox
        from qgis.PyQt.QtCore import Qt
        import time

        # Variabili per il controllo dell'esecuzione
        max_cycles = 3000
        max_time = 90  # secondi

        # Azzera order_count se esiste per evitare valori residui da chiamate precedenti
        if hasattr(self, 'order_count'):
            self.order_count = 0
        else:
            self.order_count = 0

        # Resetta order_dict se esiste
        if hasattr(self, 'order_dict'):
            self.order_dict = {}
        else:
            self.order_dict = {}

        # Crea una progress bar più semplice che si aggiorna meno frequentemente
        progress = QProgressBar()
        progress.setWindowTitle("Generazione ordine stratigrafico")
        progress.setGeometry(300, 300, 400, 40)
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(True)
        progress.setFormat("Inizializzazione...")

        try:
            # Utilizziamo la classe Qt di QGIS
            progress.setWindowModality(Qt.WindowModal)
            progress.setAlignment(Qt.AlignCenter)
        except AttributeError:
            pass

        progress.show()
        QApplication.processEvents()
        time.sleep(0.2)  # Pausa per assicurarsi che la UI si aggiorni

        # Controlla se siamo connessi a SQLite
        is_sqlite = False
        try:
            if 'sqlite' in str(self.db.engine.url).lower():
                is_sqlite = True
                print("Rilevata connessione SQLite")
        except:
            print("Impossibile determinare il tipo di database")

        try:
            # Fase 1: Trova la base del matrix
            progress.setValue(10)
            progress.setFormat("Ricerca base matrix...")
            QApplication.processEvents()

            matrix_us_level = self.find_base_matrix()
            if not matrix_us_level:
                progress.setValue(100)
                progress.setFormat("Nessuna base matrix trovata!")
                QApplication.processEvents()
                time.sleep(1)
                progress.close()
                QMessageBox.warning(None, "Attenzione", "Nessuna US di base trovata per iniziare il matrix!")
                return "error"

            progress.setValue(15)
            progress.setFormat("Inserimento dati iniziali...")
            QApplication.processEvents()

            # Inseriamo i dati iniziali nel dizionario
            self.insert_into_dict(matrix_us_level)
            print(f"Inseriti {len(matrix_us_level)} record iniziali nel dizionario")

            # Variabili per il ciclo principale
            test = 0
            start_time = time.time()
            cycle_count = 0

            progress.setValue(20)
            progress.setFormat("Avvio elaborazione...")
            QApplication.processEvents()
            time.sleep(0.2)

            # Array per monitorare quando aggiornare la UI
            update_cycles = [1, 5, 10, 25, 50, 100, 200, 500, 1000, 1500, 2000, 2500, 3000]

            # Ciclo principale
            while test == 0:
                cycle_count += 1

                # Aggiorna progress bar solo in cicli specifici o ogni 100 cicli dopo i primi 500
                should_update = (cycle_count in update_cycles) or (cycle_count > 500 and cycle_count % 100 == 0)

                if should_update:
                    # Calcola percentuale basata sul numero di cicli
                    progress_percentage = 20 + min(75, (cycle_count / max_cycles) * 75)
                    progress.setValue(int(progress_percentage))
                    progress.setFormat(f"Ciclo {cycle_count}/{max_cycles} ({int(progress_percentage)}%)")
                    QApplication.processEvents()
                    print(f"Ciclo {cycle_count}: order_count = {self.order_count}")

                # Ottieni tutti gli elementi US nel dizionario corrente
                rec_list_str = []
                for i in matrix_us_level:
                    rec_list_str.append(str(i))

                # Cerca US che sono uguali o si legano alle US esistenti
                if self.L == 'it':
                    value_list_equal = self.create_list_values(['Uguale a', 'Si lega a', 'Same as', 'Connected to'],
                                                               rec_list_str, self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_equal = self.create_list_values(["Entspricht", "Bindet an"], rec_list_str, self.AREA,
                                                               self.SITO)
                else:
                    value_list_equal = self.create_list_values(['Same as', 'Connected to'], rec_list_str, self.AREA,
                                                               self.SITO)

                # Ottieni i risultati usando la funzione appropriate
                # try:
                res = self.db.query_in_contains(value_list_equal, self.SITO, self.AREA)
                # except Exception as e:
                #     print( f"query_in_contains fallita: {str(e)}")
                #     if is_sqlite:
                #         try:
                #             res = self.db.query_in_contains_onlysqlite(value_list_equal, self.SITO, self.AREA)
                #         except Exception as e2:
                #             print( f"Anche query_in_contains_onlysqlite fallita: {str(e2)}")
                #             res = []
                #     else:
                #         res = []

                # Elabora i risultati per i legami uguali
                matrix_us_equal_level = []
                for r in res:
                    matrix_us_equal_level.append(str(r.us))

                # Aggiungi i risultati al dizionario se ce ne sono
                if matrix_us_equal_level:
                    self.insert_into_dict(matrix_us_equal_level, 1)
                    # if should_update:
                    # print( f"Ciclo {cycle_count}: Aggiunti {len(matrix_us_equal_level)} elementi 'equal'")

                # Combina le liste per la prossima ricerca
                rec = rec_list_str + matrix_us_equal_level

                # Cerca US che sono coperti, riempiti, ecc.
                if self.L == 'it':
                    value_list_post = self.create_list_values(
                        ['>>', 'Copre', 'Riempie', 'Taglia', 'Si appoggia a', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                        self.AREA, self.SITO)
                elif self.L == 'de':
                    value_list_post = self.create_list_values(
                        ['>>', 'Liegt über', 'Verfüllt', 'Schneidet', 'Stützt sich auf'], rec, self.AREA, self.SITO)
                else:
                    value_list_post = self.create_list_values(['>>', 'Covers', 'Fills', 'Cuts', 'Abuts'], rec,
                                                              self.AREA, self.SITO)

                # Ottieni i risultati usando la funzione appropriate
                # try:
                res_t = self.db.query_in_contains(value_list_post, self.SITO, self.AREA)
                # except Exception as e:
                #     print( f"query_in_contains fallita: {str(e)}")
                #     if is_sqlite:
                #         try:
                #             res_t = self.db.query_in_contains_onlysqlite(value_list_post, self.SITO, self.AREA)
                #         except Exception as e2:
                #             print( f"Anche query_in_contains_onlysqlite fallita: {str(e2)}")
                #             res_t = []
                #     else:
                #         res_t = []

                # Elabora i risultati
                matrix_us_level = []
                for e in res_t:
                    matrix_us_level.append(str(e.us))

                # Controlla se è il momento di terminare
                elapsed_time = time.time() - start_time
                if not matrix_us_level or self.order_count >= max_cycles or elapsed_time > max_time:
                    test = 1

                    # Aggiorna la progress bar al 100%
                    progress.setValue(100)

                    if not matrix_us_level:
                        progress.setFormat(f"Completato! Cicli: {cycle_count}, Record: {self.order_count}")
                    elif self.order_count >= max_cycles:
                        progress.setFormat(f"Limite di record raggiunto: {self.order_count}")
                    elif elapsed_time > max_time:
                        progress.setFormat(f"Tempo massimo superato: {int(elapsed_time)}s")

                    QApplication.processEvents()
                    time.sleep(1)
                    progress.close()

                    print(f"Completato! order_count = {self.order_count}, order_dict size = {len(self.order_dict)}")

                    if self.order_count < max_cycles:
                        return self.order_dict
                    else:
                        return "error"
                else:
                    # Aggiungi i nuovi elementi al dizionario
                    previous_count = self.order_count
                    self.insert_into_dict(matrix_us_level, 1)
                    if should_update and (self.order_count > previous_count):
                        print(f"Ciclo {cycle_count}: Aggiunti {self.order_count - previous_count} nuovi elementi")

            # Questa parte non dovrebbe mai essere raggiunta, ma per sicurezza:
            progress.close()
            return self.order_dict if self.order_count < max_cycles else "error"

        except Exception as e:
            # Gestione degli errori
            error_msg = str(e)
            QMessageBox.information(None, "Avviso", f"Errore nell'elaborazione: {error_msg}")

            progress.setValue(100)
            short_error = error_msg[:30] + "..." if len(error_msg) > 30 else error_msg
            progress.setFormat(f"Errore: {short_error}")
            QApplication.processEvents()
            time.sleep(1)
            progress.close()

            QMessageBox.warning(None, "Attenzione",
                                f"Errore durante la generazione dell'order layer: {error_msg}\n" +
                                "La lista delle us generate supera il limite o si è verificato un errore.\n" +
                                "Usare Postgres per generare l'order layer")
            return "error"

    def find_base_matrix(self):
        res = self.db.select_not_like_from_db_sql(self.SITO, self.AREA)

        rec_list = []
        for rec in res:
            rec_list.append(str(rec.us))
        # QMessageBox.warning(None, "Messaggio", "find base_matrix by sql" + str(rec_list), QMessageBox.Ok)
        return rec_list

    def create_list_values(self, rapp_type_list, value_list, ar, si):
        self.rapp_type_list = rapp_type_list
        self.value_list = value_list
        self.ar = ar
        self.si = si

        value_list_to_find = []
        # QMessageBox.warning(None, "rapp1", str(self.rapp_type_list) + '-' + str(self.value_list), QMessageBox.Ok)
        for sing_value in self.value_list:
            for sing_rapp in self.rapp_type_list:
                sql_query_string = "['%s', '%s', '%s', '%s']" % (sing_rapp, sing_value, self.ar, self.si)  # funziona!!!

                value_list_to_find.append(sql_query_string)

        # QMessageBox.warning(None, "rapp1", str(value_list_to_find), QMessageBox.Ok)
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
