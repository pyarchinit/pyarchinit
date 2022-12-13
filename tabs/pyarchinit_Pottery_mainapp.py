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
 *   (at your option) any later version.                                    *
 ***************************************************************************/
"""
from __future__ import absolute_import

import os
from datetime import date
import sys
import re
import platform
from pdf2docx import parse
from builtins import range

from datetime import date
from qgis.core import *
from qgis.PyQt import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *

from qgis.PyQt.uic import loadUiType
from ..modules.utility.settings import Settings
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..gui.quantpanelmain import QuantPanelMain
from ..modules.utility.pyarchinit_exp_POTTERYsheet_pdf import generate_POTTERY_pdf



from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management

from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.db.pyarchinit_utility import Utility
from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config

from numpy import *

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'pyarchinit_Pottery_ui.ui'))

class pyarchinit_Pottery(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale")[0:2]
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Ceramica"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Pottery form"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Pottery formular"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config

    if L == 'it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}

    if L == 'de':
        STATUS_ITEMS = {"b": "Aktuell ", "f": "Finden", "n": "Neuer Rekord"}

    else:
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L == 'it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    if L == 'de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    SORT_ITEMS_CONVERTED = ''
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'pottery_table'
    MAPPER_TABLE_CLASS = "POTTERY"
    HOME = os.environ['PYARCHINIT_HOME']
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    NOME_SCHEDA = "Scheda Pottery"
    ID_TABLE = "id_rep"
    ID_SITO = "sito"

    CONVERSION_DICT = {
    ID_TABLE:ID_TABLE,
    "ID Number":"id_number",
    "Sito":"sito",
    "Area":"area",
    "US":"us",
    "Box":"box",
    "Photo":"photo",
    "Drawing":"drawing",
    "Year":"anno",
    "Fabric":"fabric",
    "Percent":"percent",
    "Material":"material",
    "Shape":"form",
    "Specific form":"specific_form",
    "Ware":"ware",
    "Munsell color":"munsell",
    "Surface treatment":"surf_trat",
    "External decoration":"exdeco",
    "Internal decoration":"intdeco",
    "Wheel made":"wheel_made",
    "Description external decoration":"descrip_ex_deco",
    "Description internal decoration":"descrip_in_deco",
    "Note":"note",
    "Diameter Max":"diametro_max",
    "QTY":"qty",
    "Diameter Rim":"diametro_rim",
    "Diameter Bottom":"diametro_bottom",
    "Total height":"diametro_height",
    "Preserved height":"diametro_preserved",
    "Specific shape":"specific_shape",
    "Bag": "bag",
    "Sector": "sector"
    }

    SORT_ITEMS = [
                ID_TABLE,
                "ID Number",
                "Sito",
                "Area",
                "US",
                "Box",
                "Photo",
                "Drawing",
                "Year",
                "Fabric",
                "Percent",
                "Material",
                "Shape",
                "Specific form",
                "Ware",
                "Munsell color",
                "Surface treatment",
                "External decoration",
                "Internal decoration",
                "Wheel made",
                "Description external decoration",
                "Description internal decoration",
                "Note",
                "Diameter Max",
                "QTY",
                "Diameter Rim",
                "Diameter Bottom",
                "Total height",
                "Preserved height",
                "Specific shape",
                "Bag",
                "Sector"
                ]
    QUANT_ITEMS = [
                'Fabric',
                'US',
                'Area',
                'Material',
                'Percent',
                'Shape',
                'Specific form',
                'Ware',
                'Munsell color',
                'Surface treatment',
                'External decoration',
                'Internal decoration',
                'Wheel made',
                ]

    TABLE_FIELDS_UPDATE = [
                    "id_number",
                    "sito",
                    "area",
                    "us",
                    "box",
                    "photo",
                    "drawing",
                    "anno",
                    "fabric",
                    "percent",
                    "material",
                    "form",
                    "specific_form",
                    "ware",
                    "munsell",
                    "surf_trat",
                    "exdeco",
                    "intdeco",
                    "wheel_made",
                    "descrip_ex_deco",
                    "descrip_in_deco",
                    "note",
                    "diametro_max",
                    "qty",
                    "diametro_rim",
                    "diametro_bottom",
                    "diametro_height",
                    "diametro_preserved",
                    "specific_shape",
                    "bag",
                    "sector"
                    ]
    TABLE_FIELDS = [
                    "id_number",
                    "sito",
                    "area",
                    "us",
                    "box",
                    "photo",
                    "drawing",
                    "anno",
                    "fabric",
                    "percent",
                    "material",
                    "form",
                    "specific_form",
                    "ware",
                    "munsell",
                    "surf_trat",
                    "exdeco",
                    "intdeco",
                    "wheel_made",
                    "descrip_ex_deco",
                    "descrip_in_deco",
                    "note",
                    "diametro_max",
                    "qty",
                    "diametro_rim",
                    "diametro_bottom",
                    "diametro_height",
                    "diametro_preserved",
                    "specific_shape",
                    "bag",
                    "sector"
                    ]
    LANG = {
        "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN_US": ['en_US', 'EN_US', 'en', 'EN'],
        "DE": ['de_DE', 'de', 'DE', 'DE_DE']
    }


    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    DB_SERVER = "not defined"  ####nuovo sistema sort
    QUANT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Quantificazioni_folder")

    def __init__(self, iface):
        super().__init__()
        self.iface = iface

        self.setupUi(self)
        self.mDockWidget_4.setHidden(True)
        self.mDockWidget_export.setHidden(True)
        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Sistema di connessione", str(e),  QMessageBox.Ok)
        if len(self.DATA_LIST)==0:
            self.comboBox_sito.setCurrentIndex(0)
        else:
            self.comboBox_sito.setCurrentIndex(1)
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)

        self.fill_fields()
        self.msg_sito()
        self.set_sito()
        self.show()
        self.customize_GUI()
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        self.setnone()
    def setnone(self):
        if self.lineEdit_diametro_max.text=='None' or None or 'NULL'or 'Null':
            self.lineEdit_diametro_max.clear()
            self.lineEdit_diametro_max.setText('')
            self.lineEdit_diametro_max.update()
        if self.lineEdit_diametro_rim.text()=='None' or None or 'NULL'or 'Null':
            self.lineEdit_diametro_rim.clear()
            self.lineEdit_diametro_rim.setText('')
            self.lineEdit_diametro_rim.update()
        if self.lineEdit_diametro_bottom.text=='None' or None or 'NULL'or 'Null':
            self.lineEdit_diametro_bottom.clear()
            self.lineEdit_diametro_bottom.setText('')
            self.lineEdit_diametro_bottom.update()
        if self.lineEdit_diametro_preserved.text == 'None' or None or 'NULL'or 'Null':
            self.lineEdit_diametro_preserved.clear()
            self.lineEdit_diametro_preserved.setText('')
            self.lineEdit_diametro_preserved.update()
        if self.lineEdit_diametro_height.text == 'None' or None or 'NULL'or 'Null':
            self.lineEdit_diametro_height.clear()
            self.lineEdit_diametro_height.setText('')
            self.lineEdit_diametro_height.update()
    def generate_list_pdf2(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            data_list_foto.append([
                str(self.DATA_LIST[i].sito),  # 1 - Sito
                str(self.DATA_LIST[i].area),
                str(self.DATA_LIST[i].us),
                str(self.DATA_LIST[i].sector),
                str(self.DATA_LIST[i].anno),
                str(self.DATA_LIST[i].id_number),  # 2 -
                str(self.DATA_LIST[i].note),
                str(foto)])  # 6
        return data_list

    def generate_list_foto(self):
        data_list_foto = []
        for i in range(len(self.DATA_LIST)):
            conn = Connection()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']

            if thumb_path_str == '':
                if self.L == 'it':
                    QMessageBox.information(self, "Info",
                                            "devi settare prima la path per salvare le thumbnail . Vai in impostazioni di sistema/ path setting ")
                elif self.L == 'de':
                    QMessageBox.information(self, "Info",
                                            "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
                else:
                    QMessageBox.information(self, "Message",
                                            "you must first set the path to save the thumbnails and videos. Go to system/path setting")
            else:
                search_dict = {'id_entity': "'" + str(eval("self.DATA_LIST[i].id_rep")) + "'", 'entity_type': "'CERAMICA'"}
                record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
                for media in record_doc_list:
                    thumbnail = (thumb_path_str + media.filepath)
                    foto = (media.id_media)

                    data_list_foto.append([
                        str(self.DATA_LIST[i].sito),  # 1 - Sito
                        str(self.DATA_LIST[i].area),
                        str(self.DATA_LIST[i].us),
                        str(self.DATA_LIST[i].sector),
                        str(self.DATA_LIST[i].anno),
                        str(self.DATA_LIST[i].id_number),  # 2 -
                        str(self.DATA_LIST[i].note),
                        str(foto), # 5
                        str(thumbnail)])  # 6

        return data_list_foto

        # #####################fine########################

    # def generate_list_pdf(self):
    #     data_list = []
    #     for i in range(len(self.DATA_LIST)):
    #         data_list.append([
    #             str(self.DATA_LIST[i].divelog_id),
    #             str(self.DATA_LIST[i].artefact_id),
    #             str(self.DATA_LIST[i].site),
    #             str(self.DATA_LIST[i].area),
    #             str(self.DATA_LIST[i].inclusions),
    #             str(self.DATA_LIST[i].form),
    #             str(self.DATA_LIST[i].specific_part),
    #             str(self.DATA_LIST[i].category),
    #             str(self.DATA_LIST[i].typology),
    #             str(self.DATA_LIST[i].depth),
    #             str(self.DATA_LIST[i].retrieved),
    #             str(self.DATA_LIST[i].percent_inclusion),
    #             str(self.DATA_LIST[i].provenance),
    #             str(self.DATA_LIST[i].munsell_clay),
    #             str(self.DATA_LIST[i].munsell_surf),
    #             str(self.DATA_LIST[i].surf_treatment),
    #             str(self.DATA_LIST[i].conservation),
    #             str(self.DATA_LIST[i].storage_),
    #             str(self.DATA_LIST[i].period),
    #             str(self.DATA_LIST[i].state),
    #             str(self.DATA_LIST[i].samples),
    #             str(self.DATA_LIST[i].washed),
    #             str(self.DATA_LIST[i].dm),
    #             str(self.DATA_LIST[i].dr),
    #             str(self.DATA_LIST[i].db),
    #             str(self.DATA_LIST[i].th),
    #             str(self.DATA_LIST[i].ph),
    #             str(self.DATA_LIST[i].bh),
    #             str(self.DATA_LIST[i].thickmin),
    #             str(self.DATA_LIST[i].thickmax),
    #             str(self.DATA_LIST[i].date_),
    #             str(self.DATA_LIST[i].years),
    #             str(self.DATA_LIST[i].description),
    #             str(self.DATA_LIST[i].photographed),
    #             str(self.DATA_LIST[i].drawing),
    #             str(self.DATA_LIST[i].wheel_made)
    #         ])
    #     return data_list

    def on_pushButton_print_pressed(self):

        # if self.checkBox_s_pottery.isChecked():
        #     pottery_pdf_sheet = generate_POTTERY_pdf()
        #     data_list = self.generate_list_pdf()
        #     pottery_pdf_sheet.build_POTTERY_sheets(data_list)
        #     QMessageBox.warning(self, 'Ok', "Export completed", QMessageBox.Ok)
        # else:
        #     pass



        if self.checkBox_e_foto_t.isChecked():
            POTTERY_index_pdf = generate_POTTERY_pdf()
            data_list_foto = self.generate_list_foto()

            try:
                if bool(data_list_foto):
                    POTTERY_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok', "Export completed", QMessageBox.Ok)

                else:
                    QMessageBox.warning(self, 'Warning',
                                        "Pottery list photo can't to be exported, you must tag before the pics",
                                        QMessageBox.Ok)
            except Exception as e:
                QMessageBox.warning(self, 'Warning', str(e), QMessageBox.Ok)

        if self.checkBox_e_foto.isChecked():
            POTTERY_index_pdf = generate_POTTERY_pdf()
            data_list_foto = self.generate_list_foto()

            try:
                if bool(data_list_foto):
                    POTTERY_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                    QMessageBox.warning(self, 'Ok', "Export completed", QMessageBox.Ok)

                else:
                    QMessageBox.warning(self, 'Warniong',
                                        "Pottery list photo can't to be exported because the image are not tagged",
                                        QMessageBox.Ok)
            except Exception as e:
                QMessageBox.warning(self, 'Warning', str(e), QMessageBox.Ok)

    def setPathpdf(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.PDFFOLDER,
            " PDF (*.pdf)"
        )[0]
        # filename=dbpath.split("/")[-1]
        if dbpath:
            self.lineEdit_pdf_path.setText(dbpath)
            s.setValue('', dbpath)

    def openpdfDir(self):

        path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_PDF_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def on_pushButton_convert_pressed(self):
        # if not bool(self.setPathpdf()):
        # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
        # QMessageBox.Ok)
        try:
            pdf_file = self.lineEdit_pdf_path.text()
            filename = pdf_file.split("/")[-1]
            docx_file = self.PDFFOLDER + '/' + filename + '.docx'
            # convert pdf to docx
            parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())

            QMessageBox.information(self, "INFO", "Conversion completed",
                                    QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e),
                                QMessageBox.Ok)

    def msg_sito(self):
        # self.model_a.database().close()
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:

            if self.L == 'it':
                QMessageBox.information(self, "OK", "Sei connesso al sito: %s" % str(sito_set_str), QMessageBox.Ok)

            elif self.L == 'de':
                QMessageBox.information(self, "OK",
                                        "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),
                                        QMessageBox.Ok)

            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),
                                        QMessageBox.Ok)

        elif sito_set_str == '':
            if self.L == 'it':
                msg = QMessageBox.information(self, "Attenzione",
                                              "Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",
                                              QMessageBox.Ok | QMessageBox.Cancel)
            elif self.L == 'de':
                msg = QMessageBox.information(self, "Achtung",
                                              "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",
                                              QMessageBox.Ok | QMessageBox.Cancel)
            else:
                msg = QMessageBox.information(self, "Warning",
                                              "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",
                                              QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                pass
            else:
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec_()
    def set_sito(self):
        # self.model_a.database().close()
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        try:
            if bool(sito_set_str):
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
                pass  #
        except Exception as e:
            if self.L == 'it':

                QMessageBox.information(self, "Attenzione", "Non esiste questo sito: "'"' + str(
                    sito_set_str) + '"'" in questa scheda, Per favore distattiva la 'scelta sito' dalla scheda di configurazione plugin per vedere tutti i record oppure crea la scheda",
                                        QMessageBox.Ok)
            elif self.L == 'de':

                QMessageBox.information(self, "Warnung", "Es gibt keine solche archäologische Stätte: "'""' + str(
                    sito_set_str) + '"'" in dieser Registerkarte, Bitte deaktivieren Sie die 'Site-Wahl' in der Plugin-Konfigurationsregisterkarte, um alle Datensätze zu sehen oder die Registerkarte zu erstellen",
                                        QMessageBox.Ok)
            else:

                QMessageBox.information(self, "Warning", "There is no such site: "'"' + str(
                    sito_set_str) + '"'" in this tab, Please disable the 'site choice' from the plugin configuration tab to see all records or create the tab",
                                        QMessageBox.Ok)

    def on_pushButtonQuant_pressed(self):
        dlg = QuantPanelMain(self)
        dlg.insertItems(self.QUANT_ITEMS)
        dlg.exec_()
        dataset = []
        parameter1 = dlg.TYPE_QUANT
        parameters2 = dlg.ITEMS
        contatore = 0
        if parameter1 == 'QTY':
            for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                try:
                    temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].box))
                    contatore += int(self.DATA_LIST[i].box) #conteggio totale
                    dataset.append(temp_dataset)
                except:
                    pass
            #QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
            if bool(dataset):
                dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)
                csv_dataset = []
                for sing_tup in dataset_sum:
                    sing_list = [sing_tup[0], str(sing_tup[1])]
                    csv_dataset.append(sing_list)
                filename = ('%s%squant_qty.txt') % (self.QUANT_PATH, os.sep)
                #QMessageBox.warning(self, "Esportazione", str(filename), MessageBox.Ok)
                f = open(filename, 'wb')
                Uw = UnicodeWriter(f)
                Uw.writerows(csv_dataset)
                f.close()
                self.plot_chart(dataset_sum, 'Frequency analisys', 'Qty')
            else:
                QMessageBox.warning(self, "Warning", "The datas not are present",  QMessageBox.Ok)
    def parameter_quant_creator(self, par_list, n_rec):
        self.parameter_list = par_list
        self.record_number = n_rec
        converted_parameters = []
        for par in self.parameter_list:
            converted_parameters.append(self.CONVERSION_DICT[par])
        parameter2 = ''
        for sing_par_conv in range(len(converted_parameters)):
            exec_str =  ('str(self.DATA_LIST[%d].%s)') % (self.record_number, converted_parameters[sing_par_conv])
            paramentro = str(self.parameter_list[sing_par_conv])
            exec_str = ' -' + paramentro[:4] + ": " + eval(exec_str)
            parameter2 += exec_str
        return parameter2
    def plot_chart(self, d, t, yl):
        self.data_list = d
        self.title = t
        self.ylabel = yl
        if type(self.data_list) == list:
            data_diz = {}
            for item in self.data_list:
                data_diz[item[0]] = item[1]
        x = list(range(len(data_diz)))
        n_bars = len(data_diz)
        values = list(data_diz.values())
        teams = list(data_diz.keys())
        ind = np.arange(n_bars)
        #randomNumbers = random.sample(range(0, 10), 10)
        self.widget.canvas.ax.clear()
        #QMessageBox.warning(self, "Alert", str(teams) ,  QMessageBox.Ok)
        bars = self.widget.canvas.ax.bar(x, height=values, width=0.5, align='center', alpha=0.4,picker=5)
        #guardare il metodo barh per barre orizzontali
        self.widget.canvas.ax.set_title(self.title)
        self.widget.canvas.ax.set_ylabel(self.ylabel)
        l = []
        for team in teams:
            l.append('""')
        #self.widget.canvas.ax.set_xticklabels(x , ""   ,size = 'x-small', rotation = 0)
        n = 0
        for bar in bars:
            val = int(bar.get_height())
            x_pos = bar.get_x() + 0.25
            label  = teams[n]+ ' - ' + str(val)
            y_pos = 0.1 #bar.get_height() - bar.get_height() + 1
            self.widget.canvas.ax.tick_params(axis='x', labelsize=8)
            #self.widget.canvas.ax.set_xticklabels(ind + x, ['fg'], position = (x_pos,y_pos), xsize = 'small', rotation = 90)
            self.widget.canvas.ax.text(x_pos, y_pos, label,zorder=0, ha='center', va='bottom',size = 'x-small', rotation = 90)
            n+=1
        #self.widget.canvas.ax.plot(randomNumbers)
        self.widget.canvas.draw()

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
            if self.DATA_LIST:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
                #self.setComboBoxEnable(["self.comboBox_area"], "False")
                #self.setComboBoxEnable(["self.lineEdit_us"], "False")
            else:
                if self.L == 'it':
                    QMessageBox.warning(self, "BENVENUTO",
                                        "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "WILLKOMMEN",
                                        "WILLKOMMEN in pyArchInit" + "SE-MSE formular" + ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "WELCOME",
                                        "Welcome in pyArchInit" + "Samples SU-WSU" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                #self.setComboBoxEnable(["self.comboBox_area"], "True")
                #self.setComboBoxEnable(["self.lineEdit_us"], "True")
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L == 'it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(
                        str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)

                elif self.L == 'de':
                    msg = "Verbindungsfehler {}. " \
                          " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))
            else:
                if self.L == 'it':
                    msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                elif self.L == 'de':
                    msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
    def customize_GUI(self):


        #media prevew system

        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(430, 570))

        self.iconListWidget.setUniformItemSizes(True)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.SelectionMode()
        self.iconListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)

        #overrideLocale = QSettings().value( "locale/overrideFlag", False, type=bool )
		#if overrideLocale:
			#localeFullName = QLocale.system().name()

    def loadMediaPreview(self):
        self.iconListWidget.clear()
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # if mode == 0:
        # """ if has geometry column load to map canvas """
        rec_list = self.ID_TABLE + " = " + str(
            eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
        search_dict = {
            'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
            'entity_type': "'CERAMICA'"}
        record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
        for i in record_us_list:
            search_dict = {'id_media': "'" + str(i.id_media) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            thumb_path = str(mediathumb_data[0].filepath)
            item = QListWidgetItem(str(i.media_name))
            item.setData(Qt.UserRole, str(i.media_name))
            icon = QIcon(thumb_path_str + thumb_path)
            item.setIcon(icon)
            self.iconListWidget.addItem(item)
        # elif mode == 1:
        # self.iconListWidget.clear()

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        for item in items:
            dlg = ImageViewer()
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'media_filename': "'" + str(id_orig_item) + "'", 'mediatype': "'" + 'video' + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            # try:
            res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            search_dict_2 = {'media_filename': "'" + str(id_orig_item) + "'", 'mediatype': "'" + 'image' + "'"}
            search_dict_2 = u.remove_empty_items_fr_dict(search_dict_2)
            # try:
            res_2 = self.DB_MANAGER.query_bool(search_dict_2, "MEDIA_THUMB")
            search_dict_3 = {'media_filename': "'" + str(id_orig_item) + "'"}
            search_dict_3 = u.remove_empty_items_fr_dict(search_dict_3)
            # try:
            res_3 = self.DB_MANAGER.query_bool(search_dict_3, "MEDIA_THUMB")
            # file_path = str(res[0].path_resize)
            # file_path_2 = str(res_2[0].path_resize)
            file_path_3 = str(res_3[0].path_resize)
            if bool(res):
                os.startfile(str(thumb_resize_str + file_path_3))
            elif bool(res_2):
                dlg.show_image(str(thumb_resize_str + file_path_3))
                dlg.exec_()

    def charge_list(self):
        #lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in site list: " + str(e), QMessageBox.Ok)

        self.comboBox_sito.clear()


        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)



        ########lista per l'inserimento delle sigle nel thesaurus##################################################################################

        ###################################d_stratigrafica
        #search_dict = {
        #'nome_tabella'  : "'"+'pottery_table'+"'",
        #'tipologia_sigla' : "'"+'Munsell color'+"'"
        #}

        #munsell = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')


        #munsell_vl = [ ]

        #for i in range(len(munsell)):
            #munsell_vl.append(munsell[i].sigla_estesa)
        #try:
            #munsell_vl ('')
        #except:
            #pass

        #self.comboBox_munsell.clear()
        #munsell_vl.sort()
        #self.comboBox_munsell.addItems(munsell_vl)

    # def on_toolButtonPreviewMedia_toggled(self):
    #     if self.toolButtonPreviewMedia.isChecked() == False:
    #         QMessageBox.warning(self, "Messaggio", "Modalita' Preview Media Reperti attivata. Le immagini dei Reperti saranno visualizzate nella sezione Media", QMessageBox.Ok)
    #         self.loadMediaPreview()
    #     else:
    #         self.loadMediaPreview(1)
    def on_toolButtonPreview_toggled(self):
        if self.L=='it':
            if self.toolButtonPreview.isChecked():
                QMessageBox.warning(self, "Messaggio",
                                    "Modalita' Preview US attivata. Le piante delle US saranno visualizzate nella sezione Piante",
                                    QMessageBox.Ok)
                self.loadMapPreview()
            else:
                self.loadMapPreview(1)
        elif self.L=='de':
            if self.toolButtonPreview.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Modalität' Preview der aktivierten SE. Die Plana der SE werden in der Auswahl der Plana visualisiert",
                                    QMessageBox.Ok)
                self.loadMapPreview()
            else:
                self.loadMapPreview(1)
        else:
            if self.toolButtonPreview.isChecked():
                QMessageBox.warning(self, "Message",
                                    "Preview SU mode enabled. US plants will be displayed in the Plants section",
                                    QMessageBox.Ok)
                self.loadMapPreview()
            else:
                self.loadMapPreview(1)

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()

            items,order_type = dlg.ITEMS, dlg.TYPE_ORDER

            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                #QMessageBox.warning(self, "Messaggio",i, QMessageBox.Ok)
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)]) #apportare la modifica nellle altre schede

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
            self.DATA_LIST = []

            temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS, self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = 'b'
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




    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name+".insertRow(0)"
        eval(cmd)


    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""

        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        try:
            rowIndex = (rowSelected[1].row())
            cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
            eval(cmd)
        except:
            QMessageBox.warning(self, "Messaggio", "Devi selezionare una riga",  QMessageBox.Ok)



    def on_pushButton_new_rec_pressed(self):
        conn = Connection()

        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields_nosite()

                #self.setComboBoxEditable(["self.lineEdit_id_number"], 1)
                #self.setComboBoxEditable(["self.comboBox_unita_tipo"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], False)
                self.setComboBoxEnable(["self.lineEdit_id_number"], True)
                #self.setComboBoxEnable(["self.lineEdit_us"], True)
                #self.setComboBoxEnable(["self.comboBox_unita_tipo"], True)
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])

            else:
                self.BROWSE_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.empty_fields()
                self.setComboBoxEditable(["self.comboBox_sito"], 1)
                #self.setComboBoxEditable(["self.lineEdit_id_number"], 1)
                #self.setComboBoxEditable(["self.comboBox_unita_tipo"], 1)
                #self.setComboBoxEnable(["self.comboBox_sito"], "True")
                #self.setComboBoxEnable(["self.comboBox_area"], "True")
                #self.setComboBoxEnable(["self.lineEdit_us"], "True")
                #self.setComboBoxEnable(["self.comboBox_unita_tipo"], "True")
                self.SORT_STATUS = "n"
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.enable_button(0)

    def on_pushButton_save_pressed(self):

        # self.checkBox_query.setChecked(False)
        # if self.checkBox_query.isChecked():
        #     self.model_a.database().close()
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L == 'it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                    elif self.L == 'de':
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                    else:
                        self.update_if(QMessageBox.warning(self, 'Error',
                                                           "The record has been changed. Do you want to save the changes?",
                                                           QMessageBox.Ok | QMessageBox.Cancel))
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)

                    self.fill_fields(self.REC_CORR)
                else:
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",
                                            QMessageBox.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.charge_records()
                    self.charge_list()
                    self.set_sito()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    #self.setComboBoxEditable(["self.comboBox_area"], 1)
                    self.setComboBoxEnable(["self.lineEdit_id_number"], "False")
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    #self.setComboBoxEnable(["self.comboBox_area"], "False")
                    #self.setComboBoxEnable(["self.lineEdit_us"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
            else:
                if self.L == 'it':
                    QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "ACHTUNG", "Problem der Dateneingabe", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "Problem with data entry", QMessageBox.Ok)


    def insert_new_rec(self):

        try:
            if self.lineEdit_us.text() == "":
                us = None
            else:
                us = int(self.lineEdit_us.text())

            if self.lineEdit_box.text() == "":
                box = None
            else:
                box = int(self.lineEdit_box.text())

            if self.lineEdit_anno.text() == "":
                anno = None
            else:
                anno = int(self.lineEdit_anno.text())

            if self.lineEdit_diametro_max.text() == "":
                diametro_max = None
            else:
                diametro_max = float(self.lineEdit_diametro_max.text())



            if self.lineEdit_qty.text() == "":
                qty = 0
            else:
                qty = int(self.lineEdit_qty.text())

            if self.lineEdit_diametro_rim.text() == "":
                diametro_rim = None
            else:
                diametro_rim = float(self.lineEdit_diametro_rim.text())

            if self.lineEdit_diametro_bottom.text() == "":
                diametro_bottom = None
            else:
                diametro_bottom = float(self.lineEdit_diametro_bottom.text())

            if self.lineEdit_diametro_height.text() == "":
                diametro_height = None
            else:
                diametro_height = float(self.lineEdit_diametro_height.text())

            if self.lineEdit_diametro_preserved.text() == "":
                diametro_preserved = None
            else:
                diametro_preserved = float(self.lineEdit_diametro_preserved.text())

            if self.lineEdit_bag.text() == "":
                bag = None
            else:
                bag = int(self.lineEdit_bag.text())
            data = self.DB_MANAGER.insert_pottery_values(
            self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
                    int(self.lineEdit_id_number.text()),
                    str(self.comboBox_sito.currentText()), 				#1 - Sito
                    str(self.comboBox_area.currentText()), 				#2 - Area
                    us,									#3 - US
                    box,
                    str(self.lineEdit_photo.text()),		#6 - descrizione
                    str(self.lineEdit_drawing.text()),#7 - interpretazione
                    anno,
                    str(self.comboBox_fabric.currentText()),								#14 - anno scavo
                    str(self.comboBox_percent.currentText()), 			#15 - metodo
                    str(self.comboBox_material.currentText()),			#9 - fase iniziale
                    str(self.comboBox_form.currentText()), 			#10 - periodo finale iniziale
                    str(self.comboBox_specific_form.currentText()), 			#11 - fase finale
                    str(self.comboBox_ware.currentText()),			#12 - scavato
                    str(self.comboBox_munsell.currentText()),							#13 - attivita
                    str(self.comboBox_surf_trat.currentText()),	#22 - conservazione												#18 - rapporti
                    str(self.comboBox_exdeco.currentText()),				#19 - data schedatura
                    str(self.comboBox_intdeco.currentText()),		#20 - schedatore
                    str(self.comboBox_wheel_made.currentText()),		#21 - formazione				#23 - colore
                    str(self.textEdit_descrip_ex_deco.toPlainText()),
                    str(self.textEdit_descrip_in_deco.toPlainText()),#24 - consistenza
                    str(self.textEdit_note.toPlainText()),
                    diametro_max,
                    qty,
                    diametro_rim,
                    diametro_bottom,
                    diametro_height,
                    diametro_preserved,
                    str(self.comboBox_specific_shape.currentText()),
                    bag,
                    str(self.comboBox_sector.currentText()),
                    )							#25 - struttura
                                                    #28 - documentazione
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    msg = self.ID_TABLE + u" already present in database"
                    QMessageBox.warning(self, "Warning", "Error"+ str(msg),  QMessageBox.Ok)
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Insert error 1 \n"+ str(msg),  QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Insert error 3 \n"+str(e),  QMessageBox.Ok)
            return 0
    #rif biblio
    # def on_pushButton_insert_row_rif_biblio_pressed(self):
    #     self.insert_new_row('self.tableWidget_rif_biblio')
    # def on_pushButton_remove_row_rif_biblio_pressed(self):
    #     self.remove_row('self.tableWidget_rif_biblio')
    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.lineEdit_id_number.text())) == 0:
            QMessageBox.warning(self, "Warning", "Site field. \n This field cannot be empty",  QMessageBox.Ok)
            test = 1

        if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
            QMessageBox.warning(self, "Warning", "Site field. \n This field cannot be empty",  QMessageBox.Ok)
            test = 1

        # if EC.data_is_empty(str(self.comboBox_area.currentText())) == 0:
        #     QMessageBox.warning(self, "Warning", "Area field. \n This field cannot be empty",  QMessageBox.Ok)
        #     test = 1
        #
        # if EC.data_is_empty(str(self.lineEdit_us.text())) == 0:
        #     QMessageBox.warning(self, "Warning", "US field. \n >This field cannot be empty",  QMessageBox.Ok)
        #     test = 1

        # area = self.comboBox_area.currentText()
        # us = self.lineEdit_us.text()
        # if us != "":
        #     if EC.data_is_int(us) == 0:
        #         QMessageBox.warning(self, "Warning", "US field. \n The value has to be numeric",  QMessageBox.Ok)
        #         test = 1

        return test

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L == 'it':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            elif self.L == 'de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore',
                                        "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                        QMessageBox.Ok | QMessageBox.Cancel))
            return 0
            # records surf functions



    def on_pushButton_view_all_pressed(self):

        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<class 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
    #records surf functions
    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:

            self.empty_fields()
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.fill_fields(0)
            self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)


    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except:
                pass

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR-1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                QMessageBox.warning(self, "Error", "You are on the first record!",  QMessageBox.Ok)
            else:

                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)


    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR+1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR-1
                QMessageBox.warning(self, "Error", "You are on the last record!",  QMessageBox.Ok)
            else:

                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)



    def on_pushButton_delete_pressed(self):
        if self.L == 'it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio!!!", "Tipo di errore: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "Il database è vuoto!", QMessageBox.Ok)
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
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
        elif self.L == 'de':
            msg = QMessageBox.warning(self, "Achtung!!!",
                                      "Willst du wirklich diesen Eintrag löschen? \n Der Vorgang ist unumkehrbar",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Messagge!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "Die Datenbank ist leer!", QMessageBox.Ok)
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
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
        else:
            msg = QMessageBox.warning(self, "Warning!!!",
                                      "Do you really want to break the record? \n Action is irreversible.",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Message", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.Ok)
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
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.charge_list()
                    self.fill_fields()
                    self.set_sito()
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])


    def on_pushButton_new_search_pressed(self):
        if self.BROWSE_STATUS != "f" and self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            conn = Connection()

            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']
            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:

                    self.BROWSE_STATUS = "f"
                    self.empty_fields_nosite()
                    self.lineEdit_box.setText("")
                    self.lineEdit_anno.setText("")
                    self.comboBox_fabric.setEditText("")
                    self.comboBox_ware.setEditText("")
                    #self.setComboBoxEditable(["self.comboBox_sito"],0)
                    #self.setComboBoxEditable(["self.comboBox_area"],1)
                    self.setComboBoxEnable(["self.lineEdit_id_number"],"True")
                    self.setComboBoxEnable(["self.comboBox_sito"],"False")
                    #self.setComboBoxEnable(["self.comboBox_area"],"True")
                    #self.setComboBoxEnable(["self.lineEdit_us"],"True")
                    #self.setComboBoxEnable(["self.lineEdit_qty"],"True")
                    #self.setTableEnable(["self.tableWidget_rif_biblio"], "False")
                    ###
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('','')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    #self.empty_fields()
                else:
                    self.BROWSE_STATUS = "f"

                    self.lineEdit_box.setText("")
                    self.lineEdit_anno.setText("")
                    self.comboBox_fabric.setEditText("")
                    self.comboBox_ware.setEditText("")
                    #self.setComboBoxEditable(["self.comboBox_sito"], 0)
                    #self.setComboBoxEditable(["self.comboBox_area"], 1)
                    self.setComboBoxEnable(["self.lineEdit_id_number"], "True")
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    #self.setComboBoxEnable(["self.comboBox_area"], "True")
                    #self.setComboBoxEnable(["self.lineEdit_us"], "True")
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.empty_fields()

    def on_pushButton_search_go_pressed(self):
        check_for_buttons = 0
        if self.BROWSE_STATUS != "f":
            if self.L == 'it':
                QMessageBox.warning(self, "ATTENZIONE",
                                    "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.Ok)
        else:
            if self.lineEdit_id_number.text() != "":
                id_number = int(self.lineEdit_id_number.text())
            else:
                id_number = ""
            if self.lineEdit_us.text() != "":
                us = int(self.lineEdit_us.text())
            else:
                us = ""
            if self.lineEdit_box.text() != "":
                box = int(self.lineEdit_box.text())
            else:
                box = ""
            if self.lineEdit_anno.text() != "":
                anno = int(self.lineEdit_anno.text())
            else:
                anno = ""



            if self.lineEdit_diametro_max.text() != "":
                diametro_max = float(self.lineEdit_diametro_max.text())
            else:
                diametro_max = None



            if self.lineEdit_qty.text() != "":
                qty = int(self.lineEdit_qty.text())
            else:
                qty = ""

            if self.lineEdit_diametro_rim.text() != "":
                diametro_rim = float(self.lineEdit_diametro_rim.text())
            else:
                diametro_rim = None

            if self.lineEdit_diametro_bottom.text() != "":
                diametro_bottom = float(self.lineEdit_diametro_bottom.text())
            else:
                diametro_bottom = None

            if self.lineEdit_diametro_height.text() != "":
                diametro_height = float(self.lineEdit_diametro_height.text())
            else:
                diametro_height = None

            if self.lineEdit_diametro_preserved.text() != "":
                diametro_preserved = float(self.lineEdit_diametro_preserved.text())
            else:
                diametro_preserved = None

            if self.lineEdit_bag.text() != "":
                bag = int(self.lineEdit_bag.text())
            else:
                bag = ""
            search_dict = {
            self.TABLE_FIELDS[0]  : id_number,									#1 - Sito
            self.TABLE_FIELDS[1]  : "'"+str(self.comboBox_sito.currentText())+"'",								#2 - Area
            self.TABLE_FIELDS[2]  : "'"+str(self.comboBox_area.currentText())+"'",																									#3 - US
            self.TABLE_FIELDS[3]  : us,								#4 - Definizione stratigrafica
            self.TABLE_FIELDS[4]  : box,							#5 - Definizione intepretata
            self.TABLE_FIELDS[5]  : "'"+str(self.lineEdit_photo.text())+"'",											#6 - descrizione
            self.TABLE_FIELDS[6]  : "'"+str(self.lineEdit_drawing.text())+"'",										#7 - interpretazione
            self.TABLE_FIELDS[7]  : anno,								#8 - periodo iniziale
            self.TABLE_FIELDS[8]  : "'"+str(self.comboBox_fabric.currentText())+"'",								#9 - fase iniziale
            self.TABLE_FIELDS[9]  : "'"+str(self.comboBox_percent.currentText())+"'",	 							#10 - periodo finale iniziale
            self.TABLE_FIELDS[10] : "'"+str(self.comboBox_material.currentText())+"'", 								#11 - fase finale
            self.TABLE_FIELDS[11] : "'"+str(self.comboBox_form.currentText())+"'",								#12 - scavato
            self.TABLE_FIELDS[12] : "'"+str(self.comboBox_specific_form.currentText())+"'",												#13 - attivita
            self.TABLE_FIELDS[13] : "'"+str(self.comboBox_ware.currentText())+"'",													#14 - anno scavo
            self.TABLE_FIELDS[14] : "'"+str(self.comboBox_munsell.currentText())+"'", 								#15 - metodo
            self.TABLE_FIELDS[15] : "'"+str(self.comboBox_surf_trat.currentText())+"'",
            self.TABLE_FIELDS[16] : "'"+str(self.comboBox_exdeco.currentText())+"'",
            self.TABLE_FIELDS[17] : "'"+str(self.comboBox_intdeco.currentText())+"'",
            self.TABLE_FIELDS[18] : "'"+str(self.comboBox_wheel_made.currentText())+"'",#16 - data schedatura
            self.TABLE_FIELDS[19] : "'"+str(self.textEdit_descrip_ex_deco.toPlainText())+ "'",
            self.TABLE_FIELDS[20] : "'"+str(self.textEdit_descrip_in_deco.toPlainText())+ "'",
            self.TABLE_FIELDS[21] : "'"+str(self.textEdit_note.toPlainText())+ "'",				#19 - conservazione
            self.TABLE_FIELDS[22] : diametro_max,
            self.TABLE_FIELDS[23] : qty,
            self.TABLE_FIELDS[24] : diametro_rim, 								#15 - metodo
            self.TABLE_FIELDS[25] : diametro_bottom,
            self.TABLE_FIELDS[26] : diametro_height,
            self.TABLE_FIELDS[27] : diametro_preserved,
            self.TABLE_FIELDS[28] : "'"+str(self.comboBox_specific_shape.currentText())+"'",
            self.TABLE_FIELDS[29]: bag,
            self.TABLE_FIELDS[30]: "'" + str(self.comboBox_sector.currentText()) + "'",
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                if self.L == 'it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    #self.setComboBoxEnable(["self.comboBox_area"], "True")

                    #self.setComboBoxEnable(["self.lineEdit_us"], "True")


                    self.fill_fields(self.REC_CORR)
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
                    if self.L == 'it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")

                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")

                    elif self.L == 'de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")

                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")

                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")

                        else:
                            strings = ("They have been found", self.REC_TOT, "records")


                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    #self.setComboBoxEnable(["self.comboBox_area"], "True")
                    #self.setComboBoxEnable(["self.lineEdit_us"], "True")


                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)
        self.enable_button_search(1)

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i." + self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS,
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
            str(e)
            save_file = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Report_folder")
            file_ = os.path.join(save_file, 'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            if self.L == 'it':
                QMessageBox.warning(self, "Messaggio",
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report _Folder",
                                    QMessageBox.Ok)


            elif self.L == 'de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report _Folder",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report _Ordner abrufen können",
                                    QMessageBox.Ok)

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

    def yearstrfdate(self):
        now = date.today()
        year = now.strftime("%Y")
        return year

    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename+".rowCount()")
        col = eval(self.tablename+".columnCount()")
        lista=[]
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename+".item(r,c)")
                if value != None:
                    sub_list.append(str(value.text()))

            if bool(sub_list) == True:
                lista.append(sub_list)

        return lista


    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()

        #column table count
        table_col_count_cmd = ("%s.columnCount()") % (self.table_name)
        table_col_count = eval(table_col_count_cmd)

        #clear table
        table_clear_cmd = ("%s.clearContents()") % (self.table_name)
        eval(table_clear_cmd)

        for i in range(table_col_count):
            table_rem_row_cmd = ("%s.removeRow(%d)") % (self.table_name, i)
            eval(table_rem_row_cmd)

        for i in range(len(self.data_list)):
            self.insert_new_row(self.table_name)

        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                #item = self.comboBox_sito.setEditText(self.data_list[0][col]
                item = QTableWidgetItem(str(self.data_list[row][col]))
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name,row,col)
                eval(exec_str)





    def empty_fields(self):
        #rif_biblio_row_count = self.tableWidget_rif_biblio.rowCount()
        self.lineEdit_id_number.clear()
        self.comboBox_sito.setEditText("")  								#1 - Sito
        self.comboBox_area.setEditText("") 								#2 - Area
        self.lineEdit_us.clear()													#3 - US
        self.lineEdit_box.clear()						#4 - Definizione stratigrafica					#5 - Definizione intepretata
        self.lineEdit_photo.clear()#9 - fase iniziale
        self.lineEdit_drawing.clear()									#7 - interpretazione
        self.lineEdit_anno.clear()
        self.comboBox_fabric.setEditText("")
        self.comboBox_percent.setEditText("")
        self.comboBox_material.setEditText("")									#8 - periodo iniziale
        self.comboBox_form.setEditText("")
        self.comboBox_specific_form.setEditText("")
        self.comboBox_ware.setEditText("")								#10 - periodo finale iniziale
        self.comboBox_munsell.setEditText("")								#11 - fase finale
        self.comboBox_surf_trat.setEditText("")								#12 - scavato
        self.comboBox_exdeco.setEditText("")	#20 - data schedatura											#13 - attivita
        self.comboBox_intdeco.setEditText("")						#21 - schedatore
        self.comboBox_wheel_made.setEditText("")				#22 - formazione
        self.textEdit_descrip_ex_deco.clear()#6 - descrizione
        self.textEdit_descrip_in_deco.clear()
        self.textEdit_note.clear()
        self.lineEdit_diametro_max.clear()

        self.lineEdit_qty.clear()
        self.lineEdit_diametro_rim.clear()
        self.lineEdit_diametro_bottom.clear()
        self.lineEdit_diametro_height.clear()
        self.lineEdit_diametro_preserved.clear()
        self.comboBox_specific_shape.setEditText("")
        self.lineEdit_bag.clear()
        self.comboBox_sector.setEditText("")
        #for i in range(rif_biblio_row_count):
            #self.tableWidget_rif_biblio.removeRow(0)
        #self.insert_new_row("self.tableWidget_rif_biblio")
    def empty_fields_nosite(self):
        #rif_biblio_row_count = self.tableWidget_rif_biblio.rowCount()
        self.lineEdit_id_number.clear()
         								#1 - Sito
        self.comboBox_area.setEditText("") 								#2 - Area
        self.lineEdit_us.clear()													#3 - US
        self.lineEdit_box.clear()						#4 - Definizione stratigrafica					#5 - Definizione intepretata
        self.lineEdit_photo.clear()#9 - fase iniziale
        self.lineEdit_drawing.clear()									#7 - interpretazione
        self.lineEdit_anno.clear()
        self.comboBox_fabric.setEditText("")
        self.comboBox_percent.setEditText("")
        self.comboBox_material.setEditText("")									#8 - periodo iniziale
        self.comboBox_form.setEditText("")
        self.comboBox_specific_form.setEditText("")
        self.comboBox_ware.setEditText("")								#10 - periodo finale iniziale
        self.comboBox_munsell.setEditText("")								#11 - fase finale
        self.comboBox_surf_trat.setEditText("")								#12 - scavato
        self.comboBox_exdeco.setEditText("")	#20 - data schedatura											#13 - attivita
        self.comboBox_intdeco.setEditText("")						#21 - schedatore
        self.comboBox_wheel_made.setEditText("")				#22 - formazione
        self.textEdit_descrip_ex_deco.clear()#6 - descrizione
        self.textEdit_descrip_in_deco.clear()
        self.textEdit_note.clear()
        self.lineEdit_diametro_max.clear()

        self.lineEdit_qty.clear()
        self.lineEdit_diametro_rim.clear()
        self.lineEdit_diametro_bottom.clear()
        self.lineEdit_diametro_height.clear()
        self.lineEdit_diametro_preserved.clear()
        self.comboBox_specific_shape.setEditText("")
        self.lineEdit_bag.clear()
        self.comboBox_sector.setEditText("")
        #for i in range(rif_biblio_row_count):
            #self.tableWidget_rif_biblio.removeRow(0)
        #self.insert_new_row("self.tableWidget_rif_biblio")

    def fill_fields(self, n=0):
        self.rec_num = n
        #QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
        try:
            self.lineEdit_id_number.setText(str(self.DATA_LIST[self.rec_num].id_number))	#3 - US
            str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))													#1 - Sito
            str(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))												#2 - Area
            if not self.DATA_LIST[self.rec_num].us:
                self.lineEdit_us.setText("")
            else:
                self.lineEdit_us.setText(str(self.DATA_LIST[self.rec_num].us))
            if not self.DATA_LIST[self.rec_num].box:
                self.lineEdit_box.setText("")
            else:
                self.lineEdit_box.setText(str(self.DATA_LIST[self.rec_num].box))
            str(self.lineEdit_photo.setText(self.DATA_LIST[self.rec_num].photo))
            str(self.lineEdit_drawing.setText(self.DATA_LIST[self.rec_num].drawing))
            if not self.DATA_LIST[self.rec_num].anno:
                self.lineEdit_anno.setText("")
            else:
                self.lineEdit_anno.setText(str(self.DATA_LIST[self.rec_num].anno))
            str(self.comboBox_fabric.setEditText(self.DATA_LIST[self.rec_num].fabric))
            str(self.comboBox_percent.setEditText(self.DATA_LIST[self.rec_num].percent))#5 - Definizione intepretata
            str(self.comboBox_material.setEditText(self.DATA_LIST[self.rec_num].material))
            str(self.comboBox_form.setEditText(self.DATA_LIST[self.rec_num].form))#5 - Definizione intepretata
            str(self.comboBox_specific_form.setEditText(self.DATA_LIST[self.rec_num].specific_form))#5 - Definizione intepretata
            str(self.comboBox_ware.setEditText(self.DATA_LIST[self.rec_num].ware))#5 - Definizione intepretata
            str(self.comboBox_munsell.setEditText(self.DATA_LIST[self.rec_num].munsell))#5 - Definizione intepretata
            str(self.comboBox_surf_trat.setEditText(self.DATA_LIST[self.rec_num].surf_trat))#5 - Definizione intepretata
            str(self.comboBox_exdeco.setEditText(self.DATA_LIST[self.rec_num].exdeco))#5 - Definizione intepretata
            str(self.comboBox_intdeco.setEditText(self.DATA_LIST[self.rec_num].intdeco))#5 - Definizione intepretata
            str(self.comboBox_wheel_made.setEditText(self.DATA_LIST[self.rec_num].wheel_made))#5 - Definizione intepretata
            str(self.textEdit_descrip_in_deco.setText(self.DATA_LIST[self.rec_num].descrip_in_deco))								#6 - descrizione
            str(self.textEdit_descrip_ex_deco.setText(self.DATA_LIST[self.rec_num].descrip_ex_deco))
            str(self.textEdit_note.setText(self.DATA_LIST[self.rec_num].note))
            #7 - interpretazione


            #self.tableInsertData("self.tableWidget_rif_biblio", self.DATA_LIST[self.rec_num].rif_biblio)
            if not self.DATA_LIST[self.rec_num].diametro_max:
                self.lineEdit_diametro_max.setText("")
            else:
                self.lineEdit_diametro_max.setText(str(self.DATA_LIST[self.rec_num].diametro_max))
            if not self.DATA_LIST[self.rec_num].qty:
                self.lineEdit_qty.setText("")
            else:
                self.lineEdit_qty.setText(str(self.DATA_LIST[self.rec_num].qty))

            if not self.DATA_LIST[self.rec_num].diametro_rim:
                self.lineEdit_diametro_rim.setText("")
            else:
                self.lineEdit_diametro_rim.setText(str(self.DATA_LIST[self.rec_num].diametro_rim))

            if not self.DATA_LIST[self.rec_num].diametro_bottom:
                self.lineEdit_diametro_bottom.setText("")
            else:
                self.lineEdit_diametro_bottom.setText(str(self.DATA_LIST[self.rec_num].diametro_bottom))

            if not self.DATA_LIST[self.rec_num].diametro_height:
                self.lineEdit_diametro_height.setText("")
            else:
                self.lineEdit_diametro_height.setText(str(self.DATA_LIST[self.rec_num].diametro_height))

            if not self.DATA_LIST[self.rec_num].diametro_preserved:
                self.lineEdit_diametro_preserved.setText("")
            else:
                self.lineEdit_diametro_preserved.setText(str(self.DATA_LIST[self.rec_num].diametro_preserved))


            str(self.comboBox_specific_shape.setEditText(self.DATA_LIST[self.rec_num].specific_shape))

            if not self.DATA_LIST[self.rec_num].bag:
                self.lineEdit_bag.setText("")
            else:
                self.lineEdit_bag.setText(str(self.DATA_LIST[self.rec_num].bag))

            str(self.comboBox_sector.setEditText(self.DATA_LIST[self.rec_num].sector))

            if self.toolButtonPreviewMedia.isChecked() == False:
                self.loadMediaPreview()
        except Exception as e:
            QMessageBox.warning(self, "Error Fill Fields", str(e),  QMessageBox.Ok)
    
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        if self.lineEdit_us.text() == "":
            us = None
        else:
            us = int(self.lineEdit_us.text())

        if self.lineEdit_box.text() == "":
            box =None
        else:
            box = int(self.lineEdit_box.text())

        if self.lineEdit_anno.text() == "":
            anno = None
        else:
            anno = int(self.lineEdit_anno.text())



        if self.lineEdit_diametro_max.text() == "":
            diametro_max = None
        else:
            diametro_max = float(self.lineEdit_diametro_max.text())


        if self.lineEdit_qty.text() == "":
            qty = 0
        else:
            qty = int(self.lineEdit_qty.text())

        if self.lineEdit_diametro_rim.text() == "":
            diametro_rim = None
        else:
            diametro_rim = float(self.lineEdit_diametro_rim.text())

        if self.lineEdit_diametro_bottom.text() == "":
            diametro_bottom = None
        else:
            diametro_bottom = float(self.lineEdit_diametro_bottom.text())

        if self.lineEdit_diametro_height.text() == "":
            diametro_height = None
        else:
            diametro_height = float(self.lineEdit_diametro_height.text())

        if self.lineEdit_diametro_preserved.text() == "":
            diametro_preserved = None
        else:
            diametro_preserved = float(self.lineEdit_diametro_preserved.text())

        if self.lineEdit_bag.text() == "":
            bag = None
        else:
            bag = int(self.lineEdit_bag.text())


        self.DATA_LIST_REC_TEMP = [
        str(self.lineEdit_id_number.text()),	#3 - US
        str(self.comboBox_sito.currentText()), 						#1 - Sito
        str(self.comboBox_area.currentText()), 						#2 - Area
        str(us),
        str(box),
        str(self.lineEdit_photo.text()),
        str(self.lineEdit_drawing.text()),
        str(anno),	#3 - US
        str(self.comboBox_fabric.currentText()),
        str(self.comboBox_percent.currentText()),
        str(self.comboBox_material.currentText()),#4 - Definizione stratigrafica
        str(self.comboBox_form.currentText()),
        str(self.comboBox_specific_form.currentText()),
        str(self.comboBox_ware.currentText()),
        str(self.comboBox_munsell.currentText()),
        str(self.comboBox_surf_trat.currentText()),
        str(self.comboBox_exdeco.currentText()),
        str(self.comboBox_intdeco.currentText()),
        str(self.comboBox_wheel_made.currentText()),
        str(self.textEdit_descrip_ex_deco.toPlainText()),		#6 - descrizione
        str(self.textEdit_descrip_in_deco.toPlainText()),
        str(self.textEdit_note.toPlainText()),
        str(diametro_max),

        str(qty),
        str(diametro_rim),
        str(diametro_bottom),
        str(diametro_height),
        str(diametro_preserved),
        str(self.comboBox_specific_shape.currentText()),
        str(bag),
        str(self.comboBox_sector.currentText()),
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        #QMessageBox.warning(self, "Error", str(self.DATA_LIST_REC_CORR) + str(self.DATA_LIST_REC_TEMP),  QMessageBox.Ok)
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

    def on_pushButton_open_dir_pressed(self):
        HOME = os.environ['PYARCHINIT_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


