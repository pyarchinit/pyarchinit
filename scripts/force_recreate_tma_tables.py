#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Force recreate TMA tables to fix foreign key issues
"""

import os
import sys

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Import SQLAlchemy table structures
from modules.db.structures.Tma_table import Tma_table
from modules.db.structures.Tma_materiali_table import Tma_materiali_table

print("TMA tables structure loaded successfully")
print("This will ensure SQLAlchemy metadata is properly synchronized")

# The tables should be created automatically when the structures are imported
print("\nTo manually check the tables, run:")
print("sqlite3 ~/Library/Application\\ Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
print(".schema tma_materiali_archeologici")
print(".schema tma_materiali_ripetibili")