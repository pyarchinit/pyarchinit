# Tutorial 21: UT-Formular - Topographische Einheiten

## Einfuehrung

Das **UT-Formular** (Topographische Einheiten) ist das PyArchInit-Modul zur Dokumentation archaeologischer Oberflaechenprospektion (Survey). Es ermoeglicht die Erfassung von Daten zu Materialkonzentrationen, Gelaendeanomalien und waehrend der Prospektionen identifizierten Fundstellen.

### Grundkonzepte

**Topographische Einheit (UT):**
- Abgegrenztes Areal mit homogenen archaeologischen Merkmalen
- Waehrend Oberflaechenprospektion identifiziert
- Definiert durch Materialkonzentration oder sichtbare Anomalien

**Prospektion (Survey):**
- Systematische Gelaendeerkundung
- Datensammlung zu antiker menschlicher Praesenz
- Dokumentation ohne Grabung

---

## Zugriff auf das Formular

### Ueber Menu
1. Menu **PyArchInit** in der QGIS-Menuleiste
2. **UT-Formular** (oder **TU form**) auswaehlen

### Ueber Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **UT**-Symbol klicken

---

## Oberflaechenuebersicht

Das Formular ist in mehrere Tabs zur Dokumentation aller Prospektionsaspekte unterteilt.

### Haupt-Tabs

| # | Tab | Beschreibung |
|---|-----|-------------|
| 1 | Identifikation | Projekt, UT-Nr., Lokalisierung |
| 2 | Beschreibung | Definition, Beschreibung, Interpretation |
| 3 | UT-Daten | Bedingungen, Methodik, Daten |
| 4 | Analyse | Archaeologisches Potential und Risiko |

### Haupt-Toolbar

| Schaltflaeche | Funktion |
|---------------|----------|
| Erster | Zum ersten Datensatz |
| Vorheriger | Vorheriger Datensatz |
| Naechster | Naechster Datensatz |
| Letzter | Zum letzten Datensatz |
| Suche | Erweiterte Suche |
| Speichern | Datensatz speichern |
| Loeschen | Datensatz loeschen |
| PDF | PDF-Export der Karte |
| **PDF-Liste** | UT-Liste als PDF exportieren |
| **GNA-Export** | Export im GNA-Format |
| Layer anzeigen | Layer auf Karte anzeigen |

---

## Identifikationsfelder

### Projekt

**Feld**: `comboBox_progetto`
**Datenbank**: `progetto`

Name des Prospektionsprojekts.

### UT-Nummer

**Feld**: `comboBox_nr_ut`
**Datenbank**: `nr_ut`

Fortlaufende Nummer der Topographischen Einheit.

### UT Buchstaben

**Feld**: `lineEdit_ut_letterale`
**Datenbank**: `ut_letterale`

Optionales alphabetisches Suffix (z.B. UT 15a, 15b).

---

## Lokalisierungsfelder

### Administrative Daten

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Land | `nazione` | Staat |
| Region | `regione` | Verwaltungsregion |
| Provinz | `provincia` | Provinz |
| Gemeinde | `comune` | Gemeinde |
| Ortsteil | `frazione` | Ortsteil/Ortschaft |
| Ortschaft | `localita` | Lokaler Ortsname |
| Adresse | `indirizzo` | Strasse/Weg |
| Hausnr. | `nr_civico` | Hausnummer |

### Kartographische Daten

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Topogr. Karte | `carta_topo_igm` | Kartenblatt IGM |
| CTR-Karte | `carta_ctr` | CTR-Element |
| Katasterblatt | `foglio_catastale` | Katasterreferenz |

### Koordinaten

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Geogr. Koordinaten | `coord_geografiche` | Lat/Long (Format: lat, lon) |
| Ebene Koordinaten | `coord_piane` | UTM/Gauss-Krueger (Format: x, y) |
| Hoehe | `quota` | Hoehe ue.NN |
| Koordinatenpraezision | `coordinate_precision` | GPS-Genauigkeit in Metern |

**WICHTIG**: Die Koordinaten werden fuer die Heatmap-Generierung verwendet. Mindestens eines von `coord_geografiche` oder `coord_piane` muss fuer jede UT ausgefuellt werden.

---

## Beschreibende Felder

### UT-Definition

**Feld**: `comboBox_def_ut`
**Datenbank**: `def_ut`
**Thesaurus**: Code 12.7

Typologische Klassifikation der UT. Werte werden aus dem Thesaurus geladen und automatisch in die aktuelle Sprache uebersetzt.

