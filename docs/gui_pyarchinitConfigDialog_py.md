# gui/pyarchinitConfigDialog.py

## Overview

This file contains 332 documented elements.

## Classes

### PyArchInitLogger

Simple file-based logger for debugging

#### Methods

##### __init__(self)

##### log(self, message)

Write a message to the log file with timestamp

##### log_exception(self, function_name, exception)

Log an exception with traceback

##### clear_log(self)

Clear the log file

### pyArchInitDialog_Config

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

##### setup_admin_features(self)

Setup admin-only features like user management

##### check_if_updates_needed(self)

Check if database updates are needed

##### update_database_schema(self)

Apply all database schema updates

##### check_if_concurrency_installed(self)

Check if concurrency system is already installed

##### apply_concurrency_system(self)

Apply concurrency system to all tables

##### open_user_management(self)

Open user management dialog

##### open_activity_monitor(self)

Open real-time activity monitor

##### on_users_changed(self)

Called when users/permissions are changed

##### convert_db(self)

##### on_pushButton_convert_db_sl_pressed(self)

##### on_pushButton_convert_db_pg_pressed(self)

##### sito_active(self)

##### check_table(self)

##### value_check(self, table)

##### check_geometry_table(self)

##### value_check_geometry(self, table)

##### test3(self)

##### test(self)

##### test2(self)

##### setComboBoxEnable(self, f, v)

##### customize(self)

##### db_uncheck(self)

##### upd_individui_table(self)

##### geometry_conn(self)

##### message(self)

##### check(self)

##### summary(self)

##### check_if_admin(self)

Check if current user is admin

##### db_active(self)

##### setPathDBsqlite1(self)

##### setPathDBsqlite2(self)

##### openthumbDir(self)

##### openresizeDir(self)

##### db_name_change(self)

##### save_and_clear_comboBox_sito(self)

##### save_p(self)

##### on_pushButton_update_db_pressed(self)

Handler for the new update button that updates existing databases
without deleting data using the DB_update class

##### tool_ok(self)

##### setPathDB(self)

##### setPathThumb(self)

##### setPathlogo(self)

##### setPathResize(self)

##### setPathGraphviz(self)

##### setPathPostgres(self)

##### setEnvironPath(self)

##### setEnvironPathPostgres(self)

##### set_db_parameter(self)

##### set_db_import_from_parameter(self)

##### set_db_import_to_parameter(self)

##### load_dict(self)

##### save_dict(self)

##### on_pushButton_save_pressed(self)

##### compare(self)

##### on_pushButton_crea_database_pressed(self)

##### select_version_sql(self)

##### on_pushButton_upd_postgres_pressed(self)

##### load_spatialite(self, dbapi_conn, connection_record)

##### on_pushButton_upd_sqlite_pressed(self)

##### on_pushButton_crea_database_sl_pressed(self)

##### try_connection(self)

##### connection_up(self)

##### charge_data(self)

##### test_def(self)

##### on_toolButton_active_toggled(self)

##### charge_list(self)

##### on_pushButton_import_geometry_pressed(self)

##### on_pushButton_apply_constraints_pressed(self)

Apply unique constraints to thesaurus table.

##### on_pushButton_import_pressed(self)

##### check_sqlite_db_on_init(self)

Check and fix macc field when config dialog opens

##### fix_macc_field_for_current_db(self, conn_str)

Fix macc field in the current SQLite database

##### openthumbDir(self)

##### openresizeDir(self)

##### on_pushButton_connect_pressed(self)

##### on_pushButton_convertdb_pressed(self)

### PyArchInitLogger

Simple file-based logger for debugging

#### Methods

##### __init__(self)

##### log(self, message)

Write a message to the log file with timestamp

##### log_exception(self, function_name, exception)

Log an exception with traceback

##### clear_log(self)

Clear the log file

### pyArchInitDialog_Config

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

##### setup_admin_features(self)

Setup admin-only features like user management

##### check_if_updates_needed(self)

Check if database updates are needed

##### update_database_schema(self)

Apply all database schema updates

##### check_if_concurrency_installed(self)

Check if concurrency system is already installed

##### apply_concurrency_system(self)

Apply concurrency system to all tables

##### open_user_management(self)

Open user management dialog

##### open_activity_monitor(self)

Open real-time activity monitor

##### on_users_changed(self)

Called when users/permissions are changed

##### convert_db(self)

##### on_pushButton_convert_db_sl_pressed(self)

##### on_pushButton_convert_db_pg_pressed(self)

##### sito_active(self)

##### check_table(self)

##### value_check(self, table)

##### check_geometry_table(self)

