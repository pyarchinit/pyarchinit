#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
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
from builtins import range
from builtins import str
import psycopg2
import sqlite3  as sq
from sqlite3 import Error
import os
import sys
import subprocess
import platform
import time
import pandas as pd
import numpy as np
from pdf2docx import parse
from datetime import date
import xml.etree.ElementTree as ET
from lxml import etree
import cv2
from distutils.dir_util import copy_tree
from random import randrange as rand
from PyQt5 import QtCore, QtGui, QtWidgets
from osgeo import gdal
from qgis import processing
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from qgis.PyQt.QtSql import QSqlDatabase, QSqlTableModel
import re
from .Interactive_matrix import pyarchinit_Interactive_Matrix
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis, Order_layer_v2
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
#from ..modules.utility.pyarchinit_exp_Periodosheet_pdf import generate_US_pdf
from ..modules.utility.pyarchinit_exp_USsheet_pdf import generate_US_pdf
from ..modules.utility.pyarchinit_print_utility import Print_utility
from ..modules.utility.settings import Settings
#from ..modules.utility.layout_loader import LayoutLoader
from .pyarchinit_setting_matrix import Setting_Matrix
from ..searchLayers import SearchLayers
from ..gui.imageViewer import ImageViewer
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.sortpanelmain import SortPanelMain
from ..resources.resources_rc import *

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'gpkg_export.ui'))
class pyarchinit_GPKG(QDialog, MAIN_DIALOG_CLASS):
    
    
    HOME = os.environ['PYARCHINIT_HOME']
    BIN = '{}{}{}'.format(HOME, os.sep, "pyarchinit_DB_folder")
    DB_SERVER = "not defined"  ####nuovo sistema sort
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        
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
        #filename=dbpath.split("/")[-1]
        if dbpath:
            self.lineEdit.setText(dbpath)
            s.setValue('',dbpath)
    
    def on_pushButton_gpkg_pressed(self):
        # #QGIS3
        lyrs = self.iface.layerTreeView().selectedLayers()
        # lyrs = QgsProject.instance().mapLayers()
        # lyrs = QgsProject.instance().layerTreeRoot().children()
         
        # # select layer
        # lyr = lyrs[0]
        
        #QMessageBox.warning(self, "Cached Table",str(lyrs),QMessageBox.Ok )   
        gpkgPath=str(self.lineEdit.text())
        if lyrs:
            

            # p = Path(gpkgPath)
            # if p.exists():
            QgsVectorFileWriter.writeAsVectorFormat(lyrs[0],gpkgPath,"GPKG")    
            for lyr in filter(lambda l: l.type() == QgsMapLayer.VectorLayer, lyrs):
                options = QgsVectorFileWriter.SaveVectorOptions()
                options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer 
                options.layerName = "_".join(lyr.name().split(' '))
                _writer = QgsVectorFileWriter.writeAsVectorFormat(lyr, gpkgPath, options,"GPKG")
            if _writer:
                
                QMessageBox.warning(self, "OK","Importazione completata\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
            else:
                
                QMessageBox.warning(self, "Ops","Importazione fallita\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
            
            # else:
                # for lyr in filter(lambda l: l.type() == QgsMapLayer.VectorLayer, lyrs):
                    # _writer2 = QgsVectorFileWriter.writeAsVectorFormat(lyr,gpkgPath,"GPKG")
                # if _writer2:
                    
                    # QMessageBox.warning(self, "OK","Importazione completata\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
                # else:
                    
                    # QMessageBox.warning(self, "Ops","Importazione fallita\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
        else:
            QMessageBox.warning(self, "Attenzione","Non hai selezionato nessun layer da importare\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
             
    def on_pushButton_gpkg2_pressed(self):
        # # #QGIS3
        lyrs = self.iface.layerTreeView().selectedLayers()
        #lyrs = QgsProject.instance().mapLayers().filename()
        # CRS = QgsCoordinateReferenceSystem()# lyrs = QgsProject.instance().mapLayers()
        # # lyrs = QgsProject.instance().layerTreeRoot().children()
         
        # # # select layer
        lyr = lyrs[0]
        
        # #QMessageBox.warning(self, "Cached Table",str(lyrs),QMessageBox.Ok )   
        gpkgPath=str(self.lineEdit.text())
        # if lyrs:
            

            # p = Path(gpkgPath)
            # if p.exists():
                # for lyr in lyrs:
                    # provider = lyr.dataProvider()

                    # pipe = QgsRasterPipe()

                    # pipe.set(provider.clone())

                    # rasterWriter = QgsRasterFileWriter(gpkgPath)

                    # xSize = provider.xSize()
                    # ySize = provider.ySize()

                    # _writer=rasterWriter.writeRaster(pipe, xSize, ySize, provider.extent(), CRS)
                # if _writer:
                    
                    # QMessageBox.warning(self, "OK","Importazione completata\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
                # else:
                    
                    # QMessageBox.warning(self, "Ops","Importazione fallita\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
            
            
        # else:
            # QMessageBox.warning(self, "Attenzione","Non hai selezionato nessun layer da importare\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
            
            
            
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
                        QMessageBox.warning(self, "OK","Importazione completata\n",QMessageBox.Ok )
                    else:
                        QMessageBox.warning(self, "Ops","Importazione fallita\n",QMessageBox.Ok ) # print(lyr.name(), _writer)
        ds = None    