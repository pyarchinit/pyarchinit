# Tutorial 19: Mehrbenutzerbetrieb mit PostgreSQL

## Einführung

PyArchInit unterstützt den **Mehrbenutzerbetrieb** durch die Verwendung von **PostgreSQL/PostGIS** als Datenbank-Backend. Diese Konfiguration ermöglicht es mehreren Benutzern, gleichzeitig von verschiedenen Arbeitsplätzen am selben archäologischen Projekt zu arbeiten.

### Vorteile des Mehrbenutzerbetriebs

| Aspekt | SQLite | PostgreSQL Mehrbenutzerbetrieb |
|--------|--------|-------------------------------|
| Gleichzeitige Benutzer | 1 | Unbegrenzt |
| Fernzugriff | Nein | Ja |
| Berechtigungsverwaltung | Nein | Ja |
| Zentrales Backup | Manuell | Automatisierbar |
| Leistung | Gut | Ausgezeichnet |
| Skalierbarkeit | Begrenzt | Hoch |

## Voraussetzungen

### Server

1. **PostgreSQL** 12 oder höher
2. **PostGIS** 3.0 oder höher
3. Server im Netzwerk erreichbar (LAN oder Internet)

### Client

1. QGIS mit installiertem PyArchInit
2. Netzwerkverbindung zum Server
3. Zugangsdaten

## Server-Konfiguration

