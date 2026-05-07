# -*- coding: utf-8 -*-
"""
Central i18n module for stratigraphic unit types and relationships.

DEPRECATED (since 5.1.0, scheduled for removal in 6.0.0).
New code should consume :mod:`modules.s3dgraphy.sync.VocabProvider`
directly. This module remains as a backwards-compat adapter so existing
imports keep working for one release cycle.

Provides all unit type abbreviations (US/USM equivalents) and
stratigraphic relationship terms for 10 supported languages.
"""

from __future__ import annotations

import logging
from functools import lru_cache

_log = logging.getLogger(__name__)
_DEPRECATION_LOGGED = False


def _warn_deprecation_once() -> None:
    """Log a one-shot deprecation notice on first module load."""
    global _DEPRECATION_LOGGED
    if _DEPRECATION_LOGGED:
        return
    _DEPRECATION_LOGGED = True
    _log.info(
        "modules.utility.pyarchinit_i18n_stratigraphic is deprecated "
        "(scheduled for removal in 6.0.0). New code should use "
        "modules.s3dgraphy.sync.VocabProvider directly."
    )


_warn_deprecation_once()


# ---------------------------------------------------------------------------
# Unit Type Abbreviations
# ---------------------------------------------------------------------------
# Only US and USM change per language - this is a pyarchinit UI convention
# and is NOT part of the s3dgraphy JSON formalism, so it stays hard-coded
# here. All other types (USVs, USVn, USD, CON, VSF, SF, SUS, DOC,
# Combinar, Extractor, property) come from VocabProvider when available.

UNIT_TYPE_ABBREV = {
    'it': ('US',  'USM'),
    'en': ('SU',  'WSU'),
    'de': ('SE',  'MSE'),
    'fr': ('US',  'USM'),
    'es': ('UE',  'UEM'),
    'ar': ('SU',  'WSU'),
    'ca': ('UE',  'UEM'),
    'ro': ('US',  'USZ'),
    'pt': ('UE',  'UEM'),
    'el': ('\u03a3\u039c', '\u03a4\u03a3\u039c'),  # ΣΜ, ΤΣΜ
}

# Flat sets for quick membership tests
ALL_US_ABBREVS = {v[0] for v in UNIT_TYPE_ABBREV.values()}
ALL_USM_ABBREVS = {v[1] for v in UNIT_TYPE_ABBREV.values()}
ALL_UNIT_ABBREVS = ALL_US_ABBREVS | ALL_USM_ABBREVS


# ---------------------------------------------------------------------------
# Common Items (delegated to VocabProvider, with legacy fallback)
# ---------------------------------------------------------------------------
# Hard-coded fallback used when ext_libs/s3dgraphy/ is unavailable
# (e.g. fresh clone before pip install --target). Order matters for the
# unit-type picker dialog.
_LEGACY_COMMON_ITEMS = (
    'USVA', 'USVB', 'USVC', 'USD', 'CON', 'VSF', 'SF', 'SUS',
    'Combinar', 'Extractor', 'DOC', 'property',
)

# Non-stratigraphic legacy items that VocabProvider does not expose under
# their old names: kept so existing UI/code keeps finding them.
_LEGACY_EXTRA_ITEMS = ('CON', 'SUS', 'Combinar', 'Extractor', 'DOC', 'property')


@lru_cache(maxsize=1)
def _build_common_items() -> tuple:
    """Resolve the common-items tuple from VocabProvider, lazily.

    Returns the legacy hard-coded list when the s3dgraphy bundle is
    missing (fresh clone before deps are installed).
    """
    try:
        from modules.s3dgraphy.sync.vocab_provider import get_default_provider
    except Exception as exc:  # noqa: BLE001 - adapter MUST not crash callers
        _log.debug(
            "VocabProvider unavailable (%s); falling back to legacy _COMMON_ITEMS.",
            exc,
        )
        return _LEGACY_COMMON_ITEMS

    try:
        provider = get_default_provider()
        unit_types = provider.get_unit_types()
    except Exception as exc:  # noqa: BLE001
        _log.debug(
            "VocabProvider.get_unit_types() failed (%s); falling back to legacy _COMMON_ITEMS.",
            exc,
        )
        return _LEGACY_COMMON_ITEMS

    seen: set = set()
    out: list = []
    # First pass: stratigraphic unit types from VocabProvider, minus the
    # per-language US/USM equivalents (those are added by get_unit_type_items).
    for ut in unit_types:
        abbrev = ut.abbreviation
        if abbrev in ALL_UNIT_ABBREVS:
            continue
        if abbrev in seen:
            continue
        seen.add(abbrev)
        out.append(abbrev)

    # Second pass: append legacy non-stratigraphic items that VocabProvider
    # does not expose under their old names, so old callers keep working.
    for item in _LEGACY_EXTRA_ITEMS:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)

    return tuple(out)


