#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add TMA thesaurus data for materials table
"""

import sqlite3

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Adding TMA Thesaurus Data ===")

# Add thesaurus entries for TMA materials
thesaurus_data = [
    # Categoria entries
    ('tma_materiali_ripetibili', 'C', 'Ceramica', 'Ceramica archeologica', 'categoria', 'IT', 1, None, None, 0),
    ('tma_materiali_ripetibili', 'V', 'Vetro', 'Vetro archeologico', 'categoria', 'IT', 2, None, None, 0),
    ('tma_materiali_ripetibili', 'M', 'Metallo', 'Metallo archeologico', 'categoria', 'IT', 3, None, None, 0),
    ('tma_materiali_ripetibili', 'O', 'Osso', 'Osso lavorato', 'categoria', 'IT', 4, None, None, 0),
    ('tma_materiali_ripetibili', 'P', 'Pietra', 'Pietra lavorata', 'categoria', 'IT', 5, None, None, 0),
    ('tma_materiali_ripetibili', 'L', 'Laterizio', 'Laterizio', 'categoria', 'IT', 6, None, None, 0),
    ('tma_materiali_ripetibili', 'T', 'Tessuto', 'Tessuto archeologico', 'categoria', 'IT', 7, None, None, 0),
    
    # Classe entries - Ceramica
    ('tma_materiali_ripetibili', 'CC', 'Ceramica comune', 'Ceramica comune', 'classe', 'IT', 1, 1, 'C', 1),
    ('tma_materiali_ripetibili', 'CF', 'Ceramica fine', 'Ceramica fine da mensa', 'classe', 'IT', 2, 1, 'C', 1),
    ('tma_materiali_ripetibili', 'CA', 'Anfore', 'Anfore da trasporto', 'classe', 'IT', 3, 1, 'C', 1),
    ('tma_materiali_ripetibili', 'CK', 'Ceramica da cucina', 'Ceramica da cucina', 'classe', 'IT', 4, 1, 'C', 1),
    
    # Classe entries - Vetro
    ('tma_materiali_ripetibili', 'VB', 'Vetro bottiglie', 'Bottiglie in vetro', 'classe', 'IT', 1, 2, 'V', 1),
    ('tma_materiali_ripetibili', 'VC', 'Vetro coppe', 'Coppe in vetro', 'classe', 'IT', 2, 2, 'V', 1),
    ('tma_materiali_ripetibili', 'VP', 'Vetro piatti', 'Piatti in vetro', 'classe', 'IT', 3, 2, 'V', 1),
    
    # Classe entries - Metallo
    ('tma_materiali_ripetibili', 'MF', 'Ferro', 'Oggetti in ferro', 'classe', 'IT', 1, 3, 'M', 1),
    ('tma_materiali_ripetibili', 'MB', 'Bronzo', 'Oggetti in bronzo', 'classe', 'IT', 2, 3, 'M', 1),
    ('tma_materiali_ripetibili', 'MA', 'Argento', 'Oggetti in argento', 'classe', 'IT', 3, 3, 'M', 1),
    
    # Località entries
    ('tma_materiali_ripetibili', 'ROM', 'Roma', 'Roma', 'localita', 'IT', 1, None, None, 0),
    ('tma_materiali_ripetibili', 'FIR', 'Firenze', 'Firenze', 'localita', 'IT', 2, None, None, 0),
    ('tma_materiali_ripetibili', 'NAP', 'Napoli', 'Napoli', 'localita', 'IT', 3, None, None, 0),
    
    # Sito entries
    ('tma_materiali_ripetibili', 'FOR', 'Foro Romano', 'Foro Romano', 'sito', 'IT', 1, None, None, 0),
    ('tma_materiali_ripetibili', 'COL', 'Colosseo', 'Colosseo', 'sito', 'IT', 2, None, None, 0),
    ('tma_materiali_ripetibili', 'POM', 'Pompei', 'Pompei', 'sito', 'IT', 3, None, None, 0),
    
    # Settore entries
    ('tma_materiali_ripetibili', 'A', 'Settore A', 'Settore A', 'settore', 'IT', 1, None, None, 0),
    ('tma_materiali_ripetibili', 'B', 'Settore B', 'Settore B', 'settore', 'IT', 2, None, None, 0),
    ('tma_materiali_ripetibili', 'C', 'Settore C', 'Settore C', 'settore', 'IT', 3, None, None, 0),
]

# Insert thesaurus data
for data in thesaurus_data:
    try:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        print(f"Added: {data[2]} ({data[1]}) - {data[4]}")
    except sqlite3.IntegrityError as e:
        print(f"Skipped (already exists): {data[2]} ({data[1]})")
    except Exception as e:
        print(f"Error adding {data[2]}: {e}")

conn.commit()

# Verify insertion
cursor.execute("SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle WHERE nome_tabella = 'tma_materiali_ripetibili'")
count = cursor.fetchone()[0]
print(f"\nTotal TMA thesaurus entries: {count}")

# Show sample entries by type
print("\n=== Sample Entries by Type ===")
for tipo in ['categoria', 'classe', 'localita', 'sito', 'settore']:
    cursor.execute("""
        SELECT sigla, sigla_estesa 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_ripetibili' 
        AND tipologia_sigla = ?
        LIMIT 3
    """, (tipo,))
    entries = cursor.fetchall()
    if entries:
        print(f"\n{tipo.upper()}:")
        for sigla, estesa in entries:
            print(f"  {sigla} - {estesa}")

conn.close()
print("\n=== Thesaurus Data Added Successfully ===")