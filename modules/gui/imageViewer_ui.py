# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'imageView.ui'
#
# Created: Sun May  2 22:08:16 2010
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DialogViewer(object):
    def setupUi(self, DialogView):
        DialogView.setObjectName("DialogView")
        DialogView.resize(456, 466)
        self.gridLayout = QtGui.QGridLayout(DialogView)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(DialogView)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.scrollArea = QtGui.QScrollArea(DialogView)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 428, 398))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_3 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(DialogView)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DialogView.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DialogView.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogView)

    def retranslateUi(self, DialogView):
        DialogView.setWindowTitle(QtGui.QApplication.translate("DialogView", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

