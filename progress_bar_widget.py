#!/usr/bin/python

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

##			  self.button = QtGui.QPushButton('Start', widget)
##			  self.connect(self.button, QtCore.SIGNAL('clicked()'), self.StartProgress)
##
##			  self.horiz = QtGui.QPushButton('Vertical', widget)
##			  self.horiz.setCheckable(True)
##			  self.connect(self.horiz, QtCore.SIGNAL('clicked()'), self.changeOrientation)
##
##			  self.direction = QtGui.QPushButton('Reverse', widget)
##			  self.direction.setCheckable(True)
##			  self.connect(self.direction, QtCore.SIGNAL('clicked()'), self.Reverse)

			  grid.addWidget(self.progressBar, 0, 0, 1, 3)
			  grid.addWidget(self.button, 1, 0)
			  grid.addWidget(self.horiz, 1, 1)
			  grid.addWidget(self.direction, 1, 2)

			  self.timer = QtCore.QBasicTimer()
			  self.step = 0

			  widget.setLayout(grid)
			  self.setCentralWidget(widget)

##	  def Reverse(self):
##			  if self.direction.isChecked():
##					  self.progressBar.setInvertedAppearance(True)
##			  else:
##					  self.progressBar.setInvertedAppearance(False)
##
##	  def changeOrientation(self):
##			  if self.horiz.isChecked():
##					  self.progressBar.setOrientation(QtCore.Qt.Vertical)
##			  else:
##					  self.progressBar.setOrientation(QtCore.Qt.Horizontal)

	  def timerEvent(self, event):
			  if self.step >= 100:
					  self.timer.stop()
					  return
			  self.step = self.step+1
			  self.progressBar.setValue(self.step)

##	  def StartProgress(self):
##			  if self.timer.isActive():
##					  self.timer.stop()
##					  self.button.setText('Start')
##			  else:
##					  self.timer.start(100, self)
##					  self.button.setText('Stop')

app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())