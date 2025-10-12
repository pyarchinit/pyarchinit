#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GraphML Spatial Enhancer
Enhances GraphML export with spatial/functional groupings for yEd
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional


class GraphMLSpatialEnhancer:
    """
    Enhances GraphML files with spatial/functional grouping information
    compatible with yEd's group nodes
    """
    
    def __init__(self):
        self.ns = {
            'graphml': 'http://graphml.graphdrawing.org/xmlns',
            'y': 'http://www.yworks.com/xml/graphml'
        }
        
    def enhance_graphml_with_groups(self, graphml_file: str, groupings: Dict[str, List[str]], 
                                   output_file: Optional[str] = None):
        """
        Enhance GraphML file with group nodes for spatial/functional groupings
        
        Args:
            graphml_file: Path to input GraphML file
            groupings: Dictionary of group_name -> list of node IDs
            output_file: Optional output path (overwrites input if None)
        """
        if output_file is None:
            output_file = graphml_file
            
        # Parse the GraphML file
        tree = ET.parse(graphml_file)
        root = tree.getroot()
        
        # Register namespaces
        for prefix, uri in self.ns.items():
            ET.register_namespace(prefix, uri)
        
        # Find the graph element
        graph = root.find('.//graphml:graph', self.ns)
        if graph is None:
            print("No graph element found in GraphML")
            return
        
        # Create a mapping of node labels to node elements
        node_map = {}
        for node in graph.findall('graphml:node', self.ns):
            node_id = node.get('id')
            # Try to extract the original US ID from the node
            # This depends on how nodes are labeled in the GraphML
            for data in node.findall('graphml:data', self.ns):
                if data.get('key') == 'd0':  # Assuming d0 is the name/label key
                    label = data.text or ''
                    node_map[label] = node
                    break
        
        # Create group nodes for each grouping
        group_id_counter = 1000  # Start group IDs from a high number to avoid conflicts
        
        for group_name, node_ids in groupings.items():
            # Create a group node
            group_id = f"group_{group_id_counter}"
            group_id_counter += 1
            
            group_node = ET.SubElement(graph, 'node')
            group_node.set('id', group_id)
            group_node.set('yfiles.foldertype', 'group')
            
            # Add group visual properties
            data = ET.SubElement(group_node, 'data')
            data.set('key', 'd6')  # Assuming d6 is the graphics key
            
            # Create ProxyAutoBoundsNode for yEd group
            proxy_node = ET.SubElement(data, 'y:ProxyAutoBoundsNode')
            
            # Realizers
            realizers = ET.SubElement(proxy_node, 'y:Realizers')
            realizers.set('active', '0')
            
            # Group node realizer
            group_realizer = ET.SubElement(realizers, 'y:GroupNode')
            
            # Geometry (will be auto-calculated by yEd)
            geom = ET.SubElement(group_realizer, 'y:Geometry')
            geom.set('height', '200.0')
            geom.set('width', '300.0')
            geom.set('x', '0.0')
            geom.set('y', '0.0')
            
            # Fill
            fill = ET.SubElement(group_realizer, 'y:Fill')
            fill.set('color', '#E8EEF7')
            fill.set('color2', '#B7C9E3')
            fill.set('transparent', 'false')
            
            # Border
            border = ET.SubElement(group_realizer, 'y:BorderStyle')
            border.set('color', '#000000')
            border.set('type', 'line')
            border.set('width', '1.0')
            
            # Label
            label = ET.SubElement(group_realizer, 'y:NodeLabel')
            label.set('alignment', 'right')
            label.set('autoSizePolicy', 'node_width')
            label.set('backgroundColor', '#EBEBEB')
            label.set('borderDistance', '0.0')
            label.set('fontFamily', 'Dialog')
            label.set('fontSize', '15')
            label.set('fontStyle', 'plain')
            label.set('hasLineColor', 'false')
            label.set('height', '25.0')
            label.set('horizontalTextPosition', 'center')
            label.set('iconTextGap', '0')
            label.set('modelName', 'internal')
            label.set('modelPosition', 't')
            label.set('textColor', '#000000')
            label.set('visible', 'true')
            label.text = group_name
            
            # Shape
            shape = ET.SubElement(group_realizer, 'y:Shape')
            shape.set('type', 'roundrectangle')
            
            # State
            state = ET.SubElement(group_realizer, 'y:State')
            state.set('closed', 'false')
            state.set('closedHeight', '80.0')
            state.set('closedWidth', '100.0')
            state.set('innerGraphDisplayEnabled', 'false')
            
            # Insets
            insets = ET.SubElement(group_realizer, 'y:Insets')
            insets.set('bottom', '15')
            insets.set('bottomF', '15.0')
            insets.set('left', '15')
            insets.set('leftF', '15.0')
            insets.set('right', '15')
            insets.set('rightF', '15.0')
            insets.set('top', '15')
            insets.set('topF', '15.0')
            
            # Border insets
            border_insets = ET.SubElement(group_realizer, 'y:BorderInsets')
            border_insets.set('bottom', '0')
            border_insets.set('bottomF', '0.0')
            border_insets.set('left', '0')
            border_insets.set('leftF', '0.0')
            border_insets.set('right', '0')
            border_insets.set('rightF', '0.0')
            border_insets.set('top', '0')
            border_insets.set('topF', '0.0')
            
            # Find nodes that belong to this group and update them
            # This needs to match the node IDs with the grouping IDs
            for node_id in node_ids:
                # Try different formats to match nodes
                possible_matches = [
                    node_id,
                    node_id.split('_')[-1],  # Just the US number
                    f"US{node_id.split('_')[-1]}",  # With US prefix
                    f"n0::n{node_id}"  # yEd format
                ]
                
                for match in possible_matches:
                    if match in node_map:
                        node = node_map[match]
                        # Update node to be part of the group
                        # In yEd, this is done by making the node a child of the group
                        graph.remove(node)
                        graph_elem = group_node.find('.//y:Graph')
                        if graph_elem is None:
                            # Create graph element inside group
                            graph_elem = ET.SubElement(group_realizer, 'y:Graph')
                            graph_elem.set('id', f"{group_id}:")
                        # Re-add node as child of group's graph
                        graph_elem.append(node)
                        break
        
        # Write the enhanced GraphML
        tree.write(output_file, encoding='UTF-8', xml_declaration=True)
        
        # Pretty print for better readability
        self._pretty_print_xml(output_file)
    
    def _pretty_print_xml(self, file_path: str):
        """Pretty print XML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            rough_string = f.read()
        
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent='  ', encoding='UTF-8')
        
        with open(file_path, 'wb') as f:
            f.write(pretty_xml)
    
    def create_hierarchical_groups(self, graphml_file: str, hierarchy: Dict[str, Dict[str, List[str]]],
                                  output_file: Optional[str] = None):
        """
        Create hierarchical groups (e.g., Area -> Settore -> US)
        
        Args:
            graphml_file: Input GraphML file
            hierarchy: Nested dictionary of groupings
            output_file: Output file path
        """
        # This is a more complex version that creates nested groups
        # For now, we'll use the flat grouping approach
        pass