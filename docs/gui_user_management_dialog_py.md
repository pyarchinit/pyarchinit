# gui/user_management_dialog.py

## Overview

This file contains 108 documented elements.

## Classes

### UserManagementDialog

Dialog per gestione utenti e permessi - Solo per Admin

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

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

Carica permessi utente selezionato

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

##### initialize_user_tables(self)

Inizializza le tabelle del sistema utenti nel database

##### get_user_tables_sql(self)

Ritorna lo script SQL per creare le tabelle utenti

### UserManagementDialog

Dialog per gestione utenti e permessi - Solo per Admin

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

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

Carica permessi utente selezionato

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

##### initialize_user_tables(self)

Inizializza le tabelle del sistema utenti nel database

##### get_user_tables_sql(self)

Ritorna lo script SQL per creare le tabelle utenti

### UserManagementDialog

Dialog per gestione utenti e permessi - Solo per Admin

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

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

Carica permessi utente selezionato

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

##### initialize_user_tables(self)

Inizializza le tabelle del sistema utenti nel database

##### get_user_tables_sql(self)

Ritorna lo script SQL per creare le tabelle utenti

### UserManagementDialog

Dialog per gestione utenti e permessi - Solo per Admin

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

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

Carica permessi utente selezionato

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

##### initialize_user_tables(self)

Inizializza le tabelle del sistema utenti nel database

##### get_user_tables_sql(self)

Ritorna lo script SQL per creare le tabelle utenti

