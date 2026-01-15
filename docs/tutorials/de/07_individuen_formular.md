# Tutorial 07: Individuenformular

## Einführung

Das **Individuenformular** ist das PyArchInit-Modul zur anthropologischen Dokumentation von bei der Ausgrabung gefundenen menschlichen Überresten. Dieses Formular erfasst Informationen über Geschlecht, Alter, Körperposition und Erhaltungszustand des Skeletts.

### Grundkonzepte

**Individuum in PyArchInit:**
- Ein Individuum ist eine Ansammlung von Knochenresten, die einer einzelnen Person zugeordnet werden können
- Es ist mit dem Grabformular verbunden (Bestattungskontext)
- Es ist mit dem Strukturformular verbunden (physische Struktur)
- Kann mit der Archäozoologie für spezifische Analysen verbunden werden

**Anthropologische Daten:**
- Biologische Geschlechtsschätzung
- Sterbealtersschätzung
- Position und Orientierung des Körpers
- Erhaltungszustand und Vollständigkeit

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **Individuenformular** (oder **Individual form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das Symbol **Individuen** klicken (menschliche Figur)

---

## Oberflächenübersicht

Das Formular hat ein in funktionale Bereiche gegliedertes Layout:

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | DB-Info | Datensatzstatus, Sortierung, Zähler |
| 3 | Identifikationsfelder | Fundort, Areal, SE, Individuennr. |
| 4 | Strukturverbindung | Kürzel und Strukturnummer |
| 5 | Tab-Bereich | Thematische Tabs für spezifische Daten |

---

## DBMS-Toolbar

Die Haupttoolbar bietet die Werkzeuge zur Datensatzverwaltung.

### Navigationsschaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| Erster | First rec | Zum ersten Datensatz |
| Vorheriger | Prev rec | Zum vorherigen Datensatz |
| Nächster | Next rec | Zum nächsten Datensatz |
| Letzter | Last rec | Zum letzten Datensatz |

### CRUD-Schaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| Neu | New record | Neuen Individuendatensatz erstellen |
| Speichern | Save | Änderungen speichern |
| Löschen | Delete | Aktuellen Datensatz löschen |

### Suchschaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| Neue Suche | New search | Neue Suche starten |
| Suche!!! | Search!!! | Suche ausführen |
| Sortieren | Order by | Ergebnisse sortieren |
| Alle anzeigen | View all | Alle Datensätze anzeigen |

### Spezielle Schaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| PDF | PDF export | In PDF exportieren |
| Verzeichnis | Open directory | Exportordner öffnen |

---

## Identifikationsfelder

Die Identifikationsfelder definieren das Individuum eindeutig in der Datenbank.

### Fundort

**Feld**: `comboBox_sito`
**Datenbank**: `sito`

Wählt den zugehörigen archäologischen Fundort aus.

### Areal

**Feld**: `comboBox_area`
**Datenbank**: `area`

Ausgrabungsareal innerhalb des Fundorts. Die Werte werden aus dem Thesaurus befüllt.

### SE

**Feld**: `comboBox_us`
**Datenbank**: `us`

Referenz-Stratigraphische Einheit.

### Individuennummer

**Feld**: `lineEdit_individuo`
**Datenbank**: `nr_individuo`

Fortlaufende Nummer des Individuums. Die nächste verfügbare Nummer wird automatisch vorgeschlagen.

**Hinweise:**
- Die Kombination Fundort + Areal + SE + Individuennr. muss eindeutig sein
- Die Nummer wird bei der Erstellung automatisch zugewiesen

### Strukturverbindung

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Strukturkürzel | `sigla_struttura` | Strukturkürzel (z.B. TM) |
| Strukturnr. | `nr_struttura` | Strukturnummer |

Diese Felder verbinden das Individuum mit der Grabstruktur.

---

## Erfassungsdaten

### Erfassungsdatum

**Feld**: `dateEdit_schedatura`
**Datenbank**: `data_schedatura`

Datum der Formularerstellung.

### Erfasser

**Feld**: `comboBox_schedatore`
**Datenbank**: `schedatore`

Name des Bearbeiters, der das Formular ausfüllt.

---

## Tab Beschreibende Daten

Der erste Tab enthält die grundlegenden anthropologischen Daten.

### Geschlechtsschätzung

**Feld**: `comboBox_sesso`
**Datenbank**: `sesso`

Biologische Geschlechtsschätzung basierend auf morphologischen Merkmalen.

**Werte:**
| Wert | Beschreibung |
|------|-------------|
| Männlich | Deutlich männliche Merkmale |
| Weiblich | Deutlich weibliche Merkmale |
| Wahrscheinlich männlich | Überwiegend männliche Merkmale |
| Wahrscheinlich weiblich | Überwiegend weibliche Merkmale |
| Unbestimmt | Nicht bestimmbar |

**Bestimmungskriterien:**
- Beckenmorphologie
- Schädelmorphologie
- Allgemeine Robustheit des Skeletts
- Knochenmaße

### Sterbealtersschätzung

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Mindestalter | `eta_min` | Untergrenze der Schätzung |
| Höchstalter | `eta_max` | Obergrenze der Schätzung |

**Schätzmethoden:**
- Schambeinsymphyse
- Facies auricularis
- Schädelnähte
- Zahnentwicklung (bei Subadulten)
- Knochenepiphysen (bei Subadulten)

### Altersklassen

**Feld**: `comboBox_classi_eta`
**Datenbank**: `classi_eta`

Klassifikation nach Altersstufen.

**Typische Werte:**
| Klasse | Ungefähres Alter |
|--------|------------------|
| Infans I | 0-6 Jahre |
| Infans II | 7-12 Jahre |
| Juvenis | 13-20 Jahre |
| Adultus | 21-40 Jahre |
| Maturus | 41-60 Jahre |
| Senilis | >60 Jahre |

### Beobachtungen

**Feld**: `textEdit_osservazioni`
**Datenbank**: `osservazioni`

Textfeld für spezifische anthropologische Notizen.

**Empfohlene Inhalte:**
- Beobachtete Pathologien
- Traumata
- Berufliche Marker
- Skelettanomalien
- Notizen zur Geschlechts- und Altersbestimmung

---

## Tab Orientierung und Position

Dieser Tab dokumentiert die Position und Orientierung des Körpers.

### Erhaltungszustand

| Feld | Datenbank | Werte |
|------|-----------|-------|
| Vollständig | `completo_si_no` | Ja / Nein |
| Gestört | `disturbato_si_no` | Ja / Nein |
| In Verbindung | `in_connessione_si_no` | Ja / Nein |

**Definitionen:**
- **Vollständig**: Alle anatomischen Bereiche sind vertreten
- **Gestört**: Anzeichen post-depositionaler Umlagerung
- **In Verbindung**: Gelenke sind erhalten

### Skelettlänge

**Feld**: `lineEdit_lunghezza`
**Datenbank**: `lunghezza_scheletro`

Gemessene Skelettlänge in situ (in cm oder m).

### Skelettposition

**Feld**: `comboBox_posizione_scheletro`
**Datenbank**: `posizione_scheletro`

Allgemeine Körperposition.

**Werte:**
- Rückenlage (auf dem Rücken)
- Bauchlage (mit Gesicht nach unten)
- Rechte Seitenlage
- Linke Seitenlage
- Hockerlage
- Irregulär

### Schädelposition

**Feld**: `comboBox_posizione_cranio`
**Datenbank**: `posizione_cranio`

Kopforientierung.

**Werte:**
- Nach rechts gewendet
- Nach links gewendet
- Nach oben gewendet
- Nach unten gewendet
- Nicht bestimmbar

### Position der oberen Extremitäten

**Feld**: `comboBox_arti_superiori`
**Datenbank**: `posizione_arti_superiori`

Armposition.

**Werte:**
- Gestreckt an den Seiten
- Auf dem Becken
- Auf der Brust
- Über der Brust gekreuzt
- Gemischt
- Nicht bestimmbar

### Position der unteren Extremitäten

**Feld**: `comboBox_arti_inferiori`
**Datenbank**: `posizione_arti_inferiori`

Beinposition.

**Werte:**
- Gestreckt
- Angewinkelt
- Gekreuzt
- Gespreizt
- Nicht bestimmbar

### Achsenorientierung

**Feld**: `comboBox_orientamento_asse`
**Datenbank**: `orientamento_asse`

Orientierung der Körperlängsachse.

**Werte:**
- N-S (Kopf im Norden)
- S-N (Kopf im Süden)
- E-W (Kopf im Osten)
- W-E (Kopf im Westen)
- NE-SW, NW-SE, usw.

### Azimutorientierung

**Feld**: `lineEdit_azimut`
**Datenbank**: `orientamento_azimut`

Numerischer Azimutwert in Grad (0-360).

---

## Tab Osteologische Überreste

Dieser Tab ist der Dokumentation der anatomischen Bereiche gewidmet.

### Bereichsdokumentation

Ermöglicht die Erfassung von:
- Vorhandensein/Fehlen einzelner Knochenelemente
- Erhaltungszustand nach Bereich
- Seite (rechts/links) für paarige Elemente

**Hauptbereiche:**
| Bereich | Elemente |
|---------|----------|
| Schädel | Kalvarium, Mandibula, Zähne |
| Wirbelsäule | Hals-, Brust-, Lendenwirbel, Sakrum |
| Thorax | Rippen, Sternum |
| Obere Extremitäten | Schlüsselbeine, Schulterblätter, Humeri, Radius, Ulna, Hände |
| Becken | Os coxae |
| Untere Extremitäten | Femora, Tibia, Fibula, Füße |

---

## Tab Weitere Eigenschaften

Dieser Tab enthält zusätzliche Informationen.

### Inhalte

- Spezifische metrische Merkmale
- Anthropometrische Indizes
- Detaillierte Pathologien
- Beziehungen zu anderen Individuen

---

## Export und Druck

### PDF-Export

Die PDF-Schaltfläche öffnet ein Feld mit Optionen:

| Option | Beschreibung |
|--------|-------------|
| Individuenliste | Kurzliste |
| Individuenformulare | Vollständige detaillierte Formulare |
| Drucken | Generiert das PDF |

### PDF-Formularinhalt

Das PDF-Formular enthält:
- Identifikationsdaten
- Anthropologische Daten (Geschlecht, Alter)
- Position und Orientierung
- Erhaltungszustand
- Beobachtungen

---

## Operativer Arbeitsablauf

### Neues Individuum erstellen

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "Neuer Datensatz" klicken
   - Individuennummer wird automatisch vorgeschlagen

3. **Identifikationsdaten**
   ```
   Fundort: Nekropole von Isola Sacra
   Areal: 1
   SE: 150
   Individuennr.: 1
   Strukturkürzel: TM
   Strukturnr.: 45
   ```

4. **Erfassungsdaten**
   ```
   Datum: 15.03.2024
   Erfasser: M. Müller
   ```

5. **Anthropologische Daten** (Tab 1)
   ```
   Geschlecht: Männlich
   Min. Alter: 35
   Max. Alter: 45
   Altersklasse: Adultus

   Beobachtungen: Geschätzte Körpergröße 170 cm.
   Lendenwirbel-Arthrose. Multiple Karies.
   ```

6. **Orientierung und Position** (Tab 2)
   ```
   Vollständig: Ja
   Gestört: Nein
   In Verbindung: Ja
   Länge: 165 cm
   Position: Rückenlage
   Schädel: Nach rechts gewendet
   Obere Extremitäten: Gestreckt an den Seiten
   Untere Extremitäten: Gestreckt
   Orientierung: E-W
   Azimut: 90
   ```

7. **Osteologische Überreste** (Tab 3)
   - Vorhandene Bereiche dokumentieren

8. **Speichern**
   - Auf "Speichern" klicken

### Individuen suchen

1. Auf "Neue Suche" klicken
2. Kriterien ausfüllen:
   - Fundort
   - Geschlecht
   - Altersklasse
   - Position
3. Auf "Suche" klicken
4. Zwischen Ergebnissen navigieren

---

## Beziehungen zu anderen Formularen

| Formular | Beziehung |
|----------|-----------|
| **Fundortformular** | Der Fundort enthält die Individuen |
| **Strukturformular** | Die Struktur enthält das Individuum |
| **Grabformular** | Das Grab dokumentiert den Kontext |
| **Archäozoologie** | Für spezifische osteologische Analysen |

### Empfohlener Arbeitsablauf

1. **Strukturformular** für das Grab erstellen
2. **Grabformular** erstellen
3. **Individuenformular** für jedes Skelett erstellen
4. Individuum mit Grab und Struktur verbinden

---

## Best Practices

### Geschlechtsbestimmung

- Mehrere morphologische Indikatoren verwenden
- Zuverlässigkeitsgrad angeben
- Verwendete Kriterien in den Beobachtungen spezifizieren

### Altersschätzung

- Immer einen Bereich (Min-Max) angeben
- Verwendete Methoden angeben
- Bei Subadulten Zahn- und Epiphysenentwicklung spezifizieren

### Position und Orientierung

- Vor der Bergung mit Fotos dokumentieren
- Kardinale Richtungen verwenden
- Azimut mit Kompass messen

### Erhaltung

- Taphonomische Verluste von antiken Entnahmen unterscheiden
- Post-depositionelle Störungen dokumentieren
- Bergungsbedingungen erfassen

---

## Fehlerbehebung

### Problem: Doppelte Individuennummer

**Ursache**: Es existiert bereits ein Individuum mit derselben Nummer.

**Lösung**:
1. Vorhandene Nummerierung überprüfen
2. Automatisch vorgeschlagene Nummer verwenden
3. Areal und SE kontrollieren

### Problem: Struktur nicht gefunden

**Ursache**: Die Struktur existiert nicht oder hat ein anderes Kürzel.

**Lösung**:
1. Strukturformular-Existenz überprüfen
2. Kürzel und Nummer kontrollieren
3. Falls nötig, zuerst die Struktur erstellen

### Problem: Altersklassen nicht verfügbar

**Ursache**: Thesaurus nicht konfiguriert.

**Lösung**:
1. Thesaurus-Konfiguration überprüfen
2. Eingestellte Sprache kontrollieren
3. Administrator kontaktieren

---

## Referenzen

### Datenbank

- **Tabelle**: `individui_table`
- **Mapper-Klasse**: `SCHEDAIND`
- **ID**: `id_scheda_ind`

### Quelldateien

- **UI**: `gui/ui/Schedaind.ui`
- **Controller**: `tabs/Schedaind.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

## Video-Tutorial

### Übersicht Individuenformular
**Dauer**: 5-6 Minuten
- Oberflächenpräsentation
- Hauptfelder
- Navigation zwischen Tabs

[Platzhalter Video: video_panoramica_individui.mp4]

### Vollständige anthropologische Erfassung
**Dauer**: 12-15 Minuten
- Neuen Datensatz erstellen
- Geschlechts- und Altersbestimmung
- Positionsdokumentation
- Osteologische Überreste erfassen

[Platzhalter Video: video_schedatura_individui.mp4]

### Grab-Individuum-Verbindung
**Dauer**: 5-6 Minuten
- Beziehung zwischen Formularen
- Korrekter Arbeitsablauf
- Best Practices

[Platzhalter Video: video_collegamento_tomba_individuo.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
