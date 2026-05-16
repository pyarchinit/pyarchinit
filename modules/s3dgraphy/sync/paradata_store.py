"""Site-scoped CRUD for paradata.graphml (atomic-safe writes).

AI05 Phase 2 closure. Manages the 3 node types without an SQL
counterpart in pyarchinit:
    - AuthorNode    (authorship metadata)
    - LicenseNode   (rights / SPDX licence)
    - EmbargoNode   (embargo dates)

File location: {db_path.parent}/paradata_{sito_slug}.graphml
where sito_slug is `re.sub(r'\\W+', '_', sito).lower()`.

Atomic writes via .tmp + os.replace() — crash-safe.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ._db_handle import _resolve_db_handle
from ._workspace import _resolve_workspace_dir
from .graph_ingestor import GraphSyncError


# ---------------------------------------------------------------------------
# Exception hierarchy (spec §5.1, extends GraphSyncError so existing
# try/except GraphSyncError handlers in CLI/UI/tests continue to catch).
# ---------------------------------------------------------------------------
class ParadataStoreError(GraphSyncError):
    """Base for ParadataStore errors."""


class ParadataReadError(ParadataStoreError):
    """File parse / schema error during read()."""


class ParadataWriteError(ParadataStoreError):
    """File write / atomic-rename failure during write()."""


class ParadataValidationError(ParadataStoreError):
    """Caller passed bogus data to add_author/license/embargo/etc."""


class ParadataNotFoundError(ParadataStoreError):
    """Required file missing where caller expected it."""


# ---------------------------------------------------------------------------
# ParadataStore
# ---------------------------------------------------------------------------
_PARADATA_NODE_TYPES: frozenset[str] = frozenset({
    "AuthorNode", "LicenseNode", "EmbargoNode",
    # 2026-05-15 yed-fastfix: the Extended Matrix paradata family also
    # spans Document / Combiner / Extractor / Property nodes. yE-D
    # dispatches each ClassificationKind → ``add_<kind>`` here; before
    # the fix only the authorship trio existed so 100% of the dispatch
    # silently skipped (manifested as paradata file never created).
    "DocumentNode", "CombinerNode", "ExtractorNode", "PropertyNode",
})


# Dedup key regex: paradata nodes that share an identity but differ by
# trailing suffix/sequence (e.g. ``D.001`` / ``D.001-2`` / ``D.001bis``)
# collapse to a single node with multiple inbound edges. The key is the
# prefix + first decimal run; anything after is discarded.
_PARADATA_DEDUP_RE = re.compile(r"^([A-Za-z]+\.?\d+)")


def _paradata_dedup_key(label: str) -> str:
    """Compute a dedup key for a paradata leaf label.

    Examples:
      'D.001'        → 'D.001'
      'D.001-2'      → 'D.001'
      'D.001bis'     → 'D.001'
      'D.001/3'      → 'D.001'
      'material'     → 'material'   (PROPERTY labels — no numeric suffix)
      'C.42'         → 'C.42'
    """
    if not label:
        return ""
    m = _PARADATA_DEDUP_RE.match(label)
    return m.group(1) if m else label

# Meta-keys produced by s3dgraphy's GraphMLImporter when it materializes
# a node (``original_id``, ``graph_id``) plus our own JSON-blob channel
# (``paradata_attrs``) that the importer additionally surfaces on
# ``node.attributes`` because we declare it as a ``<key>`` in the
# minimal GraphML emitter. These must NEVER be merged back from the
# decoded blob during _hydrate_paradata_attrs — otherwise the next
# write() would re-serialize them inside a fresh JSON blob, growing
# the file ~300 bytes per round-trip and breaking idempotency.
_PARADATA_HYDRATE_SKIP_KEYS: frozenset[str] = frozenset({
    "original_id", "graph_id", "paradata_attrs",
})


def _sito_slug(sito: str) -> str:
    """Filename-safe lowercase slug for a sito identifier."""
    return re.sub(r"\W", "_", sito).strip("_").lower()


class ParadataStore:
    """Site-scoped CRUD for paradata.graphml.

    Args:
        db_path: filesystem path to the pyarchinit SQLite DB; the
            paradata file lives in the same directory.
        sito: site identifier (a value from `us_table.sito`).

    Raises on instantiation: nothing (lazy file checks; read/write
    perform actual I/O).
    """

    def __init__(self, db_path, sito: str) -> None:
        """Construct a site-scoped paradata store.

        PG-D (5.7.3-alpha): ``db_path`` accepts ``Path | DbHandle | str``
        via the ``_resolve_db_handle`` shim from Foundation. Backward
        compat preserved for legacy callers passing a Path.
        """
        if not sito:
            raise ParadataValidationError(
                "sito is required for ParadataStore")
        self._handle = _resolve_db_handle(db_path)
        # Preserve self._db_path for any defensive code that reads it
        # directly (currently only used here for repr/debug, but keep
        # the attribute to avoid breaking subclasses).
        self._db_path = (
            self._handle.sqlite_path
            if self._handle.sqlite_path is not None
            else Path(self._handle.conn_str)
        )
        self._sito = sito
        self._slug = _sito_slug(sito)

    @property
    def file_path(self) -> Path:
        """Resolved paradata file path for this (db, sito) pair.

        PG-D (5.7.3-alpha): SQLite returns `<sqlite_parent>/paradata_<sito>.graphml`
        (byte-identical to pre-PG-D). PG returns
        `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/paradata_<sito>.graphml`.
        """
        return (
            _resolve_workspace_dir(self._handle, self._sito)
            / f"paradata_{self._slug}.graphml"
        )

    def exists(self) -> bool:
        """Whether the paradata file is present on disk."""
        return self.file_path.exists()

    @property
    def sito(self) -> str:
        return self._sito

    # ---- Low-level (D5) ------------------------------------------------
    def read(self):
        """Return a Graph populated with only the paradata-family
        nodes from the file. Returns empty Graph when file absent."""
        from s3dgraphy import Graph
        if not self.exists():
            graph = Graph(graph_id=self._sito)
            # Defensive filter even on empty: Graph() bootstraps a
            # default GeoPositionNode which is not paradata.
            graph.nodes = [
                n for n in graph.nodes
                if type(n).__name__ in _PARADATA_NODE_TYPES
            ]
            return graph
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
            graph = GraphMLImporter(filepath=str(self.file_path)).parse()
        except Exception as e:
            raise ParadataReadError(
                f"Cannot parse {self.file_path}: {e}") from e
        # AI04 helper to recover stripped attrs
        try:
            from .graph_ingestor import _hydrate_pyarchinit_data_keys
            _hydrate_pyarchinit_data_keys(graph, self.file_path)
        except Exception:
            pass
        # Paradata-specific hydrator: re-attach the JSON-blob attrs
        # we wrote out on each paradata node.
        try:
            self._hydrate_paradata_attrs(graph)
        except Exception:
            pass
        # Defensive filter: drop non-paradata node types
        graph.nodes = [
            n for n in graph.nodes
            if type(n).__name__ in _PARADATA_NODE_TYPES
        ]

        # yed-fastfix 2026-05-15: GraphMLImporter._create_paradata_image_node
        # only recognises Author / AuthorAI / License / Embargo. DocumentNode
        # / CombinerNode / ExtractorNode / PropertyNode emitted by the yE-D
        # paradata writers carry the same ``_s3d_node_type:`` round-trip
        # marker but are dropped on read. Scan the XML directly and
        # reconstruct those four types so the round-trip is symmetric.
        try:
            self._merge_extended_paradata_nodes(graph)
        except Exception:
            # Defensive: never let the extended-merge break a successful
            # importer pass.
            pass

        return graph

    _EXTENDED_PARADATA_TYPES: frozenset[str] = frozenset({
        "DocumentNode", "CombinerNode", "ExtractorNode", "PropertyNode",
    })

    def _merge_extended_paradata_nodes(self, graph) -> None:
        """Reconcile DocumentNode / CombinerNode / ExtractorNode /
        PropertyNode after the s3dgraphy GraphMLImporter.

        Two distinct cases the importer mishandles:

        1. **Drop** — Author / AuthorAI / License / Embargo round-trip
           via ``_create_paradata_image_node`` (Signal 1 marker
           handled). Document / Combiner / Extractor / Property are
           NOT supported there, so the importer just drops them.

        2. **Mis-classify** — the importer also runs a hardcoded
           "label starts with ``D.``  → ExtractorNode" rule
           (``import_graphml.py:1820``) that fires REGARDLESS of any
           ``_s3d_node_type:`` marker. A DocumentNode written with
           label ``D.001`` and a ``DocumentNode`` marker comes back
           as an ExtractorNode unless we override.

        Strategy: scan the file ourselves, find every ``<node>`` whose
        description ``<data>`` carries ``_s3d_node_type:<one of the 4>``;
        if a node with the same node_id is already in the graph but of
        the wrong class, REMOVE it and re-add with the correct subclass.
        Missing nodes are appended.
        """
        from lxml import etree as ET
        import json as _json
        NS = "http://graphml.graphdrawing.org/xmlns"
        marker = "_s3d_node_type:"

        try:
            tree = ET.parse(str(self.file_path))
        except Exception:
            return
        root = tree.getroot()

        # Resolve key ids by attr.name.
        key_by_name: dict[str, str] = {}
        for k in root.findall(f"{{{NS}}}key"):
            name = k.get("attr.name")
            if name:
                key_by_name[name] = k.get("id")
        desc_kid = key_by_name.get("description")
        attrs_kid = key_by_name.get("pyarchinit.paradata_attrs")

        existing_by_id = {
            getattr(n, "node_id", None): n for n in graph.nodes
        }

        for node_el in root.iter(f"{{{NS}}}node"):
            node_id = node_el.get("id")
            if not node_id:
                continue

            # Read description data
            description_text = ""
            attrs_blob = None
            for d_el in node_el.findall(f"{{{NS}}}data"):
                kid = d_el.get("key")
                if kid == desc_kid and d_el.text:
                    description_text = d_el.text
                elif kid == attrs_kid and d_el.text:
                    try:
                        attrs_blob = _json.loads(d_el.text)
                    except (ValueError, TypeError):
                        attrs_blob = None

            # Detect type marker
            idx = description_text.find(marker)
            if idx < 0:
                continue
            tail = description_text[idx + len(marker):]
            import re as _re
            m = _re.match(r"([A-Za-z_][A-Za-z0-9_]*)", tail)
            if not m:
                continue
            type_name = m.group(1)
            if type_name not in self._EXTENDED_PARADATA_TYPES:
                continue

            # If the importer already produced this node_id with the
            # SAME type, leave it alone. Otherwise drop the misclassified
            # instance so we can re-add with the correct subclass.
            already = existing_by_id.get(node_id)
            if already is not None and type(already).__name__ == type_name:
                continue
            if already is not None:
                graph.nodes = [
                    n for n in graph.nodes
                    if getattr(n, "node_id", None) != node_id
                ]
                existing_by_id.pop(node_id, None)

            # Extract label from y:NodeLabel
            label_text = ""
            for nl in node_el.iter(
                    "{http://www.yworks.com/xml/graphml}NodeLabel"):
                if nl.text and nl.text.strip():
                    label_text = nl.text.strip()
                    break

            # Strip the round-trip marker from description.
            clean_desc = _re.sub(
                r"\s*" + _re.escape(marker)
                + r"[A-Za-z_][A-Za-z0-9_]*\s*",
                "", description_text,
            ).strip()

            try:
                if type_name == "DocumentNode":
                    from s3dgraphy.nodes.document_node import DocumentNode
                    node = DocumentNode(
                        node_id=node_id,
                        name=label_text or node_id,
                        description=clean_desc,
                    )
                elif type_name == "CombinerNode":
                    from s3dgraphy.nodes.combiner_node import CombinerNode
                    node = CombinerNode(
                        node_id=node_id,
                        name=label_text or node_id,
                        description=clean_desc,
                    )
                elif type_name == "ExtractorNode":
                    from s3dgraphy.nodes.extractor_node import ExtractorNode
                    node = ExtractorNode(
                        node_id=node_id,
                        name=label_text or node_id,
                        description=clean_desc,
                    )
                elif type_name == "PropertyNode":
                    from s3dgraphy.nodes.property_node import PropertyNode
                    try:
                        node = PropertyNode(
                            node_id=node_id,
                            name=label_text or node_id,
                            description=clean_desc,
                            property_type=label_text or node_id,
                        )
                    except TypeError:
                        node = PropertyNode(
                            node_id=node_id,
                            name=label_text or node_id,
                            description=clean_desc,
                        )
                else:
                    continue
            except Exception:
                continue

            # Hydrate attributes from the d5 JSON blob
            attrs = {}
            if isinstance(attrs_blob, dict):
                for k, v in attrs_blob.items():
                    if k in _PARADATA_HYDRATE_SKIP_KEYS:
                        continue
                    attrs[k] = v
            try:
                node.attributes = attrs
            except Exception:
                pass
            graph.nodes.append(node)

    def _hydrate_paradata_attrs(self, graph) -> None:
        """Re-parse the paradata file and merge the JSON-blob
        ``pyarchinit.paradata_attrs`` data values back onto each
        node's ``.attributes`` dict. This is how high-level helpers
        (orcid, role, spdx_id, url, until_date, reason) survive a
        round-trip — s3dgraphy's importer strips unknown <data>
        keys, so we serialise them in our own JSON blob.
        """
        from lxml import etree as ET
        import json as _json
        NS = "http://graphml.graphdrawing.org/xmlns"
        try:
            tree = ET.parse(str(self.file_path))
        except Exception:
            return
        root = tree.getroot()
        # Find our custom key id (registered as
        # attr.name="pyarchinit.paradata_attrs").
        attrs_kid = None
        for k in root.findall(f"{{{NS}}}key"):
            if k.get("attr.name") == "pyarchinit.paradata_attrs":
                attrs_kid = k.get("id")
                break
        if not attrs_kid:
            return
        emid_to_node = {getattr(n, "node_id", None): n for n in graph.nodes}
        for node_el in root.iter(f"{{{NS}}}node"):
            blob_text = None
            emid = node_el.get("id")
            for d_el in node_el.findall(f"{{{NS}}}data"):
                if d_el.get("key") == attrs_kid and d_el.text:
                    blob_text = d_el.text
                    break
            if blob_text is None:
                continue
            try:
                blob = _json.loads(blob_text)
            except (ValueError, TypeError):
                continue
            n = emid_to_node.get(emid)
            if n is None:
                continue
            attrs = getattr(n, "attributes", None)
            if attrs is None:
                try:
                    n.attributes = {}
                    attrs = n.attributes
                except Exception:
                    continue
            # Strip s3dgraphy importer meta-keys + the raw JSON blob
            # the importer surfaced from our <key id="d5"> declaration.
            # Leaving these on .attributes would cause the next write()
            # to re-serialize them inside a fresh JSON blob, growing
            # the file ~300 bytes per round-trip and breaking the
            # idempotency invariant.
            for skip_key in _PARADATA_HYDRATE_SKIP_KEYS:
                attrs.pop(skip_key, None)
            for k, v in blob.items():
                if k in _PARADATA_HYDRATE_SKIP_KEYS:
                    continue
                if attrs.get(k) in (None, ""):
                    attrs[k] = v

    def write(self, graph) -> None:
        """Atomic write: serialise to .tmp, embed AI04 data keys,
        os.replace() to final path. Original file untouched on
        failure.

        Uses a custom minimal-GraphML serializer (rather than the
        full ``GraphMLExporter``) because the latter only emits
        paradata image nodes when they sit inside a
        ``ParadataNodeGroup`` attached to a stratigraphic unit; the
        site-level paradata file holds isolated AuthorNode /
        LicenseNode / EmbargoNode nodes with no stratigraphic
        anchors, so the heavyweight exporter would silently drop
        them. The minimal output we emit here uses the
        ``_s3d_node_type:`` round-trip marker (Signal 1 in the
        importer's ``_detect_paradata_image_type``), so
        ``GraphMLImporter`` reconstructs the right subclass on
        read().
        """
        tmp = self.file_path.with_suffix(".graphml.tmp")
        try:
            self._write_minimal_graphml(graph, tmp)
            # Embed pyarchinit data keys so round-trip preserves
            # the AI04-introduced attributes (sito + any extra
            # values stashed on node.attributes).
            from .graphml_writer import _embed_pyarchinit_data_keys
            _embed_pyarchinit_data_keys(graph, tmp)
            # Atomic rename — POSIX + Windows >= Vista.
            os.replace(str(tmp), str(self.file_path))
        except Exception as e:
            # Cleanup tmp if it exists; original is untouched.
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            raise ParadataWriteError(
                f"Cannot write {self.file_path}: {e}") from e

    def _write_minimal_graphml(self, graph, out_path: Path) -> None:
        """Emit a minimal GraphML file containing only the paradata
        nodes from *graph*. Each node carries the round-trip
        ``_s3d_node_type:<NodeType>`` marker in its description so
        ``GraphMLImporter`` rebuilds the right subclass.
        """
        from lxml import etree as ET

        NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
        NS_Y = "http://www.yworks.com/xml/graphml"
        NSMAP = {None: NS_GRAPHML, "y": NS_Y}

        root = ET.Element(f"{{{NS_GRAPHML}}}graphml", nsmap=NSMAP)

        # <key> declarations — match what the importer's
        # build_key_mapping() expects to find.
        keys = [
            ("d0", "node", None, "url", "string"),
            ("d1", "node", None, "description", "string"),
            ("d2", "node", "nodegraphics", None, None),
            ("d3", "node", None, "EMID", "string"),
            ("d4", "node", None, "URI", "string"),
            # Custom key for the paradata-attrs JSON blob (our own
            # round-trip channel for orcid / role / spdx_id /
            # until_date / reason / etc., since s3dgraphy's importer
            # strips unknown <data> keys).
            ("d5", "node", None, "pyarchinit.paradata_attrs", "string"),
        ]
        for kid, kfor, yftype, attr_name, attr_type in keys:
            kel = ET.SubElement(root, f"{{{NS_GRAPHML}}}key")
            kel.set("id", kid)
            kel.set("for", kfor)
            if yftype:
                kel.set("yfiles.type", yftype)
            if attr_name:
                kel.set("attr.name", attr_name)
            if attr_type:
                kel.set("attr.type", attr_type)

        graph_el = ET.SubElement(root, f"{{{NS_GRAPHML}}}graph")
        graph_el.set("id", f"paradata_{self._slug}")
        graph_el.set("edgedefault", "directed")

        # Filter to paradata-only nodes (defensive)
        for node in list(getattr(graph, "nodes", []) or []):
            type_name = type(node).__name__
            if type_name not in _PARADATA_NODE_TYPES:
                continue
            self._emit_paradata_node(graph_el, node, type_name,
                                    NS_GRAPHML, NS_Y)

        tree = ET.ElementTree(root)
        tree.write(str(out_path), encoding="UTF-8",
                   xml_declaration=True, pretty_print=True)

    @staticmethod
    def _emit_paradata_node(graph_el, node, type_name: str,
                            ns_graphml: str, ns_y: str) -> None:
        """Append a single paradata <node> to *graph_el*."""
        from lxml import etree as ET

        node_id = str(getattr(node, "node_id", "") or "")
        display_name = str(getattr(node, "name", "") or type_name)
        description = str(getattr(node, "description", "") or "")
        url = ""
        if type_name == "LicenseNode":
            url = str(getattr(node, "url", "") or "")

        n_el = ET.SubElement(graph_el, f"{{{ns_graphml}}}node")
        n_el.set("id", node_id)

        # d0 — url (LicenseNode only)
        if url:
            d_url = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
            d_url.set("key", "d0")
            d_url.text = url

        # d1 — description, with _s3d_node_type marker
        d_desc = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_desc.set("key", "d1")
        marker = f"_s3d_node_type:{type_name}"
        d_desc.text = (description + ("\n" if description else "")
                       + marker)

        # d2 — nodegraphics with <y:ImageNode> + <y:NodeLabel>
        d_gfx = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_gfx.set("key", "d2")
        img = ET.SubElement(d_gfx, f"{{{ns_y}}}ImageNode")
        nl = ET.SubElement(img, f"{{{ns_y}}}NodeLabel")
        nl.text = display_name

        # d3 — EMID (lets the importer re-use the node_id verbatim)
        d_emid = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_emid.set("key", "d3")
        d_emid.text = node_id

        # d5 — JSON blob carrying node.attributes for round-trip
        # of high-level helper fields (orcid, role, spdx_id,
        # until_date, reason, ...). s3dgraphy's importer drops
        # unknown <data> entries; this is our private channel.
        attrs = getattr(node, "attributes", None) or {}
        if attrs:
            import json as _json
            d_attrs = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
            d_attrs.set("key", "d5")
            d_attrs.text = _json.dumps(
                {k: v for k, v in attrs.items() if v not in (None, "")},
                ensure_ascii=False,
            )

    def add_node(self, node) -> None:
        """Append *node* to the paradata graph + write."""
        type_name = type(node).__name__
        if type_name not in _PARADATA_NODE_TYPES:
            raise ParadataValidationError(
                f"Refusing to store {type_name} in paradata.graphml — "
                f"only {sorted(_PARADATA_NODE_TYPES)} are accepted.")
        graph = self.read()
        graph.add_node(node)
        self.write(graph)

    def remove_node(self, node_uuid: str) -> None:
        """Idempotent removal: no error if node_uuid not found."""
        graph = self.read()
        before = len(graph.nodes)
        graph.nodes = [
            n for n in graph.nodes
            if getattr(n, "node_id", None) != node_uuid
        ]
        if len(graph.nodes) != before:
            self.write(graph)

    # alias for D5/B-style API consistency
    remove = remove_node

    def find(self, node_type: str, **kwargs) -> list:
        """Return matching nodes from the file. Empty list if none."""
        graph = self.read()
        out = []
        for n in graph.nodes:
            if type(n).__name__ != node_type:
                continue
            if all(getattr(n, k, None) == v
                   or (getattr(n, "data", {}) or {}).get(k) == v
                   for k, v in kwargs.items()):
                out.append(n)
        return out

    # ---- High-level (D5) ----------------------------------------------
    def add_author(self, name: str, orcid: str = None,
                   role: str = None) -> str:
        """Create + persist an AuthorNode. Returns the new node_uuid."""
        if not name or not str(name).strip():
            raise ParadataValidationError(
                "AuthorNode requires a non-empty `name`")
        from s3dgraphy.nodes.author_node import AuthorNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = AuthorNode(
            node_id=node_uuid,
            name=str(name),
            orcid=orcid or "noorcid",
        )
        # Stash extra attrs so round-trip preserves them via the AI04
        # data-keys helper; the s3dgraphy AuthorNode itself doesn't
        # have a `role` attr in 0.1.40.
        node.attributes = {
            "sito": self._sito,
            "name": str(name),
            "orcid": orcid or "",
            "role": role or "",
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def list_authors(self) -> list[dict]:
        """Return [{node_uuid, name, orcid, role}, ...]."""
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "AuthorNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            data = getattr(n, "data", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "name": getattr(n, "name", "")
                        or attrs.get("name", "")
                        or data.get("name", ""),
                "orcid": attrs.get("orcid", "")
                         or data.get("orcid", ""),
                "role": attrs.get("role", ""),
            })
        return out

    def add_license(self, spdx_id: str, url: str = None) -> str:
        """Create + persist a LicenseNode."""
        if not spdx_id or not str(spdx_id).strip():
            raise ParadataValidationError(
                "LicenseNode requires a non-empty SPDX id")
        from s3dgraphy.nodes.license_node import LicenseNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = LicenseNode(
            node_id=node_uuid,
            name=str(spdx_id),
            license_type=str(spdx_id),
            url=url or "",
        )
        node.attributes = {
            "sito": self._sito,
            "spdx_id": str(spdx_id),
            "url": url or "",
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def list_licenses(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "LicenseNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            data = getattr(n, "data", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "spdx_id": (attrs.get("spdx_id", "")
                            or data.get("license_type", "")
                            or getattr(n, "name", "")),
                "url": attrs.get("url", "") or data.get("url", ""),
            })
        return out

    def add_embargo(self, until_date: str, reason: str = None) -> str:
        """Create + persist an EmbargoNode."""
        if not until_date or not str(until_date).strip():
            raise ParadataValidationError(
                "EmbargoNode requires a non-empty until_date")
        from s3dgraphy.nodes.embargo_node import EmbargoNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = EmbargoNode(
            node_id=node_uuid,
            name=f"Embargo until {until_date}",
            embargo_end=str(until_date),
            reason=reason or "",
        )
        node.attributes = {
            "sito": self._sito,
            "until_date": str(until_date),
            "reason": reason or "",
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def list_embargos(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "EmbargoNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            data = getattr(n, "data", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "until_date": (attrs.get("until_date", "")
                               or data.get("embargo_end", "")),
                "reason": attrs.get("reason", "") or data.get("reason", ""),
            })
        return out

    # ---- yed-fastfix 2026-05-15: Extended Matrix paradata writers ----

    def _find_by_dedup_key(self, type_name: str,
                          dedup_key: str) -> str | None:
        """Return an existing node_uuid for ``type_name`` whose
        dedup_key (computed from its ``name`` or stored
        ``attributes['dedup_key']``) matches ``dedup_key``.

        Used to collapse paradata leaves that share an identity but
        differ by trailing suffix (D.001 / D.001-2 / D.001bis) into a
        single node with multiple inbound edges.
        """
        if not dedup_key:
            return None
        for n in self.read().nodes:
            if type(n).__name__ != type_name:
                continue
            attrs = getattr(n, "attributes", None) or {}
            stored_key = attrs.get("dedup_key")
            if not stored_key:
                stored_key = _paradata_dedup_key(
                    getattr(n, "name", "") or "")
            if stored_key == dedup_key:
                return getattr(n, "node_id", "") or None
        return None

    def add_document(self, label: str, description: str = "") -> str:
        """Create or dedup a DocumentNode. Returns the node_uuid
        (existing one if a dedup match is found)."""
        if not label or not str(label).strip():
            raise ParadataValidationError(
                "DocumentNode requires a non-empty label")
        dedup_key = _paradata_dedup_key(str(label))
        existing = self._find_by_dedup_key("DocumentNode", dedup_key)
        if existing:
            return existing
        from s3dgraphy.nodes.document_node import DocumentNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = DocumentNode(
            node_id=node_uuid,
            name=str(label),
            description=description or "",
        )
        node.attributes = {
            "sito": self._sito,
            "label": str(label),
            "dedup_key": dedup_key,
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def add_combiner(self, label: str, description: str = "") -> str:
        """Create or dedup a CombinerNode."""
        if not label or not str(label).strip():
            raise ParadataValidationError(
                "CombinerNode requires a non-empty label")
        dedup_key = _paradata_dedup_key(str(label))
        existing = self._find_by_dedup_key("CombinerNode", dedup_key)
        if existing:
            return existing
        from s3dgraphy.nodes.combiner_node import CombinerNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = CombinerNode(
            node_id=node_uuid,
            name=str(label),
            description=description or "",
        )
        node.attributes = {
            "sito": self._sito,
            "label": str(label),
            "dedup_key": dedup_key,
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def add_extractor(self, label: str, description: str = "") -> str:
        """Create or dedup an ExtractorNode."""
        if not label or not str(label).strip():
            raise ParadataValidationError(
                "ExtractorNode requires a non-empty label")
        dedup_key = _paradata_dedup_key(str(label))
        existing = self._find_by_dedup_key("ExtractorNode", dedup_key)
        if existing:
            return existing
        from s3dgraphy.nodes.extractor_node import ExtractorNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = ExtractorNode(
            node_id=node_uuid,
            name=str(label),
            description=description or "",
        )
        node.attributes = {
            "sito": self._sito,
            "label": str(label),
            "dedup_key": dedup_key,
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def add_property(self, label: str, value: str = "",
                     description: str = "") -> str:
        """Create or dedup a PropertyNode.

        PROPERTY labels are usually canonical names (``material``,
        ``height``, ``width``, ...); dedup falls back to the label
        itself when no numeric prefix is present.
        """
        if not label or not str(label).strip():
            raise ParadataValidationError(
                "PropertyNode requires a non-empty label")
        dedup_key = _paradata_dedup_key(str(label))
        existing = self._find_by_dedup_key("PropertyNode", dedup_key)
        if existing:
            return existing
        from s3dgraphy.nodes.property_node import PropertyNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        # PropertyNode signature varies across s3dgraphy versions;
        # try the rich signature first, fall back to the minimal one.
        try:
            node = PropertyNode(
                node_id=node_uuid,
                name=str(label),
                description=description or "",
                value=value or "",
                property_type=str(label),
            )
        except TypeError:
            node = PropertyNode(
                node_id=node_uuid,
                name=str(label),
                description=description or "",
            )
        node.attributes = {
            "sito": self._sito,
            "label": str(label),
            "dedup_key": dedup_key,
            "value": value or "",
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def list_documents(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "DocumentNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "label": attrs.get("label", "") or getattr(n, "name", ""),
                "dedup_key": attrs.get("dedup_key", ""),
            })
        return out

    def list_combiners(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "CombinerNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "label": attrs.get("label", "") or getattr(n, "name", ""),
                "dedup_key": attrs.get("dedup_key", ""),
            })
        return out

    def list_extractors(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "ExtractorNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "label": attrs.get("label", "") or getattr(n, "name", ""),
                "dedup_key": attrs.get("dedup_key", ""),
            })
        return out

    def list_properties(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "PropertyNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "label": attrs.get("label", "") or getattr(n, "name", ""),
                "value": attrs.get("value", ""),
                "dedup_key": attrs.get("dedup_key", ""),
            })
        return out
