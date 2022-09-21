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
import re
import random
import X11Colors

r_label = re.compile(r'label\s*=\s*"\s*\{[^\}]*\}\s*"\s*')
r_labelstart = re.compile(r'label\s*=\s*"\s*\{')
r_labelclose = re.compile(r'\}\s*"')

# Default output encoding for the ASCII output formats GML and GDF
latinenc = "latin-1"

def compileAttributes(attribs):
    """ return the list of attributes as a DOT text string """
    atxt = ""
    first = True
    for key, value in attribs.items():
        if not first:
            atxt += ", %s=\"%s\"" % (key, value)
        else:
            atxt += "%s=\"%s\"" % (key, value)
            first = False
            
    return "[%s]" % atxt

def parseAttributes(attribs):
    """ parse the attribute list and return a key/value dict for it """
    adict = {}
    tlist = []
    lmode = False
    ltext = ''
    # First pass: split entries by ,
    for a in attribs.split(','):
        if r_label.findall(a):
            tlist.append(a)
        elif r_labelstart.findall(a):
            ltext = a
            lmode = True
        else:
            if lmode:
                ltext += ",%s" % a
                if r_labelclose.findall(a):
                    lmode = False
                    tlist.append(ltext)
            else:
                tlist.append(a)

    # Second pass: split keys from values by =
    for t in tlist:
        apos = findUnquoted(t, '=')
        if apos > 0:
            adict[t[:apos].strip()] = t[apos+1:].strip().strip('"')

    return adict

def getLabelAttributes(label):
    """ return the sections of the label attributes in a list structure """
    sections = []
    slist = label.split('|')
    for s in slist:
        mlist = []
        s = s.replace('\\r','\\l')
        s = s.replace('\\n','\\l')
        alist = s.split('\\l')
        for a in alist:
            a = a.strip()
            if a != "":
                mlist.append(a)
        sections.append(mlist)
    return sections

def colorNameToRgb(fcol, defaultcol):
    """ convert the color name fcol to an RGB string, if required """
    if not fcol.startswith('#'):
        return X11Colors.color_map.get(fcol, defaultcol)
    else:
        return fcol
    
def getColorAttribute(attribs, key, defaultcol, conf):
    """ extract the color for the attribute key and convert it
        to RGB format if required
    """
    if conf.Colors:
        if key in attribs:
            return colorNameToRgb(attribs[key], defaultcol)
    return defaultcol

def escapeNewlines(label):
    """ convert the newline escape sequences in the given label """
    l = label.replace('\\n','\n')
    l = l.replace('\\l','\n')
    l = l.replace('\\r','\n')
    return l

def findUnescapedQuote(string, spos=0, qchar='"'):
    """ Return the position of the next unescaped quote
        character in the given string, starting at the
        position spos.
        Returns a -1, if no occurrence was found.
    """
    qpos = -1
    
    escaped = 0
    for idx, c in enumerate(string[spos:]):
        if not escaped:
            if c == '\\':
                escaped = 1
            elif c == qchar:
                return idx+spos
        else:
            escaped = 0
        
    return qpos

def findUnquoted(string, char, spos=0, qchar='"'):
    """ Return the position of the next unquoted
        character char in the given string.
        Searching for the next position starts at
        spos, while parsing the quote characters is
        always done from the start of the string.
        Returns a -1, if no occurrence was found.
        Warning: Assumes that the user never searches for an
        actual quote char with this, but uses findUnescapedQuote
        instead (see above).
    """

    # Do we find a quote char at all?
    if string.find(qchar) >= 0:
        # Yes, so try to count matching quotes
        inquotes = 0
        # Find first quote char
        qpos = findUnescapedQuote(string, 0, qchar)
        if qpos >= 0:
            inquotes = 1 - inquotes
        # Find first char to search for
        fpos = string.find(char, spos)
        while fpos >= 0 and qpos >= 0 and qpos < fpos:
            # Keep track of quote chars (inside/outside),
            # until we reach a position after the char to search for
            while qpos < fpos and qpos >= 0:
                qpos = findUnescapedQuote(string, qpos+1, qchar)
                if qpos >= 0:
                    # Toggle inside/outside counter with each found quote char
                    inquotes = 1 - inquotes
            # Did we enter a quoted environment? 
            if qpos > fpos and inquotes:
                # Then, our last occurrence of the char to search for
                # wasn't quoted and we found our match...
                return fpos
            else:
                if qpos < 0:
                    if inquotes:
                        # Catch unbalanced quoted environments
                        return -1
                    else:
                        # No further quote chars follow,
                        # so simply return our current match
                        return fpos
                # Continue search with next char position,
                # outside the current quoted environment
                while fpos < qpos and fpos >= 0:
                    fpos = string.find(char, fpos+1)
        # Couldn't find any further occurrence of the char
        return fpos
    else:
        # Return result for a simple search
        return string.find(char, spos)

