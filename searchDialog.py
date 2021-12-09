#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2021-12-01
    copyright            : (C) 2021 by Enzo Cocca <enzo.ccc@gmail.com>
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
import os
import re

from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem
from qgis.PyQt.QtCore import QThread

from qgis.core import QgsVectorLayer, Qgis, QgsSettings, QgsProject, QgsMapLayer
from .searchWorker import Worker


FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), 'searchlayers.ui'))


class LayerSearchDialog(QDialog, FORM_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    def __init__(self, iface, parent):
        '''Initialize the LayerSearch dialog box'''
        super(LayerSearchDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # Notify us when vector items ared added and removed in QGIS
        QgsProject.instance().layersAdded.connect(self.updateLayers)
        QgsProject.instance().layersRemoved.connect(self.updateLayers)
        
        self.doneButton.clicked.connect(self.closeDialog)
        self.stopButton.clicked.connect(self.killWorker)
        self.searchButton.clicked.connect(self.runSearch)
        self.clearButton.clicked.connect(self.clearResults)
        self.layerListComboBox.activated.connect(self.layerSelected)
        self.searchFieldComboBox.addItems(['<All Fields>'])
        self.maxResults = 1500
        self.resultsTable.setColumnCount(4)
        self.resultsTable.setSortingEnabled(True)
        if self.L=='it':
            self.resultsTable.setHorizontalHeaderLabels(['Valore','Tabella','Campo','Feature Id'])
            self.comparisonComboBox.addItems(['=','contiene','inizia con'])
        if self.L=='de':
            self.resultsTable.setHorizontalHeaderLabels(['Wert','Tabelle','Feld','Feature Id'])
            self.comparisonComboBox.addItems(['=','enthält','beginnen mit'])
        else:
            self.resultsTable.setHorizontalHeaderLabels(['Value','Table','Field','Feature Id'])
            self.comparisonComboBox.addItems(['=','contains','start with'])    
            
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.resultsTable.itemSelectionChanged.connect(self.select_feature)
        self.worker = None

    def closeDialog(self):
        '''Chiudere la finestra di dialogo quando si preme il pulsante Chiudi'''
        self.hide()
    
    def updateLayers(self):
        '''Chiamato quando un livello è stato aggiunto o cancellato in QGIS.
        Forza la finestra di dialogo a ricaricare.'''
        # Stop any existing search
        self.killWorker()
        if self.isVisible():
            self.populateLayerListComboBox()
            self.clearResults()
        
    def select_feature(self):
        '''Una features è stata selezionata dalla lista, quindi dobbiamo selezionare
        e zoomare su di esso'''
        if self.noSelection:
            # We do not want this event while data is being changed
            return
        # Deselect all selections
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer.removeSelection()
        # Find the layer that was selected and select the feature in the layer
        selectedRow = self.resultsTable.currentRow()
        selectedLayer = self.results[selectedRow][0]
        selectedFeature = self.results[selectedRow][1]
        selectedLayer.select(selectedFeature.id())
        # Zoom to the selected feature
        self.canvas.zoomToSelected(selectedLayer)
    
    def layerSelected(self):
        '''L'utente ha fatto una selezione, quindi dobbiamo inizializzare altre
        parti della finestra di dialogo'''
        self.initFieldList()
        
    def showEvent(self, event):
        '''Si mostra l'evento'''
        super(LayerSearchDialog, self).showEvent(event)
        self.populateLayerListComboBox()
        
    def populateLayerListComboBox(self):
        '''Trova tutti i livelli vettoriali e aggiungili alla lista dei livelli
        che l'utente può selezionare. Inoltre l'utente può cercare su tutti gli
        strati o tutti i livelli selezionati.'''
        layerlist = ['<Tutte le tabelle>','<Seleziona tabella>']
        self.searchLayers = [None, None] # This is same size as layerlist
        layers = QgsProject.instance().mapLayers().values()
        
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layerlist.append(layer.name())
                self.searchLayers.append(layer)

        self.layerListComboBox.clear()
        self.layerListComboBox.addItems(layerlist)
        self.initFieldList()
        
    def initFieldList(self):
        selectedLayer = self.layerListComboBox.currentIndex()
        self.searchFieldComboBox.clear()
        if self.L=='it':
            self.searchFieldComboBox.addItem('<Tutti i campi>')
        elif self.L=='de':
            self.searchFieldComboBox.addItem('<Alle felder>')
        if self.L=='it':
            self.searchFieldComboBox.addItem('<All fields>')    
        
        if selectedLayer > 1:
            self.searchFieldComboBox.setEnabled(True)
            for field in self.searchLayers[selectedLayer].fields():
                self.searchFieldComboBox.addItem(field.name())
        else:
            self.searchFieldComboBox.setCurrentIndex(0)
            self.searchFieldComboBox.setEnabled(False)
    
    def runSearch(self):
        '''Chiamata quando l'utente preme il pulsante Cerca'''
        selectedLayer = self.layerListComboBox.currentIndex()
        comparisonMode = self.comparisonComboBox.currentIndex()
        self.noSelection = True
        try:
            sstr = self.findStringEdit.text().strip()
        except:
            self.showErrorMessage('Invalid search')
            return
            
        if str == '':
            self.showErrorMessage('The searched string is empty')
            return
        if selectedLayer == 0:
            # Include all vector layers
            layers = QgsProject.instance().mapLayers().values()
        elif selectedLayer == 1:
            # Include all selected vector layers
            layers = self.iface.layerTreeView().selectedLayers()
        else:
            # Only search on the selected vector layer
            layers = [self.searchLayers[selectedLayer]]
        self.vlayers=[]
        # Find the vector layers that are to be searched
        for layer in layers:
            if isinstance(layer, QgsVectorLayer):
                self.vlayers.append(layer)
        if len(self.vlayers) == 0:
            self.showErrorMessage('no vectors')
            return
        
        # vlayers contains the layers that we will search in
        self.searchButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.doneButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.clearResults()
        self.resultsLabel.setText('')
        infield = self.searchFieldComboBox.currentIndex() >= 1
        if infield is True:
            selectedField = self.searchFieldComboBox.currentText()
        else:
            selectedField = None
        
        # Because this could take a lot of time, set up a separate thread
        # for a worker function to do the searching.
        thread = QThread()
        worker = Worker(self.vlayers, infield, sstr, comparisonMode, selectedField, self.maxResults)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self.workerFinished)
        worker.foundmatch.connect(self.addFoundItem)
        worker.error.connect(self.workerError)
        self.thread = thread
        self.worker = worker
        self.noSelection = False
        thread.start()

    def workerFinished(self, status):
        '''pulisci il worker e thread'''
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.worker = None
        self.resultsLabel.setText('Results: '+str(self.found))

        self.vlayers = []
        self.searchButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.doneButton.setEnabled(True)
    
    def workerError(self, exception_string):
        '''appare un errore sul display'''
        #self.showErrorMessage(exception_string)
        print(exception_string)
    
    def killWorker(self):
        '''Questo viene avviato quando l'utente preme il pulsante Stop
        e interromperà il processo di ricerca'''
        if self.worker is not None:
            self.worker.kill()
        
    def clearResults(self):
        '''Pulisci il risultato della ricerca'''
        self.noSelection = True
        self.found = 0
        self.results = []
        self.resultsTable.setRowCount(0)        
        self.noSelection = False
    
    def addFoundItem(self, layer, feature, attrname, value):
        '''Abbiamo trovato un elemento, quindi aggiungilo alla lista '''
        self.resultsTable.insertRow(self.found)
        self.results.append([layer, feature])
        self.resultsTable.setItem(self.found, 0, QTableWidgetItem(value))
        self.resultsTable.setItem(self.found, 1, QTableWidgetItem(layer.name()))
        self.resultsTable.setItem(self.found, 2, QTableWidgetItem(attrname))
        self.resultsTable.setItem(self.found, 3, QTableWidgetItem(str(feature.id())))
        
        self.found += 1        
            
    def showErrorMessage(self, message):
        '''Si mostra un messaggio di errore'''
        self.iface.messageBar().pushMessage("", message, level=Qgis.Warning, duration=2)
    
    
    def on_pushButton_go_to_scheda_pressed(self):
        # field_position = self.pyQGIS.findFieldFrDict(self.ID_TABLE) #ricava la posizione del campo
        layer = self.iface.mapCanvas().currentLayer()
        fieldname = self.ID_TABLE
        if not layer:
            if self.L=='it':
                QMessageBox.warning(self, 'ATTENZIONE', "Nessun elemento selezionato", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, 'ACHTUNG', "keine Elemente ausgewählt", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'WARNING', "No items selected", QMessageBox.Ok)
        features_list = layer.selectedFeatures()
        field_position = ""
        for single in layer.getFeatures():
            field_position = single.fieldNameIndex(fieldname)
        id_list = []
        for feat in features_list:
            attr_list = feat.attributes()
            id_list.append(attr_list[field_position])
            # viene impostata la query per il database
        items, order_type = [self.ID_TABLE], "asc"
        self.empty_fields()
        self.DATA_LIST = []
        temp_data_list = self.DB_MANAGER.query_sort(id_list, items, order_type, self.MAPPER_TABLE_CLASS, self.ID_TABLE)
        for us in temp_data_list:
            self.DATA_LIST.append(us)
            # vengono riempiti i campi con i dati trovati
        self.fill_fields()
        self.BROWSE_STATUS = 'b'
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<type 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]