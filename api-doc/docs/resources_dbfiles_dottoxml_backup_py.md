# resources/dbfiles/dottoxml_backup.py

## Overview

This file contains 9 documented elements.

## Functions

### usage()

Prints the version information, usage message, and a help hint for the `dottoxml` command-line tool to standard output. The output includes the tool name and version (`dottoxml 1.6, 2014-04-10, Dirk Baechle`), the usage string defined in `usgmsg`, and a prompt directing the user to the `-h` or `--help` options for additional information. This function takes no parameters and returns no value.

### exportDot(o, nodes, edges, options)

*No description available.*
Writes a DOT-format graph representation to the output stream `o` by opening a `graph [` block and iterating over the provided `nodes` and `edges` collections. For each node in `nodes`, it delegates to the node's own `exportDot` method, passing `o` and `options`. For each edge in `edges`, it similarly delegates to the edge's `exportDot` method, passing `o`, `nodes`, and `options`.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### exportGML(o, nodes, edges, options)

*No description available.*
Writes a complete GML (Graph Modelling Language) graph representation to the provided output stream `o`. The function opens the graph block with fixed header attributes — including a comment, `directed 1`, and `hierarchic 1` — then iterates over all entries in `nodes` and `edges`, delegating serialization to each element's own `exportGML` method. The graph block is closed with a terminating `]\n` after all nodes and edges have been written.

**Signature:**
```python
def exportGML(o, nodes, edges, options)
```

| Parameter | Description |
|-----------|-------------|
| `o` | A writable output stream to which the GML content is written. |
| `nodes` | A mapping of node identifiers to node objects, each exposing an `exportGML` method. |
| `edges` | An iterable of edge objects, each exposing an `exportGML` method. |
| `options` | Options passed through to each node's and edge's `exportGML` method (see implementation). |

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### intes()

*No description available.*
Displays a modal text input dialog using `QInputDialog`, resized to 700×100 pixels, prompting the user to enter a heading ("intestazione") for a stratigraphic diagram. Returns the entered text as a string if the dialog interaction succeeds. Catches and prints any `KeyError` exception that occurs during execution.

### reverse()

return true or false about the order epoch  

### exportGraphml(o, nodes, edges, options, ff)

Constructs and writes a complete GraphML document compatible with the yEd graph editor to the output stream `o`. The function builds a structured XML document containing a directed graph with a grouped table node representing stratigraphic periods as rows, populates it with the provided `nodes` and `edges` by delegating to their respective `exportGraphml` methods, and appends embedded SVG resources for custom node symbols. The output includes all required GraphML namespace declarations, key definitions, and yFiles-specific styling attributes.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`
- `ff`

### exportGDF(o, nodes, edges, options)

*No description available.*
Writes a GDF-formatted graph representation to the output object `o`, using the provided collections of nodes and edges. It begins by writing the node definition header `"nodedef> name\n"`, then delegates serialization to each node's and edge's own `exportGDF` method, passing along the `options` parameter. The function concludes by writing the edge definition header `"edgedef> node1,node2\n"`.

**Parameters:**
- `o`
- `nodes`
- `edges`
- `options`

### main()

*No description available.*
Entry point for the DOT graph conversion tool that parses command-line options and arguments to configure the output format (Graphml, GML, GDF, or DOT) and processing behavior (verbose output, node sweeping, label/color/arrow settings, and encoding overrides). It reads a DOT-format input file, parses its nodes and edges — including multiline definitions and default attribute inheritance — and writes the converted graph to the specified output file. If fewer than two positional arguments (input file and output file) are provided, it prints usage information and exits with a non-zero status code.

