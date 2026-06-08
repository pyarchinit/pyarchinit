"""Public API for pyArchInit ``rapporti`` ↔ canonical s3dgraphy edges.

This module is the single home for the bidirectional mapping between
pyArchInit's stratigraphic ``rapporti`` packed string format and the
canonical edge types in the s3dgraphy property graph.

Architectural baseline (decided 2026-06-04 with the EM project lead):

* **In s3dgraphy in memory**, physical/topological stratigraphic
  relationships (``copre`` / ``coperto da`` / ``taglia`` / …) are
  **first-class edges** between US-type nodes — ``overlies`` /
  ``is_overlain_by`` / ``cuts`` / etc., the canonical edge types
  declared in ``s3Dgraphy_connections_datamodel.json`` and already
  recognised by the GraphML exporter, the unified XLSX importer and
  the JSON exporter. The property graph carries the single source of
  truth.

* **In pyArchInit's `us_table.rapporti` column**, the same
  relationships are serialised as a list-of-lists Python literal
  (e.g. ``[["Copre", "12", "1", "Pompei"], …]``). pyArchInit's
  vocabulary mixes Italian and English terms; the GraphML world has
  used both depending on the file's provenance, so we accept both
  on parse and emit canonical Italian on serialise.

* **In yEd GraphML (EM 1.6 palette onwards)**, the same
  relationships are serialised again, this time as a packed string
  attribute ``physical_relationships`` on each US node — because yEd
  edges are reserved for the temporal Matrix dimension and cannot
  visually carry physical relations without polluting the layout.
  The packed format is the **same pyArchInit-native list-of-lists**
  so the GraphML ↔ pyArchInit transit is byte-identical when the
  graph between them is unmutated.

This module exposes the constants the parsers / serialisers /
dispatchers consume. The parse/serialise *functions* land in a later
commit; today's commit is purely the constants extraction from
``graphml_writer.py`` and ``graph_ingestor.py`` so the canonical
vocabulary lives in one place.

The legacy private names (``_RAPPORTI_TO_EDGE_TYPE`` etc.) remain
importable from their original modules — see the re-export shims at
the bottom of ``graphml_writer.py`` and ``graph_ingestor.py``.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Forward: pyArchInit-native label → canonical s3dgraphy edge type
# ---------------------------------------------------------------------------
#: pyArchInit ``rapporti`` labels (Italian + English) mapped to canonical
#: s3dgraphy edge types declared in
#: ``s3Dgraphy_connections_datamodel.json``.
#:
#: Used by:
#:
#: * ``s3dgraphy.sync.graph_projector`` when reading the
#:   ``us_table.rapporti`` column out of a pyArchInit DB and turning
#:   each entry into a graph edge.
#: * ``s3dgraphy.sync.graphml_writer`` for the same translation step
#:   when an external pipeline feeds ``rapporti``-style strings into
#:   the writer's pre-export enrichment.
#:
#: pyArchInit's vocabulary is loose — older sites have Italian terms,
#: newer ones with English UIs have English. Both are accepted on
#: import. On serialise we emit the verbose Italian form (or shorthand
#: tokens for non-canonical unit types — see ``RAPPORTI_SHORTHAND``).
RAPPORTI_TO_EDGE_TYPE: dict[str, str] = {
    # Italian
    "copre": "overlies",
    "coperto da": "is_overlain_by",
    "taglia": "cuts",
    "tagliato da": "is_cut_by",
    "riempie": "fills",
    "riempito da": "is_filled_by",
    "uguale a": "is_physically_equal_to",
    "si lega a": "is_bonded_to",
    "si appoggia a": "abuts",
    "gli si appoggia": "is_abutted_by",
    # English
    "covers": "overlies",
    "covered by": "is_overlain_by",
    "cuts": "cuts",
    "cut by": "is_cut_by",
    "fills": "fills",
    "filled by": "is_filled_by",
    "same as": "is_physically_equal_to",
    "bonds with": "is_bonded_to",
    "abuts": "abuts",
    "supports": "is_abutted_by",   # English reciprocal of "Abuts"
}


# ---------------------------------------------------------------------------
# Full multilingual coverage
# ---------------------------------------------------------------------------
# pyArchInit (and any EM tool with a localized UI) stores relationship labels
# in the user's language, so parse_rapporti must recognise them all —
# otherwise a graph projected from a non-IT/EN site builds no edges, and a
# reciprocity round-trip (e.g. the reciprocal of "Abuts" is "Supports" =
# is_abutted_by) silently fails. The 10×10 table below mirrors the EM/
# pyArchInit stratigraphic-relationship vocabulary (10 relations × 10 UI
# languages: it/en/de/es/fr/ar/ca/ro/pt/el).
#
# Index → canonical edge type (same order as each language's term list):
_REL_INDEX_EDGE_TYPE: tuple[str, ...] = (
    "is_physically_equal_to",  # 0  Uguale a / Same as
    "is_bonded_to",            # 1  Si lega a / Connected to
    "overlies",                # 2  Copre / Covers
    "is_overlain_by",          # 3  Coperto da / Covered by
    "fills",                   # 4  Riempie / Fills
    "is_filled_by",            # 5  Riempito da / Filled by
    "cuts",                    # 6  Taglia / Cuts
    "is_cut_by",               # 7  Tagliato da / Cut by
    "abuts",                   # 8  Si appoggia a / Abuts
    "is_abutted_by",           # 9  Gli si appoggia / Supports
)

#: 10 relationship terms per language (same indices as _REL_INDEX_EDGE_TYPE).
_REL_TERMS_BY_LANG: dict[str, tuple[str, ...]] = {
    "it": ("Uguale a", "Si lega a", "Copre", "Coperto da", "Riempie",
           "Riempito da", "Taglia", "Tagliato da", "Si appoggia a",
           "Gli si appoggia"),
    "en": ("Same as", "Connected to", "Covers", "Covered by", "Fills",
           "Filled by", "Cuts", "Cut by", "Abuts", "Supports"),
    "de": ("Entspricht", "Bindet an", "Liegt über", "Liegt unter",
           "Verfüllt", "Wird verfüllt durch", "Schneidet",
           "Wird geschnitten", "Stützt sich auf", "Wird gestützt von"),
    "es": ("Igual a", "Se liga a", "Cubre", "Cubierto por", "Rellena",
           "Rellenado por", "Corta", "Cortado por", "Se apoya en",
           "Le se apoya"),
    "fr": ("Égal à", "Se lie à", "Couvre", "Couvert par",
           "Remplit", "Rempli par", "Coupe", "Coupé par",
           "S’appuie sur", "Lui s’appuie"),
    "ar": ("مساوي ل", "يرتبط ب",
           "يغطي", "مغطى من",
           "يملأ", "ممتلئ من",
           "يقطع", "مقطوع من",
           "يستند إلى",
           "يستند عليه"),
    "ca": ("Igual a", "Es lliga a", "Cobreix", "Cobert per", "Omple",
           "Omplert per", "Talla", "Tallat per", "S’recolza en",
           "Li es recolza"),
    "ro": ("Egal cu", "Se leagă de", "Acoperă", "Acoperit de",
           "Umple", "Umplut de", "Taie", "Tăiat de",
           "Se sprijină pe", "I se sprijină"),
    "pt": ("Igual a", "Liga-se a", "Cobre", "Coberto por", "Preenche",
           "Preenchido por", "Corta", "Cortado por", "Apoia-se em",
           "Apoiado por"),
    "el": ("Ίσο με", "Συνδέεται με",
           "Καλύπτει",
           "Καλύπτεται από",
           "Γεμίζει",
           "Γεμίζεται από",
           "Τέμνει", "Τέμνεται από",
           "Εφάπτεται", "Υποστηρίζει"),
}

# Fold every language's terms into RAPPORTI_TO_EDGE_TYPE (keys lowercased to
# match parse_rapporti's lookup). setdefault keeps the explicit aliases above
# (e.g. "bonds with").
for _terms in _REL_TERMS_BY_LANG.values():
    for _i, _term in enumerate(_terms):
        RAPPORTI_TO_EDGE_TYPE.setdefault(_term.lower(), _REL_INDEX_EDGE_TYPE[_i])
del _terms, _i, _term


# ---------------------------------------------------------------------------
# Inverse: canonical edge type → verbose Italian rapporti label
# ---------------------------------------------------------------------------
#: Inverse of ``RAPPORTI_TO_EDGE_TYPE`` for the verbose-Italian dispatch
#: (the form pyArchInit's Scheda US shows). Used when serialising
#: canonical edges back into the ``us_table.rapporti`` column for the
#: subset of edges whose endpoints are both canonical Harris units
#: (US / USM ↔ US / USM). For other unit-type combinations the
#: serialiser falls back to ``RAPPORTI_SHORTHAND`` instead (see
#: convention notes below).
#:
#: ``is_after`` falls back to ``Copre`` because that's the
#: stratigraphic-precedence default pyArchInit's UI assumes when no
#: more-specific physical relation is declared.
#: ``generic_connection`` falls back to ``Connesso a`` (used for
#: paradata data-flow shorthand ``>>`` / ``<<`` that travels through
#: pyArchInit as a free-text term).
EDGE_TYPE_TO_RAPPORTI_IT: dict[str, str] = {
    "overlies": "Copre",
    "is_overlain_by": "Coperto da",
    "cuts": "Taglia",
    "is_cut_by": "Tagliato da",
    "fills": "Riempie",
    "is_filled_by": "Riempito da",
    "is_physically_equal_to": "Uguale a",
    "is_bonded_to": "Si lega a",
    "abuts": "Si appoggia a",
    "is_abutted_by": "Gli si appoggia",
    "is_after": "Copre",       # default fallback for temporal precedence
    "generic_connection": "Connesso a",
}


# ---------------------------------------------------------------------------
# Shorthand tokens for relations between non-Harris unit types
# ---------------------------------------------------------------------------
#: Shorthand ``rapporti`` tokens for relations between non-US/USM units
#: (USVs / USVn / SF / CON / Combinar / Extractor / property / DOC).
#: Per pyArchInit author convention (May 2026):
#:
#: * single arrow ``>`` / ``<`` carries simple temporal precedence
#:   (used for Continuity units, ``CON``);
#: * double arrow ``>>`` / ``<<`` carries paradata-style data flow
#:   (Extractor / Combiner / property / DOC chains, expressed as
#:   ``generic_connection`` edges so the GraphML writer's paradata
#:   filter handles them correctly).
#:
#: Each value is ``(edge_type, swap)``:
#:
#: * ``swap=False`` means emit the edge with source / target as the
#:   user wrote them (``A > B`` → ``A is_after B``);
#: * ``swap=True`` means swap source / target (``A < B`` →
#:   ``B is_after A``).
#:
#: Mirrored in ``EDGE_TYPE_DIRECTION_FORWARD`` for the
#: serialise direction.
RAPPORTI_SHORTHAND: dict[str, tuple[str, bool]] = {
    ">":  ("is_after", False),            # A > B  ⇒  A is_after B
    "<":  ("is_after", True),             # A < B  ⇒  B is_after A
    ">>": ("generic_connection", False),  # A >> B ⇒  A → B
    "<<": ("generic_connection", True),   # A << B ⇒  B → A
}


# ---------------------------------------------------------------------------
# Edge-type direction for shorthand serialise
# ---------------------------------------------------------------------------
#: Per-edge-type direction. ``True`` means the rapporti token reads as
#: ``>`` / ``>>`` (source covers target); ``False`` means ``<`` / ``<<``
#: (source is covered by target).
#:
#: Used by the serialiser when the dispatch logic falls back to
#: shorthand for non-canonical unit-type endpoints.
EDGE_TYPE_DIRECTION_FORWARD: dict[str, bool] = {
    "overlies": True,
    "is_overlain_by": False,
    "cuts": True,
    "is_cut_by": False,
    "fills": True,
    "is_filled_by": False,
    "is_physically_equal_to": True,   # equality conventionally `>`
    "is_bonded_to": True,
    "abuts": True,
    "is_abutted_by": False,
    "is_after": True,
    "is_before": False,
    "generic_connection": True,
    "extracted_from": True,
    "combines": True,
    "has_property": True,
}


# ---------------------------------------------------------------------------
# Unit-type frozensets driving the verbose-vs-shorthand dispatch
# ---------------------------------------------------------------------------
#: Localized US / USM ``unita_tipo`` code → canonical code. pyArchInit
#: localizes ONLY the US / USM abbreviations per UI language (its
#: ``pyarchinit_i18n_stratigraphic.UNIT_TYPE_ABBREV`` is the source of
#: truth). This module is the pyArchInit↔canonical bridge, and the
#: prefix-strip regex above already enumerates SU|SE|WSU|MSE|UE|…, so the
#: gating set lives here too. The mapping doubles as the normalization
#: source: any code path that needs the canonical form calls
#: :func:`canonical_unita_tipo`. ``attributes['unita_tipo']`` is kept
#: VERBATIM (original code) elsewhere so round-trip stays byte-identical;
#: only the verbose/shorthand dispatch and the projector's stratigraphic
#: gating read through this alias map.
#:
#:   US  → US (it/fr/ro) · SU (en/ar) · SE (de) · UE (es/ca/pt) · ΣΜ (el)
#:   USM → USM (it/fr) · WSU (en/ar) · MSE (de) · UEM (es/ca/pt) ·
#:         USZ (ro) · ΤΣΜ (el)
UNITA_TIPO_CANONICAL: dict[str, str] = {
    "US": "US", "SU": "US", "SE": "US", "UE": "US", "ΣΜ": "US",
    "USM": "USM", "WSU": "USM", "MSE": "USM", "UEM": "USM",
    "USZ": "USM", "ΤΣΜ": "USM",
}


def canonical_unita_tipo(unita_tipo) -> str:
    """Map a (possibly localized) US/USM code to its canonical form.

    Non-US/USM codes (USV*, SF, CON, DOC, …) and unknown values pass
    through unchanged.
    """
    return UNITA_TIPO_CANONICAL.get(unita_tipo, unita_tipo)


#: Unit types where both endpoints get the verbose dispatch ("Copre"/
#: "Covers"/…, "Coperto da"/"Covered by"/…). All language variants of the
#: Harris US/USM atoms, derived from the alias map so the two never drift.
CANONICAL_UNIT_TYPES: frozenset[str] = frozenset(UNITA_TIPO_CANONICAL)


#: Continuity unit type. Single-arrow shorthand ``>`` / ``<`` is
#: reserved for relations where at least one endpoint is a CON.
CONTINUITY_UNIT_TYPES: frozenset[str] = frozenset({"CON"})


# ---------------------------------------------------------------------------
# Python class name → pyArchInit unita_tipo column value
# ---------------------------------------------------------------------------
#: Recovery lookup for ``unita_tipo`` when a GraphML round-trip strips
#: the attribute metadata from a node. The only semantic info that
#: survives such a round-trip is the s3dgraphy Python class name; we
#: use it to recover the pyArchInit ``unita_tipo`` code so the
#: verbose-vs-shorthand dispatch in :func:`select_rapporti_label` and
#: the row-routing in :class:`GraphIngestor` keep working.
#:
#: Several entries are aliases of one another (``StructuralVirtualStratigraphicUnit``
#: vs ``VirtualStratigraphicStructuralUnit``) because historical
#: s3dgraphy classes have been renamed twice and old GraphML files
#: still carry the old names. Keep both spellings.
S3DGRAPHY_TYPE_TO_UNITA_TIPO: dict[str, str] = {
    "StratigraphicUnit": "US",
    "StructuralVirtualStratigraphicUnit": "USVs",
    "VirtualStratigraphicStructuralUnit": "USVs",
    "VirtualStratigraphicNonStructuralUnit": "USVn",
    "NonStructuralVirtualStratigraphicUnit": "USVn",
    "StratigraphicUnitMasonry": "USM",
    "DocumentaryStratigraphicUnit": "USD",
    "SpecialFindUnit": "SF",
    "VirtualSpecialFindUnit": "VSF",
    "TransformationStratigraphicUnit": "TSU",
    "WorkingUnit": "UL",
    "ContinuityNode": "CON",
    "DocumentNode": "DOC",
    "ExtractorNode": "Extractor",
    "CombinerNode": "Combinar",
    # yE-D (5.8.0-alpha): VirtualActivity used by SYNTHETIC folder
    # policy in yed_import_pipeline.py for folder-derived synthetic
    # us_table rows (unita_tipo='VA').
    "VirtualActivity": "VA",
    # s3dgraphy-bump (5.8.1-alpha): ReusedSpecialFind ("spolia"),
    # introduced in s3dgraphy 0.1.42 (DP-26). Family=real, non-series.
    # Routed to us_table by yE-D pipeline (unita_tipo='RSF').
    "ReusedSpecialFind": "RSF",
}


# ---------------------------------------------------------------------------
# Multilingual unita-tipo prefix strip
# ---------------------------------------------------------------------------
#
# Pyarchinit displays US labels with language-aware prefixes (US/SU/SE/UE/...,
# USM/WSU/MSE/..., USVs/USVn both rendered as "USV<n>", SF/VSF, CON,
# D./C. for paradata). For round-trip serialisation we strip ANY of
# these prefixes (longest match first) so the bare US identifier
# survives (e.g. "6", "102", "103a").

import re as _re

_US_PREFIX_PATTERN = _re.compile(
    r"^(?P<prefix>"
    r"USVs|USVn|USVA|USVB|USVC|USV|"
    r"USM|USD|USN|"
    r"VSF|SF|"
    r"CON|"
    r"WSU|MSE|TSU|SUS|UE|UM|UC|UL|"
    r"D\.|C\.|"
    r"US|SU|SE"
    r")\s*",
    _re.IGNORECASE,
)


def strip_us_prefix(name: str) -> str:
    """Strip the unita-tipo prefix from a node name.

    Examples::

        strip_us_prefix("USM6")    == "6"
        strip_us_prefix("USV102")  == "102"
        strip_us_prefix("US103a")  == "103a"
        strip_us_prefix("D.4001")  == "4001"
        strip_us_prefix("C.900")   == "900"
        strip_us_prefix("6")       == "6"   # no prefix → unchanged
    """
    if not name:
        return name
    m = _US_PREFIX_PATTERN.match(str(name))
    if m:
        return str(name)[m.end():]
    return str(name)


# ---------------------------------------------------------------------------
# Unita_tipo resolution helpers
# ---------------------------------------------------------------------------

def resolve_unita_tipo_for_dispatch(node) -> str | None:
    """Best-effort lookup of pyarchinit ``unita_tipo`` for *node*.

    Used by :func:`select_rapporti_label` to decide between verbose
    Italian (when both endpoints are canonical Harris units) and
    shorthand ``>`` / ``<`` / ``>>`` / ``<<`` (everything else).

    Lookup order:

    1. ``node.attributes['unita_tipo']`` (set by the AI03 enrichment
       in :mod:`graph_projector`);
    2. :data:`S3DGRAPHY_TYPE_TO_UNITA_TIPO` keyed by the node's Python
       class name (the fallback for graphs that survived a GraphML
       round-trip without preserving attributes).

    Returns ``None`` when neither source has a value — callers treat
    "unknown" as "fall through to shorthand" in the dispatcher.
    """
    if node is None:
        return None
    attrs = getattr(node, "attributes", None) or {}
    ut = attrs.get("unita_tipo")
    if ut:
        return str(ut)
    cls_name = type(node).__name__
    return S3DGRAPHY_TYPE_TO_UNITA_TIPO.get(cls_name)


def select_rapporti_label(edge_type: str,
                          src_unita_tipo: str | None,
                          tgt_unita_tipo: str | None) -> str:
    """Pick the pyarchinit ``rapporti`` token for an edge.

    Dispatch table:

    * both endpoints ∈ :data:`CANONICAL_UNIT_TYPES` (US / USM) →
      verbose Italian (``Copre`` / ``Coperto da`` / …) from
      :data:`EDGE_TYPE_TO_RAPPORTI_IT`;
    * either endpoint ∈ :data:`CONTINUITY_UNIT_TYPES` (CON) →
      single arrow ``>`` / ``<`` per the temporal-precedence
      shorthand;
    * otherwise → double arrow ``>>`` / ``<<`` (paradata-style data
      flow shorthand).

    Direction (``>`` vs ``<``, ``>>`` vs ``<<``) is read from
    :data:`EDGE_TYPE_DIRECTION_FORWARD`: ``overlies`` / ``cuts`` /
    ``is_after`` / etc. emit ``>`` (source covers target); their
    inverses emit ``<``.
    """
    src = src_unita_tipo or ""
    tgt = tgt_unita_tipo or ""
    both_canonical = (src in CANONICAL_UNIT_TYPES
                      and tgt in CANONICAL_UNIT_TYPES)
    if both_canonical:
        return EDGE_TYPE_TO_RAPPORTI_IT.get(edge_type, str(edge_type))
    forward = EDGE_TYPE_DIRECTION_FORWARD.get(edge_type, True)
    is_continuity = (src in CONTINUITY_UNIT_TYPES
                     or tgt in CONTINUITY_UNIT_TYPES)
    if is_continuity:
        return ">" if forward else "<"
    return ">>" if forward else "<<"


# ---------------------------------------------------------------------------
# Edge types that are NOT physical/stratigraphic rapporti
# ---------------------------------------------------------------------------
#: Edges with these types are intentionally **excluded** from the
#: pyarchinit ``rapporti`` column on serialise: they encode
#: epoch / paradata / property relationships that live in different
#: pyarchinit tables (or are paradata internal to s3dgraphy and have
#: no pyarchinit counterpart at all).
#:
#: Kept here (rather than as a magic constant inside ``serialize``)
#: so callers can introspect the exclusion list when debugging
#: missing rapporti.
NON_RAPPORTI_EDGE_TYPES: frozenset[str] = frozenset({
    "has_first_epoch",
    "has_paradata_nodegroup",
    "has_property",
    "extracted_from",
    "combines",
    "survive_in_epoch",
    "has_same_time",
})


# ---------------------------------------------------------------------------
# Public parse / serialize API
# ---------------------------------------------------------------------------

def parse_rapporti(value):
    """Parse a pyarchinit ``us_table.rapporti`` value into canonical
    relations ready to materialise as graph edges.

    *value* can be:

    * a ``str`` carrying the Python-literal serialisation pyarchinit
      writes to the column (``"[['Copre', '12', '1', 'Pompei'], ...]"``);
    * a ``list`` already parsed by the caller (``[['Copre', '12', '1',
      'Pompei'], ...]``);
    * ``None`` or empty — returns ``[]``.

    Returns a list of 5-tuples ``(edge_type, target_us, area, sito, swap)``:

    * ``edge_type`` — the canonical s3dgraphy edge type (e.g.
      ``overlies``, ``is_after``, ``generic_connection``);
    * ``target_us`` — the second element of the pyarchinit tuple (the
      target US identifier as a bare string, no prefix);
    * ``area``, ``sito`` — the third and fourth elements; ``None`` when
      the source row was a short 2-tuple ``["Copre", "12"]``;
    * ``swap`` — ``True`` when the shorthand token requested a
      source/target swap (``<`` and ``<<``). The caller materialises
      the edge as ``source_us is_after target_us`` after the swap.

    Labels not in :data:`RAPPORTI_TO_EDGE_TYPE` nor
    :data:`RAPPORTI_SHORTHAND` are silently skipped — the caller
    decides whether to log a warning. Malformed list entries (not a
    list, or empty) are skipped likewise.

    The function is pure and side-effect-free; it does not mutate the
    input.
    """
    items = _coerce_to_list(value)
    out = []
    for entry in items:
        if not isinstance(entry, (list, tuple)) or not entry:
            continue
        raw_label = str(entry[0]) if entry[0] is not None else ""
        named = raw_label.strip().lower()
        edge_type = RAPPORTI_TO_EDGE_TYPE.get(named)
        swap = False
        if edge_type is None:
            shorthand = RAPPORTI_SHORTHAND.get(raw_label.strip())
            if shorthand is None:
                continue
            edge_type, swap = shorthand
        target_us = str(entry[1]).strip() if len(entry) > 1 and entry[1] is not None else ""
        area = str(entry[2]).strip() if len(entry) > 2 and entry[2] is not None else None
        sito = str(entry[3]).strip() if len(entry) > 3 and entry[3] is not None else None
        out.append((edge_type, target_us, area, sito, swap))
    return out


def _coerce_to_list(value):
    """Internal: turn the various forms of a pyarchinit ``rapporti``
    value into a flat list of entries.

    Accepted shapes:

    * ``None`` or empty string / list → ``[]``
    * ``list`` → returned as-is (assumed to be the parsed list-of-lists)
    * ``str`` → ``ast.literal_eval`` round-trip; non-list results are
      treated as empty (defensive); ``ValueError`` / ``SyntaxError``
      bubble up as ``[]`` rather than raising (the caller is usually
      a row-by-row importer and one malformed row shouldn't break the
      whole batch).
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if not isinstance(value, str):
        return []
    if not value.strip():
        return []
    import ast
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []
    if isinstance(parsed, list):
        return parsed
    return []


