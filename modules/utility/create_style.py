import hashlib
import os
import random
import re


from qgis.core import QgsVectorLayer, QgsFillSymbol, QgsRuleBasedRenderer,QgsExpression,QgsFeatureRequest,QgsMapLayerStyle,QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsFeatureRequest, QgsSettings, QgsSingleSymbolRenderer
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtXml import QDomDocument

from qgis.PyQt.QtWidgets import QMessageBox,QInputDialog, QFileDialog

from .stratigraphic_order import PERIOD_FIELDS, norm, order_clauses, period_case, period_start, period_starts

# Field labels translations
FIELD_LABELS = {
    'd_stratigrafica': {
        'it': 'Definizione Stratigrafica',
        'en': 'Stratigraphic Definition',
        'de': 'Stratigraphische Definition',
        'es': 'Definición Estratigráfica',
        'fr': 'Définition Stratigraphique',
        'ar': 'التعريف الطبقي'
    },
    'tipo_us_s': {
        'it': 'Tipo US',
        'en': 'SU Type',
        'de': 'SE Typ',
        'es': 'Tipo UE',
        'fr': 'Type US',
        'ar': 'نوع الوحدة'
    },
    'd_interpretativa': {
        'it': 'Definizione Interpretativa',
        'en': 'Interpretive Definition',
        'de': 'Interpretative Definition',
        'es': 'Definición Interpretativa',
        'fr': 'Définition Interprétative',
        'ar': 'التعريف التفسيري'
    },
    'cont_per': {
        'it': 'Periodo/Fase (cont_per)',
        'en': 'Period/Phase (cont_per)',
        'de': 'Periode/Phase (cont_per)',
        'es': 'Período/Fase (cont_per)',
        'fr': 'Période/Phase (cont_per)',
        'ar': 'الفترة/المرحلة (cont_per)'
    }
}

# "Carica stile esistente": where the template style comes from
STYLE_SOURCE_LABELS = {
    'title': {'it': 'Stile esistente', 'en': 'Existing style'},
    'prompt': {'it': 'Scegli lo stile da usare come modello:', 'en': 'Choose the style to use as a template:'},
    'db': {'it': 'Database', 'en': 'Database'},
    'other': {'it': 'Altro file QML…', 'en': 'Other QML file…'},
}

DIALOG_LABELS = {
    'title': {
        'it': 'Selezione Campo per Categorizzazione',
        'en': 'Select Categorization Field',
        'de': 'Kategorisierungsfeld auswählen',
        'es': 'Seleccionar Campo de Categorización',
        'fr': 'Sélectionner le Champ de Catégorisation',
        'ar': 'اختر حقل التصنيف'
    },
    'prompt': {
        'it': 'Scegli il campo da usare per lo stile:',
        'en': 'Choose the field to use for styling:',
        'de': 'Wählen Sie das Feld für den Stil:',
        'es': 'Elige el campo a usar para el estilo:',
        'fr': 'Choisissez le champ à utiliser pour le style:',
        'ar': 'اختر الحقل المراد استخدامه للتنسيق:'
    }
}


from sqlalchemy import create_engine, text


def _plain(value):
    """Attribute value as plain Python (QGIS 3 gives NULL as a null QVariant)."""
    try:
        if value.isNull():
            return None
    except AttributeError:
        pass
    return value


def _value_colour(value):
    """Colour of a category value, the same in every session (Python's
    hash() of a string changes at every start of QGIS)."""
    digest = hashlib.md5(str(value).encode('utf-8')).digest()
    return QColor(digest[0], digest[1], digest[2])


def _no_geometry():
    try:
        from qgis.core import Qgis
        return Qgis.FeatureRequestFlag.NoGeometry
    except AttributeError:
        return QgsFeatureRequest.NoGeometry


