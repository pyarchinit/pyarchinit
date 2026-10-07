"""Export a site to em.json, the working format of the Extended Matrix.

GraphML stays only as the one-time import from yEd (spec 2026-10-07):
the matrix a user looks at lives in EMStudio, which opens em.json
natively. The graph is built by the library's own DB->graph path
(PyArchInitImporter + pyarchinit_us_mapping), named after the site,
and read back before being handed over: a file that does not read
back clean is not given to the user.

Pure Python: no Qt. The menu wiring lives in pyarchinitPlugin.
"""
from __future__ import annotations

import os
import re


class EmExportError(RuntimeError):
    """A reason the export could not be done, worded for the user."""


def emjson_available():
    """True when the installed s3dgraphy knows em.json (>= 1.6.0.dev40)."""
    try:
        from s3dgraphy.exporter import emjson_exporter  # noqa: F401
        return True
    except Exception:
        return False


def site_filename(site):
    """A filename the site name can travel in: word characters of any
    script, dash and dot survive; runs of anything else become one '_'."""
    name = re.sub(r"[^\w\-.]+", "_", str(site), flags=re.UNICODE).strip("_.")
    return (name or "sito") + ".em.json"


def export_site(connection_url, site, out_dir):
    """Build the site's graph, write <out_dir>/<site>.em.json, read it
    back. Returns (path, n_nodes, n_edges, warnings)."""
    if not emjson_available():
        raise EmExportError(
            "La libreria s3dgraphy installata non conosce em.json: "
            "aggiorna le dipendenze del plugin.")
    from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
    from s3dgraphy.exporter.emjson_exporter import export_emjson
    from s3dgraphy.importer.emjson_importer import import_emjson

    graph = PyArchInitImporter(
        connection_url=connection_url,
        mapping_name="pyarchinit_us_mapping",
        filters={"sito": site},
    ).parse()
    # dev40 scaffolds a graph-root and geo node even for an unknown site:
    # "empty" means no stratigraphic rows travelled, not no nodes at all.
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
    if not any(isinstance(n, StratigraphicNode)
               for n in getattr(graph, "nodes", []) or []):
        raise EmExportError(
            "Il sito %r non ha righe in us_table: niente da esportare." % site)
    graph.graph_id = str(site)

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, site_filename(site))
    export_emjson(graph, path)

    check, warnings = import_emjson(path)
    if (len(check.nodes), len(check.edges)) != (len(graph.nodes), len(graph.edges)):
        raise EmExportError(
            "Il file scritto non rilegge uguale (%d/%d nodi, %d/%d archi)."
            % (len(check.nodes), len(graph.nodes),
               len(check.edges), len(graph.edges)))
    return path, len(graph.nodes), len(graph.edges), list(warnings)
