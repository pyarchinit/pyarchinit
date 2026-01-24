# -*- coding: utf-8 -*-
"""
GNA Vocabulary Mapper

Maps PyArchInit thesaurus codes to GNA (Geoportale Nazionale per l'Archeologia)
controlled vocabularies.

Thesaurus mappings:
- 12.1 survey_type → MTDM (Metodo di individuazione)
- 12.2 vegetation_coverage → VGTC
- 12.3 gps_method → GPMT
- 12.4 surface_condition → MCND
- 12.5 accessibility → ACCB
- 12.6 weather_conditions → WTHR
- 12.7 def_ut → AMA (Ambito applicazione)

Classification schemes:
- VRP: Archaeological Potential (5 levels)
- VRD: Archaeological Risk (4 levels)
"""


class GNAVocabularyMapper:
    """Maps PyArchInit vocabularies to GNA controlled vocabularies."""

    # AMA - Site Type (from thesaurus 12.7 def_ut)
    # Maps internal codes to GNA AMA vocabulary
    AMA_VOCABULARY = {
        'scatter': {'code': 'AF', 'label_it': 'Area di frammenti', 'label_en': 'Fragment scatter'},
        'site': {'code': 'SA', 'label_it': 'Sito archeologico', 'label_en': 'Archaeological site'},
        'anomaly': {'code': 'AN', 'label_it': 'Anomalia', 'label_en': 'Anomaly'},
        'structure': {'code': 'SM', 'label_it': 'Struttura muraria', 'label_en': 'Masonry structure'},
        'concentration': {'code': 'CM', 'label_it': 'Concentrazione materiali', 'label_en': 'Material concentration'},
        'traces': {'code': 'TC', 'label_it': 'Tracce', 'label_en': 'Traces'},
        'findspot': {'code': 'RS', 'label_it': 'Rinvenimento sporadico', 'label_en': 'Sporadic find'},
        'negative': {'code': 'NG', 'label_it': 'Negativo', 'label_en': 'Negative'},
    }

    # MTDM - Survey Method (from thesaurus 12.1 survey_type)
    MTDM_VOCABULARY = {
        'intensive': {'code': 'RI', 'label_it': 'Ricognizione intensiva', 'label_en': 'Intensive survey'},
        'extensive': {'code': 'RE', 'label_it': 'Ricognizione estensiva', 'label_en': 'Extensive survey'},
        'targeted': {'code': 'RM', 'label_it': 'Ricognizione mirata', 'label_en': 'Targeted survey'},
        'random': {'code': 'RC', 'label_it': 'Campionamento casuale', 'label_en': 'Random sampling'},
    }

    # VGTC - Vegetation Coverage (from thesaurus 12.2)
    VGTC_VOCABULARY = {
        'none': {'code': '0', 'label_it': 'Assente', 'label_en': 'None'},
        'sparse': {'code': '1', 'label_it': 'Rada (<25%)', 'label_en': 'Sparse (<25%)'},
        'moderate': {'code': '2', 'label_it': 'Media (25-50%)', 'label_en': 'Moderate (25-50%)'},
        'dense': {'code': '3', 'label_it': 'Densa (50-75%)', 'label_en': 'Dense (50-75%)'},
        'very_dense': {'code': '4', 'label_it': 'Molto densa (>75%)', 'label_en': 'Very dense (>75%)'},
    }

    # GPMT - GPS Method (from thesaurus 12.3)
    GPMT_VOCABULARY = {
        'handheld': {'code': 'GP', 'label_it': 'GPS portatile', 'label_en': 'Handheld GPS'},
        'dgps': {'code': 'DG', 'label_it': 'GPS differenziale', 'label_en': 'Differential GPS'},
        'rtk': {'code': 'RK', 'label_it': 'RTK GPS', 'label_en': 'RTK GPS'},
        'total_station': {'code': 'TS', 'label_it': 'Stazione totale', 'label_en': 'Total station'},
    }

    # MCND - Surface Condition (from thesaurus 12.4)
    MCND_VOCABULARY = {
        'ploughed': {'code': 'AR', 'label_it': 'Arato', 'label_en': 'Ploughed'},
        'stubble': {'code': 'ST', 'label_it': 'Stoppia', 'label_en': 'Stubble'},
        'pasture': {'code': 'PA', 'label_it': 'Pascolo', 'label_en': 'Pasture'},
        'woodland': {'code': 'BO', 'label_it': 'Bosco', 'label_en': 'Woodland'},
        'urban': {'code': 'UR', 'label_it': 'Urbano', 'label_en': 'Urban'},
    }

    # ACCB - Accessibility (from thesaurus 12.5)
    ACCB_VOCABULARY = {
        'easy': {'code': 'FA', 'label_it': 'Facile', 'label_en': 'Easy'},
        'moderate_access': {'code': 'ME', 'label_it': 'Media', 'label_en': 'Moderate'},
        'difficult': {'code': 'DI', 'label_it': 'Difficile', 'label_en': 'Difficult'},
        'restricted': {'code': 'RI', 'label_it': 'Riservato', 'label_en': 'Restricted'},
    }

    # WTHR - Weather Conditions (from thesaurus 12.6)
    WTHR_VOCABULARY = {
        'sunny': {'code': 'SO', 'label_it': 'Soleggiato', 'label_en': 'Sunny'},
        'cloudy': {'code': 'NU', 'label_it': 'Nuvoloso', 'label_en': 'Cloudy'},
        'rainy': {'code': 'PI', 'label_it': 'Piovoso', 'label_en': 'Rainy'},
        'windy': {'code': 'VE', 'label_it': 'Ventoso', 'label_en': 'Windy'},
    }

    # VRP - Archaeological Potential Classification (5 levels)
    VRP_CLASSIFICATION = {
        (0, 20): {
            'code': 'NV',
            'label_it': 'Non valutabile',
            'label_en': 'Not assessable',
            'color': '#808080',
            'rgb': (128, 128, 128),
        },
        (20, 40): {
            'code': 'NU',
            'label_it': 'Nullo',
            'label_en': 'Null',
            'color': '#2ECC71',
            'rgb': (46, 204, 113),
        },
        (40, 60): {
            'code': 'BA',
            'label_it': 'Basso',
            'label_en': 'Low',
            'color': '#F1C40F',
            'rgb': (241, 196, 15),
        },
        (60, 80): {
            'code': 'ME',
            'label_it': 'Medio',
            'label_en': 'Medium',
            'color': '#E67E22',
            'rgb': (230, 126, 34),
        },
        (80, 100): {
            'code': 'AL',
            'label_it': 'Alto',
            'label_en': 'High',
            'color': '#E74C3C',
            'rgb': (231, 76, 60),
        },
    }

    # VRD - Archaeological Risk Classification (4 levels)
    VRD_CLASSIFICATION = {
        (0, 25): {
            'code': 'NU',
            'label_it': 'Nullo',
            'label_en': 'Null',
            'color': '#2ECC71',
            'rgb': (46, 204, 113),
        },
        (25, 50): {
            'code': 'BA',
            'label_it': 'Basso',
            'label_en': 'Low',
            'color': '#F1C40F',
            'rgb': (241, 196, 15),
        },
        (50, 75): {
            'code': 'ME',
            'label_it': 'Medio',
            'label_en': 'Medium',
            'color': '#E67E22',
            'rgb': (230, 126, 34),
        },
        (75, 100): {
            'code': 'AL',
            'label_it': 'Alto',
            'label_en': 'High',
            'color': '#C0392B',
            'rgb': (192, 57, 43),
        },
    }

    # OGT - Geometry Types
    OGT_VOCABULARY = {
        'point': {'code': 'PU', 'label_it': 'Puntuale', 'label_en': 'Point'},
        'line': {'code': 'LI', 'label_it': 'Lineare', 'label_en': 'Linear'},
        'polygon': {'code': 'AR', 'label_it': 'Areale', 'label_en': 'Areal'},
    }

    def __init__(self, language='it'):
        """
        Initialize vocabulary mapper.

        Args:
            language: Language code ('it', 'en', etc.)
        """
        self.language = language

    def map_def_ut_to_ama(self, def_ut_value):
        """
        Map def_ut thesaurus value to GNA AMA code.

        Args:
            def_ut_value: PyArchInit def_ut field value (internal code like 'scatter', 'site')

        Returns:
            dict with 'code' and 'label' or None if not found
        """
        if not def_ut_value:
            return None

        # Normalize: lowercase and strip
        key = str(def_ut_value).lower().strip()

        if key in self.AMA_VOCABULARY:
            vocab = self.AMA_VOCABULARY[key]
            label_key = f'label_{self.language}' if f'label_{self.language}' in vocab else 'label_it'
            return {
                'code': vocab['code'],
                'label': vocab.get(label_key, vocab.get('label_it', '')),
            }

        # Try reverse lookup from Italian labels
        for internal_key, vocab in self.AMA_VOCABULARY.items():
            if vocab.get('label_it', '').lower() == key or vocab.get('label_en', '').lower() == key:
                label_key = f'label_{self.language}' if f'label_{self.language}' in vocab else 'label_it'
                return {
                    'code': vocab['code'],
                    'label': vocab.get(label_key, vocab.get('label_it', '')),
                }

        return None

    def map_survey_type_to_mtdm(self, survey_type_value):
        """Map survey_type to GNA MTDM code."""
        return self._map_vocabulary(survey_type_value, self.MTDM_VOCABULARY)

    def map_vegetation_to_vgtc(self, vegetation_value):
        """Map vegetation_coverage to GNA VGTC code."""
        return self._map_vocabulary(vegetation_value, self.VGTC_VOCABULARY)

    def map_gps_method_to_gpmt(self, gps_value):
        """Map gps_method to GNA GPMT code."""
        return self._map_vocabulary(gps_value, self.GPMT_VOCABULARY)

    def map_surface_to_mcnd(self, surface_value):
        """Map surface_condition to GNA MCND code."""
        return self._map_vocabulary(surface_value, self.MCND_VOCABULARY)

    def map_accessibility_to_accb(self, accessibility_value):
        """Map accessibility to GNA ACCB code."""
        return self._map_vocabulary(accessibility_value, self.ACCB_VOCABULARY)

    def map_weather_to_wthr(self, weather_value):
        """Map weather_conditions to GNA WTHR code."""
        return self._map_vocabulary(weather_value, self.WTHR_VOCABULARY)

    def map_geometry_type_to_ogt(self, geom_type):
        """
        Map QGIS geometry type to GNA OGT code.

        Args:
            geom_type: QgsWkbTypes geometry type or string ('Point', 'Polygon', etc.)

        Returns:
            dict with 'code' and 'label'
        """
        if not geom_type:
            return None

        type_str = str(geom_type).lower()

        if 'point' in type_str:
            key = 'point'
        elif 'line' in type_str or 'string' in type_str:
            key = 'line'
        elif 'polygon' in type_str:
            key = 'polygon'
        else:
            return None

        return self._map_vocabulary(key, self.OGT_VOCABULARY)

    def _map_vocabulary(self, value, vocabulary):
        """
        Generic vocabulary mapping helper.

        Args:
            value: Input value to map
            vocabulary: Vocabulary dict to use

        Returns:
            dict with 'code' and 'label' or None
        """
        if not value:
            return None

        key = str(value).lower().strip()

        if key in vocabulary:
            vocab = vocabulary[key]
            label_key = f'label_{self.language}' if f'label_{self.language}' in vocab else 'label_it'
            return {
                'code': vocab['code'],
                'label': vocab.get(label_key, vocab.get('label_it', '')),
            }

        # Try reverse lookup from labels
        for internal_key, vocab in vocabulary.items():
            if vocab.get('label_it', '').lower() == key or vocab.get('label_en', '').lower() == key:
                label_key = f'label_{self.language}' if f'label_{self.language}' in vocab else 'label_it'
                return {
                    'code': vocab['code'],
                    'label': vocab.get(label_key, vocab.get('label_it', '')),
                }

        return None

    def classify_potential(self, score):
        """
        Classify potential score to VRP category.

        Args:
            score: Potential score (0-100)

        Returns:
            dict with 'code', 'label', 'color', 'rgb', 'min', 'max'
        """
        return self._classify_score(score, self.VRP_CLASSIFICATION)

    def classify_risk(self, score):
        """
        Classify risk score to VRD category.

        Args:
            score: Risk score (0-100)

        Returns:
            dict with 'code', 'label', 'color', 'rgb', 'min', 'max'
        """
        return self._classify_score(score, self.VRD_CLASSIFICATION)

    def _classify_score(self, score, classification):
        """
        Classify a score using the given classification scheme.

        Args:
            score: Numeric score
            classification: Classification dict with (min, max) keys

        Returns:
            dict with classification info
        """
        if score is None:
            return None

        try:
            score = float(score)
        except (ValueError, TypeError):
            return None

        # Clamp to 0-100 range
        score = max(0, min(100, score))

        for (min_val, max_val), class_info in classification.items():
            if min_val <= score < max_val or (max_val == 100 and score == 100):
                label_key = f'label_{self.language}' if f'label_{self.language}' in class_info else 'label_it'
                return {
                    'code': class_info['code'],
                    'label': class_info.get(label_key, class_info.get('label_it', '')),
                    'color': class_info['color'],
                    'rgb': class_info['rgb'],
                    'min': min_val,
                    'max': max_val,
                }

        return None

    def get_vrp_classification_scheme(self):
        """
        Get VRP classification scheme for heatmap generation.

        Returns:
            dict suitable for classify_to_multipolygon method
        """
        scheme = {}
        for (min_val, max_val), class_info in self.VRP_CLASSIFICATION.items():
            label_key = f'label_{self.language}' if f'label_{self.language}' in class_info else 'label_it'
            scheme[(min_val, max_val)] = {
                'code': class_info['code'],
                'label': class_info.get(label_key, class_info.get('label_it', '')),
                'color': class_info['color'],
            }
        return scheme

    def get_vrd_classification_scheme(self):
        """
        Get VRD classification scheme for heatmap generation.

        Returns:
            dict suitable for classify_to_multipolygon method
        """
        scheme = {}
        for (min_val, max_val), class_info in self.VRD_CLASSIFICATION.items():
            label_key = f'label_{self.language}' if f'label_{self.language}' in class_info else 'label_it'
            scheme[(min_val, max_val)] = {
                'code': class_info['code'],
                'label': class_info.get(label_key, class_info.get('label_it', '')),
                'color': class_info['color'],
            }
        return scheme

    def get_all_ama_codes(self):
        """Get all available AMA codes with labels."""
        return [
            {
                'internal': key,
                'code': info['code'],
                'label_it': info['label_it'],
                'label_en': info['label_en'],
            }
            for key, info in self.AMA_VOCABULARY.items()
        ]
