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

import os
from datetime import date
# from test.test_heapq import R

import sys
from builtins import range
from builtins import str
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QApplication, QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication

from .modules.db.pyarchinit_conn_strings import Connection
from .modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from .modules.db.pyarchinit_utility import Utility
from .modules.gis.pyarchinit_pyqgis_archeozoo import Pyarchinit_pyqgis
from .modules.utility.pyarchinit_error_check import Error_check
from .pyarchinit_US_mainapp import pyarchinit_US
from .sortpanelmain import SortPanelMain

valid = True
req_mods = {'osgeo': 'osgeo [python-gdal]'}
try:
    from osgeo import gdal
    from osgeo import ogr
except ImportError as e:
    valid = False

    # if the plugin is shipped with QGis catch the exception and
    # display an error message

    import os.path

    qgisUserPluginPath = \
        os.path.abspath(os.path.join(str(QgsApplication.qgisSettingsDirPath()),
                                     'python'))
    if not os.path.dirname(__file__).startswith(qgisUserPluginPath):
        title = QCoreApplication.translate('GdalTools', 'Plugin error')
        message = QCoreApplication.translate('GdalTools',
                                             '''Unable to load %1 plugin.
                             The required "%2" module is missing.
                             Install it and try again.''')
        import qgis.utils

        QMessageBox.warning(qgis.utils.iface.mainWindow(), title,
                            message.arg('GdalTools'
                                        ).arg(req_mods['osgeo']))
    else:

        # if a module is missing show a more friendly module's name

        error_str = e.args[0]
        error_mod = error_str.replace('No module named ', '')
        if error_mod in req_mods:
            error_str = error_str.replace(error_mod,
                                          req_mods[error_mod])
        raise ImportError(error_str)

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), 'modules', 'gui', 'pyarchinit_Archeozoology_ui.ui'))


