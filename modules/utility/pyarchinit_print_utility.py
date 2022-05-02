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

from builtins import range
from builtins import str
from qgis.PyQt.QtCore import QRectF, pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QMessageBox, QApplication
from qgis.core import (QgsProject,
                       QgsDataSourceUri,
                       QgsVectorLayer,
                       QgsCoordinateReferenceSystem,
                       QgsRectangle,
                       QgsLayout,
                       QgsLayoutSize,
                       QgsLayoutItemMap,
                       QgsLayoutPoint,
                       QgsLayoutItemLabel,
                       QgsLayoutItemScaleBar,
                       QgsLayoutExporter)

from .settings import Settings


class Print_utility(QObject):
    progressBarUpdated = pyqtSignal(int, int)

    HOME = os.environ['PYARCHINIT_HOME']
    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Report_folder")
    FILEPATH = os.path.dirname(__file__)
    LAYER_STYLE_PATH = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles', os.sep)
    LAYER_STYLE_PATH_SPATIALITE = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles_spatialite', os.sep)
    SRS = 3004

    layerUS = ""
    layerQuote = ""
    ##  layerCL = ""
    ##  layerGriglia = "" #sperimentale da riattivare

    USLayerId = ""
    CLayerId = ""
    QuoteLayerId = ""
    GrigliaLayerId = ""

    mapHeight = ""
    mapWidth = ""

    tav_num = ""
    us = ""
    uri = ""

    def __init__(self, iface, data):
        super().__init__()
        self.iface = iface
        self.data = data
        # self.area = area
        # self.us = us
        self.canvas = self.iface.mapCanvas()

    # set host name, port, database name, username and password

    """
    def on_pushButton_runTest_pressed(self):
        self.first_batch_try()
    """

    def first_batch_try(self, server):

        if server == 'postgres':
            for i in range(len(self.data)):
                test = self.charge_layer_postgis(self.data[i].sito, self.data[i].area,self.data[i].us)
                self.us = self.data[i].us
                self.periodo_iniziale = self.data[i].periodo_iniziale
                self.periodo_fianle = self.data[i].fase_finale
                if test != 0:
                    if self.layerUS.featureCount() > 0:
                        self.test_bbox()
                        tav_num = i
                        self.print_map(tav_num)
                        self.progressBarUpdated.emit(i, len(self.data)-1)
                        QApplication.processEvents()
                    else:
                        self.remove_layer()
                if test == 0:
                    Report_path = '{}{}{}'.format(self.REPORT_PATH, os.sep,'report_errori.txt')
                    f = open(Report_path, "w")
                    f.write(str("Presenza di errori nel layer"))
                    f.close()

        elif server == 'sqlite':
            for i in range(len(self.data)):
                test = self.charge_layer_sqlite(self.data[i].sito, self.data[i].area, self.data[i].us)
                self.us = self.data[i].us
                if test != 0:
                    if self.layerUS.featureCount() > 0:
                        self.test_bbox()
                        tav_num = i
                        self.print_map(tav_num)
                        self.progressBarUpdated.emit(i, len(self.data)-1)
                        QApplication.processEvents()
                    else:
                        self.remove_layer()
                if test == 0:
                    Report_path = '{}{}{}'.format(self.REPORT_PATH, os.sep,'report_errori.txt')
                    f = open(Report_path, "w")
                    f.write(str("Presenza di errori nel layer"))
                    f.close()

    def converter_1_20(self, n):
        n *= 100
        res = n / 20
        return res

    def test_bbox(self):
        # f = open("/test_type.txt", "w")
        # ff.write(str(type(self.layerUS)))
        # ff.close()

        self.layerUS.select([])  # recuperi tutte le geometrie senza attributi
        #  featPoly = QgsFeature()  # crei una feature vuota per il poligono

        dizionario_id_contains = {}
        lista_quote = []

        it = self.layerUS.getFeatures()
        featPoly = next(it)  # cicli sulle feature recuperate, featPoly conterra la feature poligonale attuale
        bbox = featPoly.geometry().boundingBox()  # recupera i punti nel bbox del poligono
        self.height = self.converter_1_20(float(bbox.height())) * 10  # la misura da cm e' portata in mm
        self.width = self.converter_1_20(float(bbox.width())) * 10  # la misura da cm e' portata in mm

        # f = open("/test_paper_size_5.txt", "w")
        # f.write(str(self.width))
        # f.close()

    def getMapExtentFromMapCanvas(self, mapWidth, mapHeight, scale):
        # code from easyPrint plugin
        # print "in methode: " + str(scale)

        xmin = self.canvas.extent().xMinimum()
        xmax = self.canvas.extent().xMaximum()
        ymin = self.canvas.extent().yMinimum()
        ymax = self.canvas.extent().yMaximum()
        xcenter = xmin + (xmax - xmin) / 2
        ycenter = ymin + (ymax - ymin) / 2

        mapWidth = mapWidth * scale / 1000  # misura in punti
        mapHeight = mapHeight * scale / 1000  # misura in punti

        # f = open("/test_paper_size_3.txt", "w")
        # f.write(str(mapWidth))
        # f.close()

        minx = xcenter - mapWidth / 2
        miny = ycenter - mapHeight / 2
        maxx = xcenter + mapWidth / 2
        maxy = ycenter + mapHeight / 2

        return QgsRectangle(minx, miny, maxx, maxy)

    def print_map(self, tav_num):
        self.tav_num = tav_num

        p = QgsProject.instance()
        crs = QgsCoordinateReferenceSystem()
        crs.createFromSrid(self.SRS)
        p.setCrs(crs)

        l = QgsLayout(p)
        l.initializeDefaults()
        page = l.pageCollection().page(0)

        # map - this item tells the libraries where to put the map itself. Here we create a map and stretch it over the whole paper size:
        x, y = 0, 0  # angolo 0, o in alto a sx

        if (0 <= self.width <= 297) and (0 <= self.height <= 210):
            width, height = 297, 210  # Formato A4 Landscape
        elif (0 <= self.height <= 297) and (0 <= self.width <= 210):
            width, height = 210, 297  # Formato A4

        elif (0 <= self.width <= 420) and (0 <= self.height <= 297):
            width, height = 297, 420  # Formato A3 Landscape
        elif (0 <= self.height <= 420) and (0 <= self.width <= 297):
            width, height = 240, 297  # Formato A4

        elif (0 <= self.width <= 1189) and (0 <= self.height <= 841):
            width, height = 1189, 841  # Formato A0 Landscape
        elif (0 <= self.height <= 1189) and (0 <= self.width <= 841):
            width, height = 841, 1189  # Formato A0
        else:
            width, height = self.width * 1.2, self.height * 1.2  # self.width*10, self.height*10 da un valore alla larghezza e altezza del foglio aumentato di 5 per dare un margine

        size = QgsLayoutSize(width, height)
        page.setPageSize(size)

        map = QgsLayoutItemMap(l)

        rect = self.getMapExtentFromMapCanvas(page.pageSize().width(), page.pageSize().height(), 20.0)

        map.attemptSetSceneRect(QRectF(0, 0, page.pageSize().width(), page.pageSize().height()))
        map.setExtent(rect)
        map.setLayers([self.layerUS])
        l.setReferenceMap(map)
        l.addLayoutItem(map)

        intestazioneLabel = QgsLayoutItemLabel(l)
        txt = "Tavola %s - US:%d " % (self.tav_num + 1, self.us)
        intestazioneLabel.setText(txt)
        intestazioneLabel.adjustSizeToText()
        intestazioneLabel.attemptMove(QgsLayoutPoint(1, 0), page=0)
        intestazioneLabel.setFrameEnabled(False)
        l.addLayoutItem(intestazioneLabel)

        scaleLabel = QgsLayoutItemLabel(l)
        txt = "Scala: "
        scaleLabel.setText(txt)
        scaleLabel.adjustSizeToText()
        scaleLabel.attemptMove(QgsLayoutPoint(1, 5), page=0)
        scaleLabel.setFrameEnabled(False)
        l.addLayoutItem(scaleLabel)

        # aggiunge la scale bar
        scaleBarItem = QgsLayoutItemScaleBar(l)
        scaleBarItem.setStyle('Numeric')  # optionally modify the style
        scaleBarItem.setLinkedMap(map)
        scaleBarItem.applyDefaultSize()
        scaleBarItem.attemptMove(QgsLayoutPoint(10, 5), page=0)
        scaleBarItem.setFrameEnabled(False)
        l.addLayoutItem(scaleBarItem)

        le = QgsLayoutExporter(l)
        settings = QgsLayoutExporter.ImageExportSettings()
        settings.dpi = 100

        MAPS_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_MAPS_folder")
        tav_name = "Tavola_{}_us_{}.png".format(self.tav_num + 1, self.us)
        filename_png = '{}{}{}'.format(MAPS_path, os.sep, tav_name)

        le.exportToImage(filename_png, settings)

        self.remove_layer()

    def open_connection_postgis(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()
        self.uri = QgsDataSourceUri()
        self.uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
    
    def open_connection_sqlite(self):
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()
        self.uri = QgsDataSourceUri()
        self.uri.setConnection(settings.DATABASE)
    def remove_layer(self):
        if self.USLayerId != "":
            QgsProject.instance().removeMapLayer(self.USLayerId)
            self.USLayerId = ""

        if self.QuoteLayerId != "":
            QgsProject.instance().removeMapLayer(self.QuoteLayerId)
            self.QuoteLayerId = ""

    def charge_layer_sqlite(self, sito, area, us):
        
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        sqliteDB_path = os.path.join(os.sep, 'pyarchinit_DB_folder', settings.DATABASE)

        
        db_file_path='{}{}'.format(self.HOME, sqliteDB_path)
        uri = QgsDataSourceUri()
        uri.setDatabase(db_file_path)
        #srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

        gidstr = "scavo_s = '%s' and area_s = '%s' and us_s = '%s'" % (sito, area, us)

        #uri = QgsDataSourceUri()
        #uri.setDatabase(db_file_path)

        uri.setDataSource('', 'pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
        self.layerUS = QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

        if self.layerUS.isValid():
            #self.layerUS.setCrs(srs)
            self.USLayerId = self.layerUS.id()
            # self.mapLayerRegistry.append(USLayerId)
            style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
            self.layerUS.loadNamedStyle(style_path)
            self.iface.mapCanvas().setExtent(self.layerUS.extent())
            QgsProject.instance().addMapLayer(self.layerUS, True)
        else:
            QMessageBox.warning(None, "Errore", "Non Valido", QMessageBox.Ok)
            return 0
            # QMessageBox.warning(self, "Messaggio", "Geometria inesistente", QMessageBox.Ok)

        gidstr = "sito_q = '%s' and area_q = '%s' and us_q = '%d'" % (sito, area, us)

        uri.setDataSource('', 'pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
        self.layerQuote = QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

        if self.layerQuote.isValid():
            #self.layerQuote.setCrs(srs)
            self.QuoteLayerId = self.layerQuote.id()
            # self.mapLayerRegistry.append(QuoteLayerId)
            style_path = '{}{}'.format(self.LAYER_STYLE_PATH_SPATIALITE, 'stile_quote.qml')
            self.layerQuote.loadNamedStyle(style_path)
            QgsProject.instance().addMapLayer(self.layerQuote, True)

    def charge_layer_postgis(self, sito, area, us):
        self.open_connection_postgis()

        srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

        gidstr = "scavo_s = '%s' and area_s = '%s' and us_s = '%d'" % (sito, area, us)

        self.uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, 'gid')

        self.layerUS = QgsVectorLayer(self.uri.uri(), "US", "postgres")

        if self.layerUS.isValid():
            self.layerUS.setCrs(srs)
            self.USLayerId = self.layerUS.id()
            # self.mapLayerRegistry.append(USLayerId)
            #style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
            #self.layerUS.loadNamedStyle(style_path)
            self.iface.mapCanvas().setExtent(self.layerUS.extent())
            QgsProject.instance().addMapLayer(self.layerUS, True)
        else:
            return 0

        gidstr = "sito_q = '%s' and area_q = '%s' and us_q = '%d'" % (sito, area, us)

        self.uri.setDataSource("public", "pyarchinit_quote", "the_geom", gidstr, 'gid')
        self.layerQuote = QgsVectorLayer(self.uri.uri(), "Quote", "postgres")

        if self.layerQuote.isValid():
            self.layerQuote.setCrs(srs)
            self.QuoteLayerId = self.layerQuote.id()
            # self.mapLayerRegistry.append(QuoteLayerId)
            #style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'stile_quote.qml')
            #self.layerQuote.loadNamedStyle(style_path)
            QgsProject.instance().addMapLayer(self.layerQuote, True)
