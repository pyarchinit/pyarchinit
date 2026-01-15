# Tutorial 11: Harris-Matrix

## Einführung

Die **Harris-Matrix** (oder stratigraphisches Diagramm) ist ein grundlegendes Werkzeug in der Archäologie zur grafischen Darstellung der stratigraphischen Beziehungen zwischen den verschiedenen Stratigraphischen Einheiten (SE). PyArchInit generiert die Harris-Matrix automatisch aus den in den SE-Formularen eingegebenen stratigraphischen Beziehungen.

### Was ist die Harris-Matrix?

Die Harris-Matrix ist ein Diagramm, das darstellt:
- Die **zeitliche Abfolge** der SE (von der jüngsten oben bis zur ältesten unten)
- Die **physischen Beziehungen** zwischen den SE (überdeckt/überdeckt von, schneidet/geschnitten von, bindet sich an)
- Die **Periodisierung** der Ausgrabung (Gruppierung nach Perioden und Phasen)

### Dargestellte Beziehungstypen

| Beziehung | Bedeutung | Darstellung |
|-----------|-----------|-------------|
| Liegt über/Liegt unter | Physische Überlagerung | Durchgezogene Linie nach unten |
| Schneidet/Geschnitten von | Negative Aktion (Grenzfläche) | Gestrichelte Linie |
| Bindet sich an/Gleich wie | Gleichzeitigkeit | Horizontale bidirektionale Linie |
| Verfüllt/Verfüllt von | Füllung eines Einschnitts | Durchgezogene Linie |
| Lehnt sich an/Angelehnt von | Strukturelle Anlehnung | Durchgezogene Linie |

## Zugriff auf die Funktion

### Vom Hauptmenü
1. **PyArchInit** in der Menüleiste
2. **Harris-Matrix** auswählen

### Vom SE-Formular
1. SE-Formular öffnen
2. Tab **Karte**
3. Schaltfläche **"Matrix exportieren"** oder **"Matrix anzeigen"**

### Voraussetzungen
- Datenbank korrekt verbunden
- SE mit ausgefüllten stratigraphischen Beziehungen
- Periodisierung definiert (optional, aber empfohlen)
- Graphviz im System installiert

## Matrix-Konfiguration

### Einstellungsfenster (Setting_Matrix)

Vor der Generierung erscheint ein Konfigurationsfenster:

#### Tab Allgemein

| Feld | Beschreibung | Empfohlener Wert |
|------|-------------|------------------|
| DPI | Bildauflösung | 150-300 |
| Perioden anzeigen | SE nach Periode/Phase gruppieren | Ja |
| Legende anzeigen | Legende im Diagramm einschließen | Ja |

#### Tab Knoten "Ante/Post" (Normale Beziehungen)

| Parameter | Beschreibung | Optionen |
|-----------|-------------|----------|
| Knotenform | Geometrische Form | box, ellipse, diamond |
| Füllfarbe | Innenfarbe | white, lightblue, usw. |
| Stil | Rahmenaussehen | solid, dashed |
| Linienstärke | Rahmenbreite | 0.5 - 2.0 |
| Pfeiltyp | Pfeilspitze | normal, diamond, none |
| Pfeilgröße | Spitzengröße | 0.5 - 1.5 |

#### Tab Knoten "Negativ" (Einschnitte)

| Parameter | Beschreibung | Optionen |
|-----------|-------------|----------|
| Knotenform | Geometrische Form | box, ellipse, diamond |
| Füllfarbe | Unterscheidende Farbe | gray, lightcoral |
| Linienstil | Verbindungsaussehen | dashed (gestrichelt) |

#### Tab Knoten "Gleichzeitig"

| Parameter | Beschreibung | Optionen |
|-----------|-------------|----------|
| Knotenform | Geometrische Form | box, ellipse |
| Füllfarbe | Unterscheidende Farbe | lightyellow, white |
| Linienstil | Verbindungsaussehen | solid |
| Pfeil | Verbindungstyp | none (bidirektional) |

#### Tab Spezielle Verbindungen (">", ">>")

Für spezielle stratigraphische Beziehungen oder dokumentarische Verbindungen:

| Parameter | Beschreibung |
|-----------|-------------|
| Form | box, ellipse |
| Farbe | lightgreen, usw. |
| Stil | solid, dashed |

## Exporttypen

### 1. Standard-Matrix-Export

Generiert die Basis-Matrix mit:
- Alle stratigraphischen Beziehungen
- Gruppierung nach Periode/Phase
- Vertikales Layout (TB - Top to Bottom)

