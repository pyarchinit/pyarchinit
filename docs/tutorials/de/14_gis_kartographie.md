# Tutorial 14: GIS und Kartographie

## Einführung

PyArchInit ist tief in **QGIS** integriert und nutzt dessen vollständige GIS-Funktionalitäten für die räumliche Verwaltung archäologischer Daten. Dieses Tutorial behandelt die kartographische Integration, vordefinierte Layer und erweiterte Funktionen wie die **automatische SAM-Segmentierung**.

### Haupt-GIS-Funktionen

- SE-Visualisierung auf Karte
- Vordefinierte Vektorlayer
- Benutzerdefiniertes QML-Styling
- GIS-Höhen und Messungen
- Automatische Segmentierung (SAM)
- Kartographischer Export

## Vordefinierte PyArchInit-Layer

### Hauptvektorlayer

| Layer | Geometrie | Beschreibung |
|-------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | Ablagerungs-SE |
| `pyunitastratigrafiche_usm` | MultiPolygon | Mauerwerks-SE |
| `pyarchinit_quote` | Point | Höhenpunkte |
| `pyarchinit_siti` | Point | Fundortlokalisierung |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Grabungsareale |
| `pyarchinit_strutture_ipotesi` | Polygon | Hypothetische Strukturen |
| `pyarchinit_documentazione` | Point | Dokumentationsverweise |

### SE-Layer-Attribute

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `gid` | Integer | Eindeutige ID |
| `scavo_s` | Text | Fundortname |
| `area_s` | Text | Arealnummer |
| `us_s` | Text | SE-Nummer |
| `stratigraph_index_us` | Integer | Stratigraphischer Index |
| `tipo_us_s` | Text | SE-Typ |
| `rilievo_originale` | Text | Ursprungsvermessung |
| `disegnatore` | Text | Vermessungsautor |
| `data` | Date | Vermessungsdatum |

## SE-Visualisierung auf Karte

### Vom Tab "Karte" im SE-Formular

1. Ein SE-Formular öffnen
2. Tab **Karte** auswählen
3. Verfügbare Funktionen:

| Schaltfläche | Funktion |
|--------------|----------|
| SE anzeigen | Aktuelle SE auf Karte anzeigen |
| Alle anzeigen | Alle SE des Areals anzeigen |
| Neuer Datensatz | Neue Geometrie erstellen |
| Schwenken zu | Karte auf SE zentrieren |

### Visualisierung aus Suche

1. SE-Suche durchführen
2. Schaltfläche **"Datensatz anzeigen"** → zeigt einzelne an
3. Schaltfläche **"Alle anzeigen"** → zeigt alle Ergebnisse an

### Stilauswahl (SE und USM)

Seit **5.13.112-alpha** erscheint das unten beschriebene Fenster **Style Choice** **nur, wenn für die Ansicht kein Standardstil gespeichert ist**: Mit einem Standardstil (für den Fundort oder für alle Fundorte) lädt das Formular die Ansicht, wendet ihn an und fragt nichts. Standardstile werden im Fenster **View styles** angelegt (siehe den Abschnitt «Stile der Ansichten» weiter unten).

Werden die SE oder die Mauerwerks-SE (USM) der Suchergebnisse auf die Karte geladen, erscheint das Fenster **Style Choice** ("How do you want to manage the layer style?"). Die Schaltflächen erscheinen auf Englisch:

| Schaltfläche | Wirkung |
|--------------|---------|
| **Save new style** | Erstellt den Stil anhand des gewählten Feldes und speichert ihn unter einem Namen in der Datenbank |
| **Load existing style** | Verwendet einen fertigen Stil, der aus einer Liste gewählt wird (siehe unten), als Vorlage und erstellt den Stil anhand des gewählten Feldes, ohne ihn in der Datenbank zu speichern |
| **Use temporary style** | Erstellt den Stil anhand des gewählten Feldes, ohne ihn in der Datenbank zu speichern |
| **Single symbol (outline only)** | Zeichnet nur die Umrisse der Geometrien, ohne Füllung |

Seit 5.13.19-alpha öffnet **Load existing style** das Fenster **Existing style** ("Choose the style to use as a template:", auf Englisch) mit der Liste der verfügbaren Stile: die in der Datenbank gespeicherten Stile (*Database: Name*), die mit pyArchInit gelieferten QML-Stile (`us_*.qml`, aufgeführt als *pyArchInit: …*) und **Other QML file…**, um eine beliebige `.qml`-Datei auszuwählen. Der gewählte Stil wird in den Layer geladen (Transparenz und Mischmodus kommen mit, die Beschriftungen nicht: Auf den Polygon-Ansichten von SE und USM sind es seit 5.13.110-alpha die des Absatzes **Beschriftungen** weiter unten, die eingekreiste Nummer der Einheit, was auch immer der Vorlagenstil vorgibt) und dient als **Vorlage**: Nach der Wahl des Kategorisierungsfeldes behalten die Werte, die der Stil bereits enthält, seine Farbe und sein Symbol; die übrigen erhalten eine Kopie seines Symbols mit einer eigenen Farbe. Wird die Auswahl abgebrochen, funktioniert es wie **Use temporary style**. Vorher wurde nur unter den Stilen der Datenbank gesucht und, wenn keiner vorhanden war, direkt das Kategorisierungsfenster geöffnet.

Bei **Save new style**, **Load existing style** und **Use temporary style** wird anschließend das Kategorisierungsfeld gewählt (Fenster **Kategorisierungsfeld auswählen**): **Stratigraphische Definition**, **SE Typ**, **Interpretative Definition** oder **Periode/Phase (cont_per)** (seit 5.13.19-alpha) und, seit 5.13.116-alpha, **SE-Nummer** (eine Kategorie je Einheit, in der Legende «US 12»), nur ein Eintrag je Einheit, gleich welchen SE-Typs; jeder Wert des Feldes erhält eine eigene Farbe, die seit 5.13.19-alpha bei jedem Laden des Layers gleich bleibt. Bei **Periode/Phase (cont_per)** zeigt der Legendeneintrag jedes Codes auch die Datierung der Periode/Phase aus der Periodisierung. Es werden nur die im Layer vorhandenen Felder angeboten.

**Zeichenreihenfolge.** Seit 5.13.19-alpha werden die Einheiten in der Reihenfolge gezeichnet, die der Time Manager verwendet, wie in der Matrix: zuerst die Einheiten ohne Periode, dann nach der Chronologie der Periode (aus der Periodisierung der Anfangsperiode/-phase der SE oder aus `cont_per`), dann nach `order_layer` (0 = älteste), sodass die jüngsten Einheiten oben liegen; innerhalb derselben Einheit (seit 5.13.117-alpha) liegen die Zeichnungen mit stratigraphischem Index 2, der Schicht, und die ohne Index unten, die mit Index 1, dem Objekt, oben. Das gilt für alle Stiloptionen, auch für **Single symbol (outline only)**. Werden die Layer Periode für Periode geladen, wird der Stil nur einmal abgefragt und für alle Perioden verwendet. Seit 5.13.114-alpha ist auch die **Legende** des Layers im QGIS-Layer-Bedienfeld wie die Matrix geordnet, vom Jüngsten zum Ältesten — bei den Kategorien nach Periode das Anfangsjahr aus der Periodisierung, dann `order_layer`, beide absteigend; die Einträge ohne `order_layer` am Ende — und bei Gleichstand das Objekt (Index 1) über der Schicht (Index 2), sodass sichtbar wird, was darunter liegt, wenn man die Häkchen der Einträge von oben her entfernt.

