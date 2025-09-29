#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Graph visualization for S3DGraphy Extended Matrix
Creates an interactive graph visualization using networkx and matplotlib
"""

import os
from typing import Dict, List, Tuple, Optional
import json

try:
    # Suppress numpy warnings
    import warnings
    warnings.filterwarnings('ignore', message='numpy.dtype size changed')
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')

    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend to avoid GUI issues
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.patches as mpatches
    NETWORKX_AVAILABLE = True
except ImportError as e:
    NETWORKX_AVAILABLE = False
    print(f"NetworkX/Matplotlib not installed: {e}")
    print("Install with: pip install networkx matplotlib")


class MatrixGraphVisualizer:
    """
    Creates a hierarchical graph visualization of the stratigraphic matrix
    """

    def __init__(self):
        self.graph = None
        self.pos = None
        self.node_colors = {}
        self.node_shapes = {}

    def create_interactive_graph(self, graph_data: Dict, output_path: str = None) -> bool:
        """
        Create an interactive hierarchical graph visualization

        Args:
            graph_data: Extended Matrix data
            output_path: Optional path to save the image

        Returns:
            True if successful
        """
        if not NETWORKX_AVAILABLE:
            print("NetworkX not available")
            return False

        try:
            # Create directed graph
            self.graph = nx.DiGraph()

            # Build node hierarchy levels based on relationships
            levels = self._calculate_hierarchy_levels(graph_data)

            # Add nodes with attributes
            for node in graph_data.get('nodes', []):
                node_id = node.get('node_id', '')
                if node.get('node_type') == 'geo_position':
                    continue  # Skip geo nodes

                self.graph.add_node(
                    node_id,
                    label=node.get('name', node.get('us', '')),
                    node_type=node.get('node_type', 'stratigraphic_unit'),
                    unita_tipo=node.get('unita_tipo', 'US'),
                    level=levels.get(node_id, 0),
                    description=node.get('description', ''),
                    periodo=node.get('periodo', ''),
                    fase=node.get('fase', '')
                )

            # Add edges
            for edge in graph_data.get('edges', []):
                source = edge.get('edge_source', '')
                target = edge.get('edge_target', '')
                edge_type = edge.get('edge_type', 'generic_connection')

                if source in self.graph.nodes and target in self.graph.nodes:
                    self.graph.add_edge(source, target,
                                       relationship=edge_type,
                                       color=self._get_edge_color(edge_type))

            # Calculate hierarchical layout
            self.pos = self._calculate_hierarchical_layout(levels)

            # Create the visualization
            self._create_visualization(output_path)

            return True

        except Exception as e:
            print(f"Error creating graph visualization: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _calculate_hierarchy_levels(self, graph_data: Dict) -> Dict[str, int]:
        """
        Calculate hierarchical levels based on stratigraphic relationships
        Higher levels = earlier/deeper stratigraphy
        """
        levels = {}
        edges = graph_data.get('edges', [])

        # Build adjacency lists
        above = {}  # What is above each node
        below = {}  # What is below each node

        for edge in edges:
            source = edge.get('edge_source', '')
            target = edge.get('edge_target', '')
            edge_type = edge.get('edge_type', '')

            # Interpret relationships
            if edge_type == 'is_before':
                # Source is before (above) target stratigraphically
                if target not in above:
                    above[target] = []
                above[target].append(source)

                if source not in below:
                    below[source] = []
                below[source].append(target)

        # Calculate levels using topological sort
        # Start from nodes with nothing above them (top of sequence)
        visited = set()

        def calculate_level(node_id, visited_in_path=None):
            if visited_in_path is None:
                visited_in_path = set()

            if node_id in visited_in_path:
                return 0  # Cycle detected

            if node_id in levels:
                return levels[node_id]

            visited_in_path.add(node_id)

            # Find maximum level of nodes above
            max_level = -1
            if node_id in above:
                for parent in above[node_id]:
                    parent_level = calculate_level(parent, visited_in_path.copy())
                    max_level = max(max_level, parent_level)

            levels[node_id] = max_level + 1
            visited.add(node_id)

            return levels[node_id]

        # Calculate levels for all nodes
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node_id not in levels and node.get('node_type') != 'geo_position':
                calculate_level(node_id)

        # Normalize levels (0 = top, increasing downward)
        if levels:
            max_level = max(levels.values())
            for node_id in levels:
                levels[node_id] = max_level - levels[node_id]

        return levels

    def _calculate_hierarchical_layout(self, levels: Dict[str, int]) -> Dict:
        """
        Calculate positions for hierarchical layout
        Nodes at same stratigraphic level are on same horizontal line
        """
        pos = {}

        # Group nodes by level
        level_nodes = {}
        for node_id, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node_id)

        # Position nodes
        max_width = max(len(nodes) for nodes in level_nodes.values()) if level_nodes else 1

        for level, nodes in level_nodes.items():
            # Spread nodes horizontally at each level
            num_nodes = len(nodes)
            for i, node_id in enumerate(nodes):
                # Center the nodes horizontally
                x = (i - num_nodes/2.0 + 0.5) * (10.0 / max_width)
                y = -level * 2  # Negative y for top-to-bottom layout
                pos[node_id] = (x, y)

        return pos

    def _create_visualization(self, output_path: str = None):
        """
        Create the actual visualization using matplotlib
        """
        # Create figure with larger size for better visibility
        fig, ax = plt.subplots(figsize=(16, 12))

        # Set title
        ax.set_title("Extended Matrix - Stratigraphic Sequence", fontsize=16, fontweight='bold')

        # Draw edges first (so they appear behind nodes)
        edge_colors = []
        edge_styles = []
        for u, v, data in self.graph.edges(data=True):
            edge_colors.append(data.get('color', '#999999'))
            rel_type = data.get('relationship', '')
            if rel_type == 'has_same_time':
                edge_styles.append('dashed')
            else:
                edge_styles.append('solid')

        # Draw edges with arrows
        for (u, v), color, style in zip(self.graph.edges(), edge_colors, edge_styles):
            if u in self.pos and v in self.pos:
                ax.annotate('', xy=self.pos[v], xytext=self.pos[u],
                           arrowprops=dict(arrowstyle='->',
                                         connectionstyle='arc3,rad=0.1',
                                         color=color,
                                         linestyle=style,
                                         linewidth=1.5,
                                         alpha=0.7))

        # Prepare node colors and shapes by type
        node_colors = []
        node_sizes = []
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            node_type = node_data.get('node_type', 'stratigraphic_unit')
            unita_tipo = node_data.get('unita_tipo', 'US')

            # Color by unit type
            color_map = {
                'US': '#4CAF50',  # Green for regular US
                'USM': '#FF9800',  # Orange for masonry
                'USF': '#2196F3',  # Blue for features
                'USD': '#795548',  # Brown for deposits
                'USR': '#9C27B0',  # Purple for structural
                'virtual_reconstruction': '#E91E63'  # Pink for virtual
            }
            node_colors.append(color_map.get(unita_tipo, '#607D8B'))

            # Size by importance
            if node_type == 'virtual_reconstruction':
                node_sizes.append(1000)
            else:
                node_sizes.append(800)

        # Draw nodes
        nx.draw_networkx_nodes(self.graph, self.pos,
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.9,
                              edgecolors='black',
                              linewidths=2,
                              ax=ax)

        # Draw labels
        labels = {}
        for node_id in self.graph.nodes():
            labels[node_id] = self.graph.nodes[node_id].get('label', node_id.split('_')[-1])

        nx.draw_networkx_labels(self.graph, self.pos, labels,
                               font_size=10,
                               font_weight='bold',
                               ax=ax)

        # Add level lines and labels
        levels_dict = {}
        for node_id, (x, y) in self.pos.items():
            level = self.graph.nodes[node_id].get('level', 0)
            if level not in levels_dict:
                levels_dict[level] = []
            levels_dict[level].append(y)

        # Draw horizontal lines for each level
        for level, y_positions in levels_dict.items():
            if y_positions:
                y = y_positions[0]  # All nodes at same level have same y
                ax.axhline(y=y, color='lightgray', linestyle='--', alpha=0.3)
                ax.text(-8, y, f'Level {level}', fontsize=9,
                       ha='right', va='center', color='gray')

        # Add legend
        legend_elements = [
            mpatches.Patch(color='#4CAF50', label='US - Stratigraphic Unit'),
            mpatches.Patch(color='#FF9800', label='USM - Masonry Unit'),
            mpatches.Patch(color='#2196F3', label='USF - Feature Unit'),
            mpatches.Patch(color='#795548', label='USD - Deposit Unit'),
            mpatches.Patch(color='#9C27B0', label='USR - Structural Unit'),
            mpatches.Patch(color='#E91E63', label='Virtual Reconstruction')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

        # Add relationship legend
        rel_legend = [
            mpatches.Patch(color='none', label='Relationships:'),
            mpatches.Patch(color='#2196F3', label='— Is Before (temporal)'),
            mpatches.Patch(color='#4CAF50', label='-- Contemporary'),
            mpatches.Patch(color='#999999', label='— Generic Connection')
        ]
        ax.legend(handles=rel_legend, loc='upper right', fontsize=10)

        # Clean up the plot
        ax.set_axis_off()
        plt.tight_layout()

        # Save if path provided
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"Graph saved to: {output_path}")

        # Close the plot to free memory
        plt.close(fig)

    def _get_edge_color(self, edge_type: str) -> str:
        """
        Get color for edge based on relationship type
        """
        color_map = {
            'is_before': '#2196F3',  # Blue
            'has_same_time': '#4CAF50',  # Green
            'generic_connection': '#999999',  # Gray
            'covers': '#FF5722',  # Red
            'cuts': '#FF9800',  # Orange
            'fills': '#795548'  # Brown
        }
        return color_map.get(edge_type, '#999999')

    def export_to_dot(self, graph_data: Dict, output_path: str) -> bool:
        """
        Export to DOT format for Graphviz
        """
        try:
            if not self.graph:
                return False

            # Write DOT file
            nx.drawing.nx_agraph.write_dot(self.graph, output_path)
            print(f"DOT file exported to: {output_path}")
            return True

        except Exception as e:
            # Try alternative method
            try:
                with open(output_path, 'w') as f:
                    f.write("digraph ExtendedMatrix {\n")
                    f.write('  rankdir=TB;\n')  # Top to bottom
                    f.write('  node [shape=box, style=filled];\n')

                    # Write nodes
                    for node_id in self.graph.nodes():
                        node_data = self.graph.nodes[node_id]
                        label = node_data.get('label', node_id)
                        color = '#4CAF50' if node_data.get('unita_tipo') == 'US' else '#FF9800'
                        f.write(f'  "{node_id}" [label="{label}", fillcolor="{color}"];\n')

                    # Write edges
                    for u, v, data in self.graph.edges(data=True):
                        rel = data.get('relationship', '')
                        f.write(f'  "{u}" -> "{v}" [label="{rel}"];\n')

                    f.write("}\n")

                print(f"DOT file exported to: {output_path}")
                return True

            except Exception as e2:
                print(f"Error exporting to DOT: {str(e2)}")
                return False