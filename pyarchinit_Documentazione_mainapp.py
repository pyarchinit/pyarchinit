#! /usr/bin/env python
#-*- coding: utf-8 -*-
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

from  pyarchinit_db_manager import *

from datetime import date
from psycopg2 import *

#--import pyArchInit modules--#
from  pyarchinit_documentazione_ui import Ui_DialogDocumentazione_tipo_doc
from  pyarchinit_documentazione_ui import *
from  pyarchinit_utility import *
from  pyarchinit_error_check import *
#buttare
from  pyarchinit_exp_Documentazionesheet_pdf import *
#buttare

from  pyarchinit_pyqgis import Pyarchinit_pyqgis
from  sortpanelmain import SortPanelMain

from pyarchinit_documentazione_preview_mainapp import pyarchinit_doc_preview

#from  pyarchinit_exp_Campsheet_pdf import *

##from 

class pyarchinit_Documentazione(QDialog, Ui_DialogDocumentazione_tipo_doc):
	MSG_BOX_TITLE = "PyArchInit - pyarchinit_version 0.4 - Scheda Documentazione"
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
	TABLE_NAME = 'documentazione_table'
	MAPPER_TABLE_CLASS = "DOCUMENTAZIONE"
	NOME_SCHEDA = "Scheda Documentazione"
	ID_TABLE = "id_documentazione"
	CONVERSION_DICT = {
	ID_TABLE:ID_TABLE, 
	"Sito":"sito",
	"Nome documentazione":"nome_doc",
	"Data":"data",
	"Tipo documentazione":"tipo_documentazione",
	"Sorgente":"sorgente",
	"Scala":"scala",
	"Disegnatore":"disegnatore",
	"Note":"note",
	}

	SORT_ITEMS = [
				ID_TABLE,
				"Sito",
				"Nome documentazione",
				"Data",
				"Tipo documentazione",
				"Sorgente",
				"Scala",
				"Disegnatore",
				"Note",
				]

	TABLE_FIELDS = [
				"sito",
				"nome_doc",
				"data",
				"tipo_documentazione",
				"sorgente",
				"scala",
				"disegnatore",
				"note",
				]

	DB_SERVER = "not defined" ####nuovo sistema sort


	def __init__(self, iface):
		self.iface = iface
		self.pyQGIS = Pyarchinit_pyqgis(self.iface)
		QDialog.__init__(self)
		self.setupUi(self)
		self.currentLayerId = None
		try:
			self.on_pushButton_connect_pressed()
		except Exception as e:
			QMessageBox.warning(self, "Sistema di connessione", str(e),  QMessageBox.Ok)

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
		from pyarchinit_conn_strings import *
		conn = Connection()
		conn_str = conn.conn_str()
		test_conn = conn_str.find('sqlite')
		if test_conn == 0:
			self.DB_SERVER = "sqlite"
		try:
			self.DB_MANAGER = Pyarchinit_db_management(conn_str)
			self.DB_MANAGER.connection()
			self.charge_records() #charge records from DB
			#check if DB is empty
			if bool(self.DATA_LIST) == True:
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
				self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
				self.BROWSE_STATUS = 'b'
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
				QMessageBox.warning(self, "Alert", "La connessione e' fallita <br><br> Tabella non presente. E' NECESSARIO RIAVVIARE QGIS" + str(e) ,  QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Alert", "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e) ,  QMessageBox.Ok)

####################################

	def charge_list(self):
		sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

		try:
			sito_vl.remove('')
		except:
			pass
		self.comboBox_sito_doc.clear()
		sito_vl.sort()
		self.comboBox_sito_doc.addItems(sito_vl)

