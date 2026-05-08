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

        def _store(self):
            from modules.s3dgraphy.sync.paradata_store import ParadataStore
            db_path = self.db_manager.get_sqlite_path() if self.db_manager else None
            if db_path is None:
                QMessageBox.critical(
                    self, "No SQLite DB",
                    "Paradata management requires a SQLite-backed pyarchinit project.")
                return None
            return ParadataStore(db_path, self.sito)

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

        def _on_add_author(self):
            store = self._store()
            if store is None:
                return
            name = self.le_auth_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Invalid", "Name is required.")
                return
            try:
                store.add_author(
                    name,
                    orcid=self.le_auth_orcid.text().strip() or None,
                    role=self.le_auth_role.text().strip() or None,
                )
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self.le_auth_name.clear()
            self.le_auth_orcid.clear()
            self.le_auth_role.clear()
            self._load_data()

        def _on_add_license(self):
            store = self._store()
            if store is None:
                return
            spdx = self.le_lic_spdx.text().strip()
            if not spdx:
                QMessageBox.warning(self, "Invalid", "SPDX ID is required.")
                return
            try:
                store.add_license(
                    spdx, url=self.le_lic_url.text().strip() or None)
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
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
            try:
                store.add_embargo(
                    until,
                    reason=self.le_emb_reason.text().strip() or None,
                )
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self.le_emb_until.clear()
            self.le_emb_reason.clear()
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
            store = self._store()
            if store is None:
                return
            try:
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
