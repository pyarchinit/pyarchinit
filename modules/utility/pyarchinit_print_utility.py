#! /usr/bin/env python
#-*- coding: utf-8 -*-
"""
/***************************************************************************
 testerDialog
								 A QGIS plugin
 test print
							 -------------------
		begin				 : 2012-06-20
		copyright			 : (C) 2012 by luca
		email				 : pyarchinit@gmail.com
 ***************************************************************************/

/***************************************************************************
 *																		   *
 *	 This program is free software; you can redistribute it and/or modify  *
 *	 it under the terms of the GNU General Public License as published by  *
 *	 the Free Software Foundation; either version 2 of the License, or	   *
 *	 (at your option) any later version.								   *
 *																		   *
 ***************************************************************************/
"""
import os

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui

from qgis.core import *
from qgis.gui import *

from settings import *

#from ui_tester import Ui_tester
# create the dialog for zoom to point

class Print_utility:
	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']
	FILEPATH = os.path.dirname(__file__)
	LAYER_STYLE_PATH = ('%s%s%s%s') % (FILEPATH, os.sep, 'styles', os.sep)
	LAYER_STYLE_PATH_SPATIALITE = ('%s%s%s%s') % (FILEPATH, os.sep, 'styles_spatialite', os.sep)
	SRS = 3004

	layerUS = ""
	layerQuote = ""
