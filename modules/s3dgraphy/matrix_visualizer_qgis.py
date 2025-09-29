#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QGIS visualization for S3DGraphy Extended Matrix
Creates a visual representation of the stratigraphic matrix in QGIS canvas
"""

from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsFields, QgsProject, QgsLineString,
    QgsWkbTypes, QgsVectorDataProvider, QgsMarkerSymbol,
    QgsLineSymbol, QgsSingleSymbolRenderer, QgsRuleBasedRenderer,
    QgsSymbol, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling,
    QgsSimpleFillSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleLineSymbolLayer
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont
import math
from typing import Dict, List, Tuple, Optional


class MatrixVisualizerQGIS:
    """
    Creates a visual representation of the Extended Matrix in QGIS
    """

    def __init__(self, iface=None):
        self.iface = iface
        self.node_positions = {}
        self.layers = {}

    def visualize_extended_matrix(self, graph_data: Dict, chronological_sequence: Dict = None) -> Dict:
        """
        Create QGIS layers to visualize the Extended Matrix

        Args:
            graph_data: Extended Matrix data
            chronological_sequence: Optional chronological ordering

        Returns:
            Dictionary of created layers
        """
        try:
            # Create layers
            nodes_layer = self._create_nodes_layer(graph_data, chronological_sequence)
            edges_layer = self._create_edges_layer(graph_data)
            labels_layer = self._create_labels_layer(graph_data)

            # Group layers
            root = QgsProject.instance().layerTreeRoot()
            matrix_group = root.addGroup("Extended Matrix Visualization")

            # Add layers to project and group
            QgsProject.instance().addMapLayer(edges_layer, False)
            QgsProject.instance().addMapLayer(nodes_layer, False)
            QgsProject.instance().addMapLayer(labels_layer, False)

            matrix_group.addLayer(labels_layer)
            matrix_group.addLayer(nodes_layer)
            matrix_group.addLayer(edges_layer)

            self.layers = {
                'nodes': nodes_layer,
                'edges': edges_layer,
                'labels': labels_layer
            }

            # Zoom to extent
            if self.iface:
                canvas = self.iface.mapCanvas()
                canvas.setExtent(nodes_layer.extent())
                canvas.refresh()

            return self.layers

        except Exception as e:
            print(f"Error creating visualization: {str(e)}")
            return {}

    def _create_nodes_layer(self, graph_data: Dict, chronological_sequence: Dict = None) -> QgsVectorLayer:
        """
        Create a point layer for nodes
        """
        # Create layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "Extended Matrix - Nodes", "memory")
        provider = layer.dataProvider()

        # Add fields
        fields = QgsFields()
        fields.append(QgsField("node_id", QVariant.String))
        fields.append(QgsField("name", QVariant.String))
        fields.append(QgsField("node_type", QVariant.String))
        fields.append(QgsField("unita_tipo", QVariant.String))
        fields.append(QgsField("sito", QVariant.String))
        fields.append(QgsField("area", QVariant.String))
        fields.append(QgsField("us", QVariant.String))
        fields.append(QgsField("periodo", QVariant.String))
        fields.append(QgsField("fase", QVariant.String))
        fields.append(QgsField("level", QVariant.Int))
        fields.append(QgsField("is_virtual", QVariant.Bool))
        provider.addAttributes(fields)
        layer.updateFields()

        # Calculate positions using chronological sequence or default layout
        if chronological_sequence and 'phases' in chronological_sequence:
            self._calculate_phased_positions(graph_data, chronological_sequence)
        else:
            self._calculate_default_positions(graph_data)

        # Add features
        features = []
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')

            if node_id in self.node_positions:
                x, y = self.node_positions[node_id]

                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
                feature.setAttributes([
                    node_id,
                    node.get('name', ''),
                    node.get('node_type', ''),
                    node.get('unita_tipo', ''),
                    node.get('sito', ''),
                    node.get('area', ''),
                    node.get('us', ''),
                    node.get('periodo', ''),
                    node.get('fase', ''),
                    self.node_positions.get(node_id + '_level', 0),
                    node.get('node_type') == 'virtual_reconstruction'
                ])
                features.append(feature)

        provider.addFeatures(features)

        # Apply symbology
        self._apply_node_symbology(layer)

        return layer

    def _create_edges_layer(self, graph_data: Dict) -> QgsVectorLayer:
        """
        Create a line layer for edges (relationships)
        """
        layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Extended Matrix - Relationships", "memory")
        provider = layer.dataProvider()

        # Add fields
        fields = QgsFields()
        fields.append(QgsField("edge_id", QVariant.String))
        fields.append(QgsField("source", QVariant.String))
        fields.append(QgsField("target", QVariant.String))
        fields.append(QgsField("edge_type", QVariant.String))
        provider.addAttributes(fields)
        layer.updateFields()

        # Add features
        features = []
        for edge in graph_data.get('edges', []):
            source_id = edge.get('edge_source', '')
            target_id = edge.get('edge_target', '')

            if source_id in self.node_positions and target_id in self.node_positions:
                source_pos = self.node_positions[source_id]
                target_pos = self.node_positions[target_id]

                # Create line geometry
                line = QgsLineString([
                    QgsPointXY(source_pos[0], source_pos[1]),
                    QgsPointXY(target_pos[0], target_pos[1])
                ])

                feature = QgsFeature()
                feature.setGeometry(QgsGeometry(line))
                feature.setAttributes([
                    edge.get('edge_id', ''),
                    source_id,
                    target_id,
                    edge.get('edge_type', '')
                ])
                features.append(feature)

        provider.addFeatures(features)

        # Apply symbology
        self._apply_edge_symbology(layer)

        return layer

    def _create_labels_layer(self, graph_data: Dict) -> QgsVectorLayer:
        """
        Create a layer for labels
        """
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "Extended Matrix - Labels", "memory")
        provider = layer.dataProvider()

        # Add fields
        fields = QgsFields()
        fields.append(QgsField("label", QVariant.String))
        fields.append(QgsField("node_type", QVariant.String))
        provider.addAttributes(fields)
        layer.updateFields()

        # Add features
        features = []
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')

            if node_id in self.node_positions:
                x, y = self.node_positions[node_id]

                feature = QgsFeature()
                # Offset label slightly
                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y + 0.0001)))
                feature.setAttributes([
                    node.get('name', node.get('us', '')),
                    node.get('node_type', '')
                ])
                features.append(feature)

        provider.addFeatures(features)

        # Enable labels
        self._apply_label_settings(layer)

        return layer

    def _calculate_phased_positions(self, graph_data: Dict, chronological_sequence: Dict):
        """
        Calculate node positions based on chronological phases
        """
        phases = chronological_sequence.get('phases', [])

        for level, phase_nodes in enumerate(phases):
            num_nodes = len(phase_nodes)
            for i, node_id in enumerate(phase_nodes):
                # Arrange nodes horizontally within each phase
                x = (i - num_nodes / 2) * 0.001  # Spacing
                y = -level * 0.002  # Vertical spacing by phase
                self.node_positions[node_id] = (x, y)
                self.node_positions[node_id + '_level'] = level

    def _calculate_default_positions(self, graph_data: Dict):
        """
        Calculate default circular layout for nodes
        """
        nodes = graph_data.get('nodes', [])
        num_nodes = len(nodes)

        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / num_nodes
            x = 0.01 * math.cos(angle)
            y = 0.01 * math.sin(angle)
            self.node_positions[node.get('node_id', '')] = (x, y)
            self.node_positions[node.get('node_id', '') + '_level'] = 0

    def _apply_node_symbology(self, layer: QgsVectorLayer):
        """
        Apply rule-based symbology to nodes based on type
        """
        # Create rules for different node types
        root_rule = QgsRuleBasedRenderer.Rule(None)

        # Regular stratigraphic units
        symbol_us = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '#4CAF50',
            'outline_color': '#2E7D32',
            'size': '4'
        })
        rule_us = QgsRuleBasedRenderer.Rule(symbol_us)
        rule_us.setFilterExpression('"node_type" = \'stratigraphic_unit\'')
        rule_us.setLabel('Stratigraphic Unit')
        root_rule.appendChild(rule_us)

        # Masonry units
        symbol_usm = QgsMarkerSymbol.createSimple({
            'name': 'square',
            'color': '#FF9800',
            'outline_color': '#E65100',
            'size': '4'
        })
        rule_usm = QgsRuleBasedRenderer.Rule(symbol_usm)
        rule_usm.setFilterExpression('"node_type" = \'masonry_unit\'')
        rule_usm.setLabel('Masonry Unit')
        root_rule.appendChild(rule_usm)

        # Virtual reconstructions
        symbol_vr = QgsMarkerSymbol.createSimple({
            'name': 'diamond',
            'color': '#9C27B0',
            'outline_color': '#4A148C',
            'size': '5'
        })
        rule_vr = QgsRuleBasedRenderer.Rule(symbol_vr)
        rule_vr.setFilterExpression('"is_virtual" = true')
        rule_vr.setLabel('Virtual Reconstruction')
        root_rule.appendChild(rule_vr)

        renderer = QgsRuleBasedRenderer(root_rule)
        layer.setRenderer(renderer)

    def _apply_edge_symbology(self, layer: QgsVectorLayer):
        """
        Apply symbology to edges based on relationship type
        """
        root_rule = QgsRuleBasedRenderer.Rule(None)

        # Temporal relationships (is_before)
        symbol_before = QgsLineSymbol.createSimple({
            'color': '#2196F3',
            'width': '0.5',
            'line_style': 'solid'
        })
        rule_before = QgsRuleBasedRenderer.Rule(symbol_before)
        rule_before.setFilterExpression('"edge_type" = \'is_before\'')
        rule_before.setLabel('Is Before')
        root_rule.appendChild(rule_before)

        # Contemporary relationships
        symbol_contemporary = QgsLineSymbol.createSimple({
            'color': '#4CAF50',
            'width': '0.5',
            'line_style': 'dash'
        })
        rule_contemporary = QgsRuleBasedRenderer.Rule(symbol_contemporary)
        rule_contemporary.setFilterExpression('"edge_type" = \'has_same_time\'')
        rule_contemporary.setLabel('Contemporary')
        root_rule.appendChild(rule_contemporary)

        # Generic relationships
        symbol_generic = QgsLineSymbol.createSimple({
            'color': '#9E9E9E',
            'width': '0.3',
            'line_style': 'dot'
        })
        rule_generic = QgsRuleBasedRenderer.Rule(symbol_generic)
        rule_generic.setFilterExpression('"edge_type" = \'generic_connection\'')
        rule_generic.setLabel('Generic Connection')
        root_rule.appendChild(rule_generic)

        renderer = QgsRuleBasedRenderer(root_rule)
        layer.setRenderer(renderer)

    def _apply_label_settings(self, layer: QgsVectorLayer):
        """
        Configure label settings for the layer
        """
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = 'label'
        label_settings.enabled = True

        text_format = QgsTextFormat()
        text_format.setSize(10)
        text_format.setColor(QColor('#000000'))
        font = QFont('Arial', 10)
        font.setBold(True)
        text_format.setFont(font)
        label_settings.setFormat(text_format)

        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)