# modules/s3dgraphy/s3dgraphy_integration.py

## Overview

This file contains 92 documented elements.

## Classes

### S3DGraphyIntegration

Integrates S3DGraphy Extended Matrix with PyArchInit
for advanced stratigraphic documentation and 3D visualization

#### Methods

##### __init__(self, db_manager)

##### is_available(self)

Check if S3DGraphy is available

##### create_stratigraphic_graph(self, site_name)

Create a new stratigraphic graph for a site

Args:
    site_name: Name of the archaeological site

Returns:
    Graph object or None if S3DGraphy not available

##### add_virtual_reconstruction(self, vr_data)

Add a virtual reconstruction node to the graph
These are hypothetical/reconstructed units for visualization

Args:
    vr_data: Dictionary with virtual reconstruction data

Returns:
    Node object or None

##### add_stratigraphic_unit(self, us_data)

Add a stratigraphic unit to the graph

Args:
    us_data: Dictionary with US data from PyArchInit

Returns:
    Node object or None

##### add_stratigraphic_relationship(self, us_from, us_to, relationship_type)

Add a stratigraphic relationship between two units

Args:
    us_from: Source US identifier
    us_to: Target US identifier
    relationship_type: Type of relationship (covers, cuts, fills, etc.)

Returns:
    True if successful, False otherwise

##### import_from_pyarchinit(self, site, area)

Import stratigraphic data from PyArchInit database

Args:
    site: Site name
    area: Optional area filter

Returns:
    True if successful, False otherwise

##### export_to_graphml(self, filepath)

Export the graph to GraphML format

Args:
    filepath: Path to save the GraphML file

Returns:
    True if successful, False otherwise

##### export_to_json(self, filepath)

Export the graph to JSON format

Args:
    filepath: Path to save the JSON file

Returns:
    True if successful, False otherwise

##### generate_harris_matrix(self)

Generate Harris Matrix from the stratigraphic graph

Returns:
    Dictionary representing the Harris Matrix or None

##### prepare_for_3d_visualization(self)

Prepare data for 3D visualization in Blender via EMtools

Returns:
    Dictionary with 3D visualization data or None

##### validate_stratigraphic_sequence(self)

Validate the stratigraphic sequence for logical consistency

Returns:
    List of validation warnings/errors

##### import_from_extended_matrix(self, filepath)

Import Extended Matrix data (JSON/GraphML) back to PyArchInit

Args:
    filepath: Path to Extended Matrix file

Returns:
    True if successful, False otherwise

##### calculate_chronological_sequence(self)

Calculate the chronological sequence of stratigraphic units
using topological sorting of the directed graph

Returns:
    Dictionary with phases and chronological ordering

##### export_phased_matrix(self, filepath)

Export a phased/periodized matrix view

Args:
    filepath: Path to save the phased matrix

Returns:
    True if successful

### PyArchInitS3DGraphyDialog

Dialog for S3DGraphy integration in PyArchInit

#### Methods

##### __init__(self, parent, db_manager)

##### export_to_extended_matrix(self, site, area, output_path)

Export site data to Extended Matrix format

### QgsMessageLog

#### Methods

##### logMessage(msg, tag, level)

### Qgis

### S3DGraphyIntegration

Integrates S3DGraphy Extended Matrix with PyArchInit
for advanced stratigraphic documentation and 3D visualization

#### Methods

##### __init__(self, db_manager)

##### is_available(self)

Check if S3DGraphy is available

##### create_stratigraphic_graph(self, site_name)

Create a new stratigraphic graph for a site

Args:
    site_name: Name of the archaeological site

Returns:
    Graph object or None if S3DGraphy not available

##### add_virtual_reconstruction(self, vr_data)

Add a virtual reconstruction node to the graph
These are hypothetical/reconstructed units for visualization

Args:
    vr_data: Dictionary with virtual reconstruction data

Returns:
    Node object or None

##### add_stratigraphic_unit(self, us_data)

Add a stratigraphic unit to the graph

Args:
    us_data: Dictionary with US data from PyArchInit

Returns:
    Node object or None

##### add_stratigraphic_relationship(self, us_from, us_to, relationship_type)

