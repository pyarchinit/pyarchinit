# Tutorial 18: Backup und Wiederherstellung

## Einführung

Die **Backup**-Verwaltung ist grundlegend für die Sicherheit archäologischer Daten. PyArchInit bietet Werkzeuge zur Durchführung von Datenbank- und zugehörigen Dateien-Backups, sowohl für SQLite als auch für PostgreSQL.

### Bedeutung des Backups

- **Datenschutz**: Schutz vor versehentlichem Verlust
- **Versionierung**: Möglichkeit zur Rückkehr zu früheren Zuständen
- **Migration**: Transfer zwischen Systemen
- **Archivierung**: Aufbewahrung abgeschlossener Projekte

---

## Backup-Typen

### SQLite-Datenbank-Backup

Für SQLite-Datenbanken (`.sqlite`-Datei):
- Direkte Kopie der Datenbankdatei
- Einfach und schnell
- Enthält alle Daten

### PostgreSQL-Datenbank-Backup

Für PostgreSQL-Datenbanken:
- Export über `pg_dump`
- SQL- oder Custom-Format
- Kann Schema und/oder Daten enthalten

### Vollständiges Backup

Enthält:
- Datenbank
- Mediendateien (Bilder, Videos)
- Konfigurationsdateien
- Generierte Berichte

---

## Zugriff auf Backup-Funktionen

### Über Konfigurationspanel

1. Menü **PyArchInit** > **Sketchy GPT** > **Settings** (oder Settings direkt)
2. Im Konfigurationsfenster
3. Tab oder Abschnitt für Backup

### Über Dateisystem

Für SQLite kann direkt kopiert werden:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## SQLite-Backup

### Manuelle Prozedur

1. Alle offenen PyArchInit-Formulare **schließen**
2. Datenbankdatei **finden**:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   Unter Windows:
   ```
   C:\Users\[benutzer]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. Datei in einen Backup-Ordner **kopieren**:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. Integrität **überprüfen** durch Öffnen der Kopie mit einem SQLite-Tool

### Automatisches Skript (optional)

Für automatische Backups ein Skript erstellen:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Backup abgeschlossen: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Backup abgeschlossen: %DEST%
```

---

## PostgreSQL-Backup

### Mit pg_dump

1. Terminal/Eingabeaufforderung **öffnen**

2. pg_dump **ausführen**:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Parameter:
   - `-h`: Datenbank-Host
   - `-U`: Benutzer
   - `-d`: Datenbankname
   - `-F c`: Custom-Format (komprimiert)
   - `-f`: Ausgabedatei

3. Passwort **eingeben** wenn angefordert

### Nur-Daten-Backup

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_daten.sql
```

### Nur-Schema-Backup

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_schema.sql
```

---

## Mediendateien-Backup

### Medienordner

Die Mediendateien befinden sich im Ordner:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Prozedur

1. Ordner **finden**:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. Gesamten Ordner **kopieren**:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Komprimieren** (optional):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Wiederherstellung (Restore)

### SQLite-Wiederherstellung

1. QGIS und PyArchInit **schließen**
2. Aktuelle Datenbank **umbenennen** (zur Sicherheit):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. Backup in den Originalordner **kopieren**:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. QGIS **neu starten**

### PostgreSQL-Wiederherstellung

1. Leere Datenbank **erstellen** (falls nötig):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. Backup **wiederherstellen**:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. PyArchInit-Konfiguration **aktualisieren** für neue Datenbank

### Mediendateien-Wiederherstellung

1. Backup-Dateien in den Medienordner **kopieren**:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Vollständiges Projekt-Backup

### Was einzuschließen ist

| Element | Pfad |
|---------|------|
| SQLite-Datenbank | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Medien | `pyarchinit_image_folder/` |
| Generierte PDFs | `pyarchinit_PDF_folder/` |
| Berichte | `pyarchinit_Report_folder/` |
| Konfiguration | `pyarchinit_Logo_folder/`, .txt-Dateien |

### Skript für vollständiges Backup

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Datenbank
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Medien
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF und Berichte
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Komprimieren
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Vollständiges Backup: $BACKUP_DIR.tar.gz"
```

---

## Best Practices

### Backup-Häufigkeit

| Aktivitätstyp | Empfohlene Häufigkeit |
|---------------|----------------------|
| Aktive Grabung | Täglich |
| Nachgrabung | Wöchentlich |
| Archivierung | Vor jeder signifikanten Änderung |

### Aufbewahrung

- Mindestens **3 Kopien** an verschiedenen Orten aufbewahren
- **Cloud-Speicher** für Redundanz nutzen
- **Regelmäßig die Integrität** der Backups überprüfen

### Benennung

Empfohlenes Format:
```
[projekt]_[typ]_[datum]_[version]
Beispiel: roemische_villa_db_20240115_v1.sqlite
```

### Dokumentation

Ein Backup-Protokoll erstellen:
```
Datum: 2024-01-15
Typ: Vollständiges Backup
Datei: roemische_villa_backup_20240115.tar.gz
Größe: 2.5 GB
Notizen: Vor Abschluss Kampagne 2024
```

---

## Backup-Automatisierung

### Cron Job (Linux/Mac)

Zu crontab hinzufügen (`crontab -e`):
```
# Tägliches Backup um 23:00
0 23 * * * /path/to/backup_script.sh
```

### Aufgabenplanung (Windows)

1. **Aufgabenplanung** öffnen
2. Einfache Aufgabe erstellen
3. Trigger einstellen (täglich)
4. Aktion: Programm starten > Batch-Skript

---

## Fehlerbehebung

### Problem: Datenbank nach Wiederherstellung beschädigt

**Ursache**: Unvollständige oder beschädigte Backup-Datei.

**Lösung**:
1. Integrität prüfen mit `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Früheres Backup verwenden
3. Wiederherstellung mit SQLite-Tools versuchen

### Problem: Übermäßige Backup-Größe

**Ursache**: Viele Mediendateien oder sehr große Datenbank.

**Lösung**:
1. Backups komprimieren
2. VACUUM auf der Datenbank ausführen
3. Ältere Medien separat archivieren

### Problem: pg_dump Verbindungsfehler

**Ursache**: Falsche Verbindungsparameter.

**Lösung**:
1. Host, Port, Benutzer überprüfen
2. pg_hba.conf auf Berechtigungen prüfen
3. Verbindung mit psql testen

---

## Migration zwischen Datenbanken

### Von SQLite zu PostgreSQL

1. Daten aus SQLite exportieren
2. Schema in PostgreSQL erstellen
3. Daten importieren

PyArchInit verwaltet dies über die Konfigurationseinstellungen.

### Von PostgreSQL zu SQLite

1. Daten aus PostgreSQL exportieren
2. SQLite-Datenbank erstellen
3. Daten importieren

---

## Referenzen

### Standardpfade

| System | Basispfad |
|--------|-----------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[benutzer]\pyarchinit\` |

### Nützliche Werkzeuge

- **SQLite Browser**: SQLite-Datenbank anzeigen/bearbeiten
- **pgAdmin**: PostgreSQL-Verwaltung
- **7-Zip/tar**: Backup-Komprimierung
- **rsync**: Inkrementelle Synchronisation

---

## Video-Tutorial

### Backup und Datensicherheit
**Dauer**: 10-12 Minuten
- Backup-Prozeduren
- Datenbank-Wiederherstellung
- Automatisierung

[Platzhalter Video: video_backup_restore.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
