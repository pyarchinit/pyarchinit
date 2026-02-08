# PyArchInit - StratiGraph: UUID Identifiers

## Index
1. [Introduction](#introduction)
2. [What are UUIDs](#what-are-uuids)
3. [Why UUIDs are needed in StratiGraph](#why-uuids-are-needed-in-stratigraph)
4. [How they work in PyArchInit](#how-they-work-in-pyarchinit)
5. [Tables with UUID](#tables-with-uuid)
6. [Frequently Asked Questions](#frequently-asked-questions)

---

## Introduction

Starting from version **5.0.1-alpha**, PyArchInit integrates a system of **Universal Unique Identifiers (UUID)** for all archaeological entities. This functionality is part of the European **StratiGraph** project (Horizon Europe) and ensures that each record in the database has a stable and globally unique identifier.

<!-- VIDEO: Introduction to UUIDs in StratiGraph -->
> **Video Tutorial**: [Insert video link UUID introduction]

---

## What are UUIDs

A **UUID** (Universally Unique Identifier) is a 128-bit alphanumeric code that uniquely identifies an entity. PyArchInit uses version 4 (UUID v4), which is randomly generated.

### UUID Example

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### UUID Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Format** | 32 hexadecimal characters separated by hyphens (8-4-4-4-12) |
| **Uniqueness** | The probability of collision is statistically negligible (~1 in 2^122) |
| **Independence** | Does not depend on the database, server, or creation time |
| **Persistence** | Once assigned, it never changes |
| **Version** | UUID v4 (randomly generated) |

### Difference with traditional IDs

| ID Type | Example | Stable across DBs? | Globally unique? |
|---------|---------|-----------------|---------------------|
| Auto-increment (id_us) | `1`, `2`, `3`... | No | No |
| Composite constraint | `Site1-Area1-US100` | Yes (semantic) | Depends |
| **UUID** | `a3f7b2c1-8d4e-...` | **Yes** | **Yes** |

Auto-incremental IDs (`id_us`, `id_invmat`, etc.) change when you copy a database or import data. UUIDs instead remain **always the same**, regardless of where the data is located.

---

## Why UUIDs are needed in StratiGraph

The StratiGraph project requires that archaeological data can be:

### 1. Exported to the Knowledge Graph

PyArchInit data is exported as **bundles** (structured packages) to a central Knowledge Graph. Each entity must have a stable identifier to be recognized in the graph.

```
Local entity (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     SU 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Synchronized between devices

When working in the field without internet connection, data is saved locally. Upon return of connectivity, data is synchronized. UUIDs ensure that the same record is recognized and updated (not duplicated).

### 3. Mapped to CIDOC-CRM

The CIDOC-CRM ontology requires **persistent URIs** for each entity. UUIDs are used to construct these URIs:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Tracked over time

Every modification, export, or synchronization refers to the same UUID. This allows to:
- Reconstruct the history of a record
- Verify the provenance of data
- Link data between different projects

---

## How they work in PyArchInit

### Automatic generation

UUIDs are generated **automatically** at two moments:

| Moment | Description |
|---------|-------------|
| **New record creation** | When inserting a new record (e.g., new SU), a UUID v4 is automatically generated |
| **Existing database migration** | At first startup after the update, all existing records without UUID receive a generated UUID |

The user **does not need to do anything**: UUIDs are entirely managed by the system.

### Where the UUID is located

Each main database table has an `entity_uuid` column of TEXT type. The field is visible in the database but does not appear in the data entry forms, as it is managed internally.

### Automatic migration

When updating PyArchInit to version 5.0.1-alpha (or later):

1. **At first startup**, the system checks if the tables have the `entity_uuid` column
2. If missing, the column is **automatically added**
3. Existing records without UUID receive a **generated UUID**
4. This operation occurs **only once** per QGIS session

The process is transparent and does not require manual intervention. It works with both **PostgreSQL** and **SQLite**.

---

## Tables with UUID

The `entity_uuid` column is present in the following 19 tables:

| Table | Content |
|---------|-----------|
| `site_table` | Archaeological sites |
| `us_table` | Stratigraphic Units (SU/WSU) |
| `inventario_materiali_table` | Finds inventory |
| `tomba_table` | Burials |
| `periodizzazione_table` | Periodization and phases |
| `struttura_table` | Structures |
| `campioni_table` | Samples |
| `individui_table` | Anthropological individuals |
| `pottery_table` | Pottery |
| `media_table` | Media files |
| `media_thumb_table` | Media thumbnails |
| `media_to_entity_table` | Media-entity relationships |
| `fauna_table` | Archaeozoological data (Fauna) |
| `ut_table` | Topographic Units |
| `tma_materiali_archeologici` | TMA Archaeological Materials |
| `tma_materiali_ripetibili` | TMA Repeatable Materials |
| `archeozoology_table` | Archaeozoology |
| `documentazione_table` | Documentation |
| `inventario_lapidei_table` | Stone Inventory |

---

## Frequently Asked Questions

### Do I need to manually insert UUIDs?

**No.** UUIDs are automatically generated by the system. It is not necessary (nor recommended) to modify them manually.

### What happens if I copy the database?

UUIDs are copied along with the database. This is the desired behavior: the same record maintains the same UUID even on different copies of the database.

### Can I see UUIDs in the forms?

Currently, UUIDs are not visible in the data entry forms. They are visible directly in the database (e.g., via DB Manager in QGIS) in the `entity_uuid` column of each table.

### Do UUIDs slow down the database?

No. The UUID is a simple TEXT field and does not have a significant impact on database performance.

### What happens to existing databases?

Existing databases are automatically updated at first startup: the `entity_uuid` column is added and all existing records receive a generated UUID.

### Do UUIDs work with both PostgreSQL and SQLite?

Yes. The system is compatible with both database types supported by PyArchInit.

---

*PyArchInit Documentation - StratiGraph UUID*
*Version: 5.0.1-alpha*
*Last update: February 2026*
