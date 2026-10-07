"""em.json export of a site (B1, spec 2026-10-07 §5).

The graph travels the library's canonical DB->graph path and the file
is read back before being handed over: a file that does not read back
clean is not given to the user. GraphML stays only as the one-time
import from yEd.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(_ROOT), str(_ROOT / "ext_libs")):
    if entry not in sys.path:
        sys.path.append(entry)

from modules.s3dgraphy import em_export  # noqa: E402

if not em_export.emjson_available():
    pytest.skip("s3dgraphy senza em.json (pin pre-dev40)", allow_module_level=True)


@pytest.fixture()
def sample_db(tmp_path):
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    os.environ["PYARCHINIT_HOME"] = str(tmp_path)
    return "sqlite:///%s" % (folder / "db.sqlite")


def test_a_site_travels_and_reads_back(sample_db, tmp_path):
    path, nodes, edges, warnings = em_export.export_site(
        sample_db, "Scavo archeologico", str(tmp_path / "out"))
    assert os.path.exists(path) and path.endswith(".em.json")
    assert nodes > 0 and edges > 0
    assert warnings == []


def test_a_site_recorded_in_english_keeps_its_units(sample_db, tmp_path):
    # Review Focus 1: SU/WSU rows (the sample ships the same site in 10 languages)
    path, nodes, edges, _ = em_export.export_site(
        sample_db, "Archaeological Excavation", str(tmp_path / "out"))
    from s3dgraphy.importer.emjson_importer import import_emjson
    check, _w = import_emjson(path)
    from s3dgraphy.nodes.stratigraphic_node import (
        StratigraphicNode, is_masonry)
    strat = [n for n in check.nodes if isinstance(n, StratigraphicNode)]
    assert len(strat) >= 51, "le 51 US inglesi devono arrivare nel file"
    assert any(is_masonry(n) for n in strat), (
        "le WSU devono restare murarie anche rilette dal file")


def test_the_file_carries_the_matrix(sample_db, tmp_path):
    """C1 (final review 2026-10-07): an em.json with zero stratigraphic
    relations is a Harris matrix without the matrix. The graph must
    travel through the plugin's projector, which builds the rapporti
    edges the dev40 importer does not."""
    path, nodes, edges, _ = em_export.export_site(
        sample_db, "Scavo archeologico", str(tmp_path / "out"))
    from s3dgraphy.importer.emjson_importer import import_emjson
    check, _w = import_emjson(path)
    STRAT_EDGES = {
        "overlies", "is_overlain_by", "cuts", "is_cut_by", "fills",
        "is_filled_by", "abuts", "is_abutted_by", "equals", "bonded_to",
        "is_physically_equal_to", "is_bonded_to", "is_after", "is_before",
        "leans_on", "is_leaned_on_by",
    }
    rel = [e for e in check.edges
           if getattr(e, "edge_type", None) in STRAT_EDGES]
    assert len(rel) > 0, "nessun arco stratigrafico nel file: matrix vuoto"


def test_only_the_requested_site_travels(sample_db, tmp_path):
    """I1: the sample DB ships ~10 sites; the file must carry one."""
    path, nodes, edges, _ = em_export.export_site(
        sample_db, "Scavo archeologico", str(tmp_path / "out"))
    from s3dgraphy.importer.emjson_importer import import_emjson
    check, _w = import_emjson(path)
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
    strat = [n for n in check.nodes if isinstance(n, StratigraphicNode)]
    # on re-read the exporter's data{} lands in node.data (attributes
    # keep only the lifecycle keys): look where the file actually put it
    sites = {(getattr(n, "data", None) or {}).get("sito")
             or (getattr(n, "attributes", None) or {}).get("sito")
             for n in strat}
    assert sites <= {"Scavo archeologico"}, sites
    assert len(strat) < 100, "più siti nel file (%d unità)" % len(strat)


def test_projector_warnings_reach_the_caller(tmp_path):
    """I3: a suspicious chronology must come back in the warnings the
    dialog shows — never a silent '0 avvisi'."""
    import sqlite3
    db = tmp_path / "warn.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT DEFAULT '1', us TEXT, unita_tipo TEXT,
        node_uuid TEXT, rapporti TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT,
        attivita TEXT, struttura TEXT, settore TEXT, ambient TEXT,
        saggio TEXT, quad_par TEXT, documentazione TEXT,
        other_locations TEXT)""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, periodo TEXT, fase TEXT,
        cron_iniziale INTEGER, cron_finale INTEGER,
        descrizione TEXT, datazione_estesa TEXT)""")
    conn.execute("""CREATE TABLE site_table (
        id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT,
        nazione TEXT, regione TEXT, provincia TEXT, comune TEXT)""")
    conn.execute(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid, rapporti,"
        " periodo_iniziale, fase_iniziale) "
        "VALUES ('S', '1', 'US', 'uuid-1', '[]', '2', '1')")
    conn.execute(
        "INSERT INTO periodizzazione_table (sito, periodo, fase,"
        " cron_iniziale, cron_finale, descrizione) "
        "VALUES ('S', '2', '1', 1650, 1450, 'Bronzo')")
    conn.commit()
    conn.close()
    path, nodes, edges, warnings = em_export.export_site(
        "sqlite:///%s" % db, "S", str(tmp_path / "out"))
    assert any("1650" in str(w) for w in warnings), warnings


def test_internal_failures_speak_the_users_language(tmp_path):
    """I2: a DB without us_table must come back as EmExportError, not
    an ImportError traceback through the dialog."""
    import sqlite3
    db = tmp_path / "bare.sqlite"
    sqlite3.connect(db).close()
    with pytest.raises(em_export.EmExportError):
        em_export.export_site("sqlite:///%s" % db, "X", str(tmp_path / "out"))


