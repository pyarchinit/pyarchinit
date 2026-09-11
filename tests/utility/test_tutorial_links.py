"""Links inside the tutorials (2026-09-11).

On Windows the Tutorial tab opened the web browser, never the chapter or
paragraph clicked: every link that was not an animation went to
webbrowser.open() — '#introduzione' (the "Indice" of every tutorial, 1267
links) and '34_movecost.md' included — and the headings had no anchors to
scroll to. Now '#...' scrolls inside the tutorial, 'NN_x.md#...' opens that
tutorial in the viewer at that paragraph, animations stay in the embedded
viewer, files and web pages go to the system with file:/// URLs that also
work on Windows. Pure Python except the last test (Qt).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import tutorial_links as tl  # noqa: E402


def test_slugs_like_the_tables_of_contents():
    assert tl.slugify("Concetti Fondamentali") == "concetti-fondamentali"
    assert tl.slugify("Cos'e un'Unita Stratigrafica (US)") == "cose-ununita-stratigrafica-us"
    assert tl.slugify("Προσβαση στο εργαλειο") == "προσβαση-στο-εργαλειο"
    assert tl.slugify("<strong>Campo</strong> <code>order_layer</code>") == "campo-order_layer"
    assert tl.slugify("Esporta &amp; importa") == "esporta--importa"


def test_headings_get_anchors_and_duplicates_are_numbered():
    html = tl.add_heading_anchors("<h2>Esempio</h2><p>x</p><h3 class='a'>Esempio</h3><h1>Altro</h1>")
    assert 'name="esempio"' in html and 'name="esempio-1"' in html and 'name="altro"' in html
    assert tl.heading_slugs("## Esempio\n```\n## non un titolo\n```\n### Esempio\n") == {"esempio", "esempio-1"}


def test_every_table_of_contents_entry_finds_its_heading():
    missing = []
    for path in sorted((_ROOT / "docs" / "tutorials").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        slugs = tl.heading_slugs(text)
        for anchor in re.findall(r'(?<!!)\[[^\]]+\]\(#([^)\s]+)\)', text):
            if anchor not in slugs:
                missing.append(f"{path.parent.name}/{path.name}: #{anchor}")
    assert not missing, "\n".join(missing)


@pytest.mark.parametrize("href,kind,target,fragment", [
    ("#introduzione", "anchor", None, "introduzione"),
    ("#%CE%B5%CE%B9%CF%83", "anchor", None, "εισ"),
    ("34_movecost.md", "tutorial", "34_movecost.md", ""),
    ("34_movecost.md#accesso-allo-strumento", "tutorial", "34_movecost.md", "accesso-allo-strumento"),
    ("../../animations/harris_matrix_animation.html", "animation",
     os.path.join("..", "..", "animations", "harris_matrix_animation.html"), ""),
    ("images/figura.png", "file", os.path.join("images", "figura.png"), ""),
    ("https://www.qgis.org/#download", "external", "https://www.qgis.org/#download", ""),
    ("mailto:pyarchinit@gmail.com", "external", "mailto:pyarchinit@gmail.com", ""),
])
def test_link_kinds(tmp_path, href, kind, target, fragment):
    here = str(tmp_path / "docs" / "it")
    got_kind, got_target, got_fragment = tl.classify_link(href, here)
    assert (got_kind, got_fragment) == (kind, fragment)
    if kind in ("tutorial", "animation", "file"):
        assert got_target == os.path.normpath(os.path.join(here, target))
    elif kind == "external":
        assert got_target == target


def test_a_file_url_given_by_qt_is_a_local_file(tmp_path):
    page = tmp_path / "03_scheda_us.md"
    page.write_text("# x", encoding="utf-8")
    assert tl.classify_link(page.as_uri() + "#campi", str(tmp_path)) == ("tutorial", str(page), "campi")


class _Browser:
    def __init__(self):
        self.anchors = []

    def scrollToAnchor(self, name):
        self.anchors.append(name)


def test_each_kind_of_link_goes_where_it_should(tmp_path):
    (tmp_path / "34_movecost.md").write_text("# x", encoding="utf-8")
    animation = tmp_path / "a.html"
    animation.write_text("<html></html>", encoding="utf-8")
    calls, browser = [], _Browser()
    handlers = dict(open_tutorial=lambda path, fragment: calls.append(("tutorial", path, fragment)),
                    open_animation=lambda path: calls.append(("animation", path)),
                    open_external=lambda url: calls.append(("external", url)))

    tl.follow_link("#accesso", str(tmp_path), browser, **handlers)
    tl.follow_link("34_movecost.md#uso", str(tmp_path), browser, **handlers)
    tl.follow_link("a.html", str(tmp_path), browser, **handlers)
    tl.follow_link("https://qgis.org", str(tmp_path), browser, **handlers)

    assert browser.anchors == ["accesso"]                     # never the web browser
    assert calls == [("tutorial", str(tmp_path / "34_movecost.md"), "uso"),
                     ("animation", str(animation)),
                     ("external", "https://qgis.org")]


def test_without_an_embedded_viewer_a_local_file_goes_to_the_system_as_a_file_url(tmp_path):
    animation = tmp_path / "a b.html"
    animation.write_text("x", encoding="utf-8")
    calls = []
    tl.follow_link("a%20b.html", str(tmp_path), _Browser(), open_external=calls.append)
    assert calls == [animation.as_uri()]                      # file:///C:/... on Windows


def test_the_viewers_use_the_shared_link_handling():
    for source in ("tabs/Tutorial_viewer.py", "pyarchinitDockWidget.py"):
        text = (_ROOT / source).read_text(encoding="utf-8")
        assert "follow_link(" in text and "add_heading_anchors(" in text, source
        assert "file://{" not in text, source                 # the malformed Windows URL


def test_the_text_browser_scrolls_to_a_heading():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from qgis.PyQt.QtWidgets import QApplication, QTextBrowser
    except ImportError:
        # no QGIS here, or a stub qgis.PyQt.QtWidgets left in sys.modules by
        # another test (test_us_pdf_rapporti_overflow.py installs one)
        pytest.skip("real Qt widgets not available")
    app = QApplication.instance() or QApplication([])
    browser = QTextBrowser()
    browser.resize(400, 200)
    body = "".join(f"<h2>Capitolo {i}</h2>" + "<p>testo</p>" * 20 for i in range(10))
    browser.setHtml(tl.add_heading_anchors(body))
    browser.show()
    app.processEvents()
    assert browser.verticalScrollBar().value() == 0
    tl.scroll_to_anchor(browser, "capitolo-8")
    app.processEvents()
    assert browser.verticalScrollBar().value() > 0