**Standardwerte:**
| Code | Deutsch | Englisch |
|------|---------|----------|
| scatter | Materialstreuung | Material scatter |
| site | Archaeologische Fundstelle | Archaeological site |
| anomaly | Gelaendeanomalie | Terrain anomaly |
| structure | Aufgehende Struktur | Outcropping structure |
| concentration | Fundkonzentration | Finds concentration |
| traces | Anthropogene Spuren | Anthropic traces |
| findspot | Einzelfund | Sporadic find |
| negative | Negativer Befund | Negative result |

### UT-Beschreibung

**Feld**: `textEdit_descrizione`
**Datenbank**: `descrizione_ut`

Detaillierte Beschreibung der Topographischen Einheit.

**Inhalte:**
- Ausdehnung und Form des Bereichs
- Materialdichte
- Gelaendemerkmale
- Sichtbarkeit und Bedingungen

### UT-Interpretation

**Feld**: `textEdit_interpretazione`
**Datenbank**: `interpretazione_ut`

Funktionale/historische Interpretation.

---

## Survey-Felder mit Thesaurus

Die folgenden Felder nutzen das Thesaurus-System fuer standardisierte, in 7 Sprachen (DE, IT, EN, ES, FR, AR, CA) uebersetzte Terminologie.

### Survey-Typ (12.1)

**Feld**: `comboBox_survey_type`
**Datenbank**: `survey_type`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| intensive | Intensive Prospektion | Systematische intensive Begehung |
| extensive | Extensive Prospektion | Stichprobenartige Begehung |
| targeted | Gezielte Prospektion | Untersuchung spezifischer Bereiche |
| random | Zufallsstichprobe | Zufaellige Stichprobenmethodik |

### Vegetationsbedeckung (12.2)

**Feld**: `comboBox_vegetation_coverage`
**Datenbank**: `vegetation_coverage`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| none | Keine Vegetation | Offener Boden |
| sparse | Spaerliche Vegetation | Bedeckung < 25% |
| moderate | Maessige Vegetation | Bedeckung 25-50% |
| dense | Dichte Vegetation | Bedeckung 50-75% |
| very_dense | Sehr dichte Vegetation | Bedeckung > 75% |

### GPS-Methode (12.3)

**Feld**: `comboBox_gps_method`
**Datenbank**: `gps_method`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| handheld | Handheld GPS | Handgehaltenes GPS-Geraet |
| dgps | Differential GPS | DGPS mit Basisstation |
| rtk | RTK GPS | Echtzeit-Kinematik |
| total_station | Totalstation | Totalstation-Vermessung |

### Oberflaechenzustand (12.4)

**Feld**: `comboBox_surface_condition`
**Datenbank**: `surface_condition`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| ploughed | Gepfluegt | Frisch gepfluegtes Feld |
| stubble | Stoppelfeld | Ernterueckstaende vorhanden |
| pasture | Weide | Gruenland/Weide |
| woodland | Wald | Bewaldetes Gebiet |
| urban | Urban | Bebautes Gebiet |

### Zugaenglichkeit (12.5)

**Feld**: `comboBox_accessibility`
**Datenbank**: `accessibility`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| easy | Leicht zugaenglich | Keine Einschraenkungen |
| moderate_access | Maessig zugaenglich | Einige Schwierigkeiten |
| difficult | Schwer zugaenglich | Erhebliche Probleme |
| restricted | Eingeschraenkter Zugang | Nur mit Genehmigung |

### Wetterbedingungen (12.6)

**Feld**: `comboBox_weather_conditions`
**Datenbank**: `weather_conditions`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| sunny | Sonnig | Klares Wetter |
| cloudy | Bewoelkt | Bedeckte Bedingungen |
| rainy | Regnerisch | Regen waehrend Prospektion |
| windy | Windig | Starker Wind |

---

## Umweltdaten

### Sichtbarkeitsprozentsatz

**Feld**: `spinBox_visibility_percent`
**Datenbank**: `visibility_percent`

Bodensichtbarkeit in Prozent (0-100%). Numerischer Wert, wichtig fuer die Berechnung des archaeologischen Potentials.

### Gelaendeneigung

**Feld**: `lineEdit_andamento_terreno_pendenza`
**Datenbank**: `andamento_terreno_pendenza`

Gelaendemorphologie und Neigung.

### Bodennutzung

**Feld**: `lineEdit_utilizzo_suolo_vegetazione`
**Datenbank**: `utilizzo_suolo_vegetazione`

