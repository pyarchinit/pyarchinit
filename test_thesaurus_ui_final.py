#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test finale per verificare che i widget del Thesaurus siano visibili
"""

import sys
import os

# Aggiungi il percorso di QGIS se necessario
qgis_path = '/Applications/QGIS.app/Contents/MacOS/share/qgis/python'
if os.path.exists(qgis_path) and qgis_path not in sys.path:
    sys.path.append(qgis_path)

from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QComboBox
from qgis.PyQt.QtCore import Qt

def test_widget_visibility():
    """Test che simula la creazione dei widget nel Thesaurus"""
    
    # Crea un'applicazione di test
    app = QApplication([])
    
    # Crea widget principale
    main_widget = QWidget()
    main_widget.setWindowTitle("Test Thesaurus Hierarchy Widgets")
    main_widget.resize(400, 300)
    
    # Crea un grid layout come in Thesaurus
    gridLayout = QGridLayout()
    main_widget.setLayout(gridLayout)
    
    # Aggiungi alcuni widget di esempio (simulando il form esistente)
    gridLayout.addWidget(QLabel("Nome tabella:"), 0, 0)
    gridLayout.addWidget(QComboBox(), 0, 1)
    
    gridLayout.addWidget(QLabel("Sigla:"), 1, 0)
    gridLayout.addWidget(QComboBox(), 1, 1)
    
    gridLayout.addWidget(QLabel("Tipologia sigla:"), 4, 0)
    tipologia_combo = QComboBox()
    tipologia_combo.addItems(['', '10.3', '10.7', '10.15'])
    gridLayout.addWidget(tipologia_combo, 4, 1)
    
    # Crea i widget gerarchici (come farebbe create_hierarchy_widgets)
    label_parent_localita = QLabel("Località parent:")
    comboBox_parent_localita = QComboBox()
    comboBox_parent_localita.setEditable(True)
    comboBox_parent_localita.addItems(['', 'LOC01 - Festòs', 'LOC02 - Agia Triada'])
    
    label_parent_area = QLabel("Area parent:")
    comboBox_parent_area = QComboBox()
    comboBox_parent_area.setEditable(True)
    comboBox_parent_area.addItems(['', 'AREA01 - Area Sud', 'AREA02 - Area Nord'])
    
    # Aggiungi i widget al layout (come fa il codice modificato)
    gridLayout.addWidget(label_parent_localita, 5, 0)
    gridLayout.addWidget(comboBox_parent_localita, 5, 1)
    
    gridLayout.addWidget(label_parent_area, 6, 0)
    gridLayout.addWidget(comboBox_parent_area, 6, 1)
    
    # Funzione per mostrare/nascondere i widget
    def on_tipologia_changed():
        current_tipologia = tipologia_combo.currentText()
        
        # Nascondi tutto di default
        label_parent_localita.hide()
        comboBox_parent_localita.hide()
        label_parent_area.hide()
        comboBox_parent_area.hide()
        
        # Mostra in base alla tipologia
        if current_tipologia == '10.7':  # Area
            label_parent_localita.show()
            comboBox_parent_localita.show()
            print("Mostrati widget per Area (solo località)")
        elif current_tipologia == '10.15':  # Settore
            label_parent_localita.show()
            comboBox_parent_localita.show()
            label_parent_area.show()
            comboBox_parent_area.show()
            print("Mostrati widget per Settore (località e area)")
        else:
            print("Nessun widget gerarchico da mostrare")
    
    # Connetti il cambio di tipologia
    tipologia_combo.currentTextChanged.connect(on_tipologia_changed)
    
    # Nascondi inizialmente
    label_parent_localita.hide()
    comboBox_parent_localita.hide()
    label_parent_area.hide()
    comboBox_parent_area.hide()
    
    # Mostra il widget
    main_widget.show()
    
    print("Test UI avviato:")
    print("1. Seleziona '10.7' dalla tipologia per vedere il widget località")
    print("2. Seleziona '10.15' dalla tipologia per vedere entrambi i widget")
    print("3. I widget dovrebbero apparire sotto la tipologia sigla")
    
    # Esegui l'applicazione
    app.exec_()

if __name__ == "__main__":
    test_widget_visibility()