"""Site-scoped CRUD for groups.graphml (atomic-safe writes).

AI06 Phase 2 / node grouping. Manages user-authored ad-hoc groups
that don't derive from any us_table column. SQL-derived groups
(struttura/area/attivita/settore/ambient/saggio/quad_par) are
materialized at export time by group_projector — they're NOT
persisted here.

File location: {db_path.parent}/groups_{sito_slug}.graphml
where sito_slug is `re.sub(r'\\W', '_', sito).lower()` (consistent
with AI05 paradata_store).

Atomic writes via .tmp + os.replace() — crash-safe.
Custom lxml serializer (s3dgraphy GraphMLExporter doesn't render
isolated ActivityNodeGroup instances without a stratigraphic
anchor — same constraint as AI05 paradata).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ._db_handle import _resolve_db_handle
from ._workspace import _resolve_workspace_dir
from .graph_ingestor import GraphSyncError


class GroupStoreError(GraphSyncError):
    """Base for GroupStore errors."""


class GroupReadError(GroupStoreError):
    """File parse / schema error during read()."""


class GroupWriteError(GroupStoreError):
    """File write / atomic-rename failure during write()."""


class GroupValidationError(GroupStoreError):
    """Caller passed bogus data to add_group/add_us_to_group/etc."""


class GroupNotFoundError(GroupStoreError):
    """Required file or group_uuid missing where caller expected it."""


# Meta-keys produced by s3dgraphy's GraphMLImporter that must NOT be
# round-tripped (same lesson as AI05 paradata).
_GROUP_HYDRATE_SKIP_KEYS: frozenset = frozenset({
    "original_id", "graph_id", "group_attrs",
})


# Type-name → background color mapping for the EM template. The
# importer's ``determine_group_node_type_by_color`` is what reconstructs
# the right GroupNode subclass on round-trip read, so the background
# color we emit is load-bearing — not cosmetic.
_GROUP_KIND_BACKGROUND_COLORS: dict = {
    "ActivityNodeGroup": "#CCFFFF",
    "ParadataNodeGroup": "#FFCC99",
    "TimeBranchNodeGroup": "#99CC00",
}


def _sito_slug(sito: str) -> str:
    """Filename-safe lowercase slug for a sito identifier (matches AI05)."""
    return re.sub(r"\W", "_", sito).strip("_").lower()


class GroupStore:
    """Site-scoped CRUD for groups.graphml."""

    def __init__(self, db_path, sito: str) -> None:
        """Construct a site-scoped group store.

        PG-D (5.7.3-alpha): ``db_path`` accepts ``Path | DbHandle | str``
        via the ``_resolve_db_handle`` shim from Foundation. Backward
        compat preserved for legacy callers passing a Path.
        """
        if not sito:
            raise GroupValidationError(
                "sito is required for GroupStore")
        self._handle = _resolve_db_handle(db_path)
        # Preserve self._db_path for any defensive code that reads it
        # directly. Same pattern as ParadataStore.
        self._db_path = (
            self._handle.sqlite_path
            if self._handle.sqlite_path is not None
            else Path(self._handle.conn_str)
        )
        self._sito = sito
        self._slug = _sito_slug(sito)

    @property
    def file_path(self) -> Path:
        """Resolved groups file path for this (db, sito) pair.

        PG-D (5.7.3-alpha): SQLite returns `<sqlite_parent>/groups_<sito>.graphml`
        (byte-identical to pre-PG-D). PG returns
        `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/groups_<sito>.graphml`.
        """
        return (
            _resolve_workspace_dir(self._handle, self._sito)
            / f"groups_{self._slug}.graphml"
        )

    def exists(self) -> bool:
        return self.file_path.exists()

    @property
    def sito(self) -> str:
        return self._sito

    # ---- Low-level ------------------------------------------------------
    def read(self):
        """Return a Graph populated only with ad-hoc group nodes from
        the file. Returns empty Graph when file absent."""
        from s3dgraphy import Graph
        if not self.exists():
            graph = Graph(graph_id=self._sito)
            # Defensive filter: drop the default GeoPositionNode
            graph.nodes = [
                n for n in graph.nodes
                if (getattr(n, "attributes", None) or {}).get("group_kind")
            ]
            return graph
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
            graph = GraphMLImporter(filepath=str(self.file_path)).parse()
        except Exception as e:
            raise GroupReadError(
                f"Cannot parse {self.file_path}: {e}") from e
        # Hydrate AI04 data keys + group_attrs JSON blob
        try:
            from .graph_ingestor import _hydrate_pyarchinit_data_keys
            _hydrate_pyarchinit_data_keys(graph, self.file_path)
        except Exception:
            pass
        try:
            self._hydrate_group_attrs(graph)
        except Exception:
            pass
        # Filter to nodes that carry a group_kind attribute
        graph.nodes = [
            n for n in graph.nodes
            if (getattr(n, "attributes", None) or {}).get("group_kind")
        ]
        return graph

    def _hydrate_group_attrs(self, graph) -> None:
        """Re-parse the file and merge `pyarchinit.group_attrs` JSON
        blob back onto each node's `.attributes` dict."""
        from lxml import etree as ET
        import json as _json
        NS = "http://graphml.graphdrawing.org/xmlns"
        try:
            tree = ET.parse(str(self.file_path))
        except Exception:
            return
        root = tree.getroot()
        attrs_kid = None
        for k in root.findall(f"{{{NS}}}key"):
            if k.get("attr.name") == "pyarchinit.group_attrs":
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
            for skip_key in _GROUP_HYDRATE_SKIP_KEYS:
                attrs.pop(skip_key, None)
            for k, v in blob.items():
                if k in _GROUP_HYDRATE_SKIP_KEYS:
                    continue
                if attrs.get(k) in (None, ""):
                    attrs[k] = v

    def write(self, graph) -> None:
        """Atomic write via .tmp + os.replace."""
        tmp = self.file_path.with_suffix(".graphml.tmp")
        try:
            self._write_minimal_graphml(graph, tmp)
            from .graphml_writer import _embed_pyarchinit_data_keys
            _embed_pyarchinit_data_keys(graph, tmp)
            os.replace(str(tmp), str(self.file_path))
        except Exception as e:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            raise GroupWriteError(
                f"Cannot write {self.file_path}: {e}") from e

    def _write_minimal_graphml(self, graph, out_path: Path) -> None:
        """Emit a minimal GraphML containing only the group nodes."""
        from lxml import etree as ET

        NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
        NS_Y = "http://www.yworks.com/xml/graphml"
        NSMAP = {None: NS_GRAPHML, "y": NS_Y}

        root = ET.Element(f"{{{NS_GRAPHML}}}graphml", nsmap=NSMAP)
        keys = [
            ("d0", "node", None, "url", "string"),
            ("d1", "node", None, "description", "string"),
            ("d2", "node", "nodegraphics", None, None),
            ("d3", "node", None, "EMID", "string"),
            ("d4", "node", None, "URI", "string"),
            ("d5", "node", None, "pyarchinit.group_attrs", "string"),
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
        graph_el.set("id", f"groups_{self._slug}")
        graph_el.set("edgedefault", "directed")

        for node in list(getattr(graph, "nodes", []) or []):
            attrs = getattr(node, "attributes", None) or {}
            if not attrs.get("group_kind"):
                continue
            self._emit_group_node(graph_el, node, NS_GRAPHML, NS_Y)

        tree = ET.ElementTree(root)
        tree.write(str(out_path), encoding="UTF-8",
                   xml_declaration=True, pretty_print=True)

    @staticmethod
    def _emit_group_node(graph_el, node, ns_graphml, ns_y):
        """Append a single group <node> with the EM canonical layout."""
        from lxml import etree as ET
        import json as _json

        node_id = str(getattr(node, "node_id", "") or "")
        display_name = str(getattr(node, "name", "") or "Group")
        type_name = type(node).__name__

        n_el = ET.SubElement(graph_el, f"{{{ns_graphml}}}node")
        n_el.set("id", node_id)
        # yfiles.foldertype="group" makes GraphMLImporter._check_node_type
        # classify this <node> as 'node_group' (otherwise it falls through
        # to 'node_simple' and gets dropped at parse time because we don't
        # emit a stratigraphic shape).
        n_el.set("yfiles.foldertype", "group")

        d_desc = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_desc.set("key", "d1")
        d_desc.text = f"_s3d_node_type:{type_name}"

        d_gfx = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_gfx.set("key", "d2")
        img = ET.SubElement(d_gfx, f"{{{ns_y}}}GroupNode")
        nl = ET.SubElement(img, f"{{{ns_y}}}NodeLabel")
        # backgroundColor="#CCFFFF" → determine_group_node_type_by_color
        # returns 'ActivityNodeGroup' on round-trip read.
        nl.set("backgroundColor", _GROUP_KIND_BACKGROUND_COLORS.get(
            type_name, "#CCFFFF"))
        nl.text = display_name

        d_emid = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_emid.set("key", "d3")
        d_emid.text = node_id

        attrs = getattr(node, "attributes", None) or {}
        if attrs:
            _SKIP = {"original_id", "graph_id", "group_attrs"}
            clean = {k: v for k, v in attrs.items()
                     if k not in _SKIP and v not in (None, "")}
            if clean:
                d_attrs = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
                d_attrs.set("key", "d5")
                d_attrs.text = _json.dumps(clean, ensure_ascii=False)

    def add_node(self, node) -> None:
        """Append *node* to the group graph + write."""
        attrs = getattr(node, "attributes", None) or {}
        if not attrs.get("group_kind"):
            raise GroupValidationError(
                "Refusing to store node without group_kind attribute")
        graph = self.read()
        graph.add_node(node)
        self.write(graph)

    def remove_node(self, group_uuid: str) -> None:
        """Idempotent — no error if uuid not found."""
        graph = self.read()
        before = len(graph.nodes)
        graph.nodes = [
            n for n in graph.nodes
            if getattr(n, "node_id", None) != group_uuid
        ]
        if len(graph.nodes) != before:
            self.write(graph)

    def find(self, group_kind: str = None, **kwargs) -> list:
        """Return matching group nodes."""
        out = []
        for n in self.read().nodes:
            attrs = getattr(n, "attributes", None) or {}
            if group_kind is not None and attrs.get("group_kind") != group_kind:
                continue
            if all(getattr(n, k, None) == v
                   or attrs.get(k) == v
                   for k, v in kwargs.items()):
                out.append(n)
        return out

    # ---- High-level (D6) -----------------------------------------------
    def add_group(
        self,
        name: str,
        group_kind: str = "adhoc",
        member_us_uuids: list = None,
        description: str = None,
    ) -> str:
        """Create + persist an ActivityNodeGroup. Returns uuid7."""
        if not name or not str(name).strip():
            raise GroupValidationError("Group name is required")
        if not group_kind:
            raise GroupValidationError("group_kind is required")
        from s3dgraphy.nodes.group_node import ActivityNodeGroup
        from .uuid7 import uuid7
        group_uuid = str(uuid7())
        members = list(member_us_uuids or [])
        node = ActivityNodeGroup(node_id=group_uuid, name=str(name))
        node.attributes = {
            "group_kind": str(group_kind),
            "sito": self._sito,
            "name": str(name),
            "member_us_uuids": ",".join(members),  # serialise as CSV
            "description": str(description or ""),
            "group_uuid": group_uuid,
        }
        self.add_node(node)
        return group_uuid

    def list_groups(self) -> list:
        """Return [{group_uuid, name, group_kind, member_us_uuids, description}]."""
        out = []
        for n in self.read().nodes:
            attrs = getattr(n, "attributes", None) or {}
            members_csv = str(attrs.get("member_us_uuids", "") or "")
            members = [m for m in members_csv.split(",") if m]
            out.append({
                "group_uuid": getattr(n, "node_id", ""),
                "name": (attrs.get("name", "")
                         or getattr(n, "name", "")),
                "group_kind": attrs.get("group_kind", ""),
                "member_us_uuids": members,
                "description": attrs.get("description", ""),
            })
        return out

    def remove_group(self, group_uuid: str) -> None:
        """Alias for remove_node — high-level naming."""
        self.remove_node(group_uuid)

    def add_us_to_group(self, group_uuid: str, us_uuid: str) -> None:
        """Append us_uuid to the group's member list. Idempotent on
        duplicate. Raises GroupNotFoundError if group_uuid unknown."""
        if not us_uuid:
            raise GroupValidationError("us_uuid required")
        graph = self.read()
        target = next((n for n in graph.nodes
                       if getattr(n, "node_id", None) == group_uuid), None)
        if target is None:
            raise GroupNotFoundError(f"Group {group_uuid} not found")
        attrs = getattr(target, "attributes", None) or {}
        members_csv = str(attrs.get("member_us_uuids", "") or "")
        members = [m for m in members_csv.split(",") if m]
        if us_uuid in members:
            return  # idempotent
        members.append(us_uuid)
        attrs["member_us_uuids"] = ",".join(members)
        target.attributes = attrs
        self.write(graph)

    def remove_us_from_group(self, group_uuid: str, us_uuid: str) -> None:
        """Idempotent — no error if us_uuid not in member list."""
        graph = self.read()
        target = next((n for n in graph.nodes
                       if getattr(n, "node_id", None) == group_uuid), None)
        if target is None:
            return  # idempotent on missing group too
        attrs = getattr(target, "attributes", None) or {}
        members_csv = str(attrs.get("member_us_uuids", "") or "")
        members = [m for m in members_csv.split(",") if m]
        if us_uuid not in members:
            return
        members.remove(us_uuid)
        attrs["member_us_uuids"] = ",".join(members)
        target.attributes = attrs
        self.write(graph)

    def list_members(self, group_uuid: str) -> list:
        """Return the list of us_uuid strings of a group."""
        for n in self.read().nodes:
            if getattr(n, "node_id", None) == group_uuid:
                attrs = getattr(n, "attributes", None) or {}
                csv = str(attrs.get("member_us_uuids", "") or "")
                return [m for m in csv.split(",") if m]
        return []
