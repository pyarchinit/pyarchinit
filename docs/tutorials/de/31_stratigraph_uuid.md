# PyArchInit - StratiGraph: UUID-Identifikatoren

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Was sind UUIDs](#was-sind-uuids)
3. [Warum UUIDs in StratiGraph benötigt werden](#warum-uuids-in-stratigraph-benötigt-werden)
4. [Wie sie in PyArchInit funktionieren](#wie-sie-in-pyarchinit-funktionieren)
5. [Tabellen mit UUID](#tabellen-mit-uuid)
6. [Häufig gestellte Fragen](#häufig-gestellte-fragen)

---

## Einführung

Ab Version **5.0.1-alpha** integriert PyArchInit ein System von **universellen eindeutigen Identifikatoren (UUID)** für alle archäologischen Entitäten. Diese Funktionalität ist Teil des europäischen Projekts **StratiGraph** (Horizon Europe) und stellt sicher, dass jeder Datensatz in der Datenbank eine stabile und global eindeutige Kennung hat.

<!-- VIDEO: Einführung in UUIDs in StratiGraph -->
> **Video-Tutorial**: [Video-Link UUID-Einführung einfügen]

---

## Was sind UUIDs

Eine **UUID** (Universally Unique Identifier) ist ein 128-Bit alphanumerischer Code, der eine Entität eindeutig identifiziert. PyArchInit verwendet Version 4 (UUID v4), die zufällig generiert wird.

### UUID-Beispiel

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### UUID-Eigenschaften

| Eigenschaft | Beschreibung |
|---------------|-------------|
| **Format** | 32 hexadezimale Zeichen, getrennt durch Bindestriche (8-4-4-4-12) |
| **Eindeutigkeit** | Die Wahrscheinlichkeit einer Kollision ist statistisch vernachlässigbar (~1 zu 2^122) |
| **Unabhängigkeit** | Hängt nicht von der Datenbank, dem Server oder dem Erstellungszeitpunkt ab |
| **Persistenz** | Einmal zugewiesen, ändert sie sich nie |
| **Version** | UUID v4 (zufällig generiert) |

### Unterschied zu traditionellen IDs

| ID-Typ | Beispiel | Stabil über DBs? | Global eindeutig? |
|---------|---------|-----------------|---------------------|
| Auto-Inkrement (id_us) | `1`, `2`, `3`... | Nein | Nein |
| Zusammengesetzte Einschränkung | `Fundstelle1-Bereich1-SE100` | Ja (semantisch) | Abhängig |
| **UUID** | `a3f7b2c1-8d4e-...` | **Ja** | **Ja** |

Auto-inkrementelle IDs (`id_us`, `id_invmat`, etc.) ändern sich beim Kopieren einer Datenbank oder beim Importieren von Daten. UUIDs bleiben dagegen **immer gleich**, unabhängig davon, wo sich die Daten befinden.

---

## Warum UUIDs in StratiGraph benötigt werden

Das StratiGraph-Projekt erfordert, dass archäologische Daten:

### 1. In den Knowledge Graph exportiert werden können

PyArchInit-Daten werden als **Bundles** (strukturierte Pakete) in einen zentralen Knowledge Graph exportiert. Jede Entität muss eine stabile Kennung haben, um im Graph erkannt zu werden.

```
Lokale Entität (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     SE 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Zwischen Geräten synchronisiert werden können

Bei der Arbeit im Feld ohne Internetverbindung werden Daten lokal gespeichert. Bei Wiederherstellung der Verbindung werden die Daten synchronisiert. UUIDs stellen sicher, dass derselbe Datensatz erkannt und aktualisiert (nicht dupliziert) wird.

### 3. Auf CIDOC-CRM abgebildet werden können

Die CIDOC-CRM-Ontologie erfordert **persistente URIs** für jede Entität. UUIDs werden verwendet, um diese URIs zu konstruieren:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Im Zeitverlauf nachverfolgt werden können

Jede Änderung, jeder Export oder jede Synchronisierung bezieht sich auf dieselbe UUID. Dies ermöglicht:
- Die Geschichte eines Datensatzes zu rekonstruieren
- Die Herkunft der Daten zu überprüfen
- Daten zwischen verschiedenen Projekten zu verknüpfen

---

## Wie sie in PyArchInit funktionieren

### Automatische Generierung

UUIDs werden **automatisch** zu zwei Zeitpunkten generiert:

| Zeitpunkt | Beschreibung |
|---------|-------------|
| **Erstellung neuer Datensätze** | Beim Einfügen eines neuen Datensatzes (z.B. neue SE) wird automatisch eine UUID v4 generiert |
| **Migration bestehender Datenbanken** | Beim ersten Start nach dem Update erhalten alle bestehenden Datensätze ohne UUID eine generierte UUID |

Der Benutzer **muss nichts tun**: UUIDs werden vollständig vom System verwaltet.

### Wo sich die UUID befindet

Jede Haupttabelle der Datenbank hat eine Spalte `entity_uuid` vom Typ TEXT. Das Feld ist in der Datenbank sichtbar, erscheint aber nicht in den Eingabeformularen, da es intern verwaltet wird.

### Automatische Migration

Beim Aktualisieren von PyArchInit auf Version 5.0.1-alpha (oder später):

1. **Beim ersten Start** prüft das System, ob die Tabellen die Spalte `entity_uuid` haben
2. Falls fehlend, wird die Spalte **automatisch hinzugefügt**
3. Bestehende Datensätze ohne UUID erhalten eine **generierte UUID**
4. Dieser Vorgang erfolgt **nur einmal** pro QGIS-Sitzung

Der Prozess ist transparent und erfordert keinen manuellen Eingriff. Er funktioniert sowohl mit **PostgreSQL** als auch mit **SQLite**.

---

## Tabellen mit UUID

Die Spalte `entity_uuid` ist in den folgenden 19 Tabellen vorhanden:

| Tabelle | Inhalt |
|---------|-----------|
| `site_table` | Archäologische Fundstellen |
| `us_table` | Stratigraphische Einheiten (SE/WSE) |
| `inventario_materiali_table` | Fundinventar |
| `tomba_table` | Gräber |
| `periodizzazione_table` | Periodisierung und Phasen |
| `struttura_table` | Strukturen |
| `campioni_table` | Proben |
| `individui_table` | Anthropologische Individuen |
| `pottery_table` | Keramik |
| `media_table` | Mediendateien |
| `media_thumb_table` | Medien-Miniaturansichten |
| `media_to_entity_table` | Medien-Entitäts-Beziehungen |
| `fauna_table` | Archäozoologische Daten (Fauna) |
| `ut_table` | Topographische Einheiten |
| `tma_materiali_archeologici` | TMA Archäologische Materialien |
| `tma_materiali_ripetibili` | TMA Wiederholbare Materialien |
| `archeozoology_table` | Archäozoologie |
| `documentazione_table` | Dokumentation |
| `inventario_lapidei_table` | Steininventar |

---

## Häufig gestellte Fragen

### Muss ich UUIDs manuell eingeben?

**Nein.** UUIDs werden automatisch vom System generiert. Es ist nicht notwendig (und auch nicht empfohlen), sie manuell zu ändern.

### Was passiert, wenn ich die Datenbank kopiere?

UUIDs werden zusammen mit der Datenbank kopiert. Dies ist das gewünschte Verhalten: Derselbe Datensatz behält dieselbe UUID auch bei verschiedenen Kopien der Datenbank.

### Kann ich UUIDs in den Formularen sehen?

Derzeit sind UUIDs in den Eingabeformularen nicht sichtbar. Sie sind direkt in der Datenbank sichtbar (z.B. über den DB-Manager in QGIS) in der Spalte `entity_uuid` jeder Tabelle.

### Verlangsamen UUIDs die Datenbank?

Nein. Die UUID ist ein einfaches TEXT-Feld und hat keinen signifikanten Einfluss auf die Datenbankleistung.

### Was passiert mit bestehenden Datenbanken?

Bestehende Datenbanken werden beim ersten Start automatisch aktualisiert: Die Spalte `entity_uuid` wird hinzugefügt und alle bestehenden Datensätze erhalten eine generierte UUID.

### Funktionieren UUIDs sowohl mit PostgreSQL als auch mit SQLite?

Ja. Das System ist mit beiden von PyArchInit unterstützten Datenbanktypen kompatibel.

---

*PyArchInit-Dokumentation - StratiGraph UUID*
*Version: 5.0.1-alpha*
*Letzte Aktualisierung: Februar 2026*
