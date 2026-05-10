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

## Referenzen

- Upstream-Issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit-Repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
