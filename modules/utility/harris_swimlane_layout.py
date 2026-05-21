"""Compute swimlane positions for a Harris matrix from s3dgraphy data.

The swimlane layout places nodes on a 2-D plane where:

- **Y axis** = epoch (period) row. Convention: OLDEST at the BOTTOM
  (Harris matrix convention — earliest stratigraphic events are
  beneath later ones). Unassigned nodes (no ``has_first_epoch`` edge)
  go to a synthetic row ABOVE the newest epoch.
- **X axis** = position within the row. Nodes are CENTERED within the
  maximum row width so rows with fewer nodes appear visually balanced.
  Optional :func:`compute_layout` ``group_by`` parameter clusters
  consecutive nodes that share an attribute value (``"area"``,
  ``"attivita"``, or any key in ``node.data``) with a small inter-group
  gap.

Output: :class:`SwimlaneLayout` containing:

- ``positions``: ``{node_id: (x, y)}`` floats in "logical units" (one
  unit per row vertically, one unit per node-slot horizontally — the
  renderer scales these to pixels)
- ``rows``: ordered ``RowInfo`` list with ``y_center``, ``y_top``,
  ``y_bottom``, ``label``, ``epoch_color``, ``node_ids``
- ``max_row_width``: int — number of horizontal slots needed for the
  widest row (used by the renderer to size the figure)

Non-stratigraphic nodes (epochs themselves, properties, documents,
extractors, combiners, groups, paradata) are EXCLUDED from the
swimlane positions — they're either drawn as row labels (epochs) or
overlay annotations (the renderer decides). Only nodes whose
``bucket == "stratigraphic"`` enter the position map.
"""
from __future__ import annotations

import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .s3d_json_loader import S3DGraphData


_NATURAL_SPLIT = re.compile(r'(\d+)')


def _natural_sort_key(s: str) -> List:
    """Natural sort: 'US 60' < 'US 100' (numeric chunks compared as ints)."""
    return [int(tok) if tok.isdigit() else tok.lower()
            for tok in _NATURAL_SPLIT.split(s or "")]


@dataclass
class RowInfo:
    """One swimlane row (one epoch)."""
    epoch_id: Optional[str]   # None for the synthetic "unassigned" row
    label: str                # epoch name or "Senza periodo"
    epoch_color: Optional[str]
    y_center: float           # logical y of row centerline
    y_top: float
    y_bottom: float
    node_ids: List[str] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class SwimlaneLayout:
    positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    rows: List[RowInfo] = field(default_factory=list)
    max_row_width: int = 0  # logical slot count for the widest row


def _group_within_row(node_ids: List[str], data: S3DGraphData,
                      group_by: Optional[str]) -> List[List[str]]:
    """Partition a row's nodes into ordered groups by ``group_by`` attr.

    Returns a list of groups (lists of node_ids). Group order is by
    sorted key value; nodes inside a group are sorted by their ``name``
    (or ``node_id`` if ``name`` is empty) for deterministic output.

    When ``group_by`` is None, returns a single group with all nodes
    sorted by name.
    """
    nx = data.networkx

    def _sort_key(nid: str):
        # Natural sort by node name (or id fallback) — "US 60" < "US 100".
        return _natural_sort_key(nx.nodes[nid].get("name") or nid)

    if not group_by:
        return [sorted(node_ids, key=_sort_key)]

    buckets: Dict[str, List[str]] = {}
    no_key: List[str] = []
    for nid in node_ids:
        attrs = nx.nodes[nid]
        raw_data = attrs.get("data", {})
        # group_by may be a top-level attr ("kind", "name") or live
        # inside the nested "data" sub-dict — check both.
        val = attrs.get(group_by)
        if val is None and isinstance(raw_data, dict):
            val = raw_data.get(group_by)
        if val is None or val == "":
            no_key.append(nid)
        else:
            buckets.setdefault(str(val), []).append(nid)

    # Sort group keys for stable ordering. The "no-key" bucket goes last.
    ordered_keys = sorted(buckets.keys())
    groups = [sorted(buckets[k], key=_sort_key) for k in ordered_keys]
    if no_key:
        groups.append(sorted(no_key, key=_sort_key))
    return groups


