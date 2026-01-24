# Tutorial 21: UT-Formular - Topographische Einheiten

## Einführung

Das **UT-Formular** (Topographische Einheiten) ist das PyArchInit-Modul zur Dokumentation archäologischer Oberflächenprospektionen (Survey). Es ermöglicht die Erfassung von Daten zu Materialkonzentrationen, Geländeanomalien und während der Prospektionen identifizierten Fundstellen.

### Grundkonzepte

**Topographische Einheit (UT):**
- Abgegrenztes Areal mit homogenen archäologischen Merkmalen
- Während Oberflächenprospektionen identifiziert
- Definiert durch Materialkonzentration oder sichtbare Anomalien

**Prospektion (Survey):**
- Systematische Geländeerkundung
- Datensammlung zu antiker menschlicher Präsenz
- Dokumentation ohne Grabung

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **UT-Formular** auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **UT**-Symbol klicken

---

## Oberflächenübersicht

Das Formular ist in mehrere Tabs zur Dokumentation aller Prospektionsaspekte unterteilt.

### Haupt-Tabs

| # | Tab | Beschreibung |
|---|-----|-------------|
| 1 | Identifikation | Projekt, UT-Nr., Lokalisierung |
| 2 | Beschreibung | Definition, Beschreibung, Interpretation |
| 3 | UT-Daten | Bedingungen, Methodik, Daten |
| 4 | Analyse | Archäologisches Potential und Risiko |

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
| Adresse | `indirizzo` | Straße/Weg |
| Hausnr. | `nr_civico` | Hausnummer |

### Kartographische Daten

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Topogr. Karte | `carta_topo_igm` | Kartenblatt |
| CTR-Karte | `carta_ctr` | CTR-Element |
| Katasterblatt | `foglio_catastale` | Katasterreferenz |

### Koordinaten

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Geogr. Koordinaten | `coord_geografiche` | Lat/Long |
| Ebene Koordinaten | `coord_piane` | UTM/Gauß-Krüger |
| Höhe | `quota` | Höhe ü.NN |
| Koordinatenpräzision | `coordinate_precision` | GPS-Genauigkeit |

---

## Beschreibende Felder

### UT-Definition ⭐ NEU

**Feld**: `comboBox_def_ut`
**Datenbank**: `def_ut`
**Thesaurus**: Code 12.7

Typologische Klassifikation der UT. Werte werden aus dem Thesaurus geladen und automatisch in die aktuelle Sprache übersetzt.

**Standardwerte:**
| Code | Deutsch | Italienisch |
|------|---------|------------|
| scatter | Materialstreuung | Area di dispersione materiali |
| site | Archäologische Fundstelle | Sito archeologico |
| anomaly | Geländeanomalie | Anomalia del terreno |
| structure | Aufgehende Struktur | Struttura affiorante |
| concentration | Fundkonzentration | Concentrazione reperti |
| traces | Anthropogene Spuren | Tracce antropiche |
| findspot | Einzelfund | Rinvenimento sporadico |
| negative | Negativer Befund | Esito negativo |

### UT-Beschreibung

**Feld**: `textEdit_descrizione`
**Datenbank**: `descrizione_ut`

Detaillierte Beschreibung der Topographischen Einheit.

**Inhalte:**
- Ausdehnung und Form des Bereichs
- Materialdichte
- Geländemerkmale
- Sichtbarkeit und Bedingungen

### UT-Interpretation

**Feld**: `textEdit_interpretazione`
**Datenbank**: `interpretazione_ut`

Funktionale/historische Interpretation.

---

## Thesaurus Survey-Felder ⭐ NEU

Die folgenden Felder nutzen das Thesaurus-System für standardisierte, in 7 Sprachen (DE, IT, EN, ES, FR, AR, CA) übersetzte Terminologie.

### Survey-Typ (12.1)

**Feld**: `comboBox_survey_type`
**Datenbank**: `survey_type`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| intensive | Intensive Prospektion | Systematische Begehung |
| extensive | Extensive Prospektion | Übersichtsbegehung |
| targeted | Gezielte Prospektion | Untersuchung spezifischer Bereiche |
| random | Zufallsstichprobe | Stichprobenmethodik |

