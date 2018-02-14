# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'quant_panel_ui.ui'
#
# Created: Wed Feb 20 23:44:04 2013
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_quantPanel(object):
    def setupUi(self, quantPanel):
        quantPanel.setObjectName(_fromUtf8("quantPanel"))
        quantPanel.setWindowModality(QtCore.Qt.NonModal)
        quantPanel.resize(635, 340)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        quantPanel.setWindowIcon(icon)
        self.gridlayout = QtGui.QGridLayout(quantPanel)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.label = QtGui.QLabel(quantPanel)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(387, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 1, 1, 4)
        self.FieldsList = QtGui.QListWidget(quantPanel)
        self.FieldsList.setAcceptDrops(True)
        self.FieldsList.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed|QtGui.QAbstractItemView.SelectedClicked)
        self.FieldsList.setDragEnabled(True)
        self.FieldsList.setDragDropOverwriteMode(True)
        self.FieldsList.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.FieldsList.setAlternatingRowColors(True)
        self.FieldsList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.FieldsList.setViewMode(QtGui.QListView.ListMode)
        self.FieldsList.setObjectName(_fromUtf8("FieldsList"))
        self.gridlayout.addWidget(self.FieldsList, 1, 0, 9, 2)
        spacerItem1 = QtGui.QSpacerItem(41, 81, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 1, 2, 5, 1)
        self.FieldListsort = QtGui.QListWidget(quantPanel)
        self.FieldListsort.setAcceptDrops(True)
        self.FieldListsort.setAutoScroll(False)
        self.FieldListsort.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.FieldListsort.setProperty(_fromUtf8("showDropIndicator"), False)
        self.FieldListsort.setDragEnabled(False)
        self.FieldListsort.setDragDropOverwriteMode(False)
        self.FieldListsort.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.FieldListsort.setAlternatingRowColors(True)
        self.FieldListsort.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.FieldListsort.setMovement(QtGui.QListView.Free)
        self.FieldListsort.setViewMode(QtGui.QListView.ListMode)
        self.FieldListsort.setObjectName(_fromUtf8("FieldListsort"))
        self.gridlayout.addWidget(self.FieldListsort, 1, 3, 9, 1)
        self.radioButtonFormeMin = QtGui.QRadioButton(quantPanel)
        self.radioButtonFormeMin.setChecked(True)
        self.radioButtonFormeMin.setObjectName(_fromUtf8("radioButtonFormeMin"))
        self.gridlayout.addWidget(self.radioButtonFormeMin, 1, 4, 1, 1)
        self.radioButtonFormeMax = QtGui.QRadioButton(quantPanel)
        self.radioButtonFormeMax.setEnabled(False)
        self.radioButtonFormeMax.setObjectName(_fromUtf8("radioButtonFormeMax"))
        self.gridlayout.addWidget(self.radioButtonFormeMax, 2, 4, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(91, 171, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem2, 5, 4, 4, 1)
        self.pushButtonRight = QtGui.QPushButton(quantPanel)
        self.pushButtonRight.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButtonRight.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/6_rightArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonRight.setIcon(icon1)
        self.pushButtonRight.setCheckable(False)
        self.pushButtonRight.setAutoDefault(True)
        self.pushButtonRight.setObjectName(_fromUtf8("pushButtonRight"))
        self.gridlayout.addWidget(self.pushButtonRight, 6, 2, 1, 1)
        self.pushButtonLeft = QtGui.QPushButton(quantPanel)
        self.pushButtonLeft.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButtonLeft.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/4_leftArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonLeft.setIcon(icon2)
        self.pushButtonLeft.setCheckable(False)
        self.pushButtonLeft.setAutoDefault(True)
        self.pushButtonLeft.setObjectName(_fromUtf8("pushButtonLeft"))
        self.gridlayout.addWidget(self.pushButtonLeft, 7, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(41, 121, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem3, 8, 2, 2, 1)
        self.pushButtonQuant = QtGui.QPushButton(quantPanel)
        self.pushButtonQuant.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButtonQuant.setCheckable(False)
        self.pushButtonQuant.setAutoDefault(True)
        self.pushButtonQuant.setObjectName(_fromUtf8("pushButtonQuant"))
        self.gridlayout.addWidget(self.pushButtonQuant, 9, 4, 1, 1)
        self.radioButtonFrammenti = QtGui.QRadioButton(quantPanel)
        self.radioButtonFrammenti.setEnabled(True)
        self.radioButtonFrammenti.setObjectName(_fromUtf8("radioButtonFrammenti"))
        self.gridlayout.addWidget(self.radioButtonFrammenti, 3, 4, 1, 1)
        self.radioButtonPeso = QtGui.QRadioButton(quantPanel)
        self.radioButtonPeso.setEnabled(False)
        self.radioButtonPeso.setObjectName(_fromUtf8("radioButtonPeso"))
        self.gridlayout.addWidget(self.radioButtonPeso, 4, 4, 1, 1)

        self.retranslateUi(quantPanel)
        QtCore.QMetaObject.connectSlotsByName(quantPanel)

    def retranslateUi(self, quantPanel):
        quantPanel.setWindowTitle(QtGui.QApplication.translate("quantPanel", "Ordina", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("quantPanel", "Criteri di ordinamento", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonFormeMin.setText(QtGui.QApplication.translate("quantPanel", "Forme minime", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonFormeMax.setText(QtGui.QApplication.translate("quantPanel", "Forme Massime", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonQuant.setText(QtGui.QApplication.translate("quantPanel", "Quantifica", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonFrammenti.setText(QtGui.QApplication.translate("quantPanel", "Frammenti", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonPeso.setText(QtGui.QApplication.translate("quantPanel", "Peso", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
