"""Library for the USVA/USVB→USVs, USVC→USVn migration.

Split from the CLI script so tests can import the logic without invoking
argparse. The CLI module imports plan_changes/apply_changes from here.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

# Mapping from legacy pyarchinit unit-type abbreviations to the
# EM 1.5dev1 canonical names used by the s3dgraphy GraphMLExporter.
#
# Per legacy resources/dbfiles/dot.py:
#   USVA → parallelogram (Structural Virtual SU = USV/s)
#   USVB → hexagon (Non-Structural Virtual SU = USV/n)
#   USVC → ellipse (Series of USV — pyarchinit had no separate
#                   "series" type so we collapse to USV/n which
#                   shares the green border palette).
REPLACEMENTS = {
    "USVA": "USVs",
    "USVB": "USVn",
    "USVC": "USVn",
}


def plan_changes(db_path: Path) -> dict[str, int]:
    """Return counts per source-abbreviation. No mutation."""
    counts: dict[str, int] = {k: 0 for k in REPLACEMENTS}
    counts["USVs (already-aligned)"] = 0
    counts["USVn (already-aligned)"] = 0
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for src in REPLACEMENTS:
            cur.execute(
                "SELECT COUNT(*) FROM us_table WHERE unita_tipo = ?", (src,))
            counts[src] = cur.fetchone()[0]
        for tgt in {"USVs", "USVn"}:
            cur.execute(
                "SELECT COUNT(*) FROM us_table WHERE unita_tipo = ?", (tgt,))
            counts[f"{tgt} (already-aligned)"] = cur.fetchone()[0]
    finally:
        conn.close()
    return counts


def apply_changes(db_path: Path) -> dict[str, int]:
    """Apply REPLACEMENTS in-place; return counts of rows updated per source."""
    applied: dict[str, int] = {}
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for src, tgt in REPLACEMENTS.items():
            cur.execute(
                "UPDATE us_table SET unita_tipo = ? WHERE unita_tipo = ?",
                (tgt, src))
            applied[src] = cur.rowcount
        conn.commit()
    finally:
        conn.close()
    return applied
