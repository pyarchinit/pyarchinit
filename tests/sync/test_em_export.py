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
    assert nodes >= 51, "le 51 US inglesi devono arrivare nel grafo"


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
