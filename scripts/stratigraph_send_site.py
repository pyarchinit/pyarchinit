#!/usr/bin/env python3
"""Bring a pyArchInit site into a room of a StratiGraph node.

    python scripts/stratigraph_send_site.py --db ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite \\
        --site "Scavo archeologico" --node https://em.localhost:8443/em --room scavo-demo

Without ``--token`` (or ``STRATIGRAPH_TOKEN``) the node's sign-in page opens in
the browser: the token comes back to this process and is never written. With
``--dry-run`` the plan is printed and nothing is written on the node.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(ROOT, "ext_libs"), ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)
os.environ.setdefault("PYARCHINIT_HOME", os.path.join(os.path.expanduser("~"), "pyarchinit_5"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", required=True,
                        help="a .sqlite file, or a SQLAlchemy URL (postgresql://…)")
    parser.add_argument("--site", required=True)
    parser.add_argument("--node", required=True, help="e.g. https://em.localhost:8443/em")
    parser.add_argument("--room", required=True, help="the room id: one path segment, no spaces")
    parser.add_argument("--title", default=None)
    parser.add_argument("--token", default=os.environ.get("STRATIGRAPH_TOKEN"))
    parser.add_argument("--workdir", default=None, help="where the em.json is written")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    from modules.stratigraph import node_client as NC

    url = args.db if "://" in args.db else "sqlite:///" + os.path.abspath(os.path.expanduser(args.db))
    token = args.token
    if not token:
        print(f"Signing in to {args.node} — complete it in the browser…", file=sys.stderr)
        token = NC.sign_in(args.node)["access_token"]
    who = NC.whoami(args.node, token)
    print(f"Signed in as {who.get('name') or who.get('orcid') or who.get('preferred_username')}"
          f" (may create rooms: {who.get('may_create')})", file=sys.stderr)

    workdir = args.workdir or tempfile.mkdtemp(prefix="pyarchinit-room-")
    report = NC.send_site(url, args.site, node=args.node, room=args.room, token=token,
                          workdir=workdir, title=args.title, dry_run=args.dry_run)
    print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                            # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
