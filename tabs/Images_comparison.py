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

from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.PyQt.uic import loadUiType

from PIL import Image
import numpy as np

from ..modules.utility.pyarchinit_media_utility import *
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility

filepath = os.path.dirname(__file__)

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Images_comparison.ui'))


class Comparision(QDialog, MAIN_DIALOG_CLASS):
    delegateSites = ''
    DB_MANAGER = ""
    TABLE_NAME = 'media_table'
    MAPPER_TABLE_CLASS = "MEDIA"
    ID_TABLE = "id_media"
    MAPPER_TABLE_CLASS_mediatoentity = 'MEDIATOENTITY'
    ID_TABLE_mediatoentity = 'id_mediaToEntity'
    NOME_SCHEDA = "Scheda Media Manager"

    TABLE_THUMB_NAME = 'media_thumb_table'
    MAPPER_TABLE_CLASS_thumb = 'MEDIA_THUMB'
    ID_TABLE_THUMB = "id_media_thumb"

    UTILITY = Utility()

    DATA = ''
    NUM_DATA_BEGIN = 0
    NUM_DATA_END = 25

    PATH = ""
    FILE = ""

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("pyArchInit - Images Comparision Tools")
        QMessageBox.warning(self, "Alert", "Sistema sperimentale solo per lo sviluppo", QMessageBox.Ok)

    def connection(self):

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "La connessione e' fallita <br><br> Tabella non presente. E' NECESSARIO RIAVVIARE QGIS",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e),
                                    QMessageBox.Ok)

    def on_pushButton_chose_dir_pressed(self):
        path = QFileDialog.getExistingDirectory(self, "Scegli una directory", "Seleziona una directory:",
                                                QFileDialog.ShowDirsOnly)
        if path:
            self.PATH = path

    def on_pushButton_chose_file_pressed(self):
        file = QFileDialog.getOpenFileName(self, 'Open file', os.environ['PYARCHINIT_HOME'], '(*.png *.xpm *.jpg)')
        if file:
            self.FILE = str(file[0])

    def on_pushButton_run_pressed(self):
        file_list = self.generate_files_couples()
        lista = []
        lunghezza = len(file_list)
        calculate_res = None
        for i in file_list:
            calculate_res = self.calculate([i[0], i[1]])

            if calculate_res is not None:
                tupla_di_ritorno = calculate_res
                lista.append(tupla_di_ritorno)
                lunghezza -= 1
            calculate_res = None
        self.plot_chart(lista)

    def calculate(self, imgs):
        try:
            img1 = Image.open(str(imgs[0]))
            img2 = Image.open(str(imgs[1]))

            if img1.size != img2.size or img1.getbands() != img2.getbands():
                return -1

            s = 0
            for band_index, band in enumerate(img1.getbands()):
                m1 = np.array([p[band_index] for p in img1.getdata()]).reshape(*img1.size)
                m2 = np.array([p[band_index] for p in img2.getdata()]).reshape(*img2.size)
                s += np.sum(np.abs(m1 - m2))
            s = s / 1000000

            (filepath1, filename1) = os.path.split(str(imgs[0]))
            (filepath2, filename2) = os.path.split(str(imgs[1]))
            label = filename1 + "-" + filename2

            return (label, s)
        except Exception as e:
            QMessageBox.warning(self, "Messaggio", str(e), QMessageBox.Ok)

    def generate_files_couples(self):
        path = self.PATH

        lista_files = os.listdir(path)
        lista_files_dup = lista_files

        lista_con_coppie = []

        for sing_file in lista_files:
            path1 = self.FILE
            path2 = path + os.sep + str(sing_file)
            lista_con_coppie.append([path1, path2])

        return lista_con_coppie

    def plot_chart(self, d):
        self.data_list = d
        try:
            if isinstance(self.data_list, list):
                data_diz = {}
                for item in self.data_list:
                    if not isinstance(item, int):
                        data_diz[item[0]] = item[1]
            x = list(range(len(data_diz)))
            n_bars = len(data_diz)
            values = list(data_diz.values())
            teams = list(data_diz.keys())
            ind = np.arange(n_bars)
            self.widget.canvas.ax.clear()

            bars = self.widget.canvas.ax.bar(left=x, height=values, width=0.3, align='center', alpha=0.4, picker=5)

            self.widget.canvas.ax.set_title('Classifica')
            self.widget.canvas.ax.set_ylabel('Indice di differenza')
            n = 0
            for bar in bars:
                val = int(bar.get_height())
                x_pos = bar.get_x() + 0.2
                y_pos = 1.5  # bar.get_height() - 1
                self.widget.canvas.ax.text(x_pos, y_pos, teams[n], zorder=0, ha='center', va='center', size='x-small',
                                           rotation=90)
                n += 1
        except:
            QMessageBox.warning(self, "self.data_list", str(self.data_list), QMessageBox.Ok)

        self.widget.canvas.draw()
