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
from pathlib import Path
from builtins import str
import os
from osgeo import gdal
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import *
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'gpkg_export.ui'))
class pyarchinit_GPKG(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Importa in Geopackge"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Import into Geopackage"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Import ain Geopackage"  
    HOME = os.environ['PYARCHINIT_HOME']
    BIN = '{}{}{}'.format(HOME, os.sep, "pyarchinit_DB_folder")
    DB_SERVER = "not defined"
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        QDialog.__init__(self, None,Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.toolButton.clicked.connect(self.setPath)
    def setPath(self):
        s = QgsSettings()
        dbpath = QFileDialog.getSaveFileName(
            self,
            "Set file name",
            self.BIN,
            " GPKG (*.gpkg)"
        )[0]
        if dbpath:
            self.lineEdit.setText(dbpath)
            s.setValue('',dbpath)
    def on_pushButton_gpkg_pressed(self):
        lyrs = self.iface.layerTreeView().selectedLayers()
        gpkgPath=str(self.lineEdit.text())
        if lyrs:
            p = Path(gpkgPath)
            if p.exists():
                for lyr in filter(lambda l: l.type() == QgsMapLayer.VectorLayer, lyrs):
                    options = QgsVectorFileWriter.SaveVectorOptions()
                    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer 
                    options.layerName = "_".join(lyr.name().split(' '))
                    _writer = QgsVectorFileWriter.writeAsVectorFormat(lyr, gpkgPath, options,"GPKG")
                if _writer:
                    if self.L=='it':
                        QMessageBox.warning(self, "OK","Importazione completata\n",QMessageBox.Ok ) 
                    else:
                        QMessageBox.warning(self, "OK","Import completed\n",QMessageBox.Ok )
                else:
                    if self.L=='it':
                        QMessageBox.warning(self, "Ops","Importazione fallita\n",QMessageBox.Ok )
                    else:
                        QMessageBox.warning(self, "OK","Import completed\n",QMessageBox.Ok )
            else:
                QgsVectorFileWriter.writeAsVectorFormat(lyrs[0],gpkgPath,"GPKG")    
                for lyr in filter(lambda l: l.type() == QgsMapLayer.VectorLayer, lyrs):
                    options = QgsVectorFileWriter.SaveVectorOptions()
                    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer 
                    options.layerName = "_".join(lyr.name().split(' '))
                    _writer = QgsVectorFileWriter.writeAsVectorFormat(lyr, gpkgPath, options,"GPKG")
                if _writer:
                    if self.L=='it':
                        QMessageBox.warning(self, "OK","Importazione completata\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
                    else:
                        QMessageBox.warning(self, "OK","Import completed\n",QMessageBox.Ok )
                else:
                    if self.L=='it':
                        QMessageBox.warning(self, "Ops","Importazione fallita\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
                    else:
                        QMessageBox.warning(self, "OK","Import completed\n",QMessageBox.Ok )
        else:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione","Non è stato selezionato nessun layer\n",QMessageBox.Ok )
            else:
                QMessageBox.warning(self, "Warning","No layer selected\n",QMessageBox.Ok )
    def on_pushButton_gpkg2_pressed(self):
        lyrs = self.iface.layerTreeView().selectedLayers()
        lyr = lyrs[0]
        gpkgPath=str(self.lineEdit.text())
        ds = gdal.Open(gpkgPath, True)
        source = QgsRasterLayer(lyr.source(),'raster','gdal')
        if source.isValid():
            provider = source.dataProvider()
            fw = QgsRasterFileWriter(gpkgPath)
            fw.setOutputFormat('gpkg')
            fw.setCreateOptions(["RASTER_TABLE=" + str(lyr.name()), 'APPEND_SUBDATASET=YES'])
            pipe = QgsRasterPipe()
            if pipe.set(provider.clone()) is True:
                projector = QgsRasterProjector()
                projector.setCrs(provider.crs(), provider.crs())
                if pipe.insert(2, projector) is True:
                    if fw.writeRaster(pipe, provider.xSize(),provider.ySize(),provider.extent(),provider.crs()) == 0:
                        QMessageBox.warning(self, "OK","Import completed\n",QMessageBox.Ok )
                    else:
                        QMessageBox.warning(self, "Ops","Import failed\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
        ds = None    