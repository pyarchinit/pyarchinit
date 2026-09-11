# Tutorial 25: Time Manager (GIS-Zeitsteuerung)

## Einführung

Der **Time Manager** (GIS-Zeitsteuerung) ist ein fortgeschrittenes Werkzeug zur Visualisierung der stratigraphischen Sequenz im zeitlichen Verlauf. Er ermöglicht die "Navigation" durch die Schichten mittels Zeitsteuerung und zeigt progressiv die SE von der ältesten bis zur jüngsten (die Entstehung des Fundorts).

### Hauptfunktionen

- Progressive Visualisierung der stratigraphischen Schichten
- Steuerung über Drehregler/Schieberegler
- Kumulativer Modus oder Einzelschicht
- Automatische Bild-/Videogenerierung
- Integration mit Harris-Matrix

## Zugriff

### Über Menü
**PyArchInit** → **Time Manager**

### Voraussetzungen

- Layer mit Feld `order_layer` (stratigraphischer Index)
- SE mit ausgefülltem order_layer
- Layer in QGIS geladen

## Oberfläche

### Hauptpanel

```
+--------------------------------------------------+
|         GIS-Zeitverwaltung                        |
+--------------------------------------------------+
| Verfügbare Layer:                                 |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] anderer_layer                                |
+--------------------------------------------------+
|              [Drehregler]                         |
|                   /  \                            |
|                  /    \                           |
|                 /______\                          |
|                                                   |
|         Schicht: [SpinBox: 0-N]                  |
+--------------------------------------------------+
| [x] Kumulativer Modus (zeigt <= Schicht)        |
+--------------------------------------------------+
| [ ] Matrix anzeigen      [Stop] [Video erzeugen] |
+--------------------------------------------------+
| [Matrix-/Bildvorschau]                           |
+--------------------------------------------------+
```

### Steuerungen

| Steuerung | Funktion |
|-----------|----------|
| Layer-Checkbox | Layer zur Steuerung auswählen |
| Drehregler | Durch Schichten navigieren (Drehung) |
| SpinBox | Direkte Schichteingabe |
| Kumulativer Modus | Alle Schichten bis zur ausgewählten anzeigen |
| Matrix anzeigen | Synchronisierte Harris-Matrix anzeigen |

## Das Feld order_layer

### Was ist order_layer?

Das Feld `order_layer` definiert die stratigraphische Anzeigereihenfolge:
- **0** = Älteste Schicht (tief)
- **N** = Jüngste Schicht (oberflächlich)

Das ist die Konvention der Schaltfläche **Ordine stratigrafico** (stratigraphische Reihenfolge) mit aktiviertem Kontrollkästchen "Reihenfolge: Alt → Neu" (Standardeinstellung, siehe Tutorial 03): Wurde die Reihenfolge umgekehrt berechnet, zeigen der Time Manager und die Karte die Sequenz auf den Kopf gestellt.

### order_layer ausfüllen

Im SE-Formular, Tab **Hilfe** → **Tool Box**, berechnet die Schaltfläche **Ordine stratigrafico** (stratigraphische Reihenfolge) `order_layer` aus den stratigraphischen Beziehungen (siehe Tutorial 03); der Wert der aktuellen SE erscheint im Feld unter der Schaltfläche. Regeln:
1. 0 für die ältesten SE, aufsteigende Werte zu den jüngsten hin (an der Oberfläche)
2. Zeitgleiche SE können denselben Wert haben
3. Der Matrix-Sequenz folgen

### Beispiel

| SE | order_layer | Beschreibung |
|----|-------------|--------------|
| SE001 | 4 | Oberflächenhumus |
| SE002 | 3 | Pflugschicht |
| SE003 | 2 | Versturz |
| SE004 | 1 | Laufhorizont |
| SE005 | 0 | Fundament |

Seit 5.13.19-alpha werden die SE- und USM-Layer, die pyArchInit auf die Karte lädt (siehe Tutorial 14, *Stilauswahl*), in derselben Reihenfolge gezeichnet, die der Time Manager verwendet: nach der Chronologie der Periode, dann nach `order_layer` (0 = älteste), sodass die jüngsten Einheiten oben liegen.

## Anzeigemodi

### Einzelschicht-Modus

