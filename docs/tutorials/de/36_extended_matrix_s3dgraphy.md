# Tutorial 36: Extended Matrix Export und s3dgraphy Bridge

## Einleitung

Ab Version **5.2.0-alpha** integriert PyArchInit eine **bidirektionale Bridge** mit der Bibliothek **s3dgraphy** (Extended-Matrix-Datenmodell von Emanuel Demetrescu). Die Bridge erlaubt:

- **Export** des stratigraphischen Diagramms als Extended Matrix in **em.json**, dem Format, das EMStudio öffnet (der alte GraphML-Export ist im Ruhestand)
- **Re-Import** von in yEd vorgenommenen Änderungen (SE-Bewegungen zwischen Perioden/Gruppen) zur Aktualisierung der SQL-Datenbank
- **Anhängen von Paradata** (Author / License / Embargo) auf Stättenebene
- **Gruppieren** von SE nach Dimension (struttura, area, attivita, settore, ambient, saggio, quad_par oder Ad-hoc-Gruppen)

Aktueller Tag: `narrativa-3d-rifiniture-5.13.133-alpha` (2026-10-17).

---

## 1. Voraussetzungen

- SQLite/Spatialite-Datenbank **oder PostgreSQL/PostGIS**: der em.json-Export ist auf beiden Systemen derselbe (die Verbindung ist die des Projekts; `export_site` akzeptiert `sqlite://` und `postgresql://`)
- **Phase 1 node_uuid-Migration** wird beim DB-Öffnen automatisch angewendet
- **EMStudio**, um die em.json zu öffnen (Installation über **Extended Matrix → Installa EMStudio…**), oder das Panel **Vedi la matrice…** in QGIS, das nichts weiter braucht. **yEd** (https://www.yworks.com/products/yed) wird nur gebraucht, wenn dort gezeichnete GraphML-Dateien importiert werden (§5)

> ⚠️ Bei DBs vor 5.2.0-alpha kann ein QGIS-Neustart nötig sein.

---

## 2. Extended Matrix exportieren (grüner Knopf)

### 2.1 Dialog öffnen

1. Öffne das **SE-Formular** der gewünschten Stätte
2. Klicke den grünen Knopf **"Esporta Extended Matrix"** (unter dem Tab Rapporti)

### 2.2 Tab "Export"

Das Fenster sagt oben, wofür jedes Format gut ist. Es enthält:

- **Formati** (Formate): **DOT (Graphviz) — matrice di Harris** und **em.json (Extended Matrix, per EMStudio)**, beide von Anfang an angehakt, dazu **Matrice per fasi** (Matrix nach Phasen, chronologische Analyse), wahlweise. GraphML wird nicht mehr exportiert: das JSON dieses Fensters **ist em.json**, dieselbe Datei, die der Menüpunkt **Extended Matrix → Esporta sito in em.json…** erzeugt — gleicher Projektor, gleiche Symbolik.
- **Opzioni** (Optionen): **Controlla la sequenza stratigrafica e segnala i problemi** (die stratigraphische Sequenz prüfen und die Probleme melden). Es ist die einzige verbliebene Option, und sie wird wirklich gelesen: ohne Haken findet die Prüfung nicht statt. Die zwei alten Kästchen, die zu yEd sprachen (Auto-Layout-Hinweise, Färbung nach Periode), sind mit dem GraphML-Export verschwunden.
- **Extended Matrix**: vier Knöpfe neben dem Export — **Apri in EMStudio** und **Vedi la matrice** (beide werden nach einem erfolgreichen em.json-Export aktiv; der zweite zeichnet die Matrix innerhalb von QGIS, ohne EMStudio), **Consegna alla stanza…** und **Apri la stanza**. Es sind dieselben pyArchInit-Menüpunkte, nur in Reichweite.

Beim Druck auf **Esporta** wird nach dem **Zielordner** gefragt.

Autoren, Lizenzen, Embargos und Gruppen verwaltet das Fenster **"Manage paradata"** (§3).

### 2.2.1 Sondagen: ein einziger Graph für die ganze Stätte

Ab Version **5.13.109-alpha** enthält die em.json **einen einzigen Graphen** mit den Einheiten aller Sondagen: Es gibt nichts auszuwählen. Das Fenster «Esporta Extended Matrix» hat die Gruppe «Saggi» (Sondagen) nicht mehr, und die Menüeinträge **Esporta sito in em.json…** und **Vedi la matrice…** fragen nur noch nach der Stätte.

Die Sondage ist das Feld **Saggio** des SE-Formulars: Es bleibt ein Feld wie die anderen, das sich als Dimension zum Gruppieren der Einheiten verwenden lässt (`saggio`, §4) und in das *Briefing* der Erzählung eingeht (§10.4), die Datei aber nicht mehr teilt. Eine mit früheren Versionen (bis 5.13.108-alpha) exportierte Datei mit einem Graphen je Sondage lässt sich im Panel der Matrix weiterhin öffnen (§10.8).

### 2.3 Klick auf "Esporta"

Die Dateien, die entstehen, je nach angehakten Formaten:
- `<Stätte>.em.json` — Extended Matrix, in EMStudio zu öffnen oder an einen Raum zu übergeben
- `Extended_Matrix_<site>[_<area>].dot` — Graphviz DOT, für die klassische Harris-Matrix
- `Extended_Matrix_<site>[_<area>]_phased.json` — Ansicht pro Epoche

> **Orte kommen in die em.json.** Der Ort der Stätte, die Toponymkette und die Gruppen der Areale, Sektoren, Sondagen und Räume werden zusammen mit den Einheiten exportiert, verbunden durch `is_in_location`-Kanten (§4).

Die Schlussmeldung listet die Dateien auf und, für em.json, **wie viele Knoten und wie viele Kanten** herauskamen, samt etwaigen Hinweisen.

> **Ab 5.13.122-alpha kommt die em.json sauberer heraus.** Jede Einheit hat **nur eine** Kante zu der Epoche, in der sie entsteht (vorher hatte sie zwei gleiche: Die Bibliothek fügte ihre eigene hinzu, nachdem die des Importers bereits wieder angehängt worden war); die **Beschreibung** des Knotens ist die stratigraphische Definition oder, falls diese leer ist, die Beschreibung des Datensatzes (vorher erschien das Wort «None»); der Graph hat einen **Namen**, nämlich den der Stätte (vorher öffnete EMStudio ihn als «Untitled»); eine Einheit, die bis in eine jüngere Epoche fortbesteht, hat die Kante `survive_in_epoch` zu **jeder** dazwischenliegenden Epoche, nicht nur zur letzten. Für eine Stätte, die aus einer em.json von EMStudio stammt, siehe auch §5.0, «Die em.json wird gemerkt».

> **GraphML wird nicht mehr exportiert**: die Matrix wird in EMStudio angesehen und validiert, das em.json liest. Die Zeitzeilen (Swimlanes) des alten GraphML sind mit ihm gegangen. GraphML überlebt nur im **Eingang**, für in yEd gezeichnete Dateien (§5).

---

## 3. "Manage paradata"-Dialog (4 Tabs)

### 3.1 Zugriff
Klicke den Knopf **"Manage paradata"** im SE-Formular (neben dem grünen Export-Knopf).

### 3.2 Die 4 Tabs

| Tab | Inhalt | Erzeugte Datei |
|---|---|---|
| **Authors** | Autoren hinzufügen (Name + ORCID + Rolle) | `paradata_<site>.graphml` |
| **Licenses** | Dataset-Lizenz (z.B. CC-BY-NC-4.0 + URL) | dito |
| **Embargoes** | Embargo-Daten + Begründung | dito |
| **Groups** | Ad-hoc-Gruppen (Name + SE-Mitgliederauswahl) | `groups_<site>.graphml` |

Dateien werden neben der SQLite-DB gespeichert und sind **Git-versionierbar**.

---

## 4. Dimensionen und Gruppentypen in der em.json

Die em.json, die pyArchInit exportiert, enthält die **Ortsgruppen** (`LocationNodeGroup`) des SE-Formulars, unterschieden durch den Typ `kind`: `toponym`, die Kette nazione → regione → provincia → comune und der Ort der Stätte (§4.1); `study`, die **Areale**, **Sektoren** und **Sondagen**; `functional`, die **Räume**. Jede Einheit ist durch `is_in_location`-Kanten mit den Gruppen verbunden, in denen sie liegt; die Kennung der Gruppe nennt das Feld, aus dem sie entsteht (zum Beispiel `loc::area::study::1`). Die Datei enthält keine Farben: Welche Farben erscheinen, entscheidet, wer sie liest – EMStudio mit seinem eigenen Stil, das Matrix-Panel in QGIS mit den visuellen Regeln der Bibliothek s3dgraphy. Der alte GraphML-Export färbte die Gruppen nach Dimension ein: diese Palette ist mit ihm in den Ruhestand gegangen. Die Bibliothek kann auch nach **Struktur**, **Aktivität**, **Quadrat** und nach Ad-hoc-Gruppen gruppieren, wobei eine Zugehörigkeit primär ist und die übrigen sekundär (`is_primary`): pyArchInit verlangt das heute nicht von ihr, und in der Datei erscheint dieses Attribut nur an den Kanten der Toponymkette, dort stets falsch.

### 4.1 Toponymkette (5.6.0-alpha)

Die Felder `site_table.{nazione, regione, provincia, comune}` werden automatisch als rekursive `LocationNodeGroup(kind="toponym")`-Kette emittiert (Parent: nazione → regione → provincia → comune). Leere Verwaltungsebenen werden übersprungen, ohne die Kette zu unterbrechen. Eine Cross-Site-Deduplizierung garantiert, dass dasselbe `comune` in 2 Sites zu **einem geteilten Knoten** in der em.json wird.

---

## 4.2 Mehrdimensionale Mitgliedschaft (5.6.0-alpha)

Eine Einheit kann zugleich in mehreren Gruppen liegen — einem Areal, einem Sektor, einer Sondage, einem Raum, dazu dem Ort der Stätte — und hat in der Datei für jede eine `is_in_location`-Kante, alle gleichrangig. Beispiel: Eine SE mit `area=1`, `settore=1` und `ambient=Ambiente 3` hat drei Kanten, zu «1» (Areal, `study`), «1» (Sektor, `study`) und «Ambiente 3» (`functional`), dazu die Kante zum Ort der Stätte, von dem aus die Toponymkette aufsteigt. Die Unterscheidung zwischen primärer und sekundärer Zugehörigkeit (`is_primary`, mit `struttura` an erster Stelle und `toponym` nie primär) gehört zum Modell der Bibliothek, für den Fall, dass man von ihr Gruppen nach Dimension verlangt: In der em.json von pyArchInit gibt es sie nicht.

---

## 5. Round-trip (Import-Tab)

> **Was importiert werden kann**: der Import-Tab liest nun auch **em.json** — aus EMStudio oder von einem StratiGraph-Knoten — und wählt den Leser nach der Dateiendung; eine yEd-`.graphml` wird für ältere Dateien weiterhin angenommen. Das Verfahren unten, SE zwischen Gruppen zu verschieben, betrifft den Weg über yEd/GraphML.

### 5.0 Eine em.json aus EMStudio importieren (auch in eine leere Datenbank)

Eine em.json, die von **EMStudio** (nicht von pyArchInit) geschrieben wurde, lässt sich in die pyArchInit-Datenbank importieren — **auch wenn die Datenbank leer ist** (ab 5.13.121-alpha): Die Stätte, die Perioden, die Datensätze, die Beziehungen und die Medien entstehen aus der Datei, ohne dass zuvor eine Stätte angelegt werden muss.

1. Das Menü **Plugins → pyArchInit - Archaeological GIS Tools** öffnen und den Eintrag **Extended Matrix → Importa em.json…** (em.json importieren) wählen: Das Fenster der Extended Matrix öffnet sich gleich auf dem Tab **Import**, auch wenn die Datenbank keine einzige Stätte enthält. Vom SE-Formular aus gelangt man an dieselbe Stelle: Die grüne Schaltfläche **Esporta Extended Matrix** öffnet, wenn keine Stätte gewählt ist, dasselbe Fenster auf dem Tab Import, statt abzubrechen (der **Export** verlangt dagegen weiterhin eine Stätte).
2. **Browse…** drücken und die em.json wählen.
3. Das Feld **Sito target:** (Zielstätte) prüfen. Ist es leer — der Fall einer Datenbank ohne Stätten —, wird der in der em.json geschriebene Name des Graphen vorgeschlagen (zum Beispiel «Temple») oder, falls er fehlt, der Dateiname ohne «.em.json»; er lässt sich ändern. Steht dort bereits eine Stätte (bei einer Datenbank mit Stätten: die des SE-Formulars, von dem man ausgeht, oder, vom Menü aus, die alphabetisch erste), wird kein Name vorgeschlagen: den Namen der neuen Stätte eintippen oder die Stätte wählen, in die importiert werden soll. Darunter stehen zwei Checkboxen, standardmäßig aktiviert: **Crea periodi mancanti se assenti** (Fehlende Perioden anlegen — wird sie deaktiviert und hat die Stätte die Perioden der Datei noch nicht, bricht der Import mit dem Fehler «MissingEpochError» ab) und **Importa anche i media citati (immagini, video, 3D, documenti)** (Auch die zitierten Medien importieren — Bilder, Videos, 3D, Dokumente). Darunter steht das Feld **Cartella dei file** (Ordner der Dateien), optional, mit der Schaltfläche **Sfoglia…** (Durchsuchen…): Es wird gebraucht, wenn die em.json allein kopiert wurde, fern von den Dateien, die sie zitiert — den Projektordner von EMStudio angeben (den mit `EM/`, `DosCo`, `proxies`, `RB` …).
4. **Anteprima** (Vorschau) drücken: Es wird nichts geschrieben, und die Zusammenfassung sagt, wie viele Datensätze neu, aktualisiert und unverändert sind, wie viele Perioden neu sind und, als Liste, wie viele Datensätze welchen Typs, wie viele Knoten der Datei keine Datensätze werden und wie viele Einheiten ihren **3D-Proxy** haben (ab 5.13.124-alpha; für TempluMare «65 unità su 112 hanno il loro proxy 3D.»: dieselben 65, die EMStudio anzeigt; dort sind es 114 Einheiten, weil auch die 2 Kontinuitätsknoten mitgezählt werden).
5. **Applica** (Anwenden; die Schaltfläche wird nach der Vorschau aktiv) drücken: Der Import läuft, und dieselbe Zusammenfassung erscheint, dazu die der Medien.

Was dabei geschieht, in Kürze:

- **Was zum Datensatz wird.** Nur die Einheiten, deren Typ pyArchInit kennt (US, USM, USD, USVs, USVn, serUSVn, SF, VSF, RSF, USN, USNt …), und die Paradata: Eigenschaften (`property`), Extraktoren (`Extractor`), Kombinierer (`Combinar`) und Dokumente (`DOC`). Ressourcen, Dateien, 3D-Modelle, semantische Formen, Prozesse des digitalen Zwillings, Gruppen, Epochen und die Erzählung werden **nicht** zu Datensätzen: Vor 5.13.121-alpha wurden sie alle zu «US».
- **Die Namen (Feld US).** Der Name des Knotens ohne das Typpräfix: USV105 → 105, D.05 → 05, D.05.02 → 05.02. Eigenschaften mit gleichem Namen (zum Beispiel «height», das bei vielen Einheiten vorkommt) erhalten in Klammern den Namen der Einheit, zu der sie gehören: «height (105)». Würden zwei verschiedene Typen dieselbe Nummer ergeben — der Kombinierer «C.10» und das Dokument «D.10», die US «SU002» und die USD «USD002» —, behält der stärkere Typ (die US, dann die übrigen Einheiten, dann Dokumente, Extraktoren, Kombinierer) die Nummer, und der andere behält den vollständigen EMStudio-Namen («C.10», «USD002»), damit die Beziehungen nicht verwechselt werden.
- **Die Beziehungen.** Zwischen zwei US/USM sind es die gewohnten pyArchInit-Beziehungen («Copre» (überlagert), «Taglia» (schneidet) …), und die Beziehung «kommt nach» (`is_after`: die Einheit ist jünger als die andere, ohne zu sagen, dass sie diese berührt) wird mit dem Pfeil `>` geschrieben (`A > B`: A ist jünger als B), zwischen zwei US wie zwischen allen anderen Typen: Bis 5.13.130-alpha wurde sie zwischen zwei US zu «Copre» (überlagert), einem physischen Kontakt, den die Datei nicht angibt, und der Export machte daraus wieder `overlies` (die neun `is_after` von TempluMare). Zwischen Einheiten verschiedenen Typs werden die physischen Beziehungen ausgeschrieben («Taglia», «Si appoggia a» (lehnt an)), und die Paradata-Kette — Einheit → Eigenschaft → Extraktor oder Kombinierer → Dokument sowie der Fund «Teil von» einem virtuellen Fund — mit `>>`. Perioden, Aktivitäten, Gruppen und Ressourcen sind keine Beziehungen. Beim Export werden aus diesen Zeichen wieder die Kanten der Extended Matrix (`is_after`, `has_property`, `has_data_provenance`, `extracted_from`, `combines`, `is_part_of`). Jede Beziehung wird auf **beiden** Datensätzen geschrieben, auf dem zweiten umgekehrt — «Copre»/«Coperto da» (überlagert/wird überlagert von), «Taglia»/«Tagliato da» (schneidet/wird geschnitten von), `>`/`<`, `>>`/`<<` —, wie es die Beziehungsprüfung des SE-Formulars verlangt; ein Datensatz ohne Beziehungen hat eine leere Liste, kein leeres Feld. Vor 5.13.125-alpha lieferte die Prüfung «malformed node or string: None» und «Rapporto reciproco non trovato» (reziproke Beziehung nicht gefunden).
- **Aktivität und Beschreibung.** Die Aktivität des Knotens (die Gruppe ActivityNodeGroup) kommt in das Feld **Aktivität** des Datensatzes, die Beschreibung des Knotens in das Feld **Beschreibung**.
- **Periodisierung.** Die Epochen aus EMStudio, die nur einen Namen und Daten haben, werden in der Periodisierung der Stätte über den Namen wiedergefunden; fehlende werden zu neuen Perioden, von der ältesten an, nummeriert nach der letzten Periode der Stätte, in Phase 1, mit Anfangs- und Enddatum und dem Namen als erweiterter Datierung. Jede Einheit übernimmt Anfangsperiode und -phase von der Epoche, in der sie entsteht, und Endperiode und -phase von der letzten Epoche, in der sie fortbesteht (oder dieselben wie die anfänglichen). Perioden ohne **Periodencode** erhalten ihn der Reihe nach, 1, 2, 3…, in der Reihenfolge von Periode und Phase; jede Einheit übernimmt die **Datierung** ihrer Anfangsperiode und den **Periodencode**, wie ihn «Crea codice periodo» (Periodencode erstellen) schreibt — zum Beispiel 1/2/3 für eine Einheit, die von Periode 1 bis 3 besteht —, falls sie beides nicht schon hat (ab 5.13.125-alpha).
- **Stättendatensatz.** Existiert die Stätte nicht, wird sie angelegt. Die **Definition** ist das Kulturgut, von dem die Studie handelt, wenn die em.json es angibt, sonst der Name des Graphen (für TempluMare «Temple»); **Staat, Region, Provinz und Gemeinde** stammen aus der Ortskette der em.json, sofern es eine gibt. Alle fünf werden auch im **Thesaurus** abgelegt (Fundort-Formular, Codes 1.1–1.5), aus dem das Fundort-Formular sie liest. Die Beschreibung wird aus dem Graphen entnommen: Name, Code, Autoren und Position (EPSG und Ursprung). Existiert die Stätte bereits, wird nur ausgefüllt, was leer ist, und die Definition «Extended Matrix», die Versionen vor 5.13.125-alpha geschrieben haben, wird ersetzt.
- **Medien.** Entlang der Verknüpfungen der em.json — Datensatz → Ressource → Datei, Datensatz → 3D-Modell → Ressource → Datei sowie die URL des Dokuments oder des Extraktors — werden die zitierten Dateien zu Medien des Datensatzes. Gesucht wird so, wie EMStudio sucht: im Ordner der em.json und im Baum ihres EM-Projekts (`EM/`, `EM/DosCo`, `EM/proxies`, `RB`, `RM`, `SB`), dazu im Ordner des Feldes **Cartella dei file**, falls er angegeben wurde. Es zählen Bilder, Videos, 3D-Modelle (auch **GLB** und **GLTF**) und Dokumente (**PDF, Word, Excel, ODT, ODS, RTF, CSV, TXT**). Das Medium verweist auf die **Originaldatei**, wie die über den Datensatz hinzugefügten; das Vorschaubild und die Kopie kommen in die Ordner **Thumbnail path** und **Image resize** der Konfiguration (Tutorial 01): 3D-Modelle haben ihre eigene Ansicht, PDFs die erste Seite, die übrigen Dokumente ein Symbol mit dem Typ. Der **3D-Proxy** einer Einheit — im Graphen hängt er an deren Eigenschaft «geometry» — wird dem Datensatz der Einheit zugeordnet. Wird die Eigenschaft von mehreren Einheiten geteilt — eine USV, die die Geometrie der US erbt, die sie ergänzt —, geht der Proxy an die Einheit, die die Eigenschaft erzeugt hat, wie in EMStudio (vor 5.13.124-alpha ging er an die erste in der Datei gefundene Einheit). Die Zusammenfassung sagt, wie viele Medien neu sind und welchen Typs, wie viele schon vorhanden waren, wie viele Vorschaubilder, wie viele zitierte Dateien nicht gefunden wurden (mit dem Rat, den Projektordner anzugeben), wie viele Kopien leer sind (Cloud-Platzhalter, die erneut heruntergeladen werden müssen), wie viele externe Verweise (Web, Netzwerk, Cloud) Adressen bleiben und welche Dateien keine Medien sind (`.blend`, `.mtl`, `.zip` …). Eine in einem Bucket archivierte Datei, die auch eine Kopie auf der Festplatte hat (in der em.json mehrere Adressen für dieselbe Ressource), wird aus der Kopie auf der Festplatte importiert; vor 5.13.124-alpha blieb sie ein externer Verweis. Ein zweiter Import dupliziert nichts. Vor 5.13.122-alpha wurden die Dateien in den Hauptordner von pyArchInit kopiert, GLBs hatten kein Vorschaubild (und der Datensatz zeigte sie nicht), die Proxys hingen an der Eigenschaft statt an der Einheit, und PDFs blieben außen vor. Ab 5.13.127-alpha werden die Ansichten der 3D-Modelle alle zusammen in einem eigenen Python-Prozess außerhalb von QGIS gezeichnet: vorher schloss sich QGIS unter macOS von selbst, sobald die Zusammenfassung des Imports geschlossen wurde.
- **Erneut importieren.** Dieselbe Datei erneut zu importieren verdoppelt weder Perioden noch Datensätze: Bereits vorhandene erscheinen als «invariate» (unverändert) oder «aggiornate» (aktualisiert), und wo Datenbank und Datei voneinander abweichen, gewinnt die Datei (die Zusammenfassung zählt sie als «conflitti», Konflikte). Die Vorschau zählt auch die Datensätze als «aggiornate», denen der Import Beziehungen, Datierung oder Periodencode hinzufügt (zuvor erschienen sie als «invariate»). Die em.json erneut in eine Datenbank zu importieren, die vor 5.13.125-alpha importiert wurde, repariert sie: Definition der Stätte, Beziehungen auf beiden Datensätzen, Datierung und Periodencodes.
- **Die em.json wird gemerkt.** pyArchInit hält in seinen Tabellen die Einheiten, die Paradata, die Beziehungen und die Epochen; alles Übrige des Graphen — Ressourcen, Dateien, Modelle, semantische Formen, Prozesse des digitalen Zwillings, Gruppen von Paradata und von Aktivitäten, Autoren, Lizenzen, die Erzählung — wird zusammen mit dem Titel, dem **Studiencode** (zum Beispiel GT16: Es ist das Präfix, mit dem Blender die Proxys wieder anhängt), der Georeferenzierung (EPSG und Verschiebungen) und den Namen aus EMStudio beim Import gemerkt (Tabelle `pyarchinit_em_sources`, eine Zeile pro Stätte; der letzte Import gewinnt). Beim **Export** der em.json der Stätte kommt all das zurück: die Originalnamen (SU006, D.07.08, height …) für die Datensätze, die noch die beim Import vergebene Nummer haben — ein in pyArchInit umbenannter Datensatz behält den neuen Namen —, die Daten der Knoten (zum Beispiel die Eigenschaft «geometry» mit ihrer Form, aus der EMStudio die Proxys zählt) und die Knoten, die keine Datensätze sind, mit ihren Kanten, angehängt an die Datensätze, die noch existieren: Ein Zweig, der ohne Datensatz geblieben ist (zum Beispiel die Form einer gelöschten Eigenschaft), kommt nicht zurück. Beziehungen, Perioden und Beschreibungen stammen immer aus der Datenbank. Die Meldung am Ende des Exports sagt, wie viel zurückgekommen ist, zum Beispiel «Dall'em.json importato tornano 851 nomi, 1090 nodi e 1969 archi, codice dello studio GT16.» (Aus der importierten em.json kommen 851 Namen, 1090 Knoten und 1969 Kanten zurück, Studiencode GT16). Getestet an TempluMare_v3.2 (1946 Knoten): kein Name und keine Beschreibung weicht vom Original ab, und in EMStudio haben 65 von 114 Einheiten den Proxy und 2 von 3 Epochen ein Modell, wie im Original. Unterschiedlich bleiben die 9 «kommt nach»-Beziehungen zwischen zwei US, die pyArchInit «Copre» schreibt, und die Ortsgruppen der Stätte und des Areals mit der Studie, die pyArchInit hinzufügt.

### 5.0.1 Das EM-Projekt für EMStudio exportieren, mit seinen Dateien

Ab **5.13.131-alpha**. Die em.json, die pyArchInit in `pyarchinit_EM_folder` schreibt, enthält die Pfade der Dateien (`proxies/SU002.glb`, `DosCo/D.05 ….pdf`, `../RB/…`), aber nicht die Dateien: Von dort aus geöffnet, findet EMStudio weder die Proxys noch die Dokumente. Der Menüpunkt **Extended Matrix → Esporta progetto EM per EMStudio…** (EM-Projekt für EMStudio exportieren) legt den Ordner eines vollständigen EM-Projekts an, mit dem Standardbaum der Bibliothek s3dgraphy — dem, in dem EMStudio die Dateien sucht:

```
<Projekt>/
  EM/            die em.json
    DosCo/       die Dokumente (D.01, D.02.03 …)
    proxies/     die 3D-Proxys der Einheiten (<Einheit>.glb)
  RB/            die Vermessung (LOD0, LOD1 …, Texturen, Kacheln)
  SB/            die aus den Quellen gewonnenen Modelle
  RM/            die Repräsentationsmodelle
```

1. Die **Stätte** wählen.
2. Den **Projektordner** wählen. Ist er leer oder bereits ein EM-Projekt (er enthält einen Ordner `EM/` oder ist selbst der Ordner `EM/` eines Projekts), ist er das Projekt; andernfalls — der Schreibtisch, ein Ordner mit anderen Dateien — legt pyArchInit darin einen neuen Ordner mit dem Namen der Stätte an (zum Beispiel `Temple/`). Der gewählte Ordner wird für das nächste Mal gemerkt.
3. pyArchInit exportiert die Stätte wie **Esporta sito in em.json…** (Stätte nach em.json exportieren) — in den Arbeitsordner `pyarchinit_EM_folder`, also mit der im Panel vorbereiteten Erzählung (§10.8) — und kopiert die em.json nach `EM/`. Dann kopiert es daneben, unter dem Pfad, den die em.json angibt, **jede zitierte Datei, die die Datenbank kennt**: die mit der em.json importierten Medien (§5.0). Eine nur mit ihrem Namen zitierte Datei — die URL der Dokumente und der Extraktoren, die EMStudio aus `DosCo` nimmt — kommt nach `EM/DosCo/`. Ist das Original nicht erreichbar (externe Festplatte nicht angeschlossen), wird die Datei aus dem Ordner **Image resize** genommen, wenn dort dieselbe Datei liegt (3D-Modelle und PDFs, unverändert kopiert); ein Bild dagegen nicht: Dort ist es als PNG verkleinert und nicht mehr die zitierte Datei. Ein Fortschrittsbalken zählt die Dateien.
4. Die Zusammenfassung sagt, wie viele Dateien kopiert wurden und wie viele schon vorhanden waren und **wie viele Ressourcen der em.json EMStudio vom Projekt aus findet** — gezählt vom Resolver der Bibliothek, demselben, den EMStudio verwendet —; sie nennt, nach Ordnern, die zitierten Dateien, die die Datenbank nicht hat und die von Hand aus dem Originalprojekt zu kopieren sind, sowie die kopierten Dateien, deren **sha256** nicht die in der em.json geschriebene ist. **Details einblenden…** listet sie einzeln auf. Die Schaltflächen: **Apri in EMStudio** (In EMStudio öffnen: öffnet die em.json des Projekts), **Apri la cartella** (Ordner öffnen), **Chiudi** (Schließen).

Ein erneuter Export in denselben Ordner kopiert nicht noch einmal, was schon da ist, und **überschreibt keine Projektdatei, die von der Fassung der Datenbank abweicht** (es kann in EMStudio geleistete Arbeit sein): Die Zusammenfassung meldet es («lasciati come sono», so belassen, wie sie sind); wer eine solche Datei ersetzen will, löscht sie und exportiert erneut. Die vorherige em.json bleibt, wenn sie abweicht, daneben als `<Stätte>.em.json.bak` erhalten.

Bei TempluMare (der Datenbank des Imports aus §5.0, mit nicht angeschlossener externer Festplatte): 96 Dateien kopiert (238,7 MB: die 65 Proxys und 31 Dokumente, alle mit der in der em.json geschriebenen sha256); EMStudio findet vom Projekt aus 96 der 536 Ressourcen; von Hand zu kopieren bleiben die 343 Dateien, die die Datenbank nie hatte — die Vermessung in `RB/` (158) und die Modelle in `SB/` (175), die keine Medien sind, die `.blend`-Dateien eingeschlossen —, dazu die 10 JPG-Fotos von `DosCo`, die bei angeschlossener Festplatte aus den Originalen kopiert werden.

Es folgt der Weg über yEd/GraphML, um Einheiten zwischen Gruppen zu verschieben.

Um die SQL-Datenbank durch das Verschieben von SE zwischen Gruppen im GraphML zu aktualisieren:

1. GraphML in **yEd** öffnen
2. Eine SE in eine andere Gruppe ziehen, speichern
3. Zurück zum Dialog → Tab **"Import"**
4. **Anhaken** der Checkbox *"Update SQL on import (struttura/area/...)"*
5. Modifizierte GraphML laden

Das System läuft als atomare Transaktion: Bei Fehlern **vollständiges Rollback** (DB bleibt unverändert). `adhoc`-Gruppen schreiben nie SQL — sie aktualisieren nur `groups_<site>.graphml`.

Ab 5.6.0-alpha ist der Import-Walker **rekursiv** und unterstützt verschachtelte Folder (z. B. Toponymkette `nazione > regione > provincia > comune > SE`). Bei Zyklen im Folder-Graph wird `CycleDetectedError` ausgelöst und der Import mit Rollback abgebrochen.

---

## 6. CLI (Alternative zum Dialog)

Für Skripte / Batch:

```bash
# Export
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Liste der Ad-hoc-Gruppen
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Autor hinzufügen
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit-Codes: 0 = Erfolg, 1 = Bridge-Fehler, 2 = argparse-Fehler.

---

## 7. Fehlerbehebung

| Symptom | Ursache | Lösung |
|---|---|---|
| "no such column: node_uuid" | Phase-1-Migration nicht durchgeführt | QGIS neu starten, DB erneut öffnen |
| Leeres GraphML | DB ohne rapporti / Area-Filter zu eng | us_table.rapporti prüfen |
| "rapporti müssen TEXT sein" | Zahl als Integer eingegeben | SE/Area-Felder sind **TEXT**, nicht Integer |
| Falsche Großschreibung in rapporti | Kleines "copre" in DB | "Copre", "Coperto da" groß schreiben |
| `DeprecationWarning` bei 5.5.x-Datei | Legacy-Datei mit `ActivityNodeGroup + group_kind` | Der Projector promoviert sie in-memory zu `LocationNodeGroup`. Erneut exportieren, um die Datei auf der Festplatte zu migrieren. |
| Swimlane-Zeilen zeigen einen sehr langen Text | Ältere Versionen verwendeten die Descrizione der Periodisierung als Beschriftung | Plugin aktualisieren und erneut exportieren und/oder **Datazione estesa** mit einem kurzen Namen füllen |
| Swimlane-Epochen in falscher Reihenfolge (z. B. Bronzezeit über der Spätantike) | Die Zeilen werden nach **Anfangschronologie** sortiert; als positive Zahlen eingegebene v. Chr.-Jahre (1650 statt -1650) werden wie n. Chr. sortiert | Im Periodisierungsformular v. Chr.-Jahre als negative Zahlen eingeben und erneut exportieren. Die Export-Zusammenfassung zeigt jetzt eine Warnung "⚠️ Periodizzazione: ..." mit der Liste der zu korrigierenden Perioden |
| EMStudio öffnet die exportierte em.json, findet aber weder die 3D-Proxys noch die Dokumente | Die em.json in `pyarchinit_EM_folder` enthält die Pfade der Dateien, nicht die Dateien | Mit **Extended Matrix → Esporta progetto EM per EMStudio…** (§5.0.1) exportieren und die em.json des Projekts öffnen |

---

## 8. Technische Dokumentation

Für Architektur, Designentscheidungen und Roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Aufgeschobene Carry-Overs:
- **AI08-F3**: Auto-Layout-Heuristiken (Sub-Group-Bin-Packing) — weiterhin aufgeschoben
- **AI09**: TimeBranchNodeGroup-Mapping — Zukunft
- **Phase 3**: SyncEngine + REST API — Zukunft
- **Phase 4**: GraphDBBackend + SPARQL — Zukunft

Ausgeliefert:
- **AI07** (5.6.0-alpha, 2026-05-10): `LocationNodeGroup`-Migration mit `kind`-Enum + Toponymkette + mehrdimensionale Mitgliedschaften
- **AI08-F1** (in AI07 zusammengeführt): natives hierarchisches Nesting via `is_primary`

---

## 5. yEd-aware Import — extern erstellte GraphMLs importieren (5.8.x)

Ab **5.8.0-alpha** ist die Bridge **auch für GraphMLs bidirektional, die direkt in yEd erstellt wurden** (also ohne vorherigen pyarchinit-Export). Pyarchinit erkennt automatisch „yEd-raw"-GraphMLs — also solche ohne `pyarchinit.*`-Data-Keys — und importiert sie über einen eigenen Dispatch, der Node-Label-Präfixe auf stratigrafische Typen abbildet, TableNode-Zeilen als Perioden erkennt, Group-Folder als archäologische Dimensionen durchläuft und Sie zwischen verschiedenen Policies für Folder-berührende Edges wählen lässt.

### 5.1 Rollout in 6 Meilensteinen

| Meilenstein | Tag | Inhalt |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — Flavour-Flag `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — `ClassificationKind`-Enum mit 13 Werten (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + order-sensitive Regex |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate aus TableNode-Zeilen) + `yed_group_walker.py` (FolderCandidate mit Auto-Dimension aus Label-Präfix: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — Orchestrator `import_yed_raw()` + 5 Write-Funktionen + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + Paradata via `ParadataStore` + `_DryRunRollback`-Sentinel + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` mit 5 Seiten (classifier / periods / folders / policy / preview) + `YedOverrides`-Dataclass + Sidecar-Persistenz `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Diese Dokumentation + Dev-Log + CHANGELOG. |

### 5.2 So funktioniert es — Benutzer-Flow

1. **Öffnen Sie eine GraphML in QGIS über das Menü Import GraphML** (gleicher Pfad wie der bestehende pyarchinit-projected-Flow).
2. Pyarchinit erkennt automatisch, dass es sich um yEd-raw handelt (keine `pyarchinit.*`-Keys) → dispatcht in den neuen Branch, statt auf den Legacy-Pfad zurückzufallen.
3. Der Wizard `YedImportDialog` öffnet sich mit **5 Seiten**:
   - **1/5 Classifier** — Tabelle mit einer Zeile pro Leaf-Node. Jede Zeile zeigt `label` + `auto_kind` (z. B. `us_real` / `usv_virtual` / `property`) + eine Override-Combobox `user_kind`. Die Schaltfläche **Auto übernehmen** setzt alle Zeilen auf ihr `auto_kind` zurück (Overrides löschen).
   - **2/5 Periods** — eine Zeile pro geparster TableNode-Zeile, editierbare Spalten `periodo` + `fase`. Datumsangaben (`datazione_iniziale`/`finale`) bleiben leer: yEd-raw-GraphMLs enthalten keine Daten.
   - **3/5 Folders** — eine Zeile pro Group-Folder. Combobox für `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` zum Ausschließen). `value` editierbar (Default = `auto_value` aus dem Label-Präfix abgeleitet).
   - **4/5 Rapporti policy** — 4 Radio-Buttons für die Behandlung von Folder-berührenden Edges:
     - **SKIP** (Default): Folder-berührende Edges verwerfen. Leaf-to-Leaf-Edges bleiben unverändert.
     - **FAN_OUT**: Eine Edge `folder_A → folder_B` wird auf `N×M` Leaf-Paare expandiert (kartesisches Produkt der Mitglieder).
     - **REPRESENTATIVE**: Das erste Mitglied jedes Folders dient als Proxy.
     - **SYNTHETIC**: Pro Folder wird eine us_table-Zeile angelegt (`unita_tipo='VA'`, virtual activity) + Edges werden über diese Anker umgeleitet.
   - **5/5 Preview** — Dry-Run von `import_yed_raw(overrides=..., dry_run=True)`. Zeigt Counts (us / inv / period / paradata) **ohne Commit**. Klick auf **Finish** committet, **Cancel** bricht ab.
4. Bei **Finish** speichert der Wizard Ihre Overrides in einer **Sidecar-JSON** `<graphml>.yed_overrides.json` neben der Datei. Beim erneuten Öffnen derselben GraphML wird das Sidecar vorab geladen, sodass Ihre vorherigen Overrides bereits angewandt sind.

### 5.3 Destination Routing

Der Dispatch nutzt `_classify_destination` (in `yed_import_pipeline.py`), um jedes Leaf zuzuordnen:

| ClassificationKind | Ziel | Hinweis |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | aus Label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | aus `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | aus `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | aus `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` aus Label-Präfix abgeleitet: USVs/USVn/USVc) | aus `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | aus `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | aus `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | aus `^VSF\d+` |
| DOCUMENT | `paradata` | aus `^D\.\d+` |
| COMBINER | `paradata` | aus `^C\.\d+` |
| PROPERTY | `paradata` | Label-Keyword (`material`/`position`/`width`/...) |

**Nutzerentscheidung 2026-05-13**: USV* (virtuelle) sind „unità tipo" (weiterhin stratigrafische Einheiten) und gehören in `us_table`, nicht in Paradata. Nur DOC/COMB/PROP/VIRTUAL_FIND bleiben in Paradata.

### 5.4 Sidecar JSON — Schema

Versioniert für Forward-Compatibility:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Nur vom Benutzer GEÄNDERTE Felder werden persistiert (Diff). Unbekannte `ClassificationKind`-Werte (z. B. aus zukünftigen s3dgraphy-Releases) werden beim Laden stillschweigend übersprungen.

### 5.5 CLI für skriptgesteuertes Ingest

Für CI / Batch-Re-Runs:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` für SQLite- vs. PostgreSQL-Backend. `--overrides` ist optional (keine Overrides = yE-D-Defaults). `--auto-defaults` ist ein No-op-Flag für Forward-Compat.

