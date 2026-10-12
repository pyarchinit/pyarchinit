# PyArchInit - GeoArchaeo - Geostatistische Analyse

## Inhaltsverzeichnis
1. [Einleitung](#einleitung)
2. [Zugriff auf das Werkzeug](#zugriff-auf-das-werkzeug)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Registerkarte Daten](#registerkarte-daten)
5. [Registerkarte Variogramm](#registerkarte-variogramm)
6. [Registerkarte Kriging](#registerkarte-kriging)
7. [Registerkarte Muster (ML)](#registerkarte-muster-ml)
8. [Registerkarte Stichprobenplanung](#registerkarte-stichprobenplanung)
9. [Registerkarte Bericht](#registerkarte-bericht)
10. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
11. [Fehlerbehebung](#fehlerbehebung)
12. [Technische Hinweise](#technische-hinweise)

---

## Einleitung

**GeoArchaeo** ist das in PyArchInit integrierte Modul für geostatistische Analysen; es entspricht der Version **1.3.1** des GeoArchaeo-Plugins. Es arbeitet mit jedem Punktlayer des QGIS-Projekts, der ein numerisches Feld besitzt (Scherbenzahlen, geophysikalische Messwerte, Bodenanalysen, Grabmaße…), und führt die Analyse von der deskriptiven Statistik über das Variogramm und die Interpolation mit gewöhnlichem Kriging samt Unsicherheit bis zur Suche nach Gruppen und Anomalien mit maschinellem Lernen, zum Vorschlag neuer Probenahmestellen und schließlich zu einem Bericht.

Die Oberfläche von GeoArchaeo gibt es nur auf Italienisch und Englisch. In dieser Anleitung werden die Beschriftungen übersetzt; in Klammern steht jeweils die englische Beschriftung, die im Panel erscheint.

<!-- VIDEO: Einfuehrung in GeoArchaeo -->
> **Video-Tutorial**: [Videolink GeoArchaeo-Einfuehrung einfuegen]

### Warum geostatistische Analyse in der Archäologie?

Die geostatistische Analyse ermöglicht es:

- die Verteilung der Messwerte zu **beschreiben** (Mittelwert, Streuung, Schiefe, Ausreißer)
- die räumliche Korrelation zu **quantifizieren**, also bis zu welcher Distanz sich die Werte ähneln (Variogramm)
- Werte zwischen bekannten Punkten zu **interpolieren** und so eine kontinuierliche Oberfläche samt ihrer Unsicherheit zu erhalten (Kriging)
- Gruppen ähnlicher Punkte und Anomalien zu **erkennen** (maschinelles Lernen)
- zu **planen**, wo in den nächsten Kampagnen beprobt oder gegraben werden soll
- die Analysen in einem Bericht zu **dokumentieren**

### Arbeitsablauf-Übersicht

```
Eingabedaten: Punktlayer + numerisches Feld (oben, nur einmal gewählt)
  │
  ├─ 1 Daten ................. deskriptive Statistik, Histogramm
  ├─ 2 Variogramm ............ Nugget, Sill, Range, Anisotropie
  ├─ 3 Kriging ............... Schätz- und Unsicherheitsraster, Kreuzvalidierung
  ├─ 4 Muster (ML) ........... Gruppen und Anomalien (Punktlayer)
  ├─ 5 Stichprobenplanung .... vorgeschlagene neue Punkte (Punktlayer)
  └─ 6 Bericht ............... HTML-Dokument mit interaktiven Diagrammen oder PDF
```

### Neu in Version 1.3.1

- Layer und Feld werden **einmal** oben gewählt und gelten für alle Registerkarten; jede Registerkarte behält ihre eigenen Ergebnisse
- Diagramme erscheinen im Panel auch ohne QtWebEngine (statische Vorschau und Schaltfläche zum Öffnen im Browser)
- Das Kriging erzeugt auch das **Unsicherheitsraster**, wendet die Farbskala an und berechnet eine echte **Leave-one-out-Kreuzvalidierung**
- Die Anisotropie wird mit echten **Richtungsvariogrammen** geprüft; Nugget, Sill und Range lassen sich von Hand festlegen
- Variogramm und Kriging sind deutlich schneller (Nachbarsuche mit KD-Baum): Gitter bis **500 × 500 Zellen**
- NULL-Werte bringen Statistik und Kriging nicht mehr zum Absturz; der Bericht enthält die Diagramme; die Beispieldaten stammen aus dem Modulordner
- Die Sprache des Panels wird in den QGIS-Einstellungen gespeichert

---

## Zugriff auf das Werkzeug

GeoArchaeo gehört zur Gruppe der Analysewerkzeuge von PyArchInit.

### Über die Werkzeugleiste

1. In der PyArchInit-Werkzeugleiste die Dropdown-Schaltfläche der **Analysewerkzeuge** suchen (dieselbe Gruppe, die unter anderem SAM, Pottery Tools und MoveCost enthält)
2. Auf den Pfeil neben der Schaltfläche klicken: das sichtbare Symbol kann zu einem anderen Werkzeug der Gruppe gehören
3. **GeoArchaeo - Geostatistische Analyse** wählen

<!-- IMAGE: Dropdown-Schaltflaeche der Analysewerkzeuge in der Werkzeugleiste -->
> **Abb. 1**: Das Dropdown-Menü der Analysewerkzeuge in der PyArchInit-Werkzeugleiste

Derselbe Eintrag befindet sich im Menü **pyArchInit** der QGIS-Menüleiste sowie im Plugin-Menü unter **pyArchInit - Archaeological GIS Tools**.

Das GeoArchaeo-Panel öffnet sich als **andockbares Bedienfeld** am rechten Rand des QGIS-Fensters: Es lässt sich wie jedes QGIS-Bedienfeld verschieben, in der Größe ändern oder abkoppeln. Wird es geschlossen, öffnet derselbe Eintrag es wieder, und die Ergebnisse der Sitzung sind noch vorhanden.

<!-- IMAGE: GeoArchaeo-Panel rechts in QGIS angedockt -->
> **Abb. 2**: Das GeoArchaeo-Panel am rechten Rand des QGIS-Fensters angedockt

### Sprachauswahl

Oben rechts bietet die Auswahlliste **«Sprache:»** (*Language:*) **Italiano** und **English**, die einzigen beiden Sprachen der GeoArchaeo-Oberfläche. Der Wechsel erfolgt sofort, ohne QGIS neu zu starten, und die Wahl wird in den QGIS-Einstellungen gespeichert. Solange keine Wahl getroffen wurde, folgt das Panel der QGIS-Sprache: Italienisch, wenn QGIS auf Italienisch läuft, in allen anderen Fällen Englisch – also auch bei deutschem QGIS.

---

## Benutzeroberfläche

Das Panel enthält von oben nach unten: die Kopfzeile mit den Schaltflächen, die Gruppe **«Eingabedaten (von allen Registerkarten verwendet)»** (*Input data (used by all tabs)*), die **6 Registerkarten** der Analyse und, während einer Berechnung, den Fortschrittsbalken mit der Schaltfläche **«Abbrechen»** (*Cancel*).

### Kopfzeile

| Element | Funktion |
|---------|----------|
| **«Beispieldaten laden»** (*Load example data*) | Öffnet die Liste der mit dem Modul gelieferten Testdatensätze (siehe Registerkarte Daten) |
| **«Tutorial»** (*Tutorial*) | Öffnet die integrierte GeoArchaeo-Anleitung auf Italienisch oder Englisch, die sich auch im Browser öffnen lässt |
| **«Sprache:»** (*Language:*) | Auswahlliste Italiano / English |

### Eingabedaten

In der Gruppe **«Eingabedaten (von allen Registerkarten verwendet)»** (*Input data (used by all tabs)*) wählt man nur einmal:

- **«Punktlayer:»** (*Point layer:*): einen Vektor-Punktlayer des Projekts
- **«Wertefeld (numerisch):»** (*Value field (numeric):*): das zu analysierende Feld (die Liste zeigt nur numerische Felder)

Darunter zeigt eine Zusammenfassung die gültigen Punkte von der Gesamtzahl, das KBS (CRS) und die Ausdehnung des Layers, zum Beispiel «500 gültige Punkte von 500 · CRS EPSG:32633 · …» (*500 valid points of 500 · CRS EPSG:32633 · …*). Punkte ohne Wert (NULL oder nicht numerischer Text) zählen nicht als gültig. Die Zusammenfassung warnt außerdem, wenn das Projekt keine Punktlayer enthält, wenn der Layer keine numerischen Felder hat oder wenn das KBS geographisch ist (Grad).

Beim Wechsel des Layers schlägt das Panel außerdem die maximale Distanz des Variogramms und die Zellengröße des Krigings vor und wählt den Layer in der Registerkarte Muster (ML) vor, sofern dort noch nichts ausgewählt ist.

### Die sechs Registerkarten

| Registerkarte | Funktion | Ergebnis |
|---------------|----------|----------|
| **Daten** (*Data*) | Deskriptive Statistik des Feldes | Statistiktabelle, Histogramm mit Boxplot |
| **Variogramm** (*Variogram*) | Räumliche Struktur der Werte | Nugget, Sill, Range, Anisotropie, Diagramm |
| **Kriging** (*Kriging*) | Interpolation auf einem regelmäßigen Gitter | Schätz- und Unsicherheitsraster, Kreuzvalidierung |
| **Muster (ML)** (*Patterns (ML)*) | Gruppen und Anomalien mit maschinellem Lernen | Punktlayer mit der Gruppenbezeichnung |
| **Stichprobenplanung** (*Sampling*) | Vorschlag neuer Probenahmepunkte | Punktlayer und Koordinatentabelle |
| **Bericht** (*Report*) | Zusammenstellung der Analysen der Sitzung | HTML-Datei mit interaktiven Diagrammen oder PDF |

<!-- IMAGE: Kopfzeile, Gruppe Eingabedaten und die sechs GeoArchaeo-Registerkarten -->
> **Abb. 3**: Die Kopfzeile, die Gruppe «Eingabedaten» und die sechs Registerkarten des GeoArchaeo-Panels

### Ergebnisse und Diagramme

Jede Registerkarte zeigt ihre Ergebnisse in einem **Feld** unter der Berechnungsschaltfläche, das sichtbar bleibt, bis die Analyse wiederholt wird, sowie das **Diagramm** im Panel:

- verfügt QGIS über QtWebEngine, ist das Plotly-Diagramm direkt im Panel interaktiv (Zoom, Werte beim Überfahren mit der Maus)
- andernfalls erscheint eine **statische Vorschau** mit dem Hinweis «Statische Vorschau (QtWebEngine in dieser QGIS-Installation nicht verfügbar).» (*Static preview (QtWebEngine not available in this QGIS installation).*)
- in beiden Fällen öffnet die Schaltfläche **«Interaktives Diagramm im Browser öffnen»** (*Open interactive chart in browser*) die interaktive Version im Webbrowser

Die Registerkarten Daten, Variogramm und Kriging enden mit einem Verweis auf den nächsten Schritt, zum Beispiel **«Nächster Schritt: Variogramm →»** (*Next step: Variogram →*).

### Laufende Analysen

Variogramm, Kriging, Mustererkennung und Stichprobenplanung werden in einem **separaten Thread** berechnet: QGIS bleibt bedienbar, und unten im Panel erscheinen der **Fortschrittsbalken** (beim Kriging in Prozent) und die Schaltfläche **«Abbrechen»** (*Cancel*). Es läuft immer nur eine Analyse; wird eine weitere gestartet, erscheint «Eine Analyse läuft bereits: warten Sie, bis sie fertig ist, oder brechen Sie sie ab.» (*An analysis is already running: wait for it to finish or cancel it.*)

---

## Registerkarte Daten

Die Registerkarte **Daten** (*Data*, «1. Explorative Analyse» / *1. Exploratory analysis*) beschreibt die Verteilung der Werte, bevor sie interpoliert werden.

### Statistik berechnen

1. In der Gruppe «Eingabedaten» den Punktlayer und das numerische Feld wählen
2. Die Registerkarte **Daten** öffnen
3. Auf **«Statistik berechnen»** (*Calculate statistics*) klicken

<!-- IMAGE: Registerkarte Daten mit Statistik und Histogramm -->
> **Abb. 4**: Die Registerkarte Daten mit der Statistiktabelle und dem Histogramm des gewählten Feldes

### Statistik und Interpretation

| Kennwert | Beschreibung |
|----------|--------------|
| **Anzahl der Werte** (*Number of values*), **Fehlende Werte** (*Missing values*) | Punkte mit gültigem Wert und ausgeschlossene Punkte (NULL oder nicht numerischer Text) |
| **Minimum**, **Maximum**, **Mittelwert** (*Mean*), **Median** | Spannweite und Lage der Werte |
| **Standardabweichung** (*Std. deviation*), **Variationskoeffizient** (*Coeff. of variation*) | Absolute und relative Streuung |
| **Erstes Quartil (Q1)**, **Drittes Quartil (Q3)** (*First/Third quartile*) | Grenzen der mittleren 50 % der Werte |
| **Schiefe** (*Skewness*), **Kurtosis** (*Kurtosis*) | Form der Verteilung |

Unter der Tabelle ergänzt das Panel eine Deutung in Worten:

- Schiefe größer als 1: rechtsschiefe Verteilung (wenige sehr hohe Werte); vor dem Kriging eine logarithmische Transformation erwägen, zum Beispiel durch ein neues Feld mit dem Feldrechner
- Schiefe kleiner als -1: linksschiefe Verteilung (wenige sehr niedrige Werte)
- sonst: annähernd symmetrische Verteilung, für das Kriging geeignet
- die Anzahl möglicher Ausreißer, d. h. Werte, die mehr als 3 Standardabweichungen vom Mittelwert entfernt sind

Das Diagramm zeigt das **Histogramm** der Werte mit einem **Boxplot** (in der statischen Vorschau nur das Histogramm).

### Beispieldaten

Die Schaltfläche **«Beispieldaten laden»** (*Load example data*) öffnet das Fenster «GeoArchaeo-Beispieldaten» (*GeoArchaeo example data*) mit den Datensätzen im Ordner `test_layers` des Moduls; der Pfad steht unter **«Ordner:»** (*Folder:*) und lässt sich mit **«Durchsuchen…»** (*Browse…*) ändern. GeoPackages und GeoJSON-Dateien sind bereits angehakt. CSV-Dateien erscheinen nur, wenn kein GeoPackage oder GeoJSON gleichen Namens existiert; sie müssen von Hand angehakt werden und werden als Textdatei mit Trennzeichen geladen (Felder `x` und `y`, EPSG:32633). Mit **OK** werden die Layer dem Projekt hinzugefügt, und der erste geladene Punktlayer wird zum Eingabelayer des Panels.

| Datensatz | Punkte | Wichtigste numerische Felder | Empfohlene Verwendung |
|-----------|--------|------------------------------|-----------------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Statistik, Variogramm, Kriging |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Wie `villa_ceramica` | Alle Registerkarten ausprobieren |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, Test mit einem großen Datensatz |
| `necropoli` (GeoPackage) | 120 Gräber | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN oder K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Kriging von Bodeneigenschaften |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Kriging der Funddichte, Stichprobenplanung |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variogramm und Kriging mit wenigen Punkten |
| `area_studio` (GeoJSON) | 1 Polygon | — | Untersuchungsgebiet für die Stichprobenplanung |

Unter den CSV-Dateien enthält `magnetometria_grid` (2500 Punkte, Feld `mag_nT`) simulierte magnetische Anomalien (zwei Mauern, eine Grube, ein Ofen). Alle Daten sind simuliert und liegen in EPSG:32633 (UTM 33N, Meter) vor. Das Polygon `area_studio` deckt das Gebiet von `ricognizione_survey`, `unita_scavo_ceramica` und `magnetometria_grid` ab, nicht das der übrigen Datensätze.

### Datenanforderungen

- Der Layer muss ein Vektorlayer mit **Punkten** sein (bei Multipunkten wird der erste Punkt verwendet)
- Das Feld muss **numerisch** sein: ein Textfeld mit Zahlen muss mit dem Feldrechner umgewandelt werden
- NULL- oder nicht numerische Werte werden automatisch ausgeschlossen und als fehlend gezählt
- Für Variogramm und Kriging sind mindestens **5 Punkte** mit gültigem Wert nötig (1 für die Statistik); ein zuverlässiges Variogramm braucht in der Regel einige Dutzend Punkte
- Empfohlen wird ein **projiziertes KBS** in Metern (z. B. UTM): bei einem geographischen KBS warnt die Zusammenfassung, und Variogramm und Kriging fragen nach einer Bestätigung

---

## Registerkarte Variogramm

Die Registerkarte **Variogramm** (*Variogram*, «2. Variogramm» / *2. Variogram*) misst, wie der Unterschied zwischen den Werten mit der Distanz wächst: Sie beschreibt die räumliche Struktur der Daten und steuert das Kriging.

### Was ist ein Variogramm?

Das Variogramm setzt die **Semivarianz** von Punktpaaren in Beziehung zur **Distanz** zwischen ihnen. Die Modellparameter sind:

| Parameter | Beschreibung |
|-----------|--------------|
| **Nugget** | Variabilität bei nahezu null Distanz: Messfehler und kleinräumige Variabilität |
| **Sill** | Gesamtvarianz, die das Modell erreicht (das "Plateau") |
| **Range** | Distanz, ab der die Werte nicht mehr korreliert sind; in GeoArchaeo die praktische Reichweite (95 % des Sill) |

### Berechnung des Variogramms

1. Die Registerkarte **Variogramm** öffnen
2. In der Gruppe **«Parameter»** (*Parameters*) **«Maximale Distanz:»** (*Maximum distance:*) prüfen: die Schaltfläche **«Auto»** schlägt etwa 1/3 der Diagonale der von den Punkten bedeckten Fläche vor (derselbe Wert wird beim Layerwechsel vorgeschlagen)
3. Das **«Theoretische Modell:»** (*Theoretical model:*) wählen
4. Bei Bedarf **«Anisotropie prüfen (Richtungsvariogramme)»** (*Check anisotropy (directional variograms)*) anhaken
5. Auf **«Variogramm berechnen»** (*Calculate variogram*) klicken

Die Punktpaare werden in **15 Distanzklassen** (Lags) zwischen null und der maximalen Distanz gruppiert; die Anzahl der Klassen lässt sich im Panel nicht ändern. Bei mehr als **3000 Punkten** wird das Variogramm aus einer Zufallsstichprobe von 3000 Punkten berechnet, weil die Zahl der Paare quadratisch mit der Punktzahl wächst. Das Modell wird mit der Methode der kleinsten Quadrate angepasst, gewichtet nach der Zahl der Paare je Klasse.

<!-- IMAGE: Registerkarte Variogramm mit Parametern und Ergebnissen -->
> **Abb. 5**: Die Registerkarte Variogramm mit den Parametern, dem theoretischen Modell und dem Ergebnisfeld

### Theoretische Modelle

| Modell | Verlauf | Wann verwenden |
|--------|---------|----------------|
| **«Sphärisch (empfohlen)»** (*Spherical (recommended)*) | Steigt bis zur Range und bleibt dann konstant | Am häufigsten: Funddichten, Verteilungen mit scharfen Grenzen |
| **«Exponentiell»** (*Exponential*) | Steigt nahe dem Ursprung schnell an und erreicht den Sill allmählich | Kontinuierlich abklingende Phänomene, z. B. chemische Elemente im Boden |
| **«Gaußsch»** (*Gaussian*) | Sehr glatt nahe dem Ursprung | Sehr "glatte" Phänomene (Oberflächen); mit Vorsicht verwenden |
| **«Matérn»** (*Matérn*) | Zwischen exponentiell und Gaußsch (ν = 1,5) | Flexible Alternative |

Faustregel: mit dem sphärischen Modell beginnen und den RMSE der Anpassung mit dem der anderen Modelle vergleichen. Das Kriging verwendet das **zuletzt** berechnete Variogramm: nach den Vergleichen das gewählte Modell erneut berechnen.

### Manuelle Parameter

Die standardmäßig deaktivierte Gruppe **«Manuelle Parameter (optional)»** (*Manual parameters (optional)*) erlaubt es, **«Nugget:»** (*Nugget:*), **«Sill (Gesamtvarianz):»** (*Sill (total variance):*) und **«Range (Korrelationsdistanz):»** (*Range (correlation distance):*) festzulegen. Ist die Gruppe aktiv, bleiben Werte ungleich null fest, und die auf «Auto» (null) belassenen werden geschätzt.

### Ergebnisse lesen

Das Ergebnisfeld zeigt:

- das Modell mit **Nugget**, **Sill**, **Range** (in Einheiten des KBS) und dem **RMSE** der Anpassung
- die Anzahl der Punktpaare und Distanzklassen, gegebenenfalls mit der verwendeten Stichprobe
- eine Deutung der Range: bis zu dieser Distanz sind die Werte räumlich korreliert, darüber beeinflussen sie sich nicht
- das Verhältnis Nugget/Sill: unter 25 % starke kleinräumige Kontinuität, bis 60 % mäßige Kontinuität, über 60 % hohe kleinräumige Variabilität oder Messfehler (das Kriging ist dann wenig aussagekräftig)

Das Diagramm zeigt die Punkte des experimentellen Variogramms (größer, wo mehr Paare vorliegen), die Modellkurve und die Linien für Nugget, Sill und Range.

<!-- IMAGE: Experimentelles Variogramm mit angepasstem Modell -->
> **Abb. 6**: Experimentelles Variogramm und sphärisches Modell mit den Linien für Nugget, Sill und Range

### Richtungsvariogramme (Anisotropie)

Ist **«Anisotropie prüfen (Richtungsvariogramme)»** (*Check anisotropy (directional variograms)*) angehakt, berechnet GeoArchaeo zusätzlich die Variogramme in den Richtungen **0°, 45°, 90° und 135°** (Winkel von Osten gegen den Uhrzeigersinn gemessen, Toleranz ±22,5°). Nugget und Sill sind die des Gesamtvariogramms; für jede Richtung wird die Range geschätzt.

- Übersteigt das Verhältnis zwischen größter und kleinster Range den Wert **2**, meldet das Feld die Anisotropie und die Hauptrichtung (z. B. entlang einer Mauer, einer Straße oder eines Hangs)
- Andernfalls meldet es «Keine relevante Anisotropie» (*No relevant anisotropy*) mit dem berechneten Verhältnis
- Bei zu wenigen Paaren je Richtung erscheint «Nicht genügend Paare für Richtungsvariogramme.» (*Not enough pairs for directional variograms.*)

Im interaktiven Diagramm sind die Richtungsvariogramme anfangs ausgeblendete Legendeneinträge: auf 0°, 45°, 90° oder 135° klicken, um sie anzuzeigen (in der statischen Vorschau werden sie immer gezeichnet). Das Kriging des Panels verwendet das richtungsunabhängige Modell: die Anisotropie dient der Interpretation.

---

## Registerkarte Kriging

Die Registerkarte **Kriging** (*Kriging*, «3. Gewöhnliches Kriging» / *3. Ordinary kriging*) interpoliert die Werte mithilfe des Variogramms auf einem regelmäßigen Gitter, erzeugt auch die Unsicherheitskarte und fügt die Raster dem Projekt hinzu.

### Gewöhnliches Kriging

Das Panel führt **gewöhnliches Kriging** (Ordinary Kriging: konstanter, aber unbekannter lokaler Mittelwert) aus, das für die meisten archäologischen Daten geeignet ist. Für jede Zelle verwendet es die **20 nächsten Punkte**, die mit einem KD-Baum gefunden werden; diese Zahl lässt sich im Panel nicht ändern. Co-Kriging, raumzeitliches Kriging und kachelweises Kriging für sehr große Datensätze gibt es nur als Processing-Algorithmen des eigenständigen GeoArchaeo-Plugins; in PyArchInit sind sie nicht verfügbar.

### Kriging ausführen

1. Die Registerkarte **Kriging** öffnen und die Statuszeile des Variogramms lesen (siehe unten); die Schaltfläche **«← Zum Variogramm»** (*← Go to Variogram*) führt zur vorherigen Registerkarte zurück
2. **«Zellengröße:»** (*Cell size:*) einstellen, also die Kantenlänge einer Zelle in Einheiten des KBS: das Panel schlägt etwa 100 Zellen auf der längeren Seite des Layers vor und zeigt darunter das resultierende Gitter («Gitter: … × … = … Zellen» / *Grid: … × … = … cells*)
3. **«Berechnetes Variogramm verwenden»** (*Use the calculated variogram*) angehakt lassen, um das Variogramm der vorherigen Registerkarte zu nutzen; ist die Option aus, wird das Variogramm automatisch geschätzt
4. **«Auch das Unsicherheitsraster erstellen (Standardabweichung)»** (*Also create the uncertainty raster (std. deviation)*) angehakt lassen, wenn die Unsicherheitskarte benötigt wird
5. Auf **«Kriging ausführen»** (*Run kriging*) klicken: der Fortschrittsbalken zeigt den Prozentsatz, **«Abbrechen»** (*Cancel*) beendet die Berechnung

Die Statuszeile kann lauten:

- «Variogramm verfügbar: …, Range … ✓» (*Variogram available: …, range … ✓*): das für denselben Layer und dasselbe Feld berechnete Variogramm wird verwendet
- «Kein Variogramm berechnet: es wird automatisch geschätzt (sphärisches Modell).» (*No variogram calculated: it will be estimated automatically (spherical model).*)
- «Das Variogramm wurde für einen anderen Layer/ein anderes Feld berechnet: es wird neu berechnet.» (*The variogram was calculated on another layer/field: it will be recalculated.*), ebenfalls mit automatischer Schätzung

> **Gitter**: Das Gitter deckt die Ausdehnung des Punktlayers ab und ist auf **500 Zellen pro Seite** begrenzt. Ist die gewählte Zellengröße zu fein, wird sie automatisch vergrößert, und die Gitterzeile weist darauf hin («minimale Zellengröße … (max. 500 Zellen pro Seite)» / *minimum cell size … (max 500 cells per side)*). Ab **40.000 Zellen** wird die Zeile orange, und beim Start fragt das Panel nach einer Bestätigung, weil die Berechnung einige Minuten dauern kann.

<!-- IMAGE: Kriging-Raster und Kennwerte der Kreuzvalidierung -->
> **Abb. 7**: Schätz- und Unsicherheitsraster auf der Karte mit dem Ergebnisfeld und der Kreuzvalidierung

### Kriging-Ergebnisse

Das Kriging fügt dem Projekt zwei GeoTIFF-Raster im KBS des Punktlayers hinzu:

| Layer | Inhalt | Stil |
|-------|--------|------|
| `Kriging_<Feld>` | Geschätzter Wert jeder Zelle | Farbverlauf von Blau über Gelb nach Rot; sichtbar |
| `Kriging_<Feld>_uncertainty` | Standardabweichung der Schätzung (Unsicherheit) | Verlauf von Hellgelb nach Rot; oben in der Layerliste eingefügt, aber ausgeblendet |

Ist das Panel auf Italienisch eingestellt, heißt das zweite Raster `Kriging_<Feld>_incertezza`. Die Dateien werden in einen **temporären Ordner** geschrieben: um sie zu behalten, über das Kontextmenü des Layers exportieren (**Exportieren**).

Das Ergebnisfeld fasst verwendete Punkte, Gittergröße, Zellengröße, Modell und Range zusammen; das Diagramm zeigt die Karte der geschätzten Werte und die Unsicherheitskarte mit den überlagerten Stichprobenpunkten.

### Leave-one-out-Kreuzvalidierung

Nach dem Kriging führt GeoArchaeo eine **Leave-one-out-Kreuzvalidierung** durch: Jeder Punkt wird entfernt und aus den übrigen neu geschätzt (bei größeren Datensätzen an höchstens 200 zufällig gewählten Punkten). Die Kennwerte erscheinen im Ergebnisfeld:

| Kennwert | Bedeutung | Wünschenswerter Wert |
|----------|-----------|----------------------|
| **RMSE** (*root mean squared error*) | Typischer Schätzfehler | So niedrig wie möglich, verglichen mit der Standardabweichung der Daten |
| **MAE** (*mean absolute error*) | Mittlerer absoluter Fehler | So niedrig wie möglich |
| **ME** (*mean error, bias*) | Systematische Über- oder Unterschätzung | Nahe 0 |
| **R²** (*explained variance*) | Vorhersagegüte | Ab 0,5 gut, unter 0,2 gering |
| **MSDR** (*standardized error*) | Realismus der geschätzten Unsicherheit | Etwa 1; über 1,5 Unsicherheit unterschätzt, unter 0,5 überschätzt |

Das Panel ergänzt ein Urteil in Worten über die Vorhersagegüte (gut, mäßig oder gering) und bei Bedarf über den MSDR.

> **Hinweis**: Das Kriging läuft in einem **Hintergrund-Thread**, sodass die QGIS-Oberfläche während der Berechnung benutzbar bleibt; der Fortschrittsbalken zeigt den Verarbeitungsstatus an.

---

## Registerkarte Muster (ML)

Die Registerkarte **Muster (ML)** (*Patterns (ML)*, «4. Mustererkennung (maschinelles Lernen)» / *4. Pattern recognition (machine learning)*) gruppiert die Punkte nach Lage und numerischen Attributen oder erkennt Anomalien und erstellt einen Layer mit der Bezeichnung jedes Punktes.

### Verfügbare Methoden

| Methode (Eintrag der Auswahlliste) | Funktionsweise | Parameter |
|------------------------------------|----------------|-----------|
| **«K-Means – Gruppen nach Ähnlichkeit»** (*K-Means – groups by similarity*) | Teilt die Punkte in K nach Lage und Attributen ähnliche Gruppen | **«Anzahl der Gruppen (0 = automatisch):»** (*Number of groups (0 = automatic):*); bei 0 wird die Anzahl nach der Punktzahl gewählt (2 bis 5) |
| **«DBSCAN – Gruppen nach Dichte (findet auch isolierte Punkte)»** (*DBSCAN – groups by density (also finds isolated points)*) | Findet Dichtegruppen, ohne ihre Anzahl festzulegen; isolierte Punkte bilden die Gruppe «Isoliert / Rauschen» (*Isolated / noise*) | Automatisch |
| **«Isolation Forest – Anomalieerkennung»** (*Isolation Forest – anomaly detection*) | Kennzeichnet etwa 10 % der Punkte, die sich am stärksten von den anderen unterscheiden, als «Anomalie» (*Anomaly*); die übrigen sind «Normal» (*Normal*) | Automatisch |

### Ausführung

1. Die Registerkarte **Muster (ML)** öffnen
2. In der Liste **«Zu analysierende Punktlayer (einer oder mehrere):»** (*Point layers to analyse (one or more):*) einen oder mehrere Punktlayer auswählen (ist nichts ausgewählt, wird der Eingabelayer vorausgewählt)
3. Die **«Methode:»** (*Method:*) wählen
4. Nur für K-Means **«Anzahl der Gruppen (0 = automatisch):»** einstellen
5. Auf **«Mustererkennung starten»** (*Run pattern recognition*) klicken

Analysiert werden die **X- und Y-Koordinaten** und **alle numerischen Felder** der ausgewählten Layer, standardisiert; fehlende Werte werden durch den Feldmittelwert ersetzt. Es wird also nicht nur das oben gewählte Wertefeld verwendet: alle numerischen Felder gehen ein, auch Kennungen und laufende Nummern, und wenn sie die Gruppen verfälschen, analysiert man besser eine Kopie des Layers mit den relevanten Feldern. Werden mehrere Layer zusammen analysiert, sollten sie dieselben numerischen Felder in derselben Reihenfolge und dasselbe KBS haben (der neue Layer verwendet das KBS des ersten ausgewählten Layers).

<!-- IMAGE: Registerkarte Muster (ML) mit dem Gruppen-Layer -->
> **Abb. 8**: Die Registerkarte Muster (ML) mit dem Gruppendiagramm und dem Layer `ML_groups` auf der Karte

### Ergebnisse

- Das Ergebnisfeld nennt die Methode, die Anzahl der Gruppen und wie viele Punkte auf jede entfallen (z. B. «Gruppe A (n=42)» / *Group A (n=42)*)
- Das Diagramm zeigt die Punkte in der Ebene der ersten beiden Hauptkomponenten (PC1, PC2) der Variablen, nach Gruppen eingefärbt
- Es wird ein temporärer Punktlayer `ML_groups` (K-Means, DBSCAN) oder `ML_anomalies` (Isolation Forest) mit kategorisierter Legende erstellt: grau für isolierte Punkte, rot und größer für Anomalien; mit italienischem Panel heißen die Layer `Gruppi_ML` und `Anomalie_ML`

| Feld | Inhalt |
|------|--------|
| `cluster_id` | Gruppennummer (-1 = isoliert bei DBSCAN; 1 = Anomalie und 0 = normal bei Isolation Forest) |
| `cluster_name` | Lesbarer Name, z. B. «Group A (n=42)», «Isolated / noise (n=5)», «Anomaly (n=12)» |
| `cluster_size` | Anzahl der Punkte der Gruppe |
| `method` | Verwendete Methode |
| `x_coord`, `y_coord` | Koordinaten des Punktes |

### Überwachte Klassifikation

Unter der Methode weist das Panel darauf hin, dass sich die überwachte Klassifikation (Random Forest mit einem Feld bekannter Klassen) unter **Processing → GeoArchaeo** befindet. Dieser Algorithmus gehört zum eigenständigen GeoArchaeo-Plugin: In PyArchInit wird der Processing-Provider von GeoArchaeo nicht registriert, daher ist Random Forest nicht verfügbar. Dafür wird das separate GeoArchaeo-Plugin benötigt.

---

## Registerkarte Stichprobenplanung

Die Registerkarte **Stichprobenplanung** (*Sampling*, «5. Neue Probenahmestellen» / *5. New sampling locations*) schlägt ausgehend von den vorhandenen Punkten vor, wo künftig beprobt oder gegraben werden soll, und erstellt einen Layer mit den vorgeschlagenen Punkten.

### Auswahlkriterien

| Kriterium (Eintrag der Auswahlliste) | Wie die Punkte gewählt werden | Wann verwenden |
|--------------------------------------|-------------------------------|----------------|
| **«Abdeckung (Maximin)»** (*Coverage (maximin)*) | Jeder neue Punkt liegt so weit wie möglich von allen anderen entfernt | Lücken gleichmäßig füllen |
| **«Unsicherheitsreduktion (Kriging-Varianz)»** (*Uncertainty reduction (kriging variance)*) | Jeder neue Punkt kommt dorthin, wo die Kriging-Varianz am größten ist | Den Kriging-Fehler dort verringern, wo er am größten ist |
| **«Geschichtetes Gitter»** (*Stratified grid*) | Eine Position pro Zelle eines regelmäßigen Gitters mit leichter zufälliger Verschiebung | Regelmäßige Abdeckung eines festgelegten Gebiets |
| **«Adaptiv (dünner besetzte Bereiche)»** (*Adaptive (sparser areas)*) | Zufallsauswahl mit höherer Wahrscheinlichkeit dort, wo es wenige Punkte gibt | Wenig beprobte Zonen bevorzugen und dabei eine Zufallskomponente behalten |

Das Kriterium «Unsicherheitsreduktion» verwendet das berechnete Variogramm, wenn es denselben Layer und dasselbe Feld betrifft und in der Registerkarte Kriging «Berechnetes Variogramm verwenden» angehakt ist; andernfalls verwendet es ein allgemeines Modell auf Grundlage des typischen Punktabstands.

### Stichprobe planen

1. **«Vorhandene Punkte:»** (*Existing points:*) prüfen: es ist der oben in der Gruppe «Eingabedaten» gewählte Layer (für die Stichprobenplanung wird das numerische Feld nicht benötigt)
2. Optional: unter **«Untersuchungsgebiet (Polygon, optional):»** (*Study area (polygon, optional):*) einen Polygonlayer wählen; alle seine Polygone werden vereinigt und in das KBS der Punkte umprojiziert, auch wenn der Layer in einem anderen KBS vorliegt
3. **«Vorzuschlagende neue Punkte:»** (*New points to propose:*) einstellen (1 bis 500, Standard 10)
4. Das **«Kriterium:»** (*Criterion:*) wählen: unter der Auswahlliste erscheint seine Beschreibung
5. Auf **«Neue Punkte berechnen»** (*Calculate new points*) klicken

Ohne Untersuchungsgebiet werden die Punkte im Rechteck gesucht, das die vorhandenen Punkte umschließt, auf jeder Seite um 20 % erweitert.

<!-- IMAGE: Vorgeschlagene neue Probenahmepunkte -->
> **Abb. 9**: Die neuen Probenahmepunkte (gelbe Sterne), vorgeschlagen innerhalb des Untersuchungsgebiets

### Ergebnisse der Stichprobenplanung

- Das Ergebnisfeld gibt an, wie viele Punkte mit welchem Kriterium vorgeschlagen wurden; darunter listet die Tabelle «Koordinaten der vorgeschlagenen Punkte:» (*Coordinates of the proposed points:*) Nummer, X und Y auf
- Es wird der temporäre Punktlayer `New_sampling_points` erstellt (`Nuovi_punti_campionamento` mit italienischem Panel), mit gelbem Sternsymbol und den Feldern `point_id`, `x_coord`, `y_coord` und `type` (Wert `suggested`)

---

## Registerkarte Bericht

Die Registerkarte **Bericht** (*Report*, «6. Bericht» / *6. Report*) fasst die in dieser Sitzung durchgeführten Analysen in einem Dokument zusammen: Statistik, interaktive Diagramme, Parameter und Validierung.

### Berichtsinhalt

In der Gruppe **«Einzuschließende Abschnitte»** (*Sections to include*) ist jeder Abschnitt als «verfügbar» (*available*) oder «noch nicht berechnet» (*not yet calculated*) gekennzeichnet; noch nicht berechnete Abschnitte lassen sich nicht auswählen.

| Abschnitt | Inhalt |
|-----------|--------|
| **Deskriptive Statistik** (*Descriptive statistics*) | Layer und Feld, Statistiktabelle mit der Deutung in Worten, Histogramm |
| **Variogramm** (*Variogram*) | Modell, Nugget, Sill, Range, RMSE, maximale Distanz, Interpretation, Diagramm |
| **Kriging und Kreuzvalidierung** (*Kriging and cross-validation*) | Methode, Zellengröße, Gittergröße, Kennwerte der Kreuzvalidierung, Diagramm |
| **Mustererkennung** (*Pattern recognition*) | Analysierte Layer, Gruppen mit Punktzahl, Diagramm |
| **Neue Probenahmestellen** (*New sampling locations*) | Kriterium, Layer, Koordinatentabelle |

Jeder Abschnitt enthält die **letzte** Analyse seiner Art aus der Sitzung.

### Bericht erstellen

1. Die gewünschten Analysen in den anderen Registerkarten ausführen
2. Die Registerkarte **Bericht** öffnen und die gewünschten Abschnitte angehakt lassen (standardmäßig sind sie angehakt)
3. Auf **«HTML-Bericht speichern»** (*Save HTML report*) oder **«PDF-Bericht speichern»** (*Save PDF report*) klicken und den Dateinamen wählen

Beim Speichern zeigt das Panel außerdem eine Vorschau des Berichts ohne Diagramme; der Hinweis «Vorschau: Die interaktiven Diagramme sind in der gespeicherten HTML-Datei enthalten.» (*Preview: the interactive charts are included in the saved HTML file.*) erinnert daran, wo sie zu finden sind.

<!-- IMAGE: HTML-Bericht von GeoArchaeo im Browser -->
> **Abb. 10**: Ein HTML-Bericht von GeoArchaeo mit interaktiven Diagrammen, im Browser geöffnet

### Export

| Format | Inhalt | Hinweise |
|--------|--------|----------|
| **HTML** (`geoarchaeo_report.html`) | Text, Tabellen und **interaktive Diagramme** | Die Datei ist eigenständig (die Diagrammbibliothek ist eingebettet, sie funktioniert auch offline) und öffnet sich sofort im Browser |
| **PDF** (`geoarchaeo_report.pdf`) | Text und Tabellen, **ohne Diagramme** | Lässt sich das PDF nicht erstellen, den HTML-Bericht speichern und im Browser als PDF drucken |

Wurde noch keine Analyse ausgeführt, erscheint «Keine Analyse verfügbar: führen Sie zuerst mindestens eine Analyse aus.» (*No analysis available: run at least one analysis first.*); ist kein Abschnitt angehakt, «Wählen Sie mindestens einen Abschnitt» (*Select at least one section*).

---

## Operativer Arbeitsablauf

Ein vollständiges Beispiel mit den Beispieldaten des Moduls (Panel auf Englisch).

### Schritt 1: Datenvorbereitung

1. GeoArchaeo über die PyArchInit-Werkzeugleiste öffnen
2. Auf **«Beispieldaten laden»** (*Load example data*) klicken und mit **OK** bestätigen (GeoPackages und GeoJSON-Dateien werden geladen)
3. In der Gruppe «Eingabedaten» den Layer `villa_ceramica` und das Feld `ceramic_count` wählen
4. Die Zusammenfassung prüfen: 500 gültige Punkte von 500, CRS EPSG:32633

### Schritt 2: Datenexploration

1. Registerkarte **Daten** → **«Statistik berechnen»** (*Calculate statistics*)
2. Schiefe und Ausreißer lesen; bei starker Rechtsschiefe eine logarithmische Transformation erwägen

### Schritt 3: Variogramm-Analyse

1. Registerkarte **Variogramm** → **«Auto»** für die maximale Distanz, Modell **«Sphärisch (empfohlen)»** (*Spherical (recommended)*) → **«Variogramm berechnen»** (*Calculate variogram*)
2. Mit **«Exponentiell»** (*Exponential*) wiederholen und den RMSE der Anpassung vergleichen
3. Optional: mit **«Anisotropie prüfen (Richtungsvariogramme)»** erneut berechnen
4. Zuletzt das gewählte Modell erneut berechnen und Nugget, Sill und Range notieren

### Schritt 4: Interpolation

1. Registerkarte **Kriging**: die Zeile «Variogramm verfügbar … ✓» (*Variogram available … ✓*) prüfen
2. Die vorgeschlagene Zellengröße beibehalten oder 1 (Meter) einstellen
3. **«Kriging ausführen»** (*Run kriging*)
4. Die Raster `Kriging_ceramic_count` und `Kriging_ceramic_count_uncertainty` sowie die Werte von R² und MSDR prüfen

### Schritt 5: Muster und Stichprobenplanung (optional)

1. Registerkarte **Muster (ML)**: in der Liste nur `necropoli` ausgewählt lassen, Methode DBSCAN → **«Mustererkennung starten»** (*Run pattern recognition*); der Layer `ML_groups` zeigt die Grabgruppen und die isolierten Punkte
2. Oben den Layer `ricognizione_survey` (Feld `densita_mq`) wählen; Registerkarte **Stichprobenplanung**: Untersuchungsgebiet `area_studio`, 10 Punkte, Kriterium «Abdeckung (Maximin)» (*Coverage (maximin)*) → **«Neue Punkte berechnen»** (*Calculate new points*)

### Schritt 6: Bericht

1. Registerkarte **Bericht**: die verfügbaren Abschnitte angehakt lassen
2. **«HTML-Bericht speichern»** (*Save HTML report*): der Bericht öffnet sich im Browser mit den interaktiven Diagrammen
3. Die Raster und temporären Layer exportieren, die erhalten bleiben sollen

---

## Fehlerbehebung

### Häufige Probleme

| Problem | Ursache | Lösung |
|---------|---------|--------|
| «Kein Punktlayer im Projekt…» (*No point layer in the project: load one or use the example data.*) | Das Projekt enthält keine Punktlayer | Einen Punktlayer hinzufügen oder **«Beispieldaten laden»** verwenden |
| «Der Layer hat keine numerischen Felder…» (*The layer has no numeric fields…*) | Das zu analysierende Feld ist ein Textfeld | Mit dem Feldrechner in eine Zahl umwandeln |
| «Mindestens 5 Punkte mit gültigem Wert sind erforderlich…» (*At least 5 points with a valid value are required (found …)*) | Zu viele NULL- oder nicht numerische Werte | Die Attributtabelle prüfen oder ein anderes Feld wählen |
| Warnung «geographisches KBS (Grad)» (*geographic CRS (degrees)*) | Der Layer ist nicht in einem projizierten KBS | Den Layer umprojizieren, z. B. nach UTM, und die Analyse wiederholen |
| Fehler «No point pairs within the maximum distance…» | Maximale Distanz des Variogramms zu klein | **«Maximale Distanz:»** erhöhen oder **«Auto»** verwenden |
| «Nicht genügend Paare für Richtungsvariogramme.» (*Not enough pairs for directional variograms.*) | Zu wenige Paare je Richtung | Die maximale Distanz erhöhen oder auf die Anisotropieprüfung verzichten |
| Langsames Kriging, Bestätigungsfrage oder «Speicher reicht nicht aus: Zellengröße erhöhen.» (*Out of memory: increase the cell size.*) | Gitter mit zu vielen Zellen | **«Zellengröße:»** erhöhen |
| Niedriges R² in der Kreuzvalidierung | Geringe räumliche Korrelation oder zu viel Rauschen | Die Karte nur als Anhaltspunkt betrachten und das Unsicherheitsraster prüfen |
| DBSCAN stellt fast alle Punkte in «Isoliert / Rauschen» (*Isolated / noise*) | Gleichmäßige Dichte oder zu viele Variablen | K-Means versuchen oder die numerischen Felder reduzieren |
| «Machine Learning features not available. Please install scikit-learn.» | scikit-learn fehlt | scikit-learn in der Python-Umgebung von QGIS installieren |
| «Plotly visualization not available. Please install plotly.» | Plotly fehlt | plotly in der Python-Umgebung von QGIS installieren |
| Diagramm nur als statisches Bild | QtWebEngine nicht verfügbar | **«Interaktives Diagramm im Browser öffnen»** (*Open interactive chart in browser*) verwenden |
| «PDF kann nicht erstellt werden…» (*Cannot create the PDF…*) | Fehler beim PDF-Druck | Den HTML-Bericht speichern und im Browser drucken |
| Panel nicht sichtbar | Panel geschlossen | Über die Werkzeugleiste oder das Menü pyArchInit wieder öffnen: die Ergebnisse der Sitzung sind noch vorhanden |

### Häufige Fehlermeldungen

- **«Eine Analyse läuft bereits…»** (*An analysis is already running: wait for it to finish or cancel it.*): das Ende der Berechnung abwarten oder «Abbrechen» drücken
- **«Analyse abgebrochen»** (*Analysis cancelled*): die Analyse wurde mit «Abbrechen» beendet und hat keine Ergebnisse geliefert
- **«Wählen Sie mindestens einen Layer»** (*Select at least one layer*, Registerkarte Muster): mindestens einen Layer in der Liste auswählen
- **«Wählen Sie den Layer der vorhandenen Punkte (oben)»** (*Select the existing points layer (above)*, Registerkarte Stichprobenplanung): den Layer in der Gruppe «Eingabedaten» wählen
- **«Wählen Sie einen Punktlayer und ein numerisches Feld (oben im Panel)»** (*Select a point layer and a numeric field (at the top of the panel)*): die Auswahl in der Gruppe «Eingabedaten» vervollständigen

### Leistung

- Die Analysen laufen in einem **Hintergrund-Thread**: QGIS bleibt bedienbar, und die Berechnung kann abgebrochen werden
- Das Variogramm verwendet höchstens 3000 Punkte (Zufallsstichprobe), die Kreuzvalidierung höchstens 200
- Das Kriging verwendet für jede Zelle die 20 nächsten Punkte: die Rechenzeit hängt vor allem von der Zahl der Zellen ab
- Das Gitter ist auf 500 × 500 Zellen begrenzt; ab 40.000 Zellen fragt das Panel nach einer Bestätigung
- Bei großen Datensätzen (z. B. den 4800 Punkten von `geofisica_survey`) die Zellengröße erhöhen

---

## Technische Hinweise

### Version und Herkunft

- Das Modul `modules/geoarchaeo/` entspricht **GeoArchaeo 1.3.1**, dem eigenständigen Plugin von Enzo Cocca (github.com/enzococca/GeoArchaeo)
- In PyArchInit ist nur das Panel integriert: der Processing-Provider von GeoArchaeo (Co-Kriging, raumzeitliches Kriging, kachelweises Kriging, Kompositionsanalyse, Random Forest) wird **nicht** registriert
- Das Modul ist mit QGIS 3 (Qt5) und QGIS 4 (Qt6) kompatibel

### Abhängigkeiten

| Bibliothek | Verwendung |
|------------|------------|
| **NumPy** | Numerische Berechnungen |
| **SciPy** | Anpassung der Variogrammmodelle, Nachbarsuche (KD-Baum), Statistik |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, Hauptkomponenten (für die Registerkarte Muster erforderlich) |
| **Plotly** | Interaktive Diagramme im Panel und im HTML-Bericht |
| **Matplotlib** | Statische Diagrammvorschau, wenn QtWebEngine fehlt |
| **QtWebEngine** (optional) | Interaktive Diagramme direkt im Panel |
| **threadpoolctl** (optional) | Begrenzt die Rechen-Threads während der Hintergrundanalysen |
| **GDAL** | Schreiben der GeoTIFF-Raster (in QGIS enthalten) |

### Koordinatenbezugssysteme

- Distanzen (maximale Distanz, Range, Zellengröße) werden in den **Einheiten des KBS des Punktlayers** angegeben
- Ein **projiziertes KBS** in Metern verwenden: bei einem geographischen KBS warnt die Zusammenfassung, und Variogramm und Kriging fragen nach einer Bestätigung
- Kriging-Raster und erzeugte Layer verwenden das KBS des Punktlayers (in der Registerkarte Muster das des ersten ausgewählten Layers)
- Das Untersuchungsgebiet wird automatisch in das KBS der Punkte umprojiziert

### Erzeugte Layer und Dateien

| Ergebnis | Typ | Speicherort |
|----------|-----|-------------|
| `Kriging_<Feld>`, `Kriging_<Feld>_uncertainty` | GeoTIFF-Raster (LZW-Kompression) | Temporärer Ordner des Systems |
| `ML_groups` / `ML_anomalies` | Temporärer Punktlayer (im Speicher) | Nur im geöffneten Projekt |
| `New_sampling_points` | Temporärer Punktlayer (im Speicher) | Nur im geöffneten Projekt |
| Bericht | HTML oder PDF | Beim Speichern gewählter Pfad |

Raster und temporäre Layer müssen exportiert werden (Kontextmenü des Layers → **Exportieren**), damit sie beim Schließen des Projekts nicht verloren gehen. Die Layernamen folgen der Sprache des Panels zum Zeitpunkt der Berechnung.

### Einstellungen

- Die Sprache des Panels wird in den QGIS-Einstellungen gespeichert (Schlüssel `GeoArchaeo/language`)
- Die Ergebnisse bleiben im Speicher, solange QGIS geöffnet ist: das Schließen des Panels löscht sie nicht

---

> **Hinweis**: GeoArchaeo wird ständig weiterentwickelt. Um Fehler zu melden oder Verbesserungen vorzuschlagen, das Issue-Tracking-System des PyArchInit-Projekts auf GitHub verwenden.
