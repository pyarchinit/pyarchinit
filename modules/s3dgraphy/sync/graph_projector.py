"""pyArchInit's projector: the library's, plus the host's own passes.

One bridge (A2, spec 2026-10-07): the DB→graph projection is the
library's ``s3dgraphy.sync.graph_projector`` — written for the dev40
importer, whose nodes carry uuid7 ids and the composite label
(``1.US1``). What stays here is only what belongs to pyArchInit:

- the paradata edge refinement (``paradata_edge_resolver``, a
  pyArchInit module): generic_connection edges between paradata and
  stratigraphy get their EM type back;
- the chronology warning (``modules.utility.periodization_checks``,
  host code the library must not import): periods whose start is later
  than their end are reported on ``graph.warnings``.

Everything else re-exports the library, names the tests and the
GraphML writer consume included.
"""
from __future__ import annotations

import contextlib
import logging
import threading

from s3dgraphy.sync.graph_projector import *  # noqa: F401,F403
from s3dgraphy.sync.graph_projector import (  # noqa: F401  (private, used by tests)
    GraphProjector as _LibGraphProjector,
    ProjectionError,
    _create_paradata_node_for_unita_tipo,
    _create_stratigraphic_node_for_unita_tipo,
    _resolve_target_for_folder,
)


#: EM paradata serialised into us_table rows. Bug P (2026-05-15): they
#: project as StratigraphicUnit with the identity in
#: ``attributes['unita_tipo']`` — the writer dispatches shape by value,
#: and the swimlane keeps them beside their stratigraphy.
_PARADATA_UNITA_TIPO = ("DOC", "Combinar", "Extractor", "property")

#: The stratigraphic family us_table rows can carry (canonical codes).
_STRAT_FAMILY = ("US", "USM", "USR", "USD", "USV", "USVs", "USVn", "USVc",
                 "SF", "VSF", "RSF", "CON")


_MISSING = object()

#: The codes pyArchInit used for virtual units, with the reading its own
#: historical exporter gave them (resources/dbfiles/dot.py:855-865): USVA
#: a parallelogram = structural, USVB a hexagon = non-structural, USVC an
#: ellipse (a series) = folded onto non-structural. The library does not
#: know them — ``canonical_unita_tipo`` hands them back unchanged — so a
#: virtual unit came out as a plain US. Same table as
#: scripts/migrations/_2026_05_us_vocabulary_alignment_lib.REPLACEMENTS and
#: room/us_ops.UNIT_TYPES; a test per file keeps the three in step.
LEGACY_UNITA_TIPO = {
    "USVA": "USVs", "USVB": "USVn", "USVC": "USVn", "USVc": "USVn",
}

#: Codes whose class the library files under another name: pyArchInit's
#: continuity (CON) is the ContinuityNode, which the library calls BR.
_CLASS_KEY_ALIAS = {"CON": "BR"}

#: The fields that belong to the node, not to its class: a node that
#: changes class keeps them.
_IDENTITY_FIELDS = ("node_id", "name", "description", "attributes", "data")

#: What the new class would have set in __init__ and must be refreshed,
#: because the old class had already set it to something non-None.
_PRESENTATION_FIELDS = ("symbol", "label", "detailed_description")


def _class_key_for_unita_tipo(declared):
    """The STRATIGRAPHIC_CLASS_MAP key ``declared`` names, or None.

    Order matters: pyArchInit's legacy codes first, then the library's
    canonicalisation (which folds UE/SU/SE/ΣΜ onto US and the masonry
    codes onto USM), then the name aliases. The other way round — reading
    the raw code — 'SE', which in pyArchInit is the German for US, would
    land on StratigraphicEventNode and turn a whole site into events.
    """
    code = str(declared or "").strip()
    if not code:
        return None
    code = LEGACY_UNITA_TIPO.get(code, code)
    try:
        from s3dgraphy.rapporti import canonical_unita_tipo
        code = canonical_unita_tipo(code) or code
    except Exception:                               # noqa: BLE001
        pass
    return _CLASS_KEY_ALIAS.get(code, code)


#: What pyArchInit writes in a list column that nobody filled in.
_EMPTY_PROPERTY_VALUES = ("", "[]", "[[]]", "{}", "none", "null")


