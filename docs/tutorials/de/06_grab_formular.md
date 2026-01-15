# Tutorial 06: Grabformular

## Einführung

Das **Grabformular** ist das PyArchInit-Modul zur Dokumentation archäologischer Bestattungen. Dieses Werkzeug ermöglicht die Erfassung aller Aspekte eines Grabes: von der Grabstruktur bis zum Ritus, von der Beigabe bis zu den bestatteten Individuen.

### Grundkonzepte

**Grab in PyArchInit:**
- Ein Grab ist eine Bestattungsstruktur, die ein oder mehrere Individuen enthält
- Es ist mit dem Strukturformular verbunden (die physische Struktur der Bestattung)
- Es ist mit dem Individuenformular verbunden (für anthropologische Daten)
- Es dokumentiert Ritus, Beigaben und Depositionsmerkmale

**Beziehungen:**
```
Grab → Struktur (physischer Behälter)
     → Individuum/en (menschliche Überreste)
     → Beigaben (Begleitobjekte)
     → Fundinventar (zugehörige Funde)
```

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **Grabformular** (oder **Grave form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das Symbol **Grab** klicken (Bestattungssymbol)

---

## Oberflächenübersicht

Das Formular hat ein in funktionale Bereiche gegliedertes Layout:

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | DB-Info | Datensatzstatus, Sortierung, Zähler |
| 3 | Identifikationsfelder | Fundort, Areal, Formularnummer, Struktur |
| 4 | Individuenfelder | Verbindung zum Individuum |
| 5 | Tab-Bereich | Thematische Tabs für spezifische Daten |

---

## Identifikationsfelder

Die Identifikationsfelder definieren das Grab eindeutig in der Datenbank.

### Fundort

**Feld**: `comboBox_sito`
**Datenbank**: `sito`

Wählt den zugehörigen archäologischen Fundort aus.

### Areal

**Feld**: `comboBox_area`
**Datenbank**: `area`

Ausgrabungsareal innerhalb des Fundorts.

### Formularnummer

**Feld**: `lineEdit_nr_scheda`
**Datenbank**: `nr_scheda_taf`

Fortlaufende Nummer des Grabformulars. Die nächste verfügbare Nummer wird automatisch vorgeschlagen.

### Kürzel und Strukturnummer

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Strukturkürzel | `sigla_struttura` | Kürzel der Struktur (z.B. TM, TB) |
| Strukturnr. | `nr_struttura` | Nummer der Struktur |

Diese Felder verbinden das Grab mit dem entsprechenden Strukturformular.

### Individuennummer

**Feld**: `comboBox_nr_individuo`
**Datenbank**: `nr_individuo`

Nummer des bestatteten Individuums. Verbindet das Grab mit dem Individuenformular.

**Hinweise:**
- Ein Grab kann mehrere Individuen enthalten (Mehrfachbestattung)
- Das Menü zeigt die für die ausgewählte Struktur verfügbaren Individuen

---

## Tab Beschreibende Daten

Der erste Tab enthält die grundlegenden Felder zur Beschreibung der Bestattung.

### Ritus

**Feld**: `comboBox_rito`
**Datenbank**: `rito`

Art des praktizierten Bestattungsrituals.

**Typische Werte:**
| Ritus | Beschreibung |
|-------|-------------|
| Inhumation | Deposition des vollständigen Körpers |
| Kremation | Einäscherung der Überreste |
| Primäre Einäscherung | Kremation vor Ort |
| Sekundäre Einäscherung | Kremation anderswo und Deposition |
| Gemischt | Kombination von Riten |
| Unbestimmt | Nicht bestimmbar |

### Grabtyp

**Feld**: `comboBox_tipo_sepoltura`
**Datenbank**: `tipo_sepoltura`

Typologische Klassifikation der Bestattung.

**Beispiele:**
- Einfaches Erdgrab
- Kastengrab
- Kammergrab
- Ziegelgrab (alla cappuccina)
- Enchytrismos-Grab
- Sarkophag
- Ossuar

### Depositionstyp

**Feld**: `comboBox_tipo_deposizione`
**Datenbank**: `tipo_deposizione`

Art der Körperdeposition.

**Werte:**
- Primär (direkte Deposition)
- Sekundär (Reduktion/Verlagerung)
- Mehrfach simultan
- Mehrfach sukzessiv

### Erhaltungszustand

**Feld**: `comboBox_stato_conservazione`
**Datenbank**: `stato_di_conservazione`

Bewertung des Erhaltungszustands.

**Skala:**
- Ausgezeichnet
- Gut
- Mittelmäßig
- Schlecht
- Sehr schlecht

### Beschreibung

**Feld**: `textEdit_descrizione`
**Datenbank**: `descrizione_taf`

Detaillierte Beschreibung des Grabes.

**Empfohlene Inhalte:**
- Form und Abmessungen der Grube
- Orientierung
- Tiefe
- Merkmale der Verfüllung
- Zustand zum Zeitpunkt der Ausgrabung

### Interpretation

**Feld**: `textEdit_interpretazione`
**Datenbank**: `interpretazione_taf`

Historisch-archäologische Interpretation der Bestattung.

---

## Grabeigenschaften

### Grabmale

**Feld**: `comboBox_segnacoli`
**Datenbank**: `segnacoli`

Vorhandensein und Art von Grabmarkierungen.

**Werte:**
- Nicht vorhanden
- Stele
- Cippus
- Tumulus
- Umfriedung
- Andere

### Libationskanal

**Feld**: `comboBox_canale_libatorio`
**Datenbank**: `canale_libatorio_si_no`

Vorhandensein eines Kanals für rituelle Libationen.

**Werte:** Ja / Nein

### Abdeckung

**Feld**: `comboBox_copertura_tipo`
**Datenbank**: `copertura_tipo`

Art der Grababdeckung.

**Beispiele:**
- Dachziegel
- Steinplatten
- Holzbretter
- Erde
- Nicht vorhanden

### Überrestbehälter

**Feld**: `comboBox_tipo_contenitore`
**Datenbank**: `tipo_contenitore_resti`

Art des Behälters für die Überreste.

**Beispiele:**
- Erdgrube
- Holzkiste
- Steinkiste
- Amphore
- Urne
- Sarkophag

### Externe Objekte

**Feld**: `comboBox_oggetti_esterno`
**Datenbank**: `oggetti_rinvenuti_esterno`

Außerhalb des Grabes gefundene, aber damit assoziierte Objekte.

---

## Tab Beigaben

Dieser Tab verwaltet die Dokumentation der Grabbeigaben.

### Beigabenvorhandensein

**Feld**: `comboBox_corredo_presenza`
**Datenbank**: `corredo_presenza`

Gibt an, ob das Grab Beigaben enthielt.

**Werte:**
- Ja
- Nein
- Wahrscheinlich
- Entfernt

### Beigabentyp

**Feld**: `comboBox_corredo_tipo`
**Datenbank**: `corredo_tipo`

Allgemeine Klassifikation der Beigaben.

**Kategorien:**
- Persönlich (Schmuck, Fibeln)
- Rituell (Gefäße, Lampen)
- Symbolisch (Münzen, Amulette)
- Instrumental (Werkzeuge)
- Gemischt

### Beigabenbeschreibung

**Feld**: `textEdit_corredo_descrizione`
**Datenbank**: `corredo_descrizione`

Detaillierte Beschreibung der Beigabenobjekte.

### Beigabentabelle

**Widget**: `tableWidget_corredo_tipo`

Tabelle zur Erfassung der einzelnen Beigabenelemente.

**Spalten:**
| Spalte | Beschreibung |
|--------|-------------|
| Fund-ID | Inventarnummer des Fundes |
| Indv.-ID | Zugehöriges Individuum |
| Material | Materialart |
| Beigabenposition | Wo es im Grab platziert war |
| Position im Beigabenensemble | Position zum Körper |

**Hinweise:**
- Elemente sind mit dem Fundinventarformular verbunden
- Die Tabelle wird automatisch mit den Funden der Struktur befüllt

---

## Tab Weitere Eigenschaften

Dieser Tab enthält zusätzliche Informationen zur Bestattung.

### Periodisierung

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Anfangsperiode | `periodo_iniziale` | Nutzungsbeginn-Periode |
| Anfangsphase | `fase_iniziale` | Phase in der Periode |
| Endperiode | `periodo_finale` | Nutzungsende-Periode |
| Endphase | `fase_finale` | Phase in der Periode |
| Erweiterte Datierung | `datazione_estesa` | Wörtliche Datierung |

Die Werte werden basierend auf dem Periodisierungsformular des Fundorts befüllt.

---

## Tab Werkzeuge

Der Tab Werkzeuge enthält zusätzliche Funktionen.

### Medienverwaltung

Ermöglicht:
- Anzeige zugeordneter Bilder
- Hinzufügen neuer Fotos per Drag & Drop
- Mediensuche in der Datenbank

### Export

Exportoptionen:
- Gräberliste (Kurzliste)
- Grabformulare (vollständige Formulare)
- PDF zu Word-Konvertierung

---

## GIS-Integration

### Kartenanzeige

| Schaltfläche | Funktion |
|--------------|----------|
| GIS-Schalter | Automatisches Laden aktivieren/deaktivieren |
| In GIS laden | Grab auf Karte laden |

### GIS-Layer

Das Formular verwendet grabspezifische Layer:
- **pyarchinit_tomba**: Grabgeometrie
- Verbindung mit Struktur- und SE-Layern

---

## Export und Druck

### PDF-Export

Die PDF-Schaltfläche öffnet ein Feld mit Optionen:

| Option | Beschreibung |
|--------|-------------|
| Gräberliste | Kurzliste der Gräber |
| Grabformulare | Vollständige detaillierte Formulare |
| Drucken | Generiert das PDF |

### PDF-Formularinhalt

Das PDF-Formular enthält:
- Identifikationsdaten
- Ritus und Grabtyp
- Beschreibung und Interpretation
- Beigabendaten
- Periodisierung
- Zugehörige Bilder

---

## Operativer Arbeitsablauf

### Neues Grab erstellen

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "Neuer Datensatz" klicken
   - Formularnummer wird automatisch vorgeschlagen

3. **Identifikationsdaten**
   ```
   Fundort: Nekropole von Isola Sacra
   Areal: 1
   Formularnr.: 45
   Strukturkürzel: TM
   Strukturnr.: 45
   ```

4. **Individuenverbindung**
   ```
   Individuennr.: 1
   ```

5. **Beschreibende Daten** (Tab 1)
   ```
   Ritus: Inhumation
   Grabtyp: Einfaches Erdgrab
   Depositionstyp: Primär
   Erhaltungszustand: Gut

   Beschreibung: Rechteckige Grube mit
   abgerundeten Ecken, orientiert E-W...

   Grabmale: Cippus
   Abdeckung: Ziegelgrab alla cappuccina
   ```

6. **Beigaben** (Tab 2)
   ```
   Vorhandensein: Ja
   Typ: Persönlich
   Beschreibung: Bronzefibel an der
   rechten Schulter, Münze beim Mund...
   ```

7. **Periodisierung**
   ```
   Anfangsperiode: II - Phase A
   Endperiode: II - Phase A
   Datierung: 2. Jh. n. Chr.
   ```

8. **Speichern**
   - Auf "Speichern" klicken

### Gräber suchen

1. Auf "Neue Suche" klicken
2. Kriterien ausfüllen:
   - Fundort
   - Ritus
   - Grabtyp
   - Periode
3. Auf "Suche" klicken
4. Zwischen Ergebnissen navigieren

---

## Beziehungen zu anderen Formularen

| Formular | Beziehung |
|----------|-----------|
| **Fundortformular** | Der Fundort enthält die Gräber |
| **Strukturformular** | Die physische Struktur des Grabes |
| **Individuenformular** | Die menschlichen Überreste im Grab |
| **Fundinventarformular** | Die Beigabenfunde |
| **Periodisierungsformular** | Die Chronologie |

### Empfohlener Arbeitsablauf

1. **Fundortformular** erstellen (falls nicht vorhanden)
2. **Strukturformular** für das Grab erstellen
3. **Grabformular** mit Strukturverbindung erstellen
4. **Individuenformular** für jedes Individuum erstellen
5. Beigaben im **Fundinventarformular** erfassen

---

## Best Practices

### Nomenklatur

- Einheitliche Kürzel verwenden (TM, TB, SEP)
- Fortlaufende Nummerierung innerhalb des Fundorts
- Angenommene Konventionen dokumentieren

### Beschreibung

- Form, Abmessungen, Orientierung systematisch beschreiben
- Zustand zum Zeitpunkt der Ausgrabung dokumentieren
- Objektive Beobachtungen von Interpretationen trennen

### Beigaben

- Genaue Position jedes Objekts erfassen
- Jedes Element mit dem Fundinventar verbinden
- Bedeutsame Assoziationen dokumentieren

### Periodisierung

- Datierung auf diagnostische Elemente stützen
- Zuverlässigkeitsgrad angeben
- Mit ähnlichen Bestattungen vergleichen

---

## Fehlerbehebung

### Problem: Individuum nicht im Menü verfügbar

**Ursache**: Das Individuum wurde noch nicht erstellt oder ist nicht mit der Struktur verknüpft.

**Lösung**:
1. Überprüfen, ob Individuenformular existiert
2. Kontrollieren, ob das Individuum derselben Struktur zugeordnet ist

### Problem: Beigaben nicht in Tabelle angezeigt

**Ursache**: Die Funde sind nicht mit der Struktur verknüpft.

**Lösung**:
1. Fundinventarformular öffnen
2. Überprüfen, ob die Funde die richtige Struktur haben
3. Grabformular aktualisieren

### Problem: Grab nicht auf Karte sichtbar

**Ursache**: Keine Geometrie zugeordnet.

**Lösung**:
1. Überprüfen, ob Grab-Layer existiert
2. Kontrollieren, ob der Struktur eine Geometrie zugeordnet ist
3. Referenzsystem überprüfen

---

## Referenzen

### Datenbank

- **Tabelle**: `tomba_table`
- **Mapper-Klasse**: `TOMBA`
- **ID**: `id_tomba`

### Quelldateien

- **UI**: `gui/ui/Tomba.ui`
- **Controller**: `tabs/Tomba.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

## Video-Tutorial

### Übersicht Grabformular
**Dauer**: 5-6 Minuten
- Oberflächenpräsentation
- Hauptfelder
- Navigation zwischen Tabs

[Platzhalter Video: video_panoramica_tomba.mp4]

### Vollständige Graberfassung
**Dauer**: 10-12 Minuten
- Neuen Datensatz erstellen
- Alle Felder ausfüllen
- Individuen und Beigaben verbinden

[Platzhalter Video: video_schedatura_tomba.mp4]

### Beigabenverwaltung
**Dauer**: 6-8 Minuten
- Beigabenelemente erfassen
- Verbindung mit Fundinventar
- Positionsdokumentation

[Platzhalter Video: video_corredo_tomba.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
