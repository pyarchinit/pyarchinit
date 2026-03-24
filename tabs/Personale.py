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
from qgis.PyQt.QtCore import QDate, QTimer
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings

from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from ..gui.sortpanelmain import SortPanelMain
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.pyarchinit_theme_manager import ThemeManager

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Personale.ui'))


class pyarchinit_Personale(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Scheda Personale"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Personnel Form"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Personalformular"
    elif L == 'es':
        MSG_BOX_TITLE = "PyArchInit - Personal de Obra"
    elif L == 'fr':
        MSG_BOX_TITLE = "PyArchInit - Personnel de Chantier"
    elif L == 'ar':
        MSG_BOX_TITLE = "PyArchInit - موظفو الموقع"
    elif L == 'ca':
        MSG_BOX_TITLE = "PyArchInit - Personal d'Obra"
    elif L == 'ro':
        MSG_BOX_TITLE = "PyArchInit - Personal Șantier"
    elif L == 'pt':
        MSG_BOX_TITLE = "PyArchInit - Pessoal de Obra"
    elif L == 'el':
        MSG_BOX_TITLE = "PyArchInit - Προσωπικό Εργοταξίου"
    else:
        MSG_BOX_TITLE = "PyArchInit - Personnel Form"

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    SITO = pyArchInitDialog_Config

    if L == 'it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    elif L == 'de':
        STATUS_ITEMS = {"b": "Aktuell", "f": "Finden", "n": "Neuer Rekord"}
    elif L == 'es':
        STATUS_ITEMS = {"b": "navegar", "f": "buscar", "n": "nuevo registro"}
    elif L == 'fr':
        STATUS_ITEMS = {"b": "parcourir", "f": "rechercher", "n": "nouveau"}
    elif L == 'ar':
        STATUS_ITEMS = {"b": "تصفح", "f": "بحث", "n": "جديد"}
    elif L == 'ca':
        STATUS_ITEMS = {"b": "navegar", "f": "cercar", "n": "nou registre"}
    elif L == 'ro':
        STATUS_ITEMS = {"b": "navigare", "f": "căutare", "n": "înregistrare nouă"}
    elif L == 'pt':
        STATUS_ITEMS = {"b": "navegar", "f": "pesquisar", "n": "novo registo"}
    elif L == 'el':
        STATUS_ITEMS = {"b": "περιήγηση", "f": "αναζήτηση", "n": "νέα εγγραφή"}
    else:
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}

    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'

    if L == 'it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    elif L == 'de':
        SORTED_ITEMS = {"n": "Nicht sortiert", "o": "Sortiert"}
    elif L == 'es':
        SORTED_ITEMS = {"n": "No ordenados", "o": "Ordenados"}
    elif L == 'fr':
        SORTED_ITEMS = {"n": "Non triés", "o": "Triés"}
    elif L == 'ar':
        SORTED_ITEMS = {"n": "غير مرتب", "o": "مرتب"}
    elif L == 'ca':
        SORTED_ITEMS = {"n": "No ordenats", "o": "Ordenats"}
    elif L == 'ro':
        SORTED_ITEMS = {"n": "Nesortat", "o": "Sortat"}
    elif L == 'pt':
        SORTED_ITEMS = {"n": "Não ordenados", "o": "Ordenados"}
    elif L == 'el':
        SORTED_ITEMS = {"n": "Μη ταξινομημένα", "o": "Ταξινομημένα"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}

    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'personale_table'
    MAPPER_TABLE_CLASS = "PERSONALE"
    NOME_SCHEDA = "Scheda Personale"
    ID_TABLE = "id_personale"

    if L == 'it':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sito": "sito",
            "Nome": "nome",
            "Cognome": "cognome",
            "Ruolo": "ruolo",
            "Qualifica": "qualifica",
            "Codice Fiscale": "codice_fiscale",
            "Email": "email",
            "Telefono": "telefono",
            "Data di nascita": "data_nascita",
            "Indirizzo": "indirizzo",
            "Tipo contratto": "tipo_contratto",
            "Inizio contratto": "data_inizio_contratto",
            "Fine contratto": "data_fine_contratto",
            "Tariffa oraria": "tariffa_oraria",
            "Tariffa giornaliera": "tariffa_giornaliera",
            "IBAN": "iban",
            "Note": "note",
            "Attivo": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sito",
            "Nome",
            "Cognome",
            "Ruolo",
            "Tipo contratto",
            "Attivo"
        ]
    elif L == 'en':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "First Name": "nome",
            "Last Name": "cognome",
            "Role": "ruolo",
            "Qualification": "qualifica",
            "Tax Code": "codice_fiscale",
            "Email": "email",
            "Phone": "telefono",
            "Date of Birth": "data_nascita",
            "Address": "indirizzo",
            "Contract Type": "tipo_contratto",
            "Contract Start": "data_inizio_contratto",
            "Contract End": "data_fine_contratto",
            "Hourly Rate": "tariffa_oraria",
            "Daily Rate": "tariffa_giornaliera",
            "IBAN": "iban",
            "Notes": "note",
            "Active": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "First Name",
            "Last Name",
            "Role",
            "Contract Type",
            "Active"
        ]
    elif L == 'de':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Fundort": "sito",
            "Vorname": "nome",
            "Nachname": "cognome",
            "Rolle": "ruolo",
            "Qualifikation": "qualifica",
            "Steuernummer": "codice_fiscale",
            "Email": "email",
            "Telefon": "telefono",
            "Geburtsdatum": "data_nascita",
            "Adresse": "indirizzo",
            "Vertragsart": "tipo_contratto",
            "Vertragsbeginn": "data_inizio_contratto",
            "Vertragsende": "data_fine_contratto",
            "Stundensatz": "tariffa_oraria",
            "Tagessatz": "tariffa_giornaliera",
            "IBAN": "iban",
            "Anmerkungen": "note",
            "Aktiv": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Fundort",
            "Vorname",
            "Nachname",
            "Rolle",
            "Vertragsart",
            "Aktiv"
        ]
    elif L == 'es':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Nombre": "nome",
            "Apellido": "cognome",
            "Rol": "ruolo",
            "Cualificacion": "qualifica",
            "Codigo Fiscal": "codice_fiscale",
            "Email": "email",
            "Telefono": "telefono",
            "Fecha de nacimiento": "data_nascita",
            "Direccion": "indirizzo",
            "Tipo de contrato": "tipo_contratto",
            "Inicio contrato": "data_inizio_contratto",
            "Fin contrato": "data_fine_contratto",
            "Tarifa horaria": "tariffa_oraria",
            "Tarifa diaria": "tariffa_giornaliera",
            "IBAN": "iban",
            "Notas": "note",
            "Activo": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Nombre",
            "Apellido",
            "Rol",
            "Tipo de contrato",
            "Activo"
        ]
    elif L == 'fr':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "Prenom": "nome",
            "Nom": "cognome",
            "Role": "ruolo",
            "Qualification": "qualifica",
            "Code fiscal": "codice_fiscale",
            "Email": "email",
            "Telephone": "telefono",
            "Date de naissance": "data_nascita",
            "Adresse": "indirizzo",
            "Type de contrat": "tipo_contratto",
            "Debut du contrat": "data_inizio_contratto",
            "Fin du contrat": "data_fine_contratto",
            "Tarif horaire": "tariffa_oraria",
            "Tarif journalier": "tariffa_giornaliera",
            "IBAN": "iban",
            "Notes": "note",
            "Actif": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "Prenom",
            "Nom",
            "Role",
            "Type de contrat",
            "Actif"
        ]
    elif L == 'ar':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "موقع": "sito",
            "الاسم": "nome",
            "اللقب": "cognome",
            "الدور": "ruolo",
            "المؤهل": "qualifica",
            "الرمز الضريبي": "codice_fiscale",
            "البريد الإلكتروني": "email",
            "الهاتف": "telefono",
            "تاريخ الميلاد": "data_nascita",
            "العنوان": "indirizzo",
            "نوع العقد": "tipo_contratto",
            "بداية العقد": "data_inizio_contratto",
            "نهاية العقد": "data_fine_contratto",
            "الأجر بالساعة": "tariffa_oraria",
            "الأجر اليومي": "tariffa_giornaliera",
            "IBAN": "iban",
            "ملاحظات": "note",
            "نشط": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "موقع",
            "الاسم",
            "اللقب",
            "الدور",
            "نوع العقد",
            "نشط"
        ]
    elif L == 'ca':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Jaciment": "sito",
            "Nom": "nome",
            "Cognom": "cognome",
            "Rol": "ruolo",
            "Qualificacio": "qualifica",
            "Codi Fiscal": "codice_fiscale",
            "Email": "email",
            "Telefon": "telefono",
            "Data de naixement": "data_nascita",
            "Adreca": "indirizzo",
            "Tipus de contracte": "tipo_contratto",
            "Inici contracte": "data_inizio_contratto",
            "Fi contracte": "data_fine_contratto",
            "Tarifa horaria": "tariffa_oraria",
            "Tarifa diaria": "tariffa_giornaliera",
            "IBAN": "iban",
            "Notes": "note",
            "Actiu": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Jaciment",
            "Nom",
            "Cognom",
            "Rol",
            "Tipus de contracte",
            "Actiu"
        ]
    elif L == 'ro':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sit": "sito",
            "Prenume": "nome",
            "Nume": "cognome",
            "Rol": "ruolo",
            "Calificare": "qualifica",
            "Cod fiscal": "codice_fiscale",
            "Email": "email",
            "Telefon": "telefono",
            "Data nasterii": "data_nascita",
            "Adresa": "indirizzo",
            "Tip contract": "tipo_contratto",
            "Inceput contract": "data_inizio_contratto",
            "Sfarsit contract": "data_fine_contratto",
            "Tarif orar": "tariffa_oraria",
            "Tarif zilnic": "tariffa_giornaliera",
            "IBAN": "iban",
            "Note": "note",
            "Activ": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sit",
            "Prenume",
            "Nume",
            "Rol",
            "Tip contract",
            "Activ"
        ]
    elif L == 'pt':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Sitio": "sito",
            "Nome": "nome",
            "Apelido": "cognome",
            "Funcao": "ruolo",
            "Qualificacao": "qualifica",
            "Codigo Fiscal": "codice_fiscale",
            "Email": "email",
            "Telefone": "telefono",
            "Data de nascimento": "data_nascita",
            "Endereco": "indirizzo",
            "Tipo de contrato": "tipo_contratto",
            "Inicio do contrato": "data_inizio_contratto",
            "Fim do contrato": "data_fine_contratto",
            "Taxa horaria": "tariffa_oraria",
            "Taxa diaria": "tariffa_giornaliera",
            "IBAN": "iban",
            "Notas": "note",
            "Ativo": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Sitio",
            "Nome",
            "Apelido",
            "Funcao",
            "Tipo de contrato",
            "Ativo"
        ]
    elif L == 'el':
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Θέση": "sito",
            "Όνομα": "nome",
            "Επώνυμο": "cognome",
            "Ρόλος": "ruolo",
            "Προσόν": "qualifica",
            "ΑΦΜ": "codice_fiscale",
            "Email": "email",
            "Τηλέφωνο": "telefono",
            "Ημερομηνία γέννησης": "data_nascita",
            "Διεύθυνση": "indirizzo",
            "Τύπος σύμβασης": "tipo_contratto",
            "Έναρξη σύμβασης": "data_inizio_contratto",
            "Λήξη σύμβασης": "data_fine_contratto",
            "Ωριαία αμοιβή": "tariffa_oraria",
            "Ημερήσια αμοιβή": "tariffa_giornaliera",
            "IBAN": "iban",
            "Σημειώσεις": "note",
            "Ενεργός": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Θέση",
            "Όνομα",
            "Επώνυμο",
            "Ρόλος",
            "Τύπος σύμβασης",
            "Ενεργός"
        ]
    else:
        CONVERSION_DICT = {
            ID_TABLE: ID_TABLE,
            "Site": "sito",
            "First Name": "nome",
            "Last Name": "cognome",
            "Role": "ruolo",
            "Qualification": "qualifica",
            "Tax Code": "codice_fiscale",
            "Email": "email",
            "Phone": "telefono",
            "Date of Birth": "data_nascita",
            "Address": "indirizzo",
            "Contract Type": "tipo_contratto",
            "Contract Start": "data_inizio_contratto",
            "Contract End": "data_fine_contratto",
            "Hourly Rate": "tariffa_oraria",
            "Daily Rate": "tariffa_giornaliera",
            "IBAN": "iban",
            "Notes": "note",
            "Active": "attivo"
        }
        SORT_ITEMS = [
            ID_TABLE,
            "Site",
            "First Name",
            "Last Name",
            "Role",
            "Contract Type",
            "Active"
        ]

    TABLE_FIELDS = [
        'sito',
        'nome',
        'cognome',
        'ruolo',
        'qualifica',
        'codice_fiscale',
        'email',
        'telefono',
        'data_nascita',
        'indirizzo',
        'tipo_contratto',
        'data_inizio_contratto',
        'data_fine_contratto',
        'tariffa_oraria',
        'tariffa_giornaliera',
        'iban',
        'note',
        'attivo'
    ]

    LANG_TO_THESAURUS = {
        'it': 'IT', 'en': 'en_US', 'de': 'de_DE', 'es': 'es_ES',
        'fr': 'fr_FR', 'ar': 'ar_AR', 'ca': 'ca_ES', 'ro': 'ro_RO',
        'pt': 'pt_PT', 'el': 'el_GR'
    }

    DB_SERVER = "not defined"
    HOME = os.environ['PYARCHINIT_HOME']

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)

        # Apply theme
        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)

        self.currentLayerId = None
        self.retranslate_ui()
        QTimer.singleShot(0, self._deferred_init)

    def _deferred_init(self):
        """Load data after the window is visible."""
        try:
            self.on_pushButton_connect_pressed()
        except:
            pass
        self.fill_fields()
        self.set_sito()
        self.msg_sito()

    def retranslate_ui(self):
        """Translate UI labels based on current locale."""
        lang = self.L
        translations = {
            'it': {
                'title': 'pyArchInit Gestione Cantiere - Personale',
                'anagrafica': 'Anagrafica', 'nome': 'Nome', 'cognome': 'Cognome',
                'codice_fiscale': 'Codice Fiscale', 'data_nascita': 'Data Nascita',
                'email': 'Email', 'telefono': 'Telefono', 'indirizzo': 'Indirizzo',
                'ruolo': 'Ruolo', 'qualifica': 'Qualifica',
                'contratto': 'Contratto', 'tipo_contratto': 'Tipo Contratto',
                'data_inizio': 'Data Inizio', 'data_fine': 'Data Fine',
                'tariffa_oraria': 'Tariffa Oraria', 'tariffa_giornaliera': 'Tariffa Giornaliera',
                'iban': 'IBAN', 'stato': 'Stato', 'attivo': 'Attivo', 'note': 'Note',
                'sito': 'Sito', 'ordinamento': 'Ordinamento',
            },
            'en': {
                'title': 'pyArchInit Site Management - Personnel',
                'anagrafica': 'Personal Data', 'nome': 'First Name', 'cognome': 'Surname',
                'codice_fiscale': 'Tax ID', 'data_nascita': 'Date of Birth',
                'email': 'Email', 'telefono': 'Phone', 'indirizzo': 'Address',
                'ruolo': 'Role', 'qualifica': 'Qualification',
                'contratto': 'Contract', 'tipo_contratto': 'Contract Type',
                'data_inizio': 'Start Date', 'data_fine': 'End Date',
                'tariffa_oraria': 'Hourly Rate', 'tariffa_giornaliera': 'Daily Rate',
                'iban': 'IBAN', 'stato': 'Status', 'attivo': 'Active', 'note': 'Notes',
                'sito': 'Site', 'ordinamento': 'Sort Order',
            },
            'de': {
                'title': 'pyArchInit Grabungsverwaltung - Personal',
                'anagrafica': 'Persönliche Daten', 'nome': 'Vorname', 'cognome': 'Nachname',
                'codice_fiscale': 'Steuernummer', 'data_nascita': 'Geburtsdatum',
                'email': 'E-Mail', 'telefono': 'Telefon', 'indirizzo': 'Adresse',
                'ruolo': 'Rolle', 'qualifica': 'Qualifikation',
                'contratto': 'Vertrag', 'tipo_contratto': 'Vertragstyp',
                'data_inizio': 'Startdatum', 'data_fine': 'Enddatum',
                'tariffa_oraria': 'Stundensatz', 'tariffa_giornaliera': 'Tagessatz',
                'iban': 'IBAN', 'stato': 'Status', 'attivo': 'Aktiv', 'note': 'Notizen',
                'sito': 'Fundstelle', 'ordinamento': 'Sortierung',
            },
            'es': {
                'title': 'pyArchInit Gestión de Obra - Personal',
                'anagrafica': 'Datos Personales', 'nome': 'Nombre', 'cognome': 'Apellido',
                'codice_fiscale': 'NIF', 'data_nascita': 'Fecha de Nacimiento',
                'email': 'Correo', 'telefono': 'Teléfono', 'indirizzo': 'Dirección',
                'ruolo': 'Rol', 'qualifica': 'Cualificación',
                'contratto': 'Contrato', 'tipo_contratto': 'Tipo de Contrato',
                'data_inizio': 'Fecha Inicio', 'data_fine': 'Fecha Fin',
                'tariffa_oraria': 'Tarifa Horaria', 'tariffa_giornaliera': 'Tarifa Diaria',
                'iban': 'IBAN', 'stato': 'Estado', 'attivo': 'Activo', 'note': 'Notas',
                'sito': 'Sitio', 'ordinamento': 'Orden',
            },
            'fr': {
                'title': 'pyArchInit Gestion de Chantier - Personnel',
                'anagrafica': 'Données Personnelles', 'nome': 'Prénom', 'cognome': 'Nom',
                'codice_fiscale': 'Numéro Fiscal', 'data_nascita': 'Date de Naissance',
                'email': 'Courriel', 'telefono': 'Téléphone', 'indirizzo': 'Adresse',
                'ruolo': 'Rôle', 'qualifica': 'Qualification',
                'contratto': 'Contrat', 'tipo_contratto': 'Type de Contrat',
                'data_inizio': 'Date de Début', 'data_fine': 'Date de Fin',
                'tariffa_oraria': 'Tarif Horaire', 'tariffa_giornaliera': 'Tarif Journalier',
                'iban': 'IBAN', 'stato': 'Statut', 'attivo': 'Actif', 'note': 'Notes',
                'sito': 'Site', 'ordinamento': 'Classement',
            },
            'ar': {
                'title': 'pyArchInit إدارة الموقع - الموظفون',
                'anagrafica': 'البيانات الشخصية', 'nome': 'الاسم', 'cognome': 'اللقب',
                'codice_fiscale': 'الرقم الضريبي', 'data_nascita': 'تاريخ الميلاد',
                'email': 'البريد الإلكتروني', 'telefono': 'الهاتف', 'indirizzo': 'العنوان',
                'ruolo': 'الدور', 'qualifica': 'المؤهل',
                'contratto': 'العقد', 'tipo_contratto': 'نوع العقد',
                'data_inizio': 'تاريخ البداية', 'data_fine': 'تاريخ النهاية',
                'tariffa_oraria': 'الأجر بالساعة', 'tariffa_giornaliera': 'الأجر اليومي',
                'iban': 'IBAN', 'stato': 'الحالة', 'attivo': 'نشط', 'note': 'ملاحظات',
                'sito': 'الموقع', 'ordinamento': 'الترتيب',
            },
            'ca': {
                'title': "pyArchInit Gestió d'Obra - Personal",
                'anagrafica': 'Dades Personals', 'nome': 'Nom', 'cognome': 'Cognom',
                'codice_fiscale': 'NIF', 'data_nascita': 'Data de Naixement',
                'email': 'Correu', 'telefono': 'Telèfon', 'indirizzo': 'Adreça',
                'ruolo': 'Rol', 'qualifica': 'Qualificació',
                'contratto': 'Contracte', 'tipo_contratto': 'Tipus de Contracte',
                'data_inizio': "Data d'Inici", 'data_fine': 'Data Final',
                'tariffa_oraria': 'Tarifa Horària', 'tariffa_giornaliera': 'Tarifa Diària',
                'iban': 'IBAN', 'stato': 'Estat', 'attivo': 'Actiu', 'note': 'Notes',
                'sito': 'Lloc', 'ordinamento': 'Ordenació',
            },
            'ro': {
                'title': 'pyArchInit Gestiune Șantier - Personal',
                'anagrafica': 'Date Personale', 'nome': 'Prenume', 'cognome': 'Nume',
                'codice_fiscale': 'CNP', 'data_nascita': 'Data Nașterii',
                'email': 'Email', 'telefono': 'Telefon', 'indirizzo': 'Adresă',
                'ruolo': 'Rol', 'qualifica': 'Calificare',
                'contratto': 'Contract', 'tipo_contratto': 'Tip Contract',
                'data_inizio': 'Data Început', 'data_fine': 'Data Sfârșit',
                'tariffa_oraria': 'Tarif Orar', 'tariffa_giornaliera': 'Tarif Zilnic',
                'iban': 'IBAN', 'stato': 'Stare', 'attivo': 'Activ', 'note': 'Note',
                'sito': 'Sit', 'ordinamento': 'Ordonare',
            },
            'pt': {
                'title': 'pyArchInit Gestão de Obra - Pessoal',
                'anagrafica': 'Dados Pessoais', 'nome': 'Nome', 'cognome': 'Apelido',
                'codice_fiscale': 'NIF', 'data_nascita': 'Data de Nascimento',
                'email': 'Email', 'telefono': 'Telefone', 'indirizzo': 'Morada',
                'ruolo': 'Função', 'qualifica': 'Qualificação',
                'contratto': 'Contrato', 'tipo_contratto': 'Tipo de Contrato',
                'data_inizio': 'Data de Início', 'data_fine': 'Data de Fim',
                'tariffa_oraria': 'Taxa Horária', 'tariffa_giornaliera': 'Taxa Diária',
                'iban': 'IBAN', 'stato': 'Estado', 'attivo': 'Ativo', 'note': 'Notas',
                'sito': 'Sítio', 'ordinamento': 'Ordenação',
            },
            'el': {
                'title': 'pyArchInit Διαχείριση Ανασκαφής - Προσωπικό',
                'anagrafica': 'Προσωπικά Στοιχεία', 'nome': 'Όνομα', 'cognome': 'Επώνυμο',
                'codice_fiscale': 'ΑΦΜ', 'data_nascita': 'Ημερομηνία Γέννησης',
                'email': 'Email', 'telefono': 'Τηλέφωνο', 'indirizzo': 'Διεύθυνση',
                'ruolo': 'Ρόλος', 'qualifica': 'Προσόντα',
                'contratto': 'Σύμβαση', 'tipo_contratto': 'Τύπος Σύμβασης',
                'data_inizio': 'Ημ. Έναρξης', 'data_fine': 'Ημ. Λήξης',
                'tariffa_oraria': 'Ωριαία Αμοιβή', 'tariffa_giornaliera': 'Ημερήσια Αμοιβή',
                'iban': 'IBAN', 'stato': 'Κατάσταση', 'attivo': 'Ενεργός', 'note': 'Σημειώσεις',
                'sito': 'Τοποθεσία', 'ordinamento': 'Ταξινόμηση',
            },
        }
        t = translations.get(lang, translations.get('en', translations['it']))
        self.setWindowTitle(t['title'])
        self.groupBox_anagrafica.setTitle(t['anagrafica'])
        self.label_nome.setText(t['nome'])
        self.label_cognome.setText(t['cognome'])
        self.label_codice_fiscale.setText(t['codice_fiscale'])
        self.label_data_nascita.setText(t['data_nascita'])
        self.label_email.setText(t['email'])
        self.label_telefono.setText(t['telefono'])
        self.label_indirizzo.setText(t['indirizzo'])
        self.label_ruolo.setText(t['ruolo'])
        self.label_qualifica.setText(t['qualifica'])
        self.groupBox_contratto.setTitle(t['contratto'])
        self.label_tipo_contratto.setText(t['tipo_contratto'])
        self.label_data_inizio_contratto.setText(t['data_inizio'])
        self.label_data_fine_contratto.setText(t['data_fine'])
        self.label_tariffa_oraria.setText(t['tariffa_oraria'])
        self.label_tariffa_giornaliera.setText(t['tariffa_giornaliera'])
        self.label_iban.setText(t['iban'])
        self.groupBox_stato.setTitle(t['stato'])
        self.label_note.setText(t['note'])
        self.label_sito.setText(t['sito'])
        self.label_lbl_sort.setText(t['ordinamento'])

    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_show_all.setEnabled(n)
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
        self.pushButton_show_all.setEnabled(n)
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
            self.charge_records()
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                if self.L == 'it':
                    QMessageBox.warning(self, "BENVENUTO",
                                        "Benvenuto in pyArchInit " + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "WILLKOMMEN",
                                        "WILLKOMMEN in pyArchInit " + self.NOME_SCHEDA + ". Die Datenbank ist leer. Tippe 'Ok' und aufgehts!",
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WELCOME",
                                        "Welcome in pyArchInit " + self.NOME_SCHEDA + ". The DB is empty. Push 'Ok' and Good Work!",
                                        QMessageBox.StandardButton.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                if self.L == 'it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                elif self.L == 'de':
                    msg = "Verbindungsfehler {}. " \
                          " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                else:
                    msg = "The connection failed {}. " \
                          "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))
            else:
                if self.L == 'it':
                    msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                elif self.L == 'de':
                    msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                else:
                    msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))

    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

        # Thesaurus-based combobox population
        th_lang = self.LANG_TO_THESAURUS.get(self.L, 'en_US')
        try:
            thesaurus = self.DB_MANAGER.query_thesaurus_batch(
                'cantiere_personale_table', th_lang)

            ruolo_values = [v.sigla_estesa for v in thesaurus.get('14.1', [])]
            self.comboBox_ruolo.clear()
            self.comboBox_ruolo.addItems(ruolo_values)

            contratto_values = [v.sigla_estesa for v in thesaurus.get('14.2', [])]
            self.comboBox_tipo_contratto.clear()
            self.comboBox_tipo_contratto.addItems(contratto_values)
        except Exception as e:
            pass

    def msg_sito(self):
        conn = Connection()
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']
        if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
            if self.L == 'it':
                QMessageBox.information(self, "OK", "Sei connesso al sito: %s" % str(sito_set_str),
                                        QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.information(self, "OK",
                                        "Sie sind mit der archäologischen Stätte verbunden: %s" % str(sito_set_str),
                                        QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "OK", "You are connected to the site: %s" % str(sito_set_str),
                                        QMessageBox.StandardButton.Ok)
        elif sito_set_str == '':
            if self.L == 'it':
                msg = QMessageBox.information(self, "Attenzione",
                                              "Non hai settato alcun sito. Vuoi settarne uno? click Ok altrimenti Annulla per vedere tutti i record",
                                              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            elif self.L == 'de':
                msg = QMessageBox.information(self, "Achtung",
                                              "Sie haben keine archäologischen Stätten eingerichtet. Klicken Sie auf OK oder Abbrechen, um alle Datensätze zu sehen",
                                              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            else:
                msg = QMessageBox.information(self, "Warning",
                                              "You have not set up any archaeological site. Do you want to set one? click Ok otherwise Cancel to see all records",
                                              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
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

                if len(self.DATA_LIST) == 0:
                    if self.L == 'it':
                        QMessageBox.information(self, "Attenzione",
                                                "Il sito '%s' non ha record in questa scheda." % str(sito_set_str),
                                                QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.information(self, "Warnung",
                                                "Die Fundstelle '%s' hat keine Datensätze." % str(sito_set_str),
                                                QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Warning",
                                                "Site '%s' has no records in this tab." % str(sito_set_str),
                                                QMessageBox.StandardButton.Ok)
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
                QMessageBox.warning(self, "Errore",
                                    "Errore nel caricamento del sito '%s':\n%s" % (str(sito_set_str), str(e)),
                                    QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Fehler",
                                    "Fehler beim Laden der Fundstelle '%s':\n%s" % (str(sito_set_str), str(e)),
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Error",
                                    "Error loading site '%s':\n%s" % (str(sito_set_str), str(e)),
                                    QMessageBox.StandardButton.Ok)

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
        sito_set = conn.sito_set()
        sito_set_str = sito_set['sito_set']

        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if bool(self.DATA_LIST):
                        if self.records_equal_check() == 1:
                            if self.L == 'it':
                                self.update_if(QMessageBox.warning(self, 'Errore',
                                                                   "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                                   QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            elif self.L == 'de':
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                                                   QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                            else:
                                self.update_if(QMessageBox.warning(self, 'Error',
                                                                   "The record has been changed. Do you want to save the changes?",
                                                                   QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))

        if self.BROWSE_STATUS != "n":
            if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
                self.BROWSE_STATUS = "n"
                self.setComboBoxEnable(["self.comboBox_sito"], "False")
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields_nosite()
            else:
                self.BROWSE_STATUS = "n"
                self.setComboBoxEnable(["self.comboBox_sito"], "True")
                self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.empty_fields()

            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    if self.L == 'it':
                        self.update_if(QMessageBox.warning(self, 'Errore',
                                                           "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
                    elif self.L == 'de':
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
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",
                                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "Keine Änderung vorgenommen",
                                            QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "No changes have been made",
                                            QMessageBox.StandardButton.Ok)
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
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if self.L == 'it':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Sito obbligatorio!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_nome.text() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Nome obbligatorio!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_cognome.text() == "":
                QMessageBox.warning(self, "ATTENZIONE", "Campo Cognome obbligatorio!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
        elif self.L == 'de':
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Fundort erforderlich!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_nome.text() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Vorname erforderlich!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_cognome.text() == "":
                QMessageBox.warning(self, "ACHTUNG", "Feld Nachname erforderlich!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
        else:
            if self.comboBox_sito.currentText() == "":
                QMessageBox.warning(self, "WARNING", "Site field required!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_nome.text() == "":
                QMessageBox.warning(self, "WARNING", "First Name field required!",
                                    QMessageBox.StandardButton.Ok)
                test = 1
            if self.lineEdit_cognome.text() == "":
                QMessageBox.warning(self, "WARNING", "Last Name field required!",
                                    QMessageBox.StandardButton.Ok)
                test = 1

        return test

    def insert_new_rec(self):
        try:
            # Handle optional numeric fields
            tariffa_oraria = None
            if self.lineEdit_tariffa_oraria.text():
                try:
                    tariffa_oraria = float(self.lineEdit_tariffa_oraria.text())
                except ValueError:
                    tariffa_oraria = None

            tariffa_giornaliera = None
            if self.lineEdit_tariffa_giornaliera.text():
                try:
                    tariffa_giornaliera = float(self.lineEdit_tariffa_giornaliera.text())
                except ValueError:
                    tariffa_giornaliera = None

            # Handle checkbox for attivo
            attivo = 1 if self.checkBox_attivo.isChecked() else 0

            data = self.DB_MANAGER.insert_personale_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_sito.currentText()),                  # sito
                str(self.lineEdit_nome.text()),                         # nome
                str(self.lineEdit_cognome.text()),                      # cognome
                str(self.comboBox_ruolo.currentText()),                 # ruolo
                str(self.lineEdit_qualifica.text()),                    # qualifica
                str(self.lineEdit_codice_fiscale.text()),               # codice_fiscale
                str(self.lineEdit_email.text()),                        # email
                str(self.lineEdit_telefono.text()),                     # telefono
                str(self.lineEdit_data_nascita.date().toString("yyyy-MM-dd")),                 # data_nascita
                str(self.lineEdit_indirizzo.text()),                    # indirizzo
                str(self.comboBox_tipo_contratto.currentText()),        # tipo_contratto
                str(self.lineEdit_data_inizio_contratto.date().toString("yyyy-MM-dd")),        # data_inizio_contratto
                str(self.lineEdit_data_fine_contratto.date().toString("yyyy-MM-dd")),          # data_fine_contratto
                tariffa_oraria,                                         # tariffa_oraria
                tariffa_giornaliera,                                    # tariffa_giornaliera
                str(self.lineEdit_iban.text()),                         # iban
                str(self.textEdit_note.toPlainText()),                  # note
                attivo)                                                 # attivo

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    if self.L == 'it':
                        msg = self.ID_TABLE + " gia' presente nel database"
                    elif self.L == 'de':
                        msg = self.ID_TABLE + " bereits in der Datenbank"
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
            return 1
        elif self.records_equal_check() == 1 and ec == 0:
            if self.L == 'it':
                self.update_if(
                    QMessageBox.warning(self, 'Errore',
                                        "Il record e' stato modificato. Vuoi salvare le modifiche?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            elif self.L == 'de':
                self.update_if(
                    QMessageBox.warning(self, 'Errore',
                                        "Der Record wurde geändert. Möchtest du die Änderungen speichern?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            else:
                self.update_if(
                    QMessageBox.warning(self, "Error",
                                        "The record has been changed. You want to save the changes?",
                                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel))
            return 0

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

    # Alias for UI button name compatibility
    on_pushButton_show_all_pressed = on_pushButton_view_all_pressed

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
                if self.L == 'it':
                    QMessageBox.warning(self, "Attenzione", "Sei al primo record!",
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im ersten Datensatz!",
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are at the first record!",
                                        QMessageBox.StandardButton.Ok)
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
                if self.L == 'it':
                    QMessageBox.warning(self, "Attenzione", "Sei all'ultimo record!",
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "Achtung", "du befindest dich im letzten Datensatz!",
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "Warning", "You are at the last record!",
                                        QMessageBox.StandardButton.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.StandardButton.Ok)

    def on_pushButton_delete_pressed(self):
        if self.L == 'it':
            msg = QMessageBox.warning(self, "Attenzione!!!",
                                      "Vuoi veramente eliminare il record? \n L'azione è irreversibile",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Messaggio!!!", "Azione Annullata!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()
                    QMessageBox.warning(self, "Messaggio!!!", "Record eliminato!")
                except Exception as e:
                    QMessageBox.warning(self, "Messaggio!!!", "Tipo di errore: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Attenzione", "Il database è vuoto!",
                                        QMessageBox.StandardButton.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
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
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Aktion annulliert!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()
                    QMessageBox.warning(self, "Message!!!", "Record gelöscht!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "Errortyp: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "Die Datenbank ist leer!",
                                        QMessageBox.StandardButton.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
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
                                      "Do you really want to delete the record? \n Action is irreversible.",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action deleted!")
            else:
                try:
                    id_to_delete = getattr(self.DATA_LIST[self.REC_CORR], self.ID_TABLE)
                    self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                    self.charge_records()
                    QMessageBox.warning(self, "Message!!!", "Record deleted!")
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
                if not bool(self.DATA_LIST):
                    QMessageBox.warning(self, "Warning", "the db is empty!",
                                        QMessageBox.StandardButton.Ok)
                    self.DATA_LIST = []
                    self.DATA_LIST_REC_CORR = []
                    self.DATA_LIST_REC_TEMP = []
                    self.REC_CORR = 0
                    self.REC_TOT = 0
                    self.empty_fields()
                    self.set_rec_counter(0, 0)
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
            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']

            if self.BROWSE_STATUS != "f":
                if bool(self.comboBox_sito.currentText()) and self.comboBox_sito.currentText() == sito_set_str:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields_nosite()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                else:
                    self.BROWSE_STATUS = "f"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.empty_fields()
                    self.set_rec_counter('', '')
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.setComboBoxEnable(["self.comboBox_sito"], "True")
                    self.charge_list()

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            if self.L == 'it':
                QMessageBox.warning(self, "ATTENZIONE",
                                    "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",
                                    QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "ACHTUNG",
                                    "Um eine neue Abfrage zu starten drücke 'new search' ",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "WARNING",
                                    "To perform a new search click on the 'new search' button ",
                                    QMessageBox.StandardButton.Ok)
        else:
            search_dict = {
                'sito': "'" + str(self.comboBox_sito.currentText()) + "'",
                'nome': "'" + str(self.lineEdit_nome.text()) + "'",
                'cognome': "'" + str(self.lineEdit_cognome.text()) + "'",
                'ruolo': "'" + str(self.comboBox_ruolo.currentText()) + "'",
                'qualifica': "'" + str(self.lineEdit_qualifica.text()) + "'",
                'codice_fiscale': "'" + str(self.lineEdit_codice_fiscale.text()) + "'",
                'email': "'" + str(self.lineEdit_email.text()) + "'",
                'telefono': "'" + str(self.lineEdit_telefono.text()) + "'",
                'data_nascita': "'" + str(self.lineEdit_data_nascita.date().toString("yyyy-MM-dd")) + "'",
                'indirizzo': "'" + str(self.lineEdit_indirizzo.text()) + "'",
                'tipo_contratto': "'" + str(self.comboBox_tipo_contratto.currentText()) + "'",
                'data_inizio_contratto': "'" + str(self.lineEdit_data_inizio_contratto.date().toString("yyyy-MM-dd")) + "'",
                'data_fine_contratto': "'" + str(self.lineEdit_data_fine_contratto.date().toString("yyyy-MM-dd")) + "'",
                'tariffa_oraria': "'" + str(self.lineEdit_tariffa_oraria.text()) + "'",
                'tariffa_giornaliera': "'" + str(self.lineEdit_tariffa_giornaliera.text()) + "'",
                'iban': "'" + str(self.lineEdit_iban.text()) + "'",
                'note': str(self.textEdit_note.toPlainText()),
            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                if self.L == 'it':
                    QMessageBox.warning(self, "ATTENZIONE", "Non è stata impostata nessuna ricerca!!!",
                                        QMessageBox.StandardButton.Ok)
                elif self.L == 'de':
                    QMessageBox.warning(self, "ACHTUNG", "Keine Abfrage definiert!!!",
                                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(self, "WARNING", "No search has been set!!!",
                                        QMessageBox.StandardButton.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    if self.L == 'it':
                        QMessageBox.warning(self, "ATTENZIONE", "Non e' stato trovato alcun record!",
                                            QMessageBox.StandardButton.Ok)
                    elif self.L == 'de':
                        QMessageBox.warning(self, "ACHTUNG", "kein Eintrag gefunden!",
                                            QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.warning(self, "Warning", "The record has not been found",
                                            QMessageBox.StandardButton.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
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

                    self.setComboBoxEnable(["self.comboBox_sito"], "False")
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings,
                                        QMessageBox.StandardButton.Ok)

        self.enable_button_search(1)

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
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
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

    def charge_records(self):
        self.DATA_LIST = self.DB_MANAGER.query_ordered(self.MAPPER_TABLE_CLASS, self.ID_TABLE, 'asc')

    def setComboBoxEditable(self, f, n):
        for fn in f:
            widget_name = fn.replace('self.', '') if fn.startswith('self.') else fn
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEditable(bool(n))

    def setComboBoxEnable(self, f, v):
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

    def empty_fields_nosite(self):
        self.lineEdit_nome.clear()
        self.lineEdit_cognome.clear()
        self.comboBox_ruolo.setEditText("")
        self.lineEdit_qualifica.clear()
        self.lineEdit_codice_fiscale.clear()
        self.lineEdit_email.clear()
        self.lineEdit_telefono.clear()
        self.lineEdit_data_nascita.setDate(QDate(2000, 1, 1))
        self.lineEdit_indirizzo.clear()
        self.comboBox_tipo_contratto.setEditText("")
        self.lineEdit_data_inizio_contratto.setDate(QDate(2000, 1, 1))
        self.lineEdit_data_fine_contratto.setDate(QDate(2000, 1, 1))
        self.lineEdit_tariffa_oraria.clear()
        self.lineEdit_tariffa_giornaliera.clear()
        self.lineEdit_iban.clear()
        self.textEdit_note.clear()
        self.checkBox_attivo.setChecked(False)

    def empty_fields(self):
        self.comboBox_sito.setEditText("")
        self.lineEdit_nome.clear()
        self.lineEdit_cognome.clear()
        self.comboBox_ruolo.setEditText("")
        self.lineEdit_qualifica.clear()
        self.lineEdit_codice_fiscale.clear()
        self.lineEdit_email.clear()
        self.lineEdit_telefono.clear()
        self.lineEdit_data_nascita.setDate(QDate(2000, 1, 1))
        self.lineEdit_indirizzo.clear()
        self.comboBox_tipo_contratto.setEditText("")
        self.lineEdit_data_inizio_contratto.setDate(QDate(2000, 1, 1))
        self.lineEdit_data_fine_contratto.setDate(QDate(2000, 1, 1))
        self.lineEdit_tariffa_oraria.clear()
        self.lineEdit_tariffa_giornaliera.clear()
        self.lineEdit_iban.clear()
        self.textEdit_note.clear()
        self.checkBox_attivo.setChecked(False)

    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            self.comboBox_sito.setEditText(str(self.DATA_LIST[self.rec_num].sito))
            self.lineEdit_nome.setText(str(self.DATA_LIST[self.rec_num].nome))
            self.lineEdit_cognome.setText(str(self.DATA_LIST[self.rec_num].cognome))
            self.comboBox_ruolo.setEditText(str(self.DATA_LIST[self.rec_num].ruolo) if self.DATA_LIST[self.rec_num].ruolo else "")
            self.lineEdit_qualifica.setText(str(self.DATA_LIST[self.rec_num].qualifica) if self.DATA_LIST[self.rec_num].qualifica else "")
            self.lineEdit_codice_fiscale.setText(str(self.DATA_LIST[self.rec_num].codice_fiscale) if self.DATA_LIST[self.rec_num].codice_fiscale else "")
            self.lineEdit_email.setText(str(self.DATA_LIST[self.rec_num].email) if self.DATA_LIST[self.rec_num].email else "")
            self.lineEdit_telefono.setText(str(self.DATA_LIST[self.rec_num].telefono) if self.DATA_LIST[self.rec_num].telefono else "")
            date_str = str(self.DATA_LIST[self.rec_num].data_nascita) if self.DATA_LIST[self.rec_num].data_nascita else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_nascita.setDate(qd)
                else:
                    self.lineEdit_data_nascita.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_nascita.setDate(QDate(2000, 1, 1))
            self.lineEdit_indirizzo.setText(str(self.DATA_LIST[self.rec_num].indirizzo) if self.DATA_LIST[self.rec_num].indirizzo else "")
            self.comboBox_tipo_contratto.setEditText(str(self.DATA_LIST[self.rec_num].tipo_contratto) if self.DATA_LIST[self.rec_num].tipo_contratto else "")
            date_str = str(self.DATA_LIST[self.rec_num].data_inizio_contratto) if self.DATA_LIST[self.rec_num].data_inizio_contratto else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_inizio_contratto.setDate(qd)
                else:
                    self.lineEdit_data_inizio_contratto.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_inizio_contratto.setDate(QDate(2000, 1, 1))
            date_str = str(self.DATA_LIST[self.rec_num].data_fine_contratto) if self.DATA_LIST[self.rec_num].data_fine_contratto else ""
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if not qd.isValid():
                    qd = QDate.fromString(date_str, "dd/MM/yyyy")
                if qd.isValid():
                    self.lineEdit_data_fine_contratto.setDate(qd)
                else:
                    self.lineEdit_data_fine_contratto.setDate(QDate.currentDate())
            else:
                self.lineEdit_data_fine_contratto.setDate(QDate(2000, 1, 1))

            if self.DATA_LIST[self.rec_num].tariffa_oraria is not None:
                self.lineEdit_tariffa_oraria.setText(str(self.DATA_LIST[self.rec_num].tariffa_oraria))
            else:
                self.lineEdit_tariffa_oraria.setText("")

            if self.DATA_LIST[self.rec_num].tariffa_giornaliera is not None:
                self.lineEdit_tariffa_giornaliera.setText(str(self.DATA_LIST[self.rec_num].tariffa_giornaliera))
            else:
                self.lineEdit_tariffa_giornaliera.setText("")

            self.lineEdit_iban.setText(str(self.DATA_LIST[self.rec_num].iban) if self.DATA_LIST[self.rec_num].iban else "")
            self.textEdit_note.setText(str(self.DATA_LIST[self.rec_num].note) if self.DATA_LIST[self.rec_num].note else "")

            # Handle attivo as checkbox
            attivo_val = self.DATA_LIST[self.rec_num].attivo
            self.checkBox_attivo.setChecked(bool(attivo_val) if attivo_val is not None else False)
        except:
            pass

    def set_LIST_REC_TEMP(self):
        # Handle optional numeric fields
        tariffa_oraria = str(self.lineEdit_tariffa_oraria.text()) if self.lineEdit_tariffa_oraria.text() else ''
        tariffa_giornaliera = str(self.lineEdit_tariffa_giornaliera.text()) if self.lineEdit_tariffa_giornaliera.text() else ''

        # Handle checkbox
        attivo = '1' if self.checkBox_attivo.isChecked() else '0'

        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),                  # sito
            str(self.lineEdit_nome.text()),                         # nome
            str(self.lineEdit_cognome.text()),                      # cognome
            str(self.comboBox_ruolo.currentText()),                 # ruolo
            str(self.lineEdit_qualifica.text()),                    # qualifica
            str(self.lineEdit_codice_fiscale.text()),               # codice_fiscale
            str(self.lineEdit_email.text()),                        # email
            str(self.lineEdit_telefono.text()),                     # telefono
            str(self.lineEdit_data_nascita.date().toString("yyyy-MM-dd")),                 # data_nascita
            str(self.lineEdit_indirizzo.text()),                    # indirizzo
            str(self.comboBox_tipo_contratto.currentText()),        # tipo_contratto
            str(self.lineEdit_data_inizio_contratto.date().toString("yyyy-MM-dd")),        # data_inizio_contratto
            str(self.lineEdit_data_fine_contratto.date().toString("yyyy-MM-dd")),          # data_fine_contratto
            tariffa_oraria,                                         # tariffa_oraria
            tariffa_giornaliera,                                    # tariffa_giornaliera
            str(self.lineEdit_iban.text()),                         # iban
            str(self.textEdit_note.toPlainText()),                  # note
            attivo                                                  # attivo
        ]

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
            save_file = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Report_folder")
            file_ = os.path.join(save_file, 'error_encodig_data_recover.txt')
            with open(file_, "a") as fh:
                try:
                    raise ValueError(str(e))
                except ValueError as s:
                    print(s, file=fh)
            if self.L == 'it':
                QMessageBox.warning(self, "Messaggio",
                                    "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database.",
                                    QMessageBox.StandardButton.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered.",
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Message",
                                    "Encoding problem: accents or characters not accepted by the database were entered.",
                                    QMessageBox.StandardButton.Ok)
            return 0

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

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


## Class end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = pyarchinit_Personale()
    ui.show()
    sys.exit(app.exec())
