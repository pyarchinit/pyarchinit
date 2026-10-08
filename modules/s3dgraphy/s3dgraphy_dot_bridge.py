#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
S3DGraphy DOT Bridge
Integration between s3dgraphy Extended Matrix and PyArchInit DOT/GraphML converters
"""

import os
import sys
import json
import tempfile
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from modules.utility.pyarchinit_home import pyarchinit_home

# Import s3dgraphy integration
from .s3dgraphy_integration import S3DGraphyIntegration
# em.json è il formato di lavoro dell'Extended Matrix (A4, spec
# 2026-10-07): la finestra usa la stessa funzione del menu, così il file
# che esce da qui e quello che esce da lì sono lo stesso file.
from .em_export import EmExportError, export_site, open_in_emstudio


def read_graph_for_import(path):
    """Il grafo di un file da importare, scelto dall'estensione.

    em.json è il formato di lavoro; il GraphML resta accettato perché è
    la via d'ingresso dei file yEd di prima (A4: «GraphML sopravvive solo
    come import una tantum»). Ritorna ``(graph, warnings)``.
    """
    name = str(path).lower()
    if name.endswith(".json"):
        from s3dgraphy.importer.emjson_importer import import_emjson
        return import_emjson(str(path))
    if name.endswith(".graphml"):
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
        except ImportError:
            from s3dgraphy.importer.graphml_importer import GraphMLImporter
        return GraphMLImporter(filepath=str(path)).parse(), []
    raise ValueError(
        "Non so leggere «%s»: serve un em.json (o un .graphml di yEd)."
        % os.path.basename(str(path)))


def _pyarchinit_plugin():
    """Il plugin caricato in QGIS, o None fuori da QGIS."""
    try:
        from qgis import utils as _qgis_utils
        return _qgis_utils.plugins.get("pyarchinit")
    except Exception:                               # noqa: BLE001
        return None


def open_exported_emjson(exported_files):
    """Apre in EMStudio l'em.json appena esportato. False se non c'è."""
    path = (exported_files or {}).get("emjson")
    if not path:
        return False
    return bool(open_in_emstudio(path))

# Make QGIS imports optional
try:
    from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                     QLabel, QPushButton, QComboBox,
                                     QCheckBox, QGroupBox, QMessageBox,
                                     QFileDialog, QProgressBar,
                                     QTabWidget, QWidget, QLineEdit)
    from qgis.PyQt.QtCore import Qt
    from qgis.core import QgsMessageLog, Qgis
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class S3DGraphyDotBridge:
    """
    Bridge class that converts between s3dgraphy Extended Matrix format
    and PyArchInit DOT/GraphML formats for yEd compatibility
    """
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.s3d_integration = S3DGraphyIntegration(db_manager)

    def _connection_url(self):
        """La stringa di connessione del progetto, come la legge il menu."""
        from modules.db.pyarchinit_conn_strings import Connection
        return Connection().conn_str()

    def s3dgraphy_to_dot(self, site: str, area: Optional[str] = None) -> str:
        """
        Convert s3dgraphy Extended Matrix data to DOT format
        
        Args:
            site: Site name
            area: Optional area filter
            
        Returns:
            DOT format string
        """
        # Import data into s3dgraphy
        if not self.s3d_integration.import_from_pyarchinit(site, area):
            return ""
            
        # Build DOT string from s3dgraphy graph
        dot_lines = []
        dot_lines.append('digraph "Extended_Matrix" {')
        dot_lines.append('    charset="UTF-8";')
        dot_lines.append('    rankdir=TB;')
        dot_lines.append('    node [shape=rectangle];')
        dot_lines.append('')
        
        # Add nodes
        if self.s3d_integration.graph:
            for node in self.s3d_integration.graph.nodes:
                # Skip geo_position nodes
                if hasattr(node, 'node_type') and node.node_type == 'geo_position':
                    continue
                    
                # Build node attributes
                attrs = []
                
                # Map s3dgraphy node types to PyArchInit types
                unit_type = getattr(node, 'unita_tipo', 'US')
                label = f"{unit_type}{getattr(node, 'us', '')}"
                
                # Add period/phase info
                periodo = getattr(node, 'periodo', '')
                fase = getattr(node, 'fase', '')
                if periodo and fase:
                    label += f"_{periodo}_{fase}"
                
                # Add descriptions
                d_strat = getattr(node, 'd_stratigrafica', '')
                d_interp = getattr(node, 'd_interpretativa', '')
                if d_strat or d_interp:
                    description = f"{d_strat} | {d_interp}".strip(' | ')
                    label += f"_{description}"
                
                attrs.append(f'label="{label}"')
                
                # Resolve fill color via VocabProvider's visual rules;
                # fall back to a small hardcoded table (kept for offline
                # callers / cases where ext_libs/s3dgraphy is missing) and
                # then to a generic #CCCCCC.
                fillcolor = self._fill_color_for(unit_type)
                attrs.append(f'fillcolor="{fillcolor}"')
                attrs.append('style="filled"')
                
                # Add node to DOT
                attrs_str = ' [' + ', '.join(attrs) + ']' if attrs else ''
                dot_lines.append(f'    "{node.node_id}"{attrs_str};')
            
            dot_lines.append('')
            
            # Add edges
            for edge in self.s3d_integration.graph.edges:
                # Map Extended Matrix relationships to PyArchInit
                edge_style = ""
                if edge.edge_type == 'has_same_time':
                    edge_style = ' [style="dashed"]'
                elif edge.edge_type == 'generic_connection':
                    edge_style = ' [style="dotted"]'
                    
                dot_lines.append(f'    "{edge.edge_source}" -> "{edge.edge_target}"{edge_style};')
        
        dot_lines.append('}')
        dot_content = '\n'.join(dot_lines)
        return dot_content
    
    def export_integrated_matrix(self, site: str, area: Optional[str] = None,
                                output_dir: str = None, formats: List[str] = None,
                                groups: Optional[List[str]] = None,
                                primary_priority: Optional[List[str]] = None,
                                validate: bool = True
                                ) -> Dict[str, str]:
        """
        Export Extended Matrix in multiple formats with s3dgraphy integration

        Args:
            site: Site name
            area: Optional area filter
            output_dir: Output directory (default: temp)
            formats: List of formats to export ['dot', 'emjson', 'phased']
                ('json' is accepted as a synonym of 'emjson')
            groups: AI06 — list of group dimensions to materialize into
                yEd folder nodes (subset of {area, struttura, attivita,
                settore, ambient, saggio, quad_par, adhoc}). Default
                None / [] preserves AC-2 byte-identical baseline.
            primary_priority: AI07 — optional list of dimension names
                ordered from highest to lowest priority for the
                ``is_primary`` selection on is_in_location edges. When
                None, ``DEFAULT_PRIMARY_PRIORITY`` is used. Toponym is
                always excluded from primary regardless.
            validate: when False, skip the stratigraphic sequence check
                (the dialog's own checkbox, which until 2026-10-08 was
                built and never read).

        Returns:
            Dictionary of format: filepath
        """
        if formats is None:
            formats = ['dot', 'emjson']
            
        if output_dir is None:
            output_dir = tempfile.gettempdir()
            
        exported_files = {}
        base_name = f"Extended_Matrix_{site}"
        if area:
            base_name += f"_{area}"
            
        # Import data into s3dgraphy
        if not self.s3d_integration.import_from_pyarchinit(site, area):
            return exported_files
            
        # Validate sequence (only when asked: the dialog's checkbox)
        warnings = (self.s3d_integration.validate_stratigraphic_sequence()
                    if validate else [])
        if warnings and QGIS_AVAILABLE:
            QgsMessageLog.logMessage(
                f"Validation warnings: {'; '.join(warnings)}",
                "PyArchInit", Qgis.Warning
            )
        
        # Export DOT format
        if 'dot' in formats:
            dot_path = os.path.join(output_dir, f"{base_name}.dot")
            dot_content = self.s3dgraphy_to_dot(site, area)
            if dot_content:
                with open(dot_path, 'w', encoding='utf-8') as f:
                    f.write(dot_content)
                exported_files['dot'] = dot_path
        
        # A4 (spec 2026-10-07): the GraphML export retired — em.json is the
        # working format (Extended Matrix menu) and EMStudio the viewer.
        # A 'graphml' entry in *formats* is ignored.
        if 'emjson' in formats or 'json' in formats:
            try:
                path, nodes, edges, warn = export_site(
                    self._connection_url(), site, output_dir)
                exported_files['emjson'] = path
                exported_files['emjson_counts'] = (nodes, edges, warn)
            except EmExportError as e:
                exported_files['emjson_error'] = str(e)
        
        # Export phased matrix
        if 'phased' in formats:
            phased_path = os.path.join(output_dir, f"{base_name}_phased.json")
            if self.s3d_integration.export_phased_matrix(phased_path):
                exported_files['phased'] = phased_path

        return exported_files
    
    # Legacy fallback used when VocabProvider's get_visual_rule() returns
    # nothing for a given unit type (e.g. ext_libs/s3dgraphy missing).
    _LEGACY_FILL_FALLBACK = {
        'US': '#FFFFFF',
        'USM': '#C0C0C0',
        'USD': '#FFFFFF',
        'SF': '#FFFFFF',
        'VSF': '#000000',
        'CON': '#000000',
    }

    def _fill_color_for(self, unit_type: str) -> str:
        """Resolve a node fill color via VocabProvider, with fallbacks.

        Order: VocabProvider.get_visual_rule(unit_type).fill →
        legacy hardcoded table → generic #CCCCCC.
        """
        try:
            from modules.s3dgraphy.sync import get_vocab_provider
            provider = get_vocab_provider()
            rule = provider.get_visual_rule(unit_type)
            if rule and rule.fill:
                return rule.fill
        except Exception:
            pass
        return self._LEGACY_FILL_FALLBACK.get(unit_type, '#CCCCCC')


if QGIS_AVAILABLE:
    class S3DGraphyExportDialog(QDialog):
        """
        Dialog for configuring integrated s3dgraphy/yEd export
        """
        
        def __init__(self, parent=None, db_manager=None, site=None, area=None):
            super().__init__(parent)
            self.db_manager = db_manager
            self.bridge = S3DGraphyDotBridge(db_manager)
            self.site = site
            self.area = area
            self.exported_files = {}
            self._last_preview_result = None
            self._last_preview_path = None
            self._last_source_path = None
            
            self.setWindowTitle("Export Extended Matrix - Integrated s3dgraphy + yEd")
            self.setMinimumWidth(500)
            self.setupUI()
            
        def setupUI(self):
            layout = QVBoxLayout()

            # Title (unchanged from AI03)
            title = QLabel("<h3>Extended Matrix — s3dgraphy Bridge</h3>")
            layout.addWidget(title)

            # Tabs
            self.tabs = QTabWidget()
            layout.addWidget(self.tabs)

            # ---- Tab "Export" — existing AI03 body, untouched ----
            export_tab = QWidget()
            export_layout = QVBoxLayout()

            desc = QLabel(
                "Esporta la matrice del sito. «em.json» è il formato "
                "dell'Extended Matrix: lo apre EMStudio e lo legge il nodo "
                "StratiGraph. «DOT» serve a Graphviz per la matrice di "
                "Harris classica."
            )
            desc.setWordWrap(True)
            export_layout.addWidget(desc)

            format_group = QGroupBox("Formati")
            format_layout = QVBoxLayout()
            self.cb_dot = QCheckBox("DOT (Graphviz) — matrice di Harris")
            self.cb_dot.setChecked(True)
            format_layout.addWidget(self.cb_dot)
            # A4 (spec 2026-10-07): the GraphML export retired — the matrix
            # travels as em.json (Extended Matrix menu), GraphML survives
            # only as the one-time IMPORT from yEd.
            self.cb_json = QCheckBox("em.json (Extended Matrix, per EMStudio)")
            self.cb_json.setChecked(True)
            format_layout.addWidget(self.cb_json)
            self.cb_phased = QCheckBox("Matrice per fasi (analisi cronologica)")
            self.cb_phased.setChecked(False)
            format_layout.addWidget(self.cb_phased)
            format_group.setLayout(format_layout)
            export_layout.addWidget(format_group)

            # Le due opzioni yEd (suggerimenti di auto-layout, colori per
            # periodo) parlavano al writer GraphML, ritirato in A4: erano
            # caselle che non facevano niente. Resta quella che conta, e
            # ora viene davvero letta.
            options_group = QGroupBox("Opzioni")
            options_layout = QVBoxLayout()
            self.cb_validate = QCheckBox(
                "Controlla la sequenza stratigrafica e segnala i problemi")
            self.cb_validate.setChecked(True)
            options_layout.addWidget(self.cb_validate)
            options_group.setLayout(options_layout)
            export_layout.addWidget(options_group)

            self.progress = QProgressBar()
            self.progress.setVisible(False)
            export_layout.addWidget(self.progress)

            export_btn_layout = QHBoxLayout()
            self.btn_export = QPushButton("Esporta")
            self.btn_export.clicked.connect(self.on_export)
            export_btn_layout.addWidget(self.btn_export)
            export_layout.addLayout(export_btn_layout)

            # I comandi dell'Extended Matrix che stanno nel menu, accanto
            # all'export che li riguarda. Non riscrivono niente: chiamano
            # gli stessi slot del plugin, così restano una cosa sola.
            em_group = QGroupBox("Extended Matrix")
            em_layout = QHBoxLayout()
            self.btn_open_emstudio = QPushButton("Apri in EMStudio")
            self.btn_open_emstudio.setEnabled(False)
            self.btn_open_emstudio.setToolTip(
                "Si attiva dopo un'esportazione em.json riuscita.")
            self.btn_open_emstudio.clicked.connect(self._on_open_emstudio)
            em_layout.addWidget(self.btn_open_emstudio)

            self.btn_room_delivery = QPushButton("Consegna alla stanza…")
            self.btn_room_delivery.clicked.connect(
                lambda: self._call_plugin_slot("_run_room_delivery"))
            em_layout.addWidget(self.btn_room_delivery)

            self.btn_room_open = QPushButton("Apri la stanza")
            self.btn_room_open.clicked.connect(
                lambda: self._call_plugin_slot("_open_rooms_door"))
            em_layout.addWidget(self.btn_room_open)

            if _pyarchinit_plugin() is None:
                for b in (self.btn_room_delivery, self.btn_room_open):
                    b.setEnabled(False)
                    b.setToolTip(
                        "Disponibile dentro QGIS, con il plugin pyArchInit "
                        "caricato.")
            em_group.setLayout(em_layout)
            export_layout.addWidget(em_group)

            export_tab.setLayout(export_layout)
            self.tabs.addTab(export_tab, "Export")

            # ---- Tab "Import" — NEW (AI04) ----
            import_tab = QWidget()
            import_layout = QVBoxLayout()

            import_desc = QLabel(
                "Riporta nel database un em.json dell'Extended Matrix "
                "(EMStudio, nodo StratiGraph). Si accetta ancora un "
                ".graphml di yEd, per i file di prima. Di norma è una "
                "prova a vuoto: prima «Anteprima», si guarda la "
                "differenza, poi «Applica»."
            )
            import_desc.setWordWrap(True)
            import_layout.addWidget(import_desc)

            file_row = QHBoxLayout()
            self.le_import_file = QLineEdit()
            self.le_import_file.setPlaceholderText(
                "/percorso/del/sito.em.json")
            self.btn_browse = QPushButton("Browse…")
            self.btn_browse.clicked.connect(self._on_browse_import)
            file_row.addWidget(self.le_import_file)
            file_row.addWidget(self.btn_browse)
            import_layout.addLayout(file_row)

            # Sito selector — populated from site_table at dialog open
            # time. Includes a "(new sito)" marker that the user can
            # replace by typing a new name (the combo is editable).
            sito_row = QHBoxLayout()
            sito_row.addWidget(QLabel("Sito target:"))
            self.cb_sito = QComboBox()
            self.cb_sito.setEditable(True)
            self.cb_sito.setInsertPolicy(QComboBox.NoInsert)
            self._populate_sito_combo()
            sito_row.addWidget(self.cb_sito, stretch=1)
            import_layout.addLayout(sito_row)

            self.cb_create_epochs = QCheckBox("Crea periodi mancanti se assenti")
            self.cb_create_epochs.setChecked(False)
            import_layout.addWidget(self.cb_create_epochs)

            # AI06: opt-in SQL UPDATE for SQL-derived group kinds
            # (struttura/area/attivita/settore/ambient/saggio/quad_par).
            # Default OFF — D5-C safe default; ad-hoc groups never go
            # to SQL regardless of this flag.
            self.cb_sql_apply_groups = QCheckBox(
                "Update SQL on import (struttura/area/attivita/settore/"
                "ambient/saggio/quad_par)")
            self.cb_sql_apply_groups.setChecked(False)
            import_layout.addWidget(self.cb_sql_apply_groups)

            import_btn_layout = QHBoxLayout()
            self.btn_preview = QPushButton("Anteprima")
            self.btn_preview.clicked.connect(self._on_import_preview)
            self.btn_apply = QPushButton("Applica")
            self.btn_apply.setEnabled(False)
            self.btn_apply.clicked.connect(self._on_import_apply)
            import_btn_layout.addWidget(self.btn_preview)
            import_btn_layout.addWidget(self.btn_apply)
            import_layout.addLayout(import_btn_layout)

            self.import_summary = QLabel("(no preview yet)")
            self.import_summary.setWordWrap(True)
            import_layout.addWidget(self.import_summary)

            import_tab.setLayout(import_layout)
            self.tabs.addTab(import_tab, "Import")

            # ---- Verifica rapporti tab ----
            # Same validators + conservative auto-fix as the former
            # standalone menu dialog, embedded here so the user can verify
            # and repair the stratigraphic rapporti right after importing.
            # db_provider routes the panel at the active project DB (the
            # same backend the import wrote into).
            try:
                from gui.rapporti_check_dialog import RapportiCheckPanel
                self.rapporti_panel = RapportiCheckPanel(
                    db_provider=lambda: self.db_manager)
                self.tabs.addTab(self.rapporti_panel, "Verifica rapporti")
            except Exception as _rc_exc:
                self.rapporti_panel = None
                import logging as _lg
                _lg.getLogger(__name__).warning(
                    "Verifica rapporti tab unavailable: %s", _rc_exc)

            # ---- Common bottom row ----
            self.btn_cancel = QPushButton("Cancel")
            self.btn_cancel.clicked.connect(self.reject)
            layout.addWidget(self.btn_cancel)

            self.setLayout(layout)

        def _on_open_emstudio(self):
            """Apre in EMStudio l'em.json appena esportato."""
            if not open_exported_emjson(self.exported_files):
                QMessageBox.information(
                    self, "EMStudio",
                    "Non ho trovato EMStudio su questo computer, oppure "
                    "non c'è ancora un em.json esportato in questa "
                    "finestra.")

        def _call_plugin_slot(self, name):
            """Chiama lo slot del menu, senza riscriverne la logica."""
            plugin = _pyarchinit_plugin()
            slot = getattr(plugin, name, None) if plugin else None
            if slot is None:
                QMessageBox.information(
                    self, "Extended Matrix",
                    "Comando disponibile dentro QGIS, con il plugin "
                    "pyArchInit caricato.")
                return
            slot()

        def on_export(self):
            """Handle export button click"""
            # Get output directory
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Output Directory",
                "",
                QFileDialog.ShowDirsOnly
            )
            
            if not output_dir:
                return
            
            # Collect selected formats
            formats = []
            if self.cb_dot.isChecked():
                formats.append('dot')
            if self.cb_json.isChecked():
                formats.append('emjson')
            if self.cb_phased.isChecked():
                formats.append('phased')
            
            if not formats:
                QMessageBox.warning(self, "No Formats Selected",
                                  "Please select at least one export format.")
                return

            # Show progress
            self.progress.setVisible(True)
            self.progress.setMaximum(len(formats))
            self.progress.setValue(0)

            try:
                # Export using bridge
                self.exported_files = self.bridge.export_integrated_matrix(
                    self.site,
                    self.area,
                    output_dir,
                    formats,
                    validate=self.cb_validate.isChecked(),
                )
                
                # Update progress
                self.progress.setValue(len(formats))
                
                # Show results
                if self.exported_files:
                    exported_files = self.exported_files
                    lines = []
                    if 'dot' in exported_files:
                        lines.append(f"✅ DOT  → {exported_files['dot']}")
                    if 'emjson' in exported_files:
                        nodes, edges, warn = exported_files.get(
                            'emjson_counts', (0, 0, []))
                        lines.append(
                            f"✅ em.json → {exported_files['emjson']}\n"
                            f"   {nodes} nodi, {edges} archi")
                        for w in warn:
                            lines.append(f"   ⚠️ {w}")
                    elif 'emjson_error' in exported_files:
                        lines.append(
                            f"❌ em.json non esportato: "
                            f"{exported_files['emjson_error']}")
                    if 'phased' in exported_files:
                        lines.append(f"✅ Phased JSON → {exported_files['phased']}")

                    self.btn_open_emstudio.setEnabled(
                        bool(exported_files.get('emjson')))
                    QMessageBox.information(
                        self,
                        "Esportazione Extended Matrix completata",
                        "\n".join(lines) if lines else "Nothing exported.",
                    )
                    self.accept()
                else:
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        "No files were exported. Check the logs for details."
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Error during export:\n{str(e)}"
                )
            finally:
                self.progress.setVisible(False)

        def _populate_sito_combo(self):
            """Fill the sito combo with distinct values from site_table.

            The combo is editable so the user can type a NEW sito; on
            apply, the GraphIngestor will auto-create the row in
            site_table if it doesn't already exist (#3 from H.4
            extended fixes).

            The current `self.site` (the sito the user was working on
            in the parent form) is preselected when present in
            site_table; otherwise the combo defaults to the first
            entry.
            """
            try:
                self.cb_sito.clear()
                if not self.db_manager:
                    return
                sqlite_path = self.db_manager.get_sqlite_path()
                if sqlite_path is None:
                    return
                import sqlite3
                conn = sqlite3.connect(str(sqlite_path))
                try:
                    rows = conn.execute(
                        "SELECT DISTINCT sito FROM site_table "
                        "WHERE sito IS NOT NULL ORDER BY sito").fetchall()
                finally:
                    conn.close()
                for r in rows:
                    self.cb_sito.addItem(r[0])
                if self.site:
                    idx = self.cb_sito.findText(self.site)
                    if idx >= 0:
                        self.cb_sito.setCurrentIndex(idx)
                    else:
                        # Add the parent-form sito on the fly so the user
                        # can keep using it even if it's not in the DB.
                        self.cb_sito.addItem(self.site)
                        self.cb_sito.setCurrentText(self.site)
            except Exception:
                # Defensive — combo stays empty/editable; user can type
                pass

        def _on_browse_import(self):
            """File picker for the Import tab."""
            path, _ = QFileDialog.getOpenFileName(
                self, "Select GraphML to import", "",
                "Extended Matrix (*.json);;yEd (*.graphml);;"
                "Tutti i file (*)")
            if path:
                self.le_import_file.setText(path)

        def _on_import_preview(self):
            """Run dry-run populate_list and show summary."""
            from pathlib import Path
            from modules.s3dgraphy.sync.graph_ingestor import (
                GraphIngestor, GraphSyncError)
            source_path = self.le_import_file.text().strip()
            if not source_path or not Path(source_path).exists():
                QMessageBox.warning(
                    self, "Nessun file",
                    "Scegli prima un em.json (o un .graphml di yEd).")
                return
            # graphml_path serve solo al ramo yEd dell'ingestore: su un
            # em.json non c'è niente di specifico da reidratare.
            graphml_path = (source_path
                            if source_path.lower().endswith(".graphml")
                            else None)
            try:
                try:
                    graph, _read_warnings = read_graph_for_import(source_path)
                except ValueError as e:
                    QMessageBox.warning(self, "Formato non riconosciuto",
                                        str(e))
                    return
                # PG-UIFix (5.7.8-alpha): GraphIngestor.populate_list
                # accepts db_manager (Path | DbHandle | str) via the
                # _resolve_db_handle shim from Foundation. Both SQLite
                # and PostgreSQL backends supported since PG-C.
                if self.db_manager is None:
                    QMessageBox.critical(
                        self, "No DB",
                        "Import requires an active pyarchinit project.")
                    return
                db_path = self.db_manager
                target_sito = (self.cb_sito.currentText().strip()
                               or self.site)
                if not target_sito:
                    QMessageBox.warning(
                        self, "No sito",
                        "Please select or type the sito target.")
                    return
                try:
                    result = GraphIngestor().populate_list(
                        graph, db_path,
                        sito=target_sito,
                        dry_run=True,
                        create_missing_epochs=self.cb_create_epochs.isChecked(),
                        graphml_path=graphml_path,
                    )
                except TypeError:
                    # Stale module cache: older populate_list without
                    # graphml_path. Fall back without that kwarg so the
                    # user can still run preview (the lossy path —
                    # graphml-specific data keys won't hydrate, but the
                    # rest works).
                    result = GraphIngestor().populate_list(
                        graph, db_path,
                        sito=target_sito,
                        dry_run=True,
                        create_missing_epochs=self.cb_create_epochs.isChecked(),
                    )
            except GraphSyncError as e:
                # AI07/H.5 follow-up: auto-detect missing node_uuid
                # column (Phase 1 migration not yet applied on this DB)
                # and offer to run the backfill in-place. On success,
                # retry the populate_list call once.
                from modules.s3dgraphy.sync.graph_ingestor import (
                    SchemaMismatchError)
                if isinstance(e, SchemaMismatchError):
                    if self._offer_node_uuid_migration(db_path, e):
                        try:
                            result = GraphIngestor().populate_list(
                                graph, db_path,
                                sito=target_sito,
                                dry_run=True,
                                create_missing_epochs=self.cb_create_epochs.isChecked(),
                                graphml_path=graphml_path,
                            )
                        except Exception as retry_err:
                            QMessageBox.critical(
                                self, "Import preview failed (post-migration)",
                                f"{type(retry_err).__name__}: {retry_err}")
                            return
                    else:
                        return
                else:
                    QMessageBox.critical(
                        self, type(e).__name__,
                        f"{type(e).__name__}: {e}")
                    return
            except Exception as e:
                QMessageBox.critical(
                    self, "Import preview failed",
                    f"{type(e).__name__}: {e}")
                return
            self._last_preview_result = result
            self._last_preview_path = graphml_path    # solo per il ramo yEd
            self._last_source_path = source_path
            self.import_summary.setText(
                f"Preview: applied={result.applied} "
                f"(inserted={result.inserted}, updated={result.updated}, "
                f"skipped={result.skipped}, conflicts={len(result.conflicts)}, "
                f"epochs_created={result.epochs_created})")
            self.btn_apply.setEnabled(True)

        def _on_import_apply(self):
            """Run write-mode populate_list."""
            from pathlib import Path
            from modules.s3dgraphy.sync.graph_ingestor import (
                GraphIngestor, GraphSyncError)
            try:
                graph, _read_warnings = read_graph_for_import(
                    self._last_source_path)
                # PG-UIFix (5.7.8-alpha): db_manager pass-through;
                # both backends supported via _resolve_db_handle shim.
                if self.db_manager is None:
                    QMessageBox.critical(
                        self, "No DB",
                        "Import requires an active pyarchinit project.")
                    return
                db_path = self.db_manager
                target_sito = (self.cb_sito.currentText().strip()
                               or self.site)
                if not target_sito:
                    QMessageBox.warning(
                        self, "No sito",
                        "Please select or type the sito target.")
                    return
                try:
                    result = GraphIngestor().populate_list(
                        graph, db_path,
                        sito=target_sito,
                        dry_run=False,
                        create_missing_epochs=self.cb_create_epochs.isChecked(),
                        graphml_path=self._last_preview_path,
                        sql_apply_groups=self.cb_sql_apply_groups.isChecked(),  # NEW (AI06)
                    )
                except TypeError:
                    # Stale module cache fallback (see preview handler).
                    result = GraphIngestor().populate_list(
                        graph, db_path,
                        sito=target_sito,
                        dry_run=False,
                        create_missing_epochs=self.cb_create_epochs.isChecked(),
                    )
            except GraphSyncError as e:
                # AI07/H.5: same auto-migration logic as preview path.
                from modules.s3dgraphy.sync.graph_ingestor import (
                    SchemaMismatchError)
                if isinstance(e, SchemaMismatchError):
                    if self._offer_node_uuid_migration(db_path, e):
                        try:
                            result = GraphIngestor().populate_list(
                                graph, db_path,
                                sito=target_sito,
                                dry_run=False,
                                create_missing_epochs=self.cb_create_epochs.isChecked(),
                                graphml_path=self._last_preview_path,
                                sql_apply_groups=self.cb_sql_apply_groups.isChecked(),
                            )
                        except Exception as retry_err:
                            QMessageBox.critical(
                                self, "Import failed (post-migration)",
                                f"{type(retry_err).__name__}: {retry_err}")
                            return
                    else:
                        return
                else:
                    QMessageBox.critical(self, type(e).__name__, str(e))
                    return
            except Exception as e:
                QMessageBox.critical(
                    self, "Import failed", f"{type(e).__name__}: {e}")
                return
            QMessageBox.information(
                self, "Import complete",
                f"Applied: {result.applied}\n"
                f"  inserted: {result.inserted}\n"
                f"  updated: {result.updated}\n"
                f"  skipped: {result.skipped}\n"
                f"  epochs created: {result.epochs_created}\n"
                f"  conflicts (resolved as graph_wins): {len(result.conflicts)}")
            self.btn_apply.setEnabled(False)

            # Steer the user to the "Verifica rapporti" tab on the site just
            # imported, so they can immediately check / repair its rapporti.
            if getattr(self, "rapporti_panel", None) is not None:
                try:
                    self.rapporti_panel._load_sites()
                    self.rapporti_panel.select_sito(target_sito)
                    self.tabs.setCurrentWidget(self.rapporti_panel)
                except Exception:
                    pass

        def _offer_node_uuid_migration(self, db_input, error) -> bool:
            """Offer to auto-apply the Phase 1 node_uuid backfill migration.

            PG-A (5.7.0-alpha): db_input may be a Path (legacy SQLite call
            sites) or a DbManager / conn-str / DbHandle (new). Backend
            detected via _resolve_db_handle.

            Returns True iff the migration was applied successfully and
            the caller should retry the import.
            """
            try:
                from s3dgraphy.sync._db_handle import _resolve_db_handle
                from ..scripts.migrations._2026_05_node_uuid_backfill_lib import (
                    add_columns, backfill_uuids,
                )
                from ..scripts.migrations._common import (
                    BackupSkipped, auto_backup_postgres, auto_backup_sqlite,
                )
            except ImportError:
                from s3dgraphy.sync._db_handle import _resolve_db_handle
                from scripts.migrations._2026_05_node_uuid_backfill_lib import (
                    add_columns, backfill_uuids,
                )
                from scripts.migrations._common import (
                    BackupSkipped, auto_backup_postgres, auto_backup_sqlite,
                )

            try:
                handle = _resolve_db_handle(db_input)
            except Exception as e:
                QMessageBox.critical(
                    self, "Errore di connessione",
                    f"Impossibile aprire il DB per la migrazione:\n{e}",
                )
                return False

            backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                             + "/" + str(handle.engine.url.database or "")
                             if handle.is_postgres
                             else f"SQLite: {handle.sqlite_path}")
            reply = QMessageBox.question(
                self,
                "Migrazione node_uuid richiesta",
                f"{error}\n\n"
                f"Backend: {backend_label}\n\n"
                f"Il database non ha la colonna `node_uuid` richiesta dal "
                f"bridge s3dgraphy (Phase 1 migration).\n\n"
                f"Vuoi applicare la migrazione adesso?\n"
                f"- Verrà fatto un backup automatico\n"
                f"- La colonna `node_uuid` (TEXT) sarà aggiunta alle "
                f"tabelle stratigrafiche\n"
                f"- A ogni record verrà assegnato un UUID v7",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply != QMessageBox.Yes:
                return False

            try:
                if handle.is_postgres:
                    from pathlib import Path as _P
                    dest_dir = (_P(pyarchinit_home()) / "pyarchinit_DB_folder"
                                / "_pga_backups")
                    try:
                        backup = auto_backup_postgres(
                            handle.engine, tag="node_uuid_backfill",
                            dest_dir=dest_dir,
                        )
                    except BackupSkipped as e:
                        skip = QMessageBox.question(
                            self, "Backup non disponibile",
                            f"{e}\n\nProcedere SENZA backup (sconsigliato)?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No,
                        )
                        if skip != QMessageBox.Yes:
                            return False
                        backup = None
                else:
                    backup = auto_backup_sqlite(
                        handle.sqlite_path, tag="node_uuid_backfill",
                    )
                add_columns(handle)
                counts = backfill_uuids(handle)
            except Exception as mig_err:
                QMessageBox.critical(
                    self, "Errore migrazione",
                    f"La migrazione è fallita:\n{mig_err}",
                )
                return False

            QMessageBox.information(
                self, "Migrazione applicata",
                f"Backup: {backup}\n\nUUID v7 assegnati:\n"
                + "\n".join(f"  {t}: {n}" for t, n in counts.items())
            )
            return True


    def integrate_with_us_usm(us_usm_instance):
        """
        Add integrated export functionality to US_USM interface
        
        Args:
            us_usm_instance: Instance of US_USM class
        """
        def on_integrated_export():
            """Handler for integrated export button"""
            try:
                # Get current site and area
                site = us_usm_instance.comboBox_sito.currentText()
                area = us_usm_instance.comboBox_area.currentText()
                
                if not site:
                    QMessageBox.warning(
                        us_usm_instance,
                        "No Site Selected",
                        "Please select a site before exporting."
                    )
                    return
                
                # Show export dialog
                dialog = S3DGraphyExportDialog(
                    us_usm_instance,
                    us_usm_instance.DB_MANAGER,
                    site,
                    area if area else None
                )
                
                if dialog.exec():
                    # Export was successful
                    pass
                    
            except Exception as e:
                QMessageBox.critical(
                    us_usm_instance,
                    "Export Error",
                    f"Error launching integrated export:\n{str(e)}"
                )
        
        # Connect the existing Extended Matrix button to our integrated export
        if hasattr(us_usm_instance, 'pushButton_export_extended_matrix'):
            # Disconnect existing handler if any
            try:
                us_usm_instance.pushButton_export_extended_matrix.clicked.disconnect()
            except:
                pass
            
            # Connect our integrated handler
            us_usm_instance.pushButton_export_extended_matrix.clicked.connect(on_integrated_export)
            
            # Update button tooltip
            us_usm_instance.pushButton_export_extended_matrix.setToolTip(
                "Export Extended Matrix with s3dgraphy integration\n"
                "Combines s3dgraphy processing with yEd-compatible output"
            )
        
        return on_integrated_export
else:
    # Dummy class when QGIS is not available
    class S3DGraphyExportDialog:
        def __init__(self, *args, **kwargs):
            raise ImportError("QGIS is required for S3DGraphyExportDialog")