###################################


	#buttons functions
	def generate_list_pdf(self):
		data_list = []
		for i in range(len(self.DATA_LIST)):

			sito =  str(self.DATA_LIST[i].sito)
			tipo_doc = str(self.DATA_LIST[i].tipo_documentazione)
			nome_doc = str(self.DATA_LIST[i].nome_doc)
			note = str(self.DATA_LIST[i].note)

			res_us_doc = self.DB_MANAGER.select_us_doc_from_db_sql(sito, tipo_doc, nome_doc)

			res_usneg_doc = self.DB_MANAGER.select_usneg_doc_from_db_sql(sito, tipo_doc, nome_doc)

			elenco_us_doc = []
			elenco_usneg_doc = []

			if bool(res_us_doc) == True:
				for sing_rec in res_us_doc:
					tup_area_us = (int(sing_rec[1]),int(sing_rec[3]))
					elenco_us_doc.append(tup_area_us)

			if bool(res_usneg_doc) == True:
				for sing_rec in res_usneg_doc:
					tup_area_usneg = (int(sing_rec[2]),int(sing_rec[3]))
					elenco_usneg_doc.append(tup_area_usneg)

			elenco_us_pdf = elenco_us_doc+elenco_usneg_doc

			string_to_pdf = ""

			if bool(elenco_us_pdf) == True:

				elenco_us_pdf.sort()

				area_corr = str(elenco_us_pdf[0][0])
				us_elenco = ""

				string_to_pdf = ""

				for rec_us in range(len(elenco_us_pdf)):
					if area_corr == str(elenco_us_pdf[rec_us][0]):
						us_elenco += str(elenco_us_pdf[rec_us][1]) + ", "
					else:
						if string_to_pdf == "":
							string_to_pdf = "Area " + area_corr + ": "+ us_elenco[:-2]
							area_corr = str(elenco_us_pdf[rec_us][0])
							us_elenco = str(elenco_us_pdf[rec_us][1]) + ", " 
						else:
							string_to_pdf += "<br/>Area " + area_corr + ": "+ us_elenco[:-2]
							area_corr = str(elenco_us_pdf[rec_us][0])
							us_elenco = str(elenco_us_pdf[rec_us][1]) + ", " 

				string_to_pdf += "<br/>Area " + area_corr + ": "+ us_elenco[:-2]
			else:
				pass

			data_list.append([
			str(self.DATA_LIST[i].sito), 								#1 - Sito
			str(self.DATA_LIST[i].nome_doc),						#2 - Area
			str(self.DATA_LIST[i].data),								#4 - definizione stratigrafica
			str(self.DATA_LIST[i].tipo_documentazione),			#5 - definizione intepretata
			str(self.DATA_LIST[i].sorgente),							#6 - descrizione
			str(self.DATA_LIST[i].scala),								#7 - interpretazione
			str(self.DATA_LIST[i].disegnatore),						#8 - periodo iniziale
			str(self.DATA_LIST[i].note),								#9 - fase iniziale
			note])

		return data_list


	def on_pushButton_disegno_doc_pressed(self):
		sing_layer = [self.DATA_LIST[self.REC_CORR]]
		self.pyQGIS.charge_vector_layers_doc(sing_layer)

	def on_pushButton_exp_scheda_doc_pressed(self):
		single_Documentazione_pdf_sheet = generate_documentazione_pdf()
		data_list = self.generate_list_pdf()
		single_Documentazione_pdf_sheet.build_Documentazione_sheets(data_list)


	def on_pushButton_exp_elenco_doc_pressed(self):
		Documentazione_index_pdf = generate_documentazione_pdf()
		data_list = self.generate_list_pdf()
		Documentazione_index_pdf.build_index_Documentazione(data_list, data_list[0][0])

	def on_pushButtonPreview_pressed(self):
		#sing_layer =self.DATA_LIST[self.REC_CORR]

		docstr = (' \"%s\"=\'%s\' AND \"%s\"=\'%s\' AND \"%s\"=\'%s\' ')  % ('sito',
																											str(self.DATA_LIST[self.REC_CORR].sito),
																											'nome_doc',
																											str(self.DATA_LIST[self.REC_CORR].nome_doc),
																											'tipo_doc',
																											str(self.DATA_LIST[self.REC_CORR].tipo_documentazione))

		QMessageBox.warning(self, "query", str(docstr),  QMessageBox.Ok)

		dlg = pyarchinit_doc_preview(self, docstr)

		dlg.exec_()


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

	def on_pushButton_new_rec_pressed(self):
		if bool(self.DATA_LIST) == True:
			if self.data_error_check() == 1:
				pass
			else:
				if self.BROWSE_STATUS == "b":
					if bool(self.DATA_LIST) == True:
						if self.records_equal_check() == 1:
							msg = self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))


