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

    # --- Row wrapping: split any row that would exceed max_nodes_per_row ---
    # We rebuild the rows list, inserting multiple visual sub-rows when
    # needed. Sub-rows share the SAME epoch metadata (label + color +
    # start/end_time) so the renderer's period band drawing still works.
    expanded: List[RowInfo] = []
    for row in rows:
        if len(row.node_ids) <= max_nodes_per_row:
            expanded.append(row)
            continue
        # Need wrapping: split node_ids into chunks of max_nodes_per_row.
        chunks = [row.node_ids[i:i + max_nodes_per_row]
                  for i in range(0, len(row.node_ids), max_nodes_per_row)]
        for chunk_idx, chunk in enumerate(chunks):
            suffix = f"  ({chunk_idx + 1}/{len(chunks)})"
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
    # Re-assign y coordinates to the expanded list (bottom-up).
    for new_idx, row in enumerate(expanded):
        row.y_bottom = new_idx * row_height
        row.y_top = row.y_bottom + row_height
        row.y_center = (row.y_top + row.y_bottom) / 2.0
    rows = expanded

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
