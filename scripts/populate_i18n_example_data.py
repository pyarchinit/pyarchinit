#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate the template SQLite DB with i18n example data for all 10 languages.

Reads the existing Italian data from site_table, periodizzazione_table, and
us_table, then inserts translated copies for 9 additional languages.

Usage:
    python scripts/populate_i18n_example_data.py
"""

import ast
import os
import sqlite3
import sys
import uuid

# ---------------------------------------------------------------------------
# Path to the template database
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PLUGIN_DIR, 'resources', 'dbfiles', 'pyarchinit_db.sqlite')

# Add plugin dir so we can import the i18n module
sys.path.insert(0, PLUGIN_DIR)
from modules.utility.pyarchinit_i18n_stratigraphic import (
    RELATIONSHIPS, UNIT_TYPE_ABBREV,
)

# Source site (Italian)
IT_SITE = 'Scavo archeologico'
LANGS = ['en', 'de', 'es', 'fr', 'ar', 'ca', 'ro', 'pt', 'el']

# ---------------------------------------------------------------------------
# Site names and metadata per language
# ---------------------------------------------------------------------------
SITE_NAMES = {
    'en': 'Archaeological Excavation',
    'de': 'Archäologische Ausgrabung',
    'es': 'Excavación Arqueológica',
    'fr': 'Fouille Archéologique',
    'ar': 'تنقيب أثري',
    'ca': 'Excavació Arqueològica',
    'ro': 'Săpătură Arheologică',
    'pt': 'Escavação Arqueológica',
    'el': 'Αρχαιολογική Ανασκαφή',
}

NAZIONE = {
    'en': 'Italy', 'de': 'Italien', 'es': 'Italia', 'fr': 'Italie',
    'ar': 'إيطاليا', 'ca': 'Itàlia', 'ro': 'Italia', 'pt': 'Itália',
    'el': 'Ιταλία',
}

DEFINIZIONE_SITO = {
    'en': 'Stratigraphic excavation', 'de': 'Stratigraphische Grabung',
    'es': 'Excavación estratigráfica', 'fr': 'Fouille stratigraphique',
    'ar': 'تنقيب طبقي', 'ca': 'Excavació estratigràfica',
    'ro': 'Săpătură stratigrafică', 'pt': 'Escavação estratigráfica',
    'el': 'Στρωματογραφική ανασκαφή',
}

SITE_DESCRIZIONE = {
    'en': 'Stratigraphic excavation (March-April 2021), maximum depth -2.20 metres, positive result: frequentation of 13th-14th c., buildings of 14th-16th c.',
    'de': 'Stratigraphische Grabung (März-April 2021), maximale Tiefe -2,20 m, positives Ergebnis: Besiedlung 13.-14. Jh., Gebäude 14.-16. Jh.',
    'es': 'Excavación estratigráfica (marzo-abril 2021), profundidad máxima -2,20 m, resultado positivo: frecuentación s. XIII-XIV, edificios s. XIV-XVI.',
    'fr': 'Fouille stratigraphique (mars-avril 2021), profondeur max. -2,20 m, résultat positif : fréquentation XIIIe-XIVe s., bâtiments XIVe-XVIe s.',
    'ar': 'تنقيب طبقي (مارس-أبريل 2021)، عمق أقصى -2.20 متر، نتيجة إيجابية: استيطان القرن 13-14، مبانٍ القرن 14-16.',
    'ca': 'Excavació estratigràfica (març-abril 2021), profunditat màxima -2,20 m, resultat positiu: freqüentació s. XIII-XIV, edificis s. XIV-XVI.',
    'ro': 'Săpătură stratigrafică (martie-aprilie 2021), adâncime maximă -2,20 m, rezultat pozitiv: frecventare sec. XIII-XIV, edificii sec. XIV-XVI.',
    'pt': 'Escavação estratigráfica (março-abril 2021), profundidade máxima -2,20 m, resultado positivo: frequentação séc. XIII-XIV, edifícios séc. XIV-XVI.',
    'el': 'Στρωματογραφική ανασκαφή (Μάρτιος-Απρίλιος 2021), μέγιστο βάθος -2,20 μ., θετικό αποτέλεσμα: χρήση 13ου-14ου αι., κτίρια 14ου-16ου αι.',
}

# ---------------------------------------------------------------------------
# Relationship term mapping  IT → target language
# ---------------------------------------------------------------------------
# Build a mapping from each Italian term to its index, then translate
IT_RELS = RELATIONSHIPS['it']
_REL_INDEX = {term: i for i, term in enumerate(IT_RELS)}


def translate_rel_term(term, lang):
    """Translate an Italian relationship term to the target language."""
    idx = _REL_INDEX.get(term)
    if idx is not None:
        return RELATIONSHIPS[lang][idx]
    # Symbol operators or unknown terms: keep as-is
    return term


# ---------------------------------------------------------------------------
# Unit type mapping
# ---------------------------------------------------------------------------
IT_US, IT_USM = UNIT_TYPE_ABBREV['it']  # 'US', 'USM'


def translate_unit_type(ut, lang):
    """Translate unit type abbreviation (only US/USM change)."""
    target_us, target_usm = UNIT_TYPE_ABBREV[lang]
    if ut == IT_US:
        return target_us
    if ut == IT_USM:
        return target_usm
    return ut  # USVA, USVB, CON, SF, DOC, Extractor, property, Combinar


# ---------------------------------------------------------------------------
# Short field translations (d_stratigrafica, d_interpretativa, etc.)
# ---------------------------------------------------------------------------

# d_stratigrafica values
D_STRATIGRAFICA = {
    'Strato di macerie': {
        'en': 'Rubble layer', 'de': 'Trümmerschicht', 'es': 'Estrato de escombros',
        'fr': 'Couche de décombres', 'ar': 'طبقة أنقاض', 'ca': 'Estrat de runes',
        'ro': 'Strat de moloz', 'pt': 'Camada de entulho', 'el': 'Στρώμα ερειπίων',
    },
    'Strato di terra': {
        'en': 'Earth layer', 'de': 'Erdschicht', 'es': 'Estrato de tierra',
        'fr': 'Couche de terre', 'ar': 'طبقة تراب', 'ca': 'Estrat de terra',
        'ro': 'Strat de pământ', 'pt': 'Camada de terra', 'el': 'Στρώμα χώματος',
    },
    'Strato di sabbia e terra': {
        'en': 'Sand and earth layer', 'de': 'Sand- und Erdschicht',
        'es': 'Estrato de arena y tierra', 'fr': 'Couche de sable et terre',
        'ar': 'طبقة رمل وتراب', 'ca': 'Estrat de sorra i terra',
        'ro': 'Strat de nisip și pământ', 'pt': 'Camada de areia e terra',
        'el': 'Στρώμα άμμου και χώματος',
    },
    'Struttura in muratura': {
        'en': 'Masonry structure', 'de': 'Mauerwerksstruktur',
        'es': 'Estructura de mampostería', 'fr': 'Structure en maçonnerie',
        'ar': 'بنية بناء', 'ca': 'Estructura de maçoneria',
        'ro': 'Structură din zidărie', 'pt': 'Estrutura em alvenaria',
        'el': 'Κατασκευή τοιχοποιίας',
    },
    'Taglio': {
        'en': 'Cut', 'de': 'Schnitt', 'es': 'Corte', 'fr': 'Coupe',
        'ar': 'قطع', 'ca': 'Tall', 'ro': 'Tăietură', 'pt': 'Corte',
        'el': 'Τομή',
    },
    'Riempimento': {
        'en': 'Fill', 'de': 'Verfüllung', 'es': 'Relleno', 'fr': 'Remplissage',
        'ar': 'ملء', 'ca': 'Rebliment', 'ro': 'Umplutură', 'pt': 'Enchimento',
        'el': 'Επίχωση',
    },
    'Strato di malta': {
        'en': 'Mortar layer', 'de': 'Mörtelschicht', 'es': 'Estrato de mortero',
        'fr': 'Couche de mortier', 'ar': 'طبقة ملاط', 'ca': 'Estrat de morter',
        'ro': 'Strat de mortar', 'pt': 'Camada de argamassa', 'el': 'Στρώμα κονιάματος',
    },
    'Strato di terra e carboni': {
        'en': 'Earth and charcoal layer', 'de': 'Erd- und Kohleschicht',
        'es': 'Estrato de tierra y carbones', 'fr': 'Couche de terre et charbons',
        'ar': 'طبقة تراب وفحم', 'ca': 'Estrat de terra i carbons',
        'ro': 'Strat de pământ și cărbuni', 'pt': 'Camada de terra e carvões',
        'el': 'Στρώμα χώματος και κάρβουνων',
    },
    'Strato di sabbia e argilla': {
        'en': 'Sand and clay layer', 'de': 'Sand- und Tonschicht',
        'es': 'Estrato de arena y arcilla', 'fr': 'Couche de sable et argile',
        'ar': 'طبقة رمل وطين', 'ca': 'Estrat de sorra i argila',
        'ro': 'Strat de nisip și argilă', 'pt': 'Camada de areia e argila',
        'el': 'Στρώμα άμμου και αργίλου',
    },
    'Strato di carbone e cenere': {
        'en': 'Charcoal and ash layer', 'de': 'Kohle- und Ascheschicht',
        'es': 'Estrato de carbón y ceniza', 'fr': 'Couche de charbon et cendre',
        'ar': 'طبقة فحم ورماد', 'ca': 'Estrat de carbó i cendra',
        'ro': 'Strat de cărbune și cenușă', 'pt': 'Camada de carvão e cinza',
        'el': 'Στρώμα κάρβουνου και στάχτης',
    },
    'Strato di sabbia': {
        'en': 'Sand layer', 'de': 'Sandschicht', 'es': 'Estrato de arena',
        'fr': 'Couche de sable', 'ar': 'طبقة رمل', 'ca': 'Estrat de sorra',
        'ro': 'Strat de nisip', 'pt': 'Camada de areia', 'el': 'Στρώμα άμμου',
    },
    'Strato di legno carbonizzato': {
        'en': 'Charred wood layer', 'de': 'Verkohlte Holzschicht',
        'es': 'Estrato de madera carbonizada', 'fr': 'Couche de bois carbonisé',
        'ar': 'طبقة خشب متفحم', 'ca': 'Estrat de fusta carbonitzada',
        'ro': 'Strat de lemn carbonizat', 'pt': 'Camada de madeira carbonizada',
        'el': 'Στρώμα απανθρακωμένου ξύλου',
    },
    'Strato di malta e ciottoli': {
        'en': 'Mortar and pebble layer', 'de': 'Mörtel- und Kieselschicht',
        'es': 'Estrato de mortero y guijarros', 'fr': 'Couche de mortier et galets',
        'ar': 'طبقة ملاط وحصى', 'ca': 'Estrat de morter i còdols',
        'ro': 'Strat de mortar și pietriș', 'pt': 'Camada de argamassa e seixos',
        'el': 'Στρώμα κονιάματος και βοτσάλων',
    },
    'Strato di sabbia concotta': {
        'en': 'Fired sand layer', 'de': 'Gebrannte Sandschicht',
        'es': 'Estrato de arena cocida', 'fr': 'Couche de sable cuit',
        'ar': 'طبقة رمل محروق', 'ca': 'Estrat de sorra cuita',
        'ro': 'Strat de nisip ars', 'pt': 'Camada de areia cozida',
        'el': 'Στρώμα ψημένης άμμου',
    },
    'Strato di sabbia e argilla': {
        'en': 'Sand and clay layer', 'de': 'Sand- und Tonschicht',
        'es': 'Estrato de arena y arcilla', 'fr': 'Couche de sable et argile',
        'ar': 'طبقة رمل وطين', 'ca': 'Estrat de sorra i argila',
        'ro': 'Strat de nisip și argilă', 'pt': 'Camada de areia e argila',
        'el': 'Στρώμα άμμου και αργίλου',
    },
    'Continuity': {
        'en': 'Continuity', 'de': 'Kontinuität', 'es': 'Continuidad',
        'fr': 'Continuité', 'ar': 'استمرارية', 'ca': 'Continuïtat',
        'ro': 'Continuitate', 'pt': 'Continuidade', 'el': 'Συνέχεια',
    },
}

# d_interpretativa values
D_INTERPRETATIVA = {
    'Fondazione in muratura': {
        'en': 'Masonry foundation', 'de': 'Mauerwerksfundament',
        'es': 'Cimentación de mampostería', 'fr': 'Fondation en maçonnerie',
        'ar': 'أساس بناء', 'ca': 'Fonamentació de maçoneria',
        'ro': 'Fundație din zidărie', 'pt': 'Fundação em alvenaria',
        'el': 'Θεμελίωση τοιχοποιίας',
    },
    'Livellamento': {
        'en': 'Levelling', 'de': 'Planierung', 'es': 'Nivelación',
        'fr': 'Nivellement', 'ar': 'تسوية', 'ca': 'Anivellament',
        'ro': 'Nivelare', 'pt': 'Nivelamento', 'el': 'Ισοπέδωση',
    },
    'Abbandono': {
        'en': 'Abandonment', 'de': 'Aufgabe', 'es': 'Abandono',
        'fr': 'Abandon', 'ar': 'هجر', 'ca': 'Abandonament',
        'ro': 'Abandon', 'pt': 'Abandono', 'el': 'Εγκατάλειψη',
    },
    'Pavimentazione in terra': {
        'en': 'Earth floor', 'de': 'Erdboden', 'es': 'Pavimento de tierra',
        'fr': 'Sol en terre', 'ar': 'أرضية ترابية', 'ca': 'Paviment de terra',
        'ro': 'Pardoseală din pământ', 'pt': 'Pavimento de terra',
        'el': 'Δάπεδο χωμάτινο',
    },
    'Focolare': {
        'en': 'Hearth', 'de': 'Feuerstelle', 'es': 'Hogar',
        'fr': 'Foyer', 'ar': 'موقد', 'ca': 'Llar de foc',
        'ro': 'Vatră', 'pt': 'Lareira', 'el': 'Εστία',
    },
    'Muro': {
        'en': 'Wall', 'de': 'Mauer', 'es': 'Muro',
        'fr': 'Mur', 'ar': 'جدار', 'ca': 'Mur',
        'ro': 'Zid', 'pt': 'Muro', 'el': 'Τοίχος',
    },
    'Buca': {
        'en': 'Pit', 'de': 'Grube', 'es': 'Fosa',
        'fr': 'Fosse', 'ar': 'حفرة', 'ca': 'Fossa',
        'ro': 'Groapă', 'pt': 'Fossa', 'el': 'Λάκκος',
    },
    'Palo': {
        'en': 'Post', 'de': 'Pfahl', 'es': 'Poste',
        'fr': 'Poteau', 'ar': 'عمود', 'ca': 'Pal',
        'ro': 'Stâlp', 'pt': 'Poste', 'el': 'Πάσσαλος',
    },
    'Punto di fuoco': {
        'en': 'Fire point', 'de': 'Feuerstelle', 'es': 'Punto de fuego',
        'fr': 'Point de feu', 'ar': 'نقطة نار', 'ca': 'Punt de foc',
        'ro': 'Punct de foc', 'pt': 'Ponto de fogo', 'el': 'Σημείο φωτιάς',
    },
    'Disfacimento': {
        'en': 'Decay', 'de': 'Zerfall', 'es': 'Descomposición',
        'fr': 'Dégradation', 'ar': 'تآكل', 'ca': 'Degradació',
        'ro': 'Degradare', 'pt': 'Degradação', 'el': 'Αποσάθρωση',
    },
    'Battuto': {
        'en': 'Beaten floor', 'de': 'Stampfboden', 'es': 'Suelo apisonado',
        'fr': 'Sol battu', 'ar': 'أرضية مدكوكة', 'ca': 'Sòl piconat',
        'ro': 'Pardoseală bătătorită', 'pt': 'Piso batido', 'el': 'Πατημένο δάπεδο',
    },
    'Preparazione': {
        'en': 'Preparation', 'de': 'Vorbereitung', 'es': 'Preparación',
        'fr': 'Préparation', 'ar': 'تحضير', 'ca': 'Preparació',
        'ro': 'Pregătire', 'pt': 'Preparação', 'el': 'Προετοιμασία',
    },
    'Pilastro': {
        'en': 'Pillar', 'de': 'Pfeiler', 'es': 'Pilar',
        'fr': 'Pilier', 'ar': 'عمود', 'ca': 'Pilar',
        'ro': 'Pilon', 'pt': 'Pilar', 'el': 'Πεσσός',
    },
    'Fossa di spoliazione': {
        'en': 'Robber trench', 'de': 'Ausraubungsgrube',
        'es': 'Fosa de expolio', 'fr': 'Fosse de récupération',
        'ar': 'حفرة نهب', 'ca': 'Fossa d\'espoli',
        'ro': 'Groapă de spoliere', 'pt': 'Fossa de espoliação',
        'el': 'Τάφρος σύλησης',
    },
    # Terms that appear in rapporti2 descriptions for special types - keep as-is
    'test': {l: 'test' for l in LANGS},
    'bla bla bla': {l: 'bla bla bla' for l in LANGS},
    'gggg': {l: 'gggg' for l in LANGS},
    'hhhh': {l: 'hhhh' for l in LANGS},
    'USV 1': {l: 'USV 1' for l in LANGS},
    'blabla bla': {l: 'blabla bla' for l in LANGS},
    'ggggg': {l: 'ggggg' for l in LANGS},
    'Materiale pietra dura': {l: 'Materiale pietra dura' for l in LANGS},
}

# Also handle "continuità con US 12" which includes the unit abbreviation
_CONTINUITY_PREFIX = 'continuità con '


def translate_d_interpretativa(val, lang):
    """Translate d_interpretativa, handling continuity references."""
    if not val:
        return val
    if val.startswith(_CONTINUITY_PREFIX):
        rest = val[len(_CONTINUITY_PREFIX):]
        # e.g. "US 12" → "SU 12"
        for it_abbr, tgt_abbr in [(IT_US, UNIT_TYPE_ABBREV[lang][0]),
                                   (IT_USM, UNIT_TYPE_ABBREV[lang][1])]:
            if rest.startswith(it_abbr + ' '):
                rest = tgt_abbr + rest[len(it_abbr):]
                break
        cont_word = {
            'en': 'continuity with ', 'de': 'Kontinuität mit ',
            'es': 'continuidad con ', 'fr': 'continuité avec ',
            'ar': 'استمرارية مع ', 'ca': 'continuïtat amb ',
            'ro': 'continuitate cu ', 'pt': 'continuidade com ',
            'el': 'συνέχεια με ',
        }
        return cont_word[lang] + rest
    # Also handle DosCo paths - keep as-is
    if val.startswith('DosCo'):
        return val
    return D_INTERPRETATIVA.get(val, {}).get(lang, val)


# formazione
FORMAZIONE = {
    'Antropica': {
        'en': 'Anthropic', 'de': 'Anthropogen', 'es': 'Antrópica',
        'fr': 'Anthropique', 'ar': 'بشري', 'ca': 'Antròpica',
        'ro': 'Antropică', 'pt': 'Antrópica', 'el': 'Ανθρωπογενής',
    },
    'Antropico': {
        'en': 'Anthropic', 'de': 'Anthropogen', 'es': 'Antrópico',
        'fr': 'Anthropique', 'ar': 'بشري', 'ca': 'Antròpic',
        'ro': 'Antropic', 'pt': 'Antrópico', 'el': 'Ανθρωπογενής',
    },
    'Naturale': {
        'en': 'Natural', 'de': 'Natürlich', 'es': 'Natural',
        'fr': 'Naturel', 'ar': 'طبيعي', 'ca': 'Natural',
        'ro': 'Natural', 'pt': 'Natural', 'el': 'Φυσικός',
    },
}

# stato_di_conservazione
STATO_CONSERVAZIONE = {
    'Buono': {
        'en': 'Good', 'de': 'Gut', 'es': 'Bueno', 'fr': 'Bon',
        'ar': 'جيد', 'ca': 'Bo', 'ro': 'Bun', 'pt': 'Bom', 'el': 'Καλή',
    },
    'Ottimo': {
        'en': 'Excellent', 'de': 'Ausgezeichnet', 'es': 'Excelente',
        'fr': 'Excellent', 'ar': 'ممتاز', 'ca': 'Excel·lent',
        'ro': 'Excelent', 'pt': 'Excelente', 'el': 'Εξαιρετική',
    },
    'Discreto': {
        'en': 'Fair', 'de': 'Mäßig', 'es': 'Discreto', 'fr': 'Correct',
        'ar': 'مقبول', 'ca': 'Discret', 'ro': 'Acceptabil', 'pt': 'Razoável',
        'el': 'Μέτρια',
    },
    'Scarso': {
        'en': 'Poor', 'de': 'Schlecht', 'es': 'Escaso', 'fr': 'Mauvais',
        'ar': 'ضعيف', 'ca': 'Escàs', 'ro': 'Slab', 'pt': 'Fraco',
        'el': 'Κακή',
    },
}

# colore
COLORE = {
    'Arancione': {
        'en': 'Orange', 'de': 'Orange', 'es': 'Naranja', 'fr': 'Orange',
        'ar': 'برتقالي', 'ca': 'Taronja', 'ro': 'Portocaliu', 'pt': 'Laranja',
        'el': 'Πορτοκαλί',
    },
    'Marrone scuro': {
        'en': 'Dark brown', 'de': 'Dunkelbraun', 'es': 'Marrón oscuro',
        'fr': 'Brun foncé', 'ar': 'بني داكن', 'ca': 'Marró fosc',
        'ro': 'Maro închis', 'pt': 'Castanho escuro', 'el': 'Σκούρο καφέ',
    },
    'Marrone chiaro': {
        'en': 'Light brown', 'de': 'Hellbraun', 'es': 'Marrón claro',
        'fr': 'Brun clair', 'ar': 'بني فاتح', 'ca': 'Marró clar',
        'ro': 'Maro deschis', 'pt': 'Castanho claro', 'el': 'Ανοιχτό καφέ',
    },
    'Biancastro': {
        'en': 'Whitish', 'de': 'Weißlich', 'es': 'Blanquecino',
        'fr': 'Blanchâtre', 'ar': 'أبيض باهت', 'ca': 'Blanquinós',
        'ro': 'Albicios', 'pt': 'Esbranquiçado', 'el': 'Υπόλευκο',
    },
    'Nerastro': {
        'en': 'Blackish', 'de': 'Schwärzlich', 'es': 'Negruzco',
        'fr': 'Noirâtre', 'ar': 'أسود باهت', 'ca': 'Negrós',
        'ro': 'Negricios', 'pt': 'Enegrecido', 'el': 'Μαυριδερό',
    },
    'Giallo scuro': {
        'en': 'Dark yellow', 'de': 'Dunkelgelb', 'es': 'Amarillo oscuro',
        'fr': 'Jaune foncé', 'ar': 'أصفر داكن', 'ca': 'Groc fosc',
        'ro': 'Galben închis', 'pt': 'Amarelo escuro', 'el': 'Σκούρο κίτρινο',
    },
    'Marrone': {
        'en': 'Brown', 'de': 'Braun', 'es': 'Marrón', 'fr': 'Brun',
        'ar': 'بني', 'ca': 'Marró', 'ro': 'Maro', 'pt': 'Castanho',
        'el': 'Καφέ',
    },
    'Grigio scuro': {
        'en': 'Dark grey', 'de': 'Dunkelgrau', 'es': 'Gris oscuro',
        'fr': 'Gris foncé', 'ar': 'رمادي داكن', 'ca': 'Gris fosc',
        'ro': 'Gri închis', 'pt': 'Cinzento escuro', 'el': 'Σκούρο γκρι',
    },
    'Marrone/giallastro': {
        'en': 'Brown/yellowish', 'de': 'Braun/gelblich', 'es': 'Marrón/amarillento',
        'fr': 'Brun/jaunâtre', 'ar': 'بني/مصفر', 'ca': 'Marró/groguenc',
        'ro': 'Maro/gălbui', 'pt': 'Castanho/amarelado', 'el': 'Καφέ/κιτρινωπό',
    },
}

# consistenza
CONSISTENZA = {
    'Compatta': {
        'en': 'Compact', 'de': 'Kompakt', 'es': 'Compacta', 'fr': 'Compacte',
        'ar': 'متراصة', 'ca': 'Compacta', 'ro': 'Compactă', 'pt': 'Compacta',
        'el': 'Συμπαγής',
    },
    'Friabile': {
        'en': 'Friable', 'de': 'Bröckelig', 'es': 'Friable', 'fr': 'Friable',
        'ar': 'هشة', 'ca': 'Friable', 'ro': 'Friabilă', 'pt': 'Friável',
        'el': 'Εύθρυπτη',
    },
    'Molto friabile': {
        'en': 'Very friable', 'de': 'Sehr bröckelig', 'es': 'Muy friable',
        'fr': 'Très friable', 'ar': 'هشة جداً', 'ca': 'Molt friable',
        'ro': 'Foarte friabilă', 'pt': 'Muito friável', 'el': 'Πολύ εύθρυπτη',
    },
    'Sabbiosa': {
        'en': 'Sandy', 'de': 'Sandig', 'es': 'Arenosa', 'fr': 'Sableuse',
        'ar': 'رملية', 'ca': 'Sorrera', 'ro': 'Nisipoasă', 'pt': 'Arenosa',
        'el': 'Αμμώδης',
    },
    'Argillosa': {
        'en': 'Clayey', 'de': 'Tonig', 'es': 'Arcillosa', 'fr': 'Argileuse',
        'ar': 'طينية', 'ca': 'Argilosa', 'ro': 'Argiloasă', 'pt': 'Argilosa',
        'el': 'Αργιλώδης',
    },
}

# metodo_di_scavo
METODO_SCAVO = {
    'Manuale': {
        'en': 'Manual', 'de': 'Manuell', 'es': 'Manual', 'fr': 'Manuel',
        'ar': 'يدوي', 'ca': 'Manual', 'ro': 'Manual', 'pt': 'Manual',
        'el': 'Χειροκίνητη',
    },
    'Stratigrafico': {
        'en': 'Stratigraphic', 'de': 'Stratigraphisch', 'es': 'Estratigráfico',
        'fr': 'Stratigraphique', 'ar': 'طبقي', 'ca': 'Estratigràfic',
        'ro': 'Stratigrafic', 'pt': 'Estratigráfico', 'el': 'Στρωματογραφική',
    },
}

# scavato (Si/No)
SCAVATO = {
    'Si': {
        'en': 'Yes', 'de': 'Ja', 'es': 'Sí', 'fr': 'Oui',
        'ar': 'نعم', 'ca': 'Sí', 'ro': 'Da', 'pt': 'Sim', 'el': 'Ναι',
    },
    'No': {
        'en': 'No', 'de': 'Nein', 'es': 'No', 'fr': 'Non',
        'ar': 'لا', 'ca': 'No', 'ro': 'Nu', 'pt': 'Não', 'el': 'Όχι',
    },
}

# inclusi items
INCLUSI = {
    'Calce': {
        'en': 'Lime', 'de': 'Kalk', 'es': 'Cal', 'fr': 'Chaux',
        'ar': 'كلس', 'ca': 'Calç', 'ro': 'Var', 'pt': 'Cal', 'el': 'Ite',
    },
    'Laterizio': {
        'en': 'Brick', 'de': 'Ziegel', 'es': 'Ladrillo', 'fr': 'Brique',
        'ar': 'آجر', 'ca': 'Maó', 'ro': 'Cărămidă', 'pt': 'Tijolo', 'el': 'Τούβλο',
    },
    'Malta': {
        'en': 'Mortar', 'de': 'Mörtel', 'es': 'Mortero', 'fr': 'Mortier',
        'ar': 'ملاط', 'ca': 'Morter', 'ro': 'Mortar', 'pt': 'Argamassa',
        'el': 'Κονίαμα',
    },
    'Carboni': {
        'en': 'Charcoal', 'de': 'Kohle', 'es': 'Carbones', 'fr': 'Charbons',
        'ar': 'فحم', 'ca': 'Carbons', 'ro': 'Cărbuni', 'pt': 'Carvões',
        'el': 'Κάρβουνα',
    },
    'Ciottoli': {
        'en': 'Pebbles', 'de': 'Kiesel', 'es': 'Guijarros', 'fr': 'Galets',
        'ar': 'حصى', 'ca': 'Còdols', 'ro': 'Pietricele', 'pt': 'Seixos',
        'el': 'Βότσαλα',
    },
    'Pietre': {
        'en': 'Stones', 'de': 'Steine', 'es': 'Piedras', 'fr': 'Pierres',
        'ar': 'حجارة', 'ca': 'Pedres', 'ro': 'Pietre', 'pt': 'Pedras',
        'el': 'Λίθοι',
    },
    'Sabbia': {
        'en': 'Sand', 'de': 'Sand', 'es': 'Arena', 'fr': 'Sable',
        'ar': 'رمل', 'ca': 'Sorra', 'ro': 'Nisip', 'pt': 'Areia',
        'el': 'Άμμος',
    },
    'Ghiaia': {
        'en': 'Gravel', 'de': 'Kies', 'es': 'Grava', 'fr': 'Gravier',
        'ar': 'حصى خشن', 'ca': 'Grava', 'ro': 'Pietriș', 'pt': 'Cascalho',
        'el': 'Χαλίκι',
    },
}

# documentazione items
DOCUMENTAZIONE = {
    'Fotografie': {
        'en': 'Photographs', 'de': 'Fotografien', 'es': 'Fotografías',
        'fr': 'Photographies', 'ar': 'صور فوتوغرافية', 'ca': 'Fotografies',
        'ro': 'Fotografii', 'pt': 'Fotografias', 'el': 'Φωτογραφίες',
    },
    'Planimetrie': {
        'en': 'Plans', 'de': 'Pläne', 'es': 'Planimetrías',
        'fr': 'Plans', 'ar': 'مخططات', 'ca': 'Planimetries',
        'ro': 'Planimetrii', 'pt': 'Planimetrias', 'el': 'Κατόψεις',
    },
    'Sezioni': {
        'en': 'Sections', 'de': 'Schnitte', 'es': 'Secciones',
        'fr': 'Coupes', 'ar': 'مقاطع', 'ca': 'Seccions',
        'ro': 'Secțiuni', 'pt': 'Secções', 'el': 'Τομές',
    },
    'Diapositive': {
        'en': 'Slides', 'de': 'Dias', 'es': 'Diapositivas',
        'fr': 'Diapositives', 'ar': 'شرائح', 'ca': 'Diapositives',
        'ro': 'Diapozitive', 'pt': 'Diapositivos', 'el': 'Διαφάνειες',
    },
    'Fotopiano': {
        'en': 'Photoplans', 'de': 'Fotopläne', 'es': 'Fotoplanos',
        'fr': 'Photoplans', 'ar': 'مخططات فوتوغرافية', 'ca': 'Fotoplànols',
        'ro': 'Fotoplanuri', 'pt': 'Fotoplanos', 'el': 'Φωτοσχέδια',
    },
}

# ---------------------------------------------------------------------------
# Period descriptions
# ---------------------------------------------------------------------------
PERIOD_DESC = {
    "Eta' contemporanea": {
        'en': 'Contemporary era', 'de': 'Zeitgenössische Epoche',
        'es': 'Edad contemporánea', 'fr': 'Époque contemporaine',
        'ar': 'العصر المعاصر', 'ca': 'Edat contemporània',
        'ro': 'Epoca contemporană', 'pt': 'Idade contemporânea',
        'el': 'Σύγχρονη εποχή',
    },
    'Età contemporanea': {  # alternate form
        'en': 'Contemporary era', 'de': 'Zeitgenössische Epoche',
        'es': 'Edad contemporánea', 'fr': 'Époque contemporaine',
        'ar': 'العصر المعاصر', 'ca': 'Edat contemporània',
        'ro': 'Epoca contemporană', 'pt': 'Idade contemporânea',
        'el': 'Σύγχρονη εποχή',
    },
    'Età moderna': {
        'en': 'Modern era', 'de': 'Neuzeit', 'es': 'Edad moderna',
        'fr': 'Époque moderne', 'ar': 'العصر الحديث', 'ca': 'Edat moderna',
        'ro': 'Epoca modernă', 'pt': 'Idade moderna', 'el': 'Νεότερη εποχή',
    },
    'Fine XVI secolo - Inizi XVII secolo': {
        'en': 'Late 16th - Early 17th century', 'de': 'Ende 16. - Anfang 17. Jh.',
        'es': 'Finales del s. XVI - Inicios del s. XVII',
        'fr': 'Fin XVIe - Début XVIIe siècle',
        'ar': 'نهاية القرن 16 - بداية القرن 17',
        'ca': 'Finals del s. XVI - Inicis del s. XVII',
        'ro': 'Sfârșitul sec. XVI - Începutul sec. XVII',
        'pt': 'Finais do séc. XVI - Inícios do séc. XVII',
        'el': 'Τέλη 16ου - Αρχές 17ου αι.',
    },
    'Prima metà del XVI secolo': {
        'en': 'First half of the 16th century', 'de': 'Erste Hälfte 16. Jh.',
        'es': 'Primera mitad del s. XVI', 'fr': 'Première moitié du XVIe siècle',
        'ar': 'النصف الأول من القرن 16', 'ca': 'Primera meitat del s. XVI',
        'ro': 'Prima jumătate a sec. XVI', 'pt': 'Primeira metade do séc. XVI',
        'el': 'Πρώτο μισό 16ου αι.',
    },
    'XV secolo': {
        'en': '15th century', 'de': '15. Jahrhundert', 'es': 'Siglo XV',
        'fr': 'XVe siècle', 'ar': 'القرن الخامس عشر', 'ca': 'Segle XV',
        'ro': 'Secolul XV', 'pt': 'Século XV', 'el': '15ος αιώνας',
    },
    "Prima metà' del XV secolo": {
        'en': 'First half of the 15th century', 'de': 'Erste Hälfte 15. Jh.',
        'es': 'Primera mitad del s. XV', 'fr': 'Première moitié du XVe siècle',
        'ar': 'النصف الأول من القرن 15', 'ca': 'Primera meitat del s. XV',
        'ro': 'Prima jumătate a sec. XV', 'pt': 'Primeira metade do séc. XV',
        'el': 'Πρώτο μισό 15ου αι.',
    },
    'Inizi XV secolo': {
        'en': 'Early 15th century', 'de': 'Anfang 15. Jh.',
        'es': 'Inicios del s. XV', 'fr': 'Début XVe siècle',
        'ar': 'بداية القرن 15', 'ca': 'Inicis del s. XV',
        'ro': 'Începutul sec. XV', 'pt': 'Inícios do séc. XV',
        'el': 'Αρχές 15ου αι.',
    },
    'Fine XIV secolo': {
        'en': 'Late 14th century', 'de': 'Ende 14. Jh.',
        'es': 'Finales del s. XIV', 'fr': 'Fin XIVe siècle',
        'ar': 'نهاية القرن 14', 'ca': 'Finals del s. XIV',
        'ro': 'Sfârșitul sec. XIV', 'pt': 'Finais do séc. XIV',
        'el': 'Τέλη 14ου αι.',
    },
    'Seconda metà del XIV secolo': {
        'en': 'Second half of the 14th century', 'de': 'Zweite Hälfte 14. Jh.',
        'es': 'Segunda mitad del s. XIV', 'fr': 'Seconde moitié du XIVe siècle',
        'ar': 'النصف الثاني من القرن 14', 'ca': 'Segona meitat del s. XIV',
        'ro': 'A doua jumătate a sec. XIV', 'pt': 'Segunda metade do séc. XIV',
        'el': 'Δεύτερο μισό 14ου αι.',
    },
    "Seconda metà' del XIV secolo": {  # alternate form with '
        'en': 'Second half of the 14th century', 'de': 'Zweite Hälfte 14. Jh.',
        'es': 'Segunda mitad del s. XIV', 'fr': 'Seconde moitié du XIVe siècle',
        'ar': 'النصف الثاني من القرن 14', 'ca': 'Segona meitat del s. XIV',
        'ro': 'A doua jumătate a sec. XIV', 'pt': 'Segunda metade do séc. XIV',
        'el': 'Δεύτερο μισό 14ου αι.',
    },
    'Generico XIII secolo - Primi del XIV secolo': {
        'en': 'Generic 13th - Early 14th century', 'de': 'Allgemein 13. - Anfang 14. Jh.',
        'es': 'Genérico s. XIII - Inicios del s. XIV',
        'fr': 'Générique XIIIe - Début XIVe siècle',
        'ar': 'عام القرن 13 - بداية القرن 14',
        'ca': 'Genèric s. XIII - Inicis del s. XIV',
        'ro': 'Generic sec. XIII - Începutul sec. XIV',
        'pt': 'Genérico séc. XIII - Inícios do séc. XIV',
        'el': 'Γενικά 13ος - Αρχές 14ου αι.',
    },
    'XV sec rec': {
        'en': '15th cent. recent', 'de': '15. Jh. rezent',
        'es': 'S. XV reciente', 'fr': 'XVe s. récent',
        'ar': 'القرن 15 حديث', 'ca': 'S. XV recent',
        'ro': 'Sec. XV recent', 'pt': 'Séc. XV recente',
        'el': '15ος αι. πρόσφατος',
    },
    "Prima metà del XV secolo rec": {
        'en': 'First half 15th cent. recent', 'de': 'Erste Hälfte 15. Jh. rezent',
        'es': 'Primera mitad s. XV reciente', 'fr': 'Première moitié XVe s. récent',
        'ar': 'النصف الأول القرن 15 حديث', 'ca': 'Primera meitat s. XV recent',
        'ro': 'Prima jumătate sec. XV recent', 'pt': 'Primeira metade séc. XV recente',
        'el': 'Πρώτο μισό 15ου αι. πρόσφατος',
    },
    "Prima metà' del XV secolo rec": {
        'en': 'First half 15th cent. recent', 'de': 'Erste Hälfte 15. Jh. rezent',
        'es': 'Primera mitad s. XV reciente', 'fr': 'Première moitié XVe s. récent',
        'ar': 'النصف الأول القرن 15 حديث', 'ca': 'Primera meitat s. XV recent',
        'ro': 'Prima jumătate sec. XV recent', 'pt': 'Primeira metade séc. XV recente',
        'el': 'Πρώτο μισό 15ου αι. πρόσφατος',
    },
}

# ---------------------------------------------------------------------------
# Long-text term replacements for descrizione / interpretazione
# ---------------------------------------------------------------------------
# These Italian terms will be searched and replaced in long text fields.
# Ordered longest-first to avoid partial matches.
LONG_TEXT_TERMS = {
    'en': [
        ('Struttura in muratura', 'Masonry structure'),
        ('Strato di terra', 'Earth layer'),
        ('Strato di sabbia', 'Sand layer'),
        ('Strato di malta', 'Mortar layer'),
        ('strato di terra', 'earth layer'),
        ('strato di sabbia', 'sand layer'),
        ('strato di malta', 'mortar layer'),
        ('pavimentazione in terra', 'earth floor'),
        ('punto di fuoco', 'fire point'),
        ('fossa di spoliazione', 'robber trench'),
        ('area di scavo', 'excavation area'),
        ('in muratura', 'masonry'),
        ('composta da laterizi', 'composed of bricks'),
        ('legati da malta', 'bonded by mortar'),
        ('di reimpiego', 'reused'),
        ('di recupero', 'salvaged'),
        ('in senso est ovest', 'east-west oriented'),
        ('in senso est-ovest', 'east-west oriented'),
        ('Pianta e quote', 'Plan and elevations'),
        ('Pianta e quota', 'Plan and elevation'),
        ('Piante e quote', 'Plans and elevations'),
        ('pianta e quote', 'plan and elevations'),
        ('in fase di scavo', 'during excavation'),
        ('fase di scavo', 'excavation phase'),
        ('buca di palo', 'post hole'),
        ('alloggio per palo', 'post socket'),
        ('laterizi di reimpiego', 'reused bricks'),
        ('laterizi di riuso', 'reused bricks'),
        ('laterizi di recupero', 'salvaged bricks'),
        ('frammenti di laterizio', 'brick fragments'),
        ('frammenti di ceramica', 'pottery fragments'),
        ('di composizione eterogenea', 'of heterogeneous composition'),
        ('di consistenza compatta', 'of compact consistency'),
        ('di consistenza friabile', 'of friable consistency'),
        ('di colore marrone scuro', 'of dark brown colour'),
        ('di colore marrone chiaro', 'of light brown colour'),
        ('di colore biancastro', 'of whitish colour'),
        ('di colore marrone', 'of brown colour'),
        ('di colore nerastro', 'of blackish colour'),
        ('di colore grigio', 'of grey colour'),
        ('di colore nero', 'of black colour'),
        ('forma irregolarmente circolare', 'irregularly circular shape'),
        ('diametro di circa', 'diameter of approximately'),
        ('profondo circa', 'approximately deep'),
        ('profondo 10-12 cm', '10-12 cm deep'),
        ('nella parte sud', 'in the south part'),
        ('nella parte nord', 'in the north part'),
        ('nella parte est', 'in the east part'),
        ('nella parte ovest', 'in the west part'),
        ('parte sud-ovest', 'south-west part'),
        ('parte nord-est', 'north-east part'),
        ('in appoggio', 'abutting'),
        ('Gli si appoggia', 'It abuts'),
        ('Si appoggia', 'It abuts'),
        ('si appoggia', 'abuts'),
        ('Coperto da', 'Covered by'),
        ('coperto da', 'covered by'),
        ('E\' coperto', 'It is covered'),
        ('e\' coperto', 'is covered'),
        ('edificio', 'building'),
        ('scavo', 'excavation'),
        ('sezione', 'section'),
        ('saggio', 'trial trench'),
        ('superficie', 'surface'),
        ('muratura', 'masonry'),
        ('perimetrale', 'perimeter wall'),
        ('focolare', 'hearth'),
        ('pavimentazione', 'floor'),
        ('livellamento', 'levelling'),
        ('disfacimento', 'decay'),
        ('abbandono', 'abandonment'),
        ('riempimento', 'fill'),
        ('preparazione', 'preparation'),
        ('fondazione', 'foundation'),
        ('pilastro', 'pillar'),
        ('spoliazione', 'spoliation'),
        ('battuto', 'beaten floor'),
        ('laterizi', 'bricks'),
        ('laterizio', 'brick'),
        ('ciottoli', 'pebbles'),
        ('carboni', 'charcoals'),
        ('cenere', 'ash'),
        ('ceneri', 'ashes'),
        ('calce', 'lime'),
        ('sabbia', 'sand'),
        ('sabbie', 'sands'),
        ('argilla', 'clay'),
        ('argille', 'clays'),
        ('ghiaia', 'gravel'),
        ('macerie', 'rubble'),
        ('pietre', 'stones'),
        ('terra', 'earth'),
        ('muro', 'wall'),
        ('muri', 'walls'),
        ('palo', 'post'),
        ('buca', 'pit'),
        ('taglio', 'cut'),
        ('strato', 'layer'),
        ('colore', 'colour'),
        ('spessore', 'thickness'),
        ('inclusi', 'inclusions'),
        ('Pianta', 'Plan'),
        ('pianta', 'plan'),
        ('quota', 'elevation'),
        ('rari', 'rare'),
    ],
    'de': [
        ('Struttura in muratura', 'Mauerwerksstruktur'),
        ('Strato di terra', 'Erdschicht'),
        ('Strato di sabbia', 'Sandschicht'),
        ('Strato di malta', 'Mörtelschicht'),
        ('pavimentazione in terra', 'Erdboden'),
        ('punto di fuoco', 'Feuerstelle'),
        ('area di scavo', 'Grabungsfläche'),
        ('in muratura', 'Mauerwerk'),
        ('Pianta e quote', 'Plan und Höhen'),
        ('focolare', 'Feuerstelle'),
        ('laterizi', 'Ziegel'),
        ('calce', 'Kalk'),
        ('sabbia', 'Sand'),
        ('argilla', 'Ton'),
        ('terra', 'Erde'),
        ('muro', 'Mauer'),
        ('strato', 'Schicht'),
        ('edificio', 'Gebäude'),
        ('scavo', 'Grabung'),
    ],
    'es': [
        ('Struttura in muratura', 'Estructura de mampostería'),
        ('Strato di terra', 'Estrato de tierra'),
        ('pavimentazione in terra', 'pavimento de tierra'),
        ('punto di fuoco', 'punto de fuego'),
        ('area di scavo', 'área de excavación'),
        ('Pianta e quote', 'Planta y cotas'),
        ('focolare', 'hogar'),
        ('laterizi', 'ladrillos'),
        ('calce', 'cal'),
        ('sabbia', 'arena'),
        ('terra', 'tierra'),
        ('muro', 'muro'),
        ('strato', 'estrato'),
        ('edificio', 'edificio'),
        ('scavo', 'excavación'),
    ],
    'fr': [
        ('Struttura in muratura', 'Structure en maçonnerie'),
        ('Strato di terra', 'Couche de terre'),
        ('pavimentazione in terra', 'sol en terre'),
        ('punto di fuoco', 'point de feu'),
        ('area di scavo', 'zone de fouille'),
        ('Pianta e quote', 'Plan et altitudes'),
        ('focolare', 'foyer'),
        ('laterizi', 'briques'),
        ('calce', 'chaux'),
        ('sabbia', 'sable'),
        ('terra', 'terre'),
        ('muro', 'mur'),
        ('strato', 'couche'),
        ('edificio', 'bâtiment'),
        ('scavo', 'fouille'),
    ],
    'ar': [
        ('Struttura in muratura', 'بنية بناء'),
        ('Strato di terra', 'طبقة تراب'),
        ('pavimentazione in terra', 'أرضية ترابية'),
        ('punto di fuoco', 'نقطة نار'),
        ('area di scavo', 'منطقة التنقيب'),
        ('Pianta e quote', 'مخطط وارتفاعات'),
        ('focolare', 'موقد'),
        ('laterizi', 'آجر'),
        ('calce', 'كلس'),
        ('sabbia', 'رمل'),
        ('terra', 'تراب'),
        ('muro', 'جدار'),
        ('strato', 'طبقة'),
        ('edificio', 'مبنى'),
        ('scavo', 'تنقيب'),
    ],
    'ca': [
        ('Struttura in muratura', 'Estructura de maçoneria'),
        ('Strato di terra', 'Estrat de terra'),
        ('pavimentazione in terra', 'paviment de terra'),
        ('punto di fuoco', 'punt de foc'),
        ('area di scavo', 'àrea d\'excavació'),
        ('Pianta e quote', 'Planta i cotes'),
        ('focolare', 'llar de foc'),
        ('laterizi', 'maons'),
        ('calce', 'calç'),
        ('sabbia', 'sorra'),
        ('terra', 'terra'),
        ('muro', 'mur'),
        ('strato', 'estrat'),
        ('edificio', 'edifici'),
        ('scavo', 'excavació'),
    ],
    'ro': [
        ('Struttura in muratura', 'Structură din zidărie'),
        ('Strato di terra', 'Strat de pământ'),
        ('pavimentazione in terra', 'pardoseală din pământ'),
        ('punto di fuoco', 'punct de foc'),
        ('area di scavo', 'zona de săpătură'),
        ('Pianta e quote', 'Plan și cote'),
        ('focolare', 'vatră'),
        ('laterizi', 'cărămizi'),
        ('calce', 'var'),
        ('sabbia', 'nisip'),
        ('terra', 'pământ'),
        ('muro', 'zid'),
        ('strato', 'strat'),
        ('edificio', 'edificiu'),
        ('scavo', 'săpătură'),
    ],
    'pt': [
        ('Struttura in muratura', 'Estrutura em alvenaria'),
        ('Strato di terra', 'Camada de terra'),
        ('pavimentazione in terra', 'pavimento de terra'),
        ('punto di fuoco', 'ponto de fogo'),
        ('area di scavo', 'área de escavação'),
        ('Pianta e quote', 'Planta e cotas'),
        ('focolare', 'lareira'),
        ('laterizi', 'tijolos'),
        ('calce', 'cal'),
        ('sabbia', 'areia'),
        ('terra', 'terra'),
        ('muro', 'muro'),
        ('strato', 'camada'),
        ('edificio', 'edifício'),
        ('scavo', 'escavação'),
    ],
    'el': [
        ('Struttura in muratura', 'Κατασκευή τοιχοποιίας'),
        ('Strato di terra', 'Στρώμα χώματος'),
        ('pavimentazione in terra', 'χωμάτινο δάπεδο'),
        ('punto di fuoco', 'σημείο φωτιάς'),
        ('area di scavo', 'περιοχή ανασκαφής'),
        ('Pianta e quote', 'Κάτοψη και υψόμετρα'),
        ('focolare', 'εστία'),
        ('laterizi', 'τούβλα'),
        ('calce', 'ite'),
        ('sabbia', 'άμμος'),
        ('terra', 'χώμα'),
        ('muro', 'τοίχος'),
        ('strato', 'στρώμα'),
        ('edificio', 'κτίριο'),
        ('scavo', 'ανασκαφή'),
    ],
}


def translate_long_text(text, lang):
    """Best-effort translation of long Italian text via term replacement."""
    if not text:
        return text
    result = text
    replacements = LONG_TEXT_TERMS.get(lang, [])
    for it_term, tgt_term in replacements:
        result = result.replace(it_term, tgt_term)
    return result


# ---------------------------------------------------------------------------
# Translate list-encoded fields (inclusi, campioni, documentazione, rapporti)
# ---------------------------------------------------------------------------

def safe_eval(text):
    """Safely parse a Python list literal stored as TEXT."""
    if not text or text in ('', '[]'):
        return []
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return []


def translate_inclusi(items, lang):
    """Translate inclusi list items."""
    result = []
    for item in items:
        if isinstance(item, list) and len(item) >= 1:
            translated = INCLUSI.get(item[0], {}).get(lang, item[0])
            result.append([translated] + item[1:])
        else:
            result.append(item)
    return result


def translate_documentazione(items, lang):
    """Translate documentazione list items and Si/No values."""
    result = []
    for item in items:
        if isinstance(item, list) and len(item) >= 2:
            doc_type = DOCUMENTAZIONE.get(item[0], {}).get(lang, item[0])
            yes_no = SCAVATO.get(item[1], {}).get(lang, item[1])
            result.append([doc_type, yes_no] + item[2:])
        else:
            result.append(item)
    return result


def translate_rapporti(items, lang):
    """Translate rapporti: [['Copre', '2'], ...]"""
    result = []
    for item in items:
        if isinstance(item, list) and len(item) >= 2:
            term = translate_rel_term(item[0], lang)
            result.append([term] + item[1:])
        else:
            result.append(item)
    return result


def translate_rapporti2(items, lang):
    """Translate rapporti2: [['Copre', '2', 'US', 'Livellamento', '1-2'], ...]"""
    result = []
    for item in items:
        if isinstance(item, list) and len(item) >= 5:
            term = translate_rel_term(item[0], lang)
            us_num = item[1]
            unit_type = translate_unit_type(item[2], lang)
            d_interp = translate_d_interpretativa(item[3], lang)
            period_phase = item[4]
            result.append([term, us_num, unit_type, d_interp, period_phase])
        elif isinstance(item, list) and len(item) >= 2:
            term = translate_rel_term(item[0], lang)
            result.append([term] + item[1:])
        else:
            result.append(item)
    return result


# ---------------------------------------------------------------------------
# GIS tipo_us_s translations (material/feature types in geometry layers)
# ---------------------------------------------------------------------------
GIS_TIPO_US = {
    'barba': {
        'en': 'barbican', 'de': 'Barbakane', 'es': 'barbacana',
        'fr': 'barbacane', 'ar': 'حاجز', 'ca': 'barbacana',
        'ro': 'barbacană', 'pt': 'barbacã', 'el': 'προμαχώνας',
    },
    'calce': {
        'en': 'lime', 'de': 'Kalk', 'es': 'cal', 'fr': 'chaux',
        'ar': 'كلس', 'ca': 'calç', 'ro': 'var', 'pt': 'cal', 'el': 'ite',
    },
    'carboni': {
        'en': 'charcoal', 'de': 'Kohle', 'es': 'carbones', 'fr': 'charbons',
        'ar': 'فحم', 'ca': 'carbons', 'ro': 'cărbuni', 'pt': 'carvões', 'el': 'κάρβουνα',
    },
    'ciottolo': {
        'en': 'pebble', 'de': 'Kiesel', 'es': 'guijarro', 'fr': 'galet',
        'ar': 'حصاة', 'ca': 'còdol', 'ro': 'pietricică', 'pt': 'seixo', 'el': 'βότσαλο',
    },
    'coppo': {
        'en': 'roof tile', 'de': 'Dachziegel', 'es': 'teja', 'fr': 'tuile',
        'ar': 'قرميد', 'ca': 'teula', 'ro': 'țiglă', 'pt': 'telha', 'el': 'κεραμίδι',
    },
    'curva di livello': {
        'en': 'contour line', 'de': 'Höhenlinie', 'es': 'curva de nivel',
        'fr': 'courbe de niveau', 'ar': 'خط كنتور', 'ca': 'corba de nivell',
        'ro': 'curbă de nivel', 'pt': 'curva de nível', 'el': 'ισοϋψής',
    },
    'laterizio': {
        'en': 'brick', 'de': 'Ziegel', 'es': 'ladrillo', 'fr': 'brique',
        'ar': 'آجر', 'ca': 'maó', 'ro': 'cărămidă', 'pt': 'tijolo', 'el': 'τούβλο',
    },
    'malta': {
        'en': 'mortar', 'de': 'Mörtel', 'es': 'mortero', 'fr': 'mortier',
        'ar': 'ملاط', 'ca': 'morter', 'ro': 'mortar', 'pt': 'argamassa', 'el': 'κονίαμα',
    },
    'negativa': {
        'en': 'negative', 'de': 'negativ', 'es': 'negativa', 'fr': 'négative',
        'ar': 'سلبي', 'ca': 'negativa', 'ro': 'negativă', 'pt': 'negativa', 'el': 'αρνητική',
    },
    'positiva': {
        'en': 'positive', 'de': 'positiv', 'es': 'positiva', 'fr': 'positive',
        'ar': 'إيجابي', 'ca': 'positiva', 'ro': 'pozitivă', 'pt': 'positiva', 'el': 'θετική',
    },
    'sabbia': {
        'en': 'sand', 'de': 'Sand', 'es': 'arena', 'fr': 'sable',
        'ar': 'رمل', 'ca': 'sorra', 'ro': 'nisip', 'pt': 'areia', 'el': 'άμμος',
    },
    'sabbia concotta': {
        'en': 'fired sand', 'de': 'gebrannter Sand', 'es': 'arena cocida',
        'fr': 'sable cuit', 'ar': 'رمل محروق', 'ca': 'sorra cuita',
        'ro': 'nisip ars', 'pt': 'areia cozida', 'el': 'ψημένη άμμος',
    },
    'struttura': {
        'en': 'structure', 'de': 'Struktur', 'es': 'estructura', 'fr': 'structure',
        'ar': 'بنية', 'ca': 'estructura', 'ro': 'structură', 'pt': 'estrutura', 'el': 'δομή',
    },
}

# ---------------------------------------------------------------------------
# Struttura field translations
# ---------------------------------------------------------------------------
STRUTTURA_CATEGORIA = {
    'Edificio': {
        'en': 'Building', 'de': 'Gebäude', 'es': 'Edificio', 'fr': 'Bâtiment',
        'ar': 'مبنى', 'ca': 'Edifici', 'ro': 'Edificiu', 'pt': 'Edifício', 'el': 'Κτίριο',
    },
    'Focolare': {
        'en': 'Hearth', 'de': 'Feuerstelle', 'es': 'Hogar', 'fr': 'Foyer',
        'ar': 'موقد', 'ca': 'Llar de foc', 'ro': 'Vatră', 'pt': 'Lareira', 'el': 'Εστία',
    },
    'Muro': {
        'en': 'Wall', 'de': 'Mauer', 'es': 'Muro', 'fr': 'Mur',
        'ar': 'جدار', 'ca': 'Mur', 'ro': 'Zid', 'pt': 'Muro', 'el': 'Τοίχος',
    },
    'Pavimentazione': {
        'en': 'Flooring', 'de': 'Bodenbelag', 'es': 'Pavimentación', 'fr': 'Revêtement de sol',
        'ar': 'أرضية', 'ca': 'Pavimentació', 'ro': 'Pardoseală', 'pt': 'Pavimentação', 'el': 'Δάπεδο',
    },
    'Fossa': {
        'en': 'Pit', 'de': 'Grube', 'es': 'Fosa', 'fr': 'Fosse',
        'ar': 'حفرة', 'ca': 'Fossa', 'ro': 'Groapă', 'pt': 'Fossa', 'el': 'Λάκκος',
    },
    'Spoliazione': {
        'en': 'Robbing', 'de': 'Ausraubung', 'es': 'Expolio', 'fr': 'Récupération',
        'ar': 'نهب', 'ca': 'Espoli', 'ro': 'Spoliere', 'pt': 'Espoliação', 'el': 'Σύληση',
    },
}

STRUTTURA_TIPOLOGIA = {
    'Edificio privato': {
        'en': 'Private building', 'de': 'Privatgebäude', 'es': 'Edificio privado',
        'fr': 'Bâtiment privé', 'ar': 'مبنى خاص', 'ca': 'Edifici privat',
        'ro': 'Edificiu privat', 'pt': 'Edifício privado', 'el': 'Ιδιωτικό κτίριο',
    },
    'Focolare domestico': {
        'en': 'Domestic hearth', 'de': 'Häusliche Feuerstelle', 'es': 'Hogar doméstico',
        'fr': 'Foyer domestique', 'ar': 'موقد منزلي', 'ca': 'Llar de foc domèstica',
        'ro': 'Vatră domestică', 'pt': 'Lareira doméstica', 'el': 'Οικιακή εστία',
    },
    'Muro perimetrale': {
        'en': 'Perimeter wall', 'de': 'Umfassungsmauer', 'es': 'Muro perimetral',
        'fr': 'Mur périmétral', 'ar': 'جدار محيطي', 'ca': 'Mur perimetral',
        'ro': 'Zid perimetral', 'pt': 'Muro perimetral', 'el': 'Περιμετρικός τοίχος',
    },
    'Muro interno': {
        'en': 'Internal wall', 'de': 'Innenwand', 'es': 'Muro interno',
        'fr': 'Mur intérieur', 'ar': 'جدار داخلي', 'ca': 'Mur intern',
        'ro': 'Zid interior', 'pt': 'Muro interno', 'el': 'Εσωτερικός τοίχος',
    },
    'Tramezzo': {
        'en': 'Partition wall', 'de': 'Trennwand', 'es': 'Tabique',
        'fr': 'Cloison', 'ar': 'حاجز', 'ca': 'Envà',
        'ro': 'Perete despărțitor', 'pt': 'Tabique', 'el': 'Χώρισμα',
    },
    'Pavimentazione in terra': {
        'en': 'Earth floor', 'de': 'Erdboden', 'es': 'Pavimento de tierra',
        'fr': 'Sol en terre', 'ar': 'أرضية ترابية', 'ca': 'Paviment de terra',
        'ro': 'Pardoseală din pământ', 'pt': 'Pavimento de terra', 'el': 'Χωμάτινο δάπεδο',
    },
    'Fossa': {
        'en': 'Pit', 'de': 'Grube', 'es': 'Fosa', 'fr': 'Fosse',
        'ar': 'حفرة', 'ca': 'Fossa', 'ro': 'Groapă', 'pt': 'Fossa', 'el': 'Λάκκος',
    },
    'Fossa di spoliazione': {
        'en': 'Robber trench', 'de': 'Ausraubungsgrube', 'es': 'Fosa de expolio',
        'fr': 'Fosse de récupération', 'ar': 'حفرة نهب', 'ca': "Fossa d'espoli",
        'ro': 'Groapă de spoliere', 'pt': 'Fossa de espoliação', 'el': 'Τάφρος σύλησης',
    },
}

STRUTTURA_DEFINIZIONE = {
    'Casa': {
        'en': 'House', 'de': 'Haus', 'es': 'Casa', 'fr': 'Maison',
        'ar': 'منزل', 'ca': 'Casa', 'ro': 'Casă', 'pt': 'Casa', 'el': 'Σπίτι',
    },
    'Focolare': {
        'en': 'Hearth', 'de': 'Feuerstelle', 'es': 'Hogar', 'fr': 'Foyer',
        'ar': 'موقد', 'ca': 'Llar de foc', 'ro': 'Vatră', 'pt': 'Lareira', 'el': 'Εστία',
    },
    'Muro perimetrale': {
        'en': 'Perimeter wall', 'de': 'Umfassungsmauer', 'es': 'Muro perimetral',
        'fr': 'Mur périmétral', 'ar': 'جدار محيطي', 'ca': 'Mur perimetral',
        'ro': 'Zid perimetral', 'pt': 'Muro perimetral', 'el': 'Περιμετρικός τοίχος',
    },
    'Muro interno': {
        'en': 'Internal wall', 'de': 'Innenwand', 'es': 'Muro interno',
        'fr': 'Mur intérieur', 'ar': 'جدار داخلي', 'ca': 'Mur intern',
        'ro': 'Zid interior', 'pt': 'Muro interno', 'el': 'Εσωτερικός τοίχος',
    },
    'Tramezzo': {
        'en': 'Partition wall', 'de': 'Trennwand', 'es': 'Tabique',
        'fr': 'Cloison', 'ar': 'حاجز', 'ca': 'Envà',
        'ro': 'Perete despărțitor', 'pt': 'Tabique', 'el': 'Χώρισμα',
    },
    'Pavimento': {
        'en': 'Floor', 'de': 'Boden', 'es': 'Pavimento', 'fr': 'Sol',
        'ar': 'أرضية', 'ca': 'Paviment', 'ro': 'Pardoseală', 'pt': 'Pavimento', 'el': 'Δάπεδο',
    },
    'Fossa': {
        'en': 'Pit', 'de': 'Grube', 'es': 'Fosa', 'fr': 'Fosse',
        'ar': 'حفرة', 'ca': 'Fossa', 'ro': 'Groapă', 'pt': 'Fossa', 'el': 'Λάκκος',
    },
    'Fossa di spoliazione': {
        'en': 'Robber trench', 'de': 'Ausraubungsgrube', 'es': 'Fosa de expolio',
        'fr': 'Fosse de récupération', 'ar': 'حفرة نهب', 'ca': "Fossa d'espoli",
        'ro': 'Groapă de spoliere', 'pt': 'Fossa de espoliação', 'el': 'Τάφρος σύλησης',
    },
}

# Struttura relationship terms not in the main RELATIONSHIPS dict
STRUTTURA_RAPPORTI_EXTRA = {
    'Fa parte di': {
        'en': 'Part of', 'de': 'Teil von', 'es': 'Parte de',
        'fr': 'Fait partie de', 'ar': 'جزء من', 'ca': 'Part de',
        'ro': 'Parte din', 'pt': 'Parte de', 'el': 'Μέρος του',
    },
    'Contiene': {
        'en': 'Contains', 'de': 'Enthält', 'es': 'Contiene',
        'fr': 'Contient', 'ar': 'يحتوي', 'ca': 'Conté',
        'ro': 'Conține', 'pt': 'Contém', 'el': 'Περιέχει',
    },
}

# Structural element names
STRUTTURA_ELEMENTI = {
    'Tramezzo interno': {
        'en': 'Internal partition', 'de': 'Innere Trennwand', 'es': 'Tabique interno',
        'fr': 'Cloison interne', 'ar': 'حاجز داخلي', 'ca': 'Envà intern',
        'ro': 'Perete despărțitor interior', 'pt': 'Tabique interno', 'el': 'Εσωτερικό χώρισμα',
    },
    'Focolare': {
        'en': 'Hearth', 'de': 'Feuerstelle', 'es': 'Hogar', 'fr': 'Foyer',
        'ar': 'موقد', 'ca': 'Llar de foc', 'ro': 'Vatră', 'pt': 'Lareira', 'el': 'Εστία',
    },
    'Muro perimetrale': {
        'en': 'Perimeter wall', 'de': 'Umfassungsmauer', 'es': 'Muro perimetral',
        'fr': 'Mur périmétral', 'ar': 'جدار محيطي', 'ca': 'Mur perimetral',
        'ro': 'Zid perimetral', 'pt': 'Muro perimetral', 'el': 'Περιμετρικός τοίχος',
    },
    'Pavimento': {
        'en': 'Floor', 'de': 'Boden', 'es': 'Pavimento', 'fr': 'Sol',
        'ar': 'أرضية', 'ca': 'Paviment', 'ro': 'Pardoseală', 'pt': 'Pavimento', 'el': 'Δάπεδο',
    },
}

# ---------------------------------------------------------------------------
# Tomba field translations
# ---------------------------------------------------------------------------
TOMBA_RITO = {
    'Inumazione': {
        'en': 'Inhumation', 'de': 'Körperbestattung', 'es': 'Inhumación',
        'fr': 'Inhumation', 'ar': 'دفن', 'ca': 'Inhumació',
        'ro': 'Înhumare', 'pt': 'Inumação', 'el': 'Ενταφιασμός',
    },
    'Cremazione': {
        'en': 'Cremation', 'de': 'Brandbestattung', 'es': 'Cremación',
        'fr': 'Crémation', 'ar': 'حرق', 'ca': 'Cremació',
        'ro': 'Incinerare', 'pt': 'Cremação', 'el': 'Αποτέφρωση',
    },
}

TOMBA_TIPO_DEPOSIZIONE = {
    'Primaria': {
        'en': 'Primary', 'de': 'Primär', 'es': 'Primaria', 'fr': 'Primaire',
        'ar': 'أولي', 'ca': 'Primària', 'ro': 'Primară', 'pt': 'Primária', 'el': 'Πρωτογενής',
    },
    'Secondaria': {
        'en': 'Secondary', 'de': 'Sekundär', 'es': 'Secundaria', 'fr': 'Secondaire',
        'ar': 'ثانوي', 'ca': 'Secundària', 'ro': 'Secundară', 'pt': 'Secundária', 'el': 'Δευτερογενής',
    },
}

TOMBA_TIPO_SEPOLTURA = {
    'Fossa semplice': {
        'en': 'Simple pit', 'de': 'Einfache Grube', 'es': 'Fosa simple',
        'fr': 'Fosse simple', 'ar': 'حفرة بسيطة', 'ca': 'Fossa simple',
        'ro': 'Groapă simplă', 'pt': 'Fossa simples', 'el': 'Απλός λάκκος',
    },
    'Fossa con copertura in laterizi': {
        'en': 'Pit with brick cover', 'de': 'Grube mit Ziegelabdeckung',
        'es': 'Fosa con cubierta de ladrillos', 'fr': 'Fosse avec couverture en briques',
        'ar': 'حفرة بغطاء من الآجر', 'ca': 'Fossa amb coberta de maons',
        'ro': 'Groapă cu acoperire din cărămizi', 'pt': 'Fossa com cobertura de tijolos',
        'el': 'Λάκκος με κάλυψη πλίνθων',
    },
    'Fossa con copertura in tegole': {
        'en': 'Pit with tile cover', 'de': 'Grube mit Ziegelplattenabdeckung',
        'es': 'Fosa con cubierta de tejas', 'fr': 'Fosse avec couverture en tuiles',
        'ar': 'حفرة بغطاء من القرميد', 'ca': 'Fossa amb coberta de teules',
        'ro': 'Groapă cu acoperire din țigle', 'pt': 'Fossa com cobertura de telhas',
        'el': 'Λάκκος με κάλυψη κεράμων',
    },
    'Cassa in laterizi': {
        'en': 'Brick coffin', 'de': 'Ziegelkiste', 'es': 'Caja de ladrillos',
        'fr': 'Caisson en briques', 'ar': 'صندوق من الآجر', 'ca': 'Caixa de maons',
        'ro': 'Ladă din cărămizi', 'pt': 'Caixa de tijolos', 'el': 'Κιβώτιο πλίνθων',
    },
}

TOMBA_COPERTURA_TIPO = {
    'Laterizi': {
        'en': 'Bricks', 'de': 'Ziegel', 'es': 'Ladrillos', 'fr': 'Briques',
        'ar': 'آجر', 'ca': 'Maons', 'ro': 'Cărămizi', 'pt': 'Tijolos', 'el': 'Πλίνθοι',
    },
    'Tegole': {
        'en': 'Tiles', 'de': 'Dachziegel', 'es': 'Tejas', 'fr': 'Tuiles',
        'ar': 'قرميد', 'ca': 'Teules', 'ro': 'Țigle', 'pt': 'Telhas', 'el': 'Κέραμοι',
    },
    'Nuda terra': {
        'en': 'Bare earth', 'de': 'Nackte Erde', 'es': 'Tierra desnuda',
        'fr': 'Terre nue', 'ar': 'تربة عارية', 'ca': 'Terra nua',
        'ro': 'Pământ gol', 'pt': 'Terra nua', 'el': 'Γυμνό χώμα',
    },
}

TOMBA_CONTENITORE = {
    'Fossa terragna': {
        'en': 'Earth pit', 'de': 'Erdgrube', 'es': 'Fosa de tierra',
        'fr': 'Fosse en terre', 'ar': 'حفرة ترابية', 'ca': 'Fossa de terra',
        'ro': 'Groapă de pământ', 'pt': 'Fossa de terra', 'el': 'Χωμάτινος λάκκος',
    },
    'Cassa in laterizi': {
        'en': 'Brick coffin', 'de': 'Ziegelkiste', 'es': 'Caja de ladrillos',
        'fr': 'Caisson en briques', 'ar': 'صندوق من الآجر', 'ca': 'Caixa de maons',
        'ro': 'Ladă din cărămizi', 'pt': 'Caixa de tijolos', 'el': 'Κιβώτιο πλίνθων',
    },
}

TOMBA_SEGNACOLI = {
    'Nessuno': {
        'en': 'None', 'de': 'Keine', 'es': 'Ninguno', 'fr': 'Aucun',
        'ar': 'لا يوجد', 'ca': 'Cap', 'ro': 'Niciunul', 'pt': 'Nenhum', 'el': 'Κανένα',
    },
    'Presente': {
        'en': 'Present', 'de': 'Vorhanden', 'es': 'Presente', 'fr': 'Présent',
        'ar': 'موجود', 'ca': 'Present', 'ro': 'Prezent', 'pt': 'Presente', 'el': 'Παρόν',
    },
}

# ---------------------------------------------------------------------------
# Individui field translations
# ---------------------------------------------------------------------------
INDIVIDUI_SESSO = {
    'Maschio': {
        'en': 'Male', 'de': 'Männlich', 'es': 'Masculino', 'fr': 'Masculin',
        'ar': 'ذكر', 'ca': 'Masculí', 'ro': 'Masculin', 'pt': 'Masculino', 'el': 'Αρσενικό',
    },
    'Femmina': {
        'en': 'Female', 'de': 'Weiblich', 'es': 'Femenino', 'fr': 'Féminin',
        'ar': 'أنثى', 'ca': 'Femení', 'ro': 'Feminin', 'pt': 'Feminino', 'el': 'Θηλυκό',
    },
    'Indeterminato': {
        'en': 'Indeterminate', 'de': 'Unbestimmt', 'es': 'Indeterminado',
        'fr': 'Indéterminé', 'ar': 'غير محدد', 'ca': 'Indeterminat',
        'ro': 'Nedeterminat', 'pt': 'Indeterminado', 'el': 'Αδιευκρίνιστο',
    },
}

INDIVIDUI_CLASSI_ETA = {
    'Adulto': {
        'en': 'Adult', 'de': 'Erwachsener', 'es': 'Adulto', 'fr': 'Adulte',
        'ar': 'بالغ', 'ca': 'Adult', 'ro': 'Adult', 'pt': 'Adulto', 'el': 'Ενήλικας',
    },
    'Giovane adulto': {
        'en': 'Young adult', 'de': 'Junger Erwachsener', 'es': 'Adulto joven',
        'fr': 'Jeune adulte', 'ar': 'شاب بالغ', 'ca': 'Adult jove',
        'ro': 'Adult tânăr', 'pt': 'Adulto jovem', 'el': 'Νεαρός ενήλικας',
    },
    'Subadulto': {
        'en': 'Subadult', 'de': 'Subadult', 'es': 'Subadulto', 'fr': 'Subadulte',
        'ar': 'يافع', 'ca': 'Subadult', 'ro': 'Subadult', 'pt': 'Subadulto', 'el': 'Υποενήλικας',
    },
    'Infante': {
        'en': 'Infant', 'de': 'Säugling', 'es': 'Infante', 'fr': 'Nourrisson',
        'ar': 'رضيع', 'ca': 'Infant', 'ro': 'Sugar', 'pt': 'Infante', 'el': 'Βρέφος',
    },
    'Bambino': {
        'en': 'Child', 'de': 'Kind', 'es': 'Niño', 'fr': 'Enfant',
        'ar': 'طفل', 'ca': 'Nen', 'ro': 'Copil', 'pt': 'Criança', 'el': 'Παιδί',
    },
    'Anziano': {
        'en': 'Elderly', 'de': 'Älterer', 'es': 'Anciano', 'fr': 'Âgé',
        'ar': 'مسن', 'ca': 'Ancià', 'ro': 'Vârstnic', 'pt': 'Idoso', 'el': 'Ηλικιωμένος',
    },
}

INDIVIDUI_POSIZIONE_SCHELETRO = {
    'Supino': {
        'en': 'Supine', 'de': 'Rückenlage', 'es': 'Supino', 'fr': 'Supine',
        'ar': 'مستلقي', 'ca': 'Supí', 'ro': 'Pe spate', 'pt': 'Supino', 'el': 'Ύπτια',
    },
    'Prono': {
        'en': 'Prone', 'de': 'Bauchlage', 'es': 'Prono', 'fr': 'Prone',
        'ar': 'منبطح', 'ca': 'Pron', 'ro': 'Pe burtă', 'pt': 'Prono', 'el': 'Πρηνής',
    },
    'Laterale destro': {
        'en': 'Right lateral', 'de': 'Rechte Seitenlage', 'es': 'Lateral derecho',
        'fr': 'Latéral droit', 'ar': 'جانب أيمن', 'ca': 'Lateral dret',
        'ro': 'Lateral drept', 'pt': 'Lateral direito', 'el': 'Δεξιά πλευρά',
    },
    'Laterale sinistro': {
        'en': 'Left lateral', 'de': 'Linke Seitenlage', 'es': 'Lateral izquierdo',
        'fr': 'Latéral gauche', 'ar': 'جانب أيسر', 'ca': 'Lateral esquerre',
        'ro': 'Lateral stâng', 'pt': 'Lateral esquerdo', 'el': 'Αριστερή πλευρά',
    },
}

INDIVIDUI_POSIZIONE_CRANIO = {
    'Volto a destra': {
        'en': 'Facing right', 'de': 'Nach rechts blickend', 'es': 'Mirando a la derecha',
        'fr': 'Tourné à droite', 'ar': 'وجه لليمين', 'ca': 'Mirant a la dreta',
        'ro': 'Cu fața la dreapta', 'pt': 'Virado à direita', 'el': 'Στραμμένο δεξιά',
    },
    'Volto a sinistra': {
        'en': 'Facing left', 'de': 'Nach links blickend', 'es': 'Mirando a la izquierda',
        'fr': 'Tourné à gauche', 'ar': 'وجه لليسار', 'ca': 'Mirant a la esquerra',
        'ro': 'Cu fața la stânga', 'pt': 'Virado à esquerda', 'el': 'Στραμμένο αριστερά',
    },
    'Volto in alto': {
        'en': 'Facing up', 'de': 'Nach oben blickend', 'es': 'Mirando hacia arriba',
        'fr': 'Tourné vers le haut', 'ar': 'وجه للأعلى', 'ca': 'Mirant amunt',
        'ro': 'Cu fața în sus', 'pt': 'Virado para cima', 'el': 'Στραμμένο πάνω',
    },
    'Volto in basso': {
        'en': 'Facing down', 'de': 'Nach unten blickend', 'es': 'Mirando hacia abajo',
        'fr': 'Tourné vers le bas', 'ar': 'وجه للأسفل', 'ca': 'Mirant avall',
        'ro': 'Cu fața în jos', 'pt': 'Virado para baixo', 'el': 'Στραμμένο κάτω',
    },
}

INDIVIDUI_POSIZIONE_ARTI_SUP = {
    'Distesi lungo i fianchi': {
        'en': 'Extended along flanks', 'de': 'Seitlich ausgestreckt',
        'es': 'Extendidos a los lados', 'fr': 'Étendus le long des flancs',
        'ar': 'ممتدان على الجانبين', 'ca': 'Estesos als costats',
        'ro': 'Întinse de-a lungul corpului', 'pt': 'Estendidos ao longo do corpo',
        'el': 'Τεντωμένα στα πλάγια',
    },
    'Incrociati sul petto': {
        'en': 'Crossed on chest', 'de': 'Über der Brust gekreuzt',
        'es': 'Cruzados sobre el pecho', 'fr': 'Croisés sur la poitrine',
        'ar': 'متقاطعان على الصدر', 'ca': 'Creuats sobre el pit',
        'ro': 'Încrucișate pe piept', 'pt': 'Cruzados sobre o peito',
        'el': 'Σταυρωμένα στο στήθος',
    },
    'Incrociati sul bacino': {
        'en': 'Crossed on pelvis', 'de': 'Über dem Becken gekreuzt',
        'es': 'Cruzados sobre la pelvis', 'fr': 'Croisés sur le bassin',
        'ar': 'متقاطعان على الحوض', 'ca': 'Creuats sobre la pelvis',
        'ro': 'Încrucișate pe bazin', 'pt': 'Cruzados sobre a pélvis',
        'el': 'Σταυρωμένα στη λεκάνη',
    },
}

INDIVIDUI_POSIZIONE_ARTI_INF = {
    'Distesi': {
        'en': 'Extended', 'de': 'Ausgestreckt', 'es': 'Extendidos', 'fr': 'Étendus',
        'ar': 'ممتدان', 'ca': 'Estesos', 'ro': 'Întinse', 'pt': 'Estendidos', 'el': 'Τεντωμένα',
    },
    'Flessi a destra': {
        'en': 'Flexed right', 'de': 'Rechts angewinkelt', 'es': 'Flexionados a la derecha',
        'fr': 'Fléchis à droite', 'ar': 'مثنيان لليمين', 'ca': 'Flexionats a la dreta',
        'ro': 'Flexate la dreapta', 'pt': 'Fletidos à direita', 'el': 'Λυγισμένα δεξιά',
    },
    'Flessi a sinistra': {
        'en': 'Flexed left', 'de': 'Links angewinkelt', 'es': 'Flexionados a la izquierda',
        'fr': 'Fléchis à gauche', 'ar': 'مثنيان لليسار', 'ca': 'Flexionats a la esquerra',
        'ro': 'Flexate la stânga', 'pt': 'Fletidos à esquerda', 'el': 'Λυγισμένα αριστερά',
    },
}

# ---------------------------------------------------------------------------
# Pottery field translations
# ---------------------------------------------------------------------------
POTTERY_WARE = {
    'Maiolica': {
        'en': 'Majolica', 'de': 'Majolika', 'es': 'Mayólica', 'fr': 'Majolique',
        'ar': 'خزف مزجج', 'ca': 'Majòlica', 'ro': 'Maiolică', 'pt': 'Majólica', 'el': 'Μαγιόλικα',
    },
    'Invetriata': {
        'en': 'Glazed', 'de': 'Glasiert', 'es': 'Vidriada', 'fr': 'Vernissée',
        'ar': 'مزججة', 'ca': 'Vidriada', 'ro': 'Smălțuită', 'pt': 'Vidrada', 'el': 'Εφυαλωμένη',
    },
    'Grezza': {
        'en': 'Coarse', 'de': 'Grobkeramik', 'es': 'Tosca', 'fr': 'Grossière',
        'ar': 'خشنة', 'ca': 'Grollera', 'ro': 'Grosieră', 'pt': 'Grosseira', 'el': 'Χονδροειδής',
    },
    'Ingobbiata': {
        'en': 'Slipped', 'de': 'Engobiert', 'es': 'Engobada', 'fr': 'Engobée',
        'ar': 'مطلية', 'ca': 'Engalbada', 'ro': 'Angobată', 'pt': 'Engobada', 'el': 'Επιχρισμένη',
    },
}

POTTERY_FORM = {
    'Ciotola': {
        'en': 'Bowl', 'de': 'Schale', 'es': 'Cuenco', 'fr': 'Bol',
        'ar': 'وعاء', 'ca': 'Bol', 'ro': 'Bol', 'pt': 'Tigela', 'el': 'Λεκάνη',
    },
    'Brocca': {
        'en': 'Jug', 'de': 'Krug', 'es': 'Jarra', 'fr': 'Cruche',
        'ar': 'إبريق', 'ca': 'Gerra', 'ro': 'Ulcior', 'pt': 'Jarro', 'el': 'Κανάτα',
    },
    'Piatto': {
        'en': 'Plate', 'de': 'Teller', 'es': 'Plato', 'fr': 'Assiette',
        'ar': 'صحن', 'ca': 'Plat', 'ro': 'Farfurie', 'pt': 'Prato', 'el': 'Πιάτο',
    },
    'Olla': {
        'en': 'Pot', 'de': 'Topf', 'es': 'Olla', 'fr': 'Marmite',
        'ar': 'قدر', 'ca': 'Olla', 'ro': 'Oală', 'pt': 'Panela', 'el': 'Χύτρα',
    },
    'Bacino': {
        'en': 'Basin', 'de': 'Becken', 'es': 'Bacín', 'fr': 'Bassin',
        'ar': 'حوض', 'ca': 'Bacina', 'ro': 'Bazin', 'pt': 'Bacia', 'el': 'Λεκάνη',
    },
    'Scodella': {
        'en': 'Dish', 'de': 'Schüssel', 'es': 'Escudilla', 'fr': 'Écuelle',
        'ar': 'صحن عميق', 'ca': 'Escudella', 'ro': 'Castron', 'pt': 'Malga', 'el': 'Πινάκιο',
    },
    'Tazza': {
        'en': 'Cup', 'de': 'Tasse', 'es': 'Taza', 'fr': 'Tasse',
        'ar': 'كأس', 'ca': 'Tassa', 'ro': 'Ceașcă', 'pt': 'Chávena', 'el': 'Φλιτζάνι',
    },
    'Orciolo': {
        'en': 'Small jug', 'de': 'Kännchen', 'es': 'Orcita', 'fr': 'Petit pot',
        'ar': 'جرة صغيرة', 'ca': 'Orçola', 'ro': 'Ulcioraș', 'pt': 'Púcaro', 'el': 'Αρυβαλλίσκος',
    },
}

POTTERY_MATERIAL = {
    'Ceramica': {
        'en': 'Ceramic', 'de': 'Keramik', 'es': 'Cerámica', 'fr': 'Céramique',
        'ar': 'خزف', 'ca': 'Ceràmica', 'ro': 'Ceramică', 'pt': 'Cerâmica', 'el': 'Κεραμική',
    },
    'Terracotta': {
        'en': 'Terracotta', 'de': 'Terrakotta', 'es': 'Terracota', 'fr': 'Terre cuite',
        'ar': 'فخار', 'ca': 'Terracuita', 'ro': 'Teracotă', 'pt': 'Terracota', 'el': 'Τερακότα',
    },
}

POTTERY_SURF_TRAT = {
    'Invetriatura': {
        'en': 'Glazing', 'de': 'Glasur', 'es': 'Vidriado', 'fr': 'Vernissage',
        'ar': 'تزجيج', 'ca': 'Vidriat', 'ro': 'Smălțuire', 'pt': 'Vidramento', 'el': 'Εφυάλωση',
    },
    'Ingobbiatura': {
        'en': 'Slipping', 'de': 'Engobe', 'es': 'Engobado', 'fr': 'Engobage',
        'ar': 'طلاء', 'ca': 'Engalbat', 'ro': 'Angobaj', 'pt': 'Engobe', 'el': 'Επίχριση',
    },
    'Nessuno': {
        'en': 'None', 'de': 'Keine', 'es': 'Ninguno', 'fr': 'Aucun',
        'ar': 'لا يوجد', 'ca': 'Cap', 'ro': 'Niciunul', 'pt': 'Nenhum', 'el': 'Κανένα',
    },
}

# ---------------------------------------------------------------------------
# Inventario materiali field translations
# ---------------------------------------------------------------------------
INVENTARIO_TIPO_REPERTO = {
    'Ceramica': {
        'en': 'Ceramic', 'de': 'Keramik', 'es': 'Cerámica', 'fr': 'Céramique',
        'ar': 'خزف', 'ca': 'Ceràmica', 'ro': 'Ceramică', 'pt': 'Cerâmica', 'el': 'Κεραμική',
    },
    'Metallo': {
        'en': 'Metal', 'de': 'Metall', 'es': 'Metal', 'fr': 'Métal',
        'ar': 'معدن', 'ca': 'Metall', 'ro': 'Metal', 'pt': 'Metal', 'el': 'Μέταλλο',
    },
    'Vetro': {
        'en': 'Glass', 'de': 'Glas', 'es': 'Vidrio', 'fr': 'Verre',
        'ar': 'زجاج', 'ca': 'Vidre', 'ro': 'Sticlă', 'pt': 'Vidro', 'el': 'Γυαλί',
    },
    'Osso': {
        'en': 'Bone', 'de': 'Knochen', 'es': 'Hueso', 'fr': 'Os',
        'ar': 'عظم', 'ca': 'Os', 'ro': 'Os', 'pt': 'Osso', 'el': 'Οστό',
    },
    'Moneta': {
        'en': 'Coin', 'de': 'Münze', 'es': 'Moneda', 'fr': 'Monnaie',
        'ar': 'عملة', 'ca': 'Moneda', 'ro': 'Monedă', 'pt': 'Moeda', 'el': 'Νόμισμα',
    },
    'Laterizio': {
        'en': 'Brick', 'de': 'Ziegel', 'es': 'Ladrillo', 'fr': 'Brique',
        'ar': 'آجر', 'ca': 'Maó', 'ro': 'Cărămidă', 'pt': 'Tijolo', 'el': 'Τούβλο',
    },
}

INVENTARIO_DEFINIZIONE = {
    'Frammento di ciotola': {
        'en': 'Bowl fragment', 'de': 'Schalenfragment', 'es': 'Fragmento de cuenco',
        'fr': 'Fragment de bol', 'ar': 'شظية وعاء', 'ca': 'Fragment de bol',
        'ro': 'Fragment de bol', 'pt': 'Fragmento de tigela', 'el': 'Θραύσμα λεκάνης',
    },
    'Chiodo in ferro': {
        'en': 'Iron nail', 'de': 'Eisennagel', 'es': 'Clavo de hierro',
        'fr': 'Clou en fer', 'ar': 'مسمار حديدي', 'ca': 'Clau de ferro',
        'ro': 'Cui de fier', 'pt': 'Prego de ferro', 'el': 'Σιδερένιο καρφί',
    },
    'Frammento di vetro': {
        'en': 'Glass fragment', 'de': 'Glasfragment', 'es': 'Fragmento de vidrio',
        'fr': 'Fragment de verre', 'ar': 'شظية زجاج', 'ca': 'Fragment de vidre',
        'ro': 'Fragment de sticlă', 'pt': 'Fragmento de vidro', 'el': 'Θραύσμα γυαλιού',
    },
    'Frammento di osso lavorato': {
        'en': 'Worked bone fragment', 'de': 'Bearbeitetes Knochenfragment',
        'es': 'Fragmento de hueso trabajado', 'fr': "Fragment d'os travaillé",
        'ar': 'شظية عظم مشغول', 'ca': "Fragment d'os treballat",
        'ro': 'Fragment de os prelucrat', 'pt': 'Fragmento de osso trabalhado',
        'el': 'Θραύσμα κατεργασμένου οστού',
    },
    'Moneta in bronzo': {
        'en': 'Bronze coin', 'de': 'Bronzemünze', 'es': 'Moneda de bronce',
        'fr': 'Monnaie en bronze', 'ar': 'عملة برونزية', 'ca': 'Moneda de bronze',
        'ro': 'Monedă de bronz', 'pt': 'Moeda de bronze', 'el': 'Χάλκινο νόμισμα',
    },
    'Frammento di piatto': {
        'en': 'Plate fragment', 'de': 'Tellerfragment', 'es': 'Fragmento de plato',
        'fr': "Fragment d'assiette", 'ar': 'شظية صحن', 'ca': 'Fragment de plat',
        'ro': 'Fragment de farfurie', 'pt': 'Fragmento de prato', 'el': 'Θραύσμα πιάτου',
    },
    'Frammento di laterizio': {
        'en': 'Brick fragment', 'de': 'Ziegelfragment', 'es': 'Fragmento de ladrillo',
        'fr': 'Fragment de brique', 'ar': 'شظية آجر', 'ca': 'Fragment de maó',
        'ro': 'Fragment de cărămidă', 'pt': 'Fragmento de tijolo', 'el': 'Θραύσμα πλίνθου',
    },
    'Fibbia in bronzo': {
        'en': 'Bronze buckle', 'de': 'Bronzeschnalle', 'es': 'Hebilla de bronce',
        'fr': 'Boucle en bronze', 'ar': 'إبزيم برونزي', 'ca': 'Sivella de bronze',
        'ro': 'Cataramă de bronz', 'pt': 'Fivela de bronze', 'el': 'Χάλκινη πόρπη',
    },
    'Frammento di brocca': {
        'en': 'Jug fragment', 'de': 'Krugfragment', 'es': 'Fragmento de jarra',
        'fr': 'Fragment de cruche', 'ar': 'شظية إبريق', 'ca': 'Fragment de gerra',
        'ro': 'Fragment de ulcior', 'pt': 'Fragmento de jarro', 'el': 'Θραύσμα κανάτας',
    },
    'Frammento di bicchiere': {
        'en': 'Drinking glass fragment', 'de': 'Trinkglasfragment',
        'es': 'Fragmento de vaso', 'fr': 'Fragment de verre à boire',
        'ar': 'شظية كأس', 'ca': 'Fragment de got',
        'ro': 'Fragment de pahar', 'pt': 'Fragmento de copo', 'el': 'Θραύσμα ποτηριού',
    },
}

INVENTARIO_CRITERIO = {
    'Per classe': {
        'en': 'By class', 'de': 'Nach Klasse', 'es': 'Por clase', 'fr': 'Par classe',
        'ar': 'حسب الفئة', 'ca': 'Per classe', 'ro': 'Pe clasă', 'pt': 'Por classe', 'el': 'Κατά κατηγορία',
    },
    'Per reperto singolo': {
        'en': 'By single find', 'de': 'Nach Einzelfund', 'es': 'Por hallazgo individual',
        'fr': 'Par objet individuel', 'ar': 'حسب القطعة', 'ca': 'Per objecte individual',
        'ro': 'Pe obiect individual', 'pt': 'Por achado individual', 'el': 'Κατά μεμονωμένο εύρημα',
    },
}

# Extra period descriptions needed for new tables
PERIOD_DESC_EXTRA = {
    'XIII secolo - XIV secolo': {
        'en': '13th-14th century', 'de': '13.-14. Jahrhundert',
        'es': 'Siglo XIII-XIV', 'fr': 'XIIIe-XIVe siècle',
        'ar': 'القرن 13-14', 'ca': 'Segle XIII-XIV',
        'ro': 'Secolul XIII-XIV', 'pt': 'Século XIII-XIV', 'el': '13ος-14ος αιώνας',
    },
    'XV secolo - XVI secolo': {
        'en': '15th-16th century', 'de': '15.-16. Jahrhundert',
        'es': 'Siglo XV-XVI', 'fr': 'XVe-XVIe siècle',
        'ar': 'القرن 15-16', 'ca': 'Segle XV-XVI',
        'ro': 'Secolul XV-XVI', 'pt': 'Século XV-XVI', 'el': '15ος-16ος αιώνας',
    },
    'XIV secolo': {
        'en': '14th century', 'de': '14. Jahrhundert',
        'es': 'Siglo XIV', 'fr': 'XIVe siècle',
        'ar': 'القرن الرابع عشر', 'ca': 'Segle XIV',
        'ro': 'Secolul XIV', 'pt': 'Século XIV', 'el': '14ος αιώνας',
    },
    'XIV-XV secolo': {
        'en': '14th-15th century', 'de': '14.-15. Jahrhundert',
        'es': 'Siglo XIV-XV', 'fr': 'XIVe-XVe siècle',
        'ar': 'القرن 14-15', 'ca': 'Segle XIV-XV',
        'ro': 'Secolul XIV-XV', 'pt': 'Século XIV-XV', 'el': '14ος-15ος αιώνας',
    },
}


# ---------------------------------------------------------------------------
# Helper functions for additional table translations
# ---------------------------------------------------------------------------

def translate_struttura_rel_term(term, lang):
    """Translate structure relationship term, checking extra dict first."""
    extra = STRUTTURA_RAPPORTI_EXTRA.get(term, {}).get(lang)
    if extra:
        return extra
    return translate_rel_term(term, lang)


def translate_struttura_materiali(items, lang):
    """Translate materiali_impiegati list: [['Ciottoli'], ['Laterizio'], ...]"""
    result = []
    for item in items:
        if isinstance(item, list) and len(item) >= 1:
            translated = INCLUSI.get(item[0], {}).get(lang, item[0])
            result.append([translated] + item[1:])
        else:
            result.append(item)
    return result


def translate_struttura_elementi(items, lang):
    """Translate elementi_strutturali: [['Tramezzo interno', '1'], ...]"""
    result = []
    for item in items:
        if isinstance(item, list) and len(item) >= 1:
            translated = STRUTTURA_ELEMENTI.get(item[0], {}).get(lang, item[0])
            result.append([translated] + item[1:])
        else:
            result.append(item)
    return result


def translate_struttura_rapporti(items, lang, new_site):
    """Translate rapporti_struttura: [['term', 'site', 'sigla', 'num'], ...]"""
    result = []
    for item in items:
        if isinstance(item, list) and len(item) >= 4:
            term = translate_struttura_rel_term(item[0], lang)
            # Replace site name
            site = new_site
            sigla = item[2]
            num = item[3]
            result.append([term, site, sigla, num])
        else:
            result.append(item)
    return result


def translate_datazione_ext(val, lang):
    """Translate datazione_estesa using both PERIOD_DESC and PERIOD_DESC_EXTRA."""
    if not val:
        return val
    tr = PERIOD_DESC.get(val, {}).get(lang)
    if tr:
        return tr
    tr = PERIOD_DESC_EXTRA.get(val, {}).get(lang)
    if tr:
        return tr
    return val


def translate_field(val, dict_map, lang):
    """Generic single-value field translation."""
    if not val:
        return val
    return dict_map.get(val, {}).get(lang, val)


# ---------------------------------------------------------------------------
# Insert Italian example data for sparse/empty tables
# ---------------------------------------------------------------------------

def insert_italian_example_data(conn):
    """Insert Italian example records for struttura, tomba, individui, pottery, inventario."""
    cur = conn.cursor()

    # Check if already run (FC 1 would exist)
    cur.execute("SELECT COUNT(*) FROM struttura_table WHERE sito = ? AND sigla_struttura = 'FC'",
                (IT_SITE,))
    if cur.fetchone()[0] > 0:
        print("Italian example data already inserted, skipping.")
        return

    print("\n--- Inserting Italian example data ---")

    # --- Struttura (9 new records) ---
    cur.execute("SELECT MAX(id_struttura) FROM struttura_table")
    next_id = (cur.fetchone()[0] or 0) + 1

    struttura_records = [
        # (sigla, numero, categoria, tipologia, definizione, descrizione,
        #  interpretazione, per_ini, fas_ini, per_fin, fas_fin, datazione_estesa,
        #  materiali, elementi, rapporti)
        ('ED', 2, 'Edificio', 'Edificio privato', 'Casa',
         'Edificio a pianta rettangolare realizzato in ciottoli e laterizi legati da malta. '
         'Conservato a livello di fondazione.',
         'Possibile abitazione del XIII-XIV secolo.',
         1, 1, 1, 3, 'XIII secolo - XIV secolo',
         repr([['Laterizio'], ['Ciottoli'], ['Malta']]),
         repr([['Muro perimetrale', '2'], ['Pavimento', '1']]),
         repr([['Gli si appoggia', IT_SITE, 'ED', '1']])),
        ('FC', 1, 'Focolare', 'Focolare domestico', 'Focolare',
         'Focolare in muratura di forma circolare, con piano di fuoco in laterizi.',
         'Focolare domestico per la cottura dei cibi.',
         2, 2, 2, 3, 'XV secolo',
         repr([['Laterizio'], ['Terra']]),
         repr([]),
         repr([['Fa parte di', IT_SITE, 'ED', '1']])),
        ('MR', 1, 'Muro', 'Muro perimetrale', 'Muro perimetrale',
         'Muro perimetrale in laterizi di reimpiego legati da malta, conservato per 3 filari.',
         'Muro perimetrale est dell\'edificio ED 1.',
         2, 1, 2, 4, 'XV secolo - XVI secolo',
         repr([['Laterizio'], ['Calce'], ['Malta']]),
         repr([]),
         repr([['Fa parte di', IT_SITE, 'ED', '1']])),
        ('MR', 2, 'Muro', 'Muro interno', 'Muro interno',
         'Muro interno in laterizi legati da malta, conservato per 2 filari.',
         'Muro interno che divide i due ambienti dell\'edificio ED 1.',
         2, 2, 2, 3, 'XV secolo',
         repr([['Laterizio'], ['Malta']]),
         repr([]),
         repr([['Si lega a', IT_SITE, 'MR', '1']])),
        ('MR', 3, 'Muro', 'Tramezzo', 'Tramezzo',
         'Tramezzo in laterizi e terra, conservato per 1 filare.',
         'Tramezzo interno dell\'edificio ED 2.',
         1, 1, 1, 3, 'XIII secolo - XIV secolo',
         repr([['Laterizio'], ['Terra']]),
         repr([]),
         repr([['Si appoggia a', IT_SITE, 'MR', '1']])),
        ('PV', 1, 'Pavimentazione', 'Pavimentazione in terra', 'Pavimento',
         'Pavimentazione in terra battuta di colore marrone scuro, spessore 5-8 cm.',
         'Piano pavimentale in terra battuta dell\'edificio ED 1.',
         2, 1, 2, 4, 'XV secolo - XVI secolo',
         repr([['Terra'], ['Sabbia']]),
         repr([]),
         repr([['Fa parte di', IT_SITE, 'ED', '1']])),
        ('PV', 2, 'Pavimentazione', 'Pavimentazione in terra', 'Pavimento',
         'Pavimentazione in terra battuta di colore marrone chiaro, spessore 4-6 cm.',
         'Piano pavimentale in terra battuta dell\'edificio ED 2.',
         2, 2, 2, 3, 'XV secolo',
         repr([['Terra'], ['Sabbia']]),
         repr([]),
         repr([['Fa parte di', IT_SITE, 'ED', '2']])),
        ('FO', 1, 'Fossa', 'Fossa', 'Fossa',
         'Fossa di forma irregolarmente circolare, diametro di circa 1.2 m, profondo circa 0.8 m. '
         'Riempimento di terra di colore marrone scuro con frammenti di ceramica.',
         'Fossa di scarico di epoca moderna.',
         3, 1, 3, 1, 'Età moderna',
         repr([]),
         repr([]),
         repr([])),
        ('SP', 1, 'Spoliazione', 'Fossa di spoliazione', 'Fossa di spoliazione',
         'Fossa di spoliazione che taglia il muro MR 1, larghezza 0.6 m.',
         'Fossa di spoliazione per il recupero di materiale edilizio.',
         1, 3, 2, 1, 'Fine XIV secolo',
         repr([]),
         repr([]),
         repr([['Taglia', IT_SITE, 'MR', '1']])),
    ]

    cols = ('id_struttura, sito, sigla_struttura, numero_struttura, '
            'categoria_struttura, tipologia_struttura, definizione_struttura, '
            'descrizione, interpretazione, periodo_iniziale, fase_iniziale, '
            'periodo_finale, fase_finale, datazione_estesa, materiali_impiegati, '
            'elementi_strutturali, rapporti_struttura, misure_struttura, entity_uuid')
    for rec in struttura_records:
        vals = (next_id, IT_SITE) + rec + (repr([[]]), str(uuid.uuid4()))
        cur.execute(f"INSERT INTO struttura_table ({cols}) VALUES "
                    f"({','.join(['?'] * 19)})", vals)
        next_id += 1
    print(f"  Inserted {len(struttura_records)} struttura records")

    # --- Update existing tomba to fill sparse fields ---
    cur.execute("""UPDATE tomba_table SET
        nr_individuo = '1', rito = 'Inumazione',
        descrizione_taf = 'Sepoltura in fossa semplice con inumato in posizione supina.',
        interpretazione_taf = 'Sepoltura individuale di epoca medievale.',
        segnacoli = 'Nessuno', canale_libatorio_si_no = 'No',
        stato_di_conservazione = 'Discreto',
        copertura_tipo = 'Nuda terra', tipo_contenitore_resti = 'Fossa terragna',
        tipo_deposizione = 'Primaria', tipo_sepoltura = 'Fossa semplice',
        corredo_presenza = 'No',
        periodo_iniziale = 1, fase_iniziale = 3,
        periodo_finale = 2, fase_finale = 1,
        datazione_estesa = 'XIV-XV secolo'
        WHERE sito = ? AND nr_scheda_taf = 1""", (IT_SITE,))

    # --- Tomba (9 new records, TB 1 already exists) ---
    cur.execute("SELECT MAX(id_tomba) FROM tomba_table")
    next_id = (cur.fetchone()[0] or 0) + 1

    # (nr_scheda, sigla_str, nr_str, nr_individuo, rito, desc, interp, segnacoli,
    #  canale, stato, copertura, contenitore, deposizione, sepoltura,
    #  corredo_pres, corr_tipo, corr_desc, per_ini, fas_ini, per_fin, fas_fin, datazione)
    tomba_records = [
        (2, 'ED', 2, '2', 'Inumazione',
         'Sepoltura in fossa semplice con inumato in posizione supina, orientamento E-W.',
         'Sepoltura individuale di adulto.',
         'Nessuno', 'No', 'Buono', 'Nuda terra', 'Fossa terragna',
         'Primaria', 'Fossa semplice', 'No', repr([]), '',
         1, 3, 2, 1, 'XIV-XV secolo'),
        (3, 'ED', 1, '3', 'Inumazione',
         'Sepoltura in fossa semplice con inumato in posizione supina, orientamento W-E.',
         'Sepoltura individuale di giovane adulto.',
         'Nessuno', 'No', 'Buono', 'Nuda terra', 'Fossa terragna',
         'Primaria', 'Fossa semplice', 'Si', repr([['Chiodo in ferro', '3']]),
         'Tre chiodi in ferro presso il cranio.',
         2, 2, 2, 3, 'XV secolo'),
        (4, 'ED', 1, '4', 'Inumazione',
         'Sepoltura in fossa semplice con inumato in posizione supina.',
         'Sepoltura individuale di adulto di sesso femminile.',
         'Nessuno', 'No', 'Discreto', 'Nuda terra', 'Fossa terragna',
         'Primaria', 'Fossa semplice', 'No', repr([]), '',
         1, 1, 1, 3, 'XIV secolo'),
        (5, 'ED', 2, '5', 'Inumazione',
         'Sepoltura in fossa semplice con resti in connessione parziale.',
         'Sepoltura individuale di subadulto.',
         'Nessuno', 'No', 'Scarso', 'Nuda terra', 'Fossa terragna',
         'Primaria', 'Fossa semplice', 'No', repr([]), '',
         2, 2, 2, 3, 'XV secolo'),
        (6, 'ED', 1, '6', 'Inumazione',
         'Sepoltura in fossa con copertura in laterizi, inumato supino, orientamento E-W.',
         'Sepoltura con copertura in laterizi di reimpiego.',
         'Nessuno', 'No', 'Buono', 'Laterizi', 'Fossa terragna',
         'Primaria', 'Fossa con copertura in laterizi', 'Si',
         repr([['Moneta in bronzo', '1']]),
         'Una moneta in bronzo presso la mano destra.',
         1, 1, 1, 3, 'XIV secolo'),
        (7, 'ED', 1, '7', 'Inumazione',
         'Sepoltura in fossa con copertura in tegole, inumato supino.',
         'Sepoltura con copertura in tegole.',
         'Nessuno', 'No', 'Buono', 'Tegole', 'Fossa terragna',
         'Primaria', 'Fossa con copertura in tegole', 'No', repr([]), '',
         2, 2, 2, 3, 'XV secolo'),
        (8, 'ED', 2, '8', 'Inumazione',
         'Sepoltura in cassa di laterizi, inumato supino, orientamento W-E.',
         'Sepoltura in cassa di laterizi di reimpiego.',
         'Nessuno', 'No', 'Ottimo', 'Laterizi', 'Cassa in laterizi',
         'Primaria', 'Cassa in laterizi', 'Si',
         repr([['Fibbia in bronzo', '1']]),
         'Fibbia in bronzo presso la cintura.',
         1, 1, 1, 3, 'XIV secolo'),
        (9, 'ED', 1, '9', 'Cremazione',
         'Sepoltura a cremazione in fossa semplice con resti combusti.',
         'Sepoltura a cremazione individuale.',
         'Nessuno', 'No', 'Discreto', 'Nuda terra', 'Fossa terragna',
         'Secondaria', 'Fossa semplice', 'No', repr([]), '',
         1, 1, 1, 3, 'XIV secolo'),
        (10, 'ED', 2, '10', 'Inumazione',
         'Sepoltura in fossa semplice, inumato disturbato da interventi successivi.',
         'Sepoltura disturbata da attività post-deposizionali.',
         'Nessuno', 'No', 'Scarso', 'Nuda terra', 'Fossa terragna',
         'Primaria', 'Fossa semplice', 'No', repr([]), '',
         1, 3, 2, 1, 'XIV-XV secolo'),
    ]

    tomba_cols = ('id_tomba, sito, area, nr_scheda_taf, sigla_struttura, nr_struttura, '
                  'nr_individuo, rito, descrizione_taf, interpretazione_taf, segnacoli, '
                  'canale_libatorio_si_no, oggetti_rinvenuti_esterno, stato_di_conservazione, '
                  'copertura_tipo, tipo_contenitore_resti, tipo_deposizione, tipo_sepoltura, '
                  'corredo_presenza, corredo_tipo, corredo_descrizione, '
                  'periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, '
                  'datazione_estesa, entity_uuid')
    for rec in tomba_records:
        # rec[:9] = nr_scheda..canale, then insert '' for oggetti_rinvenuti_esterno,
        # then rec[9:] = stato..datazione
        vals = (next_id, IT_SITE, 2) + rec[:9] + ('',) + rec[9:] + (str(uuid.uuid4()),)
        cur.execute(f"INSERT INTO tomba_table ({tomba_cols}) VALUES "
                    f"({','.join(['?'] * 27)})", vals)
        next_id += 1
    print(f"  Inserted {len(tomba_records)} tomba records (+ updated TB 1)")

    # --- Update existing individuo to fill sparse fields ---
    cur.execute("""UPDATE individui_table SET
        data_schedatura = '2021-04-15', schedatore = 'Antropologo',
        sesso = 'Maschio', eta_min = 35, eta_max = 45, classi_eta = 'Adulto',
        osservazioni = 'Scheletro in buono stato di conservazione.',
        completo_si_no = 'Si', disturbato_si_no = 'No',
        in_connessione_si_no = 'Si', lunghezza_scheletro = 168.0,
        posizione_scheletro = 'Supino', posizione_cranio = 'Volto a destra',
        posizione_arti_superiori = 'Distesi lungo i fianchi',
        posizione_arti_inferiori = 'Distesi',
        orientamento_asse = 'E-W', orientamento_azimut = '90'
        WHERE sito = ? AND nr_individuo = 1""", (IT_SITE,))

    # --- Individui (9 new records) ---
    cur.execute("SELECT MAX(id_scheda_ind) FROM individui_table")
    next_id = (cur.fetchone()[0] or 0) + 1

    # (nr_individuo, area, us, sesso, eta_min, eta_max, classi_eta, osservazioni,
    #  sigla_str, nr_str, completo, disturbato, connessione, lunghezza,
    #  pos_scheletro, pos_cranio, pos_arti_sup, pos_arti_inf, orient_asse, orient_azimut)
    individui_records = [
        (2, '2', '42', 'Femmina', 25, 35, 'Giovane adulto',
         'Scheletro in buono stato, completo.',
         'ED', '2', 'Si', 'No', 'Si', 162.0,
         'Supino', 'Volto a sinistra', 'Incrociati sul petto', 'Distesi', 'E-W', '85'),
        (3, '2', '43', 'Maschio', 20, 30, 'Giovane adulto',
         'Scheletro completo con tracce di patologia sulle vertebre.',
         'ED', '1', 'Si', 'No', 'Si', 172.0,
         'Supino', 'Volto a destra', 'Distesi lungo i fianchi', 'Distesi', 'W-E', '270'),
        (4, '2', '44', 'Femmina', 30, 40, 'Adulto',
         'Scheletro parzialmente conservato.',
         'ED', '1', 'No', 'No', 'Si', 158.0,
         'Supino', 'Volto in alto', 'Distesi lungo i fianchi', 'Distesi', 'E-W', '90'),
        (5, '2', '45', 'Indeterminato', 5, 10, 'Bambino',
         'Resti scheletrici frammentari di subadulto.',
         'ED', '2', 'No', 'No', 'No', 0,
         'Supino', 'Volto a destra', 'Distesi lungo i fianchi', 'Distesi', 'E-W', '88'),
        (6, '2', '46', 'Maschio', 40, 50, 'Adulto',
         'Scheletro completo in ottimo stato di conservazione.',
         'ED', '1', 'Si', 'No', 'Si', 175.0,
         'Supino', 'Volto a sinistra', 'Incrociati sul bacino', 'Distesi', 'E-W', '92'),
        (7, '2', '47', 'Femmina', 35, 45, 'Adulto',
         'Scheletro completo.',
         'ED', '1', 'Si', 'No', 'Si', 160.0,
         'Supino', 'Volto in alto', 'Distesi lungo i fianchi', 'Distesi', 'W-E', '268'),
        (8, '2', '48', 'Maschio', 45, 55, 'Adulto',
         'Scheletro in ottimo stato di conservazione.',
         'ED', '2', 'Si', 'No', 'Si', 170.0,
         'Supino', 'Volto a destra', 'Incrociati sul petto', 'Distesi', 'W-E', '275'),
        (9, '2', '49', 'Indeterminato', 30, 50, 'Adulto',
         'Resti cremati frammentari.',
         'ED', '1', 'No', 'No', 'No', 0,
         '', '', '', '', '', ''),
        (10, '2', '50', 'Femmina', 25, 40, 'Adulto',
         'Scheletro disturbato da interventi successivi, parzialmente in connessione.',
         'ED', '2', 'No', 'Si', 'No', 155.0,
         'Supino', 'Volto in basso', 'Distesi lungo i fianchi', 'Flessi a destra', 'E-W', '95'),
    ]

    ind_cols = ('id_scheda_ind, sito, nr_individuo, area, us, '
                'data_schedatura, schedatore, sesso, eta_min, eta_max, classi_eta, '
                'osservazioni, sigla_struttura, nr_struttura, completo_si_no, '
                'disturbato_si_no, in_connessione_si_no, lunghezza_scheletro, '
                'posizione_scheletro, posizione_cranio, posizione_arti_superiori, '
                'posizione_arti_inferiori, orientamento_asse, orientamento_azimut, entity_uuid')
    for rec in individui_records:
        vals = (next_id, IT_SITE, rec[0], rec[1], rec[2],
                '2021-04-15', 'Antropologo',
                rec[3], rec[4], rec[5], rec[6], rec[7],
                rec[8], rec[9], rec[10], rec[11], rec[12], rec[13],
                rec[14], rec[15], rec[16], rec[17], rec[18], rec[19],
                str(uuid.uuid4()))
        cur.execute(f"INSERT INTO individui_table ({ind_cols}) VALUES "
                    f"({','.join(['?'] * 25)})", vals)
        next_id += 1
    print(f"  Inserted {len(individui_records)} individui records (+ updated IND 1)")

    # --- Pottery (10 records) ---
    cur.execute("SELECT MAX(id_rep) FROM pottery_table")
    max_id = cur.fetchone()[0]
    next_id = (max_id or 0) + 1

    # (id_number, area, us, material, form, ware, surf_trat, wheel_made,
    #  note, diametro_max, qty, datazione)
    pottery_records = [
        (1, '1', '3', 'Ceramica', 'Ciotola', 'Maiolica', 'Invetriatura', 'Si',
         'Frammento di orlo e parete, decorazione in blu.', 18.5, 3, 'XV secolo'),
        (2, '1', '4', 'Ceramica', 'Brocca', 'Invetriata', 'Invetriatura', 'Si',
         'Frammento di ansa e collo.', 12.0, 1, 'XV secolo'),
        (3, '1', '8', 'Ceramica', 'Piatto', 'Maiolica', 'Invetriatura', 'Si',
         'Frammento di fondo con piede ad anello.', 22.0, 2, 'XV secolo'),
        (4, '1', '10', 'Ceramica', 'Olla', 'Grezza', 'Nessuno', 'No',
         'Frammento di orlo estroflesso.', 16.0, 5, 'XIV secolo'),
        (5, '1', '11', 'Ceramica', 'Bacino', 'Ingobbiata', 'Ingobbiatura', 'Si',
         'Frammento di orlo e parete con ingobbio bianco.', 28.0, 2, 'XV secolo'),
        (6, '1', '15', 'Ceramica', 'Scodella', 'Maiolica', 'Invetriatura', 'Si',
         'Frammento di parete con decorazione geometrica.', 14.0, 1, 'XV secolo'),
        (7, '1', '18', 'Ceramica', 'Tazza', 'Invetriata', 'Invetriatura', 'Si',
         'Frammento di orlo e ansa.', 8.0, 1, 'XIV-XV secolo'),
        (8, '1', '22', 'Ceramica', 'Olla', 'Grezza', 'Nessuno', 'No',
         'Frammento di fondo piano.', 14.0, 3, 'XIV secolo'),
        (9, '1', '25', 'Ceramica', 'Piatto', 'Ingobbiata', 'Ingobbiatura', 'Si',
         'Frammento di orlo con ingobbio e graffito.', 20.0, 2, 'XV secolo'),
        (10, '1', '30', 'Ceramica', 'Orciolo', 'Grezza', 'Nessuno', 'No',
         'Frammento di collo stretto.', 10.0, 1, 'XIV secolo'),
    ]

    pot_cols = ('id_rep, id_number, sito, area, us, anno, '
                'material, form, ware, surf_trat, wheel_made, '
                'note, diametro_max, qty, datazione, entity_uuid')
    for rec in pottery_records:
        vals = (next_id, rec[0], IT_SITE, rec[1], rec[2], 2021,
                rec[3], rec[4], rec[5], rec[6], rec[7],
                rec[8], rec[9], rec[10], rec[11], str(uuid.uuid4()))
        cur.execute(f"INSERT INTO pottery_table ({pot_cols}) VALUES "
                    f"({','.join(['?'] * 16)})", vals)
        next_id += 1
    print(f"  Inserted {len(pottery_records)} pottery records")

    # --- Inventario materiali (10 records) ---
    cur.execute("SELECT MAX(id_invmat) FROM inventario_materiali_table")
    max_id = cur.fetchone()[0]
    next_id = (max_id or 0) + 1

    # (numero_inv, tipo_reperto, criterio, definizione, descrizione, area, us,
    #  lavato, stato_conservazione, datazione_reperto, repertato, diagnostico)
    inv_records = [
        (1, 'Ceramica', 'Per classe', 'Frammento di ciotola',
         'Frammento di ciotola in maiolica con decorazione in blu.',
         '1', '3', 'Si', 'Buono', 'XV secolo', 'Si', 'Si'),
        (2, 'Metallo', 'Per reperto singolo', 'Chiodo in ferro',
         'Chiodo in ferro a sezione quadrata, lunghezza 8 cm.',
         '1', '5', 'No', 'Discreto', 'XV secolo', 'Si', 'No'),
        (3, 'Vetro', 'Per classe', 'Frammento di vetro',
         'Frammento di vetro trasparente verdastro.',
         '1', '8', 'Si', 'Scarso', 'XV secolo', 'Si', 'No'),
        (4, 'Osso', 'Per reperto singolo', 'Frammento di osso lavorato',
         'Frammento di osso lavorato, possibile puntale.',
         '1', '10', 'Si', 'Buono', 'XIV secolo', 'Si', 'Si'),
        (5, 'Moneta', 'Per reperto singolo', 'Moneta in bronzo',
         'Moneta in bronzo, illeggibile, diametro 18 mm.',
         '1', '15', 'Si', 'Scarso', 'XIV-XV secolo', 'Si', 'Si'),
        (6, 'Ceramica', 'Per classe', 'Frammento di piatto',
         'Frammento di piatto in maiolica arcaica.',
         '1', '18', 'Si', 'Buono', 'XV secolo', 'Si', 'Si'),
        (7, 'Laterizio', 'Per classe', 'Frammento di laterizio',
         'Frammento di laterizio con tracce di malta.',
         '1', '22', 'No', 'Buono', '', 'No', 'No'),
        (8, 'Metallo', 'Per reperto singolo', 'Fibbia in bronzo',
         'Fibbia in bronzo a forma rettangolare.',
         '1', '25', 'Si', 'Discreto', 'XIV-XV secolo', 'Si', 'Si'),
        (9, 'Ceramica', 'Per classe', 'Frammento di brocca',
         'Frammento di brocca invetriata con ansa a nastro.',
         '1', '30', 'Si', 'Buono', 'XV secolo', 'Si', 'No'),
        (10, 'Vetro', 'Per classe', 'Frammento di bicchiere',
         'Frammento di bicchiere in vetro trasparente.',
         '1', '35', 'Si', 'Scarso', 'XV secolo', 'Si', 'No'),
    ]

    inv_cols = ('id_invmat, sito, numero_inventario, tipo_reperto, criterio_schedatura, '
                'definizione, descrizione, area, us, lavato, '
                'stato_conservazione, datazione_reperto, repertato, diagnostico, '
                'years, schedatore, date_scheda, entity_uuid')
    for rec in inv_records:
        vals = (next_id, IT_SITE, rec[0], rec[1], rec[2],
                rec[3], rec[4], rec[5], rec[6], rec[7],
                rec[8], rec[9], rec[10], rec[11],
                2021, 'Schedatore', '2021-04-15', str(uuid.uuid4()))
        cur.execute(f"INSERT INTO inventario_materiali_table ({inv_cols}) VALUES "
                    f"({','.join(['?'] * 18)})", vals)
        next_id += 1
    print(f"  Inserted {len(inv_records)} inventario materiali records")

    conn.commit()
    print("Italian example data insertion complete.")


# ---------------------------------------------------------------------------
# Main population logic
# ---------------------------------------------------------------------------

def get_column_names(cursor, table):
    """Get column names for a table."""
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def populate(db_path):
    """Populate the database with i18n example data."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # --- Insert Italian example data for sparse/empty tables ---
    insert_italian_example_data(conn)

    # --- Read existing Italian data ---
    # Get column names first (these use the cursor for PRAGMA queries)
    site_cols = get_column_names(cur, 'site_table')
    period_cols = get_column_names(cur, 'periodizzazione_table')
    us_cols = get_column_names(cur, 'us_table')
    struttura_cols = get_column_names(cur, 'struttura_table')
    tomba_cols = get_column_names(cur, 'tomba_table')
    individui_cols = get_column_names(cur, 'individui_table')
    pottery_cols = get_column_names(cur, 'pottery_table')
    invmat_cols = get_column_names(cur, 'inventario_materiali_table')
    gis_us_cols = get_column_names(cur, 'pyunitastratigrafiche')
    gis_usm_cols = get_column_names(cur, 'pyunitastratigrafiche_usm')
    gis_quote_cols = get_column_names(cur, 'pyarchinit_quote')

    # Now fetch data (each fetchone/fetchall must follow its SELECT immediately)
    cur.execute("SELECT * FROM site_table WHERE sito = ?", (IT_SITE,))
    site_row = cur.fetchone()
    if not site_row:
        print(f"ERROR: No site found with sito='{IT_SITE}'")
        return

    cur.execute("SELECT * FROM periodizzazione_table WHERE sito = ? ORDER BY id_perfas",
                (IT_SITE,))
    period_rows = cur.fetchall()

    cur.execute("SELECT * FROM us_table WHERE sito = ? ORDER BY id_us", (IT_SITE,))
    us_rows = cur.fetchall()

    # Read additional table data
    cur.execute("SELECT * FROM struttura_table WHERE sito = ? ORDER BY id_struttura", (IT_SITE,))
    struttura_rows = cur.fetchall()

    cur.execute("SELECT * FROM tomba_table WHERE sito = ? ORDER BY id_tomba", (IT_SITE,))
    tomba_rows = cur.fetchall()

    cur.execute("SELECT * FROM individui_table WHERE sito = ? ORDER BY id_scheda_ind", (IT_SITE,))
    individui_rows = cur.fetchall()

    cur.execute("SELECT * FROM pottery_table WHERE sito = ? ORDER BY id_rep", (IT_SITE,))
    pottery_rows = cur.fetchall()

    cur.execute("SELECT * FROM inventario_materiali_table WHERE sito = ? ORDER BY id_invmat",
                (IT_SITE,))
    invmat_rows = cur.fetchall()

    # GIS layers
    cur.execute("SELECT * FROM pyunitastratigrafiche WHERE scavo_s = ? ORDER BY gid", (IT_SITE,))
    gis_us_rows = cur.fetchall()

    cur.execute("SELECT * FROM pyunitastratigrafiche_usm WHERE scavo_s = ? ORDER BY gid",
                (IT_SITE,))
    gis_usm_rows = cur.fetchall()

    cur.execute("SELECT * FROM pyarchinit_quote WHERE sito_q = ? ORDER BY gid", (IT_SITE,))
    gis_quote_rows = cur.fetchall()

    print(f"Read Italian data: 1 site, {len(period_rows)} periods, {len(us_rows)} US records")
    print(f"  + {len(struttura_rows)} struttura, {len(tomba_rows)} tomba, "
          f"{len(individui_rows)} individui")
    print(f"  + {len(pottery_rows)} pottery, {len(invmat_rows)} inventario")
    print(f"  + {len(gis_us_rows)} GIS US, {len(gis_usm_rows)} GIS USM, "
          f"{len(gis_quote_rows)} GIS quote")

    # Build column index maps
    site_idx = {c: i for i, c in enumerate(site_cols)}
    period_idx = {c: i for i, c in enumerate(period_cols)}
    us_idx = {c: i for i, c in enumerate(us_cols)}
    struttura_idx = {c: i for i, c in enumerate(struttura_cols)}
    tomba_idx = {c: i for i, c in enumerate(tomba_cols)}
    individui_idx = {c: i for i, c in enumerate(individui_cols)}
    pottery_idx = {c: i for i, c in enumerate(pottery_cols)}
    invmat_idx = {c: i for i, c in enumerate(invmat_cols)}
    gis_us_idx = {c: i for i, c in enumerate(gis_us_cols)}
    gis_usm_idx = {c: i for i, c in enumerate(gis_usm_cols)}
    gis_quote_idx = {c: i for i, c in enumerate(gis_quote_cols)}

    # Get next IDs
    cur.execute("SELECT MAX(id_sito) FROM site_table")
    next_site_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(id_perfas) FROM periodizzazione_table")
    next_period_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(id_us) FROM us_table")
    next_us_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(id_struttura) FROM struttura_table")
    next_struttura_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(id_tomba) FROM tomba_table")
    next_tomba_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(id_scheda_ind) FROM individui_table")
    next_ind_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(id_rep) FROM pottery_table")
    next_pot_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(id_invmat) FROM inventario_materiali_table")
    next_inv_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(gid) FROM pyunitastratigrafiche")
    next_gis_us_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(gid) FROM pyunitastratigrafiche_usm")
    next_gis_usm_id = (cur.fetchone()[0] or 0) + 1
    cur.execute("SELECT MAX(gid) FROM pyarchinit_quote")
    next_gis_quote_id = (cur.fetchone()[0] or 0) + 1

    for lang in LANGS:
        new_site = SITE_NAMES[lang]
        print(f"\n--- {lang.upper()}: {new_site} ---")

        # Check if site/period/US already inserted
        cur.execute("SELECT COUNT(*) FROM site_table WHERE sito = ?", (new_site,))
        site_exists = cur.fetchone()[0] > 0

        if site_exists:
            print(f"  Site '{new_site}' already exists, skipping site/period/US")
        if not site_exists:
            # ---- Insert site ----
            site_data = list(site_row)
            site_data[site_idx['id_sito']] = next_site_id
            next_site_id += 1
            site_data[site_idx['sito']] = new_site
            site_data[site_idx['nazione']] = NAZIONE[lang]
            site_data[site_idx['descrizione']] = SITE_DESCRIZIONE[lang]
            site_data[site_idx['definizione_sito']] = DEFINIZIONE_SITO[lang]
            if 'entity_uuid' in site_idx:
                site_data[site_idx['entity_uuid']] = str(uuid.uuid4())

            placeholders = ', '.join(['?'] * len(site_cols))
            cur.execute(f"INSERT INTO site_table ({', '.join(site_cols)}) VALUES ({placeholders})",
                        site_data)
            print(f"  Inserted site: {new_site}")

            # ---- Insert periods ----
            for prow in period_rows:
                pdata = list(prow)
                pdata[period_idx['id_perfas']] = next_period_id
                next_period_id += 1
                pdata[period_idx['sito']] = new_site

                # Translate descrizione
                desc = pdata[period_idx['descrizione']]
                pdata[period_idx['descrizione']] = PERIOD_DESC.get(desc, {}).get(lang, desc)

                # Translate datazione_estesa
                dat = pdata[period_idx['datazione_estesa']]
                pdata[period_idx['datazione_estesa']] = PERIOD_DESC.get(dat, {}).get(lang, dat)

                if 'entity_uuid' in period_idx:
                    pdata[period_idx['entity_uuid']] = str(uuid.uuid4())

                cur.execute(
                    f"INSERT INTO periodizzazione_table ({', '.join(period_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(period_cols))})",
                    pdata)
            print(f"  Inserted {len(period_rows)} periods")

            # ---- Insert US records ----
            for urow in us_rows:
                udata = list(urow)
                udata[us_idx['id_us']] = next_us_id
                next_us_id += 1
                udata[us_idx['sito']] = new_site

                # Translate unita_tipo
                ut = udata[us_idx['unita_tipo']]
                udata[us_idx['unita_tipo']] = translate_unit_type(ut, lang)

                # Translate d_stratigrafica
                ds = udata[us_idx['d_stratigrafica']]
                udata[us_idx['d_stratigrafica']] = D_STRATIGRAFICA.get(ds, {}).get(lang, ds)

                # Translate d_interpretativa
                di = udata[us_idx['d_interpretativa']]
                udata[us_idx['d_interpretativa']] = translate_d_interpretativa(di, lang)

                # Translate descrizione (long text)
                desc = udata[us_idx['descrizione']]
                udata[us_idx['descrizione']] = translate_long_text(desc, lang)

                # Translate interpretazione (long text)
                interp = udata[us_idx['interpretazione']]
                udata[us_idx['interpretazione']] = translate_long_text(interp, lang)

                # Translate formazione
                fm = udata[us_idx['formazione']]
                udata[us_idx['formazione']] = FORMAZIONE.get(fm, {}).get(lang, fm)

                # Translate stato_di_conservazione
                sc = udata[us_idx['stato_di_conservazione']]
                udata[us_idx['stato_di_conservazione']] = STATO_CONSERVAZIONE.get(sc, {}).get(lang, sc)

                # Translate colore
                cl = udata[us_idx['colore']]
                udata[us_idx['colore']] = COLORE.get(cl, {}).get(lang, cl)

                # Translate consistenza
                cn = udata[us_idx['consistenza']]
                udata[us_idx['consistenza']] = CONSISTENZA.get(cn, {}).get(lang, cn)

                # Translate metodo_di_scavo
                ms = udata[us_idx['metodo_di_scavo']]
                udata[us_idx['metodo_di_scavo']] = METODO_SCAVO.get(ms, {}).get(lang, ms)

                # Translate scavato
                sv = udata[us_idx['scavato']]
                udata[us_idx['scavato']] = SCAVATO.get(sv, {}).get(lang, sv)

                # Translate inclusi
                inc = safe_eval(udata[us_idx['inclusi']])
                udata[us_idx['inclusi']] = repr(translate_inclusi(inc, lang))

                # Translate documentazione
                doc = safe_eval(udata[us_idx['documentazione']])
                udata[us_idx['documentazione']] = repr(translate_documentazione(doc, lang))

                # Translate rapporti
                rapp = safe_eval(udata[us_idx['rapporti']])
                udata[us_idx['rapporti']] = repr(translate_rapporti(rapp, lang))

                # Translate rapporti2
                rapp2_raw = udata[us_idx['rapporti2']]
                rapp2 = safe_eval(rapp2_raw) if rapp2_raw else []
                udata[us_idx['rapporti2']] = repr(translate_rapporti2(rapp2, lang))

                # New UUID
                if 'entity_uuid' in us_idx:
                    udata[us_idx['entity_uuid']] = str(uuid.uuid4())

                cur.execute(
                    f"INSERT INTO us_table ({', '.join(us_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(us_cols))})",
                    udata)

            print(f"  Inserted {len(us_rows)} US records")

        # ---- Replicate GIS layers ----
        cur.execute("SELECT COUNT(*) FROM pyunitastratigrafiche WHERE scavo_s = ?", (new_site,))
        if cur.fetchone()[0] == 0 and gis_us_rows:
            for grow in gis_us_rows:
                gdata = list(grow)
                gdata[gis_us_idx['gid']] = next_gis_us_id
                next_gis_us_id += 1
                gdata[gis_us_idx['scavo_s']] = new_site
                # Translate tipo_us_s
                tipo = gdata[gis_us_idx['tipo_us_s']]
                if tipo:
                    gdata[gis_us_idx['tipo_us_s']] = GIS_TIPO_US.get(tipo, {}).get(lang, tipo)
                # Translate unita_tipo_s
                ut = gdata[gis_us_idx['unita_tipo_s']]
                if ut:
                    gdata[gis_us_idx['unita_tipo_s']] = translate_unit_type(ut, lang)
                cur.execute(
                    f"INSERT INTO pyunitastratigrafiche ({', '.join(gis_us_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(gis_us_cols))})", gdata)
            print(f"  Inserted {len(gis_us_rows)} GIS US records")

        cur.execute("SELECT COUNT(*) FROM pyunitastratigrafiche_usm WHERE scavo_s = ?",
                    (new_site,))
        if cur.fetchone()[0] == 0 and gis_usm_rows:
            for grow in gis_usm_rows:
                gdata = list(grow)
                gdata[gis_usm_idx['gid']] = next_gis_usm_id
                next_gis_usm_id += 1
                gdata[gis_usm_idx['scavo_s']] = new_site
                tipo = gdata[gis_usm_idx['tipo_us_s']]
                if tipo:
                    gdata[gis_usm_idx['tipo_us_s']] = GIS_TIPO_US.get(tipo, {}).get(lang, tipo)
                ut = gdata[gis_usm_idx['unita_tipo_s']]
                if ut:
                    gdata[gis_usm_idx['unita_tipo_s']] = translate_unit_type(ut, lang)
                cur.execute(
                    f"INSERT INTO pyunitastratigrafiche_usm ({', '.join(gis_usm_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(gis_usm_cols))})", gdata)
            print(f"  Inserted {len(gis_usm_rows)} GIS USM records")

        cur.execute("SELECT COUNT(*) FROM pyarchinit_quote WHERE sito_q = ?", (new_site,))
        if cur.fetchone()[0] == 0 and gis_quote_rows:
            # Temporarily drop SpatiaLite geometry triggers (we're copying valid BLOBs)
            cur.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' "
                        "AND tbl_name='pyarchinit_quote' AND name LIKE 'ggi_%'")
            quote_triggers = cur.fetchall()
            for tname, _ in quote_triggers:
                cur.execute(f'DROP TRIGGER IF EXISTS "{tname}"')
            for grow in gis_quote_rows:
                gdata = list(grow)
                gdata[gis_quote_idx['gid']] = next_gis_quote_id
                next_gis_quote_id += 1
                gdata[gis_quote_idx['sito_q']] = new_site
                if 'unita_tipo_q' in gis_quote_idx:
                    ut = gdata[gis_quote_idx['unita_tipo_q']]
                    if ut:
                        gdata[gis_quote_idx['unita_tipo_q']] = translate_unit_type(ut, lang)
                cur.execute(
                    f"INSERT INTO pyarchinit_quote ({', '.join(gis_quote_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(gis_quote_cols))})", gdata)
            # Recreate triggers
            for _, tsql in quote_triggers:
                if tsql:
                    cur.execute(tsql)
            print(f"  Inserted {len(gis_quote_rows)} GIS quote records")

        # ---- Replicate struttura_table ----
        cur.execute("SELECT COUNT(*) FROM struttura_table WHERE sito = ?", (new_site,))
        if cur.fetchone()[0] == 0 and struttura_rows:
            for srow in struttura_rows:
                sdata = list(srow)
                sdata[struttura_idx['id_struttura']] = next_struttura_id
                next_struttura_id += 1
                sdata[struttura_idx['sito']] = new_site
                # Translate fields
                sdata[struttura_idx['categoria_struttura']] = translate_field(
                    sdata[struttura_idx['categoria_struttura']], STRUTTURA_CATEGORIA, lang)
                sdata[struttura_idx['tipologia_struttura']] = translate_field(
                    sdata[struttura_idx['tipologia_struttura']], STRUTTURA_TIPOLOGIA, lang)
                sdata[struttura_idx['definizione_struttura']] = translate_field(
                    sdata[struttura_idx['definizione_struttura']], STRUTTURA_DEFINIZIONE, lang)
                sdata[struttura_idx['descrizione']] = translate_long_text(
                    sdata[struttura_idx['descrizione']], lang)
                sdata[struttura_idx['interpretazione']] = translate_long_text(
                    sdata[struttura_idx['interpretazione']], lang)
                sdata[struttura_idx['datazione_estesa']] = translate_datazione_ext(
                    sdata[struttura_idx['datazione_estesa']], lang)
                # Translate materiali_impiegati
                mat = safe_eval(sdata[struttura_idx['materiali_impiegati']])
                sdata[struttura_idx['materiali_impiegati']] = repr(
                    translate_struttura_materiali(mat, lang))
                # Translate elementi_strutturali
                elem = safe_eval(sdata[struttura_idx['elementi_strutturali']])
                sdata[struttura_idx['elementi_strutturali']] = repr(
                    translate_struttura_elementi(elem, lang))
                # Translate rapporti_struttura
                rapp = safe_eval(sdata[struttura_idx['rapporti_struttura']])
                sdata[struttura_idx['rapporti_struttura']] = repr(
                    translate_struttura_rapporti(rapp, lang, new_site))
                if 'entity_uuid' in struttura_idx:
                    sdata[struttura_idx['entity_uuid']] = str(uuid.uuid4())
                cur.execute(
                    f"INSERT INTO struttura_table ({', '.join(struttura_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(struttura_cols))})", sdata)
            print(f"  Inserted {len(struttura_rows)} struttura records")

        # ---- Replicate tomba_table ----
        cur.execute("SELECT COUNT(*) FROM tomba_table WHERE sito = ?", (new_site,))
        if cur.fetchone()[0] == 0 and tomba_rows:
            for trow in tomba_rows:
                tdata = list(trow)
                tdata[tomba_idx['id_tomba']] = next_tomba_id
                next_tomba_id += 1
                tdata[tomba_idx['sito']] = new_site
                tdata[tomba_idx['rito']] = translate_field(
                    tdata[tomba_idx['rito']], TOMBA_RITO, lang)
                tdata[tomba_idx['descrizione_taf']] = translate_long_text(
                    tdata[tomba_idx['descrizione_taf']], lang)
                tdata[tomba_idx['interpretazione_taf']] = translate_long_text(
                    tdata[tomba_idx['interpretazione_taf']], lang)
                tdata[tomba_idx['segnacoli']] = translate_field(
                    tdata[tomba_idx['segnacoli']], TOMBA_SEGNACOLI, lang)
                tdata[tomba_idx['canale_libatorio_si_no']] = translate_field(
                    tdata[tomba_idx['canale_libatorio_si_no']], SCAVATO, lang)
                tdata[tomba_idx['stato_di_conservazione']] = translate_field(
                    tdata[tomba_idx['stato_di_conservazione']], STATO_CONSERVAZIONE, lang)
                tdata[tomba_idx['copertura_tipo']] = translate_field(
                    tdata[tomba_idx['copertura_tipo']], TOMBA_COPERTURA_TIPO, lang)
                tdata[tomba_idx['tipo_contenitore_resti']] = translate_field(
                    tdata[tomba_idx['tipo_contenitore_resti']], TOMBA_CONTENITORE, lang)
                tdata[tomba_idx['tipo_deposizione']] = translate_field(
                    tdata[tomba_idx['tipo_deposizione']], TOMBA_TIPO_DEPOSIZIONE, lang)
                tdata[tomba_idx['tipo_sepoltura']] = translate_field(
                    tdata[tomba_idx['tipo_sepoltura']], TOMBA_TIPO_SEPOLTURA, lang)
                tdata[tomba_idx['corredo_presenza']] = translate_field(
                    tdata[tomba_idx['corredo_presenza']], SCAVATO, lang)
                tdata[tomba_idx['corredo_descrizione']] = translate_long_text(
                    tdata[tomba_idx['corredo_descrizione']], lang)
                tdata[tomba_idx['datazione_estesa']] = translate_datazione_ext(
                    tdata[tomba_idx['datazione_estesa']], lang)
                if 'entity_uuid' in tomba_idx:
                    tdata[tomba_idx['entity_uuid']] = str(uuid.uuid4())
                cur.execute(
                    f"INSERT INTO tomba_table ({', '.join(tomba_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(tomba_cols))})", tdata)
            print(f"  Inserted {len(tomba_rows)} tomba records")

        # ---- Replicate individui_table ----
        cur.execute("SELECT COUNT(*) FROM individui_table WHERE sito = ?", (new_site,))
        if cur.fetchone()[0] == 0 and individui_rows:
            for irow in individui_rows:
                idata = list(irow)
                idata[individui_idx['id_scheda_ind']] = next_ind_id
                next_ind_id += 1
                idata[individui_idx['sito']] = new_site
                idata[individui_idx['sesso']] = translate_field(
                    idata[individui_idx['sesso']], INDIVIDUI_SESSO, lang)
                idata[individui_idx['classi_eta']] = translate_field(
                    idata[individui_idx['classi_eta']], INDIVIDUI_CLASSI_ETA, lang)
                idata[individui_idx['osservazioni']] = translate_long_text(
                    idata[individui_idx['osservazioni']], lang)
                idata[individui_idx['completo_si_no']] = translate_field(
                    idata[individui_idx['completo_si_no']], SCAVATO, lang)
                idata[individui_idx['disturbato_si_no']] = translate_field(
                    idata[individui_idx['disturbato_si_no']], SCAVATO, lang)
                idata[individui_idx['in_connessione_si_no']] = translate_field(
                    idata[individui_idx['in_connessione_si_no']], SCAVATO, lang)
                idata[individui_idx['posizione_scheletro']] = translate_field(
                    idata[individui_idx['posizione_scheletro']],
                    INDIVIDUI_POSIZIONE_SCHELETRO, lang)
                idata[individui_idx['posizione_cranio']] = translate_field(
                    idata[individui_idx['posizione_cranio']],
                    INDIVIDUI_POSIZIONE_CRANIO, lang)
                idata[individui_idx['posizione_arti_superiori']] = translate_field(
                    idata[individui_idx['posizione_arti_superiori']],
                    INDIVIDUI_POSIZIONE_ARTI_SUP, lang)
                idata[individui_idx['posizione_arti_inferiori']] = translate_field(
                    idata[individui_idx['posizione_arti_inferiori']],
                    INDIVIDUI_POSIZIONE_ARTI_INF, lang)
                if 'entity_uuid' in individui_idx:
                    idata[individui_idx['entity_uuid']] = str(uuid.uuid4())
                cur.execute(
                    f"INSERT INTO individui_table ({', '.join(individui_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(individui_cols))})", idata)
            print(f"  Inserted {len(individui_rows)} individui records")

        # ---- Replicate pottery_table ----
        cur.execute("SELECT COUNT(*) FROM pottery_table WHERE sito = ?", (new_site,))
        if cur.fetchone()[0] == 0 and pottery_rows:
            for prow in pottery_rows:
                pdata = list(prow)
                pdata[pottery_idx['id_rep']] = next_pot_id
                next_pot_id += 1
                pdata[pottery_idx['sito']] = new_site
                pdata[pottery_idx['material']] = translate_field(
                    pdata[pottery_idx['material']], POTTERY_MATERIAL, lang)
                pdata[pottery_idx['form']] = translate_field(
                    pdata[pottery_idx['form']], POTTERY_FORM, lang)
                pdata[pottery_idx['ware']] = translate_field(
                    pdata[pottery_idx['ware']], POTTERY_WARE, lang)
                pdata[pottery_idx['surf_trat']] = translate_field(
                    pdata[pottery_idx['surf_trat']], POTTERY_SURF_TRAT, lang)
                pdata[pottery_idx['wheel_made']] = translate_field(
                    pdata[pottery_idx['wheel_made']], SCAVATO, lang)
                pdata[pottery_idx['note']] = translate_long_text(
                    pdata[pottery_idx['note']], lang)
                pdata[pottery_idx['datazione']] = translate_datazione_ext(
                    pdata[pottery_idx['datazione']], lang)
                if 'entity_uuid' in pottery_idx:
                    pdata[pottery_idx['entity_uuid']] = str(uuid.uuid4())
                cur.execute(
                    f"INSERT INTO pottery_table ({', '.join(pottery_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(pottery_cols))})", pdata)
            print(f"  Inserted {len(pottery_rows)} pottery records")

        # ---- Replicate inventario_materiali_table ----
        cur.execute("SELECT COUNT(*) FROM inventario_materiali_table WHERE sito = ?",
                    (new_site,))
        if cur.fetchone()[0] == 0 and invmat_rows:
            for mrow in invmat_rows:
                mdata = list(mrow)
                mdata[invmat_idx['id_invmat']] = next_inv_id
                next_inv_id += 1
                mdata[invmat_idx['sito']] = new_site
                mdata[invmat_idx['tipo_reperto']] = translate_field(
                    mdata[invmat_idx['tipo_reperto']], INVENTARIO_TIPO_REPERTO, lang)
                mdata[invmat_idx['criterio_schedatura']] = translate_field(
                    mdata[invmat_idx['criterio_schedatura']], INVENTARIO_CRITERIO, lang)
                mdata[invmat_idx['definizione']] = translate_field(
                    mdata[invmat_idx['definizione']], INVENTARIO_DEFINIZIONE, lang)
                mdata[invmat_idx['descrizione']] = translate_long_text(
                    mdata[invmat_idx['descrizione']], lang)
                mdata[invmat_idx['lavato']] = translate_field(
                    mdata[invmat_idx['lavato']], SCAVATO, lang)
                mdata[invmat_idx['stato_conservazione']] = translate_field(
                    mdata[invmat_idx['stato_conservazione']], STATO_CONSERVAZIONE, lang)
                mdata[invmat_idx['datazione_reperto']] = translate_datazione_ext(
                    mdata[invmat_idx['datazione_reperto']], lang)
                mdata[invmat_idx['repertato']] = translate_field(
                    mdata[invmat_idx['repertato']], SCAVATO, lang)
                mdata[invmat_idx['diagnostico']] = translate_field(
                    mdata[invmat_idx['diagnostico']], SCAVATO, lang)
                if 'entity_uuid' in invmat_idx:
                    mdata[invmat_idx['entity_uuid']] = str(uuid.uuid4())
                cur.execute(
                    f"INSERT INTO inventario_materiali_table ({', '.join(invmat_cols)}) "
                    f"VALUES ({', '.join(['?'] * len(invmat_cols))})", mdata)
            print(f"  Inserted {len(invmat_rows)} inventario records")

    conn.commit()

    # ---- Verification ----
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    cur.execute("SELECT DISTINCT sito FROM site_table ORDER BY sito")
    sites = [r[0] for r in cur.fetchall()]
    print(f"\nDistinct sites in site_table ({len(sites)}):")
    for s in sites:
        print(f"  - {s}")

    cur.execute("SELECT DISTINCT sito FROM us_table ORDER BY sito")
    us_sites = [r[0] for r in cur.fetchall()]
    print(f"\nDistinct sites in us_table ({len(us_sites)}):")
    for s in us_sites:
        print(f"  - {s}")

    cur.execute("SELECT COUNT(*) FROM us_table")
    total = cur.fetchone()[0]
    print(f"\nTotal US records: {total}")

    cur.execute("SELECT COUNT(*) FROM periodizzazione_table")
    total_p = cur.fetchone()[0]
    print(f"Total period records: {total_p}")

    # Check unit types for US 6 (which is USM in Italian)
    print("\nUnit type for us=6 per site:")
    cur.execute("SELECT sito, unita_tipo FROM us_table WHERE us='6' ORDER BY sito")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check rapporti for US 7 (EN site)
    print("\nRapporti for us=7, English site:")
    cur.execute("SELECT rapporti FROM us_table WHERE us='7' AND sito=?",
                (SITE_NAMES['en'],))
    row = cur.fetchone()
    if row:
        print(f"  {row[0]}")

    # Check rapporti2 for US 3, German site (has USM reference)
    print("\nRapporti2 for us=3, German site:")
    cur.execute("SELECT rapporti2 FROM us_table WHERE us='3' AND sito=?",
                (SITE_NAMES['de'],))
    row = cur.fetchone()
    if row:
        print(f"  {row[0]}")

    # --- GIS layer verification ---
    print("\n--- GIS Layers ---")
    cur.execute("SELECT scavo_s, COUNT(*) FROM pyunitastratigrafiche GROUP BY scavo_s ORDER BY scavo_s")
    for row in cur.fetchall():
        print(f"  pyunitastratigrafiche: {row[0]} = {row[1]}")

    cur.execute("SELECT scavo_s, COUNT(*) FROM pyunitastratigrafiche_usm GROUP BY scavo_s ORDER BY scavo_s")
    for row in cur.fetchall():
        print(f"  pyunitastratigrafiche_usm: {row[0]} = {row[1]}")

    cur.execute("SELECT sito_q, COUNT(*) FROM pyarchinit_quote GROUP BY sito_q ORDER BY sito_q")
    for row in cur.fetchall():
        print(f"  pyarchinit_quote: {row[0]} = {row[1]}")

    # --- New tables verification ---
    print("\n--- New Tables ---")
    for table, col in [('struttura_table', 'sito'), ('tomba_table', 'sito'),
                        ('individui_table', 'sito'), ('pottery_table', 'sito'),
                        ('inventario_materiali_table', 'sito')]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        total = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(DISTINCT {col}) FROM {table}")
        nsites = cur.fetchone()[0]
        print(f"  {table}: {total} records across {nsites} sites")

    # Check struttura translations
    print("\nStruttura definizione_struttura for ED 1:")
    cur.execute("SELECT sito, definizione_struttura FROM struttura_table "
                "WHERE numero_struttura=1 AND sigla_struttura='ED' ORDER BY sito")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check tomba translations
    print("\nTomba rito for TB 1:")
    cur.execute("SELECT sito, rito FROM tomba_table WHERE nr_scheda_taf=1 ORDER BY sito")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check individui translations
    print("\nIndividui sesso for IND 1:")
    cur.execute("SELECT sito, sesso FROM individui_table WHERE nr_individuo=1 ORDER BY sito")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check pottery translations
    print("\nPottery ware for record 1:")
    cur.execute("SELECT sito, ware FROM pottery_table WHERE id_number=1 ORDER BY sito")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check inventario translations
    print("\nInventario tipo_reperto for inv 1:")
    cur.execute("SELECT sito, tipo_reperto, definizione FROM inventario_materiali_table "
                "WHERE numero_inventario=1 ORDER BY sito")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} / {row[2]}")

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
    print(f"Populating: {DB_PATH}")
    populate(DB_PATH)
