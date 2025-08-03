#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix completo per i widget gerarchici del Thesaurus
"""

# Questo codice dovrebbe sostituire i metodi in Thesaurus.py

def setupUi_additions(self):
    """Aggiunte all'interfaccia dopo setupUi - da chiamare in __init__"""
    # Crea i widget per la gerarchia TMA
    self.create_hierarchy_widgets()
    
    # Connetti il cambio di nome_tabella
    try:
        self.comboBox_nome_tabella.currentTextChanged.disconnect()
    except:
        pass
    self.comboBox_nome_tabella.currentTextChanged.connect(self.on_nome_tabella_changed)

def create_hierarchy_widgets(self):
    """Create hierarchy selection widgets and add them to the UI."""
    # Crea i widget
    self.label_parent_localita = QLabel("Località parent:")
    self.comboBox_parent_localita = QComboBox()
    self.comboBox_parent_localita.setEditable(True)
    
    self.label_parent_area = QLabel("Area parent:")
    self.comboBox_parent_area = QComboBox()
    self.comboBox_parent_area.setEditable(True)
    
    # Connetti i segnali
    self.comboBox_parent_localita.currentTextChanged.connect(self.on_parent_localita_changed)
    
    # Trova dove inserire i widget - dopo tipologia_sigla
    try:
        # Trova il layout principale del form
        # Assumiamo che ci sia un widget principale con un layout
        main_widget = self.findChild(QWidget, "formLayoutWidget")
        if main_widget:
            layout = main_widget.layout()
        else:
            # Prova a trovare il primo QFormLayout
            for widget in self.findChildren(QWidget):
                if widget.layout() and isinstance(widget.layout(), QFormLayout):
                    layout = widget.layout()
                    break
            else:
                # Se non troviamo un form layout, proviamo con il layout principale
                layout = self.layout()
        
        if isinstance(layout, QFormLayout):
            # Trova la riga di tipologia_sigla
            for i in range(layout.rowCount()):
                field_item = layout.itemAt(i, QFormLayout.FieldRole)
                if field_item and field_item.widget() == self.comboBox_tipologia_sigla:
                    # Inserisci dopo questa riga
                    layout.insertRow(i + 1, self.label_parent_localita, self.comboBox_parent_localita)
                    layout.insertRow(i + 2, self.label_parent_area, self.comboBox_parent_area)
                    break
        else:
            # Se non è un form layout, aggiungi in fondo
            print("Warning: Could not find form layout, widgets may not appear correctly")
            
    except Exception as e:
        print(f"Error adding hierarchy widgets: {e}")
    
    # Nascondi inizialmente
    self.hide_hierarchy_widgets()

def on_nome_tabella_changed(self):
    """Handle table name change."""
    current_table = self.comboBox_nome_tabella.currentText()
    
    # Se è TMA materiali archeologici, attiva la gestione gerarchica
    if 'TMA materiali archeologici' in current_table:
        self.setup_tma_hierarchy_widgets()
    else:
        self.hide_hierarchy_widgets()

def setup_tma_hierarchy_widgets(self):
    """Setup hierarchy management widgets for TMA materials."""
    # Connetti il cambio di tipologia
    try:
        self.comboBox_tipologia_sigla.currentTextChanged.disconnect(self.on_tma_tipologia_changed)
    except:
        pass
    self.comboBox_tipologia_sigla.currentTextChanged.connect(self.on_tma_tipologia_changed)
    
    # Controlla la tipologia corrente
    self.on_tma_tipologia_changed()

def on_tma_tipologia_changed(self):
    """Handle TMA tipologia change to show hierarchy options."""
    current_tipologia = self.comboBox_tipologia_sigla.currentText()
    
    # Nascondi tutto di default
    self.hide_hierarchy_widgets()
    
    # Mostra in base alla tipologia
    if current_tipologia == '10.7':  # Area - needs Località parent
        self.show_area_parent_widgets()
    elif current_tipologia == '10.15':  # Settore - needs Località and Area parent
        self.show_settore_parent_widgets()

def hide_hierarchy_widgets(self):
    """Hide all hierarchy selection widgets."""
    if hasattr(self, 'label_parent_localita'):
        self.label_parent_localita.hide()
        self.comboBox_parent_localita.hide()
    if hasattr(self, 'label_parent_area'):
        self.label_parent_area.hide()
        self.comboBox_parent_area.hide()

def show_area_parent_widgets(self):
    """Show widgets for selecting località parent for area."""
    # Mostra solo località
    self.label_parent_localita.show()
    self.comboBox_parent_localita.show()
    
    # Carica le opzioni
    self.load_parent_localita()
    
    # Nascondi area
    self.label_parent_area.hide()
    self.comboBox_parent_area.hide()

def show_settore_parent_widgets(self):
    """Show widgets for selecting località and area parents for settore."""
    # Mostra entrambi
    self.label_parent_localita.show()
    self.comboBox_parent_localita.show()
    self.label_parent_area.show()
    self.comboBox_parent_area.show()
    
    # Carica le località
    self.load_parent_localita()

def load_parent_localita(self):
    """Load available località from thesaurus."""
    self.comboBox_parent_localita.clear()
    self.comboBox_parent_localita.addItem("")  # Opzione vuota
    
    if not self.DB_MANAGER:
        return
        
    # Ottieni lingua corrente
    lingua = self.comboBox_lingua.currentText()
    lang_key = ""
    for key, values in self.LANG.items():
        if lingua in values:
            lang_key = key
            break
    
    # Query località (10.3)
    search_dict = {
        'nome_tabella': "'TMA materiali archeologici'",
        'tipologia_sigla': "'10.3'",
        'lingua': f"'{lang_key}'"
    }
    
    try:
        res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
        
        localita_items = []
        for record in res:
            localita_items.append(f"{record.sigla} - {record.sigla_estesa}")
        
        localita_items.sort()
        self.comboBox_parent_localita.addItems(localita_items)
        
    except Exception as e:
        print(f"Error loading località: {e}")

def on_parent_localita_changed(self):
    """When località selection changes, update available areas."""
    # Solo se il widget area è visibile
    if not hasattr(self, 'comboBox_parent_area') or not self.comboBox_parent_area.isVisible():
        return
        
    # Pulisci e ricarica le aree
    self.comboBox_parent_area.clear()
    self.comboBox_parent_area.addItem("")  # Opzione vuota
    
    selected_localita = self.comboBox_parent_localita.currentText()
    if not selected_localita:
        return
        
    # Estrai sigla
    localita_sigla = selected_localita.split(' - ')[0] if ' - ' in selected_localita else ''
    if not localita_sigla:
        return
        
    if not self.DB_MANAGER:
        return
        
    # Ottieni lingua
    lingua = self.comboBox_lingua.currentText()
    lang_key = ""
    for key, values in self.LANG.items():
        if lingua in values:
            lang_key = key
            break
    
    # Query aree per questa località
    search_dict = {
        'nome_tabella': "'TMA materiali archeologici'",
        'tipologia_sigla': "'10.7'",
        'parent_sigla': f"'{localita_sigla}'",
        'lingua': f"'{lang_key}'"
    }
    
    try:
        res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
        
        area_items = []
        for record in res:
            area_items.append(f"{record.sigla} - {record.sigla_estesa}")
        
        area_items.sort()
        self.comboBox_parent_area.addItems(area_items)
        
    except Exception as e:
        print(f"Error loading areas: {e}")