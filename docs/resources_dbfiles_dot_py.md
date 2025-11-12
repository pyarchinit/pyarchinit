# resources/dbfiles/dot.py

## Overview

This file contains 120 documented elements.

## Classes

### Node

a single node in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract node info from the given text line 

##### getLabel(self, conf, multiline)

return the label of the node 

##### getLabelWidth(self, conf, multiline)

return the maximum width label of the node label

##### complementAttributes(self, node)

from node copy all new attributes, that do not exist in self 

##### exportDot(self, o, conf)

write the node in DOT format to the given file 

##### exportGDF(self, o, conf)

write the node in GDF format to the given file 

##### exportGML(self, o, conf)

write the node in GML format to the given file 

##### get_y(self, epoch, nome_us)

##### exportGraphml(self, doc, parent, conf, epoch_sigla)

export the node in Graphml format and append it to the parent XML node 

### Edge

a single edge in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract edge info from the given text line 

##### getLabel(self, nodes, conf)

return the label of the edge 

##### complementAttributes(self, edge)

from edge copy all new attributes, that do not exist in self 

##### exportDot(self, o, nodes, conf)

write the edge in DOT format to the given file 

##### exportGDF(self, o, nodes, conf)

write the edge in GDF format to the given file 

##### exportGML(self, o, nodes, conf)

write the edge in GML format to the given file 

##### exportGraphml(self, doc, parent, nodes, conf)

export the edge in Graphml format and append it to the parent XML node 

### Node

a single node in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract node info from the given text line 

##### getLabel(self, conf, multiline)

return the label of the node 

##### getLabelWidth(self, conf, multiline)

return the maximum width label of the node label

##### complementAttributes(self, node)

from node copy all new attributes, that do not exist in self 

##### exportDot(self, o, conf)

write the node in DOT format to the given file 

##### exportGDF(self, o, conf)

write the node in GDF format to the given file 

##### exportGML(self, o, conf)

write the node in GML format to the given file 

##### get_y(self, epoch, nome_us)

##### exportGraphml(self, doc, parent, conf, epoch_sigla)

export the node in Graphml format and append it to the parent XML node 

### Edge

a single edge in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract edge info from the given text line 

##### getLabel(self, nodes, conf)

return the label of the edge 

##### complementAttributes(self, edge)

from edge copy all new attributes, that do not exist in self 

##### exportDot(self, o, nodes, conf)

write the edge in DOT format to the given file 

##### exportGDF(self, o, nodes, conf)

write the edge in GDF format to the given file 

##### exportGML(self, o, nodes, conf)

write the edge in GML format to the given file 

##### exportGraphml(self, doc, parent, nodes, conf)

export the edge in Graphml format and append it to the parent XML node 

### Node

a single node in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract node info from the given text line 

##### getLabel(self, conf, multiline)

return the label of the node 

##### getLabelWidth(self, conf, multiline)

return the maximum width label of the node label

##### complementAttributes(self, node)

from node copy all new attributes, that do not exist in self 

##### exportDot(self, o, conf)

write the node in DOT format to the given file 

##### exportGDF(self, o, conf)

write the node in GDF format to the given file 

##### exportGML(self, o, conf)

write the node in GML format to the given file 

##### get_y(self, epoch, nome_us)

##### exportGraphml(self, doc, parent, conf, epoch_sigla)

export the node in Graphml format and append it to the parent XML node 

### Edge

a single edge in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract edge info from the given text line 

##### getLabel(self, nodes, conf)

return the label of the edge 

##### complementAttributes(self, edge)

from edge copy all new attributes, that do not exist in self 

##### exportDot(self, o, nodes, conf)

write the edge in DOT format to the given file 

##### exportGDF(self, o, nodes, conf)

write the edge in GDF format to the given file 

##### exportGML(self, o, nodes, conf)

write the edge in GML format to the given file 

##### exportGraphml(self, doc, parent, nodes, conf)

export the edge in Graphml format and append it to the parent XML node 

### Node

a single node in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract node info from the given text line 

##### getLabel(self, conf, multiline)

return the label of the node 

##### getLabelWidth(self, conf, multiline)

return the maximum width label of the node label

##### complementAttributes(self, node)

from node copy all new attributes, that do not exist in self 

##### exportDot(self, o, conf)

write the node in DOT format to the given file 

##### exportGDF(self, o, conf)

write the node in GDF format to the given file 

##### exportGML(self, o, conf)

write the node in GML format to the given file 

##### get_y(self, epoch, nome_us)

##### exportGraphml(self, doc, parent, conf, epoch_sigla)

export the node in Graphml format and append it to the parent XML node 

### Edge

a single edge in the graph 

#### Methods

##### __init__(self)

##### initFromString(self, line)

extract edge info from the given text line 

##### getLabel(self, nodes, conf)

return the label of the edge 

##### complementAttributes(self, edge)

from edge copy all new attributes, that do not exist in self 

##### exportDot(self, o, nodes, conf)

write the edge in DOT format to the given file 

##### exportGDF(self, o, nodes, conf)

write the edge in GDF format to the given file 

##### exportGML(self, o, nodes, conf)

write the edge in GML format to the given file 

##### exportGraphml(self, doc, parent, nodes, conf)

export the edge in Graphml format and append it to the parent XML node 

## Functions

### compileAttributes(attribs)

return the list of attributes as a DOT text string 

