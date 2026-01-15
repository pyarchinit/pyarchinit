# Tutorial 23: Bildersuche

## Einführung

Die Funktion **Bildersuche** ermöglicht das schnelle Auffinden von Bildern in der PyArchInit-Datenbank durch Filterung nach Fundort, Entitätstyp und anderen Kriterien. Sie ist ein ergänzendes Werkzeug zum Medien-Manager für die globale Suche.

## Zugriff

### Über Menü
**PyArchInit** → **Bildersuche**

## Oberfläche

### Suchpanel

```
+--------------------------------------------------+
|           Bildersuche                            |
+--------------------------------------------------+
| Filter:                                          |
|   Fundort: [ComboBox]                            |
|   Entitätstyp: [-- Alle -- | SE | Keramik | ...]|
|   [ ] Nur nicht getaggte Bilder                 |
+--------------------------------------------------+
| [Suchen]  [Zurücksetzen]                         |
+--------------------------------------------------+
| Ergebnisse:                                      |
|  +------+  +------+  +------+                   |
|  | Bild |  | Bild |  | Bild |                   |
|  | Info |  | Info |  | Info |                   |
|  +------+  +------+  +------+                   |
+--------------------------------------------------+
| [Bild öffnen] [Exportieren] [Zum Datensatz]     |
+--------------------------------------------------+
```

### Verfügbare Filter

| Filter | Beschreibung |
|--------|-------------|
| Fundort | Spezifischen Fundort oder alle auswählen |
| Entitätstyp | SE, Keramik, Materialien, Grab, Struktur, UT |
| Nur nicht getaggte | Nur Bilder ohne Verknüpfungen anzeigen |

### Entitätstypen

| Typ | Beschreibung |
|-----|-------------|
| -- Alle -- | Alle Entitäten |
| SE | Stratigraphische Einheiten |
| Keramik | Keramik |
| Materialien | Funde/Inventar |
| Grab | Bestattungen |
| Struktur | Strukturen |
| UT | Topographische Einheiten |

## Funktionen

### Basissuche

1. Gewünschte Filter auswählen
2. Auf **"Suchen"** klicken
3. Ergebnisse im Raster anzeigen

### Aktionen auf Ergebnissen

| Schaltfläche | Funktion |
|--------------|----------|
| Bild öffnen | Bild in Originalgröße anzeigen |
| Exportieren | Ausgewähltes Bild exportieren |
| Zum Datensatz | Formular der verknüpften Entität öffnen |
| Medien-Manager öffnen | Medien-Manager mit ausgewähltem Bild öffnen |

### Kontextmenü (Rechtsklick)

- **Bild öffnen**
- **Bild exportieren...**
- **Zum Datensatz**

### Nicht getaggte Bilder suchen

Checkbox **"Nur nicht getaggte Bilder"**:
- Findet Bilder in der Datenbank ohne Verknüpfungen
- Nützlich für Bereinigung und Organisation
- Ermöglicht die Identifikation noch zu katalogisierender Bilder

## Typischer Arbeitsablauf

### 1. Bilder eines Fundorts finden

```
1. Fundort aus ComboBox auswählen
2. "-- Alle --" für Entitätstyp belassen
3. Suchen klicken
4. Ergebnisse durchsuchen
```

### 2. Spezifische SE-Bilder finden

```
1. Fundort auswählen
2. "SE" als Entitätstyp auswählen
3. Suchen klicken
4. Doppelklick zum Öffnen des Bildes
```

### 3. Nicht katalogisierte Bilder identifizieren

```
1. Fundort auswählen (oder alle)
2. "Nur nicht getaggte Bilder" aktivieren
3. Suchen klicken
4. Für jedes Ergebnis:
   - Bild öffnen
   - Inhalt identifizieren
   - Über Medien-Manager verknüpfen
```

## Export

### Einzelbild exportieren

1. Bild in den Ergebnissen auswählen
2. Auf **"Exportieren"** oder Kontextmenü klicken
3. Ziel auswählen
4. Speichern

### Mehrfachexport

Für den Export mehrerer Bilder die dedizierte Funktion **Bilder exportieren** verwenden (Tutorial 24).

## Best Practices

### 1. Effiziente Suche

- Spezifische Filter für gezielte Ergebnisse verwenden
- Mit breiten Filtern beginnen, dann einschränken
- Regelmäßig nicht getaggte Suche verwenden

### 2. Organisation

- Nicht getaggte Bilder regelmäßig katalogisieren
- Verknüpfungen nach Import überprüfen
- Konsistente Benennung beibehalten

## Fehlerbehebung

### Keine Ergebnisse

**Ursachen**:
- Zu restriktive Filter
- Keine Bilder für die Kriterien

**Lösungen**:
- Filter erweitern
- Datenexistenz überprüfen

### Bild nicht anzeigbar

**Ursachen**:
- Datei nicht gefunden
- Format nicht unterstützt

**Lösungen**:
- Dateipfad überprüfen
- Bildformat kontrollieren

## Referenzen

### Quelldateien
- `tabs/Image_search.py` - Suchoberfläche
- `gui/ui/pyarchinit_image_search_dialog.ui` - UI-Layout

### Datenbank
- `media_table` - Mediendaten
- `media_to_entity_table` - Verknüpfungen

---

## Video-Tutorial

### Bildersuche
`[Platzhalter: video_bildersuche.mp4]`

**Inhalte**:
- Filterverwendung
- Erweiterte Suche
- Ergebnisexport

**Voraussichtliche Dauer**: 8-10 Minuten

---

*Letzte Aktualisierung: Januar 2026*
