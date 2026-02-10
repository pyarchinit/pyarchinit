# Tutorial 14: GIS und Kartographie

## Einführung

PyArchInit ist tief in **QGIS** integriert und nutzt dessen vollständige GIS-Funktionalitäten für die räumliche Verwaltung archäologischer Daten. Dieses Tutorial behandelt die kartographische Integration, vordefinierte Layer und erweiterte Funktionen wie die **automatische SAM-Segmentierung**.

### Haupt-GIS-Funktionen

- SE-Visualisierung auf Karte
- Vordefinierte Vektorlayer
- Benutzerdefiniertes QML-Styling
- GIS-Höhen und Messungen
- Automatische Segmentierung (SAM)
- Kartographischer Export

## Vordefinierte PyArchInit-Layer

### Hauptvektorlayer

| Layer | Geometrie | Beschreibung |
|-------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | Ablagerungs-SE |
| `pyunitastratigrafiche_usm` | MultiPolygon | Mauerwerks-SE |
| `pyarchinit_quote` | Point | Höhenpunkte |
| `pyarchinit_siti` | Point | Fundortlokalisierung |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Grabungsareale |
| `pyarchinit_strutture_ipotesi` | Polygon | Hypothetische Strukturen |
| `pyarchinit_documentazione` | Point | Dokumentationsverweise |

### SE-Layer-Attribute

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `gid` | Integer | Eindeutige ID |
| `scavo_s` | Text | Fundortname |
| `area_s` | Text | Arealnummer |
| `us_s` | Text | SE-Nummer |
| `stratigraph_index_us` | Integer | Stratigraphischer Index |
| `tipo_us_s` | Text | SE-Typ |
| `rilievo_originale` | Text | Ursprungsvermessung |
| `disegnatore` | Text | Vermessungsautor |
| `data` | Date | Vermessungsdatum |

## SE-Visualisierung auf Karte

### Vom Tab "Karte" im SE-Formular

1. Ein SE-Formular öffnen
2. Tab **Karte** auswählen
3. Verfügbare Funktionen:

| Schaltfläche | Funktion |
|--------------|----------|
| SE anzeigen | Aktuelle SE auf Karte anzeigen |
| Alle anzeigen | Alle SE des Areals anzeigen |
| Neuer Datensatz | Neue Geometrie erstellen |
| Schwenken zu | Karte auf SE zentrieren |

### Visualisierung aus Suche

1. SE-Suche durchführen
2. Schaltfläche **"Datensatz anzeigen"** → zeigt einzelne an
3. Schaltfläche **"Alle anzeigen"** → zeigt alle Ergebnisse an

## Layer-Styling

### QML-Dateien

PyArchInit enthält vordefinierte Stile im QML-Format:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Stil anwenden

1. Layer in Legende auswählen
2. Rechtsklick → **Eigenschaften**
3. Tab **Stil**
4. **Stil laden** → QML auswählen

### Anpassung

Stile können angepasst werden für:
- Farben nach SE-Typ
- Beschriftungen mit SE-Nummer
- Transparenz
- Rahmen und Füllungen

## Höhen und Messungen

### Höhen-Layer

Der Layer `pyarchinit_quote` speichert:
- X, Y-Koordinaten
- Z-Höhe (absolut)
- Höhenpunkttyp
- Referenz-SE
- Referenzareal

### Automatische Höhenberechnung

Vom SE-Formular werden Min/Max-Höhen berechnet:
1. Abfrage der mit der SE verbundenen Höhenpunkte
2. Extraktion von Minimal- und Maximalwert
3. Anzeige im Bericht

### Höheneingabe

1. Höhen-Layer im Bearbeitungsmodus
2. Punkt auf Karte zeichnen
3. Attribute ausfüllen:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Automatische SAM-Segmentierung

### Was ist SAM?

**SAM (Segment Anything Model)** ist ein von Meta entwickeltes KI-Modell zur automatischen Bildsegmentierung. PyArchInit integriert es für:
- Automatische Digitalisierung von Steinen/Elementen
- Orthofoto-Segmentierung
- Beschleunigung der Vermessung

