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
    back. Returns (path, n_nodes, n_edges, warnings).

    The graph travels through the plugin's GraphProjector — NOT the raw
    importer: the dev40 mapping has no `relations` yet (s3Dgraphy#26),
    so only the projector's passes give the file the stratigraphic
    edges the matrix lives on (C1, final review 2026-10-07). Every
    failure on the way is worded for the user as EmExportError.
    """
    if not emjson_available():
        raise EmExportError(
            "La libreria s3dgraphy installata non conosce em.json: "
            "aggiorna le dipendenze del plugin.")
    from s3dgraphy.exporter.emjson_exporter import export_emjson
    from s3dgraphy.importer.emjson_importer import import_emjson
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode

    from .sync.graph_projector import GraphProjector

    try:
        graph = GraphProjector().populate_graph(connection_url, sito=site)
    except Exception as e:
        raise EmExportError(
            "Lettura del sito %r fallita: %s" % (site, e)) from e
    strat = [n for n in getattr(graph, "nodes", []) or []
             if isinstance(n, StratigraphicNode)]
    if not strat:
        raise EmExportError(
            "Il sito %r non ha righe in us_table: niente da esportare." % site)
    graph.graph_id = str(site)
    warnings = [str(w) for w in (getattr(graph, "warnings", None) or [])]

    # The emjson exporter lifts node.attributes into data{} but does not
    # serialise a group's `kind` of its own (upstream gap, s3Dgraphy#25
    # follow-up): without this mirror the toponym chain comes back as
    # "constructor failed ... kind must be one of" and degrades to Node.
    for n in graph.nodes:
        k = getattr(n, "kind", None)
        if k is not None and hasattr(n, "attributes"):
            if n.attributes is None:
                n.attributes = {}
            n.attributes.setdefault("kind", k)

    try:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, site_filename(site))
        export_emjson(graph, path)
    except Exception as e:
        raise EmExportError(
            "Scrittura di %s fallita: %s" % (site_filename(site), e)) from e

    try:
        check, read_warnings = import_emjson(path)
    except Exception as e:
        raise EmExportError(
            "Il file scritto non si rilegge: %s" % e) from e
    if (len(check.nodes), len(check.edges)) != (len(graph.nodes), len(graph.edges)):
        raise EmExportError(
            "Il file scritto non rilegge uguale (%d/%d nodi, %d/%d archi)."
            % (len(check.nodes), len(graph.nodes),
               len(check.edges), len(graph.edges)))
    warnings.extend(str(w) for w in read_warnings)
    return path, len(graph.nodes), len(graph.edges), warnings


def open_in_emstudio(path, runner=None):
    """Hand the file to EMStudio; True when something opened, False —
    never an exception — when nothing is installed (the caller then
    points at the EMStudio releases page)."""
    import platform
    import subprocess
    run = runner or subprocess.run
    system = platform.system()
    try:
        if system == "Darwin":
            return run(["open", "-a", "EMStudio", path],
                       capture_output=True).returncode == 0
        if system == "Windows":
            os.startfile(path)      # l'associazione .em.json decide
            return True
        return run(["xdg-open", path], capture_output=True).returncode == 0
    except Exception:
        return False
