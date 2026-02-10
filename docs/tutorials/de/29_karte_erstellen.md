# Tutorial 29: Karte erstellen

## Einführung

**Karte erstellen** ist die PyArchInit-Funktion zur Erstellung professioneller Karten und Drucklayouts direkt aus der aktuellen QGIS-Ansicht. Sie verwendet vordefinierte Layout-Templates zur Erstellung standardisierter kartographischer Ausgaben.

### Funktionen

- Schnelle Kartenerstellung aus aktueller Ansicht
- Vordefinierte Templates für verschiedene Formate
- Anpassung von Kopfzeilen und Legenden
- Export in PDF, PNG, SVG

## Zugriff

### Über Toolbar
Symbol **"Make your Map"** (Drucker) in der PyArchInit-Toolbar

### Über Menü
**PyArchInit** → **Make your Map**

## Grundlegende Verwendung

### Schnelle Erstellung

1. Gewünschte Kartenansicht in QGIS konfigurieren
2. Korrekten Zoom und Ausschnitt einstellen
3. Auf **"Make your Map"** klicken
4. Gewünschtes Template auswählen
5. Titel und Informationen eingeben
6. Karte generieren

## Verfügbare Templates

### Standardformate

| Template | Format | Ausrichtung | Verwendung |
|----------|--------|-------------|------------|
| A4 Hochformat | A4 | Vertikal | Standarddokumentation |
| A4 Querformat | A4 | Horizontal | Erweiterte Ansichten |
| A3 Hochformat | A3 | Vertikal | Detaillierte Tafeln |
| A3 Querformat | A3 | Horizontal | Planimetrische Pläne |

### Template-Elemente

Jedes Template enthält:
- **Kartenbereich** - Hauptansicht
- **Kopfzeile** - Titel und Projektinformationen
- **Maßstab** - Grafischer Maßstabsbalken
- **Nordpfeil** - Nordrichtungsanzeige
- **Legende** - Layer-Symbole
- **Schriftfeld** - Technische Informationen

## Anpassung

### Einfügbare Informationen

| Feld | Beschreibung |
|------|-------------|
| Titel | Name der Karte |
| Untertitel | Zusätzliche Beschreibung |
| Fundort | Name des Fundorts |
| Areal | Arealnummer |
| Datum | Erstellungsdatum |
| Autor | Autorenname |
| Maßstab | Darstellungsmaßstab |

### Kartenstil

Vor der Generierung:
1. Layer-Stile in QGIS konfigurieren
2. Gewünschte Layer aktivieren/deaktivieren
3. Beschriftungen einrichten
4. Legende überprüfen

## Export

### Verfügbare Formate

| Format | Verwendung | Qualität |
|--------|------------|----------|
| PDF | Druck, Archiv | Vektoriell |
| PNG | Web, Präsentationen | Raster |
| SVG | Bearbeitung, Veröffentlichung | Vektoriell |
| JPG | Web, Vorschau | Komprimiertes Raster |

### Auflösung

| DPI | Verwendung |
|-----|------------|
| 96 | Bildschirm/Vorschau |
| 150 | Web-Veröffentlichung |
| 300 | Standarddruck |
| 600 | Hochwertiger Druck |

## Integration mit Time Manager

### Sequenzgenerierung

In Kombination mit Time Manager:
1. Time Manager konfigurieren
2. Für jede stratigraphische Schicht:
   - Schicht einstellen
   - Karte generieren
   - Mit fortlaufendem Namen speichern

### Animationsausgabe

Kartenserie für:
- Präsentationen
- Zeitraffer-Video
- Progressive Dokumentation

## Typischer Arbeitsablauf

### 1. Vorbereitung

```
1. Benötigte Layer laden
2. Passende Stile konfigurieren
3. Bezugssystem einstellen
4. Kartenausschnitt definieren
```

### 2. Ansichtskonfiguration

```
1. Auf Interessenbereich zoomen
2. Layer aktivieren/deaktivieren
3. Beschriftungen überprüfen
4. Legende kontrollieren
```

### 3. Generierung

```
1. Make your Map klicken
2. Template auswählen
3. Informationen ausfüllen
4. Exportformat wählen
5. Speichern
```

## Best Practices

### 1. Vor der Generierung

- Datenvollständigkeit überprüfen
- Layer-Stile kontrollieren
- Passenden Maßstab einstellen

### 2. Templates

- Konsistente Templates im Projekt verwenden
- Kopfzeilen für Institution anpassen
- Kartographische Standards einhalten

### 3. Ausgabe

- In hoher Auflösung für Druck speichern
- PDF-Kopie für Archiv aufbewahren
- Beschreibende Benennung verwenden

## Template-Anpassung

### Template modifizieren

QGIS-Templates können modifiziert werden:
1. Layout-Manager in QGIS öffnen
2. Bestehendes Template bearbeiten
3. Als neues Template speichern
4. Verfügbar in Make your Map

### Template erstellen

1. Neues Layout in QGIS erstellen
2. Benötigte Elemente hinzufügen
3. Variablen für dynamische Felder konfigurieren
4. Im Templates-Ordner speichern

## Fehlerbehebung

### Leere Karte

**Ursachen**:
- Kein aktiver Layer
- Falscher Ausschnitt

**Lösungen**:
- Sichtbare Layer aktivieren
- Auf Bereich mit Daten zoomen

### Unvollständige Legende

**Ursache**: Layer nicht korrekt konfiguriert

**Lösung**: Layer-Eigenschaften in QGIS überprüfen

### Export fehlgeschlagen

**Ursachen**:
- Nicht beschreibbarer Pfad
- Format nicht unterstützt

**Lösungen**:
- Ordnerberechtigungen überprüfen
- Anderes Format wählen

## Referenzen

### Quelldateien
- `pyarchinitPlugin.py` - Funktion runPrint
- Templates im Ordner `resources/templates/`

### QGIS
- Layout-Manager
- Print Composer

---

## Video-Tutorial

### Karte erstellen
`[Platzhalter: video_karte_erstellen.mp4]`

**Inhalte**:
- Ansichtsvorbereitung
- Template-Verwendung
- Anpassung
- Format-Export

**Voraussichtliche Dauer**: 10-12 Minuten

---

*Letzte Aktualisierung: Januar 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../animations/pyarchinit_create_map_animation.html)
