# Tutorial 26: Keramik-Werkzeuge

## Einführung

**Keramik-Werkzeuge** ist ein fortgeschrittenes Modul zur Verarbeitung von Keramikbildern. Es bietet Werkzeuge zum Extrahieren von Bildern aus PDFs, Generieren von Tafellayouts, Verarbeiten von Zeichnungen mit KI (PotteryInk) und weitere spezialisierte Funktionen für die Keramikdokumentation.

### Hauptfunktionen

- Bildextraktion aus PDF
- Generierung von Keramiktafel-Layouts
- Bildverarbeitung mit KI
- Zeichnungsformatkonvertierung
- Integration mit Keramik-Formular

## Zugriff

### Über Menü
**PyArchInit** → **Pottery Tools**

## Oberfläche

### Hauptpanel

```
+--------------------------------------------------+
|              Keramik-Werkzeuge                    |
+--------------------------------------------------+
| [Tab: PDF-Extraktion]                            |
| [Tab: Layout-Generator]                          |
| [Tab: Bildverarbeitung]                          |
| [Tab: PotteryInk KI]                             |
+--------------------------------------------------+
| [Fortschrittsbalken]                             |
| [Log-Meldungen]                                  |
+--------------------------------------------------+
```

## Tab PDF-Extraktion

### Funktion

Extrahiert automatisch Bilder aus PDF-Dokumenten mit Keramiktafeln.

### Verwendung

1. Quell-PDF-Datei auswählen
2. Zielordner angeben
3. Auf **"Extrahieren"** klicken
4. Bilder werden als separate Dateien gespeichert

### Optionen

| Option | Beschreibung |
|--------|-------------|
| DPI | Extraktionsauflösung (150-600) |
| Format | PNG, JPG, TIFF |
| Seiten | Alle oder spezifischer Bereich |

## Tab Layout-Generator

### Funktion

Generiert automatisch Keramiktafeln mit standardisiertem Layout.

### Layout-Typen

| Layout | Beschreibung |
|--------|-------------|
| Raster | Bilder in regelmäßigem Raster |
| Sequenz | Bilder in nummerierter Reihenfolge |
| Vergleich | Layout für Vergleiche |
| Katalog | Katalogformat mit Bildunterschriften |

### Verwendung

1. Einzuschließende Bilder auswählen
2. Layout-Typ wählen
3. Parameter konfigurieren (Maße, Ränder)
4. Tafel generieren

### Layout-Parameter

| Parameter | Beschreibung |
|-----------|-------------|
| Seitengröße | A4, A3, Benutzerdefiniert |
| Ausrichtung | Hochformat, Querformat |
| Ränder | Randabstände |
| Abstände | Abstand zwischen Bildern |
| Bildunterschriften | Text unter Bildern |

## Tab Bildverarbeitung

### Funktion

Stapelverarbeitung von Keramikbildern.

### Verfügbare Operationen

| Operation | Beschreibung |
|-----------|-------------|
| Skalieren | Bilder skalieren |
| Zuschneiden | Automatisches/manuelles Zuschneiden |
| Drehen | Gradrotation |
| Konvertieren | Formatwechsel |
| Optimieren | Qualitätskompression |

### Stapelverarbeitung

1. Quellordner auswählen
2. Anzuwendende Operationen wählen
3. Ziel angeben
4. Verarbeitung ausführen

## Tab PotteryInk KI

### Funktion

Verwendet künstliche Intelligenz für:
- Umwandlung Foto → Technische Zeichnung
- Erkennung von Keramikformen
- Klassifikationsvorschläge
- Automatische Vermessung

### Voraussetzungen

- Konfigurierte Python-Umgebung
- Heruntergeladene KI-Modelle (YOLO, etc.)
- GPU empfohlen (aber nicht zwingend)

### Verwendung

1. Keramikbild laden
2. Verarbeitungstyp auswählen
3. KI-Verarbeitung abwarten
4. Ergebnis überprüfen und speichern

### KI-Verarbeitungstypen

| Typ | Beschreibung |
|-----|-------------|
| Tuschen-Konvertierung | Konvertiert Foto in technische Zeichnung |
| Formerkennung | Erkennt Gefäßform |
| Profilextraktion | Extrahiert Keramikprofil |
| Dekorationsanalyse | Analysiert Verzierungen |

## Virtuelle Umgebung

### Automatische Einrichtung

Beim ersten Start erstellen die Keramik-Werkzeuge:
1. Virtuelle Umgebung in `~/pyarchinit/bin/pottery_venv/`
2. Installation notwendiger Abhängigkeiten
3. Download der KI-Modelle (falls angefordert)

### Abhängigkeiten

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Installation überprüfen

Das Log zeigt den Status:
```
✓ Virtuelle Umgebung erstellt
✓ Abhängigkeiten installiert
✓ Modelle heruntergeladen
✓ Keramik-Werkzeuge erfolgreich initialisiert!
```

## Datenbankintegration

### Verknüpfung mit Keramik-Formular

Verarbeitete Bilder können:
- Automatisch mit Keramik-Datensätzen verknüpft werden
- Mit entsprechenden Metadaten gespeichert werden
- Nach Fundort/Inventar organisiert werden

## Best Practices

### 1. Eingabebildqualität

- Mindestauflösung: 300 DPI
- Gleichmäßige Beleuchtung
- Neutraler Hintergrund (weiß/grau)
- Sichtbarer Maßstab

### 2. KI-Verarbeitung

- KI-Ergebnisse immer überprüfen
- Bei Bedarf manuell korrigieren
- Originale und Verarbeitete speichern

### 3. Ausgabeorganisation

- Konsistente Benennung verwenden
- Nach Fundort/Kampagne organisieren
- Rückverfolgbarkeit gewährleisten

## Fehlerbehebung

### Virtuelle Umgebung nicht erstellt

**Ursachen**:
- Python nicht gefunden
- Unzureichende Berechtigungen

**Lösungen**:
- Python-Installation überprüfen
- Ordnerberechtigungen kontrollieren

### KI-Verarbeitung langsam

**Ursachen**:
- Keine GPU verfügbar
- Zu große Bilder

**Lösungen**:
- Bildgröße reduzieren
- CPU verwenden (langsamer aber funktioniert)

### PDF-Extraktion fehlgeschlagen

**Ursachen**:
- Geschütztes PDF
- Format nicht unterstützt

**Lösungen**:
- PDF-Schutz überprüfen
- Mit anderer PDF-Software versuchen

## Referenzen

### Quelldateien
- `tabs/Pottery_tools.py` - Hauptoberfläche
- `modules/utility/pottery_utilities.py` - Verarbeitungs-Utilities
- `gui/ui/Pottery_tools.ui` - UI-Layout

### Ordner
- `~/pyarchinit/bin/pottery_venv/` - Virtuelle Umgebung
- `~/pyarchinit/models/` - KI-Modelle

---

## Video-Tutorial

### Vollständige Keramik-Werkzeuge
`[Platzhalter: video_keramik_werkzeuge.mp4]`

**Inhalte**:
- Extraktion aus PDF
- Layout-Generierung
- KI-Verarbeitung
- Datenbankintegration

**Voraussichtliche Dauer**: 20-25 Minuten

---

*Letzte Aktualisierung: Januar 2026*