Bodennutzung zum Zeitpunkt der Prospektion.

---

## Materialdaten

### UT-Abmessungen

**Feld**: `lineEdit_dimensioni_ut`
**Datenbank**: `dimensioni_ut`

Flaechenausdehnung in qm.

### Funde pro qm

**Feld**: `lineEdit_rep_per_mq`
**Datenbank**: `rep_per_mq`

Materialdichte pro Quadratmeter. Kritischer Wert fuer die Potentialberechnung.

### Datierende Funde

**Feld**: `lineEdit_rep_datanti`
**Datenbank**: `rep_datanti`

Beschreibung diagnostischer Materialien.

---

## Chronologie

### Periode I

| Feld | Datenbank |
|------|-----------|
| Periode I | `periodo_I` |
| Datierung I | `datazione_I` |
| Interpretation I | `interpretazione_I` |

### Periode II

| Feld | Datenbank |
|------|-----------|
| Periode II | `periodo_II` |
| Datierung II | `datazione_II` |
| Interpretation II | `interpretazione_II` |

---

## Analyse-Tab - Archaeologisches Potential und Risiko

Der **Analyse**-Tab bietet erweiterte Werkzeuge zur automatischen Berechnung des archaeologischen Potentials und Risikos.

### Archaeologisches Potential

Das System berechnet einen Score von 0 bis 100 basierend auf verschiedenen gewichteten Faktoren:

| Faktor | Gewicht | Beschreibung | Berechnung |
|--------|---------|-------------|------------|
| UT-Definition | 30% | Art der archaeologischen Evidenz | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, usw. |
| Historische Periode | 25% | Materialchronologie | Aeltere Perioden gewichten mehr (Praehistorisch = 90, Roemisch = 85, Mittelalterlich = 70, usw.) |
| Funddichte | 20% | Materialien pro qm | >10/qm = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Oberflaechenzustand | 15% | Sichtbarkeit und Zugaenglichkeit | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Dokumentation | 10% | Dokumentationsqualitaet | Fotos vorhanden = +20, Bibliographie = +30, Untersuchungen = +50 |

**Score-Klassifizierung:**

| Score | Stufe | Farbe | Bedeutung |
|-------|-------|-------|-----------|
| 80-100 | Hoch | Gruen | Hohe Wahrscheinlichkeit bedeutender Ablagerungen |
| 60-79 | Mittel-Hoch | Gelb-Gruen | Gute Wahrscheinlichkeit, Ueberpruefung empfohlen |
| 40-59 | Mittel | Orange | Maessige Wahrscheinlichkeit |
| 20-39 | Niedrig | Rot | Geringe Wahrscheinlichkeit |
| 0-19 | Nicht bewertbar | Grau | Ungenugende Daten |

### Archaeologisches Risiko

Bewertet das Risiko von Beeintraechtigung/Verlust des Kulturerbes:

| Faktor | Gewicht | Beschreibung | Berechnung |
|--------|---------|-------------|------------|
| Zugaenglichkeit | 25% | Leichtigkeit des Zugangs zum Gebiet | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Bodennutzung | 25% | Landwirtschaftliche/bauliche Aktivitaeten | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Bestehende Auflagen | 20% | Rechtlicher Schutz | Keine Auflagen = 80, Landschaftsschutz = 40, Denkmalschutz = 10 |
| Fruehere Untersuchungen | 15% | Kenntnisstand | Keine Untersuchung = 60, Prospektion = 40, Grabung = 20 |
| Potential | 15% | Umgekehrt proportional zum Potential | Hohes Potential = hohes Verlustrisiko |

**Risiko-Klassifizierung:**

| Score | Stufe | Farbe | Empfohlene Massnahme |
|-------|-------|-------|----------------------|
| 75-100 | Hoch | Rot | Dringender Eingriff, sofortige Schutzmassnahmen |
| 50-74 | Mittel | Orange | Aktives Monitoring, Schutz erwaegen |
| 25-49 | Niedrig | Gelb | Periodisches Monitoring |
| 0-24 | Null | Gruen | Kein unmittelbarer Eingriff erforderlich |

### Datenbank-Felder fuer die Analyse

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Potential-Score | `potential_score` | Berechneter Wert 0-100 |
| Risiko-Score | `risk_score` | Berechneter Wert 0-100 |
| Potential-Faktoren | `potential_factors` | JSON mit Faktordetails |
| Risiko-Faktoren | `risk_factors` | JSON mit Faktordetails |
| Analyse-Datum | `analysis_date` | Zeitstempel der Berechnung |
| Analyse-Methode | `analysis_method` | Verwendeter Algorithmus |

