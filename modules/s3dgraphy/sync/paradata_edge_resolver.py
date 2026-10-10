"""Datamodel-driven refinement of ``generic_connection`` edges into the
specific Extended-Matrix paradata edge types (post-projection pass).

Why
---
pyArchInit stores virtual / paradata links in ``us_table.rapporti`` with the
EM shorthand ``>>`` / ``<<``, which :func:`parse_rapporti` resolves to the
generic ``generic_connection`` edge. The Extended Matrix data model, however,
distinguishes those links by the *node types* at each end:

* Extractor → Document  ⇒ ``extracted_from``
* Combiner  → Extractor ⇒ ``combines``
* (Strat|Document) → Property ⇒ ``has_property``
* Property → (Extractor|Combiner) ⇒ ``has_data_provenance``
* (Strat|SF|USV) → Document ⇒ ``has_documentation``
* (SF|VSF) → StratigraphicUnit ⇒ ``is_part_of``

The rules (which node classes may be linked by which edge type) live in the
authoritative s3dgraphy data model
(``JSON_config/s3Dgraphy_connections_datamodel.json``, ``allowed_connections``).
This module reads that file — no rules are hard-coded here — and retypes each
``generic_connection`` edge to the most specific allowed type, swapping the
endpoints when the rule is satisfied only in the reverse direction.

Combiner / Extractor never connect to a plain US/USM: no datamodel rule allows
it, so such edges simply stay ``generic_connection``.

Qt-free and pyarchinit-free: only stdlib + the vendored ``s3dgraphy`` package.
"""
from __future__ import annotations

import functools
import json
from pathlib import Path

#: Specific edge types to try, in resolution priority order. The first rule
#: that matches (in either direction) wins. ``generic_connection`` is the
#: implicit fallback and is intentionally absent.
_CANDIDATE_ORDER = (
    "extracted_from",
    "combines",
    "has_data_provenance",
    "has_property",
    "has_documentation",
    "has_visual_reference",
    "is_part_of",
)