**Ausgabe**: `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Matrix 2ED-Export (Erweitert)

Erweiterte Version mit:
- Zusätzliche Informationen in den Knoten (SE + Definition + Datierung)
- Spezielle Verbindungen (>, >>)
- Export auch im GraphML-Format

**Ausgabe**: `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. Matrix anzeigen (Schnellansicht)

Für schnelle Visualisierung ohne Konfigurationsoptionen:
- Verwendet Standardeinstellungen
- Schnellere Generierung
- Ideal für schnelle Kontrollen

## Generierungsprozess

### Schritt 1: Datensammlung

Das System sammelt automatisch:
```
Für jede SE im ausgewählten Fundort/Areal:
  - SE-Nummer
  - Einheitstyp (SE/USM)
  - Stratigraphische Beziehungen
  - Anfangsperiode und -phase
  - Interpretative Definition
```

### Schritt 2: Graph-Konstruktion

Erstellung der Beziehungen:
```
Sequenz (Ante/Post):
  SE1 -> SE2 (SE1 überdeckt SE2)

Negativ (Einschnitte):
  SE3 -> SE4 (SE3 schneidet SE4)

Gleichzeitig:
  SE5 <-> SE6 (SE5 bindet sich an SE6)
```

### Schritt 3: Clustering nach Perioden

Hierarchische Gruppierung:
```
Fundort
  └── Areal
      └── Periode 1 : Phase 1 : "Römische Zeit"
          ├── SE101
          ├── SE102
          └── SE103
      └── Periode 1 : Phase 2 : "Spätantike"
          ├── SE201
          └── SE202
```

### Schritt 4: Transitive Reduktion (tred)

Der `tred`-Befehl von Graphviz entfernt redundante Beziehungen:
- Wenn SE1 -> SE2 und SE2 -> SE3, entfernt SE1 -> SE3
- Vereinfacht das Diagramm
- Behält nur direkte Beziehungen bei

### Schritt 5: Finale Darstellung

Bildgenerierung mit mehreren Formaten:
- DOT (Graphviz-Quelle)
- JPG (komprimiertes Bild)
- PNG (verlustfreies Bild)

## Interpretation der Matrix

### Vertikale Lesung

```
     [Jüngste SE]
           ↓
        SE 001
           ↓
        SE 002
           ↓
        SE 003
           ↓
     [Älteste SE]
```

### Cluster-Lesung

Die farbigen Boxen repräsentieren Perioden/Phasen:
- **Hellblau**: Perioden-Cluster
- **Gelb**: Phasen-Cluster
- **Grau**: Fundort-Hintergrund

### Verbindungstypen

```
─────────→  Durchgezogene Linie = Überdeckt/Verfüllt/Lehnt sich an
- - - - →  Gestrichelte Linie = Schneidet
←────────→  Bidirektional = Gleichzeitig/Gleich wie
```

### Knotenfarben

| Farbe | Typische Bedeutung |
|-------|-------------------|
| Weiß | Normale Ablagerungs-SE |
| Grau | Negative SE (Einschnitt) |
| Gelb | Gleichzeitige SE |
| Hellblau | SE mit speziellen Beziehungen |

## Problemlösung

### Fehler: "Loop Detected"

**Ursache**: Es existieren Zyklen in den Beziehungen (A überdeckt B, B überdeckt A)

**Lösung**:
1. SE-Formular öffnen
2. Die Beziehungen der angegebenen SE überprüfen
3. Die zirkulären Beziehungen korrigieren
4. Matrix neu generieren

### Fehler: "tred command not found"

**Ursache**: Graphviz nicht installiert

**Lösung**:
- **Windows**: Graphviz von graphviz.org installieren
- **macOS**: `brew install graphviz`
- **Linux**: `sudo apt install graphviz`

### Matrix nicht generiert

**Mögliche Ursachen**:
1. Keine stratigraphischen Beziehungen eingegeben
2. SE ohne zugewiesene Periode/Phase
3. Berechtigungsprobleme im Ausgabeordner

**Überprüfung**:
1. Prüfen, dass die SE Beziehungen haben
2. Periodisierung überprüfen
3. Berechtigungen von `pyarchinit_Matrix_folder` prüfen

### Matrix zu groß

**Problem**: Unlesbares Bild bei vielen SE

**Lösungen**:
1. DPI reduzieren (100-150)
2. Nach spezifischem Areal filtern
3. Matrix-Anzeige für einzelne Areale verwenden
4. In Vektorformat (DOT) exportieren und mit yEd öffnen