---

## Geometrische UT-Layer

PyArchInit verwaltet drei Geometrietypen fuer Topographische Einheiten:

### Geometrische Tabellen

| Layer | Tabelle | Geometrietyp | Verwendung |
|-------|---------|--------------|------------|
| UT Punkte | `pyarchinit_ut_point` | Point | Punktuelle Lokalisierung |
| UT Linien | `pyarchinit_ut_line` | LineString | Trassen, Wege |
| UT Polygone | `pyarchinit_ut_polygon` | Polygon | Streuungsbereiche |

### UT-Layer erstellen

1. **Ueber QGIS Browser:**
   - Datenbank im Browser oeffnen
   - Tabelle `pyarchinit_ut_point/line/polygon` finden
   - Auf die Karte ziehen

2. **Ueber PyArchInit Menu:**
   - Menu **PyArchInit** > **GIS Tools** > **UT-Layer laden**
   - Geometrietyp auswaehlen

### UT-Geometrie-Verknuepfung

Jeder Geometrie-Datensatz ist mit der UT-Karte verknuepft durch:

| Feld | Beschreibung |
|------|-------------|
| `progetto` | Projektname (muss uebereinstimmen) |
| `nr_ut` | UT-Nummer (muss uebereinstimmen) |

### Arbeitsablauf Geometrie-Erstellung

1. **Bearbeitung aktivieren** auf dem gewuenschten UT-Layer
2. **Geometrie zeichnen** auf der Karte
3. **Attribute ausfuellen** `progetto` und `nr_ut`
4. **Layer speichern**
5. **Verknuepfung ueberpruefen** vom UT-Formular aus

---

## Heatmap-Generierung

Das Heatmap-Generierungsmodul ermoeglicht die Visualisierung der raeumlichen Verteilung von archaeologischem Potential und Risiko.

### Mindestanforderungen

- **Mindestens 2 UTs** mit gueltigen Koordinaten (`coord_geografiche` ODER `coord_piane`)
- **Berechnete Scores** fuer Potential und/oder Risiko
- **Definiertes KBS** im QGIS-Projekt

### Interpolationsmethoden

| Methode | Beschreibung | Anwendungsfall |
|---------|-------------|----------------|
| **KDE** (Kernel Density) | Gauss'sche Kernel-Dichteschaetzung | Kontinuierliche Verteilung, viele Punkte |
| **IDW** (Inverse Distance) | Umgekehrte Distanzgewichtung | Sparse Daten, wichtige Punktwerte |
| **Grid** | Interpolation auf regulaerem Raster | Systematische Analysen |

### Heatmap-Parameter

| Parameter | Standardwert | Beschreibung |
|-----------|--------------|-------------|
| Zellgroesse | 50 m | Rasteraufloesung |
| Bandbreite (KDE) | Auto | Einflussradius |
| Potenz (IDW) | 2 | Gewichtungsexponent |

### Generierungsverfahren

1. **Vom UT-Formular aus:**
   - Zum **Analyse**-Tab gehen
   - Ueberpruefen, dass die Scores berechnet sind
   - Auf **Heatmap generieren** klicken

2. **Parameterauswahl:**
   - Typ: Potential oder Risiko
   - Methode: KDE, IDW oder Grid
   - Zellgroesse: typischerweise 25-100 m

3. **Ausgabe:**
   - Raster-Layer wird zu QGIS hinzugefuegt
   - Gespeichert in `pyarchinit_Raster_folder`
   - Symbologie wird automatisch angewendet

### Heatmap mit Polygonmaske (GNA)

Um Heatmaps **innerhalb eines Projektgebiets** zu generieren (z.B. Untersuchungsperimeter):

1. **Polygon vorbereiten** des Projektgebiets
2. **GNA-Export verwenden** (siehe naechster Abschnitt)
3. Das System **maskiert** die Heatmap automatisch auf das Polygon

---

## GNA-Export - Nationales Geoportal Archaeologie

### Was ist GNA?

Das **Geoportale Nazionale per l'Archeologia** (GNA) ist das Informationssystem des italienischen Kulturministeriums zur Verwaltung territorialer archaeologischer Daten. PyArchInit unterstuetzt den Export im GNA-Standard-GeoPackage-Format.

### GNA GeoPackage-Struktur