### 5.6 Bekannte Einschränkungen

- **Keine Datumsbearbeitung im Wizard**: yEd-raw-GraphMLs enthalten keine `datazione_iniziale`/`datazione_finale`. Die Periods-Seite editiert nur `periodo` + `fase` (FK-Ziele).
- **Teilweise ParadataStore-API**: Upstream-s3dgraphy liefert die Methoden `add_virtual_us` / `add_document` / `add_combiner` / `add_property` noch nicht. yE-D loggt „skip — method missing" pro Paradata-Leaf, zählt die Versuche aber in der Vorschau.
- **PropertyNode → Path B (kein US-Linkage)**: PROPERTY-Nodes werden ohne Ziel-US geschrieben. Der Wizard gibt eine Warnung aus. Zukunft: yE-Closure-Follow-up, um „assign target" in der UI zu ergänzen.
- **Multi-DB**: Die Sidecar-JSON ist pro GraphML, nicht pro DB. Wenn Sie dieselbe GraphML in verschiedene DBs importieren, gelten dieselben Overrides für beide.

### 5.7 Finale Test-Coverage

| Suite | Test | Coverage |
|---|---|---|
| yE-A | `test_yed_detector.py` | Flavour-Detection |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + order-sensitive Regex |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | PeriodCandidate + FolderCandidate Parse |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 inkl. 2 L1 Overrides e2e) | Policies + Write-Funktionen + Dispatch |
| yE-E | `test_yed_import_dialog.py` (5 Sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | Sidecar-Persistenz + CLI |

**Gesamt-Suite nach Rollout**: 354 passed / 42 skipped (PG-L1 benötigt psycopg2).

### 5.8 Update 5.8.5-alpha (yed-fastfix)

Verhaltens-Fixpack auf Basis von `5.8.3-alpha`, das die Qualität des GraphML-Re-Exports nach einem yEd-aware-Import verbessert. Für Endanwender relevante Änderungen:

- **Multi-Folder-Paradata**: DOC- / Combinar- / Extractor- / Property-Labels, die zwischen yEd-Foldern geteilt werden (z. B. `material`, referenziert aus VA01 + VA04 + VA05), erzeugen jetzt EINE Zeile in `us_table` PRO Vorkommen — Multi-Folder-Sichtbarkeit im re-exportierten GraphML wiederhergestellt. Trade-off: Identitäts-Dedup (`D.01` / `D.01-2` / `D.01bis` werden zu einer einzigen Zeile zusammengefasst) gilt nicht mehr für das zweite/dritte Vorkommen.
- **Reziproke Rapporti**: jede yEd-Edge `a → b` schreibt den Vorwärts-Rapporto in die Zeile von `a` UND die Umkehrung in die Zeile von `b` (`<<` / „Coperto da" / usw.). DOCs zeigen jetzt alle eingehenden Extractor-Verbindungen im Scheda-US-Formular.
- **Stripping des numerischen `us`-Präfixes**: `US100` → `us='100'` `unita_tipo='US'` (vorher `us='US100'`). SF/VSF/RSF werden dual nach `us_table` + `inventario_materiali` geschrieben.
- **Periodo/Fase Auto-Fill**: Die Zugehörigkeit einer yEd-TableNode-Row zu einer Periode propagiert in `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **BPMN-aware Classifier**: `D.NN` (BPMN-Data-Object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — bewahrt die semantische EM-1.5-Unterscheidung.
- **Idempotenter Re-Import**: Erneutes Ausführen desselben Imports überspringt bereits vorhandene Zeilen; kein Rollback bei UNIQUE-Kollision beim wiederholten Lauf.
- **USV-Palette**: USV-Nodes werden jetzt mit dem EM-kanonischen blauen Parallelogramm dargestellt (vorher Rechteck mit rotem Rand).

### 5.9 yE-F Mehrordner-Paradata (5.9.0-alpha)

Strukturelle Weiterentwicklung von `yed-fastfix-5.8.5-alpha`: Der Trade-off von Bug R B1 (eine `us_table`-Zeile pro Vorkommen, mit `us='D.01_2'` / `us='D.01_3'`) wurde abgelöst. Ein Paradata-Leaf (DOC / Combinar / Extractor / property), das von mehreren yEd-Foldern geteilt wird, erzeugt nun **eine einzige Zeile** in `us_table` pro kanonischem Label, und die Mehrfach-Zugehörigkeit wird in einer neuen Spalte `other_locations` bewahrt.

Für Endanwender sichtbare Änderungen:

1. **Neues Widget „Weitere Aktivitäten" im US/USM-Formular**: Im Tab *Periodizzazione* erscheint ein `QListWidget` mit dem Label „Weitere Aktivitäten" — sichtbar **nur**, wenn `unita_tipo` eine Paradata-Tipologie ist (`DOC`, `Combinar`, `Extractor`, `property`). Der Anwender kann mehrere Activity-Codes auswählen; die Auswahl wird als JSON-Liste in der neuen Spalte `other_locations` serialisiert.
2. **Neuer QGIS-Menüeintrag**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Muss **einmal** auf jeder bestehenden DB ausgeführt werden, um die neue Spalte hinzuzufügen (DBs, die nach 5.9 erstellt wurden, haben die Spalte bereits).
3. **Verbesserter yEd-aware Import**: Ein Paradata-Leaf, das in N yEd-Foldern auftritt, erzeugt jetzt **nur 1** `us_table`-Zeile (keine N Zeilen mehr mit Suffix `_2`/`_3` wie in 5.8.5). Der erste angetroffene Folder wird zur primären `attivita`; sekundäre Folder werden in `other_locations` gelistet. Beim **Export** werden N visuelle yEd-Kopien erzeugt (eine pro Folder), alle mit derselben kanonischen `node_uuid`, um die Round-Trip-Identität zu garantieren.

**Rückwärtskompatibilität**: Daten, die durch Bug R B1 in 5.8.5-alpha erzeugt wurden (Zeilen mit Suffix `_2`/`_3`), bleiben ohne automatische Konvertierung lesbar. Die neue Logik gilt für neue Imports; Legacy-Zeilen verhalten sich weiterhin wie zuvor.

Vorgänger: siehe Abschnitt 5.8 (`yed-fastfix-5.8.5-alpha`) für das abgelöste Verhalten.

---

## 6. Kontinuität generieren (CON-Datensätze)

Im Panel **„Verifica rapporti"** — verfügbar als Tab innerhalb des s3dgraphy-Import-/Export-Dialogs — befindet sich die Schaltfläche **„Genera continuità"** (Label wie im Plugin auf Italienisch belassen). Für die aktuell ausgewählte Fundstelle erzeugt diese Funktion automatisch die **Kontinuitäts-Datensätze** der US/USM, deren Lebensdauer sich über mehr als eine Periode erstreckt.

### 6.1 Was sie tut

1. Sie durchsucht alle US/USM der Fundstelle, bei denen **Anfangsperiode ≠ Endperiode** ist (deren Leben sich also über mehrere Perioden erstreckt).
2. Für jede erzeugt oder aktualisiert sie einen Kontinuitäts-Datensatz mit dem Namen **`CON_<us>`** (z. B. `US5` → `CON_US5`).
3. Der CON-Datensatz **erbt** von der Mutter-Einheit: Fundstelle, Area (plus etwaige sekundäre Areas), Struktur und die gesamte Periodenspanne (Anfang → Ende). Seine Beschreibung wird automatisch generiert.
4. Sie schreibt eine **reziproke Kontinuitäts-Beziehung** auf beiden Seiten: auf dem CON und auf der Mutter-Einheit.

> **Die Phase zählt für sich nicht.** Die Regel schaut auf die **Periode**: eine USM von **2/3 bis 2/4** — gleiche Periode, nur die Phase wechselt — erzeugt nichts. Wenn Ihre Einheiten von Phase zu Phase innerhalb derselben Periode weiterleben, aktivieren Sie **„anche i salti di fase"** („auch Phasensprünge") neben der Schaltfläche: dann zählen auch diese Sprünge, sofern **beide** Phasen ausgefüllt sind. Eine Einheit, die sich nicht bewegt — gleiche Periode und gleiche Phase — ist nie eine Kontinuität. Das Feld ist zunächst **nicht** aktiviert und gilt für die Vorschau und das Schreiben gemeinsam.

### 6.2 Idempotenz

Der Vorgang ist **idempotent**: Ein erneuter Lauf dupliziert vorhandene Datensätze nicht — er aktualisiert die bestehenden `CON_<us>`, wenn sich die Daten der Mutter-Einheit geändert haben.

### 6.3 Dry-Run-Vorschau und Backup

Vor dem Schreiben wird eine **Dry-Run-Vorschau** mit den Zählungen angezeigt: wie viele Datensätze zu **erstellen**, zu **aktualisieren**, **unverändert** sind und wie viele **verwaist** sind. Änderungen werden **erst nach Bestätigung** angewendet (Schaltfläche „Genera"). Beim Anwenden wird zuvor automatisch ein **Datenbank-Backup** erstellt.

Ein CON-Datensatz ist **verwaist**, wenn seine Mutter-Einheit sich nicht mehr über mehrere Perioden erstreckt (z. B. wurden Anfangs- und Endperiode gleichgesetzt). Standardmäßig werden Verwaiste nur **markiert**; eine **Checkbox** („Rimuovi anche le CON orfane") erlaubt es, sie zu entfernen.

**Eine von Hand angelegte Kontinuität wird erkannt.** Ein CON-Datensatz, dessen Beziehungen eine einzige Einheit nennen — `> 12` oder „Kontinuität nach 12“ — ist die Kontinuität dieser Einheit, wie auch immer er heißt: der Generator **aktualisiert** ihn (Periodenspanne, kanonisches Label), und der Name bleibt seiner. Es entsteht keine zweite: Kontinuität ist **eine je Einheit**. Existiert zusätzlich eine kanonische `CON_<us>`, gewinnt diese, und die andere bleibt eine von Hand zu entscheidende Waise.

### 6.4 Im Extended-Matrix-Export

Die so erzeugten `CON_<us>`-Datensätze erscheinen in der **em.json** der Extended Matrix als **Kontinuitäts-Elemente** (der GraphML-Export ist im Ruhestand, §2.3).

---

## 7. Prüfung zeitlicher (stratigrafischer) Widersprüche

Im Bereich **"Verifica rapporti"** (Beziehungsprüfung — ein Reiter des s3dgraphy-Import-/Export-Dialogs) meldet die Prüfung nun auch **zeitliche Widersprüche**: wenn die einer Einheit zugewiesene Periode/Phase der beobachteten Stratigrafie widerspricht. Die Stratigrafie ist das Referenzdatum, daher verschieben die automatischen Korrekturen die **Perioden**, nicht die Beziehungen.

### 7.1 Was sie erkennt
- **Zeitliche Umkehrung**: zwei datierte Einheiten, die durch eine Ordnungsbeziehung verbunden sind (z. B. US5 «überdeckt» US7), bei denen die stratigrafisch jüngere Einheit nach Periode vollständig **älter** ist.
- **Inkonsistente Gleichzeitigkeit**: Einheiten, die als gleichzeitig deklariert sind (physische Gleichheit / Bindung), aber mit **disjunkten** chronologischen Intervallen.
- **Nicht bewertbar**: eine Ordnungsbeziehung, bei der mindestens eine der beiden Einheiten keine datierbare Periode hat (nur gemeldet, keine Korrektur).

Hinweis zur Grenze: zwei **benachbarte Perioden, die sich** an einem einzigen chronologischen Punkt **berühren**, gelten als überlappend → sie sind **kein** Widerspruch (im Zweifel zugunsten).

### 7.2 Automatische Korrektur und Vorschläge
- Wenn eine einzige Verschiebung den Konflikt löst, schlägt die Prüfung vor, die **Einzelperioden**-Einheit zu verschieben, die im Konflikt mit der Mehrheit ihrer Nachbarn steht, wobei die Periode mit der geringsten Verschiebung gewählt wird; bei Gleichzeitigkeiten mit einer nicht datierbaren Einheit kopiert sie die Periode des datierten Nachbarn.
- In mehrdeutigen Fällen — Gleichstand, **Mehrperioden**-Einheiten (z. B. CON-Datensätze), keine gültige Periode — korrigiert sie nicht automatisch: sie liefert einen **«Was + Wie»-Vorschlag** (z. B. «Verschiebe US5 auf eine Periode ≥ 3, oder US7 auf eine Periode ≤ 1, oder überprüfe die Beziehung»).

### 7.3 Vorschau und Backup
- Die **Vorschau** zeigt die vorgeschlagenen Periodenänderungen vor ihrer Anwendung.
- Vor dem Schreiben der Perioden wird ein **automatisches Datenbank-Backup** durchgeführt (SQLite und PostgreSQL).
- Führe die Prüfung nach der Anwendung erneut aus, um etwaige verbleibende Widersprüche zu kontrollieren.

---

## 8. Prüfung der Chronologie (Periodisierung und Formulare)

Im selben Bereich **"Verifica rapporti"** (Beziehungsprüfung — ein Reiter des s3dgraphy-Import-/Export-Dialogs) findet und korrigiert die Prüfung seit Version 5.13.64-alpha auch **Chronologieprobleme** des ausgewählten Fundorts. Die Prüfung zeitlicher Widersprüche (Abschnitt 7) vergleicht die Periode einer Einheit mit der Stratigrafie; diese Prüfung vergleicht die Periodisierung mit sich selbst und mit den SE-Formularen, die sie kopieren.

### 8.1 Was sie erkennt

Der Baum im Bereich gruppiert die Probleme nach Art. Neben den Beziehungsgruppen erscheinen vier neue Gruppen:

| Gruppe | Was gemeldet wird | Behandlung |
|--------|-------------------|------------|
| **Phasen mit überlappenden Intervallen** | Zwei Zeilen der Periodisierung, deren Jahresintervalle sich schneiden | Manuell: Der Bereich schlägt eine Einengung nur vor, wenn nach der Einengung ein nutzbares Intervall übrig bleibt |
| **Abweichende Datierung des Formulars** | Das Feld `datazione` des SE-Formulars sagt etwas anderes als die `datazione_estesa` der zugehörigen Periode/Phase | Automatisch: Die Periodisierung ist die Quelle, das Formular die Kopie; die Kopie wird also aus der Quelle neu geschrieben. Ein leeres Feld wird auf dieselbe Weise gefüllt. Eine SE ohne Periode wird übersprungen, weil es nichts zu kopieren gibt |
| **Periodisierung mit Beginn nach dem Ende** | `cron_iniziale` größer als `cron_finale` | Manuell: wahrscheinlich v. Chr.-Jahre ohne Minuszeichen — der Bereich schlägt vor, beide Jahre negativ zu schreiben (`-1650` statt `1650`); handelt es sich dagegen um einen Tippfehler, die beiden Werte von Hand tauschen |
| **Phase ohne Jahre** | Eine Phase, deren Jahre fehlen oder nicht lesbar sind | Nur gemeldet: Es gibt nichts, wovon sie geerbt werden könnten |

Ein Beispiel zu den Überlappungen. In der Beispieldatenbank gibt es zwei, und keine der beiden hat einen Vorschlag: Die beiden Phasen haben **identische** Intervalle, und jede Einengung würde eine Phase enden lassen, bevor sie beginnt. Der Bereich teilt dies nur mit; die Entscheidung (Phasen zusammenlegen, Jahre korrigieren, alles belassen) liegt bei der Archäologin bzw. dem Archäologen.

### 8.2 Automatische Korrektur und Vorschläge

**Automatische Korrekturen und Vorschläge.** Automatische Korrekturen sind **bereits angehakt**; Vorschläge sind es **nicht** und werden nur angewendet, wenn man das Kästchen anhakt. Früher galt eine andere Regel: Ein Problem, dessen Korrektur eine menschliche Entscheidung erforderte, konnte nur gelesen werden. Jetzt hat es ein Kästchen, das leer bleibt. Das gilt auch für die beiden älteren Beziehungskategorien, die einen Vorschlag anbieten, nämlich den direkten Widerspruch und den stratigraphischen Zyklus.

So verwenden Sie den Bereich:

1. Wählen Sie im Bereich den zu prüfenden **Fundort** aus. Die Prüfung erfolgt **pro Fundort**: Sie betrachtet nur den gewählten Fundort und korrigiert nur diesen. In einer Datenbank mit zehn Fundorten ist das wichtig, weil dieselben SE-Nummern in allen vorkommen.
2. Lesen Sie die **Zusammenfassungszeile** über dem Baum: Sie nennt die Zahl der Probleme, wie viele automatisch korrigierbar sind und **wie viele Vorschläge von Hand anzuhaken sind**.
3. Öffnen Sie die Gruppen und wählen Sie ein Problem aus, um sein Detail im Vorschaubereich zu lesen.
4. Prüfen Sie die Kästchen. Automatische Korrekturen sind bereits angehakt: Entfernen Sie den Haken bei denen, die Sie nicht anwenden möchten. Haken Sie die Vorschläge an, denen Sie zustimmen.
5. Wenden Sie die Korrekturen an. Bevor etwas geschrieben wird, wird ein **automatisches Backup** erstellt (Kopie der SQLite-Datei bzw. `pg_dump` bei PostgreSQL nach `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); das Backup, das es für die Korrekturen der Periodenfelder bereits gab, deckt nun auch die chronologischen ab.
6. Wenn das Ergebnis nicht überzeugt, klicken Sie auf **Annulla ultimo fix** (letzte Korrektur rückgängig machen): Das Rückgängigmachen nimmt auch die in die Periodisierungstabelle geschriebenen Korrekturen zurück.

### 8.3 Vorschau und Backup

**Die Vorschau zeigt das berechnete Datum.** Für jede von einem Problem genannte Einheit zeigt der Vorschaubereich ihr berechnetes Datum in einer Zeile wie dieser:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

Die Zeile nennt der Reihe nach das Jahresintervall, die Regel, die es erzeugt hat, und die Beziehung, entlang der die Bedingung gelaufen ist, samt dem Knoten, von dem sie stammt. Kommen die beiden Enden des Intervalls auf verschiedenen Wegen zustande, ist jedes Ende beschriftet (`inizio …` und `fine …`), sodass ein Datum nie der falschen Beziehung zugeschrieben wird. Heute entnimmt in einer normalen Datenbank jede Einheit ihre Daten ihrer eigenen Periode, daher lauten die meisten Zeilen `epoca`. Der Sinn der Zeile ist nicht, zu überraschen, sondern sichtbar zu machen, **woher** ein Datum stammt.

---

## 9. Wie man die Kanten der Matrix liest

Einige Entscheidungen in der Matrixzeichnung wirken seltsam, sind aber keine Fehler:

- **Ein Pfeil läuft nie unter einem Knoten hindurch.** Ist die Zielspalte belegt, tritt der Pfeil **von der Seite** in das Kästchen ein: das ist normal.
- **Gleichheit ist keine Überlagerung.** Eine Beziehung «Uguale a» (Gleich) oder «Si lega a» (Bindet an) stellt die beiden Einheiten auf **dieselbe Zeile**, nebeneinander, verbunden durch **zwei waagerechte Linien** (das Gleichheitszeichen) **ohne Pfeilspitze**.
- **Redundante Kanten werden nicht gezeichnet.** Wenn SE 1 die SE 2 überdeckt und SE 2 die SE 3, erscheint der Pfeil von 1 nach 3 nicht, weil er nichts hinzufügt. Innerhalb eines **Zyklus** bleiben dagegen alle Kanten, denn ein Zyklus ist ein Fehler, den man sehen muss.
- **Die Linien sagen, welche Beziehung sie sind.** Grau und durchgezogen: die Abfolge (überlagert, verfüllt, lehnt an). **Grün gepunktet**: ein Schnitt (`Taglia` / `Tagliato da`), unabhängig von der stratigraphischen Definition und in jeder Sprache. **Dick und schwarz**: die Kontinuität — eine kleine schwarze Raute ohne Namen (der Name erscheint beim Überfahren mit der Maus) in der Spalte ihrer Einheit, die Linie ist also gerade. **Rot**: ein Pfeil, der die Bänder hinaufsteigt, also ein Widerspruch zwischen Stratigraphie und Chronologie; ein aufsteigender Schnitt ist rot **und** bleibt gepunktet.
- **Paradaten sind nie eine durchgezogene Linie.** Farbe und Strich kommen aus den Regeln der Extended Matrix (`em_visual_rules.json`): braunrot gepunktet „extrahiert aus", orange gestrichelt „Datenherkunft", gold gestrichelt „Eigenschaft", grau gestrichelt „allgemeine Verbindung", tomatenrot gestrichelt „kombiniert" (in der Datei durchgezogen: die einzige Abweichung, weil ein Bogen zu einem Dokument nicht wie eine Überlagerung aussehen darf).
- **Paradaten stehen unter ihrer Einheit.** Eigenschaften, Extraktoren, Kombinatoren und Dokumente einer Einheit liegen in ihrer **Gruppe**, dem gestrichelten Rahmen unter ihrem Kästchen, wie die Paradaten-Gruppen von EMStudio: eine Zeile für jede Stufe der Kette (zuerst die Eigenschaften, dann Extraktoren und Kombinatoren, dann die Dokumente), und sie zählen nicht bei den stratigraphischen Ebenen. Ein Dokument, das mehrere Einheiten nutzen, erscheint in der Gruppe jeder dieser Einheiten, wie in EMStudio, und die Linien der Paradaten bleiben innerhalb der Gruppe. Paradaten, die keine Einheit erreicht, haben unten ein eigenes Band („Paradati senza unità“). Der Kopf des Panels zählt sie getrennt: „114 unità · 739 paradati · 3 epoche · 90 rapporti“ für TempluMare (ab 5.13.126-alpha; vorher nahmen die Paradaten als Einheiten an den Ebenen teil, und die Matrix einer Fundstelle wie TempluMare wurde zu einem Knäuel).
- **Ein brauner Rand ist Mauerwerk.** USM-Einheiten — WSU, MSE, UEM, USZ, ΤΣΜ in den anderen Sprachen — haben dasselbe Kästchen wie die US, mit braunem statt rotem Rand.

---

## 10. Narrative (Erzählung) mit KI

Ab Version **5.13.106-alpha** hat das Matrix-Panel innerhalb von QGIS (§2.2, «Vedi la matrice») in seiner rechten Spalte zwei Tabs: **Units** (*Unità*; Einheiten) — das Formular der gewählten Einheit, der Zoom auf die Geometrie und die Medien, wie bisher — und **Narrative** (*Narrativa*; Erzählung), neu. Der Tab Narrative lässt eine KI die **Geschichte der Stätte** schreiben, ein Kapitel je Epoche, und erlaubt Ihnen anschließend, sie zu lesen, von einer Person validieren zu lassen und als HTML, DOCX oder PDF zu exportieren. Er liest und schreibt **dieselbe em.json**, die EMStudio öffnet, im Format der s3dgraphy-Bibliothek: Die Erzählung, die Sie hier sehen, ist dieselbe, die EMStudio in seinem Tab *Narrative* zeigt.

> **Keine neuen Einstellungen.** Der Tab hat kein eigenes Konfigurationsfenster: Er verwendet die KI, die Sie bereits an anderer Stelle in pyArchInit eingerichtet haben (§10.2).

> **Die KI schreibt Entwürfe, keine endgültigen Texte.** Jeder vom Modell geschriebene Absatz bleibt ein «AI draft» (KI-Entwurf), bis eine Person ihn validiert (§10.6), und trägt in exportierten Dokumenten das Zeichen ⚠.

Die Namen der Tabs und der Schaltflächen des Tabs Narrative gibt es auf Italienisch und auf Englisch: **auf Italienisch, wenn QGIS auf Italienisch läuft, auf Englisch bei jeder anderen Sprache**. Hier stehen immer beide. Die Menüeinträge und Dialogfenster des Plugins (wie «Vedi la matrice…» oder die drei Schaltflächen aus §10.9) gibt es dagegen nur auf Italienisch; die deutsche Übersetzung steht in Klammern.

### 10.1 Den Tab Narrative öffnen

1. Öffnen Sie das Menü **Plugins → pyArchInit - Archaeological GIS Tools** und wählen Sie den Eintrag **Extended Matrix → Vedi la matrice…** (Die Matrix ansehen).
2. Wählen Sie die **Stätte**.
3. pyArchInit exportiert die Stätte aus der Datenbank nach `<home>/pyarchinit_EM_folder/<Stätte>.em.json` — `<home>` ist `~/pyarchinit_5` oder der Ordner, den die Umgebungsvariable `PYARCHINIT_HOME` angibt — und öffnet das Panel **«Matrice — `<Stätte>`»**, rechts am QGIS-Fenster angedockt. Der Dateiname ist der Name der Stätte, wobei Sonderzeichen durch «_» ersetzt werden (zum Beispiel wird «Scavo 1» zu `Scavo_1.em.json`).
4. Klicken Sie in der rechten Spalte des Panels auf den Tab **Narrative**.

<!-- IMMAGINE: Screenshot des Menüs Plugins → pyArchInit - Archaeological GIS Tools mit dem Eintrag «Extended Matrix → Vedi la matrice…» -->
![Menü Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Abbildung 1: Der Eintrag «Extended Matrix → Vedi la matrice…» im Menü des Plugins*

<!-- IMMAGINE: Screenshot des rechts angedockten Matrix-Panels mit den Tabs Units und Narrative -->
![Panel mit zwei Tabs](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Abbildung 2: Das Matrix-Panel mit den Tabs Units und Narrative*

Die Datei ist **eine je Stätte und bleibt auf der Festplatte**: Sie liegt nicht mehr in einem temporären Ordner. Es ist die Datei, die EMStudio öffnet, und in ihr wird die Erzählung geschrieben. Jedes Mal, wenn Sie «Vedi la matrice…» wählen, wird die Stätte **erneut aus der Datenbank exportiert** und die Datei neu geschrieben; die bereits vorhandene Erzählung bleibt erhalten (§10.8).

Den Tab erreichen Sie auch an zwei weiteren Stellen:

- über den Eintrag **Extended Matrix → Esporta sito in em.json…** (Stätte nach em.json exportieren), der am Ende die Schaltfläche «Narrativa con l'AI» (Erzählung mit KI) anbietet (§10.9);
- über die Schaltfläche **Vedi la matrice** im Fenster «Esporta Extended Matrix» des SE-Formulars (§2.2): Sie öffnet dasselbe Panel mit der Datei, die Sie gerade exportiert haben, in dem Ordner, den Sie gewählt haben.

### 10.2 Welche KI verwendet wird

Oben im Tab Narrative sagt eine Zeile, welche KI er verwenden wird: **«Model: `<model>` (`<where it comes from>`)»**, gefolgt vom Hinweis zu EMStudio. Findet er keine, steht dort **«No AI configured: set it in the US form with “Report” (AI provider) or with “Query AI Database”.»**, und die Schaltflächen **Generate with AI** (Mit KI generieren) und **Regenerate chapter** (Kapitel neu generieren) bleiben deaktiviert.

Der Tab liest die KI-Einstellungen, die die anderen pyArchInit-Fenster **bereits gespeichert** haben, in dieser Reihenfolge und verwendet die **erste**, die ein Modell hat und — bei Online-Providern — den API-Key:

| # | Wo sie eingestellt wird | Wie der Tab sie nennt (en / it) |
|---|-------------------------|----------------------------------|
| 1 | SE-Formular, Schaltfläche «Report» → Fenster «Generatore di Report» (Report-Generator), Gruppe «Provider AI» | Report generator of the US form / Generatore di Report della scheda US |
| 2 | SE-Formular, Schaltfläche «Query AI Database» | Query AI Database / Query AI Database |
| 3 | Fenster palimpsestr, Schaltfläche «Report AI (analisi descrittiva)…», Auswahlfeld «Provider AI» | Palimpsest report / Relazione Palimpsest |
| 4 | Fenster «Generazione SQL con AI» (Text-zu-SQL: siehe Tutorial 30) | Text to SQL / Testo in SQL |

Die Provider sind die der Auswahlfelder «Provider AI»: **OpenAI** und **Anthropic (Claude)** über das Netz, mit dem API-Key, der im Feld «API key» eingetragen wird; **Ollama** und **LM Studio** auf Ihrem eigenen Computer, ohne Key. Das Auswahlfeld speichert Ihre Wahl, sobald Sie sie ändern. Möchten Sie ein anderes Modell verwenden, ändern Sie es in dem Fenster, das der Tab in Klammern nennt (oder in einem, das in der Liste weiter oben steht). Der Tab liest die Einstellungen neu ein, **wenn das Panel geöffnet wird**: Öffnen Sie die Matrix nach einer Änderung noch einmal.

### 10.3 Der Tab Narrative

```
┌─ Units ─┬─ Narrative ───────────────────────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the                        │
│ file open, close it first: the last writer wins.                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                                        │
│ Early 15th century — AI draft                                                       │
│ 15th century — endorsed                                                             │
│ Modern age — AI draft, truncated                                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                                    │
│ Language of the prose: [English ▾]                                                  │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]                                │
│ [Prepare the chapters]  [Choose the media]  [Show on the map]  [Export…]            │
│ [Open in EMStudio]  [Cancel]*                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

\* Die Fortschrittszeile und die Schaltfläche «Cancel» sind nur sichtbar, während die KI schreibt. In diesem Schema sind die Listenzeilen die der Beispielstätte.

<!-- IMMAGINE: Screenshot des Tabs Narrative mit der Kapitelliste, dem Text des gewählten Kapitels und den acht Schaltflächen -->
![Tab Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Abbildung 3: Der Tab Narrative*

Von oben nach unten:

- **die Statuszeile**: das verwendete Modell (§10.2) und der Hinweis *«If EMStudio has the file open, close it first: the last writer wins.»* (Hat EMStudio die Datei geöffnet, schließen Sie es zuerst: Wer zuletzt schreibt, gewinnt.);
- **die Kapitelliste**, eine Zeile je Kapitel: *Titel — Zustand*. Eine Datei aus einer früheren Version, die nach Sondagen geteilt ist, zeigt alle Graphen: Jeder Zeile geht der Name des Graphen in eckigen Klammern voran, zum Beispiel `[Saggio A] 15th century — AI draft`;
- **der Text des gewählten Kapitels**: der Fließtext, in dem die Einheiten mit ihrem Namen zitiert werden — die Namen sind **Links**: Ein Klick zeigt die Einheit auf der Karte (§10.10); unter dem Absatz, in dem eine Einheit zum ersten Mal genannt wird, erscheinen bis zu zwei ihrer Fotos (§10.11). Hat das Kapitel noch keinen Text, sehen Sie seinen Platzhalter «[to be written: …]»;
- **die Fortschrittszeile**, nur während der Generierung: «Chapter 3 of 9 · 15th century»;
- **die Sprache des Textes** (ab 5.13.128-alpha): die Sprache, in der die KI die Kapitel schreibt und in der die Titel neuer Kapitel entstehen (§10.4, «Die Sprache»);
- **die Schaltflächen**, in zwei Zeilen.

Das Ergebnis jeder Operation erscheint in der QGIS-Meldungsleiste, mit dem Titel «Narrative».

Wenn die Datei **noch keine Erzählung enthält**, ist die Liste leer, und ein Text sagt: *«No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it.»* (Keine Erzählung in der Datei: «Prepare the chapters» erstellt die Gliederung — N Kapitel über Epochen und Aktivitäten —, «Generate with AI» schreibt sie.)

#### Die Zustände eines Kapitels

| Zustand (en / it) | Was er bedeutet |
|-------------------|-----------------|
| **to be written** / da scrivere | Noch zu schreiben: Das Kapitel enthält nur den Platzhalter «[to be written: …]». |
| **AI draft** / bozza AI | KI-Entwurf: Es gibt vom Modell geschriebenen Text, den keine Person validiert hat. Ein Absatz genügt: Hat das Kapitel auch nur einen nicht validierten Absatz, ist dies sein Zustand, selbst wenn weiterer Text vorhanden ist. |
| **endorsed** / convalidato | Validiert: Der gesamte von der KI geschriebene Text wurde von einer Person validiert. |
| **written** / scritto | Geschrieben: Von einer Person (in EMStudio) geschriebener Text. |
| **truncated** / troncato | Abgeschnitten: Wird dem Zustand hinzugefügt (zum Beispiel «AI draft, truncated»): Das Modell hat angehalten, weil es die Längengrenze erreicht hat, und der Text endet mittendrin. |

#### Die Schaltflächen

| Schaltfläche (en) | Auf Italienisch | Was sie tut |
|-------------------|-----------------|-------------|
| **Generate with AI** | Genera con l'AI | Schreibt **nacheinander** alle Kapitel, die noch «to be written» sind — zuerst die **Presentation**, dann die der Epochen (und der Aktivitäten); bereits geschriebene bleiben unberührt. Gibt es noch keine Erzählung, wird zuerst die Gliederung angelegt. Zeigt den Fortschritt und die Schaltfläche **Cancel**. Nur aktiv, wenn eine Datei geöffnet und eine KI eingerichtet ist. Bringt die Datei eine eigene Erzählung mit — etwa die von TempluMare, in EMStudio geschrieben —, werden keine Kapitel hinzugefügt: Geschrieben werden nur die Kapitel von pyArchInit, die noch «to be written» sind, sofern Sie sie mit «Prepare the chapters» hinzugefügt haben (bis 5.13.127-alpha wurden sie von selbst hinzugefügt). |
| **Regenerate chapter** | Rigenera capitolo | Schreibt **das in der Liste gewählte Kapitel** neu: Der nicht validierte KI-Entwurf wird ersetzt — aber erst, wenn das Modell geantwortet hat: Schlägt der Aufruf fehl, bleibt der frühere Entwurf erhalten —, und bereits validierte Blöcke bleiben. Die Schaltfläche wird aktiv, wenn Sie die Presentation oder ein Kapitel einer Epoche oder einer Aktivität wählen und eine KI eingerichtet ist; bei «Where it is» bleibt sie deaktiviert. Die Presentation ist die von pyArchInit: Das erste Kapitel der Erzählung einer Datei (die Einleitung von TempluMare) ist sie nicht und wird nicht neu generiert. |
| **Endorse…** | Convalida… | Öffnet ein Menü mit «This chapter» und «All chapters» und fragt dann, wer validiert (§10.6). Aktiv, wenn eine Erzählung vorhanden ist. |
| **Prepare the chapters** | Prepara i capitoli | Legt **nur die Gliederung** der Kapitel an, ohne KI: Das geht auch, wenn keine KI eingerichtet ist, sodass Sie in EMStudio von Hand schreiben können. Bereits geschriebener Text bleibt unberührt, und die Kapitel neuer Epochen werden hinzugefügt. Ergebnis: «Chapters prepared: N.» Bringt die Datei eine eigene Erzählung mit, wird zuerst nachgefragt: **Only the file's chapters** (es wird nichts hinzugefügt: «The file's N chapters stay as they are: no chapter added.»), **Add pyArchInit's** (die Presentation, «Where it is», ein Kapitel für jede Epoche und jede Aktivität, die keines hat, hinter den Kapiteln der Datei, die unberührt bleiben) oder **Cancel**. Es wird jedes Mal nachgefragt, bis Sie sie hinzugefügt haben. Die Titel der neuen Kapitel stehen in der **Sprache des Textes**. |
| **Choose the media** | Scegli i media | Seit 5.13.130-alpha. Wählt für jedes Kapitel unter den Medien der Einheiten, von denen es spricht — den 3D-Modellen, Bildern und Videos der Datensätze und denen ihrer Belegkette (das Bild des Extraktors, die Tafel des Dokuments); PDFs nicht, sie sind Quellen —, diejenigen aus, die **in den Text** gehören, nach dem Absatz, der von ihnen spricht, mit einer Bildunterschrift in der **Sprache des Textes**. Ist eine KI eingerichtet, wählt die KI bei **Temperatur null** nur unter diesen Medien aus, höchstens vier je Kapitel; ohne KI oder wenn ihre Antwort nicht lesbar ist, erfolgt die Auswahl automatisch: ein Medium je Einheit, in der Reihenfolge, in der der Text sie nennt, höchstens drei. Die Auswahl **bleibt in der Datei** (in den Daten der Erzählung), und der HTML-Export verwendet sie immer unverändert, bis Sie die Schaltfläche erneut anklicken. Erforderlich ist die Projektdatenbank mit den Medien der Datensätze (bei TempluMare die aus der em.json importierten). Ergebnis: «Media chosen: N in M chapters (with the AI)». Aktiv, wenn eine Erzählung vorhanden ist. |
| **Show on the map** | Mostra sulla mappa | Wählt die Einheiten, von denen das gewählte Kapitel spricht, **gemeinsam** auf der Karte aus und rückt sie ins Bild (§10.10): die im Fließtext zitierten oder, wenn das Kapitel noch nicht geschrieben ist, alle Einheiten seines Bandes. Nur aktiv, wenn mindestens eine der Einheiten, von denen das gewählte Kapitel spricht, eine Zeile des SE-Formulars ist. |
| **Export…** | Esporta… | Speichert die Erzählung als HTML (mit der interaktiven Karte der Stätte, §10.7), DOCX oder druckfähiges PDF (§10.7), mit den Fotos der zitierten Einheiten, wenn es welche gibt (§10.11). Aktiv, wenn eine Erzählung vorhanden ist. |
| **Open in EMStudio** | Apri in EMStudio | Öffnet die em.json in EMStudio. Ist EMStudio nicht vorhanden, verweist die Meldungsleiste auf den Menüeintrag **Extended Matrix → Installa EMStudio…** (EMStudio installieren). |
| **Cancel** | Annulla | Erscheint nur während der Generierung: Die KI hält **nach dem laufenden Kapitel** an, und das bisher Geschriebene wird gespeichert. |

Während der Generierung sind alle Schaltflächen deaktiviert, außer **Cancel**.

### 10.4 Was die KI schreibt

**Welche Kapitel.** Die Gliederung stammt aus der s3dgraphy-Bibliothek (die Vorlage «site_story»):

- Seit **5.13.110-alpha** ist die **Presentation** (Vorstellung) ein kanonisches Kapitel, das die KI wie die anderen schreibt, und zwar aus einem Briefing der ganzen Stätte (siehe «Das Briefing der Presentation» unten); vorher blieb sie ein Platzhalter. **Where it is** (Lage) ist das andere kanonische Kapitel und bleibt ein Platzhalter «[to be written: …]», der in EMStudio von Hand zu schreiben ist: Es entsteht aus der Position der Stätte, und die Bibliothek setzt die Karte hinein. «Where it is» gibt es nur, wenn der Graph eine geographische Position trägt. Die KI generiert es nicht.
- **Ein Kapitel je Epoche** (Periode/Phase), die Einheiten hat, von der ältesten zur jüngsten. Der Titel ist der Name der Epoche, nämlich die «Datazione estesa» (erweiterte Datierung) der Periodisierung; fehlt sie, entsteht ein allgemeiner Name wie «Period 8 Phase 1»: Füllen Sie sie im Periodisierungsformular aus, um gut lesbare Titel zu erhalten. Eine Einheit erscheint im Kapitel der Epoche, in der sie entsteht, und in den Kapiteln der Epochen, in denen sie fortbesteht.
- **Ein Kapitel je Aktivität**, wenn der Graph Aktivitätsgruppen enthält. Eine aus der Datenbank exportierte Stätte hat normalerweise keine — das Feld Aktivität des SE-Formulars reist als Eigenschaft der Einheit mit —, und dann sind die Kapitel die der Epochen.

**Die Erzählung der Datei.** Eine em.json von EMStudio kann mit einer eigenen Erzählung ankommen: TempluMare bringt 13 Kapitel von Emanuel Demetrescu mit, auf Englisch, von ihm selbst geschrieben. pyArchInit behält sie, wie sie ist: Die Kapitel der Erzählung werden nicht angetastet, und die der Vorlage «site_story» werden nur mit **Prepare the chapters** → **Add pyArchInit's** hinzugefügt (bis 5.13.127-alpha wurden sie auch von «Generate with AI» und von jedem Export der Stätte hinzugefügt). Ein Kapitel der Datei, das an eine Aktivität verankert ist, gilt als das Kapitel dieser Aktivität: In TempluMare ist «Virtual Activity 2: colonnade» an die Aktivität VAct.03 verankert und «Virtual Activity 4: Temple» an VAct.01, sodass VAct.02 und VAct.04 kein Kapitel haben und pyArchInit jeweils eines hinzufügt («VAct.02 Columnade», «VAct.04 Temple»): Zu korrigieren sind die Anker der Datei.

**Was das Modell erhält.** Für jedes Kapitel einer Epoche oder Aktivität erhält das Modell ein *Briefing* mit folgenden Angaben für jede Einheit: Name, Typ und Beschreibung; die ausgefüllten Felder des SE-Formulars (stratigraphische und interpretative Definition, Interpretation, Periode und Phase, Datierung, Aktivität, Struktur, Sondage, Raum, Sektor, Areal); die Epochen; **die stratigraphischen Beziehungen** zu den anderen Einheiten (überdeckt, schneidet, verfüllt, lehnt an, gleich …) mit deren Namen; und, falls vorhanden, die verknüpften dokumentarischen Quellen. Die Einheiten werden **von der ältesten zur jüngsten** aufgelistet, den Beziehungen folgend. Bei mehr als **80 Einheiten** je Kapitel wird das Briefing auf die ersten 80 gekürzt. Außerdem gilt eine Obergrenze für seine Länge (etwa 25.000 Zeichen): Wird sie überschritten, werden die langen Texte der Formulare gekürzt, wiederholte Beziehungen und Belegketten entfallen und, wenn das immer noch nicht reicht, werden die jüngsten Einheiten ausgelassen. In beiden Fällen wird dem Modell mitgeteilt, wie viele Einheiten fehlen.

**Die Regeln.** Das Modell erhält die fünf Regeln der Bibliothek: nur schreiben, was der Kontext stützt (keine erfundenen Datierungen, Materialien, Funktionen oder Ereignisse); die Unsicherheit bewahren (eine virtuelle Einheit ist eine Hypothese, keine Tatsache); keine Quelle zitieren, die nicht vorhanden ist; Fließtext schreiben, ohne Listen und Überschriften; offen sagen, wenn der Kontext zu dürftig ist. Verlangt werden ein bis drei Absätze.

**Das Briefing der Presentation.** Die Presentation hat keine eigenen Einheiten: Das Modell erhält ein Briefing der **ganzen Stätte**, dem Graphen entnommen und nicht der Datenbank, mit dem Namen der Stätte; der Kette der Ortsnamen (Land → Region → Provinz → Gemeinde); den Orten des SE-Formulars (Areale, Sektoren, Sondagen, Räume); den Epochen von der ältesten zur jüngsten, jeweils mit der Zahl der in ihr vorhandenen Einheiten (dieselbe Einheit kann in mehreren Epochen liegen, die Summe kann also die Gesamtzahl übersteigen); der Zahl der Einheiten und ihren Typen sowie der Zahl der stratigraphischen Beziehungen; den Dokumenten; den in den SE-Formularen genannten Personen; und den Titeln der Kapitel der Geschichte. Seine Anweisungen sind die der Presentation, nicht die fünf Regeln oben: Sie verlangen zwei bis vier Absätze, die sagen, was die Stätte ist und wo sie liegt, welche Epochen die Geschichte umfasst, wie die Geschichte zu lesen ist (ein Kapitel je Epoche und je Aktivität, Einheiten mit ihrem Namen zitiert, Entwürfe als solche gekennzeichnet, bis eine Person sie validiert) und auf welche Quellen sie sich stützt; nur das Briefing zu verwenden, ohne Datierungen oder Fakten zu erfinden, und eine seltsam wirkende Angabe wegzulassen, statt sie zu kommentieren. Der Text steht **am Anfang** des Kapitels; die Quellenkarten (die Dokumente) folgen danach, und die Platzhalter «[to be written: a presentation of …]» und «[to be written: how this account is to be read…]» verschwinden.

**Die Sprache.** Ab 5.13.128-alpha wählt sie derjenige, der schreibt, im Auswahlfeld **Language of the prose** des Tabs: Vorgabe ist die Sprache der Erzählung der Datei, falls diese eine hat (TempluMare: Englisch), andernfalls die von QGIS. Die Auswahl gilt für den Text, den die KI mit «Generate with AI» und «Regenerate chapter» schreibt, und für die Titel der neuen Kapitel, die «Prepare the chapters» hinzufügt («Presentation», «Where it is»); bereits geschriebene Kapitel werden nicht übersetzt, und dasselbe kanonische Kapitel in einer anderen Sprache wird nicht ein zweites Mal hinzugefügt. Die Anweisungen des Modells gibt es auf Italienisch und Englisch: Für die anderen Sprachen (Deutsch, Französisch, Spanisch, Katalanisch, Portugiesisch, Rumänisch, Griechisch, Arabisch) erhält das Modell die englischen mit der Bitte, in dieser Sprache zu schreiben. Bis 5.13.127-alpha entstand der Text immer in der Sprache der Erzählung: bei TempluMare auf Englisch, auch wenn QGIS auf Italienisch lief.

**Wie es gespeichert wird.** Im Format der Bibliothek, demselben, das EMStudio liest: ein Erzählknoten (`NarrativeNode`), der die Kapitel enthält; jeder vom Modell geschriebene Absatz ist ein Block «AI draft», der dem **KI-Autor** dieses Modells zugeschrieben wird; der verwendete **Prompt** wird als Extraktor registriert, der mit den Quellen verknüpft ist, sodass sich nachvollziehen lässt, was gefragt wurde. Die im Text zitierten Einheiten sind **Erwähnungen** (`[[name]]`): In der Datei bleiben sie mit dem Knoten der Einheit verknüpft, und im Tab und in den Exporten erscheinen sie mit ihrem Namen. Eine Erwähnung, die keiner Einheit des Graphen entspricht, wird auf einfache Wörter ohne Klammern reduziert.

**Kosten und Zeiten.** Das Modell wird **einmal je Kapitel** (die Presentation eingeschlossen) aufgerufen. Bei einem Online-Provider hat jeder Aufruf Kosten und eine Wartezeit (in Versuchen mit einem Online-Modell einige Dutzend Sekunden je Kapitel: Eine Stätte mit etwa zehn Epochen braucht einige Minuten); mit Ollama oder LM Studio wird nichts bezahlt, aber die Zeiten hängen von Ihrem Computer ab.

### 10.5 Schritt für Schritt

1. Öffnen Sie die Matrix der Stätte (§10.1) und klicken Sie auf den Tab **Narrative**. Prüfen Sie oben, **welches Modell** er verwenden wird.
2. **Schließen Sie EMStudio**, wenn es die Datei geöffnet hat: pyArchInit und EMStudio schreiben dieselbe Datei, und wer zuletzt schreibt, gewinnt.
3. Optional: **Prepare the chapters** (Kapitel vorbereiten), um die Gliederung ohne KI zu sehen.
4. Klicken Sie auf **Generate with AI**. Verfolgen Sie den Fortschritt: Die Presentation, falls sie noch «to be written» ist, kommt zuerst («Chapter 1 of 9 · Presentation»), dann die Kapitel der Epochen («Chapter 3 of 9 · …»); Sie können QGIS weiter benutzen. Am Ende sagt die Meldungsleiste zum Beispiel *«7 chapters generated, 1 failed: Modern age — …»* (7 Kapitel generiert, 1 fehlgeschlagen), mit *«(cancelled)»*, wenn Sie abgebrochen haben, und die Liste wird neu geladen: Die geschriebenen Kapitel sind «AI draft».
5. **Lesen**: Wählen Sie ein Kapitel nach dem anderen und lesen Sie den Text unter der Liste. Prüfen Sie ihn anhand der Stratigraphie: Es ist ein Entwurf, der aus den Daten des SE-Formulars aufgebaut wurde. Um zu sehen, wo die Einheiten liegen, von denen es spricht, klicken Sie auf ihre Namen oder verwenden Sie **Show on the map** (Auf der Karte anzeigen; §10.10).
6. Überzeugt ein Kapitel nicht, wählen Sie seine Zeile und klicken Sie auf **Regenerate chapter**. Der neue Entwurf **ersetzt** den vorherigen, nicht validierten: Wenn Sie die frühere Fassung behalten möchten, exportieren Sie sie vorher. Ist ein Kapitel «truncated» (abgeschnitten), generieren Sie es neu, **bevor** Sie es validieren.
7. Wenn ein Kapitel stimmt, klicken Sie auf **Endorse…** (§10.6).
8. Mit **Export…** exportieren Sie die Erzählung als HTML, DOCX oder PDF (§10.7); mit **Open in EMStudio** öffnen Sie die Datei in EMStudio, um «Where it is» von Hand zu schreiben und den Rest zu überarbeiten.
9. Später können Sie die Matrix erneut öffnen: Die Erzählung bleibt erhalten (§10.8).

<!-- IMMAGINE: Screenshot der laufenden Generierung: die Fortschrittszeile «Chapter 3 of 9 · …» und die Schaltfläche Cancel -->
![Generierung läuft](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Abbildung 4: Laufende Generierung, mit Fortschrittszeile und der Schaltfläche Cancel*

Ein Kapitel, das fehlschlägt, hält die anderen nicht auf: Die Zusammenfassung sagt, welches. Um es erneut zu versuchen, genügt ein weiterer Klick auf **Generate with AI**: Es werden nur die Kapitel geschrieben, die noch «to be written» sind.

### 10.6 Validieren: wer unterschreibt

Validieren heißt, dass eine **Person** die Verantwortung für den vom Modell geschriebenen Text übernimmt. Es geschieht nie von selbst: weder durch das Generieren noch durch das Speichern.

1. Klicken Sie auf **Endorse…**. Es öffnet sich ein kleines Menü: **«This chapter»** (Dieses Kapitel) — nur aktiv, wenn das gewählte Kapitel ein «AI draft» ist — oder **«All chapters»** (Alle Kapitel), das heißt alle noch nicht validierten KI-Entwürfe in jedem Graphen der Datei. Die Presentation wird wie jedes andere Kapitel validiert: Wählen Sie sie in der Liste, und «This chapter» validiert sie für sich allein.
2. Ein Fenster fragt **«Who endorses? Pick an author or type a new name.»** (Wer validiert? Wählen Sie einen Autor oder geben Sie einen neuen Namen ein.) Die Liste enthält die **menschlichen Autoren, die bereits im Graphen sind** — die im SE-Formular genannten Personen als Erfasser (*schedatore*), SE-Leiter und SE-Verantwortlicher —, und Sie können einen neuen Namen eingeben, der zu einem neuen Autor des Graphen wird.
3. Die Meldungsleiste sagt **«N blocks endorsed by `<name>`.»** (N Blöcke vom gewählten Autor validiert.) oder «Nothing to endorse.» (Nichts zu validieren.) Die Datei wird gespeichert.

<!-- IMMAGINE: Screenshot des Menüs Endorse… («This chapter» / «All chapters») und des Fensters zur Wahl des Autors -->
![Validieren](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Abbildung 5: Validieren: das Menü und die Wahl des Autors*

Die Blöcke wechseln von «AI draft» zu «endorsed». Im exportierten Dokument erscheint die Person unter den Verantwortlichen («a cura di», herausgegeben von) und das Modell als Assistent («con l'assistenza di», mit Unterstützung von), und validierte Absätze tragen das Zeichen ⚠ nicht mehr. Das erneute Generieren löscht validierte Blöcke nicht: Eine Unterschrift ist eine Handlung und geht durch Umschreiben nicht verloren.

### 10.7 Als HTML, DOCX oder PDF exportieren

Klicken Sie auf **Export…**: Das Fenster zum Speichern öffnet sich mit drei Formaten: «HTML page» (`.html`), «Word document» (`.docx`) und «Printable PDF» (druckfähiges PDF; `.pdf`). Der vorgeschlagene Name ist `<Stätte>_narrativa`, ohne Endung, im Ordner der em.json: Die Endung ergibt sich aus dem im Filter des Fensters gewählten Format; eine von Hand eingetippte Endung (`.html`, `.docx` oder `.pdf`) hat Vorrang vor dem Filter. Die Meldungsleiste bestätigt: «Narrative exported to `<path>`».

Das Dokument enthält:

- den Titel der Erzählung (zum Beispiel «Scavo archeologico — the story of the site»; sinngemäß: Archäologische Ausgrabung — die Geschichte der Stätte), die Verantwortlichen («a cura di») und das Modell als Assistent («con l'assistenza di»);
- **das Inhaltsverzeichnis** (seit 5.13.129-alpha), nach dem Titel: die Kapitel — nach Teilen gruppiert, wenn die Titel es angeben, wie in «Rilievo e analisi — Introduction» —, darunter jeweils ihre Zwischenüberschriften und zuletzt «Sources» (Quellen). Im HTML führt jeder Eintrag zu seinem Kapitel; im PDF hat das Inhaltsverzeichnis Seitenzahlen, und die Kapitel sind zugleich Lesezeichen des PDFs; in Word ist es ein echtes Inhaltsverzeichnis (ein Feld) mit bereits geschriebenen Titeln, das Word beim Öffnen der Datei mit den Seitenzahlen aktualisiert (antworten Sie mit «Ja», wenn es fragt, ob die Felder aktualisiert werden sollen; in LibreOffice: Rechtsklick auf das Inhaltsverzeichnis → Aktualisieren);
- für jedes Kapitel zuerst den Text, in dem die Einheiten mit ihrem Namen zitiert werden, dann die Liste der Einheiten des Kapitels; für zitierte Einheiten mit Fotos steht ein Streifen mit Fotos an der Stelle ihrer Zeile (§10.11);
- die **Zwischenüberschriften**, die im Text mit «### » geschrieben werden (TempluMare hat zwölf, ab «Past researches»), werden zu Überschriften, im HTML, in Word und im PDF, und die mit «\*…\*» geschriebene Kursivschrift ist auch in Word und im PDF kursiv (seit 5.13.129-alpha; zuvor wurden die Zeichen mitgedruckt);
- am Ende jedes Kapitels die Zeile **Chapter sources** (Quellen des Kapitels; seit 5.13.129-alpha): die Dokumente, auf denen die Einheiten beruhen, von denen das Kapitel spricht — dabei folgt man den Paradata: Einheit → Eigenschaft → Extraktor (oder Kombinierer) → Dokument — und die, die das Kapitel selbst zitiert. Im HTML ist jede Quelle ein **Hotspot**: Beim Überfahren mit der Maus erscheint eine Infokarte mit der Vorschau (die erste Seite des PDFs oder das Bild), dem Typ und der Beschreibung; ein Klick öffnet rechts ein Panel mit der Datei — das PDF kann man dort lesen, das Bild sieht man ganz —, dem Link «Open the file» (Datei öffnen), dem Pfad des Originals und den **Lesungen**, die sich daraus ergeben (Einheit — Eigenschaft, mit dem Extraktor). Esc oder das × schließen das Panel. Die Datei wird in die Seite eingebettet, wenn sie bis zu 2 MB groß ist (insgesamt 25 MB); darüber zeigen Infokarte und Panel die Vorschau und den Link zum Original, das sich auf dem Computer öffnet, der die Seite exportiert hat. Die Dateien werden so gefunden wie beim Datensatz: die Medien der Zeile des Dokuments, das Original oder seine Kopie im Ordner der verkleinerten Kopien; ohne angebundene Datenbank haben die Quellen Titel, Beschreibung und Lesungen, aber nicht die Dateien. In Word und im PDF zählt die Zeile die Quellen mit ihrer Beschreibung auf;
- **die gewählten Medien** (seit 5.13.130-alpha, im HTML) mit **Choose the media**: jedes nach seinem Absatz, mit der Bildunterschrift; darunter stehen die Einheit und der Dateiname. Sie sind Hotspots wie die Quellen: Beim Überfahren mit der Maus erscheint die Infokarte, ein Klick öffnet rechts das Panel — das ganze Bild, das Video mit seinem Player und bei einem **3D-Modell** (GLB) der **interaktive Viewer**: Man dreht das Modell mit der Maus oder dem Finger und zoomt mit dem Mausrad. Der Viewer nutzt das three.js, das Teil der Seite ist (seit 5.13.133-alpha): Er funktioniert auch ohne Netz; vorher war es Googles model-viewer, der aus dem Internet geladen wurde. Lässt sich ein Modell im Viewer nicht öffnen, meldet das Panel dies, und die Datei öffnet sich mit «Open the file». Die großen Ansichten der Modelle werden beim Export in einem eigenen Prozess gezeichnet (ein paar Sekunden mehr); GLB-Modelle und Videos werden bis zu 15 MB je Datei und 60 MB insgesamt in die Seite eingebettet. In Word und im PDF bleiben die Streifen mit Fotos der zitierten Einheiten erhalten (§10.11);
- **die Einheiten des Kapitels** (seit 5.13.130-alpha, im HTML): statt der aneinandergereihten Karten der Bibliothek — Einheiten, Paradata, Dokumente und Streifen mit Fotos; im Kapitel «II A.D.» von TempluMare 367 Notizen untereinander, die Paradata ohne Angabe, zu welcher Einheit sie gehören — ein Block **Units of the chapter** («104 units, 339 paradata») mit einer Zeile je Einheit — Name, Typ, Beschreibung —, die sich aufklappt und die Tabelle ihrer Paradata zeigt: Eigenschaft, Wert und Herkunft, jeweils ein Dokument mit seinen Extraktoren, das Dokument als Hotspot; dazu das Foto oder die Modellansicht der Einheit, falls vorhanden. Die Dokumente bleiben in der Zeile mit den Quellen des Kapitels;
- **die Karte der Stätte** (seit 5.13.115-alpha, nur im HTML), in einem festen Bereich: auf breiten Bildschirmen rechts, auf dem Smartphone oben. Mit der Karte wird die Seite breiter (seit 5.13.116-alpha), und der Text bleibt in einer gut lesbaren Spalte. Im Ausgangszustand zeigt sie alle Einheiten des Graphen in Hellgrau; ein Klick auf den Namen einer Einheit im Text zeigt **nur die Einheiten der Periode dieses Kapitels** als Umrisse mit der Nummer darauf, die angeklickte Einheit **farbig**, und rückt die Gruppe ins Bild; ein Klick auf den Titel eines Kapitels bewirkt dasselbe, ohne die farbige Einheit. Die Zeile unter der Karte nennt die Periode und die Anzahl der Einheiten; «whole site» (ganze Stätte) kehrt zur Gesamtansicht zurück. Die Geometrien stammen aus den US- und USM-Ansichten der Datenbank des Projekts zum Zeitpunkt des Exports (Stätte des Graphen, Einheiten nach Areal und Nummer zugeordnet): Eine zitierte Einheit ohne Zeichnung hat den Link, aber nichts auf der Karte; ohne angebundene Datenbank hat das Dokument keine Karte;
- **die 3D-Szene der Proxys** (seit 5.13.132-alpha, nur im HTML), im festen Panel der Karte: Mit Zeichnungen und Proxys gibt es die Tabs **Map** (Karte) und **3D**; mit Proxys allein — TempluMare — zeigt das Panel nur die 3D-Ansicht. Es sind die Proxys der Einheiten, wie EMStudio sie zeichnet (Einheit → Eigenschaft «geometry» → Form → `proxies/<Einheit>.glb`), und sie kommen wie die übrigen Medien aus der Datenbank; jeder trägt seine eigene Position in der Szene, und zusammengesetzt passen sie ineinander. Im Ausgangszustand haben sie die Farben ihrer Materialien, den EM-Farbcode. Ein Klick auf den Namen einer Einheit im Text — jetzt auch ohne Karte ein Link — hebt ihren Proxy in voller Deckkraft und mit orangefarbenem Umriss hervor, macht die Proxys derselben Periode transparent, die übrigen fast unsichtbar, und rückt ihn ins Bild; ein Klick auf den Titel eines Kapitels zeigt die Proxys seiner Periode in voller Deckkraft oder, bei einem an eine Aktivität verankerten Kapitel, die seiner Einheiten; «whole site» (ganze Stätte) zeigt wieder alles. Man dreht die Szene mit der Maus oder einem Finger und zoomt mit dem Mausrad oder mit zwei Fingern; beim Überfahren eines Proxys mit der Maus erscheint sein Name, ein Klick darauf wählt seine Einheit aus, auch auf der Karte. Die Bildunterschrift nennt die Periode, die Anzahl der Proxys und die Einheit («no 3D proxy» (kein 3D-Proxy), wenn sie keinen hat). Auch mit der Tastatur (seit 5.13.133-alpha): Tab führt in die Szene, die Pfeiltasten verschieben die Ansicht, + und − zoomen hinein und heraus, Esc kehrt zu «whole site» (ganze Stätte) zurück. three.js ist Teil der Seite: Die Szene funktioniert auch ohne Netz. Proxys werden bis zu 15 MB je Datei und 40 MB insgesamt in die Seite eingebettet; die außen vor gebliebenen werden gezählt. Bei TempluMare: 65 Proxys, 2,4 MB;
- am Ende den Abschnitt **Fonti** (Quellen): die Dokumente, auf die sich die Geschichte stützt, und den Eintrag «Prompt», der auf den in der Datei gespeicherten Prompt verweist. Seit 5.13.129-alpha enthält die Liste auch die Quellen der Kapitel, jeweils mit ihrer Beschreibung, und im HTML sind sie Hotspots wie die der Kapitel; Hotspots sind auch die Quellenkarten «fonte» in den Kapiteln und die im Text zitierten Dokumente.

Wissenswertes:

- **nicht validierte Entwürfe werden aufgenommen**, jeweils mit vorangestelltem «⚠︎ non validato da una persona» (nicht von einer Person validiert), und der Kopf des Dokuments sagt, wie viele Blöcke sich in diesem Zustand befinden. Für ein Dokument ohne Markierungen validieren Sie zuerst (§10.6). Im HTML liest sich der Entwurf wie der übrige Text, mit derselben Schrift und demselben Hintergrund: Über dem Absatz steht die Hinweiszeile, links ein bernsteinfarbener Strich. Im Word-Dokument und im PDF steht der Hinweis vor dem Absatz (im PDF in einer eigenen Zeile, ohne das Zeichen ⚠, §10.11);
- **alle Kapitel werden aufgenommen**, auch die noch «to be written»: Ihr Platzhalter «[to be written: …]» bleibt im Text;
- der Text steht **am Anfang** des Kapitels, vor der Liste der Einheiten; in einer mit einer früheren Version geschriebenen Erzählung kann er noch am Ende stehen und wird durch erneutes Exportieren der Stätte (§10.8) oder mit **Prepare the chapters** (Kapitel vorbereiten) an die richtige Stelle gesetzt;
- Abbildungen, die ein Autor in EMStudio vorgesehen hat (zum Beispiel die Matrix einer Epoche), werden vom Export von pyArchInit nicht gezeichnet: Im Dokument bleibt ein Platzhalter;
- das HTML ist eine einzige, in sich geschlossene Datei (auch die Fotos sind eingebettet, und die Karte ist eine SVG-Grafik in der Datei, ohne externe Bibliotheken: Die Datei öffnet sich auch auf dem Smartphone ohne Netzverbindung); das DOCX öffnet sich mit Word oder LibreOffice und erfordert das Paket `python-docx`, das PDF die Bibliothek ReportLab (§10.11): Beide gehören zu den Abhängigkeiten des Plugins; seit 5.13.129-alpha sind im HTML auch die Dateien der Quellen eingebettet, bis zu 2 MB je Datei und 25 MB insgesamt: Bei vielen PDFs wird die Seite größer.

<!-- IMMAGINE: Screenshot des exportierten HTML-Dokuments: ein Kapitel mit einem Entwurf, dem «⚠︎ non validato da una persona» vorangestellt ist -->
![Exportiertes HTML-Dokument](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Abbildung 6: Das exportierte HTML-Dokument, mit einem markierten nicht validierten Entwurf*

### 10.8 Die Stätte erneut exportieren: Die Erzählung bleibt

Wird die Stätte erneut aus der Datenbank exportiert — mit **Vedi la matrice…**, mit **Esporta sito in em.json…** oder mit dem Fenster «Esporta Extended Matrix» des SE-Formulars —, **bleibt die Erzählung erhalten**, die in der Zieldatei bereits vorhanden ist: Text, Validierungen, KI-Autor und Prompts. Epochen, die inzwischen hinzugekommen sind, erhalten ein Kapitel «to be written». Ein Hinweis meldet dies: **«Narrative kept from the previous file (N chapters).»** (Erzählung der vorherigen Datei erhalten, N Kapitel.) Sie sehen ihn bei «Vedi la matrice…» in der Meldungsleiste, in der Zusammenfassung des Fensters «Esporta Extended Matrix» und, bei «Esporta sito in em.json…», in den Details des Abschlussfensters.

**Eine aus einer em.json importierte Stätte** (§5) hat auch die Erzählung der importierten Datei, die beim Import gemerkt wird und in den Export zurückkehrt. Ab 5.13.128-alpha gewinnt die jüngere: Wurde die Arbeitsdatei nach dem Import gespeichert — mit «Prepare the chapters», «Generate with AI», «Endorse…» oder durch EMStudio an derselben Datei —, reist ihre Erzählung mit, mit dem üblichen Hinweis; wurde die em.json später importiert, bleibt die importierte, und ein Hinweis meldet dies: *«The previous file's narrative was not kept: the em.json imported on … is newer, and its narrative wins. Backup copy of the previous file in ….»* Bis 5.13.127-alpha gewann immer die importierte: Die im Panel vorbereiteten und geschriebenen Kapitel verschwanden beim nächsten Export, mit einem Hinweis, der fälschlich die Form der Datei verantwortlich machte.

**Andere Änderungen**, die in EMStudio an der Datei vorgenommen wurden — Knotenpositionen, neu geschriebene Beschreibungen —, **gehen verloren**, wie bisher: Die Datei wird aus der Datenbank neu erstellt. Erhalten bleibt nur die Erzählung.

Bevor pyArchInit eine Datei neu schreibt, die eine Erzählung enthält, legt es daneben eine **Sicherheitskopie** an: `<Stätte>.em.json.bak` (jeder neue Export ersetzt die vorherige Kopie).

War die frühere Datei nach Sondagen geteilt (Versionen bis 5.13.108-alpha konnten einen Graphen je Sondage exportieren), hat die neue Datei beim ersten erneuten Export **einen einzigen Graphen** für die ganze Stätte: Die Graphen haben andere Namen, und die Erzählung **kann nicht in die neue Datei übernommen werden**. Ein Hinweis meldet dies: *«The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …»*. Der Text geht nicht verloren: Er liegt in der `.bak`-Kopie, die allerdings beim nächsten Export einer Datei mit Erzählung ersetzt wird — legen Sie sie an einem sicheren Ort ab. Brauchen Sie die alte Erzählung, öffnen Sie diese Kopie (umbenannt in eine `.em.json`-Datei mit einem anderen Namen); andernfalls erzeugen Sie die Kapitel in der neuen Datei neu (§10.5). Ab 5.13.109-alpha hat die Datei immer einen einzigen Graphen, und die Erzählung bleibt von einem Export zum nächsten erhalten.

Kann die vorherige Datei nicht gelesen werden (zum Beispiel eine nur halb geschriebene Datei), läuft der Export trotzdem weiter: Die unlesbare Datei wird in `<Stätte>.em.json.broken` **umbenannt**, und ein Hinweis meldet *«The previous file cannot be read (…): its narrative, if any, was not kept.»*

> **Die Erzählung liegt nicht in der Datenbank von pyArchInit: Sie lebt nur in der em.json.** Ein Datenbank-Backup kopiert sie nicht. Kopieren Sie den Ordner `pyarchinit_EM_folder` von Zeit zu Zeit.

### 10.9 Über den Eintrag «Esporta sito in em.json…»

Der Eintrag **Extended Matrix → Esporta sito in em.json…** schreibt dieselbe Datei `<Stätte>.em.json` in `pyarchinit_EM_folder`. Am Ende zeigt er «Esportato `<Pfad>`» (Exportiert) mit den Zahlen der Knoten, Kanten und Hinweise (der Text der Hinweise steht in den Details des Fensters) sowie **drei Schaltflächen**:

| Schaltfläche | Was sie tut |
|--------------|-------------|
| **Apri in EMStudio** (In EMStudio öffnen) | Öffnet die Datei in EMStudio; ist EMStudio nicht installiert, wird angeboten, es zu installieren. |
| **Narrativa con l'AI** (Erzählung mit KI) | Erscheint **nur, wenn eine KI eingerichtet ist** (§10.2): Öffnet das Matrix-Panel bereits im Tab Narrative. |
| **Chiudi** (Schließen) | Schließt das Fenster. |

<!-- IMMAGINE: Screenshot des Abschlussfensters von «Esporta sito in em.json…» mit den drei Schaltflächen -->
![Esporta sito in em.json: drei Schaltflächen](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Abbildung 7: Das Abschlussfenster von «Esporta sito in em.json…»*

### 10.10 Die Einheiten auf der Karte

Ab Version **5.13.108-alpha** bringt der Tab Narrative die Einheiten, von denen ein Kapitel spricht, auf die **QGIS-Karte**, und zwar auf zwei Arten:

- **Eine einzelne Einheit: Klicken Sie auf ihren Namen.** Im Text des gewählten Kapitels sind die Namen der zitierten Einheiten **Links**: Ein Klick wählt diese Einheit im geladenen SE-Layer aus und rückt die Karte auf sie, mit einem Aufblitzen. Es wird nichts geöffnet.
- **Alle zusammen: «Show on the map»** (*Mostra sulla mappa*; Auf der Karte anzeigen), in der zweiten Schaltflächenzeile, zwischen «Prepare the chapters» (Kapitel vorbereiten) und «Export…» (Exportieren…). Die Schaltfläche wählt alle Einheiten, von denen das gewählte Kapitel spricht, gemeinsam aus und rückt sie ins Bild: die im Fließtext zitierten oder, wenn der Fließtext keine zitiert (zum Beispiel weil das Kapitel noch nicht geschrieben ist), alle Einheiten seines Bandes (der Epoche). Die Auswahl ist eine einzige je Layer — sie ersetzt die bisherige —, und der Bildausschnitt umfasst alle gefundenen Geometrien, die kurz aufblitzen.

<!-- IMMAGINE: Screenshot von QGIS mit den Einheiten des Kapitels, auf der Karte ausgewählt, und oben der Meldungsleiste «Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.» -->
![Die Einheiten des Kapitels auf der Karte](images/36_extended_matrix_s3dgraphy/09_unita_sulla_mappa.png)
*Abbildung 8: Die Einheiten, von denen ein Kapitel spricht, auf der Karte ausgewählt, und die Meldungsleiste*

Im Projekt muss bereits ein Layer mit den Geometrien der SE geladen sein, zum Beispiel die **US-Ansicht** (US view) von pyArchInit: Der Tab sucht unter den bereits geladenen Layern, wie die Schaltfläche «Zoom sulla geometria» (Auf die Geometrie zoomen) des Tabs Units (Tutorial 01), und erkennt die Einheiten an den Feldern `sito`, `area` und `us`. **Das Projekt wird nicht verändert**: Es wird kein Layer hinzugefügt, nur die Auswahl und der Kartenausschnitt ändern sich. Seit **5.13.110-alpha** gilt: Tragen mehrere Layer dieselben Felder – wie die US-Ansicht (Polygone) und die Höhenansicht (Punkte) –, versucht der Tab zuerst die vollste Geometrie: Polygone, dann Linien, dann Punkte; die Reihenfolge der Layer in der Legende zählt nur, wenn alles andere gleich ist. Das gilt auch für die Schaltfläche «Zoom sulla geometria»: Die US-Ansicht muss nicht mehr an den Anfang der Legende gesetzt werden.

Die Meldungsleiste («Narrative») sagt, was gefunden wurde, zum Beispiel «Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.» (5 von 6 Einheiten hervorgehoben in «US view», 7 Geometrien; nicht gezeichnet: 1.US9). Der Name in Anführungszeichen ist der des Layers, in dem die Einheiten gefunden wurden, so wie er im Layer-Bedienfeld von QGIS steht; eine Einheit kann mehr als eine Geometrie haben, also können die Geometrien zahlreicher sein als die Einheiten. Gesucht werden nur Einheiten, die Zeilen des SE-Formulars sind: Ein Dokument oder ein Kontinuitätsknoten hat keine Geometrie und fließt nicht in die Zählung ein. Sind mehr als fünf Einheiten nicht gezeichnet, enden die Namen bei den ersten fünf, gefolgt von «…» und der Gesamtzahl.

Ein Klick auf einen Namen, der keine Zeile des SE-Formulars ist, findet nichts, und die Meldungsleiste sagt es. Hat kein geladener Layer die Felder, um die Einheiten zu erkennen, sagt es die Meldung: Laden Sie die US-Ansicht (§10.13).

### 10.11 Die Fotos der Einheiten und das PDF

Ab Version **5.13.108-alpha** zeigt die Erzählung auch die **Fotos** der Einheiten, von denen sie spricht — im Text des Tabs und in den Exporten — und lässt sich zusätzlich als **druckfähiges PDF** speichern.

**Im Text des Kapitels.** Unter dem Absatz, in dem eine Einheit zum ersten Mal genannt wird, erscheinen **bis zu zwei Vorschaubilder** ihrer Medien: dieselben wie im Tab Units, gelesen aus dem Vorschaubilder-Ordner des Projekts; darunter stehen in kleiner Schrift der Name der Einheit und die Namen der Medien. Wird die Einheit im selben Kapitel noch einmal genannt, werden die Fotos nicht wiederholt.

**In den Exporten.** In allen drei Formaten tritt für jede im Text zitierte Einheit, die Bilder auf der Festplatte hat, ein **Streifen mit einem oder zwei nebeneinanderliegenden Fotos** an die Stelle der Textzeile der Einheit, mit dem Namen der Einheit als Bildunterschrift: Verwendet wird die verkleinerte Kopie, falls vorhanden, sonst das Vorschaubild. Nicht im Text zitierte Einheiten bleiben eine Textzeile. Die Fotos sind in die Datei eingebettet: HTML und DOCX schreibt die Bibliothek s3dgraphy, das PDF pyArchInit.

**Das druckfähige PDF.** Es ist ein A4-Dokument, das pyArchInit mit ReportLab schreibt, in der Schrift Cambria wie die anderen PDFs des Plugins (liegt die Schriftdatei nicht im Ordner `bin` von pyArchInit, wird Helvetica verwendet). Es enthält den Titel, die Verantwortlichen («edited by») und das Modell als Assistent («with the assistance of»); oben steht außerdem, falls es nicht validierte Entwürfe gibt, ein Hinweis mit ihrer Anzahl; dann alle Kapitel wie in den anderen Formaten, jedes mit seinem Text — die zitierten Einheiten mit ihrem Namen, und vor jedem nicht validierten Absatz eine Zeile «non validato da una persona» (nicht von einer Person validiert), ohne das Zeichen ⚠ — gefolgt von den Fotos mit ihrer Bildunterschrift und den übrigen Einheiten in kleiner Schrift; am Ende die Quellen. In der Fußzeile stehen «Generated by pyArchInit on …» (von pyArchInit erstellt am …) mit dem Datum und die Seitenzahl.

<!-- IMMAGINE: Screenshots nebeneinander: der Text eines Kapitels mit den Vorschaubildern unter der ersten Nennung einer Einheit und eine Seite des druckfähigen PDFs mit dem Fotostreifen und der Bildunterschrift -->
![Fotos der Einheiten im Text und im PDF](images/36_extended_matrix_s3dgraphy/10_foto_e_pdf.png)
*Abbildung 9: Die Fotos der Einheiten im Text des Kapitels und auf einer Seite des PDFs*

**Was es braucht.** Die Fotos stehen nicht in der em.json: Sie werden aus der Datenbank und den Ordnern des Projekts gelesen. Nötig sind also die verknüpfte Datenbank (die Matrix wurde aus dem Projekt geöffnet), die in der Konfiguration eingestellten Pfade **Thumbnail path** und **Image resize** (Tutorial 01) und die Dateien auf der Festplatte; für den Text genügt der Vorschaubilder-Ordner. Bilder auf einem entfernten Speicher werden nicht verwendet. Fehlt etwas, gibt es keine Meldung: Die Fotos erscheinen einfach nicht, und der Export gelingt trotzdem (§10.13).

### 10.12 Warnungen

- **Schließen Sie EMStudio, bevor Sie generieren oder validieren.** Hat EMStudio die Datei geöffnet, gewinnt, wer zuletzt schreibt.
- **Eine KI schreibt nur aus dem, was sie im Graphen findet, und sie kann sich irren.** Die Regeln zügeln sie, machen sie aber nicht unfehlbar: Lesen Sie jedes Kapitel, bevor Sie es validieren.
- **Bei einem Online-Provider verlassen die Daten Ihren Computer.** Das Briefing jedes Kapitels (Namen, Definitionen, Beschreibungen und Beziehungen der Einheiten) und das der Presentation (Name der Stätte, Ortsnamen, Orte, Epochen, Dokumente und die in den SE-Formularen genannten Personen) werden an den gewählten Dienst gesendet; mit Ollama oder LM Studio bleiben sie lokal.
- **Die Datei wird am Ende geschrieben.** Die Generierung speichert, wenn sie fertig ist, auch wenn Sie sie abgebrochen haben: Schließen Sie QGIS nicht, während die KI schreibt. Das Speichern ist sicher: Die Datei wird daneben geschrieben, zurückgelesen und ersetzt erst dann die eigentliche Datei; geht etwas schief, **bleibt die vorherige Datei, wie sie war**.
- **Öffnen Sie die Matrix nicht erneut, während die KI schreibt.** Der Tab bleibt auf der vorherigen Datei und warnt: *«Generation in progress: wait for it to finish, or press Cancel, before changing file.»*
- **Der Text wird in EMStudio bearbeitet**, nicht in pyArchInit.
- Die Erzählung und die Knoten, die sie tragen (KI-Autor, Prompts), **erscheinen nicht in der Zeichnung der Matrix**.

### 10.13 Fehlerbehebung

| Meldung (en / it) | Ursache | Lösung |
|-------------------|---------|--------|
| «No AI configured…» / «Nessuna AI impostata…» | Keines der vier Fenster aus §10.2 hat ein Modell (und, bei OpenAI und Anthropic, den API-Key). | Stellen Sie Provider und Modell — und den Key — in einem dieser Fenster ein und **öffnen Sie dann die Matrix erneut**: Der Tab liest die Einstellungen nur beim Öffnen neu ein. Auch ohne KI können Sie die Kapitel vorbereiten, validieren, exportieren und EMStudio öffnen. |
| «No narrative in the file…» / «Nessuna narrativa nel file…» | Die Datei hat noch keine Erzählung (beim ersten Mal normal). | Klicken Sie auf **Prepare the chapters** (Gliederung) oder **Generate with AI** (Gliederung und Text). Die Zahl N zählt die Kapitel der Epochen und Aktivitäten, die die Gliederung haben wird (eine Epoche ohne Einheiten bekommt keines); die Meldung «Chapters prepared» zählt auch «Presentation» und gegebenenfalls «Where it is». «Generate with AI» schreibt außerdem die «Presentation», die N nicht mitzählt: Der Fortschritt zählt ein Kapitel mehr. |
| «EMStudio is not installed…» / «EMStudio non risulta installato…» | Das Programm wurde auf dem Computer nicht gefunden. | Verwenden Sie den Menüeintrag **Extended Matrix → Installa EMStudio…** (er heißt so bei jeder Sprache von QGIS). |
| «truncated» / «troncato» neben dem Zustand | Das Modell hat an der Längengrenze angehalten, und der Text endet mittendrin. | Klicken Sie vor dem Validieren auf **Regenerate chapter**; passiert es erneut, beenden Sie das Kapitel in EMStudio. |
| «N chapters generated, M failed: `<title>` — `<reason>`» / «N capitoli generati, M falliti: …» | Der Provider hat die Anfrage abgelehnt (ungültiger Key, Kontingent, Modell nicht verfügbar) oder der lokale Server antwortet nicht. «the model wrote nothing» bedeutet, dass die Antwort leer war. | Beseitigen Sie die Ursache und klicken Sie erneut auf **Generate with AI**: Es schreibt nur die Kapitel, die noch «to be written» sind. |
| «The previous file cannot be read (…)» / «Il file precedente non si legge (…)» | Beim erneuten Export war die vorhandene Datei keine lesbare em.json. | Der Export lief weiter: Die unlesbare Datei wurde neben der neuen als `….broken` aufbewahrt, und die Erzählung, die sie enthielt, wurde, falls vorhanden, nicht in die neue Datei übernommen. Brauchen Sie die Erzählung, stellen Sie sie aus dieser Datei oder aus einem Backup wieder her. |
| «The previous file's narrative (graphs: …) did not travel into the new file…» / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | Die frühere Datei war nach Sondagen geteilt (Versionen bis 5.13.108-alpha): Die Graphen haben andere Namen, und die Erzählung kann nicht übernommen werden. | Die frühere Datei liegt in der `.bak`-Kopie: Öffnen Sie diese, wenn Sie die alte Erzählung brauchen, oder erzeugen Sie die Kapitel in der neuen Datei neu. |
| «Could not write … The previous file is intact.» / «Non sono riuscito a scrivere … Il file precedente è intatto.» | Das Speichern ist fehlgeschlagen (Datenträger voll, gesperrte Datei, Berechtigungen). | Beheben Sie das Problem und wiederholen Sie den Vorgang: Die in dieser Sitzung generierten Kapitel waren nicht gespeichert worden. |
| «DocX export needs python-docx — install the extra: …» (immer auf Englisch) | Das Paket `python-docx` ist im Python von QGIS nicht installiert: Es wird nur für DOCX gebraucht. | Installieren Sie `python-docx` (es gehört zu den Abhängigkeiten des Plugins) oder exportieren Sie als HTML, das nichts braucht. |
| «None of the loaded layers has the fields to recognise the units…» / «Nessuno dei layer caricati porta i campi per riconoscere le unità…» | Das geöffnete Projekt hat keinen Layer mit den Feldern `sito`, `area` und `us` der Einheiten (zum Beispiel die US-Ansicht von pyArchInit): Der Tab sucht nur unter den bereits geladenen Layern. | **Laden Sie die US-Ansicht** von pyArchInit (oder einen Layer mit denselben Feldern) ins Projekt und klicken Sie erneut auf den Namen oder auf **Show on the map** (Auf der Karte anzeigen). Der Tab fügt von sich aus keine Layer hinzu. Seit 5.13.110-alpha müssen Sie sie nicht an den Anfang der Legende setzen: Bei gleichen Feldern probiert der Tab zuerst die Polygone (§10.10). Aus dem SE-Formular mit gewähltem Stil geladen (Fenster «Style Choice», Tutorial 14), trägt die US-Ansicht außerdem die Nummer der Einheit in einem Kreis. Seit 5.13.111-alpha trägt auch die Höhenansicht (Punkte), aus dem SE-Formular geladen, den Höhenwert (zwei Nachkommastellen) über dem Symbol. Stil und Beschriftungen der Ansicht werden im Fenster «View styles» eingestellt (Menüeintrag «View styles…», Tutorial 14); seit 5.13.112-alpha hat ein dort gespeicherter Standardstil beim Laden Vorrang. |
| Keine Meldung: Die Fotos erscheinen weder im Text des Kapitels noch in den Exporten | Die Fotos werden aus der Datenbank und den Ordnern des Projekts gelesen, und etwas fehlt: Die Datenbank ist nicht verknüpft (die Matrix wurde ohne sie geöffnet), der Pfad **Thumbnail path** existiert auf diesem Computer nicht oder ist ein entfernter Speicher, die Dateien liegen nicht auf der Festplatte, oder die Einheit ist keine Zeile des SE-Formulars oder hat keine Medien. | Prüfen Sie den Tab **Units**: Zeigt die Einheit dort ihre Vorschaubilder, finden Sie sie auch hier. Öffnen Sie andernfalls die Matrix aus dem Projekt, prüfen Sie **Thumbnail path** und **Image resize** in der Konfiguration (Tutorial 01) und ob die Dateien auf dem Computer liegen: Bilder auf einem entfernten Speicher werden nicht übernommen. Der Export gelingt trotzdem, ohne Fotos. |

---

## Referenzen

- Upstream-Issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit-Repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
