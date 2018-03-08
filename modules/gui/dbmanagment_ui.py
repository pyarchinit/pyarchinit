# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dbmanagment_ui.ui'
#
# Created: Mon Jul 22 13:58:46 2013
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui


class Ui_DBmanagment(object):
    def setupUi(self, DBmanagment):
        DBmanagment.setObjectName("DBmanagment")
        DBmanagment.resize(666, 285)
        self.backup = QtGui.QPushButton(DBmanagment)
        self.backup.setGeometry(QtCore.QRect(350, 70, 131, 31))
        self.backup.setObjectName("backup")
        self.label = QtGui.QLabel(DBmanagment)
        self.label.setGeometry(QtCore.QRect(170, -10, 291, 51))
        self.label.setObjectName("label")
        self.restore = QtGui.QPushButton(DBmanagment)
        self.restore.setGeometry(QtCore.QRect(440, 230, 93, 41))
        self.restore.setObjectName("restore")
        self.calendarWidget = QtGui.QCalendarWidget(DBmanagment)
        self.calendarWidget.setGeometry(QtCore.QRect(0, 38, 321, 181))
        self.calendarWidget.setMinimumSize(QtCore.QSize(191, 181))
        self.calendarWidget.setStyleSheet("font: 10pt \"Andale Mono\";")
        self.calendarWidget.setObjectName("calendarWidget")
        self.upload = QtGui.QPushButton(DBmanagment)
        self.upload.setGeometry(QtCore.QRect(40, 240, 221, 31))
        self.upload.setObjectName("upload")
        self.backup_total = QtGui.QPushButton(DBmanagment)
        self.backup_total.setGeometry(QtCore.QRect(420, 140, 131, 31))
        self.backup_total.setObjectName("backup_total")
        self.label_2 = QtGui.QLabel(DBmanagment)
        self.label_2.setGeometry(QtCore.QRect(420, 20, 161, 51))
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(DBmanagment)
        self.label_3.setGeometry(QtCore.QRect(350, 30, 251, 41))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtGui.QLabel(DBmanagment)
        self.label_4.setGeometry(QtCore.QRect(330, 110, 331, 20))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtGui.QLabel(DBmanagment)
        self.label_5.setGeometry(QtCore.QRect(380, 200, 261, 17))
        self.label_5.setObjectName("label_5")
        self.backupsqlite = QtGui.QPushButton(DBmanagment)
        self.backupsqlite.setGeometry(QtCore.QRect(500, 70, 121, 31))
        self.backupsqlite.setObjectName("backupsqlite")

        self.retranslateUi(DBmanagment)
        QtCore.QMetaObject.connectSlotsByName(DBmanagment)

    def retranslateUi(self, DBmanagment):
        DBmanagment.setWindowTitle(QtGui.QApplication.translate("DBmanagment", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.backup.setText(QtGui.QApplication.translate("DBmanagment", "Backup postgres", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DBmanagment", "             BackUP e Restore DB Pyarchinit", None, QtGui.QApplication.UnicodeUTF8))
        self.restore.setText(QtGui.QApplication.translate("DBmanagment", "Ripristina", None, QtGui.QApplication.UnicodeUTF8))
        self.upload.setText(QtGui.QApplication.translate("DBmanagment", "Scegli il file da ripristinare", None, QtGui.QApplication.UnicodeUTF8))
        self.backup_total.setText(QtGui.QApplication.translate("DBmanagment", "Backup totale", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("DBmanagment", "Backup db pyarchinit (per win e linux)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("DBmanagment", "Backup totale di tutti i db postgres (solo per linux)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("DBmanagment", "Scegli un file del backup e ripristinalo", None, QtGui.QApplication.UnicodeUTF8))
        self.backupsqlite.setText(QtGui.QApplication.translate("DBmanagment", "Backup sqlite", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DBmanagment = QtGui.QDialog()
    ui = Ui_DBmanagment()
    ui.setupUi(DBmanagment)
    DBmanagment.show()
    sys.exit(app.exec_())