**Beschriftungen.** Seit 5.13.110-alpha erhält die SE-Ansicht (und die USM-Ansicht) mit dem gewählten Stil auch ihre **Beschriftungen**: die Nummer der Einheit in **Fettschrift in einem weißen Kreis mit dunkelrotem Rand**, **eine je Einheit**, auf ihrer größten Zeichnung, sofern diese sichtbar ist (nicht vollständig von einer Zeichnung höherer Ebene bedeckt), nach demselben Rezept wie die Atlasblätter des Time Managers (Tutorial 25). Würden sich zwei Nummern überdecken, wird eine verschoben und eine Hilfslinie verbindet sie mit ihrer Zeichnung. Das gilt für SE und USM, mit SQLite und mit PostgreSQL, und für alle Stiloptionen, auch für **Single symbol (outline only)**; hatte der mit **Load existing style** geladene Stil schon Beschriftungen, nimmt die eingekreiste Nummer deren Platz ein. Punkt-Layer erhalten die eingekreiste Nummer nicht. Seit 5.13.111-alpha trägt dagegen die **Höhenansicht** (die Höhenpunkte, Layer «Hoch view») unmittelbar nach dem Laden aus dem SE-Formular die **Beschriftung mit dem Höhenwert** (zwei Nachkommastellen, zum Beispiel «12,35»), platziert **über der waagerechten Linie des Symbols**, nach demselben Rezept wie die Atlasblätter des Time Managers. Das gilt für alle Befehle, die sie laden, mit SQLite und mit PostgreSQL, und hängt nicht vom gewählten Stil ab; Layer, die keine Punkte sind oder das Höhenfeld nicht haben, erhalten diese Beschriftung nicht. Seit 5.13.112-alpha sind die eingekreiste Nummer und der Höhenwert die **Ausgangs-Voreinstellungen** der Beschriftungen: Im Tab **Beschriftungen** (*Labels*) des Fensters **View styles** (siehe den gleichnamigen Abschnitt weiter unten) lassen sie sich ändern und als Standardstil speichern, der beim Laden ihren Platz einnimmt. pyArchInit schreibt nie Beschriftungen in Hektar: Sieht man welche («0,00 ha»), stammen sie von einem anderen Layer des Projekts oder von den Anmerkungen, und seit 5.13.116-alpha nennt die QGIS-Meldungsleiste beim Laden der Ansicht den Layer, der sie trägt, und den verwendeten Ausdruck, sodass man sie in den Eigenschaften dieses Layers ausschalten kann. Heißen die Layer «pyarchinit_us_view», sind es die des Tabs **Map preview** des SE-Formulars, die im Projekt außerhalb des Layer-Bedienfelds registriert sind (bis 5.13.116-alpha blieben sie dort bei jedem Öffnen): Seit 5.13.117-alpha entfernt pyArchInit sie beim nächsten Öffnen der Map preview von selbst.

Seit 5.13.18-alpha wird der gewählte Stil (und das Kategorisierungsfeld) auch bei SQLite-Datenbanken berücksichtigt, sowohl für die SE als auch für die USM; vorher erschien die Karte immer mit einer Farbe pro SE.

## Stile der Ansichten

Seit Version **5.13.112-alpha** dient ein einziges Fenster, **View styles** (Stile der Ansichten), dazu, den Stil — **Symbologie und Beschriftungen** — jeder pyArchInit-Ansicht zusammenzustellen: die Ansichten der SE und der USM, die Höhen, die Dokumentation, die Strukturen und Gräber, die UT, die Fundorte, die Funde, die Schnitte. Der Stil ist sofort in einer **Vorschau** mit den Daten des Fundorts zu sehen, wird unter einem Namen in der Datenbank gespeichert und kann für einen Fundort oder für alle zum **Standard** gemacht werden: Von da an wenden die Formulare, die die Ansicht laden, ihn von selbst an, ohne etwas zu fragen.

<!-- IMMAGINE: Screenshot des Fensters «View styles»: links die Liste der Ansichten und der gespeicherten Stile mit ihren Schaltflächen; rechts die Vorschau und die Tabs Symbology und Labels; unten Apply to loaded layers, Save, Save as… und Close -->
![Das Fenster View styles](images/14_gis_kartographie/01_stili_delle_viste.png)
*Abbildung 1: Das Fenster «View styles»*

Die Texte des Fensters gibt es nur auf Italienisch und Englisch: Bei deutschsprachigem QGIS erscheint es auf Englisch. Im Folgenden steht nach jeder übersetzten Beschriftung die englische in Klammern. Dasselbe gilt für den Menüeintrag: Bei deutschsprachigem QGIS heißt er «View styles…».

### Wo man es öffnet

Das Fenster ist nicht modal: Es bleibt offen, während man auf der Karte arbeitet. Es lässt sich auf vier Wegen öffnen.

- **Aus der pyArchInit-Werkzeugleiste** (seit 5.13.113-alpha): die **vierte Schaltfläche**, mit dem Symbol der Farbpalette, gleich nach der von GPT («AI Query Database»). Ist der aktive Layer eine pyArchInit-Ansicht, öffnet sich das Fenster gleich auf dieser Ansicht, sonst auf der SE-Ansicht.
- **Aus dem Plugin-Menü**: **Plugins → pyArchInit - Archaeological GIS Tools → View styles…** (Stile der Ansichten; bei italienischem QGIS heißt der Eintrag «Stili delle viste…»). Ist der aktive Layer eine pyArchInit-Ansicht, öffnet sich das Fenster gleich auf dieser Ansicht, sonst auf der SE-Ansicht.
- **Aus dem Layer-Menü**: Rechtsklick auf einen Vektor-Layer im QGIS-Layer-Bedienfeld → **View styles…**. Es ist derselbe Eintrag mit demselben Namen und derselben Regel: Ist der Layer eine pyArchInit-Ansicht, öffnet sich das Fenster gleich auf ihr.
- **Aus dem SE-Formular**: die Schaltfläche **Style…** (bei italienischem QGIS **Stile…**), neben der Schaltfläche, die die Layer lädt. Sie öffnet das Fenster auf der SE-Ansicht, mit dem Fundort des Formulars.

Die Vorschau zeigt die Geometrien eines **Fundorts**: den des Formulars, wenn das Fenster über die Schaltfläche «Style…» geöffnet wird, sonst den **aktiven Fundort** aus der pyArchInit-Konfiguration (Tutorial 01). Ohne aktiven Fundort zeigt sie alle Fundorte.

### Die Ansichten und die gespeicherten Stile

Die linke Spalte enthält zwei Listen.

**Ansichten** (*Views*). Die pyArchInit-Ansichten, nach Gruppen:

| Gruppe | Ansichten |
|--------|-----------|
| «Stratigraphische Einheiten» (*Stratigraphic units*) | SE, USM, negative SE |
| «Höhen» (*Elevations*) | Höhen der SE, Höhen der USM |
| «Dokumentation» (*Documentation*) | Dokumentation (zwei Ansichten) |
| «Strukturen und Gräber» (*Structures and burials*) | Strukturen, Gräber, Individuen |
| «Topographische Einheiten» (*Topographic units*) | UT als Punkte, Linien, Polygone |
| «Fundorte» (*Sites*) | punktförmige Fundorte, flächige Fundorte |
| «Funde» (*Finds*) | Funde |
| «Schnitte» (*Sections*) | Grabungsschnitte |

Auch die Ansichten, die bisher ohne Stil geladen wurden (Dokumentation, Strukturen und Gräber, UT, Fundorte, Funde, Schnitte), haben hier einen. Eine Ansicht, die nicht in der Datenbank ist, wird **grau**, sobald man sie wählt, und die Statuszeile sagt «Ansicht in dieser Datenbank nicht vorhanden» (*View not present in this database.*).

**Gespeicherte Stile** (*Saved styles*). Darunter die für die gewählte Ansicht gespeicherten Stile, einer pro Zeile: *Name · Fundort (oder «alle Fundorte») · «✓ Standard»* (*all sites*, *✓ default*). Ein Klick auf einen Stil lädt ihn in die Vorschau und in die Tabs, zum Ansehen oder Nachbessern. Die Stile, die QGIS für diesen Layer in der Datenbank gespeichert hat, erscheinen als *Name · Mit QGIS gespeichert* (*Saved with QGIS*): Sie lassen sich laden, werden von pyArchInit aber nicht neu geschrieben; um eine Kopie unter den eigenen Stilen zu behalten, verwendet man **Speichern unter…** (*Save as…*). Die Schaltflächen unter der Liste:

