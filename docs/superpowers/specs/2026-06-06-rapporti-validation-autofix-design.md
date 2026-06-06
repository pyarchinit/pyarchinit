# Rapporti validation + conservative auto-fix + import mode — Design

**Date:** 2026-06-06
**Branch:** `Stratigraph_00001`
**Status:** design approved, pending spec review → implementation plan

## 1. Problem / context

Running s3dgraphy's validators on real pyArchInit data (khutm "Al-Khutm",
490 US, 2373 stratigraphic edges) surfaced **13 stratigraphic cycles + 3
self-loops** in the `rapporti` data — genuine Harris-matrix inconsistencies
(e.g. `605 covers 604` **and** `604 covers 605`; `670→675→686→670`; US `305`
relating to itself). s3dgraphy **has** the machinery to detect these
(`diagnostics.detect_stratigraphic_cycles`, `graph.validate_connection`,
`graph.calculate_chronology`), but it is **not wired into pyArchInit's
import/export flow**, so the errors pass silently. pyArchInit has only partial
native checks (`relashionship_check_table`, anti-direct-cycle in the
interactive matrix).

Separately, importing an exported GraphML into a **different target site**
matches existing rows **by `node_uuid`** and `_verify_sito` rewrites the
`sito` to the target → the original site is silently **renamed/moved** rather
than copied (observed: Al-Khutm → test_import). This is by-design "ingest into
site X" semantics, but surprising for "import as a new site".

## 2. Goals

- **A — Verifica rapporti:** an on-demand tool that detects rapporti
  inconsistencies (using s3dgraphy's validators) and offers an **optional,
  conservative auto-fix** with **preview, backup, and rollback**.
- **B — Import mode:** a choice between "update existing (in-place)" and
  "import as a copy (new site)" so the rename is intentional, not accidental.

Non-goals: reworking the s3dgraphy validators themselves (used as-is);
chronological-paradox UI (date coherence) — deferred.

## 3. Feature A — Verifica rapporti stratigrafici

### 3.1 Checks

| Check | Source | Notes |
|---|---|---|
| Stratigraphic cycles (multi-node) | `s3dgraphy.diagnostics.detect_stratigraphic_cycles` | the 13 cycles |
| Self-loops (US → itself) | same (1-element cycles) | 305, 550, 708 |
| Connection-type legality | `s3dgraphy.graph.Graph.validate_connection` | illegal edge type between unit types |
| Reciprocity | computed pyArchInit-side from the `rapporti` column | A "covers" B but B has no "covered by A" |

### 3.2 Fix semantics (conservative; all optional, preview + rollback)

| Class | Auto-fix? | Action |
|---|---|---|
| Self-loop | ✅ yes | remove the `[label, X, …]` entry whose target = X from X's `rapporti` (destructive but unambiguous) |
| **Missing reciprocity** | ✅ yes (**CREATE**) | **add** the inverse rapporto to the other US (e.g. A "covers" B → add "covered by A" to B). Additive/non-destructive; inverse label resolved via pyArchInit's localized `INVERSE_MAP` so it matches the site's language |
| Direct contradiction A↔B **with a consistent reciprocal already present** | ✅ yes | remove only the contradictory duplicate direction |
| Direct contradiction A↔B **without** a consistent reciprocal | ⚠️ no | show both; user chooses which to remove |
| Multi-node cycle (3+) | ⚠️ no | show the cycle + a **suggested** break-edge; user chooses which relationship to remove |

Auto-fixable classes are applied only on explicit user action, after preview.
Ambiguous classes are never modified without a per-item user choice.

### 3.3 Components (Qt-free core + Qt wrapper, matching the existing pattern)

- **`modules/s3dgraphy/sync/rapporti_check.py`** (no Qt):
  - `check_rapporti(graph) -> RapportiReport` — runs the s3dgraphy validators
    + the reciprocity scan; returns issues grouped by class, each with the
    involved US and the canonical edge.
  - `compute_fixes(report, graph) -> FixPlan` — for auto-fixable classes,
    the exact `rapporti`-column edits (per US: entries to add/remove); for
    ambiguous classes, a suggested edit flagged `needs_choice=True`.
  - `apply_fixes(plan, db_handle, selected) -> RollbackToken` — snapshots the
    affected US `rapporti` values, then writes the edits via the existing
    db layer (backend-agnostic; PG + SQLite). Returns the snapshot token.
  - `rollback(token, db_handle)` — restores the snapshotted `rapporti`.
  - The reciprocity inverse mapping is sourced from
    `modules/utility/pyarchinit_i18n_stratigraphic.INVERSE_MAP` (localized),
    injected so the core stays Qt-free.
- **`gui/rapporti_check_dialog.py`** (Qt): site picker → run check → report
  tree grouped by class → for ambiguous items a per-item choice → **preview**
  (before/after diff of each affected US `rapporti`) → **Apply** (DB backup +
  snapshot) / **Rollback**.
- Menu entry in `pyarchinitPlugin.py` (e.g. "Verifica rapporti stratigrafici").

### 3.4 Preview / backup / rollback

- **Preview:** compute the `FixPlan` and render the per-US `rapporti`
  before/after diff. **No DB write.**
- **Apply:** take a DB backup (existing auto-backup helpers) + an in-memory
  snapshot of every affected US's `rapporti`, then UPDATE.
- **Rollback:** restore the snapshot (revert the `rapporti` of the affected
  US to their pre-fix values).

## 4. Feature B — Import mode (update vs copy)

- The import dialog gains a choice:
  - **"Aggiorna esistenti (in-place)"** — current behaviour (match by
    `node_uuid`, rewrite `sito` to target). Default.
  - **"Importa come copia (nuovo sito)"** — before ingest, regenerate every
    node's `node_uuid` (fresh uuid7) so none match existing rows → all rows
    INSERT as new under the target site; the original site is untouched.
- Touches: the import dialog + a pre-ingest uuid-regeneration step in the
  ingest path (guarded by the chosen mode).

## 5. Testing

- `rapporti_check` core (no Qt, synthetic graphs):
  - self-loop → removal fix;
  - missing reciprocity → CREATE the inverse entry on the other US (correct
    localized label via INVERSE_MAP);
  - direct contradiction with/without consistent reciprocal → auto-fix vs
    needs-choice;
  - multi-node cycle → needs-choice + suggested break-edge;
  - illegal connection type → reported;
  - apply → rollback round-trip on a temp SQLite restores the original
    `rapporti` byte-for-byte.
- Import copy-mode: importing the same graph as a copy creates NEW rows
  (fresh node_uuids) under the target site without modifying the original
  site's rows.

## 6. Out of scope / follow-ups

- Chronological-paradox (date coherence) UI via `calculate_chronology`.
- Upstreaming a convenience `validate_graph()` aggregator to s3dgraphy.
- Wiring the check automatically into export/import (this iteration is
  on-demand only).

## 7. Related

- s3dgraphy issue zalmoxes-laran/s3Dgraphy#21 (multilingual unita_tipo) — the
  PR for option 1 (hardcode multilingual set) is being opened separately and
  is a prerequisite for non-Italian sites to even produce the rapporti graph.
- pyArchInit commits this session: `92f8a986` (1.6.0.dev7 migration),
  `e9c254b2` (d13 labels), `ae43c4bf` (projector multilingual), `13f1a513`
  (PG sequence resync on import), `f6295c5d` (numeric-blank coercion).