class _CommonItemsProxy(tuple):
    """Tuple-like proxy that lazy-resolves to VocabProvider on first access.

    Subclasses :class:`tuple` so that ``isinstance(_COMMON_ITEMS, tuple)``,
    ``"DOC" in _COMMON_ITEMS``, and ``_COMMON_ITEMS + (x,)`` all keep
    working exactly as before.
    """

    __slots__ = ()

    def __new__(cls):
        # Empty placeholder; real contents resolved lazily on every dunder.
        return super().__new__(cls)

    def _resolved(self) -> tuple:
        return _build_common_items()

    def __iter__(self):
        return iter(self._resolved())

    def __len__(self):
        return len(self._resolved())

    def __getitem__(self, idx):
        return self._resolved()[idx]

    def __contains__(self, item):
        return item in self._resolved()

    def __add__(self, other):
        return self._resolved() + tuple(other)

    def __radd__(self, other):
        return tuple(other) + self._resolved()

    def __eq__(self, other):
        return self._resolved() == other

    def __ne__(self, other):
        return self._resolved() != other

    def __hash__(self):
        return hash(self._resolved())

    def __repr__(self):
        return repr(self._resolved())


_COMMON_ITEMS = _CommonItemsProxy()


def get_unit_type_items(lang):
    """Return full tuple of items for the unit-type picker dialog."""
    us, usm = UNIT_TYPE_ABBREV.get(lang, UNIT_TYPE_ABBREV['en'])
    return (us, usm) + _build_common_items()


def is_us_type(abbrev):
    """Check if *abbrev* is any language's US equivalent."""
    return abbrev in ALL_US_ABBREVS


def is_usm_type(abbrev):
    """Check if *abbrev* is any language's USM equivalent."""
    return abbrev in ALL_USM_ABBREVS


def is_any_unit_prefix(text):
    """Check if *text* starts with any known US or USM abbreviation."""
    for a in ALL_UNIT_ABBREVS:
        if text.startswith(a):
            return True
    return False


# ---------------------------------------------------------------------------
# Unit Type Labels (for change_label / UI descriptions)
# ---------------------------------------------------------------------------

