# Tutorial 36: Extended Matrix Export und s3dgraphy Bridge

## Einleitung

Ab Version **5.2.0-alpha** integriert PyArchInit eine **bidirektionale Bridge** mit der Bibliothek **s3dgraphy** (Extended-Matrix-Datenmodell von Emanuel Demetrescu). Die Bridge erlaubt:

- **Export** des stratigraphischen Diagramms als Extended Matrix in GraphML (mit zeitlichen Swimlanes, transitiver Reduktion, EM-1.5-Edge-Styling)
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

Der Dialog zeigt:

- **Output formats**: DOT / GraphML / JSON / phased JSON anhaken (empfohlen: GraphML)
- **Group US by (optional)**: 7 Checkboxen für Gruppendimensionen + 1 "ad-hoc"-Checkbox
  - Im DB befüllte Dimensionen werden beim Öffnen **automatisch angehakt**
- **Primärdimension-Kombinationsfeld** (Default `struttura`): Hat eine SE Mitgliedschaften in 2+ Dimensionen, gewinnt die primäre Dimension als sichtbarer yEd-Folder (hierarchischer Parent). Sekundärdimensionen erscheinen als Inline-Badges unter dem SE-Knoten. `toponym` ist nie primär, unabhängig von der Auswahl.
- **"Select Output Directory"**: Zielordner

Ab 5.6.0-alpha kannst du **2+ Dimensionen** ankreuzen: der Export funktioniert dank des m:n-Modells mit `is_primary` nativ (siehe Abschnitt "Mehrdimensionale Mitgliedschaft").

### 2.3 Klick auf "Export"

4 Dateien werden mit Präfix `Extended_Matrix_<site>[_<area>]` erzeugt:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix für yEd (Hauptziel)
- `_s3dgraphy.json` — natives s3dgraphy-Format
- `_phased.json` — Ansicht pro Epoche

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

Die Primärdimension wird über die Combobox in §2.2 gesteuert.

---

## 5. Round-trip (Import-Tab)

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

---

## Referenzen

- Upstream-Issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit-Repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
