import datetime
from datetime import date
from builtins import object
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import (A4)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph
from .pyarchinit_OS_utility import *
from ..db.pyarchinit_conn_strings import Connection
class NumberedCanvas_USsheet(canvas.Canvas):
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
        self.drawRightString(200*mm, 20*mm, "Page %d of %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm
class NumberedCanvas_USindex(canvas.Canvas):
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
        self.drawRightString(270*mm, 10*mm, "Page %d of %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm
class single_pottery_pdf_sheet:
    def __init__(self, data):
        #self.id_dive=data[0]
        self.divelog_id=data[0]                                 
        self.artefact_id=data[1]
        self.sito=data[2]   
        self.area=data[3]   
        self.fabric=data[4] 
        self.specific_shape=data[5] 
        self.specific_part=data[6]  
        self.category=data[7]
        self.typology=data[8]   
        self.depth=data[9]
        self.retrieved=data[10] 
        self.percent=data[11]
        self.provenience=data[12]   
        self.munsell=data[13]
        self.munsell_surf=data[14]
        self.surf_trat=data[15] 
        self.treatment=data[16]
        self.storage_=data[17]  
        self.period=data[18]
        self.state=data[19]
        self.samples=data[20]                                        
        self.washed=data[21]                    
        self.diametro_max=data[22]  
        self.diametro_rim=data[23]
        self.diametro_bottom=data[24]   
        self.total_height=data[25]
        self.preserved_height=data[26]  
        self.base_height=data[27]   
        self.thickmin=data[28]  
        self.thickmax=data[29]
        self.data_=data[30] 
        self.anno=data[31]
        self.description=data[32]
        self.photographed=data[33]                                       
        self.drawing=data[34]
        self.wheel_made=data[35]    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def create_sheet(self):
        styleSheet = getSampleStyleSheet()
        stylogo = styleSheet['Normal']
        stylogo.spaceBefore = 20
        stylogo.spaceAfter = 20
        stylogo.alignment = 1  # LEFT    
        styleSheet = getSampleStyleSheet()
        styInt = styleSheet['Normal']
        styInt.spaceBefore = 20
        styInt.spaceAfter = 20
        styInt.fontSize = 8
        styInt.alignment = 1  # LEFT    
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 6
        styNormal.alignment = 0  # LEFT
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 6
        styDescrizione.alignment = 4  # Justified
        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.alignment = 1  # CENTER
        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti.fontSize = 6
        styTitoloComponenti.alignment = 1  # CENTER
        intestazione = Paragraph("<b>Archaeological Underwater Survey - POTTERY FORM<br/>" + "</b>", styInt)
        home = os.environ['PYARCHINIT_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.png')
        logo = Image(logo_path)
        ##      if test_image.drawWidth < 800:
        logo.drawHeight = 0.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 0.5*inch
        logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo2.png')
        logo2 = Image(logo_path2)
        ##      if test_image.drawWidth < 800:
        logo2.drawHeight = 0.5*inch*logo2.drawHeight / logo2.drawWidth
        logo2.drawWidth = 0.5*inch
        #1 row
        divelog_id = Paragraph("<b>Dive ID</b><br/>"  + str(self.divelog_id), styNormal)
        artefact_id = Paragraph("<b>Artefact ID</b><br/>"  + self.artefact_id, styNormal)
        sito = Paragraph("<b>Site</b><br/>"  + self.sito, styNormal)
        area = Paragraph("<b>Area</b><br/>"  + self.area, styNormal)
        fabric = Paragraph("<b>Inclusions</b><br/>"  + self.fabric, styNormal)
        specific_shape = Paragraph("<b>Form</b><br/>"  + self.specific_shape, styNormal)
        specific_part = Paragraph("<b>Specific Part</b><br/>"  + self.specific_part, styNormal)
        category = Paragraph("<b>Category</b><br/>"  + self.category, styNormal)
        typology = Paragraph("<b>Typology</b><br/>"  + self.typology, styNormal)
        depth = Paragraph("<b>Depth</b><br/>"  + self.depth, styNormal)
        retrieved = Paragraph("<b>Retrieved</b><br/>"  + self.retrieved, styNormal)
        percent = Paragraph("<b>Percent of inclusion</b><br/>"  + self.percent , styNormal)
        provenience=Paragraph("<b>Provenance</b><br/>"  + self.provenience, styNormal)
        munsell = Paragraph("<b>Munsell Clay</b><br/>"  + self.munsell, styNormal)
        munsell_surf = Paragraph("<b>Munsell Surfaces</b><br/>"  + self.munsell_surf, styNormal)
        surf_trat = Paragraph("<b>Surface Treatment</b><br/>"  + self.surf_trat, styNormal)
        treatment = Paragraph("<b>Conservation</b><br/>"  + self.treatment, styNormal)
        period = Paragraph("<b>Period</b><br/>"  + self.period, styNormal)
        state = Paragraph("<b>State</b><br/>"  + self.state, styNormal)
        samples = Paragraph("<b>Samples</b><br/>"  + self.samples, styNormal)
        diametro_max = Paragraph("<b>Diameter Max</b><br/>"  + str(self.diametro_max), styNormal)
        diametro_rim = Paragraph("<b>Diameter Rim</b><br/>"  + str(self.diametro_rim) , styNormal)
        diametro_bottom = Paragraph("<b>Diameter Bottom</b><br/>"  + str(self.diametro_bottom), styNormal)
        total_height = Paragraph("<b>Total Height</b><br/>"  + str(self.total_height), styNormal)
        preserved_height = Paragraph("<b>Preserved Height</b><br/>"  + str(self.preserved_height), styNormal)
        base_height = Paragraph("<b>Base Height</b><br/>"  + str(self.base_height), styNormal)
        thickmin = Paragraph("<b>Thickness Min</b><br/>"  + str(self.thickmin), styNormal)
        thickmax = Paragraph("<b>Thickness Max</b><br/>"  + str(self.thickmax), styNormal)
        description = Paragraph("<b>Description</b><br/>"  + self.description, styNormal)
        data_ = Paragraph("<b>Date</b><br/>"  + self.data_, styNormal)
        anno = Paragraph("<b>Year</b><br/>"  + str(self.anno), styNormal)
        photographed = Paragraph("<b>Photographed</b><br/>"  + self.photographed, styNormal)
        drawing = Paragraph("<b>Drawing</b><br/>"  + self.drawing, styNormal)
        wheel_made = Paragraph("<b>Wheel Made</b><br/>"  + self.wheel_made, styNormal)
        #schema
        cell_schema =  [
                        #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        [logo2, '01', intestazione,'03' , '04','05', '06', '07', '08', '09','10','11','12','13', '14','15',logo,'17'], #0 row ok
                        [sito, '01', '02', '03', '04','05', '06', '07', '08',artefact_id,'10','11','12','13', '14','15','16','17'], #1 row ok
                        [divelog_id, '01', '02', '03', '04','05', area, '07', '08', '09','10','11',anno,'13', '14','15','16','17'], #2 row ok
                        [fabric, '01', '02', '03', '04','05',specific_part, '07', '08', '09','10','11',category,'13', '14','15','16','17'], #2 row ok
                        [specific_shape, '01', '02', '03', '04','05',  typology, '07', '08', '09','10','11',depth,'13', '14','15','16','17'], #2 row ok
                        [retrieved, '01', '02', '03', '04','05', percent, '07', '08', '09','10','11',provenience,'13', '14','15','16','17'], #2 row ok
                        [munsell, '01', '02', '03', '04','05', munsell_surf, '07', '08', '09','10','11',surf_trat,'13', '14','15','16','17'], #2 row ok
                        [treatment, '01', '02', '03', '04','05',period, '07', '08', '09','10','11',state,'13', '14','15','16','17'], #2 row ok
                        [samples, '01', '02', '03', '04','05', photographed, '07', '08', '09','10','11',drawing,'13', '14','15',wheel_made,'17'], #2 row ok
                        [diametro_max, '01', '02', '03', '04','05', diametro_rim, '07', '08', '09','10','11',diametro_bottom,'13', '14','15','16','17'], #2 row ok
                        [total_height, '01', '02', '03', '04','05', preserved_height, '07', '08', '09','10','11',base_height,'13', '14','15','16','17'], #2 row ok
                        [thickmin, '01', '02', '03', '04','05',thickmax , '07', '08', '09','10','11',data_,'13', '14','15','16','17'], #2 row ok
                        [description, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #8 row ok
                       
                        ]
        #table style
        table_style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    #0 row
                    ('SPAN', (0,0),(1,0)),  #logo2
                    ('SPAN', (2,0),(15,0)),  #intestazione
                    ('SPAN', (16,0),(17,0)),  #logo
                    
                    ('SPAN', (0,1),(8,1)),  #sito
                    ('SPAN', (9,1),(17,1)),#divelogid
                    
                    ('SPAN', (0,2),(5,2)),  #diver1
                    ('SPAN', (6,2),(11,2)),  #date_
                    ('SPAN', (12,2),(17,2)),  #area_id
                    
                    ('SPAN', (0,3),(5,3)),  #diver2
                    ('SPAN', (6,3),(11,3)),  #date_
                    ('SPAN', (12,3),(17,3)),  #area_id
                    
                    ('SPAN', (0,4),(5,4)),  #diver2
                    ('SPAN', (6,4),(11,4)),  #date_
                    ('SPAN', (12,4),(17,4)),  #area_id
                    
                    ('SPAN', (0,5),(5,5)),  #diver2
                    ('SPAN', (6,5),(11,5)),  #date_
                    ('SPAN', (12,5),(17,5)),  #area_id
                    
                    ('SPAN', (0,6),(5,6)),  #diver2
                    ('SPAN', (6,6),(11,6)),  #date_
                    ('SPAN', (12,6),(17,6)),  #area_id
                    
                    ('SPAN', (0,7),(5,7)),  #diver2
                    ('SPAN', (6,7),(11,7)),  #date_
                    ('SPAN', (12,7),(17,7)),  #area_id
                    
                    ('SPAN', (0,8),(5,8)),  #diver2
                    ('SPAN', (6,8),(11,8)),  #date_
                    ('SPAN', (12,8),(15,8)),  #area_id
                    ('SPAN', (16,8),(17,8)),  #area_id
                    
                    ('SPAN', (0,9),(5,9)),  #diver2
                    ('SPAN', (6,9),(11,9)),  #date_
                    ('SPAN', (12,9),(17,9)),  #area_id
                    
                    ('SPAN', (0,10),(5,10)),  #diver2
                    ('SPAN', (6,10),(11,10)),  #date_
                    ('SPAN', (12,10),(17,10)),  #area_id
                    
                    ('SPAN', (0,11),(5,11)),  #diver2
                    ('SPAN', (6,11),(11,11)),  #date_
                    ('SPAN', (12,11),(17,11)),  #area_id
                    
                    ('SPAN', (0,12),(17,12)),  #standby
                    ]
        colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30)
        rowHeights = None
        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
        return t
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles


class FOTO_index_pdf_sheet_2(object):
    """PDF sheet for pottery list WITH thumbnail"""

    def __init__(self, data):
        self.sito = data[0]
        self.id_number = data[5]
        self.area = data[1]
        self.us = data[2]
        self.sector = data[3]
        self.anno = data[4]
        self.description = data[6]
        self.foto = data[7]
        self.thumbnail = data[8]
        self.photo = data[9] if len(data) > 9 else ''
        self.drawing = data[10] if len(data) > 10 else ''

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 6

        # Style for wordwrap on photo and drawing
        styWrap = ParagraphStyle('wrap', parent=styNormal, wordWrap='CJK', fontSize=5)

        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        id_number = Paragraph("<b>Pottery ID</b><br/>" + str(self.id_number), styNormal)
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>SU</b><br/>" + str(self.us), styNormal)
        sector = Paragraph("<b>Sector</b><br/>" + str(self.sector), styNormal)
        foto = Paragraph("<b>Photo ID</b><br/>" + str(self.foto), styNormal)
        decription = Paragraph("<b>Note</b><br/>" + str(self.description), styNormal)
        anno = Paragraph("<b>Year</b><br/>" + str(self.anno), styNormal)

        # Photo and Drawing with wordwrap
        photo_text = str(self.photo).replace('; ', '<br/>') if self.photo else ''
        drawing_text = str(self.drawing).replace('; ', '<br/>') if self.drawing else ''
        photo = Paragraph("<b>Photo</b><br/>" + photo_text, styWrap)
        drawing = Paragraph("<b>Drawing</b><br/>" + drawing_text, styWrap)

        logo = Image(self.thumbnail)
        logo.drawHeight = 0.8 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 0.8 * inch
        logo.hAlign = "CENTER"

        thumbnail = logo
        data = [
            id_number,
            area,
            us,
            sector,
            anno,
            decription,
            foto,
            photo,
            drawing,
            thumbnail
        ]

        return data
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles
class FOTO_index_pdf_sheet(object):
    """PDF sheet for pottery list WITHOUT thumbnail"""

    def __init__(self, data):
        self.sito = data[0]
        self.id_number = data[5]
        self.area = data[1]
        self.us = data[2]
        self.sector = data[3]
        self.anno = data[4]
        self.description = data[6]
        self.foto = data[7]
        self.photo = data[9] if len(data) > 9 else ''
        self.drawing = data[10] if len(data) > 10 else ''

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 6

        # Style for wordwrap on photo and drawing
        styWrap = ParagraphStyle('wrap', parent=styNormal, wordWrap='CJK', fontSize=5)

        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        id_number = Paragraph("<b>Pottery ID</b><br/>" + str(self.id_number), styNormal)
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>SU</b><br/>" + str(self.us), styNormal)
        sector = Paragraph("<b>Sector</b><br/>" + str(self.sector), styNormal)
        foto = Paragraph("<b>Photo ID</b><br/>" + str(self.foto), styNormal)
        description = Paragraph("<b>Note</b><br/>" + str(self.description), styNormal)
        anno = Paragraph("<b>Year</b><br/>" + str(self.anno), styNormal)

        # Photo and Drawing with wordwrap
        photo_text = str(self.photo).replace('; ', '<br/>') if self.photo else ''
        drawing_text = str(self.drawing).replace('; ', '<br/>') if self.drawing else ''
        photo = Paragraph("<b>Photo</b><br/>" + photo_text, styWrap)
        drawing = Paragraph("<b>Drawing</b><br/>" + drawing_text, styWrap)

        data = [
                id_number,
                area,
                us,
                sector,
                anno,
                description,
                foto,
                photo,
                drawing
                ]

        return data
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles    
class POTTERY_index_pdf:
    def __init__(self, data):
        self.divelog_id =                               data[0]
        self.artefact_id =                          data[1]
        self.anno =                 data[2]
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0 #LEFT
        styNormal.fontSize = 8
        #self.unzip_rapporti_stratigrafici()
        divelog_id = Paragraph("<b>Pottery ID</b><br/>" + str(self.id_number),styNormal)
        artefact_id = Paragraph("<b>Note</b><br/>" + str(self.note),styNormal)
        anno = Paragraph("<b>Year</b><br/>" + str(self.anno),styNormal)
        data1 = [divelog_id,
                artefact_id,
                anno]
        return data1
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles
class generate_POTTERY_pdf:
    HOME = os.environ['PYARCHINIT_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def build_POTTERY_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_POTTERY_sheet = single_pottery_pdf_sheet(records[i])
            elements.append(single_POTTERY_sheet.create_sheet())
            elements.append(PageBreak())
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Pottery.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)
        f.close()
    def build_index_POTTERY(self, records, divelog_id):
        HOME = os.environ['PYARCHINIT_HOME']
        PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
        home_DB_path = '{}{}{}'.format(HOME, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)
        ##      if test_image.drawWidth < 800:
        logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5*inch
        # logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo2.png')
        # logo2 = Image(logo_path2)
        # ##      if test_image.drawWidth < 800:
        # logo2.drawHeight = 0.5*inch*logo2.drawHeight / logo2.drawWidth
        # logo2.drawWidth = 0.5*inch
        # #1 row
        logo.hAlign = "LEFT"
        # logo2.hAlign = "CENTER"
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']
        data = self.datestrfdate()
        lst = []
        lst.append(logo)
        lst.append(Paragraph("<b>Pottery</b><br/><b>Date: %s</b>" % (data), styH1))
        table_data1 = []
        for i in range(len(records)):
            exp_index = POTTERY_index_pdf(records[i])
            table_data1.append(exp_index.getTable())
        styles = exp_index.makeStyles()
        colWidths=[42,60,45,45,45,58,45,58,55,64,64,52,52,65]
        table_data1_formatted = Table(table_data1, colWidths, style=styles)
        table_data1_formatted.hAlign = "LEFT"
        lst.append(table_data1_formatted)
        lst.append(Spacer(0,2))
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Pottery_list.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=(29*cm, 21*cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)
        f.close()
    def build_index_Foto_2(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>List Photo Pottery</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet_2(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        # 10 columns: id_number, area, us, sector, anno, description, foto, photo, drawing, thumbnail
        colWidths = [30, 30, 30, 30, 30, 70, 30, 65, 65, 80]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'List photo thumbnail pottery', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    def build_index_Foto(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>List photo pottery</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        # 9 columns: id_number, area, us, sector, anno, description, foto, photo, drawing
        colWidths = [35, 35, 35, 35, 35, 100, 35, 80, 80]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'List photo pottery', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()