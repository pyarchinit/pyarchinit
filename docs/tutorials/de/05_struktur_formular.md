# Tutorial 05: Strukturformular

## Einführung

Das **Strukturformular** ist das PyArchInit-Modul zur Dokumentation archäologischer Strukturen. Eine Struktur ist ein organisierter Verband von Stratigraphischen Einheiten (SE/USM), die eine erkennbare bauliche oder funktionale Einheit bilden, wie eine Mauer, ein Fußboden, ein Grab, ein Ofen oder jedes andere gebaute Element.

### Grundkonzepte

**Struktur vs. Stratigraphische Einheit:**
- Eine **SE** ist die einzelne Einheit (Schicht, Schnitt, Verfüllung)
- Eine **Struktur** gruppiert mehrere funktional zusammenhängende SE
- Beispiel: Eine Mauer (Struktur) besteht aus Fundament, Aufbau, Mörtel (verschiedene SE)

**Hierarchien:**
- Strukturen können untereinander Beziehungen haben
- Jede Struktur gehört zu einer oder mehreren chronologischen Perioden/Phasen
- Strukturen sind mit den sie bildenden SE verbunden

---

## Zugriff auf das Formular

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **Strukturverwaltung** (oder **Structure form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das Symbol **Struktur** klicken (stilisiertes Gebäude)

---

## Oberflächenübersicht

Das Formular hat ein in funktionale Bereiche gegliedertes Layout:

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | DB-Info | Datensatzstatus, Sortierung, Zähler |
| 3 | Identifikationsfelder | Fundort, Kürzel, Strukturnummer |
| 4 | Klassifikationsfelder | Kategorie, Typologie, Definition |
| 5 | Tab-Bereich | Thematische Tabs für spezifische Daten |

---

## Identifikationsfelder

Die Identifikationsfelder definieren die Struktur eindeutig in der Datenbank.

### Fundort

**Feld**: `comboBox_sito`
**Datenbank**: `sito`

Wählt den zugehörigen archäologischen Fundort aus. Das Dropdown zeigt alle in der Datenbank registrierten Fundorte.

**Hinweise:**
- Pflichtfeld
- Die Kombination Fundort + Kürzel + Nummer muss eindeutig sein
- Nach Erstellung des Datensatzes gesperrt

### Strukturkürzel

**Feld**: `comboBox_sigla_struttura`
**Datenbank**: `sigla_struttura`

Alphanumerischer Code zur Identifikation des Strukturtyps. Gängige Konventionen:

| Kürzel | Bedeutung | Beispiel |
|--------|-----------|----------|
| MR | Mauer | MR 1 |
| ST | Struktur | ST 5 |
| PV | Pflasterung | PV 2 |
| FO | Ofen | FO 1 |
| VA | Becken | VA 3 |
| TM | Grab | TM 10 |
| PT | Brunnen | PT 2 |
| CN | Kanal | CN 1 |

### Strukturnummer

**Feld**: `numero_struttura`
**Datenbank**: `numero_struttura`

Fortlaufende Nummer der Struktur innerhalb des Kürzels.

**Hinweise:**
- Numerisches Feld
- Muss eindeutig für Kombination Fundort + Kürzel sein
- Nach Erstellung gesperrt

---

## Klassifikationsfelder

Die Klassifikationsfelder definieren die Art der Struktur.

### Strukturkategorie

**Feld**: `comboBox_categoria_struttura`
**Datenbank**: `categoria_struttura`

Funktionale Makrokategorie der Struktur.

**Typische Werte:**
- Wohnbau
- Produktion
- Funerär
- Religiös
- Defensiv
- Hydraulisch
- Verkehr
- Handwerk

### Strukturtypologie

**Feld**: `comboBox_tipologia_struttura`
**Datenbank**: `tipologia_struttura`

Spezifische Typologie innerhalb der Kategorie.

**Beispiele nach Kategorie:**
| Kategorie | Typologien |
|-----------|------------|
| Wohnbau | Haus, Villa, Palast, Hütte |
| Produktion | Brennofen, Mühle, Ölpresse |
| Funerär | Erdgrab, Kammergrab, Sarkophag |
| Hydraulisch | Brunnen, Zisterne, Aquädukt, Kanal |

### Strukturdefinition

**Feld**: `comboBox_definizione_struttura`
**Datenbank**: `definizione_struttura`

Kurzgefasste und spezifische Definition des Strukturelements.

**Beispiele:**
- Umfassungsmauer
- Opus-signinum-Boden
- Steinschwelle
- Treppe
- Säulenbasis

---

## Tab Beschreibende Daten

Der erste Tab enthält die Textfelder für die detaillierte Beschreibung.

### Beschreibung

**Feld**: `textEdit_descrizione_struttura`
**Datenbank**: `descrizione`

Freitextfeld für die physische Beschreibung der Struktur.

**Empfohlene Inhalte:**
- Bautechnik
- Verwendete Materialien
- Erhaltungszustand
- Allgemeine Abmessungen
- Orientierung
- Besondere Merkmale

**Beispiel:**
```
Mauer in Opus incertum aus lokalen Kalksteinblöcken
verschiedener Größe (ca. 15-30 cm). Bindemittel aus Kalkmörtel
von weißlicher Farbe. Erhalten bis zu einer maximalen Höhe von 1,20 m.
Durchschnittliche Breite 50 cm. Orientierung NE-SW. Zeigt Putzspuren
auf der Innenseite.
```

### Interpretation

**Feld**: `textEdit_interpretazione_struttura`
**Datenbank**: `interpretazione`

Funktionale und historische Interpretation der Struktur.

**Empfohlene Inhalte:**
- Vermutete ursprüngliche Funktion
- Nutzungs-/Wiedernutzungsphasen
- Typologische Vergleiche
- Chronologische Einordnung
- Beziehungen zu anderen Strukturen

---

## Tab Periodisierung

Dieser Tab verwaltet die chronologische Einordnung der Struktur.

### Anfangsperiode und -phase

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Anfangsperiode | `periodo_iniziale` | Bau-/Nutzungsbeginn-Periode |
| Anfangsphase | `fase_iniziale` | Phase innerhalb der Periode |

Die Werte werden automatisch basierend auf den im Periodisierungsformular für den ausgewählten Fundort definierten Perioden befüllt.

### Endperiode und -phase

| Feld | Datenbank | Beschreibung |
|------|-----------|-------------|
| Endperiode | `periodo_finale` | Aufgabe-/Stilllegungsperiode |
| Endphase | `fase_finale` | Phase innerhalb der Periode |

### Erweiterte Datierung

**Feld**: `comboBox_datazione_estesa`
**Datenbank**: `datazione_estesa`

Automatisch berechnete oder manuell eingegebene wörtliche Datierung.

**Formate:**
- "1. Jh. v. Chr. - 2. Jh. n. Chr."
- "100 v. Chr. - 200 n. Chr."
- "Römische Kaiserzeit"

---

## Tab Beziehungen

Dieser Tab verwaltet die Beziehungen zwischen Strukturen.

### Tabelle Strukturbeziehungen

**Widget**: `tableWidget_rapporti`
**Datenbank**: `rapporti_struttura`

Registriert die Beziehungen zwischen der aktuellen Struktur und anderen Strukturen.

**Spalten:**
| Spalte | Beschreibung |
|--------|-------------|
| Beziehungstyp | Stratigraphische/funktionale Beziehung |
| Fundort | Fundort der korrelierten Struktur |
| Kürzel | Kürzel der korrelierten Struktur |
| Nummer | Nummer der korrelierten Struktur |

**Beziehungstypen:**

| Beziehung | Umkehrung | Beschreibung |
|-----------|-----------|-------------|
| Bindet an | Bindet an | Zeitgleiche physische Verbindung |
| Liegt über | Liegt unter | Überlagerungsbeziehung |
| Schneidet | Geschnitten von | Schnittbeziehung |
| Verfüllt | Verfüllt von | Verfüllungsbeziehung |
| Stützt sich auf | Wird gestützt von | Anlagerungsbeziehung |
| Gleich | Gleich | Gleiche Struktur mit anderem Namen |

### Zeilenverwaltung

| Schaltfläche | Funktion |
|--------------|----------|
| + | Neue Zeile hinzufügen |
| - | Ausgewählte Zeile entfernen |

---

## Tab Bauelemente

Dieser Tab dokumentiert die Materialien und Elemente, aus denen die Struktur besteht.

### Verwendete Materialien

**Widget**: `tableWidget_materiali_impiegati`
**Datenbank**: `materiali_impiegati`

Liste der bei der Konstruktion verwendeten Materialien.

**Beispiele für Materialien:**
- Kalksteinblöcke
- Ziegel
- Kalkmörtel
- Flusskiesel
- Dachziegel
- Marmor
- Tuff

### Strukturelemente

**Widget**: `tableWidget_elementi_strutturali`
**Datenbank**: `elementi_strutturali`

Liste der Bauelemente mit Mengenangabe.

**Spalten:**
| Spalte | Beschreibung |
|--------|-------------|
| Elementtyp | Art des Elements |
| Menge | Anzahl der Elemente |

**Beispiele für Elemente:**
| Element | Menge |
|---------|-------|
| Säulenbasis | 4 |
| Kapitell | 2 |
| Schwelle | 1 |
| Quaderstein | 45 |

---

## Tab Maße

Dieser Tab erfasst die Abmessungen der Struktur.

### Messungstabelle

**Widget**: `tableWidget_misurazioni`
**Datenbank**: `misure_struttura`

**Spalten:**
| Spalte | Beschreibung |
|--------|-------------|
| Messungstyp | Art der Dimension |
| Maßeinheit | m, cm, m², usw. |
| Wert | Numerischer Wert |

### Häufige Messungstypen

| Typ | Beschreibung |
|-----|-------------|
| Länge | Größte Ausdehnung |
| Breite | Kleinere Ausdehnung |
| Erhaltene Höhe | Erhaltener Aufbau |
| Ursprüngliche Höhe | Geschätzte ursprüngliche Höhe |
| Tiefe | Für eingetiefte Strukturen |
| Durchmesser | Für runde Strukturen |
| Stärke | Für Mauern, Böden |
| Fläche | Fläche in m² |

### Beispiel für Ausfüllung

| Messungstyp | Maßeinheit | Wert |
|-------------|------------|------|
| Länge | m | 8,50 |
| Breite | cm | 55 |
| Erhaltene Höhe | m | 1,20 |
| Fläche | m² | 4,68 |

---

## Tab Medien

Verwaltung von Bildern, Videos und 3D-Modellen, die der Struktur zugeordnet sind.

### Funktionen

**Widget**: `iconListWidget`

Zeigt Miniaturansichten der zugeordneten Medien an.

### Schaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| Alle Bilder | All images | Zeigt alle Bilder |
| Tags entfernen | Remove tags | Entfernt Medienzuordnung |
| Suchen | Search images | Sucht Bilder in der Datenbank |

### Drag & Drop

Dateien können direkt auf das Formular gezogen werden:

**Unterstützte Formate:**
- Bilder: JPG, JPEG, PNG, TIFF, TIF, BMP
- Videos: MP4, AVI, MOV, MKV, FLV
- 3D: OBJ, STL, PLY, FBX, 3DS

### Anzeige

- **Doppelklick** auf Miniatur: öffnet den Viewer
- Für Videos: öffnet den integrierten Video-Player
- Für 3D: öffnet den PyVista 3D-Viewer

---

## GIS-Integration

### Kartenanzeige

| Schaltfläche | Funktion |
|--------------|----------|
| Kartenvorschau | Vorschau im Tab Karte ein-/ausschalten |
| Struktur zeichnen | Struktur auf QGIS-Karte hervorheben |
| In GIS laden | Strukturlayer laden |
| Alle laden | Alle Strukturen des Fundorts laden |

### GIS-Layer

Das Formular verwendet den Layer **pyarchinit_strutture** für die Visualisierung:
- Geometrie: Polygon oder Multipolygon
- Attribute verknüpft mit Formularfeldern

---

## Export und Druck

### PDF-Export

Die PDF-Schaltfläche öffnet ein Feld mit Exportoptionen:

| Option | Beschreibung |
|--------|-------------|
| Strukturliste | Kurzliste der Strukturen |
| Strukturformulare | Vollständige detaillierte Formulare |
| Drucken | Generiert das PDF |
| In Word konvertieren | Konvertiert PDF in Word-Format |

### PDF zu Word-Konvertierung

Erweiterte Funktion zur Konvertierung generierter PDFs in bearbeitbare Word-Dokumente:

1. Zu konvertierende PDF-Datei auswählen
2. Seitenbereich angeben (optional)
3. Auf "Konvertieren" klicken
4. Word-Datei wird im gleichen Ordner gespeichert

---

## Operativer Arbeitsablauf

### Neue Struktur erstellen

1. **Formular öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "Neuer Datensatz" klicken
   - Identifikationsfelder werden editierbar

3. **Identifikationsdaten**
   ```
   Fundort: Römische Villa Settefinestre
   Kürzel: MR
   Nummer: 15
   ```

4. **Klassifikation**
   ```
   Kategorie: Wohnbau
   Typologie: Umfassungsmauer
   Definition: Mauer in Opus incertum
   ```

5. **Beschreibende Daten** (Tab 1)
   ```
   Beschreibung: In Opus incertum ausgeführte Mauer
   mit lokalen Kalksteinblöcken...

   Interpretation: Nordgrenze der Domus, Phase I
   der Wohnanlage...
   ```

6. **Periodisierung** (Tab 2)
   ```
   Anfangsperiode: I - Phase: A
   Endperiode: II - Phase: B
   Datierung: 1. Jh. v. Chr. - 2. Jh. n. Chr.
   ```

7. **Beziehungen** (Tab 3)
   ```
   Bindet an: MR 16, MR 17
   Geschnitten von: ST 5
   ```

8. **Bauelemente** (Tab 4)
   ```
   Materialien: Kalksteinblöcke, Kalkmörtel
   Elemente: Quadersteine (52), Schwelle (1)
   ```

9. **Maße** (Tab 5)
   ```
   Länge: 12,50 m
   Breite: 0,55 m
   Erhaltene Höhe: 1,80 m
   ```

10. **Speichern**
    - Auf "Speichern" klicken
    - Speicherbestätigung überprüfen

### Strukturen suchen

1. Auf "Neue Suche" klicken
2. Ein oder mehrere Filterfelder ausfüllen:
   - Fundort
   - Strukturkürzel
   - Kategorie
   - Periode
3. Auf "Suche" klicken
4. Zwischen Ergebnissen navigieren

---

## Best Practices

### Nomenklatur

- Einheitliche Kürzel im gesamten Projekt verwenden
- Verwendete Konventionen dokumentieren
- Doppelte Nummerierung vermeiden

### Beschreibung

- Systematisch bei der Beschreibung sein
- Schema befolgen: Technik > Materialien > Abmessungen > Zustand
- Objektive Beschreibung von Interpretation trennen

### Periodisierung

- Immer mit im Periodisierungsformular definierten Perioden verknüpfen
- Sowohl Anfangs- als auch Endphase angeben
- Erweiterte Datierung für Zusammenfassung verwenden

### Beziehungen

- Alle wichtigen Beziehungen erfassen
- Gegenseitigkeit der Beziehungen überprüfen
- Mit den die Struktur bildenden SE verbinden

---

## Fehlerbehebung

### Problem: Struktur nicht auf Karte sichtbar

**Ursache**: Keine Geometrie zugeordnet oder Layer nicht geladen.

**Lösung**:
1. Überprüfen, ob Layer `pyarchinit_strutture` existiert
2. Kontrollieren, ob der Struktur eine Geometrie zugeordnet ist
3. Referenzsystem überprüfen

### Problem: Perioden nicht verfügbar

**Ursache**: Für den Fundort keine Perioden definiert.

**Lösung**:
1. Periodisierungsformular öffnen
2. Perioden für den aktuellen Fundort definieren
3. Zum Strukturformular zurückkehren

### Problem: Speicherfehler "Datensatz existiert"

**Ursache**: Kombination Fundort + Kürzel + Nummer existiert bereits.

**Lösung**:
1. Vorhandene Nummerierung überprüfen
2. Freie fortlaufende Nummer verwenden
3. Auf Duplikate prüfen

---

## Synchronisation mit SE-Formular

Wenn eine Struktur im Strukturformular erstellt wird, erscheint sie automatisch in der Dropdown-Liste des Feldes **Struktur** im SE-Formular.

### Erforderliche Felder für die Synchronisation

Damit eine Struktur in der SE-Dropdown-Liste erscheint:
1. **Fundort**: Muss mit dem Fundort der SE übereinstimmen
2. **Strukturkürzel**: Muss ausgefüllt sein (z.B. MR, ST, PV)
3. **Strukturnummer**: Muss ausgefüllt sein

### Arbeitsablauf

1. **Struktur erstellen**: Füllen Sie Fundort, Kürzel und Nummer aus
2. **Speichern**: Der Datensatz muss gespeichert werden
3. **Im SE-Formular**: Die Struktur erscheint jetzt in der Dropdown-Liste des Strukturfeldes
4. **Zuweisen**: Wählen Sie die Struktur(en) für die SE aus
5. **Synchronisierung**: Die Daten werden zwischen den Formularen verknüpft

### Strukturen von SE entfernen

Um alle Strukturen von einer SE zu entfernen:
1. Öffnen Sie das SE-Formular
2. **Rechtsklick** auf das Feld Struktur
3. Wählen Sie **"Feld Struktur leeren"**
4. Speichern Sie den Datensatz

---

## Referenzen

### Datenbank

- **Tabelle**: `struttura_table`
- **Mapper-Klasse**: `STRUTTURA`
- **ID**: `id_struttura`

### Quelldateien

- **UI**: `gui/ui/Struttura.ui`
- **Controller**: `tabs/Struttura.py`
- **PDF-Export**: `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

## Video-Tutorial

### Übersicht Strukturformular
**Dauer**: 5-6 Minuten
- Allgemeine Oberflächenpräsentation
- Navigation zwischen Tabs
- Hauptfunktionen

[Platzhalter Video: video_panoramica_struttura.mp4]

### Vollständige Strukturerfassung
**Dauer**: 10-12 Minuten
- Neuen Datensatz erstellen
- Alle Felder ausfüllen
- Beziehungen und Maße verwalten

[Platzhalter Video: video_schedatura_struttura.mp4]

### GIS-Integration und Export
**Dauer**: 6-8 Minuten
- Kartenanzeige
- Layer laden
- PDF- und Word-Export

[Platzhalter Video: video_gis_export_struttura.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
