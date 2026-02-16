# PyArchInit - GeoArchaeo - Geostatistische Analyse

## Inhaltsverzeichnis
1. [Einleitung](#einleitung)
2. [Zugriff auf das Werkzeug](#zugriff-auf-das-werkzeug)
3. [Benutzeroberflaeche](#benutzeroberflaeche)
4. [Registerkarte Daten](#registerkarte-daten)
5. [Registerkarte Variogramm](#registerkarte-variogramm)
6. [Registerkarte Kriging](#registerkarte-kriging)
7. [Registerkarte Machine Learning](#registerkarte-machine-learning)
8. [Registerkarte Stichprobenplanung](#registerkarte-stichprobenplanung)
9. [Registerkarte Bericht](#registerkarte-bericht)
10. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
11. [Fehlerbehebung](#fehlerbehebung)
12. [Technische Hinweise](#technische-hinweise)

---

## Einleitung

**GeoArchaeo** ist das in PyArchInit integrierte Modul fuer geostatistische Analysen. Es bietet ein umfassendes Werkzeugset fuer die raeumliche Analyse archaeologischer Daten -- von der Variogramm-Modellierung ueber Kriging-Interpolation bis hin zu Machine-Learning-Vorhersagen und der Planung von Stichprobenstrategien.

<!-- VIDEO: Einfuehrung in GeoArchaeo -->
> **Video-Tutorial**: [Videolink GeoArchaeo-Einfuehrung einfuegen]

### Warum geostatistische Analyse in der Archaeologie?

Die geostatistische Analyse ermoeglicht es:

- **Interpolieren** von Werten zwischen bekannten Messpunkten, um aus diskreten Daten kontinuierliche Oberflaechen zu erzeugen
- **Quantifizieren** der raeumlichen Korrelation in archaeologischen Daten (z.B. Funddichte, Schichtdicke)
- **Vorhersagen** raeumlicher Verteilungen in noch nicht ausgegrabenen Bereichen
- **Optimieren** von Stichprobenstrategien fuer zukuenftige Prospektionen
- **Erstellen** umfassender analytischer Berichte fuer die wissenschaftliche Dokumentation

### Arbeitsablauf-Uebersicht

```
1. Daten laden          2. Variogramm          3. Kriging/ML
   (Registerkarte          (Registerkarte         (Registerkarte
    Daten)                  Variogramm)            Kriging/ML)
        |                      |                      |
   Layer und Felder       Variogramm berechnen   Interpolation oder
   auswaehlen             und modellieren         raeumliche Vorhersage
                               |                      |
                          4. Stichprobe          5. Bericht
                             (Registerkarte         (Registerkarte
                              Stichprobe)            Bericht)
                                  |                      |
                             Stichproben-         Analysebericht
                             strategie            erstellen
                             entwerfen
```

---

## Zugriff auf das Werkzeug

GeoArchaeo ist ueber die PyArchInit-Werkzeugleiste im Dropdown-Menue der Analysewerkzeuge zugaenglich.

### Ueber die Werkzeugleiste

1. Den **Analysewerkzeuge**-Button (Dropdown-Symbol) in der PyArchInit-Werkzeugleiste suchen
2. Auf den Dropdown-Pfeil klicken
3. **GeoArchaeo** aus der Liste auswaehlen

<!-- IMAGE: Analysewerkzeuge-Button in der Werkzeugleiste -->
> **Abb. 1**: Das Dropdown-Menue Analysewerkzeuge in der PyArchInit-Werkzeugleiste

Das GeoArchaeo-Panel erscheint als **Dock-Widget** in der QGIS-Oberflaeche. Es kann wie jedes andere QGIS-Panel verschoben, in der Groesse geaendert oder abgedockt werden.

<!-- IMAGE: GeoArchaeo-Panel in QGIS angedockt -->
> **Abb. 2**: Das GeoArchaeo-Panel in der QGIS-Oberflaeche angedockt

### Sprachauswahl

Das GeoArchaeo-Panel enthaelt oben eine **Sprachauswahl**, mit der die Sprache der Oberflaeche geaendert werden kann, ohne QGIS neu starten zu muessen. Unterstuetzte Sprachen sind Italienisch, Englisch, Deutsch, Franzoesisch, Spanisch, Arabisch, Katalanisch, Rumaenisch, Portugiesisch und Griechisch.

---

## Benutzeroberflaeche

Das GeoArchaeo-Panel ist in **6 Hauptregisterkarten** unterteilt, die jeweils einer Phase des geostatistischen Analyse-Arbeitsablaufs gewidmet sind.

| Registerkarte | Symbol | Funktion |
|---------------|--------|----------|
| **Daten** | Tabelle | Laden und Erkunden raeumlicher Daten aus QGIS-Layern |
| **Variogramm** | Diagramm | Berechnen und Modellieren experimenteller Variogramme |
| **Kriging** | Raster | Kriging-Interpolation durchfuehren (ordinaer, universell) |
| **ML** | Gehirn | Raeumliche Vorhersagen mit Machine Learning |
| **Stichprobe** | Zielscheibe | Planung von Stichprobenstrategien fuer archaeologische Prospektionen |
| **Bericht** | Dokument | Analyseberichte erstellen |

<!-- IMAGE: Uebersicht der 6 GeoArchaeo-Registerkarten -->
> **Abb. 3**: Die sechs Registerkarten des GeoArchaeo-Panels

### Panel-Werkzeugleiste

Am oberen Rand des Panels befinden sich:

- **Sprachauswahl**: Dropdown zum Aendern der Oberflaechen-Sprache
- **Beispieldaten laden**: Schaltflaeche zum Laden eines Testdatensatzes
- **Hilfe**: Schaltflaeche zum Zugriff auf die Dokumentation

---

## Registerkarte Daten

Die Registerkarte **Daten** ist der Ausgangspunkt jeder geostatistischen Analyse. Sie ermoeglicht das Laden und Anzeigen raeumlicher Daten aus QGIS-Layern.

### Daten laden

1. Die Registerkarte **Daten** oeffnen
2. Einen **Vektor-Layer** aus dem Dropdown auswaehlen (alle Punkt-Layer im QGIS-Projekt werden aufgelistet)
3. Das **Analysefeld** auswaehlen (das numerische Feld, das analysiert werden soll)
4. Auf **Daten laden** klicken

<!-- IMAGE: Registerkarte Daten mit ausgewaehltem Layer und Feld -->
> **Abb. 4**: Die Registerkarte Daten mit einem ausgewaehlten Layer und Analysefeld

### Beispieldaten

Um sich mit dem Werkzeug vertraut zu machen, kann ein **Beispieldatensatz** ueber die entsprechende Schaltflaeche geladen werden. Der Beispieldatensatz enthaelt simulierte archaeologische Daten mit Koordinaten und numerischen Werten, die fuer die geostatistische Analyse geeignet sind.

### Datenexploration

Nach dem Laden zeigt die Registerkarte:

| Information | Beschreibung |
|-------------|-------------|
| **Anzahl der Punkte** | Gesamtzahl der geladenen Punkte |
| **Ausdehnung** | Bounding Box des Datensatzes (xmin, ymin, xmax, ymax) |
| **Statistiken** | Mittelwert, Median, Standardabweichung, Min, Max |
| **Vorschau** | Tabelle mit den ersten Zeilen des Datensatzes |

### Datenanforderungen

- Der Layer muss ein **Punkt-Vektor-Layer** sein
- Das Analysefeld muss **numerische Werte** enthalten
- Die Punkte muessen **gueltige Koordinaten** im Koordinatenreferenzsystem des Projekts haben
- Mindestens **30 Punkte** werden fuer eine aussagekraeftige geostatistische Analyse empfohlen

---

## Registerkarte Variogramm

Die Registerkarte **Variogramm** ermoeglicht die Berechnung und Modellierung experimenteller Variogramme, die die Struktur der raeumlichen Korrelation in den Daten beschreiben.

### Was ist ein Variogramm?

Ein Variogramm ist ein Diagramm, das zeigt, wie die **Varianz** zwischen Punktepaaren sich in Abhaengigkeit von der **Entfernung** zwischen ihnen aendert. Die wichtigsten Parameter sind:

| Parameter | Beschreibung |
|-----------|-------------|
| **Nugget** | Varianz bei Entfernung Null (Messfehler + Mikroskalige Variabilitaet) |
| **Sill** | Erreichte Maximalvarianz (Plateau des Variogramms) |
| **Range** | Entfernung, ab der keine raeumliche Korrelation mehr besteht |

### Berechnung des experimentellen Variogramms

1. Sicherstellen, dass Daten in der Registerkarte Daten geladen wurden
2. Die Registerkarte **Variogramm** oeffnen
3. Die Parameter einstellen:
   - **Anzahl der Lags**: Anzahl der Entfernungsintervalle (Standard: 15)
   - **Maximale Entfernung**: Maximal zu beruecksichtigende Entfernung (Standard: auto)
   - **Winkeltoleranz**: Fuer Richtungsvariogramme (Standard: omnidirektional)
4. Auf **Variogramm berechnen** klicken

<!-- IMAGE: Berechnetes experimentelles Variogramm -->
> **Abb. 5**: Ein aus archaeologischen Daten berechnetes experimentelles Variogramm

### Variogramm-Modellierung

Nach der Berechnung des experimentellen Variogramms kann ein **theoretisches Modell** angepasst werden:

1. Den **Modelltyp** auswaehlen:
   - **Sphaerisch**: Das gaengigste Modell, erreicht den Sill bei einer endlichen Entfernung
   - **Exponentiell**: Erreicht den Sill asymptotisch
   - **Gaussisch**: Allmaelicher Uebergang, geeignet fuer sehr gleichmaessige Phaenomene
   - **Linear**: Variogramm ohne definierten Sill
2. Auf **Modell anpassen** klicken
3. Die geschaetzten Parameter (Nugget, Sill, Range) und die Anpassungsguete ueberpruefen

<!-- IMAGE: Angepasstes Variogramm-Modell -->
> **Abb. 6**: An das experimentelle Variogramm angepasstes sphaerisches Modell

### Richtungsvariogramme

Zur Ueberpruefung der **Anisotropie** (Variation der raeumlichen Struktur in verschiedenen Richtungen):

1. Eine **Winkeltoleranz** festlegen (z.B. 22,5 Grad)
2. Die zu analysierenden **Richtungen** auswaehlen (0, 45, 90, 135 Grad)
3. Die Variogramme in verschiedenen Richtungen vergleichen

---

## Registerkarte Kriging

Die Registerkarte **Kriging** ermoeglicht die Kriging-Interpolation, die geostatistische Standardmethode fuer optimale raeumliche Vorhersagen.

### Verfuegbare Kriging-Typen

| Typ | Beschreibung | Wann verwenden |
|-----|-------------|----------------|
| **Ordinaeres Kriging** | Nimmt einen konstanten, aber unbekannten lokalen Mittelwert an | Haeufigster Fall, stationaere Daten |
| **Universelles Kriging** | Beruecksichtigt einen raeumlichen Trend (Drift) | Wenn die Daten einen Richtungstrend zeigen |

### Kriging ausfuehren

1. Sicherstellen, dass ein Variogramm in der Registerkarte Variogramm modelliert wurde
2. Die Registerkarte **Kriging** oeffnen
3. Den **Kriging-Typ** auswaehlen (ordinaer oder universell)
4. Die Ausgaberaster-Parameter einstellen:
   - **Aufloesung**: Zellgroesse des Rasters (in CRS-Einheiten)
   - **Ausdehnung**: Automatisch aus dem Datensatz oder benutzerdefiniert
5. Die Kriging-Parameter einstellen:
   - **Minimale Punkte**: Mindestanzahl naher Punkte
   - **Maximale Punkte**: Hoechstanzahl naher Punkte
   - **Suchradius**: Maximale Entfernung fuer nahe Punkte
6. Auf **Kriging ausfuehren** klicken

<!-- IMAGE: Ergebnis der Kriging-Interpolation -->
> **Abb. 7**: Kriging-Interpolationskarte mit dem Vorhersageraster

### Kriging-Ergebnisse

Die Analyse erzeugt zwei Raster-Layer:

- **Vorhersage**: Die interpolierten Werte auf dem Raster
- **Kriging-Varianz**: Die Vorhersageunsicherheit in jeder Zelle

Die Layer werden automatisch zum QGIS-Projekt hinzugefuegt und auf der Karte angezeigt.

> **Hinweis**: Die Analyse wird in einem **Hintergrund-Thread** ausgefuehrt, sodass die QGIS-Oberflaeche waehrend der Berechnung benutzbar bleibt. Ein Fortschrittsbalken zeigt den Verarbeitungsstatus an.

---

## Registerkarte Machine Learning

Die Registerkarte **ML** bietet Machine-Learning-Methoden fuer raeumliche Vorhersagen als Alternative oder Ergaenzung zum Kriging.

### Verfuegbare Algorithmen

| Algorithmus | Beschreibung | Vorteile |
|-------------|-------------|----------|
| **Random Forest** | Ensemble von Entscheidungsbaeumen | Robust, behandelt nichtlineare Beziehungen |
| **Gradient Boosting** | Sequentielle Entscheidungsbaeume | Hohe Genauigkeit, geeignet fuer komplexe Muster |
| **SVR** | Support Vector Regression | Gut bei wenig Daten, flexible Kernel |

### ML-Arbeitsablauf

1. Die Registerkarte **ML** oeffnen
2. Den gewuenschten **Algorithmus** auswaehlen
3. Die **Praediktorvariablen** konfigurieren:
   - Koordinaten (X, Y)
   - Zusaetzliche Felder aus dem Layer (z.B. Hoehe, Neigung, Entfernung zu einem Fluss)
4. Die **Parameter** des Algorithmus einstellen (oder Standardwerte verwenden)
5. Die **Validierungsmethode** auswaehlen:
   - K-Fold-Kreuzvalidierung (Standard: 5 Folds)
   - Hold-out (Testprozentsatz)
6. Auf **Modell trainieren** klicken

<!-- IMAGE: ML-Modellkonfiguration -->
> **Abb. 8**: Random-Forest-Modellkonfiguration in der Registerkarte ML

### ML-Ergebnisse

| Ergebnis | Beschreibung |
|----------|-------------|
| **Vorhersagekarte** | Raster-Layer mit vorhergesagten Werten |
| **Variablenwichtigkeit** | Diagramm der relativen Bedeutung der Praediktorvariablen |
| **Validierungsmetriken** | R-Quadrat, RMSE, MAE aus der Kreuzvalidierung |
| **Residuendiagramm** | Streudiagramm der beobachteten vs. vorhergesagten Werte |

### Vergleich Kriging vs. ML

Zum Vergleich der Ergebnisse:

1. Sowohl Kriging als auch ML auf denselben Daten ausfuehren
2. Validierungsmetriken in der Registerkarte Bericht vergleichen
3. Differenzkarten visualisieren

---

## Registerkarte Stichprobenplanung

Die Registerkarte **Stichprobe** ermoeglicht die Planung optimaler Stichprobenstrategien fuer zukuenftige archaeologische Prospektionen.

### Stichprobenstrategien

| Strategie | Beschreibung | Wann verwenden |
|-----------|-------------|----------------|
| **Einfach zufaellig** | Zufaellig im Gebiet verteilte Punkte | Ohne Vorabinformationen |
| **Geschichtet zufaellig** | Zufaellige Punkte innerhalb definierter Schichten | Bei Gebieten mit unterschiedlichen Zonen |
| **Regelmaessiges Raster** | Punkte auf einem regelmaessigen Raster | Fuer gleichmaessige Flaechenabdeckung |
| **Optimiert** | Punkte zur Minimierung der Kriging-Varianz positioniert | Wenn ein Variogramm vorliegt |

### Stichprobenplanung entwerfen

1. Die Registerkarte **Stichprobe** oeffnen
2. Die **Stichprobenstrategie** auswaehlen
3. Die gewuenschte **Anzahl der Punkte** festlegen
4. Das **Untersuchungsgebiet** definieren:
   - Aus der Ausdehnung des aktuellen Layers
   - Aus einem Polygon-Layer
   - Durch manuelles Zeichnen auf der Karte
5. Optionale **Einschraenkungen** festlegen:
   - Mindestabstand zwischen Punkten
   - Ausschlussgebiete
6. Auf **Stichprobe generieren** klicken

<!-- IMAGE: Generierte Stichprobenpunkte -->
> **Abb. 9**: Optimierte Stichprobenpunkte ueberlagert auf der Karte des Untersuchungsgebiets

### Stichprobenergebnisse

- Ein **Punkt-Vektor-Layer** mit Stichprobenpunkten wird dem QGIS-Projekt hinzugefuegt
- Eine **Attributtabelle** mit Koordinaten und Punkt-Identifikatoren
- Ein **Bericht** mit Strategiestatistiken (Abdeckung, Entfernungen, usw.)

---

## Registerkarte Bericht

Die Registerkarte **Bericht** ermoeglicht die Erstellung umfassender Berichte der geostatistischen Analyse.

### Berichtsinhalt

Der Bericht enthaelt automatisch alle waehrend der Sitzung durchgefuehrten Analysen:

| Abschnitt | Inhalt |
|-----------|--------|
| **Zusammenfassung** | Ueberblick ueber den Datensatz und die durchgefuehrten Analysen |
| **Daten** | Deskriptive Statistiken, Verteilung, Punktkarte |
| **Variogramm** | Experimentelles Variogramm, Modell, Parameter |
| **Interpolation** | Kriging-/ML-Karte, Validierungsmetriken |
| **Stichprobe** | Strategie, Punktkarte, Statistiken |
| **Schlussfolgerungen** | Zusammenfassende Interpretation der Ergebnisse |

### Bericht erstellen

1. Die Registerkarte **Bericht** oeffnen
2. Die **Abschnitte** auswaehlen, die einbezogen werden sollen (standardmaessig alle)
3. Das **Ausgabeformat** festlegen:
   - PDF (empfohlen fuer die Dokumentation)
   - HTML (fuer interaktive Ansicht)
   - Markdown (fuer spaetere Bearbeitung)
4. Optionale **zusaetzliche Anmerkungen** oder Kommentare eingeben
5. Auf **Bericht erstellen** klicken

<!-- IMAGE: Vorschau des erstellten Berichts -->
> **Abb. 10**: Vorschau eines von GeoArchaeo erstellten geostatistischen Analyseberichts

### Export

Der Bericht kann lokal gespeichert oder in den verfuegbaren Formaten exportiert werden. Bilder (Diagramme, Karten) werden direkt in den Bericht eingebettet.

---

## Operativer Arbeitsablauf

Hier ist ein typischer Arbeitsablauf fuer eine vollstaendige geostatistische Analyse in GeoArchaeo:

### Schritt 1: Datenvorbereitung

1. Den Punkt-Vektor-Layer in QGIS laden
2. Sicherstellen, dass das zu analysierende numerische Feld vorhanden und korrekt ist
3. Das Koordinatenreferenzsystem ueberpruefen

### Schritt 2: Datenexploration

1. GeoArchaeo ueber die Werkzeugleiste oeffnen
2. In der Registerkarte **Daten** den Layer und das Feld auswaehlen
3. Die deskriptiven Statistiken ueberpruefen
4. Die Datenverteilung pruefen (nach Ausreissern oder anomalen Werten suchen)

### Schritt 3: Variogramm-Analyse

1. In der Registerkarte **Variogramm** das experimentelle Variogramm berechnen
2. Verschiedene Modelle ausprobieren (sphaerisch, exponentiell, gaussisch)
3. Das Modell mit der besten Anpassung waehlen
4. Die Parameter notieren (Nugget, Sill, Range)

### Schritt 4: Interpolation

1. In der Registerkarte **Kriging** die Rasterparameter einstellen
2. Ordinaeres Kriging ausfuehren
3. Die Vorhersagekarte und Varianz ueberpruefen
4. Optional mit einem ML-Modell in der Registerkarte ML vergleichen

### Schritt 5: Stichprobe (optional)

1. In der Registerkarte **Stichprobe** eine Strategie fuer zukuenftige Prospektionen entwerfen
2. Das Variogramm fuer optimierte Stichprobennahme verwenden

### Schritt 6: Bericht

1. In der Registerkarte **Bericht** den Abschlussbericht erstellen
2. Als PDF fuer die Dokumentation exportieren

---

## Fehlerbehebung

### Haeufige Probleme

| Problem | Ursache | Loesung |
|---------|---------|---------|
| Keine Layer verfuegbar | Keine Punkt-Layer im Projekt | Einen Punkt-Vektor-Layer zum QGIS-Projekt hinzufuegen |
| Keine numerischen Felder | Der Layer hat keine numerischen Felder | Die Attributtabelle des Layers ueberpruefen |
| Flaches Variogramm | Daten ohne raeumliche Korrelation | Daten pruefen, maximale Entfernung erhoehen |
| Kriging schlaegt fehl | Variogramm-Modell nicht angepasst | Zuerst ein Modell in der Registerkarte Variogramm anpassen |
| Schlechte ML-Ergebnisse | Zu wenig Daten oder nicht informative Variablen | Praediktorvariablen hinzufuegen oder Daten erweitern |
| Panel nicht sichtbar | Widget versehentlich geschlossen | Ueber das Menue Analysewerkzeuge erneut oeffnen |

### Haeufige Fehler

- **"Unzureichende Daten"**: Mindestens 30 Punkte werden fuer eine zuverlaessige Analyse benoetigt
- **"Variogramm-Modell nicht definiert"**: Vor dem Kriging ein Modell anpassen
- **"Inkompatibles CRS"**: Alle Layer muessen dasselbe Koordinatenreferenzsystem verwenden

### Leistung

- Die Analyse wird in einem **Hintergrund-Thread** ausgefuehrt: Die QGIS-Oberflaeche bleibt benutzbar
- Bei sehr grossen Datensaetzen (>10.000 Punkte) kann die Verarbeitung laenger dauern
- Der Fortschritt kann ueber den Balken am unteren Rand des Panels verfolgt werden

---

## Technische Hinweise

### Abhaengigkeiten

GeoArchaeo verwendet folgende Python-Bibliotheken:

| Bibliothek | Verwendung |
|------------|-----------|
| **NumPy** | Numerische und Matrixberechnungen |
| **SciPy** | Optimierung und Modellanpassung |
| **scikit-learn** | Machine-Learning-Algorithmen |
| **Matplotlib** | Diagrammerstellung |

### Koordinatenreferenzsysteme

- GeoArchaeo arbeitet im Koordinatenreferenzsystem des aktuellen QGIS-Projekts
- Ein **projiziertes CRS** (in Metern) wird fuer die geostatistische Analyse empfohlen
- Geographische Systeme (in Grad) koennen ungenaue Ergebnisse liefern

### Export der Ergebnisse

Ergebnisse koennen in verschiedenen Formaten exportiert werden:

- **Raster-Layer** (GeoTIFF) fuer interpolierte Oberflaechen
- **Vektor-Layer** (GeoPackage, Shapefile) fuer Stichprobenpunkte
- **Diagramme** (PNG, SVG) fuer Variogramme und Diagnostiken
- **Berichte** (PDF, HTML, Markdown) fuer die Dokumentation

### QGIS-Integration

- Ausgabe-Layer werden automatisch dem **Layer**-Panel in QGIS hinzugefuegt
- Die Darstellung von Raster-Layern kann ueber die QGIS-Layereigenschaften angepasst werden
- Die Ergebnisse sind mit allen raeumlichen Analysewerkzeugen von QGIS kompatibel

---

> **Hinweis**: GeoArchaeo befindet sich in aktiver Entwicklung. Um Fehler zu melden oder Verbesserungen vorzuschlagen, verwenden Sie bitte den Issue-Tracker des PyArchInit-Projekts auf GitHub.
