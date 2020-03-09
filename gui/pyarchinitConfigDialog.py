# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
    ------------------------------------------------------------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
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
import time
from sqlalchemy.event import listen

from builtins import range
from builtins import str
import pysftp
from sqlalchemy.sql import select, func
from sqlalchemy import create_engine
from qgis.PyQt.QtCore import  pyqtSlot, pyqtSignal,QThread
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog,QLineEdit,QWidget

from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication, QgsSettings, QgsProject

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.pyarchinit_db_update import DB_update
from modules.db.db_createdump import CreateDatabase, RestoreSchema, DropDatabase, SchemaDump
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

from modules.utility.pyarchinit_print_utility import Print_utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'pyarchinitConfigDialog.ui'))





class pyArchInitDialog_Config(QDialog, MAIN_DIALOG_CLASS):
    progressBarUpdated = pyqtSignal(int,int)
    L=QgsSettings().value("locale/userLocale")[0:2]
    
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
                   'EXPERIMENTAL': ''}

    def __init__(self, parent=None, db=None):
       
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        
        self.setupUi(self)
        
        s = QgsSettings()
        self.load_dict()
        self.charge_data()
        self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
        self.comboBox_server_rd.editTextChanged.connect(self.set_db_import_from_parameter)
        self.comboBox_server_wt.editTextChanged.connect(self.set_db_import_to_parameter)
        self.pushButton_save.clicked.connect(self.on_pushButton_save_pressed)
        self.pushButtonGraphviz.clicked.connect(self.setPathGraphviz)
        self.pbnSaveEnvironPath.clicked.connect(self.setEnvironPath)
        self.toolButton_thumbpath.clicked.connect(self.setPathThumb)
        self.toolButton_resizepath.clicked.connect(self.setPathResize)
        self.toolButton_db.clicked.connect(self.setPathDB)
        self.pushButtonR.clicked.connect(self.setPathR)
        self.pbnSaveEnvironPathR.clicked.connect(self.setEnvironPathR)
        self.pushButton_import.clicked.connect(self.on_pushButton_import_pressed)
        self.graphviz_bin = s.value('pyArchInit/graphvizBinPath', None, type=str)
        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)

        if Pyarchinit_OS_Utility.checkGraphvizInstallation():
            self.pushButtonGraphviz.setEnabled(False)
            self.pbnSaveEnvironPath.setEnabled(False)
            self.lineEditGraphviz.setEnabled(False)
        
        self.r_bin = s.value('pyArchInit/rBinPath', None, type=str)
        if self.r_bin:
            self.lineEditR.setText(self.r_bin)

        if Pyarchinit_OS_Utility.checkRInstallation():
            self.pushButtonR.setEnabled(False)
            self.pbnSaveEnvironPathR.setEnabled(False)
            self.lineEditR.setEnabled(False)
        
        
        
        self.selectorCrsWidget.setCrs(QgsProject.instance().crs())
        self.selectorCrsWidget_sl.setCrs(QgsProject.instance().crs())

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
    
    def setPathR(self):
        s = QgsSettings()
        self.r_bin = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )

        if self.r_bin:
            self.lineEditR.setText(self.r_bin)
            s.setValue('pyArchInit/rBinPath', self.r_bin)
    
    
    def setEnvironPath(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.graphviz_bin)
        QMessageBox.warning(self, "Set Environmental Variable", "The path has been set successful", QMessageBox.Ok)
    def setEnvironPathR(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.r_bin)
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
        QMessageBox.warning(self, "ok", "entered in read.", QMessageBox.Ok)

        if self.comboBox_server_rd.currentText() == 'postgres':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            self.lineEdit_host_rd.setText('127.0.0.1')
            self.lineEdit_username_rd.setText('postgres')
            self.lineEdit_database_rd.setText('pyarchinit')
            self.lineEdit_port_rd.setText('5432')

        if self.comboBox_server_rd.currentText() == 'sqlite':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)

            self.lineEdit_host_rd.setText.setText('')
            self.lineEdit_username_rd.setText('')
            self.lineEdit_lineEdit_pass_rd.setText('')
            self.lineEdit_database_rd.setText('pyarchinit_db.sqlite')
            self.lineEdit_port_rd.setText('')

    def set_db_import_to_parameter(self):
        QMessageBox.warning(self, "ok", "entered in write", QMessageBox.Ok)

        if self.comboBox_server_wt.currentText() == 'postgres':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)

            self.lineEdit_host_wt.setText('127.0.0.1')
            self.lineEdit_username_wt.setText('postgres')
            self.lineEdit_database_wt.setText('pyarchinit')
            self.lineEdit_port_wt.setText('5432')

        if self.comboBox_server_wt.currentText() == 'sqlite':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)

            self.lineEdit_host_wt.setText.setText('')
            self.lineEdit_username_wt.setText('')
            self.lineEdit_lineEdit_pass_wt.setText('')
            self.lineEdit_database_wt.setText('pyarchinit_db.sqlite')
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
        self.PARAMS_DICT['SERVER'] = str(self.comboBox_Database.currentText())
        self.PARAMS_DICT['HOST'] = str(self.lineEdit_Host.text())
        self.PARAMS_DICT['DATABASE'] = str(self.lineEdit_DBname.text())
        self.PARAMS_DICT['PASSWORD'] = str(self.lineEdit_Password.text())
        self.PARAMS_DICT['PORT'] = str(self.lineEdit_Port.text())
        self.PARAMS_DICT['USER'] = str(self.lineEdit_User.text())
        self.PARAMS_DICT['THUMB_PATH'] = str(self.lineEdit_Thumb_path.text())
        self.PARAMS_DICT['THUMB_RESIZE'] = str(self.lineEdit_Thumb_resize.text())
        self.PARAMS_DICT['EXPERIMENTAL'] = str(self.comboBox_experimental.currentText())

        self.save_dict()
        self.try_connection()
        # QMessageBox.warning(self, "ok", "Per rendere effettive le modifiche e' necessario riavviare Qgis. Grazie.",
        #                     QMessageBox.Ok)

    def on_pushButton_crea_database_pressed(self,):
        schema_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'pyarchinit_schema_clean.sql')
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'create_view.sql')
        create_database = CreateDatabase(self.lineEdit_dbname.text(), self.lineEdit_db_host.text(),
                                         self.lineEdit_port_db.text(), self.lineEdit_db_user.text(),
                                         self.lineEdit_db_passwd.text())

        ok, db_url = create_database.createdb()

        if ok:
            try:
                RestoreSchema(db_url, schema_file).restore_schema()
            except Exception as e:
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


    def on_pushButton_upd_postgres_pressed(self):
       
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'pyarchinit_update_postgres.sql')
        
        conn = Connection()
        db_url = conn.conn_str()
        #RestoreSchema(db_url,None).update_geom_srid( 'public','%d' % int(self.lineEdit_crs.text()))
        
        if RestoreSchema(db_url,view_file).restore_schema()== False:
            
            QMessageBox.warning(self, "INFO", "The DB exist already", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "INFO", "Updated", QMessageBox.Ok)
        

        
    def load_spatialite(self,dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)
        
        if Pyarchinit_OS_Utility.isWindows()== True:
            dbapi_conn.load_extension('mod_spatialite.dll')
        
        elif Pyarchinit_OS_Utility.isMac()== True:
            dbapi_conn.load_extension('mod_spatialite.dylib')
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
            sql_und = """CREATE TABLE IF NOT EXISTS"pyarchinit_us_negative_doc" (
                "pkuid" integer PRIMARY KEY AUTOINCREMENT,
                "sito_n" text,
                "area_n" text,
                "us_n" integer,
                "tipo_doc_n" text,
                "nome_doc_n" text, "the_geom" LINESTRING);"""
            c.execute(sql_und)
            c.execute(select([func.AddGeometryColumn('pyarchinit_us_negative_doc', 'the_geom', 4326, 'LINESTRING', 'XY')]))
            c.execute(select([func.CreateSpatialIndex('pyarchinit_us_negative_doc', 'the_geom')]))
            sql_doc = """CREATE TABLE IF NOT EXISTS"pyarchinit_documentazione" (
                "pkuid" integer PRIMARY KEY AUTOINCREMENT,
                "sito" text,
                "nome_doc" text,
                "tipo_doc" text,
                "path_qgis_pj" text, "the_geom" LINESTRING);"""
            c.execute(sql_doc)
            c.execute(select([func.AddGeometryColumn('pyarchinit_documentazione', 'the_geom', 4326, 'LINESTRING', 'XY')]))
            c.execute(select([func.CreateSpatialIndex('pyarchinit_documentazione', 'the_geom')]))
                
            sql_rep = """CREATE TABLE if not exists "pyarchinit_reperti" ("ROWIND" INTEGER PRIMARY KEY AUTOINCREMENT, "id_rep" INTEGER, "siti" TEXT, "link" TEXT);"""
            c.execute(sql_rep)
            #c.connect(db_path)
            c.execute(select([func.AddGeometryColumn('pyarchinit_reperti', 'the_geom', 4326, 'POINT', 'XY')]))
            c.execute(select([func.CreateSpatialIndex('pyarchinit_reperti', 'the_geom')]))
            
            sql_view_ndv="""CREATE VIEW IF NOT EXISTS"pyarchinit_us_negative_doc_view" AS
                SELECT "a"."ROWID" AS "ROWID", "a"."pkuid" AS "pkuid",
                "a"."sito_n" AS "sito_n", "a"."area_n" AS "area_n",
                "a"."us_n" AS "us_n", "a"."tipo_doc_n" AS "tipo_doc_n",
                "a"."nome_doc_n" AS "nome_doc_n", "a"."the_geom" AS "the_geom",
                "b"."ROWID" AS "ROWID_1", "b"."id_us" AS "id_us",
                "b"."sito" AS "sito", "b"."area" AS "area", "b"."us" AS "us",
                "b"."d_stratigrafica" AS "d_stratigrafica", "b"."d_interpretativa" AS "d_interpretativa",
                "b"."descrizione" AS "descrizione", "b"."interpretazione" AS "interpretazione",
                "b"."periodo_iniziale" AS "periodo_iniziale", "b"."fase_iniziale" AS "fase_iniziale",
                "b"."periodo_finale" AS "periodo_finale", "b"."fase_finale" AS "fase_finale",
                "b"."scavato" AS "scavato", "b"."attivita" AS "attivita",
                "b"."anno_scavo" AS "anno_scavo", "b"."metodo_di_scavo" AS "metodo_di_scavo",
                "b"."inclusi" AS "inclusi", "b"."campioni" AS "campioni",
                "b"."rapporti" AS "rapporti", "b"."data_schedatura" AS "data_schedatura",
                "b"."schedatore" AS "schedatore", "b"."formazione" AS "formazione",
                "b"."stato_di_conservazione" AS "stato_di_conservazione",
                "b"."colore" AS "colore", "b"."consistenza" AS "consistenza",
                "b"."struttura" AS "struttura", "b"."cont_per" AS "cont_per",
                "b"."order_layer" AS "order_layer", "b"."documentazione" AS "documentazione"
                FROM "pyarchinit_us_negative_doc" AS "a"
                JOIN "us_table" AS "b" ON ("a"."sito_n" = "b"."sito" AND "a"."area_n" = "b"."area"
                AND "a"."us_n" = "b"."us");"""
            c.execute(sql_view_ndv)
            sql_view_ndv_geom= """INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column)
                    VALUES ('pyarchinit_us_negative_doc_view', 'the_geom', 'ROWID', 'pyarchinit_us_negative_doc', 'the_geom')"""  
            c.execute(sql_view_ndv_geom)
            
            sql_doc_view= """CREATE VIEW IF NOT EXISTS"pyarchinit_doc_view" AS
                    SELECT "a"."ROWID" AS "ROWID", "a"."id_documentazione" AS "id_documentazione",
                    "a"."sito" AS "sito", "a"."nome_doc" AS "nome_doc",
                    "a"."data" AS "data", "a"."tipo_documentazione" AS "tipo_documentazione",
                    "a"."sorgente" AS "sorgente", "a"."scala" AS "scala",
                    "a"."disegnatore" AS "disegnatore", "a"."note" AS "note",
                    "b"."ROWID" AS "ROWID_1", "b"."pkuid" AS "pkuid",
                    "b"."sito" AS "sito_1", "b"."nome_doc" AS "nome_doc_1",
                    "b"."tipo_doc" AS "tipo_doc", "b"."path_qgis_pj" AS "path_qgis_pj",
                    "b"."the_geom" AS "the_geom"
                    FROM "documentazione_table" AS "a"
                    JOIN "pyarchinit_documentazione" AS "b" ON ("a"."sito" = "b"."sito" AND "a"."nome_doc" = "b"."nome_doc"
                    AND "a"."tipo_documentazione" = "b"."tipo_doc");"""
            c.execute(sql_doc_view)
            sql_view_doc_geom ="""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column)
                    VALUES ('pyarchinit_doc_view', 'the_geom', 'rowid', 'pyarchinit_documentazione', 'the_geom')"""
            c.execute(sql_view_doc_geom)
            
            sql_drop_view= """DROP view if EXISTS mediaentity_view;"""
            c.execute(sql_drop_view)
            
            sql_alter= """alter table media_thumb_table rename to 'temp_media_thumb';"""
            c.execute(sql_alter)
            
            sql_media_thumb="""CREATE TABLE media_thumb_table (id_media_thumb INTEGER NOT NULL, id_media INTEGER, mediatype TEXT, media_filename TEXT, media_thumb_filename TEXT, filetype VARCHAR(10), filepath TEXT, path_resize TEXT, PRIMARY KEY (id_media_thumb), CONSTRAINT "ID_media_thumb_unico" UNIQUE (media_thumb_filename) )"""
            c.execute(sql_media_thumb)
            
            
            sql_insert_media_thumb="""INSERT INTO media_thumb_table(id_media_thumb, id_media , mediatype , media_filename, media_thumb_filename , filetype , filepath) SELECT id_media_thumb, id_media , mediatype , media_filename, media_thumb_filename , filetype , filepath FROM temp_media_thumb;"""
            c.execute(sql_insert_media_thumb)
            
            
            sql_drop_temp="""DROP TABLE temp_media_thumb;"""
            c.execute(sql_drop_temp)
            
            
            sql_view_mediaentity="""CREATE VIEW IF NOT EXISTS "mediaentity_view" AS
                 SELECT media_thumb_table.id_media_thumb,
                    media_thumb_table.id_media,
                    media_thumb_table.filepath,
                    media_thumb_table.path_resize,
                    media_to_entity_table.entity_type,
                    media_to_entity_table.id_media AS id_media_m,
                    media_to_entity_table.id_entity
                   FROM media_thumb_table
                     JOIN media_to_entity_table ON (media_thumb_table.id_media = media_to_entity_table.id_media)
                  ORDER BY media_to_entity_table.id_entity;"""
            c.execute(sql_view_mediaentity)
            
            sql_trigger_delete_media= """CREATE TRIGGER IF NOT EXISTS delete_media_table 
                    After delete 
                    ON media_thumb_table 

                    BEGIN 
                    DELETE from media_table 
                    where id_media = OLD.id_media ; 
                    END; """
            c.execute(sql_trigger_delete_media)
            
            sql_trigger_delete_mediaentity="""CREATE TRIGGER IF NOT EXISTS media_entity_delete 
                After delete 
                ON media_thumb_table 

                BEGIN 
                DELETE from media_to_entity_table 
                where id_media = OLD.id_media ; 
                END;"""
            c.execute(sql_trigger_delete_mediaentity)
            sql_view_rep="""CREATE VIEW if not exists "pyarchinit_reperti_view" AS
                SELECT "a"."ROWID" AS "ROWID", "a"."ROWIND" AS "ROWIND",
                    "a"."the_geom" AS "the_geom",
                    "a"."id_rep" AS "id_rep", "a"."siti" AS "siti", "a"."link" AS "link",
                    "b"."ROWID" AS "ROWID_1", "b"."id_invmat" AS "id_invmat",
                    "b"."sito" AS "sito", "b"."numero_inventario" AS "numero_inventario",
                    "b"."tipo_reperto" AS "tipo_reperto", "b"."criterio_schedatura" AS "criterio_schedatura",
                    "b"."definizione" AS "definizione", "b"."descrizione" AS "descrizione",
                    "b"."area" AS "area", "b"."us" AS "us", "b"."lavato" AS "lavato",
                    "b"."nr_cassa" AS "nr_cassa", "b"."luogo_conservazione" AS "luogo_conservazione",
                    "b"."stato_conservazione" AS "stato_conservazione",
                    "b"."datazione_reperto" AS "datazione_reperto",
                    "b"."elementi_reperto" AS "elementi_reperto", "b"."misurazioni" AS "misurazioni",
                    "b"."rif_biblio" AS "rif_biblio", "b"."tecnologie" AS "tecnologie",
                    "b"."forme_minime" AS "forme_minime", "b"."forme_massime" AS "forme_massime",
                    "b"."totale_frammenti" AS "totale_frammenti", "b"."corpo_ceramico" AS "corpo_ceramico",
                    "b"."rivestimento" AS "rivestimento"
                FROM "pyarchinit_reperti" AS "a"
                JOIN "inventario_materiali_table_toimp" AS "b" ON ("a"."siti" = "b"."sito" AND "a"."id_rep" = "b"."numero_inventario")"""
            c.execute(sql_view_rep)
            sql_view_rep_geom= """INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column)
                    VALUES ('pyarchinit_reperti_view', 'the_geom', 'rowid', 'pyarchinit_reperti', 'the_geom')"""  
            c.execute(sql_view_rep_geom)
            
            
            
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
        conn = Connection()
        conn_str = conn.conn_str()

        self.DB_MANAGER = Pyarchinit_db_management(
            conn_str)  # sqlite:///\Users\Windows\pyarchinit_DB_folder\pyarchinit_db.sqlite

        test = self.DB_MANAGER.connection()
        if self.L=='it':
            if test:
                QMessageBox.warning(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
           
            else:
                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                    "Cambia i parametri e riprova a connetterti. Se cambi server (Postgres o Sqlite) ricordati di cliccare su connetti e RIAVVIARE Qgis",
                                    QMessageBox.Ok)
        elif self.L=='de':
            if test:
                QMessageBox.warning(self, "Message", "Erfolgreich verbunden", QMessageBox.Ok)
            # elif test.find("create_engine") != -1:
            #     QMessageBox.warning(self, "Alert",
            #                         "Verifica i parametri di connessione. <br> Se sono corretti RIAVVIA QGIS",
            #                         QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "Verbindungsfehler: <br>" +
                    "Ändern Sie die Parameter und versuchen Sie, sich erneut zu verbinden. Wenn Sie den Server wechseln (Postgres oder Sqlite), denken Sie daran, auf Verbinden zu klicken und Qgis erneut anzusehen.",
                                    QMessageBox.Ok)
                                    
        else:
            if test:
                QMessageBox.warning(self, "Message", "Successfully connected", QMessageBox.Ok)
            # elif test.find("create_engine") != -1:
            #     QMessageBox.warning(self, "Alert",
            #                         "Verifica i parametri di connessione. <br> Se sono corretti RIAVVIA QGIS",
            #                         QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "Connection error: <br>" +
                    "Change the parameters and try to connect again. If you change servers (Postgres or Sqlite) remember to click on connect and REVIEW Qgis",
                                    QMessageBox.Ok)                         
    def charge_data(self):
        # load data from config.cfg file
        # print self.PARAMS_DICT
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
            ###############

    def test_def(self):
        pass
    
    

    

    def on_pushButton_import_pressed(self):
        
        
        if self.L=='it':
            id_table_class_mapper_conv_dict = {
                'SITE': 'id_sito',
                'US': 'id_us',
                'UT': 'id_ut',
                'PERIODIZZAZIONE': 'id_perfas',
                'INVENTARIO_MATERIALI': 'id_invmat',
                'STRUTTURA': 'id_struttura',
                'TAFONOMIA': 'id_tafonomia',
                'SCHEDAIND': 'id_scheda_ind',
                'CAMPIONE': 'id_campione',
                'DOCUMENTAZIONE': 'id_documentazione',
                'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle'
            }
        elif self.L=='de':
            id_table_class_mapper_conv_dict = {
                'SE': 'id_us',
                'TE': 'id_ut',
                'AUSGRABUNGSSTÄTTE': 'id_sito',
                'PERIODISIERUNG': 'id_perfas',
                'ARTEFAKT-INVENTAR': 'id_invmat',
                'STRUKTUREN': 'id_struttura',
                'TAPHONOMIE': 'id_tafonomia',
                'INDIVIDUEL': 'id_scheda_ind',
                'BEISPIELS': 'id_campione',
                'DOKUMENTATION': 'id_documentazione',
                'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle'
            }
        else:
            id_table_class_mapper_conv_dict = {
                'SU': 'id_us',
                'TU': 'id_ut',
                'SITE': 'id_sito',
                'PERIODIATION': 'id_perfas',
                'ARTEFACT': 'id_invmat',
                'STRUCTURE': 'id_struttura',
                'TAPHONOMY': 'id_tafonomia',
                'INDIVIDUAL': 'id_scheda_ind',
                'SAMPLE': 'id_campione',
                'DOCUMENTATION': 'id_documentazione',
                'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle'
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
            QMessageBox.warning(self, "Alert", "Connection error: <br>", QMessageBox.Ok)
        """elif test.find("create_engine") != -1:
            #QMessageBox.warning(self, "Alert",
                                "Try connection parameter. <br> If they are correct restart QGIS",
                                QMessageBox.Ok)"""


        ####LEGGE I RECORD IN BASE AL PARAMETRO CAMPO=VALORE
        search_dict = {
            self.lineEdit_field_rd.text(): "'" + str(self.lineEdit_value_rd.text()) + "'"
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
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
                        data_list_toimp[sing_rec].uso_primario_usm
                    )
                    

                    self.DB_MANAGER_write.insert_data_session(data)
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                    
                    
                    
                except Exception as e :
                    e_error= str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
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
                        data_list_toimp[sing_rec].diagnostico
                    )
                    
                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
            QMessageBox.information(self, "Message", "Data Loaded")
        
        elif mapper_class_write == 'TAFONOMIA' :
            for sing_rec in range(len(data_list_toimp)):

                # blocco oritentamento_azimut
                test_azimut = data_list_toimp[sing_rec].orientamento_azimut

                if test_azimut == "" or test_azimut == None:
                    orientamento_azimut = None
                else:
                    orientamento_azimut = float(data_list_toimp[sing_rec].orientamento_azimut)
                ##                  if conn_str_dict_write['server'] == 'postgres':
                ##                      orientamento_azimut = float(orientamento_azimut)
                ##

                # blocco oritentamento_azimut
                test_lunghezza_scheletro = data_list_toimp[sing_rec].lunghezza_scheletro

                if test_lunghezza_scheletro == "" or test_lunghezza_scheletro == None:
                    lunghezza_scheletro = None
                else:
                    lunghezza_scheletro = float(data_list_toimp[sing_rec].lunghezza_scheletro)

                    # blocco periodo_iniziale
                test_per_iniz = data_list_toimp[sing_rec].periodo_iniziale

                if test_per_iniz == "" or test_per_iniz == None:
                    per_iniz = None
                else:
                    per_iniz = int(data_list_toimp[sing_rec].periodo_iniziale)

                    # blocco fase_iniziale
                test_fas_iniz = data_list_toimp[sing_rec].fase_iniziale

                if test_fas_iniz == "" or test_fas_iniz == None:
                    fase_iniz = None
                else:
                    fase_iniz = int(data_list_toimp[sing_rec].fase_iniziale)

                    # blocco periodo_finale
                test_per_fin = data_list_toimp[sing_rec].periodo_finale

                if test_per_fin == "" or test_per_fin == None:
                    per_fin = None
                else:
                    per_fin = int(data_list_toimp[sing_rec].periodo_finale)

                    # blocco fase_finale
                test_fas_fin = data_list_toimp[sing_rec].fase_finale

                if test_fas_fin == "" or test_fas_fin == None:
                    fase_fin = None
                else:
                    fase_fin = int(data_list_toimp[sing_rec].fase_finale)

                try:
                    data = self.DB_MANAGER_write.insert_values_tafonomia(

                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        str(data_list_toimp[sing_rec].sito),
                        int(data_list_toimp[sing_rec].nr_scheda_taf),
                        str(data_list_toimp[sing_rec].sigla_struttura),
                        int(data_list_toimp[sing_rec].nr_struttura),
                        int(data_list_toimp[sing_rec].nr_individuo),
                        str(data_list_toimp[sing_rec].rito),
                        str(data_list_toimp[sing_rec].descrizione_taf),
                        str(data_list_toimp[sing_rec].interpretazione_taf),
                        str(data_list_toimp[sing_rec].segnacoli),
                        str(data_list_toimp[sing_rec].canale_libatorio_si_no),
                        str(data_list_toimp[sing_rec].oggetti_rinvenuti_esterno),
                        str(data_list_toimp[sing_rec].stato_di_conservazione),
                        str(data_list_toimp[sing_rec].copertura_tipo),
                        str(data_list_toimp[sing_rec].tipo_conteni+++tore_resti),
                        str(data_list_toimp[sing_rec].orientamento_asse),
                        orientamento_azimut,
                        str(data_list_toimp[sing_rec].corredo_presenza),
                        str(data_list_toimp[sing_rec].corredo_tipo),
                        str(data_list_toimp[sing_rec].corredo_descrizione),
                        lunghezza_scheletro,
                        str(data_list_toimp[sing_rec].posizione_scheletro),
                        str(data_list_toimp[sing_rec].posizione_cranio),
                        str(data_list_toimp[sing_rec].posizione_arti_superiori),
                        str(data_list_toimp[sing_rec].posizione_arti_inferiori),
                        str(data_list_toimp[sing_rec].completo_si_no),
                        str(data_list_toimp[sing_rec].disturbato_si_no),
                        str(data_list_toimp[sing_rec].in_connessione_si_no),
                        str(data_list_toimp[sing_rec].caratteristiche),
                        per_iniz,
                        fase_iniz,
                        per_fin,
                        fase_fin,
                        str(data_list_toimp[sing_rec].datazione_estesa),
                        str(data_list_toimp[sing_rec].misure_tafonomia)
                    )
                        
                    self.DB_MANAGER_write.insert_data_session(data)
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
            QMessageBox.information(self, "Message", "Data Loaded")
        
        elif mapper_class_write == 'SCHEDAIND' :
            for sing_rec in range(len(data_list_toimp)):
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
                        data_list_toimp[sing_rec].osservazioni
                    )
                
                    self.DB_MANAGER_write.insert_data_session(data)
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
            QMessageBox.information(self, "Message", "Data Loaded")
        
        elif mapper_class_write == 'CAMPIONE':
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_values_campioni(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        data_list_toimp[sing_rec].sito,
                        data_list_toimp[sing_rec].area,
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
                    return 0
                
           
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                    
                    
                except :
                    
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    return 0
            #self.progress_bar.close()
            QMessageBox.information(self, "Message", "Data Loaded")


        
        
        elif mapper_class_write == 'PYARCHINIT_THESAURUS_SIGLE' :
            
            for sing_rec in range(len(data_list_toimp)):
                
                #try:
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
                for i in range(0,100):    
                    #time.sleep()
                    self.progress_bar.setValue(((i)/100)*100)
                 
                    QApplication.processEvents()
                    
                # except :
                    
                    # QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                    # return 0
            #self.progress_bar.close()
            QMessageBox.information(self, "Message", "Data Loaded")

    
    
    def on_pushButton_connect_pressed(self):
        
        # Defines parameter
        self.ip=str(self.lineEdit_ip.text())
        
       
        self.user=str(self.lineEdit_user.text())
        
        
        
        self.pwd=str(self.lineEdit_password.text())
        
       
        
  
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 
        srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
        self.lineEdit_2.insert("Connection succesfully stablished ......... ")
        dirlist = []
        dirlist = srv.listdir()
        for item in dirlist:
            self.listWidget.insertItem(0,item)
        
        
        # Download the file from the remote server
        #remote_file = '/home/data/ftp/demoliz/qgis/rep5/test.qgs'
        
        # with srv.cd('../'):             # still in .
            # srv.chdir('home')    # now in ./static
            # srv.chdir('data')      # now in ./static/here
            # srv.chdir('ftp')
            # srv.chdir('demoliz')    
            
            # srv.chdir('qgis')
            # srv.chdir('rep5')
            # self.listWidget.insertItem(0,"--------------------------------------------")
            
        
        #srv.close()
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
    def on_pushButton_change_dir_pressed(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 
        with pysftp.Connection(host="37.139.2.71", username="root",
        password="lizmap1",cnopts =cnopts ) as sftp:
        
            try:
                msg = sftp.cwd('/home') # Switch to a remote directory

                directory_structure = sftp.listdir_attr()# Obtain structure of the remote directory 

                for attr in directory_structure:
                    self.listWidget.insertItem(attr.filename, attr)

            except:
                self.lineEdit_2.insert("\n")
                self.lineEdit_2.insert("Unable to change directory")
            dirlist = []
            dirlist = sftp.listdir()
            for item in dirlist:
                self.listWidget.insertItem(0,item)


    def on_pushButton_disconnect_pressed(self):
        
       cnopts = pysftp.CnOpts()
       cnopts.hostkeys = None 
       srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
       self.lineEdit_2.insert("Connection Close ............. ")
       srv.close()