def test_site_names_become_writable_filenames():
    # Review Focus 2
    assert em_export.site_filename("Scavo archeologico") == "Scavo_archeologico.em.json"
    assert em_export.site_filename("Festòs_2025") == "Festòs_2025.em.json"
    arabic = em_export.site_filename("تنقيب أثري")
    assert arabic.endswith(".em.json") and not arabic.startswith(".")


def test_an_empty_site_refuses_with_a_reason(sample_db, tmp_path):
    # Review Focus 3
    with pytest.raises(em_export.EmExportError) as err:
        em_export.export_site(sample_db, "SITO_CHE_NON_ESISTE", str(tmp_path / "out"))
    assert "niente da esportare" in str(err.value)
    assert not list((tmp_path / "out").glob("*.em.json")) if (tmp_path / "out").exists() else True


def test_a_stale_library_refuses_with_a_user_message(monkeypatch, tmp_path):
    # Review Focus 5
    monkeypatch.setattr(em_export, "emjson_available", lambda: False)
    with pytest.raises(em_export.EmExportError) as err:
        em_export.export_site("sqlite:///nowhere.sqlite", "X", str(tmp_path))
    assert "aggiorna le dipendenze" in str(err.value)


def test_the_opener_reports_failure_instead_of_raising(tmp_path):
    # Review Focus 4: EMStudio not installed
    target = tmp_path / "x.em.json"
    target.write_text("{}", encoding="utf-8")

    class _Run:                                     # finto subprocess.run
        def __init__(self, code): self.code = code
        def __call__(self, *a, **k):
            class R: returncode = self.code
            return R()

    assert em_export.open_in_emstudio(str(target), runner=_Run(0)) is True
    assert em_export.open_in_emstudio(str(target), runner=_Run(1)) is False

    def esplode(*a, **k): raise OSError("no app")
    assert em_export.open_in_emstudio(str(target), runner=esplode) is False


def test_the_menu_offers_the_export_and_handles_a_missing_emstudio():
    src = (_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert "Esporta sito in em.json" in src
    assert "open_in_emstudio" in src and "EMStudio/releases" in src
    # a plugin reload must not duplicate the entry (deferred minor)
    import re
    unload = re.search(r"def unload\(self\):(.*?)\n    def ", src, re.S)
    assert unload and "actionEmExport" in unload.group(1)


def test_the_opener_never_claims_success_without_emstudio(monkeypatch, tmp_path):
    """Deferred minor (final review): on Windows os.startfile and on
    Linux xdg-open follow the .json association — Notepad or an editor
    opens, the opener says True, and the 'where to get EMStudio' dialog
    never shows. Without a findable EMStudio the opener must say False."""
    import platform
    target = tmp_path / "x.em.json"
    target.write_text("{}", encoding="utf-8")
    for system in ("Windows", "Linux"):
        monkeypatch.setattr(platform, "system", lambda s=system: s)
        monkeypatch.setattr(em_export, "_find_emstudio_executable",
                            lambda: None)
        assert em_export.open_in_emstudio(str(target)) is False


def test_the_opener_launches_a_found_emstudio(monkeypatch, tmp_path):
    import platform
    target = tmp_path / "x.em.json"
    target.write_text("{}", encoding="utf-8")
    fake_exe = tmp_path / "EMStudio.exe"
    fake_exe.write_text("")
    launched = []
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(em_export, "_find_emstudio_executable",
                        lambda: str(fake_exe))

    def fake_popen(cmd, **k):
        launched.append(cmd)

        class P:
            pass
        return P()

    import subprocess
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    assert em_export.open_in_emstudio(str(target)) is True
    assert launched and launched[0][0] == str(fake_exe)
    assert launched[0][-1] == str(target)


def test_two_sites_with_the_same_safe_name_get_two_files(tmp_path):
    """Deferred minor (final review): 'Scavo 1' and 'Scavo/1' both
    sanitize to Scavo_1.em.json — the second export silently overwrote
    the first site's file. Same site -> same file (idempotent re-export);
    DIFFERENT site behind the same safe name -> a distinct file."""
    import sqlite3
    db = tmp_path / "two.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT DEFAULT '1', us TEXT, unita_tipo TEXT,
        node_uuid TEXT, rapporti TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT,
        attivita TEXT, struttura TEXT, settore TEXT, ambient TEXT,
        saggio TEXT, quad_par TEXT, documentazione TEXT,
        other_locations TEXT)""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, periodo TEXT, fase TEXT,
        cron_iniziale INTEGER, cron_finale INTEGER,
        descrizione TEXT, datazione_estesa TEXT)""")
    conn.execute("""CREATE TABLE site_table (
        id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT,
        nazione TEXT, regione TEXT, provincia TEXT, comune TEXT)""")
    for i, sito in enumerate(("Scavo 1", "Scavo/1")):
        conn.execute(
            "INSERT INTO us_table (sito, us, unita_tipo, node_uuid, rapporti) "
            "VALUES (?, ?, 'US', ?, '[]')", (sito, str(i + 1), "uuid-%d" % i))
    conn.commit()
    conn.close()
    url = "sqlite:///%s" % db
    out = str(tmp_path / "out")

    path_a, *_ = em_export.export_site(url, "Scavo 1", out)
    path_a2, *_ = em_export.export_site(url, "Scavo 1", out)
    assert path_a2 == path_a, "re-exporting the SAME site must reuse its file"
    path_b, *_ = em_export.export_site(url, "Scavo/1", out)
    assert path_b != path_a, "a different site must never overwrite another's file"

    from s3dgraphy.importer.emjson_importer import import_emjson
    assert import_emjson(path_a)[0].graph_id == "Scavo 1"
    assert import_emjson(path_b)[0].graph_id == "Scavo/1"