| Schaltfläche | Was sie tut |
|--------------|-------------|
| **Neu** (*New*) | Beginnt mit einem Stil, der noch zusammenzustellen ist: nur Umriss, mit den Ausgangsbeschriftungen der Ansicht. Der Name wird beim ersten **Speichern** (*Save*) abgefragt |
| **Duplizieren** (*Duplicate*) | Kopiert den gewählten Stil unter dem Namen «… (2)»; die Kopie ist kein Standard |
| **Umbenennen…** (*Rename…*) | Ändert den Namen des gewählten Stils |
| **Löschen** (*Delete*) | Löscht den gewählten Stil nach einer Bestätigung |
| **Standard für diesen Fundort** (*Default for this site*) | Der gewählte Stil wird der, der beim Laden der Ansicht für den aktuellen Fundort angewendet wird (ist der Stil einer für «alle Fundorte», legt das Fenster davon eine Kopie für den aktuellen Fundort an und macht die Kopie zum Standard; das Original bleibt, wie es ist) |
| **Standard für alle Fundorte** (*Default for all sites*) | Er wird der, der auf die Fundorte angewendet wird, die keinen eigenen haben (gehört der Stil zu einem Fundort, legt das Fenster davon eine Kopie für alle Fundorte an und macht die Kopie zum Standard; das Original bleibt, wie es ist) |
| **QML exportieren…** (*Export QML…*), **QML importieren…** (*Import QML…*) | Siehe «Exportieren und Importieren» |

Für jede Ansicht gibt es nur einen Standardstil je Fundort und nur einen für alle Fundorte: Wird ein anderer Stil zum Standard, verliert der vorherige die Markierung «✓ Standard». Duplizieren, Umbenennen, Löschen und die beiden «Standard» wirken auf den in der Liste gewählten Stil; ist keiner gewählt, erscheint der Hinweis «Wählen Sie zuerst einen gespeicherten Stil» (*Choose a saved style first.*).

### Vorschau, Symbologie und Beschriftungen

**Vorschau.** Oben rechts zeigt eine Karte die gewählte Ansicht, aus der Datenbank gelesen und auf den aktuellen Fundort gefiltert: Jede Änderung am Stil ist sofort zu sehen. **Auf Daten zoomen** (*Zoom to data*) bringt die Karte auf alle Geometrien. Die Statuszeile unter der Karte sagt, wie viele es sind (*482 Geometrien des Fundorts „Scavo 2026“.*, *482 geometries of site “Scavo 2026”.*) oder, wenn der Fundort in dieser Ansicht keine hat, «Keine Geometrie für den aktuellen Fundort» (*No geometry for the current site.*): Der Stil lässt sich trotzdem zusammenstellen. Die Vorschau ist ein eigener Layer, **nicht zum Projekt hinzugefügt**: Die Layer des QGIS-Projekts ändern sich nicht, bis man **Auf geladene Layer anwenden** (*Apply to loaded layers*) drückt. Wenn eine Ansicht gewählt wird, geht die Vorschau von dem aus, was pyArchInit ihr in diesem Moment beim Laden anwenden würde (siehe «Standardstile und Laden»).

Unter der Karte gibt es zwei Tabs: **Symbologie** (*Symbology*) und **Beschriftungen** (*Labels*).

**Tab Symbologie.** Oben die Auswahlliste **Voreinstellung** (*Preset:*):

| Voreinstellung | Wirkung |
|----------------|---------|
| «— unverändert lassen —» (*— keep as is —*) | Ändert nichts |
| «Nur Umriss» (*Outline only*) | Polygone ohne Füllung und mit dunkelgrauem Rand, dünne Linien, Punkte als leere Kreise |
| «Mit pyArchInit gelieferter Stil» (*Style shipped with pyArchInit*) | Das QML, das dem Plugin beiliegt: Es gibt es für die Ansichten SE und USM und für die Höhen |
| «Kategorien nach „Feld“» (*Categories by “field”*) | Eine Kategorie mit eigener Farbe für jeden Wert des Feldes. Es gibt einen Eintrag für jedes der für diese Ansicht sinnvollen Felder, die der Layer besitzt: für die Einheiten `d_stratigrafica`, `tipo_us_s`, `d_interpretativa`, `cont_per` und `us` (eine Kategorie je Einheit); für die anderen Ansichten zum Beispiel `tipo_doc`, `tipologia_struttura` oder `tipo_reperto` |

Unter der Liste steht der **Symbologie-Editor von QGIS**, derselbe wie in den Layer-Eigenschaften (einzelnes Symbol, kategorisiert, abgestuft, regelbasiert…): Die Voreinstellung ist der Ausgangspunkt, und von dort aus lässt sich alles nachbessern; jede Änderung ist sofort in der Vorschau zu sehen.

**Tab Beschriftungen.**

| Steuerelement | Was es tut |
|---------------|------------|
| **Beschriftungen aktiv** (*Labels on*) | Schaltet die Beschriftungen der Ansicht ein und aus |
| **Was geschrieben wird** (*What to write:*) | «Keine Beschriftung» (*No label*); «Nummer der Einheit in einem Kreis» (*Unit number in a circle*: die Nummer in Fettschrift in einem weißen Kreis mit dunkelrotem Rand, wie auf den Atlasblättern des Time Managers, Tutorial 25); «Höhe über dem Symbol» (*Elevation above the symbol*: der Höhenwert über der waagerechten Linie des Symbols); «Ein Feld oder ein Ausdruck» (*A field or an expression*) |
| **Feld** (*Field:*), **Ausdruck** (*Expression:*) | Für den letzten Eintrag: das zu schreibende Feld der Ansicht oder ein QGIS-Ausdruck (ist einer eingetragen, hat er Vorrang vor dem Feld) |
| **Position** (*Placement:*), **Versatz (mm)** (*Offset (mm):*) | Für den letzten Eintrag: «Zentriert» (*Centred*), «Um den Punkt» (*Around the point*) oder «Über dem Symbol» (*Above the symbol*); der Versatz hebt die Beschriftung um so viele Millimeter an und gilt für «Über dem Symbol» |
| **Eine Beschriftung pro Einheit (auf der größten sichtbaren Zeichnung)** (*One label per unit (on the largest visible drawing)*) | Für die Nummer der Einheit: eine einzige Beschriftung pro Einheit, auf ihrer größten Zeichnung, die zu sehen ist (nicht vollständig von einer höheren Ebene bedeckt); ausgeschaltet, hat jede Zeichnung ihre eigene |
| **Schrift und Hintergrund** (*Font and background*) | Schriftart, **Größe (mm)** (*Size (mm):*), **Fett** (*Bold*), **Farbe…** (*Colour…*) des Textes, **Weißer Puffer** (*White buffer*), **Kreisförmiger Hintergrund** (*Circle background*) mit **Füllung…** (*Fill…*) und **Umrandung…** (*Stroke…*) |

Die Nummer der Einheit in einem Kreis ist die Ausgangs-Voreinstellung der Ansichten SE und USM, die Höhe über dem Symbol die der Höhenansichten: Es sind die Beschriftungen des Absatzes **Beschriftungen** in «Stilauswahl (SE und USM)» (oben), die hier geändert werden können. Die anderen Ansichten haben anfangs keine Beschriftungen. Das Bedienfeld ist das von pyArchInit, einfacher als der Beschriftungs-Editor von QGIS (regelbasiert und so weiter), der sich nur in den Layer-Eigenschaften öffnen lässt.

### Standardstile und Laden

Unten gibt es vier Schaltflächen:

| Schaltfläche | Was sie tut |
|--------------|-------------|
| **Auf geladene Layer anwenden** (*Apply to loaded layers*) | Wendet den in der Vorschau sichtbaren Stil — Symbologie und Beschriftungen — auf die Layer des QGIS-Projekts an, die aus dieser Ansicht stammen; die Statuszeile sagt «Stil auf N Projekt-Layer angewendet» (*Style applied to N project layers.*) oder «Kein Layer dieser Ansicht im Projekt» (*No layer of this view in the project.*). Es wird nichts in der Datenbank gespeichert |
| **Speichern** (*Save*) | Speichert auf den aktuellen Stil (den in der Liste gewählten); ist keiner da, fragt es nach dem Namen und legt einen neuen Stil an |
| **Speichern unter…** (*Save as…*) | Fragt nach dem Namen und speichert einen neuen Stil, für alle Fundorte: «Stil „Name“ gespeichert» (*Style “name” saved.*) |
| **Schließen** (*Close*) | Schließt das Fenster |

Damit ein Stil bei jedem Laden zu sehen ist: (1) die Ansicht wählen; (2) Symbologie und Beschriftungen zusammenstellen und dabei die Vorschau beobachten; (3) **Speichern unter…** mit einem Namen; (4) **Standard für diesen Fundort** oder **Standard für alle Fundorte**; (5) wenn die Layer schon im Projekt sind, **Auf geladene Layer anwenden**.

**Beim Laden gilt der Standardstil.** Wenn ein pyArchInit-Formular (zum Beispiel das SE-Formular) eine Ansicht lädt, wendet es der Reihe nach an:

