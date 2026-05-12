"""ParadataManagerDialog — single-dialog 3-tab CRUD for site-level
paradata (Authors / Licenses / Embargoes).

Triggered by the "Manage paradata" button in the US scheda
(`tabs/US_USM.py`). Uses the qgis.PyQt abstraction for Qt5/Qt6
compatibility (mirrors the AI03/AI04 dialog pattern).
"""
from __future__ import annotations

try:
    from qgis.PyQt.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
        QLineEdit, QFormLayout, QMessageBox, QHeaderView,
        QComboBox,                # NEW (AI06)
    )
    from qgis.PyQt.QtCore import Qt
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


if QGIS_AVAILABLE:
    class ParadataManagerDialog(QDialog):
        """3-tab dialog for Author/License/Embargo CRUD on
        paradata_{sito}.graphml.
        """

        def __init__(self, parent, db_manager, sito: str):
            super().__init__(parent)
            self.db_manager = db_manager
            self.sito = sito
            self.setWindowTitle(f"Manage paradata — {sito}")
            self.setMinimumWidth(700)
            self._setup_ui()
            self._load_data()

        def _setup_ui(self):
            layout = QVBoxLayout()
            title = QLabel(f"<h3>Paradata for site: {self.sito}</h3>")
            layout.addWidget(title)
            desc = QLabel(
                "Manage authorship, licensing and embargo metadata "
                "stored in paradata.graphml (versionable in Git).")
            desc.setWordWrap(True)
            layout.addWidget(desc)

            self.tabs = QTabWidget()
            layout.addWidget(self.tabs)

            self._setup_tab_authors()
            self._setup_tab_licenses()
            self._setup_tab_embargoes()
            self._setup_tab_groups()  # NEW (AI06)

            close = QPushButton("Close")
            close.clicked.connect(self.accept)
            layout.addWidget(close)
            self.setLayout(layout)

        def _setup_tab_authors(self):
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_authors = QTableWidget(0, 3)
            self.table_authors.setHorizontalHeaderLabels(
                ["Name", "ORCID", "Role"])
            self.table_authors.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_authors)

            form = QFormLayout()
            self.le_auth_name = QLineEdit()
            self.le_auth_orcid = QLineEdit()
            self.le_auth_role = QLineEdit()
            form.addRow("Name:", self.le_auth_name)
            form.addRow("ORCID:", self.le_auth_orcid)
            form.addRow("Role:", self.le_auth_role)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add")
            btn_add.clicked.connect(self._on_add_author)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_authors, "author"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Authors")

        def _setup_tab_licenses(self):
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_licenses = QTableWidget(0, 2)
            self.table_licenses.setHorizontalHeaderLabels(
                ["SPDX ID", "URL"])
            self.table_licenses.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_licenses)

            form = QFormLayout()
            self.le_lic_spdx = QLineEdit()
            self.le_lic_url = QLineEdit()
            form.addRow("SPDX ID:", self.le_lic_spdx)
            form.addRow("URL:", self.le_lic_url)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add")
            btn_add.clicked.connect(self._on_add_license)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_licenses, "license"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Licenses")

        def _setup_tab_embargoes(self):
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_embargoes = QTableWidget(0, 2)
            self.table_embargoes.setHorizontalHeaderLabels(
                ["Until", "Reason"])
            self.table_embargoes.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_embargoes)

            form = QFormLayout()
            self.le_emb_until = QLineEdit()
            self.le_emb_until.setPlaceholderText("YYYY-MM-DD")
            self.le_emb_reason = QLineEdit()
            form.addRow("Until:", self.le_emb_until)
            form.addRow("Reason:", self.le_emb_reason)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add")
            btn_add.clicked.connect(self._on_add_embargo)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_embargoes, "embargo"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Embargoes")

        def _setup_tab_groups(self):
            """AI06: 4th tab — ad-hoc US groups CRUD."""
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_groups = QTableWidget(0, 3)
            self.table_groups.setHorizontalHeaderLabels(
                ["Name", "Kind", "US members"])
            self.table_groups.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_groups)

            form = QFormLayout()
            self.le_grp_name = QLineEdit()
            self.cb_grp_kind = QComboBox()
            # AI06: only "adhoc" via UI; SQL-derived kinds enter via
            # round-trip with sql_apply_groups, never user input.
            self.cb_grp_kind.addItems(["adhoc"])
            self.btn_grp_pick_us = QPushButton("Pick US members…")
            self.btn_grp_pick_us.clicked.connect(self._on_pick_us_for_group)
            self._picked_us_uuids = []
            self.lbl_grp_picked = QLabel("0 selected")
            form.addRow("Name:", self.le_grp_name)
            form.addRow("Kind:", self.cb_grp_kind)
            form.addRow("Members:", self.btn_grp_pick_us)
            form.addRow("", self.lbl_grp_picked)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add group")
            btn_add.clicked.connect(self._on_add_group)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_groups, "group"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Groups")

        def _store(self):
            # PG-UIFix (5.7.8-alpha): pass db_manager directly to
            # ParadataStore. The _resolve_db_handle shim (PG-D era)
            # accepts Path | DbHandle | str so both SQLite and
            # PostgreSQL backends work.
            from modules.s3dgraphy.sync.paradata_store import ParadataStore
            if self.db_manager is None:
                QMessageBox.critical(
                    self, "No DB",
                    "Paradata management requires an active pyarchinit "
                    "project.")
                return None
            return ParadataStore(self.db_manager, self.sito)

        def _group_store(self):
            """AI06: GroupStore factory analogous to _store().

            PG-UIFix (5.7.8-alpha): db_manager pass-through; both
            SQLite and PostgreSQL backends supported via
            _resolve_db_handle shim from Foundation.
            """
            from modules.s3dgraphy.sync.group_store import GroupStore
            if self.db_manager is None:
                QMessageBox.critical(
                    self, "No DB",
                    "Group management requires an active pyarchinit "
                    "project.")
                return None
            return GroupStore(self.db_manager, self.sito)

        def _load_data(self):
            store = self._store()
            if store is None:
                return
            try:
                authors = store.list_authors()
                licenses = store.list_licenses()
                embargoes = store.list_embargos()
            except Exception as e:
                QMessageBox.critical(
                    self, "Read failed",
                    f"Cannot load paradata: {type(e).__name__}: {e}")
                return
            self._fill_authors(authors)
            self._fill_licenses(licenses)
            self._fill_embargoes(embargoes)
            # AI06: also load groups (best-effort — failures must not
            # break paradata tabs).
            try:
                gstore = self._group_store()
                if gstore is not None:
                    groups = gstore.list_groups()
                    self._fill_groups(groups)
            except Exception as e:
                self._diag(f"groups load failed: {e}")

        def _fill_authors(self, rows):
            self.table_authors.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_authors.setItem(
                    i, 0, QTableWidgetItem(r.get("name", "")))
                self.table_authors.setItem(
                    i, 1, QTableWidgetItem(r.get("orcid", "")))
                self.table_authors.setItem(
                    i, 2, QTableWidgetItem(r.get("role", "")))
                # Stash uuid in row's first item user data
                self.table_authors.item(i, 0).setData(
                    Qt.UserRole, r["node_uuid"])

        def _fill_licenses(self, rows):
            self.table_licenses.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_licenses.setItem(
                    i, 0, QTableWidgetItem(r.get("spdx_id", "")))
                self.table_licenses.setItem(
                    i, 1, QTableWidgetItem(r.get("url", "")))
                self.table_licenses.item(i, 0).setData(
                    Qt.UserRole, r["node_uuid"])

        def _fill_embargoes(self, rows):
            self.table_embargoes.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_embargoes.setItem(
                    i, 0, QTableWidgetItem(r.get("until_date", "")))
                self.table_embargoes.setItem(
                    i, 1, QTableWidgetItem(r.get("reason", "")))
                self.table_embargoes.item(i, 0).setData(
                    Qt.UserRole, r["node_uuid"])

        def _fill_groups(self, rows):
            """AI06: populate the groups table from
            GroupStore.list_groups() rows. Each row is a dict with
            keys: group_uuid, name, group_kind, member_us_uuids."""
            self.table_groups.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_groups.setItem(
                    i, 0, QTableWidgetItem(r.get("name", "")))
                self.table_groups.setItem(
                    i, 1, QTableWidgetItem(r.get("group_kind", "")))
                count = len(r.get("member_us_uuids", []))
                self.table_groups.setItem(
                    i, 2, QTableWidgetItem(str(count)))
                self.table_groups.item(i, 0).setData(
                    Qt.UserRole, r["group_uuid"])

        def _diag(self, msg: str) -> None:
            """Print to QGIS Python console + stderr — survives even when
            the main pyarchinit logger isn't wired up."""
            try:
                print(f"[ParadataManager] {msg}")
            except Exception:
                pass

        def _on_add_author(self):
            store = self._store()
            if store is None:
                return
            name = self.le_auth_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Invalid", "Name is required.")
                return
            self._diag(f"add_author start: sito={self.sito!r} name={name!r} "
                       f"file={store.file_path}")
            try:
                uuid = store.add_author(
                    name,
                    orcid=self.le_auth_orcid.text().strip() or None,
                    role=self.le_auth_role.text().strip() or None,
                )
                self._diag(f"add_author OK: uuid={uuid} "
                           f"file_size={store.file_path.stat().st_size if store.exists() else 0}")
            except Exception as e:
                self._diag(f"add_author FAILED: {type(e).__name__}: {e}")
                import traceback
                self._diag(traceback.format_exc())
                QMessageBox.critical(
                    self, type(e).__name__,
                    f"Cannot add author: {e}\n\n"
                    f"File: {store.file_path}\n"
                    f"See QGIS Python Console for full traceback.")
                return
            self.le_auth_name.clear()
            self.le_auth_orcid.clear()
            self.le_auth_role.clear()
            self._load_data()
            after = store.list_authors()
            self._diag(f"after refresh: {len(after)} authors in store; "
                       f"file_size={store.file_path.stat().st_size if store.exists() else 0}")

        def _on_add_license(self):
            store = self._store()
            if store is None:
                return
            spdx = self.le_lic_spdx.text().strip()
            if not spdx:
                QMessageBox.warning(self, "Invalid", "SPDX ID is required.")
                return
            self._diag(f"add_license start: spdx={spdx!r} file={store.file_path}")
            try:
                uuid = store.add_license(
                    spdx, url=self.le_lic_url.text().strip() or None)
                self._diag(f"add_license OK: uuid={uuid} "
                           f"file_size={store.file_path.stat().st_size if store.exists() else 0}")
            except Exception as e:
                self._diag(f"add_license FAILED: {type(e).__name__}: {e}")
                import traceback
                self._diag(traceback.format_exc())
                QMessageBox.critical(
                    self, type(e).__name__,
                    f"Cannot add license: {e}\n\nSee QGIS Python Console for traceback.")
                return
            self.le_lic_spdx.clear()
            self.le_lic_url.clear()
            self._load_data()

        def _on_add_embargo(self):
            store = self._store()
            if store is None:
                return
            until = self.le_emb_until.text().strip()
            if not until:
                QMessageBox.warning(self, "Invalid", "Until date is required.")
                return
            self._diag(f"add_embargo start: until={until!r} file={store.file_path}")
            try:
                uuid = store.add_embargo(
                    until,
                    reason=self.le_emb_reason.text().strip() or None,
                )
                self._diag(f"add_embargo OK: uuid={uuid} "
                           f"file_size={store.file_path.stat().st_size if store.exists() else 0}")
            except Exception as e:
                self._diag(f"add_embargo FAILED: {type(e).__name__}: {e}")
                import traceback
                self._diag(traceback.format_exc())
                QMessageBox.critical(
                    self, type(e).__name__,
                    f"Cannot add embargo: {e}\n\nSee QGIS Python Console for traceback.")
                return
            self.le_emb_until.clear()
            self.le_emb_reason.clear()
            self._load_data()

        def _on_pick_us_for_group(self):
            """AI06: open secondary multi-select dialog of US for the
            current sito. Stores selection in self._picked_us_uuids."""
            from qgis.PyQt.QtWidgets import (
                QDialog, QListWidget, QListWidgetItem,
                QDialogButtonBox, QVBoxLayout)

            dlg = QDialog(self)
            dlg.setWindowTitle(f"Pick US for group — {self.sito}")
            dlg.setMinimumWidth(500)
            dlg.setMinimumHeight(400)
            layout = QVBoxLayout()

            lst = QListWidget()
            lst.setSelectionMode(QListWidget.MultiSelection)
            # Load US for sito.
            # PG-UIFix (5.7.8-alpha): rewritten to use SQLAlchemy via
            # the db_manager engine so it works on both SQLite and
            # PostgreSQL backends. Replaces the previous raw
            # sqlite3.connect(...) which was SQLite-only.
            try:
                if self.db_manager is None:
                    QMessageBox.critical(
                        dlg, "No DB",
                        "US picker requires an active pyarchinit project.")
                    return
                from modules.s3dgraphy.sync._db_handle import (
                    _resolve_db_handle)
                from sqlalchemy import text
                _handle = _resolve_db_handle(self.db_manager)
                with _handle.engine.connect() as conn:
                    rows = conn.execute(
                        text(
                            "SELECT node_uuid, us, area, unita_tipo "
                            "FROM us_table WHERE sito = :sito "
                            "ORDER BY us"
                        ),
                        {"sito": self.sito},
                    ).fetchall()
                for node_uuid, us, area, unita_tipo in rows:
                    if not node_uuid:
                        continue
                    label = f"{unita_tipo or 'US'} {us} (area {area or '-'})"
                    item = QListWidgetItem(label)
                    item.setData(Qt.UserRole, node_uuid)
                    lst.addItem(item)
            except Exception as e:
                QMessageBox.critical(dlg, "Load failed", str(e))
                return
            layout.addWidget(lst)

            btns = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            btns.accepted.connect(dlg.accept)
            btns.rejected.connect(dlg.reject)
            layout.addWidget(btns)
            dlg.setLayout(layout)

            if dlg.exec_() == QDialog.Accepted:
                self._picked_us_uuids = [
                    lst.item(i).data(Qt.UserRole)
                    for i in range(lst.count())
                    if lst.item(i).isSelected()
                ]
                self.lbl_grp_picked.setText(
                    f"{len(self._picked_us_uuids)} selected")

        def _on_add_group(self):
            """AI06: add a new ad-hoc group via GroupStore."""
            store = self._group_store()
            if store is None:
                return
            name = self.le_grp_name.text().strip()
            if not name:
                QMessageBox.warning(
                    self, "Invalid", "Group name is required.")
                return
            kind = self.cb_grp_kind.currentText().strip() or "adhoc"
            try:
                uuid = store.add_group(
                    name,
                    group_kind=kind,
                    member_us_uuids=list(self._picked_us_uuids),
                )
                self._diag(f"add_group OK: {uuid}, "
                           f"{len(self._picked_us_uuids)} members")
            except Exception as e:
                import traceback
                self._diag(traceback.format_exc())
                QMessageBox.critical(
                    self, type(e).__name__,
                    f"Cannot add group: {e}")
                return
            self.le_grp_name.clear()
            self._picked_us_uuids = []
            self.lbl_grp_picked.setText("0 selected")
            self._load_data()

        def _on_remove_selected(self, table, label):
            row = table.currentRow()
            if row < 0:
                QMessageBox.information(
                    self, "No selection",
                    f"Select a {label} row to remove.")
                return
            uuid = table.item(row, 0).data(Qt.UserRole)
            if not uuid:
                return
            try:
                if label == "group":
                    # AI06: groups dispatch
                    store = self._group_store()
                    if store is None:
                        return
                    store.remove_group(uuid)
                else:
                    store = self._store()
                    if store is None:
                        return
                    store.remove(uuid)
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self._load_data()


else:
    class ParadataManagerDialog:
        """Fallback when QGIS Qt is not available (CI / test envs).
        Importable but not instantiable."""
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "ParadataManagerDialog requires QGIS PyQt — not available")
