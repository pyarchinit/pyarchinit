# Tutorial 09: Probenformular

## Einführung

Das **Probenformular** ist das PyArchInit-Modul zur Verwaltung archäologischer Probenahmen. Es ermöglicht die Registrierung und Verfolgung aller während der Ausgrabung entnommenen Probentypen: Erde, Holzkohle, Samen, Knochen, Mörtel, Metalle und anderes Material für spezialisierte Analysen.

### Probentypen

Archäologische Proben umfassen:
- **Sedimente**: für sedimentologische, granulometrische Analysen
- **Holzkohlen**: für radiometrische Datierungen (C14)
- **Samen/Pollen**: für archäobotanische Analysen
- **Knochen**: für archäozoologische, isotopische, DNA-Analysen
- **Mörtel/Putze**: für archäometrische Analysen
- **Metalle/Schlacken**: für metallurgische Analysen
- **Keramiken**: für Tonanalysen, Herkunftsbestimmung

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **Probenformular** (oder **Samples form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **Proben**-Symbol klicken

---

## Oberflächenübersicht

Das Formular präsentiert ein vereinfachtes Layout für die schnelle Probenverwaltung.

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | DB-Info | Datensatzstatus, Sortierung, Zähler |
| 3 | Identifikationsfelder | Fundort, Probennr., Typ |
| 4 | Beschreibende Felder | Beschreibung, Notizen |
| 5 | Aufbewahrungsfelder | Kiste, Ort |

---

## DBMS-Toolbar

### Navigationsschaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| First rec | Zum ersten Datensatz |
| Prev rec | Zum vorherigen Datensatz |
| Next rec | Zum nächsten Datensatz |
| Last rec | Zum letzten Datensatz |

### CRUD-Schaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| New record | Erstellt neuen Probendatensatz |
| Save | Speichert die Änderungen |
| Delete | Löscht den aktuellen Datensatz |

### Suchschaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| New search | Startet neue Suche |
| Search!!! | Führt Suche aus |
| Order by | Sortiert Ergebnisse |
| View all | Zeigt alle Datensätze an |

---

## Formularfelder

### Fundort

**Feld**: `comboBox_sito`
**Datenbank**: `sito`

Wählt den zugehörigen archäologischen Fundort.

### Probennummer

**Feld**: `lineEdit_nr_campione`
**Datenbank**: `nr_campione`

Fortlaufende Identifikationsnummer der Probe.

### Probentyp

**Feld**: `comboBox_tipo_campione`
**Datenbank**: `tipo_campione`

Typologische Klassifikation der Probe. Die Werte stammen aus dem Thesaurus.

**Übliche Typen:**
| Typ | Beschreibung |
|-----|-------------|
| Sediment | Erdprobe |
| Holzkohle | Für C14-Datierungen |
| Samen | Karpologische Reste |
| Knochen | Faunistische Reste |
| Mörtel | Baumaterialien |
| Keramik | Für Tonanalysen |
| Metall | Für metallurgische Analysen |
| Pollen | Für palynologische Analysen |

### Beschreibung

**Feld**: `textEdit_descrizione`
**Datenbank**: `descrizione`

Detaillierte Beschreibung der Probe.

**Empfohlene Inhalte:**
- Physische Eigenschaften der Probe
- Entnommene Menge
- Entnahmemethode
- Grund der Probenahme
- Geplante Analysen

### Areal

**Feld**: `comboBox_area`
**Datenbank**: `area`

Herkunfts-Ausgrabungsareal.

### SE

**Feld**: `comboBox_us`
**Datenbank**: `us`

Herkunfts-Stratigraphische Einheit.

### Material-Inventarnummer

**Feld**: `lineEdit_nr_inv_mat`
**Datenbank**: `numero_inventario_materiale`

Wenn die Probe mit einem inventarisierten Fund verbunden ist, Inventarnummer angeben.

### Kistennummer

**Feld**: `lineEdit_nr_cassa`
**Datenbank**: `nr_cassa`

Kiste oder Aufbewahrungsbehälter.

### Aufbewahrungsort

**Feld**: `comboBox_luogo_conservazione`
**Datenbank**: `luogo_conservazione`

Wo die Probe aufbewahrt wird.

**Beispiele:**
- Grabungslabor
- Museumsdepot
- Externes Analyselabor
- Universität

---

## Operativer Arbeitsablauf

### Neue Probe erstellen

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "New Record" klicken

3. **Identifikationsdaten**
   ```
   Fundort: Römische Villa Settefinestre
   Probennr.: P-2024-001
   Probentyp: Holzkohle
   ```

4. **Herkunft**
   ```
   Areal: 1000
   SE: 150
   ```

5. **Beschreibung**
   ```
   Holzkohleprobe entnommen von der
   Oberfläche des Brandlehms SE 150.
   Menge: ca. 50 gr.
   Entnommen für C14-Datierung.
   ```

6. **Aufbewahrung**
   ```
   Kistennr.: Probe-1
   Ort: Grabungslabor
   ```

7. **Speichern**
   - Auf "Save" klicken

### Proben suchen

1. Auf "New Search" klicken
2. Kriterien ausfüllen:
   - Fundort
   - Probentyp
   - SE
3. Auf "Search" klicken
4. Zwischen Ergebnissen navigieren

---

## PDF-Export

Das Formular unterstützt den PDF-Export für:
- Probenliste
- Detaillierte Einzelformulare

---

## Best Practices

### Nomenklatur

- Eindeutige und aussagekräftige Codes verwenden
- Empfohlenes Format: `FUNDORT-JAHR-NUMMER`
- Beispiel: `VRS-2024-P001`

### Entnahme

- Immer die Entnahmekoordinaten dokumentieren
- Den Entnahmepunkt fotografieren
- Tiefe und Kontext notieren

### Aufbewahrung

- Dem Typ entsprechende Behälter verwenden
- Jede Probe deutlich beschriften
- Geeignete Bedingungen beibehalten

### Dokumentation

- Immer mit der Herkunfts-SE verknüpfen
- Geplante Analysen angeben
- Versand an externe Labore registrieren

---

## Fehlerbehebung

### Problem: Probentyp nicht verfügbar

**Ursache**: Thesaurus nicht konfiguriert.

**Lösung**:
1. Thesaurus-Formular öffnen
2. Fehlenden Typ für `campioni_table` hinzufügen
3. Speichern und Probenformular erneut öffnen

### Problem: SE nicht angezeigt

**Ursache**: SE nicht für den ausgewählten Fundort registriert.

**Lösung**:
1. Überprüfen, dass die SE im SE-Formular existiert
2. Prüfen, dass sie zum selben Fundort gehört

---

## Referenzen

### Datenbank

- **Tabelle**: `campioni_table`
- **Mapper-Klasse**: `CAMPIONI`
- **ID**: `id_campione`

### Quelldateien

- **UI**: `gui/ui/Campioni.ui`
- **Controller**: `tabs/Campioni.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

## Video-Tutorial

### Probenverwaltung
**Dauer**: 5-6 Minuten
- Neue Probe erstellen
- Felder ausfüllen
- Suche und Export

[Platzhalter Video: video_proben.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