def _topological_sublayers(node_ids: List[str], nx_graph) -> List[List[str]]:
    """Partition ``node_ids`` into ordered topological layers.

    Uses ``networkx.condensation`` to collapse strongly-connected
    components (cycles) into super-nodes, then runs topological
    layering on the resulting DAG. Each output layer contains the
    union of all original nodes in the SCCs at that layer level.

    Cycles in pyarchinit-derived graphs come from reciprocal edge
    encodings (``A → B`` AND ``B → A`` representing the same
    ``is_after`` / ``is_before`` pair). SCC condensation keeps the
    semantic layering correct: all nodes inside one mutual cycle land
    in the same layer (they're "at the same level"), which is the
    right visual.

    Layer 0 = roots, deepest layer = leaves. Empty input → empty
    output. Within each layer, nodes are sorted by natural key
    ("US 60" < "US 100").
    """
    if not node_ids:
        return []

    import networkx as _nx  # local import to keep module-load cheap

    node_set = set(node_ids)
    # Build the induced subgraph as a separate DiGraph.
    sub = _nx.DiGraph()
    sub.add_nodes_from(node_ids)
    for src, tgt in nx_graph.edges:
        if src in node_set and tgt in node_set and src != tgt:
            sub.add_edge(src, tgt)

    if sub.number_of_edges() == 0:
        # All singletons → one layer with all nodes.
        return [sorted(node_ids, key=lambda nid: _natural_sort_key(
            nx_graph.nodes[nid].get("name") or nid))]

    # Condense SCCs → DAG of components.
    condensation = _nx.condensation(sub)
    # Each DAG node has attr 'members' = the set of original node ids
    # that form the SCC. (Standard networkx behaviour.)
    members = _nx.get_node_attributes(condensation, "members")

    out: List[List[str]] = []

    if condensation.number_of_edges() == 0:
        # All SCCs are disconnected from each other — there's no
        # topological ordering AMONG them. Give each SCC its own
        # visual sub-row so the user sees the structure of each
        # independent cluster. Order: largest SCC at the BOTTOM
        # (highest visual mass goes to the base of the period band).
        scc_sizes = [(scc_idx, len(members.get(scc_idx, set())))
                     for scc_idx in condensation.nodes]
        scc_sizes.sort(key=lambda kv: kv[1])  # ascending → smaller TOP
        for scc_idx, _size in scc_sizes:
            scc_nodes = sorted(
                members.get(scc_idx, set()),
                key=lambda nid: _natural_sort_key(
                    nx_graph.nodes[nid].get("name") or nid),
            )
            if scc_nodes:
                out.append(scc_nodes)
        return out

    # Normal case: condensation DAG has edges → topological layering.
    layers_of_sccs = list(_nx.topological_generations(condensation))
    for gen in layers_of_sccs:
        layer_nodes: List[str] = []
        for scc_idx in gen:
            scc_nodes = members.get(scc_idx, set())
            layer_nodes.extend(scc_nodes)
        if layer_nodes:
            out.append(sorted(layer_nodes,
                              key=lambda nid: _natural_sort_key(
                                  nx_graph.nodes[nid].get("name") or nid)))
    return out


def _kind_fallback_rows(data: S3DGraphData) -> List[Tuple[str, List[str]]]:
    """When the JSON has no epochs, fall back to one row per unique
    ``unita_tipo`` (or ``kind`` if unita_tipo is empty), so the
    renderer still produces a meaningful visualization instead of
    cramming 250+ nodes into a single "Senza periodo" row.

    Returns ordered ``[(label, [node_ids])]`` with US-family kinds
    appearing first (most-common stratigraphic) then USM/USV/etc.
    """
    nx = data.networkx
    buckets: Dict[str, List[str]] = {}
    for nid, attrs in nx.nodes(data=True):
        if attrs.get("bucket") != "stratigraphic":
            continue
        # Prefer unita_tipo (from flat exports) — falls back to kind.
        ut = (attrs.get("data", {}) or {}).get("unita_tipo")
        label = ut.strip() if isinstance(ut, str) and ut.strip() else attrs.get("kind", "?")
        buckets.setdefault(label, []).append(nid)
    # Stable order: US first, then alphabetical for the rest.
    ordered_keys = sorted(buckets.keys(), key=lambda k: (k != "US", k))
    return [(k, buckets[k]) for k in ordered_keys]


