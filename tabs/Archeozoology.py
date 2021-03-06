#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        .................... stored in Postgres
                             -------------------
    begin                : 2010-12-01
    copyright            : (C) 2008 by Enzo Cocca
    email                : enzo.ccc@gmail.com
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
from builtins import range
from builtins import str
import os
from datetime import date
import psycopg2 
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.axes3d import *
    import matplotlib.pyplot as plt
    from matplotlib import cm

    #import numpy as np
    #from matplotlib.mlab import griddata
    #import scipy as sp
    #import scipy.interpolate
    from pyper import R

except:
    pass#import visvis
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidget, QListView, QFrame, QAbstractItemView, \
    QTableWidgetItem, QListWidgetItem
from qgis.PyQt.QtWidgets import QAction, QApplication, QDialog, QMessageBox,QFileDialog
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication, Qgis, QgsSettings


from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis_archeozoo import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
from ..gui.sortpanelmain import SortPanelMain
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Archeozoology.ui'))


class pyarchinit_Archeozoology(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    MSG_BOX_TITLE = "PyArchInit - pyarchinit_version 1.6 - Scheda Archeozoologia Quantificazioni"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config
    STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'fauna'
    MAPPER_TABLE_CLASS = "ARCHEOZOOLOGY"
    NOME_SCHEDA = "Scheda Archeozoologia"
    ID_TABLE = "id_"
    CONVERSION_DICT = {
    ID_TABLE:ID_TABLE, 
        "Code":"code",
        "N_rilievo":"n_rilievo",
        "N_codice":"n_codice",
        "Anno":"anno",
        "Sito":"sito",
        "Quadrato":"quadrato", 
        "US":"us",
        "Periodo":"periodo",
        "Fase":"fase", 
        "Specie":"specie",
        "Classe":"classe",
        "Ordine":"ordine",
        "Famiglia":"famiglia",
        "Elemento_g":"elemnto_anat_generico",
        "Elemento_sp":"elem_specifici",
        "Taglia":"taglia",
        "Eta":"eta",
        "Lato":"lato",
        "Lunghezza":"lunghezza",
        "Larghezza":"larghezza",
        "Spessore":"spessore",
        "Porzione":"porzione",
        "Peso":"peso",
        "Coordinata x":"coord_x",
        "Coordinata y":"coord_y",
        "Coordinata z":"coord_z",
        "Modificazioni":"azione",
        "Tipologia osso":"modulo_osso"
        }
    SORT_ITEMS = [
        ID_TABLE,
        "Code",
        "N_rilievo",
        "N_codice",
        "Anno",
        "Sito",
        "Quadrato",
        "US",
        "Periodo",
        "Fase",
        "Specie",
        "Classe",
        "Ordine",
        "Famiglia",
        "Elemento_g",
        "Elemento_sp",
        "Taglia",
        "Eta",
        "Lato",
        "Lunghezza",
        "Larghezza",
        "Spessore",
        "Porzione",
        "Peso",
        "Coordinata x",
        "Coordinata y",
        "Coordinata z",
        "Modificazioni",
        "Tipologia osso"
        ]

    TABLE_FIELDS = [
        'code',
        'n_rilievo',
        'n_codice',
        'anno',
        'sito',
        'quadrato', 
        'us',
        'periodo',
        'fase', 
        'specie',
        'classe',
        'ordine',
        'famiglia',
        'elemnto_anat_generico',
        'elem_specifici',
        'taglia',
        'eta',
        'lato',
        'lunghezza',
        'larghezza',
        'spessore',
        'porzione',
        'peso',
        'coord_x',
        'coord_y',
        'coord_z',
        'azione',
        'modulo_osso'
        ]
    
    
    HOME = os.environ['PYARCHINIT_HOME'] 
    DB_SERVER = "not defined"  ####nuovo sistema sort

    def __init__(self, iface):
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(self.iface)
        QDialog.__init__(self)
        self.setupUi(self)
        self.currentLayerId = None
        
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)
        self.fill_fields()
        
        self.set_sito()
        self.msg_sito()
    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_new_search.setEnabled(n)

        self.pushButton_search_go.setEnabled(n)
        
        self.pushButton_sort.setEnabled(n)
        
        self.calcola.setEnabled(n)

        self.mappa.setEnabled(n)

        self.report.setEnabled(n)

        self.matrix.setEnabled(n)

        self.tre_d.setEnabled(n)

        self.hist.setEnabled(n)

        self.coplot.setEnabled(n)

        self.automap.setEnabled(n)
        
        self.boxplot.setEnabled(n)

        self.hist_period.setEnabled(n)

        self.clipper.setEnabled(n)

        
        self.Help_button.setEnabled(n)

    def enable_button_search(self, n):
        self.pushButton_connect.setEnabled(n)

        self.pushButton_new_rec.setEnabled(n)

        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_save.setEnabled(n)

        self.pushButton_sort.setEnabled(n)

        self.calcola.setEnabled(n)

        self.mappa.setEnabled(n)

        self.report.setEnabled(n)

        self.matrix.setEnabled(n)

        self.tre_d.setEnabled(n)

        self.hist.setEnabled(n)

        self.coplot.setEnabled(n)

        self.automap.setEnabled(n)

        self.boxplot.setEnabled(n)

        self.hist_period.setEnabled(n)

        self.clipper.setEnabled(n)

        self.Help_button.setEnabled(n)


    def on_Help_button_pressed(self):
        
        
        pass#form = helpform.HelpForm("help.html", self)
        #form.show()
        
        
    def on_hist_graph_pressed(self):
        
        if self.lineEdit_sql.text() == "":
            lineEdit_sql = ''
        else:
            lineEdit_sql = str(self.lineEdit_sql.text())
        conn_ = Connection()
        conn_str = conn_.conn_str()
        # prepare a cursor
        #import psycopg2
        # conn = psycopg2.connect("host='%s' dbname='%s' password='%s' user='%s' port=%d") % (str(self.host.currentText()), str(self.db.text()), str(self.password.text()), str(self.user.currentText()), int(self.port.currentText()))
        conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        )
        return conn

        
        cur = conn.cursor()
        # execute the query
        cur.execute('(%s)' % str(self.lineEdit_sql.text()))
        data = cur.fetchall()
        cur.close()
        conn.close()
        # graph code
        a = zip(*data)
        plt.hist(a)
        plt.title ('(%s)' % str(self.lineEdit_2.text()))
        plt.xlabel ('(%s)' % str(self.lineEdit_3.text()))
        plt.ylabel ('(%s)' % str(self.lineEdit_4.text()))
        #plt.bar(cursor)
        plt.show()



    def on_pushButton_connect_pressed(self):

        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            self.DB_SERVER = "sqlite"
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if self.DATA_LIST:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "SE-MSE formular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples SU-WSU" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)    
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
            
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
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        
        try:
            sito_vl.remove('')
            
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        

    def msg_sito(self):
        conn = Connection()
        
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        if bool(self.comboBox_sito.currentText())==sito_set_str:
            QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.Ok) 
        
        
        elif not bool(self.comboBox_sito.currentText()):
            pass
            
        else:    
            QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito pertanto vedrai tutti i record se il db non è vuoto",QMessageBox.Ok) 
    
    
    def set_sito(self):
        conn = Connection()
            
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        try:
            if bool (sito_set_str):
                
                
            
           
            
                search_dict = {
                    'sito': "'" + str(sito_set_str) + "'"}  # 1 - Sito
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)

                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                
            else:
                
                pass#
                
        except:
            QMessageBox.information(self, "Attenzione" ,"Non esiste questo sito: "'"'+ str(sito_set_str) +'"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",QMessageBox.Ok)  
    def on_pushButton_sort_pressed(self):
        dlg = SortPanelMain(self)
        dlg.insertItems(self.SORT_ITEMS)
        dlg.exec_()

        items,order_type = dlg.ITEMS, dlg.TYPE_ORDER

        self.SORT_ITEMS_CONVERTED = []
        for i in items:
            self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

        self.SORT_MODE = order_type
        self.empty_fields()

        id_list = []
        for i in self.DATA_LIST:
            id_list.append(eval("i." + self.ID_TABLE))
        self.DATA_LIST = []

        temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS, self.ID_TABLE)

        for i in temp_data_list:
            self.DATA_LIST.append(i)
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<type 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR

        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "o"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
        self.fill_fields()
        
        
    def on_toolButtonGis_toggled(self):
        if self.toolButtonGis.isChecked() == True:
            QMessageBox.warning(self, "Messaggio", "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Messaggio", "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS", QMessageBox.Ok)
    
    def on_pushButton_new_rec_pressed(self):
        if self.DATA_LIST:
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if self.DATA_LIST:
                        if self.records_equal_check() == 1:
                            if self.L=='it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                                                   "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.Ok | QMessageBox.Cancel))
                            elif self.L=='de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                                   QMessageBox.Ok | QMessageBox.Cancel))
                                                                   
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "The record has been changed. Do you want to save the changes?",
                                                                   QMessageBox.Ok | QMessageBox.Cancel))
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEnable(["self.comboBox_sito"],"True")
            self.setComboBoxEnable(["self.lineEdit_quadrato"],"True")
            self.setComboBoxEnable(["self.lineEdit_us"],"True")
            self.setComboBoxEnable(["self.lineEdit_periodo"],"True")            
            self.setComboBoxEnable(["self.lineEdit_fase"],"True")

            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        #save record
        if self.BROWSE_STATUS == "b":
            if self.records_equal_check() == 1:
                self.update_if(QMessageBox.warning(self,'ATTENZIONE',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.enable_button(1)
            else:
                QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",  QMessageBox.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.set_sito()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
                    self.fill_fields(self.REC_CORR)
                    self.setComboBoxEnable(["self.comboBox_sito"],"False")
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
            test = 1
        elif EC.data_is_empty(str(self.lineEdit_quadrato.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Quadrato. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
            test = 1
        elif EC.data_is_empty(str(self.lineEdit_us.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo US. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
            test = 1
        elif EC.data_is_empty(str(self.lineEdit_periodo.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Periodo. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
            test = 1

        elif EC.data_is_empty(str(self.lineEdit_fase.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Fase. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
            test = 1  
        return test

    def insert_new_rec(self):
        
        if self.lineEdit_code.text() == "":
            code = None
        else:
            code = str(self.lineEdit_code.text())


        if self.lineEdit_n_riliev.text() == "":
            n_rilievo = None
        else:
            n_rilievo = str(self.lineEdit_n_riliev.text())

        if self.lineEdit_n_inv.text() == "":
            n_codice = None
        else:
            n_codice = str(self.lineEdit_n_inv.text())
        if self.lineEdit_us.text() == "":
            us = None
        else:
            us = int(self.lineEdit_us.text())


        if self.lineEdit_quadrato.text() == "":
            quadrato = None
        else:
            quadrato = str(self.lineEdit_quadrato.text())

        if self.lineEdit_periodo.text() == "":
            periodo = None
        else:
            periodo = int(self.lineEdit_periodo.text())
               

        if self.lineEdit_fase.text() == "":
            fase = None
        else:
            fase = int(self.lineEdit_fase.text())


        if self.lineEdit_coord_x.text() == "":
            coord_x = None
        else:
            coord_x = float(self.lineEdit_coord_x.text())

        #f = open("test_coord.txt", "w")
        #f.write(str(coord_x))
        #f.close()

        if self.lineEdit_coord_y.text() == "":
            coord_y = None
        else:
            coord_y = float(self.lineEdit_coord_y.text())

        if self.lineEdit_coord_z.text() == "":
            coord_z = None
        else:
            coord_z = float(self.lineEdit_coord_z.text())

        

        if self.lineEdit_code.text() == "":
            code = None
        else:
            code = int(self.lineEdit_code.text())

        if self.comboBox_ordine.currentText() == "":
            ordine = None
        else:
            ordine = str(self.comboBox_ordine.currentText())

        if self.comboBox_specie.currentText() == "":
            specie = None
        else:
            specie = str(self.comboBox_specie.currentText())

        if self.comboBox_famiglia.currentText() == "":
            famiglia = None
        else:
            famiglia = str(self.comboBox_famiglia.currentText())

        if self.comboBox_classe.currentText() == "":
            classe = None
        else:
            classe = str(self.comboBox_classe.currentText())

        if self.lineEdit_elem_sp.text() == "":
            elem_specifici = None
        else:
            elem_specifici = str(self.lineEdit_elem_sp.text())

        if self.comboBox_elem_gen.currentText() == "":
            elemnto_anat_generico = None
        else:
            elemnto_anat_generico = str(self.comboBox_elem_gen.currentText())   

        if self.lineEdit_azione.text() == "":
            azione = None
        else:
            azione = str(self.lineEdit_azione.text())

        if self.lineEdit_mod_osso.text() == "":
            modulo_osso = None
        else:
            modulo_osso = str(self.lineEdit_mod_osso.text())

        if self.lineEdit_peso.text() == "":
            peso = None
        else:
            peso = float(self.lineEdit_peso.text())

        if self.comboBox_lungh.currentText() == "":
            lunghezza = None
        else:
            lunghezza = str(self.comboBox_lungh.currentText())

        if self.comboBox_largh.currentText() == "":
            larghezza = None
        else:
            larghezza = str(self.comboBox_largh.currentText())
            
        if self.comboBox_spess.currentText() == "":
            spessore = None
        else:
            spessore = str(self.comboBox_spess.currentText())


        try:
            data = self.DB_MANAGER.insert_values_archeozoology(
            self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
            code,
            str(self.lineEdit_n_riliev.text()),
            str(self.lineEdit_n_inv.text()),
            str(self.lineEdit_anno.text()),
            str(self.comboBox_sito.currentText()),
            str(self.lineEdit_quadrato.text()),
            us,
            periodo,
            fase,
            str(self.comboBox_specie.currentText()),
            str(self.comboBox_classe.currentText()),
            str(self.comboBox_ordine.currentText()),
            str(self.comboBox_famiglia.currentText()),
            str(self.comboBox_elem_gen.currentText()),
            str(self.lineEdit_elem_sp.text()),
            str(self.lineEdit_taglia.text()),
            str(self.lineEdit_eta.text()),
            str(self.lineEdit_porzione.text()),
            str(self.comboBox_lato.currentText()),
            str(self.comboBox_lungh.currentText()),
            str(self.comboBox_largh.currentText()),
            str(self.comboBox_spess.currentText()),
            peso,
            coord_x,
            coord_y,
            coord_z)
            str(self.lineEdit_azione.text()),
            str(self.lineEdit_mod_osso.text())      
            
            
            
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
            if e_str.__contains__("Integrity"):
                msg = self.ID_TABLE + " gia' presente nel database"
            else:
                msg = e
            QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n"+ str(msg),  QMessageBox.Ok)
            return 0
        except Exception as e:
            QMessageBox.warning(self, "Errore", "Attenzione 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0

    def on_pushButton_view_all_pressed(self):
        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<type 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.label_sort.setText(self.SORTED_ITEMS["n"])

    #records surf functions
    def on_pushButton_first_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))

        self.REC_CORR = self.REC_CORR-1
        if self.REC_CORR == -1:
            self.REC_CORR = 0
            QMessageBox.warning(self, "Errore", "Sei al primo record!",  QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

    def on_pushButton_next_rec_pressed(self):

        if self.records_equal_check() == 1:
            self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))

        self.REC_CORR = self.REC_CORR+1
        if self.REC_CORR >= self.REC_TOT:
            self.REC_CORR = self.REC_CORR-1
            QMessageBox.warning(self, "Errore", "Sei all'ultimo record!",  QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

    def on_pushButton_delete_pressed(self):
        msg = QMessageBox.warning(self,"Attenzione!!!","Vuoi veramente eliminare il record? \n L'azione e' irreversibile", QMessageBox.Cancel,1)
        if msg != 1:
            QMessageBox.warning(self,"Messagio!!!","Azione Annullata!")
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records() #charge records from DB
                QMessageBox.warning(self,"Messaggio!!!","Record eliminato!")
                self.charge_list()
            except:
                QMessageBox.warning(self, "Attenzione", "Il database e' vuoto!",  QMessageBox.Ok)

            if bool(self.DATA_LIST) == False:

                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
            #check if DB is empty
            if bool(self.DATA_LIST) == True:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.set_sito()
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
        self.label_sort.setText(self.SORTED_ITEMS["n"])

    def on_pushButton_new_search_pressed(self):
        #self.setComboBoxEditable()
        self.enable_button_search(0)

        #set the GUI for a new search
        if self.BROWSE_STATUS != "f":
            self.BROWSE_STATUS = "f"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.set_rec_counter('','')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.setComboBoxEnable(["self.comboBox_sito"],"True")
            self.setComboBoxEnable(["self.lineEdit_periodo"],"True")
            self.setComboBoxEnable(["self.lineEdit_us"],"True")
            self.setComboBoxEnable(["self.lineEdit_quadrato"],"True")
            self.setComboBoxEnable(["self.lineEdit_fase"],"True")
    

    








        
    def on_toolButton_esp_generale_pressed(self):
        self.percorso = QFileDialog.getExistingDirectory(self,'Choose Save Directory')
        self.lineEdit_esp_generale.setText(self.percorso)       
        
    def on_calcola_pressed(self):#####modifiche apportate per il calcolo statistico con R
        
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        #return test
        
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())
        
        
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"          
        else:
            self.close()
            
        if self.bos.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.calcinati.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.camoscio.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.combuste.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.coni.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.pdi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.capriolo.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.cervi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.stambecco.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.strie.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.canidi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.ursidi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.megacero.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
            
        if self.psill.text() == "":
            psill = 0
        else:
            psill = int(self.psill.text())

        if self.model.currentText() == "":
            model = ''
        else:
            model = str(self.model.currentText())

        if self.rang.text() == "":
            rang = ''
        else:
            rang = str(self.rang.text())
            
        if self.nugget_2.text() == "":
            nugget_2 = 0
        else:
            nugget_2 = int(self.nugget_2.text())
            
        if self.cutoff.text() == "":
            cutoff = 0
        else:
            cutoff = int(self.cutoff.text())
            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
        
        if self.set_size_plot.text() == "":
            set_size_plot = 0
        else:
            set_size_plot = int(self.set_size_plot.text())


        if self.c1.currentText() == "":
            c1 = ''
        else:
            c1 = str(self.c1.currentText())
        if self.c2.currentText() == "":
            c2 = ''
        else:
            c2 = str(self.c2.currentText())
        if self.c3.currentText() == "":
            c3 = ''
        else:
            c3 = str(self.c3.currentText())
        if self.c4.currentText() == "":
            c4 = ''
        else:
            c4 = str(self.c4.currentText())
        if self.c5.currentText() == "":
            c5 = ''
        else:
            c5 = str(self.c5.currentText())
        if self.c6.currentText() == "":
            c6 = ''
        else:
            c6 = str(self.c6.currentText())
        if self.c7.currentText() == "":
            c7 = ''
        else:
            c7 = str(self.c7.currentText())
        if self.c8.currentText() == "":
            c8 = ''
        else:
            c8 = str(self.c8.currentText())
        if self.c9.currentText() == "":
            c9 = ''
        else:
            c9 = str(self.c9.currentText())
        if self.c10.currentText() == "":
            c10 = ''
        else:
            c10 = str(self.c10.currentText())
        if self.c11.currentText() == "":
            c11 = ''
        else:
            c11 = str(self.c11.currentText())
        if self.c12.currentText() == "":
            c12 = ''
        else:
            c12 = str(self.c12.currentText())
        if self.c13.currentText() == "":
            c13 = ''
        else:
            c13 = str(self.c13.currentText())


        if self.lineEdit_bos_2.currentText() == "":
            lineEdit_bos_2 = ""
        else:
            lineEdit_bos_2 = str(self.lineEdit_bos_2.currentText())
        if self.lineEdit_calcinati_2.text() == "":
            lineEdit_calcinati_2 = ""
        else:
            lineEdit_calcinati_2 = str(self.lineEdit_calcinati_2.text())
        if self.lineEdit_camoscio_2.text() == "":
            lineEdit_camoscio_2 = ""
        else:
            lineEdit_camoscio_2 = str(self.lineEdit_camoscio_2.text())
        if self.lineEdit_capriolo_2.text() == "":
            lineEdit_capriolo_2 = ""
        else:
            lineEdit_capriolo_2 = str(self.lineEdit_capriolo_2.text())
        if self.lineEdit_cervo_2.text() == "":
            lineEdit_cervo_2 = ""
        else:
            lineEdit_cervo_2 = str(self.lineEdit_cervo_2.text())
        if self.lineEdit_combusto_2.text() == "":
            lineEdit_combusto_2 = ""
        else:
            lineEdit_combusto_2 = str(self.lineEdit_combusto_2.text())
        if self.lineEdit_coni_2.text() == "":
            lineEdit_coni_2 = ""
        else:
            lineEdit_coni_2 = str(self.lineEdit_coni_2.text())
        if self.lineEdit_pdi_2.text() == "":
            lineEdit_pdi_2 = ""
        else:
            lineEdit_pdi_2 = str(self.lineEdit_pdi_2.text())
        if self.lineEdit_stambecco_2.text() == "":
            lineEdit_stambecco_2 = ""
        else:
            lineEdit_stambecco_2 = str(self.lineEdit_stambecco_2.text())
        if self.lineEdit_strie_2.text() == "":
            lineEdit_strie_2 = ""
        else:
            lineEdit_strie_2 = str(self.lineEdit_strie_2.text())
        if self.lineEdit_canidi_2.text() == "":
            lineEdit_canidi_2 = ""
        else:
            lineEdit_canidi_2 = str(self.lineEdit_canidi_2.text())
        if self.lineEdit_ursidi_2.text() == "":
            lineEdit_ursidi_2 = ""
        else:
            lineEdit_ursidi_2 = str(self.lineEdit_ursidi_2.text())
        if self.lineEdit_megacero_2.text() == "":
            lineEdit_megacero_2 = ""
        else:
            lineEdit_megacero_2 = str(self.lineEdit_megacero_2.text())
        if self.lineEdit_width.text() == "":
            lineEdit_width = ""
        else:
            lineEdit_width = str(self.lineEdit_width.text())

        if self.kappa.text() == "":
            kappa = ""
        else:
            kappa = str(self.kappa.text())
    
            # bottone per creare semivariogrammi
                #dlg = QuantPanelMain(self)
        #dlg.exec_()
        #dataset = []
                
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(gstat)')
        r('drv <- dbDriver("PostgreSQL")')
        n = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (n)
        con = "r('archezoology_table<-dbGetQuery(con,\"select * from tot_specie_terrestre where fase = %d AND bos_bison IS NOT NULL\")')" % int(self.DATA_LIST[i].fase)
        eval (con)
        if self.bos.isChecked() == True:            
            x1="r('VGM_PARAM_A3 <- gstat(id=\"%s\", formula=%s~1,locations=~coord_x+coord_y, data=archezoology_table, nmax = 10)')" % (str(self.lineEdit_bos_2.currentText()),str(self.c1.currentText()))
            eval(x1)
        else:
            pass
        if self.calcinati.isChecked() == True:
            x2="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y, archezoology_table, nmax = 10)')"% (str(self.lineEdit_calcinati_2.text()),str(self.c2.currentText()))
            eval (x2)
        else:
            pass
        if self.camoscio.isChecked() == True:
            x3="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3,\"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_camoscio_2.text()),str(self.c3.currentText()))
            eval (x3)
        else:
            pass    
        if self.capriolo.isChecked() == True:   
            x4="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_capriolo_2.text()),str(self.c4.currentText()))
            eval (x4)
        else:
            pass
        if self.cervi.isChecked() == True:
            x5="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_cervo_2.text()),str(self.c5.currentText()))
            eval (x5)
        else:
            pass
        if self.combuste.isChecked() == True:   
            x6="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_combusto_2.text()),str(self.c6.currentText()))
            eval (x6)
        else:
            pass
        if self.coni.isChecked() == True:   
            x7="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_coni_2.text()),str(self.c7.currentText()))
            eval (x7)
        else:
            pass
        if self.pdi.isChecked() == True:    
            x8="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_pdi_2.text()),str(self.c8.currentText()))
            eval (x8)
        else:
            pass
        if self.stambecco.isChecked() == True:  
            x9="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_stambecco_2.text()),str(self.c9.currentText()))
            eval (x9)
        else:
            pass
        if self.strie.isChecked() == True:  
            x10="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_strie_2.text()),str(self.c10.currentText()))
        else:
            pass
        if self.megacero.isChecked() == True:   
            x11="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_megacero_2.text()),str(self.c13.currentText()))
            eval (x11)
        else:
            pass
        if self.ursidi.isChecked() == True:
            x12="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_ursidi_2.text()),str(self.c12.currentText()))
            eval(x12)
        else:
            pass
        if self.canidi.isChecked() == True:
            x13="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_canidi_2.text()),str(self.c11.currentText()))
            eval (x13)
        else:
            pass     
            c = "r('A3 <- gstat(VGM_PARAM_A3, fill.all=TRUE, model=vgm(%d,\"%s\",%s, nugget = %d, kappa= %s))')" % (int(self.psill.text()), str(self.model.currentText()), str(self.rang.text()), int(self.nugget_2.text()), str(self.kappa.text()))
            eval(c)
            d = "r('ESV_A3 <- variogram(A3, width=%s, cutoff=%d)')" % (str(self.lineEdit_width.text()), int(self.cutoff.text()))
            eval (d)
            
            fittare="r('VARMODEL_A3 = fit.lmc(ESV_A3, A3,model=vgm(%d,\"%s\",%s, nugget = %d, kappa= %s))')" % (int(self.psill.text()), str(self.model.currentText()), str(self.rang.text()), int(self.nugget_2.text()), str(self.kappa.text()))
            eval (fittare)          
            a = "r('png(\"%s/A%d_semivariogram.png\", width=%d, height=%d, res=400); plot(ESV_A3, model=VARMODEL_A3,xlab=,ylab=,pch=20, cex=0.7, col=\"red\", main=\"Linear Model of Coregionalization A%d\")')" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].us), int(self.set_size_plot.text()), int(self.set_size_plot.text()),int(self.DATA_LIST[i].us))
            eval(a)
            
        
    
    def on_mappa_pressed(self):#####modifiche apportate per il calcolo statistico con R
            
        
        self.ITEMS = []
        
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        #return test
        
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())
        
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"
        
    
        
            
        else:
            self.close()
        if self.bos.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.calcinati.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.camoscio.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.combuste.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.coni.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.pdi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.capriolo.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.cervi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.stambecco.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.strie.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.canidi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.ursidi.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass
        if self.megacero.isChecked() == True:
            self.TYPE_QUANT = ""            
        else:
            pass    
            
        if self.psill.text() == "":
            psill = 0
        else:
            psill = int(self.psill.text())

        if self.model.currentText() == "":
            model = ''
        else:
            model = str(self.model.currentText())

        if self.rang.text() == "":
            rang = ''
        else:
            rang = str(self.rang.text())
            
        if self.nugget_2.text() == "":
            nugget_2 = 0
        else:
            nugget_2 = int(self.nugget_2.text())
            
        if self.cutoff.text() == "":
            cutoff = 0
        else:
            cutoff = int(self.cutoff.text())
            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())


        if self.set_size_plot.text() == "":
            set_size_plot = 0
        else:
            set_size_plot = int(self.set_size_plot.text())

        if self.c1.currentText() == "":
            c1 = ''
        else:
            c1 = str(self.c1.currentText())
        if self.c2.currentText() == "":
            c2 = ''
        else:
            c2 = str(self.c2.currentText())
        if self.c3.currentText() == "":
            c3 = ''
        else:
            c3 = str(self.c3.currentText())
        if self.c4.currentText() == "":
            c4 = ''
        else:
            c4 = str(self.c4.currentText())
        if self.c5.currentText() == "":
            c5 = ''
        else:
            c5 = str(self.c5.currentText())
        if self.c6.currentText() == "":
            c6 = ''
        else:
            c6 = str(self.c6.currentText())
        if self.c7.currentText() == "":
            c7 = ''
        else:
            c7 = str(self.c7.currentText())
        if self.c8.currentText() == "":
            c8 = ''
        else:
            c8 = str(self.c8.currentText())
        if self.c9.currentText() == "":
            c9 = ''
        else:
            c9 = str(self.c9.currentText())
        if self.c10.currentText() == "":
            c10 = ''
        else:
            c10 = str(self.c10.currentText())
        if self.c11.currentText() == "":
            c11 = ''
        else:
            c11 = str(self.c11.currentText())
        if self.c12.currentText() == "":
            c12 = ''
        else:
            c12 = str(self.c12.currentText())
        if self.c13.currentText() == "":
            c13 = ''
        else:
            c13 = str(self.c13.currentText())


        if self.lineEdit_bos_2.currentText() == "":
            lineEdit_bos_2 = ""
        else:
            lineEdit_bos_2 = str(self.lineEdit_bos_2.currentText())
        if self.lineEdit_calcinati_2.text() == "":
            lineEdit_calcinati_2 = ""
        else:
            lineEdit_calcinati_2 = str(self.lineEdit_calcinati_2.text())
        if self.lineEdit_camoscio_2.text() == "":
            lineEdit_camoscio_2 = ""
        else:
            lineEdit_camoscio_2 = str(self.lineEdit_camoscio_2.text())
        if self.lineEdit_capriolo_2.text() == "":
            lineEdit_capriolo_2 = ""
        else:
            lineEdit_capriolo_2 = str(self.lineEdit_capriolo_2.text())
        if self.lineEdit_cervo_2.text() == "":
            lineEdit_cervo_2 = ""
        else:
            lineEdit_cervo_2 = str(self.lineEdit_cervo_2.text())
        if self.lineEdit_combusto_2.text() == "":
            lineEdit_combusto_2 = ""
        else:
            lineEdit_combusto_2 = str(self.lineEdit_combusto_2.text())
        if self.lineEdit_coni_2.text() == "":
            lineEdit_coni_2 = ""
        else:
            lineEdit_coni_2 = str(self.lineEdit_coni_2.text())
        if self.lineEdit_pdi_2.text() == "":
            lineEdit_pdi_2 = ""
        else:
            lineEdit_pdi_2 = str(self.lineEdit_pdi_2.text())
        if self.lineEdit_stambecco_2.text() == "":
            lineEdit_stambecco_2 = ""
        else:
            lineEdit_stambecco_2 = str(self.lineEdit_stambecco_2.text())
        if self.lineEdit_strie_2.text() == "":
            lineEdit_strie_2 = ""
        else:
            lineEdit_strie_2 = str(self.lineEdit_strie_2.text())
        if self.lineEdit_canidi_2.text() == "":
            lineEdit_canidi_2 = ""
        else:
            lineEdit_canidi_2 = str(self.lineEdit_canidi_2.text())
        if self.lineEdit_ursidi_2.text() == "":
            lineEdit_ursidi_2 = ""
        else:
            lineEdit_ursidi_2 = str(self.lineEdit_ursidi_2.text())
        if self.lineEdit_megacero_2.text() == "":
            lineEdit_megacero_2 = ""
        else:
            lineEdit_megacero_2 = str(self.lineEdit_megacero_2.text())
        if self.lineEdit_width.text() == "":
            lineEdit_width = ""
        else:
            lineEdit_width = str(self.lineEdit_width.text())

        if self.kappa.text() == "":
            kappa = ""
        else:
            kappa = str(self.kappa.text())
        
            # bottone per creare semivariogrammi
                #dlg = QuantPanelMain(self)
        #dlg.exec_()
        #dataset = []
                
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].us))
                    
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(gstat)')
        r('drv <- dbDriver("PostgreSQL")')
        n = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (n)
        con = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(self.DATA_LIST[i].us)
        eval (con)
        if self.bos.isChecked() == True:            
            x1= "r('VGM_PARAM_A3 <- gstat(id=\"%s\", formula=%s~1,locations=~coord_x+coord_y, data=archezoology_table, nmax = 10)')" % (str(self.lineEdit_bos_2.currentText()),str(self.c1.currentText()))
            eval (x1)
        else:
            pass
        if self.calcinati.isChecked() == True:
            x2="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y, archezoology_table, nmax = 10)')"% (str(self.lineEdit_calcinati_2.text()),str(self.c2.currentText()))
            eval (x2)
        else:
            pass
        if self.camoscio.isChecked() == True:
            x3="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3,\"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_camoscio_2.text()),str(self.c3.currentText()))
            eval (x3)
        else:
            pass    
        if self.capriolo.isChecked() == True:   
            x4="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_capriolo_2.text()),str(self.c4.currentText()))
            eval (x4)
        else:
            pass
        if self.cervi.isChecked() == True:
            x5="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_cervo_2.text()),str(self.c5.currentText()))
            eval (x5)
        else:
            pass
        if self.combuste.isChecked() == True:   
            x6="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_combusto_2.text()),str(self.c6.currentText()))
            eval (x6)
        else:
            pass
        if self.coni.isChecked() == True:   
            x7="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_coni_2.text()),str(self.c7.currentText()))
            eval (x7)
        else:
            pass
        if self.pdi.isChecked() == True:    
            x8="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_pdi_2.text()),str(self.c8.currentText()))
            eval (x8)
        else:
            pass
        if self.stambecco.isChecked() == True:  
            x9="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_stambecco_2.text()),str(self.c9.currentText()))
            eval (x9)
        else:
            pass
        if self.strie.isChecked() == True:  
            x10="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_strie_2.text()),str(self.c10.currentText()))
        else:
            pass
        if self.megacero.isChecked() == True:   
            x11="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_megacero_2.text()),str(self.c13.currentText()))
            eval (x11)
        else:
            pass
        if self.ursidi.isChecked() == True:
            x12="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_ursidi_2.text()),str(self.c12.currentText()))
            eval (x12)
        else:
            pass
        if self.canidi.isChecked() == True:
            x13="r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')"% (str(self.lineEdit_canidi_2.text()),str(self.c11.currentText()))
            eval (x13)
        else:
            pass     
            c = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, fill.all=TRUE, model=vgm(%d,\"%s\",%s, nugget = %d, kappa= %s))')" % (int(self.psill.text()), str(self.model.currentText()), str(self.rang.text()), int(self.nugget_2.text()), str(self.kappa.text()))
            eval(c)
            d = "r('ESV_A3 <- variogram(VGM_PARAM_A3, map=TRUE, width=%s, cutoff=%d)')" % (str(self.lineEdit_width.text()), int(self.cutoff.text()))
            eval (d)
            r('VARMODEL_A3 = fit.lmc(ESV_A3, VGM_PARAM_A3)')
            a = "r('png(\"%s/A%d_semivariogram_map.png\", width=%d, height=%d, res=400); plot(ESV_A3, threshold = 5, col.regions = terrain.colors, model=vgm(%d,\"%s\",%s,%d),xlab=,ylab=, main=\"Linear Model of Coregionalization A%d\")')" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].us), int(self.set_size_plot.text()), int(self.set_size_plot.text()),int(self.psill.text()), str(self.model.currentText()), str(self.rang.text()), int(self.nugget_2.text()),int(self.DATA_LIST[i].us))
            eval(a)
        

    

    def on_automap_pressed(self):#####modifiche apportate per il calcolo statistico con R
        
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"          
        else:
            self.close()
            
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())
            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
        
        if self.lineEdit_automap.currentText() == "":
            lineEdit_automap = ""
        else:
            lineEdit_automap = str(self.lineEdit_automap.currentText())

        if self.psill_2.text() == "":
            psill_2 = "NA"
        else:
            psill_2 = str(self.psill_2.text())

        if self.model_2.currentText() == "":
            model_2 = ''
        else:
            model_2 = str(self.model_2.currentText())

        if self.rang_2.text() == "":
            rang_2 = "NA"
        else:
            rang_2 = str(self.rang_2.text())
            
        if self.nugget_3.text() == "":
            nugget_3 = "NA"
        else:
            nugget_3 = str(self.nugget_3.text())

        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].us))
                    
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(gstat)')
        r('library(automap)')
        r('library(raster)')
        r('drv <- dbDriver("PostgreSQL")')
        n = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (n)
        con = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(self.DATA_LIST[i].us)
        eval (con)
        
        r('coordinates(archezoology_table) =~coord_x+coord_y')
        
        kr= "r('kriging_result = autoKrige(%s~1, archezoology_table,model=c(\"%s\"),fix.values = c(%s,%s,%s))')" % (str(self.lineEdit_automap.currentText()), str(self.model_2.currentText()), str(self.nugget_3.text()), str(self.rang_2.text()), str(self.psill_2.text()))
        eval(kr)

        plotkr = "r('png(\"%s/A%d_kriging_%s.png\", width=3500, height=3500, res=400); plot(kriging_result)')" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].us),  str(self.lineEdit_automap.currentText()))
        eval(plotkr)
        
        plot2= "r('png(\"%s/A%d_kriging_predict_%s.png\", width=3500, height=3500, res=400); automapPlot(kriging_result$krige_output, \"var1.pred\", sp.layout = list(\"sp.points\", archezoology_table))')" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].us),  str(self.lineEdit_automap.currentText()))
        eval(plot2)
        raster= "r('writeRaster(raster(kriging_result$krige_output),\"%s/A%d_kriging_predict_%s.tif\",\"GTiff\")')" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].us),  str(self.lineEdit_automap.currentText()))     
        eval(raster)
        add_map="self.iface.addRasterLayer(\"%s/A%d_kriging_predict_%s.tif\")" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].us),  str(self.lineEdit_automap.currentText()))
        eval(add_map)
        test= "r('verifica_errore <- krige.cv(%s~1, archezoology_table, model=vgm(%s,\"%s\",%s,%s),nfold=nrow(archezoology_table))')"% (str(self.lineEdit_automap.currentText()),  str(self.psill_2.text()), str(self.model_2.currentText()),str(self.rang_2.text()),str(self.nugget_3.text())) 
        eval(test)

        r('''
ME <- function(xv.obj){
     
     tmp <- xv.obj$residual
     
     return(sum(tmp)/length(tmp))}
MSE <- function(xv.obj){
     
     tmp <- xv.obj$residual
     
     return(sqrt((sum(tmp^2)/length(tmp))))
 }
MSDR <- function(xv.obj){
     
     e2 <- xv.obj$residual^2
     
     s2 <- xv.obj$var1.var
     
     msdr <- sum(e2/s2)/length(e2)
     
     return(msdr)}
''')
        error= "r('write.table(ME(verifica_errore),\"%s\ME.txt\");write.table(MSE(verifica_errore),\"%s\MSE.txt\");write.table(MSDR(verifica_errore),\"%s\MSDR.txt\")')" % (str(self.lineEdit_esp_generale.text()),str(self.lineEdit_esp_generale.text()),str(self.lineEdit_esp_generale.text()))
        eval(error)
        
    def on_report_pressed(self):
        
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"
        
    
        
            
        else:
            self.close()
            
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())
            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
            
        if self.plot.currentText() == "":
            plot = ""
        else:
            plot = str(self.plot.currentText())
            
        if self.l1.currentText() == "":
            l1 = ""
        else:
            l1 = int(self.l1.currentText()) 
            
        if self.l2.currentText() == "":
            l2 = ""
        else:
            l2 = str(self.l2.currentText()) 
            
        if self.size.text() == "":
            size = 1
        else:
            size = str(self.size.text())    
        
        
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    contatore += int(self.DATA_LIST[i].fase) #conteggio totale
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('library(R2HTML)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (con)
        query = "r('archezoology_table<-dbGetQuery(con,\"select distinct  coord_x, coord_y, a.fase, %s from fauna as a, tot_specie_terrestre as b where a.quadrato = b.quadrato and a.fase = %s \")')" % (str(self.plot.currentText()), int(self.DATA_LIST[i].fase))
        eval (query)    
        direc = "r('directory = setwd(\"%s\")')"% str(self.lineEdit_esp_generale.text())
        eval(direc) 
        test1 = "r('myfile<-file.path(getwd(),\"%s.html\")')"  % str(self.plot.currentText())
        eval(test1)
        test2 = "r('HTMLoutput=file.path(getwd(),\"%s.html\")')" % str(self.plot.currentText())
        eval (test2)
        nome = "r('graf=\"%s.png\"')"% str(self.plot.currentText())
        eval(nome)      
        r('png(file.path(getwd(),graf))')
        data = "r('dat <- rnorm(archezoology_table$%s)')"% str(self.plot.currentText())
        eval(data)
        r('cex_brks <- quantile(dat, c(0.25,0.5,0.75))')
        r('cex_size <- c(1)')
        cex = "r('cex=(archezoology_table$%s)/%d')" % (str(self.plot.currentText()), int(self.size.text()))
        eval(cex)
        r('''
            for (i in 1:3) {
                cex[is.na(cex) & dat<=cex_brks[[i]]] <- cex_size[[i]]
            }
            cex[is.na(cex)] <- cex_size[[4]]
            ''')
        plot ="r('plot(archezoology_table$coord_x,archezoology_table$coord_y, cex=cex,xlab=\"x axis\", ylab=\"y axis\", main=\"Pianta a dispersione di Fase%d - %s\", ylim=c(0,10), xlim=c(0,10), pch=1,col=\"red\")')" %(int(self.DATA_LIST[i].fase),str(self.plot.currentText())) 
        eval(plot)
        legend = "r('legend(9,10, pch = 0.1, c(1:%d),pt.cex = (1:%d/%d), cex = cex_size, col=\"red\")')" % (int(self.size.text()), int(self.size.text()), int(self.size.text()))
        eval (legend)
        r('dev.off()')
        test3= "r('tab<-summary(archezoology_table[%d:%d])')" % (int(self.l1.currentText()), int(self.l2.currentText()))
        eval(test3)

        r('''
            cat("<table border=0><td width=50%>",file=HTMLoutput, append=TRUE)
            HTMLInsertGraph(graf,file=HTMLoutput,caption="Grafico")
            cat("</td><td width=50%>",file=HTMLoutput, append=TRUE)
            HTML(tab,file=HTMLoutput)
            cat("</td></table>",file=HTMLoutput, append=TRUE)
            browseURL(myfile)
        ''')
                
    

    def on_hist_pressed(self):
        
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"
        
    
        
            
        else:
            self.close()
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())  
                            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
            
        if self.plot.currentText() == "":
            plot = ""
        else:
            plot = str(self.plot.currentText())
            
        if self.l1.currentText() == "":
            l1 = ""
        else:
            l1 = int(self.l1.currentText()) 
            
        if self.l2.currentText() == "":
            l2 = ""
        else:
            l2 = str(self.l2.currentText()) 
            
        if self.size.text() == "":
            size = 1
        else:
            size = str(self.size.text())    
        
        
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    contatore += int(self.DATA_LIST[i].fase) #conteggio totale
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (con)
        
        query = "r('archezoology_table<-dbGetQuery(con,\"select sum(\"aves\") as aves, sum(\"mammifera\") as mammifera from tot_classe where fase=%d and aves != 0 and mammifera != 0 group by fase, aves, mammifera order by fase asc\")')" % int(self.DATA_LIST[i].fase)
        eval (query)
        
        
        histogram= "r('png(\"%s/%s_histogram.png\", width=2500, height=2500, res=400); hist(archezoology_table$%s, col=\"yellow\",xlab=\"Quantità\", ylab=\"Frequenza\",labels=TRUE, main=\"Distribuzione di frequenza %s\")')" % (str(self.lineEdit_esp_generale.text()), str(self.plot.currentText()), str(self.plot.currentText()), str(self.plot.currentText()))
        eval(histogram)
        abline1= "r('abline(v=mean(archezoology_table$%s, na.rm=TRUE),col=\"red\", lwd=2)')"%str(self.plot.currentText())
        eval(abline1)
        abline2= "r('abline(v=mean(archezoology_table$%s, na.rm=TRUE)+sd(archezoology_table$%s, na.rm=TRUE),col=3, lty=2)')"%(str(self.plot.currentText()), str(self.plot.currentText()))
        eval(abline2)
        abline3= "r('abline(v=mean(archezoology_table$%s, na.rm=TRUE)-sd(archezoology_table$%s, na.rm=TRUE),col=3, lty=2)')"%(str(self.plot.currentText()), str(self.plot.currentText()))
        eval(abline3)
        
            




    def on_hist_period_pressed(self):
        
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())

        if self.c1_2.currentText() == "":
            c1_2 = ''
        else:
            c1_2 = str(self.c1_2.currentText())
        if self.c2_2.currentText() == "":
            c2_2 = ''
        else:
            c2_2 = str(self.c2_2.currentText())
        if self.c3_2.currentText() == "":
            c3_2 = ''
        else:
            c3_2 = str(self.c3_2.currentText())
        if self.c4_2.currentText() == "":
            c4_2 = ''
        else:
            c4_2 = str(self.c4_2.currentText())

        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
            
        if self.plot.currentText() == "":
            plot = ""
        else:
            plot = str(self.plot.currentText())
            
        if self.l1.currentText() == "":
            l1 = ""
        else:
            l1 = int(self.l1.currentText()) 
            
        if self.l2.currentText() == "":
            l2 = ""
        else:
            l2 = str(self.l2.currentText()) 
            
        if self.size.text() == "":
            size = 1
        else:
            size = str(self.size.text())    
        
        
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    contatore += int(self.DATA_LIST[i].fase) #conteggio totale
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (con)
        
        query =  "r('archezoology_table<-dbGetQuery(con,\"select * from tot_specie_terrestre where fase = %d\")')"%int(self.DATA_LIST[i].fase)
        eval (query)
        
        
        histogram1= "r('png(\"%s/A%d_test.png\", width=7000, height=3500, res=400)')" %(str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].fase))
        eval(histogram1)

        r('''
        
op <- par(mfcol=c(2,4),    #mfcol imposta 2 righe e 4 colonne di grafici
mar=c(3,2,2,4)+0.1)  #mar imposta i margini, dal basso in senso orario
do.it <- function (x) {
     hist(x, col='light blue', xlab="", ylab="", main="")  # istogrammi
     par(new = T)              #impongo nuovi parametri per la stessa figura
     plot(density(x), type='l', col='red', lwd=2, axes=F, main="",
          xlab="", ylab="")    #curva di densità
     axis(4)                   #asse secondario (= asse verticale a destra)
     x <- sort(x)              #ordina la variabile in maniera crescente
     q <- ppoints(length(x))   #genera la sequenza di probabilità per
                               #creare la curva cumulativa
     plot(q~x, type='l', xlab="",  ylab="", main="")    #curva cumulativa
     abline(h=c(.25,.5,.75), lty=3, lwd=3, col='blue')  #3 linee orizzontali
 }''')
 #Ora applico la funzione appena creata a 4 variabili del dataframe "dati.na"
        histogram2="r('do.it(archezoology_table$%s); title(\"%s\"); do.it(archezoology_table$%s); title(\"%s\"); do.it(archezoology_table$%s); title(\"%s\"); do.it(archezoology_table$%s); title(\"%s\"); par(op)')" % (str(self.c1_2.currentText()), str(self.c1_2.currentText()),str(self.c2_2.currentText()),str(self.c2_2.currentText()), str(self.c3_2.currentText()),str(self.c3_2.currentText()), str(self.c4_2.currentText()), str(self.c4_2.currentText()))
        eval(histogram2)
        

    def on_boxplot_pressed(self):
        
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1

        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())

        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
            
        if self.plot.currentText() == "":
            plot = ""
        else:
            plot = str(self.plot.currentText())
            
        
        
        
        
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    contatore += int(self.DATA_LIST[i].fase) #conteggio totale
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (con)
        
        query = "r('archezoology_table<-dbGetQuery(con,\"select * from tot_specie_terrestre where fase=%d\")')"%int(self.DATA_LIST[i].fase)
        eval (query)
        
        
        boxplot="r('png(\"%s/%s_boxplot.png\", width=3500, height=3500, res=400)')"%(str(self.lineEdit_esp_generale.text()),str(self.plot.currentText()))
        eval(boxplot)
        r('op=par(mar=c(0,5,0,0)); layout(matrix(c(1,1,1,2), nc=1))')
        codice= "r('a=archezoology_table$%s')"%str(self.plot.currentText())
        eval(codice)
        r('y=ppoints(length(a));x=sort(a);plot(y ~ x, type=\"l\", lwd=2, ylab=\"percent\", main="");abline(h=c(0,.25,.5,.75,1), col=1, lwd=2,lty=3);abline(v=quantile(a), col=2, lwd=2, lty=2);abline(v=mean(a), col=3, lwd=1.5, lty=4);points(quantile(a), c(0,.25,.5,.75,1), lwd=5,col=4);legend(1000,0.1,"legend");boxplot(a, horizontal=TRUE, notch=FALSE, col=5, lwd=2, cex=2);abline(v=quantile(a), col=2, lwd=2, lty=2);abline(v=mean(a), col=3, lwd=1.5, lty=4)')
        r('par(op)')

        

        
        
        
        #q= "r('abline(v=mean(archezoology_table$%s), lty=2, col=4, lwd=4)')"%str(self.plot.currentText())
        #eval(q)
        #w= "r('abline(v=mean(archezoology_table$%s)+sd(archezoology_table$%s), lty=3, col=3, lwd=2)')"%(str(self.plot.currentText()), str(self.plot.currentText()))
        #eval(w)
        #e= "r('abline(v=mean(archezoology_table$%s)­-sd(archezoology_table$%s), lty=3, col=3, lwd=2)')"%(str(self.plot.currentText()), str(self.plot.currentText()))
        #eval(e)
        #r= "r('abline(v=median(archezoology_table$%s), lty=4, col=2, lwd=2)')"%str(self.plot.currentText())
        #eval(r)
        #t= "r('rug(archezoology_table$%s, col=\"red\")')"%str(self.plot.currentText())
        #eval(t)





    def on_coplot_pressed(self):
        
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"
        
    
        
            
        else:
            self.close()
            
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())
            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
            
        if self.plot.currentText() == "":
            plot = ""
        else:
            plot = str(self.plot.currentText())
            
        if self.l1.currentText() == "":
            l1 = ""
        else:
            l1 = int(self.l1.currentText()) 
            
        if self.l2.currentText() == "":
            l2 = ""
        else:
            l2 = str(self.l2.currentText()) 
            
        if self.size.text() == "":
            size = 1
        else:
            size = str(self.size.text())    
        
        
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    contatore += int(self.DATA_LIST[i].fase) #conteggio totale
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
        
        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (con)
        query = "r('archezoology_table<-dbGetQuery(con,\"select distinct  coord_x, coord_y, a.fase, %s from fauna as a, tot_specie_terrestre as b where b.us=a.us and b.fase = a.fase \" )')" % str(self.plot.currentText())
        eval (query)    

        coplot= "r('png(\"%s/%s_coplot.png\", width=3500, height=3500, res=400); coplot(coord_y ~ coord_x | %s , data= archezoology_table, overlap=0, cex=1,pch=20,col=1)')" % (str(self.lineEdit_esp_generale.text()), str(self.plot.currentText()), str(self.plot.currentText()))
        eval(coplot)

    def on_clipper_pressed(self):
            #from tools.doClipper import GdalToolsDialog as Clipper
            d = Clipper( self.iface )
            self.runToolDialog( d )
            self.clipper = QAction( QIcon( ":icons/raster-clip.png" ), QCoreApplication.translate( "GdalTools", "Clipper" ), self.iface.mainWindow() )
            #self.clipper.setStatusTip( QCoreApplication.translate( "GdalTools", "Converts raster data between different formats") )
            #QObject.connect( self.clipper, SIGNAL( "triggered()" ), self.doClipper )

    def unload( self ):
            if not valid: return
            pass

    
            

    def runToolDialog( self, dlg ):
            dlg.show_()
            dlg.exec_()
            del dlg

    def doSettings( self ):
            #from tools.doSettings import GdalToolsSettingsDialog as Settings
            d = Settings( self.iface )
            d.exec_()


    def on_matrix_pressed(self):

       
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"
        
    
        
            
        else:
            self.close()
            
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())
            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
            
        if self.plot.currentText() == "":
            plot = ""
        else:
            plot = str(self.plot.currentText())
            
        if self.l1.currentText() == "":
            l1 = ""
        else:
            l1 = int(self.l1.currentText()) 
            
        if self.l2.currentText() == "":
            l2 = ""
        else:
            l2 = str(self.l2.currentText()) 
            
        if self.size.text() == "":
            size = 1
        else:
            size = str(self.size.text())
        
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    contatore += int(self.DATA_LIST[i].fase) #conteggio totale
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
            
        r = R()
        #r('load("/home/postgres/.RData")')
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (con)
        g = "r('png(\"%s/Fase%d_correlation_matrix.png\", width=2500, height=2500, pointsize=20)')" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].fase))
        eval(g)
        h = "r('archezoology_table<-dbGetQuery(con,\"select * from tot_famiglia where fase = %d\")')" % int(self.DATA_LIST[i].fase)
        eval (h)        
        
        r('''
panel.hist <- function(x, ...)      {
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(usr[1:2], 0, 1.5) )
  h <- hist(x, plot = FALSE)
  breaks <- h$breaks; nB <- length(breaks)
  y <- h$counts; y <- y/max(y)
  rect(breaks[-nB], 0, breaks[-1], y, col="cornsilk2", ...)
}
panel.cor <- function(x, y, digits=3, prefix="", cex.cor)     {
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(0, 1, 0, 1))
  r <- cor(y, x, use="all.obs")
  rabs <- abs(r)
  txt <- format(c(r, 0.123456789), digits=digits)[1]
  txt <- paste(prefix, "r=", txt, sep="")
  cl = 0.95         ### Confidence limit = 1-(level of significance)
  rtp <-cor.test(x,y,method="pearson",alternative="two.sided", 
                 conf.level=cl)
  pp <- format(c(rtp$p.value, 0.123456789), digits=digits)[1]
  pp <- paste(prefix, "p.val=", pp, sep="") ###p.value pearson cor.test
  if ( rabs<0.25 ) {
    text(0.5, 0.6, txt, cex = 0.8, col="blue")
  } else if ( rabs>0.4999 ) {
    text(0.5, 0.6, txt, cex = 0.8, col="red")
  } else {
    text(0.5, 0.6, txt, cex = 0.8, col="green")
  }
  if(missing(cex.cor))
    if ( rtp$p.value > (1-cl) ) {
      text(0.5, 0.4, pp, cex=0.8,col="hotpink")  #p.val Pearson > alfa
    } else {
      text(0.5, 0.4, pp, cex=0.8,col="green4")  #p.val Pearson <= alfa
    }
}


pairs(archezoology_table[7:29],
      lower.panel = panel.smooth,    # matrice inferiore: scatterplot
      upper.panel = panel.cor,       # matrice superiore: r Pearson e cor.test
      diag.panel = panel.hist)       # diagonale: istogrammi di frequenza

title(sub="Rosso = coppie con r>|0.5|, Verde = coppie con |0.25|<r<|0.5|;
      p.val verde scuro = coppie per cui si definisce r con una confidenza del 95%",
      cex.sub=0.7)
        ''')#### creazione ed esportazione della statistica descrittiva
        
    
    def on_matrix_2_pressed(self):

       
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",  QMessageBox.Ok)
            test = 1    
        if self.radioButtonUsMin.isChecked() == True:
            self.TYPE_QUANT = "US"
        
    
        
            
        else:
            self.close()
            
        if self.lineEdit_esp_generale.text() == "":
            lineEdit_esp_generale = ''
        else:
            lineEdit_esp_generale = str(self.lineEdit_esp_generale.text())
            
        if self.host.currentText() == "":
            host = ''
        else:
            host = str(self.host.currentText())
            
        if self.user.currentText() == "":
            user = ''
        else:
            user = str(self.user.currentText())
            
        if self.port.currentText() == "":
            port = ''
        else:
            port = int(self.port.currentText())
            
        if self.password.text() == "":
            password = 0
        else:
            password = str(self.password.text())
            
        if self.db.text() == "":
            db = 0
        else:
            db = str(self.db.text())
            
        if self.plot.currentText() == "":
            plot = ""
        else:
            plot = str(self.plot.currentText())
            
        if self.l1.currentText() == "":
            l1 = ""
        else:
            l1 = int(self.l1.currentText()) 
            
        if self.l2.currentText() == "":
            l2 = ""
        else:
            l2 = str(self.l2.currentText()) 
            
        if self.size.text() == "":
            size = 1
        else:
            size = str(self.size.text())
        
        
        for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                
                try:
                    temp_dataset = (int(self.DATA_LIST[i].fase))
                    
                    
                    contatore += int(self.DATA_LIST[i].fase) #conteggio totale
                    
                    dataset.append(temp_dataset)
                    
                except:
                    pass
            
        r = R()
        #r('load("/home/postgres/.RData")')
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()), str(self.user.currentText()))
        eval (con)
        g = "r('png(\"%s/Fase%d_correlation_matrix.png\", width=2500, height=2500, pointsize=20)')" % (str(self.lineEdit_esp_generale.text()),int(self.DATA_LIST[i].fase))
        eval(g)
        h = "r('archezoology_table<-dbGetQuery(con,\"select * from tot_ordine where fase = %d\")')" % int(self.DATA_LIST[i].fase)
        eval (h)        
        
        r('''
panel.hist <- function(x, ...)      {
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(usr[1:2], 0, 1.5) )
  h <- hist(x, plot = FALSE)
  breaks <- h$breaks; nB <- length(breaks)
  y <- h$counts; y <- y/max(y)
  rect(breaks[-nB], 0, breaks[-1], y, col="cornsilk2", ...)
}
panel.cor <- function(x, y, digits=3, prefix="", cex.cor)     {
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(0, 1, 0, 1))
  r <- cor(x, y, use="complete.obs")
  rabs <- abs(r)
  txt <- format(c(r, 0.123456789), digits=digits)[1]
  txt <- paste(prefix, "r=", txt, sep="")
  cl = 0.95         ### Confidence limit = 1-(level of significance)
  rtp <-cor.test(x,y,method="pearson",alternative="two.sided", 
                 conf.level=cl)
  pp <- format(c(rtp$p.value, 0.123456789), digits=digits)[1]
  pp <- paste(prefix, "p.val=", pp, sep="") ###p.value pearson cor.test
  if ( rabs<0.25 ) {
    text(0.5, 0.6, txt, cex = 1.8, col="blue")
  } else if ( rabs>0.4999 ) {
    text(0.5, 0.6, txt, cex = 1.8, col="red")
  } else {
    text(0.5, 0.6, txt, cex = 1.8, col="green")
  }
  if(missing(cex.cor))
    if ( rtp$p.value > (1-cl) ) {
      text(0.5, 0.4, pp, cex=1.8,col="hotpink")  #p.val Pearson > alfa
    } else {
      text(0.5, 0.4, pp, cex=1.8,col="green4")  #p.val Pearson <= alfa
    }
}

pairs(archezoology_table[7:9],
      lower.panel = panel.smooth,    # matrice inferiore: scatterplot
      upper.panel = panel.cor,       # matrice superiore: r Pearson e cor.test
      diag.panel = panel.hist)       # diagonale: istogrammi di frequenza
pairs(archezoology_table[11:19],
      lower.panel = panel.smooth,    # matrice inferiore: scatterplot
      upper.panel = panel.cor,       # matrice superiore: r Pearson e cor.test
      diag.panel = panel.hist)       # diagonale: istogrammi di frequenza
title(sub="Rosso = coppie con r>|0.5|, Verde = coppie con |0.25|<r<|0.5|;
      p.val verde scuro = coppie per cui si definisce r con una confidenza del 95%",
      cex.sub=0.7)
        ''')#### creazione ed esportazione della statistica descrittiva

    # #def on_tre_d_pressed(self):
        
        # mylayer = self.iface.activeLayer()
        
        # if self.tab_5.text() == "":
            # tab_5 = 0
        # else:
            # tab_5 = int(self.tab_5.text())

        # from shapely.wkb import loads
    
        # x=[]
        # y=[]
        # z=[]
        # for elem in mylayer.selectedFeatures():
               
               # geom= elem.geometry() 
               # wkb = geom.asWkb()
               # data = loads(wkb)
              
               # x.append(data.x)
               # y.append(data.y)
               # z.append(0)
               
        # x=[]
        # y=[]
        # z=[]
        # for elem in mylayer.selectedFeatures():
               
               # geom= elem.geometry() 
               # x.append(geom.asPoint()[0])
               # y.append(geom.asPoint()[1])
               # tab = "(z.append(elem.attributes()[%d]))" % int(self.tab_5.text()) 
               # eval (tab)
              
        
        # fig = plt.figure()
        # ax = Axes3D(fig)
        # ax.scatter3D(x,y,z,c=z,cmap=plt.cm.jet)
        # plt.show()

        
        # # apre la finestra per visualizzare i punti
        # f = visvis.gca()
        # m = visvis.plot(x,y,z, lc='k', ls='', mc='g', mw=2, lw=2, ms='.')
        # f.daspect = 1,1,10 # z x 10
        
       
        # # creazione di una griglia 2d
        # xi = np.linspace(min(x), max(x))
        # yi = np.linspace(min(y), max(y))
        # X, Y = np.meshgrid(xi, yi)
        # # interpolation
        # Z = griddata(x, y, z, xi, yi)
        # f = visvis.gca()
        # m = visvis.grid(xi,yi,Z) 
        # f.daspect = 1,1,10
        # m = visvis.surf(xi,yi,Z)
        # m.colormap = visvis.CM_JET
        
       
        # # costruzione della griglia
        # spline = sp.interpolate.Rbf(x,y,z,function='thin-plate')
        # xi = np.linspace(min(x), max(x))
        # yi = np.linspace(min(y), max(y))
        # X, Y = np.meshgrid(xi, yi)
        # # interpolazione
        # Z = spline(X,Y)
        # f = visvis.gca()
        # m = visvis.surf(xi,yi,Z)
        # m.colormap = visvis.CM_JET 
        # f.axis.visible = True

    
    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",  QMessageBox.Ok)
        else:   

            if self.comboBox_sito.currentText() == "":
                sito = None
            else:
                sito = str(self.comboBox_sito.currentText())

            if self.lineEdit_us.text() == "":
                us = None
            else:
                us = int(self.lineEdit_us.text())

            if self.lineEdit_periodo.text() == "":
                periodo = None
            else:
                periodo = int(self.lineEdit_periodo.text())

            if self.lineEdit_quadrato.text() == "":
                quadrato = None
            else:
                quadrato = str(self.lineEdit_quadrato.text())

            if self.lineEdit_fase.text() == "":
                fase = None
            else:
                fase = int(self.lineEdit_fase.text())


            if self.lineEdit_coord_x.text() == "":
                coord_x = None
            else:
                coord_x = float(self.lineEdit_coord_x.text())

            #f = open("test_coord.txt", "w")
            #f.write(str(coord_x))
            #f.close()

            if self.lineEdit_coord_y.text() == "":
                coord_y = None
            else:
                coord_y = float(self.lineEdit_coord_y.text())

            if self.lineEdit_coord_z.text() == "":
                coord_z = None
            else:
                coord_z = float(self.lineEdit_coord_z.text())

            if self.lineEdit_n_riliev.text() == "":
                n_rilievo = None
            else:
                n_rilievo = str(self.lineEdit_n_riliev.text())

            if self.lineEdit_n_inv.text() == "":
                n_codice = None
            else:
                n_codice = str(self.lineEdit_n_inv.text())

            if self.lineEdit_code.text() == "":
                code = None
            else:
                code = int(self.lineEdit_code.text())

            if self.comboBox_ordine.currentText() == "":
                ordine = None
            else:
                ordine = str(self.comboBox_ordine.currentText())

            if self.comboBox_specie.currentText() == "":
                specie = None
            else:
                specie = str(self.comboBox_specie.currentText())

            if self.comboBox_famiglia.currentText() == "":
                famiglia = None
            else:
                famiglia = str(self.comboBox_famiglia.currentText())

            if self.comboBox_classe.currentText() == "":
                classe = None
            else:
                classe = str(self.comboBox_classe.currentText())

            if self.lineEdit_elem_sp.text() == "":
                elem_specifici = None
            else:
                elem_specifici = str(self.lineEdit_elem_sp.text())

            if self.comboBox_elem_gen.currentText() == "":
                elemnto_anat_generico = None
            else:
                elemnto_anat_generico = str(self.comboBox_elem_gen.currentText())   

            if self.lineEdit_azione.text() == "":
                azione = None
            else:
                azione = str(self.lineEdit_azione.text())

            if self.lineEdit_mod_osso.text() == "":
                modulo_osso = None
            else:
                modulo_osso = str(self.lineEdit_mod_osso.text())

            if self.lineEdit_peso.text() == "":
                peso = None
            else:
                peso = float(self.lineEdit_peso.text())

            if self.comboBox_lungh.currentText() == "":
                lunghezza = None
            else:
                lunghezza = str(self.comboBox_lungh.currentText())

            if self.comboBox_largh.currentText() == "":
                larghezza = None
            else:
                larghezza = str(self.comboBox_largh.currentText())
            
            if self.comboBox_spess.currentText() == "":
                spessore = None
            else:
                spessore = str(self.comboBox_spess.currentText())

            
            
            search_dict = {
            
            self.TABLE_FIELDS[0]  : code, 
            self.TABLE_FIELDS[1]  : "'"+str(self.lineEdit_n_riliev.text())+"'",                                     #1 - Sito
            self.TABLE_FIELDS[2]  : "'"+str(self.lineEdit_n_inv.text())+"'",                                    #2 - Area
            self.TABLE_FIELDS[3]  : "'"+str(self.lineEdit_anno.text())+"'",
            self.TABLE_FIELDS[4]  :"'"+str(self.comboBox_sito.currentText())+"'",                                               #3 
            self.TABLE_FIELDS[5]  : "'"+str(self.lineEdit_quadrato.text())+"'",
            self.TABLE_FIELDS[6]  : us,
            self.TABLE_FIELDS[7]  : periodo,
            self.TABLE_FIELDS[8]  : fase,                           #7 - interpretazione
            self.TABLE_FIELDS[9]  : "'"+str(self.comboBox_specie.currentText())+"'",                            #8 - periodo iniziale
            self.TABLE_FIELDS[10] : "'"+str(self.comboBox_classe.currentText())+"'",                                #9 - fase iniziale
            self.TABLE_FIELDS[11] : "'"+str(self.comboBox_ordine.currentText())+"'",                                #10 - periodo finale iniziale
            self.TABLE_FIELDS[12] : "'"+str(self.comboBox_famiglia.currentText())+"'",                              #11 - fase finale
            self.TABLE_FIELDS[13] : "'"+str(self.comboBox_elem_gen.currentText())+"'",                              #12 - attivita  
            self.TABLE_FIELDS[14] : "'"+str(self.lineEdit_elem_sp.text())+"'",                                  #13 - attivita  
            self.TABLE_FIELDS[15] : "'"+str(self.lineEdit_taglia.text())+"'",                                           #14 - anno scavo
            self.TABLE_FIELDS[16] : "'"+str(self.lineEdit_eta.text())+"'",                                  #15 - metodo
            self.TABLE_FIELDS[17] : "'"+str(self.comboBox_lato.currentText())+"'",                              #16 - data schedatura
            self.TABLE_FIELDS[18] : "'"+str(self.comboBox_lungh.currentText())+"'",                         #17 - schedatore
            self.TABLE_FIELDS[19] : "'"+str(self.comboBox_largh.currentText())+"'",                         #18 - formazione
            self.TABLE_FIELDS[20] : "'"+str(self.comboBox_spess.currentText())+"'", 
            self.TABLE_FIELDS[21] : "'"+str(self.lineEdit_porzione.text())+"'",             #19 - conservazione
            self.TABLE_FIELDS[22] : peso,
            self.TABLE_FIELDS[23] : coord_x,                            #5 - Definizione intepretata
            self.TABLE_FIELDS[24] : coord_y,                                    #6 - descrizione
            self.TABLE_FIELDS[25] : coord_z,
            self.TABLE_FIELDS[26] : "'"+str(self.lineEdit_elem_sp.text())+"'",                                  #6 - descrizione
            self.TABLE_FIELDS[27] : "'"+str(self.lineEdit_elem_sp.text())+"'",                              #20 - colore
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if bool(search_dict) == False:
                QMessageBox.warning(self, "ATTENZIONE", "Non e' stata impostata alcuna ricerca!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if bool(res) == False:
                    QMessageBox.warning(self, "ATTENZIONE", "Non è¨ stato trovato nessun record!",  QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"],"False")
                    self.setComboBoxEnable(["self.lineEdit_periodo"],"False")
                    self.setComboBoxEnable(["self.lineEdit_us"],"False")
                    self.setComboBoxEnable(["self.lineEdit_quadrato"],"False")
                    self.setComboBoxEnable(["self.lineEdit_fase"],"False")
                    
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)

                    if self.REC_TOT == 1:
                        strings = ("E' stato trovato", self.REC_TOT, "record")
                        if self.toolButtonGis.isChecked() == True:
                           self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")
                        if self.toolButtonGis.isChecked() == True:
                           self.pyQGIS.charge_vector_layers(self.DATA_LIST)

                    self.setComboBoxEnable(["self.comboBox_sito"],"False")
                    self.setComboBoxEnable(["self.lineEdit_periodo"],"False")
                    self.setComboBoxEnable(["self.lineEdit_us"],"False")
                    self.setComboBoxEnable(["self.lineEdit_quadrato"],"False")
                    self.setComboBoxEnable(["self.lineEdit_fase"],"False")
                    
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings,  QMessageBox.Ok)
        self.enable_button_search(1)

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        self.msg = msg
        if self.msg == 1:
            self.update_record()
            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i."+ self.ID_TABLE))
            self.DATA_LIST = []
            if self.SORT_STATUS == "n":
                #self.testing('test_sort.txt', 'qua')
                temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE)
            else:
                temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS, self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR


    #custom functions
    def charge_records(self):
        self.DATA_LIST = []

        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_list.append(eval("i." + self.ID_TABLE))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)


    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today


    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename+".rowCount()")
        col = eval(self.tablename+".columnCount()")
        lista=[]
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename+".item(r,c)")
                if bool(value) == True:
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista


    def empty_fields(self):
        self.lineEdit_code.clear()
        self.lineEdit_n_riliev.clear()
        self.lineEdit_n_inv.clear()
        self.lineEdit_anno.clear()
        self.comboBox_sito.setEditText("")
        self.lineEdit_quadrato.clear()
        self.lineEdit_us.clear()
        self.lineEdit_periodo.clear()       
        self.lineEdit_fase.clear()  
        self.comboBox_specie.setEditText("")
        self.comboBox_classe.setEditText("")
        self.comboBox_ordine.setEditText("")
        self.comboBox_famiglia.setEditText("")
        self.comboBox_elem_gen.setEditText("")
        self.lineEdit_elem_sp.clear()
        self.lineEdit_taglia.clear()
        self.lineEdit_eta.clear()
        self.comboBox_lato.setEditText("")
        self.comboBox_lungh.setEditText("")
        self.comboBox_largh.setEditText("")
        self.comboBox_spess.setEditText("")
        self.lineEdit_porzione.clear()
        self.lineEdit_peso.clear()
        self.lineEdit_coord_x.clear()
        self.lineEdit_coord_y.clear()
        self.lineEdit_coord_z.clear()       
        self.lineEdit_azione.clear()
        self.lineEdit_mod_osso.clear()

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito)                                   #1 - Sito
            #self.lineEdit_periodo.setText(str(self.DATA_LIST[self.rec_num].periodo))                       #2 - Periodo
            
            if self.DATA_LIST[self.rec_num].us == None:                                             #4 - cronologia iniziale
                self.lineEdit_us.setText("")
            else:
                self.lineEdit_us.setText(str(self.DATA_LIST[self.rec_num].us))
            
            if self.DATA_LIST[self.rec_num].periodo == None:                                                #4 - cronologia iniziale
                self.lineEdit_periodo.setText("")
            else:
                self.lineEdit_periodo.setText(str(self.DATA_LIST[self.rec_num].periodo))

            if self.DATA_LIST[self.rec_num].quadrato == None:                                               #4 - cronologia iniziale
                self.lineEdit_quadrato.setText("")
            else:
                self.lineEdit_quadrato.setText(str(self.DATA_LIST[self.rec_num].quadrato))


            if self.DATA_LIST[self.rec_num].fase == None:                                               #4 - cronologia iniziale
                self.lineEdit_fase.setText("")
            else:
                self.lineEdit_fase.setText(str(self.DATA_LIST[self.rec_num].fase))                      #2 - Periodo
            #self.lineEdit_quadrato.setText(str(self.DATA_LIST[self.rec_num].quadrato))                         #2 - Periodo

            if self.DATA_LIST[self.rec_num].coord_x == None:                                                #4 - cronologia iniziale
                self.lineEdit_coord_x.setText("")
            else:
                self.lineEdit_coord_x.setText(str(self.DATA_LIST[self.rec_num].coord_x))

            if self.DATA_LIST[self.rec_num].coord_y == None:                                                #4 - cronologia iniziale
                self.lineEdit_coord_y.setText("")
            else:
                self.lineEdit_coord_y.setText(str(self.DATA_LIST[self.rec_num].coord_y))

            if self.DATA_LIST[self.rec_num].coord_z == None:                                                #4 - cronologia iniziale
                self.lineEdit_coord_z.setText("")
            else:
                self.lineEdit_coord_z.setText(str(self.DATA_LIST[self.rec_num].coord_z))

            if self.DATA_LIST[self.rec_num].peso == None:                                               #4 - cronologia iniziale
                self.lineEdit_peso.setText("")
            else:
                self.lineEdit_peso.setText(str(self.DATA_LIST[self.rec_num].peso))

            if self.DATA_LIST[self.rec_num].code == None:                                               #4 - cronologia iniziale
                self.lineEdit_code.setText("")
            else:
                self.lineEdit_code.setText(str(self.DATA_LIST[self.rec_num].code))

            if self.DATA_LIST[self.rec_num].n_rilievo == None:                                              #4 - cronologia iniziale
                self.lineEdit_n_riliev.setText("")
            else:
                self.lineEdit_n_riliev.setText(str(self.DATA_LIST[self.rec_num].n_rilievo))

            if self.DATA_LIST[self.rec_num].n_codice == None:                                               #4 - cronologia iniziale
                self.lineEdit_n_inv.setText("")
            else:
                self.lineEdit_n_inv.setText(str(self.DATA_LIST[self.rec_num].n_codice))

            if self.DATA_LIST[self.rec_num].anno == None:                                               #4 - cronologia iniziale
                self.lineEdit_anno.setText("")
            else:
                self.lineEdit_anno.setText(str(self.DATA_LIST[self.rec_num].anno))

            if self.DATA_LIST[self.rec_num].specie == None:                                             #4 - cronologia iniziale
                self.comboBox_specie.setEditText("")
            else:
                self.comboBox_specie.setEditText(str(self.DATA_LIST[self.rec_num].specie))

            if self.DATA_LIST[self.rec_num].ordine == None:                                             #4 - cronologia iniziale
                self.comboBox_ordine.setEditText("")
            else:
                self.comboBox_ordine.setEditText(str(self.DATA_LIST[self.rec_num].ordine))

            if self.DATA_LIST[self.rec_num].classe == None:                                             #4 - cronologia iniziale
                self.comboBox_specie.setEditText("")
            else:
                self.comboBox_classe.setEditText(str(self.DATA_LIST[self.rec_num].classe))

            if self.DATA_LIST[self.rec_num].famiglia == None:                                               #4 - cronologia iniziale
                self.comboBox_famiglia.setEditText("")
            else:
                self.comboBox_famiglia.setEditText(str(self.DATA_LIST[self.rec_num].famiglia))

            if self.DATA_LIST[self.rec_num].taglia == None:                                             #4 - cronologia iniziale
                self.lineEdit_taglia.setText("")
            else:
                self.lineEdit_taglia.setText(str(self.DATA_LIST[self.rec_num].taglia))

            if self.DATA_LIST[self.rec_num].eta == None:                                                #4 - cronologia iniziale
                self.lineEdit_eta.setText("")
            else:
                self.lineEdit_eta.setText(str(self.DATA_LIST[self.rec_num].eta))

            if self.DATA_LIST[self.rec_num].porzione == None:                                               #4 - cronologia iniziale
                self.lineEdit_porzione.setText("")
            else:
                self.lineEdit_porzione.setText(str(self.DATA_LIST[self.rec_num].porzione))

            if self.DATA_LIST[self.rec_num].azione == None:                                             #4 - cronologia iniziale
                self.lineEdit_azione.setText("")
            else:
                self.lineEdit_azione.setText(str(self.DATA_LIST[self.rec_num].azione))

            if self.DATA_LIST[self.rec_num].modulo_osso == None:                                                #4 - cronologia iniziale
                self.lineEdit_mod_osso.setText("")
            else:
                self.lineEdit_mod_osso.setText(str(self.DATA_LIST[self.rec_num].modulo_osso))

            if self.DATA_LIST[self.rec_num].lato == None:                                               #4 - cronologia iniziale
                self.comboBox_lato.setEditText("")
            else:
                self.comboBox_lato.setEditText(str(self.DATA_LIST[self.rec_num].lato))

            if self.DATA_LIST[self.rec_num].elem_specifici == None:                                             #4 - cronologia iniziale
                self.lineEdit_elem_sp.setText("")
            else:
                self.lineEdit_elem_sp.setText(str(self.DATA_LIST[self.rec_num].elem_specifici))

            if self.DATA_LIST[self.rec_num].elemnto_anat_generico == None:                                              #4 - cronologia iniziale
                self.comboBox_elem_gen.setEditText("")
            else:
                self.comboBox_elem_gen.setEditText(str(self.DATA_LIST[self.rec_num].elemnto_anat_generico))


        except :
            pass#QMessageBox.warning(self, "Errore Fill Fields", str(e),  QMessageBox.Ok)


    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        #data
        if self.lineEdit_us.text() == "":
            us = None
        else:
            us = int(self.lineEdit_us.text())

        if self.lineEdit_us.text() == "":
            periodo = None
        else:
            periodo = int(self.lineEdit_periodo.text())

        if self.lineEdit_fase.text() == "":
            fase = None
        else:
            fase = int(self.lineEdit_fase.text())

        if self.lineEdit_quadrato.text() == "":
            quadrato = None
        else:
            quadrato = str(self.lineEdit_quadrato.text())

        if self.comboBox_sito.currentText() == "":
            sito = None
        else:
            sito = str(self.comboBox_sito.currentText())

        if self.lineEdit_coord_x.text() == "":
            coord_x = None
        else:
            coord_x = float(self.lineEdit_coord_x.text())

        if self.lineEdit_coord_y.text() == "":
            coord_y = None
        else:
            coord_y = float(self.lineEdit_coord_y.text())

        if self.lineEdit_coord_z.text() == "":
            coord_z = None
        else:
            coord_z = float(self.lineEdit_coord_z.text())

        if self.lineEdit_peso.text() == "":
            peso = None
        else:
            peso = float(self.lineEdit_peso.text())

        if self.lineEdit_code.text() == "":
            code = None
        else:
            code = int(self.lineEdit_code.text())

        if self.lineEdit_n_riliev.text() == "":
            n_riliev = None
        else:
            n_riliev = str(self.lineEdit_n_riliev.text())

        if self.comboBox_famiglia.currentText() == "":
            famiglia = None
        else:
            famiglia = str(self.comboBox_famiglia.currentText())


        if self.comboBox_classe.currentText() == "":
            classe = None
        else:
            classe = str(self.comboBox_classe.currentText())

        if self.comboBox_specie.currentText() == "":
            specie = None
        else:
            classe = str(self.comboBox_specie.currentText())

        if self.comboBox_ordine.currentText() == "":
            ordine = None
        else:
            ordine = str(self.comboBox_ordine.currentText())


        if self.lineEdit_anno.text() == "":
            anno = None
        else:
            anno = str(self.lineEdit_anno.text())

        if self.lineEdit_taglia.text() == "":
            taglia = None
        else:
            taglia = str(self.lineEdit_taglia.text())

        if self.comboBox_lato.currentText() == "":
            lato = None
        else:
            lato = str(self.comboBox_lato.currentText())

        if self.lineEdit_porzione.text() == "":
            porzione = None
        else:
            porzione = str(self.lineEdit_porzione.text())

        if self.lineEdit_eta.text() == "":
            eta = None
        else:
            eta = str(self.lineEdit_eta.text())

        if self.comboBox_lungh.currentText() == "":
            lunghezza = None
        else:
            lunghezza = str(self.comboBox_lungh.currentText())

        if self.comboBox_largh.currentText() == "":
            larghezza = None
        else:
            larghezza = str(self.comboBox_largh.currentText())

        if self.comboBox_spess.currentText() == "":
            spessore = None
        else:
            spessore = str(self.comboBox_spess.currentText())

        if self.lineEdit_porzione.text() == "":
            porzione = None
        else:
            porzione = str(self.lineEdit_porzione.text())

        
        if self.lineEdit_azione.text() == "":
            azione = None
        else:
            azione = str(self.lineEdit_azione.text())

        if self.lineEdit_mod_osso.text() == "":
            modulo_osso = None
        else:
            modulo_osso = str(self.lineEdit_mod_osso.text())

        if self.lineEdit_elem_sp.text() == "":
            elem_specifici = None
        else:
            elem_specifici = str(self.lineEdit_elem_sp.text())


        if self.comboBox_elem_gen.currentText() == "":
            elemnto_anat_generico = None
        else:
            elemnto_anat_generico = str(self.comboBox_elem_gen.currentText())



        self.DATA_LIST_REC_TEMP = [
        str(code),
        str(self.lineEdit_n_riliev.text()),
        str(self.lineEdit_n_inv.text()),
        str(self.lineEdit_anno.text()),
        str(self.comboBox_sito.currentText()),
        str(self.lineEdit_quadrato.text()),                             #2 - periodo
        str(us),
        str(periodo), 
        str(fase), 
        str(self.comboBox_specie.currentText()),                 
        str(self.comboBox_classe.currentText()),
        str(self.comboBox_ordine.currentText()),
        str(self.comboBox_famiglia.currentText()),
        str(self.comboBox_elem_gen.currentText()),
        str(self.lineEdit_elem_sp.text()),
        str(self.lineEdit_taglia.text()),
        str(self.lineEdit_eta.text()),
        str(self.comboBox_lato.currentText()),
        str(self.comboBox_lungh.currentText()),
        str(self.comboBox_largh.currentText()),
        str(self.comboBox_spess.currentText()),
        str(self.lineEdit_porzione.text()),
        str(peso),
        str(coord_x),
        str(coord_y),
        str(coord_z),       
        str(self.lineEdit_azione.text()),
        str(self.lineEdit_mod_osso.text())
        
        ]                                               #8 - cont_per provvisorio


    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = ('%s%s%s%s') % (fn, '.setEnabled(', v, ')')
            eval(cmd)

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def update_record(self):
        """
        txt=self.rec_to_update()
        f = open("/test_coord_x.txt", 'w')
        f.write(str(txt))
        f.close()
        """

        self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, 
                        self.ID_TABLE,
                        [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE+")")],
                        self.TABLE_FIELDS,
                        self.rec_toupdate())

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_US()
    ui.show()
    barra.show()
    sys.exit(app.exec_())
