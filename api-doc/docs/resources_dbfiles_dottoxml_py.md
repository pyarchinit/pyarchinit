# resources/dbfiles/dottoxml.py

## Overview

This file contains 9 documented elements.

## Functions

### usage()

Prints the version information, usage message, and a help hint for the `dottoxml` command-line tool to standard output. The output includes the application name and version (`dottoxml 1.6, 2014-04-10, Dirk Baechle`), the usage string defined in `usgmsg`, and a prompt directing the user to invoke `-h` or `--help` for additional information. This function takes no parameters and returns no value.

### exportDot(o, nodes, edges, options)

*No description available.*
Writes a DOT-format graph representation to the output stream `o` by opening a `graph [` block and iterating over all provided nodes and edges. For each node in the `nodes` mapping, it delegates serialization to the node's own `exportDot` method, passing `o` and `options`. Each edge in the `edges` collection is similarly serialized via its `exportDot` method, with `o`, `nodes`, and `options` forwarded as arguments.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### exportGML(o, nodes, edges, options)

*No description available.*
Writes a GML (Graph Modelling Language) representation of a directed, hierarchic graph to the output stream `o`. The function writes the opening `graph [` block with fixed metadata comments, then iterates over all nodes and edges, delegating serialization to each element's own `exportGML` method, before closing the block with `]`. The `options` parameter is passed through to each node's and edge's individual export call.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### intes()

*No description available.*
Displays a localized input dialog prompting the user to enter a stratigraphic site identifier. The dialog title and message are retrieved from language-specific lookup dictionaries (`_INTES_TITLE` and `_INTES_MSG`) based on the current language returned by `_get_lang()`, falling back to English if the language key is not found. Returns the user-entered value as a string, or prints the error message if a `KeyError` is raised.

### reverse()

return true or false about the order epoch

### exportGraphml(o, nodes, edges, options, ff)

Exports a graph structure to a GraphML file compatible with the yEd graph editor, constructing a complete XML document with the required namespace declarations, key definitions, and a table node (`y:TableNode`) that organizes stratigraphic units into chronological rows derived from the provided `nodes` and `edges` collections. The function iterates over sorted epoch and unit-prefix entries to generate labeled rows and columns, delegates individual node and edge rendering to their respective `exportGraphml` methods, and embeds three inline SVG resources representing graphical symbols. The fully serialized XML document is written as a UTF-8 encoded string to the output object `o`.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`
- `ff`

### exportGDF(o, nodes, edges, options)

*No description available.*
Writes a GDF (Graph Data Format) representation of a graph to the output stream `o`. It begins by writing the node definition header `"nodedef> name"`, then iterates over all entries in the `nodes` mapping and all items in the `edges` collection, delegating serialization to each element's own `exportGDF` method. The function concludes by writing the edge definition header `"edgedef> node1,node2"` to the output stream.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### main()

Parses command-line arguments to configure output format (Graphml, GML, GDF, or DOT), encoding, and display options, then reads a DOT-format input file to collect node and edge definitions. It resolves default attributes, optionally removes unreferenced nodes via a sweep operation, and writes the converted graph data to the specified output file using the selected export format.