1. den **Standardstil des Fundorts, für den die Ansicht geladen wird** (falls vorhanden): Das SE-Formular übergibt den Fundort des Formulars, die Lader nach Perioden (Time Manager) den Fundort, den sie gerade zeichnen; wo der Lader den Fundort nicht kennt, gilt der aktive Fundort der pyArchInit-Konfiguration (Tutorial 01);
2. sonst den **Standardstil für alle Fundorte**;
3. sonst, für die Ansichten SE, USM und Höhen, den mit pyArchInit gelieferten Stil mit eingekreister Nummer beziehungsweise Höhe über dem Symbol (wie seit 5.13.110-alpha und 5.13.111-alpha); die übrigen Ansichten werden wie bisher ohne Stil geladen.

Das dreistufige Fenster **Style Choice** (Absatz «Stilauswahl (SE und USM)», oben) erscheint **nur, wenn für diese Ansicht kein Standardstil gespeichert ist**; mit einem Standardstil lädt das SE-Formular einfach, und ein von Hand gewählter Stil überschreibt ihn nicht. «Eine Beschriftung pro Einheit» wird bei jedem Laden neu berechnet, auf den Zeichnungen des Filters dieses Moments: Sie hängt nicht von dem Filter ab, mit dem der Stil gespeichert wurde. Auch der Tab **Map preview** des SE-Formulars berücksichtigt den gespeicherten Standardstil (mit SQLite seit 5.13.113-alpha, davor trat ein Fehler auf; mit PostgreSQL schon seit 5.13.112-alpha); ohne Standardstil zeigt er wie bisher seine automatische Symbologie, und auch dort bleiben die Polygone in stratigraphischer Reihenfolge.

**Die Zeichenreihenfolge ist immer die stratigraphische** (seit 5.13.113-alpha). Bei den Ansichten der Einheiten (SE, USM, negative SE) werden die Polygone von der ältesten Einheit, unten, bis zur jüngsten, oben, gezeichnet, wie in der Matrix: zuerst die Perioden nach Chronologie, wenn sich die Periodisierung des Fundorts lesen lässt (die Einheiten ohne Periode vorweg), dann `order_layer` aufsteigend (0 = die älteste, zuerst gezeichnet), und innerhalb derselben Einheit der stratigraphische Index (Index 2, die Schicht, und ohne Index unten; Index 1, das Objekt, oben), wie im Time Manager (Tutorial 25). Das gilt für jeden Stil — den gespeicherten Standardstil, das gelieferte QML, ein importiertes QML, den in der Vorschau zusammengestellten Stil — auch bei **Auf geladene Layer anwenden** (*Apply to loaded layers*) und in der Vorschau des Fensters. So sieht man, wenn man in der QGIS-Legende das Häkchen bei einer Kategorie entfernt, was darunter liegt. Die anderen Ansichten (Höhen, Dokumentation, Strukturen…) erhalten keine Reihenfolge.

### Exportieren und Importieren

- **QML exportieren…** schreibt den Stil, wie er in der Vorschau zu sehen ist — Symbologie und Beschriftungen —, in eine `.qml`-Datei; der vorgeschlagene Name ist der der Ansicht (zum Beispiel `pyarchinit_us_view.qml`). Das dient dazu, eine Kopie aufzubewahren oder ihn in einer anderen Datenbank oder in QGIS zu verwenden.
- **QML importieren…** liest eine `.qml`-Datei, zeigt sie in der Vorschau und speichert sie als neuen Stil, für alle Fundorte, mit dem Dateinamen. Lässt sich die Datei nicht als QML lesen, sagt das eine Warnung mit dem Dateinamen (*“name.qml” does not read as QML.*), und es wird nichts geschrieben.
- Die gespeicherten Stile liegen in der mit pyArchInit **verbundenen Datenbank**, in der Tabelle `pyarchinit_view_styles`, die sich von selbst anlegt, mit SQLite und mit PostgreSQL: Mit PostgreSQL sehen sie alle Benutzer derselben Datenbank. Um sie in eine andere Datenbank zu übertragen, exportiert und importiert man sie als QML.
- Ist die Datenbank nicht verbunden (oder lässt sich die Stiltabelle nicht anlegen, zum Beispiel auf PostgreSQL ohne die Berechtigung, Tabellen anzulegen), sind die gespeicherten Stile nicht verfügbar und man kann nur exportieren: Die Statuszeile unter der Vorschau sagt es nach der Anzahl der Geometrien, mit «Datenbank nicht verbunden: Stile können nur exportiert werden» (*Database not connected: styles can only be exported.*) oder «Die Stiltabelle lässt sich in dieser Datenbank nicht anlegen: Stile können nur exportiert werden» (*The styles table cannot be created in this database: styles can only be exported.*).

## Layer-Styling

### QML-Dateien

PyArchInit enthält vordefinierte Stile im QML-Format:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Stil anwenden

1. Layer in Legende auswählen
2. Rechtsklick → **Eigenschaften**
3. Tab **Stil**
4. **Stil laden** → QML auswählen

### Anpassung

Stile können angepasst werden für:
- Farben nach SE-Typ
- Beschriftungen mit SE-Nummer
- Transparenz
- Rahmen und Füllungen

## Höhen und Messungen

### Höhen-Layer

Der Layer `pyarchinit_quote` speichert:
- X, Y-Koordinaten
- Z-Höhe (absolut)
- Höhenpunkttyp
- Referenz-SE
- Referenzareal

### Automatische Höhenberechnung

Vom SE-Formular werden Min/Max-Höhen berechnet:
1. Abfrage der mit der SE verbundenen Höhenpunkte
2. Extraktion von Minimal- und Maximalwert
3. Anzeige im Bericht

### Höheneingabe

1. Höhen-Layer im Bearbeitungsmodus
2. Punkt auf Karte zeichnen
3. Attribute ausfüllen:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Automatische SAM-Segmentierung

### Was ist SAM?

**SAM (Segment Anything Model)** ist das KI-Modell von Meta, das ein Bild in seine Objekte zerlegt. In pyArchInit verwandelt das SAM-Fenster ein Bild in **Polygone**, und zwar ausgehend von:

- einem **Orthofoto** (einer Rasterdatei: GeoTIFF, georeferenziertes JPEG…);
- oder einem in QGIS geladenen **Kachel-Layer oder Dienst**: XYZ wie ESRI World Imagery oder Google, WMS, ArcGIS REST.

Nicht nur Steine: auch **Gebäude, Straßen, Felder, Flüsse, Mauern**. Es gibt zwei Modellfamilien:

- **SAM 2.1** (Meta) findet die Umrisse der Objekte — aller Objekte oder derjenigen, die Sie mit Punkten, einem Rechteck oder einem Polygon angeben —, sagt aber nicht, was sie sind;
- die **Textklassen** (YOLOE-26 lokal, SAM 3 in der Cloud) suchen das, was Sie eintippen («building, road, river, field»), und jedes Polygon trägt seine Beschriftung.

Die Polygone landen in einem Layer Ihrer Wahl: in den SE-Layern von pyArchInit, in einem beliebigen Polygon-Layer des Projekts oder in einem neuen temporären Layer.

### Zugriff auf die Funktion

1. Aus der pyArchInit-Werkzeugleiste: Dropdown-Schaltfläche **Analysewerkzeuge** (Analysis Tools) → «SAM - Segmentierung (Steine, Gebäude, Straßen, Felder…)». Es ist die Standardaktion der Schaltfläche: Ein Klick auf das Symbol öffnet das Fenster sofort.
2. Oder über das Menü **pyArchInit** → «SAM - Segmentierung (Steine, Gebäude, Straßen, Felder…)».

Das Fenster heißt «SAM — Segmentation (stones, buildings, roads, fields, rivers…)». Seine Beschriftungen gibt es nur auf Italienisch und Englisch: Bei deutschsprachigem QGIS erscheint es auf Englisch, wie in der Skizze. Im Folgenden steht nach jeder übersetzten Beschriftung die englische in Klammern.

### SAM-Oberfläche

