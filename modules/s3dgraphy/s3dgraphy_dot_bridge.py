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

# Import DOT converters
try:
    # Add resources directory to path for X11Colors import
    resources_dir = os.path.join(parent_dir, 'resources', 'dbfiles')
    if resources_dir not in sys.path:
        sys.path.insert(0, resources_dir)
    
    import dot
    import dottoxml
except ImportError as e:
    print(f"Error importing DOT modules: {e}")
    # Fallback: try direct import
    from resources.dbfiles import dot
    from resources.dbfiles import dottoxml

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
        self.spatial_groupings = None  # Will store spatial/functional groupings
        
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
                
                # Set colors based on unit type
                color_map = {
                    'US': '#FFFFFF',
                    'USM': '#C0C0C0',
                    'USD': '#FFFFFF',
                    'SF': '#FFFFFF',
                    'VSF': '#000000',
                    'CON': '#000000'
                }
                fillcolor = color_map.get(unit_type, '#FFFFFF')
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
        
        # Apply spatial groupings if configured
        if self.spatial_groupings:
            from .spatial_grouping_manager import SpatialGroupingManager
            manager = SpatialGroupingManager()
            dot_content = manager.apply_grouping_to_dot(dot_content, self.spatial_groupings)
        
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
        
        # Export GraphML format (via DOT conversion)
        if 'graphml' in formats and 'dot' in exported_files:
            graphml_path = os.path.join(output_dir, f"{base_name}.graphml")
            try:
                # Create temporary options object for dottoxml
                class Options:
                    def __init__(self):
                        self.format = 'Graphml'
                        self.verbose = False
                        self.sweep = False
                        self.NodeLabels = True
                        self.EdgeLabels = True
                        self.NodeUml = True
                        self.Arrows = True
                        self.Colors = True
                        self.LumpAttributes = True
                        self.SepChar = '_'
                        self.EdgeLabelsAutoComplete = False
                        self.DefaultArrowHead = 'normal'
                        self.DefaultArrowTail = 'none'
                        self.DefaultNodeColor = '#CCCCFF'
                        self.DefaultEdgeColor = '#000000'
                        self.DefaultNodeTextColor = '#000000'
                        self.DefaultEdgeTextColor = '#000000'
                        self.InputEncoding = 'utf-8'
                        self.OutputEncoding = 'utf-8'
                
                options = Options()
                
                # Convert DOT to GraphML using existing converter
                self._convert_dot_to_graphml(exported_files['dot'], graphml_path, options)
                
                # Enhance GraphML with spatial groupings if configured
                if self.spatial_groupings:
                    from .graphml_spatial_enhancer import GraphMLSpatialEnhancer
                    enhancer = GraphMLSpatialEnhancer()
                    enhancer.enhance_graphml_with_groups(graphml_path, self.spatial_groupings)
                
                exported_files['graphml'] = graphml_path
                
            except Exception as e:
                if QGIS_AVAILABLE:
                    QgsMessageLog.logMessage(
                        f"Error converting to GraphML: {str(e)}",
                        "PyArchInit", Qgis.Warning
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
    
    def _convert_dot_to_graphml(self, dot_file: str, graphml_file: str, options):
        """
        Convert DOT file to GraphML using PyArchInit's dottoxml converter
        """
        # Read DOT file and parse
        with open(dot_file, 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
        
        # Parse nodes and edges using dot.py classes
        nodes = {}
        edges = []
        nid = 1
        eid = 1
        
        for line in content:
            line = line.strip()
            if '->' in line and not line.startswith('#'):
                # Parse edge
                e = dot.Edge()
                e.initFromString(line)
                e.id = eid
                eid += 1
                edges.append(e)
            elif line.startswith('"') and ';' in line:
                # Parse node
                n = dot.Node()
                n.initFromString(line)
                n.id = nid
                nid += 1
                nodes[n.label] = n
        
        # Export to GraphML
        with open(graphml_file, 'w', encoding='utf-8') as o:
            # Note: The original dottoxml.exportGraphml expects epoch_sigla parameter
            # For now, we'll pass an empty list as we're not using epoch-based positioning
            dottoxml.exportGraphml(o, nodes, edges, options, [])


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
            
            # Add spatial grouping option
            self.cb_spatial_grouping = QCheckBox("Configure spatial/functional groupings")
            self.cb_spatial_grouping.setChecked(False)
            options_layout.addWidget(self.cb_spatial_grouping)
            
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
            # Check if spatial grouping is requested
            spatial_groupings = None
            if self.cb_spatial_grouping.isChecked():
                # Import grouping dialog
                from .spatial_grouping_manager import SpatialGroupingDialog
                
                # Get US data from database
                search_dict = {'sito': self.site}
                if self.area:
                    search_dict['area'] = self.area
                    
                us_records = self.db_manager.query_bool(search_dict, 'US')
                
                # Convert to dict format
                us_data = []
                for record in us_records:
                    us_data.append({
                        'sito': record.sito,
                        'area': record.area,
                        'us': record.us,
                        'settore': getattr(record, 'settore', ''),
                        'struttura': getattr(record, 'struttura', ''),
                        'd_stratigrafica': record.d_stratigrafica,
                        'd_interpretativa': record.d_interpretativa,
                        'interpretazione': getattr(record, 'interpretazione', ''),
                        'descrizione': getattr(record, 'descrizione', '')
                    })
                
                # Show grouping dialog
                grouping_dialog = SpatialGroupingDialog(us_data, self)
                if grouping_dialog.exec():
                    spatial_groupings = grouping_dialog.get_groupings()
                else:
                    # User cancelled grouping configuration
                    return
            
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
                # Store spatial groupings in bridge if configured
                if spatial_groupings:
                    self.bridge.spatial_groupings = spatial_groupings
                else:
                    self.bridge.spatial_groupings = None
                
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
                    file_list = "\n".join([f"- {fmt}: {path}" 
                                          for fmt, path in self.exported_files.items()])
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Extended Matrix exported successfully:\n\n{file_list}"
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