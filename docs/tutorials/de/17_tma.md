# Tutorial 17: TMA - Tabelle Archäologischer Materialien

## Einführung

Das **TMA-Formular** (Tabelle Archäologischer Materialien) ist das erweiterte PyArchInit-Modul zur Verwaltung von Grabungsmaterialien nach italienischen ministeriellen Standards. Es ermöglicht eine detaillierte Katalogisierung gemäß ICCD-Vorschriften (Istituto Centrale per il Catalogo e la Documentazione).

### Hauptmerkmale

- ICCD-standardkonforme Katalogisierung
- Materialverwaltung nach Kiste/Behälter
- Detaillierte chronologische Felder
- Tabelle zugeordneter Materialien
- Integrierte Medienverwaltung
- Export von Etiketten und PDF-Formularen

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **TMA-Formular** auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **TMA**-Symbol klicken

---

## Oberflächenübersicht

Das Formular präsentiert eine komplexe Oberfläche mit vielen Feldern.

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | Identifikationsfelder | Fundort, Areal, SE, Kiste |
| 3 | Lokalisierungsfelder | Aufbewahrungsort, Raum, Sondage |
| 4 | Chronologische Felder | Zeitabschnitt, Unterteilung, Chronologien |
| 5 | Materialtabelle | Detail zugeordneter Materialien |
| 6 | Medien-Tab | Bilder und Dokumente |

---

## Identifikationsfelder

### Fundort

**Feld**: `comboBox_sito`
**Datenbank**: `sito`

Archäologischer Fundort (SCAN - ICCD-Grabungsbezeichnung).

### Areal

**Feld**: `comboBox_area`
**Datenbank**: `area`

Ausgrabungsareal.

### SE (DSCU)

**Feld**: `comboBox_us`
**Datenbank**: `dscu`

Herkunfts-Stratigraphische Einheit (DSCU = Descrizione Scavo Unita).

### Sektor

**Feld**: `comboBox_settore`
**Datenbank**: `settore`

Ausgrabungssektor.

### Inventar

**Feld**: `lineEdit_inventario`
**Datenbank**: `inventario`

Inventarnummer.

### Kiste

**Feld**: `lineEdit_cassetta`
**Datenbank**: `cassetta`

Nummer der Kiste/des Behälters.

---

## ICCD-Lokalisierungsfelder

### LDCT - Aufbewahrungstyp

**Feld**: `comboBox_ldct`
**Datenbank**: `ldct`

Typ des Aufbewahrungsortes.

**ICCD-Werte:**
- museo (Museum)
- soprintendenza (Denkmalamt)
- deposito (Depot)
- laboratorio (Labor)
- altro (Anderes)

### LDCN - Aufbewahrungsbezeichnung

**Feld**: `lineEdit_ldcn`
**Datenbank**: `ldcn`

Spezifischer Name des Aufbewahrungsortes.

### Alte Aufbewahrung

**Feld**: `lineEdit_vecchia_coll`
**Datenbank**: `vecchia_collocazione`

Eventuelle frühere Aufbewahrung.

### SCAN - Grabungsbezeichnung

**Feld**: `lineEdit_scan`
**Datenbank**: `scan`

Offizieller Name der Grabung/Forschung.

### Sondage

**Feld**: `comboBox_saggio`
**Datenbank**: `saggio`

Referenzsondage/Schnitt.

### Raum/Locus

**Feld**: `lineEdit_vano`
**Datenbank**: `vano_locus`

Herkunftsraum oder Locus.

---

## Chronologische Felder

### DTZG - Chronologischer Zeitabschnitt

**Feld**: `comboBox_dtzg`
**Datenbank**: `dtzg`

Allgemeiner chronologischer Zeitraum.

**ICCD-Beispiele:**
- eta del bronzo (Bronzezeit)
- eta del ferro (Eisenzeit)
- eta romana (Römische Zeit)
- eta medievale (Mittelalter)

### DTZS - Chronologische Unterteilung

**Feld**: `comboBox_dtzs`
**Datenbank**: `dtzs`

Unterteilung der Periode.

**Beispiele:**
- antico/a (früh)
- medio/a (mittel)
- tardo/a (spät)
- finale (end)

### Chronologien

**Feld**: `tableWidget_cronologie`
**Datenbank**: `cronologie`

Tabelle für mehrfache oder detaillierte Chronologien.

---

## Erwerbsfelder

### AINT - Erwerbstyp

**Feld**: `comboBox_aint`
**Datenbank**: `aint`

Art des Materialerwerbs.

**ICCD-Werte:**
- scavo (Grabung)
- ricognizione (Prospektion)
- acquisto (Kauf)
- donazione (Schenkung)
- sequestro (Beschlagnahme)

### AIND - Erwerbsdatum

**Feld**: `dateEdit_aind`
**Datenbank**: `aind`

Datum des Erwerbs.

### RCGD - Prospektionsdatum

**Feld**: `dateEdit_rcgd`
**Datenbank**: `rcgd`

Datum der Prospektion (falls zutreffend).

### RCGZ - Prospektionsdetails

**Feld**: `textEdit_rcgz`
**Datenbank**: `rcgz`

Notizen zur Prospektion.

---

## Materialfelder

### OGTM - Material

**Feld**: `comboBox_ogtm`
**Datenbank**: `ogtm`

Hauptmaterial (Oggetto Tipo Materiale).

**ICCD-Werte:**
- ceramica (Keramik)
- vetro (Glas)
- metallo (Metall)
- osso (Knochen)
- pietra (Stein)
- laterizio (Ziegel)

### Fundanzahl

