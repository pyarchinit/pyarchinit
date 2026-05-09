# modules/db/structures_metadata/Pyarchinit_thesaurus_sigle.py

## Overview

This file contains 3 documented elements.

## Classes

### Pyarchinit_thesaurus_sigle

*No description available.*
Defines the SQLAlchemy table structure for `pyarchinit_thesaurus_sigle`, a thesaurus of archaeological abbreviations and codes used within the pyarchinit system. Each entry stores a short abbreviation (`sigla`, max 3 characters) alongside its extended form, description, typology, associated database table name, and language. The primary key `id_thesaurus_sigle` is also enforced by a named unique constraint (`id_thesaurus_sigle_pk`).

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'pyarchinit_thesaurus_sigle'` bound to the provided `metadata`, representing a thesaurus of archaeological abbreviations and codes. The table includes columns for a primary key (`id_thesaurus_sigle`), the associated database table name (`nome_tabella`), a short abbreviation of up to three characters (`sigla`), its extended form (`sigla_estesa`), a description, a typology category, and a language field. A `UniqueConstraint` named `'id_thesaurus_sigle_pk'` is applied to the `id_thesaurus_sigle` column.

