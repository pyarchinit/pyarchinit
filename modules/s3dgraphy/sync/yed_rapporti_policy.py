"""yE-D Group A: folder-edge policy module.

When a yEd-raw graphml is imported, some authoring edges connect
group folders (yfiles.foldertype="group") rather than leaf nodes.
The us_table.rapporti column only stores leaf-to-leaf relations, so
folder-touching edges must be reduced to leaf-to-leaf pairs (or
dropped) via one of four policies:

* SKIP           — drop folder-touching edges entirely.
* FAN_OUT        — expand A->B (folders) to N x M leaf pairs.
* REPRESENTATIVE — use the first member of each folder as proxy.
* SYNTHETIC      — create one virtual us_table row (unita_tipo='VA')
                   per folder and rewire folder edges through them.

Self-loop folder edges (source == target) are filtered out of ALL
policies before policy application — they arise from nested folder
member edges authored in yEd and would otherwise produce noise.

Public API:

    FolderEdgePolicy (StrEnum: skip / fan_out / representative / synthetic)
    FolderEdge      (dataclass: src, tgt, src_is_folder, tgt_is_folder, edge_type)
    FolderEdgeReport (dataclass: total, leaf_to_leaf, folder_touching, folder_self_loops)
    ExpandedRapporti (dataclass: policy, rapporti, synthetic_us_rows)
    analyze_edges(graphml_path, classified, folders) -> FolderEdgeReport
    apply_policy(report, policy, *, all_folders, classified) -> ExpandedRapporti

Implementation notes:
* `analyze_edges` parses <edge> elements via lxml (falling back to
  stdlib `xml.etree.ElementTree`) and classifies each endpoint as a
  folder or a leaf based on the dataclass lookups passed in.
* `apply_policy` for SYNTHETIC generates `node_uuid` values via
  `uuid.uuid4().hex` here — the real UUID v7 generation happens at
  write-time in Group B (`yed_import_pipeline.py`), which will
  re-mint these node_uuids using the `uuid7` helper. Group A's
  output is treated as a planning dataclass.

Added in yE-D (yed-import-pipeline-5.8.0-alpha).
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .yed_classifier import ClassifiedNode
from .yed_group_walker import FolderCandidate

logger = logging.getLogger(__name__)


class FolderEdgePolicy(str, Enum):
    """Strategy for folder-touching edges during yEd-raw import."""
    SKIP           = "skip"
    FAN_OUT        = "fan_out"
    REPRESENTATIVE = "representative"
    SYNTHETIC      = "synthetic"


@dataclass(frozen=True)
class FolderEdge:
    """One graphml <edge> at least one endpoint of which is a folder."""
    source_id: str
    target_id: str
    source_is_folder: bool
    target_is_folder: bool
    edge_type: str | None  # e.g. "covers" / "cuts" / None for generic


@dataclass
class FolderEdgeReport:
    """Output of analyze_edges -- partition of all <edge> elements
    by their endpoint kinds.

    `leaf_to_leaf` always passes through `apply_policy` unchanged.
    `folder_touching` is the queue policies act on.
    `folder_self_loops` is filtered out BEFORE policy application
    (a folder pointing to itself, common with nested folder member
    edges authored in yEd, would yield noise).
    """
    total_edges: int
    leaf_to_leaf: list[tuple[str, str, str | None]]
    folder_touching: list[FolderEdge]
    folder_self_loops: list[FolderEdge] = field(default_factory=list)


@dataclass
class ExpandedRapporti:
    """Result of apply_policy.

    `rapporti` is the final list of leaf-to-leaf (source, target,
    edge_type) tuples ready to write into us_table.rapporti.

    `synthetic_us_rows` is non-empty ONLY when policy=SYNTHETIC and
    contains dicts ready to INSERT into us_table. Each row has at
    minimum `node_uuid`, `unita_tipo='VA'`, `us=<folder_label>`,
    and `_yed_folder_id=<source folder yed_id>` so Group B can
    rewire edges.
    """
    policy: FolderEdgePolicy
    rapporti: list[tuple[str, str, str | None]]
    synthetic_us_rows: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# analyze_edges
# ---------------------------------------------------------------------------

def analyze_edges(
    graphml_path: Path | str,
    classified: list[ClassifiedNode],
    folders: list[FolderCandidate],
) -> FolderEdgeReport:
    """Parse <edge> elements; partition by endpoint kinds.

    Args:
        graphml_path: filesystem path to .graphml file.
        classified: yE-B classifier output for leaf nodes.
        folders: yE-C folder walker output for group folders.

    Returns:
        FolderEdgeReport with total_edges, leaf_to_leaf list,
        folder_touching list, and folder_self_loops list (filtered
        out from folder_touching).

    Empty/malformed/missing file -> empty report.
    """
    path = Path(graphml_path)
    if not path.exists():
        return FolderEdgeReport(
            total_edges=0, leaf_to_leaf=[], folder_touching=[],
        )

    folder_ids: set[str] = {f.yed_id for f in folders}
    leaf_ids: set[str] = {c.yed_id for c in classified}

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"

    leaf_to_leaf: list[tuple[str, str, str | None]] = []
    folder_touching: list[FolderEdge] = []
    folder_self_loops: list[FolderEdge] = []
    total = 0

    try:
        tree = _ET.parse(str(path))
    except Exception:
        return FolderEdgeReport(
            total_edges=0, leaf_to_leaf=[], folder_touching=[],
        )

    root = tree.getroot()
    for edge in root.iter(f"{GRAPHML_NS}edge"):
        src = edge.get("source") or ""
        tgt = edge.get("target") or ""
        if not src or not tgt:
            continue
        total += 1

        src_is_folder = src in folder_ids
        tgt_is_folder = tgt in folder_ids
        src_is_leaf = src in leaf_ids
        tgt_is_leaf = tgt in leaf_ids

        # edge_type: read <y:LineStyle type="..."/> or <y:EdgeLabel> if any.
        # For MVP we use None (graphml fixtures don't set explicit types
        # at the schema level). Future yE-E can read these.
        edge_type: str | None = None

        if src_is_leaf and tgt_is_leaf:
            leaf_to_leaf.append((src, tgt, edge_type))
            continue

        if src_is_folder or tgt_is_folder:
            fe = FolderEdge(
                source_id=src,
                target_id=tgt,
                source_is_folder=src_is_folder,
                target_is_folder=tgt_is_folder,
                edge_type=edge_type,
            )
            # Filter folder self-loops here (BEFORE policy application).
            if src == tgt and src_is_folder and tgt_is_folder:
                folder_self_loops.append(fe)
            else:
                folder_touching.append(fe)
            continue

        # Endpoint not found in either set -- treat as leaf-to-leaf
        # for safety (caller may have filtered classified to a subset).
        leaf_to_leaf.append((src, tgt, edge_type))

    return FolderEdgeReport(
        total_edges=total,
        leaf_to_leaf=leaf_to_leaf,
        folder_touching=folder_touching,
        folder_self_loops=folder_self_loops,
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _folder_members(
    folder: FolderCandidate,
    all_folders: list[FolderCandidate],
) -> list[str]:
    """Recursive flatten: direct leaf members + nested folders' members.

    Nested folders not present in `all_folders` are skipped (defensive).
    Cycles cannot occur because yed_group_walker already filters them
    via CycleDetectedError on parse.
    """
    by_id: dict[str, FolderCandidate] = {f.yed_id: f for f in all_folders}

    out: list[str] = []
    seen: set[str] = set()

    def _walk(f: FolderCandidate) -> None:
        if f.yed_id in seen:
            return
        seen.add(f.yed_id)
        out.extend(f.member_yed_ids)
        for nested_id in f.nested_folder_ids:
            nested = by_id.get(nested_id)
            if nested is None:
                continue
            _walk(nested)

    _walk(folder)
    return out


def _self_loop(edge: FolderEdge) -> bool:
    """True if the edge is a folder self-loop (source == target)."""
    return (
        edge.source_id == edge.target_id
        and edge.source_is_folder
        and edge.target_is_folder
    )


# ---------------------------------------------------------------------------
# apply_policy
# ---------------------------------------------------------------------------

def apply_policy(
    report: FolderEdgeReport,
    policy: FolderEdgePolicy,
    *,
    all_folders: list[FolderCandidate],
    classified: list[ClassifiedNode],
) -> ExpandedRapporti:
    """Apply the chosen policy to report.folder_touching.

    Leaf-to-leaf edges always pass through unchanged. The four
    policies differ only in how folder-touching edges are reduced
    to leaf-to-leaf pairs (or dropped).

    Args:
        report: output of analyze_edges.
        policy: one of FolderEdgePolicy values.
        all_folders: yE-C folder walker output (for member flatten).
        classified: yE-B classifier output (currently unused, but
            reserved for REPRESENTATIVE / SYNTHETIC labelling).

    Returns:
        ExpandedRapporti with rapporti list and (for SYNTHETIC)
        synthetic_us_rows.
    """
    # Defensive: drop any self-loops that slipped through.
    folder_edges = [e for e in report.folder_touching if not _self_loop(e)]

    by_id: dict[str, FolderCandidate] = {f.yed_id: f for f in all_folders}
    leaf_label_by_id: dict[str, str] = {c.yed_id: c.label for c in classified}

    rapporti: list[tuple[str, str, str | None]] = list(report.leaf_to_leaf)
    synthetic_rows: list[dict] = []

    if policy == FolderEdgePolicy.SKIP:
        # Drop folder-touching edges entirely.
        return ExpandedRapporti(
            policy=policy,
            rapporti=rapporti,
            synthetic_us_rows=[],
        )

    if policy == FolderEdgePolicy.FAN_OUT:
        for fe in folder_edges:
            src_members = _resolve_endpoint_members(
                fe.source_id, fe.source_is_folder, by_id, all_folders,
            )
            tgt_members = _resolve_endpoint_members(
                fe.target_id, fe.target_is_folder, by_id, all_folders,
            )
            if not src_members or not tgt_members:
                logger.warning(
                    "FAN_OUT: skipping edge %s->%s (empty member list "
                    "for folder endpoint)", fe.source_id, fe.target_id,
                )
                continue
            for s in src_members:
                for t in tgt_members:
                    if s == t:
                        # Self-loops at leaf level can occur for
                        # folder->itself member edges; skip.
                        continue
                    rapporti.append((s, t, fe.edge_type))
        return ExpandedRapporti(
            policy=policy,
            rapporti=rapporti,
            synthetic_us_rows=[],
        )

    if policy == FolderEdgePolicy.REPRESENTATIVE:
        for fe in folder_edges:
            src_one = _representative(
                fe.source_id, fe.source_is_folder, by_id, all_folders,
            )
            tgt_one = _representative(
                fe.target_id, fe.target_is_folder, by_id, all_folders,
            )
            if src_one is None or tgt_one is None:
                logger.warning(
                    "REPRESENTATIVE: skipping edge %s->%s (empty member "
                    "list for folder endpoint)",
                    fe.source_id, fe.target_id,
                )
                continue
            if src_one == tgt_one:
                continue
            rapporti.append((src_one, tgt_one, fe.edge_type))
        return ExpandedRapporti(
            policy=policy,
            rapporti=rapporti,
            synthetic_us_rows=[],
        )

    if policy == FolderEdgePolicy.SYNTHETIC:
        # Build a synthetic us_table row per UNIQUE folder appearing in
        # folder_edges. Then rewire endpoints through the synthetic
        # anchor node_uuid.
        unique_folders: list[str] = []
        seen: set[str] = set()
        for fe in folder_edges:
            for endpoint_id, is_folder in (
                (fe.source_id, fe.source_is_folder),
                (fe.target_id, fe.target_is_folder),
            ):
                if not is_folder:
                    continue
                if endpoint_id in seen:
                    continue
                seen.add(endpoint_id)
                unique_folders.append(endpoint_id)

        # Map yed folder_id -> synthetic node_uuid (used as leaf id in rapporti).
        folder_to_synthetic: dict[str, str] = {}
        for folder_id in unique_folders:
            folder = by_id.get(folder_id)
            label = folder.full_label if folder is not None else folder_id
            node_uuid_hex = uuid.uuid4().hex
            folder_to_synthetic[folder_id] = node_uuid_hex
            synthetic_rows.append({
                "node_uuid": node_uuid_hex,
                "us": label,
                "unita_tipo": "VA",
                "_yed_folder_id": folder_id,
            })

        for fe in folder_edges:
            src = (
                folder_to_synthetic[fe.source_id]
                if fe.source_is_folder
                else fe.source_id
            )
            tgt = (
                folder_to_synthetic[fe.target_id]
                if fe.target_is_folder
                else fe.target_id
            )
            if src == tgt:
                continue
            rapporti.append((src, tgt, fe.edge_type))

        return ExpandedRapporti(
            policy=policy,
            rapporti=rapporti,
            synthetic_us_rows=synthetic_rows,
        )

    # Unknown policy -- defensive: fall back to SKIP semantics.
    logger.warning(
        "apply_policy: unknown policy %r -- falling back to SKIP", policy,
    )
    return ExpandedRapporti(
        policy=FolderEdgePolicy.SKIP,
        rapporti=list(report.leaf_to_leaf),
        synthetic_us_rows=[],
    )


# Suppress lint hint about classified parameter -- reserved for future
# REPRESENTATIVE/SYNTHETIC use cases (e.g., label-aware proxy selection).
# leaf_label_by_id is currently consumed only when synthetic rows
# missing folder candidate need a fallback label.
_ = "classified reserved for yE-E hooks"


def _resolve_endpoint_members(
    endpoint_id: str,
    is_folder: bool,
    by_id: dict[str, FolderCandidate],
    all_folders: list[FolderCandidate],
) -> list[str]:
    """For a folder endpoint, return its recursive leaf members.
    For a leaf endpoint, return [endpoint_id]."""
    if not is_folder:
        return [endpoint_id]
    folder = by_id.get(endpoint_id)
    if folder is None:
        return []
    return _folder_members(folder, all_folders)


def _representative(
    endpoint_id: str,
    is_folder: bool,
    by_id: dict[str, FolderCandidate],
    all_folders: list[FolderCandidate],
) -> str | None:
    """First member of a folder endpoint (document order); leaf -> itself."""
    members = _resolve_endpoint_members(
        endpoint_id, is_folder, by_id, all_folders,
    )
    return members[0] if members else None