```
┌────────────────────────────────────────────────────────────────────┐
│ SAM — Segmentation (stones, buildings, roads, fields, rivers…)     │
├────────────────────────────────────────────────────────────────────┤
│ Automatic segmentation — from an orthophoto or a tile layer        │
│ (ESRI, Google, WMS) to polygons, with SAM 2.1 (Meta) or with text  │
│ classes.                                                           │
├─ Local environment ────────────────────────────────────────────────┤
│ ready — ultralytics 8.4.x, torch 2.x, mps                          │
│                                     [Install / update]  [Show log] │
├─ Image ────────────────────────────────────────────────────────────┤
│ Raster layer: [orthophoto.tif                                 v]   │
│               orthophoto.tif — 12000 × 9000 px                     │
│ Area:         (o) current view   ( ) whole raster                  │
│ Resolution (map units/px): [0.100000]                              │
│ Max side (px):             [2048]                                  │
├─ What to segment ──────────────────────────────────────────────────┤
│ (o) Everything (automatic)                                         │
│ ( ) Points: click the objects on the map                           │
│ ( ) Box: draw a rectangle                                          │
│ ( ) Polygon: draw the area                                         │
│ ( ) Polygon from layer: [polygon layer                        v]   │
│ ( ) Text classes:       [building, road, river, field          ]   │
│ Threshold: [0.30]                                                  │
├─ Model ────────────────────────────────────────────────────────────┤
│ Model: [Locale: SAM 2.1 Tiny — ~78 MB                         v]   │
│        weights present ✓                      [Download weights]   │
│ API key: [••••••••]                                Replicate key   │
├─ Target ───────────────────────────────────────────────────────────┤
│ Layer: [pyunitastratigrafiche                                 v]   │
│ Site: [Excavation 2026]           Area: [1]                        │
│ Stratigraphic index: [1]          US type: [pietra            v]   │
│ Field for the label: [label                                   v]   │
├────────────────────────────────────────────────────────────────────┤
│ Ready                                                              │
│                                         [Start]  [Cancel]  [Close] │
└────────────────────────────────────────────────────────────────────┘
```

Fünf Gruppen, von oben nach unten auszufüllen: «Lokale Umgebung» (*Local environment*), «Bild» (*Image*), «Was segmentiert werden soll» (*What to segment*), «Modell» (*Model*), «Ziel» (*Target*). Darunter folgen die Statuszeile («Bereit», *Ready*), in der auch die Meldungen der laufenden Arbeit erscheinen, und die Schaltflächen «Starten» (*Start*), «Abbrechen» (*Cancel*, nur während der Arbeit sichtbar) und «Schließen» (*Close*). Manche Zeilen erscheinen nur bei Bedarf: «API-Schlüssel:» (*API key:*) anstelle des Gewichtsstatus bei Cloud-Modellen; «Fundort:» (*Site:*), «Areal:» (*Area:*), «Stratigraphischer Index:» (*Stratigraphic index:*) und «SE-Typ:» (*US type:*) bei SE-Layern; «Feld für die Beschriftung:» (*Field for the label:*) bei anderen Layern. Das Fenster merkt sich das letzte Areal, die Klassen, die maximale Seitenlänge, das gewählte Modell und die API-Schlüssel.

Die Einträge der Modellliste sind immer italienisch beschriftet («Locale» = lokal), ebenso einige der unten zitierten Dienstmeldungen.

#### Lokale Umgebung

Die lokalen Modelle (SAM 2.1 und YOLOE) laufen nicht im Python von QGIS, sondern in einem **separaten Python**, das das Fenster selbst anlegt und prüft. Beim Öffnen zeigt die Gruppe «prüfe…» (*checking…*), dann:

- in Grün «bereit — ultralytics …, torch …, mps» (*ready — …*): Die Umgebung ist vorhanden; das letzte Wort ist das Rechengerät (`mps`, `cuda` oder `cpu`);
- in Orange «nicht installiert: für die lokalen Modelle (SAM 2.1, YOLOE) nötig. Ein System-Python 3.10–3.13, ~1,5 GB Pakete.» (*not installed: needed for the local models (SAM 2.1, YOLOE). A system Python 3.10–3.13, ~1.5 GB of packages.*).

«Installieren / aktualisieren» (*Install / update*) legt die Umgebung an oder aktualisiert ihre Pakete (siehe unten «Lokale SAM-Installation»); «Protokoll anzeigen» (*Show log*) blendet das Installationsprotokoll mit der Ausgabe von pip Zeile für Zeile ein und aus. Für Cloud-Modelle wird die Umgebung nicht gebraucht.

#### Bild

- «Raster-Layer:» (*Raster layer:*): das zu segmentierende Bild, gewählt unter den Rastern des Projekts: ein Orthofoto (Datei) oder ein Kachel- bzw. Dienst-Layer. Darunter steht in Grau, um welches der beiden es sich handelt: Dateiname und Größe in Pixeln (`orthophoto.tif — 12000 × 9000 px`) oder die Art des Dienstes, aus der Ansicht gerendert (`tile / WMS (reso dalla vista)`, `ArcGIS REST (reso dalla vista)` — diese Zeile ist italienisch, *reso dalla vista* = aus der Ansicht gerendert).
- «Bereich:» (*Area:*): «aktuelle Ansicht» (*current view*, das, was in der Karte zu sehen ist) oder «ganzes Raster» (*whole raster*). «ganzes Raster» ist nur bei Dateien wählbar: Ein Kacheldienst hat keinen Rand, man arbeitet immer auf der Ansicht (oder auf einem Rechteck oder Polygon).
- «Auflösung (Karteneinheiten/px):» (*Resolution (map units/px):*): nur für Kacheln: wie viele Karteneinheiten (Meter, oder Grad, wenn die Karte in geographischen Koordinaten ist) pro Pixel des gerenderten Bildes. Vorgeschlagen wird der Wert der Ansicht beim Öffnen des Fensters oder bei der Wahl des Layers: Wenn Sie danach zoomen, korrigieren Sie ihn von Hand. Je kleiner, desto mehr Details.
- «Maximale Seitenlänge (px):» (*Max side (px):*): die längste Seite des Bildes, das an das Modell geht: standardmäßig 2048, von 512 bis 8192. Darüber wird das Bild verkleinert; SAM arbeitet intern ohnehin mit 1024 px.

### Segmentierungsmodi

Die Gruppe «Was segmentiert werden soll» (*What to segment*) bietet sechs Modi. Mit dem Modus ändert sich die Modellliste (siehe «Verfügbare Modelle»), und darunter erscheint in Blau die Anleitung für diesen Modus.

#### 1. Alles automatisch

«Alles (automatisch)» (*Everything (automatic)*): SAM 2.1 segmentiert jedes Objekt, das es im gewählten «Bereich:» findet («aktuelle Ansicht» oder «ganzes Raster»). Die Polygone haben keine Klasse: Im temporären Layer bekommen sie die Beschriftung «segment». Gestartet wird mit «Starten» (*Start*).

#### 2. Punkte

«Punkte: Objekte auf der Karte anklicken» (*Points: click the objects on the map*): «Auswahl starten» (*Start selection*) drücken; das Fenster verschwindet, und die QGIS-Meldungsleiste nennt die Befehle. Die Objekte einzeln anklicken: Jeder Klick ist ein Objekt. Rechtsklick oder Enter beendet, die Rücktaste entfernt den letzten Punkt, Esc bricht ab. Das Fenster kehrt zurück, und die Segmentierung läuft auf dem gewählten «Bereich:», ein Objekt pro Punkt; Punkte außerhalb des Bildes werden ignoriert.

#### 3. Rechteck

«Rechteck: ein Rechteck zeichnen» (*Box: draw a rectangle*): «Auswahl starten» drücken und ein Rechteck auf der Karte aufziehen (Esc oder Rechtsklick bricht ab). Das Bild wird auf das Rechteck zugeschnitten, und alles darin wird segmentiert.

#### 4. Polygon

«Polygon: den Bereich zeichnen» (*Polygon: draw the area*): «Auswahl starten» drücken und die Stützpunkte anklicken; Rechtsklick, Enter oder Doppelklick schließen das Polygon (mindestens drei Stützpunkte), die Rücktaste entfernt den letzten Stützpunkt, Esc bricht ab. Segmentiert wird nur innerhalb des Polygons.

#### 5. Polygon aus Layer

«Polygon aus Layer:» (*Polygon from layer:*): im Dropdown daneben einen Polygon-Layer wählen. Verwendet wird das ausgewählte Objekt des Layers, oder alle, wenn keines ausgewählt ist (mehrere Objekte werden zu einem vereinigt). Wie beim gezeichneten Polygon wird nur innerhalb segmentiert: praktisch, um innerhalb eines Schnitts, einer Grabungsfläche oder einer schon gezeichneten Grenze zu arbeiten. Gestartet wird mit «Starten».