##### value_check_geometry(self, table)

##### test3(self)

##### test(self)

##### test2(self)

##### setComboBoxEnable(self, f, v)

##### customize(self)

##### db_uncheck(self)

##### upd_individui_table(self)

##### geometry_conn(self)

##### message(self)

##### check(self)

##### summary(self)

##### check_if_admin(self)

Check if current user is admin

##### db_active(self)

##### setPathDBsqlite1(self)

##### setPathDBsqlite2(self)

##### openthumbDir(self)

##### openresizeDir(self)

##### db_name_change(self)

##### save_and_clear_comboBox_sito(self)

##### save_p(self)

##### on_pushButton_update_db_pressed(self)

Handler for the new update button that updates existing databases
without deleting data using the DB_update class

##### tool_ok(self)

##### setPathDB(self)

##### setPathThumb(self)

##### setPathlogo(self)

##### setPathResize(self)

##### setPathGraphviz(self)

##### setPathPostgres(self)

##### setEnvironPath(self)

##### setEnvironPathPostgres(self)

##### set_db_parameter(self)

##### set_db_import_from_parameter(self)

##### set_db_import_to_parameter(self)

##### load_dict(self)

##### save_dict(self)

##### on_pushButton_save_pressed(self)

##### compare(self)

##### on_pushButton_crea_database_pressed(self)

##### select_version_sql(self)

##### on_pushButton_upd_postgres_pressed(self)

##### load_spatialite(self, dbapi_conn, connection_record)

##### on_pushButton_upd_sqlite_pressed(self)

##### on_pushButton_crea_database_sl_pressed(self)

##### try_connection(self)

##### connection_up(self)

##### charge_data(self)

##### test_def(self)

##### on_toolButton_active_toggled(self)

##### charge_list(self)

##### on_pushButton_import_geometry_pressed(self)

##### on_pushButton_apply_constraints_pressed(self)

Apply unique constraints to thesaurus table.

##### on_pushButton_import_pressed(self)

##### check_sqlite_db_on_init(self)

Check and fix macc field when config dialog opens

##### fix_macc_field_for_current_db(self, conn_str)

Fix macc field in the current SQLite database

##### openthumbDir(self)

##### openresizeDir(self)

##### on_pushButton_connect_pressed(self)

##### on_pushButton_convertdb_pressed(self)

### PyArchInitLogger

Simple file-based logger for debugging

#### Methods

##### __init__(self)

##### log(self, message)

Write a message to the log file with timestamp

##### log_exception(self, function_name, exception)

Log an exception with traceback

##### clear_log(self)

Clear the log file

### pyArchInitDialog_Config

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

##### setup_admin_features(self)

Setup admin-only features like user management

##### check_if_updates_needed(self)

Check if database updates are needed

##### update_database_schema(self)

Apply all database schema updates

##### check_if_concurrency_installed(self)

Check if concurrency system is already installed

##### apply_concurrency_system(self)

Apply concurrency system to all tables

##### open_user_management(self)

Open user management dialog

##### open_activity_monitor(self)

Open real-time activity monitor

##### on_users_changed(self)

Called when users/permissions are changed

##### convert_db(self)

##### on_pushButton_convert_db_sl_pressed(self)

##### on_pushButton_convert_db_pg_pressed(self)

##### sito_active(self)

##### check_table(self)

##### value_check(self, table)

##### check_geometry_table(self)

##### value_check_geometry(self, table)

##### test3(self)

##### test(self)

##### test2(self)

##### setComboBoxEnable(self, f, v)

##### customize(self)

##### db_uncheck(self)

##### upd_individui_table(self)

##### geometry_conn(self)

##### message(self)

##### check(self)

##### summary(self)

##### check_if_admin(self)

Check if current user is admin

##### db_active(self)

##### setPathDBsqlite1(self)

##### setPathDBsqlite2(self)

##### openthumbDir(self)

##### openresizeDir(self)

##### db_name_change(self)

##### save_and_clear_comboBox_sito(self)

##### save_p(self)

##### on_pushButton_update_db_pressed(self)

Handler for the new update button that updates existing databases
without deleting data using the DB_update class

##### tool_ok(self)

##### setPathDB(self)

##### setPathThumb(self)

##### setPathlogo(self)

##### setPathResize(self)

##### setPathGraphviz(self)

##### setPathPostgres(self)

##### setEnvironPath(self)

##### setEnvironPathPostgres(self)

##### set_db_parameter(self)

##### set_db_import_from_parameter(self)

##### set_db_import_to_parameter(self)

##### load_dict(self)

##### save_dict(self)

##### on_pushButton_save_pressed(self)

