"""s3dgraphy 1.6.0.dev40: a masonry unit is a US with a kind (2026-10-07).

USM is a recording practice, so in the EM model a masonry unit is a
``US`` with ``stratigraphic_kind = "masonry"`` and USR/USS a US with
``"coating"``; localised codes (WSU, MSE, UEM…) are recognised. The code
a unit came in with is kept, and ``unit_code()`` gives it back for the
way to pyArchInit. The bridge used to rely on the node CLASS to say
"masonry": these tests pin the new behaviour at our creation points.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(_ROOT), str(_ROOT / "ext_libs")):
    if entry not in sys.path:
        sys.path.append(entry)

sn = pytest.importorskip("s3dgraphy.nodes.stratigraphic_node")
if not hasattr(sn, "set_kind"):           # pre-dev40 library: nothing to pin yet
    pytest.skip("s3dgraphy senza stratigraphic_kind (pin ancora a dev9)",
                allow_module_level=True)

from modules.s3dgraphy.sync.graph_projector import (  # noqa: E402
    _create_stratigraphic_node_for_unita_tipo,
)


def test_a_masonry_row_becomes_a_us_with_the_masonry_kind():
    node = _create_stratigraphic_node_for_unita_tipo("USM", "10", "uuid-10")
    assert node is not None
    assert type(node).__name__ == "StratigraphicUnit"   # not a class of its own
    assert sn.is_masonry(node)
    assert sn.unit_code(node) == "USM"


def test_a_localised_masonry_code_keeps_its_own_spelling():
    node = _create_stratigraphic_node_for_unita_tipo("WSU", "4", "uuid-4")
    assert node is not None and sn.is_masonry(node)
    assert sn.unit_code(node) == "WSU", "the way back must return the site's code"


def test_a_plain_us_has_no_kind():
    node = _create_stratigraphic_node_for_unita_tipo("US", "1", "uuid-1")
    assert node is not None
    assert not sn.is_masonry(node) and not sn.is_coating(node)
    assert sn.unit_code(node) is None


def test_the_virtual_units_keep_their_own_classes():
    node = _create_stratigraphic_node_for_unita_tipo("USVs", "2", "uuid-2")
    assert node is not None
    assert type(node).__name__ == "StructuralVirtualStratigraphicUnit"


def test_the_library_is_the_one_the_plugin_pins():
    import re
    pinned = re.search(r"^s3dgraphy==(\S+)$",
                       (_ROOT / "requirements.txt").read_text(encoding="utf-8"), re.M)
    from importlib.metadata import version, PackageNotFoundError
    try:
        installed = version("s3dgraphy")
    except PackageNotFoundError:
        pytest.skip("s3dgraphy senza metadata qui")
    assert pinned and pinned.group(1) == installed, (
        "ext_libs ha %s ma requirements.txt chiede %s" % (installed, pinned and pinned.group(1)))


def test_the_way_back_resolves_a_masonry_us_to_its_code():
    """Ingestor side (1.6.12/13): a kind-bearing US whose attrs were
    stripped by a graphml round-trip must land as a USM/WSU row, not US."""
    from modules.s3dgraphy.sync.graph_ingestor import _resolve_unita_tipo
    node = _create_stratigraphic_node_for_unita_tipo("USM", "10", "uuid-10")
    assert _resolve_unita_tipo(node, {}) == "USM"
    wsu = _create_stratigraphic_node_for_unita_tipo("WSU", "4", "uuid-4")
    assert _resolve_unita_tipo(wsu, {}) == "WSU"
    plain = _create_stratigraphic_node_for_unita_tipo("US", "1", "uuid-1")
    assert _resolve_unita_tipo(plain, {}) == "US"
