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
import re
import webbrowser
from datetime import date, datetime

import sys
from qgis._core import QgsMessageLog

# OpenAI import removed to avoid pydantic conflicts - will be imported lazily in contenuto method
import requests
from qgis.PyQt.QtCore import QUrl, Qt, QTimer
from qgis.PyQt.QtWidgets import QApplication, QFileDialog,QDialog, QMessageBox,QCompleter,QComboBox,QInputDialog,QLabel,QFormLayout,QPushButton,QVBoxLayout,QHBoxLayout
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis
from qgis.core import QgsSettings
import csv, sqlite3
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.pyarchinit_error_check import Error_check
# MyApp is imported lazily in contenuto to avoid pydantic/openai conflicts on Windows
from ..gui.sortpanelmain import SortPanelMain
from ..modules.utility.pyarchinit_theme_manager import ThemeManager

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Thesaurus.ui'))


class pyarchinit_Thesaurus(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L=='it':
        MSG_BOX_TITLE = "PyArchInit - Thesaurus"
    
    elif L=='de':
        MSG_BOX_TITLE = "PyArchInit - Thesaurus"
    else:
        MSG_BOX_TITLE = "PyArchInit - Thesaurus" 
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    HOME = os.environ['PYARCHINIT_HOME']
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'pyarchinit_thesaurus_sigle'
    MAPPER_TABLE_CLASS = "PYARCHINIT_THESAURUS_SIGLE"
    NOME_SCHEDA = "Scheda Thesaurus Sigle"
    ID_TABLE = "id_thesaurus_sigle"
    if L=='it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Nome tabella": "nome_tabella",
            "Sigla": "sigla",
            "Sigla estesa": "sigla_estesa",
            "Descrizione": "descrizione",
            "Tipologia sigla": "tipologia_sigla",
            "Lingua": "lingua"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Nome tabella",
            "Sigla",
            "Sigla estesa",
            "Descrizione",
            "Tipologia sigla",
            "Lingua"
        ]
    elif L=='de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Tabellenname": "nome_tabella",
            "Abkürzung": "sigla",
            "Erweitertes Abkürzungszeichen": "sigla_estesa",
            "Beschreibung": "descrizione",
            "Abkürzungtyp": "tipologia_sigla",
            "Sprache": "lingua"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Tabellenname",
            "Abkürzung",
            "Erweitertes Abkürzungszeichen",
            "Beschreibung",
            "Abkürzungtyp",
            "Sprache"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Table name": "nome_tabella",
            "Code": "sigla",
            "Code whole": "sigla_estesa",
            "Description": "descrizione",
            "Code typology": "tipologia_sigla",
            "Language": "lingua"
        }

        SORT_ITEMS = [
            ID_TABLE,
            "Table name",
            "Code",
            "Code whole",
            "Description",
            "Code typology",
            "Language"
        ]   
    LANG = {
        "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        "EN": ['en', 'EN'],
        "EN_US": ['en_US', 'EN_US', 'EN_EN'],
        "DE": ['de_DE', 'de', 'DE', 'DE_DE'],
        "FR": ['fr_FR', 'fr', 'FR', 'FR_FR'],
        "ES": ['es_ES', 'es', 'ES', 'ES_ES'],
        "PT": ['pt_PT', 'pt', 'PT', 'PT_PT'],
        "SV": ['sv_SV', 'sv', 'SV', 'SV_SV'],
        "RU": ['ru_RU', 'ru', 'RU', 'RU_RU'],
        "RO": ['ro_RO', 'ro', 'RO', 'RO_RO'],
        "AR": ['ar_LB', 'ar', 'AR', 'AR_LB', 'ar_AR', 'AR_AR'],
        "CA": ['ca_ES', 'ca', 'CA', 'CA_ES'],
        "PT_BR": ['pt_BR', 'PT_BR'],
        "SL": ['sl_SL', 'sl', 'SL', 'SL_SL'],
    }

    TABLE_FIELDS = [
        "nome_tabella",
        "sigla",
        "sigla_estesa",
        "descrizione",
        "tipologia_sigla",
        "lingua",
        "order_layer",
        "id_parent", 
        "parent_sigla",
        "hierarchy_level"
    ]
    DB_SERVER = "not defined"  ####nuovo sistema sort

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)

        # Apply theme
        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        self.currentLayerId = None
        
        # Create hierarchy widgets after UI setup
        self.create_hierarchy_widgets()
        
        self.comboBox_nome_tabella.currentTextChanged.connect(self.charge_n_sigla)
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.StandardButton.Ok)
        self.comboBox_sigla_estesa.editTextChanged.connect(self.find_text)
        self.check_db()

    def read_api_key(self, path):
        with open(path, 'r') as f:
            return f.read().strip()

    def write_api_key(self, path, api_key):
        with open(path, 'w') as f:
            f.write(api_key)



    def apikey_gpt(self):
        # HOME = os.environ['PYARCHINIT_HOME']
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
    def check_db(self):
        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.pushButton_import_csvthesaurus.setHidden(False)
        else:
            self.pushButton_import_csvthesaurus.setHidden(True)

    def contenuto(self, b):
        # Lazy import to avoid pydantic conflicts
        try:
            from openai import OpenAI
        except ImportError as e:
            QMessageBox.warning(
                self,
                "GPT Feature Unavailable",
                f"Cannot load GPT feature due to import error:\n\n{str(e)}\n\n"
                "Please install or update: python -m pip install --upgrade openai pydantic pydantic-core",
                QMessageBox.StandardButton.Ok
            )
            return ""

        models = ["gpt-4o", "gpt-4-turbo"]  # Replace with actual model names
        os.environ["OPENAI_API_KEY"] = self.apikey_gpt()
        combo = QComboBox()
        combo.addItems(models)
        selected_model, ok = QInputDialog.getItem(self, "Select Model", "Choose a model for GPT:", models, 0,
                                                  False)

        if ok and selected_model:
            client = OpenAI()

            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "user", "content": f"forniscimi una descrizione e 3 link wikipidia riguardo a questo "
                                                f"contenuto {b}, tenendo presente che il contesto è archeologico"}
                ],
                stream=True
            )

            combined_message = "GPT Response:\n "
            self.textEdit_descrizione_sigla.setPlainText(combined_message)

            try:
                end = ''

                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        # print(chunk.choices[0].delta.content, end="")
                        combined_message += chunk.choices[0].delta.content
                        combined_message += end
                        # Rendi i link cliccabili
                        self.textEdit_descrizione_sigla.setPlainText(combined_message)
                        QApplication.processEvents()
                return combined_message
            except requests.exceptions.JSONDecodeError as e:
                print("Error decoding JSON response:", e)

                return str(e)

        elif not ok:
            return "Model selection was canceled."
    def webview(self):
        description=str(self.textEdit_descrizione_sigla.toPlainText())

        links = re.findall("(?P<url>https?://[^\s]+)", description)

        # Create an HTML string to display in the QWebView
        html_string = "<html><body>"
        html_string += "<p>" + description.replace("\n", "<br>") + "</p>"
        html_string += "<ul>"
        for link in links:
            html_string += f"<li><a href='{link}'>{link}</a></li>"
        html_string += "</ul>"
        html_string += "</body></html>"
        vista=html_string
        QMessageBox.information(self, 'testo', str(html_string))
        # Display the HTML in the QTextBrowser widget
        self.webView_adarte.setHtml(vista)


        # Show the QWebView widget
        self.webView_adarte.show()
    def handleComboActivated(self, index):
        selected_text = self.comboBox_sigla_estesa.itemText(index)
        generate_text = self.contenuto(selected_text)
        reply = QMessageBox.information(self, 'Info', generate_text, QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Ok:
            self.textEdit_descrizione_sigla.setText(generate_text)

    def on_suggerimenti_pressed(self):
        s = self.contenuto(self.comboBox_sigla_estesa.currentText())
        generate_text = s
        #QMessageBox.information(self, 'info', str(generate_text), QMessageBox.Ok | QMessageBox.Cancel)

        if QMessageBox.StandardButton.Ok:
            self.textEdit_descrizione_sigla.setText(str(generate_text))
            self.webview()
        else:
            pass
    def find_text(self):

        if self.comboBox_sigla_estesa.currentText()=='':
            uri= 'https://vast-lab.org/thesaurus/ra/vocab/index.php?'
        else:

            uri= 'https://vast-lab.org/thesaurus/ra/vocab/index.php?ws=t&xstring='+ self.comboBox_sigla_estesa.currentText()+'&hasTopTerm=&hasNote=NA&fromDate=&termDeep=&boton=Conferma&xsearch=1#xstring'
            self.comboBox_sigla_estesa.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.comboBox_sigla_estesa.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        # Load URL content in the internal webView_adarte widget
        try:
            response = requests.get(uri, timeout=10)
            response.raise_for_status()
            self.webView_adarte.setHtml(response.text)
            self.webView_adarte.show()
        except requests.RequestException as e:
            QMessageBox.warning(self, "Thesaurus", f"Errore nel caricamento: {str(e)}", QMessageBox.StandardButton.Ok)
    

    def  on_pushButton_import_csvthesaurus_pressed(self):
        '''funzione valida solo per sqlite'''
        
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            '',
            " csv pyarchinit thesaurus (*.csv)"
        )[0]
        filename=dbpath#.split("/")[-1]
        try:
            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()
            
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            
            con = sqlite3.connect(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            cur = con.cursor()
            
            with open(str(filename),'r') as fin: 
                dr = csv.DictReader(fin) # comma is default delimiter
                to_db = [(i['nome_tabella'], i['sigla'], i['sigla_estesa'], i['descrizione'],i['tipologia_sigla'], i['lingua']) for i in dr]

            cur.executemany("INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua ) VALUES (?, ?, ?,?,?,?);", to_db)
            con.commit()
            con.close()
            
        except AssertionError as e:
            QMessageBox.warning(self, 'error', str(e), QMessageBox.StandardButton.Ok)
        self.pushButton_view_all.click()  
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
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
                #
            else:
                if self.L=='it':
                    QMessageBox.warning(self,"BENVENUTO", "Benvenuto in pyArchInit" + "Scheda Campioni" + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.StandardButton.Ok)
                
                elif self.L=='de':
                    
                    QMessageBox.warning(self,"WILLKOMMEN","WILLKOMMEN in pyArchInit" + "Munsterformular"+ ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.StandardButton.Ok) 
                else:
                    QMessageBox.warning(self,"WELCOME", "Welcome in pyArchInit" + "Samples form" + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.StandardButton.Ok)   
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
        #pass
        self.comboBox_lingua.clear()
        lingua = []
        for key, values in self.LANG.items():
            lingua.append(key)
        self.comboBox_lingua.addItems(lingua)
        
        # Populate nome_tabella combobox with user-friendly names
        self.comboBox_nome_tabella.clear()
        
        # Define table mapping: display name -> actual table name
        self.TABLE_DISPLAY_MAPPING = {
            'Sito': 'site_table',
            'US': 'us_table',
            'UT': 'ut_table',
            'Fauna': 'fauna_table',
            'Inventario Materiali': 'inventario_materiali_table',
            'Campioni': 'campioni_table',
            'Inventario Lapidei': 'inventario_lapidei_table',
            'Struttura': 'struttura_table',
            'Tomba': 'tomba_table',
            'Individui': 'individui_table',
            'Documentazione': 'documentazione_table',
            'TMA materiali archeologici': 'tma_materiali_archeologici',
            'TMA Materiali Ripetibili': 'tma_materiali_ripetibili',
            'Pottery': 'pottery_table'
        }
        
        # Mappatura dei campi sincronizzati tra tabelle
        # Ogni campo comune ha una lista di tuple (nome_tabella, codice_tipologia)
        self.SYNCHRONIZED_FIELDS = {
            'area': [
                ('us_table', '2.43'),
                ('inventario_materiali_table', '3.11'),
                ('tomba_table', '7.8'),
                ('individui_table', '8.6'),
                ('TMA materiali archeologici', '10.7'),
                ('pottery_table', '11.13')
            ],
            

            'materiale': [
                ('TMA materiali archeologici', '10.4'),
                ('TMA Materiali Ripetibili', '10.4')
            ],
            'categoria': [
                ('TMA materiali archeologici', '10.10'),
                ('TMA Materiali Ripetibili', '10.10')
            ],
            'classe': [
                ('TMA materiali archeologici', '10.11'),
                ('TMA Materiali Ripetibili', '10.11')
            ],
            'precisazione_tipologica': [
                ('TMA materiali archeologici', '10.12'),
                ('TMA Materiali Ripetibili', '10.12')
            ],
            'definizione': [
                ('TMA materiali archeologici', '10.13'),
                ('TMA Materiali Ripetibili', '10.13')
            ],
            'cronologia': [
                ('TMA materiali archeologici', '10.4'),
                ('TMA Materiali Ripetibili', '10.4')
            ],
            
        }
        
        # Add display names to combobox
        display_names = list(self.TABLE_DISPLAY_MAPPING.keys())
        self.comboBox_nome_tabella.addItems(display_names)
    def get_table_name_from_display(self, display_name):
        """Convert display name to actual table name"""
        if hasattr(self, 'TABLE_DISPLAY_MAPPING'):
            return self.TABLE_DISPLAY_MAPPING.get(display_name, display_name)
        return display_name
    
    def get_display_name_from_table(self, table_name):
        """Convert table name to display name"""
        if hasattr(self, 'TABLE_DISPLAY_MAPPING'):
            for display, table in self.TABLE_DISPLAY_MAPPING.items():
                if table == table_name:
                    return display
        return table_name
    
    def charge_n_sigla(self):    
        self.comboBox_tipologia_sigla.clear()
        self.comboBox_tipologia_sigla.update()
        
        # Define code descriptions for each table - multilingual support
        code_descriptions = {
            'site_table': {
                '1.1': {'it': 'Definizione sito', 'en': 'Site definition', 'de': 'Fundortdefinition', 'es': 'Definición del sitio', 'fr': 'Définition du site', 'ar': 'تعريف الموقع'}
            },
            'us_table': {
                '2.1': {'it': 'Settore', 'en': 'Sector', 'de': 'Sektor', 'es': 'Sector', 'fr': 'Secteur', 'ar': 'القطاع'},
                '2.2': {'it': 'Soprintendenza', 'en': 'Superintendence', 'de': 'Aufsichtsbehörde', 'es': 'Superintendencia', 'fr': 'Surintendance', 'ar': 'الإشراف'},
                '2.43': {'it': 'Area', 'en': 'Area', 'de': 'Bereich', 'es': 'Área', 'fr': 'Zone', 'ar': 'المنطقة'},
                '2.3': {'it': 'Definizione stratigrafica', 'en': 'Stratigraphic definition', 'de': 'Stratigraphische Definition', 'es': 'Definición estratigráfica', 'fr': 'Définition stratigraphique', 'ar': 'التعريف الطبقي'},
                '2.4': {'it': 'Definizione interpretata', 'en': 'Interpreted definition', 'de': 'Interpretierte Definition', 'es': 'Definición interpretada', 'fr': 'Définition interprétée', 'ar': 'التعريف المفسر'},
                '2.5': {'it': 'Funzione statica', 'en': 'Static function', 'de': 'Statische Funktion', 'es': 'Función estática', 'fr': 'Fonction statique', 'ar': 'الوظيفة الثابتة'},
                '2.6': {'it': 'Consistenza legante usm', 'en': 'USM binder consistency', 'de': 'USM Bindemittelkonsistenz', 'es': 'Consistencia del aglutinante USM', 'fr': 'Consistance du liant USM', 'ar': 'اتساق رابط USM'},
                '2.7': {'it': 'Consistenza/texture', 'en': 'Consistency/texture', 'de': 'Konsistenz/Textur', 'es': 'Consistencia/textura', 'fr': 'Consistance/texture', 'ar': 'الاتساق/الملمس'},
                '2.8': {'it': 'Metodo di scavo', 'en': 'Excavation method', 'de': 'Grabungsmethode', 'es': 'Método de excavación', 'fr': 'Méthode de fouille', 'ar': 'طريقة الحفر'},
                '2.9': {'it': 'Formazione', 'en': 'Formation', 'de': 'Formation', 'es': 'Formación', 'fr': 'Formation', 'ar': 'التكوين'},
                '2.10': {'it': 'Modo formazione', 'en': 'Formation mode', 'de': 'Bildungsmodus', 'es': 'Modo de formación', 'fr': 'Mode de formation', 'ar': 'نمط التكوين'},
                '2.11': {'it': 'Consistenza', 'en': 'Consistency', 'de': 'Konsistenz', 'es': 'Consistencia', 'fr': 'Consistance', 'ar': 'الاتساق'},
                '2.12': {'it': 'Stato di conservazione', 'en': 'Conservation state', 'de': 'Erhaltungszustand', 'es': 'Estado de conservación', 'fr': 'État de conservation', 'ar': 'حالة الحفظ'},
                '2.13': {'it': 'Campioni', 'en': 'Samples', 'de': 'Proben', 'es': 'Muestras', 'fr': 'Échantillons', 'ar': 'العينات'},
                '2.14': {'it': 'Componenti organici', 'en': 'Organic components', 'de': 'Organische Komponenten', 'es': 'Componentes orgánicos', 'fr': 'Composants organiques', 'ar': 'المكونات العضوية'},
                '2.15': {'it': 'Componenti inorganici', 'en': 'Inorganic components', 'de': 'Anorganische Komponenten', 'es': 'Componentes inorgánicos', 'fr': 'Composants inorganiques', 'ar': 'المكونات غير العضوية'},
                '2.16': {'it': 'Schedatore', 'en': 'Recorder', 'de': 'Erfasser', 'es': 'Registrador', 'fr': 'Enregistreur', 'ar': 'المسجل'},
                '2.17': {'it': 'Direttore us', 'en': 'SU director', 'de': 'SE Direktor', 'es': 'Director US', 'fr': 'Directeur US', 'ar': 'مدير الوحدة'},
                '2.18': {'it': 'Responsabile us', 'en': 'SU responsible', 'de': 'SE Verantwortlicher', 'es': 'Responsable US', 'fr': 'Responsable US', 'ar': 'المسؤول عن الوحدة'},
                '2.19': {'it': 'Tipo documentazione', 'en': 'Documentation type', 'de': 'Dokumentationstyp', 'es': 'Tipo de documentación', 'fr': 'Type de documentation', 'ar': 'نوع التوثيق'},
                '2.20': {'it': 'Tipologia dell\'opera', 'en': 'Work typology', 'de': 'Werktypologie', 'es': 'Tipología de la obra', 'fr': 'Typologie de l\'ouvrage', 'ar': 'تصنيف العمل'},
                '2.21': {'it': 'Sezione muraria', 'en': 'Wall section', 'de': 'Mauerquerschnitt', 'es': 'Sección de muro', 'fr': 'Section murale', 'ar': 'مقطع الجدار'},
                '2.22': {'it': 'Superficie analizzata', 'en': 'Analyzed surface', 'de': 'Analysierte Oberfläche', 'es': 'Superficie analizada', 'fr': 'Surface analysée', 'ar': 'السطح المحلل'},
                '2.23': {'it': 'Orientamento', 'en': 'Orientation', 'de': 'Orientierung', 'es': 'Orientación', 'fr': 'Orientation', 'ar': 'التوجه'},
                '2.24': {'it': 'Materiali laterizi', 'en': 'Brick materials', 'de': 'Ziegelmaterialien', 'es': 'Materiales de ladrillo', 'fr': 'Matériaux en brique', 'ar': 'مواد الطوب'},
                '2.25': {'it': 'Lavorazione laterizi', 'en': 'Brick processing', 'de': 'Ziegelbearbeitung', 'es': 'Procesamiento de ladrillos', 'fr': 'Traitement des briques', 'ar': 'معالجة الطوب'},
                '2.26': {'it': 'Consistenza laterizi', 'en': 'Brick consistency', 'de': 'Ziegelkonsistenz', 'es': 'Consistencia de ladrillos', 'fr': 'Consistance des briques', 'ar': 'اتساق الطوب'},
                '2.27': {'it': 'Forma laterizi', 'en': 'Brick shape', 'de': 'Ziegelform', 'es': 'Forma de ladrillos', 'fr': 'Forme des briques', 'ar': 'شكل الطوب'},
                '2.28': {'it': 'Colore laterizi', 'en': 'Brick color', 'de': 'Ziegelfarbe', 'es': 'Color de ladrillos', 'fr': 'Couleur des briques', 'ar': 'لون الطوب'},
                '2.29': {'it': 'Impasto laterizi', 'en': 'Brick fabric', 'de': 'Ziegelteig', 'es': 'Pasta de ladrillos', 'fr': 'Pâte des briques', 'ar': 'عجينة الطوب'},
                '2.30': {'it': 'Materiali litici', 'en': 'Lithic materials', 'de': 'Steinmaterialien', 'es': 'Materiales líticos', 'fr': 'Matériaux lithiques', 'ar': 'المواد الحجرية'},
                '2.31': {'it': 'Consistenza materiali litici', 'en': 'Lithic materials consistency', 'de': 'Steinmaterialkonsistenz', 'es': 'Consistencia de materiales líticos', 'fr': 'Consistance des matériaux lithiques', 'ar': 'اتساق المواد الحجرية'},
                '2.32': {'it': 'Forma materiali litici', 'en': 'Lithic materials shape', 'de': 'Steinmaterialform', 'es': 'Forma de materiales líticos', 'fr': 'Forme des matériaux lithiques', 'ar': 'شكل المواد الحجرية'},
                '2.33': {'it': 'Colore materiali litici', 'en': 'Lithic materials color', 'de': 'Steinmaterialfarbe', 'es': 'Color de materiales líticos', 'fr': 'Couleur des matériaux lithiques', 'ar': 'لون المواد الحجرية'},
                '2.34': {'it': 'Taglio', 'en': 'Cut', 'de': 'Schnitt', 'es': 'Corte', 'fr': 'Coupe', 'ar': 'القطع'},
                '2.35': {'it': 'Posa opera materiali litici', 'en': 'Lithic materials laying', 'de': 'Steinmaterialverlegung', 'es': 'Colocación de materiales líticos', 'fr': 'Pose des matériaux lithiques', 'ar': 'وضع المواد الحجرية'},
                '2.36': {'it': 'Posa in opera laterizi', 'en': 'Brick laying', 'de': 'Ziegelverlegung', 'es': 'Colocación de ladrillos', 'fr': 'Pose des briques', 'ar': 'وضع الطوب'},
                '2.37': {'it': 'Tecniche costruttive', 'en': 'Construction techniques', 'de': 'Bautechniken', 'es': 'Técnicas constructivas', 'fr': 'Techniques de construction', 'ar': 'تقنيات البناء'},
                '2.38': {'it': 'Modulo', 'en': 'Module', 'de': 'Modul', 'es': 'Módulo', 'fr': 'Module', 'ar': 'الوحدة'},
                '2.39': {'it': 'Inerti', 'en': 'Aggregates', 'de': 'Zuschlagstoffe', 'es': 'Áridos', 'fr': 'Agrégats', 'ar': 'الركام'},
                '2.40': {'it': 'Tipologia legante', 'en': 'Binder typology', 'de': 'Bindemitteltypologie', 'es': 'Tipología del aglutinante', 'fr': 'Typologie du liant', 'ar': 'تصنيف الرابط'},
                '2.41': {'it': 'Rifinitura', 'en': 'Finishing', 'de': 'Endbearbeitung', 'es': 'Acabado', 'fr': 'Finition', 'ar': 'التشطيب'},
                '2.42': {'it': 'Lavorazione litica', 'en': 'Lithic processing', 'de': 'Steinbearbeitung', 'es': 'Procesamiento lítico', 'fr': 'Traitement lithique', 'ar': 'المعالجة الحجرية'},
                '201.201': {'it': 'Colore legante', 'en': 'Binder color', 'de': 'Bindemittelfarbe', 'es': 'Color del aglutinante', 'fr': 'Couleur du liant', 'ar': 'لون الرابط'},
                '202.202': {'it': 'Inclusi', 'en': 'Inclusions', 'de': 'Einschlüsse', 'es': 'Inclusiones', 'fr': 'Inclusions', 'ar': 'الشوائب'},
                '203.203': {'it': 'Valori sì/no', 'en': 'Yes/No values', 'de': 'Ja/Nein-Werte', 'es': 'Valores sí/no', 'fr': 'Valeurs oui/non', 'ar': 'قيم نعم/لا'}
            },
            'inventario_materiali_table': {
                '3.1': {'it': 'Tipo reperto', 'en': 'Find type', 'de': 'Fundtyp', 'es': 'Tipo de hallazgo', 'fr': 'Type de trouvaille', 'ar': 'نوع المكتشف'},
                '3.2': {'it': 'Classe materiale', 'en': 'Material class', 'de': 'Materialklasse', 'es': 'Clase de material', 'fr': 'Classe de matériau', 'ar': 'فئة المادة'},
                '3.3': {'it': 'Definizione reperto', 'en': 'Find definition', 'de': 'Funddefinition', 'es': 'Definición del hallazgo', 'fr': 'Définition de la trouvaille', 'ar': 'تعريف المكتشف'},
                '3.4': {'it': 'Elemento rinvenuto', 'en': 'Found element', 'de': 'Gefundenes Element', 'es': 'Elemento encontrado', 'fr': 'Élément trouvé', 'ar': 'العنصر المكتشف'},
                '3.5': {'it': 'Tipo di misura', 'en': 'Measurement type', 'de': 'Messungstyp', 'es': 'Tipo de medida', 'fr': 'Type de mesure', 'ar': 'نوع القياس'},
                '3.6': {'it': 'Misurazioni - Unità di misura', 'en': 'Measurements - Unit of measure', 'de': 'Messungen - Maßeinheit', 'es': 'Mediciones - Unidad de medida', 'fr': 'Mesures - Unité de mesure', 'ar': 'القياسات - وحدة القياس'},
                '3.7': {'it': 'Tipo tecnologia', 'en': 'Technology type', 'de': 'Technologietyp', 'es': 'Tipo de tecnología', 'fr': 'Type de technologie', 'ar': 'نوع التقنية'},
                '3.8': {'it': 'Posizione', 'en': 'Position', 'de': 'Position', 'es': 'Posición', 'fr': 'Position', 'ar': 'الموقع'},
                '3.9': {'it': 'Tipo quantità', 'en': 'Quantity type', 'de': 'Mengentyp', 'es': 'Tipo de cantidad', 'fr': 'Type de quantité', 'ar': 'نوع الكمية'},
                '3.10': {'it': 'Tecnologie - Unità di misura', 'en': 'Technologies - Unit of measure', 'de': 'Technologien - Maßeinheit', 'es': 'Tecnologías - Unidad de medida', 'fr': 'Technologies - Unité de mesure', 'ar': 'التقنيات - وحدة القياس'},
                '3.11': {'it': 'Area', 'en': 'Area', 'de': 'Bereich', 'es': 'Área', 'fr': 'Zone', 'ar': 'المنطقة'},
                '3.41': {'it': 'Tipologia', 'en': 'Typology', 'de': 'Typologie', 'es': 'Tipología', 'fr': 'Typologie', 'ar': 'التصنيف'},
                '3.13': {'it': 'Anno', 'en': 'Year', 'de': 'Jahr', 'es': 'Año', 'fr': 'Année', 'ar': 'السنة'},
                '301.301': {'it': 'Valori sì/no', 'en': 'Yes/No values', 'de': 'Ja/Nein-Werte', 'es': 'Valores sí/no', 'fr': 'Valeurs oui/non', 'ar': 'قيم نعم/لا'}
            },
            'campioni_table': {
                '4.1': {'it': 'Tipo campione', 'en': 'Sample type', 'de': 'Probentyp', 'es': 'Tipo de muestra', 'fr': 'Type d\'échantillon', 'ar': 'نوع العينة'}
            },
            'inventario_lapidei_table': {
                '5.1': {'it': 'Tipologia', 'en': 'Typology', 'de': 'Typologie', 'es': 'Tipología', 'fr': 'Typologie', 'ar': 'التصنيف'},
                '5.2': {'it': 'Materiale', 'en': 'Material', 'de': 'Material', 'es': 'Material', 'fr': 'Matériau', 'ar': 'المادة'},
                '5.3': {'it': 'Oggetto', 'en': 'Object', 'de': 'Objekt', 'es': 'Objeto', 'fr': 'Objet', 'ar': 'الكائن'}
            },
            'struttura_table': {
                '6.1': {'it': 'Sigla struttura', 'en': 'Structure code', 'de': 'Strukturkürzel', 'es': 'Código estructura', 'fr': 'Code structure', 'ar': 'رمز الهيكل'},
                '6.2': {'it': 'Categoria', 'en': 'Category', 'de': 'Kategorie', 'es': 'Categoría', 'fr': 'Catégorie', 'ar': 'الفئة'},
                '6.3': {'it': 'Tipologia', 'en': 'Typology', 'de': 'Typologie', 'es': 'Tipología', 'fr': 'Typologie', 'ar': 'التصنيف'},
                '6.4': {'it': 'Definizione', 'en': 'Definition', 'de': 'Definition', 'es': 'Definición', 'fr': 'Définition', 'ar': 'التعريف'},
                '6.5': {'it': 'Materiali impiegati', 'en': 'Materials used', 'de': 'Verwendete Materialien', 'es': 'Materiales utilizados', 'fr': 'Matériaux utilisés', 'ar': 'المواد المستخدمة'},
                '6.6': {'it': 'Tipologia elemento strutturale', 'en': 'Structural element type', 'de': 'Strukturelementtyp', 'es': 'Tipo de elemento estructural', 'fr': 'Type d\'élément structurel', 'ar': 'نوع العنصر الهيكلي'},
                '6.7': {'it': 'Tipo misura', 'en': 'Measurement type', 'de': 'Messungstyp', 'es': 'Tipo de medida', 'fr': 'Type de mesure', 'ar': 'نوع القياس'},
                '6.8': {'it': 'Unità di misura', 'en': 'Unit of measure', 'de': 'Maßeinheit', 'es': 'Unidad de medida', 'fr': 'Unité de mesure', 'ar': 'وحدة القياس'},
                '6.9': {'it': 'Elementi architettonici AR', 'en': 'AR architectural elements', 'de': 'AR architektonische Elemente', 'es': 'Elementos arquitectónicos AR', 'fr': 'Éléments architecturaux AR', 'ar': 'العناصر المعمارية AR'},
                '6.10': {'it': 'Fattori agenti', 'en': 'Acting factors', 'de': 'Einwirkende Faktoren', 'es': 'Factores agentes', 'fr': 'Facteurs agissants', 'ar': 'العوامل المؤثرة'},
                '6.11': {'it': 'Prospetto ingresso', 'en': 'Entrance facade', 'de': 'Eingangsfassade', 'es': 'Fachada de entrada', 'fr': 'Façade d\'entrée', 'ar': 'واجهة المدخل'},
                '6.12': {'it': 'Elementi costitutivi', 'en': 'Constituent elements', 'de': 'Bauteile', 'es': 'Elementos constitutivos', 'fr': 'Éléments constitutifs', 'ar': 'العناصر المكونة'},
                '6.13': {'it': 'Manufatti', 'en': 'Artifacts', 'de': 'Artefakte', 'es': 'Artefactos', 'fr': 'Artefacts', 'ar': 'القطع الأثرية'},
                '6.14': {'it': 'Definizione fasi funzionali', 'en': 'Functional phases definition', 'de': 'Funktionsphasen Definition', 'es': 'Definición fases funcionales', 'fr': 'Définition phases fonctionnelles', 'ar': 'تعريف المراحل الوظيفية'},
                '6.15': {'it': 'Sviluppo planimetrico', 'en': 'Planimetric development', 'de': 'Planimetrische Entwicklung', 'es': 'Desarrollo planimétrico', 'fr': 'Développement planimétrique', 'ar': 'التطور المستوي'}
            },
            'tomba_table': {
                '7.1': {'it': 'Tipo rituale', 'en': 'Ritual type', 'de': 'Ritualtyp', 'es': 'Tipo de ritual', 'fr': 'Type de rituel', 'ar': 'نوع الطقس'},
                '7.2': {'it': 'Stato di conservazione', 'en': 'Conservation state', 'de': 'Erhaltungszustand', 'es': 'Estado de conservación', 'fr': 'État de conservation', 'ar': 'حالة الحفظ'},
                '7.3': {'it': 'Tipo copertura', 'en': 'Cover type', 'de': 'Abdeckungstyp', 'es': 'Tipo de cubierta', 'fr': 'Type de couverture', 'ar': 'نوع الغطاء'},
                '7.4': {'it': 'Tipo tomba', 'en': 'Tomb type', 'de': 'Grabtyp', 'es': 'Tipo de tumba', 'fr': 'Type de tombe', 'ar': 'نوع القبر'},
                '7.5': {'it': 'Corredo', 'en': 'Grave goods', 'de': 'Grabbeigaben', 'es': 'Ajuar funerario', 'fr': 'Mobilier funéraire', 'ar': 'المرفقات الجنائزية'},
                '7.6': {'it': 'Tipo deposizione', 'en': 'Deposition type', 'de': 'Bestattungstyp', 'es': 'Tipo de deposición', 'fr': 'Type de dépôt', 'ar': 'نوع الإيداع'},
                '7.7': {'it': 'Tipo sepoltura', 'en': 'Burial type', 'de': 'Bestattungsart', 'es': 'Tipo de sepultura', 'fr': 'Type de sépulture', 'ar': 'نوع الدفن'},
                '7.8': {'it': 'Area', 'en': 'Area', 'de': 'Bereich', 'es': 'Área', 'fr': 'Zone', 'ar': 'المنطقة'},
                '701.701': {'it': 'Segnacoli / Canale libatorio', 'en': 'Markers / Libation channel', 'de': 'Markierungen / Libationskanal', 'es': 'Señalizadores / Canal de libación', 'fr': 'Marqueurs / Canal de libation', 'ar': 'العلامات / قناة السكب'},
                '702.702': {'it': 'Presenza Corredo', 'en': 'Grave goods presence', 'de': 'Grabbeigaben vorhanden', 'es': 'Presencia de ajuar', 'fr': 'Présence de mobilier', 'ar': 'وجود المرفقات'}
            },
            'individui_table': {
                '8.1': {'it': 'Tipo rituale', 'en': 'Ritual type', 'de': 'Ritualtyp', 'es': 'Tipo de ritual', 'fr': 'Type de rituel', 'ar': 'نوع الطقس'},
                '8.2': {'it': 'Stato di conservazione', 'en': 'Conservation state', 'de': 'Erhaltungszustand', 'es': 'Estado de conservación', 'fr': 'État de conservation', 'ar': 'حالة الحفظ'},
                '8.3': {'it': 'Tipo copertura', 'en': 'Cover type', 'de': 'Abdeckungstyp', 'es': 'Tipo de cubierta', 'fr': 'Type de couverture', 'ar': 'نوع الغطاء'},
                '8.4': {'it': 'Tipo tomba', 'en': 'Tomb type', 'de': 'Grabtyp', 'es': 'Tipo de tumba', 'fr': 'Type de tombe', 'ar': 'نوع القبر'},
                '8.5': {'it': 'Corredo', 'en': 'Grave goods', 'de': 'Grabbeigaben', 'es': 'Ajuar funerario', 'fr': 'Mobilier funéraire', 'ar': 'المرفقات الجنائزية'},
                '8.6': {'it': 'Area', 'en': 'Area', 'de': 'Bereich', 'es': 'Área', 'fr': 'Zone', 'ar': 'المنطقة'},
                '801.801': {'it': 'Segnacoli / Canale libatorio', 'en': 'Markers / Libation channel', 'de': 'Markierungen / Libationskanal', 'es': 'Señalizadores / Canal de libación', 'fr': 'Marqueurs / Canal de libation', 'ar': 'العلامات / قناة السكب'}
            },
            'documentazione_table': {
                '9.1': {'it': 'Tipo Documentazione', 'en': 'Documentation type', 'de': 'Dokumentationstyp', 'es': 'Tipo de documentación', 'fr': 'Type de documentation', 'ar': 'نوع التوثيق'},
                '9.2': {'it': 'Sorgente', 'en': 'Source', 'de': 'Quelle', 'es': 'Fuente', 'fr': 'Source', 'ar': 'المصدر'}
            },
            'tma_materiali_archeologici': {
                '10.1': {'it': 'Denominazione collocazione', 'en': 'Location name', 'de': 'Standortbezeichnung', 'es': 'Nombre de ubicación', 'fr': 'Nom de l\'emplacement', 'ar': 'اسم الموقع'},
                '10.2': {'it': 'Tipologia Collocazione', 'en': 'Location typology', 'de': 'Standorttypologie', 'es': 'Tipología de ubicación', 'fr': 'Typologie d\'emplacement', 'ar': 'تصنيف الموقع'},
                '10.3': {'it': 'Località', 'en': 'Locality', 'de': 'Ortschaft', 'es': 'Localidad', 'fr': 'Localité', 'ar': 'المحلية'},
                '10.4': {'it': 'Fascia Cronologica', 'en': 'Chronological range', 'de': 'Chronologischer Bereich', 'es': 'Rango cronológico', 'fr': 'Plage chronologique', 'ar': 'النطاق الزمني'},
                '10.5': {'it': 'Denominazione Scavo', 'en': 'Excavation name', 'de': 'Grabungsbezeichnung', 'es': 'Nombre de excavación', 'fr': 'Nom de la fouille', 'ar': 'اسم الحفرية'},
                '10.6': {'it': 'Tipologia Acquisizione', 'en': 'Acquisition typology', 'de': 'Erwerbstypologie', 'es': 'Tipología de adquisición', 'fr': 'Typologie d\'acquisition', 'ar': 'تصنيف الاستحواذ'},
                '10.7': {'it': 'Area', 'en': 'Area', 'de': 'Bereich', 'es': 'Área', 'fr': 'Zone', 'ar': 'المنطقة'},
                '10.8': {'it': 'Tipo foto', 'en': 'Photo type', 'de': 'Fototyp', 'es': 'Tipo de foto', 'fr': 'Type de photo', 'ar': 'نوع الصورة'},
                '10.9': {'it': 'Tipo disegno', 'en': 'Drawing type', 'de': 'Zeichnungstyp', 'es': 'Tipo de dibujo', 'fr': 'Type de dessin', 'ar': 'نوع الرسم'},
                '10.15': {'it': 'Settore', 'en': 'Sector', 'de': 'Sektor', 'es': 'Sector', 'fr': 'Secteur', 'ar': 'القطاع'}
            },
            'tma_materiali_ripetibili': {
                '10.10': {'it': 'Categoria', 'en': 'Category', 'de': 'Kategorie', 'es': 'Categoría', 'fr': 'Catégorie', 'ar': 'الفئة'},
                '10.11': {'it': 'Classe', 'en': 'Class', 'de': 'Klasse', 'es': 'Clase', 'fr': 'Classe', 'ar': 'الصنف'},
                '10.12': {'it': 'Precisazione tipologica', 'en': 'Typological specification', 'de': 'Typologische Präzisierung', 'es': 'Precisión tipológica', 'fr': 'Précision typologique', 'ar': 'التحديد التصنيفي'},
                '10.13': {'it': 'Definizione', 'en': 'Definition', 'de': 'Definition', 'es': 'Definición', 'fr': 'Définition', 'ar': 'التعريف'},
                '10.4': {'it': 'Cronologia', 'en': 'Chronology', 'de': 'Chronologie', 'es': 'Cronología', 'fr': 'Chronologie', 'ar': 'التسلسل الزمني'}
            },
            'pottery_table': {
                '11.1': {'it': 'Impasto', 'en': 'Fabric', 'de': 'Ton', 'es': 'Pasta', 'fr': 'Pâte', 'ar': 'العجينة'},
                '11.2': {'it': 'Percentuale', 'en': 'Percent', 'de': 'Prozent', 'es': 'Porcentaje', 'fr': 'Pourcentage', 'ar': 'النسبة المئوية'},
                '11.3': {'it': 'Materiale', 'en': 'Material', 'de': 'Material', 'es': 'Material', 'fr': 'Matériau', 'ar': 'المادة'},
                '11.4': {'it': 'Forma', 'en': 'Form', 'de': 'Form', 'es': 'Forma', 'fr': 'Forme', 'ar': 'الشكل'},
                '11.5': {'it': 'Forma specifica', 'en': 'Specific form/part', 'de': 'Spezifische Form/Teil', 'es': 'Forma específica', 'fr': 'Forme spécifique', 'ar': 'الشكل المحدد'},
                '11.6': {'it': 'Tipo ceramica', 'en': 'Ware type', 'de': 'Keramiktyp', 'es': 'Tipo de cerámica', 'fr': 'Type de céramique', 'ar': 'نوع الفخار'},
                '11.7': {'it': 'Colore Munsell', 'en': 'Munsell color', 'de': 'Munsell-Farbe', 'es': 'Color Munsell', 'fr': 'Couleur Munsell', 'ar': 'لون مونسل'},
                '11.8': {'it': 'Trattamento superficie', 'en': 'Surface treatment', 'de': 'Oberflächenbehandlung', 'es': 'Tratamiento de superficie', 'fr': 'Traitement de surface', 'ar': 'معالجة السطح'},
                '11.9': {'it': 'Decorazione esterna', 'en': 'External decoration', 'de': 'Außendekoration', 'es': 'Decoración externa', 'fr': 'Décoration externe', 'ar': 'الزخرفة الخارجية'},
                '11.10': {'it': 'Decorazione interna', 'en': 'Internal decoration', 'de': 'Innendekoration', 'es': 'Decoración interna', 'fr': 'Décoration interne', 'ar': 'الزخرفة الداخلية'},
                '11.11': {'it': 'Tornio', 'en': 'Wheel made', 'de': 'Drehscheibe', 'es': 'Torno', 'fr': 'Tour', 'ar': 'الدولاب'},
                '11.12': {'it': 'Forma specifica', 'en': 'Specific shape', 'de': 'Spezifische Form', 'es': 'Forma específica', 'fr': 'Forme spécifique', 'ar': 'الشكل المحدد'},
                '11.13': {'it': 'Area', 'en': 'Area', 'de': 'Bereich', 'es': 'Área', 'fr': 'Zone', 'ar': 'المنطقة'},
                '11.14': {'it': 'Tipo decorazione', 'en': 'Decoration type', 'de': 'Dekorationstyp', 'es': 'Tipo de decoración', 'fr': 'Type de décoration', 'ar': 'نوع الزخرفة'},
                '11.15': {'it': 'Motivo decorazione', 'en': 'Decoration motif', 'de': 'Dekorationsmotiv', 'es': 'Motivo de decoración', 'fr': 'Motif de décoration', 'ar': 'زخرفة الزخرفة'},
                '11.16': {'it': 'Posizione decorazione', 'en': 'Decoration position', 'de': 'Dekorationsposition', 'es': 'Posición de decoración', 'fr': 'Position de décoration', 'ar': 'موقع الزخرفة'}
            },
            'ut_table': {
                '12.1': {'it': 'Tipo ricognizione', 'en': 'Survey type', 'de': 'Prospektionstyp', 'es': 'Tipo de prospección', 'fr': 'Type de prospection', 'ar': 'نوع المسح'},
                '12.2': {'it': 'Copertura vegetazione', 'en': 'Vegetation coverage', 'de': 'Vegetationsbedeckung', 'es': 'Cobertura de vegetación', 'fr': 'Couverture végétale', 'ar': 'الغطاء النباتي'},
                '12.3': {'it': 'Metodo GPS', 'en': 'GPS method', 'de': 'GPS-Methode', 'es': 'Método GPS', 'fr': 'Méthode GPS', 'ar': 'طريقة GPS'},
                '12.4': {'it': 'Condizione superficie', 'en': 'Surface condition', 'de': 'Oberflächenzustand', 'es': 'Condición de superficie', 'fr': 'État de surface', 'ar': 'حالة السطح'},
                '12.5': {'it': 'Accessibilità', 'en': 'Accessibility', 'de': 'Zugänglichkeit', 'es': 'Accesibilidad', 'fr': 'Accessibilité', 'ar': 'إمكانية الوصول'},
                '12.6': {'it': 'Condizioni meteo', 'en': 'Weather conditions', 'de': 'Wetterbedingungen', 'es': 'Condiciones meteorológicas', 'fr': 'Conditions météorologiques', 'ar': 'الظروف الجوية'}
            },
            'fauna_table': {
                '13.1': {'it': 'Contesto', 'en': 'Context', 'de': 'Kontext', 'es': 'Contexto', 'fr': 'Contexte', 'ar': 'السياق'},
                '13.2': {'it': 'Metodologia Recupero', 'en': 'Recovery methodology', 'de': 'Bergungsmethodik', 'es': 'Metodología de recuperación', 'fr': 'Méthodologie de récupération', 'ar': 'منهجية الاسترداد'},
                '13.3': {'it': 'Tipologia Accumulo', 'en': 'Accumulation type', 'de': 'Akkumulationstyp', 'es': 'Tipo de acumulación', 'fr': 'Type d\'accumulation', 'ar': 'نوع التراكم'},
                '13.4': {'it': 'Deposizione', 'en': 'Deposition', 'de': 'Ablagerung', 'es': 'Deposición', 'fr': 'Dépôt', 'ar': 'الترسب'},
                '13.5': {'it': 'Stato Frammentazione', 'en': 'Fragmentation state', 'de': 'Fragmentierungszustand', 'es': 'Estado de fragmentación', 'fr': 'État de fragmentation', 'ar': 'حالة التجزئة'},
                '13.6': {'it': 'Stato Conservazione', 'en': 'Conservation state', 'de': 'Erhaltungszustand', 'es': 'Estado de conservación', 'fr': 'État de conservation', 'ar': 'حالة الحفظ'},
                '13.7': {'it': 'Affidabilità Stratigrafica', 'en': 'Stratigraphic reliability', 'de': 'Stratigraphische Zuverlässigkeit', 'es': 'Fiabilidad estratigráfica', 'fr': 'Fiabilité stratigraphique', 'ar': 'الموثوقية الطبقية'},
                '13.8': {'it': 'Tracce Combustione', 'en': 'Burning traces', 'de': 'Verbrennungsspuren', 'es': 'Trazas de combustión', 'fr': 'Traces de combustion', 'ar': 'آثار الاحتراق'},
                '13.9': {'it': 'Tipo Combustione', 'en': 'Combustion type', 'de': 'Verbrennungstyp', 'es': 'Tipo de combustión', 'fr': 'Type de combustion', 'ar': 'نوع الاحتراق'},
                '13.10': {'it': 'Connessione Anatomica', 'en': 'Anatomical connection', 'de': 'Anatomische Verbindung', 'es': 'Conexión anatómica', 'fr': 'Connexion anatomique', 'ar': 'الاتصال التشريحي'}
            }
        }
        
        # Convert display name to actual table name
        display_name = self.comboBox_nome_tabella.currentText()
        current_table = self.get_table_name_from_display(display_name)
        
        if current_table in code_descriptions:
            self.comboBox_tipologia_sigla.clear()
            codes = list(code_descriptions[current_table].keys())

            # Get current language - use self.L which is set from QGIS locale
            # Map QGIS locale to PyArchInit supported languages
            lang = self.L.lower() if hasattr(self, 'L') else 'it'
            # Fallback to 'it' if language not supported
            supported_langs = ['it', 'en', 'de', 'es', 'fr', 'ar']
            if lang not in supported_langs:
                lang = 'it'

            # Add codes with tooltips
            for code in codes:
                self.comboBox_tipologia_sigla.addItem(code)
                index = self.comboBox_tipologia_sigla.count() - 1
                desc_value = code_descriptions[current_table][code]

                # Handle both old format (string) and new format (dict with language keys)
                if isinstance(desc_value, dict):
                    description = desc_value.get(lang, desc_value.get('it', str(desc_value)))
                else:
                    description = str(desc_value)

                self.comboBox_tipologia_sigla.setItemData(index, description, Qt.ItemDataRole.ToolTipRole)
                
        # Show hierarchy management widgets for TMA materials
        if current_table == 'TMA materiali archeologici':
            self.setup_tma_hierarchy_widgets()
    
    def setup_tma_hierarchy_widgets(self):
        """Setup hierarchy management widgets for TMA materials."""
        # Connect tipologia_sigla change to show/hide hierarchy widgets
        try:
            self.comboBox_tipologia_sigla.currentTextChanged.disconnect()
        except:
            pass
        self.comboBox_tipologia_sigla.currentTextChanged.connect(self.on_tma_tipologia_changed)
        
        # Check current tipologia
        self.on_tma_tipologia_changed()
    
    def on_tma_tipologia_changed(self):
        """Handle TMA tipologia change to show hierarchy options."""
        current_tipologia = self.comboBox_tipologia_sigla.currentText()
        
        QgsMessageLog.logMessage(f"TMA tipologia changed to: '{current_tipologia}'", "PyArchInit", Qgis.Info)
        
        # Hide hierarchy widgets by default
        self.hide_hierarchy_widgets()
        
        # Show hierarchy options based on tipologia
        # Correct codes:
        # - 10.3 = Località (no parent needed)
        # - 10.7 = Area (needs Località parent)
        # - 10.15 = Settore (needs Località and Area parent)
        
        if current_tipologia == '10.7':  # Area - needs Località parent
            QgsMessageLog.logMessage("Showing area parent widgets", "PyArchInit", Qgis.Info)
            self.show_area_parent_widgets()
        elif current_tipologia == '10.15':  # Settore - needs Località and Area parent
            QgsMessageLog.logMessage("Showing settore parent widgets", "PyArchInit", Qgis.Info)
            self.show_settore_parent_widgets()
    
    def hide_hierarchy_widgets(self):
        """Hide all hierarchy selection widgets."""
        if hasattr(self, 'label_parent_localita'):
            self.label_parent_localita.hide()
            self.comboBox_parent_localita.hide()
        if hasattr(self, 'label_parent_area'):
            self.label_parent_area.hide()
            self.comboBox_parent_area.hide()
    
    def show_area_parent_widgets(self):
        """Show widgets for selecting località parent for area."""
        # Show località selection
        if hasattr(self, 'label_parent_localita'):
            self.label_parent_localita.show()
            self.comboBox_parent_localita.show()
        
        # Hide area selection (not needed for area)
        if hasattr(self, 'label_parent_area'):
            self.label_parent_area.hide()
            self.comboBox_parent_area.hide()
        
        # Load località options
        QgsMessageLog.logMessage("About to load parent località", "PyArchInit", Qgis.Info)
        self.load_parent_localita()
        
        QgsMessageLog.logMessage("Area parent widgets shown", "PyArchInit", Qgis.Info)
    
    def show_settore_parent_widgets(self):
        """Show widgets for selecting località and area parents for settore."""
        # Show both località and area selection
        if hasattr(self, 'label_parent_localita'):
            self.label_parent_localita.show()
            self.comboBox_parent_localita.show()
        
        if hasattr(self, 'label_parent_area'):
            self.label_parent_area.show()
            self.comboBox_parent_area.show()
        
        # Load località options
        QgsMessageLog.logMessage("About to load parent località for settore", "PyArchInit", Qgis.Info)
        self.load_parent_localita()
        
        QgsMessageLog.logMessage("Settore parent widgets shown", "PyArchInit", Qgis.Info)
    
    def show_area_parent_dialog(self):
        """Show dialog for selecting località parent for area."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleziona Località per Area")
        dialog.setModal(True)
        dialog.resize(400, 150)
        
        layout = QVBoxLayout(dialog)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Località selection
        combo_localita = QComboBox()
        combo_localita.addItem("--- Seleziona località ---")
        
        # Load località options
        lingua = ""
        l = self.comboBox_lingua.currentText()
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lingua = key
        
        search_dict = {
            'nome_tabella': "'TMA materiali archeologici'",
            'tipologia_sigla': "'10.3'",  # Corrected: Località code
            'lingua': "'" + lingua + "'"
        }
        
        res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
        for i in res:
            combo_localita.addItem(f"{i.sigla} - {i.sigla_estesa}")
        
        form_layout.addRow("Località:", combo_localita)
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Annulla")
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
        
        # Store selection
        self.selected_localita_parent = None
        
        def on_ok():
            if combo_localita.currentIndex() > 0:
                self.selected_localita_parent = combo_localita.currentText().split(' - ')[0]
            dialog.accept()
        
        def on_cancel():
            self.selected_localita_parent = None
            dialog.reject()
        
        btn_ok.clicked.connect(on_ok)
        btn_cancel.clicked.connect(on_cancel)
        
        dialog.exec()
    
    def show_settore_parent_dialog(self):
        """Show dialog for selecting località and area parents for settore."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleziona Località e Area per Settore")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Località selection
        combo_localita = QComboBox()
        combo_localita.addItem("--- Seleziona località ---")
        
        # Area selection
        combo_area = QComboBox()
        combo_area.addItem("--- Prima seleziona località ---")
        combo_area.setEnabled(False)
        
        # Load località options
        lingua = ""
        l = self.comboBox_lingua.currentText()
        for key, values in self.LANG.items():
            if values.__contains__(l):
                lingua = key
        
        search_dict = {
            'nome_tabella': "'TMA materiali archeologici'",
            'tipologia_sigla': "'10.3'",  # Corrected: Località code
            'lingua': "'" + lingua + "'"
        }
        
        res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
        for i in res:
            combo_localita.addItem(f"{i.sigla} - {i.sigla_estesa}")
        
        # Update areas when località changes
        def on_localita_changed():
            combo_area.clear()
            if combo_localita.currentIndex() > 0:
                combo_area.setEnabled(True)
                combo_area.addItem("--- Seleziona area ---")
                
                localita_sigla = combo_localita.currentText().split(' - ')[0]
                
                search_dict = {
                    'nome_tabella': "'TMA materiali archeologici'",
                    'tipologia_sigla': "'10.7'",  # Area code,
                    'parent_sigla': "'" + localita_sigla + "'",
                    'lingua': "'" + lingua + "'"
                }
                
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                for i in res:
                    combo_area.addItem(f"{i.sigla} - {i.sigla_estesa}")
            else:
                combo_area.setEnabled(False)
                combo_area.addItem("--- Prima seleziona località ---")
        
        combo_localita.currentIndexChanged.connect(on_localita_changed)
        
        form_layout.addRow("Località:", combo_localita)
        form_layout.addRow("Area:", combo_area)
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Annulla")
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
        
        # Store selections
        self.selected_area_parent = None
        
        def on_ok():
            if combo_area.currentIndex() > 0:
                self.selected_area_parent = combo_area.currentText().split(' - ')[0]
            dialog.accept()
        
        def on_cancel():
            self.selected_area_parent = None
            dialog.reject()
        
        btn_ok.clicked.connect(on_ok)
        btn_cancel.clicked.connect(on_cancel)
        
        dialog.exec()
    
    def create_hierarchy_widgets(self):
        """Create hierarchy selection widgets dynamically."""
        # Create widgets for hierarchy selection
        self.label_parent_localita = QLabel("Località parent:")
        self.comboBox_parent_localita = QComboBox()
        self.comboBox_parent_localita.setEditable(True)
        
        self.label_parent_area = QLabel("Area parent:")
        self.comboBox_parent_area = QComboBox()
        self.comboBox_parent_area.setEditable(True)
        
        # Connect localita change to update areas
        self.comboBox_parent_localita.currentTextChanged.connect(self.on_parent_localita_changed)
        
        # Find the gridLayout_8 which contains the form fields
        try:
            # The UI file shows gridLayout_8 contains the form fields
            if hasattr(self, 'gridLayout_8'):
                layout = self.gridLayout_8
                
                # Find the row where tipologia_sigla is located (row 4 according to UI)
                # Add our widgets after tipologia_sigla (which is at row 4)
                
                # Add località parent at row 5
                layout.addWidget(self.label_parent_localita, 5, 0)
                layout.addWidget(self.comboBox_parent_localita, 5, 1)
                
                # Add area parent at row 6 
                layout.addWidget(self.label_parent_area, 6, 0)
                layout.addWidget(self.comboBox_parent_area, 6, 1)
                
                QgsMessageLog.logMessage("Hierarchy widgets added to gridLayout_8", "PyArchInit", Qgis.Info)
            else:
                QgsMessageLog.logMessage("gridLayout_8 not found in UI", "PyArchInit", Qgis.Warning)
                    
        except Exception as e:
            QgsMessageLog.logMessage(f"Could not add hierarchy widgets: {str(e)}", "PyArchInit", Qgis.Warning)
        
        # Initially hide all hierarchy widgets
        self.hide_hierarchy_widgets()
    
    def load_parent_areas(self):
        """Load available parent areas from thesaurus."""
        self.comboBox_parent_area.clear()
        self.comboBox_parent_area.addItem("")  # Empty option
        
        # Query areas from thesaurus
        search_dict = {
            'nome_tabella': 'TMA materiali archeologici',
            'tipologia_sigla': '10.7',  # Area code
            'lingua': self.comboBox_lingua.currentText()
        }
        
        res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
        
        areas = []
        for i in res:
            areas.append(f"{i.sigla} - {i.sigla_estesa}")
        
        areas.sort()
        self.comboBox_parent_area.addItems(areas)
    
    def load_parent_localita(self):
        """Load available località from thesaurus."""
        self.comboBox_parent_localita.clear()
        self.comboBox_parent_localita.addItem("")  # Empty option
        
        if not self.DB_MANAGER:
            QgsMessageLog.logMessage("DB_MANAGER not available for loading località", "PyArchInit", Qgis.Warning)
            return
            
        try:
            # Get current language
            lingua = ""
            l = self.comboBox_lingua.currentText()
            for key, values in self.LANG.items():
                if values.__contains__(l):
                    lingua = key
            
            # Query località (code 10.3)
            search_dict = {
                'nome_tabella': "'TMA materiali archeologici'",
                'tipologia_sigla': "'10.3'",  # Località
                'lingua': "'" + lingua + "'"
            }
            
            res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            
            localita_items = []
            for i in res:
                localita_items.append(f"{i.sigla} - {i.sigla_estesa}")
            
            localita_items.sort()
            self.comboBox_parent_localita.addItems(localita_items)
            
            QgsMessageLog.logMessage(f"Loaded {len(localita_items)} località items", "PyArchInit", Qgis.Info)
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error loading località: {str(e)}", "PyArchInit", Qgis.Warning)
            self.comboBox_parent_localita.addItem("--- Errore caricamento località ---")
    
    def on_parent_localita_changed(self):
        """When località selection changes, update available areas."""
        if hasattr(self, 'comboBox_parent_area') and self.comboBox_parent_area.isVisible():
            # Clear and reload areas based on selected località
            self.comboBox_parent_area.clear()
            self.comboBox_parent_area.addItem("")  # Empty option
            
            selected_localita = self.comboBox_parent_localita.currentText()
            if selected_localita and selected_localita != "":
                
                # Extract sigla from selection
                localita_sigla = selected_localita.split(' - ')[0] if ' - ' in selected_localita else ''
                
                if not localita_sigla or not self.DB_MANAGER:
                    return
                    
                try:
                    # Get current language
                    lingua = ""
                    l = self.comboBox_lingua.currentText()
                    for key, values in self.LANG.items():
                        if values.__contains__(l):
                            lingua = key
                    
                    # Query areas that belong to this località
                    search_dict = {
                        'nome_tabella': "'TMA materiali archeologici'",
                        'tipologia_sigla': "'10.7'",  # Area code
                        'parent_sigla': "'" + localita_sigla + "'",
                        'lingua': "'" + lingua + "'"
                    }
                    
                    res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                    
                    areas = []
                    for i in res:
                        areas.append(f"{i.sigla} - {i.sigla_estesa}")
                    
                    areas.sort()
                    self.comboBox_parent_area.addItems(areas)
                    
                    QgsMessageLog.logMessage(f"Loaded {len(areas)} areas for località {localita_sigla}", "PyArchInit", Qgis.Info)
                    
                except Exception as e:
                    QgsMessageLog.logMessage(f"Error loading areas: {str(e)}", "PyArchInit", Qgis.Warning)
    
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

                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEditable(["self.comboBox_sigla"], 1)
            self.setComboBoxEditable(["self.comboBox_sigla_estesa"], 1)
            self.setComboBoxEditable(["self.comboBox_tipologia_sigla"], 1)
            self.setComboBoxEditable(["self.comboBox_nome_tabella"], 1)
            self.setComboBoxEditable(["self.comboBox_lingua"], 1)

            self.setComboBoxEnable(["self.comboBox_sigla"], "True")
            self.setComboBoxEnable(["self.comboBox_sigla_estesa"], "True")
            self.setComboBoxEnable(["self.comboBox_tipologia_sigla"], "True")
            self.setComboBoxEnable(["self.comboBox_nome_tabella"], "True")
            self.setComboBoxEnable(["self.comboBox_lingua"], "True")

            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
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
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    self.setComboBoxEditable(["self.comboBox_sigla"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_estesa"], 1)
                    self.setComboBoxEditable(["self.comboBox_tipologia_sigla"], 1)
                    self.setComboBoxEditable(["self.comboBox_nome_tabella"], 1)
                    self.setComboBoxEditable(["self.comboBox_lingua"], 1)

                    self.setComboBoxEnable(["self.comboBox_sigla"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_estesa"], "False")
                    self.setComboBoxEnable(["self.comboBox_tipologia_sigla"], "False")
                    self.setComboBoxEnable(["self.comboBox_nome_tabella"], "False")
                    self.setComboBoxEnable(["self.comboBox_lingua"], "False")

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()
        if self.L=='it':
            if EC.data_is_empty(str(self.comboBox_sigla.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sigla \n Il campo non deve essere vuoto", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_sigla_estesa.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sigla estesa \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_tipologia_sigla.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Tipologia sigla. \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_nome_tabella.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Nome tabella \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_lingua.currentText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo lingua \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.textEdit_descrizione_sigla.toPlainText())) == 0:
                QMessageBox.warning(self, "ATTENZIONE", "Campo Descrizione \n Il campo non deve essere vuoto",
                                    QMessageBox.StandardButton.Ok)
                test = 1
        
        

        elif self.L=='de':
            if EC.data_is_empty(str(self.comboBox_sigla.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Abkürzung \n Das Feld darf nicht leer sein", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_sigla_estesa.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Erweitertes Abkürzungszeichen \n Das Feld darf nicht leer sein",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_tipologia_sigla.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Abkürzungtyp. \n Das Feld darf nicht leer sein",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_nome_tabella.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Tabellenname \n Das Feld darf nicht leer sein",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_lingua.currentText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Sprache \n Das Feld darf nicht leer sein",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.textEdit_descrizione_sigla.toPlainText())) == 0:
                QMessageBox.warning(self, "ACHTUNG", "Feld Beschreibung \n Das Feld darf nicht leer sein",
                                    QMessageBox.StandardButton.Ok)
                test = 1
        else:
            if EC.data_is_empty(str(self.comboBox_sigla.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Code Field \n The field must not be empty", QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_sigla_estesa.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Code whole field \n The field must not be empty",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_tipologia_sigla.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Code typology \n The field must not be empty",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_nome_tabella.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Table name \n The field must not be empty",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.comboBox_lingua.currentText())) == 0:
                QMessageBox.warning(self, "WARNING", "Language field \n The field must not be empty",
                                    QMessageBox.StandardButton.Ok)
                test = 1

            if EC.data_is_empty(str(self.textEdit_descrizione_sigla.toPlainText())) == 0:
                QMessageBox.warning(self, "WARNING", "Description field \n The field must not be empty",
                                    QMessageBox.StandardButton.Ok)
                test = 1        
        return test

    def insert_new_rec(self):
        try:
            # Get display name and convert to actual table name
            display_name = str(self.comboBox_nome_tabella.currentText())
            table_name = self.get_table_name_from_display(display_name)
            
            # Get hierarchy data if this is TMA material
            id_parent = None
            parent_sigla = None
            hierarchy_level = 0
            
            if table_name == 'tma_materiali_archeologici':
                tipologia = str(self.comboBox_tipologia_sigla.currentText())
                
                if tipologia == '10.7':  # Area
                    # Show dialog to select parent località
                    self.show_area_parent_dialog()
                    if hasattr(self, 'selected_localita_parent') and self.selected_localita_parent:
                        parent_sigla = self.selected_localita_parent
                    
                    if parent_sigla:
                        # Find parent ID - try multiple table name formats
                        lingua = str(self.comboBox_lingua.currentText())
                        
                        # Try with display name first
                        search_dict = {
                            'nome_tabella': display_name,
                            'sigla': parent_sigla,
                            'tipologia_sigla': "10.3",  # Località
                            'lingua': lingua
                        }
                        QgsMessageLog.logMessage(f"Searching for parent with: {search_dict}", "PyArchInit", Qgis.Info)
                        parent_records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                        QgsMessageLog.logMessage(f"Found {len(parent_records) if parent_records else 0} parent records", "PyArchInit", Qgis.Info)
                        
                        # If not found, try with lowercase table name (actual database format)
                        if not parent_records:
                            search_dict_lowercase = {
                                'nome_tabella': 'TMA materiali archeologici',
                                'sigla': parent_sigla,
                                'tipologia_sigla': "10.3",  # Località
                                'lingua': lingua
                            }
                            QgsMessageLog.logMessage(f"Trying with lowercase table name: {search_dict_lowercase}", "PyArchInit", Qgis.Info)
                            parent_records = self.DB_MANAGER.query_bool(search_dict_lowercase, self.MAPPER_TABLE_CLASS)
                            QgsMessageLog.logMessage(f"Found {len(parent_records) if parent_records else 0} parent records with lowercase", "PyArchInit", Qgis.Info)
                        
                        if parent_records:
                            id_parent = parent_records[0].id_thesaurus_sigle
                            QgsMessageLog.logMessage(f"Setting id_parent to: {id_parent}", "PyArchInit", Qgis.Info)
                        else:
                            QgsMessageLog.logMessage(f"No parent record found for sigla: {parent_sigla}", "PyArchInit", Qgis.Warning)
                            # Try without language constraint
                            search_dict_no_lang = {
                                'nome_tabella': 'TMA materiali archeologici',
                                'sigla': parent_sigla,
                                'tipologia_sigla': "10.3"  # Località
                            }
                            QgsMessageLog.logMessage(f"Trying search without language: {search_dict_no_lang}", "PyArchInit", Qgis.Info)
                            parent_records = self.DB_MANAGER.query_bool(search_dict_no_lang, self.MAPPER_TABLE_CLASS)
                            if parent_records:
                                id_parent = parent_records[0].id_thesaurus_sigle
                                QgsMessageLog.logMessage(f"Found parent without language constraint, setting id_parent to: {id_parent}", "PyArchInit", Qgis.Info)
                            else:
                                QgsMessageLog.logMessage(f"Still no parent record found for sigla: {parent_sigla}", "PyArchInit", Qgis.Warning)
                        hierarchy_level = 2
                        
                elif tipologia == '10.15':  # Settore
                    # Show dialog to select parent area
                    self.show_settore_parent_dialog()
                    if hasattr(self, 'selected_area_parent') and self.selected_area_parent:
                        parent_sigla = self.selected_area_parent
                        
                        if parent_sigla:
                            # Find parent ID - try multiple table name formats
                            lingua = str(self.comboBox_lingua.currentText())
                            
                            # Try with display name first
                            search_dict = {
                                'nome_tabella': display_name,
                                'sigla': parent_sigla,
                                'tipologia_sigla': "10.7",  # Area
                                'lingua': lingua
                            }
                            QgsMessageLog.logMessage(f"Searching for area parent with: {search_dict}", "PyArchInit", Qgis.Info)
                            parent_records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                            QgsMessageLog.logMessage(f"Found {len(parent_records) if parent_records else 0} area parent records", "PyArchInit", Qgis.Info)
                            
                            # If not found, try with lowercase table name (actual database format)
                            if not parent_records:
                                search_dict_lowercase = {
                                    'nome_tabella': 'TMA materiali archeologici',
                                    'sigla': parent_sigla,
                                    'tipologia_sigla': "10.7",  # Area
                                    'lingua': lingua
                                }
                                QgsMessageLog.logMessage(f"Trying area search with lowercase table name: {search_dict_lowercase}", "PyArchInit", Qgis.Info)
                                parent_records = self.DB_MANAGER.query_bool(search_dict_lowercase, self.MAPPER_TABLE_CLASS)
                                QgsMessageLog.logMessage(f"Found {len(parent_records) if parent_records else 0} area parent records with lowercase", "PyArchInit", Qgis.Info)
                            
                            if parent_records:
                                id_parent = parent_records[0].id_thesaurus_sigle
                                QgsMessageLog.logMessage(f"Setting id_parent to: {id_parent}", "PyArchInit", Qgis.Info)
                            else:
                                QgsMessageLog.logMessage(f"No area parent record found for sigla: {parent_sigla}", "PyArchInit", Qgis.Warning)
                                # Try without language constraint
                                search_dict_no_lang = {
                                    'nome_tabella': 'TMA materiali archeologici',
                                    'sigla': parent_sigla,
                                    'tipologia_sigla': "10.7"  # Area
                                }
                                QgsMessageLog.logMessage(f"Trying area search without language: {search_dict_no_lang}", "PyArchInit", Qgis.Info)
                                parent_records = self.DB_MANAGER.query_bool(search_dict_no_lang, self.MAPPER_TABLE_CLASS)
                                if parent_records:
                                    id_parent = parent_records[0].id_thesaurus_sigle
                                    QgsMessageLog.logMessage(f"Found area parent without language constraint, setting id_parent to: {id_parent}", "PyArchInit", Qgis.Info)
                                else:
                                    QgsMessageLog.logMessage(f"Still no area parent record found for sigla: {parent_sigla}", "PyArchInit", Qgis.Warning)
                            hierarchy_level = 3
            
            # Create data with hierarchy fields - use display name for nome_tabella
            data = self.DB_MANAGER.insert_values_thesaurus(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                display_name,  # 1 - nome tabella (use display name/alias)
                str(self.comboBox_sigla.currentText()),  # 2 - sigla
                str(self.comboBox_sigla_estesa.currentText()),  # 3 - sigla estesa
                str(self.textEdit_descrizione_sigla.toPlainText()),  # 4 - descrizione
                str(self.comboBox_tipologia_sigla.currentText()),  # 5 - tipologia sigla
                str(self.comboBox_lingua.currentText()),  # 6 - lingua
                0,  # 7 - order_layer (default)
                id_parent,  # 8 - id_parent
                parent_sigla,  # 9 - parent_sigla
                hierarchy_level)  # 10 - hierarchy_level

            try:
                self.DB_MANAGER.insert_data_session(data)
                
                # Check if this field should be synchronized
                sigla = str(self.comboBox_sigla.currentText())
                sigla_estesa = str(self.comboBox_sigla_estesa.currentText())
                descrizione = str(self.textEdit_descrizione_sigla.toPlainText())
                tipologia_sigla = str(self.comboBox_tipologia_sigla.currentText())
                lingua = str(self.comboBox_lingua.currentText())
                
                # Synchronize if needed
                self.synchronize_field_values(sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, display_name)
                
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
    
    def check_synchronized_field(self, sigla_estesa, tipologia_sigla, table_name):
        """Check if this field should be synchronized across tables"""
        # Convert display name to actual table name for comparison
        actual_table_name = self.get_table_name_from_display(table_name)
        for field_name, table_list in self.SYNCHRONIZED_FIELDS.items():
            for table, code in table_list:
                if table == actual_table_name and code == tipologia_sigla:
                    # This is a synchronized field
                    return field_name, table_list
        return None, None
    
    def synchronize_field_values(self, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, table_name):
        """Synchronize field values across all related tables"""
        field_name, table_list = self.check_synchronized_field(sigla_estesa, tipologia_sigla, table_name)
        
        if field_name and table_list:
            # This is a synchronized field - propagate to all related tables
            sync_count = 0
            errors = []
            actual_table_name = self.get_table_name_from_display(table_name)
            
            for target_table, target_code in table_list:
                if target_table != actual_table_name:  # Don't sync to the same table
                    try:
                        # Convert target table to display name
                        target_display_name = self.get_display_name_from_table(target_table)
                        
                        # Check if record already exists
                        search_dict = {
                            'nome_tabella': "'" + target_display_name + "'",
                            'sigla': "'" + sigla + "'",
                            'tipologia_sigla': "'" + target_code + "'",
                            'lingua': "'" + lingua + "'"
                        }
                        existing = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                        
                        if not existing:
                            # Insert new synchronized record using display name
                            data = self.DB_MANAGER.insert_values_thesaurus(
                                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                                target_display_name,  # Use display name
                                sigla,
                                sigla_estesa,
                                descrizione + " [Sincronizzato da " + table_name + "]",
                                target_code,
                                lingua
                            )
                            self.DB_MANAGER.insert_data_session(data)
                            sync_count += 1
                        else:
                            # Update existing record
                            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                                 self.ID_TABLE,
                                                 [existing[0].id_thesaurus_sigle],
                                                 ['sigla_estesa', 'descrizione'],
                                                 [sigla_estesa, descrizione + " [Sincronizzato da " + table_name + "]"])
                            sync_count += 1
                    except Exception as e:
                        errors.append("Errore sincronizzazione con " + self.get_display_name_from_table(target_table) + ": " + str(e))
            
            # Report results
            if sync_count > 0:
                if self.L == 'it':
                    msg = f"Campo '{field_name}' sincronizzato su {sync_count} tabelle"
                elif self.L == 'de':
                    msg = f"Feld '{field_name}' auf {sync_count} Tabellen synchronisiert"
                else:
                    msg = f"Field '{field_name}' synchronized to {sync_count} tables"
                
                if errors:
                    msg += "\n\nErrori:\n" + "\n".join(errors)
                
                QMessageBox.information(self, "Sincronizzazione", msg, QMessageBox.StandardButton.Ok)
    
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
                    QMessageBox.warning(self, "Messagge!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Achtung", "Die Datenbank ist leer!", QMessageBox.StandardButton.Ok)
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
        else:
            msg = QMessageBox.warning(self, "Warning!!!",
                                      "Do you really want to break the record? \n Action is irreversible.",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
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
            
            
            
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

    def on_pushButton_sigle_pressed(self):
        """Load thesaurus codes documentation in webView_adarte"""
        filepath = os.path.dirname(__file__)
        # Map language codes to file names
        lang_files = {
            'it': 'codici_it.html',
            'de': 'codici_de.html',
            'en': 'codici_en.html',
            'es': 'codici_es.html',
            'fr': 'codici_fr.html',
            'ar': 'codici_ar.html',
            'ca': 'codici_ca.html',
        }
        # Get the file for current language, default to English
        filename = lang_files.get(self.L, 'codici_en.html')
        filepath = os.path.join(filepath, filename)
        # Check if file exists, fallback to English if not
        if not os.path.exists(filepath):
            filepath = os.path.join(os.path.dirname(__file__), 'codici_en.html')
        # Read HTML content and display in webView_adarte
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.webView_adarte.setHtml(html_content)
            self.webView_adarte.show()
        except Exception as e:
            QMessageBox.warning(self, "Thesaurus", f"Errore nel caricamento: {str(e)}", QMessageBox.StandardButton.Ok)
    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)

            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                ###
                self.setComboBoxEditable(["self.comboBox_sigla"], 1)
                self.setComboBoxEditable(["self.comboBox_sigla_estesa"], 1)
                self.setComboBoxEditable(["self.comboBox_tipologia_sigla"], 1)
                self.setComboBoxEditable(["self.comboBox_nome_tabella"], 1)
                self.setComboBoxEditable(["self.comboBox_lingua"], 1)

                self.setComboBoxEnable(["self.comboBox_sigla"], "True")
                self.setComboBoxEnable(["self.comboBox_sigla_estesa"], "True")
                self.setComboBoxEnable(["self.comboBox_tipologia_sigla"], "True")
                self.setComboBoxEnable(["self.comboBox_nome_tabella"], "True")
                self.setComboBoxEnable(["self.comboBox_lingua"], "True")

                self.setComboBoxEnable(["self.textEdit_descrizione_sigla"], "False")
                ###
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()

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
            # Convert display name to actual table name for search
            table_name = self.get_table_name_from_display(str(self.comboBox_nome_tabella.currentText()))
            search_dict = {
                self.TABLE_FIELDS[0]: "'" + table_name + "'",  # 1 - Nome tabella
                self.TABLE_FIELDS[1]: "'" + str(self.comboBox_sigla.currentText()) + "'",  # 2 - sigla
                self.TABLE_FIELDS[2]: "'" + str(self.comboBox_sigla_estesa.currentText()) + "'",  # 3 - sigla estesa
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_tipologia_sigla.currentText()) + "'",
                self.TABLE_FIELDS[5]: "'" + str(self.comboBox_lingua.currentText()) + "'"
                # 3 - tipologia sigla
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
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stato trovato nessun record!", QMessageBox.StandardButton.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Keinen Record gefunden!", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.StandardButton.Ok) 

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEditable(["self.comboBox_sigla"], 1)
                    self.setComboBoxEditable(["self.comboBox_sigla_estesa"], 1)
                    self.setComboBoxEditable(["self.comboBox_tipologia_sigla"], 1)
                    self.setComboBoxEditable(["self.comboBox_nome_tabella"], 1)
                    self.setComboBoxEditable(["self.comboBox_lingua"], 1)

                    self.setComboBoxEnable(["self.comboBox_sigla"], "False")
                    self.setComboBoxEnable(["self.comboBox_sigla_estesa"], "False")
                    self.setComboBoxEnable(["self.comboBox_tipologia_sigla"], "False")
                    self.setComboBoxEnable(["self.comboBox_nome_tabella"], "False")
                    self.setComboBoxEnable(["self.comboBox_lingua"], "False")

                    self.setComboBoxEnable(["self.textEdit_descrizione_sigla"], "True")

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

                    if self.L=='it':
                        if self.REC_TOT == 1:
                            strings = ("E' stato trovato", self.REC_TOT, "record")
                        else:
                            strings = ("Sono stati trovati", self.REC_TOT, "records")
                    elif self.L=='de':
                        if self.REC_TOT == 1:
                            strings = ("Es wurde gefunden", self.REC_TOT, "record")
                        else:
                            strings = ("Sie wurden gefunden", self.REC_TOT, "records")
                    else:
                        if self.REC_TOT == 1:
                            strings = ("It has been found", self.REC_TOT, "record")
                        else:
                            strings = ("They have been found", self.REC_TOT, "records")

                        self.setComboBoxEditable(["self.comboBox_sigla"], 1)
                        self.setComboBoxEditable(["self.comboBox_sigla_estesa"], 1)
                        self.setComboBoxEditable(["self.comboBox_tipologia_sigla"], 1)
                        self.setComboBoxEditable(["self.comboBox_nome_tabella"], 1)
                        self.setComboBoxEditable(["self.comboBox_lingua"], 1)

                        self.setComboBoxEnable(["self.comboBox_sigla"], "False")
                        self.setComboBoxEnable(["self.comboBox_sigla_estesa"], "False")
                        self.setComboBoxEnable(["self.comboBox_tipologia_sigla"], "False")
                        self.setComboBoxEnable(["self.comboBox_nome_tabella"], "False")
                        self.setComboBoxEnable(["self.comboBox_lingua"], "False")

                        self.setComboBoxEnable(["self.textEdit_descrizione_sigla"], "True")

                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.StandardButton.Ok)

        self.enable_button_search(1)

    def on_pushButton_test_pressed(self):
        pass

    ##      data = "Sito: " + str(self.comboBox_sito.currentText())
    ##
    ##      test = Test_area(data)
    ##      test.run_test()

    def on_pushButton_draw_pressed(self):
        pass

        # self.pyQGIS.charge_layers_for_draw(["1", "2", "3", "4", "5", "7", "8", "9", "10", "12"])

    def on_pushButton_sites_geometry_pressed(self):
        pass

    ##      sito = unicode(self.comboBox_sito.currentText())
    ##      self.pyQGIS.charge_sites_geometry(["1", "2", "3", "4", "8"], "sito", sito)

    def on_pushButton_sync_tma_thesaurus_pressed(self):
        """Sincronizza il thesaurus TMA con inventario materiali e aree"""
        try:
            # Import the sync module
            from ..modules.utility.pyarchinit_tma_thesaurus_sync import TMAThesaurusSync
            
            # Ask user which sync direction they want
            from qgis.PyQt.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Direzione Sincronizzazione")
            msg.setText("Scegli la direzione della sincronizzazione:")
            msg.setInformativeText("Da Tabelle verso Thesaurus: sincronizza i dati esistenti nelle tabelle verso il thesaurus\n\n"
                                   "Da TMA verso altre tabelle: copia le voci predefinite del thesaurus TMA verso US e Inventario")
            
            btn_to_thesaurus = msg.addButton("Da Tabelle → Thesaurus", QMessageBox.ButtonRole.AcceptRole)
            btn_from_tma = msg.addButton("Da TMA → Altre tabelle", QMessageBox.ButtonRole.AcceptRole)
            msg.addButton(QMessageBox.StandardButton.Cancel)
            
            msg.exec()
            
            if msg.clickedButton() == btn_to_thesaurus:
                # Original sync: from tables to thesaurus
                self._sync_tables_to_thesaurus()
            elif msg.clickedButton() == btn_from_tma:
                # New sync: from TMA thesaurus to other tables
                self._sync_tma_to_other_tables()
                
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sincronizzazione: {str(e)}", "PyArchInit", Qgis.Critical)
            QMessageBox.critical(self, "Errore", f"Errore durante la sincronizzazione:\n{str(e)}")
    
    def _sync_tables_to_thesaurus(self):
        """Sincronizza dai dati delle tabelle verso il thesaurus"""
        try:
            from ..modules.utility.pyarchinit_tma_thesaurus_sync import TMAThesaurusSync
            from qgis.PyQt.QtWidgets import QProgressDialog
            
            progress = QProgressDialog("Sincronizzazione in corso...", "Annulla", 0, 100, self)
            progress.setWindowTitle("Sincronizzazione Tabelle → Thesaurus")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            
            sync = TMAThesaurusSync(self.DB_MANAGER)
            
            # Step 1: Sync all areas from all tables
            progress.setLabelText("Sincronizzazione aree da tutte le tabelle...")
            progress.setValue(20)
            QApplication.processEvents()
            
            if not progress.wasCanceled():
                sync.sync_all_areas_to_thesaurus()
            
            # Step 2: Sync all settori from us_table and tma
            progress.setLabelText("Sincronizzazione settori...")
            progress.setValue(50)
            QApplication.processEvents()
            
            if not progress.wasCanceled():
                sync.sync_all_settori_to_thesaurus()
            
            # Step 3: Sync inventory materials
            progress.setLabelText("Sincronizzazione materiali da inventario...")
            progress.setValue(70)
            QApplication.processEvents()
            
            if not progress.wasCanceled():
                sync.sync_all_inventory_to_thesaurus()
            
            progress.setValue(90)
            
            # Reload thesaurus data
            self.charge_records()
            self.fill_fields()
            
            progress.close()
            
            if self.L == 'it':
                QMessageBox.information(self, "Completato", "Sincronizzazione completata!")
            else:
                QMessageBox.information(self, "Complete", "Synchronization complete!")
                
        except Exception as e:
            progress.close()
            QgsMessageLog.logMessage(f"Errore sync tables to thesaurus: {str(e)}", "PyArchInit", Qgis.Critical)
            QMessageBox.critical(self, "Errore", f"Errore durante la sincronizzazione:\n{str(e)}")
    
    def _sync_tma_to_other_tables(self):
        """Sincronizza dal thesaurus TMA verso le altre tabelle"""
        try:
            from ..modules.utility.pyarchinit_tma_thesaurus_sync import TMAThesaurusSync
            from qgis.PyQt.QtWidgets import QProgressDialog
            
            progress = QProgressDialog("Sincronizzazione in corso...", "Annulla", 0, 100, self)
            progress.setWindowTitle("Sincronizzazione TMA → Altre Tabelle")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            
            sync = TMAThesaurusSync(self.DB_MANAGER)
            
            # Step 1: Sync TMA areas to US and other tables
            progress.setLabelText("Sincronizzazione aree TMA verso US...")
            progress.setValue(30)
            QApplication.processEvents()
            
            areas_synced = 0
            if not progress.wasCanceled():
                areas_synced = sync.sync_tma_thesaurus_to_other_tables()
            
            # Step 2: Sync TMA materials to inventory
            progress.setLabelText("Sincronizzazione materiali TMA verso Inventario...")
            progress.setValue(60)
            QApplication.processEvents()
            
            materials_synced = 0
            if not progress.wasCanceled():
                materials_synced = sync.sync_tma_materials_to_inventory()
            
            progress.setValue(90)
            
            # Reload thesaurus data
            if not progress.wasCanceled():
                progress.setLabelText("Ricaricamento dati...")
                self.charge_records()
                self.charge_list()
                self.fill_fields()
            
            progress.close()
            
            # Show results
            msg_text = f"Sincronizzazione completata!\n\n"
            msg_text += f"Aree sincronizzate da TMA verso US: {areas_synced}\n"
            msg_text += f"Valori materiali sincronizzati: {materials_synced}"
            
            if self.L == 'it':
                QMessageBox.information(self, "Completato", msg_text)
            else:
                msg_text = f"Synchronization complete!\n\n"
                msg_text += f"Areas synced from TMA to US: {areas_synced}\n"
                msg_text += f"Material values synced: {materials_synced}"
                QMessageBox.information(self, "Complete", msg_text)
                
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            QgsMessageLog.logMessage(f"Errore sync TMA to other tables: {str(e)}", "PyArchInit", Qgis.Critical)
            QMessageBox.critical(self, "Errore", f"Errore durante la sincronizzazione:\n{str(e)}")
            
    def on_pushButton_rel_pdf_pressed(self):
        pass

    ##      check=QMessageBox.warning(self, "Attention", "Under testing: this method can contains some bugs. Do you want proceed?",QMessageBox.Cancel,1)
    ##      if check == 1:
    ##          erp = exp_rel_pdf(unicode(self.comboBox_sito.currentText()))
    ##          erp.export_rel_pdf()

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
        # Single ordered query - replaces double query pattern for better performance
        self.DATA_LIST = self.DB_MANAGER.query_ordered(self.MAPPER_TABLE_CLASS, self.ID_TABLE, 'asc')

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

    def empty_fields(self):
        self.comboBox_sigla.setEditText("")  # 1 - Sigla
        self.comboBox_sigla_estesa.setEditText("")  # 2 - Sigla estesa
        self.comboBox_tipologia_sigla.setEditText("")  # 1 - Tipologia sigla
        self.comboBox_nome_tabella.setEditText("")  # 2 - Nome tabella
        self.textEdit_descrizione_sigla.clear()  # 4 - Descrizione
        self.comboBox_lingua.setEditText("")

    def fill_fields(self, n=0):
        self.rec_num = n

        str(self.comboBox_sigla.setEditText(self.DATA_LIST[self.rec_num].sigla))  # 1 - Sigla
        str(self.comboBox_sigla_estesa.setEditText(self.DATA_LIST[self.rec_num].sigla_estesa))  # 2 - Sigla estesa
        str(self.comboBox_tipologia_sigla.setEditText(
            self.DATA_LIST[self.rec_num].tipologia_sigla))  # 3 - tipologia sigla
        # Convert table name to display name when loading
        display_name = self.get_display_name_from_table(self.DATA_LIST[self.rec_num].nome_tabella)
        str(self.comboBox_nome_tabella.setEditText(display_name))  # 4 - nome tabella
        str(str(
            self.textEdit_descrizione_sigla.setText(self.DATA_LIST[self.rec_num].descrizione)))  # 5 - descrizione sigla
        str(self.comboBox_lingua.setEditText(self.DATA_LIST[self.rec_num].lingua))  # 6 - lingua
        
        # Handle hierarchy fields for TMA materials
        if hasattr(self.DATA_LIST[self.rec_num], 'parent_sigla') and self.DATA_LIST[self.rec_num].parent_sigla:
            # Let the tipologia change handler create the widgets and populate them
            # This will trigger on_comboBox_tipologia_sigla_currentIndexChanged which creates the widgets
            # Then we need to set the parent values
            QTimer.singleShot(100, lambda: self._restore_parent_selections(n))
    
    def _restore_parent_selections(self, n):
        """Restore parent selections after widgets are created."""
        try:
            record = self.DATA_LIST[n]
            table_name = record.nome_tabella
            tipologia = record.tipologia_sigla
            
            if table_name == 'TMA materiali archeologici' and hasattr(record, 'parent_sigla') and record.parent_sigla:
                if tipologia == '10.7' and hasattr(self, 'comboBox_parent_localita'):  # Area
                    # Find and select the parent località
                    for i in range(self.comboBox_parent_localita.count()):
                        if self.comboBox_parent_localita.itemText(i).startswith(record.parent_sigla + ' - '):
                            self.comboBox_parent_localita.setCurrentIndex(i)
                            break
                elif tipologia == '10.15' and hasattr(self, 'comboBox_parent_area'):  # Settore
                    # Find and select the parent area
                    for i in range(self.comboBox_parent_area.count()):
                        if self.comboBox_parent_area.itemText(i).startswith(record.parent_sigla + ' - '):
                            self.comboBox_parent_area.setCurrentIndex(i)
                            break
                    # Also need to populate the parent località combobox
                    if hasattr(self, 'comboBox_parent_localita') and record.hierarchy_level >= 2:
                        # Get the parent area's parent (località)
                        search_dict = {
                            'nome_tabella': "'" + table_name + "'",
                            'sigla': "'" + record.parent_sigla + "'",
                            'tipologia_sigla': "'10.7'"
                        }
                        parent_area = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                        if parent_area and hasattr(parent_area[0], 'parent_sigla') and parent_area[0].parent_sigla:
                            for i in range(self.comboBox_parent_localita.count()):
                                if self.comboBox_parent_localita.itemText(i).startswith(parent_area[0].parent_sigla + ' - '):
                                    self.comboBox_parent_localita.setCurrentIndex(i)
                                    break
        except Exception as e:
            QgsMessageLog.logMessage(f"Error restoring parent selections: {e}", "PyArchInit", Qgis.Warning)

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        # Get lingua - use the text directly from combobox (it should match what's in DB)
        lingua = str(self.comboBox_lingua.currentText())

        # data - Convert display name to actual table name
        table_name = self.get_table_name_from_display(str(self.comboBox_nome_tabella.currentText()))
        
        # Get hierarchy data if this is TMA material
        id_parent = None
        parent_sigla = None
        hierarchy_level = None
        order_layer = None

        if self.DATA_LIST and self.REC_CORR < len(self.DATA_LIST):
            # Get existing values from record
            current_record = self.DATA_LIST[self.REC_CORR]
            order_layer = getattr(current_record, 'order_layer', None)
            id_parent = getattr(current_record, 'id_parent', None)
            parent_sigla = getattr(current_record, 'parent_sigla', None)
            hierarchy_level = getattr(current_record, 'hierarchy_level', None)
            
            # Update if hierarchy widgets are visible and this is TMA
            if table_name == 'TMA materiali archeologici' and hasattr(self, 'comboBox_parent_localita'):
                tipologia = str(self.comboBox_tipologia_sigla.currentText())
                
                if tipologia == '10.7':  # Area
                    # Get parent località from combobox
                    if hasattr(self, 'comboBox_parent_localita') and self.comboBox_parent_localita.currentText():
                        parent_text = self.comboBox_parent_localita.currentText()
                        if ' - ' in parent_text:
                            parent_sigla = parent_text.split(' - ')[0]
                        # Find parent ID
                        search_dict = {
                            'nome_tabella': "'" + table_name + "'",
                            'sigla': "'" + parent_sigla + "'",
                            'tipologia_sigla': "'10.3'"  # Località
                        }
                        parent_records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                        if parent_records:
                            id_parent = parent_records[0].id_thesaurus_sigle
                        hierarchy_level = 1
                elif tipologia == '10.15':  # Settore
                    # Get parent area from combobox
                    if hasattr(self, 'comboBox_parent_area') and self.comboBox_parent_area.currentText():
                        parent_text = self.comboBox_parent_area.currentText()
                        if ' - ' in parent_text:
                            parent_sigla = parent_text.split(' - ')[0]
                        # Find parent ID
                        search_dict = {
                            'nome_tabella': "'" + table_name + "'",
                            'sigla': "'" + parent_sigla + "'",
                            'tipologia_sigla': "'10.7'"  # Area
                        }
                        parent_records = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                        if parent_records:
                            id_parent = parent_records[0].id_thesaurus_sigle
                        hierarchy_level = 2
        
        self.DATA_LIST_REC_TEMP = [
            table_name,  # 1 - Nome tabella
            str(self.comboBox_sigla.currentText()),  # 2 - sigla
            str(self.comboBox_sigla_estesa.currentText()),  # 3 - sigla estesa
            str(self.textEdit_descrizione_sigla.toPlainText()),  # 4 - descrizione
            str(self.comboBox_tipologia_sigla.currentText()),  # 5 - tipologia sigla
            str(lingua),  # 6 - lingua
            str(order_layer) if order_layer is not None else 'None',  # 7 - order_layer (integer)
            str(id_parent) if id_parent is not None else 'None',  # 8 - id_parent (integer)
            str(parent_sigla) if parent_sigla else 'None',  # 9 - parent_sigla (text)
            str(hierarchy_level) if hierarchy_level is not None else 'None'  # 10 - hierarchy_level (integer)
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            value = getattr(self.DATA_LIST[self.REC_CORR], i, None)
            # Convert None to 'None' string (for pos_none_in_list compatibility)
            if value is None:
                value = 'None'
            self.DATA_LIST_REC_CORR.append(str(value))

    def setComboBoxEnable(self, f, v):
        """Set enabled state for widgets - uses getattr instead of eval for security"""
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEnabled(v == "True" or v is True)

    def setComboBoxEditable(self, f, n):
        """Set editable state for widgets - uses getattr instead of eval for security"""
        for fn in f:
            widget_name = fn.replace('self.' , '') if fn.startswith('self.' ) else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def records_equal_check(self):
        # If we're in new record mode, there's nothing to compare
        if self.BROWSE_STATUS == "n":
            return 0
            
        # If no data list, nothing to compare
        if not self.DATA_LIST:
            return 0
            
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1

    def update_record(self):
        try:
            # Get current record data before update
            current_record = self.DATA_LIST[self.REC_CORR]
            old_sigla = current_record.sigla
            old_tipologia = current_record.tipologia_sigla
            old_lingua = current_record.lingua
            old_table = current_record.nome_tabella
            
            # Perform the update
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [int(getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE))],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            
            # Check if this was a synchronized field that was updated
            new_sigla = str(self.comboBox_sigla.currentText())
            new_sigla_estesa = str(self.comboBox_sigla_estesa.currentText())
            new_descrizione = str(self.textEdit_descrizione_sigla.toPlainText())
            new_tipologia = str(self.comboBox_tipologia_sigla.currentText())
            new_lingua = str(self.comboBox_lingua.currentText())
            table_name = self.get_table_name_from_display(str(self.comboBox_nome_tabella.currentText()))
            
            # If the sigla_estesa changed, check if we need to synchronize
            if old_sigla == new_sigla and old_tipologia == new_tipologia and old_lingua == new_lingua and old_table == table_name:
                # Same field, just value update - synchronize
                self.synchronize_field_values(new_sigla, new_sigla_estesa, new_descrizione, new_tipologia, new_lingua, table_name)
            
            return 1
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_traceback = traceback.format_exc()

            # Print to console for debugging
            print(f"[Thesaurus] Update error: {error_msg}")
            print(f"[Thesaurus] Traceback: {error_traceback}")

            save_file = os.path.join(self.HOME, "pyarchinit_Report_folder")
            if not os.path.exists(save_file):
                os.makedirs(save_file)
            file_ = os.path.join(save_file, 'error_encoding_data_recover.txt')
            with open(file_, "a", encoding='utf-8') as fh:
                fh.write(f"\n--- Error at {str(datetime.now())} ---\n")
                fh.write(f"Error: {error_msg}\n")
                fh.write(f"Traceback: {error_traceback}\n")
                fh.write(f"DATA_LIST_REC_TEMP: {self.DATA_LIST_REC_TEMP}\n")

            if self.L == 'it':
                QMessageBox.warning(self, "Messaggio",
                                    f"Errore durante l'aggiornamento: {error_msg}\n\nDettagli salvati in pyarchinit_Report_folder", QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Nachricht",
                                    f"Fehler beim Aktualisieren: {error_msg}\n\nDetails im pyarchinit_Report_Ordner gespeichert", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    f"Error during update: {error_msg}\n\nDetails saved in pyarchinit_Report_folder", QMessageBox.StandardButton.Ok)
            return 0

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()


# ## Class end
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     ui = pyarchinit_US()
#     ui.show()
#     sys.exit(app.exec())
