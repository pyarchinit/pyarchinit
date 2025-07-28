#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for TMA functionality
Tests:
1. Creating TMA records without materials
2. Creating TMA records with materials
3. PDF export functionality
"""

import sys
import os
from datetime import datetime

# Add the plugin path to Python path
plugin_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_path)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.entities.TMA import TMA
from modules.db.entities.TMA_MATERIALI import TMA_MATERIALI
from modules.utility.pyarchinit_exp_Tmasheet_pdf import single_TMA_pdf

def test_tma_functionality():
    """Test TMA record creation and PDF export"""
    
    # Initialize database connection
    conn = Connection()
    db_manager = Pyarchinit_db_management(conn.conn_str())
    db_manager.connection()
    
    print("=== Testing TMA Functionality ===")
    
    # Test 1: Create TMA record without materials
    print("\n1. Testing TMA record creation without materials...")
    try:
        test_tma = TMA(
            id=None,  # Will be auto-generated
            sito="Test Site",
            area="Area 1",
            ogtm="Ceramica",
            ldct="Deposito",
            ldcn="Deposito principale",
            vecchia_collocazione="Vecchia coll. 1",
            cassetta="TEST001",
            scan="Scavo 2025",
            saggio="Saggio A",
            vano_locus="Locus 1",
            dscd="2025-01-28",
            dscu="US 100",
            rcgd="",
            rcgz="",
            aint="",
            aind="",
            dtzg="Età romana",
            deso="Materiali vari da US 100",
            nsc="Note storico-critiche test",
            ftap="Digitale",
            ftan="IMG_001",
            drat="Pianta",
            dran="DIS_001",
            draa="E. Cocca",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            created_by="test_user",
            updated_by="test_user"
        )
        
        # Try to insert the record
        result = db_manager.insert_data_session(test_tma)
        if result:
            print("✓ Successfully created TMA record without materials")
            tma_id = result
        else:
            print("✗ Failed to create TMA record")
            return
            
    except Exception as e:
        print(f"✗ Error creating TMA record: {str(e)}")
        return
    
    # Test 2: Add materials to the TMA record
    print("\n2. Testing material addition to TMA record...")
    try:
        test_material = TMA_MATERIALI(
            id=None,
            id_tma=tma_id,
            madi="INV001",
            macc="ceramica",
            macl="ceramica comune",
            macp="anfora",
            macd="frammento di parete",
            cronologia_mac="I-II sec. d.C.",
            macq="5",
            peso=120.5,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            created_by="test_user",
            updated_by="test_user"
        )
        
        result = db_manager.insert_data_session(test_material)
        if result:
            print("✓ Successfully added material to TMA record")
        else:
            print("✗ Failed to add material")
            
    except Exception as e:
        print(f"✗ Error adding material: {str(e)}")
    
    # Test 3: Export TMA to PDF
    print("\n3. Testing PDF export...")
    try:
        # Retrieve the TMA record with materials
        search_dict = {'cassetta': 'TEST001'}
        tma_records = db_manager.query_bool(search_dict, 'TMA')
        
        if tma_records:
            tma_record = tma_records[0]
            
            # Get materials for this TMA
            mat_search = {'id_tma': tma_record.id}
            materials = db_manager.query_bool(mat_search, 'TMA_MATERIALI')
            
            # Generate PDF
            pdf_path = single_TMA_pdf([tma_record, materials])
            
            if os.path.exists(pdf_path):
                print(f"✓ Successfully exported PDF to: {pdf_path}")
            else:
                print("✗ Failed to create PDF file")
        else:
            print("✗ Could not retrieve TMA record for PDF export")
            
    except Exception as e:
        print(f"✗ Error exporting PDF: {str(e)}")
    
    # Clean up test data
    print("\n4. Cleaning up test data...")
    try:
        # Delete test materials first (due to foreign key constraint)
        if 'materials' in locals():
            for mat in materials:
                db_manager.delete_one_record('TMA_MATERIALI', 'id', mat.id)
        
        # Delete test TMA record
        if 'tma_id' in locals():
            db_manager.delete_one_record('TMA', 'id', tma_id)
            
        print("✓ Test data cleaned up successfully")
        
    except Exception as e:
        print(f"✗ Error cleaning up: {str(e)}")
    
    print("\n=== TMA Functionality Test Complete ===")

if __name__ == "__main__":
    test_tma_functionality()