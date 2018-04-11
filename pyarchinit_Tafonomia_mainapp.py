#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import *
from qgis.gui import *

from .modules.db.pyarchinit_conn_strings import Connection
from .modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from .modules.db.pyarchinit_utility import Utility
from .modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from .modules.utility.pyarchinit_error_check import Error_check
from .modules.utility.pyarchinit_exp_Tafonomiasheet_pdf import generate_tafonomia_pdf
from .modules.utility.pyarchinit_exp_USsheet_pdf import *
from .sortpanelmain import SortPanelMain

# --import pyArchInit modules--#
try:
    from pyarchinit_matrix_exp import *
except:
    pass

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'modules', 'gui', 'pyarchinit_Tafonomia_ui.ui'))


class pyarchinit_Tafonomia(QDialog, MAIN_DIALOG_CLASS):
    MSG_BOX_TITLE = "PyArchInit - Scheda Tafonomica"
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
    SORT_ITEMS_CONVERTED = ''
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'Tafonomia_table'
    MAPPER_TABLE_CLASS = "TAFONOMIA"
    NOME_SCHEDA = "Scheda Tafonomica"
    ID_TABLE = "id_tafonomia"
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Sito": "sito",
        "Numero scheda": "nr_scheda_taf",
        "Sigla struttura": "sigla_struttura",
        "Nr struttura": "nr_struttura",
        "Nr Individuo": "nr_individuo",
        "Rito": "rito",
        "Decrizione": "descrizione_taf",
        "Interpretazione": "interpretazione_taf",
        "Segnacoli": "segnacoli",
        "Canale libatorio": "canale_libatorio_si_no",
        "Oggetti esterni rinvenuti": "oggetti_rinvenuti_esterno",
        "Stato di conservazione": "stato_di_conservazione",
        "Tipo di copertura": "copertura_tipo",
        "Tipo contenitore resti": "tipo_contenitore_resti",
        "Orientamento asse": "orientamento_asse",
        "Orientament Azimut": "orientamento_azimut",
        "Presenza del corredo": "corredo_presenza",
        "Tipo di corredo": "corredo_tipo",
        "Descrizione corredo": "corredo_descrizione",
        "Lunghezza scheletro": "lunghezza_scheletro",
        "Posizione scheletro": "posizione_scheletro",
        "Posizione cranio": "posizione_cranio",
        "Posizione arti superiori": "posizione_arti_superiori",
        "Posizione arti inferiori": "posizione_arti_inferiori",
        "Completo": "completo_si_no",
        "Disturbato": "disturbato_si_no",
        "In connessione": "in_connessione_si_no",
        "Caratteristiche": "caratteristiche",
        "Periodo iniziale": "periodo_iniziale",
        "Fase iniziale": "fase_iniziale",
        "Periodo finale": "periodo_finale",
        "Fase finale": "fase_finale",
        "Datazione estesa": "datazione_estesa"
    }

    SORT_ITEMS = [
        ID_TABLE,
        "Sito",
        "Numero scheda",
        "Sigla struttura",
        "Nr struttura",
        "Nr Individuo",
        "Rito",
        "Decrizione",
        "Interpretazione",
        "Segnacoli",
        "Canale libatorio",
        "Oggetti esterni rinvenuti",
        "Stato di conservazione",
        "Tipo di copertura",
        "Tipo contenitore resti",
        "Orientamento asse",
        "Orientament Azimut",
        "Presenza del corredo",
        "Tipo di corredo",
        "Descrizione corredo",
        "Lunghezza scheletro",
        "Posizione scheletro",
        "Posizione cranio",
        "Posizione arti superiori",
        "Posizione arti inferiori",
        "Completo",
        "Disturbato",
        "In connessione",
        "Caratteristiche",
        "Periodo iniziale",
        "Fase iniziale",
        "Periodo finale",
        "Fase finale",
        "Datazione estesa"
    ]

    TABLE_FIELDS = [
        "sito",
        "nr_scheda_taf",
        "sigla_struttura",
        "nr_struttura",
        "nr_individuo",
        "rito",
        "descrizione_taf",
        "interpretazione_taf",
        "segnacoli",
        "canale_libatorio_si_no",
        "oggetti_rinvenuti_esterno",
        "stato_di_conservazione",
        "copertura_tipo",
        "tipo_contenitore_resti",
        "orientamento_asse",
        "orientamento_azimut",
        "corredo_presenza",
        "corredo_tipo",
        "corredo_descrizione",
        "lunghezza_scheletro",
        "posizione_scheletro",
        "posizione_cranio",
        "posizione_arti_superiori",
        "posizione_arti_inferiori",
        "completo_si_no",
        "disturbato_si_no",
        "in_connessione_si_no",
        "caratteristiche",
        "periodo_iniziale",
        "fase_iniziale",
        "periodo_finale",
        "fase_finale",
        "datazione_estesa",
        "misure_tafonomia"
    ]

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
            QMessageBox.warning(self, "Sistema di connessione", str(e), QMessageBox.Ok)
        self.customize_GUI()  # call for GUI customizations

        # SIGNALS & SLOTS Functions
        self.comboBox_sito.currentIndexChanged.connect(self.charge_struttura_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_individuo_list)

        # SIGNALS & SLOTS Functions
        self.comboBox_sito.editTextChanged .connect(self.charge_periodo_iniz_list)
        self.comboBox_sito.editTextChanged .connect(self.charge_periodo_fin_list)

        self.comboBox_sito.currentIndexChanged.connect(self.charge_periodo_iniz_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_periodo_fin_list)

        self.comboBox_per_iniz.editTextChanged .connect(self.charge_fase_iniz_list)
        self.comboBox_per_iniz.currentIndexChanged.connect(self.charge_fase_iniz_list)

        self.comboBox_per_fin.editTextChanged .connect(self.charge_fase_fin_list)
        self.comboBox_per_fin.currentIndexChanged.connect(self.charge_fase_fin_list)

        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        self.charge_periodo_iniz_list()
        self.charge_periodo_fin_list()
        self.fill_fields()

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
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort_2.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                QMessageBox.warning(self, "BENVENUTO",
                                    "Benvenuto in pyArchInit" + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                    QMessageBox.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "La connessione e' fallita <br><br> %s. E' NECESSARIO RIAVVIARE QGIS" % (str(e)),
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e),
                                    QMessageBox.Ok)

    def customize_GUI(self):
        self.tableWidget_caratteristiche.setColumnWidth(1, 300)
        self.tableWidget_caratteristiche.setColumnWidth(1, 200)

        # comboBox customizations
        self.setComboBoxEditable(["self.comboBox_sito"], 1)
        self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
        self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
        self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
        self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "False")

        """soluzione provvisoria"""
        self.setComboBoxEditable(["self.comboBox_in_connessione"], 1)
        self.setComboBoxEditable(["self.comboBox_disturbato"], 1)
        self.setComboBoxEditable(["self.comboBox_completo"], 1)

        self.setComboBoxEditable(["self.comboBox_per_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_iniz"], 1)
        self.setComboBoxEditable(["self.comboBox_per_fin"], 1)
        self.setComboBoxEditable(["self.comboBox_fas_fin"], 1)

    def loadMapPreview(self, mode=0):
        if mode == 0:
            """ if has geometry column load to map canvas """

            gidstr = self.ID_TABLE + " = " + str(
                eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            layerToSet = self.pyQGIS.loadMapPreview(gidstr)
            self.mapPreview.setLayerSet(layerToSet)
            self.mapPreview.zoomToFullExtent()

        elif mode == 1:
            self.mapPreview.setLayerSet([])
            self.mapPreview.zoomToFullExtent()

    def loadMediaPreview(self, mode=0):
        pass

    def openWide_image(self):
        pass

    def charge_list(self):
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Sito: " + str(e), QMessageBox.Ok)

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

    def charge_periodo_iniz_list(self):
        sito = str(self.comboBox_sito.currentText())

        search_dict = {
            'sito': "'" + sito + "'"
        }

        periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

        periodo_list = []

        for i in range(len(periodo_vl)):
            periodo_list.append(str(periodo_vl[i].periodo))
        try:
            periodo_vl.remove('')
        except:
            pass

        self.comboBox_per_iniz.clear()
        self.comboBox_per_iniz.addItems(self.UTILITY.remove_dup_from_list(periodo_list))

        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova":
            self.comboBox_per_iniz.setEditText("")
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa":
            if len(self.DATA_LIST) > 0:
                try:
                    self.comboBox_per_iniz.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                except:
                    pass  # non vi sono periodi per questo scavo

    def charge_periodo_fin_list(self):
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'"
        }

        periodo_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')
        periodo_list = []

        for i in range(len(periodo_vl)):
            periodo_list.append(str(periodo_vl[i].periodo))
        try:
            periodo_vl.remove('')
        except:
            pass

        self.comboBox_per_fin.clear()
        self.comboBox_per_fin.addItems(self.UTILITY.remove_dup_from_list(periodo_list))

        if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova":
            self.comboBox_per_fin.setEditText("")
        elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa":
            if len(self.DATA_LIST) > 0:
                try:
                    self.comboBox_per_fin.setEditText(self.DATA_LIST[self.rec_num].periodo_iniziale)
                except:
                    pass

    def charge_fase_iniz_list(self):
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_iniz.currentText()) + "'",
            }

            fase_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

            fase_list = []

            for i in range(len(fase_list_vl)):
                fase_list.append(str(fase_list_vl[i].fase))
            try:
                fase_list.remove('')
            except:
                pass

            self.comboBox_fas_iniz.clear()

            fase_list.sort()
            self.comboBox_fas_iniz.addItems(self.UTILITY.remove_dup_from_list(fase_list))

            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova":
                self.comboBox_fas_iniz.setEditText("")
            else:
                self.comboBox_fas_iniz.setEditText(self.DATA_LIST[self.rec_num].fase_iniziale)
        except:
            pass

    def charge_fase_fin_list(self):
        try:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'periodo': "'" + str(self.comboBox_per_fin.currentText()) + "'",
            }

            fase_list_vl = self.DB_MANAGER.query_bool(search_dict, 'PERIODIZZAZIONE')

            fase_list = []

            for i in range(len(fase_list_vl)):
                fase_list.append(str(fase_list_vl[i].fase))
            try:
                fase_list.remove('')
            except:
                pass

            self.comboBox_fas_fin.clear()
            fase_list.sort()
            self.comboBox_fas_fin.addItems(self.UTILITY.remove_dup_from_list(fase_list))

            if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova":
                self.comboBox_fas_fin.setEditText("")
            else:
                self.comboBox_fas_fin.setEditText(self.DATA_LIST[self.rec_num].fase_finale)
        except:
            pass

    def charge_struttura_list(self):
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
        }

        struttura_vl = self.DB_MANAGER.query_bool(search_dict, 'STRUTTURA')

        # carica il tipo di struttura
        sigla_struttura_list = []

        for i in range(len(struttura_vl)):
            sigla_struttura_list.append(str(struttura_vl[i].sigla_struttura))
        try:
            sigla_struttura_list.remove('')
        except:
            pass

        sigla_struttura_list.sort()

        self.comboBox_sigla_struttura.clear()
        self.comboBox_sigla_struttura.addItems(sigla_struttura_list)
        try:
            self.comboBox_sigla_struttura.setEditText(str(self.DATA_LIST[self.rec_num].sigla_struttura))
        except:
            pass

        nr_struttura_list = []

        for i in range(len(struttura_vl)):
            nr_struttura_list.append(str(struttura_vl[i].numero_struttura))
        try:
            nr_struttura_list.remove('')
        except:
            pass

        nr_struttura_list.sort()

        self.comboBox_nr_struttura.clear()
        self.comboBox_nr_struttura.addItems(nr_struttura_list)
        try:
            self.comboBox_nr_struttura.setEditText(self.DATA_LIST[self.rec_num].numero_struttura)
        except:
            pass

    def charge_individuo_list(self):
        search_dict = {
            'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
        }

        individuo_vl = self.DB_MANAGER.query_bool(search_dict, 'SCHEDAIND')

        # carica il tipo di individuo
        nr_individuo_list = []

        for i in range(len(individuo_vl)):
            nr_individuo_list.append(str(individuo_vl[i].nr_individuo))
        try:
            nr_individuo_list.remove('')
        except:
            pass

        nr_individuo_list.sort()

        self.comboBox_nr_individuo.clear()
        self.comboBox_nr_individuo.addItems(nr_individuo_list)
        try:
            self.comboBox_nr_individuo.setEditText(self.DATA_LIST[self.rec_num].nr_individuo)
        except:
            pass

            # buttons functions

    def on_pushButton_exp_index_pressed(self):
        Tafonomia_index_pdf = generate_tafonomia_pdf()
        data_list = self.generate_list_pdf()
        Tafonomia_index_pdf.build_index_Tafonomia(data_list, data_list[0][0])

    def on_toolButtonPan_toggled(self):
        self.toolPan = QgsMapToolPan(self.mapPreview)
        self.mapPreview.setMapTool(self.toolPan)

    def on_pushButton_showSelectedFeatures_pressed(self):
        field_position = self.pyQGIS.findFieldFrDict(self.ID_TABLE)

        field_list = self.pyQGIS.selectedFeatures()

        id_list_sf = self.pyQGIS.findItemInAttributeMap(field_position, field_list)
        id_list = []
        for idl in id_list_sf:
            sid = idl.toInt()
            id_list.append(sid[0])

        items, order_type = [self.ID_TABLE], "asc"
        self.empty_fields()

        self.DATA_LIST = []

        temp_data_list = self.DB_MANAGER.query_sort(id_list, items, order_type, self.MAPPER_TABLE_CLASS, self.ID_TABLE)

        for us in temp_data_list:
            self.DATA_LIST.append(us)

        self.fill_fields()
        self.BROWSE_STATUS = 'b'
        self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<type 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR

        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
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
            self.BROWSE_STATUS = 'b'
            self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR

            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort_2.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()

    def on_toolButtonGis_toggled(self):
        if self.toolButtonGis.isChecked():
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' GIS attiva. Da ora le tue ricerche verranno visualizzate sul GIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' GIS disattivata. Da ora le tue ricerche non verranno piu' visualizzate sul GIS",
                                QMessageBox.Ok)

    def on_toolButtonPreview_toggled(self):
        if self.toolButtonPreview.isChecked():
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' Preview US attivata. Le piante delle US saranno visualizzate nella sezione Piante",
                                QMessageBox.Ok)
            self.loadMapPreview()
        else:
            self.loadMapPreview(1)

    def on_toolButtonPreviewMedia_toggled(self):
        if self.toolButtonPreviewMedia.isChecked():
            QMessageBox.warning(self, "Messaggio",
                                "Modalita' Preview Media US attivata. Le immagini delle US saranno visualizzate nella sezione Media",
                                QMessageBox.Ok)
            self.loadMediaPreview()
        else:
            self.loadMediaPreview(1)

    def on_pushButton_addRaster_pressed(self):
        if self.toolButtonGis.isChecked():
            self.pyQGIS.addRasterLayer()

    def on_pushButton_new_rec_pressed(self):
        # set the GUI for a new record
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
                        if self.records_equal_check() == 1:
                            msg = self.update_if(QMessageBox.warning(self, 'Errore',
                                                                     "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                                     QMessageBox.Cancel, 1))

        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()

            self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "True")

            self.setComboBoxEditable(["self.comboBox_sito"], 0)
            self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
            self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
            self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)

            self.setComboBoxEnable(["self.comboBox_sito"], "True")
            self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "True")
            self.setComboBoxEnable(["self.comboBox_nr_struttura"], "True")
            self.setComboBoxEnable(["self.comboBox_nr_individuo"], "True")

            self.SORT_STATUS = "n"
            self.label_sort_2.setText(self.SORTED_ITEMS[self.SORT_STATUS])

            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    self.update_if(QMessageBox.warning(self, 'ATTENZIONE',
                                                       "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                       QMessageBox.Cancel, 1))
                    self.SORT_STATUS = "n"
                    self.label_sort_2.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort_2.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
                    self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "False")
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_struttura"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_individuo"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
            QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto", QMessageBox.Ok)
            test = 1

        return test

    def insert_new_rec(self):
        ##Caratteristiche
        caratteristiche = self.table2dict("self.tableWidget_caratteristiche")
        ##
        corredo_tipo = self.table2dict("self.tableWidget_corredo_tipo")
        ##Misurazioni
        misurazioni = self.table2dict("self.tableWidget_misurazioni")

        ##orientamento azimut
        if self.lineEdit_orientamento_azimut.text() == "":
            orientamento_azimut = None
        else:
            orientamento_azimut = float(self.lineEdit_orientamento_azimut.text())

        ##lunghezza scheletro
        if self.lineEdit_lunghezza_scheletro.text() == "":
            lunghezza_scheletro = None
        else:
            lunghezza_scheletro = float(self.lineEdit_lunghezza_scheletro.text())

        if self.comboBox_per_iniz.currentText() == "":
            per_iniz = None
        else:
            per_iniz = int(self.comboBox_per_iniz.currentText())

        if self.comboBox_fas_iniz.currentText() == "":
            fas_iniz = None
        else:
            fas_iniz = int(self.comboBox_fas_iniz.currentText())

        if self.comboBox_per_fin.currentText() == "":
            per_fin = None
        else:
            per_fin = int(self.comboBox_per_fin.currentText())

        if self.comboBox_fas_fin.currentText() == "":
            fas_fin = None
        else:
            fas_fin = int(self.comboBox_fas_fin.currentText())

        try:
            # data
            data = self.DB_MANAGER.insert_values_tafonomia(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),  # 1 - Sito
                int(self.lineEdit_nr_scheda.text()),  # 2 - nr scheda tafonomica
                str(self.comboBox_sigla_struttura.currentText()),  # 3 - tipo struttura
                int(self.comboBox_nr_struttura.currentText()),  # 4 - nr struttura
                int(self.comboBox_nr_individuo.currentText()),  # 5 - nr  individuo
                str(self.comboBox_rito.currentText()),  # 6 - rito
                str(self.textEdit_descrizione_taf.toPlainText()),  # 7 - descrizione
                str(self.textEdit_interpretazione_taf.toPlainText()),  # 8 - interpretazione
                str(self.comboBox_segnacoli.currentText()),  # 9 - segnacoli
                str(self.comboBox_canale_libatorio.currentText()),  # 10 - canale libatorio
                str(self.comboBox_oggetti_esterno.currentText()),  # 11 - oggetti esterno
                str(self.comboBox_conservazione_taf.currentText()),  # 12 - conservazione
                str(self.comboBox_copertura_tipo.currentText()),  # 13 - copertura
                str(self.comboBox_tipo_contenitore_resti.currentText()),  # 14 - tipo contenitore resti
                str(self.lineEdit_orientamento_asse.text()),  # 15 - orientamento asse
                orientamento_azimut,  # 16 - orientamento azimut
                str(self.comboBox_corredo_presenza.currentText()),  # 17 - corredo presenza
                str(corredo_tipo),  # 18 - corredo tipo
                str(self.textEdit_descrizione_corredo.toPlainText()),  # 19 - descrizione corredo
                lunghezza_scheletro,  # 20 - lunghezza scheletro
                str(self.comboBox_posizione_scheletro.currentText()),  # 21 - posizione scheletro
                str(self.comboBox_posizione_cranio.currentText()),  # 22 - posizione cranio
                str(self.comboBox_arti_superiori.currentText()),  # 23 - arti inferiori
                str(self.comboBox_arti_inferiori.currentText()),  # 24 - arti superiori
                str(self.comboBox_completo.currentText()),  # 25 - completo
                str(self.comboBox_disturbato.currentText()),  # 26 - disturbato
                str(self.comboBox_in_connessione.currentText()),  # 27 - in connessione
                str(caratteristiche),  # 28 - caratteristiche
                per_iniz,  # 29 - periodo iniziale
                fas_iniz,  # 30 - fase iniziale
                per_fin,  # 31 - periodo finale iniziale
                fas_fin,  # 32 - fase finale
                str(self.lineEdit_datazione_estesa.text()),  # 33 - datazione estesa
                str(misurazioni))  # 34 - misurazioni

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " gia' presente nel database"
                else:
                    msg = e
                QMessageBox.warning(self, "Errore imm1", "Errore di immisione 1 \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Errore imm2", "Errore di immisione 2 \n" + str(e), QMessageBox.Ok)
            return 0

            # insert new row into tableWidget

    def on_pushButton_insert_row_corredo_pressed(self):
        self.insert_new_row('self.tableWidget_corredo_tipo')

    def on_pushButton_remove_row_corredo_pressed(self):
        self.remove_row('self.tableWidget_corredo_tipo')

    def on_pushButton_insert_row_caratteristiche_pressed(self):
        self.insert_new_row('self.tableWidget_caratteristiche')

    def on_pushButton_remove_row_caratteristiche_pressed(self):
        self.remove_row('self.tableWidget_caratteristiche')

    def on_pushButton_insert_row_misure_pressed(self):
        self.insert_new_row('self.tableWidget_misurazioni')

    def on_pushButton_remove_row_misure_pressed(self):
        self.remove_row('self.tableWidget_misurazioni')

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            self.update_if(
                QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                    QMessageBox.Cancel, 1))
            # self.charge_records() incasina lo stato trova
            return 0  # non ci sono errori di immissione

            # records surf functions

    def on_pushButton_view_all_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.empty_fields()
            self.charge_records()
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.label_sort_2.setText(self.SORTED_ITEMS["n"])

    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e), QMessageBox.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
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
        if self.check_record_state() == 1:
            pass
        else:
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
            if not bool(self.DATA_LIST):
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
                # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                self.BROWSE_STATUS = "b"
                self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.fill_fields()
        self.SORT_STATUS = "n"
        self.label_sort_2.setText(self.SORTED_ITEMS[self.SORT_STATUS])

    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)

            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                ###
                self.setComboBoxEditable(["self.comboBox_sito"], 1)
                self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
                self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
                self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "True")
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "True")
                self.setComboBoxEnable(["self.comboBox_nr_struttura"], "True")
                self.setComboBoxEnable(["self.comboBox_nr_individuo"], "True")

                self.setComboBoxEnable(["self.textEdit_descrizione_taf"], "False")
                self.setComboBoxEnable(["self.textEdit_interpretazione_taf"], "False")
                self.setComboBoxEnable(["self.textEdit_descrizione_corredo"], "False")
                self.setTableEnable(["self.tableWidget_caratteristiche", "self.tableWidget_corredo_tipo",
                                     "self.tableWidget_misurazioni"], "False")

                ###
                self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort_2.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()

    def on_pushButton_showLayer_pressed(self):
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_vector_layers(sing_layer)

    def on_pushButton_crea_codice_periodo_pressed(self):
        sito = str(self.comboBox_sito.currentText())
        self.DB_MANAGER.update_cont_per(sito)
        self.empty_fields()
        self.charge_records()
        self.fill_fields(self.REC_CORR)  # ricaricare tutti i record in uso e passare il valore REC_CORR a fill_fields

        QMessageBox.warning(self, "Attenzione", "Codice periodo aggiornato per lo scavo %s" % (sito), QMessageBox.Ok)

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                QMessageBox.Ok)
        else:
            ## nr scheda
            if self.lineEdit_nr_scheda.text() != "":
                nr_scheda = int(self.lineEdit_nr_scheda.text())
            else:
                nr_scheda = ""

            ## nr struttura
            if self.comboBox_nr_struttura.currentText() != "":
                nr_struttura = int(self.comboBox_nr_struttura.currentText())
            else:
                nr_struttura = ""

            ## nr individuo
            if self.comboBox_nr_individuo.currentText() != "":
                nr_individuo = int(self.comboBox_nr_individuo.currentText())
            else:
                nr_individuo = ""

            ##orientamento azimut
            if self.lineEdit_orientamento_azimut.text() != "":
                orientamento_azimut = float(self.lineEdit_orientamento_azimut.text())
            else:
                orientamento_azimut = None

            ##lunghezza scheletro
            if self.lineEdit_lunghezza_scheletro.text() != "":
                lunghezza_scheletro = float(self.lineEdit_lunghezza_scheletro.text())
            else:
                lunghezza_scheletro = None

            if self.comboBox_per_iniz.currentText() != "":
                periodo_iniziale = int(self.comboBox_per_iniz.currentText())
            else:
                periodo_iniziale = ""

            if self.comboBox_fas_iniz.currentText() != "":
                fase_iniziale = int(self.comboBox_fas_iniz.currentText())
            else:
                fase_iniziale = ""

            if self.comboBox_per_fin.currentText() != "":
                periodo_finale = int(self.comboBox_per_fin.currentText())
            else:
                periodo_finale = ""

            if self.comboBox_fas_fin.currentText() != "":
                fase_finale = int(self.comboBox_fas_fin.currentText())
            else:
                fase_finale = ""

            search_dict = {
                self.TABLE_FIELDS[0]: "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]: nr_scheda,  # 2 - Nr schede
                self.TABLE_FIELDS[2]: "'" + str(self.comboBox_sigla_struttura.currentText()) + "'",
            # 3 - Tipo struttura
                self.TABLE_FIELDS[3]: nr_struttura,  # 4 - Nr struttura
                self.TABLE_FIELDS[4]: nr_individuo,  # 5 - Nr struttura
                self.TABLE_FIELDS[5]: "'" + str(self.comboBox_rito.currentText()) + "'",  # 6 - Rito
                self.TABLE_FIELDS[6]: "'" + str(self.textEdit_descrizione_taf.toPlainText()) + "'",
                # 7 - Descrizione tafonimia
                self.TABLE_FIELDS[7]: "'" + str(self.textEdit_interpretazione_taf.toPlainText()) + "'",
                # 8 - Interpretazione tafonimia
                self.TABLE_FIELDS[8]: "'" + str(self.comboBox_segnacoli.currentText()) + "'",  # 9 - Segnacoli
                self.TABLE_FIELDS[9]: "'" + str(self.comboBox_canale_libatorio.currentText()) + "'",
            # 10 - Canale libatorio
                self.TABLE_FIELDS[10]: "'" + str(self.comboBox_oggetti_esterno.currentText()) + "'",
            # 11 - Oggetti esterno
                self.TABLE_FIELDS[11]: "'" + str(self.comboBox_conservazione_taf.currentText()) + "'",
                # 12 - Conservazione tafonomia
                self.TABLE_FIELDS[12]: "'" + str(self.comboBox_copertura_tipo.currentText()) + "'",
            # 13 - Copertura tipo
                self.TABLE_FIELDS[13]: "'" + str(self.comboBox_tipo_contenitore_resti.currentText()) + "'",
                # 14 - Tipo contenitore resti
                self.TABLE_FIELDS[14]: "'" + str(self.lineEdit_orientamento_asse.text()) + "'",
            # 15 - orientamento asse
                self.TABLE_FIELDS[15]: orientamento_azimut,  # 16 - orientamento azimut
                self.TABLE_FIELDS[17]: "'" + str(self.comboBox_corredo_presenza.currentText()) + "'",  # 17 - corredo
                self.TABLE_FIELDS[20]: lunghezza_scheletro,  # 18 - lunghezza scheletro
                self.TABLE_FIELDS[21]: "'" + str(self.comboBox_posizione_scheletro.currentText()) + "'",
                # 19 - posizione scheletro
                self.TABLE_FIELDS[22]: "'" + str(self.comboBox_posizione_cranio.currentText()) + "'",
            # 20 - posizione cranio
                self.TABLE_FIELDS[23]: "'" + str(self.comboBox_arti_superiori.currentText()) + "'",
            # 21 - arti superiori
                self.TABLE_FIELDS[24]: "'" + str(self.comboBox_arti_inferiori.currentText()) + "'",
            # 24 - arti inferiori
                self.TABLE_FIELDS[25]: "'" + str(self.comboBox_completo.currentText()) + "'",  # 25 - completo
                self.TABLE_FIELDS[26]: "'" + str(self.comboBox_disturbato.currentText()) + "'",  # 26 - disturbato
                self.TABLE_FIELDS[27]: "'" + str(self.comboBox_in_connessione.currentText()) + "'",
            # 27 - in connessione
                self.TABLE_FIELDS[29]: periodo_iniziale,  # 29 - periodo iniziale
                self.TABLE_FIELDS[30]: fase_iniziale,  # 10 - fase iniziale
                self.TABLE_FIELDS[31]: periodo_finale,  # 11 - periodo finale
                self.TABLE_FIELDS[32]: fase_finale,  # 12 - fase finale
                self.TABLE_FIELDS[33]: str(self.lineEdit_datazione_estesa.text())  # 10 - datazione_estesa
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                QMessageBox.warning(self, "ATTENZIONE", "Non e' stata impostata alcuna ricerca!!!", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
                    self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "False")
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_struttura"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_individuo"], "False")
                    self.setComboBoxEnable(["self.textEdit_descrizione_taf"], "True")
                    self.setComboBoxEnable(["self.textEdit_interpretazione_taf"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_corredo"], "True")
                    self.setTableEnable(["self.tableWidget_caratteristiche", "self.tableWidget_corredo_tipo",
                                         "self.tableWidget_misurazioni"], "True")
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)

                    if self.REC_TOT == 1:
                        strings = ("E' stato trovato", self.REC_TOT, "record")
                        if self.toolButtonGis.isChecked():
                            self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")
                        if self.toolButtonGis.isChecked():
                            self.pyQGIS.charge_vector_layers(self.DATA_LIST)

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_struttura"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_struttura"], 1)
                    self.setComboBoxEditable(["self.comboBox_nr_individuo"], 1)
                    self.setComboBoxEnable(["self.lineEdit_nr_scheda"], "False")
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_struttura"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_struttura"], "False")
                    self.setComboBoxEnable(["self.comboBox_nr_individuo"], "False")
                    self.setComboBoxEnable(["self.textEdit_descrizione_taf"], "True")
                    self.setComboBoxEnable(["self.textEdit_interpretazione_taf"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_corredo"], "True")
                    self.setTableEnable(["self.tableWidget_caratteristiche", "self.tableWidget_corredo_tipo",
                                         "self.tableWidget_misurazioni"], "True")

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
        self.enable_button_search(1)

    def on_pushButton_pdf_exp_pressed(self):
        Tafonomia_pdf_sheet = generate_tafonomia_pdf()
        data_list = self.generate_list_pdf()
        Tafonomia_pdf_sheet.build_Tafonomia_sheets(data_list)

    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            sito = str(self.DATA_LIST[i].sito)
            nr_individuo = str(self.DATA_LIST[i].nr_individuo)
            nr_individuo_find = int(self.DATA_LIST[i].nr_individuo)
            sigla_struttura = ('%s%s') % (str(self.DATA_LIST[i].sigla_struttura), str(self.DATA_LIST[i].nr_struttura))

            res_ind = self.DB_MANAGER.query_bool({"sito": "'" + sito + "'", "nr_individuo": nr_individuo_find},
                                                 "SCHEDAIND")

            us_ind_list = []
            if bool(res_ind):
                for ri in res_ind:
                    us_ind_list.append([str(ri.sito), str(ri.area), str(ri.us)])
                us_ind_list.sort()

                # self.testing('C:\Users\Luca\pyarchinit_Test_folder\lista_strutture.txt', str(res_ind))

            quote_ind = []
            if bool(us_ind_list):
                res_quote_ind = self.DB_MANAGER.select_quote_from_db_sql(us_ind_list[0][0], us_ind_list[0][1],
                                                                         us_ind_list[0][2])

                for sing_us in res_quote_ind:
                    sing_quota_value = str(sing_us[5])
                    if sing_quota_value[0] == '-':
                        sing_quota_value = sing_quota_value[:7]
                    else:
                        sing_quota_value = sing_quota_value[:6]

                    sing_quota = [sing_quota_value, sing_us[4]]
                    quote_ind.append(sing_quota)
                quote_ind.sort()

            if bool(quote_ind):
                quota_min_ind = '%s %s' % (quote_ind[0][0], quote_ind[0][1])
                quota_max_ind = '%s %s' % (quote_ind[-1][0], quote_ind[-1][1])
            else:
                quota_min_ind = "Non inserita su GIS"
                quota_max_ind = "Non inserita su GIS"

            ##########################################################################

            res_strutt = self.DB_MANAGER.query_bool(
                {"sito": "'" + str(sito) + "'", "struttura": "'" + str(sigla_struttura) + "'"}, "US")
            # res = db.query_distinct('INVENTARIO_MATERIALI',[['sito','"Sito archeologico"']], ['area', 'us'])
            us_strutt_list = []
            if bool(res_strutt):
                for rs in res_strutt:
                    us_strutt_list.append([str(rs.sito), str(rs.area), str(rs.us)])
                us_strutt_list.sort()

            quote_strutt = []
            if bool(us_strutt_list):
                for sing_us in us_strutt_list:
                    res_quote_strutt = self.DB_MANAGER.select_quote_from_db_sql(sing_us[0], sing_us[1], sing_us[2])
                    if bool(res_quote_strutt):
                        for sing_us in res_quote_strutt:
                            sing_quota_value = str(sing_us[5])
                            if sing_quota_value[0] == '-':
                                sing_quota_value = sing_quota_value[:7]
                            else:
                                sing_quota_value = sing_quota_value[:6]

                            sing_quota = [sing_quota_value, sing_us[4]]
                            quote_strutt.append(sing_quota)
                        quote_strutt.sort()

            if bool(quote_strutt):
                quota_min_strutt = '%s %s' % (quote_strutt[0][0], quote_strutt[0][1])
                quota_max_strutt = '%s %s' % (quote_strutt[-1][0], quote_strutt[-1][1])
            else:
                quota_min_strutt = "Non inserita su GIS"
                quota_max_strutt = "Non inserita su GIS"

            data_list.append([
                str(self.DATA_LIST[i].sito),  # 0 - Sito
                str(self.DATA_LIST[i].nr_scheda_taf),  # 1 - numero scheda taf
                str(self.DATA_LIST[i].sigla_struttura),  # 2 - sigla struttura
                str(self.DATA_LIST[i].nr_struttura),  # 3 - nr struttura
                str(self.DATA_LIST[i].nr_individuo),  # 4 - nr individuo
                str(self.DATA_LIST[i].rito),  # 5 - rito
                str(self.DATA_LIST[i].descrizione_taf),  # 6 - descrizione
                str(self.DATA_LIST[i].interpretazione_taf),  # 7 - interpretazione
                str(self.DATA_LIST[i].segnacoli),  # 8 - segnacoli
                str(self.DATA_LIST[i].canale_libatorio_si_no),  # 9- canale libatorio l
                str(self.DATA_LIST[i].oggetti_rinvenuti_esterno),  # 10- oggetti rinvenuti esterno
                str(self.DATA_LIST[i].stato_di_conservazione),  # 11 - stato_di_conservazione
                str(self.DATA_LIST[i].copertura_tipo),  # 12 - copertura tipo
                str(self.DATA_LIST[i].tipo_contenitore_resti),  # 13 - tipo contenitore resti
                str(self.DATA_LIST[i].orientamento_asse),  # 14 - orientamento asse
                self.DATA_LIST[i].orientamento_azimut,  # 15 orientamento azimut
                str(self.DATA_LIST[i].corredo_presenza),  # 16-  corredo presenza
                str(self.DATA_LIST[i].corredo_tipo),  # 17 - corredo tipo
                str(self.DATA_LIST[i].corredo_descrizione),  # 18 - corredo descrizione
                self.DATA_LIST[i].lunghezza_scheletro,  # 19 - lunghezza scheletro
                str(self.DATA_LIST[i].posizione_cranio),  # 20 - posizione cranio
                str(self.DATA_LIST[i].posizione_scheletro),  # 21 - posizione cranio
                str(self.DATA_LIST[i].posizione_arti_superiori),  # 22 - posizione arti superiori
                str(self.DATA_LIST[i].posizione_arti_inferiori),  # 23 - posizione arti inferiori
                str(self.DATA_LIST[i].completo_si_no),  # 24 - completo
                str(self.DATA_LIST[i].disturbato_si_no),  # 25- disturbato
                str(self.DATA_LIST[i].in_connessione_si_no),  # 26 - in connessione
                str(self.DATA_LIST[i].caratteristiche),  # 27 - caratteristiche
                str(self.DATA_LIST[i].periodo_iniziale),  # 28 - periodo iniziale
                str(self.DATA_LIST[i].fase_iniziale),  # 29 - fase iniziale
                str(self.DATA_LIST[i].periodo_finale),  # 30 - periodo finale
                str(self.DATA_LIST[i].fase_finale),  # 31 - fase finale
                str(self.DATA_LIST[i].datazione_estesa),  # 32 - datazione estesa
                str(self.DATA_LIST[i].misure_tafonomia),  # 33 - misure tafonomia
                quota_min_ind,  # 34 - quota min individuo
                quota_max_ind,  # 35 - quota max individuo
                quota_min_strutt,  # 36 - quota min struttura
                quota_max_strutt,  # 37 - quota max struttura
                us_ind_list,  # 38 - us individuo
                us_strutt_list  # 39 - us struttura
            ])

        return data_list

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        self.msg = msg
        if self.msg == 1:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i." + self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS,
                                                                self.ID_TABLE)  # self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status_2.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                if type(self.REC_CORR) == "<type 'str'>":
                    corr = 0
                else:
                    corr = self.REC_CORR
                return 1
            elif test == 0:
                return 0

    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            QMessageBox.warning(self, "Messaggio",
                                "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Se chiudete ora la scheda senza correggere gli errori perderete i dati. Fare una copia di tutto su un foglio word a parte. Errore :" + str(
                                    e), QMessageBox.Ok)
            return 0

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

        # custom functions

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
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if value != None:
                    sub_list.append(str(value.text()))

            if bool(sub_list):
                lista.append(sub_list)
        return lista

    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()

        # column table count
        table_col_count_cmd = ("%s.columnCount()") % (self.table_name)
        table_col_count = eval(table_col_count_cmd)

        # clear table
        table_clear_cmd = ("%s.clearContents()") % (self.table_name)
        eval(table_clear_cmd)

        for i in range(table_col_count):
            table_rem_row_cmd = ("%s.removeRow(%d)") % (self.table_name, i)
            eval(table_rem_row_cmd)

        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                item = QTableWidgetItem(self.data_list[row][col])
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name, row, col)
                eval(exec_str)

    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
        eval(cmd)

    def empty_fields(self):
        caratteristiche_row_count = self.tableWidget_caratteristiche.rowCount()
        corredo_tipo_row_count = self.tableWidget_corredo_tipo.rowCount()
        misurazioni_row_count = self.tableWidget_misurazioni.rowCount()

        for i in range(caratteristiche_row_count):
            self.tableWidget_caratteristiche.removeRow(0)
        self.insert_new_row("self.tableWidget_caratteristiche")  # 17 - caratteristiche

        for i in range(corredo_tipo_row_count):
            self.tableWidget_corredo_tipo.removeRow(0)
        self.insert_new_row("self.tableWidget_corredo_tipo")  # 18 - corredo tipo

        for i in range(misurazioni_row_count):
            self.tableWidget_misurazioni.removeRow(0)
        self.insert_new_row("self.tableWidget_misurazioni")  # 19 - misurazioni

        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.lineEdit_nr_scheda.clear()  # 2 - nr scheda tafonomica
        self.comboBox_sigla_struttura.setEditText("")  # 3 - tipo struttura
        self.comboBox_nr_struttura.setEditText("")  # 4 - nr struttura
        self.comboBox_nr_individuo.setEditText("")  # 4 - nr struttura
        self.comboBox_rito.setEditText("")  # 5 - rito
        self.textEdit_descrizione_taf.clear()  # 6 - descrizione
        self.textEdit_interpretazione_taf.clear()  # 7 - interpretazione
        self.comboBox_segnacoli.setEditText("")  # 8 - segnacoli
        self.comboBox_canale_libatorio.setEditText("")  # 9 - canale libatorio
        self.comboBox_oggetti_esterno.setEditText("")  # 10 - oggetti esterno
        self.comboBox_conservazione_taf.setEditText("")  # 11 - conservazione
        self.comboBox_copertura_tipo.setEditText("")  # 12 - copertura
        self.comboBox_tipo_contenitore_resti.setEditText("")  # 13 - tipo contenitore resti
        self.lineEdit_orientamento_asse.clear()  # 14 - orientamento asse
        self.lineEdit_orientamento_azimut.clear()  # 14 - orientamento azimut
        self.comboBox_corredo_presenza.setEditText("")  # 19 - corredo presenza
        self.textEdit_descrizione_corredo.clear()  # 20 - descrizione corredo
        self.lineEdit_lunghezza_scheletro.clear()  # 21 - lunghezza scheletro
        self.comboBox_posizione_scheletro.setEditText("")  # 22 - posizione scheletro
        self.comboBox_posizione_cranio.setEditText("")  # 23 - posizione cranio
        self.comboBox_arti_superiori.setEditText("")  # 24 - arti inferiori
        self.comboBox_arti_inferiori.setEditText("")  # 25 - arti superiori
        self.comboBox_completo.setEditText("")  # 26 - completo
        self.comboBox_disturbato.setEditText("")  # 27 - disturbato
        self.comboBox_in_connessione.setEditText("")  # 28 - in connessione
        self.comboBox_per_iniz.setEditText("")  # 9 - periodo iniziale
        self.comboBox_fas_iniz.setEditText("")  # 10 - fase iniziale
        self.comboBox_per_fin.setEditText("")  # 11 - periodo finale iniziale
        self.comboBox_fas_fin.setEditText("")  # 12 - fase finale
        self.lineEdit_datazione_estesa.clear()  # 13 - datazione estesa

    def fill_fields(self, n=0):
        self.rec_num = n
        if bool(self.DATA_LIST):
            try:

                self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito
                self.lineEdit_nr_scheda.setText(str(self.DATA_LIST[self.rec_num].nr_scheda_taf))  # 2 - nr_scheda_taf
                self.comboBox_sigla_struttura.setEditText(
                    self.DATA_LIST[self.rec_num].sigla_struttura)  # 3 - sigla_struttura
                self.comboBox_nr_struttura.setEditText(
                    str(self.DATA_LIST[self.rec_num].nr_struttura))  # 4 - nr_struttura
                self.comboBox_nr_individuo.setEditText(
                    str(self.DATA_LIST[self.rec_num].nr_individuo))  # 5 - nr_individuo
                self.comboBox_rito.setEditText(str(self.DATA_LIST[self.rec_num].rito))  # 6 - rito
                str(self.textEdit_descrizione_taf.setText(
                    self.DATA_LIST[self.rec_num].descrizione_taf))  # 7 - descrizione_taf
                str(self.textEdit_interpretazione_taf.setText(
                    self.DATA_LIST[self.rec_num].interpretazione_taf))  # 8 - interpretazione_taf
                self.comboBox_segnacoli.setEditText(self.DATA_LIST[self.rec_num].segnacoli)  # 9 - segnacoli
                self.comboBox_canale_libatorio.setEditText(
                    self.DATA_LIST[self.rec_num].canale_libatorio_si_no)  # 10 - canale_libatorio_si_no
                self.comboBox_oggetti_esterno.setEditText(
                    self.DATA_LIST[self.rec_num].oggetti_rinvenuti_esterno)  # 11 -  oggetti_rinvenuti_esterno
                self.comboBox_conservazione_taf.setEditText(
                    self.DATA_LIST[self.rec_num].stato_di_conservazione)  # 12 - stato_di_conservazione
                self.comboBox_copertura_tipo.setEditText(
                    self.DATA_LIST[self.rec_num].copertura_tipo)  # 13 - copertura_tipo
                self.comboBox_tipo_contenitore_resti.setEditText(self.DATA_LIST[
                                                                     self.rec_num].tipo_contenitore_resti)  # 14 - tipo contenitore resti tipo_contenitore_resti
                self.lineEdit_orientamento_asse.setText(
                    self.DATA_LIST[self.rec_num].orientamento_asse)  # 15 - orientamento asse
                self.comboBox_corredo_presenza.setEditText(
                    str(self.DATA_LIST[self.rec_num].corredo_presenza))  # 16 - corredo presenza
                str(self.textEdit_descrizione_corredo.setText(
                    self.DATA_LIST[self.rec_num].corredo_descrizione))  # 17 - descrizione corredo
                self.comboBox_posizione_scheletro.setEditText(
                    self.DATA_LIST[self.rec_num].posizione_scheletro)  # 18 - posizione scheletro
                self.comboBox_posizione_cranio.setEditText(
                    self.DATA_LIST[self.rec_num].posizione_cranio)  # 19 - posizione cranio
                self.comboBox_arti_superiori.setEditText(
                    self.DATA_LIST[self.rec_num].posizione_arti_superiori)  # 20 - arti superiori
                self.comboBox_arti_inferiori.setEditText(
                    self.DATA_LIST[self.rec_num].posizione_arti_inferiori)  # 21 - arti inferiori
                self.comboBox_completo.setEditText(self.DATA_LIST[self.rec_num].completo_si_no)  # 22 - completo
                self.comboBox_disturbato.setEditText(self.DATA_LIST[self.rec_num].disturbato_si_no)  # 23 - disturbato
                self.comboBox_in_connessione.setEditText(
                    self.DATA_LIST[self.rec_num].in_connessione_si_no)  # 24 - in connessione
                self.lineEdit_datazione_estesa.setText(
                    str(self.DATA_LIST[self.rec_num].datazione_estesa))  # 12 - datazione estesa
                self.tableInsertData("self.tableWidget_caratteristiche",
                                     self.DATA_LIST[self.rec_num].caratteristiche)  # 26 - caratteristiche
                self.tableInsertData("self.tableWidget_corredo_tipo",
                                     self.DATA_LIST[self.rec_num].corredo_tipo)  # 27 - corredo tipo
                self.tableInsertData("self.tableWidget_misurazioni",
                                     self.DATA_LIST[self.rec_num].misure_tafonomia)  # 28 - misure struttura

                if self.DATA_LIST[self.rec_num].periodo_iniziale == None:
                    self.comboBox_per_iniz.setEditText("")
                else:
                    self.comboBox_per_iniz.setEditText(str(self.DATA_LIST[self.rec_num].periodo_iniziale))

                if self.DATA_LIST[self.rec_num].fase_iniziale == None:
                    self.comboBox_fas_iniz.setEditText("")
                else:
                    self.comboBox_fas_iniz.setEditText(str(self.DATA_LIST[self.rec_num].fase_iniziale))

                if self.DATA_LIST[self.rec_num].periodo_finale == None:
                    self.comboBox_per_fin.setEditText("")
                else:
                    self.comboBox_per_fin.setEditText(str(self.DATA_LIST[self.rec_num].periodo_finale))

                if self.DATA_LIST[self.rec_num].fase_finale == None:
                    self.comboBox_fas_fin.setEditText("")
                else:
                    self.comboBox_fas_fin.setEditText(str(self.DATA_LIST[self.rec_num].fase_finale))

                if self.DATA_LIST[self.rec_num].orientamento_azimut == None:
                    self.lineEdit_orientamento_azimut.setText("")
                else:
                    self.lineEdit_orientamento_azimut.setText(
                        str(self.DATA_LIST[self.rec_num].orientamento_azimut))  # 14 - orientamento azimut

                if self.DATA_LIST[self.rec_num].lunghezza_scheletro == None:
                    self.lineEdit_lunghezza_scheletro.setText("")
                else:
                    self.lineEdit_lunghezza_scheletro.setText(
                        str(self.DATA_LIST[self.rec_num].lunghezza_scheletro))  # 14 - orientamento azimut

                    # gestione tool
                if self.toolButtonPreview.isChecked():
                    self.loadMapPreview()
                if self.toolButtonPreviewMedia.isChecked():
                    self.loadMediaPreview()
            except Exception as e:
                QMessageBox.warning(self, "Errore fill", str(e), QMessageBox.Ok)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot_2.setText(str(self.rec_tot))
        self.label_rec_corrente_2.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        ## nr scheda
        if self.lineEdit_nr_scheda.text() == "":
            nr_scheda = None
        else:
            nr_scheda = self.lineEdit_nr_scheda.text()

        ## nr struttura
        if self.comboBox_nr_struttura.currentText() == "":
            nr_struttura = None
        else:
            nr_struttura = self.comboBox_nr_struttura.currentText()

        ## nr individuo
        if self.comboBox_nr_individuo.currentText() == "":
            nr_individuo = None
        else:
            nr_individuo = self.comboBox_nr_individuo.currentText()

        ##orientamento azimut
        if self.lineEdit_orientamento_azimut.text() == "":
            orientamento_azimut = None
        else:
            orientamento_azimut = self.lineEdit_orientamento_azimut.text()

        ##lunghezza scheletro
        if self.lineEdit_lunghezza_scheletro.text() == "":
            lunghezza_scheletro = None
        else:
            lunghezza_scheletro = self.lineEdit_lunghezza_scheletro.text()

        if self.comboBox_per_iniz.currentText() == "":
            periodo_iniziale = None
        else:
            periodo_iniziale = self.comboBox_per_iniz.currentText()

        if self.comboBox_fas_iniz.currentText() == "":
            fase_iniziale = None
        else:
            fase_iniziale = self.comboBox_fas_iniz.currentText()

        if self.comboBox_per_fin.currentText() == "":
            periodo_finale = None
        else:
            periodo_finale = self.comboBox_per_fin.currentText()

        if self.comboBox_fas_fin.currentText() == "":
            fase_finale = None
        else:
            fase_finale = self.comboBox_fas_fin.currentText()

            # TableWidget

        ##Caratteristiche
        caratteristiche = self.table2dict("self.tableWidget_caratteristiche")
        ##Corredo tipo
        corredo_tipo = self.table2dict("self.tableWidget_corredo_tipo")
        ##Misurazioni
        misurazioni = self.table2dict("self.tableWidget_misurazioni")

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(nr_scheda),  # 2 - Nr schede
            str(self.comboBox_sigla_struttura.currentText()),  # 3 - Tipo struttura
            str(nr_struttura),  # 4 - Nr struttura
            str(nr_individuo),  # 5 - Nr individuo
            str(self.comboBox_rito.currentText()),  # 6 - Rito
            str(self.textEdit_descrizione_taf.toPlainText()),  # 7 - Descrizione tafonimia
            str(self.textEdit_interpretazione_taf.toPlainText()),  # 8 - Interpretazione tafonimia
            str(self.comboBox_segnacoli.currentText()),  # 9 - Segnacoli
            str(self.comboBox_canale_libatorio.currentText()),  # 10 - Canale libatorio
            str(self.comboBox_oggetti_esterno.currentText()),  # 11 - Oggetti esterno
            str(self.comboBox_conservazione_taf.currentText()),  # 12 - Conservazione tafonomia
            str(self.comboBox_copertura_tipo.currentText()),  # 13 - Copertura tipo
            str(self.comboBox_tipo_contenitore_resti.currentText()),  # 14 - Tipo contenitore resti
            str(self.lineEdit_orientamento_asse.text()),  # 15 - orientamento asse
            str(orientamento_azimut),  # 16 - orientamento azimut
            str(self.comboBox_corredo_presenza.currentText()),  # 17 - corredo
            str(corredo_tipo),  # 18 - corredo tipo
            str(self.textEdit_descrizione_corredo.toPlainText()),  # 19 - descrizione corredo
            str(lunghezza_scheletro),  # 20 - lunghezza scheletro
            str(self.comboBox_posizione_scheletro.currentText()),  # 21 - posizione scheletro
            str(self.comboBox_posizione_cranio.currentText()),  # 22 - posizione cranio
            str(self.comboBox_arti_superiori.currentText()),  # 23 - arti superiori
            str(self.comboBox_arti_inferiori.currentText()),  # 24 - arti inferiori
            str(self.comboBox_completo.currentText()),  # 25 - completo
            str(self.comboBox_disturbato.currentText()),  # 26 - disturbato
            str(self.comboBox_in_connessione.currentText()),  # 27 - in connessione
            str(caratteristiche),  # 28 - caratteristiche
            str(periodo_iniziale),  # 6 - descrizioene
            str(fase_iniziale),  # 6 - descrizioene
            str(periodo_finale),  # 6 - descrizioene
            str(fase_finale),  # 6 - descrizioene
            str(self.lineEdit_datazione_estesa.text()),  # 7- cron estesa
            str(misurazioni)
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n

        for fn in field_names:
            cmd = ('%s%s%d%s') % (fn, '.setEditable(', n, ')')
            eval(cmd)

    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = ('%s%s%s%s') % (fn, '.setEnabled(', v, ')')
            eval(cmd)

    def setTableEnable(self, t, v):
        tab_names = t
        value = v

        for tn in tab_names:
            cmd = ('%s%s%s%s') % (tn, '.setEnabled(', v, ')')
            eval(cmd)

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()

## Class end