class pyarchinit_Archeozoology(QDialog, MAIN_DIALOG_CLASS):
    MSG_BOX_TITLE = "PyArchInit - pyarchinit_version 0.4 - Scheda Archeozoologia Quantificazioni"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'archeozoology_table'
    MAPPER_TABLE_CLASS = "ARCHEOZOOLOGY"
    NOME_SCHEDA = "Scheda Archeozoologia"
    ID_TABLE = "id_archzoo"
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        'Sito': 'sito',
        'Area': 'area',
        'US': 'us',
        'Quadrato': 'quadrato',
        'Coordinata x': 'coord_x',
        'Coordinata y': 'coord_y',
        'Coordinata z': 'coord_z',
        'Bos/Bison': 'bos_bison',
        'Calcinati': 'calcinati',
        'Camoscio': 'camoscio',
        'Capriolo': 'capriolo',
        'Cervo': 'cervo',
        'Combusto': 'combusto',
        'Coni': 'coni',
        'Pdi': 'pdi',
        'Stambecco': 'stambecco',
        'Strie': 'strie',
        'Canidi': 'canidi',
        'Ursidi': 'ursidi',
        'Megacero': 'megacero'
    }
    SORT_ITEMS = [
        ID_TABLE,
        'Sito',
        'Area',
        'US',
        'Quadrato',
        'Coordinata x',
        'Coordinata y',
        'Coordinata z',
        'Bos/Bison',
        'Calcinati',
        'Camoscio',
        'Capriolo',
        'Cervo',
        'Combusto',
        'Coni',
        'Pdi',
        'Stambecco',
        'Strie',
        'Canidi',
        'Ursidi',
        'Megacero'
    ]

    TABLE_FIELDS = [
        'sito',
        'area',
        'us',
        'quadrato',
        'coord_x',
        'coord_y',
        'coord_z',
        'bos_bison',
        'calcinati',
        'camoscio',
        'capriolo',
        'cervo',
        'combusto',
        'coni',
        'pdi',
        'stambecco',
        'strie',
        'canidi',
        'ursidi',
        'megacero'
    ]

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None

        try:
            self.on_pushButton_connect_pressed()
        except:
            pass

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

    def on_pushButton_connect_pressed(self):
        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST) == True:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                QMessageBox.warning(self, "BENVENUTO",
                                    "Benvenuto in pyArchInit" + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                    QMessageBox.Ok)
                self.charge_list()
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert 1",
                                    "La connessione e' fallita <br><br> Tabella non presente. E' NECESSARIO RIAVVIARE QGIS" + str(
                                        e), QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert 2", "La connessione e' fallita <br> Errore: <br>" + str(e),
                                    QMessageBox.Ok)

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

    # buttons functions
    def on_pushButton_sort_pressed(self):
        dlg = SortPanelMain(self)
        dlg.insertItems(self.SORT_ITEMS)
        dlg.exec_()

        items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

        self.SORT_ITEMS_CONVERTED = []
        for i in items:
            self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

        self.SORT_MODE = order_type
        self.empty_fields()

        id_list = []
        for i in self.DATA_LIST:
            id_list.append(eval("i." + self.ID_TABLE))
        self.DATA_LIST = []

        temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                    self.MAPPER_TABLE_CLASS, self.ID_TABLE)

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
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.fill_fields()

    def on_toolButtonGis_toggled(self):
        if self.toolButtonGis.isChecked() == True:
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                QMessageBox.Ok)

    def on_pushButton_new_rec_pressed(self):
        # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEnable(["self.lineEdit_area"], "True")
            self.setComboBoxEnable(["self.lineEdit_us"], "True")
            self.setComboBoxEnable(["self.lineEdit_quadrato"], "True")

            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.records_equal_check() == 1:
                self.update_if(
                    QMessageBox.warning(self, 'ATTENZIONE', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.Cancel, 1))
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.enable_button(1)
            else:
                QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    self.fill_fields(self.REC_CORR)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
            test = 1
        elif EC.data_is_empty(str(self.lineEdit_quadrato.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Quadrato. \n Il campo non deve essere vuoto", QMessageBox.Ok)
            test = 1

        return test

    def insert_new_rec(self):
        if self.lineEdit_us.text() == "":
            us = None
        else:
            us = int(self.lineEdit_us.text())

        if self.lineEdit_coord_x.text() == "":
            coord_x = None
        else:
            coord_x = float(self.lineEdit_coord_x.text())

        # f = open("test_coord.txt", "w")
        # f.write(str(coord_x))
        # f.close()

        if self.lineEdit_coord_y.text() == "":
            coord_y = None
        else:
            coord_y = float(self.lineEdit_coord_y.text())

        if self.lineEdit_coord_z.text() == "":
            coord_z = None
        else:
            coord_z = float(self.lineEdit_coord_z.text())

        if self.lineEdit_bos_bison.text() == "":
            bos_bison = None
        else:
            bos_bison = int(self.lineEdit_bos_bison.text())

        if self.lineEdit_calcinati.text() == "":
            calcinati = None
        else:
            calcinati = int(self.lineEdit_calcinati.text())

        if self.lineEdit_camoscio.text() == "":
            camoscio = None
        else:
            camoscio = int(self.lineEdit_camoscio.text())

        if self.lineEdit_capriolo.text() == "":
            capriolo = None
        else:
            capriolo = int(self.lineEdit_capriolo.text())

        if self.lineEdit_cervi.text() == "":
            cervo = None
        else:
            cervo = int(self.lineEdit_cervi.text())

        if self.lineEdit_combuste.text() == "":
            combusto = None
        else:
            combusto = int(self.lineEdit_combuste.text())

        if self.lineEdit_Coni.text() == "":
            coni = None
        else:
            coni = int(self.lineEdit_Coni.text())

        if self.lineEdit_pdi.text() == "":
            pdi = None
        else:
            pdi = int(self.lineEdit_pdi.text())

        if self.lineEdit_stambecco.text() == "":
            stambecco = None
        else:
            stambecco = int(self.lineEdit_stambecco.text())

        if self.lineEdit_strie.text() == "":
            strie = None
        else:
            strie = int(self.lineEdit_strie.text())

        if self.lineEdit_canidi.text() == "":
            canidi = None
        else:
            canidi = int(self.lineEdit_canidi.text())

        if self.lineEdit_ursidi.text() == "":
            ursidi = None
        else:
            ursidi = int(self.lineEdit_ursidi.text())

        if self.lineEdit_megacero.text() == "":
            megacero = None
        else:
            megacero = int(self.lineEdit_megacero.text())

        try:
            data = self.DB_MANAGER.insert_values_archeozoology(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                str(self.lineEdit_area.text()),
                us,
                str(self.lineEdit_quadrato.text()),
                coord_x,
                coord_y,
                coord_z,
                bos_bison,
                calcinati,
                camoscio,
                capriolo,
                cervo,
                combusto,
                coni,
                pdi,
                stambecco,
                strie,
                canidi,
                ursidi,
                megacero)

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " gia' presente nel database"
                else:
                    msg = e
                QMessageBox.warning(self, "Errore", "Attenzione 1 ! \n" + str(msg), QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, "Errore", "Attenzione 2 ! \n" + str(e), QMessageBox.Ok)
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
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.label_sort.setText(self.SORTED_ITEMS["n"])

    # records surf functions
    def on_pushButton_first_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Cancel, 1))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Cancel, 1))
        try:
            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
            self.fill_fields(self.REC_CORR)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Cancel, 1))

        self.REC_CORR = self.REC_CORR - 1
        if self.REC_CORR == -1:
            self.REC_CORR = 0
            QMessageBox.warning(self, "Errore", "Sei al primo record!", QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_next_rec_pressed(self):

        if self.records_equal_check() == 1:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Cancel, 1))

        self.REC_CORR = self.REC_CORR + 1
        if self.REC_CORR >= self.REC_TOT:
            self.REC_CORR = self.REC_CORR - 1
            QMessageBox.warning(self, "Errore", "Sei all'ultimo record!", QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_delete_pressed(self):
        msg = QMessageBox.warning(self, "Attenzione!!!",
                                  "Vuoi veramente eliminare il record? \n L'azione e' irreversibile",
                                  QMessageBox.Cancel, 1)
        if msg != 1:
            QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records()  # charge records from DB
                QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                self.charge_list()
            except:
                QMessageBox.warning(self, "Attenzione", "Il database e' vuoto!", QMessageBox.Ok)

            if bool(self.DATA_LIST) == False:
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
            # check if DB is empty
            if bool(self.DATA_LIST) == True:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.label_sort.setText(self.SORTED_ITEMS["n"])

    def on_pushButton_new_search_pressed(self):
        # self.setComboBoxEditable()
        self.enable_button_search(0)

        # set the GUI for a new search
        if self.BROWSE_STATUS != "f":
            self.BROWSE_STATUS = "f"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEnable(["self.lineEdit_area"], "True")
            self.setComboBoxEnable(["self.lineEdit_us"], "True")
            self.setComboBoxEnable(["self.lineEdit_quadrato"], "True")

    def on_toolButton_esp_generale_pressed(self):
        self.percorso = QFileDialog.getExistingDirectory(self, 'Choose Save Directory')
        self.lineEdit_esp_generale.setText(self.percorso)

    def on_calcola_pressed(self):  #####modifiche apportate per il calcolo statistico con R
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
            test = 1
        # return test

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
        # dlg = QuantPanelMain(self)
        # dlg.exec_()
        # dataset = []

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
        n = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(n)
        con = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(con)
        if self.bos.isChecked() == True:
            x1 = "r('VGM_PARAM_A3 <- gstat(id=\"%s\", formula=%s~1,locations=~coord_x+coord_y, data=archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_bos_2.currentText()), str(self.c1.currentText()))
            eval(x1)
        else:
            pass
        if self.calcinati.isChecked() == True:
            x2 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y, archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_calcinati_2.text()), str(self.c2.currentText()))
            eval(x2)
        else:
            pass
        if self.camoscio.isChecked() == True:
            x3 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3,\"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_camoscio_2.text()), str(self.c3.currentText()))
            eval(x3)
        else:
            pass
        if self.capriolo.isChecked() == True:
            x4 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_capriolo_2.text()), str(self.c4.currentText()))
            eval(x4)
        else:
            pass
        if self.cervi.isChecked() == True:
            x5 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_cervo_2.text()), str(self.c5.currentText()))
            eval(x5)
        else:
            pass
        if self.combuste.isChecked() == True:
            x6 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_combusto_2.text()), str(self.c6.currentText()))
            eval(x6)
        else:
            pass
        if self.coni.isChecked() == True:
            x7 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_coni_2.text()), str(self.c7.currentText()))
            eval(x7)
        else:
            pass
        if self.pdi.isChecked() == True:
            x8 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_pdi_2.text()), str(self.c8.currentText()))
            eval(x8)
        else:
            pass
        if self.stambecco.isChecked() == True:
            x9 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_stambecco_2.text()), str(self.c9.currentText()))
            eval(x9)
        else:
            pass
        if self.strie.isChecked() == True:
            x10 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_strie_2.text()), str(self.c10.currentText()))
        else:
            pass
        if self.megacero.isChecked() == True:
            x11 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_megacero_2.text()), str(self.c13.currentText()))
            eval(x11)
        else:
            pass
        if self.ursidi.isChecked() == True:
            x12 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_ursidi_2.text()), str(self.c12.currentText()))
            eval(x12)
        else:
            pass
        if self.canidi.isChecked() == True:
            x13 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_canidi_2.text()), str(self.c11.currentText()))
            eval(x13)
        else:
            pass
            c = "r('A3 <- gstat(VGM_PARAM_A3, fill.all=TRUE, model=vgm(%d,\"%s\",%s, nugget = %d, kappa= %s))')" % (
                int(self.psill.text()), str(self.model.currentText()), str(self.rang.text()), int(self.nugget_2.text()),
                str(self.kappa.text()))
            eval(c)
            d = "r('ESV_A3 <- variogram(A3, width=%s, cutoff=%d)')" % (
                str(self.lineEdit_width.text()), int(self.cutoff.text()))
            eval(d)

            fittare = "r('VARMODEL_A3 = fit.lmc(ESV_A3, A3,model=vgm(%d,\"%s\",%s, nugget = %d, kappa= %s))')" % (
                int(self.psill.text()), str(self.model.currentText()), str(self.rang.text()), int(self.nugget_2.text()),
                str(self.kappa.text()))
            eval(fittare)
            a = "r('png(\"%s/A%d_semivariogram.png\", width=%d, height=%d, res=400); plot(ESV_A3, model=VARMODEL_A3,xlab=,ylab=,pch=20, cex=0.7, col=\"red\", main=\"Linear Model of Coregionalization A%d\")')" % (
                str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us), int(self.set_size_plot.text()),
                int(self.set_size_plot.text()), int(self.DATA_LIST[i].us))
            eval(a)

    def on_mappa_pressed(self):  #####modifiche apportate per il calcolo statistico con R
        self.ITEMS = []

        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
            test = 1
        # return test

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
        # dlg = QuantPanelMain(self)
        # dlg.exec_()
        # dataset = []

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
        n = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(n)
        con = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(con)
        if self.bos.isChecked() == True:
            x1 = "r('VGM_PARAM_A3 <- gstat(id=\"%s\", formula=%s~1,locations=~coord_x+coord_y, data=archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_bos_2.currentText()), str(self.c1.currentText()))
            eval(x1)
        else:
            pass
        if self.calcinati.isChecked() == True:
            x2 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y, archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_calcinati_2.text()), str(self.c2.currentText()))
            eval(x2)
        else:
            pass
        if self.camoscio.isChecked() == True:
            x3 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3,\"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_camoscio_2.text()), str(self.c3.currentText()))
            eval(x3)
        else:
            pass
        if self.capriolo.isChecked() == True:
            x4 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_capriolo_2.text()), str(self.c4.currentText()))
            eval(x4)
        else:
            pass
        if self.cervi.isChecked() == True:
            x5 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_cervo_2.text()), str(self.c5.currentText()))
            eval(x5)
        else:
            pass
        if self.combuste.isChecked() == True:
            x6 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_combusto_2.text()), str(self.c6.currentText()))
            eval(x6)
        else:
            pass
        if self.coni.isChecked() == True:
            x7 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_coni_2.text()), str(self.c7.currentText()))
            eval(x7)
        else:
            pass
        if self.pdi.isChecked() == True:
            x8 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_pdi_2.text()), str(self.c8.currentText()))
            eval(x8)
        else:
            pass
        if self.stambecco.isChecked() == True:
            x9 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_stambecco_2.text()), str(self.c9.currentText()))
            eval(x9)
        else:
            pass
        if self.strie.isChecked() == True:
            x10 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_strie_2.text()), str(self.c10.currentText()))
        else:
            pass
        if self.megacero.isChecked() == True:
            x11 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_megacero_2.text()), str(self.c13.currentText()))
            eval(x11)
        else:
            pass
        if self.ursidi.isChecked() == True:
            x12 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_ursidi_2.text()), str(self.c12.currentText()))
            eval(x12)
        else:
            pass
        if self.canidi.isChecked() == True:
            x13 = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, \"%s\", %s~1, locations=~coord_x+coord_y,archezoology_table, nmax = 10)')" % (
                str(self.lineEdit_canidi_2.text()), str(self.c11.currentText()))
            eval(x13)
        else:
            pass
            c = "r('VGM_PARAM_A3 <- gstat(VGM_PARAM_A3, fill.all=TRUE, model=vgm(%d,\"%s\",%s, nugget = %d, kappa= %s))')" % (
                int(self.psill.text()), str(self.model.currentText()), str(self.rang.text()), int(self.nugget_2.text()),
                str(self.kappa.text()))
            eval(c)
            d = "r('ESV_A3 <- variogram(VGM_PARAM_A3, map=TRUE, width=%s, cutoff=%d)')" % (
                str(self.lineEdit_width.text()), int(self.cutoff.text()))
            eval(d)
            r('VARMODEL_A3 = fit.lmc(ESV_A3, VGM_PARAM_A3)')
            a = "r('png(\"%s/A%d_semivariogram_map.png\", width=%d, height=%d, res=400); plot(ESV_A3, threshold = 5, col.regions = terrain.colors, model=vgm(%d,\"%s\",%s,%d),xlab=,ylab=, main=\"Linear Model of Coregionalization A%d\")')" % (
                str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us), int(self.set_size_plot.text()),
                int(self.set_size_plot.text()), int(self.psill.text()), str(self.model.currentText()),
                str(self.rang.text()), int(self.nugget_2.text()), int(self.DATA_LIST[i].us))
            eval(a)

    def on_automap_pressed(self):  #####modifiche apportate per il calcolo statistico con R
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
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
        n = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(n)
        con = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(con)

        r('coordinates(archezoology_table) =~coord_x+coord_y')

        kr = "r('kriging_result = autoKrige(%s~1, archezoology_table,model=c(\"%s\"),fix.values = c(%s,%s,%s))')" % (
            str(self.lineEdit_automap.currentText()), str(self.model_2.currentText()), str(self.nugget_3.text()),
            str(self.rang_2.text()), str(self.psill_2.text()))
        eval(kr)

        plotkr = "r('png(\"%s/A%d_kriging_%s.png\", width=3500, height=3500, res=400); plot(kriging_result)')" % (
            str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us), str(self.lineEdit_automap.currentText()))
        eval(plotkr)

        plot2 = "r('png(\"%s/A%d_kriging_predict_%s.png\", width=3500, height=3500, res=400); automapPlot(kriging_result$krige_output, \"var1.pred\", sp.layout = list(\"sp.points\", archezoology_table))')" % (
            str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us), str(self.lineEdit_automap.currentText()))
        eval(plot2)
        raster = "r('writeRaster(raster(kriging_result$krige_output),\"%s/A%d_kriging_predict_%s.tif\",\"GTiff\")')" % (
            str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us), str(self.lineEdit_automap.currentText()))
        eval(raster)
        add_map = "self.iface.addRasterLayer(\"%s/A%d_kriging_predict_%s.tif\")" % (
            str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us), str(self.lineEdit_automap.currentText()))
        eval(add_map)
        test = "r('verifica_errore <- krige.cv(%s~1, archezoology_table, model=vgm(%s,\"%s\",%s,%s),nfold=nrow(archezoology_table))')" % (
            str(self.lineEdit_automap.currentText()), str(self.psill_2.text()), str(self.model_2.currentText()),
            str(self.rang_2.text()), str(self.nugget_3.text()))
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
        error = "r('write.table(ME(verifica_errore),\"%s\ME.txt\");write.table(MSE(verifica_errore),\"%s\MSE.txt\");write.table(MSDR(verifica_errore),\"%s\MSDR.txt\")')" % (
            str(self.lineEdit_esp_generale.text()), str(self.lineEdit_esp_generale.text()),
            str(self.lineEdit_esp_generale.text()))
        eval(error)

    def on_report_pressed(self):
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
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
                temp_dataset = (int(self.DATA_LIST[i].us))

                contatore += int(self.DATA_LIST[i].us)  # conteggio totale

                dataset.append(temp_dataset)

            except:
                pass

        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('library(R2HTML)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(con)
        query = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(query)
        direc = "r('directory = setwd(\"%s\")')" % str(self.lineEdit_esp_generale.text())
        eval(direc)
        test1 = "r('myfile<-file.path(getwd(),\"%s.html\")')" % str(self.plot.currentText())
        eval(test1)
        test2 = "r('HTMLoutput=file.path(getwd(),\"%s.html\")')" % str(self.plot.currentText())
        eval(test2)
        nome = "r('graf=\"%s.png\"')" % str(self.plot.currentText())
        eval(nome)
        r('png(file.path(getwd(),graf))')
        data = "r('dat <- rnorm(archezoology_table$%s)')" % str(self.plot.currentText())
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
        plot = "r('plot(archezoology_table$coord_x,archezoology_table$coord_y, cex=cex,xlab=\"x axis\", ylab=\"y axis\", main=\"Pianta a dispersione di A%d - %s\", ylim=c(0,10), xlim=c(0,10), pch=1,col=\"red\")')" % (
            int(self.DATA_LIST[i].us), str(self.plot.currentText()))
        eval(plot)
        legend = "r('legend(9,10, pch = 1, c(1:%d),pt.cex = (1:%d/%d), cex = cex_size, col=\"red\")')" % (
            int(self.size.text()), int(self.size.text()), int(self.size.text()))
        eval(legend)
        r('dev.off()')
        test3 = "r('tab<-summary(archezoology_table[%d:%d])')" % (
            int(self.l1.currentText()), int(self.l2.currentText()))
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
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
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
                temp_dataset = (int(self.DATA_LIST[i].us))

                contatore += int(self.DATA_LIST[i].us)  # conteggio totale

                dataset.append(temp_dataset)

            except:
                pass

        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(con)

        query = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(query)

        histogram = "r('png(\"%s/%s_histogram.png\", width=2500, height=2500, res=400); hist(archezoology_table$%s, col=\"yellow\",xlab=\"Quantità\", ylab=\"Frequenza\",labels=TRUE, main=\"Distribuzione di frequenza %s\")')" % (
            str(self.lineEdit_esp_generale.text()), str(self.plot.currentText()), str(self.plot.currentText()),
            str(self.plot.currentText()))
        eval(histogram)
        abline1 = "r('abline(v=mean(archezoology_table$%s, na.rm=TRUE),col=\"red\", lwd=2)')" % str(
            self.plot.currentText())
        eval(abline1)
        abline2 = "r('abline(v=mean(archezoology_table$%s, na.rm=TRUE)+sd(archezoology_table$%s, na.rm=TRUE),col=3, lty=2)')" % (
            str(self.plot.currentText()), str(self.plot.currentText()))
        eval(abline2)
        abline3 = "r('abline(v=mean(archezoology_table$%s, na.rm=TRUE)-sd(archezoology_table$%s, na.rm=TRUE),col=3, lty=2)')" % (
            str(self.plot.currentText()), str(self.plot.currentText()))
        eval(abline3)

    def on_hist_period_pressed(self):
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
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
                temp_dataset = (int(self.DATA_LIST[i].us))

                contatore += int(self.DATA_LIST[i].us)  # conteggio totale

                dataset.append(temp_dataset)

            except:
                pass

        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(con)

        query = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us=%d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(query)

        histogram1 = "r('png(\"%s/A%d/histogram/test.png\", width=7000, height=3500, res=400)')" % (
            str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us))
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
        # Ora applico la funzione appena creata a 4 variabili del dataframe "dati.na"
        histogram2 = "r('do.it(archezoology_table$%s); title(\"%s\"); do.it(archezoology_table$%s); title(\"%s\"); do.it(archezoology_table$%s); title(\"%s\"); do.it(archezoology_table$%s); title(\"%s\"); par(op)')" % (
            str(self.c1_2.currentText()), str(self.c1_2.currentText()), str(self.c2_2.currentText()),
            str(self.c2_2.currentText()), str(self.c3_2.currentText()), str(self.c3_2.currentText()),
            str(self.c4_2.currentText()), str(self.c4_2.currentText()))
        eval(histogram2)

    def on_boxplot_pressed(self):
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
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
                temp_dataset = (int(self.DATA_LIST[i].us))

                contatore += int(self.DATA_LIST[i].us)  # conteggio totale

                dataset.append(temp_dataset)

            except:
                pass

        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(con)

        query = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us=%d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(query)

        boxplot = "r('png(\"%s/A%d/boxplot/%s_boxplot.png\", width=3500, height=3500, res=400)')" % (
            str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us), str(self.plot.currentText()))
        eval(boxplot)
        r('op=par(mar=c(0,5,0,0)); layout(matrix(c(1,1,1,2), nc=1))')
        codice = "r('a=archezoology_table$%s')" % str(self.plot.currentText())
        eval(codice)
        r(
            'y=ppoints(length(a));x=sort(a);plot(y ~ x, type=\"l\", lwd=2, ylab=\"percent\", main="");abline(h=c(0,.25,.5,.75,1), col=1, lwd=2,lty=3);abline(v=quantile(a), col=2, lwd=2, lty=2);abline(v=mean(a), col=3, lwd=1.5, lty=4);points(quantile(a), c(0,.25,.5,.75,1), lwd=5,col=4);legend(1000,0.1,"legend");boxplot(a, horizontal=TRUE, notch=FALSE, col=5, lwd=2, cex=2);abline(v=quantile(a), col=2, lwd=2, lty=2);abline(v=mean(a), col=3, lwd=1.5, lty=4)')
        r('par(op)')

    # q= "r('abline(v=mean(archezoology_table$%s), lty=2, col=4, lwd=4)')"%str(self.plot.currentText())
    # eval(q)
    # w= "r('abline(v=mean(archezoology_table$%s)+sd(archezoology_table$%s), lty=3, col=3, lwd=2)')"%(str(self.plot.currentText()), str(self.plot.currentText()))
    # eval(w)
    # e= "r('abline(v=mean(archezoology_table$%s)­-sd(archezoology_table$%s), lty=3, col=3, lwd=2)')"%(str(self.plot.currentText()), str(self.plot.currentText()))
    # eval(e)
    # r= "r('abline(v=median(archezoology_table$%s), lty=4, col=2, lwd=2)')"%str(self.plot.currentText())
    # eval(r)
    # t= "r('rug(archezoology_table$%s, col=\"red\")')"%str(self.plot.currentText())
    # eval(t)

    def on_coplot_pressed(self):
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
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
                temp_dataset = (int(self.DATA_LIST[i].us))

                contatore += int(self.DATA_LIST[i].us)  # conteggio totale

                dataset.append(temp_dataset)

            except:
                pass

        r = R()
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(con)
        query = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table\" )')"
        eval(query)

        coplot = "r('png(\"%s/%s_coplot.png\", width=3500, height=3500, res=400); coplot(coord_y ~ coord_x | us*%s , data= archezoology_table, overlap=0, cex=1,pch=20,col=4)')" % (
            str(self.lineEdit_esp_generale.text()), str(self.plot.currentText()), str(self.plot.currentText()))
        eval(coplot)

    def on_clipper_pressed(self):
        from tools.doClipper import GdalToolsDialog as Clipper
        d = Clipper(self.iface)
        self.runToolDialog(d)
        self.clipper = QAction(QIcon(":icons/raster-clip.png"), QCoreApplication.translate("GdalTools", "Clipper"),
                               self.iface.mainWindow())

    # self.clipper.setStatusTip( QCoreApplication.translate( "GdalTools", "Converts raster data between different formats") )
    # QObject.connect( self.clipper, SIGNAL( "triggered()" ), self.doClipper )

    def unload(self):
        if not valid: return
        pass

    def runToolDialog(self, dlg):
        dlg.show_()
        dlg.exec_()
        del dlg

    def doSettings(self):
        from tools.doSettings import GdalToolsSettingsDialog as Settings
        d = Settings(self.iface)
        d.exec_()

    def on_matrix_pressed(self):
        self.ITEMS = []
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.lineEdit_esp_generale.text())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo scegli la path. \n Aggiungi path per l'sportazione",
                                QMessageBox.Ok)
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
                temp_dataset = (int(self.DATA_LIST[i].us))

                contatore += int(self.DATA_LIST[i].us)  # conteggio totale

                dataset.append(temp_dataset)

            except:
                pass

        r = R()
        # r('load("/home/postgres/.RData")')
        r('library(RPostgreSQL)')
        r('library(lattice)')
        r('drv <- dbDriver("PostgreSQL")')
        con = "r('con <- dbConnect(drv, host=\"%s\", dbname=\"%s\", port=\"%d\", password=\"%s\", user=\"%s\")')" % (
            str(self.host.currentText()), str(self.db.text()), int(self.port.currentText()), str(self.password.text()),
            str(self.user.currentText()))
        eval(con)
        g = "r('png(\"%s/A%d_correlation_matrix.png\", width=2500, height=2500, pointsize=20)')" % (
            str(self.lineEdit_esp_generale.text()), int(self.DATA_LIST[i].us))
        eval(g)
        h = "r('archezoology_table<-dbGetQuery(con,\"select * from archeozoology_table where us = %d AND bos_bison IS NOT NULL\")')" % int(
            self.DATA_LIST[i].us)
        eval(h)

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

