#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_qfield.py — CLI per importare i dati QField nel DB pyArchInit.

Wrapper sottile su modules.utility.qfield_importer.run_qfield_import.
DRY-RUN È IL DEFAULT: usare --apply per scrivere davvero.

Esempi:
  # anteprima sul DB configurato nel plugin (config.cfg)
  python3 scripts/import_qfield.py --qfield-dir ~/qfield/scavo2026

  # import vero su PostGIS esplicito, foto su WebDAV di default
  python3 scripts/import_qfield.py --qfield-dir ~/qfield/scavo2026 \
      --conn-str postgresql://user:pw@host:5432/pyarchinit --apply

  # SpatiaLite esplicito, senza thumbnails
  python3 scripts/import_qfield.py --qfield-dir ~/qfield/scavo2026 \
      --db /percorso/pyarchinit_db.sqlite --apply --no-thumbs
"""
import argparse
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from modules.utility.qfield_importer import (  # noqa: E402
    QFieldImportError, default_media_dest, run_qfield_import,
)


def _plugin_conn():
    """(conn_str, thumb_path, thumb_resize) dal config.cfg del plugin."""
    from modules.db.pyarchinit_conn_strings import Connection
    conn = Connection()
    return (conn.conn_str(),
            conn.thumb_path()["thumb_path"],
            conn.thumb_resize()["thumb_resize"])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Importa i dati QField (pyarchinit-qfield) nel DB "
                    "pyArchInit. Dry-run di default: --apply per scrivere.")
    parser.add_argument("--qfield-dir", required=True,
                        help="Cartella del progetto QField (contiene i .gpkg)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--db", help="Percorso SQLite/SpatiaLite")
    group.add_argument("--conn-str", help="postgresql://user:pw@host/db")
    parser.add_argument("--apply", action="store_true",
                        help="Scrive davvero (default: dry-run)")
    parser.add_argument("--sito", default=None)
    parser.add_argument("--srid", type=int, default=None)
    parser.add_argument("--media-dest", default=None,
                        help="Cartella/URL destinazione foto "
                             "(default: parent della cartella thumb)")
    parser.add_argument("--no-geom-dedup", action="store_true")
    parser.add_argument("--no-media", action="store_true",
                        help="Non copiare le foto")
    parser.add_argument("--no-thumbs", action="store_true",
                        help="Non generare thumbnail")
    args = parser.parse_args(argv)

    if not Path(args.qfield_dir).is_dir():
        sys.exit(f"Cartella non trovata: {args.qfield_dir}")

    thumb_path = thumb_resize = None
    if args.db:
        db = f"sqlite:///{Path(args.db).expanduser().resolve()}"
    elif args.conn_str:
        db = args.conn_str
    else:
        db, thumb_path, thumb_resize = _plugin_conn()
    if thumb_path is None:
        try:
            _, thumb_path, thumb_resize = _plugin_conn()
        except Exception:
            thumb_path = thumb_resize = ""

    media_dest = args.media_dest or default_media_dest(thumb_path or "")

    try:
        result = run_qfield_import(
            db, args.qfield_dir, sito=args.sito, srid=args.srid,
            dry_run=not args.apply, geom_dedup=not args.no_geom_dedup,
            copy_media=not args.no_media, make_thumbs=not args.no_thumbs,
            media_dest=media_dest, thumb_path=thumb_path,
            thumb_resize=thumb_resize)
    except QFieldImportError as e:
        sys.exit(f"Errore: {e}")

    errors = (result.us.errors + result.materiali.errors +
              result.geometrie.errors + result.quote.errors +
              result.media.errors + result.links.errors +
              result.thumbs.errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
