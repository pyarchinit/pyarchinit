"""Test fabric for pyarchinit-projected GraphML files.

The writer retired with A4 (spec 2026-10-07, decision 2): em.json is the
working format and EMStudio the viewer. Projected GraphML files already
IN THE WILD still reach the one-time import path, so the import tests
fabricate them here: the library's GraphMLExporter writes the file and
``embed_pyarchinit_data_keys`` (moved verbatim from the retired
``graphml_writer._embed_pyarchinit_data_keys``) adds the ``pyarchinit.*``
<key>/<data> entries ``detect_flavor()`` and the ingestor read.
"""
from __future__ import annotations

from pathlib import Path

_PYARCHINIT_NODE_DATA_KEYS = (
    ("us", "pyarchinit.us"),
    ("area", "pyarchinit.area"),
    ("sito", "pyarchinit.sito"),
    ("unita_tipo", "pyarchinit.unita_tipo"),
    ("periodo_iniziale", "pyarchinit.periodo_iniziale"),
    ("fase_iniziale", "pyarchinit.fase_iniziale"),
    ("rapporti", "pyarchinit.rapporti"),
    ("d_stratigrafica", "pyarchinit.d_stratigrafica"),
    # AI08-F2 hotfix: also expose the interpretative description per US
    ("d_interpretativa", "pyarchinit.d_interpretativa"),
    ("documentazione", "pyarchinit.documentazione"),  # DOC URL/path
    # AI06: persist DB node_uuid so round-trip via GraphMLImporter
    # (which generates a fresh internal node_id) can still identify
    # the original us_table row for UPDATE selettivo.
    ("node_uuid", "pyarchinit.node_uuid"),
    # AI06 D.2: register the SQL-derived group_kind columns so
    # _inject_group_folders can emit a pyarchinit.<kind> data entry
    # on each group folder. The round-trip importer
    # (sql_apply_groups=True) reads these to discover which us_table
    # column to UPDATE.
    ("struttura", "pyarchinit.struttura"),
    ("attivita", "pyarchinit.attivita"),
    ("settore", "pyarchinit.settore"),
    ("ambient", "pyarchinit.ambient"),
    ("saggio", "pyarchinit.saggio"),
    ("quad_par", "pyarchinit.quad_par"),
    # AI08-F2 hotfix: per-US datazione_estesa resolved from
    # periodizzazione_table by (sito, periodo_iniziale, fase_iniziale).
    ("datazione_estesa", "pyarchinit.datazione_estesa"),
)

_PYARCHINIT_EPOCH_DATA_KEYS = (
    ("periodo", "pyarchinit.periodo"),
    ("fase", "pyarchinit.fase"),
    ("cron_iniziale", "pyarchinit.cron_iniziale"),
    ("cron_finale", "pyarchinit.cron_finale"),
    ("datazione_estesa", "pyarchinit.datazione_estesa"),
)

