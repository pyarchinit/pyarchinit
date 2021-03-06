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
 *   (at your option) any later version.  #simple                          *
 *                                                                         *
 ***************************************************************************/
"""

import os

from builtins import object
from builtins import range
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.core import QgsProject, QgsDataSourceUri, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsSettings,QgsEditorWidgetSetup
from qgis.gui import QgsMapCanvas

from ..utility.settings import Settings


class Pyarchinit_pyqgis(QDialog):
    HOME = os.environ['PYARCHINIT_HOME']
    FILEPATH = os.path.dirname(__file__)
    LAYER_STYLE_PATH = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles', os.sep)
    LAYER_STYLE_PATH_SPATIALITE = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles_spatialite', os.sep)
    SRS = 3004
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
                  "28": "pyarchinit_sezioni_view"
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
                              "pyunitastratigrafiche": "Unita Stratigrafiche disegno",
                              "pyarchinit_documentazione": "Resgistro documentazione",
                              "pyarchinit_doc_view": "Documentazione Vista",
                              "pyarchinit_us_negative_doc": "US Negative per sezioni/elevati",
                              "pyarchinit_us_negative_doc_view": "Vista US Negative per sezioni/elevati",
                              "pyarchinit_site_view": "Localizzazione siti Vista",
                              "pyarchinit_siti_polygonal": "Perimetrazione siti poligonali",
                              "pyarchinit_siti_polygonal_view": "Perimetrazione siti poligonali Vista",
                              "pyarchinit_site_view": "Localizzazione siti puntuale Vista",
                              "pyarchinit_strutture_view": "Ipotesi strutture da scavo Vista",
                              "pyarchinit_tomba_view": "Tomba View",
                              "pyarchinit_tafonomia": "Tomba",
                              "pyarchinit_doc_view_b": "Documentazione Vista B",
                              "pyarchinit_reperti": "Reperti",
                              "pyarchinit_reperti_view": "Reperti view",
                              "pyarchinit_sezioni_view": "Sezioni di scavo Vista",

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
                              "pyarchinit_site_view": "Genauer Ausgrabungsstättenbereich Ansicht",
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
                              "pyarchinit_site_view": "Site view",
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
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_us = '" + str(data[0]) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = '" + str(data[i]) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            
                
            uri.setDataSource('', 'pyarchinit_us_view', 'Geometry', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, 'spatialite')
            ###################################################################
            if layerUS.isValid():
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_caratterizzazioni.qml')
                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            
            uri.setDataSource('', 'pyarchinit_quote_view', 'Geometry', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), name_layer_q, 'spatialite')

            if layerQUOTE.isValid():
                QgsProject.instance().addMapLayers([layerQUOTE], True)


        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "id_us = " + str(data[0])
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = " + str(data[i])

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, "postgres")

            if layerUS.isValid():
                layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)

            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), name_layer_q, "postgres")

            if layerQUOTE.isValid():
                layerQUOTE.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    QgsProject.instance().addMapLayers([layerQUOTE], True)
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
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_us = '" + str(self.idus) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, 'spatialite')

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer valid", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), name_layer_q, 'spatialite')

            if layerQUOTE.isValid():
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer valid", QMessageBox.Ok)

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "id_us = " + str(self.idus)

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(),name_layer_s , "postgres")

            if layerUS.isValid():
                layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayersID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer US non valido", QMessageBox.Ok)

            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), name_layer_q, "postgres")

            if layerQUOTE.isValid():
                layerQUOTE.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    QgsProject.instance().addMapLayers([layerQUOTE], True)
                except Exception as e:
                    pass
                    # f = open('/test_ok.txt','w')
                    # f.write(str(e))
                    # f.close()
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Quote non valido", QMessageBox.Ok)
        
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
        

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

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
                QMessageBox.warning(self, "TESTER", "Layer Sezioni valido", QMessageBox.Ok)
                QgsProject.instance().addMapLayers([layerPos], True)
           
            else:
                QMessageBox.warning(self, "TESTER", "Layer Sezioni non valido", QMessageBox.Ok)
            
            
            
            
            
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
                QMessageBox.warning(self, "TESTER", "Layer Registro Documentazione valido", QMessageBox.Ok)
                QgsProject.instance().addMapLayers([layerPos], True)
           
            else:
                QMessageBox.warning(self, "TESTER", "Layer Registro Documentazione non valido", QMessageBox.Ok)
                


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
                QMessageBox.warning(self, "TESTER", "OK Layer US Negative valido", QMessageBox.Ok)
                QgsProject.instance().addMapLayers([layerNeg], True)
              
                
            else:
                QMessageBox.warning(self, "TESTER", "Layer US Negative non valido", QMessageBox.Ok)
            
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
            

            layer_name_pos = "US Positive - "+ str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)

            uri.setDataSource("public", 'pyarchinit_us_view', 'the_geom', docstr, "ROWID")
            
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'spatialite')

            if layerPos.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)
                QgsProject.instance().addMapLayers([layerPos], True)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(layerPos.extent())
            
            
        elif settings.SERVER == 'postgres':
            

            
            uri = QgsDataSourceUri()
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
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
            

            layer_name_pos = str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)

            uri.setDataSource("", 'pyarchinit_us_view', 'the_geom', docstr, "gid")
            
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'postgres')

            if layerPos.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)
                QgsProject.instance().addMapLayers([layerPos], True)
                self.canvas = QgsMapCanvas()
                self.canvas.setExtent(layerPos.extent())


            layer_name_neg = str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc) + " - negative"

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
                QMessageBox.warning(self, "TESTER", "OK Layer US Negative valido", QMessageBox.Ok)
                QgsProject.instance().addMapLayers([layerNeg], True)

              

            else:
                QMessageBox.warning(self, "TESTER", "Layer US Negative non valido", QMessageBox.Ok)
            
            
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
            
            
            layer_name_pos = str(data[0].tipo_documentazione) + ": " + str(data[0].nome_doc)
            uri.setDataSource("", 'pyarchinit_doc_view', 'the_geom', docstr, "gid")
            ##          uri.setDataSource('','pyarchinit_doc_view_b', 'the_geom', docstr, "ROWID")
            layerPos = QgsVectorLayer(uri.uri(), layer_name_pos, 'postgres')
            if layerPos.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)
                QgsProject.instance().addMapLayers([layerPos], True)
                #self.canvas = QgsMapCanvas()
                #self.canvas.setExtent(layerPos.extent())
            else:
                QMessageBox.warning(self, "TESTER", "Layer US non valido", QMessageBox.Ok)
                

          

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
            name_layer_s_n='US negative view'
        elif self.L=='de':
            name_layer_s_n='SE negative view'
        else:
            name_layer_s_n='SU negative view'   
            
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            doc_from_us_str = "sito = '" + sito + "' AND tipo_doc = '" + tipo_documentazione + "' AND nome_doc = '" + nome_doc + "'"
            # if len(data) > 1:
            # for i in range(len(data)):
            # doc_from_us_str += " OR (sito = '" + str(data[i].sito) +" AND tipo_documentazione = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_doc_view', 'the_geom', doc_from_us_str, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_d, 'spatialite')

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
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
                QMessageBox.warning(self, "TESTER", "OK Layer US negative valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUSneg], True)
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
                QMessageBox.warning(self, "TESTER", "OK Layer valid", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "TESTER", "Layer US non valido", QMessageBox.Ok)

                # implementare sistema per quote se si vogliono visualizzare sulle piante
            """
            uri.setDataSource('','pyarchinit_quote_view', 'the_geom', gidstr.tipodoc(pianta), "ROWID")
            layerQUOTE=QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if  layerQUOTE.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Quote non valido",QMessageBox.Ok)
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
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
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
                QMessageBox.warning(self, "TESTER", "OK Layer US negative valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUSneg], True)
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
                QMessageBox.warning(self, "TESTER", "OK Layer valid", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "TESTER", "Layer US non valido", QMessageBox.Ok)

                # implementare sistema per quote se si vogliono visualizzare sulle piante
            """
            uri.setDataSource('','pyarchinit_quote_view', 'the_geom', gidstr.tipodoc(pianta), "ROWID")
            layerQUOTE=QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if  layerQUOTE.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Quote non valido",QMessageBox.Ok)
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
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_us = '" + str(data[0].id_us) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = '" + str(data[i].id_us) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, 'spatialite')

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                # style_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.LAYER_STYLE_PATH)

                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
                # originalSubsetString = layerUS.subsetString() 4D dimension
                # newSubSetString = "%s OR id_us = '0'" % (originalSubsetString) 4D dimension

                # layerUS.setSubsetString(newSubSetString)

            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), name_layer_q, 'spatialite')

            if layerQUOTE.isValid():
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer not valid", QMessageBox.Ok)

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "id_us = " + str(data[0].id_us)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = " + str(data[i].id_us)

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer_s, "postgres")

            if layerUS.isValid():
                layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayersID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer US non valido", QMessageBox.Ok)

            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), name_layer_q, "postgres")

            if layerQUOTE.isValid():
                layerQUOTE.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    QgsProject.instance().addMapLayers([layerQUOTE], True)
                except Exception as e:
                    pass
                    # f = open('/test_ok.txt','w')
                    # f.write(str(e))
                    # f.close()
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer not valide", QMessageBox.Ok)

    def charge_vector_layers_periodo(self, sito_p, cont_per, per_label, fas_label):
        self.sito_p = sito_p
        self.cont_per = str(cont_per)
        self.per_label = per_label
        self.fas_label = fas_label
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
            layer_name_label_us = "Unita Stratigrafiche - Per: %s / Fas: %s" % (self.per_label, self.fas_label)
            layer_name_label_quote = "Quote US - Per: %s / Fas: %s" % (self.per_label, self.fas_label)
        elif self.L=='de':
            layer_name_label_us = "Stratigraphischen Einheiten  - Period: %s / Phase: %s" % (self.per_label, self.fas_label)
            layer_name_label_quote = "Nivellements der SE - Period: %s / Phase: %s" % (self.per_label, self.fas_label)
        else:
            layer_name_label_us = "Stratigraphic Units - Per: %s / Phase: %s" % (self.per_label, self.fas_label)
            layer_name_label_quote = "Elevations SU - Per: %s / Phase: %s" % (self.per_label, self.fas_label)
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', cont_per_string, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, 'spatialite')

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer US non valido", QMessageBox.Ok)

            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', cont_per_string, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, 'spatialite')

            if layerQUOTE.isValid():
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], True)

        elif settings.SERVER == 'postgres':
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            cont_per_string = "sito = '" + self.sito_p + "' AND (" + " cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%')"

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", cont_per_string, "gid")
            layerUS = QgsVectorLayer(uri.uri(), layer_name_label_us, "postgres")
            if layerUS.isValid():
                layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer US non valido", QMessageBox.Ok)

            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", cont_per_string, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), layer_name_label_quote, "postgres")
            if layerQUOTE.isValid():
                layerQUOTE.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                layerQUOTE.loadNamedStyle(style_path)
                try:
                    QgsProject.instance().addMapLayers([layerQUOTE], True)
                except Exception as e:
                    pass
                    # f = open('/test_ok.txt','w')
                    # f.write(str(e))
                    # f.close()


                ##"""
                ##  def find_us_cutted(self, gl):
                ##      gid_list = gl
                ##      lista_rapporti = []
                ##      for i in range(len(gid_list)):
                ##          lista_rapporti.append([gid_list[i].sito,
                ##                                  gid_list[i].area,
                ##                                  gid_list[i].us,
                ##                                  gid_list[i].rapporti])
                ##
                ##      for i in lista_rapporti:
                ##          pass
                ##      """

    def loadMapPreview(self, gidstr):
        """ if has geometry column load to map canvas """
        layerToSet = []
        srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
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

            # layerUS
            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, "id_us")
            layerUS = QgsVectorLayer(uri.uri(), "Unita' Stratigrafiche", "postgres")

            if layerUS.isValid():
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                layerToSet.append(layerUS)

                # layerQuote
            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "id_us")
            layerQUOTE = QgsVectorLayer(uri.uri(), "pyarchinit_quote_view", "postgres")

            if layerQUOTE.isValid():
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                # layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
                layerToSet.append(layerQUOTE)

            return layerToSet

        elif settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            # layerQuote
            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if layerQUOTE.isValid():
                ###QMessageBox.warning(self, "TESTER", "OK Layer Quote valido",#QMessageBox.Ok)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
                layerToSet.append(layerQUOTE)
            else:
                pass
                # QMessageBox.warning(self, "TESTER", "OK Layer Quote non valido",   #QMessageBox.Ok)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                # QMessageBox.warning(self, "TESTER", "OK ayer US valido",   #QMessageBox.Ok)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                layerToSet.append(layerUS)
            else:
                pass
                # QMessageBox.warning(self, "TESTER", "NOT! Layer US not valid",#QMessageBox.Ok)

            return layerToSet

    def loadMapPreviewDoc(self,docstr):
        """ if has geometry column load to map canvas """
        layerToSet = []
        srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
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
            docstr = ' "nome_doc" = \'A-B\' '
            # layerUS
            ##          uri.setDataSource("public", "pyarchinit_us_view", "the_geom", sing_layer, "id_us")
            uri.setDataSource("public", "pyarchinit_us_view", "the_geom", docstr, "id_us")
            layerUS = QgsVectorLayer(uri.uri(), "pyarchinit_doc_view_b", "postgres")

            if layerUS.isValid():
                QMessageBox.warning(self, "WARNING", "OK layer ", QMessageBox.Ok)
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
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            # docstr =  docstr
            docstr = ' "nome_doc" = \'A-B\' '

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', docstr, "ROWID")

            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK ayer US valido", QMessageBox.Ok)
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                layerToSet.append(layerUS)
            else:
                QMessageBox.warning(self, "TESTER", "NOT! Layer US not valid", QMessageBox.Ok)

            ##          docstrn =  "sito_n = '" + str(data[0].sito) + "' AND nome_doc_n = '" + str(data[0].nome_doc) + "' AND tipo_doc_n = '" + str(data[0].tipo_documentazione) + "'"
            ##          if len(data) > 1:
            ##              for i in range(len(data)):
            ##                  docstr += " OR (sito = '" + str(data[i].sito) +"' AND tipo_doc = '" + str(data[i].tipo_documentazione) +" AND nome_doc = '"+ str(data[i].nome_doc)+ "')"
            ##
            ##          f = open("/test_preview.txt", "w")
            ##
            ##          f.write()

            ##          uri.setDataSource('','pyarchinit_us_negative_doc_view', 'the_geom', docstrn, "ROWID")
            ##          layerUSn=QgsVectorLayer(uri.uri(), 'pyarchinit_us_negative_doc_view', 'spatialite')
            ##
            ##          if layerUSn.isValid() == True:
            ##              #QMessageBox.warning(self, "TESTER", "OK ayer US valido",    #QMessageBox.Ok)
            ####                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
            ####                layerUSn.loadNamedStyle(style_path)
            ##              QgsProject.instance().addMapLayers([layerUSn], False)
            ##              layerToSet.append(QgsMapCanvas(layerUSn, True, False))
            ##          else:
            ##              pass
            ##              #QMessageBox.warning(self, "TESTER", "NOT! Layer US not valid",#QMessageBox.Ok)

            return layerToSet

    """
    def addRasterLayer(self):
        fileName = "/rimini_1_25000/Rimini_25000_g.tif"
        fileInfo = QFileInfo(fileName)
        baseName = fileInfo.baseName()
        rlayer = QgsRasterLayer(fileName, baseName)

        if not rlayer.isValid():
            #QMessageBox.warning(self, "TESTER", "PROBLEMA DI CARICAMENTO RASTER" + str(baseName),   #QMessageBox.Ok)

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

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'" + str(layer_name) + "'"
                cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
                eval(cmq_set_uri_data_source)
                layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                layer_label_conv = "'" + layer_label + "'"
                cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
                layer = eval(cmq_set_vector_layer)
                
                if layer.isValid():
                    # self.USLayerId = layerUS.getLayerID()
                    ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    ##ayerUS.loadNamedStyle(style_path)
                    QgsProject.instance().addMapLayers([layer], True)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer not valid: " + str(layer_name), QMessageBox.Ok)

                ###AGGIUNGERE IL SISTEMA PER POSTGRES#####
        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'" + str(layer_name) + "'"
                cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
                eval(cmq_set_uri_data_source)
                layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                layer_label_conv = "'" + layer_label + "'"
                cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
                layer = eval(cmq_set_vector_layer)
                #fieldIndex = layer.fields().indexFromName( 'scavo_s' )
                #editor_widget_setup = QgsEditorWidgetSetup( 'ValueMap', {
                #                         'map': {u'Description 1': u'value1',
                #                                 u'Description 2': u'value2'}
                #                        }
                #                      )
                #layer.setEditorWidgetSetup( fieldIndex, editor_widget_setup )
                if layer.isValid():
                    layer.setCrs(srs)
                    # self.USLayerId = layerUS.getLayerID()
                    ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    ##ayerUS.loadNamedStyle(style_path)
                    QgsProject.instance().addMapLayers([layer], True)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
        
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

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'" + str(layer_name) + "'"
                value_conv = ('"%s = %s"') % (self.col, "'" + str(self.val) + "'")
                cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (
                layer_name_conv, "'the_geom'", value_conv)
                eval(cmq_set_uri_data_source)
                layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                layer_label_conv = "'" + layer_label + "'"
                cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
                layer = eval(cmq_set_vector_layer)

                if layer.isValid():
                    # self.USLayerId = layerUS.getLayerID()
                    ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    ##ayerUS.loadNamedStyle(style_path)
                    self.iface.mapCanvas().setExtent(layer.extent())
                    QgsProject.instance().addMapLayers([layer], True)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer not valid: {}".format(layer.name()), QMessageBox.Ok)

                    # pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
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
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

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
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
            
                
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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)    
            
            
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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
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
                # self.USLayerId = layerUS.getLayerID()
                ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
            
            
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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
            layer_name = 'pyarchinit_sezioni'
            layer_name_conv = "'" + str(layer_name) + "'"
            value_conv = ('"siti = %s"') % ("'" + str(self.val) + "'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'" + layer_label + "'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer = eval(cmq_set_vector_layer)

            if layer.isValid():
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

            ###AGGIUNGERE IL SISTEMA PER POSTGRES#####
        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'" + str(layer_name) + "'"
                value_conv = ('"%s = %s"') % (self.col, "'" + str(self.val) + "'")
                cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (
                layer_name_conv, "'the_geom'", value_conv)
                eval(cmq_set_uri_data_source)
                layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                layer_label_conv = "'" + layer_label + "'"
                cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
                layer = eval(cmq_set_vector_layer)

                if layer.isValid():
                    layer.setCrs(srs)
                    # self.USLayerId = layerUS.getLayerID()
                    ##style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    ##ayerUS.loadNamedStyle(style_path)
                    QgsProject.instance().addMapLayers([layer], True)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

                    # pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            
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
                layer.setCrs(srs)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
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
                layer.setCrs(srs)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
                
                
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
                layer.setCrs(srs)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)
            
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
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)  
            
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
                layer.setCrs(srs)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

            
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
                layer.setCrs(srs)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

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
                layer.setCrs(srs)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer not valid", QMessageBox.Ok)

            
            

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

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "sito_nome= '" + str(data[0].sito) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR sito_nome = '" + str(data[i].sito) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_site_view', 'the_geom', gidstr, "ROWID")
            layerSITE = QgsVectorLayer(uri.uri(), 'pyarchinit_site_view', 'spatialite')

            if layerSITE.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer Sito valido", QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layerSITE.extent())
                QgsProject.instance().addMapLayers([layerSITE], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer US non valido", QMessageBox.Ok)

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
                QMessageBox.warning(self, "TESTER", "OK Layer Sito valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerSITE.extent())
                QgsProject.instance().addMapLayers([layerSITE], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer US non valido", QMessageBox.Ok)
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
        
        if self.L=='it':
            name_layer='Reperti view'
        elif self.L=='de':
            name_layer='ArtefaKt view'
        else:
            name_layer='Artefact view'
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "numero_inventario = '" + str(data[0].numero_inventario) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR numero_inventario = '" + str(data[i].numero_inventario) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_reperti_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, 'spatialite')

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                

                
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer not valid", QMessageBox.Ok)    
            

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "numero_inventario = " + str(data[0].numero_inventario)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR numero_inventario = " + str(data[i].numero_inventario)

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_reperti_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, "postgres")

            if layerUS.isValid():
                layerUS.setCrs(srs)
                
               
                QgsProject.instance().addMapLayers([layerUS], True)
           
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer not valid", QMessageBox.Ok)
    
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
        
        if self.L=='it':
            name_layer='Tomba view'
        elif self.L=='de':
            name_layer='ArtefaKt view'
        else:
            name_layer='Artefact view'
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "nr_scheda_taf = '" + str(data[0].nr_scheda_taf) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR nr_scheda_taf = '" + str(data[i].nr_scheda_taf) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_tomba_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, 'spatialite')

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                

                
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer not valid", QMessageBox.Ok)    
            

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "nr_scheda_taf = " + str(data[0].nr_scheda_taf)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR nr_scheda_taf = " + str(data[i].nr_scheda_taf)

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_tomba_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), name_layer, "postgres")

            if layerUS.isValid():
                layerUS.setCrs(srs)
                
               
                QgsProject.instance().addMapLayers([layerUS], True)
           
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer not valid", QMessageBox.Ok)
    
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

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_struttura = '" + str(data[0].id_struttura) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_struttura = '" + str(data[i].id_struttura) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_strutture_view', 'the_geom', gidstr, "ROWID")
            layerSTRUTTURA = QgsVectorLayer(uri.uri(), 'pyarchinit_strutture_view', 'spatialite')

            if layerSTRUTTURA.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer Struttura valido", QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layerSTRUTTURA.extent())
                QgsProject.instance().addMapLayers([layerSTRUTTURA], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Struttura non valido", QMessageBox.Ok)

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
                QMessageBox.warning(self, "TESTER", "OK Layer Struttura valido", QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layerSTRUTTURA.extent())
                QgsProject.instance().addMapLayers([layerSTRUTTURA], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Struttura non valido", QMessageBox.Ok)

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

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_scheda_ind = '" + str(data[0].id_scheda_ind) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_scheda_ind = '" + str(data[i].id_scheda_ind) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_individui_view', 'the_geom', gidstr, "ROWID")
            layerIndividui = QgsVectorLayer(uri.uri(), 'pyarchinit_individui_view', 'spatialite')

            if layerIndividui.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer Individui valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Individui non valido", QMessageBox.Ok)

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = "id_scheda_ind = '" + str(data[0].id_scheda_ind) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_scheda_ind = '" + str(data[i].id_scheda_ind) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_individui_view', 'the_geom', gidstr, "gid")
            layerIndividui = QgsVectorLayer(uri.uri(), 'pyarchinit_individui_view', 'postgres')

            if layerIndividui.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer Individui valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                ##              style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Individui non valido", QMessageBox.Ok)


class Order_layers_DEPRECATED(object):
    HOME = os.environ['PYARCHINIT_HOME']

    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")

    LISTA_US = []  # lista che contiene tutte le US singole prese dai singoli rapporti stratigrafici
    DIZ_ORDER_LAYERS = {}  # contiene una serie di chiavi valori dove la chiave e' il livello di ordinamento e il valore l'US relativa
    MAX_VALUE_KEYS = -1  # contiene l'indice progressivo dei livelli del dizionario
    TUPLE_TO_REMOVING = []  # contiene le tuple da rimuovere dai rapporti stratigrafici man mano che si passa ad un livello successivo
    LISTA_RAPPORTI = ""

    """variabili di controllo di paradossi nei rapporti stratigrafici"""
    status = 0  # contiene lo stato della lunghezza della lista dei rapporti stratigrafici
    check_status = 0  # il valore aumenta se la lunghezza della lista dei rapporti stratigrafici non cambia. Va in errore dopo 4000 ripetizioni del loop stratigraficocambia
    stop_while = ''  # assume il valore 'stop' dopo 4000 ripetizioni ed esce dal loop

    def __init__(self, lr):
        self.LISTA_RAPPORTI = lr  # istanzia la classe con una lista di tuple rappresentanti i rapporti stratigrafici
        # f = open('C:\\test_matrix_1.txt', 'w') #to delete
        # f.write(str(self.lista_rapporti))
        # f.close()
        self.LISTA_RAPPORTI.sort()  # ordina la lista dei rapporti stratigrafici E' IN POSIZIONE GIUSTA??? MEGLIO DENTRO AL WHILE?
        self.status = len(
            self.LISTA_RAPPORTI)  # assegna la lunghezza della lista dei rapporti per verificare se cambia nel corso del loop

        # print self.lista_rapporti

    def main(self):
        # esegue la funzione per creare la lista valori delle US dai singoli rapporti stratigrafici
        self.add_values_to_lista_us()  # fin qui  e' ok controllo da ufficio
        # finche la lista US contiene valori la funzione bool ritorna True e il ciclo while prosegue NON E' VVVEROOO!!

        len_lista = len(self.LISTA_RAPPORTI)

        while bool(self.LISTA_RAPPORTI) == True and self.stop_while == '':
            # viene eseguito il ciclo per ogni US contenuto nella lista delle US
            # QMessageBox.warning(self, "TESTER", str(self.LISTA_RAPPORTI), #QMessageBox.Ok)
            self.loop_on_lista_us()
            # dovrebbero rimanere le US che non hanno altre US, dopo
        if bool(self.LISTA_RAPPORTI) == False and bool(self.LISTA_US) == True:
            for sing_us in self.LISTA_US:
                self.add_key_value_to_diz(sing_us)
        return self.DIZ_ORDER_LAYERS

    ##BLOCCO OK
    def add_values_to_lista_us(self):
        # crea la lista valori delle US dai singoli rapporti stratigrafici
        for i in self.LISTA_RAPPORTI:
            if i[0] == i[1]:
                msg = str(i)
                filename_errori_in_add_value = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'errori_in_add_value.txt')
                f = open(filename_errori_in_add_value, "w")
                f.write(msg)
                f.close()
                # self.stop_while = "stop"
            else:
                if self.LISTA_US.count(i[0]) == 0:
                    self.LISTA_US.append(i[0])
                if self.LISTA_US.count(i[1]) == 0:
                    self.LISTA_US.append(i[1])
        self.LISTA_US.sort()

        filename_errori_in_add_value = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'test_lista_us.txt')
        f = open(filename_errori_in_add_value, "w")
        f.write(str(self.LISTA_US))
        f.close()

        # print "lista us", str(self.LISTA_US)

    ##BLOCCO OK

    def loop_on_lista_us(self):
        # se il valore di stop_while rimane vuoto (ovvero non vi sono paradossi stratigrafici) parte la ricerca del livello da assegnare all'US
        ##      if self.stop_while == '':
        for i in self.LISTA_US:
            if self.check_position(
                    i) == 1:  # se la funzione check_position ritorna 1 significa che e' stata trovata l'US che va nel prossimo livello e in seguito viene rimossa
                self.LISTA_US.remove(i)
            else:
                # se il valore ritornato e' 0 significa che e' necessario passare all'US successiva in lista US e la lista delle tuple da rimuovere e' svuotata
                self.TUPLE_TO_REMOVING = []
                # se il valore di status non cambia significa che non e' stata trovata l'US da rimuovere. Se cio' accade per + di 4000 volte e' possibile che vi sia un paradosso e lo script va in errore
            if self.status == len(self.LISTA_RAPPORTI):
                self.check_status += 1
                # print self.check_status
                if self.check_status > 10:
                    self.stop_while = ''
            else:
                # se entro le 4000 ricerche il valore cambia il check status torna a 0 e lo script va avanti
                self.check_status = 0

    def check_position(self, n):
        # riceve un numero di US dalla lista_US
        num_us = n
        # assegna 0 alla variabile check
        check = 0
        # inizia l'iterazione sUlla lista rapporti
        for i in self.LISTA_RAPPORTI:
            # se la tupla assegnata a i contiene in prima posizione il numero di US, ovvero e' un'US che viene dopo le altre nella sequenza, check diventa 1 e non si ha un nuovo livello stratigrafico
            if i[1] == num_us:
                # print "num_us", num_us
                check = 1
                self.TUPLE_TO_REMOVING = []
                # break
                # se invece il valore e' sempre e solo in posizione 1, ovvero e' in cima ai rapporti stratigrafici viene assegnata la tupla di quei rapporti stratigrafici per essere rimossa in seguito
            elif i[0] == num_us:
                msg = "check_tuple: \n" + str(i) + "  Lista rapporti presenti: \n" + str(
                    self.LISTA_RAPPORTI) + '---' + str(i)
                filename_check_position = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'check_tuple.txt')
                f = open(filename_check_position, "w")
                f.write(msg)
                f.close()
                self.TUPLE_TO_REMOVING.append(i)
                # se alla fine dell'iterazione check e' rimasto 0, significa che quell'US e' in cima ai rapporti stratigrafici e si passa all'assegnazione di un nuovo livello stratigrafico nel dizionario
        if bool(self.TUPLE_TO_REMOVING):
            # viene eseguita la funzione di aggiunta valori al dizionario passandogli il numero di US
            self.add_key_value_to_diz(num_us)
            # vengono rimosse tutte le tuple in cui e' presente l'us assegnata al dizionario e la lista di tuple viene svuotata
            for i in self.TUPLE_TO_REMOVING:
                try:
                    self.LISTA_RAPPORTI.remove(i)
                except Exception as e:
                    msg = "check_position: \n" + str(i) + "  Lista rapporti presenti: \n" + str(
                        self.LISTA_RAPPORTI) + str(e)
                    filename_check_position = '{}{}{}'.format(self.REPORT_PATH, os.sep, 'check_position.txt')
                    f = open(filename_check_position, "w")
                    f.write(msg)
                    f.close()
            self.TUPLE_TO_REMOVING = []
            # la funzione ritorna il valore 1
            return 1

    def add_key_value_to_diz(self, n):
        self.num_us_value = n  # numero di US da inserire nel dizionario
        self.MAX_VALUE_KEYS += 1  # il valore globale del numero di chiave aumenta di 1
        self.DIZ_ORDER_LAYERS[
            self.MAX_VALUE_KEYS] = self.num_us_value  # viene assegnata una nuova coppia di chiavi-valori


class Order_layer_v2(object):
    order_dict = {}
    order_count = 0
    db = ''  # Pyarchinit_db_management('sqlite:////Users//Windows//pyarchinit_DB_folder//pyarchinit_db.sqlite')
    # db.connection()
    L=QgsSettings().value("locale/userLocale")[0:2]
    SITO = ""
    AREA = ""

    def __init__(self, dbconn, SITOol, AREAol):
        self.db = dbconn
        self.SITO = SITOol
        self.AREA = AREAol

    def main_order_layer(self):
        # ricava la base delle us del matrix a cui non succedono altre US
        matrix_us_level = self.find_base_matrix()

        self.insert_into_dict(matrix_us_level)
        # il test per il ciclo while viene settato a 0(zero)
        test = 0
        while test == 0:
            rec_list_str = []
            for i in matrix_us_level:
                rec_list_str.append(str(i))
                # cerca prima di tutto se ci sono us uguali o che si legano alle US sottostanti
            if self.L=='it':
                value_list_equal = self.create_list_values(['Uguale a', 'Si lega a'], rec_list_str)
            elif self.L=='de':
                value_list_equal = self.create_list_values(["Entspricht", "Bindet an"], rec_list_str)
            else:
                value_list_equal = self.create_list_values(['Same as','Connected to'], rec_list_str)
            
            res = self.db.query_in_contains(value_list_equal, self.SITO, self.AREA)

            matrix_us_equal_level = []
            for r in res:
                matrix_us_equal_level.append(str(r.us))

            if matrix_us_equal_level:
                self.insert_into_dict(matrix_us_equal_level, 1)
                # se res bool == True

                # aggiunge le us al dizionario nel livello in xui trova l'us uguale a cui è uguale
                # se l'US è già presente non la aggiunge
                # le us che derivano dall'uguaglianza vanno aggiunte al rec_list_str
            rec = rec_list_str+matrix_us_equal_level#rec_list_str+
            if self.L=='it':
                value_list_post = value_list_equal = self.create_list_values(['Copre', 'Riempie', 'Taglia', 'Si appoggia a'], rec)
            elif self.L=='de':
                value_list_post = value_list_equal = self.create_list_values(["Liegt über","Verfüllt","Schneidet","Stützt sich auf"], rec)
            else:
                value_list_post = value_list_equal = self.create_list_values(["Covers","Fills","Cuts","Abuts"], rec)
            
            res_t = self.db.query_in_contains(value_list_post, self.SITO, self.AREA)

            matrix_us_level = []
            for e in res_t:
                matrix_us_level.append(str(e.us))
                #QMessageBox.warning(self, "Errore", str(matrix_us_level), QMessageBox.Ok)
            if not matrix_us_level:
                test = 1
                return self.order_dict
            elif self.order_count >=500:
                test = 1
                #QMessageBox.warning(self, "Errore", str(self.order_dict), QMessageBox.Ok)

                return "error"
            else:
                self.insert_into_dict(matrix_us_level, 1)

    def find_base_matrix(self):
        res = self.db.select_not_like_from_db_sql(self.SITO, self.AREA)
        rec_list = []
        for rec in res:
            rec_list.append(str(rec.us))
        return rec_list

    def create_list_values(self, rapp_type_list, value_list):
        self.rapp_type_list = rapp_type_list
        self.value_list = value_list

        value_list_to_find = []
        for sing_value in self.value_list:
            for sing_rapp in self.rapp_type_list:
                sql_query_string = "['%s', '%s']" % (sing_rapp, sing_value)  # funziona!!!
                value_list_to_find.append(sql_query_string)
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
