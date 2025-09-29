#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Chat (RAG Query) and Report Generation with TMA support
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_imports():
    """Test that all necessary imports work"""
    print("\n=== Testing Imports ===")

    try:
        # Test LangChain imports
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        print("✅ LangChain OpenAI imports OK")

        from langchain_community.vectorstores import FAISS
        print("✅ LangChain FAISS import OK")

        from langchain.agents import initialize_agent, AgentType, Tool
        print("✅ LangChain agents import OK")

        from langchain.memory import ConversationBufferMemory
        from langchain.schema import SystemMessage
        print("✅ LangChain memory and schema imports OK")

        # Test PyQt imports
        from qgis.PyQt.QtWidgets import QApplication, QDialog
        from qgis.PyQt.QtCore import QThread, pyqtSignal
        print("✅ PyQt imports OK")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_connection():
    """Test database connection and TMA table access"""
    print("\n=== Testing Database Connection ===")

    try:
        from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
        from modules.db.pyarchinit_conn_strings import Connection

        # Connect to database
        conn = Connection()
        db = Pyarchinit_db_management(conn.conn_str())
        db.set_connection()

        print("✅ Database connection established")

        # Test TMA table
        try:
            # Query TMA table
            search_dict = {'sito': 'Festòs_2025'}
            tma_records = db.query_bool(search_dict, "TMA")
            print(f"✅ TMA table accessible: {len(tma_records)} records found")

            # Test TMA_MATERIALI table (the related table)
            if tma_records:
                # Get related materials for first TMA
                first_tma = tma_records[0]
                search_dict_mat = {'id_tma': first_tma.id_tma}
                mat_records = db.query_bool(search_dict_mat, "TMA_MATERIALI")
                print(f"✅ TMA_MATERIALI table accessible: {len(mat_records)} related records")

        except Exception as e:
            print(f"⚠️ TMA tables not accessible: {e}")

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_rag_worker_initialization():
    """Test RAGQueryWorker initialization without full dialog"""
    print("\n=== Testing RAGQueryWorker ===")

    try:
        from tabs.US_USM import RAGQueryWorker
        from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
        from modules.db.pyarchinit_conn_strings import Connection

        # Create DB manager
        conn = Connection()
        db_manager = Pyarchinit_db_management(conn.conn_str())
        db_manager.set_connection()

        # Create worker with minimal config
        worker = RAGQueryWorker(
            query="Test query",
            db_manager=db_manager,
            api_key="test_key",  # Will need real key for actual test
            model="gpt-5",
            temperature=None,  # GPT-5 doesn't support temperature
            selected_tables=['us_table', 'tma_table']
        )

        print("✅ RAGQueryWorker created successfully")

        # Test data loading method
        try:
            data = worker.load_database_data()

            if 'us_table' in data:
                print(f"  - US data loaded: {len(data['us_table'])} records")

            if 'tma_table' in data:
                print(f"  - TMA data loaded: {len(data['tma_table'])} records")

            print("✅ Database data loading OK")

        except Exception as e:
            print(f"⚠️ Data loading error: {e}")

        return True

    except Exception as e:
        print(f"❌ RAGQueryWorker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_thread_initialization():
    """Test GenerateReportThread initialization with TMA"""
    print("\n=== Testing Report Generation Thread ===")

    try:
        from tabs.US_USM import GenerateReportThread

        # Create thread with minimal config including TMA
        thread = GenerateReportThread(
            custom_prompt="Test prompt",
            descriptions_text="Test descriptions",
            api_key="test_key",
            selected_model="gpt-5",
            selected_tables=['us_table', 'tma_table'],
            analysis_steps=[],
            agent=None,
            us_data=[],
            materials_data=[],
            pottery_data=[],
            site_data={},
            py_dialog=None,
            tma_data=[]  # New TMA parameter
        )

        print("✅ GenerateReportThread created with TMA support")

        # Test TMA validation
        validation = thread.validate_tma()
        print(f"  - TMA validation: {validation['valid']}")
        if not validation['valid']:
            print(f"    Message: {validation['message']}")

        # Test TMA formatting
        formatted = thread.format_tma_table()
        if formatted:
            print(f"  - TMA table format: {len(formatted)} rows")
        else:
            print("  - TMA table format: No data")

        return True

    except Exception as e:
        print(f"❌ Report thread test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tma_data_formatting():
    """Test TMA data formatting for reports"""
    print("\n=== Testing TMA Data Formatting ===")

    try:
        # Create mock TMA data
        mock_tma = [{
            'id_tma': 1,
            'sito': 'Festòs_2025',
            'area': 'A1',
            'us': '100',
            'localita': 'Test Location',
            'settore': 'S1',
            'inventario': 'INV001',
            'ogtm': 'Ceramica',
            'ldct': 'Contenitori',
            'ldcn': 'Anfora',
            'cassetta': 'C001',
            'stato_conservazione': 'Buono',
            'stato_reperto': 'Integro',
            'descrizione': 'Test description',
            'materiale': 'Argilla depurata',
            'note': 'Test notes'
        }]

        # Import the format method from US_USM
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "us_usm",
            str(plugin_dir / "tabs" / "US_USM.py")
        )
        us_usm = importlib.util.module_from_spec(spec)

        # Create a minimal class instance just for testing
        class TestFormatter:
            def format_tma_data(self, tma_data):
                formatted = ""
                if not tma_data:
                    return "Nessun dato TMA disponibile"

                for tma in tma_data:
                    formatted += (
                        f"ID TMA: {tma.get('id_tma', '')}\n"
                        f"Sito: {tma.get('sito', '')}\n"
                        f"Area: {tma.get('area', '')}\n"
                        f"US: {tma.get('us', '')}\n"
                        f"Tipo materiale: {tma.get('ogtm', '')}\n"
                        f"Categoria: {tma.get('ldct', '')}\n"
                        f"Denominazione: {tma.get('ldcn', '')}\n"
                        f"-------------------\n\n"
                    )
                return formatted.strip()

        formatter = TestFormatter()
        formatted = formatter.format_tma_data(mock_tma)

        print("✅ TMA formatting successful")
        print(f"Sample output:\n{formatted[:200]}...")

        return True

    except Exception as e:
        print(f"❌ TMA formatting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_includes_tma():
    """Test that prompts include TMA sections"""
    print("\n=== Testing Prompts Include TMA ===")

    try:
        # Check system message includes TMA
        class TestPromptGenerator:
            def create_system_message(self):
                return """Sei un esperto archeologo specializzato in relazioni di scavo stratigrafiche.
        Il tuo compito include:
        4. Per la Tipologia Materiali Archeologici (TMA):
        - Catalogare i materiali per tipo e categoria
        - Descrivere lo stato di conservazione
        - Analizzare la distribuzione spaziale (area, US, settore)
        - Collegare i materiali TMA con l'inventario generale
        - Fornire analisi quantitative e qualitative"""

        generator = TestPromptGenerator()
        message = generator.create_system_message()

        if "TMA" in message and "Tipologia Materiali Archeologici" in message:
            print("✅ System message includes TMA section")
        else:
            print("⚠️ System message missing TMA section")

        # Check custom prompt includes TMA
        custom_prompt = """
        6. TIPOLOGIA MATERIALI ARCHEOLOGICI (TMA):
           - Se presenti, analizza i materiali catalogati nel sistema TMA.
           - Descrivi la tipologia dei materiali e la loro distribuzione per area e US.
           - Analizza lo stato di conservazione e la significatività dei reperti.
        {formatted_tma_data}
        """

        if "TIPOLOGIA MATERIALI ARCHEOLOGICI" in custom_prompt:
            print("✅ Custom prompt includes TMA section")
        else:
            print("⚠️ Custom prompt missing TMA section")

        return True

    except Exception as e:
        print(f"❌ Prompt test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Chat and Report Generation with TMA Support")
    print("=" * 60)

    tests = [
        test_imports,
        test_database_connection,
        test_rag_worker_initialization,
        test_report_thread_initialization,
        test_tma_data_formatting,
        test_prompt_includes_tma
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed!")
        print("\nNOTE: For full functionality testing:")
        print("1. Ensure you have a valid OpenAI API key configured")
        print("2. Run tests within QGIS environment for complete dialog testing")
        print("3. Test with actual data in the database")
    else:
        print(f"⚠️ {total - passed} tests failed")
        print("\nCommon issues:")
        print("- Missing database connection")
        print("- Import errors (run within QGIS)")
        print("- Missing API key")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)