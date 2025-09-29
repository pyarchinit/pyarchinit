#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactive Plotly visualizer for Extended Matrix
Creates interactive graph that integrates with QGIS selection
"""

import os
import json
from typing import Dict, List, Optional, Tuple
import webbrowser
import tempfile

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from qgis.core import QgsProject, QgsExpression, QgsFeatureRequest
    from qgis.utils import iface
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class PlotlyMatrixVisualizer:
    """
    Creates interactive stratigraphic matrix visualization using Plotly
    """

    def __init__(self, qgis_integration=True):
        self.positions = {}
        self.levels = {}
        self.qgis_integration = qgis_integration and QGIS_AVAILABLE
        self.selected_nodes = []

    def create_interactive_graph(self, graph_data: Dict, output_path: str = None) -> bool:
        """
        Create interactive graph visualization with Plotly
        """
        if not PLOTLY_AVAILABLE:
            print("Plotly not available. Install with: pip install plotly")
            return False

        try:
            # Calculate hierarchy levels
            self._calculate_levels(graph_data)

            # Calculate positions
            self._calculate_positions(graph_data)

            # Create the plotly figure
            fig = go.Figure()

            # Add edges first (so they appear behind nodes)
            edge_trace = self._create_edge_traces(graph_data)
            for trace in edge_trace:
                fig.add_trace(trace)

            # Add nodes
            node_traces = self._create_node_traces(graph_data)
            for trace in node_traces:
                fig.add_trace(trace)

            # Update layout
            fig.update_layout(
                title={
                    'text': 'Extended Matrix - Interactive Stratigraphic Sequence',
                    'x': 0.5,
                    'xanchor': 'center'
                },
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=True, zeroline=False, gridcolor='lightgray'),
                plot_bgcolor='white',
                height=800,
                clickmode='event+select'
            )

            # Add interactivity for QGIS
            if self.qgis_integration:
                self._add_qgis_callbacks(fig, graph_data)

            # Save or show
            if output_path:
                if output_path.endswith('.html'):
                    fig.write_html(output_path)
                    print(f"Interactive graph saved to: {output_path}")
                else:
                    # Save as HTML and open in browser
                    html_path = output_path.replace('.png', '.html')
                    fig.write_html(html_path)
                    webbrowser.open('file://' + os.path.realpath(html_path))
                    print(f"Interactive graph opened in browser: {html_path}")
            else:
                fig.show()

            return True

        except Exception as e:
            print(f"Error creating interactive graph: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _calculate_levels(self, graph_data: Dict):
        """
        Calculate hierarchy levels using proper topological sorting
        """
        # Initialize nodes
        nodes = {}
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node.get('node_type') != 'geo_position':
                nodes[node_id] = node
                self.levels[node_id] = 0

        # Build dependency graph
        dependencies = {node_id: set() for node_id in nodes}
        dependents = {node_id: set() for node_id in nodes}

        for edge in graph_data.get('edges', []):
            source = edge.get('edge_source', '')
            target = edge.get('edge_target', '')
            edge_type = edge.get('edge_type', '')

            if source in nodes and target in nodes:
                if edge_type == 'is_before':
                    # Source is stratigraphically above target
                    dependencies[target].add(source)
                    dependents[source].add(target)

        # Calculate levels using Kahn's algorithm
        visited = set()
        max_level = 0

        # Find nodes with no dependencies (top nodes)
        queue = [node_id for node_id, deps in dependencies.items() if not deps]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue

            visited.add(current)

            # Update levels of dependent nodes
            for dependent in dependents[current]:
                self.levels[dependent] = max(self.levels[dependent], self.levels[current] + 1)
                max_level = max(max_level, self.levels[dependent])

                # Check if all dependencies of dependent are visited
                if dependencies[dependent].issubset(visited):
                    queue.append(dependent)

        # Handle nodes not connected by is_before relationships
        for node_id in nodes:
            if node_id not in visited:
                # Place unconnected nodes at bottom
                self.levels[node_id] = max_level + 1

        print(f"Calculated {len(self.levels)} levels:")
        for level in range(max_level + 2):
            nodes_at_level = [nid for nid, lvl in self.levels.items() if lvl == level]
            if nodes_at_level:
                print(f"  Level {level}: {', '.join(nodes_at_level[:5])}")
                if len(nodes_at_level) > 5:
                    print(f"    ... and {len(nodes_at_level) - 5} more")

    def _calculate_positions(self, graph_data: Dict):
        """
        Calculate node positions for visualization
        """
        # Group nodes by level
        level_nodes = {}
        for node_id, level in self.levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node_id)

        # Position nodes
        max_width = max(len(nodes) for nodes in level_nodes.values()) if level_nodes else 1

        for level, nodes in level_nodes.items():
            num_nodes = len(nodes)
            for i, node_id in enumerate(sorted(nodes)):
                # Spread nodes horizontally
                if num_nodes == 1:
                    x = 0
                else:
                    # Scale based on max width to prevent overlap
                    spread = min(10, max_width * 1.5)
                    x = (i - (num_nodes - 1) / 2) * spread / max(num_nodes - 1, 1)

                y = -level * 2  # Negative so top is higher
                self.positions[node_id] = (x, y)

    def _create_node_traces(self, graph_data: Dict) -> List:
        """
        Create node traces grouped by unit type
        """
        traces = []

        # Group nodes by unit type
        nodes_by_type = {}
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node_id not in self.positions:
                continue

            unita_tipo = node.get('unita_tipo', 'US')
            if unita_tipo not in nodes_by_type:
                nodes_by_type[unita_tipo] = []
            nodes_by_type[unita_tipo].append(node)

        # Color mapping
        color_map = {
            'US': '#4CAF50',   # Green
            'USM': '#FF9800',  # Orange
            'USF': '#2196F3',  # Blue
            'USD': '#795548',  # Brown
            'USR': '#9C27B0',  # Purple
            'CON': '#FFA07A',  # Light salmon
            'SF': '#F0E68C',   # Khaki
            'USN': '#E91E63',  # Pink
            'SU': '#00BCD4',   # Cyan
            'virtual_reconstruction': '#FF5722'  # Deep orange
        }

        # Create trace for each unit type
        for unita_tipo, nodes in nodes_by_type.items():
            x_vals = []
            y_vals = []
            text_vals = []
            customdata = []

            for node in nodes:
                node_id = node.get('node_id', '')
                x, y = self.positions[node_id]
                x_vals.append(x)
                y_vals.append(y)

                # Create hover text
                label = node.get('name', node.get('us', ''))
                description = node.get('description', node.get('d_stratigrafica', ''))
                sito = node.get('sito', '')
                area = node.get('area', '')

                hover_text = f"<b>{label}</b>"
                if description:
                    hover_text += f"<br>{description[:60]}"
                if sito and area:
                    hover_text += f"<br>Site: {sito}, Area: {area}"

                text_vals.append(hover_text)
                customdata.append(node_id)

            # Create node trace
            trace = go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers+text',
                name=f'{unita_tipo} Units',
                text=[n.get('name', n.get('us', '')) for n in nodes],
                textposition='middle center',
                textfont=dict(size=10, color='white'),
                hovertext=text_vals,
                hoverinfo='text',
                customdata=customdata,
                marker=dict(
                    size=40,
                    color=color_map.get(unita_tipo, '#9E9E9E'),
                    line=dict(width=2, color='black')
                )
            )
            traces.append(trace)

        return traces

    def _create_edge_traces(self, graph_data: Dict) -> List:
        """
        Create edge traces grouped by relationship type
        """
        traces = []

        # Group edges by type
        edges_by_type = {}
        for edge in graph_data.get('edges', []):
            edge_type = edge.get('edge_type', '')
            if edge_type not in edges_by_type:
                edges_by_type[edge_type] = []
            edges_by_type[edge_type].append(edge)

        # Style mapping
        style_map = {
            'is_before': {'color': '#2196F3', 'width': 2, 'dash': 'solid', 'name': 'Stratigraphic'},
            'has_same_time': {'color': '#4CAF50', 'width': 2, 'dash': 'dash', 'name': 'Contemporary'},
            'generic_connection': {'color': '#9E9E9E', 'width': 1, 'dash': 'dot', 'name': 'Generic'}
        }

        # Create trace for each edge type
        for edge_type, edges in edges_by_type.items():
            x_vals = []
            y_vals = []

            style = style_map.get(edge_type, style_map['generic_connection'])

            for edge in edges:
                source = edge.get('edge_source', '')
                target = edge.get('edge_target', '')

                if source in self.positions and target in self.positions:
                    x1, y1 = self.positions[source]
                    x2, y2 = self.positions[target]

                    # Add edge line
                    x_vals.extend([x1, x2, None])
                    y_vals.extend([y1, y2, None])

            if x_vals:
                trace = go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines',
                    name=style['name'],
                    line=dict(
                        color=style['color'],
                        width=style['width'],
                        dash=style['dash']
                    ),
                    hoverinfo='skip'
                )
                traces.append(trace)

        return traces

    def _add_qgis_callbacks(self, fig, graph_data):
        """
        Add QGIS integration callbacks
        """
        if not QGIS_AVAILABLE:
            return

        # Create JavaScript for node click handling
        js_callback = """
        <script>
        // This would need to be implemented with a proper bridge
        // For now, we'll save selection to a file that QGIS can monitor
        function selectInQGIS(nodeId) {
            console.log('Selected node:', nodeId);
            // Write selection to temp file
            fetch('/select_node', {
                method: 'POST',
                body: JSON.stringify({node_id: nodeId})
            });
        }
        </script>
        """

        # For now, we'll use a simpler approach with file monitoring
        self._setup_selection_monitor(graph_data)

    def _setup_selection_monitor(self, graph_data):
        """
        Setup monitoring for QGIS selection synchronization
        """
        # Save node mapping for QGIS integration
        temp_dir = tempfile.gettempdir()
        mapping_file = os.path.join(temp_dir, 'pyarchinit_matrix_mapping.json')

        mapping = {
            'nodes': {
                node['node_id']: {
                    'us': node.get('us', ''),
                    'sito': node.get('sito', ''),
                    'area': node.get('area', '')
                }
                for node in graph_data.get('nodes', [])
            }
        }

        with open(mapping_file, 'w') as f:
            json.dump(mapping, f)

        print(f"Node mapping saved for QGIS integration: {mapping_file}")