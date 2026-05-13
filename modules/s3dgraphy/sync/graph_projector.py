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
import logging
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from sqlalchemy import text

from ._db_handle import DbHandle, _columns_of, _resolve_db_handle
from .graph_ingestor import GraphSyncError

if TYPE_CHECKING:
    import s3dgraphy


__all__ = [
    "GraphProjector",
    "ProjectionError",
    "DEFAULT_PRIMARY_PRIORITY",
    "compute_primary",
]


class ProjectionError(GraphSyncError):
    """Read-side failure during GraphProjector.populate_graph()."""


# AI07: hardcoded priority order for compute_primary. Toponym is
# explicitly excluded — toponym memberships are NEVER primary.
DEFAULT_PRIMARY_PRIORITY: list = [
    "struttura", "attivita", "area", "settore",
    "ambient", "saggio", "quad_par",
]


def compute_primary(memberships: list, priority_order: list) -> dict:
    """Pick exactly one primary group_uuid per us_id following priority.

    memberships: list of dicts with at least these keys:
      - us_id: graph node_id of the US
      - group_uuid: target group node_id
      - group_kind: pyarchinit dimension (struttura, area, ..., toponym)

    priority_order: list of group_kind names, highest priority first.
      Toponym is excluded automatically (never primary).

    Returns: dict us_id → group_uuid (the primary). US without any
    eligible spatial/activity membership get no entry.
    """
    by_us: dict = {}  # us_id → {group_kind → group_uuid}
    for m in memberships:
        if m["group_kind"] == "toponym":
            continue  # toponym never primary
        by_us.setdefault(m["us_id"], {})[m["group_kind"]] = m["group_uuid"]

    out: dict = {}
    for us_id, dims in by_us.items():
        for dim in priority_order:
            if dim in dims:
                out[us_id] = dims[dim]
                break
        else:
            # Fallback: take the membership with the alphabetically-first
            # group_kind for cross-process determinism (deferred Group C nit).
            if dims:
                out[us_id] = dims[sorted(dims.keys())[0]]
    return out