#### 6. Textklassen

«Textklassen:» (*Text classes:*): ins Feld daneben schreiben, wonach gesucht werden soll: **englische** Wörter, durch Kommas getrennt (Standard «building, road, river, field»; weitere Beispiele: stone, wall). Jede Klasse wird zur Beschriftung der Polygone. Das funktioniert mit YOLOE-26 lokal oder mit SAM 3 von Roboflow in der Cloud, auf dem gewählten «Bereich:». Gestartet wird mit «Starten».

**«Schwellenwert:»** (*Threshold:*; standardmäßig 0,30, von 0,05 bis 0,95) ist die Mindestkonfidenz, damit ein Ergebnis behalten wird: niedriger ergibt mehr Polygone, auch unsichere; höher ergibt weniger, aber sicherere. Das Cloud-Modell von Replicate verwendet ihn nicht.

### Verfügbare Modelle

Die Gruppe «Modell» (*Model*) hat ein Dropdown «Modell:» (*Model:*), dessen Inhalt vom gewählten Modus abhängt:

| Modell | Typ | Voraussetzungen | Modi |
|--------|-----|-----------------|------|
| SAM 2.1 Tiny | Lokal | lokale Umgebung + Gewichte ~78 MB | alle außer Textklassen; das leichteste und schnellste |
| SAM 2.1 Small | Lokal | lokale Umgebung + Gewichte ~92 MB | alle außer Textklassen |
| SAM 2.1 Base+ | Lokal | lokale Umgebung + Gewichte ~162 MB | alle außer Textklassen |
| SAM 2.1 Large | Lokal | lokale Umgebung + Gewichte ~449 MB | alle außer Textklassen; das genaueste und langsamste |
| Cloud: Replicate SAM-2 | Cloud | API-Schlüssel von Replicate | nur automatische Segmentierung (im Modus «Punkte» werden die Klicks mit einer Warnung ignoriert) |
| YOLOE-26 S | Lokal | lokale Umgebung + Gewichte ~31 MB + MobileCLIP2 254 MB (einmalig) | Textklassen |
| YOLOE-26 M | Lokal | lokale Umgebung + Gewichte ~70 MB + MobileCLIP2 254 MB (einmalig) | Textklassen |
| YOLOE-26 L | Lokal | lokale Umgebung + Gewichte ~79 MB + MobileCLIP2 254 MB (einmalig) | Textklassen |
| Cloud: Roboflow SAM 3 | Cloud | API-Schlüssel von Roboflow | Textklassen |

Im Dropdown lauten die Einträge: «Locale: SAM 2.1 Tiny — ~78 MB», «Locale: YOLOE-26 S (classi a testo) — ~31 MB + MobileCLIP2 254 MB», «Cloud: Replicate SAM-2 (solo automatico, chiave API)», «Cloud: Roboflow SAM 3 (classi a testo, chiave API)» (*locale* = lokal, *classi a testo* = Textklassen, *solo automatico* = nur automatisch, *chiave* = Schlüssel).

**Gewichte.** Bei einem lokalen Modell steht unter dem Dropdown der Status der Gewichte: «Gewichte vorhanden ✓» (*weights present ✓*, grün) oder «Gewichte fehlen (~N MB)» (*weights missing (~N MB)*, orange), daneben die Schaltfläche «Gewichte herunterladen» (*Download weights*). Der Download mit Fortschrittsbalken holt die Dateien aus den öffentlichen Assets von ultralytics auf GitHub (kein Konto nötig). Für YOLOE wird zusätzlich der Text-Encoder MobileCLIP2 (254 MB) geladen, nur einmal für S, M und L. Die Gewichte liegen in `~/pyarchinit_5/bin/models/sam/`.

**API-Schlüssel.** Bei einem Cloud-Modell ersetzen das Feld «API-Schlüssel:» (*API key:*) und der Link zum Schlüssel den Gewichtsstatus (siehe «API-Konfiguration»).

### SAM-3 mit Text-Prompt

Im Modus «Textklassen» bittet man nicht „zerlege alles“, sondern „finde diese Dinge“:

- eine oder mehrere Klassen auf Englisch, durch Kommas getrennt, eingeben: `building, road, river, field` oder `stone, wall`…;
- **YOLOE-26** (lokal, S/M/L) versteht die Wörter über den Text-Encoder MobileCLIP2; **SAM 3** von Roboflow (Cloud) erhält dieselben Klassen als Text-Prompts (höchstens 16);
- jedes Polygon trägt die Klasse, die es gefunden hat: im temporären Layer im Feld `label`, in einem eigenen Layer im «Feld für die Beschriftung:» (*Field for the label:*). In den SE-Layern von pyArchInit wird die Klasse nicht geschrieben.

SAM 2.1 im Modus «Alles (automatisch)» vergibt dagegen keine Klassen: Es findet Umrisse, keine Namen.

### API-Konfiguration

Schlüssel braucht man nur für Cloud-Modelle. Das Cloud-Modell im Dropdown wählen, den Schlüssel in das Feld «API-Schlüssel:» (*API key:*) einfügen (der Text bleibt verborgen) und «Starten» drücken: Der Schlüssel wird in den QGIS-Einstellungen gespeichert und beim nächsten Mal wieder vorgeschlagen. Bei Cloud-Modellen wird das vorbereitete Bild an den Dienst gesendet.

