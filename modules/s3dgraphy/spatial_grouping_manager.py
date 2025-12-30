#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spatial Grouping Manager for Extended Matrix
Allows grouping US by spatial/functional criteria (area, sector, building parts, etc.)
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Make QGIS imports optional
try:
    from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                     QLabel, QPushButton, QComboBox,
                                     QListWidget, QListWidgetItem,
                                     QCheckBox, QGroupBox, QMessageBox,
                                     QLineEdit, QTableWidget, QTableWidgetItem,
                                     QAbstractItemView, QSplitter)
    from qgis.PyQt.QtCore import Qt
    from qgis.core import QgsMessageLog, Qgis
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class SpatialGroupingManager:
    """
    Manages spatial/functional groupings of stratigraphic units
    for Extended Matrix visualization
    """
    
    def __init__(self):
        self.groupings = {}  # {group_name: [list of US]}
        self.grouping_types = {
            'area': 'Area',
            'settore': 'Settore',
            'struttura': 'Struttura/Edificio',
            'funzione': 'Funzione/Uso',
            'custom': 'Personalizzato'
        }
        
    def create_area_based_groups(self, us_data: List[Dict]) -> Dict[str, List[str]]:
        """
        Create groups based on area field
        """
        area_groups = defaultdict(list)
        for us in us_data:
            area = us.get('area', 'Unknown')
            us_id = f"{us.get('sito', '')}_{area}_{us.get('us', '')}"
            area_groups[f"Area {area}"].append(us_id)
        return dict(area_groups)
    
    def create_sector_based_groups(self, us_data: List[Dict]) -> Dict[str, List[str]]:
        """
        Create groups based on settore field
        """
        sector_groups = defaultdict(list)
        for us in us_data:
            settore = us.get('settore', 'Unknown')
            if settore:
                us_id = f"{us.get('sito', '')}_{us.get('area', '')}_{us.get('us', '')}"
                sector_groups[f"Settore {settore}"].append(us_id)
        return dict(sector_groups)
    
    def create_structure_based_groups(self, us_data: List[Dict]) -> Dict[str, List[str]]:
        """
        Create groups based on struttura field or interpretation
        """
        structure_groups = defaultdict(list)
        for us in us_data:
            us_id = f"{us.get('sito', '')}_{us.get('area', '')}_{us.get('us', '')}"
            
            # Check struttura field
            struttura = us.get('struttura', '')
            if struttura:
                structure_groups[struttura].append(us_id)
            else:
                # Try to infer from interpretation
                interpretation = us.get('d_interpretativa', '').lower()
                if 'muro' in interpretation or 'wall' in interpretation:
                    structure_groups['Muri'].append(us_id)
                elif 'paviment' in interpretation or 'floor' in interpretation:
                    structure_groups['Pavimenti'].append(us_id)
                elif 'tetto' in interpretation or 'roof' in interpretation:
                    structure_groups['Tetti'].append(us_id)
                elif 'fondazion' in interpretation or 'foundation' in interpretation:
                    structure_groups['Fondazioni'].append(us_id)
        
        return dict(structure_groups)
    
    def create_custom_groups(self, us_data: List[Dict], custom_rules: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Create custom groups based on user-defined rules
        
        Args:
            us_data: List of US records
            custom_rules: Dict of {group_name: [list of US numbers or patterns]}
        """
        custom_groups = defaultdict(list)
        
        for group_name, us_patterns in custom_rules.items():
            for us in us_data:
                us_number = str(us.get('us', ''))
                us_id = f"{us.get('sito', '')}_{us.get('area', '')}_{us.get('us', '')}"
                
                # Check if US matches any pattern
                for pattern in us_patterns:
                    if pattern == us_number or pattern in us_number:
                        custom_groups[group_name].append(us_id)
                        break
        
        return dict(custom_groups)
    
    def apply_grouping_to_dot(self, dot_content: str, groupings: Dict[str, List[str]]) -> str:
        """
        Modify DOT content to add subgraph clusters for groupings
        """
        lines = dot_content.split('\n')
        new_lines = []
        
        # Find where to insert subgraphs (after initial declarations)
        insert_pos = 0
        for i, line in enumerate(lines):
            if 'node [' in line or 'charset=' in line or 'rankdir=' in line:
                insert_pos = i + 1
        
        # Add initial lines
        new_lines.extend(lines[:insert_pos])
        new_lines.append('')
        
        # Create subgraphs for each group
        cluster_id = 0
        node_lines = []  # Store node definitions
        
        # First, collect all node definitions
        for line in lines[insert_pos:]:
            if line.strip().startswith('"') and '->' not in line and '{' not in line and '}' not in line:
                node_lines.append(line)
        
        # Create subgraphs
        for group_name, us_list in groupings.items():
            cluster_id += 1
            new_lines.append(f'    subgraph cluster_{cluster_id} {{')
            new_lines.append(f'        label="{group_name}";')
            new_lines.append(f'        style="rounded,filled";')
            new_lines.append(f'        fillcolor="lightgrey";')
            new_lines.append(f'        fontsize=16;')
            new_lines.append(f'        labeljust="l";')
            new_lines.append('')
            
            # Add nodes belonging to this group
            for node_line in node_lines:
                # Extract node ID from line
                if '"' in node_line:
                    node_id = node_line.split('"')[1]
                    if node_id in us_list:
                        new_lines.append('    ' + node_line.strip())
            
            new_lines.append('    }')
            new_lines.append('')
        
        # Add remaining lines (edges and closing)
        for line in lines[insert_pos:]:
            if '->' in line or line.strip() == '}':
                new_lines.append(line)
        
        return '\n'.join(new_lines)


if QGIS_AVAILABLE:
    class SpatialGroupingDialog(QDialog):
        """
        Dialog for configuring spatial/functional groupings
        """
        
        def __init__(self, us_data: List[Dict], parent=None):
            super().__init__(parent)
            self.us_data = us_data
            self.manager = SpatialGroupingManager()
            self.selected_groupings = {}
            
            self.setWindowTitle("Configurazione Raggruppamenti Spaziali/Funzionali")
            self.setMinimumSize(800, 600)
            self.setupUI()
            
        def setupUI(self):
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("<h3>Raggruppamento US per criteri spaziali/funzionali</h3>")
            layout.addWidget(title)
            
            # Main splitter
            splitter = QSplitter(Qt.Orientation.Horizontal)
            
            # Left panel - Grouping options
            left_panel = QGroupBox("Opzioni di Raggruppamento")
            left_layout = QVBoxLayout()
            
            # Grouping type selector
            type_label = QLabel("Tipo di raggruppamento:")
            self.grouping_type = QComboBox()
            for key, value in self.manager.grouping_types.items():
                self.grouping_type.addItem(value, key)
            self.grouping_type.currentIndexChanged.connect(self.on_grouping_type_changed)
            
            left_layout.addWidget(type_label)
            left_layout.addWidget(self.grouping_type)
            
            # Preview button
            self.preview_btn = QPushButton("Anteprima Raggruppamenti")
            self.preview_btn.clicked.connect(self.preview_groupings)
            left_layout.addWidget(self.preview_btn)
            
            # Custom grouping panel
            self.custom_panel = QGroupBox("Raggruppamenti Personalizzati")
            custom_layout = QVBoxLayout()
            
            # Add custom group
            add_layout = QHBoxLayout()
            self.group_name_input = QLineEdit()
            self.group_name_input.setPlaceholderText("Nome gruppo (es. Basilica)")
            add_btn = QPushButton("Aggiungi Gruppo")
            add_btn.clicked.connect(self.add_custom_group)
            add_layout.addWidget(self.group_name_input)
            add_layout.addWidget(add_btn)
            custom_layout.addLayout(add_layout)
            
            # Custom groups table
            self.custom_table = QTableWidget()
            self.custom_table.setColumnCount(3)
            self.custom_table.setHorizontalHeaderLabels(["Gruppo", "US", "Azione"])
            self.custom_table.horizontalHeader().setStretchLastSection(True)
            custom_layout.addWidget(self.custom_table)
            
            self.custom_panel.setLayout(custom_layout)
            left_layout.addWidget(self.custom_panel)
            self.custom_panel.setVisible(False)
            
            left_panel.setLayout(left_layout)
            
            # Right panel - Preview
            right_panel = QGroupBox("Anteprima Raggruppamenti")
            right_layout = QVBoxLayout()
            
            self.preview_list = QListWidget()
            self.preview_list.setSelectionMode(QAbstractItemView.MultiSelection)
            right_layout.addWidget(self.preview_list)
            
            # Group details
            details_label = QLabel("Dettagli gruppo selezionato:")
            right_layout.addWidget(details_label)
            
            self.details_list = QListWidget()
            self.details_list.setMaximumHeight(200)
            right_layout.addWidget(self.details_list)
            
            right_panel.setLayout(right_layout)
            
            # Add panels to splitter
            splitter.addWidget(left_panel)
            splitter.addWidget(right_panel)
            splitter.setStretchFactor(0, 1)
            splitter.setStretchFactor(1, 2)
            
            layout.addWidget(splitter)
            
            # Predefined location groups
            locations_group = QGroupBox("Raggruppamenti Predefiniti per Località")
            locations_layout = QVBoxLayout()
            
            # Common archaeological locations
            self.location_checks = {}
            locations = [
                ("basilica", "Basilica"),
                ("foro", "Foro/Forum"),
                ("terme", "Terme/Baths"),
                ("teatro", "Teatro/Theatre"),
                ("tempio", "Tempio/Temple"),
                ("domus", "Domus/Casa"),
                ("necropoli", "Necropoli"),
                ("via", "Via/Strada"),
                ("porta", "Porta/Gate"),
                ("mura", "Mura/Walls"),
                ("cisterna", "Cisterna"),
                ("acquedotto", "Acquedotto"),
                ("colonnato", "Colonnato"),
                ("giardino", "Giardino/Hortus"),
                ("taberna", "Taberna/Shop")
            ]
            
            # Create checkboxes in grid
            from qgis.PyQt.QtWidgets import QGridLayout
            grid = QGridLayout()
            for i, (key, label) in enumerate(locations):
                cb = QCheckBox(label)
                self.location_checks[key] = cb
                grid.addWidget(cb, i // 3, i % 3)
            
            locations_layout.addLayout(grid)
            
            # Apply locations button
            apply_locations_btn = QPushButton("Applica Raggruppamenti per Località")
            apply_locations_btn.clicked.connect(self.apply_location_groupings)
            locations_layout.addWidget(apply_locations_btn)
            
            locations_group.setLayout(locations_layout)
            layout.addWidget(locations_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            self.ok_btn = QPushButton("Applica")
            self.ok_btn.clicked.connect(self.accept)
            
            self.cancel_btn = QPushButton("Annulla")
            self.cancel_btn.clicked.connect(self.reject)
            
            button_layout.addStretch()
            button_layout.addWidget(self.ok_btn)
            button_layout.addWidget(self.cancel_btn)
            
            layout.addLayout(button_layout)
            self.setLayout(layout)
            
            # Connect preview list selection
            self.preview_list.itemSelectionChanged.connect(self.show_group_details)
        
        def on_grouping_type_changed(self):
            """Handle grouping type change"""
            grouping_type = self.grouping_type.currentData()
            self.custom_panel.setVisible(grouping_type == 'custom')
        
        def preview_groupings(self):
            """Preview groupings based on selected type"""
            grouping_type = self.grouping_type.currentData()
            
            if grouping_type == 'area':
                self.selected_groupings = self.manager.create_area_based_groups(self.us_data)
            elif grouping_type == 'settore':
                self.selected_groupings = self.manager.create_sector_based_groups(self.us_data)
            elif grouping_type == 'struttura':
                self.selected_groupings = self.manager.create_structure_based_groups(self.us_data)
            elif grouping_type == 'custom':
                # Get custom groups from table
                custom_rules = self.get_custom_rules()
                self.selected_groupings = self.manager.create_custom_groups(self.us_data, custom_rules)
            
            self.update_preview_list()
        
        def update_preview_list(self):
            """Update the preview list with current groupings"""
            self.preview_list.clear()
            
            for group_name, us_list in self.selected_groupings.items():
                item = QListWidgetItem(f"{group_name} ({len(us_list)} US)")
                item.setData(Qt.UserRole, group_name)
                self.preview_list.addItem(item)
        
        def show_group_details(self):
            """Show details of selected group"""
            self.details_list.clear()
            
            selected_items = self.preview_list.selectedItems()
            if not selected_items:
                return
            
            # Show US for first selected group
            group_name = selected_items[0].data(Qt.UserRole)
            us_list = self.selected_groupings.get(group_name, [])
            
            for us_id in sorted(us_list):
                # Extract US number from ID
                parts = us_id.split('_')
                if len(parts) >= 3:
                    us_num = parts[-1]
                    self.details_list.addItem(f"US {us_num}")
        
        def add_custom_group(self):
            """Add a custom group"""
            group_name = self.group_name_input.text().strip()
            if not group_name:
                return
            
            # Add to table
            row = self.custom_table.rowCount()
            self.custom_table.insertRow(row)
            
            self.custom_table.setItem(row, 0, QTableWidgetItem(group_name))
            
            # US input
            us_input = QLineEdit()
            us_input.setPlaceholderText("US numbers (comma separated)")
            self.custom_table.setCellWidget(row, 1, us_input)
            
            # Remove button
            remove_btn = QPushButton("Rimuovi")
            remove_btn.clicked.connect(lambda: self.custom_table.removeRow(row))
            self.custom_table.setCellWidget(row, 2, remove_btn)
            
            self.group_name_input.clear()
        
        def get_custom_rules(self) -> Dict[str, List[str]]:
            """Get custom grouping rules from table"""
            rules = {}
            
            for row in range(self.custom_table.rowCount()):
                group_item = self.custom_table.item(row, 0)
                us_widget = self.custom_table.cellWidget(row, 1)
                
                if group_item and us_widget:
                    group_name = group_item.text()
                    us_text = us_widget.text()
                    
                    # Parse US numbers
                    us_list = [us.strip() for us in us_text.split(',') if us.strip()]
                    if us_list:
                        rules[group_name] = us_list
            
            return rules
        
        def apply_location_groupings(self):
            """Apply groupings based on location keywords"""
            location_groups = defaultdict(list)
            
            # Get selected locations
            selected_locations = []
            for key, cb in self.location_checks.items():
                if cb.isChecked():
                    selected_locations.append((key, cb.text()))
            
            if not selected_locations:
                QMessageBox.warning(self, "Nessuna selezione", 
                                  "Seleziona almeno una località")
                return
            
            # Search for US matching location keywords
            for us in self.us_data:
                us_id = f"{us.get('sito', '')}_{us.get('area', '')}_{us.get('us', '')}"
                
                # Check in various fields
                fields_to_check = [
                    us.get('d_stratigrafica', ''),
                    us.get('d_interpretativa', ''),
                    us.get('interpretazione', ''),
                    us.get('descrizione', '')
                ]
                
                text = ' '.join(fields_to_check).lower()
                
                # Check each location
                for key, label in selected_locations:
                    if key in text:
                        location_groups[label].append(us_id)
            
            # Update groupings
            self.selected_groupings = dict(location_groups)
            self.update_preview_list()
            
            if not self.selected_groupings:
                QMessageBox.information(self, "Nessun risultato", 
                                      "Nessuna US trovata per le località selezionate")
        
        def get_groupings(self) -> Dict[str, List[str]]:
            """Get the configured groupings"""
            return self.selected_groupings