def _drop_empty_property_nodes(graph):
    """Drop the property nodes that say nothing, and their edges.

    A pyArchInit list column left empty holds the string ``"[]"``, which
    upstream reads as a value worth a node: 30 of the demo site's 219
    property nodes carried it. Nodes that come from a us_table row
    (``attributes['us']``) are the user's own data and are never swept,
    whatever their value.
    """
    doomed = {
        n.node_id for n in graph.nodes
        if getattr(n, "node_type", None) == "property"
        and not (getattr(n, "attributes", None) or {}).get("us")
        and str(getattr(n, "value", "") or "").strip().lower()
        in _EMPTY_PROPERTY_VALUES}
    if not doomed:
        return 0
    graph.nodes = [n for n in graph.nodes if n.node_id not in doomed]
    graph.edges = [e for e in graph.edges
                   if e.edge_source not in doomed
                   and e.edge_target not in doomed]
    if hasattr(graph, "invalidate_indices"):
        graph.invalidate_indices()
    return len(doomed)


#: I node_type che l'Extended Matrix considera paradati.
_PARADATA_NODE_TYPES = ("property", "document", "extractor", "combiner")

#: Gli archi con cui una unità appende a sé i propri paradati.
_PARADATA_EDGE_TYPES = ("has_property", "has_documentation", "has_author")


def _drop_paradata_of_paradata(graph, paradata_ids):
    """Toglie i paradati nati dalle colonne di una riga che è un paradato.

    Una riga di us_table che l'EM legge come paradato (property, DOC,
    Extractor, Combinar) riceve dall'importer gli stessi nodi di
    contorno di una unità — «Interpretation», la documentazione, gli
    autori. Una volta che la riga prende la sua classe quei nodi
    diventano paradati di un paradato, e il datamodel di EMStudio lo
    segnala («has_property is not allowed towards a property»,
    misurato il 2026-10-08).
    """
    doomed_edges = [e for e in graph.edges
                    if e.edge_source in paradata_ids
                    and e.edge_type in _PARADATA_EDGE_TYPES]
    if not doomed_edges:
        return 0
    orphan_candidates = {e.edge_target for e in doomed_edges}
    survivors = [e for e in graph.edges if e not in doomed_edges]
    still_touched = {e.edge_source for e in survivors}
    still_touched |= {e.edge_target for e in survivors}
    doomed_nodes = {n.node_id for n in graph.nodes
                    if n.node_id in orphan_candidates
                    and n.node_id not in still_touched
                    and getattr(n, "node_type", None) in _PARADATA_NODE_TYPES}
    graph.edges = survivors
    if doomed_nodes:
        graph.nodes = [n for n in graph.nodes
                       if n.node_id not in doomed_nodes]
    if hasattr(graph, "invalidate_indices"):
        graph.invalidate_indices()
    return len(doomed_edges)


def _paradata_class_of(declared):
    """The paradata class ``declared`` names, or None.

    pyArchInit keeps in us_table rows that the Extended Matrix reads as
    paradata (the yEd round-trip's legacy, Bug P 2026-05-15). While the
    GraphML writer existed they stayed StratigraphicUnit and it picked
    their shape from ``attributes['unita_tipo']``; em.json picks it from
    ``node_type``, so they came out as US.
    """
    code = str(declared or "").strip()
    if code not in _PARADATA_UNITA_TIPO:
        return None
    from s3dgraphy.nodes.combiner_node import CombinerNode
    from s3dgraphy.nodes.document_node import DocumentNode
    from s3dgraphy.nodes.extractor_node import ExtractorNode
    from s3dgraphy.nodes.property_node import PropertyNode
    return {"property": PropertyNode, "DOC": DocumentNode,
            "Extractor": ExtractorNode, "Combinar": CombinerNode}.get(code)


