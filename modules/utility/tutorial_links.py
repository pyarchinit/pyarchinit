"""Links inside the tutorials shown by pyArchInit (Tutorial window and dock).

The tutorials are Markdown shown in a QTextBrowser that handles clicks
itself. Every link that was not an animation went to webbrowser.open():
on Windows the web browser opened and never the chapter or paragraph
clicked — '#introduzione' (the "Indice" of every tutorial) and
'34_movecost.md' included — and the headings had no anchors to scroll to
(2026-09-11). Here: heading anchors named like GitHub (the tables of
contents use those names), where each kind of link goes, and the scroll.

Pure Python; Qt only in scroll_to_anchor() (duck-typed) and in the default
way of handing a URL to the system.
"""
from __future__ import annotations

import html as _html
import os
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import url2pathname

_TAG = re.compile(r'<[^>]+>')
_HEADING_HTML = re.compile(r'<h([1-6])([^>]*)>(.*?)</h\1>', re.S | re.I)
_HEADING_MD = re.compile(r'^#{1,6} (.+)$', re.M)
_EXTERNAL = ('http', 'https', 'mailto', 'ftp')


def slugify(text):
    """GitHub-style anchor of a heading: 'Concetti Fondamentali' ->
    'concetti-fondamentali' (tags, markup and punctuation dropped)."""
    text = _html.unescape(_TAG.sub('', text)).strip().lower()
    text = re.sub(r'[^\w\- ]', '', text)
    return text.replace(' ', '-')


def _numbered(seen, slug):
    count = seen[slug]
    seen[slug] += 1
    return slug if count == 0 else '%s-%d' % (slug, count)


def heading_slugs(markdown_text):
    """Anchors of the headings of a Markdown text (fenced code skipped)."""
    body = re.sub(r'```.*?```', '', markdown_text, flags=re.S)
    seen = Counter()
    return {_numbered(seen, slugify(h)) for h in _HEADING_MD.findall(body)}


def add_heading_anchors(html):
    """Name every <h1>..<h6> with its slug — an <a name> inside the heading,
    what QTextBrowser.scrollToAnchor() looks for; repeated headings get
    -1, -2 ... like on GitHub."""
    seen = Counter()

    def anchor(m):
        name = _html.escape(_numbered(seen, slugify(m.group(3))), quote=True)
        return '<h%s%s><a name="%s"></a>%s</h%s>' % (m.group(1), m.group(2), name, m.group(3), m.group(1))

    return _HEADING_HTML.sub(anchor, html)


def classify_link(href, current_dir):
    """(kind, target, fragment) of a link clicked in a tutorial. kind:
    'anchor' (a paragraph of the same tutorial), 'tutorial' (.md),
    'animation' (.html), 'file' (another local file), 'external' (web,
    mail). Local targets are absolute paths resolved from current_dir."""
    parts = urlsplit(href)
    scheme = parts.scheme.lower()
    fragment = unquote(parts.fragment)
    if scheme in _EXTERNAL:
        return 'external', href, ''
    if len(scheme) == 1:                       # Windows path: 'C:\...'
        path = href.split('#', 1)[0]
    elif scheme == 'file':
        path = url2pathname(parts.path)
    elif not parts.path and not parts.netloc:
        return 'anchor', None, fragment
    else:
        path = unquote(parts.path)
    if not os.path.isabs(path):
        path = os.path.join(current_dir or '', path)
    path = os.path.normpath(path)
    ext = os.path.splitext(path)[1].lower()
    kind = 'tutorial' if ext == '.md' else 'animation' if ext in ('.html', '.htm') else 'file'
    return kind, path, fragment


def scroll_to_anchor(browser, fragment):
    """Scroll a QTextBrowser to a paragraph; a link written with the
    heading text instead of its anchor is tried as a slug too."""
    if not fragment:
        return
    browser.scrollToAnchor(fragment)
    slug = slugify(fragment)
    if slug and slug != fragment:
        browser.scrollToAnchor(slug)


def local_file_url(path, fragment=''):
    """file:/// URL of a local file (file:///C:/... on Windows)."""
    return Path(path).as_uri() + ('#' + fragment if fragment else '')


def _open_with_system(url):
    from qgis.PyQt.QtCore import QUrl
    from qgis.PyQt.QtGui import QDesktopServices
    QDesktopServices.openUrl(QUrl(url))


def follow_link(href, current_dir, browser, open_tutorial=None, open_animation=None, open_external=None):
    """Do what a click on ``href`` should do and return its kind
    ('missing' when a local target does not exist): scroll to the
    paragraph, open the other tutorial (open_tutorial(path, fragment)), the
    animation (open_animation(path)), else hand the URL to the system."""
    open_external = open_external or _open_with_system
    kind, target, fragment = classify_link(href, current_dir)
    if kind == 'anchor':
        scroll_to_anchor(browser, fragment)
    elif kind == 'external':
        open_external(target)
    elif not os.path.isfile(target):
        kind = 'missing'
    elif kind == 'tutorial' and open_tutorial is not None:
        open_tutorial(target, fragment)
    elif kind == 'animation' and open_animation is not None:
        open_animation(target)
    else:
        open_external(local_file_url(target, fragment))
    return kind
