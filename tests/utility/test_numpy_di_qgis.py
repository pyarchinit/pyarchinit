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
    assert pe.needs_newer_numpy(str(ext), "1.26.4") == ["pandas"]
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
    assert pe.numpy_repairs(str(req), str(ext), path=[str(ext), str(qgis)]) == ["pandas>=2.0.0"]


def test_l_installatore_usa_il_vincolo_e_ripara():
    corpo = INIT[INIT.index("    def install(package: str) -> None:"):]
    corpo = corpo[:corpo.index("\n    @staticmethod", 10)]
    assert "numpy_constraint_args(" in corpo
    missing = INIT[INIT.index("def get_missing_packages()"):]
    missing = missing[:missing.index("\ndef ", 10)]
    assert "numpy_repairs(" in missing


def test_si_rifa_solo_quando_cambia_la_versione_principale(ambiente):
    """numpy 1 → 2 è il salto che rompe (pandas 3 si rifiuta di partire); una
    versione minore più nuova in un requisito non giustifica una
    reinstallazione a ogni avvio."""
    _qgis, ext = ambiente
    assert "langchain-community" not in pe.needs_newer_numpy(str(ext), "1.26.4")


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
