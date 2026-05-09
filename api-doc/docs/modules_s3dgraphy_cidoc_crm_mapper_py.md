# modules/s3dgraphy/cidoc_crm_mapper.py

## Overview

This file contains 7 documented elements.

## Classes

### CIDOCCRMMapper

Maps PyArchInit/Extended Matrix data to CIDOC-CRM classes and properties
CIDOC-CRM is the standard ontology for cultural heritage documentation

#### Methods

##### __init__(self)

Initializes a new instance of the class by setting up the three core RDF namespace URIs used for ontology mapping. The `namespace` attribute is set to the CIDOC-CRM base URI, `crmdig_namespace` to the CRMdig extension URI, and `pyarchinit_namespace` to the pyarchinit project-specific ontology URI. These namespaces serve as the foundational references for subsequent CIDOC-CRM mapping operations performed by the class.

##### map_node_to_cidoc(self, node_data)

Map a stratigraphic unit node to CIDOC-CRM

Args:
    node_data: Node data from Extended Matrix

Returns:
    CIDOC-CRM mapped entity

##### map_edge_to_cidoc(self, edge_data)

Map a relationship edge to CIDOC-CRM property

Args:
    edge_data: Edge data from Extended Matrix

Returns:
    CIDOC-CRM mapped property

##### export_to_cidoc_jsonld(self, graph_data, filepath)

Export Extended Matrix graph to CIDOC-CRM JSON-LD format

Args:
    graph_data: Extended Matrix graph data
    filepath: Output file path

Returns:
    True if successful

##### export_to_rdf_turtle(self, graph_data, filepath)

Export to RDF Turtle format for triple stores

Args:
    graph_data: Extended Matrix graph data
    filepath: Output file path

Returns:
    True if successful

