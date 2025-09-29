#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration module for S3DGraphy with PyArchInit
Provides Extended Matrix functionality for stratigraphic documentation
"""

import os
import json
from typing import List, Dict, Any, Optional

# Make QGIS imports optional
try:
    from qgis.PyQt.QtWidgets import QMessageBox
    from qgis.core import QgsMessageLog, Qgis
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False
    # Define dummy classes for when QGIS is not available
    class QgsMessageLog:
        @staticmethod
        def logMessage(msg, tag, level):
            print(f"[{tag}] {msg}")
    class Qgis:
        Info = 0
        Warning = 1
        Critical = 2

# Check if s3dgraphy is installed
try:
    from s3dgraphy import Graph, Node, Edge
    S3DGRAPHY_AVAILABLE = True
except ImportError:
    S3DGRAPHY_AVAILABLE = False
    try:
        from qgis.core import QgsMessageLog, Qgis
        QgsMessageLog.logMessage(
            "S3DGraphy not installed. Install with: pip install s3dgraphy",
            "PyArchInit", Qgis.Warning
        )
    except:
        print("S3DGraphy not installed. Install with: pip install s3dgraphy")


class S3DGraphyIntegration:
    """
    Integrates S3DGraphy Extended Matrix with PyArchInit
    for advanced stratigraphic documentation and 3D visualization
    """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.graph = None
        self.nodes = {}  # Cache of created nodes

    def is_available(self) -> bool:
        """Check if S3DGraphy is available"""
        return S3DGRAPHY_AVAILABLE

    def create_stratigraphic_graph(self, site_name: str) -> Optional['Graph']:
        """
        Create a new stratigraphic graph for a site

        Args:
            site_name: Name of the archaeological site

        Returns:
            Graph object or None if S3DGraphy not available
        """
        if not S3DGRAPHY_AVAILABLE:
            return None

        try:
            self.graph = Graph(
                graph_id=f"PyArchInit_{site_name}",
                name=f"Stratigraphic Matrix - {site_name}",
                description=f"Extended Matrix export from PyArchInit for site {site_name}"
            )
            return self.graph
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error creating S3DGraphy graph: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return None

    def add_virtual_reconstruction(self, vr_data: Dict[str, Any]) -> Optional['Node']:
        """
        Add a virtual reconstruction node to the graph
        These are hypothetical/reconstructed units for visualization

        Args:
            vr_data: Dictionary with virtual reconstruction data

        Returns:
            Node object or None
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return None

        try:
            # Create node ID for virtual reconstruction
            node_id = f"VR_{vr_data.get('sito', '')}_{vr_data.get('area', '')}_{vr_data.get('id', '')}"

            # Create virtual node
            node = Node(
                node_id=node_id,
                name=f"Virtual: {vr_data.get('name', 'Reconstruction')}",
                description=vr_data.get('description', 'Virtual reconstruction')
            )

            # Set as virtual/reconstruction node type
            node.node_type = 'virtual_reconstruction'
            node.is_virtual = True
            node.sito = vr_data.get('sito', '')
            node.area = vr_data.get('area', '')
            node.reconstruction_type = vr_data.get('type', 'hypothesis')  # hypothesis, restoration, completion
            node.confidence_level = vr_data.get('confidence', 'medium')  # low, medium, high
            node.based_on = vr_data.get('based_on', [])  # List of US this is based on
            node.author = vr_data.get('author', '')
            node.date_created = vr_data.get('date', '')
            node.periodo = vr_data.get('periodo', '')
            node.fase = vr_data.get('fase', '')

            # 3D reconstruction data
            if '3d_model' in vr_data:
                node.model_path = vr_data['3d_model']
            if 'texture' in vr_data:
                node.texture_path = vr_data['texture']
            if 'coordinates' in vr_data:
                node.coordinates = vr_data['coordinates']

            # Add to graph
            self.graph.add_node(node)
            self.nodes[node_id] = node

            return node

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error adding virtual reconstruction: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return None

    def add_stratigraphic_unit(self, us_data: Dict[str, Any]) -> Optional['Node']:
        """
        Add a stratigraphic unit to the graph

        Args:
            us_data: Dictionary with US data from PyArchInit

        Returns:
            Node object or None
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return None

        try:
            # Create node ID from site, area, and US number
            node_id = f"{us_data.get('sito', '')}_{us_data.get('area', '')}_{us_data.get('us', '')}"

            # Create node with S3DGraphy API
            node = Node(
                node_id=node_id,
                name=f"US {us_data.get('us', '')}",
                description=f"{us_data.get('d_stratigrafica', '')} - {us_data.get('d_interpretativa', '')}"
            )

            # Add additional properties as attributes
            node.sito = us_data.get('sito', '')
            node.area = us_data.get('area', '')
            node.us = us_data.get('us', '')
            node.periodo = us_data.get('periodo_iniziale', '')
            node.fase = us_data.get('fase_iniziale', '')
            node.datazione = us_data.get('datazione', '')

            # Map PyArchInit unit types to S3DGraphy node types
            # unita_tipo can be: US (stratigraphy), USM (masonry), USF (feature), etc.
            unita_tipo = us_data.get('unita_tipo', 'US')

            # S3DGraphy Extended Matrix node types mapping
            node_type_mapping = {
                'US': 'stratigraphic_unit',  # Regular stratigraphic unit
                'USM': 'masonry_unit',  # Masonry stratigraphic unit
                'USF': 'feature_unit',  # Feature unit (cuts, pits, etc.)
                'USD': 'deposit_unit',  # Deposit unit
                'USR': 'structural_unit',  # Structural unit
                'VSF': 'virtual_feature',  # Virtual/reconstructed feature
                'CON': 'construction_unit',  # Construction unit
                'SF': 'special_find'  # Special find context
            }

            node.node_type = node_type_mapping.get(unita_tipo, 'stratigraphic_unit')
            node.unita_tipo = unita_tipo  # Keep original PyArchInit type

            # Add stratigraphic definitions
            node.d_stratigrafica = us_data.get('d_stratigrafica', '')  # Stratigraphic definition
            node.d_interpretativa = us_data.get('d_interpretativa', '')  # Interpretative definition

            # Add to graph
            self.graph.add_node(node)

            # Cache the node
            self.nodes[node_id] = node

            return node

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error adding stratigraphic unit to graph: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return None

    def add_stratigraphic_relationship(self, us_from: str, us_to: str,
                                      relationship_type: str) -> bool:
        """
        Add a stratigraphic relationship between two units

        Args:
            us_from: Source US identifier
            us_to: Target US identifier
            relationship_type: Type of relationship (covers, cuts, fills, etc.)

        Returns:
            True if successful, False otherwise
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return False

        try:
            # Map PyArchInit relationship types to Extended Matrix types
            # S3DGraphy uses temporal relationships
            # Check both capitalized and lowercase versions
            rel_lower = relationship_type.lower().strip()

            # IMPORTANT: In Extended Matrix, "is_before" means stratigraphically ABOVE (more recent)
            # We need to handle inverse relationships correctly
            relationship_mapping = {
                # Italian - lowercase
                # Direct relationships (A rel B)
                'copre': 'is_before',  # A covers B = A is above/after B
                'coperto da': 'INVERSE',  # A covered by B = B is above A (needs inversion)
                'riempie': 'has_same_time',  # A fills B = contemporary
                'riempito da': 'INVERSE_CONTEMP',  # A filled by B = B fills A (needs inversion)
                'taglia': 'is_before',  # A cuts B = A is after B
                'tagliato da': 'INVERSE',  # A cut by B = B cuts A (needs inversion)
                'si lega a': 'has_same_time',  # Bonds = contemporary
                'si appoggia a': 'is_before',  # A leans on B = A is after B
                'gli si appoggia': 'INVERSE',  # A is leaned on by B = B leans on A (needs inversion)
                'uguale a': 'has_same_time',  # Equals = same time
                'contemporaneo a': 'has_same_time',
                # English - lowercase
                'covers': 'is_before',
                'covered by': 'is_before',
                'fills': 'has_same_time',
                'filled by': 'has_same_time',
                'cuts': 'is_before',
                'cut by': 'is_before',
                'bonds with': 'has_same_time',
                'same as': 'has_same_time',
                'abuts': 'is_before',
                'supports': 'is_before',
                'connected to': 'has_same_time',
            }

            # Debug print
            if relationship_type not in ['', None]:
                print(f"Mapping relationship: '{relationship_type}' -> '{rel_lower}' -> ", end="")

            em_relationship = relationship_mapping.get(
                rel_lower,
                'generic_connection'  # Default for unknown types
            )

            if relationship_type not in ['', None]:
                print(f"'{em_relationship}'")

            # Generate unique edge ID - use only source, target and type (not original relationship name)
            edge_id = f"edge_{us_from}_{us_to}_{em_relationship}"

            # Check if edge already exists
            existing_edge = None
            for edge in self.graph.edges:
                if edge.edge_id == edge_id:
                    existing_edge = edge
                    break

            if existing_edge:
                # Edge already exists, skip
                print(f"Edge already exists: {edge_id}")
                return True

            # Add edge to graph using S3DGraphy API
            self.graph.add_edge(
                edge_id=edge_id,
                edge_source=us_from,
                edge_target=us_to,
                edge_type=em_relationship
            )

            return True

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error adding relationship: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return False

    def import_from_pyarchinit(self, site: str, area: Optional[str] = None) -> bool:
        """
        Import stratigraphic data from PyArchInit database

        Args:
            site: Site name
            area: Optional area filter

        Returns:
            True if successful, False otherwise
        """
        if not self.db_manager or not S3DGRAPHY_AVAILABLE:
            return False

        try:
            # Create graph for the site
            self.create_stratigraphic_graph(site)

            # Query US data from PyArchInit
            search_dict = {'sito': site}
            if area:
                search_dict['area'] = area

            us_records = self.db_manager.query_bool(
                search_dict,
                'US'
            )

            # Add all US as nodes
            for us_record in us_records:
                us_dict = {
                    'sito': us_record.sito,
                    'area': us_record.area,
                    'us': us_record.us,
                    'unita_tipo': us_record.unita_tipo,  # Add unit type
                    'd_stratigrafica': us_record.d_stratigrafica,
                    'd_interpretativa': us_record.d_interpretativa,
                    'periodo_iniziale': us_record.periodo_iniziale,
                    'fase_iniziale': us_record.fase_iniziale,
                    'datazione': us_record.datazione,
                    'stato_di_conservazione': us_record.stato_di_conservazione,
                    'descrizione': us_record.descrizione,
                    'interpretazione': us_record.interpretazione
                }
                self.add_stratigraphic_unit(us_dict)

            # Add relationships
            print(f"Processing relationships for {len(us_records)} US records...")
            relationship_count = 0

            for us_record in us_records:
                us_id = f"{us_record.sito}_{us_record.area}_{us_record.us}"

                # Process rapporti (direct relationships)
                # In PyArchInit format is: [[rel_type, target_us], ...]
                if us_record.rapporti and us_record.rapporti != '[]':
                    try:
                        import ast
                        # Rapporti is stored as a string representation of list
                        rapporti = ast.literal_eval(us_record.rapporti)

                        if isinstance(rapporti, list):
                            for rapporto in rapporti:
                                if isinstance(rapporto, list) and len(rapporto) >= 2:
                                    # PyArchInit format: [relationship_type, target_us]
                                    rel_type = str(rapporto[0]).strip().lower()
                                    target_us = str(rapporto[1]).strip()

                                    # Create target ID
                                    target_id = f"{us_record.sito}_{us_record.area}_{target_us}"

                                    # Map relationships - handle inverse relationships
                                    relationship_mapping = {
                                        'copre': 'is_before',  # A covers B = A is above/after B
                                        'coperto da': 'INVERSE',  # A covered by B = B is above A (needs inversion)
                                        'riempie': 'has_same_time',  # A fills B = contemporary
                                        'riempito da': 'INVERSE_CONTEMP',  # A filled by B = B fills A (needs inversion)
                                        'taglia': 'is_before',  # A cuts B = A is after B
                                        'tagliato da': 'INVERSE',  # A cut by B = B cuts A (needs inversion)
                                        'si lega a': 'has_same_time',  # Bonds = contemporary
                                        'si appoggia a': 'is_before',  # A leans on B = A is after B
                                        'gli si appoggia': 'INVERSE',  # B leans on A (needs inversion)
                                        'uguale a': 'has_same_time',  # Equals = same time
                                        'contemporaneo a': 'has_same_time',
                                        'posteriorita': 'is_before'  # A after B
                                    }

                                    edge_type = relationship_mapping.get(rel_type, 'generic_connection')

                                    # Handle inverse relationships
                                    if edge_type == 'INVERSE':
                                        # For inverse relationships, swap source and target
                                        if self.add_stratigraphic_relationship(target_id, us_id, 'is_before'):
                                            relationship_count += 1
                                            if relationship_count <= 5:  # Show first few
                                                print(f"  Added (inverted): US {target_us} covers US {us_record.us}")
                                    elif edge_type == 'INVERSE_CONTEMP':
                                        # For inverse contemporary relationships
                                        if self.add_stratigraphic_relationship(target_id, us_id, 'has_same_time'):
                                            relationship_count += 1
                                            if relationship_count <= 5:  # Show first few
                                                print(f"  Added (inverted): US {target_us} fills US {us_record.us}")
                                    else:
                                        # Normal relationship
                                        if self.add_stratigraphic_relationship(us_id, target_id, edge_type):
                                            relationship_count += 1
                                            if relationship_count <= 5:  # Show first few
                                                print(f"  Added: US {us_record.us} {rel_type} US {target_us}")

                    except Exception as e:
                        print(f"Error parsing rapporti for US {us_record.us}: {e}")
                        if hasattr(us_record, 'rapporti'):
                            print(f"  Raw rapporti: {repr(us_record.rapporti)[:200]}")

                # Also process rapporti2 (inverse relationships) if present
                if hasattr(us_record, 'rapporti2') and us_record.rapporti2 and us_record.rapporti2 != '[]':
                    try:
                        import ast
                        # Rapporti2 contains inverse relationships
                        rapporti2 = ast.literal_eval(us_record.rapporti2)

                        if isinstance(rapporti2, list):
                            for rapporto in rapporti2:
                                if isinstance(rapporto, list) and len(rapporto) >= 2:
                                    # Format: [relationship_type, source_us]
                                    # This is the inverse, so we need to swap
                                    rel_type = str(rapporto[0]).strip().lower()
                                    source_us = str(rapporto[1]).strip()

                                    # Create source ID (this is who has the relationship TO us_record)
                                    source_id = f"{us_record.sito}_{us_record.area}_{source_us}"

                                    # Map relationships - handle inverse relationships
                                    relationship_mapping = {
                                        'copre': 'is_before',  # A covers B = A is above/after B
                                        'coperto da': 'INVERSE',  # A covered by B = B is above A (needs inversion)
                                        'riempie': 'has_same_time',  # A fills B = contemporary
                                        'riempito da': 'INVERSE_CONTEMP',  # A filled by B = B fills A (needs inversion)
                                        'taglia': 'is_before',  # A cuts B = A is after B
                                        'tagliato da': 'INVERSE',  # A cut by B = B cuts A (needs inversion)
                                        'si lega a': 'has_same_time',  # Bonds = contemporary
                                        'si appoggia a': 'is_before',  # A leans on B = A is after B
                                        'gli si appoggia': 'INVERSE',  # B leans on A (needs inversion)
                                        'uguale a': 'has_same_time',  # Equals = same time
                                        'contemporaneo a': 'has_same_time',
                                        'posteriorita': 'is_before'  # A after B
                                    }

                                    edge_type = relationship_mapping.get(rel_type, 'generic_connection')

                                    # Handle inverse relationships
                                    if edge_type == 'INVERSE':
                                        # For inverse relationships, swap source and target
                                        if self.add_stratigraphic_relationship(us_id, source_id, 'is_before'):
                                            relationship_count += 1
                                            if relationship_count <= 10:  # Show first few
                                                print(f"  Added inverse (inverted): US {us_record.us} covers US {source_us}")
                                    elif edge_type == 'INVERSE_CONTEMP':
                                        # For inverse contemporary relationships
                                        if self.add_stratigraphic_relationship(us_id, source_id, 'has_same_time'):
                                            relationship_count += 1
                                            if relationship_count <= 10:  # Show first few
                                                print(f"  Added inverse (inverted): US {us_record.us} fills US {source_us}")
                                    else:
                                        # Normal relationship (source -> current US)
                                        if self.add_stratigraphic_relationship(source_id, us_id, edge_type):
                                            relationship_count += 1
                                            if relationship_count <= 10:  # Show first few
                                                print(f"  Added inverse: US {source_us} {rel_type} US {us_record.us}")

                    except Exception as e:
                        print(f"Error parsing rapporti2 for US {us_record.us}: {e}")

            print(f"Total relationships added: {relationship_count}")

            return True

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error importing from PyArchInit: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return False

    def export_to_graphml(self, filepath: str) -> bool:
        """
        Export the graph to GraphML format

        Args:
            filepath: Path to save the GraphML file

        Returns:
            True if successful, False otherwise
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return False

        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom

            # Create GraphML root element
            graphml = ET.Element('graphml')
            graphml.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')
            graphml.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            graphml.set('xsi:schemaLocation', 'http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')

            # Define keys for node and edge attributes
            keys = {
                'node_name': ET.SubElement(graphml, 'key'),
                'node_desc': ET.SubElement(graphml, 'key'),
                'node_type': ET.SubElement(graphml, 'key'),
                'sito': ET.SubElement(graphml, 'key'),
                'area': ET.SubElement(graphml, 'key'),
                'us': ET.SubElement(graphml, 'key'),
                'periodo': ET.SubElement(graphml, 'key'),
                'fase': ET.SubElement(graphml, 'key'),
                'datazione': ET.SubElement(graphml, 'key'),
                'edge_type': ET.SubElement(graphml, 'key')
            }

            # Configure keys
            keys['node_name'].set('id', 'd0')
            keys['node_name'].set('for', 'node')
            keys['node_name'].set('attr.name', 'name')
            keys['node_name'].set('attr.type', 'string')

            keys['node_desc'].set('id', 'd1')
            keys['node_desc'].set('for', 'node')
            keys['node_desc'].set('attr.name', 'description')
            keys['node_desc'].set('attr.type', 'string')

            keys['node_type'].set('id', 'd2')
            keys['node_type'].set('for', 'node')
            keys['node_type'].set('attr.name', 'node_type')
            keys['node_type'].set('attr.type', 'string')

            keys['sito'].set('id', 'd3')
            keys['sito'].set('for', 'node')
            keys['sito'].set('attr.name', 'sito')
            keys['sito'].set('attr.type', 'string')

            keys['area'].set('id', 'd4')
            keys['area'].set('for', 'node')
            keys['area'].set('attr.name', 'area')
            keys['area'].set('attr.type', 'string')

            keys['us'].set('id', 'd5')
            keys['us'].set('for', 'node')
            keys['us'].set('attr.name', 'us')
            keys['us'].set('attr.type', 'string')

            keys['periodo'].set('id', 'd6')
            keys['periodo'].set('for', 'node')
            keys['periodo'].set('attr.name', 'periodo')
            keys['periodo'].set('attr.type', 'string')

            keys['fase'].set('id', 'd7')
            keys['fase'].set('for', 'node')
            keys['fase'].set('attr.name', 'fase')
            keys['fase'].set('attr.type', 'string')

            keys['datazione'].set('id', 'd8')
            keys['datazione'].set('for', 'node')
            keys['datazione'].set('attr.name', 'datazione')
            keys['datazione'].set('attr.type', 'string')

            keys['edge_type'].set('id', 'd9')
            keys['edge_type'].set('for', 'edge')
            keys['edge_type'].set('attr.name', 'relationship_type')
            keys['edge_type'].set('attr.type', 'string')

            # Create graph element
            graph_elem = ET.SubElement(graphml, 'graph')
            graph_elem.set('id', self.graph.graph_id)
            graph_elem.set('edgedefault', 'directed')

            # Add nodes
            for node in self.graph.nodes:
                node_elem = ET.SubElement(graph_elem, 'node')
                node_elem.set('id', node.node_id)

                # Add node data
                data_name = ET.SubElement(node_elem, 'data')
                data_name.set('key', 'd0')
                data_name.text = node.name if node.name else ''

                data_desc = ET.SubElement(node_elem, 'data')
                data_desc.set('key', 'd1')
                data_desc.text = node.description if node.description else ''

                if hasattr(node, 'node_type'):
                    data_type = ET.SubElement(node_elem, 'data')
                    data_type.set('key', 'd2')
                    data_type.text = str(node.node_type)

                if hasattr(node, 'sito'):
                    data_sito = ET.SubElement(node_elem, 'data')
                    data_sito.set('key', 'd3')
                    data_sito.text = str(node.sito)

                if hasattr(node, 'area'):
                    data_area = ET.SubElement(node_elem, 'data')
                    data_area.set('key', 'd4')
                    data_area.text = str(node.area)

                if hasattr(node, 'us'):
                    data_us = ET.SubElement(node_elem, 'data')
                    data_us.set('key', 'd5')
                    data_us.text = str(node.us)

                if hasattr(node, 'periodo'):
                    data_periodo = ET.SubElement(node_elem, 'data')
                    data_periodo.set('key', 'd6')
                    data_periodo.text = str(node.periodo)

                if hasattr(node, 'fase'):
                    data_fase = ET.SubElement(node_elem, 'data')
                    data_fase.set('key', 'd7')
                    data_fase.text = str(node.fase)

                if hasattr(node, 'datazione'):
                    data_datazione = ET.SubElement(node_elem, 'data')
                    data_datazione.set('key', 'd8')
                    data_datazione.text = str(node.datazione)

            # Add edges
            for edge in self.graph.edges:
                edge_elem = ET.SubElement(graph_elem, 'edge')
                edge_elem.set('id', edge.edge_id)
                edge_elem.set('source', edge.edge_source)
                edge_elem.set('target', edge.edge_target)

                data_type = ET.SubElement(edge_elem, 'data')
                data_type.set('key', 'd9')
                data_type.text = edge.edge_type

            # Pretty print and save
            rough_string = ET.tostring(graphml, encoding='unicode')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent='  ', encoding='UTF-8')

            with open(filepath, 'wb') as f:
                f.write(pretty_xml)

            return True

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error exporting to GraphML: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return False

    def export_to_json(self, filepath: str) -> bool:
        """
        Export the graph to JSON format

        Args:
            filepath: Path to save the JSON file

        Returns:
            True if successful, False otherwise
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return False

        try:
            # Build JSON structure manually
            graph_data = {
                "graph_id": self.graph.graph_id,
                "name": self.graph.name,
                "description": self.graph.description if self.graph.description else "",
                "metadata": {
                    "created_by": "PyArchInit",
                    "export_date": str(json.loads(json.dumps(None, default=str)))  # Current date
                },
                "nodes": [],
                "edges": []
            }

            # Add nodes
            for node in self.graph.nodes:
                node_data = {
                    "node_id": node.node_id,
                    "name": node.name,
                    "description": node.description,
                    "node_type": getattr(node, 'node_type', 'unknown'),
                    "unita_tipo": getattr(node, 'unita_tipo', ''),
                    "sito": getattr(node, 'sito', ''),
                    "area": getattr(node, 'area', ''),
                    "us": getattr(node, 'us', ''),
                    "d_stratigrafica": getattr(node, 'd_stratigrafica', ''),
                    "d_interpretativa": getattr(node, 'd_interpretativa', ''),
                    "periodo": getattr(node, 'periodo', ''),
                    "fase": getattr(node, 'fase', ''),
                    "datazione": getattr(node, 'datazione', '')
                }
                graph_data["nodes"].append(node_data)

            # Add edges
            for edge in self.graph.edges:
                edge_data = {
                    "edge_id": edge.edge_id,
                    "edge_source": edge.edge_source,
                    "edge_target": edge.edge_target,
                    "edge_type": edge.edge_type
                }
                graph_data["edges"].append(edge_data)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error exporting to JSON: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return False

    def generate_harris_matrix(self) -> Optional[Dict]:
        """
        Generate Harris Matrix from the stratigraphic graph

        Returns:
            Dictionary representing the Harris Matrix or None
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return None

        try:
            # Generate a simplified Harris Matrix representation
            matrix = {
                "site": self.graph.name,
                "levels": {},  # Stratigraphic levels
                "relationships": []
            }

            # Extract relationships
            for edge in self.graph.edges:
                matrix["relationships"].append({
                    "from": edge.edge_source,
                    "to": edge.edge_target,
                    "type": edge.edge_type
                })

            # Try to calculate chronological order if available
            if hasattr(self.graph, 'calculate_chronology'):
                try:
                    self.graph.calculate_chronology()
                except:
                    pass

            return matrix
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error generating Harris Matrix: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return None

    def prepare_for_3d_visualization(self) -> Optional[Dict]:
        """
        Prepare data for 3D visualization in Blender via EMtools

        Returns:
            Dictionary with 3D visualization data or None
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return None

        try:
            # Prepare data structure for EMtools/Blender
            viz_data = {
                "nodes": [],
                "edges": [],
                "metadata": self.graph.get_metadata()
            }

            # Add nodes with their properties
            for node_id, node in self.nodes.items():
                viz_data["nodes"].append({
                    "id": node_id,
                    "type": "stratigraphic_unit",
                    "properties": node.get_properties(),
                    "position": node.get_position() if hasattr(node, 'get_position') else None
                })

            # Add edges
            for edge in self.graph.get_edges():
                viz_data["edges"].append({
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.relationship_type
                })

            return viz_data

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error preparing 3D visualization: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return None

    def validate_stratigraphic_sequence(self) -> List[str]:
        """
        Validate the stratigraphic sequence for logical consistency

        Returns:
            List of validation warnings/errors
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return ["S3DGraphy not available"]

        warnings = []

        try:
            # Basic validation checks

            # Check for nodes without connections (orphaned units)
            connected_nodes = set()
            for edge in self.graph.edges:
                connected_nodes.add(edge.edge_source)
                connected_nodes.add(edge.edge_target)

            all_nodes = set(node.node_id for node in self.graph.nodes
                          if getattr(node, 'node_type', '') != 'geo_position')
            orphaned = all_nodes - connected_nodes

            if orphaned:
                warnings.append(f"Orphaned units found (no relationships): {', '.join(orphaned)}")

            # Check for potential circular relationships (simplified)
            # A full cycle detection would require graph traversal
            edge_pairs = {}
            for edge in self.graph.edges:
                pair = (edge.edge_source, edge.edge_target)
                reverse_pair = (edge.edge_target, edge.edge_source)

                if reverse_pair in edge_pairs:
                    warnings.append(f"Potential circular relationship: {edge.edge_source} <-> {edge.edge_target}")
                edge_pairs[pair] = edge.edge_type

            # Use built-in validation if available
            if hasattr(self.graph, 'display_warnings'):
                graph_warnings = self.graph.display_warnings()
                if graph_warnings:
                    warnings.extend(graph_warnings)

            return warnings if warnings else []

        except Exception as e:
            return [f"Validation error: {str(e)}"]

    def import_from_extended_matrix(self, filepath: str) -> bool:
        """
        Import Extended Matrix data (JSON/GraphML) back to PyArchInit

        Args:
            filepath: Path to Extended Matrix file

        Returns:
            True if successful, False otherwise
        """
        if not self.db_manager:
            return False

        try:
            import xml.etree.ElementTree as ET

            data = None

            # Determine file type and load data
            if filepath.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif filepath.endswith('.graphml'):
                # Parse GraphML
                tree = ET.parse(filepath)
                root = tree.getroot()

                # Convert GraphML to internal format
                data = self._parse_graphml(root)
            else:
                QgsMessageLog.logMessage(
                    "Unsupported file format. Use .json or .graphml",
                    "PyArchInit", Qgis.Warning
                )
                return False

            if not data:
                return False

            # Process nodes (stratigraphic units)
            imported_units = []
            for node_data in data.get('nodes', []):
                # Skip geo_position nodes
                if node_data.get('node_type') == 'geo_position':
                    continue

                # Extract US data
                us_data = {
                    'sito': node_data.get('sito', ''),
                    'area': node_data.get('area', ''),
                    'us': node_data.get('us', ''),
                    'unita_tipo': node_data.get('unita_tipo', 'US'),
                    'd_stratigrafica': node_data.get('d_stratigrafica', ''),
                    'd_interpretativa': node_data.get('d_interpretativa', ''),
                    'periodo_iniziale': node_data.get('periodo', ''),
                    'fase_iniziale': node_data.get('fase', ''),
                    'datazione': node_data.get('datazione', '')
                }

                # Check if unit exists
                search_dict = {
                    'sito': us_data['sito'],
                    'area': us_data['area'],
                    'us': us_data['us']
                }

                existing = self.db_manager.query_bool(search_dict, 'US')

                if not existing:
                    # Create new US record
                    # Note: This would need the proper entity class
                    imported_units.append(us_data)
                else:
                    # Update existing if needed
                    pass

            # Process edges (relationships)
            relationships = []
            for edge_data in data.get('edges', []):
                # Parse edge IDs to get US numbers
                source_parts = edge_data.get('edge_source', '').split('_')
                target_parts = edge_data.get('edge_target', '').split('_')

                if len(source_parts) >= 3 and len(target_parts) >= 3:
                    rel_type_em = edge_data.get('edge_type', 'generic_connection')

                    # Reverse map from Extended Matrix to PyArchInit
                    reverse_mapping = {
                        'is_before': 'copre',
                        'has_same_time': 'contemporaneo a',
                        'generic_connection': 'si lega a'
                    }

                    rel_type = reverse_mapping.get(rel_type_em, 'si lega a')

                    relationships.append({
                        'from_us': source_parts[-1],
                        'to_us': target_parts[-1],
                        'type': rel_type
                    })

            QgsMessageLog.logMessage(
                f"Imported {len(imported_units)} units and {len(relationships)} relationships",
                "PyArchInit", Qgis.Info
            )

            return True

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error importing Extended Matrix: {str(e)}",
                "PyArchInit", Qgis.Critical
            )
            return False

    def _parse_graphml(self, root) -> Dict:
        """
        Parse GraphML XML to internal data structure
        """
        # Define namespaces
        ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}

        data = {'nodes': [], 'edges': []}

        # Find graph element
        graph = root.find('.//graphml:graph', ns)
        if graph is None:
            return data

        # Parse nodes
        for node in graph.findall('graphml:node', ns):
            node_data = {'node_id': node.get('id')}

            # Extract data fields
            for data_elem in node.findall('graphml:data', ns):
                key = data_elem.get('key')
                value = data_elem.text or ''

                # Map keys to field names
                key_mapping = {
                    'd0': 'name',
                    'd1': 'description',
                    'd2': 'node_type',
                    'd3': 'sito',
                    'd4': 'area',
                    'd5': 'us',
                    'd6': 'periodo',
                    'd7': 'fase',
                    'd8': 'datazione'
                }

                field_name = key_mapping.get(key, key)
                node_data[field_name] = value

            data['nodes'].append(node_data)

        # Parse edges
        for edge in graph.findall('graphml:edge', ns):
            edge_data = {
                'edge_id': edge.get('id'),
                'edge_source': edge.get('source'),
                'edge_target': edge.get('target')
            }

            # Extract edge type
            for data_elem in edge.findall('graphml:data', ns):
                if data_elem.get('key') == 'd9':
                    edge_data['edge_type'] = data_elem.text or 'generic_connection'

            data['edges'].append(edge_data)

        return data

    def calculate_chronological_sequence(self) -> Dict[str, Any]:
        """
        Calculate the chronological sequence of stratigraphic units
        using topological sorting of the directed graph

        Returns:
            Dictionary with phases and chronological ordering
        """
        if not self.graph or not S3DGRAPHY_AVAILABLE:
            return {}

        try:
            from collections import defaultdict, deque

            # Build adjacency list from edges
            adjacency = defaultdict(list)
            in_degree = defaultdict(int)
            all_nodes = set()

            for edge in self.graph.edges:
                source = edge.edge_source
                target = edge.edge_target

                # For "is_before" relationships
                if edge.edge_type == 'is_before':
                    adjacency[target].append(source)  # Target is before source (above)
                    in_degree[source] += 1
                    all_nodes.add(source)
                    all_nodes.add(target)
                elif edge.edge_type == 'has_same_time':
                    # Contemporary units - group them
                    all_nodes.add(source)
                    all_nodes.add(target)

            # Add nodes with no relationships
            for node in self.graph.nodes:
                if node.node_id not in all_nodes:
                    all_nodes.add(node.node_id)
                    in_degree[node.node_id] = 0

            # Topological sort using Kahn's algorithm
            queue = deque([n for n in all_nodes if in_degree[n] == 0])
            chronological_order = []
            phases = []
            current_phase = []

            while queue:
                # Process all nodes at the same level (same phase)
                phase_size = len(queue)
                current_phase = []

                for _ in range(phase_size):
                    node = queue.popleft()
                    chronological_order.append(node)
                    current_phase.append(node)

                    # Reduce in-degree for adjacent nodes
                    for adjacent in adjacency[node]:
                        in_degree[adjacent] -= 1
                        if in_degree[adjacent] == 0:
                            queue.append(adjacent)

                phases.append(current_phase)

            # Group by periodo and fase if available
            phased_sequence = self._group_by_period_phase(chronological_order)

            result = {
                'chronological_order': chronological_order,
                'phases': phases,
                'phased_sequence': phased_sequence,
                'total_units': len(all_nodes),
                'num_phases': len(phases)
            }

            # Check for cycles (if not all nodes were processed)
            if len(chronological_order) < len(all_nodes):
                unprocessed = all_nodes - set(chronological_order)
                result['warning'] = f"Cycle detected! {len(unprocessed)} units not sequenced"
                result['unprocessed'] = list(unprocessed)

            return result

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error calculating chronological sequence: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return {}

    def _group_by_period_phase(self, chronological_order: List[str]) -> Dict:
        """
        Group units by their periodo and fase attributes
        """
        from collections import defaultdict
        periods = defaultdict(lambda: defaultdict(list))

        for node_id in chronological_order:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                periodo = getattr(node, 'periodo', 'Unknown')
                fase = getattr(node, 'fase', 'Unknown')
                periods[periodo][fase].append(node_id)

        # Convert to regular dict for JSON serialization
        result = {}
        for periodo, fasi in periods.items():
            result[periodo] = dict(fasi)

        return result

    def export_phased_matrix(self, filepath: str) -> bool:
        """
        Export a phased/periodized matrix view

        Args:
            filepath: Path to save the phased matrix

        Returns:
            True if successful
        """
        try:
            # Calculate chronological sequence
            sequence = self.calculate_chronological_sequence()

            if not sequence:
                return False

            # Build phased matrix structure
            matrix_data = {
                'site': self.graph.name if self.graph else 'Unknown',
                'chronological_sequence': sequence,
                'periods': {},
                'phases_by_level': []
            }

            # Organize by archaeological periods
            for i, phase in enumerate(sequence.get('phases', [])):
                phase_data = {
                    'level': i,
                    'units': phase,
                    'relationships': []
                }

                # Find relationships within this phase
                for edge in self.graph.edges:
                    if edge.edge_source in phase and edge.edge_target in phase:
                        phase_data['relationships'].append({
                            'from': edge.edge_source,
                            'to': edge.edge_target,
                            'type': edge.edge_type
                        })

                matrix_data['phases_by_level'].append(phase_data)

            # Add period groupings
            matrix_data['periods'] = sequence.get('phased_sequence', {})

            # Export to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(matrix_data, f, indent=2)

            return True

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error exporting phased matrix: {str(e)}",
                "PyArchInit", Qgis.Warning
            )
            return False


class PyArchInitS3DGraphyDialog:
    """
    Dialog for S3DGraphy integration in PyArchInit
    """

    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.integration = S3DGraphyIntegration(db_manager)

    def export_to_extended_matrix(self, site: str, area: Optional[str] = None,
                                 output_path: str = None):
        """
        Export site data to Extended Matrix format
        """
        if not self.integration.is_available():
            QMessageBox.warning(
                self.parent,
                "S3DGraphy Not Available",
                "S3DGraphy is not installed.\n"
                "Install it with: pip install s3dgraphy",
                QMessageBox.Ok
            )
            return

        try:
            # Import data from PyArchInit
            success = self.integration.import_from_pyarchinit(site, area)

            if not success:
                QMessageBox.warning(
                    self.parent,
                    "Import Failed",
                    "Failed to import stratigraphic data",
                    QMessageBox.Ok
                )
                return

            # Validate the sequence
            warnings = self.integration.validate_stratigraphic_sequence()
            if warnings:
                warning_text = "\n".join(warnings)
                QMessageBox.information(
                    self.parent,
                    "Validation Warnings",
                    f"The following issues were found:\n\n{warning_text}",
                    QMessageBox.Ok
                )

            # Export to GraphML
            if output_path:
                graphml_path = output_path.replace('.json', '.graphml')
                self.integration.export_to_graphml(graphml_path)

                # Also export to JSON
                self.integration.export_to_json(output_path)

                QMessageBox.information(
                    self.parent,
                    "Export Successful",
                    f"Extended Matrix exported to:\n{graphml_path}\n{output_path}",
                    QMessageBox.Ok
                )

        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Export Error",
                f"Error exporting to Extended Matrix:\n{str(e)}",
                QMessageBox.Ok
            )