### Vegetationsbedeckung (12.2)

**Feld**: `comboBox_vegetation_coverage`
**Datenbank**: `vegetation_coverage`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| none | Keine Vegetation | Offener Boden |
| sparse | Spärliche Vegetation | Bedeckung < 25% |
| moderate | Mäßige Vegetation | Bedeckung 25-50% |
| dense | Dichte Vegetation | Bedeckung 50-75% |
| very_dense | Sehr dichte Vegetation | Bedeckung > 75% |

### GPS-Methode (12.3)

**Feld**: `comboBox_gps_method`
**Datenbank**: `gps_method`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| handheld | Handheld GPS | Handgehaltenes GPS-Gerät |
| dgps | Differential GPS | DGPS mit Basisstation |
| rtk | RTK GPS | Echtzeit-Kinematik |
| total_station | Totalstation | Totalstation-Vermessung |

### Oberflächenzustand (12.4)

**Feld**: `comboBox_surface_condition`
**Datenbank**: `surface_condition`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| ploughed | Gepflügt | Frisch gepflügtes Feld |
| stubble | Stoppelfeld | Ernterückstände vorhanden |
| pasture | Weide | Grünland/Weide |
| woodland | Wald | Bewaldetes Gebiet |
| urban | Urban | Bebautes Gebiet |

### Zugänglichkeit (12.5)

**Feld**: `comboBox_accessibility`
**Datenbank**: `accessibility`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| easy | Leicht zugänglich | Keine Einschränkungen |
| moderate_access | Mäßig zugänglich | Einige Schwierigkeiten |
| difficult | Schwer zugänglich | Erhebliche Probleme |
| restricted | Eingeschränkter Zugang | Nur mit Genehmigung |

### Wetterbedingungen (12.6)

**Feld**: `comboBox_weather_conditions`
**Datenbank**: `weather_conditions`

| Code | Deutsch | Beschreibung |
|------|---------|-------------|
| sunny | Sonnig | Klar und sonnig |
| cloudy | Bewölkt | Bedeckte Bedingungen |
| rainy | Regnerisch | Regen während Prospektion |
| windy | Windig | Starker Wind |

---

## Umweltdaten

### Sichtbarkeitsprozentsatz

**Feld**: `spinBox_visibility_percent`
**Datenbank**: `visibility_percent`

Bodensichtbarkeit in Prozent (0-100%). Numerischer Wert.

### Geländeneigung

**Feld**: `lineEdit_andamento_terreno_pendenza`
**Datenbank**: `andamento_terreno_pendenza`

Geländemorphologie und Neigung.

### Bodennutzung

**Feld**: `lineEdit_utilizzo_suolo_vegetazione`
**Datenbank**: `utilizzo_suolo_vegetazione`

Bodennutzung zum Zeitpunkt der Prospektion.

---

## Materialdaten

### UT-Abmessungen

**Feld**: `lineEdit_dimensioni_ut`
**Datenbank**: `dimensioni_ut`

Flächenausdehnung in qm.

### Funde pro qm

**Feld**: `lineEdit_rep_per_mq`
**Datenbank**: `rep_per_mq`

Materialdichte pro Quadratmeter.

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

## Analyse-Tab ⭐ NEU

Der **Analyse**-Tab bietet erweiterte Werkzeuge zur automatischen Berechnung des archäologischen Potentials und Risikos.

### Archäologisches Potential

Das System berechnet einen Score von 0 bis 100 basierend auf:

| Faktor | Gewicht | Beschreibung |
|--------|---------|-------------|
| UT-Definition | 30% | Art der archäologischen Evidenz |
| Historische Periode | 25% | Materialchronologie |
| Funddichte | 20% | Materialien pro qm |
| Oberflächenzustand | 15% | Sichtbarkeit und Zugänglichkeit |
| Dokumentation | 10% | Dokumentationsqualität |

**Anzeige:**
- Farbiger Fortschrittsbalken (grün = hoch, gelb = mittel, rot = niedrig)
- Detaillierte Faktorentabelle mit Einzelwerten
- Automatischer Beschreibungstext mit Interpretation

