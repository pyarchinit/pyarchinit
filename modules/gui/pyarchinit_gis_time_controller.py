# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyarchinit_gis_time_controller.ui'
#
# Created: Mon Aug 11 17:04:24 2014
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import resources_rc


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DialogGisTimeController(object):
    def setupUi(self, DialogGisTimeController):
        DialogGisTimeController.setObjectName(_fromUtf8("DialogGisTimeController"))
        DialogGisTimeController.resize(500, 250)
        DialogGisTimeController.setMinimumSize(QtCore.QSize(400, 156))
        DialogGisTimeController.setMaximumSize(QtCore.QSize(500, 250))
        DialogGisTimeController.setSizeIncrement(QtCore.QSize(400, 156))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/iconTimeControll.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogGisTimeController.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(DialogGisTimeController)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(DialogGisTimeController)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.textEdit = QtGui.QTextEdit(self.tab)
        self.textEdit.setEnabled(False)
        self.textEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout_2.addWidget(self.textEdit, 0, 0, 1, 5)
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 5)
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.spinBox_cron_iniz = QtGui.QSpinBox(self.tab)
        self.spinBox_cron_iniz.setMinimum(-4000000)
        self.spinBox_cron_iniz.setMaximum(2010)
        self.spinBox_cron_iniz.setSingleStep(250)
        self.spinBox_cron_iniz.setObjectName(_fromUtf8("spinBox_cron_iniz"))
        self.gridLayout_2.addWidget(self.spinBox_cron_iniz, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 2, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self.tab)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 3, 1, 1)
        self.spinBox_cron_fin = QtGui.QSpinBox(self.tab)
        self.spinBox_cron_fin.setMinimum(-4000000)
        self.spinBox_cron_fin.setMaximum(2010)
        self.spinBox_cron_fin.setSingleStep(250)
        self.spinBox_cron_fin.setObjectName(_fromUtf8("spinBox_cron_fin"))
        self.gridLayout_2.addWidget(self.spinBox_cron_fin, 2, 4, 1, 1)
        self.pushButton_visualize = QtGui.QPushButton(self.tab)
        self.pushButton_visualize.setMinimumSize(QtCore.QSize(100, 25))
        self.pushButton_visualize.setObjectName(_fromUtf8("pushButton_visualize"))
        self.gridLayout_2.addWidget(self.pushButton_visualize, 3, 0, 1, 5)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.tab_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.dial_relative_cronology = QtGui.QDial(self.tab_2)
        self.dial_relative_cronology.setMaximum(30)
        self.dial_relative_cronology.setNotchesVisible(True)
        self.dial_relative_cronology.setObjectName(_fromUtf8("dial_relative_cronology"))
        self.horizontalLayout.addWidget(self.dial_relative_cronology)
        self.spinBox_relative_cronology = QtGui.QSpinBox(self.tab_2)
        self.spinBox_relative_cronology.setMaximumSize(QtCore.QSize(100, 16777215))
        self.spinBox_relative_cronology.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_relative_cronology.setAccelerated(False)
        self.spinBox_relative_cronology.setMinimum(0)
        self.spinBox_relative_cronology.setMaximum(1000)
        self.spinBox_relative_cronology.setProperty(_fromUtf8("value"), 0)
        self.spinBox_relative_cronology.setObjectName(_fromUtf8("spinBox_relative_cronology"))
        self.horizontalLayout.addWidget(self.spinBox_relative_cronology)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(DialogGisTimeController)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(DialogGisTimeController)

    def retranslateUi(self, DialogGisTimeController):
        DialogGisTimeController.setWindowTitle(QtGui.QApplication.translate("DialogGisTimeController", "pyArchInit Gestione Scavi - Time Controller", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit.setHtml(QtGui.QApplication.translate("DialogGisTimeController", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:600;\">Per funzionare il sistema di ricerca per cronologie assolute richiede la creazione dei periodi di scavo nella scheda Periodizzazione. La cronologia assoluta qui utilizzata viene riferita ai termini &quot;avanti Cristo&quot; e &quot;dopo Cristo&quot;. Per settare valori avanti Cristo utilizzare il segno &quot;-&quot; davanti all\'anno (ex: 268 a.C. = -268). Per settare valori dopo Cristo utilizzare non e\' necessario utilizzare alcun segno (1400 d.C. = 1440).</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:600;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("DialogGisTimeController", "Visualizza l\'intervallo di tempo compreso tra l\'anno:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DialogGisTimeController", "Cronologia iniziale", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("DialogGisTimeController", "e l\'anno", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("DialogGisTimeController", "Cronologia finale", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_visualize.setToolTip(QtGui.QApplication.translate("DialogGisTimeController", "Prev rec", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_visualize.setText(QtGui.QApplication.translate("DialogGisTimeController", "Visualizza", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("DialogGisTimeController", "Absolute cronology system", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("DialogGisTimeController", "Relative cronology system", None, QtGui.QApplication.UnicodeUTF8))