| Layer | Typ | Beschreibung |
|-------|-----|-------------|
| **MOPR** | Polygon | Projektgebiet/Perimeter |
| **MOSI** | Point/Polygon | Archaeologische Fundstellen (UT) |
| **VRP** | MultiPolygon | Karte des Archaeologischen Potentials |
| **VRD** | MultiPolygon | Karte des Archaeologischen Risikos |

### Feldzuordnung UT nach MOSI GNA

| GNA-Feld | PyArchInit UT-Feld | Hinweise |
|----------|-------------------|----------|
| ID | `{progetto}_{nr_ut}` | Zusammengesetzte Kennung |
| AMA | `def_ut` | GNA-kontrolliertes Vokabular |
| OGD | `interpretazione_ut` | Objektdefinition |
| OGT | `geometria` | Geometrietyp |
| DES | `descrizione_ut` | Beschreibung (max 10000 Zeichen) |
| OGM | `metodo_rilievo_e_ricognizione` | Erfassungsmethode |
| DTSI | `periodo_I` -> Datum | Startdatum (negativ fuer v.Chr.) |
| DTSF | `periodo_II` -> Datum | Enddatum |
| PRVN | `nazione` | Land |
| PVCR | `regione` | Region |
| PVCP | `provincia` | Provinz |
| PVCC | `comune` | Gemeinde |
| LCDQ | `quota` | Hoehe ue.NN |

### VRP-Klassifizierung (Potential)

| Bereich | GNA-Code | Bezeichnung | Farbe |
|---------|----------|-------------|-------|
| 0-20 | NV | Nicht bewertbar | Grau |
| 20-40 | NU | Null | Gruen |
| 40-60 | BA | Niedrig | Gelb |
| 60-80 | ME | Mittel | Orange |
| 80-100 | AL | Hoch | Rot |

### VRD-Klassifizierung (Risiko)

| Bereich | GNA-Code | Bezeichnung | Farbe |
|---------|----------|-------------|-------|
| 0-25 | NU | Null | Gruen |
| 25-50 | BA | Niedrig | Gelb |
| 50-75 | ME | Mittel | Orange |
| 75-100 | AL | Hoch | Rot |

### GNA-Export-Verfahren

1. **Datenvorbereitung:**
   - Ueberpruefen, dass alle UTs Koordinaten haben
   - Potential-/Risiko-Scores berechnen
   - Polygon des Projektgebiets (MOPR) vorbereiten

2. **Export starten:**
   - Vom UT-Formular auf **GNA-Export** klicken
   - Oder Menu **PyArchInit** > **GNA** > **Export**

3. **Konfiguration:**
   ```
   Projekt: [Projekt auswaehlen]
   Projektgebiet: [MOPR-Polygon-Layer auswaehlen]
   Ausgabe: [Pfad zur .gpkg-Datei]

   [x] MOSI exportieren (Fundstellen)
   [x] VRP generieren (Potential)
   [x] VRD generieren (Risiko)

   Heatmap-Methode: KDE
   Zellgroesse: 50 m
   ```

4. **Ausfuehrung:**
   - Auf **Exportieren** klicken
   - Generierung abwarten (kann einige Minuten dauern)
   - Das GeoPackage wird im angegebenen Pfad gespeichert

5. **Ausgabe ueberpruefen:**
   - GeoPackage in QGIS oeffnen
   - Layer MOPR, MOSI, VRP, VRD ueberpruefen
   - Kontrollieren, dass VRP/VRD-Geometrien auf MOPR zugeschnitten sind

### GNA-Validierung

Um die Ausgabe gegen GNA-Spezifikationen zu validieren:

1. GeoPackage im **offiziellen GNA-Template** laden
2. Ueberpruefen, dass die Layer erkannt werden
3. Kontrollierte Vokabulare pruefen
4. Geometrische Beziehungen verifizieren (MOSI innerhalb MOPR)

---

## PDF-Export

### Einzelne UT-Karte

Exportiert das vollstaendige UT-Formular im professionellen PDF-Format.

**Inhalt:**
- Kopfzeile mit Projekt und UT-Nummer
- Abschnitt Identifikation
- Abschnitt Lokalisierung
- Abschnitt Gelaende
- Abschnitt Survey-Daten
- Abschnitt Chronologie
- Abschnitt Analyse (Potential/Risiko mit farbigen Balken)
- Abschnitt Dokumentation

**Verfahren:**
1. UT-Datensatz auswaehlen
2. Auf die **PDF**-Schaltflaeche in der Toolbar klicken
3. Das PDF wird in `pyarchinit_PDF_folder` gespeichert

