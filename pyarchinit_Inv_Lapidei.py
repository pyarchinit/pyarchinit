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
import csv_writer
from csv_writer import *
import sys, os
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
try:
	from qgis.core import *
	from qgis.gui import *
except:
	pass

from datetime import date
from psycopg2 import *

from  pyarchinit_exp_Invlapsheet_pdf import *

#--import pyArchInit modules--#
#from  pyarchinit_inventario_reperti_ui import Ui_DialogSchedaRavenna
from  pyarchinit_scheda_Lapidei_ui import *
from  pyarchinit_utility import *
from  pyarchinit_error_check import *
import shutil

try:
	from  pyarchinit_db_manager import *
except:
	pass
from  sortpanelmain import SortPanelMain
from  quantpanelmain import QuantPanelMain

##from  pyarchinit_exp_Findssheet_pdf import *

from  imageViewer import ImageViewer
import numpy as np
import random
from numpy import *

from  delegateComboBox import *




class pyarchinit_Inventario_Lapidei(QDialog, Ui_DialogSchedaLapidei):
##	MSG_BOX_TITLE = "PyArchInit - Scheda Inventario Lapidei"
	DATA_LIST = []
	DATA_LIST_REC_CORR = []
	DATA_LIST_REC_TEMP = []
	REC_CORR = 0
	REC_TOT = 0
	BROWSE_STATUS = "b"
	STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
	SORT_MODE = 'asc'
	SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
	SORT_STATUS = "n"
	UTILITY = Utility()
	DB_MANAGER = ""
	TABLE_NAME = 'inventario_lapidei_table'
	MAPPER_TABLE_CLASS = "INVENTARIO_LAPIDEI"
	NOME_SCHEDA = "Scheda 	 Scheda reperti lapidei"
	ID_TABLE = "id_invlap"
	
	CONVERSION_DICT = {
	ID_TABLE:ID_TABLE,
	"Sito" : "sito",
	"Scheda Numero" : "scheda_numero",
	"Collocazione" : "collocazione",
	"Oggetto" : "oggetto",
	"Tipologia" : "tipologia",
	"Materiale" : "materiale",
	"D (letto posa)" : "d_letto_posa",
	"d (letto attesa)" : "d_letto_attesa",
	"Toro" : "toro",
	"Spessore" : "spessore",
	"Larghezza" : "larghezza",
	"Lunghezza" : "lunghezza",
	"h" : 'h',
	"Descrizione" : 'descrizione',
	"Lavorazione e stato di conservazione" : 'lavorazione_e_stato_di_conservazione',
	"Confronti" : 'confronti',
	"Cronologia" : 'cronologia',
	"Bibliografia": 'bibliografia',
	"Autore scheda" : 'compilatore'
	}

	SORT_ITEMS = [
				ID_TABLE,
				"Sito",
				"Scheda Numero",
				"Collocazione",
				"Oggetto",
				"Tipologia",
				"Materiale",
				"D (letto posa)",
				"d (letto attesa)",
				"Toro",
				"Spessore"
				"Larghezza",
				"Lunghezza",
				"h",
				"Descrizione",
				"Lavorazione e stato di conservazione",
				"Confronti",
				"Cronologia",
				"Bibliografia",
				"Autore scheda"
				]

	TABLE_FIELDS = [
					"sito",
					"scheda_numero",
					"collocazione",
					"oggetto",
					"tipologia",
					"materiale",
					"d_letto_posa",
					"d_letto_attesa",
					"toro",
					"spessore",
					"larghezza",
					"lunghezza",
					"h",
					"descrizione",
					"lavorazione_e_stato_di_conservazione",
					"confronti",
					"cronologia",
					"bibliografia",
					"compilatore"
					]

	TABLE_FIELDS_UPDATE = [
					"collocazione",
					"oggetto",
					"tipologia",
					"materiale",
					"d_letto_posa",
					"d_letto_attesa",
					"toro",
					"spessore",
					"larghezza",
					"lunghezza",
					"h",
					"descrizione",
					"lavorazione_e_stato_di_conservazione",
					"confronti",
					"cronologia",
					"bibliografia",
					"compilatore"
					]

	SEARCH_DICT_TEMP = ""

	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']
	
