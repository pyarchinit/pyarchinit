#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to debug TMA materials saving issue
"""

import sqlite3
import os
import sys


def check_tma_materials(db_path, tma_id):
    """Check materials for a specific TMA ID"""
    print(f"\nChecking materials for TMA ID: {tma_id}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all materials for this TMA
        cursor.execute("""
            SELECT id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso
            FROM tma_materiali_ripetibili
            WHERE id_tma = ?
            ORDER BY id
        """, (tma_id,))
        
        materials = cursor.fetchall()
        
        if materials:
            print(f"Found {len(materials)} materials:")
            print("-" * 60)
            headers = ["ID", "TMA_ID", "Material", "Category", "Class", "Typology", "Definition", "Chronology", "Quantity", "Weight"]
            
            # Print headers
            print("| " + " | ".join(f"{h:^10}" for h in headers) + " |")
            print("|" + "-" * (len(headers) * 12 + len(headers) - 1) + "|")
            
            # Print data
            for mat in materials:
                row_data = []
                for i, val in enumerate(mat):
                    if val is None:
                        row_data.append("")
                    elif i in [0, 1]:  # ID fields
                        row_data.append(str(val))
                    elif i == 9:  # Weight
                        row_data.append(f"{val:.2f}" if val else "0.00")
                    else:
                        row_data.append(str(val)[:10])  # Truncate long strings
                
                print("| " + " | ".join(f"{d:^10}" for d in row_data) + " |")
        else:
            print("No materials found for this TMA ID")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        conn.close()


def list_recent_tma_records(db_path, limit=10):
    """List recent TMA records"""
    print(f"\nRecent TMA records (last {limit}):")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, sito, area, dscd, cassetta
            FROM tma_materiali_archeologici
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        records = cursor.fetchall()
        
        if records:
            headers = ["ID", "Site", "Area", "DSCD", "Cassetta"]
            
            # Print headers
            print("| " + " | ".join(f"{h:^12}" for h in headers) + " |")
            print("|" + "-" * (len(headers) * 14 + len(headers) - 1) + "|")
            
            # Print data
            for rec in records:
                row_data = []
                for val in rec:
                    if val is None:
                        row_data.append("")
                    else:
                        row_data.append(str(val)[:12])  # Truncate long strings
                
                print("| " + " | ".join(f"{d:^12}" for d in row_data) + " |")
                
                # Check materials count for each TMA
                cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili WHERE id_tma = ?", (rec[0],))
                mat_count = cursor.fetchone()[0]
                if mat_count > 0:
                    print(f"  └─> {mat_count} materials")
        else:
            print("No TMA records found")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        conn.close()


def check_duplicate_material_ids(db_path):
    """Check for duplicate material IDs"""
    print("\nChecking for duplicate material IDs:")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, COUNT(*) as count
            FROM tma_materiali_ripetibili
            GROUP BY id
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate IDs:")
            for dup_id, count in duplicates:
                print(f"  - ID {dup_id}: {count} occurrences")
        else:
            print("No duplicate material IDs found (good!)")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        conn.close()


def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return 1
        
    print(f"Testing TMA materials in: {db_path}")
    
    # List recent TMA records
    list_recent_tma_records(db_path)
    
    # Check for duplicate IDs
    check_duplicate_material_ids(db_path)
    
    # If specific TMA ID provided as argument, check its materials
    if len(sys.argv) > 1:
        try:
            tma_id = int(sys.argv[1])
            check_tma_materials(db_path, tma_id)
        except ValueError:
            print(f"\nInvalid TMA ID: {sys.argv[1]}")
    else:
        print("\nTip: Run with TMA ID as argument to see its materials:")
        print(f"  python {sys.argv[0]} <TMA_ID>")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())