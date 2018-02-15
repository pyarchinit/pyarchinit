#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib import *
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


##import matplotlib.pyplot.figure as Figure
class MplCanvas(FigureCanvas):
	def __init__(self):
		
		self.fig = plt.figure()
		self.ax = self.fig.add_subplot(111)
		FigureCanvas.__init__(self, self.fig)
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

class MplwidgetMatrix(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.canvas = MplCanvas()
		#self.canvas = FigureCanvas(self.fig)
		
		self.navBar = NavigationToolbar(self.canvas, self)
		self.vbl = QVBoxLayout()
		self.vbl.addWidget(self.canvas)
		self.vbl.addWidget(self.navBar)
		self.setLayout(self.vbl)
