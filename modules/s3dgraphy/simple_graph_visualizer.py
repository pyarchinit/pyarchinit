#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple graph visualizer without NetworkX
Creates a basic hierarchical visualization using only matplotlib
"""

import os
from typing import Dict, List, Tuple, Optional
import json
import math

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    from matplotlib.patches import Circle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class SimpleGraphVisualizer:
    """
    Creates a hierarchical graph visualization without NetworkX
    """

    def __init__(self):
        self.positions = {}
        self.levels = {}

    def create_graph_image(self, graph_data: Dict, output_path: str = None) -> bool:
        """
        Create a hierarchical graph visualization using only matplotlib

        Args:
            graph_data: Extended Matrix data
            output_path: Path to save the image

        Returns:
            True if successful
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available")
            return False

        try:
            # Calculate hierarchy levels
            self._calculate_levels(graph_data)

            # Calculate positions
            self._calculate_positions(graph_data)

            # Create the plot
            fig, ax = plt.subplots(figsize=(16, 12))
            ax.set_title("Extended Matrix - Stratigraphic Sequence", fontsize=16, fontweight='bold')

            # Draw edges (relationships)
            self._draw_edges(ax, graph_data)

            # Draw nodes
            self._draw_nodes(ax, graph_data)

            # Draw level lines
            self._draw_level_lines(ax)

            # Add legend
            self._add_legend(ax)

            # Clean up
            ax.set_xlim(-10, 10)
            ax.set_ylim(-max(self.levels.values()) * 2 - 2 if self.levels else -2, 2)
            ax.set_aspect('equal')
            ax.axis('off')

            plt.tight_layout()

            # Save
            if output_path:
                plt.savefig(output_path, dpi=150, bbox_inches='tight',
                           facecolor='white', edgecolor='none')
                print(f"Graph saved to: {output_path}")

            plt.close(fig)
            return True

        except Exception as e:
            print(f"Error creating graph: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _calculate_levels(self, graph_data: Dict):
        """
        Calculate hierarchy levels based on relationships
        """
        # Initialize all nodes at level 0
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node.get('node_type') != 'geo_position':
                self.levels[node_id] = 0

        # Process edges to determine levels
        edges = graph_data.get('edges', [])
        changed = True
        iterations = 0
        max_iterations = 100

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1

            for edge in edges:
                source = edge.get('edge_source', '')
                target = edge.get('edge_target', '')
                edge_type = edge.get('edge_type', '')

                if source in self.levels and target in self.levels:
                    if edge_type == 'is_before':
                        # Source is stratigraphically above target
                        new_target_level = self.levels[source] + 1
                        if self.levels[target] < new_target_level:
                            self.levels[target] = new_target_level
                            changed = True

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
        for level, nodes in level_nodes.items():
            num_nodes = len(nodes)
            for i, node_id in enumerate(sorted(nodes)):  # Sort for consistency
                # Spread nodes horizontally
                if num_nodes == 1:
                    x = 0
                else:
                    x = (i - (num_nodes - 1) / 2) * 3  # 3 units spacing
                y = -level * 2  # 2 units vertical spacing
                self.positions[node_id] = (x, y)

    def _draw_edges(self, ax, graph_data: Dict):
        """
        Draw relationships between nodes
        """
        edges = graph_data.get('edges', [])

        for edge in edges:
            source = edge.get('edge_source', '')
            target = edge.get('edge_target', '')
            edge_type = edge.get('edge_type', '')

            if source in self.positions and target in self.positions:
                x1, y1 = self.positions[source]
                x2, y2 = self.positions[target]

                # Choose color based on edge type
                if edge_type == 'is_before':
                    color = '#2196F3'  # Blue
                    style = 'solid'
                elif edge_type == 'has_same_time':
                    color = '#4CAF50'  # Green
                    style = 'dashed'
                else:
                    color = '#9E9E9E'  # Gray
                    style = 'dotted'

                # Draw arrow
                arrow = FancyArrowPatch((x1, y1 - 0.3), (x2, y2 + 0.3),
                                      connectionstyle="arc3,rad=0.1",
                                      arrowstyle='-|>',
                                      color=color,
                                      linestyle=style,
                                      linewidth=1.5,
                                      alpha=0.7)
                ax.add_patch(arrow)

    def _draw_nodes(self, ax, graph_data: Dict):
        """
        Draw nodes as circles with labels
        """
        nodes = graph_data.get('nodes', [])

        for node in nodes:
            node_id = node.get('node_id', '')
            if node_id not in self.positions:
                continue

            x, y = self.positions[node_id]

            # Get node properties
            node_type = node.get('node_type', 'stratigraphic_unit')
            unita_tipo = node.get('unita_tipo', 'US')
            label = node.get('name', node.get('us', ''))

            # Choose color based on unit type
            color_map = {
                'US': '#4CAF50',  # Green
                'USM': '#FF9800',  # Orange
                'USF': '#2196F3',  # Blue
                'USD': '#795548',  # Brown
                'USR': '#9C27B0',  # Purple
                'virtual_reconstruction': '#E91E63'  # Pink
            }
            color = color_map.get(unita_tipo, '#607D8B')

            # Draw node circle
            circle = Circle((x, y), 0.4, facecolor=color, edgecolor='black',
                          linewidth=2, alpha=0.9)
            ax.add_patch(circle)

            # Add label
            ax.text(x, y, label, ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')

            # Add description below
            description = node.get('description', '')
            if description:
                ax.text(x, y - 0.6, description[:30], ha='center', va='top',
                       fontsize=8, color='gray', style='italic')

    def _draw_level_lines(self, ax):
        """
        Draw horizontal lines for each stratigraphic level
        """
        level_y_positions = {}
        for node_id, (x, y) in self.positions.items():
            level = self.levels.get(node_id, 0)
            level_y_positions[level] = y

        for level, y in level_y_positions.items():
            ax.axhline(y=y, color='lightgray', linestyle='--', alpha=0.3)
            ax.text(-9, y, f'Level {level}', fontsize=9,
                   ha='left', va='center', color='gray')

    def _add_legend(self, ax):
        """
        Add legend to the plot
        """
        # Unit type legend
        unit_patches = [
            mpatches.Patch(color='#4CAF50', label='US - Stratigraphic Unit'),
            mpatches.Patch(color='#FF9800', label='USM - Masonry Unit'),
            mpatches.Patch(color='#2196F3', label='USF - Feature Unit'),
            mpatches.Patch(color='#795548', label='USD - Deposit Unit'),
        ]
        legend1 = ax.legend(handles=unit_patches, loc='upper left',
                          title='Unit Types', fontsize=9)
        ax.add_artist(legend1)

        # Relationship legend
        rel_patches = [
            mpatches.Patch(color='#2196F3', label='Is Before'),
            mpatches.Patch(color='#4CAF50', label='Contemporary'),
            mpatches.Patch(color='#9E9E9E', label='Generic'),
        ]
        ax.legend(handles=rel_patches, loc='upper right',
                 title='Relationships', fontsize=9)