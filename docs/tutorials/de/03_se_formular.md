# PyArchInit - SE/USM-Formular (Stratigraphische Einheit)

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Grundlegende Konzepte](#grundlegende-konzepte)
3. [Zugriff auf das Formular](#zugriff-auf-das-formular)
4. [Allgemeine Oberfläche](#allgemeine-oberfläche)
5. [Identifikationsfelder](#identifikationsfelder)
6. [Tab Lokalisierung](#tab-lokalisierung)
7. [Tab Beschreibende Daten](#tab-beschreibende-daten)
8. [Tab Periodisierung](#tab-periodisierung)
9. [Tab Stratigraphische Beziehungen](#tab-stratigraphische-beziehungen)
10. [Tab Physische Daten](#tab-physische-daten)
11. [Tab Erfassungsdaten](#tab-erfassungsdaten)
12. [Tab SE-Maße](#tab-se-maße)
13. [Tab Dokumentation](#tab-dokumentation)
14. [Tab Bautechnik USM](#tab-bautechnik-usm)
15. [Tab Bindemittel USM](#tab-bindemittel-usm)
16. [Tab Medien](#tab-medien)
17. [Tab Hilfe - Tool Box](#tab-hilfe---tool-box)
18. [Harris-Matrix](#harris-matrix)
19. [GIS-Funktionen](#gis-funktionen)
20. [Exporte](#exporte)
21. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
22. [Fehlerbehebung](#fehlerbehebung)

---

## Einführung

Das **SE/USM-Formular** (Stratigraphische Einheit / Mauerwerks-Stratigraphische Einheit) ist das Herzstück der archäologischen Dokumentation in PyArchInit. Es stellt das Hauptwerkzeug zur Erfassung aller Informationen zu den bei der Ausgrabung identifizierten stratigraphischen Einheiten dar.

Dieses Formular implementiert die Prinzipien der **stratigraphischen Methode**, die von Edward C. Harris entwickelt wurde, und ermöglicht die Dokumentation von:
- Den physischen Eigenschaften jeder Schicht
- Den stratigraphischen Beziehungen zwischen den Einheiten
- Der relativen und absoluten Chronologie
- Der zugehörigen grafischen und fotografischen Dokumentation

> **Video-Tutorial**: [Link zum Einführungsvideo des SE-Formulars einfügen]

---

## Grundlegende Konzepte

### Was ist eine Stratigraphische Einheit (SE)

Eine **Stratigraphische Einheit** ist die kleinste identifizierbare und von anderen unterscheidbare Ausgrabungseinheit. Sie kann sein:
- **Schicht**: Erdablagerung mit homogenen Eigenschaften
- **Interface**: Kontaktfläche zwischen Schichten (z.B. Grubenschnitt)
- **Strukturelement**: Teil eines Bauwerks

### Einheitentypen

| Typ | Kürzel | Beschreibung |
|-----|--------|-------------|
| SE | Stratigraphische Einheit | Allgemeine Schicht |
| USM | Mauerwerks-SE | Mauerwerk-Bauelement |
| USVA | Vertikale SE A | Vertikaler Aufbau Typ A |
| USVB | Vertikale SE B | Vertikaler Aufbau Typ B |
| USD | Abbruch-SE | Schutt-/Abbruchschicht |
| CON | Werkstücke | Architekturblöcke |
| VSF | Virtuelles Stratigraphisches Feature | Virtuelles Element |
| SF | Stratigraphisches Feature | Stratigraphisches Merkmal |
| SUS | Sub-Stratigraphische Einheit | Unterteilung einer SE |

### Stratigraphische Beziehungen

Stratigraphische Beziehungen definieren die zeitlichen Verhältnisse zwischen den SE:

| Beziehung | Umkehrung | Bedeutung |
|-----------|-----------|-----------|
| **Liegt über** | Liegt unter | Die SE überlagert physisch |
| **Schneidet** | Geschnitten von | Die SE unterbricht/durchquert |
| **Verfüllt** | Verfüllt von | Die SE füllt einen Hohlraum |
| **Stützt sich auf** | Wird gestützt von | Anlehnungsbeziehung |

![Stratigraphische Beziehungen](images/03_se_formular/01_schema_rapporti.png)
*Abbildung 1: Schema der stratigraphischen Beziehungen*

---

## Zugriff auf das Formular

Um auf das SE-Formular zuzugreifen:

1. Menü **PyArchInit** → **Archaeological record management** → **SU/WSU**
2. Oder klicken Sie in der PyArchInit-Toolbar auf das Symbol **SE/USM**

![Zugriff SE-Formular](images/03_se_formular/02_menu_scheda_us.png)
*Abbildung 2: Zugriff auf das SE-Formular über Menü*

![Toolbar SE](images/03_se_formular/03_toolbar_us.png)
*Abbildung 3: SE-Formularsymbol in der Toolbar*

---

## Allgemeine Oberfläche

Das SE-Formular ist in verschiedene Funktionsbereiche unterteilt:

![SE-Oberfläche](images/03_se_formular/04_interfaccia_completa.png)
*Abbildung 4: Vollständige Oberfläche des SE-Formulars*

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | **Identifikationsfelder** | Fundort, Areal, SE, Typ, Definitionen |
| 2 | **DBMS-Toolbar** | Navigation, Speichern, Suche |
| 3 | **Daten-Tabs** | Thematische Registerkarten für Daten |
| 4 | **GIS-Toolbar** | Kartenvisualisierungswerkzeuge |
| 5 | **Tab Tool Box** | Erweiterte Werkzeuge und Matrix |

### DBMS-Toolbar

Die DBMS-Toolbar ist identisch mit der des Fundort-Formulars mit einigen zusätzlichen Funktionen:

![DBMS-Toolbar](images/03_se_formular/05_toolbar_dbms.png)
*Abbildung 5: DBMS-Toolbar des SE-Formulars*

| Schaltfläche | Funktion | Beschreibung |
|--------------|----------|-------------|
| **Neuer Datensatz** | Neu | Erstellt ein neues SE-Formular |
| **Speichern** | Speichern | Speichert Änderungen |
| **Löschen** | Löschen | Löscht aktuelles Formular |
| **Alle anzeigen** | Alle ansehen | Zeigt alle Datensätze |
| **Erster/Vorher/Nächster/Letzter** | Navigation | Navigiert zwischen Datensätzen |
| **Neue Suche** | Suche | Startet Suchmodus |
| **Suche!!!** | Ausführen | Führt Suche aus |
| **Sortieren nach** | Sortieren | Sortiert Datensätze |
| **Bericht** | Drucken | Generiert PDF-Bericht |
| **SE-Liste/Fotos** | Liste | Generiert Listen |

---

## Identifikationsfelder

Die Identifikationsfelder sind immer im oberen Teil des Formulars sichtbar.

![Identifikationsfelder](images/03_se_formular/06_campi_identificativi.png)
*Abbildung 6: Identifikationsfelder*

### Pflichtfelder

| Feld | Beschreibung | Format |
|------|-------------|--------|
| **Fundort** | Name des archäologischen Fundorts | Text (aus Combobox) |
| **Areal** | Nummer des Ausgrabungsareals | Ganzzahl (1-20) |
| **SE/USM** | Nummer der stratigraphischen Einheit | Ganzzahl |
| **Einheitentyp** | Typ der Einheit (SE, USM, usw.) | Auswahl |

### Beschreibende Felder

| Feld | Beschreibung |
|------|-------------|
| **Stratigraphische Definition** | Stratigraphische Klassifizierung (aus Thesaurus) |
| **Interpretative Definition** | Funktionale Interpretation (aus Thesaurus) |

### Stratigraphische Definitionen (Beispiele)

| Definition | Beschreibung |
|------------|-------------|
| Schicht | Allgemeine Ablagerung |
| Verfüllung | Füllmaterial |
| Schnitt | Negative Schnittstelle |
| Nutzungshorizont | Begehungsoberfläche |
| Schutt | Schuttmaterial |
| Stampfboden | Gestampfter Erdboden |

### Interpretative Definitionen (Beispiele)

| Definition | Beschreibung |
|------------|-------------|
| Baustellentätigkeit | Bauphase |
| Aufgabe | Aufgabephase |
| Bodenbelag | Fußbodenebene |
| Mauer | Mauerstruktur |
| Grube | Absichtliche Aushebung |
| Nivellierung | Vorbereitungsschicht |

---

## Tab Lokalisierung

Enthält die Positionierungsdaten innerhalb der Ausgrabung.

![Tab Lokalisierung](images/03_se_formular/07_tab_localizzazione.png)
*Abbildung 7: Tab Lokalisierung*

### Lokalisierungsfelder

| Feld | Beschreibung | Hinweis |
|------|-------------|---------|
| **Sektor** | Ausgrabungssektor | Buchstaben A-H oder Zahlen 1-20 |
| **Quadrat/Wand** | Räumliche Referenz | Für Rasterausgrabungen |
| **Raum** | Raumnummer | Für Gebäude/Strukturen |
| **Sondage** | Sondagenummer | Für Prüfsondagen |

### Katalognummern

| Feld | Beschreibung |
|------|-------------|
| **Allg. Katalog-Nr.** | Allgemeine Katalognummer |
| **Interne Katalog-Nr.** | Interne Katalognummer |
| **Internat. Katalog-Nr.** | Internationaler Code |

---

## Tab Beschreibende Daten

Enthält die textliche Beschreibung der stratigraphischen Einheit.

![Tab Beschreibende Daten](images/03_se_formular/08_tab_dati_descrittivi.png)
*Abbildung 8: Tab Beschreibende Daten*

### Beschreibende Felder

| Feld | Beschreibung | Tipps |
|------|-------------|-------|
| **Beschreibung** | Physische Beschreibung der SE | Farbe, Konsistenz, Zusammensetzung, Grenzen |
| **Interpretation** | Funktionale Interpretation | Funktion, Entstehung, Bedeutung |
| **Datierende Elemente** | Datierungsmaterialien | Keramik, Münzen, datierende Objekte |
| **Bemerkungen** | Zusätzliche Notizen | Zweifel, Hypothesen, Vergleiche |

### So beschreiben Sie eine SE

**Physische Beschreibung:**
```
Tonige Erdschicht, dunkelbraune Farbe (10YR 3/3),
kompakte Konsistenz, mit Einschlüssen von Ziegelfragmenten (2-5 cm),
Kalksteingeröllen (1-3 cm) und Holzkohle. Scharfe Grenzen oben,
verschwommene Grenzen unten. Variable Stärke 15-25 cm.
```

**Interpretation:**
```
Aufgabeschicht, entstanden nach Beendigung der
Aktivitäten im Raum. Das Vorhandensein von fragmentiertem
Baumaterial deutet auf einen teilweisen Einsturz der Strukturen hin.
```

---

## Tab Periodisierung

Verwaltet die Chronologie der stratigraphischen Einheit.

![Tab Periodisierung](images/03_se_formular/09_tab_periodizzazione.png)
*Abbildung 9: Tab Periodisierung*

### Relative Periodisierung

| Feld | Beschreibung |
|------|-------------|
| **Anfangsperiode** | Entstehungsperiode |
| **Anfangsphase** | Entstehungsphase |
| **Endperiode** | Obliterierungsperiode |
| **Endphase** | Obliterierungsphase |

**Hinweis**: Perioden und Phasen müssen zuerst im **Periodisierungsformular** erstellt werden.

### Absolute Chronologie

| Feld | Beschreibung |
|------|-------------|
| **Datierung** | Absolutes Datum oder Intervall |
| **Jahr** | Ausgrabungsjahr |

### Weitere Felder

| Feld | Beschreibung | Werte |
|------|-------------|-------|
| **Aktivität** | Art der Aktivität | Freitext |
| **Struktur** | Zugehöriger Strukturcode | Aus Strukturformular |
| **Ausgegraben** | Ausgrabungsstatus | Ja / Nein |
| **Ausgrabungsmethode** | Ausgrabungsweise | Mechanisch / Stratigraphisch |

### Feld Struktur

Das **Struktur**-Feld (`comboBox_struttura`) ist ein Mehrfachauswahlfeld, das mit dem Strukturformular synchronisiert wird.

**Wichtige Merkmale:**
- Das Feld zeigt alle im Strukturformular für den aktuellen Fundort definierten Strukturen
- Sie können mehrere Strukturen auswählen, indem Sie die entsprechenden Kontrollkästchen ankreuzen
- Nach dem Speichern werden die Daten zwischen SE und Struktur synchronisiert

**Wie man Strukturen zuweist:**
1. Auf das Strukturfeld klicken, um das Dropdown zu öffnen
2. Die gewünschten Strukturen durch Ankreuzen der Kontrollkästchen auswählen
3. Die Datensatz speichern

**Wie man alle Strukturen entfernt:**
1. **Rechtsklick** auf das Strukturfeld
2. Im Kontextmenü **"Feld Struktur leeren"** auswählen
3. Alle Auswahlen werden entfernt
4. Den Datensatz speichern, um die Änderung zu bestätigen

> **Hinweis**: Das Leeren des Feldes entfernt die Auswahlen im aktuellen Datensatz. Um nur einzelne Strukturen abzuwählen, die Kontrollkästchen im Dropdown manuell deaktivieren.

### Feld Schichtordnung

Das **Schichtordnung**-Feld (`order_layer`) definiert die Position der SE in der stratigraphischen Sequenz.

**Wichtige Regeln:**
- Die Ordnung muss **immer sequentiell** sein: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13...
- **Keine Lücken erlaubt**: Sie können nicht 1, 2, 5, 8 haben (3, 4, 6, 7 fehlen)
- **Keine Duplikate**: Jede SE muss eine eindeutige Ordnungsnummer haben
- Wenn Sie alphabetische Ordnung verwenden: A, B, C, D, E, F... (auch keine Lücken)

**Automatische Berechnung:**
Die Schichtordnung wird automatisch aus den stratigraphischen Beziehungen berechnet. Das System analysiert die Beziehungen zwischen den SE (liegt über, liegt unter, schneidet, usw.) und weist jedem eine sequentielle Ordnungsnummer zu.

**Beispiel korrekter Ordnung:**
| SE | Schichtordnung |
|-----|---------------|
| US 1 | 1 |
| US 2 | 2 |
| US 3 | 3 |
| US 4 | 4 |

**Beispiel falscher Ordnung (vermeiden):**
| SE | Schichtordnung |
|-----|---------------|
| US 1 | 1 |
| US 2 | 3 | ← Falsch, 2 fehlt |
| US 3 | 7 | ← Falsch, 4, 5, 6 fehlen |

---

## Tab Stratigraphische Beziehungen

**Dies ist der wichtigste Tab des SE-Formulars.** Er definiert die stratigraphischen Beziehungen zu anderen Einheiten.

![Tab Beziehungen](images/03_se_formular/10_tab_rapporti.png)
*Abbildung 10: Tab Stratigraphische Beziehungen*

> **Video-Tutorial**: [Link zum Video stratigraphische Beziehungen einfügen]

### Struktur der Beziehungstabelle

| Spalte | Beschreibung |
|--------|-------------|
| **Fundort** | Fundort der korr. SE |
| **Areal** | Areal der korr. SE |
| **SE** | Nummer der korr. SE |
| **Beziehungstyp** | Art der Beziehung |

### Verfügbare Beziehungstypen

| Deutsch | Englisch | Italienisch |
|---------|----------|-------------|
| Liegt über | Covers | Copre |
| Liegt unter | Covered by | Coperto da |
| Schneidet | Cuts | Taglia |
| Geschnitten von | Cut by | Tagliato da |
| Verfüllt | Fills | Riempie |
| Verfüllt von | Filled by | Riempito da |
| Stützt sich auf | Abuts | Si appoggia a |
| Wird gestützt von | Supports | Gli si appoggia |
| Gleich | Same as | Uguale a |
| Früher | Earlier | Anteriore |
| Später | Later | Posteriore |

### Beziehungen einfügen

1. Klicken Sie auf **+** zum Hinzufügen einer Zeile
2. Geben Sie Fundort, Areal, SE der korr. SE ein
3. Wählen Sie den Beziehungstyp
4. Speichern

![Beziehung einfügen](images/03_se_formular/11_inserimento_rapporto.png)
*Abbildung 11: Einfügen einer stratigraphischen Beziehung*

### Beziehungsschaltflächen

| Schaltfläche | Funktion |
|--------------|----------|
| **+** | Zeile hinzufügen |
| **-** | Zeile entfernen |
| **Inverse Beziehung einfügen/aktualisieren** | Erstellt automatisch die inverse Beziehung |
| **Zur SE gehen** | Navigiert zur ausgewählten SE |
| **Matrix anzeigen** | Zeigt die Harris-Matrix |
| **Reparieren** | Korrigiert Beziehungsfehler |

### Automatische inverse Beziehungen

Wenn Sie eine Beziehung eingeben, können Sie automatisch die Umkehrung erstellen:

| Bei Eingabe von | Wird erstellt |
|-----------------|---------------|
| SE 1 **liegt über** SE 2 | SE 2 **liegt unter** SE 1 |
| SE 1 **schneidet** SE 2 | SE 2 **geschnitten von** SE 1 |
| SE 1 **verfüllt** SE 2 | SE 2 **verfüllt von** SE 1 |

### Beziehungsprüfung

Die Schaltfläche **Beziehungen prüfen** überprüft die Konsistenz:
- Erkennt fehlende Beziehungen
- Findet Inkonsistenzen
- Meldet logische Fehler

![Beziehungsprüfung](images/03_se_formular/12_controllo_rapporti.png)
*Abbildung 12: Ergebnis der Beziehungsprüfung*

---

## Tab Physische Daten

Beschreibt die physischen Eigenschaften der stratigraphischen Einheit.

![Tab Physische Daten](images/03_se_formular/14_tab_dati_fisici.png)
*Abbildung 14: Tab Physische Daten*

### Allgemeine Eigenschaften

| Feld | Werte |
|------|-------|
| **Farbe** | Braun, Gelb, Grau, Schwarz, usw. |
| **Konsistenz** | Tonig, Kompakt, Locker, Sandig |
| **Entstehung** | Künstlich, Natürlich |
| **Position** | - |
| **Entstehungsweise** | Aufschüttung, Abtragung, Anhäufung, Rutschung |
| **Unterscheidungskriterien** | Freitext |

### Komponententabellen

| Tabelle | Inhalt |
|---------|--------|
| **Organische Komp.** | Knochen, Holz, Holzkohle, Samen, usw. |
| **Anorganische Komp.** | Steine, Ziegel, Keramik, usw. |
| **Künstliche Einschlüsse** | Enthaltene anthropogene Materialien |

### Beprobung

| Feld | Werte |
|------|-------|
| **Flotation** | Ja / Nein |
| **Siebung** | Ja / Nein |
| **Zuverlässigkeit** | Gering, Gut, Befriedigend, Ausgezeichnet |
| **Erhaltungszustand** | Ungenügend, Gering, Gut, Befriedigend, Ausgezeichnet |

---

## Tab Erfassungsdaten

Informationen zur Formularerstellung.

![Tab Erfassungsdaten](images/03_se_formular/15_tab_schedatura.png)
*Abbildung 15: Tab Erfassungsdaten*

### Behörde und Verantwortliche

| Feld | Beschreibung |
|------|-------------|
| **Zuständige Behörde** | Behörde, die die Ausgrabung leitet |
| **Denkmalamt** | Zuständiges Denkmalamt |
| **Wissenschaftliche Leitung** | Grabungsleiter |
| **Erfasser** | Wer das Formular vor Ort ausgefüllt hat |
| **Bearbeiter** | Wer die Daten bearbeitet hat |

### Daten

| Feld | Format |
|------|--------|
| **Aufnahmedatum** | TT/MM/JJJJ |
| **Erfassungsdatum** | TT/MM/JJJJ |
| **Bearbeitungsdatum** | TT/MM/JJJJ |

---

## Tab SE-Maße

Enthält alle Messungen der stratigraphischen Einheit.

![Tab Maße](images/03_se_formular/16_tab_misure.png)
*Abbildung 16: Tab SE-Maße*

### Höhen

| Feld | Beschreibung | Einheit |
|------|-------------|---------|
| **Absolute Höhe** | Höhe über Meeresspiegel | Meter |
| **Relative Höhe** | Höhe bezogen auf Referenzpunkt | Meter |
| **Max. absolute Höhe** | Maximale absolute Höhe | Meter |
| **Min. absolute Höhe** | Minimale absolute Höhe | Meter |

### Abmessungen

| Feld | Beschreibung | Einheit |
|------|-------------|---------|
| **Max. Länge** | Maximale Länge | Meter |
| **Mittlere Breite** | Durchschnittliche Breite | Meter |
| **Max. Höhe** | Maximale Höhe | Meter |
| **Min. Höhe** | Minimale Höhe | Meter |
| **Stärke** | Schichtdicke | Meter |
| **Max. Tiefe** | Maximale Tiefe | Meter |

---

## Tab Dokumentation

Verwaltet die Verweise auf grafische und fotografische Dokumentation.

![Tab Dokumentation](images/03_se_formular/17_tab_documentazione.png)
*Abbildung 17: Tab Dokumentation*

### Dokumentationstabelle

| Spalte | Beschreibung |
|--------|-------------|
| **Dokumentationstyp** | Foto, Planum, Profil, Ansicht, usw. |
| **Referenzen** | Nummer/Code des Dokuments |

### Dokumentationstypen

| Typ | Beschreibung |
|-----|-------------|
| Foto | Fotodokumentation |
| Planum | Grabungsplan |
| Profil | Stratigraphisches Profil |
| Ansicht | Maueransicht |
| Zeichnung | Grafische Zeichnung |
| 3D | Dreidimensionales Modell |

---

## Tab Bautechnik USM

Tab speziell für Mauerwerks-Stratigraphische Einheiten (USM).

![Tab Bautechnik](images/03_se_formular/18_tab_tecnica_usm.png)
*Abbildung 18: Tab Bautechnik USM*

### USM-spezifische Daten

| Feld | Beschreibung |
|------|-------------|
| **USM-Länge** | Länge des Mauerwerks (Meter) |
| **USM-Höhe** | Höhe des Mauerwerks (Meter) |
| **Analysierte Fläche** | Prozentsatz analysiert |
| **Mauerquerschnitt** | Querschnittstyp |
| **Modul** | Baumodul |
| **Werktyp** | Mauerwerkstyp |
| **Orientierung** | Strukturausrichtung |
| **Wiederverwendung** | Ja / Nein |

### Materialien und Techniken

| Bereich | Felder |
|---------|--------|
| **Ziegel** | Materialien, Bearbeitung, Konsistenz, Form, Farbe, Mischung, Verlegung |
| **Steinelemente** | Materialien, Bearbeitung, Konsistenz, Form, Farbe, Schnitt, Verlegung |

---

## Tab Bindemittel USM

Beschreibt die Eigenschaften der Bindemittel (Mörtel) in Mauerstrukturen.

![Tab Bindemittel](images/03_se_formular/19_tab_leganti.png)
*Abbildung 19: Tab Bindemittel USM*

### Bindemitteleigenschaften

| Feld | Beschreibung |
|------|-------------|
| **Bindemitteltyp** | Mörtel, Lehm, Keines, usw. |
| **Konsistenz** | Fest, Locker, usw. |
| **Farbe** | Bindemittelfarbe |
| **Oberfläche** | Oberflächentyp |
| **Bindemittelstärke** | Stärke in cm |

---

## Tab Medien

Zeigt die der stratigraphischen Einheit zugeordneten Bilder an.

![Tab Medien](images/03_se_formular/20_tab_media.png)
*Abbildung 20: Tab Medien*

### SE-Liste

Die Tabelle zeigt alle SE mit zugehörigen Bildern:
- Zum Formular navigieren
- Kontrollkästchen für Mehrfachauswahl
- Vorschau-Thumbnails

---

## Tab Hilfe - Tool Box

Enthält erweiterte Werkzeuge für Kontrolle und Export.

![Tab Tool Box](images/03_se_formular/21_tab_toolbox.png)
*Abbildung 21: Tab Tool Box*

### Kontrollsysteme

| Werkzeug | Beschreibung |
|----------|-------------|
| **Stratigraphische Beziehungen prüfen** | Überprüft Beziehungskonsistenz |
| **Prüfen, los!!!!** | Führt Prüfung aus |

### Matrix-Export

| Schaltfläche | Ausgabe |
|--------------|---------|
| **Matrix exportieren** | DOT-Datei für Graphviz |
| **GraphML exportieren** | GraphML-Datei für yEd |
| **In Extended Matrix exportieren** | S3DGraphy-Format |
| **Interaktive Matrix** | Interaktive Visualisierung |

---

## Harris-Matrix

Die Harris-Matrix ist eine grafische Darstellung der stratigraphischen Beziehungen.

![Harris-Matrix](images/03_se_formular/22_matrix_harris.png)
*Abbildung 22: Beispiel einer Harris-Matrix*

> **Video-Tutorial**: [Link zum Video Harris-Matrix einfügen]

### Matrix-Generierung

1. Fundort und Areal auswählen
2. Überprüfen, ob die Beziehungen korrekt sind
3. Zu **Tab Hilfe** → **Tool Box** gehen
4. Auf **Matrix exportieren** klicken

### Exportformate

| Format | Software | Verwendung |
|--------|----------|------------|
| DOT | Graphviz | Basisvisualisierung |
| GraphML | yEd, Gephi | Erweiterte Bearbeitung |
| Extended Matrix | S3DGraphy | 3D-Visualisierung |
| CSV | Excel | Datenanalyse |

---

## GIS-Funktionen

Das SE-Formular ist eng mit QGIS integriert.

![GIS-Integration](images/03_se_formular/24_gis_integration.png)
*Abbildung 24: GIS-Integration*

### GIS-Toolbar

| Schaltfläche | Funktion | Tastenkürzel |
|--------------|----------|--------------|
| **GIS-Viewer** | Lädt SE-Layer | Strg+G |
| **SE-Plan-Vorschau** | Geometrievorschau | Strg+G |
| **SE zeichnen** | Aktiviert Zeichnen | - |

### Zugehörige GIS-Layer

| Layer | Geometrie | Beschreibung |
|-------|-----------|-------------|
| PYUS | Polygon | Stratigraphische Einheiten |
| PYUSM | Polygon | Mauerwerkseinheiten |
| PYQUOTE | Punkt | Höhenpunkte |
| PYQUOTEUSM | Punkt | USM-Höhenpunkte |
| PYUS_NEGATIVE | Polygon | Negative SE |

---

## Exporte

### SE-Formulare PDF

1. Klicken Sie auf **Bericht** in der Toolbar
2. Format wählen (PDF, Word)
3. Zu exportierende Formulare auswählen

![PDF-Export](images/03_se_formular/25_esportazione_pdf.png)
*Abbildung 25: PDF-Exportoptionen*

### Listen

| Typ | Inhalt |
|-----|--------|
| **SE-Liste** | Liste aller SE |
| **Fotoliste mit Thumbnails** | Liste mit Vorschauen |
| **Fotoliste ohne Thumbnails** | Einfache Liste |
| **SE-Formulare** | Vollständige Formulare |

---

## Operativer Arbeitsablauf

### Neue SE erstellen

> **Video-Tutorial**: [Link zum Video SE-Erstellung einfügen]

#### Schritt 1: Formular öffnen
![Schritt 1](images/03_se_formular/26_workflow_step1.png)

#### Schritt 2: Neuer Datensatz klicken
![Schritt 2](images/03_se_formular/27_workflow_step2.png)

#### Schritt 3: Identifikatoren eingeben
- Fundort auswählen
- Areal eingeben
- SE-Nummer eingeben
- Typ auswählen

![Schritt 3](images/03_se_formular/28_workflow_step3.png)

#### Schritt 4: Definitionen
- Stratigraphische Definition auswählen
- Interpretative Definition auswählen

![Schritt 4](images/03_se_formular/29_workflow_step4.png)

#### Schritt 5: Beschreibung
- Physische Beschreibung ausfüllen
- Interpretation ausfüllen

![Schritt 5](images/03_se_formular/30_workflow_step5.png)

#### Schritt 6: Stratigraphische Beziehungen
- Beziehungen zu anderen SE eingeben
- Inverse Beziehungen erstellen

![Schritt 6](images/03_se_formular/31_workflow_step6.png)

#### Schritt 7: Physische Daten und Maße
- Physische Eigenschaften ausfüllen
- Maße eingeben

![Schritt 7](images/03_se_formular/32_workflow_step7.png)

#### Schritt 8: Speichern
- Auf Speichern klicken
- Speicherung überprüfen

![Schritt 8](images/03_se_formular/33_workflow_step8.png)

---

## Fehlerbehebung

### Speicherfehler
- Überprüfen Sie, ob Fundort, Areal und SE ausgefüllt sind
- Stellen Sie sicher, dass die Kombination eindeutig ist

### Inkonsistente Beziehungen
- Beziehungsprüfung verwenden
- Inverse Beziehungen überprüfen
- Mit der Reparieren-Schaltfläche korrigieren

### Matrix wird nicht generiert
- Überprüfen Sie, ob Graphviz installiert ist
- Pfad in der Konfiguration kontrollieren
- Stellen Sie sicher, dass Beziehungen existieren

### GIS-Layer werden nicht geladen
- Datenbankverbindung überprüfen
- Kontrollieren, ob Geometrien existieren
- Referenzsystem überprüfen

---

## Technische Hinweise

### Datenbank

- **Haupttabelle**: `us_table`
- **Hauptfelder**: über 80 Felder
- **Primärschlüssel**: `id_us`
- **Zusammengesetzter Schlüssel**: fundort + areal + se

### Thesaurus

Felder mit Thesaurus (Definitionen) verwenden die Tabelle `pyarchinit_thesaurus_sigle`:
- tipologia_sigla = '1.1' für stratigraphische Definition
- tipologia_sigla = '1.2' für interpretative Definition

---

*PyArchInit-Dokumentation - SE/USM-Formular*
*Version: 4.9.x*
*Letzte Aktualisierung: Januar 2026*
