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

import os
import sys
from datetime import date
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QInputDialog, QComboBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

import pandas as pd

from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.sortpanelmain import SortPanelMain
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from qgis.PyQt.QtCore import QTimer
from ..modules.db.concurrency_manager import ConcurrencyManager, RecordLockIndicator
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
# MyApp is imported lazily in contenuto to avoid pydantic/openai conflicts on Windows
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_exp_Periodizzazionesheet_pdf import generate_Periodizzazione_pdf

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Periodizzazione.ui'))


class pyarchinit_Periodizzazione(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Periodizzazione"
    elif L=='en':
        MSG_BOX_TITLE = "PyArchInit - Periodization Form"
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Formular Period"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}

    if L=='de':
        STATUS_ITEMS = {"b": "Aktuell ", "f": "Finden", "n": "Neuer Rekord"}
    
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    if L=='de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'periodizzazione_table'
    MAPPER_TABLE_CLASS = "PERIODIZZAZIONE"
    NOME_SCHEDA = "Scheda Periodizzazione"
    ID_TABLE = "id_perfas"
    if L=='it': 
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Periodo": "periodo",
            "Fase": "fase",
            "Cronologia iniziale": "cron_iniziale",
            "Cronologia finale": "cron_finale",
            "Descrizione": "descrizione",
            "Datazione estesa": "datazione_estesa",
            "Codice periodo": "cont_per",
            #"Area": "area"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Periodo",
            "Fase",
            "Descrizione",
            "Cronologia iniziale",
            "Cronologia finale",
            "Codice periodo",
            #"Area"
        ]
    elif L=='de':   
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Ausgrabungsstätte": "sito",
            "Period": "periodo",
            "Phase": "fase",
            "Anfangschronologie": "cron_iniziale",
            "Letzte Chronologie": "cron_finale",
            "Beschreibung": "descrizione",
            "Erweiterte Datierung": "datazione_estesa",
            "Periodencode erstellen": "cont_per"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Ausgrabungsstätte",
            "Period",
            "Phase",
            "Anfangschronologie",
            "Letzte Chronologie",
            "Beschreibung",
            "Erweiterte Datierung",
            "Periodencode erstellen"
        ]
    else:   
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Period": "periodo",
            "Phase": "fase",
            "Start chronology": "cron_iniziale",
            "Final chronology": "cron_finale",
            "Description": "descrizione",
            "Letteral datation": "datazione_estesa",
            "Perion code": "cont_per"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Period",
            "Phase",
            "Start chronology",
            "Final chronology",
            "Description",
            "Letteral datation",
            "Perion code"
        ]   
    TABLE_FIELDS = [
        'sito',
        'periodo',
        'fase',
        'cron_iniziale',
        'cron_finale',
        'descrizione',
        'datazione_estesa',
        'cont_per',
        #'area'
    ]

    DB_SERVER = "not defined"  ####nuovo sistema sort
    HOME = os.environ['PYARCHINIT_HOME']
    BIN = '{}{}{}'.format(HOME, os.sep, "bin")
    CSV=os.path.join(BIN,'epoche_storiche.csv')
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
        self.fill_fields()
        self.set_sito()
        self.msg_sito()
        self.read_epoche()
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
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)

            # Get database username and set it in the concurrency manager
            user_info = conn.datauser()
            db_username = user_info.get('user', 'unknown')
            if hasattr(self, 'concurrency_manager'):
                self.concurrency_manager.set_username(db_username)

            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                #self.charge_list()
                self.charge_list()
                self.fill_fields()
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.StandardButton.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "individuel formular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.StandardButton.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "individual form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.StandardButton.Ok)
                self.charge_list()
                #self.charge_list()
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

    def read_epoche(self):
        try:
            # Memorizza il valore corrente del comboBox
            current_value = self.comboBox_per_estesa.currentText()

            # Leggi il file CSV con il formato corretto
            df = pd.read_csv(self.CSV,
                             quotechar='"',  # Usa le virgolette doppie per le stringhe
                             encoding='utf-8',
                             skipinitialspace=True)  # Salta gli spazi iniziali

            # Debug: stampa le informazioni sul DataFrame
            print("Colonne nel DataFrame:", df.columns.tolist())
            print("\nPrime righe del DataFrame:")
            print(df.head())

            # Estrai l'epoca e gli anni dal dataframe
            epoche = df['Periodo'].tolist()
            evento = df['Evento'].tolist()
            anni = df['Anno/Secolo'].tolist()

            # Elabora gli anni
            anni_inizio = []
            anni_fine = []

            for anno_originale in anni:
                try:
                    # Mantieni l'anno originale per il display
                    anno = anno_originale.strip()

                    # Funzione helper per estrarre un numero da una stringa con marcatori
                    def estrai_numero(anno_str):
                        # Rimuovi spazi e converti in minuscolo per il controllo
                        anno_lower = anno_str.lower()

                        # Controlla se è a.C. (avanti Cristo)
                        if 'a.c.' in anno_lower or 'ac' in anno_lower or 'bce' in anno_lower:
                            # Rimuovi tutti i marcatori di a.C. per estrarre il numero
                            numero = anno_str
                            for marker in ['a.C.', 'a.c.', 'A.C.', 'aC', 'ac', 'AC', 'BCE', 'bce']:
                                numero = numero.replace(marker, '')
                            numero = numero.strip()
                            return -int(numero)

                        # Controlla se è d.C. (dopo Cristo)
                        elif 'd.c.' in anno_lower or 'dc' in anno_lower or 'ce' in anno_lower:
                            # Rimuovi tutti i marcatori di d.C. per estrarre il numero
                            numero = anno_str
                            for marker in ['d.C.', 'd.c.', 'D.C.', 'dC', 'dc', 'DC', 'CE', 'ce']:
                                numero = numero.replace(marker, '')
                            numero = numero.strip()
                            return int(numero)

                        # Se non ha marcatori, assumiamo sia d.C. (dopo Cristo)
                        else:
                            # Estrai solo i numeri
                            numero = ''.join(filter(str.isdigit, anno_str))
                            if numero:
                                return int(numero)
                            else:
                                raise ValueError(f"Nessun numero trovato in: {anno_str}")

                    # Funzione per processare un intervallo con slash (es: 1930/1950)
                    def processa_intervallo_slash(intervallo_str):
                        if '/' in intervallo_str:
                            parti = intervallo_str.split('/')
                            # Estrai il primo e l'ultimo numero
                            primo = estrai_numero(parti[0].strip())
                            ultimo = estrai_numero(parti[-1].strip())
                            return primo, ultimo
                        else:
                            # Se non c'è slash, il valore è sia inizio che fine
                            valore = estrai_numero(intervallo_str)
                            return valore, valore

                    # Cerca il trattino come separatore principale
                    if '-' in anno:
                        # Gestisci con attenzione i numeri negativi (date a.C.)
                        # Se c'è "a.C." o "BCE", potrebbero esserci numeri negativi
                        if any(marker in anno.lower() for marker in ['a.c.', 'ac', 'bce']):
                            # Usa regex per trovare il trattino separatore
                            import re
                            # Cerca un trattino che non sia all'inizio e che separi due parti
                            match = re.search(r'(.+?)\s*-\s*(.+)', anno)
                            if match:
                                prima_parte = match.group(1).strip()
                                seconda_parte = match.group(2).strip()
                            else:
                                parti = anno.split('-', 1)
                                prima_parte = parti[0].strip() if len(parti) > 0 else ""
                                seconda_parte = parti[1].strip() if len(parti) > 1 else ""
                        else:
                            # Se non ci sono date a.C., dividi normalmente
                            parti = anno.split('-', 1)
                            prima_parte = parti[0].strip() if len(parti) > 0 else ""
                            seconda_parte = parti[1].strip() if len(parti) > 1 else ""

                        # Processa la prima parte
                        primo_inizio, primo_fine = processa_intervallo_slash(prima_parte)

                        # Processa la seconda parte
                        secondo_inizio, secondo_fine = processa_intervallo_slash(seconda_parte)

                        # Per l'intervallo complessivo usa:
                        # - Il primo valore della prima parte come inizio
                        # - L'ultimo valore della seconda parte come fine
                        anno_inizio = primo_inizio
                        anno_fine = secondo_fine

                    else:
                        # Se non c'è trattino, potrebbe essere solo uno slash o un singolo anno
                        primo, ultimo = processa_intervallo_slash(anno)
                        anno_inizio = primo
                        anno_fine = ultimo

                    # Se l'intera stringa termina con a.C./BCE, applica a entrambi i valori
                    if any(marker in anno.lower() for marker in ['a.c.', 'ac', 'bce']):
                        if any(anno.lower().rstrip().endswith(marker) for marker in ['a.c.', 'ac', 'bce']):
                            if anno_inizio > 0:
                                anno_inizio = -abs(anno_inizio)
                            if anno_fine > 0:
                                anno_fine = -abs(anno_fine)

                    anni_inizio.append(anno_inizio)
                    anni_fine.append(anno_fine)

                    print(f"Processato: '{anno}' -> valori interni: {anno_inizio} a {anno_fine}")

                except ValueError as e:
                    print(f'Errore nella conversione dell\'anno "{anno_originale}": {str(e)}')
                    anni_inizio.append(0)
                    anni_fine.append(0)
                except Exception as e:
                    print(f'Errore generico per l\'anno "{anno_originale}": {str(e)}')
                    import traceback
                    traceback.print_exc()
                    anni_inizio.append(0)
                    anni_fine.append(0)

            # Formatta le epoche per il comboBox
            # USA L'ANNO ORIGINALE NEL DISPLAY, NON I VALORI ESTRATTI
            formatted_epoche = []
            for epoca, evento, anno_display, anno_inizio, anno_fine in zip(epoche, evento, anni, anni_inizio, anni_fine):
                # Mantieni il formato originale dell'anno nel display
                f = f'{epoca} - {evento} ({anno_display})'
                formatted_epoche.append(f)
                if self.comboBox_per_estesa.findText(f) == -1:
                    # Salva i valori numerici come dati associati per uso interno
                    self.comboBox_per_estesa.addItem(f, (anno_inizio, anno_fine))

            # Connetti il segnale di cambiamento
            try:
                self.comboBox_per_estesa.currentIndexChanged.disconnect(self.update_anni)
            except TypeError:
                pass  # Ignora se non era connesso
            self.comboBox_per_estesa.currentIndexChanged.connect(self.update_anni)

            # Ripristina il valore precedente se possibile
            if current_value in formatted_epoche:
                self.comboBox_per_estesa.setCurrentText(current_value)

        except Exception as e:
            print(f"Errore nella lettura del file CSV: {str(e)}")
            import traceback
            traceback.print_exc()

            # Prova a leggere e stampare il contenuto grezzo del file per debug
            try:
                with open(self.CSV, 'r', encoding='utf-8') as f:
                    print("\nContenuto grezzo del file CSV:")
                    print(f.read())
            except Exception as read_error:
                print(f"Errore nella lettura grezza del file: {str(read_error)}")


    def update_anni(self, index):
        # Quando l'indice della combo box cambia, imposta i valori delle line edit
        if index >= 0:  # -1 indica nessuna selezione
            anni = self.comboBox_per_estesa.itemData(index)  # Ottieni gli anni associati all'elemento selezionato
            self.lineEdit_cron_iniz.setText(str(anni[0]))
            self.lineEdit_cron_fin.setText(str(anni[1]))


    def contenuto(self, b):
        """Get content suggestions from GPT with lazy import to avoid pydantic conflicts."""
        try:
            # Lazy import to avoid loading openai/pydantic at plugin startup
            from ..modules.utility.askgpt import MyApp
        except ImportError as e:
            error_msg = str(e)
            if 'pydantic' in error_msg.lower() or 'openai' in error_msg.lower():
                QMessageBox.warning(
                    self,
                    "GPT Feature Unavailable",
                    "The GPT suggestion feature cannot be loaded due to a pydantic/openai library conflict.\n\n"
                    "This is a known issue with incompatible versions of pydantic and pydantic_core.\n\n"
                    "Possible solutions:\n"
                    "1. Update pydantic: python -m pip install --upgrade pydantic pydantic-core\n"
                    "2. Reinstall openai: python -m pip uninstall openai -y && python -m pip install openai\n\n"
                    "The rest of the plugin will continue to work normally.",
                    QMessageBox.StandardButton.Ok
                )
            else:
                QMessageBox.warning(
                    self,
                    "Import Error",
                    f"Cannot load GPT feature:\n\n{error_msg}",
                    QMessageBox.StandardButton.Ok
                )
            return ""
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"An unexpected error occurred:\n\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
            return ""

        models = ["gpt-4o", "gpt-4"]  # Replace with actual model names
        combo = QComboBox()
        combo.addItems(models)
        selected_model, ok = QInputDialog.getItem(self, "Select Model", "Choose a model for GPT:", models, 0,
                                                  False)

        if ok and selected_model:
            text = MyApp.ask_gpt(self,
                                 f'forniscimi una descrizione e 3 link wikipidia riguardo a questo contenuto {b}, tenendo presente che il contesto è archeologico',
                                 self.apikey_gpt(),selected_model)
            #url_pattern = r"(https?:\/\/\S+)"
            #urls = re.findall(url_pattern, text)
            return text#, urls
        return ""

    def handleComboActivated(self, index):
        selected_text = self.comboBox_per_estesa.itemText(index)
        generate_text = self.contenuto(selected_text)
        reply = QMessageBox.information(self, 'Info', generate_text, QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Ok:
            self.textEdit_descrizione_per.setText(generate_text)

    def on_suggerimenti_pressed(self):
        s = self.contenuto(self.comboBox_per_estesa.currentText())
        generate_text = s
        QMessageBox.information(self, 'info', str(generate_text), QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if QMessageBox.StandardButton.Ok:
            self.textEdit_descrizione_per.setText(str(generate_text))

        else:
            pass


    def apikey_gpt(self):
        #HOME = os.environ['PYARCHINIT_HOME']
        BIN = '{}{}{}'.format(self.HOME, os.sep, "bin")
        api_key = ""
        # Verifica se il file gpt_api_key.txt esiste
        path_key = os.path.join(BIN, 'gpt_api_key.txt')
        if os.path.exists(path_key):

            # Leggi l'API Key dal file
            with open(path_key, 'r') as f:
                api_key = f.read().strip()
                try:

                    return api_key

                except:
                    reply = QMessageBox.question(None, 'Warning', 'Apikey non valida' + '\n'
                                                 + 'Clicca ok per inserire la chiave',
                                                 QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                    if reply == QMessageBox.StandardButton.Ok:

                        api_key, ok = QInputDialog.getText(None, 'Apikey gpt', 'Inserisci apikey valida:')
                        if ok:
                            # Salva la nuova API Key nel file
                            with open(path_key, 'w') as f:
                                f.write(api_key)
                                f.close()
                            with open(path_key, 'r') as f:
                                api_key = f.read().strip()
                    else:
                        return api_key


        else:
            # Chiedi all'utente di inserire una nuova API Key
            api_key, ok = QInputDialog.getText(None, 'Apikey gpt', 'Inserisci apikey:')
            if ok:
                # Salva la nuova API Key nel file
                with open(path_key, 'w') as f:
                    f.write(api_key)
                    f.close()
                with open(path_key, 'r') as f:
                    api_key = f.read().strip()

        return api_key

    def charge_list_sito(self):

        pass

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
        #self.model_a.database().close()
        conn = Connection()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
            
            if self.L=='it':
                QMessageBox.information(self, "OK" ,"Sei connesso al sito: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok) 
        
            elif self.L=='de':
                QMessageBox.information(self, "OK", "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok) 
                
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),QMessageBox.StandardButton.Ok)     
        
        elif sito_set_str=='':    
            if self.L=='it':
                msg = QMessageBox.information(self, "Attenzione" ,"Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per  vedere tutti i record",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            elif self.L=='de':
                msg = QMessageBox.information(self, "Achtung", "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            else:
                msg = QMessageBox.information(self, "Warning" , "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) 
            if msg == QMessageBox.StandardButton.Cancel:
                pass
            else: 
                dlg = pyArchInitDialog_Config(self)
                dlg.charge_list()
                dlg.exec()
    def set_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        try:
            if bool(sito_set_str):
                search_dict = {'sito': "'" + str(sito_set_str) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                self.DATA_LIST = []
                for i in res:
                    self.DATA_LIST.append(i)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0

                # Check if we have results before accessing DATA_LIST[0]
                if len(self.DATA_LIST) == 0:
                    if self.L == 'it':
                        QMessageBox.information(self, "Attenzione", f"Il sito '{sito_set_str}' non ha record in questa scheda. Crea un nuovo record o disattiva la 'scelta sito' dalla configurazione.", QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.information(self, "Warnung", f"Die Fundstelle '{sito_set_str}' hat keine Datensätze. Erstellen Sie einen neuen Datensatz oder deaktivieren Sie die 'Site-Wahl'.", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Warning", f"Site '{sito_set_str}' has no records in this tab. Create a new record or disable 'site choice' from configuration.", QMessageBox.StandardButton.Ok)
                    return

                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.SORT_STATUS = "n"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
            else:
                pass
        except Exception as e:
            if self.L == 'it':
                QMessageBox.warning(self, "Errore", f"Errore nel caricamento del sito '{sito_set_str}':\n{str(e)}", QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Fundstelle '{sito_set_str}':\n{str(e)}", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Error", f"Error loading site '{sito_set_str}':\n{str(e)}", QMessageBox.StandardButton.Ok)  
    def on_pushButton_pdf_scheda_exp_pressed(self):
        if self.L=='it':    
            Periodizzazione_pdf_sheet = generate_Periodizzazione_pdf()
            data_list = self.generate_list_pdf()
            Periodizzazione_pdf_sheet.build_Periodizzazione_sheets(
                data_list)
        elif self.L=='de':  
            Periodizzazione_pdf_sheet = generate_Periodizzazione_pdf()
            data_list = self.generate_list_pdf()
            Periodizzazione_pdf_sheet.build_Periodizzazione_sheets_de(
                data_list)
        else:   
            Periodizzazione_pdf_sheet = generate_Periodizzazione_pdf()
            data_list = self.generate_list_pdf()
            Periodizzazione_pdf_sheet.build_Periodizzazione_sheets_en(
                data_list)      
    def on_pushButton_pdf_lista_exp_pressed(self):
        if self.L=='it':    
            Periodizzazione_pdf_list = generate_Periodizzazione_pdf()
            data_list = self.generate_list_pdf()
            Periodizzazione_pdf_list.build_index_Periodizzazione(data_list, data_list[0][
                0])
        
        elif self.L=='de':  
            Periodizzazione_pdf_list = generate_Periodizzazione_pdf()
            data_list = self.generate_list_pdf()
            Periodizzazione_pdf_list.build_index_Periodizzazione_de(data_list, data_list[0][
                0])
                
        else:   
            Periodizzazione_pdf_list = generate_Periodizzazione_pdf()
            data_list = self.generate_list_pdf()
            Periodizzazione_pdf_list.build_index_Periodizzazione_en(data_list, data_list[0][
                0])     
        # codice per l'esportazione sperimentale dei PDF #
        """
        dlg = pyarchinit_PDFAdministrator()
        dlg.set_table_name(self.TABLE_NAME)
        dlg.connect()
        msg = QMessageBox.warning(self,'ATTENZIONE',"Vuoi creare un nuovo layout PFD?", QMessageBox.Cancel,1)
        dlg.connect()
        ##      dlg.on_pushButton_connect_pressed()
        if msg == 1:
            dlg.on_pushButton_new_rec_pressed()
            dlg.charge_list()

        id_list = []

        for i in self.DATA_LIST:
            id_list.append(getattr(i, self.ID_TABLE))
        dlg.add_id_list(id_list)

        dlg.exec()
        """

    def generate_list_pdf(self):
        # periodo = ""
        # fase = ""
        # cron_iniz = ""
        # cron_fin = ""

        data_list = []
        for i in range(len(self.DATA_LIST)):

            if not self.DATA_LIST[i].periodo:
                periodo = ""
            else:
                periodo = str(self.DATA_LIST[i].periodo)

            if not self.DATA_LIST[i].fase:
                fase = ""
            else:
                fase = str(self.DATA_LIST[i].fase)

            if not self.DATA_LIST[i].cron_iniziale:
                cron_iniz = ""
            else:
                cron_iniz = str(self.DATA_LIST[i].cron_iniziale)

            if not self.DATA_LIST[i].cron_finale:
                cron_fin = ""
            else:
                cron_fin = str(self.DATA_LIST[i].cron_finale)

            data_list.append([
                str(self.DATA_LIST[i].sito.replace('_',' ')),  # 1 - Sito
                str(periodo),  # 2 - periodo
                str(fase),  # 3 - fase
                str(cron_iniz),  # 4 - cron iniz
                str(cron_fin),  # 5 - cron fin
                str(self.DATA_LIST[i].datazione_estesa),  # 6 - datazione_estesa
                str(self.DATA_LIST[i].descrizione)  # 7 - descrizione
            ])
        return data_list

        # buttons functions

    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(getattr(i, self.ID_TABLE))
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

    def on_pushButton_new_rec_pressed(self):
        conn = Connection()
        
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
                        if self.records_equal_check() == 1:
                            if self.L=='it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            elif self.L=='de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                                                                   
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "The record has been changed. Do you want to save the changes?",
                                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))

        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
            
                self.BROWSE_STATUS = "n"

                ###

                #self.setComboBoxEditable(["self.comboBox_sito"], 0)
                self.setComboBoxEditable(["self.comboBox_periodo"], 1)
                self.setComboBoxEditable(["self.comboBox_fase"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.setComboBoxEnable(["self.comboBox_periodo"], "True")
                self.setComboBoxEnable(["self.comboBox_fase"], "True")

                ###
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields_nosite()

            else:
                self.BROWSE_STATUS = "n"

                ###

                self.setComboBoxEditable(["self.comboBox_sito"], 0)
                self.setComboBoxEditable(["self.comboBox_periodo"], 1)
                self.setComboBoxEditable(["self.comboBox_fase"], 1)
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.setComboBoxEnable(["self.comboBox_periodo"], "True")
                self.setComboBoxEnable(["self.comboBox_fase"], "True")

                ###
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields()
            
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            
                    # Check for version conflicts before updating
                    if hasattr(self, 'current_record_version') and self.current_record_version:
                        conflict = self.concurrency_manager.check_version_conflict(
                            'periodizzazione_table',
                            self.editing_record_id,
                            self.current_record_version,
                            self.DB_MANAGER
                        )

                        if conflict and conflict['has_conflict']:
                            # Handle the conflict
                            record_data = self.fill_record()
                            if self.concurrency_manager.handle_conflict(
                                'periodizzazione_table',
                                record_data,
                                conflict
                            ):
                                # User chose to reload - refresh the form
                                self.charge_records()
                                self.fill_fields(self.REC_CORR)
                                return
                            # Otherwise continue with save (user chose to overwrite)

                    if self.data_error_check() == 0:
                            if self.records_equal_check() == 1:
                                if self.L=='it':
                                    self.update_if(QMessageBox.warning(self, 'Errore',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche?",QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                                elif self.L=='de':
                                    self.update_if(QMessageBox.warning(self, 'Error',
                                                           "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                                                           
                                else:
                                    self.update_if(QMessageBox.warning(self, 'Error',
                                                           "The record has been changed. Do you want to save the changes?",
                                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                                self.SORT_STATUS = "n"
                                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                                self.enable_button(1)
                                self.fill_fields(self.REC_CORR)
                            else:
                                if self.L=='it':
                                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.", QMessageBox.StandardButton.Ok)
                                elif self.L=='de':
                                    QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen", QMessageBox.StandardButton.Ok)
                                else:
                                    QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.StandardButton.Ok)
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
                    self.setComboBoxEditable(["self.comboBox_periodo"], 1)
                    self.setComboBoxEditable(["self.comboBox_fase"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_periodo"], "False")
                    self.setComboBoxEnable(["self.comboBox_fase"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
            else:
                pass#QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati", QMessageBox.Ok)

    def data_error_check(self):
        test = 0
        EC = Error_check()

        # Controlli solo per i campi obbligatori
        sito = self.comboBox_sito.currentText()
        periodo = self.comboBox_periodo.currentText()
        fase = self.comboBox_fase.currentText()

        if self.L=='it':
            # Controlli campi obbligatori
            if sito == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1

            if periodo == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Periodo obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(periodo) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Periodo. \n Il valore deve essere di tipo numerico",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if fase == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Fase obbligatorio!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(fase) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Fase. \n Il valore deve essere di tipo numerico",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            # Controlli campi opzionali (solo se compilati)
            data_estesa = self.comboBox_per_estesa.currentText()
            if data_estesa != "":
                if EC.data_lenght(data_estesa, 299) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Datazione estesa. \n non deve superare i 300 caratteri alfanumerici",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cron_iniz = self.lineEdit_cron_iniz.text()
            if cron_iniz != "":
                if EC.data_is_int(cron_iniz) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Cronologia Iniziale. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cron_fin = self.lineEdit_cron_fin.text()
            if cron_fin != "":
                if EC.data_is_int(cron_fin) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Cronologia Finale. \n Il valore deve essere di tipo numerico",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cod_per = self.lineEdit_codice_periodo.text()
            if cod_per != "":
                if EC.data_is_int(cod_per) == 0:
                    QMessageBox.warning(self, "ATTENZIONE",
                                        "Campo Codice Periodo \n Il valore deve essere di tipo numerico", QMessageBox.StandardButton.Ok)
                    test = 1

            return test

        elif self.L=='de':
            # Controlli campi obbligatori
            if sito == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Ausgrabungsstätte erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1

            if periodo == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Period erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(periodo) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld period \n Der Wert muss numerisch eingegeben werden",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if fase == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Phase erforderlich!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(fase) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Phase \n Der Wert muss numerisch eingegeben werden",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            # Controlli campi opzionali (solo se compilati)
            data_estesa = self.comboBox_per_estesa.currentText()
            if data_estesa != "":
                if EC.data_lenght(data_estesa, 299) == 0:
                    QMessageBox.warning(self, "ACHTUNG",
                                        "Erweitertes Dating-Feld. \n darf 300 alphanumerische Zeichen nicht überschreiten",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cron_iniz = self.lineEdit_cron_iniz.text()
            if cron_iniz != "":
                if EC.data_is_int(cron_iniz) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Anfangschronologie \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cron_fin = self.lineEdit_cron_fin.text()
            if cron_fin != "":
                if EC.data_is_int(cron_fin) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld Letzte Chronologie \n Der Wert muss numerisch eingegeben werden",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cod_per = self.lineEdit_codice_periodo.text()
            if cod_per != "":
                if EC.data_is_int(cod_per) == 0:
                    QMessageBox.warning(self, "ACHTUNG", "Feld periodencode \n Der Wert muss numerisch eingegeben werden", QMessageBox.StandardButton.Ok)
                    test = 1

            return test

        else:
            # Controlli campi obbligatori
            if sito == "":
                QMessageBox.warning(self, "WARNING", "Site field required!", QMessageBox.StandardButton.Ok)
                test = 1

            if periodo == "":
                QMessageBox.warning(self, "WARNING", "Period field required!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(periodo) == 0:
                QMessageBox.warning(self, "WARNING", "Period Field. \n The value must be numerical",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if fase == "":
                QMessageBox.warning(self, "WARNING", "Phase field required!", QMessageBox.StandardButton.Ok)
                test = 1
            elif EC.data_is_int(fase) == 0:
                QMessageBox.warning(self, "WARNING", "Phase Field. \n The value must be numerical",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            # Controlli campi opzionali (solo se compilati)
            data_estesa = self.comboBox_per_estesa.currentText()
            if data_estesa != "":
                if EC.data_lenght(data_estesa, 299) == 0:
                    QMessageBox.warning(self, "WARNING", "Extended Dating Field. \n must not exceed 300 alphanumeric characters",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cron_iniz = self.lineEdit_cron_iniz.text()
            if cron_iniz != "":
                if EC.data_is_int(cron_iniz) == 0:
                    QMessageBox.warning(self, "WARNING", "Start chron. Field. \n The value must be numerical",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cron_fin = self.lineEdit_cron_fin.text()
            if cron_fin != "":
                if EC.data_is_int(cron_fin) == 0:
                    QMessageBox.warning(self, "WARNING", "Final chron. Field. \n The value must be numerical",
                                        QMessageBox.StandardButton.Ok)
                    test = 1

            cod_per = self.lineEdit_codice_periodo.text()
            if cod_per != "":
                if EC.data_is_int(cod_per) == 0:
                    QMessageBox.warning(self, "WARNING", "period code Field. \n The value must be numerical", QMessageBox.StandardButton.Ok)
                    test = 1

            return test
    def insert_new_rec(self):
        try:
            # Campi opzionali - gestione valori vuoti
            if not self.lineEdit_cron_iniz.text():
                cron_iniz = None  # Usa None invece di stringa vuota per NULL nel database
            else:
                cron_iniz = int(self.lineEdit_cron_iniz.text())

            if not self.lineEdit_cron_fin.text():
                cron_fin = None  # Usa None invece di stringa vuota per NULL nel database
            else:
                cron_fin = int(self.lineEdit_cron_fin.text())

            if not self.lineEdit_codice_periodo.text():
                cont_per = None  # Usa None invece di stringa vuota per NULL nel database
            else:
                cont_per = int(self.lineEdit_codice_periodo.text())

            # Gestione datazione estesa opzionale
            if not self.comboBox_per_estesa.currentText():
                datazione_estesa = ""  # Stringa vuota per campo testo
            else:
                datazione_estesa = str(self.comboBox_per_estesa.currentText())

            data = self.DB_MANAGER.insert_periodizzazione_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,  # 0 - max num id
                str(self.comboBox_sito.currentText()),  # 1 - Sito (obbligatorio)
                int(self.comboBox_periodo.currentText()),  # 2 - Periodo (obbligatorio)
                int(self.comboBox_fase.currentText()),  # 3 - Fase (obbligatorio)
                cron_iniz,  # 4 - Cron iniziale (opzionale)
                cron_fin,  # 5 - Cron finale (opzionale)
                str(self.textEdit_descrizione_per.toPlainText()),  # 6 - Descrizione (obbligatorio)
                datazione_estesa,  # 7 - Periodizzazione estesa (opzionale)
                cont_per)  # 8 - Cont_per (opzionale)

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    if self.L=='it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)
                    else:
                        msg = self.ID_TABLE + " exist in db"
                        QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.StandardButton.Ok)
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.StandardButton.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.StandardButton.Ok)
            return 0

    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L=='it':
                self.update_if(
                
                    QMessageBox.warning(self, 'Errore', "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            elif self.L=='de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore', "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            # self.charge_records()
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
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

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
                QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.StandardButton.Ok)        
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                if self.L=='it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.StandardButton.Ok)  
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_delete_pressed(self):
        
        if self.L=='it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio!!!", "Tipo di errore: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "Il database è vuoto!", QMessageBox.StandardButton.Ok)
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
        elif self.L=='de':
            msg = QMessageBox.warning(self, "Achtung!!!",
                                      "Willst du wirklich diesen Eintrag löschen? \n Der Vorgang ist unumkehrbar",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "Die Datenbank ist leer!", QMessageBox.StandardButton.Ok)
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
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Messagio!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()  # charge records from DB
                    QMessageBox.warning(self, "Message!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.StandardButton.Ok)
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
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            conn = Connection()
        
            sito_set= conn.sito_set()
            sito_set_str = sito_set['sito_set']
            

            # set the GUI for a new search

            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText()==sito_set_str:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields_nosite()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])

                    #self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_periodo"], 1)
                    self.setComboBoxEditable(["self.comboBox_fase"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_periodo"], "True")
                    self.setComboBoxEnable(["self.comboBox_fase"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_per"], "False")
                    #self.charge_list()
                else:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_periodo"], 1)
                    self.setComboBoxEditable(["self.comboBox_fase"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "True")
                    self.setComboBoxEnable(["self.comboBox_periodo"], "True")
                    self.setComboBoxEnable(["self.comboBox_fase"], "True")
                    self.setComboBoxEnable(["self.textEdit_descrizione_per"], "False")
                    self.charge_list()

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L=='it':
                QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.StandardButton.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Um eine neue Abfrage zu starten drücke  'new search' ",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.StandardButton.Ok)
        else:
            if self.lineEdit_cron_iniz.text() != "":
                cron_iniziale = "'" + str(self.lineEdit_cron_iniz.text()) + "'"
            else:
                cron_iniziale = ""

            if self.lineEdit_cron_fin.text() != "":
                cron_finale = "'" + str(self.lineEdit_cron_fin.text()) + "'"
            else:
                cron_finale = ""

            if self.comboBox_periodo.currentText() != "":
                periodo = "'" + str(self.comboBox_periodo.currentText()) + "'"
            else:
                periodo = ""

            if self.comboBox_fase.currentText() != "":
                fase = "'" + str(self.comboBox_fase.currentText()) + "'"
            else:
                fase = ""
            # if self.comboBox_area.currentText() != "":
                # area = "'" + str(self.comboBox_area.currentText()) + "'"
            # else:
                # area = ""
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",  # 1 - Sito
                'periodo': periodo,  # 2 - Periodo
                'fase': fase,  # 3 - Fase
                'cron_iniziale': cron_iniziale,  # 4 - Cron iniziale
                'cron_finale': cron_finale,  # 5 - Crion finale
                'descrizione': str(self.textEdit_descrizione_per.toPlainText()),  # 6 - Descrizione
                'datazione_estesa': "'" + str(self.comboBox_per_estesa.currentText()) + "'",  # 7 - Periodizzazione estesa
                'cont_per': "'" + str(self.lineEdit_codice_periodo.text()) + "'",  # 8 - Codice periodo
                #'area' : area
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                if self.L=='it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!", QMessageBox.StandardButton.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.StandardButton.Ok) 
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "kein Eintrag gefunden!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "The record has not been found ", QMessageBox.StandardButton.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_periodo"], 1)
                    self.setComboBoxEditable(["self.comboBox_fase"], 1)

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_periodo"], "False")
                    self.setComboBoxEnable(["self.comboBox_fase"], "False")

                    self.setComboBoxEnable(["self.textEdit_descrizione_per"], "True")

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
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")

                    self.setComboBoxEditable(["self.comboBox_sito"], 1)
                    self.setComboBoxEditable(["self.comboBox_periodo"], 1)
                    self.setComboBoxEditable(["self.comboBox_fase"], 1)
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.setComboBoxEnable(["self.comboBox_periodo"], "False")
                    self.setComboBoxEnable(["self.comboBox_fase"], "False")
                    self.setComboBoxEnable(["self.textEdit_descrizione_per"], "True")

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)

        self.enable_button_search(1)

    def on_pushButton_show_periodo_pressed(self):
        if not self.lineEdit_codice_periodo.text():
            QMessageBox.warning(self, "Message", "Period code not add", QMessageBox.StandardButton.Ok)
        else:
            sito_p = self.comboBox_sito.currentText()
            cont_per = self.lineEdit_codice_periodo.text()
            per_label = self.comboBox_periodo.currentText()
            fas_label = self.comboBox_fase.currentText()
            dat=self.comboBox_per_estesa.currentText()
            self.pyQGIS.charge_vector_layers_periodo(sito_p, int(cont_per), per_label, fas_label,dat)
            self.pyQGIS.charge_vector_usm_layers_periodo(sito_p, int(cont_per), per_label, fas_label,dat)
    def on_pushButton_all_period_pressed(self):
        #self.set_sito()
        if not self.lineEdit_codice_periodo.text():
            QMessageBox.warning(self, "Message", "Period code not add", QMessageBox.StandardButton.Ok)
        else:
            lista=[]
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


                for e in self.DATA_LIST:
                    sito_p = e.sito
                    cont_per = e.cont_per
                    per_label = e.periodo
                    fas_label = e.fase
                    dat=e.datazione_estesa
                    self.pyQGIS.charge_vector_layers_all_period(sito_p, str(cont_per),per_label,fas_label,dat)
                    #self.pyQGIS.charge_vector_layers_usm_all_period(sito_p, str(cont_per),per_label,fas_label,dat)
            except Exception as e:
                print(str(e))    
    
    def on_pushButton_all_period_usm_pressed(self):
        #self.set_sito()
        if not self.lineEdit_codice_periodo.text():
            QMessageBox.warning(self, "Message", "Period code not add", QMessageBox.StandardButton.Ok)
        else:
            lista=[]
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
            
            
                for e in self.DATA_LIST:
                    sito_p = e.sito
                    cont_per = e.cont_per
                    per_label = e.periodo
                    fas_label = e.fase
                    dat=e.datazione_estesa
                    #self.pyQGIS.charge_vector_layers_all_period(sito_p, str(cont_per),per_label,fas_label,dat)
                    self.pyQGIS.charge_vector_layers_usm_all_period(sito_p, str(cont_per),per_label,fas_label,dat)
            except Exception as e:
                print(str(e))    
    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.StandardButton.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(getattr(i, self.ID_TABLE))
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
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                if type(self.REC_CORR) == "<type 'str'>":
                    corr = 0
                else:
                    corr = self.REC_CORR
                return 1
            elif test == 0:
                return 0

                # custom functions

    def charge_records(self):
        self.DATA_LIST = []

        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_list.append(getattr(i, self.ID_TABLE))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)

    def setComboBoxEditable(self, f, n):
        """Set editable state for widgets - uses getattr instead of eval for security"""
        for fn in f:
            widget_name = fn.replace('self.' , '') if fn.startswith('self.' ) else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def table2dict(self, n):
        self.tablename = n
        table = getattr(self, self.tablename.replace("self.", "") if self.tablename.startswith("self.") else self.tablename)
        row = table.rowCount()
        col = table.columnCount()
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = table.item(r, c)
                if bool(value):
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista

    def empty_fields_nosite(self):
        #self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_periodo.setEditText("")  # 2 - Periodo
        self.comboBox_fase.setEditText("")  # 3 - Fase
        self.lineEdit_cron_iniz.clear()  # 4 - Cronologia iniziale
        self.lineEdit_cron_fin.clear()  # 5 - Cronologia finale
        self.comboBox_per_estesa.setEditText("")  # 6 - Datazione estesa
        self.textEdit_descrizione_per.clear()  # 7 - Descrizione
        self.lineEdit_codice_periodo.clear()
        #self.comboBox_area.setEditText("")        # 8 - Codice periodo
    
    def empty_fields(self):
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_periodo.setEditText("")  # 2 - Periodo
        self.comboBox_fase.setEditText("")  # 3 - Fase
        self.lineEdit_cron_iniz.clear()  # 4 - Cronologia iniziale
        self.lineEdit_cron_fin.clear()  # 5 - Cronologia finale
        self.comboBox_per_estesa.setEditText("")  # 6 - Datazione estesa
        self.textEdit_descrizione_per.clear()  # 7 - Descrizione
        self.lineEdit_codice_periodo.clear()
        #self.comboBox_area.setEditText("")        # 8 - Codice periodo

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))  # 1 - Sito

            self.comboBox_periodo.setEditText(str(self.DATA_LIST[self.rec_num].periodo))  # 2 - Periodo
            self.comboBox_fase.setEditText(str(self.DATA_LIST[self.rec_num].fase))  # 3 - Fase

            if not self.DATA_LIST[self.rec_num].cron_iniziale:  # 4 - Cronologia iniziale
                self.lineEdit_cron_iniz.setText("")
            else:
                self.lineEdit_cron_iniz.setText(str(self.DATA_LIST[self.rec_num].cron_iniziale))

            if not self.DATA_LIST[self.rec_num].cron_finale:  # 5 - Cronologia finale
                self.lineEdit_cron_fin.setText("")
            else:
                self.lineEdit_cron_fin.setText(str(self.DATA_LIST[self.rec_num].cron_finale))

            str(self.comboBox_per_estesa.setEditText(self.DATA_LIST[self.rec_num].datazione_estesa))  # 6 - Datazione estesa
            str(self.textEdit_descrizione_per.setText(self.DATA_LIST[self.rec_num].descrizione))  # 7 - Descrizione

            if not self.DATA_LIST[self.rec_num].cont_per:  # 8 - Codice periodo
                self.lineEdit_codice_periodo.setText("")
            else:
                self.lineEdit_codice_periodo.setText(str(self.DATA_LIST[self.rec_num].cont_per))
            #self.comboBox_area.setEditText(str(self.DATA_LIST[self.rec_num].area))
        except :
            pass#QMessageBox.warning(self, "Error Fill Fields", str(e), QMessageBox.Ok)

        # Track version number and record ID for concurrency
        if hasattr(self, 'concurrency_manager'):
            try:
                if n < len(self.DATA_LIST):
                    current_record = self.DATA_LIST[n]
                    if hasattr(current_record, 'version_number'):
                        self.current_record_version = current_record.version_number
                    if hasattr(current_record, 'id_perfass'):
                        self.editing_record_id = getattr(current_record, 'id_perfass')

                    # Update lock indicator
                    if hasattr(current_record, 'editing_by'):
                        self.lock_indicator.update_lock_status(
                            current_record.editing_by,
                            current_record.editing_since if hasattr(current_record, 'editing_since') else None
                        )

                    # Set soft lock for this record
                    if self.editing_record_id:
                        import getpass
                        current_user = getpass.getuser()
                        # self.DB_MANAGER.set_editing_lock(
                        #     'periodizzazione_table',
                        #     self.editing_record_id,
                        #     current_user
                        # )
            except Exception as e:
                QgsMessageLog.logMessage(f"Error setting version tracking: {str(e)}", "PyArchInit", Qgis.Warning)

    def setComboBoxEnable(self, f, v):
        """Set enabled state for widgets"""
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEnabled(v == "True")

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # data
        if not self.lineEdit_cron_iniz.text():
            cron_iniz = ''
        else:
            cron_iniz = str(self.lineEdit_cron_iniz.text())

        if not self.lineEdit_cron_fin.text():
            cron_fin = ''
        else:
            cron_fin = str(self.lineEdit_cron_fin.text())

        if not self.lineEdit_codice_periodo.text():
            cont_per = ''
        else:
            cont_per = str(self.lineEdit_codice_periodo.text())

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_periodo.currentText()),  # 2 - Periodo
            str(self.comboBox_fase.currentText()),  # 3 - Fase
            str(cron_iniz),  # 4 - Cron iniziale
            str(cron_fin),  # 5 - Cron finale
            str(self.textEdit_descrizione_per.toPlainText()),  # 6 - Descrizioene
            str(self.comboBox_per_estesa.currentText()),  # 7 - Cron estesa
            str(cont_per)]
            #str(self.comboBox_area.currentText())]  # 8 - Cont_per

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(str(getattr(self.DATA_LIST[self.REC_CORR], i)))

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
                                   [int(getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE))],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            str(e)
            save_file='{}{}{}'.format(self.HOME, os.sep,"pyarchinit_Report_folder") 
            file_=os.path.join(save_file,'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            if self.L=='it':
                QMessageBox.warning(self, "Messaggio",
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Verrà fatta una copia dell'errore con i dati che puoi recuperare nella cartella pyarchinit_Report _Folder", QMessageBox.StandardButton.Ok)
            
            
            elif self.L=='de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered. A copy of the error will be made with the data you can retrieve in the pyarchinit_Report _Folder", QMessageBox.StandardButton.Ok) 
            else:
                QMessageBox.warning(self, "Message",
                                    "Kodierungsproblem: Es wurden Akzente oder Zeichen eingegeben, die von der Datenbank nicht akzeptiert werden. Es wird eine Kopie des Fehlers mit den Daten erstellt, die Sie im pyarchinit_Report _Ordner abrufen können", QMessageBox.StandardButton.Ok)
            return 0

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()



    def check_for_updates(self):
        """Check if current record has been modified by others"""
        try:
            if self.BROWSE_STATUS == "b" and self.editing_record_id and self.DB_MANAGER:
                # Skip check if we're currently saving to avoid false positives
                if hasattr(self, 'is_saving') and self.is_saving:
                    return

                # Determine table name
                table_name = 'periodizzazione_table'

                # Get current username to skip self-modifications
                current_user = self.concurrency_manager.get_username() if hasattr(self, 'concurrency_manager') else 'unknown'

                has_conflict, db_version, last_modified_by, last_modified_timestamp = \
                    self.concurrency_manager.check_version_conflict(
                        table_name,
                        self.editing_record_id,
                        self.current_record_version,
                        self.DB_MANAGER
                    )

                # Only show conflict if it's a real conflict:
                # - Not a self-modification (different user)
                # - Not a system update
                # - Has actual version change
                if has_conflict and last_modified_by and \
                   last_modified_by != current_user and \
                   last_modified_by.lower() not in ['system', 'postgres'] and \
                   db_version != self.current_record_version:
                    # Show notification
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Record Modificato / Record Modified")
                    msg.setText(
                        f"Questo record è stato modificato da {last_modified_by} "
                        f"alle {last_modified_timestamp}.\n\n"
                        f"This record was modified by {last_modified_by} "
                        f"at {last_modified_timestamp}.\n\n"
                        f"Vuoi ricaricare il record? / Do you want to reload?"
                    )
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                    if msg.exec() == QMessageBox.StandardButton.Yes:
                        # Save current record position
                        current_pos = self.REC_CORR
                        # Reload records
                        self.charge_records()
                        # Restore position and fill fields
                        self.fill_fields(current_pos)
                        # Update version after reload
                        self.current_record_version = db_version
        except Exception as e:
            # Log silently to avoid annoying messages
            pass  # QgsMessageLog.logMessage(f"Update check error: {str(e)}", "PyArchInit", Qgis.Info)

## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_US()
    ui.show()
    sys.exit(app.exec())
