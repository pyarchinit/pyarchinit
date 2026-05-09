# modules/db/structures_metadata/DETETA_table.py

## Overview

This file contains 3 documented elements.

## Classes

### DETETA_table

*No description available.*
A SQLAlchemy table definition class representing age determination data for skeletal remains in an archaeological context. It exposes a single class method, `define_table(cls, metadata)`, which constructs and returns a `Table` object named `'deteta_table'` bound to the provided metadata, comprising columns for recording osteological age indicators such as symphysis pubis ranges, auricular surface values, maxillary suture measurements, dental wear, endocranial suture scores, and vault/lateral suture data. A `UniqueConstraint` named `'ID_det_eta_unico'` enforces the uniqueness of each combination of archaeological site (`sito`) and individual number (`nr_individuo`).

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'deteta_table'` using the provided `metadata`, representing age determination data for skeletal remains. The table includes an integer primary key (`id_det_eta`), a site name (`sito`), an individual number (`nr_individuo`), and numerous integer columns capturing osteological age indicators such as symphysis pubis ranges, auricular surface ranges, maxillary suture ranges, dental wear, endocranial suture scores, and vault/lateral suture scores. A `UniqueConstraint` named `'ID_det_eta_unico'` enforces uniqueness on the combination of `sito` and `nr_individuo`.

