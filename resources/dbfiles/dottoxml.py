#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2021-12-01
    copyright            : Enzo Cocca <enzo.ccc@gmail.com>

 ***************************************************************************/
/***************************************************************************
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""
import random
import sys
import locale
import optparse
import dot
import xml.dom.minidom as F
from xml.dom.minidom import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QInputDialog, QApplication
# Usage message
usgmsg = "Usage: dottoxml.py [options] infile.dot outfile.graphml"

def usage():
    print("dottoxml 1.6, 2014-04-10, Dirk Baechle\n")
    print(usgmsg)
    print("Hint: Try '-h' or '--help' for further infos!")

def exportDot(o, nodes, edges, options):
    o.write("graph [\n")

    for k,nod in nodes.items():
        nod.exportDot(o,options)
    for el in edges:
        el.exportDot(o,nodes,options)

def exportGML(o, nodes, edges, options):
    o.write("graph [\n")
    o.write("  comment \"Created by dottoxml.py\"\n")
    o.write("  directed 1\n")
    o.write("  hierarchic 1\n")

    for k,nod in nodes.items():
        nod.exportGML(o,options)
    for el in edges:
        el.exportGML(o,nodes,options)

    o.write("]\n")

def intes():
    try: 
        dialog = QInputDialog()
        dialog.resize(QtCore.QSize(700, 100))
        ID_Sito = dialog.getText(None, 'Intestazione', "Aggiungi una intestazione al tuo diagramma stratigrafico")
        Sito = str(ID_Sito[0])
        return Sito
    except KeyError as e:
        print(str(e))
def reverse():
    '''return true or false about the order epoch  '''
    try: 
        dialog = QInputDialog()
        dialog.resize(QtCore.QSize(700, 100))
        ID_rev = dialog.getText(None, 'Ordinamento', "Scrivi true se il Periodo 1 corrisponde all'utima epoca scavata.\n Altrimeti lascia vuoto e clicca 'ok'")
        rev = str(ID_rev[0])
        if rev=='true':
            return 1
        else:
            return 0
    except KeyError as e:
        print(str(e))

def exportGraphml(o, nodes, edges, options,ff=0):    
    tf=reverse()
    ints=intes()
    doc = F.Document()
    root = doc.createElement('graphml')
    root.setAttribute('xmlns','http://graphml.graphdrawing.org/xmlns')
    root.setAttribute('xmlns:java','http://www.yworks.com/xml/yfiles-common/1.0/java')
    root.setAttribute('xmlns:sys','http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0')
    root.setAttribute('xmlns:x','http://www.yworks.com/xml/yfiles-common/markup/2.0')
    root.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xmlns:y','http://www.yworks.com/xml/graphml')
    root.setAttribute('xmlns:yed','http://www.yworks.com/xml/yed/3')
    root.setAttribute('xsi:schemaLocation','http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd')
    doc.appendChild(root)        
    
    key = doc.createElement('key')
    key.setAttribute('attr.name','Description') 
    key.setAttribute('for','graph')    
    key.setAttribute('attr.type','string')
    key.setAttribute('id','d0')    
    root.appendChild(key)
    
    key = doc.createElement('key')
    key.setAttribute('for','port')    
    key.setAttribute('id','d1')    
    key.setAttribute('yfiles.type','portgraphics')    
    root.appendChild(key)
    
    key = doc.createElement('key')
    key.setAttribute('for','port')    
    key.setAttribute('id','d2')    
    key.setAttribute('yfiles.type','portgeometry')    
    root.appendChild(key)
    
    key = doc.createElement('key')
    key.setAttribute('for','port')    
    key.setAttribute('id','d3')    
    key.setAttribute('yfiles.type','portuserdata')    
    root.appendChild(key)
   
    key = doc.createElement('key')
    key.setAttribute('attr.name','url')    
    key.setAttribute('attr.type','string')    
    key.setAttribute('for','node')    
    key.setAttribute('id','d4')    
    root.appendChild(key)
        
    key = doc.createElement('key')
    key.setAttribute('attr.name','description')    
    key.setAttribute('attr.type','string')    
    key.setAttribute('for','node')    
    key.setAttribute('id','d5')    
    root.appendChild(key) 
        
    key = doc.createElement('key')
    key.setAttribute('for','node')    
    key.setAttribute('id','d6')    
    key.setAttribute('yfiles.type','nodegraphics')    
    root.appendChild(key)

    key = doc.createElement('key')
    key.setAttribute('for','graphml')    
    key.setAttribute('id','d7') 
    #key.setAttribute('yfiles.folder','group')
    key.setAttribute('yfiles.type','resources')    
    root.appendChild(key)
    
    key = doc.createElement('key')
    key.setAttribute('attr.name','url')    
    key.setAttribute('attr.type','string')    
    key.setAttribute('for','edge')    
    key.setAttribute('id','d8')    
    root.appendChild(key)

    key = doc.createElement('key')
    key.setAttribute('attr.name','description')    
    key.setAttribute('attr.type','string')    
    key.setAttribute('for','edge')    
    key.setAttribute('id','d9')    
    root.appendChild(key)

    key = doc.createElement('key')
    key.setAttribute('for','edge')    
    key.setAttribute('id','d10')    
    key.setAttribute('yfiles.type','edgegraphics')    
    root.appendChild(key)
    
    
    
    
    graph = doc.createElement('graph')
    graph.setAttribute('edgedefault','directed')    
    graph.setAttribute('id','G') 
    data01 = doc.createElement('data')
    data01.setAttribute('key', 'd0')
    data01.setAttribute('xml:space','preserve')    
    graph.appendChild(data01)
    
    
    
    node1 = doc.createElement('node')        
    node1.setAttribute('id','n0')
    node1.setAttribute('yfiles.foldertype','group')    
    #LabelText = self.getLabel(conf, True)
    data1 = doc.createElement('data')
    data1.setAttribute('key', 'd5')
    data1.setAttribute('xml:space','preserve')
    data1.appendChild(doc.createTextNode('Stratigrafia'))  
    node1.appendChild(data1)    
    data0 = doc.createElement('data')
    data0.setAttribute('key', 'd6')    
    tablenode= doc.createElement('y:TableNode')
    tablenode.setAttribute('configuration','YED_TABLE_NODE')
    geom = doc.createElement('y:Geometry')
    geom.setAttribute('height','10000.86965344368')
    geom.setAttribute('width','1044.0')
    geom.setAttribute('x','-29.0')
    geom.setAttribute('y','-596.1141011840689')
    tablenode.appendChild(geom)
    
    fill = doc.createElement('y:Fill')
    fill.setAttribute('color','#ecf5ff')
    fill.setAttribute('color2','#0042F440')
    fill.setAttribute('transparent','false')
    tablenode.appendChild(fill)
    
    border = doc.createElement('y:BorderStyle')
    border.setAttribute('hascolor','false')
    border.setAttribute('type','line')
    border.setAttribute('width','1.0')
    tablenode.appendChild(border)
    label01 = doc.createElement('y:NodeLabel')
    label01.setAttribute('alignment','center')
    label01.setAttribute('autoSizePolicy','content')
    label01.setAttribute('fontFamily','DialogInputInput')
    label01.setAttribute('fontSize','24')
    label01.setAttribute('fontStyle','bold')
    label01.setAttribute('hasBackgroundColor','false')
    label01.setAttribute('hasLineColor','false')
    label01.setAttribute('height','22.37646484375')
    label01.setAttribute('horizontalTextPosition','center')
    label01.setAttribute('iconTextGap','4')
    label01.setAttribute('modelName','internal')        
    label01.setAttribute('modelPosition','t')
    label01.setAttribute('textColor','#000000')
    label01.setAttribute('verticalTextPosition','bottom')
    label01.setAttribute('visible','true')    
    label01.setAttribute('width','134.9130859375')
    label01.setAttribute('x','454.54345703125')
    label01.setAttribute('xml:space','preserve')
    label01.setAttribute('y','0.0')
    nodelabel01Text = '{}'.format(ints)
    label01.appendChild(doc.createTextNode(nodelabel01Text))        
    tablenode.appendChild(label01)
    n = dot.Node()
    # for s in nodes:
        # n.label
    # if not 'US' in s:
        # s
    x=700
    w=200
    epoch=[]
    epoch_sigla = []
    area=[]
    area_sigla=[]
    per_area=[]
    for i in sorted(nodes):
        if i.startswith('Periodo') or i.startswith('Period'):
            epoch.append(i)
        if i.startswith('Area'):
            area.append(i)
        elif i.startswith('US') or i.startswith('SU') or i.startswith('WSU'):
            singola_epoca,area_singola = i.rsplit('_',1)
            #print(area_singola)
            descrizione_us, singola_epoca = i.rsplit('_',1)
            #print(singola_epoca)
            nome_us, descrizione_us= descrizione_us.split('_',1)
            print(f"La US {nome_us}, {descrizione_us}, appartiene all'epoca {singola_epoca}, dell'area {area_singola}")
            if singola_epoca not in epoch_sigla:
                epoch_sigla.append(singola_epoca)
            
    #print(epoch_sigla)
    
    
    for i in sorted(epoch, reverse=tf):
        color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        s=i.split(' : ')
        a=len(i)
        a=x/a*100
        b=w/a*100
        label02 = doc.createElement('y:NodeLabel')
        label02.setAttribute('alignment','center')
        label02.setAttribute('autoSizePolicy','content')
        label02.setAttribute('fontFamily','DialogInput')
        label02.setAttribute('fontSize','24')
        label02.setAttribute('fontStyle','bold')
        label02.setAttribute('backgroundColor','{}'.format(color))
        label02.setAttribute('hasLineColor','false')
        label02.setAttribute('height','18.701171875')
        label02.setAttribute('horizontalTextPosition','center')
        label02.setAttribute('iconTextGap','4')
        label02.setAttribute('modelName','custom')        
        label02.setAttribute('rotationAngle','270.0')
        label02.setAttribute('textColor','#000000')
        label02.setAttribute('verticalTextPosition','bottom')
        label02.setAttribute('visible','true')    
        label02.setAttribute('width','%r'%b)
        label02.setAttribute('x','3.0')
        label02.setAttribute('xml:space','preserve')
        label02.setAttribute('y','%r'%a)
        nodelabel02Text = '%s'%s[-1]
        label02.appendChild(doc.createTextNode(nodelabel02Text)) 
        labelz = doc.createElement('y:LabelModel')
        labelz1 = doc.createElement('y:RowNodeLabelModel')
        labelz1.setAttribute('offset','3.0')
        labelz.appendChild(labelz1)
        labelz2 = doc.createElement('y:ModelParameter')
        labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
        labelz3.setAttribute('horizontalPosition','0.0')
        labelz3.setAttribute('id','row_%s'%s[-1].replace(' ','_'))
        labelz3.setAttribute('inside','true')
        
        labelz2.appendChild(labelz3)
        label02.appendChild(labelz)    
        label02.appendChild(labelz2)    
        tablenode.appendChild(label02)
    
    for i in sorted(area):
        color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        s=i.split(' : ')
        a=len(i)
        a=x/a*100
        b=w/a*100
        label02 = doc.createElement('y:NodeLabel')
        label02.setAttribute('alignment','center')
        label02.setAttribute('autoSizePolicy','content')
        label02.setAttribute('fontFamily','DialogInput')
        label02.setAttribute('fontSize','30')
        label02.setAttribute('fontStyle','bold')
        label02.setAttribute('backgroundColor','{}'.format(color))
        label02.setAttribute('hasLineColor','false')
        label02.setAttribute('height','43.169921875')
        label02.setAttribute('horizontalTextPosition','center')
        label02.setAttribute('iconTextGap','4')
        label02.setAttribute('modelName','custom')        
        label02.setAttribute('textColor','#000000')
        label02.setAttribute('verticalTextPosition','bottom')
        label02.setAttribute('visible','true')    
        label02.setAttribute('width','%r'%b)
        label02.setAttribute('x','%r'%a)
        label02.setAttribute('xml:space','preserve')
        label02.setAttribute('y','93.0')
        nodelabel02Text = '%s'%s[-1]
        label02.appendChild(doc.createTextNode(nodelabel02Text)) 
        labelz = doc.createElement('y:LabelModel')
        labelz1 = doc.createElement('y:ColumnNodeLabelModel')
        labelz1.setAttribute('offset','3.0')
        labelz.appendChild(labelz1)
        labelz2 = doc.createElement('y:ModelParameter')
        labelz3 = doc.createElement('y:ColumnNodeLabelModelParameter')
        labelz3.setAttribute('id','column_%s'%s[-1].replace(' ','_'))
        labelz3.setAttribute('inside','true')
        labelz3.setAttribute('verticalPosition','0.0')
        labelz2.appendChild(labelz3)
        label02.appendChild(labelz)    
        label02.appendChild(labelz2)    
        tablenode.appendChild(label02)
    propertyStyle=doc.createElement('y:StyleProperties')
    
    property1=doc.createElement('y:Property')
    property1.setAttribute('name','y.view.tabular.TableNodePainter.ALTERNATE_COLUMN_SELECTION_STYLE')
    simplestyle1=doc.createElement('y:SimpleStyle')
    simplestyle1.setAttribute('fillColor','#474A4340')
    simplestyle1.setAttribute('lineColor','#000000')
    simplestyle1.setAttribute('lineType','line')
    simplestyle1.setAttribute('lineWidth','3.0')
    property1.appendChild(simplestyle1)
    
    propertyStyle.appendChild(property1)
    
    property2=doc.createElement('y:Property')
    property2.setAttribute('name','y.view.tabular.TableNodePainter.ALTERNATE_ROW_SELECTION_STYLE')
    simplestyle2=doc.createElement('y:SimpleStyle')
    simplestyle2.setAttribute('fillColor','#474A4340')
    simplestyle2.setAttribute('lineColor','#000000')
    simplestyle2.setAttribute('lineType','line')
    simplestyle2.setAttribute('lineWidth','3.0')
    property2.appendChild(simplestyle2)
    
    propertyStyle.appendChild(property2)
    
    property5=doc.createElement('y:Property')
    property5.setAttribute('class','java.lang.Integer')
    property5.setAttribute('name','yed.table.header.font.size')
    property5.setAttribute('value','12')
    
    propertyStyle.appendChild(property5)
    
    property3=doc.createElement('y:Property')
    property3.setAttribute('class','java.awt.Color')
    property3.setAttribute('name','yed.table.lane.color.main')
    property3.setAttribute('value','#c4d7ed')
    
    propertyStyle.appendChild(property3)
    
    property3=doc.createElement('y:Property')
    property3.setAttribute('class','java.awt.Color')
    property3.setAttribute('name','yed.table.lane.color.alternating')
    property3.setAttribute('value','#abc8e2')
    
    tablenode.appendChild(property3)
    
    property3=doc.createElement('y:Property')
    property3.setAttribute('class','java.awt.Color')
    property3.setAttribute('name','yed.table.lane.color.main')
    property3.setAttribute('value','#c4d7ed')
    
    propertyStyle.appendChild(property3)
    
    
    property=doc.createElement('y:Property')
    property.setAttribute('name','y.view.tabular.TableNodePainter.ALTERNATE_ROW_STYLE')
    simplestyle=doc.createElement('y:SimpleStyle')
    simplestyle.setAttribute('fillColor','#474A4340')
    simplestyle.setAttribute('lineColor','#000000')
    simplestyle.setAttribute('lineType','line')
    simplestyle.setAttribute('lineWidth','1.0')
    property.appendChild(simplestyle)
    
    propertyStyle.appendChild(property)
    
    property3=doc.createElement('y:Property')
    property3.setAttribute('class','java.awt.Color')
    property3.setAttribute('name','yed.table.section.color')
    property3.setAttribute('value','#7192b2')
    
    propertyStyle.appendChild(property3)
    
    property4=doc.createElement('y:Property')
    property4.setAttribute('class','java.lang.Double')
    property4.setAttribute('name','yed.table.header.height')
    property4.setAttribute('value','54.0')
    
    propertyStyle.appendChild(property4)
    
    property3=doc.createElement('y:Property')
    property3.setAttribute('class','java.awt.Color')
    property3.setAttribute('name','yed.table.header.color.alternating')
    property3.setAttribute('value','#abc8e2')
    
    propertyStyle.appendChild(property3)
    
    property9=doc.createElement('y:Property')
    property9.setAttribute('class','java.lang.String')
    property9.setAttribute('name','yed.table.lane.style')
    property9.setAttribute('value','lane.style.rows')
    
    propertyStyle.appendChild(property9)
    
    property11=doc.createElement('y:Property')
    property11.setAttribute('name','y.view.tabular.TableNodePainter.ALTERNATE_COLUMN_SELECTION_STYLE')
    simplestyle11=doc.createElement('y:SimpleStyle')
    simplestyle11.setAttribute('fillColor','#474A4340')
    simplestyle11.setAttribute('lineColor','#000000')
    simplestyle11.setAttribute('lineType','line')
    simplestyle11.setAttribute('lineWidth','1.0')
    property11.appendChild(simplestyle11)
    
    propertyStyle.appendChild(property11)
    
    
    #inserire per ultimo##############
    tablenode.appendChild(propertyStyle)
    
    
    state=doc.createElement('y:State')
    state.setAttribute('autoResize','true')
    state.setAttribute('closed','false')
    state.setAttribute('closedHeight','80.0')
    state.setAttribute('closedWidth','100.0')
    tablenode.appendChild(state)
    
    
    
    insets=doc.createElement('y:Insets')
    insets.setAttribute('bottom','0')
    insets.setAttribute('bottomF','0.0')
    insets.setAttribute('left','0')
    insets.setAttribute('leftF','0.0')
    insets.setAttribute('right','0')
    insets.setAttribute('rightF','0.0')
    insets.setAttribute('top','0')
    insets.setAttribute('topF','0.0')
    tablenode.appendChild(insets)
    
    
    borderinsets=doc.createElement('y:BorderInsets')
    borderinsets.setAttribute('bottom','62')
    borderinsets.setAttribute('bottomF','61.8')
    borderinsets.setAttribute('left','40')
    borderinsets.setAttribute('leftF','40.0')
    borderinsets.setAttribute('right','40')
    borderinsets.setAttribute('rightF','40.0')
    borderinsets.setAttribute('top','70')
    borderinsets.setAttribute('topF','71.0')
    tablenode.appendChild(borderinsets)
    
    table=doc.createElement('y:Table')
    table.setAttribute('autoResizeTable','true' )
    table.setAttribute('defaultColumnWidth','120.0')
    table.setAttribute('defaultMinimumColumnWidth','80.0')
    table.setAttribute('defaultMinimumRowHeight','50.0')
    table.setAttribute('defaultRowHeight','80.0')
    
    
    
    defaultcomment=doc.createElement('y:DefaultColumnInsets')
    defaultcomment.setAttribute('bottom','0.0')
    defaultcomment.setAttribute('left','0.0')
    defaultcomment.setAttribute('right','0.0')
    defaultcomment.setAttribute('top','0.0')
    table.appendChild(defaultcomment)
    
    defaultrowinsets=doc.createElement('y:DefaultRowInsets')
    defaultrowinsets.setAttribute('bottom','0.0')
    defaultrowinsets.setAttribute('left','54.0')
    defaultrowinsets.setAttribute('right','0.0')
    defaultrowinsets.setAttribute('top','0.0')
    table.appendChild(defaultrowinsets)
    
    
    
    
    insets=doc.createElement('y:Insets')
    insets.setAttribute('bottom','0.0')
    insets.setAttribute('left','0.0')
    insets.setAttribute('right','0.0')
    insets.setAttribute('top','30.0')
    table.appendChild(insets)
    
    
    
    
    
    #n.initFromString(l)
    rows=doc.createElement('y:Rows')
    
    
    
    for i in sorted(epoch,reverse=tf):
        
        
        s=i.split(' : ')
        a=len(i)
        a=x/100*94
            
        row=doc.createElement('y:Row')
        
        row.setAttribute('height','%r'%a)
        
        row.setAttribute('id','row_%s' % s[-1].replace(' ','_'))
        row.setAttribute('minimumHeight','50.0')    
        insets3=doc.createElement('y:Insets')
        insets3.setAttribute('bottom','0.0')
        insets3.setAttribute('left','54.0')
        insets3.setAttribute('right','0.0')
        insets3.setAttribute('top','0.0')
        rows.appendChild(row)
        row.appendChild(insets3)   
        table.appendChild(rows)
    
    columns=doc.createElement('y:Columns')
    x=1000.0
    for i in sorted(area):
        s=i.split(':')
        a=len(i)
        a=x/100*94
        column=doc.createElement('y:Column')
        column.setAttribute('id','column_%s' % s[-1].replace(' ','_'))
        column.setAttribute('minimumWidth','80.0')
        column.setAttribute('width','1020.0')    
        insets2=doc.createElement('y:Insets')
        insets2.setAttribute('bottom','0.0')
        insets2.setAttribute('left','0.0')
        insets2.setAttribute('right','0.0')
        insets2.setAttribute('top','0.0')   
        columns.appendChild(column)
        column.appendChild(insets2)    
        table.appendChild(columns)
    
    
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    node1.appendChild(data0)
    
    graph1 = doc.createElement('graph')
    graph1.setAttribute('edgedefault','directed')    
    graph1.setAttribute('id','n0:')
    
    
    for k,nod in nodes.items():
        
        
        nod.exportGraphml(doc, graph1, options, sorted(area_sigla),sorted(epoch_sigla, reverse=tf))
        
    
    node1.appendChild(graph1)
   
    graph.appendChild(node1)
    
    for el in edges:
        el.exportGraphml(doc, graph, nodes, options)
    
    root.appendChild(graph)
    
    
    #######creo i simboli  svg per gli estrattori, i combinar e le continuity########
    data = doc.createElement('data')
    data.setAttribute('key','d7')    
    res = doc.createElement('y:Resources')
    
    res2 = doc.createElement('y:Resource')
    
    res2.setAttribute('id','1')
    res2.setAttribute('xml:space','preserve')
    
    res2.appendChild(doc.createTextNode('''

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="48px"
   height="48px"
   id="svg4050"
   version="1.1"
   inkscape:version="0.48.4 r9939"
   sodipodi:docname="New document 13">
 <defs
     id="defs4052" />
 <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="9.8994949"
     inkscape:cx="18.095997"
     inkscape:cy="17.278115"
     inkscape:current-layer="layer1"
     showgrid="true"
     inkscape:grid-bbox="true"
     inkscape:document-units="px"
     inkscape:window-width="1920"
     inkscape:window-height="1025"
     inkscape:window-x="-2"
     inkscape:window-y="-3"
     inkscape:window-maximized="1" />
 <metadata
     id="metadata4055">
   <rdf:RDF>
     <cc:Work
         rdf:about="">
       <dc:format>image/svg+xml</dc:format>
       <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
       <dc:title></dc:title>
     </cc:Work>
   </rdf:RDF>
 </metadata>
 <g
     id="layer1"
     inkscape:label="Layer 1"
     inkscape:groupmode="layer">
   <g
       transform="matrix(0.41470954,0,0,0.41438764,-58.075087,96.197996)"
       id="g3932">
     <path
         transform="translate(-176.7767,-1080.8632)"
         d="m 430.32499,906.90021 c 0,30.68405 -24.87434,55.55839 -55.55839,55.55839 -30.68405,0 -55.55839,-24.87434 -55.55839,-55.55839 0,-30.68405 24.87434,-55.55839 55.55839,-55.55839 30.68405,0 55.55839,24.87434 55.55839,55.55839 z"
         sodipodi:ry="55.558392"
         sodipodi:rx="55.558392"
         sodipodi:cy="906.90021"
         sodipodi:cx="374.7666"
         id="path2996-3"
         style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
         sodipodi:type="arc" />
     <path
         inkscape:connector-curvature="0"
         id="path3795"
         d="m 195.82737,-229.48049 c -29.75104,1.0602 -53.53125,25.52148 -53.53125,55.53125 0,30.00977 23.78021,54.4398 53.53125,55.5 l 0,-38.875 -18.1875,0 0,-32.8125 18.1875,0 0,-39.34375 z"
         style="fill:#7d7d7d;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
     <rect
         y="-187.49332"
         x="212.49696"
         height="27.142857"
         width="26.071428"
         id="rect3805"
         style="fill:#7d7d7d;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
     <path
         inkscape:connector-curvature="0"
         id="path3807"
         d="m 180.35416,-173.20759 c 29.28571,0 29.28571,0 29.28571,0"
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" />
   </g>
 </g>
</svg>'''))
    
    res.appendChild(res2)
    res3 = doc.createElement('y:Resource')
    #if 'Extractor' in node:
    res3.setAttribute('id','2')
    res3.setAttribute('xml:space','preserve')
    
    
    res3.appendChild(doc.createTextNode('''

<svg
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:cc="http://creativecommons.org/ns#"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:svg="http://www.w3.org/2000/svg"
xmlns="http://www.w3.org/2000/svg"
xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
width="48px"
height="48px"
id="svg4192"
version="1.1"
inkscape:version="0.48.4 r9939"
sodipodi:docname="New document 20">
<defs id="defs4194" />
<sodipodi:namedview
 id="base"
 pagecolor="#ffffff"
 bordercolor="#666666"
 borderopacity="1.0"
 inkscape:pageopacity="0.0"
 inkscape:pageshadow="2"
 inkscape:zoom="14"
 inkscape:cx="24.612064"
 inkscape:cy="28.768962"
 inkscape:current-layer="layer1"
 showgrid="true"
 inkscape:grid-bbox="true"
 inkscape:document-units="px"
 inkscape:window-width="1920"
 inkscape:window-height="1025"
 inkscape:window-x="-2"
 inkscape:window-y="-3"
 inkscape:window-maximized="1" />
<metadata id="metadata4197">
<rdf:RDF>
  <cc:Work
     rdf:about="">
    <dc:format>image/svg+xml</dc:format>
    <dc:type
       rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
    <dc:title></dc:title>
  </cc:Work>
</rdf:RDF>
</metadata>
<g 
 id="layer1"
 inkscape:label="Layer 1"
 inkscape:groupmode="layer">
<g
   transform="matrix(0.40828104,0,0,0.41346794,-201.56174,97.998396)"
   id="g3922">
  <path
     sodipodi:type="arc"
     style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
     id="path3912"
     sodipodi:cx="374.7666"
     sodipodi:cy="906.90021"
     sodipodi:rx="55.558392"
     sodipodi:ry="55.558392"
     d="m 430.32499,906.90021 c 0,30.68405 -24.87434,55.55839 -55.55839,55.55839 -30.68405,0 -55.55839,-24.87434 -55.55839,-55.55839 0,-30.68405 24.87434,-55.55839 55.55839,-55.55839 30.68405,0 55.55839,24.87434 55.55839,55.55839 z"
     transform="translate(177.55723,-1085.7479)" />
  <path
     sodipodi:nodetypes="ccsccc"
     inkscape:connector-curvature="0"
     id="path3914"
     d="m 543.53146,-169.98986 63.36579,-17.50001 c 0,0 0.71429,3.97312 0.71429,11.68875 0,7.71563 -2.93748,15.70661 -2.93748,15.70661 l -61.1426,17.05358 z"
     style="fill:#7b7b7b;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
  <path
     sodipodi:nodetypes="ccccsc"
     inkscape:connector-curvature="0"
     id="path3916"
     d="m 501.52478,-201.54471 54.88091,-14.27148 0,26.94893 -59.23348,15.97426 c 0,0 -0.15898,-6.266 0.10274,-12.48413 0.34368,-8.16509 4.24983,-16.16758 4.24983,-16.16758 z"
     style="fill:#7b7b7b;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
</g>
</g>
</svg> '''))
    res.appendChild(res3)
    res4 = doc.createElement('y:Resource')
    #if 'Extractor' in node:
    res4.setAttribute('id','3')
    res4.setAttribute('xml:space','preserve')
    
    
    res4.appendChild(doc.createTextNode('''

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="7mm"
   height="7mm"
   viewBox="0 0 7 7"
   version="1.1"
   id="svg8"
   inkscape:version="0.92.2 5c3e80d, 2017-08-06"
   sodipodi:docname="continuity.svg">
  <defs
     id="defs2" />
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="1.8181416"
     inkscape:cx="-10.002405"
     inkscape:cy="-64.860066"
     inkscape:document-units="mm"
     inkscape:current-layer="layer1"
     showgrid="false"
     fit-margin-top="0"
     fit-margin-left="0"
     fit-margin-right="0"
     fit-margin-bottom="0"
     inkscape:window-width="1440"
     inkscape:window-height="800"
     inkscape:window-x="0"
     inkscape:window-y="1"
     inkscape:window-maximized="1" />
  <metadata
     id="metadata5">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Livello 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-82.089519,-139.87478)">
    <rect
       id="rect12"
       width="4.9497476"
       height="4.9497476"
       x="159.42734"
       y="38.385479"
       style="stroke-width:0.01220008"
       transform="rotate(45)" />
  </g>
</svg> '''))
    res.appendChild(res4)
    data.appendChild(res)
    root.appendChild(data)
    
    o.write('{}'.format(doc.toxml(encoding='UTF-8').decode()))
    

    # parsed_xml = xml.dom.minidom.parseString(xml_string)
    # pretty_xml_as_string = parsed_xml.toprettyxml()

    # file = open("./content_new.xml", 'w')
    # o.write(xml_string)
    
def exportGDF(o, nodes, edges, options):
    o.write("nodedef> name\n")
    for k,nod in nodes.items():
        nod.exportGDF(o, options)
    for el in edges:
        el.exportGDF(o,nodes,options)
    o.write("edgedef> node1,node2\n")

def main():
    parser = optparse.OptionParser(usage=usgmsg)
    parser.add_option('-f', '--format',
                      action='store', dest='format', default='Graphml',
                      help='selects the output format (Graphml|GML|GDF) [default : %default]')
    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose', default=False,
                      help='enables messages (infos, warnings)')
    parser.add_option('-s', '--sweep',
                      action='store_true', dest='sweep', default=False,
                      help='sweep nodes (remove nodes that are not connected)')
    parser.add_option('--nn', '--no-nodes',
                      action='store_false', dest='NodeLabels', default=True,
                      help='do not output any node labels [Graphml]')
    parser.add_option('--ne', '--no-edges',
                      action='store_false', dest='EdgeLabels', default=True,
                      help='do not output any edge labels [Graphml]')
    parser.add_option('--nu', '--no-uml',
                      action='store_false', dest='NodeUml', default=True,
                      help='do not output any node methods/attributes in UML [Graphml]')
    parser.add_option('--na', '--no-arrows',
                      action='store_false', dest='Arrows', default=True,
                      help='do not output any arrows [Graphml]')
    parser.add_option('--nc', '--no-colors',
                      action='store_false', dest='Colors', default=True,
                      help='do not output any colors [Graphml]')
    parser.add_option('--la', '--lump-attributes',
                      action='store_true', dest='LumpAttributes', default=True,
                      help='lump class attributes/methods together with the node label [Graphml]')
    parser.add_option('--sc', '--separator-char',
                      action='store', dest='SepChar', default='_', metavar='SEPCHAR',
                      help='default separator char when lumping attributes/methods [default : "_"]')
    parser.add_option('--ae', '--auto-edges',
                      action='store_true', dest='EdgeLabelsAutoComplete', default=False,
                      help='auto-complete edge labels')
    parser.add_option('--ah', '--arrowhead',
                      action='store', dest='DefaultArrowHead', default='none', metavar='TYPE',
                      help='sets the default appearance of arrow heads for edges (normal|diamond|dot|...) [default : %default]')
    parser.add_option('--at', '--arrowtail',
                      action='store', dest='DefaultArrowTail', default='none', metavar='TYPE',
                      help='sets the default appearance of arrow tails for edges (normal|diamond|dot|...) [default : %default]')
    parser.add_option('--cn', '--color-nodes',
                      action='store', dest='DefaultNodeColor', default='#CCCCFF', metavar='COLOR',
                      help='default node color [default : "#CCCCFF"]')
    parser.add_option('--ce', '--color-edges',
                      action='store', dest='DefaultEdgeColor', default='#000000', metavar='COLOR',
                      help='default edge color [default : "#000000"]')
    parser.add_option('--cnt', '--color-nodes-text',
                      action='store', dest='DefaultNodeTextColor', default='#000000', metavar='COLOR',
                      help='default node text color for labels [default : "#000000"]')
    parser.add_option('--cet', '--color-edges-text',
                      action='store', dest='DefaultEdgeTextColor', default='#000000', metavar='COLOR',
                      help='default edge text color for labels [default : "#000000"]')
    parser.add_option('--ienc', '--input-encoding',
                      action='store', dest='InputEncoding', default='', metavar='ENCODING',
                      help='override encoding for input file [default : locale setting]')
    parser.add_option('--oenc', '--output-encoding',
                      action='store', dest='OutputEncoding', default='', metavar='ENCODING',
                      help='override encoding for text output files [default : locale setting]')

    options, args = parser.parse_args()
    
    if len(args) < 2:
        usage()
        sys.exit(1)

    infile = args[0]
    outfile = args[1]

    options.DefaultNodeColor = dot.colorNameToRgb(options.DefaultNodeColor, '#CCCCFF')
    options.DefaultEdgeColor = dot.colorNameToRgb(options.DefaultEdgeColor, '#000000')
    options.DefaultNodeTextColor = dot.colorNameToRgb(options.DefaultNodeTextColor, '#000000')
    options.DefaultEdgeTextColor = dot.colorNameToRgb(options.DefaultEdgeTextColor, '#000000')
    
    preferredEncoding = locale.getpreferredencoding()
    if options.InputEncoding == "":
        options.InputEncoding = preferredEncoding
    if options.OutputEncoding == "":
        options.OutputEncoding = preferredEncoding
    
    if options.verbose:
        print("Input file: %s " % infile)
        print("Output file: %s " % outfile)
        print("Output format: %s" % options.format.lower())
        print("Input encoding: %s" % options.InputEncoding)
        if options.format.lower() == "graphml":
            print("Output encoding: utf-8 (fix for Graphml)")
        else:
            print("Output encoding: %s" % options.OutputEncoding)

    # Collect nodes and edges
    nodes = {}
    edges = []
    default_edge = None
    default_node = None
    nid = 1
    eid = 1
    f = open(infile, 'r')
    content = f.read().splitlines()
    f.close()

    idx = 0
    while idx < len(content):
        l = '{}'.format(content[idx])
        if '->' in l:
            # Check for multiline edge
            if '[' in l and ']' not in l:
                ml = ""
                while ']' not in ml:
                    idx += 1
                    ml = '{}'.format(content[idx])
                    l = ' '.join([l.rstrip(), ml.lstrip()])
                    
            # Process edge
            e = dot.Edge()
            e.initFromString(l)
            e.id = eid
            eid += 1
            if default_edge:
                e.complementAttributes(default_edge)
            edges.append(e)
        elif '[' in l:
            # Check for multiline node
            if ']' not in l:
                ml = ""
                while ']' not in ml:
                    idx += 1
                    ml = '{}'.format(content[idx])
                    l = ' '.join([l.rstrip(), ml.lstrip()])
            # Process node
            n = dot.Node()
            n.initFromString(l)
            lowlabel = n.label.lower()
            if (lowlabel != 'graph' and
                lowlabel != 'subgraph' and
                lowlabel != 'edge' and
                lowlabel != 'node'):
                n.id = nid
                nid += 1
                if default_node:
                    n.complementAttributes(default_node)
                nodes[n.label] = n
            else:
                if lowlabel == 'edge':
                    default_edge = n
                elif lowlabel == 'node':
                    default_node = n   
        elif 'charset=' in l:
            # Pick up input encoding from DOT file
            li = l.strip().split('=')
            if len(li) == 2:
                ienc = li[1].strip('"')
                if ienc != "":
                    options.InputEncoding = ienc
                    if options.verbose:
                        print("Info: Picked up input encoding '%s' from the DOT file." % ienc)
        idx += 1
            
    #print(nodes)
    # Add single nodes, if required
    for e in edges:
        if e.src not in nodes:
            n = dot.Node()
            n.label = e.src
            n.id = nid
            nid += 1
            nodes[e.src] = n
        if e.dest not in nodes:
            n = dot.Node()
            n.label = e.dest
            n.id = nid
            nid += 1
            nodes[e.dest] = n
        nodes[e.src].referenced = True
        nodes[e.dest].referenced = True

    if options.verbose:
        print("\nNodes: %d " % len(nodes))
        print("Edges: %d " % len(edges))
    
    if options.sweep:
        rnodes = {}
        for key, n in nodes.items():
            if n.referenced:
                rnodes[key] = n
        nodes = rnodes
        if options.verbose:
            print("\nNodes after sweep: %d " % len(nodes))
    
    # Output
    o = open(outfile, 'w')
    format = options.format.lower()
    if format == 'dot':
        exportDot(o, nodes, edges, options)
    elif format == 'graphml':
        exportGraphml(o, nodes, edges, options)
    elif format == 'gdf':
        exportGDF(o, nodes, edges, options)
    else: # GML
        exportGML(o, nodes, edges, options)
    
    o.close()
    
    if options.verbose:
        print("\nDone.")

if __name__ == '__main__':
    app=QApplication(sys.argv)
    
    main()