"""5.19.4-alpha: the export says where the site is (EPSG of its GIS layers,
anchor in the middle of its drawings): without it EMStudio listed the room's
plans and drew none. A graph that already says where it is stays as it is."""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (_ROOT, _ROOT / "ext_libs"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
pytest.importorskip("s3dgraphy")


def test_an_undeclared_graph_gets_the_site_frame(monkeypatch):
    from s3dgraphy import api
    from s3dgraphy.graph import Graph
    from modules.s3dgraphy import site_frame as SF
    monkeypatch.setattr(SF, "site_frame", lambda url, site: (3004, 2324920.0, 4881960.0))
    g = Graph(graph_id="S")
    assert api.georeference_state(g) == "undeclared"
    assert SF.declare_site_frame(g, "sqlite:///x", "S") == (3004, 2324920.0, 4881960.0)
    a = api._geo_anchor(g)
    assert (a["epsg"], a["shift_x"], a["shift_y"]) == (3004, 2324920.0, 4881960.0)


def test_a_declared_graph_is_left_alone(monkeypatch):
    from s3dgraphy import api
    from s3dgraphy.graph import Graph
    from modules.s3dgraphy import site_frame as SF
    monkeypatch.setattr(SF, "site_frame", lambda url, site: (3004, 1.0, 2.0))
    g = Graph(graph_id="T")
    api.declare_georeference(g, 31700, shift_x=327300.0, shift_y=448370.0)
    assert SF.declare_site_frame(g, "sqlite:///x", "T") is None
    assert api._geo_anchor(g)["epsg"] == 31700


def test_no_drawings_no_frame(tmp_path):
    import shutil
    from modules.s3dgraphy.site_frame import site_frame
    db = tmp_path / "d.sqlite"
    shutil.copy(_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite", db)
    assert site_frame(f"sqlite:///{db}", "nowhere") is None
