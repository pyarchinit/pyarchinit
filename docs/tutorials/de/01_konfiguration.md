# PyArchInit - Konfigurationsanleitung

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Zugriff auf die Konfiguration](#zugriff-auf-die-konfiguration)
3. [Tab Verbindungsparameter](#tab-verbindungsparameter)
4. [Tab DB Installation](#tab-db-installation)
5. [Tab Import-Tools](#tab-import-tools)
6. [Tab Graphviz](#tab-graphviz)
7. [Tab PostgreSQL](#tab-postgresql)
8. [Tab Hilfe](#tab-hilfe)
9. [Tab FTP zu Lizmap](#tab-ftp-zu-lizmap)

---

## Einführung

Das PyArchInit-Konfigurationsfenster ermöglicht die Einstellung aller Parameter, die für das ordnungsgemäße Funktionieren des Plugins erforderlich sind. Bevor Sie mit der Dokumentation einer archäologischen Ausgrabung beginnen, müssen Sie die Datenbankverbindung und die Ressourcenpfade korrekt konfigurieren.

> **Video-Tutorial**: [Link zum Einführungsvideo der Konfiguration einfügen]

---

## Zugriff auf die Konfiguration

Für den Zugriff auf die Konfiguration:
1. QGIS öffnen
2. Menü **PyArchInit** → **Config**

Oder klicken Sie in der PyArchInit-Toolbar auf das Symbol **Einstellungen**.

![Zugriff auf die Konfiguration](images/01_konfiguration/01_menu_config.png)
*Abbildung 1: Zugriff auf das Konfigurationsfenster über das PyArchInit-Menü*

![PyArchInit-Toolbar](images/01_konfiguration/02_toolbar_config.png)
*Abbildung 2: Konfigurationssymbol in der Toolbar*

---

## Tab Verbindungsparameter

Dies ist die Hauptregisterkarte zur Konfiguration der Datenbankverbindung.

![Tab Verbindungsparameter](images/01_konfiguration/03_tab_parametri_connessione.png)
*Abbildung 3: Tab Verbindungsparameter - Vollständige Ansicht*

### Abschnitt DB-Einstellungen

| Feld | Beschreibung |
|------|-------------|
| **Database** | Datenbanktyp auswählen: `sqlite` (lokal) oder `postgres` (Server) |
| **Host** | PostgreSQL-Serveradresse (z.B. `localhost` oder Server-IP) |
| **DBname** | Datenbankname (z.B. `pyarchinit`) |
| **Port** | Verbindungsport (Standard: `5432` für PostgreSQL) |
| **User** | Benutzername für die Verbindung |
| **Password** | Benutzerpasswort |
| **SSL Mode** | SSL-Modus für PostgreSQL: `allow`, `prefer`, `require`, `disable` |

![DB-Einstellungen](images/01_konfiguration/04_db_settings.png)
*Abbildung 4: Abschnitt DB-Einstellungen*

#### Datenbankauswahl

**SQLite/Spatialite** (Empfohlen für Einzelbenutzer):
- Lokale Datenbank, kein Server erforderlich
- Ideal für individuelle oder kleine Projekte
- Die `.sqlite`-Datei wird im Ordner `pyarchinit_DB_folder` gespeichert

![SQLite-Konfiguration](images/01_konfiguration/05_config_sqlite.png)
*Abbildung 5: Beispiel SQLite-Konfiguration*

**PostgreSQL/PostGIS** (Empfohlen für Teams):
- Datenbank auf Server, Mehrbenutzerzugriff
- PostgreSQL mit PostGIS-Erweiterung erforderlich
- Unterstützt Benutzer- und Rechteverwaltung
- Ideal für große Projekte mit mehreren Bearbeitern

![PostgreSQL-Konfiguration](images/01_konfiguration/06_config_postgres.png)
*Abbildung 6: Beispiel PostgreSQL-Konfiguration*

> **Video-Tutorial**: [Link zum Video zur Datenbankkonfiguration einfügen]

### Abschnitt Pfadeinstellungen

| Feld | Beschreibung | Schaltfläche |
|------|-------------|--------------|
| **Thumbnail path** | Pfad zum Speichern der Miniaturbilder | `...` zum Durchsuchen |
| **Image resize** | Pfad für skalierte Bilder | `...` zum Durchsuchen |
| **Logo path** | Pfad zum benutzerdefinierten Logo für Berichte | `...` zum Durchsuchen |

![Pfadeinstellungen](images/01_konfiguration/07_path_settings.png)
*Abbildung 7: Abschnitt Pfadeinstellungen*

#### Unterstützte Remote-Pfade

PyArchInit unterstützt auch Remote-Speicher:
- **Google Drive**: `gdrive://folder/path/`
- **Dropbox**: `dropbox://folder/path/`
- **Amazon S3**: `s3://bucket/path/`
- **Cloudinary**: `cloudinary://cloud_name/folder/`
- **WebDAV**: `webdav://server/path/`
- **HTTP/HTTPS**: `https://server/path/`

![Remote-Speicher](images/01_konfiguration/08_remote_storage.png)
*Abbildung 8: Beispiel Remote-Speicher-Konfiguration*

### Abschnitt Experimentell

| Feld | Beschreibung |
|------|-------------|
| **Experimental** | Aktiviert experimentelle Funktionen (`Ja`/`Nein`) |

### Abschnitt Fundort-Aktivierung

| Feld | Beschreibung |
|------|-------------|
| **Aktiviere Fundort-Abfrage** | Wählt den aktiven Fundort zum Filtern der Daten in den Formularen |

Diese Option ist wichtig, wenn Sie mit mehreren archäologischen Fundorten in derselben Datenbank arbeiten. Bei Auswahl eines Fundorts zeigen alle Formulare nur die Daten dieses Fundorts an.

![Fundort-Auswahl](images/01_konfiguration/09_selezione_sito.png)
*Abbildung 9: Auswahl des aktiven Fundorts*

### Aktionsschaltflächen

| Schaltfläche | Funktion |
|--------------|----------|
| **Parameter speichern** | Speichert alle konfigurierten Einstellungen |
| **DB aktualisieren** | Aktualisiert das bestehende Datenbankschema ohne Datenverlust |

### Datenbank-Ausrichtungsfunktionen

| Schaltfläche | Beschreibung |
|--------------|-------------|
| **Postgres ausrichten** | Richtet die PostgreSQL-Datenbankstruktur aus und aktualisiert sie |
| **Spatialite ausrichten** | Richtet die SQLite-Datenbankstruktur aus und aktualisiert sie |
| **EPSG-Code** | EPSG-Code des Datenbank-Referenzsystems eingeben |

![Datenbank-Ausrichtung](images/01_konfiguration/10_allineamento_db.png)
*Abbildung 10: Schaltflächen zur Datenbankausrichtung*

### Zusammenfassung

Der Abschnitt Zusammenfassung zeigt eine Übersicht der aktuellen Einstellungen im HTML-Format.

![Zusammenfassung](images/01_konfiguration/11_summary.png)
*Abbildung 11: Zusammenfassungsbereich mit Konfigurationsübersicht*

---

## Tab DB Installation

Diese Registerkarte ermöglicht das Erstellen einer neuen Datenbank von Grund auf.

![Tab DB Installation](images/01_konfiguration/12_tab_installazione_db.png)
*Abbildung 12: Tab DB Installation - Vollständige Ansicht*

> **Video-Tutorial**: [Link zum Video zur Datenbankinstallation einfügen]

### Datenbank installieren (PostgreSQL/PostGIS)

| Feld | Beschreibung |
|------|-------------|
| **host** | Serveradresse (Standard: `localhost`) |
| **port (5432)** | PostgreSQL-Server-Port |
| **user** | Benutzer mit DB-Erstellungsrechten (z.B. `postgres`) |
| **password** | Benutzerpasswort |
| **db name** | Name der neuen Datenbank (Standard: `pyarchinit`) |
| **SRID auswählen** | Räumliches Referenzsystem (z.B. `4326` für WGS84, `32632` für UTM 32N) |

![PostgreSQL-Installation](images/01_konfiguration/13_install_postgres.png)
*Abbildung 13: PostgreSQL-Datenbankinstallationsformular*

**Schaltfläche Installieren**: Erstellt die Datenbank mit allen erforderlichen Tabellen.

### Datenbank installieren (SpatiaLite)

| Feld | Beschreibung |
|------|-------------|
| **db name** | Datenbankdateiname (Standard: `pyarchinit`) |
| **SRID auswählen** | Räumliches Referenzsystem |

![SQLite-Installation](images/01_konfiguration/14_install_sqlite.png)
*Abbildung 14: SQLite-Datenbankinstallationsformular*

**Schaltfläche Installieren**: Erstellt die lokale SQLite-Datenbank.

### Häufige SRIDs in Deutschland

| SRID | Beschreibung |
|------|-------------|
| 4326 | WGS 84 (geographische Koordinaten) |
| 25832 | ETRS89 / UTM Zone 32N (Deutschland) |
| 25833 | ETRS89 / UTM Zone 33N (Ostdeutschland) |
| 31466 | DHDN / 3-Grad Gauss-Krüger Zone 2 |
| 31467 | DHDN / 3-Grad Gauss-Krüger Zone 3 |

![UTM-Zonen](images/01_konfiguration/15_zone_utm.png)
*Abbildung 15: Karte der UTM-Zonen*

---

## Tab Import-Tools

Diese Registerkarte ermöglicht den Import von Daten aus anderen Datenbanken oder CSV-Dateien.

![Tab Import-Tools](images/01_konfiguration/16_tab_importazione.png)
*Abbildung 16: Tab Import-Tools - Vollständige Ansicht*

> **Video-Tutorial**: [Link zum Video zum Datenimport einfügen]

### Abschnitt Datenimport

#### Quelldatenbank (Ressource)

| Feld | Beschreibung |
|------|-------------|
| **Database** | Quelldatenbanktyp (`sqlite` oder `postgres`) |
| **Host/Port/Username/Password** | Anmeldedaten für PostgreSQL-Quelle |
| **...** | SQLite-Quelldatei auswählen |

![Quelldatenbank](images/01_konfiguration/17_db_sorgente.png)
*Abbildung 17: Quelldatenbank-Konfiguration*

#### Zieldatenbank

| Feld | Beschreibung |
|------|-------------|
| **Database** | Zieldatenbanktyp |
| **Host/Port/Username/Password** | Anmeldedaten für PostgreSQL-Ziel |
| **...** | SQLite-Zieldatei auswählen |

![Zieldatenbank](images/01_konfiguration/18_db_destinazione.png)
*Abbildung 18: Zieldatenbank-Konfiguration*

### Verfügbare Tabellen für Import

| Tabelle | Beschreibung |
|---------|-------------|
| SITE | Archäologische Fundorte |
| US | Stratigraphische Einheiten |
| PERIODIZZAZIONE | Periodisierung und Phasen |
| INVENTARIO_MATERIALI | Fundinventar |
| TMA | Archäologische Materialtabellen |
| POTTERY | Keramik |
| STRUTTURA | Strukturen |
| TOMBA | Gräber |
| SCHEDAIND | Anthropologische Individuen |
| ARCHEOZOOLOGY | Archäozoologische Daten |
| MEDIA | Mediendateien |
| ALL | Alle Tabellen |

### Import-Optionen

| Option | Beschreibung |
|--------|-------------|
| **Replace** | Ersetzt vorhandene Datensätze |
| **Ignore** | Ignoriert Duplikate |
| **Abort** | Bricht bei Fehler ab |
| **Apply Constraints** | Wendet Eindeutigkeitsbeschränkungen auf Thesaurus an |

![Import-Optionen](images/01_konfiguration/19_opzioni_import.png)
*Abbildung 19: Import-Optionen*

### Geometrie-Import

| Layer | Beschreibung |
|-------|-------------|
| PYSITO_POLYGON | Fundort-Polygone |
| PYSITO_POINT | Fundort-Punkte |
| PYUS | Stratigraphische Einheiten |
| PYUSM | Mauerwerk-Einheiten |
| PYQUOTE | Höhenpunkte |
| PYSTRUTTURE | Strukturen |
| PYREPERTI | Funde |
| PYINDIVIDUI | Individuen |

![Geometrie-Import](images/01_konfiguration/20_import_geometrie.png)
*Abbildung 20: Layer-Auswahl für Geometrie-Import*

### Schaltflächen

| Schaltfläche | Funktion |
|--------------|----------|
| **Import Table** | Importiert die Daten der ausgewählten Tabelle |
| **Import Geometry** | Importiert die ausgewählten Geometrien |
| **Konvertiere DB zu Spatialite** | Konvertiert von PostgreSQL zu SQLite |
| **Konvertiere DB zu Postgres** | Konvertiert von SQLite zu PostgreSQL |

---

## Tab Graphviz

Graphviz ist erforderlich, um Harris-Matrix-Diagramme zu generieren.

![Tab Graphviz](images/01_konfiguration/21_tab_graphviz.png)
*Abbildung 21: Tab Graphviz*

### Konfiguration

| Feld | Beschreibung |
|------|-------------|
| **bin-Pfad** | Pfad zum Graphviz `/bin`-Ordner |
| **...** | Durchsuchen zur Ordnerauswahl |
| **Speichern** | Speichert den Pfad in der PATH-Umgebungsvariable |

### Graphviz-Installation

**Windows**: Von https://graphviz.org/download/ herunterladen und installieren

![Graphviz-Download](images/01_konfiguration/22_graphviz_download.png)
*Abbildung 22: Graphviz-Download-Seite*

**macOS**:
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install graphviz
```

Wenn Graphviz bereits korrekt im System-PATH installiert ist, werden die Felder automatisch deaktiviert.

> **Video-Tutorial**: [Link zum Graphviz-Video einfügen]

---

## Tab PostgreSQL

Konfiguration des PostgreSQL-Pfads für erweiterte Operationen.

![Tab PostgreSQL](images/01_konfiguration/23_tab_postgresql.png)
*Abbildung 23: Tab PostgreSQL*

| Feld | Beschreibung |
|------|-------------|
| **bin-Pfad** | Pfad zum PostgreSQL `/bin`-Ordner |
| **...** | Durchsuchen zur Ordnerauswahl |
| **Speichern** | Speichert den Pfad in der PATH-Umgebungsvariable |

Erforderlich für Operationen wie Datenbank-Dump/Restore.

---

## Tab Hilfe

Enthält Hilferessourcen und Dokumentation.

![Tab Hilfe](images/01_konfiguration/24_tab_help.png)
*Abbildung 24: Tab Hilfe*

### Nützliche Links

| Ressource | Beschreibung |
|-----------|-------------|
| **Video-Tutorials** | Links zu YouTube-Video-Tutorials |
| **Online-Dokumentation** | https://pyarchinit.github.io/pyarchinit_doc/index.html |
| **Facebook** | UnaQuantum-Seite |

---

## Tab FTP zu Lizmap

Ermöglicht die Veröffentlichung von Daten auf einem Lizmap-Server für die Webvisualisierung.

![Tab FTP Lizmap](images/01_konfiguration/25_tab_ftp_lizmap.png)
*Abbildung 25: Tab FTP zu Lizmap*

> **Video-Tutorial**: [Link zum Lizmap-Video einfügen]

### FTP-Verbindungsparameter

| Feld | Beschreibung |
|------|-------------|
| **IP-Adresse** | IP-Adresse des FTP-Servers |
| **Port** | FTP-Port (Standard: 21) |
| **User** | FTP-Benutzername |
| **Password** | FTP-Passwort |

### Verfügbare Operationen

| Schaltfläche | Funktion |
|--------------|----------|
| **Verbinden** | Mit FTP-Server verbinden |
| **Trennen** | Vom Server trennen |
| **Verzeichnis wechseln** | Aktuelles Verzeichnis wechseln |
| **Verzeichnis erstellen** | Neues Verzeichnis erstellen |
| **Datei hochladen** | Datei auf Server hochladen |
| **Datei herunterladen** | Datei vom Server herunterladen |
| **Datei löschen** | Datei löschen |
| **Verzeichnis löschen** | Verzeichnis löschen |

---

## Administrator-Funktionen (nur PostgreSQL)

Bei Verbindung als Administrator erscheint ein zusätzlicher Abschnitt:

![Admin-Funktionen](images/01_konfiguration/26_funzioni_admin.png)
*Abbildung 26: Abschnitt Administrator-Funktionen*

### Benutzer- und Rechteverwaltung
Ermöglicht das Erstellen, Ändern und Löschen von Benutzern mit verschiedenen Zugriffsebenen.

![Benutzerverwaltung](images/01_konfiguration/27_gestione_utenti.png)
*Abbildung 27: Dialog Benutzerverwaltung*

### Echtzeit-Aktivitätsmonitor
Zeigt in Echtzeit die Datenbankaktivitäten und verbundenen Benutzer an.

![Aktivitätsmonitor](images/01_konfiguration/28_monitor_attivita.png)
*Abbildung 28: Echtzeit-Aktivitätsmonitor*

---

## Empfohlener Arbeitsablauf für ein neues Projekt

> **Video-Tutorial**: [Link zum Video des vollständigen Arbeitsablaufs einfügen]

1. **Konfiguration öffnen** über das PyArchInit-Menü
2. **Datenbanktyp wählen** (SQLite für Einzelnutzer, PostgreSQL für Teams)
3. **Tab DB Installation**: Neue Datenbank mit entsprechendem SRID erstellen
4. **Tab Verbindungsparameter**: Verbindungsparameter konfigurieren
5. **Pfade festlegen** für Thumbnails, Resize und Logo
6. **Parameter speichern**
7. **Verbindung testen** durch Öffnen eines beliebigen Formulars (z.B. Fundort)

---

## Fehlerbehebung

### PostgreSQL-Verbindungsfehler
- Überprüfen Sie, ob der PostgreSQL-Server gestartet ist
- Kontrollieren Sie Host, Port und Anmeldedaten
- Stellen Sie sicher, dass die PostGIS-Erweiterung installiert ist

### SQLite-Datenbank nicht gefunden
- Überprüfen Sie, ob die Datei im Ordner `pyarchinit_DB_folder` existiert
- Kontrollieren Sie die Lese-/Schreibrechte

### Graphviz funktioniert nicht
- Überprüfen Sie die Graphviz-Installation
- Setzen Sie den Pfad manuell im Tab Graphviz
- Starten Sie QGIS nach der Konfiguration neu

### Bilder werden nicht angezeigt
- Überprüfen Sie die Pfade für Thumbnail und Image resize
- Kontrollieren Sie, ob die Ordner existieren und zugänglich sind

---

## Technische Hinweise

- Die Einstellungen werden in den QgsSettings von QGIS gespeichert
- Die Standard-Datenbank ist `Home/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite`
- Debug-Logs werden in `[TEMP]/pyarchinit_debug.log` gespeichert
- Die Umgebungsvariable `PYARCHINIT_HOME` zeigt auf den `pyarchinit`-Ordner im Home-Verzeichnis

---

*PyArchInit-Dokumentation - Konfigurationsformular*
*Version: 4.9.x*
*Letzte Aktualisierung: Januar 2026*
