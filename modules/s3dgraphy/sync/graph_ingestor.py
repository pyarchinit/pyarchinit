"""Bridge from a s3dgraphy Graph back to the PyArchInit SQL tables.

This module hosts the public `GraphIngestor` class (Group C onwards)
and the full exception hierarchy used by both the projector and the
ingestor. All ingestion is atomic (single BEGIN/COMMIT/ROLLBACK).
"""
from __future__ import annotations

from typing import Iterable

# ---------------------------------------------------------------------------
# Mapped columns — the subset of us_table columns the s3dgraphy bridge
# round-trips. Composed of the columns covered by
# pyarchinit_us_mapping.json (5) + the columns added by
# `_enrich_pyarchinit_graph` in graphml_writer.py (7). Anything else
# in us_table (descrizione, foto, profondita, …) is preserved by
# UPDATE selettivo and never overwritten.
# ---------------------------------------------------------------------------
MAPPED_COLUMNS: tuple[str, ...] = (
    # From pyarchinit_us_mapping.json
    "us",
    "d_stratigrafica",
    "d_interpretativa",
    "attivita",
    "struttura",
    # Added by _enrich_pyarchinit_graph
    "sito",
    "area",
    "unita_tipo",
    "periodo_iniziale",
    "fase_iniziale",
    "rapporti",
    "node_uuid",
    # AI04.1: DOC nodes carry a URL/path in s3dgraphy DocumentNode.url
    # → us_table.documentazione (#6 H.4 fix).
    "documentazione",
)


# ---------------------------------------------------------------------------
# Exception hierarchy (spec §5.1)
# ---------------------------------------------------------------------------
class GraphSyncError(Exception):
    """Base class for all GraphProjector / GraphIngestor errors."""


class GraphIngestError(GraphSyncError):
    """Write-side failure. Always means DB rolled back to pre-call state."""


class SchemaMismatchError(GraphIngestError):
    """us_table.node_uuid column missing (Phase 1 migration not applied).

    Hint: run scripts/migrations/2026_05_node_uuid_backfill.py --apply.
    """


class UnknownUnitaTipoError(GraphIngestError):
    """Graph node has unita_tipo not in the vocabulary.

    Hint: run scripts/migrations/2026_05_us_vocabulary_alignment.py --apply.
    """


class SiteMismatchError(GraphIngestError):
    """Graph contains a node whose attributes['sito'] != populate_list(sito=...)."""


class MissingEpochError(GraphIngestError):
    """One or more EpochNodes reference (periodo, fase) not present in
    periodizzazione_table while create_missing_epochs=False.

    The exception carries `missing: list[tuple[int, str]]` so callers
    can show all the missing keys at once instead of one per call.
    """
    def __init__(self, missing: Iterable[tuple]) -> None:
        self.missing = list(missing)
        super().__init__(
            f"Missing periodizzazione_table rows for: {self.missing}. "
            f"Run with create_missing_epochs=True to auto-create."
        )


# ---------------------------------------------------------------------------
# GraphIngestor (Groups C–D)
# ---------------------------------------------------------------------------
import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from .conflict_resolver import ConflictResolver
from .ingest_result import (
    ConflictRecord, ConflictResolution, IngestResult)

if TYPE_CHECKING:
    import s3dgraphy

log = logging.getLogger("modules.s3dgraphy.sync.graph_ingestor")


