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
}


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
#: Unit types where both endpoints get the verbose Italian dispatch
#: ("Copre", "Coperto da", ...). Stratigraphic Harris atoms only.
CANONICAL_UNIT_TYPES: frozenset[str] = frozenset({"US", "USM"})


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
        rapporti_label = select_rapporti_label(
            et, src_unita_tipo, tgt_unita_tipo)
        tgt_attrs = getattr(tgt_node, "attributes", None) or {}
        tgt_us = tgt_attrs.get("us")
        if not tgt_us:
            tgt_name = getattr(tgt_node, "name", None)
            if not tgt_name:
                continue
            tgt_us = strip_us_prefix(str(tgt_name))
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

