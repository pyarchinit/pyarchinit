import os
import copy
from reportlab.lib.testutils import makeSuiteForClasses, outputfile, printLocation
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Paragraph, Spacer, TableStyle
from reportlab.platypus.paragraph import Paragraph

from datetime import date, time

from pyarchinit_OS_utility import *

class NumberedCanvas_Individuisheet(canvas.Canvas):
	def __init__(self, *args, **kwargs):
		canvas.Canvas.__init__(self, *args, **kwargs)
		self._saved_page_states = []
		
	def define_position(self, pos):
		self.page_position(pos)

	def showPage(self):
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()

	def save(self):
		"""add page info to each page (page x of y)"""
		num_pages = len(self._saved_page_states)
		for state in self._saved_page_states:
			self.__dict__.update(state)
			self.draw_page_number(num_pages)
			canvas.Canvas.showPage(self)
		canvas.Canvas.save(self)

	def draw_page_number(self, page_count):
		self.setFont("Helvetica", 8)
		self.drawRightString(200*mm, 20*mm, "Pag. %d di %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm

class single_pdf_sheet:
	DATA = ""
	def __init__(self, data):
		self.DATA = data
##		print data
##		self.area = data[1]
##		self.us = data[2]
##		self.nr_individuo = data[3]
##		self.data_schedatura = data[4]
##		self.schedatore = data[5]
##		self.sesso = data[6]
##		self.eta_min = data[7]
##		self.eta_max =  data[8]
##		self.classi_eta = data[9]
##		self.osservazioni = data[10]

	def datestrfdate(self):
		now = date.today()
		today = now.strftime("%d-%m-%Y")
		return today

	def create_sheet(self):
		styleSheet = getSampleStyleSheet()
		styNormal = styleSheet['Normal']
		styNormal.spaceBefore = 20
		styNormal.spaceAfter = 20
		styNormal.alignment = 0 #LEFT

		styleSheet = getSampleStyleSheet()
		styDescrizione = styleSheet['Normal']
		styDescrizione.spaceBefore = 20
		styDescrizione.spaceAfter = 20
		styDescrizione.alignment = 4 #Justified

		values_dict = {}
##		print len(self.DATA)
		for i in range(len(self.DATA)):
			values_dict["val"+str(i)] = self.DATA[i]
##			print values_dict

##		print values_dict
##		
		paragraph_list = []
		for i in range(len(values_dict)):
			key = "val"+str(i)
			paragraph_list.append(Paragraph("<b>" + values_dict[key] + "</b><br/>", styNormal))

##		#0 row
##		intestazione = Paragraph("<b>SCHEDA INDIVIDUI<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
##		intestazione2 = Paragraph("<b>pyArchInit</b>", styNormal)
##
##		#1 row
##		sito = Paragraph("<b>Sito</b><br/>"  + str(self.sito), styNormal)
##		area = Paragraph("<b>Area</b><br/>"  + str(self.area), styNormal)
##		us = Paragraph("<b>US</b><br/>"  + str(self.us), styNormal)
##		nr_inventario = Paragraph("<b>Nr. Individuo</b><br/>"  + str(self.nr_individuo), styNormal)
##
##		#2 row
##		sesso = Paragraph("<b>Sesso</b><br/>"  + self.sesso, styNormal)
##		eta_min = Paragraph("<b>Eta' minima</b><br/>"  + self.eta_min, styNormal)
##		eta_max = Paragraph("<b>Eta' massima</b><br/>"  + self.eta_max, styNormal)
##
##		#3 row
##		classi_eta = Paragraph("<b>Classi di eta'</b><br/>"  + self.classi_eta, styNormal)
##
##		#4 row
##		osservazioni = ''
##		try:
##			osservazioni = Paragraph("<b>Osservazioni</b><br/>" + str(self.osservazioni), styDescrizione)
##		except:
##			pass
##
##		#12 row
##		data_schedatura  = Paragraph("<b>Data schedatura</b><br/>" + self.data_schedatura,styNormal)
##		schedatore = Paragraph("<b>Schedatore</b><br/>" + self.schedatore,styNormal)

		#schema
		cell_schema =  [ #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
						[paragraph_list[0], 'value', '02', '03', '04','05', '06', '07', paragraph_list[1], '09'],
						[paragraph_list[2], '01', '02', paragraph_list[3], '04', paragraph_list[4],'06', '07', paragraph_list[4], '09'], #1 row ok
						[paragraph_list[5], '01', '02', paragraph_list[6],'04', '05',paragraph_list[7], '07', '08', '09'], #2 row ok
						[paragraph_list[8], '01', '02', '03', '04', '05', '06', '07', '08', '09'], #3 row ok
						[paragraph_list[9], '01','02', '03', '04', '05','06', '07', '08', '09'], #4 row ok
						[paragraph_list[10], '01', '02', '03', '04', '05', paragraph_list[10], '07', '08', '09'], #5 row ok
						['https://sites.google.com/site/pyarchinit/', '01', '02', '03', '04','05', '06', '07','08', '09'] #6 row
						]


		#table style
		table_style=[

					('GRID',(0,0),(-1,-1),0.5,colors.black),
					#0 row
					('SPAN', (0,0),(7,0)),  #intestazione
					('SPAN', (8,0),(9,0)), #intestazione2

					#1 row
					('SPAN', (0,1),(2,1)),  #sito
					('SPAN', (3,1),(4,1)),  #area
					('SPAN', (5,1),(7,1)),  #us
					('SPAN', (8,1),(9,1)),  #nr_inventario

					#2 row
					('SPAN', (0,2),(2,2)),  #sesso
					('SPAN', (3,2),(5,2)),  #eta_min
					('SPAN', (6,2),(9,2)),  #eta_max
					('VALIGN',(0,2),(9,2),'TOP'), 

					#3 row
					('SPAN', (0,3),(9,3)), #classi_eta
					
					#4 row
					('SPAN', (0,4),(9,4)),  #osservazioni

					#5 row
					('SPAN', (0,5),(5,5)),  #data_schedatura
					('SPAN', (6,5),(9,5)),  #schedatore

					#13 row
					('SPAN', (0,6),(9,6)),  #pie' di pagina
					('ALIGN',(0,6),(9,6),'CENTER')

					]

		t=Table(cell_schema, colWidths=50, rowHeights=None,style= table_style)

		return t
	
class generate_pdf:
	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']
	
	PDF_path = ('%s%s%s') % (HOME, os.sep, "pyarchinit_PDF_folder")

	def datestrfdate(self):
		now = date.today()
		today = now.strftime("%d-%m-%Y")
		return today

	def build_Individui_sheets(self, records):
		elements = []
		for i in range(len(records)):
			single_pdf_sheet_class = single_pdf_sheet(records[i])
			elements.append(single_pdf_sheet_class.create_sheet())
			elements.append(PageBreak())
		filename = ('%s%s%s') % (self.PDF_path, os.sep, 'scheda_Individui.pdf')
##		print "pippo"
		f = open(filename, "wb")
		doc = SimpleDocTemplate(f)
		doc.build(elements, canvasmaker=NumberedCanvas_Individuisheet)
		f.close()

if __name__ == '__main__':
##	print "gigi"
	gen_pdf = generate_pdf()
	gen_pdf.build_Individui_sheets([["a", "pyArchInit", "c", "d", "e", "f", "g", "h", "i", "l", "m"]])
	
	
	
	
	