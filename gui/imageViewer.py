#! /usr/bin/env python

# -*- coding: utf-8 -*-

"""

/***************************************************************************

        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset

                             stored in Postgres

                             -------------------

    begin                : 2007-12-01

    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>

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
import shutil
import tempfile

from qgis.PyQt.QtGui import QPixmap

from qgis.PyQt.QtCore import Qt

from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QGraphicsView, QGraphicsScene, QPushButton, QFileDialog

from qgis.PyQt.uic import loadUiType

from qgis.PyQt import QtWidgets

# Import remote image loader for handling unibo://, cloudinary://, http:// paths
try:
    from ..modules.utility.remote_image_loader import (
        RemoteImageLoader,
        load_pixmap as remote_load_pixmap,
        is_remote_url,
        is_unibo_path,
        load_unibo_credentials_from_qgis
    )
    REMOTE_LOADER_AVAILABLE = True
except ImportError:
    REMOTE_LOADER_AVAILABLE = False
    print("[ImageViewer] WARNING: remote_image_loader not available")

IMAGE_VIEWER, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'Image_Viewer.ui'))





class ImageViewer(QDialog, IMAGE_VIEWER):

    def __init__(self, parent=None, origPixmap=None):

        QDialog.__init__(self, parent)

        self.setupUi(self)

        # Store current image path for export
        self.current_image_path = None

        # Add export button to the button box
        self.exportButton = QPushButton("Esporta")
        self.exportButton.clicked.connect(self.export_image)
        self.buttonBox.addButton(self.exportButton, self.buttonBox.ActionRole)



    



    def show_image(self, path, flags=Qt.AspectRatioMode.KeepAspectRatioByExpanding):
        """
            Displays an image at the specified path in a QGraphicsView widget.
            Supports local paths, HTTP/HTTPS URLs, cloudinary://, and unibo:// paths.

            Args:
                path (str): The path to the image file (local or remote).
                flags (Union[Qt.AspectRatioMode, Qt.Transformations], optional): The aspect ratio mode to use when displaying the image. Defaults to Qt.AspectRatioMode.KeepAspectRatioByExpanding.

            Returns:
                None
        """

        # Store the path for export functionality
        self.current_image_path = path
        self._temp_file = None  # For cleanup of temp files

        pic = QPixmap()

        # Check if we need to use remote loader
        if REMOTE_LOADER_AVAILABLE and path:
            # Check if it's a remote path (unibo://, cloudinary://, http://, https://)
            if is_remote_url(path) or is_unibo_path(path):

                # Ensure credentials are loaded
                if is_unibo_path(path):
                    load_unibo_credentials_from_qgis()

                # Load using remote loader
                pic = remote_load_pixmap(path)
            else:
                # Local path
                if os.path.exists(path):
                    pic.load(path)
        else:
            # Fallback to direct QPixmap loading
            if path and os.path.exists(path):
                pic.load(path)

        grview = ImageViewClass(origPixmap=pic)

        scene = QGraphicsScene()

        scene.addPixmap(pic)

        grview.setScene(scene)

        self.gridLayout_2.addWidget(grview)

    def export_image(self):
        """Export the current image to a user-chosen location.
        Works with both local and remote (unibo://, http://, cloudinary://) paths.
        """
        if not self.current_image_path:
            QMessageBox.warning(self, "Attenzione", "Nessuna immagine da esportare.")
            return

        # Check if it's a remote path
        is_remote = False
        if REMOTE_LOADER_AVAILABLE:
            is_remote = is_remote_url(self.current_image_path) or is_unibo_path(self.current_image_path)

        # For local paths, check if file exists
        if not is_remote and not os.path.exists(self.current_image_path):
            QMessageBox.warning(self, "Attenzione", f"File non trovato:\n{self.current_image_path}")
            return

        # Get the original filename
        if '/' in self.current_image_path:
            filename = self.current_image_path.split('/')[-1]
        else:
            filename = os.path.basename(self.current_image_path)

        # Ask user for save location
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta immagine",
            os.path.join(os.path.expanduser("~"), "Desktop", filename),
            "Tutti i file (*.*)"
        )

        if save_path:
            try:
                if is_remote:
                    # For remote images, save from the loaded pixmap
                    pixmap = remote_load_pixmap(self.current_image_path)
                    if not pixmap.isNull():
                        # Determine format from extension
                        ext = os.path.splitext(save_path)[1].lower()
                        fmt = 'PNG' if ext == '.png' else 'JPEG' if ext in ('.jpg', '.jpeg') else None
                        if pixmap.save(save_path, fmt):
                            QMessageBox.information(self, "Successo", f"Immagine esportata:\n{save_path}")
                        else:
                            QMessageBox.critical(self, "Errore", "Errore durante il salvataggio dell'immagine")
                    else:
                        QMessageBox.critical(self, "Errore", "Impossibile caricare l'immagine remota")
                else:
                    # Local file - copy directly
                    shutil.copy2(self.current_image_path, save_path)
                    QMessageBox.information(self, "Successo", f"Immagine esportata:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione:\n{str(e)}")

        

    





class ImageViewClass(QGraphicsView):

    zoom_in = 1.25

    def __init__(self, parent=None, origPixmap=None):

        """

        QGraphicsView that will show an image scaled to the current widget size

        using events

        """

        super(ImageViewClass, self).__init__(parent)

        self.origPixmap = origPixmap

        

    # def resizeEvent(self, event):

        # """

        # Handle the resize event.

        # """

        # size = event.size()

        # item = list(self.items())[0]



        # # using current pixmap after n-resizes would get really blurry image

        # pixmap = item.pixmap()

        # pixmap = self.origPixmap

        

        # pixmap = pixmap.scaled(size,Qt.KeepAspectRatio)
        

        # self.centerOn(0,0)

        # item.setPixmap(pixmap)

        # centerPos = (size.width()-pixmap.width())/2
        # item.setPos(centerPos,0)



    

    def wheelEvent(self,event):        

        delta = event.angleDelta()

        if delta.y() > 0:

            scale = self.zoom_in

        else:

            scale = 1 / self.zoom_in

        # Set Anchors

        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)


        cur_pos = self.mapToScene(event.pos())

        self.scale(scale, scale)

        new_pos = self.mapToScene(event.pos())

        delta_zoomed = new_pos - cur_pos

        self.translate(delta_zoomed.x(), delta_zoomed.y())



        event.accept()

        return

        return super(ImageViewClass, self).wheelEvent(event)

         