##### compare(self)

##### on_pushButton_crea_database_pressed(self)

##### select_version_sql(self)

##### on_pushButton_upd_postgres_pressed(self)

##### load_spatialite(self, dbapi_conn, connection_record)

##### on_pushButton_upd_sqlite_pressed(self)

##### on_pushButton_crea_database_sl_pressed(self)

##### try_connection(self)

##### connection_up(self)

##### charge_data(self)

##### test_def(self)

##### on_toolButton_active_toggled(self)

##### charge_list(self)

##### on_pushButton_import_geometry_pressed(self)

##### on_pushButton_apply_constraints_pressed(self)

Apply unique constraints to thesaurus table.

##### on_pushButton_import_pressed(self)

##### check_sqlite_db_on_init(self)

Check and fix macc field when config dialog opens

##### fix_macc_field_for_current_db(self, conn_str)

Fix macc field in the current SQLite database

##### openthumbDir(self)

##### openresizeDir(self)

##### on_pushButton_connect_pressed(self)

##### on_pushButton_convertdb_pressed(self)

### PyArchInitLogger

Simple file-based logger for debugging

#### Methods

##### __init__(self)

##### log(self, message)

Write a message to the log file with timestamp

##### log_exception(self, function_name, exception)

Log an exception with traceback

##### clear_log(self)

Clear the log file

### pyArchInitDialog_Config

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

##### setup_admin_features(self)

Setup admin-only features like user management

##### check_if_updates_needed(self)

Check if database updates are needed

##### update_database_schema(self)

Apply all database schema updates

##### check_if_concurrency_installed(self)

Check if concurrency system is already installed

##### apply_concurrency_system(self)

Apply concurrency system to all tables

##### open_user_management(self)

Open user management dialog

##### open_activity_monitor(self)

Open real-time activity monitor

##### on_users_changed(self)

Called when users/permissions are changed

##### convert_db(self)

##### on_pushButton_convert_db_sl_pressed(self)

##### on_pushButton_convert_db_pg_pressed(self)

##### sito_active(self)

##### check_table(self)

##### value_check(self, table)

##### check_geometry_table(self)

##### value_check_geometry(self, table)

##### test3(self)

##### test(self)

##### test2(self)

##### setComboBoxEnable(self, f, v)

##### customize(self)

##### db_uncheck(self)

##### upd_individui_table(self)

##### geometry_conn(self)

##### message(self)

##### check(self)

##### summary(self)

##### check_if_admin(self)

Check if current user is admin

##### db_active(self)

##### setPathDBsqlite1(self)

##### setPathDBsqlite2(self)

##### openthumbDir(self)

##### openresizeDir(self)

##### db_name_change(self)

##### save_and_clear_comboBox_sito(self)

##### save_p(self)

##### on_pushButton_update_db_pressed(self)

Handler for the new update button that updates existing databases
without deleting data using the DB_update class

##### tool_ok(self)

##### setPathDB(self)

##### setPathThumb(self)

##### setPathlogo(self)

##### setPathResize(self)

##### setPathGraphviz(self)

##### setPathPostgres(self)

##### setEnvironPath(self)

##### setEnvironPathPostgres(self)

##### set_db_parameter(self)

##### set_db_import_from_parameter(self)

##### set_db_import_to_parameter(self)

##### load_dict(self)

##### save_dict(self)

##### on_pushButton_save_pressed(self)

##### compare(self)

##### on_pushButton_crea_database_pressed(self)

##### select_version_sql(self)

##### on_pushButton_upd_postgres_pressed(self)

##### load_spatialite(self, dbapi_conn, connection_record)

##### on_pushButton_upd_sqlite_pressed(self)

##### on_pushButton_crea_database_sl_pressed(self)

##### try_connection(self)

##### connection_up(self)

##### charge_data(self)

##### test_def(self)

##### on_toolButton_active_toggled(self)

##### charge_list(self)

##### on_pushButton_import_geometry_pressed(self)

##### on_pushButton_apply_constraints_pressed(self)

Apply unique constraints to thesaurus table.

##### on_pushButton_import_pressed(self)

##### check_sqlite_db_on_init(self)

Check and fix macc field when config dialog opens

##### fix_macc_field_for_current_db(self, conn_str)

Fix macc field in the current SQLite database

##### openthumbDir(self)

##### openresizeDir(self)

##### on_pushButton_connect_pressed(self)

##### on_pushButton_convertdb_pressed(self)

## Functions

### reconnect_set_db_parameter()

### reconnect_set_db_parameter()

### reconnect_set_db_parameter()

### reconnect_set_db_parameter()