def _become(node, target_cls):
    """``node`` becomes a ``target_cls``, keeping its identity and edges.

    Reassigning ``__class__`` is legal on instances of plain Python
    classes and skips ``__init__``: the fields the new class would have
    set are copied from a throwaway probe, everything else stays the
    node's. Replacing the node in the graph instead would mean surgery
    on its lists and indices — and ``add_node(overwrite=True)`` leaves a
    warning per node on ``graph.warnings``, which the export shows the
    user.
    """
    probe = target_cls(node_id="_probe", name="_probe")
    node.__class__ = target_cls
    # Node.__init__ copies the class attribute onto the instance
    # (base_node.py:61), and the stale copy would win over the new class.
    node.node_type = target_cls.node_type
    for field in _PRESENTATION_FIELDS:
        if hasattr(probe, field):
            setattr(node, field, getattr(probe, field))
    for field, value in vars(probe).items():
        if field in _IDENTITY_FIELDS or field in _PRESENTATION_FIELDS:
            continue
        if getattr(node, field, _MISSING) in (_MISSING, None):
            setattr(node, field, value)
    return node


#: The patch below swaps a module symbol: two projections at once (one in
#: a QgsTask, one on the GUI thread) would read each other's site. The lock
#: serialises the swap and the projection, which takes tenths of a second.
_IMPORTER_PATCH_LOCK = threading.RLock()


@contextlib.contextmanager
def _site_filtered_importer(sito):
    """Make the library's SQLite importer read only ``sito``'s rows.

    dev40 builds ``PyArchInitImporter`` with no ``filters``, so the
    SQLite path parses the WHOLE us_table. In a multi-site DB the other
    sites' rows arrive too and — because the node label carries no site
    (``{area}.{settore}.{unita_tipo}{us}``) — two sites that number
    their units alike collapse onto ONE node, which then holds both
    sites' documentation, properties and epochs. Measured on the sample
    DB (2026-10-08): 210 units / 342 documents / 132 epochs without the
    filter, 51 / 87 / 24 with it. The PostgreSQL path already passes the
    site (``import_from_pg``), so only SQLite needs this. Upstream
    candidate: s3Dgraphy#25.
    """
    import s3dgraphy.importer.pyarchinit_importer as mod

    with _IMPORTER_PATCH_LOCK:
        original = mod.PyArchInitImporter

        class _SiteFiltered(original):
            def __init__(self, *args, **kwargs):
                if not kwargs.get("filters"):
                    kwargs["filters"] = {"sito": sito}
                super().__init__(*args, **kwargs)

        mod.PyArchInitImporter = _SiteFiltered
        try:
            yield
        finally:
            mod.PyArchInitImporter = original


