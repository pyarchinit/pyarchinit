#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix for Thesaurus hierarchy widgets to show them instead of dialogs
"""

# Replace the on_tma_tipologia_changed method to show widgets instead of dialogs
def on_tma_tipologia_changed(self):
    """Handle TMA tipologia change to show hierarchy options."""
    current_tipologia = self.comboBox_tipologia_sigla.currentText()
    
    # Hide hierarchy widgets by default
    self.hide_hierarchy_widgets()
    
    # Show hierarchy options based on tipologia
    # Correct codes:
    # - 10.3 = Località (no parent needed)
    # - 10.7 = Area (needs Località parent)
    # - 10.15 = Settore (needs Località and Area parent)
    
    if current_tipologia == '10.7':  # Area - needs Località parent
        self.show_area_parent_widgets()
    elif current_tipologia == '10.15':  # Settore - needs Località and Area parent
        self.show_settore_parent_widgets()

def show_area_parent_widgets(self):
    """Show widgets for selecting località parent for area."""
    # Ensure widgets exist
    if not hasattr(self, 'label_parent_localita'):
        self.create_hierarchy_widgets()
    
    # Show località selection
    self.label_parent_localita.show()
    self.comboBox_parent_localita.show()
    
    # Load località options
    self.load_parent_localita_options()
    
    # Hide area selection (not needed for area)
    if hasattr(self, 'label_parent_area'):
        self.label_parent_area.hide()
        self.comboBox_parent_area.hide()

def show_settore_parent_widgets(self):
    """Show widgets for selecting località and area parents for settore."""
    # Ensure widgets exist
    if not hasattr(self, 'label_parent_localita'):
        self.create_hierarchy_widgets()
    
    # Show both località and area selection
    self.label_parent_localita.show()
    self.comboBox_parent_localita.show()
    self.label_parent_area.show()
    self.comboBox_parent_area.show()
    
    # Load località options
    self.load_parent_localita_options()
    
    # Area will be loaded when località is selected

# The following code should replace the methods in Thesaurus.py
# starting from line 754 (on_tma_tipologia_changed) to line 770