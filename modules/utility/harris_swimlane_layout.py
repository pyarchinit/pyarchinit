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


def compute_layout(data: S3DGraphData,
                   group_by: Optional[str] = None,
                   intergroup_gap: float = 0.5,
                   row_height: float = 1.0) -> SwimlaneLayout:
    """Compute swimlane positions for a parsed s3dgraphy graph.

    :param data: output of :func:`s3d_json_loader.load_s3d_json`
    :param group_by: attribute key to cluster nodes within each row
        (e.g. ``"area"`` or ``"attivita"``). None = flat row.
    :param intergroup_gap: extra horizontal logical units between
        groups when ``group_by`` is active (default 0.5 of a node slot).
    :param row_height: vertical extent of each row in logical units
        (default 1.0 — renderer scales).

    Convention: OLDEST epoch at y=0 (bottom), newest at the top, then
    a synthetic "unassigned" row on top of that.
    """
    nx = data.networkx

    # 1) Bucket stratigraphic nodes per epoch_id.
    nodes_per_epoch: Dict[Optional[str], List[str]] = {}
    for node_id, attrs in nx.nodes(data=True):
        if attrs.get("bucket") != "stratigraphic":
            continue
        epoch_id = data.node_to_epoch.get(node_id)
        nodes_per_epoch.setdefault(epoch_id, []).append(node_id)

    # 2) Row order: epochs chronological (oldest first => row 0 at bottom),
    # then synthetic "unassigned" on top.
    ordered_epoch_ids: List[Optional[str]] = [e.epoch_id for e in data.epochs]
    has_unassigned = None in nodes_per_epoch and bool(nodes_per_epoch.get(None))

    rows: List[RowInfo] = []
    layout = SwimlaneLayout()

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
