# PyArchInit - Fundort-Formular

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Zugriff auf das Formular](#zugriff-auf-das-formular)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Beschreibende Daten des Fundorts](#beschreibende-daten-des-fundorts)
5. [DBMS-Toolbar](#dbms-toolbar)
6. [GIS-Funktionen](#gis-funktionen)
7. [SE-Generierung](#se-generierung)
8. [MoveCost - Weganalyse](#movecost---weganalyse)
9. [Berichtexport](#berichtexport)
10. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)

---

## Einführung

Das **Fundort-Formular** ist der Ausgangspunkt für die Dokumentation einer archäologischen Ausgrabung in PyArchInit. Jedes archäologische Projekt beginnt mit der Erstellung eines Fundorts, der als Hauptcontainer für alle anderen Informationen dient (Stratigraphische Einheiten, Strukturen, Funde, etc.).

Ein **archäologischer Fundort** in PyArchInit stellt ein definiertes geografisches Gebiet dar, in dem archäologische Forschungsaktivitäten durchgeführt werden. Dies kann eine Ausgrabung, ein Survey-Gebiet, ein Monument usw. sein.

> **Video-Tutorial**: [Link zum Einführungsvideo des Fundort-Formulars einfügen]

---

## Zugriff auf das Formular

Um auf das Fundort-Formular zuzugreifen:

1. Menü **PyArchInit** → **Archaeological record management** → **Site**
2. Oder klicken Sie in der PyArchInit-Toolbar auf das Symbol **Fundort**

![Zugriff Fundort-Formular](images/02_fundort_formular/01_menu_scheda_sito.png)
*Abbildung 1: Zugriff auf das Fundort-Formular über das PyArchInit-Menü*

![Toolbar Fundort](images/02_fundort_formular/02_toolbar_sito.png)
*Abbildung 2: Fundort-Symbol in der Toolbar*

---

## Benutzeroberfläche

Das Fundort-Formular ist in verschiedene Funktionsbereiche unterteilt:

![Oberfläche Fundort-Formular](images/02_fundort_formular/03_interfaccia_completa.png)
*Abbildung 3: Vollständige Oberfläche des Fundort-Formulars*

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | **DBMS-Toolbar** | Werkzeugleiste für Navigation und Datensatzverwaltung |
| 2 | **Beschreibende Daten** | Felder zur Eingabe der Fundortinformationen |
| 3 | **SE-Generator** | Werkzeug zum Batch-Erstellen von SE-Formularen |
| 4 | **GIS-Viewer** | Steuerelemente für kartografische Anzeige |
| 5 | **MoveCost** | Erweiterte räumliche Analysewerkzeuge |
| 6 | **Hilfe** | Dokumentation und Video-Tutorials |

---

## Beschreibende Daten des Fundorts

### Tab Beschreibende Daten

![Tab Beschreibende Daten](images/02_fundort_formular/04_tab_dati_descrittivi.png)
*Abbildung 4: Tab Beschreibende Daten*

#### Pflichtfelder

| Feld | Beschreibung | Hinweis |
|------|-------------|---------|
| **Fundort** | Identifizierender Name des Fundorts | Pflichtfeld, muss eindeutig sein |

#### Geografische Felder

| Feld | Beschreibung | Beispiel |
|------|-------------|----------|
| **Land** | Staat, in dem sich der Fundort befindet | Deutschland |
| **Region** | Verwaltungsregion | Bayern |
| **Provinz** | Landkreis | München |
| **Gemeinde** | Gemeinde | München |

![Geografische Felder](images/02_fundort_formular/05_campi_geografici.png)
*Abbildung 5: Beispiel ausgefüllter geografischer Felder*

#### Beschreibende Felder

| Feld | Beschreibung |
|------|-------------|
| **Name** | Erweiterter/beschreibender Name des Fundorts |
| **Definition** | Fundorttyp (aus Thesaurus) |
| **Beschreibung** | Freitextfeld für detaillierte Beschreibung |
| **Ordner** | Pfad zum lokalen Projektordner |

![Beschreibungsfeld](images/02_fundort_formular/06_campo_descrizione.png)
*Abbildung 6: Textfeld Beschreibung*

### Fundortdefinition (Thesaurus)

Das Feld **Definition** verwendet ein kontrolliertes Vokabular (Thesaurus). Verfügbare Optionen umfassen:

| Definition | Beschreibung |
|------------|-------------|
| Ausgrabungsgebiet | Zone mit stratigraphischer Untersuchung |
| Survey-Gebiet | Oberflächenprospektionsgebiet |
| Archäologischer Fundort | Lokalität mit archäologischen Befunden |
| Monument | Einzelnes monumentales Bauwerk |
| Nekropole | Bestattungsareal |
| Siedlung | Wohngebiet |
| Heiligtum | Sakraler/kultischer Bereich |

![Fundortdefinition](images/02_fundort_formular/07_definizione_sito.png)
*Abbildung 7: Auswahl der Fundortdefinition aus Thesaurus*

### Projektordner

Das Feld **Ordner** ermöglicht die Zuordnung eines lokalen Verzeichnisses zum Fundort zur Organisation der Projektdateien.

![Ordnerauswahl](images/02_fundort_formular/08_selezione_cartella.png)
*Abbildung 8: Auswahl des Projektordners*

| Schaltfläche | Funktion |
|--------------|----------|
| **...** | Durchsuchen zur Ordnerauswahl |
| **Öffnen** | Öffnet den Ordner im Dateimanager |

---

## DBMS-Toolbar

Die DBMS-Toolbar bietet alle Steuerelemente für die Datensatzverwaltung.

![DBMS-Toolbar](images/02_fundort_formular/09_toolbar_dbms.png)
*Abbildung 9: DBMS-Toolbar*

### Statusanzeigen

| Anzeige | Beschreibung |
|---------|-------------|
| **DB Info** | Zeigt den verbundenen Datenbanktyp (SQLite/PostgreSQL) |
| **Status** | Aktueller Status: `Verwenden` (Browse), `Suchen`, `Neuer Datensatz` |
| **Sortierung** | Zeigt an, ob Datensätze sortiert sind |
| **Datensatz Nr.** | Nummer des aktuellen Datensatzes |
| **Gesamt** | Gesamtzahl der Datensätze |

![Statusanzeigen](images/02_fundort_formular/10_indicatori_stato.png)
*Abbildung 10: Statusanzeigen*

### Datensatz-Navigation

| Schaltfläche | Symbol | Funktion | Tastenkürzel |
|--------------|--------|----------|--------------|
| **Erster Datensatz** | |< | Zum ersten Datensatz | - |
| **Vorheriger** | < | Zum vorherigen Datensatz | - |
| **Nächster** | > | Zum nächsten Datensatz | - |
| **Letzter Datensatz** | >| | Zum letzten Datensatz | - |

![Navigation](images/02_fundort_formular/11_navigazione_record.png)
*Abbildung 11: Navigationsschaltflächen*

### Datensatzverwaltung

| Schaltfläche | Funktion | Beschreibung |
|--------------|----------|-------------|
| **Neuer Datensatz** | Neu erstellen | Bereitet das Formular für einen neuen Fundort vor |
| **Speichern** | Speichern | Speichert Änderungen oder neuen Datensatz |
| **Datensatz löschen** | Löschen | Löscht aktuellen Datensatz (mit Bestätigung) |
| **Alle anzeigen** | Alle ansehen | Zeigt alle Datensätze in der Datenbank |

![Datensatzverwaltung](images/02_fundort_formular/12_gestione_record.png)
*Abbildung 12: Schaltflächen zur Datensatzverwaltung*

### Suche und Sortierung

| Schaltfläche | Funktion | Beschreibung |
|--------------|----------|-------------|
| **Neue Suche** | Neue Suche | Startet Suchmodus |
| **Suche!!!** | Suche ausführen | Führt Suche mit eingegebenen Kriterien aus |
| **Sortieren nach** | Sortieren | Öffnet Sortierungsbereich |

![Suche](images/02_fundort_formular/13_ricerca.png)
*Abbildung 13: Suchfunktionen*

#### So führen Sie eine Suche durch

1. Klicken Sie auf **Neue Suche** - Status ändert sich zu "Suchen"
2. Füllen Sie die Felder mit Suchkriterien aus
3. Klicken Sie auf **Suche!!!** zur Ausführung
4. Die Ergebnisse werden angezeigt und Sie können zwischen ihnen navigieren

![Suchbeispiel](images/02_fundort_formular/14_esempio_ricerca.png)
*Abbildung 14: Beispiel einer Suche nach Region*

> **Video-Tutorial**: [Link zum Suchvideo einfügen]

#### Sortierungsbereich

Durch Klicken auf **Sortieren nach** öffnet sich ein Bereich zum Sortieren der Datensätze:

![Sortierungsbereich](images/02_fundort_formular/15_pannello_ordinamento.png)
*Abbildung 15: Sortierungsbereich*

| Option | Beschreibung |
|--------|-------------|
| **Feld** | Wählt das Feld für die Sortierung |
| **Aufsteigend** | Reihenfolge A-Z, 0-9 |
| **Absteigend** | Reihenfolge Z-A, 9-0 |

---

## GIS-Funktionen

Das Fundort-Formular bietet verschiedene GIS-Integrationsfunktionen.

![GIS-Bereich](images/02_fundort_formular/16_sezione_gis.png)
*Abbildung 16: GIS-Funktionsbereich*

### Layer-Laden

| Schaltfläche | Funktion |
|--------------|----------|
| **GIS-Viewer** | Lädt alle Layer zum Einfügen von Geometrien |
| **Fundort-Layer laden** (Globus-Symbol) | Lädt nur die Layer des aktuellen Fundorts |
| **Alle Fundorte laden** (Mehrfach-Globus) | Lädt die Layer aller Fundorte |

![GIS-Schaltflächen](images/02_fundort_formular/17_bottoni_gis.png)
*Abbildung 17: Schaltflächen zum Laden von GIS-Layern*

### Geocoding - Adresssuche

Die Geocoding-Funktion ermöglicht die Lokalisierung einer Adresse auf der Karte.

![Geocoding](images/02_fundort_formular/18_geocoding.png)
*Abbildung 18: Adresssuchfeld*

1. Geben Sie die Adresse in das Textfeld ein
2. Klicken Sie auf **Zoom zu**
3. Die Karte zentriert sich auf die gefundene Position

| Feld | Beschreibung |
|------|-------------|
| **Adresse** | Straße, Stadt, Land eingeben |
| **Zoom zu** | Zentriert die Karte auf die Adresse |

### Aktiver GIS-Modus

Der Schalter **Suchergebnis-Laden aktivieren** aktiviert/deaktiviert die automatische Anzeige der Suchergebnisse auf der Karte.

![GIS-Schalter](images/02_fundort_formular/19_toggle_gis.png)
*Abbildung 19: GIS-Modus-Schalter*

- **Aktiv**: Suchen werden automatisch auf der Karte angezeigt
- **Inaktiv**: Suchen ändern die Kartenanzeige nicht

### WMS Archäologische Denkmäler

Die WMS-Schaltfläche lädt den Layer der archäologischen Denkmäler.

![WMS Denkmäler](images/02_fundort_formular/20_wms_vincoli.png)
*Abbildung 20: WMS archäologische Denkmäler-Layer*

### Basiskarten

Die Basiskarten-Schaltfläche ermöglicht das Laden von Grundkarten (Google Maps, OpenStreetMap, usw.).

![Basiskarten](images/02_fundort_formular/21_base_maps.png)
*Abbildung 21: Basiskarten-Auswahl*

---

## SE-Generierung

Diese Funktion ermöglicht das automatische Erstellen einer beliebigen Anzahl von SE-Formularen für den aktuellen Fundort.

![SE-Generator](images/02_fundort_formular/22_generatore_us.png)
*Abbildung 22: Bereich SE-Generierung*

### Parameter

| Feld | Beschreibung | Beispiel |
|------|-------------|----------|
| **Arealnummer** | Nummer des Ausgrabungsareals | 1 |
| **SE-Startnummer** | Anfangsnummer SE | 1 |
| **Anzahl zu erstellender Formulare** | Wie viele SE generieren | 100 |
| **Typ** | SE oder USM | SE |

### Verfahren

1. Stellen Sie sicher, dass Sie beim richtigen Fundort sind
2. Geben Sie die Arealnummer ein
3. Geben Sie die SE-Startnummer ein
4. Geben Sie ein, wie viele Formulare erstellt werden sollen
5. Wählen Sie den Typ (SE oder USM)
6. Klicken Sie auf **SE generieren**

![Generierungsbeispiel](images/02_fundort_formular/23_esempio_generazione.png)
*Abbildung 23: Beispiel Generierung von 50 SE ab SE 101*

> **Video-Tutorial**: [Link zum Video SE-Batch-Generierung einfügen]

---

## MoveCost - Weganalyse

Der Bereich **MovecostToPyarchinit** integriert R-Funktionen für die Least-Cost-Path-Analyse.

![MoveCost](images/02_fundort_formular/24_movecost_sezione.png)
*Abbildung 24: MoveCost-Bereich*

### Voraussetzungen

- **R** auf dem System installiert
- R-Paket **movecost** installiert
- **Processing R Provider** Plugin in QGIS aktiv

### Verfügbare Funktionen

| Funktion | Beschreibung |
|----------|-------------|
| **movecost** | Berechnet Bewegungskosten und kürzeste Wege von einem Ursprungspunkt |
| **movecost by polygon** | Wie oben, mit Polygon zum DTM-Download |
| **movebound** | Berechnet Grenzen der Wegkosten um Punkte |
| **movcorr** | Berechnet Least-Cost-Korridore zwischen Punkten |
| **movalloc** | Territoriale Zuordnung basierend auf Kosten |

![MoveCost-Beispiel](images/02_fundort_formular/25_esempio_movecost.png)
*Abbildung 25: Beispiel MoveCost-Analyseausgabe*

### Skripte hinzufügen

Die Schaltfläche **Skripte hinzufügen** installiert automatisch die erforderlichen R-Skripte im QGIS-Profil.

> **Video-Tutorial**: [Link zum MoveCost-Video einfügen]

---

## Berichtexport

### Grabungsbericht exportieren

Die Schaltfläche **Exportieren** generiert ein PDF mit dem Grabungsbericht für den aktuellen Fundort.

![Export](images/02_fundort_formular/26_esportazione.png)
*Abbildung 26: Schaltfläche Berichtexport*

**Hinweis**: Diese Funktion befindet sich in der Entwicklungsversion und kann Fehler enthalten.

Der Bericht enthält:
- Identifikationsdaten des Fundorts
- Liste der SE
- Stratigraphische Sequenz
- Harris-Matrix (falls verfügbar)

![PDF-Beispiel](images/02_fundort_formular/27_esempio_pdf.png)
*Abbildung 27: Beispiel eines generierten PDF-Berichts*

---

## Operativer Arbeitsablauf

### Neuen Fundort erstellen

> **Video-Tutorial**: [Link zum Video Workflow neuer Fundort einfügen]

#### Schritt 1: Fundort-Formular öffnen
![Workflow Schritt 1](images/02_fundort_formular/28_workflow_step1.png)
*Abbildung 28: Schritt 1 - Formular öffnen*

#### Schritt 2: "Neuer Datensatz" klicken
Der Status ändert sich zu "Neuer Datensatz" und die Felder werden geleert.

![Workflow Schritt 2](images/02_fundort_formular/29_workflow_step2.png)
*Abbildung 29: Schritt 2 - Neuer Datensatz*

#### Schritt 3: Pflichtdaten ausfüllen
Geben Sie mindestens den Namen des Fundorts ein (Pflichtfeld).

![Workflow Schritt 3](images/02_fundort_formular/30_workflow_step3.png)
*Abbildung 30: Schritt 3 - Daten ausfüllen*

#### Schritt 4: Geografische Daten ausfüllen
Land, Region, Landkreis, Gemeinde eingeben.

![Workflow Schritt 4](images/02_fundort_formular/31_workflow_step4.png)
*Abbildung 31: Schritt 4 - Geografische Daten*

#### Schritt 5: Definition auswählen
Fundorttyp aus Thesaurus wählen.

![Workflow Schritt 5](images/02_fundort_formular/32_workflow_step5.png)
*Abbildung 32: Schritt 5 - Fundortdefinition*

#### Schritt 6: Beschreibung hinzufügen
Beschreibungsfeld mit detaillierten Informationen ausfüllen.

![Workflow Schritt 6](images/02_fundort_formular/33_workflow_step6.png)
*Abbildung 33: Schritt 6 - Beschreibung*

#### Schritt 7: Speichern
Klicken Sie auf **Speichern**, um den neuen Fundort zu speichern.

![Workflow Schritt 7](images/02_fundort_formular/34_workflow_step7.png)
*Abbildung 34: Schritt 7 - Speichern*

#### Schritt 8: Überprüfen
Der Fundort wurde erstellt, der Status kehrt zu "Verwenden" zurück.

![Workflow Schritt 8](images/02_fundort_formular/35_workflow_step8.png)
*Abbildung 35: Schritt 8 - Erstellungsüberprüfung*

### Bestehenden Fundort ändern

1. Zum zu ändernden Fundort navigieren
2. Gewünschte Felder ändern
3. Klicken Sie auf **Speichern**
4. Speichern der Änderungen bestätigen

### Fundort löschen

**Achtung**: Das Löschen eines Fundorts löscht NICHT automatisch die zugehörigen SE, Strukturen und Funde.

1. Zum zu löschenden Fundort navigieren
2. Klicken Sie auf **Datensatz löschen**
3. Löschung bestätigen

![Löschbestätigung](images/02_fundort_formular/36_conferma_eliminazione.png)
*Abbildung 36: Dialog Löschbestätigung*

---

## Tab Hilfe

Der Tab Hilfe bietet schnellen Zugriff auf die Dokumentation.

![Tab Hilfe](images/02_fundort_formular/37_tab_help.png)
*Abbildung 37: Tab Hilfe*

| Ressource | Link |
|-----------|------|
| Video-Tutorial | YouTube |
| Dokumentation | pyarchinit.github.io |
| Community | Facebook UnaQuantum |

---

## Parallelitätsverwaltung (PostgreSQL)

Bei der Verwendung von PostgreSQL in einer Mehrbenutzerumgebung verwaltet das System automatisch Bearbeitungskonflikte:

- **Sperranzeige**: Zeigt, ob der Datensatz von einem anderen Benutzer bearbeitet wird
- **Versionskontrolle**: Erkennt gleichzeitige Änderungen
- **Konfliktlösung**: Ermöglicht die Auswahl, welche Version beibehalten werden soll

![Parallelität](images/02_fundort_formular/38_concorrenza.png)
*Abbildung 38: Anzeige für gesperrten Datensatz*

---

## Fehlerbehebung

### Fundort wird nicht gespeichert
- Überprüfen Sie, ob das Feld "Fundort" ausgefüllt ist
- Stellen Sie sicher, dass der Name nicht bereits in der Datenbank existiert

### GIS-Layer werden nicht geladen
- Überprüfen Sie die Datenbankverbindung
- Stellen Sie sicher, dass dem Fundort Geometrien zugeordnet sind

### Geocoding-Fehler
- Überprüfen Sie die Internetverbindung
- Kontrollieren Sie, ob die Adresse korrekt geschrieben ist

### MoveCost funktioniert nicht
- Überprüfen Sie, ob R installiert ist
- Stellen Sie sicher, dass das Plugin Processing R Provider aktiv ist
- Installieren Sie das movecost-Paket in R

---

## Technische Hinweise

- **Datenbanktabelle**: `site_table`
- **Datenbankfelder**: sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Zugehörige GIS-Layer**: PYSITO_POLYGON, PYSITO_POINT
- **Thesaurus**: tipologia_sigla = '1.1'

---

*PyArchInit-Dokumentation - Fundort-Formular*
*Version: 4.9.x*
*Letzte Aktualisierung: Januar 2026*