Add a stratigraphic relationship between two units

Args:
    us_from: Source US identifier
    us_to: Target US identifier
    relationship_type: Type of relationship (covers, cuts, fills, etc.)

Returns:
    True if successful, False otherwise

##### import_from_pyarchinit(self, site, area)

Import stratigraphic data from PyArchInit database

Args:
    site: Site name
    area: Optional area filter

Returns:
    True if successful, False otherwise

##### export_to_graphml(self, filepath)

Export the graph to GraphML format

Args:
    filepath: Path to save the GraphML file

Returns:
    True if successful, False otherwise

##### export_to_json(self, filepath)

Export the graph to JSON format

Args:
    filepath: Path to save the JSON file

Returns:
    True if successful, False otherwise

##### generate_harris_matrix(self)

Generate Harris Matrix from the stratigraphic graph

Returns:
    Dictionary representing the Harris Matrix or None

##### prepare_for_3d_visualization(self)

Prepare data for 3D visualization in Blender via EMtools

Returns:
    Dictionary with 3D visualization data or None

##### validate_stratigraphic_sequence(self)

Validate the stratigraphic sequence for logical consistency

Returns:
    List of validation warnings/errors

##### import_from_extended_matrix(self, filepath)

Import Extended Matrix data (JSON/GraphML) back to PyArchInit

Args:
    filepath: Path to Extended Matrix file

Returns:
    True if successful, False otherwise

##### calculate_chronological_sequence(self)

Calculate the chronological sequence of stratigraphic units
using topological sorting of the directed graph

Returns:
    Dictionary with phases and chronological ordering

##### export_phased_matrix(self, filepath)

Export a phased/periodized matrix view

Args:
    filepath: Path to save the phased matrix

Returns:
    True if successful

### PyArchInitS3DGraphyDialog

Dialog for S3DGraphy integration in PyArchInit

#### Methods

##### __init__(self, parent, db_manager)

##### export_to_extended_matrix(self, site, area, output_path)

Export site data to Extended Matrix format

### QgsMessageLog

#### Methods

##### logMessage(msg, tag, level)

### Qgis

### S3DGraphyIntegration

Integrates S3DGraphy Extended Matrix with PyArchInit
for advanced stratigraphic documentation and 3D visualization

#### Methods

##### __init__(self, db_manager)

##### is_available(self)

Check if S3DGraphy is available

##### create_stratigraphic_graph(self, site_name)

Create a new stratigraphic graph for a site

Args:
    site_name: Name of the archaeological site

Returns:
    Graph object or None if S3DGraphy not available

##### add_virtual_reconstruction(self, vr_data)

Add a virtual reconstruction node to the graph
These are hypothetical/reconstructed units for visualization

Args:
    vr_data: Dictionary with virtual reconstruction data

Returns:
    Node object or None

##### add_stratigraphic_unit(self, us_data)

Add a stratigraphic unit to the graph

Args:
    us_data: Dictionary with US data from PyArchInit

Returns:
    Node object or None

##### add_stratigraphic_relationship(self, us_from, us_to, relationship_type)

Add a stratigraphic relationship between two units

Args:
    us_from: Source US identifier
    us_to: Target US identifier
    relationship_type: Type of relationship (covers, cuts, fills, etc.)

Returns:
    True if successful, False otherwise

##### import_from_pyarchinit(self, site, area)

Import stratigraphic data from PyArchInit database

Args:
    site: Site name
    area: Optional area filter

Returns:
    True if successful, False otherwise

##### export_to_graphml(self, filepath)

Export the graph to GraphML format

Args:
    filepath: Path to save the GraphML file

Returns:
    True if successful, False otherwise

##### export_to_json(self, filepath)

Export the graph to JSON format

Args:
    filepath: Path to save the JSON file

Returns:
    True if successful, False otherwise

##### generate_harris_matrix(self)

Generate Harris Matrix from the stratigraphic graph

Returns:
    Dictionary representing the Harris Matrix or None

##### prepare_for_3d_visualization(self)

Prepare data for 3D visualization in Blender via EMtools

Returns:
    Dictionary with 3D visualization data or None

