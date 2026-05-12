"""yEd group folder walker (yE-C Parsers, 5.7.7-alpha).

Descends `yfiles.foldertype="group"` hierarchy and produces
FolderCandidate records with prefix-derived auto-classification
(VA->attivita, AR->area, ST->struttura, SE->settore, AM->ambient,
SG->saggio, QP->quad_par).

Excludes the top-level swimlane (TableNode container) — yE-C
yed_table_parser handles that as periods.

Auto-value extraction: regex `^([A-Z]+\\d+)` captures the
"VA01" prefix from "VA01-foundation example"; the trailing
description is preserved in extra_attrs["description"].

Cycle detection via visited set; raises CycleDetectedError
(imported from graph_ingestor.py) on malformed input.

Returns [] on parse error / missing file / no folders.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .graph_ingestor import CycleDetectedError


# Order-sensitive: first match wins. Patterns match prefix only;
# auto_value strips trailing digits + description.
DEFAULT_FOLDER_PREFIX_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^VA"), "attivita"),
    (re.compile(r"^AR"), "area"),
    (re.compile(r"^ST"), "struttura"),
    (re.compile(r"^SE"), "settore"),
    (re.compile(r"^AM"), "ambient"),
    (re.compile(r"^SG"), "saggio"),
    (re.compile(r"^QP"), "quad_par"),
]


_VALUE_PREFIX_RE = re.compile(r"^([A-Z]+\d+)")


@dataclass
class FolderCandidate:
    """One yEd group folder with prefix-derived auto-classification."""
    yed_id: str
    full_label: str
    auto_dimension: str | None
    user_dimension: str | None
    auto_value: str
    user_value: str
    member_yed_ids: list[str] = field(default_factory=list)
    nested_folder_ids: list[str] = field(default_factory=list)
    parent_folder_id: str | None = None
    extra_attrs: dict = field(default_factory=dict)


def _classify_label(full_label: str) -> tuple[str | None, str, dict]:
    """Return (auto_dimension, auto_value, extra_attrs) for a folder label."""
    dimension: str | None = None
    for pat, dim in DEFAULT_FOLDER_PREFIX_MAP:
        if pat.match(full_label):
            dimension = dim
            break

    # Extract prefix-only via regex; trailing text -> description
    match = _VALUE_PREFIX_RE.match(full_label)
    if match:
        value = match.group(1)
        rest = full_label[len(value):].lstrip("- ").strip()
        extra = {"description": rest} if rest else {}
    else:
        value = full_label
        extra = {}

    return dimension, value, extra


def walk_folders(graphml_path: Path | str) -> list[FolderCandidate]:
    """Walk yEd group folder hierarchy and build candidates.

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        List of FolderCandidate in document order. Empty list if no
        folders found, parse error, or missing file.

    Raises:
        CycleDetectedError: if folder A contains folder B contains
            folder A (malformed graphml). Hook's outer try/except
            swallows this gracefully.
    """
    path = Path(graphml_path)
    if not path.exists():
        return []

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"
    Y_NS = "{http://www.yworks.com/xml/graphml}"

    try:
        tree = _ET.parse(str(path))
    except Exception:
        return []

    root = tree.getroot()

    result: list[FolderCandidate] = []
    visited: set[str] = set()

    def _is_top_level_tablenode(node) -> bool:
        """True if this folder is the swimlane (has TableNode child)."""
        tn = node.find(f".//{Y_NS}TableNode")
        return tn is not None and tn.get("configuration") == "YED_TABLE_NODE"

    def _extract_label(node) -> str:
        """First non-empty <y:NodeLabel> text."""
        for nl in node.iter(f"{Y_NS}NodeLabel"):
            txt = (nl.text or "").strip()
            if txt:
                return txt
        return ""

    def _walk(node, parent_id: str | None):
        nid = node.get("id") or ""
        if nid in visited:
            raise CycleDetectedError(
                f"Cycle detected: folder {nid!r} visited twice"
            )
        visited.add(nid)

        # Find this folder's nested <graph> element (direct child)
        inner_graph = node.find(f"{GRAPHML_NS}graph")
        member_ids: list[str] = []
        nested_ids: list[str] = []

        if inner_graph is not None:
            for child in inner_graph.findall(f"{GRAPHML_NS}node"):
                cid = child.get("id") or ""
                if child.get("yfiles.foldertype") == "group":
                    # Skip top-level TableNode swimlane (handled by
                    # table_parser). For non-TableNode subfolders,
                    # record + recurse.
                    if _is_top_level_tablenode(child):
                        continue
                    nested_ids.append(cid)
                    # Recurse (depth-first walk)
                    _walk(child, parent_id=nid)
                else:
                    member_ids.append(cid)

        full_label = _extract_label(node)
        dim, value, extra = _classify_label(full_label)
        candidate = FolderCandidate(
            yed_id=nid,
            full_label=full_label,
            auto_dimension=dim,
            user_dimension=dim,
            auto_value=value,
            user_value=value,
            member_yed_ids=member_ids,
            nested_folder_ids=nested_ids,
            parent_folder_id=parent_id,
            extra_attrs=extra,
        )
        result.append(candidate)

    # Top-level: iterate all <graph><node yfiles.foldertype="group">
    # in document order. Skip the TableNode swimlane.
    for top_graph in root.findall(f"{GRAPHML_NS}graph"):
        for child in top_graph.findall(f"{GRAPHML_NS}node"):
            if child.get("yfiles.foldertype") != "group":
                continue
            if _is_top_level_tablenode(child):
                # Swimlane container — recurse INTO it to find
                # nested folders, but don't record it.
                inner = child.find(f"{GRAPHML_NS}graph")
                if inner is not None:
                    for inner_child in inner.findall(
                            f"{GRAPHML_NS}node"):
                        if inner_child.get(
                                "yfiles.foldertype") == "group":
                            _walk(inner_child, parent_id=None)
                continue
            _walk(child, parent_id=None)

    return result
