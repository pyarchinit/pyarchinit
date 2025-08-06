# -*- coding: utf-8 -*-
"""
Thesaurus compatibility module for PyArchInit
Handles backward compatibility between database table names and friendly UI names
"""

# Mapping of database table names to friendly UI names
TABLE_NAME_MAPPINGS = {
    # TMA tables
    'tma_table': 'TMA materiali archeologici',
    'tma_materiali_table': 'TMA Materiali Ripetibili',
    'tma_materiali_archeologici': 'TMA materiali archeologici',
    'tma_materiali_ripetibili': 'TMA Materiali Ripetibili',
    
    # Other tables (exact mappings from pyarchinit_db_update_thesaurus.py)
    'inventario_materiali_table': 'Inventario Materiali',
    'tomba_table': 'Tomba',
    'struttura_table': 'Struttura',
    'us_table': 'US',
    'us_table_usm': 'USM',
    'site_table': 'Sito',
    'pyarchinit_reperti': 'Reperti',
    'individui_table': 'Individui',
    'pottery_table': 'Pottery',
    
    # Additional mappings for all forms
    'documentazione_table': 'Documentazione',
    'campioni_table': 'Campioni',
    'detsesso_table': 'Detsesso',
    'deteta_table': 'Deteta',
    'inventario_lapidei_table': 'Inventario Lapidei',
    'media_table': 'MEDIA',
    'media_thumb_table': 'MEDIA_THUMB',
    'mediatoentity_table': 'MEDIATOENTITY',
    'mediaview_table': 'MEDIAVIEW',
    'pdf_administrator_table': 'PDF_ADMINISTRATOR',
    'periodizzazione_table': 'PERIODIZZAZIONE',
    'pyquote_table': 'PYQUOTE',
    'pyquoteusm_table': 'PYQUOTEUSM',
    'pyus_table': 'PYUS',
    'pyusm_table': 'PYUSM',
    'pyus_negative_table': 'PYUS_NEGATIVE',
    'pystrutture_table': 'PYSTRUTTURE',
    'pyreperti_table': 'PYREPERTI',
    'pyindividui_table': 'PYINDIVIDUI',
    'pycampioni_table': 'PYCAMPIONI',
    'pytomba_table': 'PYTOMBA',
    'pydocumentazione_table': 'PYDOCUMENTAZIONE',
    'pylineeriferimento_table': 'PYLINEERIFERIMENTO',
    'pyripartizioni_spaziali_table': 'PYRIPARTIZIONI_SPAZIALI',
    'pysezioni_table': 'PYSEZIONI',
    'pysito_point_table': 'PYSITO_POINT',
    'pysito_polygon_table': 'PYSITO_POLYGON',
    'ut_table': 'UT'
}

# Reverse mapping for lookups
UI_NAME_TO_TABLE = {v: k for k, v in TABLE_NAME_MAPPINGS.items()}


def get_ui_name(table_name):
    """
    Get the friendly UI name for a database table name.
    Returns the original name if no mapping exists.
    """
    return TABLE_NAME_MAPPINGS.get(table_name, table_name)


def get_table_name(ui_name):
    """
    Get the database table name for a friendly UI name.
    Returns the original name if no mapping exists.
    """
    # First check if it's already a table name
    if ui_name in TABLE_NAME_MAPPINGS:
        return ui_name
    
    # Check reverse mapping
    return UI_NAME_TO_TABLE.get(ui_name, ui_name)


def get_compatible_names(name):
    """
    Get all compatible names (both database and UI) for a given name.
    Returns a list of all possible names that should match.
    """
    names = [name]
    
    # Add UI name if this is a table name
    if name in TABLE_NAME_MAPPINGS:
        names.append(TABLE_NAME_MAPPINGS[name])
    
    # Add table name if this is a UI name
    if name in UI_NAME_TO_TABLE:
        names.append(UI_NAME_TO_TABLE[name])
    
    # For TMA tables, add all variations
    if 'tma' in name.lower() or 'TMA' in name:
        if 'ripetibili' in name.lower() or 'materiali_table' in name:
            names.extend(['tma_materiali_table', 'TMA materiali ripetibili', 'TMA Materiali Ripetibili', 'tma_materiali_ripetibili'])
        else:
            names.extend(['tma_table', 'TMA materiali archeologici', 'tma_materiali_archeologici'])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_names = []
    for n in names:
        if n not in seen:
            seen.add(n)
            unique_names.append(n)
    
    return unique_names