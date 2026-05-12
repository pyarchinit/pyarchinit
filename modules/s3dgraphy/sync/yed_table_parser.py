"""yEd TableNode period extractor (yE-C Parsers, 5.7.7-alpha).

Reads the top-level <y:TableNode configuration="YED_TABLE_NODE"> of a
yEd-raw graphml and extracts archaeological period candidates from
its swimlane rows. Each row produces a PeriodCandidate with:
  - auto_label from <y:NodeLabel> text
  - auto_periodo from 1-based row ordinal
  - auto_fase always 1 (yEd table rows don't encode phases)
  - member_yed_ids from leaf nodes whose Y-coordinate falls in the
    row's Y-range

datazione_iniziale / datazione_finale are NOT extracted (yEd doesn't
encode dates on table rows) — user fills them later in the
pyarchinit Periodizzazione tab.

Folder nodes (yfiles.foldertype="group") are skipped in the
membership scan — yE-C yed_group_walker handles them.

Returns [] on parse error / missing file / no TableNode (safe
default; the branch hook's try/except wrapper passes through).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PeriodCandidate:
    """One period extracted from a yEd TableNode row.

    auto_* fields are heuristic-derived; user_* are editable by the
    yE-E dialog (in yE-C they default to auto_* values).
    """
    yed_row_id: str
    auto_label: str
    user_label: str
    auto_periodo: int
    auto_fase: int
    user_periodo: int
    user_fase: int
    member_yed_ids: list[str] = field(default_factory=list)
    y_min: float = 0.0
    y_max: float = 0.0


def extract_periods(graphml_path: Path | str) -> list[PeriodCandidate]:
    """Find top-level yEd TableNode rows and build PeriodCandidate list.

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        List of PeriodCandidate in row document order. Empty list if
        no TableNode found, malformed file, or missing file.
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

    # First pass: find the first top-level y:TableNode + extract its
    # geometry, row labels, row heights.
    table_node = None
    table_geom_y = 0.0
    table_geom_x = 0.0
    table_geom_width = 0.0
    rows: list[tuple[str, str, float]] = []  # (row_id, label, height)
    header_height = 30.0  # yEd default if not specified

    for node in root.iter(f"{GRAPHML_NS}node"):
        tn = node.find(f".//{Y_NS}TableNode")
        if tn is not None and tn.get("configuration") == "YED_TABLE_NODE":
            table_node = node
            # Geometry of the TableNode itself
            geom = tn.find(f"{Y_NS}Geometry")
            if geom is not None:
                try:
                    table_geom_y = float(geom.get("y") or "0")
                    table_geom_x = float(geom.get("x") or "0")
                    table_geom_width = float(geom.get("width") or "0")
                except (ValueError, TypeError):
                    pass

            # Build {row_id: label} from NodeLabels with
            # RowNodeLabelModelParameter children
            row_labels: dict[str, str] = {}
            for nl in tn.findall(f"{Y_NS}NodeLabel"):
                rmp = nl.find(
                    f".//{Y_NS}RowNodeLabelModelParameter")
                if rmp is not None:
                    rid = rmp.get("id") or ""
                    txt = (nl.text or "").strip()
                    row_labels[rid] = txt

            # Header height (yEd Insets top), if specified
            table_el = tn.find(f"{Y_NS}Table")
            if table_el is not None:
                insets = table_el.find(f"{Y_NS}Insets")
                if insets is not None:
                    try:
                        header_height = float(
                            insets.get("top") or "30.0")
                    except (ValueError, TypeError):
                        pass

                # Row geometries in order
                rows_el = table_el.find(f"{Y_NS}Rows")
                if rows_el is not None:
                    for row_el in rows_el.findall(f"{Y_NS}Row"):
                        rid = row_el.get("id") or ""
                        try:
                            height = float(
                                row_el.get("height") or "0")
                        except (ValueError, TypeError):
                            height = 0.0
                        label = row_labels.get(rid, "")
                        if not label:
                            # Placeholder for empty-label rows
                            label = f"row_{len(rows)}"
                        rows.append((rid, label, height))
            break  # only the first top-level TableNode

    if not rows:
        return []

    # Build PeriodCandidate list with Y ranges
    periods: list[PeriodCandidate] = []
    current_y = table_geom_y + header_height
    for idx, (rid, label, height) in enumerate(rows):
        y_min = current_y
        y_max = current_y + height
        periods.append(PeriodCandidate(
            yed_row_id=rid,
            auto_label=label,
            user_label=label,
            auto_periodo=idx + 1,
            auto_fase=1,
            user_periodo=idx + 1,
            user_fase=1,
            member_yed_ids=[],
            y_min=y_min,
            y_max=y_max,
        ))
        current_y = y_max

    if not periods:
        return []

    # Second pass: assign every non-folder leaf to a row by Y-coord.
    # Skip the TableNode itself and any node with foldertype="group".
    table_node_id = table_node.get("id") if table_node is not None else None
    for node in root.iter(f"{GRAPHML_NS}node"):
        nid = node.get("id") or ""
        if nid == table_node_id:
            continue
        if node.get("yfiles.foldertype") == "group":
            continue
        # Find <y:Geometry y="...">
        geom = node.find(f".//{Y_NS}Geometry")
        if geom is None:
            continue
        try:
            y = float(geom.get("y") or "")
        except (ValueError, TypeError):
            continue
        # Find which row contains it
        for period in periods:
            if period.y_min <= y < period.y_max:
                period.member_yed_ids.append(nid)
                break

    return periods