### UT-Liste (PDF-Liste)

Exportiert eine tabellarische Liste aller UTs im Querformat.

**Spalten:**
- UT, Projekt, Definition, Interpretation
- Gemeinde, Koordinaten, Periode I, Periode II
- Funde/qm, Sichtbarkeit, Potential, Risiko

**Verfahren:**
1. Zu exportierende UTs laden (Suche oder alle anzeigen)
2. Auf die **PDF-Liste**-Schaltflaeche in der Toolbar klicken
3. Das PDF wird als `Elenco_UT.pdf` gespeichert

### UT-Analysebericht

Generiert einen detaillierten Bericht der Potential-/Risikoanalyse.

**Inhalt:**
1. UT-Identifikationsdaten
2. Abschnitt Archaeologisches Potential
   - Score mit grafischer Anzeige
   - Beschreibender Narrativtext
   - Faktorentabelle mit Beitraegen
3. Abschnitt Archaeologisches Risiko
   - Score mit grafischer Anzeige
   - Narrativtext mit Empfehlungen
   - Faktorentabelle mit Beitraegen
4. Abschnitt Methodik

---

## Vollstaendiger operativer Arbeitsablauf

### Phase 1: Projekt-Setup

1. **Neues Projekt erstellen** in PyArchInit oder bestehendes verwenden
2. **Untersuchungsgebiet definieren** (MOPR-Polygon)
3. **KBS des QGIS-Projekts konfigurieren**

### Phase 2: UT-Erfassung im Feld

1. **UT-Formular oeffnen**
2. **Neuer Datensatz** (Klick auf "New Record")
3. **Identifikationsdaten ausfuellen:**
   ```
   Projekt: Survey Tibertal 2024
   UT-Nr.: 25
   ```

4. **Lokalisierung ausfuellen:**
   ```
   Region: Latium
   Provinz: Rom
   Gemeinde: Fiano Romano
   Ortschaft: Colle Alto
   Geogr. Koordinaten: 42.1234, 12.5678
   Hoehe: 125 m
   GPS-Praezision: 3 m
   ```

5. **Beschreibung ausfuellen** (mit Thesaurus):
   ```
   Definition: Fundkonzentration
   Beschreibung: Elliptischer Bereich von ca. 50x30 m
   mit Konzentration von Keramikfragmenten
   und Ziegeln an suedexponiertem Hang...
   ```

6. **Survey-Daten ausfuellen** (mit Thesaurus):
   ```
   Survey-Typ: Intensive Prospektion
   Vegetationsbedeckung: Spaerlich
   GPS-Methode: Differential GPS
   Oberflaechenzustand: Gepfluegt
   Zugaenglichkeit: Leicht zugaenglich
   Wetterbedingungen: Sonnig
   Sichtbarkeit: 80%
   Datum: 15.04.2024
   Verantwortlich: Team A
   ```

7. **Materialien und Chronologie ausfuellen:**
   ```
   Abmessungen: 1500 qm
   Funde/qm: 5-8
   Datierende Funde: Gebrauchskeramik,
   Italische Sigillata, Ziegel

   Periode I: Roemisch
   Datierung I: 1.-2. Jh. n.Chr.
   Interpretation I: Villa rustica
   ```

8. **Speichern** (Klick auf "Save")

### Phase 3: Geometrie-Erstellung

1. **Layer laden** `pyarchinit_ut_polygon`
2. **Bearbeitung aktivieren**
3. **Perimeter zeichnen** der UT auf der Karte
4. **Attribute ausfuellen**: progetto, nr_ut
5. **Layer speichern**

### Phase 4: Analyse

1. **Analyse-Tab oeffnen** im UT-Formular
2. **Automatisch berechnete Scores ueberpruefen**
3. **Heatmap generieren** falls erforderlich
4. **PDF-Bericht exportieren** der Analyse

### Phase 5: GNA-Export (falls erforderlich)

1. **Datenvollstaendigkeit ueberpruefen** fuer alle UTs
2. **MOPR-Polygon vorbereiten** des Projektgebiets
3. **GNA-Export ausfuehren**
4. **Ausgabe validieren** gegen GNA-Spezifikationen

---

## Tipps & Tricks

### Arbeitsablauf-Optimierung

1. **Thesaurus vorbereiten** vor Beginn der Prospektionen
2. **Projektvorlagen verwenden** mit voreingestellten gemeinsamen Daten
3. **Koordinaten synchronisieren** vom GPS zum Feld `coord_geografiche`
4. **Haeufig speichern** waehrend der Eingabe