class GraphIngestor:
    """Persist a s3dgraphy Graph back to the PyArchInit SQL tables.

    Single atomic transaction (BEGIN/COMMIT/ROLLBACK). Idempotent on
    re-runs against the same input. AI04 always uses
    ConflictResolution.GRAPH_WINS for value diffs.
    """

    def __init__(self, conflict_resolver: ConflictResolver | None = None) -> None:
        self._resolver = conflict_resolver or ConflictResolver()

    def populate_list(
        self,
        graph: "s3dgraphy.Graph",
        db_path: Path,
        sito: str,
        *,
        dry_run: bool = False,
        create_missing_epochs: bool = False,
        graphml_path: Path | str | None = None,
    ) -> IngestResult:
        """See spec §3.2 docstring for full contract.

        When *graphml_path* is provided, AI04's custom data-keys
        (`pyarchinit.us`, `pyarchinit.area`, etc. — see
        graphml_writer._embed_pyarchinit_data_keys) are parsed from
        the file and merged into graph node attributes, so the
        round-trip preserves columns that s3dgraphy's own importer
        would otherwise drop.
        """
        db_path = Path(db_path)
        # 1. Sito parameter must be non-empty (cheap check, do first
        # so we fail fast even when db_path is invalid).
        self._verify_sito(graph, sito)
        if graphml_path is not None:
            try:
                _hydrate_pyarchinit_data_keys(graph, Path(graphml_path))
            except Exception:
                # Defensive: if hydration fails, the graph still has
                # whatever attributes the s3dgraphy importer preserved.
                pass
        # 2. Schema check
        self._verify_schema(db_path)
        # 3. Run the actual ingestion (Group C: dry-run only)
        return self._run(graph, db_path, sito,
                         dry_run=dry_run,
                         create_missing_epochs=create_missing_epochs)

    # ------------------------------------------------------------------ helpers
    def _verify_schema(self, db_path: Path) -> None:
        if not db_path.exists():
            raise GraphIngestError(f"DB file not found: {db_path}")
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise GraphIngestError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise SchemaMismatchError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")

    def _verify_sito(self, graph, sito: str) -> None:
        """Validate the sito parameter.

        Note: AI04.1 changed semantics — we no longer raise on graph
        nodes carrying a different sito. The user's workflow is "load
        this graph and ingest into MY sito X", so we treat the
        parameter as authoritative. The per-node loop overrides each
        node's sito attribute to *sito* before INSERT/UPDATE.
        """
        if not sito:
            raise SiteMismatchError(
                "sito parameter is mandatory; AI04 only supports "
                "single-site graphs.")

    def _run(self, graph, db_path, sito, *, dry_run, create_missing_epochs):
        inserted = updated = skipped = 0
        epochs_created = 0
        sito_created = False
        conflicts: list[ConflictRecord] = []
        errors: list[str] = []

        # Pre-compute per-source rapporti from graph edges so the write
        # path can populate us_table.rapporti as JSON-list-of-lists.
        rapporti_by_source = _build_rapporti_from_edges(graph, sito)

        # Open the transaction (we always use BEGIN even in dry-run so
        # any side effects from other code paths get isolated and
        # ROLLBACK'd).
        conn = sqlite3.connect(str(db_path))
        conn.execute("BEGIN")
        try:
            cur = conn.cursor()
            # Ensure site_table has a row for `sito` — create if missing.
            cur.execute(
                "SELECT COUNT(*) FROM site_table WHERE sito = ?", (sito,))
            if cur.fetchone()[0] == 0:
                if not dry_run:
                    cur.execute(
                        "INSERT INTO site_table (sito, nazione, regione, "
                        "definizione_sito) VALUES (?, '', '', "
                        "'auto-created by AI04 import')",
                        (sito,),
                    )
                sito_created = True
            for node in graph.nodes:
                # Skip wrapper / metadata node types that have no SQL
                # counterpart in us_table (PropertyNode etc. land in
                # paradata.graphml under AI05; GeoPositionNode and
                # ParadataNodeGroup are layout-only; EpochNode is
                # handled in its own loop below).
                type_name = type(node).__name__
                if type_name in _NON_STRAT_TYPES:
                    continue
                attrs = dict(getattr(node, "attributes", None) or {})
                # Look up by node_uuid. Prefer the explicit attribute
                # (set by GraphProjector._propagate_node_uuid_and_us);
                # fall back to node_id when the graph was built outside
                # the projector and node_id IS the DB uuid.
                node_uuid = attrs.get("node_uuid") or getattr(
                    node, "node_id", None)
                if not node_uuid:
                    continue
                # Make sure the node carries a `us` value. Priority:
                #   1. attrs["us"] (set by GraphProjector)
                #   2. node.name with prefix stripped (graphml-imported)
                # Examples of stripping:
                #   "USM6"   → "6"
                #   "USV102" → "102"
                #   "US103a" → "103a"  (us column is TEXT)
                if "us" not in attrs or attrs["us"] is None:
                    fallback_us = getattr(node, "name", None)
                    if not fallback_us:
                        continue
                    attrs["us"] = _strip_us_prefix(str(fallback_us))
                # Always force sito to the populate_list parameter so
                # the user can import a graph (made for ANY sito) into
                # the chosen target sito (#3 H.4 fix).
                attrs["sito"] = sito
                # unita_tipo is best resolved from the s3dgraphy class
                # name when attrs has lost it via round-trip.
                if "unita_tipo" not in attrs or attrs["unita_tipo"] is None:
                    resolved_tipo = _resolve_unita_tipo(node, attrs)
                    if resolved_tipo:
                        attrs["unita_tipo"] = resolved_tipo
                # DocumentNode: stash its `url` field into the
                # documentazione column (#6 H.4 fix). Path is typically
                # relative, e.g. "documents/scheda_1.pdf".
                if (type_name == "DocumentNode"
                        and not attrs.get("documentazione")):
                    doc_url = (getattr(node, "url", None)
                               or attrs.get("url"))
                    if doc_url:
                        attrs["documentazione"] = str(doc_url)
                cur.execute(
                    "SELECT * FROM us_table WHERE node_uuid = ?",
                    (node_uuid,),
                )
                row = cur.fetchone()
                if row is None:
                    inserted += 1
                    continue
                # Build {col: db_val} dict from row + cursor.description
                col_names = [d[0] for d in cur.description]
                db_row = dict(zip(col_names, row))
                row_changed = False
                for col in MAPPED_COLUMNS:
                    if col not in attrs:
                        continue
                    db_val = db_row.get(col)
                    graph_val = attrs.get(col)
                    if _values_equal(col, db_val, graph_val):
                        continue
                    row_changed = True
                    self._resolver.resolve(
                        db_row=db_row, graph_value=graph_val, field=col)
                    conflicts.append(ConflictRecord(
                        node_uuid=node_uuid, field=col,
                        db_value=db_val, graph_value=graph_val,
                        resolution=ConflictResolution.GRAPH_WINS.value,
                    ))
                if row_changed:
                    updated += 1
                else:
                    skipped += 1

            # ---- EpochNode loop ----
            # Read existing (periodo, fase) pairs FOR THIS SITO. The
            # UNIQUE constraint on periodizzazione_table is
            # (sito, periodo, fase) so the same period/phase combo
            # can legitimately exist for a different site.
            cur.execute(
                "SELECT CAST(periodo AS TEXT), CAST(fase AS TEXT) "
                "FROM periodizzazione_table WHERE sito = ?",
                (sito,))
            existing_epochs = {(r[0], r[1]) for r in cur.fetchall()}
            missing_epochs: list[tuple] = []
            for node in graph.nodes:
                if not _is_epoch_node_local(node):
                    continue
                attrs = getattr(node, "attributes", None) or {}
                periodo = attrs.get("periodo")
                fase = attrs.get("fase")
                if periodo is None:
                    continue
                key = (str(periodo), str(fase) if fase is not None else "")
                if key in existing_epochs:
                    continue
                if create_missing_epochs:
                    epochs_created += 1
                    # Group D writes the actual INSERT here. For dry-run, just count.
                else:
                    # Coerce periodo back to int for the error payload
                    try:
                        p_int = int(periodo)
                    except (TypeError, ValueError):
                        p_int = periodo
                    missing_epochs.append((p_int, str(fase)))
            if missing_epochs:
                # rollback now and let the outer except GraphSyncError
                # branch re-raise (it also calls rollback, which is a
                # no-op once the transaction is already rolled back).
                raise MissingEpochError(missing=missing_epochs)

            # ---- Write block (Group D): INSERT new rows + UPDATE existing ----
            # In dry-run mode, this loop is skipped entirely and the
            # transaction is rolled back below. In write mode, we re-walk
            # graph.nodes to replay the same decisions made in the
            # detection loop above, this time issuing actual SQL writes.
            applied = 0
            if not dry_run:
                for node in graph.nodes:
                    type_name = type(node).__name__
                    if type_name in _NON_STRAT_TYPES:
                        continue
                    attrs = dict(getattr(node, "attributes", None) or {})
                    # Same priority as the detection loop above:
                    # explicit attrs.node_uuid wins (projector-built graphs),
                    # node_id is the fallback (graphs built outside the
                    # projector where node_id IS the DB uuid).
                    node_uuid = attrs.get("node_uuid") or getattr(
                        node, "node_id", None)
                    if not node_uuid:
                        continue
                    if "us" not in attrs or attrs["us"] is None:
                        fallback_us = getattr(node, "name", None)
                        if not fallback_us:
                            continue
                        attrs["us"] = _strip_us_prefix(str(fallback_us))
                    # Force sito to parameter (override anything the
                    # graph carried — the user's choice is authoritative).
                    attrs["sito"] = sito
                    if ("unita_tipo" not in attrs
                            or attrs["unita_tipo"] is None):
                        resolved_tipo = _resolve_unita_tipo(node, attrs)
                        if resolved_tipo:
                            attrs["unita_tipo"] = resolved_tipo
                    if (type_name == "DocumentNode"
                            and not attrs.get("documentazione")):
                        doc_url = (getattr(node, "url", None)
                                   or attrs.get("url"))
                        if doc_url:
                            attrs["documentazione"] = str(doc_url)
                    # area is part of the UNIQUE constraint
                    # (sito, area, us, unita_tipo) — default to "1"
                    # if the graph doesn't carry it.
                    if "area" not in attrs or attrs["area"] is None:
                        attrs["area"] = "1"
                    # rapporti from edges (#4): walk graph edges grouped
                    # by source node_id and serialise as the pyarchinit
                    # list-of-lists format. Edges-derived takes priority
                    # over a graphml-hydrated rapporti string because
                    # the latter may carry the SOURCE sito (e.g.
                    # "TestSite") which we want overridden to the
                    # target sito.
                    if node_uuid in rapporti_by_source:
                        attrs["rapporti"] = str(
                            rapporti_by_source[node_uuid])
                    elif "rapporti" in attrs and attrs["rapporti"]:
                        # Hydrated string — rewrite the sito in each
                        # rapporto to the target sito.
                        attrs["rapporti"] = _rewrite_rapporti_sito(
                            attrs["rapporti"], sito)
                    # periodizzazione from has_first_epoch edges (#5).
                    p_iniz, f_iniz = _find_first_epoch(
                        graph, node_uuid)
                    if p_iniz is not None and (
                            "periodo_iniziale" not in attrs
                            or not attrs["periodo_iniziale"]):
                        attrs["periodo_iniziale"] = str(p_iniz)
                    if f_iniz is not None and (
                            "fase_iniziale" not in attrs
                            or not attrs["fase_iniziale"]):
                        attrs["fase_iniziale"] = str(f_iniz)
                    cur.execute(
                        "SELECT * FROM us_table WHERE node_uuid = ?",
                        (node_uuid,),
                    )
                    existing = cur.fetchone()
                    col_payload = {col: attrs.get(col)
                                   for col in MAPPED_COLUMNS
                                   if col in attrs}
                    col_payload["node_uuid"] = node_uuid
                    col_payload["sito"] = sito
                    if existing is None:
                        # INSERT
                        cols = list(col_payload.keys())
                        placeholders = ",".join("?" for _ in cols)
                        col_list = ",".join(cols)
                        cur.execute(
                            f"INSERT INTO us_table ({col_list}) VALUES "
                            f"({placeholders})",
                            [col_payload[c] for c in cols],
                        )
                        applied += 1
                    else:
                        # UPDATE selettivo: only the MAPPED_COLUMNS that
                        # actually differ. Any column not in attrs and
                        # any us_table column not in MAPPED_COLUMNS is
                        # left untouched (preserves descrizione, foto,
                        # etc.).
                        col_names = [d[0] for d in cur.description]
                        db_row = dict(zip(col_names, existing))
                        diff_cols = []
                        diff_vals = []
                        for col in MAPPED_COLUMNS:
                            if col not in attrs:
                                continue
                            if _values_equal(col, db_row.get(col),
                                              attrs.get(col)):
                                continue
                            diff_cols.append(col)
                            diff_vals.append(attrs.get(col))
                        if diff_cols:
                            set_clause = ", ".join(
                                f"{c} = ?" for c in diff_cols)
                            cur.execute(
                                f"UPDATE us_table SET {set_clause} "
                                f"WHERE node_uuid = ?",
                                [*diff_vals, node_uuid],
                            )
                            applied += 1

                # Epoch INSERT (D5-B path, write mode only).
                # Populate cron_iniziale/cron_finale and datazione when
                # the EpochNode carries them. start_time/end_time are
                # numeric (year), datazione is the human label.
                if create_missing_epochs:
                    for node in graph.nodes:
                        if not _is_epoch_node_local(node):
                            continue
                        eattrs = getattr(node, "attributes", None) or {}
                        periodo = eattrs.get("periodo")
                        fase = eattrs.get("fase")
                        # Fall back to parsing from node_id when attrs
                        # are stripped by the importer.
                        if periodo is None:
                            tid = getattr(node, "node_id", "") or ""
                            m = _re.match(
                                r"^epoch_([^_]+)_(.+?)(_synthetic)?$",
                                str(tid))
                            if m:
                                periodo, fase = m.group(1), m.group(2)
                        if periodo is None:
                            continue
                        ekey = (str(periodo),
                                str(fase) if fase is not None else "")
                        if ekey in existing_epochs:
                            continue
                        descrizione = getattr(node, "name", "") or ""
                        cron_ini = getattr(node, "start_time", None)
                        cron_fin = getattr(node, "end_time", None)
                        # cron columns are INTEGER in pyarchinit
                        cron_ini_i = (int(cron_ini)
                                      if cron_ini not in (None, 0, 0.0)
                                      else None)
                        cron_fin_i = (int(cron_fin)
                                      if cron_fin not in (None, 0, 0.0)
                                      else None)
                        # datazione_estesa: free-text human label,
                        # often the epoch name for external graphs.
                        datazione = (eattrs.get("datazione")
                                     or eattrs.get("datazione_estesa")
                                     or descrizione)
                        # The UNIQUE constraint on periodizzazione_table
                        # is (sito, periodo, fase), so populate sito.
                        try:
                            periodo_i = int(periodo)
                        except (TypeError, ValueError):
                            periodo_i = None
                        cur.execute(
                            "INSERT INTO periodizzazione_table "
                            "(sito, periodo, fase, descrizione, "
                            " cron_iniziale, cron_finale, "
                            " datazione_estesa) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (sito, periodo_i, fase, descrizione,
                             cron_ini_i, cron_fin_i, datazione),
                        )

            # Commit or rollback
            if dry_run:
                conn.rollback()
            else:
                conn.commit()
        except GraphSyncError:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise GraphIngestError(f"Ingest failed: {e}") from e
        finally:
            conn.close()

        return IngestResult(
            applied=applied,
            inserted=inserted, updated=updated, skipped=skipped,
            epochs_created=epochs_created,
            conflicts=tuple(conflicts), errors=tuple(errors),
            dry_run=dry_run,
        )


