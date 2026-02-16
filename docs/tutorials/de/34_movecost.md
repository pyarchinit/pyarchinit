# PyArchInit - MoveCost - Wegkostenanalyse

## Inhaltsverzeichnis

1. [Einfuehrung](#einfuehrung)
2. [Zugriff auf das Werkzeug](#zugriff-auf-das-werkzeug)
3. [Voraussetzungen](#voraussetzungen)
4. [Benutzeroberflaeche](#benutzeroberflaeche)
5. [Registerkarte Algorithmen](#registerkarte-algorithmen)
6. [Registerkarte Ergebnisse](#registerkarte-ergebnisse)
7. [Registerkarte Export](#registerkarte-export)
8. [Registerkarte Einstellungen](#registerkarte-einstellungen)
9. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
10. [Fehlerbehebung](#fehlerbehebung)
11. [Technische Hinweise](#technische-hinweise)

---

## Einfuehrung

**MoveCost** ist ein eigenstaendiges PyArchInit-Werkzeug fuer die Wegkostenanalyse (Least-Cost Path Analysis, LCPA) basierend auf R-Skripten. Die Wegkostenanalyse ist eine grundlegende Methodik in der Landschaftsarchaeologie, die es ermoeglicht, die wahrscheinlichsten Routen zwischen Standorten zu modellieren, wobei die Gelaendetopographie und der energetische Bewegungsaufwand beruecksichtigt werden.

### Geschichte

Zuvor war die MoveCost-Funktionalitaet direkt in das Fundstellen-Formular (Site form) von PyArchInit eingebettet. Ab der aktuellen Version wurde MoveCost als **eigenstaendiges Analysewerkzeug** extrahiert, zugaenglich ueber einen dedizierten QDialog. Diese Trennung bietet mehrere Vorteile:

- **Dedizierte Oberflaeche**: Ein Dialog mit 4 Registerkarten, organisiert nach Funktion
- **Bessere Organisation**: Algorithmen, Ergebnisse, Export und Einstellungen klar getrennt
- **Schneller Zugriff**: Verfuegbar ueber die Werkzeugleiste ohne das Fundstellen-Formular zu oeffnen
- **Erweiterbarkeit**: Modulare Struktur, die das Hinzufuegen neuer Algorithmen erleichtert

### Was ist eine Wegkostenanalyse?

Die Wegkostenanalyse berechnet den optimalen Pfad zwischen zwei oder mehr Punkten auf einer Kostenoberflaeche, die aus einem digitalen Gelaendemodell (DGM) abgeleitet wird. Die Bewegungskosten haengen von der Gelaendeneigung ab und werden mit anisotropen Kostenfunktionen berechnet, die die Bewegungsrichtung (bergauf vs. bergab) beruecksichtigen.

<!-- IMAGE: Beispiel eines Wegkostenpfades auf DGM -->
> **Abb. 1**: Beispiel eines berechneten Wegkostenpfades auf einem digitalen Gelaendemodell

---

## Zugriff auf das Werkzeug

### Ueber die Werkzeugleiste

1. Den **Analysewerkzeuge**-Dropdown-Button in der PyArchInit-Werkzeugleiste finden -- er hat ein Diagramm-/Analyse-Symbol
2. Auf den Dropdown-Pfeil klicken
3. **MoveCost** aus dem Menue auswaehlen

<!-- IMAGE: Analysewerkzeuge-Button in der Werkzeugleiste -->
> **Abb. 2**: Der Analysewerkzeuge-Button in der PyArchInit-Werkzeugleiste mit geoeffnetem Dropdown-Menue

### Dialogfenster

Beim Klicken oeffnet sich ein **modaler QDialog** mit vier Registerkarten:

```
+-----------------------------------------------------------+
|  MoveCost - Wegkostenanalyse                               |
+-----------------------------------------------------------+
| [Algorithmen] | [Ergebnisse] | [Export] | [Einstellungen] |
+-----------------------------------------------------------+
|                                                           |
|              (Inhalt der aktiven Registerkarte)             |
|                                                           |
+-----------------------------------------------------------+
|                              [Schliessen]                  |
+-----------------------------------------------------------+
```

---

## Voraussetzungen

Vor der Verwendung von MoveCost muessen die folgenden Komponenten installiert und konfiguriert sein:

### 1. R (Statistische Programmiersprache)

| Anforderung | Detail |
|-------------|--------|
| **Software** | R (Version >= 4.0 empfohlen) |
| **Download** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Ueberpruefung** | Terminal oeffnen und `R --version` eingeben |

### 2. R-Paket `movecost`

Das Paket innerhalb von R installieren:

```r
install.packages("movecost")
```

Haupt-Abhaengigkeiten werden automatisch installiert: `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Anforderung | Detail |
|-------------|--------|
| **Plugin** | Processing R Provider |
| **Installation** | QGIS > Erweiterungen > Erweiterungen verwalten und installieren > "Processing R Provider" suchen |
| **Konfiguration** | Verarbeitungseinstellungen > Sketcher > R > R-Ordnerpfad |

### 4. Eingabedaten

- **DGM/DEM**: Ein digitales Gelaendemodell-Raster fuer das Untersuchungsgebiet
- **Punktlayer**: Ursprungs- und Zielpunkte fuer die Analyse
- **Polygonlayer**: (Optional) Fuer die "by polygon"-Algorithmusvarianten

### Schnelle Voraussetzungs-Checkliste

```
+-------------------------------------------+
| Voraussetzungen-Checkliste                 |
+-------------------------------------------+
| [x] R installiert und im PATH            |
| [x] movecost-Paket in R installiert      |
| [x] Processing R Provider aktiv in QGIS  |
| [x] DGM im QGIS-Projekt geladen          |
| [x] Punktlayer mit Urspruengen/Zielen     |
+-------------------------------------------+
```

---

## Benutzeroberflaeche

Der MoveCost-Dialog ist in **4 Registerkarten** (Tabs) unterteilt, jede mit einer spezifischen Funktion.

### Registerkarten-Uebersicht

| Registerkarte | Symbol | Funktion |
|---------------|--------|----------|
| **Algorithmen** | Zahnrad | Die 14 Analyse-Algorithmen auswaehlen und starten |
| **Ergebnisse** | Diagramm | Kostenstatistiken und R-Plots anzeigen |
| **Export** | Diskette | Ergebnisse als CSV, PDF oder HTML exportieren |
| **Einstellungen** | Schraubenschluessel | R-Skripte, Sprache, Layer-Organisation konfigurieren |

<!-- IMAGE: MoveCost-Dialog-Uebersicht mit 4 Registerkarten -->
> **Abb. 3**: Der MoveCost-Dialog mit allen vier Registerkarten

---

## Registerkarte Algorithmen

Die Registerkarte **Algorithmen** ist das Herzstk des MoveCost-Werkzeugs. Sie enthaelt **14 Algorithmen** basierend auf R-Skripten, organisiert in **3 Funktionsgruppen**.

### Gruppe 1: Kostenoberflaeche und Pfade

Algorithmen zur Berechnung akkumulierter Kostenoberflaechen und Wegkostenpfade.

| Algorithmus | Beschreibung |
|-------------|-------------|
| **movecost** | Berechnet die akkumulierte anisotrope neigungsabhaengige Bewegungskostenoberflaeche und Wegkostenpfade von einem Punktursprung |
| **movecost by polygon** | Wie oben, aber unter Verwendung eines Polygonbereichs zur Definition der DGM-Ausdehnung |
| **movebound** | Berechnet neigungsabhaengige Gehkosten-Grenzen um Punktstandorte |
| **movebound by polygon** | Wie oben, aber unter Verwendung eines Polygons |

### Gruppe 2: Korridor- und Netzwerkanalyse

Algorithmen fuer die Kostenkorridoranalyse und optimale Pfadnetzwerke.

| Algorithmus | Beschreibung |
|-------------|-------------|
| **movecorr** | Berechnet den Korridor mit den geringsten Kosten zwischen Punktstandorten |
| **movecorr by polygon** | Wie oben, aber unter Verwendung eines Polygons |
| **movealloc** | Berechnet die neigungsabhaengige Gehkosten-Zuordnung zu Urspruengen |
| **movealloc by polygon** | Wie oben, aber unter Verwendung eines Polygons |
| **movenetw** | Berechnet das Wegkostenpfad-Netzwerk zwischen mehreren Punkten |
| **movenetw by polygon** | Wie oben, aber unter Verwendung eines Polygons |

### Gruppe 3: Vergleich und Rangfolge

Algorithmen zum Vergleich von Kostenfunktionen und zur Rangfolge von Zielen.

| Algorithmus | Beschreibung |
|-------------|-------------|
| **movecomp** | Vergleicht Wegkostenpfade, die mit verschiedenen Kostenfunktionen generiert wurden |
| **movecomp by polygon** | Wie oben, aber unter Verwendung eines Polygons |
| **moverank** | Ordnet Ziele nach Gehkosten von einem Ursprung |
| **moverank by polygon** | Wie oben, aber unter Verwendung eines Polygons |

### Einen Algorithmus starten

1. Den gewuenschten Algorithmus aus der Liste auswaehlen
2. Die QGIS-Processing-Oberflaeche oeffnet sich mit algorithmus-spezifischen Parametern
3. Die Eingabeparameter konfigurieren:
   - **DGM/DEM**: Das Gelaenderaster auswaehlen
   - **Ursprungspunkt(e)**: Den Punktlayer auswaehlen
   - **Polygon** (bei "by polygon"-Variante): Das Untersuchungsgebiet auswaehlen
   - **Kostenfunktion**: Aus verfuegbaren Funktionen waehlen (Tobler, Minetti, usw.)
4. Auf **Ausfuehren** klicken
5. Ergebnisse werden automatisch zum QGIS-Projekt hinzugefuegt

<!-- IMAGE: Registerkarte Algorithmen mit 3 Gruppen -->
> **Abb. 4**: Die Registerkarte Algorithmen mit den drei hervorgehobenen Algorithmengruppen

<!-- IMAGE: Processing-Oberflaeche fuer einen movecost-Algorithmus -->
> **Abb. 5**: Die QGIS-Processing-Oberflaeche fuer den movecost-Algorithmus mit konfigurierten Parametern

### "By Polygon"-Varianten

Die "by polygon"-Varianten jedes Algorithmus ermoeglichen:
- **Begrenzung des Analysegebiets** auf eine bestimmte Region
- **Reduzierung der Berechnungszeit** durch Arbeit mit einem ausgeschnittenen DGM
- **Fokussierung der Analyse** auf ein archaeologisch relevantes Gebiet

---

## Registerkarte Ergebnisse

Die Registerkarte **Ergebnisse** ermoeglicht die Anzeige der Ergebnisse ausgefuehrter Analysen.

### Kostenzusammenfassung

Ein Textbereich (QTextEdit) zeigt zusammenfassende Statistiken der generierten Kostenlayer:

| Statistik | Beschreibung |
|-----------|-------------|
| **Minimum** | Minimaler Kostenwert in der Oberflaeche |
| **Maximum** | Maximaler Kostenwert in der Oberflaeche |
| **Mittelwert** | Durchschnittlicher Kostenwert |
| **Std.-Abweichung** | Standardabweichung der Kostenwerte |

```
+---------------------------------------------------+
| Kostenzusammenfassung                              |
+---------------------------------------------------+
| Layer: movecost_accumulated_cost                   |
| Minimum: 0.00                                      |
| Maximum: 15234.56                                  |
| Mittelwert: 4521.89                                |
| Std.-Abweichung: 2103.45                           |
|                                                    |
| Layer: movecost_back_link                          |
| Minimum: 0.00                                      |
| Maximum: 8.00                                      |
| Mittelwert: 4.12                                   |
+---------------------------------------------------+
```

### R-Plot-Betrachter

Der R-Plot-Betrachter zeigt den neuesten von R-Skripten generierten Plot:

| Funktion | Beschreibung |
|----------|-------------|
| **Automatische Anzeige** | Zeigt den neuesten R-Plot aus dem temporaeren Verzeichnis |
| **Aktualisieren** | Laedt den neuesten verfuegbaren Plot neu |
| **Speichern** | Speichert den aktuellen Plot als Bilddatei (PNG, JPG) |
| **Manuelle Auswahl** | Ermoeglicht das Oeffnen eines bestimmten R-Plots von beliebigem Standort |

<!-- IMAGE: Registerkarte Ergebnisse mit Kostenzusammenfassung und R-Plot -->
> **Abb. 6**: Die Registerkarte Ergebnisse mit Kostenstatistiken und einem R-Plot

### R-Plot-Speicherorte

R-Plots werden in temporaeren QGIS/R-Verzeichnissen gespeichert. Der Betrachter sucht automatisch in folgenden Verzeichnissen:

- Temporaeres QGIS-Processing-Verzeichnis
- Temporaeres R-Verzeichnis (`tempdir()`)
- Vom Benutzer angegebener Ausgabeordner

---

## Registerkarte Export

Die Registerkarte **Export** bietet drei Optionen zum Exportieren von Analyseergebnissen.

### Kostentabelle exportieren (CSV)

Exportiert Kostenlayer-Statistiken in eine CSV-Datei:

1. Auf **Kostentabelle exportieren** klicken
2. Dateispeicherort und -namen auswaehlen
3. Die CSV-Datei enthaelt: Layername, Minimum, Maximum, Mittelwert, Standardabweichung

| Spalte | Beschreibung |
|--------|-------------|
| `layer_name` | Name des Kostenlayers |
| `min_value` | Minimaler Wert |
| `max_value` | Maximaler Wert |
| `mean_value` | Mittelwert |
| `std_dev` | Standardabweichung |

### Bericht exportieren (PDF)

> **Hinweis**: Diese Funktion befindet sich derzeit in der Entwicklung (Stub). Sie wird in einer zukuenftigen Version verfuegbar sein.

### Bericht exportieren (HTML)

Generiert einen vollstaendigen, gestalteten HTML-Bericht, der Folgendes enthaelt:

- **Kopfzeile** mit Projekttitel und Datum
- **Verwendete Analyseparameter**
- **Layerstatistiken** im Tabellenformat
- **R-Plots** als eingebettete Bilder
- **Integriertes CSS-Styling** fuer professionelle Praesentation

1. Auf **Bericht exportieren (HTML)** klicken
2. Dateispeicherort und -namen auswaehlen
3. Der Bericht oeffnet sich automatisch im Standardbrowser

<!-- IMAGE: Beispiel eines exportierten HTML-Berichts -->
> **Abb. 7**: Ein Beispiel-HTML-Bericht, generiert von MoveCost mit Statistiken und Plots

---

## Registerkarte Einstellungen

Die Registerkarte **Einstellungen** ermoeglicht die Konfiguration des MoveCost-Werkzeugs.

### R-Skripte installieren

| Funktion | Beschreibung |
|----------|-------------|
| **R-Skripte installieren** | Kopiert movecost-R-Skripte in das QGIS-Processing-Verzeichnis |

Dieser Vorgang ist bei der **Ersteinrichtung** oder nach einem Plugin-Update erforderlich. Skripte werden in den Processing-R-Skript-Ordner kopiert:

```
{QGIS_HOME}/processing/rscripts/
```

### Sprachauswahl

MoveCost unterstuetzt **5 Sprachen** fuer die Oberflaeche:

| Sprache | Code |
|---------|------|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

Die ausgewaehlte Sprache gilt fuer:
- Beschriftungen der Dialogoberflaeche
- Status- und Fehlermeldungen
- Kopfzeilen der Ergebnistabellen

### Layer-Organisation

| Funktion | Beschreibung |
|----------|-------------|
| **Layer organisieren** | Automatische Organisation und Stilzuweisung fuer movecost-Ausgabelayer |

Diese Funktion:
1. Gruppiert Ausgabelayer in logische Gruppen im QGIS-Layer-Panel
2. Wendet vordefinierte Farbstile an (Farbrampen fuer Kostenoberflaechen)
3. Benennt Layer mit beschreibenden Namen um

### Dokumentation

| Funktion | Beschreibung |
|----------|-------------|
| **Hilfe** | Oeffnet die Inline-Werkzeug-Dokumentation |

<!-- IMAGE: Registerkarte Einstellungen mit allen Optionen -->
> **Abb. 8**: Die MoveCost-Registerkarte Einstellungen mit Konfigurationsoptionen

---

## Operativer Arbeitsablauf

### Schritt-fuer-Schritt-Beispiel: Berechnung eines Wegkostenpfades

Dieses Beispiel zeigt, wie ein Wegkostenpfad zwischen einer Siedlung und einer Wasserquelle berechnet wird.

### Schritt 1: Datenvorbereitung

```
1. Das DGM des Untersuchungsgebiets in das QGIS-Projekt laden
2. Einen Punktlayer erstellen mit:
   - Ursprungspunkt (Siedlung)
   - Zielpunkt(e) (Wasserquelle)
3. Sicherstellen, dass das Koordinatenreferenzsystem konsistent ist
```

### Schritt 2: Voraussetzungen pruefen

```
1. MoveCost ueber die Werkzeugleiste oeffnen
2. Zur Registerkarte Einstellungen wechseln
3. Auf "R-Skripte installieren" klicken (wenn erstmalig)
4. Ueberpruefen, dass keine Fehler gemeldet werden
```

### Schritt 3: Analyse ausfuehren

```
1. Zur Registerkarte Algorithmen wechseln
2. "movecost" aus Gruppe 1 auswaehlen
3. Im Processing-Fenster:
   - DGM: Gelaenderaster auswaehlen
   - Ursprung: Siedlungspunkt auswaehlen
   - Ziel: Wasserquellenpunkt auswaehlen
   - Kostenfunktion: Tobler (empfohlener Standard)
4. Auf Ausfuehren klicken
5. Auf den Abschluss der Verarbeitung warten
```

### Schritt 4: Ergebnisse analysieren

```
1. Zur Registerkarte Ergebnisse wechseln
2. Die Kostenzusammenfassung fuer Statistiken ueberpruefen
3. Den R-Plot zur Visualisierung untersuchen
4. Im QGIS-Canvas beobachten:
   - Die akkumulierte Kostenoberflaeche (farbiges Raster)
   - Den Wegkostenpfad (Vektorlinie)
```

### Schritt 5: Export

```
1. Zur Registerkarte Export wechseln
2. Die Kostentabelle als CSV fuer weitere Analysen exportieren
3. Den HTML-Bericht fuer die Dokumentation generieren
4. Den R-Plot aus der Registerkarte Ergebnisse speichern
```

### Schritt 6: Organisation

```
1. Zur Registerkarte Einstellungen zurueckkehren
2. Auf "Layer organisieren" klicken, um die Ergebnisse zu sortieren
3. Layer werden automatisch gruppiert und gestaltet
```

<!-- IMAGE: Vollstaendiger Arbeitsablauf mit annotierten Screenshots -->
> **Abb. 9**: Der vollstaendige Arbeitsablauf von der Datenvorbereitung bis zu den Endergebnissen

---

## Fehlerbehebung

### R nicht gefunden

**Symptom**: Fehlermeldung "R nicht gefunden" oder "R is not installed"

**Loesungen**:
1. Ueberpruefen, ob R installiert ist: Terminal oeffnen und `R --version` eingeben
2. Den R-Pfad in den Processing-Einstellungen pruefen:
   - **QGIS** > **Einstellungen** > **Optionen** > **Sketcher** > **Sketcher** > **R**
   - Den **R-Ordnerpfad** korrekt einstellen
3. Auf macOS kann R sich unter `/Library/Frameworks/R.framework/Resources/` befinden
4. Auf Windows typischerweise unter `C:\Program Files\R\R-4.x.x\`
5. Auf Linux mit `which R` ueberpruefen

### R-Skripte fehlen

**Symptom**: Algorithmen erscheinen nicht in der Processing-Werkzeugkiste

**Loesungen**:
1. MoveCost > Einstellungen > auf **R-Skripte installieren** klicken
2. QGIS nach der Installation der Skripte neu starten
3. Ueberpruefen, ob der Processing R Provider aktiv ist:
   - **QGIS** > **Erweiterungen** > **Erweiterungen verwalten und installieren** > "Processing R Provider" pruefen
4. Den R-Skript-Ordner pruefen: `{QGIS_HOME}/processing/rscripts/`

### R-Plots werden nicht angezeigt

**Symptom**: Die Registerkarte Ergebnisse zeigt keinen Plot an

**Loesungen**:
1. In der Registerkarte Ergebnisse auf **Aktualisieren** klicken
2. **Manuelle Auswahl** verwenden, um zum Plot-Ordner zu navigieren
3. Ueberpruefen, ob die Analyse erfolgreich abgeschlossen wurde
4. Die temporaeren Verzeichnisse pruefen:
   - macOS/Linux: `/tmp/` oder `$TMPDIR`
   - Windows: `%TEMP%`
5. Einige Algorithmen generieren moeglicherweise keine Plots

### movecost-Paket nicht in R installiert

**Symptom**: Fehler "there is no package called 'movecost'"

**Loesungen**:
1. R oder RStudio oeffnen
2. Ausfuehren: `install.packages("movecost")`
3. Ueberpruefen: `library(movecost)` -- sollte keine Fehler erzeugen
4. Bei Abhaengigkeitsproblemen: `install.packages("movecost", dependencies = TRUE)`

### Analyse sehr langsam

**Symptom**: Die Verarbeitung dauert sehr lange

**Loesungen**:
1. Die **"by polygon"**-Varianten verwenden, um das Berechnungsgebiet zu begrenzen
2. Die DGM-Aufloesung reduzieren (Resampling)
3. Die DGM-Dimensionen pruefen:
   - Sehr grosse DGMs (>10000x10000 Pixel) erfordern erhebliche Zeit
   - Das DGM vor der Analyse auf das Untersuchungsgebiet zuschneiden
4. Andere Anwendungen schliessen, um RAM freizugeben

### Projektions-/KBS-Fehler

**Symptom**: Inkonsistente Ergebnisse oder Koordinatenreferenzsystem-Fehler

**Loesungen**:
1. Sicherstellen, dass DGM und Punktlayer das **gleiche KBS** haben
2. Ein **projiziertes KBS** (metrisch) verwenden, kein geographisches
3. Empfohlene KBS: UTM (z.B. EPSG:32632 fuer Mittelitalien)
4. Layer bei Bedarf vor der Analyse umprojizieren

---

## Technische Hinweise

### Werkzeugarchitektur

MoveCost ist als eigenstaendiger **QDialog** (`MoveCostDialog`) implementiert, der:
- Mit dem QGIS Processing Framework zur Ausfuehrung von R-Algorithmen interagiert
- Ergebnisse aus im Projekt geladenen Layern liest
- Die R-Plot-Visualisierung ueber QLabel/QPixmap verwaltet
- HTML-Berichte mit vordefinierten Templates generiert

### Quelldateien

| Datei | Beschreibung |
|-------|-------------|
| `tabs/MoveCost.py` | Hauptdialog und Oberflaechenlogik |
| `gui/ui/MoveCost.ui` | Qt-Designer-Oberflaechenlayout |
| `resources/r_scripts/` | R-Skripte fuer movecost-Algorithmen |

### Unterstuetzte Kostenfunktionen

Das R-Paket `movecost` unterstuetzt mehrere anisotrope Kostenfunktionen:

| Funktion | Autor | Beschreibung |
|----------|-------|-------------|
| **Tobler** | Tobler (1993) | Klassische Wanderkostenfunktion |
| **Minetti** | Minetti et al. (2002) | Basierend auf metabolischen Kosten |
| **Herzog** | Herzog (2010) | Modifizierte Variante |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Energetisches Modell |
| **Andere** | Verschiedene | Siehe R-Paket-Dokumentation |

### Bibliographische Referenzen

- Alberti, G. (2019). `movecost`: An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Kompatibilitaet

| Komponente | Mindestversion |
|------------|---------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| movecost R-Paket | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Video-Tutorial

### MoveCost - Wegkostenanalyse
`[Platzhalter: video_movecost.mp4]`

**Inhalte**:
- Konfiguration von R und dem movecost-Paket
- Installation der R-Skripte in QGIS
- Ausfuehrung des grundlegenden movecost-Algorithmus
- Anzeige der Ergebnisse und R-Plots
- Export von Berichten

**Erwartete Dauer**: 20-25 Minuten

---

*PyArchInit-Dokumentation - MoveCost*
*Version: 5.0.x*
*Letzte Aktualisierung: Februar 2026*
