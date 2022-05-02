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

from __future__ import print_function
import shutil
from PIL import Image
from builtins import object
from builtins import str
from qgis.PyQt.QtWidgets import QMessageBox
from ..db.pyarchinit_conn_strings import *


class Media_utility(object):
    """
    >> import Image                      # importo il modulo
>>> image_path = r"C:\test\snake.png" # assegno l' immagine alla variabile tramite raw string (r"path\files")
>>> image = Image.open(image_path)    # apro l'immagine
>>> width, height = (150, 110)        # ridimensiono l'immagine l' originale era 300x350px
>>> size = (width, height)            # assegno grandezza e altezza
>>> new_image_thumbnail = r"C:\test\snake_small.png" # che sia pitone grande o  pitone piccolo l' importante che pitone è
>>> image.thumbnail(size, Image.ANTIALIAS) # creo la thumbnail vera e propria con antialias ma potevamo anche bicubic bilinear ecc
>>> image.save(new_image_thumbnail)        # salvo la nuova immagine "thumbnail"
"""

    def resample_images(self, mid, ip, i, o, ts):
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        size = 150, 150
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
        self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)
        im = Image.open(infile)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(outfile, dpi=(100, 100))


if __name__ == '__main__':
    m = Media_utility()
    conn = Connection()
    thumb_path = conn.thumb_path()
    thumb_path_str = thumb_path['thumb_path']
    print(thumb_path_str)
    

class Media_utility_resize(object):


    def resample_images(self, mid, ip, i, o, ts):
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        size = 2008, 1417
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
        self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)
        im = Image.open(infile)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(outfile, dpi=(300, 300))


if __name__ == '__main__':
    m = Media_utility_resize()
    conn = Connection()
    thumb_resize = conn.thumb_resize()
    thumb_resize_str = thumb_resize['thumb_resize']
    print(thumb_resize_str)
    
class Video_utility(object):


    def resample_images(self, mid, ip, i, o, ts):
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        #size = 2008, 1417
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
        self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)
        shutil.move(infile, outfile)
            

if __name__ == '__main__':
    m = Video_utility()
    conn = Connection()
    thumb_path = conn.thumb_path()
    thumb_path_str = thumb_path['thumb_path']
    print(thumb_path_str)   
    
class Video_utility_resize(object):


    def resample_images(self, mid, ip, i, o, ts):
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        #size = 2008, 1417
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
        self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)
        shutil.copy(infile, outfile)
            

if __name__ == '__main__':
    m = Video_utility_resize()
    conn = Connection()
    thumb_resize = conn.thumb_resize()
    thumb_resize_str = thumb_resize['thumb_resize']
    print(thumb_resize_str)   