**Feld**: `spinBox_n_reperti`
**Datenbank**: `n_reperti`

Gesamtzahl der Funde.

### Gewicht

**Feld**: `doubleSpinBox_peso`
**Datenbank**: `peso`

Gesamtgewicht in Gramm.

### DESO - Objektangabe

**Feld**: `textEdit_deso`
**Datenbank**: `deso`

Kurzbeschreibung der Objekte.

---

## Materialien-Detailtabelle

**Widget**: `tableWidget_materiali`
**Verknüpfte Tabelle**: `tma_materiali`

Ermöglicht die Erfassung der einzelnen in der Kiste enthaltenen Materialien.

### Spalten

| ICCD-Feld | Beschreibung |
|-----------|-------------|
| MADI | Materialinventar |
| MACC | Kategorie |
| MACL | Klasse |
| MACP | Typologische Präzisierung |
| MACD | Definition |
| Cronologia | Spezifische Datierung |
| MACQ | Menge |

### Zeilenverwaltung

| Schaltfläche | Funktion |
|--------------|----------|
| + | Material hinzufügen |
| - | Material entfernen |

---

## Dokumentationsfelder

### FTAP - Fototyp

**Feld**: `comboBox_ftap`
**Datenbank**: `ftap`

Typ der fotografischen Dokumentation.

### FTAN - Fotocode

**Feld**: `lineEdit_ftan`
**Datenbank**: `ftan`

Identifikationscode des Fotos.

### DRAT - Zeichnungstyp

**Feld**: `comboBox_drat`
**Datenbank**: `drat`

Typ der grafischen Dokumentation.

### DRAN - Zeichnungscode

**Feld**: `lineEdit_dran`
**Datenbank**: `dran`

Identifikationscode der Zeichnung.

### DRAA - Zeichnungsautor

**Feld**: `lineEdit_draa`
**Datenbank**: `draa`

Autor der Zeichnung.

---

## Medien-Tab

Verwaltung von mit der Kiste/TMA verknüpften Bildern.

### Funktionen

- Miniaturanzeige
- Drag & Drop zum Hinzufügen von Bildern
- Doppelklick zum Anzeigen
- Verknüpfung mit Mediendatenbank

---

## Tabellenansicht-Tab

Tabellarische Ansicht aller TMA-Datensätze für schnelle Konsultation.

### Funktionen

- Rasteransicht
- Spaltensortierung
- Schnellfilter
- Mehrfachauswahl

---

## Export und Druck

### PDF-Export

| Option | Beschreibung |
|--------|-------------|
| TMA-Formular | Vollständiges Formular |
| Etiketten | Etiketten für Kisten |

### Kistenetiketten

Automatische Generierung von Etiketten für:
- Kistenidentifikation
- Kurzinhalt
- Herkunftsdaten
- Barcode (optional)

---

## Operativer Arbeitsablauf

### Registrierung neuer TMA

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "New Record" klicken

3. **Identifikationsdaten**
   ```
   Fundort: Römische Villa
   Areal: 1000
   SE: 150
   Kiste: K-001
   ```

4. **Lokalisierung**
   ```
   LDCT: deposito
   LDCN: Depot Denkmalamt Rom
   SCAN: Grabungen Römische Villa 2024
   ```

5. **Chronologie**
   ```
   DTZG: eta romana
   DTZS: imperiale
   ```

6. **Materialien** (Tabelle)
   ```
   | Inv | Kat | Klasse | Def | Anz |
   |-----|-----|--------|-----|-----|
   | 001 | ceramica | comune | olla | 5 |
   | 002 | ceramica | sigillata | piatto | 3 |
   | 003 | vetro | - | unguentario | 1 |
   ```

7. **Speichern**
   - Auf "Save" klicken

---

## Best Practices

### ICCD-Standards

- Kontrollierte ICCD-Vokabulare verwenden
- Offizielle Kürzel einhalten
- Terminologische Konsistenz beibehalten

### Kistenorganisation

- Eindeutige fortlaufende Nummerierung
- Ein TMA pro physischer Kiste
- Nach SE trennen wenn möglich

### Dokumentation

- Immer Fotos und Zeichnungen verknüpfen
- Eindeutige Codes für Medien verwenden
- Autor und Datum erfassen

---

## Fehlerbehebung

### Problem: ICCD-Vokabulare nicht verfügbar

**Ursache**: Thesaurus nicht konfiguriert.

**Lösung**:
1. Standard-ICCD-Vokabulare importieren
2. Thesaurus-Konfiguration überprüfen

### Problem: Materialien nicht gespeichert

**Ursache**: Materialtabelle nicht synchronisiert.

**Lösung**:
1. Überprüfen, dass alle Pflichtfelder ausgefüllt sind
2. Hauptformular speichern, bevor Materialien hinzugefügt werden

---

## Referenzen

### Datenbank

- **Haupttabelle**: `tma_materiali_archeologici`
- **Detailtabelle**: `tma_materiali`
- **Mapper-Klasse**: `TMA`, `TMA_MATERIALI`
- **ID**: `id`

### Quelldateien

- **UI**: `gui/ui/Tma.ui`
- **Controller**: `tabs/Tma.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Etiketten**: `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Video-Tutorial

### TMA-Katalogisierung
**Dauer**: 15-18 Minuten
- ICCD-Standards
- Vollständige Erfassung
- Materialverwaltung

[Platzhalter Video: video_tma_katalogisierung.mp4]

### Etikettengenerierung
**Dauer**: 5-6 Minuten
- Etikettenkonfiguration
- Stapeldruck
- Anpassung

[Platzhalter Video: video_tma_etiketten.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
