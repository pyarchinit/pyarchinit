import os
import random


from qgis.core import QgsVectorLayer, QgsFillSymbol, QgsRuleBasedRenderer,QgsExpression,QgsFeatureRequest,QgsMapLayerStyle,QgsCategorizedSymbolRenderer, QgsRendererCategory
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt

from qgis.PyQt.QtWidgets import QMessageBox,QInputDialog


from sqlalchemy import create_engine, text


class ThesaurusStyler:
    def __init__(self, default_style_path):
        """
        Inizializza la classe con il percorso dello stile QML predefinito.

        :param default_style_path: Percorso del file QML di default
        """
        self.default_style_path = default_style_path
        self.default_style = self.load_default_style()

    def load_default_style(self):
        """
        Carica lo stile predefinito dal file QML.
        """
        if os.path.exists(self.default_style_path):
            # Crea un layer temporaneo
            temp_layer = QgsVectorLayer("Polygon?crs=epsg:4326", "temp", "memory")

            # Carica lo stile sul layer temporaneo
            temp_layer.loadNamedStyle(self.default_style_path)

            # Estrai il simbolo dal renderer del layer
            if temp_layer.renderer():
                symbol = temp_layer.renderer().symbol()
                if symbol:
                    return symbol.clone()

        # Se qualcosa va storto, restituisci un simbolo di default
        return QgsFillSymbol.createSimple({'color': '200,200,200,100', 'outline_color': 'black'})

    def get_style(self, sigla):
        """
        Restituisce lo stile per una data sigla.
        In questo caso, restituisce sempre lo stile predefinito.

        :param sigla: La sigla per cui si vuole lo stile (non utilizzata in questa implementazione)
        :return: QgsFillSymbol predefinito
        """
        return self.default_style.clone() if self.default_style else None

    def apply_style_to_layer(self, layer, d_stratigrafica_field, thesaurus_mapping):
        """
        Applica gli stili al layer basandosi sul mapping del thesaurus.

        :param layer: Il layer QGIS a cui applicare gli stili
        :param d_stratigrafica_field: Il nome del campo contenente i valori d_stratigrafica
        :param thesaurus_mapping: Il mapping tra d_stratigrafica e sigla_estesa
        """
        if not layer.isValid():
            print("Layer non valido")
            return

        categories = []
        unique_values = layer.uniqueValues(layer.fields().indexOf(d_stratigrafica_field))

        for value in unique_values:
            sigla_estesa = thesaurus_mapping.get(value)
            if sigla_estesa:
                symbol = self.get_style(sigla_estesa)
                if symbol:
                    symbol.setOpacity(0.3)
                    symbol.setColor(QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                    category = QgsRendererCategory(value, symbol, str(value))
                    categories.append(category)
                    print(f"Categoria creata per {value}: {sigla_estesa} con colore {symbol.color().name()}")
            else:
                print(f"Nessuna sigla trovata per il valore {value}")

        if categories:
            renderer = QgsCategorizedSymbolRenderer(d_stratigrafica_field, categories)
            layer.setRenderer(renderer)
            print(f"Renderer applicato con {len(categories)} categorie")
        else:
            print("Nessuna categoria creata, il renderer non è stato applicato")

        layer.triggerRepaint()


class USViewStyler:
    def __init__(self, connection):
        self.connection = connection
        self.engine = create_engine(self.connection.conn_str())
        self.DB_SERVER = "sqlite" if self.connection.conn_str().startswith('sqlite') else "postgres"
        self.us_data = self._load_us_data()
        self.us_styles = self._create_styles_for_us()

    def _load_us_data(self):
        query = text("SELECT d_stratigrafica, tipo_us_s, stratigraph_index_us FROM pyarchinit_us_view")
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row) for row in result]

    def _create_style(self, d_stratigrafica, tipo_us_s, stratigraph_index_us):
        symbol = QgsFillSymbol.createSimple({})

        if stratigraph_index_us == 1:
            color = QColor(hash(str(d_stratigrafica)) % 256, hash(str(d_stratigrafica) * 2) % 256,
                           hash(str(d_stratigrafica) * 3) % 256)
        else:
            color = QColor(255, 255, 255)  # Bianco per stratigraph_index_us = 2

        symbol.setColor(color)
        symbol.setOpacity(random.uniform(0.5, 1.0) if stratigraph_index_us == 1 else 1.0)

        tipo_us_s = tipo_us_s or "non specificato"

        if tipo_us_s.lower() == "negativa":
            symbol.symbolLayer(0).setStrokeStyle(Qt.DotLine)
        elif tipo_us_s.lower() == "non specificato":
            symbol.symbolLayer(0).setStrokeStyle(Qt.DashLine)

        else:
            symbol.symbolLayer(0).setStrokeStyle(Qt.SolidLine)

        symbol.symbolLayer(0).setStrokeColor(QColor(0, 0, 0))
        symbol.symbolLayer(0).setStrokeWidth(0.5)
        return symbol

    def _create_styles_for_us(self):
        styles = {}
        for entry in self.us_data:
            d_stratigrafica = entry['d_stratigrafica'] or "non specificato"
            tipo_us_s = entry['tipo_us_s'] or "non specificato"
            stratigraph_index_us = entry['stratigraph_index_us'] or 1
            key = (d_stratigrafica, tipo_us_s, stratigraph_index_us)
            styles[key] = self._create_style(d_stratigrafica, tipo_us_s, stratigraph_index_us)
        return styles

    def ask_user_style_preference(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText("Come vuoi gestire lo stile del layer?")
        msg_box.setWindowTitle("Scelta Stile")

        save_button = msg_box.addButton("Salva nuovo stile", QMessageBox.ActionRole)
        load_button = msg_box.addButton("Carica stile esistente", QMessageBox.ActionRole)
        temp_button = msg_box.addButton("Usa stile temporaneo", QMessageBox.ActionRole)

        msg_box.exec_()

        if msg_box.clickedButton() == save_button:
            return "save"
        elif msg_box.clickedButton() == load_button:
            return "load"
        else:
            return "temp"

    def load_style_from_db(self, layer):
        try:
            styles = layer.listStylesInDatabase()



            # Verifica se styles è una tupla e ha almeno quattro elementi
            if not isinstance(styles, tuple) or len(styles) < 4:
                self.show_message("Formato dei dati degli stili non valido.")
                return None

            # Verifica se il secondo e terzo elemento della tupla sono liste non vuote
            if not isinstance(styles[1], list) or not styles[1] or not isinstance(styles[2], list) or not styles[2]:
                self.show_message("Nessuno stile salvato trovato nel database.")
                return None


            style_ids = styles[1]
            style_names = styles[2]

            if len(style_ids) == 1:
                # Se c'è solo uno stile, caricalo direttamente
                style_id = style_ids[0]
                style_xml = layer.getStyleFromDatabase(style_id)[0]
                return style_xml
            else:
                # Se ci sono più stili, chiedi all'utente quale caricare
                style_name, ok = QInputDialog.getItem(None, "Seleziona Stile",
                                                      "Scegli lo stile da caricare:",
                                                      style_names, 0, False)
                if ok and style_name:
                    # Trova l'ID dello stile selezionato
                    index = style_names.index(style_name)
                    style_id = style_ids[index]
                    style_xml = layer.getStyleFromDatabase(style_id)[0]
                    return style_xml
                else:
                    self.show_message("Selezione dello stile annullata.")
                    return None
        except Exception as e:
            self.show_message(f"Errore nel caricamento degli stili: {str(e)}")
            return None

    def apply_style_to_layer(self, layer):
        if not layer.isValid():
            print("Layer non valido")
            return

        fields = layer.fields()
        required_fields = ['d_stratigrafica', 'tipo_us_s', 'stratigraph_index_us']
        if not all(field in fields.names() for field in required_fields):
            print(f"Campi mancanti nel layer. Richiesti: {', '.join(required_fields)}")
            return

        choice = self.ask_user_style_preference()

        if choice == "load":

            saved_style = self.load_style_from_db(layer)
            if saved_style:
                layer.loadNamedStyle(saved_style)
                print("Stile caricato dal database")
            else:
                print("Nessuno stile salvato trovato o selezione annullata. Verrà creato uno stile temporaneo.")
                self._apply_temp_style(layer)
        elif choice == "save":
            self._apply_temp_style(layer)
            self.save_style_to_db(layer)
        else:  # temp
            self._apply_temp_style(layer)

        layer.triggerRepaint()
        layer.legendChanged.emit()
        print(f"Stile applicato con {len(layer.renderer().rootRule().children())} regole")

    def show_message(self, message):
        """Mostra un messaggio all'utente."""
        QMessageBox.information(None, 'Informazione', message, QMessageBox.Ok)

    def _apply_temp_style(self, layer):
        root_rule = QgsRuleBasedRenderer.Rule(None)
        all_rules = []

        # Raggruppa gli stili per d_stratigrafica e stratigraph_index_us
        grouped_styles = {}
        for (d_stratigrafica, tipo_us_s, stratigraph_index_us), symbol in self.us_styles.items():
            key = (d_stratigrafica, stratigraph_index_us)
            if key not in grouped_styles:
                grouped_styles[key] = []
            grouped_styles[key].append((tipo_us_s, symbol))

        for (d_stratigrafica, stratigraph_index_us), style_group in grouped_styles.items():
            expression = f"\"d_stratigrafica\" = '{d_stratigrafica}' AND \"stratigraph_index_us\" = {stratigraph_index_us}"
            request = QgsFeatureRequest(QgsExpression(expression))
            count = sum(1 for _ in layer.getFeatures(request))

            if count > 0:
                # Crea un nuovo simbolo combinando gli stili per i diversi tipo_us_s
                combined_symbol = QgsFillSymbol.createSimple({})
                combined_symbol.setColor(style_group[0][1].color())  # Usa il colore del primo stile

                # Imposta lo stile del contorno in base ai tipo_us_s presenti
                if any(tipo == "negativa" for tipo, _ in style_group):
                    combined_symbol.symbolLayer(0).setStrokeStyle(Qt.DotLine)
                elif any(tipo == "non specificato" for tipo, _ in style_group):
                    combined_symbol.symbolLayer(0).setStrokeStyle(Qt.DashLine)
                else:
                    combined_symbol.symbolLayer(0).setStrokeStyle(Qt.SolidLine)

                combined_symbol.symbolLayer(0).setStrokeColor(QColor(0, 0, 0))
                combined_symbol.symbolLayer(0).setStrokeWidth(0.5)

                label = f"{d_stratigrafica} - Indice {stratigraph_index_us} (Count: {count})"
                rule = QgsRuleBasedRenderer.Rule(combined_symbol, 0, 0, expression, label)
                all_rules.append((stratigraph_index_us, rule))
            else:
                print(f"Nessun elemento trovato per: {d_stratigrafica} - Indice {stratigraph_index_us}")

        all_rules.sort(key=lambda x: x[0], reverse=False)
        for _, rule in all_rules:
            root_rule.appendChild(rule)

        renderer = QgsRuleBasedRenderer(root_rule)
        layer.setRenderer(renderer)

    def save_style_to_db(self, layer):
        try:
            # Chiedi all'utente di inserire un nome per lo stile
            style_name, ok = QInputDialog.getText(None, "Salva Stile",
                                                  "Inserisci un nome per lo stile:")
            if ok and style_name:
                style = QgsMapLayerStyle()
                style.readFromLayer(layer)

                # Prova a salvare lo stile e cattura eventuali eccezioni
                try:
                    result = layer.saveStyleToDatabase(style_name, "", True, "")
                    self.show_message(f"Risultato del salvataggio: {result}")
                except Exception as e:
                    self.show_message(f"Eccezione durante il salvataggio: {str(e)}")

                    return

                if result is None:
                    self.show_message("Il salvataggio dello stile ha restituito None")
                    self.show_message(f"Tipo di layer: {layer.type()}")
                    self.show_message(
                        f"Provider: {layer.dataProvider().name() if layer.dataProvider() else 'Nessun provider'}")
                    self.show_message(f"Fonte dei dati: {layer.source()}")
                else:
                    self.show_message(f"Stile '{style_name}' salvato nel database. Risultato: {result}")
            else:
                self.show_message("Salvataggio dello stile annullato")
        except Exception as e:
            self.show_message(f"Errore nel salvataggio dello stile: {str(e)}")


    def get_all_styles(self):
        return self.us_styles