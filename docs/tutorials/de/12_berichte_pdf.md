# Tutorial 12: Berichte und PDF-Drucke

## Einführung

PyArchInit bietet ein vollständiges System zur Generierung von **PDF-Berichten** für alle archäologischen Formulare. Diese Funktion ermöglicht den Export der Dokumentation in druckbares Format, konform mit ministeriellen Standards und bereit zur Archivierung.

### Verfügbare Berichtstypen

| Typ | Beschreibung | Ursprungsformular |
|-----|-------------|-------------------|
| SE-Formulare | Vollständige SE/USM-Berichte | SE-Formular |
| SE-Index | Kurzliste SE | SE-Formular |
| Periodisierungsformulare | Perioden/Phasen-Berichte | Periodisierungsformular |
| Strukturformulare | Strukturberichte | Strukturformular |
| Fundformulare | Materialinventarberichte | Inventarformular |
| Grabformulare | Bestattungsberichte | Grabformular |
| Probenformulare | Probenahmeberichte | Probenformular |
| Individuenformulare | Anthropologische Berichte | Individuenformular |

## Zugriff auf die Funktion

### Vom Hauptmenü
1. **PyArchInit** in der Menüleiste
2. **PDF exportieren** auswählen

### Von der Toolbar
Auf das **PDF**-Symbol in der PyArchInit-Toolbar klicken

## Exportoberfläche

### Fensterübersicht

Das PDF-Exportfenster zeigt:

```
+------------------------------------------+
|        PyArchInit - PDF Export            |
+------------------------------------------+
| Fundort: [ComboBox Fundortauswahl]  [v]  |
+------------------------------------------+
| Zu exportierende Formulare:               |
| [x] SE-Formulare                          |
| [x] Periodisierungsformulare              |
| [x] Strukturformulare                     |
| [x] Fundformulare                         |
| [x] Grabformulare                         |
| [x] Probenformulare                       |
| [x] Individuenformulare                   |
+------------------------------------------+
| [Ordner öffnen]  [PDF exportieren]  [Abbrechen] |
+------------------------------------------+
```

### Fundortauswahl

| Feld | Beschreibung |
|------|-------------|
| ComboBox Fundort | Liste aller Fundorte in der Datenbank |

**Hinweis**: Der Export erfolgt pro Fundort. Um mehrere Fundorte zu exportieren, den Vorgang wiederholen.

### Formular-Checkboxen

Jede Checkbox aktiviert den Export eines bestimmten Typs:

| Checkbox | Generiert |
|----------|-----------|
| SE-Formulare | Vollständige Formulare + SE-Index |
| Periodisierungsformulare | Periodenformulare + Index |
| Strukturformulare | Strukturformulare + Index |
| Fundformulare | Materialformulare + Index |
| Grabformulare | Bestattungsformulare + Index |
| Probenformulare | Probenformulare + Index |
| Individuenformulare | Anthropologische Formulare + Index |

## Exportprozess

### Schritt 1: Datenauswahl

```python
# Das System führt für jeden ausgewählten Typ aus:
1. Datenbankabfrage für ausgewählten Fundort
2. Datensortierung (nach Nummer, Areal, usw.)
3. Listenvorbereitung für Generierung
```

### Schritt 2: PDF-Generierung

Für jeden Formulartyp:
1. **Einzelformular**: Detailliertes PDF für jeden Datensatz
2. **Index**: Zusammenfassendes PDF mit allen Datensätzen

### Schritt 3: Speicherung

Ausgabe im Ordner:
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Berichtsinhalt

### SE-Formular

Enthaltene Informationen:
- **Identifikationsdaten**: Fundort, Areal, SE-Nummer, Einheitstyp
- **Definitionen**: Stratigraphisch, Interpretativ
- **Beschreibung**: Vollständiger Beschreibungstext
- **Interpretation**: Interpretative Analyse
- **Periodisierung**: Anfangs- und Endperiode/-phase
- **Physische Merkmale**: Farbe, Konsistenz, Entstehung
- **Maße**: Min/Max-Höhen, Abmessungen
- **Beziehungen**: Liste stratigraphischer Beziehungen
- **Dokumentation**: Grafische und fotografische Verweise
- **USM-Daten**: (falls zutreffend) Mauerwerkstechnik, Materialien

### SE-Index

Zusammenfassungstabelle mit Spalten:
| Fundort | Areal | SE | Stratigr. Def. | Interpret. Def. | Periode |

### Periodisierungsformular

- Fundort
- Periodennummer
- Phasennummer
- Anfangs-/Endchronologie
- Erweiterte Datierung
- Periodenbeschreibung

### Strukturformular

- Identifikationsdaten (Fundort, Kürzel, Nummer)
- Kategorie, Typologie, Definition
- Beschreibung und Interpretation
- Periodisierung
- Verwendete Materialien
- Strukturelemente
- Strukturbeziehungen
- Maße und Höhen

### Fundformular

- Fundort, Inventarnummer
- Fundtyp, Definition
- Beschreibung
- Herkunft (Areal, SE)
- Erhaltungszustand
- Datierung
- Elemente und Messungen
- Bibliographie

### Grabformular

- Identifikationsdaten
- Ritus (Inhumation/Kremation)
- Bestattungs- und Depositionstyp
- Beschreibung und Interpretation
- Beigaben (Vorhandensein, Typ, Beschreibung)
- Periodisierung
- Struktur- und Individuenhöhen
- Zugehörige SE

### Probenformular

- Fundort, Probennummer
- Probentyp
- Beschreibung
- Herkunft (Areal, SE)
- Aufbewahrungsort
- Kistennummer

