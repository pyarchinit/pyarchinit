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

import logging

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


class GraphProjector(_LibGraphProjector):
    """The library's projector with pyArchInit's closing passes."""

    def populate_graph(self, db_path, sito, **kwargs):
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
                src_node, dst_node = ((target_node, us_node) if swap
                                      else (us_node, target_node))
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
