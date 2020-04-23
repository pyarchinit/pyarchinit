import os
import re

from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem
from qgis.PyQt.QtCore import QThread

from qgis.core import QgsVectorLayer, Qgis, QgsProject, QgsMapLayer
from .searchWorker import Worker


FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), 'searchlayers.ui'))


class LayerSearchDialog(QDialog, FORM_CLASS):
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
        self.resultsTable.setSortingEnabled(False)
        self.resultsTable.setHorizontalHeaderLabels(['Valore','Tabella','Campo','Feature Id'])
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.comparisonComboBox.addItems(['=','contiene','inizia con'])
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
        self.searchFieldComboBox.addItem('<Tutti i campi>')
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
            self.showErrorMessage('Ricerca invalida ')
            return
            
        if str == '':
            self.showErrorMessage('La stringa cercata è vuota')
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
            self.showErrorMessage('qui non ci sono strati vettoriali da cercare')
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
        self.resultsLabel.setText('Risultati: '+str(self.found))

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
