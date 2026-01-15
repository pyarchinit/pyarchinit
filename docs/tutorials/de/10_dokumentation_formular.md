# Tutorial 10: Dokumentationsformular

## Einführung

Das **Dokumentationsformular** ist das PyArchInit-Modul zur Verwaltung der grafischen Grabungsdokumentation: Plana, Schnitte, Ansichten, Vermessungen und alle anderen grafischen Ausarbeitungen, die während der archäologischen Tätigkeiten erstellt wurden.

### Dokumentationstypen

- **Plana**: Schichtplana, Phasenplana, Gesamtplana
- **Schnitte**: Stratigraphische Schnitte
- **Ansichten**: Maueransichten, Grabungsfronten
- **Vermessungen**: Topographische, photogrammetrische Aufnahmen
- **Orthofotos**: Ausarbeitungen von Drohnen/Photogrammetrie
- **Fundzeichnungen**: Keramik, Metalle, usw.

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **Dokumentationsformular** (oder **Documentation form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **Dokumentation**-Symbol klicken

---

## Oberflächenübersicht

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | DB-Info | Datensatzstatus, Sortierung, Zähler |
| 3 | Identifikationsfelder | Fundort, Name, Datum |
| 4 | Typologische Felder | Typ, Quelle, Maßstab |
| 5 | Beschreibende Felder | Zeichner, Notizen |

---

## DBMS-Toolbar

### Standardschaltflächen

| Funktion | Beschreibung |
|----------|-------------|
| First/Prev/Next/Last rec | Navigation zwischen Datensätzen |
| New record | Erstellt neuen Datensatz |
| Save | Speichert die Änderungen |
| Delete | Löscht den Datensatz |
| New search / Search | Suchfunktionen |
| Order by | Sortiert Ergebnisse |
| View all | Zeigt alle Datensätze an |

---

## Formularfelder

### Fundort

**Feld**: `comboBox_sito_doc`
**Datenbank**: `sito`

Referenz-archäologischer Fundort.

### Dokumentationsname

**Feld**: `lineEdit_nome_doc`
**Datenbank**: `nome_doc`

Identifikationsname des Dokuments.

**Namenskonventionen:**
- `P` = Planum (z.B. P001)
- `S` = Schnitt (z.B. S001)
- `A` = Ansicht (z.B. A001)
- `V` = Vermessung (z.B. V001)

### Datum

**Feld**: `dateEdit_data`
**Datenbank**: `data`

Datum der Zeichnungs-/Vermessungsausführung.

### Dokumentationstyp

**Feld**: `comboBox_tipo_doc`
**Datenbank**: `tipo_documentazione`

Dokumententypologie.

**Typische Werte:**
| Typ | Beschreibung |
|-----|-------------|
| Schichtplanum | Einzelne SE |
| Phasenplanum | Mehrere zeitgleiche SE |
| Gesamtplanum | Gesamtansicht |
| Stratigraphischer Schnitt | Vertikales Profil |
| Ansicht | Maueraufriss |
| Topographische Vermessung | Gesamtplan |
| Orthofoto | Aus Photogrammetrie |
| Fundzeichnung | Keramik, Metall, usw. |

### Quelle

**Feld**: `comboBox_sorgente`
**Datenbank**: `sorgente`

Quelle/Produktionsmethode.

**Werte:**
- Direkte Vermessung
- Photogrammetrie
- Laserscanner
- GPS/Totalstation
- CAD-Digitalisierung
- Drohnen-Orthofoto

### Maßstab

**Feld**: `comboBox_scala`
**Datenbank**: `scala`

Darstellungsmaßstab.

**Übliche Maßstäbe:**
| Maßstab | Typische Verwendung |
|---------|---------------------|
| 1:1 | Fundzeichnungen |
| 1:5 | Details |
| 1:10 | Schnitte, Details |
| 1:20 | Schichtplana |
| 1:50 | Gesamtplana |
| 1:100 | Lageplane |
| 1:200+ | Topographische Karten |

### Zeichner

**Feld**: `comboBox_disegnatore`
**Datenbank**: `disegnatore`

Autor der Zeichnung/Vermessung.

### Notizen

**Feld**: `textEdit_note`
**Datenbank**: `note`

Zusätzliche Notizen zum Dokument.

---

## Operativer Arbeitsablauf

### Neue Dokumentation registrieren

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "New Record" klicken

3. **Identifikationsdaten**
   ```
   Fundort: Römische Villa Settefinestre
   Name: P025
   Datum: 15.06.2024
   ```

4. **Klassifikation**
   ```
   Typ: Schichtplanum
   Quelle: Direkte Vermessung
   Maßstab: 1:20
   ```

5. **Autor und Notizen**
   ```
   Zeichner: M. Rossi
   Notizen: Planum SE 150. Zeigt
   Grenzen des Fußbodenestrichs.
   ```

6. **Speichern**
   - Auf "Save" klicken

### Dokumentation suchen

1. Auf "New Search" klicken
2. Kriterien ausfüllen:
   - Fundort
   - Dokumentationstyp
   - Maßstab
   - Zeichner
3. Auf "Search" klicken
4. Zwischen Ergebnissen navigieren

---

## PDF-Export

Das Formular unterstützt den PDF-Export für:
- Dokumentationsliste
- Detaillierte Formulare

---

## Best Practices

### Nomenklatur

- Einheitliche Codes im gesamten Projekt verwenden
- Fortlaufende Nummerierung nach Typ
- Angenommene Konventionen dokumentieren

### Organisation

- Immer mit dem Referenz-Fundort verknüpfen
- Tatsächlichen Maßstab angeben
- Datum und Autor registrieren

### Archivierung

- Digitale Dateien über die Medienverwaltung verknüpfen
- Sicherungskopien pflegen
- Standardformate verwenden (PDF, TIFF)

---

## Fehlerbehebung

### Problem: Dokumentationstyp nicht verfügbar

**Ursache**: Thesaurus nicht konfiguriert.

**Lösung**:
1. Thesaurus-Formular öffnen
2. Fehlende Typen für `documentazione_table` hinzufügen

### Problem: Datei wird nicht angezeigt

**Ursache**: Pfad nicht korrekt oder Datei fehlt.

**Lösung**:
1. Überprüfen, dass die Datei existiert
2. Pfad in der Medienkonfiguration prüfen

---

## Referenzen

### Datenbank

- **Tabelle**: `documentazione_table`
- **Mapper-Klasse**: `DOCUMENTAZIONE`
- **ID**: `id_documentazione`

### Quelldateien

- **UI**: `gui/ui/Documentazione.ui`
- **Controller**: `tabs/Documentazione.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

## Video-Tutorial

### Verwaltung der grafischen Dokumentation
**Dauer**: 6-8 Minuten
- Neue Dokumentation registrieren
- Klassifikation und Metadaten
- Suche und Abfrage

[Platzhalter Video: video_dokumentation.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
