"""config.cfg lacking keys is completed as a dictionary, not patched by byte
offsets (which wrote «'SITE_SET' :','LOGO'» and broke every export, 27 Nov 2026)."""
import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def test_missing_keys_are_added_and_the_file_still_parses(tmp_path):
    from modules.utility.settings import _ensure_config_keys
    cfg = tmp_path / "config.cfg"
    cfg.write_text("{'DATABASE': 'X.sqlite', 'SERVER': 'sqlite', 'THUMB_PATH': '/a/'}")   # no newline
    _ensure_config_keys(str(cfg))
    conf = ast.literal_eval(cfg.read_text())
    assert conf["DATABASE"] == "X.sqlite" and conf["SITE_SET"] == "" and conf["SSLMODE"] == "allow"
    assert "THUMB_RESIZE" in conf and "LOGO" in conf
    before = cfg.read_text()
    _ensure_config_keys(str(cfg))
    assert cfg.read_text() == before


def test_a_file_that_does_not_parse_is_left_alone(tmp_path):
    from modules.utility.settings import _ensure_config_keys
    cfg = tmp_path / "config.cfg"
    cfg.write_text("{'DATABASE': 'X.sqlite',")
    _ensure_config_keys(str(cfg))
    assert cfg.read_text() == "{'DATABASE': 'X.sqlite',"
