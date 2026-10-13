"""La tabella `pyarchinit_view_styles`: salvare, elencare, predefiniti per
sito e per tutti, rinominare, eliminare. Lo stesso giro su SQLite (qui) e
su PostgreSQL (`tests/sync/test_view_styles_store_pg.py`)."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import view_styles_store as store  # noqa: E402
from modules.utility.view_styles import LabelRecipe, SavedStyle, choose_style  # noqa: E402


def _pulisci(engine):
    store.ensure_table(engine)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM pyarchinit_view_styles"))


def _nuovo(view, site, name, qml, recipe=None, author=""):
    return SavedStyle(None, view, site, name, qml, recipe or LabelRecipe(), author=author)


def giro_completo(engine):
    """Il giro che vale per tutti e due i motori."""
    store.ensure_table(engine)
    store.ensure_table(engine)                                  # due volte: nessun errore
    _pulisci(engine)
    base = _nuovo("pyarchinit_us_view", None, "Base", "<qgis a/>",
                  LabelRecipe(enabled=True, preset="us_circle", one_per_unit=True), author="enzo")
    ia = store.save_style(engine, base)
    assert ia and base.id == ia and base.updated_at
    ib = store.save_style(engine, _nuovo("pyarchinit_us_view", "Scavo", "Scavo rosso", "<qgis b/>"))
    ic = store.save_style(engine, _nuovo("pyarchinit_us_view", "Altro", "Altro", "<qgis c/>"))
    store.save_style(engine, _nuovo("pyarchinit_quote_view", None, "Quote", "<qgis q/>",
                                    LabelRecipe(enabled=True, preset="quota")))
    elenco = store.list_styles(engine, "pyarchinit_us_view")
    assert [s.name for s in elenco] == ["Base", "Altro", "Scavo rosso"]      # prima «tutti», poi per sito
    assert elenco[0].recipe.preset == "us_circle" and elenco[0].recipe.one_per_unit
    assert elenco[0].author == "enzo" and elenco[0].for_all_sites
    assert choose_style(elenco, "Scavo") is None                             # nessun predefinito ancora
    for i in (ia, ib, ic):
        store.set_default(engine, i)
    elenco = store.list_styles(engine, "pyarchinit_us_view")
    assert choose_style(elenco, "Scavo").id == ib
    assert choose_style(elenco, "Boh").id == ia
    assert choose_style(elenco, None).id == ia
    idd = store.save_style(engine, _nuovo("pyarchinit_us_view", "Scavo", "Scavo blu", "<qgis d/>"))
    store.set_default(engine, idd)                                          # spegne «Scavo rosso»…
    elenco = store.list_styles(engine, "pyarchinit_us_view")
    assert [s.id for s in elenco if s.is_default and s.site == "Scavo"] == [idd]
    assert {s.id for s in elenco if s.is_default} == {ia, ic, idd}           # …e non gli altri
    store.clear_default(engine, idd)
    assert choose_style(store.list_styles(engine, "pyarchinit_us_view"), "Scavo").id == ia
    store.rename_style(engine, ib, "Scavo rinominato")
    b2 = next(s for s in store.list_styles(engine, "pyarchinit_us_view") if s.id == ib)
    assert b2.name == "Scavo rinominato"
    b2.qml = "<qgis b2/>"
    assert store.save_style(engine, b2) == ib                                # aggiorna, non duplica
    elenco = store.list_styles(engine, "pyarchinit_us_view")
    assert len(elenco) == 4 and next(s for s in elenco if s.id == ib).qml == "<qgis b2/>"
    store.delete_style(engine, ic)
    assert ic not in {s.id for s in store.list_styles(engine, "pyarchinit_us_view")}
    assert [s.name for s in store.list_styles(engine, "pyarchinit_quote_view")] == ["Quote"]
    assert store.list_styles(engine, "pyarchinit_tomba_view") == []
    _pulisci(engine)


def test_il_giro_completo_su_sqlite(tmp_path):
    giro_completo(create_engine("sqlite:///%s" % (tmp_path / "stili.sqlite")))


def test_il_gestore_del_database_sa_creare_la_tabella():
    sorgente = (_ROOT / "modules" / "db" / "pyarchinit_db_manager.py").read_text(encoding="utf-8")
    albero = ast.parse(sorgente)
    metodo = next((n for n in ast.walk(albero)
                   if isinstance(n, ast.FunctionDef) and n.name == "ensure_view_styles_table_exists"), None)
    assert metodo is not None
    assert "ensure_table" in ast.get_source_segment(sorgente, metodo)


def test_now_iso_e_una_data_leggibile():
    assert len(store.now_iso()) >= 19 and "T" in store.now_iso()