##########################################


		#set the GUI for a new record
		if self.BROWSE_STATUS != "n":
			self.BROWSE_STATUS = "n"
			self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
			self.empty_fields()
			self.label_sort.setText(self.SORTED_ITEMS["n"])

			self.setComboBoxEditable(["self.comboBox_sito_doc"],1)
			self.setComboBoxEnable(["self.comboBox_sito_doc"],"True")
			self.setComboBoxEnable(["self.comboBox_tipo_doc"], "True")
			self.setComboBoxEnable(["self.lineEdit_nome_doc"],"True")

			self.set_rec_counter('', '')
			self.enable_button(0)


###########################################



	def on_pushButton_save_pressed(self):
		#save record
		if self.BROWSE_STATUS == "b":
			if self.data_error_check() == 0:
				if self.records_equal_check() == 1:
					self.update_if(QMessageBox.warning(self,'ATTENZIONE',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
					self.label_sort.setText(self.SORTED_ITEMS["n"])
					self.enable_button(1)
					self.fill_fields(self.REC_CORR)
				else:
					QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",  QMessageBox.Ok)
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
					self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)

##################################################

					self.setComboBoxEditable(["self.comboBox_sito_doc"],1)
					self.setComboBoxEnable(["self.comboBox_sito_doc"],"False")
					self.setComboBoxEnable(["self.comboBox_tipo_doc"], "False")
					self.setComboBoxEnable(["self.lineEdit_nome_doc"],"False")

					self.fill_fields(self.REC_CORR)
					self.enable_button(1)
				else:
					pass

##################################################

	def data_error_check(self):
		test = 0
		EC = Error_check()

		if EC.data_is_empty(str(self.comboBox_sito_doc.currentText())) == 0:
			QMessageBox.warning(self, "ATTENZIONE", "Campo Sito. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
			test = 1

		if EC.data_is_empty(str(self.comboBox_tipo_doc.currentText())) == 0:
			QMessageBox.warning(self, "ATTENZIONE", "Campo Tipo documentazione \n Il campo non deve essere vuoto",  QMessageBox.Ok)
			test = 1

		if EC.data_is_empty(str(self.lineEdit_nome_doc.text())) == 0:
			QMessageBox.warning(self, "ATTENZIONE", "Campo Nome documentazione \n Il campo non deve essere vuoto",  QMessageBox.Ok)
			test = 1


		return test

	def insert_new_rec(self):
		try:
##			if self.lineEdit_nr_campione.text() == "":
##				nr_campione = None
##			else:
##				nr_campione = int(self.lineEdit_nr_campione.text())
##
##			if self.lineEdit_us.text() == "":
##				us = None
##			else:
##				us = int(self.lineEdit_us.text())
##
##			if self.lineEdit_cassa.text() == "":
##				nr_cassa = None
##			else:
##				nr_cassa = int(self.lineEdit_cassa.text())
##
##			if self.lineEdit_n_inv_mat.text() == "":
##				numero_inventario_materiale = None
##			else:
##				numero_inventario_materiale = int(self.lineEdit_n_inv_mat.text())

			data = self.DB_MANAGER.insert_values_documentazione(
			self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
			str(self.comboBox_sito_doc.currentText()), 						#1 - Sito
			str(self.lineEdit_nome_doc.text()),									#2 - Nome Documentazione
			str(self.lineEdit_data_doc.text()),										#3 - Data
			str(self.comboBox_tipo_doc.currentText()),						#4 - Tipo Documentazione
			str(self.comboBox_sorgente_doc.currentText()),					#5 - Sorgente
			str(self.comboBox_scala_doc.currentText()),						#6 - Scala
			str(self.lineEdit_disegnatore_doc.text()),								#7 - Disegnatore
			str(self.textEdit_note_doc.toPlainText()))							#8 - Note

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

	def check_record_state(self):
		ec = self.data_error_check()
		if ec == 1:
			return 1 #ci sono errori di immissione
		elif self.records_equal_check() == 1 and ec == 0:
			self.update_if(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
			#self.charge_records() incasina lo stato trova
			return 0 #non ci sono errori di immissione

	def on_pushButton_view_all_pressed(self):
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




##	def on_pushButton_disegno_doc_pressed(self):
##		"""
##		for sing_us in range(len(self.DATA_LIST)):
##			sing_layer = [self.DATA_LIST[sing_us]]
##			self.pyQGIS.charge_vector_layers(sing_layer)
##		"""
##
##		sing_layer = [self.DATA_LIST[self.REC_CORR]]
##		self.pyQGIS.charge_vector_layers_doc(sing_layer)



	#records surf functions
	def on_pushButton_first_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			try:
				self.empty_fields()
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
				self.fill_fields(0)
				self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
			except Exception as e:
				QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

	def on_pushButton_last_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			try:
				self.empty_fields()
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
				self.fill_fields(self.REC_CORR)
				self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
			except Exception as e:
				QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

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

	def on_pushButton_delete_pressed(self):
		msg = QMessageBox.warning(self,"Attenzione!!!","Vuoi veramente eliminare il record? \n L'azione è irreversibile", QMessageBox.Cancel,1)
		if msg != 1:
			QMessageBox.warning(self,"Messaggio!!!","Azione Annullata!")
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

################################################

			#set the GUI for a new search
			if self.BROWSE_STATUS != "f":
				self.BROWSE_STATUS = "f"
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.setComboBoxEnable(["self.comboBox_sito_doc"],"True")
				self.setComboBoxEnable(["self.lineEdit_nome_doc"],"True")
				self.setComboBoxEnable(["self.comboBox_tipo_doc"],"True")
				self.setComboBoxEnable(["self.textEdit_note_doc"],"False")
				self.setComboBoxEditable(["self.comboBox_sito_doc"],1)
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.set_rec_counter('','')
				self.label_sort.setText(self.SORTED_ITEMS["n"])
				self.charge_list()
				self.empty_fields()

################################################


	def on_pushButton_search_go_pressed(self):
		if self.BROWSE_STATUS != "f":
			QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",  QMessageBox.Ok)
		else:

##			if self.lineEdit_nr_campione.text() == "":
##				nr_campione = None
##			else:
##				nr_campione = int(self.lineEdit_nr_campione.text())
##
##			if self.lineEdit_us.text() == "":
##				us = None
##			else:
##				us = int(self.lineEdit_us.text())
##
##			if self.lineEdit_cassa.text() == "":
##				nr_cassa = None
##			else:
##				nr_cassa = int(self.lineEdit_cassa.text())
##
##			if self.lineEdit_n_inv_mat.text() == "":
##				numero_inventario_materiale = None
##			else:
##				numero_inventario_materiale = int(self.lineEdit_n_inv_mat.text())

			search_dict = {
			self.TABLE_FIELDS[0] : "'"+str(self.comboBox_sito_doc.currentText())+"'",				#1 - Sito
			self.TABLE_FIELDS[1] : "'"+str(self.lineEdit_nome_doc.text())+"'" , 					#2 - Nome Documentazione
			self.TABLE_FIELDS[2] : "'"+str(self.lineEdit_data_doc.text())+"'" ,					#3 - Data
			self.TABLE_FIELDS[3] : "'"+str(self.comboBox_tipo_doc.currentText())+"'", 				#4 - Tipo Documentazione
			self.TABLE_FIELDS[4] : "'"+str(self.comboBox_sorgente_doc.currentText())+"'",			#5 - Sorgente
			self.TABLE_FIELDS[5] : "'"+str(self.comboBox_scala_doc.currentText())+"'",				#6 - Scala
			self.TABLE_FIELDS[6] : "'"+str(self.lineEdit_disegnatore_doc.text())+"'"				#7 - Disegnatore
			}

			u = Utility()
			search_dict = u.remove_empty_items_fr_dict(search_dict)

			if bool(search_dict) == False:
				QMessageBox.warning(self, "ATTENZIONE", "Non e' stata impostata alcuna ricerca!!!",  QMessageBox.Ok)
			else:
				res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
				if bool(res) == False:
					QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!",  QMessageBox.Ok)

					self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
					self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

					self.fill_fields(self.REC_CORR)
					self.BROWSE_STATUS = "b"
					self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

					self.setComboBoxEnable(["self.comboBox_sito_doc"],"False")
					self.setComboBoxEnable(["self.lineEdit_nome_doc"],"False")
					self.setComboBoxEnable(["self.comboBox_tipo_doc"],"False")
					self.setComboBoxEnable(["self.textEdit_note_doc"],"True")
					self.setComboBoxEditable(["self.comboBox_sito_doc"],1)

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

					self.setComboBoxEnable(["self.comboBox_sito_doc"],"False")
					self.setComboBoxEnable(["self.lineEdit_nome_doc"],"False")
					self.setComboBoxEnable(["self.comboBox_tipo_doc"],"False")
					self.setComboBoxEnable(["self.textEdit_note_doc"],"True")
					self.setComboBoxEditable(["self.comboBox_sito_doc"],1)

					QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)

		self.enable_button_search(1)


	def on_pushButton_test_pressed(self):
		pass
##		data = "Sito: " + str(self.comboBox_sito.currentText())
##
##		test = Test_area(data)
##		test.run_test()
##
##	def on_pushButton_draw_pressed(self):
##		self.pyQGIS.charge_layers_for_draw(["1", "2", "3", "4", "5", "7", "8", "9", "10", "12"])
##
##
##	def on_pushButton_sites_geometry_pressed(self):
##		sito = unicode(self.comboBox_sito.currentText())
##		self.pyQGIS.charge_sites_geometry(["1", "2", "3", "4", "8"], "sito", sito)

##	def on_pushButton_rel_pdf_pressed(self):
##		check=QMessageBox.warning(self, "Attention", "Under testing: this method can contains some bugs. Do you want proceed?", QMessageBox.Cancel,1)
##		if check == 1:
##			erp = exp_rel_pdf(unicode(self.comboBox_sito.currentText()))
##			erp.export_rel_pdf()

#********************************************************************************

##	def on_pushButton_elenco_casse_pressed(self):
##		if self.records_equal_check() == 1:
##			self.update_if(QMessageBox.warning(self,'Errore',u"Il record è stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
##
##		sito_ec = unicode(self.comboBox_sito.currentText())
##		Mat_casse_pdf = generate_reperti_pdf()
##		data_list = self.generate_el_casse_pdf(sito_ec)
##
##		Mat_casse_pdf.build_index_Casse(data_list, sito_ec)
##		Mat_casse_pdf.build_box_labels_Finds(data_list, sito_ec)

#********************************************************************************

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


	#custom functions
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
		self.comboBox_sito_doc.setEditText("")				#1 - Sito
		self.lineEdit_nome_doc.clear()						#2 - Nome Dcumentazione
		self.lineEdit_data_doc.clear()						#3 - Data
		self.comboBox_tipo_doc.setEditText("")						#4 - Tipo Documentazione
		self.comboBox_sorgente_doc.setEditText("")					#5 - Sorgente
		self.comboBox_scala_doc.setEditText("")						#6 - Scala
		self.lineEdit_disegnatore_doc.clear()				#7 - Dsegnatore
		self.textEdit_note_doc.clear()						#8 - Note

	def fill_fields(self, n=0):
		self.rec_num = n
##		if str(self.DATA_LIST[self.rec_num].nr_campione) == 'None':
##			numero_campione = ''
##		else:
##			numero_campione = str(self.DATA_LIST[self.rec_num].nr_campione)
##
##		if str(self.DATA_LIST[self.rec_num].us) == 'None':
##			us = ''
##		else:
##			us = str(self.DATA_LIST[self.rec_num].us)
##
##		if str(self.DATA_LIST[self.rec_num].numero_inventario_materiale) == 'None':
##			numero_inventario_materiale = ''
##		else:
##			numero_inventario_materiale = str(self.DATA_LIST[self.rec_num].numero_inventario_materiale)
##
##		if str(self.DATA_LIST[self.rec_num].nr_cassa) == 'None':
##			nr_cassa = ''
##		else:
##			nr_cassa = str(self.DATA_LIST[self.rec_num].nr_cassa)


		str(self.comboBox_sito_doc.setEditText(self.DATA_LIST[self.rec_num].sito))										#1 - Sito
		str(self.lineEdit_nome_doc.setText(self.DATA_LIST[self.rec_num].nome_doc))										#2 - Nome Dcumentazione
		str(self.lineEdit_data_doc.setText(self.DATA_LIST[self.rec_num].data))												#3 - Data
		str(self.comboBox_tipo_doc.setEditText(self.DATA_LIST[self.rec_num].tipo_documentazione))				#4 - Tipo Documentazione
		str(self.comboBox_sorgente_doc.setEditText(self.DATA_LIST[self.rec_num].sorgente))							#5 - Sorgente
		str(self.comboBox_scala_doc.setEditText(self.DATA_LIST[self.rec_num].scala))									#6 - Scala
		str(self.lineEdit_disegnatore_doc.setText(self.DATA_LIST[self.rec_num].disegnatore))							#7 - Dsegnatore
		str(self.textEdit_note_doc.setText(self.DATA_LIST[self.rec_num].note))												#8 - Note


	def set_rec_counter(self, t, c):
		self.rec_tot = t
		self.rec_corr = c
		self.label_rec_tot.setText(str(self.rec_tot))
		self.label_rec_corrente.setText(str(self.rec_corr))

	def set_LIST_REC_TEMP(self):

##		if self.lineEdit_nr_campione.text() == "":
##			nr_campione = None
##		else:
##			nr_campione = int(self.lineEdit_nr_campione.text())
##
##		if self.lineEdit_us.text() == "":
##			us = None
##		else:
##			us = int(self.lineEdit_us.text())
##
##		if self.lineEdit_cassa.text() == "":
##			nr_cassa = None
##		else:
##			nr_cassa = int(self.lineEdit_cassa.text())
##
##		if self.lineEdit_n_inv_mat.text() == "":
##			numero_inventario_materiale = None
##		else:
##			numero_inventario_materiale = int(self.lineEdit_n_inv_mat.text())

		#data
		self.DATA_LIST_REC_TEMP = [
		str(self.comboBox_sito_doc.currentText()), 						#1 - Sito
		str(self.lineEdit_nome_doc.text()), 					#2 - Nome Documentazione
		str(self.lineEdit_data_doc.text()), 				#3 - Data
		str(self.comboBox_tipo_doc.currentText()), 					#4 - Tipo Documentazione
		str(self.comboBox_sorgente_doc.currentText()),					#5 - Sorgente
		str(self.comboBox_scala_doc.currentText()),					#6 - Scala
		str(self.lineEdit_disegnatore_doc.text()),						#7 - Disegnatore
		str(self.textEdit_note_doc.toPlainText())								#8 - Note
		]


	def set_LIST_REC_CORR(self):
		self.DATA_LIST_REC_CORR = []
		for i in self.TABLE_FIELDS:
			self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

	def setComboBoxEnable(self, f, v):
		field_names = f
		value = v

		for fn in field_names:
			cmd = ('%s%s%s%s') % (fn, '.setEnabled(', v, ')')
			eval(cmd)


	def setComboBoxEditable(self, f, n):
		field_names = f
		value = n

		for fn in field_names:
			cmd = ('%s%s%d%s') % (fn, '.setEditable(', n, ')')
			eval(cmd)

	def rec_toupdate(self):
		rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
		return rec_to_update

	def records_equal_check(self):
		self.set_LIST_REC_TEMP()
		self.set_LIST_REC_CORR()

		if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
			return 0
		else:
			return 1

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

	def testing(self, name_file, message):
		f = open(str(name_file), 'w')
		f.write(str(message))
		f.close()


## Class end

if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = pyarchinit_US()
	ui.show()
	sys.exit(app.exec_())
