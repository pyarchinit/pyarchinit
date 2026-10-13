# Tutorial 25: Time Manager (GIS-Zeitsteuerung)

## Einführung

Der **Time Manager** (GIS-Zeitsteuerung) ist ein fortgeschrittenes Werkzeug zur Visualisierung der stratigraphischen Sequenz im zeitlichen Verlauf. Er ermöglicht die "Navigation" durch die Schichten mittels Zeitsteuerung und zeigt progressiv die SE von der ältesten bis zur jüngsten (die Entstehung des Fundorts).

### Hauptfunktionen

- Progressive Visualisierung der stratigraphischen Schichten
- Steuerung über Drehregler/Schieberegler
- Kumulativer Modus oder Einzelschicht
- Automatischer Druck der Atlasblätter, eines je Schicht
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
| [ ] Kumulativer Modus (zeigt <= Schicht)        |
+--------------------------------------------------+
| [ ] Matrix anzeigen                              |
| [Atlas Druck Periodentabellen]                   |
| [Druckvorgang stoppen]                           |
+--------------------------------------------------+
| [Matrix-/Bildvorschau]                           |
+--------------------------------------------------+
```

### Steuerungen

| Steuerung | Funktion |
|-----------|----------|
| Reiter (oben) | **System der relativen Chronologie** (Layer-Liste, Drehregler und Schicht) und **Absolutes Chronologiesystem** (Suche nach Jahren, siehe "Absolute Chronologie") |
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

Das ist die Konvention der Schaltfläche **Stratigraphische Ordnung** mit aktiviertem Kontrollkästchen "Reihenfolge: Alt → Neu" (Standardeinstellung, siehe Tutorial 03): Wurde die Reihenfolge umgekehrt berechnet, zeigen der Time Manager und die Karte die Sequenz auf den Kopf gestellt.

### order_layer ausfüllen

Im SE-Formular, Tab **Hilfe** → **Tool Box**, berechnet die Schaltfläche **Stratigraphische Ordnung** `order_layer` aus den stratigraphischen Beziehungen (siehe Tutorial 03); der Wert der aktuellen SE erscheint im Feld unter der Schaltfläche. Regeln:
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

### Absolute Chronologie

Der zweite Reiter des Fensters, **Absolutes Chronologiesystem**, arbeitet mit Jahren statt mit den Schichten von `order_layer`: Man wählt ein Zeitintervall, und die SE der Perioden, die sich mit diesem Intervall überschneiden, werden auf die Karte geladen. Voraussetzung ist die ausgefüllte Periodisierung (siehe Tutorial 04) mit der **Anfangschronologie** und der **Endchronologie** jeder Periode und Phase: Eine Periode ohne Jahre wird nicht gefunden.

**Steuerungen.**

- **Anfängliche Chronologie** und **Abschließende Chronologie**: zwei Zahlenfelder, die sich so lesen: "Zeigt das Zeitintervall zwischen dem Jahr an: … und das jahr …". Die Jahre reichen von `-4.000.000` bis `2100`: Negative Werte sind v. Chr. (268 v. Chr. = `-268`), positive sind n. Chr. ohne Vorzeichen (1400 n. Chr. = `1400`). Das ältere Jahr kommt in die Anfängliche Chronologie.
- Schaltfläche **Siehe**: startet die Suche.

**Was die Schaltfläche Siehe tut.**

1. Sie sucht in der Periodisierung (aller Fundorte der Datenbank) die Perioden und Phasen, deren Datierung sich mit dem Intervall **überschneidet**, also die nicht vor dem Anfangsjahr enden und nicht nach dem Endjahr beginnen. Findet sie keine, warnt sie "Es gibt keine Perioden in diesem Zeitintervall." und bricht ab.
2. Sie nimmt die SE, deren Anfangsperiode und Anfangsphase den gefundenen entsprechen. Gibt es keine, warnt sie "es gibt keine Geometrien, die angezeigt werden können".
3. Sie lädt die Layer dieser SE auf die Karte, mit derselben Ladefunktion wie das SE-Formular (siehe Tutorial 03).
4. Sie aktualisiert die Matrix-Vorschau, wenn **Matrix anzeigen** aktiviert ist: Die Vorschau folgt den angehakten Layern und der Schicht des relativen Reiters, nicht dem Jahresintervall.

**Unterschied zum relativen Reiter.** Der Drehregler und der kumulative Modus **filtern** bereits geladene Layer; **Siehe** dagegen **fügt** dem Projekt bei jedem Klick eine neue Layergruppe **hinzu** (die früheren bleiben im Projekt). Wie im SE-Formular filtert die Ladefunktion bei einer PostgreSQL-Datenbank nach Fundort und nicht nach einzelner SE: Die Layer zeigen den ganzen Fundort.

## Matrix-Integration

### Synchronisierte Anzeige

Mit aktiviertem Checkbox **"Matrix anzeigen"**:
- Die Harris-Matrix erscheint im Panel
- Aktualisiert sich synchron mit der Schicht
- Hebt SE der aktuellen Schicht hervor

### Bildgenerierung

Der Time Manager kann generieren:
- Ein Blatt für jede Schicht, gestaltet mit der gewählten Layout-Vorlage (JPG-Bild)
- Die Harris-Matrix dieser Schicht im Blatt, wenn **Matrix anzeigen** aktiviert ist

## Druck der Blätter

### Prozess

1. Einzuschließende Layer auswählen
2. **Matrix anzeigen** aktivieren, wenn die Matrix auf den Blättern erscheinen soll (sonst wird das Matrixbild der Vorlage ausgeblendet)
3. Auf **Atlas Druck Periodentabellen** klicken
4. Im sich öffnenden Fenster die Layout-Vorlage wählen (siehe die Anmerkung «Welche Vorlage» am Ende) und bestätigen
5. Den Ordner wählen, in dem die Blätter gespeichert werden
6. Die Frage beantworten, ob der Layout Designer geöffnet werden soll, um die Vorlage vor dem Start nachzubearbeiten
7. Abwarten: Ein Fortschrittsbalken zeigt das Blatt in Arbeit, und am Ende nennt eine Meldung den Speicherort
8. Zum Anhalten der Erzeugung auf **Druckvorgang stoppen** klicken: Die bereits geschriebenen Blätter bleiben im Ordner

### Ausgabe

- Eine `Tavola_N.jpg` für jede Schicht (N ist der Wert von `order_layer`) im gewählten Ordner: die Karte auf dieser Schicht, im aktiven Modus (kumulativ oder Einzelschicht)
- Der Titel «Tavola N» und das Matrixbild erscheinen, wenn die Vorlage sie vorsieht (die Matrix nur bei aktiviertem **Matrix anzeigen**)
- Schichten, in denen keine SE eine ausgefüllte Datierung hat, werden übersprungen: In der Dateinummerierung entstehen deshalb Lücken
- Bei einer zweiseitigen Vorlage entstehen je Schicht zwei Bilder, das zweite heißt `Tavola_N_2.jpg` (siehe die Anmerkung «Eine beliebige Vorlage tauglich machen» am Ende)

**Beschriftungen des Blatts.** Beim Erzeugen der Atlasblätter setzt der Time Manager die Beschriftungen des Blatts auf die gewählten Layer — die Nummer der Einheit in einem Kreis bei den SE, die Höhe bei den Punkten — und entfernt sie am Ende der Erzeugung wieder, wobei er die vorherigen zurücksetzt. Seit 5.13.110-alpha entfernt er sie in jedem Fall, auch wenn ein Blatt scheitert: Früher blieben sie in diesem Fall auf den Layern des Projekts und landeten beim Speichern in der Projektdatei.

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
2. Die Blätter mit "Atlas Druck Periodentabellen" drucken
3. Die Dateien Tavola_N.jpg im gewählten Ordner prüfen
```

