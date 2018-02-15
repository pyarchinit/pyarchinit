# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'quant_panel_ui_zoo.ui'
#
# Created: Tue Oct 29 19:59:16 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import resources_rc


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_quantPanel_zoo(object):
    def setupUi(self, quantPanel_zoo):
        quantPanel_zoo.setObjectName(_fromUtf8("quantPanel_zoo"))
        quantPanel_zoo.setWindowModality(QtCore.Qt.NonModal)
        quantPanel_zoo.resize(282, 210)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        quantPanel_zoo.setWindowIcon(icon)
        self.gridlayout = QtGui.QGridLayout(quantPanel_zoo)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.radioButtonUsMin = QtGui.QRadioButton(quantPanel_zoo)
        self.radioButtonUsMin.setChecked(True)
        self.radioButtonUsMin.setObjectName(_fromUtf8("radioButtonUsMin"))
        self.gridlayout.addWidget(self.radioButtonUsMin, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 3, 3, 1, 2)
        self.nugget_2 = QtGui.QLineEdit(quantPanel_zoo)
        self.nugget_2.setObjectName(_fromUtf8("nugget_2"))
        self.gridlayout.addWidget(self.nugget_2, 5, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 5, 3, 1, 1)
        self.nugget = QtGui.QLabel(quantPanel_zoo)
        self.nugget.setObjectName(_fromUtf8("nugget"))
        self.gridlayout.addWidget(self.nugget, 5, 2, 1, 1)
        self.label = QtGui.QLabel(quantPanel_zoo)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 1, 2, 1, 1)
        self.model = QtGui.QComboBox(quantPanel_zoo)
        self.model.setObjectName(_fromUtf8("model"))
        self.model.addItem(_fromUtf8(""))
        self.model.addItem(_fromUtf8(""))
        self.model.addItem(_fromUtf8(""))
        self.model.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.model, 3, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 7, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem3, 4, 3, 1, 1)
        self.rang = QtGui.QLineEdit(quantPanel_zoo)
        self.rang.setObjectName(_fromUtf8("rang"))
        self.gridlayout.addWidget(self.rang, 4, 1, 1, 1)
        self.range = QtGui.QLabel(quantPanel_zoo)
        self.range.setObjectName(_fromUtf8("range"))
        self.gridlayout.addWidget(self.range, 4, 2, 1, 1)
        self.label_2 = QtGui.QLabel(quantPanel_zoo)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridlayout.addWidget(self.label_2, 3, 2, 1, 1)
        self.psill = QtGui.QLineEdit(quantPanel_zoo)
        self.psill.setObjectName(_fromUtf8("psill"))
        self.gridlayout.addWidget(self.psill, 1, 1, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem4, 6, 3, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem5, 1, 3, 1, 2)
        spacerItem6 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem6, 6, 1, 1, 1)
        self.calcola1 = QtGui.QPushButton(quantPanel_zoo)
        self.calcola1.setObjectName(_fromUtf8("calcola1"))
        self.gridlayout.addWidget(self.calcola1, 7, 3, 1, 1)

        self.retranslateUi(quantPanel_zoo)
        QtCore.QMetaObject.connectSlotsByName(quantPanel_zoo)

    def retranslateUi(self, quantPanel_zoo):
        quantPanel_zoo.setWindowTitle(QtGui.QApplication.translate("quantPanel_zoo", "Ordina", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonUsMin.setText(QtGui.QApplication.translate("quantPanel_zoo", "US", None, QtGui.QApplication.UnicodeUTF8))
        self.nugget.setText(QtGui.QApplication.translate("quantPanel_zoo", "Nugget", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("quantPanel_zoo", "Psill", None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(0, QtGui.QApplication.translate("quantPanel_zoo", "Sph", None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(1, QtGui.QApplication.translate("quantPanel_zoo", "Exp ", None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(2, QtGui.QApplication.translate("quantPanel_zoo", "Gau", None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(3, QtGui.QApplication.translate("quantPanel_zoo", "Mat", None, QtGui.QApplication.UnicodeUTF8))
        self.range.setText(QtGui.QApplication.translate("quantPanel_zoo", "Range", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("quantPanel_zoo", "Model", None, QtGui.QApplication.UnicodeUTF8))
        self.calcola1.setText(QtGui.QApplication.translate("quantPanel_zoo", "Genera Semivariogramma", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    quantPanel_zoo = QtGui.QDialog()
    ui = Ui_quantPanel_zoo()
    ui.setupUi(quantPanel_zoo)
    quantPanel_zoo.show()
    sys.exit(app.exec_())

