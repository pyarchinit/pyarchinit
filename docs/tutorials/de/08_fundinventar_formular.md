# Tutorial 08: Fundinventar-Formular

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Zugriff auf das Formular](#zugriff-auf-das-formular)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Hauptfelder](#hauptfelder)
5. [Formular-Tabs](#formular-tabs)
6. [DBMS-Toolbar](#dbms-toolbar)
7. [Medienverwaltung](#medienverwaltung)
8. [GIS-Funktionen](#gis-funktionen)
9. [Quantifizierungen und Statistiken](#quantifizierungen-und-statistiken)
10. [Export und Berichte](#export-und-berichte)
11. [KI-Integration](#ki-integration)
12. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
13. [Best Practices](#best-practices)
14. [Fehlerbehebung](#fehlerbehebung)

---

## Einführung

Das **Fundinventar-Formular** ist das Hauptwerkzeug zur Verwaltung archäologischer Funde in PyArchInit. Es ermöglicht die Katalogisierung, Beschreibung und Quantifizierung aller während der Ausgrabung gefundenen Materialien, von Keramik bis Metalle, von Glas bis Tierknochen.

### Zweck des Formulars

- Inventarisierung aller gefundenen Objekte
- Zuordnung der Funde zu den Herkunfts-SE
- Verwaltung der typologischen Klassifikation
- Dokumentation der physischen und technologischen Eigenschaften
- Berechnung von Quantifizierungen (Mindestformen, EVE, Gewicht)
- Verknüpfung von Fotos und Zeichnungen mit den Funden
- Generierung von Berichten und Statistiken

### Verwaltbare Materialtypen

Das Formular unterstützt verschiedene Materialarten:
- **Keramik**: Gefäße, Terrakotten, Baukeramik
- **Metalle**: Bronze, Eisen, Blei, Gold, Silber
- **Glas**: Behälter, Fensterglas
- **Knochen/Elfenbein**: Artefakte aus tierischem Hartmaterial
- **Stein**: Lithische Werkzeuge, Skulpturen
- **Münzen**: Numismatik
- **Organische Materialien**: Holz, Textilien, Leder

---

## Zugriff auf das Formular

### Über Menü

1. QGIS mit aktiviertem PyArchInit-Plugin öffnen
2. Menü **PyArchInit** → **Archaeological record management** → **Artefact** → **Artefact form**

### Über Toolbar

1. PyArchInit-Toolbar finden
2. Auf das Symbol **Funde** (Amphoren-/Gefäß-Symbol) klicken

### Tastaturkürzel

- **Strg+G**: Aktiviert/deaktiviert GIS-Anzeige des aktuellen Fundes

---

## Benutzeroberfläche

Die Oberfläche ist in drei Hauptbereiche unterteilt:

### Hauptbereiche

| Bereich | Beschreibung |
|---------|-------------|
| **1. Header** | DBMS-Toolbar, Statusanzeigen, GIS- und Export-Schaltflächen |
| **2. Identifikationsfelder** | Fundort, Areal, SE, Inventarnummer, RA, Fundtyp |
| **3. Beschreibende Felder** | Klasse, Definition, Erhaltungszustand, Datierung |
| **4. Detail-Tabs** | 6 Tabs für spezifische Daten |

### Verfügbare Tabs

| Tab | Inhalt |
|-----|--------|
| **Beschreibung** | Beschreibungstext, Medien-Viewer, Datierung |
| **Dias** | Verwaltung von Dias und Negativen |
| **Quantitative Daten** | Fundelemente, Formen, Keramikmessungen |
| **Technologien** | Produktions- und Dekorationstechniken |
| **Bibl. Referenzen** | Bibliographische Verweise |
| **Quantifizierungen** | Diagramme und Statistiken |

---

## Hauptfelder

### Identifikationsfelder

#### Fundort
- **Typ**: ComboBox (nach Speicherung schreibgeschützt)
- **Pflichtfeld**: Ja
- **Beschreibung**: Herkunftsfundort
- **Hinweis**: Bei Konfiguration automatisch vorausgefüllt

#### Inventarnummer
- **Typ**: Numerisches LineEdit
- **Pflichtfeld**: Ja
- **Beschreibung**: Eindeutige fortlaufende Nummer des Fundes innerhalb des Fundorts
- **Einschränkung**: Eindeutig pro Fundort

#### Areal
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Nein
- **Beschreibung**: Herkunfts-Ausgrabungsareal

#### SE (Stratigraphische Einheit)
- **Typ**: LineEdit
- **Pflichtfeld**: Nein (aber dringend empfohlen)
- **Beschreibung**: Nummer der Fund-SE
- **Verknüpfung**: Verbindet den Fund mit dem entsprechenden SE-Formular

#### Struktur
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Nein
- **Beschreibung**: Zugehörige Struktur (falls zutreffend)
- **Hinweis**: Wird automatisch basierend auf der SE befüllt

#### RA (Reperto Archeologico)
- **Typ**: Numerisches LineEdit
- **Pflichtfeld**: Nein
- **Beschreibung**: Archäologische Fundnummer (alternative Nummerierung)
- **Hinweis**: Für besonders bedeutende Funde verwendet

### Klassifikationsfelder

#### Fundtyp
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Ja
- **Typische Werte**: Keramik, Metall, Glas, Knochen, Stein, Münze, usw.
- **Hinweis**: Bestimmt die spezifisch auszufüllenden Felder

#### Materialklasse (Erfassungskriterium)
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Nein
- **Beschreibung**: Klassenzugehörigkeit des Materials
- **Beispiele für Keramik**:
  - Gebrauchskeramik
  - Italische Sigillata
  - Afrikanische Sigillata
  - Schwarzgefirnisste Keramik
  - Dünnwandige Keramik
  - Amphoren
  - Lampen

#### Definition
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Nein
- **Beschreibung**: Spezifische typologische Definition
- **Beispiele**: Teller, Schale, Topf, Krug, Deckel, usw.

#### Typ
- **Typ**: LineEdit
- **Pflichtfeld**: Nein
- **Beschreibung**: Spezifische Typologie (z.B. Dressel 1, Hayes 50)

### Status- und Erhaltungsfelder

#### Gewaschen
- **Typ**: ComboBox
- **Werte**: Ja, Nein
- **Beschreibung**: Gibt an, ob der Fund gewaschen wurde

#### Repertorisiert
- **Typ**: ComboBox
- **Werte**: Ja, Nein
- **Beschreibung**: Gibt an, ob der Fund für die Studie ausgewählt wurde

#### Diagnostisch
- **Typ**: ComboBox
- **Werte**: Ja, Nein
- **Beschreibung**: Gibt an, ob der Fund diagnostisch ist (nützlich für Klassifikation)

#### Erhaltungszustand
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Nein
- **Typische Werte**: Vollständig, Fragmentarisch, Lückenhaft, Restauriert

### Depotfelder

#### Kistennr.
- **Typ**: LineEdit
- **Beschreibung**: Nummer der Depotkiste

#### Behältertyp
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Behälterart (Kiste, Beutel, Schachtel)

#### Aufbewahrungsort
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Magazin oder Depot der Aufbewahrung

#### Jahr
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Fundjahr

### Erfassungsfelder

#### Bearbeiter
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Name des Erfassers

#### Fundpunkt
- **Typ**: LineEdit
- **Beschreibung**: Koordinaten oder räumliche Referenz des Fundpunkts

---

## Formular-Tabs

### Tab 1: Beschreibung

Der Haupttab enthält die Textbeschreibung des Fundes und die Medienverwaltung.

#### Beschreibungsfeld
- **Typ**: Mehrzeiliges TextEdit
- **Empfohlener Inhalt**:
  - Allgemeine Form
  - Erhaltene Teile
  - Technische Merkmale
  - Dekorationen
  - Typologische Vergleiche

#### Funddatierung
- **Typ**: Editierbare ComboBox
- **Beschreibung**: Chronologische Einordnung des Fundes
- **Format**: Textuell (z.B. "1. Jh. v. Chr.", "2.-3. Jh. n. Chr.")

#### Medien-Viewer
Bereich zur Anzeige der dem Fund zugeordneten Bilder:
- **Alle Bilder anzeigen**: Lädt alle verknüpften Fotos
- **Bilder suchen**: Suche in den Bildern
- **Tag entfernen**: Entfernt Bild-Fund-Zuordnung
- **SketchGPT**: Generiert KI-Beschreibung aus Bild

### Tab 2: Dias

Verwaltung der traditionellen Fotodokumentation.

#### Dias-Tabelle
| Spalte | Beschreibung |
|--------|-------------|
| Code | Identifikationscode des Dias |
| Nr. | Fortlaufende Nummer |

#### Negative-Tabelle
| Spalte | Beschreibung |
|--------|-------------|
| Code | Code der Negativrolle |
| Nr. | Bildnummer |

#### Zusätzliche Felder
- **Foto-ID**: Namen der zugeordneten Fotos (automatisch befüllt)
- **Zeichnungs-ID**: Namen der zugeordneten Zeichnungen (automatisch befüllt)

### Tab 3: Quantitative Daten

Grundlegender Tab für die quantitative Analyse, besonders für Keramik.

#### Fundelemente-Tabelle
Ermöglicht die Erfassung der einzelnen Elemente, aus denen der Fund besteht:

| Spalte | Beschreibung | Beispiel |
|--------|-------------|----------|
| Gefundenes Element | Anatomischer Teil des Gefäßes | Rand, Wand, Boden, Henkel |
| Mengentyp | Zustand des Fragments | Fragment, Vollständig |
| Menge | Stückzahl | 5 |

#### Keramik-Quantifizierungsfelder

| Feld | Beschreibung |
|------|-------------|
| **Mindestformen** | Minimale Individuenzahl (MNI) |
| **Maximalformen** | Maximale Individuenzahl |
| **Gesamtfragmente** | Automatische Zählung aus Elementtabelle |
| **Gewicht** | Gewicht in Gramm |
| **Randdurchmesser** | Randdurchmesser in cm |
| **EVE Rand** | Estimated Vessel Equivalent (erhaltener Randprozentsatz) |

#### Schaltfläche Gesamtfragmente berechnen
Berechnet automatisch die Gesamtfragmente durch Summierung der Mengen aus der Elementtabelle.

#### Messungstabelle
Ermöglicht die Erfassung mehrerer Maße:

| Spalte | Beschreibung |
|--------|-------------|
| Messungstyp | Höhe, Breite, Dicke, usw. |
| Maßeinheit | cm, mm, m |
| Wert | Numerischer Wert |

### Tab 4: Technologien

Erfassung der Produktions- und Dekorationstechniken.

#### Technologie-Tabelle

| Spalte | Beschreibung | Beispiel |
|--------|-------------|----------|
| Technologietyp | Technische Kategorie | Produktion, Dekoration |
| Position | Wo sie sich befindet | Innen, Außen, Körper |
| Menge | Falls zutreffend | - |
| Maßeinheit | Falls zutreffend | - |

#### Keramikspezifische Felder

| Feld | Beschreibung |
|------|-------------|
| **Keramikkörper** | Tonart (Fein, Halbfein, Grob) |
| **Überzug** | Überzugsart (Firnis, Engobe, Glasur) |

### Tab 5: Bibliographische Referenzen

Verwaltung der Vergleichsbibliographie.

#### Referenztabelle

| Spalte | Beschreibung |
|--------|-------------|
| Autor | Autorennachname(n) |
| Jahr | Publikationsjahr |
| Titel | Kurzform des Titels |
| Seite | Seitenverweis |
| Abbildung | Abbildungs-/Tafelverweis |

### Tab 6: Quantifizierungen

Tab zur Generierung von Diagrammen und Statistiken über die Daten.

#### Verfügbare Quantifizierungstypen

| Typ | Beschreibung |
|-----|-------------|
| **Mindestformen** | Diagramm für MNI |
| **Maximalformen** | Diagramm für Maximalzahl |
| **Gesamtfragmente** | Diagramm für Fragmentzählung |
| **Gewicht** | Diagramm für Gewicht |
| **EVE Rand** | Diagramm für EVE |

#### Gruppierungsparameter

Die Diagramme können gruppiert werden nach:
- Fundtyp
- Materialklasse
- Definition
- Keramikkörper
- Überzug
- Typ
- Datierung
- RA
- Jahr

---

## DBMS-Toolbar

Die Toolbar bietet alle Werkzeuge zur Datensatzverwaltung.

### Standardschaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| Connection test | Verbindungstest | Überprüft Datenbankverbindung |
| First/Prev/Next/Last | Navigation | Navigation zwischen Datensätzen |
| New record | Neu | Erstellt neuen Fund |
| Save | Speichern | Speichert Änderungen |
| Delete | Löschen | Löscht aktuellen Fund |
| View all | Alle | Zeigt alle Datensätze |
| New search | Suche | Aktiviert Suchmodus |
| Search!!! | Ausführen | Führt Suche aus |
| Order by | Sortieren | Sortiert Datensätze |

### Spezifische Schaltflächen

| Symbol | Funktion | Beschreibung |
|--------|----------|-------------|
| GIS | GIS anzeigen | Zeigt Fund auf Karte |
| PDF | PDF-Export | Generiert PDF-Formular |
| Sheet | Listen-Export | Generiert PDF-Liste |
| Excel | Excel-Export | Exportiert im Excel/CSV-Format |
| A5 | A5-Export | Generiert Etikett im A5-Format |
| Quant | Quantifizierungen | Öffnet Quantifizierungspanel |

---

## Medienverwaltung

### Bildzuordnung

#### Drag & Drop
Es ist möglich, Bilder direkt in die Liste zu ziehen, um sie dem Fund zuzuordnen.

#### Medien-Schaltflächen

| Schaltfläche | Funktion |
|--------------|----------|
| **Alle Bilder** | Lädt alle zugeordneten Bilder |
| **Bilder suchen** | Öffnet Bildersuche |
| **Tag entfernen** | Entfernt aktuelle Zuordnung |

### Bildanzeige

Doppelklick auf ein Bild in der Liste öffnet die vollständige Anzeige mit:
- Zoom
- Schwenken
- Rotation
- EXIF-Informationen

### Video-Player

Für Funde mit zugeordneten Videos steht ein integrierter Player zur Verfügung für:
- Wiedergabe von Artefakt-Videos
- Anzeige von 3D-Modellen (falls verfügbar)

---

## GIS-Funktionen

### Kartenanzeige

#### GIS-Schaltfläche (Umschalter)
- **Aktiv**: Der Fund wird auf der QGIS-Karte hervorgehoben
- **Inaktiv**: Keine Anzeige
- **Kürzel**: Strg+G

#### Voraussetzungen
- Der Fund muss die Herkunfts-SE angegeben haben
- Die SE muss eine Geometrie im GIS-Layer haben

### Verknüpfung von der Karte

Es ist möglich, einen Fund durch Klicken auf die Karte auszuwählen:
1. Auswahlwerkzeug in QGIS aktivieren
2. Auf die gewünschte SE klicken
3. Die Funde der SE werden im Formular gefiltert

---

## Quantifizierungen und Statistiken

### Zugriff auf Quantifizierungen

1. Auf die **Quant**-Schaltfläche in der Toolbar klicken
2. Quantifizierungstyp auswählen
3. Gruppierungsparameter auswählen
4. OK klicken

### Diagrammtypen

#### Balkendiagramm
Zeigt die Verteilung nach ausgewählter Kategorie an.

### Export der Quantifizierungen

Die Quantifizierungsdaten werden automatisch exportiert in:
- CSV-Datei im Ordner `pyarchinit_Quantificazioni_folder`
- Am Bildschirm angezeigtes Diagramm

---

## Export und Berichte

### PDF-Export Einzelformular

Generiert ein vollständiges PDF-Formular des aktuellen Fundes mit:
- Alle Identifikationsdaten
- Beschreibung
- Quantitative Daten
- Bibliographische Referenzen
- Zugeordnete Bilder (falls verfügbar)

### PDF-Export Liste

Generiert eine PDF-Liste aller angezeigten Funde (aktuelles Suchergebnis):
- Zusammenfassungstabelle
- Wesentliche Daten für jeden Fund

### A5-Export (Etiketten)

Generiert Etiketten im A5-Format für:
- Kistenidentifikation
- Fundetikettierung
- Mobile Karteikarten

PDF-Pfadkonfiguration:
1. Auf das Ordnersymbol neben dem Pfadfeld klicken
2. Zielordner auswählen
3. "A5 exportieren" klicken

### Excel/CSV-Export

Exportiert die Daten in Tabellenformat für:
- Externe statistische Auswertungen
- Import in andere Software
- Archivierung

---

## KI-Integration

### SketchGPT

KI-Funktion zur automatischen Generierung von Fundbeschreibungen aus Bildern.

#### Verwendung

1. Bild dem Fund zuordnen
2. Auf die **SketchGPT**-Schaltfläche klicken
3. Zu analysierendes Bild auswählen
4. GPT-Modell auswählen (gpt-4-vision, gpt-4o)
5. Das System generiert eine archäologische Beschreibung

#### Ausgabe

Die generierte Beschreibung enthält:
- Identifikation des Fundtyps
- Beschreibung der sichtbaren Merkmale
- Mögliche typologische Vergleiche
- Datierungsvorschläge

> **Hinweis**: Erfordert konfigurierte OpenAI API-Key.

---

## Operativer Arbeitsablauf

### Erstellen eines neuen Fundes

#### Schritt 1: Formular öffnen
1. Fundinventar-Formular öffnen
2. Datenbankverbindung überprüfen

#### Schritt 2: Neuer Datensatz
1. **New record** klicken
2. Status wechselt zu "Neuer Datensatz"

#### Schritt 3: Identifikationsdaten
1. **Fundort** überprüfen/auswählen
2. **Inventarnummer** eingeben (fortlaufend)
3. **Areal** und Herkunfts-**SE** eingeben

#### Schritt 4: Klassifikation
1. **Fundtyp** auswählen
2. **Materialklasse** auswählen
3. **Definition** auswählen/eingeben

#### Schritt 5: Beschreibung
1. **Beschreibung**-Feld im Beschreibung-Tab ausfüllen
2. **Datierung** auswählen
3. Eventuelle Bilder zuordnen

#### Schritt 6: Quantitative Daten (bei Keramik)
1. Tab **Quantitative Daten** öffnen
2. Elemente in die Tabelle eingeben
3. Mindest-/Maximalformen ausfüllen
4. Gewicht und Maße eingeben

#### Schritt 7: Depot
1. **Kistennr.** eingeben
2. **Aufbewahrungsort** auswählen
3. **Erhaltungszustand** angeben

#### Schritt 8: Speichern
1. **Save** klicken
2. Bestätigungsmeldung überprüfen
3. Der Datensatz ist nun in der Datenbank gespeichert

### Funde suchen

#### Einfache Suche
1. **New search** klicken
2. Gewünschte Suchfelder ausfüllen
3. **Search!!!** klicken

#### Suche nach SE
1. Suche aktivieren
2. Nur die SE-Nummer im SE-Feld eingeben
3. Suche ausführen

---

## Best Practices

### Inventarnummerierung

- Fortlaufende Nummerierung ohne Unterbrechungen verwenden
- Eine Nummer = ein Fund (oder homogene Gruppe)
- Inventarisierungskriterium dokumentieren

### Klassifikation

- Kontrollierte Vokabulare für Klassen verwenden
- Konsistenz bei der Definition der Typen beibehalten
- Thesaurus bei Bedarf aktualisieren

### Keramikquantifizierung

Für korrekte Quantifizierung:
1. **Mindestformen (MNI)**: Nur diagnostische Elemente zählen (Ränder, unterscheidbare Böden)
2. **EVE**: Prozentsatz des erhaltenen Umfangs messen
3. **Gewicht**: Alle Fragmente der Gruppe wiegen

### Fotografische Dokumentation

- Alle diagnostischen Funde fotografieren
- Maßstab in den Fotos verwenden
- Fotos über den Medienmanager zuordnen

### SE-Verknüpfung

- Immer überprüfen, dass die SE existiert, bevor sie zugeordnet wird
- Für Funde aus Reinigung/Oberfläche entsprechende SE verwenden
- Fälle von Funden außerhalb des Kontexts dokumentieren

---

## Fehlerbehebung

### Häufige Probleme

#### Doppelte Inventarnummer
- **Fehler**: "Es existiert bereits ein Datensatz mit dieser Inventarnummer"
- **Ursache**: Die Nummer wird bereits für den Fundort verwendet
- **Lösung**: Nächste verfügbare Nummer mit "View all" überprüfen

#### Bilder werden nicht angezeigt
- **Ursache**: Bildpfad nicht korrekt
- **Lösung**:
  1. Pfadkonfiguration in Einstellungen überprüfen
  2. Überprüfen, dass die Bilder im richtigen Ordner sind
  3. Bilder neu zuordnen

#### Leere Quantifizierungen
- **Ursache**: Quantitative Felder nicht ausgefüllt
- **Lösung**: Mindest-/Maximalformen oder Gesamtfragmente ausfüllen

#### Leerer PDF-Export
- **Ursache**: Kein Datensatz ausgewählt
- **Lösung**: Überprüfen, dass mindestens ein Datensatz angezeigt wird

#### GIS funktioniert nicht
- **Ursache**: SE hat keine Geometrie oder Layer nicht geladen
- **Lösung**:
  1. Überprüfen, dass der SE-Layer in QGIS geladen ist
  2. Überprüfen, dass die SE eine zugeordnete Geometrie hat

---

## Video-Tutorial

### Video 1: Übersicht Fundinventar-Formular
*Dauer: 5-6 Minuten*

[Platzhalter für Video-Tutorial]

**Inhalte:**
- Allgemeine Oberfläche
- Navigation zwischen Tabs
- Hauptfunktionen

### Video 2: Vollständige Keramikerfassung
*Dauer: 8-10 Minuten*

[Platzhalter für Video-Tutorial]

**Inhalte:**
- Alle Felder ausfüllen
- Keramikquantifizierung
- Fundelemente
- Technologien

### Video 3: Medien- und Fotoverwaltung
*Dauer: 4-5 Minuten*

[Platzhalter für Video-Tutorial]

**Inhalte:**
- Bildzuordnung
- Anzeige
- SketchGPT

### Video 4: Export und Quantifizierungen
*Dauer: 5-6 Minuten*

[Platzhalter für Video-Tutorial]

**Inhalte:**
- PDF-Export
- Excel-Export
- Quantifizierungsdiagramme

---

## Datenbankfelder-Zusammenfassung

| Feld | Typ | Datenbank | Pflichtfeld |
|------|-----|-----------|-------------|
| Fundort | Text | sito | Ja |
| Inventarnummer | Integer | numero_inventario | Ja |
| Fundtyp | Text | tipo_reperto | Ja |
| Materialklasse | Text | criterio_schedatura | Nein |
| Definition | Text | definizione | Nein |
| Beschreibung | Text | descrizione | Nein |
| Areal | Text | area | Nein |
| SE | Text | us | Nein |
| Gewaschen | String(3) | lavato | Nein |
| Kistennr. | Text | nr_cassa | Nein |
| Aufbewahrungsort | Text | luogo_conservazione | Nein |
| Erhaltungszustand | String(200) | stato_conservazione | Nein |
| Datierung | String(200) | datazione_reperto | Nein |
| Mindestformen | Integer | forme_minime | Nein |
| Maximalformen | Integer | forme_massime | Nein |
| Gesamtfragmente | Integer | totale_frammenti | Nein |
| Keramikkörper | String(200) | corpo_ceramico | Nein |
| Überzug | String(200) | rivestimento | Nein |
| Randdurchmesser | Numeric | diametro_orlo | Nein |
| Gewicht | Numeric | peso | Nein |
| Typ | String(200) | tipo | Nein |
| EVE Rand | Numeric | eve_orlo | Nein |
| Repertorisiert | String(3) | repertato | Nein |
| Diagnostisch | String(3) | diagnostico | Nein |
| RA | Integer | n_reperto | Nein |
| Behältertyp | String(200) | tipo_contenitore | Nein |
| Struktur | String(200) | struttura | Nein |
| Jahr | Integer | years | Nein |

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*