### Datenqualitaet verbessern

1. **ALLE relevanten Felder ausfuellen** fuer jede UT
2. **Immer Thesaurus verwenden** statt Freitext
3. **Koordinaten auf Karte ueberpruefen** vor dem Speichern
4. **Jede UT fotografisch dokumentieren**

### Heatmap-Optimierung

1. **Angemessene Zellgroesse**: 25-50m fuer kleine Gebiete, 100-200m fuer grosse Gebiete verwenden
2. **KDE-Methode** fuer kontinuierliche und homogene Verteilungen
3. **IDW-Methode** wenn Punktwerte kritisch sind
4. **Immer ueberpruefen**, dass Koordinaten korrekt sind vor der Generierung

### Effizienter GNA-Export

1. **MOPR-Polygon vorbereiten** im Voraus als separaten Layer
2. **Ueberpruefen, dass alle UTs** gueltige Koordinaten haben
3. **Scores berechnen** vor dem Export
4. **Beschreibende Dateinamen verwenden** fuer GeoPackages

### Mehrbenutzerverwaltung

1. **Konventionen definieren** fuer gemeinsame UT-Nummerierung
2. **PostgreSQL-Datenbank verwenden** fuer gleichzeitigen Zugriff
3. **Daten periodisch synchronisieren**
4. **Aenderungen dokumentieren** in den Notizfeldern

---

## Fehlerbehebung

### Problem: Leere Thesaurus-Comboboxen

**Symptome:** Die Dropdown-Menus fuer survey_type, vegetation usw. sind leer.

**Ursachen:**
- Thesaurus-Eintraege nicht in der Datenbank vorhanden
- Falscher Sprachcode
- Thesaurus-Tabelle nicht aktualisiert

**Loesungen:**
1. Menu **PyArchInit** > **Datenbank** > **Datenbank aktualisieren**
2. Tabelle `pyarchinit_thesaurus_sigle` auf Eintraege fuer `ut_table` ueberpruefen
3. Spracheinstellungen kontrollieren
4. Falls erforderlich, Thesaurus aus Template neu importieren

### Problem: Ungueltige Koordinaten

**Symptome:** Fehler beim Speichern oder Koordinaten an falscher Position angezeigt.

**Ursachen:**
- Falsches Format (Komma vs. Dezimalpunkt)
- Nicht uebereinstimmendes Bezugssystem
- Lat/Lon-Reihenfolge vertauscht

**Loesungen:**
1. Korrektes Format `coord_geografiche`: `42.1234, 12.5678` (lat, lon)
2. Korrektes Format `coord_piane`: `1234567.89, 4567890.12` (x, y)
3. Immer Punkt als Dezimaltrennzeichen verwenden
4. KBS des QGIS-Projekts ueberpruefen

### Problem: UT nicht auf Karte sichtbar

**Symptome:** Nach dem Speichern erscheint die UT nicht auf der Karte.

**Ursachen:**
- Geometrie nicht im Layer erstellt
- Attribute `progetto`/`nr_ut` stimmen nicht ueberein
- Layer nicht geladen oder ausgeblendet
- Unterschiedliches KBS zwischen Layer und Projekt

**Loesungen:**
1. Ueberpruefen, dass der Layer `pyarchinit_ut_point/polygon` existiert
2. Kontrollieren, dass die Attribute korrekt ausgefuellt sind
3. Layer-Sichtbarkeit im Layer-Panel aktivieren
4. "Auf Layer zoomen" verwenden, um die Ausdehnung zu ueberpruefen

### Problem: Heatmap nicht generiert

**Symptome:** Fehler "Mindestens 2 Punkte mit gueltigen Koordinaten erforderlich".

**Ursachen:**
- Weniger als 2 UTs mit Koordinaten
- Koordinaten im falschen Format
- Koordinatenfelder leer

**Loesungen:**
1. Ueberpruefen, dass mindestens 2 UTs `coord_geografiche` ODER `coord_piane` ausgefuellt haben
2. Koordinatenformat pruefen (Dezimalpunkt, korrekte Reihenfolge)
3. Scores vor der Heatmap-Generierung neu berechnen
4. Ueberpruefen, dass die Felder keine Sonderzeichen enthalten

### Problem: Potential-/Risiko-Score nicht berechnet

**Symptome:** Die Felder potential_score und risk_score sind leer oder null.