def apply_stratigraphic_order(layer, periodization=None, override=True):
    """Drawing order of a US/USM layer, like the Time Manager: undated
    units first, then periods by chronology (``periodization``: rows
    (sito, periodo, fase, cron_iniziale, cont_per) of periodizzazione_table),
    order_layer, stratigraph_index_us — the most recent end up on top (see
    modules/utility/stratigraphic_order.py). The order is set on the
    renderer: QgsVectorLayer has no setOrderBy(). With override=False an
    order already on the renderer is kept. Returns True when set."""
    renderer = layer.renderer() if layer is not None else None
    if renderer is None or (not override and renderer.orderByEnabled()):
        return False
    names = layer.fields().names()
    expression = None
    fields = [f for f in PERIOD_FIELDS if f in names]
    if periodization and ('periodo_iniziale' in fields or 'cont_per' in fields):
        starts = period_starts(periodization)
        combos = {}
        request = QgsFeatureRequest().setFlags(_no_geometry()).setSubsetOfAttributes(fields, layer.fields())
        for feature in layer.getFeatures(request):
            combos.setdefault(tuple(_plain(feature[f]) for f in fields), None)

        def value(values, field):
            return values[fields.index(field)] if field in fields else None

        expression = period_case([
            (dict(zip(fields, values)),
             period_start(starts, value(values, 'sito'), value(values, 'periodo_iniziale'),
                          value(values, 'fase_iniziale'), value(values, 'cont_per')))
            for values in combos])
    clauses = order_clauses(names, expression)
    if not clauses:
        return False
    renderer.setOrderBy(QgsFeatureRequest.OrderBy(
        [QgsFeatureRequest.OrderByClause(e, ascending, nulls_first) for e, ascending, nulls_first in clauses]))
    renderer.setOrderByEnabled(True)
    layer.triggerRepaint()
    return True


def _is_fill(symbol):
    return isinstance(symbol, QgsFillSymbol)


def _template_symbols(renderer):
    """Fill symbols of a template style by category value. Cloned at once:
    categories() and legendSymbolItems() return temporary copies whose
    symbols are deleted with them."""
    found = {}
    if isinstance(renderer, QgsCategorizedSymbolRenderer):
        for category in renderer.categories():
            if _is_fill(category.symbol()):
                found.setdefault(str(category.value()), category.symbol().clone())
    elif isinstance(renderer, QgsRuleBasedRenderer):
        for rule in renderer.rootRule().descendants():
            if not _is_fill(rule.symbol()):
                continue
            m = re.search(r"=\s*'((?:[^']|'')*)'", rule.filterExpression() or '')
            found.setdefault(m.group(1).replace("''", "'") if m else rule.label(), rule.symbol().clone())
    return found


def _template_symbol(renderer):
    """The fill symbol (a copy) of a template style the new categories
    start from."""
    if renderer is None:
        return None
    if isinstance(renderer, QgsSingleSymbolRenderer):
        return renderer.symbol().clone() if _is_fill(renderer.symbol()) else None
    if isinstance(renderer, QgsCategorizedSymbolRenderer) and _is_fill(renderer.sourceSymbol()):
        return renderer.sourceSymbol().clone()
    try:
        for item in renderer.legendSymbolItems():
            if _is_fill(item.symbol()):
                return item.symbol().clone()
    except Exception:
        pass
    return None


_STYLE_DIRS = (('gis', 'styles_spatialite'), ('gis', 'styles'), ('utility', 'styles_spatialite'), ('utility', 'styles'))


