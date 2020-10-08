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
       
        self.combo_box.currentIndexChanged.connect(self.on_Ucolor)
        #self.combo_box.currentTextChanged.connect(self.on_Ucolor_t)
        self.idx_()
    
    def idx_(self):
        #self.combo_box.setCurrentText(self.on_Ucolor)
        self.combo_box.currentText()
        
    def on_Ucolor(self,s):  
        
        self.combo_box.setCurrentIndex(s)
        
        self.combo_box.currentText()
        return str(self.combo_box.currentText())
        
    # def on_Ucolor_t(self,ss):  
        # idx=ss
        # #self.combo_box.setCurrentText(idx)
        
        # #self.combo_box.currentText()
        # #return str(self.combo_box.currentText())    
   