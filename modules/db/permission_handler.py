#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Centralized permission and error handler for PyArchInit
Provides user-friendly error messages without exposing SQL details
"""

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog, Qgis


class PermissionHandler:
    """
    Handles permission errors and provides user-friendly messages
    """

    def __init__(self, parent_form, language='it'):
        self.form = parent_form
        self.L = language
        self.db_manager = None

    def set_db_manager(self, db_manager):
        """Set the database manager"""
        self.db_manager = db_manager

    def has_permission(self, table_name, permission_type):
        """
        Check if user has specific permission on table
        Returns True if permission exists, False otherwise
        """
        if not self.db_manager:
            return True  # Assume permission if no db_manager

        # For SQLite, always return True
        if hasattr(self.db_manager, 'engine') and 'sqlite' in str(self.db_manager.engine.url):
            return True

        try:
            # Check permission using PostgreSQL has_table_privilege function
            check_sql = f"""
            SELECT has_table_privilege(current_user, '{table_name}', '{permission_type}')
            """
            result = self.db_manager.execute_sql(check_sql)
            if result and len(result) > 0:
                # Handle both tuple and dict results
                if isinstance(result[0], tuple):
                    return result[0][0] if len(result[0]) > 0 else False
                elif isinstance(result[0], dict):
                    return list(result[0].values())[0] if result[0] else False
                else:
                    return bool(result[0])
        except:
            # If check fails, assume permission exists
            return True

        return False

    # Translations for permission titles
    PERMISSION_TITLES = {
        'it': "Permessi Insufficienti",
        'en': "Insufficient Permissions",
        'de': "Unzureichende Berechtigungen",
        'es': "Permisos Insuficientes",
        'fr': "Permissions Insuffisantes",
        'ar': "صلاحيات غير كافية",
        'ca': "Permisos Insuficients",
        'ro': "Permisiuni Insuficiente",
        'pt': "Permissoes Insuficientes",
        'el': "Aneparkis Dikaiomata",
    }

    # Translations for permission operation messages
    PERMISSION_MESSAGES = {
        'INSERT': {
            'it': "Non hai i permessi per inserire nuovi record in questa tabella.",
            'en': "You don't have permission to insert new records in this table.",
            'de': "Sie haben keine Berechtigung, neue Datensatze in diese Tabelle einzufugen.",
            'es': "No tiene permisos para insertar nuevos registros en esta tabla.",
            'fr': "Vous n'avez pas la permission d'inserer de nouveaux enregistrements dans cette table.",
            'ar': "ليس لديك صلاحية لادراج سجلات جديدة في هذا الجدول.",
            'ca': "No teniu permisos per inserir nous registres en aquesta taula.",
            'ro': "Nu aveti permisiunea de a insera inregistrari noi in acest tabel.",
            'pt': "Nao tem permissao para inserir novos registos nesta tabela.",
            'el': "Den echete dikaioma na eisagete nees egraphes se afton ton pinaka.",
        },
        'UPDATE': {
            'it': "Non hai i permessi per modificare record in questa tabella.",
            'en': "You don't have permission to modify records in this table.",
            'de': "Sie haben keine Berechtigung, Datensatze in dieser Tabelle zu andern.",
            'es': "No tiene permisos para modificar registros en esta tabla.",
            'fr': "Vous n'avez pas la permission de modifier les enregistrements de cette table.",
            'ar': "ليس لديك صلاحية لتعديل السجلات في هذا الجدول.",
            'ca': "No teniu permisos per modificar registres en aquesta taula.",
            'ro': "Nu aveti permisiunea de a modifica inregistrarile din acest tabel.",
            'pt': "Nao tem permissao para modificar registos nesta tabela.",
            'el': "Den echete dikaioma na tropopoiisete egraphes se afton ton pinaka.",
        },
        'DELETE': {
            'it': "Non hai i permessi per eliminare record da questa tabella.",
            'en': "You don't have permission to delete records from this table.",
            'de': "Sie haben keine Berechtigung, Datensatze aus dieser Tabelle zu loschen.",
            'es': "No tiene permisos para eliminar registros de esta tabla.",
            'fr': "Vous n'avez pas la permission de supprimer des enregistrements de cette table.",
            'ar': "ليس لديك صلاحية لحذف السجلات من هذا الجدول.",
            'ca': "No teniu permisos per eliminar registres d'aquesta taula.",
            'ro': "Nu aveti permisiunea de a sterge inregistrari din acest tabel.",
            'pt': "Nao tem permissao para eliminar registos desta tabela.",
            'el': "Den echete dikaioma na diagrapsete egraphes apo afton ton pinaka.",
        },
        'SELECT': {
            'it': "Non hai i permessi per visualizzare record di questa tabella.",
            'en': "You don't have permission to view records from this table.",
            'de': "Sie haben keine Berechtigung, Datensatze aus dieser Tabelle anzuzeigen.",
            'es': "No tiene permisos para visualizar registros de esta tabla.",
            'fr': "Vous n'avez pas la permission de visualiser les enregistrements de cette table.",
            'ar': "ليس لديك صلاحية لعرض السجلات من هذا الجدول.",
            'ca': "No teniu permisos per visualitzar registres d'aquesta taula.",
            'ro': "Nu aveti permisiunea de a vizualiza inregistrarile din acest tabel.",
            'pt': "Nao tem permissao para visualizar registos desta tabela.",
            'el': "Den echete dikaioma na deite egraphes apo afton ton pinaka.",
        },
        'DEFAULT': {
            'it': "Non hai i permessi necessari per questa operazione.",
            'en': "You don't have the necessary permissions for this operation.",
            'de': "Sie haben nicht die erforderlichen Berechtigungen fur diesen Vorgang.",
            'es': "No tiene los permisos necesarios para esta operacion.",
            'fr': "Vous n'avez pas les permissions necessaires pour cette operation.",
            'ar': "ليس لديك الصلاحيات اللازمة لهذه العملية.",
            'ca': "No teniu els permisos necessaris per a aquesta operacio.",
            'ro': "Nu aveti permisiunile necesare pentru aceasta operatiune.",
            'pt': "Nao tem as permissoes necessarias para esta operacao.",
            'el': "Den echete ta aparaitita dikaiomata gia afti tin leitourgia.",
        },
    }

    # Translations for error titles and messages
    ERROR_TITLES = {
        'encoding': {
            'it': "Errore Caratteri", 'en': "Character Error", 'de': "Zeichenfehler",
            'es': "Error de Caracteres", 'fr': "Erreur de Caracteres", 'ar': "خطا في الاحرف",
            'ca': "Error de Caracters", 'ro': "Eroare de Caractere", 'pt': "Erro de Caracteres",
            'el': "Sfalma Charaktiron",
        },
        'connection': {
            'it': "Errore Connessione", 'en': "Connection Error", 'de': "Verbindungsfehler",
            'es': "Error de Conexion", 'fr': "Erreur de Connexion", 'ar': "خطا في الاتصال",
            'ca': "Error de Connexio", 'ro': "Eroare de Conexiune", 'pt': "Erro de Conexao",
            'el': "Sfalma Syndesis",
        },
        'duplicate': {
            'it': "Record Duplicato", 'en': "Duplicate Record", 'de': "Doppelter Datensatz",
            'es': "Registro Duplicado", 'fr': "Enregistrement En Double", 'ar': "سجل مكرر",
            'ca': "Registre Duplicat", 'ro': "Inregistrare Duplicata", 'pt': "Registo Duplicado",
            'el': "Diplotypi Eggrafi",
        },
        'foreign_key': {
            'it': "Errore Dipendenze", 'en': "Dependency Error", 'de': "Abhangigkeitsfehler",
            'es': "Error de Dependencias", 'fr': "Erreur de Dependances", 'ar': "خطا في التبعيات",
            'ca': "Error de Dependencies", 'ro': "Eroare de Dependente", 'pt': "Erro de Dependencias",
            'el': "Sfalma Exartiseon",
        },
        'generic': {
            'it': "Errore Database", 'en': "Database Error", 'de': "Datenbankfehler",
            'es': "Error de Base de Datos", 'fr': "Erreur de Base de Donnees", 'ar': "خطا في قاعدة البيانات",
            'ca': "Error de Base de Dades", 'ro': "Eroare de Baza de Date", 'pt': "Erro de Base de Dados",
            'el': "Sfalma Vasis Dedomenon",
        },
    }

    ERROR_MESSAGES = {
        'encoding': {
            'it': "Alcuni caratteri nel record non sono supportati. Controllare i dati inseriti.",
            'en': "Some characters in the record are not supported. Please check your input.",
            'de': "Einige Zeichen im Datensatz werden nicht unterstutzt. Bitte uberprufen Sie die Eingabe.",
            'es': "Algunos caracteres en el registro no son compatibles. Verifique los datos ingresados.",
            'fr': "Certains caracteres de l'enregistrement ne sont pas pris en charge. Verifiez les donnees saisies.",
            'ar': "بعض الاحرف في السجل غير مدعومة. يرجى التحقق من المدخلات.",
            'ca': "Alguns caracters del registre no son compatibles. Comproveu les dades introduides.",
            'ro': "Unele caractere din inregistrare nu sunt acceptate. Verificati datele introduse.",
            'pt': "Alguns caracteres no registo nao sao suportados. Verifique os dados introduzidos.",
            'el': "Merikoi charaktires stin eggrafi den ypostirizondai. Elegxte ta dedomena eisodou.",
        },
        'connection': {
            'it': "Impossibile connettersi al database. Verificare la connessione.",
            'en': "Cannot connect to database. Please check your connection.",
            'de': "Verbindung zur Datenbank fehlgeschlagen. Bitte Verbindung uberprufen.",
            'es': "No se puede conectar a la base de datos. Verifique la conexion.",
            'fr': "Impossible de se connecter a la base de donnees. Verifiez la connexion.",
            'ar': "تعذر الاتصال بقاعدة البيانات. يرجى التحقق من الاتصال.",
            'ca': "No es pot connectar a la base de dades. Comproveu la connexio.",
            'ro': "Nu se poate conecta la baza de date. Verificati conexiunea.",
            'pt': "Nao e possivel conectar-se a base de dados. Verifique a conexao.",
            'el': "Adynati i syndesi me ti vasi dedomenon. Elegxte ti syndesi sas.",
        },
        'duplicate': {
            'it': "Record duplicato. Esiste gia un record con questi valori.",
            'en': "Duplicate record. A record with these values already exists.",
            'de': "Doppelter Datensatz. Ein Datensatz mit diesen Werten existiert bereits.",
            'es': "Registro duplicado. Ya existe un registro con estos valores.",
            'fr': "Enregistrement en double. Un enregistrement avec ces valeurs existe deja.",
            'ar': "سجل مكرر. يوجد بالفعل سجل بهذه القيم.",
            'ca': "Registre duplicat. Ja existeix un registre amb aquests valors.",
            'ro': "Inregistrare duplicata. Exista deja o inregistrare cu aceste valori.",
            'pt': "Registo duplicado. Ja existe um registo com estes valores.",
            'el': "Diplotypi eggrafi. Yparchi idi mia eggrafi me aftes tis times.",
        },
        'foreign_key': {
            'it': "Impossibile completare l'operazione: alcuni dati dipendono da altri record.",
            'en': "Cannot complete operation: data depends on other records.",
            'de': "Vorgang kann nicht abgeschlossen werden: Daten hangen von anderen Datensatzen ab.",
            'es': "No se puede completar la operacion: algunos datos dependen de otros registros.",
            'fr': "Impossible de completer l'operation: certaines donnees dependent d'autres enregistrements.",
            'ar': "تعذر اكمال العملية: بعض البيانات تعتمد على سجلات اخرى.",
            'ca': "No es pot completar l'operacio: algunes dades depenen d'altres registres.",
            'ro': "Nu se poate finaliza operatiunea: unele date depind de alte inregistrari.",
            'pt': "Nao e possivel completar a operacao: alguns dados dependem de outros registos.",
            'el': "Adynati i oloklirosin tis leitourgias: ta dedomena exartondai apo alles egraphes.",
        },
    }

    CONTEXT_TRANSLATIONS = {
        'save': {
            'it': 'il salvataggio', 'en': 'save', 'de': 'Speichern', 'es': 'el guardado',
            'fr': 'l\'enregistrement', 'ar': 'الحفظ', 'ca': 'el desament', 'ro': 'salvarea',
            'pt': 'o salvamento', 'el': 'tin apothikeusi',
        },
        'delete': {
            'it': 'l\'eliminazione', 'en': 'delete', 'de': 'Loschen', 'es': 'la eliminacion',
            'fr': 'la suppression', 'ar': 'الحذف', 'ca': 'l\'eliminacio', 'ro': 'stergerea',
            'pt': 'a eliminacao', 'el': 'ti diagrafi',
        },
        'update': {
            'it': 'l\'aggiornamento', 'en': 'update', 'de': 'Aktualisierung', 'es': 'la actualizacion',
            'fr': 'la mise a jour', 'ar': 'التحديث', 'ca': 'l\'actualitzacio', 'ro': 'actualizarea',
            'pt': 'a atualizacao', 'el': 'tin enimerosin',
        },
        'insert': {
            'it': 'l\'inserimento', 'en': 'insert', 'de': 'Einfugen', 'es': 'la insercion',
            'fr': 'l\'insertion', 'ar': 'الادراج', 'ca': 'la insercio', 'ro': 'inserarea',
            'pt': 'a insercao', 'el': 'tin eisagogi',
        },
        'search': {
            'it': 'la ricerca', 'en': 'search', 'de': 'Suche', 'es': 'la busqueda',
            'fr': 'la recherche', 'ar': 'البحث', 'ca': 'la cerca', 'ro': 'cautarea',
            'pt': 'a pesquisa', 'el': 'tin anazitisi',
        },
        'operation': {
            'it': 'l\'operazione', 'en': 'operation', 'de': 'Vorgang', 'es': 'la operacion',
            'fr': 'l\'operation', 'ar': 'العملية', 'ca': 'l\'operacio', 'ro': 'operatiunea',
            'pt': 'a operacao', 'el': 'ti leitourgia',
        },
    }

    GENERIC_ERROR_MSG = {
        'it': "Errore durante {context}. Se il problema persiste, contattare l'amministratore.",
        'en': "Error during {context}. If problem persists, contact administrator.",
        'de': "Fehler bei {context}. Bei anhaltenden Problemen wenden Sie sich an den Administrator.",
        'es': "Error durante {context}. Si el problema persiste, contacte al administrador.",
        'fr': "Erreur lors de {context}. Si le probleme persiste, contactez l'administrateur.",
        'ar': "خطا اثناء {context}. اذا استمرت المشكلة، اتصل بالمسؤول.",
        'ca': "Error durant {context}. Si el problema persisteix, contacteu amb l'administrador.",
        'ro': "Eroare in timpul {context}. Daca problema persista, contactati administratorul.",
        'pt': "Erro durante {context}. Se o problema persistir, contacte o administrador.",
        'el': "Sfalma kata ti diarkeia {context}. An to provlima synechisti, epikoinoniste me ton diacheiristi.",
    }

    def _get_lang(self):
        """Get the current language, falling back to 'en' if not supported"""
        return self.L if self.L in ('it', 'en', 'de', 'es', 'fr', 'ar', 'ca', 'ro', 'pt', 'el') else 'en'

    def handle_permission_error(self, error, operation='operation', show_message=True):
        """
        Handle permission errors with user-friendly messages
        Returns True if error was handled, False otherwise
        """
        error_str = str(error)
        error_type = str(type(error))

        # Check if it's a permission error
        if not ('InsufficientPrivilege' in error_type or
                'permission denied' in error_str.lower() or
                'insufficient privilege' in error_str.lower()):
            return False

        # Log technical details for debugging
        QgsMessageLog.logMessage(
            f"Permission error in {self.form.__class__.__name__}: {error_str}",
            "PyArchInit", Qgis.Info
        )

        if show_message:
            lang = self._get_lang()
            title = self.PERMISSION_TITLES.get(lang, self.PERMISSION_TITLES['en'])
            op_key = operation.upper() if operation.upper() in self.PERMISSION_MESSAGES else 'DEFAULT'
            msg = self.PERMISSION_MESSAGES[op_key].get(lang, self.PERMISSION_MESSAGES[op_key]['en'])

            QMessageBox.warning(self.form, title, msg, QMessageBox.Ok)

        return True

    def handle_database_error(self, error, context='', show_message=True):
        """
        Handle database errors with user-friendly messages
        Returns True if error was handled, False otherwise
        """
        # First check if it's a permission error
        if self.handle_permission_error(error, context, show_message):
            return True

        error_str = str(error)

        # Log technical details
        QgsMessageLog.logMessage(
            f"Database error in {self.form.__class__.__name__}: {error_str}",
            "PyArchInit", Qgis.Warning
        )

        if not show_message:
            return False

        lang = self._get_lang()

        # Determine error type and show appropriate message
        if 'encode' in error_str.lower() or 'decode' in error_str.lower():
            error_key = 'encoding'
        elif 'connection' in error_str.lower() or 'connect' in error_str.lower():
            error_key = 'connection'
        elif 'duplicate' in error_str.lower() or 'unique' in error_str.lower():
            error_key = 'duplicate'
        elif 'foreign key' in error_str.lower():
            error_key = 'foreign_key'
        else:
            error_key = None

        if error_key:
            title = self.ERROR_TITLES[error_key].get(lang, self.ERROR_TITLES[error_key]['en'])
            msg = self.ERROR_MESSAGES[error_key].get(lang, self.ERROR_MESSAGES[error_key]['en'])
        else:
            # Generic database error
            title = self.ERROR_TITLES['generic'].get(lang, self.ERROR_TITLES['generic']['en'])
            ctx_key = context.lower() if context and context.lower() in self.CONTEXT_TRANSLATIONS else 'operation'
            ctx = self.CONTEXT_TRANSLATIONS[ctx_key].get(lang, self.CONTEXT_TRANSLATIONS[ctx_key]['en'])
            msg_template = self.GENERIC_ERROR_MSG.get(lang, self.GENERIC_ERROR_MSG['en'])
            msg = msg_template.format(context=ctx)

        QMessageBox.warning(self.form, title, msg, QMessageBox.Ok)
        return True