### Archäologisches Risiko

Bewertet das Risiko von Beeinträchtigung/Verlust des Kulturguts:

| Faktor | Gewicht | Beschreibung |
|--------|---------|-------------|
| Zugänglichkeit | 25% | Leichtigkeit des Zugangs |
| Bodennutzung | 25% | Landwirtschaftliche/bauliche Aktivitäten |
| Bestehende Auflagen | 20% | Rechtlicher Schutz |
| Frühere Untersuchungen | 15% | Kenntnisstand |
| Sichtbarkeit | 15% | Exposition der Fundstelle |

### Heatmap-Generierung

Die Schaltfläche **Heatmap generieren** erstellt Rasterlayer mit:
- **Potential-Heatmap**: Räumliche Verteilung des archäologischen Potentials
- **Risiko-Heatmap**: Gefährdungskarte

**Verfügbare Methoden:**
- Kernel Density Estimation (KDE)
- Inverse Distance Weighting (IDW)
- Natural Neighbor

---

## PDF-Export ⭐ VERBESSERT

### Standard UT-Formular

Exportiert das vollständige UT-Formular mit allen ausgefüllten Feldern.

### UT-Analysebericht

Generiert einen PDF-Bericht mit:

1. **UT-Identifikationsdaten**
2. **Archäologisches Potential-Sektion**
   - Score mit grafischer Anzeige
   - Beschreibender Narrativtext
   - Faktorentabelle mit Beiträgen
   - Potential-Heatmap-Bild (falls generiert)
3. **Archäologisches Risiko-Sektion**
   - Score mit grafischer Anzeige
   - Narrativtext mit Empfehlungen
   - Faktorentabelle mit Beiträgen
   - Risiko-Heatmap-Bild (falls generiert)
4. **Methodik-Sektion**
   - Beschreibung der verwendeten Algorithmen
   - Hinweise zu Faktorgewichtungen

Der Bericht ist in allen 7 unterstützten Sprachen verfügbar.

---

## Operativer Arbeitsablauf

### Neue UT registrieren

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "New Record" klicken

3. **Identifikationsdaten**
   ```
   Projekt: Survey Tibertal 2024
   UT-Nr.: 25
   ```

4. **Lokalisierung**
   ```
   Region: Latium
   Provinz: Rom
   Gemeinde: Fiano Romano
   Ortschaft: Colle Alto
   Koord.: 42.1234 N, 12.5678 E
   Höhe: 125 m
   ```

5. **Beschreibung** (mit Thesaurus)
   ```
   Definition: Fundkonzentration (aus Thesaurus)
   Beschreibung: Elliptischer Bereich von ca. 50x30 m
   mit Konzentration von Keramikfragmenten
   und Ziegeln an südexponiertem Hang...
   ```

6. **Survey-Daten** (mit Thesaurus)
   ```
   Survey-Typ: Intensive Prospektion
   Vegetationsbedeckung: Spärlich
   GPS-Methode: Differential GPS
   Oberflächenzustand: Gepflügt
   Zugänglichkeit: Leicht zugänglich
   Wetterbedingungen: Sonnig
   Sichtbarkeit: 80%
   Datum: 15.04.2024
   Verantwortlich: Team A
   ```

7. **Materialien und Chronologie**
   ```
   Abmessungen: 1500 qm
   Funde/qm: 5-8
   Datierende Funde: Gebrauchskeramik,
   Italische Sigillata, Ziegel

   Periode I: Römisch
   Datierung I: 1.-2. Jh. n. Chr.
   Interpretation I: Villa rustica
   ```

8. **Analyse** (Analyse-Tab)
   - Potential-Score prüfen
   - Risiko-Score prüfen
   - Heatmap bei Bedarf generieren

9. **Speichern**
   - Auf "Save" klicken

---

## GIS-Integration

Das UT-Formular ist eng mit QGIS integriert:

- **UT-Layer**: Geometrie-Visualisierung
- **Verknüpfte Attribute**: Daten aus dem Formular
- **Auswahl von Karte**: Klick auf Geometrie öffnet Formular
- **Heatmap als Layer**: Generierte Karten werden als Rasterlayer gespeichert

