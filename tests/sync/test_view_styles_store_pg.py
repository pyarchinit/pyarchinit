"""Lo stesso giro di `tests/utility/test_view_styles_store.py`, su PostgreSQL
(salta se il server di prova non c'è)."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.sync.conftest_pg import PG_CONN_STR, pg_engine, clean_pg  # noqa: F401,E402
from tests.utility.test_view_styles_store import giro_completo  # noqa: E402


def test_il_giro_completo_su_postgres(pg_engine):  # noqa: F811
    giro_completo(pg_engine)