##	layerCL = ""
##	layerGriglia = "" #sperimentale da riattivare

	USLayerId = ""
	CLayerId = ""
	QuoteLayerId = ""
	GrigliaLayerId = ""

	mapHeight = ""
	mapWidth = ""

	tav_num = ""
	us = ""
	uri = ""


	def __init__(self, iface, data):
		self.iface = iface
		self.data = data
		#self.area = area
		#self.us = us
		self.canvas = self.iface.mapCanvas()
		# set host name, port, database name, username and password

	"""
	def on_pushButton_runTest_pressed(self):
		self.first_batch_try()
    """

	def first_batch_try(self, server):
		self.server = server
		##		f = open("C:\Users\Windows\pyarchinit_Report_folder\test.txt", "w")
		##		f.write(str(server))
		##		f.close()
		if self.server == 'postgres':
			for i in range(len(self.data)):
				test = self.charge_layer_postgis(self.data[i].sito, self.data[i].area, self.data[i].us)
				self.us = self.data[i].us
				if test != 0:
					if self.layerUS.featureCount() > 0:
						self.test_bbox()
						tav_num= i
						self.print_map(tav_num)
					else:
						self.remove_layer()
			if test == 0:
				Report_path = ('%s%s%s') % (self.HOME, os.sep, "pyarchinit_Report_folder/report_errori.txt")
				f = open(Report_path, "w")
				f.write(str("Presenza di errori nel layer"))
				f.close()

		elif self.server == 'sqlite':
			for i in range(len(self.data)):
				test = self.charge_layer_sqlite(self.data[i].sito, self.data[i].area, self.data[i].us)
				self.us = self.data[i].us
				if test != 0:
					if self.layerUS.featureCount() > 0:
						self.test_bbox()
						tav_num= i
						self.print_map(tav_num)
					else:
						self.remove_layer()
				else:
					pass

			"""
			for i in self.data:
				self.charge_layer_postgis(i.sito,i.area,i.us)
				self.test_bbox()
				self.print_map(i)
			"""

	def converter_1_20(self, n):
		n *= 100
		res = n / 20
		return res

	def test_bbox(self):
		#f = open("/test_type.txt", "w")
		#ff.write(str(type(self.layerUS)))
		#ff.close()

		self.layerUS.select( [] ) # recuperi tutte le geometrie senza attributi
		featPoly = QgsFeature() # crei una feature vuota per il poligono

		dizionario_id_contains = {}
		lista_quote = []

		self.layerUS.nextFeature( featPoly ) # cicli sulle feature recuperate, featPoly conterra la feature poligonale attuale
		bbox = featPoly.geometry().boundingBox() # recupera i punti nel bbox del poligono
		self.height = self.converter_1_20(float(bbox.height())) * 10 #la misura da cm e' portata in mm
		self.width = self.converter_1_20(float(bbox.width())) * 10 #la misura da cm e' portata in mm

		#f = open("/test_paper_size_5.txt", "w")
		#f.write(str(self.width))
		#f.close()


	def getMapExtentFromMapCanvas(self,	 mapWidth, mapHeight, scale):
		#code from easyPrint plugin
		#print "in methode: " + str(scale)

		xmin = self.canvas.extent().xMinimum()
		xmax = self.canvas.extent().xMaximum()
		ymin = self.canvas.extent().yMinimum()
		ymax = self.canvas.extent().yMaximum()
		xcenter = xmin + (xmax - xmin) / 2
		ycenter = ymin + (ymax - ymin) / 2 

		mapWidth = mapWidth * scale / 1000 #misura in punti
		mapHeight = mapHeight * scale / 1000 #misura in punti
		
		#f = open("/test_paper_size_3.txt", "w")
		#f.write(str(mapWidth))
		#f.close()

		minx = xcenter - mapWidth / 2
		miny = ycenter - mapHeight / 2
		maxx = xcenter + mapWidth / 2
		maxy = ycenter + mapHeight / 2 

		return QgsRectangle(minx,  miny,  maxx,	 maxy)


	def print_map(self, tav_num):
		self.tav_num = tav_num

		mapRenderer = self.iface.mapCanvas().mapRenderer()
		
		c = QgsComposition(mapRenderer)
		c.setPlotStyle(QgsComposition.Print)

		#map - this item tells the libraries where to put the map itself. Here we create a map and stretch it over the whole paper size:
		x, y = 0, 0 #angolo 0, o in alto a sx

		if (self.width >= 0 and self.width <= 297) and (self.height >= 0 and self.height <= 210):
			width, height = 297, 210 #Formato A4 Landscape
		elif (self.height >= 0 and self.height <= 297) and (self.width >= 0 and self.width <= 210):
			width, height = 210, 297 #Formato A4

		elif (self.width >= 0 and self.width <= 420) and (self.height >= 0 and self.height <= 297):
			width, height = 297, 420  #Formato A3 Landscape
		elif (self.height >= 0 and self.height <= 420) and (self.width >= 0 and self.width <= 297):
			width, height = 240, 297 #Formato A4

		elif (self.width >= 0 and self.width <= 1189) and (self.height >= 0 and self.height <= 841):
			width, height = 1189, 841  #Formato A0 Landscape
		elif (self.height >= 0 and self.height <= 1189) and (self.width >= 0 and self.width <= 841):
			width, height = 841, 1189 #Formato A0
		else:
			width, height = self.width*1.2, self.height*1.2  #self.width*10, self.height*10 da un valore alla larghezza e altezza del foglio aumentato di 5 per dare un margine

		dpi = 100 #viene settata la risoluzione di stampa

		c.setPaperSize(width, height) #setta le dimensioni della pagina
		composerMap = QgsComposerMap(c, x, y, width, height) #crea un mapComposer passandogli la classere Composition che a sua volta ha incapsulato con la classe mapRenderer il canvas corrente
		rect = self.getMapExtentFromMapCanvas(c.paperWidth(), c.paperHeight(), 20.0) #ricava la mappa in scala da inserire nel compositore passando le dimensioni di pagina in mm e ricavandoli in punti
		composerMap.setNewExtent(rect) #setta l'estensione della mappa
		c.addItem(composerMap) #aggiunge la mappa alla composizione c


		intestazioneLabel = QgsComposerLabel(c)
		txt = "Tavola %s - US:%d" % (self.tav_num+1, self.us)
		intestazioneLabel.setText(txt)
		intestazioneLabel.adjustSizeToText()
		# set label 1cm from the top and 2cm from the left of the page
		#intestazioneLabel.setItemPosition(1,0)
		# set both label's position and size (width 10cm, height 3cm)
		intestazioneLabel.setItemPosition(1,0)
		#A frame is drawn around each item by default. How to remove the frame:
		intestazioneLabel.setFrame(False)
		c.addItem(intestazioneLabel)
	
		scaleLabel = QgsComposerLabel(c)
		txt = "Scala: "
		scaleLabel.setText(txt)
		scaleLabel.adjustSizeToText()
		# set label 1cm from the top and 2cm from the left of the page
		scaleLabel.setItemPosition(1,5)
		# set both label's position and size (width 10cm, height 3cm)
		#composerLabel.setItemPosition(20,10, 100, 30)
		#A frame is drawn around each item by default. How to remove the frame:
		scaleLabel.setFrame(False)
		c.addItem(scaleLabel)



		#aggiunge la scale bar
		scaleBarItem = QgsComposerScaleBar(c)
		scaleBarItem.setStyle('Numeric') # optionally modify the style
		scaleBarItem.setComposerMap(composerMap)
		scaleBarItem.applyDefaultSize()
		scaleBarItem.setItemPosition(10,5)
		scaleBarItem.setFrame(False)
		c.addItem(scaleBarItem)
		
		#ff = open("/test_scaleBar.txt", "w")
		#ff.write(str(dir(scaleBarItem)))
		#ff.close()


		"""
		#aggiunge la scale bar
		scaleBarLine = QgsComposerScaleBar(c)
		scaleBarLine.setStyle('Line Ticks Middle') # optionally modify the style
		scaleBarLine.setUnitLabeling('m')
		scaleBarLine.setComposerMap(composerMap)
		scaleBarLine.applyDefaultSize()
		scaleBarLine.setItemPosition(0,50)
		scaleBarLine.setFrame(False)
		c.addItem(scaleBarLine)
		"""

		c.setPrintResolution(dpi) #setta la risoluzione di stampa

		#Output to a raster image
		#The following code fragment shows how to render a composition to a raster image:
		dpmm = dpi / 25.4 #ricava il valore dei punti per mm
		width_point = float(dpmm * c.paperWidth())
		height_point = float(dpmm * c.paperHeight())

		# create output image and initialize it
		image = QImage(QSize(width_point, height_point), QImage.Format_ARGB32)
		image.setDotsPerMeterX(dpmm * 1000)
		image.setDotsPerMeterY(dpmm * 1000)
		image.fill(0)

		# render the composition
		imagePainter = QPainter(image)
		sourceArea = QRectF(0, 0, c.paperWidth(), c.paperHeight()) #viene settata l'area sorgente con le misure in mm della carta
		targetArea = QRectF(0, 0, width_point, height_point) #viene settata l'area in cui inserire la mappa con le misure in punti per mm
		c.render(imagePainter, targetArea, sourceArea)
		imagePainter.end()
		
		MAPS_path = ('%s%s%s') % (self.HOME, os.sep, "pyarchinit_MAPS_folder")
		tav_name = ("Tavola_%d_us_%d.png") % (self.tav_num+1, self.us)
		filename_png = ('%s%s%s') % (MAPS_path, os.sep, tav_name)
		image.save(str(filename_png), "png")
		
		self.remove_layer()
		
		#f = open("/test_registry.txt", "w")
		#f.write(str(type(self.USLayerId)))
		#f.close()
		
		#QgsMapLayerRegistry.instance().removeMapLayer(layer_id)

		#Output to PDF
		#The following code fragment renders a composition to a PDF file:
		"""
		printer = QPrinter()
		printer.setOutputFormat(QPrinter.PdfFormat)
		printer.setOutputFileName("/out.pdf")
		printer.setPaperSize(QSizeF(self.mapWidth, self.mapHeight), QPrinter.Millimeter)
		printer.setFullPage(True)
		printer.setColorMode(QPrinter.Color)
		printer.setResolution(c.printResolution())

		pdfPainter = QPainter(printer)
		paperRectMM = printer.pageRect(QPrinter.Millimeter)
		paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
		c.render(pdfPainter, paperRectPixel, paperRectMM)
		pdfPainter.end()
		"""

	def open_connection_postgis(self):
		cfg_rel_path = os.path.join(os.sep,'pyarchinit_DB_folder', 'config.cfg')
		file_path = ('%s%s') % (self.HOME, cfg_rel_path)
		conf = open(file_path, "r")
		con_sett = conf.read()
		conf.close() 
		settings = Settings(con_sett)
		settings.set_configuration()
		self.uri = QgsDataSourceURI()
		self.uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

	def remove_layer(self):
		if self.USLayerId != "":
			QgsMapLayerRegistry.instance().removeMapLayer(self.USLayerId)
			self.USLayerId = ""