## Layout-Templates

### Template laden

Der Time Manager unterstützt QGIS-Templates für:
- Benutzerdefinierte Drucklayouts
- Kopfzeilen und Legenden
- Standardformate

### Verfügbare Templates

Das Auswahlfenster listet die `.qpt`-Dateien auf, die im Plugin-Ordner, in `resources/dbfiles/` und in `~/pyarchinit_5/bin/profile/template/` gefunden werden:
- `layout_TimeManager`: die Vorlage des Time Managers, mit dem Titel «Tavola N» und dem Matrixbild
- die Drucklayouts des pyArchInit-Profils (zum Beispiel die «Modello adArte…»)
- jede andere `.qpt`, gewählt mit der Schaltfläche **Sfoglia...** (Durchsuchen)

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
- Blätter für Berichte drucken (eines je Schicht)

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
- Druck der Blätter
- Matrix-Integration

**Voraussichtliche Dauer**: 15-18 Minuten

---

*Letzte Aktualisierung: Oktober 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../../animations/pyarchinit_timemanager_animation.html)

---

## Die Matrix, ab 5.13.44

Die Matrix des Time Managers geht nicht mehr über Graphviz. Sie wird von derselben Layout-Engine gezeichnet wie das Panel **Matrix ansehen**, innerhalb von QGIS und ohne Unterprozesse.

- **Sie ist sofort da.** Auf der Beispielstätte (51 SE, 81 Beziehungen) kostet die Zeichnung wenige Millisekunden statt etwa drei Zehntelsekunden, und die gelegentlich hängenden Prozesse `dot` und `tred` sind weg. Die Perioden der Stätte werden **einmal** gelesen: vorher je einmal pro Areal und pro Periode, bei jedem Rasten des Drehreglers.
- **Im Atlas ist die Matrix vektoriell.** Das Bild im Blatt ist ein SVG von einigen zehn KB statt eines JPEG von Megabytes.
- **Es ist dieselbe Matrix** wie im Extended-Matrix-Panel: gleiche Periodenbänder, gleiche Symbologie, gleiche Redundanzreduktion. Pfeile, die die Bänder **hinaufsteigen** — wo Stratigraphie und Chronologie sich widersprechen — werden **rot** gezeichnet.
- Die Matrix enthält weiterhin nur die an der aktuellen Reglerposition sichtbaren SE.

- Einheiten, die an der aktuellen Position **nicht sichtbar** sind, aber von einer Beziehung genannt werden, erscheinen dennoch in der Zeichnung, **blass**: ohne sie wirkte die Abfolge zerrissen, wie die anderen gezeichnet wirkten sie wie auf der Karte.

> **Welche Vorlage.** In der Auswahl ist jede Vorlage markiert: **✓** hat Titel und Matrixbild (die des Time Managers), **•** nur die Karte — die Blätter entstehen, nur schlichter — **✗** hat keine Karte. Früher führte eine Vorlage ohne diese Elemente dazu, dass der Generator wortlos zurückkehrte.

> **Eine beliebige Vorlage tauglich machen.** Mit `scripts/prepare_atlas_templates.py` (mit dem Python von QGIS auszuführen) entsteht neben jeder Vorlage eine Kopie mit dem Zusatz « + Time Manager», die Titel und Matrixbild auf einer **neuen Seite** trägt. Die Originale bleiben unberührt. Jede Stufe liefert dann zwei Bilder.