_UNIT_TYPE_LABELS = {
    'it': {
        'property':  'Descrizione della propriet\u00e0',
        'USV':       'Descrizione della Unit\u00e0 Str. Virtuale',
        'CON':       'Riferimento alla Unit\u00e0 Continuativa',
        'Combinar':  'Descrizione connettore',
        'Extractor': 'Descrizione estrattore',
        'SUS':       'Descrizione',
        'SF':        'Descrizione',
        'DOC':       'Riferimento documentazione',
    },
    'en': {
        'property':  'Property description',
        'USV':       'Virtual Stratigraphic Unit description',
        'CON':       'Continuity Unit reference',
        'Combinar':  'Connector description',
        'Extractor': 'Extractor description',
        'SUS':       'Description',
        'SF':        'Description',
        'DOC':       'Documentation reference',
    },
    'de': {
        'property':  'Eigenschaftsbeschreibung',
        'USV':       'Beschreibung der virtuellen stratigraphischen Einheit',
        'CON':       'Verweis auf die Kontinuit\u00e4tseinheit',
        'Combinar':  'Verbindungsbeschreibung',
        'Extractor': 'Extraktor-Beschreibung',
        'SUS':       'Beschreibung',
        'SF':        'Beschreibung',
        'DOC':       'Dokumentationsreferenz',
    },
    'es': {
        'property':  'Descripci\u00f3n de la propiedad',
        'USV':       'Descripci\u00f3n de la Unidad Estratigr\u00e1fica Virtual',
        'CON':       'Referencia a la Unidad Continuativa',
        'Combinar':  'Descripci\u00f3n del conector',
        'Extractor': 'Descripci\u00f3n del extractor',
        'SUS':       'Descripci\u00f3n',
        'SF':        'Descripci\u00f3n',
        'DOC':       'Referencia documental',
    },
    'fr': {
        'property':  'Description de la propri\u00e9t\u00e9',
        'USV':       'Description de l\u2019unit\u00e9 stratigraphique virtuelle',
        'CON':       'R\u00e9f\u00e9rence \u00e0 l\u2019unit\u00e9 continuative',
        'Combinar':  'Description du connecteur',
        'Extractor': 'Description de l\u2019extracteur',
        'SUS':       'Description',
        'SF':        'Description',
        'DOC':       'R\u00e9f\u00e9rence documentaire',
    },
    'ar': {
        'property':  '\u0648\u0635\u0641 \u0627\u0644\u062e\u0627\u0635\u064a\u0629',
        'USV':       '\u0648\u0635\u0641 \u0627\u0644\u0648\u062d\u062f\u0629 \u0627\u0644\u0637\u0628\u0642\u064a\u0629 \u0627\u0644\u0627\u0641\u062a\u0631\u0627\u0636\u064a\u0629',
        'CON':       '\u0645\u0631\u062c\u0639 \u0627\u0644\u0648\u062d\u062f\u0629 \u0627\u0644\u0627\u0633\u062a\u0645\u0631\u0627\u0631\u064a\u0629',
        'Combinar':  '\u0648\u0635\u0641 \u0627\u0644\u0645\u0648\u0635\u0644',
        'Extractor': '\u0648\u0635\u0641 \u0627\u0644\u0645\u0633\u062a\u062e\u0631\u062c',
        'SUS':       '\u0648\u0635\u0641',
        'SF':        '\u0648\u0635\u0641',
        'DOC':       '\u0645\u0631\u062c\u0639 \u0627\u0644\u062a\u0648\u062b\u064a\u0642',
    },
    'ca': {
        'property':  'Descripci\u00f3 de la propietat',
        'USV':       'Descripci\u00f3 de la Unitat Estratigr\u00e0fica Virtual',
        'CON':       'Refer\u00e8ncia a la Unitat Continuativa',
        'Combinar':  'Descripci\u00f3 del connector',
        'Extractor': 'Descripci\u00f3 de l\u2019extractor',
        'SUS':       'Descripci\u00f3',
        'SF':        'Descripci\u00f3',
        'DOC':       'Refer\u00e8ncia documental',
    },
    'ro': {
        'property':  'Descrierea propriet\u0103\u021bii',
        'USV':       'Descrierea Unit\u0103\u021bii Stratigrafice Virtuale',
        'CON':       'Referin\u021b\u0103 la Unitatea Continuativ\u0103',
        'Combinar':  'Descrierea conectorului',
        'Extractor': 'Descrierea extractorului',
        'SUS':       'Descriere',
        'SF':        'Descriere',
        'DOC':       'Referin\u021b\u0103 documentar\u0103',
    },
    'pt': {
        'property':  'Descri\u00e7\u00e3o da propriedade',
        'USV':       'Descri\u00e7\u00e3o da Unidade Estratigr\u00e1fica Virtual',
        'CON':       'Refer\u00eancia \u00e0 Unidade Continuativa',
        'Combinar':  'Descri\u00e7\u00e3o do conector',
        'Extractor': 'Descri\u00e7\u00e3o do extrator',
        'SUS':       'Descri\u00e7\u00e3o',
        'SF':        'Descri\u00e7\u00e3o',
        'DOC':       'Refer\u00eancia documental',
    },
    'el': {
        'property':  '\u03a0\u03b5\u03c1\u03b9\u03b3\u03c1\u03b1\u03c6\u03ae \u03b9\u03b4\u03b9\u03cc\u03c4\u03b7\u03c4\u03b1\u03c2',
        'USV':       '\u03a0\u03b5\u03c1\u03b9\u03b3\u03c1\u03b1\u03c6\u03ae \u0395\u03b9\u03ba\u03bf\u03bd\u03b9\u03ba\u03ae\u03c2 \u03a3\u03c4\u03c1\u03c9\u03bc\u03b1\u03c4\u03bf\u03b3\u03c1\u03b1\u03c6\u03b9\u03ba\u03ae\u03c2 \u039c\u03bf\u03bd\u03ac\u03b4\u03b1\u03c2',
        'CON':       '\u0391\u03bd\u03b1\u03c6\u03bf\u03c1\u03ac \u03c3\u03c4\u03b7 \u039c\u03bf\u03bd\u03ac\u03b4\u03b1 \u03a3\u03c5\u03bd\u03ad\u03c7\u03b5\u03b9\u03b1\u03c2',
        'Combinar':  '\u03a0\u03b5\u03c1\u03b9\u03b3\u03c1\u03b1\u03c6\u03ae \u03c3\u03c5\u03bd\u03b4\u03ad\u03c3\u03bc\u03bf\u03c5',
        'Extractor': '\u03a0\u03b5\u03c1\u03b9\u03b3\u03c1\u03b1\u03c6\u03ae \u03b5\u03be\u03b1\u03b3\u03c9\u03b3\u03ad\u03b1',
        'SUS':       '\u03a0\u03b5\u03c1\u03b9\u03b3\u03c1\u03b1\u03c6\u03ae',
        'SF':        '\u03a0\u03b5\u03c1\u03b9\u03b3\u03c1\u03b1\u03c6\u03ae',
        'DOC':       '\u0391\u03bd\u03b1\u03c6\u03bf\u03c1\u03ac \u03c4\u03b5\u03ba\u03bc\u03b7\u03c1\u03af\u03c9\u03c3\u03b7\u03c2',
    },
}