### Individuenformular

- Identifikationsdaten
- Geschlecht, Alter (min/max), Altersklassen
- Skelettposition
- Orientierung (Achse, Azimut)
- Erhaltungszustand
- Beobachtungen

## Unterstützte Sprachen

Das System generiert Berichte basierend auf der Systemsprache:

| Sprache | Code | Vorlage |
|---------|------|---------|
| Italienisch | IT | `build_*_sheets()` |
| Deutsch | DE | `build_*_sheets_de()` |
| Englisch | EN | `build_*_sheets_en()` |

Die Sprache wird automatisch aus den QGIS-Einstellungen erkannt.

## Ausgabeordner

### Standardpfad
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Struktur der generierten Dateien

```
pyarchinit_PDF_folder/
├── US_[fundort]_schede.pdf           # Vollständige SE-Formulare
├── US_[fundort]_indice.pdf           # SE-Index
├── Periodizzazione_[fundort].pdf     # Periodisierungsformulare
├── Struttura_[fundort]_schede.pdf    # Strukturformulare
├── Struttura_[fundort]_indice.pdf    # Struktur-Index
├── Reperti_[fundort]_schede.pdf      # Fundformulare
├── Reperti_[fundort]_indice.pdf      # Fund-Index
├── Tomba_[fundort]_schede.pdf        # Grabformulare
├── Campioni_[fundort]_schede.pdf     # Probenformulare
├── Individui_[fundort]_schede.pdf    # Individuenformulare
└── ...
```

### Ordner öffnen

Die Schaltfläche **"Ordner öffnen"** öffnet das Ausgabeverzeichnis direkt im Dateimanager des Systems.

## Berichtsanpassung

### PDF-Vorlagen

Die Vorlagen sind in den Modulen definiert:
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Verwendete Bibliothek

Die PDFs werden mit **ReportLab** generiert, was ermöglicht:
- Anpassbare Layouts
- Bildeinfügung
- Formatierte Tabellen
- Kopf-/Fußzeilen

### Erforderliche Schriften

Das System verwendet spezifische Schriften:
- **Cambria** (Hauptschrift)
- Automatische Installation beim ersten Start des Plugins

## Empfohlener Arbeitsablauf

### 1. Datenvorbereitung

```
1. Alle Formulare des Fundorts vervollständigen
2. Datenvollständigkeit überprüfen
3. Periodisierung kontrollieren
4. Stratigraphische Beziehungen überprüfen
```

### 2. Export

```
1. PDF-Export öffnen
2. Fundort auswählen
3. Formulartypen auswählen
4. "PDF exportieren" klicken
5. Abschluss abwarten
```

### 3. Überprüfung

```
1. Ausgabeordner öffnen
2. Generierte PDFs kontrollieren
3. Formatierung überprüfen
4. Drucken oder archivieren
```

## Problemlösung

### Fehler: "No form to print"

**Ursache**: Keine Datensätze für den ausgewählten Typ gefunden

**Lösung**:
- Überprüfen, dass Daten für den ausgewählten Fundort existieren
- Datenbank kontrollieren

### Leere oder unvollständige PDFs

**Mögliche Ursachen**:
1. Pflichtfelder nicht ausgefüllt
2. Zeichenkodierungsprobleme
3. Fehlende Schriften

**Lösungen**:
- Pflichtfelder vervollständigen
- Cambria-Schriftinstallation überprüfen

### Schriftfehler

**Ursache**: Cambria-Schrift nicht installiert

**Lösung**:
- Das Plugin versucht automatische Installation
- Bei Problemen manuell installieren

### Langsamer Export

**Ursache**: Viele zu exportierende Datensätze

**Lösung**:
- Nach Typologie getrennt exportieren
- Abschluss abwarten

## Best Practices

### 1. Organisation

- Während der Ausgrabung regelmäßig exportieren
- Backups der generierten PDFs erstellen
- Nach Kampagne/Jahr organisieren

### 2. Datenvollständigkeit

- Alle Felder vor dem Export ausfüllen
- Höhen aus GIS-Messungen überprüfen
- Stratigraphische Beziehungen kontrollieren

### 3. Archivierung

- PDFs auf sicherem Speicher ablegen
- In die Enddokumentation einbeziehen
- Dem Grabungsbericht beifügen

### 4. Druck

- Säurefreies Papier für Archivierung verwenden
- Im A4-Format drucken
- Nach Kampagne binden

## Integration mit anderen Funktionen

### Höhen aus GIS

Das System ruft automatisch ab:
- Minimale und maximale Höhen aus Geometrien
- Verweise auf GIS-Pläne

### Fotografische Dokumentation

Die Berichte können Verweise auf Folgendes enthalten:
- Verknüpfte Fotografien
- Zeichnungen und Vermessungen

### Periodisierung

Die SE-Berichte enthalten automatisch:
- Erweiterte Datierung aus der zugewiesenen Periode/Phase
- Chronologische Verweise

## Referenzen

### Quelldateien
- `tabs/Pdf_export.py` - Export-Oberfläche
- `modules/utility/pyarchinit_exp_*_pdf.py` - PDF-Generatoren

### Abhängigkeiten
- ReportLab (PDF-Generierung)
- Cambria-Schrift

---

## Video-Tutorial

### Vollständiger PDF-Export
`[Platzhalter: video_export_pdf.mp4]`

**Inhalte**:
- Fundort- und Formularauswahl
- Exportprozess
- Ausgabeüberprüfung
- Archivorganisation

**Voraussichtliche Dauer**: 10-12 Minuten

---

*Letzte Aktualisierung: Januar 2026*
