#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QGraphicsView, QGraphicsScene
from qgis.PyQt.uic import loadUiType

IMAGE_VIEWER, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'Image_Viewer.ui'))


class ImageViewer(QDialog, IMAGE_VIEWER):
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

    def resizeEvent(self, event):
        """
        Handle the resize event.
        """
        size = event.size()
        item = list(self.items())[0]

        # using current pixmap after n-resizes would get really blurry image
        pixmap = item.pixmap()
        pixmap = self.origPixmap

        pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.centerOn(0, 0)
        item.setPixmap(pixmap)
