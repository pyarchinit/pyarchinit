#!/usr/bin/env python3
"""Test script to verify ComboBox tooltips work correctly"""

import sys
from qgis.PyQt.QtWidgets import QApplication, QMainWindow, QTableWidget, QVBoxLayout, QWidget, QPushButton
from qgis.PyQt.QtCore import Qt

# Import the delegate
from modules.utility.delegateComboBox import ComboBoxDelegate

def test_tooltip_combobox():
    """Test the tooltip functionality in ComboBox"""
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Test ComboBox Tooltips")
    window.setGeometry(100, 100, 600, 400)
    
    # Create central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Create table widget
    table = QTableWidget(5, 3)
    table.setHorizontalHeaderLabels(["Categoria", "Classe", "Definizione"])
    
    # Test data with long names
    test_values = [
        "Ceramica da mensa - sigillata italica decorata a matrice",
        "Ceramica comune - pentole con orlo ingrossato e scanalatura per coperchio",
        "Anfore da trasporto - Dressel 20 per olio betico",
        "Vetro - bottiglie soffiato a stampo con decorazione a nido d'ape",
        "Metallo - fibule in bronzo tipo Aucissa con cerniera"
    ]
    
    # Set delegate for first column
    delegate = ComboBoxDelegate(test_values)
    table.setItemDelegateForColumn(0, delegate)
    
    # Add some sample data
    for row in range(3):
        for col in range(3):
            if col == 0:
                table.setItem(row, col, QTableWidget.QTableWidgetItem("Doppio click per modificare"))
            else:
                table.setItem(row, col, QTableWidget.QTableWidgetItem(f"Dato {row},{col}"))
    
    # Add info button
    info_btn = QPushButton("Doppio click su una cella della prima colonna per vedere il ComboBox con tooltip")
    
    layout.addWidget(info_btn)
    layout.addWidget(table)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_tooltip_combobox()