##		if self.CLayerId != "":
##			QgsMapLayerRegistry.instance().removeMapLayer(self.CLayerId)
##			self.CLayerId = ""

		if self.QuoteLayerId != "":
			QgsMapLayerRegistry.instance().removeMapLayer(self.QuoteLayerId)
			self.QuoteLayerId = ""
#sperimentale da riattivare
##		if self.GrigliaLayerId != "":
##			QgsMapLayerRegistry.instance().removeMapLayer(self.GrigliaLayerId)
##			self.GrigliaLayerId = ""

	def charge_layer_sqlite(self, sito, area, us):
		sqliteDB_path = os.path.join(os.sep,'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')

		db_file_path = ('%s%s') % (self.HOME, sqliteDB_path)

		srs = QgsCoordinateReferenceSystem(3004, QgsCoordinateReferenceSystem.PostgisCrsId)


		gidstr = ("scavo_s = '%s' and area_s = '%s' and us_s = '%d'") % (sito, area, us)

		uri = QgsDataSourceURI()
		uri.setDatabase(db_file_path)

		uri.setDataSource('','pyarchinit_us_view', 'the_geom', gidstr, "ROWID")
		self.layerUS=QgsVectorLayer(uri.uri(), 'pyarchinit_us_view', 'spatialite')

		if self.layerUS.isValid() == True:
			self.layerUS.setCrs(srs)
			self.USLayerId = self.layerUS.getLayerID()
			#self.mapLayerRegistry.append(USLayerId)
			style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
			self.layerUS.loadNamedStyle(style_path)
			self.iface.mapCanvas().setExtent(self.layerUS.extent())
			QgsMapLayerRegistry.instance().addMapLayer( self.layerUS, True)
		else:
			return 0
			#QMessageBox.warning(self, "Messaggio", "Geometria inesistente", QMessageBox.Ok)

		gidstr = ("sito_q = '%s' and area_q = '%s' and us_q = '%d'") % (sito, area, us)

		uri.setDataSource('','pyarchinit_quote_view', 'the_geom', gidstr, "ROWID")
		self.layerQuote=QgsVectorLayer(uri.uri(), 'pyarchinit_quote_view', 'spatialite')

		if self.layerQuote.isValid() == True:
			self.layerQuote.setCrs(srs)
			self.QuoteLayerId = self.layerQuote.getLayerID()
			#self.mapLayerRegistry.append(QuoteLayerId)
			style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'stile_quote.qml')
			self.layerQuote.loadNamedStyle(style_path)
			QgsMapLayerRegistry.instance().addMapLayer(self.layerQuote, True)

