#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User Management Dialog for PyArchInit Admin
"""

from qgis.PyQt.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QTableWidget, QTableWidgetItem, QPushButton,
                            QLineEdit, QComboBox, QCheckBox, QLabel,
                            QGroupBox, QMessageBox, QHeaderView, QFormLayout,
                            QTextEdit, QSplitter, QListWidget, QListWidgetItem)
from qgis.PyQt.QtCore import Qt, QTimer, pyqtSignal
from qgis.PyQt.QtGui import QBrush, QColor, QFont
from qgis.core import QgsSettings
import hashlib
import getpass
from datetime import datetime

class UserManagementDialog(QDialog):
    """Dialog per gestione utenti e permessi - Solo per Admin"""

    user_changed = pyqtSignal()  # Segnale quando cambiano utenti/permessi

    # Translation dictionary for all user-facing strings in 10 languages
    TRANSLATIONS = {
        'window_title': {
            'it': "Gestione Utenti e Permessi - PyArchInit",
            'en': "User & Permission Management - PyArchInit",
            'de': "Benutzer- & Rechteverwaltung - PyArchInit",
            'es': "Gestion de Usuarios y Permisos - PyArchInit",
            'fr': "Gestion des Utilisateurs et Permissions - PyArchInit",
            'ar': "ادارة المستخدمين والصلاحيات - PyArchInit",
            'ca': "Gestio d'Usuaris i Permisos - PyArchInit",
            'ro': "Gestionarea Utilizatorilor si Permisiunilor - PyArchInit",
            'pt': "Gestao de Utilizadores e Permissoes - PyArchInit",
            'el': "Diacheirisi Christon kai Dikaiomadon - PyArchInit",
        },
        'header_title': {
            'it': "GESTIONE UTENTI E PERMESSI",
            'en': "USER & PERMISSION MANAGEMENT",
            'de': "BENUTZER- & RECHTEVERWALTUNG",
            'es': "GESTION DE USUARIOS Y PERMISOS",
            'fr': "GESTION DES UTILISATEURS ET PERMISSIONS",
            'ar': "ادارة المستخدمين والصلاحيات",
            'ca': "GESTIO D'USUARIS I PERMISOS",
            'ro': "GESTIONAREA UTILIZATORILOR SI PERMISIUNILOR",
            'pt': "GESTAO DE UTILIZADORES E PERMISSOES",
            'el': "DIACHEIRISI CHRISTON KAI DIKAIOMADON",
        },
        'connected_as': {
            'it': "Connesso come",
            'en': "Connected as",
            'de': "Verbunden als",
            'es': "Conectado como",
            'fr': "Connecte en tant que",
            'ar': "متصل باسم",
            'ca': "Connectat com",
            'ro': "Conectat ca",
            'pt': "Conectado como",
            'el': "Syndedemenos os",
        },
        'tab_users': {
            'it': "Utenti",
            'en': "Users",
            'de': "Benutzer",
            'es': "Usuarios",
            'fr': "Utilisateurs",
            'ar': "المستخدمون",
            'ca': "Usuaris",
            'ro': "Utilizatori",
            'pt': "Utilizadores",
            'el': "Christes",
        },
        'tab_permissions': {
            'it': "Permessi",
            'en': "Permissions",
            'de': "Berechtigungen",
            'es': "Permisos",
            'fr': "Permissions",
            'ar': "الصلاحيات",
            'ca': "Permisos",
            'ro': "Permisiuni",
            'pt': "Permissoes",
            'el': "Dikaiomata",
        },
        'tab_monitor': {
            'it': "Monitor",
            'en': "Monitor",
            'de': "Monitor",
            'es': "Monitor",
            'fr': "Moniteur",
            'ar': "المراقبة",
            'ca': "Monitor",
            'ro': "Monitor",
            'pt': "Monitor",
            'el': "Parakolouthisi",
        },
        'tab_roles': {
            'it': "Ruoli",
            'en': "Roles",
            'de': "Rollen",
            'es': "Roles",
            'fr': "Roles",
            'ar': "الادوار",
            'ca': "Rols",
            'ro': "Roluri",
            'pt': "Papeis",
            'el': "Roloi",
        },
        'btn_init_db': {
            'it': "Inizializza Database Utenti",
            'en': "Initialize User Database",
            'de': "Benutzerdatenbank initialisieren",
            'es': "Inicializar Base de Datos de Usuarios",
            'fr': "Initialiser la Base de Donnees Utilisateurs",
            'ar': "تهيئة قاعدة بيانات المستخدمين",
            'ca': "Inicialitza Base de Dades d'Usuaris",
            'ro': "Initializeaza Baza de Date Utilizatori",
            'pt': "Inicializar Base de Dados de Utilizadores",
            'el': "Archikopoisisi Vasis Dedomenon Christon",
        },
        'btn_refresh': {
            'it': "Aggiorna",
            'en': "Refresh",
            'de': "Aktualisieren",
            'es': "Actualizar",
            'fr': "Actualiser",
            'ar': "تحديث",
            'ca': "Actualitza",
            'ro': "Actualizeaza",
            'pt': "Atualizar",
            'el': "Ananeosin",
        },
        'btn_close': {
            'it': "Chiudi",
            'en': "Close",
            'de': "Schliessen",
            'es': "Cerrar",
            'fr': "Fermer",
            'ar': "اغلاق",
            'ca': "Tanca",
            'ro': "Inchide",
            'pt': "Fechar",
            'el': "Kleisimo",
        },
        'user_list': {
            'it': "Lista Utenti",
            'en': "User List",
            'de': "Benutzerliste",
            'es': "Lista de Usuarios",
            'fr': "Liste des Utilisateurs",
            'ar': "قائمة المستخدمين",
            'ca': "Llista d'Usuaris",
            'ro': "Lista Utilizatorilor",
            'pt': "Lista de Utilizadores",
            'el': "Lista Christon",
        },
        'col_username': {
            'it': "Username", 'en': "Username", 'de': "Benutzername", 'es': "Usuario",
            'fr': "Identifiant", 'ar': "اسم المستخدم", 'ca': "Usuari", 'ro': "Utilizator",
            'pt': "Utilizador", 'el': "Onoma Christi",
        },
        'col_name': {
            'it': "Nome", 'en': "Name", 'de': "Name", 'es': "Nombre",
            'fr': "Nom", 'ar': "الاسم", 'ca': "Nom", 'ro': "Nume",
            'pt': "Nome", 'el': "Onoma",
        },
        'col_role': {
            'it': "Ruolo", 'en': "Role", 'de': "Rolle", 'es': "Rol",
            'fr': "Role", 'ar': "الدور", 'ca': "Rol", 'ro': "Rol",
            'pt': "Papel", 'el': "Rolos",
        },
        'col_email': {
            'it': "Email", 'en': "Email", 'de': "E-Mail", 'es': "Email",
            'fr': "Email", 'ar': "البريد الالكتروني", 'ca': "Correu", 'ro': "Email",
            'pt': "Email", 'el': "Email",
        },
        'col_active': {
            'it': "Attivo", 'en': "Active", 'de': "Aktiv", 'es': "Activo",
            'fr': "Actif", 'ar': "نشط", 'ca': "Actiu", 'ro': "Activ",
            'pt': "Ativo", 'el': "Energos",
        },
        'btn_new_user': {
            'it': "Nuovo Utente",
            'en': "New User",
            'de': "Neuer Benutzer",
            'es': "Nuevo Usuario",
            'fr': "Nouvel Utilisateur",
            'ar': "مستخدم جديد",
            'ca': "Nou Usuari",
            'ro': "Utilizator Nou",
            'pt': "Novo Utilizador",
            'el': "Neos Christis",
        },
        'btn_delete': {
            'it': "Elimina",
            'en': "Delete",
            'de': "Loschen",
            'es': "Eliminar",
            'fr': "Supprimer",
            'ar': "حذف",
            'ca': "Elimina",
            'ro': "Sterge",
            'pt': "Eliminar",
            'el': "Diagrafi",
        },
        'user_details': {
            'it': "Dettagli Utente",
            'en': "User Details",
            'de': "Benutzerdetails",
            'es': "Detalles del Usuario",
            'fr': "Details de l'Utilisateur",
            'ar': "تفاصيل المستخدم",
            'ca': "Detalls de l'Usuari",
            'ro': "Detalii Utilizator",
            'pt': "Detalhes do Utilizador",
            'el': "Stoicheia Christi",
        },
        'lbl_username': {
            'it': "Username:", 'en': "Username:", 'de': "Benutzername:", 'es': "Usuario:",
            'fr': "Identifiant:", 'ar': "اسم المستخدم:", 'ca': "Usuari:", 'ro': "Utilizator:",
            'pt': "Utilizador:", 'el': "Onoma Christi:",
        },
        'lbl_password': {
            'it': "Password:", 'en': "Password:", 'de': "Passwort:", 'es': "Contrasena:",
            'fr': "Mot de passe:", 'ar': "كلمة المرور:", 'ca': "Contrasenya:", 'ro': "Parola:",
            'pt': "Palavra-passe:", 'el': "Kodikos:",
        },
        'lbl_fullname': {
            'it': "Nome Completo:", 'en': "Full Name:", 'de': "Vollstandiger Name:", 'es': "Nombre Completo:",
            'fr': "Nom Complet:", 'ar': "الاسم الكامل:", 'ca': "Nom Complet:", 'ro': "Nume Complet:",
            'pt': "Nome Completo:", 'el': "Plires Onoma:",
        },
        'lbl_email': {
            'it': "Email:", 'en': "Email:", 'de': "E-Mail:", 'es': "Email:",
            'fr': "Email:", 'ar': "البريد الالكتروني:", 'ca': "Correu:", 'ro': "Email:",
            'pt': "Email:", 'el': "Email:",
        },
        'lbl_role': {
            'it': "Ruolo:", 'en': "Role:", 'de': "Rolle:", 'es': "Rol:",
            'fr': "Role:", 'ar': "الدور:", 'ca': "Rol:", 'ro': "Rol:",
            'pt': "Papel:", 'el': "Rolos:",
        },
        'lbl_status': {
            'it': "Stato:", 'en': "Status:", 'de': "Status:", 'es': "Estado:",
            'fr': "Statut:", 'ar': "الحالة:", 'ca': "Estat:", 'ro': "Stare:",
            'pt': "Estado:", 'el': "Katastasi:",
        },
        'lbl_notes': {
            'it': "Note:", 'en': "Notes:", 'de': "Notizen:", 'es': "Notas:",
            'fr': "Notes:", 'ar': "ملاحظات:", 'ca': "Notes:", 'ro': "Note:",
            'pt': "Notas:", 'el': "Simeiosis:",
        },
        'lbl_last_login': {
            'it': "Ultimo Accesso:", 'en': "Last Login:", 'de': "Letzter Zugriff:", 'es': "Ultimo Acceso:",
            'fr': "Derniere Connexion:", 'ar': "اخر دخول:", 'ca': "Ultim Acces:", 'ro': "Ultima Autentificare:",
            'pt': "Ultimo Acesso:", 'el': "Teleftaia Syndesi:",
        },
        'user_active': {
            'it': "Utente Attivo",
            'en': "User Active",
            'de': "Benutzer Aktiv",
            'es': "Usuario Activo",
            'fr': "Utilisateur Actif",
            'ar': "مستخدم نشط",
            'ca': "Usuari Actiu",
            'ro': "Utilizator Activ",
            'pt': "Utilizador Ativo",
            'el': "Energos Christis",
        },
        'password_placeholder': {
            'it': "Lascia vuoto per non cambiare",
            'en': "Leave empty to keep current",
            'de': "Leer lassen, um nicht zu andern",
            'es': "Dejar vacio para no cambiar",
            'fr': "Laisser vide pour ne pas changer",
            'ar': "اتركه فارغا للابقاء على الحالي",
            'ca': "Deixa buit per no canviar",
            'ro': "Lasati gol pentru a nu schimba",
            'pt': "Deixar vazio para nao alterar",
            'el': "Afiste keno gia na min allaxei",
        },
        'btn_save_user': {
            'it': "Salva Utente",
            'en': "Save User",
            'de': "Benutzer Speichern",
            'es': "Guardar Usuario",
            'fr': "Enregistrer Utilisateur",
            'ar': "حفظ المستخدم",
            'ca': "Desa Usuari",
            'ro': "Salveaza Utilizator",
            'pt': "Guardar Utilizador",
            'el': "Apothikefsi Christi",
        },
        'lbl_user': {
            'it': "Utente:", 'en': "User:", 'de': "Benutzer:", 'es': "Usuario:",
            'fr': "Utilisateur:", 'ar': "المستخدم:", 'ca': "Usuari:", 'ro': "Utilizator:",
            'pt': "Utilizador:", 'el': "Christis:",
        },
        'btn_apply_all': {
            'it': "Applica a Tutte le Tabelle",
            'en': "Apply to All Tables",
            'de': "Auf alle Tabellen anwenden",
            'es': "Aplicar a Todas las Tablas",
            'fr': "Appliquer a Toutes les Tables",
            'ar': "تطبيق على جميع الجداول",
            'ca': "Aplica a Totes les Taules",
            'ro': "Aplica la Toate Tabelele",
            'pt': "Aplicar a Todas as Tabelas",
            'el': "Efarmogi se Olous tous Pinakes",
        },
        'btn_save_permissions': {
            'it': "Salva Permessi",
            'en': "Save Permissions",
            'de': "Berechtigungen Speichern",
            'es': "Guardar Permisos",
            'fr': "Enregistrer Permissions",
            'ar': "حفظ الصلاحيات",
            'ca': "Desa Permisos",
            'ro': "Salveaza Permisiuni",
            'pt': "Guardar Permissoes",
            'el': "Apothikefsi Dikaiomaton",
        },
        'col_table': {
            'it': "Tabella", 'en': "Table", 'de': "Tabelle", 'es': "Tabla",
            'fr': "Table", 'ar': "الجدول", 'ca': "Taula", 'ro': "Tabel",
            'pt': "Tabela", 'el': "Pinakas",
        },
        'col_view': {
            'it': "Visualizza", 'en': "View", 'de': "Anzeigen", 'es': "Ver",
            'fr': "Voir", 'ar': "عرض", 'ca': "Veure", 'ro': "Vizualizeaza",
            'pt': "Ver", 'el': "Provoli",
        },
        'col_insert': {
            'it': "Inserisci", 'en': "Insert", 'de': "Einfugen", 'es': "Insertar",
            'fr': "Inserer", 'ar': "ادراج", 'ca': "Inserir", 'ro': "Insereaza",
            'pt': "Inserir", 'el': "Eisagogi",
        },
        'col_update': {
            'it': "Modifica", 'en': "Update", 'de': "Andern", 'es': "Modificar",
            'fr': "Modifier", 'ar': "تعديل", 'ca': "Modificar", 'ro': "Modifica",
            'pt': "Modificar", 'el': "Enimerosin",
        },
        'col_delete': {
            'it': "Elimina", 'en': "Delete", 'de': "Loschen", 'es': "Eliminar",
            'fr': "Supprimer", 'ar': "حذف", 'ca': "Eliminar", 'ro': "Sterge",
            'pt': "Eliminar", 'el': "Diagrafi",
        },
        'col_type': {
            'it': "Tipo", 'en': "Type", 'de': "Typ", 'es': "Tipo",
            'fr': "Type", 'ar': "النوع", 'ca': "Tipus", 'ro': "Tip",
            'pt': "Tipo", 'el': "Typos",
        },
        'quick_permissions': {
            'it': "Permessi Rapidi:", 'en': "Quick Permissions:", 'de': "Schnellberechtigungen:",
            'es': "Permisos Rapidos:", 'fr': "Permissions Rapides:", 'ar': "صلاحيات سريعة:",
            'ca': "Permisos Rapids:", 'ro': "Permisiuni Rapide:", 'pt': "Permissoes Rapidas:",
            'el': "Grigora Dikaiomata:",
        },
        'realtime_monitor': {
            'it': "Monitor Real-Time",
            'en': "Real-Time Monitor",
            'de': "Echtzeit-Monitor",
            'es': "Monitor en Tiempo Real",
            'fr': "Moniteur en Temps Reel",
            'ar': "مراقبة فورية",
            'ca': "Monitor en Temps Real",
            'ro': "Monitor in Timp Real",
            'pt': "Monitor em Tempo Real",
            'el': "Parakolouthisi Pragmatikou Chronou",
        },
        'col_user_monitor': {
            'it': "Utente", 'en': "User", 'de': "Benutzer", 'es': "Usuario",
            'fr': "Utilisateur", 'ar': "المستخدم", 'ca': "Usuari", 'ro': "Utilizator",
            'pt': "Utilizador", 'el': "Christis",
        },
        'col_table_monitor': {
            'it': "Tabella", 'en': "Table", 'de': "Tabelle", 'es': "Tabla",
            'fr': "Table", 'ar': "الجدول", 'ca': "Taula", 'ro': "Tabel",
            'pt': "Tabela", 'el': "Pinakas",
        },
        'col_record': {
            'it': "Record", 'en': "Record", 'de': "Datensatz", 'es': "Registro",
            'fr': "Enregistrement", 'ar': "سجل", 'ca': "Registre", 'ro': "Inregistrare",
            'pt': "Registo", 'el': "Eggraphi",
        },
        'col_action': {
            'it': "Azione", 'en': "Action", 'de': "Aktion", 'es': "Accion",
            'fr': "Action", 'ar': "اجراء", 'ca': "Accio", 'ro': "Actiune",
            'pt': "Acao", 'el': "Energeia",
        },
        'col_minutes': {
            'it': "Da Minuti", 'en': "Minutes", 'de': "Seit Minuten", 'es': "Minutos",
            'fr': "Depuis Minutes", 'ar': "دقائق", 'ca': "Des de Minuts", 'ro': "De Minute",
            'pt': "Minutos", 'el': "Lepta",
        },
        'col_ip': {
            'it': "IP", 'en': "IP", 'de': "IP", 'es': "IP",
            'fr': "IP", 'ar': "IP", 'ca': "IP", 'ro': "IP",
            'pt': "IP", 'el': "IP",
        },
        'col_status': {
            'it': "Stato", 'en': "Status", 'de': "Status", 'es': "Estado",
            'fr': "Statut", 'ar': "الحالة", 'ca': "Estat", 'ro': "Stare",
            'pt': "Estado", 'el': "Katastasi",
        },
        'auto_refresh': {
            'it': "Auto-refresh ogni 10 secondi",
            'en': "Auto-refresh every 10 seconds",
            'de': "Automatische Aktualisierung alle 10 Sekunden",
            'es': "Auto-actualizacion cada 10 segundos",
            'fr': "Actualisation auto toutes les 10 secondes",
            'ar': "تحديث تلقائي كل 10 ثوان",
            'ca': "Actualitzacio automatica cada 10 segons",
            'ro': "Actualizare automata la fiecare 10 secunde",
            'pt': "Atualizacao automatica a cada 10 segundos",
            'el': "Aftomati ananeosin kathe 10 defterolepdo",
        },
        'btn_unlock': {
            'it': "Sblocca Record Selezionato",
            'en': "Unlock Selected Record",
            'de': "Ausgewahlten Datensatz Entsperren",
            'es': "Desbloquear Registro Seleccionado",
            'fr': "Deverrouiller l'Enregistrement Selectionne",
            'ar': "فتح السجل المحدد",
            'ca': "Desbloqueja Registre Seleccionat",
            'ro': "Deblocheaza Inregistrarea Selectata",
            'pt': "Desbloquear Registo Selecionado",
            'el': "Xekleidoma Epilegmenis Eggrafis",
        },
        'access_log': {
            'it': "Log Accessi (ultime 24 ore)",
            'en': "Access Log (last 24 hours)",
            'de': "Zugriffsprotokoll (letzte 24 Stunden)",
            'es': "Registro de Accesos (ultimas 24 horas)",
            'fr': "Journal des Acces (dernieres 24 heures)",
            'ar': "سجل الوصول (اخر 24 ساعة)",
            'ca': "Registre d'Accessos (ultimes 24 hores)",
            'ro': "Jurnal Acces (ultimele 24 ore)",
            'pt': "Registo de Acessos (ultimas 24 horas)",
            'el': "Archeio Prosvaseon (teleftaies 24 ores)",
        },
        'col_timestamp': {
            'it': "Timestamp", 'en': "Timestamp", 'de': "Zeitstempel", 'es': "Marca de Tiempo",
            'fr': "Horodatage", 'ar': "الطابع الزمني", 'ca': "Marca de Temps", 'ro': "Marca Temporala",
            'pt': "Marca Temporal", 'el': "Chronosfragida",
        },
        'col_success': {
            'it': "Successo", 'en': "Success", 'de': "Erfolg", 'es': "Exito",
            'fr': "Succes", 'ar': "نجاح", 'ca': "Exit", 'ro': "Succes",
            'pt': "Sucesso", 'el': "Epitichia",
        },
        'col_error': {
            'it': "Errore", 'en': "Error", 'de': "Fehler", 'es': "Error",
            'fr': "Erreur", 'ar': "خطا", 'ca': "Error", 'ro': "Eroare",
            'pt': "Erro", 'el': "Sfalma",
        },
        'col_role_table': {
            'it': "Ruolo", 'en': "Role", 'de': "Rolle", 'es': "Rol",
            'fr': "Role", 'ar': "الدور", 'ca': "Rol", 'ro': "Rol",
            'pt': "Papel", 'el': "Rolos",
        },
        'col_description': {
            'it': "Descrizione", 'en': "Description", 'de': "Beschreibung", 'es': "Descripcion",
            'fr': "Description", 'ar': "الوصف", 'ca': "Descripcio", 'ro': "Descriere",
            'pt': "Descricao", 'el': "Perigrafi",
        },
        'col_system': {
            'it': "Sistema", 'en': "System", 'de': "System", 'es': "Sistema",
            'fr': "Systeme", 'ar': "النظام", 'ca': "Sistema", 'ro': "Sistem",
            'pt': "Sistema", 'el': "Systima",
        },
        'roles_info': {
            'it': "I ruoli di sistema (admin) non possono essere modificati.\nI permessi dei ruoli sono i default applicati agli utenti con quel ruolo.",
            'en': "System roles (admin) cannot be modified.\nRole permissions are the defaults applied to users with that role.",
            'de': "Systemrollen (admin) konnen nicht geandert werden.\nRollenberechtigungen sind die Standardwerte fur Benutzer mit dieser Rolle.",
            'es': "Los roles de sistema (admin) no se pueden modificar.\nLos permisos de rol son los predeterminados aplicados a los usuarios con ese rol.",
            'fr': "Les roles systeme (admin) ne peuvent pas etre modifies.\nLes permissions de role sont les valeurs par defaut appliquees aux utilisateurs ayant ce role.",
            'ar': "ادوار النظام (المشرف) لا يمكن تعديلها.\nصلاحيات الادوار هي الافتراضية المطبقة على المستخدمين بهذا الدور.",
            'ca': "Els rols de sistema (admin) no es poden modificar.\nEls permisos de rol son els predeterminats aplicats als usuaris amb aquest rol.",
            'ro': "Rolurile de sistem (admin) nu pot fi modificate.\nPermisiunile rolurilor sunt valorile implicite aplicate utilizatorilor cu acel rol.",
            'pt': "Os papeis de sistema (admin) nao podem ser modificados.\nAs permissoes de papel sao os valores predefinidos aplicados aos utilizadores com esse papel.",
            'el': "Oi roloi systimatos (admin) den mporoun na tropopoiithoun.\nTa dikaiomata rolon einai ta proepilogi pou efarmozondai stous christes me afton ton rolo.",
        },
        'access_denied': {
            'it': "Accesso Negato",
            'en': "Access Denied",
            'de': "Zugriff Verweigert",
            'es': "Acceso Denegado",
            'fr': "Acces Refuse",
            'ar': "الوصول مرفوض",
            'ca': "Acces Denegat",
            'ro': "Acces Refuzat",
            'pt': "Acesso Negado",
            'el': "Apagoreusi Prosvaseos",
        },
        'admin_only': {
            'it': "Solo gli amministratori possono accedere a questa funzione",
            'en': "Only administrators can access this function",
            'de': "Nur Administratoren konnen auf diese Funktion zugreifen",
            'es': "Solo los administradores pueden acceder a esta funcion",
            'fr': "Seuls les administrateurs peuvent acceder a cette fonction",
            'ar': "فقط المشرفون يمكنهم الوصول الى هذه الوظيفة",
            'ca': "Nomes els administradors poden accedir a aquesta funcio",
            'ro': "Doar administratorii pot accesa aceasta functie",
            'pt': "Apenas os administradores podem aceder a esta funcao",
            'el': "Mono oi diacheiristes mporoun na prosvasoun afti ti leitourgia",
        },
        'error': {
            'it': "Errore", 'en': "Error", 'de': "Fehler", 'es': "Error",
            'fr': "Erreur", 'ar': "خطا", 'ca': "Error", 'ro': "Eroare",
            'pt': "Erro", 'el': "Sfalma",
        },
        'success': {
            'it': "Successo", 'en': "Success", 'de': "Erfolg", 'es': "Exito",
            'fr': "Succes", 'ar': "نجاح", 'ca': "Exit", 'ro': "Succes",
            'pt': "Sucesso", 'el': "Epitichia",
        },
        'confirm': {
            'it': "Conferma", 'en': "Confirm", 'de': "Bestatigen", 'es': "Confirmar",
            'fr': "Confirmer", 'ar': "تاكيد", 'ca': "Confirma", 'ro': "Confirma",
            'pt': "Confirmar", 'el': "Epivevaiosin",
        },
        'table_not_found': {
            'it': "Tabella utenti non trovata",
            'en': "User table not found",
            'de': "Benutzertabelle nicht gefunden",
            'es': "Tabla de usuarios no encontrada",
            'fr': "Table utilisateurs non trouvee",
            'ar': "جدول المستخدمين غير موجود",
            'ca': "Taula d'usuaris no trobada",
            'ro': "Tabelul utilizatorilor nu a fost gasit",
            'pt': "Tabela de utilizadores nao encontrada",
            'el': "O pinakas christon den vrethike",
        },
        'run_update_script': {
            'it': "Esegui prima lo script di aggiornamento database",
            'en': "Run the database update script first",
            'de': "Fuhren Sie zuerst das Datenbank-Update-Skript aus",
            'es': "Ejecute primero el script de actualizacion de base de datos",
            'fr': "Executez d'abord le script de mise a jour de la base de donnees",
            'ar': "قم بتشغيل سكريبت تحديث قاعدة البيانات اولا",
            'ca': "Executeu primer l'script d'actualitzacio de base de dades",
            'ro': "Rulati mai intai scriptul de actualizare a bazei de date",
            'pt': "Execute primeiro o script de atualizacao da base de dados",
            'el': "Ekteleste proto to senario enimeroseon vaseon dedomenon",
        },
        'loading_users_error': {
            'it': "Errore caricamento utenti",
            'en': "Error loading users",
            'de': "Fehler beim Laden der Benutzer",
            'es': "Error al cargar usuarios",
            'fr': "Erreur de chargement des utilisateurs",
            'ar': "خطا في تحميل المستخدمين",
            'ca': "Error en carregar usuaris",
            'ro': "Eroare la incarcarea utilizatorilor",
            'pt': "Erro ao carregar utilizadores",
            'el': "Sfalma fortosis christon",
        },
        'loading_perms_error': {
            'it': "Errore caricamento permessi",
            'en': "Error loading permissions",
            'de': "Fehler beim Laden der Berechtigungen",
            'es': "Error al cargar permisos",
            'fr': "Erreur de chargement des permissions",
            'ar': "خطا في تحميل الصلاحيات",
            'ca': "Error en carregar permisos",
            'ro': "Eroare la incarcarea permisiunilor",
            'pt': "Erro ao carregar permissoes",
            'el': "Sfalma fortosis dikaiomaton",
        },
        'custom': {
            'it': "Personalizzato", 'en': "Custom", 'de': "Benutzerdefiniert", 'es': "Personalizado",
            'fr': "Personnalise", 'ar': "مخصص", 'ca': "Personalitzat", 'ro': "Personalizat",
            'pt': "Personalizado", 'el': "Prosarmosmeno",
        },
        'default': {
            'it': "Default", 'en': "Default", 'de': "Standard", 'es': "Predeterminado",
            'fr': "Par defaut", 'ar': "افتراضي", 'ca': "Predeterminat", 'ro': "Implicit",
            'pt': "Predefinido", 'el': "Proepilogi",
        },
        'view_not_exists': {
            'it': "La vista active_editing_sessions non esiste. Eseguire 'Applica Sistema Concorrenza' dalla configurazione.",
            'en': "The active_editing_sessions view does not exist. Run 'Apply Concurrency System' from configuration.",
            'de': "Die Ansicht active_editing_sessions existiert nicht. Fuhren Sie 'Konkurrenzsystem anwenden' aus der Konfiguration aus.",
            'es': "La vista active_editing_sessions no existe. Ejecute 'Aplicar Sistema de Concurrencia' desde la configuracion.",
            'fr': "La vue active_editing_sessions n'existe pas. Executez 'Appliquer Systeme de Concurrence' depuis la configuration.",
            'ar': "عرض active_editing_sessions غير موجود. قم بتشغيل 'تطبيق نظام التزامن' من الاعدادات.",
            'ca': "La vista active_editing_sessions no existeix. Executeu 'Aplica Sistema de Concurrencia' des de la configuracio.",
            'ro': "Vizualizarea active_editing_sessions nu exista. Rulati 'Aplica Sistemul de Concurenta' din configurare.",
            'pt': "A vista active_editing_sessions nao existe. Execute 'Aplicar Sistema de Concorrencia' a partir da configuracao.",
            'el': "I proepiskopisi active_editing_sessions den yparchi. Ekteleste 'Efarmogi Systimatos Syndromotitas' apo tis rythmiseis.",
        },
        'no_active_sessions': {
            'it': "Nessuna sessione di editing attiva al momento",
            'en': "No active editing sessions at this time",
            'de': "Derzeit keine aktiven Bearbeitungssitzungen",
            'es': "No hay sesiones de edicion activas en este momento",
            'fr': "Aucune session d'edition active pour le moment",
            'ar': "لا توجد جلسات تحرير نشطة حاليا",
            'ca': "No hi ha sessions d'edicio actives en aquest moment",
            'ro': "Nu exista sesiuni de editare active in acest moment",
            'pt': "Nenhuma sessao de edicao ativa neste momento",
            'el': "Den yparxoun energes synedries epimelias afti ti stigmi",
        },
        'status_active': {
            'it': "Attivo", 'en': "Active", 'de': "Aktiv", 'es': "Activo",
            'fr': "Actif", 'ar': "نشط", 'ca': "Actiu", 'ro': "Activ",
            'pt': "Ativo", 'el': "Energos",
        },
        'status_ongoing': {
            'it': "In corso", 'en': "Ongoing", 'de': "Laufend", 'es': "En curso",
            'fr': "En cours", 'ar': "جار", 'ca': "En curs", 'ro': "In curs",
            'pt': "Em curso", 'el': "Se exelixi",
        },
        'status_stalled': {
            'it': "Stallo", 'en': "Stalled", 'de': "Blockiert", 'es': "Estancado",
            'fr': "Bloque", 'ar': "متوقف", 'ca': "Estancat", 'ro': "Blocat",
            'pt': "Bloqueado", 'el': "Mplokare",
        },
        'log_not_exists': {
            'it': "La tabella pyarchinit_access_log non esiste. Eseguire 'Inizializza Database Utenti' per crearla.",
            'en': "The pyarchinit_access_log table does not exist. Run 'Initialize User Database' to create it.",
            'de': "Die Tabelle pyarchinit_access_log existiert nicht. Fuhren Sie 'Benutzerdatenbank initialisieren' aus.",
            'es': "La tabla pyarchinit_access_log no existe. Ejecute 'Inicializar Base de Datos de Usuarios' para crearla.",
            'fr': "La table pyarchinit_access_log n'existe pas. Executez 'Initialiser la Base de Donnees Utilisateurs' pour la creer.",
            'ar': "جدول pyarchinit_access_log غير موجود. قم بتشغيل 'تهيئة قاعدة بيانات المستخدمين' لانشائه.",
            'ca': "La taula pyarchinit_access_log no existeix. Executeu 'Inicialitza Base de Dades d'Usuaris' per crear-la.",
            'ro': "Tabelul pyarchinit_access_log nu exista. Rulati 'Initializeaza Baza de Date Utilizatori' pentru a-l crea.",
            'pt': "A tabela pyarchinit_access_log nao existe. Execute 'Inicializar Base de Dados de Utilizadores' para cria-la.",
            'el': "O pinakas pyarchinit_access_log den yparchi. Ekteleste 'Archikopoisisi Vasis Dedomenon Christon' gia na ton dimiourgisite.",
        },
        'no_logs': {
            'it': "Nessun log di accesso nelle ultime 24 ore",
            'en': "No access log entries in the last 24 hours",
            'de': "Keine Zugriffsprotokolle in den letzten 24 Stunden",
            'es': "Sin registros de acceso en las ultimas 24 horas",
            'fr': "Aucune entree de journal d'acces dans les dernieres 24 heures",
            'ar': "لا توجد سجلات وصول في اخر 24 ساعة",
            'ca': "Sense registres d'acces en les ultimes 24 hores",
            'ro': "Nu exista inregistrari in jurnalul de acces in ultimele 24 de ore",
            'pt': "Sem registos de acesso nas ultimas 24 horas",
            'el': "Den yparxoun katachoreseis prosvaseon tis teleftaies 24 ores",
        },
        'system_role': {
            'it': "Sistema", 'en': "System", 'de': "System", 'es': "Sistema",
            'fr': "Systeme", 'ar': "نظام", 'ca': "Sistema", 'ro': "Sistem",
            'pt': "Sistema", 'el': "Systima",
        },
        'custom_role': {
            'it': "Custom", 'en': "Custom", 'de': "Benutzerdefiniert", 'es': "Personalizado",
            'fr': "Personnalise", 'ar': "مخصص", 'ca': "Personalitzat", 'ro': "Personalizat",
            'pt': "Personalizado", 'el': "Prosarmosmeno",
        },
        'never_logged_in': {
            'it': "Mai effettuato", 'en': "Never", 'de': "Nie", 'es': "Nunca",
            'fr': "Jamais", 'ar': "ابدا", 'ca': "Mai", 'ro': "Niciodata",
            'pt': "Nunca", 'el': "Pote",
        },
        'cannot_delete_admin': {
            'it': "Non puoi eliminare l'utente admin!",
            'en': "You cannot delete the admin user!",
            'de': "Der Admin-Benutzer kann nicht geloscht werden!",
            'es': "No puede eliminar el usuario admin!",
            'fr': "Vous ne pouvez pas supprimer l'utilisateur admin!",
            'ar': "لا يمكنك حذف مستخدم المشرف!",
            'ca': "No podeu eliminar l'usuari admin!",
            'ro': "Nu puteti sterge utilizatorul admin!",
            'pt': "Nao pode eliminar o utilizador admin!",
            'el': "Den mporeis na diagrapseis ton christi admin!",
        },
        'confirm_delete_user': {
            'it': "Eliminare l'utente {username}?",
            'en': "Delete user {username}?",
            'de': "Benutzer {username} loschen?",
            'es': "Eliminar el usuario {username}?",
            'fr': "Supprimer l'utilisateur {username}?",
            'ar': "حذف المستخدم {username}؟",
            'ca': "Eliminar l'usuari {username}?",
            'ro': "Stergeti utilizatorul {username}?",
            'pt': "Eliminar o utilizador {username}?",
            'el': "Diagrafi tou christi {username};",
        },
        'user_deleted': {
            'it': "Utente eliminato",
            'en': "User deleted",
            'de': "Benutzer geloscht",
            'es': "Usuario eliminado",
            'fr': "Utilisateur supprime",
            'ar': "تم حذف المستخدم",
            'ca': "Usuari eliminat",
            'ro': "Utilizator sters",
            'pt': "Utilizador eliminado",
            'el': "O christis diagrafike",
        },
        'delete_error': {
            'it': "Errore eliminazione",
            'en': "Deletion error",
            'de': "Loschfehler",
            'es': "Error de eliminacion",
            'fr': "Erreur de suppression",
            'ar': "خطا في الحذف",
            'ca': "Error d'eliminacio",
            'ro': "Eroare la stergere",
            'pt': "Erro de eliminacao",
            'el': "Sfalma diagrafis",
        },
        'username_required': {
            'it': "Username obbligatorio!",
            'en': "Username is required!",
            'de': "Benutzername ist erforderlich!",
            'es': "El nombre de usuario es obligatorio!",
            'fr': "L'identifiant est obligatoire!",
            'ar': "اسم المستخدم مطلوب!",
            'ca': "L'usuari es obligatori!",
            'ro': "Numele de utilizator este obligatoriu!",
            'pt': "O nome de utilizador e obrigatorio!",
            'el': "To onoma christi einai apardaitito!",
        },
        'password_required_new': {
            'it': "Password obbligatoria per nuovo utente!",
            'en': "Password is required for a new user!",
            'de': "Passwort ist fur neue Benutzer erforderlich!",
            'es': "La contrasena es obligatoria para un nuevo usuario!",
            'fr': "Le mot de passe est obligatoire pour un nouvel utilisateur!",
            'ar': "كلمة المرور مطلوبة للمستخدم الجديد!",
            'ca': "La contrasenya es obligatoria per a un nou usuari!",
            'ro': "Parola este obligatorie pentru un utilizator nou!",
            'pt': "A palavra-passe e obrigatoria para um novo utilizador!",
            'el': "O kodikos einai aparaititos gia neo christi!",
        },
        'user_saved': {
            'it': "Utente salvato correttamente e creato in PostgreSQL!",
            'en': "User saved successfully and created in PostgreSQL!",
            'de': "Benutzer erfolgreich gespeichert und in PostgreSQL erstellt!",
            'es': "Usuario guardado correctamente y creado en PostgreSQL!",
            'fr': "Utilisateur enregistre et cree dans PostgreSQL avec succes!",
            'ar': "تم حفظ المستخدم بنجاح وانشاؤه في PostgreSQL!",
            'ca': "Usuari desat correctament i creat a PostgreSQL!",
            'ro': "Utilizator salvat cu succes si creat in PostgreSQL!",
            'pt': "Utilizador guardado com sucesso e criado no PostgreSQL!",
            'el': "O christis apothikeftike kai dimiourgithike sto PostgreSQL!",
        },
        'save_error': {
            'it': "Errore salvataggio",
            'en': "Save error",
            'de': "Speicherfehler",
            'es': "Error al guardar",
            'fr': "Erreur d'enregistrement",
            'ar': "خطا في الحفظ",
            'ca': "Error en desar",
            'ro': "Eroare la salvare",
            'pt': "Erro ao guardar",
            'el': "Sfalma apothikefsis",
        },
        'select_user': {
            'it': "Seleziona un utente",
            'en': "Select a user",
            'de': "Wahlen Sie einen Benutzer",
            'es': "Seleccione un usuario",
            'fr': "Selectionnez un utilisateur",
            'ar': "اختر مستخدما",
            'ca': "Seleccioneu un usuari",
            'ro': "Selectati un utilizator",
            'pt': "Selecione um utilizador",
            'el': "Epilexte enan christi",
        },
        'user_not_found': {
            'it': "Utente non trovato",
            'en': "User not found",
            'de': "Benutzer nicht gefunden",
            'es': "Usuario no encontrado",
            'fr': "Utilisateur non trouve",
            'ar': "المستخدم غير موجود",
            'ca': "Usuari no trobat",
            'ro': "Utilizator negasit",
            'pt': "Utilizador nao encontrado",
            'el': "O christis den vrethike",
        },
        'permissions_saved': {
            'it': "Permessi salvati correttamente e sincronizzati con PostgreSQL!",
            'en': "Permissions saved successfully and synced with PostgreSQL!",
            'de': "Berechtigungen erfolgreich gespeichert und mit PostgreSQL synchronisiert!",
            'es': "Permisos guardados correctamente y sincronizados con PostgreSQL!",
            'fr': "Permissions enregistrees et synchronisees avec PostgreSQL avec succes!",
            'ar': "تم حفظ الصلاحيات بنجاح ومزامنتها مع PostgreSQL!",
            'ca': "Permisos desats correctament i sincronitzats amb PostgreSQL!",
            'ro': "Permisiuni salvate cu succes si sincronizate cu PostgreSQL!",
            'pt': "Permissoes guardadas com sucesso e sincronizadas com o PostgreSQL!",
            'el': "Ta dikaiomata apothikeftikan kai sygchronistikan me to PostgreSQL!",
        },
        'permissions_save_error': {
            'it': "Errore salvataggio permessi",
            'en': "Error saving permissions",
            'de': "Fehler beim Speichern der Berechtigungen",
            'es': "Error al guardar permisos",
            'fr': "Erreur d'enregistrement des permissions",
            'ar': "خطا في حفظ الصلاحيات",
            'ca': "Error en desar permisos",
            'ro': "Eroare la salvarea permisiunilor",
            'pt': "Erro ao guardar permissoes",
            'el': "Sfalma apothikefsis dikaiomaton",
        },
        'confirm_apply_all': {
            'it': "Applicare questi permessi a TUTTE le tabelle per {username}?",
            'en': "Apply these permissions to ALL tables for {username}?",
            'de': "Diese Berechtigungen auf ALLE Tabellen fur {username} anwenden?",
            'es': "Aplicar estos permisos a TODAS las tablas para {username}?",
            'fr': "Appliquer ces permissions a TOUTES les tables pour {username}?",
            'ar': "تطبيق هذه الصلاحيات على جميع الجداول لـ {username}؟",
            'ca': "Aplicar aquests permisos a TOTES les taules per a {username}?",
            'ro': "Aplicati aceste permisiuni la TOATE tabelele pentru {username}?",
            'pt': "Aplicar estas permissoes a TODAS as tabelas para {username}?",
            'el': "Efarmogi afton ton dikaiomaton se OLOUS tous pinakes gia {username};",
        },
        'permissions_applied': {
            'it': "Permessi applicati!",
            'en': "Permissions applied!",
            'de': "Berechtigungen angewendet!",
            'es': "Permisos aplicados!",
            'fr': "Permissions appliquees!",
            'ar': "تم تطبيق الصلاحيات!",
            'ca': "Permisos aplicats!",
            'ro': "Permisiuni aplicate!",
            'pt': "Permissoes aplicadas!",
            'el': "Ta dikaiomata efarmostikan!",
        },
        'apply_error': {
            'it': "Errore applicazione permessi",
            'en': "Error applying permissions",
            'de': "Fehler beim Anwenden der Berechtigungen",
            'es': "Error al aplicar permisos",
            'fr': "Erreur d'application des permissions",
            'ar': "خطا في تطبيق الصلاحيات",
            'ca': "Error en aplicar permisos",
            'ro': "Eroare la aplicarea permisiunilor",
            'pt': "Erro ao aplicar permissoes",
            'el': "Sfalma efarmogis dikaiomaton",
        },
        'confirm_unlock': {
            'it': "Sbloccare forzatamente il record {record} in {table} (bloccato da {user})?",
            'en': "Force unlock record {record} in {table} (locked by {user})?",
            'de': "Datensatz {record} in {table} gewaltsam entsperren (gesperrt von {user})?",
            'es': "Desbloquear forzosamente el registro {record} en {table} (bloqueado por {user})?",
            'fr': "Deverrouiller de force l'enregistrement {record} dans {table} (verrouille par {user})?",
            'ar': "فتح السجل {record} قسريا في {table} (مقفل بواسطة {user})؟",
            'ca': "Desbloquejar forcosament el registre {record} a {table} (bloquejat per {user})?",
            'ro': "Deblocati fortat inregistrarea {record} in {table} (blocata de {user})?",
            'pt': "Desbloquear forcadamente o registo {record} em {table} (bloqueado por {user})?",
            'el': "Exanancastiko xekleidoma eggrafis {record} ston pinaka {table} (kleidomeno apo {user});",
        },
        'record_unlocked': {
            'it': "Record sbloccato!",
            'en': "Record unlocked!",
            'de': "Datensatz entsperrt!",
            'es': "Registro desbloqueado!",
            'fr': "Enregistrement deverrouille!",
            'ar': "تم فتح السجل!",
            'ca': "Registre desbloquejat!",
            'ro': "Inregistrare deblocata!",
            'pt': "Registo desbloqueado!",
            'el': "I eggrafi xekliodothike!",
        },
        'unlock_error': {
            'it': "Errore sblocco",
            'en': "Unlock error",
            'de': "Entsperrfehler",
            'es': "Error de desbloqueo",
            'fr': "Erreur de deverrouillage",
            'ar': "خطا في فتح القفل",
            'ca': "Error de desbloqueig",
            'ro': "Eroare la deblocare",
            'pt': "Erro de desbloqueio",
            'el': "Sfalma xekleidomatos",
        },
        'confirm_init_db': {
            'it': "Vuoi creare le tabelle del sistema utenti?\nQuesta operazione creera:\n- pyarchinit_users (utenti)\n- pyarchinit_permissions (permessi)\n- pyarchinit_roles (ruoli)\n- pyarchinit_access_log (log accessi)",
            'en': "Do you want to create the user system tables?\nThis operation will create:\n- pyarchinit_users (users)\n- pyarchinit_permissions (permissions)\n- pyarchinit_roles (roles)\n- pyarchinit_access_log (access log)",
            'de': "Mochten Sie die Benutzersystemtabellen erstellen?\nDieser Vorgang erstellt:\n- pyarchinit_users (Benutzer)\n- pyarchinit_permissions (Berechtigungen)\n- pyarchinit_roles (Rollen)\n- pyarchinit_access_log (Zugriffsprotokoll)",
            'es': "Desea crear las tablas del sistema de usuarios?\nEsta operacion creara:\n- pyarchinit_users (usuarios)\n- pyarchinit_permissions (permisos)\n- pyarchinit_roles (roles)\n- pyarchinit_access_log (registro de accesos)",
            'fr': "Voulez-vous creer les tables du systeme utilisateurs?\nCette operation creera:\n- pyarchinit_users (utilisateurs)\n- pyarchinit_permissions (permissions)\n- pyarchinit_roles (roles)\n- pyarchinit_access_log (journal des acces)",
            'ar': "هل تريد انشاء جداول نظام المستخدمين؟\nستنشئ هذه العملية:\n- pyarchinit_users (المستخدمون)\n- pyarchinit_permissions (الصلاحيات)\n- pyarchinit_roles (الادوار)\n- pyarchinit_access_log (سجل الوصول)",
            'ca': "Voleu crear les taules del sistema d'usuaris?\nAquesta operacio creara:\n- pyarchinit_users (usuaris)\n- pyarchinit_permissions (permisos)\n- pyarchinit_roles (rols)\n- pyarchinit_access_log (registre d'accessos)",
            'ro': "Doriti sa creati tabelele sistemului de utilizatori?\nAceasta operatiune va crea:\n- pyarchinit_users (utilizatori)\n- pyarchinit_permissions (permisiuni)\n- pyarchinit_roles (roluri)\n- pyarchinit_access_log (jurnal acces)",
            'pt': "Deseja criar as tabelas do sistema de utilizadores?\nEsta operacao criara:\n- pyarchinit_users (utilizadores)\n- pyarchinit_permissions (permissoes)\n- pyarchinit_roles (papeis)\n- pyarchinit_access_log (registo de acessos)",
            'el': "Thelete na dimiourgisete tous pinakes systimatos christon?\nAfti i leitourgia tha dimiourgisei:\n- pyarchinit_users (christes)\n- pyarchinit_permissions (dikaiomata)\n- pyarchinit_roles (roloi)\n- pyarchinit_access_log (archeio prosvaseon)",
        },
        'tables_created': {
            'it': "Tabelle create con successo!\nOra puoi iniziare a gestire gli utenti.",
            'en': "Tables created successfully!\nYou can now start managing users.",
            'de': "Tabellen erfolgreich erstellt!\nSie konnen jetzt mit der Benutzerverwaltung beginnen.",
            'es': "Tablas creadas con exito!\nAhora puede empezar a gestionar usuarios.",
            'fr': "Tables creees avec succes!\nVous pouvez maintenant commencer a gerer les utilisateurs.",
            'ar': "تم انشاء الجداول بنجاح!\nيمكنك الان البدء في ادارة المستخدمين.",
            'ca': "Taules creades amb exit!\nAra podeu comencar a gestionar usuaris.",
            'ro': "Tabele create cu succes!\nAcum puteti incepe sa gestionati utilizatorii.",
            'pt': "Tabelas criadas com sucesso!\nAgora pode comecar a gerir utilizadores.",
            'el': "Oi pinakes dimiourgithikan me epitichia!\nMporeite tora na archisete ti diacheirisi christon.",
        },
        'table_creation_error': {
            'it': "Errore durante la creazione delle tabelle",
            'en': "Error creating tables",
            'de': "Fehler beim Erstellen der Tabellen",
            'es': "Error al crear las tablas",
            'fr': "Erreur lors de la creation des tables",
            'ar': "خطا اثناء انشاء الجداول",
            'ca': "Error durant la creacio de les taules",
            'ro': "Eroare la crearea tabelelor",
            'pt': "Erro ao criar as tabelas",
            'el': "Sfalma kata ti dimiourgia ton pinakon",
        },
        'authorized_sites': {
            'it': "Siti autorizzati",
            'en': "Authorized Sites",
            'de': "Autorisierte Fundorte",
            'es': "Sitios autorizados",
            'fr': "Sites autorises",
            'ar': "المواقع المصرح بها",
            'ca': "Llocs autoritzats",
            'ro': "Site-uri autorizate",
            'pt': "Sitios autorizados",
            'el': "Exousiodotimenes Theseis",
        },
        'select_all': {
            'it': "Seleziona tutti",
            'en': "Select All",
            'de': "Alle auswaehlen",
            'es': "Seleccionar todos",
            'fr': "Tout selectionner",
            'ar': "تحديد الكل",
            'ca': "Selecciona tots",
            'ro': "Selecteaza tot",
            'pt': "Selecionar tudo",
            'el': "Epilogi olon",
        },
        'deselect_all': {
            'it': "Deseleziona tutti",
            'en': "Deselect All",
            'de': "Alle abwaehlen",
            'es': "Deseleccionar todos",
            'fr': "Tout deselectionner",
            'ar': "الغاء تحديد الكل",
            'ca': "Desselecciona tots",
            'ro': "Deselecteaza tot",
            'pt': "Desselecionar tudo",
            'el': "Apoepilogi olon",
        },
        'sites_empty_hint': {
            'it': "Vuoto = accesso a tutti i siti",
            'en': "Empty = access to all sites",
            'de': "Leer = Zugriff auf alle Fundorte",
            'es': "Vacio = acceso a todos los sitios",
            'fr': "Vide = acces a tous les sites",
            'ar': "فارغ = الوصول لجميع المواقع",
            'ca': "Buit = acces a tots els llocs",
            'ro': "Gol = acces la toate site-urile",
            'pt': "Vazio = acesso a todos os sitios",
            'el': "Keno = prosvasi se oles tis theseis",
        },
    }

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager

        # Detect language
        self.L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if self.L not in ('it', 'en', 'de', 'es', 'fr', 'ar', 'ca', 'ro', 'pt', 'el'):
            self.L = 'en'

        # Get database username from QGIS settings, fallback to OS username
        s = QgsSettings()
        self.current_user = s.value('pyArchInit/current_user', '', type=str)
        if not self.current_user:
            # Fallback: try to get from database connection
            self.current_user = getpass.getuser()
        # Also store the database connection username
        self.db_username = self._get_db_username()

        # Verifica se l'utente è admin
        if not self.check_admin_access():
            QMessageBox.critical(self, self.tr_('access_denied'),
                               self.tr_('admin_only'))
            self.close()
            return

        self.init_ui()

        # Apply theme and add toggle button
        try:
            from ..modules.utility.pyarchinit_theme_manager import ThemeManager
            ThemeManager.apply_theme(self)
            self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)
        except Exception:
            pass

        self.load_data()

    def _get_db_username(self):
        """Get the database connection username"""
        # First try from settings (saved by pyarchinitConfigDialog)
        try:
            s = QgsSettings()
            db_username = s.value('pyArchInit/db_username', '', type=str)
            if db_username:
                return db_username
        except:
            pass

        # Fallback: query database directly
        try:
            query = "SELECT current_user"
            result = self.db_manager.execute_sql(query)
            if result and result[0][0]:
                return result[0][0]
        except:
            pass
        return ''

    def tr_(self, key, **kwargs):
        """Get translated string for current language"""
        t = self.TRANSLATIONS.get(key, {})
        text = t.get(self.L, t.get('en', key))
        if kwargs:
            text = text.format(**kwargs)
        return text

    def check_admin_access(self):
        """Verifica se l'utente corrente è admin"""
        # Debug info
        print(f"Admin access check - current_user: {self.current_user}, db_username: {self.db_username}")

        # Prima verifica: se siamo collegati come 'postgres' (superuser database)
        if self.db_username:
            db_user_lower = self.db_username.lower()
            if db_user_lower == 'postgres' or db_user_lower.startswith('postgres.'):
                print(f"Admin access granted - database superuser: {self.db_username}")
                return True

        # Seconda verifica: controlla nella tabella pyarchinit_users
        try:
            # Check if table exists first
            check_table = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'pyarchinit_users'
                )
            """
            table_exists = self.db_manager.execute_sql(check_table)

            if not table_exists or not table_exists[0][0]:
                # Table doesn't exist - allow admin for initial setup
                print("Admin access granted - pyarchinit_users table doesn't exist")
                return True

            # Query per verificare ruolo admin - check both current_user and db_username
            usernames_to_check = [self.current_user, self.db_username]
            usernames_to_check = [u for u in usernames_to_check if u]  # Remove empty strings

            for username in usernames_to_check:
                query = """
                    SELECT role FROM pyarchinit_users
                    WHERE LOWER(username) = LOWER(:username) AND is_active = TRUE
                """
                result = self.db_manager.execute_sql(query, {'username': username})
                if result and len(result) > 0:
                    if result[0][0] == 'admin':
                        print(f"Admin access granted - user '{username}' has admin role")
                        return True
                    else:
                        print(f"Admin access denied - user '{username}' has role: {result[0][0]}")
                        return False

            # User not found in table
            print(f"Admin access denied - user not found in pyarchinit_users")
            return False

        except Exception as e:
            # If query fails, allow admin for backward compatibility
            print(f"Admin check query failed ({e}), defaulting to admin")
            return True

    def init_ui(self):
        """Inizializza interfaccia"""
        self.setWindowTitle(self.tr_('window_title'))
        self.setMinimumSize(1200, 700)

        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel(self.tr_('header_title'))
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #64B5F6;")
        header_layout.addWidget(title)

        # Show both PyArchInit user and database user for clarity
        user_display = self.current_user if self.current_user else self.db_username
        db_display = f" [DB: {self.db_username}]" if self.db_username and self.db_username != user_display else ""
        self.status_label = QLabel(f"{self.tr_('connected_as')}: {user_display}{db_display} (Admin)")
        self.status_label.setStyleSheet("color: #66BB6A;")
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Tab widget
        self.tabs = QTabWidget()

        # Tab 1: Users
        self.users_tab = self.create_users_tab()
        self.tabs.addTab(self.users_tab, self.tr_('tab_users'))

        # Tab 2: Permissions
        self.permissions_tab = self.create_permissions_tab()
        self.tabs.addTab(self.permissions_tab, self.tr_('tab_permissions'))

        # Tab 3: Monitor
        self.monitor_tab = self.create_monitor_tab()
        self.tabs.addTab(self.monitor_tab, self.tr_('tab_monitor'))

        # Tab 4: Roles
        self.roles_tab = self.create_roles_tab()
        self.tabs.addTab(self.roles_tab, self.tr_('tab_roles'))

        layout.addWidget(self.tabs)

        # Footer buttons
        footer_layout = QHBoxLayout()

        self.init_db_btn = QPushButton(self.tr_('btn_init_db'))
        self.init_db_btn.clicked.connect(self.initialize_user_tables)
        self.init_db_btn.setStyleSheet("background-color: #FF9800; color: white;")

        self.refresh_btn = QPushButton(self.tr_('btn_refresh'))
        self.refresh_btn.clicked.connect(self.load_data)

        self.close_btn = QPushButton(self.tr_('btn_close'))
        self.close_btn.clicked.connect(self.close)

        footer_layout.addWidget(self.init_db_btn)
        footer_layout.addWidget(self.refresh_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self.close_btn)

        layout.addLayout(footer_layout)
        self.setLayout(layout)

    def create_users_tab(self):
        """Crea tab gestione utenti"""
        widget = QWidget()
        layout = QHBoxLayout()

        # Left: User list
        left_panel = QGroupBox(self.tr_('user_list'))
        left_layout = QVBoxLayout()

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            self.tr_('col_username'), self.tr_('col_name'), self.tr_('col_role'),
            self.tr_('col_email'), self.tr_('col_active')
        ])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.itemSelectionChanged.connect(self.on_user_selected)

        left_layout.addWidget(self.users_table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton(self.tr_('btn_new_user'))
        self.add_user_btn.clicked.connect(self.add_new_user)
        self.delete_user_btn = QPushButton(self.tr_('btn_delete'))
        self.delete_user_btn.clicked.connect(self.delete_user)
        self.refresh_btn = QPushButton(self.tr_('btn_refresh'))
        self.refresh_btn.clicked.connect(self.load_data)

        btn_layout.addWidget(self.add_user_btn)
        btn_layout.addWidget(self.delete_user_btn)
        btn_layout.addWidget(self.refresh_btn)
        left_layout.addLayout(btn_layout)

        left_panel.setLayout(left_layout)

        # Right: User details
        right_panel = QGroupBox(self.tr_('user_details'))
        right_layout = QFormLayout()

        self.username_edit = QLineEdit()
        self.fullname_edit = QLineEdit()
        self.email_edit = QLineEdit()

        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "responsabile", "archeologo", "studente", "guest"])

        self.active_check = QCheckBox(self.tr_('user_active'))

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText(self.tr_('password_placeholder'))

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)

        right_layout.addRow(self.tr_('lbl_username'), self.username_edit)
        right_layout.addRow(self.tr_('lbl_password'), self.password_edit)
        right_layout.addRow(self.tr_('lbl_fullname'), self.fullname_edit)
        right_layout.addRow(self.tr_('lbl_email'), self.email_edit)
        right_layout.addRow(self.tr_('lbl_role'), self.role_combo)
        right_layout.addRow(self.tr_('lbl_status'), self.active_check)
        right_layout.addRow(self.tr_('lbl_notes'), self.notes_edit)

        # Authorized sites section
        sites_group = QGroupBox(self.tr_('authorized_sites'))
        sites_vlayout = QVBoxLayout()

        # Hint label
        sites_hint = QLabel(self.tr_('sites_empty_hint'))
        sites_hint.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        sites_vlayout.addWidget(sites_hint)

        # Select All / Deselect All buttons
        sites_btn_layout = QHBoxLayout()
        self.select_all_sites_btn = QPushButton(self.tr_('select_all'))
        self.deselect_all_sites_btn = QPushButton(self.tr_('deselect_all'))
        self.select_all_sites_btn.clicked.connect(self._select_all_sites)
        self.deselect_all_sites_btn.clicked.connect(self._deselect_all_sites)
        sites_btn_layout.addWidget(self.select_all_sites_btn)
        sites_btn_layout.addWidget(self.deselect_all_sites_btn)
        sites_vlayout.addLayout(sites_btn_layout)

        # Site list widget with checkboxes
        self.site_list_widget = QListWidget()
        self.site_list_widget.setMaximumHeight(150)
        sites_vlayout.addWidget(self.site_list_widget)

        sites_group.setLayout(sites_vlayout)
        right_layout.addRow(sites_group)

        # Populate sites list
        self._populate_site_list()

        # Last login info
        self.last_login_label = QLabel("-")
        right_layout.addRow(self.tr_('lbl_last_login'), self.last_login_label)

        # Add save button for user
        self.save_user_btn = QPushButton(self.tr_('btn_save_user'))
        self.save_user_btn.clicked.connect(self.save_changes)
        self.save_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        right_layout.addRow("", self.save_user_btn)

        right_panel.setLayout(right_layout)

        # Add to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        widget.setLayout(layout)

        return widget

    def create_permissions_tab(self):
        """Crea tab gestione permessi"""
        widget = QWidget()
        layout = QVBoxLayout()

        # User selector
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr_('lbl_user')))

        self.perm_user_combo = QComboBox()
        self.perm_user_combo.currentTextChanged.connect(self.load_user_permissions)
        top_layout.addWidget(self.perm_user_combo)

        self.perm_role_label = QLabel()
        self.perm_role_label.setStyleSheet("font-weight: bold; color: #64B5F6;")
        top_layout.addWidget(self.perm_role_label)

        top_layout.addStretch()

        self.apply_to_all_btn = QPushButton(self.tr_('btn_apply_all'))
        self.apply_to_all_btn.clicked.connect(self.apply_permissions_to_all)
        top_layout.addWidget(self.apply_to_all_btn)

        # Add save button for permissions
        self.save_permissions_btn = QPushButton(self.tr_('btn_save_permissions'))
        self.save_permissions_btn.clicked.connect(self.save_permissions)
        self.save_permissions_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        top_layout.addWidget(self.save_permissions_btn)

        layout.addLayout(top_layout)

        # Permissions table
        self.permissions_table = QTableWidget()
        self.permissions_table.setColumnCount(6)
        self.permissions_table.setHorizontalHeaderLabels([
            self.tr_('col_table'), self.tr_('col_view'), self.tr_('col_insert'),
            self.tr_('col_update'), self.tr_('col_delete'), self.tr_('col_type')
        ])

        header = self.permissions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        layout.addWidget(self.permissions_table)

        # Quick permissions
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel(self.tr_('quick_permissions')))

        self.quick_view = QCheckBox(self.tr_('col_view'))
        self.quick_insert = QCheckBox(self.tr_('col_insert'))
        self.quick_update = QCheckBox(self.tr_('col_update'))
        self.quick_delete = QCheckBox(self.tr_('col_delete'))

        quick_layout.addWidget(self.quick_view)
        quick_layout.addWidget(self.quick_insert)
        quick_layout.addWidget(self.quick_update)
        quick_layout.addWidget(self.quick_delete)

        quick_layout.addStretch()
        layout.addLayout(quick_layout)

        widget.setLayout(layout)
        return widget

    def create_monitor_tab(self):
        """Crea tab monitor attività"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Real-time monitor
        monitor_group = QGroupBox(self.tr_('realtime_monitor'))
        monitor_layout = QVBoxLayout()

        self.monitor_table = QTableWidget()
        self.monitor_table.setColumnCount(7)
        self.monitor_table.setHorizontalHeaderLabels([
            self.tr_('col_user_monitor'), self.tr_('col_table_monitor'), self.tr_('col_record'),
            self.tr_('col_action'), self.tr_('col_minutes'), self.tr_('col_ip'), self.tr_('col_status')
        ])

        monitor_layout.addWidget(self.monitor_table)

        # Auto-refresh
        refresh_layout = QHBoxLayout()
        self.auto_refresh_check = QCheckBox(self.tr_('auto_refresh'))
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        refresh_layout.addWidget(self.auto_refresh_check)

        self.force_unlock_btn = QPushButton(self.tr_('btn_unlock'))
        self.force_unlock_btn.clicked.connect(self.force_unlock_record)
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.force_unlock_btn)

        monitor_layout.addLayout(refresh_layout)
        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)

        # Access log
        log_group = QGroupBox(self.tr_('access_log'))
        log_layout = QVBoxLayout()

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            self.tr_('col_timestamp'), self.tr_('col_user_monitor'), self.tr_('col_action'),
            self.tr_('col_table_monitor'), self.tr_('col_success'), self.tr_('col_error')
        ])

        log_layout.addWidget(self.log_table)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        widget.setLayout(layout)
        return widget

    def create_roles_tab(self):
        """Crea tab gestione ruoli"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Roles table
        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(7)
        self.roles_table.setHorizontalHeaderLabels([
            self.tr_('col_role_table'), self.tr_('col_description'), self.tr_('col_view'),
            self.tr_('col_insert'), self.tr_('col_update'), self.tr_('col_delete'), self.tr_('col_system')
        ])

        layout.addWidget(self.roles_table)

        # Info
        info_label = QLabel(self.tr_('roles_info'))
        info_label.setStyleSheet("background-color: rgba(100,181,246,0.15); padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        widget.setLayout(layout)
        return widget

    def load_data(self):
        """Carica tutti i dati"""
        self.load_users()
        self.load_roles()
        self.load_monitor()
        self.load_access_log()

    def load_users(self):
        """Carica lista utenti"""
        try:
            # Prima verifica se la tabella esiste
            check_table = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'pyarchinit_users'
                )
            """
            exists = self.db_manager.execute_sql(check_table)

            if not exists or not exists[0][0]:
                # Tabella non esiste, mostra messaggio
                self.users_table.setRowCount(1)
                self.users_table.setItem(0, 0, QTableWidgetItem(self.tr_('table_not_found')))
                self.users_table.setItem(0, 1, QTableWidgetItem(self.tr_('run_update_script')))
                return

            query = """
                SELECT username, full_name, role, email, is_active, last_login, notes
                FROM pyarchinit_users
                ORDER BY username
            """
            users = self.db_manager.execute_sql(query)

            if not users:
                users = []  # Lista vuota se non ci sono utenti

            self.users_table.setRowCount(len(users) if users else 0)

            # Clear and repopulate combo boxes if they exist
            if hasattr(self, 'perm_user_combo'):
                self.perm_user_combo.clear()

            for i, user in enumerate(users if users else []):
                self.users_table.setItem(i, 0, QTableWidgetItem(user[0]))
                self.users_table.setItem(i, 1, QTableWidgetItem(user[1] or ""))
                self.users_table.setItem(i, 2, QTableWidgetItem(user[2]))
                self.users_table.setItem(i, 3, QTableWidgetItem(user[3] or ""))

                active_item = QTableWidgetItem("✓" if user[4] else "✗")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if not user[4]:
                    active_item.setBackground(QBrush(QColor(255, 200, 200)))
                self.users_table.setItem(i, 4, active_item)

                # Add to combo box if it exists
                if hasattr(self, 'perm_user_combo'):
                    self.perm_user_combo.addItem(user[0])

        except Exception as e:
            QMessageBox.warning(self, self.tr_('error'), f"{self.tr_('loading_users_error')}: {e}")

    def load_user_permissions(self):
        """Carica permessi utente selezionato - mostra SEMPRE tutte le tabelle"""
        username = self.perm_user_combo.currentText()
        if not username:
            return

        try:
            # Get user role
            role = 'guest'
            query = "SELECT role FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})
            if result:
                role = result[0][0]
                self.perm_role_label.setText(f"{self.tr_('col_role')}: {role}")

            # Get existing custom permissions from database
            query = """
                SELECT table_name, can_view, can_insert, can_update, can_delete
                FROM pyarchinit_permissions p
                JOIN pyarchinit_users u ON p.user_id = u.id
                WHERE u.username = :username
            """
            db_permissions = self.db_manager.execute_sql(query, {'username': username})

            # Convert to dictionary for easy lookup
            custom_perms = {}
            if db_permissions:
                for perm in db_permissions:
                    custom_perms[perm[0]] = (perm[1], perm[2], perm[3], perm[4])

            # Define ALL tables - always show complete list
            all_tables = [
                # Archaeological data tables
                'us_table', 'tma_materiali_archeologici', 'inventario_materiali_table',
                'site_table', 'periodizzazione_table', 'struttura_table', 'tomba_table',
                'individui_table', 'campioni_table', 'documentazione_table',
                'detsesso_table', 'deteta_table', 'archeozoology_table', 'pottery_table',
                'inventario_lapidei_table', 'tafonomia_table', 'ut_table',
                'tma_materiali_ripetibili', 'media_table', 'media_thumb_table',
                'media_to_entity_table', 'media_to_us_table',
                # Thesaurus tables
                'pyarchinit_thesaurus_sigle', 'pyarchinit_codici_tipologia',
                # Geometric tables (points, lines, polygons)
                'pyunitastratigrafiche', 'pyunitastratigrafiche_usm',
                'pyarchinit_quote', 'pyarchinit_quote_usm',
                'pyarchinit_siti', 'pyarchinit_siti_polygonal',
                'pyarchinit_ripartizioni_spaziali', 'pyarchinit_ripartizioni_temporali',
                'pyarchinit_documentazione', 'pyarchinit_individui',
                'pyarchinit_campionature', 'pyarchinit_reperti',
                'pyarchinit_strutture_ipotesi', 'pyarchinit_ipotesi_strutture',
                'pyarchinit_tafonomia', 'pyarchinit_sezioni', 'pyarchinit_sondaggi',
                'pyarchinit_linee_rif', 'pyarchinit_punti_rif',
                'pyarchinit_inventario_materiali', 'pyarcheozoo',
                'pyuscarlinee', 'pyuscaratterizzazioni',
                'pyarchinit_us_negative_doc', 'pyarchinit_tipologia_sepolture'
            ]

            # Build permissions list - use custom if exists, otherwise default based on role
            permissions = []
            for table in all_tables:
                if table in custom_perms:
                    # Use custom permissions from database
                    p = custom_perms[table]
                    permissions.append([table, p[0], p[1], p[2], p[3], True])  # True = custom
                else:
                    # Use default permissions based on role
                    if role == 'admin':
                        permissions.append([table, True, True, True, True, False])
                    elif role == 'responsabile':
                        permissions.append([table, True, True, True, False, False])
                    elif role == 'archeologo':
                        permissions.append([table, True, True, False, False, False])
                    elif role == 'studente':
                        permissions.append([table, True, False, False, False, False])
                    else:  # guest
                        permissions.append([table, True, False, False, False, False])

            self.permissions_table.setRowCount(len(permissions))

            for i, perm in enumerate(permissions):
                # Table name
                self.permissions_table.setItem(i, 0, QTableWidgetItem(perm[0]))

                # Checkboxes for permissions
                for j, value in enumerate(perm[1:5], 1):
                    checkbox = QCheckBox()
                    checkbox.setChecked(bool(value))
                    self.permissions_table.setCellWidget(i, j, checkbox)

                # Permission type (custom if from DB, default if generated)
                is_custom = perm[5]
                type_item = QTableWidgetItem(self.tr_('custom') if is_custom else self.tr_('default'))
                if is_custom:
                    type_item.setBackground(QBrush(QColor(255, 255, 200)))
                self.permissions_table.setItem(i, 5, type_item)

        except Exception as e:
            QMessageBox.warning(self, self.tr_('error'), f"{self.tr_('loading_perms_error')}: {e}")

    def load_monitor(self):
        """Carica monitor attività real-time"""
        try:
            # First check if the view exists
            check_view = """
                SELECT EXISTS (
                    SELECT FROM pg_views
                    WHERE viewname = 'active_editing_sessions'
                )
            """
            view_exists = self.db_manager.execute_sql(check_view)

            if not view_exists or not view_exists[0][0]:
                # View doesn't exist - show info message
                self.monitor_table.setRowCount(1)
                item = QTableWidgetItem(self.tr_('view_not_exists'))
                item.setBackground(QBrush(QColor(255, 255, 200)))
                self.monitor_table.setItem(0, 0, item)
                self.monitor_table.setSpan(0, 0, 1, 7)
                print("Monitor: active_editing_sessions view doesn't exist")
                return

            query = """
                SELECT
                    editing_by,
                    table_name,
                    reference,
                    'Editing' as action,
                    ROUND(minutes_editing::numeric, 1) as minutes,
                    '' as ip,
                    CASE
                        WHEN minutes_editing < 5 THEN 'active'
                        WHEN minutes_editing < 30 THEN 'ongoing'
                        ELSE 'stalled'
                    END as status
                FROM active_editing_sessions
                ORDER BY editing_since DESC
            """

            activities = self.db_manager.execute_sql(query)

            if not activities:
                # No active sessions
                self.monitor_table.setRowCount(1)
                item = QTableWidgetItem(self.tr_('no_active_sessions'))
                item.setBackground(QBrush(QColor(200, 255, 200)))
                self.monitor_table.setItem(0, 0, item)
                self.monitor_table.setSpan(0, 0, 1, 7)
                print("Monitor: No active editing sessions")
                return

            self.monitor_table.clearSpans()
            self.monitor_table.setRowCount(len(activities))

            # Map status codes to translated labels
            _status_map = {
                'active': self.tr_('status_active'),
                'ongoing': self.tr_('status_ongoing'),
                'stalled': self.tr_('status_stalled'),
            }

            for i, activity in enumerate(activities):
                for j, value in enumerate(activity):
                    display_val = str(value) if value is not None else ""
                    if j == 6:  # Status column - translate
                        display_val = _status_map.get(display_val, display_val)
                    item = QTableWidgetItem(display_val)
                    if j == 6:  # Status column
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if str(value) == 'stalled':
                            item.setBackground(QBrush(QColor(255, 200, 200)))
                    self.monitor_table.setItem(i, j, item)

            print(f"Monitor: Loaded {len(activities)} active sessions")

        except Exception as e:
            print(f"Errore monitor: {e}")
            self.monitor_table.setRowCount(1)
            item = QTableWidgetItem(f"Errore: {str(e)[:50]}...")
            item.setBackground(QBrush(QColor(255, 200, 200)))
            self.monitor_table.setItem(0, 0, item)
            self.monitor_table.setSpan(0, 0, 1, 7)

    def load_access_log(self):
        """Carica log accessi"""
        try:
            # First check if the table exists
            check_table = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'pyarchinit_access_log'
                )
            """
            table_exists = self.db_manager.execute_sql(check_table)

            if not table_exists or not table_exists[0][0]:
                # Table doesn't exist - show info message
                self.log_table.setRowCount(1)
                item = QTableWidgetItem(self.tr_('log_not_exists'))
                item.setBackground(QBrush(QColor(255, 255, 200)))
                self.log_table.setItem(0, 0, item)
                self.log_table.setSpan(0, 0, 1, 6)
                print("Access log: pyarchinit_access_log table doesn't exist")
                return

            query = """
                SELECT
                    timestamp,
                    username,
                    action,
                    table_accessed,
                    success,
                    error_message
                FROM pyarchinit_access_log
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                ORDER BY timestamp DESC
                LIMIT 100
            """

            logs = self.db_manager.execute_sql(query)

            if not logs:
                # No logs in last 24 hours
                self.log_table.setRowCount(1)
                item = QTableWidgetItem(self.tr_('no_logs'))
                item.setBackground(QBrush(QColor(200, 255, 200)))
                self.log_table.setItem(0, 0, item)
                self.log_table.setSpan(0, 0, 1, 6)
                print("Access log: No logs in last 24 hours")
                return

            self.log_table.clearSpans()
            self.log_table.setRowCount(len(logs))

            for i, log in enumerate(logs):
                for j, value in enumerate(log):
                    if j == 0 and value:  # Timestamp
                        try:
                            item = QTableWidgetItem(value.strftime("%Y-%m-%d %H:%M:%S"))
                        except:
                            item = QTableWidgetItem(str(value))
                    elif j == 4:  # Success
                        item = QTableWidgetItem("✓" if value else "✗")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if not value:
                            item.setBackground(QBrush(QColor(255, 200, 200)))
                    else:
                        item = QTableWidgetItem(str(value) if value else "")
                    self.log_table.setItem(i, j, item)

            print(f"Access log: Loaded {len(logs)} entries")

        except Exception as e:
            print(f"Errore log: {e}")
            self.log_table.setRowCount(1)
            item = QTableWidgetItem(f"Errore: {str(e)[:50]}...")
            item.setBackground(QBrush(QColor(255, 200, 200)))
            self.log_table.setItem(0, 0, item)
            self.log_table.setSpan(0, 0, 1, 6)

    def load_roles(self):
        """Carica ruoli"""
        try:
            query = """
                SELECT role_name, description,
                       default_can_view, default_can_insert,
                       default_can_update, default_can_delete,
                       is_system_role
                FROM pyarchinit_roles
                ORDER BY role_name
            """

            roles = self.db_manager.execute_sql(query)

            # If no roles or empty result, set empty table
            if not roles:
                self.roles_table.setRowCount(0)
                return

            self.roles_table.setRowCount(len(roles))

            for i, role in enumerate(roles):
                self.roles_table.setItem(i, 0, QTableWidgetItem(role[0]))
                self.roles_table.setItem(i, 1, QTableWidgetItem(role[1] or ""))

                for j, value in enumerate(role[2:6], 2):
                    item = QTableWidgetItem("✓" if value else "✗")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if value:
                        item.setBackground(QBrush(QColor(200, 255, 200)))
                    self.roles_table.setItem(i, j, item)

                system_item = QTableWidgetItem(self.tr_('system_role') if role[6] else self.tr_('custom_role'))
                if role[6]:
                    system_item.setBackground(QBrush(QColor(200, 200, 200)))
                self.roles_table.setItem(i, 6, system_item)

        except Exception as e:
            print(f"Errore ruoli: {e}")

    def _populate_site_list(self):
        """Populate the site list widget with all available sites from site_table"""
        try:
            self.site_list_widget.clear()
            query = "SELECT DISTINCT sito FROM site_table ORDER BY sito"
            result = self.db_manager.execute_sql(query)
            if result:
                for row in result:
                    site_name = row[0]
                    if site_name:
                        item = QListWidgetItem(site_name)
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.site_list_widget.addItem(item)
        except Exception as e:
            print(f"Error populating site list: {e}")

    def _select_all_sites(self):
        """Check all sites in the list"""
        for i in range(self.site_list_widget.count()):
            self.site_list_widget.item(i).setCheckState(Qt.CheckState.Checked)

    def _deselect_all_sites(self):
        """Uncheck all sites in the list"""
        for i in range(self.site_list_widget.count()):
            self.site_list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _load_user_site_filter(self, username):
        """Load site_filter for a user and check corresponding sites"""
        try:
            # Uncheck all first
            self._deselect_all_sites()

            query = "SELECT site_filter FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})
            if result and result[0][0]:
                allowed_sites = [s.strip() for s in result[0][0].split(',') if s.strip()]
                for i in range(self.site_list_widget.count()):
                    item = self.site_list_widget.item(i)
                    if item.text() in allowed_sites:
                        item.setCheckState(Qt.CheckState.Checked)
        except Exception as e:
            print(f"Error loading site filter: {e}")

    def _get_site_filter_string(self):
        """Get comma-separated string of checked sites"""
        checked = []
        for i in range(self.site_list_widget.count()):
            item = self.site_list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked.append(item.text())
        return ','.join(checked) if checked else ''

    def on_user_selected(self):
        """Quando viene selezionato un utente"""
        row = self.users_table.currentRow()
        if row < 0:
            return

        username = self.users_table.item(row, 0).text()

        # Load user details
        try:
            query = """
                SELECT username, full_name, email, role, is_active, notes, last_login
                FROM pyarchinit_users
                WHERE username = :username
            """
            result = self.db_manager.execute_sql(query, {'username': username})

            if result:
                user = result[0]
                self.username_edit.setText(user[0])
                self.fullname_edit.setText(user[1] or "")
                self.email_edit.setText(user[2] or "")
                self.role_combo.setCurrentText(user[3])
                self.active_check.setChecked(user[4])
                self.notes_edit.setText(user[5] or "")

                if user[6]:
                    self.last_login_label.setText(user[6].strftime("%Y-%m-%d %H:%M"))
                else:
                    self.last_login_label.setText(self.tr_('never_logged_in'))

                # Load site filter for this user
                self._load_user_site_filter(username)

        except Exception as e:
            print(f"Errore selezione utente: {e}")

    def add_new_user(self):
        """Aggiunge nuovo utente"""
        # Reset form
        self.username_edit.clear()
        self.password_edit.clear()
        self.fullname_edit.clear()
        self.email_edit.clear()
        self.role_combo.setCurrentIndex(2)  # archeologo
        self.active_check.setChecked(True)
        self.notes_edit.clear()
        self._deselect_all_sites()

        self.username_edit.setFocus()

    def delete_user(self):
        """Elimina utente selezionato"""
        row = self.users_table.currentRow()
        if row < 0:
            return

        username = self.users_table.item(row, 0).text()

        if username == 'admin':
            QMessageBox.warning(self, self.tr_('error'), self.tr_('cannot_delete_admin'))
            return

        reply = QMessageBox.question(self, self.tr_('confirm'),
                                    self.tr_('confirm_delete_user', username=username),
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM pyarchinit_users WHERE username = :username"
                self.db_manager.execute_sql(query, {'username': username})
                self.load_data()
                QMessageBox.information(self, self.tr_('success'), self.tr_('user_deleted'))
            except Exception as e:
                QMessageBox.critical(self, self.tr_('error'), f"{self.tr_('delete_error')}: {e}")

    def save_changes(self):
        """Salva modifiche utente"""
        username = self.username_edit.text()
        if not username:
            QMessageBox.warning(self, self.tr_('error'), self.tr_('username_required'))
            return

        try:
            # Check if user exists
            query = "SELECT id FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})

            # Get site_filter from checked sites
            site_filter_value = self._get_site_filter_string() if hasattr(self, 'site_list_widget') else ''

            if result and len(result) > 0:
                # Update existing
                if self.password_edit.text():
                    # Update with password
                    password_hash = hashlib.sha256(
                        self.password_edit.text().encode()
                    ).hexdigest()
                    query = """
                        UPDATE pyarchinit_users
                        SET full_name = :full_name, email = :email, role = :role,
                            is_active = :is_active, notes = :notes, password_hash = :password_hash,
                            site_filter = :site_filter
                        WHERE username = :username
                    """
                    params = {
                        'full_name': self.fullname_edit.text(),
                        'email': self.email_edit.text(),
                        'role': self.role_combo.currentText(),
                        'is_active': self.active_check.isChecked(),
                        'notes': self.notes_edit.toPlainText() if hasattr(self, 'notes_edit') else '',
                        'password_hash': password_hash,
                        'site_filter': site_filter_value or None,
                        'username': username
                    }
                else:
                    # Update without password
                    query = """
                        UPDATE pyarchinit_users
                        SET full_name = :full_name, email = :email, role = :role,
                            is_active = :is_active, notes = :notes,
                            site_filter = :site_filter
                        WHERE username = :username
                    """
                    params = {
                        'full_name': self.fullname_edit.text(),
                        'email': self.email_edit.text(),
                        'role': self.role_combo.currentText(),
                        'is_active': self.active_check.isChecked(),
                        'notes': self.notes_edit.toPlainText() if hasattr(self, 'notes_edit') else '',
                        'site_filter': site_filter_value or None,
                        'username': username
                    }

            else:
                # Insert new
                if not self.password_edit.text():
                    QMessageBox.warning(self, self.tr_('error'), self.tr_('password_required_new'))
                    return

                password_hash = hashlib.sha256(
                    self.password_edit.text().encode()
                ).hexdigest()

                query = """
                    INSERT INTO pyarchinit_users
                    (username, password_hash, full_name, email, role, is_active, notes, created_by, site_filter)
                    VALUES (:username, :password_hash, :full_name, :email, :role, :is_active, :notes, :created_by, :site_filter)
                """
                params = {
                    'username': username,
                    'password_hash': password_hash,
                    'full_name': self.fullname_edit.text(),
                    'email': self.email_edit.text(),
                    'role': self.role_combo.currentText(),
                    'is_active': self.active_check.isChecked(),
                    'notes': self.notes_edit.toPlainText() if hasattr(self, 'notes_edit') else '',
                    'created_by': getattr(self, 'current_user', 'admin'),
                    'site_filter': site_filter_value or None
                }

            # Execute the query
            result = self.db_manager.execute_sql(query, params)

            # Force commit if using PostgreSQL
            try:
                if hasattr(self.db_manager, 'engine'):
                    self.db_manager.engine.dispose()  # Force close connections
            except:
                pass

            # IMPORTANT: Save password and role BEFORE clearing the form!
            password_for_postgres = self.password_edit.text() or username
            role_for_postgres = self.role_combo.currentText()

            # Reload data to show changes
            self.load_data()

            # Also specifically reload the users list
            self.load_users()

            # Clear the form
            self.username_edit.clear()
            self.password_edit.clear()
            self.fullname_edit.clear()
            self.email_edit.clear()
            if hasattr(self, 'notes_edit'):
                self.notes_edit.clear()
            if hasattr(self, 'site_list_widget'):
                self._deselect_all_sites()

            self.user_changed.emit()

            # Crea automaticamente l'utente PostgreSQL (using saved password, not the cleared field!)
            self.create_postgres_user(username, password_for_postgres, role_for_postgres)

            QMessageBox.information(self, self.tr_('success'), self.tr_('user_saved'))

        except Exception as e:
            QMessageBox.critical(self, self.tr_('error'), f"{self.tr_('save_error')}: {e}")

    def save_permissions(self):
        """Salva i permessi modificati per l'utente selezionato"""
        username = self.perm_user_combo.currentText()
        if not username:
            QMessageBox.warning(self, self.tr_('error'), self.tr_('select_user'))
            return

        try:
            # Get user ID
            query = "SELECT id FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})
            if not result:
                QMessageBox.warning(self, self.tr_('error'), self.tr_('user_not_found'))
                return

            user_id = result[0][0]

            # First delete existing permissions
            delete_query = "DELETE FROM pyarchinit_permissions WHERE user_id = :user_id"
            self.db_manager.execute_sql(delete_query, {'user_id': user_id})

            # Then insert new permissions from table
            for row in range(self.permissions_table.rowCount()):
                table_name = self.permissions_table.item(row, 0).text()
                can_view = self.permissions_table.cellWidget(row, 1).isChecked()
                can_insert = self.permissions_table.cellWidget(row, 2).isChecked()
                can_update = self.permissions_table.cellWidget(row, 3).isChecked()
                can_delete = self.permissions_table.cellWidget(row, 4).isChecked()

                insert_query = """
                    INSERT INTO pyarchinit_permissions
                    (user_id, table_name, can_view, can_insert, can_update, can_delete)
                    VALUES (:user_id, :table_name, :can_view, :can_insert, :can_update, :can_delete)
                """
                params = {
                    'user_id': user_id,
                    'table_name': table_name,
                    'can_view': can_view,
                    'can_insert': can_insert,
                    'can_update': can_update,
                    'can_delete': can_delete
                }
                self.db_manager.execute_sql(insert_query, params)

            # Reload permissions to show they are now custom
            self.load_user_permissions()

            # Sincronizza i permessi con PostgreSQL
            self.sync_postgres_permissions_for_user(username)

            QMessageBox.information(self, self.tr_('success'), self.tr_('permissions_saved'))

        except Exception as e:
            QMessageBox.critical(self, self.tr_('error'), f"{self.tr_('permissions_save_error')}: {e}")

    def create_postgres_user(self, username, password, role):
        """Crea un utente PostgreSQL con i permessi base del ruolo"""
        try:
            # Use the provided password or fallback to username
            actual_password = password if password else username

            # Check if user already exists
            check_query = "SELECT 1 FROM pg_user WHERE usename = :username"
            user_exists = False
            try:
                result = self.db_manager.execute_sql(check_query, {'username': username})
                user_exists = bool(result)
            except:
                pass

            if user_exists:
                # User exists - UPDATE the password
                print(f"Utente PostgreSQL {username} già esistente, aggiorno la password...")
                try:
                    alter_query = f"ALTER USER {username} WITH PASSWORD '{actual_password}'"
                    self.db_manager.execute_sql(alter_query)
                    print(f"Password aggiornata per utente PostgreSQL {username}")
                except Exception as e:
                    print(f"Errore aggiornamento password PostgreSQL: {e}")
            else:
                # Create new user
                create_query = f"CREATE USER {username} WITH PASSWORD '{actual_password}'"
                self.db_manager.execute_sql(create_query)
                print(f"Utente PostgreSQL {username} creato")

            # Grant basic permissions
            db_name = self.db_manager.engine.url.database
            grant_connect = f"GRANT CONNECT ON DATABASE {db_name} TO {username}"
            self.db_manager.execute_sql(grant_connect)

            grant_usage = f"GRANT USAGE ON SCHEMA public TO {username}"
            self.db_manager.execute_sql(grant_usage)

            # Apply role-based permissions
            if role == 'admin' or role == 'administrator':
                # Grant all permissions
                self.db_manager.execute_sql(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {username}")

            elif role == 'archeologo':
                # Can view, insert, and update most tables
                self.db_manager.execute_sql(f"GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {username}")
                # UPDATE on sequences is needed to increment gid when inserting geometric features
                self.db_manager.execute_sql(f"GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {username}")

            elif role == 'responsabile':
                # Responsabile can view, insert, update, and delete most tables
                self.db_manager.execute_sql(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {username}")
                # UPDATE on sequences is needed to increment gid when inserting geometric features
                self.db_manager.execute_sql(f"GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {username}")

            elif role == 'studente':
                # Limited permissions - mainly view and some insert
                self.db_manager.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"GRANT INSERT ON us_table, campioni_table TO {username}")
                # UPDATE on sequences is needed for INSERT to work (to get next gid)
                self.db_manager.execute_sql(f"GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {username}")

            elif role == 'guest':
                # Read-only access
                self.db_manager.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {username}")

            # Grant execute on functions
            self.db_manager.execute_sql(f"GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO {username}")

            # Grant permissions on PyArchInit system tables (needed for UI functionality)
            system_tables = [
                'pyarchinit_thesaurus_sigle',
                'pyarchinit_roles',
                'pyarchinit_users',
                'pyarchinit_permissions',
                'pyarchinit_config',
                'pyarchinit_codici_tipologia',
                'pyarchinit_access_log',
                'pyarchinit_activity_log',
                'pyarchinit_audit_log'
            ]

            for table in system_tables:
                try:
                    self.db_manager.execute_sql(f"GRANT SELECT ON {table} TO {username}")
                except:
                    pass  # Table might not exist

            # Grant SELECT on all views and pyarchinit_* tables
            try:
                self.db_manager.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username}")
            except:
                pass

            print(f"Utente PostgreSQL {username} creato con ruolo {role}")

        except Exception as e:
            print(f"Errore creazione utente PostgreSQL: {e}")
            # Don't raise - just log error

    def sync_postgres_permissions_for_user(self, username):
        """Sincronizza i permessi PyArchInit con PostgreSQL per un utente specifico"""
        try:
            # Get user info
            query = "SELECT id, password_hash, role FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})
            if not result:
                return

            user_id, password_hash, role = result[0]

            # Check if PostgreSQL user exists
            check_query = "SELECT 1 FROM pg_user WHERE usename = :username"
            try:
                pg_result = self.db_manager.execute_sql(check_query, {'username': username})
                user_exists = bool(pg_result)
            except:
                user_exists = False

            if not user_exists:
                # Create PostgreSQL user with temporary password
                create_user_query = f"CREATE USER {username} WITH PASSWORD '{username}123'"
                self.db_manager.execute_sql(create_user_query)

                # Grant basic permissions
                grant_connect = f"GRANT CONNECT ON DATABASE {self.db_manager.engine.url.database} TO {username}"
                self.db_manager.execute_sql(grant_connect)

                grant_usage = f"GRANT USAGE ON SCHEMA public TO {username}"
                self.db_manager.execute_sql(grant_usage)

            # Get permissions for this user
            perm_query = """
                SELECT table_name, can_view, can_insert, can_update, can_delete
                FROM pyarchinit_permissions
                WHERE user_id = :user_id
            """
            permissions = self.db_manager.execute_sql(perm_query, {'user_id': user_id})

            # Apply each permission
            for table_name, can_view, can_insert, can_update, can_delete in permissions:
                # Build permission list
                perms = []
                if can_view:
                    perms.append('SELECT')
                if can_insert:
                    perms.append('INSERT')
                if can_update:
                    perms.append('UPDATE')
                if can_delete:
                    perms.append('DELETE')

                if perms:
                    # Revoke all first
                    try:
                        revoke_query = f"REVOKE ALL PRIVILEGES ON {table_name} FROM {username}"
                        self.db_manager.execute_sql(revoke_query)
                    except:
                        pass

                    # Grant new permissions
                    perm_str = ', '.join(perms)
                    grant_query = f"GRANT {perm_str} ON {table_name} TO {username}"
                    self.db_manager.execute_sql(grant_query)

                    # If INSERT or UPDATE permission, also grant sequence permissions
                    if can_insert or can_update:
                        self._grant_sequence_permissions_for_table(username, table_name)

            print(f"Permessi PostgreSQL sincronizzati per utente {username}")

        except Exception as e:
            print(f"Errore sincronizzazione permessi PostgreSQL: {e}")
            # Don't raise - just log error

    def _grant_sequence_permissions_for_table(self, username, table_name):
        """Grant sequence permissions for a table (needed for INSERT/UPDATE on geometric tables)"""
        try:
            # Method 1: Find sequences directly dependent on the table
            seq_query = f"""
                SELECT c.relname
                FROM pg_class c
                JOIN pg_depend d ON d.objid = c.oid
                JOIN pg_class t ON t.oid = d.refobjid
                WHERE c.relkind = 'S' AND t.relname = '{table_name}'
            """
            sequences = self.db_manager.execute_sql(seq_query)

            if sequences:
                for seq in sequences:
                    try:
                        grant_seq = f"GRANT USAGE, SELECT, UPDATE ON SEQUENCE {seq[0]} TO {username}"
                        self.db_manager.execute_sql(grant_seq)
                        print(f"  Granted sequence permissions on {seq[0]} to {username}")
                    except Exception as e:
                        print(f"  Warning: Could not grant on sequence {seq[0]}: {e}")

            # Method 2: Try common naming patterns for sequences
            # PostgreSQL typically names sequences as table_column_seq
            common_patterns = [
                f"{table_name}_gid_seq",
                f"{table_name}_id_seq",
                f"{table_name}_pkuid_seq",
                f"{table_name}_fid_seq",
            ]

            for seq_name in common_patterns:
                try:
                    # Check if sequence exists
                    check_seq = f"""
                        SELECT 1 FROM pg_class
                        WHERE relkind = 'S' AND relname = '{seq_name}'
                    """
                    exists = self.db_manager.execute_sql(check_seq)
                    if exists:
                        grant_seq = f"GRANT USAGE, SELECT, UPDATE ON SEQUENCE {seq_name} TO {username}"
                        self.db_manager.execute_sql(grant_seq)
                        print(f"  Granted sequence permissions on {seq_name} to {username}")
                except:
                    pass  # Sequence doesn't exist or already granted

            # Method 3: For geometric tables, also check related sequences
            # Map of geometric tables to their known sequences
            geometric_seq_map = {
                'pyunitastratigrafiche': ['pyunitastratigrafiche_gid_seq'],
                'pyunitastratigrafiche_usm': ['pyunitastratigrafiche_usm_gid_seq'],
                'pyarchinit_quote': ['pyarchinit_quote_gid_seq'],
                'pyarchinit_quote_usm': ['pyarchinit_quote_usm_gid_seq'],
                'pyarchinit_siti': ['pyarchinit_siti_gid_seq'],
                'pyarchinit_siti_polygonal': ['pyarchinit_siti_polygonal_gid_seq'],
                'pyarchinit_ripartizioni_spaziali': ['pyarchinit_ripartizioni_spaziali_gid_seq'],
                'pyarchinit_documentazione': ['pyarchinit_documentazione_gid_seq'],
                'pyarchinit_individui': ['pyarchinit_individui_gid_seq'],
                'pyarchinit_reperti': ['pyarchinit_reperti_gid_seq'],
                'pyarchinit_strutture_ipotesi': ['pyarchinit_strutture_ipotesi_gid_seq', 'pyarchinit_strutture_ipotesi_gid_seq1'],
                'pyarchinit_ipotesi_strutture': ['pyarchinit_ipotesi_strutture_gid_seq'],
                'pyarchinit_sezioni': ['pyarchinit_sezioni_gid_seq'],
                'pyarchinit_sondaggi': ['pyarchinit_sondaggi_gid_seq'],
                'pyarchinit_linee_rif': ['pyarchinit_linee_rif_gid_seq'],
                'pyarchinit_punti_rif': ['pyarchinit_punti_rif_gid_seq', 'pyarchinit_punti_rif_gid'],
                'pyarcheozoo': ['pyarcheozoo_gid_seq'],
            }

            if table_name in geometric_seq_map:
                for seq_name in geometric_seq_map[table_name]:
                    try:
                        grant_seq = f"GRANT USAGE, SELECT, UPDATE ON SEQUENCE {seq_name} TO {username}"
                        self.db_manager.execute_sql(grant_seq)
                        print(f"  Granted sequence permissions on {seq_name} to {username} (geometric table)")
                    except Exception as e:
                        print(f"  Warning: Could not grant on sequence {seq_name}: {e}")

        except Exception as e:
            print(f"Error granting sequence permissions for {table_name}: {e}")

    def apply_permissions_to_all(self):
        """Applica permessi a tutte le tabelle"""
        username = self.perm_user_combo.currentText()
        if not username:
            return

        view = self.quick_view.isChecked()
        insert = self.quick_insert.isChecked()
        update = self.quick_update.isChecked()
        delete = self.quick_delete.isChecked()

        reply = QMessageBox.question(self, self.tr_('confirm'),
            self.tr_('confirm_apply_all', username=username),
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Get all tables
                for row in range(self.permissions_table.rowCount()):
                    table_name = self.permissions_table.item(row, 0).text()

                    query = """
                        SELECT set_user_permission(%s, %s, %s, %s, %s, %s, %s)
                    """
                    self.db_manager.execute_sql(query, [
                        username, table_name, insert, update, delete, view, self.current_user
                    ])

                self.load_user_permissions()
                QMessageBox.information(self, self.tr_('success'), self.tr_('permissions_applied'))

            except Exception as e:
                QMessageBox.critical(self, self.tr_('error'), f"{self.tr_('apply_error')}: {e}")

    def force_unlock_record(self):
        """Forza sblocco record"""
        row = self.monitor_table.currentRow()
        if row < 0:
            return

        table = self.monitor_table.item(row, 1).text()
        record = self.monitor_table.item(row, 2).text()
        user = self.monitor_table.item(row, 0).text()

        reply = QMessageBox.question(self, self.tr_('confirm'),
            self.tr_('confirm_unlock', record=record, table=table, user=user),
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                query = f"""
                    UPDATE {table}
                    SET editing_by = NULL, editing_since = NULL
                    WHERE reference = :record
                """
                self.db_manager.execute_sql(query, {'record': record})
                self.load_monitor()
                QMessageBox.information(self, self.tr_('success'), self.tr_('record_unlocked'))
            except Exception as e:
                QMessageBox.critical(self, self.tr_('error'), f"{self.tr_('unlock_error')}: {e}")

    def toggle_auto_refresh(self, state):
        """Attiva/disattiva auto-refresh"""
        if state == Qt.Checked:
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.refresh_all_monitors)
            self.refresh_timer.start(10000)  # 10 secondi
        else:
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()

    def refresh_all_monitors(self):
        """Aggiorna monitor e log accessi"""
        self.load_monitor()
        self.load_access_log()

    def initialize_user_tables(self):
        """Inizializza le tabelle del sistema utenti nel database"""
        reply = QMessageBox.question(self, self.tr_('confirm'),
                                    self.tr_('confirm_init_db'),
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Leggi lo script SQL
                import os
                plugin_dir = os.path.dirname(os.path.dirname(__file__))
                sql_file = os.path.join(plugin_dir, 'sql', 'create_user_management_system.sql')

                if not os.path.exists(sql_file):
                    # Se il file non esiste, usa lo script inline
                    sql_script = self.get_user_tables_sql()
                else:
                    with open(sql_file, 'r') as f:
                        sql_script = f.read()

                # Esegui lo script
                queries = sql_script.split(';')
                for query in queries:
                    if query.strip():
                        self.db_manager.execute_sql(query)

                QMessageBox.information(self, self.tr_('success'),
                                      self.tr_('tables_created'))

                # Ricarica i dati
                self.load_data()

            except Exception as e:
                QMessageBox.critical(self, self.tr_('error'),
                                   f"{self.tr_('table_creation_error')}:\n{str(e)}")

    def get_user_tables_sql(self):
        """Ritorna lo script SQL per creare le tabelle utenti"""
        return """
-- Tabella utenti
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'archeologo',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    last_login TIMESTAMP,
    last_ip VARCHAR(50),
    notes TEXT
);

-- Tabella permessi
CREATE TABLE IF NOT EXISTS pyarchinit_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    can_insert BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_view BOOLEAN DEFAULT TRUE,
    site_filter VARCHAR(100),
    area_filter VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    UNIQUE(user_id, table_name)
);

-- Tabella ruoli
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    default_can_insert BOOLEAN DEFAULT FALSE,
    default_can_update BOOLEAN DEFAULT FALSE,
    default_can_delete BOOLEAN DEFAULT FALSE,
    default_can_view BOOLEAN DEFAULT TRUE,
    is_system_role BOOLEAN DEFAULT FALSE
);

-- Tabella log accessi
CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id),
    username VARCHAR(50),
    action VARCHAR(50),
    table_accessed VARCHAR(100),
    operation VARCHAR(20),
    record_id INTEGER,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT
);

-- Inserisci ruoli predefiniti
INSERT INTO pyarchinit_roles (role_name, description, default_can_insert, default_can_update, default_can_delete, default_can_view, is_system_role) VALUES
('admin', 'Amministratore - Accesso completo', TRUE, TRUE, TRUE, TRUE, TRUE),
('responsabile', 'Responsabile scavo - Può modificare tutto', TRUE, TRUE, TRUE, TRUE, FALSE),
('archeologo', 'Archeologo - Può inserire e modificare', TRUE, TRUE, FALSE, TRUE, FALSE),
('studente', 'Studente - Solo inserimento', TRUE, FALSE, FALSE, TRUE, FALSE),
('guest', 'Ospite - Solo visualizzazione', FALSE, FALSE, FALSE, TRUE, FALSE)
ON CONFLICT (role_name) DO NOTHING;

-- Crea utente admin predefinito (password: admin123)
INSERT INTO pyarchinit_users (username, password_hash, full_name, role, is_active)
VALUES ('admin', SHA256('admin123'), 'Amministratore Sistema', 'admin', TRUE)
ON CONFLICT (username) DO NOTHING;
"""