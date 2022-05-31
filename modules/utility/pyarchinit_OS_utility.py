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
import sys
import shutil
import subprocess


class Pyarchinit_OS_Utility(object):
    def create_dir(self, d):
        dirname = d

        try:
            os.makedirs(dirname)
            return 1
        except OSError:
            if os.path.exists(dirname):
                # We are nearly safe
                return 0  # la cartella esiste
            else:
                # There was an error on creation, so make sure we know about it
                raise

    def copy_file_img(self, f, d):
        file_path = os.path.normpath(f)
        destination = os.path.normpath(d)
        shutil.copy(file_path, destination)
        return 0
    def copy_file(self, f, d):
        file_path = os.path.normpath(f)
        destination = os.path.normpath(d)
        if os.access(destination, 0):
            return 0  # la cartella esiste
        else:
            try:
                shutil.copy(file_path, destination)
                return 1
            except OSError:
                if os.path.exists(destination):
                    return 0
                else:
                    raise

    @staticmethod
    def checkGraphvizInstallation():
        try:
            subprocess.call(['dot', '-V'])
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def checkPostgresInstallation():
        try:
            subprocess.call(['pg_dump','-V'])
            return True
        except Exception as e:
            return False
    
    
    @staticmethod
    def isWindows():
        return os.name == 'nt'

    @staticmethod
    def isMac():
        return sys.platform == 'darwin'