@functools.lru_cache(maxsize=1)
def _allowed_connections():
    """``{edge_type: (frozenset(source_classes), frozenset(target_classes))}``
    for the candidate edge types, read from the s3dgraphy data model."""
    import s3dgraphy  # vendored in ext_libs
    path = (Path(s3dgraphy.__file__).parent / "JSON_config"
            / "s3Dgraphy_connections_datamodel.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for et, spec in (data.get("edge_types") or {}).items():
        ac = (spec or {}).get("allowed_connections") or {}
        out[et] = (frozenset(ac.get("source", [])),
                   frozenset(ac.get("target", [])))
    return out


#: pyArchInit renders row-paradata (and the special/virtual stratigraphic
#: kinds) as a plain ``StratigraphicUnit`` whose real EM identity lives in
#: ``attributes['unita_tipo']`` (the GraphML writer dispatches the BPMN shape
#: from it — see ``_create_paradata_node_for_unita_tipo``). So the
#: authoritative node type for datamodel matching is the ``unita_tipo``, NOT
#: the Python class. Map each code to its s3dgraphy class + bases so the
#: datamodel ``allowed_connections`` (which name those classes) match.
_UT_TO_CLASSNAMES = {
    "DOC":       frozenset({"DocumentNode", "ParadataNode", "Node"}),
    "Combinar":  frozenset({"CombinerNode", "ParadataNode", "Node"}),
    "Combiner":  frozenset({"CombinerNode", "ParadataNode", "Node"}),
    "Extractor": frozenset({"ExtractorNode", "ParadataNode", "Node"}),
    "property":  frozenset({"PropertyNode", "ParadataNode", "Node"}),
    "Property":  frozenset({"PropertyNode", "ParadataNode", "Node"}),
    "USD":  frozenset({"DocumentaryStratigraphicUnit", "StratigraphicNode", "Node"}),
    "USVs": frozenset({"StructuralVirtualStratigraphicUnit", "StratigraphicNode", "Node"}),
    "USVn": frozenset({"NonStructuralVirtualStratigraphicUnit", "StratigraphicNode", "Node"}),
    "SF":   frozenset({"SpecialFindUnit", "StratigraphicNode", "Node"}),
    "VSF":  frozenset({"VirtualSpecialFindUnit", "StratigraphicNode", "Node"}),
    "RSF":  frozenset({"ReusedSpecialFind", "StratigraphicNode", "Node"}),
    "US":   frozenset({"StratigraphicUnit", "StratigraphicNode", "Node"}),
    "USM":  frozenset({"StratigraphicUnit", "StratigraphicNode", "Node"}),
}


def _class_names(node) -> frozenset:
    """EM class-name set for datamodel matching.

    pyArchInit stores row-paradata as a ``StratigraphicUnit`` whose real EM
    type lives in ``attributes['unita_tipo']``. When that attribute names a
    known EM kind we use ITS class set (authoritative); otherwise we fall
    back to the Python MRO (so genuinely-typed nodes — DocumentNode,
    StratigraphicNode subclasses — still match a base-class rule)."""
    attrs = getattr(node, "attributes", None) or {}
    ut = str(attrs.get("unita_tipo") or "").strip()
    mapped = _UT_TO_CLASSNAMES.get(ut)
    if mapped:
        return mapped
    return frozenset(c.__name__ for c in type(node).__mro__)


def resolve_edge_type(source_names, target_names, allowed=None):
    """Most specific paradata edge type for a connection between a source whose
    MRO class-name set is ``source_names`` and a target ``target_names``.

    Returns ``(edge_type, swap)`` or ``None`` when only ``generic_connection``
    fits. ``swap=True`` means the rule matched *target → source*, so the caller
    must swap the endpoints before applying ``edge_type``.
    """
    if allowed is None:
        allowed = _allowed_connections()
    source_names = frozenset(source_names)
    target_names = frozenset(target_names)
    for et in _CANDIDATE_ORDER:
        rule = allowed.get(et)
        if not rule:
            continue
        src_ok, tgt_ok = rule
        if (source_names & src_ok) and (target_names & tgt_ok) \
                and not _solo_col_grafo(et, target_names):
            return et, False
        if (target_names & src_ok) and (source_names & tgt_ok) \
                and not _solo_col_grafo(et, source_names):
            return et, True
    return None


#: La coppia che per classe è ambigua: un estrattore verso una proprietà.
#:
#: Dalla connections 1.6.36 ``extracted_from`` accetta anche una
#: ``PropertyNode`` come bersaglio — la proprietà MASTER che un estrattore
#: legge come fonte — ma la stessa coppia di classi è anche la vecchia
#: linea di provenienza disegnata al contrario (la catena EM va proprietà →
#: estrattore). Il datamodel confronta per classe e non le distingue; il
#: grafo sì, con ``property_source.reads_as_source``. Senza grafo la
#: libreria non nomina l'arco (``connection_resolver.candidate_edge_types``),
#: e qui si fa lo stesso: resta la provenienza, che è quello che le schede
#: di pyArchInit scrivono. Risposta di E.D. su s3Dgraphy#25, 2026-10-10.
def _solo_col_grafo(edge_type: str, target_names) -> bool:
    return edge_type == "extracted_from" and "PropertyNode" in target_names


def resolve_edge_type_for_nodes(src, tgt, graph):
    """Come :func:`resolve_edge_type`, ma chiedendo alla libreria **col grafo**.

    «Il modo sicuro per qualunque consumatore è chiedere a
    ``candidate_edge_types`` col grafo, invece di scorrere
    ``allowed_connections`` in ordine» (E.D., s3Dgraphy#25). La libreria
    risponde con tutti i tipi che quella coppia di nodi ammette — e per
    l'estrattore verso una proprietà guarda il grafo per dire se è una
    lettura o una provenienza al contrario. Qui si sceglie il più specifico
    fra quelli che offre, nell'ordine del datamodel.

    Ricade su :func:`resolve_edge_type` se la libreria è più vecchia e non
    ha il risolutore, o se qualcosa va storto: meglio un tipo generico che
    una raffinazione che solleva.
    """
    try:
        from s3dgraphy.edges.connection_resolver import candidate_edge_types

        avanti = set(candidate_edge_types(src, tgt, graph=graph) or ())
        indietro = set(candidate_edge_types(tgt, src, graph=graph) or ())
    except Exception:                               # noqa: BLE001
        return resolve_edge_type(_class_names(src), _class_names(tgt))
    for et in _CANDIDATE_ORDER:
        if et in avanti:
            return et, False
        if et in indietro:
            return et, True
    return None


def refine_generic_connections(graph) -> int:
    """Retype ``generic_connection`` edges of ``graph`` into specific EM edge
    types based on endpoint node classes. Mutates edges in place and returns
    the number retyped. Best-effort: never raises."""
    try:
        allowed = _allowed_connections()
    except Exception:
        return 0
    by_id = {getattr(n, "node_id", None): n
             for n in getattr(graph, "nodes", [])}
    retyped = 0
    for edge in getattr(graph, "edges", []):
        if getattr(edge, "edge_type", None) != "generic_connection":
            continue
        src = by_id.get(getattr(edge, "edge_source", None))
        tgt = by_id.get(getattr(edge, "edge_target", None))
        if src is None or tgt is None:
            continue
        res = resolve_edge_type_for_nodes(src, tgt, graph)
        if not res:
            continue
        edge_type, swap = res
        if swap:
            edge.edge_source, edge.edge_target = (
                edge.edge_target, edge.edge_source)
        edge.edge_type = edge_type
        retyped += 1
    return retyped
