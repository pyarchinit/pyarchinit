# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/pyarchinit/.qgis/python/plugins/pyarchinit/modules/gui/Ui_UpdValues.ui'
#
# Created: Wed Mar 24 22:35:48 2010
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DialogSostituisciValori(object):
    def setupUi(self, DialogSostituisciValori):
        DialogSostituisciValori.setObjectName("DialogSostituisciValori")
        DialogSostituisciValori.resize(488, 194)
        self.gridLayout = QtGui.QGridLayout(DialogSostituisciValori)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.nome_campoLabel = QtGui.QLabel(DialogSostituisciValori)
        self.nome_campoLabel.setObjectName("nome_campoLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.nome_campoLabel)
        self.nome_campoLineEdit = QtGui.QLineEdit(DialogSostituisciValori)
        self.nome_campoLineEdit.setObjectName("nome_campoLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.nome_campoLineEdit)
        self.gridLayout.addLayout(self.formLayout, 2, 0, 1, 1)
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.sostituisci_conLabel = QtGui.QLabel(DialogSostituisciValori)
        self.sostituisci_conLabel.setObjectName("sostituisci_conLabel")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.sostituisci_conLabel)
        self.sostituisci_conLineEdit = QtGui.QLineEdit(DialogSostituisciValori)
        self.sostituisci_conLineEdit.setObjectName("sostituisci_conLineEdit")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.sostituisci_conLineEdit)
        self.gridLayout.addLayout(self.formLayout_2, 3, 0, 1, 1)
        self.pushButton = QtGui.QPushButton(DialogSostituisciValori)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 4, 0, 1, 1)
        self.formLayout_3 = QtGui.QFormLayout()
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout_3.setObjectName("formLayout_3")
        self.campoIDLabel = QtGui.QLabel(DialogSostituisciValori)
        self.campoIDLabel.setObjectName("campoIDLabel")
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.campoIDLabel)
        self.campoIDLineEdit = QtGui.QLineEdit(DialogSostituisciValori)
        self.campoIDLineEdit.setObjectName("campoIDLineEdit")
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.campoIDLineEdit)
        self.gridLayout.addLayout(self.formLayout_3, 1, 0, 1, 1)
        self.formLayout_4 = QtGui.QFormLayout()
        self.formLayout_4.setObjectName("formLayout_4")
        self.nometabellaLabel = QtGui.QLabel(DialogSostituisciValori)
        self.nometabellaLabel.setObjectName("nometabellaLabel")
        self.formLayout_4.setWidget(0, QtGui.QFormLayout.LabelRole, self.nometabellaLabel)
        self.nome_tabellaLineEdit = QtGui.QLineEdit(DialogSostituisciValori)
        self.nome_tabellaLineEdit.setObjectName("nome_tabellaLineEdit")
        self.formLayout_4.setWidget(0, QtGui.QFormLayout.FieldRole, self.nome_tabellaLineEdit)
        self.gridLayout.addLayout(self.formLayout_4, 0, 0, 1, 1)

        self.retranslateUi(DialogSostituisciValori)
        QtCore.QMetaObject.connectSlotsByName(DialogSostituisciValori)

    def retranslateUi(self, DialogSostituisciValori):
        DialogSostituisciValori.setWindowTitle(QtGui.QApplication.translate("DialogSostituisciValori", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.nome_campoLabel.setText(QtGui.QApplication.translate("DialogSostituisciValori", "Sostituisci i valori nel campo", None, QtGui.QApplication.UnicodeUTF8))
        self.nome_campoLineEdit.setText(QtGui.QApplication.translate("DialogSostituisciValori", "nome del campo", None, QtGui.QApplication.UnicodeUTF8))
        self.sostituisci_conLabel.setText(QtGui.QApplication.translate("DialogSostituisciValori", "con il valore", None, QtGui.QApplication.UnicodeUTF8))
        self.sostituisci_conLineEdit.setText(QtGui.QApplication.translate("DialogSostituisciValori", "inserisci un valore", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("DialogSostituisciValori", "Sostituisci", None, QtGui.QApplication.UnicodeUTF8))
        self.campoIDLabel.setText(QtGui.QApplication.translate("DialogSostituisciValori", "In base ai valori selezionati sul GIS nel campo", None, QtGui.QApplication.UnicodeUTF8))
        self.campoIDLineEdit.setText(QtGui.QApplication.translate("DialogSostituisciValori", "nome del campo", None, QtGui.QApplication.UnicodeUTF8))
        self.nometabellaLabel.setText(QtGui.QApplication.translate("DialogSostituisciValori", "Sostituisci i valori nella tabella", None, QtGui.QApplication.UnicodeUTF8))
        self.nome_tabellaLineEdit.setText(QtGui.QApplication.translate("DialogSostituisciValori", "nome del layer", None, QtGui.QApplication.UnicodeUTF8))