def get_unit_type_label(unit_type, lang):
    """Return a localized label for *unit_type* (used by change_label)."""
    labels = _UNIT_TYPE_LABELS.get(lang, _UNIT_TYPE_LABELS['en'])
    # USV* types share one label
    if unit_type.startswith('USV'):
        return labels.get('USV', '')
    return labels.get(unit_type, '')


# ---------------------------------------------------------------------------
# Stratigraphic Relationships (10 terms x 10 languages)
# ---------------------------------------------------------------------------
# Index:  0=Uguale a  1=Si lega a  2=Copre  3=Coperto da  4=Riempie
#         5=Riempito da  6=Taglia  7=Tagliato da  8=Si appoggia a  9=Gli si appoggia

RELATIONSHIPS = {
    'it': ['Uguale a', 'Si lega a', 'Copre', 'Coperto da',
           'Riempie', 'Riempito da', 'Taglia', 'Tagliato da',
           'Si appoggia a', 'Gli si appoggia'],
    'en': ['Same as', 'Connected to', 'Covers', 'Covered by',
           'Fills', 'Filled by', 'Cuts', 'Cut by',
           'Abuts', 'Supports'],
    'de': ['Entspricht', 'Bindet an', 'Liegt \u00fcber', 'Liegt unter',
           'Verf\u00fcllt', 'Wird verf\u00fcllt durch', 'Schneidet', 'Wird geschnitten',
           'St\u00fctzt sich auf', 'Wird gest\u00fctzt von'],
    'es': ['Igual a', 'Se liga a', 'Cubre', 'Cubierto por',
           'Rellena', 'Rellenado por', 'Corta', 'Cortado por',
           'Se apoya en', 'Le se apoya'],
    'fr': ['\u00c9gal \u00e0', 'Se lie \u00e0', 'Couvre', 'Couvert par',
           'Remplit', 'Rempli par', 'Coupe', 'Coup\u00e9 par',
           'S\u2019appuie sur', 'Lui s\u2019appuie'],
    'ar': ['\u0645\u0633\u0627\u0648\u064a \u0644', '\u064a\u0631\u062a\u0628\u0637 \u0628', '\u064a\u063a\u0637\u064a', '\u0645\u063a\u0637\u0649 \u0645\u0646',
           '\u064a\u0645\u0644\u0623', '\u0645\u0645\u062a\u0644\u0626 \u0645\u0646', '\u064a\u0642\u0637\u0639', '\u0645\u0642\u0637\u0648\u0639 \u0645\u0646',
           '\u064a\u0633\u062a\u0646\u062f \u0625\u0644\u0649', '\u064a\u0633\u062a\u0646\u062f \u0639\u0644\u064a\u0647'],
    'ca': ['Igual a', 'Es lliga a', 'Cobreix', 'Cobert per',
           'Omple', 'Omplert per', 'Talla', 'Tallat per',
           'S\u2019recolza en', 'Li es recolza'],
    'ro': ['Egal cu', 'Se leag\u0103 de', 'Acoper\u0103', 'Acoperit de',
           'Umple', 'Umplut de', 'Taie', 'T\u0103iat de',
           'Se sprijin\u0103 pe', 'I se sprijin\u0103'],
    'pt': ['Igual a', 'Liga-se a', 'Cobre', 'Coberto por',
           'Preenche', 'Preenchido por', 'Corta', 'Cortado por',
           'Apoia-se em', 'Apoiado por'],
    'el': ['\u038a\u03c3\u03bf \u03bc\u03b5', '\u03a3\u03c5\u03bd\u03b4\u03ad\u03b5\u03c4\u03b1\u03b9 \u03bc\u03b5', '\u039a\u03b1\u03bb\u03cd\u03c0\u03c4\u03b5\u03b9', '\u039a\u03b1\u03bb\u03cd\u03c0\u03c4\u03b5\u03c4\u03b1\u03b9 \u03b1\u03c0\u03cc',
           '\u0393\u03b5\u03bc\u03af\u03b6\u03b5\u03b9', '\u0393\u03b5\u03bc\u03af\u03b6\u03b5\u03c4\u03b1\u03b9 \u03b1\u03c0\u03cc', '\u03a4\u03ad\u03bc\u03bd\u03b5\u03b9', '\u03a4\u03ad\u03bc\u03bd\u03b5\u03c4\u03b1\u03b9 \u03b1\u03c0\u03cc',
           '\u0395\u03c6\u03ac\u03c0\u03c4\u03b5\u03c4\u03b1\u03b9', '\u03a5\u03c0\u03bf\u03c3\u03c4\u03b7\u03c1\u03af\u03b6\u03b5\u03b9'],
}