class GraphProjector(_LibGraphProjector):
    """The library's projector with pyArchInit's closing passes."""

    def populate_graph(self, db_path, sito, **kwargs):
        with _site_filtered_importer(sito):
            graph = super().populate_graph(db_path, sito, **kwargs)

        # pyArchInit's flat attributes (us / sito / unita_tipo / ...):
        # the round-trip ingestor, the d13 serialiser and the writers
        # key off them; the dev40 library keeps this data as qualia
        # instead, so writing them is host business now.
        try:
            self._apply_pyarchinit_attributes(graph, db_path, sito)
        except Exception as e:                      # noqa: BLE001
            raise ProjectionError(
                "pyArchInit attribute propagation failed for sito=%r: %s"
                % (sito, e)) from e

        # One site per projection: on SQLite the library importer reads
        # the WHOLE us_table and its post-filter keeps every dev40 node
        # (they carry no attributes['sito']). What the attribute pass
        # did not claim belongs to another site — prune it, with the
        # decoration that only served it (I1, final review 2026-10-07;
        # upstream candidate: filters={'sito': ...} on the importer).
        self._prune_foreign_site_nodes(graph, sito)

        # One epoch per (periodo, fase), named the way pyArchInit names
        # periods: the importer and the library projector each create
        # their own epoch nodes (upstream double, s3Dgraphy#27 follow-up)
        # and the library's names stop at descrizione.
        try:
            self._fix_epochs(graph, db_path, sito)
        except Exception as e:                      # noqa: BLE001
            raise ProjectionError(
                "epoch naming failed for sito=%r: %s" % (sito, e)) from e

        # pyArchInit's rapporti column -> stratigraphic edges: the dev40
        # mapping has no `relations` yet (s3Dgraphy#26), so the edges the
        # matrix lives on are built here, from the attributes just written.
        try:
            self._build_rapporti_edges(graph)
        except Exception as e:                      # noqa: BLE001
            raise ProjectionError(
                "rapporti edge building failed for sito=%r: %s"
                % (sito, e)) from e

        # Every node the class its unita_tipo declares: node_type is what
        # em.json writes and EMStudio reads to choose the shape.
        try:
            self._retype_nodes_from_unita_tipo(graph)
        except Exception as e:                      # noqa: BLE001
            raise ProjectionError(
                "node retyping failed for sito=%r: %s" % (sito, e)) from e

        # A column nobody filled in is not a paradatum.
        try:
            _drop_empty_property_nodes(graph)
        except Exception:                           # noqa: BLE001
            pass                                    # hygiene, never a failure

        # EM typing of generic paradata→stratigraphy connections.
        try:
            from .paradata_edge_resolver import refine_generic_connections
            n_retyped = refine_generic_connections(graph)
            if n_retyped:
                logging.getLogger(__name__).info(
                    "paradata edge refinement: retyped %d "
                    "generic_connection edge(s)", n_retyped)
        except Exception as e:                      # noqa: BLE001
            logging.getLogger(__name__).warning(
                "paradata edge refinement skipped: %s", e)

        # Chronologies written backwards (BC years without the minus):
        # the warning of v4.9.13, host-side because it imports
        # modules.utility.
        try:
            self._warn_suspicious_chronologies(graph, db_path)
        except Exception:                           # noqa: BLE001
            pass                                    # a warning, never a failure
        return graph

    @staticmethod
    def _prune_foreign_site_nodes(graph, sito):
        from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
        drop = {n.node_id for n in graph.nodes
                if isinstance(n, StratigraphicNode)
                and (getattr(n, "attributes", None) or {}).get("sito") != sito}
        # Le epoche degli ALTRI siti non muoiono da orfane: tengono archi
        # fra sé e le proprie date (misurato da Enzo sul demo: 57 epoche
        # in dieci lingue nel file di un sito solo). L'importer le firma
        # per sito — epoch::sito::p::f — quindi si potano per nome.
        for n in graph.nodes:
            nid = str(getattr(n, "node_id", ""))
            if (type(n).__name__ == "EpochNode" and nid.startswith("epoch::")
                    and nid.split("::")[1] != str(sito)):
                drop.add(n.node_id)
        if not drop:
            return
        graph.nodes = [n for n in graph.nodes if n.node_id not in drop]
        graph.edges = [e for e in graph.edges
                       if e.edge_source not in drop
                       and e.edge_target not in drop]
        # Decoration that only served the dropped nodes: a property, an
        # epoch or a date left with no edge at all is another site's.
        # A FIXPOINT, not one pass: the dates orphaned by a dropped epoch
        # can orphan something else in turn.
        prunable = ("PropertyNode", "EpochNode", "LocationNodeGroup",
                    "ActivityNodeGroup", "DocumentNode", "AuthorNode")
        while True:
            referenced = set()
            for e in graph.edges:
                referenced.add(e.edge_source)
                referenced.add(e.edge_target)
            orphans = {n.node_id for n in graph.nodes
                       if type(n).__name__ in prunable
                       and n.node_id not in referenced}
            if not orphans:
                break
            graph.nodes = [n for n in graph.nodes
                           if n.node_id not in orphans]
            graph.edges = [e for e in graph.edges
                           if e.edge_source not in orphans
                           and e.edge_target not in orphans]
        if hasattr(graph, "invalidate_indices"):
            graph.invalidate_indices()

    @staticmethod
    def _retype_nodes_from_unita_tipo(graph):
        """Give every node the class its ``unita_tipo`` declares.

        ``node_type`` is a CLASS attribute: it is what em.json writes and
        what EMStudio reads to pick the shape. The importer builds every
        us_table row as a ``StratigraphicUnit`` and keeps the genre
        aside (``apply_legacy_kind``), so a virtual unit, a special find
        or a continuity all came out as a US with a white rectangle —
        seen by Enzo on the demo, 2026-10-08.

        Returns the count per resulting node_type.
        """
        from s3dgraphy.utils.utils import get_stratigraphic_node_class

        counts = {}
        became_paradata = set()
        for node in list(graph.nodes):
            declared = (getattr(node, "attributes", None) or {}).get(
                "unita_tipo")
            target = _paradata_class_of(declared)
            if target is None:
                key = _class_key_for_unita_tipo(declared)
                if not key:
                    continue
                target = get_stratigraphic_node_class(key)
            if target is None or type(node) is target:
                continue
            node_type = getattr(target, "node_type", None)
            if node_type in (None, "StratigraphicNode"):
                continue                 # abstract, or a node with no type
            _become(node, target)
            if node_type in _PARADATA_NODE_TYPES:
                became_paradata.add(node.node_id)
            counts[node_type] = counts.get(node_type, 0) + 1
        if became_paradata:
            _drop_paradata_of_paradata(graph, became_paradata)
        return counts

    @staticmethod
    def _apply_pyarchinit_attributes(graph, db_path, sito):
        """Write each us_table row's columns onto its node.

        Nodes are matched by ``node_uuid`` first (the dev40 importer's
        node_id IS the row's node_uuid), then by name (the composite
        ``area.unita_tipoUS`` label or the bare us), each node claimed
        by at most one row; a row with no node left (the importer
        skipped it, or two rows share a name) is back-filled — paradata
        rows included, per Bug P. Epochs get the period's
        ``datazione_estesa`` as their name, the label pyArchInit shows.
        """
        from sqlalchemy import text

        from s3dgraphy.rapporti import canonical_unita_tipo
        from s3dgraphy.sync._db_handle import _resolve_db_handle

        handle = _resolve_db_handle(db_path)
        with handle.engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT us, node_uuid, sito, area, unita_tipo, "
                "periodo_iniziale, fase_iniziale, rapporti, "
                "d_stratigrafica, d_interpretativa, attivita, struttura, "
                "settore, ambient, saggio, quad_par, documentazione "
                "FROM us_table WHERE sito = :sito"), {"sito": sito}).fetchall()
            period_datazione = {}
            try:
                for p_per, p_fase, p_dat in conn.execute(text(
                        "SELECT periodo, fase, datazione_estesa "
                        "FROM periodizzazione_table WHERE sito = :sito"),
                        {"sito": sito}).fetchall():
                    if p_dat:
                        period_datazione[(str(p_per), str(p_fase))] = str(p_dat)
            except Exception:                       # noqa: BLE001
                period_datazione = {}

        by_id = {str(n.node_id): n for n in graph.nodes}
        by_name = {}
        for n in graph.nodes:
            by_name.setdefault(str(getattr(n, "name", "")), n)
        claimed = set()

        def _find(node_uuid, us_name, area, ut_str):
            node = by_id.get(str(node_uuid)) if node_uuid else None
            if node is None:
                composite = "%s.%s%s" % (area or "", ut_str, us_name)
                for key in (composite, us_name):
                    cand = by_name.get(key)
                    if cand is not None and id(cand) not in claimed:
                        node = cand
                        break
            if node is not None and id(node) in claimed:
                return None                          # a row per node, mai due
            return node

        for (us_val, node_uuid, sito_v, area, unita_tipo, periodo_ini,
             fase_ini, rapporti_raw, d_strat, d_interp, attivita, struttura,
             settore, ambient, saggio, quad_par, documentazione) in rows:
            us_name = str(us_val) if us_val is not None else None
            if not us_name:
                continue
            ut_str = str(unita_tipo) if unita_tipo is not None else ""
            ut_canon = canonical_unita_tipo(ut_str)
            node = _find(node_uuid, us_name, area, ut_str)
            if node is None:
                # back-fill: the importer skipped the row, or its name
                # was claimed by another row (paradata collisions)
                make_as = ut_canon if ut_canon in _STRAT_FAMILY else "US"
                node = _create_stratigraphic_node_for_unita_tipo(
                    make_as, us_name,
                    str(node_uuid) if node_uuid
                    else "%s_%s_%s" % (sito, us_name, ut_str))
                if node is None:
                    continue
                try:
                    graph.add_node(node)
                except Exception:                   # noqa: BLE001
                    continue
                by_id[str(node.node_id)] = node
            claimed.add(id(node))

            attrs = getattr(node, "attributes", None)
            if attrs is None:
                node.attributes = attrs = {}
            if node_uuid is not None:
                attrs["node_uuid"] = str(node_uuid)
            attrs["us"] = us_name
            for key, value in (("sito", sito_v), ("area", area),
                               ("unita_tipo", ut_str or None),
                               ("periodo_iniziale", periodo_ini),
                               ("fase_iniziale", fase_ini),
                               ("rapporti", rapporti_raw),
                               ("d_stratigrafica", d_strat),
                               ("d_interpretativa", d_interp),
                               ("attivita", attivita),
                               ("struttura", struttura),
                               ("settore", settore),
                               ("ambient", ambient),
                               ("saggio", saggio),
                               ("quad_par", quad_par),
                               ("documentazione", documentazione)):
                if value is not None:
                    attrs[key] = str(value)
            dat_value = period_datazione.get(
                (str(periodo_ini) if periodo_ini is not None else "",
                 str(fase_ini) if fase_ini is not None else ""))
            if dat_value:
                attrs["datazione_estesa"] = dat_value
            try:
                from s3dgraphy.utils.utils import apply_legacy_kind
                apply_legacy_kind(node, ut_str)
            except Exception:                       # noqa: BLE001
                pass


    @staticmethod
    def _fix_epochs(graph, db_path, sito):
        """One epoch per (periodo, fase), with pyArchInit's label.

        The dev40 importer writes ``epoch::sito::p::f`` nodes and the
        library projector writes ``epoch_p_f`` ones — the same period
        twice. The canonical node here is ``epoch_p_f`` (what the
        round-trip and the tests key on): the importer twin's edges are
        retargeted onto it and the twin dropped. Names follow the
        Ventena fix (2026-08-27): ``datazione_estesa``, else
        ``descrizione``, else ``Period P Phase F``; names shared by two
        periods get ``(periodo P, fase F)`` appended, because the
        swimlane rows and the round-trip hydration key on the name.
        ``description`` carries the free-text ``descrizione``.
        """
        from sqlalchemy import text

        from s3dgraphy.sync._db_handle import _resolve_db_handle

        handle = _resolve_db_handle(db_path)
        with handle.engine.connect() as conn:
            try:
                rows = conn.execute(text(
                    "SELECT periodo, fase, descrizione, datazione_estesa "
                    "FROM periodizzazione_table WHERE sito = :sito"),
                    {"sito": sito}).fetchall()
            except Exception:                       # noqa: BLE001
                rows = []
        info = {}
        for periodo, fase, descr, dat in rows:
            if periodo is None:
                continue
            try:
                key = (int(periodo), str(fase) if fase is not None else "")
            except (TypeError, ValueError):
                continue
            info[key] = (descr, dat)

        # i nomi, con i tre ripieghi e la disambiguazione
        base_names = {}
        for key, (descr, dat) in info.items():
            base_names[key] = ((dat or "").strip()
                               or (descr or "").strip()
                               or "Period %s Phase %s" % key)
        seen = {}
        for key in sorted(base_names):
            seen.setdefault(base_names[key], []).append(key)
        names = {}
        for name, keys in seen.items():
            if len(keys) == 1:
                names[keys[0]] = name
            else:
                for key in keys:
                    names[key] = "%s (periodo %s, fase %s)" % (name, key[0], key[1])

        by_id = {str(n.node_id): n for n in graph.nodes}
        drop = []
        for key, name in names.items():
            canonical = by_id.get("epoch_%s_%s" % key)
            twin = by_id.get("epoch::%s::%s::%s" % (sito, key[0], key[1]))
            keep = canonical or twin
            if keep is None:
                continue
            if canonical is not None and twin is not None and twin is not canonical:
                twin_id, keep_id = str(twin.node_id), str(keep.node_id)
                for e in getattr(graph, "edges", None) or []:
                    if getattr(e, "edge_source", None) == twin_id:
                        e.edge_source = keep_id
                    if getattr(e, "edge_target", None) == twin_id:
                        e.edge_target = keep_id
                drop.append(twin)
            keep.name = names[key]
            descr, dat = info[key]
            if descr:
                keep.description = str(descr)
            attrs = getattr(keep, "attributes", None)
            if attrs is None:
                keep.attributes = attrs = {}
            if dat:
                attrs["datazione_estesa"] = str(dat)
        if drop:
            dropped = {id(n) for n in drop}
            graph.nodes = [n for n in graph.nodes if id(n) not in dropped]
            if hasattr(graph, "invalidate_indices"):
                graph.invalidate_indices()

    @staticmethod
    def _build_rapporti_edges(graph):
        """pyArchInit's ``rapporti`` strings → stratigraphic edges.

        Ported from the pre-one-bridge projector: targets are found by
        the ``us`` attribute (dev40 node names are composite labels),
        same-family preference discriminates rows sharing a name
        (Bug P), the yE-F folder resolver picks the right multi-folder
        copy, and the stable edge id collapses the two symmetric
        declarations of one relation into one edge.
        """
        from s3dgraphy.rapporti import parse_rapporti

        # Il datamodel EM non ammette i tipi inversi verso una US
        # (avviso di EMStudio sul demo, 2026-10-07): la coppia
        # Copre/Coperto da deve essere UN arco diretto, come già
        # nell'adapter della stanza (room/us_ops.INVERSE_TO_FORWARD).
        inverse_to_forward = {
            "is_overlain_by": "overlies",
            "is_cut_by": "cuts",
            "is_filled_by": "fills",
            "is_abutted_by": "abuts",
            "is_leaned_on_by": "leans_on",
            "is_before": "is_after",
        }
        symmetric = {"equals", "bonded_to", "has_same_time",
                     "is_physically_equal_to", "is_bonded_to"}

        paradata = frozenset(_PARADATA_UNITA_TIPO)

        def family(ut):
            return "paradata" if ut in paradata else "strat"

        by_us = {}
        for n in graph.nodes:
            us = (getattr(n, "attributes", None) or {}).get("us")
            if us:
                by_us.setdefault(str(us), []).append(n)

        added = 0
        for us_node in list(graph.nodes):
            attrs = getattr(us_node, "attributes", None) or {}
            raw = attrs.get("rapporti")
            if not raw:
                continue
            src_family = family(attrs.get("unita_tipo") or "US")
            src_folder = attrs.get("attivita")
            for (edge_type, target_us, _area, _sito, swap) in \
                    parse_rapporti(raw):
                candidates = by_us.get(str(target_us), [])
                target_node = None
                if candidates and src_folder:
                    for c in candidates:
                        resolved = _resolve_target_for_folder(
                            c, src_folder, graph)
                        if resolved is not c:
                            target_node = resolved
                            break
                if target_node is None and candidates:
                    for c in candidates:
                        c_attrs = getattr(c, "attributes", None) or {}
                        if family(c_attrs.get("unita_tipo") or "US") == src_family:
                            target_node = c
                            break
                    if target_node is None:
                        target_node = candidates[0]
                if target_node is None:
                    continue
                if edge_type in inverse_to_forward:
                    edge_type = inverse_to_forward[edge_type]
                    swap = not swap
                src_node, dst_node = ((target_node, us_node) if swap
                                      else (us_node, target_node))
                if edge_type in symmetric \
                        and str(dst_node.node_id) < str(src_node.node_id):
                    src_node, dst_node = dst_node, src_node
                edge_id = "rap_%s_%s_%s" % (
                    src_node.node_id, dst_node.node_id, edge_type)
                if graph.find_edge_by_id(edge_id) is None:
                    try:
                        graph.add_edge(edge_id=edge_id,
                                       edge_source=src_node.node_id,
                                       edge_target=dst_node.node_id,
                                       edge_type=edge_type)
                        added += 1
                    except Exception:               # noqa: BLE001
                        pass
        return added

    @staticmethod
    def _warn_suspicious_chronologies(graph, db_path):
        from sqlalchemy import text

        from modules.utility.periodization_checks import (
            format_chronology_warning, suspicious_chronologies)
        from s3dgraphy.sync._db_handle import _resolve_db_handle
        handle = _resolve_db_handle(db_path)
        with handle.engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT periodo, fase, cron_iniziale, cron_finale, "
                "descrizione FROM periodizzazione_table")).fetchall()
        bad = suspicious_chronologies(
            (r[0], r[1], r[2], r[3], r[4]) for r in rows)
        if bad:
            if not hasattr(graph, "warnings") or graph.warnings is None:
                graph.warnings = []
            graph.warnings.append(format_chronology_warning(bad, 'it'))
            print("[GraphProjector] " + format_chronology_warning(bad, 'en'))