def compute_layout(data: S3DGraphData,
                   group_by: Optional[str] = None,
                   intergroup_gap: float = 0.5,
                   row_height: float = 1.0,
                   max_nodes_per_row: int = 30) -> SwimlaneLayout:
    """Compute swimlane positions for a parsed s3dgraphy graph.

    :param data: output of :func:`s3d_json_loader.load_s3d_json`
    :param group_by: attribute key to cluster nodes within each row
        (e.g. ``"area"`` or ``"attivita"``). None = flat row.
    :param intergroup_gap: extra horizontal logical units between
        groups when ``group_by`` is active (default 0.5 of a node slot).
    :param row_height: vertical extent of each row in logical units
        (default 1.0 — renderer scales).
    :param max_nodes_per_row: when a row would exceed this width, it
        is split into multiple visual sub-rows (same epoch label,
        stacked vertically). Default 30 keeps figures readable.
        Set to a very large number to disable wrapping.

    Convention: OLDEST epoch at y=0 (bottom), newest at the top, then
    a synthetic "unassigned" row on top of that.

    **Fallback when no epochs are assigned**: if ``data.epochs`` is
    empty (typical for early/incomplete pyArchInit DBs that never set
    periodo on US records), the layout creates synthetic rows from
    the ``unita_tipo`` attribute (one row per US / USM / USVs ...).
    Renderer behaviour is otherwise identical.
    """
    nx = data.networkx

    rows: List[RowInfo] = []
    layout = SwimlaneLayout()

    # --- Decide the row source: real epochs OR unita_tipo fallback ---
    use_kind_fallback = not data.epochs

    if use_kind_fallback:
        # Build synthetic rows from unita_tipo.
        synthetic = _kind_fallback_rows(data)
        for row_index, (label, node_ids) in enumerate(synthetic):
            y_bottom = row_index * row_height
            y_top = y_bottom + row_height
            rows.append(RowInfo(
                epoch_id=None,
                label=label,
                epoch_color=None,
                y_center=(y_top + y_bottom) / 2.0,
                y_top=y_top,
                y_bottom=y_bottom,
                node_ids=node_ids,
            ))
    else:
        # 1) Bucket stratigraphic nodes per epoch_id.
        nodes_per_epoch: Dict[Optional[str], List[str]] = {}
        for node_id, attrs in nx.nodes(data=True):
            if attrs.get("bucket") != "stratigraphic":
                continue
            epoch_id = data.node_to_epoch.get(node_id)
            nodes_per_epoch.setdefault(epoch_id, []).append(node_id)

        ordered_epoch_ids: List[Optional[str]] = [e.epoch_id for e in data.epochs]
        has_unassigned = None in nodes_per_epoch and bool(nodes_per_epoch.get(None))

        # Build RowInfo for each epoch, oldest-first (y=0 bottom).
        for row_index, epoch_id in enumerate(ordered_epoch_ids):
            epoch = data.epochs[row_index]
            node_ids_here = nodes_per_epoch.get(epoch_id, [])
            y_bottom = row_index * row_height
            y_top = y_bottom + row_height
            rows.append(RowInfo(
                epoch_id=epoch_id,
                label=epoch.name or epoch_id,
                epoch_color=epoch.color,
                y_center=(y_top + y_bottom) / 2.0,
                y_top=y_top,
                y_bottom=y_bottom,
                node_ids=node_ids_here,
                start_time=epoch.start_time,
                end_time=epoch.end_time,
            ))

        # Synthetic "Senza periodo" row on top, if any unassigned stratigraphic.
        if has_unassigned:
            row_index = len(rows)
            y_bottom = row_index * row_height
            y_top = y_bottom + row_height
            rows.append(RowInfo(
                epoch_id=None,
                label="Senza periodo",
                epoch_color=None,
                y_center=(y_top + y_bottom) / 2.0,
                y_top=y_top,
                y_bottom=y_bottom,
                node_ids=nodes_per_epoch[None],
            ))

    # --- Topological sub-layering within each period row ---
    # Each row now becomes a STACK of sub-layers based on the
    # subgraph topology of its nodes (parents on top, children below).
    # This gives a real Harris-matrix vertical hierarchy WITHIN each
    # period band instead of all nodes crammed in a single horizontal
    # line. Wrapping (max_nodes_per_row) still applies PER SUB-LAYER
    # so we don't get one absurdly wide layer at the bottom.
    expanded: List[RowInfo] = []
    for row in rows:
        sublayers = _topological_sublayers(row.node_ids, nx)
        if not sublayers:
            continue
        # For each sublayer, wrap if too wide.
        for layer_idx, layer_nodes in enumerate(sublayers):
            if len(layer_nodes) <= max_nodes_per_row:
                chunks = [layer_nodes]
            else:
                chunks = [layer_nodes[i:i + max_nodes_per_row]
                          for i in range(0, len(layer_nodes), max_nodes_per_row)]
            for chunk_idx, chunk in enumerate(chunks):
                # Build a per-sublayer label suffix only when needed.
                if len(sublayers) > 1 or len(chunks) > 1:
                    sub_parts = []
                    if len(sublayers) > 1:
                        sub_parts.append(f"L{layer_idx + 1}/{len(sublayers)}")
                    if len(chunks) > 1:
                        sub_parts.append(f"{chunk_idx + 1}/{len(chunks)}")
                    suffix = f"  ({', '.join(sub_parts)})"
                else:
                    suffix = ""
                expanded.append(RowInfo(
                    epoch_id=row.epoch_id,
                    label=row.label + suffix,
                    epoch_color=row.epoch_color,
                    y_center=0,  # recomputed below
                    y_top=0,
                    y_bottom=0,
                    node_ids=chunk,
                    start_time=row.start_time,
                    end_time=row.end_time,
                ))
    # Re-assign y coordinates to the expanded list. Convention preserved:
    # OLDEST period at the bottom (y=0); within a period, the SHALLOWEST
    # topological layer (roots / parents) is at the TOP, deepest layer
    # (leaves / children) at the BOTTOM. Since we appended period-by-period
    # and within each period appended layer-by-layer (layer 0 = roots first),
    # the reverse iteration during y assignment puts layer 0 above its
    # children — matching Harris-matrix convention.
    for new_idx, row in enumerate(reversed(expanded)):
        # new_idx 0 = top of the list of "expanded" (because reversed).
        # We want top of figure = end of `expanded` list when grouped
        # so that older period (y=0) lands at bottom.
        pass
    # Simpler explicit reassignment:
    n_total = len(expanded)
    for new_idx, row in enumerate(expanded):
        # The natural append order already has: oldest-period-first,
        # within-period roots-first. We want roots LAST in the period
        # band so they appear ABOVE children. So flip each period
        # internally: nodes appended late within a period go to the
        # bottom of that period's slice — we want them at the TOP.
        # The simplest fix: leave append order (parents added first
        # so parents at lower y => below children) and INVERT logic
        # at render time? No — let's reverse per period in place.
        pass
    # Reorder: for each period (same epoch_id), reverse the order of
    # its sublayers so roots are LAST in the list (=> highest y =>
    # ABOVE in matplotlib coords with normal Y axis).
    by_epoch: Dict[Optional[str], List[RowInfo]] = defaultdict(list)
    order: List[Optional[str]] = []
    for row in expanded:
        if row.epoch_id not in by_epoch:
            order.append(row.epoch_id)
        by_epoch[row.epoch_id].append(row)
    reordered: List[RowInfo] = []
    for ep_id in order:
        # Reverse: deepest layer first (lower y, appears at bottom of
        # period band), roots last (higher y, appears at top of band).
        reordered.extend(reversed(by_epoch[ep_id]))

    # --- Paradata bands (Extended Matrix convention: top of figure) ---
    # Each paradata kind (Extractor / property / document / combiner)
    # gets ITS OWN row, placed ABOVE all stratigraphic period rows.
    # This mirrors how yEd renders EM diagrams: paradata sits in a
    # documentation strip above the strat units, with arrows
    # crossing down to whichever US they annotate.
    paradata_by_kind: Dict[str, List[str]] = defaultdict(list)
    for node_id, attrs in nx.nodes(data=True):
        if attrs.get("bucket") == "paradata":
            paradata_by_kind[attrs.get("kind", "paradata")].append(node_id)
    paradata_rows: List[RowInfo] = []
    if paradata_by_kind:
        # Stable kind order: combiner / extractor / document / property
        # (most-aggregated first). Unknown kinds go alphabetical last.
        canonical_order = ["combiner", "Combinar", "extractor", "Extractor",
                           "document", "Document", "DOC",
                           "property", "Property"]
        kind_index = {k: i for i, k in enumerate(canonical_order)}
        kinds_sorted = sorted(
            paradata_by_kind.keys(),
            key=lambda k: (kind_index.get(k, 999), k),
        )
        for kind in kinds_sorted:
            ids = paradata_by_kind[kind]
            # Wrap paradata if too wide too.
            chunks = ([ids] if len(ids) <= max_nodes_per_row
                      else [ids[i:i + max_nodes_per_row]
                            for i in range(0, len(ids), max_nodes_per_row)])
            for chunk_idx, chunk in enumerate(chunks):
                # Pretty label per kind. Translate the pyArchInit
                # flat-export forms to human-friendly labels.
                pretty = {
                    "combiner": "Combiners", "Combinar": "Combiners",
                    "extractor": "Extractors", "Extractor": "Extractors",
                    "document": "Documenti", "Document": "Documenti", "DOC": "Documenti",
                    "property": "Properties", "Property": "Properties",
                }.get(kind, kind)
                suffix = f" ({chunk_idx + 1}/{len(chunks)})" if len(chunks) > 1 else ""
                paradata_rows.append(RowInfo(
                    epoch_id=None,
                    label=f"▸ {pretty}{suffix}",
                    epoch_color=None,
                    y_center=0, y_top=0, y_bottom=0,
                    node_ids=sorted(chunk, key=lambda nid: _natural_sort_key(
                        nx.nodes[nid].get("name") or nid)),
                ))

    # Append paradata AFTER strat rows so they sit at the top in
    # matplotlib coords (highest y). Order: reverse so the "highest
    # priority" paradata kind (combiners) ends up at the very top.
    final_rows = reordered + list(reversed(paradata_rows))

    for new_idx, row in enumerate(final_rows):
        row.y_bottom = new_idx * row_height
        row.y_top = row.y_bottom + row_height
        row.y_center = (row.y_top + row.y_bottom) / 2.0
    rows = final_rows

    # 3) Compute max row width (in logical slots, with grouping accounted for).
    grouped_rows: List[List[List[str]]] = []
    max_width = 0
    for row in rows:
        groups = _group_within_row(row.node_ids, data, group_by)
        grouped_rows.append(groups)
        total_nodes = sum(len(g) for g in groups)
        if group_by and len(groups) > 1:
            total_nodes += int((len(groups) - 1) * intergroup_gap)
        max_width = max(max_width, total_nodes)
    layout.max_row_width = max_width

    # 4) Place each node at (x, y_center) — CENTER alignment within row.
    for row, groups in zip(rows, grouped_rows):
        if not groups or not any(groups):
            continue
        total_slots = sum(len(g) for g in groups)
        if group_by and len(groups) > 1:
            total_slots += (len(groups) - 1) * intergroup_gap
        # Left edge so the row is centered in [0, max_width].
        x_start = (max_width - total_slots) / 2.0
        x = x_start
        for gi, group in enumerate(groups):
            for nid in group:
                layout.positions[nid] = (x + 0.5, row.y_center)  # +0.5 = node center within its slot
                x += 1.0
            # Inter-group gap (except after last group)
            if group_by and gi < len(groups) - 1:
                x += intergroup_gap

    layout.rows = rows
    return layout