### Zugriff auf die Funktion

1. **PyArchInit** → **SAM Segmentation**
2. Oder von der Toolbar: **SAM**-Symbol

### SAM-Oberfläche

```
+--------------------------------------------------+
|        SAM Stone Segmentation                     |
+--------------------------------------------------+
| Eingabe:                                          |
|   Raster-Layer: [ComboBox Orthofoto]             |
+--------------------------------------------------+
| Ziel-Layer:                                       |
|   [o] pyunitastratigrafiche                      |
|   [ ] pyunitastratigrafiche_usm                  |
+--------------------------------------------------+
| Standard-Attribute:                               |
|   Fundort (sito): [automatisches Feld]           |
|   Areal: [Areal-Eingabe]                         |
|   Stratigr. Index: [1-10]                        |
|   SE-Typ: [Stein|Schicht|Anhäufung|Einschnitt]   |
+--------------------------------------------------+
| Segmentierungsmodus:                              |
|   [o] Automatisch (alle Steine erkennen)         |
|   [ ] Klick-Modus (jeden Stein anklicken)        |
|   [ ] Box-Modus (Rechteck zeichnen)              |
|   [ ] Polygon-Modus (Freihand zeichnen)          |
|   [ ] Von Layer (bestehendes Polygon nutzen)     |
+--------------------------------------------------+
| Modell:                                           |
|   [ComboBox Modell]                              |
|   API-Key: [******]                              |
+--------------------------------------------------+
|     [Segmentierung starten]  [Abbrechen]          |
+--------------------------------------------------+
```

### Segmentierungsmodi

#### 1. Automatischer Modus
- Segmentiert automatisch alle sichtbaren Objekte
- Ideal für Bereiche mit vielen Steinen
- Erfordert Orthofoto guter Qualität

#### 2. Klick-Modus
- Jedes zu segmentierende Objekt anklicken
- Rechtsklick oder Enter zum Beenden
- Escape zum Abbrechen
- Präziser für bestimmte Objekte

#### 3. Box-Modus
- Rechteck über den Bereich zeichnen
- Segmentiert nur den ausgewählten Bereich
- Nützlich für begrenzte Zonen

#### 4. Polygon-Modus
- Freies Polygon zeichnen
- Klick zum Hinzufügen von Eckpunkten
- Rechtsklick zum Abschließen
- Für unregelmäßige Bereiche

#### 5. Von-Layer-Modus
- Bestehendes Polygon als Maske verwenden
- Polygon-Layer auswählen
- Segmentiert nur innerhalb des Polygons

### Verfügbare Modelle

| Modell | Typ | Anforderungen | Qualität |
|--------|-----|---------------|----------|
| Replicate SAM-2 | Cloud API | API-Key | Ausgezeichnet |
| Roboflow SAM-3 | Cloud API | API-Key | Ausgezeichnet + Text-Prompt |
| SAM vit_b | Lokal | 375MB VRAM | Gut |
| SAM vit_l | Lokal | 1.2GB VRAM | Sehr gut |
| SAM vit_h | Lokal | 2.5GB VRAM | Ausgezeichnet |
| OpenCV | Lokal | Keine | Basis |

### SAM-3 mit Text-Prompt

Die SAM-3-Version (Roboflow) unterstützt **Text-Prompts**:
- "stones" - Steine
- "pottery fragments" - Keramikfragmente
- "bones" - Knochen
- Jede Textbeschreibung

### API-Konfiguration