#: Arrow tokens emitted by :func:`select_rapporti_label` for
#: non-canonical endpoints. When the dispatch returns one of these we do
#: NOT override it with a verbose row term (virtual units keep ``>>`` /
#: ``<<``, continuity keeps ``>`` / ``<``).
_SHORTHAND_TOKENS: frozenset[str] = frozenset({">", "<", ">>", "<<"})


def _source_rapporti_label(src_node, target_us: str, edge_type: str):
    """Original pyArchInit ``rapporti`` term on *src_node* for *target_us*.

    The d13 packed string is wire format that should byte-match the
    originating ``us_table.rapporti``, so for a verbose relation we anchor
    the label on the source row's own stored term (in the site's UI
    language — "Covers" / "Couvre" / "Copre" / …) rather than the canonical
    Italian. The label language can't be reconstructed from ``edge_type``
    alone (e.g. "US" is shared by it / fr / ro), so the node's own term is
    the only reliable source.

    Returned in the canonical display casing (first letter upper, rest
    lower — the form pyArchInit shows). Matching prefers the entry whose
    label maps to the SAME canonical ``edge_type`` (disambiguates multiple
    relations to one target), falling back to any verbose entry pointing at
    ``target_us``. Returns ``None`` when the node carries no usable
    ``rapporti`` attribute (e.g. a yEd-imported graph) — the caller then
    keeps the canonical dispatch label.
    """
    attrs = getattr(src_node, "attributes", None) or {}
    fallback = None
    for entry in _coerce_to_list(attrs.get("rapporti")):
        if not isinstance(entry, (list, tuple)) or len(entry) < 2:
            continue
        lbl = str(entry[0]).strip()
        tgt = str(entry[1]).strip()
        if tgt != str(target_us) or not lbl or lbl in _SHORTHAND_TOKENS:
            continue
        lbl = lbl.capitalize()
        if RAPPORTI_TO_EDGE_TYPE.get(lbl.lower()) == edge_type:
            return lbl
        if fallback is None:
            fallback = lbl
    return fallback


