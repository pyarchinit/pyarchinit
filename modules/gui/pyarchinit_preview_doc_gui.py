# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyarchinit_preview_doc_gui.ui'
#
# Created: Wed Nov 12 14:57:13 2014
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_DialogPreviewDoc(object):
    def setupUi(self, DialogPreviewDoc):
        DialogPreviewDoc.setObjectName(_fromUtf8("DialogPreviewDoc"))
        DialogPreviewDoc.setWindowModality(QtCore.Qt.WindowModal)
        DialogPreviewDoc.resize(622, 521)
        DialogPreviewDoc.setMinimumSize(QtCore.QSize(540, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/finds.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogPreviewDoc.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(DialogPreviewDoc)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.widgetPreviewDoc = QtGui.QWidget(DialogPreviewDoc)
        self.widgetPreviewDoc.setObjectName(_fromUtf8("widgetPreviewDoc"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widgetPreviewDoc)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout.addWidget(self.widgetPreviewDoc, 0, 0, 1, 1)

        self.retranslateUi(DialogPreviewDoc)
        QtCore.QMetaObject.connectSlotsByName(DialogPreviewDoc)

    def retranslateUi(self, DialogPreviewDoc):
        DialogPreviewDoc.setWindowTitle(
            QtGui.QApplication.translate("DialogPreviewDoc", "pyArchInit Gestione Scavi - Preview Documetazione", None,
                                         QtGui.QApplication.UnicodeUTF8))
