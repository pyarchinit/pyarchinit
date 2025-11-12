# gui/backup_restore_dialog.py

## Overview

This file contains 88 documented elements.

## Classes

### BackupWorker

Worker thread for backup operations

**Inherits from**: QThread

#### Methods

##### __init__(self, command, env)

##### run(self)

Execute backup command

### BackupRestoreDialog

Advanced Backup/Restore Dialog with calendar and progress tracking

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### init_ui(self)

Initialize the user interface

##### load_settings(self)

Load database settings

##### load_backup_info(self)

Load backup information from JSON file

##### save_backup_info(self)

Save backup information to JSON file

##### update_calendar(self)

Update calendar to show backup dates

##### update_backup_list(self)

Update the list of available backups

##### on_date_selected(self, date)

Handle date selection in calendar

##### on_backup_selected(self, item)

Handle backup selection from list

##### perform_backup(self)

Perform database backup

##### backup_sqlite(self)

Backup SQLite database

##### backup_postgresql(self)

Backup PostgreSQL database

##### on_backup_finished(self, success, message)

Handle backup completion

##### perform_restore(self)

Perform database restore

##### restore_sqlite(self, backup_path)

Restore SQLite database

##### restore_postgresql(self, backup_path)

Restore PostgreSQL database

##### delete_backup(self)

Delete selected backup

### BackupWorker

Worker thread for backup operations

**Inherits from**: QThread

#### Methods

##### __init__(self, command, env)

##### run(self)

Execute backup command

### BackupRestoreDialog

Advanced Backup/Restore Dialog with calendar and progress tracking

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### init_ui(self)

Initialize the user interface

##### load_settings(self)

Load database settings

##### load_backup_info(self)

Load backup information from JSON file

##### save_backup_info(self)

Save backup information to JSON file

##### update_calendar(self)

Update calendar to show backup dates

##### update_backup_list(self)

Update the list of available backups

##### on_date_selected(self, date)

Handle date selection in calendar

##### on_backup_selected(self, item)

Handle backup selection from list

##### perform_backup(self)

Perform database backup

##### backup_sqlite(self)

Backup SQLite database

##### backup_postgresql(self)

Backup PostgreSQL database

##### on_backup_finished(self, success, message)

Handle backup completion

##### perform_restore(self)

Perform database restore

##### restore_sqlite(self, backup_path)

Restore SQLite database

##### restore_postgresql(self, backup_path)

Restore PostgreSQL database

##### delete_backup(self)

Delete selected backup

### BackupWorker

Worker thread for backup operations

**Inherits from**: QThread

#### Methods

##### __init__(self, command, env)

##### run(self)

Execute backup command

### BackupRestoreDialog

Advanced Backup/Restore Dialog with calendar and progress tracking

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### init_ui(self)

Initialize the user interface

##### load_settings(self)

Load database settings

##### load_backup_info(self)

Load backup information from JSON file

##### save_backup_info(self)

Save backup information to JSON file

##### update_calendar(self)

Update calendar to show backup dates

##### update_backup_list(self)

Update the list of available backups

##### on_date_selected(self, date)

Handle date selection in calendar

##### on_backup_selected(self, item)

Handle backup selection from list

##### perform_backup(self)

Perform database backup

##### backup_sqlite(self)

Backup SQLite database

##### backup_postgresql(self)

Backup PostgreSQL database

##### on_backup_finished(self, success, message)

Handle backup completion

##### perform_restore(self)

Perform database restore

##### restore_sqlite(self, backup_path)

Restore SQLite database

##### restore_postgresql(self, backup_path)

Restore PostgreSQL database

##### delete_backup(self)

Delete selected backup

### BackupWorker

Worker thread for backup operations

**Inherits from**: QThread

#### Methods

##### __init__(self, command, env)

##### run(self)

Execute backup command

### BackupRestoreDialog

Advanced Backup/Restore Dialog with calendar and progress tracking

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### init_ui(self)

Initialize the user interface

##### load_settings(self)

Load database settings

##### load_backup_info(self)

Load backup information from JSON file

##### save_backup_info(self)

Save backup information to JSON file

##### update_calendar(self)

Update calendar to show backup dates

##### update_backup_list(self)

Update the list of available backups

##### on_date_selected(self, date)

Handle date selection in calendar

##### on_backup_selected(self, item)

Handle backup selection from list

##### perform_backup(self)

Perform database backup

##### backup_sqlite(self)

Backup SQLite database

##### backup_postgresql(self)

Backup PostgreSQL database

##### on_backup_finished(self, success, message)

Handle backup completion

##### perform_restore(self)

Perform database restore

##### restore_sqlite(self, backup_path)

Restore SQLite database

##### restore_postgresql(self, backup_path)

Restore PostgreSQL database

##### delete_backup(self)

Delete selected backup