def serialize_rapporti_from_edges(graph, default_sito: str):
    """Walk *graph*'s edges and produce per-US rapporti lists ready
    for the pyarchinit ``us_table.rapporti`` column.

    Output: a ``dict`` mapping source node id to a list of
    ``[label, target_us, area, sito]`` entries — the pyarchinit
    list-of-lists serialisation, with verbose-Italian or shorthand
    labels picked by :func:`select_rapporti_label`.

    *default_sito* is the site name to stamp into the 4th element of
    every entry, regardless of what the graph might carry — this
    matches the "import to a NEW sito" workflow consumers run
    (``GraphIngestor.populate_list`` passes the user's chosen site).

    Behaviour notes:

    * Edges with types in :data:`NON_RAPPORTI_EDGE_TYPES` are
      excluded (paradata / property / epoch edges that don't belong
      in the pyarchinit ``rapporti`` column).
    * Target US is read from ``tgt_node.attributes['us']`` when
      present, otherwise derived from ``tgt_node.name`` via
      :func:`strip_us_prefix`.
    * Area defaults to ``"1"`` (compatible with most legacy
      pyarchinit data).
    * Duplicates within a source are dropped — external graphml may
      carry redundant edges for the same ``(label, target)`` and we
      keep the column clean.
    """
    by_id = {}
    for n in graph.nodes:
        nid = getattr(n, "node_id", None)
        if nid:
            by_id[nid] = n
    out: dict[str, list[list]] = {}
    for e in getattr(graph, "edges", None) or []:
        src = getattr(e, "edge_source", None)
        tgt = getattr(e, "edge_target", None)
        et = getattr(e, "edge_type", None)
        if not src or not tgt or not et:
            continue
        if et in NON_RAPPORTI_EDGE_TYPES:
            continue
        src_node = by_id.get(src)
        tgt_node = by_id.get(tgt)
        if tgt_node is None:
            continue
        src_unita_tipo = resolve_unita_tipo_for_dispatch(src_node)
        tgt_unita_tipo = resolve_unita_tipo_for_dispatch(tgt_node)
        tgt_attrs = getattr(tgt_node, "attributes", None) or {}
        tgt_us = tgt_attrs.get("us")
        if not tgt_us:
            tgt_name = getattr(tgt_node, "name", None)
            if not tgt_name:
                continue
            tgt_us = strip_us_prefix(str(tgt_name))
        rapporti_label = select_rapporti_label(
            et, src_unita_tipo, tgt_unita_tipo)
        # For a verbose relation (both endpoints real US/USM, any language)
        # anchor the term on the source row's own rapporti column so the
        # packed string byte-matches the DB in the site's UI language;
        # fall back to the canonical label when the source carries no
        # rapporti attribute (e.g. yEd-imported graphs). Virtual units
        # (``>>`` / ``<<``) and continuity (``>`` / ``<``) keep shorthand.
        if rapporti_label not in _SHORTHAND_TOKENS:
            original = _source_rapporti_label(src_node, str(tgt_us), et)
            if original:
                rapporti_label = original
        tgt_area = str(tgt_attrs.get("area") or "1")
        tgt_sito = default_sito
        rapporto = [rapporti_label, str(tgt_us), tgt_area, tgt_sito]
        bucket = out.setdefault(src, [])
        if rapporto not in bucket:
            bucket.append(rapporto)
    return out


__all__ = [
    # Vocabulary constants (commit 1)
    "RAPPORTI_TO_EDGE_TYPE",
    "EDGE_TYPE_TO_RAPPORTI_IT",
    "RAPPORTI_SHORTHAND",
    "EDGE_TYPE_DIRECTION_FORWARD",
    "UNITA_TIPO_CANONICAL",
    "canonical_unita_tipo",
    "CANONICAL_UNIT_TYPES",
    "CONTINUITY_UNIT_TYPES",
    "NON_RAPPORTI_EDGE_TYPES",
    # Type / prefix helpers (commit 2)
    "S3DGRAPHY_TYPE_TO_UNITA_TIPO",
    "strip_us_prefix",
    "resolve_unita_tipo_for_dispatch",
    "select_rapporti_label",
    # Parser / serialiser (commit 2)
    "parse_rapporti",
    "serialize_rapporti_from_edges",
]