# Symbol operators appended after the 10 relationship terms
_SYMBOL_OPS = ['>', '<', '<<', '>>', '<->', '']


def get_relationship_values(lang):
    """Return the full list for combobox delegates (10 terms + symbols)."""
    terms = RELATIONSHIPS.get(lang, RELATIONSHIPS['en'])
    return terms + _SYMBOL_OPS


# ---------------------------------------------------------------------------
# Inverse Relationship Map
# ---------------------------------------------------------------------------
# Built automatically: for each language, index pairs (0,0), (1,1), (2,3),
# (4,5), (6,7), (8,9) are reciprocals, plus symbol operators.

_INVERSE_PAIRS = [(0, 0), (1, 1), (2, 3), (3, 2), (4, 5), (5, 4),
                  (6, 7), (7, 6), (8, 9), (9, 8)]

_SYMBOL_INVERSES = {
    '>>': '<<', '<<': '>>', '>': '<', '<': '>',
    '<->': '<->',
}

INVERSE_MAP = {}
for _lang, _terms in RELATIONSHIPS.items():
    for _a, _b in _INVERSE_PAIRS:
        INVERSE_MAP[_terms[_a]] = _terms[_b]
INVERSE_MAP.update(_SYMBOL_INVERSES)


def get_inverse_relationship(term):
    """Return the inverse/reciprocal of *term*. Falls back to *term* itself."""
    return INVERSE_MAP.get(term, term)


# ---------------------------------------------------------------------------
# Relationship Group Sets (across all languages)
# ---------------------------------------------------------------------------
# Group by semantic index position across all languages.

