"""
Data conversion utilities for PyArchInit database import/export
Handles conversion of empty strings to None for numeric fields
"""

def convert_empty_to_none(value, field_type='text'):
    """
    Convert empty strings to None for database fields

    Args:
        value: The value to convert
        field_type: The expected field type ('text', 'integer', 'bigint', 'numeric', 'float')

    Returns:
        Converted value suitable for database insertion
    """
    if field_type in ['integer', 'bigint', 'numeric', 'float']:
        # For numeric types, convert empty string to None
        if value == '' or value == '""' or (isinstance(value, str) and value.strip() == ''):
            return None
        # Also handle cases where value is already None
        if value is None:
            return None
        # Try to convert to appropriate numeric type
        try:
            if field_type in ['integer', 'bigint']:
                return int(value) if value != '' else None
            elif field_type in ['numeric', 'float']:
                return float(value) if value != '' else None
        except (ValueError, TypeError):
            return None
    else:
        # For text fields, keep the value as is
        return value if value is not None else ''

def prepare_inventario_materiali_data(data_record):
    """
    Prepare inventario_materiali data for insertion
    Converts empty strings to None for numeric fields
    """
    return {
        'area': data_record.area,
        'us': data_record.us,
        'lavato': data_record.lavato,
        'nr_cassa': convert_empty_to_none(data_record.nr_cassa, 'text'),  # Changed to TEXT
        'luogo_conservazione': data_record.luogo_conservazione,
        'stato_conservazione': data_record.stato_conservazione,
        'datazione_reperto': data_record.datazione_reperto,
        'elementi_reperto': data_record.elementi_reperto,
        'misurazioni': data_record.misurazioni,
        'rif_biblio': data_record.rif_biblio,
        'tecnologie': data_record.tecnologie,
        'forme_minime': convert_empty_to_none(data_record.forme_minime, 'integer'),
        'forme_massime': convert_empty_to_none(data_record.forme_massime, 'integer'),
        'totale_frammenti': convert_empty_to_none(data_record.totale_frammenti, 'integer'),
        'corpo_ceramico': data_record.corpo_ceramico,
        'rivestimento': data_record.rivestimento,
        'diametro_orlo': convert_empty_to_none(data_record.diametro_orlo, 'float'),
        'peso': convert_empty_to_none(data_record.peso, 'float'),
        'tipo': data_record.tipo,
        'eve_orlo': convert_empty_to_none(data_record.eve_orlo, 'float'),
        'repertato': data_record.repertato,
        'diagnostico': data_record.diagnostico,
        'n_reperto': convert_empty_to_none(data_record.n_reperto, 'bigint'),
        'tipo_contenitore': data_record.tipo_contenitore,
        'struttura': data_record.struttura,
        'years': convert_empty_to_none(data_record.years, 'integer'),
        'schedatore': data_record.schedatore,
        'date_scheda': data_record.date_scheda,
        'punto_rinv': data_record.punto_rinv,
        'negativo_photo': data_record.negativo_photo,
        'diapositiva': data_record.diapositiva
    }

def prepare_thesaurus_data(data_record):
    """
    Prepare thesaurus data for insertion
    Converts empty strings to None/0 for numeric fields
    """
    return {
        'nome_tabella': data_record.nome_tabella,
        'sigla': data_record.sigla,
        'sigla_estesa': data_record.sigla_estesa,
        'descrizione': data_record.descrizione,
        'tipologia_sigla': data_record.tipologia_sigla,
        'lingua': data_record.lingua,
        'order_layer': convert_empty_to_none(getattr(data_record, 'order_layer', 0), 'integer') or 0,
        'id_parent': convert_empty_to_none(getattr(data_record, 'id_parent', None), 'integer'),
        'parent_sigla': getattr(data_record, 'parent_sigla', None),
        'hierarchy_level': convert_empty_to_none(getattr(data_record, 'hierarchy_level', 0), 'integer') or 0
    }

def prepare_tma_data(data_record):
    """
    Prepare TMA data for insertion
    Handles both tma_materiali_archeologici and ripetibili tables
    """
    # Fix: Check for 'dtzs' attribute and convert to 'dtzg'
    dtzg_value = None
    if hasattr(data_record, 'dtzg'):
        dtzg_value = data_record.dtzg
    elif hasattr(data_record, 'dtzs'):
        # Handle old field name 'dtzs'
        dtzg_value = data_record.dtzs

    return {
        'sito': data_record.sito,
        'area': data_record.area,
        'localita': getattr(data_record, 'localita', ''),
        'settore': getattr(data_record, 'settore', ''),
        'inventario': getattr(data_record, 'inventario', ''),
        'ogtm': data_record.ogtm,
        'ldct': data_record.ldct,
        'ldcn': data_record.ldcn,
        'vecchia_collocazione': data_record.vecchia_collocazione,
        'cassetta': data_record.cassetta,
        'scan': data_record.scan,
        'saggio': data_record.saggio,
        'vano_locus': data_record.vano_locus,
        'dscd': data_record.dscd,
        'dscu': data_record.dscu,
        'rcgd': data_record.rcgd,
        'rcgz': data_record.rcgz,
        'aint': data_record.aint,
        'aind': data_record.aind,
        'dtzg': dtzg_value,  # Use the corrected field
        'deso': data_record.deso,
        'nsc': getattr(data_record, 'nsc', ''),
        'ftap': data_record.ftap,
        'ftan': data_record.ftan,
        'drat': data_record.drat,
        'dran': data_record.dran,
        'draa': data_record.draa,
        'created_at': getattr(data_record, 'created_at', ''),
        'updated_at': getattr(data_record, 'updated_at', ''),
        'created_by': getattr(data_record, 'created_by', ''),
        'updated_by': getattr(data_record, 'updated_by', '')
    }