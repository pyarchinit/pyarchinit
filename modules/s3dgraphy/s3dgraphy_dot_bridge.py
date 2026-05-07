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

# Import s3dgraphy integration
from .s3dgraphy_integration import S3DGraphyIntegration

# Make QGIS imports optional
try:
    from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                     QLabel, QPushButton, QComboBox,
                                     QCheckBox, QGroupBox, QMessageBox,
                                     QFileDialog, QProgressBar)
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
                                output_dir: str = None, formats: List[str] = None) -> Dict[str, str]:
        """
        Export Extended Matrix in multiple formats with s3dgraphy integration
        
        Args:
            site: Site name
            area: Optional area filter
            output_dir: Output directory (default: temp)
            formats: List of formats to export ['dot', 'graphml', 'json', 'phased']
            
        Returns:
            Dictionary of format: filepath
        """
        if formats is None:
            formats = ['dot', 'graphml', 'json']
            
        if output_dir is None:
            output_dir = tempfile.gettempdir()
            
        exported_files = {}
        base_name = f"Extended_Matrix_{site}"
        if area:
            base_name += f"_{area}"
            
        # Import data into s3dgraphy
        if not self.s3d_integration.import_from_pyarchinit(site, area):
            return exported_files
            
        # Validate sequence
        warnings = self.s3d_integration.validate_stratigraphic_sequence()
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
        
        # Export GraphML format via s3dgraphy.GraphMLExporter (AI03 cut-over).
        # Phase 1's DOT->GraphML pipeline is gone; the produced file now has
        # epoch swimlanes, transitive reduction, and full EM 1.5 edge styling.
        if 'graphml' in formats:
            graphml_path = os.path.join(output_dir, f"{base_name}.graphml")
            db_path = None
            if self.db_manager is not None:
                db_path = self.db_manager.get_sqlite_path()
            if db_path is None:
                # PG backend (or no db_manager). Skip GraphML and
                # surface a friendly status — DOT/JSON still produced.
                if QGIS_AVAILABLE:
                    QgsMessageLog.logMessage(
                        "GraphML export requires SQLite backend; "
                        "PostgreSQL support arrives with AI04. "
                        "DOT and JSON exports are unaffected.",
                        "PyArchInit", Qgis.Info,
                    )
                exported_files['graphml_status'] = {
                    'level': 'info',
                    'reason': 'postgresql backend not yet supported',
                }
            else:
                from .sync.graphml_writer import (
                    export_graphml,
                    EmptyGraphError,
                    GraphMLExportError,
                )
                try:
                    result = export_graphml(
                        db_path=db_path,
                        mapping='pyarchinit_us_mapping',
                        output_path=graphml_path,
                        site_filter=site,
                        persist_auxiliary=False,
                    )
                    exported_files['graphml'] = graphml_path
                    exported_files['graphml_result'] = result
                except (FileNotFoundError, EmptyGraphError) as e:
                    exported_files['graphml_status'] = {
                        'level': 'warning',
                        'reason': str(e),
                    }
                    if QGIS_AVAILABLE:
                        QgsMessageLog.logMessage(
                            f"GraphML skipped: {e}",
                            "PyArchInit", Qgis.Warning,
                        )
                except GraphMLExportError as e:
                    import traceback
                    exported_files['graphml_status'] = {
                        'level': 'error',
                        'stage': e.stage,
                        'reason': str(e),
                        'traceback': traceback.format_exc(),
                    }
                    if QGIS_AVAILABLE:
                        QgsMessageLog.logMessage(
                            f"GraphML export failed at {e.stage}: "
                            f"{e.original}",
                            "PyArchInit", Qgis.Critical,
                        )
                        QgsMessageLog.logMessage(
                            traceback.format_exc(),
                            "PyArchInit", Qgis.Critical,
                        )
        
        # Export native s3dgraphy JSON format
        if 'json' in formats:
            json_path = os.path.join(output_dir, f"{base_name}_s3dgraphy.json")
            if self.s3d_integration.export_to_json(json_path):
                exported_files['json'] = json_path
        
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
            
            self.setWindowTitle("Export Extended Matrix - Integrated s3dgraphy + yEd")
            self.setMinimumWidth(500)
            self.setupUI()
            
        def setupUI(self):
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("<h3>Export Extended Matrix with s3dgraphy Integration</h3>")
            layout.addWidget(title)
            
            # Description
            desc = QLabel(
                "This export combines s3dgraphy Extended Matrix processing with "
                "yEd-compatible GraphML output for advanced visualization."
            )
            desc.setWordWrap(True)
            layout.addWidget(desc)
            
            # Format selection
            format_group = QGroupBox("Export Formats")
            format_layout = QVBoxLayout()
            
            self.cb_dot = QCheckBox("DOT Format (Graphviz)")
            self.cb_dot.setChecked(True)
            format_layout.addWidget(self.cb_dot)
            
            self.cb_graphml = QCheckBox("GraphML Format (yEd compatible)")
            self.cb_graphml.setChecked(True)
            format_layout.addWidget(self.cb_graphml)
            
            self.cb_json = QCheckBox("JSON Format (s3dgraphy native)")
            self.cb_json.setChecked(True)
            format_layout.addWidget(self.cb_json)
            
            self.cb_phased = QCheckBox("Phased Matrix (chronological analysis)")
            self.cb_phased.setChecked(False)
            format_layout.addWidget(self.cb_phased)
            
            format_group.setLayout(format_layout)
            layout.addWidget(format_group)
            
            # Processing options
            options_group = QGroupBox("Processing Options")
            options_layout = QVBoxLayout()
            
            self.cb_validate = QCheckBox("Validate stratigraphic sequence")
            self.cb_validate.setChecked(True)
            options_layout.addWidget(self.cb_validate)
            
            self.cb_auto_layout = QCheckBox("Generate yEd auto-layout hints")
            self.cb_auto_layout.setChecked(True)
            options_layout.addWidget(self.cb_auto_layout)
            
            self.cb_period_colors = QCheckBox("Apply period-based coloring")
            self.cb_period_colors.setChecked(True)
            options_layout.addWidget(self.cb_period_colors)

            options_group.setLayout(options_layout)
            layout.addWidget(options_group)
            
            # Progress bar
            self.progress = QProgressBar()
            self.progress.setVisible(False)
            layout.addWidget(self.progress)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            self.btn_export = QPushButton("Export")
            self.btn_export.clicked.connect(self.on_export)
            button_layout.addWidget(self.btn_export)
            
            self.btn_cancel = QPushButton("Cancel")
            self.btn_cancel.clicked.connect(self.reject)
            button_layout.addWidget(self.btn_cancel)
            
            layout.addLayout(button_layout)
            self.setLayout(layout)
        
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
            if self.cb_graphml.isChecked():
                formats.append('graphml')
            if self.cb_json.isChecked():
                formats.append('json')
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
                    formats
                )
                
                # Update progress
                self.progress.setValue(len(formats))
                
                # Show results
                if self.exported_files:
                    exported_files = self.exported_files
                    lines = []
                    if 'dot' in exported_files:
                        lines.append(f"✅ DOT  → {exported_files['dot']}")
                    if 'json' in exported_files:
                        lines.append(f"✅ JSON → {exported_files['json']}")
                    if 'phased' in exported_files:
                        lines.append(f"✅ Phased JSON → {exported_files['phased']}")

                    if 'graphml' in exported_files:
                        r = exported_files.get('graphml_result')
                        if r:
                            lines.append(
                                f"✅ GraphML → {exported_files['graphml']}\n"
                                f"   {r.node_count} nodes, {r.edge_count} edges, "
                                f"{r.epoch_count} epochs, "
                                f"{r.tred_removed_edges} redundancies removed by "
                                f"transitive reduction"
                            )
                            for w in r.warnings:
                                lines.append(f"   ⚠️ {w}")
                        else:
                            lines.append(f"✅ GraphML → {exported_files['graphml']}")
                    elif 'graphml_status' in exported_files:
                        st = exported_files['graphml_status']
                        level = st.get('level', 'warning')
                        glyph = '⚠️' if level == 'warning' else '❌' if level == 'error' else 'ℹ️'
                        reason = st.get('reason', 'unknown')
                        if 'stage' in st:
                            lines.append(
                                f"{glyph} GraphML failed at {st['stage']}: {reason}")
                        else:
                            lines.append(f"{glyph} GraphML skipped: {reason}")

                    QMessageBox.information(
                        self,
                        "Extended Matrix export complete",
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