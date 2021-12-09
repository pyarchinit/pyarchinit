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

from qgis.PyQt.QtCore import QObject, pyqtSignal

from qgis.core import QgsVectorLayer, QgsFeatureRequest
import traceback

class Worker(QObject):
    '''Questo fa tutto il lavoro duro. Prende tutti i parametri di ricerca e 
    cerca una corrispondenza attraverso i livelli vettoriali.'''
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    foundmatch = pyqtSignal(QgsVectorLayer, object, object, str)
    
    def __init__(self, vlayers, infield, searchStr, comparisonMode, selectedField, maxResults):
        QObject.__init__(self)
        self.vlayers = vlayers
        self.infield = infield
        self.searchStr = searchStr
        self.comparisonMode = comparisonMode
        self.selectedField = selectedField
        self.killed = False
        self.maxResults = maxResults
        
    def run(self):
        '''Worker esegue routine'''
        self.found = 0
        try:
            # Check to see if we are searching within a particular column of a specified
            # layer or whether we are searching all columns.
            if self.infield is True:
                for layer in self.vlayers:
                    self.searchFieldInLayer(layer, self.searchStr, self.comparisonMode, self.selectedField)
            else:
                for layer in self.vlayers:
                    self.searchLayer(layer, self.searchStr, self.comparisonMode)
        except:
            self.error.emit(traceback.format_exc())
        self.finished.emit(True)
            
    def kill(self):
        '''imposta uno stop alla ricerca'''
        self.killed = True
        
    def searchLayer(self, layer, searchStr, comparisonMode):
        '''Esegue una ricerca per stringa in tutte le colonne di una tabella'''
        if self.killed:
            return
        fnames = []
        # Get and Keep a copy of the field names
        for field in layer.fields():
            fnames.append(field.name())
        # Get an iterator for all the features in the vector
        iter = layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry))
        if comparisonMode == 0: # Searching for an exact match
            for feature in iter:
                # Check to see if it has been aborted
                if self.killed is True:
                    return
                # Get all the feature attributes or columns
                attrs = feature.attributes()
                # For now just search as if it were a string
                for id, f in enumerate(attrs):
                    try:
                        if str(f) == searchStr:
                            self.foundmatch.emit(layer, feature, fnames[id], str(f))
                            self.found += 1
                            if self.found >= self.maxResults:
                                self.killed=True
                                return
                    except:
                        pass
        elif comparisonMode == 1: # contains string
            p = re.compile(re.escape(searchStr), re.I|re.UNICODE)
            for feature in iter:
                # Check to see if it has been aborted
                if self.killed is True:
                    return
                attrs = feature.attributes()
                # For now just search as if it were a string
                for id, f in enumerate(attrs):
                    try:
                        if p.search(str(f)):
                            self.foundmatch.emit(layer, feature, fnames[id], str(f))
                            self.found += 1
                            if self.found >= self.maxResults:
                                self.killed=True
                                return
                    except:
                        pass
        else: # begins with string
            p = re.compile(re.escape(searchStr), re.I|re.UNICODE)
            for feature in iter:
                # Check to see if it has been aborted
                if self.killed is True:
                    return
                attrs = feature.attributes()
                # For now just search as if it were a string
                for id, f in enumerate(attrs):
                    try:
                        if p.match(str(f)):
                            self.foundmatch.emit(layer, feature, fnames[id], str(f))
                            self.found += 1
                            if self.found >= self.maxResults:
                                self.killed=True
                                return
                    except:
                        pass

    def searchFieldInLayer(self, layer, searchStr, comparisonMode, selectedField):
        '''Esegue una ricerca per stringa su una colonna specifica della tabella.'''
        if self.killed:
            return

        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
        request.setSubsetOfAttributes([selectedField], layer.fields())
        if comparisonMode == 0: # Searching for an exact match
            request.setFilterExpression('"{}" LIKE \'{}\''.format(selectedField,searchStr))
        elif comparisonMode == 1: # contains string
            
            request.setFilterExpression('"{}" ILIKE \'%{}%\''.format(selectedField,searchStr))
        else: # begins with string
            request.setFilterExpression('"{}" ILIKE \'%{}%\''.format(selectedField,searchStr))

        for feature in layer.getFeatures(request):
            # Check to see if it has been aborted
            if self.killed is True:
                return
            f = feature.attribute(selectedField)
            self.foundmatch.emit(layer, feature, selectedField, str(f))
            self.found += 1
            if self.found >= self.maxResults:
                self.killed=True
                return

