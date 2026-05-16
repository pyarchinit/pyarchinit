"""Label-prefix classifier for yEd-raw graphml leaf nodes.

Maps leaf node label patterns (US*, USV*, SF*, VSF*, D.*, C.*,
material/position/height/...) to ClassificationKind enum values
that drive the downstream import pipeline (yE-C onward).

The detection pattern is regex-based and order-sensitive: more
specific patterns (USV*, USM*, VSF*) must precede generic ones
(US*, SF*) to avoid mis-classification. The DEFAULT_CLASSIFIER_RULES
list is the single source of truth for MVP (yE-B); the dialog in
yE-E will let the user override per-node.

Folder nodes (yfiles.foldertype="group") are EXCLUDED from
classification -- yE-C `yed_group_walker` handles them separately.

Added in yE-B (yed-import-classifier-5.7.6-alpha). Inherits design
from parent spec docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md §5
specialized to Path-only input for MVP.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ClassificationKind(str, Enum):
    """Leaf classification destinations (14 values since EXTRACTOR added)."""
    US_REAL          = "us_real"
    US_MASONRY       = "us_masonry"
    US_DOCUMENTARY   = "us_documentary"
    USV_VIRTUAL      = "usv_virtual"
    USV_FORMAL       = "usv_formal"
    SPECIAL_FIND     = "special_find"
    VIRTUAL_FIND     = "virtual_find"
    # s3dgraphy 0.1.42 introduced ReusedSpecialFind for spolia: re-used
    # architectural / decorative elements with a stratigraphic identity
    # of their own (family=real, non-series). DP-26 last pre-EM-1.5
    # Development Project. Routed to us_table like the other US family
    # members with unita_tipo='RSF'.
    REUSED_SPECIAL_FIND = "reused_special_find"
    DOCUMENT         = "document"
    COMBINER         = "combiner"
    EXTRACTOR        = "extractor"
    PROPERTY         = "property"
    UNKNOWN          = "unknown"
    SKIP             = "skip"


# Default regex map (ORDER-SENSITIVE -- first match wins).
# Specific prefixes (USV, USM, USD, VSF, RSF) MUST precede generic
# ones (US, SF) to avoid mis-classification.
DEFAULT_CLASSIFIER_RULES: list[tuple[re.Pattern, ClassificationKind]] = [
    (re.compile(r"^USVs\d*$|^USVn\d*$"),            ClassificationKind.USV_FORMAL),
    (re.compile(r"^USV\d+"),                        ClassificationKind.USV_VIRTUAL),
    (re.compile(r"^USM\d+|^USR\d+|^USS\d+"),        ClassificationKind.US_MASONRY),
    (re.compile(r"^USD\d+"),                        ClassificationKind.US_DOCUMENTARY),
    (re.compile(r"^US\d+"),                         ClassificationKind.US_REAL),
    (re.compile(r"^VSF\d+"),                        ClassificationKind.VIRTUAL_FIND),
    # RSF MUST precede SF (RSF labels start with R, but kept explicit
    # for documentation — a stricter `^SF\d+` would still match e.g.
    # 'SF101' but not 'RSF101').
    (re.compile(r"^RSF\d+"),                        ClassificationKind.REUSED_SPECIAL_FIND),
    (re.compile(r"^SF\d+"),                         ClassificationKind.SPECIAL_FIND),
    (re.compile(r"^D\.\d+"),                        ClassificationKind.DOCUMENT),
    (re.compile(r"^C\.\d+"),                        ClassificationKind.COMBINER),
    (re.compile(r"^E\.\d+"),                        ClassificationKind.EXTRACTOR),
    (re.compile(
        r"^(material|position|width|length|height|heigth|type|color|weight|proportion|size)$",
        re.I,
    ),                                              ClassificationKind.PROPERTY),
]


@dataclass
class ClassifiedNode:
    """One leaf node classified by the heuristic.

    `auto_kind` is what the classifier produced.
    `user_kind` is initially equal to `auto_kind`; the yE-E dialog
    lets the user override per-node before commit. yE-B always
    leaves them equal (no dialog yet).
    """
    yed_id: str
    label: str
    auto_kind: ClassificationKind
    user_kind: ClassificationKind
    extra_attrs: dict = field(default_factory=dict)


def classify_leaves(
    graphml_path: Path | str,
    rules: list[tuple[re.Pattern, ClassificationKind]] | None = None,
) -> list[ClassifiedNode]:
    """Classify every leaf node in the graphml by label-prefix.

    Returns nodes in yEd document order (preserving authoring sequence,
    so the dialog in yE-E can present them in the order the user
    expects).

    Empty / malformed / missing file -> [] (safe default -- caller
    falls through to legacy path).

    Folder nodes (yfiles.foldertype="group") are skipped -- yE-C
    yed_group_walker handles them.

    Args:
        graphml_path: filesystem path to the .graphml file.
        rules: optional override of DEFAULT_CLASSIFIER_RULES (for
            unit testing or future extensibility). None uses default.

    Returns:
        List of ClassifiedNode in document order. Empty list on any
        error (file missing, parse error, etc.).
    """
    path = Path(graphml_path)
    if not path.exists():
        return []

    active_rules = rules if rules is not None else DEFAULT_CLASSIFIER_RULES

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"
    Y_NS = "{http://www.yworks.com/xml/graphml}"

    result: list[ClassifiedNode] = []
    try:
        context = _ET.iterparse(str(path), events=("end",))
        for _event, elem in context:
            if elem.tag != f"{GRAPHML_NS}node":
                continue
            # Skip group folders -- yE-C territory
            if elem.get("yfiles.foldertype") == "group":
                elem.clear()
                continue

            yed_id = elem.get("id") or ""
            # Find first non-empty NodeLabel descendant text
            label = ""
            for nl in elem.iter(f"{Y_NS}NodeLabel"):
                txt = (nl.text or "").strip()
                if txt:
                    label = txt
                    break

            # Bug I (2026-05-15 user feedback): mirror the s3dgraphy
            # importer's discrimination logic so D.NN (BPMN data
            # object) → DocumentNode and D.NN.MM (no BPMN type) →
            # ExtractorNode. Without this, both labels match the same
            # ``D\.\d+`` regex → both classified as DOCUMENT → the
            # us_table dedup collapses them into ONE row → edges from
            # extractors back to their parent document become self-
            # loops and get dropped. The check inspects:
            #   * ``<y:Property name="...dataObjectType"
            #       value="DATA_OBJECT_TYPE_PLAIN"/>`` → DocumentNode
            #   * ``<y:Property name="...type"
            #       value="ARTIFACT_TYPE_ANNOTATION"/>`` → PropertyNode
            # These take precedence over the label-prefix rules.
            bpmn_kind = _detect_bpmn_kind(elem, Y_NS)

            # Run rules in order; first match wins
            kind = ClassificationKind.UNKNOWN
            for pattern, target_kind in active_rules:
                if pattern.match(label):
                    kind = target_kind
                    break

            # BPMN signal overrides label-based fallback for paradata:
            # mirrors s3dgraphy's import_graphml.py dispatch order
            # (document → property → extractor → combiner).
            if bpmn_kind is not None:
                kind = bpmn_kind
            elif kind == ClassificationKind.DOCUMENT and "." in label[2:]:
                # Label-only fallback: ``D.NN.MM`` (multi-level path
                # after the alphabetic prefix) is an Extractor in the
                # EM convention, NOT a Document. The DOCUMENT regex
                # ``^D\.\d+`` only matched the prefix — the second dot
                # tells us this is hierarchical.
                kind = ClassificationKind.EXTRACTOR

            result.append(ClassifiedNode(
                yed_id=yed_id,
                label=label,
                auto_kind=kind,
                user_kind=kind,
            ))
            elem.clear()
    except Exception:
        # Parse errors / IO errors -> safe-default empty list
        return []

    return result


def _detect_bpmn_kind(node_element, y_ns: str):
    """Read yEd BPMN ``<y:Property>`` markers to discriminate paradata
    flavors that share the same label prefix.

    Returns ``ClassificationKind.DOCUMENT`` if the node carries the
    BPMN data-object property; ``ClassificationKind.PROPERTY`` if it
    carries the BPMN annotation property; ``None`` otherwise (caller
    falls back to label-prefix rules).

    Used by ``classify_leaves`` to mirror s3dgraphy's importer
    (``import_graphml.py:1718-1799``) so the round-trip through
    pyArchInit doesn't lose the Document/Extractor distinction.
    """
    for prop in node_element.iter(f"{y_ns}Property"):
        name = prop.attrib.get("name", "")
        value = prop.attrib.get("value", "")
        if (name.endswith("dataObjectType")
                and value == "DATA_OBJECT_TYPE_PLAIN"):
            return ClassificationKind.DOCUMENT
        if (name.endswith(".type")
                and value == "ARTIFACT_TYPE_ANNOTATION"):
            return ClassificationKind.PROPERTY
    return None