Checkbox **NICHT** aktiviert:
- Zeigt NUR SE der ausgewählten Schicht
- Nützlich zum Isolieren einzelner Schichten
- "Scheiben"-Ansicht

### Kumulativer Modus

Checkbox **AKTIVIERT**:
- Zeigt alle SE von Schicht 0 (älteste) bis zur ausgewählten
- Zeigt die Entstehung des Fundorts, von den ältesten zu den jüngsten SE
- Realistischere Darstellung

## Matrix-Integration

### Synchronisierte Anzeige

Mit aktiviertem Checkbox **"Matrix anzeigen"**:
- Die Harris-Matrix erscheint im Panel
- Aktualisiert sich synchron mit der Schicht
- Hebt SE der aktuellen Schicht hervor

### Bildgenerierung

Der Time Manager kann generieren:
- Screenshots für jede Schicht
- Bildsequenzen
- Zeitraffer-Videos

## Video-/Bildgenerierung

### Prozess

1. Einzuschließende Layer auswählen
2. Schichtbereich konfigurieren (min-max)
3. Auf **"Video erzeugen"** klicken
4. Verarbeitung abwarten
5. Ausgabe im vorgesehenen Ordner

### Ausgabe

- PNG-Bilder für jede Schicht
- Optional: Kompiliertes MP4-Video

## Typischer Arbeitsablauf

### 1. Vorbereitung

```
1. QGIS-Projekt mit SE-Layern öffnen
2. Überprüfen, dass order_layer ausgefüllt ist
3. Time Manager öffnen
```

### 2. Layer-Auswahl

```
1. Zu steuernde Layer auswählen
2. Üblicherweise: pyunitastratigrafiche und/oder _usm
```

### 3. Navigation

```
1. Drehregler oder SpinBox verwenden
2. Änderung der Anzeige beobachten
3. Kumulativen Modus aktivieren/deaktivieren
```

### 4. Dokumentation

```
1. "Matrix anzeigen" aktivieren
2. Aussagekräftige Screenshots erstellen
3. Optional: Video generieren
```

## Layout-Templates

### Template laden

Der Time Manager unterstützt QGIS-Templates für:
- Benutzerdefinierte Drucklayouts
- Kopfzeilen und Legenden
- Standardformate

### Verfügbare Templates

Im Ordner `resources/templates/`:
- Basis-Template
- Template mit Matrix
- Template für Video

## Best Practices

### 1. order_layer

- VOR Verwendung des Time Managers ausfüllen
- Aufeinanderfolgende Werte verwenden
- Zeitgleiche SE = gleicher Wert

### 2. Visualisierung

- Mit Schicht 0 (älteste) beginnen
- In aufsteigender Reihenfolge fortfahren
- Kumulativen Modus für Präsentationen verwenden

### 3. Dokumentation

- Screenshots bei bedeutsamen Schichten erstellen
- Phasenübergänge dokumentieren
- Videos für Berichte generieren

## Fehlerbehebung

### Layer nicht in der Liste sichtbar

**Ursache**: Layer ohne order_layer-Feld

**Lösung**:
- Feld order_layer zum Layer hinzufügen
- Mit entsprechenden Werten füllen

### Keine visuelle Änderung

**Ursachen**:
- order_layer nicht ausgefüllt
- Filter nicht angewendet

**Lösungen**:
- order_layer-Werte in SE überprüfen
- Prüfen, dass Layer ausgewählt ist

### Drehregler reagiert nicht

**Ursache**: Kein Layer ausgewählt

**Lösung**: Mindestens einen Layer aus der Liste auswählen

## Referenzen

### Quelldateien
- `tabs/Gis_Time_controller.py` - Hauptoberfläche
- `gui/ui/Gis_Time_controller.ui` - UI-Layout

### Datenbankfeld
- `us_table.order_layer` - Stratigraphischer Index

---

## Video-Tutorial

### Time Manager
`[Platzhalter: video_time_manager.mp4]`

**Inhalte**:
- order_layer-Konfiguration
- Zeitliche Navigation
- Videogenerierung
- Matrix-Integration

**Voraussichtliche Dauer**: 15-18 Minuten

---

*Letzte Aktualisierung: Januar 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../../animations/pyarchinit_timemanager_animation.html)