def _embed_pyarchinit_data_keys(graph, xml_path: Path) -> None:
    """Append custom <data> entries on each <node> in the produced
    GraphML so AI04's import path can recover the pyarchinit columns
    that s3dgraphy's GraphMLImporter would otherwise strip.

    Each attribute gets its own <key for="node" attr.name="…"/> at
    the document level, plus a per-node <data key="…">value</data>.
    """
    try:
        from lxml import etree
    except ImportError:
        return

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # Build EMID → graph node lookup so we can pull attributes per node.
    emid_to_node = {}
    for n in graph.nodes:
        emid = getattr(n, "node_id", None)
        if emid:
            emid_to_node[emid] = n

    # Allocate fresh data-key ids that don't collide.
    used_ids = {k.get("id") for k in root.findall(f"{{{NS_GRAPHML}}}key")
                if k.get("id")}
    next_n = 0
    def _alloc_id() -> str:
        nonlocal next_n
        while f"d{next_n}" in used_ids:
            next_n += 1
        kid = f"d{next_n}"
        used_ids.add(kid)
        next_n += 1
        return kid

    # Register node-level keys
    node_attrname_to_keyid: dict[str, str] = {}
    for attr_name, attr_named in _PYARCHINIT_NODE_DATA_KEYS:
        kid = _alloc_id()
        node_attrname_to_keyid[attr_name] = kid
        key_el = etree.Element(f"{{{NS_GRAPHML}}}key")
        key_el.set("for", "node")
        key_el.set("id", kid)
        key_el.set("attr.name", attr_named)
        key_el.set("attr.type", "string")
        # Insert after existing keys
        existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
        if existing_keys:
            existing_keys[-1].addnext(key_el)
        else:
            root.insert(0, key_el)

    # Register epoch-level keys (we'll write them on EpochNode shapes;
    # those are inside <y:Row> in the swimlane TableNode, but s3dgraphy
    # also emits them as separate <node> entries — we put data on both
    # via the same key set, applied conditionally below).
    epoch_attrname_to_keyid: dict[str, str] = {}
    for attr_name, attr_named in _PYARCHINIT_EPOCH_DATA_KEYS:
        kid = _alloc_id()
        epoch_attrname_to_keyid[attr_name] = kid
        key_el = etree.Element(f"{{{NS_GRAPHML}}}key")
        key_el.set("for", "node")
        key_el.set("id", kid)
        key_el.set("attr.name", attr_named)
        key_el.set("attr.type", "string")
        existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
        if existing_keys:
            existing_keys[-1].addnext(key_el)
        else:
            root.insert(0, key_el)

    # ---- Epoch metadata block (#5 H.4 fix) ----
    # EpochNodes don't appear as separate <node> elements in s3dgraphy
    # output (they live inside the swimlane <y:TableNode>'s <y:Row>),
    # so per-node data keys can't reach them. Instead embed a single
    # JSON blob on the <graph> element listing every EpochNode's
    # periodo/fase/cron metadata, indexed by name. The AI04 hydrator
    # reads this and propagates back to graph.nodes by name match.
    import json as _json
    epoch_meta = []
    for n in graph.nodes:
        if type(n).__name__ != "EpochNode":
            continue
        nattrs = getattr(n, "attributes", None) or {}
        meta = {"name": getattr(n, "name", "")}
        for key in ("periodo", "fase", "cron_iniziale",
                    "cron_finale", "datazione_estesa"):
            if nattrs.get(key) is not None:
                meta[key] = str(nattrs[key])
        if getattr(n, "start_time", None) not in (None, 0, 0.0):
            meta.setdefault("cron_iniziale", str(int(n.start_time)))
        if getattr(n, "end_time", None) not in (None, 0, 0.0):
            meta.setdefault("cron_finale", str(int(n.end_time)))
        if len(meta) > 1:
            epoch_meta.append(meta)
    if epoch_meta:
        epochs_kid = _alloc_id()
        ekey_el = etree.Element(f"{{{NS_GRAPHML}}}key")
        ekey_el.set("for", "graph")
        ekey_el.set("id", epochs_kid)
        ekey_el.set("attr.name", "pyarchinit.epochs_meta")
        ekey_el.set("attr.type", "string")
        existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
        if existing_keys:
            existing_keys[-1].addnext(ekey_el)
        else:
            root.insert(0, ekey_el)
        # Find the top-level <graph> child to attach the data blob to
        graph_el = root.find(f"{{{NS_GRAPHML}}}graph")
        if graph_el is not None:
            ed = etree.SubElement(graph_el, f"{{{NS_GRAPHML}}}data")
            ed.set("key", epochs_kid)
            ed.text = _json.dumps(epoch_meta)

    # Walk every <node>, look up its EMID in emid_to_node, attach the
    # corresponding pyarchinit data values when present.
    known_emids = set(emid_to_node.keys())
    for node_el in root.iter(f"{{{NS_GRAPHML}}}node"):
        emid = None
        for d_el in node_el.findall(f"{{{NS_GRAPHML}}}data"):
            txt = (d_el.text or "").strip()
            if txt and txt in known_emids:
                emid = txt
                break
        if emid is None:
            continue
        n = emid_to_node[emid]
        attrs = getattr(n, "attributes", None) or {}
        # Choose the right attr-set based on node type
        is_epoch = type(n).__name__ == "EpochNode"
        if is_epoch:
            attrname_to_kid = epoch_attrname_to_keyid
            # Auto-derive periodo/fase from EpochNode.node_id when not
            # already in attrs (so our import side sees them).
            import re as _re_local
            tid = getattr(n, "node_id", "") or ""
            m = _re_local.match(
                r"^epoch_([^_]+)_(.+?)(_synthetic)?$", str(tid))
            if m:
                attrs = dict(attrs)
                attrs.setdefault("periodo", m.group(1))
                attrs.setdefault("fase", m.group(2))
            cron_ini = getattr(n, "start_time", None)
            cron_fin = getattr(n, "end_time", None)
            if cron_ini not in (None, 0, 0.0):
                attrs.setdefault("cron_iniziale", str(int(cron_ini)))
            if cron_fin not in (None, 0, 0.0):
                attrs.setdefault("cron_finale", str(int(cron_fin)))
            datazione = attrs.get("datazione_estesa") or getattr(n, "name", "")
            if datazione:
                attrs.setdefault("datazione_estesa", str(datazione))
        else:
            attrname_to_kid = node_attrname_to_keyid
            # DocumentNode: copy `url` field into a documentazione
            # attribute so the data-key emitter picks it up. AI04.1 #6.
            if type(n).__name__ == "DocumentNode":
                doc_url = (getattr(n, "url", None)
                           or attrs.get("url"))
                if doc_url and not attrs.get("documentazione"):
                    attrs = dict(attrs)
                    attrs["documentazione"] = str(doc_url)
        for attr_name, kid in attrname_to_kid.items():
            val = attrs.get(attr_name)
            if val is None or val == "":
                continue
            d = etree.SubElement(node_el, f"{{{NS_GRAPHML}}}data")
            d.set("key", kid)
            d.text = str(val)

    tree.write(str(xml_path), encoding="UTF-8", xml_declaration=True)


# Public spelling for the tests; the underscore original stays callable.
embed_pyarchinit_data_keys = _embed_pyarchinit_data_keys


def export_projected(db_path, sito, out_path, graph=None, groups=None):
    """GraphProjector -> library GraphMLExporter -> embedded data keys:
    a pyarchinit-projected file as the wild ones the import path reads."""
    from s3dgraphy.exporter.graphml.graphml_exporter import GraphMLExporter

    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    if graph is None:
        kw = {"groups": groups} if groups else {}
        graph = GraphProjector().populate_graph(db_path, sito=sito, **kw)
    GraphMLExporter(graph).export(str(out_path), persist_auxiliary=False)
    _embed_pyarchinit_data_keys(graph, Path(out_path))
    return graph