#	QUANT_PATH = ('%s%s%s') % (HOME, os.sep, "pyarchinit_Quantificazioni_folder")

	DB_SERVER = 'not defined'

	def __init__(self, iface):
		self.iface = iface

		QDialog.__init__(self)
		self.setupUi(self)
		self.currentLayerId = None
		try:
			self.on_pushButton_connect_pressed()
		except Exception as e:
			QMessageBox.warning(self, "Sistema di connessione", str(e),  QMessageBox.Ok)


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

		bars = self.widget.canvas.ax.bar(left=x, height=values, width=0.5, align='center', alpha=0.4,picker=5)
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

	def on_pushButton_connect_pressed(self):
		from pyarchinit_conn_strings import *
		#self.setComboBoxEditable(["self.comboBox_sito"],1)
		conn = Connection()
		conn_str = conn.conn_str()

		test_conn = conn_str.find('sqlite')

		if test_conn == 0:
			self.DB_SERVER = "sqlite"

		try:
			self.DB_MANAGER = Pyarchinit_db_management(conn_str)
			self.DB_MANAGER.connection()
			self.charge_records()
			#check if DB is empty
			if bool(self.DATA_LIST) == True:
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
				self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
				self.BROWSE_STATUS = "b"
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.label_sort.setText(self.SORTED_ITEMS["n"])
				self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
				self.charge_list()
				self.fill_fields()
			else:
				QMessageBox.warning(self, "BENVENUTO", "Benvenuto in pyArchInit" + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",  QMessageBox.Ok)
				self.charge_list()
				self.BROWSE_STATUS = 'x'
				self.on_pushButton_new_rec_pressed()
		except Exception as e:
			e = str(e)
			if e.find("no such table"):
				QMessageBox.warning(self, "Alert", "La connessione e' fallita <br><br> E' NECESSARIO RIAVVIARE QGIS " + e ,  QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Alert", "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e) ,  QMessageBox.Ok)

	def customize_gui(self):
		#media prevew system
		self.iconListWidget = QtGui.QListWidget(self)
		self.iconListWidget.setFrameShape(QtGui.QFrame.StyledPanel)
		self.iconListWidget.setFrameShadow(QtGui.QFrame.Sunken)
		self.iconListWidget.setLineWidth(2)
		self.iconListWidget.setMidLineWidth(2)
		self.iconListWidget.setProperty("showDropIndicator", False)
		self.iconListWidget.setIconSize(QtCore.QSize(150, 150))
		self.iconListWidget.setMovement(QtGui.QListView.Snap)
		self.iconListWidget.setResizeMode(QtGui.QListView.Adjust)
		self.iconListWidget.setLayoutMode(QtGui.QListView.Batched)
		self.iconListWidget.setGridSize(QtCore.QSize(160, 160))
		self.iconListWidget.setViewMode(QtGui.QListView.IconMode)
		self.iconListWidget.setUniformItemSizes(True)
		self.iconListWidget.setBatchSize(1000)
		self.iconListWidget.setObjectName("iconListWidget")
		self.iconListWidget.SelectionMode()
		self.iconListWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		self.connect(self.iconListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.openWide_image)
		self.tabWidget.addTab(self.iconListWidget, "Media")
		
		#delegate combobox

#		valuesTE = ["frammento", "frammenti", "intero", "integro"]
#		self.delegateTE = ComboBoxDelegate()
#		self.delegateTE.def_values(valuesTE)
#		self.delegateTE.def_editable('False')
#		self.tableWidget_elementi_reperto.setItemDelegateForColumn(1,self.delegateTE)


