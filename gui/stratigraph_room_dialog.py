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

from .stratigraph_i18n import t
from qgis.PyQt.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout, QMessageBox,
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton,
                                 QTextEdit, QVBoxLayout)
from qgis.core import QgsSettings

SETTINGS_NODE = "pyArchInit/stratigraph/node_url"
#: the Keycloak client to sign in as; empty = the one the node names
SETTINGS_CLIENT = "pyArchInit/stratigraph/client_id"
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
        self.setWindowTitle(t("title"))
        self.connection_url = connection_url
        self.session = None            # NodeSession: tokens in memory, renewed by itself
        self._job = None

        self.node = QLineEdit(QgsSettings().value(SETTINGS_NODE, DEFAULT_NODE))
        self.site = QComboBox()
        self.site.addItems([str(s) for s in sites])
        self.room = QLineEdit()
        self.title = QLineEdit()
        self.dry_run = QCheckBox(t("plan_only"))
        self.who = QLabel(t("not_signed_in"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.btn_sign = QPushButton(t("sign_in"))
        self.btn_send = QPushButton(t("send_site"))
        self.btn_send.setEnabled(False)
        # both directions with a room that already holds data
        self.btn_compare = QPushButton(t("compare"))
        self.btn_push = QPushButton(t("send_changes"))
        self.btn_pull = QPushButton(t("pull"))
        # the local values a confirmed pull replaced, put back (local only)
        self.btn_restore = QPushButton(t("restore_btn"))
        self.btn_restore.setToolTip(t("restore_tip"))
        self._found = None             # the last contribution (pyArchInit → room)
        self._pull = None              # the last dry pull (room → pyArchInit)

        form = QFormLayout()
        form.addRow(t("f_node"), self.node)
        form.addRow(t("f_site"), self.site)
        form.addRow(t("f_room_id"), self.room)
        form.addRow(t("f_room_title"), self.title)
        form.addRow("", self.dry_run)
        form.addRow(t("f_identity"), self.who)
        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_sign)
        buttons.addWidget(self.btn_send)
        sync = QHBoxLayout()
        sync.addWidget(self.btn_compare)
        sync.addWidget(self.btn_push)
        sync.addWidget(self.btn_pull)
        sync.addWidget(self.btn_restore)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(buttons)
        root.addLayout(sync)
        root.addWidget(self.log)
        self.resize(560, 460)

        self.site.currentTextChanged.connect(self._site_changed)
        self.btn_sign.clicked.connect(self._sign_in)
        self.btn_send.clicked.connect(self._send)
        self.btn_compare.clicked.connect(self._compare)
        self.btn_push.clicked.connect(self._push)
        self.btn_pull.clicked.connect(self._pull_room)
        self.btn_restore.clicked.connect(self._restore)
        self._site_changed(self.site.currentText())

    def _site_changed(self, site: str):
        self.room.setText(room_id_for(site))
        self.title.setText(site)

    def _say(self, text: str):
        self.log.append(text)

    def _has_overwritten(self) -> bool:
        try:
            from ..modules.stratigraph import room_state
            node, site, room = self._target()
            return bool(room_state.overwritten(self.connection_url, site, node, room))
        except Exception:  # noqa: BLE001
            return False

    def _restore(self):
        from ..modules.stratigraph import room_state
        node, site, room = self._target()
        done = room_state.restore_overwritten(self.connection_url, site, node, room)
        self._say(t("restored", n=done["restored"]))
        for what in done["skipped"][:6]:
            self._say(t("restore_skipped", what=what))
        self._busy(False)

    def _say_ambiguous(self, found):
        """Same number, different type: the rapporti towards it are ambiguous."""
        for a in (found or [])[:8]:
            self._say(t("ambiguous_number", us=a["us"], area=a["area"], types=", ".join(a["types"]),
                        n=len(a["referenced_by"]), refs=", ".join(a["referenced_by"][:5])))

    def _busy(self, busy: bool):
        self.btn_sign.setEnabled(not busy)
        signed = not busy and self.session is not None
        self.btn_send.setEnabled(signed)
        self.btn_compare.setEnabled(signed)
        self.btn_push.setEnabled(signed and self._found is not None
                                 and bool(self._found["new_nodes"] or self._found["new_edges"]
                                          or self._found.get("local_edits")
                                          or self._found.get("send_removals")))
        self.btn_pull.setEnabled(signed and self._pull is not None)
        self.btn_restore.setEnabled(not busy and self._has_overwritten())

    def _run(self, fn, on_done):
        self._busy(True)
        self._job = _Job(fn, self)
        self._job.done.connect(lambda result: (self._busy(False), on_done(result)))
        self._job.failed.connect(lambda why: (self._busy(False), self._say(t("error", why=why))))
        self._job.start()

    def _sign_in(self):
        from ..modules.stratigraph import node_client as NC
        node = self.node.text().strip()
        QgsSettings().setValue(SETTINGS_NODE, node)
        self._say(t("opening_signin", node=node))

        def work():
            session = NC.NodeSession.sign_in(
                node, client_id=(QgsSettings().value(SETTINGS_CLIENT, "") or None))
            return session, NC.whoami(node, session.access_token())

        def done(result):
            self.session, who = result
            name = who.get("name") or who.get("orcid") or who.get("preferred_username") or "?"
            self.who.setText(t("may_create", name=name, may=who.get('may_create')))
            self._say(t("signed_in", name=name))
            self._busy(False)

        self._run(work, done)

    def _send(self):
        from ..modules.stratigraph import node_client as NC
        node, site = self.node.text().strip(), self.site.currentText()
        room, title, dry = self.room.text().strip(), self.title.text().strip(), self.dry_run.isChecked()
        workdir = tempfile.mkdtemp(prefix="pyarchinit-room-")
        self._say(t("planning" if dry else "sending", site=site, room=room))

        def work():
            # renewed here if it is about to expire: the node's tokens live minutes
            return NC.send_site(self.connection_url, site, node=node, room=room,
                                token=self.session.access_token(), workdir=workdir,
                                title=title, dry_run=dry)

        def done(report):
            self._say(t("exported", nodes=report.get('nodes'), edges=report.get('edges'),
                        file=os.path.basename(str(report.get('em_json')))))
            if dry:
                plan = report.get("plan") or {}
                upload = plan.get("upload") or {}
                self._say(t("plan", files=upload.get('files', 0), refs=plan.get('references', 0)))
                return
            seeded = report.get("seeded") or {}
            self._say(t("ops", applied=seeded.get('applied', 0), refused=seeded.get('refused', 0),
                        graphs=len(seeded.get('graphs') or [])))
            uploaded = report.get("uploaded") or {}
            self._say(t("uploaded", files=uploaded.get('files', 0),
                        dbs=len(set(report.get('kept_as_reference') or []))))
            records = report.get("records") or {}
            if records:
                self._say(t("records_sent", units=records.get("units", 0),
                            fields=records.get("fields", 0)))
            self._say_ambiguous(report.get("ambiguous_numbers"))
            media = report.get("media") or {}
            if media:
                self._say(t("media_sent", res=media.get('resources', 0), links=media.get('links', 0),
                            missing=len(media.get('missing') or [])))
                other = media.get("other_entities") or {}
                if other:
                    self._say(t("media_local",
                                list=", ".join(f"{k} {v}" for k, v in sorted(other.items()))))
            plans = report.get("plans") or {}
            if plans.get("plans"):
                self._say(t("plans_sent", n=plans["plans"], units=plans.get("units", 0)))
            for refusal in (seeded.get("refusals") or [])[:5]:
                self._say(t("refused", what=json.dumps(refusal, ensure_ascii=False, default=str)[:200]))
            link = report.get("room_link") or report.get("link")
            if link:
                self._say(t("room_link", link=link))

        self._run(work, done)

    # ── both directions with a room that already holds data ──────────────

    def _target(self):
        return self.node.text().strip(), self.site.currentText(), self.room.text().strip()

    def _compare(self):
        from ..modules.stratigraph import room_sync as RS
        node, site, room = self._target()
        workdir = tempfile.mkdtemp(prefix="pyarchinit-room-")
        self._say(t("comparing", site=site, room=room))

        def work():
            token = self.session.access_token()
            found = RS.contribution(self.connection_url, site, node=node, room=room,
                                    token=token, workdir=workdir)
            pulled = RS.pull_room(self.connection_url, site, node=node, room=room,
                                  token=token, workdir=workdir, found=found)
            return found, pulled

        def done(result):
            self._found, self._pull = result
            f, p = self._found, self._pull
            self._say_ambiguous(f.get("ambiguous_numbers"))
            how = f.get("read") or {}
            if how.get("read") == "incremental":
                self._say(t("read_incremental", n=how.get("operations", 0)))
            else:
                self._say(t("read_full"))
            if not f.get("base"):
                self._say(t("no_base_hint"))
            self._say(t("room_to_pa", ins=p['inserted'], upd=p['updated'], fmt=p['format_only'],
                        real=len(p['real'])))
            m = p.get("media") or {}
            if m:
                self._say(t("media_preview", new=m.get('new', 0), known=m.get('known', 0)))
            g = p.get("geometry") or {}
            if g.get("footprints"):
                self._say(t("geometry_preview", new=g.get("inserted", 0) + g.get("updated", 0),
                            same=g.get("same", 0), kept=len(g.get("kept_local") or [])))
            pl = p.get("plans") or {}
            if pl.get("plans"):
                self._say(t("plans_preview", new=pl.get("written", 0), same=pl.get("same", 0),
                            kept=len(pl.get("kept_local") or [])))
            for r in ([] if f.get("base") else p["real"][:8]):
                if r["field"] == "rapporti":
                    self._say(t("rel_diff", us=r['us'], ut=r['unita_tipo'], here=r['only_local'],
                                room=r['only_room']))
                else:
                    self._say(t("field_diff", us=r['us'], field=r['field'], here=r['local'],
                                room=r['room']))
            self._say(t("pa_to_room", n=len(f['new_nodes']), names=f['new_nodes'][:6],
                        edges=f['new_edges']))
            if f.get("base"):
                if f["local_edits"]:
                    self._say(t("local_edits", n=len(f["local_edits"]), list=f["local_edits"][:6]))
                if f.get("removed_relations"):
                    self._say(t("removed_here", n=len(f["removed_relations"]),
                                list=f["removed_relations"][:6]))
                if f["room_edits"]:
                    self._say(t("room_edits", n=len(f["room_edits"]), list=f["room_edits"][:6]))
                if f["removed_in_room"]:
                    self._say(t("removed_in_room", n=f["removed_in_room"]))
                for c in f["conflicts"][:8]:
                    self._say(t("conflict", name=c["name"], field=c["field"], here=c["here"],
                                room=c["room"]))
            elif f["field_changes"]:
                self._say(t("fields_differ", n=len(f['field_changes']), list=f['field_changes'][:5]))
            if f["room_only"]:
                self._say(t("room_only", n=f['room_only']))
            self._busy(False)

        self._run(work, done)

    def _push(self):
        from ..modules.stratigraph import room_sync as RS
        node, _site, room = self._target()

        def work():
            return RS.push_new(self._found, node=node, room=room, token=self.session.access_token())

        def done(result):
            self._say(t("changes_sent", applied=result.get('applied', 0),
                        refused=len(result.get('refused') or []), uploaded=result.get('uploaded', 0),
                        fields=result.get('fields', 0), removals=result.get('removals', 0)))
            self._found = None
            self._busy(False)

        self._run(work, done)

    def _pull_room(self):
        from ..modules.stratigraph import room_sync as RS
        node, site, room = self._target()
        pulled = self._pull or {}
        force = False
        if pulled.get("base"):
            # with a base: only local work not yet sent can be overwritten
            u = pulled.get("unsent") or {}
            items = ([f"{n} · {fld}" for n, fld in u.get("edits", [])]
                     + [f"{c.get('name')} · {c.get('field')}: «{c.get('here')}» / «{c.get('room')}»"
                        for c in u.get("conflicts", [])]
                     + ["− " + " ".join(map(str, r)) for r in u.get("removals", [])])
            question = t("unsent_question", lines="\n".join(items[:12])) if items else None
        else:
            drops = [r for r in pulled.get("real", []) if r.get("only_local")]
            question = (t("pull_question", lines="\n".join(
                f"{r['unita_tipo']} {r['us']}: {r['only_local']}" for r in drops[:10]))
                if drops else None)
        if question:
            answer = QMessageBox.question(self, t("pull"), question)
            if answer != QMessageBox.StandardButton.Yes:
                self._say(t("pull_cancelled"))
                return
            force = True
        workdir = tempfile.mkdtemp(prefix="pyarchinit-room-")

        def work():
            return RS.pull_room(self.connection_url, site, node=node, room=room,
                                token=self.session.access_token(), workdir=workdir,
                                apply=True, force=force)

        def done(report):
            self._say(t("pulled", room=room, ins=report['inserted'], upd=report['updated']))
            m = report.get("media") or {}
            if m:
                self._say(t("media_pulled", down=m.get('downloaded', 0), imp=m.get('imported', 0),
                            rel=m.get('relinked', 0), known=m.get('known', 0)))
            g = report.get("geometry") or {}
            if g.get("footprints"):
                self._say(t("geometry_pulled", new=g.get("inserted", 0) + g.get("updated", 0),
                            same=g.get("same", 0), kept=len(g.get("kept_local") or [])))
                for item in (g.get("kept_local") or [])[:6]:
                    self._say(t("geometry_kept", what=item))
            pl = report.get("plans") or {}
            if pl.get("plans"):
                self._say(t("plans_pulled", new=pl.get("written", 0), feat=pl.get("features", 0),
                            same=pl.get("same", 0), kept=len(pl.get("kept_local") or [])))
                for item in (pl.get("kept_local") or [])[:6]:
                    self._say(t("geometry_kept", what=item))
            if report.get("applied") and not report.get("errors"):
                # the fields pyArchInit computes, computed again (GUI thread)
                try:
                    from ..modules.stratigraph.room_derived import recompute
                    d = recompute(self.connection_url, site)
                    self._say(t("derived_recomputed", d=d["datazione"], c=d["cont_per"],
                                o=sum(d["order_layer"].values()), a=len(d["order_layer"])))
                    for err in d["errors"][:5]:
                        self._say(t("error", why=err))
                except Exception as e:  # noqa: BLE001
                    self._say(t("error", why=f"{type(e).__name__}: {e}"))
            if report.get("relations_kept"):
                self._say(t("relations_kept", n=report["relations_kept"]))
            if report.get("overwritten"):
                self._say(t("overwritten_saved", n=report["overwritten"]))
            self._pull = None
            self._busy(False)

        self._run(work, done)
