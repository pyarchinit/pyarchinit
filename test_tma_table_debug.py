#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test to understand why TMA materials table loses data
"""

from qgis.PyQt.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QComboBox, QStyledItemDelegate
from qgis.PyQt.QtCore import Qt
import sys


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        editor.setEditable(True)
        editor.setInsertPolicy(QComboBox.NoInsert)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value:
            editor.setCurrentText(str(value))
    
    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)
        model.setData(index, value, Qt.DisplayRole)
        print(f"Delegate setModelData: row={index.row()}, col={index.column()}, value='{value}'")
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


def test_table_behavior():
    """Test table widget behavior with delegates"""
    app = QApplication(sys.argv)
    
    # Create table
    table = QTableWidget(3, 3)
    table.setHorizontalHeaderLabels(['Category', 'Class', 'Type'])
    
    # Add items to all cells
    for row in range(3):
        for col in range(3):
            table.setItem(row, col, QTableWidgetItem(""))
    
    # Set delegate for first column
    delegate = ComboBoxDelegate(['ceramica', 'vetro', 'metallo'])
    table.setItemDelegateForColumn(0, delegate)
    
    # Show table
    table.show()
    
    def print_table_contents():
        """Print current table contents"""
        print("\nCurrent table contents:")
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    text = item.text()
                    data = item.data(Qt.EditRole)
                    row_data.append(f"'{text}' (data:{data})")
                else:
                    row_data.append("None")
            print(f"Row {row}: {row_data}")
    
    def save_clicked():
        """Simulate save button click"""
        print("\n=== SAVE CLICKED ===")
        
        # Method 1: Direct read
        print("\nMethod 1 - Direct read:")
        print_table_contents()
        
        # Method 2: Force close editor first
        print("\nMethod 2 - After closing editor:")
        if table.state() == QTableWidget.EditingState:
            print("Table is in editing state, closing editor...")
            table.closePersistentEditor(table.currentItem())
        table.setCurrentCell(-1, -1)
        print_table_contents()
        
        # Method 3: Check specific row
        print("\nMethod 3 - Check row 1 specifically:")
        item = table.item(1, 0)
        if item:
            print(f"Row 1, Col 0: text()='{item.text()}', data(EditRole)='{item.data(Qt.EditRole)}', data(DisplayRole)='{item.data(Qt.DisplayRole)}'")
        else:
            print("Row 1, Col 0: No item!")
    
    # Add button to test save
    from qgis.PyQt.QtWidgets import QPushButton, QVBoxLayout, QWidget
    
    main_widget = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(table)
    
    btn = QPushButton("Simulate Save")
    btn.clicked.connect(save_clicked)
    layout.addWidget(btn)
    
    main_widget.setLayout(layout)
    main_widget.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_table_behavior()