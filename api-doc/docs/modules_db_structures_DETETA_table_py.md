# modules/db/structures/DETETA_table.py

## Overview

This file contains 2 documented elements.

## Classes

### DETETA_table

*No description available.*
Defines the SQLAlchemy table schema for `deteta_table`, which stores age estimation data for individual skeletal remains within archaeological sites. The table captures a wide range of osteological age indicators per individual, including symphysis pubis scores (`sinf`, `SSPIA`–`SSPID`), auricular surface ranges (`sup_aur`), dental wear (`usura`, `ms_sup`, `ms_inf`), endocranial suture closure values for numbered cranial sutures (`Id_endo` through `Xs_endo`), vault and lateral suture scores (`volta_1`–`volta_7`, `lat_6`–`lat_10`), and derived minimum/maximum age range columns. A composite unique constraint on `sito` and `nr_individuo` enforces that each individual per site has only one age estimation record.

