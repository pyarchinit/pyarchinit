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
2. **UT-Formular** (oder **TU form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **UT**-Symbol klicken

---

## Oberflächenübersicht

Das Formular enthält zahlreiche Felder zur Dokumentation aller Aspekte der Prospektion.

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | Identifikationsfelder | Projekt, UT-Nr. |
| 3 | Lokalisierung | Geographische und administrative Daten |
| 4 | Beschreibung | Definition, Beschreibung, Interpretation |
| 5 | Survey-Daten | Bedingungen, Methodik |
| 6 | Chronologie | Perioden und Datierungen |

---

## Identifikationsfelder

### Projekt

**Feld**: `lineEdit_progetto`
**Datenbank**: `progetto`

Name des Prospektionsprojekts.

### UT-Nummer

**Feld**: `lineEdit_nr_ut`
**Datenbank**: `nr_ut`

Fortlaufende Nummer der Topographischen Einheit.

### UT Buchstaben

**Feld**: `lineEdit_ut_letterale`
**Datenbank**: `ut_letterale`

Eventuelles alphabetisches Suffix (z.B. UT 15a, 15b).

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
| GPS-Methode | `gps_method` | Erfassungsart |

---

## Beschreibende Felder

### UT-Definition

**Feld**: `comboBox_def_ut`
**Datenbank**: `def_ut`

Typologische Klassifikation der UT.

**Werte:**
- Materialkonzentration
- Fragmentbereich
- Geländeanomalie
- Aufgehende Struktur
- Archäologische Fundstelle

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

## Umweltdaten

### Geländebeschaffenheit

**Feld**: `comboBox_terreno`
**Datenbank**: `andamento_terreno_pendenza`

Morphologie und Neigung.

**Werte:**
- Eben
- Leichte Neigung
- Mittlere Neigung
- Starke Neigung
- Terrassiert

### Bodennutzung

**Feld**: `comboBox_suolo`
**Datenbank**: `utilizzo_suolo_vegetazione`

Bodennutzung zum Zeitpunkt der Prospektion.

**Werte:**
- Ackerland
- Wiese/Weide
- Weinberg
- Olivenhain
- Brache
- Wald
- Urban

### Bodenbeschreibung

**Feld**: `textEdit_suolo`
**Datenbank**: `descrizione_empirica_suolo`

Beobachtete pedologische Eigenschaften.

### Ortsbeschreibung

**Feld**: `textEdit_luogo`
**Datenbank**: `descrizione_luogo`

Landschaftskontext.

---

## Survey-Daten

### Prospektionsmethode

**Feld**: `comboBox_metodo`
**Datenbank**: `metodo_rilievo_e_ricognizione`

Angewandte Methodik.

**Werte:**
- Systematische Prospektion
- Extensive Prospektion
- Gezielte Prospektion
- Fundmeldungskontrolle

### Survey-Typ

**Feld**: `comboBox_survey_type`
**Datenbank**: `survey_type`

Prospektionsart.

### Sichtbarkeit

**Feld**: `spinBox_visibility`
**Datenbank**: `visibility_percent`

Prozentsatz der Bodensichtbarkeit (0-100%).

### Vegetationsbedeckung

**Feld**: `comboBox_vegetation`
**Datenbank**: `vegetation_coverage`

Grad der Vegetationsbedeckung.

### Oberflächenzustand

**Feld**: `comboBox_surface`
**Datenbank**: `surface_condition`

Zustand der Oberfläche.

**Werte:**
- Frisch gepflügt
- Gepflügt, nicht gefräst
- Niedriges Gras
- Hohes Gras
- Stoppeln

### Zugänglichkeit

**Feld**: `comboBox_accessibility`
**Datenbank**: `accessibility`

Leichtigkeit des Zugangs zum Bereich.

### Datum

**Feld**: `dateEdit_data`
**Datenbank**: `data`

Datum der Prospektion.

### Uhrzeit/Wetter

**Feld**: `lineEdit_meteo`
**Datenbank**: `ora_meteo`

Wetterbedingungen und Uhrzeit.

### Verantwortlicher

**Feld**: `comboBox_responsabile`
**Datenbank**: `responsabile`

Prospektionsverantwortlicher.

### Team

**Feld**: `textEdit_team`
**Datenbank**: `team_members`

Teammitglieder.

---

## Materialdaten

### UT-Abmessungen

**Feld**: `lineEdit_dimensioni`
**Datenbank**: `dimensioni_ut`

Ausdehnung in qm.

### Funde pro qm

**Feld**: `lineEdit_rep_mq`
**Datenbank**: `rep_per_mq`

Materialdichte.

### Datierende Funde

**Feld**: `textEdit_rep_datanti`
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

## Weitere Felder

### Geometrie

**Feld**: `comboBox_geometria`
**Datenbank**: `geometria`

Form der UT.

### Bibliographie

**Feld**: `textEdit_bibliografia`
**Datenbank**: `bibliografia`

Bibliographische Verweise.

### Dokumentation

**Feld**: `textEdit_documentazione`
**Datenbank**: `documentazione`

Erstellte Dokumentation (Fotos, Zeichnungen).

### Foto-Dokumentation

**Feld**: `textEdit_photo_doc`
**Datenbank**: `photo_documentation`

Liste der fotografischen Dokumentation.

### Schutz/Auflagen

**Feld**: `textEdit_vincoli`
**Datenbank**: `enti_tutela_vincoli`

Auflagen und Schutzbehörden.

### Voruntersuchungen

**Feld**: `textEdit_indagini`
**Datenbank**: `indagini_preliminari`

Bereits durchgeführte Untersuchungen.

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

5. **Beschreibung**
   ```
   Definition: Materialkonzentration
   Beschreibung: Elliptischer Bereich von ca. 50x30 m
   mit Konzentration von Keramikfragmenten
   und Ziegeln an südexponiertem Hang...
   ```

6. **Survey-Daten**
   ```
   Methode: Systematische Prospektion
   Sichtbarkeit: 80%
   Zustand: Frisch gepflügt
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

8. **Speichern**
   - Auf "Save" klicken

---

## GIS-Integration

Das UT-Formular ist eng mit QGIS integriert:

- **UT-Layer**: Geometrie-Visualisierung
- **Verknüpfte Attribute**: Daten aus dem Formular
- **Auswahl von Karte**: Klick auf Geometrie öffnet Formular

---

## PDF-Export

Das Formular unterstützt den PDF-Export für:
- Einzelne UT-Formulare
- Listen nach Projekt
- Survey-Berichte

---

## Best Practices

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

### Materialien

- Diagnostische Proben sammeln
- Dichte pro Fläche schätzen
- Räumliche Verteilung dokumentieren

---

## Fehlerbehebung

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

---

## Video-Tutorial

### Prospektionsdokumentation
**Dauer**: 15-18 Minuten
- UT-Erfassung
- Survey-Daten
- Geolokalisierung

[Platzhalter Video: video_ut_survey.mp4]

### GIS-Integration Survey
**Dauer**: 10-12 Minuten
- Layer und Attribute
- Ergebnisvisualisierung
- Räumliche Analyse

[Platzhalter Video: video_ut_gis.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