### SE nicht nach Periode gruppiert

**Ursache**: Periodisierung fehlt oder nicht aktiviert

**Lösung**:
1. Periodisierungsformular ausfüllen
2. Den SE Anfangsperiode/-phase zuweisen
3. "Perioden anzeigen" in den Einstellungen aktivieren

## Ausgabe und generierte Dateien

### Ausgabeordner

```
~/pyarchinit/pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Graphviz-Quelle
├── Harris_matrix_tred.dot      # Nach transitiver Reduktion
├── Harris_matrix_tred.dot.jpg  # Finales JPG-Bild
├── Harris_matrix_tred.dot.png  # Finales PNG-Bild
├── Harris_matrix2ED.dot        # Erweiterte Version
├── Harris_matrix2ED_graphml.dot # Für GraphML-Export
└── matrix_error.txt            # Fehlerprotokoll
```

### Dateiverwendung

| Datei | Verwendung |
|-------|-----------|
| *.jpg/*.png | Einfügung in Berichte |
| *.dot | Bearbeitung mit Graphviz-Editor |
| _graphml.dot | Import in yEd für erweiterte Bearbeitung |

## Best Practices

### 1. Vor der Generierung

- Vollständigkeit der stratigraphischen Beziehungen überprüfen
- Abwesenheit von Zyklen kontrollieren
- Allen SE Periode/Phase zuweisen
- Interpretative Definition ausfüllen

### 2. Während der SE-Erfassung

- Korrekte bidirektionale Beziehungen eingeben
- Konsistente Terminologie verwenden
- Korrektes Areal in den Beziehungen überprüfen

### 3. Ausgabeoptimierung

- Für Druck: DPI 300
- Für Bildschirm: DPI 150
- Für komplexe Grabungen: nach Arealen aufteilen

### 4. Qualitätskontrolle

- Matrix mit Grabungsdokumentation vergleichen
- Logische Sequenzen überprüfen
- Gruppierungen nach Periode kontrollieren

## Vollständiger Arbeitsablauf

### 1. Datenvorbereitung

```
1. SE-Formulare mit allen Beziehungen vervollständigen
2. Periodisierungsformular ausfüllen
3. Den SE Periode/Phase zuweisen
4. Datenkonsistenz überprüfen
```

### 2. Matrix-Generierung

```
1. Menü PyArchInit → Harris-Matrix
2. Einstellungen konfigurieren (DPI, Farben)
3. Cluster für Perioden aktivieren
4. Matrix generieren
```

### 3. Überprüfung und Korrektur

```
1. Generierte Matrix kontrollieren
2. Eventuelle Fehler identifizieren
3. Beziehungen in SE-Formularen korrigieren
4. Bei Bedarf neu generieren
```

### 4. Finale Verwendung

```
1. In Grabungsbericht einfügen
2. Für Publikation exportieren
3. Mit Dokumentation archivieren
```

## Integration mit anderen Werkzeugen

### Export für yEd

Die Datei `_graphml.dot` kann in yEd geöffnet werden für:
- Manuelles Layout-Editing
- Hinzufügen von Anmerkungen
- Export in verschiedene Formate

### Export für s3egraph

PyArchInit unterstützt den Export für das s3egraph-System:
- Kompatibles Format
- Behält stratigraphische Beziehungen bei
- Unterstützung für 3D-Visualisierung

## Referenzen

### Quelldateien
- `tabs/Interactive_matrix.py` - Interaktive Oberfläche
- `modules/utility/pyarchinit_matrix_exp.py` - Klassen HarrisMatrix und ViewHarrisMatrix

### Datenbank
- `us_table` - SE-Daten und Beziehungen
- `periodizzazione_table` - Perioden und Phasen

### Abhängigkeiten
- Graphviz (dot, tred)
- Python graphviz-Bibliothek

---

## Video-Tutorial

### Harris-Matrix - Vollständige Generierung
`[Platzhalter: video_harris_matrix.mp4]`

**Inhalte**:
- Einstellungen konfigurieren
- Matrix generieren
- Ergebnisse interpretieren
- Häufige Probleme lösen

**Voraussichtliche Dauer**: 15-20 Minuten

### Harris-Matrix - Erweiterte Bearbeitung mit yEd
`[Platzhalter: video_matrix_yed.mp4]`

**Inhalte**:
- Export für yEd
- Layout bearbeiten
- Anmerkungen hinzufügen
- Re-Export

**Voraussichtliche Dauer**: 10-12 Minuten

---

*Letzte Aktualisierung: Januar 2026*
