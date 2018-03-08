#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from PyQt4 import QtGui, QtCore


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(350, 250)
        self.setWindowTitle('ProgressBar')
        widget = QtGui.QWidget()

        grid = QtGui.QGridLayout(widget)
        self.progressBar = QtGui.QProgressBar(widget)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        grid.addWidget(self.progressBar, 0, 0, 1, 3)
        grid.addWidget(self.button, 1, 0)
        grid.addWidget(self.horiz, 1, 1)
        grid.addWidget(self.direction, 1, 2)

        self.timer = QtCore.QBasicTimer()
        self.step = 0

        widget.setLayout(grid)
        self.setCentralWidget(widget)

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            return
        self.step = self.step + 1
        self.progressBar.setValue(self.step)


app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())		