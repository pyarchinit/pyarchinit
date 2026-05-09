# modules/db/structures_metadata/DETSESSO_table.py

## Overview

This file contains 3 documented elements.

## Classes

### DETSESSO_table

*No description available.*
A SQLAlchemy table definition class representing sex determination records for skeletal remains in an archaeological context. It defines the `detsesso_table` schema via the `define_table` classmethod, which declares columns for a unique record identifier, site name, individual number, cranial morphological trait importance degrees and values (glabella, mastoid process, nuchal plane, zygomatic structures, supraorbital features, occipital protuberance, frontal inclination), mandibular trait importance degrees and values (palate, mandibular morphology, mental protuberance, mandibular angle, inferior margin, mandibular branch, condyle), cranial sex scores, and pelvic sex indicators (superior pubis, ischium, composite arch, iliac branch, and iliac proportions). A `UniqueConstraint` named `ID_det_sesso_unico` enforces uniqueness on the combination of `sito` and `num_individuo`.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'detsesso_table'` bound to the provided `metadata`, representing sex determination data for skeletal remains. The table includes a primary key column `id_det_sesso`, site and individual identifiers, integer columns for importance degrees and values of ten cranial morphological features (glabella, mastoid process, nuchal plane, zygomatic process, supraorbital arch, tuberosity, occipital protuberance, frontal inclination, zygomatic bone, and supraorbital margin), seven mandibular feature columns, cranial sex score and indicator fields, and a series of pelvic sex determination indicators. A `UniqueConstraint` named `'ID_det_sesso_unico'` enforces uniqueness on the combination of `sito` and `num_individuo`.

