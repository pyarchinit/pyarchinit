# -*- coding: utf-8 -*-
"""
GNA Field Mapper

Maps PyArchInit UT fields to GNA MOSI fields with validation and transformation.

GNA mandatory fields:
- ID: Unique identifier (max 10 chars)
- AMA: Site type (controlled vocabulary)
- OGD: Object definition
- OGT: Geometry type
- DES: Description (max 10000 chars)
- OGM: Discovery method
- DTSI: Start date (numeric, negative for BC)
- DTSF: End date (numeric, negative for BC)
"""

import re
from datetime import datetime
from .gna_vocabulary_mapper import GNAVocabularyMapper


class GNAFieldMapper:
    """Maps PyArchInit UT fields to GNA MOSI fields."""

    # Field length constraints from GNA specification
    FIELD_CONSTRAINTS = {
        'ID': {'max_length': 10, 'required': True},
        'AMA': {'max_length': 5, 'required': True},
        'OGD': {'max_length': 500, 'required': True},
        'OGT': {'max_length': 5, 'required': True},
        'DES': {'max_length': 10000, 'required': True},
        'OGM': {'max_length': 200, 'required': True},
        'DTSI': {'type': 'date', 'required': False},
        'DTSF': {'type': 'date', 'required': False},
        'DTSV': {'max_length': 50, 'required': False},
        'DTSL': {'max_length': 50, 'required': False},
        'PRVN': {'max_length': 100, 'required': False},
        'PVCR': {'max_length': 100, 'required': False},
        'PVCP': {'max_length': 5, 'required': False},
        'PVCC': {'max_length': 200, 'required': False},
        'PVCF': {'max_length': 200, 'required': False},
        'LCGG': {'max_length': 50, 'required': False},
        'LCDQ': {'type': 'float', 'required': False},
        'RSPR': {'max_length': 200, 'required': False},
        'BIBR': {'max_length': 5000, 'required': False},
    }

    # Mapping from UT fields to GNA fields
    UT_TO_MOSI_MAPPING = {
        # Core identification
        'progetto': 'CPR',  # For MOPR
        'nr_ut': 'ID_SUFFIX',  # Combined with progetto for ID
        'def_ut': 'AMA',  # Needs vocabulary translation
        'interpretazione_ut': 'OGD',
        'descrizione_ut': 'DES',
        'metodo_rilievo_e_ricognizione': 'OGM',

        # Chronology
        'periodo_I': 'DTSI_RAW',
        'datazione_I': 'DTSI_TEXT',
        'periodo_II': 'DTSF_RAW',
        'datazione_II': 'DTSF_TEXT',

        # Location - administrative
        'nazione': 'PRVN',
        'regione': 'PVCR',
        'provincia': 'PVCP',
        'comune': 'PVCC',
        'frazione': 'PVCF',
        'localita': 'LCLTA',  # Additional location info
        'indirizzo': 'LCIND',

        # Location - coordinates
        'coord_geografiche': 'LCGG',
        'coord_piane': 'LCGP',
        'quota': 'LCDQ',

        # Survey metadata
        'survey_type': 'MTDM',
        'vegetation_coverage': 'VGTC',
        'gps_method': 'GPMT',
        'surface_condition': 'MCND',
        'accessibility': 'ACCB',
        'weather_conditions': 'WTHR',
        'visibility_percent': 'VCND',
        'responsabile': 'RSPR',
        'data': 'DTRR',

        # Analysis scores (for VRP/VRD generation)
        'potential_score': 'POTENTIAL',
        'risk_score': 'RISK',
    }

    # Period mapping to numeric years
    # Negative = BC, Positive = AD
    PERIOD_TO_YEAR_RANGES = {
        # Prehistory
        'paleolitico': (-2500000, -10000),
        'paleolithic': (-2500000, -10000),
        'mesolitico': (-10000, -8000),
        'mesolithic': (-10000, -8000),
        'neolitico': (-8000, -3000),
        'neolithic': (-8000, -3000),
        'eneolitico': (-3500, -2200),
        'eneolithic': (-3500, -2200),
        'età del bronzo': (-2200, -900),
        'bronze age': (-2200, -900),
        'età del ferro': (-900, -27),
        'iron age': (-900, -27),

        # Classical
        'greco': (-800, -146),
        'greek': (-800, -146),
        'etrusco': (-900, -27),
        'etruscan': (-900, -27),
        'romano repubblicano': (-509, -27),
        'roman republican': (-509, -27),
        'romano imperiale': (-27, 476),
        'roman imperial': (-27, 476),
        'romano': (-509, 476),
        'roman': (-509, 476),
        'tardoantico': (284, 600),
        'late antique': (284, 600),

        # Medieval and later
        'altomedievale': (500, 1000),
        'early medieval': (500, 1000),
        'medievale': (500, 1500),
        'medieval': (500, 1500),
        'bassomedievale': (1000, 1500),
        'late medieval': (1000, 1500),
        'rinascimentale': (1400, 1600),
        'renaissance': (1400, 1600),
        'moderno': (1500, 1800),
        'modern': (1500, 1800),
        'contemporaneo': (1800, 2000),
        'contemporary': (1800, 2000),
    }

    def __init__(self, language='it'):
        """
        Initialize field mapper.

        Args:
            language: Language code for vocabulary translations
        """
        self.language = language
        self.vocab_mapper = GNAVocabularyMapper(language)

    def map_ut_record_to_mosi(self, ut_record, geometry=None):
        """
        Map a complete UT record to GNA MOSI fields.

        Args:
            ut_record: UT database record (dict or SQLAlchemy object)
            geometry: Optional QgsGeometry for geometry type determination

        Returns:
            dict with GNA MOSI field names and values
        """
        # Convert SQLAlchemy object to dict if needed
        if hasattr(ut_record, '__dict__'):
            record = {k: v for k, v in ut_record.__dict__.items() if not k.startswith('_')}
        else:
            record = dict(ut_record)

        mosi = {}

        # Generate composite ID (max 10 chars)
        mosi['ID'] = self._generate_id(
            record.get('progetto', ''),
            record.get('nr_ut', '')
        )

        # Map AMA with vocabulary translation
        ama_result = self.vocab_mapper.map_def_ut_to_ama(record.get('def_ut'))
        mosi['AMA'] = ama_result['code'] if ama_result else 'NI'  # NI = Non identificato

        # Direct text mappings
        mosi['OGD'] = self._truncate(record.get('interpretazione_ut', ''), 500)
        mosi['DES'] = self._truncate(record.get('descrizione_ut', ''), 10000)
        mosi['OGM'] = self._truncate(record.get('metodo_rilievo_e_ricognizione', ''), 200)

        # Geometry type
        if geometry:
            ogt_result = self.vocab_mapper.map_geometry_type_to_ogt(
                geometry.type() if hasattr(geometry, 'type') else str(geometry)
            )
            mosi['OGT'] = ogt_result['code'] if ogt_result else 'PU'
        else:
            mosi['OGT'] = 'PU'  # Default to Point

        # Chronology - convert periods to numeric dates
        dtsi, dtsf = self._map_chronology(
            record.get('periodo_I'),
            record.get('datazione_I'),
            record.get('periodo_II'),
            record.get('datazione_II')
        )
        mosi['DTSI'] = dtsi
        mosi['DTSF'] = dtsf
        mosi['DTSV'] = record.get('datazione_I', '')  # Original text for validation
        mosi['DTSL'] = record.get('datazione_II', '')

        # Administrative location
        mosi['PRVN'] = self._truncate(record.get('nazione', ''), 100)
        mosi['PVCR'] = self._truncate(record.get('regione', ''), 100)
        mosi['PVCP'] = self._map_province_code(record.get('provincia', ''))
        mosi['PVCC'] = self._truncate(record.get('comune', ''), 200)
        mosi['PVCF'] = self._truncate(record.get('frazione', ''), 200)

        # Coordinates
        mosi['LCGG'] = record.get('coord_geografiche', '')
        mosi['LCDQ'] = self._parse_float(record.get('quota'))

        # Survey metadata with vocabulary translations
        survey_type = self.vocab_mapper.map_survey_type_to_mtdm(record.get('survey_type'))
        mosi['MTDM'] = survey_type['code'] if survey_type else ''

        vegetation = self.vocab_mapper.map_vegetation_to_vgtc(record.get('vegetation_coverage'))
        mosi['VGTC'] = vegetation['code'] if vegetation else ''

        gps = self.vocab_mapper.map_gps_method_to_gpmt(record.get('gps_method'))
        mosi['GPMT'] = gps['code'] if gps else ''

        surface = self.vocab_mapper.map_surface_to_mcnd(record.get('surface_condition'))
        mosi['MCND'] = surface['code'] if surface else ''

        access = self.vocab_mapper.map_accessibility_to_accb(record.get('accessibility'))
        mosi['ACCB'] = access['code'] if access else ''

        weather = self.vocab_mapper.map_weather_to_wthr(record.get('weather_conditions'))
        mosi['WTHR'] = weather['code'] if weather else ''

        # Numeric fields
        mosi['VCND'] = self._parse_int(record.get('visibility_percent'))

        # Responsibility and dates
        mosi['RSPR'] = self._truncate(record.get('responsabile', ''), 200)
        mosi['DTRR'] = self._format_date(record.get('data'))

        # Analysis scores (for internal use in VRP/VRD generation)
        mosi['_potential_score'] = self._parse_float(record.get('potential_score'))
        mosi['_risk_score'] = self._parse_float(record.get('risk_score'))

        return mosi

    def _generate_id(self, project, nr_ut):
        """
        Generate GNA-compliant ID (max 10 chars).

        Strategy: Use first 5 chars of project + 5 chars of UT number
        If project is short, use more for UT number
        """
        project = str(project).strip() if project else ''
        nr_ut = str(nr_ut).strip() if nr_ut else '0'

        # Clean project name: alphanumeric only, uppercase
        project_clean = re.sub(r'[^A-Za-z0-9]', '', project).upper()

        # Determine split
        if len(project_clean) <= 4:
            project_part = project_clean
            ut_part = nr_ut.zfill(10 - len(project_part))[:10 - len(project_part)]
        else:
            project_part = project_clean[:5]
            ut_part = nr_ut.zfill(5)[:5]

        combined = f"{project_part}{ut_part}"

        # Ensure max 10 chars
        return combined[:10]

    def _map_chronology(self, periodo_i, datazione_i, periodo_ii, datazione_ii):
        """
        Map period/dating fields to numeric DTSI/DTSF.

        Returns:
            tuple (dtsi, dtsf) as strings or None
        """
        dtsi = None
        dtsf = None

        # Try to extract from periodo_I
        if periodo_i:
            year_range = self._period_to_years(periodo_i)
            if year_range:
                dtsi = str(year_range[0])

        # Try to extract from datazione_I text
        if not dtsi and datazione_i:
            years = self._extract_years_from_text(datazione_i)
            if years:
                dtsi = str(years[0])

        # Try to extract end date from periodo_II or use range end
        if periodo_ii:
            year_range = self._period_to_years(periodo_ii)
            if year_range:
                dtsf = str(year_range[1])
        elif periodo_i and not dtsf:
            year_range = self._period_to_years(periodo_i)
            if year_range:
                dtsf = str(year_range[1])

        # Try to extract from datazione_II
        if not dtsf and datazione_ii:
            years = self._extract_years_from_text(datazione_ii)
            if years:
                dtsf = str(years[-1])

        return dtsi, dtsf

    def _period_to_years(self, period_name):
        """Convert period name to year range."""
        if not period_name:
            return None

        period_lower = str(period_name).lower().strip()

        # Direct lookup
        if period_lower in self.PERIOD_TO_YEAR_RANGES:
            return self.PERIOD_TO_YEAR_RANGES[period_lower]

        # Partial match
        for key, value in self.PERIOD_TO_YEAR_RANGES.items():
            if key in period_lower or period_lower in key:
                return value

        return None

    def _extract_years_from_text(self, text):
        """Extract numeric years from dating text."""
        if not text:
            return None

        text = str(text).lower()

        # Pattern for centuries (e.g., "I sec. a.C.", "2nd century AD")
        century_patterns = [
            r'(\d+)\s*(?:°|st|nd|rd|th)?\s*(?:sec\.?|secolo|century)\s*(?:a\.?\s*c\.?|bc)',  # BC
            r'(\d+)\s*(?:°|st|nd|rd|th)?\s*(?:sec\.?|secolo|century)\s*(?:d\.?\s*c\.?|ad)?',  # AD
        ]

        # Try century patterns
        for pattern in century_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                century = int(match.group(1))
                is_bc = 'a.c' in text.lower() or 'bc' in text.lower()
                if is_bc:
                    start = -century * 100
                    end = -(century - 1) * 100
                else:
                    start = (century - 1) * 100
                    end = century * 100
                return [start, end]

        # Pattern for explicit years
        year_patterns = [
            r'(\d{3,4})\s*(?:a\.?\s*c\.?|bc)',  # Year BC
            r'(\d{3,4})\s*(?:d\.?\s*c\.?|ad)',  # Year AD
            r'(\d{3,4})',  # Plain year
        ]

        years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                year = int(match)
                if 'a.c' in text.lower() or 'bc' in text.lower():
                    year = -year
                years.append(year)

        return years if years else None

    def _map_province_code(self, province):
        """Convert province name to 2-letter code."""
        if not province:
            return ''

        # Common Italian province codes
        province_codes = {
            'agrigento': 'AG', 'alessandria': 'AL', 'ancona': 'AN', 'aosta': 'AO',
            'arezzo': 'AR', 'ascoli piceno': 'AP', 'asti': 'AT', 'avellino': 'AV',
            'bari': 'BA', 'barletta-andria-trani': 'BT', 'belluno': 'BL', 'benevento': 'BN',
            'bergamo': 'BG', 'biella': 'BI', 'bologna': 'BO', 'bolzano': 'BZ',
            'brescia': 'BS', 'brindisi': 'BR', 'cagliari': 'CA', 'caltanissetta': 'CL',
            'campobasso': 'CB', 'caserta': 'CE', 'catania': 'CT', 'catanzaro': 'CZ',
            'chieti': 'CH', 'como': 'CO', 'cosenza': 'CS', 'cremona': 'CR',
            'crotone': 'KR', 'cuneo': 'CN', 'enna': 'EN', 'fermo': 'FM',
            'ferrara': 'FE', 'firenze': 'FI', 'foggia': 'FG', 'forlì-cesena': 'FC',
            'frosinone': 'FR', 'genova': 'GE', 'gorizia': 'GO', 'grosseto': 'GR',
            'imperia': 'IM', 'isernia': 'IS', "l'aquila": 'AQ', 'la spezia': 'SP',
            'latina': 'LT', 'lecce': 'LE', 'lecco': 'LC', 'livorno': 'LI',
            'lodi': 'LO', 'lucca': 'LU', 'macerata': 'MC', 'mantova': 'MN',
            'massa-carrara': 'MS', 'matera': 'MT', 'messina': 'ME', 'milano': 'MI',
            'modena': 'MO', 'monza e brianza': 'MB', 'napoli': 'NA', 'novara': 'NO',
            'nuoro': 'NU', 'oristano': 'OR', 'padova': 'PD', 'palermo': 'PA',
            'parma': 'PR', 'pavia': 'PV', 'perugia': 'PG', 'pesaro e urbino': 'PU',
            'pescara': 'PE', 'piacenza': 'PC', 'pisa': 'PI', 'pistoia': 'PT',
            'pordenone': 'PN', 'potenza': 'PZ', 'prato': 'PO', 'ragusa': 'RG',
            'ravenna': 'RA', 'reggio calabria': 'RC', 'reggio emilia': 'RE', 'rieti': 'RI',
            'rimini': 'RN', 'roma': 'RM', 'rovigo': 'RO', 'salerno': 'SA',
            'sassari': 'SS', 'savona': 'SV', 'siena': 'SI', 'siracusa': 'SR',
            'sondrio': 'SO', 'sud sardegna': 'SU', 'taranto': 'TA', 'teramo': 'TE',
            'terni': 'TR', 'torino': 'TO', 'trapani': 'TP', 'trento': 'TN',
            'treviso': 'TV', 'trieste': 'TS', 'udine': 'UD', 'varese': 'VA',
            'venezia': 'VE', 'verbano-cusio-ossola': 'VB', 'vercelli': 'VC', 'verona': 'VR',
            'vibo valentia': 'VV', 'vicenza': 'VI', 'viterbo': 'VT',
        }

        province_lower = str(province).lower().strip()

        # Direct match
        if province_lower in province_codes:
            return province_codes[province_lower]

        # Already a code
        if len(province) == 2 and province.upper() in province_codes.values():
            return province.upper()

        # Partial match
        for name, code in province_codes.items():
            if name in province_lower or province_lower in name:
                return code

        return province[:5]  # Return truncated if no match

    def _truncate(self, value, max_length):
        """Truncate string to max length."""
        if not value:
            return ''
        value = str(value).strip()
        if len(value) > max_length:
            return value[:max_length - 3] + '...'
        return value

    def _parse_float(self, value):
        """Parse value to float or None."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value):
        """Parse value to int or None."""
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _format_date(self, date_value):
        """Format date for GNA DTRR field."""
        if not date_value:
            return ''

        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')

        if isinstance(date_value, str):
            # Try to parse common formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y']
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue

        return str(date_value)

    def validate_mosi_record(self, mosi_record):
        """
        Validate a MOSI record against GNA constraints.

        Args:
            mosi_record: Dict of MOSI field values

        Returns:
            dict with 'valid' bool and 'errors' list
        """
        errors = []

        for field, constraints in self.FIELD_CONSTRAINTS.items():
            value = mosi_record.get(field)

            # Check required fields
            if constraints.get('required', False):
                if not value or (isinstance(value, str) and not value.strip()):
                    errors.append(f"Campo obbligatorio mancante: {field}")
                    continue

            if not value:
                continue

            # Check length constraints
            if 'max_length' in constraints:
                if len(str(value)) > constraints['max_length']:
                    errors.append(
                        f"Campo {field} supera la lunghezza massima "
                        f"({len(str(value))} > {constraints['max_length']})"
                    )

            # Check type constraints
            if constraints.get('type') == 'float':
                if value is not None:
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Campo {field} deve essere numerico")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }

    def get_mopr_fields(self, project_info):
        """
        Map project information to MOPR fields.

        Args:
            project_info: Dict with project metadata

        Returns:
            dict with MOPR field values
        """
        return {
            'CPR': self._truncate(project_info.get('code', ''), 20),
            'TITOLO': self._truncate(project_info.get('title', ''), 500),
            'RESPONSABILE': self._truncate(project_info.get('responsible', ''), 200),
            'DATA_INIZIO': self._format_date(project_info.get('start_date')),
            'DATA_FINE': self._format_date(project_info.get('end_date')),
            'NOTE': self._truncate(project_info.get('notes', ''), 5000),
        }