def _shipped_us_styles():
    """QML files shipped with pyArchInit for the US/USM layers."""
    modules_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    found, seen = [], set()
    for sub_dir in _STYLE_DIRS:
        folder = os.path.join(modules_dir, *sub_dir)
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            continue
        for name in names:
            low = name.lower()
            if low.endswith('.qml') and low.startswith(('us_', 'usm')) and low not in seen:
                seen.add(low)
                found.append(os.path.join(folder, name))
    return found


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
    def __init__(self, connection, sito=None):
        self.connection = connection
        self.sito = sito
        self.engine = create_engine(self.connection.conn_str())
        self.DB_SERVER = "sqlite" if self.connection.conn_str().startswith('sqlite') else "postgres"
        self.us_data = self._load_us_data()
        self.us_styles = self._create_styles_for_us()
        self.periodization = self._load_periodization()
        # (choice, template, category field): asked once, reused for the
        # other layers styled by this styler (per-period loads)
        self._decision = None

    def _load_us_data(self):
        if self.sito:
            query = text("SELECT DISTINCT d_stratigrafica, unita_tipo AS tipo_us_s, order_layer AS stratigraph_index_us, d_interpretativa FROM us_table WHERE sito = :sito")
            params = {"sito": self.sito}
        else:
            query = text("SELECT DISTINCT d_stratigrafica, unita_tipo AS tipo_us_s, order_layer AS stratigraph_index_us, d_interpretativa FROM us_table")
            params = {}
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                return [row._asdict() if hasattr(row, '_asdict') else dict(zip(result.keys(), row)) for row in result]
        except Exception:
            return []

    def _load_periodization(self):
        """periodizzazione_table rows (sito, periodo, fase, cron_iniziale,
        cont_per, datazione_estesa) of the site (all sites when None)."""
        sql = ("SELECT sito, periodo, fase, cron_iniziale, cont_per, datazione_estesa "
               "FROM periodizzazione_table" + (" WHERE sito = :sito" if self.sito else ""))
        try:
            with self.engine.connect() as conn:
                return [tuple(row) for row in conn.execute(text(sql), {"sito": self.sito} if self.sito else {})]
        except Exception:
            return []

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

        L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if L == 'it':
            msg_box.setText("Come vuoi gestire lo stile del layer?")
            msg_box.setWindowTitle("Scelta Stile")
            save_label = "Salva nuovo stile"
            load_label = "Carica stile esistente"
            temp_label = "Usa stile temporaneo"
            null_label = "Simbolo singolo (solo contorno)"
        else:
            msg_box.setText("How do you want to manage the layer style?")
            msg_box.setWindowTitle("Style Choice")
            save_label = "Save new style"
            load_label = "Load existing style"
            temp_label = "Use temporary style"
            null_label = "Single symbol (outline only)"

        save_button = msg_box.addButton(save_label, QMessageBox.ActionRole)
        load_button = msg_box.addButton(load_label, QMessageBox.ActionRole)
        temp_button = msg_box.addButton(temp_label, QMessageBox.ActionRole)
        null_button = msg_box.addButton(null_label, QMessageBox.ActionRole)

        msg_box.exec()

        if msg_box.clickedButton() == save_button:
            return "save"
        elif msg_box.clickedButton() == load_button:
            return "load"
        elif msg_box.clickedButton() == null_button:
            return "null_fill"
        else:
            return "temp"

    def ask_user_categorization_field(self, layer=None):
        """
        Ask user which field to use for rule-based categorization.
        Only shows fields that are available in the layer.
        Uses localized labels based on QGIS language settings.

        Args:
            layer: Optional QgsVectorLayer to check for available fields

        Returns the selected field name or default if cancelled.
        """
        # Get current language
        lang = QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        # Available field names
        available_fields = ['d_stratigrafica', 'tipo_us_s', 'd_interpretativa', 'cont_per']

        # Filter to only fields present in the layer
        if layer is not None:
            layer_fields = layer.fields().names()
            available_fields = [f for f in available_fields if f in layer_fields]

        if not available_fields:
            print("Nessun campo di categorizzazione disponibile")
            return "d_stratigrafica"

        # Build field options with localized labels
        field_options = {}
        for field_name in available_fields:
            # Get localized label, fallback to English, then to field name
            label = FIELD_LABELS.get(field_name, {}).get(lang)
            if not label:
                label = FIELD_LABELS.get(field_name, {}).get('en', field_name)
            field_options[label] = field_name

        # If only one option available, use it directly
        if len(field_options) == 1:
            selected = list(field_options.values())[0]
            print(f"Unico campo disponibile: {selected}")
            return selected

        # Get localized dialog labels
        dialog_title = DIALOG_LABELS['title'].get(lang, DIALOG_LABELS['title']['en'])
        dialog_prompt = DIALOG_LABELS['prompt'].get(lang, DIALOG_LABELS['prompt']['en'])

        field_label, ok = QInputDialog.getItem(
            None,
            dialog_title,
            dialog_prompt,
            list(field_options.keys()),
            0,
            False
        )

        if ok and field_label:
            return field_options[field_label]
        else:
            # Default to first available field if cancelled
            return list(field_options.values())[0]

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

    def load_style_from_db_new(self, layer):
        try:
            styles = layer.listStylesInDatabase()

            # Verifica se ci sono stili nel database
            if not styles or len(styles) < 2 or not styles[1]:
                print("Nessuno stile trovato nel database.")
                return None

            style_ids = styles[1]
            style_names = styles[2] if len(styles) > 2 else style_ids

            if len(style_ids) == 1:
                # Se c'è solo uno stile, caricalo direttamente
                style_id = style_ids[0]
                style_data = layer.getStyleFromDatabase(style_id)
                if style_data:
                    style_xml = style_data[0]
                    print(f"Caricato stile unico: {style_names[0]}")
                    return style_xml
                else:
                    print("Errore nel caricamento dello stile unico.")
                    return None
            else:
                # Se ci sono più stili, chiedi all'utente quale caricare
                style_name, ok = QInputDialog.getItem(None, "Seleziona Stile",
                                                      "Scegli lo stile da caricare:",
                                                      style_names, 0, False)
                if ok and style_name:
                    index = style_names.index(style_name)
                    if 0 <= index < len(style_ids):
                        style_id = style_ids[index]
                        style_data = layer.getStyleFromDatabase(style_id)
                        if style_data:
                            style_xml = style_data[0]
                            print(f"Caricato stile selezionato: {style_name}")
                            return style_xml
                        else:
                            print(f"Errore nel caricamento dello stile: {style_name}")
                            return None
                    else:
                        self.show_message("Indice dello stile non valido.")
                        return None
                else:
                    print("Selezione dello stile annullata.")
                    return None

        except Exception as e:
            print(f"Errore nel caricamento degli stili: {str(e)}")
            return None

    def choose_existing_style(self, layer):
        """Style to use as template: saved in the database, shipped with
        pyArchInit or any .qml file. Returns ('db', xml) / ('file', path),
        or None when cancelled."""
        lang = QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        def label(key):
            return STYLE_SOURCE_LABELS[key].get(lang, STYLE_SOURCE_LABELS[key]['en'])

        choices = {}
        try:
            styles = layer.listStylesInDatabase()
            if styles and len(styles) > 2:
                for style_id, name in zip(styles[1], styles[2]):
                    choices["%s: %s" % (label('db'), name)] = ('db', style_id)
        except Exception:
            pass
        for path in _shipped_us_styles():
            choices["pyArchInit: %s" % os.path.basename(path)] = ('file', path)
        other = label('other')
        item, ok = QInputDialog.getItem(None, label('title'), label('prompt'), list(choices) + [other], 0, False)
        if not ok or not item:
            return None
        if item == other:
            path, _ = QFileDialog.getOpenFileName(None, label('title'), os.path.expanduser('~'), "QGIS (*.qml)")
            return ('file', path) if path else None
        kind, value = choices[item]
        if kind == 'db':
            try:
                xml = layer.getStyleFromDatabase(value)
                xml = xml[0] if isinstance(xml, tuple) else xml
                return ('db', xml) if xml else None
            except Exception as e:
                print(f"Stile non letto dal database: {e}")
                return None
        return ('file', value)

    @staticmethod
    def _load_template(layer, template):
        """Load the chosen style into the layer (labels, opacity and blending
        come with it) and return a copy of its renderer, or None."""
        kind, value = template
        try:
            if kind == 'file':
                result = layer.loadNamedStyle(value)
                ok = result[1] if isinstance(result, tuple) else bool(result)
            else:
                doc = QDomDocument()
                doc.setContent(value)
                result = layer.importNamedStyle(doc)
                ok = result[0] if isinstance(result, tuple) else bool(result)
        except Exception as e:
            print(f"Stile non caricato: {e}")
            return None
        if not ok:
            print(f"Stile non caricato: {value if kind == 'file' else 'database'}")
            return None
        return layer.renderer().clone() if layer.renderer() else None

    def apply_style_to_layer(self, layer, choice=None):
        """Style chosen by the user — save a new one / an existing one as
        template / temporary / outline only — categorised on the chosen
        field, then the drawing order of the Time Manager. The choice is
        asked once per styler and reused for the next layers (the per-period
        loaders pass ``choice`` when they already asked it)."""
        if not layer.isValid():
            print("Layer non valido")
            return

        fields = layer.fields()
        # Base required fields for styling
        required_fields = ['stratigraph_index_us', 'tipo_us_s']
        # Optional categorization fields (at least one should be present)
        categorization_fields = ['d_stratigrafica', 'tipo_us_s', 'd_interpretativa', 'cont_per']

        if not all(field in fields.names() for field in required_fields):
            print(f"Campi mancanti nel layer. Richiesti: {', '.join(required_fields)}")
            return
        if not any(field in fields.names() for field in categorization_fields):
            print(f"Nessun campo di categorizzazione disponibile. Richiesto almeno uno tra: {', '.join(categorization_fields)}")
            return

        first = self._decision is None
        if first:
            choice = choice or self.ask_user_style_preference()
            template = self.choose_existing_style(layer) if choice == "load" else None
            category_field = None if choice == "null_fill" else self.ask_user_categorization_field(layer)
            self._decision = (choice, template, category_field)
        choice, template, category_field = self._decision

        if choice == "null_fill":
            try:
                symbol = QgsFillSymbol.createSimple({
                    'color': '0,0,0,0',  # transparent fill
                    'outline_color': '50,50,50,255',  # dark grey outline
                    'outline_width': '0.3',
                    'outline_style': 'solid'
                })
                layer.setRenderer(QgsSingleSymbolRenderer(symbol))
            except Exception as e:
                print(f"Error applying null fill: {e}")
        else:
            template_renderer = self._load_template(layer, template) if template else None
            print(f"Stile sul campo {category_field}" + (" con uno stile esistente come modello" if template_renderer else ""))
            self._apply_temp_style(layer, category_field, template_renderer)

        # Drawing order: most recent units on top, like the Time Manager
        self._apply_feature_ordering(layer)

        if choice == "save" and first:
            self.save_style_to_db(layer)

        layer.triggerRepaint()
        layer.legendChanged.emit()

    def _category_label(self, field, value):
        """Legend label of a category; cont_per codes also show their dating."""
        if field != 'cont_per' or value in (None, '', 'non specificato'):
            return f"{value}"
        dating = {norm(row[4]): row[5] for row in self.periodization if len(row) > 5 and row[5]}
        parts = [dating.get(norm(code)) for code in str(value).split('/')]
        parts = [p for p in parts if p]
        return f"{value} – {' / '.join(parts)}" if parts else f"{value}"

    def _apply_feature_ordering(self, layer):
        """Drawing order like the Time Manager: undated units first, periods
        by chronology, order_layer (0 = oldest), stratigraph_index_us (the
        cut over its fill). It lives on the renderer."""
        try:
            if apply_stratigraphic_order(layer, [row[:5] for row in self.periodization]):
                print("Ordinamento come il Time Manager: periodo, order_layer, stratigraph_index_us")
        except Exception as e:
            print(f"Errore nell'applicazione dell'ordinamento: {str(e)}")

    def _apply_temp_style(self, layer, category_field="d_stratigrafica", template=None):
        """
        Rule-based style: one rule per value of category_field and
        stratigraph_index_us, legend sorted by order_layer.

        Args:
            layer: The QgsVectorLayer to style
            category_field: d_stratigrafica, tipo_us_s, d_interpretativa or cont_per
            template: renderer of an existing style — the values it already
                has keep its symbol, the others get a copy of its symbol with
                their own colour
        """
        root_rule = QgsRuleBasedRenderer.Rule(None)
        all_rules = []

        field_idx = layer.fields().indexOf(category_field)
        if field_idx == -1:
            print(f"Campo '{category_field}' non trovato nel layer")
            return

        known = _template_symbols(template)
        base = _template_symbol(template)
        has_order_layer = 'order_layer' in layer.fields().names()

        # Unique combinations of category value, stratigraph_index_us and
        # tipo_us_s, with their minimum order_layer (legend order)
        unique_combinations = {}
        for feature in layer.getFeatures():
            cat_value = _plain(feature[category_field]) or "non specificato"
            strat_idx = _plain(feature['stratigraph_index_us']) or 1
            tipo_us = _plain(feature['tipo_us_s']) or "non specificato"
            order_layer = _plain(feature['order_layer']) if has_order_layer else 0
            if order_layer is None:
                order_layer = 9999  # Put NULL order_layer at the end
            key = (cat_value, strat_idx, tipo_us)
            unique_combinations[key] = min(unique_combinations.get(key, order_layer), order_layer)

        for (cat_value, stratigraph_index_us, tipo_us_s), min_order_layer in unique_combinations.items():
            if cat_value == "non specificato":
                expression = f"(\"{category_field}\" IS NULL OR \"{category_field}\" = '') AND \"stratigraph_index_us\" = {stratigraph_index_us}"
            else:
                escaped_value = str(cat_value).replace("'", "''")
                expression = f"\"{category_field}\" = '{escaped_value}' AND \"stratigraph_index_us\" = {stratigraph_index_us}"

            if str(cat_value) in known:
                symbol = known[str(cat_value)].clone()        # colour of the existing style
            elif base is not None:
                symbol = base.clone()                         # existing style as template
                symbol.setColor(_value_colour(cat_value))
            else:
                symbol = QgsFillSymbol.createSimple({})
                symbol.setColor(_value_colour(cat_value))
                symbol.setOpacity(random.uniform(0.5, 1.0))
                if str(tipo_us_s).lower() == "negativa":
                    symbol.symbolLayer(0).setStrokeStyle(Qt.PenStyle.DotLine)
                elif str(tipo_us_s).lower() == "non specificato":
                    symbol.symbolLayer(0).setStrokeStyle(Qt.PenStyle.DashLine)
                else:
                    symbol.symbolLayer(0).setStrokeStyle(Qt.PenStyle.SolidLine)
                symbol.symbolLayer(0).setStrokeColor(QColor(0, 0, 0))
                symbol.symbolLayer(0).setStrokeWidth(0.5)
            if stratigraph_index_us != 1:
                # White for stratigraph_index_us = 2
                symbol.setColor(QColor(255, 255, 255))
                symbol.setOpacity(1.0)

            rule = QgsRuleBasedRenderer.Rule(symbol, 0, 0, expression, self._category_label(category_field, cat_value))
            all_rules.append((min_order_layer, stratigraph_index_us, rule))

        # Legend: order_layer ASC, then stratigraph_index_us ASC
        all_rules.sort(key=lambda x: (x[0], x[1]))
        for _, _, rule in all_rules:
            root_rule.appendChild(rule)

        layer.setRenderer(QgsRuleBasedRenderer(root_rule))
        print(f"Stile applicato con {len(root_rule.children())} regole (campo: {category_field})")

    def show_message(self, message):
        """Mostra un messaggio all'utente."""
        QMessageBox.information(None, 'Informazione', message, QMessageBox.Ok)

    def _apply_temp_style_old(self, layer):
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

                label = f"{d_stratigrafica}"
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
                    #self.show_message(f"Risultato del salvataggio: {result}")
                except Exception as e:
                    self.show_message(f"Eccezione durante il salvataggio: {str(e)}")

                    return

                if result is None:
                    #self.show_message("Il salvataggio dello stile ha restituito None")
                    #self.show_message(f"Tipo di layer: {layer.type()}")
                    #self.show_message(
                        #f"Provider: {layer.dataProvider().name() if layer.dataProvider() else 'Nessun provider'}")
                    print(f"Fonte dei dati: {layer.source()}")
                else:
                    print(f"Stile '{style_name}' salvato nel database. Risultato: {result}")
            else:
                self.show_message("Salvataggio dello stile annullato")
        except Exception as e:
            self.show_message(f"Errore nel salvataggio dello stile: {str(e)}")


    def get_all_styles(self):
        return self.us_styles