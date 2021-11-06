# coding: utf-8
# Copyright (c) 2009,2010,2011,2012,2013,2014 Dirk Baechle.
# www: https://bitbucket.org/dirkbaechle/dottoxml
# mail: dl9obn AT darc.de
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""
  %dottoxml.py [options] <infile.dot> <outfile.graphml>
  convert a DOT file to Graphml XML (and various other formats)
"""

import sys
import locale
import optparse
import dot
import xml.dom.minidom as F
from xml.dom.minidom import *
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

def exportGraphml(o, nodes, edges, options,ff=0):
    
    doc = F.Document()
    root = doc.createElement('graphml')
    root.setAttribute('xmlns','http://graphml.graphdrawing.org/download.html')
    root.setAttribute('xmlns:java','http://www.yworks.com/xml/yfiles-common/1.0/java')
    root.setAttribute('xmlns:sys','http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0')
    root.setAttribute('xmlns:x','http://www.yworks.com/xml/yfiles-common/markup/2.0')
    root.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xmlns:y','http://www.yworks.com/xml/graphml')
    root.setAttribute('xmlns:yed','http://www.yworks.com/xml/yed/3')
    root.setAttribute('xsi:schemaLocation','http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.0/ygraphml.xsd')
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
    key.setAttribute('yfiles.folder','group')
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
    geom.setAttribute('height','4066.2706350074')
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
    label01.setAttribute('fontFamily','Dialog')
    label01.setAttribute('fontSize','12')
    label01.setAttribute('fontStyle','plain')
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
    label01.setAttribute('y','4.0')
    nodelabel01Text = 'Scavo archeologico'
    label01.appendChild(doc.createTextNode(nodelabel01Text))        
    tablenode.appendChild(label01)
    
    label02 = doc.createElement('y:NodeLabel')
    label02.setAttribute('alignment','center')
    label02.setAttribute('autoSizePolicy','content')
    label02.setAttribute('fontFamily','Dialog')
    label02.setAttribute('fontSize','12')
    label02.setAttribute('fontStyle','plain')
    label02.setAttribute('backgroundColor','#CCFFCC')
    label02.setAttribute('hasLineColor','false')
    label02.setAttribute('height','18.701171875')
    label02.setAttribute('horizontalTextPosition','center')
    label02.setAttribute('iconTextGap','4')
    label02.setAttribute('modelName','custom')        
    label02.setAttribute('rotationAngle','270.0')
    label02.setAttribute('textColor','#000000')
    label02.setAttribute('verticalTextPosition','bottom')
    label02.setAttribute('visible','true')    
    label02.setAttribute('width','74.998046875')
    label02.setAttribute('x','3.0')
    label02.setAttribute('xml:space','preserve')
    label02.setAttribute('y','492.7377903407562')
    nodelabel02Text = 'Età Moderna'
    label02.appendChild(doc.createTextNode(nodelabel02Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_0')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label02.appendChild(labelz)    
    label02.appendChild(labelz2)    
    tablenode.appendChild(label02)
    
    label03 = doc.createElement('y:NodeLabel')
    label03.setAttribute('alignment','center')
    label03.setAttribute('autoSizePolicy','content')
    label03.setAttribute('fontFamily','Dialog')
    label03.setAttribute('fontSize','12')
    label03.setAttribute('fontStyle','plain')
    label03.setAttribute('backgroundColor','#FF99CC')
    label03.setAttribute('hasLineColor','false')
    label03.setAttribute('height','18.701171875')
    label03.setAttribute('horizontalTextPosition','center')
    label03.setAttribute('iconTextGap','4')
    label03.setAttribute('modelName','custom')        
    label03.setAttribute('rotationAngle','270.0')
    label03.setAttribute('textColor','#000000')
    label03.setAttribute('verticalTextPosition','bottom')
    label03.setAttribute('visible','true')    
    label03.setAttribute('width','147.68359375')
    label03.setAttribute('x','3.0')
    label03.setAttribute('xml:space','preserve')
    label03.setAttribute('y','1088.6480275329657')
    nodelabel03Text = 'Prima metà del XVI secolo'
    label03.appendChild(doc.createTextNode(nodelabel03Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_1')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label03.appendChild(labelz)    
    label03.appendChild(labelz2)    
    tablenode.appendChild(label03)
    
    label04 = doc.createElement('y:NodeLabel')
    label04.setAttribute('alignment','center')
    label04.setAttribute('autoSizePolicy','content')
    label04.setAttribute('fontFamily','Dialog')
    label04.setAttribute('fontSize','12')
    label04.setAttribute('fontStyle','plain')
    label04.setAttribute('backgroundColor','#ccffff')
    label04.setAttribute('hasLineColor','false')
    label04.setAttribute('height','18.701171875')
    label04.setAttribute('horizontalTextPosition','center')
    label04.setAttribute('iconTextGap','4')
    label04.setAttribute('modelName','custom')        
    label04.setAttribute('rotationAngle','270.0')
    label04.setAttribute('textColor','#000000')
    label04.setAttribute('verticalTextPosition','bottom')
    label04.setAttribute('visible','true')    
    label04.setAttribute('width','111.02734375')
    label04.setAttribute('x','3.0')
    label04.setAttribute('xml:space','preserve')
    label04.setAttribute('y','145.67039701628096')
    nodelabel04Text = 'Età contemporanea'
    label04.appendChild(doc.createTextNode(nodelabel04Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_2')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label04.appendChild(labelz)    
    label04.appendChild(labelz2)    
    tablenode.appendChild(label04)
    
    label05 = doc.createElement('y:NodeLabel')
    label05.setAttribute('alignment','center')
    label05.setAttribute('autoSizePolicy','content')
    label05.setAttribute('fontFamily','Dialog')
    label05.setAttribute('fontSize','12')
    label05.setAttribute('fontStyle','plain')
    label05.setAttribute('backgroundColor','#800080')
    label05.setAttribute('hasLineColor','false')
    label05.setAttribute('height','18.701171875')
    label05.setAttribute('horizontalTextPosition','center')
    label05.setAttribute('iconTextGap','4')
    label05.setAttribute('modelName','custom')        
    label05.setAttribute('rotationAngle','270.0')
    label05.setAttribute('textColor','#000000')
    label05.setAttribute('verticalTextPosition','bottom')
    label05.setAttribute('visible','true')    
    label05.setAttribute('width','58.029296875')
    label05.setAttribute('x','3.0')
    label05.setAttribute('xml:space','preserve')
    label05.setAttribute('y','1661.1393309758478')
    nodelabel05Text = 'XV secolo'
    label05.appendChild(doc.createTextNode(nodelabel05Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_3')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label05.appendChild(labelz)    
    label05.appendChild(labelz2)    
    tablenode.appendChild(label05)
    
    
    label06 = doc.createElement('y:NodeLabel')
    label06.setAttribute('alignment','center')
    label06.setAttribute('autoSizePolicy','content')
    label06.setAttribute('fontFamily','Dialog')
    label06.setAttribute('fontSize','12')
    label06.setAttribute('fontStyle','plain')
    label06.setAttribute('backgroundColor','#CC99FF')
    label06.setAttribute('hasLineColor','false')
    label06.setAttribute('height','18.701171875')
    label06.setAttribute('horizontalTextPosition','center')
    label06.setAttribute('iconTextGap','4')
    label06.setAttribute('modelName','custom')        
    label06.setAttribute('rotationAngle','270.0')
    label06.setAttribute('textColor','#000000')
    label06.setAttribute('verticalTextPosition','bottom')
    label06.setAttribute('visible','true')    
    label06.setAttribute('width','184.076171875')
    label06.setAttribute('x','3.0')
    label06.setAttribute('xml:space','preserve')
    label06.setAttribute('y','750.0717095415097')
    nodelabel06Text = 'Fine XVI secolo - Inizi XVII secolo'
    label06.appendChild(doc.createTextNode(nodelabel06Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_4')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label06.appendChild(labelz)    
    label06.appendChild(labelz2)    
    tablenode.appendChild(label06)
    
    label07 = doc.createElement('y:NodeLabel')
    label07.setAttribute('alignment','center')
    label07.setAttribute('autoSizePolicy','content')
    label07.setAttribute('fontFamily','Dialog')
    label07.setAttribute('fontSize','12')
    label07.setAttribute('fontStyle','plain')
    label07.setAttribute('backgroundColor','#FFFF99')
    label07.setAttribute('hasLineColor','false')
    label07.setAttribute('height','18.701171875')
    label07.setAttribute('horizontalTextPosition','center')
    label07.setAttribute('iconTextGap','4')
    label07.setAttribute('modelName','custom')        
    label07.setAttribute('rotationAngle','270.0')
    label07.setAttribute('textColor','#000000')
    label07.setAttribute('verticalTextPosition','bottom')
    label07.setAttribute('visible','true')    
    label07.setAttribute('width','144.349609375')
    label07.setAttribute('x','3.0')
    label07.setAttribute('xml:space','preserve')
    label07.setAttribute('y','2177.7011540046424')
    nodelabel07Text = 'Prima metà del XV secolo'
    label07.appendChild(doc.createTextNode(nodelabel07Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_5')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label07.appendChild(labelz)    
    label07.appendChild(labelz2)    
    tablenode.appendChild(label07)
    
    label08 = doc.createElement('y:NodeLabel')
    label08.setAttribute('alignment','center')
    label08.setAttribute('autoSizePolicy','content')
    label08.setAttribute('fontFamily','Dialog')
    label08.setAttribute('fontSize','12')
    label08.setAttribute('fontStyle','plain')
    label08.setAttribute('backgroundColor','#FFCC7F')
    label08.setAttribute('hasLineColor','false')
    label08.setAttribute('height','18.701171875')
    label08.setAttribute('horizontalTextPosition','center')
    label08.setAttribute('iconTextGap','4')
    label08.setAttribute('modelName','custom')        
    label08.setAttribute('rotationAngle','270.0')
    label08.setAttribute('textColor','#000000')
    label08.setAttribute('verticalTextPosition','bottom')
    label08.setAttribute('visible','true')    
    label08.setAttribute('width','82.703125')
    label08.setAttribute('x','3.0')
    label08.setAttribute('xml:space','preserve')
    label08.setAttribute('y','2581.749149581203')
    nodelabel08Text = 'Inizi XV secolo'
    label08.appendChild(doc.createTextNode(nodelabel08Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_6')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label08.appendChild(labelz)    
    label08.appendChild(labelz2)    
    tablenode.appendChild(label08)
    
    label09 = doc.createElement('y:NodeLabel')
    label09.setAttribute('alignment','center')
    label09.setAttribute('autoSizePolicy','content')
    label09.setAttribute('fontFamily','Dialog')
    label09.setAttribute('fontSize','12')
    label09.setAttribute('fontStyle','plain')
    label09.setAttribute('backgroundColor','#CCFFFF')
    label09.setAttribute('hasLineColor','false')
    label09.setAttribute('height','18.701171875')
    label09.setAttribute('horizontalTextPosition','center')
    label09.setAttribute('iconTextGap','4')
    label09.setAttribute('modelName','custom')        
    label09.setAttribute('rotationAngle','270.0')
    label09.setAttribute('textColor','#000000')
    label09.setAttribute('verticalTextPosition','bottom')
    label09.setAttribute('visible','true')    
    label09.setAttribute('width','88.041015625')
    label09.setAttribute('x','3.0')
    label09.setAttribute('xml:space','preserve')
    label09.setAttribute('y','2991.9117256879044')
    nodelabel09Text = 'Fine XIV secolo'
    label09.appendChild(doc.createTextNode(nodelabel09Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_7')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label09.appendChild(labelz)    
    label09.appendChild(labelz2)    
    tablenode.appendChild(label09)
    
    label00 = doc.createElement('y:NodeLabel')
    label00.setAttribute('alignment','center')
    label00.setAttribute('autoSizePolicy','content')
    label00.setAttribute('fontFamily','Dialog')
    label00.setAttribute('fontSize','12')
    label00.setAttribute('fontStyle','plain')
    label00.setAttribute('backgroundColor','#C0C0C0')
    label00.setAttribute('hasLineColor','false')
    label00.setAttribute('height','18.701171875')
    label00.setAttribute('horizontalTextPosition','center')
    label00.setAttribute('iconTextGap','4')
    label00.setAttribute('modelName','custom')        
    label00.setAttribute('rotationAngle','270.0')
    label00.setAttribute('textColor','#000000')
    label00.setAttribute('verticalTextPosition','bottom')
    label00.setAttribute('visible','true')    
    label00.setAttribute('width','163.720703125')
    label00.setAttribute('x','3.0')
    label00.setAttribute('xml:space','preserve')
    label00.setAttribute('y','3399.0268433799793')
    nodelabel00Text = 'Seconda metà del XIV secolo'
    label00.appendChild(doc.createTextNode(nodelabel00Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_8')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label00.appendChild(labelz)    
    label00.appendChild(labelz2)    
    tablenode.appendChild(label00)
    
    label001 = doc.createElement('y:NodeLabel')
    label001.setAttribute('alignment','center')
    label001.setAttribute('autoSizePolicy','content')
    label001.setAttribute('fontFamily','Dialog')
    label001.setAttribute('fontSize','12')
    label001.setAttribute('fontStyle','plain')
    label001.setAttribute('backgroundColor','#FF9900')
    label001.setAttribute('hasLineColor','false')
    label001.setAttribute('height','18.701171875')
    label001.setAttribute('horizontalTextPosition','center')
    label001.setAttribute('iconTextGap','4')
    label001.setAttribute('modelName','custom')        
    label001.setAttribute('rotationAngle','270.0')
    label001.setAttribute('textColor','#000000')
    label001.setAttribute('verticalTextPosition','bottom')
    label001.setAttribute('visible','true')    
    label001.setAttribute('width','230.08984375')
    label001.setAttribute('x','3.0')
    label001.setAttribute('xml:space','preserve')
    label001.setAttribute('y','3761.9913160572523')
    nodelabel001Text = 'Generico XIII secolo - Primi del XIV secolo'
    label001.appendChild(doc.createTextNode(nodelabel001Text)) 
    labelz = doc.createElement('y:LabelModel')
    labelz1 = doc.createElement('y:RowNodeLabelModel')
    labelz1.setAttribute('offset','3.0')
    labelz.appendChild(labelz1)
    labelz2 = doc.createElement('y:ModelParameter')
    labelz3 = doc.createElement('y:RowNodeLabelModelParameter')
    labelz3.setAttribute('horizontalPosition','0.0')
    labelz3.setAttribute('id','row_9')
    labelz3.setAttribute('inside','true')
    
    labelz2.appendChild(labelz3)
    label001.appendChild(labelz)    
    label001.appendChild(labelz2)    
    tablenode.appendChild(label001)
    
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
    property4.setAttribute('value','24.0')
    
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
    defaultrowinsets.setAttribute('left','24.0')
    defaultrowinsets.setAttribute('right','0.0')
    defaultrowinsets.setAttribute('top','0.0')
    table.appendChild(defaultrowinsets)
    
    
    
    
    insets=doc.createElement('y:Insets')
    insets.setAttribute('bottom','0.0')
    insets.setAttribute('left','0.0')
    insets.setAttribute('right','0.0')
    insets.setAttribute('top','30.0')
    table.appendChild(insets)
    
    
    columns=doc.createElement('y:Columns')
    column=doc.createElement('y:Column')
    column.setAttribute('id','column_0')
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
    
    
    
    rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','342.3681377825619')
    row.setAttribute('id','row_2')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','315.73735199138855')
    row.setAttribute('id','row_0')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','308.0086114101184')
    row.setAttribute('id','row_4')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','332.75144644779346')
    row.setAttribute('id','row_1')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','722.576863562971')
    row.setAttribute('id','row_3')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','396.8670949946179')
    row.setAttribute('id','row_5')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','349.5824117835043')
    row.setAttribute('id','row_6')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','476.0806310548976')
    row.setAttribute('id','row_7')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','413.8292918292518')
    row.setAttribute('id','row_8')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    #table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    
    #rows=doc.createElement('y:Rows')    
    row=doc.createElement('y:Row')
    row.setAttribute('height','378.4687941502948')
    row.setAttribute('id','row_9')
    row.setAttribute('minimumHeight','50.0')    
    insets3=doc.createElement('y:Insets')
    insets3.setAttribute('bottom','0.0')
    insets3.setAttribute('left','24.0')
    insets3.setAttribute('right','0.0')
    insets3.setAttribute('top','0.0')
    rows.appendChild(row)
    row.appendChild(insets3)   
    table.appendChild(rows)
    tablenode.appendChild(table)
    data0.appendChild(tablenode)
    graph1 = doc.createElement('graph')
    graph1.setAttribute('edgedefault','directed')    
    graph1.setAttribute('id','n0:')
    
    
    
    
    
    
    node1.appendChild(data0)
    #graph.appendChild(node1)
    #graph1.appendChild(node1)
    graph.appendChild(node1)
    # graph.setAttribute('parse.edges','%d' % len(edges))   
    # graph.setAttribute('parse.nodes','%d' % len(nodes))
    # graph.setAttribute('parse.order', 'free')    
   
    for k,nod in nodes.items():
        nod.exportGraphml(doc, graph, options)
    for el in edges:
        el.exportGraphml(doc, graph, nodes, options)
    
    root.appendChild(graph)
    
    data = doc.createElement('data')
    data.setAttribute('key','d7')    
    res = doc.createElement('y:Resources')
    data.appendChild(res)    
    root.appendChild(data)
    
    o.write('{}'.format(doc.toxml(encoding='UTF-8').decode()))
    

    # parsed_xml = xml.dom.minidom.parseString(xml_string)
    # pretty_xml_as_string = parsed_xml.toprettyxml()

    #file = open("./content_new.xml", 'w')
    #o.write(xml_string)
    
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
    main()