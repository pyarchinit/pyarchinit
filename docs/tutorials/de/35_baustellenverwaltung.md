# PyArchInit - Baustellenverwaltung

## Inhaltsverzeichnis

1. [Einfuehrung](#einfuehrung)
2. [Zugriff auf das Modul](#zugriff-auf-das-modul)
3. [Baustellen-Dashboard](#baustellen-dashboard)
4. [Personalformular](#personalformular)
5. [Anwesenheitsformular](#anwesenheitsformular)
6. [Ausruestungsformular](#ausruestungsformular)
7. [Budgetformular](#budgetformular)
8. [Operativer Arbeitsablauf](#operativer-arbeitsablauf)
9. [Haeufig gestellte Fragen (FAQ)](#haeufig-gestellte-fragen-faq)
10. [Fehlerbehebung](#fehlerbehebung)
11. [Technische Hinweise](#technische-hinweise)

---

## Einfuehrung

Das Modul **Baustellenverwaltung** (it. *Gestione Cantiere*) erweitert PyArchInit um umfassende Funktionen zur Verwaltung logistischer und administrativer Aspekte archaeologischer Grabungen. Es ergaenzt die wissenschaftliche Dokumentation (Stratigraphische Einheiten, Strukturen, Funde) um die operative Projektsteuerung: Personalverwaltung, Anwesenheitserfassung, Ausruestungskontrolle, Budgetueberwachung und Massenberechnungen.

Das Modul besteht aus **fuenf eigenstaendigen Komponenten**, die ueber eine dedizierte Werkzeugleiste erreichbar sind:

| Komponente | Symbol | Beschreibung |
|------------|--------|-------------|
| **Baustellen-Dashboard** | Cantiere-Symbol | Zentrale Uebersicht mit Kennzahlen und Massenberechnungen |
| **Personal** | Personen-Symbol | Verwaltung der Mitarbeiter und ihrer Vertragsdaten |
| **Anwesenheit** | Kalender-Symbol | Tageserfassung von Arbeitszeiten und Abwesenheiten |
| **Ausruestung** | Werkzeug-Symbol | Geraeteinventar mit Wartungsplanung |
| **Budget** | Euro-Symbol | Kostenplanung und -verfolgung |

<!-- IMAGE: Uebersicht der fuenf Baustellenverwaltungsmodule -->
> **Abb. 1**: Die fuenf Komponenten der Baustellenverwaltung und ihre Zusammenhaenge

---

## Zugriff auf das Modul

### Ueber die Werkzeugleiste

Nach dem Laden des Plugins erscheint in QGIS eine dedizierte Werkzeugleiste **pyArchInit - Gestione Cantiere** mit fuenf Symbolen:

```
+---------------------------------------------------------------+
| [Dashboard] | [Personal] [Anwesenheit] | [Ausruestung] [Budget] |
+---------------------------------------------------------------+
```

1. **Dashboard-Symbol** (Baustellen-Dashboard) -- oeffnet die zentrale Uebersicht
2. **Personen-Symbol** (Personal) -- oeffnet das Personalformular
3. **Kalender-Symbol** (Anwesenheit) -- oeffnet das Anwesenheitsformular
4. **Werkzeug-Symbol** (Ausruestung) -- oeffnet das Ausruestungsformular
5. **Euro-Symbol** (Budget) -- oeffnet das Budgetformular

<!-- IMAGE: Baustellenverwaltung-Werkzeugleiste in QGIS -->
> **Abb. 2**: Die Baustellenverwaltung-Werkzeugleiste mit den fuenf Symbolen

### Ueber das Menue

Alternativ sind alle fuenf Formulare ueber das Menue erreichbar:

**PyArchInit** > **Archaeological GIS Tools** > **Dashboard Cantiere / Personal / Anwesenheit / Ausruestung / Budget**

---

## Baustellen-Dashboard

Das **Baustellen-Dashboard** ist das zentrale Cockpit des Moduls. Es bietet eine Echtzeit-Uebersicht ueber die wichtigsten Kennzahlen einer Grabungsbaustelle, ohne dass einzelne Formulare geoeffnet werden muessen.

<!-- IMAGE: Vollstaendiges Baustellen-Dashboard -->
> **Abb. 3**: Das Baustellen-Dashboard mit allen Zusammenfassungsbereichen

### Fundort- und Jahresauswahl

Im oberen Bereich des Dashboards befinden sich zwei Auswahlfelder:

| Steuerelement | Beschreibung |
|---------------|-------------|
| **Fundort** (comboBox_sito) | Waehlt den aktiven Fundort aus der Datenbank |
| **Jahr** (comboBox_anno) | Waehlt das Bezugsjahr (letzten 10 Jahre) |
| **Aktualisieren** | Laedt alle Kennzahlen fuer die aktuelle Auswahl neu |

Die Auswahl wird automatisch mit dem in der Konfiguration hinterlegten Fundort vorbelegt. Bei Aenderung des Fundorts oder Jahres aktualisiert sich das Dashboard automatisch.

### Budgetzusammenfassung

Zeigt eine Schnelluebersicht der finanziellen Situation:

| Anzeige | Beschreibung |
|---------|-------------|
| **Geplant** (label_budget_previsto) | Summe aller geplanten Betraege (importo_previsto) |
| **Ausgegeben** (label_budget_speso) | Summe aller tatsaechlichen Betraege (importo_effettivo) |
| **Fortschrittsbalken** (progressBar_budget) | Visueller Verbrauchsindikator (0-100%) |
| **Kreisdiagramm** (widget_chart) | Aufteilung der Ausgaben nach Kategorie |

<!-- IMAGE: Budgetbereich des Dashboards mit Fortschrittsbalken und Kreisdiagramm -->
> **Abb. 4**: Budgetzusammenfassung mit Fortschrittsbalken und Kreisdiagramm nach Kategorien

Das Kreisdiagramm wird mit **matplotlib** gerendert und zeigt die tatsaechlichen Ausgaben, gruppiert nach der Budgetkategorie. Die Prozentwerte beziehen sich auf den Anteil jeder Kategorie an den Gesamtausgaben.

### Personalzusammenfassung

Zeigt den aktuellen Personalstatus (basierend auf den Anwesenheitsdaten des heutigen Tages):

| Anzeige | Beschreibung |
|---------|-------------|
| **Anwesend** (label_presenti) | Mitarbeiter mit tipo_giornata = 'lavorativa' |
| **Urlaub** (label_ferie) | Mitarbeiter mit tipo_giornata = 'ferie' |
| **Krank** (label_malattia) | Mitarbeiter mit tipo_giornata = 'malattia' |
| **Monatsstunden** (label_ore_mese) | Summe ordinaere + Ueberstunden im laufenden Monat |
| **Monatskosten** (label_costo_mese) | Summe aller Tageskosten im laufenden Monat |

<!-- IMAGE: Personalbereich des Dashboards -->
> **Abb. 5**: Personalzusammenfassung mit Tagesstatus und Monatskennzahlen

### Ausruestungszusammenfassung

Zeigt den aktuellen Status des Geraeteinventars:

| Anzeige | Beschreibung |
|---------|-------------|
| **Gesamt** (label_totali) | Gesamtanzahl der registrierten Ausruestungsgegenstaende |
| **In Gebrauch** (label_in_uso) | Geraete mit stato = 'in_uso' |
| **Wartung** (label_manutenzione) | Geraete mit stato = 'manutenzione' |
| **Wartungsalarm** (label_alert_manutenzione) | Ueberfaellige Wartungstermine (rot hervorgehoben) |

Der Wartungsalarm erscheint in **roter Schrift**, wenn Geraete existieren, deren naechster Wartungstermin (data_prossima_manutenzione) ueberschritten ist und die sich nicht im Status 'fuori_uso' befinden.

<!-- IMAGE: Ausruestungsbereich mit Wartungsalarm -->
> **Abb. 6**: Ausruestungszusammenfassung mit aktivem Wartungsalarm (2 ueberfaellige Geraete)

### Massenberechnung (Computo Metrico)

Der untere Bereich des Dashboards bietet GIS-basierte Massenberechnungen fuer Aushubvolumen und Flaechen:

#### Berechnungsmethode 1: DEM-Differenz

Berechnet das Volumen aus der Differenz zweier Digitaler Gelaendemodelle (DEM vor und nach dem Aushub):

| Feld | Beschreibung |
|------|-------------|
| **DEM vorher** (comboBox_dem_pre) | Raster-Layer des DEM vor dem Eingriff |
| **DEM nachher** (comboBox_dem_post) | Raster-Layer des DEM nach dem Eingriff |

Die Berechnung nutzt den QGIS-Rasterrechner, um pixelweise die Hoehendifferenz zu bestimmen, und summiert die absoluten Volumina.

#### Berechnungsmethode 2: DEM + Polygon

Berechnet Flaecheninhalte und Volumen innerhalb eines definierten Polygons mithilfe von Zonalstatistiken:

| Feld | Beschreibung |
|------|-------------|
| **DEM** (comboBox_dem_pre) | Raster-Layer des DEM |
| **Polygon-Layer** (comboBox_layer_poligono) | Vektor-Layer mit der Berechnungsflaeche |

#### Ergebnisanzeige

| Anzeige | Beschreibung |
|---------|-------------|
| **Flaeche** (label_area_mq) | Berechnete Flaeche in m2 |
| **Volumen** (label_volume_mc) | Berechnetes Volumen in m3 |
| **Berechnen** | Startet die Berechnung mit der gewaehlten Methode |
| **Ergebnis speichern** | Speichert das Ergebnis in der Tabelle computo_metrico |

<!-- IMAGE: Massenberechnungsbereich mit DEM-Auswahl -->
> **Abb. 7**: Massenberechnungsbereich mit DEM-Differenz-Methode und Ergebnisanzeige

#### Berechnungsverlauf

Die Tabelle im unteren Bereich zeigt alle gespeicherten Berechnungsergebnisse:

| Spalte | Beschreibung |
|--------|-------------|
| **Datum** | Zeitpunkt der Berechnung |
| **Typ** | differenza_dem oder dem_poligono |
| **Flaeche (m2)** | Berechnete Flaeche |
| **Volumen (m3)** | Berechnetes Volumen |
| **Notizen** | Optionale Anmerkungen |

<!-- IMAGE: Berechnungsverlaufstabelle mit mehreren Eintraegen -->
> **Abb. 8**: Berechnungsverlaufstabelle mit gespeicherten Massenberechnungen

---

## Personalformular

Das **Personalformular** (Personale) verwaltet die Stammdaten aller Mitarbeiter einer Grabungsbaustelle.

### Benutzeroberflaeche

Das Formular folgt dem Standard-DBMS-Muster von PyArchInit mit Navigationsleiste, Suchfunktion und Datensatzverwaltung.

<!-- IMAGE: Personalformular mit ausgefuellten Feldern -->
> **Abb. 9**: Das Personalformular mit einer vollstaendigen Mitarbeiterakte

### DBMS-Toolbar

Die DBMS-Toolbar am oberen Rand bietet die Standard-Funktionen:

| Funktion | Beschreibung |
|----------|-------------|
| **Neuer Datensatz** | Erstellt einen leeren Personaldatensatz |
| **Speichern** | Speichert den aktuellen Datensatz |
| **Loeschen** | Entfernt den aktuellen Datensatz |
| **Suche starten / Suche ausfuehren** | Ermoeglicht die Suche nach beliebigen Feldern |
| **Navigation** | Blaettert zwischen Datensaetzen (Erster/Vorheriger/Naechster/Letzter) |
| **Alle anzeigen** | Zeigt alle Datensaetze |
| **Sortieren** | Sortiert nach gewaehltem Feld |

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Vorname** | nome | Text | Vorname des Mitarbeiters |
| **Nachname** | cognome | Text | Nachname des Mitarbeiters |
| **Rolle** | ruolo | Text | Funktion im Projekt (z.B. Grabungsleiter, Techniker) |
| **Qualifikation** | qualifica | Text | Berufliche Qualifikation (z.B. Archaeologe, Geometer) |
| **Steuernummer** | codice_fiscale | Text | Identifikationsnummer |
| **E-Mail** | email | Text | Kontakt-E-Mail |
| **Telefon** | telefono | Text | Telefonnummer |
| **Geburtsdatum** | data_nascita | Datum | Format: JJJJ-MM-TT |
| **Adresse** | indirizzo | Text | Wohnanschrift |
| **Vertragsart** | tipo_contratto | Text | Art des Vertrags (z.B. Festanstellung, freiberuflich) |
| **Vertragsbeginn** | data_inizio_contratto | Datum | Beginn des Arbeitsvertrags |
| **Vertragsende** | data_fine_contratto | Datum | Ende des Arbeitsvertrags |
| **Stundensatz** | tariffa_oraria | Dezimal | Verguetung pro Stunde (EUR) |
| **Tagessatz** | tariffa_giornaliera | Dezimal | Verguetung pro Tag (EUR) |
| **IBAN** | iban | Text | Bankverbindung |
| **Notizen** | note | Text | Freitext fuer zusaetzliche Informationen |
| **Aktiv** | attivo | Boolean | Ob der Mitarbeiter aktuell aktiv ist |

<!-- IMAGE: Personalformular-Felder im Detail -->
> **Abb. 10**: Detailansicht der Personalformularfelder mit Beispieldaten

---

## Anwesenheitsformular

Das **Anwesenheitsformular** (Presenze) erfasst die taegliche Arbeitszeit und Abwesenheiten des Personals.

### Benutzeroberflaeche

<!-- IMAGE: Anwesenheitsformular mit Tageseintrag -->
> **Abb. 11**: Das Anwesenheitsformular mit einem typischen Tageseintrag

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Personal-ID** | id_personale | Ganzzahl | Verweis auf den Personaldatensatz |
| **Datum** | data | Datum | Tag der Anwesenheit (JJJJ-MM-TT) |
| **Eintritt** | ora_ingresso | Zeit | Uhrzeit des Arbeitsbeginns |
| **Austritt** | ora_uscita | Zeit | Uhrzeit des Arbeitsendes |
| **Regulaere Stunden** | ore_ordinarie | Dezimal | Anzahl regulaerer Arbeitsstunden |
| **Ueberstunden** | ore_straordinario | Dezimal | Anzahl der Ueberstunden |
| **Tagestyp** | tipo_giornata | Auswahl | Art des Tages (siehe Tabelle unten) |
| **Schicht** | turno | Text | Bezeichnung der Schicht (z.B. Frueh, Spaet) |
| **Arbeitsbereich** | area_lavoro | Text | Grabungsareal oder Taetigkeitsbereich |
| **Notizen** | note | Text | Bemerkungen zum Tag |
| **Tageskosten** | costo_giornata | Dezimal | Berechnete Kosten fuer diesen Tag (EUR) |

### Tagestypen (tipo_giornata)

| Wert | Deutsche Bezeichnung | Beschreibung |
|------|---------------------|-------------|
| `lavorativa` | Arbeitstag | Normaler Arbeitstag |
| `ferie` | Urlaub | Geplanter Urlaubstag |
| `malattia` | Krankheit | Krankheitsbedingter Ausfall |
| `permesso` | Erlaubnis | Sonderurlaub / Freistellung |

<!-- IMAGE: Anwesenheitsformular mit Tagestyp-Auswahl -->
> **Abb. 12**: Auswahl des Tagestyps im Anwesenheitsformular

### Erfassung eines Arbeitstages

1. Auf **Neuer Datensatz** klicken
2. **Fundort** auswaehlen
3. **Personal-ID** des Mitarbeiters eingeben
4. **Datum** auswaehlen
5. **Eintritt** und **Austritt** eingeben
6. **Regulaere Stunden** und ggf. **Ueberstunden** eintragen
7. **Tagestyp** waehlen (z.B. lavorativa)
8. Optional: **Arbeitsbereich**, **Schicht** und **Notizen** ausfuellen
9. **Tageskosten** eintragen oder berechnen lassen
10. Auf **Speichern** klicken

<!-- IMAGE: Schritt-fuer-Schritt-Anwesenheitserfassung -->
> **Abb. 13**: Workflow zur Erfassung eines Arbeitstages

---

## Ausruestungsformular

Das **Ausruestungsformular** (Attrezzature) verwaltet das Inventar an Geraeten, Werkzeugen und Maschinen der Grabungsbaustelle, einschliesslich Wartungsplanung.

### Benutzeroberflaeche

<!-- IMAGE: Ausruestungsformular mit Geraeteeintrag -->
> **Abb. 14**: Das Ausruestungsformular mit einem typischen Geraeteeintrag

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Inventarnummer** | codice_inventario | Text | Eindeutige Inventarkennung |
| **Name** | nome | Text | Bezeichnung des Geraets |
| **Kategorie** | categoria | Text | Geraetekategorie (z.B. Vermessung, Aushub, Dokumentation) |
| **Marke** | marca | Text | Hersteller |
| **Modell** | modello | Text | Modellbezeichnung |
| **Seriennummer** | numero_serie | Text | Seriennummer des Geraets |
| **Eigentum** | proprieta | Text | Eigentuemer (z.B. Firma, Miete, Leasing) |
| **Kaufdatum** | data_acquisto | Datum | Datum der Anschaffung |
| **Kaufpreis** | costo_acquisto | Dezimal | Anschaffungskosten (EUR) |
| **Mietkosten/Tag** | costo_noleggio_giorno | Dezimal | Tagespreis bei Miete (EUR) |
| **Status** | stato | Auswahl | Aktueller Zustand (siehe Tabelle unten) |
| **Zugewiesen an** | assegnato_a | Text | Name des verantwortlichen Mitarbeiters |
| **Letzte Wartung** | data_ultima_manutenzione | Datum | Datum der letzten Wartung |
| **Naechste Wartung** | data_prossima_manutenzione | Datum | Geplantes Datum der naechsten Wartung |
| **Notizen** | note | Text | Zusaetzliche Informationen, Zustandsbeschreibung |

### Statuswerte (stato)

| Wert | Deutsche Bezeichnung | Beschreibung |
|------|---------------------|-------------|
| `in_uso` | In Gebrauch | Geraet ist aktiv im Einsatz |
| `manutenzione` | Wartung | Geraet befindet sich in Wartung oder Reparatur |
| `fuori_uso` | Ausser Betrieb | Geraet ist defekt oder ausgemustert |

<!-- IMAGE: Statusauswahl im Ausruestungsformular -->
> **Abb. 15**: Die drei Statusoptionen fuer Ausruestungsgegenstaende

### Wartungsplanung

Das System ueberwacht automatisch die Wartungstermine. Geraete, deren Feld **Naechste Wartung** (data_prossima_manutenzione) in der Vergangenheit liegt und die sich nicht im Status 'fuori_uso' befinden, werden im Dashboard als **ueberfaellig** markiert.

**Empfohlener Workflow**:
1. Bei Neuaufnahme eines Geraets das Datum der naechsten Wartung eintragen
2. Nach jeder Wartung: **Letzte Wartung** aktualisieren und neues Datum bei **Naechste Wartung** setzen
3. Dashboard regelmaessig auf Wartungsalarme pruefen

<!-- IMAGE: Wartungsfelder im Ausruestungsformular -->
> **Abb. 16**: Wartungsdatumsfelder mit hervorgehobenem ueberfaelligem Termin

---

## Budgetformular

Das **Budgetformular** (Budget) ermoeglicht die Planung und Verfolgung aller Kosten einer Grabungsbaustelle.

### Benutzeroberflaeche

<!-- IMAGE: Budgetformular mit Kosteneintrag -->
> **Abb. 17**: Das Budgetformular mit einem typischen Kosteneintrag

### Datenfelder

| Feld | DB-Spalte | Typ | Beschreibung |
|------|-----------|-----|-------------|
| **Fundort** | sito | Text | Zugeordneter Fundort (Pflichtfeld) |
| **Jahr** | anno | Ganzzahl | Bezugsjahr des Budgeteintrags |
| **Kategorie** | categoria | Text | Kostenkategorie (z.B. Personal, Material, Geraete, Logistik) |
| **Beschreibung** | descrizione | Text | Detaillierte Beschreibung des Budgetpostens |
| **Geplanter Betrag** | importo_previsto | Dezimal | Budgetierter Betrag (EUR) |
| **Tatsaechlicher Betrag** | importo_effettivo | Dezimal | Tatsaechlich ausgegebener Betrag (EUR) |
| **Erfassungsdatum** | data_registrazione | Datum | Datum der Budgeterfassung |
| **Ausgabedatum** | data_spesa | Datum | Datum der tatsaechlichen Ausgabe |
| **Lieferant** | fornitore | Text | Name des Lieferanten oder Dienstleisters |
| **Rechnungsnummer** | numero_fattura | Text | Referenznummer der Rechnung |
| **Notizen** | note | Text | Zusaetzliche Informationen |

<!-- IMAGE: Budgetformular-Felder im Detail -->
> **Abb. 18**: Detailansicht der Budgetfelder mit Beispiel einer Materialbestellung

### Budgetplanung vs. Kostenverfolgung

Das System unterscheidet zwischen zwei Nutzungsmodi:

**1. Budgetplanung (Voraus)**:
- **Geplanter Betrag** ausfuellen
- **Tatsaechlicher Betrag** leer lassen oder auf 0 setzen
- Dient als Kostenschaetzung vor Projektbeginn

**2. Kostenverfolgung (Laufend)**:
- **Tatsaechlicher Betrag** nach jeder Ausgabe aktualisieren
- **Ausgabedatum**, **Lieferant** und **Rechnungsnummer** eintragen
- Ermoeglicht Soll-Ist-Vergleich im Dashboard

---

## Operativer Arbeitsablauf

### Projekt einrichten

Ein typischer Arbeitsablauf fuer eine neue Grabungsbaustelle:

#### Schritt 1: Fundort anlegen

Zunaechst muss der Fundort im Fundort-Formular angelegt werden (siehe [Fundort-Formular Tutorial](02_fundort_formular.md)).

#### Schritt 2: Budget planen

```
1. Budgetformular oeffnen
2. Fundort auswaehlen
3. Jahr eintragen
4. Fuer jede Kostenkategorie einen Eintrag mit geplantem Betrag erstellen:
   - Personal (Loehne, Honorare)
   - Material (Verbrauchsmaterial, Werkzeug)
   - Geraete (Miete, Wartung)
   - Logistik (Transport, Unterkunft)
   - Dokumentation (Fotografie, Zeichnung)
5. Jeden Eintrag speichern
```

#### Schritt 3: Personal erfassen

```
1. Personalformular oeffnen
2. Jeden Mitarbeiter mit vollstaendigen Stammdaten anlegen
3. Vertragsdaten (Beginn, Ende, Tagessatz) eintragen
4. Datensaetze speichern
```

#### Schritt 4: Ausruestung registrieren

```
1. Ausruestungsformular oeffnen
2. Jedes Geraet mit Inventarnummer und Status registrieren
3. Wartungstermine eintragen
4. Datensaetze speichern
```

#### Schritt 5: Taeglicher Betrieb

```
1. Anwesenheitsformular oeffnen
2. Fuer jeden Mitarbeiter den Tageseintrag erstellen:
   - Anwesend: Tagestyp 'lavorativa', Stunden eintragen
   - Abwesend: Tagestyp 'ferie', 'malattia' oder 'permesso'
3. Datensaetze speichern
4. Dashboard pruefen fuer Tagesuebersicht
```

<!-- IMAGE: Schematischer Arbeitsablauf von Einrichtung bis taeglichem Betrieb -->
> **Abb. 19**: Schematischer Arbeitsablauf der Baustellenverwaltung

### Massenberechnung durchfuehren

```
1. Dashboard oeffnen
2. Fundort und Jahr auswaehlen
3. Berechnungsmethode waehlen:
   a) DEM-Differenz: Beide DEM-Layer auswaehlen
   b) DEM + Polygon: DEM und Polygon-Layer auswaehlen
4. Auf "Berechnen" klicken
5. Ergebnisse (Flaeche und Volumen) ablesen
6. Auf "Ergebnis speichern" klicken, um den Eintrag zu archivieren
7. Berechnungsverlauf in der Tabelle pruefen
```

<!-- IMAGE: Massenberechnung mit DEM-Differenz-Ergebnis -->
> **Abb. 20**: Ergebnis einer DEM-Differenz-Berechnung mit gespeichertem Verlaufseintrag

---

## Haeufig gestellte Fragen (FAQ)

### Wie werden die Tageskosten im Anwesenheitsformular berechnet?

Die Tageskosten (costo_giornata) koennen manuell eingetragen werden. Eine kuenftige Version wird die automatische Berechnung basierend auf dem Tagessatz des Mitarbeiters und den geleisteten Stunden unterstuetzen.

### Kann ich das Dashboard fuer mehrere Fundorte gleichzeitig anzeigen?

Nein, das Dashboard zeigt immer nur die Daten des aktuell ausgewaehlten Fundorts. Sie koennen jedoch schnell zwischen Fundorten wechseln, indem Sie den Fundort im Auswahlfeld aendern.

### Werden die Budgetdaten im Kreisdiagramm in Echtzeit aktualisiert?

Ja. Das Kreisdiagramm wird bei jeder Aktualisierung des Dashboards neu gerendert. Es zeigt die tatsaechlichen Ausgaben (importo_effettivo) gruppiert nach Kategorie. Wenn noch keine tatsaechlichen Ausgaben erfasst sind, bleibt das Diagramm leer.

### Wie funktioniert der Wartungsalarm?

Das System vergleicht bei jeder Dashboard-Aktualisierung das Datum im Feld "Naechste Wartung" (data_prossima_manutenzione) mit dem heutigen Datum. Liegt das Wartungsdatum in der Vergangenheit und der Geraetestatus ist nicht 'fuori_uso', erscheint ein roter Warnhinweis mit der Anzahl ueberfaelliger Geraete.

### Benoetige ich matplotlib fuer das Dashboard?

Das Kreisdiagramm im Budgetbereich benoetigt **matplotlib**. Wenn matplotlib nicht installiert ist, funktioniert das Dashboard weiterhin -- nur das Diagramm wird nicht angezeigt. Alle numerischen Zusammenfassungen bleiben verfuegbar.

### Welche DEM-Formate werden fuer die Massenberechnung unterstuetzt?

Alle Rasterformate, die von QGIS unterstuetzt werden (GeoTIFF, ASC, IMG, usw.). Die DEM-Layer muessen bereits in das aktuelle QGIS-Projekt geladen sein, um in den Auswahlfeldern zu erscheinen.

---

## Fehlerbehebung

### Dashboard zeigt keine Daten an

**Symptom**: Alle Kennzahlen zeigen 0 oder sind leer.

**Loesungen**:
1. Pruefen, ob die Datenbankverbindung aktiv ist (DB Info in der Statusleiste)
2. Sicherstellen, dass ein Fundort im Auswahlfeld gewaehlt ist
3. Pruefen, ob fuer den gewaehlten Fundort und das Jahr tatsaechlich Daten erfasst wurden
4. Auf **Aktualisieren** klicken

### Massenberechnung schlaegt fehl

**Symptom**: Fehlermeldung bei Klick auf "Berechnen".

**Loesungen**:
1. Sicherstellen, dass die DEM-Layer im QGIS-Projekt geladen sind
2. Bei DEM-Differenz: Pruefen, ob beide DEMs die gleiche Aufloesung und Ausdehnung haben
3. Bei DEM + Polygon: Pruefen, ob DEM und Polygon dasselbe Koordinatenreferenzsystem haben
4. Sicherstellen, dass die Layer-Auswahlfelder nicht leer sind

### Personalformular speichert nicht

**Symptom**: Fehlermeldung beim Speichern eines neuen Personaldatensatzes.

**Loesungen**:
1. Pruefen, ob der Fundort (sito) ausgefuellt ist
2. Sicherstellen, dass ein gueltiges Einstellungsdatum im Format JJJJ-MM-TT eingegeben wurde
3. Datenbankverbindung ueberpruefen

### Kreisdiagramm wird nicht angezeigt

**Symptom**: Der Diagrammbereich im Dashboard bleibt leer.

**Loesungen**:
1. Pruefen, ob matplotlib installiert ist: `pip install matplotlib`
2. Sicherstellen, dass tatsaechliche Ausgaben (importo_effettivo) erfasst sind
3. QGIS neu starten, falls matplotlib nachtraeglich installiert wurde

---

## Technische Hinweise

### Quelldateien

| Datei | Beschreibung |
|-------|-------------|
| `tabs/Cantiere.py` | Dashboard-Controller |
| `tabs/Personale.py` | Personal-Controller |
| `tabs/Presenze.py` | Anwesenheits-Controller |
| `tabs/Attrezzature.py` | Ausruestungs-Controller |
| `tabs/Budget.py` | Budget-Controller |
| `gui/ui/Cantiere.ui` | Dashboard-Oberflaeche (Qt Designer) |
| `gui/ui/Personale.ui` | Personal-Oberflaeche |
| `gui/ui/Presenze.ui` | Anwesenheits-Oberflaeche |
| `gui/ui/Attrezzature.ui` | Ausruestungs-Oberflaeche |
| `gui/ui/Budget.ui` | Budget-Oberflaeche |
| `modules/db/entities/PERSONALE.py` | Personal-Entity-Klasse |
| `modules/db/entities/PRESENZE.py` | Anwesenheits-Entity-Klasse |
| `modules/db/entities/ATTREZZATURE.py` | Ausruestungs-Entity-Klasse |
| `modules/db/entities/BUDGET.py` | Budget-Entity-Klasse |

### Datenbanktabellen

| Tabelle | Beschreibung |
|---------|-------------|
| `personale_table` | Mitarbeiterstammdaten |
| `presenze_table` | Tagesanwesenheiten |
| `attrezzature_table` | Geraeteinventar |
| `budget_table` | Budgetplanung und -verfolgung |
| `computo_metrico_table` | Massenberechnungsergebnisse |

### Werkzeugleisten-Symbole

| Symbol | Datei | Aktion |
|--------|-------|--------|
| Cantiere | `resources/icons/iconCantiere.png` | runCantiere() |
| Personale | `resources/icons/iconPersonale.png` | runPersonale() |
| Presenze | `resources/icons/iconPresenze.png` | runPresenze() |
| Attrezzature | `resources/icons/iconAttrezzature.png` | runAttrezzature() |
| Budget | `resources/icons/iconBudget.png` | runBudget() |

### Kompatibilitaet

| Komponente | Mindestversion |
|------------|---------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| Python | 3.9+ |
| matplotlib | 3.0+ (optional, fuer Diagramme) |

---

*PyArchInit-Dokumentation - Baustellenverwaltung*
*Version: 5.0.x*
*Letzte Aktualisierung: Februar 2026*
