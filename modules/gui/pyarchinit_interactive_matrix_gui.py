# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyarchinit_interactive_matrix_gui.ui'
#
# Created: Wed Oct 16 19:41:50 2013
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from mplwidgetmatrix import MplwidgetMatrix


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DialogInteractiveMatrix(object):
    def setupUi(self, DialogInteractiveMatrix):
        DialogInteractiveMatrix.setObjectName(_fromUtf8("DialogInteractiveMatrix"))
        DialogInteractiveMatrix.setWindowModality(QtCore.Qt.WindowModal)
        DialogInteractiveMatrix.resize(697, 644)
        DialogInteractiveMatrix.setMinimumSize(QtCore.QSize(540, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/finds.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogInteractiveMatrix.setWindowIcon(icon)
        self.gridLayout_18 = QtGui.QGridLayout(DialogInteractiveMatrix)
        self.gridLayout_18.setObjectName(_fromUtf8("gridLayout_18"))
        self.widgetMatrix = MplwidgetMatrix(DialogInteractiveMatrix)
        self.widgetMatrix.setObjectName(_fromUtf8("widgetMatrix"))
        self.gridLayout_18.addWidget(self.widgetMatrix, 0, 0, 1, 1)

        self.retranslateUi(DialogInteractiveMatrix)
        QtCore.QMetaObject.connectSlotsByName(DialogInteractiveMatrix)

    def retranslateUi(self, DialogInteractiveMatrix):
        DialogInteractiveMatrix.setWindowTitle(QtGui.QApplication.translate("DialogInteractiveMatrix", "pyArchInit Gestione Scavi - Sistema Matrix Interattivo", None, QtGui.QApplication.UnicodeUTF8))