##### validate_stratigraphic_sequence(self)

Validate the stratigraphic sequence for logical consistency

Returns:
    List of validation warnings/errors

##### import_from_extended_matrix(self, filepath)

Import Extended Matrix data (JSON/GraphML) back to PyArchInit

Args:
    filepath: Path to Extended Matrix file

Returns:
    True if successful, False otherwise

##### calculate_chronological_sequence(self)

Calculate the chronological sequence of stratigraphic units
using topological sorting of the directed graph

Returns:
    Dictionary with phases and chronological ordering

##### export_phased_matrix(self, filepath)

Export a phased/periodized matrix view

Args:
    filepath: Path to save the phased matrix

Returns:
    True if successful

### PyArchInitS3DGraphyDialog

Dialog for S3DGraphy integration in PyArchInit

#### Methods

##### __init__(self, parent, db_manager)

##### export_to_extended_matrix(self, site, area, output_path)

Export site data to Extended Matrix format

### QgsMessageLog

#### Methods

##### logMessage(msg, tag, level)

### Qgis

### S3DGraphyIntegration

Integrates S3DGraphy Extended Matrix with PyArchInit
for advanced stratigraphic documentation and 3D visualization

#### Methods

##### __init__(self, db_manager)

##### is_available(self)

Check if S3DGraphy is available

##### create_stratigraphic_graph(self, site_name)

Create a new stratigraphic graph for a site

Args:
    site_name: Name of the archaeological site

Returns:
    Graph object or None if S3DGraphy not available

##### add_virtual_reconstruction(self, vr_data)

Add a virtual reconstruction node to the graph
These are hypothetical/reconstructed units for visualization

Args:
    vr_data: Dictionary with virtual reconstruction data

Returns:
    Node object or None

##### add_stratigraphic_unit(self, us_data)

Add a stratigraphic unit to the graph

Args:
    us_data: Dictionary with US data from PyArchInit

Returns:
    Node object or None

##### add_stratigraphic_relationship(self, us_from, us_to, relationship_type)

Add a stratigraphic relationship between two units

Args:
    us_from: Source US identifier
    us_to: Target US identifier
    relationship_type: Type of relationship (covers, cuts, fills, etc.)

Returns:
    True if successful, False otherwise

##### import_from_pyarchinit(self, site, area)

Import stratigraphic data from PyArchInit database

Args:
    site: Site name
    area: Optional area filter

Returns:
    True if successful, False otherwise

##### export_to_graphml(self, filepath)

Export the graph to GraphML format

Args:
    filepath: Path to save the GraphML file

Returns:
    True if successful, False otherwise

##### export_to_json(self, filepath)

Export the graph to JSON format

Args:
    filepath: Path to save the JSON file

Returns:
    True if successful, False otherwise

##### generate_harris_matrix(self)

Generate Harris Matrix from the stratigraphic graph

Returns:
    Dictionary representing the Harris Matrix or None

##### prepare_for_3d_visualization(self)

Prepare data for 3D visualization in Blender via EMtools

Returns:
    Dictionary with 3D visualization data or None

##### validate_stratigraphic_sequence(self)

Validate the stratigraphic sequence for logical consistency

Returns:
    List of validation warnings/errors

##### import_from_extended_matrix(self, filepath)

Import Extended Matrix data (JSON/GraphML) back to PyArchInit

Args:
    filepath: Path to Extended Matrix file

Returns:
    True if successful, False otherwise

##### calculate_chronological_sequence(self)

Calculate the chronological sequence of stratigraphic units
using topological sorting of the directed graph

Returns:
    Dictionary with phases and chronological ordering

##### export_phased_matrix(self, filepath)

Export a phased/periodized matrix view

Args:
    filepath: Path to save the phased matrix

Returns:
    True if successful

### PyArchInitS3DGraphyDialog

Dialog for S3DGraphy integration in PyArchInit

#### Methods

##### __init__(self, parent, db_manager)

##### export_to_extended_matrix(self, site, area, output_path)

Export site data to Extended Matrix format

### QgsMessageLog

#### Methods

##### logMessage(msg, tag, level)

### Qgis

