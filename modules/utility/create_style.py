import random
from qgis.core import QgsFillSymbol
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface

from sqlalchemy import create_engine, text



class ThesaurusStyler:
    def __init__(self, connection):
        """
        Inizializza la classe con una connessione SQLAlchemy.

        :param connection: Oggetto Connection di SQLAlchemy
        """
        self.connection = connection
        self.engine = create_engine(self.connection.conn_str())
        self.DB_SERVER = "sqlite" if self.connection.conn_str().startswith('sqlite') else "postgres"
        self.thesaurus_data = self._load_thesaurus_data()
        self.us_table_styles = self._create_styles_for_us_table()

    def _load_thesaurus_data(self):
        """
        Carica i dati del thesaurus dal database usando SQLAlchemy.

        :return: Lista di dizionari contenenti i dati del thesaurus
        """
        query = text("SELECT nome_tabella, sigla, sigla_estesa FROM pyarchinit_thesaurus_sigle")

        with self.engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row) for row in result]

    def _create_style_from_thesaurus(self, sigla_estesa):
        """
        Crea uno stile basato sulla sigla_estesa fornita dal thesaurus.

        :param sigla_estesa: La descrizione estesa della sigla dal thesaurus
        :return: Un oggetto QgsFillSymbol con stile specifico
        """
        symbol = QgsFillSymbol.createSimple({})

        # Genera un colore casuale ma consistente per ogni sigla_estesa
        color = QColor(hash(sigla_estesa) % 256, hash(sigla_estesa * 2) % 256, hash(sigla_estesa * 3) % 256)
        symbol.setColor(color)

        # Imposta un'opacità casuale ma non troppo trasparente
        opacity = random.uniform(0.5, 1.0)
        symbol.setOpacity(opacity)

        # Imposta uno stile di riempimento casuale
        fill_styles = [
            Qt.SolidPattern,
            Qt.Dense1Pattern,
            Qt.Dense2Pattern,
            Qt.Dense3Pattern,
            Qt.Dense4Pattern,
            Qt.Dense5Pattern,
            Qt.Dense6Pattern,
            Qt.Dense7Pattern
        ]
        symbol.symbolLayer(0).setBrushStyle(random.choice(fill_styles))

        # Imposta un bordo con colore leggermente più scuro
        border_color = color.darker(120)
        symbol.symbolLayer(0).setStrokeColor(border_color)
        symbol.symbolLayer(0).setStrokeWidth(0.5)

        return symbol
    def _create_styles_for_us_table(self):
        """
        Crea stili per tutte le entries nella us_table del thesaurus.

        :return: Dizionario con sigla come chiave e QgsFillSymbol come valore
        """
        styles = {}
        for entry in self.thesaurus_data:
            if entry['nome_tabella'] == 'us_table':
                styles[entry['sigla_estesa']] = self._create_style_from_thesaurus(entry['sigla_estesa'])
        return styles

    def get_style(self, sigla):
        """
        Restituisce lo stile per una data sigla.

        :param sigla: La sigla per cui si vuole lo stile
        :return: QgsFillSymbol corrispondente alla sigla
        """
        return self.us_table_styles.get(sigla)

    def apply_style_to_layer(self, layer, sigla):
        """
        Applica lo stile corrispondente alla sigla al layer fornito.

        :param layer: Il layer QGIS a cui applicare lo stile
        :param sigla: La sigla dello stile da applicare
        """
        style = self.get_style(sigla)
        if style:
            layer.renderer().setSymbol(style)
            layer.triggerRepaint()
        else:
            print(f"Nessuno stile trovato per la sigla: {sigla}")

    def get_all_styles(self):
        """
        Restituisce tutti gli stili creati.

        :return: Dizionario con tutti gli stili
        """
        return self.us_table_styles


