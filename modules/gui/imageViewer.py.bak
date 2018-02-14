import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui
from PyQt4 import QtCore, QtGui
from imageViewer_ui import Ui_DialogViewer

class ImageViewer(QDialog, Ui_DialogViewer):
	def __init__(self, parent=None, origPixmap=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)

	
	def show_image(self, path, flags=Qt.KeepAspectRatioByExpanding):
		pic = QPixmap(path)
		grview = ImageViewClass(origPixmap=pic)
		scene = QGraphicsScene()
		scene.addPixmap(pic)
		grview.setScene(scene)
		self.gridLayout_2.addWidget(grview)
		

class ImageViewClass(QGraphicsView):
	def __init__(self, parent=None, origPixmap=None):
		"""
		QGraphicsView that will show an image scaled to the current widget size
		using events
		"""
		super(ImageViewClass, self).__init__(parent)
		self.origPixmap = origPixmap
		QMetaObject.connectSlotsByName(self)

	def resizeEvent(self, event):
		"""
		Handle the resize event.
		"""
		size = event.size()
		item =  self.items()[0]

		# using current pixmap after n-resizes would get really blurry image
		pixmap = item.pixmap()
		pixmap = self.origPixmap

		pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.centerOn(0,0)
		item.setPixmap(pixmap)

"""
app = QApplication(sys.argv)
listdir = os.listdir('/Users/pyarchinit/Desktop')
lista = []
for i in listdir:
	lista.append('/Users/pyarchinit/Desktop/'+i)
pic = QPixmap('/Users/pyarchinit/Desktop/IMG_4919.JPG')
grview = ImageViewClass(origPixmap=pic)

scene = QGraphicsScene()
scene.addPixmap(pic)

grview.setScene(scene)
grview.show()

sys.exit(app.exec_())
"""