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

### 6.2 Idempotenz

Der Vorgang ist **idempotent**: Ein erneuter Lauf dupliziert vorhandene Datensätze nicht — er aktualisiert die bestehenden `CON_<us>`, wenn sich die Daten der Mutter-Einheit geändert haben.

### 6.3 Dry-Run-Vorschau und Backup

Vor dem Schreiben wird eine **Dry-Run-Vorschau** mit den Zählungen angezeigt: wie viele Datensätze zu **erstellen**, zu **aktualisieren**, **unverändert** sind und wie viele **verwaist** sind. Änderungen werden **erst nach Bestätigung** angewendet (Schaltfläche „Genera"). Beim Anwenden wird zuvor automatisch ein **Datenbank-Backup** erstellt.

Ein CON-Datensatz ist **verwaist**, wenn seine Mutter-Einheit sich nicht mehr über mehrere Perioden erstreckt (z. B. wurden Anfangs- und Endperiode gleichgesetzt). Standardmäßig werden Verwaiste nur **markiert**; eine **Checkbox** („Rimuovi anche le CON orfane") erlaubt es, sie zu entfernen.

### 6.4 Im Extended-Matrix-Export

Die so erzeugten `CON_<us>`-Datensätze erscheinen im Extended-Matrix-GraphML-Export als **Kontinuitäts-Elemente**.

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

@@OLDFIG@@
Der Baum im Bereich gruppiert die Probleme nach Art. Neben den Beziehungsgruppen erscheinen vier neue Gruppen:

| Gruppe | Was gemeldet wird | Behandlung |
|--------|-------------------|------------|
| **Phasen mit überlappenden Intervallen** | Zwei Zeilen der Periodisierung, deren Jahresintervalle sich schneiden | Manuell: Der Bereich schlägt eine Einengung nur vor, wenn nach der Einengung ein nutzbares Intervall übrig bleibt |
| **Abweichende Datierung des Formulars** | Das Feld `datazione` des SE-Formulars sagt etwas anderes als die `datazione_estesa` der zugehörigen Periode/Phase | Automatisch: Die Periodisierung ist die Quelle, das Formular die Kopie; die Kopie wird also aus der Quelle neu geschrieben. Ein leeres Feld wird auf dieselbe Weise gefüllt. Eine SE ohne Periode wird übersprungen, weil es nichts zu kopieren gibt |
| **Periodisierung mit Beginn nach dem Ende** | `cron_iniziale` größer als `cron_finale` | Automatisch: Die beiden Jahre werden vertauscht |
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

## Referenzen

- Upstream-Issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit-Repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
