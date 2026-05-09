# modules/db/structures/UT_table.py

## Overview

This file contains 2 documented elements.

## Classes

### UT_table

*No description available.*
Defines the SQLAlchemy table schema for `ut_table`, which stores data records for archaeological survey units (UT — *Unità Topografica*). The table encompasses a wide range of fields covering project identification, geographic and cadastral location, terrain description, survey methodology, chronological interpretation, and documentation, as well as extended survey attributes (added in v4.9.21+) and archaeological potential/risk analysis scores (added in v4.9.67+). A composite unique constraint (`ID_ut_unico`) is enforced on the `progetto`, `nr_ut`, and `ut_letterale` columns to prevent duplicate unit records within a project.

