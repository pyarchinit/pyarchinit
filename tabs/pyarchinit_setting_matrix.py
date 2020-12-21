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
        
        # self.combo_box.currentTextChanged.connect(self.idx_)
        # # #self.idx_('')
    
    # # @pyqtSlot(str)
    # # def idx_(self,s=''):
        # # self.s=s
        # # self.combo_box.setCurrentText(s)
        # # return self.combo_box.currentText()
    # def color(self):
        
        # return self.idx_()
    
    