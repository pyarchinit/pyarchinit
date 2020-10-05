import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType


from ..gui.pyarchinitConfigDialog import pyArchInitDialog_Config
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Setting_Matrix.ui'))


class Setting_Matrix(QDialog,MAIN_DIALOG_CLASS):
    
    def __init__(self):
       super().__init__()
       self.setupUi(self) 
       self.comboBox.currentTextChanged.connect(self.on_setcolor_pressed)
       #self.mColorButton.clicked(self.Ucolor)
    
    def on_setcolor_pressed(self):
        self.comboBox.setCurrentText(str(self.Ucolor))
        QMessageBox.information(self, 'ok',"colore settato", QMessageBox.Ok)
        return
    
    def Ucolor(self):  
        
        self.comboBox.currentText()
        #return str(self.comboBox.currentText())
    
    