def _values_equal(col: str, a, b) -> bool:
    """Loose equality matching the conventions in graphml_writer
    enrichment. JSON-serialised columns (rapporti) get parse-then-compare."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if col == "rapporti":
        try:
            import ast
            return ast.literal_eval(str(a)) == ast.literal_eval(str(b))
        except (ValueError, SyntaxError):
            return str(a) == str(b)
    return str(a) == str(b)


def _is_epoch_node_local(node) -> bool:
    return type(node).__name__ == "EpochNode"


# Inverse mapping of `_RAPPORTI_TO_EDGE_TYPE` from graphml_writer.py:
# convert s3dgraphy edge_type back to the Italian rapporti label that
# pyarchinit stores in us_table.rapporti.
_EDGE_TYPE_TO_RAPPORTI_IT: dict[str, str] = {
    "overlies": "Copre",
    "is_overlain_by": "Coperto da",
    "cuts": "Taglia",
    "is_cut_by": "Tagliato da",
    "fills": "Riempie",
    "is_filled_by": "Riempito da",
    "is_physically_equal_to": "Uguale a",
    "is_bonded_to": "Si lega a",
    "abuts": "Si appoggia a",
    "is_abutted_by": "Gli si appoggia",
    "is_after": "Copre",       # default fallback for temporal precedence
    "generic_connection": "Connesso a",
}


def _hydrate_pyarchinit_data_keys(graph, graphml_path: Path) -> None:
    """Re-parse the GraphML at *graphml_path* via lxml and merge the
    pyarchinit-specific data keys (`pyarchinit.us`, `pyarchinit.area`,
    `pyarchinit.unita_tipo`, etc.) into graph node attributes.

    This is the IMPORT-side counterpart of
    graphml_writer._embed_pyarchinit_data_keys. s3dgraphy's
    GraphMLImporter strips unknown attributes; we recover the
    pyarchinit-specific ones by reading the same XML directly.

    No-op if the GraphML doesn't contain our custom data keys (older
    files / files from non-pyarchinit producers).
    """
    try:
        from lxml import etree
    except ImportError:
        return

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    parser = etree.XMLParser(remove_blank_text=False)
    try:
        tree = etree.parse(str(graphml_path), parser)
    except Exception:
        return
    root = tree.getroot()

    # Build keyid → attr_name index for any key whose attr.name
    # starts with 'pyarchinit.'.
    key_id_to_attr: dict[str, str] = {}
    epochs_meta_kid = None
    for k in root.findall(f"{{{NS_GRAPHML}}}key"):
        attr_named = k.get("attr.name") or ""
        if not attr_named.startswith("pyarchinit."):
            continue
        kid = k.get("id")
        if not kid:
            continue
        if attr_named == "pyarchinit.epochs_meta":
            epochs_meta_kid = kid
            continue
        key_id_to_attr[kid] = attr_named[len("pyarchinit."):]

    # Hydrate EpochNodes from the graph-level JSON blob (#5 H.4 fix).
    if epochs_meta_kid:
        graph_el = root.find(f"{{{NS_GRAPHML}}}graph")
        if graph_el is not None:
            for d_el in graph_el.findall(f"{{{NS_GRAPHML}}}data"):
                if d_el.get("key") != epochs_meta_kid:
                    continue
                try:
                    import json as _json
                    epoch_meta_list = _json.loads(d_el.text or "[]")
                except (ValueError, TypeError):
                    epoch_meta_list = []
                for meta in epoch_meta_list:
                    name = meta.get("name", "")
                    if not name:
                        continue
                    # Find the EpochNode in graph.nodes with same name
                    for n in graph.nodes:
                        if (type(n).__name__ == "EpochNode"
                                and getattr(n, "name", "") == name):
                            attrs = getattr(n, "attributes", None)
                            if attrs is None:
                                try:
                                    n.attributes = {}
                                    attrs = n.attributes
                                except Exception:
                                    continue
                            for key in ("periodo", "fase", "cron_iniziale",
                                        "cron_finale", "datazione_estesa"):
                                if (key in meta
                                        and not attrs.get(key)):
                                    attrs[key] = meta[key]
                            break
                break

    if not key_id_to_attr:
        return

    # Build EMID → graph node lookup
    emid_to_node = {}
    for n in graph.nodes:
        emid = getattr(n, "node_id", None)
        if emid:
            emid_to_node[emid] = n
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
        attrs = getattr(n, "attributes", None)
        if attrs is None:
            try:
                n.attributes = {}
                attrs = n.attributes
            except Exception:
                continue
        for d_el in node_el.findall(f"{{{NS_GRAPHML}}}data"):
            kid = d_el.get("key")
            if kid not in key_id_to_attr:
                continue
            val = (d_el.text or "").strip()
            if val == "":
                continue
            attr_name = key_id_to_attr[kid]
            # Don't overwrite existing attr unless empty
            if attrs.get(attr_name) in (None, ""):
                attrs[attr_name] = val


def _find_first_epoch(graph, node_uuid: str) -> tuple:
    """Walk has_first_epoch edges from *node_uuid* and return the
    `(periodo, fase)` tuple of the linked EpochNode, or `(None, None)`.

    s3dgraphy's GraphMLImporter strips most attributes but preserves
    edge `edge_type`. The EpochNode keeps `node.name` (e.g. "XV secolo")
    and any `attributes['periodo']` / `attributes['fase']` set by the
    projector. When attrs are stripped, fall back to parsing from
    EpochNode.node_id (which the projector formats as
    `epoch_<periodo>_<fase>`).
    """
    by_id = {}
    for n in graph.nodes:
        nid = getattr(n, "node_id", None)
        if nid:
            by_id[nid] = n
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) != "has_first_epoch":
            continue
        if getattr(e, "edge_source", None) != node_uuid:
            continue
        target = by_id.get(getattr(e, "edge_target", None))
        if target is None or not _is_epoch_node_local(target):
            continue
        attrs = getattr(target, "attributes", None) or {}
        periodo = attrs.get("periodo")
        fase = attrs.get("fase")
        if periodo is None:
            # Fall back to parsing the node_id format
            tid = getattr(target, "node_id", "") or ""
            m = _re.match(r"^epoch_([^_]+)_(.+?)(_synthetic)?$", str(tid))
            if m:
                periodo, fase = m.group(1), m.group(2)
        return periodo, fase
    return None, None


def _rewrite_rapporti_sito(rapporti_str: str, target_sito: str) -> str:
    """Parse a pyarchinit rapporti list-of-lists string and rewrite
    the sito (4th element of each rapporto) to *target_sito*. Returns
    the re-serialised string. Defensive — returns the input unchanged
    if parsing fails."""
    if not rapporti_str:
        return rapporti_str
    try:
        import ast
        data = ast.literal_eval(str(rapporti_str))
    except (ValueError, SyntaxError):
        return rapporti_str
    if not isinstance(data, list):
        return rapporti_str
    out = []
    for item in data:
        if isinstance(item, list) and len(item) >= 4:
            new_item = list(item)
            new_item[3] = target_sito
            out.append(new_item)
        else:
            out.append(item)
    return str(out)


def _build_rapporti_from_edges(graph, default_sito: str) -> dict:
    """Walk graph.edges and return a dict {source_node_id: rapporti_list}
    where each rapporti_list is the pyarchinit list-of-lists serialisation
    `[[type, target_us, area, sito], …]`.

    The `target_us` is extracted from the target node's name with the
    unita_tipo prefix stripped. `area` defaults to '1' when the graph
    didn't preserve it (compatible with most legacy pyarchinit data).
    """
    # Index nodes by id for fast lookup
    by_id = {}
    for n in graph.nodes:
        nid = getattr(n, "node_id", None)
        if nid:
            by_id[nid] = n
    out: dict[str, list[list]] = {}
    for e in getattr(graph, "edges", None) or []:
        src = getattr(e, "edge_source", None)
        tgt = getattr(e, "edge_target", None)
        et = getattr(e, "edge_type", None)
        if not src or not tgt or not et:
            continue
        # Skip non-stratigraphic relationships (e.g. has_first_epoch
        # connects US → EpochNode; has_paradata_nodegroup connects US →
        # PD wrapper). Only is_after/cuts/abuts/etc. become rapporti.
        if et in ("has_first_epoch", "has_paradata_nodegroup",
                  "has_property", "extracted_from", "combines",
                  "survive_in_epoch", "has_same_time"):
            continue
        rapporti_label = _EDGE_TYPE_TO_RAPPORTI_IT.get(et, str(et))
        # Resolve target's us value
        tgt_node = by_id.get(tgt)
        if tgt_node is None:
            continue
        tgt_attrs = getattr(tgt_node, "attributes", None) or {}
        tgt_us = tgt_attrs.get("us")
        if not tgt_us:
            tgt_name = getattr(tgt_node, "name", None)
            if not tgt_name:
                continue
            tgt_us = _strip_us_prefix(str(tgt_name))
        tgt_area = str(tgt_attrs.get("area") or "1")
        # Always use the target sito (caller's choice) rather than
        # whatever the graph carried — this matches the
        # "import to a NEW sito" workflow.
        tgt_sito = default_sito
        rapporto = [rapporti_label, str(tgt_us), tgt_area, tgt_sito]
        # Dedup: pyarchinit `tred` already runs in AI03 export but
        # external graphml may carry duplicate edges for the same
        # (label, target). Drop duplicates here so us_table.rapporti
        # stays clean.
        bucket = out.setdefault(src, [])
        if rapporto not in bucket:
            bucket.append(rapporto)
    return out


# Map s3dgraphy class names to pyarchinit `unita_tipo` codes.
# When a graphml round-trip strips attribute metadata, the only
# semantic info that survives is the s3dgraphy node CLASS name —
# we use it to recover unita_tipo.
_S3DGRAPHY_TYPE_TO_UNITA_TIPO: dict[str, str] = {
    "StratigraphicUnit": "US",
    "StructuralVirtualStratigraphicUnit": "USVs",
    "VirtualStratigraphicStructuralUnit": "USVs",
    "VirtualStratigraphicNonStructuralUnit": "USVn",
    "NonStructuralVirtualStratigraphicUnit": "USVn",
    "StratigraphicUnitMasonry": "USM",
    "DocumentaryStratigraphicUnit": "USD",
    "SpecialFindUnit": "SF",
    "VirtualSpecialFindUnit": "VSF",
    "TransformationStratigraphicUnit": "TSU",
    "WorkingUnit": "UL",
    "ContinuityNode": "CON",
    "DocumentNode": "DOC",
    "ExtractorNode": "Extractor",
    "CombinerNode": "Combinar",
}


# Multilingual prefix-strip regex. Pyarchinit displays US labels with
# language-aware prefixes (US/SU/SE/UE/...), USM/WSU/MSE/..., USVs/USVn
# both rendered as "USV<n>", SF/VSF, CON, D./C. for paradata.
# We strip ANY of these prefixes (longest match first) and return
# whatever remains (which is the bare us identifier — text, e.g.
# "6", "102", "103a").
import re as _re

_US_PREFIX_PATTERN = _re.compile(
    r"^(?P<prefix>"
    r"USVs|USVn|USVA|USVB|USVC|USV|"
    r"USM|USD|USN|"
    r"VSF|SF|"
    r"CON|"
    r"WSU|MSE|TSU|SUS|UE|UM|UC|UL|"
    r"D\.|C\.|"
    r"US|SU|SE"
    r")\s*",
    _re.IGNORECASE,
)


def _strip_us_prefix(name: str) -> str:
    """Strip the unita-tipo prefix from a node name.

    Examples:
        "USM6"   → "6"
        "USV102" → "102"
        "US103a" → "103a"
        "D.4001" → "4001"
        "C.900"  → "900"
        "6"      → "6"  (no prefix → unchanged)
    """
    if not name:
        return name
    m = _US_PREFIX_PATTERN.match(str(name))
    if m:
        return str(name)[m.end():]
    return str(name)


def _resolve_unita_tipo(node, attrs: dict) -> str | None:
    """Return the unita_tipo for *node*, prefering attrs (set by
    GraphProjector) over s3dgraphy class name (when graphml round-trip
    has stripped attrs)."""
    if attrs.get("unita_tipo"):
        return str(attrs["unita_tipo"])
    type_name = type(node).__name__
    return _S3DGRAPHY_TYPE_TO_UNITA_TIPO.get(type_name)


# Node types that have no us_table counterpart and must be skipped by
# the per-node loop. EpochNode is in its own loop and intentionally
# excluded from this set so the EpochNode branch can still see it.
# Note: DocumentNode is INCLUDED in the per-node loop (us_table.unita_tipo
# = 'DOC' is supported) — see #6 H.4 fix. The DocumentNode.url value is
# written to us_table.documentazione during INSERT/UPDATE.
_NON_STRAT_TYPES: frozenset[str] = frozenset({
    "EpochNode",
    "GeoPositionNode",
    "PropertyNode",
    "ParadataNodeGroup",
    "AuthorNode",
    "LicenseNode",
    "EmbargoNode",
    "ExtractorNode",
    "CombinerNode",
    "VirtualSpecialFindUnit",  # paradata-only, AI05 territory
})
