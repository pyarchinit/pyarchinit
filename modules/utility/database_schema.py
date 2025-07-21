from sqlalchemy import MetaData, create_engine

# Importa le classi delle tabelle
from modules.db.structures_metadata.Campioni_table import Campioni_table
# from modules.db.structures_metadata.DETETA_table import DETETA_table
# from modules.db.structures_metadata.DETSESSO_table import DETSESSO_table
from modules.db.structures_metadata.Documentazione_table import Documentazione_table
# from modules.db.structures_metadata.Inventario_Lapidei_table import Inventario_Lapidei_table
from modules.db.structures_metadata.Inventario_materiali_table import Inventario_materiali_table
# from modules.db.structures_metadata.Media_table import Media_table
# from modules.db.structures_metadata.Media_thumb_table import Media_thumb_table
from modules.db.structures_metadata.Media_to_Entity_table import Media_to_Entity_table
from modules.db.structures_metadata.Media_to_Entity_table_view import Media_to_Entity_table_view
# from modules.db.structures_metadata.PDF_administrator_table import PDF_administrator_table
from modules.db.structures_metadata.Periodizzazione_table import Periodizzazione_table
from modules.db.structures_metadata.Pottery_table import PotteryTable
# from modules.db.structures_metadata.Pyarchinit_thesaurus_sigle import Pyarchinit_thesaurus_sigle
from modules.db.structures_metadata.SCHEDAIND_table import SCHEDAIND_table
from modules.db.structures_metadata.Site_table import Site_table
from modules.db.structures_metadata.Struttura_table import Struttura_table
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
# from modules.db.structures_metadata.US_table_toimp import US_table_toimp
# from modules.db.structures_metadata.UT_table import UT_table
from modules.db.structures_metadata.pyunitastratigrafiche import pyunitastratigrafiche
from modules.db.structures_metadata.pyunitastratigrafiche_usm import pyunitastratigrafiche_usm
from modules.db.structures_metadata.pyus_negative import pyus_negative
from ..db.pyarchinit_conn_strings import Connection

# Crea una singola connessione e MetaData per l'applicazione
internal_connection = Connection()
engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
metadata = MetaData()
# Inizializza ogni classe di tabella con l'oggetto MetaData
Campioni_table.define_table(metadata)
# DETETA_table(metadata)
# DETSESSO_table(metadata)
Documentazione_table.define_table(metadata)
# Inventario_Lapidei_table(metadata)
Inventario_materiali_table.define_table(metadata)
# Media_table(metadata)
# Media_thumb_table(metadata)
Media_to_Entity_table.define_table(metadata)
Media_to_Entity_table_view.define_table(metadata)
# PDF_administrator_table(metadata)
Periodizzazione_table.define_table(metadata)
# Pyarchinit_thesaurus_sigle(metadata)
SCHEDAIND_table.define_table(metadata)
Site_table.define_table(metadata)
Struttura_table.define_table(metadata)
Tomba_table.define_table(metadata)
US_table.define_table(metadata)
# US_table_toimp(metadata)
# UT_table(metadata)
pyunitastratigrafiche.define_table(metadata)
pyunitastratigrafiche_usm.define_table(metadata)
pysito_point.define_table(metadata)
pysito_polygon.define_table(metadata)
pyquote.define_table(metadata)
pyquote_usm.define_table(metadata)
pyus_negative.define_table(metadata)
pystrutture.define_table(metadata)
pyreperti.define_table(metadata)
pyindividui.define_table(metadata)
pycampioni.define_table(metadata)
pytomba.define_table(metadata)
pydocumentazione.define_table(metadata)
pylineeriferimento.define_table(metadata)
pyripartizioni_spaziali.define_table(metadata)
pysezioni.define_table(metadata)
PotteryTable.define_table(metadata)
Tma_table.define_table(metadata)

# Creare tutte le tabelle nel database
metadata.create_all(engine)
# Definisci le tue tabelle qui, passando `metadata` a ogni classe di tabella se necessario
# Nota: Dovrai modificare le classi per accettare `metadata` come parametro, se non già fatto.


