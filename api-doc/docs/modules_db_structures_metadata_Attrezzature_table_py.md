# modules/db/structures_metadata/Attrezzature_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Attrezzature_table

*No description available.*
A SQLAlchemy table definition class representing an archaeological site equipment inventory. It exposes a single class method, `define_table`, which constructs and returns a `Table` object named `'attrezzature_table'` containing columns for equipment identification (`id_attrezzatura`, `codice_inventario`, `entity_uuid`), descriptive attributes (`nome`, `categoria`, `marca`, `modello`, `numero_serie`), ownership and financial data (`proprieta`, `costo_acquisto`, `costo_noleggio_giorno`), maintenance scheduling (`data_ultima_manutenzione`, `data_prossima_manutenzione`), and operational state (`stato`, `assegnato_a`). A `UniqueConstraint` named `'ID_attrezzatura_unico'` enforces uniqueness on the combination of `sito` and `codice_inventario`.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'attrezzature_table'` bound to the provided `metadata`, representing an archaeological site equipment inventory. The table includes columns for equipment identification (`id_attrezzatura` as primary key, `entity_uuid`), descriptive attributes (`sito`, `codice_inventario`, `nome`, `categoria`, `marca`, `modello`, `numero_serie`), ownership and cost information (`proprieta`, `costo_acquisto`, `costo_noleggio_giorno`), lifecycle tracking (`stato`, `assegnato_a`, `data_acquisto`, `data_ultima_manutenzione`, `data_prossima_manutenzione`), and a `note` field. A `UniqueConstraint` named `'ID_attrezzatura_unico'` enforces uniqueness on the combination of `sito` and `codice_inventario`.