def _build_group(*indices):
    """Build a set of all terms at the given indices across all languages."""
    s = set()
    for terms in RELATIONSHIPS.values():
        for i in indices:
            s.add(terms[i])
    return frozenset(s)


# "Same as" group (index 0)
SAME_AS_GROUP = _build_group(0)
CONTEMPORARY_GROUP = SAME_AS_GROUP  # alias

# "Connected to" / "Si lega a" group (index 1)
CONNECTED_GROUP = _build_group(1)

# "Covers" group (index 2) — active direction
COVERS_GROUP = _build_group(2)

# "Covered by" group (index 3) — passive direction
COVERED_BY_GROUP = _build_group(3)

# "Fills" group (index 4)
FILLS_GROUP = _build_group(4)

# "Filled by" group (index 5)
FILLED_BY_GROUP = _build_group(5)

# "Cuts" group (index 6) — active direction
CUTS_GROUP = _build_group(6)

# "Cut by" group (index 7) — passive direction
CUT_BY_GROUP = _build_group(7)

# "Abuts" / "Si appoggia a" group (index 8)
ABUTS_GROUP = _build_group(8)

# "Supports" / "Gli si appoggia" group (index 9)
SUPPORTS_GROUP = _build_group(9)

# Composite groups used by matrix builders
# "data" list: Covers + Abuts + Fills + Same + Connected (positive physical)
POSITIVE_GROUP = COVERS_GROUP | ABUTS_GROUP | FILLS_GROUP | SAME_AS_GROUP | CONNECTED_GROUP
# "negative" list: Cuts
NEGATIVE_GROUP = CUTS_GROUP
# Passive groups (need relationship inversion in matrix)
PASSIVE_COVERS_GROUP = COVERED_BY_GROUP | FILLED_BY_GROUP
PASSIVE_CUTS_GROUP = CUT_BY_GROUP
# Contemporary group for matrix: Connected + Same + Supports
MATRIX_CONTEMPORARY_GROUP = CONNECTED_GROUP | SAME_AS_GROUP | SUPPORTS_GROUP


def is_covers_group(term):
    """Term is any language's 'Covers' equivalent."""
    return term in COVERS_GROUP


def is_covered_by_group(term):
    """Term is any language's 'Covered by' equivalent."""
    return term in COVERED_BY_GROUP


def is_fills_group(term):
    """Term is any language's 'Fills' equivalent."""
    return term in FILLS_GROUP


def is_filled_by_group(term):
    """Term is any language's 'Filled by' equivalent."""
    return term in FILLED_BY_GROUP


def is_cuts_group(term):
    """Term is any language's 'Cuts' equivalent."""
    return term in CUTS_GROUP


def is_cut_by_group(term):
    """Term is any language's 'Cut by' equivalent."""
    return term in CUT_BY_GROUP


def is_contemporary_group(term):
    """Term is any language's 'Same as' equivalent."""
    return term in SAME_AS_GROUP


def is_connected_group(term):
    """Term is any language's 'Connected to' equivalent."""
    return term in CONNECTED_GROUP


def is_abuts_group(term):
    """Term is any language's 'Abuts' equivalent."""
    return term in ABUTS_GROUP


def is_supports_group(term):
    """Term is any language's 'Supports' equivalent."""
    return term in SUPPORTS_GROUP


# ---------------------------------------------------------------------------
# All relationship terms (flat set for quick membership check)
# ---------------------------------------------------------------------------

ALL_RELATIONSHIP_TERMS = set()
for _terms in RELATIONSHIPS.values():
    ALL_RELATIONSHIP_TERMS.update(_terms)
ALL_RELATIONSHIP_TERMS = frozenset(ALL_RELATIONSHIP_TERMS)


# ---------------------------------------------------------------------------
# RELATIONSHIP_TYPES list (for backward compat with code that references it)
# ---------------------------------------------------------------------------

RELATIONSHIP_TYPES = []
for _terms in RELATIONSHIPS.values():
    for _t in _terms:
        if _t not in RELATIONSHIP_TYPES:
            RELATIONSHIP_TYPES.append(_t)