pairs(archezoology_table[9:18],
      lower.panel = panel.smooth,    # matrice inferiore: scatterplot
      upper.panel = panel.cor,       # matrice superiore: r Pearson e cor.test
      diag.panel = panel.hist)       # diagonale: istogrammi di frequenza

title(sub="Rosso = coppie con r>|0.5|, Verde = coppie con |0.25|<r<|0.5|;
      p.val verde scuro = coppie per cui si definisce r con una confidenza del 95%",
      cex.sub=0.7)
		''')  #### creazione ed esportazione della statistica descrittiva

    def on_tre_d_pressed(self):

        # layer.select([])
        # layer.setSelectedFeatures([obj.id() for obj in layer])
        # tre_d =''
        mylayer = self.iface.activeLayer()
        # self.iface.activeLayer().select([])
        # self.iface.activeLayer().setSelectedFeatures([obj.id() for obj in mylayer])
        # tre_d(mylayer)
        # edge_id = getIntAttributeByIndex(feature, edge_id_fno)
        if self.tab_5.text() == "":
            tab_5 = 0
        else:
            tab_5 = int(self.tab_5.text())

        from shapely.wkb import loads

        x = []
        y = []
        z = []
        for elem in mylayer.selectedFeatures():
            geom = elem.geometry()
            wkb = geom.asWkb()
            data = loads(wkb)

            x.append(data.x)
            y.append(data.y)
            z.append(0)

        x = []
        y = []
        z = []
        for elem in mylayer.selectedFeatures():
            geom = elem.geometry()
            x.append(geom.asPoint()[0])
            y.append(geom.asPoint()[1])
            tab = "(z.append(elem.attributes()[%d]))" % int(self.tab_5.text())
            eval(tab)

        fig = plt.figure()
        ax = Axes3D(fig)
        ax.scatter3D(x, y, z, c=z, cmap=plt.cm.jet)
        # self.widget.canvas.draw()
        plt.show()

        import visvis
        # abrir un ventana y visualizar los puntos
        f = visvis.gca()
        m = visvis.plot(x, y, z, lc='k', ls='', mc='g', mw=2, lw=2, ms='.')
        f.daspect = 1, 1, 10  # z x 10

        import numpy as np
        from matplotlib.mlab import griddata
        # création d'une grille 2D
        xi = np.linspace(min(x), max(x))
        yi = np.linspace(min(y), max(y))
        X, Y = np.meshgrid(xi, yi)
        # interpolation
        Z = griddata(x, y, z, xi, yi)
        # fig = plt.figure()
        # ax = Axes3D(fig)
        # ax.plot_surface(X, Y, Z, rstride=1, cstride=1,cmap=cm.jet,linewidth=1, antialiased=True)
        # self.widget.canvas.draw()
        # plt.show()

        f = visvis.gca()
        m = visvis.grid(xi, yi, Z)  # o m= =visvis.grid(yi,xi,Z) con una antigua versión
        f.daspect = 1, 1, 10  # z x 10
        m = visvis.surf(xi, yi, Z)
        m.colormap = visvis.CM_JET

        import scipy as sp
        # construction de la grille
        spline = sp.interpolate.Rbf(x, y, z, function='thin-plate')
        xi = np.linspace(min(x), max(x))
        yi = np.linspace(min(y), max(y))
        X, Y = np.meshgrid(xi, yi)
        # interpolation
        Z = spline(X, Y)
        f = visvis.gca()
        m = visvis.surf(xi, yi, Z)
        m.colormap = visvis.CM_JET
        f.axis.visible = True

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                QMessageBox.Ok)
        else:
            if self.lineEdit_us.text() == "":
                us = ''
            else:
                us = int(self.lineEdit_us.text())

            if self.lineEdit_coord_x.text() == "":
                coord_x = ''
            else:
                coord_x = int(self.lineEdit_coord_x.text())

            if self.lineEdit_coord_y.text() == "":
                coord_y = ''
            else:
                coord_y = int(self.lineEdit_coord_y.text())

            if self.lineEdit_coord_z.text() == "":
                coord_z = ''
            else:
                coord_z = int(self.lineEdit_coord_z.text())

            if self.lineEdit_bos_bison.text() == "":
                bos_bison = ''
            else:
                bos_bison = int(self.lineEdit_bos_bison.text())

            if self.lineEdit_calcinati.text() == "":
                calcinati = ''
            else:
                calcinati = int(self.lineEdit_calcinati.text())

            if self.lineEdit_camoscio.text() == "":
                camoscio = ''
            else:
                camoscio = int(self.lineEdit_camoscio.text())

            if self.lineEdit_capriolo.text() == "":
                capriolo = ''
            else:
                capriolo = int(self.lineEdit_capriolo.text())

            if self.lineEdit_cervi.text() == "":
                cervo = ''
            else:
                cervo = int(self.lineEdit_cervi.text())

            if self.lineEdit_combuste.text() == "":
                combusto = ''
            else:
                combusto = int(self.lineEdit_combuste.text())

            if self.lineEdit_Coni.text() == "":
                coni = ''
            else:
                coni = int(self.lineEdit_Coni.text())

            if self.lineEdit_pdi.text() == "":
                pdi = ''
            else:
                pdi = int(self.lineEdit_pdi.text())

            if self.lineEdit_stambecco.text() == "":
                stambecco = ''
            else:
                stambecco = int(self.lineEdit_stambecco.text())

            if self.lineEdit_strie.text() == "":
                strie = ''
            else:
                strie = int(self.lineEdit_strie.text())

            if self.lineEdit_canidi.text() == "":
                canidi = ''
            else:
                canidi = int(self.lineEdit_canidi.text())

            if self.lineEdit_ursidi.text() == "":
                ursidi = ''
            else:
                ursidi = int(self.lineEdit_ursidi.text())

            if self.lineEdit_megacero.text() == "":
                megacero = ''
            else:
                megacero = int(self.lineEdit_megacero.text())

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: "'" + str(self.lineEdit_area.text()) + "'",  # 2 - Area
                self.TABLE_FIELDS[2]: us,  # 3 - US
                self.TABLE_FIELDS[3]: "'" + str(self.lineEdit_quadrato.text()) + "'",  # 4 - Definizione stratigrafica
                self.TABLE_FIELDS[4]: coord_x,  # 5 - Definizione intepretata
                self.TABLE_FIELDS[5]: coord_y,  # 6 - descrizione
                self.TABLE_FIELDS[6]: coord_z,  # 7 - interpretazione
                self.TABLE_FIELDS[7]: bos_bison,  # 8 - periodo iniziale
                self.TABLE_FIELDS[8]: calcinati,  # 9 - fase iniziale
                self.TABLE_FIELDS[9]: camoscio,  # 10 - periodo finale iniziale
                self.TABLE_FIELDS[10]: capriolo,  # 11 - fase finale
                self.TABLE_FIELDS[11]: cervo,  # 12 - attivita
                self.TABLE_FIELDS[12]: combusto,  # 13 - attivita
                self.TABLE_FIELDS[13]: coni,  # 14 - anno scavo
                self.TABLE_FIELDS[14]: pdi,  # 15 - metodo
                self.TABLE_FIELDS[15]: stambecco,  # 16 - data schedatura
                self.TABLE_FIELDS[16]: strie,  # 17 - schedatore
                self.TABLE_FIELDS[17]: canidi,  # 18 - formazione
                self.TABLE_FIELDS[18]: ursidi,  # 19 - conservazione
                self.TABLE_FIELDS[19]: megacero,  # 20 - colore
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if bool(search_dict) == False:
                QMessageBox.warning(self, "ATTENZIONE", "Non e' stata impostata alcuna ricerca!!!", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if bool(res) == False:
                    QMessageBox.warning(self, "ATTENZIONE", "Non è¨ stato trovato nessun record!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.lineEdit_area"], "False")
                    self.setComboBoxEnable(["self.lineEdit_us"], "False")
                    self.setComboBoxEnable(["self.lineEdit_quadrato"], "False")

                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

                    if self.REC_TOT == 1:
                        strings = ("E' stato trovato", self.REC_TOT, "record")
                        if self.toolButtonGis.isChecked() == True:
                            self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")
                        if self.toolButtonGis.isChecked() == True:
                            self.pyQGIS.charge_vector_layers(self.DATA_LIST)

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.lineEdit_area"], "False")
                    self.setComboBoxEnable(["self.lineEdit_us"], "False")
                    self.setComboBoxEnable(["self.lineEdit_quadrato"], "False")

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
        self.enable_button_search(1)

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        self.msg = msg
        if self.msg == 1:
            self.update_record()
            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
            self.DATA_LIST = []
            if self.SORT_STATUS == "n":
                # self.testing('test_sort.txt', 'qua')
                temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                            self.ID_TABLE)
            else:
                temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                            self.MAPPER_TABLE_CLASS, self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR

    # custom functions
    def charge_records(self):
        self.DATA_LIST = []
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
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if bool(value) == True:
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista

    def empty_fields(self):
        self.comboBox_sito.setEditText("")
        self.lineEdit_area.clear()
        self.lineEdit_us.clear()
        self.lineEdit_quadrato.clear()
        self.lineEdit_coord_x.clear()
        self.lineEdit_coord_y.clear()
        self.lineEdit_coord_z.clear()
        self.lineEdit_bos_bison.clear()
        self.lineEdit_calcinati.clear()
        self.lineEdit_camoscio.clear()
        self.lineEdit_capriolo.clear()
        self.lineEdit_cervi.clear()
        self.lineEdit_combuste.clear()
        self.lineEdit_Coni.clear()
        self.lineEdit_pdi.clear()
        self.lineEdit_stambecco.clear()
        self.lineEdit_strie.clear()
        self.lineEdit_canidi.clear()
        self.lineEdit_ursidi.clear()
        self.lineEdit_megacero.clear()

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito)  # 1 - Sito
            self.lineEdit_area.setText(str(self.DATA_LIST[self.rec_num].area))  # 2 - Periodo

            if self.DATA_LIST[self.rec_num].us == None:  # 4 - cronologia iniziale
                self.lineEdit_us.setText("")
            else:
                self.lineEdit_us.setText(str(self.DATA_LIST[self.rec_num].us))

            # 2 - Periodo
            self.lineEdit_quadrato.setText(str(self.DATA_LIST[self.rec_num].quadrato))  # 2 - Periodo

            if self.DATA_LIST[self.rec_num].coord_x == None:  # 4 - cronologia iniziale
                self.lineEdit_coord_x.setText("")
            else:
                self.lineEdit_coord_x.setText(str(self.DATA_LIST[self.rec_num].coord_x))

            if self.DATA_LIST[self.rec_num].coord_y == None:  # 4 - cronologia iniziale
                self.lineEdit_coord_y.setText("")
            else:
                self.lineEdit_coord_y.setText(str(self.DATA_LIST[self.rec_num].coord_y))

            if self.DATA_LIST[self.rec_num].coord_z == None:  # 4 - cronologia iniziale
                self.lineEdit_coord_z.setText("")
            else:
                self.lineEdit_coord_z.setText(str(self.DATA_LIST[self.rec_num].coord_z))

            if self.DATA_LIST[self.rec_num].bos_bison == None:  # 4 - cronologia iniziale
                self.lineEdit_bos_bison.setText("")
            else:
                self.lineEdit_bos_bison.setText(str(self.DATA_LIST[self.rec_num].bos_bison))

            if self.DATA_LIST[self.rec_num].calcinati == None:  # 4 - cronologia iniziale
                self.lineEdit_calcinati.setText("")
            else:
                self.lineEdit_calcinati.setText(str(self.DATA_LIST[self.rec_num].calcinati))

            if self.DATA_LIST[self.rec_num].camoscio == None:  # 4 - cronologia iniziale
                self.lineEdit_camoscio.setText("")
            else:
                self.lineEdit_camoscio.setText(str(self.DATA_LIST[self.rec_num].camoscio))

            if self.DATA_LIST[self.rec_num].capriolo == None:  # 4 - cronologia iniziale
                self.lineEdit_capriolo.setText("")
            else:
                self.lineEdit_capriolo.setText(str(self.DATA_LIST[self.rec_num].capriolo))

            if self.DATA_LIST[self.rec_num].cervo == None:  # 4 - cronologia iniziale
                self.lineEdit_cervi.setText("")
            else:
                self.lineEdit_cervi.setText(str(self.DATA_LIST[self.rec_num].cervo))

            if self.DATA_LIST[self.rec_num].combusto == None:  # 4 - cronologia iniziale
                self.lineEdit_combuste.setText("")
            else:
                self.lineEdit_combuste.setText(str(self.DATA_LIST[self.rec_num].combusto))

            if self.DATA_LIST[self.rec_num].coni == None:  # 4 - cronologia iniziale
                self.lineEdit_Coni.setText("")
            else:
                self.lineEdit_Coni.setText(str(self.DATA_LIST[self.rec_num].coni))

            if self.DATA_LIST[self.rec_num].pdi == None:  # 4 - cronologia iniziale
                self.lineEdit_pdi.setText("")
            else:
                self.lineEdit_pdi.setText(str(self.DATA_LIST[self.rec_num].pdi))

            if self.DATA_LIST[self.rec_num].stambecco == None:  # 4 - cronologia iniziale
                self.lineEdit_stambecco.setText("")
            else:
                self.lineEdit_stambecco.setText(str(self.DATA_LIST[self.rec_num].stambecco))

            if self.DATA_LIST[self.rec_num].strie == None:  # 4 - cronologia iniziale
                self.lineEdit_strie.setText("")
            else:
                self.lineEdit_strie.setText(str(self.DATA_LIST[self.rec_num].strie))

            if self.DATA_LIST[self.rec_num].canidi == None:  # 4 - cronologia iniziale
                self.lineEdit_canidi.setText("")
            else:
                self.lineEdit_canidi.setText(str(self.DATA_LIST[self.rec_num].canidi))

            if self.DATA_LIST[self.rec_num].ursidi == None:  # 4 - cronologia iniziale
                self.lineEdit_ursidi.setText("")
            else:
                self.lineEdit_ursidi.setText(str(self.DATA_LIST[self.rec_num].ursidi))

            if self.DATA_LIST[self.rec_num].megacero == None:  # 4 - cronologia iniziale
                self.lineEdit_megacero.setText("")
            else:
                self.lineEdit_megacero.setText(str(self.DATA_LIST[self.rec_num].megacero))

        except Exception as e:
            QMessageBox.warning(self, "Errore Fill Fields", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # data
        if self.lineEdit_us.text() == "":
            us = None
        else:
            us = str(self.lineEdit_us.text())

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

        if self.lineEdit_bos_bison.text() == "":
            bos_bison = None
        else:
            bos_bison = str(self.lineEdit_bos_bison.text())

        if self.lineEdit_calcinati.text() == "":
            calcinati = None
        else:
            calcinati = str(self.lineEdit_calcinati.text())

        if self.lineEdit_camoscio.text() == "":
            camoscio = None
        else:
            camoscio = str(self.lineEdit_camoscio.text())

        if self.lineEdit_capriolo.text() == "":
            capriolo = None
        else:
            capriolo = str(self.lineEdit_capriolo.text())

        if self.lineEdit_cervi.text() == "":
            cervo = None
        else:
            cervo = str(self.lineEdit_cervi.text())

        if self.lineEdit_combuste.text() == "":
            combusto = None
        else:
            combusto = str(self.lineEdit_combuste.text())

        if self.lineEdit_Coni.text() == "":
            coni = None
        else:
            coni = str(self.lineEdit_Coni.text())

        if self.lineEdit_pdi.text() == "":
            pdi = None
        else:
            pdi = str(self.lineEdit_pdi.text())

        if self.lineEdit_stambecco.text() == "":
            stambecco = None
        else:
            stambecco = str(self.lineEdit_stambecco.text())

        if self.lineEdit_strie.text() == "":
            strie = None
        else:
            strie = str(self.lineEdit_strie.text())

        if self.lineEdit_canidi.text() == "":
            canidi = None
        else:
            canidi = str(self.lineEdit_canidi.text())

        if self.lineEdit_ursidi.text() == "":
            ursidi = None
        else:
            ursidi = str(self.lineEdit_ursidi.text())

        if self.lineEdit_megacero.text() == "":
            megacero = None
        else:
            megacero = str(self.lineEdit_megacero.text())

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.lineEdit_area.text()),  # 2 - periodo
            str(us),
            str(self.lineEdit_quadrato.text()),  # 3 - fase
            str(coord_x),
            str(coord_y),
            str(coord_z),
            str(bos_bison),
            str(calcinati),
            str(camoscio),
            str(capriolo),
            str(cervo),
            str(combusto),
            str(coni),
            str(pdi),
            str(stambecco),
            str(strie),
            str(canidi),
            str(ursidi),
            str(megacero)]  # 8 - cont_per provvisorio

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
                               [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
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