---

## Best Practices

### Thesaurus-Nutzung

- Immer Thesaurus-Werte für Konsistenz bevorzugen
- Werte werden automatisch in Benutzersprache übersetzt
- Für neue Werte, diese zuerst im Thesaurus hinzufügen

### Nomenklatur

- Fortlaufende Nummerierung pro Projekt
- Suffixe für Unterteilungen verwenden
- Konventionen dokumentieren

### Geolokalisierung

- Differenzial-GPS wenn möglich verwenden
- Immer Methode und Präzision angeben
- Koordinaten auf Karte überprüfen

### Dokumentation

- Jede UT fotografieren
- Planimetrische Skizzen anfertigen
- Sichtbarkeitsbedingungen erfassen

### Analyse

- Berechnete Scores immer verifizieren
- Heatmaps für vollständige Projekte generieren
- Berichte zur Dokumentation exportieren

---

## UT Thesaurus-Codes

| Code | Feld | Beschreibung |
|------|------|-------------|
| 12.1 | survey_type | Survey-Typ |
| 12.2 | vegetation_coverage | Vegetationsbedeckung |
| 12.3 | gps_method | GPS-Methode |
| 12.4 | surface_condition | Oberflächenzustand |
| 12.5 | accessibility | Zugänglichkeit |
| 12.6 | weather_conditions | Wetterbedingungen |
| 12.7 | def_ut | UT-Definition |

---

## Fehlerbehebung

### Problem: Leere Comboboxen

**Ursache**: Thesaurus-Einträge nicht in Datenbank vorhanden.

**Lösung**:
1. Datenbank über "Update database" aktualisieren
2. Überprüfen, dass `pyarchinit_thesaurus_sigle` Tabelle Einträge für `ut_table` enthält
3. Sprachcode in Einstellungen prüfen

### Problem: Ungültige Koordinaten

**Ursache**: Falsches Format oder Bezugssystem.

**Lösung**:
1. Format überprüfen (DD oder DMS)
2. Bezugssystem kontrollieren
3. QGIS-Umrechnungstool verwenden

### Problem: UT nicht auf Karte sichtbar

**Ursache**: Keine Geometrie zugeordnet.

**Lösung**:
1. Überprüfen, dass UT-Layer existiert
2. Prüfen, dass Datensatz Geometrie hat
3. Layer-Projektion überprüfen

### Problem: Heatmap nicht generiert

**Ursache**: Unzureichende Daten oder Berechnungsfehler.

**Lösung**:
1. Überprüfen, dass mindestens 3 UTs mit vollständigen Daten existieren
2. Prüfen, dass Geometrien gültig sind
3. Verfügbaren Speicherplatz prüfen

---

## Referenzen

### Datenbank

- **Tabelle**: `ut_table`
- **Mapper-Klasse**: `UT`
- **ID**: `id_ut`

### Quelldateien

- **UI**: `gui/ui/UT_ui.ui`
- **Controller**: `tabs/UT.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_UTsheet_pdf.py`
- **Analyse-PDF**: `modules/utility/pyarchinit_exp_UT_analysis_pdf.py`
- **Potential-Berechnung**: `modules/analysis/ut_potential.py`
- **Risiko-Berechnung**: `modules/analysis/ut_risk.py`
- **Heatmap-Generator**: `modules/analysis/ut_heatmap_generator.py`

---

## Video-Tutorial

### Prospektionsdokumentation
**Dauer**: 15-18 Minuten
- UT-Erfassung
- Survey-Daten mit Thesaurus
- Geolokalisierung

[Platzhalter Video: video_ut_survey.mp4]

### Potential- und Risikoanalyse
**Dauer**: 10-12 Minuten
- Automatische Score-Berechnung
- Ergebnisinterpretation
- Heatmap-Generierung

[Platzhalter Video: video_ut_analysis.mp4]

### PDF-Berichtsexport
**Dauer**: 8-10 Minuten
- Standard-UT-Formular
- Analysebericht mit Karten
- Ausgabe-Anpassung

[Platzhalter Video: video_ut_pdf.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit v4.9.68 - Archäologisches Datenverwaltungssystem*
