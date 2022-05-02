#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
from builtins import str
from builtins import range
from builtins import object

from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.core import QgsProject, QgsDataSourceUri, QgsVectorLayer, QgsCoordinateReferenceSystem

from ..utility.settings import Settings


class Pyarchinit_pyqgis(QDialog):
    HOME = os.environ['PYARCHINIT_HOME']
    FILEPATH = os.path.dirname(__file__)
    LAYER_STYLE_PATH = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles', os.sep)
    LAYER_STYLE_PATH_SPATIALITE = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles_spatialite', os.sep)
    SRS = 3004

    USLayerId = ""

    def __init__(self, iface):
        super().__init__()
        self.iface = iface

    def remove_USlayer_from_registry(self):
        QgsProject.instance().removeMapLayer(self.USLayerId)
        return 0

    def charge_individui_us(self, data):
        # Clean Qgis Map Later Registry
        # QgsMapLayerRegistry.instance().removeAllMapLayers()
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
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = id_us = "id_us = '" + str(data[0]) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = '" + str(data[i]) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'Geometry', gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')
            ###################################################################�
            if layerUS.isValid():
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_caratterizzazioni.qml')
                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)

            uri.setDataSource('', 'pyarchinit_quote_view', 'Geometry', gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if layerQUOTE.isValid():
                QgsProject.instance().addMapLayers([layerQUOTE], True)


        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "id_archzoo = " + str(data[0])
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_archzoo = " + str(data[i])

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_archeozoo_view", "the_geom", gidstr, "gid")
            layerUS = QgsVectorLayer(uri.uri(), "Fauna", "postgres")

            if layerUS.isValid():
                layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)

            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), "Quote Unita' Stratigrafiche", "postgres")

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

    def charge_vector_layers(self, data):
        # Clean Qgis Map Later Registry
        # QgsMapLayerRegistry.instance().removeAllMapLayers()
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
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_us = '" + str(data[0].id_us) + "'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_us = '" + str(data[i].id_us) + "'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer US non valido", QMessageBox.Ok)

            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if layerQUOTE.isValid():
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Quote non valido", QMessageBox.Ok)

        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr = id_us = "id_archzoo = " + str(data[0].id_archzoo)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_archzoo = " + str(data[i].id_archzoo)

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public", "pyarchinit_archeozoo_view", "the_geom", gidstr, "id")
            layerUS = QgsVectorLayer(uri.uri(), "Fauna", "postgres")

            if layerUS.isValid():
                layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayersID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_caratterizzazioni.qml')
                style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer US non valido", QMessageBox.Ok)

            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), "Quote Unita' Stratigrafiche", "postgres")

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

    def charge_vector_layers_periodo(self, cont_per):
        self.cont_per = str(cont_per)
        # Clean Qgis Map Later Registry
        # QgsMapLayerRegistry.instance().removeAllMapLayers()
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
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            cont_per_string = "cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%'"

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', cont_per_string, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            if layerUS.isValid():
                QMessageBox.warning(self, "TESTER", "OK Layer US valido", QMessageBox.Ok)

                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer US non valido", QMessageBox.Ok)

            uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', cont_per_string, "ROWID")
            layerQUOTE = QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

            if layerQUOTE.isValid():
                # self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'quote_us_view.qml')
                layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], True)

        elif settings.SERVER == 'postgres':
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            # cont_per_string =  "cont_per = '" + self.cont_per + "' OR cont_per LIKE '" + self.cont_per + "/%' OR cont_per LIKE '%/" + self.cont_per + "' OR cont_per LIKE '%/" + self.cont_per + "/%'"
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            uri.setDataSource("public", "pyarchinit_archeozoo_view", "the_geom", cont_per_string, "id")
            layerUS = QgsVectorLayer(uri.uri(), "Fauna", "postgres")
            if layerUS.isValid():
                layerUS.setCrs(srs)
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                style_path = QFileDialog.getOpenFileName(self, 'Open file', self.LAYER_STYLE_PATH)
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], True)
            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", cont_per_string, "gid")
            layerQUOTE = QgsVectorLayer(uri.uri(), "Quote Unita' Stratigrafiche", "postgres")
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
                ##	def find_us_cutted(self, gl):
                ##		gid_list = gl
                ##		lista_rapporti = []
                ##		for i in range(len(gid_list)):
                ##			lista_rapporti.append([gid_list[i].sito,
                ##			 						gid_list[i].area,
                ##									gid_list[i].us,
                ##									gid_list[i].rapporti])
                ##
                ##		for i in lista_rapporti:
                ##			pass
                ##		"""

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
            uri.setDataSource("public", "pyarchinit_archeozoo_view", "the_geom", gidstr, "id_archzoo")
            layerUS = QgsVectorLayer(uri.uri(), "Fauna", "postgres")

            if layerUS.isValid():
                # self.USLayerId = layerUS.getLayerID()
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                # layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                layerToSet.append(layerUS)

                # layerQuote
            uri.setDataSource("public", "pyarchinit_quote_view", "the_geom", gidstr, "id_us")
            layerQUOTE = QgsVectorLayer(uri.uri(), "Quote", "postgres")

            if layerQUOTE.isValid():
                # style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
                # layerQUOTE.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerQUOTE], False)
                layerToSet.append(layerQUOTE)

            return layerToSet

        elif settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')
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
                # QMessageBox.warning(self, "TESTER", "OK Layer Quote non valido",	 #QMessageBox.Ok)

            uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
            layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

            if layerUS.isValid():
                # QMessageBox.warning(self, "TESTER", "OK ayer US valido",	 #QMessageBox.Ok)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerUS], False)
                layerToSet.append(layerQUOTE)
            else:
                pass
                # QMessageBox.warning(self, "TESTER", "NOT! Layer US not valid",#QMessageBox.Ok)

            return layerToSet

    """
    def addRasterLayer(self):
        fileName = "/rimini_1_25000/Rimini_25000_g.tif"
        fileInfo = QFileInfo(fileName)
        baseName = fileInfo.baseName()
        rlayer = QgsRasterLayer(fileName, baseName)

        if not rlayer.isValid():
            #QMessageBox.warning(self, "TESTER", "PROBLEMA DI CARICAMENTO RASTER" + str(baseName),	 #QMessageBox.Ok)

        srs = QgsCoordinateReferenceSystem(3004, QgsCoordinateReferenceSystem.PostgisCrsId)
        rlayer.setCrs(srs)
        # add layer to the registry
        QgsMapLayerRegistry.instance().addMapLayers(rlayer);

        self.canvas = QgsMapCanvas()
        self.canvas.setExtent(rlayer.extent())

        # set the map canvas layer set
        cl = QgsMapCanvasLayer(rlayer)
        layers = [cl]
        self.canvas.setLayerSet(layers)
    """

    # iface custom methods
    def dataProviderFields(self):
        fields = self.iface.mapCanvas().currentLayer().dataProvider().fields()
        return fields

    def selectedFeatures(self):
        selected_features = self.iface.mapCanvas().currentLayer().selectedFeatures()
        return selected_features

    def findFieldFrDict(self, fn):
        self.field_name = fn
        fields_dict = self.dataProviderFields()
        for k in fields_dict:
            if fields_dict[k].name() == self.field_name:
                res = k
        return res

    def findItemInAttributeMap(self, fp, fl):
        self.field_position = fp
        self.features_list = fl
        value_list = []
        for item in self.iface.mapCanvas().currentLayer().selectedFeatures():
            value_list.append(item.attributeMap().__getitem__(self.field_position).toString())
        return value_list


class Order_layers(object):
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
        ##		if self.stop_while == '':
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


"""
	def print_values(self):
		print "dizionario_valori per successione stratigrafica: ",self.DIZ_ORDER_LAYERS
		print "ordine di successione delle US: "
		for k in self.DIZ_ORDER_LAYERS.keys():
			print k
"""


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# !/usr/bin/python
