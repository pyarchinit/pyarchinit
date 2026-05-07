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
    

if QGIS_AVAILABLE:
    # Qt-only symbols may be defined here in future phases.
    pass
