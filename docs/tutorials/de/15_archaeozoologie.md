# Tutorial 15: Archäozoologie-Formular (Fauna)

## Einführung

Das **Archäozoologie/Fauna-Formular** (Formular FR - Fauna Record) ist das PyArchInit-Modul für die Analyse und Dokumentation faunistischer Reste. Es ermöglicht die Erfassung detaillierter archäozoologischer Daten zur Erforschung antiker Subsistenzwirtschaften.

### Grundkonzepte

**Archäozoologie:**
- Untersuchung tierischer Überreste aus archäologischen Kontexten
- Analyse der Mensch-Tier-Beziehungen in der Vergangenheit
- Rekonstruktion von Ernährung, Viehzucht, Jagd

**Erfasste Daten:**
- Taxonomische Identifikation (Spezies)
- Vorhandene Skelettteile
- MNI (Mindestindividuenzahl)
- Erhaltungszustand
- Taphonomische Spuren
- Schlachtspuren

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **Fauna-Formular** (oder **Fauna form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **Fauna**-Symbol (stilisierter Knochen) klicken

---

## Oberflächenübersicht

Das Formular ist in thematische Tabs organisiert:

### Haupttabs

| # | Tab | Inhalt |
|---|-----|--------|
| 1 | Identifikationsdaten | Fundort, Areal, SE, Kontext |
| 2 | Archäozoologische Daten | Spezies, MNI, Skelettteile |
| 3 | Taphonomische Daten | Erhaltung, Fragmentierung, Spuren |
| 4 | Kontextuelle Daten | Depositionskontext, Assoziationen |
| 5 | Statistiken | Diagramme und Quantifizierungen |

---

## Toolbar

Die Toolbar bietet Standardfunktionen:

| Symbol | Funktion |
|--------|----------|
| First/Prev/Next/Last | Datensatznavigation |
| New | Neuer Datensatz |
| Save | Speichern |
| Delete | Löschen |
| Search | Suche |
| View All | Alle anzeigen |
| PDF | PDF-Export |

---

## Tab Identifikationsdaten

### SE-Auswahl

**Feld**: `comboBox_us_select`

Wählt die Herkunfts-SE. Zeigt verfügbare SE im Format "Fundort - Areal - SE".

### Fundort

**Feld**: `comboBox_sito`
**Datenbank**: `sito`

Archäologischer Fundort.

### Areal

**Feld**: `comboBox_area`
**Datenbank**: `area`

Ausgrabungsareal.

### Sondage

**Feld**: `comboBox_saggio`
**Datenbank**: `saggio`

Herkunftssondage/Schnitt.

### SE

**Feld**: `comboBox_us`
**Datenbank**: `us`

Stratigraphische Einheit.

### SE-Datierung

**Feld**: `lineEdit_datazione`
**Datenbank**: `datazione_us`

Chronologische Einordnung der SE.

### Verantwortlicher

**Feld**: `comboBox_responsabile`
**Datenbank**: `responsabile_scheda`

Autor der Erfassung.

### Erfassungsdatum

**Feld**: `dateEdit_data`
**Datenbank**: `data_compilazione`

Datum der Formularerfassung.

---

## Tab Archäozoologische Daten

### Kontext

**Feld**: `comboBox_contesto`
**Datenbank**: `contesto`

Typ des Depositionskontexts.

**Werte:**
- Siedlung
- Abfall/Deponie
- Verfüllung
- Begehungsschicht
- Bestattung
- Rituell

### Spezies

**Feld**: `comboBox_specie`
**Datenbank**: `specie`

Taxonomische Identifikation.

**Häufige Spezies in der Archäozoologie:**
| Spezies | Wissenschaftlicher Name |
|---------|------------------------|
| Rind | Bos taurus |
| Schaf | Ovis aries |
| Ziege | Capra hircus |
| Schwein | Sus domesticus |
| Pferd | Equus caballus |
| Hirsch | Cervus elaphus |
| Wildschwein | Sus scrofa |
| Hase | Lepus europaeus |
| Hund | Canis familiaris |
| Katze | Felis catus |
| Geflügel | Gallus gallus |

### Mindestindividuenzahl (MNI)

**Feld**: `spinBox_nmi`
**Datenbank**: `numero_minimo_individui`

Schätzung der minimalen Anzahl repräsentierter Individuen.

### Skelettteile

**Feld**: `tableWidget_parti`
**Datenbank**: `parti_scheletriche`

Tabelle zur Erfassung der vorhandenen anatomischen Teile.

**Spalten:**
| Spalte | Beschreibung |
|--------|-------------|
| Element | Knochen/anatomischer Teil |
| Seite | Re/Li/Axial |
| Menge | Fragmentanzahl |
| MNI | Beitrag zum MNI |

### Knochenmessungen

**Feld**: `tableWidget_misure`
**Datenbank**: `misure_ossa`

Standard-osteometrische Messungen.

---

## Tab Taphonomische Daten

### Fragmentierungszustand

**Feld**: `comboBox_frammentazione`
**Datenbank**: `stato_frammentazione`

Fragmentierungsgrad der Reste.

**Werte:**
- Vollständig
- Wenig fragmentiert
- Fragmentiert
- Stark fragmentiert

### Erhaltungszustand

**Feld**: `comboBox_conservazione`
**Datenbank**: `stato_conservazione`

Allgemeine Erhaltungsbedingungen.

**Werte:**
- Ausgezeichnet
- Gut
- Mittelmäßig
- Schlecht
- Sehr schlecht

### Verbrennungsspuren

**Feld**: `comboBox_combustione`
**Datenbank**: `tracce_combustione`

Vorhandensein von Feuerspuren.

**Werte:**
- Nicht vorhanden
- Schwärzung
- Verkohlung
- Kalzinierung

### Taphonomische Spuren

**Feld**: `comboBox_segni_tafo`
**Datenbank**: `segni_tafonomici_evidenti`

Spuren von post-depositionellen Veränderungen.

**Typen:**
- Weathering (Witterungseinflüsse)
- Wurzelspuren
- Nagetierabrieb
- Trittspuren

### Morphologische Veränderungen

**Feld**: `textEdit_alterazioni`
**Datenbank**: `alterazioni_morfologiche`

Detaillierte Beschreibung der beobachteten Veränderungen.

---

## Tab Kontextuelle Daten

### Bergungsmethodik

**Feld**: `comboBox_metodologia`
**Datenbank**: `metodologia_recupero`

Methode der Restesammlung.

**Werte:**
- Auslese
- Trockensiebung
- Flotation
- Nasssiebung

### Reste in anatomischem Verband

**Feld**: `checkBox_connessione`
**Datenbank**: `resti_connessione_anatomica`

Vorhandensein von Teilen im Verband.

### Assoziierte Fundklassen

**Feld**: `textEdit_associazioni`
**Datenbank**: `classi_reperti_associazione`

Andere mit den faunistischen Resten assoziierte Materialien.

### Beobachtungen

**Feld**: `textEdit_osservazioni`
**Datenbank**: `osservazioni`

Allgemeine Notizen.

### Interpretation

**Feld**: `textEdit_interpretazione`
**Datenbank**: `interpretazione`

Interpretation des faunistischen Kontexts.

---

## Tab Statistiken

Bietet Werkzeuge für:
- Verteilungsdiagramme nach Spezies
- Berechnung der Gesamt-MNI
- Vergleiche zwischen SE/Phasen
- Export statistischer Daten

---

## Operativer Arbeitsablauf

### Erfassung faunistischer Reste

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "New Record" klicken

3. **Identifikationsdaten**
   ```
   Fundort: Römische Villa
   Areal: 1000
   SE: 150
   Verantwortlicher: G. Verdi
   Datum: 20.07.2024
   ```

4. **Archäozoologische Daten** (Tab 2)
   ```
   Kontext: Abfall/Deponie
   Spezies: Bos taurus
   MNI: 3

   Skelettteile:
   - Humerus / Re / 2 / 1
   - Tibia / Li / 3 / 2
   - Metapodium / - / 5 / 1
   ```

5. **Taphonomische Daten** (Tab 3)
   ```
   Fragmentierung: Fragmentiert
   Erhaltung: Gut
   Verbrennung: Nicht vorhanden
   Taphonomische Spuren: Wurzelspuren
   ```

6. **Interpretation**
   ```
   Nahrungsmittelabfall.
   Schlachtspuren an einigen
   Langknochen vorhanden.
   ```

7. **Speichern**
   - Auf "Save" klicken

---

## Best Practices

### Identifikation

- Referenzsammlungen verwenden
- Grad der ID-Sicherheit angeben
- Auch nicht identifizierbare Reste erfassen

### MNI

- Für jede Spezies separat berechnen
- Seite und Alter der Funde berücksichtigen
- Berechnungsmethode dokumentieren

### Taphonomie

- Jeden Fund systematisch beobachten
- Spuren vor dem Waschen dokumentieren
- Signifikante Fälle fotografieren

### Kontext

- Immer mit Herkunfts-SE verknüpfen
- Bergungsmethode erfassen
- Signifikante Assoziationen notieren

---

## PDF-Export

Das Formular ermöglicht die Generierung von:
- Detaillierten Einzelformularen
- Listen nach SE oder Phase
- Statistischen Berichten

---

## Fehlerbehebung

### Problem: Spezies nicht verfügbar

**Ursache**: Unvollständige Speziesliste.

**Lösung**:
1. Fauna-Thesaurus überprüfen
2. Fehlende Spezies hinzufügen
3. Administrator kontaktieren

### Problem: MNI nicht berechnet

**Ursache**: Skelettteile nicht erfasst.

**Lösung**:
1. Skelettteile-Tabelle ausfüllen
2. Seite und Menge angeben
3. Das System berechnet automatisch

---

## Referenzen

### Datenbank

- **Tabelle**: `fauna_table`
- **Mapper-Klasse**: `FAUNA`
- **ID**: `id_fauna`

### Quelldateien

- **Controller**: `tabs/Fauna.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

## Video-Tutorial

### Archäozoologische Erfassung
**Dauer**: 12-15 Minuten
- Taxonomische Identifikation
- Skelettteile-Erfassung
- Taphonomische Analyse

[Platzhalter Video: video_archaeozoologie.mp4]

### Faunistische Statistiken
**Dauer**: 8-10 Minuten
- MNI-Berechnung
- Verteilungsdiagramme
- Datenexport

[Platzhalter Video: video_fauna_statistiken.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
