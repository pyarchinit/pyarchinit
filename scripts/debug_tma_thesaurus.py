#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per debug completo del thesaurus TMA
"""

import sqlite3
import os
import sys

def debug_thesaurus(db_path):
    """Debug completo del thesaurus."""
    print(f"Debug thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verifica i campi nel codice Tma.py vs database
        print("\n" + "=" * 100)
        print("MAPPATURA CAMPI TMA.PY vs DATABASE")
        print("=" * 100)
        
        field_mapping = [
            # Campo UI -> Tipologia nel DB -> Campo nel codice
            ("ogtm (Tipo materiale)", "10.1", "self.comboBox_ogtm"),
            ("ldct (Tipo contenitore)", "10.2", "self.comboBox_ldct"),
            ("ldcn (Nome contenitore)", "10.3", "self.comboBox_ldcn"),
            ("scan (Nome scavo)", "10.4", "self.comboBox_scan"),
            ("aint (Tipo acquisizione)", "10.5", "self.comboBox_aint o lineEdit_aint?"),
            ("dtzg (Fascia cronologica)", "10.6", "self.comboBox_dtzg"),
            ("localita", "10.13", "self.comboBox_localita"),
            ("area", "10.14", "self.comboBox_area"),
            ("settore", "10.15", "self.comboBox_settore"),
            # Campi per tabwidget_materiali
            ("macc (Categoria)", "10.7", "tabwidget col 0"),
            ("macl (Classe)", "10.8", "tabwidget col 1"),
            ("macp (Precisazione)", "10.9", "tabwidget col 2"),
            ("macd (Definizione)", "10.10", "tabwidget col 3"),
            ("cronologia", "10.11", "tabwidget col 4"),
            # Documentazione
            ("ftap (Tipo foto)", "10.12", "tableWidget_foto"),
        ]
        
        for field_name, tipo_code, widget_name in field_mapping:
            cursor.execute("""
                SELECT COUNT(*), MIN(sigla), MAX(sigla) 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici' 
                AND tipologia_sigla = ?
            """, (tipo_code,))
            
            count, min_sigla, max_sigla = cursor.fetchone()
            print(f"{field_name:<30} tipo={tipo_code:<6} widget={widget_name:<30} count={count or 0:<5} range={min_sigla or 'N/A'}-{max_sigla or 'N/A'}")
        
        # 2. Verifica lingua = 'IT' per tutti
        print("\n" + "=" * 100)
        print("VERIFICA LINGUA")
        print("=" * 100)
        
        cursor.execute("""
            SELECT tipologia_sigla, COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND lingua != 'IT'
            GROUP BY tipologia_sigla
        """)
        
        wrong_lang = cursor.fetchall()
        if wrong_lang:
            print("⚠️ Record con lingua diversa da 'IT':")
            for tipo, count in wrong_lang:
                print(f"  Tipo {tipo}: {count} record")
        else:
            print("✅ Tutti i record hanno lingua = 'IT'")
        
        # 3. Verifica gerarchie
        print("\n" + "=" * 100)
        print("VERIFICA GERARCHIE LOCALITÀ->AREA->SETTORE")
        print("=" * 100)
        
        # Località con hierarchy_level = 1
        cursor.execute("""
            SELECT sigla, sigla_estesa, hierarchy_level 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.13'
            ORDER BY sigla
        """)
        
        print("\nLocalità (10.13):")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (level={row[2]})")
        
        # Aree con parent
        cursor.execute("""
            SELECT a.sigla, a.sigla_estesa, a.parent_sigla, l.sigla_estesa as localita_nome
            FROM pyarchinit_thesaurus_sigle a
            LEFT JOIN pyarchinit_thesaurus_sigle l 
                ON a.parent_sigla = l.sigla 
                AND l.tipologia_sigla = '10.13'
            WHERE a.nome_tabella = 'tma_materiali_archeologici' 
            AND a.tipologia_sigla = '10.14'
            AND a.sigla IN ('AREA001', 'AREA004', 'AREA007')
        """)
        
        print("\nAree esempio (10.14):")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} -> parent={row[2]} ({row[3]})")
        
        # 4. Verifica problemi specifici nel codice
        print("\n" + "=" * 100)
        print("PROBLEMI DA VERIFICARE IN TMA.PY")
        print("=" * 100)
        
        issues = [
            "1. load_thesaurus_values() usa i codici giusti?",
            "2. filter_area_by_localita() cerca tipologia '10.14' per area?",
            "3. filter_settore_by_area() cerca tipologia '10.15' per settore?",
            "4. aint è ComboBox o LineEdit?",
            "5. Le query includono lingua='IT'?",
            "6. I widget hanno i nomi corretti (comboBox_xxx)?",
            "7. setup_table_delegate() carica i valori del thesaurus?"
        ]
        
        for issue in issues:
            print(f"  ❓ {issue}")
            
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
        return False
        
    finally:
        conn.close()
    
    return True

def main():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato: {db_path}")
        return 1
    
    print("Debug completo thesaurus TMA")
    print("=" * 60)
    
    if debug_thesaurus(db_path):
        print("\n✅ Debug completato!")
    else:
        print("\n❌ Debug fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())