#	def loadMediaPreview(self, mode = 0):
		self.iconListWidget.clear()
		if mode == 0:
			""" if has geometry column load to map canvas """

			rec_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
			search_dict = {'id_entity'  : "'"+str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'REPERTO'"}
			record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
			for i in record_us_list:
				search_dict = {'id_media' : "'"+str(i.id_media)+"'"}

				u = Utility()
				search_dict = u.remove_empty_items_fr_dict(search_dict)
				mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
				thumb_path = str(mediathumb_data[0].filepath)

				item = QListWidgetItem(str(i.id_media))

				item.setData(QtCore.Qt.UserRole,str(i.id_media))
				icon = QIcon(thumb_path)
				item.setIcon(icon)
				self.iconListWidget.addItem(item)
		elif mode == 1:
			self.iconListWidget.clear()


	def openWide_image(self):
		items = self.iconListWidget.selectedItems()
		for item in items:
			dlg = ImageViewer(self)
			id_orig_item = item.text() #return the name of original file

			search_dict = {'id_media' : "'"+str(id_orig_item)+"'"}

			u = Utility()
			search_dict = u.remove_empty_items_fr_dict(search_dict)

			try:
				res = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
				file_path = str(res[0].filepath)
			except Exception as e:
				QMessageBox.warning(self, "Errore", "Attenzione 1 file: "+ str(e),  QMessageBox.Ok)

			dlg.show_image(str(file_path)) #item.data(QtCore.Qt.UserRole).toString()))
			dlg.exec_()

	def charge_list(self):
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


		#lista definizione_sito
#		search_dict = {
#		'nome_tabella'  : "'"+'inventario_lapidei_table'+"'",
#		'tipologia_sigla' : "'"+'definizione sito'+"'"
#		}

#		sito = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')

#		sito_vl = [ ]


	#buttons functions

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

##	def on_toolButtonPreviewMedia_toggled(self):
##		if self.toolButtonPreviewMedia.isChecked() == True:
##			QMessageBox.warning(self, "Messaggio", "Modalita' Preview Media Reperti attivata. Le immagini dei Reperti saranno visualizzate nella sezione Media", QMessageBox.Ok)
##			self.loadMediaPreview()
##		else:
##			self.loadMediaPreview(1)

	def on_pushButton_new_rec_pressed(self):
		if bool(self.DATA_LIST) == True:
			if self.data_error_check() == 1:
				pass
			else:
				if self.BROWSE_STATUS == "b":
					if bool(self.DATA_LIST) == True:
						if self.records_equal_check() == 1:
							msg = self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))

		if self.BROWSE_STATUS != "n":
			self.BROWSE_STATUS = "n"
			self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
			self.empty_fields()

			self.setComboBoxEditable(['self.comboBox_sito'], 0)
			#self.setComboBoxEditable(['self.comboBox_sito'], 1)
			self.setComboBoxEnable(['self.comboBox_sito'], 'True')
			self.setComboBoxEnable(['self.lineEdit_num_inv'], 'True')

			self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

			self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
			self.set_rec_counter('','')
			self.label_sort.setText(self.SORTED_ITEMS["n"])
			self.empty_fields()

			self.enable_button(0)

	def on_pushButton_save_pressed(self):
		#save record
		if self.BROWSE_STATUS == "b":
			if self.data_error_check() == 0:
				if self.records_equal_check() == 1:
					self.update_if(QMessageBox.warning(self,'ATTENZIONE',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
					self.SORT_STATUS = "n"
					self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
					self.enable_button(1)
					self.fill_fields(self.REC_CORR)
				else:
					QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",  QMessageBox.Ok)
		else:
			if self.data_error_check() == 0:
				test_insert = self.insert_new_rec()
				if test_insert == 1:
					self.empty_fields()
					self.SORT_STATUS = "n"
					self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
					self.charge_records()
					self.charge_list()
					self.BROWSE_STATUS = "b"
					self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
					self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)

					self.setComboBoxEditable(['self.comboBox_sito'], 1)
					self.setComboBoxEnable(['self.comboBox_sito'], 'False')
					self.setComboBoxEnable(['self.lineEdit_num_inv'], 'False')

					self.fill_fields(self.REC_CORR)
					self.enable_button(1)
				
	def generate_list_pdf(self):
		data_list = []
		for i in range(len(self.DATA_LIST)):
			data_list.append([
			str(self.DATA_LIST[i].id_invlap), 							#0 - id_invlap
			str(self.DATA_LIST[i].sito),								#1- contesto_provenienza
			int(self.DATA_LIST[i].scheda_numero),				#2- scheda_numero
			str(self.DATA_LIST[i].collocazione),					#3 - collocazione
			str(self.DATA_LIST[i].oggetto),			#4 - oggetto
			str(self.DATA_LIST[i].tipologia),					#5 - tipologia
			str(self.DATA_LIST[i].materiale),					#6 - materiale
			str(self.DATA_LIST[i].d_letto_posa),								#7 - D_letto_posa
			str(self.DATA_LIST[i].d_letto_attesa),							#8 - d_letto_attesa
			str(self.DATA_LIST[i].toro), 						#9 - toro
			str(self.DATA_LIST[i].spessore),		#10 - spessore
			str(self.DATA_LIST[i].larghezza),		#11 - larghezza
			str(self.DATA_LIST[i].lunghezza),			#12 - lunghezza
			str(self.DATA_LIST[i].h),			#13 - h
			str(self.DATA_LIST[i].descrizione),					#14 - descrizione
			str(self.DATA_LIST[i].lavorazione_e_stato_di_conservazione),						#15 - lavorazione_e_stato_di_conservazione
			str(self.DATA_LIST[i].confronti),						#16 - confronti
			str(self.DATA_LIST[i].cronologia),								#17 - .cronologia
			str(self.DATA_LIST[i].bibliografia),				#18 - .bibliografia
			str(self.DATA_LIST[i].compilatore)				#19 - autore scheda
		])
		return data_list

	def on_pushButton_exp_pdf_sheet_pressed(self):
		if self.records_equal_check() == 1:
			self.update_if(QMessageBox.warning(self,'Errore',"Il record è stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))

		Invlap_pdf_sheet = generate_reperti_pdf()
		data_list = self.generate_list_pdf()
		Invlap_pdf_sheet.build_Invlap_sheets(data_list)
#********************************************************************************
##			###cerca le singole area/us presenti in quella cassa
##			res_tip_reperto = self.DB_MANAGER.query_distinct('INVENTARIO_MATERIALI',[['sito','"Sito archeologico"'], ['nr_cassa',cassa]], ['tipo_reperto'])
##
##			tip_rep_res_list = ""
##			for i in res_tip_reperto:
##				tip_rep_res_list += str(i.tipo_reperto) +"<br/>"
##
##			#inserisce l'elenco degli inventari
##			single_cassa.append(tip_rep_res_list)
##
##		#QMessageBox.warning(self,'tk',str(data_for_pdf), QMessageBox.Ok)
##		return data_for_pdf

####################################################
#********************************************************************************

	def data_error_check(self):
		test = 0
		EC = Error_check()

		nr_inv = self.lineEdit_num_inv.text()
#		d_letto_posa = self.lineEdit_d_letto_posa.text()
#		d_letto_attesa = self.lineEdit_d_letto_attesa.text()
#		toro = self.lineEdit_toro.text()
#		spessore = self.lineEdit_spessore.text()
#		larghezza = self.lineEdit_larghezza.text()
#		lunghezza = self.lineEdit_lunghezza.text()
#		h = self.lineEdit_h.text()



		if EC.data_is_empty(str(self.comboBox_sito.currentText())) == 0:
			QMessageBox.warning(self, "ATTENZIONE", "Campo Contesto-Provenienza. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
			test = 1

		if EC.data_is_empty(str(self.lineEdit_num_inv.text())) == 0:
			QMessageBox.warning(self, "ATTENZIONE", "Campo Scheda numero. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
			test = 1

		if nr_inv != "":
			if EC.data_is_int(nr_inv) == 0:
				QMessageBox.warning(self, "ATTENZIONE", "Campo Numero inventario\nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
				test = 1


#		if d_letto_posa != "":
#			if EC.data_is_int(d_letto_posa) == 0:
#				QMessageBox.warning(self, "ATTENZIONE", "D (letto posa).\nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
#				test = 1

#		if d_letto_attesa != "":
#			if EC.data_is_int(d_letto_attesa) == 0:
#				QMessageBox.warning(self, "ATTENZIONE", "Campo d (letto attesa)\nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
#				test = 1

#		if toro != "":
#			if EC.data_is_int(toro) == 0:
#				QMessageBox.warning(self, "ATTENZIONE", "Campo Toro.\nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
#				test = 1

#		if spessore != "":
#			if EC.data_is_int(spessore) == 0:
#				QMessageBox.warning(self, "ATTENZIONE", "Campo Spessore.\nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
#				test = 1

#		if larghezza != "":
#			if EC.data_is_int(larghezza) == 0:
#				QMessageBox.warning(self, "ATTENZIONE", "Campo Larghezza.\nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
#				test = 1

#		if lunghezza != "":
#			if EC.data_is_int(lunghezza) == 0:
#				QMessageBox.warning(self, "ATTENZIONE", "Campo Lunghezza.\nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
#				test = 1

#		if h != "":
#			if EC.data_is_int(h) == 0:
#				QMessageBox.warning(self, "ATTENZIONE", "Campo h. \nIl valore deve essere di tipo numerico",  QMessageBox.Ok)
#				test = 1

		return test


	def insert_new_rec(self):
		##bibliografia
		bibliografia = self.table2dict("self.tableWidget_bibliografia")


		try:
			if self.lineEdit_d_letto_posa.text() == "":
				d_letto_posa = None
			else:
				d_letto_posa = float(self.lineEdit_d_letto_posa.text())

			if self.lineEdit_d_letto_attesa.text() == "":
				d_letto_attesa = None
			else:
				d_letto_attesa = float(self.lineEdit_d_letto_attesa.text())

			if self.lineEdit_toro.text() == "":
				toro = None
			else:
				toro = float(self.lineEdit_toro.text())

			if self.lineEdit_spessore.text() == "":
				spessore = None
			else:
				spessore = float(self.lineEdit_spessore.text())

			if self.lineEdit_larghezza.text() == "":
				larghezza = None
			else:
				larghezza = float(self.lineEdit_larghezza.text())

			if self.lineEdit_lunghezza.text() == "":
				lunghezza = None
			else:
				lunghezza = float(self.lineEdit_lunghezza.text())

			if self.lineEdit_h.text() == "":
				h = None
			else:
				h = float(self.lineEdit_h.text())


			data = self.DB_MANAGER.insert_values_Lapidei(
			self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1, 			#0 - IDsito
						str(self.comboBox_sito.currentText()), 													#1 - Sito
						int(self.lineEdit_num_inv.text()),														#2 - num_inv
						str(self.lineEdit_collocazione.text()), 											#3 - tipo_reperto
						str(self.comboBox_oggetto.currentText()),									#4 - criterio
						str(self.comboBox_tipologia.currentText()), 											#5 - definizione
						str(self.comboBox_materiale.currentText()),								#6 - descrizione
						d_letto_posa,										#12 - stato di conservazione
						d_letto_attesa,													#13 - datazione reperto
						toro,
						spessore,
						larghezza,
						lunghezza,
						h,
						str(self.textEdit_descrizione.toPlainText()),
						str(self.textEdit_lavorazione_e_stato_di_conservazione.toPlainText()),												#11 - luogo conservazione
						str(self.textEdit_confronti.toPlainText()),
						str(self.lineEdit_cronologia.text()), 											#5 - definizione
						str(bibliografia),
						str(self.lineEdit_compilatore.text()),										#16 - rif biblio
						)


			try:
				self.DB_MANAGER.insert_data_session(data)
				return 1
			except Exception as e:
				e_str = str(e)
				if e_str.__contains__("Integrity"):
					msg = self.ID_TABLE + " gia' presente nel database"
				else:
					msg = e
				QMessageBox.warning(self, "Errore", "immisione 1 \n"+ str(msg),  QMessageBox.Ok)
				return 0

			finally:
				pass

		except Exception as e:
			QMessageBox.warning(self, "Errore", "Errore di immisione 2 \n"+str(e),  QMessageBox.Ok)
			return 0



	#insert new row into tableWidget
	#bibliografia
	def on_pushButton_insert_row_bibliografia_pressed(self):
		self.insert_new_row('self.tableWidget_bibliografia')
	def on_pushButton_remove_row_bibliografia_pressed(self):
		self.remove_row('self.tableWidget_bibliografia')

	def check_record_state(self):
		ec = self.data_error_check()
		if ec == 1:
			return 1 #ci sono errori di immissione
		elif self.records_equal_check() == 1 and ec == 0:
			self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
			#self.charge_records() incasina lo stato trova
			return 0 #non ci sono errori di immissione

	def on_pushButton_view_all_2_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
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
##			if self.toolButtonPreviewMedia.isChecked() == True:
##				self.loadMediaPreview(1)

	#records surf functions
	def on_pushButton_first_rec_pressed(self):
		if self.check_record_state() == 1:
##			if self.toolButtonPreviewMedia.isChecked() == True:
				self.loadMediaPreview(1)
		else:
			try:
				self.empty_fields()
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
				self.fill_fields(0)
				self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
			except Exception as e:
				QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
##				if self.toolButtonPreviewMedia.isChecked() == True:
##					self.loadMediaPreview(0)
#se si decidesse di aggiungere if self toolButtonPreviewMedia si metterà prima di except

	def on_pushButton_last_rec_pressed(self):
		if self.check_record_state() == 1:
##			if self.toolButtonPreviewMedia.isChecked() == True:
				self.loadMediaPreview(0)		
		else:

			try:
				self.empty_fields()
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
				self.fill_fields(self.REC_CORR)
				self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
			except Exception as e:
				QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
##				if self.toolButtonPreviewMedia.isChecked() == True:
##					self.loadMediaPreview(0)


	def on_pushButton_prev_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
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
##					if self.toolButtonPreviewMedia.isChecked() == True:
##						self.loadMediaPreview(0)


	def on_pushButton_next_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
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
##					if self.toolButtonPreviewMedia.isChecked() == True:
##						self.loadMediaPreview(0)


	def on_pushButton_delete_pressed(self):
		msg = QMessageBox.warning(self,"Attenzione!!!","Vuoi veramente eliminare il record? \n L'azione è irreversibile", QMessageBox.Cancel,1)
		if msg != 1:
			QMessageBox.warning(self,"Messagio!!!","Azione Annullata!")
		else:
			try:
				id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
				self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
				self.charge_records() #charge records from DB
				QMessageBox.warning(self,"Messaggio!!!","Record eliminato!")
			except Exception as e:
				QMessageBox.warning(self,"Messaggio!!!","Tipo di errore: "+str(e))
			if bool(self.DATA_LIST) == False:
				QMessageBox.warning(self, "Attenzione", "Il database è vuoto!",  QMessageBox.Ok)
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

				self.BROWSE_STATUS = "b"
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
				self.charge_list()
				self.fill_fields()
		self.SORT_STATUS = "n"
		self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

	def on_pushButton_new_search_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			self.enable_button_search(0)

			#set the GUI for a new search


			if self.BROWSE_STATUS != "f":
				self.BROWSE_STATUS = "f"
				###
				self.setComboBoxEditable(['self.comboBox_sito'], 1)
				self.setComboBoxEnable(['self.comboBox_sito'], 'True')
				self.setlineEditEnable(['self.lineEdit_num_inv'], 'True') #verificare
				self.settextEditEnable(["self.textEdit_descrizione"],"False") #verificare
				self.setTableEnable(["self.tableWidget_bibliografia"], "False")
				###
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.set_rec_counter('','')
				self.label_sort.setText(self.SORTED_ITEMS["n"])
				self.charge_list()
				self.empty_fields()

	def on_pushButton_search_go_pressed(self):
		check_for_buttons = 0
		if self.BROWSE_STATUS != "f":
			QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",  QMessageBox.Ok)
		else:
			##scavato
			if self.lineEdit_num_inv.text() != "":
				scheda_numero = int(self.lineEdit_num_inv.text())
			else:
				scheda_numero = ""

			if self.lineEdit_d_letto_posa.text() != "":
				d_letto_posa = int(self.lineEdit_d_letto_posa.text())
			else:
				d_letto_posa = ""

			if self.lineEdit_d_letto_attesa.text() != "":
				d_letto_attesa = int(self.lineEdit_d_letto_attesa.text())
			else:
				d_letto_attesa = ""

			if self.lineEdit_toro.text() != "":
				toro = int(self.lineEdit_toro.text())
			else:
				toro = ""

			if self.lineEdit_spessore.text() != "":
				spessore = int(self.lineEdit_spessore.text())
			else:
				spessore = ""

			if self.lineEdit_larghezza.text() != "":
				larghezza = int(self.lineEdit_larghezza.text())
			else:
				larghezza = ""

			if self.lineEdit_lunghezza.text() != "":
				lunghezza = int(self.lineEdit_lunghezza.text())
			else:
				lunghezza = ""

			if self.lineEdit_h.text() != "":
				h = int(self.lineEdit_h.text())
			else:
				h = ""


			search_dict = {
			self.TABLE_FIELDS[0] : "'"+str(self.comboBox_sito.currentText())+"'",
			self.TABLE_FIELDS[1] : scheda_numero,
			self.TABLE_FIELDS[2] : "'" + str(self.lineEdit_collocazione.text()) + "'",
			self.TABLE_FIELDS[3] : "'" + str(self.comboBox_oggetto.currentText()) + "'",
			self.TABLE_FIELDS[4] : "'" + str(self.comboBox_tipologia.currentText()) + "'",
			self.TABLE_FIELDS[5] : "'" + str(self.textEdit_materiale.text()) + "'",
			self.TABLE_FIELDS[6] : d_letto_posa,
			self.TABLE_FIELDS[7] : d_letto_attesa,
			self.TABLE_FIELDS[8] : toro,
			self.TABLE_FIELDS[9] : spessore,
			self.TABLE_FIELDS[10] : larghezza,
			self.TABLE_FIELDS[11] : lunghezza,
			self.TABLE_FIELDS[12] : h,
			self.TABLE_FIELDS[13] : "'" + str(self.textEdit_descrizione.text()) + "'",
			self.TABLE_FIELDS[14] : "'" + str(self.lineEdit_lavorazione_e_stato_di_conservazione.text()) + "'",
			self.TABLE_FIELDS[15] : "'" + str(self.lineEdit_confronti.text()) + "'",
			self.TABLE_FIELDS[16] : "'" + str(self.lineEdit_cronologia.text()) + "'",
			self.TABLE_FIELDS[17] : "'" + str(self.lineEdit_bibliografia.text()) + "'",
			self.TABLE_FIELDS[18] : "'" + str(self.lineEdit_compilatore.text()) + "'",
			}

			u = Utility()
			search_dict = u.remove_empty_items_fr_dict(search_dict)

			if bool(search_dict) == False:
				QMessageBox.warning(self, "ATTENZIONE", "Non e' stata impostata alcuna ricerca!!!",  QMessageBox.Ok)
				
			else:
				self.SEARCH_DICT_TEMP = search_dict
				res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
				if bool(res) == False:
					QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!",  QMessageBox.Ok)
					
					self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
					self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

					self.fill_fields(self.REC_CORR)

					self.BROWSE_STATUS = "b"
					self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

					self.setComboBoxEditable(["self.comboBox_sito"],1)
					self.setComboBoxEnable(["self.comboBox_sito"],"False")
					self.setlineEditEnable(["self.lineEdit_num_inv"],"False")
					self.settextEditEnable(["self.textEdit_descrizione"],"True")
					self.setTableEnable(["self.tableWidget_bibliografia"], "True")
					check_for_buttons = 1

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
					else:
						strings = ("Sono stati trovati", self.REC_TOT, "records")

					self.setComboBoxEditable(["self.comboBox_sito"],1)
					self.setlineEditEnable(['self.lineEdit_num_inv'], "False")
					self.setComboBoxEnable(['self.comboBox_sito'], "False")
					self.setTableEnable(["self.tableWidget_bibliografia"], "True")
					check_for_buttons = 1

					QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
		
		if check_for_buttons == 1:
			self.enable_button_search(1)

	def update_if(self, msg):
		rec_corr = self.REC_CORR
		self.msg = msg
		if self.msg == 1:
			test = self.update_record()
			if test == 1:
				id_list = []
				for i in self.DATA_LIST:
					id_list.append(eval("i."+ self.ID_TABLE))
				self.DATA_LIST = []
				if self.SORT_STATUS == "n":
					temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE) #self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
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
				return 1
			elif test == 0:
				return 0

	def update_record(self):
		try:
			self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, 
						self.ID_TABLE,
						[eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE+")")],
						self.TABLE_FIELDS,
						self.rec_toupdate())
			return 1
		except Exception as e:
			QMessageBox.warning(self, "Messaggio", "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Se chiudete ora la scheda senza correggere gli errori perderete i dati. Fare una copia di tutto su un foglio word a parte. Errore :" + str(e), QMessageBox.Ok)
			return 0

	def rec_toupdate(self):
		rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
		#rec_to_update = rec_to_update[:2]
		return rec_to_update

	#custom functions
######old system
##	def charge_records(self):
##		self.DATA_LIST = []
##		id_list = []
##		for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
##			id_list.append(eval("i."+ self.ID_TABLE))
##
##		temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE)
##		for i in temp_data_list:
##			self.DATA_LIST.append(i)


	def charge_records(self):
		self.DATA_LIST = []

		if self.DB_SERVER == 'sqlite':
			for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
				self.DATA_LIST.append(i)
		else:
			id_list = []
			for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
				id_list.append(eval("i."+ self.ID_TABLE))

			temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE)
			for i in temp_data_list:
				self.DATA_LIST.append(i)


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

		#for i in range(len(self.data_list)):
			#self.insert_new_row(self.table_name)

		for row in range(len(self.data_list)):
			cmd = ('%s.insertRow(%s)') % (self.table_name, row)
			eval(cmd)
			for col in range(len(self.data_list[row])):
				#item = self.comboBox_sito.setEditText(self.data_list[0][col]
				item = QTableWidgetItem(str(self.data_list[row][col]))
				exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name,row,col)
				eval(exec_str)


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


	def empty_fields(self):
		bibliografia_row_count = self.tableWidget_bibliografia.rowCount()


		self.comboBox_sito.setEditText("") 							#1 - Sito
		self.lineEdit_num_inv.clear()								#2 - num_inv
		self.lineEdit_collocazione.clear()  						#3 - collocazione
		self.comboBox_oggetto.setEditText("") 						#4 - oggetto
		self.comboBox_tipologia.setEditText("") 					#5 - tipologia
		self.comboBox_materiale.setEditText("")						#9 - materiale
		self.lineEdit_d_letto_posa.clear()							#6 - d_letto_posa
		self.lineEdit_d_letto_attesa.clear()						#7 - d_letto_attesa
		self.lineEdit_toro.clear()									#8 - toro
		self.lineEdit_spessore.clear()								#10 - spessore
		self.lineEdit_larghezza.clear()								#11 - larghezza
		self.lineEdit_lunghezza.clear()								#13 - lunghezza
		self.lineEdit_h.clear()										#14 - h
		self.textEdit_descrizione.clear() 							#12 - descrizione
		self.textEdit_lavorazione_e_stato_di_conservazione.clear()	#15 - lavorazione e stato...
		self.textEdit_confronti.clear()								#16 - confronti
		self.lineEdit_cronologia.clear()							#17 - cronologia
		self.lineEdit_compilatore.clear()							#18 - compilatore


		for i in range(bibliografia_row_count):
			self.tableWidget_bibliografia.removeRow(0)
		self.insert_new_row("self.tableWidget_bibliografia")		#19- bibliografia


	def fill_fields(self, n=0):
		self.rec_num = n
		#QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
		try:
			str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito)) 						#1 - Sito
			self.lineEdit_num_inv.setText(str(self.DATA_LIST[self.rec_num].scheda_numero))						#2 - scheda numero
			str(self.comboBox_tipologia.setEditText(self.DATA_LIST[self.rec_num].tipologia))				#3 - tipologia
			str(self.comboBox_materiale.setEditText(self.DATA_LIST[self.rec_num].materiale))				#4 - materiale
			str(self.comboBox_oggetto.setEditText(self.DATA_LIST[self.rec_num].oggetto))					#5 - oggetto
			str(self.textEdit_descrizione.setText(self.DATA_LIST[self.rec_num].descrizione))				#6 - descrizione
			str(self.textEdit_lavorazione_e_stato_di_conservazione.setText(self.DATA_LIST[self.rec_num].lavorazione_e_stato_di_conservazione))				#6 - descrizione
			self.lineEdit_collocazione.setText(str(self.DATA_LIST[self.rec_num].collocazione))						#2 - scheda numero
			self.lineEdit_compilatore.setText(str(self.DATA_LIST[self.rec_num].compilatore))						#2 - scheda numero
			str(self.textEdit_confronti.setText(self.DATA_LIST[self.rec_num].confronti))				#6 - descrizione
			self.lineEdit_cronologia.setText(str(self.DATA_LIST[self.rec_num].cronologia))						#2 - scheda numero


			self.tableInsertData("self.tableWidget_bibliografia", self.DATA_LIST[self.rec_num].bibliografia)	#8 - bibliografia

			if self.DATA_LIST[self.rec_num].d_letto_posa == None:												#9 - d_letto_posa
				self.lineEdit_d_letto_posa.setText("")
			else:
				self.lineEdit_d_letto_posa.setText(str(self.DATA_LIST[self.rec_num].d_letto_posa))

			if self.DATA_LIST[self.rec_num].d_letto_attesa == None:											#10 - d_letto_attesa
				self.lineEdit_d_letto_attesa.setText("")
			else:
				self.lineEdit_d_letto_attesa.setText(str(self.DATA_LIST[self.rec_num].d_letto_attesa))

			if self.DATA_LIST[self.rec_num].toro == None:															#11 - toro
				self.lineEdit_toro.setText("")
			else:
				self.lineEdit_toro.setText(str(self.DATA_LIST[self.rec_num].toro))

			if self.DATA_LIST[self.rec_num].spessore == None:															#12 - spessore
				self.lineEdit_spessore.setText("")
			else:
				self.lineEdit_spessore.setText(str(self.DATA_LIST[self.rec_num].spessore))

			if self.DATA_LIST[self.rec_num].larghezza == None:															#13 - larghezza
				self.lineEdit_larghezza.setText("")
			else:
				self.lineEdit_larghezza.setText(str(self.DATA_LIST[self.rec_num].larghezza))

			if self.DATA_LIST[self.rec_num].lunghezza == None:															#14 - lunghezza
				self.lineEdit_lunghezza.setText("")
			else:
				self.lineEdit_lunghezza.setText(str(self.DATA_LIST[self.rec_num].lunghezza))

			if self.DATA_LIST[self.rec_num].h == None:															#15 - h
				self.lineEdit_h.setText("")
			else:
				self.lineEdit_h.setText(str(self.DATA_LIST[self.rec_num].h))

