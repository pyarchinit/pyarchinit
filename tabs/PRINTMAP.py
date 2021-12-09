#! /usr/bin/env python
# -*- coding: utf 8 -*-
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
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import range
from builtins import str
import psycopg2
import sqlite3  as sq
from sqlite3 import Error
import os
import sys
import subprocess
import platform
import time
import pandas as pd
import numpy as np

from datetime import date

from distutils.dir_util import copy_tree
from random import randrange as rand
from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtXml import QDomDocument
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis, QgsSettings,QgsGeometry,QgsProject,QgsApplication
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from qgis.PyQt.QtSql import QSqlDatabase, QSqlTableModel
from ..gui.imageViewer import ImageViewer
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

from ..resources.resources_rc import *

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Print_map.ui'))
class pyarchinit_PRINTMAP(QDialog, MAIN_DIALOG_CLASS):
    
    HOME = os.environ['PYARCHINIT_HOME']
    
    BIN = '{}{}{}'.format(HOME, os.sep, "bin")
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.mDockWidget.setHidden(True)
        self.plugin_dir = os.path.dirname(__file__)
        self.listWidget.itemClicked.connect(self.suggestLayoutName)
        self.btnAddMore.clicked.connect(self.addMoreTemplates)        
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.listMenu)
        self.customize_GUI()
        self.txtLayoutName.setEnabled(False)
        self.run()
        
        
    def customize_GUI(self):
        self.listWidget_2.itemDoubleClicked.connect(self.opentepmplatePreview)
    
    def loadTemplates(self):
        self.listWidget.clear()
        profile_dir = self.HOME
        templates_dir = os.path.join(profile_dir,'bin','profile','template')
          
        # Does the composer_templates folder exist? Otherwise create it.
        if os.path.isdir(templates_dir) == False:
            os.mkdir(templates_dir)
          
        # Search the templates folder and add files to templates list and sort it
        templates = [f.name for f in os.scandir(templates_dir) if f.is_file() ]
        templates.sort()
          
        # Get the project file name and if it exist the project title. Use for Title suggestion
        project_file_name = QFileInfo(QgsProject.instance().fileName()).baseName()
        project_title = QgsProject.instance().title()
        if project_title == '':
            project_title = project_file_name
        self.txtMapTitle.setText(project_title)
          
        # Add all the templates from the list to the listWidget (only add files with *.qpt extension)
        for template in templates:
            filename, extension = os.path.splitext(template) 
            if extension == '.qpt':
                self.listWidget.addItem(filename)
            
                
   
    
    def listMenu(self, position):
        self.txtLayoutName.setEnabled(False)
        indexes = self.listWidget.selectedIndexes()
        template_name = self.listWidget.selectedItems()[0].text()
        template_path = os.path.join(self.HOME,'bin','profile','template',template_name + '.qpt')
        
        if indexes:
            
            
            menu = QMenu()
            menu.addAction('Cancella Template')
            menu.addAction('Mostra Preview')
            # menu.addAction(self.tr('Future context menu option'))
         
            menu_choice = menu.exec_(self.listWidget.viewport().mapToGlobal(position))

            try:
                
                if menu_choice.text() == 'Cancella Template':
                    template_name = self.listWidget.selectedItems()[0].text()
                    template_path = os.path.join(self.HOME,'bin','profile','template',template_name + '.qpt')
                    
                    
                    if os.path.exists(str(template_path)):
                        os.remove(template_path)
                        self.loadTemplates
                        self.txtLayoutName.setText('{} - Cancellato'.format(template_name))
            
                    else:
                        self.txtLayoutName.setText('{} - non è stato cancellato'.format(template_name))
                elif menu_choice.text() == 'Mostra Preview':
                    self.listWidget_2.clear()
                    template_name = self.listWidget.selectedItems()[0].text()
                    template_path = os.path.join(self.HOME,'bin','profile','template',template_name + '.jpeg')
                    
                    item = QListWidgetItem(str(template_name))
                    item.setData(Qt.UserRole, str(template_name))
                    icon = QIcon(template_path)
                    item.setIcon(icon)
                    self.listWidget_2.addItem(item)
                    
            except:# Exception as e:
                pass#QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
          
    def opentepmplatePreview(self):
    
        self.listWidget_2.clear()
        template_name = self.listWidget.selectedItems()[0].text()
        template_path = os.path.join(self.HOME,'bin','profile','template',template_name + '.jpeg')
        dlg = ImageViewer()
        dlg.show_image(template_path)  
        dlg.exec_()
    
    
    # Does a layout already exist
    
    
    def addMoreTemplates(self):
          are_you_sure = 'Questo aggiungerà modelli e risorse come file SVG e funzioni di script.\n\n'
          are_you_sure += 'Vuoi sovrascrivere i file esistenti con lo stesso nome?'
          addMoreBox = QMessageBox()
          addMoreBox.setIcon(QMessageBox.Question)
          addMoreBox.setWindowTitle('Aggiungi Template')
          addMoreBox.setText(are_you_sure)
          more_information = 'Se schiacci \'No\', i file non saranno sovrascritti, ma un nuovo fila verrà aggiunto.\n\n'
          more_information += 'Se schiacci \'Sì\' i file che hai modificato manualmente saranno sovrascritti con quelli nuovi.\n'
          more_information += 'Se schiacci \'Annulla\' Non si apporterà nessuna modifica!\n\n'
          more_information += 'Alcune funzioni potrebbero richiedere il riavvio di QGIS come per le mappe militari prima di funzionare correttamente.'
          addMoreBox.setDetailedText(more_information)
          addMoreBox.setStandardButtons(QMessageBox.Cancel|QMessageBox.No|QMessageBox.Yes)
          
          button_pressed = addMoreBox.exec_()
          
          # Paths to source files and qgis profile directory
          source_profile = os.path.join(self.HOME,'bin', 'profile')
          profile_home = QgsApplication.qgisSettingsDirPath()

          # The acutal "copy" with or without overwrite (update)
          if button_pressed == QMessageBox.Yes:
              copy_tree(source_profile, profile_home)
              self.loadTemplates()
          elif button_pressed == QMessageBox.No:
              copy_tree(source_profile, profile_home, update=1)
              self.loadTemplates()
    
    def suggestLayoutName(self):
          self.txtLayoutName.setEnabled(True)
          layout_name_string = self.listWidget.currentItem().text()
          if self.txtMapTitle != '':
              layout_name_string += ' ' + self.txtMapTitle.text()
          self.txtLayoutName.setText(layout_name_string)
    
    
    
    def layout_exists(self, layout_name):
          lm = QgsProject.instance().layoutManager()
          layouts = []
          for l in lm.layouts():
              layouts.append(l.name())
          if layout_name in layouts:
             return sum(layout_name in s for s in layouts)
          else:
             return 0  
    # Add templates and resources from plugin to user profile (triggers on dialog button clicked signal)
    # Somehow a lot of QMessageBox's are generated.
    
    def layoutLoader(self, template_source, layout_name, title_text):
        """ Generate the layout """
        from qgis.core import (QgsProject,
                       QgsPrintLayout,
                       QgsReadWriteContext)
        from qgis.utils import iface
        from PyQt5.QtXml import QDomDocument

        #template_source = '/home/user/Document/Template.qpt'
        #layout_name = 'NewLayout'
        #title_text = 'New Title'
        
        # Create objects lm = layout manager, l = print layout
        lm = QgsProject.instance().layoutManager()
        l = QgsPrintLayout(QgsProject.instance())
        l.initializeDefaults()
        
        # Load template file and load it into the layout (l)
        template_file = open(template_source, 'r+', encoding='utf-8')
        template_content = template_file.read()
        template_file.close()
        document = QDomDocument()
        document.setContent(template_content)
        context = QgsReadWriteContext()
        l.loadFromTemplate(document, context)
        
        # Give the layout a name (must be unique)
        l.setName(layout_name)
        
        # Get current canvas extent and apply that to all maps (items) in layout
        # Replace any text "{{title}}" in any layout label with the dialog Title text
        canvas = self.iface.mapCanvas()
        for item in l.items():
            if item.type()==65639: # Map
                item.zoomToExtent(canvas.extent())
            if item.type()==65641: # Label
                item.setText(item.text().replace('{{title}}',title_text))
        
        # Add layout to layout manager
        l.refresh()
        lm.addLayout(l)
        
        # Open and show the layout in designer
        try:
           self.iface.openLayoutDesigner(l)
        except:
           oopsBox = QMessageBox()
           oopsBox.setIcon(QMessageBox.Warning)
           oopsBox.setText('Ooops. Qualcosa è andato storto. Il tentativo di aprire il layout generato ({}) ha restituito errori.'.format(l.name()))
           oopsBox.setWindowTitle('Crea la tua mappa')
           oopsBox.exec_()
    
    def run(self):
        """Run method that performs all the real work"""
        # This loads the dialog with templates (again) TODO check when it's best to do this
        self.loadTemplates()
        
        

        # See if OK was pressed TODO: probably need something to happen when pressing "cancel" too.
        #if result:
        # Get values from dialog list and text fields
        #show the dialog
        #self.show()
        # Run the dialog event loop
        result = self.exec_()
        
        # See if OK was pressed TODO: probably need something to happen when pressing "cancel" too.
        if result:
            try:
               template_name = self.listWidget.currentItem().text()
            except:
                template_name = ''
            layout_name = self.txtLayoutName.text()
            # Generate random layout name for blank names (REDUNDANT?)
            if layout_name == '':
               layout_name = 'Layout'
            
            # Add function to test the layout name so that it doesn't exist. If it does handle the exception
            
            map_title = self.txtMapTitle.text()
            profile_dir = self.HOME
            # create the template item selected full path (assuming extension is lower case)
            template_source = os.path.join(profile_dir,'bin','profile','template',template_name + '.qpt')
            
            # Call function to generate layout, renaming duplicate layout names
            layout_count = self.layout_exists(layout_name) # How many layouts with the same name exist already
            if layout_count >> 0:
               name = layout_name.split('_')
               if layout_count >> 1:
                  layout_name = '_'.join(name) + '_' + str(layout_count + 1)
               else:
                layout_name += '_2'
            try:
               if os.path.exists(template_source):
                  self.layoutLoader(template_source, layout_name, map_title) # CALLING MAIN LAYOUT LOADING PROCESS
               else:
                  infoBox = QMessageBox()
                  infoBox.setIcon(QMessageBox.Information)
                  infoBox.setText('Seleziona un template valido dalla lista.')
                  infoBox.setWindowTitle('Crea la tua mappa')
                  infoBox.exec_()
            except:
               oopsBox = QMessageBox()
               oopsBox.setIcon(QMessageBox.Warning)
               oopsBox.setText('Ooops. qualcosa è andato storto ({}). Ma non so cosa?'.format(layout_name))
               oopsBox.setWindowTitle('Crea la tua mappa')
               oopsBox.setDetailedText('Titolo della Mappa: {}\nNome del Template: {}\nNome del Layout: {}\nDorectory del profilo {}\nPath del Template: {}\nConteggio Layout: {}' % (map_title, template_name, layout_name, profile_dir, template_source, layout_count))
               oopsBox.exec_()
                   
            # Clean up
            self.txtLayoutName.clear()
            self.txtLayoutName.setEnabled(False)
            self.txtMapTitle.clear()
            self.txtMapTitle.setFocus()
        self.reject()
