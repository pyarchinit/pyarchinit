"""yEd-flavor detection for graphml import.

Distinguishes graphmls produced by pyarchinit's own GraphProjector
(`pyarchinit-projected`) from graphmls authored externally in yEd
or other tools (`yed-raw`).

The detection marker is the presence of ANY `pyarchinit.<*>` key in
the top-level `<key>` declarations of the graphml — NOT specifically
`pyarchinit.node_uuid` (that key is conditionally emitted only when
the source DB has node_uuid populated; the robust marker is the
namespace prefix).

O(1) header scan: stops at the first `<graph>` element. Safe-default
to `"yed-raw"` on parse error / missing file / empty file — the
yEd-aware pipeline downstream will surface the problem to the user.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

GraphMLFlavor = Literal["pyarchinit-projected", "yed-raw"]


def detect_flavor(graphml_path: Path | str) -> GraphMLFlavor:
    """Return the graphml flavor based on key declarations.

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        ``"pyarchinit-projected"`` if any top-level ``<key>`` declares an
        attribute name starting with ``pyarchinit.``; ``"yed-raw"``
        otherwise (including all error cases: file not found,
        unparseable XML, empty content).

    Behaviour:
        - lxml.etree.iterparse preferred for speed
        - xml.etree.iterparse fallback when lxml unavailable
        - stops scanning at the first ``<graph>`` element open event
          (key declarations always precede the graph in valid graphml)
        - O(1) in graphml size — file is not fully loaded
    """
    path = Path(graphml_path)
    if not path.exists():
        return "yed-raw"

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"

    try:
        context = _ET.iterparse(str(path), events=("start", "end"))
        for event, elem in context:
            tag = elem.tag
            if event == "end" and tag == f"{GRAPHML_NS}key":
                attr_name = elem.get("attr.name") or ""
                if attr_name.startswith("pyarchinit."):
                    return "pyarchinit-projected"
                elem.clear()
            elif event == "start" and tag == f"{GRAPHML_NS}graph":
                return "yed-raw"
    except Exception:
        return "yed-raw"

    return "yed-raw"