#SPERIMENTALE DA RIATTIVARE
##		gidstr = ("sito = '%s' AND def_punto = 'Griglia'") % (sito)
##
##		self.uri.setDataSource("public", "pyarchinit_punti_rif", "the_geom", gidstr)
##		self.layerGriglia = QgsVectorLayer(self.uri.uri(), "Quote", "postgres")
##
##		if self.layerGriglia.isValid() == True:
##			self.layerGriglia.setCrs(srs)
##			self.GrigliaLayerId =  self.layerGriglia.getLayerID()
##			#self.mapLayerRegistry.append(USLayerId)
##			style_path = ('%s%s') % (self.LAYER_STYLE_PATH, 'stile_griglia.qml')
##			self.layerGriglia.loadNamedStyle(style_path)
##			QgsMapLayerRegistry.instance().addMapLayer( self.layerGriglia, True)

	def charge_layer_postgis(self, sito, area, us):
		self.open_connection_postgis()
		
		srs = QgsCoordinateReferenceSystem(3004, QgsCoordinateReferenceSystem.PostgisCrsId)

		gidstr = ("scavo_s = '%s' and area_s = '%s' and us_s = '%d'") % (sito, area, us)

		self.uri.setDataSource("public", "pyarchinit_us_view", "the_geom", gidstr, 'gid')

		self.layerUS = QgsVectorLayer(self.uri.uri(), "US", "postgres")

		if self.layerUS.isValid() == True:
			self.layerUS.setCrs(srs)
			self.USLayerId = self.layerUS.getLayerID()
			#self.mapLayerRegistry.append(USLayerId)
			style_path = ('%s%s') % (self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
			self.layerUS.loadNamedStyle(style_path)
			self.iface.mapCanvas().setExtent(self.layerUS.extent())
			QgsMapLayerRegistry.instance().addMapLayer( self.layerUS, True)
		else:
			return 0

		gidstr = ("sito_q = '%s' and area_q = '%s' and us_q = '%d'") % (sito, area, us)

		self.uri.setDataSource("public", "pyarchinit_quote", "the_geom", gidstr, 'gid')
		self.layerQuote = QgsVectorLayer(self.uri.uri(), "Quote", "postgres")

		if self.layerQuote.isValid() == True:
			self.layerQuote.setCrs(srs)
			self.QuoteLayerId = self.layerQuote.getLayerID()
			#self.mapLayerRegistry.append(QuoteLayerId)
			style_path = ('%s%s') % (self.LAYER_STYLE_PATH, 'stile_quote.qml')
			self.layerQuote.loadNamedStyle(style_path)
			QgsMapLayerRegistry.instance().addMapLayer(self.layerQuote, True)

#SPERIMENTALE DA RIATTIVARE
##		gidstr = ("sito = '%s' AND def_punto = 'Griglia'") % (sito)
##
##		self.uri.setDataSource("public", "pyarchinit_punti_rif", "the_geom", gidstr)
##		self.layerGriglia = QgsVectorLayer(self.uri.uri(), "Quote", "postgres")
##
##		if self.layerGriglia.isValid() == True:
##			self.layerGriglia.setCrs(srs)
##			self.GrigliaLayerId =  self.layerGriglia.getLayerID()
##			#self.mapLayerRegistry.append(USLayerId)
##			style_path = ('%s%s') % (self.LAYER_STYLE_PATH, 'stile_griglia.qml')
##			self.layerGriglia.loadNamedStyle(style_path)
##			QgsMapLayerRegistry.instance().addMapLayer( self.layerGriglia, True)
