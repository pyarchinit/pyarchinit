# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyarchinit_images_comparision.ui'
#
# Created: Sat Nov 17 17:04:07 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DialogImagesComparision(object):
    def setupUi(self, DialogImagesComparision):
        DialogImagesComparision.setObjectName(_fromUtf8("DialogImagesComparision"))
        DialogImagesComparision.resize(710, 548)
        self.gridLayout = QtGui.QGridLayout(DialogImagesComparision)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.line_3 = QtGui.QFrame(DialogImagesComparision)
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.gridLayout.addWidget(self.line_3, 0, 1, 7, 2)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.widget = Mplwidget(DialogImagesComparision)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(470, 460))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_3.addWidget(self.widget)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(DialogImagesComparision)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout_3, 1, 2, 6, 1)
        self.pushButton_chose_file = QtGui.QPushButton(DialogImagesComparision)
        self.pushButton_chose_file.setObjectName(_fromUtf8("pushButton_chose_file"))
        self.gridLayout.addWidget(self.pushButton_chose_file, 1, 0, 1, 1)
        self.pushButton_chose_dir = QtGui.QPushButton(DialogImagesComparision)
        self.pushButton_chose_dir.setObjectName(_fromUtf8("pushButton_chose_dir"))
        self.gridLayout.addWidget(self.pushButton_chose_dir, 2, 0, 1, 1)
        self.pushButton_run = QtGui.QPushButton(DialogImagesComparision)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/7_rightArrows.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_run.setIcon(icon)
        self.pushButton_run.setObjectName(_fromUtf8("pushButton_run"))
        self.gridLayout.addWidget(self.pushButton_run, 4, 0, 1, 1)
        self.line = QtGui.QFrame(DialogImagesComparision)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 5, 0, 1, 1)
        self.line_2 = QtGui.QFrame(DialogImagesComparision)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 6, 0, 1, 1)

        self.retranslateUi(DialogImagesComparision)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DialogImagesComparision.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DialogImagesComparision.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogImagesComparision)

    def retranslateUi(self, DialogImagesComparision):
        DialogImagesComparision.setWindowTitle(QtGui.QApplication.translate("DialogImagesComparision", "ChartMaker", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_chose_file.setText(QtGui.QApplication.translate("DialogImagesComparision", "Scegli un file", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_chose_dir.setText(QtGui.QApplication.translate("DialogImagesComparision", "Scegli la directory", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_run.setToolTip(QtGui.QApplication.translate("DialogImagesComparision", "Last rec", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_run.setText(QtGui.QApplication.translate("DialogImagesComparision", "Run", None, QtGui.QApplication.UnicodeUTF8))

from mplwidget import Mplwidget
