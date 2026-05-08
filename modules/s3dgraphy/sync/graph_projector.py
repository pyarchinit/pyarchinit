"""Project PyArchInit DB rows into a stratigraphic-layer s3dgraphy Graph.

AI05 promotes this module from the AI04 thin-wrapper (Strategy D) to a
proper class (Strategy A). The body of the former
``_enrich_pyarchinit_graph`` standalone function (deleted from
``graphml_writer`` in AI05 Group C) now lives inside
:py:meth:`GraphProjector._enrich_into`.

Exposed publicly so callers (UI Import tab, CLI helper, future
SyncEngine in Phase 3) have a stable API surface even while the
underlying implementation evolves.
"""
from __future__ import annotations

import ast
import sqlite3
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from .graph_ingestor import GraphSyncError

if TYPE_CHECKING:
    import s3dgraphy


class ProjectionError(GraphSyncError):
    """Read-side failure during GraphProjector.populate_graph()."""


class GraphProjector:
    """Stratigraphic-layer projection from PyArchInit DB to s3dgraphy Graph.

    Usage:
        projector = GraphProjector()
        graph = projector.populate_graph(db_path, sito="Scavo archeologico")

    The graph contains StratigraphicUnit / USM / USVs / USVn / USD /
    SF / VSF / CON / DOC / Extractor / Combinar / property nodes plus
    EpochNodes for the (periodo, fase) tuples present in the filtered
    rows. Edges follow the rapporti column conventions decoded by
    `_RAPPORTI_TO_EDGE_TYPE` and `_RAPPORTI_SHORTHAND` in
    graphml_writer.py.
    """

    def __init__(self, vocab_provider=None) -> None:
        # vocab_provider parameter is here for API forward-compat
        # with AI06+ (where vocabulary aliases drive normalisation).
        # AI04 does not consume it.
        self._vocab_provider = vocab_provider

    def populate_graph(
        self,
        db_path: Path,
        sito: str,
        *,
        include_paradata: bool = True,
        strict_schema: bool = True,
        groups: list = None,                # NEW (AI06 D7-A: None = no grouping)
    ) -> "s3dgraphy.Graph":
        """Build and return a s3dgraphy.Graph populated with the
        stratigraphic rows of `sito` from the SQLite at `db_path`.

        Args:
            db_path: filesystem path to the pyarchinit SQLite DB.
            sito: site identifier (`us_table.sito` value). Mandatory
                — multi-graph projections are out of scope for AI04.
            include_paradata: when True (default), merge any
                ``paradata.graphml`` produced by :class:`ParadataStore`
                for the (db, sito) pair. When False, return the pure
                stratigraphic layer (backward-compat for AI04 callers
                like ``graphml_writer.export_graphml``). On read errors
                we log a warning and fall back to strat-only — never
                fatal.
            strict_schema: when True (default), require that the
                Phase-1 migration has been applied (i.e.
                ``us_table.node_uuid`` exists) and propagate node-UUID
                attributes onto each StratigraphicUnit so AI04 can do a
                round-trip. When False, skip both the schema check and
                ``_propagate_node_uuid_and_us``: useful for the AI03
                strat-only export path (``graphml_writer.export_graphml``)
                which only needs labels/edges/swimlanes — node_uuid is
                irrelevant there and AC-2 fixtures pre-date the
                migration.

        Returns:
            A populated `s3dgraphy.Graph`. Empty graph (zero nodes) is
            valid: it just means the site has no rows.

        Raises:
            ProjectionError: on any failure reaching the DB or
                instantiating the in-memory graph.
        """
        if not sito:
            raise ProjectionError(
                "sito parameter is mandatory for GraphProjector.populate_graph(); "
                "AI04 only supports single-site graphs.")
        db_path = Path(db_path)
        if not db_path.exists():
            raise ProjectionError(f"DB file not found: {db_path}")

        # Verify Phase 1 migration applied: us_table.node_uuid column.
        # Skipped when strict_schema=False (AI03 export path).
        if strict_schema:
            self._verify_node_uuid_column(db_path)

        # Delegate to the existing AI03 enrichment routine.
        try:
            from s3dgraphy import Graph
            from s3dgraphy.importer.pyarchinit_importer import (
                PyArchInitImporter)
        except ImportError as e:
            raise ProjectionError(f"s3dgraphy import failed: {e}") from e

        # Stage 1: import the StratigraphicUnit nodes from us_table via
        # the upstream PyArchInitImporter (spec §3.2: "Reuses the
        # already-existing s3dgraphy.importer.pyarchinit_importer as
        # base"). The importer creates one Graph with `graph_id` derived
        # from the file basename; we then transplant its nodes/edges
        # into a graph keyed by `sito` for AI04 single-site semantics.
        try:
            importer = PyArchInitImporter(
                filepath=str(db_path),
                mapping_name="pyarchinit_us_mapping",
            )
            imported = importer.parse()
        except Exception as e:
            raise ProjectionError(
                f"Importer failed for db={db_path}: {e}") from e

        graph = Graph(graph_id=sito)
        # Transplant imported nodes/edges into the sito-keyed graph.
        # Skip the auto-created GeoPositionNode of `imported` (graph
        # already has its own from Graph.__init__).
        for node in list(imported.nodes):
            if type(node).__name__ == "GeoPositionNode":
                continue
            try:
                graph.add_node(node, overwrite=True)
            except Exception:
                # Defensive: best-effort; fall through to enrichment.
                pass
        for edge in list(imported.edges):
            try:
                graph.add_edge(
                    edge_id=edge.edge_id,
                    edge_source=edge.edge_source,
                    edge_target=edge.edge_target,
                    edge_type=edge.edge_type,
                )
            except Exception:
                pass

        try:
            self._enrich_into(graph, db_path, sito_filter=sito)
        except Exception as e:
            raise ProjectionError(
                f"Enrichment failed for sito={sito!r}: {e}") from e

        # Stage 2b: propagate node_uuid, us, and the remaining mapped
        # columns from the DB so the GraphIngestor can do its
        # `WHERE node_uuid = ?` round-trip. The upstream
        # `_enrich_pyarchinit_graph` only sets 4 attributes
        # (sito/area/unita_tipo/d_stratigrafica) — AI04 needs the full
        # MAPPED_COLUMNS set on each StratigraphicUnit.
        # Skipped when strict_schema=False (AI03 export path doesn't need
        # node_uuid and may run on pre-migration fixtures).
        if strict_schema:
            try:
                self._propagate_node_uuid_and_us(graph, db_path, sito)
            except Exception as e:
                raise ProjectionError(
                    f"node_uuid propagation failed: {e}") from e

        # Filter post-enrichment: keep only nodes whose attributes['sito']
        # match (defence in depth — _enrich already filters us_table rows
        # but EpochNodes are global and may belong to other sites).
        # We do NOT prune EpochNodes that are referenced via
        # has_first_epoch from any kept node.
        kept_node_ids = {
            n.node_id for n in graph.nodes
            if not hasattr(n, "attributes")
            or n.attributes is None
            or n.attributes.get("sito") in (None, sito)
        }
        # EpochNodes are global — keep them all if any strat node references them.
        # The downstream SiteMismatchError check in GraphIngestor catches mismatches.
        graph.nodes = [n for n in graph.nodes if n.node_id in kept_node_ids
                       or _is_epoch_node(n)]

        # D3: optionally merge paradata.graphml on top of the strat layer.
        if include_paradata:
            self._merge_paradata(graph, db_path, sito)

        # AI06: optional grouping by us_table dimensions + ad-hoc
        if groups:
            try:
                self._merge_groups(graph, db_path, sito, groups)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f"_merge_groups failed, continuing without groups: {e}")

        return graph

    def _verify_node_uuid_column(self, db_path: Path) -> None:
        """Ensure the Phase-1 migration that added ``us_table.node_uuid``
        has been applied. Raises :class:`ProjectionError` otherwise.

        Extracted from ``populate_graph`` in AI05 Group C step 2 so the
        schema-check is testable in isolation and reusable by any future
        method that touches strat tables.
        """
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise ProjectionError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise ProjectionError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")

    def _merge_paradata(self, graph, db_path: Path, sito: str) -> None:
        """Read ``paradata.graphml`` for *sito* and add its nodes to
        *graph*.

        Non-fatal on read errors — logs a warning and returns. The
        caller still gets the strat layer.

        De-duplication: nodes whose ``node_id`` already exists on the
        target graph are skipped (the strat layer wins). Edges from the
        paradata graph are NOT merged here; AI05 Group C does
        node-only merging because the paradata graph is currently
        author/license/embargo nodes with no connecting edges.
        """
        from .paradata_store import ParadataStore, ParadataReadError
        import logging
        log = logging.getLogger(__name__)

        store = ParadataStore(db_path, sito)
        if not store.exists():
            return
        try:
            paradata_graph = store.read()
        except ParadataReadError as e:
            log.warning(
                "Paradata file unreadable, falling back to strat-only: %s",
                e)
            return

        existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}
        for n in paradata_graph.nodes:
            nid = getattr(n, "node_id", None)
            if nid and nid not in existing_ids:
                try:
                    graph.add_node(n)
                except Exception:
                    # Defensive: best-effort merge; never fail strat path.
                    pass

    def _propagate_node_uuid_and_us(self, graph, db_path, sito) -> None:
        """Set attributes['node_uuid'], 'us' and the remaining mapped
        columns on each StratigraphicUnit-family node.

        Match nodes by `name` (the importer emits name=str(us_table.us))
        within the requested sito. Idempotent: re-running yields the
        same attribute values.
        """
        # Build a name -> node index over the importer-emitted strat nodes.
        strat_by_name = {}
        for n in graph.nodes:
            cls = type(n).__name__
            if cls.startswith("Stratigraphic") or cls == "USNode":
                strat_by_name[str(getattr(n, "name", ""))] = n
        if not strat_by_name:
            return  # nothing to propagate

        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT us, node_uuid, sito, area, unita_tipo, "
                "periodo_iniziale, fase_iniziale, rapporti, "
                "d_stratigrafica, d_interpretativa, attivita, struttura "
                "FROM us_table WHERE sito = ?",
                (sito,),
            )
            rows = cur.fetchall()
        finally:
            conn.close()

        for (us_val, node_uuid, sito_v, area, unita_tipo,
             periodo_ini, fase_ini, rapporti_raw, d_strat,
             d_interp, attivita, struttura) in rows:
            us_name = str(us_val) if us_val is not None else None
            if not us_name or us_name not in strat_by_name:
                continue
            node = strat_by_name[us_name]
            attrs = node.attributes
            # Always set node_uuid + us (these are the lookup keys).
            if node_uuid is not None:
                attrs["node_uuid"] = str(node_uuid)
            attrs["us"] = us_name
            # Also propagate any other MAPPED_COLUMNS not already set
            # by _enrich (defensive overwrite — projector wins by
            # definition for round-trip identity).
            if sito_v is not None:
                attrs["sito"] = str(sito_v)
            if area is not None:
                attrs["area"] = str(area)
            if unita_tipo is not None:
                attrs["unita_tipo"] = str(unita_tipo)
            if periodo_ini is not None:
                attrs["periodo_iniziale"] = str(periodo_ini)
            if fase_ini is not None:
                attrs["fase_iniziale"] = str(fase_ini)
            if rapporti_raw is not None:
                attrs["rapporti"] = str(rapporti_raw)
            if d_strat is not None:
                attrs["d_stratigrafica"] = str(d_strat)
            if d_interp is not None:
                attrs["d_interpretativa"] = str(d_interp)
            if attivita is not None:
                attrs["attivita"] = str(attivita)
            if struttura is not None:
                attrs["struttura"] = str(struttura)

    def _enrich_into(self, graph, db_path, sito_filter=None):
        """Phase 2 / Strategy A — full-class implementation.

        Body absorbed verbatim from the now-deleted standalone function
        formerly named ``_enrich_pyarchinit_graph`` in ``graphml_writer``.

        Bake epoch swimlanes + topological rapporti edges into *graph*.

        The vendored s3dgraphy 0.1.40 PyArchInitImporter is incomplete:
        it imports only US columns mapped in the JSON mapping (us_table
        → StratigraphicNode + PropertyNodes), and does NOT:

          * read periodizzazione_table → create EpochNodes
          * add ``has_first_epoch`` edges from each US to its periodo
          * parse the ``rapporti`` JSON column → create topological edges

        Without those, the GraphMLExporter has no input for swimlanes
        and no input for the TemporalInferenceEngine — both AI03
        acceptance criteria fail. We perform the enrichment here, in
        the orchestrator's filter+enrich layer, so the bridge stays a
        one-call surface and so the test fixture remains pure
        pyArchInit-shaped data.

        Mutates the graph in place. No-op if the DB file lacks the
        expected tables.
        """
        from s3dgraphy.nodes.epoch_node import EpochNode
        # Lazy-import the rapporti tables and palette from graphml_writer
        # to avoid duplicating these constants — they remain authoritative
        # in the writer module.
        from .graphml_writer import (
            _RAPPORTI_TO_EDGE_TYPE,
            _RAPPORTI_SHORTHAND,
            _EPOCH_ROW_PALETTE,
        )

        # Build a name → StratigraphicNode index over the existing
        # importer-emitted nodes; rapporti reference US by their numeric
        # name, not by the importer-generated UUIDs.
        strat_by_name = {}
        for n in graph.nodes:
            # Importer emits `name = str(us_number)` for stratigraphic
            # rows. Skip PropertyNodes (they have a name like
            # "Interpretation" rather than the US id).
            nclass = type(n).__name__
            if nclass.startswith("Stratigraphic") or nclass == "USNode":
                strat_by_name[str(n.name)] = n

        if not strat_by_name:
            return  # nothing to enrich

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
        except sqlite3.Error:
            return

        try:
            # ---- 1. EpochNodes from periodizzazione_table -------------
            # Schema columns vary slightly across pyArchInit releases;
            # we read defensively. Each (periodo, fase) is one epoch.
            epoch_by_key = {}  # (periodo:int, fase:str) -> EpochNode
            try:
                cursor.execute(
                    "SELECT periodo, fase, cron_iniziale, cron_finale, "
                    "descrizione FROM periodizzazione_table"
                )
                raw_rows = cursor.fetchall()
            except sqlite3.Error:
                raw_rows = []
            # Sort the periodizzazione rows by (periodo asc, fase asc) so
            # that when we add EpochNodes to the graph, ties on cron_iniziale
            # are broken by the natural phase numbering. The swimlane
            # generator at `epoch_generator.py:298` uses Python's stable
            # `sorted(..., reverse=True)`, so ties preserve insertion order:
            # phases inserted earlier here will end up above phases inserted
            # later in the rendered matrix when their cron_iniziale tie.
            def _sort_key(row):
                periodo, fase, *_ = row
                try:
                    p_num = int(periodo) if periodo is not None else 0
                except (TypeError, ValueError):
                    p_num = 0
                try:
                    f_num = float(fase) if fase is not None else 0.0
                except (TypeError, ValueError):
                    f_num = 0.0
                return (p_num, f_num)
            rows_sorted = sorted(raw_rows, key=_sort_key)

            try:
                for periodo, fase, cron_ini, cron_fin, descr in rows_sorted:
                    if periodo is None:
                        continue
                    key = (int(periodo), str(fase) if fase is not None else "")
                    node_id = f"epoch_{key[0]}_{key[1]}"
                    # Skip if already present (idempotent on repeat
                    # invocation in single-graph mode).
                    if graph.find_node_by_id(node_id) is not None:
                        epoch_by_key[key] = graph.find_node_by_id(node_id)
                        continue
                    start = float(cron_ini) if cron_ini is not None else 0.0
                    end = float(cron_fin) if cron_fin is not None else 0.0
                    label = descr or f"Period {key[0]} Phase {key[1]}"
                    # Cycle a pastel palette across epochs so each
                    # swimlane row renders in a distinct background colour.
                    # The s3dgraphy EpochSwimlanesGenerator
                    # (`epoch_generator.py:360`) honours `epoch.color` when
                    # it is not the default `#FFFFFF`; without an explicit
                    # color it falls back to a single `#CCFFCC` for every
                    # row, which is what the user reported as "tutti
                    # verdino".
                    row_color = _EPOCH_ROW_PALETTE[
                        len(epoch_by_key) % len(_EPOCH_ROW_PALETTE)]
                    ep = EpochNode(
                        node_id=node_id,
                        name=str(label),
                        start_time=start,
                        end_time=end,
                        color=row_color,
                    )
                    # Stash periodo/fase on the EpochNode so the AI04
                    # graphml round-trip can recover them via the
                    # _embed_pyarchinit_data_keys post-processor (which
                    # reads from `attributes` rather than parsing node_id —
                    # node_id may be reassigned by GraphMLExporter).
                    if not hasattr(ep, "attributes") or ep.attributes is None:
                        ep.attributes = {}
                    ep.attributes["periodo"] = str(key[0])
                    ep.attributes["fase"] = str(key[1])
                    if cron_ini is not None:
                        ep.attributes["cron_iniziale"] = str(int(cron_ini))
                    if cron_fin is not None:
                        ep.attributes["cron_finale"] = str(int(cron_fin))
                    if descr:
                        ep.attributes["datazione_estesa"] = str(descr)
                    graph.add_node(ep)
                    epoch_by_key[key] = ep
            except sqlite3.Error:
                pass  # missing table is tolerated; epoch_count just stays 0

            # ---- 2. has_first_epoch edges and rapporti edges ----------
            # Also propagate `sito` and `area` to attributes so
            # _filter_by_site can match — the upstream PyArchInitImporter
            # mapping JSON only emits 5 columns and `sito` is not one of
            # them, leaving us_node.attributes empty post-import.
            try:
                if sito_filter is not None:
                    cursor.execute(
                        "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                        "fase_iniziale, rapporti, d_stratigrafica "
                        "FROM us_table WHERE sito = ?",
                        (sito_filter,),
                    )
                else:
                    cursor.execute(
                        "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                        "fase_iniziale, rapporti, d_stratigrafica "
                        "FROM us_table"
                    )
                rows = cursor.fetchall()
            except sqlite3.Error:
                rows = []

            for (us_val, sito, area, unita_tipo, periodo_ini, fase_ini,
                 rapporti_raw, d_stratigrafica) in rows:
                us_name = str(us_val) if us_val is not None else None
                if not us_name or us_name not in strat_by_name:
                    continue
                us_node = strat_by_name[us_name]

                # Propagate identity attributes so site/area filters work
                # and so the post-processor can drive per-type styling.
                if sito is not None:
                    us_node.attributes["sito"] = str(sito)
                if area is not None:
                    us_node.attributes["area"] = str(area)
                if unita_tipo is not None:
                    us_node.attributes["unita_tipo"] = str(unita_tipo)
                # d_stratigrafica is the user-friendly description used as
                # the LABEL for property nodes (e.g. "Materiale").
                if d_stratigrafica is not None:
                    us_node.attributes["d_stratigrafica"] = str(d_stratigrafica)

                # 2a. has_first_epoch edge
                if periodo_ini is not None:
                    try:
                        p_int = int(periodo_ini)
                    except (TypeError, ValueError):
                        p_int = None
                    if p_int is not None:
                        f_str = (str(fase_ini) if fase_ini is not None else "")
                        epoch = epoch_by_key.get((p_int, f_str))
                        # If exact (periodo, fase) not found, fall back to
                        # any epoch with the same periodo (some fixtures
                        # store fase as int, others as str).
                        if epoch is None:
                            for (p, _f), e in epoch_by_key.items():
                                if p == p_int:
                                    epoch = e
                                    break
                        if epoch is not None:
                            edge_id = f"hfe_{us_node.node_id}_{epoch.node_id}"
                            if graph.find_edge_by_id(edge_id) is None:
                                graph.add_edge(
                                    edge_id=edge_id,
                                    edge_source=us_node.node_id,
                                    edge_target=epoch.node_id,
                                    edge_type="has_first_epoch",
                                )

                # 2b. rapporti → topological edges
                if not rapporti_raw or rapporti_raw == "[]":
                    continue
                try:
                    rapporti = ast.literal_eval(rapporti_raw)
                except (ValueError, SyntaxError):
                    continue
                if not isinstance(rapporti, list):
                    continue
                for rapporto in rapporti:
                    if not isinstance(rapporto, list) or len(rapporto) < 2:
                        continue
                    # Preserve case for the shorthand tokens (>, >>, <, <<);
                    # the named relations (copre/cuts/...) are case-folded.
                    rel_raw = str(rapporto[0]).strip()
                    rel_type_named = rel_raw.lower()
                    target_us = str(rapporto[1]).strip()
                    target_node = strat_by_name.get(target_us)
                    if target_node is None:
                        continue

                    # Try named-relation table first, then shorthand tokens.
                    edge_type = _RAPPORTI_TO_EDGE_TYPE.get(rel_type_named)
                    swap = False
                    if edge_type is None:
                        shorthand = _RAPPORTI_SHORTHAND.get(rel_raw)
                        if shorthand is None:
                            continue
                        edge_type, swap = shorthand

                    src_node, dst_node = (
                        (target_node, us_node) if swap
                        else (us_node, target_node)
                    )
                    # Stable ID keyed on (src, dst, edge_type): when both
                    # endpoints declare the same relation in their rapporti
                    # (e.g. 102 says "> 6" and 6 says "< 102", both
                    # encoding "102 is_after 6"), only one edge is added.
                    edge_id = (
                        f"rap_{src_node.node_id}_{dst_node.node_id}_"
                        f"{edge_type}")
                    if graph.find_edge_by_id(edge_id) is None:
                        graph.add_edge(
                            edge_id=edge_id,
                            edge_source=src_node.node_id,
                            edge_target=dst_node.node_id,
                            edge_type=edge_type,
                        )
        finally:
            conn.close()

    def _merge_groups(self, graph, db_path, sito, dimensions):
        """Materialize ActivityNodeGroup nodes + is_in_activity edges
        from SQL columns and ad-hoc store. Each group node carries
        a ``group_kind`` attribute distinguishing the dimension."""
        from .group_projector import (
            build_groups_from_sql, merge_adhoc_groups,
        )
        # SQL-derived dims (anything except 'adhoc')
        sql_dims = [d for d in dimensions if d != "adhoc"]
        specs = build_groups_from_sql(db_path, sito, sql_dims)

        if "adhoc" in dimensions:
            from .group_store import GroupStore
            store = GroupStore(db_path, sito)
            specs = merge_adhoc_groups(specs, store)

        # Materialize as s3dgraphy ActivityNodeGroup nodes
        from s3dgraphy.nodes.group_node import ActivityNodeGroup

        # Build node_uuid (DB) -> node_id (graph) map for stratigraphic
        # nodes: GroupSpec.member_us_uuids are us_table.node_uuid values,
        # but the s3dgraphy node_id is the importer-assigned EMID. The
        # node_uuid is propagated onto the StratigraphicUnit's attributes
        # by _propagate_node_uuid_and_us (Stage 2b).
        node_uuid_to_id: dict = {}
        for n in graph.nodes:
            attrs = getattr(n, "attributes", None) or {}
            nu = attrs.get("node_uuid")
            if nu:
                node_uuid_to_id[str(nu)] = getattr(n, "node_id", None)

        existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}
        for spec in specs:
            if spec.group_uuid in existing_ids:
                continue  # idempotent — don't double-add on retry
            node = ActivityNodeGroup(
                node_id=spec.group_uuid,
                name=spec.name,
                description=spec.description or "",
            )
            data_key = f"pyarchinit.{spec.group_kind}"
            node.attributes = {
                "group_kind": spec.group_kind,
                "sito": sito,
                "name": spec.name,
                data_key: spec.name,
                "group_uuid": spec.group_uuid,
            }
            graph.add_node(node)
            existing_ids.add(spec.group_uuid)

            # is_in_activity edge from each US member to this group.
            # Translate DB node_uuid -> graph node_id when available;
            # fall back to the raw UUID (round-trip / external reference).
            for us_uuid in spec.member_us_uuids:
                src_id = node_uuid_to_id.get(str(us_uuid), us_uuid)
                # Edge ID uses full UUIDs to avoid collisions among
                # members whose node_uuids share an 8-char prefix
                # (UUID7 timestamps make this common in batched seeds).
                edge_id = f"grp_{us_uuid}_{spec.group_uuid}"
                try:
                    graph.add_edge(
                        edge_id=edge_id,
                        edge_source=src_id,
                        edge_target=spec.group_uuid,
                        edge_type="is_in_activity",
                    )
                except Exception:
                    # Edge validation may reject if connection
                    # rules don't accept the source type — log
                    # and continue (defensive).
                    pass


def _is_epoch_node(node) -> bool:
    """Return True if node is an EpochNode. Defensive — avoids importing
    EpochNode at module top because it forces s3dgraphy load too early."""
    return type(node).__name__ == "EpochNode"