##########
		except Exception as e:
			QMessageBox.warning(self, "Errore Fill Fields", str(e),  QMessageBox.Ok)

	def set_rec_counter(self, t, c):
		self.rec_tot = t
		self.rec_corr = c
		self.label_rec_tot.setText(str(self.rec_tot))
		self.label_rec_corrente.setText(str(self.rec_corr))

	def set_LIST_REC_TEMP(self):
		#TableWidget

		#bibliografia
		bibliografia = self.table2dict("self.tableWidget_bibliografia")
		
		
		##Dimensioni
		if self.lineEdit_d_letto_posa.text() == "":
			d_letto_posa = None
		else:
			d_letto_posa = self.lineEdit_d_letto_posa.text()

		if self.lineEdit_d_letto_attesa.text() == "":
			d_letto_attesa = None
		else:
			d_letto_attesa = self.lineEdit_d_letto_attesa.text()
	
		if self.lineEdit_toro.text() == "":
			toro = None
		else:
			toro = self.lineEdit_toro.text()

		if self.lineEdit_spessore.text() == "":
			spessore = None
		else:
			spessore = self.lineEdit_spessore.text()

		if self.lineEdit_larghezza.text() == "":
			larghezza = None
		else:
			larghezza = self.lineEdit_larghezza.text()

		if self.lineEdit_lunghezza.text() == "":
			lunghezza = None
		else:
			lunghezza = self.lineEdit_lunghezza.text()

		if self.lineEdit_h.text() == "":
			h = None
		else:
			h = self.lineEdit_h.text()

		#data
		self.DATA_LIST_REC_TEMP = [
		str(self.comboBox_sito.currentText()), 								#1 - Sito
		str(self.lineEdit_num_inv.text()), 									#2 - num_inv
		str(self.lineEdit_collocazione.text()), 								#3 - collocazione
		str(self.comboBox_oggetto.currentText()),								#4 - oggetto
		str(self.comboBox_tipologia.currentText()), 							#5 - tipologia
		str(self.comboBox_materiale.currentText()), 							#6 - materiale
		str(d_letto_posa),														#8 - d_letto_posa
		str(d_letto_attesa),													#9 - d_letto_attesa
		str(toro),																#10 - toro
		str(spessore),															#11 - spessore
		str(larghezza),															#12 - larghezza
		str(lunghezza),															#13 - lunghezza
		str(h),																	#14 - h
		str(self.textEdit_descrizione.toPlainText()),							#15 - descrizione
		str(self.textEdit_lavorazione_e_stato_di_conservazione.toPlainText()),	#16 - lavorazione
		str(self.textEdit_confronti.toPlainText()),							#17 - confronti
		str(self.lineEdit_cronologia.text()),									#18 - cronologia
		str(bibliografia),														#19 - bibliografia
		str(self.lineEdit_compilatore.text()),									#20 - compilatore
		]


	def enable_button(self, n):
		self.pushButton_connect.setEnabled(n)

		self.pushButton_new_rec.setEnabled(n)

		self.pushButton_view_all_2.setEnabled(n)

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

		self.pushButton_view_all_2.setEnabled(n)

		self.pushButton_first_rec.setEnabled(n)

		self.pushButton_last_rec.setEnabled(n)

		self.pushButton_prev_rec.setEnabled(n)

		self.pushButton_next_rec.setEnabled(n)

		self.pushButton_delete.setEnabled(n)

		self.pushButton_save.setEnabled(n)

		self.pushButton_sort.setEnabled(n)


	def setTableEnable(self, t, v):
		tab_names = t
		value = v

		for tn in tab_names:
			cmd = ('%s%s%s%s') % (tn, '.setEnabled(', v, ')')
			eval(cmd)


	def set_LIST_REC_CORR(self):
		self.DATA_LIST_REC_CORR = []
		for i in self.TABLE_FIELDS:
			self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

	def records_equal_check(self):
		self.set_LIST_REC_TEMP()
		self.set_LIST_REC_CORR()
		
		#test
		
		#QMessageBox.warning(self, "ATTENZIONE", str(self.DATA_LIST_REC_CORR) + " temp " + str(self.DATA_LIST_REC_TEMP), QMessageBox.Ok)

		check_str = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)

		if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
			return 0
		else:
			return 1




	def testing(self, name_file, message):
		f = open(str(name_file), 'w')
		f.write(str(message))
		f.close()



if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = pyarchinit_scheda_Lapidei()
	ui.show()
	sys.exit(app.exec_())
