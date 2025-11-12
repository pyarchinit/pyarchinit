# modules/utility/pyarchinit_matrix_exp.py

## Overview

This file contains 52 documented elements.

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

### ViewHarrisMatrix

#### Methods

##### __init__(self, sequence, negative, conteporene, connection, connection_to, periodi)

##### export_matrix(self)

##### export_matrix_3(self)

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

### ViewHarrisMatrix

#### Methods

##### __init__(self, sequence, negative, conteporene, connection, connection_to, periodi)

##### export_matrix(self)

##### export_matrix_3(self)

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

### ViewHarrisMatrix

#### Methods

##### __init__(self, sequence, negative, conteporene, connection, connection_to, periodi)

##### export_matrix(self)

##### export_matrix_3(self)

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

### ViewHarrisMatrix

#### Methods

##### __init__(self, sequence, negative, conteporene, connection, connection_to, periodi)

##### export_matrix(self)

##### export_matrix_3(self)

## Functions

### node_loops_to_self(objects)

This function checks if there are any loops in the graph. A loop in a graph is a situation where a node is connected to itself.

Parameters:
objects (list): A list of lists. Each inner list represents a set of edges in the graph, where each edge is a tuple of two elements (source, target).

Returns:
bool: True if there is at least one loop in the graph, False otherwise.

**Parameters:**
- `objects`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### node_loops_to_self(objects)

This function checks if there are any loops in the graph. A loop in a graph is a situation where a node is connected to itself.

Parameters:
objects (list): A list of lists. Each inner list represents a set of edges in the graph, where each edge is a tuple of two elements (source, target).

Returns:
bool: True if there is at least one loop in the graph, False otherwise.

**Parameters:**
- `objects`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### node_loops_to_self(objects)

This function checks if there are any loops in the graph. A loop in a graph is a situation where a node is connected to itself.

Parameters:
objects (list): A list of lists. Each inner list represents a set of edges in the graph, where each edge is a tuple of two elements (source, target).

Returns:
bool: True if there is at least one loop in the graph, False otherwise.

**Parameters:**
- `objects`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### node_loops_to_self(objects)

This function checks if there are any loops in the graph. A loop in a graph is a situation where a node is connected to itself.

Parameters:
objects (list): A list of lists. Each inner list represents a set of edges in the graph, where each edge is a tuple of two elements (source, target).

Returns:
bool: True if there is at least one loop in the graph, False otherwise.

**Parameters:**
- `objects`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

### showMessage(message, title, icon)

**Parameters:**
- `message`
- `title`
- `icon`

