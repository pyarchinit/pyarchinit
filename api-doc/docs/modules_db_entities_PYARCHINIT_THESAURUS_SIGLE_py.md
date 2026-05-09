# modules/db/entities/PYARCHINIT_THESAURUS_SIGLE.py

## Overview

This file contains 4 documented elements.

## Classes

### PYARCHINIT_THESAURUS_SIGLE

*No description available.*
A data model class representing a thesaurus entry with abbreviation (sigla) definitions used within the pyArchInit archaeological information system. Each instance encapsulates a controlled vocabulary term identified by a unique `id_thesaurus_sigle`, associated with a target table (`nome_tabella`), a short abbreviation (`sigla`), its extended form (`sigla_estesa`), a description, typology, and language. The class also supports hierarchical organisation of terms through the `id_parent`, `parent_sigla`, `hierarchy_level`, and `order_layer` fields, with optional numeric typology and abbreviation identifiers (`n_tipologia`, `n_sigla`).

**Inherits from**: object

#### Methods

##### __init__(self, id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level, n_tipologia, n_sigla)

Initializes a new instance of the `PYARCHINIT_THESAURUS_SIGLE` class, representing a thesaurus entry with abbreviation and classification data. Assigns the required parameters `id_thesaurus_sigle`, `nome_tabella`, `sigla`, `sigla_estesa`, `descrizione`, `tipologia_sigla`, and `lingua` to their corresponding instance attributes, along with the optional parameters `order_layer`, `id_parent`, `parent_sigla`, `hierarchy_level`, `n_tipologia`, and `n_sigla`, which default to `0`, `None`, `None`, `0`, `None`, and `None` respectively.

##### __repr__(self)

Returns the official string representation of a `PYARCHINIT_THESAURUS_SIGLE` instance, formatted as a structured string containing all thirteen fields of the object: `id_thesaurus_sigle`, `nome_tabella`, `sigla`, `sigla_estesa`, `descrizione`, `tipologia_sigla`, `lingua`, `order_layer`, `id_parent`, `parent_sigla`, `hierarchy_level`, `n_tipologia`, and `n_sigla`. Fields that may be `None` — specifically `descrizione`, `id_parent`, `parent_sigla`, `n_tipologia`, and `n_sigla` — are substituted with an empty string or the literal `'None'` as appropriate.

