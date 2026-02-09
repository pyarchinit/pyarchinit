#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a test TMA record
"""

import sqlite3

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert a test TMA record
cursor.execute("""
    INSERT INTO tma_materiali_archeologici 
    (sito, area, localita, settore, ogtm, ldct, ldcn, cassetta, dscu, dtzg)
    VALUES 
    ('Test Site', 'Area 1', 'Località Test', 'Settore A', 'Test Material', 
     'Magazzino', 'LDCN001', 'C001', 'US001', 'I secolo d.C.')
""")

tma_id = cursor.lastrowid
print(f"Created TMA record with ID: {tma_id}")

# Insert test materials
cursor.execute("""
    INSERT INTO tma_materiali_ripetibili 
    (id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso)
    VALUES 
    (?, 'Ceramica', 'Ceramica comune', 'Classe A', 'Tipo 1', 'Olla', 
     'I secolo d.C.', '5', 2.5)
""", (tma_id,))

conn.commit()
conn.close()

print("Test data created successfully!")