# PyArchInit - Baustellenverwaltung

## Inhaltsverzeichnis

1. [Einfuehrung](#einfuehrung)
2. [Zugriff auf das Modul](#zugriff-auf-das-modul)
3. [Baustellen-Dashboard](#baustellen-dashboard)
4. [Personalformular](#personalformular)
5. [Anwesenheitsformular](#anwesenheitsformular)
6. [Ausruestungsformular](#ausruestungsformular)
7. [Budgetformular](#budgetformular)
8. [2D- und 3D-Visualisierung der Massenberechnung](#2d--und-3d-visualisierung-der-massenberechnung)
9. [PDF- und CSV-Export des Dashboards](#pdf--und-csv-export-des-dashboards)
10. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
11. [Haeufig gestellte Fragen (FAQ)](#haeufig-gestellte-fragen-faq)
12. [Fehlerbehebung](#fehlerbehebung)
13. [Technische Hinweise](#technische-hinweise)

---

## Einfuehrung

Das Modul **Baustellenverwaltung** (it. *Gestione Cantiere*) erweitert PyArchInit um umfassende Funktionen zur Verwaltung logistischer und administrativer Aspekte archaeologischer Grabungen. Es ergaenzt die wissenschaftliche Dokumentation (Stratigraphische Einheiten, Strukturen, Funde) um die operative Projektsteuerung: Personalverwaltung, Anwesenheitserfassung, Ausruestungskontrolle, Budgetueberwachung und Massenberechnungen.

Das Modul besteht aus **fuenf eigenstaendigen Komponenten**, die ueber eine dedizierte Werkzeugleiste erreichbar sind:

| Komponente | Symbol | Beschreibung |
|------------|--------|-------------|
| **Baustellen-Dashboard** | Cantiere-Symbol | Zentrale Uebersicht mit Kennzahlen und Massenberechnungen |
| **Personal** | Personen-Symbol | Verwaltung der Mitarbeiter und ihrer Vertragsdaten |
| **Anwesenheit** | Kalender-Symbol | Tageserfassung von Arbeitszeiten und Abwesenheiten |
| **Ausruestung** | Werkzeug-Symbol | Geraeteinventar mit Wartungsplanung |
| **Budget** | Euro-Symbol | Kostenplanung und -verfolgung |

<!-- IMAGE: Uebersicht der fuenf Baustellenverwaltungsmodule -->
> **Abb. 1**: Die fuenf Komponenten der Baustellenverwaltung und ihre Zusammenhaenge

---

## Zugriff auf das Modul

### Ueber die Werkzeugleiste

Nach dem Laden des Plugins erscheint in QGIS eine dedizierte Werkzeugleiste **pyArchInit - Gestione Cantiere** mit fuenf Symbolen:

```
+---------------------------------------------------------------+
| [Dashboard] | [Personal] [Anwesenheit] | [Ausruestung] [Budget] |
+---------------------------------------------------------------+
```

1. **Dashboard-Symbol** (Baustellen-Dashboard) -- oeffnet die zentrale Uebersicht
2. **Personen-Symbol** (Personal) -- oeffnet das Personalformular
3. **Kalender-Symbol** (Anwesenheit) -- oeffnet das Anwesenheitsformular
4. **Werkzeug-Symbol** (Ausruestung) -- oeffnet das Ausruestungsformular
5. **Euro-Symbol** (Budget) -- oeffnet das Budgetformular

<!-- IMAGE: Baustellenverwaltung-Werkzeugleiste in QGIS -->
> **Abb. 2**: Die Baustellenverwaltung-Werkzeugleiste mit den fuenf Symbolen

### Ueber das Menue

Alternativ sind alle fuenf Formulare ueber das Menue erreichbar:

**PyArchInit** > **Archaeological GIS Tools** > **Dashboard Cantiere / Personal / Anwesenheit / Ausruestung / Budget**

---

## Baustellen-Dashboard

Das **Baustellen-Dashboard** ist das zentrale Cockpit des Moduls. Es bietet eine Echtzeit-Uebersicht ueber die wichtigsten Kennzahlen einer Grabungsbaustelle, ohne dass einzelne Formulare geoeffnet werden muessen.

<!-- IMAGE: Vollstaendiges Baustellen-Dashboard -->
> **Abb. 3**: Das Baustellen-Dashboard mit allen Zusammenfassungsbereichen

### Fundort- und Jahresauswahl

Im oberen Bereich des Dashboards befinden sich zwei Auswahlfelder:

| Steuerelement | Beschreibung |
|---------------|-------------|
| **Fundort** (comboBox_sito) | Waehlt den aktiven Fundort aus der Datenbank |
| **Jahr** (comboBox_anno) | Waehlt das Bezugsjahr (letzten 10 Jahre) |
| **Aktualisieren** | Laedt alle Kennzahlen fuer die aktuelle Auswahl neu |

Die Auswahl wird automatisch mit dem in der Konfiguration hinterlegten Fundort vorbelegt. Bei Aenderung des Fundorts oder Jahres aktualisiert sich das Dashboard automatisch.

### Budgetzusammenfassung

Zeigt eine Schnelluebersicht der finanziellen Situation:

| Anzeige | Beschreibung |
|---------|-------------|
| **Geplant** (label_budget_previsto) | Summe aller geplanten Betraege (importo_previsto) |
| **Ausgegeben** (label_budget_speso) | Summe aller tatsaechlichen Betraege (importo_effettivo) |
| **Fortschrittsbalken** (progressBar_budget) | Visueller Verbrauchsindikator (0-100%) |
| **Kreisdiagramm** (widget_chart) | Aufteilung der Ausgaben nach Kategorie |

<!-- IMAGE: Budgetbereich des Dashboards mit Fortschrittsbalken und Kreisdiagramm -->
> **Abb. 4**: Budgetzusammenfassung mit Fortschrittsbalken und Kreisdiagramm nach Kategorien

Das Kreisdiagramm wird mit **matplotlib** gerendert und zeigt die tatsaechlichen Ausgaben, gruppiert nach der Budgetkategorie. Die Prozentwerte beziehen sich auf den Anteil jeder Kategorie an den Gesamtausgaben.

### Personalzusammenfassung

Zeigt den aktuellen Personalstatus (basierend auf den Anwesenheitsdaten des heutigen Tages):

| Anzeige | Beschreibung |
|---------|-------------|
| **Anwesend** (label_presenti) | Mitarbeiter mit tipo_giornata = 'lavorativa' |
| **Urlaub** (label_ferie) | Mitarbeiter mit tipo_giornata = 'ferie' |
| **Krank** (label_malattia) | Mitarbeiter mit tipo_giornata = 'malattia' |
| **Monatsstunden** (label_ore_mese) | Summe ordinaere + Ueberstunden im laufenden Monat |
| **Monatskosten** (label_costo_mese) | Summe aller Tageskosten im laufenden Monat |

<!-- IMAGE: Personalbereich des Dashboards -->
> **Abb. 5**: Personalzusammenfassung mit Tagesstatus und Monatskennzahlen

### Ausruestungszusammenfassung

Zeigt den aktuellen Status des Geraeteinventars:

| Anzeige | Beschreibung |
|---------|-------------|
| **Gesamt** (label_totali) | Gesamtanzahl der registrierten Ausruestungsgegenstaende |
| **In Gebrauch** (label_in_uso) | Geraete mit stato = 'in_uso' |
| **Wartung** (label_manutenzione) | Geraete mit stato = 'manutenzione' |
| **Wartungsalarm** (label_alert_manutenzione) | Ueberfaellige Wartungstermine (rot hervorgehoben) |

Der Wartungsalarm erscheint in **roter Schrift**, wenn Geraete existieren, deren naechster Wartungstermin (data_prossima_manutenzione) ueberschritten ist und die sich nicht im Status 'fuori_uso' befinden.

<!-- IMAGE: Ausruestungsbereich mit Wartungsalarm -->
> **Abb. 6**: Ausruestungszusammenfassung mit aktivem Wartungsalarm (2 ueberfaellige Geraete)

### Massenberechnung (Computo Metrico)

Der untere Bereich des Dashboards bietet GIS-basierte Massenberechnungen fuer Aushubvolumen und Flaechen:

#### Berechnungsmethode 1: DEM-Differenz

Berechnet das Volumen aus der Differenz zweier Digitaler Gelaendemodelle (DEM vor und nach dem Aushub):

| Feld | Beschreibung |
|------|-------------|
| **DEM vorher** (comboBox_dem_pre) | Raster-Layer des DEM vor dem Eingriff |
| **DEM nachher** (comboBox_dem_post) | Raster-Layer des DEM nach dem Eingriff |

Die Berechnung nutzt den QGIS-Rasterrechner, um pixelweise die Hoehendifferenz zu bestimmen, und summiert die absoluten Volumina.

#### Berechnungsmethode 2: DEM + Polygon

Berechnet Flaecheninhalte und Volumen innerhalb eines definierten Polygons mithilfe von Zonalstatistiken:

| Feld | Beschreibung |
|------|-------------|
| **DEM** (comboBox_dem_pre) | Raster-Layer des DEM |
| **Polygon-Layer** (comboBox_layer_poligono) | Vektor-Layer mit der Berechnungsflaeche |

#### Ergebnisanzeige

| Anzeige | Beschreibung |
|---------|-------------|
| **Flaeche** (label_area_mq) | Berechnete Flaeche in m2 |
| **Volumen** (label_volume_mc) | Berechnetes Volumen in m3 |
| **Berechnen** | Startet die Berechnung mit der gewaehlten Methode |
| **Ergebnis speichern** | Speichert das Ergebnis in der Tabelle computo_metrico |

<!-- IMAGE: Massenberechnungsbereich mit DEM-Auswahl -->
> **Abb. 7**: Massenberechnungsbereich mit DEM-Differenz-Methode und Ergebnisanzeige

#### Berechnungsverlauf

Die Tabelle im unteren Bereich zeigt alle gespeicherten Berechnungsergebnisse:

| Spalte | Beschreibung |
|--------|-------------|
| **Datum** | Zeitpunkt der Berechnung |
| **Typ** | differenza_dem oder dem_poligono |
| **Flaeche (m2)** | Berechnete Flaeche |
| **Volumen (m3)** | Berechnetes Volumen |
| **Notizen** | Optionale Anmerkungen |

<!-- IMAGE: Berechnungsverlaufstabelle mit mehreren Eintraegen -->
> **Abb. 8**: Berechnungsverlaufstabelle mit gespeicherten Massenberechnungen

Ab Version 5.1 stehen neben der Schaltflaeche **Berechnen** drei weitere Schaltflaechen zur Verfuegung (**2D anzeigen**, **3D anzeigen**, **3D-Netz erstellen**), mit denen das Ergebnis direkt in der Karte und in einer interaktiven 3D-Ansicht dargestellt werden kann. Details siehe Abschnitt [2D- und 3D-Visualisierung der Massenberechnung](#2d--und-3d-visualisierung-der-massenberechnung).

---

## 2D- und 3D-Visualisierung der Massenberechnung

Ab Version 5.1 zeigt das Baustellen-Dashboard nach einem Klick auf **Berechnen** im Bereich Massenberechnung nicht mehr nur die numerischen Ergebnisse (Flaeche und Volumen), sondern erzeugt automatisch eine Reihe kartographischer Layer und stellt eine interaktive 3D-Ansicht bereit.

### Was passiert beim Klick auf "Berechnen"

Nach einer DEM-Differenz-Berechnung fuehrt das Dashboard automatisch folgende Schritte aus:

1. **Permanente Speicherung des Differenzrasters**: Das berechnete Raster (DEM post - DEM pre) wird als dauerhaftes GeoTIFF unter `<PYARCHINIT_HOME>/site_dashboard/<Baustellenname>/` gespeichert. Das Raster geht beim Schliessen von QGIS nicht mehr verloren und kann jederzeit erneut verwendet werden.
2. **Hinzufuegen zum QGIS-Projekt**: Das Raster wird im Bedienfeld "Layer" innerhalb einer eigenen Layergruppe namens **"Site Dashboard - Computi"** hinzugefuegt, damit alle Berechnungen uebersichtlich zusammenbleiben.
3. **Automatische Stilzuweisung**: Das Raster erhaelt eine **divergierende Farbrampe**:
   - **Rot** fuer Aushubbereiche (negative Werte, entfernter Boden)
   - **Blau** fuer Auftragsbereiche (positive Werte, hinzugefuegter Boden)
   - **Transparent / neutral** fuer Zellen mit vernachlaessigbarer Veraenderung (|diff| <= 1 cm)
4. **Polygonisierung der Interventionsflaeche**: Rasterzellen mit |diff| > 1 cm werden in einen Vektor-Polygonlayer umgewandelt, der ebenfalls der Gruppe "Site Dashboard - Computi" mit hervorgehobener Darstellung hinzugefuegt wird, damit die Gesamtausdehnung des Eingriffs sofort sichtbar ist.
5. **Automatischer Zoom**: Der Haupt-Kartenbereich von QGIS wird automatisch auf die Ausdehnung der Berechnung gezoomt.

### Voraussetzungen

Damit die neuen 2D/3D-Visualisierungen verwendet werden koennen, muessen:

- Zwei **DEM-Rasterlayer** im QGIS-Projekt geladen sein (typischerweise ein DEM **vor** und ein DEM **nach** dem Aushub)
- In den Comboboxen **DEM Pre** und **DEM Post** im Bereich Massenberechnung korrekt ausgewaehlt werden
- Das CRS beider Raster konsistent sein

### Neue Schaltflaechen

Neben der Schaltflaeche **Berechnen** stehen drei neue Schaltflaechen zur Verfuegung:

| Schaltflaeche | Beschreibung |
|---------------|--------------|
| **2D anzeigen** | Zentriert die QGIS-Karte erneut auf die Ausdehnung der letzten Berechnung. Nuetzlich, um nach dem Arbeiten in anderen Bereichen schnell zur aktiven Massenberechnung zurueckzukehren. |
| **3D anzeigen** | Oeffnet einen interaktiven 3D-Dialog, der das DEM **pre** als Gelaendemodell verwendet und das Differenzraster darueber legt. Der Dialog bietet: einen Spinbox fuer die **vertikale Ueberhoehung**, Kontrollkaestchen zum Ein-/Ausschalten einzelner Layer und eine Schaltflaeche **Ansicht zuruecksetzen**. |
| **3D-Netz erstellen** | Erzeugt TIN-Netze aus den pre- und post-DEMs ueber QGIS-Processing-Algorithmen. Die Netze koennen im 3D-Viewer angezeigt werden, um die beiden Oberflaechen und das dazwischen liegende Volumen visuell zu vergleichen. |

<!-- IMAGE: Die neuen Schaltflaechen 2D anzeigen, 3D anzeigen und 3D-Netz erstellen neben Berechnen -->
> **Abb. 9**: Die neuen Schaltflaechen **2D anzeigen**, **3D anzeigen** und **3D-Netz erstellen** neben der Schaltflaeche **Berechnen**

<!-- IMAGE: Interaktive 3D-Ansicht mit DEM pre als Gelaende und aufgelegtem Differenzraster -->
> **Abb. 10**: Der interaktive 3D-Dialog der Massenberechnung mit vertikaler Ueberhoehung und Layer-Umschaltung

### Typischer Arbeitsablauf

1. Die zwei DEM-Raster (pre und post) in das QGIS-Projekt laden
2. Das **Baustellen-Dashboard** oeffnen
3. Im Bereich **Massenberechnung** die beiden DEMs in **DEM Pre** und **DEM Post** auswaehlen
4. Auf **Berechnen** klicken: Differenzraster und Interventionspolygon werden automatisch erzeugt, die Karte auf die Ausdehnung gezoomt
5. Die numerischen Werte (Flaeche, Volumen, Aushub, Auftrag) direkt im Bereich ablesen
6. Auf **3D anzeigen** klicken, um die interaktive 3D-Ansicht zu oeffnen
7. (Optional) Auf **3D-Netz erstellen** klicken, um die TIN-Netze beider DEMs zu erzeugen und darzustellen
8. Auf **Ergebnis speichern** klicken, um das Ergebnis im Berechnungsverlauf zu archivieren

### Ablage auf der Festplatte

Alle von der Massenberechnung erzeugten Raster und Layer werden gespeichert unter:

```
<PYARCHINIT_HOME>/site_dashboard/<Baustellenname>/
```

wobei `<PYARCHINIT_HOME>` der in den PyArchInit-Einstellungen konfigurierte Arbeitsordner ist und `<Baustellenname>` die im Dashboard ausgewaehlte Baustelle. Auf diese Weise bleibt ein physischer Verlauf aller Berechnungen erhalten und die Layer koennen auch in anderen QGIS-Projekten weiterverwendet werden.

### Aktualisierung: "2D anzeigen" -- Analytischer Schnittdialog

Ab der naechsten Version zentriert die Schaltflaeche **2D anzeigen** im Bereich Massenberechnung die Karte nicht mehr nur auf die letzte Berechnung, sondern oeffnet einen **matplotlib-basierten analytischen Dialog**, der die Aushubergebnisse als klassische archaeologische Schnittansicht praesentiert.

Der Dialog steht **nur zur Verfuegung, wenn die Berechnung im Modus "DEM-Differenz"** (mit Pre- und Post-DEM) durchgefuehrt wurde. Bei Verwendung des Modus **DEM + Polygon** verhaelt sich die Schaltflaeche wie zuvor und zoomt lediglich die QGIS-Karte auf die Ausdehnung der Berechnung.

Wenn verfuegbar, enthaelt der Dialog folgende Panels:

| Panel | Beschreibung |
|-------|--------------|
| **Heatmap der DEM-Differenz** | 2D-Heatmap des Differenzrasters mit divergierender Farbrampe (Rot fuer Aushub, Blau fuer Auftrag) |
| **Histogramm** | Verteilung der **Aushub**-Tiefen und **Auftrags**-Hoehen, fuer einen sofortigen statistischen Ueberblick ueber das bewegte Volumen |
| **Laengsschnitt (O-W)** | Der klassische archaeologische Schnitt: das **Pre-DEM** wird in **Blau** gezeichnet, das **Post-DEM** in **Rot**, und das ausgehobene Volumen ist zwischen den beiden Linien **ausgefuellt** |
| **Querschnitt (N-S)** | Gleiche Logik wie der O-W-Schnitt, aber entlang der Nord-Sued-Richtung |
| **Zeilen- / Spalten-Spinbox** | Ermoeglichen das interaktive Verschieben der Schnittposition auf dem Raster, um den gesamten Aushub zu erkunden |
| **Schaltflaeche "PNG speichern"** | Exportiert die gesamte Abbildung (Heatmap, Histogramm und beide Schnitte) als PNG-Bild, bereit zur Aufnahme in den Grabungsbericht |

<!-- IMAGE: Analytischer 2D-Dialog mit Heatmap, Histogramm und O-W / N-S-Schnitten -->
> **Abb. 11**: Der neue analytische **2D anzeigen**-Dialog mit Heatmap der DEM-Differenz, Aushub/Auftrags-Histogramm sowie Laengs- und Querschnitt (Pre-DEM in Blau, Post-DEM in Rot, Aushubvolumen zwischen den Linien gefuellt)

### Aktualisierung: "3D anzeigen" -- matplotlib-Fallback

Die Schaltflaeche **3D anzeigen** behandelt nun automatisch zwei Szenarien, je nachdem, welche QGIS-Version installiert ist:

1. **QGIS mit nativem 3D-Modul (Qt3D verfuegbar)**: Wie bisher wird der eingebettete `Qgs3DMapCanvas`-Dialog geoeffnet, mit Gelaende aus dem Pre-DEM, vertikaler Ueberhoehung und Layer-Steuerung.
2. **QGIS ohne 3D-Modul (Fehler "QGIS 3D module not available")**: Das Baustellen-Dashboard wechselt automatisch zu einem **matplotlib-basierten 3D-Viewer**. Da matplotlib zu den mit PyArchInit mitgelieferten Abhaengigkeiten gehoert, funktioniert dieser Viewer **immer**, auch auf minimalen QGIS-Builds ohne 3D-Unterstuetzung.

Der Fallback-Viewer bietet:

| Steuerung | Beschreibung |
|-----------|--------------|
| **Anzeigemodus** | Drei waehlbare Modi: **Pre + Post** (beide Oberflaechen ueberlagert), **Nur Differenz** (nur die Aushub/Auftrags-Oberflaeche), **Nur Pre** (das Pre-DEM als Referenzoberflaeche) |
| **Vertikale Ueberhoehung** | Schieberegler zur Hervorhebung des Hoehenunterschieds zwischen den beiden Oberflaechen, besonders nuetzlich bei geringen Aushubtiefen |
| **Interaktive Rotation** | Durch Ziehen mit der Maus kann die 3D-Szene in Echtzeit gedreht werden, um den Aushub aus jedem Blickwinkel zu betrachten |

<!-- IMAGE: matplotlib 3D-Fallback-Viewer im Modus Pre + Post -->
> **Abb. 12**: Der matplotlib 3D-Fallback-Viewer, wenn das native Qt3D-Modul von QGIS nicht verfuegbar ist: zeigt die Pre- und Post-Oberflaechen mit einstellbarer vertikaler Ueberhoehung

### Aktualisierung: "3D-Netz erstellen" -- Automatische Gelaendestilzuweisung

Die Schaltflaeche **3D-Netz erstellen** wendet nun automatisch eine **gelaendeartige Farbrampe** auf das Netz-Dataset **Bed Elevation** an. Zuvor wirkte das Netz wie eine flache, schwer lesbare Oberflaeche; jetzt wird es sofort zu einer aussagekraeftigen Hoehenkarte:

- **Gruen** fuer die niedrigsten Hoehen
- **Orange** fuer mittlere Hoehen
- **Braun** fuer die hoechsten Hoehen

Dadurch ist das Netz bereits im QGIS-Kartenbereich sichtbar und aussagekraeftig, noch bevor die 3D-Ansicht geoeffnet wird. Nach dem Erstellen genuegt ein Klick auf **3D anzeigen**, um das Netz als 3D-Oberflaeche zu rendern, entweder ueber das native QGIS-3D-Modul oder ueber den oben beschriebenen matplotlib-Fallback-Viewer.

<!-- IMAGE: 3D-Netz mit der neuen gruen/orange/braun Gelaenderampe -->
> **Abb. 13**: Das 3D-Netz mit der neuen gelaendeartigen Farbrampe, die automatisch auf das Hoehen-Dataset angewendet wird

### Aktualisierung: Polygon als Zuschneidemaske

Wenn Sie im Panel Massenberechnung zusaetzlich zu den beiden DEMs auch einen Vektorlayer im Kombinationsfeld **Polygon-Layer** auswaehlen und gleichzeitig den Modus **DEM-Differenz** aktiv lassen, wird das Polygon jetzt als **Zuschneidemaske** verwendet: Beide DEMs werden vor der Differenzberechnung auf das Polygon zugeschnitten, sodass die 2D-Analyseansicht, der matplotlib-3D-Fallback und das TIN-Netz ausschliesslich auf dem Eingriffsbereich arbeiten. Der typische Ablauf ist: Ein Polygon um den Grabungsbereich zeichnen, Pre- und Post-DEM auswaehlen, das Polygon im Kombinationsfeld **Polygon-Layer** waehlen und **Berechnen** druecken. Die beiden zugeschnittenen Raster werden automatisch zur Gruppe **"Cruscotto Cantiere - Computi"** im Layerbaum hinzugefuegt und koennen sofort wiederverwendet werden.

### Aktualisierung: "3D-Netz erstellen" -- keine Abstuerze mehr

Fruehere Versionen konnten QGIS auf bestimmten Builds zum Absturz bringen, weil es in den fuer die Netzgenerierung verwendeten Processing-Algorithmen zu einem C++-Segfault kam. Die Netzerzeugung wurde in **reinem Python** neu geschrieben: Das Dashboard liest das DEM mit GDAL und schreibt direkt eine 2DM-Datei mit einem **Viereck-Netz auf regelmaessigem Gitter**, ohne auf die nativen Algorithmen angewiesen zu sein. Das Ergebnis ist auf jeder QGIS-Version sicher. Netze mit mehr als etwa **15 000 Zellen** werden automatisch heruntergerechnet, um die Erstellung schnell und die Datei schlank zu halten, waehrend nodata-Zellen uebersprungen werden: Bei aktiver Polygon-Zuschneidemaske folgt das Netz somit exakt der Form des zugeschnittenen Eingriffsbereichs. Sollte die Erzeugung in seltenen Faellen aus anderen Gruenden scheitern (Festplatte voll, fehlende Berechtigungen), schlaegt der Dialog jetzt vor, direkt **3D anzeigen** zu oeffnen, das den matplotlib-Fallback-Viewer verwendet und keinen Netzlayer benoetigt.

### Aktualisierung: Automatische Aktualisierung der Comboboxen beim Klick auf "Berechnen"

Der Bereich Massenberechnung **aktualisiert die DEM- und Polygon-Listen nun automatisch bei jedem Klick auf "Berechnen"**: Es ist nicht mehr noetig, das Baustellen-Dashboard zu schliessen und wieder zu oeffnen, nachdem ein neues Raster geladen oder ein neues Polygon im Projekt gezeichnet wurde. Einfach den Layer in QGIS hinzufuegen, zum Panel zurueckkehren und **Berechnen** druecken -- die Comboboxen **DEM Pre**, **DEM Post** und **Polygon-Layer** werden sofort mit dem aktuellen Projektstand neu befuellt. Die Diagnose des Zuschneidevorgangs (Erfolg, nicht uebereinstimmendes CRS, leere Schnittflaeche) erscheint in der **QGIS-Meldungsleiste**, sodass jederzeit ersichtlich ist, welche Layer tatsaechlich fuer die Berechnung verwendet wurden.

### Aktualisierung: Schaltflaeche umbenannt in "2DM + 3D exportieren"

Die zuvor als **3D-Netz erstellen** bezeichnete Schaltflaeche wurde in **2DM + 3D exportieren** umbenannt, um ihr neues Verhalten widerzuspiegeln: Sie laedt das Netz **nicht mehr** als Layer in das QGIS-Projekt (die native Mesh-API kann auf einigen QGIS-Builds abstuerzen) und fuehrt stattdessen zwei sichere, sich ergaenzende Aktionen aus. Sie schreibt die **2DM**-Dateien aus dem Pre- und Post-DEM auf die Festplatte (nuetzlich fuer den Import in externe Nachbearbeitungssoftware) und oeffnet direkt die **matplotlib-3D-Ansicht** der zugeschnittenen DEMs, sodass das Ergebnis sofort visuell beurteilt werden kann. Abstuerze sind damit vollstaendig ausgeschlossen, da die QGIS-Mesh-API nie angesprochen wird.

### Aktualisierung: Polygon-Zuschnitt mit sichtbarer Diagnose

Wenn Sie zusammen mit den beiden DEMs einen Layer in der Combobox **Polygon-Layer** auswaehlen, wird das Zuschneiden der Raster auf das Polygon jetzt **in der QGIS-Meldungsleiste protokolliert**: Bei Erfolg werden die auf die Festplatte geschriebenen zugeschnittenen Dateien aufgelistet, bei einem Fehlschlag wird der genaue Grund angezeigt (zum Beispiel Polygon in einem anderen CRS als die DEMs, keine geometrische Schnittmenge zwischen Polygon und Raster, fehlende oder nicht lesbare Quelldatei). So wird sofort klar, warum ein Zuschnitt nicht angewendet wurde und was zu korrigieren ist (Polygon umprojizieren, ueber den DEM-Bereich verschieben, Dateipfad pruefen), ohne Logs oder die Python-Konsole oeffnen zu muessen.

### Aktualisierung: Polygon-Zuschnitt auch im Modus "DEM auf Polygon"

Der Polygon-Zuschnitt funktioniert jetzt auch, wenn der Radio-Button **DEM auf Polygon** ausgewaehlt ist (Zonalstatistik-Modus mit nur einem DEM): Das Raster wird **vor** der Uebergabe an die Viewer **2D anzeigen**, **3D anzeigen** und **2DM + 3D exportieren** auf die Ausdehnung des Polygons zugeschnitten, sodass der analytische Schnitt und die 3D-Ansicht ausschliesslich die Eingriffsflaeche anzeigen und nicht mehr wie zuvor das gesamte DEM. Die Zuschnitt-Diagnose erscheint in der **QGIS-Meldungsleiste** genau wie im Modus DEM-Differenz. In diesem Szenario mit einem einzelnen DEM passt sich der Viewer **2D anzeigen** automatisch an: Die Heatmap zeigt die Hoehen mit einer **terrain**-Farbrampe, das Histogramm stellt die Hoehenverteilung mit der Mittelwertlinie dar, und die beiden Laengs-/Querschnitte zeichnen nur eine einzelne Hoehenlinie (ohne Fuellung zwischen Pre und Post, da kein Post-DEM vorhanden ist).

### Aktualisierung: Kostenanalyse der Massenberechnung

Im Computo-Metrico-Panel des Baustellen-Dashboards wurde ein neuer Bereich **Kostenanalyse** mit zwei Eingabeparametern hinzugefuegt: **Einheitskosten** (in Euro/m3) und **Produktivitaet** (in m3/Tag). Bei jedem Klick auf **Berechnen** aktualisiert das Panel automatisch drei abgeleitete Werte, die auf einen Blick sichtbar sind: **Gesamtkosten** (Volumen x Einheitskosten), **Geschaetzte Tage** (Volumen / Produktivitaet) und **Tageskosten** (Einheitskosten x Produktivitaet). Beide Eingaben werden **pro Baustelle** in den QGIS-Einstellungen gespeichert (Schluessel `pyArchInit/site_dashboard/costs/<baustelle>/...`), sodass sie nur einmal pro Baustelle eingegeben werden muessen: Beim Wechsel der Baustelle werden die gespeicherten Werte automatisch neu geladen, und die drei Gesamtwerte werden bei jeder neuen Berechnung in Echtzeit neu berechnet.

### Aktualisierung: Pre/Post-Zuschnitt ausgerichtet

Die Berechnung der DEM-Differenz setzt voraus, dass die beiden DEMs (pre und post) exakt auf demselben Pixelraster ausgerichtet sind. In den vorherigen Versionen konnten die beiden zugeschnittenen DEMs bei Verwendung eines Zuschnittpolygons auf leicht unterschiedlichen Rastern landen, sodass `pre - post` falsch oder leer berechnet wurde. Jetzt verwenden beide Zuschnitte die **native Aufloesung des Pre-DEM** als Referenz (gleiche `xRes` / `yRes` und gleiche Rasterausrichtung), sodass die beiden zugeschnittenen Raster immer pixelgenau uebereinstimmen und die Differenz ein gueltiges Ergebnis liefert. Selbst minimale Graeben, aus denen nur "10 Eimer Erde" (etwa 1 m3) entnommen wurden, werden jetzt korrekt von der Massenberechnung erfasst.

### Aktualisierung: Neue Combo "Mauern / Strukturen"

Im Computo-Metrico-Panel wurde eine zweite Combo **Mauern / Strukturen** hinzugefuegt, mit der sich eine Polygonebene auswaehlen laesst, die Mauern, aufgehendes Mauerwerk, Pfeiler oder andere bauliche Elemente darstellt, die **nicht** in die Berechnung der Aushubkubikmeter einfliessen sollen. Beim Klick auf **Berechnen** werden die Mauer-Polygone als NODATA in das zugeschnittene Differenzraster gebrannt und ihre Zellen vom Volumen-Gesamtwert ausgeschlossen; die Diagnose erscheint in der QGIS-Meldungsleiste (z. B. `walls masked: muri_trincea_42`). Typischer archaeologischer Arbeitsablauf: Pre-DEM + Post-DEM + Polygon der Grabungsflaeche + Polygon der aufgefundenen Mauern laden, beide in den zwei Combos auswaehlen und **Berechnen** druecken -- das ausgehobene Volumen schliesst das Volumen der Strukturen automatisch aus.

---

## PDF- und CSV-Export des Dashboards

Das Baustellen-Dashboard kann eine vollstaendige Zusammenfassung aller Verwaltungsdaten in zwei Formaten exportieren: **PDF** (paginiertes Dokument, ideal fuer Auftraggeber oder Archivierung) und **CSV** (ideal fuer weitere Auswertungen in Excel oder anderen Tabellenkalkulationen).

### PDF-Export

Die Schaltflaeche **PDF exportieren** erzeugt einen vollstaendigen Baustellenbericht. Ab Version 5.1 enthaelt das PDF:

- **Ueberarbeitete Titelseite** mit Baustellenname, Bezugsjahr und Erstellungsdatum
- **Budget-Zusammenfassung** mit detaillierten Tabellen nach Kategorie und Gesamtsummen (geplant vs. tatsaechlich)
- **Personal-Zusammenfassung** mit Anwesenheitsstatistiken, Arbeitsstunden und Kosten
- **Ausruestungs-Zusammenfassung** mit Inventarstatus und ueberfaelligen Wartungen
- **Neuer Abschnitt "Computo Metrico"** mit:
  - Detaillierter Tabelle aller gespeicherten Berechnungen
  - **Gesamtsummen**: Gesamtflaeche (m2) und Gesamtvolumen (m3)
  - **Statistik**: Aushubvolumen, Auftragsvolumen, betroffene Flaeche
- **Neuer Abschnitt "Kostenanalyse"** (zwischen **Computo Metrico** und **Statistik** eingefuegt) mit einer Parameterkarte der konfigurierten Werte (Einheitskosten in Euro/m3 und Produktivitaet in m3/Tag), einer detaillierten Tabelle pro Datensatz (Datum, Typ, Volumen, Kosten, geschaetzte Tage, Tageskosten) und einer **Summenzeile** am Ende; der Block **Statistik** wurde um **Gesamtkosten** und **Gesamttage** der Baustelle erweitert
- **Vollstaendige Unterstuetzung fuer Sonderzeichen**: Das PDF-Rendering wurde fuer alle unterstuetzten Sprachen korrigiert, einschliesslich rumaenischer Akzentbuchstaben (**a**, **a**, **i**, **s**, **t**), **griechischer**, **arabischer**, **portugiesischer** und **katalanischer** Zeichen.

### CSV-Export

Die Schaltflaeche **CSV exportieren** erzeugt eine CSV-Datei, die mit den gaengigen Tabellenkalkulationen kompatibel ist. Ab Version 5.1:

- **UTF-8-Kodierung mit BOM**: garantiert, dass Excel (insbesondere die europaeische Version) die Datei korrekt oeffnet, ohne Sonderzeichen zu beschaedigen
- **Trennzeichen Semikolon (`;`)**: kompatibel mit dem europaeischen Excel-Gebietsschema
- **Abschnitt COMPUTO METRICO**: enthaelt alle Massenberechnungsdaten mit Typ, Flaeche, Volumen und Notizen jeder Berechnung
- **Neuer Abschnitt `=== KOSTENANALYSE ===`**: beginnt mit den beiden Parametern (Einheitskosten in Euro/m3 und Produktivitaet in m3/Tag) und wird von der detaillierten Tabelle pro Datensatz (Datum, Typ, Volumen, Kosten, geschaetzte Tage, Tageskosten) gefolgt, bereit zum Filtern oder Aggregieren in Excel
- **Erweiterter abschliessender SUMMARY-Block**: eine aggregierte Zusammenfassung mit Gesamtsummen und Statistiken fuer schnelle Auswertungen ohne zusaetzliche Formeln; jetzt zusaetzlich mit **Gesamtkosten** und **Gesamttage**, berechnet aus der neuen Kostenanalyse

<!-- IMAGE: PDF-Export mit dem neuen Abschnitt Computo Metrico -->
> **Abb. 11**: PDF-Export mit dem neuen Abschnitt **Computo Metrico** (Tabelle, Gesamtsummen und Statistik)

<!-- IMAGE: CSV-Export in Excel mit dem Abschnitt COMPUTO METRICO und dem Block SUMMARY -->
> **Abb. 12**: In Excel geoeffneter CSV-Export mit dem Abschnitt **COMPUTO METRICO** und dem abschliessenden Block **SUMMARY**

### Neues Tab-Layout des Baustellen-Dashboards

Ab der aktuellen Version ist das Fenster **Baustellen-Dashboard** in **drei Reiter** gegliedert, um dem neuen Panel **Kostenanalyse** Platz zu schaffen, ohne die Ansicht zu ueberladen. Die Kopfzeile mit **Baustelle**, **Jahr** und der Schaltflaeche **Aktualisieren** bleibt oberhalb der Reiter sichtbar, sodass jederzeit Baustelle oder Jahr gewechselt werden kann: alle Reiter werden automatisch aktualisiert.

| Reiter | Inhalt |
|--------|--------|
| **Uebersicht** | Ansicht, die beim Oeffnen des Dashboards zuerst angezeigt wird. Oben, in voller Breite, die **Budget-Zusammenfassung** (Fortschrittsbalken und Tortendiagramm); darunter nebeneinander die Zusammenfassungen **Personal** und **Ausruestung** |
| **Massenberechnung** | Enthaelt den gesamten DEM-Berechnungsworkflow: Comboboxen **DEM Pre**, **DEM Post** und **Polygon**, Radiobuttons **DEM-Differenz** / **DEM ueber Polygon**, Schaltflaeche **Berechnen**, Beschriftungen fuer **Flaeche** und **Volumen**, die neue Gruppe **Kostenanalyse** (EUR/m3, m3/Tag -> Gesamtkosten, geschaetzte Tage, Tageskosten), Schaltflaeche **Datensatz speichern**, Schaltflaechen **2D anzeigen** / **3D anzeigen** / **Export 2DM + 3D** und die **Historien-Tabelle** unten |
| **Export** | Die Schaltflaechen fuer den **PDF-** und **CSV-Export** mit einer kurzen Beschreibung |

<!-- IMAGE: Neues Tab-Layout des Baustellen-Dashboards (Uebersicht / Massenberechnung / Export) -->
> **Abb. 13**: Das neue Tab-Layout des Baustellen-Dashboards mit der stets sichtbaren Kopfzeile Baustelle / Jahr / Aktualisieren

**Fix**: DEMs verschwinden nicht mehr beim Druecken von **Berechnen** (Regression aus 5.0.13-alpha, bei der die automatische Aktualisierung der Comboboxen die aktuelle Auswahl zuruecksetzte).

---

## Personalformular

Das **Personalformular** (Personale) verwaltet die Stammdaten aller Mitarbeiter einer Grabungsbaustelle.

### Benutzeroberflaeche

Das Formular folgt dem Standard-DBMS-Muster von PyArchInit mit Navigationsleiste, Suchfunktion und Datensatzverwaltung.

<!-- IMAGE: Personalformular mit ausgefuellten Feldern -->
> **Abb. 9**: Das Personalformular mit einer vollstaendigen Mitarbeiterakte

### DBMS-Toolbar

Die DBMS-Toolbar am oberen Rand bietet die Standard-Funktionen:

| Funktion | Beschreibung |
|----------|-------------|
| **Neuer Datensatz** | Erstellt einen leeren Personaldatensatz |
| **Speichern** | Speichert den aktuellen Datensatz |
| **Loeschen** | Entfernt den aktuellen Datensatz |
| **Suche starten / Suche ausfuehren** | Ermoeglicht die Suche nach beliebigen Feldern |
| **Navigation** | Blaettert zwischen Datensaetzen (Erster/Vorheriger/Naechster/Letzter) |
| **Alle anzeigen** | Zeigt alle Datensaetze |
| **Sortieren** | Sortiert nach gewaehltem Feld |

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Vorname** | nome | Text | Vorname des Mitarbeiters |
| **Nachname** | cognome | Text | Nachname des Mitarbeiters |
| **Rolle** | ruolo | Text | Funktion im Projekt (z.B. Grabungsleiter, Techniker) |
| **Qualifikation** | qualifica | Text | Berufliche Qualifikation (z.B. Archaeologe, Geometer) |
| **Steuernummer** | codice_fiscale | Text | Identifikationsnummer |
| **E-Mail** | email | Text | Kontakt-E-Mail |
| **Telefon** | telefono | Text | Telefonnummer |
| **Geburtsdatum** | data_nascita | Datum | Format: JJJJ-MM-TT |
| **Adresse** | indirizzo | Text | Wohnanschrift |
| **Vertragsart** | tipo_contratto | Text | Art des Vertrags (z.B. Festanstellung, freiberuflich) |
| **Vertragsbeginn** | data_inizio_contratto | Datum | Beginn des Arbeitsvertrags |
| **Vertragsende** | data_fine_contratto | Datum | Ende des Arbeitsvertrags |
| **Stundensatz** | tariffa_oraria | Dezimal | Verguetung pro Stunde (EUR) |
| **Tagessatz** | tariffa_giornaliera | Dezimal | Verguetung pro Tag (EUR) |
| **IBAN** | iban | Text | Bankverbindung |
| **Notizen** | note | Text | Freitext fuer zusaetzliche Informationen |
| **Aktiv** | attivo | Boolean | Ob der Mitarbeiter aktuell aktiv ist |

<!-- IMAGE: Personalformular-Felder im Detail -->
> **Abb. 10**: Detailansicht der Personalformularfelder mit Beispieldaten

---

## Anwesenheitsformular

Das **Anwesenheitsformular** (Presenze) erfasst die taegliche Arbeitszeit und Abwesenheiten des Personals.

### Benutzeroberflaeche

<!-- IMAGE: Anwesenheitsformular mit Tageseintrag -->
> **Abb. 11**: Das Anwesenheitsformular mit einem typischen Tageseintrag

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Personal-ID** | id_personale | Ganzzahl | Verweis auf den Personaldatensatz |
| **Datum** | data | Datum | Tag der Anwesenheit (JJJJ-MM-TT) |
| **Eintritt** | ora_ingresso | Zeit | Uhrzeit des Arbeitsbeginns |
| **Austritt** | ora_uscita | Zeit | Uhrzeit des Arbeitsendes |
| **Regulaere Stunden** | ore_ordinarie | Dezimal | Anzahl regulaerer Arbeitsstunden |
| **Ueberstunden** | ore_straordinario | Dezimal | Anzahl der Ueberstunden |
| **Tagestyp** | tipo_giornata | Auswahl | Art des Tages (siehe Tabelle unten) |
| **Schicht** | turno | Text | Bezeichnung der Schicht (z.B. Frueh, Spaet) |
| **Arbeitsbereich** | area_lavoro | Text | Grabungsareal oder Taetigkeitsbereich |
| **Notizen** | note | Text | Bemerkungen zum Tag |
| **Tageskosten** | costo_giornata | Dezimal | Berechnete Kosten fuer diesen Tag (EUR) |

### Tagestypen (tipo_giornata)

| Wert | Deutsche Bezeichnung | Beschreibung |
|------|---------------------|-------------|
| `lavorativa` | Arbeitstag | Normaler Arbeitstag |
| `ferie` | Urlaub | Geplanter Urlaubstag |
| `malattia` | Krankheit | Krankheitsbedingter Ausfall |
| `permesso` | Erlaubnis | Sonderurlaub / Freistellung |

<!-- IMAGE: Anwesenheitsformular mit Tagestyp-Auswahl -->
> **Abb. 12**: Auswahl des Tagestyps im Anwesenheitsformular

### Erfassung eines Arbeitstages

1. Auf **Neuer Datensatz** klicken
2. **Fundort** auswaehlen
3. **Personal-ID** des Mitarbeiters eingeben
4. **Datum** auswaehlen
5. **Eintritt** und **Austritt** eingeben
6. **Regulaere Stunden** und ggf. **Ueberstunden** eintragen
7. **Tagestyp** waehlen (z.B. lavorativa)
8. Optional: **Arbeitsbereich**, **Schicht** und **Notizen** ausfuellen
9. **Tageskosten** eintragen oder berechnen lassen
10. Auf **Speichern** klicken

<!-- IMAGE: Schritt-fuer-Schritt-Anwesenheitserfassung -->
> **Abb. 13**: Workflow zur Erfassung eines Arbeitstages

---

## Ausruestungsformular

Das **Ausruestungsformular** (Attrezzature) verwaltet das Inventar an Geraeten, Werkzeugen und Maschinen der Grabungsbaustelle, einschliesslich Wartungsplanung.

### Benutzeroberflaeche

<!-- IMAGE: Ausruestungsformular mit Geraeteeintrag -->
> **Abb. 14**: Das Ausruestungsformular mit einem typischen Geraeteeintrag

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Inventarnummer** | codice_inventario | Text | Eindeutige Inventarkennung |
| **Name** | nome | Text | Bezeichnung des Geraets |
| **Kategorie** | categoria | Text | Geraetekategorie (z.B. Vermessung, Aushub, Dokumentation) |
| **Marke** | marca | Text | Hersteller |
| **Modell** | modello | Text | Modellbezeichnung |
| **Seriennummer** | numero_serie | Text | Seriennummer des Geraets |
| **Eigentum** | proprieta | Text | Eigentuemer (z.B. Firma, Miete, Leasing) |
| **Kaufdatum** | data_acquisto | Datum | Datum der Anschaffung |
| **Kaufpreis** | costo_acquisto | Dezimal | Anschaffungskosten (EUR) |
| **Mietkosten/Tag** | costo_noleggio_giorno | Dezimal | Tagespreis bei Miete (EUR) |
| **Status** | stato | Auswahl | Aktueller Zustand (siehe Tabelle unten) |
| **Zugewiesen an** | assegnato_a | Text | Name des verantwortlichen Mitarbeiters |
| **Letzte Wartung** | data_ultima_manutenzione | Datum | Datum der letzten Wartung |
| **Naechste Wartung** | data_prossima_manutenzione | Datum | Geplantes Datum der naechsten Wartung |
| **Notizen** | note | Text | Zusaetzliche Informationen, Zustandsbeschreibung |

### Statuswerte (stato)

| Wert | Deutsche Bezeichnung | Beschreibung |
|------|---------------------|-------------|
| `in_uso` | In Gebrauch | Geraet ist aktiv im Einsatz |
| `manutenzione` | Wartung | Geraet befindet sich in Wartung oder Reparatur |
| `fuori_uso` | Ausser Betrieb | Geraet ist defekt oder ausgemustert |

<!-- IMAGE: Statusauswahl im Ausruestungsformular -->
> **Abb. 15**: Die drei Statusoptionen fuer Ausruestungsgegenstaende

### Wartungsplanung

Das System ueberwacht automatisch die Wartungstermine. Geraete, deren Feld **Naechste Wartung** (data_prossima_manutenzione) in der Vergangenheit liegt und die sich nicht im Status 'fuori_uso' befinden, werden im Dashboard als **ueberfaellig** markiert.

**Empfohlener Workflow**:
1. Bei Neuaufnahme eines Geraets das Datum der naechsten Wartung eintragen
2. Nach jeder Wartung: **Letzte Wartung** aktualisieren und neues Datum bei **Naechste Wartung** setzen
3. Dashboard regelmaessig auf Wartungsalarme pruefen

<!-- IMAGE: Wartungsfelder im Ausruestungsformular -->
> **Abb. 16**: Wartungsdatumsfelder mit hervorgehobenem ueberfaelligem Termin

---

## Budgetformular

Das **Budgetformular** (Budget) ermoeglicht die Planung und Verfolgung aller Kosten einer Grabungsbaustelle.

### Benutzeroberflaeche

<!-- IMAGE: Budgetformular mit Kosteneintrag -->
> **Abb. 17**: Das Budgetformular mit einem typischen Kosteneintrag

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Jahr** | anno | Ganzzahl | Bezugsjahr des Budgeteintrags |
| **Kategorie** | categoria | Text | Kostenkategorie (z.B. Personal, Material, Geraete, Logistik) |
| **Beschreibung** | descrizione | Text | Detaillierte Beschreibung des Budgetpostens |
| **Geplanter Betrag** | importo_previsto | Dezimal | Budgetierter Betrag (EUR) |
| **Tatsaechlicher Betrag** | importo_effettivo | Dezimal | Tatsaechlich ausgegebener Betrag (EUR) |
| **Erfassungsdatum** | data_registrazione | Datum | Datum der Budgeterfassung |
| **Ausgabedatum** | data_spesa | Datum | Datum der tatsaechlichen Ausgabe |
| **Lieferant** | fornitore | Text | Name des Lieferanten oder Dienstleisters |
| **Rechnungsnummer** | numero_fattura | Text | Referenznummer der Rechnung |
| **Notizen** | note | Text | Zusaetzliche Informationen |

<!-- IMAGE: Budgetformular-Felder im Detail -->
> **Abb. 18**: Detailansicht der Budgetfelder mit Beispiel einer Materialbestellung

### Budgetplanung vs. Kostenverfolgung

Das System unterscheidet zwischen zwei Nutzungsmodi:

**1. Budgetplanung (Voraus)**:
- **Geplanter Betrag** ausfuellen
- **Tatsaechlicher Betrag** leer lassen oder auf 0 setzen
- Dient als Kostenschaetzung vor Projektbeginn

**2. Kostenverfolgung (Laufend)**:
- **Tatsaechlicher Betrag** nach jeder Ausgabe aktualisieren
- **Ausgabedatum**, **Lieferant** und **Rechnungsnummer** eintragen
- Ermoeglicht Soll-Ist-Vergleich im Dashboard

---

## Operativer Arbeitsablauf

### Projekt einrichten

Ein typischer Arbeitsablauf fuer eine neue Grabungsbaustelle:

#### Schritt 1: Fundort anlegen

Zunaechst muss der Fundort im Fundort-Formular angelegt werden (siehe [Fundort-Formular Tutorial](02_fundort_formular.md)).

#### Schritt 2: Budget planen

```
1. Budgetformular oeffnen
2. Fundort auswaehlen
3. Jahr eintragen
4. Fuer jede Kostenkategorie einen Eintrag mit geplantem Betrag erstellen:
   - Personal (Loehne, Honorare)
   - Material (Verbrauchsmaterial, Werkzeug)
   - Geraete (Miete, Wartung)
   - Logistik (Transport, Unterkunft)
   - Dokumentation (Fotografie, Zeichnung)
5. Jeden Eintrag speichern
```

#### Schritt 3: Personal erfassen

```
1. Personalformular oeffnen
2. Jeden Mitarbeiter mit vollstaendigen Stammdaten anlegen
3. Vertragsdaten (Beginn, Ende, Tagessatz) eintragen
4. Datensaetze speichern
```

#### Schritt 4: Ausruestung registrieren

```
1. Ausruestungsformular oeffnen
2. Jedes Geraet mit Inventarnummer und Status registrieren
3. Wartungstermine eintragen
4. Datensaetze speichern
```

#### Schritt 5: Taeglicher Betrieb

```
1. Anwesenheitsformular oeffnen
2. Fuer jeden Mitarbeiter den Tageseintrag erstellen:
   - Anwesend: Tagestyp 'lavorativa', Stunden eintragen
   - Abwesend: Tagestyp 'ferie', 'malattia' oder 'permesso'
3. Datensaetze speichern
4. Dashboard pruefen fuer Tagesuebersicht
```

<!-- IMAGE: Schematischer Arbeitsablauf von Einrichtung bis taeglichem Betrieb -->
> **Abb. 19**: Schematischer Arbeitsablauf der Baustellenverwaltung

### Massenberechnung durchfuehren

```
1. Dashboard oeffnen
2. Fundort und Jahr auswaehlen
3. Berechnungsmethode waehlen:
   a) DEM-Differenz: Beide DEM-Layer auswaehlen
   b) DEM + Polygon: DEM und Polygon-Layer auswaehlen
4. Auf "Berechnen" klicken
5. Ergebnisse (Flaeche und Volumen) ablesen
6. Auf "Ergebnis speichern" klicken, um den Eintrag zu archivieren
7. Berechnungsverlauf in der Tabelle pruefen
```

<!-- IMAGE: Massenberechnung mit DEM-Differenz-Ergebnis -->
> **Abb. 20**: Ergebnis einer DEM-Differenz-Berechnung mit gespeichertem Verlaufseintrag

---

## Haeufig gestellte Fragen (FAQ)

### Wie werden die Tageskosten im Anwesenheitsformular berechnet?

Die Tageskosten (costo_giornata) koennen manuell eingetragen werden. Eine kuenftige Version wird die automatische Berechnung basierend auf dem Tagessatz des Mitarbeiters und den geleisteten Stunden unterstuetzen.

### Kann ich das Dashboard fuer mehrere Fundorte gleichzeitig anzeigen?

Nein, das Dashboard zeigt immer nur die Daten des aktuell ausgewaehlten Fundorts. Sie koennen jedoch schnell zwischen Fundorten wechseln, indem Sie den Fundort im Auswahlfeld aendern.

### Werden die Budgetdaten im Kreisdiagramm in Echtzeit aktualisiert?

Ja. Das Kreisdiagramm wird bei jeder Aktualisierung des Dashboards neu gerendert. Es zeigt die tatsaechlichen Ausgaben (importo_effettivo) gruppiert nach Kategorie. Wenn noch keine tatsaechlichen Ausgaben erfasst sind, bleibt das Diagramm leer.

### Wie funktioniert der Wartungsalarm?

Das System vergleicht bei jeder Dashboard-Aktualisierung das Datum im Feld "Naechste Wartung" (data_prossima_manutenzione) mit dem heutigen Datum. Liegt das Wartungsdatum in der Vergangenheit und der Geraetestatus ist nicht 'fuori_uso', erscheint ein roter Warnhinweis mit der Anzahl ueberfaelliger Geraete.

### Benoetige ich matplotlib fuer das Dashboard?

Das Kreisdiagramm im Budgetbereich benoetigt **matplotlib**. Wenn matplotlib nicht installiert ist, funktioniert das Dashboard weiterhin -- nur das Diagramm wird nicht angezeigt. Alle numerischen Zusammenfassungen bleiben verfuegbar.

### Welche DEM-Formate werden fuer die Massenberechnung unterstuetzt?

Alle Rasterformate, die von QGIS unterstuetzt werden (GeoTIFF, ASC, IMG, usw.). Die DEM-Layer muessen bereits in das aktuelle QGIS-Projekt geladen sein, um in den Auswahlfeldern zu erscheinen.

---

## Fehlerbehebung

### Dashboard zeigt keine Daten an

**Symptom**: Alle Kennzahlen zeigen 0 oder sind leer.

**Loesungen**:
1. Pruefen, ob die Datenbankverbindung aktiv ist (DB Info in der Statusleiste)
2. Sicherstellen, dass ein Fundort im Auswahlfeld gewaehlt ist
3. Pruefen, ob fuer den gewaehlten Fundort und das Jahr tatsaechlich Daten erfasst wurden
4. Auf **Aktualisieren** klicken

### Massenberechnung schlaegt fehl

**Symptom**: Fehlermeldung bei Klick auf "Berechnen".

**Loesungen**:
1. Sicherstellen, dass die DEM-Layer im QGIS-Projekt geladen sind
2. Bei DEM-Differenz: Pruefen, ob beide DEMs die gleiche Aufloesung und Ausdehnung haben
3. Bei DEM + Polygon: Pruefen, ob DEM und Polygon dasselbe Koordinatenreferenzsystem haben
4. Sicherstellen, dass die Layer-Auswahlfelder nicht leer sind

### Personalformular speichert nicht

**Symptom**: Fehlermeldung beim Speichern eines neuen Personaldatensatzes.

**Loesungen**:
1. Pruefen, ob der Fundort (sito) ausgefuellt ist
2. Sicherstellen, dass ein gueltiges Einstellungsdatum im Format JJJJ-MM-TT eingegeben wurde
3. Datenbankverbindung ueberpruefen

### Kreisdiagramm wird nicht angezeigt

**Symptom**: Der Diagrammbereich im Dashboard bleibt leer.

**Loesungen**:
1. Pruefen, ob matplotlib installiert ist: `pip install matplotlib`
2. Sicherstellen, dass tatsaechliche Ausgaben (importo_effettivo) erfasst sind
3. QGIS neu starten, falls matplotlib nachtraeglich installiert wurde

---

## Technische Hinweise

### Quelldateien

| Datei | Beschreibung |
|-------|-------------|
| `tabs/Cantiere.py` | Dashboard-Controller |
| `tabs/Personale.py` | Personal-Controller |
| `tabs/Presenze.py` | Anwesenheits-Controller |
| `tabs/Attrezzature.py` | Ausruestungs-Controller |
| `tabs/Budget.py` | Budget-Controller |
| `gui/ui/Cantiere.ui` | Dashboard-Oberflaeche (Qt Designer) |
| `gui/ui/Personale.ui` | Personal-Oberflaeche |
| `gui/ui/Presenze.ui` | Anwesenheits-Oberflaeche |
| `gui/ui/Attrezzature.ui` | Ausruestungs-Oberflaeche |
| `gui/ui/Budget.ui` | Budget-Oberflaeche |
| `modules/db/entities/PERSONALE.py` | Personal-Entity-Klasse |
| `modules/db/entities/PRESENZE.py` | Anwesenheits-Entity-Klasse |
| `modules/db/entities/ATTREZZATURE.py` | Ausruestungs-Entity-Klasse |
| `modules/db/entities/BUDGET.py` | Budget-Entity-Klasse |

### Datenbanktabellen

| Tabelle | Beschreibung |
|---------|-------------|
| `personale_table` | Mitarbeiterstammdaten |
| `presenze_table` | Tagesanwesenheiten |
| `attrezzature_table` | Geraeteinventar |
| `budget_table` | Budgetplanung und -verfolgung |
| `computo_metrico_table` | Massenberechnungsergebnisse |

### Werkzeugleisten-Symbole

| Symbol | Datei | Aktion |
|--------|-------|--------|
| Cantiere | `resources/icons/iconCantiere.png` | runCantiere() |
| Personale | `resources/icons/iconPersonale.png` | runPersonale() |
| Presenze | `resources/icons/iconPresenze.png` | runPresenze() |
| Attrezzature | `resources/icons/iconAttrezzature.png` | runAttrezzature() |
| Budget | `resources/icons/iconBudget.png` | runBudget() |

### Kompatibilitaet

| Komponente | Mindestversion |
|------------|---------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| Python | 3.9+ |
| matplotlib | 3.0+ (optional, fuer Diagramme) |

---

*PyArchInit-Dokumentation - Baustellenverwaltung*
*Version: 5.0.x*
*Letzte Aktualisierung: Februar 2026*
