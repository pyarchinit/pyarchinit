# Tutorial 20: Web-Veröffentlichung mit Lizmap

## Einführung

PyArchInit unterstützt die **Web-Veröffentlichung** archäologischer Daten durch **Lizmap**, eine Anwendung, die QGIS-Projekte in interaktive Webanwendungen umwandelt.

### Was ist Lizmap?

Lizmap besteht aus:
- **QGIS-Plugin**: Zur Konfiguration der Veröffentlichung
- **Lizmap Web Client**: Webanwendung zur Kartenansicht
- **QGIS Server**: Backend zur Kartenauslieferung

### Vorteile der Web-Veröffentlichung

| Aspekt | Beschreibung |
|--------|-------------|
| Zugänglichkeit | Daten über Browser abrufbar |
| Teilen | Einfache Verteilung an Stakeholder |
| Interaktivität | Zoom, Schwenken, Abfragen, Popups |
| Aktualisierung | Synchronisation mit Datenbank |
| Mobil | Zugriff von Smartphone/Tablet |

## Voraussetzungen

### Server

1. **QGIS Server** installiert
2. **Lizmap Web Client** konfiguriert
3. Webserver (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (empfohlen)

### Client

1. **QGIS Desktop** mit Lizmap-Plugin
2. **PyArchInit** konfiguriert
3. QGIS-Projekt gespeichert

## Lizmap-Plugin-Installation

### Aus QGIS

1. **Plugins** → **Plugins verwalten**
2. Nach "Lizmap" suchen
3. **Lizmap** installieren
4. QGIS neu starten

## Projektvorbereitung

### 1. Layer-Organisation

Empfohlene Struktur:
```
QGIS-Projekt
├── Gruppe: Basis
│   ├── Orthofoto
│   └── Kataster/Grundkarte
├── Gruppe: Grabung
│   ├── pyunitastratigrafiche
│   ├── pyunitastratigrafiche_usm
│   └── pyarchinit_quote
├── Gruppe: Dokumentation
│   ├── Georeferenzierte Fotos
│   └── Vermessungen
└── Gruppe: Analyse
    └── Harris-Matrix (Bild)
```

### 2. Layer-Styling

Für jeden Layer:
1. Passenden Stil anwenden
2. Beschriftungen konfigurieren
3. Sichtbarkeitsmaßstab einstellen

### 3. Popups und Attribute

Popups für jeden Layer konfigurieren:
1. Rechtsklick auf Layer → **Eigenschaften**
2. Tab **Darstellung**
3. **HTML Map Tip** konfigurieren

Beispiel-Popup für SE:
```html
<h3>SE [% "us_s" %]</h3>
<p><b>Areal:</b> [% "area_s" %]</p>
<p><b>Typ:</b> [% "tipo_us_s" %]</p>
<p><b>Definition:</b> [% "definizione" %]</p>
```

### 4. Projekt speichern

1. Projekt (.qgz) im Lizmap-Ordner speichern
2. Relative Pfade für Daten verwenden
3. Überprüfen, dass alle Layer erreichbar sind

## Lizmap-Konfiguration

### Plugin öffnen

1. **Web** → **Lizmap** → **Lizmap**

### Tab Allgemein

| Feld | Beschreibung | Wert |
|------|-------------|------|
| Kartentitel | Angezeigter Name | "Grabung Via Roma" |
| Zusammenfassung | Beschreibung | "Archäologische Dokumentation..." |
| Bild | Projekt-Thumbnail | project_thumb.png |
| Repository | Server-Ordner | /var/www/lizmap/projects |

### Tab Layer

Für jeden Layer konfigurieren:

| Option | Beschreibung |
|--------|-------------|
| Aktiviert | Layer in Lizmap sichtbar |
| Basislayer | Hintergrundlayer (Orthofoto, etc.) |
| Popup | Popup bei Klick aktivieren |
| Bearbeitung | Online-Bearbeitung erlauben |
| Filter | Benutzerfilter |

### Tab Basiskarte

Hintergründe konfigurieren:
- OpenStreetMap
- Google Maps (API-Key erforderlich)
- Bing Maps
- Benutzerdefiniertes Orthofoto

### Tab Suche

Ortssuche:
- Layer für Suche konfigurieren
- Suchfelder
- Anzeigeformat

### Tab Bearbeitung (Optional)

Für Online-Bearbeitung:
1. Bearbeitbare Layer auswählen
2. Bearbeitbare Felder konfigurieren
3. Berechtigungen einstellen

### Tab Werkzeuge

Aktivieren/Deaktivieren:
- Drucken
- Messen
- Auswahl
- Permalink
- etc.

### Konfiguration speichern

**Speichern** klicken um die `.qgs.cfg`-Datei zu generieren

## Veröffentlichung

### Upload auf Server

1. `.qgz` und `.qgz.cfg` Dateien auf Server kopieren
2. Dateiberechtigungen überprüfen
3. QGIS Server konfigurieren

### Server-Struktur

```
/var/www/lizmap/
├── lizmap/           # Lizmap-Anwendung
├── projects/         # QGIS-Projekte
│   ├── grabung_roma.qgz
│   └── grabung_roma.qgz.cfg
└── var/              # Anwendungsdaten
```

### QGIS Server-Konfiguration

Datei `/etc/apache2/sites-available/lizmap.conf`:
```apache
<VirtualHost *:80>
    ServerName lizmap.example.com
    DocumentRoot /var/www/lizmap/lizmap/www

    <Directory /var/www/lizmap/lizmap/www>
        AllowOverride All
        Require all granted
    </Directory>

    # QGIS Server
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride All
        Require all granted
    </Directory>

    FcgidInitialEnv QGIS_SERVER_LOG_FILE /var/log/qgis/qgis_server.log
    FcgidInitialEnv QGIS_SERVER_LOG_LEVEL 0
</VirtualHost>
```

## Web-Zugriff

### Anwendungs-URL

```
http://lizmap.example.com/
```

### Navigation

1. Projektauswahl auf der Startseite
2. Interaktive Kartenansicht
3. Werkzeuge in der Toolbar

### Benutzerfunktionen

| Funktion | Beschreibung |
|----------|-------------|
| Zoom | Mausrad, +/- Schaltflächen |
| Schwenken | Karte ziehen |
| Popup | Klick auf Feature |
| Suche | Suchleiste |
| Drucken | PDF-Export |
| Permalink | Teilbare URL |

## PyArchInit-Integration

### Echtzeit-Daten

Mit PostgreSQL:
- Daten sind immer aktuell
- Änderungen in PyArchInit sofort sichtbar
- Keine manuelle Synchronisation

### Empfohlene Layer

| PyArchInit-Layer | Veröffentlichung |
|------------------|-----------------|
| pyunitastratigrafiche | Ja, mit Popup |
| pyunitastratigrafiche_usm | Ja, mit Popup |
| pyarchinit_quote | Ja |
| pyarchinit_siti | Ja, als Übersicht |
| Harris-Matrix | Als statisches Bild |

### SE-Popup-Konfiguration

Erweitertes HTML-Template:
```html
<div class="se-popup">
    <h3 style="color:#2c3e50;">SE [% "us_s" %]</h3>
    <table>
        <tr><td><b>Fundort:</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Areal:</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Typ:</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Definition:</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Periode:</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Sicherheit

### Authentifizierung

Lizmap unterstützt:
- Lokale Benutzer
- LDAP
- OAuth2

### Benutzerkonfiguration

In Lizmap-Admin:
1. Gruppen erstellen (admin, archaeologe, public)
2. Benutzer erstellen
3. Berechtigungen pro Projekt zuweisen

### Layer-Berechtigungen

| Gruppe | Anzeigen | Bearbeiten | Drucken |
|--------|----------|------------|---------|
| Admin | Alle | Alle | Ja |
| Archäologe | Alle | Einige | Ja |
| Öffentlich | Nur Basis | Nein | Nein |

## Wartung

### Projekte aktualisieren

1. Projekt in QGIS Desktop bearbeiten
2. Lizmap-Konfiguration neu generieren
3. Auf Server hochladen

### Cache

Tile-Cache verwalten:
```bash
# Cache leeren
lizmap-cache-clearer.php -project grabung_roma

# Tiles neu generieren
lizmap-tiles-seeder.php -project grabung_roma -bbox xmin,ymin,xmax,ymax
```

### Log und Debug

```bash
# QGIS Server-Log
tail -f /var/log/qgis/qgis_server.log

# Lizmap-Log
tail -f /var/www/lizmap/var/log/messages.log
```

## Best Practices

### 1. Leistungsoptimierung

- Vorgerenderte Raster-Layer verwenden
- Feature-Anzahl pro Layer begrenzen
- Sichtbarkeitsmaßstäbe konfigurieren
- Räumliche Indizes verwenden

### 2. Benutzererfahrung

- Informative aber prägnante Popups
- Klare und lesbare Stile
- Logische Layer-Organisation
- Benutzerdokumentation

### 3. Sicherheit

- HTTPS obligatorisch
- Regelmäßige Updates
- Konfigurations-Backups
- Zugriffsüberwachung

### 4. Backup

- `.qgz` und `.cfg` Dateien sichern
- PostgreSQL-Datenbank sichern
- Konfigurationen versionieren

## Problemlösung

### Karte wird nicht angezeigt

**Ursachen**:
- QGIS Server nicht konfiguriert
- Falsche Dateipfade
- Unzureichende Berechtigungen

**Lösungen**:
- QGIS Server-Log überprüfen
- Pfade im Projekt kontrollieren
- Dateiberechtigungen überprüfen

### Popups funktionieren nicht

**Ursachen**:
- Layer nicht für Popup konfiguriert
- Fehlerhaftes HTML im Template

**Lösungen**:
- Popup in Lizmap aktivieren
- HTML-Syntax überprüfen

### Langsame Leistung

**Ursachen**:
- Zu viele Daten
- Cache nicht konfiguriert
- Unterdimensionierter Server

**Lösungen**:
- Sichtbare Daten reduzieren
- Tile-Cache konfigurieren
- Server-Ressourcen erhöhen

## Referenzen

### Software
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Dokumentation
- [Lizmap Documentation](https://docs.lizmap.com/)
- [QGIS Server Documentation](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Video-Tutorial

### Lizmap-Setup
`[Platzhalter: video_lizmap_setup.mp4]`

**Inhalte**:
- Plugin-Installation
- Projektkonfiguration
- Veröffentlichung

**Voraussichtliche Dauer**: 20-25 Minuten

### Web-Anpassung
`[Platzhalter: video_lizmap_custom.mp4]`

**Inhalte**:
- Erweiterte Popups
- Benutzerdefinierte Stile
- Benutzerverwaltung

**Voraussichtliche Dauer**: 15-18 Minuten

---

*Letzte Aktualisierung: Januar 2026*