**Parameters:**
- `attribs`

### parseAttributes(attribs)

parse the attribute list and return a key/value dict for it 

**Parameters:**
- `attribs`

### getLabelAttributes(label)

return the sections of the label attributes in a list structure 

**Parameters:**
- `label`

### colorNameToRgb(fcol, defaultcol)

convert the color name fcol to an RGB string, if required 

**Parameters:**
- `fcol`
- `defaultcol`

### getColorAttribute(attribs, key, defaultcol, conf)

extract the color for the attribute key and convert it
to RGB format if required

**Parameters:**
- `attribs`
- `key`
- `defaultcol`
- `conf`

### escapeNewlines(label)

convert the newline escape sequences in the given label 

**Parameters:**
- `label`

### findUnescapedQuote(string, spos, qchar)

Return the position of the next unescaped quote
character in the given string, starting at the
position spos.
Returns a -1, if no occurrence was found.

**Parameters:**
- `string`
- `spos`
- `qchar`

### findUnquoted(string, char, spos, qchar)

Return the position of the next unquoted
character char in the given string.
Searching for the next position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

### findLastUnquoted(string, char, spos, qchar)

Return the position of the last unquoted
character char in the given string.
Searching for the last position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

### compileAttributes(attribs)

return the list of attributes as a DOT text string 

**Parameters:**
- `attribs`

### parseAttributes(attribs)

parse the attribute list and return a key/value dict for it 

**Parameters:**
- `attribs`

### getLabelAttributes(label)

return the sections of the label attributes in a list structure 

**Parameters:**
- `label`

### colorNameToRgb(fcol, defaultcol)

convert the color name fcol to an RGB string, if required 

**Parameters:**
- `fcol`
- `defaultcol`

### getColorAttribute(attribs, key, defaultcol, conf)

extract the color for the attribute key and convert it
to RGB format if required

**Parameters:**
- `attribs`
- `key`
- `defaultcol`
- `conf`

### escapeNewlines(label)

convert the newline escape sequences in the given label 

**Parameters:**
- `label`

### findUnescapedQuote(string, spos, qchar)

Return the position of the next unescaped quote
character in the given string, starting at the
position spos.
Returns a -1, if no occurrence was found.

**Parameters:**
- `string`
- `spos`
- `qchar`

### findUnquoted(string, char, spos, qchar)

Return the position of the next unquoted
character char in the given string.
Searching for the next position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

### findLastUnquoted(string, char, spos, qchar)

Return the position of the last unquoted
character char in the given string.
Searching for the last position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

### compileAttributes(attribs)

return the list of attributes as a DOT text string 

**Parameters:**
- `attribs`

### parseAttributes(attribs)

parse the attribute list and return a key/value dict for it 

**Parameters:**
- `attribs`

### getLabelAttributes(label)

return the sections of the label attributes in a list structure 

**Parameters:**
- `label`

### colorNameToRgb(fcol, defaultcol)

convert the color name fcol to an RGB string, if required 

**Parameters:**
- `fcol`
- `defaultcol`

### getColorAttribute(attribs, key, defaultcol, conf)

extract the color for the attribute key and convert it
to RGB format if required

**Parameters:**
- `attribs`
- `key`
- `defaultcol`
- `conf`

### escapeNewlines(label)

convert the newline escape sequences in the given label 

**Parameters:**
- `label`

### findUnescapedQuote(string, spos, qchar)

Return the position of the next unescaped quote
character in the given string, starting at the
position spos.
Returns a -1, if no occurrence was found.

**Parameters:**
- `string`
- `spos`
- `qchar`

### findUnquoted(string, char, spos, qchar)

Return the position of the next unquoted
character char in the given string.
Searching for the next position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

### findLastUnquoted(string, char, spos, qchar)

Return the position of the last unquoted
character char in the given string.
Searching for the last position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

### compileAttributes(attribs)

return the list of attributes as a DOT text string 

**Parameters:**
- `attribs`

### parseAttributes(attribs)

parse the attribute list and return a key/value dict for it 

**Parameters:**
- `attribs`

### getLabelAttributes(label)

return the sections of the label attributes in a list structure 

**Parameters:**
- `label`

### colorNameToRgb(fcol, defaultcol)

convert the color name fcol to an RGB string, if required 

**Parameters:**
- `fcol`
- `defaultcol`

### getColorAttribute(attribs, key, defaultcol, conf)

extract the color for the attribute key and convert it
to RGB format if required

**Parameters:**
- `attribs`
- `key`
- `defaultcol`
- `conf`

### escapeNewlines(label)

convert the newline escape sequences in the given label 

**Parameters:**
- `label`

### findUnescapedQuote(string, spos, qchar)

Return the position of the next unescaped quote
character in the given string, starting at the
position spos.
Returns a -1, if no occurrence was found.

**Parameters:**
- `string`
- `spos`
- `qchar`

### findUnquoted(string, char, spos, qchar)

Return the position of the next unquoted
character char in the given string.
Searching for the next position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

### findLastUnquoted(string, char, spos, qchar)

Return the position of the last unquoted
character char in the given string.
Searching for the last position starts at
spos, while parsing the quote characters is
always done from the start of the string.
Returns a -1, if no occurrence was found.
Warning: Assumes that the user never searches for an
actual quote char with this, but uses findUnescapedQuote
instead (see above).

**Parameters:**
- `string`
- `char`
- `spos`
- `qchar`

