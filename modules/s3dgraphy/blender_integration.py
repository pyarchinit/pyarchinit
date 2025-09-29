#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Blender integration for PyArchInit Extended Matrix
Allows 3D visualization of stratigraphic sequences in Blender
"""

import os
import json
import socket
import tempfile
from typing import Dict, Optional, List


class BlenderIntegration:
    """
    Integrates PyArchInit with Blender for 3D stratigraphic visualization
    """

    def __init__(self):
        self.host = 'localhost'
        self.port = 8765  # Default port for Blender addon
        self.socket = None

    def is_blender_connected(self) -> bool:
        """
        Check if Blender is running with PyArchInit addon
        """
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            result = test_socket.connect_ex((self.host, self.port))
            test_socket.close()
            return result == 0
        except:
            return False

    def send_to_blender(self, data: Dict) -> bool:
        """
        Send Extended Matrix data to Blender for 3D visualization
        """
        try:
            if not self.is_blender_connected():
                print("Blender not connected. Make sure Blender is running with PyArchInit addon.")
                return False

            # Prepare data for Blender
            blender_data = self._prepare_for_blender(data)

            # Send via socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                message = json.dumps(blender_data)
                s.sendall(message.encode('utf-8'))

                # Wait for response
                response = s.recv(1024)
                if response:
                    print(f"Blender response: {response.decode('utf-8')}")
                    return True

            return False

        except Exception as e:
            print(f"Error sending to Blender: {str(e)}")
            return False

    def _prepare_for_blender(self, matrix_data: Dict) -> Dict:
        """
        Prepare Extended Matrix data for Blender visualization
        """
        # Calculate 3D positions based on stratigraphy
        positions_3d = self._calculate_3d_positions(matrix_data)

        blender_data = {
            'type': 'extended_matrix',
            'action': 'create_stratigraphy',
            'data': {
                'nodes': [],
                'edges': [],
                'settings': {
                    'layer_height': 0.5,
                    'layer_spacing': 0.1,
                    'node_size': 1.0
                }
            }
        }

        # Process nodes
        for node in matrix_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node_id in positions_3d:
                x, y, z = positions_3d[node_id]

                blender_node = {
                    'id': node_id,
                    'name': node.get('name', node.get('us', '')),
                    'type': node.get('unita_tipo', 'US'),
                    'position': [x, y, z],
                    'color': self._get_color_for_type(node.get('unita_tipo', 'US')),
                    'metadata': {
                        'description': node.get('description', ''),
                        'sito': node.get('sito', ''),
                        'area': node.get('area', '')
                    }
                }
                blender_data['data']['nodes'].append(blender_node)

        # Process edges
        for edge in matrix_data.get('edges', []):
            blender_edge = {
                'source': edge.get('edge_source', ''),
                'target': edge.get('edge_target', ''),
                'type': edge.get('edge_type', ''),
                'color': self._get_edge_color(edge.get('edge_type', ''))
            }
            blender_data['data']['edges'].append(blender_edge)

        return blender_data

    def _calculate_3d_positions(self, matrix_data: Dict) -> Dict:
        """
        Calculate 3D positions for stratigraphic units
        """
        positions = {}
        levels = self._calculate_levels(matrix_data)

        # Group by level
        level_nodes = {}
        for node_id, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node_id)

        # Calculate positions
        for level, nodes in level_nodes.items():
            num_nodes = len(nodes)
            for i, node_id in enumerate(sorted(nodes)):
                # Arrange in circle at each level
                if num_nodes == 1:
                    x, y = 0, 0
                else:
                    import math
                    angle = 2 * math.pi * i / num_nodes
                    radius = min(5, num_nodes * 0.5)
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)

                z = -level * 2  # Stack vertically by stratigraphy
                positions[node_id] = (x, y, z)

        return positions

    def _calculate_levels(self, graph_data: Dict) -> Dict:
        """
        Calculate stratigraphic levels
        """
        levels = {}

        # Initialize
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node.get('node_type') != 'geo_position':
                levels[node_id] = 0

        # Process edges
        changed = True
        iterations = 0

        while changed and iterations < 50:
            changed = False
            iterations += 1

            for edge in graph_data.get('edges', []):
                source = edge.get('edge_source', '')
                target = edge.get('edge_target', '')
                edge_type = edge.get('edge_type', '')

                if source in levels and target in levels:
                    if edge_type == 'is_before':
                        new_level = levels[source] + 1
                        if levels[target] < new_level:
                            levels[target] = new_level
                            changed = True

        return levels

    def _get_color_for_type(self, unita_tipo: str) -> List[float]:
        """
        Get RGB color for unit type
        """
        colors = {
            'US': [0.3, 0.7, 0.3],   # Green
            'USM': [1.0, 0.6, 0.0],  # Orange
            'USF': [0.2, 0.5, 1.0],  # Blue
            'USD': [0.5, 0.3, 0.1],  # Brown
            'USR': [0.6, 0.2, 0.6],  # Purple
            'USN': [0.9, 0.1, 0.4],  # Pink
            'CON': [1.0, 0.6, 0.4],  # Salmon
            'SF': [0.9, 0.9, 0.5],   # Khaki
            'SU': [0.0, 0.7, 0.8]    # Cyan
        }
        return colors.get(unita_tipo, [0.5, 0.5, 0.5])

    def _get_edge_color(self, edge_type: str) -> List[float]:
        """
        Get RGB color for edge type
        """
        colors = {
            'is_before': [0.2, 0.5, 1.0],      # Blue
            'has_same_time': [0.3, 0.7, 0.3],  # Green
            'generic_connection': [0.5, 0.5, 0.5]  # Gray
        }
        return colors.get(edge_type, [0.5, 0.5, 0.5])

    def export_for_blender_addon(self, matrix_data: Dict, output_path: str) -> bool:
        """
        Export Extended Matrix data for manual import in Blender
        """
        try:
            blender_data = self._prepare_for_blender(matrix_data)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(blender_data, f, indent=2, ensure_ascii=False)

            print(f"Blender data exported to: {output_path}")
            return True

        except Exception as e:
            print(f"Error exporting for Blender: {str(e)}")
            return False


class BlenderAddonScript:
    """
    Generate Blender Python addon script for PyArchInit integration
    """

    @staticmethod
    def generate_addon() -> str:
        """
        Generate the Blender addon Python script
        """
        addon_script = '''# PyArchInit Blender Addon for Extended Matrix Visualization
# Save this as pyarchinit_extended_matrix.py in Blender's addon folder

bl_info = {
    "name": "PyArchInit Extended Matrix",
    "author": "PyArchInit Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > PyArchInit",
    "description": "Visualize archaeological stratigraphy from PyArchInit",
    "category": "3D View",
}

import bpy
import json
import socket
import threading
import mathutils
from bpy.props import StringProperty, BoolProperty, FloatProperty


class PYARCHINIT_OT_import_matrix(bpy.types.Operator):
    """Import Extended Matrix from PyArchInit"""
    bl_idname = "pyarchinit.import_matrix"
    bl_label = "Import Extended Matrix"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(
        name="File Path",
        description="Path to Extended Matrix JSON file",
        subtype='FILE_PATH'
    )

    def execute(self, context):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)

            self.create_stratigraphy(data)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}

    def create_stratigraphy(self, data):
        """Create 3D stratigraphy from Extended Matrix data"""

        # Create collection for stratigraphy
        collection = bpy.data.collections.new("Stratigraphy")
        bpy.context.scene.collection.children.link(collection)

        # Create materials for different unit types
        materials = self.create_materials()

        # Create nodes
        nodes = data.get('data', {}).get('nodes', [])
        for node in nodes:
            self.create_node(node, collection, materials)

        # Create edges
        edges = data.get('data', {}).get('edges', [])
        for edge in edges:
            self.create_edge(edge, collection)

    def create_materials(self):
        """Create materials for different unit types"""
        materials = {}

        unit_colors = {
            'US': (0.3, 0.7, 0.3, 1.0),   # Green
            'USM': (1.0, 0.6, 0.0, 1.0),  # Orange
            'USF': (0.2, 0.5, 1.0, 1.0),  # Blue
            'USD': (0.5, 0.3, 0.1, 1.0),  # Brown
            'USR': (0.6, 0.2, 0.6, 1.0),  # Purple
        }

        for unit_type, color in unit_colors.items():
            mat = bpy.data.materials.new(name=f"Mat_{unit_type}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            bsdf.inputs[0].default_value = color
            materials[unit_type] = mat

        return materials

    def create_node(self, node_data, collection, materials):
        """Create a node (stratigraphic unit) in 3D"""

        # Create mesh
        mesh = bpy.data.meshes.new(name=node_data['id'])
        obj = bpy.data.objects.new(node_data['name'], mesh)

        # Link to collection
        collection.objects.link(obj)

        # Create box geometry
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.primitive_cube_add(size=1)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Set position
        pos = node_data['position']
        obj.location = (pos[0], pos[1], pos[2])

        # Apply material
        unit_type = node_data.get('type', 'US')
        if unit_type in materials:
            obj.data.materials.append(materials[unit_type])

        # Add custom properties for metadata
        obj["us_id"] = node_data['id']
        obj["us_name"] = node_data['name']
        obj["us_type"] = unit_type

        metadata = node_data.get('metadata', {})
        for key, value in metadata.items():
            obj[f"us_{key}"] = value

    def create_edge(self, edge_data, collection):
        """Create edge (relationship) between nodes"""

        # Create curve
        curve = bpy.data.curves.new(name=f"Edge_{edge_data['source']}_{edge_data['target']}", type='CURVE')
        curve.dimensions = '3D'

        # Create spline
        spline = curve.splines.new('BEZIER')
        spline.bezier_points.add(1)  # We need 2 points total

        # Find source and target objects
        source_obj = None
        target_obj = None

        for obj in collection.objects:
            if obj.get("us_id") == edge_data['source']:
                source_obj = obj
            elif obj.get("us_id") == edge_data['target']:
                target_obj = obj

        if source_obj and target_obj:
            # Set curve points
            spline.bezier_points[0].co = source_obj.location
            spline.bezier_points[1].co = target_obj.location

            # Create curve object
            curve_obj = bpy.data.objects.new(f"Edge_{edge_data['source']}_{edge_data['target']}", curve)
            collection.objects.link(curve_obj)

            # Set edge color based on type
            edge_color = edge_data.get('color', [0.5, 0.5, 0.5])
            curve.materials.append(self.create_edge_material(edge_color))

    def create_edge_material(self, color):
        """Create material for edge"""
        mat = bpy.data.materials.new(name="Edge_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs[0].default_value = (*color, 1.0)
        return mat

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class PYARCHINIT_PT_main_panel(bpy.types.Panel):
    """PyArchInit panel in the 3D viewport"""
    bl_label = "PyArchInit Extended Matrix"
    bl_idname = "PYARCHINIT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyArchInit"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("pyarchinit.import_matrix")

        row = layout.row()
        row.prop(context.scene, "pyarchinit_server_port")

        row = layout.row()
        row.prop(context.scene, "pyarchinit_auto_update")


def register():
    bpy.utils.register_class(PYARCHINIT_OT_import_matrix)
    bpy.utils.register_class(PYARCHINIT_PT_main_panel)

    # Add properties
    bpy.types.Scene.pyarchinit_server_port = bpy.props.IntProperty(
        name="Server Port",
        default=8765,
        min=1024,
        max=65535
    )

    bpy.types.Scene.pyarchinit_auto_update = bpy.props.BoolProperty(
        name="Auto Update",
        default=False
    )


def unregister():
    bpy.utils.unregister_class(PYARCHINIT_OT_import_matrix)
    bpy.utils.unregister_class(PYARCHINIT_PT_main_panel)

    del bpy.types.Scene.pyarchinit_server_port
    del bpy.types.Scene.pyarchinit_auto_update


if __name__ == "__main__":
    register()
'''
        return addon_script

    @staticmethod
    def save_addon(output_path: str) -> bool:
        """
        Save the Blender addon script to file
        """
        try:
            script = BlenderAddonScript.generate_addon()
            with open(output_path, 'w') as f:
                f.write(script)
            print(f"Blender addon saved to: {output_path}")
            print("Install in Blender: Edit -> Preferences -> Add-ons -> Install...")
            return True
        except Exception as e:
            print(f"Error saving Blender addon: {str(e)}")
            return False