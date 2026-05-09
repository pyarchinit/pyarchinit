# gui/user_management_dialog.py

## Overview

This file contains 29 documented elements.

## Classes

### UserManagementDialog

Dialog per gestione utenti e permessi - Solo per Admin

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

Initializes the dialog by accepting a `db_manager` instance and an optional `parent` widget, then performs setup in a fixed sequence. It detects the user's locale from QGIS settings (falling back to `'en'` if the locale is not among the supported languages), retrieves the current user from QGIS settings or the OS username as a fallback, and obtains the database connection username via `_get_db_username()`. If the user does not pass the admin access check, a critical message box is displayed and the dialog is closed immediately; otherwise, the UI is initialized, a theme is applied (with an optional toggle button), and data is loaded via `load_data()`.

##### tr_(self, key)

Get translated string for current language

##### check_admin_access(self)

Verifica se l'utente corrente è admin

##### init_ui(self)

Inizializza interfaccia

##### create_users_tab(self)

Crea tab gestione utenti

##### create_permissions_tab(self)

Crea tab gestione permessi

##### create_monitor_tab(self)

Crea tab monitor attività

##### create_roles_tab(self)

Crea tab gestione ruoli

##### load_data(self)

Carica tutti i dati

##### load_users(self)

Carica lista utenti

##### load_user_permissions(self)

Carica permessi utente selezionato - mostra SEMPRE tutte le tabelle

##### load_monitor(self)

Carica monitor attività real-time

##### load_access_log(self)

Carica log accessi

##### load_roles(self)

Carica ruoli

##### on_user_selected(self)

Quando viene selezionato un utente

##### add_new_user(self)

Aggiunge nuovo utente

##### delete_user(self)

Elimina utente selezionato

##### save_changes(self)

Salva modifiche utente

##### save_permissions(self)

Salva i permessi modificati per l'utente selezionato

##### create_postgres_user(self, username, password, role)

Crea un utente PostgreSQL con i permessi base del ruolo

##### sync_postgres_permissions_for_user(self, username)

Sincronizza i permessi PyArchInit con PostgreSQL per un utente specifico

##### apply_permissions_to_all(self)

Applica permessi a tutte le tabelle

##### force_unlock_record(self)

Forza sblocco record

##### toggle_auto_refresh(self, state)

Attiva/disattiva auto-refresh

##### refresh_all_monitors(self)

Aggiorna monitor e log accessi

##### initialize_user_tables(self)

Inizializza le tabelle del sistema utenti nel database

##### get_user_tables_sql(self)

Ritorna lo script SQL per creare le tabelle utenti

