"""«Send to room…»: a pyArchInit site into a room of a StratiGraph node.

The window only collects four things — the node, the room, its title, the
site — and calls ``modules.stratigraph.node_client``: the browser sign-in
(Authorization Code + PKCE against the node's own realm) and the room import
through s3dgraphy's one engine. Both run in a thread, so QGIS stays usable
while the person completes the sign-in in the browser. The token lives in
this window only and goes with it.
"""
from __future__ import annotations

import json
import os
import re
import tempfile

from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout,
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton,
                                 QTextEdit, QVBoxLayout)
from qgis.core import QgsSettings

SETTINGS_NODE = "pyArchInit/stratigraph/node_url"
DEFAULT_NODE = "https://em.localhost:8443/em"


class _Job(QThread):
    done = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn, parent=None):
        super().__init__(parent)
        self._fn = fn

    def run(self):
        try:
            self.done.emit(self._fn())
        except Exception as exc:                        # noqa: BLE001 — shown to the person
            self.failed.emit(str(exc))


def room_id_for(site: str) -> str:
    """A room id from a site name: one ASCII path segment, no spaces. A name
    with no Latin letters (Greek, Arabic) gets a short id stable for that name."""
    import hashlib
    import unicodedata
    ascii_name = unicodedata.normalize("NFKD", site).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9.-]+", "-", ascii_name.strip().lower()).strip("-")
    if slug:
        return slug
    return "site-" + hashlib.sha1(site.encode("utf-8")).hexdigest()[:8]


class StratiGraphRoomDialog(QDialog):

    def __init__(self, connection_url: str, sites, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Send a site to a StratiGraph room")
        self.connection_url = connection_url
        self.token = None
        self._job = None

        self.node = QLineEdit(QgsSettings().value(SETTINGS_NODE, DEFAULT_NODE))
        self.site = QComboBox()
        self.site.addItems([str(s) for s in sites])
        self.room = QLineEdit()
        self.title = QLineEdit()
        self.dry_run = QCheckBox("Plan only (write nothing on the node)")
        self.who = QLabel("Not signed in")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.btn_sign = QPushButton("Sign in…")
        self.btn_send = QPushButton("Send site")
        self.btn_send.setEnabled(False)

        form = QFormLayout()
        form.addRow("Node", self.node)
        form.addRow("Site", self.site)
        form.addRow("Room id", self.room)
        form.addRow("Room title", self.title)
        form.addRow("", self.dry_run)
        form.addRow("Identity", self.who)
        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_sign)
        buttons.addWidget(self.btn_send)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(buttons)
        root.addWidget(self.log)
        self.resize(560, 460)

        self.site.currentTextChanged.connect(self._site_changed)
        self.btn_sign.clicked.connect(self._sign_in)
        self.btn_send.clicked.connect(self._send)
        self._site_changed(self.site.currentText())

    def _site_changed(self, site: str):
        self.room.setText(room_id_for(site))
        self.title.setText(site)

    def _say(self, text: str):
        self.log.append(text)

    def _busy(self, busy: bool):
        self.btn_sign.setEnabled(not busy)
        self.btn_send.setEnabled(not busy and bool(self.token))

    def _run(self, fn, on_done):
        self._busy(True)
        self._job = _Job(fn, self)
        self._job.done.connect(lambda result: (self._busy(False), on_done(result)))
        self._job.failed.connect(lambda why: (self._busy(False), self._say(f"✖ {why}")))
        self._job.start()

    def _sign_in(self):
        from ..modules.stratigraph import node_client as NC
        node = self.node.text().strip()
        QgsSettings().setValue(SETTINGS_NODE, node)
        self._say(f"Opening the sign-in page of {node} in the browser…")

        def work():
            tokens = NC.sign_in(node)
            return tokens["access_token"], NC.whoami(node, tokens["access_token"])

        def done(result):
            self.token, who = result
            name = who.get("name") or who.get("orcid") or who.get("preferred_username") or "?"
            self.who.setText(f"{name} — may create rooms: {who.get('may_create')}")
            self._say(f"✔ Signed in as {name}")
            self._busy(False)

        self._run(work, done)

    def _send(self):
        from ..modules.stratigraph import node_client as NC
        node, site = self.node.text().strip(), self.site.currentText()
        room, title, dry = self.room.text().strip(), self.title.text().strip(), self.dry_run.isChecked()
        workdir = tempfile.mkdtemp(prefix="pyarchinit-room-")
        self._say(f"{'Planning' if dry else 'Sending'} «{site}» → room {room} …")

        def work():
            return NC.send_site(self.connection_url, site, node=node, room=room,
                                token=self.token, workdir=workdir, title=title,
                                dry_run=dry)

        def done(report):
            self._say(f"✔ {report.get('nodes')} nodes, {report.get('edges')} edges exported "
                      f"({os.path.basename(str(report.get('em_json')))})")
            if dry:
                plan = report.get("plan") or {}
                upload = plan.get("upload") or {}
                self._say(f"  Plan: {upload.get('files', 0)} file(s) to upload, "
                          f"{plan.get('references', 0)} kept as reference — nothing written")
                return
            seeded = report.get("seeded") or {}
            self._say(f"  Operations applied: {seeded.get('applied', 0)}, "
                      f"refused: {seeded.get('refused', 0)}, "
                      f"graphs: {len(seeded.get('graphs') or [])}")
            uploaded = report.get("uploaded") or {}
            self._say(f"  Files uploaded: {uploaded.get('files', 0)}; databases kept as "
                      f"reference: {len(set(report.get('kept_as_reference') or []))}")
            for refusal in (seeded.get("refusals") or [])[:5]:
                self._say(f"  ✖ refused: {json.dumps(refusal, ensure_ascii=False, default=str)[:200]}")
            link = report.get("room_link") or report.get("link")
            if link:
                self._say(f"Room: {link}")

        self._run(work, done)
