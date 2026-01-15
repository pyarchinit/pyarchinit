# Tutorial 18: Backup and Restore

## Introduction

**Backup** management is fundamental for archaeological data security. PyArchInit offers tools to backup the database and associated files, both for SQLite and PostgreSQL.

### Importance of Backup

- **Data protection**: safeguard against accidental loss
- **Versioning**: ability to return to previous states
- **Migration**: transfer between systems
- **Archiving**: preservation of completed projects

---

## Types of Backup

### SQLite Database Backup

For SQLite databases (`.sqlite` files):
- Direct copy of database file
- Simple and fast
- Includes all data

### PostgreSQL Database Backup

For PostgreSQL databases:
- Export via `pg_dump`
- SQL or custom format
- Can include schema and/or data

### Complete Backup

Includes:
- Database
- Media files (images, videos)
- Configuration files
- Generated reports

---

## Accessing Backup Functions

### Via Configuration Panel

1. Menu **PyArchInit** > **Sketchy GPT** > **Settings** (or Settings directly)
2. In the configuration window
3. Tab or section dedicated to backup

### Via File System

For SQLite, you can directly copy:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## SQLite Backup

### Manual Procedure

1. **Close** all open PyArchInit forms
2. **Locate** the database file:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   On Windows:
   ```
   C:\Users\[user]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Copy** the file to a backup folder:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Verify** integrity by opening the copy with an SQLite tool

### Automatic Script (optional)

For automatic backups, create a script:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Backup completed: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Backup completed: %DEST%
```

---

## PostgreSQL Backup

### Using pg_dump

1. **Open** a terminal/command prompt

2. **Run** pg_dump:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Parameters:
   - `-h`: database host
   - `-U`: user
   - `-d`: database name
   - `-F c`: custom format (compressed)
   - `-f`: output file

3. **Enter** password when prompted

### Data-Only Backup

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_data.sql
```

### Schema-Only Backup

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_schema.sql
```

---

## Media File Backup

### Media Folder

Media files are in the folder:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Procedure

1. **Locate** the folder:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Copy** the entire folder:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Compress** (optional):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Restore

### SQLite Restore

1. **Close** QGIS and PyArchInit
2. **Rename** the current database (for safety):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Copy** the backup to the original folder:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Restart** QGIS

### PostgreSQL Restore

1. **Create** an empty database (if needed):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Restore** the backup:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Update** PyArchInit configuration to use the new database

### Media File Restore

1. **Copy** backup files to media folder:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Complete Project Backup

### What to Include

| Element | Path |
|---------|------|
| SQLite Database | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Media | `pyarchinit_image_folder/` |
| Generated PDFs | `pyarchinit_PDF_folder/` |
| Reports | `pyarchinit_Report_folder/` |
| Configuration | `pyarchinit_Logo_folder/`, .txt files |

### Complete Backup Script

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Database
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Media
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF and Reports
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Compress
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Complete backup: $BACKUP_DIR.tar.gz"
```

---

## Best Practices

### Backup Frequency

| Activity Type | Recommended Frequency |
|---------------|----------------------|
| Active excavation | Daily |
| Post-excavation | Weekly |
| Archiving | Before every significant change |

### Retention

- Keep at least **3 copies** in different locations
- Use **cloud storage** for redundancy
- **Periodically verify** backup integrity

### Naming

Recommended format:
```
[project]_[type]_[date]_[version]
Example: roman_villa_db_20240115_v1.sqlite
```

### Documentation

Create a backup log:
```
Date: 2024-01-15
Type: Complete backup
File: roman_villa_backup_20240115.tar.gz
Size: 2.5 GB
Notes: Pre-closure 2024 campaign
```

---

## Backup Automation

### Cron Job (Linux/Mac)

Add to crontab (`crontab -e`):
```
# Daily backup at 23:00
0 23 * * * /path/to/backup_script.sh
```

### Task Scheduler (Windows)

1. Open **Task Scheduler**
2. Create basic task
3. Set trigger (daily)
4. Action: Start program > batch script

---

## Troubleshooting

### Problem: Database corrupted after restore

**Cause**: Incomplete or damaged backup file.

**Solution**:
1. Verify integrity with `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Use a previous backup
3. Attempt recovery with SQLite tools

### Problem: Excessive backup size

**Cause**: Many media files or very large database.

**Solution**:
1. Compress backups
2. Run VACUUM on database
3. Archive older media separately

### Problem: pg_dump connection error

**Cause**: Incorrect connection parameters.

**Solution**:
1. Verify host, port, user
2. Check pg_hba.conf for permissions
3. Test connection with psql

---

## Migration Between Databases

### From SQLite to PostgreSQL

1. Export data from SQLite
2. Create schema in PostgreSQL
3. Import data

PyArchInit manages this through configuration settings.

### From PostgreSQL to SQLite

1. Export data from PostgreSQL
2. Create SQLite database
3. Import data

---

## References

### Standard Paths

| System | Base Path |
|--------|-----------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[user]\pyarchinit\` |

### Useful Tools

- **SQLite Browser**: SQLite database viewing/editing
- **pgAdmin**: PostgreSQL management
- **7-Zip/tar**: backup compression
- **rsync**: incremental synchronization

---

## Video Tutorial

### Backup and Data Security
**Duration**: 10-12 minutes
- Backup procedures
- Database restore
- Automation

[Video placeholder: video_backup_restore.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
