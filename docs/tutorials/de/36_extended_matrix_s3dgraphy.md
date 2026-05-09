# Tutorial 36: Extended Matrix Export und s3dgraphy Bridge

## Einleitung

Ab Version **5.2.0-alpha** integriert PyArchInit eine **bidirektionale Bridge** mit der Bibliothek **s3dgraphy** (Extended-Matrix-Datenmodell von Emanuel Demetrescu). Die Bridge erlaubt:

- **Export** des stratigraphischen Diagramms als Extended Matrix in GraphML (mit zeitlichen Swimlanes, transitiver Reduktion, EM-1.5-Edge-Styling)
- **Re-Import** von in yEd vorgenommenen Änderungen (SE-Bewegungen zwischen Perioden/Gruppen) zur Aktualisierung der SQL-Datenbank
- **Anhängen von Paradata** (Author / License / Embargo) auf Stättenebene
- **Gruppieren** von SE nach Dimension (struttura, area, attivita, settore, ambient, saggio, quad_par oder Ad-hoc-Gruppen)

Aktueller Tag: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

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
- **"Select Output Directory"**: Zielordner

### 2.3 Single-dimension-Limit (5.5.2-alpha)

Wenn du **2 oder mehr** Gruppen-Checkboxen ankreuzst, erscheint eine Warnung:

> *"Multi-dim Export noch nicht unterstützt. Mit NUR der ersten ausgewählten Dimension fortfahren?"*

Wähle **Ja** (Export mit erster angekreuzter Dimension) oder **Abbrechen** (Auswahl ändern). Hierarchisches Nesting (struttura > attivita > SE) kommt mit AI08-F1.

### 2.4 Klick auf "Export"

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

## 4. Visueller Stil pro Dimension (5.5.1-alpha)

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

Die 50%-Alpha lässt die Epochen-Swimlanes hinter dem Gruppenrechteck sichtbar.

---

## 5. Round-trip (Import-Tab)

Um die SQL-Datenbank durch das Verschieben von SE zwischen Gruppen im GraphML zu aktualisieren:

1. GraphML in **yEd** öffnen
2. Eine SE in eine andere Gruppe ziehen, speichern
3. Zurück zum Dialog → Tab **"Import"**
4. **Anhaken** der Checkbox *"Update SQL on import (struttura/area/...)"*
5. Modifizierte GraphML laden

Das System läuft als atomare Transaktion: Bei Fehlern **vollständiges Rollback** (DB bleibt unverändert). `adhoc`-Gruppen schreiben nie SQL — sie aktualisieren nur `groups_<site>.graphml`.

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
| Leerer Gruppenordner in yEd | 2+ Dimensionen angekreuzt (5.5.2-alpha-Limit) | Nur eine Dimension wählen |
| "rapporti müssen TEXT sein" | Zahl als Integer eingegeben | SE/Area-Felder sind **TEXT**, nicht Integer |
| Falsche Großschreibung in rapporti | Kleines "copre" in DB | "Copre", "Coperto da" groß schreiben |

---

## 8. Technische Dokumentation

Für Architektur, Designentscheidungen und Roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Aufgeschobene Carry-Overs:
- **AI07**: `LocationNodeGroup`-Migration (Upstream-Deadline 2026-05-23)
- **AI08-F1**: Hierarchisches Nesting (sauberer Multi-dim-Export)
- **AI08-F3**: Auto-Layout-Heuristiken (Sub-Group-Bin-Packing)
- **AI09**: TimeBranchNodeGroup-Mapping
- **Phase 3**: SyncEngine + REST API
- **Phase 4**: GraphDBBackend + SPARQL

---

## Referenzen

- Upstream-Issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit-Repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
