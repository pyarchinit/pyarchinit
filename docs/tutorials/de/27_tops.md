# Tutorial 27: TOPS - Total Open Station

## Einführung

**TOPS** (Total Open Station) ist die PyArchInit-Integration mit der Open-Source-Software zum Herunterladen und Konvertieren von Daten aus Totalstationen. Sie ermöglicht den direkten Import von topographischen Vermessungen in das PyArchInit-System.

### Was ist Total Open Station?

Total Open Station ist eine freie Software für:
- Daten-Download von Totalstationen
- Formatkonvertierung
- Export in GIS-kompatible Formate

PyArchInit integriert TOPS zur Vereinfachung des Imports von Grabungsdaten.

## Zugriff

### Über Menü
**PyArchInit** → **TOPS (Total Open Station)**

## Oberfläche

### Hauptpanel

```
+--------------------------------------------------+
|         Total Open Station zu PyArchInit          |
+--------------------------------------------------+
| Eingabe:                                          |
|   Datei: [___________________] [Durchsuchen]     |
|   Eingabeformat: [ComboBox Formate]              |
+--------------------------------------------------+
| Ausgabe:                                          |
|   Datei: [___________________] [Durchsuchen]     |
|   Ausgabeformat: [csv | dxf | ...]               |
+--------------------------------------------------+
| [ ] Koordinaten konvertieren                     |
+--------------------------------------------------+
| [Datenvorschau - Tabellenansicht]                |
+--------------------------------------------------+
|              [Exportieren]                        |
+--------------------------------------------------+
```

## Unterstützte Formate

### Eingabeformate (Totalstationen)

| Format | Hersteller | Erweiterung |
|--------|------------|-------------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| Generisches CSV | - | .csv |

### Ausgabeformate

| Format | Verwendung |
|--------|------------|
| CSV | Import in PyArchInit Höhen |
| DXF | Import in CAD/GIS |
| GeoJSON | Direkter GIS-Import |
| Shapefile | GIS-Standard |

## Arbeitsablauf

### 1. Daten von Totalstation importieren

```
1. Totalstation mit PC verbinden
2. Datendatei herunterladen (natives Format)
3. Im Arbeitsordner speichern
```

### 2. Konvertierung mit TOPS

```
1. TOPS in PyArchInit öffnen
2. Eingabedatei auswählen (Durchsuchen)
3. Korrektes Eingabeformat wählen
4. Ausgabedatei festlegen
5. Ausgabeformat wählen (CSV empfohlen)
6. Exportieren klicken
```

### 3. Import in PyArchInit

Nach dem CSV-Export:
1. Das System fragt automatisch nach:
   - **Name des Fundorts**
   - **Maßeinheit** (Meter)
   - **Name des Zeichners**
2. Die Punkte werden als QGIS-Layer geladen
3. Optional: Kopie in Höhen-SE-Layer

### 4. Koordinatenkonvertierung (Optional)

Wenn Checkbox **"Koordinaten konvertieren"** aktiv:
- Offset X, Y, Z eingeben
- Koordinatentransformation anwenden
- Nützlich für lokale Bezugssysteme

## Datenvorschau

### Tabellenansicht

Zeigt Vorschau der importierten Daten:
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Datenbearbeitung

- Zeilen zur Löschung auswählen
- Schaltfläche **Löschen** entfernt ausgewählte Zeilen
- Nützlich zum Filtern nicht benötigter Punkte

## Integration mit SE-Höhen

### Automatische Kopie

Nach dem Import kann TOPS die Punkte in den Layer **"Höhen SE Zeichnung"** kopieren:
1. Fundortname wird abgefragt
2. Maßeinheit wird abgefragt
3. Zeichner wird abgefragt
4. Punkte werden mit korrekten Attributen kopiert

### Ausgefüllte Attribute

| Attribut | Wert |
|----------|------|
| sito_q | Eingegebener Fundortname |
| area_q | Aus point_name extrahiert |
| unita_misu_q | Eingegebene Einheit (Meter) |
| disegnatore | Eingegebener Name |
| data | Aktuelles Datum |

## Namenskonventionen

### Format point_name

Für automatische Arealextraktion:
```
[AREAL]-[PUNKTNAME]
Beispiel: 1000-P001
```

Das System trennt automatisch:
- `area_q` = 1000
- `point_name` = P001

## Best Practices

### 1. Im Feld

- Konsistente Punktbenennung verwenden
- Arealcode im Punktnamen einschließen
- Verwendetes Bezugssystem notieren

### 2. Import

- Korrektes Eingabeformat überprüfen
- Vorschau vor Export kontrollieren
- Fehlerhafte/doppelte Punkte löschen

### 3. Nach dem Import

- Koordinaten in QGIS überprüfen
- Höhen-SE-Layer kontrollieren
- Punkte mit korrekten SE verknüpfen

## Fehlerbehebung

### Format nicht erkannt

**Ursache**: Stationsformat nicht unterstützt

**Lösung**:
- Von Station in generisches Format exportieren (CSV)
- Stationsdokumentation überprüfen

### Falsche Koordinaten

**Ursachen**:
- Anderes Bezugssystem
- Offset nicht angewendet

**Lösungen**:
- Projektbezugssystem überprüfen
- Koordinatenkonvertierung anwenden

### Layer nicht erstellt

**Ursache**: Fehler während des Imports

**Lösung**:
- Fehlerlog kontrollieren
- Ausgabedateiformat überprüfen
- Konvertierung wiederholen

## Referenzen

### Quelldateien
- `tabs/tops_pyarchinit.py` - Hauptoberfläche
- `gui/ui/Tops2pyarchinit.ui` - UI-Layout

### Externe Software
- [Total Open Station](https://tops.iosa.it/) - Hauptsoftware
- Dokumentation der Stationsformate

---

## Video-Tutorial

### TOPS-Import
`[Platzhalter: video_tops.mp4]`

**Inhalte**:
- Download von Totalstation
- Formatkonvertierung
- Import in PyArchInit
- Integration mit SE-Höhen

**Voraussichtliche Dauer**: 12-15 Minuten

---

*Letzte Aktualisierung: Januar 2026*
