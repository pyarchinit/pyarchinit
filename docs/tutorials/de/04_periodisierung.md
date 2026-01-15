# Tutorial 04: Periodisierungsformular

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Zugriff auf das Formular](#zugriff-auf-das-formular)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Grundlegende Konzepte](#grundlegende-konzepte)
5. [Formularfelder](#formularfelder)
6. [DBMS-Toolbar](#dbms-toolbar)
7. [GIS-Funktionen](#gis-funktionen)
8. [PDF-Export](#pdf-export)
9. [KI-Integration](#ki-integration)
10. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
11. [Best Practices](#best-practices)
12. [Fehlerbehebung](#fehlerbehebung)

---

## Einführung

Das **Periodisierungsformular** ist ein grundlegendes Werkzeug für die Verwaltung der chronologischen Phasen einer archäologischen Ausgrabung. Es ermöglicht die Definition von Perioden und Phasen, die die stratigraphische Sequenz des Fundorts charakterisieren, wobei jeder Periode/Phase-Kombination eine chronologische Datierung und Beschreibung zugeordnet werden kann.

### Zweck des Formulars

- Definition der chronologischen Sequenz der Ausgrabung
- Zuordnung von Perioden und Phasen zu stratigraphischen Einheiten
- Verwaltung der absoluten (Jahre) und relativen (historische Perioden) Chronologie
- Visualisierung der SE nach Periode/Phase auf der GIS-Karte
- Generierung von PDF-Berichten der Periodisierung

### Beziehung zu anderen Formularen

Das Periodisierungsformular ist eng verbunden mit:
- **SE/USM-Formular**: Jede SE wird einer Periode und Phase zugeordnet
- **Fundort-Formular**: Perioden sind spezifisch für jeden Fundort
- **Harris-Matrix**: Perioden färben die Matrix nach chronologischer Phase

![Übersicht Periodisierungsformular](images/04_periodisierung/01_panoramica.png)
*Abbildung 1: Gesamtübersicht des Periodisierungsformulars*

---

## Zugriff auf das Formular

### Über Menü

1. QGIS mit aktivem PyArchInit-Plugin öffnen
2. Menü **PyArchInit** → **Archaeological record management** → **Excavation - Loss of use calculation** → **Period and Phase**

![Menü Periodisierung](images/04_periodisierung/02_menu_accesso.png)
*Abbildung 2: Zugriff auf das Formular über Menü*

### Über Toolbar

1. PyArchInit-Toolbar finden
2. Auf das Symbol **Periodisierung** klicken (Fundort-Symbol mit Uhr)

![Toolbar Periodisierung](images/04_periodisierung/03_toolbar_accesso.png)
*Abbildung 3: Symbol in der Toolbar*

---

## Benutzeroberfläche

Die Oberfläche des Periodisierungsformulars ist einfach und linear organisiert:

![Vollständige Oberfläche](images/04_periodisierung/04_interfaccia_completa.png)
*Abbildung 4: Vollständiges Oberflächen-Layout*

### Hauptbereiche

| Bereich | Beschreibung |
|---------|-------------|
| **1. DBMS-Toolbar** | Werkzeugleiste für Navigation und Datensatzverwaltung |
| **2. Statusanzeigen** | DB-Info, Status, Sortierung |
| **3. Identifikationsdaten** | Fundort, Periode, Phase, Periodencode |
| **4. Beschreibende Daten** | Textuelle Beschreibung der Periode |
| **5. Chronologie** | Anfangs- und Endjahre |
| **6. Erweiterte Datierung** | Auswahl aus Vokabular historischer Epochen |

---

## Grundlegende Konzepte

### Periode und Phase

Das Periodisierungssystem in PyArchInit basiert auf einer hierarchischen Struktur mit zwei Ebenen:

#### Periode
Die **Periode** repräsentiert eine Makrophase der chronologischen Ausgrabungssequenz. Sie wird durch eine Ganzzahl (1, 2, 3, ...) identifiziert und stellt die großen Unterteilungen der stratigraphischen Sequenz dar.

Beispiele für Perioden:
- Periode 1: Zeitgenössische Ära
- Periode 2: Mittelalter
- Periode 3: Römische Kaiserzeit
- Periode 4: Römische Republik

#### Phase
Die **Phase** repräsentiert eine interne Unterteilung der Periode. Auch diese wird durch eine Ganzzahl identifiziert und ermöglicht eine weitere Detaillierung der Sequenz.

Beispiele für Phasen in Periode 3 (Römische Kaiserzeit):
- Phase 1: 3.-4. Jahrhundert n. Chr.
- Phase 2: 2. Jahrhundert n. Chr.
- Phase 3: 1. Jahrhundert n. Chr.

### Periodencode

Der **Periodencode** ist ein eindeutiger numerischer Bezeichner, der die Periode/Phase-Kombination mit den SE verbindet. Bei der Zuweisung einer Periode/Phase zu einer SE im SE-Formular wird dieser Code verwendet.

> **Wichtig**: Der Periodencode muss für jede Kombination aus Fundort/Periode/Phase eindeutig sein.

### Konzeptionelles Schema

```
Fundort
└── Periode 1 (Zeitgenössisch)
│   ├── Phase 1 → Code 101
│   └── Phase 2 → Code 102
├── Periode 2 (Mittelalter)
│   ├── Phase 1 → Code 201
│   ├── Phase 2 → Code 202
│   └── Phase 3 → Code 203
└── Periode 3 (Römisch)
    ├── Phase 1 → Code 301
    └── Phase 2 → Code 302
```

---

## Formularfelder

### Identifikationsfelder

#### Fundort
- **Typ**: ComboBox (schreibgeschützt im Browse-Modus)
- **Pflichtfeld**: Ja
- **Beschreibung**: Wählt den archäologischen Fundort, zu dem die Periodisierung gehört
- **Hinweis**: Wenn ein Standardfundort in der Konfiguration eingestellt ist, wird dieses Feld vorausgefüllt und nicht änderbar sein

![Feld Fundort](images/04_periodisierung/05_campo_sito.png)
*Abbildung 5: Fundortauswahlfeld*

#### Periode
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Ja
- **Werte**: Ganzzahlen von 1 bis 15 (vordefiniert) oder benutzerdefinierte Werte
- **Beschreibung**: Nummer der chronologischen Periode
- **Hinweis**: Niedrige Zahlen zeigen jüngere Perioden, hohe Zahlen ältere Perioden

#### Phase
- **Typ**: Editierbare ComboBox
- **Pflichtfeld**: Ja
- **Werte**: Ganzzahlen von 1 bis 15 (vordefiniert) oder benutzerdefinierte Werte
- **Beschreibung**: Phasennummer innerhalb der Periode

![Felder Periode und Phase](images/04_periodisierung/06_campi_periodo_fase.png)
*Abbildung 6: Felder Periode und Phase*

#### Periodencode
- **Typ**: LineEdit (Text)
- **Pflichtfeld**: Nein (aber dringend empfohlen)
- **Beschreibung**: Eindeutiger numerischer Code zur Identifikation der Periode/Phase-Kombination
- **Empfehlung**: Konvention wie `[Periode][Phase]` verwenden (z.B. 101, 102, 201, 301)

![Feld Periodencode](images/04_periodisierung/07_codice_periodo.png)
*Abbildung 7: Feld Periodencode*

### Beschreibende Felder

#### Beschreibung
- **Typ**: TextEdit (mehrzeilig)
- **Pflichtfeld**: Nein
- **Beschreibung**: Textuelle Beschreibung der Periode/Phase
- **Empfohlener Inhalt**:
  - Allgemeine Merkmale der Periode
  - Korrelierte historische Ereignisse
  - Erwartete Struktur-/Materialtypen
  - Bibliografische Referenzen

![Feld Beschreibung](images/04_periodisierung/08_campo_descrizione.png)
*Abbildung 8: Beschreibungsfeld*

### Chronologische Felder

#### Anfangschronologie
- **Typ**: LineEdit (numerisch)
- **Pflichtfeld**: Nein
- **Format**: Numerisches Jahr
- **Hinweise**:
  - Positive Werte = n. Chr.
  - Negative Werte = v. Chr.
  - Beispiel: `-100` für 100 v. Chr., `200` für 200 n. Chr.

#### Endchronologie
- **Typ**: LineEdit (numerisch)
- **Pflichtfeld**: Nein
- **Format**: Numerisches Jahr (gleiche Konventionen wie Anfangschronologie)

![Chronologiefelder](images/04_periodisierung/09_campi_cronologia.png)
*Abbildung 9: Felder Anfangs- und Endchronologie*

#### Erweiterte Datierung (Historische Epochen)
- **Typ**: Editierbare ComboBox mit vorgeladenem Vokabular
- **Pflichtfeld**: Nein
- **Beschreibung**: Auswahl aus einem Vokabular vordefinierter historischer Epochen
- **Automatische Funktion**: Bei Auswahl einer Epoche werden die Felder Anfangs- und Endchronologie automatisch ausgefüllt

![Erweiterte Datierung](images/04_periodisierung/10_datazione_estesa.png)
*Abbildung 10: ComboBox Erweiterte Datierung mit vorgeladenen Epochen*

### Vokabular Historische Epochen

Das Vokabular umfasst eine breite Palette historischer Perioden:

| Kategorie | Beispiele |
|-----------|-----------|
| **Zeitgenössische Ära** | 21. Jahrhundert, 20. Jahrhundert |
| **Neuzeit** | 19.-16. Jahrhundert |
| **Mittelalter** | 15.-8. Jahrhundert |
| **Antike** | 7.-1. Jahrhundert |
| **Römisches Reich** | Spezifische Perioden (Julisch-Claudisch, Flavisch, usw.) |
| **Byzantinisches Reich** | Spezifische Perioden |
| **Vorgeschichte** | Paläolithikum, Mesolithikum, Neolithikum, Bronzezeit, Eisenzeit |

---

## DBMS-Toolbar

Die DBMS-Toolbar ermöglicht die vollständige Verwaltung der Datensätze:

![DBMS-Toolbar](images/04_periodisierung/11_toolbar_dbms.png)
*Abbildung 11: Vollständige DBMS-Toolbar*

### Navigationsschaltflächen

| Symbol | Name | Funktion |
|--------|------|----------|
| ![First](images/icons/first.png) | Erster | Zum ersten Datensatz |
| ![Prev](images/icons/prev.png) | Vorheriger | Zum vorherigen Datensatz |
| ![Next](images/icons/next.png) | Nächster | Zum nächsten Datensatz |
| ![Last](images/icons/last.png) | Letzter | Zum letzten Datensatz |

### Datensatzverwaltungsschaltflächen

| Symbol | Name | Funktion |
|--------|------|----------|
| ![New](images/icons/new.png) | Neuer Datensatz | Erstellt neuen Datensatz |
| ![Save](images/icons/save.png) | Speichern | Speichert Änderungen |
| ![Delete](images/icons/delete.png) | Löschen | Löscht aktuellen Datensatz |
| ![View All](images/icons/view_all.png) | Alle anzeigen | Zeigt alle Datensätze |

### Suchschaltflächen

| Symbol | Name | Funktion |
|--------|------|----------|
| ![New Search](images/icons/new_search.png) | Neue Suche | Aktiviert Suchmodus |
| ![Search](images/icons/search.png) | Suche!!! | Führt Suche aus |
| ![Sort](images/icons/sort.png) | Sortieren nach | Sortiert Datensätze |

### Statusanzeigen

![Statusanzeigen](images/04_periodisierung/12_indicatori_stato.png)
*Abbildung 12: Statusanzeigen*

| Anzeige | Beschreibung |
|---------|-------------|
| **Status** | Aktueller Modus: "Verwenden" (Browse), "Suchen" (Suche), "Neuer Datensatz" |
| **Sortierung** | "Nicht sortiert" oder "Sortiert" |
| **Datensatz Nr.** | Nummer des aktuellen Datensatzes |
| **Gesamt** | Gesamtzahl der Datensätze |

---

## GIS-Funktionen

Das Periodisierungsformular bietet leistungsstarke GIS-Visualisierungsfunktionen zur Anzeige der jeder Periode/Phase zugeordneten SE.

### GIS-Schaltflächen

![GIS-Schaltflächen](images/04_periodisierung/13_pulsanti_gis.png)
*Abbildung 13: Schaltflächen für GIS-Visualisierung*

#### Einzelne Periode anzeigen (GIS-Symbol)
- **Funktion**: Lädt alle der aktuellen Periode/Phase zugeordneten SE auf die QGIS-Karte
- **Voraussetzung**: Das Feld Periodencode muss ausgefüllt sein
- **Geladene Layer**: SE und USM gefiltert nach Periodencode

#### Alle Perioden anzeigen - SE (Mehrfach-Layer-Symbol)
- **Funktion**: Lädt alle Perioden als separate Layer auf die Karte (nur SE)
- **Ergebnis**: Ein Layer für jede Periode/Phase-Kombination

#### Alle Perioden anzeigen - USM (GIS3-Symbol)
- **Funktion**: Lädt alle Perioden als separate Layer auf die Karte (nur USM)
- **Ergebnis**: Ein Layer für jede Periode/Phase-Kombination für Mauerwerkseinheiten

### Kartenanzeige

![Karte mit Perioden](images/04_periodisierung/14_mappa_periodi.png)
*Abbildung 14: SE nach Periode auf der QGIS-Karte visualisiert*

Beim Laden der Layer nach Periode:
- Jede Periode/Phase hat eine charakteristische Farbe
- SE werden basierend auf dem zugewiesenen Periodencode gefiltert
- Einzelne Layer können ein-/ausgeschaltet werden

---

## PDF-Export

Das Formular bietet zwei PDF-Exportmodi:

### Export Einzelformular

![Schaltfläche PDF-Formular](images/04_periodisierung/15_pulsante_pdf_scheda.png)
*Abbildung 15: Schaltfläche PDF-Formularexport*

- **Symbol**: PDF
- **Funktion**: Generiert ein PDF mit den Daten der aktuellen Periode/Phase
- **Inhalt**:
  - Identifikationsdaten (Fundort, Periode, Phase)
  - Chronologie (Anfang, Ende, erweiterte Datierung)
  - Vollständige Beschreibung

### Export Periodisierungsliste

![Schaltfläche PDF-Liste](images/04_periodisierung/16_pulsante_pdf_lista.png)
*Abbildung 16: Schaltfläche PDF-Listenexport*

- **Symbol**: Blatt/Sheet
- **Funktion**: Generiert ein PDF mit der Liste aller Perioden/Phasen des Fundorts
- **Inhalt**: Zusammenfassungstabelle mit allen Perioden

---

## KI-Integration

Das Periodisierungsformular enthält eine GPT-Integration für automatische Vorschläge zur Beschreibung historischer Perioden.

### Schaltfläche Vorschläge

![Schaltfläche Vorschläge](images/04_periodisierung/18_pulsante_suggerimenti.png)
*Abbildung 18: KI-Vorschläge-Schaltfläche*

### Funktionsweise

1. Eine historische Epoche aus dem Feld **Erweiterte Datierung** auswählen
2. Auf die Schaltfläche **Vorschläge** klicken
3. Das zu verwendende GPT-Modell auswählen (gpt-4o oder gpt-4)
4. Das System generiert automatisch:
   - Eine Beschreibung der historischen Periode
   - 3 relevante Wikipedia-Links
5. Der generierte Text kann in das Beschreibungsfeld eingefügt werden

### API-Key-Konfiguration

Zur Nutzung dieser Funktion:
1. API-Key von OpenAI erhalten
2. Bei der ersten Verwendung fragt das System nach dem Schlüssel
3. Der Schlüssel wird in `PYARCHINIT_HOME/bin/gpt_api_key.txt` gespeichert

> **Hinweis**: Diese Funktion erfordert eine Internetverbindung und ein OpenAI-Konto mit verfügbarem Guthaben.

---

## Operativer Arbeitsablauf

### Neue Periodisierung erstellen

#### Schritt 1: Formularzugriff
1. Periodisierungsformular über Menü oder Toolbar öffnen
2. Datenbankverbindung überprüfen (Statusanzeige)

![Workflow Schritt 1](images/04_periodisierung/19_workflow_step1.png)
*Abbildung 19: Formular öffnen*

#### Schritt 2: Neuer Datensatz
1. Auf **Neuer Datensatz** klicken
2. Status ändert sich zu "Neuer Datensatz"
3. Felder werden editierbar

![Workflow Schritt 2](images/04_periodisierung/20_workflow_step2.png)
*Abbildung 20: Klick auf Neuer Datensatz*

#### Schritt 3: Fundort auswählen
1. Falls nicht voreingestellt, **Fundort** aus Dropdown auswählen
2. Der Fundort muss bereits im Fundort-Formular existieren

![Workflow Schritt 3](images/04_periodisierung/21_workflow_step3.png)
*Abbildung 21: Fundortauswahl*

#### Schritt 4: Periode und Phase definieren
1. **Perioden**-Nummer auswählen oder eingeben
2. **Phasen**-Nummer auswählen oder eingeben
3. Eindeutigen **Periodencode** eingeben

![Workflow Schritt 4](images/04_periodisierung/22_workflow_step4.png)
*Abbildung 22: Periode und Phase definieren*

#### Schritt 5: Chronologie
1. **Erweiterte Datierung** aus Epochenvokabular auswählen
2. Felder Anfangs- und Endchronologie werden automatisch ausgefüllt
3. Oder Jahre manuell eingeben

![Workflow Schritt 5](images/04_periodisierung/23_workflow_step5.png)
*Abbildung 23: Chronologie einstellen*

#### Schritt 6: Beschreibung
1. **Beschreibungs**-Feld mit Periodeninformationen ausfüllen
2. Optional: **Vorschläge**-Schaltfläche für KI-generierten Text verwenden

![Workflow Schritt 6](images/04_periodisierung/24_workflow_step6.png)
*Abbildung 24: Beschreibung ausfüllen*

#### Schritt 7: Speichern
1. Auf **Speichern** klicken
2. Datensatz wird in der Datenbank gespeichert
3. Status kehrt zu "Verwenden" zurück

![Workflow Schritt 7](images/04_periodisierung/25_workflow_step7.png)
*Abbildung 25: Speichern*

### Empfohlenes Periodisierungsschema

Für eine typische Ausgrabung wird empfohlen, die Periodisierung nach diesem Schema zu erstellen:

| Periode | Phase | Code | Beschreibung |
|---------|-------|------|-------------|
| 1 | 1 | 101 | Zeitgenössisch - Ackerbau |
| 1 | 2 | 102 | Zeitgenössisch - Aufgabe |
| 2 | 1 | 201 | Mittelalter - Spätphase |
| 2 | 2 | 202 | Mittelalter - Mittelphase |
| 2 | 3 | 203 | Mittelalter - Frühphase |
| 3 | 1 | 301 | Römisch - Kaiserzeit |
| 3 | 2 | 302 | Römisch - Republik |
| 4 | 1 | 401 | Vorrömisch |

---

## Best Practices

### Nummerierungskonventionen

1. **Perioden**: Vom jüngsten (1) zum ältesten nummerieren
2. **Phasen**: Vom jüngsten (1) zum ältesten innerhalb der Periode nummerieren
3. **Codes**: Formel `[Periode * 100 + Phase]` für eindeutige Codes verwenden

### Effektive Beschreibungen

Eine gute Periodenbeschreibung sollte enthalten:
- Chronologische Einordnung
- Hauptmerkmale der Periode
- Erwartete Struktur-/Materialtypen
- Vergleiche mit zeitgleichen Fundorten
- Bibliografische Referenzen

### Chronologieverwaltung

- Immer numerische Jahre für Chronologien verwenden
- Für v. Chr.-Daten negative Zahlen verwenden
- Konsistenz überprüfen: Endchronologie muss >= Anfangschronologie sein (im Absolutwert für v. Chr.)

### Verbindung mit SE

Nach Erstellung der Periodisierung:
1. SE-Formular öffnen
2. Im Tab **Periodisierung** Anfangs-/Endperiode und Anfangs-/Endphase zuweisen
3. Das System ordnet die SE automatisch der Periodisierung zu

---

## Fehlerbehebung

### Häufige Probleme

#### "Periodencode nicht hinzugefügt"
- **Ursache**: Das Feld Periodencode ist leer
- **Lösung**: Periodencode-Feld vor Verwendung der GIS-Funktionen ausfüllen

#### Chronologie wird nicht automatisch ausgefüllt
- **Ursache**: Die ausgewählte Epoche hat keine zugeordneten Daten
- **Lösung**: Überprüfen, ob die Epoche in der CSV-Datei der historischen Epochen vorhanden ist

#### Speicherfehler: Doppelter Datensatz
- **Ursache**: Es existiert bereits ein Datensatz mit derselben Kombination Fundort/Periode/Phase
- **Lösung**: Werte überprüfen und eindeutige Kombination verwenden

#### SE erscheinen nicht in der GIS-Visualisierung
- **Ursache**: Den SE ist kein Periodencode zugewiesen
- **Lösung**:
  1. Im SE-Formular überprüfen, ob die Felder Periode/Phase ausgefüllt sind
  2. Überprüfen, ob der Periodencode übereinstimmt

#### KI-Vorschläge funktioniert nicht
- **Ursache**: API-Key fehlt oder ist ungültig
- **Lösung**:
  1. Internetverbindung überprüfen
  2. Gültigkeit des API-Keys kontrollieren
  3. Bibliotheken neu installieren: `pip install --upgrade openai pydantic`

---

## Video-Tutorial

### Video 1: Übersicht Periodisierungsformular
*Dauer: 3-4 Minuten*

[Platzhalter für Video-Tutorial]

**Inhalte:**
- Formular öffnen
- Oberflächenbeschreibung
- Navigation zwischen Datensätzen

### Video 2: Vollständige Periodisierung erstellen
*Dauer: 5-6 Minuten*

[Platzhalter für Video-Tutorial]

**Inhalte:**
- Neue Periodisierung erstellen
- Alle Felder ausfüllen
- Epochenvokabular verwenden
- Speichern

### Video 3: GIS-Visualisierung nach Periode
*Dauer: 3-4 Minuten*

[Platzhalter für Video-Tutorial]

**Inhalte:**
- GIS-Schaltflächen verwenden
- SE nach Periode visualisieren
- Geladene Layer verwalten

---

## Feldübersicht

| Feld | Typ | Pflicht | Datenbank |
|------|-----|---------|-----------|
| Fundort | ComboBox | Ja | sito |
| Periode | ComboBox | Ja | periodo |
| Phase | ComboBox | Ja | fase |
| Periodencode | LineEdit | Nein | cont_per |
| Beschreibung | TextEdit | Nein | descrizione |
| Anfangschronologie | LineEdit | Nein | cron_iniziale |
| Endchronologie | LineEdit | Nein | cron_finale |
| Erweiterte Datierung | ComboBox | Nein | datazione_estesa |

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Sketches of Sketches*
