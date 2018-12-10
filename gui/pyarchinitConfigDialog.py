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
from builtins import range
from builtins import str
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog

from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication, QgsSettings, QgsProject

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.pyarchinit_db_update import DB_update
from modules.db.db_createdump import CreateDatabase, RestoreSchema, DropDatabase
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

from modules.utility.pyarchinit_print_utility import Print_utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'pyarchinitConfigDialog.ui'))


class pyArchInitDialog_Config(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    
    HOME = os.environ['PYARCHINIT_HOME']

    PARAMS_DICT = {'SERVER': '',
                   'HOST': '',
                   'DATABASE': '',
                   'PASSWORD': '',
                   'PORT': '',
                   'USER': '',
                   'THUMB_PATH': '',
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

        self.graphviz_bin = s.value('pyArchInit/graphvizBinPath', None, type=str)
        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)

        if Pyarchinit_OS_Utility.checkGraphvizInstallation():
            self.pushButtonGraphviz.setEnabled(False)
            self.pbnSaveEnvironPath.setEnabled(False)
            self.lineEditGraphviz.setEnabled(False)

        self.selectorCrsWidget.setCrs(QgsProject.instance().crs())
        self.selectorCrsWidget_sl.setCrs(QgsProject.instance().crs())

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

    def setEnvironPath(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.graphviz_bin)
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

        
        RestoreSchema(db_url,view_file).restore_schema()
       

        
        

        
        
    def on_pushButton_upd_sqlite_pressed(self):
       
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'pyarchinit_update_sqlite.sql')
        
        view_file1 = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   '2.sql')
        
        view_file3 = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   '3.sql')
        
        view_file4 = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   '4.sql')
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)
        
        conn = Connection()
        db_url = conn.conn_str()

        
        RestoreSchema(db_url,view_file).restore_schema()
        RestoreSchema(db_url,view_file1).restore_schema()
        RestoreSchema(db_url,view_file3).restore_schema()
        RestoreSchema(db_url,view_file4).restore_schema()
        
               
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
    
    
    
    def on_pushButton_crea_layer_pressed(self):
        import time
        try:
            qgis_dir = QgsApplication.qgisSettingsDirPath()
            module_path_rel = os.path.join(os.sep, 'python', 'plugins', 'pyarchinit', 'modules', 'utility',
                                           'dbfiles', 'pyarchinit_postgis15_empty.dump')
            module_path = '{}{}'.format(qgis_dir, module_path_rel)
            postgis15 = os.popen(
                "pg_restore --host localhost --port %s --username postgres --dbname %s --role postgres --no-password  --verbose %s" % (
                    self.lineEdit_port_db.text(), self.lineEdit_dbname.text(), module_path))
            barra2 = self.pyarchinit_progressBar_template
            barra2.setMinimum(0)
            barra2.setMaximum(9)
            for a in range(10):
                time.sleep(1)
                barra2.setValue(a)
            QMessageBox.warning(self, "ok", "Installazione avvenuta con successo", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "opss", "qualcosa non va" + str(e), QMessageBox.Ok)

    def on_pushButton_crea_layer_2_pressed(self):
        import time
        try:
            qgis_dir = QgsApplication.qgisSettingsDirPath()
            module_path_rel = os.path.join(os.sep, 'python', 'plugins', 'pyarchinit', 'modules', 'utility',
                                           'dbfiles', 'pyarchinit_postgis20_empty.dump')
            module_path = '{}{}'.format(qgis_dir, module_path_rel)
            postgis15 = os.popen(
                "pg_restore --host localhost --port %s --username postgres --dbname %s --role postgres --no-password  --verbose %s" % (
                    self.lineEdit_port_db.text(), self.lineEdit_dbname.text(), module_path))
            barra2 = self.pyarchinit_progressBar_template
            barra2.setMinimum(0)
            barra2.setMaximum(9)
            for a in range(10):
                time.sleep(1)
                barra2.setValue(a)
            QMessageBox.warning(self, "ok", "Installazione avvenuta con successo", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "opss", "qualcosa non va" + str(e), QMessageBox.Ok)

    def on_pushButton_crea_db_sqlite_pressed(self):
        try:
            conn = Connection()
            conn_str = conn.conn_str()
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.DB_MANAGER.execute_sql_create_spatialite_db()
        except:
            QMessageBox.warning(self, "Alert",
                                "L'installazione e' fallita. Riavvia Qgis. Se l'errore persiste verifica che i layer non siano gia' installati oppure sia stia usando un db Postgres",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Alert", "L'installazione ha avuto successo!", QMessageBox.Ok)

    def try_connection(self):
        conn = Connection()
        conn_str = conn.conn_str()

        self.DB_MANAGER = Pyarchinit_db_management(
            conn_str)  # sqlite:///\Users\Windows\pyarchinit_DB_folder\pyarchinit_db.sqlite

        test = self.DB_MANAGER.connection()
        if self.L=='it':
            if test:
                QMessageBox.warning(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
            # elif test.find("create_engine") != -1:
            #     QMessageBox.warning(self, "Alert",
            #                         "Verifica i parametri di connessione. <br> Se sono corretti RIAVVIA QGIS",
            #                         QMessageBox.Ok)
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
                'US': 'id_us',
                'UT': 'id_ut',
                'SITE': 'id_sito',
                'PERIODIZZAZIONE': 'id_perfas',
                'INVENTARIO_MATERIALI': 'id_invmat',
                'STRUTTURA': 'id_struttura',
                'TAFONOMIA': 'id_tafonomia',
                'SCHEDAIND': 'id_scheda_ind',
                'CAMPIONE': 'id_campione',
                'DOCUMENTAZIONE': 'id_documentazione'
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
                'DOKUMENTATION': 'id_documentazione'
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
                'DOCUMENTATION': 'id_documentazione'
            }       
        # creazione del cursore di lettura
        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
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
            sqlite_DB_path = '{}{}{}'.format(home, os.sep,
                                             "pyarchinit_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\pyarchinit_san_marco\\" fare modifiche anche in pyarchinit_pyqgis
            dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_read["db_name"]
            conn_str_read = "%s:///%s" % (conn_str_dict_read["server"], dbname_abs)
            QMessageBox.warning(self, "Alert", str(conn_str_dict_read["db_name"]), QMessageBox.Ok)
        ####SI CONNETTE AL DATABASE
        self.DB_MANAGER_read = Pyarchinit_db_management(conn_str_read)
        test = self.DB_MANAGER_read.connection()
        if test:
            QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
        elif test.find("create_engine") != -1:
            QMessageBox.warning(self, "Alert",
                                "Try connection parameter. <br> If they are correct restart QGIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Alert", "Connection error: <br>" + test, QMessageBox.Ok)

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
        # creazione del cursore di scrittura

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
            sqlite_DB_path = '{}{}{}'.format(home, os.sep,
                                             "pyarchinit_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\pyarchinit_san_marco\\" fare modifiche anche in pyarchinit_pyqgis
            dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_write["db_name"]
            conn_str_write = "%s:///%s" % (conn_str_dict_write["server"], dbname_abs)
            QMessageBox.warning(self, "Alert", str(conn_str_dict_write["db_name"]), QMessageBox.Ok)
        ####SI CONNETTE AL DATABASE IN SCRITTURA

        self.DB_MANAGER_write = Pyarchinit_db_management(conn_str_write)
        test = self.DB_MANAGER_write.connection()
        test = str(test)

        if test:
            QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
        elif test.find("create_engine") != -1:
            QMessageBox.warning(self, "Alert",
                                "Try connection parameter. <br> If they are correct restart QGIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Alert", "Connection error: <br>" + test, QMessageBox.Ok)

        mapper_class_write = str(self.comboBox_mapper_read.currentText())
        ####inserisce i dati dentro al database

        #### US TABLE
        if mapper_class_write == 'US' or 'SE' or 'SU':
            for sing_rec in range(len(data_list_toimp)):
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
                    data_list_toimp[sing_rec].inclusi_materiali_usm
                )
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
        ####SITE TABLE
        if mapper_class_write == 'SITE' or 'AUSGRABUNGSSTÄTTE':
            for sing_rec in range(len(data_list_toimp)):
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
                    data_list_toimp[sing_rec].find_check)
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####PERIODIZZAZIONE TABLE
        if mapper_class_write == 'PERIODIZZAZIONE' or 'PERIODISIERUNG' or 'PERIODIATION':
            for sing_rec in range(len(data_list_toimp)):
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
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####INVENTARIO MATERIALI TABLE
        if mapper_class_write == 'INVENTARIO_MATERIALI' or 'ARTEFAKT-INVENTAR' or 'ARTEFACT':
            for sing_rec in range(len(data_list_toimp)):
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
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####STRUTTURA TABLE
        if mapper_class_write == 'STRUTTURA' or 'STRUKTUREN' or'STRUCTURE':
            for sing_rec in range(len(data_list_toimp)):
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
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####TAFONOMIA TABLE
        if mapper_class_write == 'TAFONOMIA' or 'TAPHONOMIE' or 'TAPHONOMY':
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
                    str(data_list_toimp[sing_rec].tipo_contenitore_resti),
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
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####INDIVIDUI TABLE
        if mapper_class_write == 'SCHEDAIND' or 'INDIVIDUEL' or 'INDIVIDUAL':
            for sing_rec in range(len(data_list_toimp)):
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
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####CAMPIONE TABLE
        if mapper_class_write == 'CAMPIONE' or 'BEISPIELS' or 'SAMPLE':
            for sing_rec in range(len(data_list_toimp)):
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
                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####DOCUMENTAZIONE TABLE
        if mapper_class_write == 'DOCUMENTAZIONE' or 'DOKUMENTATION' or 'DOCUMENTATION':
            for sing_rec in range(len(data_list_toimp)):
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

                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)
                ##              except Exception, e:
                ##                  e_str = str(e)
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
                ##                  if e_str.__contains__("Integrity"):
                ##                      msg = 'id_us' + " gia' presente nel database"
                ##                  else:
                ##                      msg = e
                ##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
                ##                  return 0
                ##
                ####UT TABLE
        if mapper_class_write == 'UT' or 'TE' or 'TU':
            for sing_rec in range(len(data_list_toimp)):
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

                ##              try:
                self.DB_MANAGER_write.insert_data_session(data)


##              except Exception, e:
##                  e_str = str(e)
##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(e_str),  QMessageBox.Ok)
##                  if e_str.__contains__("Integrity"):
##                      msg = 'id_us' + " gia' presente nel database"
##                  else:
##                      msg = e
##                  QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
##                  return 0
##
