#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori scan (Denominazione scavo) dall'Excel
"""

import sqlite3
import os
import sys

def insert_scan_values(cursor):
    """Inserisce i valori scan dal file Excel."""
    
    # Prima rimuovi i valori scan esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.5'
    """)
    print("✓ Rimossi valori scan (10.5) esistenti")
    
    # Valori esatti dall'Excel
    scan_values = [
        (1, 'Festòs Scavi 1939'),
        (2, 'Festòs Scavi Levi'),
        (3, 'Festòs Scavi Levi 1950'),
        (4, 'Festòs Scavi Levi 1951'),
        (5, 'Festòs Scavi Levi 1951-1952'),
        (6, 'Festòs Scavi Levi 1952'),
        (7, 'Festòs Scavi Levi Museo Stratigrafico 1952'),
        (8, 'Festòs Scavi Levi 1953'),
        (9, 'Festòs Scavi Levi 1954'),
        (10, 'Festòs Scavi Levi 1954, 1959'),
        (11, 'Festòs Scavi Levi 1955'),
        (12, 'Festòs Scavi Levi Museo Stratigrafico 1955'),
        (13, 'Festòs Scavi Levi 1956'),
        (14, 'Festòs Scavi Levi 1956-1957'),
        (15, 'Festòs Scavi Levi 1957'),
        (16, 'Festòs Scavi Levi 1958'),
        (17, 'Festòs Scavi Levi 1958-1959'),
        (18, 'Festòs Scavi Levi 1958-1960'),
        (19, 'Festòs Scavi Levi 1958-1961'),
        (20, 'Festòs Scavi Levi 1958-1962'),
        (21, 'Festòs Scavi Levi 1958-1963'),
        (22, 'Festòs Scavi Levi 1958-1964'),
        (23, 'Festòs Scavi Levi 1958-1965'),
        (24, 'Festòs Scavi Levi 1958-1966'),
        (25, 'Festòs Scavi Levi 1958-1967'),
        (26, 'Festòs Scavi Levi 1958-1968'),
        (27, 'Festòs Scavi Levi 1958-1969'),
        (28, 'Festòs Scavi Levi 1958-1970'),
        (29, 'Festòs Scavi Levi 1958-1971'),
        (30, 'Festòs Scavi Levi 1958-1972'),
        (31, 'Festòs Scavi Levi 1958-1973'),
        (32, 'Festòs Scavi Levi 1958-1974'),
        (33, 'Festòs Scavi Levi 1959'),
        (34, 'Festòs Scavi Levi 1959-1960'),
        (35, 'Festòs Scavi Levi 1960'),
        (36, 'Festòs Scavi Levi 1960'),
        (37, 'Festòs Scavi Levi 1960-1961'),
        (38, 'Festòs Scavi Levi 1960-1964'),
        (39, 'Festòs Scavi Levi 1960-1965'),
        (40, 'Festòs Scavi Levi 1961'),
        (41, 'Festòs Scavi Levi 1962'),
        (42, 'Festòs Scavi Levi 1963'),
        (43, 'Festòs Scavi Levi 1964'),
        (44, 'Festòs Scavi Levi 1964-1965'),
        (45, 'Festòs Scavi Levi 1965'),
        (46, 'Festòs Scavi Levi 1965-1966'),
        (47, 'Festòs Scavi Levi 1966'),
        (48, 'Festòs Scavi Levi 1967'),
        (49, 'Festòs Scavi Levi 1969'),
        (50, 'Festòs Scavi Levi 1970'),
        (51, 'Festòs Scavi Levi 1971'),
        (52, 'Festòs Scavi Levi 1973'),
        (53, 'Festòs Scavi Levi 1976'),
        (54, 'Festòs Scavi Levi 1978-1979'),
        (55, 'Festòs Scavi Levi 1979'),
        (56, 'Festòs Scavi Levi 1981'),
        (57, 'Festòs Scavi La Rosa 1994'),
        (58, 'Festòs Scavi La Rosa 2000'),
        (59, 'Festòs Scavi La Rosa 2001'),
        (60, 'Festòs Scavi La Rosa 2002'),
        (61, 'Festòs Scavi La Rosa 2004'),
        (62, 'Festòs Scavi La Rosa 2004-2005'),
        (63, 'Festòs Scavi Carinci-Militello 2013'),
        (64, 'Festòs Scavi Carinci-Militello 2015'),
        (65, 'Festòs Scavi Carinci-Militello 2016'),
        (66, 'Festòs Scavi Carinci-Militello 2016-2017'),
        (67, 'Festòs Scavi Carinci-Militello 2017'),
        (68, 'Festòs Scavi Militello 2018'),
        (69, 'Festòs Scavi Militello 2022'),
        (70, 'Festòs Scavi Militello 2022-2023'),
        (71, 'Festòs Scavi Militello 2023'),
        (72, 'Festòs Scavi Militello 2025'),
        (73, 'Festòs Scavi Todaro 2022'),
        (74, 'Festòs Scavi Todaro 2023'),
        (75, 'Festòs Scavi Todaro 2025'),
        (76, 'Festòs Scavi Caloi 2022'),
        (77, 'Festòs Scavi Caloi 2023'),
        (78, 'Festòs Scavi Caloi 2025'),
        (79, 'Festòs ?'),
        (80, 'HTR Scavi Levi 1958'),
        (81, 'HTR Scavi Levi 1970'),
        (82, 'HTR Scavi Levi 1971'),
        (83, 'HTR Scavi La Rosa 1977'),
        (84, 'HTR Scavi La Rosa 1978'),
        (85, 'HTR Scavi La Rosa 1978-1979'),
        (86, 'HTR Scavi La Rosa 1979'),
        (87, 'HTR Scavi La Rosa 1980'),
        (88, 'HTR Scavi La Rosa 1980-1982'),
        (89, 'HTR Scavi La Rosa 1981'),
        (90, 'HTR Scavi La Rosa 1982'),
        (91, 'HTR Scavi La Rosa 1983'),
        (92, 'HTR Scavi La Rosa 1983-1984'),
        (93, 'HTR Scavi La Rosa 1984'),
        (94, 'HTR Scavi La Rosa 1985'),
        (95, 'HTR Scavi La Rosa 1986'),
        (96, 'HTR Scavi La Rosa 1987'),
        (97, 'HTR Scavi La Rosa 1988'),
        (98, 'HTR Scavi La Rosa 1989'),
        (99, 'HTR Scavi La Rosa 1990'),
        (100, 'HTR Scavi La Rosa 1991'),
        (101, 'HTR Scavi La Rosa 1992'),
        (102, 'HTR Scavi La Rosa 1993'),
        (103, 'HTR Scavi La Rosa 1995'),
        (104, 'HTR Scavi La Rosa 1996'),
        (105, 'HTR Scavi La Rosa 1997'),
        (106, 'HTR Scavi La Rosa 1998'),
        (107, 'HTR Scavi La Rosa 1999'),
        (108, 'HTR Scavi La Rosa 2003'),
        (109, 'HTR Scavi La Rosa 2006'),
        (110, 'HTR Scavi La Rosa 2006-2007'),
        (111, 'HTR Scavi La Rosa 2007-2008'),
        (112, 'HTR Scavi La Rosa 2008'),
        (113, 'HTR Scavi La Rosa 2009'),
        (114, 'HTR Scavi La Rosa 2010'),
        (115, 'HTR Scavi La Rosa 2011'),
        (116, 'HTR Scavi La Rosa 2012'),
        (117, 'HTR ?'),
        (118, 'Kamilari Scavi La Rosa 1973'),
        (119, 'Kamilari Scavi La Rosa 1973-1975'),
        (120, 'Kamilari Scavi La Rosa 1973-1976'),
        (121, 'Kamilari Scavi La Rosa 1975'),
        (122, 'Kamilari Scavi La Rosa 1975-1976'),
        (123, 'Kamilari Scavi La Rosa 1976'),
        (124, 'Progetto Festòs'),
        (125, 'Progetto Festòs 2008'),
        (126, 'Progetto Festòs 2009'),
        (127, 'Progetto Festòs 2010'),
        (128, 'Progetto Festòs 2011'),
        (129, 'Progetto Festòs 2012'),
        (130, 'Progetto Festòs 2013'),
        (131, 'Progetto Festòs 2014'),
        (132, 'Progetto Festòs 2015'),
        (133, 'Progetto Festòs 2016'),
        (134, 'Progetto Festòs 2017'),
        (135, 'Progetto Festòs 2018'),
        (136, 'Progetto Festòs 2022'),
        (137, 'Scavi Banti 1958'),
        (138, 'Lavori EOT 1969'),
        (139, 'Haghia Photinì 1994'),
        (140, 'Scavo canali impianto anti-incendio'),
        (141, 'Scavo uliveto'),
        (142, 'Faunistica scavi 2016-2017'),
        (143, 'Lavori strada per Festòs'),
    ]
    
    print("\nInserimento valori scan (Denominazione scavo - 10.5):")
    inserted = 0
    
    for id_val, denominazione in scan_values:
        # Usa SCAN + numero come sigla
        sigla = f"SCAN{id_val:03d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('TMA materiali archeologici', ?, ?, '10.5', 'it')
        """, (sigla, denominazione))
        
        if inserted < 20 or inserted % 20 == 0:  # Mostra solo alcuni per non inondare l'output
            print(f"  ✓ {id_val}. {denominazione}")
        inserted += 1
    
    print(f"  ... (totale {inserted} denominazioni scavo inserite)")
    
    return inserted

def main():
    # Database path
    db_path = os.path.expanduser("/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Uso database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Inserimento valori scan (Denominazione scavo) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_scan_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica per tipo
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.5' AND sigla_estesa LIKE '%Festòs%'
        """)
        festos_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.5' AND sigla_estesa LIKE '%HTR%'
        """)
        htr_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.5' AND sigla_estesa LIKE '%Kamilari%'
        """)
        kamilari_count = cursor.fetchone()[0]
        
        print(f"\nRiepilogo per sito:")
        print(f"   Scavi Festòs: {festos_count}")
        print(f"   Scavi HTR (Haghia Triada): {htr_count}")
        print(f"   Scavi Kamilari: {kamilari_count}")
        print(f"   Altri: {inserted - festos_count - htr_count - kamilari_count}")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())