def findLastUnquoted(string, char, spos=0, qchar='"'):
    """ Return the position of the last unquoted
        character char in the given string.
        Searching for the last position starts at
        spos, while parsing the quote characters is
        always done from the start of the string.
        Returns a -1, if no occurrence was found.
        Warning: Assumes that the user never searches for an
        actual quote char with this, but uses findUnescapedQuote
        instead (see above).
    """
    lastpos = findUnquoted(string, char, spos, qchar)
    if lastpos >= 0:
        curpos = findUnquoted(string, char, lastpos+1, qchar)
        while curpos > 0:
            lastpos = curpos
            curpos = findUnquoted(string, char, lastpos+1, qchar)
            
    return lastpos

class Node:
    """ a single node in the graph """
    def __init__(self):
        self.label = ""
        self.id = 0
        self.attribs = {}
        self.referenced = False
        self.sections = []
        self.x=0.0
        self.y=0.0
    
    def initFromString(self, line):
        """ extract node info from the given text line """
        spos = findUnquoted(line, '[')
        atts = ""
        if spos >= 0:
            epos = findLastUnquoted(line, ']', spos)
            if epos > 0:
                atts = line[spos+1:epos]
                line = line[:spos] + line[epos+1:]
                line = line.strip()
            else:
                atts = line[spos+1:]
                line = line[:spos].strip()
            if line.startswith('node '):
                line = line[5:]
                line = line.lstrip()
                # Hack that allows a single "node [attributes]"
                # with default values...
                tline = line.rstrip(';')
                tline = tline.rstrip()
                if len(tline) == 0:
                    line = 'node ' + line
        # Strip off trailing ;
        line = line.rstrip(';')
        line = line.rstrip()
        # Process label
        self.label = line.strip('"')
        # Process attributes
        if len(atts):
            self.attribs = parseAttributes(atts)
        # Process sections
        if "label" in self.attribs:
            tlabel = self.attribs["label"]
            if (tlabel != "" and     
                tlabel.startswith('{') and
                tlabel.endswith('}')):
                tlabel = tlabel[1:-1]
                self.sections = getLabelAttributes(tlabel)

    def getLabel(self, conf, multiline=False):
        """ return the label of the node """
        if conf.NodeLabels:
            if 'label' in self.attribs:
                if len(self.sections) > 0:
                    if multiline:
                        return '\n'.join(self.sections[0])
                    else:
                        return ','.join(self.sections[0])
                else:
                    return self.attribs['label']
            else:
                return self.label
        else:
            return ""

    def getLabelWidth(self, conf, multiline=False):
        """ return the maximum width label of the node label"""
        if conf.NodeLabels:
            if 'label' in self.attribs:
                if len(self.sections) > 0:
                    if multiline:
                        # Find maximum label width
                        width = 1
                        for s in self.sections[0]:
                            if len(s) > width:
                                width = len(s)
                        for s in self.sections[1]:
                            if len(s) > width:
                                width = len(s)
                        for s in self.sections[2]:
                            if len(s) > width:
                                width = len(s)
                        return width
                    else:
                        return len(','.join(self.sections[0]))
                else:
                    return len(self.attribs['label'])
            else:
                return len(self.label)
        else:
            return 0

    def complementAttributes(self, node):
        """ from node copy all new attributes, that do not exist in self """
        for a in node.attribs:
            if a not in self.attribs:
                self.attribs[a] = node.attribs[a]
                
    def exportDot(self, o, conf):
        """ write the node in DOT format to the given file """
        if len(self.attribs) > 0:
            o.write("\"%s\" %s;\n" % (self.label, compileAttributes(self.attribs)))
        else:
            o.write("\"%s\";\n" % (self.label))

    def exportGDF(self, o, conf):
        """ write the node in GDF format to the given file """
        tlabel = self.getLabel(conf).encode(latinenc, errors="ignore")
        if tlabel == "":
            tlabel = "n%d" % self.id
        o.write("%s\n" % tlabel)

    def exportGML(self, o, conf):
        """ write the node in GML format to the given file """
        o.write("  node [\n")
        o.write("    id %d\n" % self.id)
        o.write("    label\n")
        o.write("    \"%s\"\n" % self.getLabel(conf).encode(latinenc, errors="ignore"))
        o.write("  ]\n")
    
    def get_y(self,epoch, nome_us) :
        index=0
        y_value=0
        while index <len(epoch):
            if epoch[index] in nome_us:
                #if nome_ex.startswith(epoch[index]):
                y_value=(index)*1000

            index+=1
            #print(str(y_value))
        return y_value
    
        
    def get_x(self,area, nome_us) :
        index=0
        x_value=0
        while index <len(area):
            if area[index] in nome_us:
                #if nome_ex.startswith(epoch[index]):
                x_value=(index)*1000
            #index+=1
            #print(str(x_value))
        return x_value
    def exportGraphml(self, doc, parent, conf, epoch_sigla,area_sigla):        
        """ export the node in Graphml format and append it to the parent XML node """
        graph1 = doc.createElement('graph')
        graph1.setAttribute('edgedefault','directed')    
        graph1.setAttribute('id','n0:')     
        node = doc.createElement('node')
        node.setAttribute('id','n0::n%d' % self.id)
        data0 = doc.createElement('data')
        data0.setAttribute('key', 'd6')
        snode = doc.createElement('y:ShapeNode')
        shape = doc.createElement('y:Shape')
        #labal in description#
        LabelText = self.getLabel(conf, True)
        #label in generic info#
        nodeLabelText = escapeNewlines(self.getLabel(conf, True))
        a = nodeLabelText.rsplit('_',)[0]        
        
        data1 = doc.createElement('data')
        geom = doc.createElement('y:Geometry')
        #elementi per  il DOC#
        generic_node=doc.createElement('y:GenericNode')
        style_prop=doc.createElement('y:StyleProperties')
        style_prop2=doc.createElement('y:StyleProperties')
        prop=doc.createElement('y:Property')
        prop1=doc.createElement('y:Property')
        prop2=doc.createElement('y:Property')
        prop3=doc.createElement('y:Property')
        prop4=doc.createElement('y:Property')
        prop5=doc.createElement('y:Property')
        
        
        svg_node=doc.createElement('y:SVGNode')
        svg_node_p=doc.createElement('y:SVGNodeProperties')
        svg_model=doc.createElement('y:SVGModel')
        svg_content=doc.createElement('y:SVGContent')
        if 'DOC' in a:
            snode=generic_node
            snode.setAttribute('configuration','com.yworks.bpmn.Artifact.withShadow')
        if 'property' in a:
            snode=generic_node
            snode.setAttribute('configuration','com.yworks.bpmn.Artifact.withShadow')
        if 'Combinar' in a:
            snode=svg_node
        if 'Extractor' in a:
            snode=svg_node
        if 'CON' in a:        
            snode=svg_node
            geom.setAttribute('height','26.0')
            geom.setAttribute('width','26.0')        
        elif 'DOC' in a:        
            geom.setAttribute('height','55.0')
            geom.setAttribute('width','35.0')    
        elif 'Extractor' in a :
            geom.setAttribute('height','25.0')
            geom.setAttribute('width','25.0') 
        elif 'Combinar' in a :
            geom.setAttribute('height','25.0')
            geom.setAttribute('width','25.0')         
        else:
            geom.setAttribute('height','30.0')
            geom.setAttribute('width','90.0')
        
             
        
        #geom.setAttribute('x','%r'% self.get_x(area_sigla, LabelText))
        geom.setAttribute('y','%r'% self.get_y(epoch_sigla, LabelText))  
        
        geom.setAttribute('x','520.0')
        snode.appendChild(geom)
        
        fill = doc.createElement('y:Fill')
        border = doc.createElement('y:BorderStyle')
        #elementi per  il property#
        la=doc.createElement('y:LabelModel')
        sn=doc.createElement('y:SmartNodeLabelModel')
        mp=doc.createElement('y:ModelParameter')
        mps=doc.createElement('y:SmartNodeLabelModelParameter')
        label = doc.createElement('y:NodeLabel')
        bb = LabelText.rsplit('_',)[:-1]        
        b = ' '.join(map(str, bb))
        
        
        if a.startswith('CON'):       
            
            label.appendChild(doc.createTextNode('{}'.format(a)))
        elif a.startswith('property'):   
            a=b
            l =' '.join(a.split()[1:2])
            label.appendChild(doc.createTextNode(l))
        
        
        elif a.startswith('DOC'):   
            
            ##inserisco il punto prima dell'ultimo carattere(questo sognifica che i doc non devono essere più di 9 per estrattore)###
            a=a[:-1] + "."+a[-1:]
            ##scrivo il nome della doc cambiando le iniziali DOC in D.###
            label.appendChild(doc.createTextNode('{}'.format(a).replace('DOC','D.')))
        
        else:
            label.appendChild(doc.createTextNode('{}'.format(a).replace('USVA','USV').replace('USVB','USV').replace('USVC','USV').replace('Extractor','D.').replace('Combinar','C.')))     
        if 'USVA' in a:    
            
            fill.setAttribute('color','#000000')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#248fe7')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','Dialog')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','custom')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#FFFFFF')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'USVB' in a:    
            
            fill.setAttribute('color','#000000')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#31792d')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','Dialog')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','custom')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#FFFFFF')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        
        elif 'USVC' in a:    
            
            fill.setAttribute('color','#000000')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#31792d')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','Dialog')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','custom')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#FFFFFF')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        
        
        elif 'USD' in a:    
            
            fill.setAttribute('color','#ffffff')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#d86400')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','Dialog')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','custom')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#FFFFFF')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'USM' in a:
            
            fill.setAttribute('color','#C0C0C0')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#9b3333')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','24')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'US' in a:
            
            fill.setAttribute('color','#FFFFFF')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#9b3333')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','24')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'SU' in a:
            
            fill.setAttribute('color','#FFFFFF')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#9b3333')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','24')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'WSU' in a:
            
            fill.setAttribute('color','#C0C0C0')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#9b3333')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','24')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'CON' in a:
            
            fill.setAttribute('color','#000000')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#000000')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','Dialog')
            label.setAttribute('fontSize','0')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','sandwich')
            label.setAttribute('modelPosition','s')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
            
        elif 'SF' in a:            
            fill.setAttribute('color','#FFFFFF')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#d8bd30')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'VSF' in a:            
            fill.setAttribute('color','#000000')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#b19f61')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'SUS' in a:            
            fill.setAttribute('color','#FFFFFF')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#9b3333')
            border.setAttribute('type','line')
            border.setAttribute('width','3.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'Extractor' in a:            
            fill.setAttribute('color','#CCCCFF')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#000000')
            border.setAttribute('type','line')
            border.setAttribute('width','1.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('borderDistance','0.0')
            label.setAttribute('fontFamily','Dialog')
            label.setAttribute('fontSize','10')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','corners')
            label.setAttribute('modelPosition','nw')
            label.setAttribute('textColor','#000000')
            label.setAttribute('underlinedText','true')
            label.setAttribute('verticalTextPosition','bottom')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
            
        elif 'Combinar' in a:    
            fill.setAttribute('color','#CCCCFF')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#000000')
            border.setAttribute('type','line')
            border.setAttribute('width','1.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('borderDistance','0.0')
            label.setAttribute('fontFamily','Dialog')
            label.setAttribute('fontSize','10')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','corners')
            label.setAttribute('modelPosition','nw')
            label.setAttribute('textColor','#000000')
            label.setAttribute('underlinedText','true')
            label.setAttribute('verticalTextPosition','bottom')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'DOC' in a:    
            
            fill.setAttribute('color','#FFFFFF')
            fill.setAttribute('transparent','false')
            border.setAttribute('color','#000000')
            border.setAttribute('type','line')
            border.setAttribute('width','1.0')
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','bold')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        
        elif 'property' in a:    
            
            fill.setAttribute('color','#FFFFFFE6')
            fill.setAttribute('transparent','false')
            
            border.setAttribute('color','#000000')
            border.setAttribute('type','line')
            border.setAttribute('width','1.0')
            
            label.setAttribute('alignment','center')
            label.setAttribute('autoSizePolicy','content')
            label.setAttribute('fontFamily','DialogInput')
            label.setAttribute('fontSize','12')
            label.setAttribute('fontStyle','plain')
            label.setAttribute('hasBackgroundColor','false')
            label.setAttribute('hasLineColor','false')
            label.setAttribute('height','18.701171875')
            label.setAttribute('horizontalTextPosition','center')
            label.setAttribute('iconTextGap','4')
            label.setAttribute('modelName','internal')
            label.setAttribute('modelPosition','c')
            label.setAttribute('textColor','#000000')
            label.setAttribute('verticalTextPosition','bottom')
            label.setAttribute('visible','true')
            label.setAttribute('width','34.017578125')
            label.setAttribute('x','27.9912109375')
            label.setAttribute('xml:space','preserve')
            label.setAttribute('y','5.6494140625')
        

        
        snode.appendChild(fill)
        snode.appendChild(border)           
        
        snode.appendChild(label)
        
        
        
        if 'USVA' in a:         
            shape.setAttribute('type','parallelogram')
            snode.appendChild(shape)
        elif 'USVB' in a:
            
            shape.setAttribute('type','hexagon')
            snode.appendChild(shape)
        elif 'USVC' in a:
            
            shape.setAttribute('type','ellipse')
            snode.appendChild(shape)
        
        elif 'US' in a:
           
            shape.setAttribute('type','rectangle')
            snode.appendChild(shape)
        elif 'USD' in a:
           
            shape.setAttribute('type','rectangle')
            snode.appendChild(shape)
        
        elif 'USM' in a:
            
            shape.setAttribute('type','rectangle')
            snode.appendChild(shape)
        elif 'SU' in a:
           
            shape.setAttribute('type','rectangle')
            snode.appendChild(shape)
        elif 'WSU' in a:
            
            shape.setAttribute('type','rectangle')
            snode.appendChild(shape)
        
        elif 'CON' in a:
            svg_node_p.setAttribute('usingVisualBounds','true')
            snode.appendChild(svg_node_p)   
            svg_model.setAttribute('svgBoundsPolicy','0')            
            svg_content.setAttribute('refid','3')
            svg_model.appendChild(svg_content)
            snode.appendChild(svg_model)
        elif 'SF' in a:
            
            shape.setAttribute('type','octagon')
            snode.appendChild(shape)
        elif 'VSF' in a:
            
            shape.setAttribute('type','octagon')
            snode.appendChild(shape)
        
        elif 'SUS' in a:
            
            shape.setAttribute('type','ellipse')
            snode.appendChild(shape)
        elif 'Extractor' in a:
            
            svg_node_p.setAttribute('usingVisualBounds','true')
            snode.appendChild(svg_node_p)   
            svg_model.setAttribute('svgBoundsPolicy','0')
            
            svg_content.setAttribute('refid','1')
            svg_model.appendChild(svg_content)
            snode.appendChild(svg_model)
        elif 'Combinar' in a:
            svg_node_p.setAttribute('usingVisualBounds','true')
            snode.appendChild(svg_node_p)   
            svg_model.setAttribute('svgBoundsPolicy','0')
            svg_content.setAttribute('refid','2')
            svg_model.appendChild(svg_content)
            snode.appendChild(svg_model)
        elif 'property' in a:
            shape = style_prop2
            prop.setAttribute('class','java.awt.Color')
            prop.setAttribute('name','com.yworks.bpmn.icon.line.color')
            prop.setAttribute('value','#000000')
            shape.appendChild(prop)
            
            prop1.setAttribute('class','java.awt.Color')
            prop1.setAttribute('name','com.yworks.bpmn.icon.fill2')
            prop1.setAttribute('value','#d4d4d4cc')
            shape.appendChild(prop1)
            
            prop2.setAttribute('class','java.awt.Color')
            prop2.setAttribute('name','com.yworks.bpmn.icon.fill')
            prop2.setAttribute('value','#ffffffe6')
            shape.appendChild(prop2)
            
            prop5.setAttribute('class','com.yworks.yfiles.bpmn.view.BPMNTypeEnum')
            prop5.setAttribute('name','com.yworks.bpmn.type')
            prop5.setAttribute('value','ARTIFACT_TYPE_ANNOTATION')
            shape.appendChild(prop5)
            snode.appendChild(shape)    
            
        elif 'DOC' in a:
            shape = style_prop
            prop.setAttribute('class','java.awt.Color')
            prop.setAttribute('name','com.yworks.bpmn.icon.line.color')
            prop.setAttribute('value','#000000')
            shape.appendChild(prop)
            
            prop1.setAttribute('class','java.awt.Color')
            prop1.setAttribute('name','com.yworks.bpmn.icon.fill2')
            prop1.setAttribute('value','#d4d4d4cc')
            shape.appendChild(prop1)
            
            prop2.setAttribute('class','java.awt.Color')
            prop2.setAttribute('name','com.yworks.bpmn.icon.fill')
            prop2.setAttribute('value','#ffffffe6')
            shape.appendChild(prop2)
            
            prop3.setAttribute('class','com.yworks.yfiles.bpmn.view.BPMNTypeEnum')
            prop3.setAttribute('name','com.yworks.bpmn.type')
            prop3.setAttribute('value','ARTIFACT_TYPE_DATA_OBJECT')
            shape.appendChild(prop3)
            
            prop4.setAttribute('class','com.yworks.yfiles.bpmn.view.DataObjectTypeEnum')
            prop4.setAttribute('name','com.yworks.bpmn.dataObjectType')
            prop4.setAttribute('value','DATA_OBJECT_TYPE_PLAIN')
            shape.appendChild(prop4)        
        
            snode.appendChild(shape)
        
        data0.appendChild(snode)
        
        
        
        
        if 'USVA' in a:         
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'USVB' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'USVC' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'USVD' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve')  
        elif 'US' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'USM' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'SU' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'WSU' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        
        elif 'CON' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
            
        elif 'SUS' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'Extractor' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
        elif 'Combinar' in a:
            data1.setAttribute('key', 'd7')
            data1.setAttribute('xml:space','preserve') 
        elif 'DOC' in a:
            data1.setAttribute('key', 'd4')
            data1.setAttribute('xml:space','preserve') 
        elif 'property' in a:
            data1.setAttribute('key', 'd5')
            data1.setAttribute('xml:space','preserve') 
            
        
        c=' '.join(b.split()[1:])
        
        data1.appendChild(doc.createTextNode('{}'.format(c)))
        node.appendChild(data1)        
        node.appendChild(data0)            
        parent.appendChild(node)
        #parent.appendChild(data_r)
        
class Edge:
    """ a single edge in the graph """
    def __init__(self):
        self.id = 0
        self.src = ""
        self.dest = ""
        self.attribs = {}

    def initFromString(self, line):
        """ extract edge info from the given text line """
        spos = findUnquoted(line, '[')
        atts = ""
        if spos >= 0:
            epos = findLastUnquoted(line, ']', spos)
            if epos > 0:
                atts = line[spos+1:epos]
                line = line[:spos] + line[epos+1:]
                line = line.strip()
            else:
                atts = line[spos+1:]
                line = line[:spos].strip()
            if line.startswith('edge '):
                line = line[5:]
                line = line.lstrip()
                # Hack that allows a single "edge [attributes]"
                # with default values...
                tline = line.rstrip(';')
                tline = tline.rstrip()
                if len(tline) == 0:
                    line = 'edge ' + line
        # Strip off trailing ;
        line = line.rstrip(';')
        line = line.rstrip()
        # Process labels
        ll = line.replace('->',' ').split()
        if len(ll) > 1:
            self.src = ll[0].strip('"')
            self.dest = ll[1].strip('"')
        # Process attributes
        if len(atts):
            self.attribs = parseAttributes(atts)
                        
    def getLabel(self, nodes, conf):
        """ return the label of the edge """
        if conf.EdgeLabels:
            if 'label' in self.attribs:
                return self.attribs['label']
            else:
                if conf.EdgeLabelsAutoComplete:
                    srclink = self.src
                    destlink = self.dest
                    if ('label' in nodes[self.src].attribs):
                        srclink = nodes[self.src].attribs['label']
                    if ('label' in nodes[self.dest].attribs):
                        destlink = nodes[self.dest].attribs['label']
                    return "%s -> %s" % (srclink, destlink)
                else:
                    return ""
        else:
            return ""

    def complementAttributes(self, edge):
        """ from edge copy all new attributes, that do not exist in self """
        for a in edge.attribs:
            if a not in self.attribs:
                self.attribs[a] = edge.attribs[a]
                
    def exportDot(self, o, nodes, conf):
        """ write the edge in DOT format to the given file """
        if len(self.attribs) > 0:
            o.write("\"%s\" -> \"%s\" %s;\n" % (self.src, self.dest, compileAttributes(self.attribs)))
        else:
            o.write("\"%s\" -> \"%s\";\n" % (self.src, self.dest))

    def exportGDF(self, o, nodes, conf):
        """ write the edge in GDF format to the given file """
        slabel = nodes[self.src].getLabel(conf)
        if slabel == "":
            slabel = "n%d" % nodes[self.src].id
        dlabel = nodes[self.dest].getLabel(conf)
        if dlabel == "":
            dlabel = "n%d" % nodes[self.dest].id
        o.write("%s,%s\n" % (slabel.encode(latinenc, errors="ignore"), dlabel.encode(latinenc, errors="ignore")))

    def exportGML(self, o, nodes, conf):
        """ write the edge in GML format to the given file """
        o.write("  edge [\n")
        o.write("    source %d\n" % nodes[self.src].id)
        o.write("    target %d\n" % nodes[self.dest].id)
        o.write("    label\n")
        o.write("    \"%s\"\n" % self.getLabel(nodes, conf).encode(latinenc, errors="ignore"))
        o.write("  ]\n")

    
    def exportGraphml(self, doc, parent, nodes, conf):
        """ export the edge in Graphml format and append it to the parent XML node """
        edge = doc.createElement('edge')
        edge.setAttribute('id','n0::e%d' % self.id)
        edge.setAttribute('source','n0::n%d'% nodes[self.src].id)
        edge.setAttribute('target','n0::n%d'% nodes[self.dest].id)
        
        data2 = doc.createElement('data')
        data2.setAttribute('key', 'd10')

        pedge = doc.createElement('y:PolyLineEdge')
        path=doc.createElement('y:Path')
        path.setAttribute('sx','0.0')
        path.setAttribute('sy','15.0')
        path.setAttribute('tx','0.0')
        path.setAttribute('ty','-15.0')
        pedge.appendChild(path)
        line = doc.createElement('y:LineStyle')
        color = getColorAttribute(self.attribs, 'color', conf.DefaultEdgeColor, conf)
        line.setAttribute('color','%s' % color)
        
        
        if 'style' in self.attribs:
            line.setAttribute('type', '%s' % self.attribs['style'])
        else:
            line.setAttribute('type', 'line')
        
        
        if 'penwidth' in self.attribs:
            line.setAttribute('width', '%s' % self.attribs['penwidth'])
        else:
            line.setAttribute('width', '1.0')
        pedge.appendChild(line)
        arrow = doc.createElement('y:Arrows')
        arrow_tail = conf.DefaultArrowTail
        arrow_head = conf.DefaultArrowHead
        if conf.Arrows:
            if 'arrowtail' in self.attribs:
                arrow_tail = self.attribs['arrowtail']
            if 'arrowhead' in self.attribs:
                arrow_head = self.attribs['arrowhead']
        arrow.setAttribute('source','%s' % arrow_tail)                
        arrow.setAttribute('target','%s' % arrow_head)                
        pedge.appendChild(arrow)
        if conf.EdgeLabels:
            tlabel = self.getLabel(nodes, conf)
            if tlabel != "":
                label = doc.createElement('y:EdgeLabel')
                color = getColorAttribute(self.attribs, 'fontcolor', conf.DefaultEdgeTextColor, conf)
                label.setAttribute('alignment','center')
                label.setAttribute('distance','0.0')
                label.setAttribute('fontFamily','DialogInput')
                label.setAttribute('fontSize','12')
                label.setAttribute('fontStyle','bold')
                label.setAttribute('hasBackgroundColor','false')
                label.setAttribute('hasLineColor','false')
                label.setAttribute('modelName','six_pos')
                label.setAttribute('modelPosition','tail')
                label.setAttribute('textColor','%s' % color)
                label.setAttribute('visible','true')
                label.setAttribute('preferredPlacement','anywhere')
                label.setAttribute('ratio','0.5')
                label.appendChild(doc.createTextNode('%s' % escapeNewlines(tlabel)))        
                pedge.appendChild(label)
        bend = doc.createElement('y:BendStyle')      
        bend.setAttribute('smoothed', 'false')
        pedge.appendChild(bend)
        data2.appendChild(pedge)
        edge.appendChild(data2)

        data3 = doc.createElement('data')
        data3.setAttribute('key', 'd9')
        edge.appendChild(data3)
        
        parent.appendChild(edge)
       