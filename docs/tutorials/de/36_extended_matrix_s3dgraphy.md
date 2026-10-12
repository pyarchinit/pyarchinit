# Tutorial 36: Extended Matrix Export und s3dgraphy Bridge

## Einleitung

Ab Version **5.2.0-alpha** integriert PyArchInit eine **bidirektionale Bridge** mit der Bibliothek **s3dgraphy** (Extended-Matrix-Datenmodell von Emanuel Demetrescu). Die Bridge erlaubt:

- **Export** des stratigraphischen Diagramms als Extended Matrix in **em.json**, dem Format, das EMStudio öffnet (der alte GraphML-Export ist im Ruhestand)
- **Re-Import** von in yEd vorgenommenen Änderungen (SE-Bewegungen zwischen Perioden/Gruppen) zur Aktualisierung der SQL-Datenbank
- **Anhängen von Paradata** (Author / License / Embargo) auf Stättenebene
- **Gruppieren** von SE nach Dimension (struttura, area, attivita, settore, ambient, saggio, quad_par oder Ad-hoc-Gruppen)

Aktueller Tag: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Voraussetzungen

- SQLite-Datenbank (PostgreSQL noch nicht unterstützt)
- **Phase 1 node_uuid-Migration** wird beim DB-Öffnen automatisch angewendet
- **yEd Graph Editor** zur Anzeige (https://www.yworks.com/products/yed)

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

### 2.2.1 Sondagen: ein Graph oder einer je Sondage

Eine Gruppe von drei Wahlmöglichkeiten im selben Fenster entscheidet,
**wie die em.json geteilt wird**, wenn die Ausgrabung mehrere Sondagen
hat:

- **Automatisch**: ein einziger Graph, wenn die Stätte eine Sondage
  hat, ein Graph je Sondage, wenn sie mehrere hat. Das ist die
  Ausgangswahl.
- **Ein einziger Graph für die ganze Stätte**: die ganze Ausgrabung in
  einem Graphen, wie bisher.
- **Ein Graph je Sondage**: **eine einzige Datei**, die einen Graphen je
  Sondage enthält, plus einen für die Einheiten ohne Angabe.
  Beziehungen, die aus der Sondage **hinausführen**, gehen nicht
  verloren: sie bleiben in der Datei als Verbindungen zwischen Graphen
  (`graph.links`).

> **EMStudio 1.6.0 zeigt jeweils einen.** Die Datei ist richtig — der
> Leser der Bibliothek liest alle Graphen wieder ein, ohne Warnung —
> aber EMStudio öffnet den in `active_graph_id` genannten Graphen, also
> die erste Sondage, und hat keine Auswahl für die anderen. Die Matrix
> in QGIS, **Matrix zeigen**, vereint sie alle und zeichnet die ganze
> Ausgrabung. Gemessen am 2026-10-12 an der Beispielstätte: 4 Graphen
> (52/49/56/51 Knoten), 32 Verbindungen zwischen Sondagen, 51 Einheiten
> in der vereinten Matrix.

Die Sondage ist das Feld **Saggio** des SE-Formulars: Einheiten ohne
Eintrag landen in einem eigenen Graphen, in derselben Datei.

### 2.3 Klick auf "Esporta"

Die Dateien, die entstehen, je nach angehakten Formaten:
- `<Stätte>.em.json` — Extended Matrix, in EMStudio zu öffnen oder an einen Raum zu übergeben
- `Extended_Matrix_<site>[_<area>].dot` — Graphviz DOT, für die klassische Harris-Matrix
- `Extended_Matrix_<site>[_<area>]_phased.json` — Ansicht pro Epoche

> **Orte kommen nicht in die em.json.** Stätte, Areal und Sektor bleiben im Formular jeder Einheit, reisen aber nicht mehr als Gruppenknoten mit ihren Kanten: solange die Datei auch nur eine `is_in_location`-Kante enthält, stapelt die **Matrix**-Ansicht von EMStudio alle Einheiten im ersten Band, statt sie nach Epoche zu verteilen (am 2026-10-08 gegen EMStudio 1.6.0-dev.26 gemessen, per Bisektion über fünf Dateien). Es geht keine Information verloren — nur eine Art, sie darzustellen.

Die Schlussmeldung listet die Dateien auf und, für em.json, **wie viele Knoten und wie viele Kanten** herauskamen, samt etwaigen Hinweisen.

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

## 4. Visueller Stil pro Dimension (5.5.1-alpha + 5.6.0-alpha)

Jede Gruppendimension hat eine eigene Farbe im GraphML:

| Dimension | Fill (50% Transparenz) | Border |
|---|---|---|
| `area` | Pastellrosa `#FFE0E680` | `#C84A5F` |
| `struttura` | Pastellorange `#FFE6CC80` | `#C66B33` |
| `attivita` | Pastellgelb `#FFF5CC80` | `#A89A33` |
| `settore` | Pastellgrün `#E6FFCC80` | `#6BC633` |
| `ambient` | Pastellaqua `#CCFFE680` | `#33A86B` |
| `saggio` | Pastellblau `#CCF5FF80` | `#3389A8` |
| `quad_par` | Pastellviolett `#E0CCFF80` | `#6633C6` |
| `adhoc` | Pastellgrau `#F5F5F580` | `#666666` |

Ab 5.6.0-alpha werden `LocationNodeGroup`-Elemente nach `kind` unterschieden:

| `kind` | Fill (50% Transparenz) | Border |
|---|---|---|
| `toponym` | Pastell-Lavendel `#E6E6FA80` | `#9370DB` |
| `study` | Pastell-Elfenbein `#FFFFE080` | `#888888` |
| `functional` | Pastell-Cyan `#E0FFFF80` | `#008B8B` |

Die 50%-Alpha lässt die Epochen-Swimlanes hinter dem Gruppenrechteck sichtbar.

### 4.1 Toponymkette (5.6.0-alpha)

Die Felder `site_table.{nazione, regione, provincia, comune}` werden automatisch als rekursive `LocationNodeGroup(kind="toponym")`-Kette emittiert (Parent: nazione → regione → provincia → comune). Leere Verwaltungsebenen werden übersprungen, ohne die Kette zu unterbrechen. Eine Cross-Site-Deduplizierung garantiert, dass dasselbe `comune` in 2 Sites zu **einem geteilten Knoten** im GraphML wird.

---

## 4.2 Mehrdimensionale Mitgliedschaft (5.6.0-alpha)

Ab 5.6.0-alpha kann eine SE dank des m:n-Modells mit `is_primary`-Flag **mehreren Dimensionen gleichzeitig** angehören. Nur die primäre Dimension wird zum sichtbaren yEd-Folder; die anderen erscheinen als **Inline-Badges** unter dem SE-Knoten und als JSON in `<data key="s3d:other_locations">` für Downstream-Tools.

Beispiel: Eine SE mit `struttura=basilica` und `area=B` (primär `struttura`) ergibt:
- yEd-Folder "struttura: basilica" als sichtbaren Parent;
- unter dem SE-Knoten ein Inline-Badge `also: B (study), TestCity (toponym)`;
- im GraphML das Attribut `s3d:other_locations` mit JSON-Array der sekundären Mitgliedschaften.

Die Primärdimension folgt einer vorgegebenen Reihenfolge, mit `struttura` an erster Stelle; `toponym` ist nie primär.

---

## 5. Round-trip (Import-Tab)

> **Was importiert werden kann**: der Import-Tab liest nun auch **em.json** — aus EMStudio oder von einem StratiGraph-Knoten — und wählt den Leser nach der Dateiendung; eine yEd-`.graphml` wird für ältere Dateien weiterhin angenommen. Das Verfahren unten, SE zwischen Gruppen zu verschieben, betrifft den Weg über yEd/GraphML.

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
- **Ein brauner Rand ist Mauerwerk.** USM-Einheiten — WSU, MSE, UEM, USZ, ΤΣΜ in den anderen Sprachen — haben dasselbe Kästchen wie die US, mit braunem statt rotem Rand.

---

## 10. Narrative (Erzählung) mit KI

Ab Version **5.13.106-alpha** hat das Matrix-Panel innerhalb von QGIS (§2.2, «Vedi la matrice») in seiner rechten Spalte zwei Tabs: **Units** (*Unità*; Einheiten) — das Formular der gewählten Einheit, der Zoom auf die Geometrie und die Medien, wie bisher — und **Narrative** (*Narrativa*; Erzählung), neu. Der Tab Narrative lässt eine KI die **Geschichte der Stätte** schreiben, ein Kapitel je Epoche, und erlaubt Ihnen anschließend, sie zu lesen, von einer Person validieren zu lassen und als HTML oder DOCX zu exportieren. Er liest und schreibt **dieselbe em.json**, die EMStudio öffnet, im Format der s3dgraphy-Bibliothek: Die Erzählung, die Sie hier sehen, ist dieselbe, die EMStudio in seinem Tab *Narrative* zeigt.

> **Keine neuen Einstellungen.** Der Tab hat kein eigenes Konfigurationsfenster: Er verwendet die KI, die Sie bereits an anderer Stelle in pyArchInit eingerichtet haben (§10.2).

> **Die KI schreibt Entwürfe, keine endgültigen Texte.** Jeder vom Modell geschriebene Absatz bleibt ein «AI draft» (KI-Entwurf), bis eine Person ihn validiert (§10.6), und trägt in exportierten Dokumenten das Zeichen ⚠.

Die Namen der Tabs und der Schaltflächen des Tabs Narrative gibt es auf Italienisch und auf Englisch: **auf Italienisch, wenn QGIS auf Italienisch läuft, auf Englisch bei jeder anderen Sprache**. Hier stehen immer beide. Die Menüeinträge und Dialogfenster des Plugins (wie «Vedi la matrice…» oder die drei Schaltflächen aus §10.9) gibt es dagegen nur auf Italienisch; die deutsche Übersetzung steht in Klammern.

### 10.1 Den Tab Narrative öffnen

1. Öffnen Sie das Menü **Plugins → pyArchInit - Archaeological GIS Tools** und wählen Sie den Eintrag **Extended Matrix → Vedi la matrice…** (Die Matrix ansehen).
2. Wählen Sie die **Stätte**.
3. Hat die Stätte **Sondagen** (*saggi*), fragt pyArchInit «Il sito ha N saggi. Come divido il file?» (Die Stätte hat N Sondagen. Wie teile ich die Datei auf?) mit zwei Antworten: «Un grafo per ogni saggio (…)» (ein Graph je Sondage), die Voreinstellung, oder «Un grafo solo per tutto il sito» (ein einziger Graph für die ganze Stätte). Es ist dieselbe Wahl wie in §2.2.1 und beim Eintrag «Esporta sito in em.json…»: Die beiden Einträge schreiben **dieselbe Datei**, in derselben Form.
4. pyArchInit exportiert die Stätte aus der Datenbank nach `<home>/pyarchinit_EM_folder/<Stätte>.em.json` — `<home>` ist `~/pyarchinit_5` oder der Ordner, den die Umgebungsvariable `PYARCHINIT_HOME` angibt — und öffnet das Panel **«Matrice — `<Stätte>`»**, rechts am QGIS-Fenster angedockt. Der Dateiname ist der Name der Stätte, wobei Sonderzeichen durch «_» ersetzt werden (zum Beispiel wird «Scavo 1» zu `Scavo_1.em.json`).
5. Klicken Sie in der rechten Spalte des Panels auf den Tab **Narrative**.

<!-- IMMAGINE: Screenshot des Menüs Plugins → pyArchInit - Archaeological GIS Tools mit dem Eintrag «Extended Matrix → Vedi la matrice…» -->
![Menü Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Abbildung 1: Der Eintrag «Extended Matrix → Vedi la matrice…» im Menü des Plugins*

<!-- IMMAGINE: Screenshot der Frage zu den Sondagen mit den zwei Antworten -->
![Frage zu den Sondagen](images/36_extended_matrix_s3dgraphy/02_domanda_saggi.png)
*Abbildung 2: Die Frage zu den Sondagen: ein Graph je Sondage oder ein einziger Graph*

<!-- IMMAGINE: Screenshot des rechts angedockten Matrix-Panels mit den Tabs Units und Narrative -->
![Panel mit zwei Tabs](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Abbildung 3: Das Matrix-Panel mit den Tabs Units und Narrative*

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
┌─ Units ─┬─ Narrative ────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the     │
│ file open, close it first: the last writer wins.                 │
├──────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                     │
│ Early 15th century — AI draft                                    │
│ 15th century — endorsed                                          │
│ Modern age — AI draft, truncated                                 │
├──────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.            │
├──────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                 │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]             │
│ [Prepare the chapters]  [Export…]  [Open in EMStudio]  [Cancel]* │
└──────────────────────────────────────────────────────────────────┘
```

\* Die Fortschrittszeile und die Schaltfläche «Cancel» sind nur sichtbar, während die KI schreibt. In diesem Schema sind die Listenzeilen die der Beispielstätte.

<!-- IMMAGINE: Screenshot des Tabs Narrative mit der Kapitelliste, dem Text des gewählten Kapitels und den sechs Schaltflächen -->
![Tab Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Abbildung 4: Der Tab Narrative*

Von oben nach unten:

- **die Statuszeile**: das verwendete Modell (§10.2) und der Hinweis *«If EMStudio has the file open, close it first: the last writer wins.»* (Hat EMStudio die Datei geöffnet, schließen Sie es zuerst: Wer zuletzt schreibt, gewinnt.);
- **die Kapitelliste**, eine Zeile je Kapitel: *Titel — Zustand*. Beim Export mit einem Graphen je Sondage (§2.2.1) hat jede Sondage ihre eigene Erzählung, und jeder Zeile geht der Name der Sondage in eckigen Klammern voran, zum Beispiel `[Saggio A] 15th century — AI draft`;
- **der Text des gewählten Kapitels**: der Fließtext, in dem die Einheiten mit ihrem Namen zitiert werden. Hat das Kapitel noch keinen Text, sehen Sie seinen Platzhalter «[to be written: …]»;
- **die Fortschrittszeile**, nur während der Generierung: «Chapter 3 of 9 · 15th century»;
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
| **Generate with AI** | Genera con l'AI | Schreibt **nacheinander** alle Kapitel der Epochen (und der Aktivitäten), die noch «to be written» sind; bereits geschriebene bleiben unberührt. Gibt es noch keine Erzählung, wird zuerst die Gliederung angelegt. Zeigt den Fortschritt und die Schaltfläche **Cancel**. Nur aktiv, wenn eine Datei geöffnet und eine KI eingerichtet ist. |
| **Regenerate chapter** | Rigenera capitolo | Schreibt **das in der Liste gewählte Kapitel** neu (bei mehreren Sondagen nur das Kapitel der gewählten Sondage): Der nicht validierte KI-Entwurf wird ersetzt — aber erst, wenn das Modell geantwortet hat: Schlägt der Aufruf fehl, bleibt der frühere Entwurf erhalten —, und bereits validierte Blöcke bleiben. Die Schaltfläche wird aktiv, wenn Sie ein Kapitel einer Epoche oder einer Aktivität wählen und eine KI eingerichtet ist; bei «Presentation» und «Where it is» bleibt sie deaktiviert. |
| **Endorse…** | Convalida… | Öffnet ein Menü mit «This chapter» und «All chapters» und fragt dann, wer validiert (§10.6). Aktiv, wenn eine Erzählung vorhanden ist. |
| **Prepare the chapters** | Prepara i capitoli | Legt **nur die Gliederung** der Kapitel an, ohne KI: Das geht auch, wenn keine KI eingerichtet ist, sodass Sie in EMStudio von Hand schreiben können. Bereits geschriebener Text bleibt unberührt, und die Kapitel neuer Epochen werden hinzugefügt. Ergebnis: «Chapters prepared: N.» |
| **Export…** | Esporta… | Speichert die Erzählung als HTML oder DOCX (§10.7). Aktiv, wenn eine Erzählung vorhanden ist. |
| **Open in EMStudio** | Apri in EMStudio | Öffnet die em.json in EMStudio. Ist EMStudio nicht vorhanden, verweist die Meldungsleiste auf den Menüeintrag **Extended Matrix → Installa EMStudio…** (EMStudio installieren). |
| **Cancel** | Annulla | Erscheint nur während der Generierung: Die KI hält **nach dem laufenden Kapitel** an, und das bisher Geschriebene wird gespeichert. |

Während der Generierung sind alle Schaltflächen deaktiviert, außer **Cancel**.

### 10.4 Was die KI schreibt

**Welche Kapitel.** Die Gliederung stammt aus der s3dgraphy-Bibliothek (die Vorlage «site_story»):

- **Presentation** (Vorstellung) und **Where it is** (Lage) sind kanonische Kapitel: Sie bleiben Platzhalter «[to be written: …]», die in EMStudio von Hand zu schreiben sind, weil der Graph nichts enthält, woraus man sie schreiben könnte, ohne etwas zu erfinden. «Where it is» gibt es nur, wenn der Graph eine geographische Position trägt. Die KI generiert sie nicht.
- **Ein Kapitel je Epoche** (Periode/Phase), die Einheiten hat, von der ältesten zur jüngsten. Der Titel ist der Name der Epoche, nämlich die «Datazione estesa» (erweiterte Datierung) der Periodisierung; fehlt sie, entsteht ein allgemeiner Name wie «Period 8 Phase 1»: Füllen Sie sie im Periodisierungsformular aus, um gut lesbare Titel zu erhalten. Eine Einheit erscheint im Kapitel der Epoche, in der sie entsteht, und in den Kapiteln der Epochen, in denen sie fortbesteht.
- **Ein Kapitel je Aktivität**, wenn der Graph Aktivitätsgruppen enthält. Eine aus der Datenbank exportierte Stätte hat normalerweise keine — das Feld Aktivität des SE-Formulars reist als Eigenschaft der Einheit mit —, und dann sind die Kapitel die der Epochen.

**Was das Modell erhält.** Für jedes Kapitel erhält das Modell ein *Briefing* mit folgenden Angaben für jede Einheit: Name, Typ und Beschreibung; die ausgefüllten Felder des SE-Formulars (stratigraphische und interpretative Definition, Interpretation, Periode und Phase, Datierung, Aktivität, Struktur, Sondage, Raum, Sektor, Areal); die Epochen; **die stratigraphischen Beziehungen** zu den anderen Einheiten (überdeckt, schneidet, verfüllt, lehnt an, gleich …) mit deren Namen; und, falls vorhanden, die verknüpften dokumentarischen Quellen. Die Einheiten werden **von der ältesten zur jüngsten** aufgelistet, den Beziehungen folgend. Bei mehr als **80 Einheiten** je Kapitel wird das Briefing auf die ersten 80 gekürzt. Außerdem gilt eine Obergrenze für seine Länge (etwa 25.000 Zeichen): Wird sie überschritten, werden die langen Texte der Formulare gekürzt, wiederholte Beziehungen und Belegketten entfallen und, wenn das immer noch nicht reicht, werden die jüngsten Einheiten ausgelassen. In beiden Fällen wird dem Modell mitgeteilt, wie viele Einheiten fehlen.

**Die Regeln.** Das Modell erhält die fünf Regeln der Bibliothek: nur schreiben, was der Kontext stützt (keine erfundenen Datierungen, Materialien, Funktionen oder Ereignisse); die Unsicherheit bewahren (eine virtuelle Einheit ist eine Hypothese, keine Tatsache); keine Quelle zitieren, die nicht vorhanden ist; Fließtext schreiben, ohne Listen und Überschriften; offen sagen, wenn der Kontext zu dürftig ist. Verlangt werden ein bis drei Absätze.

**Die Sprache.** Der Text steht in der **Sprache der Erzählung**, die festgelegt wird, wenn die Gliederung zum ersten Mal angelegt wird: **Italienisch, wenn QGIS in diesem Moment auf Italienisch läuft, Englisch bei jeder anderen Sprache** (das Modell erhält seine Anweisungen nur in diesen beiden Sprachen). Eine bereits vorhandene Erzählung behält ihre Sprache, auch wenn Sie die Sprache von QGIS später ändern. Dasselbe gilt für die Titel der kanonischen Kapitel und für die Platzhalter.

**Wie es gespeichert wird.** Im Format der Bibliothek, demselben, das EMStudio liest: ein Erzählknoten (`NarrativeNode`), der die Kapitel enthält; jeder vom Modell geschriebene Absatz ist ein Block «AI draft», der dem **KI-Autor** dieses Modells zugeschrieben wird; der verwendete **Prompt** wird als Extraktor registriert, der mit den Quellen verknüpft ist, sodass sich nachvollziehen lässt, was gefragt wurde. Die im Text zitierten Einheiten sind **Erwähnungen** (`[[name]]`): In der Datei bleiben sie mit dem Knoten der Einheit verknüpft, und im Tab und in den Exporten erscheinen sie mit ihrem Namen. Eine Erwähnung, die keiner Einheit des Graphen entspricht, wird auf einfache Wörter ohne Klammern reduziert.

**Kosten und Zeiten.** Das Modell wird **einmal je Kapitel** aufgerufen. Bei einem Online-Provider hat jeder Aufruf Kosten und eine Wartezeit (in Versuchen mit einem Online-Modell einige Dutzend Sekunden je Kapitel: Eine Stätte mit etwa zehn Epochen braucht einige Minuten); mit Ollama oder LM Studio wird nichts bezahlt, aber die Zeiten hängen von Ihrem Computer ab.

### 10.5 Schritt für Schritt

1. Öffnen Sie die Matrix der Stätte (§10.1) und klicken Sie auf den Tab **Narrative**. Prüfen Sie oben, **welches Modell** er verwenden wird.
2. **Schließen Sie EMStudio**, wenn es die Datei geöffnet hat: pyArchInit und EMStudio schreiben dieselbe Datei, und wer zuletzt schreibt, gewinnt.
3. Optional: **Prepare the chapters** (Kapitel vorbereiten), um die Gliederung ohne KI zu sehen.
4. Klicken Sie auf **Generate with AI**. Verfolgen Sie den Fortschritt («Chapter 3 of 9 · …»); Sie können QGIS weiter benutzen. Am Ende sagt die Meldungsleiste zum Beispiel *«7 chapters generated, 1 failed: Modern age — …»* (7 Kapitel generiert, 1 fehlgeschlagen), mit *«(cancelled)»*, wenn Sie abgebrochen haben, und die Liste wird neu geladen: Die geschriebenen Kapitel sind «AI draft».
5. **Lesen**: Wählen Sie ein Kapitel nach dem anderen und lesen Sie den Text unter der Liste. Prüfen Sie ihn anhand der Stratigraphie: Es ist ein Entwurf, der aus den Daten des SE-Formulars aufgebaut wurde.
6. Überzeugt ein Kapitel nicht, wählen Sie seine Zeile und klicken Sie auf **Regenerate chapter**. Der neue Entwurf **ersetzt** den vorherigen, nicht validierten: Wenn Sie die frühere Fassung behalten möchten, exportieren Sie sie vorher. Ist ein Kapitel «truncated» (abgeschnitten), generieren Sie es neu, **bevor** Sie es validieren.
7. Wenn ein Kapitel stimmt, klicken Sie auf **Endorse…** (§10.6).
8. Mit **Export…** exportieren Sie die Erzählung als HTML oder DOCX (§10.7); mit **Open in EMStudio** öffnen Sie die Datei in EMStudio, um «Presentation» und «Where it is» von Hand zu schreiben und den Rest zu überarbeiten.
9. Später können Sie die Matrix erneut öffnen: Die Erzählung bleibt erhalten (§10.8).

<!-- IMMAGINE: Screenshot der laufenden Generierung: die Fortschrittszeile «Chapter 3 of 9 · …» und die Schaltfläche Cancel -->
![Generierung läuft](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Abbildung 5: Laufende Generierung, mit Fortschrittszeile und der Schaltfläche Cancel*

Ein Kapitel, das fehlschlägt, hält die anderen nicht auf: Die Zusammenfassung sagt, welches. Um es erneut zu versuchen, genügt ein weiterer Klick auf **Generate with AI**: Es werden nur die Kapitel geschrieben, die noch «to be written» sind.

### 10.6 Validieren: wer unterschreibt

Validieren heißt, dass eine **Person** die Verantwortung für den vom Modell geschriebenen Text übernimmt. Es geschieht nie von selbst: weder durch das Generieren noch durch das Speichern.

1. Klicken Sie auf **Endorse…**. Es öffnet sich ein kleines Menü: **«This chapter»** (Dieses Kapitel) — nur aktiv, wenn das gewählte Kapitel ein «AI draft» ist — oder **«All chapters»** (Alle Kapitel), das heißt alle noch nicht validierten KI-Entwürfe in jedem Graphen der Datei.
2. Ein Fenster fragt **«Who endorses? Pick an author or type a new name.»** (Wer validiert? Wählen Sie einen Autor oder geben Sie einen neuen Namen ein.) Die Liste enthält die **menschlichen Autoren, die bereits im Graphen sind** — die im SE-Formular genannten Personen als Erfasser (*schedatore*), SE-Leiter und SE-Verantwortlicher —, und Sie können einen neuen Namen eingeben, der zu einem neuen Autor des Graphen wird (bei mehreren Sondagen in jedem Graphen, der noch zu unterzeichnende Entwürfe hat).
3. Die Meldungsleiste sagt **«N blocks endorsed by `<name>`.»** (N Blöcke vom gewählten Autor validiert.) oder «Nothing to endorse.» (Nichts zu validieren.) Die Datei wird gespeichert.

<!-- IMMAGINE: Screenshot des Menüs Endorse… («This chapter» / «All chapters») und des Fensters zur Wahl des Autors -->
![Validieren](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Abbildung 6: Validieren: das Menü und die Wahl des Autors*

Die Blöcke wechseln von «AI draft» zu «endorsed». Im exportierten Dokument erscheint die Person unter den Verantwortlichen («a cura di», herausgegeben von) und das Modell als Assistent («con l'assistenza di», mit Unterstützung von), und validierte Absätze tragen das Zeichen ⚠ nicht mehr. Das erneute Generieren löscht validierte Blöcke nicht: Eine Unterschrift ist eine Handlung und geht durch Umschreiben nicht verloren.

### 10.7 Als HTML oder DOCX exportieren

Klicken Sie auf **Export…**: Das Fenster zum Speichern öffnet sich mit zwei Formaten, «HTML page (\*.html)» und «Word document (\*.docx)». Der vorgeschlagene Name ist `<Stätte>_narrativa.html`, im Ordner der em.json; wenn Sie die Endung selbst eintippen (`.html` oder `.docx`), gilt diese, andernfalls entscheidet das gewählte Format. Beim Export mit einem Graphen je Sondage wird **eine Datei je Sondage** geschrieben, wobei der gewählte Name um den Namen der Sondage ergänzt wird. Die Meldungsleiste bestätigt: «Narrative exported to `<path>`».

Das Dokument enthält:

- den Titel der Erzählung (zum Beispiel «Scavo archeologico — the story of the site»; sinngemäß: Archäologische Ausgrabung — die Geschichte der Stätte), die Verantwortlichen («a cura di») und das Modell als Assistent («con l'assistenza di»);
- für jedes Kapitel den Text, in dem die Einheiten mit ihrem Namen zitiert werden, und die Liste der Einheiten des Kapitels;
- am Ende den Abschnitt **Fonti** (Quellen): die Dokumente, auf die sich die Geschichte stützt, und den Eintrag «Prompt», der auf den in der Datei gespeicherten Prompt verweist.

Wissenswertes:

- **nicht validierte Entwürfe werden aufgenommen**, jeweils mit vorangestelltem «⚠︎ non validato da una persona» (nicht von einer Person validiert), und der Kopf des Dokuments sagt, wie viele Blöcke sich in diesem Zustand befinden. Für ein Dokument ohne Markierungen validieren Sie zuerst (§10.6);
- **alle Kapitel werden aufgenommen**, auch die noch «to be written»: Ihr Platzhalter «[to be written: …]» bleibt im Text;
- Abbildungen, die ein Autor in EMStudio vorgesehen hat (zum Beispiel die Matrix einer Epoche), werden vom Export von pyArchInit nicht gezeichnet: Im Dokument bleibt ein Platzhalter;
- das HTML ist eine einzige, in sich geschlossene Datei; das DOCX öffnet sich mit Word oder LibreOffice und erfordert das Paket `python-docx`, eine der Abhängigkeiten des Plugins.

<!-- IMMAGINE: Screenshot des exportierten HTML-Dokuments: ein Kapitel mit einem Entwurf, dem «⚠︎ non validato da una persona» vorangestellt ist -->
![Exportiertes HTML-Dokument](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Abbildung 7: Das exportierte HTML-Dokument, mit einem markierten nicht validierten Entwurf*

### 10.8 Die Stätte erneut exportieren: Die Erzählung bleibt

Wird die Stätte erneut aus der Datenbank exportiert — mit **Vedi la matrice…**, mit **Esporta sito in em.json…** oder mit dem Fenster «Esporta Extended Matrix» des SE-Formulars —, **bleibt die Erzählung erhalten**, die in der Zieldatei bereits vorhanden ist: Text, Validierungen, KI-Autor und Prompts. Epochen, die inzwischen hinzugekommen sind, erhalten ein Kapitel «to be written». Ein Hinweis meldet dies: **«Narrative kept from the previous file (N chapters).»** (Erzählung der vorherigen Datei erhalten, N Kapitel.) Sie sehen ihn bei «Vedi la matrice…» in der Meldungsleiste, in der Zusammenfassung des Fensters «Esporta Extended Matrix» und, bei «Esporta sito in em.json…», in den Details des Abschlussfensters.

**Andere Änderungen**, die in EMStudio an der Datei vorgenommen wurden — Knotenpositionen, neu geschriebene Beschreibungen —, **gehen verloren**, wie bisher: Die Datei wird aus der Datenbank neu erstellt. Erhalten bleibt nur die Erzählung.

Bevor pyArchInit eine Datei neu schreibt, die eine Erzählung enthält, legt es daneben eine **Sicherheitskopie** an: `<Stätte>.em.json.bak` (jeder neue Export ersetzt die vorherige Kopie).

Ändern Sie die Form der Datei — von «Un grafo per ogni saggio» zu «Un grafo solo per tutto il sito» oder umgekehrt —, ändern die Graphen ihre Namen, und die Erzählung **kann nicht in die neue Datei übernommen werden**. Ein Hinweis meldet dies: *«The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …»*. Der Text geht nicht verloren: Er liegt in der `.bak`-Kopie, die allerdings beim nächsten Export einer Datei mit Erzählung ersetzt wird — legen Sie sie an einem sicheren Ort ab. Um ihn wiederherzustellen, benennen Sie die Kopie in `.em.json` um und exportieren Sie erneut mit der früheren Wahl.

Kann die vorherige Datei nicht gelesen werden (zum Beispiel eine nur halb geschriebene Datei), läuft der Export trotzdem weiter: Die unlesbare Datei wird in `<Stätte>.em.json.broken` **umbenannt**, und ein Hinweis meldet *«The previous file cannot be read (…): its narrative, if any, was not kept.»*

> **Die Erzählung liegt nicht in der Datenbank von pyArchInit: Sie lebt nur in der em.json.** Ein Datenbank-Backup kopiert sie nicht. Kopieren Sie den Ordner `pyarchinit_EM_folder` von Zeit zu Zeit.

### 10.9 Über den Eintrag «Esporta sito in em.json…»

Der Eintrag **Extended Matrix → Esporta sito in em.json…** stellt dieselbe Frage zu den Sondagen und schreibt dieselbe Datei `<Stätte>.em.json` in `pyarchinit_EM_folder`. Am Ende zeigt er «Esportato `<Pfad>`» (Exportiert) mit den Zahlen der Knoten, Kanten und Hinweise (der Text der Hinweise steht in den Details des Fensters) sowie **drei Schaltflächen**:

| Schaltfläche | Was sie tut |
|--------------|-------------|
| **Apri in EMStudio** (In EMStudio öffnen) | Öffnet die Datei in EMStudio; ist EMStudio nicht installiert, wird angeboten, es zu installieren. |
| **Narrativa con l'AI** (Erzählung mit KI) | Erscheint **nur, wenn eine KI eingerichtet ist** (§10.2): Öffnet das Matrix-Panel bereits im Tab Narrative. |
| **Chiudi** (Schließen) | Schließt das Fenster. |

<!-- IMMAGINE: Screenshot des Abschlussfensters von «Esporta sito in em.json…» mit den drei Schaltflächen -->
![Esporta sito in em.json: drei Schaltflächen](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Abbildung 8: Das Abschlussfenster von «Esporta sito in em.json…»*

### 10.10 Warnungen

- **Schließen Sie EMStudio, bevor Sie generieren oder validieren.** Hat EMStudio die Datei geöffnet, gewinnt, wer zuletzt schreibt. Bei mehreren Sondagen zeigt EMStudio jeweils einen Graphen (Hinweis in §2.2.1): Der Tab Narrative zeigt sie alle.
- **Eine KI schreibt nur aus dem, was sie im Graphen findet, und sie kann sich irren.** Die Regeln zügeln sie, machen sie aber nicht unfehlbar: Lesen Sie jedes Kapitel, bevor Sie es validieren.
- **Bei einem Online-Provider verlassen die Daten Ihren Computer.** Das Briefing jedes Kapitels (Namen, Definitionen, Beschreibungen und Beziehungen der Einheiten) wird an den gewählten Dienst gesendet; mit Ollama oder LM Studio bleibt es lokal.
- **Die Datei wird am Ende geschrieben.** Die Generierung speichert, wenn sie fertig ist, auch wenn Sie sie abgebrochen haben: Schließen Sie QGIS nicht, während die KI schreibt. Das Speichern ist sicher: Die Datei wird daneben geschrieben, zurückgelesen und ersetzt erst dann die eigentliche Datei; geht etwas schief, **bleibt die vorherige Datei, wie sie war**.
- **Öffnen Sie die Matrix nicht erneut, während die KI schreibt.** Der Tab bleibt auf der vorherigen Datei und warnt: *«Generation in progress: wait for it to finish, or press Cancel, before changing file.»*
- **Der Text wird in EMStudio bearbeitet**, nicht in pyArchInit.
- Die Erzählung und die Knoten, die sie tragen (KI-Autor, Prompts), **erscheinen nicht in der Zeichnung der Matrix**.

### 10.11 Fehlerbehebung

| Meldung (en / it) | Ursache | Lösung |
|-------------------|---------|--------|
| «No AI configured…» / «Nessuna AI impostata…» | Keines der vier Fenster aus §10.2 hat ein Modell (und, bei OpenAI und Anthropic, den API-Key). | Stellen Sie Provider und Modell — und den Key — in einem dieser Fenster ein und **öffnen Sie dann die Matrix erneut**: Der Tab liest die Einstellungen nur beim Öffnen neu ein. Auch ohne KI können Sie die Kapitel vorbereiten, validieren, exportieren und EMStudio öffnen. |
| «No narrative in the file…» / «Nessuna narrativa nel file…» | Die Datei hat noch keine Erzählung (beim ersten Mal normal). | Klicken Sie auf **Prepare the chapters** (Gliederung) oder **Generate with AI** (Gliederung und Text). Die Zahl N zählt die Kapitel der Epochen und Aktivitäten, die die Gliederung haben wird (eine Epoche ohne Einheiten bekommt keines); die Meldung «Chapters prepared» zählt auch «Presentation» und gegebenenfalls «Where it is». |
| «EMStudio is not installed…» / «EMStudio non risulta installato…» | Das Programm wurde auf dem Computer nicht gefunden. | Verwenden Sie den Menüeintrag **Extended Matrix → Installa EMStudio…** (er heißt so bei jeder Sprache von QGIS). |
| «truncated» / «troncato» neben dem Zustand | Das Modell hat an der Längengrenze angehalten, und der Text endet mittendrin. | Klicken Sie vor dem Validieren auf **Regenerate chapter**; passiert es erneut, beenden Sie das Kapitel in EMStudio. |
| «N chapters generated, M failed: `<title>` — `<reason>`» / «N capitoli generati, M falliti: …» | Der Provider hat die Anfrage abgelehnt (ungültiger Key, Kontingent, Modell nicht verfügbar) oder der lokale Server antwortet nicht. «the model wrote nothing» bedeutet, dass die Antwort leer war. | Beseitigen Sie die Ursache und klicken Sie erneut auf **Generate with AI**: Es schreibt nur die Kapitel, die noch «to be written» sind. |
| «The previous file cannot be read (…)» / «Il file precedente non si legge (…)» | Beim erneuten Export war die vorhandene Datei keine lesbare em.json. | Der Export lief weiter: Die unlesbare Datei wurde neben der neuen als `….broken` aufbewahrt, und die Erzählung, die sie enthielt, wurde, falls vorhanden, nicht in die neue Datei übernommen. Brauchen Sie die Erzählung, stellen Sie sie aus dieser Datei oder aus einem Backup wieder her. |
| «The previous file's narrative (graphs: …) did not travel into the new file…» / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | Sie haben die Form der Datei geändert (ein Graph je Sondage ↔ ein einziger Graph): Die Graphen haben andere Namen, und die Erzählung kann nicht übernommen werden. | Die frühere Datei liegt in der `.bak`-Kopie: Benennen Sie sie in `.em.json` um und exportieren Sie erneut mit der früheren Wahl. |
| «Could not write … The previous file is intact.» / «Non sono riuscito a scrivere … Il file precedente è intatto.» | Das Speichern ist fehlgeschlagen (Datenträger voll, gesperrte Datei, Berechtigungen). | Beheben Sie das Problem und wiederholen Sie den Vorgang: Die in dieser Sitzung generierten Kapitel waren nicht gespeichert worden. |
| «DocX export needs python-docx — install the extra: …» (immer auf Englisch) | Das Paket `python-docx` ist im Python von QGIS nicht installiert: Es wird nur für DOCX gebraucht. | Installieren Sie `python-docx` (es gehört zu den Abhängigkeiten des Plugins) oder exportieren Sie als HTML, das nichts braucht. |

---

## Referenzen

- Upstream-Issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit-Repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
