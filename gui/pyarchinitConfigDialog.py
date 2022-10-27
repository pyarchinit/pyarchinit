
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
    ------------------------------------------------------------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : pyarchinit at gmail.com
 ***************************************************************************/

/***************************************************************************/
*                                                                           *
*   This program is free software; you can redistribute it and/or modify   *
*   it under the terms of the GNU General Public License as published by    *
*   the Free Software Foundation; either version 2 of the License, or      *
*   (at your option) any later version.                                     *
*                                                                          *
/***************************************************************************/
"""
from __future__ import absolute_import

import os
import sqlite3

import sqlalchemy as sa

from sqlalchemy.event import listen
import platform
from builtins import range
from builtins import str

from ftplib import FTP

from sqlalchemy import create_engine

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import *
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import  pyqtSlot, pyqtSignal,QThread,QUrl
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog,QLineEdit,QWidget,QCheckBox
from qgis.PyQt.QtSql import *
from qgis.PyQt.uic import loadUiType
from qgis.core import  *
from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.pyarchinit_utility import Utility

from modules.db.db_createdump import CreateDatabase, RestoreSchema, DropDatabase, SchemaDump
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility


MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'pyarchinitConfigDialog.ui'))


class pyArchInitDialog_Config(QDialog, MAIN_DIALOG_CLASS):
    progressBarUpdated = pyqtSignal(int,int)
    L=QgsSettings().value("locale/userLocale")[0:2]
    UTILITY=Utility()
    DB_MANAGER=""

    HOME = os.environ['PYARCHINIT_HOME']
    DBFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_DB_folder")
    PARAMS_DICT = {'SERVER': '',
                   'HOST': '',
                   'DATABASE': '',
                   'PASSWORD': '',
                   'PORT': '',
                   'USER': '',
                   'THUMB_PATH': '',
                   'THUMB_RESIZE': '',
                   'EXPERIMENTAL': '',
                   'SITE_SET': ''}

    def __init__(self, parent=None, db=None):

        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.

        self.setupUi(self)

        s = QgsSettings()
        self.mDockWidget.setHidden(True)

        self.load_dict()
        self.charge_data()
        self.db_active()
        self.lineEdit_DBname.textChanged.connect(self.db_uncheck)
        self.pushButton_upd_postgres.setEnabled(True)
        self.pushButton_upd_sqlite.setEnabled(False)
        self.comboBox_sito.setCurrentText(self.sito_active())
        self.comboBox_sito.currentIndexChanged.connect(self.summary)
        self.comboBox_Database.currentIndexChanged.connect(self.db_active)
        self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
        
        # if self.comboBox_server_rd.currentText=='sqlite':
            # self.set_db_import_from_parameter()
        
        self.comboBox_server_rd.currentTextChanged.connect(self.set_db_import_from_parameter)
        self.comboBox_server_wt.currentTextChanged.connect(self.set_db_import_to_parameter)

        self.pushButton_save.clicked.connect(self.summary)
        self.pushButton_save.clicked.connect(self.on_pushButton_save_pressed)

        self.pushButtonGraphviz.clicked.connect(self.setPathGraphviz)
        self.pbnSaveEnvironPath.clicked.connect(self.setEnvironPath)
        self.toolButton_logo.clicked.connect(self.setPathlogo)
        self.toolButton_thumbpath.clicked.connect(self.setPathThumb)
        self.toolButton_resizepath.clicked.connect(self.setPathResize)
        self.toolButton_set_dbsqlite1.clicked.connect(self.setPathDBsqlite1)
        self.toolButton_set_dbsqlite2.clicked.connect(self.setPathDBsqlite2)
        self.pbnOpenthumbDirectory.clicked.connect(self.openthumbDir)
        self.pbnOpenresizeDirectory.clicked.connect(self.openresizeDir)
        
        self.toolButton_db.clicked.connect(self.setPathDB)
        self.pushButtonPostgres.clicked.connect(self.setPathPostgres)
        self.pbnSaveEnvironPathPostgres.clicked.connect(self.setEnvironPathPostgres)
        self.comboBox_server_rd.currentTextChanged.connect(self.geometry_conn)
        self.pushButton_compare.clicked.connect(self.compare)
        self.pushButton_import.clicked.connect(self.on_pushButton_import_pressed)
        self.graphviz_bin = s.value('pyArchInit/graphvizBinPath', None, type=str)

        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)

        if Pyarchinit_OS_Utility.checkGraphvizInstallation():
            self.pushButtonGraphviz.setEnabled(False)
            self.pbnSaveEnvironPath.setEnabled(False)
            self.lineEditGraphviz.setEnabled(False)

        self.postgres_bin = s.value('pyArchInit/postgresBinPath', None, type=str)
        if self.postgres_bin:
            self.lineEditPostgres.setText(self.postgres_bin)

        if Pyarchinit_OS_Utility.checkPostgresInstallation():
            self.pushButtonPostgres.setEnabled(False)
            self.pbnSaveEnvironPathPostgres.setEnabled(False)
            self.lineEditPostgres.setEnabled(False)




        self.selectorCrsWidget.setCrs(QgsProject.instance().crs())
        self.selectorCrsWidget_sl.setCrs(QgsProject.instance().crs())
        if self.checkBox_abort.isChecked():
            self.checkBox_abort.setChecked(True)
            self.checkBox_abort.stateChanged.connect(self.check)
            self.checkBox_abort.stateChanged.connect(self.message)
        elif self.checkBox_ignore.isChecked():
            self.checkBox_ignore.setChecked(True)
            self.checkBox_ignore.stateChanged.connect(self.check)
            self.checkBox_ignore.stateChanged.connect(self.message)
        elif self.checkBox_replace.isChecked():
            self.checkBox_replace.setChecked(True)
            self.checkBox_replace.stateChanged.connect(self.check)
            self.checkBox_replace.stateChanged.connect(self.message)    
        
        self.check()
        #self.upd_individui_table()
        if self.comboBox_Database.currentText()=='sqlite':
            self.setComboBoxEnable(["self.lineEdit_DBname"], "False")
        elif self.comboBox_Database.currentText()=='postgres':
            self.setComboBoxEnable(["self.lineEdit_DBname"], "True")
        self.comboBox_Database.currentIndexChanged.connect(self.customize)
        self.test()
        #self.test2()
        self.test3()
        self.comboBox_mapper_read.currentIndexChanged.connect(self.check_table)
        self.comboBox_geometry_read.currentIndexChanged.connect(self.check_geometry_table)
        self.mFeature_field_rd.currentTextChanged.connect(self.value_check)
        self.mFeature_field_rd.currentTextChanged.connect(self.value_check_geometry)
        
        self.comboBox_server_rd.currentTextChanged.connect(self.convert_db)
        self.comboBox_server_wt.currentTextChanged.connect(self.convert_db)
        self.pushButton_convert_db_sl.setHidden(True)
        self.pushButton_convert_db_pg.setHidden(True)
    
    def convert_db(self):
        if self.comboBox_server_rd.currentText()=='postgres':
            self.pushButton_convert_db_pg.setHidden(True)
            self.pushButton_convert_db_sl.show()
        if self.comboBox_server_rd.currentText()=='sqlite':
            self.pushButton_convert_db_sl.setHidden(True)
            self.pushButton_convert_db_pg.show()
    
        if self.comboBox_server_rd.currentText()=='postgres' and self.comboBox_server_wt.currentText()=='postgres' or self.comboBox_server_rd.currentText()=='':
            self.pushButton_convert_db_sl.setHidden(True)
            self.pushButton_convert_db_pg.setHidden(True)
        if self.comboBox_server_rd.currentText()=='sqlite' and self.comboBox_server_wt.currentText()=='sqlite' or self.comboBox_server_rd.currentText()=='':
            self.pushButton_convert_db_sl.setHidden(True)
            self.pushButton_convert_db_pg.setHidden(True)
    def on_pushButton_convert_db_sl_pressed(self):
        ok=QMessageBox.warning(self, "Attenzione", 'Vuoi sovrascrivere il db.\n clicca ok oppure Annulla per aggiornare', QMessageBox.Ok | QMessageBox.Cancel)
        
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        # if test_conn == 0:
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
        path=sqlite_DB_path+os.sep+self.lineEdit_database_wt.text()
        if ok==QMessageBox.Ok:
            try:
                process= os.system('start cmd /k ogr2ogr --config PG_LIST_ALL_TABLES YES --config PG_SKIP_VIEWS YES -f SQLite '+path+' -progress PG:"dbname='+self.lineEdit_database_rd.text()+' active_schema=public schemas=public host='+self.lineEdit_host_rd.text()+' port='+ self.lineEdit_port_rd.text()+' user='+self.lineEdit_username_rd.text()+' password='+self.lineEdit_pass_rd.text()+'" -lco LAUNDER=yes -dsco SPATIALITE=yes -lco SPATIAL_INDEX=yes -gt 65536 -skipfailures -update -overwrite')
                


            except KeyError as e:
                QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)
        else:
            
            
            process= os.system('start cmd /k ogr2ogr --config PG_LIST_ALL_TABLES YES --config PG_SKIP_VIEWS YES -f SQLite '+path+' -progress PG:"dbname='+self.lineEdit_database_rd.text()+' active_schema=public schemas=public host='+self.lineEdit_host_rd.text()+' port='+ self.lineEdit_port_rd.text()+' user='+self.lineEdit_username_rd.text()+' password='+self.lineEdit_pass_rd.text()+'" -lco LAUNDER=yes -dsco SPATIALITE=yes -lco SPATIAL_INDEX=yes -gt 65536 -skipfailures -update -append')
    
    
    
    def on_pushButton_convert_db_pg_pressed(self):
        ok=QMessageBox.warning(self, "Attenzione", 'Vuoi sovrascrivere il db.\n clicca ok oppure cancell per aggiornare', QMessageBox.Ok | QMessageBox.Cancel)
        
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        # if test_conn == 0:
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
        #path=sqlite_DB_path+os.sep+self.lineEdit_database_wt.text()
        path=sqlite_DB_path+os.sep+self.lineEdit_database_rd.text()
        if ok==QMessageBox.Ok:
            try:
                process= os.system('start cmd /k ogr2ogr  --config SQLITE_LIST_ALL_TABLES YES -progress  -f PostgreSQL  PG:"dbname='+self.lineEdit_database_wt.text()+' active_schema=public schemas=public host='+self.lineEdit_host_wt.text()+' port='+self.lineEdit_port_wt.text()+' user='+self.lineEdit_username_wt.text()+' password='+self.lineEdit_pass_wt.text()+'" -lco GEOMETRY_NAME="the_geom" -lco SPATIAL_INDEX=YES '+ path +' -skipfailures -update -overwrite')
                


            except KeyError as e:
                QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)
        else:
            
            process= os.system('start cmd /k ogr2ogr  --config SQLITE_LIST_ALL_TABLES YES -progress  -f PostgreSQL  PG:"dbname='+self.lineEdit_database_wt.text()+' active_schema=public schemas=public host='+self.lineEdit_host_wt.text()+' port='+self.lineEdit_port_wt.text()+' user='+self.lineEdit_username_wt.text()+' password='+self.lineEdit_pass_wt.text()+'" -lco GEOMETRY_NAME="the_geom" -lco SPATIAL_INDEX=YES '+ path +' -skipfailures -update -append')
    
    def sito_active(self):
        conn = Connection()
        conn_str = conn.conn_str()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        return sito_set_str
    def check_table(self):
        self.comboBox_mapper_read.update()
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            uri = QgsDataSourceUri()
            uri.setDatabase(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            schema = ''
            if self.comboBox_mapper_read.currentIndex()==1:
                try:
                    table = 'site_table'
                    geom_column = ''
                    uri.setDataSource(schema, table,geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                    pr = vlayer.dataProvider()
                    fi= pr.fields().names()[1:-1]
                    
                    self.mFeature_field_rd.clear()
                    self.mFeature_field_rd.addItems(fi)
                except:
                    pass
            elif self.comboBox_mapper_read.currentIndex()==2:
                
                table = 'us_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_mapper_read.currentIndex()==3:
                
                table = 'periodizzazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_mapper_read.currentIndex()==4:
                
                table = 'inventario_materiali_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi) 
            elif self.comboBox_mapper_read.currentIndex()==5:
                
                table = 'struttura_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==6:
                
                table = 'tomba_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==7:
                
                table = 'pyarchinit_thesaurus_sigle'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==8:
                
                table = 'individui_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==9:
                
                table = 'detsesso_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==10:
                
                table = 'deteta_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==11:
                
                table = 'archeozoology_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==12:
                
                table = 'campioni_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==13:
                
                table = 'documentazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==14:
                
                table = 'media_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==15:
                
                table = 'media_thumb_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==16:
                
                table = 'media_to_entity_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_mapper_read.currentIndex()==17:
                
                table = 'ut_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            try:
                self.mFeature_value_rd.clearEditText()
                self.mFeature_value_rd.update()
                self.value_check()
            except:
                pass
        else:
            uri = QgsDataSourceUri()
            uri.setConnection(conn_host["host"], conn_port["port"], conn_sqlite["db_name"], conn_user['user'], conn_password['password'])
            schema = 'public'
            if self.comboBox_mapper_read.currentIndex()==1:
                try:
                    table = 'site_table'
                    geom_column = ''
                    uri.setDataSource(schema, table,geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                    pr = vlayer.dataProvider()
                    fi= pr.fields().names()[1:-1]
                    
                    self.mFeature_field_rd.clear()
                    self.mFeature_field_rd.addItems(fi)
                except:
                    pass
            elif self.comboBox_mapper_read.currentIndex()==2:
                
                table = 'us_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_mapper_read.currentIndex()==3:
                
                table = 'periodizzazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_mapper_read.currentIndex()==4:
                
                table = 'inventario_materiali_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi) 
            elif self.comboBox_mapper_read.currentIndex()==5:
                
                table = 'struttura_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==6:
                
                table = 'tomba_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==7:
                
                table = 'pyarchinit_thesaurus_sigle'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==8:
                
                table = 'individui_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==9:
                
                table = 'detsesso_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==10:
                
                table = 'deteta_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==11:
                
                table = 'archeozoology_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==12:
                
                table = 'campioni_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==13:
                
                table = 'documentazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==14:
                
                table = 'media_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==15:
                
                table = 'media_thumb_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==16:
                
                table = 'media_to_entity_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_mapper_read.currentIndex()==17:
                
                table = 'ut_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
        try:
            self.mFeature_value_rd.clearEditText()
            self.mFeature_value_rd.update()
            self.value_check()
        except:
            pass
    def value_check(self):
        try:
            self.mFeature_value_rd.clear()
            self.mFeature_value_rd.update()
            if self.mFeature_field_rd.currentTextChanged:
                sito_vl2 = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by(table, self.mFeature_field_rd.currentText(), self.comboBox_mapper_read.currentText()))

            try:
                sito_vl2.remove('')
            except:
                pass
            self.mFeature_value_rd.clear()
            sito_vl2.sort()
            
            self.mFeature_value_rd.addItems(sito_vl2)
            self.mFeature_value_rd.update()
        except :
            pass#QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)        
    def check_geometry_table(self):
        self.comboBox_geometry_read.update()
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            uri = QgsDataSourceUri()
            uri.setDatabase(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            schema = ''
            
            ##############################################################################################
            if self.comboBox_geometry_read.currentIndex()==1:
                
                    table = 'pyarchinit_siti_polygonal'
                    geom_column = 'the_geom'
                    uri.setDataSource(schema, table,geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                    pr = vlayer.dataProvider()
                    fi= pr.fields().names()[1:-1]
                    
                    self.mFeature_field_rd.clear()
                    self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_geometry_read.currentIndex()==2:
                
                table = 'pyarchinit_siti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_geometry_read.currentIndex()==3:
                
                table = 'pyunitastratigrafiche'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_geometry_read.currentIndex()==4:
                
                table = 'pyunitastratigrafiche_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi) 
            elif self.comboBox_geometry_read.currentIndex()==5:
                
                table = 'pyarchinit_quote'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==6:
                
                table = 'pyarchinit_quote_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==7:
                
                table = 'pyarchinit_us_negative_doc'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==8:
                
                table = 'pyarchinit_strutture_ipotesi'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==9:
                
                table = 'pyarchinit_reperti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==10:
                
                table = 'pyarchinit_individui'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==11:
                
                table = 'pyarchinit_campionature'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==12:
                
                table = 'pyarchinit_tafonomia'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==13:
                
                table = 'pyarchinit_sezioni'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==14:
                
                table = 'pyarchinit_documentazione'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==15:
                
                table = 'pyarchinit_punti_rif'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==16:
                
                table = 'pyarchinit_ripartizioni_spaziali'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            
            
            try:
                self.mFeature_value_rd.clearEditText()
                self.mFeature_value_rd.update()
                self.value_check_geometry()
            except:
                pass
    
        else:
            uri = QgsDataSourceUri()
            uri.setConnection(conn_host["host"], conn_port["port"], conn_sqlite["db_name"], conn_user['user'], conn_password['password'])
            schema='public'
            ##############################################################################################
            if self.comboBox_geometry_read.currentIndex()==1:
                
                table = 'pyarchinit_siti_polygonal'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_geometry_read.currentIndex()==2:
                
                table = 'pyarchinit_siti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_geometry_read.currentIndex()==3:
                
                table = 'pyunitastratigrafiche'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[2:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_geometry_read.currentIndex()==4:
                
                table = 'pyunitastratigrafiche_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi) 
            elif self.comboBox_geometry_read.currentIndex()==5:
                
                table = 'pyarchinit_quote'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==6:
                
                table = 'pyarchinit_quote_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==7:
                
                table = 'pyarchinit_us_negative_doc'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==8:
                
                table = 'pyarchinit_strutture_ipotesi'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==9:
                
                table = 'pyarchinit_reperti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==10:
                
                table = 'pyarchinit_individui'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==11:
                
                table = 'pyarchinit_campionature'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==12:
                
                table = 'pyarchinit_tafonomia'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==13:
                
                table = 'pyarchinit_sezioni'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==14:
                
                table = 'pyarchinit_documentazione'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==15:
                
                table = 'pyarchinit_punti_rif'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==16:
                
                table = 'pyarchinit_ripartizioni_spaziali'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            
            
        try:
            self.mFeature_value_rd.clearEditText()
            self.mFeature_value_rd.update()
            self.value_check_geometry()
        except:
            pass
    
    
    def value_check_geometry(self):
        try:
            self.mFeature_value_rd.clear()
            self.mFeature_value_rd.update()
            if self.mFeature_field_rd.currentTextChanged:
                sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by(table, self.mFeature_field_rd.currentText(), self.comboBox_geometry_read.currentText()))

                try:
                    sito_vl.remove('')
                except:
                    pass
                self.mFeature_value_rd.clear()
                sito_vl.sort()
                
                self.mFeature_value_rd.addItems(sito_vl)
                self.mFeature_value_rd.update()
        except:
            pass
    
    
    def test3(self):
        
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        conn = Connection()
        db_url = conn.conn_str()
        test_conn = db_url.find('sqlite')
        if test_conn == 0:
            
            
            
            engine = create_engine(db_url, echo=True)

            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
            
            tabl=str('SELECT name FROM sqlite_master WHERE type="table" AND name="pyarchinit_quote_usm";') 
            b=c.execute(tabl).fetchone()
            
            if b==None:
                QMessageBox.warning(self, 'Attenzione','Aggiorna il db per inserire i layer per le unità stratigrafiche verticali',QMessageBox.Ok)
                
                
            try:    
                if Qgis.QGIS_VERSION_INT >=32000:
                    version_sl=str('SELECT CheckSpatialMetaData();')
                    a=c.execute(version_sl).fetchall()
                    for row in a:
                        print(row[0])
                    if str(row[0])=='1':
                        QMessageBox.warning(self, 'Attenzione','Versione DB:'+ str(row[0])+'\n'+' '+ 'La versione spatilalite di questo db dveve essere convertito',QMessageBox.Ok)
                    else:
                       pass
            except:
                pass
                
        
    def test(self):
        try:
            
            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()
            
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            
            con = sqlite3.connect(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            cur = con.cursor()
            
          
            
            delete_tab='''DELETE FROM geometry_columns WHERE f_geometry_column = 'geom';'''
            cur.execute(delete_tab)
            drop_ = '''DROP TABLE IF EXISTS sqlitestudio_temp_table2;'''
            cur.execute(drop_)
            drop_2 = '''DROP TABLE IF EXISTS sqlitestudio_temp_table;'''
            
            
            
            
            cur.executescript('''
            
            
            PRAGMA foreign_keys = 0;
                
                
                CREATE TABLE sqlitestudio_temp_table2 AS SELECT *
                                                          FROM pyarchinit_us_negative_doc;

                DROP TABLE pyarchinit_us_negative_doc;

                CREATE TABLE pyarchinit_us_negative_doc (
                    gid        "INTEGER"  PRIMARY KEY,
                    sito_n     "TEXT",
                    area_n     "TEXT",
                    us_n       "INTEGER",
                    tipo_doc_n "TEXT",
                    nome_doc_n "TEXT",
                    the_geom   LINESTRING
                );

                INSERT INTO pyarchinit_us_negative_doc (
                                                           gid,
                                                           sito_n,
                                                           area_n,
                                                           us_n,
                                                           tipo_doc_n,
                                                           nome_doc_n,
                                                           the_geom
                                                       )
                                                       SELECT pkuid,
                                                              sito_n,
                                                              area_n,
                                                              us_n,
                                                              tipo_doc_n,
                                                              nome_doc_n,
                                                              the_geom
                                                         FROM sqlitestudio_temp_table2;

                DROP TABLE sqlitestudio_temp_table2;

                
                CREATE TRIGGER ggi_pyarchinit_us_negative_doc_the_geom BEFORE INSERT ON pyarchinit_us_negative_doc FOR EACH ROW BEGIN SELECT RAISE(ROLLBACK, "pyarchinit_us_negative_doc.the_geom violates Geometry constraint [geom-type or SRID not allowed]") WHERE ( SELECT type FROM geometry_columns WHERE f_table_name = 'pyarchinit_us_negative_doc' AND f_geometry_column = 'the_geom' AND GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1 ) IS NULL; END; 
                CREATE TRIGGER ggu_pyarchinit_us_negative_doc_the_geom BEFORE UPDATE ON pyarchinit_us_negative_doc FOR EACH ROW BEGIN SELECT RAISE(ROLLBACK, "pyarchinit_documentazione.the_geom violates Geometry constraint [geom-type or SRID not allowed]") WHERE ( SELECT type FROM geometry_columns WHERE f_table_name = 'pyarchinit_us_negative_doc' AND f_geometry_column = 'the_geom' AND GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1 ) IS NULL; END;
                CREATE TRIGGER "gii_pyarchinit_us_negative_doc_the_geom" AFTER INSERT ON "pyarchinit_us_negative_doc" FOR EACH ROW BEGIN DELETE FROM "idx_pyarchinit_us_negative_doc_the_geom" WHERE pkid=NEW.rowid; SELECT RTreeAlign('idx_pyarchinit_us_negative_doc_the_geom', NEW.rowid, NEW."the_geom"); END; 
                CREATE TRIGGER "giu_pyarchinit_us_negative_doc_the_geom" AFTER UPDATE ON "pyarchinit_us_negative_doc" FOR EACH ROW BEGIN DELETE FROM "idx_pyarchinit_us_negative_doc_the_geom" WHERE pkid=NEW.rowid; SELECT RTreeAlign('idx_pyarchinit_us_negative_doc_the_geom', NEW.rowid, NEW."the_geom"); END; 
                CREATE TRIGGER "gid_pyarchinit_us_negative_doc_the_geom" AFTER DELETE ON "pyarchinit_us_negative_doc" FOR EACH ROW BEGIN DELETE FROM "idx_pyarchinit_us_negative_doc_the_geom" WHERE pkid=OLD.rowid; END; 


                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_strutture_ipotesi;

                DROP TABLE pyarchinit_strutture_ipotesi;

                CREATE TABLE pyarchinit_strutture_ipotesi (
                    gid         INTEGER                  PRIMARY KEY AUTOINCREMENT
                                                         NOT NULL,
                    sito        [CHARACTER VARYING] (80),
                    id_strutt   [CHARACTER VARYING] (80),
                    per_iniz    INTEGER,
                    per_fin     INTEGER,
                    dataz_ext   [CHARACTER VARYING] (80),
                    fase_iniz   INTEGER,
                    fase_fin    INTEGER,
                    descrizione [CHARACTER VARYING],
                    the_geom    POLYGON,
                    sigla_strut VARCHAR (3),
                    nr_strut    INTEGER                  DEFAULT 0
                );

                INSERT INTO pyarchinit_strutture_ipotesi (
                                                             gid,
                                                             sito,
                                                             id_strutt,
                                                             per_iniz,
                                                             per_fin,
                                                             dataz_ext,
                                                             fase_iniz,
                                                             fase_fin,
                                                             descrizione,
                                                             the_geom,
                                                             sigla_strut,
                                                             nr_strut
                                                         )
                                                         SELECT id,
                                                                sito,
                                                                id_strutt,
                                                                per_iniz,
                                                                per_fin,
                                                                dataz_ext,
                                                                fase_iniz,
                                                                fase_fin,
                                                                descrizione,
                                                                the_geom,
                                                                sigla_strut,
                                                                nr_strut
                                                           FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_strutture_ipotesi_the_geom
                        BEFORE INSERT
                            ON pyarchinit_strutture_ipotesi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_strutture_ipotesi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_strutture_ipotesi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_strutture_ipotesi_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_strutture_ipotesi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_strutture_ipotesi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_strutture_ipotesi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_sondaggi;

                DROP TABLE pyarchinit_sondaggi;

                CREATE TABLE pyarchinit_sondaggi (
                    gid          INTEGER                  PRIMARY KEY
                                                          NOT NULL,
                    sito_sond    [CHARACTER VARYING] (80),
                    id_sondaggio [CHARACTER VARYING] (80),
                    the_geom     POLYGON
                );

                INSERT INTO pyarchinit_sondaggi (
                                                    gid,
                                                    sito_sond,
                                                    id_sondaggio,
                                                    the_geom
                                                )
                                                SELECT id,
                                                       sito_sond,
                                                       id_sondaggio,
                                                       the_geom
                                                  FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_sondaggi_the_geom
                        BEFORE INSERT
                            ON pyarchinit_sondaggi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sondaggi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sondaggi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_sondaggi_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_sondaggi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sondaggi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sondaggi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_siti_polygonal;

                DROP TABLE pyarchinit_siti_polygonal;

                CREATE TABLE pyarchinit_siti_polygonal (
                    gid      INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito_id  TEXT,
                    the_geom POLYGON
                );

                INSERT INTO pyarchinit_siti_polygonal (
                                                          gid,
                                                          sito_id,
                                                          the_geom
                                                      )
                                                      SELECT pkuid,
                                                             sito_id,
                                                             the_geom
                                                        FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_siti_polygonal_the_geom
                        BEFORE INSERT
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti_polygonal.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti_polygonal' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_siti_polygonal_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti_polygonal.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti_polygonal' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER gii_pyarchinit_siti_polygonal_the_geom
                         AFTER INSERT
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_siti_polygonal_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER giu_pyarchinit_siti_polygonal_the_geom
                         AFTER UPDATE
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_siti_polygonal_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER gid_pyarchinit_siti_polygonal_the_geom
                         AFTER DELETE
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_siti_polygonal_the_geom
                          WHERE pkid = OLD.rowid;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_siti;

                DROP TABLE pyarchinit_siti;

                CREATE TABLE pyarchinit_siti (
                    gid        INTEGER                  NOT NULL
                                                        PRIMARY KEY AUTOINCREMENT,
                    id_sito    [CHARACTER VARYING] (80),
                    sito_nome  [CHARACTER VARYING] (80),
                    descr_sito [CHARACTER VARYING],
                    the_geom   POINT
                );

                INSERT INTO pyarchinit_siti (
                                                gid,
                                                id_sito,
                                                sito_nome,
                                                descr_sito,
                                                the_geom
                                            )
                                            SELECT id,
                                                   id_sito,
                                                   sito_nome,
                                                   descr_sito,
                                                   the_geom
                                              FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_siti_the_geom
                        BEFORE INSERT
                            ON pyarchinit_siti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_siti_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_siti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_ripartizioni_spaziali;

                DROP TABLE pyarchinit_ripartizioni_spaziali;

                CREATE TABLE pyarchinit_ripartizioni_spaziali (
                    gid      INTEGER                  NOT NULL
                                                      PRIMARY KEY AUTOINCREMENT,
                    id_rs    [CHARACTER VARYING] (80),
                    sito_rs  [CHARACTER VARYING] (80),
                    tip_rip  [CHARACTER VARYING],
                    descr_rs [CHARACTER VARYING],
                    the_geom POLYGON
                );

                INSERT INTO pyarchinit_ripartizioni_spaziali (
                                                                 gid,
                                                                 id_rs,
                                                                 sito_rs,
                                                                 tip_rip,
                                                                 descr_rs,
                                                                 the_geom
                                                             )
                                                             SELECT id,
                                                                    id_rs,
                                                                    sito_rs,
                                                                    tip_rip,
                                                                    descr_rs,
                                                                    the_geom
                                                               FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_ripartizioni_spaziali_the_geom
                        BEFORE INSERT
                            ON pyarchinit_ripartizioni_spaziali
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_ripartizioni_spaziali.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_ripartizioni_spaziali' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_ripartizioni_spaziali_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_ripartizioni_spaziali
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_ripartizioni_spaziali.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_ripartizioni_spaziali' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_reperti;

                DROP TABLE pyarchinit_reperti;

                CREATE TABLE pyarchinit_reperti (
                    gid      INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_rep   INTEGER,
                    siti     TEXT,
                    link     TEXT,
                    the_geom POINT
                );

                INSERT INTO pyarchinit_reperti (
                                                   gid,
                                                   id_rep,
                                                   siti,
                                                   link,
                                                   the_geom
                                               )
                                               SELECT ROWIND,
                                                      id_rep,
                                                      siti,
                                                      link,
                                                      the_geom
                                                 FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_reperti_the_geom
                        BEFORE INSERT
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_reperti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_reperti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_reperti_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_reperti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_reperti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER gii_pyarchinit_reperti_the_geom
                         AFTER INSERT
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_reperti_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER giu_pyarchinit_reperti_the_geom
                         AFTER UPDATE
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_reperti_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER gid_pyarchinit_reperti_the_geom
                         AFTER DELETE
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_reperti_the_geom
                          WHERE pkid = OLD.rowid;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_quote;

                DROP TABLE pyarchinit_quote;

                CREATE TABLE pyarchinit_quote (
                    gid               INTEGER                  NOT NULL
                                                               PRIMARY KEY AUTOINCREMENT,
                    sito_q            [CHARACTER VARYING] (80),
                    area_q            INTEGER,
                    us_q              INTEGER,
                    unita_misu_q      [CHARACTER VARYING] (80),
                    quota_q           [DOUBLE PRECISION],
                    data              [CHARACTER VARYING],
                    disegnatore       [CHARACTER VARYING],
                    rilievo_originale [CHARACTER VARYING],
                    the_geom          POINT
                );

                INSERT INTO pyarchinit_quote (
                                                 gid,
                                                 sito_q,
                                                 area_q,
                                                 us_q,
                                                 unita_misu_q,
                                                 quota_q,
                                                 data,
                                                 disegnatore,
                                                 rilievo_originale,
                                                 the_geom
                                             )
                                             SELECT id,
                                                    sito_q,
                                                    area_q,
                                                    us_q,
                                                    unita_misu_q,
                                                    quota_q,
                                                    data,
                                                    disegnatore,
                                                    rilievo_originale,
                                                    the_geom
                                               FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_quote_the_geom
                        BEFORE INSERT
                            ON pyarchinit_quote
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_quote.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_quote' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_quote_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_quote
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_quote.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_quote' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_punti_rif;

                DROP TABLE pyarchinit_punti_rif;

                CREATE TABLE pyarchinit_punti_rif (
                    gid                INTEGER                  NOT NULL
                                                                PRIMARY KEY AUTOINCREMENT,
                    sito               [CHARACTER VARYING] (80),
                    def_punto          [CHARACTER VARYING] (80),
                    id_punto           [CHARACTER VARYING] (80),
                    quota              [DOUBLE PRECISION],
                    unita_misura_quota [CHARACTER VARYING],
                    area               INTEGER,
                    the_geom           POINT
                );

                INSERT INTO pyarchinit_punti_rif (
                                                     gid,
                                                     sito,
                                                     def_punto,
                                                     id_punto,
                                                     quota,
                                                     unita_misura_quota,
                                                     area,
                                                     the_geom
                                                 )
                                                 SELECT id,
                                                        sito,
                                                        def_punto,
                                                        id_punto,
                                                        quota,
                                                        unita_misura_quota,
                                                        area,
                                                        the_geom
                                                   FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_punti_rif_the_geom
                        BEFORE INSERT
                            ON pyarchinit_punti_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_punti_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_punti_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_punti_rif_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_punti_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_punti_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_punti_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_linee_rif;

                DROP TABLE pyarchinit_linee_rif;

                CREATE TABLE pyarchinit_linee_rif (
                    gid        INTEGER                   NOT NULL
                                                         PRIMARY KEY AUTOINCREMENT,
                    sito       [CHARACTER VARYING] (300),
                    definizion [CHARACTER VARYING] (80),
                    descrizion [CHARACTER VARYING] (80),
                    the_geom   LINESTRING
                );

                INSERT INTO pyarchinit_linee_rif (
                                                     gid,
                                                     sito,
                                                     definizion,
                                                     descrizion,
                                                     the_geom
                                                 )
                                                 SELECT id,
                                                        sito,
                                                        definizion,
                                                        descrizion,
                                                        the_geom
                                                   FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_linee_rif_the_geom
                        BEFORE INSERT
                            ON pyarchinit_linee_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_linee_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_linee_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_linee_rif_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_linee_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_linee_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_linee_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_individui;

                DROP TABLE pyarchinit_individui;

                CREATE TABLE pyarchinit_individui (
                    gid             INTEGER                   NOT NULL
                                                              PRIMARY KEY AUTOINCREMENT,
                    sito            [CHARACTER VARYING] (255),
                    sigla_struttura [CHARACTER VARYING] (255),
                    note            [CHARACTER VARYING] (255),
                    id_individuo    INTEGER,
                    the_geom        POINT
                );

                INSERT INTO pyarchinit_individui (
                                                     gid,
                                                     sito,
                                                     sigla_struttura,
                                                     note,
                                                     id_individuo,
                                                     the_geom
                                                 )
                                                 SELECT id,
                                                        sito,
                                                        sigla_struttura,
                                                        note,
                                                        id_individuo,
                                                        the_geom
                                                   FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_individui_the_geom
                        BEFORE INSERT
                            ON pyarchinit_individui
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_individui.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_individui' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_individui_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_individui
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_individui.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_individui' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_documentazione;

                DROP TABLE pyarchinit_documentazione;

                CREATE TABLE pyarchinit_documentazione (
                    gid          INTEGER    PRIMARY KEY AUTOINCREMENT,
                    sito         TEXT,
                    nome_doc     TEXT,
                    tipo_doc     TEXT,
                    path_qgis_pj TEXT,
                    the_geom     LINESTRING
                );

                INSERT INTO pyarchinit_documentazione (
                                                          gid,
                                                          sito,
                                                          nome_doc,
                                                          tipo_doc,
                                                          path_qgis_pj,
                                                          the_geom
                                                      )
                                                      SELECT pkuid,
                                                             sito,
                                                             nome_doc,
                                                             tipo_doc,
                                                             path_qgis_pj,
                                                             the_geom
                                                        FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_documentazione_the_geom
                        BEFORE INSERT
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_documentazione.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_documentazione' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_documentazione_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_documentazione.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_documentazione' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER gii_pyarchinit_documentazione_the_geom
                         AFTER INSERT
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_documentazione_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER giu_pyarchinit_documentazione_the_geom
                         AFTER UPDATE
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_documentazione_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER gid_pyarchinit_documentazione_the_geom
                         AFTER DELETE
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_documentazione_the_geom
                          WHERE pkid = OLD.rowid;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_campionature;

                DROP TABLE pyarchinit_campionature;

                CREATE TABLE pyarchinit_campionature (
                    gid        INTEGER                   NOT NULL
                                                         PRIMARY KEY AUTOINCREMENT,
                    id_campion INTEGER,
                    sito       [CHARACTER VARYING] (200),
                    tipo_camp  [CHARACTER VARYING] (200),
                    dataz      [CHARACTER VARYING] (200),
                    cronologia INTEGER,
                    link_immag [CHARACTER VARYING] (500),
                    sigla_camp [CHARACTER VARYING],
                    the_geom   POINT
                );

                INSERT INTO pyarchinit_campionature (
                                                        gid,
                                                        id_campion,
                                                        sito,
                                                        tipo_camp,
                                                        dataz,
                                                        cronologia,
                                                        link_immag,
                                                        sigla_camp,
                                                        the_geom
                                                    )
                                                    SELECT id,
                                                           id_campion,
                                                           sito,
                                                           tipo_camp,
                                                           dataz,
                                                           cronologia,
                                                           link_immag,
                                                           sigla_camp,
                                                           the_geom
                                                      FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_campionature_the_geom
                        BEFORE INSERT
                            ON pyarchinit_campionature
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_campionature.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_campionature' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_campionature_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_campionature
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_campionature.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_campionature' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_sezioni;

                DROP TABLE pyarchinit_sezioni;

                CREATE TABLE pyarchinit_sezioni (
                    gid        INTEGER                  NOT NULL
                                                        PRIMARY KEY AUTOINCREMENT,
                    id_sezione [CHARACTER VARYING] (80),
                    sito       [CHARACTER VARYING] (80),
                    area       INTEGER,
                    descr      [CHARACTER VARYING] (80),
                    the_geom   LINESTRING,
                    tipo_doc   TEXT,
                    nome_doc   TEXT
                );

                INSERT INTO pyarchinit_sezioni (
                                                   gid,
                                                   id_sezione,
                                                   sito,
                                                   area,
                                                   descr,
                                                   the_geom,
                                                   tipo_doc,
                                                   nome_doc
                                               )
                                               SELECT id,
                                                      id_sezione,
                                                      sito,
                                                      area,
                                                      descr,
                                                      the_geom,
                                                      tipo_doc,
                                                      nome_doc
                                                 FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_sezioni_the_geom
                        BEFORE INSERT
                            ON pyarchinit_sezioni
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sezioni.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sezioni' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_sezioni_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_sezioni
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sezioni.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sezioni' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                 
                
                
                
                        ''')
            
        except Exception as e:
            pass#QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
    
    
    def test2(self):
        try:
            
            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()
            
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            
            con = sqlite3.connect(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            cur = con.cursor()
            drop_ = '''DROP TABLE IF EXISTS sqlitestudio_temp_table2;'''
            cur.execute(drop_)
            drop_2 = '''DROP TABLE IF EXISTS sqlitestudio_temp_table;'''
            # cur.execute(drop_2)
            # drop_3 = '''DROP VIEW IF EXISTS pyarchinit_strutture_view;'''
            # cur.execute(drop_3)
            # drop_4 = '''DROP VIEW IF EXISTS pyarchinit_site_view;'''
            # cur.execute(drop_4)
            cur.executescript('''PRAGMA foreign_keys = 0;
                
                DROP VIEW if EXISTS inventario_materiali_view;
                CREATE VIEW inventario_materiali_view AS
                    SELECT 
                           a.id_sito AS id_sito,
                           a.sito_nome AS sito_nome,
                           a.descr_sito AS descr_sito,
                           a.the_geom AS the_geom,
                           b.rowid AS rowid_1,
                           b.id_invmat AS id_invmat,
                           b.sito AS sito,
                           b.numero_inventario AS numero_inventario,
                           b.tipo_reperto AS tipo_reperto,
                           b.criterio_schedatura AS criterio_schedatura,
                           b.definizione AS definizione,
                           b.descrizione AS descrizione,
                           b.area AS area,
                           b.us AS us,
                           b.lavato AS lavato,
                           b.nr_cassa AS nr_cassa,
                           b.luogo_conservazione AS luogo_conservazione,
                           b.stato_conservazione AS stato_conservazione,
                           b.datazione_reperto AS datazione_reperto,
                           b.elementi_reperto AS elementi_reperto,
                           b.misurazioni AS misurazioni,
                           b.rif_biblio AS rif_biblio,
                           b.tecnologie AS tecnologie,
                           b.forme_minime AS forme_minime,
                           b.forme_massime AS forme_massime,
                           b.totale_frammenti AS totale_frammenti,
                           b.corpo_ceramico AS corpo_ceramico,
                           b.rivestimento AS rivestimento,
                           b.diametro_orlo AS diametro_orlo,
                           b.peso AS peso,
                           b.tipo AS tipo,
                           b.eve_orlo AS eve_orlo,
                           b.repertato AS repertato,
                           b.diagnostico AS diagnostico,
                           b.n_reperto AS n_reperto
                      FROM pyarchinit_siti AS a
                           JOIN
                           inventario_materiali_table AS b ON (a.sito_nome = b.sito);
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW if EXISTS pyarchinit_doc_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_doc_view AS
                    SELECT a.rowid AS rowid,
                           a.id_documentazione AS id_documentazione,
                           a.sito AS sito,
                           a.nome_doc AS nome_doc,
                           a.data AS data,
                           a.tipo_documentazione AS tipo_documentazione,
                           a.sorgente AS sorgente,
                           a.scala AS scala,
                           a.disegnatore AS disegnatore,
                           a.note AS note,
                           b.rowid AS rowid_1,
                           
                           b.sito AS sito_1,
                           b.nome_doc AS nome_doc_1,
                           b.tipo_doc AS tipo_doc,
                           b.path_qgis_pj AS path_qgis_pj,
                           b.the_geom AS the_geom
                      FROM documentazione_table AS a
                           JOIN
                           pyarchinit_documentazione AS b ON (a.sito = b.sito AND 
                                                              a.nome_doc = b.nome_doc AND 
                                                              a.tipo_documentazione = b.tipo_doc);
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW if EXISTS pyarchinit_individui_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_individui_view AS
                    SELECT a.rowid AS rowid,
                           a.id_scheda_ind AS id_scheda_ind,
                           a.sito AS sito,
                           a.area AS area,
                           a.us AS us,
                           a.nr_individuo AS nr_individuo,
                           a.data_schedatura AS data_schedatura,
                           a.schedatore AS schedatore,
                           a.sesso AS sesso,
                           a.eta_min AS eta_min,
                           a.eta_max AS eta_max,
                           a.classi_eta AS classi_eta,
                           a.osservazioni AS osservazioni,
                           b.rowid AS rowid_1,
                          
                           b.sito AS sito_1,
                           b.sigla_struttura AS sigla_struttura,
                           b.note AS note,
                           b.id_individuo AS id_individuo,
                           b.the_geom AS the_geom
                      FROM individui_table AS a
                           JOIN
                           pyarchinit_individui AS b ON (a.sito = b.sito AND 
                                                         a.nr_individuo = b.id_individuo);
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW if EXISTS pyarchinit_quote_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_quote_view AS
                    SELECT a.rowid AS rowid,
                           a.id_us AS id_us,
                           a.sito AS sito,
                           a.area AS area,
                           a.us AS us,
                           a.d_stratigrafica AS d_stratigrafica,
                           a.d_interpretativa AS d_interpretativa,
                           a.descrizione AS descrizione,
                           a.interpretazione AS interpretazione,
                           a.periodo_iniziale AS periodo_iniziale,
                           a.fase_iniziale AS fase_iniziale,
                           a.periodo_finale AS periodo_finale,
                           a.fase_finale AS fase_finale,
                           a.scavato AS scavato,
                           a.attivita AS attivita,
                           a.anno_scavo AS anno_scavo,
                           a.metodo_di_scavo AS metodo_di_scavo,
                           a.inclusi AS inclusi,
                           a.campioni AS campioni,
                           a.rapporti AS rapporti,
                           a.data_schedatura AS data_schedatura,
                           a.schedatore AS schedatore,
                           a.formazione AS formazione,
                           a.stato_di_conservazione AS stato_di_conservazione,
                           a.colore AS colore,
                           a.consistenza AS consistenza,
                           a.struttura AS struttura,
                           a.cont_per AS cont_per,
                           a.order_layer AS order_layer,
                           a.documentazione AS documentazione,
                           b.rowid AS rowid_1,
                           
                           b.sito_q AS sito_q,
                           b.area_q AS area_q,
                           b.us_q AS us_q,
                           b.unita_misu_q AS unita_misu_q,
                           b.quota_q AS quota_q,
                           b.data AS data,
                           b.disegnatore AS disegnatore,
                           b.rilievo_originale AS rilievo_originale,
                           b.the_geom AS the_geom
                      FROM us_table AS a
                           JOIN
                           pyarchinit_quote AS b ON (a.sito = b.sito_q AND 
                                                     a.area = b.area_q AND 
                                                     a.us = b.us_q) 
                     ORDER BY a.order_layer DESC;
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW if EXISTS pyarchinit_reperti_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_reperti_view AS
                    SELECT a.rowid AS rowid,
                           a.the_geom AS the_geom,
                           a.id_rep AS id_rep,
                           a.siti AS siti,
                           a.link AS link,
                           b.rowid AS rowid_1,
                           b.id_invmat AS id_invmat,
                           b.sito AS sito,
                           b.numero_inventario AS numero_inventario,
                           b.tipo_reperto AS tipo_reperto,
                           b.criterio_schedatura AS criterio_schedatura,
                           b.definizione AS definizione,
                           b.descrizione AS descrizione,
                           b.area AS area,
                           b.us AS us,
                           b.lavato AS lavato,
                           b.nr_cassa AS nr_cassa,
                           b.luogo_conservazione AS luogo_conservazione,
                           b.stato_conservazione AS stato_conservazione,
                           b.datazione_reperto AS datazione_reperto,
                           b.elementi_reperto AS elementi_reperto,
                           b.misurazioni AS misurazioni,
                           b.rif_biblio AS rif_biblio,
                           b.tecnologie AS tecnologie,
                           b.forme_minime AS forme_minime,
                           b.forme_massime AS forme_massime,
                           b.totale_frammenti AS totale_frammenti,
                           b.corpo_ceramico AS corpo_ceramico,
                           b.rivestimento AS rivestimento
                      FROM pyarchinit_reperti AS a
                           JOIN
                           inventario_materiali_table_toimp AS b ON (a.siti = b.sito AND 
                                                                     a.id_rep = b.numero_inventario);
                
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW if EXISTS pyarchinit_sezioni_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_sezioni_view AS
                    SELECT a.rowid AS rowid,
                           
                           a.sito AS sito,
                           a.area AS area,
                           a.the_geom AS the_geom,
                           a.tipo_doc AS tipo_doc,
                           a.nome_doc AS nome_doc,
                           b.rowid AS rowid_1,
                           b.id_documentazione AS id_documentazione,
                           b.sito AS sito_1,
                           b.nome_doc AS nome_doc_1,
                           b.data AS data,
                           b.tipo_documentazione AS tipo_documentazione,
                           b.sorgente AS sorgente,
                           b.scala AS scala,
                           b.disegnatore AS disegnatore,
                           b.note AS note
                      FROM pyarchinit_sezioni AS a
                           JOIN
                           documentazione_table AS b ON (a.sito = b.sito AND 
                                                         a.tipo_doc = b.tipo_documentazione AND 
                                                         a.nome_doc = b.nome_doc);
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW IF EXISTS pyarchinit_site_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_site_view AS
                    SELECT a.rowid AS rowid,
                           
                           a.id_sito AS id_sito,
                           a.sito_nome AS sito_nome,
                           a.descr_sito AS descr_sito,
                           a.the_geom AS the_geom,
                           b.rowid AS rowid_1,
                           b.id_sito AS id_sito_1,
                           b.sito AS sito,
                           b.nazione AS nazione,
                           b.regione AS regione,
                           b.comune AS comune,
                           b.descrizione AS descrizione,
                           b.provincia AS provincia,
                           b.definizione_sito AS definizione_sito
                      FROM pyarchinit_siti AS a
                           JOIN
                           site_table AS b ON (a.sito_nome = b.sito) 
                     ORDER BY b.definizione_sito;
                
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW IF EXISTS pyarchinit_siti_polygonal_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_siti_polygonal_view AS
                    SELECT a.rowid AS rowid,
                           
                           a.sito_id AS sito_id,
                           a.the_geom AS the_geom,
                           b.rowid AS rowid_1,
                           b.id_sito AS id_sito,
                           b.sito AS sito,
                           b.nazione AS nazione,
                           b.regione AS regione,
                           b.comune AS comune,
                           b.descrizione AS descrizione,
                           b.provincia AS provincia,
                           b.definizione_sito AS definizione_sito
                      FROM pyarchinit_siti_polygonal AS a
                           JOIN
                           site_table AS b ON (a.sito_id = b.sito) 
                     ORDER BY b.sito,
                              b.descrizione;
                              
                
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW IF EXISTS pyarchinit_strutture_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_strutture_view AS
                    SELECT a.rowid AS rowid,
                           
                           a.sito AS sito,
                           a.id_strutt AS id_strutt,
                           a.per_iniz AS per_iniz,
                           a.per_fin AS per_fin,
                           a.dataz_ext AS dataz_ext,
                           a.fase_iniz AS fase_iniz,
                           a.fase_fin AS fase_fin,
                           a.descrizione AS descrizione,
                           a.the_geom AS the_geom,
                           a.sigla_strut AS sigla_strut,
                           a.nr_strut AS nr_strut,
                           b.rowid AS rowid_1,
                           b.id_struttura AS id_struttura,
                           b.sito AS sito_1,
                           b.sigla_struttura AS sigla_struttura,
                           b.numero_struttura AS numero_struttura,
                           b.categoria_struttura AS categoria_struttura,
                           b.tipologia_struttura AS tipologia_struttura,
                           b.definizione_struttura AS definizione_struttura,
                           b.descrizione AS descrizione_1,
                           b.interpretazione AS interpretazione,
                           b.periodo_iniziale AS periodo_iniziale,
                           b.fase_iniziale AS fase_iniziale,
                           b.periodo_finale AS periodo_finale,
                           b.fase_finale AS fase_finale,
                           b.datazione_estesa AS datazione_estesa,
                           b.materiali_impiegati AS materiali_impiegati,
                           b.elementi_strutturali AS elementi_strutturali,
                           b.rapporti_struttura AS rapporti_struttura,
                           b.misure_struttura AS misure_struttura
                      FROM pyarchinit_strutture_ipotesi AS a
                           JOIN
                           struttura_table AS b ON (a.sito = b.sito AND 
                                                    a.sigla_strut = b.sigla_struttura AND 
                                                    a.nr_strut = b.numero_struttura);
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW if exists pyarchinit_tomba_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_tomba_view AS
                    SELECT a.id_tomba AS id_tomba,
                           a.sito AS sito,
                           a.area AS area,
                           a.nr_scheda_taf AS nr_scheda_taf,
                           a.sigla_struttura AS sigla_struttura,
                           a.nr_struttura AS nr_struttura,
                           a.nr_individuo AS nr_individuo,
                           a.rito AS rito,
                           a.descrizione_taf AS descrizione_taf,
                           a.interpretazione_taf AS interpretazione_taf,
                           a.segnacoli AS segnacoli,
                           a.canale_libatorio_si_no AS canale_libatorio_si_no,
                           a.oggetti_rinvenuti_esterno AS oggetti_rinvenuti_esterno,
                           a.stato_di_conservazione AS stato_di_conservazione,
                           a.copertura_tipo AS copertura_tipo,
                           a.tipo_contenitore_resti AS tipo_contenitore_resti,
                           a.tipo_deposizione AS tipo_deposizione,
                           a.tipo_sepoltura AS tipo_sepoltura,
                           a.corredo_presenza AS corredo_presenza,
                           a.corredo_tipo AS corredo_tipo,
                           a.corredo_descrizione AS corredo_descrizione,
                           b.rowid AS rowid,
                           
                           b.sito AS sito_1,
                           b.nr_scheda AS nr_scheda,
                           b.the_geom AS the_geom
                      FROM tomba_table AS a
                           JOIN
                           pyarchinit_tafonomia AS b ON (a.sito = b.sito AND 
                                                         a.nr_scheda_taf = b.nr_scheda) 
                     ORDER BY a.nr_scheda_taf;
                
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                DROP VIEW IF EXISTS pyarchinit_us_negative_doc_view;
                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;
                CREATE VIEW pyarchinit_us_negative_doc_view AS
                    SELECT a.rowid AS rowid,
                           
                           a.sito_n AS sito_n,
                           a.area_n AS area_n,
                           a.us_n AS us_n,
                           a.tipo_doc_n AS tipo_doc_n,
                           a.nome_doc_n AS nome_doc_n,
                           a.the_geom AS the_geom,
                           b.rowid AS rowid_1,
                           b.id_us AS id_us,
                           b.sito AS sito,
                           b.area AS area,
                           b.us AS us,
                           b.d_stratigrafica AS d_stratigrafica,
                           b.d_interpretativa AS d_interpretativa,
                           b.descrizione AS descrizione,
                           b.interpretazione AS interpretazione,
                           b.periodo_iniziale AS periodo_iniziale,
                           b.fase_iniziale AS fase_iniziale,
                           b.periodo_finale AS periodo_finale,
                           b.fase_finale AS fase_finale,
                           b.scavato AS scavato,
                           b.attivita AS attivita,
                           b.anno_scavo AS anno_scavo,
                           b.metodo_di_scavo AS metodo_di_scavo,
                           b.inclusi AS inclusi,
                           b.campioni AS campioni,
                           b.rapporti AS rapporti,
                           b.data_schedatura AS data_schedatura,
                           b.schedatore AS schedatore,
                           b.formazione AS formazione,
                           b.stato_di_conservazione AS stato_di_conservazione,
                           b.colore AS colore,
                           b.consistenza AS consistenza,
                           b.struttura AS struttura,
                           b.cont_per AS cont_per,
                           b.order_layer AS order_layer,
                           b.documentazione AS documentazione,
                           b.unita_tipo AS unita_tipo,
                           b.settore AS settore,
                           b.quad_par AS quad_par,
                           b.ambient AS ambient,
                           b.saggio AS saggio,
                           b.elem_datanti AS elem_datanti,
                           b.funz_statica AS funz_statica,
                           b.lavorazione AS lavorazione,
                           b.spess_giunti AS spess_giunti,
                           b.letti_posa AS letti_posa,
                           b.alt_mod AS alt_mod,
                           b.un_ed_riass AS un_ed_riass,
                           b.reimp AS reimp,
                           b.posa_opera AS posa_opera,
                           b.quota_min_usm AS quota_min_usm,
                           b.quota_max_usm AS quota_max_usm,
                           b.cons_legante AS cons_legante,
                           b.col_legante AS col_legante,
                           b.aggreg_legante AS aggreg_legante,
                           b.con_text_mat AS con_text_mat,
                           b.col_materiale AS col_materiale,
                           b.inclusi_materiali_usm AS inclusi_materiali_usm,
                           b.n_catalogo_generale AS n_catalogo_generale,
                           b.n_catalogo_interno AS n_catalogo_interno,
                           b.n_catalogo_internazionale AS n_catalogo_internazionale,
                           b.soprintendenza AS soprintendenza,
                           b.quota_relativa AS quota_relativa,
                           b.quota_abs AS quota_abs,
                           b.ref_tm AS ref_tm,
                           b.ref_ra AS ref_ra,
                           b.ref_n AS ref_n,
                           b.posizione AS posizione,
                           b.criteri_distinzione AS criteri_distinzione,
                           b.modo_formazione AS modo_formazione,
                           b.componenti_organici AS componenti_organici,
                           b.componenti_inorganici AS componenti_inorganici,
                           b.lunghezza_max AS lunghezza_max,
                           b.altezza_max AS altezza_max,
                           b.altezza_min AS altezza_min,
                           b.profondita_max AS profondita_max,
                           b.profondita_min AS profondita_min,
                           b.larghezza_media AS larghezza_media,
                           b.quota_max_abs AS quota_max_abs,
                           b.quota_max_rel AS quota_max_rel,
                           b.quota_min_abs AS quota_min_abs,
                           b.quota_min_rel AS quota_min_rel,
                           b.osservazioni AS osservazioni,
                           b.datazione AS datazione,
                           b.flottazione AS flottazione,
                           b.setacciatura AS setacciatura,
                           b.affidabilita AS affidabilita,
                           b.direttore_us AS direttore_us,
                           b.responsabile_us AS responsabile_us,
                           b.cod_ente_schedatore AS cod_ente_schedatore,
                           b.data_rilevazione AS data_rilevazione,
                           b.data_rielaborazione AS data_rielaborazione,
                           b.lunghezza_usm AS lunghezza_usm,
                           b.altezza_usm AS altezza_usm,
                           b.spessore_usm AS spessore_usm,
                           b.tecnica_muraria_usm AS tecnica_muraria_usm,
                           b.modulo_usm AS modulo_usm,
                           b.campioni_malta_usm AS campioni_malta_usm,
                           b.campioni_mattone_usm AS campioni_mattone_usm,
                           b.campioni_pietra_usm AS campioni_pietra_usm,
                           b.provenienza_materiali_usm AS provenienza_materiali_usm,
                           b.criteri_distinzione_usm AS criteri_distinzione_usm,
                           b.uso_primario_usm AS uso_primario_usm
                      FROM pyarchinit_us_negative_doc AS a
                           JOIN
                           us_table AS b ON (a.sito_n = b.sito AND 
                                             a.area_n = b.area AND 
                                             a.us_n = b.us);
                        
                        PRAGMA foreign_keys = 1;
            ''')
            c.close()
        except KeyError as e:
            pass#QMessageBox.warning(self, "ok", str(e), QMessageBox.Ok)
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)
    
    def customize(self):
        if self.comboBox_Database.currentText()=='sqlite':
            self.setComboBoxEnable(["self.lineEdit_DBname"], "False")
        elif self.comboBox_Database.currentText()=='postgres':
            self.setComboBoxEnable(["self.lineEdit_DBname"], "True")
    def db_uncheck(self):
        self.toolButton_active.setChecked(False)
    def upd_individui_table(self):
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        conn = Connection()
        db_url = conn.conn_str()
        test_conn = db_url.find('sqlite')
        if test_conn == 0:
            try:
                engine = create_engine(db_url, echo=True)

                listen(engine, 'connect', self.load_spatialite)
                c = engine.connect()
                sql_upd=("""
                        CREATE TABLE sqlitestudio_temp_table_ AS SELECT *
                                                                  FROM individui_table;""")

                        
                        
                sql_upd1=("""DROP TABLE individui_table;""")

                sql_upd2=(""" CREATE TABLE individui_table (
                            id_scheda_ind            INTEGER        NOT NULL,
                            sito                     TEXT,
                            area                     TEXT,
                            us                       TEXT,
                            nr_individuo             INTEGER,
                            data_schedatura          VARCHAR (100),
                            schedatore               VARCHAR (100),
                            sesso                    VARCHAR (100),
                            eta_min                  TEXT,
                            eta_max                  TEXT,
                            classi_eta               VARCHAR (100),
                            osservazioni             TEXT,
                            sigla_struttura          TEXT,
                            nr_struttura             TEXT,
                            completo_si_no           TEXT,
                            disturbato_si_no         TEXT,
                            in_connessione_si_no     TEXT,
                            lunghezza_scheletro      NUMERIC (6, 2),
                            posizione_scheletro      TEXT,
                            posizione_cranio         TEXT,
                            posizione_arti_superiori TEXT,
                            posizione_arti_inferiori TEXT,
                            orientamento_asse        TEXT,
                            orientamento_azimut      TEXT,
                            PRIMARY KEY (
                                id_scheda_ind
                            ),
                            CONSTRAINT ID_individuo_unico UNIQUE (
                                sito,
                                nr_individuo
                            )
                        );""")

                sql_upd3=("""INSERT INTO individui_table (
                                                    id_scheda_ind,
                                                    sito,
                                                    area,
                                                    us,
                                                    nr_individuo,
                                                    data_schedatura,
                                                    schedatore,
                                                    sesso,
                                                    eta_min,
                                                    eta_max,
                                                    classi_eta,
                                                    osservazioni,
                                                    sigla_struttura,
                                                    nr_struttura,
                                                    completo_si_no,
                                                    disturbato_si_no,
                                                    in_connessione_si_no,
                                                    lunghezza_scheletro,
                                                    posizione_scheletro,
                                                    posizione_cranio,
                                                    posizione_arti_superiori,
                                                    posizione_arti_inferiori,
                                                    orientamento_asse,
                                                    orientamento_azimut
                                                )
                                                SELECT id_scheda_ind,
                                                       sito,
                                                       area,
                                                       us,
                                                       nr_individuo,
                                                       data_schedatura,
                                                       schedatore,
                                                       sesso,
                                                       eta_min,
                                                       eta_max,
                                                       classi_eta,
                                                       osservazioni,
                                                       sigla_struttura,
                                                       nr_struttura,
                                                       completo_si_no,
                                                       disturbato_si_no,
                                                       in_connessione_si_no,
                                                       lunghezza_scheletro,
                                                       posizione_scheletro,
                                                       posizione_cranio,
                                                       posizione_arti_superiori,
                                                       posizione_arti_inferiori,
                                                       orientamento_asse,
                                                       orientamento_azimut
                                                  FROM sqlitestudio_temp_table_;""")

                        
                sql_upd4=("""DROP TABLE sqlitestudio_temp_table_;""")
                        
                c.execute(sql_upd)
                c.execute(sql_upd1)  
                c.execute(sql_upd2)  
                c.execute(sql_upd3)  
                c.execute(sql_upd4)              
                c.close()
                
            
            except Exception as e:
                QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        else:
            pass
    
    
    
    def geometry_conn(self):
        pass
        # if self.comboBox_server_rd.currentText()!='sqlite':
            # self.pushButton_import_geometry.setEnabled(False)
        # else:
            # self.pushButton_import_geometry.setEnabled(True)

    def message(self):
        if self.checkBox_abort.isChecked():
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Se i ci sono duplicati l'importazione verrà abortita.\n Se vuoi ignorare i duplicati o aggiornare con i dati nuovi spunta una delle opzioni ignora o aggiorna", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Wenn es Duplikate gibt, wird der Import abgebrochen.\n Wenn Sie die Duplikate ignorieren oder mit neuen Daten aktualisieren möchten, aktivieren Sie eine der Optionen ignorieren oder aktualisieren", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "If there are duplicates the import will be aborted.\n If you want to ignore the duplicates or update with new data check one of the options ignore or replace", QMessageBox.Ok)
        
        if self.checkBox_ignore.isChecked():
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", 'Verranno copiati solo i dati nuovi', QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", 'Es werden nur neue Daten kopiert.', QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", 'Only new data will be copied', QMessageBox.Ok)
        
        if self.checkBox_replace.isChecked():
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", 'Verranno copiati i dati nuovi e aggiornati quelli esistenti', QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", 'Neue Daten werden kopiert und bestehende Daten werden aktualisiert', QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", 'New data will be copied and existing data will be updated', QMessageBox.Ok)
        
    
    def check(self):
        try:
            if self.checkBox_ignore.isChecked():
                self.message()
                @compiles(Insert)
                def _prefix_insert_with_ignore(insert_srt, compiler, **kw):

                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR IGNORE'), **kw)
                    else:
                        #if the connection is postgresql
                        ck = insert_srt.table.constraints
                        # pk = insert_srt.table.primary_key
                        insert = compiler.visit_insert(insert_srt, **kw)
                        c = next(x for x in ck if isinstance(x, sa.UniqueConstraint))
                        column_names = [col.name for col in c.columns]
                        s= ", ".join(column_names)
                        ondup = f'ON CONFLICT ({s})DO NOTHING'
                    
                        upsert = ' '.join((insert, ondup))
                        return upsert
                       
                        
           
            if self.checkBox_replace.isChecked():
                self.message()
                @compiles(Insert)
                def _prefix_insert_with_replace(insert_srt, compiler, **kw):
                    ##############importo i dati nuovi aggiornando i vecchi dati########################
                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR REPLACE'), **kw)
                    else:
                        #return compiler.visit_insert(insert.prefix_with(''), **kw)
                        
                        ck = insert_srt.table.constraints
                        insert = compiler.visit_insert(insert_srt, **kw)
                        c = next(x for x in ck if isinstance(x, sa.UniqueConstraint))
                        column_names = [col.name for col in c.columns]
                        s= ", ".join(column_names)
                        
                        
                        ondup = f"ON CONFLICT ({s}) DO UPDATE SET"
                        updates = ", ".join(f'{c.name}=EXCLUDED.{c.name}' for c in insert_srt.table.columns)
                        upsert = " ".join((insert, ondup, updates))
                        return upsert
        
            if self.checkBox_abort.isChecked():
                #self.message()
                @compiles(Insert)
                def _prefix_insert_with_ignore(insert_srt, compiler, **kw):

                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR ABORT'), **kw)
                    else:
                        #return compiler.visit_insert(insert.prefix_with(''), **kw)
                        pk = insert_srt.table.primary_key
                        insert = compiler.visit_insert(insert_srt, **kw)
                        ondup = f'ON CONFLICT ({",".join(c.name for c in pk)}) DO NOTHING'
                        #updates = ', '.join(f"{c.name}=EXCLUDED.{c.name}" for c in insert_srt.table.columns)
                        upsert = ' '.join((insert, ondup))
                        return insert
        
        
        except:
            pass
    def summary(self):
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']

        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            db = QSqlDatabase("QSQLITE")
            db.setDatabaseName(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            db.open()
            #self.table = QTableView()
            self.model_a = QSqlQueryModel()

            self.tableView_summary.setModel(self.model_a)
            if bool(self.comboBox_sito.currentText()):
                query = QSqlQuery("select distinct a.sito as 'Sito',case when count( distinct a.us)=0  then 'US/USM "
                                  "mancanti' else  count( distinct a.us)  end as 'Totale US/USM',case when count("
                                  "distinct b.numero_inventario)=0 then 'No Materiali' else count(distinct "
                                  "b.numero_inventario)end as 'Totale Materiali',case when count(distinct "
                                  "c.id_struttura)=0 then 'No Strutture' else count(distinct c.id_struttura)end as "
                                  "'Totale strutture',case when count(distinct d.id_tomba)=0 then 'No Tombe' else "
                                  "count(distinct d.id_tomba)end as 'Totale tombe' from us_table as a left join "
                                  "inventario_materiali_table as b on a.sito=b.sito left join struttura_table as c on "
                                  "a.sito=c.sito left join tomba_table as d on a.sito=d.sito where a.sito = '{"
                                  "}'".format(str(self.comboBox_sito.currentText())), db=db)
                self.model_a.setQuery(query)
            else:
                            
                query1 = QSqlQuery("select s.sito as Sito,(select count(distinct id_invmat) from inventario_materiali_table m "
                                   "where s.sito = m.sito) as Materiali,(select count(distinct id_struttura) from "
                                   "struttura_table st where s.sito = st.sito) as Struttura,(select count(distinct "
                                   "id_tomba) from tomba_table t where s.sito = t.sito) as Tombe,"
                                   "(select count(distinct id_us) from us_table ad where s.sito=ad.sito) as US from ("
                                   "select sito , count(distinct id_us) from us_table group by sito) as s order by "
                                   "s.sito;",db=db)
                                   
                self.model_a.setQuery(query1)



            # self.model_a.setTable("us_table")
            # self.model_a.setEditStrategy(QSqlTableModel.OnManualSubmit)

            # if bool (sito_set_str):
                # filter_str = "sito = '{}'".format(str(self.comboBox_sito.currentText()))
                # self.model_a.setFilter(filter_str)
                # self.model_a.select()
            # else:

                # self.model_a.select()
            self.tableView_summary.clearSpans()
        else:

            db = QSqlDatabase.addDatabase("QPSQL")
            db.setHostName(conn_host["host"])

            db.setDatabaseName(conn_sqlite["db_name"])
            db.setPort(int(port_int))
            db.setUserName(conn_user['user'])
            db.setPassword(conn_password['password'])
            db.open()



            self.model_a = QSqlQueryModel()

            self.tableView_summary.setModel(self.model_a)
            if bool(self.comboBox_sito.currentText()):
                query = QSqlQuery("select distinct  a.sito as Sito ,count(distinct a.id_us) as US,count(distinct "
                                  "c.id_struttura)as Struttura,count(distinct d.id_tomba) as Tombe from us_table "
                                  "as a left join struttura_table as c on a.sito=c.sito left join tomba_table as "
                                  "d on a.sito=d.sito where a.sito = '{}' group by a.sito order by us DESC ".format(
                    str(self.comboBox_sito.currentText())), db=db)
                self.model_a.setQuery(query)
            else:
                query1 = QSqlQuery("select s.sito as Sito,(select count(distinct id_invmat) from inventario_materiali_table m "
                                   "where s.sito = m.sito) as Materiali,(select count(distinct id_struttura) from "
                                   "struttura_table st where s.sito = st.sito) as Struttura,(select count(distinct "
                                   "id_tomba) from tomba_table t where s.sito = t.sito) as Tombe,"
                                   "(select count(distinct id_us) from us_table ad where s.sito=ad.sito) as US from ("
                                   "select sito , count(distinct id_us) from us_table group by sito) as s order by "
                                   "s.sito;",db=db)
                self.model_a.setQuery(query1)

            self.tableView_summary.clearSpans()
    def db_active (self):
        self.comboBox_Database.update()
        self.comboBox_sito.clear()
        if self.comboBox_Database.currentText() == 'sqlite':
            #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
            self.toolButton_db.setEnabled(True)
            # self.pushButton_upd_postgres.setEnabled(False)
            # self.pushButton_upd_sqlite.setEnabled(True)
        if self.comboBox_Database.currentText() == 'postgres':
            #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
            self.toolButton_db.setEnabled(False)
            # self.pushButton_upd_sqlite.setEnabled(False)
            # self.pushButton_upd_postgres.setEnabled(True)
        self.comboBox_sito.clear()
    def setPathDBsqlite1(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

                self.lineEdit_database_rd.setText(filename)
                s.setValue('',filename)




    def setPathDBsqlite2(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

            self.lineEdit_database_wt.setText(filename)
            s.setValue('',filename)
    def openthumbDir(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

            self.lineEdit_DBname.setText(filename)
            s.setValue('',filename)
    def openresizeDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_resize.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    def setPathDB(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

            self.lineEdit_DBname.setText(filename)
            s.setValue('',filename)

    def setPathThumb(self):
        s = QgsSettings()
        self.thumbpath = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.thumbpath:
            self.lineEdit_Thumb_path.setText(self.thumbpath+"/")
            s.setValue('pyArchInit/thumbpath', self.thumbpath)
    def setPathlogo(self):
        
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            "image (*.*)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:

            self.lineEdit_logo.setText(dbpath)
            s.setValue('',dbpath)
    def setPathResize(self):
        s = QgsSettings()
        self.resizepath = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.resizepath:
            self.lineEdit_Thumb_resize.setText(self.resizepath+"/")
            s.setValue('pyArchInit/risizepath', self.resizepath)


    def setPathGraphviz(self):
        s = QgsSettings()
        self.graphviz_bin = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )

        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)
            s.setValue('pyArchInit/graphvizBinPath', self.graphviz_bin)

    def setPathPostgres(self):
        s = QgsSettings()
        self.postgres_bin = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )

        if self.postgres_bin:
            self.lineEditPostgres.setText(self.postgres_bin)
            s.setValue('pyArchInit/postgresBinPath', self.postgres_bin)


    def setEnvironPath(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.graphviz_bin)

        if self.L=='it':
            QMessageBox.warning(self, "Imposta variabile ambientale", "Il percorso è stato impostato con successo", QMessageBox.Ok)

        elif self.L=='de':
            QMessageBox.warning(self, "Umweltvariable setzen", "Der Weg wurde erfolgreich eingeschlagen", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Set Environmental Variable", "The path has been set successful", QMessageBox.Ok)
    def setEnvironPathPostgres(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.postgres_bin)

        if self.L=='it':
            QMessageBox.warning(self, "Imposta variabile ambientale", "Il percorso è stato impostato con successo", QMessageBox.Ok)

        elif self.L=='de':
            QMessageBox.warning(self, "Umweltvariable setzen", "Der Weg wurde erfolgreich eingeschlagen", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Set Environmental Variable", "The path has been set successful", QMessageBox.Ok)
    def set_db_parameter(self):
        if self.comboBox_Database.currentText() == 'postgres':
            self.lineEdit_DBname.setText("pyarchinit")
            self.lineEdit_Host.setText('127.0.0.1')
            self.lineEdit_Port.setText('5432')
            self.lineEdit_User.setText('postgres')

        if self.comboBox_Database.currentText() == 'sqlite':
            self.lineEdit_DBname.setText("pyarchinit_db.sqlite")
            self.lineEdit_Host.setText('')
            self.lineEdit_Password.setText('')
            self.lineEdit_Port.setText('')
            self.lineEdit_User.setText('')



    def set_db_import_from_parameter(self):
        #QMessageBox.warning(self, "ok", "entered in read.", QMessageBox.Ok)

        if self.comboBox_server_rd.currentText() == 'postgres':
            
            self.lineEdit_host_rd.setText('localhost')
            self.lineEdit_username_rd.setText('postgres')
            self.lineEdit_database_rd.setText('pyarchinit')
            self.lineEdit_port_rd.setText('5432')

        if self.comboBox_server_rd.currentText() == 'sqlite':
            #QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)

            self.lineEdit_host_rd.setText('')
            self.lineEdit_username_rd.setText('')
            self.lineEdit_pass_rd.setText('')
            self.lineEdit_database_rd.setText('pyarchinit_db.sqlite')
            self.lineEdit_port_rd.setText('')


    def set_db_import_to_parameter(self):
        #QMessageBox.warning(self, "ok", "entered in write", QMessageBox.Ok)
        #self.comboBox_server_wt.clear()
        if self.comboBox_server_wt.currentText() == 'postgres' and not self.comboBox_Database.currentText()=='postgres':
            QMessageBox.warning(self, "Attenzione", "Devi essere connesso\n prima al db di postgres", QMessageBox.Ok)
            #self.comboBox_server_wt.clear()
        if self.comboBox_server_wt.currentText() == 'postgres' and self.comboBox_Database.currentText()=='postgres':   
            
            self.lineEdit_host_wt.setText(str(self.lineEdit_Host.text()))
            
            self.lineEdit_database_wt.setText(str(self.lineEdit_DBname.text()))
           
            self.lineEdit_username_wt.setText(str(self.lineEdit_User.text()))
            
            self.lineEdit_port_wt.setText(str(self.lineEdit_Port.text()))
            
            self.lineEdit_pass_wt.setText(str(self.lineEdit_Password.text()))

        
        if self.comboBox_server_wt.currentText() == 'sqlite':   
            #QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            #self.self.comboBox_server_wt.clear()
            self.lineEdit_host_wt.setText('')
            self.lineEdit_username_wt.setText('')
            self.lineEdit_pass_wt.setText('')
            self.lineEdit_database_wt.setText(str(self.lineEdit_DBname.text()))
            self.lineEdit_port_wt.setText('')

    def load_dict(self):
        path_rel = os.path.join(os.sep, str(self.HOME), 'pyarchinit_DB_folder', 'config.cfg')
        conf = open(path_rel, "r")
        data = conf.read()
        self.PARAMS_DICT = eval(data)
        conf.close()

    def save_dict(self):
        # save data into config.cfg file
        path_rel = os.path.join(os.sep, str(self.HOME), 'pyarchinit_DB_folder', 'config.cfg')
        f = open(path_rel, "w")
        f.write(str(self.PARAMS_DICT))
        f.close()

    def on_pushButton_save_pressed(self):
        
        self.comboBox_Database.update()
        try:
            if not bool(self.lineEdit_Password.text()) and str(self.comboBox_Database.currentText())=='postgres':
                QMessageBox.warning(self, "INFO", 'non dimenticarti di inserire la password',QMessageBox.Ok)
            else:
                self.PARAMS_DICT['SERVER'] = str(self.comboBox_Database.currentText())
                self.PARAMS_DICT['HOST'] = str(self.lineEdit_Host.text())
                self.PARAMS_DICT['DATABASE'] = str(self.lineEdit_DBname.text())
                self.PARAMS_DICT['PASSWORD'] = str(self.lineEdit_Password.text())
                self.PARAMS_DICT['PORT'] = str(self.lineEdit_Port.text())
                self.PARAMS_DICT['USER'] = str(self.lineEdit_User.text())
                self.PARAMS_DICT['THUMB_PATH'] = str(self.lineEdit_Thumb_path.text())
                self.PARAMS_DICT['THUMB_RESIZE'] = str(self.lineEdit_Thumb_resize.text())
                self.PARAMS_DICT['EXPERIMENTAL'] = str(self.comboBox_experimental.currentText())
                self.PARAMS_DICT['SITE_SET'] = str(self.comboBox_sito.currentText())
                self.PARAMS_DICT['LOGO'] = str(self.lineEdit_logo.text())
                self.save_dict()

                if str(self.comboBox_Database.currentText())=='postgres':


                    b=str(self.select_version_sql())

                    a = "90313"

                    if a == b:
                        link = 'https://www.postgresql.org/download/'
                        if self.L=='it':
                            msg =   "Stai utilizzando la versione di Postgres: " + str(b)+". Tale versione è diventata obsoleta e potresti riscontrare degli errori. Aggiorna PostgreSQL ad una versione più recente. <br><a href='%s'>PostgreSQL</a>" %link
                        if self.L=='de':
                            msg =   "Sie benutzen die Postgres-Version: " + str(b)+". Diese Version ist veraltet, und Sie werden möglicherweise einige Fehler finden. Aktualisieren Sie PostgreSQL auf eine neuere Version. <br><a href='%s'>PostgreSQL</a>" %link
                        else:
                            msg = "You are using the Postgres version: " + str(b)+". This version has become obsolete and you may find some errors. Update PostgreSQL to a newer version. <br><a href='%s'>PostgreSQL</a>" %link
                        QMessageBox.information(self, "INFO", msg,QMessageBox.Ok)
                    else:
                        pass
                else:
                    pass


                self.try_connection()

        except Exception as e:
            if self.L=='it':
                QMessageBox.warning(self, "INFO", "Problema di connessione al db. Controlla i paramatri inseriti", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "INFO", "Db-Verbindungsproblem. Überprüfen Sie die eingegebenen Parameter", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "INFO", "Db connection problem. Check the parameters inserted", QMessageBox.Ok)
    def compare(self):
        if self.comboBox_server_wt.currentText() == 'sqlite':

            if platform.system() == "Windows":
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'sqldiff.exe')
            elif platform.system() == "Darwin":
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'sqldiff_osx')
            else:
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'sqldiff_linux')

            db1 = os.path.join(os.sep, self.HOME, 'bin', 'pyarchinit.sqlite')
            db2 = os.path.join(os.sep, self.HOME, 'pyarchinit_DB_folder', self.lineEdit_DBname.text())

            # text_ = cmd, self.comboBox_compare.currentText(), db1 + ' ', db2
            # result = subprocess.check_output([text_], stderr=subprocess.STDOUT)
            os.system("start cmd /k" + cmd + ' ' + self.comboBox_compare.currentText() + ' ' + db1 + ' ' + db2)
            # if result == b'':
            #
            #     pass
            # else:
            #     QMessageBox.warning(self, "Attenzione",
            #                         "Il db non allineato devi aggiornarlo. Chiudi questa finestra e clicca il bottone con l'icona di spatialite in basso a sinistra aggiungendo l'epsg del tuo db",
            #                         QMessageBox.Ok)
            #     # # #break

        else:
            pass

    def on_pushButton_crea_database_pressed(self,):
        schema_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'pyarchinit_schema_clean.sql')
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'create_view.sql')

        if not bool(self.lineEdit_db_passwd.text()):
            QMessageBox.warning(self, "INFO", "Non dimenticarti di inserire la password", QMessageBox.Ok)
        else:

            create_database = CreateDatabase(self.lineEdit_dbname.text(), self.lineEdit_db_host.text(),
                                             self.lineEdit_port_db.text(), self.lineEdit_db_user.text(),
                                             self.lineEdit_db_passwd.text())

            ok, db_url = create_database.createdb()


            if ok:
                try:
                    RestoreSchema(db_url, schema_file).restore_schema()
                except Exception as e:
                    if self.L=='it':
                        QMessageBox.warning(self, "INFO", "Devi essere superutente per creare un db. Vedi l'errore seguente", QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "INFO", "Sie müssen Superuser sein, um eine Db anzulegen. Siehe folgenden Fehler", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "INFO", "You have to be super user to create a db. See the following error", QMessageBox.Ok)
                    DropDatabase(db_url).dropdb()
                    ok = False
                    raise e

            if ok:
                crsid = self.selectorCrsWidget.crs().authid()
                srid = crsid.split(':')[1]

                res = RestoreSchema(db_url).update_geom_srid('public', srid)

                # create views
                RestoreSchema(db_url, view_file).restore_schema()
                #set owner
                if self.lineEdit_db_user.text() != 'postgres':
                    RestoreSchema(db_url).set_owner(self.lineEdit_db_user.text())

            if self.L=='it':
                if ok and res:

                    msg = QMessageBox.warning(self, 'INFO', 'Installazione avvenuta con successo, vuoi connetterti al nuovo DB?',
                                              QMessageBox.Ok | QMessageBox.Cancel)
                    if msg == QMessageBox.Ok:
                        self.comboBox_Database.setCurrentText('postgres')
                        self.lineEdit_Host.setText(self.lineEdit_db_host.text())
                        self.lineEdit_DBname.setText(self.lineEdit_dbname.text())
                        self.lineEdit_Port.setText(self.lineEdit_port_db.text())
                        self.lineEdit_User.setText(self.lineEdit_db_user.text())
                        self.lineEdit_Password.setText(self.lineEdit_db_passwd.text())
                        self.on_pushButton_save_pressed()
                else:
                    QMessageBox.warning(self, "INFO", "Database esistente", QMessageBox.Ok)
            elif self.L=='de':
                if ok and res:
                    msg = QMessageBox.warning(self, 'INFO', 'Erfolgreiche Installation, möchten Sie sich mit der neuen Datenbank verbinden?',
                                              QMessageBox.Ok | QMessageBox.Cancel)
                    if msg == QMessageBox.Ok:
                        self.comboBox_Database.setCurrentText('postgres')
                        self.lineEdit_Host.setText(self.lineEdit_db_host.text())
                        self.lineEdit_DBname.setText(self.lineEdit_dbname.text())
                        self.lineEdit_Port.setText(self.lineEdit_port_db.text())
                        self.lineEdit_User.setText(self.lineEdit_db_user.text())
                        self.lineEdit_Password.setText(self.lineEdit_db_passwd.text())
                        self.on_pushButton_save_pressed()
                else:
                    QMessageBox.warning(self, "INFO", "die Datenbank existiert", QMessageBox.Ok)
            else:
                if ok and res:
                    msg = QMessageBox.warning(self, 'INFO', 'Successful installation, do you want to connect to the new DB?',
                                              QMessageBox.Ok | QMessageBox.Cancel)
                    if msg == QMessageBox.Ok:
                        self.comboBox_Database.setCurrentText('postgres')
                        self.lineEdit_Host.setText(self.lineEdit_db_host.text())
                        self.lineEdit_DBname.setText(self.lineEdit_dbname.text())
                        self.lineEdit_Port.setText(self.lineEdit_port_db.text())
                        self.lineEdit_User.setText(self.lineEdit_db_user.text())
                        self.lineEdit_Password.setText(self.lineEdit_db_passwd.text())
                        self.on_pushButton_save_pressed()
                else:
                    QMessageBox.warning(self, "INFO", "The DB exist already", QMessageBox.Ok)
    def select_version_sql(self):
        conn = Connection()
        db_url = conn.conn_str()
        sql_query_string = "SELECT current_setting('server_version_num')"
        self.engine= create_engine(db_url)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchone()
        vers = ''.join(rows)
        res.close()#QMessageBox.information(self, "INFO", str(vers),QMessageBox.Ok)
        return vers

    def on_pushButton_upd_postgres_pressed(self):
        conn = Connection()
        db_url = conn.conn_str()
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                       'pyarchinit_update_postgres.sql')

        b=str(self.select_version_sql())

        a = "90313"
        if self.L== 'it':
            if a == b:
                QMessageBox.information(self, "INFO", " Non puoi aggiornare il db postgres per chè la tua versione è inferiore alla 9.4 "
                                                                                "Aggiorna ad una versione più recente",QMessageBox.Ok)
            else:
                RestoreSchema(db_url,view_file).restore_schema()

                QMessageBox.information(self, "INFO", "il db è stato aggiornato", QMessageBox.Ok)
        elif self.L== 'de':
            if a == b:
                QMessageBox.information(self, "INFO", " Sie können die db postgres nicht aktualisieren, da Ihre Version niedriger als 9.4 ist. "
                                                                                "Upgrade auf eine neuere Version",QMessageBox.Ok)
            else:
                RestoreSchema(db_url,view_file).restore_schema()

                QMessageBox.information(self, "INFO", "die db wurde aktualisiert", QMessageBox.Ok)
        else:
            if a == b:
                QMessageBox.information(self, "INFO", " You cannot update the db postgres because your version is lower than 9.4 "
                                                                                "Upgrade to a newer version",QMessageBox.Ok)
            else:
                RestoreSchema(db_url,view_file).restore_schema()

                QMessageBox.information(self, "INFO", "the db has been updated", QMessageBox.Ok)



    def load_spatialite(self,dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)

        if Pyarchinit_OS_Utility.isWindows()== True:
            dbapi_conn.load_extension('mod_spatialite.dll')

        elif Pyarchinit_OS_Utility.isMac()== True:
            dbapi_conn.load_extension('mod_spatialite.so')
        else:
            dbapi_conn.load_extension('mod_spatialite.so')

    def on_pushButton_upd_sqlite_pressed(self):


        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        conn = Connection()
        db_url = conn.conn_str()

        try:
            engine = create_engine(db_url, echo=True)

            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
            
            
            py3_usm='''CREATE TABLE IF NOT EXISTS pyarchinit_quote_usm (
                    gid               INTEGER                  NOT NULL
                                                               PRIMARY KEY AUTOINCREMENT,
                    sito_q            TEXT,
                    area_q            INTEGER,
                    us_q              INTEGER,
                    unita_misu_q      TEXT,
                    quota_q           [DOUBLE PRECISION],
                    data              TEXT,
                    disegnatore       TEXT,
                    rilievo_originale TEXT
                );'''
            c.execute(py3_usm)
            
            sql_pyus_geom = """select AddGeometryColumn('pyarchinit_quote_usm', 'the_geom',"""+ self.lineEdit_crs.text()+""" ,'POINT', 'XY');"""
            c.execute(sql_pyus_geom)
            
            sql_pyus_geom_spatial =""" select CreateSpatialIndex('pyarchinit_quote_usm', 'the_geom');"""
            c.execute(sql_pyus_geom_spatial)
                
            
            py8='''DROP VIEW if exists pyarchinit_quote_usm_view;'''
            c.execute(py8)
            py9='''    CREATE VIEW if not exists pyarchinit_quote_usm_view AS
                    SELECT a.rowid AS rowid,
                           a.id_us AS id_us,
                           a.sito AS sito,
                           a.area AS area,
                           a.us AS us,
                           a.d_stratigrafica AS d_stratigrafica,
                           a.d_interpretativa AS d_interpretativa,
                           a.descrizione AS descrizione,
                           a.interpretazione AS interpretazione,
                           a.periodo_iniziale AS periodo_iniziale,
                           a.fase_iniziale AS fase_iniziale,
                           a.periodo_finale AS periodo_finale,
                           a.fase_finale AS fase_finale,
                           a.scavato AS scavato,
                           a.attivita AS attivita,
                           a.anno_scavo AS anno_scavo,
                           a.metodo_di_scavo AS metodo_di_scavo,
                           a.inclusi AS inclusi,
                           a.campioni AS campioni,
                           a.rapporti AS rapporti,
                           a.data_schedatura AS data_schedatura,
                           a.schedatore AS schedatore,
                           a.formazione AS formazione,
                           a.stato_di_conservazione AS stato_di_conservazione,
                           a.colore AS colore,
                           a.consistenza AS consistenza,
                           a.struttura AS struttura,
                           a.cont_per AS cont_per,
                           a.order_layer AS order_layer,
                           a.documentazione AS documentazione,
                           b.rowid AS rowid_1,
                           b.sito_q AS sito_q,
                           b.area_q AS area_q,
                           b.us_q AS us_q,
                           b.unita_misu_q AS unita_misu_q,
                           b.quota_q AS quota_q,
                           b.data AS data,
                           b.disegnatore AS disegnatore,
                           b.rilievo_originale AS rilievo_originale,
                           b.the_geom AS the_geom
                      FROM us_table AS a
                           JOIN
                           pyarchinit_quote_usm AS b ON (a.sito = b.sito_q AND 
                                                     a.area = b.area_q AND 
                                                     a.us = b.us_q) 
                     ORDER BY a.order_layer DESC;'''
            c.execute(py9)
            
            try:
                sql_view_py10= ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('pyarchinit_quote_usm_view', 'the_geom', 'rowid', 'pyarchinit_quote_usm', 'the_geom',0)""")
           
                
                c.execute(sql_view_py10)
            except:
                pass
            
            
            
            py8='''DROP VIEW if exists pyarchinit_quote_view;'''
            c.execute(py8)
            py9='''    CREATE VIEW if not exists pyarchinit_quote_view AS
                    SELECT a.rowid AS rowid,
                           a.id_us AS id_us,
                           a.sito AS sito,
                           a.area AS area,
                           a.us AS us,
                           a.d_stratigrafica AS d_stratigrafica,
                           a.d_interpretativa AS d_interpretativa,
                           a.descrizione AS descrizione,
                           a.interpretazione AS interpretazione,
                           a.periodo_iniziale AS periodo_iniziale,
                           a.fase_iniziale AS fase_iniziale,
                           a.periodo_finale AS periodo_finale,
                           a.fase_finale AS fase_finale,
                           a.scavato AS scavato,
                           a.attivita AS attivita,
                           a.anno_scavo AS anno_scavo,
                           a.metodo_di_scavo AS metodo_di_scavo,
                           a.inclusi AS inclusi,
                           a.campioni AS campioni,
                           a.rapporti AS rapporti,
                           a.data_schedatura AS data_schedatura,
                           a.schedatore AS schedatore,
                           a.formazione AS formazione,
                           a.stato_di_conservazione AS stato_di_conservazione,
                           a.colore AS colore,
                           a.consistenza AS consistenza,
                           a.struttura AS struttura,
                           a.cont_per AS cont_per,
                           a.order_layer AS order_layer,
                           a.documentazione AS documentazione,
                           b.rowid AS rowid_1,
                           b.sito_q AS sito_q,
                           b.area_q AS area_q,
                           b.us_q AS us_q,
                           b.unita_misu_q AS unita_misu_q,
                           b.quota_q AS quota_q,
                           b.data AS data,
                           b.disegnatore AS disegnatore,
                           b.rilievo_originale AS rilievo_originale,
                           b.the_geom AS the_geom
                      FROM us_table AS a
                           JOIN
                           pyarchinit_quote AS b ON (a.sito = b.sito_q AND 
                                                     a.area = b.area_q AND 
                                                     a.us = b.us_q) 
                     ORDER BY a.order_layer DESC;'''
            c.execute(py9)
            
            try:
                sql_view_py10= ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('pyarchinit_quote_view', 'the_geom', 'rowid', 'pyarchinit_quote', 'the_geom',0)""")
           
                
                c.execute(sql_view_py10)
            except:
                pass
            
            
            sql_trigger_coord1="""CREATE TRIGGER IF NOT EXISTS create_geom_insert 
                After insert 
                ON pyunitastratigrafiche 

                BEGIN 
                
                update pyunitastratigrafiche set coord = ST_AsText(ST_Centroid(the_geom)) where scavo_s=New.scavo_s and area_s=New.area_s and us_s=New.us_s; 
                
                END;"""
            c.execute(sql_trigger_coord1)
            
            sql_drop_trigger="""Drop trigger if exists create_geom_update"""
            c.execute(sql_drop_trigger)
            
            
            sql_trigger_coord3="""CREATE TRIGGER IF NOT EXISTS create_geom_update 
                After update 
                ON pyunitastratigrafiche 

                BEGIN 
                
                update pyunitastratigrafiche set coord = ST_AsText(ST_Centroid(the_geom)) where gid = New.gid and scavo_s=New.scavo_s and area_s=New.area_s and us_s=New.us_s;
                
                END;"""
            c.execute(sql_trigger_coord3)
            # ################################################################
            sql_alter_table_us=(
            """CREATE TABLE if not exists pyunitastratigrafiche_usm (
            "gid" integer PRIMARY KEY AUTOINCREMENT,
            "area_s" integer,
            "scavo_s" text,
            "us_s" integer,            
            "stratigraph_index_us" integer,
            "tipo_us_s" text,
            "rilievo_originale" text,
            "disegnatore" text,
            "data" date,
            "tipo_doc" text,
            "nome_doc" text,
            "coord" text); """ )
            c.execute(sql_alter_table_us)
            sql_pyus_geom = """ select AddGeometryColumn('pyunitastratigrafiche_usm', 'the_geom',"""+ self.lineEdit_crs.text()+""" ,'MULTIPOLYGON', 'XY'); """
            c.execute(sql_pyus_geom)
            sql_pyus_geom_spatial =""" select CreateSpatialIndex('pyunitastratigrafiche_usm', 'the_geom');"""
            c.execute(sql_pyus_geom_spatial)
        
        
            py8='''DROP VIEW if exists pyarchinit_usm_view;'''
            c.execute(py8)
            sql_view_us=("""CREATE VIEW  IF NOT EXISTS "pyarchinit_usm_view" AS            
            SELECT "a"."rowid" AS "rowid", "a"."gid" AS "gid", "a"."area_s" AS "area_s",
            "a"."scavo_s" AS "scavo_s", "a"."us_s" AS "us_s",
            "a"."stratigraph_index_us" AS "stratigraph_index_us",
            "a"."tipo_us_s" AS "tipo_us_s", "a"."rilievo_originale" AS "rilievo_originale",
            "a"."disegnatore" AS "disegnatore", "a"."data" AS "data",
            "a"."the_geom" AS "the_geom", "a"."tipo_doc" AS "tipo_doc",
            "a"."nome_doc" AS "nome_doc", "b"."id_us" AS "id_us", "b"."sito" AS "sito", "b"."area" AS "area",
            "b"."us" AS "us", "b"."d_stratigrafica" AS "d_stratigrafica",
            "b"."d_interpretativa" AS "d_interpretativa", "b"."descrizione" AS "descrizione",
            "b"."interpretazione" AS "interpretazione", "b"."periodo_iniziale" AS "periodo_iniziale",
            "b"."fase_iniziale" AS "fase_iniziale", "b"."periodo_finale" AS "periodo_finale",
            "b"."fase_finale" AS "fase_finale", "b"."scavato" AS "scavato",
            "b"."attivita" AS "attivita", "b"."anno_scavo" AS "anno_scavo",
            "b"."metodo_di_scavo" AS "metodo_di_scavo", "b"."inclusi" AS "inclusi",
            "b"."campioni" AS "campioni", "b"."rapporti" AS "rapporti",
            "b"."data_schedatura" AS "data_schedatura", "b"."schedatore" AS "schedatore",
            "b"."formazione" AS "formazione", "b"."stato_di_conservazione" AS "stato_di_conservazione",
            "b"."colore" AS "colore", "b"."consistenza" AS "consistenza",
            "b"."struttura" AS "struttura", "b"."cont_per" AS "cont_per",
            "b"."order_layer" AS "order_layer", "b"."documentazione" AS "documentazione",
            "b"."unita_tipo" AS "unita_tipo", "b"."settore" AS "settore",
            "b"."quad_par" AS "quad_par", "b"."ambient" AS "ambient",
            "b"."saggio" AS "saggio", "b"."elem_datanti" AS "elem_datanti",
            "b"."funz_statica" AS "funz_statica", "b"."lavorazione" AS "lavorazione",
            "b"."spess_giunti" AS "spess_giunti", "b"."letti_posa" AS "letti_posa",
            "b"."alt_mod" AS "alt_mod", "b"."un_ed_riass" AS "un_ed_riass",
            "b"."reimp" AS "reimp", "b"."posa_opera" AS "posa_opera",
            "b"."quota_min_usm" AS "quota_min_usm", "b"."quota_max_usm" AS "quota_max_usm",
            "b"."cons_legante" AS "cons_legante", "b"."col_legante" AS "col_legante",
            "b"."aggreg_legante" AS "aggreg_legante", "b"."con_text_mat" AS "con_text_mat",
            "b"."col_materiale" AS "col_materiale", "b"."inclusi_materiali_usm" AS "inclusi_materiali_usm",
            "b"."n_catalogo_generale" AS "n_catalogo_generale",
            "b"."n_catalogo_interno" AS "n_catalogo_interno",
            "b"."n_catalogo_internazionale" AS "n_catalogo_internazionale",
            "b"."soprintendenza" AS "soprintendenza", "b"."quota_relativa" AS "quota_relativa",
            "b"."quota_abs" AS "quota_abs", "b"."ref_tm" AS "ref_tm",
            "b"."ref_ra" AS "ref_ra", "b"."ref_n" AS "ref_n",
            "b"."posizione" AS "posizione", "b"."criteri_distinzione" AS "criteri_distinzione",
            "b"."modo_formazione" AS "modo_formazione", "b"."componenti_organici" AS "componenti_organici",
            "b"."componenti_inorganici" AS "componenti_inorganici",
            "b"."lunghezza_max" AS "lunghezza_max", "b"."altezza_max" AS "altezza_max",
            "b"."altezza_min" AS "altezza_min", "b"."profondita_max" AS "profondita_max",
            "b"."profondita_min" AS "profondita_min", "b"."larghezza_media" AS "larghezza_media",
            "b"."quota_max_abs" AS "quota_max_abs", "b"."quota_max_rel" AS "quota_max_rel",
            "b"."quota_min_abs" AS "quota_min_abs", "b"."quota_min_rel" AS "quota_min_rel",
            "b"."osservazioni" AS "osservazioni", "b"."datazione" AS "datazione",
            "b"."flottazione" AS "flottazione", "b"."setacciatura" AS "setacciatura",
            "b"."affidabilita" AS "affidabilita", "b"."direttore_us" AS "direttore_us",
            "b"."responsabile_us" AS "responsabile_us", "b"."cod_ente_schedatore" AS "cod_ente_schedatore",
            "b"."data_rilevazione" AS "data_rilevazione", "b"."data_rielaborazione" AS "data_rielaborazione",
            "b"."lunghezza_usm" AS "lunghezza_usm", "b"."altezza_usm" AS "altezza_usm",
            "b"."spessore_usm" AS "spessore_usm", "b"."tecnica_muraria_usm" AS "tecnica_muraria_usm",
            "b"."modulo_usm" AS "modulo_usm", "b"."campioni_malta_usm" AS "campioni_malta_usm",
            "b"."campioni_mattone_usm" AS "campioni_mattone_usm",
            "b"."campioni_pietra_usm" AS "campioni_pietra_usm",
            "b"."provenienza_materiali_usm" AS "provenienza_materiali_usm",
            "b"."criteri_distinzione_usm" AS "criteri_distinzione_usm",
            "b"."uso_primario_usm" AS "uso_primario_usm"
            FROM "pyunitastratigrafiche_usm" AS "a"
            JOIN "us_table" AS "b" ON ("a"."area_s" = "b"."area" AND "a"."scavo_s" = "b"."sito"
            AND "a"."us_s" = "b"."us")
            ORDER BY "b"."order_layer" asc ;""")


            c.execute(sql_view_us)
            try:
                sql_view_us_geom= """INSERT OR REPLACE INTO views_geometry_columns
                        (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                        VALUES ('pyarchinit_usm_view', 'the_geom', 'rowid', 'pyunitastratigrafiche_usm', 'the_geom',0)"""
                c.execute(sql_view_us_geom)
            except:
                pass
            py8='''DROP VIEW if exists pyarchinit_us_view;'''
            c.execute(py8)
            sql_view_us=("""CREATE VIEW  IF NOT EXISTS "pyarchinit_us_view" AS            
            SELECT "a"."rowid" AS "rowid", "a"."gid" AS "gid", "a"."area_s" AS "area_s",
            "a"."scavo_s" AS "scavo_s", "a"."us_s" AS "us_s",
            "a"."stratigraph_index_us" AS "stratigraph_index_us",
            "a"."tipo_us_s" AS "tipo_us_s", "a"."rilievo_originale" AS "rilievo_originale",
            "a"."disegnatore" AS "disegnatore", "a"."data" AS "data",
            "a"."the_geom" AS "the_geom", "a"."tipo_doc" AS "tipo_doc",
            "a"."nome_doc" AS "nome_doc", "b"."id_us" AS "id_us", "b"."sito" AS "sito", "b"."area" AS "area",
            "b"."us" AS "us", "b"."d_stratigrafica" AS "d_stratigrafica",
            "b"."d_interpretativa" AS "d_interpretativa", "b"."descrizione" AS "descrizione",
            "b"."interpretazione" AS "interpretazione", "b"."periodo_iniziale" AS "periodo_iniziale",
            "b"."fase_iniziale" AS "fase_iniziale", "b"."periodo_finale" AS "periodo_finale",
            "b"."fase_finale" AS "fase_finale", "b"."scavato" AS "scavato",
            "b"."attivita" AS "attivita", "b"."anno_scavo" AS "anno_scavo",
            "b"."metodo_di_scavo" AS "metodo_di_scavo", "b"."inclusi" AS "inclusi",
            "b"."campioni" AS "campioni", "b"."rapporti" AS "rapporti",
            "b"."data_schedatura" AS "data_schedatura", "b"."schedatore" AS "schedatore",
            "b"."formazione" AS "formazione", "b"."stato_di_conservazione" AS "stato_di_conservazione",
            "b"."colore" AS "colore", "b"."consistenza" AS "consistenza",
            "b"."struttura" AS "struttura", "b"."cont_per" AS "cont_per",
            "b"."order_layer" AS "order_layer", "b"."documentazione" AS "documentazione",
            "b"."unita_tipo" AS "unita_tipo", "b"."settore" AS "settore",
            "b"."quad_par" AS "quad_par", "b"."ambient" AS "ambient",
            "b"."saggio" AS "saggio", "b"."elem_datanti" AS "elem_datanti",
            "b"."funz_statica" AS "funz_statica", "b"."lavorazione" AS "lavorazione",
            "b"."spess_giunti" AS "spess_giunti", "b"."letti_posa" AS "letti_posa",
            "b"."alt_mod" AS "alt_mod", "b"."un_ed_riass" AS "un_ed_riass",
            "b"."reimp" AS "reimp", "b"."posa_opera" AS "posa_opera",
            "b"."quota_min_usm" AS "quota_min_usm", "b"."quota_max_usm" AS "quota_max_usm",
            "b"."cons_legante" AS "cons_legante", "b"."col_legante" AS "col_legante",
            "b"."aggreg_legante" AS "aggreg_legante", "b"."con_text_mat" AS "con_text_mat",
            "b"."col_materiale" AS "col_materiale", "b"."inclusi_materiali_usm" AS "inclusi_materiali_usm",
            "b"."n_catalogo_generale" AS "n_catalogo_generale",
            "b"."n_catalogo_interno" AS "n_catalogo_interno",
            "b"."n_catalogo_internazionale" AS "n_catalogo_internazionale",
            "b"."soprintendenza" AS "soprintendenza", "b"."quota_relativa" AS "quota_relativa",
            "b"."quota_abs" AS "quota_abs", "b"."ref_tm" AS "ref_tm",
            "b"."ref_ra" AS "ref_ra", "b"."ref_n" AS "ref_n",
            "b"."posizione" AS "posizione", "b"."criteri_distinzione" AS "criteri_distinzione",
            "b"."modo_formazione" AS "modo_formazione", "b"."componenti_organici" AS "componenti_organici",
            "b"."componenti_inorganici" AS "componenti_inorganici",
            "b"."lunghezza_max" AS "lunghezza_max", "b"."altezza_max" AS "altezza_max",
            "b"."altezza_min" AS "altezza_min", "b"."profondita_max" AS "profondita_max",
            "b"."profondita_min" AS "profondita_min", "b"."larghezza_media" AS "larghezza_media",
            "b"."quota_max_abs" AS "quota_max_abs", "b"."quota_max_rel" AS "quota_max_rel",
            "b"."quota_min_abs" AS "quota_min_abs", "b"."quota_min_rel" AS "quota_min_rel",
            "b"."osservazioni" AS "osservazioni", "b"."datazione" AS "datazione",
            "b"."flottazione" AS "flottazione", "b"."setacciatura" AS "setacciatura",
            "b"."affidabilita" AS "affidabilita", "b"."direttore_us" AS "direttore_us",
            "b"."responsabile_us" AS "responsabile_us", "b"."cod_ente_schedatore" AS "cod_ente_schedatore",
            "b"."data_rilevazione" AS "data_rilevazione", "b"."data_rielaborazione" AS "data_rielaborazione",
            "b"."lunghezza_usm" AS "lunghezza_usm", "b"."altezza_usm" AS "altezza_usm",
            "b"."spessore_usm" AS "spessore_usm", "b"."tecnica_muraria_usm" AS "tecnica_muraria_usm",
            "b"."modulo_usm" AS "modulo_usm", "b"."campioni_malta_usm" AS "campioni_malta_usm",
            "b"."campioni_mattone_usm" AS "campioni_mattone_usm",
            "b"."campioni_pietra_usm" AS "campioni_pietra_usm",
            "b"."provenienza_materiali_usm" AS "provenienza_materiali_usm",
            "b"."criteri_distinzione_usm" AS "criteri_distinzione_usm",
            "b"."uso_primario_usm" AS "uso_primario_usm"
            FROM "pyunitastratigrafiche" AS "a"
            JOIN "us_table" AS "b" ON ("a"."area_s" = "b"."area" AND "a"."scavo_s" = "b"."sito"
            AND "a"."us_s" = "b"."us")
            ORDER BY "b"."order_layer" asc ;""")


            c.execute(sql_view_us)
            try:
                sql_view_us_geom= """INSERT OR REPLACE INTO views_geometry_columns
                        (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                        VALUES ('pyarchinit_us_view', 'the_geom', 'rowid', 'pyunitastratigrafiche', 'the_geom',0)"""
                c.execute(sql_view_us_geom)
            except:
                pass
            RestoreSchema(db_url,None).update_geom_srid_sl('%d' % int(self.lineEdit_crs.text()))
            c.close()
            QMessageBox.warning(self, "Message", "Update Done", QMessageBox.Ok)



        except Exception as e:
            QMessageBox.warning(self, "Update error", str(e), QMessageBox.Ok)



    def on_pushButton_crea_database_sl_pressed(self):


        db_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'pyarchinit.sqlite')

        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        ok = False
        if not os.path.exists(db_path):
            Pyarchinit_OS_Utility().copy_file(db_file, db_path)
            ok = True

        if ok:
            crsid = self.selectorCrsWidget_sl.crs().authid()
            srid = crsid.split(':')[1]

            db_url = 'sqlite:///{}'.format(db_path)
            res = RestoreSchema(db_url).update_geom_srid_sl(srid)

        if ok and res:
            if self.L=='it':
                msg = QMessageBox.warning(self, 'INFO', 'Installazione avvenuta con successo, vuoi connetterti al nuovo DB?', QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Ok:
                    self.comboBox_Database.setCurrentText('sqlite')
                    self.lineEdit_DBname.setText(sl_name)
                    self.on_pushButton_save_pressed()

            elif self.L=='de':
                msg = QMessageBox.warning(self, 'INFO', 'Erfolgreiche Installation, möchten Sie sich mit der neuen Datenbank verbinden?', QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Ok:
                    self.comboBox_Database.setCurrentText('sqlite')
                    self.lineEdit_DBname.setText(sl_name)
                    self.on_pushButton_save_pressed()
            else:
                msg = QMessageBox.warning(self, 'INFO', 'Successful installation, do you want to connect to the new DB?', QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Ok:
                    self.comboBox_Database.setCurrentText('sqlite')
                    self.lineEdit_DBname.setText(sl_name)
                    self.on_pushButton_save_pressed()
        else:
            if self.L=='it':
                QMessageBox.warning(self, "INFO", "Database esistente", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "INFO", "die Datenbank existiert", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "INFO", "The Database exsist already", QMessageBox.Ok)





    def try_connection(self):
        self.summary()
        
        conn = Connection()
        conn_str = conn.conn_str()

        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        test = self.DB_MANAGER.connection()

        if self.L=='it':
            if test:
                QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
            else:
                self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)
        elif self.L=='de':
            if test:
                QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
            else:
                self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)

        else:
            if test:
                QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
            else:
                self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)
    def charge_data(self):
        # load data from config.cfg file
        
            
        self.comboBox_Database.setCurrentText(self.PARAMS_DICT['SERVER'])
        self.lineEdit_Host.setText(self.PARAMS_DICT['HOST'])
        self.lineEdit_DBname.setText(self.PARAMS_DICT['DATABASE'])
        self.lineEdit_Password.setText(self.PARAMS_DICT['PASSWORD'])
        self.lineEdit_Port.setText(self.PARAMS_DICT['PORT'])
        self.lineEdit_User.setText(self.PARAMS_DICT['USER'])
        self.lineEdit_Thumb_path.setText(self.PARAMS_DICT['THUMB_PATH'])
        self.lineEdit_Thumb_resize.setText(self.PARAMS_DICT['THUMB_RESIZE'])
        
        try:
            self.comboBox_experimental.setEditText(self.PARAMS_DICT['EXPERIMENTAL'])
        except:
            self.comboBox_experimental.setEditText("No")
        self.comboBox_sito.setCurrentText(self.PARAMS_DICT['SITE_SET'])    ###############
        self.lineEdit_logo.setText(self.PARAMS_DICT['LOGO'])
    def test_def(self):
        pass

    def on_toolButton_active_toggled(self):
        if self.L=='it':
            if self.toolButton_active.isChecked():
                
                QMessageBox.information(self, "Pyarchinit", "Sistema query attivato. Seleziona un sito e clicca su salva parametri", QMessageBox.Ok)
                self.charge_list()
            else:
                self.comboBox_sito.clear()
                QMessageBox.information(self, "Pyarchinit", "Sistema query disattivato", QMessageBox.Ok)
        elif self.L=='de':
            if self.toolButton_active.isChecked():
                QMessageBox.information(self, "Pyarchinit", "Abfragesystem aktiviert. Wählen Sie einen Standort und klicken Sie auf Parameter speichern", QMessageBox.Ok)
                self.charge_list()
            else:
                self.comboBox_sito.clear()
                QMessageBox.information(self, "Pyarchinit", "Abfragesystem deaktiviert", QMessageBox.Ok)

        else:
            if self.toolButton_active.isChecked():
                QMessageBox.information(self, "Pyarchinit", "Query system activated. Select a site and click on save parameters", QMessageBox.Ok)
                self.charge_list()
            else:
                self.comboBox_sito.clear()
                QMessageBox.information(self, "Pyarchinit", "Query system deactivated", QMessageBox.Ok)
    def charge_list(self):

        self.try_connection()
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)
    
            
    def on_pushButton_import_geometry_pressed(self):
        
        if self.L=='it':

            msg = QMessageBox.warning(self, "Attenzione", "Il sistema aggiornerà le geometrie con i dati importati. Schiaccia Annulla per abortire altrimenti schiaccia Ok per contiunuare." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        elif self.L=='de':

            msg = QMessageBox.warning(self, "Warning", "Das System wird die Geometrien mit den importierten Daten aktualisieren. Drücken Sie Abbrechen, um abzubrechen, oder drücken Sie Ok, um fortzufahren." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        else:

            msg = QMessageBox.warning(self, "Warnung", "The system will update the geometries with the imported data. Press Cancel to abort otherwise press Ok to contiunue." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        if msg == QMessageBox.Cancel:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Azione annullata" ,  QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Aktion abgebrochen" ,  QMessageBox.Ok)

            else:
                QMessageBox.warning(self, "Warning", "Action aborted" ,  QMessageBox.Ok)
        else:
            
            id_table_class_mapper_conv_dict = {
                'PYSITO_POINT': 'gid',
                'PYSITO_POLYGON':'gid',
                'PYUS':'gid',
                'PYQUOTE':'gid',
                'PYUSM':'gid',
                'PYQUOTEUSM':'gid',
                'PYUS_NEGATIVE':'gid',
                'PYSTRUTTURE':'gid',
                'PYREPERTI':'gid',
                'PYINDIVIDUI':'gid' ,
                'PYCAMPIONI':'gid',
                'PYTOMBA':'gid',
                'PYDOCUMENTAZIONE':'gid' ,
                'PYLINEERIFERIMENTO':'gid',
                'PYRIPARTIZIONI_SPAZIALI':'gid',
                'PYSEZIONI':'gid'}
           
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_read = {
                "server": str(self.comboBox_server_rd.currentText()),
                "user": str(self.lineEdit_username_rd.text()),
                "password": str(self.lineEdit_pass_rd.text()),
                "host": str(self.lineEdit_host_rd.text()),
                "port": str(self.lineEdit_port_rd.text()),
                "db_name": str(self.lineEdit_database_rd.text())
            }
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_read["server"] == 'postgres':
                try:
                    conn_str_read = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"], "?sslmode=allow")
                except:
                    conn_str_read = "%s://%s:%s@%s:%d/%s" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"])
            elif conn_str_dict_read["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_read["db_name"]
                conn_str_read = "%s:///%s" % (conn_str_dict_read["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_read["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE
            self.DB_MANAGER_read = Pyarchinit_db_management(conn_str_read)
            test = self.DB_MANAGER_read.connection()
            if test:
                QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "Connection error: <br>", QMessageBox.Cancel)

            ####LEGGE I RECORD IN BASE AL PARAMETRO CAMPO=VALORE
            search_dict = {
                self.mFeature_field_rd.currentText(): "'" + str(self.mFeature_value_rd.currentText()) + "'"
            }
            mapper_class_read = str(self.comboBox_geometry_read.currentText())
            res_read = self.DB_MANAGER_read.query_bool(search_dict, mapper_class_read)
            ####INSERISCE I DATI DA UPLOADARE DENTRO ALLA LISTA DATA_LIST_TOIMP
            data_list_toimp = []
            for i in res_read:
                data_list_toimp.append(i)
            QMessageBox.warning(self, "Total record to import", str(len(data_list_toimp)), QMessageBox.Ok)
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_write = {
                "server": str(self.comboBox_server_wt.currentText()),
                "user": str(self.lineEdit_username_wt.text()),
                "password": str(self.lineEdit_pass_wt.text()),
                "host": str(self.lineEdit_host_wt.text()),
                "port": str(self.lineEdit_port_wt.text()),
                "db_name": str(self.lineEdit_database_wt.text())
            }
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_write["server"] == 'postgres':
                try:
                    conn_str_write = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                        "postgresql", conn_str_dict_writed["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"], conn_str_dict_write["port"], conn_str_dict_write["db_name"],
                        "?sslmode=allow")
                except:
                    conn_str_write = "%s://%s:%s@%s:%d/%s" % (
                        "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"],
                        int(conn_str_dict_write["port"]), conn_str_dict_write["db_name"])
            elif conn_str_dict_write["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\pyarchinit_san_marco\\" fare modifiche anche in pyarchinit_pyqgis
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_write["db_name"]
                conn_str_write = "%s:///%s" % (conn_str_dict_write["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_write["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE IN SCRITTURA
            self.DB_MANAGER_write = Pyarchinit_db_management(conn_str_write)
            test = self.DB_MANAGER_write.connection()
            test = str(test)
            mapper_class_write = str(self.comboBox_geometry_read.currentText())
            ####inserisce i dati dentro al database
            ####PYUNITASTRATIGRAFICHE TABLE
            if mapper_class_write == 'PYUS' :
                for sing_rec in range(len(data_list_toimp)):
                    
                    try:
                        data = self.DB_MANAGER_write.insert_pyus(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            
                            
                            data_list_toimp[sing_rec].area_s,
                            data_list_toimp[sing_rec].scavo_s,
                            data_list_toimp[sing_rec].us_s,
                            data_list_toimp[sing_rec].stratigraph_index_us,
                            data_list_toimp[sing_rec].tipo_us_s,
                            data_list_toimp[sing_rec].rilievo_originale,
                            data_list_toimp[sing_rec].disegnatore,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].coord,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_s)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYUSM' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyusm(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].area_s,
                            data_list_toimp[sing_rec].scavo_s,
                            data_list_toimp[sing_rec].us_s,
                            data_list_toimp[sing_rec].stratigraph_index_us,
                            data_list_toimp[sing_rec].tipo_us_s,
                            data_list_toimp[sing_rec].rilievo_originale,
                            data_list_toimp[sing_rec].disegnatore,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].coord,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_s)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            
            elif mapper_class_write == 'PYSITO_POINT' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pysito_point(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_nome,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYSITO_POLYGON' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pysito_polygon(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_id,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYQUOTE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyquote(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_q,
                            data_list_toimp[sing_rec].area_q ,
                            data_list_toimp[sing_rec].us_q ,
                            data_list_toimp[sing_rec].unita_misu_q ,
                            data_list_toimp[sing_rec].quota_q ,
                            data_list_toimp[sing_rec].data ,
                            data_list_toimp[sing_rec].disegnatore ,
                            data_list_toimp[sing_rec].rilievo_originale ,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_q)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYQUOTEUSM' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyquote_usm(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_q,
                            data_list_toimp[sing_rec].area_q ,
                            data_list_toimp[sing_rec].us_q ,
                            data_list_toimp[sing_rec].unita_misu_q ,
                            data_list_toimp[sing_rec].quota_q ,
                            data_list_toimp[sing_rec].data ,
                            data_list_toimp[sing_rec].disegnatore ,
                            data_list_toimp[sing_rec].rilievo_originale ,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_q)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            
            elif mapper_class_write == 'PYUS_NEGATIVE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyus_negative(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_n ,
                            data_list_toimp[sing_rec].area_n ,
                            data_list_toimp[sing_rec].us_n ,
                            data_list_toimp[sing_rec].tipo_doc_n ,
                            data_list_toimp[sing_rec].nome_doc_n,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYSTRUTTURE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pystrutture(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito ,
                            data_list_toimp[sing_rec].id_strutt ,
                            data_list_toimp[sing_rec].per_iniz,
                            data_list_toimp[sing_rec].per_fin ,
                            data_list_toimp[sing_rec].dataz_ext ,
                            data_list_toimp[sing_rec].fase_iniz,
                            data_list_toimp[sing_rec].fase_fin ,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].the_geom ,
                            data_list_toimp[sing_rec].sigla_strut,
                            data_list_toimp[sing_rec].nr_strut)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYREPERTI' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyreperti(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_rep ,
                            data_list_toimp[sing_rec].siti ,
                            data_list_toimp[sing_rec].link ,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYINDIVIDUI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyindividui(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].sigla_struttura,
                            data_list_toimp[sing_rec].note,
                            data_list_toimp[sing_rec].id_individuo,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYCAMPIONI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pycampioni(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_campion,
                            data_list_toimp[sing_rec].sito,
                            # data_list_toimp[sing_rec].tipo_camp ,
                            # data_list_toimp[sing_rec].dataz ,
                            # data_list_toimp[sing_rec].cronologia ,
                            # data_list_toimp[sing_rec].link_immag,
                            data_list_toimp[sing_rec].sigla_camp ,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYTOMBA':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pytomba(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nr_scheda,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYDOCUMENTAZIONE':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pydocumentazione(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].path_qgis_pj,
                            data_list_toimp[sing_rec].geom,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYLINEERIFERIMENTO':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pylineeriferimento(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].definizion ,
                            data_list_toimp[sing_rec].descrizion,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYRIPARTIZIONI_SPAZIALI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyripartizioni_spaziali(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_rs,
                            data_list_toimp[sing_rec].sito_rs,
                            data_list_toimp[sing_rec].tip_rip,
                            data_list_toimp[sing_rec].descr_rs,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYSEZIONI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pysezioni(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_sezione,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].descr,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].nome_doc)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except AssertionError as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")



    def on_pushButton_import_pressed(self):
        if self.L=='it':

            msg = QMessageBox.warning(self, "Attenzione", "Il sistema aggiornerà le tabelle con i dati importati. Schiaccia Annulla per abortire altrimenti schiaccia Ok per contiunuare." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        elif self.L=='de':

            msg = QMessageBox.warning(self, "Warning", "Das System wird die tabellarisch mit den importierten Daten aktualisieren. Drücken Sie Abbrechen, um abzubrechen, oder drücken Sie Ok, um fortzufahren." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        else:

            msg = QMessageBox.warning(self, "Warnung", "The system will update the tables with the imported data. Press Cancel to abort otherwise press Ok to contiunue." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        if msg == QMessageBox.Cancel:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Azione annullata" ,  QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Aktion abgebrochen" ,  QMessageBox.Ok)

            else:
                QMessageBox.warning(self, "Warning", "Action aborted" ,  QMessageBox.Ok)

        else:
            if self.L=='it':
                id_table_class_mapper_conv_dict = {
                    'SITE':'id_sito',
                    'US': 'id_us',
                    'UT': 'id_ut',
                    'PERIODIZZAZIONE': 'id_perfas',
                    'INVENTARIO_MATERIALI': 'id_invmat',
                    'STRUTTURA': 'id_struttura',
                    'TOMBA': 'id_tomba',
                    'SCHEDAIND': 'id_scheda_ind',
                    'CAMPIONI': 'id_campione',
                    'DOCUMENTAZIONE': 'id_documentazione',
                    'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle',
                    'MEDIA': 'id_media',
                    'MEDIA_THUMB': 'id_media_thumb',
                    'MEDIATOENTITY':'id_mediaToEntity',
                    #'ALL':''

                }
            elif self.L=='de':
                id_table_class_mapper_conv_dict = {
                    'SE': 'id_us',
                    'TE': 'id_ut',
                    'AUSGRABUNGSSTÄTTE': 'id_sito',
                    'PERIODISIERUNG': 'id_perfas',
                    'ARTEFAKT-INVENTAR': 'id_invmat',
                    'STRUKTUREN': 'id_struttura',
                    'TAPHONOMIE': 'id_tomba',
                    'INDIVIDUEL': 'id_scheda_ind',
                    'BEISPIELS': 'id_campione',
                    'DOKUMENTATION': 'id_documentazione',
                    'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle',
                    'MEDIA': 'id_media',
                    'MEDIA_THUMB': 'id_media_thumb',
                    'MEDIATOENTITY':'id_mediaToEntity'
                }
            else:
                id_table_class_mapper_conv_dict = {
                    'SU': 'id_us',
                    'TU': 'id_ut',
                    'SITE': 'id_sito',
                    'PERIODIATION': 'id_perfas',
                    'ARTEFACT': 'id_invmat',
                    'STRUCTURE': 'id_struttura',
                    'TAPHONOMY': 'id_tomba',
                    'INDIVIDUAL': 'id_scheda_ind',
                    'SAMPLE': 'id_campione',
                    'DOCUMENTATION': 'id_documentazione',
                    'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle',
                    'MEDIA': 'id_media',
                    'MEDIA_THUMB': 'id_media_thumb',
                    'MEDIATOENTITY':'id_mediaToEntity'
                }
            # creazione del cursore di lettura
            """if os.name == 'posix':
                home = os.environ['HOME']
            elif os.name == 'nt':
                home = os.environ['HOMEPATH']"""
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_read = {
                "server": str(self.comboBox_server_rd.currentText()),
                "user": str(self.lineEdit_username_rd.text()),
                "password": str(self.lineEdit_pass_rd.text()),
                "host": str(self.lineEdit_host_rd.text()),
                "port": str(self.lineEdit_port_rd.text()),
                "db_name": str(self.lineEdit_database_rd.text())
            }
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_read["server"] == 'postgres':

                try:
                    conn_str_read = "%s://%s:%s@%s:%s/%s%s" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"], "?sslmode=allow")
                except:
                    conn_str_read = "%s://%s:%s@%s:%d/%s" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"])



            elif conn_str_dict_read["server"] == 'sqlite':

                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\pyarchinit_san_marco\\" fare modifiche anche in pyarchinit_pyqgis
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_read["db_name"]
                conn_str_read = "%s:///%s" % (conn_str_dict_read["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_read["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE
            self.DB_MANAGER_read = Pyarchinit_db_management(conn_str_read)

            test = self.DB_MANAGER_read.connection()

            if test:
                QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "Connection error: <br>", QMessageBox.Cancel)
            """elif test.find("create_engine") != -1:
                #QMessageBox.warning(self, "Alert",
                                    "Try connection parameter. <br> If they are correct restart QGIS",
                                    QMessageBox.Ok)"""


            ####LEGGE I RECORD IN BASE AL PARAMETRO CAMPO=VALORE
            search_dict = {
                self.mFeature_field_rd.currentText(): "'" + str(self.mFeature_value_rd.currentText()) + "'"
            }
            mapper_class_read = str(self.comboBox_mapper_read.currentText())
            res_read = self.DB_MANAGER_read.query_bool(search_dict, mapper_class_read)

            ####INSERISCE I DATI DA UPLOADARE DENTRO ALLA LISTA DATA_LIST_TOIMP
            data_list_toimp = []
            for i in res_read:
                data_list_toimp.append(i)

            QMessageBox.warning(self, "Total record to import", str(len(data_list_toimp)), QMessageBox.Ok)

            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_write = {
                "server": str(self.comboBox_server_wt.currentText()),
                "user": str(self.lineEdit_username_wt.text()),
                "password": str(self.lineEdit_pass_wt.text()),
                "host": str(self.lineEdit_host_wt.text()),
                "port": str(self.lineEdit_port_wt.text()),
                "db_name": str(self.lineEdit_database_wt.text())
            }

            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_write["server"] == 'postgres':
                try:
                    conn_str_write = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                        "postgresql", conn_str_dict_writed["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"], conn_str_dict_write["port"], conn_str_dict_write["db_name"],
                        "?sslmode=allow")
                except:
                    conn_str_write = "%s://%s:%s@%s:%d/%s" % (
                        "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"],
                        int(conn_str_dict_write["port"]), conn_str_dict_write["db_name"])
            elif conn_str_dict_write["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\pyarchinit_san_marco\\" fare modifiche anche in pyarchinit_pyqgis
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_write["db_name"]
                conn_str_write = "%s:///%s" % (conn_str_dict_write["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_write["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE IN SCRITTURA

            self.DB_MANAGER_write = Pyarchinit_db_management(conn_str_write)
            test = self.DB_MANAGER_write.connection()
            test = str(test)



            mapper_class_write = str(self.comboBox_mapper_read.currentText())



            ####inserisce i dati dentro al database

            ####SITE TABLE
            if mapper_class_write == 'SITE' :

                for sing_rec in range(len(data_list_toimp)):

                    try:
                        data = self.DB_MANAGER_write.insert_site_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nazione,
                            data_list_toimp[sing_rec].regione,
                            data_list_toimp[sing_rec].comune,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].provincia,
                            data_list_toimp[sing_rec].definizione_sito,
                            data_list_toimp[sing_rec].sito_path,
                            data_list_toimp[sing_rec].find_check)


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except Exception as e :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            #### US TABLE


            if  mapper_class_write == 'US':

                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,

                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].d_stratigrafica,
                            data_list_toimp[sing_rec].d_interpretativa,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].interpretazione,
                            data_list_toimp[sing_rec].periodo_iniziale,
                            data_list_toimp[sing_rec].fase_iniziale,
                            data_list_toimp[sing_rec].periodo_finale,
                            data_list_toimp[sing_rec].fase_finale,
                            data_list_toimp[sing_rec].scavato,
                            data_list_toimp[sing_rec].attivita,
                            data_list_toimp[sing_rec].anno_scavo,
                            data_list_toimp[sing_rec].metodo_di_scavo,
                            data_list_toimp[sing_rec].inclusi,
                            data_list_toimp[sing_rec].campioni,
                            data_list_toimp[sing_rec].rapporti,
                            data_list_toimp[sing_rec].data_schedatura,
                            data_list_toimp[sing_rec].schedatore,
                            data_list_toimp[sing_rec].formazione,
                            data_list_toimp[sing_rec].stato_di_conservazione,
                            data_list_toimp[sing_rec].colore,
                            data_list_toimp[sing_rec].consistenza,
                            data_list_toimp[sing_rec].struttura,
                            data_list_toimp[sing_rec].cont_per,
                            data_list_toimp[sing_rec].order_layer,
                            data_list_toimp[sing_rec].documentazione,
                            data_list_toimp[sing_rec].unita_tipo,
                            # campi aggiunti per USM
                            data_list_toimp[sing_rec].settore,
                            data_list_toimp[sing_rec].quad_par,
                            data_list_toimp[sing_rec].ambient,
                            data_list_toimp[sing_rec].saggio,
                            data_list_toimp[sing_rec].elem_datanti,
                            data_list_toimp[sing_rec].funz_statica,
                            data_list_toimp[sing_rec].lavorazione,
                            data_list_toimp[sing_rec].spess_giunti,
                            data_list_toimp[sing_rec].letti_posa,
                            data_list_toimp[sing_rec].alt_mod,
                            data_list_toimp[sing_rec].un_ed_riass,
                            data_list_toimp[sing_rec].reimp,
                            data_list_toimp[sing_rec].posa_opera,
                            data_list_toimp[sing_rec].quota_min_usm,
                            data_list_toimp[sing_rec].quota_max_usm,
                            data_list_toimp[sing_rec].cons_legante,
                            data_list_toimp[sing_rec].col_legante,
                            data_list_toimp[sing_rec].aggreg_legante,
                            data_list_toimp[sing_rec].con_text_mat,
                            data_list_toimp[sing_rec].col_materiale,
                            data_list_toimp[sing_rec].inclusi_materiali_usm,
                            data_list_toimp[sing_rec].n_catalogo_generale,
                            data_list_toimp[sing_rec].n_catalogo_interno,
                            data_list_toimp[sing_rec].n_catalogo_internazionale,
                            data_list_toimp[sing_rec].soprintendenza,
                            data_list_toimp[sing_rec].quota_relativa,
                            data_list_toimp[sing_rec].quota_abs,
                            data_list_toimp[sing_rec].ref_tm,
                            data_list_toimp[sing_rec].ref_ra,
                            data_list_toimp[sing_rec].ref_n,
                            data_list_toimp[sing_rec].posizione,
                            data_list_toimp[sing_rec].criteri_distinzione,
                            data_list_toimp[sing_rec].modo_formazione,
                            data_list_toimp[sing_rec].componenti_organici,
                            data_list_toimp[sing_rec].componenti_inorganici,
                            data_list_toimp[sing_rec].lunghezza_max,
                            data_list_toimp[sing_rec].altezza_max,
                            data_list_toimp[sing_rec].altezza_min,
                            data_list_toimp[sing_rec].profondita_max,
                            data_list_toimp[sing_rec].profondita_min,
                            data_list_toimp[sing_rec].larghezza_media,
                            data_list_toimp[sing_rec].quota_max_abs,
                            data_list_toimp[sing_rec].quota_max_rel,
                            data_list_toimp[sing_rec].quota_min_abs,
                            data_list_toimp[sing_rec].quota_min_rel,
                            data_list_toimp[sing_rec].osservazioni,
                            data_list_toimp[sing_rec].datazione,
                            data_list_toimp[sing_rec].flottazione,
                            data_list_toimp[sing_rec].setacciatura,
                            data_list_toimp[sing_rec].affidabilita,
                            data_list_toimp[sing_rec].direttore_us,
                            data_list_toimp[sing_rec].responsabile_us,
                            data_list_toimp[sing_rec].cod_ente_schedatore,
                            data_list_toimp[sing_rec].data_rilevazione,
                            data_list_toimp[sing_rec].data_rielaborazione,
                            data_list_toimp[sing_rec].lunghezza_usm,
                            data_list_toimp[sing_rec].altezza_usm,
                            data_list_toimp[sing_rec].spessore_usm,
                            data_list_toimp[sing_rec].tecnica_muraria_usm,
                            data_list_toimp[sing_rec].modulo_usm,
                            data_list_toimp[sing_rec].campioni_malta_usm,
                            data_list_toimp[sing_rec].campioni_mattone_usm,
                            data_list_toimp[sing_rec].campioni_pietra_usm,
                            data_list_toimp[sing_rec].provenienza_materiali_usm,
                            data_list_toimp[sing_rec].criteri_distinzione_usm,
                            data_list_toimp[sing_rec].uso_primario_usm,
                            data_list_toimp[sing_rec].tipologia_opera,
                            data_list_toimp[sing_rec].sezione_muraria,
                            data_list_toimp[sing_rec].superficie_analizzata,
                            data_list_toimp[sing_rec].orientamento ,
                            data_list_toimp[sing_rec].materiali_lat ,
                            data_list_toimp[sing_rec].lavorazione_lat,
                            data_list_toimp[sing_rec].consistenza_lat ,
                            data_list_toimp[sing_rec].forma_lat ,
                            data_list_toimp[sing_rec].colore_lat ,
                            data_list_toimp[sing_rec].impasto_lat ,
                            data_list_toimp[sing_rec].forma_p ,
                            data_list_toimp[sing_rec].colore_p ,
                            data_list_toimp[sing_rec].taglio_p ,
                            data_list_toimp[sing_rec].posa_opera_p ,
                            data_list_toimp[sing_rec].inerti_usm ,
                            data_list_toimp[sing_rec].tipo_legante_usm,
                            data_list_toimp[sing_rec].rifinitura_usm,
                            data_list_toimp[sing_rec].materiale_p ,
                            data_list_toimp[sing_rec].consistenza_p,
                            data_list_toimp[sing_rec].rapporti2,
                            data_list_toimp[sing_rec].doc_usv

                        )


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()




                    except Exception as e :
                        e_error= str(e)
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PERIODIZZAZIONE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_periodizzazione_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].periodo,
                            data_list_toimp[sing_rec].fase,
                            data_list_toimp[sing_rec].cron_iniziale,
                            data_list_toimp[sing_rec].cron_finale,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].datazione_estesa,
                            data_list_toimp[sing_rec].cont_per)


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'INVENTARIO_MATERIALI' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values_reperti(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,

                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].numero_inventario,
                            data_list_toimp[sing_rec].tipo_reperto,
                            data_list_toimp[sing_rec].criterio_schedatura,
                            data_list_toimp[sing_rec].definizione,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].lavato,
                            data_list_toimp[sing_rec].nr_cassa,
                            data_list_toimp[sing_rec].luogo_conservazione,
                            data_list_toimp[sing_rec].stato_conservazione,
                            data_list_toimp[sing_rec].datazione_reperto,
                            data_list_toimp[sing_rec].elementi_reperto,
                            data_list_toimp[sing_rec].misurazioni,
                            data_list_toimp[sing_rec].rif_biblio,
                            data_list_toimp[sing_rec].tecnologie,
                            data_list_toimp[sing_rec].forme_minime,
                            data_list_toimp[sing_rec].forme_massime,
                            data_list_toimp[sing_rec].totale_frammenti,
                            data_list_toimp[sing_rec].corpo_ceramico,
                            data_list_toimp[sing_rec].rivestimento,
                            data_list_toimp[sing_rec].diametro_orlo,
                            data_list_toimp[sing_rec].peso,
                            data_list_toimp[sing_rec].tipo,
                            data_list_toimp[sing_rec].eve_orlo,
                            data_list_toimp[sing_rec].repertato,
                            data_list_toimp[sing_rec].diagnostico,
                            data_list_toimp[sing_rec].n_reperto,
                            data_list_toimp[sing_rec].tipo_contenitore,
                            data_list_toimp[sing_rec].struttura
                        )


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except Exception as e :

                        QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'STRUTTURA' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_struttura_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].sigla_struttura,
                            data_list_toimp[sing_rec].numero_struttura,
                            data_list_toimp[sing_rec].categoria_struttura,
                            data_list_toimp[sing_rec].tipologia_struttura,
                            data_list_toimp[sing_rec].definizione_struttura,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].interpretazione,
                            data_list_toimp[sing_rec].periodo_iniziale,
                            data_list_toimp[sing_rec].fase_iniziale,
                            data_list_toimp[sing_rec].periodo_finale,
                            data_list_toimp[sing_rec].fase_finale,
                            data_list_toimp[sing_rec].datazione_estesa,
                            data_list_toimp[sing_rec].materiali_impiegati,
                            data_list_toimp[sing_rec].elementi_strutturali,
                            data_list_toimp[sing_rec].rapporti_struttura,
                            data_list_toimp[sing_rec].misure_struttura
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()
                    except :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'TOMBA' :
                for sing_rec in range(len(data_list_toimp)):



                        # blocco periodo_iniziale
                    test_per_iniz = data_list_toimp[sing_rec].periodo_iniziale

                    if test_per_iniz == "" or test_per_iniz == None:
                        per_iniz = ''
                    else:
                        per_iniz = int(data_list_toimp[sing_rec].periodo_iniziale)

                        # blocco fase_iniziale
                    test_fas_iniz = data_list_toimp[sing_rec].fase_iniziale

                    if test_fas_iniz == "" or test_fas_iniz == None:
                        fase_iniz = ''
                    else:
                        fase_iniz = int(data_list_toimp[sing_rec].fase_iniziale)

                        # blocco periodo_finale
                    test_per_fin = data_list_toimp[sing_rec].periodo_finale

                    if test_per_fin == "" or test_per_fin == None:
                        per_fin = ''
                    else:
                        per_fin = int(data_list_toimp[sing_rec].periodo_finale)

                        # blocco fase_finale
                    test_fas_fin = data_list_toimp[sing_rec].fase_finale

                    if test_fas_fin == "" or test_fas_fin == None:
                        fase_fin = ''
                    else:
                        fase_fin = int(data_list_toimp[sing_rec].fase_finale)

                    try:
                        data = self.DB_MANAGER_write.insert_values_tomba(

                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            str(data_list_toimp[sing_rec].sito),
                            str(data_list_toimp[sing_rec].area),
                            str(data_list_toimp[sing_rec].nr_scheda_taf),
                            str(data_list_toimp[sing_rec].sigla_struttura),
                            str(data_list_toimp[sing_rec].nr_struttura),
                            str(data_list_toimp[sing_rec].nr_individuo),
                            str(data_list_toimp[sing_rec].rito),
                            str(data_list_toimp[sing_rec].descrizione_taf),
                            str(data_list_toimp[sing_rec].interpretazione_taf),
                            str(data_list_toimp[sing_rec].segnacoli),
                            str(data_list_toimp[sing_rec].canale_libatorio_si_no),
                            str(data_list_toimp[sing_rec].oggetti_rinvenuti_esterno),
                            str(data_list_toimp[sing_rec].stato_di_conservazione),
                            str(data_list_toimp[sing_rec].copertura_tipo),
                            str(data_list_toimp[sing_rec].tipo_contenitore_resti),
                            str(data_list_toimp[sing_rec].tipo_deposizione),
                            str(data_list_toimp[sing_rec].tipo_sepoltura),
                            str(data_list_toimp[sing_rec].corredo_presenza),
                            str(data_list_toimp[sing_rec].corredo_tipo),
                            str(data_list_toimp[sing_rec].corredo_descrizione),
                            per_iniz,
                            fase_iniz,
                            per_fin,
                            fase_fin,
                            str(data_list_toimp[sing_rec].datazione_estesa)
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except Exception as e :

                        QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'SCHEDAIND' :
                for sing_rec in range(len(data_list_toimp)):
                    # blocco oritentamento_azimut
                    # test_azimut = data_list_toimp[sing_rec].orientamento_azimut

                    # if test_azimut == "" or test_azimut == None:
                        # orientamento_azimut = None
                    # else:
                        # orientamento_azimut = float(data_list_toimp[sing_rec].orientamento_azimut)
                    ##                  if conn_str_dict_write['server'] == 'postgres':
                    ##                      orientamento_azimut = float(orientamento_azimut)
                    ##

                    # blocco oritentamento_azimut
                    test_lunghezza_scheletro = data_list_toimp[sing_rec].lunghezza_scheletro

                    if test_lunghezza_scheletro == "" or test_lunghezza_scheletro == None:
                        lunghezza_scheletro = None
                    else:
                        lunghezza_scheletro = float(data_list_toimp[sing_rec].lunghezza_scheletro)
                    
                    

                    try:
                        data = self.DB_MANAGER_write.insert_values_ind(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].nr_individuo,
                            data_list_toimp[sing_rec].data_schedatura,
                            data_list_toimp[sing_rec].schedatore,
                            data_list_toimp[sing_rec].sesso,
                            data_list_toimp[sing_rec].eta_min,
                            data_list_toimp[sing_rec].eta_max,
                            data_list_toimp[sing_rec].classi_eta,
                            data_list_toimp[sing_rec].osservazioni,
                            data_list_toimp[sing_rec].sigla_struttura,
                            data_list_toimp[sing_rec].nr_struttura,
                            data_list_toimp[sing_rec].completo_si_no,
                            data_list_toimp[sing_rec].disturbato_si_no,
                            data_list_toimp[sing_rec].in_connessione_si_no,
                            lunghezza_scheletro,
                            data_list_toimp[sing_rec].posizione_scheletro,
                            data_list_toimp[sing_rec].posizione_cranio,
                            data_list_toimp[sing_rec].posizione_arti_superiori,
                            data_list_toimp[sing_rec].posizione_arti_inferiori,
                            data_list_toimp[sing_rec].orientamento_asse,
                            data_list_toimp[sing_rec].orientamento_azimut
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'CAMPIONI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values_campioni(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nr_campione,
                            data_list_toimp[sing_rec].tipo_campione,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].numero_inventario_materiale,
                            data_list_toimp[sing_rec].nr_cassa,
                            data_list_toimp[sing_rec].luogo_conservazione
                        )
                        self.DB_MANAGER_write.insert_data_session(data)
                        for i in range(sing_rec):
                            #time.sleep()
                            self.progress_bar.setValue(((i)/100)*100)

                            QApplication.processEvents()

                    except :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'DOCUMENTAZIONE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values_documentazione(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].tipo_documentazione,
                            data_list_toimp[sing_rec].sorgente,
                            data_list_toimp[sing_rec].scala,
                            data_list_toimp[sing_rec].disegnatore,
                            data_list_toimp[sing_rec].note
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except Exception as  e:
                        e_str = str(e)
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)

                        return 0

                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'UT':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_ut_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].progetto,
                            data_list_toimp[sing_rec].nr_ut,
                            data_list_toimp[sing_rec].ut_letterale,
                            data_list_toimp[sing_rec].def_ut,
                            data_list_toimp[sing_rec].descrizione_ut,
                            data_list_toimp[sing_rec].interpretazione_ut,
                            data_list_toimp[sing_rec].nazione,
                            data_list_toimp[sing_rec].regione,
                            data_list_toimp[sing_rec].provincia,
                            data_list_toimp[sing_rec].comune,
                            data_list_toimp[sing_rec].frazione,
                            data_list_toimp[sing_rec].localita,
                            data_list_toimp[sing_rec].indirizzo,
                            data_list_toimp[sing_rec].nr_civico,
                            data_list_toimp[sing_rec].carta_topo_igm,
                            data_list_toimp[sing_rec].coord_geografiche,
                            data_list_toimp[sing_rec].coord_piane,
                            data_list_toimp[sing_rec].andamento_terreno_pendenza,
                            data_list_toimp[sing_rec].utilizzo_suolo_vegetazione,
                            data_list_toimp[sing_rec].descrizione_empirica_suolo,
                            data_list_toimp[sing_rec].descrizione_luogo,
                            data_list_toimp[sing_rec].metodo_rilievo_e_ricognizione,
                            data_list_toimp[sing_rec].geometria,
                            data_list_toimp[sing_rec].bibliografia,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].ora_meteo,
                            data_list_toimp[sing_rec].descrizione_luogo,
                            data_list_toimp[sing_rec].responsabile,
                            data_list_toimp[sing_rec].dimensioni_ut,
                            data_list_toimp[sing_rec].rep_per_mq,
                            data_list_toimp[sing_rec].rep_datanti,
                            data_list_toimp[sing_rec].periodo_I,
                            data_list_toimp[sing_rec].datazione_I,
                            data_list_toimp[sing_rec].responsabile,
                            data_list_toimp[sing_rec].interpretazione_I,
                            data_list_toimp[sing_rec].periodo_II,
                            data_list_toimp[sing_rec].datazione_II,
                            data_list_toimp[sing_rec].interpretazione_II,
                            data_list_toimp[sing_rec].documentazione,
                            data_list_toimp[sing_rec].enti_tutela_vincoli,
                            data_list_toimp[sing_rec].indagini_preliminari
                        )


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()


                    except :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")




            elif mapper_class_write == 'PYARCHINIT_THESAURUS_SIGLE' :

                for sing_rec in range(len(data_list_toimp)):

                    try:
                        data = self.DB_MANAGER_write.insert_values_thesaurus(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].nome_tabella,
                            data_list_toimp[sing_rec].sigla,
                            data_list_toimp[sing_rec].sigla_estesa,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].tipologia_sigla,
                            data_list_toimp[sing_rec].lingua
                            )


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except Exception as e :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            ###########################IMPORTAZIONE MEDIA##############################################    
            elif mapper_class_write == 'MEDIA' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_media_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_media,
                            data_list_toimp[sing_rec].mediatype,
                            data_list_toimp[sing_rec].filename,
                            data_list_toimp[sing_rec].filetype,
                            data_list_toimp[sing_rec].filepath,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].tags)


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()
                    except Exception as  e:
                        e_str = str(e)
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)

                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'MEDIA_THUMB' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_mediathumb_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_media_thumb,
                            data_list_toimp[sing_rec].id_media,
                            data_list_toimp[sing_rec].mediatype,
                            data_list_toimp[sing_rec].media_filename,
                            data_list_toimp[sing_rec].media_thumb_filename,
                            data_list_toimp[sing_rec].filetype,
                            data_list_toimp[sing_rec].filepath,
                            data_list_toimp[sing_rec].path_resize)


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()

                    except Exception as  e:
                        e_str = str(e)
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)

                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")


            elif mapper_class_write == 'MEDIATOENTITY' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_media2entity_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_mediaToEntity,
                            data_list_toimp[sing_rec].id_entity,
                            data_list_toimp[sing_rec].entity_type,
                            data_list_toimp[sing_rec].table_name,
                            data_list_toimp[sing_rec].id_media,
                            data_list_toimp[sing_rec].filepath,
                            data_list_toimp[sing_rec].media_name)


                        self.DB_MANAGER_write.insert_data_session(data)

                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)

                        QApplication.processEvents()
                    except Exception as  e:
                        e_str = str(e)
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)

                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")


            
    def openthumbDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_path.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    def openresizeDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_resize.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    
    def on_pushButton_connect_pressed(self):

        # Defines parameter
        self.ip=str(self.lineEdit_ip.text())


        self.user=str(self.lineEdit_user.text())



        self.pwd=str(self.lineEdit_password.text())



        try:
            ftp = FTP(self.ip)
            a = ftp.login(self.user, self.pwd)
            if bool(a):
                self.lineEdit_2.insert("Connection succesfully stablished ......... ")
                dirlist = ftp.cwd('/')

                self.listWidget.insertItem(0,dirlist)

            else:
                self.lineEdit_2.insert("Errore di connessione ......... ")

        except:
            self.lineEdit_2.insert("Errore di connessione ......... ")





        # #Download the file from the remote server
        # remote_file = '/home/data/ftp/demoliz/qgis/rep5/test.qgs'

        # with srv.cd('../'):             # still in .
            # srv.chdir('home')    # now in ./static
            # srv.chdir('data')      # now in ./static/here
            # srv.chdir('ftp')
            # srv.chdir('demoliz')

            # srv.chdir('qgis')
            # srv.chdir('rep5')
            # self.listWidget.insertItem(0,"--------------------------------------------")


        # srv.close()
    # def loginServer():
        # # user = ent_login.get()
        # # password = ent_pass.get()
        # try:
            # msg = ftp.login(user,password)
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,msg)
            # displayDir()
            # # lbl_login.place_forget()
            # # ent_login.place_forget()
            # # lbl_pass.place_forget()
            # # ent_pass.place_forget()
            # # btn_login.place_forget()
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to login")


    # def displayDir():
        # libox_serverdir.insert(0,"--------------------------------------------")
        # dirlist = []
        # dirlist = ftp.nlst()
        # for item in dirlist:
            # libox_serverdir.insert(0, item)

    # #FTP commands
    # def on_pushButton_change_dir_pressed(self):
        # cnopts = pysftp.CnOpts()
        # cnopts.hostkeys = None
        # with pysftp.Connection(host="ftp.adarteifo.it", username="adarteinfo",
        # password="adarteinfo",cnopts =cnopts ) as sftp:

            # try:
                # msg = sftp.cwd('/home') # Switch to a remote directory

                # directory_structure = sftp.listdir_attr()# Obtain structure of the remote directory

                # for attr in directory_structure:
                    # self.listWidget.insertItem(attr.filename, attr)

            # except:
                # self.lineEdit_2.insert("\n")
                # self.lineEdit_2.insert("Unable to change directory")
            # dirlist = []
            # dirlist = sftp.listdir()
            # for item in dirlist:
                # self.listWidget.insertItem(0,item)


    # def on_pushButton_disconnect_pressed(self):

       # cnopts = pysftp.CnOpts()
       # cnopts.hostkeys = None
       # srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
       # self.lineEdit_2.insert("Connection Close ............. ")
       # srv.close()
    def on_pushButton_convertdb_pressed(self):
        QMessageBox.warning(self, "Attenzione",
                                     "Assicurati che il nome del db non abbia parentesi o caratteri spaciali, altrimenti la conversione fallisce",
                                     QMessageBox.Ok)
        if self.comboBox_Database.currentText() == 'sqlite':

            if platform.system() == "Windows":
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'spatialite_convert.exe')
                #db1 = os.path.join(os.sep, self.HOME, 'bin', 'pyarchinit.sqlite')
                
            
            else:
                QMessageBox.warning(self, "Attenzione",
                                     "Funzione abilitata solo per windows",
                                     QMessageBox.Ok)

            db1 = os.path.join(os.sep, self.HOME, 'pyarchinit_DB_folder', self.lineEdit_DBname.text())

            # text_ = cmd, self.comboBox_compare.currentText(), db1 + ' ', db2
            # result = subprocess.check_output([text_], stderr=subprocess.STDOUT)
            os.system("start cmd /k" + cmd + ' --db-path ' + ' ' +db1 +' '+ '-tv 4' )
            os.system("start cmd /k" + cmd + ' --db-path ' + ' ' + db1 +' '+ '-tv 5' )
            

        else:
            QMessageBox.warning(self, "Attenzione",
                                     "ops qualcosa è andato storto",
                                     QMessageBox.Ok)
    