#### Replicate API (SAM-2)
1. Auf [replicate.com](https://replicate.com) registrieren
2. API-Key erhalten
3. In Konfiguration eingeben

#### Roboflow API (SAM-3)
1. Auf [roboflow.com](https://roboflow.com) registrieren
2. API-Key erhalten
3. In Konfiguration eingeben

### Lokale SAM-Installation

Für lokale Nutzung ohne API:
```bash
# Virtuelle Umgebung erstellen
cd ~/pyarchinit/bin
python -m venv sam_venv

# Umgebung aktivieren
source sam_venv/bin/activate

# Abhängigkeiten installieren
pip install segment-anything torch torchvision

# Modelle herunterladen (optional)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### SAM-Arbeitsablauf

1. **Vorbereitung**
   - Orthofoto als Raster-Layer laden
   - Bezugssystem überprüfen
   - Ziel-Layer vorbereiten

2. **Konfiguration**
   - Eingabe-Raster auswählen
   - Standard-Attribute einstellen
   - Modus und Modell wählen

3. **Ausführung**
   - "Segmentierung starten" klicken
   - Verarbeitung abwarten
   - Ergebnisse überprüfen

4. **Nachbearbeitung**
   - Generierte Polygone kontrollieren
   - SE-Nummern zuweisen
   - Eventuelle Fehler korrigieren

## Kartographische Integration

### GIS-Datenexport

Vom SE-Formular, Tab Karte:
- **GeoPackage exportieren**: Layer als GPKG
- **Shapefile exportieren**: Layer als SHP
- **GeoJSON exportieren**: Layer als JSON

### GIS-Datenimport

Bestehende Geometrien importieren:
1. Layer in QGIS laden
2. Feature auswählen
3. Import-Funktion verwenden

### Geoprocessing

Verfügbare räumliche Operationen:
- Puffer
- Verschneidung
- Union
- Differenz
- Zentroide

## Best Practices

### 1. Orthofotos

- Minimale Auflösung: 1-2 cm/Pixel
- Format: Georeferenziertes GeoTIFF
- Bezugssystem: Konsistent mit Projekt

### 2. Digitalisierung

- Snap für Präzision verwenden
- Topologie überprüfen
- Attributkonsistenz beibehalten

### 3. SAM-Segmentierung

- Orthofoto hoher Qualität
- Gleichmäßige Beleuchtung
- Angemessener Kontrast Objekte/Hintergrund
- Nachprüfung immer erforderlich

### 4. Layer-Organisation

- Nach Typologie gruppieren
- Konsistente Stile verwenden
- Ordnung in Legende beibehalten

## Problemlösung

### Layer nicht angezeigt

**Mögliche Ursachen**:
- Falsche Ausdehnung
- Verschiedenes Bezugssystem
- Aktiver Filter

**Lösungen**:
- Auf Layer zoomen
- KBS überprüfen
- Filter entfernen

### SAM funktioniert nicht

**Mögliche Ursachen**:
- API-Key ungültig
- Raster nicht georeferenziert
- Lokales Modell nicht installiert

**Lösungen**:
- API-Key überprüfen
- Georeferenzierung kontrollieren
- Modell installieren

### Fehlerhafte Geometrien

**Mögliche Ursachen**:
- Digitalisierungsfehler
- Problematischer Import

**Lösungen**:
- "Fix Geometries" verwenden
- Element neu zeichnen

## Referenzen

### Quelldateien
- `modules/gis/pyarchinit_pyqgis.py` - GIS-Integration
- `tabs/Sam_Segmentation_Dialog.py` - SAM-Dialog
- `modules/gis/sam_map_tools.py` - SAM-Kartenwerkzeuge

### Layer
- `pyunitastratigrafiche` - Ablagerungs-SE
- `pyunitastratigrafiche_usm` - Mauerwerks-SE
- `pyarchinit_quote` - Höhen

---

## Video-Tutorial

### GIS-Integration
`[Platzhalter: video_gis_integration.mp4]`

**Inhalte**:
- Vordefinierte Layer
- SE-Visualisierung
- Styling und Beschriftungen
- Kartographischer Export

**Voraussichtliche Dauer**: 15-18 Minuten

### SAM-Segmentierung
`[Platzhalter: video_sam_segmentation.mp4]`

**Inhalte**:
- SAM-Konfiguration
- Segmentierungsmodi
- Nachbearbeitung
- Best Practices

**Voraussichtliche Dauer**: 12-15 Minuten

---

*Letzte Aktualisierung: Januar 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../animations/pyarchinit_image_classification_animation.html)