### PostgreSQL-Installation

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Installer von [postgresql.org](https://www.postgresql.org/download/windows/) herunterladen
- Mit Stack Builder für PostGIS installieren

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Datenbank-Erstellung

```sql
-- Als Superuser verbinden
sudo -u postgres psql

-- Datenbank erstellen
CREATE DATABASE pyarchinit_db;

-- PostGIS aktivieren
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Anwendungsbenutzer erstellen
CREATE USER pyarchinit WITH PASSWORD 'sicheres_passwort';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Netzwerkzugriff konfigurieren

`pg_hba.conf` bearbeiten:
```
# Verbindungen vom lokalen Netzwerk erlauben
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# Oder von jeder IP (weniger sicher)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

`postgresql.conf` bearbeiten:
```
listen_addresses = '*'
```

PostgreSQL neu starten:
```bash
sudo systemctl restart postgresql
```

## Client PyArchInit-Konfiguration

### Ersteinrichtung

1. **PyArchInit** → **Konfiguration**
2. Tab **Datenbank**
3. **PostgreSQL** auswählen
4. Felder ausfüllen:

| Feld | Wert |
|------|------|
| Server | IP-Adresse oder Hostname |
| Port | 5432 (Standard) |
| Datenbank | pyarchinit_db |
| Benutzer | pyarchinit |
| Passwort | sicheres_passwort |

### Verbindungstest

1. **Verbindung testen** klicken
2. Erfolgsmeldung überprüfen
3. Konfiguration speichern

### Schema-Erstellung

Bei neuer Datenbank:
1. **Schema erstellen** klicken
2. Tabellenerstellung abwarten
3. Struktur überprüfen

## Benutzerverwaltung

### Zusätzliche Benutzer erstellen

```sql
-- Benutzer mit Vollzugriff
CREATE USER archaeologe1 WITH PASSWORD 'passwort1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO archaeologe1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO archaeologe1;

-- Nur-Lese-Benutzer
CREATE USER berater1 WITH PASSWORD 'passwort2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO berater1;
```

### Empfohlene Zugriffsebenen

| Rolle | Berechtigungen | Verwendung |
|-------|---------------|------------|
| Admin | ALL | Konfiguration, Verwaltung |
| Archäologe | SELECT, INSERT, UPDATE, DELETE | Tägliche Arbeit |
| Spezialist | SELECT, INSERT, UPDATE (spezifische Tabellen) | Spezialdateneingabe |
| Berater | SELECT | Dateneinsicht |
| Backup | SELECT | Backup-Skripte |

### Rollenverwaltung

```sql
-- Gruppenrolle erstellen
CREATE ROLE archaeologen;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO archaeologen;

-- Benutzer zur Gruppe hinzufügen
GRANT archaeologen TO archaeologe1;
GRANT archaeologen TO archaeologe2;
```

## Mehrbenutzerbetrieb-Workflow

### Arbeitsorganisation

#### Nach Areal
- Verschiedene Areale verschiedenen Benutzern zuweisen
- Überlappungen vermeiden

#### Nach Typologie
- Ein Benutzer: Ablagerungs-SE
- Anderer Benutzer: Mauerwerks-SE
- Anderer Benutzer: Funde

#### Nach Fundort
- Verschiedene Fundorte an verschiedene Teams

### Konfliktverwaltung

#### Datensatzsperre (empfohlen)
1. Vor Änderung überprüfen, ob niemand am selben Datensatz arbeitet
2. Mit dem Team kommunizieren

#### Konfliktlösung
Bei gleichzeitigen Änderungen:
1. Die letzte Änderung hat Vorrang
2. Daten nach jeder Sitzung überprüfen
3. Feld "Änderungsdatum" zur Nachverfolgung verwenden

### Synchronisation

Mit PostgreSQL ist die Synchronisation automatisch:
- Jede Änderung ist sofort für andere sichtbar
- Keine manuelle Synchronisation erforderlich
- Formular aktualisieren um Updates zu sehen

## Backup und Sicherheit

### Automatisches Backup

Tägliches Backup-Skript:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Nur die letzten 30 Tage behalten
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Mit cron planen:
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Wiederherstellung

```bash
# Von Backup wiederherstellen
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Sicherheit

1. **Starke Passwörter**: Mindestens 12 Zeichen, Mix aus Groß-/Kleinbuchstaben/Zahlen
2. **SSL-Verbindungen**: SSL für Remote-Verbindungen aktivieren
3. **Firewall**: Zugriff auf Port 5432 einschränken
4. **Updates**: PostgreSQL aktuell halten
5. **Audit-Log**: Verbindungsprotokollierung aktivieren

### SSL für Remote-Verbindungen

In `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

In `pg_hba.conf`:
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Überwachung

### Aktive Verbindungen

```sql
SELECT
    usename,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity
WHERE datname = 'pyarchinit_db';
```

### Datenbankgröße

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Aktive Sperren

```sql
SELECT
    l.locktype,
    l.relation::regclass,
    l.mode,
    l.granted,
    a.usename,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = 'pyarchinit_db');
```

## Migration von SQLite

### Export aus SQLite

1. PyArchInit mit SQLite-Datenbank öffnen
2. **PyArchInit** → **Utilities** → **Export Database**
3. In SQL-Format exportieren

### Import in PostgreSQL

1. PostgreSQL-Verbindung konfigurieren
2. Leeres Schema erstellen
3. Exportierte Daten importieren

## Best Practices

### 1. Planung

- Rollen und Verantwortlichkeiten definieren
- Arbeitskonventionen festlegen
- Prozeduren dokumentieren

### 2. Kommunikation

- Team-Kommunikationskanal (Chat, E-Mail)
- Beginn/Ende von Arbeitssitzungen melden
- Bereiche in Bearbeitung kommunizieren

### 3. Backup

- Tägliche automatische Backups
- Regelmäßige Wiederherstellungstests
- Off-Site-Backup

### 4. Schulung

- Training zum Mehrbenutzerbetrieb-Workflow
- Prozedurdokumentation
- Technischer Support verfügbar

## Problemlösung

### Verbindung abgelehnt

**Ursachen**:
- Server nicht erreichbar
- Firewall blockiert
- Falsche Anmeldedaten

**Lösungen**:
- Netzwerkverbindung überprüfen
- Firewall-Regeln kontrollieren
- Anmeldedaten überprüfen

### Verbindungs-Timeout

**Ursachen**:
- Langsames Netzwerk
- Server überlastet
- Zu viele Verbindungen

**Lösungen**:
- Netzwerk optimieren
- Server-Ressourcen erhöhen
- Gleichzeitige Verbindungen begrenzen

### Datenbank-Sperre

**Ursache**: Nicht abgeschlossene Transaktionen

**Lösung**:
```sql
-- Blockierende Prozesse identifizieren
SELECT * FROM pg_locks WHERE NOT granted;

-- Prozess beenden (mit Vorsicht)
SELECT pg_terminate_backend(pid);
```

## Referenzen

### Konfiguration
- `modules/db/pyarchinit_conn_strings.py` - Verbindungszeichenfolgen
- `gui/pyarchinit_Setting.py` - Konfigurations-Oberfläche

### Externe Dokumentation
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

## Video-Tutorial

### Mehrbenutzerbetrieb-Setup
`[Platzhalter: video_multiuser_setup.mp4]`

**Inhalte**:
- PostgreSQL-Installation
- Server-Konfiguration
- Client-Setup
- Benutzerverwaltung

**Voraussichtliche Dauer**: 20-25 Minuten

### Kollaborativer Workflow
`[Platzhalter: video_multiuser_workflow.mp4]`

**Inhalte**:
- Arbeitsorganisation
- Konfliktverwaltung
- Best Practices

**Voraussichtliche Dauer**: 12-15 Minuten

---

*Letzte Aktualisierung: Januar 2026*
