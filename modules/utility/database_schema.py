"""
Database schema module - SQLAlchemy 2.0 compatible
Lazy initialization to avoid connection at import time
"""
from sqlalchemy import MetaData, create_engine

# Global variables for lazy initialization
_engine = None
_metadata = None
_initialized = False


def get_engine():
    """Get or create the database engine lazily"""
    global _engine
    if _engine is None:
        from ..db.pyarchinit_conn_strings import Connection
        internal_connection = Connection()
        _engine = create_engine(internal_connection.conn_str(), echo=False)
    return _engine


def get_metadata():
    """Get or create the metadata lazily"""
    global _metadata, _initialized
    if _metadata is None:
        _metadata = MetaData()

    if not _initialized:
        _initialize_tables()
        _initialized = True

    return _metadata


def _initialize_tables():
    """Initialize all table definitions"""
    global _metadata

    # Import table classes only when needed
    try:
        from modules.db.structures_metadata.Campioni_table import Campioni_table
        from modules.db.structures_metadata.Documentazione_table import Documentazione_table
        from modules.db.structures_metadata.Inventario_materiali_table import Inventario_materiali_table
        from modules.db.structures_metadata.Media_to_Entity_table import Media_to_Entity_table
        from modules.db.structures_metadata.Media_to_Entity_table_view import Media_to_Entity_table_view
        from modules.db.structures_metadata.Periodizzazione_table import Periodizzazione_table
        from modules.db.structures_metadata.Pottery_table import PotteryTable
        from modules.db.structures_metadata.SCHEDAIND_table import SCHEDAIND_table
        from modules.db.structures_metadata.Site_table import Site_table
        from modules.db.structures_metadata.Struttura_table import Struttura_table
        from modules.db.structures_metadata.Tma_materiali_table import Tma_materiali_table
        from modules.db.structures_metadata.Tma_table import Tma_table
        from modules.db.structures_metadata.Tomba_table import Tomba_table
        from modules.db.structures_metadata.US_table import US_table
        from modules.db.structures_metadata.pycampioni import pycampioni
        from modules.db.structures_metadata.pydocumentazione import pydocumentazione
        from modules.db.structures_metadata.pyindividui import pyindividui
        from modules.db.structures_metadata.pylineeriferimento import pylineeriferimento
        from modules.db.structures_metadata.pyquote import pyquote
        from modules.db.structures_metadata.pyquote_usm import pyquote_usm
        from modules.db.structures_metadata.pyreperti import pyreperti
        from modules.db.structures_metadata.pyripartizioni_spaziali import pyripartizioni_spaziali
        from modules.db.structures_metadata.pysezioni import pysezioni
        from modules.db.structures_metadata.pysito_point import pysito_point
        from modules.db.structures_metadata.pysito_polygon import pysito_polygon
        from modules.db.structures_metadata.pystrutture import pystrutture
        from modules.db.structures_metadata.pytomba import pytomba
        from modules.db.structures_metadata.pyunitastratigrafiche import pyunitastratigrafiche
        from modules.db.structures_metadata.pyunitastratigrafiche_usm import pyunitastratigrafiche_usm
        from modules.db.structures_metadata.pyus_negative import pyus_negative

        # Initialize tables if they have define_table method
        table_classes = [
            Campioni_table, Documentazione_table, Inventario_materiali_table,
            Media_to_Entity_table, Media_to_Entity_table_view, Periodizzazione_table,
            PotteryTable, SCHEDAIND_table, Site_table, Struttura_table,
            Tma_table, Tma_materiali_table, Tomba_table, US_table,
            pyunitastratigrafiche, pyunitastratigrafiche_usm, pysito_point,
            pysito_polygon, pyquote, pyquote_usm, pyus_negative, pystrutture,
            pyreperti, pyindividui, pycampioni, pytomba, pydocumentazione,
            pylineeriferimento, pyripartizioni_spaziali, pysezioni
        ]

        for table_class in table_classes:
            if hasattr(table_class, 'define_table'):
                try:
                    table_class.define_table(_metadata)
                except Exception:
                    pass  # Table might already be defined

    except ImportError as e:
        pass  # Some modules might not be available


def create_all_tables():
    """Create all tables in the database - call explicitly when needed"""
    try:
        engine = get_engine()
        metadata = get_metadata()
        metadata.create_all(engine)
    except Exception:
        pass  # Tables already exist or geometry not supported


# For backward compatibility - these are now functions
def get_engine_compat():
    return get_engine()

def get_metadata_compat():
    return get_metadata()

# Expose as module-level for backward compatibility (lazy)
engine = property(lambda self: get_engine())
metadata = property(lambda self: get_metadata())
