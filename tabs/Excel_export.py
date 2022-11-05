
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
from __future__ import absolute_import
from builtins import str
from builtins import range

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis, QgsSettings
import psycopg2
from ..modules.utility.settings import Settings
import platform
import subprocess
import os
import sqlite3 as sq
import time
import pandas as pd
import numpy as np
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import *


from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Excel_export.ui'))


class pyarchinit_excel_export(QDialog, MAIN_DIALOG_CLASS):
    UTILITY = Utility()
    OS_UTILITY = Pyarchinit_OS_Utility()
    DB_MANAGER = ""
    HOME = ""
    DATA_LIST = []
    L=QgsSettings().value("locale/userLocale")[0:2]
    ##  if os.name == 'posix':
    ##      HOME = os.environ['HOME']
    ##  elif os.name == 'nt':
    ##      HOME = os.environ['HOMEPATH']
    ##
    ##  PARAMS_DICT={'SERVER':'',
    ##              'HOST': '',
    ##              'DATABASE':'',
    ##              'PASSWORD':'',
    ##              'PORT':'',
    ##              'USER':'',
    ##              'THUMB_PATH':''}
    DB_SERVER = "not defined"  ####nuovo sistema sort
    def __init__(self, iface):
        super().__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.iface = iface

        try:
            self.connect()
        except:
            pass
        self.charge_list()
        self.set_home_path()

        # self.load_dict()
        # self.charge_data()

    def connect(self):
        #QMessageBox.warning(self, "Alert",
                            #"Sistema sperimentale. Esporta le schede PDF in /vostro_utente/pyarchinit_Db_folder. Sostituisce i documenti gia' presenti. Se volete conservarli fatene una copia o rinominateli.",
                            #QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
                        
            if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
            elif self.L=='de':
                msg = "Verbindungsfehler {}. " \
                      " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
            else:
                msg = "The connection failed {}. " \
                      "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))        
        else:
            if self.L=='it':
                msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
            
            elif self.L=='de':
                msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)  
            else:
                msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)  
            
    def charge_list(self):
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'site', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

    def set_home_path(self):
        self.HOME = os.environ['PYARCHINIT_HOME']

    def on_pushButton_open_dir_pressed(self):
        path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_EXCEL_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def messageOnSuccess(self, printed):
        if printed:
            self.iface.messageBar().pushMessage("Exportation ok", Qgis.Success)
        else:
            self.iface.messageBar().pushMessage("Exportation falied", Qgis.Info)

    def db_search_DB(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value

        search_dict = {self.field: "'" + str(self.value) + "'"}

        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)

        return res
    
    
    def on_pushButton_exp_pdf_pressed(self):
        home = os.environ['PYARCHINIT_HOME']
        sito_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_EXCEL_folder")
        sito_location = str(self.comboBox_sito.currentText())
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(home, cfg_rel_path)
        conf = open(file_path, "r")
        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()    
        
        db_username = settings.USER
        host = settings.HOST
        port = settings.PORT
        database_password=settings.PASSWORD
        db_names = settings.DATABASE
        server=settings.SERVER    
        
        if server=='postgres':
            connessione ="dbname=%s user=%s host=%s password=%s port=%s" % (db_names,db_username,host,database_password,port)
            
            
            conn = psycopg2.connect(connessione)
            cur = conn.cursor()
            
            if self.checkBox_site.isChecked():
                name_= '%s' % (sito_location+'_Site_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, name_)
                cur.execute("SELECT * FROM site_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
                  
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                b=a.to_excel(writer, sheet_name='Sheet1')
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)
                        
            if self.checkBox_uw.isChecked():
                divelog_= '%s' % (sito_location+'_US_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, divelog_)
                cur.execute("SELECT * FROM us_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
          
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)    
                     
            if self.checkBox_art.isChecked():
                art_= '%s' % (sito_location+'_artefact_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, art_)
                cur.execute("SELECT * FROM inventario_materiali_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
       
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                
                    
            if self.checkBox_pottery.isChecked():
                pottery_= '%s' % (sito_location+'_Structures_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, pottery_)
                cur.execute("SELECT * FROM struttura_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])

                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                      
            
            if self.checkBox_anchor.isChecked():
                anchor_= '%s' % (sito_location+'_Taphonomy_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, anchor_)
                cur.execute("SELECT * FROM tomba_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
       
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)         
                    # for i in temp_data_list:
                    # self.DATA_LIST.append(i)
            QMessageBox.warning(self, "Message","Exported completed" , QMessageBox.Ok)
        
           
        
        elif server=='sqlite':        
            self.HOME = os.environ['PYARCHINIT_HOME']
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,"pyarchinit_Db_folder")
            
            file_path_sqlite = sqlite_DB_path+os.sep+db_names
            conn = sq.connect(file_path_sqlite)
            cur = conn.cursor()
            
            if self.checkBox_site.isChecked():
                name_= '%s' % (sito_location+'_Site_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, name_)
                cur.execute("SELECT * FROM site_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
                  
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                b=a.to_excel(writer, sheet_name='Sheet1')
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)
                        
            if self.checkBox_uw.isChecked():
                divelog_= '%s' % (sito_location+'_US_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, divelog_)
                cur.execute("SELECT * FROM us_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
          
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)    
                     
            if self.checkBox_art.isChecked():
                art_= '%s' % (sito_location+'_artefact_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, art_)
                cur.execute("SELECT * FROM inventario_materiali_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
       
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                
                    
            if self.checkBox_pottery.isChecked():
                pottery_= '%s' % (sito_location+'_Structures_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, pottery_)
                cur.execute("SELECT * FROM struttura_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])

                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                      
            
            if self.checkBox_anchor.isChecked():
                anchor_= '%s' % (sito_location+'_Taphonomy_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, anchor_)
                cur.execute("SELECT * FROM tomba_table where sito='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
       
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)         
                    # for i in temp_data_list:
                    # self.DATA_LIST.append(i)
            QMessageBox.warning(self, "Message","Exported completed" , QMessageBox.Ok)
            
    

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ui = pyarchinit_excel_export()
    ui.show()
    sys.exit(app.exec_())