#### Replicate API (SAM-2)
1. Ein Konto auf [replicate.com](https://replicate.com) anlegen
2. Unter [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) ein Token erzeugen (der Link «Replicate-Schlüssel» (*Replicate key*) neben dem Feld öffnet dieselbe Seite)
3. Es mit dem Modell «Cloud: Replicate SAM-2» in «API-Schlüssel:» einfügen

#### Roboflow API (SAM-3)
1. Ein Konto auf [roboflow.com](https://roboflow.com) anlegen
2. Den Schlüssel unter [app.roboflow.com/settings/api](https://app.roboflow.com/settings/api) kopieren (Link «Roboflow-Schlüssel» (*Roboflow key*) neben dem Feld)
3. Ihn mit dem Modell «Cloud: Roboflow SAM 3» in «API-Schlüssel:» einfügen

### Lokale SAM-Installation

Kein Terminalbefehl nötig: Die Umgebung für die lokalen Modelle wird aus dem Fenster installiert.

1. Nötig ist ein **System-Python 3.10–3.13**: Die Pakete werden nicht in das Python von QGIS installiert, um es nicht zu beschädigen. Das Fenster sucht es selbst: unter **macOS** das Python von [python.org](https://www.python.org/downloads/) oder von Homebrew, unter **Windows** den Launcher `py` des Pythons von python.org, unter **Linux** `python3.10`…`python3.13` oder `python3` des Systems.
2. In der Gruppe «Lokale Umgebung» auf «Installieren / aktualisieren» (*Install / update*) klicken: Die virtuelle Umgebung `~/pyarchinit_5/bin/sam_venv` wird angelegt, und darin werden `ultralytics` (das torch, torchvision, OpenCV und numpy mitbringt) und `requests` installiert: etwa **1,5 GB** Pakete, nur einmal. Unter Linux ohne NVIDIA-Karte wird die CPU-Version von torch installiert, die viel leichter ist.
3. «Protokoll anzeigen» (*Show log*) zeigt pip bei der Arbeit. Am Ende wird der Status grün: «bereit — ultralytics …, torch …, mps».
4. Die Gewichte des gewünschten Modells mit «Gewichte herunterladen» (*Download weights*, Gruppe «Modell») laden.

Ein erneuter Klick auf «Installieren / aktualisieren» aktualisiert die Pakete. Das Rechengerät wird automatisch gewählt: **MPS** auf Macs mit Apple Silicon, **CUDA** mit einer NVIDIA-Karte, sonst **CPU** (funktioniert, ist aber langsamer). Schlagen MPS oder CUDA fehl, startet die Arbeit von selbst erneut auf der CPU.

| Was | Wo |
|-----|----|
| Python-Umgebung | `~/pyarchinit_5/bin/sam_venv` |
| Modellgewichte | `~/pyarchinit_5/bin/models/sam/` |
| API-Schlüssel | QGIS-Einstellungen |

`~/pyarchinit_5` ist der Datenordner von pyArchInit (oder der in der Variablen `PYARCHINIT_HOME` angegebene Ordner).

### Ziel und Attribute

Die Gruppe «Ziel» (*Target*) bestimmt, wohin die Polygone gehen. Das Dropdown «Layer:» listet die Polygon-Layer des Projekts und «— neuer temporärer Layer —» (*— new temporary layer —*) auf; ist `pyunitastratigrafiche` geladen, wird dieser vorgeschlagen.

| Ziel | Was geschrieben wird |
|------|----------------------|
| «— neuer temporärer Layer —» | ein Memory-Layer `SAM_<Raster>_<Datum_Uhrzeit>` im KBS des Bildes, mit den Feldern `label` (die Klasse oder «segment»), `score` (Konfidenz), `area`, `source` (das Modell) und `created` (Datum und Uhrzeit) |
| `pyunitastratigrafiche` / `pyunitastratigrafiche_usm` | `scavo_s` = «Fundort:» (*Site:*; aus der Konfiguration, nicht änderbar), `area_s` = «Areal:» (*Area:*; Pflichtfeld), `stratigraph_index_us` = «Stratigraphischer Index:» (*Stratigraphic index:*; 1 = Steine/Objekte, 2 = Schicht/Fläche), `tipo_us_s` = «SE-Typ:» (*US type:*; pietra, layer, accumulo, taglio, struttura), `disegnatore` = `SAM <Modell>` (z. B. `SAM sam2.1_t.pt`), `data` = heute; `us_s` bleibt leer |
| ein anderer Polygon-Layer | die Klasse im «Feld für die Beschriftung:» (*Field for the label:*), einem Textfeld (vorgeschlagen wird `label`, `etichetta`, `classe`, `class`, `tipo` oder `nome`, falls vorhanden; leer = nicht schreiben); hat der Layer Felder `score`, `area`, `source` oder `created`, werden auch diese gefüllt |

- In den SE-Layern wird die SE-Nummer danach in der Attributtabelle vergeben; die Abschlussmeldung erinnert daran: «Danach die SE-Nummern in der Attributtabelle vergeben.» (*Then assign the US numbers in the attribute table.*).
- Die Polygone werden in das KBS des Ziel-Layers umprojiziert und sofort darin gespeichert (war der Layer schon im Bearbeitungsmodus, werden auch seine ausstehenden Änderungen gespeichert).
- Der temporäre Layer lebt nur bis zum Schließen von QGIS: Um ihn zu behalten, in eine Datei exportieren (Rechtsklick auf den Layer → Exportieren).

### Wie es funktioniert

1. **Das Bild.** Bei einer Datei wird der Bereich mit GDAL zugeschnitten und bei Bedarf verkleinert: Die Pixel sind die echten der Datei, nicht die in der Karte gezeichneten (der Layerstil spielt keine Rolle; Raster, die nicht 8 Bit haben, werden auf 0–255 gestreckt). Kacheln und Dienste haben keine Datei: QGIS rendert die Ansicht mit seiner Zeichen-Engine in der gewählten Auflösung — nur diesen Layer, ohne die anderen Layer der Karte —, und dieses Bild wird segmentiert.
2. **Der Bereich.** Bei einem Polygon (gezeichnet oder aus einem Layer) wird das umschließende Rechteck genommen, alles außerhalb des Polygons weiß gefärbt, und am Ende werden die Ergebnisse auf das Polygon zugeschnitten.
3. **Das Modell.** Die Arbeit erledigt `scripts/sam_worker.py`, das außerhalb von QGIS mit dem Python von `sam_venv` läuft (oder den Cloud-Dienst aufruft): QGIS friert nicht ein. Seine Fortschrittsmeldungen (die Zeilen `[sam] …` des Workers, auf Italienisch) erscheinen in der Statuszeile: Modell und Gerät, dann wie viele Polygone in wie vielen Sekunden. Polygone unter 20 Pixeln werden verworfen und die Umrisse vereinfacht.
4. **Zurück in die Karte.** Der Worker liefert die Polygone in Pixeln; pyArchInit rechnet sie mit der Georeferenz des Bildes in Koordinaten zurück, repariert ungültige Geometrien und projiziert sie in das KBS des Ziel-Layers.

### SAM-Arbeitsablauf

**1. Vorbereitung**
- Das Orthofoto laden oder einen Kachel-Layer (z. B. ESRI World Imagery als XYZ-Kacheln)
- Das Bezugssystem des Projekts prüfen
- Um in die SE zu schreiben: `pyunitastratigrafiche` (oder `pyunitastratigrafiche_usm`) laden und den Fundort in der Konfiguration prüfen
- Beim ersten Mal, für lokale Modelle: «Installieren / aktualisieren», dann «Gewichte herunterladen»

**2. Konfiguration**
- «Bild»: Raster-Layer, Bereich, Auflösung (bei Kacheln) und maximale Seitenlänge
- «Was segmentiert werden soll»: der Modus, der Schwellenwert und bei Textklassen die Klassen
- «Modell»: ein lokales Modell mit vorhandenen Gewichten oder ein Cloud-Modell mit seinem Schlüssel
- «Ziel»: der Layer und seine Attribute

**3. Ausführung**
- «Starten» oder «Auswahl starten», dann Punkte, Rechteck oder Polygon auf der Karte
- Die Statuszeile verfolgen; «Abbrechen» stoppt die Arbeit
- Am Ende erscheint «Fertig: N Polygone zu „Layer“ hinzugefügt (Modell).» (*Done: N polygons added to “layer” (model).*)

**4. Nachbearbeitung**
- Die Polygone prüfen; eventuelle Warnungen erscheinen in der QGIS-Meldungsleiste
- SE-Layer: die SE-Nummern (`us_s`) in der Attributtabelle vergeben
- Falsche Polygone mit den Bearbeitungswerkzeugen von QGIS korrigieren, zusammenführen oder löschen
- Temporärer Layer: exportieren, wenn er erhalten bleiben soll

## Kartographische Integration

### GIS-Datenexport

Vom SE-Formular, Tab Karte:
- **GeoPackage exportieren**: Layer als GPKG
- **Shapefile exportieren**: Layer als SHP
- **GeoJSON exportieren**: Layer als JSON

### GIS-Datenimport

Bestehende Geometrien importieren:
1. Layer in QGIS laden
2. Feature auswählen
3. Import-Funktion verwenden

### Geoprocessing

Verfügbare räumliche Operationen:
- Puffer
- Verschneidung
- Union
- Differenz
- Zentroide

## Best Practices

### 1. Orthofotos

- Minimale Auflösung: 1-2 cm/Pixel
- Format: Georeferenziertes GeoTIFF
- Bezugssystem: Konsistent mit Projekt

### 2. Digitalisierung

- Snap für Präzision verwenden
- Topologie überprüfen
- Attributkonsistenz beibehalten

### 3. SAM-Segmentierung

- Orthofoto guter Qualität, gleichmäßige Beleuchtung, guter Kontrast zwischen Objekten und Hintergrund
- **Große Orthofotos**: nach Ansicht oder Rechteck arbeiten, nicht mit «ganzes Raster». SAM arbeitet intern mit 1024 px, und oberhalb der «Maximalen Seitenlänge (px):» wird das Bild verkleinert: Auf zu großen Flächen gehen kleine Objekte verloren
- **Kacheln**: eine Zoomstufe wählen, in der die Objekte mit bloßem Auge erkennbar sind (z. B. 0,3–0,6 m/px für Gebäude und Straßen). «Auflösung (Karteneinheiten/px):» schlägt die der Ansicht vor; ist der Bereich groß, wird das Bild auf die maximale Seitenlänge verkleinert und die tatsächliche Auflösung wird schlechter
- **Textklassen**: einfache englische Substantive (building, road, river, field, stone, wall)
- Klassen kommen nur von YOLOE oder SAM 3: SAM 2.1 im Modus «Alles (automatisch)» findet Umrisse, vergibt aber keine Klassen
- **Hardware**: Macs mit Apple Silicon nutzen MPS, eine NVIDIA-Karte CUDA, sonst die langsamere CPU (dann besser SAM 2.1 Tiny oder Small, YOLOE-26 S und kleine Bereiche)
- Nachprüfung immer erforderlich

### 4. Layer-Organisation

- Nach Typologie gruppieren
- Konsistente Stile verwenden
- Ordnung in Legende beibehalten

## Problemlösung

### Layer nicht angezeigt

**Mögliche Ursachen**:
- Falsche Ausdehnung
- Verschiedenes Bezugssystem
- Aktiver Filter

**Lösungen**:
- Auf Layer zoomen
- KBS überprüfen
- Filter entfernen

### SAM funktioniert nicht

| Meldung oder Symptom | Was tun |
|----------------------|---------|
| «Lokale Umgebung» in Orange: «nicht installiert…» (*not installed…*), oder «Die lokale Umgebung ist nicht installiert: „Installieren / aktualisieren“ drücken (oder ein Cloud-Modell wählen).» (*The local environment is not installed: press “Install / update” (or choose a cloud model).*) | «Installieren / aktualisieren» drücken. Nötig ist ein System-Python 3.10–3.13; fehlt es, erscheint `Installation failed: Nessun Python 3.10–3.13 trovato: installa Python da python.org (o Homebrew) e riprova.` (kein Python 3.10–3.13 gefunden: Python von python.org oder Homebrew installieren). Scheitert pip, steht der Fehler in «Protokoll anzeigen». Unter Linux ohne NVIDIA-Karte wird die CPU-Version von torch installiert |
| «Gewichte fehlen (~N MB)» (*weights missing (~N MB)*), oder «Die Modellgewichte fehlen: „Gewichte herunterladen“ drücken.» (*The model weights are missing: press “Download weights”.*) | «Gewichte herunterladen» drücken (Internetverbindung nötig) |
| «Der API-Schlüssel des Dienstes wird benötigt.» (*The service API key is needed.*) | Bei einem Cloud-Modell den Schlüssel in «API-Schlüssel:» einfügen (siehe «API-Konfiguration») |
| «Kein Polygon gefunden: einen kleineren Bereich, einen niedrigeren Schwellenwert oder ein anderes Modell versuchen.» (*No polygon found: try a smaller area, a lower threshold or another model.*) | Kleinerer Bereich, niedrigerer «Schwellenwert:», ein anderes Modell (ein größeres SAM 2.1 oder die Textklassen); bei Kacheln eine feinere Auflösung |
| «Der gewählte Bereich deckt das Raster nicht ab» (Meldung auf Italienisch: `l'area scelta non copre il raster`) | Ansicht, Rechteck oder Polygon liegen außerhalb des Rasters: auf das Raster zoomen und erneut versuchen |
| «Das Areal für den SE-Layer ausfüllen.» (*Fill in the area for the US layer.*) | Das «Areal:» in der Gruppe «Ziel» eintragen |
| «Gedrehtes Raster: nicht unterstützt (vorher umprojizieren)» (Meldung auf Italienisch: `raster ruotato: non supportato (riproiettalo prima)`) | Das Raster mit gdalwarp umprojizieren (QGIS-Menü Raster) und die neue Datei verwenden |
| «Segmentierung fehlgeschlagen» (*Segmentation failed*) mit den letzten Zeilen des Workers | Die Zeilen in der Meldung lesen; mit kleinerem Bereich oder kleinerer «Maximaler Seitenlänge (px):» oder mit einem kleineren Modell erneut versuchen |

### Fehlerhafte Geometrien

**Mögliche Ursachen**:
- Digitalisierungsfehler
- Problematischer Import

**Lösungen**:
- "Fix Geometries" verwenden
- Element neu zeichnen

### Layer geladen, aber Geometrien nicht sichtbar (SQLite)

**Symptom**:
- Ein pyArchInit-Layer einer SQLite/SpatiaLite-Datenbank (z. B. SE `pyunitastratigrafiche`, Mauer-SE, Funde, negative SE) wird geladen und die Attributtabelle zeigt die Datensätze, aber auf der Karte wird nichts gezeichnet und "Auf Layer zoomen" funktioniert nicht

**Ursache**:
- Der räumliche Index (R*Tree) des Layers wurde nicht gepflegt: seine Trigger gingen verloren, als eine Tabelle neu erstellt wurde (z. B. durch ältere Schema-Update-Skripte), oder Daten wurden unter Umgehung der Trigger importiert
- QGIS wählt die zu zeichnenden Objekte über diesen Index aus, daher bleiben sie unsichtbar
- Betroffen sind auch Datenbanken, die zwischen Oktober 2025 und September 2026 aus der SQLite-Vorlage erstellt wurden

**Lösung (automatisch)**:
- Beim Verbinden mit einer SQLite-Datenbank prüft pyArchInit alle räumlichen Indizes (wenige Augenblicke; bei einer intakten Datenbank wird nichts geschrieben) und baut beschädigte automatisch neu auf
- Seit Version 5.13.16-alpha repariert dieselbe Prüfung auch die **räumlichen Views** (`pyarchinit_us_view`, `pyarchinit_quote_view`, Strukturen, Funde, die UT-Views usw.):
  - jede View wird an die ROWID ihrer Geometrietabelle gebunden
  - Registrierungen von Views, die nicht mehr existieren, werden entfernt
  - fehlende Standard-Views werden neu erstellt
  - die UT-Views werden als räumliche Views registriert
  - Geometrietabellen ohne räumlichen Index erhalten einen: nötig, wenn dem mit QGIS gelieferten GDAL die SpatiaLite-Funktionen fehlen (z. B. QGIS unter macOS), wo diese Layer ohne Index nichts zeichneten
- Bevor etwas geändert wird, wird EINE einzige Sicherungskopie neben der Datenbank gespeichert: `<datenbank>.sqlite.pre_spatial_index_repair_<datum-uhrzeit UTC>`
- Das Ergebnis steht im QGIS-Protokollbedienfeld (Ansicht → Bedienfelder → Protokollmeldungen, Reiter "PyArchInit")

**Vorgehen**:
- Nichts manuell zu starten: die Prüfung läuft automatisch bei der ERSTEN Verbindung mit jeder Datenbank in jeder QGIS-Sitzung (also nach dem Plugin-Update oder nach einem Neustart von QGIS)
- Waren die Layer bereits geladen, sie nach der Reparatur entfernen und erneut hinzufügen (oder das Projekt neu öffnen)
- Meldet das Protokoll "PyArchInit", dass ein Index NICHT repariert werden konnte (z. B. SpatiaLite nicht ladbar), die Ursache beheben und QGIS neu starten: die Prüfung wird erst in einer neuen Sitzung wiederholt
- Die Sicherungsdatei kann gelöscht werden, sobald die Layer überprüft sind
- Um die Prüfung erneut auszuführen (z. B. nach dem Wiederherstellen einer Sicherung), QGIS neu starten
- Hinweis: In `inventario_materiali_view` wird der Punkt des Fundorts für jeden Fund wiederholt, daher zeigt "Objekte abfragen" (Identify) auf diesem Punkt einen der Funde

## Referenzen

### Quelldateien
- `modules/gis/pyarchinit_pyqgis.py` - GIS-Integration
- `tabs/Sam_Segmentation_Dialog.py` - SAM-Fenster: Gruppen, Modi, Ziel
- `modules/utility/sam_environment.py` - Separate Python-Umgebung, Pakete und Gewichte
- `modules/gis/sam_raster_source.py` - Zu segmentierendes Bild (GDAL-Zuschnitt oder Rendering der Ansicht) und Georeferenz
- `modules/gis/sam_map_tools.py` - Kartenwerkzeuge für Punkte, Rechteck und Polygon
- `scripts/sam_worker.py` - Worker außerhalb von QGIS: SAM 2.1, YOLOE, Replicate, Roboflow

### Layer
- `pyunitastratigrafiche` - Ablagerungs-SE
- `pyunitastratigrafiche_usm` - Mauerwerks-SE
- `pyarchinit_quote` - Höhen

---

## Video-Tutorial

### GIS-Integration
`[Platzhalter: video_gis_integration.mp4]`

**Inhalte**:
- Vordefinierte Layer
- SE-Visualisierung
- Styling und Beschriftungen
- Kartographischer Export

**Voraussichtliche Dauer**: 15-18 Minuten

### SAM-Segmentierung
`[Platzhalter: video_sam_segmentation.mp4]`

**Inhalte**:
- SAM-Konfiguration
- Segmentierungsmodi
- Nachbearbeitung
- Best Practices

**Voraussichtliche Dauer**: 12-15 Minuten

---

*Letzte Aktualisierung: Oktober 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../../animations/pyarchinit_image_classification_animation.html)
