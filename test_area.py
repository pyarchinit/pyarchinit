#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2010 by Luca Mandolesi
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


class Test_area:
    HOME = os.environ['PYARCHINIT_HOME']

    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "pyarchinit_Test_folder")

    def __init__(self, data):
        self.data = data

    def run_test(self):
        pass

    def test_comment(selfself):
        ###this is a comment to test commit###
        pass
