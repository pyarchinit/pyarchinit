# -*- coding: utf-8 -*-
"""Repair blank relationship rows in ``us_table.rapporti`` / ``rapporti2``.

Background — bug report on plugin 4.9.9 (2026-08-20): ``us_table.rapporti``
of one record had grown to 78 676 rows, 78 674 of them ``['', '', '', '']``.
``tabs/US_USM.py::tableInsertData`` removed at most 4 rows before
reloading a record, and since af431e71 (4.9.7) ``table2dict(preserve_empty=True)``
turned the leftover rows into blank sublists that were persisted on
"Il record e' stato modificato. Vuoi salvare?". The UI bug is fixed in the
same release; this module removes the blank sublists already stored.

Rules:
- a *blank row* is a sublist whose cells are all empty/whitespace (or an
  empty sublist); any sublist with at least one non-blank cell is kept
  untouched, including legacy 2/3-column ones;
- values that do not parse as a Python list (``ast.literal_eval``) are
  left alone and never counted as changed;
- idempotent; SQLite and PostgreSQL; all UPDATEs in one transaction.

No Qt/QGIS imports: usable from the CLI (``scripts/repair_rapporti.py``)
and from the plugin menu.
"""
from __future__ import annotations

import ast
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

#: Columns of ``us_table`` that hold a ``str(list_of_lists)`` of relationships.
RAPPORTI_COLUMNS: Tuple[str, ...] = ("rapporti", "rapporti2")

DbInput = Union[Engine, str]


def is_blank_row(row) -> bool:
    """True when *row* is a list whose cells are all empty/whitespace."""
    if not isinstance(row, list):
        return False
    return all(cell is None or str(cell).strip() == "" for cell in row)


def strip_blank_rows(value: Optional[str]) -> Tuple[Optional[str], int]:
    """Return ``(new_value, removed_count)`` for one stored column value.

    ``new_value`` is ``value`` itself when nothing was removed.
    """
    if not value:
        return value, 0
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return value, 0
    if not isinstance(parsed, list):
        return value, 0
    kept = [row for row in parsed if not is_blank_row(row)]
    removed = len(parsed) - len(kept)
    if removed == 0:
        return value, 0
    return str(kept), removed


@dataclass
class RowChange:
    id_us: int
    sito: Optional[str]
    area: Optional[str]
    us: Optional[str]
    column: str
    before_rows: int
    after_rows: int


@dataclass
class RepairResult:
    dry_run: bool
    rows_scanned: int = 0
    rows_changed: int = 0
    blank_rows_removed: int = 0
    details: List[RowChange] = field(default_factory=list)

    def summary(self) -> str:
        mode = "DRY-RUN" if self.dry_run else "APPLICATO"
        return (f"[{mode}] record esaminati: {self.rows_scanned}; "
                f"record da correggere: {self.rows_changed}; "
                f"righe vuote rimosse: {self.blank_rows_removed}")


def _engine(db: DbInput) -> Engine:
    if isinstance(db, Engine):
        return db
    return create_engine(db)


def sqlite_path_of(db: DbInput) -> Optional[Path]:
    """File path when *db* is a file-backed SQLite engine/URL, else None."""
    engine = _engine(db)
    if engine.dialect.name != "sqlite" or not engine.url.database:
        return None
    return Path(engine.url.database)


def backup_sqlite(db_path: Path, tag: str = "rapporti_repair") -> Path:
    """Copy db_path to ``<db>.pre_<tag>_<UTC timestamp>``; return new path."""
    db_path = Path(db_path)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup = db_path.with_name(f"{db_path.name}.pre_{tag}_{stamp}")
    shutil.copy2(db_path, backup)
    return backup


def repair_blank_rapporti(db: DbInput, *, dry_run: bool = True) -> RepairResult:
    """Strip blank relationship rows from every ``us_table`` record.

    With ``dry_run=True`` nothing is written; the result still lists every
    record that *would* change. With ``dry_run=False`` all UPDATEs run in
    one transaction.
    """
    engine = _engine(db)
    result = RepairResult(dry_run=dry_run)
    cols = ", ".join(RAPPORTI_COLUMNS)
    select = text(f"SELECT id_us, sito, area, us, {cols} FROM us_table")

    with engine.begin() as conn:
        rows = conn.execute(select).fetchall()
        result.rows_scanned = len(rows)
        for row in rows:
            id_us, sito, area, us = row[0], row[1], row[2], row[3]
            new_values = {}
            for idx, col in enumerate(RAPPORTI_COLUMNS):
                old = row[4 + idx]
                new, removed = strip_blank_rows(old)
                if removed:
                    new_values[col] = new
                    result.blank_rows_removed += removed
                    result.details.append(RowChange(
                        id_us=id_us, sito=sito, area=area, us=us, column=col,
                        before_rows=len(ast.literal_eval(old)),
                        after_rows=len(ast.literal_eval(new)),
                    ))
            if not new_values:
                continue
            result.rows_changed += 1
            if dry_run:
                continue
            assignments = ", ".join(f"{c} = :{c}" for c in new_values)
            conn.execute(
                text(f"UPDATE us_table SET {assignments} WHERE id_us = :id_us"),
                {**new_values, "id_us": id_us},
            )
    return result
