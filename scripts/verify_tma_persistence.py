#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare la persistenza dei dati TMA
"""

import sqlite3
import sys
import time

def monitor_tma_data(db_path, interval=2, duration=10):
    """Monitora i dati TMA per vedere se vengono cancellati."""
    print(f"Monitoraggio dati TMA per {duration} secondi")
    print("=" * 60)
    
    start_time = time.time()
    last_count = -1
    last_materials_count = -1
    
    try:
        while time.time() - start_time < duration:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Conta record TMA
            cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
            tma_count = cursor.fetchone()[0]
            
            # Conta materiali
            cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
            materials_count = cursor.fetchone()[0]
            
            # Se è cambiato qualcosa, mostralo
            if tma_count != last_count or materials_count != last_materials_count:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] TMA: {tma_count} record, Materiali: {materials_count} record")
                
                # Se ci sono nuovi record, mostra l'ultimo
                if tma_count > 0 and tma_count != last_count:
                    cursor.execute("""
                        SELECT id, sito, area, localita, settore 
                        FROM tma_materiali_archeologici 
                        ORDER BY id DESC 
                        LIMIT 1
                    """)
                    row = cursor.fetchone()
                    print(f"           Ultimo: ID={row[0]}, Sito={row[1]}, Area={row[2]}")
                
                # Se i record sono diminuiti, segnala!
                if last_count > 0 and tma_count < last_count:
                    print(f"           ⚠️ ATTENZIONE: {last_count - tma_count} record TMA cancellati!")
                
                last_count = tma_count
                last_materials_count = materials_count
            
            conn.close()
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoraggio interrotto")
    except Exception as e:
        print(f"❌ Errore: {e}")

def show_final_state(db_path):
    """Mostra lo stato finale del database."""
    print("\n\nStato finale del database:")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Record TMA
        cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        tma_count = cursor.fetchone()[0]
        print(f"Record TMA totali: {tma_count}")
        
        if tma_count > 0:
            cursor.execute("""
                SELECT id, sito, area, localita, settore, created_by
                FROM tma_materiali_archeologici
                ORDER BY id DESC
                LIMIT 3
            """)
            print("\nUltimi 3 record TMA:")
            for row in cursor.fetchall():
                print(f"  ID: {row[0]}, Sito: {row[1]}, Area: {row[2]}")
                print(f"     Località: {row[3]}, Settore: {row[4]}, Creato da: {row[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Errore: {e}")

def main():
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    print("Verifica persistenza dati TMA")
    print("=" * 60)
    print("\nIstruzioni:")
    print("1. Lascia questo script in esecuzione")
    print("2. Vai in QGIS e salva un record TMA")
    print("3. Chiudi e riapri la scheda TMA")
    print("4. Osserva se i record vengono cancellati\n")
    
    # Monitora per 30 secondi
    monitor_tma_data(db_path, interval=1, duration=30)
    
    # Mostra stato finale
    show_final_state(db_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())