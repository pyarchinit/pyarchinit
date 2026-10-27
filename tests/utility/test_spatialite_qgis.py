"""mod_spatialite si trova nel QGIS che gira, qualunque sia la sua struttura.

Il QGIS 3.44 per macOS mette l'estensione in ``Contents/Frameworks/
mod_spatialite.so``: il plugin cercava lì solo i ``.dylib`` e trovava
``libspatialite.dylib``, che come estensione non si carica (``symbol not
found``). Funzionava solo a chi aveva Spatialite di Homebrew.
"""
import os
import sqlite3
import sys

import pytest

from modules.utility import spatialite_loader as sl


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    return path


def _bundle(root, name="QGIS.app", layout="Frameworks", files=("mod_spatialite.so",)):
    contents = root / name / "Contents"
    for f in files:
        _touch(contents / layout / f)
    return contents


def _mac(prefix, executable="", roots=(), extra=()):
    cand = sl.spatialite_candidates(system="Darwin", prefix=str(prefix), executable=str(executable),
                                    app_roots=[str(r) for r in roots], mac_extra_dirs=[str(e) for e in extra])
    assert cand[-1] == "mod_spatialite"         # per ultimo, il caricatore del sistema
    return cand[:-1]


def test_qgis_344_estensione_so_in_frameworks(tmp_path):
    contents = _bundle(tmp_path, files=("mod_spatialite.so", "mod_spatialite.8.so",
                                        "libspatialite.dylib", "libspatialite.8.dylib"))
    cand = _mac(contents / "Frameworks")
    assert cand[0] == str(contents / "Frameworks" / "mod_spatialite.so")
    assert not [c for c in cand if "libspatialite" in c]


def test_struttura_vecchia_macos_lib(tmp_path):
    contents = _bundle(tmp_path, layout="MacOS/lib", files=("mod_spatialite.so",))
    cand = _mac(contents / "MacOS", executable=contents / "MacOS" / "QGIS")
    assert cand == [str(contents / "MacOS" / "lib" / "mod_spatialite.so")]


def test_prima_il_qgis_che_gira_poi_gli_altri_poi_homebrew(tmp_path):
    apps = tmp_path / "Applications"
    altro = _bundle(apps, "QGIS-LTR.app")
    gira = _bundle(apps, "QGIS.app")
    brew = _touch(tmp_path / "brew" / "mod_spatialite.dylib")
    cand = _mac(gira / "Frameworks", roots=[apps], extra=[brew.parent])
    assert cand == [str(gira / "Frameworks" / "mod_spatialite.so"),
                    str(altro / "Frameworks" / "mod_spatialite.so"),
                    str(brew)]


def test_qgis_da_executable_fuori_dal_prefix(tmp_path):
    gira = _bundle(tmp_path / "Applications", "QGIS 3.44.app")
    cand = _mac(tmp_path / "altrove", executable=gira / "MacOS" / "QGIS")
    assert cand == [str(gira / "Frameworks" / "mod_spatialite.so")]


def test_solo_file_che_esistono_e_mai_due_volte(tmp_path):
    contents = _bundle(tmp_path, files=("mod_spatialite.8.so",))
    os.symlink("mod_spatialite.8.so", contents / "Frameworks" / "mod_spatialite.so")
    cand = _mac(contents / "Frameworks", roots=[tmp_path])
    assert cand == [str(contents / "Frameworks" / "mod_spatialite.so")]


def test_windows_e_linux_come_prima():
    assert sl.spatialite_candidates(system="Windows")[0] == "mod_spatialite.dll"
    assert sl.spatialite_candidates(system="Linux", linux_dirs=[])[0] == "mod_spatialite.so"


class _Conn:
    def __init__(self, buoni):
        self.buoni, self.provati, self.abilitato = set(buoni), [], False

    def enable_load_extension(self, flag):
        self.abilitato = flag

    def load_extension(self, path):
        self.provati.append(path)
        if path not in self.buoni:
            raise sqlite3.OperationalError("symbol not found: " + path)


def test_carica_il_primo_che_funziona():
    sl._last_good = None
    conn = _Conn({"b"})
    assert sl.load_spatialite(conn, candidates=["a", "b", "c"]) == "b"
    assert conn.abilitato and conn.provati == ["a", "b"]


def test_poi_riprova_prima_quello_buono():
    sl._last_good = None
    sl.load_spatialite(_Conn({"b"}), candidates=["a", "b"])
    conn = _Conn({"b"})
    sl.load_spatialite(conn, candidates=["a", "b"])
    assert conn.provati == ["b"]


def test_errore_dice_cosa_ha_provato():
    sl._last_good = None
    with pytest.raises(sqlite3.OperationalError) as err:
        sl.load_spatialite(_Conn(set()), candidates=["/x/mod_spatialite.so"])
    testo = str(err.value)
    assert "Could not find mod_spatialite" in testo
    assert "/x/mod_spatialite.so" in testo and "symbol not found" in testo


QGIS_SO = "/Applications/QGIS.app/Contents/Frameworks/mod_spatialite.so"
_APERTE = []


@pytest.mark.skipif(sys.platform != "darwin" or not os.path.exists(QGIS_SO)
                    or not hasattr(sqlite3.Connection, "enable_load_extension"),
                    reason="serve il QGIS 3.44 per macOS")
def test_vero_qgis_344_di_questo_mac():
    sl._last_good = None
    conn = sqlite3.connect(":memory:")
    cand = sl.spatialite_candidates(prefix="/Applications/QGIS.app/Contents/Frameworks",
                                    executable="", app_roots=[], mac_extra_dirs=[])
    assert sl.load_spatialite(conn, candidates=cand) == QGIS_SO
    conn.enable_load_extension(False)
    assert conn.execute("SELECT spatialite_version()").fetchone()[0]
    # aperta fino alla fine: chiusa scaricherebbe le librerie del QGIS che,
    # fuori da QGIS, nessun altro tiene caricate (un fork dopo andrebbe in crash)
    _APERTE.append(conn)


def test_python_senza_estensioni_da_lo_stesso_errore():
    sl._last_good = None

    class _Senza:
        pass
    with pytest.raises(sqlite3.OperationalError):
        sl.load_spatialite(_Senza(), candidates=["a"])


def test_quello_buono_si_prova_senza_rifare_la_ricerca(monkeypatch):
    sl._last_good = None
    sl.load_spatialite(_Conn({"b"}), candidates=["a", "b"])

    def _non_cercare(*a, **k):
        raise AssertionError("ricerca rifatta")
    monkeypatch.setattr(sl, "spatialite_candidates", _non_cercare)
    conn = _Conn({"b"})
    assert sl.load_spatialite(conn) == "b"
    assert conn.provati == ["b"]


def test_niente_python_di_qgis_3_scritto_fisso():
    """Il QGIS 3.44 per macOS non ha Contents/MacOS/bin/python3: chi lo
    chiamava falliva (Gis_Time_controller all'import, la conversione
    dottoxml della scheda US)."""
    radice = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    trovati = []
    for cartella in ("tabs", "modules", "gui"):
        for base, _dirs, files in os.walk(os.path.join(radice, cartella)):
            for nome in files:
                if not nome.endswith(".py") or nome == "Pottery_tools.py":   # lì è un elenco che si prova
                    continue
                percorso = os.path.join(base, nome)
                with open(percorso, encoding="utf-8", errors="replace") as f:
                    for n, riga in enumerate(f, 1):
                        if "MacOS/bin/python3" in riga and not riga.lstrip().startswith("#"):
                            trovati.append("%s:%d" % (os.path.relpath(percorso, radice), n))
    assert trovati == []