def _is_us_node(node) -> bool:
    """Return True if *node* is a stratigraphic unit (US/USM/USVs/...)."""
    cls_name = type(node).__name__
    return cls_name == "USNode" or cls_name.startswith("Stratigraphic")


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
        db_path,  # Path | DbHandle | str — PG-B: accepts shim input
        sito: str,
        *,
        include_paradata: bool = True,
        strict_schema: bool = True,
        groups: list = None,                # NEW (AI06 D7-A: None = no grouping)
        primary_priority: list = None,      # NEW (AI07 C: per-US is_primary order)
    ) -> "s3dgraphy.Graph":
        """Build and return a s3dgraphy.Graph populated with the
        stratigraphic rows of `sito` from the SQLite at `db_path`.

        Args:
            db_path: filesystem path to the pyarchinit SQLite DB, or a
                DbHandle / conn-string. PG-B (5.7.1-alpha): accepts
                ``Path | DbHandle | str`` via ``_resolve_db_handle``.
                Existing callers passing ``Path`` continue to work.
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
            primary_priority: optional list of dimension names ordered
                from highest to lowest priority for the AI07
                ``is_primary`` selection (compute_primary). When None,
                ``DEFAULT_PRIMARY_PRIORITY`` is used. Toponym is
                always excluded.

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

        # PG-Bv2 (5.7.9-alpha): route through DbHandle shim. Path
        # coercion + SQLite-only importer call are PG-fenced now;
        # SQLite path kept unchanged to preserve AC-2 byte-identical
        # baseline (α-narrow approach).
        # Pre-normalize: if db_path is a plain filesystem-path string
        # (not a SQLAlchemy URL), convert to Path so _resolve_db_handle
        # can dispatch to its Path branch (emits DeprecationWarning but
        # works). Callers passing a real conn-string / DbHandle / Engine
        # are passed through unchanged.
        from ._db_handle import _resolve_db_handle
        if (isinstance(db_path, str)
                and not db_path.startswith("sqlite:")
                and not db_path.startswith("postgresql")):
            db_path = Path(db_path)
        handle = _resolve_db_handle(db_path)

        # SQLite-only: derive a concrete filesystem path for the
        # PyArchInitImporter call below. Prefer handle.sqlite_path
        # (set by DbHandle.from_engine/from_path); fall back to
        # Path(db_path) only when db_path is itself a Path/str — never
        # mangle a DbManager instance (PG-Bv2 regression 2026-05-13).
        sqlite_path: Optional[Path] = None
        if not handle.is_postgres:
            sqlite_path = handle.sqlite_path
            if sqlite_path is None and isinstance(db_path, (str, Path)):
                sqlite_path = Path(db_path)
            if sqlite_path is None:
                raise ProjectionError(
                    "Cannot resolve SQLite filesystem path from "
                    f"db_path={type(db_path).__name__}")
            if not sqlite_path.exists():
                raise ProjectionError(f"DB file not found: {sqlite_path}")

        # Verify Phase 1 migration applied: us_table.node_uuid column.
        # Skipped when strict_schema=False (AI03 export path).
        if strict_schema:
            self._verify_node_uuid_column(handle)

        try:
            from s3dgraphy import Graph
        except ImportError as e:
            raise ProjectionError(f"s3dgraphy import failed: {e}") from e

        # Stage 1: import the StratigraphicUnit nodes from us_table.
        # PG → new SQLAlchemy native reader (PG-Bv2).
        # SQLite → upstream PyArchInitImporter (unchanged for AC-2).
        try:
            if handle.is_postgres:
                from .pyarchinit_pg_importer import import_from_pg
                imported = import_from_pg(
                    handle, sito,
                    mapping_name="pyarchinit_us_mapping",
                )
            else:
                from s3dgraphy.importer.pyarchinit_importer import (
                    PyArchInitImporter)
                importer = PyArchInitImporter(
                    filepath=str(sqlite_path),
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
        # AI06 D.2: also try in non-strict mode (best-effort) so the
        # GraphML round-trip can recover node_uuid via embedded data
        # keys. Pre-migration fixtures without the node_uuid column
        # silently skip.
        if strict_schema:
            try:
                self._propagate_node_uuid_and_us(graph, db_path, sito)
            except Exception as e:
                raise ProjectionError(
                    f"node_uuid propagation failed: {e}") from e
        else:
            try:
                self._propagate_node_uuid_and_us(graph, db_path, sito)
            except Exception:
                # Defensive — AC-2 baseline fixtures may lack the
                # node_uuid column. Best-effort only; export proceeds.
                pass

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

        # Stage 3 (AI07): toponym chain from site_table.
        # Always-on: the toponym chain is derived from project-level
        # metadata (site_table.{nazione,regione,provincia,comune}),
        # NOT from the `groups` parameter. It is unconditional even
        # when `groups=None`. To opt out, future callers may add an
        # `include_toponym=False` kwarg.
        try:
            self._emit_toponym_chain(graph, db_path, sito)
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"_emit_toponym_chain failed, continuing without "
                f"toponym chain: {e}")

        # AI06: optional grouping by us_table dimensions + ad-hoc
        if groups:
            try:
                self._merge_groups(graph, db_path, sito, groups,
                                   primary_priority)
            except Exception as e:
                logging.getLogger(__name__).warning(
                    f"_merge_groups failed, continuing without groups: {e}")

        return graph

    def _verify_node_uuid_column(self, db_path) -> None:
        """Ensure the Phase-1 migration that added ``us_table.node_uuid``
        has been applied. Raises :class:`ProjectionError` otherwise.

        PG-B (5.7.1-alpha): accepts ``Path | DbHandle | str`` via shim.
        Cross-backend introspection via Foundation's ``_columns_of``.
        """
        try:
            handle = _resolve_db_handle(db_path)
            cols = _columns_of(handle.engine, "us_table")
        except Exception as e:
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

        handle = _resolve_db_handle(db_path)
        with handle.engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT us, node_uuid, sito, area, unita_tipo, "
                    "periodo_iniziale, fase_iniziale, rapporti, "
                    "d_stratigrafica, d_interpretativa, attivita, struttura, "
                    "settore, ambient, saggio, quad_par, documentazione "
                    "FROM us_table WHERE sito = :sito"
                ),
                {"sito": sito},
            ).fetchall()

            # AI08-F2 hotfix: lookup datazione_estesa per (periodo, fase)
            # from periodizzazione_table so each US can carry its
            # period's full date string.
            period_datazione: dict = {}
            try:
                for p_per, p_fase, p_dat in conn.execute(
                    text(
                        "SELECT periodo, fase, datazione_estesa "
                        "FROM periodizzazione_table WHERE sito = :sito"
                    ),
                    {"sito": sito},
                ).fetchall():
                    if p_dat:
                        period_datazione[
                            (str(p_per), str(p_fase))
                        ] = str(p_dat)
            except Exception:
                period_datazione = {}

        for (us_val, node_uuid, sito_v, area, unita_tipo,
             periodo_ini, fase_ini, rapporti_raw, d_strat,
             d_interp, attivita, struttura,
             settore, ambient, saggio, quad_par, documentazione) in rows:
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
            # AI08-F2 hotfix: also propagate the 4 grouping dimensions
            # + documentazione + datazione_estesa per-US so they show
            # in yEd's node properties panel.
            if settore is not None and str(settore).strip():
                attrs["settore"] = str(settore)
            if ambient is not None and str(ambient).strip():
                attrs["ambient"] = str(ambient)
            if saggio is not None and str(saggio).strip():
                attrs["saggio"] = str(saggio)
            if quad_par is not None and str(quad_par).strip():
                attrs["quad_par"] = str(quad_par)
            if documentazione is not None and str(documentazione).strip() \
                    and str(documentazione).strip() != "[]":
                attrs["documentazione"] = str(documentazione)
            # datazione_estesa from periodizzazione_table (matched on
            # this US's periodo_iniziale + fase_iniziale).
            dat_key = (str(periodo_ini) if periodo_ini is not None else "",
                       str(fase_ini) if fase_ini is not None else "")
            dat_value = period_datazione.get(dat_key)
            if dat_value:
                attrs["datazione_estesa"] = dat_value

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
            handle = _resolve_db_handle(db_path)
            conn = handle.engine.connect()
        except Exception:
            return

        try:
            # ---- 1. EpochNodes from periodizzazione_table -------------
            # Schema columns vary slightly across pyArchInit releases;
            # we read defensively. Each (periodo, fase) is one epoch.
            epoch_by_key = {}  # (periodo:int, fase:str) -> EpochNode
            try:
                raw_rows = conn.execute(
                    text(
                        "SELECT periodo, fase, cron_iniziale, cron_finale, "
                        "descrizione FROM periodizzazione_table"
                    )
                ).fetchall()
            except Exception:
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
            except Exception:
                pass  # missing table is tolerated; epoch_count just stays 0

            # ---- 2. has_first_epoch edges and rapporti edges ----------
            # Also propagate `sito` and `area` to attributes so
            # _filter_by_site can match — the upstream PyArchInitImporter
            # mapping JSON only emits 5 columns and `sito` is not one of
            # them, leaving us_node.attributes empty post-import.
            try:
                if sito_filter is not None:
                    rows = conn.execute(
                        text(
                            "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                            "fase_iniziale, rapporti, d_stratigrafica "
                            "FROM us_table WHERE sito = :sito"
                        ),
                        {"sito": sito_filter},
                    ).fetchall()
                else:
                    rows = conn.execute(
                        text(
                            "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                            "fase_iniziale, rapporti, d_stratigrafica "
                            "FROM us_table"
                        )
                    ).fetchall()
            except Exception:
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

    def _merge_groups(self, graph, db_path, sito, dimensions,
                      primary_priority=None):
        """Materialize group nodes per dimension. AI07: dispatch per
        dimension — 6 spatial dims → LocationNodeGroup + is_in_location,
        attivita → ActivityNodeGroup + is_in_activity (unchanged).

        primary_priority: list[str] of dimension names ordered from highest
        to lowest priority for is_primary selection. None = use
        DEFAULT_PRIMARY_PRIORITY.
        """
        from .group_projector import (
            build_groups_from_sql, merge_adhoc_groups,
        )
        sql_dims = [d for d in dimensions if d != "adhoc"]
        specs = build_groups_from_sql(db_path, sito, sql_dims)

        if "adhoc" in dimensions:
            from .group_store import GroupStore
            store = GroupStore(db_path, sito)
            specs = merge_adhoc_groups(specs, store)

        # AI07: lazy import both classes from the vendored 0.1.41
        from s3dgraphy.nodes.group_node import (
            ActivityNodeGroup, LocationNodeGroup,
        )

        # Build node_uuid → node_id map (unchanged from AI06)
        node_uuid_to_id: dict = {}
        strat_by_name: dict = {}
        for n in graph.nodes:
            attrs = getattr(n, "attributes", None) or {}
            nu = attrs.get("node_uuid")
            if nu:
                node_uuid_to_id[str(nu)] = getattr(n, "node_id", None)
            if _is_us_node(n):
                strat_by_name[str(getattr(n, "name", ""))] = n
        if strat_by_name and not node_uuid_to_id:
            try:
                handle = _resolve_db_handle(db_path)
                with handle.engine.connect() as conn:
                    rows = conn.execute(
                        text(
                            "SELECT node_uuid, us FROM us_table "
                            "WHERE sito=:sito AND node_uuid IS NOT NULL"
                        ),
                        {"sito": sito},
                    ).fetchall()
                    for nu, us_val in rows:
                        if nu is None or us_val is None:
                            continue
                        node = strat_by_name.get(str(us_val))
                        if node is not None:
                            node_uuid_to_id[str(nu)] = node.node_id
            except Exception:
                pass

        # AI07: gather all memberships first, so compute_primary has the
        # full picture per US before any edge is added.
        memberships: list = []  # {us_id, group_uuid, group_kind, ...}
        existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}

        for spec in specs:
            if spec.group_uuid in existing_ids:
                continue  # idempotent

            # Dispatch class per spec
            if spec.node_class == "LocationNodeGroup":
                node = LocationNodeGroup(
                    node_id=spec.group_uuid,
                    name=spec.name,
                    kind=spec.kind or "functional",  # defensive default
                    description=spec.description or "",
                )
                edge_type = "is_in_location"
            else:
                node = ActivityNodeGroup(
                    node_id=spec.group_uuid,
                    name=spec.name,
                    description=spec.description or "",
                )
                edge_type = "is_in_activity"

            # Carry pyarchinit metadata as attributes (round-trip)
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

            # Collect memberships for compute_primary
            for us_uuid in spec.member_us_uuids:
                src_id = node_uuid_to_id.get(str(us_uuid), us_uuid)
                memberships.append({
                    "us_id": src_id,
                    "group_uuid": spec.group_uuid,
                    "group_kind": spec.group_kind,
                    "edge_type": edge_type,
                    "us_uuid": us_uuid,
                })

        # AI07: compute is_primary per US using priority order
        priority = primary_priority or DEFAULT_PRIMARY_PRIORITY
        primaries: dict = compute_primary(memberships, priority)

        # Materialize edges with is_primary attribute
        for m in memberships:
            edge_id = f"grp_{m['us_uuid']}_{m['group_uuid']}"
            is_primary = primaries.get(m["us_id"]) == m["group_uuid"]
            try:
                edge = graph.add_edge(
                    edge_id=edge_id,
                    edge_source=m["us_id"],
                    edge_target=m["group_uuid"],
                    edge_type=m["edge_type"],
                )
                # Stamp is_primary on the edge attributes (post-construction:
                # s3dgraphy.Graph.add_edge has no attributes kwarg in 0.1.41).
                if edge is not None:
                    if getattr(edge, "attributes", None) is None:
                        edge.attributes = {}
                    edge.attributes["is_primary"] = is_primary
            except ValueError as e:
                # Connection-rule rejection or duplicate edge_id — log and skip.
                logging.getLogger(__name__).debug(
                    "_merge_groups: skipping edge %s (%s)", edge_id, e
                )


    def _emit_toponym_chain(self, graph, db_path, sito):
        """AI07 Stage 3: emit a recursive LocationNodeGroup(kind='toponym')
        chain from site_table.{nazione,regione,provincia,comune}.

        Empty levels are skipped (Q4=c). If all 4 levels are empty, no
        chain is emitted.

        Cross-site dedupe: each (name, "toponym") pair maps to a
        deterministic group_uuid (sha1) so two sites in the same comune
        share the node.

        Each US in the projected graph gets one is_in_location edge to
        the DEEPEST non-empty level (typically `comune`), always
        is_primary=false (toponym never primary).

        The chain itself is structured top-down via is_in_location edges:
        nazione ← regione ← provincia ← comune (each lower level
        "is_in_location" of the next level up).
        """
        import hashlib
        try:
            handle = _resolve_db_handle(db_path)
            with handle.engine.connect() as conn:
                row = conn.execute(
                    text(
                        "SELECT nazione, regione, provincia, comune "
                        "FROM site_table WHERE sito=:sito"
                    ),
                    {"sito": sito},
                ).fetchone()
        except Exception as e:
            logging.getLogger(__name__).info(
                "_emit_toponym_chain: site_table not accessible (%s); "
                "skipping toponym chain",
                e,
            )
            return
        if row is None:
            logging.getLogger(__name__).info(
                "_emit_toponym_chain: sito '%s' not in site_table; "
                "skipping toponym chain",
                sito,
            )
            return

        levels: list = []  # (level_name, value)
        for col_idx, col_name in enumerate(
            ("nazione", "regione", "provincia", "comune")
        ):
            v = row[col_idx]
            if v is not None and str(v).strip():
                levels.append((col_name, str(v).strip()))

        if not levels:
            logging.getLogger(__name__).info(
                "_emit_toponym_chain: all admin levels empty for sito '%s'; "
                "skipping toponym chain",
                sito,
            )
            return

        # Lazy import (vendored 0.1.41)
        from s3dgraphy.nodes.group_node import LocationNodeGroup

        def _toponym_uuid(name: str) -> str:
            return hashlib.sha1(f"{name}|toponym".encode()).hexdigest()[:32]

        existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}

        # Get-or-create each level
        level_uuids: list = []
        for level_name, value in levels:
            uid = _toponym_uuid(value)
            level_uuids.append(uid)
            if uid in existing_ids:
                continue  # cross-site dedupe — already there
            node = LocationNodeGroup(
                node_id=uid,
                name=value,
                kind="toponym",
                description=f"Administrative level: {level_name}",
            )
            node.attributes = {
                "group_kind": "toponym",
                "level": level_name,
                "name": value,
                "group_uuid": uid,
            }
            graph.add_node(node)
            existing_ids.add(uid)

        # Chain edges: lower → upper (deeper → broader)
        # comune is_in_location provincia, provincia is_in_location regione, ...
        for lower_idx in range(len(level_uuids) - 1, 0, -1):
            lower = level_uuids[lower_idx]
            upper = level_uuids[lower_idx - 1]
            edge_id = f"chain_{lower}_{upper}"
            try:
                edge = graph.add_edge(
                    edge_id=edge_id,
                    edge_source=lower,
                    edge_target=upper,
                    edge_type="is_in_location",
                )
                # Stamp is_primary=False on the edge attributes
                if edge is not None:
                    if getattr(edge, "attributes", None) is None:
                        edge.attributes = {}
                    edge.attributes["is_primary"] = False
            except ValueError as e:
                logging.getLogger(__name__).debug(
                    "_emit_toponym_chain: skipping edge %s (%s)", edge_id, e
                )

        # US edges: each US connects to the DEEPEST level (last in `levels`)
        deepest_uuid = level_uuids[-1]
        us_nodes = [n for n in graph.nodes if _is_us_node(n)]
        for us in us_nodes:
            edge_id = f"top_{us.node_id}_{deepest_uuid}"
            try:
                edge = graph.add_edge(
                    edge_id=edge_id,
                    edge_source=us.node_id,
                    edge_target=deepest_uuid,
                    edge_type="is_in_location",
                )
                if edge is not None:
                    if getattr(edge, "attributes", None) is None:
                        edge.attributes = {}
                    edge.attributes["is_primary"] = False
            except ValueError as e:
                logging.getLogger(__name__).debug(
                    "_emit_toponym_chain: skipping edge %s (%s)", edge_id, e
                )


def _is_epoch_node(node) -> bool:
    """Return True if node is an EpochNode. Defensive — avoids importing
    EpochNode at module top because it forces s3dgraphy load too early."""
    return type(node).__name__ == "EpochNode"
