"""La narrativa sopravvive alla riesportazione dal database (2026-10-12).

Sul DB di prova: esporta, genera col modello finto, convalida, riesporta:
la narrativa c'è ancora, con il testo e la firma. Un file precedente rotto
non ferma l'esportazione.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.s3dgraphy import em_export  # noqa: E402
from modules.s3dgraphy import em_narrative as en  # noqa: E402

SITO = "Scavo archeologico"


@pytest.fixture()
def sample_db(tmp_path, monkeypatch):
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    return "sqlite:///%s" % (folder / "db.sqlite")


def test_la_narrativa_resta_quando_il_sito_si_riesporta(sample_db, tmp_path):
    out = tmp_path / "em"
    path, _n, _e, _w = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    cont, _ = en.load_project(path)
    graph = cont.active()
    assert en.narrative_of(graph) is None
    rep = en.generate(cont, chat=lambda m: "Capitolo scritto dal modello finto.",
                      model="finto", lang="it")
    assert rep.generated >= 1 and rep.failed == 0
    autore = en.human_authors(graph)[0][0]
    en.endorse(graph, en.narrative_of(graph), autore)
    en.save_project(cont, path)

    path2, _n2, _e2, avvisi = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    assert path2 == path
    assert any("conservata" in a or "kept" in a for a in avvisi)
    cont2, _ = en.load_project(path2)
    viste = en.overview(cont2, "it")
    assert viste and all(v.status == "ai_endorsed" for v in viste if v.can_generate)
    assert "Capitolo scritto dal modello finto." in viste[1].text

    senza, _, _, avvisi3 = em_export.export_site(sample_db, SITO, str(out), per_saggio=False,
                                                 keep_narrative=False)
    assert en.narrative_of(en.load_project(senza)[0].active()) is None
    assert not any("conservata" in a for a in avvisi3)


def test_un_file_precedente_rotto_non_ferma_l_esportazione(sample_db, tmp_path):
    out = tmp_path / "em"
    path, *_ = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    Path(path).write_text("{rotto", encoding="utf-8")
    path2, _n, _e, avvisi = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    assert path2 == path and any("non si legge" in a or "cannot be read" in a for a in avvisi)
    assert en.load_project(path2)


# --- l'esportazione per saggi: un grafo per saggio, una narrativa per grafo ---

import sqlite3  # noqa: E402

PROVA = _ROOT / "resources" / "dbfiles" / "pyarchinit_db_test.sqlite"
SITO_SAGGI = "Scavo a due aree"


@pytest.fixture
def con_saggi(tmp_path):
    """Una copia del database di prova in cui le due aree sono due saggi
    (la stessa di test_export_per_saggio)."""
    if not PROVA.is_file():
        pytest.skip("manca il database di prova")
    copia = tmp_path / "t.sqlite"
    shutil.copy(PROVA, copia)
    conn = sqlite3.connect(copia)
    conn.execute(
        "UPDATE us_table SET saggio = CASE WHEN CAST(area AS TEXT) = '1'"
        " THEN 'Saggio A' ELSE 'Saggio B' END")
    conn.commit()
    conn.close()
    return "sqlite:///%s" % copia


def test_con_i_saggi_ogni_grafo_tiene_la_sua_narrativa(con_saggi, tmp_path):
    out = tmp_path / "em"
    path, *_ = em_export.export_site(con_saggi, SITO_SAGGI, str(out), per_saggio=True)
    cont, _ = en.load_project(path)
    assert len(cont.graphs) >= 2
    rep = en.generate(cont, chat=lambda m: "Testo del saggio.", model="finto", lang="it")
    assert rep.generated >= 1 and rep.failed == 0
    assert all(en.narrative_of(g) is not None for g in cont.graphs.values())
    en.save_project(cont, path)

    path2, _n, _e, avvisi = em_export.export_site(con_saggi, SITO_SAGGI, str(out), per_saggio=True)
    assert path2 == path and any("conservata" in a for a in avvisi)
    cont2, _ = en.load_project(path2)
    assert sorted(cont2.graphs) == sorted(cont.graphs)
    assert all(en.narrative_of(g) is not None for g in cont2.graphs.values())
    viste = en.overview(cont2, "it")
    assert {v.graph_id for v in viste} == set(cont.graphs)
    assert any("Testo del saggio." in v.text for v in viste)


def test_riesportare_un_sito_a_saggi_torna_sullo_stesso_file(con_saggi, tmp_path):
    """Prima del 2026-10-12 ogni riesportazione per saggi finiva in un
    file nuovo col suffisso: gli id dei grafi sono «sito|saggio» e il
    controllo del proprietario non li riconosceva."""
    out = tmp_path / "em"
    p1, *_ = em_export.export_site(con_saggi, SITO_SAGGI, str(out), per_saggio=True)
    p2, *_ = em_export.export_site(con_saggi, SITO_SAGGI, str(out), per_saggio=True)
    assert p1 == p2 and sorted(x.name for x in out.iterdir()) == [Path(p1).name]


# --- revisione finale (2026-10-12): la forma del file che cambia, il file rotto ---

def test_se_la_forma_del_file_cambia_la_narrativa_non_sparisce_in_silenzio(con_saggi, tmp_path):
    out = tmp_path / "em"
    path, *_ = em_export.export_site(con_saggi, SITO_SAGGI, str(out), per_saggio=True)
    cont, _ = en.load_project(path)
    en.generate(cont, chat=lambda m: "Testo per saggio.", model="finto", lang="it")
    en.save_project(cont, path)
    path2, _n, _e, avvisi = em_export.export_site(con_saggi, SITO_SAGGI, str(out), per_saggio=False)
    assert path2 == path
    assert any("non è passata" in a or "did not travel" in a for a in avvisi)
    assert (out / (Path(path).name + ".bak")).is_file()
    assert "Testo per saggio." in (out / (Path(path).name + ".bak")).read_text(encoding="utf-8")


def test_un_file_precedente_rotto_viene_messo_da_parte(sample_db, tmp_path):
    out = tmp_path / "em"
    path, *_ = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    Path(path).write_text("{rotto", encoding="utf-8")
    path2, _n, _e, avvisi = em_export.export_site(sample_db, SITO, str(out), per_saggio=False)
    assert path2 == path and (out / (Path(path).name + ".broken")).read_text(encoding="utf-8") == "{rotto"
