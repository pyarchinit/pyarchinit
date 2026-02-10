# Tutorial 16: Pottery-Formular (Spezialisierte Keramik)

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Zugriff auf das Formular](#zugriff-auf-das-formular)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Hauptfelder](#hauptfelder)
5. [Formular-Tabs](#formular-tabs)
6. [Pottery Tools](#pottery-tools)
7. [Visuelle Ähnlichkeitssuche](#visuelle-ähnlichkeitssuche)
8. [Quantifizierungen](#quantifizierungen)
9. [Medienverwaltung](#medienverwaltung)
10. [Export und Berichte](#export-und-berichte)
11. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
12. [Best Practices](#best-practices)
13. [Fehlerbehebung](#fehlerbehebung)

---

## Einführung

Das **Pottery-Formular** ist ein spezialisiertes Werkzeug für die detaillierte Katalogisierung archäologischer Keramik. Im Gegensatz zum Materialinventar-Formular (allgemeiner) ist dieses Formular speziell für die vertiefte keramologische Analyse konzipiert, mit dedizierten Feldern für Fabric, Ware, Dekorationen und gefäßspezifische Maße.

### Unterschiede zum Materialinventar-Formular

| Aspekt | Materialinventar | Pottery |
|--------|------------------|---------|
| **Zweck** | Alle Fundtypen | Nur Keramik |
| **Detail** | Allgemein | Spezialistisch |
| **Fabric-Felder** | Keramikkörper (allgemein) | Detailliertes Fabric |
| **Dekorationen** | Einzelfeld | Innen/Außen getrennt |
| **Maße** | Allgemein | Gefäßspezifisch |
| **KI-Tools** | SketchGPT | PotteryInk, YOLO, Ähnlichkeitssuche |

### Erweiterte Funktionen

Das Pottery-Formular enthält modernste KI-Funktionen:
- **PotteryInk**: Automatische Generierung archäologischer Zeichnungen aus Fotos
- **YOLO Detection**: Automatische Erkennung keramischer Formen
- **Visual Similarity Search**: Suche ähnlicher Keramiken mittels visueller Embeddings
- **Layout Generator**: Automatische Generierung keramischer Tafeln

---

## Zugriff auf das Formular

### Über Menü

1. QGIS mit aktiviertem PyArchInit-Plugin öffnen
2. Menü **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery**

### Über Toolbar

1. PyArchInit-Toolbar finden
2. Auf das **Pottery**-Symbol (Keramikgefäß-/Amphoren-Symbol) klicken

---

## Benutzeroberfläche

Die Oberfläche ist effizient für die keramologische Erfassung organisiert:

### Hauptbereiche

| Bereich | Beschreibung |
|---------|-------------|
| **1. Header** | DBMS-Toolbar, Statusanzeigen, Filter |
| **2. Identifikation** | Fundort, Areal, SE, ID-Nummer, Box, Beutel |
| **3. Klassifikation** | Form, Ware, Fabric, Material |
| **4. Detail-Tabs** | Description, Technical Data, Supplements |
| **5. Medien-Panel** | Bild-Viewer, Vorschau |

### Verfügbare Tabs

| Tab | Inhalt |
|-----|--------|
| **Description data** | Beschreibung, Dekorationen, Notizen |
| **Technical Data** | Maße, Oberflächenbehandlung, Munsell |
| **Supplements** | Bibliographie, Statistiken |

---

## Hauptfelder

### Identifikationsfelder

#### ID-Nummer
- **Typ**: Integer
- **Pflichtfeld**: Ja
- **Beschreibung**: Eindeutige Identifikationsnummer des Keramikfragments
- **Einschränkung**: Eindeutig pro Fundort

#### Fundort
- **Typ**: ComboBox
- **Pflichtfeld**: Ja
- **Beschreibung**: Herkunftsfundort

#### Areal
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Ausgrabungsareal

#### SE (Stratigraphische Einheit)
- **Typ**: Integer
- **Beschreibung**: Nummer der Fund-SE

#### Sektor
- **Typ**: Text
- **Beschreibung**: Spezifischer Fundsektor

### Depotfelder

#### Box
- **Typ**: Integer
- **Beschreibung**: Nummer der Depotkiste

#### Bag
- **Typ**: Integer
- **Beschreibung**: Beutelnummer

#### Jahr
- **Typ**: Integer
- **Beschreibung**: Fund-/Erfassungsjahr

### Keramik-Klassifikationsfelder

#### Form
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Empfohlen
- **Typische Werte**: Bowl, Jar, Jug, Plate, Cup, Amphora, Lid, usw.
- **Beschreibung**: Allgemeine Form des Gefäßes

#### Specific Form (Spezifische Form)
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Spezifische Typologie (z.B. Hayes 50, Dressel 1)

#### Specific Shape
- **Typ**: Text
- **Beschreibung**: Detaillierte morphologische Variante

#### Ware
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Keramikklasse
- **Beispiele**:
  - African Red Slip
  - Italian Sigillata
  - Thin Walled Ware
  - Coarse Ware
  - Amphora
  - Cooking Ware

#### Material
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Grundmaterial
- **Werte**: Ceramic, Terracotta, Porcelain, usw.

#### Fabric
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Typ des keramischen Tons
- **Zu berücksichtigende Eigenschaften**:
  - Tonfarbe
  - Granulometrie der Einschlüsse
  - Härte
  - Porosität

### Erhaltungsfelder

#### Percent
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Erhaltener Prozentsatz des Gefäßes
- **Typische Werte**: <10%, 10-25%, 25-50%, 50-75%, >75%, Complete

#### QTY (Quantity)
- **Typ**: Integer
- **Beschreibung**: Fragmentanzahl

---

## Formular-Tabs

### Tab 1: Description Data

Haupttab für die Fragmentbeschreibung.

#### Dekorationen

| Feld | Beschreibung |
|------|-------------|
| **External Decoration** | Typ der Außendekoration |
| **Internal Decoration** | Typ der Innendekoration |
| **Description External Deco** | Detailbeschreibung Außendekoration |
| **Description Internal Deco** | Detailbeschreibung Innendekoration |
| **Decoration Type** | Dekorationstyp (Painted, Incised, Applique, usw.) |
| **Decoration Motif** | Dekorationsmotiv (Geometric, Vegetal, Figurative) |
| **Decoration Position** | Dekorationsposition (Rim, Body, Base, Handle) |

#### Wheel Made
- **Typ**: ComboBox
- **Werte**: Yes, No, Unknown
- **Beschreibung**: Gibt an, ob das Gefäß auf der Scheibe hergestellt wurde

#### Note
- **Typ**: Mehrzeiliges TextEdit
- **Beschreibung**: Zusätzliche Notizen und Beobachtungen

### Tab 2: Technical Data

Technische Daten und Messungen.

#### Munsell Color
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Munsell-Farbcode des Tons
- **Format**: z.B. "10YR 7/4", "5YR 6/6"
- **Hinweis**: Auf Munsell Soil Color Chart verweisen

#### Surface Treatment
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Oberflächenbehandlung
- **Typische Werte**:
  - Slip (Engobe)
  - Burnished (Poliert)
  - Glazed (Glasiert)
  - Painted (Bemalt)
  - Plain (Einfach)

#### Maße (in cm)

| Feld | Beschreibung |
|------|-------------|
| **Diameter Max** | Maximaler Durchmesser des Gefäßes |
| **Diameter Rim** | Randdurchmesser |
| **Diameter Bottom** | Bodendurchmesser |
| **Total Height** | Gesamthöhe (wenn rekonstruierbar) |
| **Preserved Height** | Erhaltene Höhe |

#### Datierung
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Chronologische Einordnung
- **Format**: Textuell (z.B. "1.-2. Jh. n. Chr.")

### Tab 3: Supplements

Tab mit Unterabschnitten für zusätzliche Daten.

#### Sub-Tab: Bibliography
Verwaltung bibliographischer Verweise für typologische Vergleiche.

| Spalte | Beschreibung |
|--------|-------------|
| Author | Autor(en) |
| Year | Publikationsjahr |
| Title | Kurztitel |
| Page | Seitenverweis |
| Figure | Abbildung/Tafel |

#### Sub-Tab: Statistic
Zugriff auf Quantifizierungs- und statistische Diagrammfunktionen.

---

## Pottery Tools

Das Pottery-Formular enthält ein leistungsstarkes Set von KI-Werkzeugen für die Keramikbildverarbeitung.

### Zugriff auf Pottery Tools

1. Menü **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery Tools**

Oder über die dedizierte Schaltfläche im Pottery-Formular.

### PotteryInk - Zeichnungsgenerierung

Wandelt Keramikfotos automatisch in stilisierte archäologische Zeichnungen um.

#### Verwendung

1. Ein Keramikbild auswählen
2. Auf "Generate Drawing" klicken
3. Das System verarbeitet das Bild mit KI
4. Die Zeichnung wird im archäologischen Stil generiert

#### Anforderungen
- Dedizierte virtuelle Umgebung (automatisch erstellt)
- Vortrainierte KI-Modelle
- GPU empfohlen für optimale Leistung

### YOLO Pottery Detection

Automatische Erkennung keramischer Formen in Bildern.

#### Funktionen

- Identifiziert automatisch die Gefäßform
- Schlägt Klassifikation vor
- Erkennt anatomische Teile (Rand, Wand, Boden, Henkel)

### Layout Generator

Generiert automatisch Keramiktafeln für Publikationen.

#### Ausgabe

- Tafeln im archäologischen Standardformat
- Automatischer Maßstab
- Optimierte Anordnung
- Export als PDF oder Bild

### PDF Extractor

Extrahiert Keramikbilder aus PDF-Publikationen für Vergleiche.

---

## Visuelle Ähnlichkeitssuche

Erweiterte Funktion zum Finden visuell ähnlicher Keramiken in der Datenbank.

### Funktionsweise

Das System verwendet **visuelle Embeddings**, die von Deep-Learning-Modellen generiert werden, um jedes Keramikbild als numerischen Vektor darzustellen. Die Suche findet Keramiken mit ähnlichsten Vektoren.

### Verwendung

1. Referenzbild auswählen
2. Auf "Find Similar" klicken
3. Das System durchsucht die Datenbank
4. Die ähnlichsten Keramiken werden nach Ähnlichkeit sortiert angezeigt

### Verfügbare Modelle

- **ResNet50**: Gute Balance Geschwindigkeit/Präzision
- **EfficientNet**: Optimale Leistung
- **CLIP**: Multimodale Suche (Text + Bild)

### Embedding-Aktualisierung

Embeddings werden automatisch generiert, wenn neue Bilder hinzugefügt werden. Eine Aktualisierung kann über das Pottery Tools-Menü erzwungen werden.

---

## Quantifizierungen

### Zugriff

1. Auf die **Quant**-Schaltfläche in der Toolbar klicken
2. Quantifizierungsparameter auswählen
3. Diagramm anzeigen

### Verfügbare Parameter

| Parameter | Beschreibung |
|-----------|-------------|
| **Fabric** | Verteilung nach Tontyp |
| **US** | Verteilung nach Stratigraphischer Einheit |
| **Area** | Verteilung nach Ausgrabungsareal |
| **Material** | Verteilung nach Material |
| **Percent** | Verteilung nach erhaltenem Prozentsatz |
| **Shape/Form** | Verteilung nach Form |
| **Specific form** | Verteilung nach spezifischer Form |
| **Ware** | Verteilung nach Keramikklasse |
| **Munsell color** | Verteilung nach Farbe |
| **Surface treatment** | Verteilung nach Oberflächenbehandlung |
| **External decoration** | Verteilung nach Außendekoration |
| **Internal decoration** | Verteilung nach Innendekoration |
| **Wheel made** | Verteilung Drehscheibe ja/nein |

### Quantifizierungs-Export

Die Daten werden exportiert in:
- CSV-Datei in `pyarchinit_Quantificazioni_folder`
- Bildschirmdiagramm

---

## Medienverwaltung

### Bildzuordnung

#### Methoden

1. **Drag & Drop**: Bilder in die Liste ziehen
2. **Schaltfläche All Images**: Lädt alle zugeordneten Bilder
3. **Search Images**: Sucht bestimmte Bilder

### Video Player

Für Keramik mit Videodokumentation steht ein integrierter Player zur Verfügung.

### Cloudinary-Integration

Unterstützung für Remote-Bilder auf Cloudinary:
- Automatisches Thumbnail-Laden
- Lokaler Cache für Leistung
- Cloud-Synchronisation

---

## Export und Berichte

### PDF-Formular-Export

Generiert ein vollständiges PDF-Formular mit:
- Identifikationsdaten
- Klassifikation
- Maße
- Zugeordnete Bilder
- Notizen

### Listen-Export

Generiert PDF-Liste aller angezeigten Datensätze.

### Daten-Export

Schaltfläche für Export im Tabellenformat (CSV/Excel).

---

## Operativer Arbeitsablauf

### Erfassung eines neuen Keramikfragments

#### Schritt 1: Öffnen und neuer Datensatz
1. Pottery-Formular öffnen
2. **New record** klicken

#### Schritt 2: Identifikationsdaten
1. **Fundort** überprüfen/auswählen
2. **ID-Nummer** eingeben (fortlaufend)
3. **Areal**, **SE**, **Sektor** eingeben
4. **Box** und **Bag** eingeben

#### Schritt 3: Klassifikation
1. **Form** auswählen (Bowl, Jar, usw.)
2. **Ware** auswählen (Keramikklasse)
3. **Fabric** auswählen (Tontyp)
4. **Material** und **Percent** angeben

#### Schritt 4: Technische Daten
1. Tab **Technical Data** öffnen
2. **Munsell color** eingeben
3. **Surface treatment** auswählen
4. **Maße** eingeben (Durchmesser, Höhen)
5. **Wheel made** angeben

#### Schritt 5: Dekorationen (falls vorhanden)
1. Zurück zu Tab **Description data**
2. Typ **External/Internal decoration** auswählen
3. Detailbeschreibungen ausfüllen
4. **Decoration type**, **motif**, **position** angeben

#### Schritt 6: Dokumentation
1. Fotos zuordnen (Drag & Drop)
2. **Photo** und **Drawing** Verweise eingeben
3. **Note** mit Beobachtungen ausfüllen

#### Schritt 7: Datierung und Vergleiche
1. **Datierung** eingeben
2. Tab **Supplements** → **Bibliography** öffnen
3. Bibliographische Verweise hinzufügen

#### Schritt 8: Speichern
1. **Save** klicken
2. Bestätigung überprüfen

---

## Best Practices

### Konsistente Klassifikation

- Standardisierte Vokabulare für Form, Ware, Fabric verwenden
- Konsistenz in der Nomenklatur beibehalten
- Thesaurus bei Bedarf aktualisieren

### Fotografische Dokumentation

- Jedes Fragment mit Maßstab fotografieren
- Innen- und Außenansicht einschließen
- Dekorative Details dokumentieren

### Messungen

- Messschieber für genaue Maße verwenden
- Immer Maßeinheit angeben (cm)
- Bei Fragmenten nur erhaltene Teile messen

### Munsell-Farbe

- Immer Munsell Soil Color Chart verwenden
- An frischer Bruchstelle messen
- Lichtbedingungen angeben

### KI-Tools-Nutzung

- Automatische Ergebnisse immer überprüfen
- PotteryInk funktioniert besser mit qualitativ hochwertigen Fotos
- Ähnlichkeitssuche ist nützlich für Vergleiche, ersetzt nicht die Analyse

---

## Fehlerbehebung

### Häufige Probleme

#### Doppelte ID-Nummer
- **Fehler**: "Es existiert bereits ein Datensatz mit dieser ID"
- **Lösung**: Nächste verfügbare Nummer überprüfen

#### Pottery Tools startet nicht
- **Ursache**: Virtuelle Umgebung nicht konfiguriert
- **Lösung**:
  1. Internetverbindung überprüfen
  2. Automatische Konfiguration abwarten
  3. Log in `pyarchinit/bin/pottery_venv` prüfen

#### PotteryInk langsam
- **Ursache**: CPU-Verarbeitung statt GPU
- **Lösung**:
  1. CUDA-Treiber installieren (NVIDIA)
  2. Überprüfen, dass PyTorch GPU nutzt

#### Ähnlichkeitssuche leer
- **Ursache**: Embeddings nicht generiert
- **Lösung**:
  1. Pottery Tools öffnen
  2. "Update Embeddings" klicken
  3. Abschluss abwarten

#### Bilder nicht geladen
- **Ursache**: Pfad nicht korrekt oder Cloudinary nicht konfiguriert
- **Lösung**:
  1. Pfadkonfiguration in Einstellungen überprüfen
  2. Für Cloudinary: Anmeldedaten überprüfen

---

## Video-Tutorial

### Video 1: Pottery-Formular Übersicht
*Dauer: 5-6 Minuten*

[Platzhalter für Video]

### Video 2: Vollständige Keramikerfassung
*Dauer: 8-10 Minuten*

[Platzhalter für Video]

### Video 3: Pottery Tools und KI
*Dauer: 10-12 Minuten*

[Platzhalter für Video]

### Video 4: Ähnlichkeitssuche
*Dauer: 5-6 Minuten*

[Platzhalter für Video]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologische Keramikanalyse*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../../animations/pyarchinit_pottery_tools_animation.html)
