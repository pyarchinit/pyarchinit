"""Issue #666 (Windows, QGIS 3.40 LTR, Python 3.12): l'installazione in
ext_libs prendeva il pandas più recente (3.x, vuole numpy >= 2.0.2), ma QGIS
carica il suo numpy 1.26.4 e quel pandas non parte: le schede US e Reperti
non si aprivano. Ora ogni installazione in ext_libs ha il vincolo del numpy
di QGIS, e un pacchetto già installato che chiede un numpy più nuovo si
reinstalla. Cartelle finte: niente pip, niente rete."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from modules.utility import python_env as pe  # noqa: E402

INIT = (_ROOT / "__init__.py").read_text(encoding="utf-8")


def _dist(radice, nome, versione, requisiti=()):
    d = radice / ("%s-%s.dist-info" % (nome, versione))
    d.mkdir(parents=True)
    righe = ["Metadata-Version: 2.1", "Name: %s" % nome, "Version: %s" % versione]
    righe += ["Requires-Dist: %s" % r for r in requisiti]
    (d / "METADATA").write_text("\n".join(righe) + "\n", encoding="utf-8")


@pytest.fixture
def ambiente(tmp_path):
    qgis, ext = tmp_path / "qgis_site", tmp_path / "ext_libs"
    _dist(qgis, "numpy", "1.26.4")
    _dist(ext, "numpy", "2.1.0")                          # tirato dentro da pandas 3
    _dist(ext, "pandas", "3.1.0", ['numpy>=2.0.2; python_version < "3.14"',
                                   'numpy>=2.3.3; python_version >= "3.14"',
                                   "python-dateutil>=2.8.2"])
    _dist(ext, "matplotlib", "3.9.0", ["numpy>=1.23"])
    _dist(ext, "qualcosa", "1.0", ['numpy>=3; extra == "turbo"'])   # solo con un extra
    # chiede 1.26.6 ma con 1.26.4 si importa lo stesso: non si rifà per questo
    _dist(ext, "langchain-community", "0.3.31", ['numpy>=1.26.6; python_version < "3.13"'])
    return qgis, ext


def test_il_numpy_che_conta_e_quello_di_qgis(ambiente):
    qgis, ext = ambiente
    assert pe.host_numpy_version(str(ext), path=[str(ext), str(qgis)]) == "1.26.4"


def test_chi_chiede_un_numpy_piu_nuovo(ambiente):
    _qgis, ext = ambiente
    assert pe.needs_newer_numpy(str(ext), "1.26.4") == ["langchain-community", "pandas"]
    assert pe.needs_newer_numpy(str(ext), "2.1.0") == []


def test_il_vincolo_per_pip(ambiente, tmp_path):
    qgis, ext = ambiente
    args = pe.numpy_constraint_args(str(ext), path=[str(ext), str(qgis)], workdir=str(tmp_path))
    assert args[0] == "--constraint"
    assert Path(args[1]).read_text(encoding="utf-8").strip() == "numpy==1.26.4"
    assert pe.numpy_constraint_args(str(ext), path=[str(tmp_path / "vuota")], workdir=str(tmp_path)) == []


def test_da_reinstallare_con_la_riga_dei_requisiti(ambiente, tmp_path):
    qgis, ext = ambiente
    req = tmp_path / "requirements.txt"
    req.write_text("SQLAlchemy>=2.0.0\npandas>=2.0.0\nmatplotlib>=3.7.0\n", encoding="utf-8")
    assert pe.numpy_repairs(str(req), str(ext), path=[str(ext), str(qgis)]) == [
        "langchain-community", "pandas>=2.0.0"]


def test_l_installatore_usa_il_vincolo_e_ripara():
    corpo = INIT[INIT.index("    def install(package: str) -> None:"):]
    corpo = corpo[:corpo.index("\n    @staticmethod", 10)]
    assert "numpy_constraint_args(" in corpo
    missing = INIT[INIT.index("def get_missing_packages()"):]
    missing = missing[:missing.index("\ndef ", 10)]
    assert "numpy_repairs(" in missing


def test_anche_una_versione_minore_conta_ma_si_tenta_una_volta(ambiente, tmp_path):
    """Revisione: un pandas 3.0 (numpy >= 1.26.0) col numpy 1.24 di Debian
    non parte, anche se la serie è la stessa. Si segnala tutto, ma una
    riparazione già tentata per quel numpy non si ripropone a ogni avvio."""
    qgis, ext = ambiente
    assert "langchain-community" in pe.needs_newer_numpy(str(ext), "1.26.4")
    req = tmp_path / "requirements.txt"
    req.write_text("pandas>=2.0.0\nlangchain-community>=0.3.27\n", encoding="utf-8")
    prima = pe.numpy_repairs(str(req), str(ext), path=[str(ext), str(qgis)])
    assert prima == ["langchain-community>=0.3.27", "pandas>=2.0.0"]
    pe.note_numpy_attempt(str(ext), "pandas>=2.0.0", path=[str(ext), str(qgis)])
    assert pe.numpy_repairs(str(req), str(ext), path=[str(ext), str(qgis)]) == ["langchain-community>=0.3.27"]


def test_qgis4_col_numpy_2_e_un_pacchetto_che_vuole_numpy_1(tmp_path):
    """QGIS 4 (Python 3.12) ha numpy 2.5: il salto al contrario, un vecchio
    pacchetto in ext_libs che chiede numpy < 2, va rifatto anche lui; pandas
    3 lì va bene."""
    qgis, ext = tmp_path / "qgis4_site", tmp_path / "ext_libs"
    _dist(qgis, "numpy", "2.5.2")
    _dist(ext, "vecchio-cv", "4.9.0", ["numpy<2"])
    _dist(ext, "pandas", "3.1.0", ['numpy>=2.0.2; python_version < "3.14"'])
    assert pe.host_numpy_version(str(ext), path=[str(ext), str(qgis)]) == "2.5.2"
    assert pe.needs_newer_numpy(str(ext), "2.5.2") == ["vecchio-cv"]


def test_i_dist_info_vecchi_non_tornano_a_chiedere(ambiente):
    """Revisione: pip --target --upgrade che scende di versione lascia il
    vecchio pandas-3.1.0.dist-info accanto al nuovo; il controllo lo
    rivedeva e la finestra tornava a ogni avvio. Si tiene il più recente."""
    import os
    import time
    _qgis, ext = ambiente
    time.sleep(0.01)
    _dist(ext, "pandas", "3.0.6", ['numpy>=1.26.0; python_version < "3.14"'])   # quello appena messo da pip
    vecchio = ext / "pandas-3.1.0.dist-info"
    os.utime(vecchio, (1, 1))
    assert "pandas" not in pe.needs_newer_numpy(str(ext), "1.26.4")
    tolti = pe.prune_stale_dists(str(ext))
    assert not vecchio.exists() and (ext / "pandas-3.0.6.dist-info").exists() and tolti


def test_la_riga_con_la_versione_di_python_giusta(tmp_path):
    """Revisione: per un nome scritto due volte si prendeva la prima riga (di
    solito quella per Python < 3.10): pip la ignorava e non reinstallava."""
    qgis, ext = tmp_path / "q", tmp_path / "e"
    _dist(qgis, "numpy", "1.26.4")
    _dist(ext, "langchain-community", "0.4.0", ["numpy>=2"])
    req = tmp_path / "requirements.txt"
    req.write_text('langchain-community>=0.3.27; python_version<"3.0"\n'
                   'langchain-community>=0.4.0; python_version>="3.0"\n', encoding="utf-8")
    assert pe.numpy_repairs(str(req), str(ext), path=[str(ext), str(qgis)]) == ["langchain-community>=0.4.0"]


def test_senza_poter_scrivere_il_vincolo_niente_blocchi(ambiente, tmp_path):
    qgis, ext = ambiente
    sola_lettura = tmp_path / "ro"
    sola_lettura.mkdir()
    sola_lettura.chmod(0o500)
    try:
        assert pe.numpy_constraint_args(str(ext), path=[str(ext), str(qgis)], workdir=str(sola_lettura)) == []
    finally:
        sola_lettura.chmod(0o700)


def test_numpy_con_etichetta_locale(tmp_path):
    qgis, ext = tmp_path / "q", tmp_path / "e"
    _dist(qgis, "numpy", "2.1.3+mkl")
    ext.mkdir()
    args = pe.numpy_constraint_args(str(ext), path=[str(ext), str(qgis)], workdir=str(tmp_path))
    assert Path(args[1]).read_text(encoding="utf-8").strip() == "numpy==2.1.3"


def test_la_copia_di_numpy_in_ext_libs_se_ne_va(ambiente):
    """pip --target ci mette numpy come dipendenza: quello che conta è di
    QGIS (già caricato), la copia in ext_libs è peso morto e per i processi
    figli col PYTHONPATH su ext_libs sarebbe il numpy sbagliato."""
    qgis, ext = ambiente
    (ext / "numpy").mkdir()
    (ext / "numpy.libs").mkdir()
    assert pe.drop_ext_numpy(str(ext), path=[str(ext), str(qgis)])
    assert not [v for v in ext.iterdir() if v.name.lower().startswith("numpy")]
    # senza un numpy di QGIS non si tocca niente
    altra = ambiente[1].parent / "ext2"
    (altra / "numpy").mkdir(parents=True)
    assert not pe.drop_ext_numpy(str(altra), path=[str(altra)]) and (altra / "numpy").exists()


def test_l_installatore_mette_in_ordine_dopo_pip():
    corpo = INIT[INIT.index("    def install(package: str) -> None:"):]
    corpo = corpo[:corpo.index("\n    @staticmethod", 10)]
    for chiamata in ("prune_stale_dists(", "drop_ext_numpy(", "note_numpy_attempt("):
        assert chiamata in corpo, chiamata
    worker = INIT[INIT.index("    def install_packages(self, packages: List[str]) -> None:"):]
    worker = worker[:worker.index("self.finished.emit()")]
    assert "except Exception" in worker          # un pacchetto che fallisce non blocca la finestra