**Ursachen:**
- Pflichtfelder nicht ausgefuellt
- Thesaurus-Werte nicht erkannt
- Berechnungsfehler

**Loesungen:**
1. Mindestens ausfuellen: `def_ut`, `periodo_I`, `visibility_percent`
2. Werte aus dem Thesaurus verwenden (kein Freitext)
3. Datensatz speichern und erneut oeffnen
4. QGIS-Logs auf Fehler ueberpruefen

### Problem: GNA-Export fehlgeschlagen

**Symptome:** Das GeoPackage wird nicht erstellt oder ist unvollstaendig.

**Ursachen:**
- GNA-Modul nicht verfuegbar
- UT-Daten unvollstaendig
- MOPR-Polygon ungueltig
- Unzureichende Schreibrechte

**Loesungen:**
1. Ueberpruefen, dass das Modul `modules/gna` installiert ist
2. Kontrollieren, dass alle UTs gueltige Koordinaten haben
3. Ueberpruefen, dass das MOPR-Polygon gueltig ist (keine Selbstueberschneidungen)
4. Berechtigungen auf den Ausgabeordner pruefen
5. Ausreichend Speicherplatz sicherstellen

### Problem: PDF-Export mit fehlenden Feldern

**Symptome:** Das generierte PDF zeigt einige Felder nicht an oder zeigt falsche Werte.

**Ursachen:**
- Datenbankfelder nicht aktualisiert
- Veraltete Datenbankschema-Version
- Daten nicht vor dem Export gespeichert

**Loesungen:**
1. Datensatz vor dem Export speichern
2. Datenbank bei Bedarf aktualisieren
3. Ueberpruefen, dass die neuen Felder (v4.9.67+) in der Tabelle existieren

### Problem: Qt6/QGIS 4.x Fehler

**Symptome:** Plugin laedt nicht auf QGIS 4.x mit Fehler `AllDockWidgetFeatures`.

**Ursachen:**
- Qt5/Qt6-Inkompatibilitaet
- UI-Datei nicht aktualisiert

**Loesungen:**
1. PyArchInit auf die neueste Version aktualisieren
2. Die Datei `UT_ui.ui` muss explizite Flags statt `AllDockWidgetFeatures` verwenden

---

## Referenzen

### Datenbank

- **Tabelle**: `ut_table`
- **Mapper-Klasse**: `UT`
- **ID**: `id_ut`

### Geometrische Tabellen

- **Punkte**: `pyarchinit_ut_point`
- **Linien**: `pyarchinit_ut_line`
- **Polygone**: `pyarchinit_ut_polygon`

### Quelldateien

| Datei | Beschreibung |
|-------|-------------|
| `gui/ui/UT_ui.ui` | Qt-Benutzeroberflaeche |
| `tabs/UT.py` | Hauptcontroller |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | PDF-Export Karten |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | PDF-Export Analyse |
| `modules/analysis/ut_potential.py` | Potentialberechnung |
| `modules/analysis/ut_risk.py` | Risikoberechnung |
| `modules/analysis/ut_heatmap_generator.py` | Heatmap-Generierung |
| `modules/gna/gna_exporter.py` | GNA-Export |
| `modules/gna/gna_vocabulary_mapper.py` | GNA-Vokabular-Mapping |

### UT Thesaurus-Codes

| Code | Feld | Beschreibung |
|------|------|-------------|
| 12.1 | survey_type | Survey-Typ |
| 12.2 | vegetation_coverage | Vegetationsbedeckung |
| 12.3 | gps_method | GPS-Methode |
| 12.4 | surface_condition | Oberflaechenzustand |
| 12.5 | accessibility | Zugaenglichkeit |
| 12.6 | weather_conditions | Wetterbedingungen |
| 12.7 | def_ut | UT-Definition |

---

## Video-Tutorials

### Prospektionsdokumentation
**Dauer**: 15-18 Minuten
- UT-Erfassung
- Survey-Daten mit Thesaurus
- Geolokalisierung

### Potential- und Risikoanalyse
**Dauer**: 10-12 Minuten
- Automatische Score-Berechnung
- Ergebnisinterpretation
- Heatmap-Generierung

### GNA-Export
**Dauer**: 12-15 Minuten
- Datenvorbereitung
- Export-Konfiguration
- Ausgabevalidierung

### PDF-Berichtsexport
**Dauer**: 8-10 Minuten
- Standard-UT-Karte
- UT-Liste
- Analysebericht mit Karten

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit v4.9.68 - Archaeologisches Datenverwaltungssystem*
