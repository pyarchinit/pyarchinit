# Tutorial 22: Medien-Manager

## Einführung

Der **Medien-Manager** ist das zentrale PyArchInit-Werkzeug zur Verwaltung von Bildern und Multimedia-Inhalten, die mit archäologischen Datensätzen verknüpft sind. Er ermöglicht die Verknüpfung von Fotos, Zeichnungen, Videos und anderen Medien mit SE, Funden, Gräbern, Strukturen und anderen Entitäten.

### Hauptfunktionen

- Zentrale Verwaltung aller Medien
- Verknüpfung mit archäologischen Entitäten (SE, Funde, Keramik, Gräber, Strukturen, UT)
- Thumbnail- und Originalbildansicht
- Tagging und Kategorisierung
- Erweiterte Suche
- GPT-Integration für Bildanalyse

## Zugriff

### Über Menü
**PyArchInit** → **Media Manager**

### Über Toolbar
Symbol **Media Manager** in der PyArchInit-Toolbar

## Oberfläche

### Hauptpanel

```
+----------------------------------------------------------+
|                    Media Manager                          |
+----------------------------------------------------------+
| Fundort: [ComboBox]  Areal: [ComboBox]  SE: [ComboBox]   |
+----------------------------------------------------------+
| [Thumbnail-Raster]                                        |
|  +------+  +------+  +------+  +------+                  |
|  | Bild1|  | Bild2|  | Bild3|  | Bild4|                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | Bild5|  | Bild6|  | Bild7|  | Bild8|                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Tags: [Liste zugeordneter Tags]                           |
+----------------------------------------------------------+
| [Navigation] << < Datensatz X von Y > >>                  |
+----------------------------------------------------------+
```

### Suchfilter

| Feld | Beschreibung |
|------|-------------|
| Fundort | Nach Fundort filtern |
| Areal | Nach Ausgrabungsareal filtern |
| SE | Nach Stratigraphischer Einheit filtern |
| Strukturkürzel | Nach Strukturkürzel filtern |
| Nr. Struktur | Nach Strukturnummer filtern |

### Thumbnail-Steuerung

| Steuerung | Funktion |
|-----------|----------|
| Größenregler | Thumbnail-Größe anpassen |
| Doppelklick | Bild in Originalgröße öffnen |
| Mehrfachauswahl | Strg+Klick für mehrere Bilder |

## Medienverwaltung

### Neue Bilder hinzufügen

1. Medien-Manager öffnen
2. Ziel-Fundort auswählen
3. Auf **"Neuer Datensatz"** klicken oder Kontextmenü verwenden
4. Bilder zum Hinzufügen auswählen
5. Metadaten ausfüllen

### Medien mit Entitäten verknüpfen

1. Bild im Raster auswählen
2. Im Tags-Panel auswählen:
   - **Entitätstyp**: SE, Fund, Keramik, Grab, Struktur, UT
   - **Kennung**: Nummer/Code der Entität
3. Auf **"Verknüpfen"** klicken

### Unterstützte Entitätstypen

| Typ | DB-Tabelle | Beschreibung |
|-----|------------|-------------|
| SE | us_table | Stratigraphische Einheiten |
| FUND | inventario_materiali_table | Funde/Materialien |
| KERAMIK | pottery_table | Keramik |
| GRAB | tomba_table | Bestattungen |
| STRUKTUR | struttura_table | Strukturen |
| UT | ut_table | Topographische Einheiten |

### Originalbild anzeigen

- **Doppelklick** auf Thumbnail
- Viewer öffnet sich mit:
  - Zoom (Mausrad)
  - Schwenken (Ziehen)
  - Rotation
  - Messung

## Erweiterte Funktionen

### Erweiterte Suche

Der Medien-Manager unterstützt Suche nach:
- Dateiname
- Einfügedatum
- Verknüpfte Entität
- Tags/Kategorien

### GPT-Integration

Schaltfläche **"GPT Sketch"** für:
- Automatische Bildanalyse
- Beschreibungsgenerierung
- Klassifikationsvorschläge

### Remote-Upload

Unterstützung für Bilder auf Remote-Servern:
- Direkte URLs
- FTP-Server
- Cloud-Speicher

## Datenbank

### Beteiligte Tabellen

| Tabelle | Beschreibung |
|---------|-------------|
| `media_table` | Medien-Metadaten |
| `media_thumb_table` | Thumbnails |
| `media_to_entity_table` | Entitätsverknüpfungen |

### Mapper-Klassen

- `MEDIA` - Haupt-Medien-Entität
- `MEDIA_THUMB` - Thumbnail
- `MEDIATOENTITY` - Medien-Entitäts-Beziehung

## Best Practices

### 1. Dateiorganisation

- Beschreibende Dateinamen verwenden
- Nach Fundort/Areal/Jahr organisieren
- Original-Backups aufbewahren

### 2. Metadaten

- Immer Fundort und Areal ausfüllen
- Aussagekräftige Beschreibungen hinzufügen
- Konsistente Tags verwenden

### 3. Bildqualität

- Empfohlene Mindestauflösung: 1920x1080
- Format: JPG für Fotos, PNG für Zeichnungen
- Moderate Kompression

### 4. Verknüpfungen

- Jedes Bild mit relevanten Entitäten verknüpfen
- Verknüpfungen nach Massenimport überprüfen
- Suche für nicht verknüpfte Bilder verwenden

## Fehlerbehebung

### Thumbnails nicht angezeigt

**Ursachen**:
- Falscher Bildpfad
- Fehlende Datei
- Berechtigungsprobleme

**Lösungen**:
- Pfad in Datenbank überprüfen
- Dateiexistenz kontrollieren
- Ordnerberechtigungen überprüfen

### Bild nicht verknüpfbar

**Ursachen**:
- Entität existiert nicht
- Falscher Entitätstyp

**Lösungen**:
- Datensatzexistenz überprüfen
- Ausgewählten Entitätstyp kontrollieren

## Referenzen

### Quelldateien
- `tabs/Image_viewer.py` - Hauptoberfläche
- `modules/utility/pyarchinit_media_utility.py` - Medien-Utilities

### Datenbank
- `media_table` - Mediendaten
- `media_to_entity_table` - Verknüpfungen

---

## Video-Tutorial

### Vollständiger Medien-Manager
`[Platzhalter: video_media_manager.mp4]`

**Inhalte**:
- Bilder hinzufügen
- Mit Entitäten verknüpfen
- Suche und Filter
- Erweiterte Funktionen

**Voraussichtliche Dauer**: 15-18 Minuten

---

*Letzte Aktualisierung: Januar 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../animations/pyarchinit_media_manager_animation.html)
