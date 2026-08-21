#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
repair_rapporti.py — rimuove le righe vuote ['', '', '', ''] dai rapporti
stratigrafici (us_table.rapporti / rapporti2) lasciate dalle versioni
4.9.7–4.9.9 del plugin. Idempotente. DRY-RUN È IL DEFAULT: --apply per
scrivere (con copia di backup automatica per SQLite).

Esempi:
  python3 scripts/repair_rapporti.py --db /percorso/pyarchinit_db.sqlite
  python3 scripts/repair_rapporti.py --db /percorso/pyarchinit_db.sqlite --apply
  python3 scripts/repair_rapporti.py --conn-str postgresql://user:pw@host/db --apply
"""
import argparse
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from modules.utility.rapporti_repair import (  # noqa: E402
    backup_sqlite, repair_blank_rapporti, sqlite_path_of,
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rimuove le righe vuote dai rapporti stratigrafici. "
                    "Dry-run di default: --apply per scrivere.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--db", help="Percorso SQLite/SpatiaLite")
    group.add_argument("--conn-str", help="postgresql://user:pw@host/db")
    parser.add_argument("--apply", action="store_true",
                        help="Scrive davvero (default: dry-run)")
    parser.add_argument("--no-backup", action="store_true",
                        help="Non creare la copia di backup (solo SQLite)")
    args = parser.parse_args(argv)

    if args.db:
        p = Path(args.db).expanduser().resolve()
        if not p.is_file():
            sys.exit(f"DB non trovato: {args.db}")
        db = f"sqlite:///{p}"
    else:
        db = args.conn_str

    if args.apply and not args.no_backup:
        sqlite_path = sqlite_path_of(db)
        if sqlite_path is not None:
            print(f"Backup: {backup_sqlite(sqlite_path)}")
        else:
            print("Backend non SQLite: nessun backup automatico "
                  "(fai un dump prima, se serve).")

    result = repair_blank_rapporti(db, dry_run=not args.apply)
    print(result.summary())
    for d in result.details:
        print(f"  US {d.us} (sito={d.sito} area={d.area}) {d.column}: "
              f"{d.before_rows} -> {d.after_rows} righe")
    if not args.apply and result.rows_changed:
        print("Dry-run: nessuna modifica scritta. Ripeti con --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
