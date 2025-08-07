#!/usr/bin/env python3
"""
/****************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
    -------------------
    begin                : 2018-04-22
    copyright            : (C) 2008 by Salvatore Larosa; Enzo Cocca <enzo.ccc@gmail.com>
    email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *                                                                        *
 ***************************************************************************/
"""

import subprocess
import sys
import platform
import os
#from .. modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

packages = sys.argv[1].split(',') if len(sys.argv) >= 2 else []
l = sys.argv[1].split(',') if len(sys.argv) >= 2 else []
# Adding the dependencies python modules in
# package list in order to install via pip module


if not packages:
    # Read dependencies from requirements.txt
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        # Fallback to minimal set if requirements.txt not found
        packages = [
            'SQLAlchemy==1.4.27',
            'SQLAlchemy-Utils',
            'geoalchemy2==0.9.4',
            'reportlab',
            'matplotlib',
            'graphviz',
            'xlsxwriter',
            'pandas',
            'opencv-python',
            'qrcode==8.2']
if not l:    
    l=[
        'totalopenstation'
        
    ]

   
python_path = sys.exec_prefix
python_version = sys.version[:3]

if platform.system()=='Windows':
    cmd = 'python'
elif platform.system()=='Darwin':
    cmd = '{}/bin/python{}'.format(python_path, python_version)
else:
    cmd = '{}/bin/python{}'.format(python_path, python_version)


for p in packages:
    
    subprocess.call(['python','-m','pip', 'install', p, '--user' ], shell=True)
for t in l:    
    if platform.system() == 'Windows':
        cmd = '{}\python'.format(python_path)
        try:
            subprocess.call(['python','-m','pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=True)
        except KeyError as e:
            print(e)
        else:
            subprocess.call(
                [cmd, '-m', 'pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=True)


    else:
        cmd = '{}/bin/python{}'.format(python_path, python_version)
        try:
            subprocess.call([cmd,'-m','pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=True)
        except KeyError as e:
            print(e)
        else:
            subprocess.call(
                [cmd, '-m', 'pip', 'install', 'https://github.com/enzococca/totalopenstation/zipball/main'], shell=False)
