"""export_graphml() must surface suspicious periodization chronologies
(BC years typed without the minus sign) in ExportResult.warnings, which
the export dialog prints as "⚠️ ..." lines (2026-08-27, Ventena DB)."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import text  # noqa: E402

from modules.s3dgraphy.sync._db_handle import DbHandle  # noqa: E402
from modules.s3dgraphy.sync.graphml_writer import export_graphml  # noqa: E402


def _make_db(path, bronze_years):
    handle = DbHandle.from_path(path)
    with handle.engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, area TEXT DEFAULT '1', us TEXT,
                unita_tipo TEXT, node_uuid TEXT,
                rapporti TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
                periodo_finale TEXT, fase_finale TEXT,
                d_stratigrafica TEXT, d_interpretativa TEXT,
                attivita TEXT, struttura TEXT, settore TEXT,
                ambient TEXT, saggio TEXT, quad_par TEXT,
                documentazione TEXT,
                UNIQUE(sito, area, us, unita_tipo)
            )
        """))
        conn.execute(text("""
            CREATE TABLE periodizzazione_table (
                id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, periodo INTEGER, fase TEXT,
                cron_iniziale INTEGER, cron_finale INTEGER,
                descrizione TEXT, datazione_estesa TEXT, cont_per INTEGER
            )
        """))
        ini, fin = bronze_years
        for p, f, ci, cf, dat in ((1, "1", 301, 600, "Tardoromana"),
                                  (2, "1", ini, fin, "Bronzo Medio")):
            conn.execute(text(
                "INSERT INTO periodizzazione_table (sito, periodo, fase, "
                "cron_iniziale, cron_finale, descrizione, datazione_estesa) "
                "VALUES ('S', :p, :f, :ci, :cf, :d, :d)"),
                {"p": p, "f": f, "ci": ci, "cf": cf, "d": dat})
        for i, p in enumerate((1, 2), start=1):
            conn.execute(text(
                "INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, "
                "periodo_iniziale, fase_iniziale, rapporti) "
                "VALUES ('S', '1', :u, 'US', :n, :p, '1', '[]')"),
                {"u": str(i), "n": f"uuid-{i}", "p": str(p)})
    return path


def test_bc_years_without_sign_are_reported_in_export_warnings(tmp_path):
    db = _make_db(tmp_path / "bad.sqlite", (1650, 1450))
    res = export_graphml(db, "pyarchinit", tmp_path / "bad.graphml", site_filter="S")
    joined = "\n".join(str(w) for w in res.warnings)
    assert "Periodo 2 Fase 1: 1650 → 1450" in joined
    assert "a.C." in joined


def test_correct_bc_years_produce_no_chronology_warning(tmp_path):
    db = _make_db(tmp_path / "ok.sqlite", (-1650, -1450))
    res = export_graphml(db, "pyarchinit", tmp_path / "ok.graphml", site_filter="S")
    assert not [w for w in res.warnings if "cronologia" in str(w)]
