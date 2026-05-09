# modules/db/structures/DETSESSO_table.py

## Overview

This file contains 2 documented elements.

## Classes

### DETSESSO_table

*No description available.*
Defines the SQLAlchemy table schema for `detsesso_table`, which stores sex determination data for individual skeletal remains within archaeological sites. The table captures cranial and mandibular morphological trait scores (both degree of impression and raw values) alongside pelvic sex indicators, aggregated sex indices, and a final sex determination per individual. A composite unique constraint on `sito` and `num_individuo` enforces that each individual per site has only one sex determination record.

