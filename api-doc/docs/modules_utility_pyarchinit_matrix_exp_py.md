# modules/utility/pyarchinit_matrix_exp.py

## Overview

This file contains 15 documented elements.

## Classes

### HarrisMatrix

This class is used to create a Harris Matrix, a tool used in archaeology to depict the temporal succession of archaeological contexts.

Attributes:
L (str): The user's locale.
HOME (str): The home directory for the PyArchInit application.
DB_MANAGER (str): The database manager for the application.
TABLE_NAME (str): The name of the table in the database.
MAPPER_TABLE_CLASS (str): The mapper table class for the application.
ID_TABLE (str): The ID of the table.
MATRIX (Setting_Matrix): The matrix settings for the application.

#### Methods

##### __init__(self, sequence, negative, conteporene, connection, connection_to, periodi)

The constructor for the HarrisMatrix class.

Parameters:
sequence (list): A list of sequences.
negative (list): A list of negative relationships.
conteporene (list): A list of contemporary relationships.
connection (list): A list of connections.
connection_to (list): A list of connections to other elements.
periodi (list): A list of periods.

##### export_matrix(self)

Export the matrix as a graph using Digraph to visualize relationships between elements, including periods, phases, and service units.
The graph includes custom colors and styles to represent different relationships and types of service units.

##### export_matrix_2(self)

*No description available.*
A read-only property that constructs and exports a Harris matrix stratigraphic diagram as a directed graph using Graphviz's `Digraph` engine. It filters stratigraphic units (US) to only those involved in at least one relationship (`sequence`, `conteporene`, `negative`, `connection`, or `connection_to`), then builds styled subgraphs for each relationship type using visual attributes sourced from dialog combo boxes. The resulting graph is rendered to a DOT file in the `pyarchinit_Matrix_folder` directory, subjected to transitive reduction via a Rust implementation or a fallback `tred` subprocess call, and finally rendered as a JPEG; an optional period grouping and a localized legend (Italian, German, or default) are included when the corresponding dialog checkboxes are checked.

### ViewHarrisMatrix

*No description available.*
A class responsible for generating and rendering Harris Matrix stratigraphic diagrams as directed graphs using the Graphviz `Digraph` engine. It accepts stratigraphic relationship data — including sequential, negative, contemporaneous, and connection relationships — and exposes two properties, `export_matrix` and `export_matrix_3`, that build DOT-format graph files, apply transitive reduction via a Rust implementation or the `tred` subprocess, and render the result as PNG and JPG image files. The `export_matrix_3` property additionally organises nodes into nested subgraphs representing sites, periods, and phases, and includes an adaptive DPI-reduction loop to handle large datasets.

#### Methods

##### __init__(self, sequence, negative, conteporene, connection, connection_to, periodi)

## `__init__` Method

Initializes an instance by accepting and storing six parameters that define the configuration of a matrix-related entity. The parameters `sequence`, `negative`, `periodi`, `conteporene`, `connection`, and `connection_to` are each assigned directly to their corresponding instance attributes. No additional processing or validation is performed during initialization.

##### export_matrix(self)

Builds a directed graph (`Digraph`) representing a Harris matrix by constructing multiple subgraphs from `self.sequence`, `self.conteporene`, `self.negative`, `self.connection`, and `self.connection_to`, each with distinct edge arrow styles. The graph is rendered to a `.dot` file in the `pyarchinit_Matrix_folder` directory, then subjected to transitive reduction via a Rust implementation or the `tred` subprocess fallback, followed by cleanup of layout attributes in the reduced output file. The cleaned transitive-reduction file is finally rendered to both PNG and JPG formats, and the two resulting `Source` objects are returned as a tuple `(g, f)`.

##### export_matrix_3(self)

Generates a directed Harris matrix graph using Graphviz's `Digraph` engine, organizing stratigraphic units (US) into nested subgraphs representing sites, periods, and phases, with distinct visual styles applied to sequence, contemporaneous, and negative relationships. The graph is rendered to a DOT file in the `pyarchinit_Matrix_folder` directory, then processed through transitive reduction (via a Rust implementation or the `tred` subprocess fallback) to produce a simplified JPG output. An adaptive DPI mechanism attempts rendering at decreasing resolution levels (`150`, `120`, `100`, `75`, `50`) to accommodate varying data sizes, logging success or failure to the console without interrupting the calling workflow.

## Functions

### rust_harris_layout(edges, node_labels, phase_groups, layer_spacing, node_spacing)

Compute Harris Matrix layout using the Rust Sugiyama engine.

Args:
    edges: list of (from_id, to_id) directed edges
    node_labels: list of all node identifiers
    phase_groups: optional list of (phase_name, [node_ids...])
    layer_spacing: vertical distance between layers (default 80)
    node_spacing: horizontal distance between nodes (default 60)

Returns:
    dict with 'node_positions' and 'edge_paths', or None if Rust unavailable.

**Parameters:**
- `edges`
- `node_labels`
- `phase_groups`
- `layer_spacing`
- `node_spacing`

### rust_layout_to_dot(layout_result, edges, node_labels, sequence_edges, negative_edges, contemporary_edges, dpi, node_shape, node_color)

Convert Rust layout result to a positioned DOT string for graphviz rendering.

Uses the Sugiyama-computed coordinates as fixed `pos` attributes so graphviz
only performs rendering (not layout). This produces output compatible with the
existing `Source.from_file(...).render()` pipeline.

Args:
    layout_result: dict from rust_harris_layout()
    edges: all directed edges
    node_labels: all node identifiers
    sequence_edges: set of (src, tgt) for stratigraphic sequence edges
    negative_edges: set of (src, tgt) for negative relationship edges
    contemporary_edges: set of (src, tgt) for contemporary edges
    dpi: output DPI
    node_shape: node shape
    node_color: node fill color

Returns:
    DOT string with fixed positions, or None on failure.

**Parameters:**
- `layout_result`
- `edges`
- `node_labels`
- `sequence_edges`
- `negative_edges`
- `contemporary_edges`
- `dpi`
- `node_shape`
- `node_color`

### node_loops_to_self(objects)

This function checks if there are any loops in the graph. A loop in a graph is a situation where a node is connected to itself.

Parameters:
objects (list): A list of lists. Each inner list represents a set of edges in the graph, where each edge is a tuple of two elements (source, target).

Returns:
bool: True if there is at least one loop in the graph, False otherwise.

**Parameters:**
- `objects`

### showMessage(message, title, icon)

*No description available.*
Displays a modal message dialog using Qt's `QMessageBox` with the specified message text, window title, and icon. The `title` parameter defaults to `'Info'` and the `icon` parameter defaults to `QMessageBox.Information` if not provided. The dialog blocks execution until the user dismisses it via `exec()`.

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

*No description available.*
```python
def showMessage(message, title='Info', icon=QMessageBox.Information):
```

Displays a modal message dialog using Qt's `QMessageBox`. Accepts a `message` string to display as the dialog body, an optional `title` string for the window title (defaulting to `'Info'`), and an optional `icon` of type `QMessageBox.Icon` (defaulting to `QMessageBox.Information`). The dialog blocks execution until the user dismisses it via `exec()`.

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

*No description available.*
Displays a modal message dialog using `QMessageBox` with the specified message text, window title, and icon. The `title` parameter defaults to `'Info'` and the `icon` parameter defaults to `QMessageBox.Information` if not provided. The dialog blocks execution until the user dismisses it via `exec()`.

**Parameters:**
- `message`
- `title`
- `icon`

