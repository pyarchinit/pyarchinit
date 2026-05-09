# resources/dbfiles/dottoxml_original.py

## Overview

This file contains 7 documented elements.

## Functions

### usage()

*No description available.*
Prints version and usage information for the `dottoxml` tool to standard output. The output includes the application name, version number, and release date, followed by the usage message stored in `usgmsg`, and a hint directing the user to the `-h` or `--help` options for additional information. This function takes no parameters and returns no value.

### exportDot(o, nodes, edges, options)

*No description available.*
Writes a DOT-format graph representation to the output stream `o` by opening a `graph [` block and iterating over all provided nodes and edges. For each node in the `nodes` mapping, it delegates serialization to the node's own `exportDot` method, passing `o` and `options`. Each edge in the `edges` collection is similarly serialized via its `exportDot` method, which additionally receives the `nodes` mapping.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### exportGML(o, nodes, edges, options)

*No description available.*
Writes a GML-formatted graph representation to the output stream `o`. The output begins with a `graph [` block containing fixed header attributes (`comment`, `directed`, and `hierarchic`), followed by GML output for each node in `nodes` and each edge in `edges`, delegating to their respective `exportGML` methods. The block is closed with a closing `]` delimiter.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### exportGraphml(o, nodes, edges, options)

*No description available.*
Serializes a graph to the GraphML format by constructing a DOM document with a `graphml` root element populated with the required namespace declarations and `yFiles`-compatible `key` definitions for nodes, edges, ports, and graph-level attributes. A `graph` child element (with `edgedefault="directed"` and id `"G"`) is appended, and each node and edge is exported into it by delegating to their respective `exportGraphml` methods. The completed XML document is written to the output stream `o` as a UTF-8 encoded string.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### exportGDF(o, nodes, edges, options)

*No description available.*
Writes a GDF (Graph Data Format) representation of a graph to the provided output stream `o`. It begins by writing the node definition header `"nodedef> name"`, then iterates over all nodes and edges, delegating serialization to each element's own `exportGDF` method. The function concludes by writing the edge definition header `"edgedef> node1,node2"`.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### main()

*No description available.*
Entry point for the DOT graph conversion tool. Parses command-line options and arguments to configure output format (Graphml, GML, GDF, or DOT), encoding, and rendering preferences, then reads a DOT-format input file to collect nodes and edges — handling multiline definitions, default node/edge attributes, and implicit node creation from edge declarations. The parsed graph data is optionally filtered by connectivity (sweep mode) before being written to the specified output file via the appropriate export function.

